"""Guarda del plan productivo de H-031-8 (Task/031): alarmas de D-11, lista CERRADA. Nunca aplica.

Decision del usuario del 2026-10-08: el cableado de la ejecutora sale del root hasta que la cuota de Lambda lo
permita, y las fases que no dependen de ella se aplican antes. El fixture parte del plan de convergencia de H-031-3
(21 recursos en `no-op`, state 21/21 sin taint, salidas `no-op`) y le anade EXACTAMENTE las 8 alarmas y su salida.
Cada prueba negativa rompe una sola cosa y exige su codigo.
"""
import copy
import inspect
import json
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.terraform_datos.check_plan_alarmas import ALARMAS, NUEVOS, check, direccion
from tests.terraform_datos.test_check_plan_convergencia import con_drift_movil, fixture as fixture_convergencia
from tests.terraform_datos.test_check_plan_recuperacion import ACCOUNT, MEDIOS, previo

AHORA = datetime(2026, 10, 8, 18, 0, 0, tzinfo=timezone.utc)
#: Enmienda de §40 del 2026-10-18 (aprobada el 2026-10-19): el valor de AWS del caso B debe ser FRESCO respecto a `AHORA`
#: (24 h como maximo). Los valores por omision de `con_drift_movil` son del 2026-10-05: rancios para este reloj.
FRESCO = {"antes": "2026-10-08T17:00:00Z", "despues": "2026-10-08T17:50:00Z"}
RAIZ = Path(__file__).resolve().parents[2]


def alarma(clave):
    metrica, estadistico, percentil, periodo, puntos, umbral, operador = ALARMAS[clave]
    nombre = f"blog-prod-rds-{clave}"
    return {
        "actions_enabled": False, "alarm_actions": [], "alarm_description": f"Razon documentada de {clave} (D-11).",
        "alarm_name": nombre, "comparison_operator": operador, "datapoints_to_alarm": puntos,
        "dimensions": {"DBInstanceIdentifier": "blog-prod-postgres"},
        "evaluate_low_sample_count_percentiles": None, "evaluation_periods": puntos,
        "extended_statistic": percentil, "insufficient_data_actions": [], "metric_name": metrica, "metric_query": [],
        "namespace": "AWS/RDS", "ok_actions": [], "period": periodo, "region": "us-east-2", "statistic": estadistico,
        "tags": {"Name": nombre}, "threshold": umbral, "threshold_metric_id": None, "treat_missing_data": "missing",
        "unit": None,
    }


def fixture():
    plan = fixture_convergencia()
    plan["applyable"] = True
    for clave in ALARMAS:
        plan["resource_changes"].append({
            "address": direccion(clave), "mode": "managed", "type": "aws_cloudwatch_metric_alarm",
            "index": clave, "provider_name": "registry.terraform.io/hashicorp/aws",
            "change": {"actions": ["create"], "before": None, "after": alarma(clave),
                       "after_unknown": {"arn": True, "id": True, "tags_all": True}}})
    plan["output_changes"]["alarmas_de_rds"] = {
        "actions": ["create"], "before": None, "after": {c: f"blog-prod-rds-{c}" for c in ALARMAS},
        "after_unknown": False, "after_sensitive": False}
    raiz = plan["configuration"]["root_module"]
    raiz["outputs"]["alarmas_de_rds"] = {}
    raiz["module_calls"]["alarmas_rds"] = {
        "source": "../terraform/modulos/alarmas_rds",
        "expressions": {
            "nombre": {"references": ["var.prefijo"]},
            "identificador_de_la_instancia": {"references": ["module.base_de_datos.identificador",
                                                             "module.base_de_datos"]},
        },
        "module": {"resources": [{"address": "aws_cloudwatch_metric_alarm.this", "expressions": {}}]},
    }
    return plan


def despues(plan, clave):
    return next(i for i in plan["resource_changes"] if i["address"] == direccion(clave))["change"]["after"]


