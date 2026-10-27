"""Segundo plan del root de datos que emitio el laboratorio el 2026-10-19, con H-031-5 a H-031-9 y H-031-6 cableados.

Ciclo completo contra Floci 2.1.0 (RDS en modo `mock`), Terraform 1.16.2 y el provider AWS 6.64.0. El ciclo se
detuvo en la idempotencia del root de datos: el gate leyo entradas que nadie habia declarado desde H-031-1A,
porque los recursos de H-031-8, H-031-9, H-031-5 y H-031-6 nunca habian pasado un ciclo completo.

Extiende la estructura de H-031-1A (`drift_observado.py`) con lo que el root anadio despues, tal como salio en el JSON
real:
- `resource_drift`:
  - las 8 alarmas de D-11, con sus tres listas de acciones de `null` a `[]`;
  - el rol de la ejecutora, con `inline_policy` de `[]` al reflejo EXACTO de sus DOS politicas en linea del state
    (`-ejecucion` y `-exportacion`);
  - la funcion, con `layers` de `null` a `[]`;
  - el rol de Grafana, con el reflejo de su politica y `tags` de `null` a `{}`;
  - `sg-admin`, que ahora refleja DOS reglas separadas: RDS y S3, la de `export`.
- `resource_changes`:
  - `datapoints_to_alarm` (de 0 a N) en las 8 alarmas, y `extended_statistic` en las dos p90, que Floci no devuelve
    (demostrado con `DescribeAlarms` directo contra el emulador);
  - los dos SecureString nuevos, con las mismas diferencias `key_id` y `tier` que la master.

Desde Floci 2.3.0 (ciclo del 2026-10-24) el emulador ya devuelve `DatapointsToAlarm` y el `KeyId`/`Tier` de SSM:
en `resource_changes` solo queda `extended_statistic`, en las dos alarmas de percentil.

Los ID son sinteticos; no hay Account ID, contrasena ni valor de una ejecucion concreta. No es un archivo de pruebas.
"""

from __future__ import annotations

import copy
import json
from typing import Any

import drift_observado as base

SENALES = ("almacenamiento", "conexiones", "cpu", "creditos", "escritura", "lectura", "memoria", "xid")
PERCENTILES = ("escritura", "lectura")
PUNTOS = {"almacenamiento": 5, "conexiones": 5, "cpu": 5, "creditos": 3, "escritura": 5, "lectura": 5,
          "memoria": 15, "xid": 1}
ALARMA = 'module.alarmas_rds.aws_cloudwatch_metric_alarm.this["{}"]'
ROL_EJECUTORA = "module.ejecutor_privado.aws_iam_role.this"
FUNCION = "module.ejecutor_privado.aws_lambda_function.this"
ROL_GRAFANA = "module.lectura_grafana.aws_iam_role.this"
SSM_NUEVOS = ("module.credenciales_sql.aws_ssm_parameter.blog_migrate",
              "module.credenciales_sql.aws_ssm_parameter.blog_app")
NOMBRE_EJECUTORA, NOMBRE_GRAFANA = "PersonalBlogEjecutorDatos", "PersonalBlogLecturaGrafana"


def _documento(sid: str, accion: str) -> str:
    return json.dumps({"Version": "2012-10-17",
                       "Statement": [{"Sid": sid, "Effect": "Allow", "Action": accion, "Resource": "*"}]})


#: Las politicas en linea del state, por rol. Contenido sintetico; la forma es la del provider.
POLITICAS = {
    "module.ejecutor_privado.aws_iam_role_policy.this": (NOMBRE_EJECUTORA, "PersonalBlogEjecutorDatos-ejecucion",
                                                         _documento("Ejecucion", "logs:PutLogEvents")),
    "module.exportacion.aws_iam_role_policy.this": (NOMBRE_EJECUTORA, "PersonalBlogEjecutorDatos-exportacion",
                                                    _documento("Exportacion", "s3:PutObject")),
    "module.lectura_grafana.aws_iam_role_policy.this": (NOMBRE_GRAFANA, "PersonalBlogLecturaGrafana-lectura",
                                                        _documento("Lectura", "cloudwatch:GetMetricData")),
}

