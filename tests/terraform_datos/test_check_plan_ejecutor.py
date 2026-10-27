"""Guarda del plan productivo de H-031-5 (Task/031): ejecutora privada de D-24, lista CERRADA. Nunca aplica.

Linea base real desde el 2026-10-15: H-031-8 y H-031-9 se aplicaron antes que H-031-5 (decision del 2026-10-08).
El fixture parte del plan de H-031-9 YA APLICADO: 31 recursos en `no-op`, state 31/31 sin taint y 17 salidas en
`no-op`. Le anade EXACTAMENTE lo que H-031-5 crea: grupo de logs, rol, su politica en linea y la funcion, mas dos
salidas nuevas. Cada prueba negativa rompe una sola cosa y exige su codigo.
"""
import base64
import copy
import json
import unittest
from datetime import datetime, timezone

from scripts.terraform_datos.check_plan_ejecutor import (
    CONFIANZA,
    FUNCION,
    LOGS,
    NUEVOS,
    POLITICA,
    ROL,
    check,
    permisos,
)
from scripts.terraform_datos.empaquetar_ejecutor import SHA256_ESPERADO
from tests.terraform_datos.test_check_plan_convergencia import con_drift_movil, fixture as fixture_convergencia
from tests.terraform_datos.test_check_plan_grafana import ROL as ROL_DE_GRAFANA, aplicado, fixture as fixture_grafana
from tests.terraform_datos.test_check_plan_recuperacion import ACCOUNT, MEDIOS, previo

AHORA = datetime(2026, 10, 5, 21, 0, 0, tzinfo=timezone.utc)
PIN_B64 = base64.b64encode(bytes.fromhex(SHA256_ESPERADO)).decode()
NOMBRE = "blog-prod-ejecutor"
SUBRED_A, SUBRED_B = 'module.red.aws_subnet.privada["a"]', 'module.red.aws_subnet.privada["b"]'
SG_ADMIN, SG_LAMBDA, SG_RDS = ("module.red.aws_security_group.admin", "module.red.aws_security_group.lambda",
                               "module.red.aws_security_group.rds")


def _id(plan, address):
    return previo(plan, address)["values"]["id"]


def _crear(address, tipo, after, desconocido):
    return {"address": address, "mode": "managed", "type": tipo, "provider_name": "registry.terraform.io/hashicorp/aws",
            "change": {"actions": ["create"], "before": None, "after": after, "after_unknown": desconocido}}


