"""Gate offline del REFRESH-ONLY de DN-2 tras H-031-3. Lee el plan JSON PRIVADO; nunca llama a AWS ni aplica.

Por que es una guarda aparte
----------------------------
El plan de recuperacion (§28) trae `resource_drift` en cuatro recursos y su guarda lo rechaza,
como debe. DN-2 propone guardar esas representaciones en el state con un refresh-only. Esta
guarda admite EXACTAMENTE el contrato fijado por el usuario antes de ver el plan, y nada mas:

- `aws_security_group.admin`: `egress: [] ->` el reflejo de `admin_a_rds`;
- `aws_security_group.lambda`: `egress: [] ->` el reflejo de `lambda_a_rds` y `lambda_a_s3`;
- `aws_security_group.rds`: `ingress: [] ->` el reflejo de `rds_desde_lambda` y `rds_desde_admin`;
- `aws_db_parameter_group.this` (tainted): `name_prefix: null -> ""` y, en `rds.force_ssl` y
  `ssl_min_protocol_version`, `apply_method: immediate -> pending-reboot` SIN cambio de valor.

El reflejo de cada grupo se deriva de las CINCO reglas que el state ya gestiona aparte: ni una
regla mas, ni un CIDR, ni la salida por omision restaurada. Ademas: cero `resource_changes`
(refresh-only), cero diferidos y el taint del parameter group conservado.

Salidas: todas `no-op` con `before == after`, SALVO exactamente las seis que dependen de la
instancia, que todavia no existe (`SALIDAS_RDS`, decision del usuario en
H-031-3-RECOVERY-DN2-OUTPUTS). El refresh-only las reevalua: tres pasan de ausentes a
desconocidas (`create`) y tres de su valor conocido a desconocido (`update`). Accion, valor
previo, `after = null`, `after_unknown = true` y no sensibles se exigen exactamente.
`check_plan.py` y `check_plan_recuperacion.py` no se tocan para esto.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.terraform_datos.check_plan import ABIERTOS, PROVIDER, _variables, require
from scripts.terraform_datos.check_plan_recuperacion import EXISTENTES, GRUPO, _estado_previo

#: Direccion -> (tipo, conjunto EXACTO de atributos que pueden diferir).
DRIFT = {
    "module.red.aws_security_group.admin": ("aws_security_group", {"egress"}),
    "module.red.aws_security_group.lambda": ("aws_security_group", {"egress"}),
    "module.red.aws_security_group.rds": ("aws_security_group", {"ingress"}),
    GRUPO: ("aws_db_parameter_group", {"name_prefix", "parameter"}),
}
REGLAS = (
    "module.red.aws_vpc_security_group_ingress_rule.rds_desde_lambda",
    "module.red.aws_vpc_security_group_ingress_rule.rds_desde_admin",
    "module.red.aws_vpc_security_group_egress_rule.lambda_a_rds",
    "module.red.aws_vpc_security_group_egress_rule.lambda_a_s3",
    "module.red.aws_vpc_security_group_egress_rule.admin_a_rds",
)
ENDPOINT = "module.red.aws_vpc_endpoint.s3"
#: Los dos parametros cuyo `apply_method` devuelve AWS como `pending-reboot` (valor = el de sistema).
REPRESENTACION = {"rds.force_ssl": "1", "ssl_min_protocol_version": "TLSv1.2"}
#: H-031-3-RECOVERY-DN2-OUTPUTS (decision del usuario, §30): las seis salidas que dependen de la
#: instancia, que todavia NO existe. El refresh-only las reevalua y no puede conservar su valor.
#: Salida -> (accion EXACTA, valor previo EXACTO). `None` = ausente del state previo.
SALIDAS_RDS = {
    "arn_rds": ("create", None),
    "endpoint_rds": ("create", None),
    "id_de_recurso_rds": ("create", None),
    "identificador_rds": ("update", "blog-prod-postgres"),
    "nombre_de_base": ("update", "personal_blog"),
    "puerto_rds": ("update", 5432),
}


def _reflejo_esperado(previos):
    """(id del grupo, sentido) -> reglas en linea esperadas, derivadas de las reglas gestionadas aparte."""
    prefix_s3 = previos[ENDPOINT]["values"].get("prefix_list_id")
    esperado = {}
    for direccion in REGLAS:
        v = previos[direccion]["values"]
        require(not v.get("cidr_ipv4") and not v.get("cidr_ipv6"), "OPEN_CIDR")
        referencia, prefijo = v.get("referenced_security_group_id"), v.get("prefix_list_id")
        require(bool(referencia) != bool(prefijo), "SG_REFLECTION")
        require(not prefijo or prefijo == prefix_s3, "SG_REFLECTION")
        sentido = "ingress" if "_ingress_rule." in direccion else "egress"
        esperado.setdefault((v["security_group_id"], sentido), []).append({
            "cidr_blocks": [], "description": v.get("description"), "from_port": v["from_port"],
            "ipv6_cidr_blocks": [], "prefix_list_ids": [prefijo] if prefijo else [], "protocol": v["ip_protocol"],
            "security_groups": [referencia] if referencia else [], "self": False, "to_port": v["to_port"],
        })
    return esperado


def _ordenadas(reglas):
    return sorted(json.dumps(r, sort_keys=True) for r in reglas)


def check(plan, account, arn_de_medios):
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True and plan.get("complete") is True and not plan.get("errored"), "INCOMPLETE")
    # Refresh-only: no planifica infraestructura. Un plan normal traeria el reemplazo del grupo tainted.
    require(not plan.get("resource_changes"), "RESOURCE_CHANGES")
    require(not plan.get("deferred_changes"), "DEFERRED")
    _variables(plan, account, arn_de_medios)
    require(plan["variables"].get("version_de_la_contrasena", {}).get("value") == 1, "PASSWORD_VERSION")
    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.operador") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")

    previos = _estado_previo(plan)
    require(set(previos) == EXISTENTES, "PRIOR_STATE")
    require({a for a, r in previos.items() if r.get("tainted")} == {GRUPO}, "TAINT")
    esperado = _reflejo_esperado(previos)

    vistos = {}
    for item in plan.get("resource_drift") or []:
        direccion = item.get("address")
        require(direccion in DRIFT and direccion not in vistos, "UNEXPECTED_DRIFT")
        tipo, atributos = DRIFT[direccion]
        require(item.get("mode") == "managed" and item.get("type") == tipo
                and item.get("provider_name") == PROVIDER, "UNEXPECTED_DRIFT")
        cambio = item["change"]
        require(not cambio.get("importing") and not item.get("previous_address"), "IMPORT_OR_MOVE")
        require(cambio.get("actions") == ["update"], "ACTIONS")
        antes, despues = cambio.get("before") or {}, cambio.get("after") or {}
        distintos = {k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k)}
        require(distintos == atributos, "ONLY_EXPECTED_ATTRIBUTES")
        require(not any(v is True for v in (cambio.get("after_unknown") or {}).values()), "ONLY_EXPECTED_ATTRIBUTES")
        require(not any(abierto in json.dumps(despues, sort_keys=True) for abierto in ABIERTOS), "OPEN_CIDR")

        if tipo == "aws_security_group":
            (sentido,) = atributos
            otro = "egress" if sentido == "ingress" else "ingress"
            require(antes.get(sentido) == [] and despues.get(otro) == [] == antes.get(otro), "SG_REFLECTION")
            require(_ordenadas(despues[sentido]) == _ordenadas(esperado.get((antes["id"], sentido), [])), "SG_REFLECTION")
            require(previos[direccion]["values"]["id"] == antes["id"] == despues["id"], "SG_REFLECTION")
        else:
            require(antes.get("name_prefix") is None and despues.get("name_prefix") == "", "NAME_PREFIX")
            previo = {p["name"]: (p["value"], p["apply_method"]) for p in antes["parameter"]}
            nuevo = {p["name"]: (p["value"], p["apply_method"]) for p in despues["parameter"]}
            require(set(previo) == set(nuevo) and len(previo) == len(antes["parameter"]) == len(despues["parameter"]),
                    "PARAMETER_TRANSITION")
            cambiados = {n for n in previo if previo[n] != nuevo[n]}
            require(cambiados == set(REPRESENTACION), "PARAMETER_TRANSITION")
            for nombre, valor in REPRESENTACION.items():
                require(previo[nombre] == (valor, "immediate") and nuevo[nombre] == (valor, "pending-reboot"),
                        "PARAMETER_TRANSITION")
        vistos[direccion] = sorted(distintos)
    require(set(vistos) == set(DRIFT), "DRIFT_SET")

    valores = plan.get("planned_values", {}).get("outputs", {})
    require(not any(dato.get("sensitive") for dato in valores.values()), "SENSITIVE_OUTPUT")
    # Ultimo control, a proposito: un rechazo OUTPUTS significa que todo lo anterior cumple.
    salidas = plan.get("output_changes", {})
    previas = plan["prior_state"]["values"].get("outputs", {})
    require(set(salidas) == set(plan["configuration"]["root_module"].get("outputs", {})), "OUTPUTS")
    require(set(SALIDAS_RDS) <= set(salidas), "OUTPUTS")
    for nombre, dato in salidas.items():
        require(dato.get("before_sensitive") is False and dato.get("after_sensitive") is False, "OUTPUTS")
        if nombre in SALIDAS_RDS:
            accion, antes = SALIDAS_RDS[nombre]
            require(dato.get("actions") == [accion] and dato.get("after") is None
                    and dato.get("after_unknown") is True, "OUTPUTS")
            require(type(dato.get("before")) is type(antes) and dato.get("before") == antes, "OUTPUTS")
            if antes is None:
                require(nombre not in previas, "OUTPUTS")
            else:
                previa = previas.get(nombre) or {}
                require(type(previa.get("value")) is type(antes) and previa.get("value") == antes
                        and previa.get("sensitive") is False, "OUTPUTS")
        else:
            require(dato.get("actions") == ["no-op"] and dato.get("before") == dato.get("after")
                    and dato.get("after_unknown") is not True, "OUTPUTS")

    return {"resource_drift": len(vistos), "resource_changes": 0, "tainted": [GRUPO],
            "atributos": dict(sorted(vistos.items())), "salidas_excepcionales": sorted(SALIDAS_RDS),
            "salidas_no_op": len(salidas) - len(SALIDAS_RDS)}


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
        raise SystemExit(f"H-031-3-RECOVERY-DN2: refresh plan rejected ({codigo}); inspect privately. No apply authorized.") from None
    print(json.dumps({"gate": "DN2_REFRESH_PLAN_OK", "json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