REGLA_ADMIN_A_S3 = base.regla_separada(
    "admin_a_s3", "egress", grupo=base.SG_ADMIN,
    descripcion="HTTPS hacia S3 por el gateway endpoint (modo export de D-24)", puerto=443,
    lista=base.LISTA_DE_PREFIJOS_S3,
)
REGLA_ADMIN_A_S3["address"] = "module.exportacion.aws_vpc_security_group_egress_rule.admin_a_s3"


def politica_previa(direccion: str) -> dict[str, Any]:
    rol, nombre, documento = POLITICAS[direccion]
    return {"address": direccion, "mode": "managed", "type": "aws_iam_role_policy", "name": "this",
            "values": {"id": f"{rol}:{nombre}", "name": nombre, "name_prefix": "", "policy": documento,
                       "role": rol}}


def reflejo(rol: str) -> list[dict[str, str]]:
    """Como `aws_iam_role` representa sus politicas en linea en `inline_policy`."""
    return [{"name": nombre, "policy": documento} for r, nombre, documento in POLITICAS.values() if r == rol]


def _rol(nombre: str, *, inline_policy: Any, tags: Any) -> dict[str, Any]:
    return {"id": nombre, "name": nombre, "path": "/", "max_session_duration": 3600,
            "inline_policy": inline_policy, "managed_policy_arns": [], "tags": tags}


def _drift_nuevo() -> list[dict[str, Any]]:
    entradas = []
    for senal in SENALES:
        comun = {"id": f"blog-lab-rds-{senal}", "alarm_name": f"blog-lab-rds-{senal}", "actions_enabled": False}
        nulas = {"alarm_actions": None, "insufficient_data_actions": None, "ok_actions": None}
        vacias = {"alarm_actions": [], "insufficient_data_actions": [], "ok_actions": []}
        entradas.append(base._entrada(ALARMA.format(senal), "aws_cloudwatch_metric_alarm",
                                      {**comun, **nulas}, {**comun, **vacias}))
    entradas.append(base._entrada(
        ROL_EJECUTORA, "aws_iam_role",
        _rol(NOMBRE_EJECUTORA, inline_policy=[], tags={"Name": NOMBRE_EJECUTORA}),
        _rol(NOMBRE_EJECUTORA, inline_policy=reflejo(NOMBRE_EJECUTORA), tags={"Name": NOMBRE_EJECUTORA})))
    funcion = {"id": "blog-lab-ejecutor", "function_name": "blog-lab-ejecutor", "timeout": 30}
    entradas.append(base._entrada(FUNCION, "aws_lambda_function", {**funcion, "layers": None},
                                  {**funcion, "layers": []}))
    entradas.append(base._entrada(
        ROL_GRAFANA, "aws_iam_role",
        _rol(NOMBRE_GRAFANA, inline_policy=[], tags=None),
        _rol(NOMBRE_GRAFANA, inline_policy=reflejo(NOMBRE_GRAFANA), tags={})))
    return entradas


def _cambios_nuevos() -> list[dict[str, Any]]:
    return [base._entrada(ALARMA.format(senal), "aws_cloudwatch_metric_alarm", {"extended_statistic": None},
                          {"extended_statistic": "p90"}) for senal in PERCENTILES]


def plan_de_datos_observado() -> dict[str, Any]:
    """Copia nueva del segundo plan observado el 2026-10-19; cada prueba puede mutarla."""
    plan = base.plan_de_datos_observado()
    admin = base.entrada(plan, base.GRUPO_ADMIN)["change"]["after"]
    admin["egress"].append(base.regla_en_linea("HTTPS hacia S3 por el gateway endpoint (modo export de D-24)", 443,
                                               lista=base.LISTA_DE_PREFIJOS_S3))
    plan["resource_drift"] += _drift_nuevo()
    plan["resource_changes"] += _cambios_nuevos()
    hijos = plan["prior_state"]["values"]["root_module"]["child_modules"]
    hijos.append({"address": "module.exportacion",
                  "resources": [REGLA_ADMIN_A_S3, politica_previa("module.exportacion.aws_iam_role_policy.this")]})
    hijos.append({"address": "module.ejecutor_privado",
                  "resources": [politica_previa("module.ejecutor_privado.aws_iam_role_policy.this")]})
    hijos.append({"address": "module.lectura_grafana",
                  "resources": [politica_previa("module.lectura_grafana.aws_iam_role_policy.this")]})
    return copy.deepcopy(plan)


def entrada(plan: dict[str, Any], direccion: str) -> dict[str, Any]:
    return base.entrada(plan, direccion)
