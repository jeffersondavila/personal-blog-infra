"""Gate offline del plan RECOVERY-3-FREE de H-031-3. Lee el plan JSON PRIVADO; nunca llama a AWS ni aplica.

Por que es una guarda aparte
----------------------------
Tras el recovery apply fallido de §32 el parameter group ya fue reemplazado y nada esta `tainted`; la
instancia no existe porque la cuenta, en plan FREE, rechazo la retencion de 7 dias. El usuario decidio
mantener FREE con una EXCEPCION TEMPORAL de 1 dia (Task/031 §34). `check_plan.py` (primer despliegue,
retencion objetivo 7) y `check_plan_recuperacion.py` (reemplazo por taint) no se tocan. Esta guarda,
escrita para la forma REAL observada, admite UNICAMENTE:

- `create` de `module.base_de_datos.aws_db_instance.this` con el contrato de D-22/D-23/D-10 salvo
  `backup_retention_period = 1`, en la zona de `use2-az1`, con `sg-rds` y `password_wo_version = 1`;
- `update` EN SITIO de `module.base_de_datos.aws_db_parameter_group.this` que solo toca `parameter`:
  queda exactamente con los cuatro explicitos y sale del conjunto la representacion de `rds.force_ssl`
  y `ssl_min_protocol_version` con sus valores de sistema (invariantes que Terraform ya no gestiona);
- `no-op` con `before == after` en los otros 19 recursos, SecureString incluido;
- ningun destroy, replace, import, move, recurso ajeno (IAM, NAT, IGW...) ni CIDR abierto.

`deferred_changes` es fail-closed. De `resource_drift` se admite SOLO la excepcion exacta autorizada en
H-031-3-RECOVERY-3-FREE-DRIFT (§35): una entrada, el parameter group, `update`, solo `parameter`, y solo
`rds.force_ssl` (1) y `ssl_min_protocol_version` (TLSv1.2) de `immediate` a `pending-reboot`; cualquier
otra forma es `DRIFT_EXCEPTION`. Ambos se comprueban AL FINAL, a proposito: si rechazan, todo lo
anterior cumple. La excepcion no prueba que no sea recurrente: lo exige la convergencia tras el apply.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.terraform_datos.check_plan import (
    ABIERTOS,
    ADDRESSES,
    BASE,
    ETIQUETAS,
    INSTANCIA,
    PARAMETROS,
    PARAMETROS_DE_SISTEMA,
    PREFIJO,
    PROVIDER,
    REGION,
    RETENCION_PLAN_FREE,
    TIPOS,
    _sin_grupo_por_omision,
    _variables,
    require,
)
from scripts.terraform_datos.check_plan_recuperacion import (
    EXISTENTES,
    GRUPO,
    INSTANCIA_RDS,
    SALIDAS_DE_RDS,
    SG_RDS,
    SIN_CAMBIOS,
    SSM,
    SUBRED_A,
    ZONA,
    _estado_previo,
)

#: Los dos invariantes de sistema que salen de la representacion del grupo en este plan.
RETIRADOS = {n: v for n, v in PARAMETROS_DE_SISTEMA.items() if n != "superuser_reserved_connections"}


def _conjunto(parametros):
    return {(p["name"], p["value"], p["apply_method"]) for p in parametros}


def check(plan, account, arn_de_medios):
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True and plan.get("complete") is True and not plan.get("errored"), "INCOMPLETE")
    _variables(plan, account, arn_de_medios)
    require(plan["variables"].get("version_de_la_contrasena", {}).get("value") == 1, "PASSWORD_VERSION")
    require(plan["variables"].get("dias_de_retencion_de_backups", {}).get("value") == RETENCION_PLAN_FREE, "RETENTION")

    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.operador") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")

    previos = _estado_previo(plan)
    require(set(previos) == EXISTENTES and not any(r.get("tainted") for r in previos.values()), "PRIOR_STATE")

    items = {}
    for item in plan.get("resource_changes", []):
        change = item["change"]
        require(not change.get("importing") and not item.get("previous_address"), "IMPORT_OR_MOVE")
        require(item.get("mode") == "managed", "DATA_SOURCE_DEFERRED")
        require(item["address"] in ADDRESSES and item["address"] not in items, "UNEXPECTED_RESOURCE")
        require(item["type"] == TIPOS[item["address"]], "UNEXPECTED_RESOURCE")
        require(item["provider_name"] == PROVIDER, "PROVIDER")
        items[item["address"]] = item
    require(set(items) == ADDRESSES, "RESOURCE_SET")

    ssm = items[SSM]["change"]
    require(ssm["actions"] == ["no-op"] and ssm["before"] == ssm["after"]
            and ssm["after"].get("value_wo_version") == 1, "SSM_CHANGED")
    for address in SIN_CAMBIOS - {SSM}:
        change = items[address]["change"]
        require(change["actions"] == ["no-op"] and change["before"] == change["after"], "EXISTING_CHANGED")

    grupo = items[GRUPO]
    require(grupo["change"]["actions"] == ["update"] and not grupo.get("action_reason"), "GROUP_UPDATE_ONLY")
    antes, despues = grupo["change"]["before"], grupo["change"]["after"]
    distintos = {k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k)}
    require(distintos <= {"parameter"}, "ONLY_PARAMETER")
    require(not any(v is True for v in (grupo["change"].get("after_unknown") or {}).values()), "ONLY_PARAMETER")
    require(despues["name"] == f"{BASE}17" == antes["name"] and despues["family"] == "postgres17", "PARAMETERS")
    require(_conjunto(despues["parameter"]) == PARAMETROS, "PARAMETERS")
    retirados = _conjunto(antes["parameter"]) - PARAMETROS
    require(PARAMETROS <= _conjunto(antes["parameter"]), "PARAMETER_TRANSITION")
    require({n for n, _v, _m in retirados} == set(RETIRADOS)
            and all(v == RETIRADOS[n] for n, v, _m in retirados), "PARAMETER_TRANSITION")

    instancia_item = items[INSTANCIA_RDS]
    require(instancia_item["change"]["actions"] == ["create"] and instancia_item["change"]["before"] is None,
            "NOT_CREATE")
    instancia = instancia_item["change"]["after"]
    for atributo, esperado in {**INSTANCIA, "backup_retention_period": RETENCION_PLAN_FREE}.items():
        require(instancia.get(atributo) == esperado, f"DB_{atributo.upper()}")
    require(not instancia.get("kms_key_id"), "DB_CUSTOMER_KEY")
    require(not instancia.get("manage_master_user_password"), "DB_SECRETS_MANAGER")
    require(instancia.get("password") is None and instancia.get("password_wo") is None, "SECRET_IN_PLAN")
    subred_a = previos[SUBRED_A]["values"]
    require(subred_a.get("availability_zone_id") == ZONA["id"] and subred_a.get("availability_zone") == ZONA["nombre"]
            and instancia.get("availability_zone") == ZONA["nombre"], "DB_AZ")
    require(instancia.get("vpc_security_group_ids") == [previos[SG_RDS]["values"]["id"]], "DB_SG")

    cambiados = {GRUPO: despues, INSTANCIA_RDS: instancia}
    require(not any(abierto in json.dumps(cambiados, sort_keys=True) for abierto in ABIERTOS), "OPEN_CIDR")
    for valores in cambiados.values():
        tags = valores.get("tags_all") or {}
        require(all(tags.get(k) == v for k, v in ETIQUETAS.items()), "TAGS")
        require(valores.get("region") == REGION, "REGION")
    _sin_grupo_por_omision(plan)

    previas = plan["prior_state"]["values"].get("outputs", {})
    salidas = plan.get("output_changes", {})
    require(set(salidas) == set(plan["configuration"]["root_module"].get("outputs", {})), "OUTPUTS")
    for nombre, dato in salidas.items():
        if nombre in SALIDAS_DE_RDS:
            require(dato["actions"] in (["create"], ["update"], ["no-op"]), "OUTPUTS")
        elif nombre in previas:
            require(dato["actions"] == ["no-op"] and dato.get("before") == dato.get("after"), "OUTPUTS")
        else:
            require(dato["actions"] == ["create"], "OUTPUTS")
    valores = plan.get("planned_values", {}).get("outputs", {})
    require(valores.get("nombre_del_parametro_master", {}).get("value") == f"/{PREFIJO}/datos/blogadmin", "OUTPUTS")
    require(valores.get("identificador_rds", {}).get("value") == BASE, "OUTPUTS")
    require(not any(dato.get("sensitive") for dato in valores.values()), "SENSITIVE_OUTPUT")

    # Ultimos controles, a proposito (DN-2): diferidos fail-closed; y del drift, SOLO la excepcion exacta.
    require(not plan.get("deferred_changes"), "DRIFT_OR_DEFERRED")
    _excepcion_de_drift(plan, antes, previos[GRUPO]["values"])

    return {"add": 1, "change": 1, "destroy": 0, "create": [INSTANCIA_RDS], "update": [GRUPO],
            "no_op": sorted(SIN_CAMBIOS), "backup_retention_period": RETENCION_PLAN_FREE,
            "parametros": len(PARAMETROS), "retirados_de_la_representacion": sorted(RETIRADOS),
            "resource_drift_admitido": [GRUPO], "drift_parametros": sorted(RETIRADOS)}


def _excepcion_de_drift(plan, refrescado, previo):
    """H-031-3-RECOVERY-3-FREE-DRIFT (§35): la UNICA entrada de `resource_drift` admitida.

    El state conserva `rds.force_ssl` y `ssl_min_protocol_version` (apply de §32) y AWS los devuelve como
    valores de sistema con `pending-reboot`. Se admite EXACTAMENTE esa representacion: una entrada, el
    parameter group, `update`, solo `parameter`, y solo esos dos pasan de `immediate` a `pending-reboot`
    con sus valores. Su `after` debe ser el state refrescado del plan (el `before` del cambio y el
    `prior_state`). NO demuestra que no sea recurrente: eso es la convergencia posterior al apply.
    """
    deriva = plan.get("resource_drift") or []
    require(len(deriva) == 1, "DRIFT_EXCEPTION")
    entrada = deriva[0]
    require(entrada.get("address") == GRUPO and entrada.get("type") == "aws_db_parameter_group"
            and entrada.get("mode") == "managed" and entrada.get("provider_name") == PROVIDER
            and not entrada.get("previous_address"), "DRIFT_EXCEPTION")
    cambio = entrada["change"]
    require(cambio.get("actions") == ["update"] and not cambio.get("importing"), "DRIFT_EXCEPTION")
    require(not any(v is True for v in (cambio.get("after_unknown") or {}).values()), "DRIFT_EXCEPTION")
    antes, despues = cambio.get("before") or {}, cambio.get("after") or {}
    require({k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k)} == {"parameter"}, "DRIFT_EXCEPTION")
    require(despues == refrescado == previo, "DRIFT_EXCEPTION")

    def mapa(parametros):
        salida = {p["name"]: (p["value"], p["apply_method"]) for p in parametros}
        require(len(salida) == len(parametros), "DRIFT_EXCEPTION")
        return salida

    viejo, nuevo = mapa(antes["parameter"]), mapa(despues["parameter"])
    nombres = {n for n, _v, _m in PARAMETROS} | set(RETIRADOS)
    require(set(viejo) == set(nuevo) == nombres, "DRIFT_EXCEPTION")
    require({n for n in viejo if viejo[n] != nuevo[n]} == set(RETIRADOS), "DRIFT_EXCEPTION")
    for nombre, valor in RETIRADOS.items():
        require(viejo[nombre] == (valor, "immediate") and nuevo[nombre] == (valor, "pending-reboot"), "DRIFT_EXCEPTION")


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
        raise SystemExit(f"H-031-3-RECOVERY-3-FREE: plan rejected ({codigo}); inspect privately. No apply authorized.") from None
    print(json.dumps({"gate": "RECOVERY_3_FREE_PLAN_OK", "json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
