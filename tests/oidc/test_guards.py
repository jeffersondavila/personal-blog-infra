import copy
import datetime as dt
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.oidc import bootstrap
from scripts.oidc.guards import (
    ROLE, ROLE_ADDRESS, PROVIDER_ADDRESS, Stop, config_check, human_check,
    ownership, plan_check, private_path, provider_arn, provider_case,
    provider_url_ok, role_check, state_resources, trust, utcnow,
)

ACCOUNT = "123456789012"  # Synthetic only.
CONFIG = {"expected_account_id": ACCOUNT, "aws_region": "us-east-1",
          "trust_phase": "main", "task_expires_at": None}


def plan():
    return {"format_version": "1.2", "terraform_version": "1.16.2", "complete": True,
            "variables": {key: {"value": value} for key, value in dict(CONFIG, provider_mode="existing").items()},
            "configuration": {"provider_config": {"aws": {"full_name": "registry.terraform.io/hashicorp/aws",
                                                         "expressions": {"region": {}, "allowed_account_ids": {}}}},
                              "root_module": {"resources": []}},
            "resource_changes": [{"address": ROLE_ADDRESS, "mode": "managed", "change": {
                "actions": ["create"], "after_unknown": {},
                "after": {"name": ROLE, "path": "/", "max_session_duration": 3600,
                          "description": "Task028 federation validation only; no resource permissions",
                          "assume_role_policy": json.dumps(trust(CONFIG))}}}]}


def converged(config):
    """Plan real posterior al apply: ambos recursos existen y ninguno cambia.

    Reproduce lo observado en Task/028 el 2026-09-24, cuando Terraform devolvio
    exit 0 con `-detailed-exitcode` y `resource_drift` vacio.
    """
    role = {"arn": f"arn:aws:iam::{ACCOUNT}:role/{ROLE}",
            "assume_role_policy": json.dumps(trust(config)),
            "description": "Task028 federation validation only; no resource permissions",
            "force_detach_policies": False, "id": ROLE, "inline_policy": [],
            "managed_policy_arns": [], "max_session_duration": 3600, "name": ROLE,
            "path": "/", "permissions_boundary": "", "tags": {}, "tags_all": {}}
    provider = {"arn": provider_arn(ACCOUNT), "client_id_list": ["sts.amazonaws.com"],
                "tags": {}, "tags_all": {}, "thumbprint_list": [],
                "url": "https://token.actions.githubusercontent.com"}
    value = plan()
    value["variables"] = {key: {"value": item}
                          for key, item in dict(config, provider_mode="create").items()}
    value["configuration"]["root_module"]["resources"] = [
        {"mode": "managed", "type": "aws_iam_role",
         "expressions": {"name": {}, "path": {}, "description": {},
                         "max_session_duration": {}, "assume_role_policy": {}}},
        {"mode": "managed", "type": "aws_iam_openid_connect_provider",
         "expressions": {"url": {}, "client_id_list": {}}, "count_expression": {}}]
    value["resource_changes"] = [
        {"address": "data.aws_caller_identity.human", "mode": "data",
         "change": {"actions": ["read"]}},
        {"address": ROLE_ADDRESS, "mode": "managed", "change": {
            "actions": ["no-op"], "before": copy.deepcopy(role), "after": role,
            "after_unknown": {}}},
        {"address": PROVIDER_ADDRESS, "mode": "managed", "change": {
            "actions": ["no-op"], "before": copy.deepcopy(provider), "after": provider,
            "after_unknown": {}}}]
    return value


