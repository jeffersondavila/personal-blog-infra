"""Guarda del REFRESH-ONLY de H-031-9 (Task/031 §47), aprobado por el usuario el 2026-10-15. Nunca aplica.

Tras crear el rol de D-20 y su politica en linea, AWS devuelve en el rol dos atributos que el state no tenia:
- `inline_policy` con esa politica, que crea el recurso `aws_iam_role_policy`;
- `tags` como `{}` en vez de `null`.

El fixture es el plan refresh-only que veria Terraform: `prior_state` refrescado con 31 recursos, cero
`resource_changes`, esa deriva del rol y el atributo movil de RDS. Cada prueba negativa rompe una sola cosa y exige su
codigo.
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.terraform_datos.check_plan_grafana import NOMBRE_DEL_ROL, POLITICA, ROL, permisos
from scripts.terraform_datos.check_plan_refresh_grafana import check
from tests.terraform_datos.test_check_plan_convergencia import con_drift_movil
from tests.terraform_datos.test_check_plan_grafana import EXTERNAL_ID, GRAFANA, aplicado
from tests.terraform_datos.test_check_plan_grafana import fixture as fixture_grafana
from tests.terraform_datos.test_check_plan_recuperacion import ACCOUNT, MEDIOS, previo

AHORA = datetime(2026, 10, 5, 21, 0, 0, tzinfo=timezone.utc)
RAIZ = Path(__file__).resolve().parents[2]
INSTANCIA = "module.base_de_datos.aws_db_instance.this"


def politica_en_linea(account=ACCOUNT):
    return [{"name": f"{NOMBRE_DEL_ROL}-lectura", "policy": json.dumps(permisos(account))}]


def deriva_del_rol(plan):
    recurso = previo(plan, ROL)
    despues = copy.deepcopy(recurso["values"])
    despues.update(inline_policy=politica_en_linea(), tags={})
    recurso["values"] = copy.deepcopy(despues)
    antes = copy.deepcopy(despues)
    antes.update(inline_policy=[], tags=None)
    return {"address": ROL, "mode": "managed", "type": "aws_iam_role",
            "provider_name": "registry.terraform.io/hashicorp/aws",
            "change": {"actions": ["update"], "before": antes, "after": despues, "after_unknown": {}}}


def fixture(con_rds=True, ahora=None):
    plan = aplicado(fixture_grafana())
    if con_rds:
        if ahora is None:
            plan = con_drift_movil(plan)
        else:
            plan = con_drift_movil(plan, antes=(ahora - timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                   despues=(ahora - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"))
    else:
        plan["resource_drift"] = []
    plan["resource_changes"] = []
    plan["applyable"] = True
    plan["resource_drift"].append(deriva_del_rol(plan))
    return plan


def rol(plan):
    return next(e for e in plan["resource_drift"] if e["address"] == ROL)


class RefreshDelRolDeGrafana(unittest.TestCase):
    def pasa(self, plan, ahora=AHORA):
        return check(plan, ACCOUNT, MEDIOS, GRAFANA, EXTERNAL_ID, ahora=ahora)

    def rechaza(self, plan, codigo):
        with self.assertRaises(ValueError) as error:
            self.pasa(plan)
        self.assertEqual(str(error.exception), codigo)

    # --- Positivos ------------------------------------------------------------

    def test_el_rol_y_el_atributo_movil(self):
        r = self.pasa(fixture())
        self.assertEqual(r["gate"], "GRAFANA_ROLE_REFRESH_OK")
        self.assertEqual((r["resource_changes"], r["add"], r["change"], r["destroy"], r["resource_drift"]),
                         (0, 0, 0, 0, 2))
        self.assertEqual(r["normalizados"], ["inline_policy", "tags"])
        self.assertEqual(r["drift_movil"], [f"{INSTANCIA}: latest_restorable_time"])

    def test_sin_el_atributo_movil(self):
        r = self.pasa(fixture(con_rds=False))
        self.assertEqual((r["gate"], r["resource_drift"], r["drift_movil"]), ("GRAFANA_ROLE_REFRESH_OK", 1, []))

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
        plan["resource_changes"] = [{"address": ROL, "change": {"actions": ["no-op"]}}]
        self.rechaza(plan, "RESOURCE_CHANGES")

    def test_variables(self):
        for romper, codigo in (
                (lambda v: v["version_de_la_contrasena"].update(value=2), "PASSWORD_VERSION"),
                (lambda v: v["dias_de_retencion_de_backups"].update(value=7), "RETENTION"),
                (lambda v: v.update(zip_de_la_ejecutora={"value": {}}), "VARIABLES"),
                (lambda v: v["integracion_grafana"].update(value={"cuenta": "000000000000",
                                                                  "external_id": EXTERNAL_ID}), "GRAFANA"),
                (lambda v: v.pop("integracion_grafana"), "GRAFANA")):
            with self.subTest(codigo=codigo):
                plan = fixture()
                romper(plan["variables"])
                self.rechaza(plan, codigo)

    # --- State previo ---------------------------------------------------------

    def test_state_previo_sin_la_politica(self):
        plan = fixture()
        for modulo in plan["prior_state"]["values"]["root_module"]["child_modules"]:
            modulo["resources"] = [r for r in modulo["resources"] if r["address"] != POLITICA]
        self.rechaza(plan, "PRIOR_STATE")

    def test_state_previo_con_taint(self):
        plan = fixture()
        previo(plan, ROL)["tainted"] = True
        self.rechaza(plan, "PRIOR_STATE")

    # --- Deriva del rol ---------------------------------------------------------

    def test_falta_la_deriva_del_rol(self):
        plan = fixture()
        plan["resource_drift"] = [e for e in plan["resource_drift"] if e["address"] != ROL]
        self.rechaza(plan, "ROLE_DRIFT")

    def test_deriva_duplicada(self):
        plan = fixture()
        plan["resource_drift"].append(copy.deepcopy(rol(plan)))
        self.rechaza(plan, "ROLE_DRIFT")

    def test_otro_atributo_del_rol(self):
        for atributo, valor in (("assume_role_policy", json.dumps({"Version": "2012-10-17", "Statement": []})),
                                ("max_session_duration", 43200), ("description", "otra"),
                                ("managed_policy_arns", ["arn:aws:iam::aws:policy/ReadOnlyAccess"])):
            with self.subTest(atributo=atributo):
                plan = fixture()
                rol(plan)["change"]["after"][atributo] = valor
                self.rechaza(plan, "ROLE_DRIFT")

    def test_politica_en_linea_distinta(self):
        otra = permisos(ACCOUNT)
        otra["Statement"][0]["Action"] = ["cloudwatch:*"]
        for valor in ([{"name": f"{NOMBRE_DEL_ROL}-lectura", "policy": json.dumps(otra)}],
                      [{"name": "otra", "policy": json.dumps(permisos(ACCOUNT))}],
                      politica_en_linea() * 2, [], politica_en_linea("000000000000")):
            with self.subTest(valor=valor):
                plan = fixture()
                rol(plan)["change"]["after"]["inline_policy"] = valor
                self.rechaza(plan, "ROLE_DRIFT")

    def test_politica_en_linea_que_no_venia_vacia(self):
        plan = fixture()
        rol(plan)["change"]["before"]["inline_policy"] = politica_en_linea()
        self.rechaza(plan, "ROLE_DRIFT")

    def test_tags_con_contenido_o_de_otra_forma(self):
        for antes, despues in ((None, {"Name": "x"}), ({}, {}), (None, None), (None, [])):
            with self.subTest(antes=antes, despues=despues):
                plan = fixture()
                cambio = rol(plan)["change"]
                cambio["before"]["tags"], cambio["after"]["tags"] = antes, despues
                self.rechaza(plan, "ROLE_DRIFT")

    def test_forma_de_la_entrada(self):
        for romper in (lambda e: e.update(type="aws_iam_user"), lambda e: e.update(mode="data"),
                       lambda e: e.update(provider_name="otro"), lambda e: e.update(previous_address="x"),
                       lambda e: e["change"].update(actions=["delete", "create"]),
                       lambda e: e["change"].update(importing={"id": "x"}),
                       lambda e: e["change"].update(after_unknown={"arn": True})):
            with self.subTest(romper=romper):
                plan = fixture()
                romper(rol(plan))
                self.rechaza(plan, "ROLE_DRIFT")

    def test_prior_state_distinto_del_valor_refrescado(self):
        plan = fixture()
        previo(plan, ROL)["values"]["tags"] = None
        self.rechaza(plan, "DRIFT_COHERENCE")

    # --- Resto de la deriva: caso A/B de §40 -----------------------------------

    def test_deriva_de_la_politica_o_de_una_alarma(self):
        for address in (POLITICA, 'module.alarmas_rds.aws_cloudwatch_metric_alarm.this["cpu"]'):
            with self.subTest(address=address):
                plan = fixture(con_rds=False)
                ajena = copy.deepcopy(rol(plan))
                ajena["address"] = address
                plan["resource_drift"].append(ajena)
                self.rechaza(plan, "DRIFT")

    def test_otro_atributo_de_rds(self):
        plan = fixture()
        next(e for e in plan["resource_drift"] if e["address"] == INSTANCIA)["change"]["after"]["publicly_accessible"] \
            = True
        self.rechaza(plan, "DRIFT")

    def movil(self, antes, despues):
        plan = con_drift_movil(fixture(con_rds=False), antes=antes, despues=despues)
        plan["resource_changes"] = []
        plan["resource_drift"].append(deriva_del_rol(plan))
        return plan

    def test_state_de_ocho_dias_con_aws_fresco(self):
        """El caso real de §47 (state del 2026-10-05, AWS del 2026-10-14) ya pasa por el contrato general de §40
        enmendado el 2026-10-18 (aprobado el 2026-10-19): mide la frescura de AWS, no la antiguedad del state."""
        r = self.pasa(self.movil("2026-10-05T19:16:49Z", "2026-10-14T03:16:52Z"),
                      ahora=datetime(2026, 10, 14, 3, 27, 0, tzinfo=timezone.utc))
        self.assertEqual((r["gate"], r["resource_drift"]), ("GRAFANA_ROLE_REFRESH_OK", 2))

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
        for romper in (lambda m: m.update(ejecutor_privado={}), lambda m: m.pop("lectura_grafana"),
                       lambda m: m.pop("alarmas_rds")):
            with self.subTest(romper=romper):
                plan = fixture()
                romper(plan["configuration"]["root_module"]["module_calls"])
                self.rechaza(plan, "WIRING")

    def test_salidas(self):
        for romper in (lambda s: s["rol_de_grafana"].update(actions=["update"]),
                       lambda s: s["rol_de_grafana"].update(after="otro"),
                       lambda s: s["alarmas_de_rds"].update(after_unknown=True),
                       lambda s: s["rol_de_grafana"].update(after_sensitive=True),
                       lambda s: s.pop("rol_de_grafana")):
            with self.subTest(romper=romper):
                plan = fixture()
                romper(plan["output_changes"])
                self.rechaza(plan, "OUTPUTS")

    # --- CLI --------------------------------------------------------------------

    def test_cli(self):
        plan = fixture(ahora=datetime.now(timezone.utc).replace(microsecond=0))
        malo = copy.deepcopy(plan)
        rol(malo)["change"]["after"]["tags"] = {"Name": "x"}
        with tempfile.TemporaryDirectory() as directorio:
            variables = Path(directorio) / "variables.json"
            variables.write_text(json.dumps({"expected_account_id": ACCOUNT, "arn_del_bucket_de_medios": MEDIOS,
                                             "integracion_grafana": {"cuenta": GRAFANA,
                                                                     "external_id": EXTERNAL_ID}}),
                                 encoding="utf-8")
            resultados = []
            for nombre, contenido in (("bueno.json", plan), ("malo.json", malo)):
                ruta = Path(directorio) / nombre
                ruta.write_text(json.dumps(contenido), encoding="utf-8")
                resultados.append(subprocess.run(
                    [sys.executable, "-B", "-m", "scripts.terraform_datos.check_plan_refresh_grafana", str(ruta),
                     "--variables", str(variables)], cwd=RAIZ, capture_output=True, text=True))
        bueno, malo = resultados
        self.assertEqual(bueno.returncode, 0, bueno.stderr)
        self.assertEqual(json.loads(bueno.stdout)["gate"], "GRAFANA_ROLE_REFRESH_OK")
        self.assertNotEqual(malo.returncode, 0)
        self.assertIn("ROLE_DRIFT", malo.stderr)


if __name__ == "__main__":
    unittest.main()
