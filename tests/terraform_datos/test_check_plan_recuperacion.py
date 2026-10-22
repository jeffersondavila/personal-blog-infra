"""El plan de RECUPERACION de H-031-3 solo puede reemplazar el parameter group tainted y crear RDS.

Tras el apply fallido de H-031-3 (§27.4) existen 20 de 21 recursos y el parameter group quedo
`tainted`. El fixture parte del plan inicial de `test_check_plan.py` y le da la forma que
Terraform 1.16.2 emite para un plan desde ese state: `prior_state` con los 20 recursos,
`no-op` con `before == after` para los 19 intactos, `["delete", "create"]` con
`action_reason = replace_because_tainted` para el grupo y `create` para la instancia.
"""
import copy
import json
import unittest

from scripts.terraform_datos.check_plan import ADDRESSES, PARAMETROS, TIPOS
from scripts.terraform_datos.check_plan_recuperacion import (
    EXISTENTES,
    GRUPO,
    INSTANCIA_RDS,
    SALIDAS_DE_RDS,
    SSM,
    check,
)
from tests.terraform_datos.test_check_plan import ACCOUNT, MEDIOS, fixture as fixture_inicial

SG_RDS = "sg-0000000000000rds0"
SUBRED_A = 'module.red.aws_subnet.privada["a"]'
SALIDAS = ["id_de_vpc", "ids_de_subredes", "id_sg_lambda", "id_sg_admin", "id_sg_rds", "id_endpoint_s3",
           "prefix_list_s3", "endpoint_rds", "puerto_rds", "nombre_de_base", "identificador_rds", "arn_rds",
           "id_de_recurso_rds", "nombre_del_parametro_master", "grupo_de_logs_rds"]
#: Lo que el apply fallido de H-031-3 dejo en el state del grupo: los siete de la D-22 de entonces.
#: Historico y explicito: no depende de los parametros vigentes.
SIETE = sorted({("log_connections", "1", "immediate"), ("log_disconnections", "1", "immediate"),
                ("log_min_duration_statement", "1000", "immediate"), ("log_statement", "ddl", "immediate"),
                ("rds.force_ssl", "1", "immediate"), ("ssl_min_protocol_version", "TLSv1.2", "immediate"),
                ("superuser_reserved_connections", "3", "pending-reboot")})


def _recurso_previo(address, valores, tainted=False):
    modulo, resto = address.split(".", 2)[0:2], address.split(".", 2)[2]
    entrada = {"address": address, "mode": "managed", "type": TIPOS[address],
               "name": resto.split(".")[1].split("[")[0], "values": valores,
               "provider_name": "registry.terraform.io/hashicorp/aws"}
    if tainted:
        entrada["tainted"] = True
    return ".".join(modulo), entrada


def fixture():
    plan = fixture_inicial()
    plan["variables"]["version_de_la_contrasena"] = {"value": 1}
    previos = {"module.red": [], "module.base_de_datos": []}
    for item in plan["resource_changes"]:
        address = item["address"]
        after = item["change"]["after"]
        if address == INSTANCIA_RDS:
            after.update(availability_zone="us-east-2a", vpc_security_group_ids=[SG_RDS])
            continue
        existente = copy.deepcopy(after)
        existente["id"] = SG_RDS if address == "module.red.aws_security_group.rds" else f"id-{address}"
        if address == SUBRED_A:
            existente["availability_zone"] = "us-east-2a"
        if address == GRUPO:
            antes = copy.deepcopy(existente)
            antes["parameter"] = [{"name": n, "value": v, "apply_method": m} for n, v, m in SIETE]
            item["change"] = {"actions": ["delete", "create"], "before": antes, "after": after}
            item["action_reason"] = "replace_because_tainted"
            modulo, previo = _recurso_previo(address, copy.deepcopy(antes), tainted=True)
        else:
            item["change"] = {"actions": ["no-op"], "before": existente, "after": copy.deepcopy(existente)}
            modulo, previo = _recurso_previo(address, copy.deepcopy(existente))
        previos[modulo].append(previo)
    salidas_previas = {n: {"value": f"valor-{n}", "sensitive": False} for n in SALIDAS if n not in SALIDAS_DE_RDS}
    plan["prior_state"] = {"values": {"outputs": salidas_previas, "root_module": {
        "resources": [{"address": "data.aws_caller_identity.operador", "mode": "data",
                       "type": "aws_caller_identity", "name": "operador", "values": {}}],
        "child_modules": [{"address": m, "resources": r} for m, r in previos.items()]}}}
    plan["output_changes"] = {
        n: ({"actions": ["create"], "before": None, "after": None} if n in SALIDAS_DE_RDS
            else {"actions": ["no-op"], "before": f"valor-{n}", "after": f"valor-{n}"})
        for n in SALIDAS}
    plan["configuration"]["root_module"]["outputs"] = {n: {} for n in SALIDAS}
    return plan


