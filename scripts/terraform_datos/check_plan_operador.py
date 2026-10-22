"""Gate offline de H-031-IAM. Lee el plan JSON PRIVADO de `bootstrap/operador-datos`; nunca llama a AWS ni aplica.

Que exige, y por que cada cosa
------------------------------
El bootstrap de la identidad operativa solo puede crear lo que aprobo el diseno
(docs/architecture/identidad-operativa-datos.md §10): el rol
`PersonalBlogDataOperator`, sus tres politicas administradas bajo
`/personal-blog/`, sus tres adjuntos y, SOLO si el preflight probo que falta,
`AWSServiceRoleForRDS`. Ni una identidad, clave, perfil de instancia o politica
mas; ni red, RDS, SSM ni CloudWatch. Solo `create`, sin import ni move.

El trust y las politicas se comparan con un render PROPIO de las plantillas
versionadas, hecho aqui en Python y no por Terraform: si `templatefile` y este
render coinciden sobre el plan real, el texto revisado —y validado por Access
Analyzer— es exactamente el que se aplicaria. Un plan que proponga otra cosa se
rechaza con un codigo corto y sin imprimir su contenido: la cuenta no sale nunca.

Lo que NO demuestra: como evalua AWS las politicas ni que alcancen para H-031-2.
Eso es la simulacion desde el bootstrap y las pruebas reales, despues del apply.
"""
import argparse
import hashlib
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PLANTILLAS = RAIZ / "bootstrap" / "operador-datos" / "politicas"

REGION = "us-east-2"
ROL = "PersonalBlogDataOperator"
USUARIO_DE_ENTRADA = "personal-blog-entry-admin"
PROVIDER = "registry.terraform.io/hashicorp/aws"
CLAVES_DE_ETIQUETA = ["Componente", "Entorno", "Gestion", "Name", "Proyecto", "Tarea"]

#: Clave de `for_each` -> plantilla, y sentencias que cada una debe tener.
PLANTILLA = {
    "Red": "fase-1-red.json.tftpl",
    "RdsYCustodia": "fase-1-rds-y-custodia.json.tftpl",
    "Denegaciones": "fase-1-denegaciones.json.tftpl",
}
CLAVES_DE_POLITICA = tuple(PLANTILLA)
#: Red tiene 8 desde la correccion S-10 de H-031-IAM: `CreateVpcEndpoint` y `ModifyVpcEndpoint`
#: salieron de `OperarSoloRecursosPropios` a sentencias propias. La plantilla aplicada en
#: H-031-IAM, con 6, se conserva en `historico/` para la guarda de reparacion.
SENTENCIAS = {"Red": 8, "RdsYCustodia": 9, "Denegaciones": 7}
ACCIONES_ALLOW = 68

ETIQUETAS = {
    "Proyecto": "personal-blog",
    "Entorno": "produccion",
    "Gestion": "terraform",
    "Componente": "identidad-operativa",
    "Tarea": "Task/031",
}

#: Expresiones exactas que la configuracion puede declarar en cada recurso. Asi
#: se rechaza, por ejemplo, un `inline_policy`, unos `managed_policy_arns` o un
#: `permissions_boundary` que el plan no mostraria como valor conocido.
EXPRESIONES = {
    "aws_iam_role.operador_datos": {
        "assume_role_policy", "description", "max_session_duration", "name", "path", "tags"},
    "aws_iam_policy.fase_1": {"description", "name", "path", "policy", "tags"},
    "aws_iam_role_policy_attachment.fase_1": {"policy_arn", "role"},
    "aws_iam_service_linked_role.rds": {"aws_service_name"},
}
ADMINISTRADOR = "AdministratorAccess"


def require(condition, code):
    if not condition:
        raise ValueError(code)


def bucket_de_estado(cuenta):
    """Mismo nombre deterministico que fija `bootstrap/terraform-state` (D-06)."""
    sufijo = hashlib.sha256(f"personal-blog:terraform-state:{cuenta}:{REGION}".encode()).hexdigest()[:12]
    return f"personal-blog-tfstate-{REGION}-{sufijo}"


