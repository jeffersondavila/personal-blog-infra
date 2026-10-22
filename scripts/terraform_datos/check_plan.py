"""Gate offline de H-031-3. Lee el plan JSON PRIVADO del root de datos; nunca llama a AWS ni aplica.

Que exige, y por que cada cosa
------------------------------
El primer apply de red y RDS solo puede crear exactamente lo que H-031-1 aprobo y
H-031-1A ajusto: 21 recursos, ninguno de mas, ninguno modificado ni destruido, ningun import ni
move, y con los valores de D-22, D-23 y D-10. Un plan que proponga otra cosa se
rechaza con un codigo corto y sin imprimir su contenido: el JSON se inspecciona
en privado, nunca en un log.

Lo que NO demuestra: que AWS acepte la configuracion, que la red aisle, que TLS
se exija ni que exista un backup restaurable. Eso es el readback de H-031-3 y las
fases siguientes.
"""
import argparse
import hashlib
import json
from pathlib import Path

PREFIJO = "blog-prod"
BASE = f"{PREFIJO}-postgres"
REGION = "us-east-2"
#: UNA identidad exacta, por decision operacional del usuario (Task/031 §24, H-031-2-ALIGN).
#: `PersonalBlogDataOperator`, creado en H-031-IAM y conservado, ya no se acepta aqui.
ROL_OPERATIVO = "PersonalBlogAdministrator"
PROVIDER = "registry.terraform.io/hashicorp/aws"

TIPOS = {
    "module.red.aws_vpc.this": "aws_vpc",
    'module.red.aws_subnet.privada["a"]': "aws_subnet",
    'module.red.aws_subnet.privada["b"]': "aws_subnet",
    'module.red.aws_route_table.privada["a"]': "aws_route_table",
    'module.red.aws_route_table.privada["b"]': "aws_route_table",
    'module.red.aws_route_table_association.privada["a"]': "aws_route_table_association",
    'module.red.aws_route_table_association.privada["b"]': "aws_route_table_association",
    "module.red.aws_vpc_endpoint.s3": "aws_vpc_endpoint",
    "module.red.aws_security_group.lambda": "aws_security_group",
    "module.red.aws_security_group.rds": "aws_security_group",
    "module.red.aws_security_group.admin": "aws_security_group",
    "module.red.aws_vpc_security_group_ingress_rule.rds_desde_lambda": "aws_vpc_security_group_ingress_rule",
    "module.red.aws_vpc_security_group_ingress_rule.rds_desde_admin": "aws_vpc_security_group_ingress_rule",
    "module.red.aws_vpc_security_group_egress_rule.lambda_a_rds": "aws_vpc_security_group_egress_rule",
    "module.red.aws_vpc_security_group_egress_rule.lambda_a_s3": "aws_vpc_security_group_egress_rule",
    "module.red.aws_vpc_security_group_egress_rule.admin_a_rds": "aws_vpc_security_group_egress_rule",
    "module.base_de_datos.aws_db_subnet_group.this": "aws_db_subnet_group",
    "module.base_de_datos.aws_db_parameter_group.this": "aws_db_parameter_group",
    "module.base_de_datos.aws_cloudwatch_log_group.postgresql": "aws_cloudwatch_log_group",
    "module.base_de_datos.aws_db_instance.this": "aws_db_instance",
    "module.base_de_datos.aws_ssm_parameter.contrasena_master": "aws_ssm_parameter",
}
ADDRESSES = frozenset(TIPOS)

ETIQUETAS = {
    "Proyecto": "personal-blog",
    "Entorno": "produccion",
    "Gestion": "terraform",
    "Componente": "datos",
    "Tarea": "Task/031",
}
SIN_ETIQUETAS = {"aws_route_table_association"}

SUBREDES = {
    "a": {"cidr": "10.40.0.0/20", "zona_id": "use2-az1"},
    "b": {"cidr": "10.40.16.0/20", "zona_id": "use2-az2"},
}

#: Los parametros EXPLICITOS del parameter group: los cuatro realmente personalizados (D-22 §3.8,
#: corregida en H-031-3-RECOVERY y RECOVERY-2). Cada uno debe ser modificable en el catalogo real:
#: lo exige `check_parametros.py` antes del plan.
PARAMETROS = {
    ("log_statement", "ddl", "immediate"),
    ("log_min_duration_statement", "1000", "immediate"),
    ("log_connections", "1", "immediate"),
    ("log_disconnections", "1", "immediate"),
}

