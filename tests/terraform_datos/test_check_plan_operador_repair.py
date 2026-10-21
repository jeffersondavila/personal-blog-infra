"""Regresiones de la guarda de la reparacion S-10 de H-031-IAM.

El bootstrap ya esta aplicado; la reparacion solo puede actualizar EN SITIO el
documento de `aws_iam_policy.fase_1["Red"]`, desde la politica aplicada en H-031-IAM
—conservada en `scripts/terraform_datos/historico/`— hasta la plantilla vigente. Todo
lo demas debe quedar `no-op`. La cuenta es la ficticia 123456789012.
"""
import copy
import hashlib
import json
import unittest

from scripts.terraform_datos.check_plan_operador import (
    CLAVES_DE_POLITICA, ETIQUETAS, ROL, USUARIO_DE_ENTRADA, bucket_de_estado, direcciones, politicas, trust,
)
from scripts.terraform_datos.check_plan_operador_repair import (
    RED, check, permisos_nuevos, politica_red_aplicada,
)

CUENTA = "123456789012"
PROVIDER = "registry.terraform.io/hashicorp/aws"
ROLE = "aws_iam_role.operador_datos"
SLR = "aws_iam_service_linked_role.rds[0]"


def politica(clave):
    return f'aws_iam_policy.fase_1["{clave}"]'


def adjunto(clave):
    return f'aws_iam_role_policy_attachment.fase_1["{clave}"]'


def _texto(doc):
    return json.dumps(doc, separators=(",", ":"), sort_keys=True)


def _estado():
    docs = politicas(CUENTA)
    docs["Red"] = politica_red_aplicada(CUENTA)
    valores = {
        ROLE: {"name": ROL, "path": "/", "max_session_duration": 3600, "arn": "arn-rol",
               "assume_role_policy": json.dumps(trust(CUENTA)), "permissions_boundary": None,
               "tags": dict(ETIQUETAS), "tags_all": dict(ETIQUETAS), "managed_policy_arns": ["a", "b", "c"]},
        SLR: {"aws_service_name": "rds.amazonaws.com", "custom_suffix": None, "arn": "arn-slr"},
    }
    for clave in CLAVES_DE_POLITICA:
        valores[politica(clave)] = {
            "name": f"PersonalBlogOperadorDatosFase1{clave}", "path": "/personal-blog/", "arn": f"arn-{clave}",
            "policy": _texto(docs[clave]), "policy_id": f"id-{clave}", "attachment_count": 1,
            "tags": dict(ETIQUETAS), "tags_all": dict(ETIQUETAS), "description": f"desc {clave}",
        }
        valores[adjunto(clave)] = {"role": ROL, "policy_arn": f"arn-{clave}", "id": f"att-{clave}"}
    return valores


def _sha(doc):
    return hashlib.sha256(_texto(doc).encode()).hexdigest()