class PlanDeAlarmas(unittest.TestCase):
    def pasa(self, plan):
        return check(plan, ACCOUNT, MEDIOS, ahora=AHORA)

    def rechaza(self, plan, codigo):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS, ahora=AHORA)
        self.assertEqual(str(error.exception), codigo)

    # --- Positivos ------------------------------------------------------------

    def test_caso_a_ocho_creates_y_nada_mas(self):
        r = self.pasa(fixture())
        self.assertEqual(r["gate"], "ALARMS_PLAN_OK")
        self.assertEqual((r["add"], r["change"], r["destroy"], r["replace"], r["deferred_changes"]), (8, 0, 0, 0, 0))
        self.assertEqual(r["resource_drift"], 0)
        self.assertEqual(r["inventario"], sorted(NUEVOS))
        self.assertLessEqual(r["alarmas_tras_el_apply"], 10)

    def test_caso_b_solo_el_atributo_movil(self):
        r = self.pasa(con_drift_movil(fixture(), **FRESCO))
        self.assertEqual((r["gate"], r["resource_drift"]), ("ALARMS_PLAN_OK", 1))
        self.assertEqual(r["drift_movil"], ["module.base_de_datos.aws_db_instance.this: latest_restorable_time"])

    def test_catalogo_de_la_guarda_igual_al_del_modulo(self):
        # La tabla de `terraform-datos/tests/fases_h0318.tftest.hcl` es la que `terraform test` contrasta con el
        # modulo (y las mutaciones demuestran que lo detecta): la guarda exige EXACTAMENTE esa tabla.
        texto = (RAIZ / "terraform-datos" / "tests" / "fases_h0318.tftest.hcl").read_text(encoding="utf-8")
        tabla = {}
        for clave, lista in re.findall(r'^\s+(\w+)\s+= (\[".+\])$', texto, flags=re.M):
            metrica, estadistico, periodo, evaluaciones, puntos, umbral, operador = json.loads(lista)
            self.assertEqual(evaluaciones, puntos)
            tabla[clave] = (metrica, estadistico, periodo, puntos, umbral, operador)
        self.assertEqual(tabla, {clave: (m, e or p, per, pts, u, op)
                                 for clave, (m, e, p, per, pts, u, op) in ALARMAS.items()})

    # --- Conjunto de recursos ---------------------------------------------------

    def test_falta_una_alarma(self):
        plan = fixture()
        plan["resource_changes"] = [i for i in plan["resource_changes"] if i["address"] != direccion("xid")]
        self.rechaza(plan, "RESOURCE_SET")

    def test_un_recurso_inesperado(self):
        plan = fixture()
        extra = copy.deepcopy(plan["resource_changes"][-1])
        extra["address"] = "module.alarmas_rds.aws_cloudwatch_metric_alarm.this[\"backup\"]"
        plan["resource_changes"].append(extra)
        self.rechaza(plan, "UNEXPECTED_RESOURCE")

    def test_la_ejecutora_no_puede_volver_en_esta_fase(self):
        plan = fixture()
        plan["resource_changes"].append({
            "address": "module.ejecutor_privado.aws_lambda_function.this", "mode": "managed",
            "type": "aws_lambda_function", "provider_name": "registry.terraform.io/hashicorp/aws",
            "change": {"actions": ["create"], "before": None, "after": {}, "after_unknown": {}}})
        self.rechaza(plan, "UNEXPECTED_RESOURCE")

    def test_un_recurso_existente_cambia(self):
        plan = fixture()
        cambio = next(i for i in plan["resource_changes"] if i["address"] == "module.red.aws_vpc.this")["change"]
        cambio["actions"] = ["update"]
        self.rechaza(plan, "EXISTING_CHANGED")

    def test_import_o_move(self):
        plan = fixture()
        plan["resource_changes"][-1]["change"]["importing"] = {"id": "x"}
        self.rechaza(plan, "IMPORT_MOVE")

    def test_state_previo_con_taint(self):
        plan = fixture()
        previo(plan, "module.red.aws_vpc.this")["tainted"] = True
        self.rechaza(plan, "PRIOR_STATE")

    # --- Atributos de las alarmas -------------------------------------------------

    def test_cada_atributo_critico(self):
        casos = (
            ("cpu", "threshold", 80), ("cpu", "comparison_operator", "GreaterThanOrEqualToThreshold"),
            ("cpu", "period", 300), ("cpu", "evaluation_periods", 3), ("cpu", "datapoints_to_alarm", 3),
            ("almacenamiento", "statistic", "Average"), ("lectura", "extended_statistic", "p99"),
            ("lectura", "statistic", "Average"), ("memoria", "metric_name", "SwapUsage"),
            ("cpu", "namespace", "AWS/EC2"), ("cpu", "dimensions", {"DBInstanceIdentifier": "otra"}),
            ("cpu", "dimensions", {"DBInstanceIdentifier": "blog-prod-postgres", "Extra": "x"}),
            ("cpu", "treat_missing_data", "breaching"), ("cpu", "alarm_name", "otra-cpu"),
            ("cpu", "unit", "Percent"), ("cpu", "threshold_metric_id", "m1"),
            ("cpu", "metric_query", [{"id": "m1"}]), ("cpu", "region", "us-east-1"),
            ("cpu", "tags", {"Name": "otra"}), ("cpu", "alarm_description", ""),
        )
        for clave, atributo, valor in casos:
            with self.subTest(clave=clave, atributo=atributo):
                plan = fixture()
                despues(plan, clave)[atributo] = valor
                self.rechaza(plan, "ALARM")

    def test_sin_acciones_ni_destinatarios(self):
        for atributo, valor in (("actions_enabled", True), ("alarm_actions", ["arn:aws:sns:us-east-2:1:t"]),
                                ("ok_actions", ["arn:aws:sns:us-east-2:1:t"]),
                                ("insufficient_data_actions", ["arn:aws:sns:us-east-2:1:t"])):
            with self.subTest(atributo=atributo):
                plan = fixture()
                despues(plan, "cpu")[atributo] = valor
                self.rechaza(plan, "ALARM_ACTIONS")

    def test_atributo_critico_desconocido(self):
        plan = fixture()
        cambio = next(i for i in plan["resource_changes"] if i["address"] == direccion("cpu"))["change"]
        cambio["after_unknown"]["dimensions"] = True
        self.rechaza(plan, "UNVERIFIABLE")

    # --- Cableado, salidas, variables y drift -----------------------------------------

    def test_cableado(self):
        casos = (
            lambda r: r["module_calls"]["alarmas_rds"]["expressions"].update(
                identificador_de_la_instancia={"constant_value": "blog-prod-postgres"}),
            lambda r: r["module_calls"]["alarmas_rds"].update(source="../otro"),
            lambda r: r["module_calls"].update(ejecutor_privado={"source": "../terraform/modulos/ejecutor_privado"}),
        )
        for romper in casos:
            with self.subTest():
                plan = fixture()
                romper(plan["configuration"]["root_module"])
                self.rechaza(plan, "WIRING")

    def test_salidas(self):
        plan = fixture()
        plan["output_changes"]["alarmas_de_rds"]["after"]["cpu"] = "otra"
        self.rechaza(plan, "OUTPUTS")
        plan = fixture()
        plan["output_changes"]["arn_de_la_ejecutora"] = {"actions": ["create"], "before": None, "after_unknown": True}
        self.rechaza(plan, "OUTPUTS")
        plan = fixture()
        plan["output_changes"]["id_de_vpc"]["actions"] = ["update"]
        self.rechaza(plan, "OUTPUTS")

    def test_variables_y_globales(self):
        for romper, codigo in (
            (lambda p: p.update(applyable=False), "APPLYABLE"),
            (lambda p: p.update(terraform_version="1.15.0"), "VERSION"),
            (lambda p: p["variables"]["dias_de_retencion_de_backups"].update(value=7), "RETENTION"),
            (lambda p: p["variables"]["version_de_la_contrasena"].update(value=2), "PASSWORD_VERSION"),
            (lambda p: p.update(deferred_changes=[{"reason": "x"}]), "DEFERRED"),
            (lambda p: p["variables"].update(zip_de_la_ejecutora={"value": {"ruta": "x.zip", "sha256": "0" * 64}}),
             "EXECUTOR_VARIABLE"),
        ):
            with self.subTest(codigo=codigo):
                plan = fixture()
                romper(plan)
                self.rechaza(plan, codigo)

    def test_drift_ajeno_rechazado(self):
        plan = con_drift_movil(fixture())
        plan["resource_drift"][0]["change"]["after"]["publicly_accessible"] = True
        self.rechaza(plan, "DRIFT")


