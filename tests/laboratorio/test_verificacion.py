"""Operaciones API estrechas que usa el ensayo controlado de Task/026."""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from laboratorio import verificacion as modulo  # noqa: E402


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
