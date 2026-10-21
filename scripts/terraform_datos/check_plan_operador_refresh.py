"""Gate offline del REFRESH-ONLY de `bootstrap/operador-datos`. Lee el plan JSON PRIVADO; nunca llama a AWS ni aplica.

Por que es una guarda aparte
----------------------------
El primer plan tras el apply de H-031-IAM trajo cinco diferencias de METADATOS, todas
`no-op` para la infraestructura: el `attachment_count` de las tres politicas (se crearon
antes que sus adjuntos), el atributo espejo `managed_policy_arns` del rol y los `tags`
del rol vinculado (`null -> {}`, normalizacion del SDKv2). Un refresh-only puede
guardarlas en el state; esta guarda exige que sean EXACTAMENTE esas, con su antes y su
despues, y nada mas:

- ningun `resource_changes` (un refresh-only no planifica infraestructura);
- ningun documento de politica, trust, nombre, ruta ni etiqueta propia distinto;
- ninguna salida que cambie: con la plantilla corregida de S-10 en la configuracion, el
  refresh-only intentaria guardar la huella de una politica que NO esta viva;
- ninguna sexta entrada, de ninguna clase.

Las guardas del bootstrap inicial y de la reparacion S-10 no se tocan para esto.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.terraform_datos.check_plan_operador import (
    CLAVES_DE_POLITICA,
    PROVIDER,
    REGION,
    USUARIO_DE_ENTRADA,
    politicas,
    require,
    trust,
)
from scripts.terraform_datos.check_plan_operador_repair import politica_red_aplicada

ROL = "aws_iam_role.operador_datos"
VINCULADO = "aws_iam_service_linked_role.rds[0]"

#: Direccion -> (tipo, el UNICO atributo que puede diferir).
DERIVA = {
    **{f'aws_iam_policy.fase_1["{c}"]': ("aws_iam_policy", "attachment_count") for c in CLAVES_DE_POLITICA},
    ROL: ("aws_iam_role", "managed_policy_arns"),
    VINCULADO: ("aws_iam_service_linked_role", "tags"),
}


def _arn_politica(cuenta, clave):
    return f"arn:aws:iam::{cuenta}:policy/personal-blog/PersonalBlogOperadorDatosFase1{clave}"


def check(plan, cuenta):
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True and plan.get("complete") is True and not plan.get("errored"), "INCOMPLETE")
    require(not plan.get("deferred_changes"), "DEFERRED")
    require(not plan.get("resource_changes"), "RESOURCE_CHANGES")

    observadas = {nombre: dato.get("value") for nombre, dato in plan.get("variables", {}).items()}
    require(observadas == {"expected_account_id": cuenta, "aws_region": REGION,
                           "usuario_de_entrada": USUARIO_DE_ENTRADA, "crear_rol_vinculado_de_rds": True},
            "VARIABLES")
    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.bootstrap") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")

    # La politica Red viva es la APLICADA en H-031-IAM; las otras dos, sus plantillas.
    vivas = {**politicas(cuenta), "Red": politica_red_aplicada(cuenta)}
    vistas = {}
    for item in plan.get("resource_drift") or []:
        direccion = item.get("address")
        require(direccion in DERIVA and direccion not in vistas, "UNEXPECTED_DRIFT")
        tipo, atributo = DERIVA[direccion]
        require(item.get("mode") == "managed" and item.get("type") == tipo, "UNEXPECTED_DRIFT")
        require(item.get("provider_name") == PROVIDER, "UNEXPECTED_DRIFT")
        require(not item.get("previous_address") and not item["change"].get("importing"), "UNEXPECTED_DRIFT")
        cambio = item["change"]
        require(cambio.get("actions") == ["update"], "ACTIONS")
        antes, despues = cambio.get("before") or {}, cambio.get("after") or {}
        distintos = {k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k)}
        require(distintos == {atributo}, "ONLY_METADATA")
        require(not any(v is True for v in (cambio.get("after_unknown") or {}).values()), "ONLY_METADATA")

        if tipo == "aws_iam_policy":
            require(antes.get(atributo) == 0 and despues.get(atributo) == 1, "ATTACHMENT_COUNT")
            clave = direccion.split('"')[1]
            require(json.loads(antes["policy"]) == vivas[clave], "POLICY_DOCUMENT")
        elif tipo == "aws_iam_role":
            esperados = sorted(_arn_politica(cuenta, c) for c in CLAVES_DE_POLITICA)
            require(antes.get(atributo) == [] and sorted(despues.get(atributo) or []) == esperados,
                    "MANAGED_POLICY_ARNS")
            require(len(despues[atributo]) == 3, "MANAGED_POLICY_ARNS")
            require(json.loads(antes["assume_role_policy"]) == trust(cuenta), "TRUST")
        else:
            require(antes.get(atributo) is None and despues.get(atributo) == {}
                    and isinstance(despues.get(atributo), dict), "SLR_TAGS")
            require(antes.get("aws_service_name") == "rds.amazonaws.com", "SLR_TAGS")
        vistas[direccion] = sorted(distintos)
    require(set(vistas) == set(DERIVA), "DRIFT_SET")

    salidas = plan.get("output_changes", {})
    require(set(salidas) == {"arn_del_rol_operativo", "bucket_de_estado", "politicas_fase_1_sha256"}, "OUTPUTS")
    for dato in salidas.values():
        require(dato.get("actions") == ["no-op"] and dato.get("before") == dato.get("after"), "OUTPUTS")

    return {"resource_drift": len(vistas), "resource_changes": 0, "attributes": dict(sorted(vistas.items())),
            "outputs": "no-op"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--variables", required=True, type=Path, help="JSON privado con expected_account_id")
    args = parser.parse_args()
    try:
        raw = args.plan_json.read_bytes()
        privadas = json.loads(args.variables.read_text(encoding="utf-8"))
        result = check(json.loads(raw), privadas["expected_account_id"])
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        codigo = str(error) if isinstance(error, ValueError) and str(error).isupper() else type(error).__name__
        raise SystemExit(f"H-031-IAM refresh: plan rejected ({codigo}); inspect privately. No apply authorized.") from None
    print(json.dumps({"gate": "REFRESH_PLAN_OK", "json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