def fixture():
    antes = _estado()
    cambios = []
    for direccion, tipo in sorted(direcciones(True).items()):
        despues = copy.deepcopy(antes[direccion])
        acciones = ["no-op"]
        if direccion == RED:
            despues["policy"] = _texto(politicas(CUENTA)["Red"])
            acciones = ["update"]
        cambios.append({"address": direccion, "mode": "managed", "type": tipo, "provider_name": PROVIDER,
                        "change": {"actions": acciones, "before": antes[direccion], "after": despues,
                                   "after_unknown": {}}})
    shas_antes = {k: _sha(json.loads(antes[politica(k)]["policy"])) for k in CLAVES_DE_POLITICA}
    shas_despues = dict(shas_antes, Red=hashlib.sha256(_texto(politicas(CUENTA)["Red"]).encode()).hexdigest())
    variables = {"expected_account_id": CUENTA, "aws_region": "us-east-2",
                 "usuario_de_entrada": USUARIO_DE_ENTRADA, "crear_rol_vinculado_de_rds": True}
    return {
        "format_version": "1.2", "terraform_version": "1.16.2",
        "applyable": True, "complete": True, "errored": False,
        "variables": {k: {"value": v} for k, v in variables.items()},
        "resource_changes": cambios,
        "output_changes": {
            "arn_del_rol_operativo": {"actions": ["no-op"], "before": "arn-rol", "after": "arn-rol"},
            "bucket_de_estado": {"actions": ["no-op"], "before": bucket_de_estado(CUENTA),
                                 "after": bucket_de_estado(CUENTA)},
            "politicas_fase_1_sha256": {"actions": ["update"], "before": shas_antes, "after": shas_despues},
        },
        "checks": [{"address": {"to_display": "data.aws_caller_identity.bootstrap"}, "status": "pass"}],
        "configuration": {"root_module": {"resources": [
            {"address": ROLE, "expressions": {k: {} for k in (
                "assume_role_policy", "description", "max_session_duration", "name", "path", "tags")}},
            {"address": "aws_iam_policy.fase_1", "expressions": {k: {} for k in (
                "description", "name", "path", "policy", "tags")}},
            {"address": "aws_iam_role_policy_attachment.fase_1", "expressions": {
                "policy_arn": {"references": ["each.value.arn", "each.value"]},
                "role": {"references": ["aws_iam_role.operador_datos.name", "aws_iam_role.operador_datos"]}}},
            {"address": "aws_iam_service_linked_role.rds", "expressions": {"aws_service_name": {}}},
        ]}},
    }


def recurso(plan, direccion):
    return next(r for r in plan["resource_changes"] if r["address"] == direccion)


