"""Diagnostico MANUAL de solo lectura de los backups de RDS (Task/031 B3, opcion A, aprobada el 2026-10-16).

RDS no publica ningun evento de «backup fallido» para instancias. Solo publica:
- el inicio de cada backup diario (RDS-EVENT-0001, «Backing up DB instance»);
- su fin (RDS-EVENT-0002, «Finished DB instance backup»);
- RDS-EVENT-0028 («Disabled automated backups»);
- los eventos de la categoria `failure`.
Por eso el fallo se detecta por AUSENCIA. Este diagnostico se ejecuta a mano, no de forma continua, y comprueba:

  1. la instancia en `available`;
  2. la retencion en 1 dia, que es la excepcion vigente del plan FREE (§34); 0 significa backups desactivados;
  3. un backup automatico TERMINADO hace como mucho 26 h. Hay uno al dia, en la ventana 07:00-07:30 UTC: justo antes
     de que acabe la ventana siguiente, el ultimo tiene hasta 24 h 30 min. El margen cubre la duracion observada
     (2-5 min) y el retraso de los eventos;
  4. ningun backup iniciado hace mas de 2 h sin terminar (los observados tardan de 2 a 5 min);
  5. `LatestRestorableTime` con 15 min de retraso como mucho, que es el objetivo de RPO de D-10. Un retraso acotado
     implica que sigue avanzando;
  6. ningun evento de backups desactivados ni de la categoria `failure` en los 14 dias que guarda RDS.

La ausencia de datos es un fallo, nunca un OK. Usa la AWS CLI con el perfil operativo (`aws login`), siempre en modo
UTF-8 (la CLI de Windows escribe cp1252), y nunca imprime cuentas, ARN ni mensajes de error de AWS: solo su codigo.

Codigos de salida:
- 0: OK.
- 1: FALLO, con hallazgos.
- 2: uso.
- 3: error de AWS o de la CLI.
- 4: credenciales caducadas; renovar el rol en la consola y despues `aws login`.
- 5: identidad no autorizada.

Uso: python -m scripts.terraform_datos.diagnostico_backups
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess

PRODUCTIVA = "blog-prod-postgres"
PERFIL = ["--profile", "personal-blog", "--region", "us-east-2", "--output", "json", "--no-cli-pager"]
RETENCION_APROBADA = 1
VENTANA_DE_BACKUP = dt.timedelta(hours=26)
BACKUP_ATASCADO = dt.timedelta(hours=2)
RETRASO_MAXIMO_DE_PITR = dt.timedelta(minutes=15)
DESFASE_TOLERADO = dt.timedelta(minutes=5)
HISTORIAL = dt.timedelta(days=14)  # lo maximo que RDS guarda y que admite `describe-events --duration`

TERMINADO, INICIADO, DESACTIVADOS = "finished db instance backup", "backing up db instance", "disabled automated backups"
_IDENTIDAD = re.compile(r"arn:aws:sts::[0-9]{12}:assumed-role/PersonalBlogAdministrator/[^/]+")
_CADUCADA = re.compile(r"session has expired|reauthenticate|ExpiredToken|RequestExpired|security token included in "
                       r"the request is expired|Unable to locate credentials|Token has expired", re.IGNORECASE)
_CODIGO = re.compile(r"An error occurred \(([A-Za-z0-9]+)\)")

RELOJ = lambda: dt.datetime.now(dt.timezone.utc)  # noqa: E731
EJECUTAR = subprocess.run


class Salida(Exception):
    """Fin controlado con un estado cerrado y su codigo de salida."""

    def __init__(self, codigo_de_salida, estado, **detalle):
        super().__init__(estado)
        self.codigo_de_salida, self.estado, self.detalle = codigo_de_salida, estado, detalle


def _aws(*argumentos):
    try:
        r = EJECUTAR(["aws", *argumentos, *PERFIL], capture_output=True, text=True, encoding="utf-8",
                     errors="replace", env={**os.environ, "PYTHONUTF8": "1"})
    except FileNotFoundError:
        raise Salida(3, "ERROR_DE_AWS", codigo="CLI_NO_ENCONTRADA") from None
    if r.returncode:
        if _CADUCADA.search(r.stderr or ""):
            raise Salida(4, "CREDENCIALES_CADUCADAS")
        codigo = _CODIGO.search(r.stderr or "")
        raise Salida(3, "ERROR_DE_AWS", codigo=codigo.group(1) if codigo else "DESCONOCIDO")
    try:
        return json.loads(r.stdout)
    except (TypeError, ValueError):
        raise Salida(3, "ERROR_DE_AWS", codigo="SALIDA_ILEGIBLE") from None


def _ilegible():
    return Salida(3, "ERROR_DE_AWS", codigo="SALIDA_ILEGIBLE")


def _instante(texto):
    try:
        instante = dt.datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        raise _ilegible() from None
    if instante.tzinfo is None:
        raise _ilegible()
    return instante


def _mensaje(evento):
    return evento["Message"].strip().rstrip(".").lower()


def _eventos(crudos):
    """Cada evento con instante, mensaje normalizado y categorias; uno sin fecha o sin mensaje es ilegible."""
    if not isinstance(crudos, list):
        raise _ilegible()
    eventos = []
    for crudo in crudos:
        if not (isinstance(crudo, dict) and isinstance(crudo.get("Message"), str) and crudo.get("Date")):
            raise _ilegible()
        eventos.append((_instante(crudo["Date"]), _mensaje(crudo), set(crudo.get("EventCategories") or [])))
    return eventos


def evaluar(instancia, eventos, ahora):
    """Hallazgos ordenados y un resumen sin cuentas ni ARN."""
    if not all(clave in instancia for clave in ("DBInstanceStatus", "BackupRetentionPeriod")):
        raise _ilegible()
    hallazgos = set()
    if instancia["DBInstanceStatus"] != "available":
        hallazgos.add("INSTANCIA_NO_DISPONIBLE")
    retencion = instancia["BackupRetentionPeriod"]
    if retencion == 0:
        hallazgos.add("BACKUPS_DESACTIVADOS")
    elif retencion != RETENCION_APROBADA:
        hallazgos.add("RETENCION_DISTINTA")

    restaurable = instancia.get("LatestRestorableTime")
    retraso = None
    if restaurable is None:
        hallazgos.add("PITR_SIN_DATOS")
    else:
        retraso = ahora - _instante(restaurable)
        if retraso > RETRASO_MAXIMO_DE_PITR:
            hallazgos.add("PITR_RETRASADO")
        elif retraso < -DESFASE_TOLERADO:
            hallazgos.add("RELOJ_DESFASADO")

    de_backup = [(instante, mensaje) for instante, mensaje, categorias in eventos if "backup" in categorias]
    terminados = [instante for instante, mensaje in de_backup if mensaje == TERMINADO]
    iniciados = [instante for instante, mensaje in de_backup if mensaje == INICIADO]
    ultimo = max(terminados) if terminados else None
    if ultimo is None or ahora - ultimo > VENTANA_DE_BACKUP:
        hallazgos.add("SIN_BACKUP_RECIENTE")
    if iniciados and (ultimo is None or max(iniciados) > ultimo) and ahora - max(iniciados) > BACKUP_ATASCADO:
        hallazgos.add("BACKUP_ATASCADO")
    if any(mensaje == DESACTIVADOS for _, mensaje, _ in eventos):
        hallazgos.add("BACKUPS_DESACTIVADOS_EN_EVENTOS")
    if any("failure" in categorias for _, _, categorias in eventos):
        hallazgos.add("FALLO_DE_INSTANCIA")

    horas = lambda delta: None if delta is None else round(delta.total_seconds() / 3600, 1)  # noqa: E731
    minutos = lambda delta: None if delta is None else round(delta.total_seconds() / 60, 1)  # noqa: E731
    resumen = {
        "instancia": {"estado": instancia["DBInstanceStatus"], "retencion_dias": retencion},
        "ultimo_backup": {"terminado": ultimo.isoformat() if ultimo else None,
                          "antiguedad_h": horas(ahora - ultimo) if ultimo else None},
        "pitr": {"latest_restorable_time": restaurable, "retraso_min": minutos(retraso)},
        "eventos_revisados": len(eventos),
    }
    return sorted(hallazgos), resumen


UMBRALES = {"backup_h": VENTANA_DE_BACKUP // dt.timedelta(hours=1),
            "backup_atascado_h": BACKUP_ATASCADO // dt.timedelta(hours=1),
            "retraso_pitr_min": RETRASO_MAXIMO_DE_PITR // dt.timedelta(minutes=1),
            "retencion_dias": RETENCION_APROBADA, "historial_dias": HISTORIAL.days}


def diagnosticar():
    if not _IDENTIDAD.fullmatch(str(_aws("sts", "get-caller-identity").get("Arn", ""))):
        raise Salida(5, "IDENTIDAD_NO_AUTORIZADA")
    try:
        instancias = _aws("rds", "describe-db-instances", "--db-instance-identifier", PRODUCTIVA).get("DBInstances")
    except Salida as salida:
        if salida.detalle.get("codigo") == "DBInstanceNotFound":
            return ["INSTANCIA_INEXISTENTE"], {}
        raise
    if not (isinstance(instancias, list) and len(instancias) == 1 and isinstance(instancias[0], dict)):
        raise _ilegible()
    crudos = _aws("rds", "describe-events", "--source-identifier", PRODUCTIVA, "--source-type", "db-instance",
                  "--duration", str(int(HISTORIAL.total_seconds() // 60))).get("Events")
    return evaluar(instancias[0], _eventos(crudos), RELOJ())


def main(argv=None):
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args(argv)
    try:
        hallazgos, resumen = diagnosticar()
    except Salida as salida:
        print(json.dumps({"estado": salida.estado, **salida.detalle}, sort_keys=True))
        return salida.codigo_de_salida
    estado = "FALLO" if hallazgos else "OK"
    print(json.dumps({"estado": estado, "hallazgos": hallazgos, **resumen, "umbrales": UMBRALES,
                      "comprobado_en": RELOJ().isoformat(timespec="seconds")}, sort_keys=True, ensure_ascii=False))
    return 1 if hallazgos else 0


if __name__ == "__main__":
    raise SystemExit(main())
