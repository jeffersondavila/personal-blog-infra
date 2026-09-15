"""Congelacion de la identidad del artefacto ZIP (Task/025, matriz 27-30).

El ZIP lo construye `personal-blog-backend/scripts/empaquetar_lambda.py`
(`Task/024`). Aqui no se construye ninguno: se comprueba que el laboratorio
detecta que el artefacto cambio entre el `plan` y el `apply`, que es el momento
en que Terraform dejaria de desplegar lo que se reviso.
"""

import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from laboratorio import artefacto as modulo  # noqa: E402


class DescripcionTests(unittest.TestCase):
    def setUp(self):
        self.directorio = tempfile.TemporaryDirectory(prefix="task025-zip-")
        self.addCleanup(self.directorio.cleanup)
        self.ruta = Path(self.directorio.name) / "paquete.zip"
        self.contenido = b"PK\x03\x04" + b"contenido sintetico del artefacto"
        self.ruta.write_bytes(self.contenido)

    def test_artefacto_descrito(self):
        descrito = modulo.describir_artefacto(self.ruta)
        self.assertEqual(descrito.tamano, len(self.contenido))
        self.assertEqual(descrito.sha256, hashlib.sha256(self.contenido).hexdigest())
        self.assertEqual(descrito.ruta, self.ruta.resolve())

    def test_artefacto_inexistente_aborta(self):
        with self.assertRaises(modulo.ErrorDeArtefacto):
            modulo.describir_artefacto(Path(self.directorio.name) / "no-existe.zip")

    def test_directorio_en_lugar_de_archivo_aborta(self):
        with self.assertRaises(modulo.ErrorDeArtefacto):
            modulo.describir_artefacto(Path(self.directorio.name))

    def test_artefacto_vacio_aborta(self):
        vacio = Path(self.directorio.name) / "vacio.zip"
        vacio.write_bytes(b"")
        with self.assertRaises(modulo.ErrorDeArtefacto):
            modulo.describir_artefacto(vacio)


class CongelacionTests(unittest.TestCase):
    def setUp(self):
        self.directorio = tempfile.TemporaryDirectory(prefix="task025-zip-")
        self.addCleanup(self.directorio.cleanup)
        self.ruta = Path(self.directorio.name) / "paquete.zip"
        self.ruta.write_bytes(b"PK\x03\x04" + b"a" * 64)
        self.descrito = modulo.describir_artefacto(self.ruta)

    def test_sin_cambios_continua(self):
        modulo.confirmar_sin_cambios(self.descrito)

    def test_zip_modificado_aborta(self):
        self.ruta.write_bytes(b"PK\x03\x04" + b"b" * 128)
        with self.assertRaises(modulo.ErrorDeArtefacto):
            modulo.confirmar_sin_cambios(self.descrito)

    def test_mismo_tamano_y_contenido_distinto_aborta(self):
        """El tamano solo no basta: la identidad es el hash."""
        original = self.ruta.read_bytes()
        alterado = original[:-1] + bytes([original[-1] ^ 0xFF])
        self.assertEqual(len(original), len(alterado))
        self.ruta.write_bytes(alterado)
        with self.assertRaises(modulo.ErrorDeArtefacto) as capturado:
            modulo.confirmar_sin_cambios(self.descrito)
        self.assertIn("sha256", str(capturado.exception).lower())

    def test_zip_desaparecido_aborta(self):
        self.ruta.unlink()
        with self.assertRaises(modulo.ErrorDeArtefacto):
            modulo.confirmar_sin_cambios(self.descrito)


if __name__ == "__main__":
    unittest.main()
