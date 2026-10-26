"""Gobernanza fail-closed del derivado reproducible de MinIO (Task/027.1)."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "security/vulnerability-baseline.json"
GATE = ROOT / "scripts/security/vulnerability_gate.py"


class MinioDerivativeGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
        self.minio = next(i for i in self.baseline["images"] if i["key"] == "minio")
        self.spec = self.minio["identity_attestation"]
        self.manifest_path = ROOT / self.spec["build_manifest"]
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def test_baseline_is_bound_to_exact_build_manifest(self):
        self.assertEqual(
            hashlib.sha256(self.manifest_path.read_bytes()).hexdigest(),
            self.spec["build_manifest_sha256"],
        )
        output = self.manifest["output"]
        self.assertEqual(
            self.minio["reference"], output["reference"] + "@" + output["manifest_digest"]
        )
        self.assertEqual(self.minio["expected_digest"], output["manifest_digest"])

    def test_the_accepted_residual_is_the_exact_corrected_set(self):
        """Task/028 lo reduce de 99 a 10 corrigiendo, no ampliando aceptaciones.

        El conjunto se comprueba entero y no por su tamano: un cambio de
        severidad, de version corregida o de binario produce una identidad
        distinta y debe notarse aqui, no en produccion.
        """
        findings = self.minio["accepted_findings"]
        self.assertEqual(len(findings), 10)
        observado = {
            (item["id"], item["package"], item["severity"],
             item["installed_version"], item["fixed_version"], item["scope"])
            for item in findings
        }
        self.assertEqual(observado, {
            ("CVE-2025-62506", "github.com/minio/minio", "HIGH",
             "v0.0.0-20250907161309-07c3a429bfed+dirty",
             "0.0.0-20251015170045-c1a49490c78e", "usr/bin/minio"),
            ("CVE-2026-32285", "github.com/buger/jsonparser", "HIGH", "v1.1.1", "1.1.2",
             "usr/bin/minio"),
            ("CVE-2026-41602", "github.com/apache/thrift", "HIGH", "v0.21.0", "0.23.0",
             "usr/bin/minio"),
            ("CVE-2026-43871", "github.com/apache/thrift", "HIGH", "v0.21.0", "0.24.0",
             "usr/bin/minio"),
            ("CVE-2026-42151", "github.com/prometheus/prometheus", "HIGH", "v0.303.0",
             "0.311.3", "usr/bin/minio"),
            ("CVE-2026-42151", "github.com/prometheus/prometheus", "HIGH", "v0.303.0",
             "0.311.3", "usr/bin/mc"),
            ("CVE-2026-42154", "github.com/prometheus/prometheus", "HIGH", "v0.303.0",
             "0.311.3, 0.305.2", "usr/bin/minio"),
            ("CVE-2026-42154", "github.com/prometheus/prometheus", "HIGH", "v0.303.0",
             "0.311.3, 0.305.2", "usr/bin/mc"),
            ("CVE-2026-4878", "libcap", "HIGH", "2.48-9.el9_2", "2.48-10.el9_8.1",
             "os-pkgs:redhat"),
            ("CVE-2026-54369", "libacl", "HIGH", "2.3.1-4.el9", "2.4.0-1.el9_8",
             "os-pkgs:redhat"),
        })

    def test_the_two_corrected_vulnerabilities_are_gone(self):
        """Lo que cada tarea corrigio no puede volver a estar aceptado."""
        findings = self.minio["accepted_findings"]
        identificadores = {item["id"] for item in findings}
        paquetes = {item["package"] for item in findings}
        # Task/027.1: amqp091-go v1.10.0 -> v1.13.0.
        self.assertNotIn("CVE-2026-79921", identificadores)
        self.assertNotIn("github.com/rabbitmq/amqp091-go", paquetes)
        # Task/028 (H-028-2): grpc v1.72.0 / v1.71.0 -> v1.83.2 en ambos binarios.
        self.assertNotIn("CVE-2026-84445", identificadores)
        self.assertNotIn("google.golang.org/grpc", paquetes)
        # Task/031 (contrato v3): pcre2 en la capa de paquetes, stdlib con Go 1.27.3, x/net y klauspost/compress.
        for corregida in ("CVE-2026-103111", "CVE-2026-86145", "CVE-2026-89161", "CVE-2026-111943",
                          "CVE-2026-78667", "CVE-2026-78669", "CVE-2026-97031", "CVE-2026-63209"):
            self.assertNotIn(corregida, identificadores)
        for paquete in ("pcre2", "pcre2-syntax", "stdlib", "golang.org/x/net", "github.com/klauspost/compress"):
            self.assertNotIn(paquete, paquetes)

    def test_the_superseded_identities_are_preserved_not_overwritten(self):
        """La identidad de Task/028 queda como anterior inmediata, y la de Task/027.1 anidada, ambas por digest."""
        anterior = self.minio["superseded_identity"]
        self.assertEqual(anterior["accepted_findings_count"], 10)
        self.assertIn(
            "sha256:247a1cd329f4d27053c8555a7f7ae83c8234839dee98ac7c4c1d6ffcd8f80702",
            anterior["reference"],
        )
        historica = anterior["superseded_identity"]
        self.assertEqual(historica["accepted_findings_count"], 99)
        self.assertIn(
            "sha256:84c67632f7e85d4cd86ea5f7f6fbb6b5b8263ecd20f08153c4cd1a42e3059129",
            historica["reference"],
        )
        self.assertNotEqual(anterior["reference"], self.minio["reference"])
        supersedes = self.manifest["supersedes"]
        self.assertEqual(supersedes["replaced_paths"], ["usr/bin/minio", "usr/bin/mc"])
        self.assertEqual(supersedes["manifest_digest"],
                         "sha256:247a1cd329f4d27053c8555a7f7ae83c8234839dee98ac7c4c1d6ffcd8f80702")
        self.assertEqual(supersedes["supersedes"]["replaced_paths"], ["usr/bin/minio"])
        self.assertEqual(supersedes["supersedes"]["manifest_digest"],
                         "sha256:84c67632f7e85d4cd86ea5f7f6fbb6b5b8263ecd20f08153c4cd1a42e3059129")
        self.assertNotEqual(supersedes["manifest_digest"],
                            self.manifest["output"]["manifest_digest"])
        self.assertNotEqual(supersedes["reference"],
                            self.manifest["output"]["reference"])

    def test_the_package_layer_updates_only_pcre2(self):
        """Task/031: la capa de paquetes corrige pcre2 y nada mas; libcap y libacl siguen aceptadas, sin tocar."""
        paquetes = self.manifest["package_updates"]["packages"]
        self.assertEqual(
            [(item["name"], item["from"], item["to"]) for item in paquetes],
            [("pcre2", "10.40-6.el9", "10.40-7.el9_8"), ("pcre2-syntax", "10.40-6.el9", "10.40-7.el9_8")],
        )
        rutas = [item["path"] for item in self.manifest["package_updates"]["layer"]["members"]]
        self.assertFalse([ruta for ruta in rutas if "libcap" in ruta or "libacl" in ruta or "libattr" in ruta])
        aceptados = {item["package"] for item in self.minio["accepted_findings"]}
        self.assertTrue({"libcap", "libacl"} <= aceptados)

    def test_the_recipe_replaces_exactly_the_two_declared_binaries(self):
        rutas = [item["path"] for item in self.manifest["output"]["replacements"]]
        self.assertEqual(rutas, ["usr/bin/minio", "usr/bin/mc"])
        for item in self.manifest["output"]["replacements"]:
            self.assertEqual((item["mode"], item["uid"], item["gid"]), (0o755, 0, 0))

    def test_project_images_still_have_zero_tolerance(self):
        entries = {item["key"]: item for item in self.baseline["images"]}
        for key in ("postgres", "traefik"):
            self.assertEqual(entries[key]["policy"], "zero-tolerance")
            self.assertEqual(entries[key]["accepted_findings"], [])

    def test_attestation_is_not_a_generic_baseline_option(self):
        sys.path.insert(0, str(ROOT / "scripts/security"))
        import vulnerability_gate as gate

        forged = json.loads(json.dumps(self.minio))
        forged["key"] = "another-image"
        data = {
            "schema": gate.SCHEMA,
            "version": 1,
            "accepted_on": "2026-09-18",
            "images": [forged],
        }
        with self.assertRaises(gate.GateError):
            gate.validar_baseline(data)

    def test_repository_coherence_rejects_a_changed_manifest_hash(self):
        changed = json.loads(json.dumps(self.baseline))
        entry = next(i for i in changed["images"] if i["key"] == "minio")
        entry["identity_attestation"]["build_manifest_sha256"] = "0" * 64
        with tempfile.TemporaryDirectory(prefix="task0271-gate-") as directory:
            path = Path(directory) / "baseline.json"
            path.write_text(json.dumps(changed), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(GATE), "--baseline", str(path),
                 "--comprobar-coherencia", str(ROOT)],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
