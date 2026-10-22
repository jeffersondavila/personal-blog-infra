"""Dependencias fijadas del operador de la ejecutora (`scripts/terraform_datos/requirements-operador.txt`).

El operador y el orquestador del restore (H-031-6 y H-031-7) se autentican con la sesion de `aws login`. Con
botocore 1.43.91, ese proveedor de credenciales exige la dependencia opcional `botocore[crt]`, que fija
`awscrt==0.36.0` («Using the login credential provider requires an additional dependency»; comprobado el 2026-10-19
con `MissingDependencyException`). Sin ella, ninguna fase de AWS del operador puede autenticarse.
"""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
OPERADOR = RAIZ / "scripts" / "terraform_datos" / "requirements-operador.txt"
EJECUTORA = RAIZ / "scripts" / "terraform_datos" / "requirements-ejecutor-h0316.txt"
#: `Requires-Dist: awscrt (==0.36.0) ; extra == 'crt'` en los metadatos de botocore 1.43.91.
CRT_DE_BOTOCORE = {"1.43.91": "0.36.0"}


def fijados(ruta):
    """{paquete: (version, [hashes])} de un archivo de requisitos con `--hash` en lineas de continuacion."""
    texto = ruta.read_text(encoding="utf-8")
    bloques = re.findall(r"(?m)^([A-Za-z0-9_.-]+)==(\S+)((?:\s*\\\n\s+--hash=sha256:[0-9a-f]{64})+)", texto)
    return {nombre.lower(): (version, re.findall(r"sha256:([0-9a-f]{64})", hashes)) for nombre, version, hashes in bloques}


class RequisitosDelOperador(unittest.TestCase):
    def setUp(self):
        self.operador = fijados(OPERADOR)

    def test_cada_requisito_tiene_version_exacta_y_hash(self):
        lineas = [linea for linea in OPERADOR.read_text(encoding="utf-8").splitlines()
                  if linea.strip() and not linea.lstrip().startswith(("#", "--hash"))]
        self.assertEqual(len(lineas), len(self.operador), "toda linea de paquete debe estar fijada con hash")
        for nombre, (version, hashes) in self.operador.items():
            with self.subTest(paquete=nombre):
                self.assertTrue(version and hashes)

    def test_el_mismo_cliente_aws_que_el_artefacto(self):
        ejecutora = fijados(EJECUTORA)
        for nombre in ("boto3", "botocore", "s3transfer", "jmespath", "urllib3"):
            with self.subTest(paquete=nombre):
                self.assertEqual(self.operador[nombre][0], ejecutora[nombre][0])

    def test_incluye_el_crt_que_exige_el_proveedor_de_aws_login(self):
        botocore = self.operador["botocore"][0]
        self.assertIn(botocore, CRT_DE_BOTOCORE, "botocore distinto: revisar su extra `crt`")
        self.assertIn("awscrt", self.operador)
        self.assertEqual(self.operador["awscrt"][0], CRT_DE_BOTOCORE[botocore])


if __name__ == "__main__":
    unittest.main()
