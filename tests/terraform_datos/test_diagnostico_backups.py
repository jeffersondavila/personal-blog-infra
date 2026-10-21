"""Diagnostico MANUAL de solo lectura de los backups de RDS (Task/031 B3, opcion A, aprobada el 2026-10-16).

Las pruebas sustituyen la AWS CLI (`EJECUTAR`) y el reloj (`RELOJ`), sin red ni credenciales. Cada negativa rompe una
sola cosa y exige su hallazgo o su estado. La ausencia de datos es siempre un fallo, nunca un OK.
"""
import datetime as dt
import json
import subprocess
import unittest
from contextlib import redirect_stdout
from io import StringIO

from scripts.terraform_datos import diagnostico_backups as diag

AHORA = dt.datetime(2026, 10, 16, 18, 0, 0, tzinfo=dt.timezone.utc)
CUENTA = "123456789012"
ARN_OPERADOR = f"arn:aws:sts::{CUENTA}:assumed-role/PersonalBlogAdministrator/personal-blog-entry-admin"


def iso(instante):
    return instante.isoformat()


def instancia(**cambios):
    datos = {"DBInstanceIdentifier": "blog-prod-postgres", "DBInstanceStatus": "available",
             "BackupRetentionPeriod": 1, "LatestRestorableTime": iso(AHORA - dt.timedelta(minutes=5)),
             "DBInstanceArn": f"arn:aws:rds:us-east-2:{CUENTA}:db:blog-prod-postgres"}
    datos.update(cambios)
    return datos


def evento(mensaje, hace, categorias=("backup",)):
    return {"SourceIdentifier": "blog-prod-postgres", "SourceType": "db-instance", "Message": mensaje,
            "EventCategories": list(categorias), "Date": iso(AHORA - hace),
            "SourceArn": f"arn:aws:rds:us-east-2:{CUENTA}:db:blog-prod-postgres"}


def backup_diario(hace_fin):
    """El par real observado en la cuenta: inicio y fin, con 3 minutos de diferencia."""
    return [evento("Backing up DB instance", hace_fin + dt.timedelta(minutes=3)),
            evento("Finished DB Instance backup", hace_fin)]


SANOS = backup_diario(dt.timedelta(hours=8)) + backup_diario(dt.timedelta(hours=32))


class CLIFalsa:
    """Responde a cada comando de la AWS CLI con un `CompletedProcess` preparado; registra lo invocado."""

    def __init__(self, identidad=ARN_OPERADOR, instancia_=None, eventos=None, fallos=None):
        self.respuestas = {
            ("sts", "get-caller-identity"): (0, json.dumps({"Arn": identidad, "Account": CUENTA}), ""),
            ("rds", "describe-db-instances"): (0, json.dumps({"DBInstances": [instancia_ or instancia()]}), ""),
            ("rds", "describe-events"): (0, json.dumps({"Events": SANOS if eventos is None else eventos}), ""),
        }
        self.respuestas.update(fallos or {})
        self.invocados = []

    def __call__(self, orden, **opciones):
        self.invocados.append((orden, opciones))
        if isinstance(self.respuestas.get(tuple(orden[1:3])), Exception):
            raise self.respuestas[tuple(orden[1:3])]
        rc, salida, error = self.respuestas[tuple(orden[1:3])]
        return subprocess.CompletedProcess(orden, rc, salida, error)


