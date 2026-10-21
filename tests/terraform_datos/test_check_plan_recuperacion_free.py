"""El plan RECOVERY-3-FREE solo puede crear RDS con retencion 1 y actualizar en sitio el parameter group.

Forma real observada el 2026-10-05 (Task/031 §34), desde el state tras el apply fallido de §32 (20/21,
sin taint, el grupo ya reemplazado con los seis parametros de entonces):
- `aws_db_instance.this`: `create`, con `backup_retention_period = 1` (excepcion temporal del plan FREE);
- `aws_db_parameter_group.this`: `update` en sitio, sin reemplazo: sale del conjunto la representacion de
  `rds.force_ssl` y `ssl_min_protocol_version`, invariantes de sistema que Terraform ya no gestiona;
- los otros 19, SecureString incluido: `no-op` con `before == after`.
`deferred_changes`: fail-closed. `resource_drift`: EXACTAMENTE la excepcion autorizada en
H-031-3-RECOVERY-3-FREE-DRIFT (§35): una entrada, el parameter group, `update`, solo `parameter`, y en ella
solo `rds.force_ssl` (1) y `ssl_min_protocol_version` (TLSv1.2) pasan de `immediate` a `pending-reboot`.

Estructura real de Terraform 1.16.2 (comprobada en el JSON privado): `prior_state` es el state YA
refrescado, igual que el `before` del cambio del grupo y que el `after` del drift; el `before` del drift
es el state de la ejecucion anterior. El fixture lo reproduce asi (antes, por error, ponia en
`prior_state` el state sin refrescar).
"""
import copy
import unittest

from scripts.terraform_datos.check_plan import PARAMETROS
from scripts.terraform_datos.check_plan_recuperacion import GRUPO, INSTANCIA_RDS, SSM
from scripts.terraform_datos.check_plan_recuperacion_free import check
from tests.terraform_datos.test_check_plan_recuperacion import ACCOUNT, MEDIOS, fixture as fixture_recuperacion, item, previo

CUATRO = [{"name": n, "value": v, "apply_method": m} for n, v, m in sorted(PARAMETROS)]
#: Lo que el apply de §32 dejo en el state del grupo: los seis de entonces, todos `immediate`.
SEIS_EN_STATE = sorted(CUATRO + [{"name": "rds.force_ssl", "value": "1", "apply_method": "immediate"},
                                 {"name": "ssl_min_protocol_version", "value": "TLSv1.2", "apply_method": "immediate"}],
                       key=lambda p: p["name"])
#: Lo que el refresh lee de AWS: esos dos, como valores de sistema.
SEIS_REFRESCADOS = sorted(CUATRO + [{"name": "rds.force_ssl", "value": "1", "apply_method": "pending-reboot"},
                                    {"name": "ssl_min_protocol_version", "value": "TLSv1.2", "apply_method": "pending-reboot"}],
                          key=lambda p: p["name"])


def fixture():
    plan = fixture_recuperacion()
    plan["variables"]["dias_de_retencion_de_backups"] = {"value": 1}
    grupo_previo = previo(plan, GRUPO)
    grupo_previo.pop("tainted")
    g = item(plan, GRUPO)
    g.pop("action_reason")
    antes = copy.deepcopy(g["change"]["before"])
    antes["parameter"] = copy.deepcopy(SEIS_REFRESCADOS)
    despues = copy.deepcopy(antes)
    despues["parameter"] = copy.deepcopy(CUATRO)
    g["change"] = {"actions": ["update"], "before": antes, "after": despues, "after_unknown": {}}
    grupo_previo["values"] = copy.deepcopy(antes)  # prior_state = state refrescado
    item(plan, INSTANCIA_RDS)["change"]["after"]["backup_retention_period"] = 1
    plan["resource_drift"] = drift_observado(plan)
    return plan


def drift_observado(plan):
    antes = copy.deepcopy(item(plan, GRUPO)["change"]["before"])
    antes["parameter"] = copy.deepcopy(SEIS_EN_STATE)
    return [{"address": GRUPO, "mode": "managed", "type": "aws_db_parameter_group",
             "provider_name": "registry.terraform.io/hashicorp/aws",
             "change": {"actions": ["update"], "before": antes, "after": copy.deepcopy(item(plan, GRUPO)["change"]["before"]),
                        "after_unknown": {}}}]


