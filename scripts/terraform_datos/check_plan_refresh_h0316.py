"""Refresh-only H-031-6: espejos exactos del rol/SG y atributo movil. Nunca aplica.

Motivo: una politica inline y una regla separada actualizan los espejos calculados del rol y el SG.
Solo admite esas dos transiciones exactas, no normalizaciones genericas. Su apply exige autorizacion nueva.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from scripts.terraform_datos.check_plan import PROVIDER, require
from scripts.terraform_datos.check_plan_convergencia import check as convergencia
from scripts.terraform_datos.check_plan_ejecutor import ROL, POLITICA, _deriva, _desconocido
from scripts.terraform_datos.check_plan_h0316 import POLITICA_DE_EXPORT, REGLA_DE_EXPORT
from scripts.terraform_datos.check_plan_recuperacion import _estado_previo, INSTANCIA_RDS

SG_ADMIN = "module.red.aws_security_group.admin"
REGLA_RDS = "module.red.aws_vpc_security_group_egress_rule.admin_a_rds"


def reflejo_regla(v):
    return {"description": v.get("description") or "", "from_port": v["from_port"], "to_port": v["to_port"],
            "protocol": v["ip_protocol"], "self": False,
            "cidr_blocks": [v["cidr_ipv4"]] if v.get("cidr_ipv4") else [],
            "ipv6_cidr_blocks": [v["cidr_ipv6"]] if v.get("cidr_ipv6") else [],
            "prefix_list_ids": [v["prefix_list_id"]] if v.get("prefix_list_id") else [],
            "security_groups": [v["referenced_security_group_id"]] if v.get("referenced_security_group_id") else []}


def _politicas(lista):
    require(isinstance(lista, list), "H0316_DRIFT")
    require(all(isinstance(p, dict) and set(p) == {"name", "policy"} for p in lista), "H0316_DRIFT")
    require(len({p["name"] for p in lista}) == len(lista), "H0316_DRIFT")
    return {p["name"]: json.loads(p["policy"]) for p in lista}


def check(plan, account, arn_de_medios, ahora=None):
    ahora = ahora or datetime.now(timezone.utc)
    require(plan.get("applyable") is True, "APPLYABLE")
    require(not plan.get("resource_changes"), "RESOURCE_CHANGES")
    previos = _estado_previo(plan)
    # Reutilizar TODAS las gates de la fase, convirtiendo solo la representacion refresh-only en no-op.
    copia = copy.deepcopy(plan)
    copia.update(applyable=False, resource_drift=[], resource_changes=[{
        "address": a, "mode": "managed", "type": r["type"], "provider_name": PROVIDER,
        "change": {"actions": ["no-op"], "before": r["values"], "after": r["values"]},
    } for a, r in previos.items()])
    # Guarda historica de H-031-6: sus planes se emitieron con Terraform 1.16.2.
    convergencia(copia, account, arn_de_medios, ahora=ahora, fase="h0316", version="1.16.2")
    vistos, normalizados, resto = set(), [], []
    for entrada in plan.get("resource_drift") or []:
        address, c = entrada.get("address"), entrada.get("change") or {}
        require(address not in vistos, "H0316_DRIFT"); vistos.add(address)
        if address not in (ROL, SG_ADMIN):
            resto.append(entrada); continue
        require(entrada.get("mode") == "managed" and entrada.get("provider_name") == PROVIDER
                and entrada.get("type") == previos[address]["type"] and not entrada.get("previous_address")
                and not c.get("importing") and not c.get("replace_paths") and c.get("actions") == ["update"]
                and not _desconocido(c.get("after_unknown")), "H0316_DRIFT")
        antes, despues = c.get("before") or {}, c.get("after") or {}
        atributo = "inline_policy" if address == ROL else "egress"
        distintos = {k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k)}
        require(distintos == {atributo}, "H0316_DRIFT")
        require(despues == previos[address]["values"], "DRIFT_COHERENCE")
        if address == ROL:
            politica = previos[POLITICA]["values"]
            export = previos[POLITICA_DE_EXPORT]["values"]
            original = {politica["name"]: json.loads(politica["policy"])}
            require(_politicas(antes[atributo]) == original and _politicas(despues[atributo])
                    == {**original, export["name"]: json.loads(export["policy"])}, "H0316_DRIFT")
        else:
            vieja = reflejo_regla(previos[REGLA_RDS]["values"])
            nueva = reflejo_regla(previos[REGLA_DE_EXPORT]["values"])
            require(antes[atributo] == [vieja] and isinstance(despues[atributo], list)
                    and len(despues[atributo]) == 2 and vieja in despues[atributo] and nueva in despues[atributo],
                    "H0316_DRIFT")
        normalizados.append(f"{address}: {atributo}")
    _, movil = _deriva({"resource_drift": resto}, ahora)
    if movil:
        require(previos[INSTANCIA_RDS]["values"] == resto[0]["change"]["after"], "DRIFT_COHERENCE")
    return {"gate": "H0316_REFRESH_OK", "add": 0, "change": 0, "destroy": 0,
            "resource_changes": 0, "resource_drift": len(vistos), "normalizados": normalizados, "drift_movil": movil}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--variables", required=True, type=Path)
    args = parser.parse_args()
    try:
        raw = args.plan_json.read_bytes()
        variables = json.loads(args.variables.read_text(encoding="utf-8"))
        resultado = check(json.loads(raw), variables["expected_account_id"], variables["arn_del_bucket_de_medios"])
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        codigo = str(error) if isinstance(error, ValueError) and str(error).isupper() else type(error).__name__
        raise SystemExit(f"Refresh H-031-6 rechazado ({codigo}). Revisar en privado; sin apply.") from None
    print(json.dumps({"json_sha256": hashlib.sha256(raw).hexdigest(), **resultado}))


if __name__ == "__main__":
    main()