def item(plan, address):
    return next(i for i in plan["resource_changes"] if i["address"] == address)


def previo(plan, address):
    for modulo in plan["prior_state"]["values"]["root_module"]["child_modules"]:
        for r in modulo["resources"]:
            if r["address"] == address:
                return r
    raise KeyError(address)


class PlanDeRecuperacion(unittest.TestCase):
    def rechaza(self, plan, codigo):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS)
        self.assertEqual(str(error.exception), codigo)

    def test_plan_esperado(self):
        resultado = check(fixture(), ACCOUNT, MEDIOS)
        self.assertEqual((resultado["add"], resultado["change"], resultado["destroy"]), (2, 0, 1))
        self.assertEqual(resultado["replace"], [GRUPO])
        self.assertEqual(resultado["create"], [INSTANCIA_RDS])
        self.assertEqual(len(resultado["no_op"]), 19)
        self.assertIn(SSM, resultado["no_op"])

    def test_constantes(self):
        self.assertEqual(len(EXISTENTES), 20)
        self.assertEqual(ADDRESSES - EXISTENTES, {INSTANCIA_RDS})

    # --- DN-2 y diferidos: fail-closed ---------------------------------------------------------

    def test_drift_rechazado(self):
        plan = fixture(); plan["resource_drift"] = [{"address": "module.red.aws_security_group.rds"}]
        self.rechaza(plan, "DRIFT_OR_DEFERRED")

    def test_diferido_rechazado(self):
        plan = fixture(); plan["deferred_changes"] = [{"reason": "x"}]
        self.rechaza(plan, "DRIFT_OR_DEFERRED")

    # --- SecureString: la contrasena se reutiliza, version 1 ----------------------------------

    def test_securestring_modificado_rechazado(self):
        plan = fixture(); i = item(plan, SSM)
        i["change"]["actions"] = ["update"]; i["change"]["after"]["value_wo_version"] = 2
        self.rechaza(plan, "SSM_CHANGED")

    def test_securestring_reemplazado_rechazado(self):
        plan = fixture(); item(plan, SSM)["change"]["actions"] = ["delete", "create"]
        self.rechaza(plan, "SSM_CHANGED")

    def test_version_de_la_contrasena_distinta_de_1_rechazada(self):
        plan = fixture(); plan["variables"]["version_de_la_contrasena"]["value"] = 2
        self.rechaza(plan, "PASSWORD_VERSION")

    def test_password_wo_version_distinta_rechazada(self):
        plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["after"]["password_wo_version"] = 2
        self.rechaza(plan, "DB_PASSWORD_WO_VERSION")

    def test_la_efimera_en_variables_es_una_fuga(self):
        plan = fixture(); plan["variables"]["contrasena_master"] = {"value": None}
        self.rechaza(plan, "EPHEMERAL_LEAK")

    def test_secreto_en_la_instancia_rechazado(self):
        plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["after"]["password"] = "x"
        self.rechaza(plan, "SECRET_IN_PLAN")

    # --- Lo existente sigue no-op ---------------------------------------------------------------

    def test_cualquier_recurso_existente_cambiado_rechazado(self):
        for address in sorted(EXISTENTES - {GRUPO, SSM}):
            for acciones in (["update"], ["delete", "create"], ["create", "delete"], ["delete"]):
                with self.subTest(address=address, acciones=acciones):
                    plan = fixture(); item(plan, address)["change"]["actions"] = acciones
                    self.rechaza(plan, "EXISTING_CHANGED")

    def test_no_op_con_valores_distintos_rechazado(self):
        plan = fixture(); item(plan, "module.red.aws_vpc.this")["change"]["after"]["cidr_block"] = "10.0.0.0/16"
        self.rechaza(plan, "EXISTING_CHANGED")

    # --- Parameter group: solo el reemplazo por tainted, delete antes de create ---------------

    def test_grupo_actualizado_en_sitio_rechazado(self):
        plan = fixture(); item(plan, GRUPO)["change"]["actions"] = ["update"]
        self.rechaza(plan, "TAINTED_REPLACE_ONLY")

    def test_grupo_create_before_destroy_rechazado(self):
        plan = fixture(); item(plan, GRUPO)["change"]["actions"] = ["create", "delete"]
        self.rechaza(plan, "TAINTED_REPLACE_ONLY")

    def test_grupo_reemplazado_por_otro_motivo_rechazado(self):
        plan = fixture(); item(plan, GRUPO)["action_reason"] = "replace_because_cannot_update"
        self.rechaza(plan, "TAINTED_REPLACE_ONLY")

    def test_grupo_con_superuser_reserved_connections_rechazado(self):
        plan = fixture()
        item(plan, GRUPO)["change"]["after"]["parameter"].append(
            {"name": "superuser_reserved_connections", "value": "3", "apply_method": "pending-reboot"})
        self.rechaza(plan, "PARAMETERS")

    def test_grupo_con_un_parametro_de_sistema_rechazado(self):
        for nombre, valor in (("rds.force_ssl", "1"), ("ssl_min_protocol_version", "TLSv1.2")):
            with self.subTest(nombre=nombre):
                plan = fixture()
                item(plan, GRUPO)["change"]["after"]["parameter"].append(
                    {"name": nombre, "value": valor, "apply_method": "immediate"})
                self.rechaza(plan, "PARAMETERS")

    def test_grupo_con_otro_nombre_rechazado(self):
        plan = fixture(); item(plan, GRUPO)["change"]["after"]["name"] = "otro"
        self.rechaza(plan, "PARAMETER_GROUP")

    # --- Instancia: create con el contrato de D-22 ---------------------------------------------

    def test_instancia_que_no_es_create_rechazada(self):
        plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["actions"] = ["update"]
        self.rechaza(plan, "NOT_CREATE")

    def test_instancia_debilitada_rechazada(self):
        for atributo, valor, codigo in (
            ("publicly_accessible", True, "DB_PUBLICLY_ACCESSIBLE"), ("multi_az", True, "DB_MULTI_AZ"),
            ("deletion_protection", False, "DB_DELETION_PROTECTION"), ("engine_version", "17.12", "DB_ENGINE_VERSION"),
            ("instance_class", "db.t4g.small", "DB_INSTANCE_CLASS"), ("allocated_storage", 21, "DB_ALLOCATED_STORAGE"),
            ("skip_final_snapshot", True, "DB_SKIP_FINAL_SNAPSHOT"), ("backup_retention_period", 1, "DB_BACKUP_RETENTION_PERIOD"),
            ("parameter_group_name", "default.postgres17", "DB_PARAMETER_GROUP_NAME"),
        ):
            with self.subTest(atributo=atributo):
                plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["after"][atributo] = valor
                self.rechaza(plan, codigo)

    def test_instancia_en_otra_zona_rechazada(self):
        plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["after"]["availability_zone"] = "us-east-2b"
        self.rechaza(plan, "DB_AZ")

    def test_subred_a_fuera_de_use2_az1_rechazada(self):
        # Una subred `a` en otra zona aparece igual en el state previo y en su no-op.
        plan = fixture()
        for valores in (previo(plan, SUBRED_A)["values"], item(plan, SUBRED_A)["change"]["before"],
                        item(plan, SUBRED_A)["change"]["after"]):
            valores["availability_zone_id"] = "use2-az3"
        self.rechaza(plan, "DB_AZ")

    def test_instancia_con_otro_grupo_rechazada(self):
        for grupos in ([SG_RDS, "sg-default"], ["sg-default"], []):
            with self.subTest(grupos=grupos):
                plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["after"]["vpc_security_group_ids"] = grupos
                self.rechaza(plan, "DB_SG")

    # --- Conjunto, state previo y salidas --------------------------------------------------------

    def test_recurso_adicional_rechazado(self):
        plan = fixture()
        plan["resource_changes"].append({"address": "module.red.aws_nat_gateway.this", "mode": "managed",
                                         "type": "aws_nat_gateway", "provider_name": "registry.terraform.io/hashicorp/aws",
                                         "change": {"actions": ["create"], "before": None, "after": {}}})
        self.rechaza(plan, "UNEXPECTED_RESOURCE")

    def test_falta_un_recurso_rechazado(self):
        plan = fixture(); plan["resource_changes"] = [i for i in plan["resource_changes"] if i["address"] != SSM]
        self.rechaza(plan, "RESOURCE_SET")

    def test_import_o_move_rechazados(self):
        plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["importing"] = {"id": "x"}
        self.rechaza(plan, "IMPORT_OR_MOVE")

    def test_state_previo_con_la_instancia_rechazado(self):
        plan = fixture()
        plan["prior_state"]["values"]["root_module"]["child_modules"][1]["resources"].append(
            {"address": INSTANCIA_RDS, "mode": "managed", "type": "aws_db_instance", "name": "this", "values": {}})
        self.rechaza(plan, "PRIOR_STATE")

    def test_state_previo_sin_tainted_o_con_otro_tainted_rechazado(self):
        plan = fixture(); previo(plan, GRUPO).pop("tainted")
        self.rechaza(plan, "PRIOR_STATE")
        plan = fixture(); previo(plan, "module.red.aws_vpc.this")["tainted"] = True
        self.rechaza(plan, "PRIOR_STATE")

    def test_state_previo_con_deposed_rechazado(self):
        plan = fixture(); previo(plan, GRUPO)["deposed_key"] = "abcd"
        self.rechaza(plan, "PRIOR_STATE")

    def test_salida_de_red_cambiada_rechazada(self):
        plan = fixture(); plan["output_changes"]["id_de_vpc"]["actions"] = ["update"]
        self.rechaza(plan, "OUTPUTS")

    def test_salida_de_rds_eliminada_rechazada(self):
        plan = fixture(); plan["output_changes"]["arn_rds"]["actions"] = ["delete"]
        self.rechaza(plan, "OUTPUTS")

    def test_salida_ausente_del_state_previo_puede_crearse(self):
        plan = fixture()
        del plan["prior_state"]["values"]["outputs"]["grupo_de_logs_rds"]
        plan["output_changes"]["grupo_de_logs_rds"] = {"actions": ["create"], "before": None, "after": "x"}
        check(plan, ACCOUNT, MEDIOS)

    def test_salida_sensible_rechazada(self):
        plan = fixture(); plan["planned_values"]["outputs"]["identificador_rds"]["sensitive"] = True
        self.rechaza(plan, "SENSITIVE_OUTPUT")

    def test_identidad_fallida_rechazada(self):
        plan = fixture(); plan["checks"][0]["status"] = "fail"
        self.rechaza(plan, "IDENTITY_CHECK")

    def test_cidr_abierto_rechazado(self):
        plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["after"]["x"] = "0.0.0.0/0"
        self.rechaza(plan, "OPEN_CIDR")

    def test_otra_version_de_terraform_rechazada(self):
        plan = fixture(); plan["terraform_version"] = "1.16.3"
        self.rechaza(plan, "VERSION")

    def test_el_json_del_fixture_es_serializable(self):
        json.dumps(fixture())


if __name__ == "__main__":
    unittest.main()
