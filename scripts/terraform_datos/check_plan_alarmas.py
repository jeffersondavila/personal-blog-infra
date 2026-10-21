"""Gate offline del plan productivo de H-031-8 (Task/031): alarmas de D-11. Nunca aplica.

Decision del usuario del 2026-10-08: el cableado de la ejecutora de D-24 sale del root hasta que la cuota de
concurrencia de Lambda permita RC=1, y las fases que no dependen de ella —estas alarmas y el rol de D-20— se aplican
antes. Lista CERRADA. El plan es aceptable solo si:
- Terraform 1.16.2; `applyable`, `complete` y no `errored`.
- Variables del root como en H-031-3, contrasena en version 1, retencion 1 (plan FREE) y SIN la variable del
  artefacto de la ejecutora; todos los checks en `pass`; el grupo por omision sin uso.
- State previo: los 21 recursos actuales, sin taint. Los 21 en `no-op` con `before == after`.
- EXACTAMENTE 8 `create`, uno por alarma de `ALARMAS`, y nada mas: ni la ejecutora ni ningun otro recurso.
- Cada alarma: nombre `blog-prod-rds-<senal>`, `AWS/RDS`, UNICA dimension la instancia productiva, metrica,
  estadistico o percentil, periodo, evaluaciones = puntos, umbral y comparador del catalogo; datos ausentes
  `missing`; sin unidad, sin metric math, en us-east-2, con razon; y SIN acciones (`actions_enabled = false` y
  listas vacias): SNS, correo o paginacion no estan aprobados.
- Cableado: `identificador_de_la_instancia` sale de `module.base_de_datos.identificador`; ninguna llamada a la
  ejecutora en la configuracion.
- Sin diferidos; las 15 salidas actuales en `no-op` y una nueva, `alarmas_de_rds`, con los ocho nombres.
- `resource_drift` en el caso A (vacio) o B (solo `latest_restorable_time` de RDS, contrato movil de §40).

EXCEPCION PUNTUAL de §47, aprobada por el usuario el 2026-10-13. El state no se escribe desde el 2026-10-05, y
la diferencia del atributo movil (8 d 8 h) supera la ventana de 24 h de §40. Solo con `--excepcion-ventana-movil` y
solo si el instante del state es EXACTAMENTE `EXCEPCION_VENTANA_MOVIL`, esa diferencia puede pasar de 24 h. Aun asi,
el instante de AWS no puede ser anterior al del state ni posterior a `ahora`, ni tener mas de 24 h (PITR vivo). El
apply pone el state al dia. La convergencia y H-031-9 conservan la ventana de §40, y ninguna otra guarda tiene esta
excepcion.

Enmienda de §40 del 2026-10-18 (aprobada el 2026-10-19): el contrato GENERAL de `instante_movil` ya mide
la frescura de AWS y no la antiguedad del state, asi que el caso de §47 pasa tambien sin la excepcion. La excepcion
queda como historia, sin cambios: es mas estricta que el contrato general porque exige ademas el instante aprobado.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from scripts.terraform_datos.check_plan import ADDRESSES, PROVIDER, REGION, _sin_grupo_por_omision, _variables, require
from scripts.terraform_datos.check_plan_ejecutor import SALIDAS_EXISTENTES, _deriva, _desconocido
from scripts.terraform_datos.check_plan_recuperacion import _estado_previo
from scripts.terraform_datos.check_plan_refresh_instancia import VENTANA_MOVIL, _instante

MODULO = "module.alarmas_rds"
INSTANCIA = "blog-prod-postgres"
LIMITE_GRATUITO = 10
#: `latest_restorable_time` del state en serial 8, el unico instante que admite la excepcion puntual de §47.
EXCEPCION_VENTANA_MOVIL = "2026-10-05T19:16:49Z"

#: senal -> (metrica, estadistico, percentil, periodo, puntos, umbral, comparador). El mismo catalogo que
#: `terraform/modulos/alarmas_rds/main.tf`; una prueba exige que coincidan.
ALARMAS = {
    "cpu": ("CPUUtilization", "Average", None, 60, 5, 90, "GreaterThanThreshold"),
    "conexiones": ("DatabaseConnections", "Average", None, 60, 5, 100, "GreaterThanThreshold"),
    "memoria": ("FreeableMemory", "Average", None, 60, 15, 268435456, "LessThanThreshold"),
    "almacenamiento": ("FreeStorageSpace", "Minimum", None, 60, 5, 1073741824, "LessThanThreshold"),
    "xid": ("MaximumUsedTransactionIDs", "Average", None, 60, 1, 1000000000, "GreaterThanThreshold"),
    "lectura": ("ReadLatency", None, "p90", 60, 5, 0.02, "GreaterThanThreshold"),
    "escritura": ("WriteLatency", None, "p90", 60, 5, 0.02, "GreaterThanThreshold"),
    "creditos": ("CPUCreditBalance", "Minimum", None, 300, 3, 29, "LessThanThreshold"),
}
CRITICOS = ("alarm_name", "namespace", "metric_name", "dimensions", "statistic", "extended_statistic", "period",
            "evaluation_periods", "datapoints_to_alarm", "threshold", "comparison_operator", "treat_missing_data",
            "actions_enabled", "alarm_actions", "ok_actions", "insufficient_data_actions", "metric_query", "unit",
            "threshold_metric_id", "tags", "alarm_description")


def direccion(clave):
    return f'{MODULO}.aws_cloudwatch_metric_alarm.this["{clave}"]'


NUEVOS = {direccion(clave): clave for clave in ALARMAS}
SALIDA_NUEVA = "alarmas_de_rds"


def _alarma(cambio, clave):
    desconocido = cambio.get("after_unknown") or {}
    require(not any(_desconocido(desconocido.get(atributo)) for atributo in CRITICOS), "UNVERIFIABLE")
    metrica, estadistico, percentil, periodo, puntos, umbral, operador = ALARMAS[clave]
    a = cambio["after"]
    nombre = f"blog-prod-rds-{clave}"
    require(a.get("alarm_name") == nombre and a.get("namespace") == "AWS/RDS" and a.get("metric_name") == metrica
            and a.get("dimensions") == {"DBInstanceIdentifier": INSTANCIA}
            and a.get("statistic") == estadistico and a.get("extended_statistic") == percentil
            and a.get("period") == periodo and a.get("evaluation_periods") == puntos
            and a.get("datapoints_to_alarm") == puntos and a.get("threshold") == umbral
            and a.get("comparison_operator") == operador and a.get("treat_missing_data") == "missing"
            and a.get("unit") is None and a.get("threshold_metric_id") is None and not a.get("metric_query")
            and a.get("region") in (None, REGION) and a.get("tags") == {"Name": nombre}
            and isinstance(a.get("alarm_description"), str) and len(a["alarm_description"]) > 0, "ALARM")
    require(a.get("actions_enabled") is False and not a.get("alarm_actions") and not a.get("ok_actions")
            and not a.get("insufficient_data_actions"), "ALARM_ACTIONS")


def _cableado(plan):
    llamadas = plan["configuration"]["root_module"]["module_calls"]
    require("ejecutor_privado" not in llamadas, "WIRING")
    llamada = llamadas.get("alarmas_rds") or {}
    expresiones = llamada.get("expressions") or {}
    require(llamada.get("source") == "../terraform/modulos/alarmas_rds"
            and expresiones.get("identificador_de_la_instancia") == {
                "references": ["module.base_de_datos.identificador", "module.base_de_datos"]}
            and expresiones.get("nombre") == {"references": ["var.prefijo"]}, "WIRING")


def _salidas(plan):
    salidas = plan.get("output_changes") or {}
    declaradas = set(plan["configuration"]["root_module"].get("outputs") or {})
    require(set(salidas) == declaradas == SALIDAS_EXISTENTES | {SALIDA_NUEVA}, "OUTPUTS")
    for nombre in SALIDAS_EXISTENTES:
        dato = salidas[nombre]
        require(dato.get("actions") == ["no-op"] and dato.get("before") == dato.get("after"), "OUTPUTS")
    nueva = salidas[SALIDA_NUEVA]
    require(nueva.get("actions") == ["create"] and nueva.get("before") is None and not nueva.get("after_sensitive")
            and not nueva.get("after_unknown")
            and nueva.get("after") == {clave: f"blog-prod-rds-{clave}" for clave in ALARMAS}, "OUTPUTS")


def instante_excepcional(anterior, posterior, ahora):
    """Excepcion puntual de §47: el state EXACTAMENTE en el instante aprobado; AWS entre el y `ahora`, y con 24 h
    como maximo de antiguedad. Sustituye solo el limite de 24 h entre state y AWS."""
    a, b = _instante(anterior), _instante(posterior)
    require(a == _instante(EXCEPCION_VENTANA_MOVIL) and a <= b <= ahora and ahora - b <= VENTANA_MOVIL,
            "MOVING_ATTRIBUTE")
    return b - a


def _excepcion_aprobada(valor):
    try:
        return _instante(valor) == _instante(EXCEPCION_VENTANA_MOVIL)
    except ValueError:
        return False


def check(plan, account, arn_de_medios, ahora=None, alarmas_existentes_en_la_cuenta=0, excepcion_ventana_movil=None):
    ahora = ahora or datetime.now(timezone.utc)
    excepcion = excepcion_ventana_movil is not None
    require(not excepcion or _excepcion_aprobada(excepcion_ventana_movil), "MOVING_EXCEPTION")
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True, "APPLYABLE")
    require(plan.get("complete") is True and plan.get("errored") is False, "INCOMPLETE")
    _variables(plan, account, arn_de_medios)
    variables = plan["variables"]
    require(variables.get("version_de_la_contrasena", {}).get("value") == 1, "PASSWORD_VERSION")
    require(variables.get("dias_de_retencion_de_backups", {}).get("value") == 1, "RETENTION")
    require("zip_de_la_ejecutora" not in variables, "EXECUTOR_VARIABLE")
    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.operador") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")
    _sin_grupo_por_omision(plan)

    previos = _estado_previo(plan)
    require(set(previos) == ADDRESSES and not any(r.get("tainted") for r in previos.values()), "PRIOR_STATE")

    vistos, nuevos = set(), {}
    for item in plan.get("resource_changes", []):
        address, cambio = item["address"], item["change"]
        require(item.get("mode") == "managed" and item.get("provider_name") == PROVIDER and address not in vistos,
                "RESOURCE_SET")
        require(not cambio.get("importing") and not item.get("previous_address"), "IMPORT_MOVE")
        vistos.add(address)
        if address in ADDRESSES:
            require(cambio.get("actions") == ["no-op"] and cambio.get("before") == cambio.get("after"),
                    "EXISTING_CHANGED")
        elif address in NUEVOS:
            require(item.get("type") == "aws_cloudwatch_metric_alarm" and cambio.get("actions") == ["create"]
                    and cambio.get("before") is None, "NOT_CREATE")
            nuevos[address] = cambio
        else:
            raise ValueError("UNEXPECTED_RESOURCE")
    require(vistos == ADDRESSES | set(NUEVOS), "RESOURCE_SET")
    require(not plan.get("deferred_changes"), "DEFERRED")
    require(alarmas_existentes_en_la_cuenta + len(NUEVOS) <= LIMITE_GRATUITO, "FREE_TIER")

    for address, clave in NUEVOS.items():
        _alarma(nuevos[address], clave)
    _cableado(plan)
    _salidas(plan)
    deriva, movil = _deriva(plan, ahora, instante_excepcional) if excepcion else _deriva(plan, ahora)

    return {"gate": "ALARMS_PLAN_OK", "add": len(NUEVOS), "change": 0, "destroy": 0, "replace": 0,
            "deferred_changes": 0, "resource_drift": len(deriva), "drift_movil": movil,
            "excepcion_ventana_movil": EXCEPCION_VENTANA_MOVIL if excepcion and movil else None,
            "inventario": sorted(NUEVOS), "alarmas_tras_el_apply": alarmas_existentes_en_la_cuenta + len(NUEVOS),
            "salidas_nuevas": [SALIDA_NUEVA]}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--variables", required=True, type=Path,
                        help="JSON privado con expected_account_id, arn_del_bucket_de_medios y alarmas_existentes")
    parser.add_argument("--excepcion-ventana-movil",
                        help=f"Excepcion puntual de §47: solo admite {EXCEPCION_VENTANA_MOVIL}")
    args = parser.parse_args()
    try:
        raw = args.plan_json.read_bytes()
        privadas = json.loads(args.variables.read_text(encoding="utf-8"))
        result = check(json.loads(raw), privadas["expected_account_id"], privadas["arn_del_bucket_de_medios"],
                       alarmas_existentes_en_la_cuenta=privadas["alarmas_existentes"],
                       excepcion_ventana_movil=args.excepcion_ventana_movil)
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        codigo = str(error) if isinstance(error, ValueError) and str(error).isupper() else type(error).__name__
        raise SystemExit(f"plan de H-031-8 rechazado ({codigo}); inspect privately. No apply authorized.") from None
    print(json.dumps({"json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
