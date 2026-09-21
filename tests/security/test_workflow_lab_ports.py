"""La guarda CI juzga puertos publicados, nunca direcciones DNS del YAML."""

import contextlib
import io
import json
from pathlib import Path
import re
import textwrap
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


class PuertosDelLaboratorioTests(unittest.TestCase):
    def ejecutar(self, puertos):
        workflow = (ROOT / ".github/workflows/ci-infra.yml").read_text(encoding="utf-8")
        paso = workflow.split("- name: Lab emulator stays on loopback and pinned by digest", 1)[1]
        script = re.search(r"(?s)python3 - <<'PY'\n(.*?)\n          PY", paso).group(1)
        compose = {"services": {"emulador": {"dns": ["::1"], "ports": puertos}}}
        with patch("subprocess.check_output", return_value=json.dumps(compose)), \
             contextlib.redirect_stdout(io.StringIO()):
            exec(compile(textwrap.dedent(script), "gate-puertos-ci", "exec"), {})

    def test_loopback_y_dns_ipv6_local_pasan(self):
        self.ejecutar([{"host_ip": "127.0.0.1", "published": "4566", "target": 4566}])

    def test_lan_o_binding_omitido_abortan(self):
        for ip in ("0.0.0.0", "::", "192.168.1.2", None):
            with self.subTest(ip=ip), self.assertRaises(SystemExit):
                self.ejecutar([{"host_ip": ip, "published": "4566", "target": 4566}])

    def test_sin_puertos_el_gate_no_pasa_en_vacio(self):
        with self.assertRaises(SystemExit):
            self.ejecutar([])


if __name__ == "__main__":
    unittest.main()
