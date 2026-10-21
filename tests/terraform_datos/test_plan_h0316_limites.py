"""Controles adicionales de la frontera del plan: estados, secretos y atributos desconocidos."""
import copy
import unittest

from tests.terraform_datos.test_check_plan_h0316 import (
    fixture, cambio, ACCOUNT, MEDIOS, AHORA, SSM_APP, FUNCION, POLITICA_DE_EXPORT, REGLA_DE_EXPORT, check,
)


class Limites(unittest.TestCase):
    def test_rechaza_planes_no_aplicables_incompletos_o_version_ajena(self):
        for campo, valor in (("applyable", False), ("complete", False), ("errored", True),
                              ("terraform_version", "1.15.0"), ("deferred_changes", [{}])):
            plan = fixture(); plan[campo] = valor
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                check(plan, ACCOUNT, MEDIOS, ahora=AHORA)

    def test_no_acepta_import_move_o_duplicados(self):
        for mutar in (lambda p: cambio(p, SSM_APP).update(importing={"id": "otro"}),
                      lambda p: p["resource_changes"][-1].update(previous_address="otra"),
                      lambda p: p["resource_changes"].append(copy.deepcopy(p["resource_changes"][-1]))):
            plan = fixture(); mutar(plan)
            with self.assertRaises(ValueError):
                check(plan, ACCOUNT, MEDIOS, ahora=AHORA)

    def test_no_acepta_atributos_nuevos_ni_desconocidos_en_creates(self):
        for address in (SSM_APP, POLITICA_DE_EXPORT, REGLA_DE_EXPORT):
            for seccion in ("after", "after_unknown"):
                plan = fixture(); cambio(plan, address)[seccion]["no_revisado"] = True
                with self.subTest(address=address, seccion=seccion), self.assertRaises(ValueError):
                    check(plan, ACCOUNT, MEDIOS, ahora=AHORA)

    def test_secretos_en_planned_values_y_state_tambien_se_rechazan(self):
        for campo in ("planned_values", "prior_state"):
            plan = fixture()
            if campo == "planned_values":
                plan[campo] = {"root_module": {"resources": [{"type": "aws_ssm_parameter", "values": {"value": "canario"}}]}}
            else:
                plan[campo]["values"]["root_module"]["child_modules"][0]["resources"][0]["values"]["password"] = "canario"
            with self.subTest(campo=campo), self.assertRaisesRegex(ValueError, "SECRET_IN_PLAN"):
                check(plan, ACCOUNT, MEDIOS, ahora=AHORA)

    def test_no_acepta_reemplazar_ningun_create(self):
        for address in (SSM_APP, POLITICA_DE_EXPORT, REGLA_DE_EXPORT):
            plan = fixture(); cambio(plan, address)["actions"] = ["delete", "create"]
            with self.subTest(address=address), self.assertRaises(ValueError):
                check(plan, ACCOUNT, MEDIOS, ahora=AHORA)

    def test_pin_anterior_debe_ser_h0315(self):
        plan = fixture()
        from scripts.terraform_datos.check_plan_recuperacion import _estado_previo
        _estado_previo(plan)[FUNCION]["values"]["source_code_hash"] = "otro"
        cambio(plan, FUNCION)["before"]["source_code_hash"] = "otro"
        with self.assertRaisesRegex(ValueError, "ARTIFACT_PIN"):
            check(plan, ACCOUNT, MEDIOS, ahora=AHORA)
