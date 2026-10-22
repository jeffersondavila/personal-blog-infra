"""El refresh-only de DN-2 (H-031-3-RECOVERY) solo puede reconciliar CUATRO representaciones del state.

Contrato fijado por el usuario antes de ver el plan:
- `aws_security_group.admin`: `egress: [] ->` reflejo de `admin_a_rds`;
- `aws_security_group.lambda`: `egress: [] ->` reflejo de `lambda_a_rds` y `lambda_a_s3`;
- `aws_security_group.rds`: `ingress: [] ->` reflejo de `rds_desde_lambda` y `rds_desde_admin`;
- `aws_db_parameter_group.this` (tainted): `name_prefix: null -> ""` y el `apply_method` de
  `rds.force_ssl` y `ssl_min_protocol_version` de `immediate` a `pending-reboot`, sin cambio de valor.
Cero cambios de infraestructura, cero diferidos, salidas `no-op` y el taint conservado.
"""
import copy
import unittest

from scripts.terraform_datos.check_plan_dn2 import DRIFT, SALIDAS_RDS, check
from scripts.terraform_datos.check_plan_recuperacion import GRUPO
from tests.terraform_datos.test_check_plan_recuperacion import ACCOUNT, MEDIOS, SALIDAS, fixture as fixture_recuperacion

SG = {"lambda": "sg-0000000000000lamb", "admin": "sg-0000000000000admi", "rds": "sg-0000000000000rds0"}
PL = "pl-00000s3"
#: Direccion de la regla -> (grupo, sentido, puerto, destino, descripcion, es prefix list)
REGLAS = {
    "module.red.aws_vpc_security_group_ingress_rule.rds_desde_lambda": ("rds", "ingress", 5432, "lambda", "PostgreSQL desde la Lambda de aplicacion"),
    "module.red.aws_vpc_security_group_ingress_rule.rds_desde_admin": ("rds", "ingress", 5432, "admin", "PostgreSQL desde la ejecutora privada"),
    "module.red.aws_vpc_security_group_egress_rule.lambda_a_rds": ("lambda", "egress", 5432, "rds", "PostgreSQL hacia RDS"),
    "module.red.aws_vpc_security_group_egress_rule.lambda_a_s3": ("lambda", "egress", 443, None, "HTTPS hacia S3 por el gateway endpoint"),
    "module.red.aws_vpc_security_group_egress_rule.admin_a_rds": ("admin", "egress", 5432, "rds", "PostgreSQL hacia RDS"),
}


def en_linea(destino_sg, puerto, descripcion, prefix=False):
    return {"cidr_blocks": [], "description": descripcion, "from_port": puerto, "ipv6_cidr_blocks": [],
            "prefix_list_ids": [PL] if prefix else [], "protocol": "tcp",
            "security_groups": [] if prefix else [destino_sg], "self": False, "to_port": puerto}


def reflejo(grupo, sentido):
    return [en_linea(SG.get(destino), puerto, desc, prefix=destino is None)
            for g, s, puerto, destino, desc in REGLAS.values() if g == grupo and s == sentido]


def _previos(plan):
    salida = {}
    for m in plan["prior_state"]["values"]["root_module"]["child_modules"]:
        for r in m["resources"]:
            salida[r["address"]] = r
    return salida


def fixture():
    plan = fixture_recuperacion()
    plan.pop("resource_changes")
    previos = _previos(plan)
    for grupo, sg in SG.items():
        valores = previos[f"module.red.aws_security_group.{grupo}"]["values"]
        valores.update(id=sg, ingress=[], egress=[], name_prefix="")
    for direccion, (grupo, _sentido, puerto, destino, desc) in REGLAS.items():
        valores = previos[direccion]["values"]
        valores.update(security_group_id=SG[grupo], description=desc, from_port=puerto, to_port=puerto,
                       ip_protocol="tcp", referenced_security_group_id=SG.get(destino),
                       prefix_list_id=PL if destino is None else None, cidr_ipv4=None, cidr_ipv6=None)
    previos["module.red.aws_vpc_endpoint.s3"]["values"]["prefix_list_id"] = PL
    grupo_antes = previos[GRUPO]["values"]
    grupo_antes["name_prefix"] = None
    grupo_despues = copy.deepcopy(grupo_antes)
    grupo_despues["name_prefix"] = ""
    for p in grupo_despues["parameter"]:
        if p["name"] in ("rds.force_ssl", "ssl_min_protocol_version"):
            p["apply_method"] = "pending-reboot"
    deriva = []
    for grupo, sentido in (("admin", "egress"), ("lambda", "egress"), ("rds", "ingress")):
        direccion = f"module.red.aws_security_group.{grupo}"
        antes = copy.deepcopy(previos[direccion]["values"])
        despues = copy.deepcopy(antes)
        despues[sentido] = reflejo(grupo, sentido)
        deriva.append(_entrada(direccion, "aws_security_group", antes, despues))
    deriva.append(_entrada(GRUPO, "aws_db_parameter_group", copy.deepcopy(grupo_antes), grupo_despues))
    plan["resource_drift"] = deriva
    # H-031-3-RECOVERY-DN2-OUTPUTS: las tres salidas de RDS con valor conocido en el plan quedaron en el
    # state tras el apply fallido; las seis dependen de la instancia y el refresh-only las reevalua.
    previas = plan["prior_state"]["values"]["outputs"]
    for nombre, (_accion, antes) in SALIDAS_RDS.items():
        if antes is not None:
            previas[nombre] = {"value": antes, "type": "number" if isinstance(antes, int) else "string",
                               "sensitive": False}
    plan["output_changes"] = {
        n: ({"actions": [SALIDAS_RDS[n][0]], "before": SALIDAS_RDS[n][1], "after": None, "after_unknown": True,
             "before_sensitive": False, "after_sensitive": False} if n in SALIDAS_RDS
            else {"actions": ["no-op"], "before": f"valor-{n}", "after": f"valor-{n}", "after_unknown": False,
                  "before_sensitive": False, "after_sensitive": False})
        for n in SALIDAS}
    return plan


