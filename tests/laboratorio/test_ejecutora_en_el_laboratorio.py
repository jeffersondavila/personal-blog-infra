"""El laboratorio sigue al root de datos (Task/031).

Un solo root `terraform-datos` y dos destinos (aws-local-parity.md §4.1.1). El 2026-10-08 entraron las alarmas de
D-11 (H-031-8) y el rol de D-20 (H-031-9), y la ejecutora de D-24 (H-031-5) salio mientras la cuota de Lambda no
permitia RC=1. El 2026-10-18 VUELVE, con D-24 modificada (aprobada el 2026-10-19): concurrencia no reservada. El lanzador debe:
- enviar a datos el endpoint de CloudWatch, ademas de los que ya tenia: sin el, las alarmas irian a AWS real;
- construir el artefacto FIJADO de la ejecutora y pasar una integracion de Grafana FICTICIA;
- tolerar alarmas, roles y ejecutora como recursos VIVOS del root de datos, tratarlos como residuo cuando datos
  ya se destruyo, e inventariarlos con verificaciones que no confunden una respuesta desconocida con ausencia.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from laboratorio import laboratorio as lanzador  # noqa: E402
from laboratorio import verificacion  # noqa: E402
from terraform_datos import empaquetar_ejecutor  # noqa: E402

ARN = "arn:aws:s3:::blog-lab-medios"
ALARMAS = [f"blog-lab-rds-{s}" for s in ("almacenamiento", "conexiones", "cpu", "creditos", "escritura", "lectura",
                                          "memoria", "xid")]


def destino():
    return SimpleNamespace(endpoints={s: "http://127.0.0.1:4566" for s in lanzador.mod_destino.SERVICIOS},
                           region="us-east-1")


def inventario(**valores):
    base = {clave: [] for clave in ("s3", "lambda", "apigatewayv2", "logs", "ssm", "ec2_vpc", "ec2_grupos",
                                    "rds_instancias", "rds_subredes", "rds_parametros", "logs_rds", "ssm_datos",
                                    "cloudwatch_alarmas", "iam_roles_datos")}
    base.update(valores)
    return base


class VariablesDeDatos(unittest.TestCase):
    def escribir(self):
        with tempfile.TemporaryDirectory() as directorio:
            generado = Path(directorio)
            ruta = generado / "destino.tfvars.json"
            with patch.object(lanzador, "DIRECTORIO_GENERADO_DE_DATOS", generado), patch.object(
                lanzador, "VARIABLES_GENERADAS_DE_DATOS", ruta
            ):
                with patch.object(lanzador, "preparar_ejecutor_h0316", side_effect=lambda p: (
                    p.write_bytes(b"artefacto simulado"), empaquetar_ejecutor.SHA256_ESPERADO_H0316)[1]):
                    lanzador.escribir_variables_de_datos(destino(), {"arn_del_bucket": ARN})
            return json.loads(ruta.read_text(encoding="utf-8")), sorted(p.name for p in generado.iterdir())

    def test_datos_declara_cloudwatch_ademas_de_iam_y_lambda(self):
        self.assertEqual(lanzador.ENDPOINTS_DEL_ROOT_DE_DATOS,
                         ("cloudwatch", "ec2", "iam", "lambda", "logs", "rds", "ssm", "sts"))

    def test_con_el_artefacto_fijado_de_la_ejecutora_y_grafana_ficticia(self):
        valores, archivos = self.escribir()
        self.assertEqual(valores["zip_de_la_ejecutora"]["sha256"], empaquetar_ejecutor.SHA256_ESPERADO_H0316)
        self.assertTrue(valores["zip_de_la_ejecutora"]["ruta"].endswith("/ejecutor.zip"))
        self.assertNotIn("\\", valores["zip_de_la_ejecutora"]["ruta"], "ruta con barras de Terraform")
        self.assertIn("ejecutor.zip", archivos)
        self.assertEqual(valores["integracion_grafana"], {"cuenta": "999999999999", "external_id": "laboratorio-d20"})
        self.assertEqual(set(valores["endpoints_aws"]), set(lanzador.ENDPOINTS_DEL_ROOT_DE_DATOS))
        self.assertNotIn("contrasena_master", valores)
        self.assertEqual(valores["arn_del_bucket_de_medios"], ARN)

    def test_la_cuenta_ficticia_de_grafana_no_es_la_del_emulador(self):
        self.assertNotEqual(lanzador.INTEGRACION_GRAFANA_DEL_LABORATORIO["cuenta"], "000000000000")


class RecursosVivosDelRootDeDatos(unittest.TestCase):
    def test_alarmas_roles_y_ejecutora_son_legitimos_de_datos(self):
        legitimos = lanzador.recursos_del_root_de_datos()
        self.assertEqual(sorted(legitimos["cloudwatch_alarmas"]), ALARMAS)
        self.assertEqual(sorted(legitimos["iam_roles_datos"]), ["PersonalBlogEjecutorDatos", "PersonalBlogLecturaGrafana"])
        self.assertEqual(legitimos["lambda"], ["blog-lab-ejecutor"])
        self.assertEqual(legitimos["logs"], ["/aws/lambda/blog-lab-ejecutor"])

    def test_vivos_no_son_residuo_mientras_datos_viva(self):
        lanzador.exigir_ausencia_en_el_destino(
            inventario(cloudwatch_alarmas=ALARMAS, iam_roles_datos=["PersonalBlogLecturaGrafana"]),
            bucket_de_medios_vivo=None, datos_vivos=True)

    def test_destruido_datos_son_residuo(self):
        for valores in ({"cloudwatch_alarmas": ALARMAS[:1]}, {"iam_roles_datos": ["PersonalBlogLecturaGrafana"]}):
            with self.subTest(valores=valores):
                with self.assertRaises(Exception):
                    lanzador.exigir_ausencia_en_el_destino(inventario(**valores), bucket_de_medios_vivo=None,
                                                          datos_vivos=False)

    def test_la_ejecutora_se_tolera_mientras_datos_viva(self):
        lanzador.exigir_ausencia_en_el_destino(
            inventario(**{"lambda": ["blog-lab-ejecutor"], "logs": ["/aws/lambda/blog-lab-ejecutor"],
                          "iam_roles_datos": ["PersonalBlogEjecutorDatos"]}),
            bucket_de_medios_vivo=None, datos_vivos=True)

    def test_destruido_datos_la_ejecutora_es_residuo(self):
        for valores in ({"lambda": ["blog-lab-ejecutor"]}, {"logs": ["/aws/lambda/blog-lab-ejecutor"]},
                        {"iam_roles_datos": ["PersonalBlogEjecutorDatos"]}):
            with self.subTest(valores=valores):
                with self.assertRaises(Exception):
                    lanzador.exigir_ausencia_en_el_destino(inventario(**valores), bucket_de_medios_vivo=None,
                                                          datos_vivos=False)

    def test_otra_funcion_con_el_prefijo_sigue_siendo_residuo(self):
        with self.assertRaises(Exception):
            lanzador.exigir_ausencia_en_el_destino(inventario(**{"lambda": ["blog-lab-ejecutor", "blog-lab-otra"]}),
                                                  bucket_de_medios_vivo=None, datos_vivos=True)

    def test_el_inventario_pregunta_por_los_dos_roles_de_datos(self):
        nombres = []
        sustitutos = {nombre: (lambda *a, **k: []) for nombre in dir(lanzador.mod_verificacion)
                      if nombre.endswith("_presentes") or nombre == "grupos_de_logs"}
        sustitutos["roles_presentes"] = lambda destino, nombres=(), **k: nombres_vistos(nombres)

        def nombres_vistos(valor):
            nombres.extend(valor)
            return []

        with patch.multiple(lanzador.mod_verificacion, **sustitutos):
            lanzador.inventario_del_destino(destino())
        self.assertEqual(sorted(nombres), ["PersonalBlogEjecutorDatos", "PersonalBlogLecturaGrafana"])

    def test_una_alarma_ajena_con_el_prefijo_es_residuo(self):
        with self.assertRaises(Exception):
            lanzador.exigir_ausencia_en_el_destino(
                inventario(cloudwatch_alarmas=ALARMAS + ["blog-lab-rds-backup"]), bucket_de_medios_vivo=None,
                datos_vivos=True)


class ClienteFalso:
    def __init__(self, *respuestas):
        self.respuestas, self.llamadas = list(respuestas), []

    def llamar(self, **argumentos):
        self.llamadas.append(argumentos)
        return self.respuestas.pop(0)


class VerificacionesNuevas(unittest.TestCase):
    def test_alarmas_por_describe_alarms_firmado_como_monitoring(self):
        xml = ("<DescribeAlarmsResponse><DescribeAlarmsResult><MetricAlarms>"
               "<member><AlarmName>blog-lab-rds-cpu</AlarmName></member>"
               "<member><AlarmName>otra-alarma</AlarmName></member>"
               "</MetricAlarms></DescribeAlarmsResult></DescribeAlarmsResponse>").encode()
        falso = ClienteFalso((200, xml))
        with patch.object(verificacion, "cliente", return_value=falso):
            nombres = verificacion.alarmas_presentes(object(), prefijo="blog-lab-", clave_aws="t", secreto="t")
        self.assertEqual(nombres, ["blog-lab-rds-cpu"])
        llamada = falso.llamadas[0]
        self.assertEqual((llamada["servicio"], llamada["metodo"], llamada["ruta"]), ("monitoring", "POST", "/"))
        self.assertEqual(llamada["cuerpo"], b"Action=DescribeAlarms&Version=2010-08-01&AlarmNamePrefix=blog-lab-")

    def test_una_respuesta_desconocida_no_demuestra_ausencia(self):
        for respuesta in ((500, b"<Error/>"), (200, b"no-xml")):
            with self.subTest(respuesta=respuesta):
                with patch.object(verificacion, "cliente", return_value=ClienteFalso(respuesta)):
                    with self.assertRaises(verificacion.ErrorDeVerificacion):
                        verificacion.alarmas_presentes(object(), prefijo="blog-lab-", clave_aws="t", secreto="t")

    def test_roles_por_get_role(self):
        with patch.object(verificacion, "describir_rol", side_effect=[(200, "<GetRoleResponse/>"), (404, "")]):
            self.assertEqual(verificacion.roles_presentes(object(), nombres=("Uno", "Dos"), clave_aws="t",
                                                          secreto="t"), ["Uno"])
        with patch.object(verificacion, "describir_rol", return_value=(500, "")):
            with self.assertRaises(verificacion.ErrorDeVerificacion):
                verificacion.roles_presentes(object(), nombres=("Uno",), clave_aws="t", secreto="t")


if __name__ == "__main__":
    unittest.main()
