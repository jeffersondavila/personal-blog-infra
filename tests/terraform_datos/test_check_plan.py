"""Regresiones de seguridad: el primer plan de red y RDS no puede ampliar ni debilitar lo aprobado.

El fixture reproduce la ESTRUCTURA del plan JSON real que Terraform 1.16.2 emitio
para este root contra el laboratorio en H-031-1 —variables sin la efimera,
`checks` con la guarda de identidad, `password`/`password_wo`/`value_wo` nulos—,
con los valores de produccion. No es un plan real de AWS: ese se genera en
H-031-2 y se revisa en privado.
"""
import copy
import json
import unittest

from scripts.terraform_datos.check_plan import (
    ADDRESSES,
    ETIQUETAS,
    INSTANCIA,
    PARAMETROS,
    SUBREDES,
    TIPOS,
    check,
    politica_del_endpoint,
)

ACCOUNT = "123456789012"
MEDIOS = "arn:aws:s3:::personal-blog-medios-ejemplo"


def _etiquetas(nombre):
    return {**ETIQUETAS, "Name": nombre}


def _valores():
    regla = {"ip_protocol": "tcp", "cidr_ipv4": None, "cidr_ipv6": None, "region": "us-east-2"}
    v = {
        "module.red.aws_vpc.this": {
            "cidr_block": "10.40.0.0/16", "enable_dns_support": True, "enable_dns_hostnames": True,
            "assign_generated_ipv6_cidr_block": False, "tags_all": _etiquetas("blog-prod-vpc"),
        },
        "module.red.aws_vpc_endpoint.s3": {
            "vpc_endpoint_type": "Gateway", "service_name": "com.amazonaws.us-east-2.s3",
            "policy": json.dumps(politica_del_endpoint(MEDIOS)), "tags_all": _etiquetas("blog-prod-s3"),
        },
        "module.base_de_datos.aws_db_subnet_group.this": {"name": "blog-prod-postgres", "tags_all": _etiquetas("x")},
        "module.base_de_datos.aws_db_parameter_group.this": {
            "name": "blog-prod-postgres17", "family": "postgres17", "tags_all": _etiquetas("x"),
            "parameter": [{"name": n, "value": val, "apply_method": m} for n, val, m in sorted(PARAMETROS)],
        },
        "module.base_de_datos.aws_cloudwatch_log_group.postgresql": {
            "name": "/aws/rds/instance/blog-prod-postgres/postgresql", "retention_in_days": 14,
            "tags_all": _etiquetas("x"),
        },
        "module.base_de_datos.aws_db_instance.this": {
            **INSTANCIA, "password": None, "password_wo": None, "tags_all": _etiquetas("blog-prod-postgres"),
        },
        "module.base_de_datos.aws_ssm_parameter.contrasena_master": {
            "name": "/blog-prod/datos/blogadmin", "type": "SecureString", "tier": "Standard",
            "key_id": "alias/aws/ssm", "value_wo": None, "value_wo_version": 1, "tags_all": _etiquetas("x"),
        },
    }
    for clave, subred in SUBREDES.items():
        v[f'module.red.aws_subnet.privada["{clave}"]'] = {
            "cidr_block": subred["cidr"], "availability_zone_id": subred["zona_id"],
            "map_public_ip_on_launch": False, "tags_all": _etiquetas(f"blog-prod-privada-{clave}"),
        }
        v[f'module.red.aws_route_table.privada["{clave}"]'] = {"tags_all": _etiquetas(f"blog-prod-privada-{clave}")}
        v[f'module.red.aws_route_table_association.privada["{clave}"]'] = {}
    for grupo in ("lambda", "rds", "admin"):
        v[f"module.red.aws_security_group.{grupo}"] = {"name": f"blog-prod-{grupo}", "tags_all": _etiquetas(grupo)}
    for nombre, puerto in (
        ("ingress_rule.rds_desde_lambda", 5432), ("ingress_rule.rds_desde_admin", 5432),
        ("egress_rule.lambda_a_rds", 5432), ("egress_rule.lambda_a_s3", 443), ("egress_rule.admin_a_rds", 5432),
    ):
        v[f"module.red.aws_vpc_security_group_{nombre}"] = {
            **regla, "from_port": puerto, "to_port": puerto, "tags_all": _etiquetas(nombre),
        }
    for address, after in v.items():
        after.setdefault("region", "us-east-2")
    return v