#: INVARIANTES DE SISTEMA: valores de los que dependen la seguridad (TLS) y el presupuesto de
#: conexiones, pero que Terraform NO gestiona. `superuser_reserved_connections` no es modificable
#: (rompio el apply de H-031-3, §27.4). `rds.force_ssl` y `ssl_min_protocol_version` coinciden con
#: el valor de sistema y AWS los devuelve como `Source = system` / `pending-reboot` aunque se
#: declaren, lo que no converge (§32, §33). `check_parametros.py` exige estos valores, con
#: `Source = system`, contra el catalogo real antes de CADA plan productivo de datos.
PARAMETROS_DE_SISTEMA = {
    "superuser_reserved_connections": "3",
    "rds.force_ssl": "1",
    "ssl_min_protocol_version": "TLSv1.2",
}

#: Retencion de backups (D-10/D-22): OBJETIVO con la cuenta en plan PAID y EXCEPCION TEMPORAL
#: mientras siga en plan FREE, que rechazo 7 con FreeTierRestrictionError (Task/031 §32-§34).
RETENCION_OBJETIVO = 7
RETENCION_PLAN_FREE = 1

#: Valores exactos que la instancia debe declarar en el plan (D-22, D-23, D-10, DH-4).
INSTANCIA = {
    "identifier": BASE,
    "engine": "postgres",
    "engine_version": "17.11",
    "instance_class": "db.t4g.micro",
    "storage_type": "gp3",
    "allocated_storage": 20,
    "max_allocated_storage": 50,
    "storage_encrypted": True,
    "publicly_accessible": False,
    "multi_az": False,
    "network_type": "IPV4",
    "port": 5432,
    "ca_cert_identifier": "rds-ca-rsa2048-g1",
    "iam_database_authentication_enabled": False,
    "backup_retention_period": RETENCION_OBJETIVO,
    "backup_window": "07:00-07:30",
    "maintenance_window": "sun:08:00-sun:09:00",
    "copy_tags_to_snapshot": True,
    "delete_automated_backups": False,
    "deletion_protection": True,
    "skip_final_snapshot": False,
    "final_snapshot_identifier": f"{BASE}-final",
    "auto_minor_version_upgrade": True,
    "allow_major_version_upgrade": False,
    "apply_immediately": False,
    "performance_insights_enabled": False,
    "monitoring_interval": 0,
    "enabled_cloudwatch_logs_exports": ["postgresql"],
    "engine_lifecycle_support": "open-source-rds-extended-support-disabled",
    "username": "blogadmin",
    "db_name": "personal_blog",
    "db_subnet_group_name": BASE,
    "parameter_group_name": f"{BASE}17",
    "password_wo_version": 1,
}

ABIERTOS = ("0.0.0.0/0", "::/0")


def require(condition, code):
    if not condition:
        raise ValueError(code)


def politica_del_endpoint(arn_de_medios):
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ObjetosDeLosBucketsDelProyecto",
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                "Resource": [f"{arn_de_medios}/*"],
            },
            {
                "Sid": "ListadoDeLosBucketsDelProyecto",
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:ListBucket"],
                "Resource": [arn_de_medios],
            },
        ],
    }


def _variables(plan, account, arn_de_medios):
    variables = plan["variables"]
    # DH-2: una variable efimera nunca aparece en el plan. Si aparece, la
    # contrasena viajaria en un archivo que se guarda y se revisa.
    require("contrasena_master" not in variables, "EPHEMERAL_LEAK")
    valor = {nombre: dato.get("value") for nombre, dato in variables.items()}
    require(valor["region"] == REGION, "REGION")
    require(valor["laboratorio"] is False, "LAB_FLAG")
    require(valor["cuentas_permitidas"] == [account], "ACCOUNT")
    require(valor["rol_operativo"] == ROL_OPERATIVO, "OPERATOR_ROLE")
    require(valor["prefijo"] == PREFIJO, "PREFIX")
    require(valor["arn_del_bucket_de_medios"] == arn_de_medios, "MEDIA_CONTRACT")
    require(valor["proteccion_contra_borrado"] is True and valor["omitir_snapshot_final"] is False, "PROTECTION")
    require(valor["cidr_de_la_vpc"] == "10.40.0.0/16" and valor["subredes"] == SUBREDES, "NETWORK_LAYOUT")
    require(valor["etiquetas"] == ETIQUETAS, "TAGS")
    require(all(v is None for v in (valor.get("endpoints_aws") or {}).values()), "ALTERNATE_ENDPOINT")