class Diagnostico(unittest.TestCase):
    def setUp(self):
        self.reloj, self.ejecutar = diag.RELOJ, diag.EJECUTAR
        diag.RELOJ = lambda: AHORA

    def tearDown(self):
        diag.RELOJ, diag.EJECUTAR = self.reloj, self.ejecutar

    def correr(self, cli):
        diag.EJECUTAR = cli
        salida = StringIO()
        with redirect_stdout(salida):
            codigo = diag.main([])
        texto = salida.getvalue()
        self.assertNotIn(CUENTA, texto, "la salida nunca lleva la cuenta ni un ARN")
        return codigo, json.loads(texto)

    def falla_con(self, cli, *hallazgos):
        codigo, resultado = self.correr(cli)
        self.assertEqual((codigo, resultado["estado"]), (1, "FALLO"))
        self.assertEqual(resultado["hallazgos"], sorted(hallazgos))
        return resultado

    # --- Positivos ------------------------------------------------------------

    def test_todo_sano(self):
        codigo, r = self.correr(CLIFalsa())
        self.assertEqual((codigo, r["estado"], r["hallazgos"]), (0, "OK", []))
        self.assertEqual((r["instancia"]["estado"], r["instancia"]["retencion_dias"]), ("available", 1))
        self.assertEqual(r["ultimo_backup"]["antiguedad_h"], 8.0)
        self.assertEqual(r["pitr"]["retraso_min"], 5.0)
        self.assertEqual(r["umbrales"], {"backup_h": 26, "backup_atascado_h": 2, "retraso_pitr_min": 15,
                                         "retencion_dias": 1, "historial_dias": 14})

    def test_los_limites_exactos_aun_pasan(self):
        cli = CLIFalsa(instancia_=instancia(LatestRestorableTime=iso(AHORA - dt.timedelta(minutes=15))),
                       eventos=backup_diario(dt.timedelta(hours=26)))
        self.assertEqual(self.correr(cli)[1]["estado"], "OK")

    def test_backup_en_curso_dentro_de_su_duracion_normal(self):
        eventos = SANOS + [evento("Backing up DB instance", dt.timedelta(minutes=30))]
        self.assertEqual(self.correr(CLIFalsa(eventos=eventos))[1]["estado"], "OK")

    def test_mensaje_con_otra_capitalizacion_y_punto_final(self):
        """El catalogo dice «Finished DB instance backup.» y la cuenta registra «Finished DB Instance backup»."""
        eventos = [evento("Backing up DB instance.", dt.timedelta(hours=8, minutes=3)),
                   evento("Finished DB instance backup.", dt.timedelta(hours=8))]
        self.assertEqual(self.correr(CLIFalsa(eventos=eventos))[1]["estado"], "OK")

    def test_consulta_exacta_y_solo_de_lectura(self):
        cli = CLIFalsa()
        self.correr(cli)
        ordenes = [orden for orden, _ in cli.invocados]
        self.assertEqual([o[1:3] for o in ordenes], [["sts", "get-caller-identity"], ["rds", "describe-db-instances"],
                                                     ["rds", "describe-events"]])
        self.assertIn("20160", ordenes[2])
        for orden, opciones in cli.invocados:
            self.assertEqual(orden[0], "aws")
            self.assertEqual(orden[-7:], ["--profile", "personal-blog", "--region", "us-east-2", "--output", "json",
                                          "--no-cli-pager"])
            self.assertEqual(opciones["env"]["PYTHONUTF8"], "1")

    # --- Instancia y retencion -------------------------------------------------

    def test_instancia_no_disponible(self):
        for estado in ("backing-up", "stopped", "failed", "storage-full", "incompatible-restore"):
            with self.subTest(estado=estado):
                self.falla_con(CLIFalsa(instancia_=instancia(DBInstanceStatus=estado)), "INSTANCIA_NO_DISPONIBLE")

    def test_instancia_inexistente(self):
        fallo = (254, "", "An error occurred (DBInstanceNotFound) when calling the DescribeDBInstances operation")
        self.falla_con(CLIFalsa(fallos={("rds", "describe-db-instances"): fallo}), "INSTANCIA_INEXISTENTE")

    def test_retencion(self):
        self.falla_con(CLIFalsa(instancia_=instancia(BackupRetentionPeriod=0)), "BACKUPS_DESACTIVADOS")
        self.falla_con(CLIFalsa(instancia_=instancia(BackupRetentionPeriod=7)), "RETENCION_DISTINTA")

    # --- Backups ----------------------------------------------------------------

    def test_sin_ningun_evento_es_un_fallo(self):
        self.falla_con(CLIFalsa(eventos=[]), "SIN_BACKUP_RECIENTE")

    def test_ultimo_backup_demasiado_antiguo(self):
        self.falla_con(CLIFalsa(eventos=backup_diario(dt.timedelta(hours=26, seconds=1))), "SIN_BACKUP_RECIENTE")

    def test_solo_eventos_de_otras_categorias(self):
        eventos = [evento("Finished DB Instance backup", dt.timedelta(hours=8), categorias=("notification",))]
        self.falla_con(CLIFalsa(eventos=eventos), "SIN_BACKUP_RECIENTE")

    def test_backup_iniciado_y_no_terminado(self):
        eventos = SANOS + [evento("Backing up DB instance", dt.timedelta(hours=2, seconds=1))]
        self.falla_con(CLIFalsa(eventos=eventos), "BACKUP_ATASCADO")

    def test_backups_desactivados_en_los_eventos(self):
        eventos = SANOS + [evento("Disabled automated backups", dt.timedelta(days=3),
                                  categorias=("configuration change",))]
        self.falla_con(CLIFalsa(eventos=eventos), "BACKUPS_DESACTIVADOS_EN_EVENTOS")

    def test_evento_de_fallo_de_instancia(self):
        eventos = SANOS + [evento("DB instance put into incompatible-restore state. RDS recommends that you initiate "
                                  "a point-in-time-restore.", dt.timedelta(days=1), categorias=("failure",))]
        self.falla_con(CLIFalsa(eventos=eventos), "FALLO_DE_INSTANCIA")

    # --- PITR ---------------------------------------------------------------------

    def test_pitr_sin_dato(self):
        datos = instancia()
        datos.pop("LatestRestorableTime")
        self.falla_con(CLIFalsa(instancia_=datos), "PITR_SIN_DATOS")

    def test_pitr_retrasado(self):
        cli = CLIFalsa(instancia_=instancia(LatestRestorableTime=iso(AHORA - dt.timedelta(minutes=15, seconds=1))))
        self.falla_con(cli, "PITR_RETRASADO")

    def test_reloj_desfasado(self):
        cli = CLIFalsa(instancia_=instancia(LatestRestorableTime=iso(AHORA + dt.timedelta(minutes=5, seconds=1))))
        self.falla_con(cli, "RELOJ_DESFASADO")

    def test_varios_hallazgos_ordenados(self):
        cli = CLIFalsa(instancia_=instancia(DBInstanceStatus="stopped", BackupRetentionPeriod=0,
                                            LatestRestorableTime=iso(AHORA - dt.timedelta(hours=3))), eventos=[])
        self.falla_con(cli, "INSTANCIA_NO_DISPONIBLE", "BACKUPS_DESACTIVADOS", "PITR_RETRASADO", "SIN_BACKUP_RECIENTE")

    # --- Fallos de la AWS CLI, credenciales e identidad -----------------------

    def test_credenciales_caducadas(self):
        for mensaje in ("aws: [ERROR]: Your session has expired. Please reauthenticate using 'aws login'.",
                        "An error occurred (ExpiredToken) when calling the GetCallerIdentity operation: expired",
                        "An error occurred (RequestExpired) when calling the DescribeEvents operation",
                        "Unable to locate credentials. You can configure credentials by running \"aws login\"."):
            with self.subTest(mensaje=mensaje):
                for comando in (("sts", "get-caller-identity"), ("rds", "describe-events")):
                    codigo, r = self.correr(CLIFalsa(fallos={comando: (255, "", mensaje)}))
                    self.assertEqual((codigo, r), (4, {"estado": "CREDENCIALES_CADUCADAS"}))

    def test_error_de_aws_sin_eco_del_mensaje(self):
        fallo = (254, "", f"An error occurred (ThrottlingException) for arn:aws:rds:us-east-2:{CUENTA}:db:x")
        codigo, r = self.correr(CLIFalsa(fallos={("rds", "describe-events"): fallo}))
        self.assertEqual((codigo, r), (3, {"estado": "ERROR_DE_AWS", "codigo": "ThrottlingException"}))

    def test_error_de_aws_sin_codigo_reconocible(self):
        codigo, r = self.correr(CLIFalsa(fallos={("rds", "describe-db-instances"): (1, "", "fallo de red")}))
        self.assertEqual((codigo, r), (3, {"estado": "ERROR_DE_AWS", "codigo": "DESCONOCIDO"}))

    def test_cli_no_instalada(self):
        codigo, r = self.correr(CLIFalsa(fallos={("sts", "get-caller-identity"): FileNotFoundError("aws")}))
        self.assertEqual((codigo, r), (3, {"estado": "ERROR_DE_AWS", "codigo": "CLI_NO_ENCONTRADA"}))

    def test_salida_ilegible(self):
        for comando, salida in ((("rds", "describe-events"), "no es json"),
                                (("rds", "describe-db-instances"), json.dumps({"DBInstances": []})),
                                (("rds", "describe-events"), json.dumps({"Events": [{"Message": "x"}]}))):
            with self.subTest(comando=comando, salida=salida):
                codigo, r = self.correr(CLIFalsa(fallos={comando: (0, salida, "")}))
                self.assertEqual((codigo, r), (3, {"estado": "ERROR_DE_AWS", "codigo": "SALIDA_ILEGIBLE"}))

    def test_identidad_no_autorizada(self):
        otra = f"arn:aws:sts::{CUENTA}:assumed-role/OtroRol/sesion"
        codigo, r = self.correr(CLIFalsa(identidad=otra))
        self.assertEqual((codigo, r), (5, {"estado": "IDENTIDAD_NO_AUTORIZADA"}))

    def test_sin_argumentos(self):
        with self.assertRaises(SystemExit) as salida, redirect_stdout(StringIO()):
            diag.main(["--lo-que-sea"])
        self.assertEqual(salida.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
