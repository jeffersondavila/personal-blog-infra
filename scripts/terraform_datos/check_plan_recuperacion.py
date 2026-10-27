"""Gate offline del plan de RECUPERACION de H-031-3. Lee el plan JSON PRIVADO; nunca llama a AWS ni aplica.

Por que es una guarda aparte
----------------------------
`check_plan.py` conserva su proposito: el primer despliegue, solo `create`, de 21 recursos
desde un state vacio. El apply de H-031-3 (§27.4) fallo despues de crear 20 de ellos: el
parameter group quedo `tainted` porque `superuser_reserved_connections` no es modificable
en RDS, y la instancia nunca se creo. Esta guarda no ablanda aquella; admite UNICAMENTE:

- reemplazar `module.base_de_datos.aws_db_parameter_group.this`, y solo por estar
  `tainted`, borrando antes de crear (tiene nombre fijo) y con los parametros
  explicitos vigentes de D-22 (`check_plan.PARAMETROS`);
- crear `module.base_de_datos.aws_db_instance.this` con el contrato de D-22, D-23 y D-10,
  en la zona de `use2-az1`, con `sg-rds` y `password_wo_version = 1`;
- `no-op` con `before == after` para los otros 19 recursos, SecureString incluido: la
  contrasena que ya custodia se reutiliza y `version_de_la_contrasena` sigue en 1.

`resource_drift` y `deferred_changes` son fail-closed: si aparecen, es una revision DN-2.

Lo que NO demuestra: que AWS acepte la configuracion ni que el valor del SecureString sea el
que recibira RDS. Lo primero lo adelanta `check_parametros.py`; lo segundo es el runner.
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
    PREFIJO,
    PROVIDER,
    REGION,
    TIPOS,
    _sin_grupo_por_omision,
    _variables,
    require,
)

GRUPO = "module.base_de_datos.aws_db_parameter_group.this"
INSTANCIA_RDS = "module.base_de_datos.aws_db_instance.this"
SSM = "module.base_de_datos.aws_ssm_parameter.contrasena_master"
SUBRED_A = 'module.red.aws_subnet.privada["a"]'
SG_RDS = "module.red.aws_security_group.rds"
EXISTENTES = ADDRESSES - {INSTANCIA_RDS}
SIN_CAMBIOS = EXISTENTES - {GRUPO}
ZONA = {"id": "use2-az1", "nombre": "us-east-2a"}
#: Salidas raiz que dependen de la instancia: son las unicas que pueden crearse o cambiar.
SALIDAS_DE_RDS = frozenset({"endpoint_rds", "puerto_rds", "nombre_de_base", "identificador_rds", "arn_rds",
                            "id_de_recurso_rds"})


def _estado_previo(plan):
    """Recursos gestionados del `prior_state`, con su bandera `tainted` y sin instancias depuestas."""
    recursos = {}

    def recorrer(modulo):
        for r in modulo.get("resources", []):
            if r.get("mode") != "managed":
                continue
            require(r["address"] not in recursos and not r.get("deposed_key"), "PRIOR_STATE")
            recursos[r["address"]] = r
        for hijo in modulo.get("child_modules", []):
            recorrer(hijo)

    recorrer(plan["prior_state"]["values"]["root_module"])
    return recursos


def check(plan, account, arn_de_medios):
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True and plan.get("complete") is True and not plan.get("errored"), "INCOMPLETE")
    require(not plan.get("resource_drift") and not plan.get("deferred_changes"), "DRIFT_OR_DEFERRED")
    _variables(plan, account, arn_de_medios)
    require(plan["variables"].get("version_de_la_contrasena", {}).get("value") == 1, "PASSWORD_VERSION")

    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.operador") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")

    previos = _estado_previo(plan)
    require(set(previos) == EXISTENTES, "PRIOR_STATE")
    require({a for a, r in previos.items() if r.get("tainted")} == {GRUPO}, "PRIOR_STATE")

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
    require(ssm["actions"] == ["no-op"] and ssm["before"] == ssm["after"], "SSM_CHANGED")
    require(ssm["after"].get("value_wo_version") == 1, "SSM_CHANGED")
    for address in SIN_CAMBIOS - {SSM}:
        change = items[address]["change"]
        require(change["actions"] == ["no-op"] and change["before"] == change["after"], "EXISTING_CHANGED")

    grupo = items[GRUPO]
    require(grupo["change"]["actions"] == ["delete", "create"]
            and grupo.get("action_reason") == "replace_because_tainted", "TAINTED_REPLACE_ONLY")
    despues = grupo["change"]["after"]
    require(despues["name"] == f"{BASE}17" == grupo["change"]["before"]["name"]
            and despues["family"] == "postgres17", "PARAMETER_GROUP")
    require({(p["name"], p["value"], p["apply_method"]) for p in despues["parameter"]} == PARAMETROS, "PARAMETERS")

    instancia_item = items[INSTANCIA_RDS]
    require(instancia_item["change"]["actions"] == ["create"] and instancia_item["change"]["before"] is None,
            "NOT_CREATE")
    instancia = instancia_item["change"]["after"]
    for atributo, esperado in INSTANCIA.items():
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
            require(dato["actions"] in (["create"], ["update"]), "OUTPUTS")
        elif nombre in previas:
            require(dato["actions"] == ["no-op"] and dato.get("before") == dato.get("after"), "OUTPUTS")
        else:
            require(dato["actions"] == ["create"], "OUTPUTS")
    valores = plan.get("planned_values", {}).get("outputs", {})
    require(valores.get("nombre_del_parametro_master", {}).get("value") == f"/{PREFIJO}/datos/blogadmin", "OUTPUTS")
    require(valores.get("identificador_rds", {}).get("value") == BASE, "OUTPUTS")
    require(not any(dato.get("sensitive") for dato in valores.values()), "SENSITIVE_OUTPUT")

    return {"add": 2, "change": 0, "destroy": 1, "replace": [GRUPO], "create": [INSTANCIA_RDS],
            "no_op": sorted(SIN_CAMBIOS), "parametros": len(PARAMETROS), "zona": ZONA["nombre"],
            "password_version": 1}


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
        raise SystemExit(f"H-031-3-RECOVERY: plan rejected ({codigo}); inspect privately. No apply authorized.") from None
    print(json.dumps({"gate": "RECOVERY_PLAN_OK", "json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
