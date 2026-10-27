"""Guarda del plan productivo de H-031-6 (Task/031): credenciales SQL, `export` y codigo h0316. Lista CERRADA.

El fixture parte del plan de H-031-5 YA APLICADO (35 recursos en `no-op`, 19 salidas) y le anade EXACTAMENTE lo que
H-031-6 cambia, con las formas REALES que el provider mostro en H-031-2 y H-031-5:
- la funcion, `update` en sitio: solo `source_code_hash` (pin h0316), `filename` y `description`;
- 2 SecureString con `value_wo` (sin valor en el plan; `value` e `insecure_value` desconocidos);
- la politica inline de `export` en el rol de la ejecutora y la regla `sg-admin -> S3:443`;
- una salida nueva con los NOMBRES de las credenciales.
Cada prueba negativa rompe una sola cosa y exige su codigo.
"""
import base64
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.terraform_datos.check_plan_ejecutor import FUNCION, ROL
from scripts.terraform_datos.check_plan_h0316 import (
    CREDENCIALES,
    DESCRIPCION_DE_LA_FUNCION,
    NUEVOS,
    POLITICA_DE_EXPORT,
    REGLA_DE_EXPORT,
    SALIDA_NUEVA,
    check,
    politica_de_exportacion,
)
from scripts.terraform_datos.empaquetar_ejecutor import SHA256_ESPERADO_H0316
from tests.terraform_datos.test_check_plan_convergencia import con_drift_movil
from tests.terraform_datos.test_check_plan_convergencia_por_fase import ejecutora_aplicada
from tests.terraform_datos.test_check_plan_ejecutor import SG_ADMIN, SG_LAMBDA, _crear, _id
from tests.terraform_datos.test_check_plan_recuperacion import ACCOUNT, MEDIOS, previo

AHORA = datetime(2026, 10, 5, 21, 0, 0, tzinfo=timezone.utc)
RAIZ = Path(__file__).resolve().parents[2]
ENDPOINT = "module.red.aws_vpc_endpoint.s3"
VPCE, PREFIX_LIST = "vpce-0123456789abcdef0", "pl-0123abcd"
PIN_H0316 = base64.b64encode(bytes.fromhex(SHA256_ESPERADO_H0316)).decode()
ZIP = "C:/privado/ejecutor-h0316.zip"
SSM_MIGRATE = "module.credenciales_sql.aws_ssm_parameter.blog_migrate"
SSM_APP = "module.credenciales_sql.aws_ssm_parameter.blog_app"
ETIQUETAS = {"Componente": "datos", "Entorno": "produccion", "Gestion": "terraform", "Proyecto": "personal-blog",
             "Tarea": "Task/031"}


MASTER = "module.base_de_datos.aws_ssm_parameter.contrasena_master"


def _en_el_state_y_su_no_op(plan, address, **valores):
    for destino in (previo(plan, address)["values"],
                    *(i["change"][k] for i in plan["resource_changes"] if i["address"] == address
                      for k in ("before", "after"))):
        destino.update(valores)
    return plan


def _con_endpoint_real(plan):
    """El endpoint del state con los formatos reales (`vpce-`, `pl-`), en el state y en su `no-op`."""
    return _en_el_state_y_su_no_op(plan, ENDPOINT, id=VPCE, prefix_list_id=PREFIX_LIST)


def _con_master_real(plan):
    """La master como la deja el provider con `value_wo` (plan real de H-031-5, 2026-10-19): `value` es la cadena
    VACIA, no `null`; el valor real nunca esta en el state."""
    return _en_el_state_y_su_no_op(plan, MASTER, value="", has_value_wo=True, insecure_value=None,
                                   allowed_pattern="", data_type="text", overwrite=None, version=1)


def _ssm(clave):
    ruta, descripcion, nombre = CREDENCIALES[clave]
    after = {"allowed_pattern": None, "description": descripcion, "key_id": "alias/aws/ssm", "name": ruta,
             "overwrite": None, "region": "us-east-2", "tags": {"Name": nombre},
             "tags_all": {**ETIQUETAS, "Name": nombre}, "tier": "Standard", "type": "SecureString",
             "value_wo": None, "value_wo_version": 1}
    desconocido = {k: True for k in ("arn", "data_type", "has_value_wo", "id", "insecure_value", "value", "version")}
    item = _crear(f"module.credenciales_sql.aws_ssm_parameter.{clave}", "aws_ssm_parameter", after, desconocido)
    item["change"]["after_sensitive"] = {"tags": {}, "tags_all": {}, "value": True, "value_wo": True}
    return item


