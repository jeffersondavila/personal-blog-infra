"""Decisiones de las politicas de fase 1, offline (H-031-IAM, correccion S-10).

La simulacion contra el rol creado encontro que S-10 —`ec2:CreateVpcEndpoint` de SSM
con `aws:ResourceTag` del proyecto— salia `allowed`. Estas regresiones ejecutan la
matriz completa de `simulacion_de_politicas.py` contra las plantillas VIGENTES y
reproducen el defecto contra la plantilla Red que se aplico en H-031-IAM, que se
conserva intacta en `scripts/terraform_datos/historico/`.
"""
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scripts.terraform_datos.check_plan_operador import _render, bucket_de_estado, politicas  # noqa: E402
import simulacion_de_politicas as sim  # noqa: E402

CUENTA = "123456789012"
RAIZ = Path(__file__).resolve().parents[2]
HISTORICA = RAIZ / "scripts" / "terraform_datos" / "historico" / "fase-1-red.h031iam-aplicada.json.tftpl"
HISTORICA_SHA256 = "031096896dadab1715440faad3c97acc18bea7c19f85ed49561be7bf7fec75e2"


def documentos(red=None):
    docs = politicas(CUENTA)
    if red is not None:
        docs["Red"] = red
    return [docs["Red"], docs["RdsYCustodia"], docs["Denegaciones"]]


def roja_aplicada():
    return _render(HISTORICA.read_text(encoding="utf-8"), CUENTA)


def _tipo(arn):
    return arn.split(":")[5].split("/")[0]


class MatrizTests(unittest.TestCase):
    def test_cada_caso_de_la_matriz(self):
        for caso, accion, recurso, contexto, esperado in sim.casos(CUENTA, bucket_de_estado(CUENTA)):
            with self.subTest(caso=caso):
                self.assertEqual(sim.evaluar(documentos(), accion, recurso, contexto), esperado)

    def test_la_matriz_cubre_los_21_casos_de_10_1(self):
        ids = {c[0] for c in sim.casos(CUENTA, bucket_de_estado(CUENTA))}
        for n in range(1, 22):
            with self.subTest(caso=n):
                self.assertTrue({f"S-{n:02d}", f"S-{n:02d}a"} & ids)

    def test_ids_unicos(self):
        ids = [c[0] for c in sim.casos(CUENTA, bucket_de_estado(CUENTA))]
        self.assertEqual(len(ids), len(set(ids)))


class DefectoS10Tests(unittest.TestCase):
    """El defecto existe en la politica aplicada y desaparece en la vigente."""

    def test_la_copia_historica_no_se_altero(self):
        self.assertEqual(hashlib.sha256(HISTORICA.read_bytes()).hexdigest(), HISTORICA_SHA256)

    def test_la_politica_aplicada_reproduce_s10(self):
        casos = {c[0]: c for c in sim.casos(CUENTA, bucket_de_estado(CUENTA))}
        for caso in ("S-10", "S-10b", "E-01", "E-02", "E-03", "E-04"):
            with self.subTest(caso=caso):
                _, accion, recurso, contexto, _ = casos[caso]
                self.assertEqual(sim.evaluar(documentos(roja_aplicada()), accion, recurso, contexto), "allowed")

    def test_la_politica_vigente_lo_deniega(self):
        casos = {c[0]: c for c in sim.casos(CUENTA, bucket_de_estado(CUENTA))}
        for caso in ("S-10", "S-10a", "S-10b", "E-01", "E-02", "E-03", "E-04"):
            with self.subTest(caso=caso):
                _, accion, recurso, contexto, _ = casos[caso]
                self.assertEqual(sim.evaluar(documentos(), accion, recurso, contexto), "implicitDeny")


