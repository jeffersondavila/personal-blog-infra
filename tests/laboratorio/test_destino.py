"""Guardas fail-closed del destino del laboratorio (Task/025, matriz 1-26, 38).

Ningun test de este archivo abre un socket. Los controles negativos usan
entradas sinteticas y destinos locales falsos: el fallo debe ocurrir **antes**
de que el lanzador invoque a Terraform, no despues.
"""

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from laboratorio import destino as guarda  # noqa: E402
from ejemplo_canonico_de_aws import (  # noqa: E402
    CLAVE_CON_FORMA_REAL,
    SECRETO_DEL_EJEMPLO,
)


def entorno_valido(**cambios):
    """Entorno minimo que la guarda debe aceptar para el modo local."""
    base = {
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test",
        "AWS_REGION": "us-east-1",
        "AWS_DEFAULT_REGION": "us-east-1",
        "AWS_EC2_METADATA_DISABLED": "true",
        "PATH": "/usr/bin",
    }
    for servicio in guarda.SERVICIOS:
        base["LAB_ENDPOINT_" + servicio.upper()] = "http://127.0.0.1:4566"
    base.update(cambios)
    return {k: v for k, v in base.items() if v is not None}


class ModoTests(unittest.TestCase):
    def test_modo_local_valido_resuelve(self):
        resuelto = guarda.resolver_destino(entorno_valido(), modo="local")
        self.assertEqual(resuelto.modo, "local")
        self.assertEqual(resuelto.region, "us-east-1")
        self.assertEqual(resuelto.cuenta_esperada, "000000000000")
        self.assertEqual(set(resuelto.endpoints), set(guarda.SERVICIOS))

    def test_modo_ausente_aborta(self):
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(entorno_valido(), modo=None)

    def test_modo_vacio_aborta(self):
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(entorno_valido(), modo="")

    def test_modo_desconocido_aborta(self):
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(entorno_valido(), modo="staging")

    def test_modo_production_aborta(self):
        """Task/025 no tiene autorizacion de AWS real: production se rechaza."""
        with self.assertRaises(guarda.ErrorDeDestino) as capturado:
            guarda.resolver_destino(entorno_valido(), modo="production")
        self.assertIn("production", str(capturado.exception))

    def test_modo_no_distingue_mayusculas_por_accidente(self):
        """`LOCAL` no es `local`: el modo es exacto, sin normalizacion silenciosa."""
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(entorno_valido(), modo="LOCAL")


class EndpointTests(unittest.TestCase):
    def test_endpoint_omitido_aborta_y_nombra_el_servicio(self):
        entorno = entorno_valido(LAB_ENDPOINT_LAMBDA=None)
        with self.assertRaises(guarda.ErrorDeDestino) as capturado:
            guarda.resolver_destino(entorno, modo="local")
        self.assertIn("lambda", str(capturado.exception))

    def test_endpoint_vacio_aborta(self):
        entorno = entorno_valido(LAB_ENDPOINT_S3="")
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(entorno, modo="local")

    def test_cada_servicio_es_obligatorio(self):
        for servicio in guarda.SERVICIOS:
            with self.subTest(servicio=servicio):
                entorno = entorno_valido(**{"LAB_ENDPOINT_" + servicio.upper(): None})
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(entorno, modo="local")

    def test_endpoint_de_aws_publico_aborta(self):
        for valor in (
            "https://s3.amazonaws.com",
            "https://s3.us-east-1.amazonaws.com",
            "https://lambda.us-east-1.amazonaws.com",
        ):
            with self.subTest(valor=valor):
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(entorno_valido(LAB_ENDPOINT_S3=valor), modo="local")

    def test_host_inesperado_aborta(self):
        for valor in (
            "http://192.168.1.9:4566",
            "http://10.0.0.5:4566",
            "http://floci.example.com:4566",
            "http://169.254.169.254:80",
        ):
            with self.subTest(valor=valor):
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(entorno_valido(LAB_ENDPOINT_S3=valor), modo="local")

    def test_endpoint_con_userinfo_aborta(self):
        entorno = entorno_valido(LAB_ENDPOINT_S3="http://usuario:clave@127.0.0.1:4566")
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(entorno, modo="local")

    def test_endpoint_sin_puerto_aborta(self):
        entorno = entorno_valido(LAB_ENDPOINT_S3="http://127.0.0.1")
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(entorno, modo="local")

    def test_esquema_no_http_aborta(self):
        for valor in ("ftp://127.0.0.1:4566", "file:///tmp/x", "127.0.0.1:4566"):
            with self.subTest(valor=valor):
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(entorno_valido(LAB_ENDPOINT_S3=valor), modo="local")

    def test_localhost_es_aceptable(self):
        entorno = entorno_valido(LAB_ENDPOINT_S3="http://localhost:4566")
        resuelto = guarda.resolver_destino(entorno, modo="local")
        self.assertEqual(resuelto.endpoints["s3"], "http://localhost:4566")