def _recurso_de_configuracion(modulo, direccion):
    return next(r for r in modulo["resources"] if r["address"] == direccion)


def _sin_grupo_por_omision(plan):
    """H-031-1A: el grupo por omision de la VPC NO se gestiona y NADA lo usa.

    Se demuestra sobre la seccion `configuration` del plan, que conserva las
    referencias reales entre recursos: RDS lleva una sola referencia, la de
    `sg-rds`; el gateway endpoint no declara grupos ni subredes; y ninguna
    expresion del proyecto nombra el grupo por omision.
    """
    configuracion = plan["configuration"]
    texto = json.dumps(configuracion)
    require("default_security_group_id" not in texto and "aws_default_security_group" not in texto,
            "DEFAULT_SG_USED")
    raiz = configuracion["root_module"]
    llamada = raiz["module_calls"]["base_de_datos"]
    require(llamada["expressions"]["id_sg_rds"] == {
        "references": ["module.red.id_sg_rds", "module.red"]
    }, "DB_SG_WIRING")
    instancia = _recurso_de_configuracion(llamada["module"], "aws_db_instance.this")
    require(instancia["expressions"]["vpc_security_group_ids"]["references"] == ["var.id_sg_rds"], "DB_SG_WIRING")
    red = raiz["module_calls"]["red"]["module"]
    require(red["outputs"]["id_sg_rds"]["expression"] == {
        "references": ["aws_security_group.rds.id", "aws_security_group.rds"]
    }, "DB_SG_WIRING")
    endpoint = _recurso_de_configuracion(red, "aws_vpc_endpoint.s3")
    require(not {"security_group_ids", "subnet_ids"} & set(endpoint["expressions"]), "ENDPOINT_SG")