class EvaluadorTests(unittest.TestCase):
    """El evaluador aborta ante lo que no modela, en vez de decidir a ciegas."""

    def test_operador_no_modelado(self):
        doc = {"Statement": [{"Effect": "Allow", "Action": "ec2:X", "Resource": "*",
                              "Condition": {"StringLike": {"aws:RequestedRegion": "us-*"}}}]}
        with self.assertRaises(ValueError):
            sim.evaluar([doc], "ec2:X", "*", {"aws:RequestedRegion": "us-east-2"})

    def test_not_action(self):
        doc = {"Statement": [{"Effect": "Allow", "NotAction": "iam:*", "Resource": "*"}]}
        with self.assertRaises(ValueError):
            sim.evaluar([doc], "ec2:X", "*", {})

    def test_deny_explicito_gana(self):
        docs = [{"Statement": [{"Effect": "Allow", "Action": "ec2:*", "Resource": "*"}]},
                {"Statement": [{"Effect": "Deny", "Action": "ec2:X", "Resource": "*"}]}]
        self.assertEqual(sim.evaluar(docs, "ec2:X", "*", {}), "explicitDeny")

    def test_forallvalues_con_clave_ausente_es_verdadero(self):
        doc = {"Statement": [{"Effect": "Allow", "Action": "ec2:X", "Resource": "*",
                              "Condition": {"ForAllValues:StringEquals": {"aws:TagKeys": ["A"]}}}]}
        self.assertEqual(sim.evaluar([doc], "ec2:X", "*", {}), "allowed")
        self.assertEqual(sim.evaluar([doc], "ec2:X", "*", {"aws:TagKeys": ["A", "B"]}), "implicitDeny")


class SentenciasDeEndpointTests(unittest.TestCase):
    """Cada Allow de endpoints solo usa claves que AWS evalua para su accion y recurso."""

    def _allows(self, accion):
        for doc in documentos():
            for s in doc["Statement"]:
                acciones = s["Action"] if isinstance(s["Action"], list) else [s["Action"]]
                if s["Effect"] == "Allow" and accion in acciones:
                    yield s

    def test_crear_endpoint_solo_sobre_los_recursos_del_gateway(self):
        recursos = set()
        for s in self._allows("ec2:CreateVpcEndpoint"):
            recursos |= {_tipo(r) for r in (s["Resource"] if isinstance(s["Resource"], list) else [s["Resource"]])}
        self.assertEqual(recursos, sim.RECURSOS_DEL_GATEWAY_S3)

    def test_el_endpoint_nuevo_exige_el_servicio_s3(self):
        for s in self._allows("ec2:CreateVpcEndpoint"):
            recursos = s["Resource"] if isinstance(s["Resource"], list) else [s["Resource"]]
            if any(_tipo(r) == "vpc-endpoint" for r in recursos):
                self.assertEqual([_tipo(r) for r in recursos], ["vpc-endpoint"])
                self.assertEqual(s["Condition"]["StringEquals"]["ec2:VpceServiceName"], "com.amazonaws.us-east-2.s3")

    def test_modificar_endpoint_sin_subredes_ni_grupos(self):
        recursos = set()
        for s in self._allows("ec2:ModifyVpcEndpoint"):
            recursos |= {_tipo(r) for r in (s["Resource"] if isinstance(s["Resource"], list) else [s["Resource"]])}
        self.assertEqual(recursos, {"vpc-endpoint", "route-table"})

    def test_ninguna_sentencia_de_endpoint_mezcla_otras_acciones(self):
        for accion in ("ec2:CreateVpcEndpoint", "ec2:ModifyVpcEndpoint"):
            for s in self._allows(accion):
                with self.subTest(sid=s["Sid"]):
                    self.assertEqual(s["Action"], accion)

    def test_claves_validas_para_cada_recurso_segun_la_referencia(self):
        for accion in ("ec2:CreateVpcEndpoint", "ec2:ModifyVpcEndpoint"):
            for s in self._allows(accion):
                claves = {k for bloque in s.get("Condition", {}).values() for k in bloque}
                genericas = {k.split("/")[0] + "/${TagKey}" if "/" in k else k for k in claves}
                for recurso in (s["Resource"] if isinstance(s["Resource"], list) else [s["Resource"]]):
                    with self.subTest(sid=s["Sid"], recurso=_tipo(recurso)):
                        self.assertIn(_tipo(recurso), sim.CLAVES_POR_RECURSO[accion])
                        validas = sim.CLAVES_POR_RECURSO[accion][_tipo(recurso)] | sim.CLAVES_GLOBALES
                        self.assertLessEqual(genericas, validas)


if __name__ == "__main__":
    unittest.main()
