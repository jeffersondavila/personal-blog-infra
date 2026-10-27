"""Gate offline de CONVERGENCIA del root de datos tras el refresh apply y el untaint (Task/031 §40). Nunca aplica.

Criterio `ACTIONABLE_CONVERGENCE_OK`. Un plan normal converge si:
- no tiene nada que aplicar: `applyable is False`, `complete is True` y `errored is False`, explicitos
  (§42: es lo que Terraform emite para «No changes»);
- cero cambios de recurso: las 21 direcciones en `no-op` con `before == after`, sin import ni move;
- cero diferidos; todas las salidas `no-op`; state previo 21/21 sin ningun taint; retencion 1; version de
  la contrasena 1; sin la variable efimera en el plan;
- y `resource_drift` es:
  - CASO A: vacio; o
  - CASO B: EXACTAMENTE una entrada, `module.base_de_datos.aws_db_instance.this`, `update`, cuya UNICA
    diferencia es `latest_restorable_time`, el atributo movil calculado por AWS, con el contrato temporal de
    `instante_movil`: instantes validos, despues >= antes, ninguno en el futuro y el de AWS con 24 h como
    maximo de antiguedad (enmienda de §40 del 2026-10-18, aprobada el 2026-10-19).
En el caso B el resultado informa `resource_drift = 1` y el drift movil: nunca `resource_drift = 0`. Ningun
otro drift se admite, y nada de esto se resuelve con `ignore_changes`.

Fases (decision del usuario del 2026-10-08): el conjunto de recursos depende de la fase aplicada. `h0313` son los 21
de H-031-3; `h0318` suma las 8 alarmas de D-11; `h0319`, ademas, el rol de D-20 y su politica; y `h0315`, ademas,
los 4 recursos de la ejecutora de D-24, que se aplica la ultima, cuando la cuota de Lambda permita RC=1 (35). La
fase se DECLARA (`--fase`): el state debe ser EXACTAMENTE su conjunto, ni un recurso de menos ni uno de mas.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from scripts.terraform_datos.check_plan import ADDRESSES, PROVIDER, _variables, require
from scripts.terraform_datos.check_plan_alarmas import NUEVOS as ALARMAS
from scripts.terraform_datos.check_plan_ejecutor import NUEVOS as EJECUTORA
from scripts.terraform_datos.check_plan_grafana import NUEVOS as ROL_DE_GRAFANA
from scripts.terraform_datos.check_plan_h0316 import NUEVOS as H0316, _sin_secretos
from scripts.terraform_datos.empaquetar_ejecutor import SHA256_ESPERADO_H0316
from scripts.terraform_datos.check_plan_recuperacion import INSTANCIA_RDS, _estado_previo
from scripts.terraform_datos.check_plan_refresh_instancia import MOVILES, instante_movil

FASES = {
    "h0313": frozenset(ADDRESSES),
    "h0318": frozenset(ADDRESSES | set(ALARMAS)),
    "h0319": frozenset(ADDRESSES | set(ALARMAS) | set(ROL_DE_GRAFANA)),
    "h0315": frozenset(ADDRESSES | set(ALARMAS) | set(ROL_DE_GRAFANA) | set(EJECUTORA)),
}
FASES["h0316"] = FASES["h0315"] | frozenset(H0316)


#: CLI operativa de los planes de convergencia (mantenimiento de CI de Task/031, 2026-10-23). Debe coincidir con
#: `VERSION_DE_TERRAFORM` de `scripts/laboratorio/herramientas.py`; una prueba lo exige. Las guardas de fases ya
#: cerradas que reutilizan esta funcion pasan `version="1.16.2"`: validan evidencia historica, no planes nuevos.
VERSION_DE_TERRAFORM = "1.16.7"


def check(plan, account, arn_de_medios, ahora=None, fase="h0313", version=VERSION_DE_TERRAFORM):
    ahora = ahora or datetime.now(timezone.utc)
    require(fase in FASES, "PHASE")
    esperados = FASES[fase]
    require(plan.get("terraform_version") == version, "VERSION")
    # §42: un plan CONVERGENTE no tiene nada que aplicar y Terraform lo marca `applyable = false`. Exigir
    # `true` (heredado de las guardas de planes con cambios) rechazaba justo la convergencia.
    require(plan.get("applyable") is False, "APPLYABLE")
    require(plan.get("complete") is True and plan.get("errored") is False, "INCOMPLETE")
    _variables(plan, account, arn_de_medios)
    if fase == "h0316":
        _sin_secretos(plan)
        require((plan["variables"].get("zip_de_la_ejecutora", {}).get("value") or {}).get("sha256")
                == SHA256_ESPERADO_H0316, "ARTIFACT_PIN")
        for nombre in ("version_de_blog_migrate", "version_de_blog_app"):
            valor = plan["variables"].get(nombre, {}).get("value")
            require(type(valor) is int and valor == 1, "SQL_CREDENTIAL_VERSION")
    require(plan["variables"].get("version_de_la_contrasena", {}).get("value") == 1, "PASSWORD_VERSION")
    require(plan["variables"].get("dias_de_retencion_de_backups", {}).get("value") == 1, "RETENTION")
    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.operador") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")

    previos = _estado_previo(plan)
    require(set(previos) == esperados and not any(r.get("tainted") for r in previos.values()), "PRIOR_STATE")

    vistos = set()
    for item in plan.get("resource_changes", []):
        cambio = item["change"]
        require(item.get("mode") == "managed" and item["address"] in esperados and item["address"] not in vistos
                and item.get("provider_name") == PROVIDER and not cambio.get("importing")
                and not item.get("previous_address") and cambio.get("actions") == ["no-op"]
                and cambio.get("before") == cambio.get("after"), "CHANGES")
        vistos.add(item["address"])
    require(vistos == esperados, "CHANGES")
    require(not plan.get("deferred_changes"), "DEFERRED")

    salidas = plan.get("output_changes", {})
    require(set(salidas) == set(plan["configuration"]["root_module"].get("outputs", {})), "OUTPUTS")
    require(all(d.get("actions") == ["no-op"] and d.get("before") == d.get("after") for d in salidas.values()), "OUTPUTS")

    deriva = plan.get("resource_drift") or []
    movil = []
    if deriva:
        require(len(deriva) == 1, "DRIFT")
        entrada = deriva[0]
        cambio = entrada.get("change", {})
        require(entrada.get("address") == INSTANCIA_RDS and entrada.get("type") == "aws_db_instance"
                and entrada.get("mode") == "managed" and entrada.get("provider_name") == PROVIDER
                and not entrada.get("previous_address") and not cambio.get("importing")
                and cambio.get("actions") == ["update"]
                and not any(v is True for v in (cambio.get("after_unknown") or {}).values()), "DRIFT")
        antes, despues = cambio.get("before") or {}, cambio.get("after") or {}
        distintos = {k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k)}
        require(distintos and distintos <= MOVILES, "DRIFT")
        for atributo in sorted(distintos):
            instante_movil(antes.get(atributo), despues.get(atributo), ahora)
            movil.append(f"{INSTANCIA_RDS}: {atributo}")

    return {"gate": "ACTIONABLE_CONVERGENCE_OK", "fase": fase, "recursos": len(esperados), "add": 0, "change": 0,
            "destroy": 0,
            "resource_drift": len(deriva), "drift_movil": movil, "deferred_changes": 0, "outputs": "no-op"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--variables", required=True, type=Path,
                        help="JSON privado con expected_account_id y arn_del_bucket_de_medios")
    parser.add_argument("--fase", choices=sorted(FASES), default="h0313", help="Fase aplicada cuyo conjunto se exige.")
    args = parser.parse_args()
    try:
        raw = args.plan_json.read_bytes()
        privadas = json.loads(args.variables.read_text(encoding="utf-8"))
        result = check(json.loads(raw), privadas["expected_account_id"], privadas["arn_del_bucket_de_medios"],
                       fase=args.fase)
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        codigo = str(error) if isinstance(error, ValueError) and str(error).isupper() else type(error).__name__
        raise SystemExit(f"convergencia rechazada ({codigo}); inspect privately. No apply authorized.") from None
    print(json.dumps({"json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