def check(plan, account, arn_de_medios):
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True and plan.get("complete") is True and not plan.get("errored"), "INCOMPLETE")
    require(not plan.get("resource_drift") and not plan.get("deferred_changes"), "DRIFT_OR_DEFERRED")
    _variables(plan, account, arn_de_medios)

    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.operador") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")

    resources = {}
    for item in plan.get("resource_changes", []):
        change = item["change"]
        require(not change.get("importing") and not item.get("previous_address"), "IMPORT_OR_MOVE")
        require(item.get("mode") == "managed", "DATA_SOURCE_DEFERRED")
        require(item["address"] in ADDRESSES and item["address"] not in resources, "UNEXPECTED_RESOURCE")
        require(item["type"] == TIPOS[item["address"]], "UNEXPECTED_RESOURCE")
        require(change["actions"] == ["create"] and change.get("before") is None, "NOT_CREATE_ONLY")
        require(item["provider_name"] == PROVIDER, "PROVIDER")
        resources[item["address"]] = change["after"]
    require(set(resources) == ADDRESSES, "RESOURCE_SET")

    # Ningun CIDR abierto en NINGUN atributo planificado: ni rutas ni reglas.
    texto = json.dumps(resources, sort_keys=True)
    require(not any(abierto in texto for abierto in ABIERTOS), "OPEN_CIDR")

    for address, after in resources.items():
        if TIPOS[address] in SIN_ETIQUETAS:
            continue
        tags = after.get("tags_all") or {}
        require(all(tags.get(k) == v for k, v in ETIQUETAS.items()), "TAGS")
        require(after.get("region") == REGION, "REGION")

    vpc = resources["module.red.aws_vpc.this"]
    require(vpc["cidr_block"] == "10.40.0.0/16", "VPC")
    require(vpc["enable_dns_support"] is True and vpc["enable_dns_hostnames"] is True, "VPC_DNS")
    require(vpc["assign_generated_ipv6_cidr_block"] is False, "IPV6")

    for clave, esperado in SUBREDES.items():
        subred = resources[f'module.red.aws_subnet.privada["{clave}"]']
        require(subred["cidr_block"] == esperado["cidr"], "SUBNET")
        require(subred["availability_zone_id"] == esperado["zona_id"], "SUBNET_ZONE")
        require(subred["map_public_ip_on_launch"] is False, "PUBLIC_IP")

    _sin_grupo_por_omision(plan)

    endpoint = resources["module.red.aws_vpc_endpoint.s3"]
    require(endpoint["vpc_endpoint_type"] == "Gateway", "ENDPOINT_TYPE")
    require(endpoint["service_name"] == f"com.amazonaws.{REGION}.s3", "ENDPOINT_SERVICE")
    require(json.loads(endpoint["policy"]) == politica_del_endpoint(arn_de_medios), "ENDPOINT_POLICY")

    for grupo in ("lambda", "rds", "admin"):
        require(resources[f"module.red.aws_security_group.{grupo}"]["name"] == f"{PREFIJO}-{grupo}", "SECURITY_GROUP")

    reglas = {
        "module.red.aws_vpc_security_group_ingress_rule.rds_desde_lambda": 5432,
        "module.red.aws_vpc_security_group_ingress_rule.rds_desde_admin": 5432,
        "module.red.aws_vpc_security_group_egress_rule.lambda_a_rds": 5432,
        "module.red.aws_vpc_security_group_egress_rule.lambda_a_s3": 443,
        "module.red.aws_vpc_security_group_egress_rule.admin_a_rds": 5432,
    }
    for address, puerto in reglas.items():
        regla = resources[address]
        require(regla["ip_protocol"] == "tcp" and regla["from_port"] == puerto == regla["to_port"], "RULE_PORT")
        require(regla.get("cidr_ipv4") is None and regla.get("cidr_ipv6") is None, "RULE_CIDR")

    require(resources["module.base_de_datos.aws_db_subnet_group.this"]["name"] == BASE, "SUBNET_GROUP")

    grupo = resources["module.base_de_datos.aws_db_parameter_group.this"]
    require(grupo["name"] == f"{BASE}17" and grupo["family"] == "postgres17", "PARAMETER_GROUP")
    observados = {(p["name"], p["value"], p["apply_method"]) for p in grupo["parameter"]}
    require(observados == PARAMETROS, "PARAMETERS")

    logs = resources["module.base_de_datos.aws_cloudwatch_log_group.postgresql"]
    require(logs["name"] == f"/aws/rds/instance/{BASE}/postgresql", "LOG_GROUP")
    require(logs["retention_in_days"] == 14, "LOG_RETENTION")

    instancia = resources["module.base_de_datos.aws_db_instance.this"]
    for atributo, esperado in INSTANCIA.items():
        require(instancia.get(atributo) == esperado, f"DB_{atributo.upper()}")
    require(not instancia.get("kms_key_id"), "DB_CUSTOMER_KEY")
    require(not instancia.get("manage_master_user_password"), "DB_SECRETS_MANAGER")
    require(instancia.get("password") is None and instancia.get("password_wo") is None, "SECRET_IN_PLAN")

    parametro = resources["module.base_de_datos.aws_ssm_parameter.contrasena_master"]
    require(parametro["name"] == f"/{PREFIJO}/datos/blogadmin", "SSM_NAME")
    require(parametro["type"] == "SecureString" and parametro["tier"] == "Standard", "SSM_TYPE")
    require(parametro["key_id"] == "alias/aws/ssm", "SSM_KEY")
    require(parametro.get("value_wo") is None and parametro.get("insecure_value") is None, "SECRET_IN_PLAN")
    require(parametro.get("value") in (None, ""), "SECRET_IN_PLAN")
    require(parametro.get("value_wo_version") == 1, "SSM_VERSION")

    salidas = plan.get("planned_values", {}).get("outputs", {})
    require(salidas.get("nombre_del_parametro_master", {}).get("value") == f"/{PREFIJO}/datos/blogadmin", "OUTPUTS")
    require(salidas.get("identificador_rds", {}).get("value") == BASE, "OUTPUTS")
    require(not any(dato.get("sensitive") for dato in salidas.values()), "SENSITIVE_OUTPUT")

    return {"add": len(resources), "change": 0, "destroy": 0, "addresses": sorted(resources)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--variables", required=True, type=Path,
                        help="JSON privado con expected_account_id y arn_del_bucket_de_medios")
    args = parser.parse_args()
    try:
        raw = args.plan_json.read_bytes()
        privadas = json.loads(args.variables.read_text(encoding="utf-8"))
        result = check(json.loads(raw), privadas["expected_account_id"], privadas["arn_del_bucket_de_medios"])
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        codigo = str(error) if isinstance(error, ValueError) and str(error).isupper() else type(error).__name__
        raise SystemExit(f"H-031-3: plan rejected ({codigo}); inspect privately. No apply authorized.") from None
    print(json.dumps({"gate": "PLAN_OK", "json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
