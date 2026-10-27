"""Regresiones de la guarda del plan de H-031-IAM (bootstrap/operador-datos).

El plan real se genera contra AWS y se revisa en privado; aqui se reproduce su
ESTRUCTURA con la cuenta ficticia 123456789012. Las politicas del fixture salen
del renderizador de la guarda: estas pruebas fijan la forma del plan y los
rechazos. Que el renderizador coincide con `templatefile` de Terraform se
demuestra sobre el plan REAL, que la guarda compara con su propio render.
"""
import copy
import hashlib
import json
import unittest

from scripts.terraform_datos.check_plan_operador import (
    CLAVES_DE_POLITICA,
    ETIQUETAS,
    ROL,
    USUARIO_DE_ENTRADA,
    acciones_allow,
    bucket_de_estado,
    check,
    direcciones,
    politicas,
    trust,
)

CUENTA = "123456789012"
PROVIDER = "registry.terraform.io/hashicorp/aws"
ROLE = "aws_iam_role.operador_datos"
SLR = "aws_iam_service_linked_role.rds[0]"


def politica(clave):
    return f'aws_iam_policy.fase_1["{clave}"]'


def adjunto(clave):
    return f'aws_iam_role_policy_attachment.fase_1["{clave}"]'


def _despues(crear_slr):
    docs = politicas(CUENTA)
    valores = {
        ROLE: {
            "name": ROL, "path": "/", "max_session_duration": 3600,
            "description": "Task031 identidad operativa minima: red y RDS privados en us-east-2",
            "assume_role_policy": json.dumps(trust(CUENTA)), "permissions_boundary": None,
            "force_detach_policies": False, "tags": dict(ETIQUETAS), "tags_all": dict(ETIQUETAS),
        },
    }
    for clave in CLAVES_DE_POLITICA:
        valores[politica(clave)] = {
            "name": f"PersonalBlogOperadorDatosFase1{clave}", "path": "/personal-blog/",
            "policy": json.dumps(docs[clave], separators=(",", ":")),
            "tags": dict(ETIQUETAS), "tags_all": dict(ETIQUETAS),
        }
        valores[adjunto(clave)] = {"role": ROL}
    if crear_slr:
        valores[SLR] = {"aws_service_name": "rds.amazonaws.com", "custom_suffix": None}
    return valores


def _desconocidos(direccion):
    if direccion.startswith("aws_iam_role_policy_attachment"):
        return {"id": True, "policy_arn": True}
    return {"arn": True, "id": True}


def _configuracion(crear_slr):
    recursos = [
        {"address": ROLE, "expressions": {k: {} for k in (
            "assume_role_policy", "description", "max_session_duration", "name", "path", "tags")}},
        {"address": "aws_iam_policy.fase_1", "expressions": {k: {} for k in (
            "description", "name", "path", "policy", "tags")}},
        {"address": "aws_iam_role_policy_attachment.fase_1", "expressions": {
            "policy_arn": {"references": ["each.value.arn", "each.value"]},
            "role": {"references": ["aws_iam_role.operador_datos.name", "aws_iam_role.operador_datos"]}}},
        {"address": "aws_iam_service_linked_role.rds", "expressions": {"aws_service_name": {}}},
        {"address": "data.aws_caller_identity.bootstrap", "mode": "data", "expressions": {}},
    ]
    return {"root_module": {"resources": recursos}}


def fixture(crear_slr=False):
    valores = _despues(crear_slr)
    variables = {
        "expected_account_id": CUENTA, "aws_region": "us-east-2",
        "usuario_de_entrada": USUARIO_DE_ENTRADA, "crear_rol_vinculado_de_rds": crear_slr,
    }
    docs = politicas(CUENTA)
    return {
        "format_version": "1.2", "terraform_version": "1.16.2",
        "applyable": True, "complete": True, "errored": False,
        "variables": {nombre: {"value": valor} for nombre, valor in variables.items()},
        "resource_changes": [
            {"address": d, "mode": "managed", "type": t, "provider_name": PROVIDER,
             "change": {"actions": ["create"], "before": None, "after": valores[d],
                        "after_unknown": _desconocidos(d)}}
            for d, t in sorted(direcciones(crear_slr).items())
        ],
        "planned_values": {"outputs": {
            "arn_del_rol_operativo": {"sensitive": False},
            "bucket_de_estado": {"value": bucket_de_estado(CUENTA), "sensitive": False},
            "politicas_fase_1_sha256": {"value": {
                k: hashlib.sha256(json.dumps(docs[k]).encode()).hexdigest() for k in CLAVES_DE_POLITICA
            }, "sensitive": False},
        }},
        "checks": [
            {"address": {"to_display": "data.aws_caller_identity.bootstrap"}, "status": "pass"},
            {"address": {"to_display": "var.expected_account_id"}, "status": "pass"},
        ],
        "configuration": _configuracion(crear_slr),
    }