def deriva(plan):
    return plan["resource_drift"][0]["change"]


class PlanRecuperacionFree(unittest.TestCase):
    def rechaza(self, plan, codigo):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS)
        self.assertEqual(str(error.exception), codigo)

    def test_forma_esperada_con_el_drift_exacto_pasa(self):
        # Requisito cambiado en §35: la forma valida incluye la unica excepcion de drift autorizada.
        r = check(fixture(), ACCOUNT, MEDIOS)
        self.assertEqual((r["add"], r["change"], r["destroy"]), (1, 1, 0))
        self.assertEqual(r["resource_drift_admitido"], [GRUPO])
        self.assertEqual(r["create"], [INSTANCIA_RDS])
        self.assertEqual(r["update"], [GRUPO])
        self.assertEqual(len(r["no_op"]), 19)
        self.assertEqual(r["backup_retention_period"], 1)

    # --- Retencion: exactamente la excepcion temporal ------------------------------------------

    def test_retencion_distinta_de_1_rechazada(self):
        for valor in (0, 7, 2, 35):
            with self.subTest(valor=valor):
                plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["after"]["backup_retention_period"] = valor
                self.rechaza(plan, "DB_BACKUP_RETENTION_PERIOD")

    def test_variable_de_retencion_distinta_de_1_rechazada(self):
        for valor in (7, None):
            with self.subTest(valor=valor):
                plan = fixture(); plan["variables"]["dias_de_retencion_de_backups"]["value"] = valor
                self.rechaza(plan, "RETENTION")

    # --- Parameter group: update en sitio, nunca destroy ni replace ----------------------------

    def test_grupo_reemplazado_o_destruido_rechazado(self):
        for acciones in (["delete", "create"], ["create", "delete"], ["delete"], ["create"]):
            with self.subTest(acciones=acciones):
                plan = fixture(); item(plan, GRUPO)["change"]["actions"] = acciones
                self.rechaza(plan, "GROUP_UPDATE_ONLY")

    def test_grupo_con_motivo_de_reemplazo_rechazado(self):
        plan = fixture(); item(plan, GRUPO)["action_reason"] = "replace_because_tainted"
        self.rechaza(plan, "GROUP_UPDATE_ONLY")

    def test_grupo_que_vuelve_a_gestionar_un_parametro_de_sistema_rechazado(self):
        plan = fixture()
        item(plan, GRUPO)["change"]["after"]["parameter"].append(
            {"name": "rds.force_ssl", "value": "1", "apply_method": "immediate"})
        self.rechaza(plan, "PARAMETERS")

    def test_grupo_que_pierde_un_parametro_explicito_rechazado(self):
        plan = fixture()
        despues = item(plan, GRUPO)["change"]["after"]
        despues["parameter"] = [p for p in despues["parameter"] if p["name"] != "log_statement"]
        self.rechaza(plan, "PARAMETERS")

    def test_transicion_que_retira_otra_cosa_rechazada(self):
        plan = fixture()
        antes = item(plan, GRUPO)["change"]["before"]
        antes["parameter"] = [p for p in antes["parameter"] if p["name"] != "ssl_min_protocol_version"] + [
            {"name": "work_mem", "value": "4096", "apply_method": "immediate"}]
        self.rechaza(plan, "PARAMETER_TRANSITION")

    def test_transicion_con_otro_valor_de_tls_rechazada(self):
        plan = fixture()
        for p in item(plan, GRUPO)["change"]["before"]["parameter"]:
            if p["name"] == "ssl_min_protocol_version":
                p["value"] = "TLSv1.1"
        self.rechaza(plan, "PARAMETER_TRANSITION")

    def test_otro_atributo_del_grupo_rechazado(self):
        plan = fixture(); item(plan, GRUPO)["change"]["after"]["description"] = "otra"
        self.rechaza(plan, "ONLY_PARAMETER")

    # --- Instancia --------------------------------------------------------------------------------

    def test_instancia_que_no_es_create_rechazada(self):
        plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["actions"] = ["update"]
        self.rechaza(plan, "NOT_CREATE")

    def test_instancia_debilitada_rechazada(self):
        for atributo, valor, codigo in (("publicly_accessible", True, "DB_PUBLICLY_ACCESSIBLE"),
                                        ("multi_az", True, "DB_MULTI_AZ"),
                                        ("deletion_protection", False, "DB_DELETION_PROTECTION"),
                                        ("skip_final_snapshot", True, "DB_SKIP_FINAL_SNAPSHOT"),
                                        ("password_wo_version", 2, "DB_PASSWORD_WO_VERSION")):
            with self.subTest(atributo=atributo):
                plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["after"][atributo] = valor
                self.rechaza(plan, codigo)

    def test_instancia_en_otra_zona_o_con_otro_grupo_rechazada(self):
        plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["after"]["availability_zone"] = "us-east-2b"
        self.rechaza(plan, "DB_AZ")
        plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["after"]["vpc_security_group_ids"] = ["sg-default"]
        self.rechaza(plan, "DB_SG")

    def test_secreto_en_el_plan_rechazado(self):
        plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["after"]["password"] = "x"
        self.rechaza(plan, "SECRET_IN_PLAN")
        plan = fixture(); plan["variables"]["contrasena_master"] = {"value": None}
        self.rechaza(plan, "EPHEMERAL_LEAK")

    def test_version_de_la_contrasena_distinta_rechazada(self):
        plan = fixture(); plan["variables"]["version_de_la_contrasena"]["value"] = 2
        self.rechaza(plan, "PASSWORD_VERSION")

    # --- SSM, red y recursos ajenos ----------------------------------------------------------------

    def test_ssm_cambiado_rechazado(self):
        for acciones in (["update"], ["delete", "create"]):
            with self.subTest(acciones=acciones):
                plan = fixture(); item(plan, SSM)["change"]["actions"] = acciones
                self.rechaza(plan, "SSM_CHANGED")

    def test_red_cambiada_rechazada(self):
        for address in ("module.red.aws_vpc.this", "module.red.aws_security_group.rds",
                        "module.red.aws_vpc_endpoint.s3", 'module.red.aws_route_table.privada["a"]'):
            for acciones in (["update"], ["delete", "create"], ["delete"]):
                with self.subTest(address=address, acciones=acciones):
                    plan = fixture(); item(plan, address)["change"]["actions"] = acciones
                    self.rechaza(plan, "EXISTING_CHANGED")

    def test_recursos_ajenos_rechazados(self):
        for tipo in ("aws_iam_role", "aws_nat_gateway", "aws_internet_gateway"):
            with self.subTest(tipo=tipo):
                plan = fixture()
                plan["resource_changes"].append({"address": f"module.red.{tipo}.x", "mode": "managed", "type": tipo,
                                                 "provider_name": "registry.terraform.io/hashicorp/aws",
                                                 "change": {"actions": ["create"], "before": None, "after": {}}})
                self.rechaza(plan, "UNEXPECTED_RESOURCE")

    def test_import_o_move_rechazados(self):
        plan = fixture(); item(plan, INSTANCIA_RDS)["change"]["importing"] = {"id": "x"}
        self.rechaza(plan, "IMPORT_OR_MOVE")

    def test_state_previo_con_taint_rechazado(self):
        plan = fixture(); previo(plan, GRUPO)["tainted"] = True
        self.rechaza(plan, "PRIOR_STATE")

    # --- Drift y diferidos: fail-closed, y comprobados AL FINAL ----------------------------------

    def test_sin_el_drift_exacto_se_rechaza(self):
        # Requisito cambiado en §35: debe existir EXACTAMENTE resource_drift = 1.
        plan = fixture(); plan["resource_drift"] = []
        self.rechaza(plan, "DRIFT_EXCEPTION")

    def test_cualquier_diferido_rechazado(self):
        plan = fixture(); plan["deferred_changes"] = [{"reason": "x"}]
        self.rechaza(plan, "DRIFT_OR_DEFERRED")

    def test_drift_se_comprueba_despues_de_todo_lo_demas(self):
        # Con drift Y retencion 7, el primer motivo que aflora es la retencion: un DRIFT_OR_DEFERRED
        # sobre el plan real significa que todo lo demas cumple.
        plan = fixture()
        item(plan, INSTANCIA_RDS)["change"]["after"]["backup_retention_period"] = 7
        self.rechaza(plan, "DB_BACKUP_RETENTION_PERIOD")


