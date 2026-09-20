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

    def test_only_previously_accepted_99_risks_remain(self):
        findings = self.minio["accepted_findings"]
        self.assertEqual(len(findings), 99)
        self.assertNotIn("CVE-2026-79921", {item["id"] for item in findings})
        self.assertFalse(any(item["package"] == "github.com/rabbitmq/amqp091-go" for item in findings))

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
