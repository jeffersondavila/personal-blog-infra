"""H-031-6 (Task/031): cableado ESTATICO de `credenciales_sql` y `exportacion` en `terraform-datos`.

Complementa `terraform-datos/tests/datos.tftest.hcl` (valores del plan con el provider simulado) y la guarda
`check_plan_h0316.py` (el plan real). Aqui se fija lo que solo se ve en el codigo:
- las dos llamadas, con sus argumentos EXACTOS y sin metaargumentos;
- las contrasenas de `blog_migrate` y `blog_app`: variables EFIMERAS, sin valor por omision, que solo llegan a
  `credenciales_sql`;
- la politica de `export` sobre el rol que crea la propia ejecutora (`module.ejecutor_privado.nombre_del_rol`);
- una sola salida nueva, con los NOMBRES de las credenciales y nunca un valor;
- la descripcion de la funcion, neutral de fase: desde H-031-6 ya no es el shell de H-031-5.
"""
import re
import unittest

from scripts.terraform_datos.check_plan_h0316 import DESCRIPCION_DE_LA_FUNCION
from tests.terraform_datos.test_modulo_ejecutor_privado import MODULO, ROOT, bloque, leer


class CableadoDeH0316(unittest.TestCase):
    def setUp(self):
        self.main = leer(ROOT / "main.tf")
        self.variables = leer(ROOT / "variables.tf")
        self.salidas = leer(ROOT / "outputs.tf")

    def exige_argumentos(self, cabecera, esperado):
        llamada = bloque(self.main, cabecera)
        for argumento, valor in esperado.items():
            with self.subTest(llamada=cabecera, argumento=argumento):
                self.assertRegex(llamada, rf"(?m)^\s*{argumento}\s*=\s*{valor}\s*$")
        self.assertEqual(sorted(re.findall(r"(?m)^\s*(\w+)\s*=", llamada)), sorted(esperado), "ningun argumento de mas")
        self.assertNotRegex(llamada, r"(?m)^\s*(count|for_each|depends_on|providers)\s*=")

    def test_credenciales_sql_con_el_cableado_exacto(self):
        self.exige_argumentos('module "credenciales_sql"', {
            "source": r'"\.\./terraform/modulos/credenciales_sql"',
            "nombre": r"var\.prefijo",
            "ruta_base": r"local\.ruta_de_datos",
            "contrasena_blog_migrate": r"var\.contrasena_blog_migrate",
            "contrasena_blog_app": r"var\.contrasena_blog_app",
            "version_de_blog_migrate": r"var\.version_de_blog_migrate",
            "version_de_blog_app": r"var\.version_de_blog_app",
        })
        locales = bloque(self.main, "locals")
        self.assertRegex(locales, r'(?m)^\s*ruta_de_datos\s*=\s*"/\$\{var\.prefijo\}/datos"\s*$')
        self.assertRegex(locales, r'(?m)^\s*ruta_de_la_master\s*=\s*"/\$\{var\.prefijo\}/datos/blogadmin"\s*$',
                         "la ruta de la master no cambia")

    def test_exportacion_con_el_cableado_exacto(self):
        self.exige_argumentos('module "exportacion"', {
            "source": r'"\.\./terraform/modulos/exportacion"',
            "nombre": r"var\.prefijo",
            "nombre_del_rol": r"module\.ejecutor_privado\.nombre_del_rol",
            "arn_del_bucket": r"var\.arn_del_bucket_de_medios",
            "id_sg_admin": r"module\.red\.id_sg_admin",
            "prefix_list_s3": r"module\.red\.prefix_list_s3",
            "id_del_endpoint_s3": r"module\.red\.id_endpoint_s3",
        })

    def test_contrasenas_efimeras_sin_valor_por_omision(self):
        for nombre in ("contrasena_blog_migrate", "contrasena_blog_app"):
            with self.subTest(variable=nombre):
                variable = bloque(self.variables, f'variable "{nombre}"')
                self.assertRegex(variable, r"(?m)^\s*sensitive\s*=\s*true\s*$")
                self.assertRegex(variable, r"(?m)^\s*ephemeral\s*=\s*true\s*$")
                self.assertNotRegex(variable, r"(?m)^\s*default\s*=")
                self.assertIn("^[A-Za-z0-9]{32,64}$", variable)
        for nombre in ("version_de_blog_migrate", "version_de_blog_app"):
            with self.subTest(variable=nombre):
                variable = bloque(self.variables, f'variable "{nombre}"')
                self.assertRegex(variable, r"(?m)^\s*default\s*=\s*1\s*$")
                self.assertRegex(variable, r"floor\(var\." + nombre + r"\)")

    def test_las_contrasenas_solo_llegan_a_credenciales_sql(self):
        llamada = bloque(self.main, 'module "credenciales_sql"')
        for nombre in ("contrasena_blog_migrate", "contrasena_blog_app"):
            with self.subTest(variable=nombre):
                self.assertEqual(len(re.findall(rf"var\.{nombre}\b", self.main + self.salidas)), 1)
                self.assertIn(f"var.{nombre}", llamada)

    def test_una_sola_salida_nueva_con_los_nombres(self):
        salida = bloque(self.salidas, 'output "nombres_de_credenciales_sql"')
        self.assertRegex(salida, r"(?m)^\s*value\s*=\s*module\.credenciales_sql\.nombres_de_los_parametros\s*$")
        self.assertNotIn("sensitive", self.salidas)
        self.assertNotIn("module.exportacion", self.salidas)
        self.assertNotIn("versiones", self.salidas)

    def test_la_ejecutora_publica_el_nombre_de_su_rol(self):
        salida = bloque(leer(MODULO / "outputs.tf"), 'output "nombre_del_rol"')
        self.assertRegex(salida, r"(?m)^\s*value\s*=\s*aws_iam_role\.this\.name\s*$")

    def test_descripcion_de_la_funcion_neutral_de_fase(self):
        funcion = bloque(leer(MODULO / "main.tf"), 'resource "aws_lambda_function" "this"')
        descripcion = re.search(r'(?m)^\s*description\s*=\s*"([^"]*)"\s*$', funcion).group(1)
        self.assertEqual(descripcion, DESCRIPCION_DE_LA_FUNCION)
        self.assertNotIn("shell", descripcion.lower())


if __name__ == "__main__":
    unittest.main()
