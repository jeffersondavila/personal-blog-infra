"""Decisiones de IAM, offline, de las politicas nuevas de H-031-6 (export) y H-031-9 (D-20) (Task/031).

Se renderizan las MISMAS plantillas que usa Terraform y se evaluan con el evaluador del repositorio
(`simulacion_de_politicas.py`, contexto pesimista). Cada politica tiene casos positivos y controles negativos.
No sustituye a `simulate-custom-policy` ni al readback en AWS: los anticipa con la misma matriz.
"""
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import simulacion_de_politicas as sim  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
CUENTA = "123456789012"
BUCKET = "blog-prod-medios-simulado"
VPCE = "vpce-0123456789abcdef0"


def renderizar(ruta, **valores):
    texto = ruta.read_text(encoding="utf-8")
    faltan = set(re.findall(r"\$\{(\w+)\}", texto)) - set(valores)
    if faltan:
        raise AssertionError(f"plantilla con variables sin valor: {sorted(faltan)}")
    return json.loads(re.sub(r"\$\{(\w+)\}", lambda m: valores[m.group(1)], texto))


class Exportacion(unittest.TestCase):
    def setUp(self):
        self.documento = renderizar(RAIZ / "terraform" / "modulos" / "exportacion" / "politica.json.tftpl",
                                    arn_del_bucket=f"arn:aws:s3:::{BUCKET}", prefijo="exportaciones/",
                                    id_del_endpoint_s3=VPCE)
        self.objeto = f"arn:aws:s3:::{BUCKET}/exportaciones/20261007T120000Z/manifiesto.json"
        self.contexto = {"s3:if-none-match": "*", "aws:SourceVpce": VPCE}

    def decision(self, accion, recurso, contexto):
        return sim.evaluar([self.documento], accion, recurso, contexto)

    def test_escritura_condicional_en_el_prefijo_por_el_endpoint(self):
        self.assertEqual(self.decision("s3:PutObject", self.objeto, self.contexto), "allowed")

    def test_controles_negativos(self):
        casos = (
            ("sin If-None-Match: podria pisar una exportacion", "s3:PutObject", self.objeto, {"aws:SourceVpce": VPCE}),
            ("If-None-Match distinto", "s3:PutObject", self.objeto, {**self.contexto, "s3:if-none-match": "etag"}),
            ("fuera del gateway endpoint", "s3:PutObject", self.objeto, {"s3:if-none-match": "*"}),
            ("otro endpoint", "s3:PutObject", self.objeto, {**self.contexto, "aws:SourceVpce": "vpce-otro"}),
            ("prefijo de medios de la aplicacion", "s3:PutObject", f"arn:aws:s3:::{BUCKET}/medios/x/original.png",
             self.contexto),
            ("otro bucket", "s3:PutObject", "arn:aws:s3:::otro-bucket/exportaciones/x.csv", self.contexto),
            ("lectura", "s3:GetObject", self.objeto, self.contexto),
            ("borrado", "s3:DeleteObject", self.objeto, self.contexto),
            ("listado", "s3:ListBucket", f"arn:aws:s3:::{BUCKET}", self.contexto),
            ("ACL", "s3:PutObjectAcl", self.objeto, self.contexto),
            ("etiquetas", "s3:PutObjectTagging", self.objeto, self.contexto),
        )
        for descripcion, accion, recurso, contexto in casos:
            with self.subTest(caso=descripcion):
                self.assertEqual(self.decision(accion, recurso, contexto), "implicitDeny")


class LecturaGrafana(unittest.TestCase):
    def setUp(self):
        self.documento = renderizar(RAIZ / "terraform" / "modulos" / "lectura_grafana" / "politica.json.tftpl",
                                    cuenta=CUENTA, region="us-east-2", prefijo="blog-prod")
        self.region = {"aws:RequestedRegion": "us-east-2"}

    def decision(self, accion, recurso="*", contexto=None):
        return sim.evaluar([self.documento], accion, recurso, self.region if contexto is None else contexto)

    def test_metricas_y_estados_de_las_alarmas_del_proyecto(self):
        self.assertEqual(self.decision("cloudwatch:GetMetricData"), "allowed")
        self.assertEqual(self.decision("cloudwatch:ListMetrics"), "allowed")
        self.assertEqual(self.decision("cloudwatch:DescribeAlarms",
                                       f"arn:aws:cloudwatch:us-east-2:{CUENTA}:alarm:blog-prod-rds-cpu"), "allowed")

    def test_controles_negativos_de_acciones_mutantes_y_ajenas(self):
        alarma = f"arn:aws:cloudwatch:us-east-2:{CUENTA}:alarm:blog-prod-rds-cpu"
        casos = (
            ("otra region", "cloudwatch:GetMetricData", "*", {"aws:RequestedRegion": "us-east-1"}),
            ("sin region en el contexto", "cloudwatch:ListMetrics", "*", {}),
            ("alarmas de otro prefijo", "cloudwatch:DescribeAlarms",
             f"arn:aws:cloudwatch:us-east-2:{CUENTA}:alarm:otro-proyecto-cpu", None),
            ("crear o cambiar alarmas", "cloudwatch:PutMetricAlarm", alarma, None),
            ("borrar alarmas", "cloudwatch:DeleteAlarms", alarma, None),
            ("forzar estados", "cloudwatch:SetAlarmState", alarma, None),
            ("publicar metricas", "cloudwatch:PutMetricData", "*", None),
            ("leer logs de PostgreSQL", "logs:GetLogEvents",
             f"arn:aws:logs:us-east-2:{CUENTA}:log-group:/aws/rds/instance/blog-prod-postgres/postgresql:log-stream:x",
             None),
            ("consultar logs", "logs:StartQuery", "*", None),
            ("filtrar logs", "logs:FilterLogEvents", "*", None),
            ("RDS", "rds:ModifyDBInstance", f"arn:aws:rds:us-east-2:{CUENTA}:db:blog-prod-postgres", None),
            ("secretos", "ssm:GetParameter", f"arn:aws:ssm:us-east-2:{CUENTA}:parameter/blog-prod/datos/blogadmin", None),
            ("S3", "s3:GetObject", f"arn:aws:s3:::{BUCKET}/exportaciones/x.csv", None),
            ("ejecutora", "lambda:InvokeFunction", f"arn:aws:lambda:us-east-2:{CUENTA}:function:blog-prod-ejecutor", None),
            ("IAM", "iam:PassRole", "*", None),
            ("otros roles", "sts:AssumeRole", "*", None),
            ("KMS", "kms:Decrypt", "*", None),
        )
        for descripcion, accion, recurso, contexto in casos:
            with self.subTest(caso=descripcion):
                self.assertEqual(self.decision(accion, recurso, contexto), "implicitDeny")

    def test_la_confianza_solo_admite_la_cuenta_de_grafana_con_external_id(self):
        confianza = renderizar(RAIZ / "terraform" / "modulos" / "lectura_grafana" / "confianza.json.tftpl",
                               cuenta_de_grafana="999999999999", external_id="stack-simulado-12345")
        (sentencia,) = confianza["Statement"]
        self.assertEqual(sentencia["Principal"], {"AWS": "arn:aws:iam::999999999999:root"})
        self.assertEqual(sentencia["Action"], "sts:AssumeRole")
        self.assertEqual(sentencia["Condition"], {"StringEquals": {"sts:ExternalId": "stack-simulado-12345"}})


if __name__ == "__main__":
    unittest.main()