def _render(texto, cuenta):
    valores = {
        "cuenta": cuenta,
        "region": REGION,
        "bucket_de_estado": bucket_de_estado(cuenta),
        "claves_de_etiqueta": json.dumps(CLAVES_DE_ETIQUETA),
    }
    for nombre, valor in valores.items():
        texto = texto.replace("${" + nombre + "}", valor)
    require("${" not in texto and "%{" not in texto, "TEMPLATE")
    return json.loads(texto)


def politicas(cuenta):
    """Las tres politicas de fase 1, renderizadas desde las plantillas versionadas."""
    return {
        clave: _render((PLANTILLAS / archivo).read_text(encoding="utf-8"), cuenta)
        for clave, archivo in PLANTILLA.items()
    }


def trust(cuenta):
    """El trust aprobado: solo el usuario de entrada, por ARN exacto y con MFA."""
    return {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "UsuarioDeEntradaConMfa",
            "Effect": "Allow",
            "Principal": {"AWS": f"arn:aws:iam::{cuenta}:user/{USUARIO_DE_ENTRADA}"},
            "Action": "sts:AssumeRole",
            "Condition": {"Bool": {"aws:MultiFactorAuthPresent": "true"}},
        }],
    }


def acciones_allow(documentos):
    """Acciones Allow distintas de un conjunto de politicas."""
    acciones = set()
    for documento in documentos.values():
        for sentencia in documento["Statement"]:
            if sentencia["Effect"] == "Allow":
                accion = sentencia["Action"]
                acciones.update([accion] if isinstance(accion, str) else accion)
    return sorted(acciones)


def direcciones(crear_rol_vinculado):
    """Direcciones exactas del plan y su tipo: 7, u 8 con el rol vinculado."""
    esperadas = {"aws_iam_role.operador_datos": "aws_iam_role"}
    for clave in CLAVES_DE_POLITICA:
        esperadas[f'aws_iam_policy.fase_1["{clave}"]'] = "aws_iam_policy"
        esperadas[f'aws_iam_role_policy_attachment.fase_1["{clave}"]'] = "aws_iam_role_policy_attachment"
    if crear_rol_vinculado:
        esperadas["aws_iam_service_linked_role.rds[0]"] = "aws_iam_service_linked_role"
    return esperadas


def _variables(plan, cuenta, crear_rol_vinculado):
    observadas = {nombre: dato.get("value") for nombre, dato in plan.get("variables", {}).items()}
    require(observadas == {
        "expected_account_id": cuenta,
        "aws_region": REGION,
        "usuario_de_entrada": USUARIO_DE_ENTRADA,
        "crear_rol_vinculado_de_rds": crear_rol_vinculado,
    }, "VARIABLES")


def _configuracion(plan):
    recursos = {
        r["address"]: r for r in plan["configuration"]["root_module"]["resources"]
        if r.get("mode", "managed") == "managed"
    }
    require(set(recursos) <= set(EXPRESIONES), "CONFIGURATION")
    require({"aws_iam_role.operador_datos", "aws_iam_policy.fase_1",
             "aws_iam_role_policy_attachment.fase_1"} <= set(recursos), "CONFIGURATION")
    for direccion, recurso in recursos.items():
        require(set(recurso.get("expressions", {})) == EXPRESIONES[direccion], "CONFIGURATION")
    adjunto = recursos["aws_iam_role_policy_attachment.fase_1"]["expressions"]
    require(adjunto["policy_arn"].get("references", [None])[0] == "each.value.arn", "CONFIGURATION")
    require(adjunto["role"].get("references", [None])[0] == "aws_iam_role.operador_datos.name", "CONFIGURATION")