def fixture(base=None):
    plan = base if base is not None else aplicado(fixture_grafana())
    plan["applyable"] = True
    plan["variables"]["zip_de_la_ejecutora"] = {"value": {"ruta": "C:/privado/h0315/ejecutor.zip",
                                                         "sha256": SHA256_ESPERADO}}
    subredes = sorted([_id(plan, SUBRED_A), _id(plan, SUBRED_B)])
    funcion = {
        "architectures": ["x86_64"], "code_signing_config_arn": None, "dead_letter_config": [],
        "description": "Ejecutora privada D-24 (Task/031 H-031-5): shell sin base de datos", "environment": [],
        "file_system_config": [], "filename": "C:/privado/h0315/ejecutor.zip", "function_name": NOMBRE,
        "handler": "ejecutor.manejar", "image_config": [], "image_uri": None, "kms_key_arn": None, "layers": None,
        "memory_size": 128, "package_type": "Zip", "publish": False, "reserved_concurrent_executions": -1,
        "runtime": "python3.12", "s3_bucket": None, "s3_key": None, "s3_object_version": None, "skip_destroy": False,
        "snap_start": [], "source_code_hash": PIN_B64, "tags": {"Name": NOMBRE}, "timeout": 30,
        "vpc_config": [{"ipv6_allowed_for_dual_stack": False, "security_group_ids": [_id(plan, SG_ADMIN)],
                        "subnet_ids": subredes}],
    }
    desconocido_funcion = {"arn": True, "code_sha256": True, "id": True, "invoke_arn": True, "last_modified": True,
                           "logging_config": True, "qualified_arn": True, "role": True, "tags_all": True,
                           "tracing_config": True, "version": True, "ephemeral_storage": True,
                           "vpc_config": [{"security_group_ids": [False], "subnet_ids": [False, False],
                                           "vpc_id": True}]}
    rol = {"assume_role_policy": json.dumps(CONFIANZA), "description": "Task031 H-031-5 rol de ejecucion propio de la "
           "ejecutora privada D-24", "force_detach_policies": False, "max_session_duration": 3600,
           "name": "PersonalBlogEjecutorDatos", "path": "/", "permissions_boundary": None,
           "tags": {"Name": "PersonalBlogEjecutorDatos"}}
    politica = {"name": "PersonalBlogEjecutorDatos-ejecucion", "policy": json.dumps(permisos(ACCOUNT))}
    logs = {"kms_key_id": None, "name": f"/aws/lambda/{NOMBRE}", "retention_in_days": 14, "skip_destroy": False,
            "tags": {"Name": NOMBRE}}
    plan["resource_changes"] += [
        _crear(LOGS, "aws_cloudwatch_log_group", logs, {"arn": True, "id": True, "tags_all": True}),
        _crear(ROL, "aws_iam_role", rol, {"arn": True, "create_date": True, "id": True, "inline_policy": True,
                                          "managed_policy_arns": True, "tags_all": True, "unique_id": True}),
        _crear(POLITICA, "aws_iam_role_policy", politica, {"id": True, "role": True}),
        _crear(FUNCION, "aws_lambda_function", funcion, desconocido_funcion),
    ]
    plan["output_changes"]["nombre_de_la_ejecutora"] = {"actions": ["create"], "before": None, "after": NOMBRE,
                                                        "after_unknown": False, "after_sensitive": False}
    plan["output_changes"]["arn_de_la_ejecutora"] = {"actions": ["create"], "before": None, "after_unknown": True,
                                                     "after_sensitive": False}
    raiz = plan["configuration"]["root_module"]
    raiz["outputs"].update({"nombre_de_la_ejecutora": {}, "arn_de_la_ejecutora": {}})
    raiz["module_calls"]["red"]["module"]["outputs"]["id_sg_admin"] = {
        "expression": {"references": ["aws_security_group.admin.id", "aws_security_group.admin"]}}
    raiz["module_calls"]["ejecutor_privado"] = {
        "source": "../terraform/modulos/ejecutor_privado",
        "expressions": {
            "id_sg_admin": {"references": ["module.red.id_sg_admin", "module.red"]},
            "ids_de_subredes": {"references": ["module.red.ids_de_subredes", "module.red"]},
        },
        "module": {"resources": [
            {"address": "aws_cloudwatch_log_group.this", "expressions": {}},
            {"address": "aws_iam_role.this", "expressions": {}},
            {"address": "aws_iam_role_policy.this", "expressions": {
                "role": {"references": ["aws_iam_role.this.id", "aws_iam_role.this"]}}},
            {"address": "aws_lambda_function.this", "expressions": {
                "role": {"references": ["aws_iam_role.this.arn", "aws_iam_role.this"]},
                "vpc_config": [{"security_group_ids": {"references": ["var.id_sg_admin"]},
                                "subnet_ids": {"references": ["var.ids_de_subredes"]},
                                "ipv6_allowed_for_dual_stack": {"constant_value": False}}]}},
        ]},
    }
    plan["checks"].append({"address": {"to_display": FUNCION}, "status": "pass"})
    return plan


def cambio(plan, address):
    return next(i for i in plan["resource_changes"] if i["address"] == address)["change"]


def despues(plan, address):
    return cambio(plan, address)["after"]


def con_politica(plan, mutar):
    documento = permisos(ACCOUNT)
    mutar(documento)
    despues(plan, POLITICA)["policy"] = json.dumps(documento)
    return plan


