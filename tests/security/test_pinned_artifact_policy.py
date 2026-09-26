"""Politica `pinned-artifact` del gate S-09, para artefactos que NO son imagenes.

Por que existe
--------------
`Task/025` introduce el **binario de Terraform**, que S-09 exige auditar igual
que cualquier otra dependencia: *«versiones fijadas y escaneo de
vulnerabilidades en CI»*. Pero el gate solo sabia de imagenes.

Sus dos politicas previas no le sirven:

- `zero-tolerance` exige residual cero, y el binario oficial de HashiCorp tiene
  hoy 9 HIGH que **no dependen de nosotros**: vienen de la *toolchain* de Go con
  la que se compilo.
- `accepted-baseline` liga la aceptacion al **digest de una imagen**, leido de
  `Metadata.RepoDigests`. Un binario suelto no tiene `RepoDigests`, asi que ese
  control no se puede ejecutar: no es que falle, es que **no aplica**.

De ahi la tercera politica. **No es una politica paralela**: vive en el mismo
`vulnerability_gate.py`, en el mismo `vulnerability-baseline.json`, y compara
hallazgos con la **misma** funcion de identidad exacta. Lo unico que cambia es
**como se establece la identidad del artefacto**, porque un ZIP publicado y
firmado no se identifica igual que una imagen OCI.

Y la identidad no se relaja: el artefacto se verifica con `sha256sum --check
--strict` contra el `SHA256SUMS` **firmado con GPG** por HashiCorp, **antes** de
escanearlo. Esa comprobacion es al menos tan fuerte como un `RepoDigest`. El
baseline registra ese `sha256` y quien lo verifica, para que la cadena quede
escrita y auditable.
"""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts/security/vulnerability_gate.py"

SHA_DEL_ARTEFACTO = "0d17011f0c4664539b164b044903d04e296c86c13cb9f28040076c65cfb3985a"


def hallazgo(**cambios):
    base = {
        "scope": "terraform",
        "id": "CVE-2026-56862",
        "package": "stdlib",
        "package_path": "",
        "severity": "HIGH",
        "installed_version": "v1.26.4",
        "fixed_version": "1.25.13, 1.26.6, 1.27.0-rc.3",
    }
    base.update(cambios)
    return base


def vulnerabilidad(**cambios):
    base = {
        "VulnerabilityID": "CVE-2026-56862",
        "PkgName": "stdlib",
        "Severity": "HIGH",
        "InstalledVersion": "v1.26.4",
        "FixedVersion": "1.25.13, 1.26.6, 1.27.0-rc.3",
    }
    base.update(cambios)
    return base


