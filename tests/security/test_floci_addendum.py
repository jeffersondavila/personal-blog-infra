"""H-025-6 cerrada por remediacion: Floci 2.3.0 sin identidades aceptadas y cero riesgos nuevos."""

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
DIGEST = "sha256:e0b292df4dc9559b7b1bf4f51bdda4bb8e269276236438cd03cae661260ea8a9"


class FlociAddendumTests(unittest.TestCase):
    def setUp(self):
        baseline = json.loads((ROOT / "security/vulnerability-baseline.json").read_text(encoding="utf-8"))
        self.floci = next(e for e in baseline["images"] if e["key"] == "floci")

    def test_no_queda_ninguna_identidad_aceptada(self):
        self.assertEqual(self.floci["accepted_findings"], [])

    def test_baseline_compose_y_ci_apuntan_al_mismo_release(self):
        self.assertEqual(self.floci["reference"], "floci/floci:2.3.0@" + DIGEST)
        self.assertEqual(self.floci["expected_digest"], DIGEST)
        env = (ROOT / "laboratorio/.env.laboratorio.example").read_text(encoding="utf-8")
        self.assertIn("LAB_EMULADOR_DIGEST=" + DIGEST + "\n", env)
        compose = (ROOT / "laboratorio/docker-compose.laboratorio.yml").read_text(encoding="utf-8")
        self.assertIn("image: floci/floci@${LAB_EMULADOR_DIGEST", compose)
        self.assertIn("platform: linux/amd64", compose)
        workflow = (ROOT / ".github/workflows/ci-infra.yml").read_text(encoding="utf-8")
        self.assertIn('floci="floci/floci:2.3.0@$(grep', workflow)


if __name__ == "__main__":
    unittest.main()