class PlanDeLaEjecutora(unittest.TestCase):
    def pasa(self, plan):
        return check(plan, ACCOUNT, MEDIOS, ahora=AHORA)

    def rechaza(self, plan, codigo):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS, ahora=AHORA)
        self.assertEqual(str(error.exception), codigo)

    # --- Positivos ------------------------------------------------------------

    def test_caso_a_cuatro_creates_y_nada_mas(self):
        r = self.pasa(fixture())
        self.assertEqual(r["gate"], "EXECUTOR_PLAN_OK")
        self.assertEqual((r["add"], r["change"], r["destroy"], r["replace"], r["deferred_changes"]), (4, 0, 0, 0, 0))
        self.assertEqual(r["resource_drift"], 0)
        self.assertEqual(r["inventario"], sorted(NUEVOS))
        self.assertEqual(r["salidas_nuevas"], ["arn_de_la_ejecutora", "nombre_de_la_ejecutora"])

    def test_caso_b_solo_el_atributo_movil_de_rds(self):
        r = self.pasa(con_drift_movil(fixture()))
        self.assertEqual(r["resource_drift"], 1)
        self.assertEqual(r["drift_movil"], ["module.base_de_datos.aws_db_instance.this: latest_restorable_time"])

    # --- Plan, variables e identidad --------------------------------------------

    def test_version_y_semantica_del_plan(self):
        for campo, valor, codigo in (("terraform_version", "1.16.3", "VERSION"), ("applyable", False, "APPLYABLE"),
                                     ("applyable", None, "APPLYABLE"), ("complete", False, "INCOMPLETE"),
                                     ("errored", True, "INCOMPLETE")):
            with self.subTest(campo=campo, valor=valor):
                plan = fixture(); plan[campo] = valor
                self.rechaza(plan, codigo)

    def test_la_efimera_en_el_plan_rechazada(self):
        plan = fixture(); plan["variables"]["contrasena_master"] = {"value": "x"}
        self.rechaza(plan, "EPHEMERAL_LEAK")

    def test_endpoint_alternativo_rechazado(self):
        plan = fixture(); plan["variables"]["endpoints_aws"]["value"]["lambda"] = "http://127.0.0.1:4566"
        self.rechaza(plan, "ALTERNATE_ENDPOINT")

    def test_artefacto_distinto_del_pin_rechazado(self):
        plan = fixture(); plan["variables"]["zip_de_la_ejecutora"]["value"]["sha256"] = "0" * 64
        self.rechaza(plan, "ARTIFACT_PIN")
        plan = fixture(); despues(plan, FUNCION)["source_code_hash"] = base64.b64encode(b"\0" * 32).decode()
        self.rechaza(plan, "ARTIFACT_PIN")

    def test_contrasena_y_retencion_intactas(self):
        plan = fixture(); plan["variables"]["version_de_la_contrasena"]["value"] = 2
        self.rechaza(plan, "PASSWORD_VERSION")
        plan = fixture(); plan["variables"]["dias_de_retencion_de_backups"]["value"] = 7
        self.rechaza(plan, "RETENTION")

    def test_checks(self):
        plan = fixture(); plan["checks"][0]["status"] = "fail"
        self.rechaza(plan, "IDENTITY_CHECK")
        plan = fixture(); plan["checks"][-1]["status"] = "unknown"
        self.rechaza(plan, "CHECKS")

    def test_la_linea_base_de_h0313_ya_no_basta(self):
        """Sin las alarmas ni el rol de D-20 en el state previo, el plan no corresponde a produccion."""
        self.rechaza(fixture(fixture_convergencia()), "PRIOR_STATE")

    def test_cambio_en_las_alarmas_o_en_el_rol_de_grafana_rechazado(self):
        for address in ('module.alarmas_rds.aws_cloudwatch_metric_alarm.this["cpu"]', ROL_DE_GRAFANA):
            with self.subTest(address=address):
                plan = fixture(); cambio(plan, address)["actions"] = ["update"]
                self.rechaza(plan, "EXISTING_CHANGED")

    def test_estado_previo_31_sin_taint(self):
        plan = fixture(); previo(plan, SG_ADMIN)["tainted"] = True
        self.rechaza(plan, "PRIOR_STATE")

    # --- Los 31 existentes: cero cambios --------------------------------------

    def test_cualquier_cambio_en_un_existente_rechazado(self):
        for acciones in (["update"], ["delete"], ["delete", "create"], ["create", "delete"]):
            with self.subTest(acciones=acciones):
                plan = fixture(); cambio(plan, SG_ADMIN)["actions"] = acciones
                self.rechaza(plan, "EXISTING_CHANGED")
        plan = fixture(); cambio(plan, "module.base_de_datos.aws_db_instance.this")["after"]["x"] = "y"
        self.rechaza(plan, "EXISTING_CHANGED")

    # --- Inventario cerrado de creates -----------------------------------------

    def test_un_recurso_no_autorizado_rechazado(self):
        for tipo in ("aws_lambda_permission", "aws_lambda_function_url", "aws_nat_gateway", "aws_internet_gateway",
                     "aws_eip", "aws_iam_role", "aws_vpc_security_group_egress_rule", "aws_iam_role_policy_attachment"):
            with self.subTest(tipo=tipo):
                plan = fixture()
                plan["resource_changes"].append(_crear(f"module.ejecutor_privado.{tipo}.extra", tipo, {}, {}))
                self.rechaza(plan, "UNEXPECTED_RESOURCE")

    def test_falta_un_recurso_nuevo(self):
        for address in NUEVOS:
            with self.subTest(address=address):
                plan = fixture(); plan["resource_changes"] = [i for i in plan["resource_changes"]
                                                              if i["address"] != address]
                self.rechaza(plan, "RESOURCE_SET")

    def test_un_nuevo_que_no_es_create_rechazado(self):
        for acciones in (["update"], ["delete", "create"], ["no-op"]):
            with self.subTest(acciones=acciones):
                plan = fixture(); cambio(plan, FUNCION)["actions"] = acciones
                self.rechaza(plan, "NOT_CREATE")

    def test_import_o_move_rechazado(self):
        plan = fixture(); cambio(plan, ROL)["importing"] = {"id": "existente"}
        self.rechaza(plan, "IMPORT_MOVE")
        plan = fixture()
        next(i for i in plan["resource_changes"] if i["address"] == ROL)["previous_address"] = "aws_iam_role.viejo"
        self.rechaza(plan, "IMPORT_MOVE")

    def test_diferidos_rechazados(self):
        plan = fixture(); plan["deferred_changes"] = [{"resource_change": {"address": FUNCION}}]
        self.rechaza(plan, "DEFERRED")

    # --- Funcion ----------------------------------------------------------------

    def test_funcion_exacta(self):
        for campo, valor in (("runtime", "python3.13"), ("architectures", ["arm64"]), ("handler", "otro.manejar"),
                             ("memory_size", 256), ("timeout", 900), ("publish", True), ("function_name", "otra"),
                             ("layers", ["arn:aws:lambda:us-east-2:123456789012:layer:x:1"]),
                             ("kms_key_arn", "arn:aws:kms:us-east-2:123456789012:key/x"), ("package_type", "Image"),
                             ("file_system_config", [{"arn": "x", "local_mount_path": "/mnt/x"}])):
            with self.subTest(campo=campo):
                plan = fixture(); despues(plan, FUNCION)[campo] = valor
                self.rechaza(plan, "FUNCTION")

    def test_sin_concurrencia_reservada(self):
        """D-24 modificada el 2026-10-18 (aprobada el 2026-10-19): -1, el valor nativo sin reserva. Ni 0, que la apagaria, ni una
        reserva, que la cuota de la cuenta no admite."""
        for valor in (None, 0, 1, 2, True, "-1"):
            with self.subTest(valor=valor):
                plan = fixture(); despues(plan, FUNCION)["reserved_concurrent_executions"] = valor
                self.rechaza(plan, "CONCURRENCY")

    def test_sin_variables_de_entorno(self):
        plan = fixture(); despues(plan, FUNCION)["environment"] = [{"variables": {"X": "y"}}]
        self.rechaza(plan, "ENVIRONMENT")

    def test_red_exacta_solo_sg_admin_y_las_dos_subredes(self):
        casos = {
            "sg_lambda": lambda p: [_id(p, SG_LAMBDA)], "sg_rds": lambda p: [_id(p, SG_RDS)],
            "admin_y_lambda": lambda p: [_id(p, SG_ADMIN), _id(p, SG_LAMBDA)], "por_omision": lambda p: ["sg-default"],
            "ninguno": lambda p: [],
        }
        for nombre, grupos in casos.items():
            with self.subTest(grupos=nombre):
                plan = fixture(); despues(plan, FUNCION)["vpc_config"][0]["security_group_ids"] = grupos(plan)
                self.rechaza(plan, "NETWORK")
        for subredes in (lambda p: [_id(p, SUBRED_A)], lambda p: [_id(p, SUBRED_A), "subnet-ajena"]):
            plan = fixture(); despues(plan, FUNCION)["vpc_config"][0]["subnet_ids"] = subredes(plan)
            self.rechaza(plan, "NETWORK")
        plan = fixture(); despues(plan, FUNCION)["vpc_config"][0]["ipv6_allowed_for_dual_stack"] = True
        self.rechaza(plan, "NETWORK")
        plan = fixture(); despues(plan, FUNCION)["vpc_config"] = []
        self.rechaza(plan, "NETWORK")

    def test_red_desconocida_no_se_puede_verificar(self):
        plan = fixture(); cambio(plan, FUNCION)["after_unknown"]["vpc_config"] = True
        self.rechaza(plan, "UNVERIFIABLE")
        plan = fixture(); cambio(plan, FUNCION)["after_unknown"]["vpc_config"][0]["security_group_ids"] = True
        self.rechaza(plan, "UNVERIFIABLE")
        plan = fixture(); cambio(plan, FUNCION)["after_unknown"]["reserved_concurrent_executions"] = True
        self.rechaza(plan, "UNVERIFIABLE")

    # --- IAM --------------------------------------------------------------------

    def test_rol_propio_exacto(self):
        for campo, valor in (("name", "PersonalBlogDataOperator"), ("path", "/personal-blog/"),
                             ("max_session_duration", 43200),
                             ("permissions_boundary", "arn:aws:iam::123456789012:policy/x")):
            with self.subTest(campo=campo):
                plan = fixture(); despues(plan, ROL)[campo] = valor
                self.rechaza(plan, "ROLE")

    def test_trust_solo_lambda(self):
        variantes = [
            {"Version": "2012-10-17", "Statement": [{**CONFIANZA["Statement"][0],
                                                      "Principal": {"Service": "ec2.amazonaws.com"}}]},
            {"Version": "2012-10-17", "Statement": [{**CONFIANZA["Statement"][0],
                                                      "Principal": {"AWS": "arn:aws:iam::123456789012:root"}}]},
            {"Version": "2012-10-17", "Statement": [CONFIANZA["Statement"][0], CONFIANZA["Statement"][0]]},
        ]
        for documento in variantes:
            with self.subTest(documento=documento):
                plan = fixture(); despues(plan, ROL)["assume_role_policy"] = json.dumps(documento)
                self.rechaza(plan, "TRUST")

    def test_politica_sin_ssm_kms_s3_ni_ampliaciones(self):
        def anadir(accion, recurso="*"):
            return lambda d: d["Statement"].append({"Effect": "Allow", "Action": [accion], "Resource": recurso})

        mutaciones = {
            "ssm": anadir("ssm:GetParameter", "arn:aws:ssm:us-east-2:123456789012:parameter/blog-prod/datos/blogadmin"),
            "kms": anadir("kms:Decrypt"), "s3": anadir("s3:PutObject", "arn:aws:s3:::x/*"),
            "rds": anadir("rds:DescribeDBInstances"), "secretos": anadir("secretsmanager:GetSecretValue"),
            "sin_deny": lambda d: d["Statement"].pop(1),
            "logs_en_todo": lambda d: d["Statement"][2].update(Resource="*"),
            "red_acotada_distinta": lambda d: d["Statement"][0]["Action"].append("ec2:CreateTags"),
        }
        for nombre, mutar in mutaciones.items():
            with self.subTest(mutacion=nombre):
                self.rechaza(con_politica(fixture(), mutar), "POLICY")

    def test_politica_de_otra_cuenta_rechazada(self):
        plan = fixture(); despues(plan, POLITICA)["policy"] = json.dumps(permisos("999999999999"))
        self.rechaza(plan, "POLICY")

    # --- Logs -------------------------------------------------------------------

    def test_logs_14_dias_del_grupo_propio(self):
        for campo, valor in (("retention_in_days", 0), ("retention_in_days", 30), ("retention_in_days", None),
                             ("name", "/aws/lambda/otra"), ("kms_key_id", "arn:aws:kms:us-east-2:1:key/x")):
            with self.subTest(campo=campo, valor=valor):
                plan = fixture(); despues(plan, LOGS)[campo] = valor
                self.rechaza(plan, "LOGS")

    # --- Cableado ---------------------------------------------------------------

    def test_cableado_con_sg_admin_y_las_subredes_de_la_red(self):
        def llamada(p):
            return p["configuration"]["root_module"]["module_calls"]["ejecutor_privado"]

        mutaciones = {
            "sg_lambda": lambda p: llamada(p)["expressions"].update(
                id_sg_admin={"references": ["module.red.id_sg_lambda", "module.red"]}),
            "subredes": lambda p: llamada(p)["expressions"].update(ids_de_subredes={"constant_value": ["subnet-x"]}),
            "salida_de_red": lambda p: p["configuration"]["root_module"]["module_calls"]["red"]["module"]["outputs"][
                "id_sg_admin"]["expression"]["references"].insert(0, "aws_security_group.lambda.id"),
            "grupo_de_la_funcion": lambda p: llamada(p)["module"]["resources"][3]["expressions"]["vpc_config"][0][
                "security_group_ids"]["references"].append("var.otro"),
        }
        for nombre, mutar in mutaciones.items():
            with self.subTest(mutacion=nombre):
                plan = fixture(); mutar(plan)
                self.rechaza(plan, "WIRING")

    def test_el_grupo_por_omision_sigue_sin_uso(self):
        plan = fixture()
        plan["configuration"]["root_module"]["module_calls"]["ejecutor_privado"]["expressions"]["x"] = {
            "references": ["aws_vpc.this.default_security_group_id"]}
        self.rechaza(plan, "DEFAULT_SG_USED")

    # --- Salidas ----------------------------------------------------------------

    def test_salidas(self):
        plan = fixture(); plan["output_changes"]["id_sg_admin"]["actions"] = ["update"]
        self.rechaza(plan, "OUTPUTS")
        plan = fixture(); plan["output_changes"]["alarmas_de_rds"]["actions"] = ["update"]
        self.rechaza(plan, "OUTPUTS")
        plan = fixture(); plan["output_changes"]["rol_de_grafana"]["after"] = "otro"
        self.rechaza(plan, "OUTPUTS")
        plan = fixture(); plan["output_changes"]["nombre_de_la_ejecutora"]["after"] = "otra"
        self.rechaza(plan, "OUTPUTS")
        plan = fixture(); plan["output_changes"]["arn_de_la_ejecutora"]["after_sensitive"] = True
        self.rechaza(plan, "OUTPUTS")
        plan = fixture(); plan["output_changes"].pop("arn_de_la_ejecutora")
        self.rechaza(plan, "OUTPUTS")
        plan = fixture(); plan["output_changes"]["extra"] = copy.deepcopy(plan["output_changes"]["arn_de_la_ejecutora"])
        plan["configuration"]["root_module"]["outputs"]["extra"] = {}
        self.rechaza(plan, "OUTPUTS")

    # --- Drift ------------------------------------------------------------------

    def test_drift_fuera_del_caso_b_rechazado(self):
        plan = con_drift_movil(fixture()); plan["resource_drift"][0]["change"]["after"]["status"] = "modifying"
        self.rechaza(plan, "DRIFT")
        plan = con_drift_movil(fixture()); plan["resource_drift"].append(copy.deepcopy(plan["resource_drift"][0]))
        self.rechaza(plan, "DRIFT")
        plan = con_drift_movil(fixture()); plan["resource_drift"][0]["address"] = SG_ADMIN
        self.rechaza(plan, "DRIFT")
        self.rechaza(con_drift_movil(fixture(), antes="2026-10-05T20:06:50Z", despues="2026-10-05T19:16:49Z"),
                     "MOVING_ATTRIBUTE")

    def test_state_antiguo_con_aws_fresco(self):
        """La situacion real de H-031-5: el state no se escribe desde la convergencia de H-031-9. Enmienda de §40 del
        2026-10-18 (aprobada el 2026-10-19): la antiguedad del state no rechaza; la frescura del valor de AWS, si."""
        r = self.pasa(con_drift_movil(fixture(), antes="2026-10-01T19:16:49Z", despues="2026-10-05T20:55:00Z"))
        self.assertEqual((r["gate"], r["resource_drift"]), ("EXECUTOR_PLAN_OK", 1))

    def test_aws_con_mas_de_24_h_rechazado(self):
        self.rechaza(con_drift_movil(fixture(), antes="2026-10-04T18:00:00Z", despues="2026-10-04T20:59:59Z"),
                     "MOVING_ATTRIBUTE")


if __name__ == "__main__":
    unittest.main()
