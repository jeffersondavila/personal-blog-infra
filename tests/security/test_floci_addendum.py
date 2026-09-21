"""H-025-6 se reduce: dos identidades historicas exactas, cero riesgos nuevos."""

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
DIGEST = "sha256:f5aa8c18302cedb4f2385f5c4e455b3efc77fee6bf7b6e5d1712b2817ba102db"


class FlociAddendumTests(unittest.TestCase):
    def setUp(self):
        baseline = json.loads((ROOT / "security/vulnerability-baseline.json").read_text(encoding="utf-8"))
        self.floci = next(e for e in baseline["images"] if e["key"] == "floci")

    def test_solo_permanecen_las_dos_identidades_historicas_exactas(self):
        comunes = {"scope": "os-pkgs:redhat", "package_path": "", "severity": "HIGH"}
        self.assertCountEqual(self.floci["accepted_findings"], [
            dict(comunes, id="CVE-2026-4878", package="libcap",
                 installed_version="2.48-10.el9_7.1", fixed_version="2.48-10.el9_8.1"),
            dict(comunes, id="CVE-2026-54369", package="libacl",
                 installed_version="2.3.1-4.el9", fixed_version="2.4.0-1.el9_8"),
        ])

    def test_baseline_compose_y_ci_apuntan_al_mismo_release(self):
        self.assertEqual(self.floci["reference"], "floci/floci:2.1.0@" + DIGEST)
        self.assertEqual(self.floci["expected_digest"], DIGEST)
        env = (ROOT / "laboratorio/.env.laboratorio.example").read_text(encoding="utf-8")
        self.assertIn("LAB_EMULADOR_DIGEST=" + DIGEST + "\n", env)
        compose = (ROOT / "laboratorio/docker-compose.laboratorio.yml").read_text(encoding="utf-8")
        self.assertIn("image: floci/floci@${LAB_EMULADOR_DIGEST", compose)
        self.assertIn("platform: linux/amd64", compose)
        workflow = (ROOT / ".github/workflows/ci-infra.yml").read_text(encoding="utf-8")
        self.assertIn('floci="floci/floci:2.1.0@$(grep', workflow)


if __name__ == "__main__":
    unittest.main()
