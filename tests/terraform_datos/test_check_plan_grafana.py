"""Guarda del plan productivo de H-031-9 (Task/031): rol de solo lectura de D-20 para Grafana Cloud. Nunca aplica.

El fixture parte del plan de H-031-8 YA APLICADO (21 + 8 recursos en `no-op`, salidas `no-op`) y le anade EXACTAMENTE
el rol `PersonalBlogLecturaGrafana`, su politica en linea y la salida con su NOMBRE. Cada prueba negativa rompe una
sola cosa y exige su codigo.
"""
import copy
import json
import unittest
from datetime import datetime, timezone

from scripts.terraform_datos.check_plan_grafana import NUEVOS, POLITICA, ROL, check, confianza, permisos
from tests.terraform_datos.test_check_plan_alarmas import fixture as fixture_alarmas
from tests.terraform_datos.test_check_plan_convergencia import con_drift_movil
from tests.terraform_datos.test_check_plan_recuperacion import ACCOUNT, MEDIOS

AHORA = datetime(2026, 10, 8, 18, 0, 0, tzinfo=timezone.utc)
#: Enmienda de §40 del 2026-10-18 (aprobada el 2026-10-19): el valor de AWS del caso B debe ser FRESCO respecto a `AHORA`
#: (24 h como maximo). Los valores por omision de `con_drift_movil` son del 2026-10-05: rancios para este reloj.
FRESCO = {"antes": "2026-10-08T17:00:00Z", "despues": "2026-10-08T17:50:00Z"}
GRAFANA = "999999999999"
EXTERNAL_ID = "1234567"


def aplicado(plan):
    """El plan con cambios convertido en el plan convergente que veria Terraform despues de aplicarlo."""
    plan = copy.deepcopy(plan)
    hijos = plan["prior_state"]["values"]["root_module"]["child_modules"]
    for item in plan["resource_changes"]:
        cambio = item["change"]
        if cambio["actions"] != ["create"]:
            continue
        modulo = item["address"].split(".aws_")[0]
        destino = next((m for m in hijos if m.get("address") == modulo), None)
        if destino is None:
            destino = {"address": modulo, "resources": []}
            hijos.append(destino)
        valores = {**cambio["after"], **{k: f"calculado-{k}" for k, v in (cambio.get("after_unknown") or {}).items()
                                         if v is True}}
        destino["resources"].append({"address": item["address"], "mode": "managed", "type": item["type"],
                                     "index": item.get("index"), "values": valores})
        item["change"] = {"actions": ["no-op"], "before": copy.deepcopy(valores), "after": copy.deepcopy(valores)}
    for dato in plan["output_changes"].values():
        if dato["actions"] == ["create"]:
            dato.update(actions=["no-op"], before=dato["after"])
    plan["applyable"] = False
    return plan


def fixture():
    plan = aplicado(fixture_alarmas())
    plan["applyable"] = True
    plan["variables"]["integracion_grafana"] = {"value": {"cuenta": GRAFANA, "external_id": EXTERNAL_ID}}
    rol = {"assume_role_policy": json.dumps(confianza(GRAFANA, EXTERNAL_ID)),
           "description": "D-20: lectura de metricas y estados de alarma de CloudWatch para Grafana Cloud. Sin logs ni "
                          "escritura.",
           "force_detach_policies": False, "max_session_duration": 3600, "name": "PersonalBlogLecturaGrafana",
           "path": "/", "permissions_boundary": None, "tags": None}
    politica = {"name": "PersonalBlogLecturaGrafana-lectura", "policy": json.dumps(permisos(ACCOUNT))}
    plan["resource_changes"] += [
        {"address": ROL, "mode": "managed", "type": "aws_iam_role", "provider_name": "registry.terraform.io/hashicorp/aws",
         "change": {"actions": ["create"], "before": None, "after": rol,
                    "after_unknown": {"arn": True, "create_date": True, "id": True, "inline_policy": True,
                                      "managed_policy_arns": True, "tags_all": True, "unique_id": True}}},
        {"address": POLITICA, "mode": "managed", "type": "aws_iam_role_policy",
         "provider_name": "registry.terraform.io/hashicorp/aws",
         "change": {"actions": ["create"], "before": None, "after": politica, "after_unknown": {"id": True, "role": True}}},
    ]
    plan["output_changes"]["rol_de_grafana"] = {"actions": ["create"], "before": None,
                                                "after": "PersonalBlogLecturaGrafana", "after_unknown": False,
                                                "after_sensitive": False}
    raiz = plan["configuration"]["root_module"]
    raiz["outputs"]["rol_de_grafana"] = {}
    raiz["module_calls"]["lectura_grafana"] = {
        "source": "../terraform/modulos/lectura_grafana",
        "expressions": {
            "nombre_del_rol": {"constant_value": "PersonalBlogLecturaGrafana"},
            "cuenta": {"references": ["data.aws_caller_identity.operador.account_id",
                                      "data.aws_caller_identity.operador"]},
            "region": {"references": ["var.region"]},
            "prefijo": {"references": ["var.prefijo"]},
            "cuenta_de_grafana": {"references": ["var.integracion_grafana.cuenta", "var.integracion_grafana"]},
            "external_id": {"references": ["var.integracion_grafana.external_id", "var.integracion_grafana"]},
        },
        "module": {"resources": [
            {"address": "aws_iam_role.this", "expressions": {}},
            {"address": "aws_iam_role_policy.this",
             "expressions": {"role": {"references": ["aws_iam_role.this.name", "aws_iam_role.this"]}}},
        ]},
    }
    return plan