def recurso(plan, direccion):
    return next(r for r in plan["resource_changes"] if r["address"] == direccion)


def despues(plan, direccion):
    return recurso(plan, direccion)["change"]["after"]


class RenderTests(unittest.TestCase):
    def test_las_tres_politicas_se_renderizan_sin_marcadores(self):
        docs = politicas(CUENTA)
        self.assertEqual(set(docs), set(CLAVES_DE_POLITICA))
        texto = json.dumps(docs)
        self.assertNotIn("${", texto)
        self.assertNotIn("%{", texto)
        self.assertEqual({k: len(v["Statement"]) for k, v in docs.items()},
                         {"Red": 8, "RdsYCustodia": 9, "Denegaciones": 7})  # 6 hasta la correccion S-10

    def test_68_acciones_allow_y_ninguna_de_iam(self):
        acciones = acciones_allow(politicas(CUENTA))
        self.assertEqual(len(acciones), 68)
        self.assertFalse([a for a in acciones if a.lower().startswith("iam:")])

    def test_bucket_de_estado_derivado_como_en_terraform_state(self):
        sufijo = hashlib.sha256(f"personal-blog:terraform-state:{CUENTA}:us-east-2".encode()).hexdigest()[:12]
        self.assertEqual(bucket_de_estado(CUENTA), f"personal-blog-tfstate-us-east-2-{sufijo}")

    def test_trust_exacto_con_mfa(self):
        self.assertEqual(trust(CUENTA)["Statement"], [{
            "Sid": "UsuarioDeEntradaConMfa", "Effect": "Allow",
            "Principal": {"AWS": f"arn:aws:iam::{CUENTA}:user/personal-blog-entry-admin"},
            "Action": "sts:AssumeRole",
            "Condition": {"Bool": {"aws:MultiFactorAuthPresent": "true"}},
        }])