def fixture():
    valores = _valores()
    variables = {
        "region": "us-east-2", "laboratorio": False, "cuentas_permitidas": [ACCOUNT],
        "rol_operativo": "PersonalBlogAdministrator", "prefijo": "blog-prod", "arn_del_bucket_de_medios": MEDIOS,
        "proteccion_contra_borrado": True, "omitir_snapshot_final": False, "cidr_de_la_vpc": "10.40.0.0/16",
        "subredes": SUBREDES, "etiquetas": ETIQUETAS, "endpoints_aws": {"ec2": None, "rds": None},
    }
    return {
        "terraform_version": "1.16.2", "applyable": True, "complete": True, "errored": False,
        "variables": {nombre: {"value": valor} for nombre, valor in variables.items()},
        "resource_changes": [
            {"address": a, "mode": "managed", "type": TIPOS[a], "provider_name": "registry.terraform.io/hashicorp/aws",
             "change": {"actions": ["create"], "before": None, "after": valores[a]}}
            for a in sorted(ADDRESSES)
        ],
        "planned_values": {"outputs": {
            "nombre_del_parametro_master": {"value": "/blog-prod/datos/blogadmin", "sensitive": False},
            "identificador_rds": {"value": "blog-prod-postgres", "sensitive": False},
        }},
        "checks": [{"address": {"to_display": "data.aws_caller_identity.operador"}, "status": "pass"},
                   {"address": {"to_display": "var.contrasena_master"}, "status": "pass"}],
        # Estructura de `configuration` tal como la emite Terraform 1.16.2 para este root.
        "configuration": {"root_module": {"module_calls": {
            "base_de_datos": {
                "expressions": {"id_sg_rds": {"references": ["module.red.id_sg_rds", "module.red"]}},
                "module": {"resources": [{"address": "aws_db_instance.this", "expressions": {
                    "vpc_security_group_ids": {"references": ["var.id_sg_rds"]}}}]},
            },
            "red": {"module": {
                "outputs": {"id_sg_rds": {"expression": {"references": ["aws_security_group.rds.id", "aws_security_group.rds"]}}},
                "resources": [{"address": "aws_vpc_endpoint.s3", "expressions": {
                    "policy": {}, "route_table_ids": {}, "service_name": {}, "tags": {},
                    "vpc_endpoint_type": {}, "vpc_id": {}}}],
            }},
        }}},
    }


def recurso(plan, address):
    return next(r for r in plan["resource_changes"] if r["address"] == address)


def despues(plan, address):
    return recurso(plan, address)["change"]["after"]


INSTANCIA_RDS = "module.base_de_datos.aws_db_instance.this"


