"""H-031-6: tres canarios, artefacto vigente y deteccion de los dos SSM en el laboratorio."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tests.laboratorio.test_ejecutora_en_el_laboratorio import lanzador, destino, ARN, inventario


class H0316(unittest.TestCase):
    def test_los_tres_parametros_son_de_datos_y_no_residuos(self):
        nombres = [f"/blog-lab/datos/{r}" for r in ("blogadmin", "blog_migrate", "blog_app")]
        self.assertEqual(lanzador.recursos_del_root_de_datos()["ssm_datos"], nombres)
        lanzador.exigir_ausencia_en_el_destino(inventario(ssm_datos=nombres), datos_vivos=True, bucket_de_medios_vivo=None)
        with self.assertRaises(Exception):
            lanzador.exigir_ausencia_en_el_destino(inventario(ssm_datos=nombres), datos_vivos=False, bucket_de_medios_vivo=None)

    def test_tres_efimeras_independientes_y_solo_en_su_archivo(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d)/"destino.tfvars.json"
            with patch.object(lanzador, "DIRECTORIO_GENERADO_DE_DATOS", Path(d)), patch.object(
                lanzador, "VARIABLES_GENERADAS_DE_DATOS", ruta
            ), patch.object(lanzador, "preparar_ejecutor_h0316", create=True, return_value="a" * 64):
                lanzador.escribir_variables_de_datos(destino(), {"arn_del_bucket": ARN})
                valores = json.loads(ruta.read_text(encoding="utf-8"))
                efimeras = json.loads(lanzador.ruta_de_las_efimeras_de_datos().read_text(encoding="utf-8"))
        self.assertEqual(set(efimeras), {"contrasena_master", "contrasena_blog_migrate", "contrasena_blog_app"})
        self.assertEqual(len(set(efimeras.values())), 3)
        self.assertFalse(set(efimeras) & set(valores))

    def test_rechaza_zip_ausente_o_alterado(self):
        with tempfile.TemporaryDirectory() as d:
            origen, destino_zip = Path(d)/"origen.zip", Path(d)/"destino.zip"
            origen.write_bytes(b"no es el artefacto fijado")
            for valor in ("", str(origen)):
                with patch.dict(os.environ, {"PERSONAL_BLOG_EJECUTOR_ZIP": valor}):
                    with self.assertRaises(lanzador.ErrorDelLaboratorio):
                        lanzador.preparar_ejecutor_h0316(destino_zip)
                self.assertFalse(destino_zip.exists())