def fixture():
    plan = _con_master_real(_con_endpoint_real(ejecutora_aplicada()))
    plan["applyable"] = True
    plan["variables"]["zip_de_la_ejecutora"] = {"value": {"ruta": ZIP, "sha256": SHA256_ESPERADO_H0316}}
    plan["variables"]["version_de_blog_migrate"] = {"value": 1}
    plan["variables"]["version_de_blog_app"] = {"value": 1}

    funcion = next(i for i in plan["resource_changes"] if i["address"] == FUNCION)
    antes = copy.deepcopy(funcion["change"]["before"])
    despues = {k: v for k, v in antes.items() if k not in ("last_modified", "code_sha256", "source_code_size")}
    despues.update(source_code_hash=PIN_H0316, filename=ZIP, description=DESCRIPCION_DE_LA_FUNCION)
    funcion["change"] = {"actions": ["update"], "before": antes, "after": despues,
                         "after_unknown": {"last_modified": True, "code_sha256": True, "source_code_size": True}}

    # Forma REAL de un `aws_iam_role_policy` nuevo (plan de H-031-5): `name_prefix` es calculado y desconocido. Aqui
    # el rol ya existe, asi que `role` es conocido.
    politica = {"name": "PersonalBlogEjecutorDatos-exportacion", "role": "PersonalBlogEjecutorDatos",
                "policy": json.dumps(politica_de_exportacion(MEDIOS, VPCE))}
    regla = {"cidr_ipv4": None, "cidr_ipv6": None, "description": "HTTPS hacia S3 por el gateway endpoint (modo export "
             "de D-24)", "from_port": 443, "ip_protocol": "tcp", "prefix_list_id": PREFIX_LIST,
             "referenced_security_group_id": None, "region": "us-east-2", "security_group_id": _id(plan, SG_ADMIN),
             "tags": {"Name": "blog-prod-admin-a-s3"}, "tags_all": {**ETIQUETAS, "Name": "blog-prod-admin-a-s3"},
             "to_port": 443}
    plan["resource_changes"] += [
        _ssm("blog_migrate"), _ssm("blog_app"),
        _crear(POLITICA_DE_EXPORT, "aws_iam_role_policy", politica, {"id": True, "name_prefix": True}),
        _crear(REGLA_DE_EXPORT, "aws_vpc_security_group_egress_rule", regla,
               {"arn": True, "id": True, "security_group_rule_id": True}),
    ]
    plan["output_changes"][SALIDA_NUEVA] = {
        "actions": ["create"], "before": None, "after": {c: CREDENCIALES[c][0] for c in CREDENCIALES},
        "after_unknown": False, "after_sensitive": False}
    raiz = plan["configuration"]["root_module"]
    raiz["outputs"][SALIDA_NUEVA] = {}
    raiz["module_calls"]["credenciales_sql"] = {"source": "../terraform/modulos/credenciales_sql", "expressions": {
        "ruta_base": {"references": ["local.ruta_de_datos"]},
        "contrasena_blog_migrate": {"references": ["var.contrasena_blog_migrate"]},
        "contrasena_blog_app": {"references": ["var.contrasena_blog_app"]},
        "version_de_blog_migrate": {"references": ["var.version_de_blog_migrate"]},
        "version_de_blog_app": {"references": ["var.version_de_blog_app"]},
    }}
    raiz["module_calls"]["exportacion"] = {"source": "../terraform/modulos/exportacion", "expressions": {
        "nombre_del_rol": {"references": ["module.ejecutor_privado.nombre_del_rol", "module.ejecutor_privado"]},
        "arn_del_bucket": {"references": ["var.arn_del_bucket_de_medios"]},
        "id_sg_admin": {"references": ["module.red.id_sg_admin", "module.red"]},
        "prefix_list_s3": {"references": ["module.red.prefix_list_s3", "module.red"]},
        "id_del_endpoint_s3": {"references": ["module.red.id_endpoint_s3", "module.red"]},
    }}
    return plan


