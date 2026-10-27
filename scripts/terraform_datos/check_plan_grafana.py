"""Gate offline del plan productivo de H-031-9 (Task/031): rol de D-20 para Grafana Cloud. Nunca aplica.

Solo despues de H-031-8 aplicado y convergente, y con el gate de D-19 registrado. Lista CERRADA. El plan es aceptable
solo si:
- Terraform 1.16.2; `applyable`, `complete` y no `errored`; variables del root como en H-031-3, contrasena en
  version 1, retencion 1, sin la variable del artefacto de la ejecutora, y `integracion_grafana` IGUAL a la cuenta
  de Grafana y al ExternalId que muestra el stack (los da el archivo privado del destino); checks en `pass`.
- State previo: los 21 recursos de H-031-3 y las 8 alarmas de H-031-8, sin taint; los 29 en `no-op`.
- EXACTAMENTE 2 `create`: el rol `PersonalBlogLecturaGrafana` y su politica en linea. Nada mas.
- Rol: path `/`, sesion maxima 3600 s, sin limite de permisos, sin politicas administradas y con la descripcion de
  D-20. Confianza EXACTA: solo la cuenta de Grafana y solo con `sts:ExternalId` igual al del stack.
- Politica EXACTA: `cloudwatch:GetMetricData` y `cloudwatch:ListMetrics` en us-east-2, y `cloudwatch:DescribeAlarms`
  solo sobre las alarmas `blog-prod-*`. Sin logs ni ninguna escritura.
- Cableado: la cuenta sale de la identidad verificada; la cuenta de Grafana y el ExternalId, de la variable; la
  ejecutora sigue fuera del root.
- Sin diferidos; las 16 salidas actuales en `no-op` y una nueva, `rol_de_grafana`, con el NOMBRE: ninguna salida
  lleva un ARN con la cuenta.
- `resource_drift` en el caso A o B (solo `latest_restorable_time`, contrato movil de §40).
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from scripts.terraform_datos.check_plan import ADDRESSES, PROVIDER, REGION, _sin_grupo_por_omision, _variables, require
from scripts.terraform_datos.check_plan_alarmas import NUEVOS as ALARMAS, SALIDA_NUEVA as SALIDA_DE_ALARMAS
from scripts.terraform_datos.check_plan_ejecutor import SALIDAS_EXISTENTES as SALIDAS_DE_H0313, _deriva, _desconocido
from scripts.terraform_datos.check_plan_recuperacion import _estado_previo

MODULO = "module.lectura_grafana"
ROL = f"{MODULO}.aws_iam_role.this"
POLITICA = f"{MODULO}.aws_iam_role_policy.this"
NUEVOS = {ROL: "aws_iam_role", POLITICA: "aws_iam_role_policy"}
PREVIOS = frozenset(ADDRESSES | set(ALARMAS))
NOMBRE_DEL_ROL = "PersonalBlogLecturaGrafana"
DESCRIPCION = "D-20: lectura de metricas y estados de alarma de CloudWatch para Grafana Cloud. Sin logs ni escritura."
PREFIJO = "blog-prod"
SALIDAS_EXISTENTES = frozenset(SALIDAS_DE_H0313 | {SALIDA_DE_ALARMAS})
SALIDA_NUEVA = "rol_de_grafana"


def confianza(cuenta_de_grafana, external_id):
    """Confianza EXACTA de D-20: la de la plantilla del modulo, para la cuenta de Grafana y el ExternalId del stack."""
    return {"Version": "2012-10-17", "Statement": [{
        "Sid": "GrafanaCloudConExternalId", "Effect": "Allow",
        "Principal": {"AWS": f"arn:aws:iam::{cuenta_de_grafana}:root"}, "Action": "sts:AssumeRole",
        "Condition": {"StringEquals": {"sts:ExternalId": external_id}}}]}


def permisos(account):
    """Politica EXACTA de D-20 para la cuenta verificada."""
    region = {"StringEquals": {"aws:RequestedRegion": REGION}}
    return {"Version": "2012-10-17", "Statement": [
        {"Sid": "MetricasSoloLectura", "Effect": "Allow",
         "Action": ["cloudwatch:GetMetricData", "cloudwatch:ListMetrics"], "Resource": "*", "Condition": region},
        {"Sid": "EstadosDeLasAlarmasDelProyecto", "Effect": "Allow", "Action": "cloudwatch:DescribeAlarms",
         "Resource": f"arn:aws:cloudwatch:{REGION}:{account}:alarm:{PREFIJO}-*", "Condition": region},
    ]}


def _rol(cambio, cuenta_de_grafana, external_id):
    desconocido = cambio.get("after_unknown") or {}
    require(not any(_desconocido(desconocido.get(clave)) for clave in (
        "name", "path", "assume_role_policy", "permissions_boundary", "max_session_duration", "description")),
        "UNVERIFIABLE")
    a = cambio["after"]
    require(a.get("name") == NOMBRE_DEL_ROL and a.get("path") == "/" and a.get("max_session_duration") == 3600
            and a.get("permissions_boundary") is None and a.get("force_detach_policies") in (False, None)
            and not a.get("managed_policy_arns") and a.get("description") == DESCRIPCION
            and a.get("tags") in (None, {}), "ROLE")
    require(json.loads(a.get("assume_role_policy") or "null") == confianza(cuenta_de_grafana, external_id), "TRUST")


def _politica(cambio, account):
    desconocido = cambio.get("after_unknown") or {}
    require(not any(_desconocido(desconocido.get(clave)) for clave in ("name", "policy")), "UNVERIFIABLE")
    a = cambio["after"]
    require(a.get("name") == f"{NOMBRE_DEL_ROL}-lectura"
            and json.loads(a.get("policy") or "null") == permisos(account), "POLICY")


def _cableado(plan):
    llamadas = plan["configuration"]["root_module"]["module_calls"]
    require("ejecutor_privado" not in llamadas, "WIRING")
    llamada = llamadas.get("lectura_grafana") or {}
    e = llamada.get("expressions") or {}
    require(llamada.get("source") == "../terraform/modulos/lectura_grafana"
            and e.get("nombre_del_rol") == {"constant_value": NOMBRE_DEL_ROL}
            and e.get("cuenta") == {"references": ["data.aws_caller_identity.operador.account_id",
                                                   "data.aws_caller_identity.operador"]}
            and e.get("region") == {"references": ["var.region"]} and e.get("prefijo") == {"references": ["var.prefijo"]}
            and e.get("cuenta_de_grafana") == {"references": ["var.integracion_grafana.cuenta",
                                                              "var.integracion_grafana"]}
            and e.get("external_id") == {"references": ["var.integracion_grafana.external_id",
                                                        "var.integracion_grafana"]}, "WIRING")


def _salidas(plan):
    salidas = plan.get("output_changes") or {}
    declaradas = set(plan["configuration"]["root_module"].get("outputs") or {})
    require(set(salidas) == declaradas == SALIDAS_EXISTENTES | {SALIDA_NUEVA}, "OUTPUTS")
    for nombre in SALIDAS_EXISTENTES:
        dato = salidas[nombre]
        require(dato.get("actions") == ["no-op"] and dato.get("before") == dato.get("after"), "OUTPUTS")
    nueva = salidas[SALIDA_NUEVA]
    require(nueva.get("actions") == ["create"] and nueva.get("before") is None and not nueva.get("after_sensitive")
            and not nueva.get("after_unknown") and nueva.get("after") == NOMBRE_DEL_ROL, "OUTPUTS")


def check(plan, account, arn_de_medios, cuenta_de_grafana, external_id, ahora=None):
    ahora = ahora or datetime.now(timezone.utc)
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True, "APPLYABLE")
    require(plan.get("complete") is True and plan.get("errored") is False, "INCOMPLETE")
    _variables(plan, account, arn_de_medios)
    variables = plan["variables"]
    require(variables.get("version_de_la_contrasena", {}).get("value") == 1, "PASSWORD_VERSION")
    require(variables.get("dias_de_retencion_de_backups", {}).get("value") == 1, "RETENTION")
    require("zip_de_la_ejecutora" not in variables, "EXECUTOR_VARIABLE")
    require(variables.get("integracion_grafana", {}).get("value") == {
        "cuenta": cuenta_de_grafana, "external_id": external_id}, "GRAFANA")
    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.operador") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")
    _sin_grupo_por_omision(plan)

    previos = _estado_previo(plan)
    require(set(previos) == PREVIOS and not any(r.get("tainted") for r in previos.values()), "PRIOR_STATE")

    vistos, nuevos = set(), {}
    for item in plan.get("resource_changes", []):
        address, cambio = item["address"], item["change"]
        require(item.get("mode") == "managed" and item.get("provider_name") == PROVIDER and address not in vistos,
                "RESOURCE_SET")
        require(not cambio.get("importing") and not item.get("previous_address"), "IMPORT_MOVE")
        vistos.add(address)
        if address in PREVIOS:
            require(cambio.get("actions") == ["no-op"] and cambio.get("before") == cambio.get("after"),
                    "EXISTING_CHANGED")
        elif address in NUEVOS:
            require(item.get("type") == NUEVOS[address] and cambio.get("actions") == ["create"]
                    and cambio.get("before") is None, "NOT_CREATE")
            nuevos[address] = cambio
        else:
            raise ValueError("UNEXPECTED_RESOURCE")
    require(vistos == PREVIOS | set(NUEVOS), "RESOURCE_SET")
    require(not plan.get("deferred_changes"), "DEFERRED")

    _rol(nuevos[ROL], cuenta_de_grafana, external_id)
    _politica(nuevos[POLITICA], account)
    _cableado(plan)
    _salidas(plan)
    deriva, movil = _deriva(plan, ahora)

    return {"gate": "GRAFANA_ROLE_PLAN_OK", "add": len(NUEVOS), "change": 0, "destroy": 0, "replace": 0,
            "deferred_changes": 0, "resource_drift": len(deriva), "drift_movil": movil,
            "inventario": sorted(NUEVOS), "salidas_nuevas": [SALIDA_NUEVA]}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--variables", required=True, type=Path,
                        help="JSON privado con expected_account_id, arn_del_bucket_de_medios y integracion_grafana")
    args = parser.parse_args()
    try:
        raw = args.plan_json.read_bytes()
        privadas = json.loads(args.variables.read_text(encoding="utf-8"))
        grafana = privadas["integracion_grafana"]
        result = check(json.loads(raw), privadas["expected_account_id"], privadas["arn_del_bucket_de_medios"],
                       grafana["cuenta"], grafana["external_id"])
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        codigo = str(error) if isinstance(error, ValueError) and str(error).isupper() else type(error).__name__
        raise SystemExit(f"plan de H-031-9 rechazado ({codigo}); inspect privately. No apply authorized.") from None
    print(json.dumps({"json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
