"""H-031-7: restore sintetico con PITR a una instancia TEMPORAL, con tiempos medidos y limpieza guardada (Task/031).

Contrato que estas pruebas fijan ANTES del codigo (D-10 §10; §9.2 de las decisiones de RDS; prompt REMAINDER §4):
- `preflight` solo lee: productiva disponible, backups con retencion >= 1, PITR al dia, cifrada, privada; ninguna
  temporal previa. La salida no lleva host, cuenta ni ARN.
- `sembrar` crea el marcador NO sensible por la ejecutora (`sintetico`) y registra id, instante, huella y t0.
- `restaurar` REGISTRA el identificador exacto antes de crear; espera a que LatestRestorableTime cubra t0 con margen;
  restaura a esa marca una instancia privada, Single-AZ, misma clase, mismo subnet group, SOLO el grupo de RDS, sin
  backups, sin exportar logs (un grupo de logs nuevo naceria con retencion infinita), sin proteccion de borrado y
  etiquetada como temporal; espera `available`, relee y mide.
- `verificar` lee el marcador en la restaurada por la ejecutora y exige la misma huella.
- `limpiar` solo borra la temporal registrada por ESTA corrida, con etiquetas de temporal, distinta de la productiva;
  lista lo que borra, borra sin snapshot final ni backups, demuestra la ausencia por API y que la productiva sigue
  intacta; despues retira el marcador de la productiva.
- `informe` calcula RPO y RTO observados contra los objetivos de D-10 (15 min y 4 h).
"""
import contextlib
import datetime as dt
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.terraform_datos import restore_sintetico as rs

UTC = dt.timezone.utc
CUENTA = "123456789012"
HOST = "blog-prod-postgres.abcdefghijkl.us-east-2.rds.amazonaws.com"
TEMPORAL = "blog-prod-restore-h0317-20261007120000"
HUELLA = "a" * 64


class Reloj:
    def __init__(self):
        self.instante = dt.datetime(2026, 10, 7, 12, 0, 0, tzinfo=UTC)

    def ahora(self):
        return self.instante

    def dormir(self, segundos):
        self.instante += dt.timedelta(seconds=segundos)


class NoEncontrada(Exception):
    def __init__(self):
        super().__init__("DBInstanceNotFound")
        self.response = {"Error": {"Code": "DBInstanceNotFound", "Message": f"arn:aws:rds:us-east-2:{CUENTA}:db:x"}}


def produccion(reloj):
    return {
        "DBInstanceIdentifier": "blog-prod-postgres", "DBInstanceStatus": "available", "DbiResourceId": "db-PRODUCTIVA",
        "DBInstanceArn": f"arn:aws:rds:us-east-2:{CUENTA}:db:blog-prod-postgres",
        "Endpoint": {"Address": HOST, "Port": 5432}, "DBInstanceClass": "db.t4g.micro", "Engine": "postgres",
        "EngineVersion": "17.11", "StorageType": "gp3", "AllocatedStorage": 20, "MultiAZ": False,
        "PubliclyAccessible": False, "StorageEncrypted": True, "BackupRetentionPeriod": 1, "DeletionProtection": True,
        "DBSubnetGroup": {"DBSubnetGroupName": "blog-prod-datos"},
        "VpcSecurityGroups": [{"VpcSecurityGroupId": "sg-rds-simulado", "Status": "active"}],
        "DBParameterGroups": [{"DBParameterGroupName": "blog-prod-postgres17", "ParameterApplyStatus": "in-sync"}],
        "LatestRestorableTime": reloj.ahora() - dt.timedelta(minutes=4), "EnabledCloudwatchLogsExports": ["postgresql"],
        "TagList": [{"Key": "Proyecto", "Value": "personal-blog"}],
    }