class PlanDeDatosTests(unittest.TestCase):
    def rechaza(self, plan, codigo):
        with self.assertRaisesRegex(ValueError, codigo):
            check(plan, ACCOUNT, MEDIOS)

    def test_wiring_no_admite_referencias_adicionales(self):
        for origen in ("entrada", "salida"):
            with self.subTest(origen=origen):
                plan = fixture()
                modulos = plan["configuration"]["root_module"]["module_calls"]
                expresion = (modulos["base_de_datos"]["expressions"]["id_sg_rds"]
                             if origen == "entrada" else
                             modulos["red"]["module"]["outputs"]["id_sg_rds"]["expression"])
                expresion["references"].append("var.grupo_ajeno")
                self.rechaza(plan, "DB_SG_WIRING")

    def test_plan_esperado(self):
        resultado = check(fixture(), ACCOUNT, MEDIOS)
        self.assertEqual((resultado["add"], resultado["change"], resultado["destroy"]), (21, 0, 0))

    def test_cualquier_accion_distinta_de_create_rechazada(self):
        for actions in (["delete"], ["delete", "create"], ["create", "delete"], ["update"], ["no-op"]):
            with self.subTest(actions=actions):
                plan = fixture(); recurso(plan, INSTANCIA_RDS)["change"]["actions"] = actions
                self.rechaza(plan, "NOT_CREATE_ONLY")

    def test_recurso_excluido_rechazado(self):
        for address, tipo in (
            ("module.red.aws_internet_gateway.this", "aws_internet_gateway"),
            ("module.red.aws_nat_gateway.this", "aws_nat_gateway"),
            ("module.red.aws_eip.this", "aws_eip"),
            ("module.base_de_datos.aws_db_proxy.this", "aws_db_proxy"),
            ("module.base_de_datos.aws_kms_key.this", "aws_kms_key"),
            ("module.ejecutora.aws_iam_role.this", "aws_iam_role"),
            ("module.computo.aws_lambda_function.backend", "aws_lambda_function"),
        ):
            with self.subTest(address=address):
                plan = fixture(); extra = copy.deepcopy(recurso(plan, INSTANCIA_RDS))
                extra.update(address=address, type=tipo)
                plan["resource_changes"].append(extra)
                self.rechaza(plan, "UNEXPECTED_RESOURCE")

    def test_falta_un_recurso_rechazado(self):
        plan = fixture(); plan["resource_changes"].pop()
        self.rechaza(plan, "RESOURCE_SET")

    def test_import_o_move_rechazados(self):
        plan = fixture(); recurso(plan, INSTANCIA_RDS)["change"]["importing"] = {"id": "existente"}
        self.rechaza(plan, "IMPORT_OR_MOVE")
        plan = fixture(); recurso(plan, INSTANCIA_RDS)["previous_address"] = "otro"
        self.rechaza(plan, "IMPORT_OR_MOVE")

    def test_drift_o_diferido_rechazado(self):
        for clave in ("resource_drift", "deferred_changes"):
            with self.subTest(clave=clave):
                plan = fixture(); plan[clave] = [{"address": "x"}]
                self.rechaza(plan, "DRIFT_OR_DEFERRED")

    def test_el_drift_que_tolera_el_laboratorio_se_rechaza_en_produccion(self):
        # H-031-1A: el laboratorio acepta `domain_dns_ips: null -> []` en
        # resource_drift (normalizacion del SDKv2, no del emulador). En AWS real
        # no se tolera: el gate exige resource_drift vacio y se aplica DN-2.
        plan = fixture()
        plan["resource_drift"] = [{
            "address": INSTANCIA_RDS, "mode": "managed", "type": "aws_db_instance",
            "change": {"actions": ["update"],
                       "before": {"domain_dns_ips": None}, "after": {"domain_dns_ips": []}},
        }]
        self.rechaza(plan, "DRIFT_OR_DEFERRED")

    def test_la_efimera_en_variables_es_una_fuga(self):
        plan = fixture(); plan["variables"]["contrasena_master"] = {"value": "x"}
        self.rechaza(plan, "EPHEMERAL_LEAK")

    def test_secreto_en_los_atributos_rechazado(self):
        for address, atributo in (
            (INSTANCIA_RDS, "password"),
            (INSTANCIA_RDS, "password_wo"),
            ("module.base_de_datos.aws_ssm_parameter.contrasena_master", "value_wo"),
            ("module.base_de_datos.aws_ssm_parameter.contrasena_master", "value"),
            ("module.base_de_datos.aws_ssm_parameter.contrasena_master", "insecure_value"),
        ):
            with self.subTest(atributo=atributo):
                plan = fixture(); despues(plan, address)[atributo] = "no-deberia-estar"
                self.rechaza(plan, "SECRET_IN_PLAN")

    def test_identidad_o_checks_fallidos_rechazados(self):
        plan = fixture(); plan["checks"][0]["status"] = "fail"
        self.rechaza(plan, "IDENTITY_CHECK")
        plan = fixture(); plan["checks"][1]["status"] = "fail"
        self.rechaza(plan, "CHECKS")

    def test_destino_equivocado_rechazado(self):
        for nombre, valor, codigo in (
            ("region", "us-east-1", "REGION"),
            ("laboratorio", True, "LAB_FLAG"),
            ("cuentas_permitidas", ["999999999999"], "ACCOUNT"),
            ("prefijo", "blog-lab", "PREFIX"),
            ("arn_del_bucket_de_medios", "arn:aws:s3:::otro", "MEDIA_CONTRACT"),
        ):
            with self.subTest(variable=nombre):
                plan = fixture(); plan["variables"][nombre] = {"value": valor}
                self.rechaza(plan, codigo)

    def test_rol_operativo_exacto(self):
        # Decision operacional del usuario (Task/031 §24): UNA identidad exacta.
        self.assertEqual(check(fixture(), ACCOUNT, MEDIOS)["add"], 21)
        for valor in ("PersonalBlogDataOperator", "OtroRol", "PersonalBlogAdministratorX", "",
                      None, ["PersonalBlogAdministrator", "PersonalBlogDataOperator"]):
            with self.subTest(rol=valor):
                plan = fixture(); plan["variables"]["rol_operativo"] = {"value": valor}
                self.rechaza(plan, "OPERATOR_ROLE")

    def test_endpoint_alternativo_rechazado(self):
        plan = fixture(); plan["variables"]["endpoints_aws"] = {"value": {"ec2": "http://127.0.0.1:4566"}}
        self.rechaza(plan, "ALTERNATE_ENDPOINT")

    def test_cidr_abierto_en_cualquier_atributo_rechazado(self):
        for address, atributo, valor in (
            ("module.red.aws_vpc_security_group_egress_rule.lambda_a_s3", "cidr_ipv4", "0.0.0.0/0"),
            ('module.red.aws_route_table.privada["a"]', "route", [{"cidr_block": "0.0.0.0/0"}]),
            ("module.red.aws_security_group.rds", "egress", [{"ipv6_cidr_blocks": ["::/0"]}]),
        ):
            with self.subTest(address=address):
                plan = fixture(); despues(plan, address)[atributo] = valor
                self.rechaza(plan, "OPEN_CIDR")

    def test_rds_publica_o_debilitada_rechazada(self):
        for atributo, valor in (
            ("publicly_accessible", True), ("storage_encrypted", False), ("deletion_protection", False),
            ("skip_final_snapshot", True), ("multi_az", True), ("instance_class", "db.t4g.small"),
            ("engine_version", "18.6"), ("iam_database_authentication_enabled", True),
            ("performance_insights_enabled", True), ("monitoring_interval", 60),
            ("backup_retention_period", 0), ("ca_cert_identifier", "rds-ca-ecc384-g1"),
            ("engine_lifecycle_support", "open-source-rds-extended-support"),
            ("delete_automated_backups", True), ("allow_major_version_upgrade", True),
        ):
            with self.subTest(atributo=atributo):
                plan = fixture(); despues(plan, INSTANCIA_RDS)[atributo] = valor
                self.rechaza(plan, f"DB_{atributo.upper()}")

    def test_clave_propia_o_secrets_manager_rechazados(self):
        plan = fixture(); despues(plan, INSTANCIA_RDS)["kms_key_id"] = "arn:aws:kms:us-east-2:1:key/x"
        self.rechaza(plan, "DB_CUSTOMER_KEY")
        plan = fixture(); despues(plan, INSTANCIA_RDS)["manage_master_user_password"] = True
        self.rechaza(plan, "DB_SECRETS_MANAGER")

    def test_tls_relajado_rechazado(self):
        plan = fixture()
        grupo = despues(plan, "module.base_de_datos.aws_db_parameter_group.this")
        grupo["parameter"] = [p for p in grupo["parameter"] if p["name"] != "rds.force_ssl"] + [
            {"name": "rds.force_ssl", "value": "0", "apply_method": "immediate"}]
        self.rechaza(plan, "PARAMETERS")

    def test_regresion_h0313_superuser_reserved_connections_no_se_gestiona(self):
        # H-031-3 (§27.4): IsModifiable=false en postgres17; su valor efectivo, 3, es el de sistema.
        plan = fixture()
        grupo = despues(plan, "module.base_de_datos.aws_db_parameter_group.this")
        self.assertEqual(len(grupo["parameter"]), 4)
        grupo["parameter"].append(
            {"name": "superuser_reserved_connections", "value": "3", "apply_method": "pending-reboot"})
        self.rechaza(plan, "PARAMETERS")

    def test_regresion_recovery2_parametros_de_sistema_no_se_gestionan(self):
        # H-031-3-RECOVERY-2 (§33): AWS los representa como Source=system / pending-reboot.
        for nombre, valor in (("rds.force_ssl", "1"), ("ssl_min_protocol_version", "TLSv1.2")):
            with self.subTest(nombre=nombre):
                plan = fixture()
                despues(plan, "module.base_de_datos.aws_db_parameter_group.this")["parameter"].append(
                    {"name": nombre, "value": valor, "apply_method": "immediate"})
                self.rechaza(plan, "PARAMETERS")

    def test_endpoint_de_interfaz_o_politica_amplia_rechazados(self):
        plan = fixture(); despues(plan, "module.red.aws_vpc_endpoint.s3")["vpc_endpoint_type"] = "Interface"
        self.rechaza(plan, "ENDPOINT_TYPE")
        plan = fixture()
        amplia = politica_del_endpoint(MEDIOS); amplia["Statement"][0]["Resource"] = ["*"]
        despues(plan, "module.red.aws_vpc_endpoint.s3")["policy"] = json.dumps(amplia)
        self.rechaza(plan, "ENDPOINT_POLICY")

    def test_subred_publica_o_en_otra_zona_rechazada(self):
        plan = fixture(); despues(plan, 'module.red.aws_subnet.privada["a"]')["map_public_ip_on_launch"] = True
        self.rechaza(plan, "PUBLIC_IP")
        plan = fixture(); despues(plan, 'module.red.aws_subnet.privada["b"]')["availability_zone_id"] = "use2-az3"
        self.rechaza(plan, "SUBNET_ZONE")

    def test_retencion_de_logs_distinta_rechazada(self):
        plan = fixture(); despues(plan, "module.base_de_datos.aws_cloudwatch_log_group.postgresql")["retention_in_days"] = 0
        self.rechaza(plan, "LOG_RETENTION")

    def test_regla_con_cidr_o_puerto_ajeno_rechazada(self):
        plan = fixture(); despues(plan, "module.red.aws_vpc_security_group_ingress_rule.rds_desde_lambda")["cidr_ipv4"] = "10.40.0.0/16"
        self.rechaza(plan, "RULE_CIDR")
        plan = fixture(); despues(plan, "module.red.aws_vpc_security_group_egress_rule.admin_a_rds")["to_port"] = 5433
        self.rechaza(plan, "RULE_PORT")

    def test_etiquetas_incompletas_rechazadas(self):
        plan = fixture(); despues(plan, "module.red.aws_vpc.this")["tags_all"].pop("Componente")
        self.rechaza(plan, "TAGS")

    def test_salida_sensible_rechazada(self):
        plan = fixture(); plan["planned_values"]["outputs"]["identificador_rds"]["sensitive"] = True
        self.rechaza(plan, "SENSITIVE_OUTPUT")

    def test_el_grupo_por_omision_no_se_gestiona(self):
        """H-031-1A: volver a gestionarlo exige permisos sobre un recurso no propio."""
        plan = fixture(); extra = copy.deepcopy(recurso(plan, INSTANCIA_RDS))
        extra.update(address="module.red.aws_default_security_group.this", type="aws_default_security_group")
        plan["resource_changes"].append(extra)
        self.rechaza(plan, "UNEXPECTED_RESOURCE")

    def test_ninguna_expresion_usa_el_grupo_por_omision(self):
        plan = fixture()
        llamada = plan["configuration"]["root_module"]["module_calls"]["base_de_datos"]
        llamada["module"]["resources"][0]["expressions"]["vpc_security_group_ids"] = {
            "references": ["module.red.aws_vpc.this.default_security_group_id"]}
        self.rechaza(plan, "DEFAULT_SG_USED")

    def test_rds_lleva_solo_sg_rds(self):
        for referencias in (["var.id_sg_rds", "var.otro_grupo"], ["var.otro_grupo"]):
            with self.subTest(referencias=referencias):
                plan = fixture()
                llamada = plan["configuration"]["root_module"]["module_calls"]["base_de_datos"]
                llamada["module"]["resources"][0]["expressions"]["vpc_security_group_ids"] = {"references": referencias}
                self.rechaza(plan, "DB_SG_WIRING")
        plan = fixture()
        red = plan["configuration"]["root_module"]["module_calls"]["red"]["module"]
        red["outputs"]["id_sg_rds"]["expression"]["references"] = ["aws_security_group.lambda.id"]
        self.rechaza(plan, "DB_SG_WIRING")

    def test_el_gateway_endpoint_no_declara_grupos(self):
        plan = fixture()
        red = plan["configuration"]["root_module"]["module_calls"]["red"]["module"]
        red["resources"][0]["expressions"]["security_group_ids"] = {"references": ["aws_security_group.lambda.id"]}
        self.rechaza(plan, "ENDPOINT_SG")

    def test_otra_version_de_terraform_rechazada(self):
        plan = fixture(); plan["terraform_version"] = "1.17.0"
        self.rechaza(plan, "VERSION")


if __name__ == "__main__":
    unittest.main()
