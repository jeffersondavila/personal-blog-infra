"""DH-2: la contrasena master no puede salir del root de datos por ningun camino.

Control negativo ESTRUCTURAL. Se copia el root a un directorio temporal, se le
anade una fuga deliberada y se exige que `terraform validate` la RECHACE. Si
alguna de estas fugas validara, la variable habria dejado de ser efimera y el
secreto podria acabar en el plan, en el state o en una salida.

El control positivo —la copia sin fuga valida— demuestra que el rechazo se debe a
la fuga y no a la preparacion. La ausencia EMPIRICA en el plan, el state y las
salidas reales se demuestra en el laboratorio (canario de `laboratorio.py`).

Necesita el binario de Terraform 1.16.2. Si no esta disponible, la prueba se
OMITE y lo dice: nunca se da por buena sin ejecutarse. En CI corre despues de
instalar Terraform. Para trabajar sin red, `PERSONAL_BLOG_PLUGIN_DIR` apunta a
un directorio de providers ya verificado.
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

#: Cada fuga con el motivo por el que Terraform DEBE rechazarla. Las salidas se
#: marcan `sensitive` a proposito: asi la unica regla que puede detenerlas es la
#: efimera, que es la que DH-2 necesita demostrar. La salida sin marcar se
#: rechaza antes por ser sensible, y se conserva como caso aparte.
FUGAS = {
    "salida_sin_marcar": ('output "fuga" {\n  value = var.contrasena_master\n}\n', "sensitive"),
    "salida_marcada_sensible": (
        'output "fuga" {\n  value     = var.contrasena_master\n  sensitive = true\n}\n',
        "ephemeral",
    ),
    "atributo_que_no_es_write_only": (
        'resource "aws_ssm_parameter" "fuga" {\n'
        '  name  = "/fuga"\n'
        '  type  = "SecureString"\n'
        '  value = var.contrasena_master\n'
        '}\n',
        "ephemeral",
    ),
    "local_hacia_una_salida": (
        'locals {\n  copia = var.contrasena_master\n}\n'
        'output "fuga" {\n  value     = local.copia\n  sensitive = true\n}\n',
        "ephemeral",
    ),
}


def binario_de_terraform():
    candidatos = [os.environ.get("PERSONAL_BLOG_TERRAFORM"), shutil.which("terraform")]
    cache = os.environ.get("LOCALAPPDATA")
    if cache:
        candidatos.append(str(Path(cache) / "personal-blog-infra/herramientas/terraform-1.16.2/windows_amd64/terraform.exe"))
    for candidato in candidatos:
        if candidato and Path(candidato).is_file():
            return candidato
    return None


class LaContrasenaNoSalePorNingunCaminoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.terraform = binario_de_terraform()
        if not cls.terraform:
            raise unittest.SkipTest("Terraform 1.16.2 no disponible: control negativo OMITIDO, no aprobado")
        cls.temporal = tempfile.TemporaryDirectory()
        base = Path(cls.temporal.name)
        shutil.copytree(
            RAIZ / "terraform-datos", base / "terraform-datos",
            ignore=shutil.ignore_patterns(".terraform", "generado", "backend.generado.tf", "tests"),
        )
        # La copia necesita los modulos que el root llama HOY: se leen de sus `source`, asi la prueba sigue al
        # cableado de cada fase (la ejecutora salio del root el 2026-10-08 y vuelve con la cuota de Lambda).
        modulos = sorted(set(re.findall(r'source\s*=\s*"\.\./terraform/modulos/([a-z_]+)"',
                                        (RAIZ / "terraform-datos" / "main.tf").read_text(encoding="utf-8"))))
        assert {"red", "base_de_datos"} <= set(modulos), modulos
        for modulo in modulos:
            shutil.copytree(RAIZ / "terraform" / "modulos" / modulo, base / "terraform" / "modulos" / modulo)
        cls.root = base / "terraform-datos"
        argumentos = ["init", "-backend=false", "-input=false", "-lockfile=readonly", "-no-color"]
        if os.environ.get("PERSONAL_BLOG_PLUGIN_DIR"):
            argumentos.append(f"-plugin-dir={os.environ['PERSONAL_BLOG_PLUGIN_DIR']}")
        resultado = cls.ejecutar(argumentos)
        if resultado.returncode != 0:
            raise AssertionError(f"init de la copia fallo: {resultado.stderr[-800:]}")

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "temporal", None):
            cls.temporal.cleanup()

    @classmethod
    def ejecutar(cls, argumentos):
        entorno = {**os.environ, "TF_IN_AUTOMATION": "1", "CHECKPOINT_DISABLE": "1"}
        return subprocess.run(
            [cls.terraform, f"-chdir={cls.root}", *argumentos],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=entorno,
        )

    def validar(self):
        return self.ejecutar(["validate", "-no-color"])

    def test_control_positivo_sin_fuga_valida(self):
        resultado = self.validar()
        self.assertEqual(resultado.returncode, 0, resultado.stderr[-800:])

    def test_cada_fuga_es_rechazada_por_terraform(self):
        for nombre, (contenido, motivo) in FUGAS.items():
            with self.subTest(fuga=nombre):
                fuga = self.root / "fuga.tf"
                fuga.write_text(contenido, encoding="utf-8")
                try:
                    resultado = self.validar()
                finally:
                    fuga.unlink()
                self.assertNotEqual(resultado.returncode, 0, f"la fuga '{nombre}' VALIDO")
                self.assertIn(motivo, (resultado.stdout + resultado.stderr).lower())


if __name__ == "__main__":
    unittest.main()