def check(plan, cuenta, crear_rol_vinculado):
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True and plan.get("complete") is True and not plan.get("errored"), "INCOMPLETE")
    require(not plan.get("resource_drift") and not plan.get("deferred_changes"), "DRIFT_OR_DEFERRED")
    _variables(plan, cuenta, crear_rol_vinculado)

    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.bootstrap") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")

    esperadas = direcciones(crear_rol_vinculado)
    recursos, desconocidos = {}, {}
    for item in plan.get("resource_changes", []):
        change = item["change"]
        require(not change.get("importing") and not item.get("previous_address"), "IMPORT_OR_MOVE")
        require(item.get("mode") == "managed", "DATA_SOURCE_DEFERRED")
        require(item["address"] in esperadas and item["address"] not in recursos, "UNEXPECTED_RESOURCE")
        require(item["type"] == esperadas[item["address"]], "UNEXPECTED_RESOURCE")
        require(change["actions"] == ["create"] and change.get("before") is None, "NOT_CREATE_ONLY")
        require(item["provider_name"] == PROVIDER, "PROVIDER")
        recursos[item["address"]] = change["after"]
        desconocidos[item["address"]] = change.get("after_unknown") or {}
    require(set(recursos) == set(esperadas), "RESOURCE_SET")
    _configuracion(plan)

    rol = recursos["aws_iam_role.operador_datos"]
    require(rol.get("name") == ROL and rol.get("path") == "/", "ROLE")
    require(rol.get("max_session_duration") == 3600 and rol.get("permissions_boundary") is None, "ROLE")
    require(json.loads(rol["assume_role_policy"]) == trust(cuenta), "TRUST")
    require(rol.get("tags") == ETIQUETAS and rol.get("tags_all") == ETIQUETAS, "TAGS")

    documentos = politicas(cuenta)
    for clave in CLAVES_DE_POLITICA:
        politica = recursos[f'aws_iam_policy.fase_1["{clave}"]']
        codigo = f"POLICY_{clave.upper()}"
        require(politica.get("name") == f"PersonalBlogOperadorDatosFase1{clave}", codigo)
        require(politica.get("path") == "/personal-blog/", codigo)
        require(len(politica["policy"]) < 6144, codigo)
        require(json.loads(politica["policy"]) == documentos[clave], codigo)
        require(len(documentos[clave]["Statement"]) == SENTENCIAS[clave], codigo)
        require(politica.get("tags") == ETIQUETAS and politica.get("tags_all") == ETIQUETAS, "TAGS")

        direccion = f'aws_iam_role_policy_attachment.fase_1["{clave}"]'
        require(recursos[direccion].get("role") == ROL, "ATTACHMENT")
        require("policy_arn" not in recursos[direccion] and desconocidos[direccion].get("policy_arn") is True,
                "ATTACHMENT")

    # Reconfirmacion sobre el render que el plan acaba de igualar.
    acciones = acciones_allow(documentos)
    require(len(acciones) == ACCIONES_ALLOW, "ALLOW_ACTIONS")
    require(not [a for a in acciones if a.lower().startswith("iam:")], "IAM_ALLOW")
    require(not [a for a in acciones if "*" in a], "WILDCARD_ALLOW")

    if crear_rol_vinculado:
        vinculado = recursos["aws_iam_service_linked_role.rds[0]"]
        require(vinculado.get("aws_service_name") == "rds.amazonaws.com", "SERVICE_LINKED_ROLE")
        require(not vinculado.get("custom_suffix"), "SERVICE_LINKED_ROLE")

    salidas = plan.get("planned_values", {}).get("outputs", {})
    require(set(salidas) == {"arn_del_rol_operativo", "bucket_de_estado", "politicas_fase_1_sha256"}, "OUTPUTS")
    require(not any(dato.get("sensitive") for dato in salidas.values()), "OUTPUTS")
    require(salidas["bucket_de_estado"].get("value") == bucket_de_estado(cuenta), "OUTPUTS")
    require(set(salidas["politicas_fase_1_sha256"].get("value") or {}) == set(CLAVES_DE_POLITICA), "OUTPUTS")

    # Ninguna politica administrada de AWS de amplio alcance, en ningun atributo.
    require(ADMINISTRADOR not in json.dumps(recursos), "ADMIN_POLICY")

    return {
        "add": len(recursos), "change": 0, "destroy": 0, "addresses": sorted(recursos),
        "statements": dict(SENTENCIAS), "allow_actions": len(acciones), "iam_allow_actions": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--variables", required=True, type=Path,
                        help="JSON privado con expected_account_id y crear_rol_vinculado_de_rds")
    args = parser.parse_args()
    try:
        raw = args.plan_json.read_bytes()
        privadas = json.loads(args.variables.read_text(encoding="utf-8"))
        result = check(json.loads(raw), privadas["expected_account_id"], privadas["crear_rol_vinculado_de_rds"])
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        codigo = str(error) if isinstance(error, ValueError) and str(error).isupper() else type(error).__name__
        raise SystemExit(f"H-031-IAM: plan rejected ({codigo}); inspect privately. No apply authorized.") from None
    print(json.dumps({"gate": "PLAN_OK", "json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