class PlanDelOperadorTests(unittest.TestCase):
    def acepta(self, plan, crear_slr):
        return check(plan, CUENTA, crear_slr)

    def rechaza(self, plan, codigo, crear_slr=False):
        with self.assertRaises(ValueError) as capturado:
            check(plan, CUENTA, crear_slr)
        self.assertEqual(str(capturado.exception), codigo)

    def test_caso_a_siete_creates(self):
        resultado = self.acepta(fixture(False), False)
        self.assertEqual((resultado["add"], resultado["change"], resultado["destroy"]), (7, 0, 0))
        self.assertNotIn(SLR, resultado["addresses"])
        self.assertEqual(resultado["allow_actions"], 68)
        self.assertEqual(resultado["iam_allow_actions"], 0)

    def test_caso_b_ocho_creates_con_el_rol_vinculado(self):
        resultado = self.acepta(fixture(True), True)
        self.assertEqual(resultado["add"], 8)
        self.assertIn(SLR, resultado["addresses"])

    def test_version_y_completitud(self):
        plan = fixture(); plan["terraform_version"] = "1.16.1"
        self.rechaza(plan, "VERSION")
        for clave, valor in (("applyable", False), ("complete", False), ("errored", True)):
            with self.subTest(clave=clave):
                plan = fixture(); plan[clave] = valor
                self.rechaza(plan, "INCOMPLETE")

    def test_drift_o_diferido(self):
        for clave in ("resource_drift", "deferred_changes"):
            with self.subTest(clave=clave):
                plan = fixture(); plan[clave] = [{"address": "x"}]
                self.rechaza(plan, "DRIFT_OR_DEFERRED")

    def test_variables(self):
        casos = {
            "otra cuenta": ("expected_account_id", "999999999999"),
            "otra region": ("aws_region", "us-east-1"),
            "otro usuario": ("usuario_de_entrada", "otro"),
            "bandera contraria": ("crear_rol_vinculado_de_rds", True),
        }
        for nombre, (clave, valor) in casos.items():
            with self.subTest(caso=nombre):
                plan = fixture(); plan["variables"][clave] = {"value": valor}
                self.rechaza(plan, "VARIABLES")
        plan = fixture(); plan["variables"]["extra"] = {"value": 1}
        self.rechaza(plan, "VARIABLES")

    def test_la_bandera_debe_coincidir_con_el_preflight(self):
        self.rechaza(fixture(True), "VARIABLES", crear_slr=False)

    def test_postcondicion_de_identidad(self):
        plan = fixture(); plan["checks"][0]["status"] = "fail"
        self.rechaza(plan, "IDENTITY_CHECK")
        plan = fixture(); plan["checks"][1]["status"] = "unknown"
        self.rechaza(plan, "CHECKS")

    def test_recurso_no_previsto(self):
        for direccion, tipo in (
            ("aws_iam_access_key.x", "aws_iam_access_key"),
            ("aws_iam_user.x", "aws_iam_user"),
            ("aws_iam_instance_profile.x", "aws_iam_instance_profile"),
            ("aws_iam_role.otro", "aws_iam_role"),
            ('aws_iam_policy.fase_1["Extra"]', "aws_iam_policy"),
            ("aws_iam_role_policy.inline", "aws_iam_role_policy"),
            ("aws_vpc.x", "aws_vpc"),
            ("aws_db_instance.x", "aws_db_instance"),
            ("aws_ssm_parameter.x", "aws_ssm_parameter"),
            ("aws_cloudwatch_log_group.x", "aws_cloudwatch_log_group"),
        ):
            with self.subTest(direccion=direccion):
                plan = fixture()
                plan["resource_changes"].append({
                    "address": direccion, "mode": "managed", "type": tipo, "provider_name": PROVIDER,
                    "change": {"actions": ["create"], "before": None, "after": {}}})
                self.rechaza(plan, "UNEXPECTED_RESOURCE")

    def test_falta_un_recurso(self):
        plan = fixture(); plan["resource_changes"].pop()
        self.rechaza(plan, "RESOURCE_SET")

    def test_rol_vinculado_sin_haberlo_autorizado_el_preflight(self):
        plan = fixture(False)
        plan["resource_changes"].append(recurso(fixture(True), SLR))
        self.rechaza(plan, "UNEXPECTED_RESOURCE")

    def test_solo_create(self):
        for acciones in (["update"], ["delete"], ["delete", "create"], ["create", "delete"], ["no-op"]):
            with self.subTest(acciones=acciones):
                plan = fixture(); recurso(plan, ROLE)["change"]["actions"] = acciones
                self.rechaza(plan, "NOT_CREATE_ONLY")
        plan = fixture(); recurso(plan, ROLE)["change"]["before"] = {"name": ROL}
        self.rechaza(plan, "NOT_CREATE_ONLY")

    def test_import_o_move(self):
        plan = fixture(); recurso(plan, ROLE)["change"]["importing"] = {"id": ROL}
        self.rechaza(plan, "IMPORT_OR_MOVE")
        plan = fixture(); recurso(plan, ROLE)["previous_address"] = "aws_iam_role.viejo"
        self.rechaza(plan, "IMPORT_OR_MOVE")

    def test_data_source_diferido_o_proveedor_ajeno(self):
        plan = fixture(); recurso(plan, ROLE)["mode"] = "data"
        self.rechaza(plan, "DATA_SOURCE_DEFERRED")
        plan = fixture(); recurso(plan, ROLE)["provider_name"] = "registry.terraform.io/otro/aws"
        self.rechaza(plan, "PROVIDER")

    def test_trust_alterado(self):
        alteraciones = {
            "raiz de la cuenta": lambda t: t["Statement"][0]["Principal"].update(AWS=f"arn:aws:iam::{CUENTA}:root"),
            "comodin": lambda t: t["Statement"][0]["Principal"].update(AWS="*"),
            "sin MFA": lambda t: t["Statement"][0].pop("Condition"),
            "sentencia extra": lambda t: t["Statement"].append(dict(t["Statement"][0], Sid="Otra")),
            "otra accion": lambda t: t["Statement"][0].update(Action="sts:*"),
        }
        for nombre, alterar in alteraciones.items():
            with self.subTest(caso=nombre):
                plan = fixture()
                documento = trust(CUENTA); alterar(documento)
                despues(plan, ROLE)["assume_role_policy"] = json.dumps(documento)
                self.rechaza(plan, "TRUST")

    def test_rol_alterado(self):
        for clave, valor in (("name", "Otro"), ("path", "/x/"), ("max_session_duration", 43200),
                             ("permissions_boundary", "arn:aws:iam::aws:policy/AdministratorAccess")):
            with self.subTest(clave=clave):
                plan = fixture(); despues(plan, ROLE)[clave] = valor
                self.rechaza(plan, "ROLE")

    def test_politicas_alteradas(self):
        def anadir_allow(accion, recurso_="*"):
            def alterar(doc):
                doc["Statement"].append({"Sid": "Extra", "Effect": "Allow", "Action": accion, "Resource": recurso_})
            return alterar

        alteraciones = {
            "iam:GetRole para probarse": anadir_allow("iam:GetRole"),
            "iam:SimulatePrincipalPolicy": anadir_allow("iam:SimulatePrincipalPolicy"),
            "comodin total": anadir_allow("*"),
            "sin una denegacion": lambda d: d["Statement"].pop(),
            "recurso ampliado": lambda d: d["Statement"][0].update(Resource="*"),
        }
        for nombre, alterar in alteraciones.items():
            with self.subTest(caso=nombre):
                plan = fixture()
                clave = "Denegaciones" if nombre == "sin una denegacion" else "Red"
                documento = json.loads(despues(plan, politica(clave))["policy"])
                alterar(documento)
                despues(plan, politica(clave))["policy"] = json.dumps(documento)
                self.rechaza(plan, f"POLICY_{clave.upper()}")

    def test_politica_con_otro_nombre_o_ruta(self):
        for campo, valor in (("name", "Otra"), ("path", "/")):
            with self.subTest(campo=campo):
                plan = fixture(); despues(plan, politica("Red"))[campo] = valor
                self.rechaza(plan, "POLICY_RED")

    def test_etiquetas(self):
        plan = fixture(); despues(plan, ROLE)["tags_all"] = {"Proyecto": "otro"}
        self.rechaza(plan, "TAGS")
        plan = fixture(); despues(plan, politica("Red"))["tags"] = {}
        self.rechaza(plan, "TAGS")

    def test_adjuntos(self):
        plan = fixture(); despues(plan, adjunto("Red"))["role"] = "PersonalBlogAdministrator"
        self.rechaza(plan, "ATTACHMENT")
        plan = fixture(); despues(plan, adjunto("Red"))["policy_arn"] = "arn:aws:iam::aws:policy/AdministratorAccess"
        recurso(plan, adjunto("Red"))["change"]["after_unknown"] = {"id": True}
        self.rechaza(plan, "ATTACHMENT")

    def test_rol_vinculado_alterado(self):
        plan = fixture(True); despues(plan, SLR)["aws_service_name"] = "ec2.amazonaws.com"
        self.rechaza(plan, "SERVICE_LINKED_ROLE", crear_slr=True)
        plan = fixture(True); despues(plan, SLR)["custom_suffix"] = "x"
        self.rechaza(plan, "SERVICE_LINKED_ROLE", crear_slr=True)

    def test_configuracion_sin_inline_ni_managed_policy_arns(self):
        for extra in ("inline_policy", "managed_policy_arns", "permissions_boundary"):
            with self.subTest(extra=extra):
                plan = fixture()
                plan["configuration"]["root_module"]["resources"][0]["expressions"][extra] = {}
                self.rechaza(plan, "CONFIGURATION")
        plan = fixture()
        plan["configuration"]["root_module"]["resources"][2]["expressions"]["policy_arn"] = {
            "constant_value": "arn:aws:iam::aws:policy/AdministratorAccess"}
        self.rechaza(plan, "CONFIGURATION")

    def test_salidas(self):
        plan = fixture(); plan["planned_values"]["outputs"]["bucket_de_estado"]["value"] = "otro"
        self.rechaza(plan, "OUTPUTS")
        plan = fixture(); plan["planned_values"]["outputs"]["bucket_de_estado"]["sensitive"] = True
        self.rechaza(plan, "OUTPUTS")

    def test_administrator_access_en_cualquier_lugar(self):
        plan = fixture()
        despues(plan, ROLE)["description"] = "arn:aws:iam::aws:policy/AdministratorAccess"
        self.rechaza(plan, "ADMIN_POLICY")

    def test_el_fixture_no_se_altera_entre_pruebas(self):
        a = fixture(); b = copy.deepcopy(a)
        self.acepta(a, False)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