def live_task_config():
    expires = (utcnow() + dt.timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return dict(CONFIG, trust_phase="task", task_expires_at=expires)


class GuardTests(unittest.TestCase):
    def test_main_exact(self):
        config_check(CONFIG)
        policy = trust(CONFIG)
        self.assertEqual(len(policy["Statement"]), 1)
        self.assertNotIn("DateLessThan", policy["Statement"][0]["Condition"])
        self.assertTrue(policy["Statement"][0]["Condition"]["StringEquals"]["token.actions.githubusercontent.com:sub"].endswith(":ref:refs/heads/main"))

    def test_task_literal_window(self):
        expires = (utcnow() + dt.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        config = dict(CONFIG, trust_phase="task", task_expires_at=expires)
        config_check(config)
        self.assertEqual(trust(config)["Statement"][0]["Condition"]["DateLessThan"], {"aws:CurrentTime": expires})

    def test_bad_expiry_and_phases(self):
        for update in ({"trust_phase": "*"}, {"trust_phase": "task"},
                       {"task_expires_at": "2099-01-01T00:00:00Z"},
                       {"trust_phase": "task", "task_expires_at": "2020-01-01T00:00:00Z"},
                       {"trust_phase": "task", "task_expires_at": "2099-01-01T00:00:00Z"},
                       {"trust_phase": "task", "task_expires_at": "timestamp()"},
                       {"expected_account_id": "000000000000"}, {"aws_region": "http://localhost"}):
            with self.subTest(update=update), self.assertRaises(Stop):
                config_check(dict(CONFIG, **update))

    def test_human_only(self):
        human_check({"Account": ACCOUNT, "Arn": f"arn:aws:sts::{ACCOUNT}:assumed-role/PersonalBlogAdministrator/test"}, ACCOUNT)
        for arn in (f"arn:aws:iam::{ACCOUNT}:root", f"arn:aws:sts::{ACCOUNT}:assumed-role/{ROLE}/test"):
            with self.assertRaises(Stop):
                human_check({"Account": ACCOUNT, "Arn": arn}, ACCOUNT)

    def test_wrong_account(self):
        with self.assertRaises(Stop):
            human_check({"Account": "999999999999", "Arn": f"arn:aws:sts::{ACCOUNT}:assumed-role/PersonalBlogAdministrator/test"}, ACCOUNT)

    def test_provider_absent_only_on_exact_error(self):
        self.assertEqual(provider_case(None, "NoSuchEntity"), "A")
        for error in (None, "AccessDenied", "Timeout"):
            with self.assertRaises(Stop):
                provider_case(None, error)

    def test_provider_existing_exact(self):
        for url in ("token.actions.githubusercontent.com", "https://token.actions.githubusercontent.com"):
            self.assertEqual(provider_case({"Url": url, "ClientIDList": ["sts.amazonaws.com"], "ThumbprintList": ["existing-observation"]}), "B")

    def test_provider_discrepant(self):
        for document in ({}, {"Url": "evil.example", "ClientIDList": ["sts.amazonaws.com"]},
                         {"Url": "token.actions.githubusercontent.com", "ClientIDList": []},
                         {"Url": "token.actions.githubusercontent.com", "ClientIDList": ["sts.amazonaws.com", "extra"]}):
            with self.assertRaises(Stop):
                provider_case(document)

    def test_ownership_preserved(self):
        self.assertEqual(ownership("A", {}, False), "create")
        self.assertEqual(ownership("B", {}, False), "existing")
        self.assertEqual(ownership("B", {PROVIDER_ADDRESS: {}, ROLE_ADDRESS: {}}, True), "create")

    def test_no_silent_adoption_or_missing_owned_resource(self):
        for case, resources, exists in (("B", {}, True), ("A", {ROLE_ADDRESS: {}}, False),
                                       ("A", {PROVIDER_ADDRESS: {}}, False)):
            with self.assertRaises(Stop):
                ownership(case, resources, exists)

    def test_external_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            repo.mkdir()
            private = root / "private"
            private.mkdir(mode=0o700)
            self.assertEqual(private_path(private / "new.tfstate", repo, must_exist=False), private / "new.tfstate")
            with self.assertRaises(Stop):
                private_path(repo / "ignored.tfstate", repo, must_exist=False)
            (private / ".git").mkdir()
            with self.assertRaises(Stop):
                private_path(private / "new.tfstate", repo, must_exist=False)

    @unittest.skipIf(os.name == "nt", "POSIX permissions are checked on Linux CI/CloudShell")
    def test_public_config_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config"
            path.write_text("{}")
            path.chmod(0o644)
            with self.assertRaises(Stop):
                private_path(path, Path(temporary) / "repo")

    def test_state_wrong_account_or_unexpected_resources(self):
        state = {"version": 4, "lineage": "synthetic", "serial": 0, "resources": [{
            "mode": "managed", "type": "aws_iam_role", "name": "validation", "instances": [{
                "attributes": {"arn": f"arn:aws:iam::{ACCOUNT}:role/{ROLE}"}}]}]}
        self.assertIn(ROLE_ADDRESS, state_resources(state, ACCOUNT))
        with self.assertRaises(Stop):
            state_resources(state, "999999999999")
        state["resources"][0]["type"] = "aws_s3_bucket"
        with self.assertRaises(Stop):
            state_resources(state, ACCOUNT)

    def test_role_audit_exact_and_zero_policies(self):
        role = {"Arn": f"arn:aws:iam::{ACCOUNT}:role/{ROLE}", "RoleName": ROLE,
                "Path": "/", "MaxSessionDuration": 3600, "AssumeRolePolicyDocument": trust(CONFIG)}
        role_check(role, [], [], trust(CONFIG), ACCOUNT)
        for attached, inline in ((["ReadOnlyAccess"], []), ([], ["inline"])):
            with self.assertRaises(Stop):
                role_check(role, attached, inline, trust(CONFIG), ACCOUNT)
        with self.assertRaises(Stop):
            role_check(dict(role, AssumeRolePolicyDocument={}), [], [], trust(CONFIG), ACCOUNT)

    def test_plan_create_reference_only(self):
        plan_check(plan(), CONFIG, "existing", {})

    def test_plan_create_owned_provider(self):
        value = plan()
        value["variables"]["provider_mode"]["value"] = "create"
        value["resource_changes"].append({"address": PROVIDER_ADDRESS, "mode": "managed", "change": {
            "actions": ["create"], "after_unknown": {"arn": True, "client_id_list": [False], "thumbprint_list": True},
            "after": {"url": "https://token.actions.githubusercontent.com", "client_id_list": ["sts.amazonaws.com"]}}})
        plan_check(value, CONFIG, "create", {})
        value["resource_changes"][-1]["change"]["after_unknown"]["client_id_list"] = [True]
        with self.assertRaisesRegex(Stop, "PLAN_PROVIDER_UNKNOWN"):
            plan_check(value, CONFIG, "create", {})

    def test_plan_rejects_resources_delete_replace_import(self):
        for mutation in ("foreign", "delete", "replace", "import", "unknown", "incomplete", "drift"):
            value = plan()
            item = value["resource_changes"][0]
            if mutation == "foreign":
                item["address"] = "aws_s3_bucket.unexpected"
            elif mutation in ("delete", "replace"):
                item["change"]["actions"] = ["delete"] if mutation == "delete" else ["delete", "create"]
            elif mutation == "import":
                item["change"]["importing"] = {"id": ROLE}
            elif mutation == "unknown":
                item["change"]["after_unknown"]["assume_role_policy"] = True
            elif mutation == "incomplete":
                value["resource_changes"] = []
            else:
                value["resource_drift"] = [{"address": ROLE_ADDRESS}]
            with self.subTest(mutation=mutation), self.assertRaises(Stop):
                plan_check(value, CONFIG, "existing", {})

    def test_plan_rejects_grants_and_wildcard(self):
        for key, entry in (("managed_policy_arns", ["AdministratorAccess"]),
                           ("inline_policy", [{"policy": "{}"}]),
                           ("assume_role_policy", json.dumps({"Statement": [{"Action": "*"}]}))):
            value = plan()
            value["resource_changes"][0]["change"]["after"][key] = entry
            with self.assertRaises(Stop):
                plan_check(value, CONFIG, "existing", {})

    def test_only_task_to_main_transition(self):
        value = plan()
        change = value["resource_changes"][0]["change"]
        change["actions"] = ["update"]
        change["before"] = copy.deepcopy(change["after"])
        previous = dict(CONFIG, trust_phase="task", task_expires_at="2020-01-01T00:00:00Z")
        change["before"]["assume_role_policy"] = json.dumps(trust(previous))
        plan_check(value, CONFIG, "existing", {ROLE_ADDRESS: {}})
        change["after"]["max_session_duration"] = 7200
        with self.assertRaises(Stop):
            plan_check(value, CONFIG, "existing", {ROLE_ADDRESS: {}})

    def test_aws_error_sanitized(self):
        with patch.object(bootstrap, "private_path", side_effect=RuntimeError("SENTINEL_PRIVATE")), patch("sys.stderr", new_callable=io.StringIO) as error:
            self.assertEqual(bootstrap.main(["inventory", "--config", "x", "--state", "y", "--inventory", "z"]), 1)
            self.assertNotIn("SENTINEL_PRIVATE", error.getvalue())

    def test_inventory_access_denied_not_absent(self):
        result = type("Result", (), {"returncode": 1, "stderr": "An error occurred (AccessDenied) SENTINEL_PRIVATE"})
        with patch("subprocess.run", return_value=result), self.assertRaises(Stop):
            bootstrap.aws_read(["iam", "get-role"], "us-east-1", True)

    def test_empty_provider_response_does_not_mean_absent(self):
        identity = {"Account": ACCOUNT, "Arn": f"arn:aws:sts::{ACCOUNT}:assumed-role/PersonalBlogAdministrator/test"}
        with tempfile.TemporaryDirectory() as temporary, patch.object(bootstrap, "aws_read", side_effect=[identity, {}]):
            with self.assertRaisesRegex(Stop, "PROVIDER_DISCREPANT_C"):
                bootstrap.inventory(CONFIG, Path(temporary) / "absent.tfstate")

    def test_plan_rejects_endpoint_overrides_and_computed_grants(self):
        value = plan()
        value["configuration"]["provider_config"]["aws"]["expressions"]["endpoints"] = {}
        with self.assertRaises(Stop):
            plan_check(value, CONFIG, "existing", {})
        value = plan()
        value["configuration"]["root_module"]["resources"] = [{"mode": "managed", "type": "aws_iam_role",
                                                               "expressions": {"inline_policy": {}}}]
        with self.assertRaises(Stop):
            plan_check(value, CONFIG, "existing", {})

    def test_plan_must_match_verified_variables(self):
        value = plan()
        value["variables"]["expected_account_id"]["value"] = "999999999999"
        with self.assertRaises(Stop):
            plan_check(value, CONFIG, "existing", {})

    def test_plan_accepts_post_apply_convergence(self):
        # Ambos recursos ya existen y el plan no cambia nada: la guarda debe
        # aceptarlo mientras el literal temporal siga vigente.
        config = live_task_config()
        plan_check(converged(config), config, "create",
                   {ROLE_ADDRESS: {}, PROVIDER_ADDRESS: {}})

    def test_plan_rejects_convergence_once_expiry_passed(self):
        # Deliberado, no defecto: plan-check tambien es la puerta previa al apply y
        # un literal vencido nunca debe pasarla. La convergencia posterior al apply
        # se acredita con el exit code de Terraform, no reejecutando esta guarda.
        config = dict(CONFIG, trust_phase="task", task_expires_at="2020-01-01T00:00:00Z")
        with self.assertRaisesRegex(Stop, "EXPIRY_WINDOW"):
            plan_check(converged(config), config, "create",
                       {ROLE_ADDRESS: {}, PROVIDER_ADDRESS: {}})

    def test_plan_provider_url_accepts_both_representations(self):
        # Esta prueba exigia antes el esquema, y era un error demostrado: el
        # 2026-09-25 la transicion real fue rechazada con PLAN_PROVIDER, y
        # GetOpenIDConnectProvider confirmo que IAM devuelve el host **sin**
        # esquema. Un create arrastra el valor configurado; un no-op refrescado
        # arrastra el de IAM. Ambos designan el mismo endpoint, y el runbook ya
        # los declaraba equivalentes.
        config = live_task_config()
        resources = {ROLE_ADDRESS: {}, PROVIDER_ADDRESS: {}}
        for url in ("https://token.actions.githubusercontent.com",
                    "token.actions.githubusercontent.com"):
            with self.subTest(url=url):
                value = converged(config)
                value["resource_changes"][-1]["change"]["after"]["url"] = url
                plan_check(value, config, "create", resources)

    def test_plan_provider_url_rejects_anything_else(self):
        # La comparacion es semantica, no laxa: solo el host exacto, con https
        # opcional y nada mas.
        config = live_task_config()
        resources = {ROLE_ADDRESS: {}, PROVIDER_ADDRESS: {}}
        for url in ("http://token.actions.githubusercontent.com",
                    "https://token.actions.githubusercontent.com/",
                    "token.actions.githubusercontent.com:443",
                    "https://evil.example", "evil.example",
                    "token.actions.githubusercontent.com.evil.example",
                    "https://https://token.actions.githubusercontent.com",
                    "", None, 42):
            with self.subTest(url=url), self.assertRaisesRegex(Stop, "PLAN_PROVIDER"):
                value = converged(config)
                value["resource_changes"][-1]["change"]["after"]["url"] = url
                plan_check(value, config, "create", resources)

    def test_provider_url_helper_is_exact(self):
        self.assertTrue(provider_url_ok("token.actions.githubusercontent.com"))
        self.assertTrue(provider_url_ok("https://token.actions.githubusercontent.com"))
        for value in ("http://token.actions.githubusercontent.com", "evil.example",
                      "https://evil.example", "", None, 42, ["x"]):
            with self.subTest(value=value):
                self.assertFalse(provider_url_ok(value))

    def test_convergent_plan_still_rejects_grants(self):
        # La convergencia no relaja nada: una politica adjunta se sigue rechazando.
        config = live_task_config()
        value = converged(config)
        value["resource_changes"][1]["change"]["after"]["managed_policy_arns"] = ["AdministratorAccess"]
        with self.assertRaisesRegex(Stop, "PLAN_GRANT"):
            plan_check(value, config, "create", {ROLE_ADDRESS: {}, PROVIDER_ADDRESS: {}})

    def test_inventory_requires_explicit_aws(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config"
            config.write_text(json.dumps(CONFIG))
            config.chmod(0o600)
            with patch.object(bootstrap, "inventory") as call, patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(bootstrap.main(["inventory", "--config", str(config), "--state", str(root / "state"), "--inventory", str(root / "inventory")]), 1)
                call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
