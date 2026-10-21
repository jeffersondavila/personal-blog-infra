"""Modo `export` de D-24 (Task/031 H-031-6): primer tramo de la via de salida fuera de la cuenta (D-10 §10.1).

Con `blog_migrate`, en UNA instantanea REPEATABLE READ de solo lectura, vuelca cada tabla del esquema `public` con
`COPY ... TO STDOUT` en CSV con cabecera y escribe cada CSV, y al final un manifiesto, en el prefijo dedicado del bucket
de medios por el gateway endpoint de S3. Sin manifiesto, una exportacion no cuenta como completa.

- Escritura condicional (`If-None-Match: *`): una exportacion nunca pisa otra; la marca la elige el operador.
- `ChecksumSHA256` en cada objeto: S3 rechaza el que no llegue integro, y el manifiesto repite el digest y las filas.
- La salida es el recuento de filas por tabla y las claves, nunca los datos ni el bucket (D-24 §8.2).
- Si el volcado no cabe en `LIMITE_DE_BYTES`, se detiene sin escribir y se pide una decision explicita (D-10 §10.1):
  no se trocea en silencio.

El cliente S3 sale del rol de ejecucion de la funcion; ninguna credencial pasa por aqui.
"""
import base64
import hashlib
import json
import re

import operaciones

PREFIJO = "exportaciones/"
FORMATO = "d24-export-v1"
COPIA = "COPY ... TO STDOUT WITH (FORMAT csv, HEADER true)"
LIMITE_DE_BYTES = 16 * 1024 * 1024
REGION = "us-east-2"
_TABLA = re.compile(r"[a-z_][a-z0-9_]{0,62}")
_SIN_CONEXION = ("EndpointConnectionError", "ConnectTimeoutError", "ReadTimeoutError", "ConnectionClosedError")


def _cliente_s3():
    import boto3  # diferido: solo `export` lo necesita y las pruebas unitarias lo sustituyen
    from botocore.config import Config

    return boto3.client("s3", region_name=REGION, config=Config(
        retries={"max_attempts": 3, "mode": "standard"}, connect_timeout=5, read_timeout=20,
        request_checksum_calculation="when_required", response_checksum_validation="when_required"))


CLIENTE_S3 = _cliente_s3


def _codigo_s3(error):
    """Codigo cerrado de un fallo de S3, o None si el error no viene de S3 (y entonces es interno)."""
    codigo = ((getattr(error, "response", None) or {}).get("Error") or {}).get("Code")
    if codigo in ("PreconditionFailed", "ConditionalRequestConflict"):
        return "EXPORTACION_YA_EXISTE"
    if codigo in ("AccessDenied", "AllAccessDisabled", "InvalidAccessKeyId", "SignatureDoesNotMatch"):
        return "S3_ACCESO_DENEGADO"
    if codigo:
        return "S3_FALLIDO"
    if type(error).__name__ in _SIN_CONEXION:
        return "S3_SIN_CONEXION"
    if type(error).__module__.startswith("botocore"):
        return "S3_FALLIDO"
    return None


def _volcar(pedido):
    """[(tabla, filas, csv)] de `public`, todo de la misma instantanea de solo lectura."""

    def trabajo(conexion, cursor, sesion):
        operaciones._revertir(conexion)  # la comprobacion de la sesion abrio una transaccion; la instantanea, aqui
        cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
        cursor.execute("SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
        tablas, total = [], 0
        for esquema, nombre in cursor.fetchall():
            if not _TABLA.fullmatch(nombre):
                raise operaciones.Fallo("TABLA_NO_ADMITIDA")
            identificador = f'{esquema}."{nombre}"'
            cursor.execute(f"SELECT count(*) FROM {identificador}")
            (filas,) = cursor.fetchone()
            datos = bytearray()
            with cursor.copy(f"COPY {identificador} TO STDOUT WITH (FORMAT csv, HEADER true)") as copia:
                for trozo in copia:
                    datos += trozo
                    total += len(trozo)
                    if total > LIMITE_DE_BYTES:
                        raise operaciones.Fallo("EXPORTACION_DEMASIADO_GRANDE")
            tablas.append((f"{esquema}.{nombre}", filas, bytes(datos)))
        operaciones._revertir(conexion)  # solo lectura: nada que confirmar
        return tablas

    return operaciones._operar(pedido, "blog_migrate", trabajo)


def _escribir(cliente, bucket, clave, cuerpo, tipo):
    cliente.put_object(Bucket=bucket, Key=clave, Body=cuerpo, ContentType=tipo,
                       ChecksumSHA256=base64.b64encode(hashlib.sha256(cuerpo).digest()).decode("ascii"),
                       IfNoneMatch="*")


def export(pedido):
    marca, bucket = pedido["salida"]["marca"], pedido["salida"]["bucket"]
    tablas = _volcar(pedido)
    base = f"{PREFIJO}{marca}/"
    manifiesto = {"formato": FORMATO, "marca": marca, "csv": COPIA, "tablas": []}
    try:
        cliente = CLIENTE_S3()
        for tabla, filas, datos in tablas:
            clave = f"{base}{tabla}.csv"
            _escribir(cliente, bucket, clave, datos, "text/csv; charset=utf-8")
            manifiesto["tablas"].append({"tabla": tabla, "objeto": clave, "filas": filas, "bytes": len(datos),
                                         "sha256": hashlib.sha256(datos).hexdigest()})
        cuerpo = json.dumps(manifiesto, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
        _escribir(cliente, bucket, f"{base}manifiesto.json", cuerpo, "application/json")
    except Exception as error:
        codigo = _codigo_s3(error)
        if codigo is None:
            raise
        raise operaciones.Fallo(codigo) from None
    return {"exportacion": {"prefijo": base, "manifiesto": f"{base}manifiesto.json",
                            "tablas": {tabla: filas for tabla, filas, _ in tablas},
                            "bytes": sum(len(datos) for _, _, datos in tablas)}}
