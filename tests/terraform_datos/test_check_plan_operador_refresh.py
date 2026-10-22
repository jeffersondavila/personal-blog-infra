"""Regresiones de la guarda del refresh-only de `bootstrap/operador-datos` (H-031-IAM).

El primer plan tras el apply trajo cinco diferencias de METADATOS en `resource_drift`.
El refresh-only solo puede guardarlas en el state, exactamente esas, y nada mas: ni un
documento de politica, ni el trust, ni una salida, ni un recurso de otra clase. Estructura
del JSON real de un refresh-only de AWS: sin `resource_changes`, con las entradas en
`resource_drift`. La cuenta es la ficticia 123456789012.
"""
import copy
import hashlib
import json
import unittest

from scripts.terraform_datos.check_plan_operador import (
    CLAVES_DE_POLITICA, ETIQUETAS, ROL, USUARIO_DE_ENTRADA, bucket_de_estado, politicas, trust,
)
from scripts.terraform_datos.check_plan_operador_refresh import check
from scripts.terraform_datos.check_plan_operador_repair import politica_red_aplicada

CUENTA = "123456789012"
PROVIDER = "registry.terraform.io/hashicorp/aws"
ROLE = "aws_iam_role.operador_datos"
SLR = "aws_iam_service_linked_role.rds[0]"


def politica(clave):
    return f'aws_iam_policy.fase_1["{clave}"]'


def arn_politica(clave):
    return f"arn:aws:iam::{CUENTA}:policy/personal-blog/PersonalBlogOperadorDatosFase1{clave}"


def _texto(doc):
    return json.dumps(doc, separators=(",", ":"))


def _entrada(direccion, tipo, antes, despues):
    return {"address": direccion, "mode": "managed", "type": tipo, "provider_name": PROVIDER,
            "change": {"actions": ["update"], "before": antes, "after": despues, "after_unknown": {}}}


def fixture():
    docs = politicas(CUENTA)
    docs["Red"] = politica_red_aplicada(CUENTA)
    deriva = []
    for clave in CLAVES_DE_POLITICA:
        base = {"name": f"PersonalBlogOperadorDatosFase1{clave}", "path": "/personal-blog/",
                "arn": arn_politica(clave), "policy": _texto(docs[clave]), "tags": dict(ETIQUETAS),
                "tags_all": dict(ETIQUETAS), "attachment_count": 0}
        deriva.append(_entrada(politica(clave), "aws_iam_policy", base, dict(base, attachment_count=1)))
    rol = {"name": ROL, "path": "/", "max_session_duration": 3600, "assume_role_policy": json.dumps(trust(CUENTA)),
           "tags": dict(ETIQUETAS), "tags_all": dict(ETIQUETAS), "managed_policy_arns": []}
    deriva.append(_entrada(ROLE, "aws_iam_role", rol, dict(
        rol, managed_policy_arns=sorted(arn_politica(c) for c in CLAVES_DE_POLITICA))))
    vinculado = {"aws_service_name": "rds.amazonaws.com", "custom_suffix": "", "tags": None, "tags_all": {}}
    deriva.append(_entrada(SLR, "aws_iam_service_linked_role", vinculado, dict(vinculado, tags={})))
    huellas = {k: hashlib.sha256(_texto(docs[k]).encode()).hexdigest() for k in CLAVES_DE_POLITICA}
    variables = {"expected_account_id": CUENTA, "aws_region": "us-east-2",
                 "usuario_de_entrada": USUARIO_DE_ENTRADA, "crear_rol_vinculado_de_rds": True}
    return {
        "format_version": "1.2", "terraform_version": "1.16.2",
        "applyable": True, "complete": True, "errored": False,
        "variables": {k: {"value": v} for k, v in variables.items()},
        "resource_drift": deriva,
        "output_changes": {
            "arn_del_rol_operativo": {"actions": ["no-op"], "before": "a", "after": "a"},
            "bucket_de_estado": {"actions": ["no-op"], "before": bucket_de_estado(CUENTA),
                                 "after": bucket_de_estado(CUENTA)},
            "politicas_fase_1_sha256": {"actions": ["no-op"], "before": huellas, "after": dict(huellas)},
        },
        "checks": [{"address": {"to_display": "data.aws_caller_identity.bootstrap"}, "status": "pass"}],
    }