def cambio(plan, address):
    return next(i for i in plan["resource_changes"] if i["address"] == address)["change"]


class PlanDeH0316(unittest.TestCase):
    def pasa(self, plan):
        return check(plan, ACCOUNT, MEDIOS, ahora=AHORA)

    def rechaza(self, plan, codigo):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS, ahora=AHORA)
        self.assertEqual(str(error.exception), codigo)

    # --- Positivos ------------------------------------------------------------

    def test_caso_a_cuatro_creates_y_el_codigo_en_sitio(self):
        r = self.pasa(fixture())
        self.assertEqual((r["gate"], r["estado_previo"], r["add"], r["change"], r["destroy"], r["replace"]),
                         ("H0316_PLAN_OK", 35, 4, 1, 0, 0))
        self.assertEqual(r["inventario"], sorted(NUEVOS))
        self.assertEqual(r["actualizado"], [FUNCION])
        self.assertEqual(r["resource_drift"], 0)

    def test_caso_b_solo_el_atributo_movil(self):
        r = self.pasa(con_drift_movil(fixture(), antes="2026-10-01T19:16:49Z", despues="2026-10-05T20:55:00Z"))
        self.assertEqual((r["gate"], r["resource_drift"]), ("H0316_PLAN_OK", 1))

    def test_las_credenciales_de_las_fases(self):
        self.assertEqual({c: CREDENCIALES[c][0] for c in CREDENCIALES},
                         {"blog_migrate": "/blog-prod/datos/blog_migrate", "blog_app": "/blog-prod/datos/blog_app"})

    # --- La funcion: SOLO el codigo y su descripcion --------------------------

    def test_otro_atributo_de_la_funcion_rechazado(self):
        for atributo, valor in (("timeout", 60), ("memory_size", 256), ("reserved_concurrent_executions", 1),
                                ("handler", "otro.manejar"), ("environment", [{"variables": {"X": "1"}}]),
                                ("layers", ["arn:aws:lambda:us-east-2:123456789012:layer:x:1"]),
                                ("vpc_config", [{"ipv6_allowed_for_dual_stack": False, "subnet_ids": ["subnet-x"],
                                                 "security_group_ids": ["sg-x"]}])):
            with self.subTest(atributo=atributo):
                plan = fixture(); cambio(plan, FUNCION)["after"][atributo] = valor
                self.rechaza(plan, "FUNCTION_UPDATE")

    def test_descripcion_distinta_rechazada(self):
        plan = fixture(); cambio(plan, FUNCION)["after"]["description"] = "otra"
        self.rechaza(plan, "FUNCTION_UPDATE")

    def test_codigo_que_no_es_el_pin_h0316_rechazado(self):
        plan = fixture(); cambio(plan, FUNCION)["after"]["source_code_hash"] = cambio(plan, FUNCION)["before"][
            "source_code_hash"]
        self.rechaza(plan, "ARTIFACT_PIN")
        plan = fixture(); cambio(plan, FUNCION)["after"]["filename"] = "C:/otro/ejecutor.zip"
        self.rechaza(plan, "ARTIFACT_PIN")

    def test_desconocido_no_admitido_en_la_funcion(self):
        plan = fixture(); cambio(plan, FUNCION)["after_unknown"]["role"] = True
        self.rechaza(plan, "UNVERIFIABLE")

    def test_reemplazo_de_la_funcion_rechazado(self):
        plan = fixture(); cambio(plan, FUNCION)["actions"] = ["delete", "create"]
        self.rechaza(plan, "FUNCTION_UPDATE")

    def test_before_incoherente_con_el_state(self):
        plan = fixture(); cambio(plan, FUNCION)["before"]["timeout"] = 31
        self.rechaza(plan, "FUNCTION_UPDATE")

    # --- Conjunto de recursos ---------------------------------------------------

    def test_un_recurso_existente_cambia(self):
        plan = fixture(); cambio(plan, ROL)["actions"] = ["update"]
        self.rechaza(plan, "EXISTING_CHANGED")

    def test_recurso_inesperado(self):
        plan = fixture()
        plan["resource_changes"].append(_crear("module.exportacion.aws_iam_policy.extra", "aws_iam_policy", {}, {}))
        self.rechaza(plan, "UNEXPECTED_RESOURCE")

    def test_falta_un_create(self):
        plan = fixture()
        plan["resource_changes"] = [i for i in plan["resource_changes"] if i["address"] != SSM_APP]
        self.rechaza(plan, "RESOURCE_SET")

    def test_state_previo_distinto(self):
        plan = fixture()
        hijos = plan["prior_state"]["values"]["root_module"]["child_modules"]
        modulo = next(m for m in hijos if m["address"] == "module.ejecutor_privado")
        modulo["resources"] = [r for r in modulo["resources"] if r["address"] != FUNCION]
        self.rechaza(plan, "PRIOR_STATE")

    # --- Credenciales SQL ------------------------------------------------------

    def test_ssm_distinto_del_contrato(self):
        for atributo, valor in (("name", "/blog-prod/datos/otra"), ("type", "String"), ("tier", "Advanced"),
                                ("key_id", "alias/otra"), ("value_wo_version", 2), ("tags", {"Name": "otra"}),
                                ("description", "otra")):
            with self.subTest(atributo=atributo):
                plan = fixture(); cambio(plan, SSM_MIGRATE)["after"][atributo] = valor
                self.rechaza(plan, "SQL_CREDENTIAL")

    def test_valor_de_la_credencial_en_el_plan(self):
        for atributo in ("value", "insecure_value", "value_wo"):
            with self.subTest(atributo=atributo):
                plan = fixture(); cambio(plan, SSM_APP)["after"][atributo] = "algo"
                cambio(plan, SSM_APP)["after_unknown"].pop(atributo, None)
                self.rechaza(plan, "SECRET_IN_PLAN")

    def test_la_master_con_value_vacio_es_la_forma_real(self):
        """`value = ""` es lo que el provider deja con `value_wo`: no es un secreto y se acepta, como en `check_plan`."""
        plan = fixture()
        self.assertEqual(previo(plan, MASTER)["values"]["value"], "")
        self.assertEqual(self.pasa(plan)["gate"], "H0316_PLAN_OK")

    def test_la_master_con_un_valor_no_vacio_en_el_state(self):
        plan = _en_el_state_y_su_no_op(fixture(), MASTER, value="algo")
        self.rechaza(plan, "SECRET_IN_PLAN")

    def test_contrasena_efimera_en_las_variables(self):
        for nombre in ("contrasena_blog_migrate", "contrasena_blog_app", "contrasena_master"):
            with self.subTest(variable=nombre):
                plan = fixture(); plan["variables"][nombre] = {"value": "x"}
                self.rechaza(plan, "EPHEMERAL_LEAK")

    def test_versiones_de_las_credenciales(self):
        for nombre in ("version_de_blog_migrate", "version_de_blog_app"):
            with self.subTest(variable=nombre):
                plan = fixture(); plan["variables"][nombre] = {"value": 2}
                self.rechaza(plan, "SQL_CREDENTIAL_VERSION")

    def test_desconocido_no_admitido_en_ssm(self):
        plan = fixture(); cambio(plan, SSM_MIGRATE)["after_unknown"]["key_id"] = True
        self.rechaza(plan, "UNVERIFIABLE")

    # --- Export: politica y regla ------------------------------------------------

    def test_politica_de_export_distinta(self):
        mutaciones = {
            "lectura": lambda d: d["Statement"][0].update(Action=["s3:PutObject", "s3:GetObject"]),
            "otro_prefijo": lambda d: d["Statement"][0].update(Resource=f"{MEDIOS}/medios/*"),
            "sin_endpoint": lambda d: d["Statement"][0]["Condition"]["StringEquals"].pop("aws:SourceVpce"),
            "otro_endpoint": lambda d: d["Statement"][0]["Condition"]["StringEquals"].update(
                {"aws:SourceVpce": "vpce-otro"}),
        }
        for nombre, mutar in mutaciones.items():
            with self.subTest(mutacion=nombre):
                plan = fixture()
                documento = politica_de_exportacion(MEDIOS, VPCE); mutar(documento)
                cambio(plan, POLITICA_DE_EXPORT)["after"]["policy"] = json.dumps(documento)
                self.rechaza(plan, "EXPORT_POLICY")

    def test_politica_en_otro_rol_o_con_otro_nombre(self):
        plan = fixture(); cambio(plan, POLITICA_DE_EXPORT)["after"]["role"] = "PersonalBlogLecturaGrafana"
        self.rechaza(plan, "EXPORT_POLICY")
        plan = fixture(); cambio(plan, POLITICA_DE_EXPORT)["after"]["name"] = "otra"
        self.rechaza(plan, "EXPORT_POLICY")

    def test_regla_de_export_distinta(self):
        plan = fixture()
        for atributo, valor in (("cidr_ipv4", "0.0.0.0/0"), ("from_port", 80), ("to_port", 8443),
                                ("ip_protocol", "-1"), ("prefix_list_id", "pl-otra"),
                                ("security_group_id", _id(plan, SG_LAMBDA)),
                                ("referenced_security_group_id", "sg-otro")):
            with self.subTest(atributo=atributo):
                plan = fixture(); cambio(plan, REGLA_DE_EXPORT)["after"][atributo] = valor
                self.rechaza(plan, "EXPORT_RULE")

    # --- Cableado, variables y salidas ----------------------------------------

    def test_cableado(self):
        mutaciones = {
            "sg_lambda": lambda e: e["exportacion"]["expressions"]["id_sg_admin"].update(
                references=["module.red.id_sg_lambda", "module.red"]),
            "rol_literal": lambda e: e["exportacion"]["expressions"].update(
                nombre_del_rol={"constant_value": "PersonalBlogEjecutorDatos"}),
            "otra_contrasena": lambda e: e["credenciales_sql"]["expressions"]["contrasena_blog_app"].update(
                references=["var.contrasena_master"]),
            "sin_exportacion": lambda e: e.pop("exportacion"),
        }
        for nombre, mutar in mutaciones.items():
            with self.subTest(mutacion=nombre):
                plan = fixture(); mutar(plan["configuration"]["root_module"]["module_calls"])
                self.rechaza(plan, "WIRING")

    def test_artefacto_declarado_distinto_del_pin(self):
        plan = fixture(); plan["variables"]["zip_de_la_ejecutora"]["value"]["sha256"] = "0" * 64
        self.rechaza(plan, "ARTIFACT_PIN")

    def test_salidas(self):
        plan = fixture(); plan["output_changes"][SALIDA_NUEVA]["after_sensitive"] = True
        self.rechaza(plan, "OUTPUTS")
        plan = fixture(); plan["output_changes"][SALIDA_NUEVA]["after"]["blog_app"] = "/otra"
        self.rechaza(plan, "OUTPUTS")
        plan = fixture(); plan["output_changes"]["id_sg_admin"]["actions"] = ["update"]
        self.rechaza(plan, "OUTPUTS")

    def test_deriva_fuera_del_caso_b(self):
        plan = con_drift_movil(fixture()); plan["resource_drift"][0]["change"]["after"]["status"] = "modifying"
        self.rechaza(plan, "DRIFT")

    # --- CLI --------------------------------------------------------------------

    def test_cli(self):
        plan = fixture()
        malo = fixture(); cambio(malo, REGLA_DE_EXPORT)["after"]["cidr_ipv4"] = "0.0.0.0/0"
        with tempfile.TemporaryDirectory() as directorio:
            variables = Path(directorio) / "variables.json"
            variables.write_text(json.dumps({"expected_account_id": ACCOUNT, "arn_del_bucket_de_medios": MEDIOS}),
                                 encoding="utf-8")
            salidas = []
            for nombre, contenido in (("bueno.json", plan), ("malo.json", malo)):
                ruta = Path(directorio) / nombre
                ruta.write_text(json.dumps(contenido), encoding="utf-8")
                salidas.append(subprocess.run(
                    [sys.executable, "-B", "-m", "scripts.terraform_datos.check_plan_h0316", str(ruta),
                     "--variables", str(variables)], cwd=RAIZ, capture_output=True, text=True))
        bueno, malo_ = salidas
        self.assertEqual(bueno.returncode, 0, bueno.stderr)
        self.assertEqual(json.loads(bueno.stdout)["gate"], "H0316_PLAN_OK")
        self.assertNotEqual(malo_.returncode, 0)
        self.assertIn("EXPORT_RULE", malo_.stderr)


if __name__ == "__main__":
    unittest.main()