class Rds:
    """RDS simulado: la temporal pasa de `creating` a `available` y de `deleting` a ausente tras unas lecturas."""

    def __init__(self, reloj, temporal_publica=False, previas=()):
        self.reloj, self.temporal_publica = reloj, temporal_publica
        self.instancias = {"blog-prod-postgres": produccion(reloj)}
        for previa in previas:
            self.instancias[previa] = {**produccion(reloj), "DBInstanceIdentifier": previa, "DbiResourceId": "db-PREVIA"}
        self.llamadas, self.lecturas = [], {}

    def _refrescar(self):
        self.instancias["blog-prod-postgres"]["LatestRestorableTime"] = self.reloj.ahora() - dt.timedelta(minutes=4)

    def describe_db_instances(self, DBInstanceIdentifier=None):
        self._refrescar()
        if DBInstanceIdentifier is None:
            return {"DBInstances": list(self.instancias.values())}
        instancia = self.instancias.get(DBInstanceIdentifier)
        if instancia is None:
            raise NoEncontrada()
        self.lecturas[DBInstanceIdentifier] = self.lecturas.get(DBInstanceIdentifier, 0) + 1
        if self.lecturas[DBInstanceIdentifier] >= 3 and instancia["DBInstanceStatus"] == "creating":
            instancia["DBInstanceStatus"] = "available"
        if self.lecturas[DBInstanceIdentifier] >= 3 and instancia["DBInstanceStatus"] == "deleting":
            del self.instancias[DBInstanceIdentifier]
            raise NoEncontrada()
        return {"DBInstances": [instancia]}

    def restore_db_instance_to_point_in_time(self, **parametros):
        self.llamadas.append(("restore", parametros))
        etiquetas = parametros["Tags"]
        self.instancias[parametros["TargetDBInstanceIdentifier"]] = {
            **produccion(self.reloj), "DBInstanceIdentifier": parametros["TargetDBInstanceIdentifier"],
            "DBInstanceStatus": "creating", "DbiResourceId": "db-TEMPORAL", "DeletionProtection": False,
            "BackupRetentionPeriod": 0, "EnabledCloudwatchLogsExports": [], "PubliclyAccessible": self.temporal_publica,
            "Endpoint": {"Address": f"{parametros['TargetDBInstanceIdentifier']}.abcdefghijkl.us-east-2.rds.amazonaws.com",
                         "Port": 5432},
            "TagList": etiquetas}
        self.lecturas[parametros["TargetDBInstanceIdentifier"]] = 0
        return {"DBInstance": {"DBInstanceIdentifier": parametros["TargetDBInstanceIdentifier"]}}

    def delete_db_instance(self, **parametros):
        self.llamadas.append(("delete", parametros))
        self.instancias[parametros["DBInstanceIdentifier"]]["DBInstanceStatus"] = "deleting"
        self.lecturas[parametros["DBInstanceIdentifier"]] = 0
        return {}

    def describe_db_instance_automated_backups(self, DBInstanceIdentifier):
        self.llamadas.append(("backups", DBInstanceIdentifier))
        return {"DBInstanceAutomatedBackups": []}


class Ejecutora:
    """Sustituye a `operar_ejecutora.invocar_modo`: responde como la ejecutora saneada."""

    def __init__(self, huella_restaurada=HUELLA):
        self.llamadas, self.huella_restaurada = [], huella_restaurada

    def __call__(self, argv, conexiones):
        self.llamadas.append(list(argv))
        if argv[0] == "sintetico" and argv[2] == "sembrar":
            return {"estado": "OK", "modo": "sintetico", "accion": "sembrar", "marcador": {"presente": True, "huella": HUELLA}}
        if argv[0] == "sintetico":
            return {"estado": "OK", "modo": "sintetico", "accion": "limpiar", "marcador": {"presente": False}}
        return {"estado": "OK", "modo": "verify", "marcador": {"presente": True, "huella": self.huella_restaurada}}


class Base(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.manifiesto = Path(self.temporal.name) / "manifiesto.json"
        self.reloj = Reloj()
        self.rds = Rds(self.reloj)
        self.ejecutora = Ejecutora()
        self.parches = [mock.patch.object(rs, "RELOJ", self.reloj.ahora), mock.patch.object(rs, "DORMIR", self.reloj.dormir),
                        mock.patch.object(rs.operador, "invocar_modo", self.ejecutora),
                        mock.patch.object(rs.operador, "_comprobar_identidad", lambda sts, secretos: None)]
        for parche in self.parches:
            parche.start()

    def tearDown(self):
        for parche in self.parches:
            parche.stop()
        self.temporal.cleanup()

    def conexiones(self):
        return {"sts": object(), "ssm": object(), "lambda": object(), "rds": self.rds}

    def ejecutar(self, *argv):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = rs.main([*argv, "--manifiesto", str(self.manifiesto)], clientes=self.conexiones)
        texto = salida.getvalue()
        for prohibido in (HOST, CUENTA, "arn:aws"):
            self.assertNotIn(prohibido, texto)
        if self.manifiesto.exists():
            for prohibido in (HOST, CUENTA, "arn:aws", ".rds.amazonaws.com"):
                self.assertNotIn(prohibido, self.manifiesto.read_text(encoding="utf-8"))
        return codigo, json.loads(texto)

    def leer(self):
        return json.loads(self.manifiesto.read_text(encoding="utf-8"))

    def hasta_restaurada(self):
        self.assertEqual(self.ejecutar("sembrar")[0], 0)
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL)[0], 0)


