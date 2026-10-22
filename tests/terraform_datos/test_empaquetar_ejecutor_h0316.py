"""H-031-6: artefacto de la ejecutora con psycopg, boto3 y la CA de RDS, determinista y con integridad fijada.

El ZIP de H-031-6 lleva las fuentes de `codigo_h0316/`, el bundle regional de la CA y el contenido de EXACTAMENTE las
ruedas de `requirements-ejecutor-h0316.txt`, verificadas por SHA-256 antes de abrirlas. Mismas reglas que H-031-5:
sin compresion, fecha fija, permisos fijos y origen Unix. Estas pruebas usan ruedas sinteticas; el pin del artefacto
real (`SHA256_ESPERADO_H0316`) lo exige la CLI al construirlo con las ruedas reales.
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
CODIGO = RAIZ / "terraform" / "modulos" / "ejecutor_privado" / "codigo_h0316"
REQUISITOS = RAIZ / "scripts" / "terraform_datos" / "requirements-ejecutor-h0316.txt"
FUENTES = ("ejecutor.py", "exportacion.py", "operaciones.py", "rds-ca-us-east-2.pem")


def sha(datos):
    return hashlib.sha256(datos).hexdigest()


def rueda(directorio, nombre, miembros):
    ruta = Path(directorio) / nombre
    with zipfile.ZipFile(ruta, "w") as z:
        for miembro, datos in miembros.items():
            z.writestr(miembro, datos)
    return ruta


class Requisitos(unittest.TestCase):
    def test_paquetes_exactos_con_un_hash_cada_uno(self):
        # Las mismas versiones y hashes de rueda que personal-blog-backend/requirements.lock. boto3 y su cadena son
        # para `export` (D-10 §10.1): el cliente S3 se empaqueta fijado, no se toma el del runtime de Lambda.
        self.assertEqual(emp.requisitos(REQUISITOS), [
            ("boto3", "1.43.82", "65319e8bba6e30f74a6e2727a5688725222da2ab71c6069bc484ce5bfd101c73"),
            ("botocore", "1.43.91", "f96363d4caf50bce45fe2fdc2d4d86b3bea7f5cd805169d53c1371c2dd4772b6"),
            ("jmespath", "1.1.0", "a5663118de4908c91729bea0acadca56526eb2698e83de10cd116ae0f4e97c64"),
            ("psycopg", "3.3.4", "b6bbc25ccf05c8fad3b061d9db2ef0909a555171b84b07f29458a447253d679a"),
            ("psycopg-binary", "3.3.4", "e7510c37550f91a187e3660a8cc50d4b760f8c3b8b2f89ebc5698cd2c7f2c85d"),
            ("python-dateutil", "2.9.0.post0", "a8b2bc7bffae282281c8140a97d3aa9c14da0b136dfe83f850eea9a5f7470427"),
            ("s3transfer", "0.19.2", "d8168eccca828cbb2cd573675333f3bddd254313a9c42494b84c76b539e8ba25"),
            ("six", "1.17.0", "4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274"),
            ("typing-extensions", "4.16.0", "481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8"),
            ("urllib3", "2.8.0", "0cf3cae568d36aa9576b28dfb35f11328f1cb974ca7647d9475ebb86c75ac6e3"),
        ])
        self.assertEqual(emp.REQUISITOS_H0316.resolve(), REQUISITOS.resolve())

    def test_formatos_no_admitidos(self):
        hash_ = "--hash=sha256:" + "a" * 64
        for texto in (
            "",
            "psycopg>=3.3.4 \\\n    " + hash_ + "\n",
            "psycopg==3.3.4\n",
            "psycopg==3.3.4 \\\n    " + hash_ + " \\\n    " + hash_ + "\n",
            "psycopg==3.3.4 \\\n    --hash=md5:" + "a" * 32 + "\n",
            "psycopg==3.3.4 \\\n    " + hash_ + "\n--index-url https://example.invalid\n",
        ):
            with self.subTest(texto=texto[:40]):
                with tempfile.TemporaryDirectory() as d:
                    ruta = Path(d) / "req.txt"
                    ruta.write_text(texto, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "REQUISITOS_NO_ADMITIDOS"):
                        emp.requisitos(ruta)


class Construccion(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.dir = Path(self.temporal.name)
        self.ruedas = self.dir / "ruedas"
        self.ruedas.mkdir()
        self.uno = rueda(self.ruedas, "uno-1.0-py3-none-any.whl",
                         {"uno/__init__.py": b"X = 1\n", "uno-1.0.dist-info/METADATA": b"Name: uno\n"})
        self.dos = rueda(self.ruedas, "dos_bin-2.0-cp312-cp312-manylinux2014_x86_64.whl",
                         {"dos_bin/_c.so": b"\x7fELF", "dos_bin.libs/libx.so.1": b"\x7fELF2"})
        self.req = self.dir / "req.txt"
        self.escribir_requisitos()

    def tearDown(self):
        self.temporal.cleanup()

    def escribir_requisitos(self):
        self.req.write_text(
            f"# sinteticos\nuno==1.0 \\\n    --hash=sha256:{sha(self.uno.read_bytes())}\n"
            f"dos-bin==2.0 \\\n    --hash=sha256:{sha(self.dos.read_bytes())}\n", encoding="utf-8")

    def construir(self, nombre="h0316.zip"):
        destino = self.dir / nombre
        with mock.patch.object(emp, "REQUISITOS_H0316", self.req):
            return destino, emp.construir_h0316(destino, self.ruedas)

    def test_dos_construcciones_dan_los_mismos_bytes(self):
        uno, sha_uno = self.construir("uno.zip")
        dos, sha_dos = self.construir("dos.zip")
        self.assertEqual(uno.read_bytes(), dos.read_bytes())
        self.assertEqual((sha_uno, sha_dos), (sha(uno.read_bytes()),) * 2)

    def test_entradas_exactas_y_ordenadas(self):
        destino, _ = self.construir()
        with zipfile.ZipFile(destino) as z:
            nombres = z.namelist()
            self.assertEqual(nombres, sorted([*FUENTES, "uno/__init__.py", "uno-1.0.dist-info/METADATA",
                                              "dos_bin/_c.so", "dos_bin.libs/libx.so.1"]))
            for fuente in FUENTES:
                self.assertEqual(z.read(fuente), (CODIGO / fuente).read_bytes())
            self.assertEqual(z.read("dos_bin/_c.so"), b"\x7fELF")

    def test_metadatos_fijos(self):
        destino, _ = self.construir()
        with zipfile.ZipFile(destino) as z:
            self.assertEqual(z.comment, b"")
            for info in z.infolist():
                with self.subTest(entrada=info.filename):
                    self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                    self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                    self.assertEqual(info.create_system, 3)
                    self.assertEqual(info.external_attr >> 16, 0o100644)
                    self.assertEqual((info.extra, info.comment), (b"", b""))

    def assertRechazado(self, codigo):
        destino = self.dir / "rechazado.zip"
        with mock.patch.object(emp, "REQUISITOS_H0316", self.req):
            with self.assertRaisesRegex(ValueError, codigo):
                emp.construir_h0316(destino, self.ruedas)
        self.assertFalse(destino.exists(), "un artefacto rechazado no se escribe")

    def test_rueda_ausente(self):
        self.dos.unlink()
        self.assertRechazado("RUEDA_AUSENTE")

    def test_rueda_alterada(self):
        rueda(self.ruedas, self.dos.name, {"dos_bin/_c.so": b"otro"})
        self.assertRechazado("RUEDA_ALTERADA")

    def test_rueda_no_fijada(self):
        rueda(self.ruedas, "tres-3.0-py3-none-any.whl", {"tres.py": b""})
        self.assertRechazado("RUEDA_NO_FIJADA")

    def test_ruedas_con_datos_o_rutas_inseguras(self):
        # Sin un caso de barra invertida: en Windows `zipfile` la convierte en `/` al escribir y al leer, asi que la
        # rueda sintetica no podria contenerla. El codigo la rechaza igualmente donde llega intacta (POSIX).
        for miembro in ("uno-1.0.data/purelib/x.py", "uno-1.0.data/platlib/x.so", "uno-1.0.data/headers/x.h",
                        "uno-1.0.data/data/x", "../fuera.py", "/abs.py", "c:/x.py"):
            with self.subTest(miembro=miembro):
                self.uno = rueda(self.ruedas, self.uno.name, {"uno/__init__.py": b"", miembro: b""})
                self.escribir_requisitos()
                self.assertRechazado("RUEDA_NO_ADMITIDA")

    def test_los_scripts_de_consola_de_una_rueda_se_omiten(self):
        # jmespath trae `jmespath-1.1.0.data/scripts/jp.py`: pip lo instalaria en bin/, fuera del codigo importable.
        # Lambda no lo necesita; el artefacto lleva solo lo importable y cualquier otro `.data/` sigue rechazado.
        self.uno = rueda(self.ruedas, self.uno.name, {"uno/__init__.py": b"X = 1\n", "uno-1.0.data/scripts/jp": b""})
        self.escribir_requisitos()
        destino, _ = self.construir()
        with zipfile.ZipFile(destino) as z:
            self.assertIn("uno/__init__.py", z.namelist())
            self.assertFalse([n for n in z.namelist() if ".data/" in n or n.endswith("jp")])

    def test_colision_con_una_fuente(self):
        self.uno = rueda(self.ruedas, self.uno.name, {"ejecutor.py": b"suplantado\n"})
        self.escribir_requisitos()
        self.assertRechazado("ENTRADA_DUPLICADA")

    def test_fuente_no_normalizada(self):
        for contenido in (b"x = 1\r\n", b"\xef\xbb\xbfx = 1\n"):
            with self.subTest(contenido=contenido):
                otro = self.dir / "codigo"
                otro.mkdir(exist_ok=True)
                for fuente in FUENTES:
                    (otro / fuente).write_bytes((CODIGO / fuente).read_bytes())
                (otro / "operaciones.py").write_bytes(contenido)
                with mock.patch.object(emp, "CODIGO_H0316", otro):
                    self.assertRechazado("FUENTE_NO_NORMALIZADA")

    def test_el_handler_del_zip_responde_selfcheck_sin_importar_psycopg(self):
        destino, _ = self.construir()
        extraido = self.dir / "extraido"
        with zipfile.ZipFile(destino) as z:
            z.extractall(extraido)
        sys.path.insert(0, str(extraido))
        try:
            for nombre in ("ejecutor", "operaciones"):
                sys.modules.pop(nombre, None)
            ejecutor = importlib.import_module("ejecutor")
            with contextlib.redirect_stdout(io.StringIO()):
                respuesta = ejecutor.manejar({"modo": "selfcheck"}, object())
        finally:
            sys.path.remove(str(extraido))
            for nombre in ("ejecutor", "operaciones"):
                sys.modules.pop(nombre, None)
        self.assertEqual((respuesta["contrato"], respuesta["estado"]), ("d24-ejecutor-h0316-v1", "OK"))


class Cli(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.dir = Path(self.temporal.name)

    def tearDown(self):
        self.temporal.cleanup()

    def test_el_pin_es_un_sha256(self):
        self.assertRegex(emp.SHA256_ESPERADO_H0316, r"^[0-9a-f]{64}$")
        self.assertNotEqual(emp.SHA256_ESPERADO_H0316, emp.SHA256_ESPERADO)

    def test_h0316_exige_el_directorio_de_ruedas(self):
        with mock.patch.object(sys, "argv", ["empaquetar_ejecutor.py", "--fase", "h0316", "--destino",
                                             str(self.dir / "x.zip")]), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                emp.main()

    def test_h0316_borra_un_artefacto_que_no_coincide_con_el_pin(self):
        destino = self.dir / "cli.zip"

        def construir_falso(ruta, ruedas):
            Path(ruta).write_bytes(b"zip")
            return sha(b"zip")

        with mock.patch.object(emp, "construir_h0316", construir_falso), \
                mock.patch.object(sys, "argv", ["empaquetar_ejecutor.py", "--fase", "h0316", "--ruedas",
                                                str(self.dir), "--destino", str(destino)]):
            with self.assertRaises(SystemExit) as salida:
                emp.main()
        self.assertIn("PIN", str(salida.exception))
        self.assertFalse(destino.exists())

    def test_h0316_informa_solo_el_digest(self):
        destino = self.dir / "cli.zip"
        texto = io.StringIO()

        def construir_falso(ruta, ruedas):
            Path(ruta).write_bytes(b"zip")
            return emp.SHA256_ESPERADO_H0316

        with mock.patch.object(emp, "construir_h0316", construir_falso), \
                mock.patch.object(sys, "argv", ["empaquetar_ejecutor.py", "--fase", "h0316", "--ruedas",
                                                str(self.dir), "--destino", str(destino)]), \
                contextlib.redirect_stdout(texto):
            emp.main()
        self.assertTrue(re.fullmatch(r'\{"artefacto": "cli\.zip", "sha256": "[0-9a-f]{64}"\}\n', texto.getvalue()))


if __name__ == "__main__":
    unittest.main()
