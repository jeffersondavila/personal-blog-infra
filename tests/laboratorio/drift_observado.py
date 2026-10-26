"""Segundo plan del root de datos tal como lo emitio el laboratorio en H-031-1A.

Reproduce la ESTRUCTURA del JSON real que Terraform 1.16.2 y el provider AWS
6.64.0 emitieron contra Floci 2.1.0 con RDS en modo `mock`: las cinco entradas
de `resource_drift`, las reglas gestionadas aparte que viven en `prior_state` y
las diferencias de `resource_changes` ya declaradas en H-031-1. Los ID son
sinteticos; no hay Account ID, contrasena ni valor del emulador que dependa de
una ejecucion concreta.

Actualizado con el segundo plan del ciclo del 2026-10-24 contra Floci 2.3.0
(Terraform 1.16.7, provider 6.70.0; mantenimiento de CI de Task/031): el
emulador ya devuelve `enabled_cloudwatch_logs_exports`,
`engine_lifecycle_support`, `max_allocated_storage` y el `KeyId`/`Tier` de SSM,
y `latest_restorable_time` avanza como en AWS.

No es un archivo de pruebas: `unittest discover -p 'test_*.py'` no lo recoge.
Lo comparten las regresiones que necesitan el mismo plan.
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any

SG_ADMIN = "sg-0a0a0a0a0a0a0a0a0"
SG_LAMBDA = "sg-0b1b1b1b1b1b1b1b1"
SG_RDS = "sg-0c2c2c2c2c2c2c2c2"
LISTA_DE_PREFIJOS_S3 = "pl-0000aaaa"

#: Instante en que el laboratorio evaluo el segundo plan (Floci 2.3.0, 2026-10-24).
#: `latest_restorable_time` avanza, y su contrato (`instante_movil`) se mide
#: contra este `ahora`, igual que la convergencia productiva.
AHORA = datetime(2026, 10, 24, 4, 27, 5, tzinfo=timezone.utc)

INSTANCIA = "module.base_de_datos.aws_db_instance.this"
GRUPO_DE_PARAMETROS = "module.base_de_datos.aws_db_parameter_group.this"
PARAMETRO_SSM = "module.base_de_datos.aws_ssm_parameter.contrasena_master"
GRUPO_ADMIN = "module.red.aws_security_group.admin"
GRUPO_LAMBDA = "module.red.aws_security_group.lambda"
GRUPO_RDS = "module.red.aws_security_group.rds"

#: La salida 0.0.0.0/0 que AWS crea en todo grupo nuevo. Floci 2.1.0 no aplica
#: `RevokeSecurityGroupEgress`, asi que sigue en el state antes Y despues del
#: refresh (aws-local-parity.md, fila de red). No es drift: no cambia.
SALIDA_POR_OMISION = {
    "cidr_blocks": ["0.0.0.0/0"],
    "description": "",
    "from_port": 0,
    "ipv6_cidr_blocks": [],
    "prefix_list_ids": [],
    "protocol": "-1",
    "security_groups": [],
    "self": False,
    "to_port": 0,
}

# Los cuatro parametros explicitos vigentes. La observacion original del laboratorio
# llevaba ademas `superuser_reserved_connections` (AWS no deja modificarlo, §27.4) y
# `rds.force_ssl` / `ssl_min_protocol_version` (AWS los representa como de sistema,
# §32/§33); se retiraron. Floci acepto los tres sin reproducir ninguna de esas conductas.
PARAMETROS = [
    {"apply_method": "immediate", "name": "log_connections", "value": "1"},
    {"apply_method": "immediate", "name": "log_disconnections", "value": "1"},
    {"apply_method": "immediate", "name": "log_min_duration_statement", "value": "1000"},
    {"apply_method": "immediate", "name": "log_statement", "value": "ddl"},
]


def regla_en_linea(
    descripcion: str,
    puerto: int,
    *,
    grupo: str | None = None,
    lista: str | None = None,
) -> dict[str, Any]:
    """Como `aws_security_group` representa una regla en `ingress`/`egress`."""
    return {
        "cidr_blocks": [],
        "description": descripcion,
        "from_port": puerto,
        "ipv6_cidr_blocks": [],
        "prefix_list_ids": [lista] if lista else [],
        "protocol": "tcp",
        "security_groups": [grupo] if grupo else [],
        "self": False,
        "to_port": puerto,
    }


def regla_separada(
    nombre: str,
    sentido: str,
    *,
    grupo: str,
    descripcion: str,
    puerto: int,
    referenciado: str | None = None,
    lista: str | None = None,
) -> dict[str, Any]:
    """Una `aws_vpc_security_group_{sentido}_rule` tal como aparece en `prior_state`."""
    tipo = f"aws_vpc_security_group_{sentido}_rule"
    return {
        "address": f"module.red.{tipo}.{nombre}",
        "mode": "managed",
        "type": tipo,
        "name": nombre,
        "values": {
            "cidr_ipv4": None,
            "cidr_ipv6": None,
            "description": descripcion,
            "from_port": puerto,
            "ip_protocol": "tcp",
            "prefix_list_id": lista,
            "referenced_security_group_id": referenciado,
            "security_group_id": grupo,
            "to_port": puerto,
        },
    }


REGLAS_SEPARADAS = [
    regla_separada(
        "admin_a_rds", "egress", grupo=SG_ADMIN, descripcion="PostgreSQL hacia RDS",
        puerto=5432, referenciado=SG_RDS,
    ),
    regla_separada(
        "lambda_a_rds", "egress", grupo=SG_LAMBDA, descripcion="PostgreSQL hacia RDS",
        puerto=5432, referenciado=SG_RDS,
    ),
    regla_separada(
        "lambda_a_s3", "egress", grupo=SG_LAMBDA,
        descripcion="HTTPS hacia S3 por el gateway endpoint", puerto=443,
        lista=LISTA_DE_PREFIJOS_S3,
    ),
    regla_separada(
        "rds_desde_admin", "ingress", grupo=SG_RDS,
        descripcion="PostgreSQL desde la ejecutora privada", puerto=5432, referenciado=SG_ADMIN,
    ),
    regla_separada(
        "rds_desde_lambda", "ingress", grupo=SG_RDS,
        descripcion="PostgreSQL desde la Lambda de aplicacion", puerto=5432,
        referenciado=SG_LAMBDA,
    ),
]


def _grupo(id_del_grupo: str, *, ingress: list, egress: list) -> dict[str, Any]:
    return {
        "id": id_del_grupo,
        "ingress": ingress,
        "egress": egress,
        "revoke_rules_on_delete": False,
        "tags": {"Name": id_del_grupo},
    }


def _entrada(direccion: str, tipo: str, antes: dict, despues: dict) -> dict[str, Any]:
    return {
        "address": direccion,
        "module_address": direccion.rsplit(".", 2)[0],
        "mode": "managed",
        "type": tipo,
        "name": "this",
        "change": {
            "actions": ["update"],
            "before": antes,
            "after": despues,
            "after_unknown": {},
        },
    }


def _drift_observado() -> list[dict[str, Any]]:
    instancia_comun = {
        "id": "db-SINTETICO",
        "identifier": "blog-lab-postgres",
        "domain": "",
        "domain_fqdn": "",
        "port": 7001,
        "warning_event_categories": None,
    }
    regla_admin_a_rds = regla_en_linea("PostgreSQL hacia RDS", 5432, grupo=SG_RDS)
    regla_lambda_a_s3 = regla_en_linea(
        "HTTPS hacia S3 por el gateway endpoint", 443, lista=LISTA_DE_PREFIJOS_S3
    )
    regla_lambda_a_rds = regla_en_linea("PostgreSQL hacia RDS", 5432, grupo=SG_RDS)
    return [
        _entrada(
            INSTANCIA,
            "aws_db_instance",
            {**instancia_comun, "domain_dns_ips": None,
             "enabled_cloudwatch_logs_exports": ["postgresql"],
             "latest_restorable_time": "2026-10-24T04:24:48Z"},
            {**instancia_comun, "domain_dns_ips": [],
             "enabled_cloudwatch_logs_exports": ["postgresql"],
             "latest_restorable_time": "2026-10-24T04:27:01Z"},
        ),
        _entrada(
            GRUPO_DE_PARAMETROS,
            "aws_db_parameter_group",
            {"id": "blog-lab-postgres17", "family": "postgres17", "parameter": PARAMETROS},
            {"id": "blog-lab-postgres17", "family": "postgres17", "parameter": []},
        ),
        _entrada(
            GRUPO_ADMIN,
            "aws_security_group",
            _grupo(SG_ADMIN, ingress=[], egress=[SALIDA_POR_OMISION]),
            _grupo(SG_ADMIN, ingress=[], egress=[SALIDA_POR_OMISION, regla_admin_a_rds]),
        ),
        _entrada(
            GRUPO_LAMBDA,
            "aws_security_group",
            _grupo(SG_LAMBDA, ingress=[], egress=[SALIDA_POR_OMISION]),
            _grupo(
                SG_LAMBDA, ingress=[],
                egress=[SALIDA_POR_OMISION, regla_lambda_a_s3, regla_lambda_a_rds],
            ),
        ),
        _entrada(
            GRUPO_RDS,
            "aws_security_group",
            _grupo(SG_RDS, ingress=[], egress=[SALIDA_POR_OMISION]),
            _grupo(
                SG_RDS,
                ingress=[
                    regla_en_linea(
                        "PostgreSQL desde la Lambda de aplicacion", 5432, grupo=SG_LAMBDA
                    ),
                    regla_en_linea(
                        "PostgreSQL desde la ejecutora privada", 5432, grupo=SG_ADMIN
                    ),
                ],
                egress=[SALIDA_POR_OMISION],
            ),
        ),
    ]


def _cambios_observados() -> list[dict[str, Any]]:
    """Las diferencias de `resource_changes` declaradas en H-031-1 que siguen con Floci 2.3.0."""
    return [
        _entrada(
            INSTANCIA,
            "aws_db_instance",
            {"ca_cert_identifier": "", "network_type": "", "port": 7001,
             "storage_type": "gp2", "domain_dns_ips": []},
            {"ca_cert_identifier": "rds-ca-rsa2048-g1", "network_type": "IPV4",
             "port": 5432, "storage_type": "gp3", "domain_dns_ips": []},
        ),
        _entrada(
            GRUPO_DE_PARAMETROS,
            "aws_db_parameter_group",
            {"parameter": []},
            {"parameter": PARAMETROS},
        ),
    ]


def plan_de_datos_observado() -> dict[str, Any]:
    """Copia nueva del segundo plan observado; cada prueba puede mutarla."""
    return copy.deepcopy(
        {
            "format_version": "1.2",
            "terraform_version": "1.16.7",
            "applyable": True,
            "complete": True,
            "errored": False,
            "resource_changes": _cambios_observados(),
            "resource_drift": _drift_observado(),
            "prior_state": {
                "values": {
                    "root_module": {
                        "child_modules": [
                            {"address": "module.red", "resources": REGLAS_SEPARADAS},
                        ]
                    }
                }
            },
        }
    )


def entrada(plan: dict[str, Any], direccion: str) -> dict[str, Any]:
    """La entrada de `resource_drift` con esa direccion."""
    for candidata in plan["resource_drift"]:
        if candidata["address"] == direccion:
            return candidata
    raise KeyError(direccion)
