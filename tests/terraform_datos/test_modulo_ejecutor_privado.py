"""H-031-5: contrato ESTATICO del modulo `ejecutor_privado` y de su cableado en `terraform-datos` (Task/031).

Complementa `terraform-datos/tests/datos.tftest.hcl`, que prueba los valores del plan con el provider simulado.
Aqui se demuestra lo que una asercion de plan no puede ver: la AUSENCIA de recursos no autorizados en todo el grafo de
datos (URL publica, permisos de invocacion, disparadores, NAT, IGW, EIP, IAM adicional), el contrato cerrado de
variables y salidas del modulo y el cableado exacto desde el root. Desde H-031-6 el grafo incluye `credenciales_sql`
y `exportacion`, y `sg-admin` tiene una segunda salida legitima: S3 por la prefix list del gateway endpoint.
"""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MODULO = RAIZ / "terraform" / "modulos" / "ejecutor_privado"
ROOT = RAIZ / "terraform-datos"
FUENTES_DEL_GRAFO = [
    *sorted(ROOT.glob("*.tf")),
    *sorted((RAIZ / "terraform" / "modulos" / "red").glob("*.tf")),
    *sorted((RAIZ / "terraform" / "modulos" / "base_de_datos").glob("*.tf")),
    *sorted(MODULO.glob("*.tf")),
    *sorted((RAIZ / "terraform" / "modulos" / "credenciales_sql").glob("*.tf")),
    *sorted((RAIZ / "terraform" / "modulos" / "exportacion").glob("*.tf")),
]
RECURSOS_DEL_MODULO = {
    ("aws_cloudwatch_log_group", "this"),
    ("aws_iam_role", "this"),
    ("aws_iam_role_policy", "this"),
    ("aws_lambda_function", "this"),
}
TIPOS_NO_AUTORIZADOS = (
    "aws_lambda_permission", "aws_lambda_function_url", "aws_lambda_event_source_mapping",
    "aws_lambda_function_event_invoke_config", "aws_lambda_alias", "aws_lambda_layer_version",
    "aws_lambda_provisioned_concurrency_config", "aws_iam_role_policy_attachment", "aws_iam_policy",
    "aws_iam_user", "aws_iam_access_key", "aws_nat_gateway", "aws_internet_gateway",
    "aws_egress_only_internet_gateway", "aws_eip", "aws_apigatewayv2_api", "aws_cloudwatch_event_rule",
    "aws_scheduler_schedule", "aws_secretsmanager_secret", "aws_kms_key", "aws_default_security_group",
)
VARIABLES_DEL_MODULO = {"nombre", "nombre_del_rol", "region", "cuenta", "ids_de_subredes", "id_sg_admin",
                        "ruta_del_zip", "sha256_del_zip", "dias_de_retencion_de_logs"}


def sin_comentarios(texto):
    return "\n".join(re.sub(r"\s*#.*$", "", linea) for linea in texto.splitlines())


def leer(ruta):
    return sin_comentarios(ruta.read_text(encoding="utf-8"))


def bloque(codigo, cabecera):
    """Cuerpo de un bloque de primer nivel, hasta la llave de cierre en la columna 0."""
    coincidencia = re.search(re.escape(cabecera) + r"\s*\{(.*?)\n\}", codigo, re.S)
    if not coincidencia:
        raise AssertionError(f"no existe el bloque {cabecera}")
    return coincidencia.group(1)


