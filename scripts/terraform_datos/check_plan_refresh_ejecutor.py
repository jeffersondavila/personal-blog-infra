"""Gate offline del REFRESH-ONLY de H-031-5 (Task/031): normalizacion de la ejecutora tras crearla. Nunca aplica.

Preparada ANTES del apply, por la leccion de H-031-8 y H-031-9. Tras CREAR recursos, el primer plan trae deriva de
normalizacion del provider, y la guarda de convergencia, de lista cerrada, la rechaza. Para la ejecutora no se sabe
de antemano que atributos normalizara AWS, asi que esta guarda admite solo dos formas sin efecto real:
- un atributo de `null` a una coleccion VACIA (`[]` o `{}`);
- en el rol, `inline_policy` de `[]` a UNA politica identica (nombre y contenido) a la que ya esta en el state como
  `aws_iam_role_policy`, el atributo espejo.
Cualquier otra diferencia es un STOP. Solo escribe el state; ningun cambio en AWS. Despues, la convergencia usa su
guarda ORIGINAL (`check_plan_convergencia --fase h0315`).

Lista CERRADA. El plan es aceptable solo si:
- Terraform 1.16.2; `applyable`, `complete` y no `errored`; CERO `resource_changes` y cero diferidos.
- Variables del root con la ejecutora cableada:
  - contrasena en version 1 y retencion 1;
  - el artefacto con el pin de `empaquetar_ejecutor.py`;
  - `integracion_grafana` presente.
- Checks en `pass` y el grupo por omision sin uso.
- `prior_state`, que ya esta refrescado: los 35 recursos de la fase `h0315`, sin taint.
- `resource_drift`:
  - como mucho UNA entrada por recurso de la ejecutora, `update`, sin desconocidos, con solo las dos formas de
    arriba y coherente con el `prior_state`;
  - para el resto, el caso A/B de §40 (AWS con 24 h como maximo de antiguedad, enmienda del 2026-10-18; sin la
    excepcion puntual de §47), tambien coherente.
- Configuracion con la ejecutora, las alarmas y D-20.
- Salidas: las 19 (las 17 tras H-031-9 y las 2 de la ejecutora), todas `no-op`.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from scripts.terraform_datos.check_plan import PROVIDER, _sin_grupo_por_omision, _variables, require
from scripts.terraform_datos.check_plan_convergencia import FASES
from scripts.terraform_datos.check_plan_ejecutor import NUEVOS, POLITICA, ROL, SALIDAS_NUEVAS, _deriva, _linea_base
from scripts.terraform_datos.check_plan_recuperacion import INSTANCIA_RDS, _estado_previo
from scripts.terraform_datos.empaquetar_ejecutor import SHA256_ESPERADO

VACIAS = ([], {})


def _reflejo_exacto(valor, politica):
    """El espejo `inline_policy` del rol: UNA politica, igual en nombre y contenido a la del state."""
    if not (isinstance(valor, list) and len(valor) == 1 and isinstance(valor[0], dict)
            and set(valor[0]) == {"name", "policy"}):
        return False
    try:
        return (valor[0]["name"] == politica.get("name")
                and json.loads(valor[0]["policy"]) == json.loads(politica.get("policy") or ""))
    except (TypeError, ValueError):
        return False


def _normalizacion(entrada, previos):
    address, cambio = entrada["address"], entrada.get("change", {})
    require(entrada.get("type") == NUEVOS[address] and entrada.get("mode") == "managed"
            and entrada.get("provider_name") == PROVIDER and not entrada.get("previous_address")
            and not cambio.get("importing") and cambio.get("actions") == ["update"]
            and not any(v is True for v in (cambio.get("after_unknown") or {}).values()), "EXECUTOR_DRIFT")
    antes, despues = cambio.get("before") or {}, cambio.get("after") or {}
    distintos = sorted(k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k))
    require(distintos, "EXECUTOR_DRIFT")
    for atributo in distintos:
        if address == ROL and atributo == "inline_policy":
            require(antes.get(atributo) == [] and _reflejo_exacto(despues.get(atributo), previos[POLITICA]["values"]),
                    "EXECUTOR_DRIFT")
        else:
            require(antes.get(atributo) is None and any(despues.get(atributo) == v and type(despues.get(atributo))
                                                        is type(v) for v in VACIAS), "EXECUTOR_DRIFT")
    require(previos[address]["values"] == despues, "DRIFT_COHERENCE")
    return [f"{address}: {atributo}" for atributo in distintos]


def check(plan, account, arn_de_medios, ahora=None):
    ahora = ahora or datetime.now(timezone.utc)
    _, salidas_previas = _linea_base()
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True and plan.get("complete") is True and not plan.get("errored"), "INCOMPLETE")
    require(not plan.get("resource_changes"), "RESOURCE_CHANGES")
    require(not plan.get("deferred_changes"), "DEFERRED")
    _variables(plan, account, arn_de_medios)
    variables = plan["variables"]
    require(variables.get("version_de_la_contrasena", {}).get("value") == 1, "PASSWORD_VERSION")
    require(variables.get("dias_de_retencion_de_backups", {}).get("value") == 1, "RETENTION")
    require((variables.get("zip_de_la_ejecutora", {}).get("value") or {}).get("sha256") == SHA256_ESPERADO,
            "ARTIFACT_PIN")
    require(variables.get("integracion_grafana", {}).get("value"), "VARIABLES")
    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.operador") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")
    _sin_grupo_por_omision(plan)

    previos = _estado_previo(plan)
    require(set(previos) == FASES["h0315"] and not any(r.get("tainted") for r in previos.values()), "PRIOR_STATE")

    deriva = plan.get("resource_drift") or []
    de_la_ejecutora = [e for e in deriva if e.get("address") in NUEVOS]
    resto = [e for e in deriva if e.get("address") not in NUEVOS]
    direcciones = [e["address"] for e in de_la_ejecutora]
    require(len(direcciones) == len(set(direcciones)), "EXECUTOR_DRIFT")
    normalizados = sorted(n for e in de_la_ejecutora for n in _normalizacion(e, previos))
    _, movil = _deriva({"resource_drift": resto}, ahora)
    if movil:
        require(previos[INSTANCIA_RDS]["values"] == resto[0]["change"]["after"], "DRIFT_COHERENCE")

    llamadas = plan["configuration"]["root_module"]["module_calls"]
    require(all(modulo in llamadas for modulo in ("ejecutor_privado", "alarmas_rds", "lectura_grafana")), "WIRING")
    salidas = plan.get("output_changes") or {}
    declaradas = set(plan["configuration"]["root_module"].get("outputs") or {})
    require(set(salidas) == declaradas == salidas_previas | SALIDAS_NUEVAS, "OUTPUTS")
    for dato in salidas.values():
        require(dato.get("actions") == ["no-op"] and dato.get("before") == dato.get("after")
                and not dato.get("after_unknown") and not dato.get("after_sensitive"), "OUTPUTS")

    return {"gate": "EXECUTOR_REFRESH_OK", "resource_changes": 0, "add": 0, "change": 0, "destroy": 0,
            "resource_drift": len(deriva), "normalizados": normalizados, "drift_movil": movil}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
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
        raise SystemExit(f"refresh-only de H-031-5 rechazado ({codigo}); inspect privately. No apply authorized.") \
            from None
    print(json.dumps({"json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