class CredencialTests(unittest.TestCase):
    def test_credencial_real_aborta_sin_filtrar_el_valor(self):
        # Credencial publica de ejemplo, partida en `ejemplo_canonico_de_aws`.
        # La prueba solo necesita que NO sea la fixture del emulador y que su
        # valor no acabe en el mensaje de error.
        secreto = CLAVE_CON_FORMA_REAL
        entorno = entorno_valido(AWS_ACCESS_KEY_ID=secreto)
        with self.assertRaises(guarda.ErrorDeDestino) as capturado:
            guarda.resolver_destino(entorno, modo="local")
        self.assertNotIn(secreto, str(capturado.exception))

    def test_secreto_real_aborta_sin_filtrar_el_valor(self):
        secreto = SECRETO_DEL_EJEMPLO
        entorno = entorno_valido(AWS_SECRET_ACCESS_KEY=secreto)
        with self.assertRaises(guarda.ErrorDeDestino) as capturado:
            guarda.resolver_destino(entorno, modo="local")
        self.assertNotIn(secreto, str(capturado.exception))

    def test_credencial_ausente_aborta(self):
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(entorno_valido(AWS_ACCESS_KEY_ID=None), modo="local")

    def test_session_token_inesperado_aborta(self):
        for nombre in ("AWS_SESSION_TOKEN", "AWS_SECURITY_TOKEN"):
            with self.subTest(nombre=nombre):
                entorno = entorno_valido(**{nombre: "token-de-sesion"})
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(entorno, modo="local")

    def test_perfil_heredado_aborta(self):
        for nombre in ("AWS_PROFILE", "AWS_DEFAULT_PROFILE"):
            with self.subTest(nombre=nombre):
                entorno = entorno_valido(**{nombre: "default"})
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(entorno, modo="local")

    def test_archivos_de_credenciales_abortan(self):
        for nombre in ("AWS_SHARED_CREDENTIALS_FILE", "AWS_CONFIG_FILE"):
            with self.subTest(nombre=nombre):
                entorno = entorno_valido(**{nombre: "/home/u/.aws/credentials"})
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(entorno, modo="local")

    def test_web_identity_y_sso_abortan(self):
        for nombre in (
            "AWS_WEB_IDENTITY_TOKEN_FILE",
            "AWS_ROLE_ARN",
            "AWS_ROLE_SESSION_NAME",
        ):
            with self.subTest(nombre=nombre):
                entorno = entorno_valido(**{nombre: "valor"})
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(entorno, modo="local")

    def test_credenciales_de_contenedor_abortan(self):
        for nombre in (
            "AWS_CONTAINER_CREDENTIALS_FULL_URI",
            "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI",
            "AWS_CONTAINER_AUTHORIZATION_TOKEN",
        ):
            with self.subTest(nombre=nombre):
                entorno = entorno_valido(**{nombre: "http://169.254.170.2/creds"})
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(entorno, modo="local")


class EntornoTests(unittest.TestCase):
    def test_metadata_habilitada_aborta(self):
        for valor in (None, "false", "0", "", "TRUE"):
            with self.subTest(valor=valor):
                entorno = entorno_valido(AWS_EC2_METADATA_DISABLED=valor)
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(entorno, modo="local")

    def test_endpoint_de_metadata_aborta(self):
        for nombre in (
            "AWS_EC2_METADATA_SERVICE_ENDPOINT",
            "AWS_EC2_METADATA_SERVICE_ENDPOINT_MODE",
        ):
            with self.subTest(nombre=nombre):
                entorno = entorno_valido(**{nombre: "http://169.254.169.254"})
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(entorno, modo="local")

    def test_proxy_externo_aborta(self):
        for nombre in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY"):
            with self.subTest(nombre=nombre):
                entorno = entorno_valido(**{nombre: "http://proxy.corp:3128"})
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(entorno, modo="local")

    def test_override_de_terraform_heredado_aborta(self):
        for nombre in ("TF_CLI_ARGS", "TF_CLI_ARGS_plan", "TF_CLI_ARGS_apply", "TF_CLI_CONFIG_FILE"):
            with self.subTest(nombre=nombre):
                entorno = entorno_valido(**{nombre: "-refresh=false"})
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(entorno, modo="local")

    def test_endpoint_url_global_externo_aborta(self):
        entorno = entorno_valido(AWS_ENDPOINT_URL="https://s3.amazonaws.com")
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(entorno, modo="local")

    def test_endpoint_url_global_local_es_aceptable(self):
        entorno = entorno_valido(AWS_ENDPOINT_URL="http://127.0.0.1:4566")
        resuelto = guarda.resolver_destino(entorno, modo="local")
        self.assertEqual(resuelto.modo, "local")

    def test_endpoint_url_por_servicio_externo_aborta(self):
        entorno = entorno_valido(AWS_ENDPOINT_URL_S3="https://s3.amazonaws.com")
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(entorno, modo="local")

    def test_region_inesperada_aborta(self):
        entorno = entorno_valido(AWS_REGION="eu-west-1")
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(entorno, modo="local")

    def test_region_ausente_aborta(self):
        entorno = entorno_valido(AWS_REGION=None)
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(entorno, modo="local")

    def test_region_por_defecto_discordante_aborta(self):
        entorno = entorno_valido(AWS_DEFAULT_REGION="eu-west-1")
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(entorno, modo="local")