class ModuloCerrado(unittest.TestCase):
    def setUp(self):
        self.main = leer(MODULO / "main.tf")

    def test_existen_los_archivos_del_modulo_y_su_codigo(self):
        for nombre in ("main.tf", "variables.tf", "outputs.tf", "codigo/ejecutor.py"):
            with self.subTest(archivo=nombre):
                self.assertTrue((MODULO / nombre).is_file())

    def test_recursos_exactos_y_sin_data_sources(self):
        recursos = set(re.findall(r'^resource\s+"(\w+)"\s+"(\w+)"', self.main, re.M))
        self.assertEqual(recursos, RECURSOS_DEL_MODULO)
        self.assertNotRegex(self.main, r'^data\s+"', "sin data sources: todo el plan se conoce de antemano")

    def test_funcion_privada_solo_con_sg_admin(self):
        funcion = bloque(self.main, 'resource "aws_lambda_function" "this"')
        self.assertRegex(funcion, r"subnet_ids\s*=\s*var\.ids_de_subredes\b")
        self.assertRegex(funcion, r"security_group_ids\s*=\s*\[var\.id_sg_admin\]")
        self.assertRegex(funcion, r"ipv6_allowed_for_dual_stack\s*=\s*false")
        for prohibido in ("sg_lambda", "id_sg_rds", "default"):
            self.assertNotIn(prohibido, funcion)

    def test_runtime_handler_literales_y_sin_concurrencia_reservada(self):
        """D-24 modificada el 2026-10-18 (aprobada el 2026-10-19): concurrencia NO reservada y sin provisionada."""
        funcion = bloque(self.main, 'resource "aws_lambda_function" "this"')
        self.assertRegex(funcion, r'runtime\s*=\s*"python3\.12"')
        self.assertRegex(funcion, r'architectures\s*=\s*\["x86_64"\]')
        self.assertRegex(funcion, r'handler\s*=\s*"ejecutor\.manejar"')
        self.assertNotIn("reserved_concurrent_executions", funcion)
        self.assertNotIn("aws_lambda_provisioned_concurrency_config", self.main)
        self.assertRegex(funcion, r"source_code_hash\s*=\s*filebase64sha256\(var\.ruta_del_zip\)")
        self.assertRegex(funcion, r"filesha256\(var\.ruta_del_zip\)\s*==\s*var\.sha256_del_zip")

    def test_sin_entorno_capas_ni_ignore_changes(self):
        for prohibido in ("environment", "layers", "ignore_changes", "kms_key_arn", "file_system_config",
                          "image_uri", "s3_bucket", "logging_config", "dead_letter_config"):
            with self.subTest(prohibido=prohibido):
                self.assertNotIn(prohibido, self.main)

    def test_politica_sin_ssm_kms_s3_ni_rds(self):
        for prohibido in ('"ssm:', '"kms:', '"s3:', '"rds', '"secretsmanager:', '"iam:', '"lambda:Invoke',
                          '"sts:Get', "NotAction", "NotResource"):
            with self.subTest(prohibido=prohibido):
                self.assertNotIn(prohibido, self.main)

    def test_variables_cerradas_sin_arns_de_parametros(self):
        variables = set(re.findall(r'^variable\s+"(\w+)"', leer(MODULO / "variables.tf"), re.M))
        self.assertEqual(variables, VARIABLES_DEL_MODULO)

    def test_salidas_minimas_no_sensibles(self):
        salidas_texto = leer(MODULO / "outputs.tf")
        self.assertEqual(set(re.findall(r'^output\s+"(\w+)"', salidas_texto, re.M)),
                         {"nombre", "arn", "configuracion_efectiva", "nombre_del_rol"})
        self.assertNotIn("sensitive", salidas_texto)


class GrafoDeDatosSinLoNoAutorizado(unittest.TestCase):
    def test_hay_fuentes_del_grafo(self):
        self.assertGreaterEqual(len(FUENTES_DEL_GRAFO), 12)

    def test_ningun_tipo_no_autorizado(self):
        for fuente in FUENTES_DEL_GRAFO:
            codigo = leer(fuente)
            for tipo in TIPOS_NO_AUTORIZADOS:
                with self.subTest(fuente=fuente.name, tipo=tipo):
                    self.assertNotRegex(codigo, rf'(resource|data)\s+"{tipo}"')

    def test_sg_admin_sale_solo_a_rds_y_a_s3_por_la_prefix_list(self):
        """H-031-5 solo tenia `sg-admin -> sg-rds:5432`. H-031-6 anade, con `exportacion`, `sg-admin -> S3:443` por
        la prefix list del gateway endpoint, para el modo `export`: nunca un CIDR."""
        reglas = re.findall(r'resource\s+"aws_vpc_security_group_egress_rule"\s+"(\w+)"\s*\{(.*?)\n\}',
                            "\n".join(leer(f) for f in FUENTES_DEL_GRAFO), re.S)
        de_admin = {nombre: cuerpo for nombre, cuerpo in reglas
                    if re.search(r"security_group_id\s*=\s*(aws_security_group\.admin\.id|var\.id_sg_admin)\b", cuerpo)}
        self.assertEqual(sorted(de_admin), ["admin_a_rds", "admin_a_s3"])
        self.assertRegex(de_admin["admin_a_s3"], r"prefix_list_id\s*=\s*var\.prefix_list_s3\b")
        self.assertRegex(de_admin["admin_a_s3"], r"from_port\s*=\s*443\b")
        self.assertRegex(de_admin["admin_a_s3"], r"to_port\s*=\s*443\b")
        self.assertNotRegex(de_admin["admin_a_s3"], r"cidr_ipv[46]|referenced_security_group_id")
        self.assertNotRegex(leer(MODULO / "main.tf"), r'resource\s+"aws_vpc_security_group')


