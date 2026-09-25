"""Second supported operator environment: the human Windows workstation.

CloudShell keeps working exactly as before. Windows is allowed only with an
explicit named profile, and every guard that protected the CloudShell flow keeps
protecting the local one.
"""
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.oidc import bootstrap
from scripts.oidc.guards import (
    EXPECTED_PROFILE, HUMAN, ROLE, Stop, environment_check,
)

ACCOUNT = "123456789012"  # Synthetic only.
CONFIG = {"expected_account_id": ACCOUNT, "aws_region": "us-east-1",
          "trust_phase": "main", "task_expires_at": None}
CLEAN = {"PATH": "/usr/bin"}


def result(stdout="{}", code=0, stderr=""):
    return type("Result", (), {"returncode": code, "stdout": stdout, "stderr": stderr})


class EnvironmentTests(unittest.TestCase):
    def test_cloudshell_unchanged(self):
        self.assertEqual(environment_check(None, "linux", CLEAN), "linux")

    def test_cloudshell_refuses_named_profile(self):
        # A profile on CloudShell would silently select another identity.
        with self.assertRaisesRegex(Stop, "CLOUDSHELL_PROFILE_FORBIDDEN"):
            environment_check(EXPECTED_PROFILE, "linux", CLEAN)

    def test_windows_requires_the_expected_profile(self):
        self.assertEqual(environment_check(EXPECTED_PROFILE, "win32", CLEAN), "win32")
        for profile in (None, "", "default", "other"):
            with self.subTest(profile=profile), self.assertRaisesRegex(Stop, "LOCAL_PROFILE_REQUIRED"):
                environment_check(profile, "win32", CLEAN)

    def test_no_other_platform_is_supported(self):
        for platform in ("darwin", "cygwin", "freebsd"):
            with self.subTest(platform=platform), self.assertRaisesRegex(Stop, "UNSUPPORTED_PLATFORM"):
                environment_check(EXPECTED_PROFILE, platform, CLEAN)

    def test_inherited_profile_is_refused(self):
        for key in ("AWS_PROFILE", "AWS_DEFAULT_PROFILE"):
            with self.subTest(key=key), self.assertRaisesRegex(Stop, "IMPLICIT_PROFILE"):
                environment_check(EXPECTED_PROFILE, "win32", dict(CLEAN, **{key: "anything"}))
            with self.subTest(key=key, platform="linux"), self.assertRaisesRegex(Stop, "IMPLICIT_PROFILE"):
                environment_check(None, "linux", dict(CLEAN, **{key: "anything"}))

    def test_long_lived_keys_are_refused_but_session_credentials_pass(self):
        with self.assertRaisesRegex(Stop, "STATIC_CREDENTIALS"):
            environment_check(None, "linux", dict(CLEAN, AWS_ACCESS_KEY_ID="AKIAEXAMPLE"))
        with self.assertRaisesRegex(Stop, "STATIC_CREDENTIALS"):
            environment_check(None, "linux", dict(CLEAN, AWS_ACCESS_KEY_ID="ASIAEXAMPLE"))
        self.assertEqual(environment_check(None, "linux", dict(
            CLEAN, AWS_ACCESS_KEY_ID="ASIAEXAMPLE", AWS_SESSION_TOKEN="opaque")), "linux")


class ProfilePlumbingTests(unittest.TestCase):
    def argv_for(self, profile):
        seen = {}

        def record(command, **kwargs):
            seen["command"] = command
            return result()

        with patch("subprocess.run", side_effect=record):
            bootstrap.aws_read(["sts", "get-caller-identity"], "us-east-1", profile=profile)
        return seen["command"]

    def test_profile_is_passed_as_an_explicit_argument(self):
        command = self.argv_for(EXPECTED_PROFILE)
        self.assertIn("--profile", command)
        self.assertEqual(command[command.index("--profile") + 1], EXPECTED_PROFILE)

    def test_cloudshell_call_carries_no_profile(self):
        self.assertNotIn("--profile", self.argv_for(None))

    def test_no_credential_material_reaches_the_command_line(self):
        command = self.argv_for(EXPECTED_PROFILE)
        joined = " ".join(command)
        for forbidden in ("AKIA", "ASIA", "aws_secret_access_key", "SessionToken",
                          "--password", "eyJ"):
            self.assertNotIn(forbidden, joined)


