"""Guarda cerrada de H-031-6: 35 existentes, cuatro altas y solo el codigo de Lambda en sitio.

No aplica ni llama a AWS. Las contrasenas efimeras se vuelven a entregar al aplicar el plan guardado;
el plan nunca las custodia. Solo se admite el drift movil de §40, aprobado el 2026-10-19.
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from scripts.terraform_datos.check_plan import ETIQUETAS, PROVIDER, REGION, _variables, require, _sin_grupo_por_omision
from scripts.terraform_datos.check_plan_ejecutor import (
    FUNCION, _cableado, _deriva, _desconocido, _linea_base, SALIDAS_NUEVAS,
)
from scripts.terraform_datos.check_plan_recuperacion import _estado_previo
from scripts.terraform_datos.empaquetar_ejecutor import SHA256_ESPERADO, SHA256_ESPERADO_H0316

DESCRIPCION_DE_LA_FUNCION = "Ejecutora privada de administracion de datos (D-24)."
CREDENCIALES = {
    "blog_migrate": ("/blog-prod/datos/blog_migrate",
                     "Contrasena de blog_migrate: migraciones, purga y export por la ejecutora de D-24 (D-23).",
                     "blog-prod-blog-migrate"),
    "blog_app": ("/blog-prod/datos/blog_app", "Contrasena de blog_app: la aplicacion en Lambda, solo DML (D-23).",
                 "blog-prod-blog-app"),
}
POLITICA_DE_EXPORT = "module.exportacion.aws_iam_role_policy.this"
REGLA_DE_EXPORT = "module.exportacion.aws_vpc_security_group_egress_rule.admin_a_s3"
SALIDA_NUEVA = "nombres_de_credenciales_sql"
NUEVOS = {**{f"module.credenciales_sql.aws_ssm_parameter.{c}": "aws_ssm_parameter" for c in CREDENCIALES},
          POLITICA_DE_EXPORT: "aws_iam_role_policy", REGLA_DE_EXPORT: "aws_vpc_security_group_egress_rule"}
EFIMERAS = ("contrasena_master", "contrasena_blog_migrate", "contrasena_blog_app")
CALCULADOS_FUNCION = {"last_modified", "code_sha256", "source_code_size"}


def politica_de_exportacion(arn, vpce):
    return {"Version": "2012-10-17", "Statement": [{
        "Sid": "EscrituraCondicionalEnElPrefijoDeExportacion", "Effect": "Allow", "Action": "s3:PutObject",
        "Resource": f"{arn}/exportaciones/*",
        "Condition": {"StringEquals": {"s3:if-none-match": "*", "aws:SourceVpce": vpce}},
    }]}


def _sin_secretos(plan):
    require(not set(EFIMERAS) & set(plan.get("variables") or {}), "EPHEMERAL_LEAK")
    # Inspeccionar tambien prior_state/planned_values, no solo resource_changes. Los marcadores de
    # sensibilidad/desconocimiento son booleanos, no valores. Nunca incluir el dato en la excepcion.
    def visitar(nodo, metadatos=False):
        if isinstance(nodo, dict):
            for clave, valor in nodo.items():
                if not metadatos and clave in {"password", "password_wo", "value_wo", "insecure_value"}:
                    require(valor is None, "SECRET_IN_PLAN")
                visitar(valor, metadatos or clave in {"after_unknown", "after_sensitive", "before_sensitive",
                                                      "sensitive_values", "expressions", "configuration"})
        elif isinstance(nodo, list):
            for valor in nodo:
                visitar(valor, metadatos)
    visitar(plan)
    def ssm(nodo):
        if isinstance(nodo, dict):
            if nodo.get("type") == "aws_ssm_parameter":
                for valores in [nodo.get("values") or {}, *[(nodo.get("change") or {}).get(k) or {}
                                                          for k in ("before", "after")]]:
                    # Con `value_wo`, el provider deja `value` como la cadena VACIA en el state (forma real del
                    # plan de H-031-5, 2026-10-19), igual que admite `check_plan`. Cualquier otro valor es un secreto.
                    require(all(valores.get(k) is None for k in ("value_wo", "insecure_value"))
                            and valores.get("value") in (None, ""), "SECRET_IN_PLAN")
            for valor in nodo.values():
                ssm(valor)
        elif isinstance(nodo, list):
            for valor in nodo:
                ssm(valor)
    ssm(plan)


def _exacto(cambio, esperado, calculados, codigo):
    unknown = cambio.get("after_unknown") or {}
    require(isinstance(unknown, dict) and all(k in calculados or not _desconocido(v)
                                             for k, v in unknown.items()), "UNVERIFIABLE")
    after = cambio.get("after") or {}
    require(set(after) <= set(esperado) | calculados, codigo)
    require(all(after.get(k) == v for k, v in esperado.items()), codigo)
    require(all(after.get(k) is None for k in calculados), codigo)


def _actualizar_funcion(cambio, previo, artefacto):
    antes, despues = cambio.get("before") or {}, cambio.get("after") or {}
    require(cambio.get("actions") == ["update"] and antes == previo["values"]
            and not cambio.get("replace_paths"), "FUNCTION_UPDATE")
    require(antes.get("source_code_hash") == base64.b64encode(bytes.fromhex(SHA256_ESPERADO)).decode(),
            "ARTIFACT_PIN")
    unknown = cambio.get("after_unknown") or {}
    require(isinstance(unknown, dict) and all(k in CALCULADOS_FUNCION or not _desconocido(v)
                                             for k, v in unknown.items()), "UNVERIFIABLE")
    require(despues.get("source_code_hash") == base64.b64encode(bytes.fromhex(SHA256_ESPERADO_H0316)).decode()
            and despues.get("filename") == artefacto["ruta"], "ARTIFACT_PIN")
    require(despues.get("description") == DESCRIPCION_DE_LA_FUNCION, "FUNCTION_UPDATE")
    cambiables = CALCULADOS_FUNCION | {"source_code_hash", "filename", "description"}
    require(all(antes.get(k) == despues.get(k) for k in set(antes) | set(despues) if k not in cambiables),
            "FUNCTION_UPDATE")
    require(all(despues.get(k) is None or despues.get(k) == antes.get(k) for k in CALCULADOS_FUNCION),
            "FUNCTION_UPDATE")


def _cableado_nuevo(plan):
    llamadas = plan["configuration"]["root_module"]["module_calls"]
    contratos = {
        "credenciales_sql": {"ruta_base": ["local.ruta_de_datos"],
                             **{k: [f"var.{k}"] for k in (*EFIMERAS[1:], "version_de_blog_migrate", "version_de_blog_app")}},
        "exportacion": {"nombre_del_rol": ["module.ejecutor_privado.nombre_del_rol", "module.ejecutor_privado"],
                        "arn_del_bucket": ["var.arn_del_bucket_de_medios"],
                        **{k: [f"module.red.{v}", "module.red"] for k, v in {
                            "id_sg_admin": "id_sg_admin", "prefix_list_s3": "prefix_list_s3",
                            "id_del_endpoint_s3": "id_endpoint_s3"}.items()}},
    }
    for nombre, contrato in contratos.items():
        llamada = llamadas.get(nombre) or {}
        require(llamada.get("source") == f"../terraform/modulos/{nombre}", "WIRING")
        expresiones = llamada.get("expressions") or {}
        require(all(expresiones.get(k) == {"references": v} for k, v in contrato.items()), "WIRING")
        require(not any(k in llamada for k in ("count_expression", "for_each_expression")), "WIRING")


def check(plan, account, arn_de_medios, ahora=None):
    from scripts.terraform_datos.check_plan_convergencia import FASES

    ahora = ahora or datetime.now(timezone.utc)
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True, "APPLYABLE")
    require(plan.get("complete") is True and plan.get("errored") is False, "INCOMPLETE")
    _sin_secretos(plan)
    _variables(plan, account, arn_de_medios)
    variables = plan["variables"]
    for nombre in ("version_de_blog_migrate", "version_de_blog_app"):
        valor = variables.get(nombre, {}).get("value")
        require(type(valor) is int and valor == 1, "SQL_CREDENTIAL_VERSION")
    require(variables.get("version_de_la_contrasena", {}).get("value") == 1, "PASSWORD_VERSION")
    require(variables.get("dias_de_retencion_de_backups", {}).get("value") == 1, "RETENTION")
    artefacto = variables.get("zip_de_la_ejecutora", {}).get("value") or {}
    require(artefacto.get("sha256") == SHA256_ESPERADO_H0316
            and str(artefacto.get("ruta", "")).endswith(".zip"), "ARTIFACT_PIN")
    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.operador") == "pass", "IDENTITY_CHECK")
    require(all(v == "pass" for v in checks.values()), "CHECKS")
    _sin_grupo_por_omision(plan)
    previos = _estado_previo(plan)
    require(set(previos) == FASES["h0315"] and not any(r.get("tainted") for r in previos.values()), "PRIOR_STATE")
    vistos, nuevos = set(), {}
    for item in plan.get("resource_changes", []):
        address, cambio = item["address"], item["change"]
        require(item.get("mode") == "managed" and item.get("provider_name") == PROVIDER and address not in vistos,
                "RESOURCE_SET")
        require(not cambio.get("importing") and not item.get("previous_address"), "IMPORT_MOVE")
        vistos.add(address)
        if address == FUNCION:
            require(item.get("type") == "aws_lambda_function", "FUNCTION_UPDATE")
            _actualizar_funcion(cambio, previos[address], artefacto)
        elif address in previos:
            require(item.get("type") == previos[address]["type"] and cambio.get("actions") == ["no-op"]
                    and cambio.get("before") == cambio.get("after") == previos[address]["values"]
                    and not _desconocido(cambio.get("after_unknown")), "EXISTING_CHANGED")
        elif address in NUEVOS:
            require(item.get("type") == NUEVOS[address] and cambio.get("actions") == ["create"]
                    and cambio.get("before") is None and not cambio.get("replace_paths"), "NOT_CREATE")
            nuevos[address] = cambio
        else:
            raise ValueError("UNEXPECTED_RESOURCE")
    require(vistos == set(previos) | set(NUEVOS), "RESOURCE_SET")
    require(not plan.get("deferred_changes"), "DEFERRED")
    for c, (ruta, descripcion, nombre) in CREDENCIALES.items():
        esperado = {"allowed_pattern": None, "description": descripcion, "key_id": "alias/aws/ssm", "name": ruta,
                    "overwrite": None, "region": REGION, "tags": {"Name": nombre},
                    "tags_all": {**ETIQUETAS, "Name": nombre}, "tier": "Standard", "type": "SecureString",
                    "value_wo": None, "value_wo_version": 1}
        _exacto(nuevos[f"module.credenciales_sql.aws_ssm_parameter.{c}"], esperado,
                {"arn", "data_type", "has_value_wo", "id", "insecure_value", "value", "version"}, "SQL_CREDENTIAL")
    endpoint = previos["module.red.aws_vpc_endpoint.s3"]["values"]
    vpce, prefix_list = endpoint["id"], endpoint["prefix_list_id"]
    require(re.fullmatch(r"vpce-[0-9a-f]+", vpce) and re.fullmatch(r"pl-[0-9a-f]+", prefix_list), "EXPORT_RULE")
    politica = nuevos[POLITICA_DE_EXPORT]
    # `name_prefix` es calculado: en el plan real de H-031-5 un `aws_iam_role_policy` nuevo lo traia desconocido.
    _exacto(politica, {"name": "PersonalBlogEjecutorDatos-exportacion", "role": "PersonalBlogEjecutorDatos",
                      "policy": politica.get("after", {}).get("policy")}, {"id", "name_prefix"}, "EXPORT_POLICY")
    require(json.loads(politica["after"].get("policy") or "null") == politica_de_exportacion(arn_de_medios, vpce),
            "EXPORT_POLICY")
    nombre = "blog-prod-admin-a-s3"
    _exacto(nuevos[REGLA_DE_EXPORT], {
        "cidr_ipv4": None, "cidr_ipv6": None, "description": "HTTPS hacia S3 por el gateway endpoint (modo export de D-24)",
        "from_port": 443, "to_port": 443, "ip_protocol": "tcp", "prefix_list_id": prefix_list,
        "referenced_security_group_id": None, "region": REGION,
        "security_group_id": previos["module.red.aws_security_group.admin"]["values"]["id"],
        "tags": {"Name": nombre}, "tags_all": {**ETIQUETAS, "Name": nombre},
    }, {"arn", "id", "security_group_rule_id"}, "EXPORT_RULE")
    _cableado(plan)
    _cableado_nuevo(plan)
    salidas = plan.get("output_changes") or {}
    esperadas = _linea_base()[1] | SALIDAS_NUEVAS | {SALIDA_NUEVA}
    require(set(salidas) == set(plan["configuration"]["root_module"].get("outputs") or {}) == esperadas, "OUTPUTS")
    for nombre, dato in salidas.items():
        require(not _desconocido(dato.get("after_unknown")) and not _desconocido(dato.get("after_sensitive")), "OUTPUTS")
        if nombre == SALIDA_NUEVA:
            require(dato.get("actions") == ["create"] and dato.get("before") is None
                    and dato.get("after") == {k: v[0] for k, v in CREDENCIALES.items()}, "OUTPUTS")
        else:
            require(dato.get("actions") == ["no-op"] and dato.get("before") == dato.get("after"), "OUTPUTS")
    deriva, movil = _deriva(plan, ahora)
    return {"gate": "H0316_PLAN_OK", "estado_previo": 35, "add": 4, "change": 1, "destroy": 0, "replace": 0,
            "inventario": sorted(NUEVOS), "actualizado": [FUNCION], "resource_drift": len(deriva), "drift_movil": movil}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--variables", required=True, type=Path)
    args = parser.parse_args()
    try:
        raw = args.plan_json.read_bytes()
        privadas = json.loads(args.variables.read_text(encoding="utf-8"))
        resultado = check(json.loads(raw), privadas["expected_account_id"], privadas["arn_del_bucket_de_medios"])
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        codigo = str(error) if isinstance(error, ValueError) and str(error).isupper() else type(error).__name__
        raise SystemExit(f"Plan H-031-6 rechazado ({codigo}). Revisar en privado; sin apply.") from None
    print(json.dumps({"json_sha256": hashlib.sha256(raw).hexdigest(), **resultado}))


if __name__ == "__main__":
    main()