class PoliticaDeArtefactoFijadoTests(unittest.TestCase):
    def setUp(self):
        self.entrada = {
            "key": "terraform",
            "policy": "pinned-artifact",
            "reference": "terraform:1.16.2",
            "expected_sha256": SHA_DEL_ARTEFACTO,
            "identity_verified_by": (
                "sha256sum --check --strict contra terraform_1.16.2_SHA256SUMS, "
                "firmado con GPG por HashiCorp Security"
            ),
            "risk": "Excepcion temporal autorizada por el usuario el 2026-09-14",
            "accepted_findings": [hallazgo()],
        }
        self.baseline = {
            "schema": "personal-blog-infra/vulnerability-baseline",
            "version": 1,
            "accepted_on": "2026-09-14",
            "images": [self.entrada],
        }
        self.informe = {
            "ArtifactName": "terraform",
            "Results": [
                {
                    "Target": "terraform",
                    "Class": "lang-pkgs",
                    "Type": "gobinary",
                    "Vulnerabilities": [vulnerabilidad()],
                }
            ],
        }

    def ejecutar(self):
        with tempfile.TemporaryDirectory(prefix="task025-gate-") as directorio:
            raiz = Path(directorio)
            (raiz / "baseline.json").write_text(json.dumps(self.baseline), encoding="utf-8")
            (raiz / "terraform.json").write_text(json.dumps(self.informe), encoding="utf-8")
            resultado = subprocess.run(
                [sys.executable, str(GATE), "--baseline", str(raiz / "baseline.json"),
                 "--reports", str(raiz)],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
        return resultado.returncode, resultado.stdout + resultado.stderr

    #: Convencion de salida del gate, preexistente y deliberada:
    #:   0 = correcto
    #:   1 = hallazgos fuera del baseline
    #:   2 = el gate NO pudo evaluar (baseline invalido, informe ausente...)
    #: Los dos ultimos son ROJO; se distinguen porque «hay un hallazgo nuevo» y
    #: «no se pudo comprobar nada» son problemas distintos.
    ROJO_POR_HALLAZGOS = 1
    ROJO_POR_GATE = 2

    def afirmar(self, esperado):
        codigo, salida = self.ejecutar()
        self.assertEqual(codigo, esperado, salida)
        return salida

    # --- camino positivo ---------------------------------------------------

    def test_inventario_exactamente_autorizado_pasa(self):
        salida = self.afirmar(0)
        self.assertIn("CVE-2026-56862", salida)

    def test_la_salida_declara_como_se_verifico_la_identidad(self):
        """Nadie debe confundir esto con una entrada verificada por digest OCI."""
        salida = self.afirmar(0)
        self.assertIn(SHA_DEL_ARTEFACTO, salida)
        self.assertIn("sha256sum", salida.lower())

    # --- controles negativos ----------------------------------------------

    def test_un_accionable_nuevo_es_rojo(self):
        self.informe["Results"][0]["Vulnerabilities"].append(
            vulnerabilidad(VulnerabilityID="CVE-2099-00001")
        )
        salida = self.afirmar(self.ROJO_POR_HALLAZGOS)
        self.assertIn("CVE-2099-00001", salida)

    def test_cada_campo_de_identidad_alterado_es_rojo(self):
        for campo, valor in (
            ("VulnerabilityID", "CVE-2099-00002"),
            ("PkgName", "otro-paquete"),
            ("Severity", "CRITICAL"),
            ("InstalledVersion", "v1.26.5"),
            ("FixedVersion", "9.9.9"),
        ):
            with self.subTest(campo=campo):
                original = self.informe["Results"][0]["Vulnerabilities"][0].copy()
                self.informe["Results"][0]["Vulnerabilities"][0][campo] = valor
                self.afirmar(self.ROJO_POR_HALLAZGOS)
                self.informe["Results"][0]["Vulnerabilities"][0] = original

    def test_un_scope_distinto_es_rojo(self):
        """`terraform` y `terraform.exe` no son el mismo artefacto observado."""
        self.informe["Results"][0]["Target"] = "terraform.exe"
        self.afirmar(self.ROJO_POR_HALLAZGOS)

    def test_sin_sha256_esperado_el_baseline_es_invalido(self):
        del self.entrada["expected_sha256"]
        self.afirmar(self.ROJO_POR_GATE)

    def test_sha256_malformado_es_invalido(self):
        self.entrada["expected_sha256"] = "no-es-un-sha256"
        self.afirmar(self.ROJO_POR_GATE)

    def test_sin_declarar_quien_verifica_la_identidad_es_invalido(self):
        """Una aceptacion sin cadena de identidad escrita no es auditable."""
        del self.entrada["identity_verified_by"]
        self.afirmar(self.ROJO_POR_GATE)

    def test_sin_riesgo_declarado_es_invalido(self):
        del self.entrada["risk"]
        self.afirmar(self.ROJO_POR_GATE)

    def test_informe_ausente_es_rojo(self):
        self.entrada["key"] = "terraform-inexistente"
        self.afirmar(self.ROJO_POR_GATE)

    def test_no_se_exige_repodigests_a_un_artefacto_que_no_es_imagen(self):
        """El informe no tiene `Metadata`, y aun asi debe poder evaluarse."""
        self.assertNotIn("Metadata", self.informe)
        self.afirmar(0)

    def test_un_hallazgo_aprobado_que_desaparece_no_rompe(self):
        """Mismo criterio que la politica de imagenes: avisa, no falla."""
        self.informe["Results"][0]["Vulnerabilities"] = []
        salida = self.afirmar(0)
        self.assertIn("baseline_stale", salida.lower().replace(" ", "_"))


class CoherenciaDeIdentidadTests(unittest.TestCase):
    """El `expected_sha256` del baseline no puede divergir de lo que se verifica.

    Hallazgo de un control negativo propio: manipular `expected_sha256` en el
    baseline NO ponia el gate en rojo. Es coherente con el diseno —la identidad de
    un artefacto suelto se establece con `sha256sum` ANTES del escaneo, y el gate
    no puede reejecutar esa comprobacion sobre un informe—, pero dejaba un hueco:
    nada ataba el valor declarado en el baseline al valor que realmente se
    verifica.

    Se cierra atando las TRES declaraciones del mismo sha256: el workflow que lo
    verifica, el modulo del laboratorio que lo fija y el baseline que lo acepta.
    Si divergen, esto se pone rojo antes de que nadie confie en el baseline.
    """

    def setUp(self):
        self.baseline = json.loads(
            (ROOT / "security/vulnerability-baseline.json").read_text(encoding="utf-8")
        )
        self.entrada = next(
            (i for i in self.baseline["images"] if i["key"] == "terraform"), None
        )
        if self.entrada is None:
            self.skipTest("todavia no existe la entrada `terraform` en el baseline")

    def test_el_workflow_verifica_el_mismo_sha256_que_acepta_el_baseline(self):
        import re

        flujo = (ROOT / ".github/workflows/ci-infra.yml").read_text(encoding="utf-8")
        m = re.search(r"SHA256_DE_TERRAFORM:\s*'([0-9a-f]{64})'", flujo)
        self.assertIsNotNone(m, "el workflow no declara SHA256_DE_TERRAFORM")
        self.assertEqual(
            m.group(1),
            self.entrada["expected_sha256"],
            "el sha256 que CI verifica no es el que el baseline acepta",
        )

    def test_el_lanzador_fija_el_mismo_sha256(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        from laboratorio import herramientas

        self.assertEqual(
            herramientas.CHECKSUMS_DE_TERRAFORM["linux_amd64"],
            self.entrada["expected_sha256"],
            "el sha256 que fija el laboratorio no es el que el baseline acepta",
        )

    def test_la_version_declarada_coincide(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        from laboratorio import herramientas

        self.assertEqual(
            self.entrada["reference"], f"terraform:{herramientas.VERSION_DE_TERRAFORM}"
        )


class VerificadorDeCoherenciaTests(unittest.TestCase):
    """El verificador canonico que CI ejecuta, no solo una comparacion de strings.

    El control negativo numero 6 demostro el hueco: se podia manipular
    `expected_sha256` en el baseline y el gate seguia verde, porque un artefacto
    suelto no lleva su identidad dentro del informe. La propiedad que hay que
    garantizar es:

      cambiar el SHA aceptado sin cambiar el que CI y el laboratorio verifican
      de verdad -> ROJO.

    Se implementa UNA vez, en el mismo `vulnerability_gate.py` que ya es la
    autoridad S-09, y se invoca desde aqui y desde CI. No se duplica la politica.
    """

    def setUp(self):
        sys.path.insert(0, str(ROOT / "scripts/security"))
        import vulnerability_gate as gate

        self.gate = gate
        self.baseline = json.loads(
            (ROOT / "security/vulnerability-baseline.json").read_text(encoding="utf-8")
        )
        self.flujo = (ROOT / ".github/workflows/ci-infra.yml").read_text(encoding="utf-8")
        sys.path.insert(0, str(ROOT / "scripts"))
        from laboratorio import herramientas

        self.checksums = dict(herramientas.CHECKSUMS_DE_TERRAFORM)
        self.versiones = {"terraform": herramientas.VERSION_DE_TERRAFORM}

    def verificar(self, baseline=None, flujo=None, checksums=None, versiones=None):
        return self.gate.verificar_coherencia_de_identidad(
            baseline if baseline is not None else self.baseline,
            flujo if flujo is not None else self.flujo,
            checksums if checksums is not None else self.checksums,
            versiones if versiones is not None else self.versiones,
        )

    def entrada(self, baseline):
        return next(i for i in baseline["images"] if i["key"] == "terraform")

    def test_el_estado_real_del_repositorio_es_coherente(self):
        comprobadas = self.verificar()
        self.assertIn("terraform", comprobadas)

    def test_sha_del_baseline_manipulado_es_rojo(self):
        """Este es exactamente el control negativo numero 6."""
        b = json.loads(json.dumps(self.baseline))
        self.entrada(b)["expected_sha256"] = "f" * 64
        with self.assertRaises(self.gate.GateError) as capturado:
            self.verificar(baseline=b)
        self.assertIn("f" * 64, str(capturado.exception))

    def test_sha_del_workflow_manipulado_es_rojo(self):
        flujo = self.flujo.replace(
            self.entrada(self.baseline)["expected_sha256"], "e" * 64
        )
        with self.assertRaises(self.gate.GateError):
            self.verificar(flujo=flujo)

    def test_sha_del_lanzador_manipulado_es_rojo(self):
        with self.assertRaises(self.gate.GateError):
            self.verificar(checksums={"linux_amd64": "d" * 64})

    def test_version_discordante_es_rojo(self):
        with self.assertRaises(self.gate.GateError):
            self.verificar(versiones={"terraform": "9.9.9"})

    def test_si_el_workflow_no_declara_el_sha_es_rojo(self):
        """Quitar la verificacion de CI no puede dejar la coherencia sin comprobar."""
        import re

        flujo = re.sub(r"SHA256_DE_TERRAFORM:.*", "", self.flujo)
        with self.assertRaises(self.gate.GateError):
            self.verificar(flujo=flujo)

    def test_si_el_lanzador_no_declara_la_plataforma_es_rojo(self):
        with self.assertRaises(self.gate.GateError):
            self.verificar(checksums={})

    def test_una_entrada_sin_pinned_artifact_no_exige_coherencia(self):
        """Solo los artefactos fijados necesitan esta comprobacion."""
        b = {"images": [{"key": "minio", "policy": "accepted-baseline",
                         "accepted_findings": []}]}
        self.assertEqual(self.verificar(baseline=b), {})

    def test_un_artefacto_fijado_sin_fuente_conocida_es_rojo(self):
        """No se puede aceptar un artefacto cuya identidad nadie verifica."""
        b = {"images": [{"key": "artefacto-desconocido", "policy": "pinned-artifact",
                         "reference": "algo:1.0", "expected_sha256": "a" * 64,
                         "identity_verified_by": "x", "risk": "y",
                         "accepted_findings": []}]}
        with self.assertRaises(self.gate.GateError):
            self.verificar(baseline=b)


class CoexistenciaTests(unittest.TestCase):
    """Las politicas conviven en el MISMO archivo y el MISMO comparador."""

    def test_el_gate_declara_exactamente_tres_politicas(self):
        sys.path.insert(0, str(ROOT / "scripts/security"))
        import vulnerability_gate as gate

        self.assertEqual(
            set(gate.POLICIES),
            {"zero-tolerance", "accepted-baseline", "pinned-artifact"},
        )

    def test_la_identidad_exacta_es_la_misma_para_todas(self):
        sys.path.insert(0, str(ROOT / "scripts/security"))
        import vulnerability_gate as gate

        self.assertEqual(
            gate.IDENTITY_FIELDS,
            ("vulnerability_id", "package", "severity", "installed_version", "fixed_version"),
        )

    def test_el_baseline_real_sigue_conservando_las_aceptaciones_historicas(self):
        # Portainer paso de 16 aceptadas a 4 el 2026-09-26 al subir de 2.39.7 a
        # 2.45.1 LTS. No es una relajacion: la version nueva RESUELVE 12 de las 16
        # y no introduce ninguna identidad nueva, asi que las 4 restantes son
        # subconjunto exacto de las ya aprobadas. Se comprobo con Trivy 0.74.0 y
        # con govulncheck en modo binario, que deja de reportar GO-2026-6443.
        datos = json.loads(
            (ROOT / "security/vulnerability-baseline.json").read_text(encoding="utf-8")
        )
        por_clave = {i["key"]: i for i in datos["images"]}
        self.assertEqual(len(por_clave["minio"]["accepted_findings"]), 99)
        self.assertEqual(len(por_clave["portainer"]["accepted_findings"]), 4)
        aceptadas = {(f["id"], f["package"]) for f in por_clave["portainer"]["accepted_findings"]}
        # Ninguna de las 4 puede ser una identidad nueva respecto de las historicas.
        historicas = {
            ("CVE-2025-15558", "github.com/docker/cli"),
            ("CVE-2026-17106", "github.com/moby/go-archive"),
            ("CVE-2026-33747", "github.com/moby/buildkit"),
            ("CVE-2026-33748", "github.com/moby/buildkit"),
        }
        self.assertEqual(aceptadas, historicas)
        # El hallazgo que motivo la subida no puede reaparecer en el baseline.
        self.assertNotIn("CVE-2026-84445", {f["id"] for f in por_clave["portainer"]["accepted_findings"]})
        for clave in ("postgres", "traefik"):
            self.assertEqual(por_clave[clave]["policy"], "zero-tolerance")
            self.assertEqual(por_clave[clave]["accepted_findings"], [])


if __name__ == "__main__":
    unittest.main()