def _entrada(direccion, tipo, antes, despues):
    return {"address": direccion, "mode": "managed", "type": tipo,
            "provider_name": "registry.terraform.io/hashicorp/aws",
            "change": {"actions": ["update"], "before": antes, "after": despues, "after_unknown": {}}}


def deriva(plan, direccion):
    return next(d for d in plan["resource_drift"] if d["address"] == direccion)


class RefreshDn2(unittest.TestCase):
    def rechaza(self, plan, codigo):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS)
        self.assertEqual(str(error.exception), codigo)

    def test_cuatro_drift_exactos_pasan(self):
        resultado = check(fixture(), ACCOUNT, MEDIOS)
        self.assertEqual(resultado["resource_drift"], 4)
        self.assertEqual(resultado["resource_changes"], 0)
        self.assertEqual(resultado["tainted"], [GRUPO])
        self.assertEqual(set(resultado["atributos"]), set(DRIFT))

    def test_una_quinta_direccion_rechazada(self):
        plan = fixture()
        extra = copy.deepcopy(deriva(plan, "module.red.aws_security_group.admin"))
        extra["address"] = "module.red.aws_vpc.this"; extra["type"] = "aws_vpc"
        plan["resource_drift"].append(extra)
        self.rechaza(plan, "UNEXPECTED_DRIFT")

    def test_falta_una_direccion_rechazada(self):
        plan = fixture(); plan["resource_drift"] = plan["resource_drift"][1:]
        self.rechaza(plan, "DRIFT_SET")

    def test_regla_sg_extra_rechazada(self):
        plan = fixture()
        deriva(plan, "module.red.aws_security_group.admin")["change"]["after"]["egress"].append(
            en_linea(SG["lambda"], 22, "SSH"))
        self.rechaza(plan, "SG_REFLECTION")

    def test_cidr_abierto_rechazado(self):
        plan = fixture()
        deriva(plan, "module.red.aws_security_group.rds")["change"]["after"]["ingress"][0]["cidr_blocks"] = ["0.0.0.0/0"]
        self.rechaza(plan, "OPEN_CIDR")

    def test_puerto_o_grupo_o_prefix_list_distintos_rechazados(self):
        for campo, valor in (("from_port", 5433), ("security_groups", ["sg-otro"]), ("description", "otra")):
            with self.subTest(campo=campo):
                plan = fixture()
                deriva(plan, "module.red.aws_security_group.lambda")["change"]["after"]["egress"][1][campo] = valor
                self.rechaza(plan, "SG_REFLECTION")
        plan = fixture()
        deriva(plan, "module.red.aws_security_group.lambda")["change"]["after"]["egress"][0]["prefix_list_ids"] = ["pl-otra"]
        self.rechaza(plan, "SG_REFLECTION")

    def test_salida_por_omision_restaurada_rechazada(self):
        plan = fixture()
        deriva(plan, "module.red.aws_security_group.rds")["change"]["after"]["egress"] = [
            {"cidr_blocks": ["0.0.0.0/0"], "description": "", "from_port": 0, "ipv6_cidr_blocks": [],
             "prefix_list_ids": [], "protocol": "-1", "security_groups": [], "self": False, "to_port": 0}]
        self.rechaza(plan, "ONLY_EXPECTED_ATTRIBUTES")

    def test_otro_atributo_del_sg_rechazado(self):
        plan = fixture(); deriva(plan, "module.red.aws_security_group.admin")["change"]["after"]["description"] = "otra"
        self.rechaza(plan, "ONLY_EXPECTED_ATTRIBUTES")

    def test_cambio_de_valor_tls_rechazado(self):
        plan = fixture()
        for p in deriva(plan, GRUPO)["change"]["after"]["parameter"]:
            if p["name"] == "ssl_min_protocol_version":
                p["value"] = "TLSv1.3"
        self.rechaza(plan, "PARAMETER_TRANSITION")

    def test_otro_apply_method_cambiado_rechazado(self):
        plan = fixture()
        for p in deriva(plan, GRUPO)["change"]["after"]["parameter"]:
            if p["name"] == "log_statement":
                p["apply_method"] = "pending-reboot"
        self.rechaza(plan, "PARAMETER_TRANSITION")

    def test_parametro_anadido_o_retirado_rechazado(self):
        plan = fixture(); deriva(plan, GRUPO)["change"]["after"]["parameter"].pop()
        self.rechaza(plan, "PARAMETER_TRANSITION")

    def test_name_prefix_distinto_rechazado(self):
        for valor in ("blog-", None):
            with self.subTest(valor=valor):
                plan = fixture(); deriva(plan, GRUPO)["change"]["after"]["name_prefix"] = valor
                self.rechaza(plan, "NAME_PREFIX" if valor is not None else "ONLY_EXPECTED_ATTRIBUTES")

    def test_otro_atributo_del_grupo_rechazado(self):
        plan = fixture(); deriva(plan, GRUPO)["change"]["after"]["family"] = "postgres16"
        self.rechaza(plan, "ONLY_EXPECTED_ATTRIBUTES")

    def test_create_update_delete_rechazados(self):
        for acciones in (["create"], ["update"], ["delete"], ["delete", "create"]):
            with self.subTest(acciones=acciones):
                plan = fixture()
                plan["resource_changes"] = [{"address": GRUPO, "mode": "managed", "type": "aws_db_parameter_group",
                                             "change": {"actions": acciones}}]
                self.rechaza(plan, "RESOURCE_CHANGES")

    def test_accion_de_drift_distinta_rechazada(self):
        plan = fixture(); deriva(plan, GRUPO)["change"]["actions"] = ["delete"]
        self.rechaza(plan, "ACTIONS")

    def test_diferido_rechazado(self):
        plan = fixture(); plan["deferred_changes"] = [{"reason": "x"}]
        self.rechaza(plan, "DEFERRED")

    def test_import_o_move_rechazados(self):
        plan = fixture(); deriva(plan, GRUPO)["change"]["importing"] = {"id": "x"}
        self.rechaza(plan, "IMPORT_OR_MOVE")
        plan = fixture(); deriva(plan, GRUPO)["previous_address"] = "module.otro.aws_db_parameter_group.this"
        self.rechaza(plan, "IMPORT_OR_MOVE")

    def test_taint_perdido_o_trasladado_rechazado(self):
        plan = fixture(); _previos(plan)[GRUPO].pop("tainted")
        self.rechaza(plan, "TAINT")
        plan = fixture(); _previos(plan)["module.red.aws_vpc.this"]["tainted"] = True
        self.rechaza(plan, "TAINT")

    def test_state_previo_distinto_de_20_rechazado(self):
        plan = fixture()
        plan["prior_state"]["values"]["root_module"]["child_modules"][1]["resources"].append(
            {"address": "module.base_de_datos.aws_db_instance.this", "mode": "managed", "type": "aws_db_instance",
             "name": "this", "values": {}})
        self.rechaza(plan, "PRIOR_STATE")

    def test_salida_que_cambia_rechazada(self):
        # Requisito cambiado en H-031-3-RECOVERY-DN2-OUTPUTS: create/update de esas dos salidas es ahora
        # el contrato; fuera de el, cualquier accion sigue rechazada.
        for nombre, acciones in (("arn_rds", ["update"]), ("identificador_rds", ["create"]), ("id_de_vpc", ["delete"])):
            with self.subTest(nombre=nombre):
                plan = fixture(); plan["output_changes"][nombre]["actions"] = acciones
                self.rechaza(plan, "OUTPUTS")

    def test_la_efimera_en_variables_es_una_fuga(self):
        plan = fixture(); plan["variables"]["contrasena_master"] = {"value": None}
        self.rechaza(plan, "EPHEMERAL_LEAK")

    def test_version_de_la_contrasena_distinta_rechazada(self):
        plan = fixture(); plan["variables"]["version_de_la_contrasena"]["value"] = 2
        self.rechaza(plan, "PASSWORD_VERSION")

    def test_valor_desconocido_en_el_drift_rechazado(self):
        plan = fixture(); deriva(plan, GRUPO)["change"]["after_unknown"] = {"parameter": True}
        self.rechaza(plan, "ONLY_EXPECTED_ATTRIBUTES")


