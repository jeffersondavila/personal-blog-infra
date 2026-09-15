"""Firma SigV4 del cliente de inspeccion del laboratorio (matriz 41).

El laboratorio necesita hablar con el emulador para comprobar S3, SSM, IAM,
Lambda y Logs. Este repositorio no tiene hoy **ninguna** dependencia de
terceros, asi que la firma se implementa con la biblioteca estandar y se valida
contra el ejemplo canonico publicado por AWS: si la firma calculada coincide con
la documentada, la implementacion sigue el protocolo y no una aproximacion.
"""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from laboratorio import firma_aws as modulo  # noqa: E402
from ejemplo_canonico_de_aws import (  # noqa: E402
    CLAVE_DEL_EJEMPLO,
    SECRETO_DEL_EJEMPLO,
)

#: Ejemplo canonico de AWS para SigV4 (`get-vanilla-query-order-key-case` de la
#: suite oficial, tal como aparece en la documentacion del proceso de firma).
#: Las dos credenciales viven en `ejemplo_canonico_de_aws`, que explica por que
#: estan partidas y no se pueden volver a unir.
MARCA_DEL_EJEMPLO = "20150830T123600Z"


class CanonicalizacionTests(unittest.TestCase):
    def test_peticion_canonica_del_ejemplo_de_aws(self):
        canonica = modulo.peticion_canonica(
            metodo="GET",
            ruta="/",
            consulta={"Action": "ListUsers", "Version": "2010-05-08"},
            cabeceras={
                "content-type": "application/x-www-form-urlencoded; charset=utf-8",
                "host": "iam.amazonaws.com",
                "x-amz-date": MARCA_DEL_EJEMPLO,
            },
            hash_del_cuerpo=modulo.HASH_DEL_CUERPO_VACIO,
        )
        self.assertTrue(canonica.startswith("GET\n/\nAction=ListUsers&Version=2010-05-08\n"))
        self.assertIn("content-type;host;x-amz-date", canonica)

    def test_hash_del_cuerpo_vacio_es_el_conocido(self):
        self.assertEqual(
            modulo.HASH_DEL_CUERPO_VACIO,
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )

    def test_la_consulta_se_ordena_y_se_codifica(self):
        canonica = modulo.peticion_canonica(
            metodo="GET",
            ruta="/",
            consulta={"b": "2", "a": "1", "espacio": "x y"},
            cabeceras={"host": "ejemplo"},
            hash_del_cuerpo=modulo.HASH_DEL_CUERPO_VACIO,
        )
        self.assertIn("a=1&b=2&espacio=x%20y", canonica)


class FirmaTests(unittest.TestCase):
    def test_firma_del_ejemplo_canonico_de_aws(self):
        firma = modulo.calcular_firma(
            clave_secreta=SECRETO_DEL_EJEMPLO,
            marca=MARCA_DEL_EJEMPLO,
            region="us-east-1",
            servicio="iam",
            peticion_canonica=modulo.peticion_canonica(
                metodo="GET",
                ruta="/",
                consulta={"Action": "ListUsers", "Version": "2010-05-08"},
                cabeceras={
                    "content-type": "application/x-www-form-urlencoded; charset=utf-8",
                    "host": "iam.amazonaws.com",
                    "x-amz-date": MARCA_DEL_EJEMPLO,
                },
                hash_del_cuerpo=modulo.HASH_DEL_CUERPO_VACIO,
            ),
        )
        self.assertEqual(
            firma,
            "5d672d79c15b13162d9279b0855cfba6789a8edb4c82c400e06b5924a6f2b5d7",
        )

    def test_la_firma_es_reproducible(self):
        argumentos = {
            "clave_secreta": "test",
            "marca": "20260913T101112Z",
            "region": "us-east-1",
            "servicio": "s3",
            "peticion_canonica": "GET\n/\n\nhost:127.0.0.1:4566\n\nhost\n"
            + modulo.HASH_DEL_CUERPO_VACIO,
        }
        self.assertEqual(modulo.calcular_firma(**argumentos), modulo.calcular_firma(**argumentos))

    def test_un_secreto_distinto_cambia_la_firma(self):
        base = {
            "marca": "20260913T101112Z",
            "region": "us-east-1",
            "servicio": "s3",
            "peticion_canonica": "GET\n/\n\nhost:127.0.0.1:4566\n\nhost\n"
            + modulo.HASH_DEL_CUERPO_VACIO,
        }
        self.assertNotEqual(
            modulo.calcular_firma(clave_secreta="test", **base),
            modulo.calcular_firma(clave_secreta="otro", **base),
        )

    def test_cabecera_de_autorizacion_bien_formada(self):
        cabecera = modulo.cabecera_de_autorizacion(
            clave_de_acceso="test",
            marca="20260913T101112Z",
            region="us-east-1",
            servicio="s3",
            cabeceras_firmadas="host;x-amz-date",
            firma="f" * 64,
        )
        self.assertTrue(cabecera.startswith("AWS4-HMAC-SHA256 Credential=test/20260913/us-east-1/s3/aws4_request,"))
        self.assertIn("SignedHeaders=host;x-amz-date", cabecera)
        self.assertIn("Signature=" + "f" * 64, cabecera)


if __name__ == "__main__":
    unittest.main()
