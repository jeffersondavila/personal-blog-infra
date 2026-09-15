"""Identidad de la herramienta Terraform y del lock del provider (matriz 31-32, 37).

Estos tests no descargan nada: comprueban el comparador de checksums y el
lector del lock con archivos temporales. La descarga real y su verificacion se
ejercitan en el ciclo del laboratorio, no en la suite unitaria.
"""

import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from laboratorio import herramientas as modulo  # noqa: E402


class VersionTests(unittest.TestCase):
    def test_la_version_declarada_es_exacta(self):
        self.assertRegex(modulo.VERSION_DE_TERRAFORM, r"^\d+\.\d+\.\d+$")
        self.assertRegex(modulo.VERSION_DEL_PROVIDER, r"^\d+\.\d+\.\d+$")

    def test_hay_checksum_para_las_dos_plataformas(self):
        for plataforma in ("linux_amd64", "windows_amd64"):
            with self.subTest(plataforma=plataforma):
                self.assertIn(plataforma, modulo.CHECKSUMS_DE_TERRAFORM)
                self.assertIn(plataforma, modulo.CHECKSUMS_DEL_PROVIDER)

    def test_los_checksums_son_sha256_hexadecimales(self):
        for tabla in (modulo.CHECKSUMS_DE_TERRAFORM, modulo.CHECKSUMS_DEL_PROVIDER):
            for plataforma, valor in tabla.items():
                with self.subTest(plataforma=plataforma):
                    self.assertRegex(valor, r"^[0-9a-f]{64}$")

    def test_la_version_de_terraform_coincide_con_la_del_bloque_versions(self):
        """`versions.tf` y el lanzador no pueden discrepar de version."""
        texto = (ROOT / "terraform" / "versions.tf").read_text(encoding="utf-8")
        self.assertIn('"= ' + modulo.VERSION_DE_TERRAFORM + '"', texto)
        self.assertIn('"= ' + modulo.VERSION_DEL_PROVIDER + '"', texto)


class ChecksumTests(unittest.TestCase):
    def setUp(self):
        self.directorio = tempfile.TemporaryDirectory(prefix="task025-tool-")
        self.addCleanup(self.directorio.cleanup)
        self.ruta = Path(self.directorio.name) / "artefacto.zip"
        self.contenido = b"artefacto sintetico"
        self.ruta.write_bytes(self.contenido)
        self.esperado = hashlib.sha256(self.contenido).hexdigest()

    def test_checksum_correcto_acepta(self):
        modulo.verificar_checksum(self.ruta, self.esperado)

    def test_checksum_erroneo_aborta(self):
        with self.assertRaises(modulo.ErrorDeHerramienta):
            modulo.verificar_checksum(self.ruta, "0" * 64)

    def test_artefacto_alterado_aborta(self):
        self.ruta.write_bytes(self.contenido + b"!")
        with self.assertRaises(modulo.ErrorDeHerramienta):
            modulo.verificar_checksum(self.ruta, self.esperado)

    def test_artefacto_ausente_aborta(self):
        self.ruta.unlink()
        with self.assertRaises(modulo.ErrorDeHerramienta):
            modulo.verificar_checksum(self.ruta, self.esperado)


def lock_sintetico(*, plataformas=("linux_amd64", "windows_amd64"), version=None):
    version = version or modulo.VERSION_DEL_PROVIDER
    hashes = "\n".join('    "h1:sintetico-%s=",' % p for p in plataformas)
    return (
        'provider "registry.terraform.io/hashicorp/aws" {\n'
        '  version     = "%s"\n'
        '  constraints = "%s"\n'
        "  hashes = [\n"
        "%s\n"
        "  ]\n"
        "}\n" % (version, version, hashes)
    )


class LockTests(unittest.TestCase):
    def test_lock_completo_acepta(self):
        modulo.verificar_lock(lock_sintetico(), zip_por_plataforma=PLATAFORMAS_SINTETICAS)

    def test_lock_sin_una_plataforma_aborta(self):
        texto = lock_sintetico(plataformas=("linux_amd64",))
        with self.assertRaises(modulo.ErrorDeHerramienta) as capturado:
            modulo.verificar_lock(texto, zip_por_plataforma={"linux_amd64": "h1:sintetico-linux_amd64="})
        self.assertIn("windows_amd64", str(capturado.exception))

    def test_lock_con_version_distinta_aborta(self):
        texto = lock_sintetico(version="1.2.3")
        with self.assertRaises(modulo.ErrorDeHerramienta):
            modulo.verificar_lock(texto, zip_por_plataforma=PLATAFORMAS_SINTETICAS)

    def test_lock_sin_el_provider_aborta(self):
        with self.assertRaises(modulo.ErrorDeHerramienta):
            modulo.verificar_lock("# vacio\n", zip_por_plataforma=PLATAFORMAS_SINTETICAS)

    def test_lock_sin_hashes_aborta(self):
        texto = (
            'provider "registry.terraform.io/hashicorp/aws" {\n'
            '  version = "%s"\n'
            "}\n" % modulo.VERSION_DEL_PROVIDER
        )
        with self.assertRaises(modulo.ErrorDeHerramienta):
            modulo.verificar_lock(texto, zip_por_plataforma=PLATAFORMAS_SINTETICAS)


PLATAFORMAS_SINTETICAS = {
    "linux_amd64": "h1:sintetico-linux_amd64=",
    "windows_amd64": "h1:sintetico-windows_amd64=",
}


class LockVersionadoTests(unittest.TestCase):
    """El lock REAL del repositorio, no uno sintetico.

    Es la comprobacion que ata la cadena de suministro: los hashes `zh:` del lock
    deben ser exactamente los `sha256` que publico HashiCorp para cada
    plataforma. Si alguien regenerase el lock contra otro artefacto, esto se
    pondria rojo.
    """

    def setUp(self):
        self.lock = ROOT / "terraform" / ".terraform.lock.hcl"
        if not self.lock.exists():
            self.skipTest("todavia no se genero terraform/.terraform.lock.hcl")
        self.texto = self.lock.read_text(encoding="utf-8")

    def test_el_lock_esta_versionado(self):
        self.assertTrue(self.lock.is_file())

    def test_el_lock_declara_la_version_exacta(self):
        modulo.verificar_lock(self.texto)

    def test_el_lock_lleva_el_checksum_oficial_de_cada_plataforma(self):
        hashes = modulo.hashes_del_lock(self.texto)
        for plataforma, sha256 in modulo.CHECKSUMS_DEL_PROVIDER.items():
            with self.subTest(plataforma=plataforma):
                self.assertIn("zh:" + sha256, hashes)

    def test_el_lock_lleva_un_hash_h1_por_plataforma(self):
        hashes = modulo.hashes_del_lock(self.texto)
        h1 = [h for h in hashes if h.startswith("h1:")]
        self.assertGreaterEqual(len(h1), len(modulo.PLATAFORMAS))


class PlataformaTests(unittest.TestCase):
    def test_plataforma_actual_es_una_de_las_fijadas(self):
        self.assertIn(modulo.plataforma_actual(), modulo.PLATAFORMAS)

    def test_plataforma_desconocida_aborta(self):
        with self.assertRaises(modulo.ErrorDeHerramienta):
            modulo.nombre_de_plataforma(sistema="Solaris", maquina="sparc")

    def test_arquitectura_no_amd64_aborta(self):
        """No existe ninguna decision que autorice ARM64 en este proyecto."""
        with self.assertRaises(modulo.ErrorDeHerramienta):
            modulo.nombre_de_plataforma(sistema="Linux", maquina="aarch64")


if __name__ == "__main__":
    unittest.main()