def despues(plan, address):
    return next(i for i in plan["resource_changes"] if i["address"] == address)["change"]["after"]


class PlanDelRolDeGrafana(unittest.TestCase):
    def pasa(self, plan, grafana=GRAFANA, external_id=EXTERNAL_ID):
        return check(plan, ACCOUNT, MEDIOS, grafana, external_id, ahora=AHORA)

    def rechaza(self, plan, codigo, grafana=GRAFANA, external_id=EXTERNAL_ID):
        with self.assertRaises(ValueError) as error:
            check(plan, ACCOUNT, MEDIOS, grafana, external_id, ahora=AHORA)
        self.assertEqual(str(error.exception), codigo)

    def test_caso_a_rol_y_politica_y_nada_mas(self):
        r = self.pasa(fixture())
        self.assertEqual(r["gate"], "GRAFANA_ROLE_PLAN_OK")
        self.assertEqual((r["add"], r["change"], r["destroy"], r["replace"], r["deferred_changes"]), (2, 0, 0, 0, 0))
        self.assertEqual(r["inventario"], sorted(NUEVOS))

    def test_caso_b_solo_el_atributo_movil(self):
        r = self.pasa(con_drift_movil(fixture(), **FRESCO))
        self.assertEqual((r["gate"], r["resource_drift"]), ("GRAFANA_ROLE_PLAN_OK", 1))

    def test_confianza(self):
        casos = (
            lambda d: d["Statement"][0].pop("Condition"),
            lambda d: d["Statement"][0]["Condition"]["StringEquals"].update({"sts:ExternalId": "otro"}),
            lambda d: d["Statement"][0]["Principal"].update(AWS="arn:aws:iam::000000000000:root"),
            lambda d: d["Statement"][0]["Principal"].update(AWS="*"),
            lambda d: d["Statement"][0].update(Action=["sts:AssumeRole", "sts:TagSession"]),
            lambda d: d["Statement"].append({"Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"},
                                             "Action": "sts:AssumeRole"}),
        )
        for romper in casos:
            with self.subTest():
                plan = fixture()
                documento = confianza(GRAFANA, EXTERNAL_ID)
                romper(documento)
                despues(plan, ROL)["assume_role_policy"] = json.dumps(documento)
                self.rechaza(plan, "TRUST")

    def test_politica(self):
        casos = (
            lambda d: d["Statement"][0]["Action"].append("logs:GetLogEvents"),
            lambda d: d["Statement"][0]["Action"].append("cloudwatch:PutMetricAlarm"),
            lambda d: d["Statement"][1].update(Resource="*"),
            lambda d: d["Statement"][0].pop("Condition"),
            lambda d: d["Statement"].append({"Effect": "Allow", "Action": "ssm:GetParameter", "Resource": "*"}),
        )
        for romper in casos:
            with self.subTest():
                plan = fixture()
                documento = permisos(ACCOUNT)
                romper(documento)
                despues(plan, POLITICA)["policy"] = json.dumps(documento)
                self.rechaza(plan, "POLICY")

    def test_rol(self):
        for atributo, valor in (("max_session_duration", 43200), ("permissions_boundary", "arn:aws:iam::1:policy/x"),
                                ("name", "OtroRol"), ("path", "/grafana/"), ("force_detach_policies", True),
                                ("managed_policy_arns", ["arn:aws:iam::aws:policy/ReadOnlyAccess"]),
                                ("description", "otra")):
            with self.subTest(atributo=atributo):
                plan = fixture()
                despues(plan, ROL)[atributo] = valor
                self.rechaza(plan, "ROLE")

    def test_valores_de_grafana_del_destino(self):
        self.rechaza(fixture(), "GRAFANA", grafana="000000000000")
        self.rechaza(fixture(), "GRAFANA", external_id="7654321")

    def test_las_alarmas_ya_aplicadas_no_cambian(self):
        plan = fixture()
        alarma = next(i for i in plan["resource_changes"] if i["address"].startswith("module.alarmas_rds."))
        alarma["change"]["actions"] = ["update"]
        self.rechaza(plan, "EXISTING_CHANGED")

    def test_cableado(self):
        casos = (
            lambda m: m["lectura_grafana"]["expressions"].update(cuenta={"constant_value": "123456789012"}),
            lambda m: m["lectura_grafana"]["expressions"].update(external_id={"constant_value": EXTERNAL_ID}),
            lambda m: m.update(ejecutor_privado={"source": "../terraform/modulos/ejecutor_privado"}),
        )
        for romper in casos:
            with self.subTest():
                plan = fixture()
                romper(plan["configuration"]["root_module"]["module_calls"])
                self.rechaza(plan, "WIRING")

    def test_salidas_sin_arn(self):
        plan = fixture()
        plan["output_changes"]["arn_del_rol_de_grafana"] = {"actions": ["create"], "before": None, "after_unknown": True}
        plan["configuration"]["root_module"]["outputs"]["arn_del_rol_de_grafana"] = {}
        self.rechaza(plan, "OUTPUTS")

    def test_un_recurso_inesperado(self):
        plan = fixture()
        extra = copy.deepcopy(plan["resource_changes"][-1])
        extra["address"] = "module.lectura_grafana.aws_iam_role_policy_attachment.this"
        plan["resource_changes"].append(extra)
        self.rechaza(plan, "UNEXPECTED_RESOURCE")


if __name__ == "__main__":
    unittest.main()
