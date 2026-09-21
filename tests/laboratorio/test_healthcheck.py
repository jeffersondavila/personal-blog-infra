"""Ejecuta la sonda del Compose con solo builtins de Bash y HTTP controlado."""

import json
import os
from pathlib import Path
import re
import shutil
import socketserver
import subprocess
import tempfile
import textwrap
import threading
import unittest

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ROOT / "laboratorio/docker-compose.laboratorio.yml"
BASH = shutil.which("bash")
if os.name == "nt" and Path("C:/Program Files/Git/bin/bash.exe").exists():
    BASH = "C:/Program Files/Git/bin/bash.exe"
SERVICIOS = ("s3", "ssm", "lambda", "logs", "iam", "apigateway")


def sonda():
    texto = COMPOSE.read_text(encoding="utf-8")
    bloque = re.search(r"(?ms)^    healthcheck:\n(.*?)^      interval:", texto).group(1)
    bloque = re.sub(r"(?m)^      #.*\n", "", bloque)
    prefijo = "      test:\n        - CMD\n        - /bin/bash\n        - -ec\n        - |\n"
    if not bloque.startswith(prefijo):
        raise AssertionError("la sonda debe usar Bash explicito sin curl ni shell implicito")
    return textwrap.dedent(bloque[len(prefijo):]).replace("$$", "$")


class HealthcheckTests(unittest.TestCase):
    def test_dns_no_reenvia_consultas_externas_desde_lambda(self):
        texto = COMPOSE.read_text(encoding="utf-8")
        # internal:true no basta: Floci tiene salida por la red entrada y su
        # servidor DNS puede actuar como relay para los contenedores Lambda.
        self.assertRegex(texto, r'(?m)^    dns:\n      - "::1"$')
        self.assertIn('FLOCI_DNS_CONTAINER_FALLBACK_ENABLED: "false"', texto)
        self.assertIn('FLOCI_DNS_CONTAINER_FALLBACK_SERVERS: "::1"', texto)

    def test_bash_explicito_y_sin_herramientas_ausentes(self):
        script = sonda()
        self.assertNotRegex(script, r"\b(curl|wget|python3?|jq|grep|sed|awk|cat|timeout)\b")
        self.assertIn("/dev/tcp/127.0.0.1/4566", script)
        self.assertIn("/_localstack/health", script)

    def ejecutar(self, estado=200, servicios=None, cuerpo=None, script=None):
        if not BASH:
            self.fail("se requiere Bash para probar la sonda real del Compose")
        if cuerpo is None:
            cuerpo = json.dumps({"services": servicios if servicios is not None else
                                 dict.fromkeys(SERVICIOS, "running")}).encode()
        respuesta = (f"HTTP/1.1 {estado} Test\r\nContent-Length: {len(cuerpo)}\r\n"
                     "Connection: close\r\n\r\n").encode() + cuerpo

        class Servidor(socketserver.BaseRequestHandler):
            def handle(self):
                self.request.recv(4096)
                self.request.sendall(respuesta)

        with socketserver.TCPServer(("127.0.0.1", 0), Servidor) as servidor:
            hilo = threading.Thread(target=servidor.handle_request, daemon=True)
            hilo.start()
            script = (script or sonda()).replace("/127.0.0.1/4566", f"/127.0.0.1/{servidor.server_address[1]}")
            # PATH vacio: cualquier dependencia accidental de otro ejecutable falla.
            with tempfile.TemporaryDirectory() as vacio:
                env = dict(os.environ, PATH=vacio)
                resultado = subprocess.run([BASH, "--noprofile", "--norc", "-ec", script],
                                           env=env, capture_output=True, timeout=8)
            hilo.join(timeout=2)
        return resultado.returncode

    def test_http_200_y_seis_servicios_running(self):
        self.assertEqual(self.ejecutar(), 0)

    def test_estado_http_erroneo_no_pasa_aunque_servicios_estan_running(self):
        self.assertNotEqual(self.ejecutar(503), 0)

    def test_cada_servicio_ausente_o_detenido_falla(self):
        for servicio in SERVICIOS:
            for valor in (None, "stopped"):
                with self.subTest(servicio=servicio, valor=valor):
                    servicios = dict.fromkeys(SERVICIOS, "running")
                    if valor is None:
                        del servicios[servicio]
                    else:
                        servicios[servicio] = valor
                    self.assertNotEqual(self.ejecutar(servicios=servicios), 0)

    def test_exigir_servicio_inexistente_falla(self):
        self.assertNotEqual(self.ejecutar(script=sonda().replace(
            "s3 ssm lambda logs iam apigateway", "s3 ssm lambda logs iam apigateway inexistente"
        )), 0)

    def test_running_fuera_de_services_no_pasa(self):
        self.assertNotEqual(self.ejecutar(cuerpo=json.dumps(dict.fromkeys(SERVICIOS, "running")).encode()), 0)


if __name__ == "__main__":
    unittest.main()
