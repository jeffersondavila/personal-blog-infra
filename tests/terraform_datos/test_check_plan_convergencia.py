"""Criterio de convergencia tras el refresh apply y el untaint (Task/031 §40): `ACTIONABLE_CONVERGENCE_OK`.

Un plan normal converge si: cero cambios de recurso (todo `no-op` con `before == after`), cero diferidos, salidas
`no-op`, state 21/21 sin taint, y `resource_drift` es:
- CASO A: vacio; o
- CASO B: exactamente una entrada, `aws_db_instance.this`, `update`, cuya UNICA diferencia es
  `latest_restorable_time` (atributo movil calculado), con instantes validos, despues >= antes, ninguno en el
  futuro y el de AWS con 24 h como maximo de antiguedad (enmienda de §40 del 2026-10-18, aprobada el
  2026-10-19: antes el limite era `despues - antes`). Nunca se informa `resource_drift = 0` en el caso B.

Semantica del plan convergente (§42): Terraform marca `applyable = false` cuando el plan no tiene NADA que
aplicar; el JSON real de §41 trae `applyable = false`, `complete = true`, `errored = false`. El fixture lo
reproduce asi (antes heredaba `applyable = true` de los planes con cambios: error de diseno de §40).
"""
import copy
from datetime import datetime, timezone
import unittest

from scripts.terraform_datos.check_plan_convergencia import check
from scripts.terraform_datos.check_plan_recuperacion import GRUPO, INSTANCIA_RDS
from tests.terraform_datos.test_check_plan_recuperacion import ACCOUNT, MEDIOS, previo
from tests.terraform_datos.test_check_plan_refresh_instancia import fixture as fixture_refresh

AHORA = datetime(2026, 10, 5, 21, 0, 0, tzinfo=timezone.utc)


def _previos(plan):
    for m in plan["prior_state"]["values"]["root_module"]["child_modules"]:
        for r in m["resources"]:
            yield r


def fixture():
    plan = fixture_refresh()
    plan.pop("resource_drift")
    previo(plan, INSTANCIA_RDS).pop("tainted")
    plan["resource_changes"] = [
        {"address": r["address"], "mode": "managed", "type": r["type"], "provider_name": "registry.terraform.io/hashicorp/aws",
         "change": {"actions": ["no-op"], "before": copy.deepcopy(r["values"]), "after": copy.deepcopy(r["values"])}}
        for r in _previos(plan)]
    for dato in plan["output_changes"].values():
        dato.update(actions=["no-op"], before=dato["after"])
    plan["resource_drift"] = []
    plan["applyable"] = False  # §42: un plan convergente no tiene nada que aplicar
    return plan


def con_drift_movil(plan, antes="2026-10-05T19:16:49Z", despues="2026-10-05T20:06:50Z"):
    valores = previo(plan, INSTANCIA_RDS)["values"]
    b = copy.deepcopy(valores); b["latest_restorable_time"] = antes
    a = copy.deepcopy(valores); a["latest_restorable_time"] = despues
    valores["latest_restorable_time"] = despues
    for item in plan["resource_changes"]:
        if item["address"] == INSTANCIA_RDS:
            item["change"]["before"] = copy.deepcopy(a); item["change"]["after"] = copy.deepcopy(a)
    plan["resource_drift"] = [{"address": INSTANCIA_RDS, "mode": "managed", "type": "aws_db_instance",
                               "provider_name": "registry.terraform.io/hashicorp/aws",
                               "change": {"actions": ["update"], "before": b, "after": a, "after_unknown": {}}}]
    return plan


