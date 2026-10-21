"""Guarda del REFRESH-ONLY de H-031-5 (Task/031), preparada ANTES del apply. Nunca aplica.

Leccion de H-031-8 y H-031-9: tras CREAR recursos, el primer plan trae deriva de normalizacion del provider. Esa
deriva la rechaza la guarda de convergencia, de lista cerrada. Para la ejecutora no se sabe de antemano que
atributos normalizara AWS, asi que la guarda admite solo dos formas:
- `null` -> `[]` / `{}`;
- el reflejo `inline_policy` del rol, identico a la politica en linea del state.
Todo lo demas es un STOP. El fixture es el plan refresh-only que veria Terraform tras aplicar H-031-5: 35 recursos
en un `prior_state` refrescado, cero `resource_changes` y deriva de normalizacion en la ejecutora mas el atributo
movil de RDS. Cada prueba negativa rompe una sola cosa y exige su codigo.
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.terraform_datos.check_plan_ejecutor import FUNCION, LOGS, POLITICA, ROL
from scripts.terraform_datos.check_plan_refresh_ejecutor import check
from tests.terraform_datos.test_check_plan_convergencia import con_drift_movil
from tests.terraform_datos.test_check_plan_convergencia_por_fase import ejecutora_aplicada
from tests.terraform_datos.test_check_plan_recuperacion import ACCOUNT, MEDIOS, previo

AHORA = datetime(2026, 10, 5, 21, 0, 0, tzinfo=timezone.utc)
RAIZ = Path(__file__).resolve().parents[2]
INSTANCIA = "module.base_de_datos.aws_db_instance.this"


def deriva(plan, address, tipo, antes, despues):
    """Entrada de `resource_drift` de normalizacion; el `prior_state` refrescado ya tiene el valor de AWS."""
    recurso = previo(plan, address)
    valores_despues = {**recurso["values"], **despues}
    valores_antes = {**valores_despues, **antes}
    recurso["values"] = copy.deepcopy(valores_despues)
    return {"address": address, "mode": "managed", "type": tipo, "provider_name": "registry.terraform.io/hashicorp/aws",
            "change": {"actions": ["update"], "before": valores_antes, "after": valores_despues, "after_unknown": {}}}


def reflejo(plan):
    politica = previo(plan, POLITICA)["values"]
    return [{"name": politica["name"], "policy": politica["policy"]}]


def fixture(con_rds=True, ahora=None):
    plan = ejecutora_aplicada()
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
    plan["resource_drift"] += [
        deriva(plan, ROL, "aws_iam_role", {"inline_policy": []}, {"inline_policy": reflejo(plan)}),
        deriva(plan, FUNCION, "aws_lambda_function", {"file_system_config": None, "image_config": None},
               {"file_system_config": [], "image_config": []}),
        deriva(plan, LOGS, "aws_cloudwatch_log_group", {"tags": None}, {"tags": {}}),
    ]
    return plan


def entrada(plan, address):
    return next(e for e in plan["resource_drift"] if e["address"] == address)


class RefreshDeLaEjecutora(unittest.TestCase):
    def pasa(self, plan, ahora=AHORA):
        return check(plan, ACCOUNT, MEDIOS, ahora=ahora)

    def rechaza(self, plan, codigo):
        with self.assertRaises(ValueError) as error:
            self.pasa(plan)
        self.assertEqual(str(error.exception), codigo)

    # --- Positivos ------------------------------------------------------------

    def test_normalizaciones_y_atributo_movil(self):
        r = self.pasa(fixture())
        self.assertEqual(r["gate"], "EXECUTOR_REFRESH_OK")
        self.assertEqual((r["resource_changes"], r["add"], r["change"], r["destroy"], r["resource_drift"]),
                         (0, 0, 0, 0, 4))
        self.assertEqual(r["normalizados"], sorted([f"{ROL}: inline_policy", f"{FUNCION}: file_system_config",
                                                    f"{FUNCION}: image_config", f"{LOGS}: tags"]))
        self.assertEqual(r["drift_movil"], [f"{INSTANCIA}: latest_restorable_time"])

    def test_solo_algunos_recursos_y_sin_rds(self):
        plan = fixture(con_rds=False)
        plan["resource_drift"] = [entrada(plan, ROL)]
        r = self.pasa(plan)
        self.assertEqual((r["resource_drift"], r["normalizados"], r["drift_movil"]),
                         (1, [f"{ROL}: inline_policy"], []))

    # --- Plan, variables y state ------------------------------------------------

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
        plan["resource_changes"] = [{"address": FUNCION, "change": {"actions": ["no-op"]}}]
        self.rechaza(plan, "RESOURCE_CHANGES")

    def test_variables(self):
        for romper, codigo in (
                (lambda v: v["version_de_la_contrasena"].update(value=2), "PASSWORD_VERSION"),
                (lambda v: v["dias_de_retencion_de_backups"].update(value=7), "RETENTION"),
                (lambda v: v["zip_de_la_ejecutora"]["value"].update(sha256="0" * 64), "ARTIFACT_PIN"),
                (lambda v: v.pop("integracion_grafana"), "VARIABLES")):
            with self.subTest(codigo=codigo):
                plan = fixture()
                romper(plan["variables"])
                self.rechaza(plan, codigo)

    def test_state_previo(self):
        plan = fixture()
        previo(plan, FUNCION)["tainted"] = True
        self.rechaza(plan, "PRIOR_STATE")
        plan = fixture()
        for modulo in plan["prior_state"]["values"]["root_module"]["child_modules"]:
            modulo["resources"] = [r for r in modulo["resources"] if r["address"] != LOGS]
        self.rechaza(plan, "PRIOR_STATE")

    # --- Deriva de la ejecutora: solo normalizacion ---------------------------

    def test_un_cambio_real_de_configuracion(self):
        for address, atributo, valor in ((FUNCION, "timeout", 60), (FUNCION, "reserved_concurrent_executions", 2),
                                         (LOGS, "retention_in_days", 7), (ROL, "max_session_duration", 7200)):
            with self.subTest(atributo=atributo):
                plan = fixture()
                entrada(plan, address)["change"]["after"][atributo] = valor
                self.rechaza(plan, "EXECUTOR_DRIFT")

    def test_null_a_una_coleccion_con_contenido_o_a_otro_tipo(self):
        for valor in (["algo"], {"clave": "valor"}, "", 0, False):
            with self.subTest(valor=valor):
                plan = fixture()
                cambio = entrada(plan, FUNCION)["change"]
                cambio["after"]["file_system_config"] = valor
                previo(plan, FUNCION)["values"]["file_system_config"] = valor
                self.rechaza(plan, "EXECUTOR_DRIFT")

    def test_vaciar_algo_que_tenia_valor(self):
        plan = fixture()
        cambio = entrada(plan, LOGS)["change"]
        cambio["before"]["tags"] = {"Name": "blog-prod-ejecutor"}
        self.rechaza(plan, "EXECUTOR_DRIFT")

    def test_reflejo_de_politica_distinto_del_state(self):
        otra = json.loads(previo(fixture(), POLITICA)["values"]["policy"])
        otra["Statement"].append({"Effect": "Allow", "Action": "s3:*", "Resource": "*"})
        for valor in ([{"name": "PersonalBlogEjecutorDatos-ejecucion", "policy": json.dumps(otra)}],
                      [{"name": "otra", "policy": previo(fixture(), POLITICA)["values"]["policy"]}],
                      reflejo(fixture()) * 2, [{"name": "PersonalBlogEjecutorDatos-ejecucion"}]):
            with self.subTest(valor=valor):
                plan = fixture()
                entrada(plan, ROL)["change"]["after"]["inline_policy"] = valor
                previo(plan, ROL)["values"]["inline_policy"] = valor
                self.rechaza(plan, "EXECUTOR_DRIFT")

    def test_reflejo_que_no_venia_vacio(self):
        plan = fixture()
        entrada(plan, ROL)["change"]["before"]["inline_policy"] = None
        self.rechaza(plan, "EXECUTOR_DRIFT")

    def test_forma_de_la_entrada(self):
        for romper in (lambda e: e.update(type="aws_lambda_alias"), lambda e: e.update(mode="data"),
                       lambda e: e.update(provider_name="otro"), lambda e: e.update(previous_address="x"),
                       lambda e: e["change"].update(actions=["delete", "create"]),
                       lambda e: e["change"].update(importing={"id": "x"}),
                       lambda e: e["change"].update(after_unknown={"arn": True})):
            with self.subTest(romper=romper):
                plan = fixture()
                romper(entrada(plan, FUNCION))
                self.rechaza(plan, "EXECUTOR_DRIFT")

    def test_deriva_duplicada(self):
        plan = fixture()
        plan["resource_drift"].append(copy.deepcopy(entrada(plan, LOGS)))
        self.rechaza(plan, "EXECUTOR_DRIFT")

    def test_prior_state_distinto_del_valor_refrescado(self):
        plan = fixture()
        previo(plan, FUNCION)["values"]["image_config"] = None
        self.rechaza(plan, "DRIFT_COHERENCE")

    # --- Resto de la deriva: caso A/B de §40 -----------------------------------

    def test_deriva_de_otro_recurso(self):
        """Recursos AJENOS a la ejecutora: su deriva sigue el caso A/B de §40, no la de normalizacion."""
        for address in ('module.alarmas_rds.aws_cloudwatch_metric_alarm.this["cpu"]',
                        "module.lectura_grafana.aws_iam_role.this"):
            with self.subTest(address=address):
                plan = fixture(con_rds=False)
                ajena = copy.deepcopy(entrada(plan, LOGS))
                ajena["address"] = address
                plan["resource_drift"].append(ajena)
                self.rechaza(plan, "DRIFT")

    def movil(self, valor_de_aws):
        plan = fixture()
        entrada(plan, INSTANCIA)["change"]["after"]["latest_restorable_time"] = valor_de_aws
        previo(plan, INSTANCIA)["values"]["latest_restorable_time"] = valor_de_aws
        return plan

    def test_state_de_dos_dias_con_aws_fresco(self):
        """Enmienda de §40 del 2026-10-18 (aprobada el 2026-10-19): la antiguedad del state no rechaza."""
        r = self.pasa(self.movil("2026-10-07T19:16:49Z"), ahora=datetime(2026, 10, 8, 0, 0, 0, tzinfo=timezone.utc))
        self.assertEqual((r["gate"], r["resource_drift"]), ("EXECUTOR_REFRESH_OK", 4))

    def test_atributo_movil_de_aws_con_mas_de_24_h(self):
        with self.assertRaises(ValueError) as error:
            self.pasa(self.movil("2026-10-05T20:00:00Z"), ahora=datetime(2026, 10, 6, 20, 0, 1, tzinfo=timezone.utc))
        self.assertEqual(str(error.exception), "MOVING_ATTRIBUTE")

    def test_rds_incoherente_con_el_prior_state(self):
        plan = fixture()
        previo(plan, INSTANCIA)["values"]["latest_restorable_time"] = "2026-10-05T19:16:49Z"
        self.rechaza(plan, "DRIFT_COHERENCE")

    # --- Configuracion y salidas ----------------------------------------------

    def test_cableado(self):
        for modulo in ("ejecutor_privado", "alarmas_rds", "lectura_grafana"):
            with self.subTest(modulo=modulo):
                plan = fixture()
                plan["configuration"]["root_module"]["module_calls"].pop(modulo)
                self.rechaza(plan, "WIRING")

    def test_salidas(self):
        for romper in (lambda s: s["arn_de_la_ejecutora"].update(actions=["update"]),
                       lambda s: s["nombre_de_la_ejecutora"].update(after="otra"),
                       lambda s: s["rol_de_grafana"].update(after_unknown=True),
                       lambda s: s["alarmas_de_rds"].update(after_sensitive=True),
                       lambda s: s.pop("nombre_de_la_ejecutora")):
            with self.subTest(romper=romper):
                plan = fixture()
                romper(plan["output_changes"])
                self.rechaza(plan, "OUTPUTS")

    # --- CLI --------------------------------------------------------------------

    def test_cli(self):
        plan = fixture(ahora=datetime.now(timezone.utc).replace(microsecond=0))
        malo = copy.deepcopy(plan)
        entrada(malo, FUNCION)["change"]["after"]["timeout"] = 60
        with tempfile.TemporaryDirectory() as directorio:
            variables = Path(directorio) / "variables.json"
            variables.write_text(json.dumps({"expected_account_id": ACCOUNT, "arn_del_bucket_de_medios": MEDIOS}),
                                 encoding="utf-8")
            resultados = []
            for nombre, contenido in (("bueno.json", plan), ("malo.json", malo)):
                ruta = Path(directorio) / nombre
                ruta.write_text(json.dumps(contenido), encoding="utf-8")
                resultados.append(subprocess.run(
                    [sys.executable, "-B", "-m", "scripts.terraform_datos.check_plan_refresh_ejecutor", str(ruta),
                     "--variables", str(variables)], cwd=RAIZ, capture_output=True, text=True))
        bueno, malo = resultados
        self.assertEqual(bueno.returncode, 0, bueno.stderr)
        self.assertEqual(json.loads(bueno.stdout)["gate"], "EXECUTOR_REFRESH_OK")
        self.assertNotEqual(malo.returncode, 0)
        self.assertIn("EXECUTOR_DRIFT", malo.stderr)


if __name__ == "__main__":
    unittest.main()