#: Excepcion PUNTUAL de §47, aprobada por el usuario el 2026-10-13: el state no se escribe desde el 2026-10-05 y la
#: diferencia del atributo movil (8 d 8 h) supera la ventana de 24 h de §40.
APROBADO = "2026-10-05T19:16:49Z"
AHORA_REAL = datetime(2026, 10, 14, 3, 27, 0, tzinfo=timezone.utc)
AWS_REAL = "2026-10-14T03:16:52Z"
MOVIL = ["module.base_de_datos.aws_db_instance.this: latest_restorable_time"]


class ExcepcionPuntualDeLaVentanaMovil(unittest.TestCase):
    """Solo con `excepcion_ventana_movil` y solo para el instante aprobado, la diferencia state -> AWS puede superar
    24 h; AWS sigue sin poder estar en el futuro, ser anterior al state ni tener mas de 24 h.

    Enmienda de §40 del 2026-10-18 (aprobada el 2026-10-19): el contrato GENERAL ya mide la frescura de
    AWS y no la antiguedad del state, asi que el caso real de §47 pasa tambien sin la excepcion. La excepcion queda
    como historia, sin cambios y mas estricta que el contrato general: exige ademas el instante aprobado."""

    def evaluar(self, plan, excepcion=APROBADO, ahora=AHORA_REAL):
        return check(plan, ACCOUNT, MEDIOS, ahora=ahora, excepcion_ventana_movil=excepcion)

    def rechaza(self, plan, codigo, **kwargs):
        with self.assertRaises(ValueError) as error:
            self.evaluar(plan, **kwargs)
        self.assertEqual(str(error.exception), codigo)

    def real(self, antes=APROBADO, despues=AWS_REAL):
        return con_drift_movil(fixture(), antes=antes, despues=despues)

    def test_sin_la_excepcion_el_contrato_general_acepta_el_caso_real(self):
        r = check(self.real(), ACCOUNT, MEDIOS, ahora=AHORA_REAL)
        self.assertEqual((r["gate"], r["drift_movil"], r["excepcion_ventana_movil"]), ("ALARMS_PLAN_OK", MOVIL, None))

    def test_sin_la_excepcion_aws_con_mas_de_24_h_rechazado(self):
        with self.assertRaises(ValueError) as error:
            check(self.real(antes="2026-10-13T00:00:00Z", despues="2026-10-13T03:26:59Z"), ACCOUNT, MEDIOS,
                  ahora=AHORA_REAL)
        self.assertEqual(str(error.exception), "MOVING_ATTRIBUTE")

    def test_acepta_el_instante_aprobado(self):
        r = self.evaluar(self.real())
        self.assertEqual((r["gate"], r["add"], r["change"], r["destroy"], r["resource_drift"]),
                         ("ALARMS_PLAN_OK", 8, 0, 0, 1))
        self.assertEqual((r["drift_movil"], r["excepcion_ventana_movil"]), (MOVIL, APROBADO))

    def test_aws_hace_exactamente_24_h_es_el_limite(self):
        r = self.evaluar(self.real(despues="2026-10-13T03:27:00Z"))
        self.assertEqual(r["excepcion_ventana_movil"], APROBADO)

    def test_aws_con_mas_de_24_h_rechazado(self):
        self.rechaza(self.real(despues="2026-10-13T03:26:59Z"), "MOVING_ATTRIBUTE")

    def test_aws_en_el_futuro_rechazado(self):
        self.rechaza(self.real(despues="2026-10-14T03:27:01Z"), "MOVING_ATTRIBUTE")

    def test_aws_anterior_al_state_rechazado(self):
        self.rechaza(self.real(despues="2026-10-05T19:16:48Z"), "MOVING_ATTRIBUTE",
                     ahora=datetime(2026, 10, 5, 20, 0, 0, tzinfo=timezone.utc))

    def test_otro_instante_del_state_rechazado(self):
        self.rechaza(self.real(antes="2026-10-05T19:16:50Z"), "MOVING_ATTRIBUTE")

    def test_otro_instante_del_state_aunque_este_dentro_de_24_h(self):
        self.rechaza(self.real(antes="2026-10-14T03:00:00Z"), "MOVING_ATTRIBUTE")

    def test_la_excepcion_solo_admite_el_instante_aprobado(self):
        self.rechaza(self.real(antes="2026-10-06T00:00:00Z"), "MOVING_EXCEPTION", excepcion="2026-10-06T00:00:00Z")

    def test_excepcion_malformada(self):
        for valor in ("", "ayer", "2026-10-05T19:16:49"):
            with self.subTest(valor=valor):
                self.rechaza(self.real(), "MOVING_EXCEPTION", excepcion=valor)

    def test_la_excepcion_no_tapa_un_drift_ajeno(self):
        plan = self.real()
        plan["resource_drift"][0]["change"]["after"]["publicly_accessible"] = True
        self.rechaza(plan, "DRIFT")

    def test_la_excepcion_no_tapa_un_cambio_de_recurso(self):
        plan = self.real()
        existente = next(i for i in plan["resource_changes"] if i["change"]["actions"] == ["no-op"])
        existente["change"]["actions"] = ["update"]
        self.rechaza(plan, "EXISTING_CHANGED")

    def test_caso_a_con_la_excepcion_activa_no_la_usa(self):
        r = self.evaluar(fixture())
        self.assertEqual((r["gate"], r["resource_drift"], r["excepcion_ventana_movil"]), ("ALARMS_PLAN_OK", 0, None))

    def test_ninguna_otra_guarda_tiene_la_excepcion(self):
        from scripts.terraform_datos import check_plan_convergencia, check_plan_ejecutor, check_plan_grafana
        from scripts.terraform_datos.check_plan_refresh_instancia import instante_movil

        for modulo in (check_plan_convergencia, check_plan_ejecutor, check_plan_grafana):
            with self.subTest(modulo=modulo.__name__):
                self.assertNotIn("excepcion_ventana_movil", inspect.signature(modulo.check).parameters)
        parametros = list(inspect.signature(check_plan_ejecutor._deriva).parameters.values())
        self.assertIs(parametros[-1].default, instante_movil)

    def test_cli(self):
        ahora = datetime.now(timezone.utc).replace(microsecond=0)
        plan = self.real(despues=(ahora - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        with tempfile.TemporaryDirectory() as directorio:
            ruta, variables = Path(directorio) / "plan.json", Path(directorio) / "variables.json"
            ruta.write_text(json.dumps(plan), encoding="utf-8")
            variables.write_text(json.dumps({"expected_account_id": ACCOUNT, "arn_del_bucket_de_medios": MEDIOS,
                                             "alarmas_existentes": 0}), encoding="utf-8")
            orden = [sys.executable, "-B", "-m", "scripts.terraform_datos.check_plan_alarmas", str(ruta),
                     "--variables", str(variables)]
            sin = subprocess.run(orden, cwd=RAIZ, capture_output=True, text=True)
            con = subprocess.run([*orden, "--excepcion-ventana-movil", APROBADO], cwd=RAIZ, capture_output=True,
                                 text=True)
        self.assertEqual((sin.returncode, con.returncode), (0, 0), sin.stderr + con.stderr)
        sin_excepcion, con_excepcion = json.loads(sin.stdout), json.loads(con.stdout)
        self.assertEqual((sin_excepcion["gate"], sin_excepcion["excepcion_ventana_movil"]), ("ALARMS_PLAN_OK", None))
        self.assertEqual((con_excepcion["gate"], con_excepcion["excepcion_ventana_movil"]), ("ALARMS_PLAN_OK", APROBADO))


if __name__ == "__main__":
    unittest.main()
