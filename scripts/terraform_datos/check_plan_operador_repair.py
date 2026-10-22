"""Gate offline de la REPARACION S-10 de H-031-IAM. Lee el plan JSON PRIVADO; nunca llama a AWS ni aplica.

Por que es una guarda aparte
----------------------------
`check_plan_operador.py` conserva su proposito: el bootstrap inicial, solo `create`, de
7 u 8 recursos. Esta reparacion es otra cosa y no debe ablandar aquella: con el
bootstrap ya aplicado, el UNICO cambio admitido es actualizar en sitio el documento de
`aws_iam_policy.fase_1["Red"]`:

- `before` = la politica Red aplicada en H-031-IAM, renderizada desde la copia
  intacta de `historico/` (su SHA-256 se fija aqui);
- `after` = la plantilla vigente, que saca `ec2:CreateVpcEndpoint` y
  `ec2:ModifyVpcEndpoint` de `OperarSoloRecursosPropios`;
- ningun otro atributo de Red cambia, ningun otro recurso deja de ser `no-op`, ninguna
  accion Allow es nueva y ninguna es de IAM.

Lo que NO demuestra: como evalua AWS la politica. Eso es la simulacion y el readback.
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
    _configuracion,
    _render,
    acciones_allow,
    bucket_de_estado,
    direcciones,
    politicas,
    require,
    trust,
)

RED = 'aws_iam_policy.fase_1["Red"]'
HISTORICA = Path(__file__).resolve().parent / "historico" / "fase-1-red.h031iam-aplicada.json.tftpl"
HISTORICA_SHA256 = "031096896dadab1715440faad3c97acc18bea7c19f85ed49561be7bf7fec75e2"


def politica_red_aplicada(cuenta):
    """La politica Red tal como se aplico en H-031-IAM (6 sentencias)."""
    crudo = HISTORICA.read_bytes()
    require(hashlib.sha256(crudo).hexdigest() == HISTORICA_SHA256, "HISTORICAL_TEMPLATE")
    return _render(crudo.decode("utf-8"), cuenta)


def permisos_nuevos(antes, despues):
    """Acciones Allow que `despues` concede y `antes` no."""
    return sorted(set(acciones_allow({"x": despues})) - set(acciones_allow({"x": antes})))


def check(plan, cuenta):
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True and plan.get("complete") is True and not plan.get("errored"), "INCOMPLETE")
    require(not plan.get("resource_drift") and not plan.get("deferred_changes"), "DRIFT_OR_DEFERRED")

    observadas = {nombre: dato.get("value") for nombre, dato in plan.get("variables", {}).items()}
    # El rol vinculado YA esta en el state: la bandera debe seguir en true o el plan lo destruiria.
    require(observadas == {"expected_account_id": cuenta, "aws_region": REGION,
                           "usuario_de_entrada": USUARIO_DE_ENTRADA, "crear_rol_vinculado_de_rds": True},
            "VARIABLES")

    checks = {c["address"]["to_display"]: c["status"] for c in plan.get("checks", [])}
    require(checks.get("data.aws_caller_identity.bootstrap") == "pass", "IDENTITY_CHECK")
    require(all(status == "pass" for status in checks.values()), "CHECKS")

    esperadas = direcciones(True)
    cambios = {}
    for item in plan.get("resource_changes", []):
        change = item["change"]
        require(not change.get("importing") and not item.get("previous_address"), "IMPORT_OR_MOVE")
        require(item.get("mode") == "managed", "DATA_SOURCE_DEFERRED")
        require(item["address"] in esperadas and item["address"] not in cambios, "UNEXPECTED_RESOURCE")
        require(item["type"] == esperadas[item["address"]], "UNEXPECTED_RESOURCE")
        require(item["provider_name"] == PROVIDER, "PROVIDER")
        cambios[item["address"]] = change
    require(set(cambios) == set(esperadas), "RESOURCE_SET")
    _configuracion(plan)

    for direccion, change in cambios.items():
        if direccion != RED:
            require(change["actions"] == ["no-op"] and change["before"] == change["after"], "UNEXPECTED_CHANGE")
    rol = cambios["aws_iam_role.operador_datos"]["after"]
    require(json.loads(rol["assume_role_policy"]) == trust(cuenta), "UNEXPECTED_CHANGE")

    red = cambios[RED]
    require(red["actions"] == ["update"], "NOT_IN_PLACE_UPDATE")
    antes, despues = red["before"], red["after"]
    distintos = {k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k)}
    require(distintos == {"policy"}, "ONLY_POLICY")
    require(not any(v is True for v in (red.get("after_unknown") or {}).values()), "ONLY_POLICY")

    aplicada = politica_red_aplicada(cuenta)
    corregida = politicas(cuenta)["Red"]
    require(json.loads(antes["policy"]) == aplicada, "BEFORE_POLICY")
    require(json.loads(despues["policy"]) == corregida, "AFTER_POLICY")
    require(len(despues["policy"]) < 6144, "AFTER_POLICY")

    require(not permisos_nuevos(aplicada, corregida), "NEW_PERMISSION")
    documentos = politicas(cuenta)
    acciones = acciones_allow(documentos)
    require(not [a for a in acciones if a.lower().startswith("iam:")], "IAM_ALLOW")
    require(not [a for a in acciones if "*" in a], "WILDCARD_ALLOW")

    salidas = plan.get("output_changes", {})
    require(set(salidas) == {"arn_del_rol_operativo", "bucket_de_estado", "politicas_fase_1_sha256"}, "OUTPUTS")
    for nombre in ("arn_del_rol_operativo", "bucket_de_estado"):
        require(salidas[nombre]["actions"] == ["no-op"], "OUTPUTS")
    require(salidas["bucket_de_estado"]["after"] == bucket_de_estado(cuenta), "OUTPUTS")
    huellas = salidas["politicas_fase_1_sha256"]
    require(huellas["actions"] == ["update"], "OUTPUTS")
    require(set(huellas["before"]) == set(huellas["after"]) == set(CLAVES_DE_POLITICA), "OUTPUTS")
    require(all(huellas["before"][k] == huellas["after"][k] for k in CLAVES_DE_POLITICA if k != "Red"), "OUTPUTS")
    require(huellas["after"]["Red"] == hashlib.sha256(despues["policy"].encode()).hexdigest(), "OUTPUTS")

    return {
        "add": 0, "change": 1, "destroy": 0, "changed": [RED],
        "no_op": sorted(d for d in cambios if d != RED),
        "red_statements": {"before": len(aplicada["Statement"]), "after": len(corregida["Statement"])},
        "red_allow_actions": {"before": len(acciones_allow({"x": aplicada})),
                              "after": len(acciones_allow({"x": corregida}))},
        "allow_actions": len(acciones), "new_allow_actions": 0, "iam_allow_actions": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--variables", required=True, type=Path,
                        help="JSON privado con expected_account_id")
    args = parser.parse_args()
    try:
        raw = args.plan_json.read_bytes()
        privadas = json.loads(args.variables.read_text(encoding="utf-8"))
        result = check(json.loads(raw), privadas["expected_account_id"])
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        codigo = str(error) if isinstance(error, ValueError) and str(error).isupper() else type(error).__name__
        raise SystemExit(f"H-031-IAM S-10: plan rejected ({codigo}); inspect privately. No apply authorized.") from None
    print(json.dumps({"gate": "REPAIR_PLAN_OK", "json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
