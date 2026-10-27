"""Contrato de convergencia de los 39 recursos de H-031-6, sin secretos ni drift nuevo."""
import unittest
import copy

from scripts.terraform_datos.check_plan_convergencia import check
from tests.terraform_datos.test_check_plan_h0316 import fixture, ACCOUNT, MEDIOS, AHORA
from tests.terraform_datos.test_check_plan_grafana import aplicado
from scripts.terraform_datos.check_plan_recuperacion import _estado_previo
from tests.terraform_datos.test_check_plan_convergencia import operativa


def convergente():
    # El helper historico solo materializa creates y simula todos los unknown como texto.
    # Un SSM write-only real devuelve null, y H-031-6 incluye ademas un update de Lambda.
    plan = aplicado(fixture())
    previos = _estado_previo(plan)
    for item in plan["resource_changes"]:
        valores = item["change"]["after"]
        if item["type"] == "aws_ssm_parameter":
            for k in ("value", "insecure_value", "value_wo"):
                valores[k] = None
        previos[item["address"]]["values"] = copy.deepcopy(valores)
        item["change"] = {"actions": ["no-op"], "before": copy.deepcopy(valores), "after": copy.deepcopy(valores)}
    return plan


class ConvergenciaH0316(unittest.TestCase):
    def test_39_recursos_convergen(self):
        r = check(operativa(convergente()), ACCOUNT, MEDIOS, ahora=AHORA, fase="h0316")
        self.assertEqual((r["gate"], r["recursos"]), ("ACTIONABLE_CONVERGENCE_OK", 39))

    def test_no_admite_una_efimera_en_el_plan(self):
        for nombre in ("contrasena_blog_migrate", "contrasena_blog_app"):
            plan = convergente()
            plan["variables"][nombre] = {"value": "canario"}
            with self.subTest(nombre=nombre), self.assertRaisesRegex(ValueError, "EPHEMERAL_LEAK"):
                check(operativa(plan), ACCOUNT, MEDIOS, ahora=AHORA, fase="h0316")

    def test_exige_el_pin_y_versiones(self):
        for nombre, valor, codigo in (
            ("zip_de_la_ejecutora", {"sha256": "0" * 64}, "ARTIFACT_PIN"),
            ("version_de_blog_app", 2, "SQL_CREDENTIAL_VERSION"),
        ):
            plan = convergente()
            plan["variables"][nombre] = {"value": valor}
            with self.subTest(nombre=nombre), self.assertRaisesRegex(ValueError, codigo):
                check(operativa(plan), ACCOUNT, MEDIOS, ahora=AHORA, fase="h0316")