def entrada(plan, direccion):
    return next(e for e in plan["resource_drift"] if e["address"] == direccion)


class RefreshTests(unittest.TestCase):
    def rechaza(self, plan, codigo):
        with self.assertRaises(ValueError) as capturado:
            check(plan, CUENTA)
        self.assertEqual(str(capturado.exception), codigo)

    def test_acepta_exactamente_los_cinco_metadatos(self):
        resultado = check(fixture(), CUENTA)
        self.assertEqual(resultado["resource_drift"], 5)
        self.assertEqual(resultado["resource_changes"], 0)
        self.assertEqual(resultado["attributes"], {
            politica("Red"): ["attachment_count"], politica("RdsYCustodia"): ["attachment_count"],
            politica("Denegaciones"): ["attachment_count"], ROLE: ["managed_policy_arns"], SLR: ["tags"],
        })

    def test_version_y_completitud(self):
        plan = fixture(); plan["terraform_version"] = "1.16.1"
        self.rechaza(plan, "VERSION")
        for clave, valor in (("applyable", False), ("complete", False), ("errored", True)):
            with self.subTest(clave=clave):
                plan = fixture(); plan[clave] = valor
                self.rechaza(plan, "INCOMPLETE")

    def test_cambio_diferido(self):
        plan = fixture(); plan["deferred_changes"] = [{"reason": "x"}]
        self.rechaza(plan, "DEFERRED")

    def test_cualquier_resource_change(self):
        for acciones in (["create"], ["delete"], ["delete", "create"], ["update"], ["no-op"]):
            with self.subTest(acciones=acciones):
                plan = fixture()
                plan["resource_changes"] = [{"address": ROLE, "mode": "managed", "type": "aws_iam_role",
                                             "change": {"actions": acciones}}]
                self.rechaza(plan, "RESOURCE_CHANGES")

    def test_variables(self):
        plan = fixture(); plan["variables"]["crear_rol_vinculado_de_rds"] = {"value": False}
        self.rechaza(plan, "VARIABLES")

    def test_identidad(self):
        plan = fixture(); plan["checks"][0]["status"] = "fail"
        self.rechaza(plan, "IDENTITY_CHECK")

    def test_otra_politica_o_recurso_de_red_rds_ssm(self):
        for direccion, tipo in (('aws_iam_policy.fase_1["Extra"]', "aws_iam_policy"),
                                ("aws_iam_role.otro", "aws_iam_role"),
                                ("aws_vpc.this", "aws_vpc"), ("aws_db_instance.this", "aws_db_instance"),
                                ("aws_ssm_parameter.x", "aws_ssm_parameter")):
            with self.subTest(direccion=direccion):
                plan = fixture()
                plan["resource_drift"].append(_entrada(direccion, tipo, {"a": 0}, {"a": 1}))
                self.rechaza(plan, "UNEXPECTED_DRIFT")

    def test_falta_una_entrada(self):
        for direccion in (politica("Red"), politica("Denegaciones"), ROLE, SLR):
            with self.subTest(direccion=direccion):
                plan = fixture()
                plan["resource_drift"] = [e for e in plan["resource_drift"] if e["address"] != direccion]
                self.rechaza(plan, "DRIFT_SET")

    def test_tipo_o_acciones_distintas(self):
        plan = fixture(); entrada(plan, ROLE)["type"] = "aws_iam_user"
        self.rechaza(plan, "UNEXPECTED_DRIFT")
        for acciones in (["delete"], ["create"], ["delete", "create"], ["no-op"]):
            with self.subTest(acciones=acciones):
                plan = fixture(); entrada(plan, politica("Red"))["change"]["actions"] = acciones
                self.rechaza(plan, "ACTIONS")

    def test_attachment_count_distinto(self):
        for antes, despues in ((0, 2), (1, 1), (1, 0), (0, None)):
            with self.subTest(antes=antes, despues=despues):
                plan = fixture()
                cambio = entrada(plan, politica("RdsYCustodia"))["change"]
                cambio["before"]["attachment_count"] = antes
                cambio["after"]["attachment_count"] = despues
                codigo = "ONLY_METADATA" if antes == despues else "ATTACHMENT_COUNT"
                self.rechaza(plan, codigo)

    def test_managed_policy_arns(self):
        casos = {
            "cuarta politica": sorted(arn_politica(c) for c in CLAVES_DE_POLITICA)
            + ["arn:aws:iam::aws:policy/AdministratorAccess"],
            "solo dos": sorted(arn_politica(c) for c in ("Red", "Denegaciones")),
            "otra en lugar de una": sorted([arn_politica("Red"), arn_politica("Denegaciones"),
                                            f"arn:aws:iam::{CUENTA}:policy/personal-blog/Otra"]),
            "otra cuenta": sorted(a.replace(CUENTA, "999999999999") for a in
                                  (arn_politica(c) for c in CLAVES_DE_POLITICA)),
        }
        for nombre, arns in casos.items():
            with self.subTest(caso=nombre):
                plan = fixture(); entrada(plan, ROLE)["change"]["after"]["managed_policy_arns"] = arns
                self.rechaza(plan, "MANAGED_POLICY_ARNS")
        plan = fixture(); entrada(plan, ROLE)["change"]["before"]["managed_policy_arns"] = [arn_politica("Red")]
        self.rechaza(plan, "MANAGED_POLICY_ARNS")

    def test_tags_del_rol_vinculado(self):
        for despues in ({"Proyecto": "x"}, None, []):
            with self.subTest(despues=despues):
                plan = fixture(); entrada(plan, SLR)["change"]["after"]["tags"] = despues
                codigo = "ONLY_METADATA" if despues is None else "SLR_TAGS"
                self.rechaza(plan, codigo)
        plan = fixture(); entrada(plan, SLR)["change"]["before"]["tags"] = {}
        self.rechaza(plan, "ONLY_METADATA")

    def test_cambia_el_trust(self):
        plan = fixture()
        otro = trust(CUENTA); otro["Statement"][0]["Principal"]["AWS"] = f"arn:aws:iam::{CUENTA}:root"
        entrada(plan, ROLE)["change"]["after"]["assume_role_policy"] = json.dumps(otro)
        self.rechaza(plan, "ONLY_METADATA")

    def test_trust_previo_distinto_del_aprobado(self):
        plan = fixture()
        otro = trust(CUENTA); otro["Statement"][0]["Condition"] = {}
        for lado in ("before", "after"):
            entrada(plan, ROLE)["change"][lado]["assume_role_policy"] = json.dumps(otro)
        self.rechaza(plan, "TRUST")

    def test_cambia_un_documento_de_politica(self):
        plan = fixture()
        cambio = entrada(plan, politica("Denegaciones"))["change"]
        doc = json.loads(cambio["after"]["policy"]); doc["Statement"].pop()
        cambio["after"]["policy"] = _texto(doc)
        self.rechaza(plan, "ONLY_METADATA")

    def test_documento_vivo_no_es_el_aplicado(self):
        plan = fixture()
        cambio = entrada(plan, politica("Red"))["change"]
        corregida = _texto(politicas(CUENTA)["Red"])
        cambio["before"]["policy"] = corregida
        cambio["after"]["policy"] = corregida
        self.rechaza(plan, "POLICY_DOCUMENT")

    def test_otros_atributos_cambian(self):
        for direccion, campo in ((politica("Red"), "tags"), (ROLE, "max_session_duration"), (SLR, "custom_suffix"),
                                 (politica("RdsYCustodia"), "path")):
            with self.subTest(direccion=direccion, campo=campo):
                plan = fixture(); entrada(plan, direccion)["change"]["after"][campo] = "otro"
                self.rechaza(plan, "ONLY_METADATA")

    def test_salida_que_cambia_es_un_sexto_cambio(self):
        plan = fixture()
        salidas = plan["output_changes"]["politicas_fase_1_sha256"]
        salidas["actions"] = ["update"]
        salidas["after"]["Red"] = hashlib.sha256(_texto(politicas(CUENTA)["Red"]).encode()).hexdigest()
        self.rechaza(plan, "OUTPUTS")
        plan = fixture(); plan["output_changes"]["extra"] = {"actions": ["create"]}
        self.rechaza(plan, "OUTPUTS")

    def test_el_fixture_no_se_altera(self):
        a = fixture(); b = copy.deepcopy(a)
        check(a, CUENTA)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
