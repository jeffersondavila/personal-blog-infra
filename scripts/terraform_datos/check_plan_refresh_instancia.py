"""Gate offline del REFRESH-ONLY de la instancia tainted con registro incompleto (Task/031 §38). Nunca aplica.

Por que es una guarda aparte
----------------------------
El apply de §36 lanzo `CreateDBInstance`, perdio las credenciales antes de la lectura posterior a la creacion y
dejo en el state (recuperado en §37) `aws_db_instance.this` `tainted` y con atributos calculados vacios. Un
refresh-only puede completarlos SIN tocar la infraestructura. Esta guarda admite UNICAMENTE la forma real
observada, contrastada contra `describe-db-instances` de la MISMA instancia (segunda entrada):

- cero `resource_changes` y cero diferidos;
- `prior_state` 21/21 con SOLO la instancia `tainted` (el refresh-only apply conserva el estado refrescado del
  plan, y con el el taint) y el parameter group con los cuatro explicitos;
- UNA entrada de `resource_drift`, la instancia, `update`, con EXACTAMENTE 36 atributos distintos: los 18 de
  `VALOR_DESDE_AWS`, de `null` al valor real, y los 18 de `FORMA_VACIA`, de `null` a su vacio exacto;
- identidad intacta e igual a AWS: identifier, base, usuario, motor y version, clase, retencion 1, AZ, subnet
  group, parameter group y solo `sg-rds`;
- salidas: `arn_rds`, `endpoint_rds` e `id_de_recurso_rds` de `null` al valor real; las demas `no-op`;
- ningun secreto en el drift ni la variable efimera en el plan.
Ninguna guarda anterior se toca.

ATRIBUTO MOVIL (H-031-3-MOVING-ATTRIBUTE, §40): `latest_restorable_time` lo hace avanzar AWS cada pocos minutos;
no es configuracion. No se compara por igualdad con un describe fresco: `instante_movil` exige instantes ISO-8601
validos y no nulos, el del plan NO posterior al de AWS, el de AWS con 24 h como maximo de antiguedad respecto al
reloj (PITR vivo; retencion productiva de 1 dia) y ninguno en el futuro, sin tolerancia porque el proyecto no tiene
convencion de clock skew. Los otros 17 valores, las 18 formas y la identidad siguen exigiendo igualdad exacta. Sin
`ignore_changes`.

ENMIENDA del 2026-10-18 (aprobada por el usuario el 2026-10-19; reporte de Task/031 §49 y §49.15): hasta entonces las 24 h
median la diferencia entre el valor del state y el de AWS, es decir, la ANTIGUEDAD DEL STATE, que no es una
propiedad de seguridad: un state sano pero sin escribir durante dias bloqueaba cualquier plan (§47). Ahora miden la
FRESCURA del valor de AWS. Las demas condiciones no cambian, y el cambio vale para todas las guardas que importan
`instante_movil`.
"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

from scripts.terraform_datos.check_plan import ADDRESSES, BASE, PARAMETROS, PROVIDER, _variables, require
from scripts.terraform_datos.check_plan_recuperacion import GRUPO, INSTANCIA_RDS, SG_RDS, _estado_previo


#: Atributos MOVILES calculados por AWS y su ventana maxima (la retencion productiva vigente, 1 dia).
MOVILES = {"latest_restorable_time"}
VENTANA_MOVIL = timedelta(days=1)


def _instante(valor):
    """Instante ISO-8601 con zona; cualquier otra cosa es `MOVING_ATTRIBUTE`."""
    require(isinstance(valor, str) and valor, "MOVING_ATTRIBUTE")
    try:
        instante = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("MOVING_ATTRIBUTE") from None
    require(instante.tzinfo is not None, "MOVING_ATTRIBUTE")
    return instante


def instante_movil(anterior, posterior, ahora):
    """Contrato temporal: `anterior` <= `posterior` <= `ahora` y `ahora - posterior` <= `VENTANA_MOVIL`.

    Enmienda de §40 del 2026-10-18 (aprobada el 2026-10-19): la ventana mide la FRESCURA del valor de
    AWS (PITR vivo), ya no la antiguedad del state (`posterior - anterior`). Devuelve el avance de AWS."""
    a, b = _instante(anterior), _instante(posterior)
    require(a <= b <= ahora and ahora - b <= VENTANA_MOVIL, "MOVING_ATTRIBUTE")
    return b - a


#: Atributo calculado -> como se obtiene de `describe-db-instances` (los 18 observados, ninguno generico).
VALOR_DESDE_AWS = {
    "resource_id": lambda d: d["DbiResourceId"],
    "arn": lambda d: d["DBInstanceArn"],
    "address": lambda d: d["Endpoint"]["Address"],
    "endpoint": lambda d: f'{d["Endpoint"]["Address"]}:{d["Endpoint"]["Port"]}',
    "hosted_zone_id": lambda d: d["Endpoint"]["HostedZoneId"],
    "status": lambda d: d["DBInstanceStatus"],
    "kms_key_id": lambda d: d["KmsKeyId"],
    "engine_version_actual": lambda d: d["EngineVersion"],
    "license_model": lambda d: d["LicenseModel"],
    "option_group_name": lambda d: d["OptionGroupMemberships"][0]["OptionGroupName"],
    "iops": lambda d: d["Iops"],
    "storage_throughput": lambda d: d["StorageThroughput"],
    "performance_insights_retention_period": lambda d: d.get("PerformanceInsightsRetentionPeriod") or 0,
    "database_insights_mode": lambda d: d["DatabaseInsightsMode"],
    "backup_target": lambda d: d["BackupTarget"],
    "latest_restorable_time": lambda d: d.get("LatestRestorableTime"),  # MOVIL: ver instante_movil
    "customer_owned_ip_enabled": lambda d: d["CustomerOwnedIpEnabled"],
    "upgrade_rollout_order": lambda d: d["UpgradeRolloutOrder"],
}

#: Normalizaciones de forma del provider: `null` -> este vacio EXACTO (los 18 observados).
FORMA_VACIA = {
    "character_set_name": "", "custom_iam_instance_profile": "", "domain": "", "domain_auth_secret_arn": "",
    "domain_dns_ips": [], "domain_fqdn": "", "domain_iam_role_name": "", "domain_ou": "", "identifier_prefix": "",
    "listener_endpoint": [], "master_user_secret": [], "monitoring_role_arn": "", "nchar_character_set_name": "",
    "performance_insights_kms_key_id": "", "replica_mode": "", "replicas": [], "replicate_source_db": "", "timezone": "",
}

#: Identidad estable: atributo del state -> (como se lee en AWS, valor del contrato).
IDENTIDAD = {
    "identifier": (lambda d: d["DBInstanceIdentifier"], BASE),
    "db_name": (lambda d: d["DBName"], "personal_blog"),
    "username": (lambda d: d["MasterUsername"], "blogadmin"),
    "engine": (lambda d: d["Engine"], "postgres"),
    "engine_version": (lambda d: d["EngineVersion"], "17.11"),
    "instance_class": (lambda d: d["DBInstanceClass"], "db.t4g.micro"),
    "backup_retention_period": (lambda d: d["BackupRetentionPeriod"], 1),
    "availability_zone": (lambda d: d["AvailabilityZone"], "us-east-2a"),
    "db_subnet_group_name": (lambda d: d["DBSubnetGroup"]["DBSubnetGroupName"], BASE),
    "parameter_group_name": (lambda d: d["DBParameterGroups"][0]["DBParameterGroupName"], f"{BASE}17"),
}
SALIDAS_COMPLETADAS = {
    "arn_rds": lambda d: d["DBInstanceArn"],
    "endpoint_rds": lambda d: d["Endpoint"]["Address"],
    "id_de_recurso_rds": lambda d: d["DbiResourceId"],
}
SALIDAS_CONOCIDAS = {"identificador_rds": BASE, "nombre_de_base": "personal_blog", "puerto_rds": 5432}


def _igual(valor, esperado):
    return type(valor) is type(esperado) and valor == esperado


def check(plan, account, arn_de_medios, rds, ahora=None):
    ahora = ahora or datetime.now(timezone.utc)
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True and plan.get("complete") is True and not plan.get("errored"), "INCOMPLETE")
    require(not plan.get("resource_changes"), "RESOURCE_CHANGES")
    require(not plan.get("deferred_changes"), "DEFERRED")
    _variables(plan, account, arn_de_medios)
    require(plan["variables"].get("version_de_la_contrasena", {}).get("value") == 1, "PASSWORD_VERSION")
    require(plan["variables"].get("dias_de_retencion_de_backups", {}).get("value") == 1, "RETENTION")
    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.operador") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")

    previos = _estado_previo(plan)
    require(set(previos) == ADDRESSES, "PRIOR_STATE")
    require({a for a, r in previos.items() if r.get("tainted")} == {INSTANCIA_RDS}, "TAINT")
    require({(p["name"], p["value"], p["apply_method"]) for p in previos[GRUPO]["values"]["parameter"]} == PARAMETROS,
            "PARAMETERS")

    deriva = plan.get("resource_drift") or []
    require(len(deriva) == 1, "DRIFT_ADDRESS")
    entrada = deriva[0]
    cambio = entrada.get("change", {})
    require(entrada.get("address") == INSTANCIA_RDS and entrada.get("type") == "aws_db_instance"
            and entrada.get("mode") == "managed" and entrada.get("provider_name") == PROVIDER
            and not entrada.get("previous_address") and not cambio.get("importing")
            and cambio.get("actions") == ["update"]
            and not any(v is True for v in (cambio.get("after_unknown") or {}).values()), "DRIFT_ADDRESS")
    antes, despues = cambio["before"], cambio["after"]
    require(despues.get("password") is None and despues.get("password_wo") is None, "SECRET_IN_PLAN")

    distintos = {k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k)}
    require(distintos == set(VALOR_DESDE_AWS) | set(FORMA_VACIA), "DRIFT_ATTRIBUTES")
    for atributo, vacio in FORMA_VACIA.items():
        require(antes.get(atributo) is None and type(despues.get(atributo)) is type(vacio)
                and despues.get(atributo) == vacio, "DRIFT_SHAPE")
    delta_movil = None
    for atributo, leer in VALOR_DESDE_AWS.items():
        require(antes.get(atributo) is None, "DRIFT_VALUE")
        if atributo in MOVILES:
            delta_movil = instante_movil(despues.get(atributo), leer(rds), ahora)
        else:
            require(_igual(despues.get(atributo), leer(rds)), "DRIFT_VALUE")
    require(despues["status"] == "available", "DRIFT_VALUE")

    sg = previos[SG_RDS]["values"]["id"]
    for atributo, (leer, contrato) in IDENTIDAD.items():
        require(despues.get(atributo) == contrato == leer(rds) == antes.get(atributo), "IDENTITY")
    require(despues.get("vpc_security_group_ids") == [sg] == [x["VpcSecurityGroupId"] for x in rds["VpcSecurityGroups"]],
            "IDENTITY")
    require(previos[INSTANCIA_RDS]["values"] == despues, "DRIFT_COHERENCE")

    salidas = plan.get("output_changes", {})
    require(set(salidas) == set(plan["configuration"]["root_module"].get("outputs", {})), "OUTPUTS")
    for nombre, dato in salidas.items():
        require(dato.get("before_sensitive") is False and dato.get("after_sensitive") is False
                and dato.get("after_unknown") is not True, "OUTPUTS")
        if nombre in SALIDAS_COMPLETADAS:
            require(dato.get("actions") == ["update"] and dato.get("before") is None
                    and dato.get("after") == SALIDAS_COMPLETADAS[nombre](rds), "OUTPUTS")
        elif nombre in SALIDAS_CONOCIDAS:
            require(dato.get("actions") == ["no-op"] and dato.get("before") == dato.get("after") == SALIDAS_CONOCIDAS[nombre],
                    "OUTPUTS")
        else:
            require(dato.get("actions") == ["no-op"] and dato.get("before") == dato.get("after"), "OUTPUTS")
    valores = plan.get("planned_values", {}).get("outputs", {})
    require(not any(dato.get("sensitive") for dato in valores.values()), "SENSITIVE_OUTPUT")

    return {"resource_changes": 0, "resource_drift": [INSTANCIA_RDS], "tainted": [INSTANCIA_RDS],
            "atributos_completados": len(VALOR_DESDE_AWS), "normalizaciones_de_forma": len(FORMA_VACIA),
            "identidad": sorted(IDENTIDAD) + ["vpc_security_group_ids"], "salidas": sorted(SALIDAS_COMPLETADAS),
            "atributo_movil": {"latest_restorable_time": "MOVING_ATTRIBUTE_OK",
                               "avance_de_aws_segundos": int(delta_movil.total_seconds())}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--variables", required=True, type=Path,
                        help="JSON privado con expected_account_id y arn_del_bucket_de_medios")
    parser.add_argument("--rds", required=True, type=Path, help="salida privada de describe-db-instances")
    args = parser.parse_args()
    try:
        raw = args.plan_json.read_bytes()
        privadas = json.loads(args.variables.read_text(encoding="utf-8"))
        rds = json.loads(args.rds.read_text(encoding="utf-8"))["DBInstances"][0]
        result = check(json.loads(raw), privadas["expected_account_id"], privadas["arn_del_bucket_de_medios"], rds)
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        codigo = str(error) if isinstance(error, ValueError) and str(error).isupper() else type(error).__name__
        raise SystemExit(f"H-031-3-RECOVERY-STATE-REFRESH: plan rejected ({codigo}); inspect privately. No apply authorized.") from None
    print(json.dumps({"gate": "INSTANCE_REFRESH_PLAN_OK", "json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
