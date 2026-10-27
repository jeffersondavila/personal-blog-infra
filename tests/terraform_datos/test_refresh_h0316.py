"""Solo espejos de recursos ya gestionados: rol inline y salida del SG, mas §40."""
import copy
import json
import unittest
from scripts.terraform_datos.check_plan_refresh_h0316 import check, SG_ADMIN
from scripts.terraform_datos.check_plan_ejecutor import ROL, POLITICA
from scripts.terraform_datos.check_plan_h0316 import POLITICA_DE_EXPORT
from scripts.terraform_datos.check_plan_recuperacion import _estado_previo
from tests.terraform_datos.test_convergencia_h0316 import convergente
from tests.terraform_datos.test_check_plan_h0316 import ACCOUNT, MEDIOS, AHORA


def fixture():
    p = convergente(); p.update(applyable=True, resource_changes=[])
    previos = _estado_previo(p)
    def espejo(address):
        v = previos[address]["values"]
        return {"name": v["name"], "policy": v["policy"]}
    antes = copy.deepcopy(previos[ROL]["values"])
    antes["inline_policy"] = [espejo(POLITICA)]
    despues = copy.deepcopy(antes)
    despues["inline_policy"].append(espejo(POLITICA_DE_EXPORT))
    previos[ROL]["values"] = copy.deepcopy(despues)
    p["resource_drift"] = [{"address": ROL, "type": "aws_iam_role", "mode": "managed",
                            "provider_name": "registry.terraform.io/hashicorp/aws", "change": {
                                "actions": ["update"], "before": antes, "after": despues, "after_unknown": {}}}]
    return p


class RefreshH0316(unittest.TestCase):
    def test_espejo_exacto(self):
        self.assertEqual(check(fixture(), ACCOUNT, MEDIOS, ahora=AHORA)["gate"], "H0316_REFRESH_OK")

    def test_no_admite_otra_politica_o_permiso(self):
        for mutar in (
            lambda a: a["inline_policy"].append({"name": "otra", "policy": "{}"}),
            lambda a: a["inline_policy"][1].update(policy=json.dumps({"Statement": []})),
            lambda a: a.update(max_session_duration=7200),
        ):
            p = fixture(); mutar(p["resource_drift"][0]["change"]["after"])
            _estado_previo(p)[ROL]["values"] = copy.deepcopy(p["resource_drift"][0]["change"]["after"])
            with self.assertRaises(ValueError):
                check(p, ACCOUNT, MEDIOS, ahora=AHORA)

    def test_no_admite_cambios_de_recurso(self):
        p = fixture(); p["resource_changes"] = [{"address": ROL}]
        with self.assertRaisesRegex(ValueError, "RESOURCE_CHANGES"):
            check(p, ACCOUNT, MEDIOS, ahora=AHORA)

    def test_exige_coherencia_con_state_refrescado(self):
        p = fixture(); _estado_previo(p)[ROL]["values"]["inline_policy"] = []
        with self.assertRaisesRegex(ValueError, "DRIFT_COHERENCE"):
            check(p, ACCOUNT, MEDIOS, ahora=AHORA)

    def test_salida_sg_solo_refleja_la_regla_administrada(self):
        from scripts.terraform_datos.check_plan_refresh_h0316 import reflejo_regla
        from scripts.terraform_datos.check_plan_h0316 import REGLA_DE_EXPORT
        p = fixture(); previos = _estado_previo(p)
        vieja = reflejo_regla(previos['module.red.aws_vpc_security_group_egress_rule.admin_a_rds']["values"])
        nueva = reflejo_regla(previos[REGLA_DE_EXPORT]["values"])
        antes = copy.deepcopy(previos[SG_ADMIN]["values"]); antes["egress"] = [vieja]
        despues = copy.deepcopy(antes); despues["egress"] = [vieja, nueva]
        previos[SG_ADMIN]["values"] = copy.deepcopy(despues)
        p["resource_drift"].append({"address": SG_ADMIN, "type": "aws_security_group", "mode": "managed",
                                  "provider_name": "registry.terraform.io/hashicorp/aws", "change": {
                                      "actions": ["update"], "before": antes, "after": despues}})
        self.assertEqual(check(p, ACCOUNT, MEDIOS, ahora=AHORA)["resource_drift"], 2)
        despues["egress"][1]["cidr_blocks"] = ["0.0.0.0/0"]
        with self.assertRaises(ValueError):
            check(p, ACCOUNT, MEDIOS, ahora=AHORA)