class Convergencia(unittest.TestCase):
    def pasa(self, plan):
        return check(plan, ACCOUNT, MEDIOS, ahora=AHORA)

    def rechaza(self, plan, codigo):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS, ahora=AHORA)
        self.assertEqual(str(error.exception), codigo)

    def test_caso_a_sin_drift(self):
        r = self.pasa(fixture())
        self.assertEqual(r["gate"], "ACTIONABLE_CONVERGENCE_OK")
        self.assertEqual((r["add"], r["change"], r["destroy"]), (0, 0, 0))
        self.assertEqual(r["resource_drift"], 0)
        self.assertEqual(r["drift_movil"], [])

    def test_caso_b_solo_el_atributo_movil(self):
        r = self.pasa(con_drift_movil(fixture()))
        self.assertEqual(r["gate"], "ACTIONABLE_CONVERGENCE_OK")
        self.assertEqual(r["resource_drift"], 1)  # nunca se informa 0 si hay drift movil
        self.assertEqual(r["drift_movil"], ["module.base_de_datos.aws_db_instance.this: latest_restorable_time"])

    def test_drift_movil_hacia_atras_rechazado(self):
        self.rechaza(con_drift_movil(fixture(), antes="2026-10-05T20:06:50Z", despues="2026-10-05T19:16:49Z"),
                     "MOVING_ATTRIBUTE")

    def test_state_de_mas_de_24h_con_aws_fresco_converge(self):
        """Enmienda de §40 del 2026-10-18: la antiguedad del state ya no rechaza; mide la frescura de AWS."""
        r = self.pasa(con_drift_movil(fixture(), antes="2026-10-04T19:00:00Z", despues="2026-10-05T20:06:50Z"))
        self.assertEqual((r["gate"], r["resource_drift"]), ("ACTIONABLE_CONVERGENCE_OK", 1))

    def test_aws_con_mas_de_24h_rechazado(self):
        self.rechaza(con_drift_movil(fixture(), antes="2026-10-04T18:00:00Z", despues="2026-10-04T20:59:59Z"),
                     "MOVING_ATTRIBUTE")

    def test_drift_movil_invalido_o_futuro_rechazado(self):
        self.rechaza(con_drift_movil(fixture(), despues="otro"), "MOVING_ATTRIBUTE")
        self.rechaza(con_drift_movil(fixture(), despues="2026-10-05T21:30:00Z"), "MOVING_ATTRIBUTE")

    def test_drift_con_otro_atributo_rechazado(self):
        plan = con_drift_movil(fixture()); plan["resource_drift"][0]["change"]["after"]["status"] = "modifying"
        self.rechaza(plan, "DRIFT")

    def test_drift_de_otra_direccion_rechazado(self):
        plan = con_drift_movil(fixture()); plan["resource_drift"][0]["address"] = GRUPO
        self.rechaza(plan, "DRIFT")

    def test_dos_entradas_de_drift_rechazadas(self):
        plan = con_drift_movil(fixture()); plan["resource_drift"].append(copy.deepcopy(plan["resource_drift"][0]))
        self.rechaza(plan, "DRIFT")

    def test_drift_con_otra_accion_rechazado(self):
        plan = con_drift_movil(fixture()); plan["resource_drift"][0]["change"]["actions"] = ["delete"]
        self.rechaza(plan, "DRIFT")

    def test_cualquier_cambio_de_recurso_rechazado(self):
        for acciones in (["update"], ["create"], ["delete"], ["delete", "create"]):
            with self.subTest(acciones=acciones):
                plan = fixture(); plan["resource_changes"][0]["change"]["actions"] = acciones
                self.rechaza(plan, "CHANGES")

    def test_no_op_con_valores_distintos_rechazado(self):
        plan = fixture(); plan["resource_changes"][0]["change"]["after"]["x"] = "y"
        self.rechaza(plan, "CHANGES")

    def test_salida_que_cambia_rechazada(self):
        for nombre in ("arn_rds", "endpoint_rds", "id_de_recurso_rds", "id_de_vpc"):
            with self.subTest(nombre=nombre):
                plan = fixture(); plan["output_changes"][nombre]["actions"] = ["update"]
                self.rechaza(plan, "OUTPUTS")

    def test_diferido_rechazado(self):
        plan = fixture(); plan["deferred_changes"] = [{"reason": "x"}]
        self.rechaza(plan, "DEFERRED")

    def test_taint_en_el_state_rechazado(self):
        plan = fixture(); previo(plan, INSTANCIA_RDS)["tainted"] = True
        self.rechaza(plan, "PRIOR_STATE")

    def test_retencion_distinta_rechazada(self):
        plan = fixture(); plan["variables"]["dias_de_retencion_de_backups"]["value"] = 7
        self.rechaza(plan, "RETENTION")

    def test_secreto_rechazado(self):
        plan = fixture(); plan["variables"]["contrasena_master"] = {"value": None}
        self.rechaza(plan, "EPHEMERAL_LEAK")


class SemanticaDelPlanConvergente(unittest.TestCase):
    """§42: `applyable is False`, `complete is True` y `errored is False`, explicitos."""

    def pasa(self, plan):
        return check(plan, ACCOUNT, MEDIOS, ahora=AHORA)

    def rechaza(self, plan, codigo):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS, ahora=AHORA)
        self.assertEqual(str(error.exception), codigo)

    # PASS
    def test_caso_a_con_la_semantica_real(self):
        plan = fixture()
        self.assertEqual((plan["applyable"], plan["complete"], plan["errored"]), (False, True, False))
        r = self.pasa(plan)
        self.assertEqual((r["gate"], r["resource_drift"]), ("ACTIONABLE_CONVERGENCE_OK", 0))

    def test_caso_b_con_la_semantica_real(self):
        plan = con_drift_movil(fixture())
        self.assertEqual((plan["applyable"], plan["complete"], plan["errored"]), (False, True, False))
        r = self.pasa(plan)
        self.assertEqual((r["gate"], r["resource_drift"]), ("ACTIONABLE_CONVERGENCE_OK", 1))

    # FAIL
    def test_applyable_true(self):
        plan = fixture(); plan["applyable"] = True
        self.rechaza(plan, "APPLYABLE")

    def test_applyable_ausente_o_nulo(self):
        plan = fixture(); plan.pop("applyable")
        self.rechaza(plan, "APPLYABLE")
        plan = fixture(); plan["applyable"] = None
        self.rechaza(plan, "APPLYABLE")

    def test_complete_false(self):
        plan = fixture(); plan["complete"] = False
        self.rechaza(plan, "INCOMPLETE")

    def test_complete_ausente_o_nulo(self):
        plan = fixture(); plan.pop("complete")
        self.rechaza(plan, "INCOMPLETE")
        plan = fixture(); plan["complete"] = None
        self.rechaza(plan, "INCOMPLETE")

    def test_errored_true(self):
        plan = fixture(); plan["errored"] = True
        self.rechaza(plan, "INCOMPLETE")

    def test_errored_ausente_o_nulo(self):
        plan = fixture(); plan.pop("errored")
        self.rechaza(plan, "INCOMPLETE")
        plan = fixture(); plan["errored"] = None
        self.rechaza(plan, "INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