class Preflight(Base):
    def test_solo_lectura_y_saneado(self):
        codigo, salida = self.ejecutar("preflight")
        self.assertEqual(codigo, 0)
        self.assertEqual(salida, {"estado": "OK", "fase": "preflight", "productiva": {
            "disponible": True, "retencion_de_backups": 1, "retraso_de_pitr_s": 240, "cifrada": True, "publica": False,
            "clase": "db.t4g.micro", "motor": "17.11"}, "temporales_previas": 0})
        self.assertEqual([c for c in self.rds.llamadas if c[0] in ("restore", "delete")], [])

    def test_una_temporal_previa_detiene(self):
        self.rds = Rds(self.reloj, previas=("blog-prod-restore-h0317-20261001000000",))
        codigo, salida = self.ejecutar("preflight")
        self.assertEqual((codigo, salida), (1, {"estado": "TEMPORAL_PREVIA_EXISTENTE"}))


class Sembrar(Base):
    def test_registra_marcador_no_sensible_y_t0(self):
        codigo, salida = self.ejecutar("sembrar")
        self.assertEqual((codigo, salida["estado"]), (0, "OK"))
        marcador = self.leer()["marcador"]
        self.assertRegex(marcador["id"], r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
        self.assertEqual((marcador["instante"], marcador["huella"]), ("2026-10-07T12:00:00Z", HUELLA))
        self.assertEqual(marcador["t0"], "2026-10-07T12:00:00Z")
        self.assertEqual(self.ejecutora.llamadas, [["sintetico", "--accion", "sembrar", "--marcador", marcador["id"],
                                                    "--instante", "2026-10-07T12:00:00Z"]])


class Restaurar(Base):
    def test_parametros_exactos_de_la_temporal(self):
        prod = produccion(self.reloj)
        instante = dt.datetime(2026, 10, 7, 12, 1, 0, tzinfo=UTC)
        self.assertEqual(rs.parametros(prod, TEMPORAL, instante), {
            "SourceDBInstanceIdentifier": "blog-prod-postgres", "TargetDBInstanceIdentifier": TEMPORAL,
            "RestoreTime": instante, "DBInstanceClass": "db.t4g.micro", "DBSubnetGroupName": "blog-prod-datos",
            "VpcSecurityGroupIds": ["sg-rds-simulado"], "DBParameterGroupName": "blog-prod-postgres17",
            "StorageType": "gp3", "PubliclyAccessible": False, "MultiAZ": False, "BackupRetentionPeriod": 0,
            "EnableCloudwatchLogsExports": [], "DeletionProtection": False, "CopyTagsToSnapshot": False,
            "AutoMinorVersionUpgrade": False, "EnableIAMDatabaseAuthentication": False,
            "Tags": [{"Key": "Proyecto", "Value": "personal-blog"}, {"Key": "Entorno", "Value": "produccion"},
                     {"Key": "Gestion", "Value": "manual-H-031-7"}, {"Key": "Componente", "Value": "datos"},
                     {"Key": "Tarea", "Value": "Task/031"}, {"Key": "Proposito", "Value": "restore-sintetico-H-031-7"},
                     {"Key": "Temporal", "Value": "true"}, {"Key": "Name", "Value": TEMPORAL}]})

    def test_registra_el_identificador_antes_de_crear(self):
        vistos = []
        original = self.rds.restore_db_instance_to_point_in_time

        def restore(**parametros):
            vistos.append(self.leer().get("temporal", {}).get("identificador"))
            return original(**parametros)

        self.rds.restore_db_instance_to_point_in_time = restore
        self.hasta_restaurada()
        self.assertEqual(vistos, [TEMPORAL])

    def test_espera_al_pitr_restaura_mide_y_relee(self):
        self.hasta_restaurada()
        (restore,) = [p for c, p in self.rds.llamadas if c == "restore"]
        temporal = self.leer()["temporal"]
        t0 = dt.datetime(2026, 10, 7, 12, 0, 0, tzinfo=UTC)
        self.assertGreaterEqual(restore["RestoreTime"], t0 + dt.timedelta(seconds=60), "el PITR cubre el marcador")
        self.assertEqual(temporal["restore_time"], restore["RestoreTime"].strftime("%Y-%m-%dT%H:%M:%SZ"))
        self.assertEqual(temporal["dbi_resource_id"], "db-TEMPORAL")
        self.assertEqual(temporal["readback"], {"disponible": True, "publica": False, "cifrada": True,
                                                "mismos_grupos": True, "mismo_subnet_group": True, "misma_clase": True,
                                                "single_az": True, "sin_backups": True, "sin_exportar_logs": True,
                                                "sin_proteccion_de_borrado": True, "etiquetada_temporal": True})
        for marca in ("t_lrt", "t_solicitud", "t_disponible"):
            self.assertRegex(temporal[marca], r"^2026-10-07T\d{2}:\d{2}:\d{2}Z$")

    def test_identificadores_no_admitidos(self):
        self.ejecutar("sembrar")
        for identificador in ("blog-prod-postgres", "blog-prod-restore-h0317-2026", "otra"):
            with self.subTest(identificador=identificador):
                codigo, salida = self.ejecutar("restaurar", "--identificador", identificador)
                self.assertEqual((codigo, salida), (1, {"estado": "IDENTIFICADOR_NO_ADMITIDO"}))
        self.assertEqual([c for c in self.rds.llamadas if c[0] == "restore"], [])

    def test_sin_marcador_no_se_restaura(self):
        codigo, salida = self.ejecutar("restaurar", "--identificador", TEMPORAL)
        self.assertEqual((codigo, salida), (1, {"estado": "SIN_MARCADOR"}))

    def test_una_temporal_publica_detiene(self):
        self.rds = Rds(self.reloj, temporal_publica=True)
        self.ejecutar("sembrar")
        codigo, salida = self.ejecutar("restaurar", "--identificador", TEMPORAL)
        self.assertEqual((codigo, salida), (1, {"estado": "RESTAURADA_NO_CONFORME"}))
        self.assertFalse(self.leer()["temporal"]["readback"]["publica"] is False)


class VerificarYLimpiar(Base):
    def test_integridad_por_huella(self):
        self.hasta_restaurada()
        codigo, salida = self.ejecutar("verificar")
        self.assertEqual((codigo, salida["estado"]), (0, "OK"))
        marcador = self.leer()["marcador"]["id"]
        self.assertEqual(self.ejecutora.llamadas[-1], ["verify", "--usuario", "blog_migrate", "--restaurada", TEMPORAL,
                                                       "--marcador", marcador])
        self.assertTrue(self.leer()["verificacion"]["integridad"])

    def test_huella_distinta_es_un_fallo(self):
        self.ejecutora.huella_restaurada = "b" * 64
        self.hasta_restaurada()
        codigo, salida = self.ejecutar("verificar")
        self.assertEqual((codigo, salida), (1, {"estado": "INTEGRIDAD_FALLIDA"}))

    def test_limpiar_borra_solo_la_temporal_y_demuestra_ausencia(self):
        self.hasta_restaurada()
        self.ejecutar("verificar")
        codigo, salida = self.ejecutar("limpiar")
        self.assertEqual(codigo, 0)
        self.assertEqual(salida["se_elimina"], [{"tipo": "aws_db_instance", "identificador": TEMPORAL,
                                                 "dbi_resource_id": "db-TEMPORAL"}])
        self.assertEqual([p for c, p in self.rds.llamadas if c == "delete"],
                         [{"DBInstanceIdentifier": TEMPORAL, "SkipFinalSnapshot": True, "DeleteAutomatedBackups": True}])
        self.assertNotIn(TEMPORAL, self.rds.instancias)
        self.assertEqual(self.leer()["limpieza"]["ausente_por_api"], True)
        self.assertEqual(self.leer()["limpieza"]["backups_automaticos_restantes"], 0)
        self.assertEqual(self.leer()["limpieza"]["productiva_intacta"], True)
        self.assertEqual(self.ejecutora.llamadas[-1][:3], ["sintetico", "--accion", "limpiar"])

    def test_limpiar_exige_la_temporal_registrada_por_esta_corrida(self):
        self.hasta_restaurada()
        datos = self.leer()
        for cambio, descripcion in ((lambda d: d["temporal"].update(identificador="blog-prod-postgres"), "productiva"),
                                    (lambda d: d["temporal"].update(identificador="blog-prod-restore-h0317-20261001000000"),
                                     "otra temporal"),
                                    (lambda d: d["temporal"].update(dbi_resource_id="db-OTRA"), "otro recurso")):
            with self.subTest(descripcion=descripcion):
                alterado = json.loads(json.dumps(datos))
                cambio(alterado)
                self.manifiesto.write_text(json.dumps(alterado), encoding="utf-8")
                codigo, salida = self.ejecutar("limpiar")
                self.assertEqual((codigo, salida), (1, {"estado": "LIMPIEZA_NO_AUTORIZADA"}))
        self.assertEqual([c for c in self.rds.llamadas if c[0] == "delete"], [])

    def test_una_temporal_que_no_llega_a_available_se_puede_limpiar(self):
        class RdsLento(Rds):
            def describe_db_instances(self, DBInstanceIdentifier=None):
                respuesta = super().describe_db_instances(DBInstanceIdentifier)
                if DBInstanceIdentifier == TEMPORAL and respuesta["DBInstances"][0]["DBInstanceStatus"] == "available":
                    respuesta["DBInstances"][0]["DBInstanceStatus"] = "incompatible-restore"
                return respuesta

        self.rds = RdsLento(self.reloj)
        self.ejecutar("sembrar")
        codigo, salida = self.ejecutar("restaurar", "--identificador", TEMPORAL)
        self.assertEqual((codigo, salida), (1, {"estado": "TEMPORAL_NO_DISPONIBLE"}))
        self.assertEqual(self.leer()["temporal"]["dbi_resource_id"], "db-TEMPORAL", "registrada en cuanto aparece")
        self.rds.instancias[TEMPORAL]["DBInstanceStatus"] = "available"
        self.rds.__class__ = Rds
        codigo, salida = self.ejecutar("limpiar")
        self.assertEqual((codigo, salida["se_elimina"][0]["identificador"]), (0, TEMPORAL))

    def test_limpiar_exige_las_etiquetas_de_temporal(self):
        self.hasta_restaurada()
        self.rds.instancias[TEMPORAL]["TagList"] = [{"Key": "Proyecto", "Value": "personal-blog"}]
        codigo, salida = self.ejecutar("limpiar")
        self.assertEqual((codigo, salida), (1, {"estado": "LIMPIEZA_NO_AUTORIZADA"}))
        self.assertEqual([c for c in self.rds.llamadas if c[0] == "delete"], [])


class Informe(unittest.TestCase):
    def test_rpo_y_rto_observados(self):
        manifiesto = {
            "marcador": {"t0": "2026-10-07T12:00:00Z"},
            "temporal": {"t_lrt": "2026-10-07T12:05:00Z", "t_solicitud": "2026-10-07T12:05:10Z",
                         "restore_time": "2026-10-07T12:01:10Z", "t_disponible": "2026-10-07T12:20:10Z"},
            "verificacion": {"t_verificado": "2026-10-07T12:21:00Z", "integridad": True},
            "limpieza": {"t_limpieza": "2026-10-07T12:30:00Z"},
        }
        self.assertEqual(rs.informe(manifiesto), {
            "espera_hasta_pitr_s": 300, "restore_hasta_available_s": 900, "verificacion_s": 50, "total_s": 1260,
            "rpo_observado_s": 240, "rto_observado_s": 950, "objetivo_rpo_s": 900, "objetivo_rto_s": 14400,
            "rpo_cumple": True, "rto_cumple": True, "integridad": True})


if __name__ == "__main__":
    unittest.main()


class ClientesSinReinvocaciones(unittest.TestCase):
    """D-24 modificada el 2026-10-18 (aprobada el 2026-10-19): el restore invoca la ejecutora con los MISMOS clientes que el
    operador, cuyo cliente de Lambda no reintenta. Un error de red no se convierte en una segunda siembra."""

    def test_reutiliza_los_clientes_del_operador(self):
        centinela = {"sts": object(), "ssm": object(), "lambda": object(), "rds": object()}
        with mock.patch.object(rs.operador, "_clientes", return_value=centinela) as clientes:
            self.assertIs(rs._clientes(), centinela)
        clientes.assert_called_once_with()
