"""Gate offline del plan productivo de H-031-5 (Task/031): ejecutora privada de D-24. Nunca aplica.

Lista CERRADA. El plan es aceptable solo si:
- Terraform 1.16.2; `applyable`, `complete` y no `errored`: hay algo que aplicar y el plan esta completo.
- Variables del root como en H-031-3 (identidad, cuenta, region, prefijo, protecciones, red, etiquetas, sin
  endpoints alternativos y sin la variable efimera); contrasena en version 1; retencion 1 (plan FREE); y el
  artefacto declarado es EXACTAMENTE el pin de `empaquetar_ejecutor.py`.
- Todos los checks en `pass`, incluida la identidad.
- State previo: la linea base REAL tras H-031-9, sin taint. Por la decision del 2026-10-08, H-031-8 y H-031-9 se
  aplicaron antes que H-031-5: son 31 recursos (los 21 de H-031-3, las 8 alarmas y el rol de D-20 con su politica).
- Los 31 actuales en `no-op` con `before == after`: cero cambios.
- Los 4 nuevos, y nada mas, en `create`: grupo de logs, rol, su politica en linea y la funcion; sin import ni move.
- Funcion: Python 3.12, x86_64, handler `ejecutor.manejar`, 128 MB, 30 s, sin versiones publicadas, SIN
  concurrencia reservada (-1: D-24 modificada el 2026-10-18, aprobada el 2026-10-19), sin variables de entorno, capas ni KMS, el
  codigo del pin, y SOLO `sg-admin` en las dos subredes privadas del state previo, sin IPv6.
- Rol `PersonalBlogEjecutorDatos` con trust exacto de Lambda; politica en linea EXACTA (ENI de Lambda en VPC, su
  Deny desde el codigo y logs del grupo propio); grupo `/aws/lambda/blog-prod-ejecutor` con 14 dias.
- Cableado desde `module.red` (sg-admin y subredes) y grupo por omision sin uso.
- Sin diferidos; las 17 salidas actuales (las 15 de H-031-3, `alarmas_de_rds` y `rol_de_grafana`) en `no-op`;
  nuevas EXACTAMENTE `nombre_de_la_ejecutora` (conocida) y
  `arn_de_la_ejecutora` (desconocida hasta crear), ninguna sensible.
- `resource_drift` en el caso A (vacio) o B (solo `latest_restorable_time` de RDS, contrato movil de §40).
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from scripts.terraform_datos.check_plan import PROVIDER, REGION, _sin_grupo_por_omision, _variables, require
from scripts.terraform_datos.check_plan_recuperacion import INSTANCIA_RDS, _estado_previo
from scripts.terraform_datos.check_plan_refresh_instancia import MOVILES, instante_movil
from scripts.terraform_datos.empaquetar_ejecutor import SHA256_ESPERADO

MODULO = "module.ejecutor_privado"
LOGS = f"{MODULO}.aws_cloudwatch_log_group.this"
ROL = f"{MODULO}.aws_iam_role.this"
POLITICA = f"{MODULO}.aws_iam_role_policy.this"
FUNCION = f"{MODULO}.aws_lambda_function.this"
NUEVOS = {LOGS: "aws_cloudwatch_log_group", ROL: "aws_iam_role", POLITICA: "aws_iam_role_policy",
          FUNCION: "aws_lambda_function"}

NOMBRE = "blog-prod-ejecutor"
NOMBRE_DEL_ROL = "PersonalBlogEjecutorDatos"
GRUPO_DE_LOGS = f"/aws/lambda/{NOMBRE}"
RETENCION_DE_LOGS = 14

SALIDAS_EXISTENTES = frozenset({
    "id_de_vpc", "ids_de_subredes", "id_sg_lambda", "id_sg_admin", "id_sg_rds", "id_endpoint_s3", "prefix_list_s3",
    "endpoint_rds", "puerto_rds", "nombre_de_base", "identificador_rds", "arn_rds", "id_de_recurso_rds",
    "nombre_del_parametro_master", "grupo_de_logs_rds",
})
SALIDAS_NUEVAS = frozenset({"nombre_de_la_ejecutora", "arn_de_la_ejecutora"})

ACCIONES_DE_RED = ["ec2:AssignPrivateIpAddresses", "ec2:CreateNetworkInterface", "ec2:DeleteNetworkInterface",
                   "ec2:DescribeNetworkInterfaces", "ec2:DescribeSubnets", "ec2:UnassignPrivateIpAddresses"]
CONFIANZA = {
    "Version": "2012-10-17",
    "Statement": [{"Sid": "LambdaAsumeElRolDeLaEjecutora", "Effect": "Allow",
                   "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}],
}
CRITICOS_DE_LA_FUNCION = ("function_name", "runtime", "handler", "architectures", "memory_size", "timeout", "publish",
                          "package_type", "reserved_concurrent_executions", "source_code_hash", "environment",
                          "layers", "kms_key_arn")
#: Dentro de `vpc_config` solo se exige conocer lo que se verifica: `vpc_id` es calculado y legitimamente desconocido.
CRITICOS_DE_LA_RED = ("security_group_ids", "subnet_ids", "ipv6_allowed_for_dual_stack")


def permisos(account):
    """Politica en linea EXACTA de la ejecutora en H-031-5, para la cuenta verificada."""
    funcion = f"arn:aws:lambda:{REGION}:{account}:function:{NOMBRE}"
    grupo = f"arn:aws:logs:{REGION}:{account}:log-group:{GRUPO_DE_LOGS}"
    return {
        "Version": "2012-10-17",
        "Statement": [
            {"Sid": "InterfacesDeRedDeLambdaEnVpc", "Effect": "Allow", "Action": ACCIONES_DE_RED, "Resource": "*"},
            {"Sid": "SinApisDeEc2DesdeElCodigo", "Effect": "Deny",
             "Action": sorted(ACCIONES_DE_RED + ["ec2:DetachNetworkInterface"]), "Resource": "*",
             "Condition": {"ArnEquals": {"lambda:SourceFunctionArn": funcion}}},
            {"Sid": "RegistrosDeLaEjecutora", "Effect": "Allow", "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
             "Resource": f"{grupo}:log-stream:*"},
        ],
    }


def pin_base64():
    return base64.b64encode(bytes.fromhex(SHA256_ESPERADO)).decode()


def _desconocido(valor):
    return valor is True or (isinstance(valor, list) and any(_desconocido(v) for v in valor)) or (
        isinstance(valor, dict) and any(_desconocido(v) for v in valor.values()))


def _verificable(cambio, claves):
    desconocido = cambio.get("after_unknown") or {}
    require(not any(_desconocido(desconocido.get(clave)) for clave in claves), "UNVERIFIABLE")


def _funcion(cambio, subredes, sg_admin):
    _verificable(cambio, CRITICOS_DE_LA_FUNCION)
    red_desconocida = (cambio.get("after_unknown") or {}).get("vpc_config")
    require(red_desconocida is not True and not (isinstance(red_desconocida, list) and any(
        _desconocido((bloque or {}).get(clave)) for bloque in red_desconocida for clave in CRITICOS_DE_LA_RED)),
        "UNVERIFIABLE")
    a = cambio["after"]
    require(a.get("function_name") == NOMBRE and a.get("runtime") == "python3.12"
            and a.get("handler") == "ejecutor.manejar" and a.get("architectures") == ["x86_64"]
            and a.get("memory_size") == 128 and a.get("timeout") == 30 and a.get("publish") is False
            and a.get("package_type") == "Zip", "FUNCTION")
    require(not a.get("layers") and a.get("kms_key_arn") is None and a.get("image_uri") is None
            and a.get("s3_bucket") is None and a.get("code_signing_config_arn") is None
            and not a.get("file_system_config") and not a.get("dead_letter_config") and not a.get("image_config")
            and not a.get("snap_start"), "FUNCTION")
    # D-24, modificada el 2026-10-18 (aprobada el 2026-10-19): -1, el valor nativo SIN reserva. Ni 0 (la apagaria) ni una reserva.
    concurrencia = a.get("reserved_concurrent_executions")
    require(type(concurrencia) is int and concurrencia == -1, "CONCURRENCY")
    require(a.get("source_code_hash") == pin_base64(), "ARTIFACT_PIN")
    require(a.get("environment") in ([], None), "ENVIRONMENT")
    red = a.get("vpc_config")
    require(isinstance(red, list) and len(red) == 1, "NETWORK")
    red = red[0]
    require(red.get("ipv6_allowed_for_dual_stack") is False and red.get("security_group_ids") == [sg_admin]
            and sorted(red.get("subnet_ids") or []) == sorted(subredes), "NETWORK")
    require(a.get("tags") == {"Name": NOMBRE}, "TAGS")


def _rol(cambio):
    _verificable(cambio, ("name", "path", "assume_role_policy", "permissions_boundary", "max_session_duration"))
    a = cambio["after"]
    require(a.get("name") == NOMBRE_DEL_ROL and a.get("path") == "/" and a.get("max_session_duration") == 3600
            and a.get("permissions_boundary") is None and a.get("force_detach_policies") in (False, None)
            and not a.get("managed_policy_arns"), "ROLE")
    require(json.loads(a.get("assume_role_policy") or "null") == CONFIANZA, "TRUST")
    require(a.get("tags") == {"Name": NOMBRE_DEL_ROL}, "TAGS")


def _politica(cambio, account):
    _verificable(cambio, ("name", "policy"))
    a = cambio["after"]
    require(a.get("name") == f"{NOMBRE_DEL_ROL}-ejecucion"
            and json.loads(a.get("policy") or "null") == permisos(account), "POLICY")


def _logs(cambio):
    _verificable(cambio, ("name", "retention_in_days", "kms_key_id"))
    a = cambio["after"]
    retencion = a.get("retention_in_days")
    require(a.get("name") == GRUPO_DE_LOGS and type(retencion) is int and retencion == RETENCION_DE_LOGS
            and a.get("kms_key_id") is None and a.get("skip_destroy") in (False, None), "LOGS")
    require(a.get("tags") == {"Name": NOMBRE}, "TAGS")


def _cableado(plan):
    """Desde la seccion `configuration`, que conserva las referencias reales entre recursos."""
    llamadas = plan["configuration"]["root_module"]["module_calls"]
    llamada = llamadas.get("ejecutor_privado") or {}
    expresiones = llamada.get("expressions") or {}
    require(expresiones.get("id_sg_admin") == {"references": ["module.red.id_sg_admin", "module.red"]}
            and expresiones.get("ids_de_subredes") == {"references": ["module.red.ids_de_subredes", "module.red"]},
            "WIRING")
    salida = (llamadas["red"]["module"].get("outputs") or {}).get("id_sg_admin") or {}
    require(salida.get("expression") == {"references": ["aws_security_group.admin.id", "aws_security_group.admin"]},
            "WIRING")
    recursos = {r["address"]: r.get("expressions") or {} for r in (llamada.get("module") or {}).get("resources", [])}
    require(set(recursos) == {"aws_cloudwatch_log_group.this", "aws_iam_role.this", "aws_iam_role_policy.this",
                              "aws_lambda_function.this"}, "WIRING")
    funcion = recursos["aws_lambda_function.this"]
    red = funcion.get("vpc_config")
    require(isinstance(red, list) and len(red) == 1
            and red[0].get("security_group_ids") == {"references": ["var.id_sg_admin"]}
            and red[0].get("subnet_ids") == {"references": ["var.ids_de_subredes"]}, "WIRING")
    require((funcion.get("role") or {}).get("references", [])[:1] == ["aws_iam_role.this.arn"], "WIRING")
    politica = recursos["aws_iam_role_policy.this"]
    require((politica.get("role") or {}).get("references", [])[:1] == ["aws_iam_role.this.id"], "WIRING")


def _salidas(plan, previas):
    salidas = plan.get("output_changes") or {}
    declaradas = set(plan["configuration"]["root_module"].get("outputs") or {})
    require(set(salidas) == declaradas == previas | SALIDAS_NUEVAS, "OUTPUTS")
    for nombre in previas:
        dato = salidas[nombre]
        require(dato.get("actions") == ["no-op"] and dato.get("before") == dato.get("after"), "OUTPUTS")
    for nombre in SALIDAS_NUEVAS:
        dato = salidas[nombre]
        require(dato.get("actions") == ["create"] and dato.get("before") is None
                and not dato.get("after_sensitive"), "OUTPUTS")
    require(salidas["nombre_de_la_ejecutora"].get("after") == NOMBRE
            and not salidas["nombre_de_la_ejecutora"].get("after_unknown"), "OUTPUTS")
    require(salidas["arn_de_la_ejecutora"].get("after_unknown") is True, "OUTPUTS")


def _deriva(plan, ahora, comprobar=instante_movil):
    """Caso A: vacio. Caso B: solo `latest_restorable_time` de la instancia, con el contrato movil de §40.
    `comprobar` solo lo sustituye la guarda de H-031-8, con la excepcion puntual de §47."""
    deriva = plan.get("resource_drift") or []
    movil = []
    if deriva:
        require(len(deriva) == 1, "DRIFT")
        entrada = deriva[0]
        cambio = entrada.get("change", {})
        require(entrada.get("address") == INSTANCIA_RDS and entrada.get("type") == "aws_db_instance"
                and entrada.get("mode") == "managed" and entrada.get("provider_name") == PROVIDER
                and not entrada.get("previous_address") and not cambio.get("importing")
                and cambio.get("actions") == ["update"] and not _desconocido(cambio.get("after_unknown") or {}),
                "DRIFT")
        antes, despues = cambio.get("before") or {}, cambio.get("after") or {}
        distintos = {k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k)}
        require(distintos and distintos <= MOVILES, "DRIFT")
        for atributo in sorted(distintos):
            comprobar(antes.get(atributo), despues.get(atributo), ahora)
            movil.append(f"{INSTANCIA_RDS}: {atributo}")
    return deriva, movil


def _linea_base():
    """Recursos y salidas de produccion tras H-031-9. Importacion diferida: las guardas de alarmas y de D-20 importan
    de esta, y a nivel de modulo seria un ciclo."""
    from scripts.terraform_datos.check_plan_convergencia import FASES
    from scripts.terraform_datos.check_plan_grafana import SALIDA_NUEVA, SALIDAS_EXISTENTES as SALIDAS_DE_H0318

    return FASES["h0319"], SALIDAS_DE_H0318 | {SALIDA_NUEVA}


def check(plan, account, arn_de_medios, ahora=None):
    ahora = ahora or datetime.now(timezone.utc)
    previos_esperados, salidas_previas = _linea_base()
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True, "APPLYABLE")
    require(plan.get("complete") is True and plan.get("errored") is False, "INCOMPLETE")
    _variables(plan, account, arn_de_medios)
    variables = plan["variables"]
    require(variables.get("version_de_la_contrasena", {}).get("value") == 1, "PASSWORD_VERSION")
    require(variables.get("dias_de_retencion_de_backups", {}).get("value") == 1, "RETENTION")
    artefacto = variables.get("zip_de_la_ejecutora", {}).get("value") or {}
    require(artefacto.get("sha256") == SHA256_ESPERADO and str(artefacto.get("ruta", "")).endswith(".zip"),
            "ARTIFACT_PIN")
    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.operador") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")
    _sin_grupo_por_omision(plan)

    previos = _estado_previo(plan)
    require(set(previos) == previos_esperados and not any(r.get("tainted") for r in previos.values()),
            "PRIOR_STATE")
    subredes = [previos[f'module.red.aws_subnet.privada["{clave}"]']["values"]["id"] for clave in ("a", "b")]
    sg_admin = previos["module.red.aws_security_group.admin"]["values"]["id"]

    vistos, nuevos = set(), {}
    for item in plan.get("resource_changes", []):
        address, cambio = item["address"], item["change"]
        require(item.get("mode") == "managed" and item.get("provider_name") == PROVIDER and address not in vistos,
                "RESOURCE_SET")
        require(not cambio.get("importing") and not item.get("previous_address"), "IMPORT_MOVE")
        vistos.add(address)
        if address in previos_esperados:
            require(cambio.get("actions") == ["no-op"] and cambio.get("before") == cambio.get("after"),
                    "EXISTING_CHANGED")
        elif address in NUEVOS:
            require(item.get("type") == NUEVOS[address] and cambio.get("actions") == ["create"]
                    and cambio.get("before") is None, "NOT_CREATE")
            nuevos[address] = cambio
        else:
            raise ValueError("UNEXPECTED_RESOURCE")
    require(vistos == previos_esperados | set(NUEVOS), "RESOURCE_SET")
    require(not plan.get("deferred_changes"), "DEFERRED")

    _funcion(nuevos[FUNCION], subredes, sg_admin)
    _rol(nuevos[ROL])
    _politica(nuevos[POLITICA], account)
    _logs(nuevos[LOGS])
    _cableado(plan)
    _salidas(plan, salidas_previas)
    deriva, movil = _deriva(plan, ahora)

    return {"gate": "EXECUTOR_PLAN_OK", "estado_previo": len(previos_esperados), "add": len(NUEVOS), "change": 0, "destroy": 0, "replace": 0,
            "deferred_changes": 0, "resource_drift": len(deriva), "drift_movil": movil,
            "inventario": sorted(NUEVOS), "salidas_nuevas": sorted(SALIDAS_NUEVAS)}


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
        raise SystemExit(f"plan de H-031-5 rechazado ({codigo}); inspect privately. No apply authorized.") from None
    print(json.dumps({"json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
