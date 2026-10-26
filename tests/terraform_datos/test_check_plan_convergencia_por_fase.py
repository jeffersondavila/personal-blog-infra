"""Convergencia del root de datos despues de cada fase aplicada (Task/031, decision del 2026-10-08).

Tras H-031-8 el root administra 21 + 8 recursos; tras H-031-9, 21 + 8 + 2. La guarda de convergencia exige EXACTAMENTE
el conjunto de la fase que se declara: ni menos (un recurso perdido) ni mas (uno inesperado). Mismas reglas de §40-§42
para todo lo demas.
"""
import unittest
from datetime import datetime, timezone

from scripts.terraform_datos.check_plan_convergencia import FASES, check
from tests.terraform_datos.test_check_plan_alarmas import fixture as fixture_alarmas
from tests.terraform_datos.test_check_plan_convergencia import con_drift_movil, fixture as fixture_h0313, operativa
from tests.terraform_datos.test_check_plan_ejecutor import fixture as fixture_ejecutor
from tests.terraform_datos.test_check_plan_grafana import aplicado, fixture as fixture_grafana
from tests.terraform_datos.test_check_plan_recuperacion import ACCOUNT, MEDIOS

AHORA = datetime(2026, 10, 8, 18, 0, 0, tzinfo=timezone.utc)
#: Enmienda de §40 del 2026-10-18 (aprobada el 2026-10-19): el valor de AWS del caso B debe ser FRESCO respecto a `AHORA`
#: (24 h como maximo). Los valores por omision de `con_drift_movil` son del 2026-10-05: rancios para este reloj.
FRESCO = {"antes": "2026-10-08T17:00:00Z", "despues": "2026-10-08T17:50:00Z"}


def ejecutora_aplicada():
    """El plan de H-031-5 ya aplicado: el ARN de la funcion, desconocido al planificar, ya existe."""
    plan = fixture_ejecutor()
    plan["output_changes"]["arn_de_la_ejecutora"].update(
        after="arn:aws:lambda:us-east-2:123456789012:function:blog-prod-ejecutor", after_unknown=False)
    return aplicado(plan)


class ConvergenciaPorFase(unittest.TestCase):
    def rechaza(self, plan, fase, codigo):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS, ahora=AHORA, fase=fase)
        self.assertEqual(str(error.exception), codigo)

    def test_conjuntos_de_cada_fase(self):
        self.assertEqual(len(FASES["h0313"]), 21)
        self.assertEqual(len(FASES["h0318"]), 29)
        self.assertEqual(len(FASES["h0319"]), 31)
        self.assertEqual(len(FASES["h0315"]), 35)
        self.assertTrue(FASES["h0313"] < FASES["h0318"] < FASES["h0319"] < FASES["h0315"])

    def test_cada_fase_converge_con_su_conjunto(self):
        for fase, plan in (("h0313", operativa(fixture_h0313())), ("h0318", operativa(aplicado(fixture_alarmas()))),
                           ("h0319", operativa(aplicado(fixture_grafana()))), ("h0315", operativa(ejecutora_aplicada()))):
            with self.subTest(fase=fase):
                r = check(plan, ACCOUNT, MEDIOS, ahora=AHORA, fase=fase)
                self.assertEqual((r["gate"], r["add"], r["change"], r["destroy"]),
                                 ("ACTIONABLE_CONVERGENCE_OK", 0, 0, 0))
                r = check(con_drift_movil(plan, **FRESCO), ACCOUNT, MEDIOS, ahora=AHORA, fase=fase)
                self.assertEqual(r["resource_drift"], 1)

    def test_por_omision_sigue_siendo_h0313(self):
        self.assertEqual(check(operativa(fixture_h0313()), ACCOUNT, MEDIOS, ahora=AHORA)["gate"], "ACTIONABLE_CONVERGENCE_OK")

    def test_un_conjunto_que_no_es_el_de_la_fase(self):
        self.rechaza(operativa(aplicado(fixture_alarmas())), "h0313", "PRIOR_STATE")
        self.rechaza(operativa(aplicado(fixture_alarmas())), "h0319", "PRIOR_STATE")
        self.rechaza(operativa(fixture_h0313()), "h0318", "PRIOR_STATE")
        self.rechaza(operativa(aplicado(fixture_grafana())), "h0315", "PRIOR_STATE")
        self.rechaza(operativa(ejecutora_aplicada()), "h0319", "PRIOR_STATE")

    def test_fase_desconocida(self):
        self.rechaza(fixture_h0313(), "h0399", "PHASE")


if __name__ == "__main__":
    unittest.main()
