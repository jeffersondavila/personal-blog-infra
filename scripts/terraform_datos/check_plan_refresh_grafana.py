"""Gate offline del REFRESH-ONLY de H-031-9 (Task/031 §47): atributos calculados del rol de D-20. Nunca aplica.

Aprobado por el usuario el 2026-10-15. Tras crear el rol y su politica en linea, AWS devuelve dos atributos que el
state no tenia:
- `inline_policy`, con la politica que crea el recurso `aws_iam_role_policy`;
- `tags` como `{}` en vez de `null`.
La guarda de convergencia, de lista cerrada, rechaza esa deriva (DRIFT). Este refresh-only solo escribe el state, sin
ningun cambio en AWS. Despues, la convergencia usa su guarda ORIGINAL.

Lista CERRADA. El plan es aceptable solo si:
- Terraform 1.16.2; `applyable`, `complete` y no `errored`; CERO `resource_changes` y cero diferidos.
- Variables del root como en H-031-9:
  - contrasena en version 1, retencion 1 y sin el artefacto de la ejecutora;
  - `integracion_grafana` IGUAL a la cuenta y al ExternalId privados.
- Checks en `pass` y el grupo por omision sin uso.
- `prior_state`, que ya esta refrescado: los 31 recursos de H-031-9, sin taint.
- `resource_drift`:
  - el rol, una sola vez, `update` con EXACTAMENTE `inline_policy` de `[]` a la UNICA politica esperada (nombre y
    contenido identicos a los de `permisos`) y `tags` de `null` a `{}`, sin desconocidos y coherente con el
    `prior_state`;
  - como mucho, la instancia RDS en el caso B de §40 (sin la excepcion de §47; desde la enmienda del 2026-10-18,
    las 24 h miden la frescura de AWS), tambien coherente.
- Configuracion con las alarmas y D-20, sin la ejecutora.
- Salidas: las 17 de H-031-9, todas `no-op`.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from scripts.terraform_datos.check_plan import ADDRESSES, PROVIDER, _sin_grupo_por_omision, _variables, require
from scripts.terraform_datos.check_plan_alarmas import NUEVOS as ALARMAS
from scripts.terraform_datos.check_plan_ejecutor import _deriva
from scripts.terraform_datos.check_plan_grafana import (NOMBRE_DEL_ROL, NUEVOS as DE_GRAFANA, ROL, SALIDA_NUEVA,
                                                        SALIDAS_EXISTENTES, permisos)
from scripts.terraform_datos.check_plan_recuperacion import INSTANCIA_RDS, _estado_previo

NORMALIZADOS = ("inline_policy", "tags")
ESTADO = ADDRESSES | set(ALARMAS) | set(DE_GRAFANA)


def _politica_esperada(valor, account):
    if not (isinstance(valor, list) and len(valor) == 1 and isinstance(valor[0], dict)
            and set(valor[0]) == {"name", "policy"} and valor[0]["name"] == f"{NOMBRE_DEL_ROL}-lectura"):
        return False
    try:
        return json.loads(valor[0]["policy"]) == permisos(account)
    except (TypeError, ValueError):
        return False


def _rol(entrada, previos, account):
    cambio = entrada.get("change", {})
    require(entrada.get("type") == "aws_iam_role" and entrada.get("mode") == "managed"
            and entrada.get("provider_name") == PROVIDER and not entrada.get("previous_address")
            and not cambio.get("importing") and cambio.get("actions") == ["update"]
            and not any(v is True for v in (cambio.get("after_unknown") or {}).values()), "ROLE_DRIFT")
    antes, despues = cambio.get("before") or {}, cambio.get("after") or {}
    distintos = {k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k)}
    require(distintos == set(NORMALIZADOS) and antes.get("inline_policy") == []
            and _politica_esperada(despues.get("inline_policy"), account)
            and antes.get("tags") is None and despues.get("tags") == {}
            and isinstance(despues.get("tags"), dict), "ROLE_DRIFT")
    require(previos[ROL]["values"] == despues, "DRIFT_COHERENCE")


def check(plan, account, arn_de_medios, cuenta_de_grafana, external_id, ahora=None):
    ahora = ahora or datetime.now(timezone.utc)
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True and plan.get("complete") is True and not plan.get("errored"), "INCOMPLETE")
    require(not plan.get("resource_changes"), "RESOURCE_CHANGES")
    require(not plan.get("deferred_changes"), "DEFERRED")
    _variables(plan, account, arn_de_medios)
    variables = plan["variables"]
    require(variables.get("version_de_la_contrasena", {}).get("value") == 1, "PASSWORD_VERSION")
    require(variables.get("dias_de_retencion_de_backups", {}).get("value") == 1, "RETENTION")
    require("zip_de_la_ejecutora" not in variables, "VARIABLES")
    require(variables.get("integracion_grafana", {}).get("value") == {
        "cuenta": cuenta_de_grafana, "external_id": external_id}, "GRAFANA")
    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.operador") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")
    _sin_grupo_por_omision(plan)

    previos = _estado_previo(plan)
    require(set(previos) == ESTADO and not any(r.get("tainted") for r in previos.values()), "PRIOR_STATE")

    deriva = plan.get("resource_drift") or []
    del_rol = [e for e in deriva if e.get("address") == ROL]
    resto = [e for e in deriva if e.get("address") != ROL]
    require(len(del_rol) == 1, "ROLE_DRIFT")
    _rol(del_rol[0], previos, account)
    _, movil = _deriva({"resource_drift": resto}, ahora)
    if movil:
        require(previos[INSTANCIA_RDS]["values"] == resto[0]["change"]["after"], "DRIFT_COHERENCE")

    llamadas = plan["configuration"]["root_module"]["module_calls"]
    require("alarmas_rds" in llamadas and "lectura_grafana" in llamadas and "ejecutor_privado" not in llamadas,
            "WIRING")
    salidas = plan.get("output_changes") or {}
    declaradas = set(plan["configuration"]["root_module"].get("outputs") or {})
    require(set(salidas) == declaradas == SALIDAS_EXISTENTES | {SALIDA_NUEVA}, "OUTPUTS")
    for dato in salidas.values():
        require(dato.get("actions") == ["no-op"] and dato.get("before") == dato.get("after")
                and not dato.get("after_unknown") and not dato.get("after_sensitive"), "OUTPUTS")

    return {"gate": "GRAFANA_ROLE_REFRESH_OK", "resource_changes": 0, "add": 0, "change": 0, "destroy": 0,
            "resource_drift": len(deriva), "normalizados": list(NORMALIZADOS), "drift_movil": movil}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--variables", required=True, type=Path,
                        help="JSON privado con expected_account_id, arn_del_bucket_de_medios e integracion_grafana")
    args = parser.parse_args()
    try:
        raw = args.plan_json.read_bytes()
        privadas = json.loads(args.variables.read_text(encoding="utf-8"))
        grafana = privadas["integracion_grafana"]
        result = check(json.loads(raw), privadas["expected_account_id"], privadas["arn_del_bucket_de_medios"],
                       grafana["cuenta"], grafana["external_id"])
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        codigo = str(error) if isinstance(error, ValueError) and str(error).isupper() else type(error).__name__
        raise SystemExit(f"refresh-only de H-031-9 rechazado ({codigo}); inspect privately. No apply authorized.") \
            from None
    print(json.dumps({"json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