class EntornoHijoTests(unittest.TestCase):
    def test_entorno_hijo_esta_curado(self):
        """El proceso hijo recibe una allowlist, no el entorno del host."""
        resuelto = guarda.resolver_destino(entorno_valido(), modo="local")
        hijo = guarda.entorno_para_terraform(
            resuelto,
            entorno={
                "PATH": "/usr/bin",
                "AWS_PROFILE": "produccion",
                "HTTPS_PROXY": "http://proxy.corp:3128",
                "SECRETO_DEL_HOST": "no-debe-pasar",
                "TF_CLI_ARGS": "-refresh=false",
            },
        )
        self.assertNotIn("AWS_PROFILE", hijo)
        self.assertNotIn("HTTPS_PROXY", hijo)
        self.assertNotIn("SECRETO_DEL_HOST", hijo)
        self.assertNotIn("TF_CLI_ARGS", hijo)
        self.assertEqual(hijo["AWS_ACCESS_KEY_ID"], "test")
        self.assertEqual(hijo["AWS_REGION"], "us-east-1")
        self.assertEqual(hijo["AWS_EC2_METADATA_DISABLED"], "true")

    def test_entorno_hijo_no_lleva_endpoints_globales(self):
        """Los endpoints viajan como variables de Terraform, no como override global."""
        resuelto = guarda.resolver_destino(entorno_valido(), modo="local")
        hijo = guarda.entorno_para_terraform(resuelto, entorno={"PATH": "/usr/bin"})
        self.assertNotIn("AWS_ENDPOINT_URL", hijo)


class IdentidadTests(unittest.TestCase):
    def test_cuenta_esperada_continua(self):
        resuelto = guarda.resolver_destino(entorno_valido(), modo="local")
        observada = guarda.confirmar_identidad(resuelto, lambda _: "000000000000")
        self.assertEqual(observada, "000000000000")

    def test_cuenta_inesperada_aborta(self):
        resuelto = guarda.resolver_destino(entorno_valido(), modo="local")
        with self.assertRaises(guarda.ErrorDeDestino) as capturado:
            guarda.confirmar_identidad(resuelto, lambda _: "123456789012")
        self.assertIn("123456789012", str(capturado.exception))

    def test_cuenta_vacia_aborta(self):
        resuelto = guarda.resolver_destino(entorno_valido(), modo="local")
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.confirmar_identidad(resuelto, lambda _: "")


class LockDeEscrituraTests(unittest.TestCase):
    def test_una_sola_operacion_escritora(self):
        """La segunda ejecucion concurrente aborta en lugar de compartir estado."""
        with tempfile.TemporaryDirectory(prefix="task025-lock-") as directorio:
            ruta = Path(directorio) / "laboratorio.lock"
            with guarda.lock_de_escritura(ruta):
                with self.assertRaises(guarda.ErrorDeDestino):
                    with guarda.lock_de_escritura(ruta):
                        pass

    def test_el_lock_se_libera_al_salir(self):
        with tempfile.TemporaryDirectory(prefix="task025-lock-") as directorio:
            ruta = Path(directorio) / "laboratorio.lock"
            with guarda.lock_de_escritura(ruta):
                pass
            with guarda.lock_de_escritura(ruta):
                pass
            self.assertFalse(ruta.exists())


if __name__ == "__main__":
    unittest.main()