class SalidasDeRdsDn2(unittest.TestCase):
    """Las seis salidas que dependen de la instancia inexistente: transiciones EXACTAS, ninguna mas."""

    def rechaza(self, plan, codigo="OUTPUTS"):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS)
        self.assertEqual(str(error.exception), codigo)

    def test_las_seis_transiciones_exactas_pasan(self):
        resultado = check(fixture(), ACCOUNT, MEDIOS)
        self.assertEqual(resultado["salidas_excepcionales"], sorted(SALIDAS_RDS))
        self.assertEqual(resultado["salidas_no_op"], len(SALIDAS) - 6)
        self.assertEqual(SALIDAS_RDS, {
            "arn_rds": ("create", None), "endpoint_rds": ("create", None), "id_de_recurso_rds": ("create", None),
            "identificador_rds": ("update", "blog-prod-postgres"), "nombre_de_base": ("update", "personal_blog"),
            "puerto_rds": ("update", 5432)})

    def test_falta_una_de_las_seis(self):
        for nombre in SALIDAS_RDS:
            with self.subTest(nombre=nombre):
                plan = fixture(); del plan["output_changes"][nombre]
                self.rechaza(plan)

    def test_una_de_las_seis_como_no_op_rechazada(self):
        plan = fixture()
        plan["output_changes"]["endpoint_rds"].update(actions=["no-op"], after_unknown=False)
        self.rechaza(plan)

    def test_aparece_una_septima(self):
        plan = fixture()
        plan["output_changes"]["grupo_de_logs_rds"].update(actions=["update"], after=None, after_unknown=True)
        self.rechaza(plan)
        plan = fixture()
        plan["output_changes"]["otra_salida"] = {"actions": ["create"], "before": None, "after": None,
                                                 "after_unknown": True, "before_sensitive": False,
                                                 "after_sensitive": False}
        self.rechaza(plan)

    def test_arn_rds_update_en_vez_de_create(self):
        plan = fixture(); plan["output_changes"]["arn_rds"]["actions"] = ["update"]
        self.rechaza(plan)

    def test_identificador_rds_create_en_vez_de_update(self):
        plan = fixture(); plan["output_changes"]["identificador_rds"]["actions"] = ["create"]
        self.rechaza(plan)

    def test_before_incorrecto(self):
        for nombre, valor in (("identificador_rds", "otro"), ("nombre_de_base", None), ("puerto_rds", "5432"),
                              ("puerto_rds", 5433), ("arn_rds", "arn:aws:rds:us-east-2:123456789012:db:x")):
            with self.subTest(nombre=nombre, valor=valor):
                plan = fixture(); plan["output_changes"][nombre]["before"] = valor
                self.rechaza(plan)

    def test_after_no_es_null(self):
        for nombre in ("endpoint_rds", "puerto_rds"):
            with self.subTest(nombre=nombre):
                plan = fixture(); plan["output_changes"][nombre]["after"] = "conocido"
                self.rechaza(plan)

    def test_after_unknown_false(self):
        for nombre in ("id_de_recurso_rds", "nombre_de_base"):
            with self.subTest(nombre=nombre):
                plan = fixture(); plan["output_changes"][nombre]["after_unknown"] = False
                self.rechaza(plan)

    def test_salida_sensible(self):
        for campo in ("before_sensitive", "after_sensitive"):
            with self.subTest(campo=campo):
                plan = fixture(); plan["output_changes"]["arn_rds"][campo] = True
                self.rechaza(plan)
        plan = fixture(); plan["planned_values"]["outputs"]["identificador_rds"]["sensitive"] = True
        self.rechaza(plan, "SENSITIVE_OUTPUT")

    def test_salida_de_red_deja_de_ser_no_op(self):
        for nombre in ("id_de_vpc", "ids_de_subredes", "id_sg_rds", "id_endpoint_s3", "prefix_list_s3",
                       "grupo_de_logs_rds", "nombre_del_parametro_master"):
            with self.subTest(nombre=nombre):
                plan = fixture(); plan["output_changes"][nombre]["after"] = "otro"
                self.rechaza(plan)

    def test_coherencia_con_el_state_previo(self):
        plan = fixture(); del plan["prior_state"]["values"]["outputs"]["identificador_rds"]
        self.rechaza(plan)
        plan = fixture(); plan["prior_state"]["values"]["outputs"]["puerto_rds"]["value"] = 5433
        self.rechaza(plan)
        plan = fixture()
        plan["prior_state"]["values"]["outputs"]["arn_rds"] = {"value": "x", "type": "string", "sensitive": False}
        self.rechaza(plan)


if __name__ == "__main__":
    unittest.main()