class LocalIdentityTests(unittest.TestCase):
    """The identity gate is the same one CloudShell uses; it must not soften."""

    def inventory_with(self, identity, then=None):
        with tempfile.TemporaryDirectory() as temporary:
            state = Path(temporary) / "absent.tfstate"
            with patch.object(bootstrap, "aws_read", side_effect=[identity, then]):
                return bootstrap.inventory(CONFIG, state, profile=EXPECTED_PROFILE)

    def test_root_is_refused(self):
        with self.assertRaisesRegex(Stop, "HUMAN_IDENTITY"):
            self.inventory_with({"Account": ACCOUNT, "Arn": f"arn:aws:iam::{ACCOUNT}:root"})

    def test_unexpected_principal_is_refused(self):
        with self.assertRaisesRegex(Stop, "HUMAN_IDENTITY"):
            self.inventory_with({"Account": ACCOUNT,
                                 "Arn": f"arn:aws:sts::{ACCOUNT}:assumed-role/{ROLE}/local"})

    def test_long_lived_user_identity_is_refused(self):
        # The profile mechanism is not inspectable without touching credential
        # material, so the proof lives here: an IAM user ARN means long-lived keys
        # and never reaches the inventory.
        with self.assertRaisesRegex(Stop, "HUMAN_IDENTITY"):
            self.inventory_with({"Account": ACCOUNT,
                                 "Arn": f"arn:aws:iam::{ACCOUNT}:user/personal-blog-entry"})

    def test_account_mismatch_is_refused(self):
        with self.assertRaisesRegex(Stop, "HUMAN_IDENTITY"):
            self.inventory_with({"Account": "999999999999",
                                 "Arn": f"arn:aws:sts::999999999999:assumed-role/{HUMAN}/local"})

    def test_expected_human_passes_the_identity_gate(self):
        identity = {"Account": ACCOUNT, "Arn": f"arn:aws:sts::{ACCOUNT}:assumed-role/{HUMAN}/local"}
        # The identity gate lets it through; the run stops later, on the provider
        # read, which is what an empty response must do.
        with self.assertRaisesRegex(Stop, "PROVIDER_DISCREPANT_C"):
            self.inventory_with(identity, then={})


class LocalPathTests(unittest.TestCase):
    @unittest.skipIf(os.name != "nt", "Windows private-root scope guard")
    def test_private_paths_must_live_under_localappdata(self):
        from scripts.oidc.guards import private_path
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "private").mkdir()
            private_path(root / "private" / "state.tfstate", root / "repo", must_exist=False)
        outside = Path(os.environ["SystemDrive"] + os.sep) / "task028-not-private.json"
        with self.assertRaisesRegex(Stop, "WINDOWS_PRIVATE_ROOT"):
            private_path(outside, Path(os.environ["LOCALAPPDATA"]) / "repo", must_exist=False)


class MainWiringTests(unittest.TestCase):
    def test_profile_reaches_the_inventory_call(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config.private.json"
            config.write_text(json.dumps(CONFIG), encoding="utf-8")
            if os.name != "nt":
                config.chmod(0o600)
                root.chmod(0o700)
            data = root / "terraform-data"
            data.mkdir()
            if os.name != "nt":
                data.chmod(0o700)
            captured = {}

            def fake(config_value, state, verify_target=False, profile=None):
                captured["profile"] = profile
                raise Stop("STOP_AFTER_WIRING")

            environ = dict(os.environ, TF_DATA_DIR=str(data))
            environ.pop("AWS_PROFILE", None)
            environ.pop("AWS_DEFAULT_PROFILE", None)
            with patch.dict(os.environ, environ, clear=True), \
                 patch.object(bootstrap, "inventory", side_effect=fake), \
                 patch("scripts.oidc.guards.sys.platform", "win32"), \
                 patch("sys.stderr", new=io.StringIO()):
                code = bootstrap.main([
                    "inventory", "--aws-real", "--aws-profile", EXPECTED_PROFILE,
                    "--config", str(config), "--state", str(root / "terraform.tfstate"),
                    "--inventory", str(root / "inventory.private.json")])
            self.assertEqual(code, 1)  # Stopped by the fake, after the wiring ran.
            self.assertEqual(captured.get("profile"), EXPECTED_PROFILE)


if __name__ == "__main__":
    unittest.main()
