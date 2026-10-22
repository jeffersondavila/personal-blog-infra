"""H-031-5: el artefacto de la ejecutora es pequeno, determinista y reproducible (Task/031).

Los mismos bytes en cualquier maquina y en cualquier momento: una sola entrada (`ejecutor.py`), sin compresion,
fecha fija, permisos fijos y sistema de origen Unix. `SHA256_ESPERADO` es el pin versionado del artefacto revisado:
si la fuente cambia, la prueba falla hasta que el pin cambie a proposito en la misma revision.
"""
import contextlib
import hashlib
import importlib
import io
import re
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from scripts.terraform_datos import empaquetar_ejecutor as emp

RAIZ = Path(__file__).resolve().parents[2]
FUENTE = RAIZ / "terraform" / "modulos" / "ejecutor_privado" / "codigo" / "ejecutor.py"


class Empaquetado(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.dir = Path(self.temporal.name)

    def tearDown(self):
        self.temporal.cleanup()

    def construir(self, nombre="ejecutor.zip"):
        destino = self.dir / nombre
        return destino, emp.construir(destino)

    def test_la_fuente_es_la_del_modulo(self):
        self.assertEqual(emp.FUENTE.resolve(), FUENTE.resolve())

    def test_dos_construcciones_dan_los_mismos_bytes(self):
        uno, sha_uno = self.construir("uno.zip")
        dos, sha_dos = self.construir("dos.zip")
        self.assertEqual(uno.read_bytes(), dos.read_bytes())
        self.assertEqual(sha_uno, sha_dos)
        self.assertEqual(sha_uno, hashlib.sha256(uno.read_bytes()).hexdigest())

    def test_el_artefacto_coincide_con_el_pin(self):
        self.assertRegex(emp.SHA256_ESPERADO, r"^[0-9a-f]{64}$")
        _, sha = self.construir()
        self.assertEqual(sha, emp.SHA256_ESPERADO)

    def test_una_sola_entrada_y_ninguna_dependencia(self):
        destino, _ = self.construir()
        with zipfile.ZipFile(destino) as z:
            self.assertEqual(z.namelist(), ["ejecutor.py"])
            self.assertEqual(z.read("ejecutor.py"), FUENTE.read_bytes())

    def test_metadatos_fijos(self):
        destino, _ = self.construir()
        with zipfile.ZipFile(destino) as z:
            (info,) = z.infolist()
            self.assertEqual(z.comment, b"")
        self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
        self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
        self.assertEqual(info.create_system, 3)
        self.assertEqual(info.external_attr >> 16, 0o100644)
        self.assertEqual((info.extra, info.comment), (b"", b""))

    def test_artefacto_pequeno(self):
        destino, _ = self.construir()
        self.assertLess(destino.stat().st_size, 16 * 1024)

    def test_una_fuente_no_normalizada_se_rechaza(self):
        for contenido in (b"x = 1\r\n", b"\xef\xbb\xbfx = 1\n"):
            with self.subTest(contenido=contenido):
                otra = self.dir / "otra.py"
                otra.write_bytes(contenido)
                with mock.patch.object(emp, "FUENTE", otra):
                    with self.assertRaisesRegex(ValueError, "FUENTE_NO_NORMALIZADA"):
                        emp.construir(self.dir / "rechazado.zip")
                self.assertFalse((self.dir / "rechazado.zip").exists())

    def test_la_cli_borra_un_artefacto_que_no_coincide_con_el_pin(self):
        destino = self.dir / "cli.zip"
        with mock.patch.object(emp, "SHA256_ESPERADO", "0" * 64), \
                mock.patch.object(sys, "argv", ["empaquetar_ejecutor.py", "--destino", str(destino)]):
            with self.assertRaises(SystemExit) as salida:
                emp.main()
        self.assertIn("PIN", str(salida.exception))
        self.assertFalse(destino.exists())

    def test_la_cli_informa_solo_el_digest(self):
        destino = self.dir / "cli.zip"
        texto = io.StringIO()
        with mock.patch.object(sys, "argv", ["empaquetar_ejecutor.py", "--destino", str(destino)]), \
                contextlib.redirect_stdout(texto):
            emp.main()
        self.assertTrue(re.fullmatch(r'\{"artefacto": "cli\.zip", "sha256": "[0-9a-f]{64}"\}\n', texto.getvalue()))

    def test_el_handler_del_zip_se_invoca(self):
        destino, _ = self.construir()
        extraido = self.dir / "extraido"
        with zipfile.ZipFile(destino) as z:
            z.extractall(extraido)
        sys.path.insert(0, str(extraido))
        try:
            sys.modules.pop("ejecutor", None)
            ejecutor = importlib.import_module("ejecutor")
            with contextlib.redirect_stdout(io.StringIO()):
                respuesta = ejecutor.manejar({"modo": "selfcheck"}, object())
        finally:
            sys.path.remove(str(extraido))
            sys.modules.pop("ejecutor", None)
        self.assertEqual(respuesta["estado"], "OK")


if __name__ == "__main__":
    unittest.main()
