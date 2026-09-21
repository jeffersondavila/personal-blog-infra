"""Operaciones API estrechas que usa el ensayo controlado de Task/026."""

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from laboratorio import verificacion as modulo  # noqa: E402
from laboratorio import laboratorio as lanzador, inventario  # noqa: E402


class InventarioApiGatewayTests(unittest.TestCase):
    def test_respuesta_real_camel_case_no_oculta_el_api(self):
        cuerpo = {"items": [{"apiId": "abc123", "name": "blog-lab-api"}]}
        self.assertEqual(modulo.extraer_nombres_de_apis(cuerpo, prefijo="blog-lab"), ["blog-lab-api"])

    def test_pascal_case_y_filtrado_del_prefijo(self):
        cuerpo = {"Items": [{"ApiId": "abc123", "Name": "blog-lab-api"},
                            {"ApiId": "otro", "Name": "ajeno-api"}]}
        self.assertEqual(modulo.extraer_nombres_de_apis(cuerpo, prefijo="blog-lab"), ["blog-lab-api"])

    def test_lista_vacia_es_ausencia_demostrable(self):
        for clave in ("items", "Items"):
            self.assertEqual(modulo.extraer_nombres_de_apis({clave: []}, prefijo="blog-lab"), [])

    def test_respuesta_invalida_no_es_prueba_de_ausencia(self):
        for cuerpo in ({}, [], {"items": None}, {"items": [{}]}, {"items": ["api"]}):
            with self.subTest(cuerpo=cuerpo), self.assertRaises(modulo.ErrorDeVerificacion):
                modulo.extraer_nombres_de_apis(cuerpo, prefijo="blog-lab")

    def test_error_http_o_json_no_es_prueba_de_ausencia(self):
        for respuesta in ((500, b'{}'), (200, b'no-json')):
            with self.subTest(respuesta=respuesta), patch.object(modulo, "cliente") as crear:
                crear.return_value.llamar.return_value = respuesta
                with self.assertRaises(modulo.ErrorDeVerificacion):
                    modulo.apis_presentes(object(), prefijo="blog-lab", clave_aws="test", secreto="test")

    def test_inventario_con_api_no_puede_aprobar_ausencia(self):
        falso = Mock()
        falso.llamar.return_value = (200, json.dumps(
            {"items": [{"apiId": "abc123", "name": "blog-lab-api"}]}
        ).encode())
        with patch.object(modulo, "cliente", return_value=falso), \
             patch.object(modulo, "buckets_presentes", return_value=[]), \
             patch.object(modulo, "funciones_presentes", return_value=[]), \
             patch.object(modulo, "grupos_de_logs", return_value=[]), \
             patch.object(modulo, "parametros_presentes", return_value=[]):
            observado = lanzador.inventario_del_destino(object())
        self.assertEqual(observado["apigatewayv2"], ["blog-lab-api"])
        with self.assertRaises(inventario.ErrorDeInventario):
            inventario.exigir_inventario_vacio(observado)


class EliminacionDeParametroTests(unittest.TestCase):
    def test_delete_parameter_usa_el_objetivo_exacto(self):
        class ClienteFalso:
            def __init__(self):
                self.llamada = None

            def json_de_servicio(self, **argumentos):
                self.llamada = argumentos
                return 200, {}

        falso = ClienteFalso()
        with patch.object(modulo, "cliente", return_value=falso):
            estado, _ = modulo.eliminar_parametro(
                object(),
                nombre="/blog-lab/local/storage_region",
                clave_aws="test",
                secreto="test",
            )

        self.assertEqual(estado, 200)
        self.assertEqual(falso.llamada["servicio"], "ssm")
        self.assertEqual(falso.llamada["objetivo"], "AmazonSSM.DeleteParameter")
        self.assertEqual(
            falso.llamada["carga"], {"Name": "/blog-lab/local/storage_region"}
        )


if __name__ == "__main__":
    unittest.main()