class ReparacionTests(unittest.TestCase):
    def rechaza(self, plan, codigo):
        with self.assertRaises(ValueError) as capturado:
            check(plan, CUENTA)
        self.assertEqual(str(capturado.exception), codigo)

    def test_acepta_solo_la_actualizacion_de_red(self):
        resultado = check(fixture(), CUENTA)
        self.assertEqual((resultado["add"], resultado["change"], resultado["destroy"]), (0, 1, 0))
        self.assertEqual(resultado["changed"], [RED])
        self.assertEqual(resultado["red_statements"], {"before": 6, "after": 8})
        self.assertEqual(resultado["new_allow_actions"], 0)
        self.assertEqual(resultado["iam_allow_actions"], 0)

    def test_version_completitud_drift(self):
        plan = fixture(); plan["terraform_version"] = "1.17.0"
        self.rechaza(plan, "VERSION")
        plan = fixture(); plan["errored"] = True
        self.rechaza(plan, "INCOMPLETE")
        for clave in ("resource_drift", "deferred_changes"):
            plan = fixture(); plan[clave] = [{"address": ROLE}]
            self.rechaza(plan, "DRIFT_OR_DEFERRED")

    def test_variables_y_rol_vinculado_conservado(self):
        plan = fixture(); plan["variables"]["crear_rol_vinculado_de_rds"] = {"value": False}
        self.rechaza(plan, "VARIABLES")
        plan = fixture(); plan["variables"]["expected_account_id"] = {"value": "999999999999"}
        self.rechaza(plan, "VARIABLES")

    def test_identidad(self):
        plan = fixture(); plan["checks"][0]["status"] = "fail"
        self.rechaza(plan, "IDENTITY_CHECK")

    def test_otro_recurso_cambia(self):
        for direccion in (politica("RdsYCustodia"), politica("Denegaciones"), ROLE, adjunto("Red"), SLR):
            for acciones in (["update"], ["delete"], ["delete", "create"], ["create", "delete"]):
                with self.subTest(direccion=direccion, acciones=acciones):
                    plan = fixture(); recurso(plan, direccion)["change"]["actions"] = acciones
                    self.rechaza(plan, "UNEXPECTED_CHANGE")

    def test_red_reemplazada_o_creada(self):
        for acciones in (["delete", "create"], ["create", "delete"], ["create"], ["delete"], ["no-op"]):
            with self.subTest(acciones=acciones):
                plan = fixture(); recurso(plan, RED)["change"]["actions"] = acciones
                self.rechaza(plan, "NOT_IN_PLACE_UPDATE")

    def test_red_cambia_algo_mas_que_el_documento(self):
        for campo, valor in (("name", "Otra"), ("path", "/"), ("tags", {}), ("description", "x")):
            with self.subTest(campo=campo):
                plan = fixture(); recurso(plan, RED)["change"]["after"][campo] = valor
                self.rechaza(plan, "ONLY_POLICY")
        plan = fixture(); recurso(plan, RED)["change"]["after_unknown"] = {"policy_id": True}
        self.rechaza(plan, "ONLY_POLICY")

    def test_before_distinto_de_lo_aplicado(self):
        plan = fixture()
        antes = json.loads(recurso(plan, RED)["change"]["before"]["policy"])
        antes["Statement"].pop()
        recurso(plan, RED)["change"]["before"]["policy"] = _texto(antes)
        self.rechaza(plan, "BEFORE_POLICY")

    def test_after_distinto_de_la_plantilla_vigente(self):
        plan = fixture()
        despues = json.loads(recurso(plan, RED)["change"]["after"]["policy"])
        despues["Statement"].append({"Sid": "Extra", "Effect": "Allow", "Action": "ec2:CreateVpcEndpoint",
                                     "Resource": "*"})
        recurso(plan, RED)["change"]["after"]["policy"] = _texto(despues)
        self.rechaza(plan, "AFTER_POLICY")

    def test_recursos_de_mas_o_de_menos(self):
        plan = fixture(); plan["resource_changes"].pop()
        self.rechaza(plan, "RESOURCE_SET")
        plan = fixture()
        plan["resource_changes"].append({"address": "aws_iam_access_key.x", "mode": "managed",
                                         "type": "aws_iam_access_key", "provider_name": PROVIDER,
                                         "change": {"actions": ["create"], "before": None, "after": {}}})
        self.rechaza(plan, "UNEXPECTED_RESOURCE")

    def test_import_o_move(self):
        plan = fixture(); recurso(plan, RED)["change"]["importing"] = {"id": "x"}
        self.rechaza(plan, "IMPORT_OR_MOVE")
        plan = fixture(); recurso(plan, RED)["previous_address"] = "aws_iam_policy.vieja"
        self.rechaza(plan, "IMPORT_OR_MOVE")

    def test_salidas(self):
        plan = fixture(); plan["output_changes"]["politicas_fase_1_sha256"]["after"]["Denegaciones"] = "x"
        self.rechaza(plan, "OUTPUTS")
        plan = fixture(); plan["output_changes"]["arn_del_rol_operativo"]["actions"] = ["update"]
        self.rechaza(plan, "OUTPUTS")
        plan = fixture(); plan["output_changes"]["politicas_fase_1_sha256"]["after"]["Red"] = "otro"
        self.rechaza(plan, "OUTPUTS")

    def test_el_documento_aplicado_es_la_copia_historica(self):
        self.assertEqual(len(politica_red_aplicada(CUENTA)["Statement"]), 6)


class PermisosNuevosTests(unittest.TestCase):
    def test_sin_permisos_nuevos_en_la_correccion(self):
        self.assertEqual(permisos_nuevos(politica_red_aplicada(CUENTA), politicas(CUENTA)["Red"]), [])

    def test_detecta_una_accion_nueva(self):
        despues = copy.deepcopy(politicas(CUENTA)["Red"])
        despues["Statement"][0]["Action"] = ["ec2:CreateVpc", "ec2:CreateInternetGateway"]
        self.assertEqual(permisos_nuevos(politica_red_aplicada(CUENTA), despues), ["ec2:CreateInternetGateway"])


if __name__ == "__main__":
    unittest.main()
