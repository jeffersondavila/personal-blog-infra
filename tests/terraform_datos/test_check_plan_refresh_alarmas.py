"""Guarda del REFRESH-ONLY de H-031-8 (Task/031 §47), aprobado por el usuario el 2026-10-15. Nunca aplica.

Tras crear las 8 alarmas, el state guardo sus tres listas de acciones como `null` y AWS las devuelve como `[]`: misma
semantica y ninguna accion. El fixture es el plan refresh-only que veria Terraform:
- `prior_state` refrescado con los 29 recursos;
- cero `resource_changes`;
- la deriva de las 8 alarmas;
- el atributo movil de RDS.
Cada prueba negativa rompe una sola cosa y exige su codigo.
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.terraform_datos.check_plan_alarmas import ALARMAS, direccion
from scripts.terraform_datos.check_plan_refresh_alarmas import LISTAS, check
from tests.terraform_datos.test_check_plan_alarmas import fixture as fixture_alarmas
from tests.terraform_datos.test_check_plan_convergencia import con_drift_movil
from tests.terraform_datos.test_check_plan_grafana import aplicado
from tests.terraform_datos.test_check_plan_recuperacion import ACCOUNT, MEDIOS, previo

AHORA = datetime(2026, 10, 5, 21, 0, 0, tzinfo=timezone.utc)
RAIZ = Path(__file__).resolve().parents[2]
INSTANCIA = "module.base_de_datos.aws_db_instance.this"


def deriva_de_alarma(plan, clave):
    """La deriva real: el state con las tres listas en `null` y AWS con `[]`. El `prior_state` ya esta refrescado."""
    recurso = previo(plan, direccion(clave))
    despues = copy.deepcopy(recurso["values"])
    for lista in LISTAS:
        despues[lista] = []
    recurso["values"] = copy.deepcopy(despues)
    antes = copy.deepcopy(despues)
    for lista in LISTAS:
        antes[lista] = None
    return {"address": direccion(clave), "mode": "managed", "type": "aws_cloudwatch_metric_alarm", "index": clave,
            "provider_name": "registry.terraform.io/hashicorp/aws",
            "change": {"actions": ["update"], "before": antes, "after": despues, "after_unknown": {}}}


def fixture(con_rds=True):
    plan = aplicado(fixture_alarmas())
    if con_rds:
        plan = con_drift_movil(plan)
    else:
        plan["resource_drift"] = []
    plan["resource_changes"] = []
    plan["applyable"] = True
    plan["resource_drift"] += [deriva_de_alarma(plan, clave) for clave in ALARMAS]
    return plan


def entrada(plan, address):
    return next(e for e in plan["resource_drift"] if e["address"] == address)


class RefreshDeLasAlarmas(unittest.TestCase):
    def pasa(self, plan, ahora=AHORA):
        return check(plan, ACCOUNT, MEDIOS, ahora=ahora)

    def rechaza(self, plan, codigo):
        with self.assertRaises(ValueError) as error:
            self.pasa(plan)
        self.assertEqual(str(error.exception), codigo)

    # --- Positivos ------------------------------------------------------------

    def test_las_ocho_alarmas_y_el_atributo_movil(self):
        r = self.pasa(fixture())
        self.assertEqual(r["gate"], "ALARMS_REFRESH_OK")
        self.assertEqual((r["resource_changes"], r["add"], r["change"], r["destroy"], r["resource_drift"]),
                         (0, 0, 0, 0, 9))
        self.assertEqual(r["normalizadas"], sorted(direccion(c) for c in ALARMAS))
        self.assertEqual(r["drift_movil"], [f"{INSTANCIA}: latest_restorable_time"])

    def test_sin_el_atributo_movil(self):
        r = self.pasa(fixture(con_rds=False))
        self.assertEqual((r["gate"], r["resource_drift"], r["drift_movil"]), ("ALARMS_REFRESH_OK", 8, []))

    # --- Plan y variables -----------------------------------------------------

    def test_globales(self):
        for clave, valor, codigo in (("terraform_version", "1.16.1", "VERSION"), ("applyable", False, "INCOMPLETE"),
                                     ("complete", False, "INCOMPLETE"), ("errored", True, "INCOMPLETE"),
                                     ("deferred_changes", [{"reason": "x"}], "DEFERRED")):
            with self.subTest(clave=clave):
                plan = fixture()
                plan[clave] = valor
                self.rechaza(plan, codigo)

    def test_un_refresh_only_no_tiene_cambios_de_recursos(self):
        plan = fixture()
        plan["resource_changes"] = [{"address": direccion("cpu"), "change": {"actions": ["no-op"]}}]
        self.rechaza(plan, "RESOURCE_CHANGES")

    def test_variables(self):
        for romper, codigo in (
                (lambda v: v["version_de_la_contrasena"].update(value=2), "PASSWORD_VERSION"),
                (lambda v: v["dias_de_retencion_de_backups"].update(value=7), "RETENTION"),
                (lambda v: v.update(zip_de_la_ejecutora={"value": {}}), "VARIABLES"),
                (lambda v: v.update(integracion_grafana={"value": {}}), "VARIABLES")):
            with self.subTest(codigo=codigo):
                plan = fixture()
                romper(plan["variables"])
                self.rechaza(plan, codigo)

    def test_checks(self):
        plan = fixture()
        plan["checks"][0]["status"] = "fail"
        with self.assertRaises(ValueError) as error:
            self.pasa(plan)
        self.assertIn(str(error.exception), ("IDENTITY_CHECK", "CHECKS"))

    # --- State previo ---------------------------------------------------------

    def test_state_previo_sin_una_alarma(self):
        plan = fixture()
        for modulo in plan["prior_state"]["values"]["root_module"]["child_modules"]:
            modulo["resources"] = [r for r in modulo["resources"] if r["address"] != direccion("xid")]
        self.rechaza(plan, "PRIOR_STATE")

    def test_state_previo_con_taint(self):
        plan = fixture()
        previo(plan, direccion("cpu"))["tainted"] = True
        self.rechaza(plan, "PRIOR_STATE")

    # --- Deriva de las alarmas -------------------------------------------------

    def test_falta_la_deriva_de_una_alarma(self):
        plan = fixture()
        plan["resource_drift"] = [e for e in plan["resource_drift"] if e["address"] != direccion("memoria")]
        self.rechaza(plan, "ALARM_DRIFT")

    def test_deriva_duplicada(self):
        plan = fixture()
        plan["resource_drift"].append(copy.deepcopy(entrada(plan, direccion("cpu"))))
        self.rechaza(plan, "ALARM_DRIFT")

    def test_otro_atributo_de_una_alarma(self):
        plan = fixture()
        entrada(plan, direccion("cpu"))["change"]["after"]["threshold"] = 80
        self.rechaza(plan, "ALARM_DRIFT")

    def test_una_lista_con_acciones(self):
        for lista in LISTAS:
            with self.subTest(lista=lista):
                plan = fixture()
                entrada(plan, direccion("cpu"))["change"]["after"][lista] = ["arn:aws:sns:us-east-2:1:topico"]
                self.rechaza(plan, "ALARM_DRIFT")

    def test_una_lista_que_no_venia_de_null(self):
        plan = fixture()
        entrada(plan, direccion("cpu"))["change"]["before"]["ok_actions"] = ["arn:aws:sns:us-east-2:1:topico"]
        self.rechaza(plan, "ALARM_DRIFT")

    def test_una_lista_de_otra_forma(self):
        plan = fixture()
        entrada(plan, direccion("cpu"))["change"]["after"]["alarm_actions"] = ""
        self.rechaza(plan, "ALARM_DRIFT")

    def test_solo_dos_listas_cambian(self):
        plan = fixture()
        e = entrada(plan, direccion("cpu"))["change"]
        e["before"]["ok_actions"] = []
        self.rechaza(plan, "ALARM_DRIFT")

    def test_forma_de_la_entrada(self):
        for romper in (lambda e: e.update(type="aws_cloudwatch_composite_alarm"), lambda e: e.update(mode="data"),
                       lambda e: e.update(provider_name="otro"), lambda e: e.update(previous_address="x"),
                       lambda e: e["change"].update(actions=["delete", "create"]),
                       lambda e: e["change"].update(importing={"id": "x"}),
                       lambda e: e["change"].update(after_unknown={"arn": True})):
            with self.subTest(romper=romper):
                plan = fixture()
                romper(entrada(plan, direccion("cpu")))
                self.rechaza(plan, "ALARM_DRIFT")

    def test_prior_state_distinto_del_valor_refrescado(self):
        plan = fixture()
        previo(plan, direccion("cpu"))["values"]["alarm_actions"] = None
        self.rechaza(plan, "DRIFT_COHERENCE")

    # --- Resto de la deriva: caso A/B de §40, sin la excepcion de §47 ----------

    def test_deriva_de_otro_recurso(self):
        plan = fixture(con_rds=False)
        ajena = copy.deepcopy(entrada(plan, direccion("cpu")))
        ajena.update(address="module.red.aws_security_group.admin", type="aws_security_group")
        plan["resource_drift"].append(ajena)
        self.rechaza(plan, "DRIFT")

    def test_otro_atributo_de_rds(self):
        plan = fixture()
        entrada(plan, INSTANCIA)["change"]["after"]["publicly_accessible"] = True
        self.rechaza(plan, "DRIFT")

    def movil(self, antes, despues):
        plan = con_drift_movil(fixture(con_rds=False), antes=antes, despues=despues)
        plan["resource_changes"] = []
        plan["resource_drift"] += [deriva_de_alarma(plan, clave) for clave in ALARMAS]
        return plan

    def test_state_de_ocho_dias_con_aws_fresco_sin_excepcion(self):
        """Esta guarda sigue SIN la excepcion puntual de §47 y no la necesita: el contrato general de §40, enmendado
        el 2026-10-18 (aprobada el 2026-10-19), mide la frescura de AWS y no la antiguedad del state."""
        r = self.pasa(self.movil("2026-10-05T19:16:49Z", "2026-10-14T03:16:52Z"),
                      ahora=datetime(2026, 10, 14, 3, 27, 0, tzinfo=timezone.utc))
        self.assertEqual((r["gate"], r["resource_drift"]), ("ALARMS_REFRESH_OK", 9))

    def test_atributo_movil_de_aws_con_mas_de_24_h(self):
        with self.assertRaises(ValueError) as error:
            self.pasa(self.movil("2026-10-13T00:00:00Z", "2026-10-13T03:26:59Z"),
                      ahora=datetime(2026, 10, 14, 3, 27, 0, tzinfo=timezone.utc))
        self.assertEqual(str(error.exception), "MOVING_ATTRIBUTE")

    def test_rds_incoherente_con_el_prior_state(self):
        plan = fixture()
        previo(plan, INSTANCIA)["values"]["latest_restorable_time"] = "2026-10-05T19:16:49Z"
        self.rechaza(plan, "DRIFT_COHERENCE")

    # --- Configuracion y salidas ----------------------------------------------

    def test_cableado(self):
        for romper in (lambda m: m.update(ejecutor_privado={}), lambda m: m.update(lectura_grafana={}),
                       lambda m: m.pop("alarmas_rds")):
            with self.subTest(romper=romper):
                plan = fixture()
                romper(plan["configuration"]["root_module"]["module_calls"])
                self.rechaza(plan, "WIRING")

    def test_salidas(self):
        for romper in (lambda s: s["alarmas_de_rds"].update(actions=["update"]),
                       lambda s: s["alarmas_de_rds"].update(after={"cpu": "otra"}),
                       lambda s: s["alarmas_de_rds"].update(after_unknown=True),
                       lambda s: s["alarmas_de_rds"].update(after_sensitive=True),
                       lambda s: s.update(rol_de_grafana={"actions": ["create"], "before": None, "after": "x"}),
                       lambda s: s.pop("alarmas_de_rds")):
            with self.subTest(romper=romper):
                plan = fixture()
                romper(plan["output_changes"])
                self.rechaza(plan, "OUTPUTS")

    # --- CLI --------------------------------------------------------------------

    def test_cli(self):
        ahora = datetime.now(timezone.utc).replace(microsecond=0)
        plan = con_drift_movil(aplicado(fixture_alarmas()),
                               antes=(ahora - timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                               despues=(ahora - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        plan["resource_changes"] = []
        plan["applyable"] = True
        plan["resource_drift"] += [deriva_de_alarma(plan, clave) for clave in ALARMAS]
        malo = copy.deepcopy(plan)
        entrada(malo, direccion("cpu"))["change"]["after"]["threshold"] = 80
        with tempfile.TemporaryDirectory() as directorio:
            variables = Path(directorio) / "variables.json"
            variables.write_text(json.dumps({"expected_account_id": ACCOUNT, "arn_del_bucket_de_medios": MEDIOS}),
                                 encoding="utf-8")
            resultados = []
            for nombre, contenido in (("bueno.json", plan), ("malo.json", malo)):
                ruta = Path(directorio) / nombre
                ruta.write_text(json.dumps(contenido), encoding="utf-8")
                resultados.append(subprocess.run(
                    [sys.executable, "-B", "-m", "scripts.terraform_datos.check_plan_refresh_alarmas", str(ruta),
                     "--variables", str(variables)], cwd=RAIZ, capture_output=True, text=True))
        bueno, malo = resultados
        self.assertEqual(bueno.returncode, 0, bueno.stderr)
        self.assertEqual(json.loads(bueno.stdout)["gate"], "ALARMS_REFRESH_OK")
        self.assertNotEqual(malo.returncode, 0)
        self.assertIn("ALARM_DRIFT", malo.stderr)


if __name__ == "__main__":
    unittest.main()
