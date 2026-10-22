"""Empaqueta la ejecutora privada de D-24 (Task/031) en un ZIP DETERMINISTA, por fases.

Por que existe
--------------
El artefacto de la ejecutora sale de UNA fuente versionada de este repositorio,
`terraform/modulos/ejecutor_privado/codigo/ejecutor.py`, que solo usa biblioteca estandar. Para que el plan
revisado y lo desplegado sean los mismos bytes, el ZIP no depende de la maquina ni del momento: una sola entrada,
sin compresion (la salida de zlib puede variar entre versiones), fecha fija, permisos fijos y sistema de origen
Unix. Sus bytes, y por tanto su SHA-256, solo cambian si cambia la fuente.

`SHA256_ESPERADO` es el PIN del artefacto revisado. Si la fuente cambia, el pin cambia en la misma revision y a
proposito: `tests/terraform_datos/test_empaquetar_ejecutor.py` y la guarda del plan de H-031-5 lo exigen. Este
repositorio no versiona el ZIP (`*.zip` esta ignorado): versiona la fuente y el pin.

Fase H-031-6 (`--fase h0316`)
-----------------------------
Las fuentes de `codigo_h0316/` -incluido el bundle regional de la CA de RDS- mas el contenido de EXACTAMENTE las
ruedas fijadas en `requirements-ejecutor-h0316.txt`. Cada rueda se verifica por SHA-256 ANTES de abrirla; una rueda
ausente, alterada, sobrante, con `.data/` o con rutas inseguras aborta sin escribir nada. Mismas reglas de bytes que
H-031-5, asi que el pin `SHA256_ESPERADO_H0316` solo cambia si cambian las fuentes o las ruedas fijadas. Las ruedas
no se versionan: se descargan con `pip download --require-hashes` (orden exacto en el archivo de requisitos).

Uso: python scripts/terraform_datos/empaquetar_ejecutor.py [--fase h0315] --destino <ruta.zip>
     python scripts/terraform_datos/empaquetar_ejecutor.py --fase h0316 --ruedas <directorio> --destino <ruta.zip>
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FUENTE = REPO / "terraform" / "modulos" / "ejecutor_privado" / "codigo" / "ejecutor.py"
ENTRADA = "ejecutor.py"
FECHA = (1980, 1, 1, 0, 0, 0)
PERMISOS = 0o100644  # archivo regular, rw-r--r--: Lambda solo necesita leerlo
SISTEMA_UNIX = 3
SHA256_ESPERADO = "e27fe7354fbbb616693cd7ba59eb20cad2dcf902b98be6df11b2016fe1e723bd"

CODIGO_H0316 = REPO / "terraform" / "modulos" / "ejecutor_privado" / "codigo_h0316"
FUENTES_H0316 = ("ejecutor.py", "exportacion.py", "operaciones.py", "rds-ca-us-east-2.pem")
REQUISITOS_H0316 = REPO / "scripts" / "terraform_datos" / "requirements-ejecutor-h0316.txt"
# 2026-10-18: el advisory lock de D-24 (modificada; aprobada el 2026-10-19) cambio `operaciones.py`. El pin anterior era
# 02cf270dd4f2cafab5607c460e3066768fc44c53ed11c1e41e276992aff88ddf (42 999 616 bytes); el nuevo pesa 43 001 155.
SHA256_ESPERADO_H0316 = "98f41bfd3a1d2c9ac97f1686d803f8eba40c3cf450bb8e7b491fa9fef5ff8e43"

_PAQUETE = re.compile(r"([a-z0-9][a-z0-9-]*)==([0-9][0-9a-z.]*) \\")
_HASH = re.compile(r"    --hash=sha256:([0-9a-f]{64})")


def contenido():
    """Bytes de la fuente, exigiendo LF y sin BOM: un CRLF de un checkout cambiaria el digest."""
    datos = FUENTE.read_bytes()
    if b"\r" in datos or datos.startswith(b"\xef\xbb\xbf"):
        raise ValueError("FUENTE_NO_NORMALIZADA")
    return datos


def _escribir(destino, entradas):
    """ZIP con `entradas` (nombre -> bytes) en orden, sin compresion, fecha y permisos fijos; devuelve su SHA-256."""
    destino = Path(destino)
    with zipfile.ZipFile(destino, "w", compression=zipfile.ZIP_STORED) as archivo:
        for nombre in sorted(entradas):
            info = zipfile.ZipInfo(nombre, date_time=FECHA)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = SISTEMA_UNIX
            info.external_attr = PERMISOS << 16
            archivo.writestr(info, entradas[nombre])
    return hashlib.sha256(destino.read_bytes()).hexdigest()


def construir(destino):
    """Escribe el ZIP de H-031-5 en `destino` y devuelve su SHA-256 en hexadecimal."""
    return _escribir(destino, {ENTRADA: contenido()})


def requisitos(ruta=None):
    """[(paquete, version, sha256)] del archivo fijado: `paquete==version \\` y UNA linea `--hash=sha256:`."""
    lineas = [linea for linea in Path(ruta or REQUISITOS_H0316).read_text(encoding="utf-8").splitlines()
              if linea.strip() and not linea.startswith("#")]
    if not lineas or len(lineas) % 2:
        raise ValueError("REQUISITOS_NO_ADMITIDOS")
    resultado = []
    for paquete, hash_ in zip(lineas[::2], lineas[1::2]):
        nombre, firma = _PAQUETE.fullmatch(paquete), _HASH.fullmatch(hash_)
        if not nombre or not firma:
            raise ValueError("REQUISITOS_NO_ADMITIDOS")
        resultado.append((nombre.group(1), nombre.group(2), firma.group(1)))
    return resultado


def _ruedas(directorio):
    """La rueda de cada requisito, verificada por SHA-256; el directorio no puede tener ninguna otra."""
    archivos = sorted(Path(directorio).glob("*.whl"))
    elegidas = []
    for paquete, version, sha in requisitos():
        prefijo = f"{paquete.replace('-', '_')}-{version}-"
        candidatas = [archivo for archivo in archivos if archivo.name.startswith(prefijo)]
        if not candidatas:
            raise ValueError("RUEDA_AUSENTE")
        verificadas = [archivo for archivo in candidatas if hashlib.sha256(archivo.read_bytes()).hexdigest() == sha]
        if len(verificadas) != 1:
            raise ValueError("RUEDA_ALTERADA")
        elegidas.append(verificadas[0])
    if sorted(elegidas) != archivos:
        raise ValueError("RUEDA_NO_FIJADA")
    return elegidas


def _admitida(nombre):
    """Una ruta relativa, sin `..`, sin unidad ni barra invertida y fuera de `<paquete>.data/`."""
    partes = nombre.split("/")
    return not (nombre.startswith("/") or "\\" in nombre or ":" in nombre or ".." in partes
                or partes[0].endswith(".data"))


def entradas_h0316(directorio_de_ruedas):
    """Nombre -> bytes del artefacto de H-031-6: fuentes normalizadas y el contenido de las ruedas fijadas."""
    entradas = {}
    for fuente in FUENTES_H0316:
        datos = (CODIGO_H0316 / fuente).read_bytes()
        if b"\r" in datos or datos.startswith(b"\xef\xbb\xbf"):
            raise ValueError("FUENTE_NO_NORMALIZADA")
        entradas[fuente] = datos
    for rueda in _ruedas(directorio_de_ruedas):
        with zipfile.ZipFile(rueda) as archivo:
            for info in archivo.infolist():
                partes = info.filename.split("/")
                # Los scripts de consola (`<paquete>.data/scripts/`) irian a bin/: no son codigo importable.
                if info.is_dir() or (partes[0].endswith(".data") and partes[1:2] == ["scripts"]):
                    continue
                if not _admitida(info.filename):
                    raise ValueError("RUEDA_NO_ADMITIDA")
                if info.filename in entradas:
                    raise ValueError("ENTRADA_DUPLICADA")
                entradas[info.filename] = archivo.read(info)
    return entradas


def construir_h0316(destino, directorio_de_ruedas):
    """Escribe el ZIP de H-031-6 en `destino` y devuelve su SHA-256. Nada se escribe si algo no cuadra."""
    return _escribir(destino, entradas_h0316(directorio_de_ruedas))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fase", choices=("h0315", "h0316"), default="h0315", help="Artefacto que se construye.")
    parser.add_argument("--ruedas", type=Path, help="Directorio con las ruedas fijadas (solo h0316).")
    parser.add_argument("--destino", required=True, type=Path, help="Ruta del ZIP que se escribe.")
    args = parser.parse_args()
    if (args.fase == "h0316") != (args.ruedas is not None):
        parser.error("--ruedas es obligatorio con --fase h0316 y no se admite con h0315")
    if args.fase == "h0316":
        sha, esperado = construir_h0316(args.destino, args.ruedas), SHA256_ESPERADO_H0316
    else:
        sha, esperado = construir(args.destino), SHA256_ESPERADO
    if sha != esperado:
        args.destino.unlink(missing_ok=True)
        raise SystemExit("PIN: el artefacto construido no coincide con el pin de su fase; se borro y no se usa.")
    print(json.dumps({"artefacto": args.destino.name, "sha256": sha}))


if __name__ == "__main__":
    main()