class CableadoDesdeElRoot(unittest.TestCase):
    """D-24 modificada el 2026-10-18 (aprobada el 2026-10-19): sin RC=1 ya no hay que esperar a la cuota de Lambda, y la ejecutora
    VUELVE al root con el contrato de regreso que dejo la decision del 2026-10-08. Fija la llamada exacta:
    - solo `sg-admin` y las dos subredes de `module.red`;
    - el artefacto declarado por variable;
    - la cuenta del operador;
    - sus dos salidas, ninguna sensible.
    """

    def setUp(self):
        self.main = leer(ROOT / "main.tf")
        self.llamada = bloque(self.main, 'module "ejecutor_privado"')

    def test_el_root_llama_a_la_ejecutora_con_el_cableado_exacto(self):
        esperado = {
            "source": r'"\.\./terraform/modulos/ejecutor_privado"',
            "nombre": r'"\$\{var\.prefijo\}-ejecutor"',
            "nombre_del_rol": r'"PersonalBlogEjecutorDatos"',
            "region": r"var\.region",
            "cuenta": r"data\.aws_caller_identity\.operador\.account_id",
            "ids_de_subredes": r"module\.red\.ids_de_subredes",
            "id_sg_admin": r"module\.red\.id_sg_admin",
            "ruta_del_zip": r"var\.zip_de_la_ejecutora\.ruta",
            "sha256_del_zip": r"var\.zip_de_la_ejecutora\.sha256",
            "dias_de_retencion_de_logs": r"var\.dias_de_retencion_de_logs",
        }
        for argumento, valor in esperado.items():
            with self.subTest(argumento=argumento):
                self.assertRegex(self.llamada, rf"(?m)^\s*{argumento}\s*=\s*{valor}\s*$")
        argumentos = re.findall(r"(?m)^\s*(\w+)\s*=", self.llamada)
        self.assertEqual(sorted(argumentos), sorted(esperado), "ningun argumento de mas")
        for prohibido in ("sg_lambda", "id_sg_rds", "reserved_concurrent_executions"):
            self.assertNotIn(prohibido, self.llamada)
        self.assertNotRegex(self.llamada, r"(?m)^\s*(count|for_each)\s*=", "una sola ejecutora, sin metaargumentos")

    def test_salidas_y_variable_del_artefacto(self):
        salidas = leer(ROOT / "outputs.tf")
        self.assertRegex(bloque(salidas, 'output "nombre_de_la_ejecutora"'),
                         r"value\s*=\s*module\.ejecutor_privado\.nombre")
        self.assertRegex(bloque(salidas, 'output "arn_de_la_ejecutora"'),
                         r"value\s*=\s*module\.ejecutor_privado\.arn")
        self.assertNotIn("sensitive", salidas)
        variable = bloque(leer(ROOT / "variables.tf"), 'variable "zip_de_la_ejecutora"')
        self.assertRegex(variable, r"ruta\s*=\s*string")
        self.assertRegex(variable, r"sha256\s*=\s*string")
        self.assertNotIn("default", variable)

    def test_el_provider_declara_iam_y_lambda(self):
        proveedor = leer(ROOT / "providers.tf")
        variables = bloque(leer(ROOT / "variables.tf"), 'variable "endpoints_aws"')
        for servicio in ("iam", "lambda"):
            with self.subTest(servicio=servicio):
                self.assertRegex(proveedor, rf"{servicio}\s*=\s*var\.endpoints_aws\.{servicio}")
                self.assertRegex(variables, rf"{servicio}\s*=\s*optional\(string\)")


if __name__ == "__main__":
    unittest.main()
