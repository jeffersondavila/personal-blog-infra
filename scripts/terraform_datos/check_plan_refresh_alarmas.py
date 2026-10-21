"""Gate offline del REFRESH-ONLY de H-031-8 (Task/031 §47): listas de acciones de las alarmas. Nunca aplica.

Aprobado por el usuario el 2026-10-15. Tras crear las 8 alarmas, el state guardo `alarm_actions`, `ok_actions` e
`insufficient_data_actions` como `null` y AWS las devuelve como `[]`: misma semantica, ninguna accion. La guarda de
convergencia, de lista cerrada, rechaza esa deriva (DRIFT) y la de H-031-9 la heredaria. Este refresh-only solo
escribe el state, sin ningun cambio en AWS; despues, la convergencia y H-031-9 usan sus guardas ORIGINALES.

Lista CERRADA. El plan es aceptable solo si:
- Terraform 1.16.2; `applyable`, `complete` y no `errored`; CERO `resource_changes` y cero diferidos.
- Variables del root como en H-031-8: contrasena en version 1, retencion 1, sin el artefacto de la ejecutora y sin
  la integracion de Grafana. Checks en `pass` y el grupo por omision sin uso.
- `prior_state`, que ya esta refrescado: los 29 recursos de H-031-8, sin taint.
- `resource_drift`: las 8 alarmas, una vez cada una, `update` con EXACTAMENTE esas 3 listas de `null` a `[]`, sin
  desconocidos y con el `prior_state` igual al valor refrescado. Ademas, como mucho, la instancia RDS en el caso B
  de §40 (solo `latest_restorable_time`, AWS con 24 h como maximo de antiguedad desde la enmienda del
  2026-10-18, SIN la excepcion puntual de §47) y coherente con el
  `prior_state`.
- Configuracion con las alarmas y sin la ejecutora ni D-20, que se retira temporalmente durante el refresh.
- Salidas: las 16 de H-031-8, todas `no-op`.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from scripts.terraform_datos.check_plan import ADDRESSES, PROVIDER, _sin_grupo_por_omision, _variables, require
from scripts.terraform_datos.check_plan_alarmas import NUEVOS as ALARMAS, SALIDA_NUEVA
from scripts.terraform_datos.check_plan_ejecutor import SALIDAS_EXISTENTES, _deriva
from scripts.terraform_datos.check_plan_recuperacion import INSTANCIA_RDS, _estado_previo

LISTAS = ("alarm_actions", "insufficient_data_actions", "ok_actions")
ESTADO = ADDRESSES | set(ALARMAS)


def _alarma(entrada, previos):
    cambio = entrada.get("change", {})
    require(entrada.get("type") == "aws_cloudwatch_metric_alarm" and entrada.get("mode") == "managed"
            and entrada.get("provider_name") == PROVIDER and not entrada.get("previous_address")
            and not cambio.get("importing") and cambio.get("actions") == ["update"]
            and not any(v is True for v in (cambio.get("after_unknown") or {}).values()), "ALARM_DRIFT")
    antes, despues = cambio.get("before") or {}, cambio.get("after") or {}
    distintos = {k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k)}
    require(distintos == set(LISTAS)
            and all(antes.get(k) is None and despues.get(k) == [] for k in LISTAS), "ALARM_DRIFT")
    require(previos[entrada["address"]]["values"] == despues, "DRIFT_COHERENCE")


def check(plan, account, arn_de_medios, ahora=None):
    ahora = ahora or datetime.now(timezone.utc)
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True and plan.get("complete") is True and not plan.get("errored"), "INCOMPLETE")
    require(not plan.get("resource_changes"), "RESOURCE_CHANGES")
    require(not plan.get("deferred_changes"), "DEFERRED")
    _variables(plan, account, arn_de_medios)
    variables = plan["variables"]
    require(variables.get("version_de_la_contrasena", {}).get("value") == 1, "PASSWORD_VERSION")
    require(variables.get("dias_de_retencion_de_backups", {}).get("value") == 1, "RETENTION")
    require("zip_de_la_ejecutora" not in variables and "integracion_grafana" not in variables, "VARIABLES")
    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.operador") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")
    _sin_grupo_por_omision(plan)

    previos = _estado_previo(plan)
    require(set(previos) == ESTADO and not any(r.get("tainted") for r in previos.values()), "PRIOR_STATE")

    deriva = plan.get("resource_drift") or []
    alarmas = [e for e in deriva if e.get("address") in ALARMAS]
    resto = [e for e in deriva if e.get("address") not in ALARMAS]
    require(sorted(e["address"] for e in alarmas) == sorted(ALARMAS), "ALARM_DRIFT")
    for entrada in alarmas:
        _alarma(entrada, previos)
    _, movil = _deriva({"resource_drift": resto}, ahora)
    if movil:
        require(previos[INSTANCIA_RDS]["values"] == resto[0]["change"]["after"], "DRIFT_COHERENCE")

    llamadas = plan["configuration"]["root_module"]["module_calls"]
    require("alarmas_rds" in llamadas and "ejecutor_privado" not in llamadas and "lectura_grafana" not in llamadas,
            "WIRING")
    salidas = plan.get("output_changes") or {}
    declaradas = set(plan["configuration"]["root_module"].get("outputs") or {})
    require(set(salidas) == declaradas == SALIDAS_EXISTENTES | {SALIDA_NUEVA}, "OUTPUTS")
    for dato in salidas.values():
        require(dato.get("actions") == ["no-op"] and dato.get("before") == dato.get("after")
                and not dato.get("after_unknown") and not dato.get("after_sensitive"), "OUTPUTS")

    return {"gate": "ALARMS_REFRESH_OK", "resource_changes": 0, "add": 0, "change": 0, "destroy": 0,
            "resource_drift": len(deriva), "normalizadas": sorted(ALARMAS), "listas": list(LISTAS),
            "drift_movil": movil}


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
        raise SystemExit(f"refresh-only de H-031-8 rechazado ({codigo}); inspect privately. No apply authorized.") \
            from None
    print(json.dumps({"json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