class ExcepcionDeDriftExacta(unittest.TestCase):
    """§35: la unica excepcion de drift autorizada, y nada mas."""

    def rechaza(self, plan, codigo="DRIFT_EXCEPTION"):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS)
        self.assertEqual(str(error.exception), codigo)

    @staticmethod
    def _parametro(lista, nombre):
        return next(p for p in lista if p["name"] == nombre)

    def test_exactamente_ese_unico_drift_pasa(self):
        r = check(fixture(), ACCOUNT, MEDIOS)
        self.assertEqual(r["resource_drift_admitido"], [GRUPO])
        self.assertEqual(r["drift_parametros"], ["rds.force_ssl", "ssl_min_protocol_version"])

    def test_segunda_direccion_de_drift(self):
        plan = fixture()
        otra = copy.deepcopy(plan["resource_drift"][0])
        otra["address"] = "module.red.aws_security_group.rds"; otra["type"] = "aws_security_group"
        plan["resource_drift"].append(otra)
        self.rechaza(plan)

    def test_otra_direccion_en_lugar_del_grupo(self):
        plan = fixture(); plan["resource_drift"][0]["address"] = "module.red.aws_vpc.this"
        self.rechaza(plan)

    def test_otro_atributo_del_grupo(self):
        for atributo, valor in (("description", "otra"), ("name_prefix", "x"), ("family", "postgres16")):
            with self.subTest(atributo=atributo):
                plan = fixture(); deriva(plan)["after"][atributo] = valor
                self.rechaza(plan)

    def test_cambio_de_valor_de_rds_force_ssl(self):
        plan = fixture(); self._parametro(deriva(plan)["after"]["parameter"], "rds.force_ssl")["value"] = "0"
        self.rechaza(plan)

    def test_cambio_de_valor_de_ssl_min_protocol_version(self):
        plan = fixture()
        self._parametro(deriva(plan)["after"]["parameter"], "ssl_min_protocol_version")["value"] = "TLSv1.3"
        self.rechaza(plan)

    def test_falta_uno_de_los_dos(self):
        plan = fixture()
        self._parametro(deriva(plan)["after"]["parameter"], "ssl_min_protocol_version")["apply_method"] = "immediate"
        self.rechaza(plan)
        plan = fixture()
        d = deriva(plan)
        d["after"]["parameter"] = [p for p in d["after"]["parameter"] if p["name"] != "rds.force_ssl"]
        self.rechaza(plan)

    def test_tercer_parametro(self):
        plan = fixture(); self._parametro(deriva(plan)["after"]["parameter"], "log_statement")["apply_method"] = "pending-reboot"
        self.rechaza(plan)
        plan = fixture()
        for lado in ("before", "after"):
            deriva(plan)[lado]["parameter"].append(
                {"name": "superuser_reserved_connections", "value": "3", "apply_method": "pending-reboot"})
        self.rechaza(plan)

    def test_pending_reboot_a_immediate(self):
        plan = fixture()
        d = deriva(plan)
        d["before"], d["after"] = d["after"], d["before"]
        self.rechaza(plan)

    def test_otra_accion(self):
        for acciones in (["delete"], ["create"], ["delete", "create"], ["no-op"]):
            with self.subTest(acciones=acciones):
                plan = fixture(); deriva(plan)["actions"] = acciones
                self.rechaza(plan)

    def test_deferred_distinto_de_cero(self):
        plan = fixture(); plan["deferred_changes"] = [{"reason": "provider_config_unknown"}]
        self.rechaza(plan, "DRIFT_OR_DEFERRED")

    def test_import_move_o_desconocido_en_el_drift(self):
        plan = fixture(); deriva(plan)["importing"] = {"id": "x"}
        self.rechaza(plan)
        plan = fixture(); plan["resource_drift"][0]["previous_address"] = "module.otro.aws_db_parameter_group.this"
        self.rechaza(plan)
        plan = fixture(); deriva(plan)["after_unknown"] = {"parameter": True}
        self.rechaza(plan)

    def test_incoherencia_con_el_plan(self):
        # El after del drift debe ser el before del cambio del grupo y el prior_state.
        plan = fixture(); deriva(plan)["after"]["tags_all"] = {"x": "y"}; deriva(plan)["before"]["tags_all"] = {"x": "y"}
        self.rechaza(plan)
        plan = fixture(); previo(plan, GRUPO)["values"]["description"] = "otra"
        self.rechaza(plan)


if __name__ == "__main__":
    unittest.main()
