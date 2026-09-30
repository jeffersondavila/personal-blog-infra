"""Security regressions: the first plan cannot expand or weaken its approved scope."""
import copy
import json
import unittest

from scripts.terraform_state.check_plan import ADDRESSES, FLAGS, TAGS, bucket_name, check

ACCOUNT = "123456789012"


def fixture():
    name = bucket_name(ACCOUNT)
    values = {
        "aws_s3_account_public_access_block.account": {"account_id": ACCOUNT, **dict.fromkeys(FLAGS, True)},
        "aws_s3_bucket.state": {"bucket": name, "force_destroy": False, "region": "us-east-2", "tags_all": TAGS},
        "aws_s3_bucket_public_access_block.state": dict.fromkeys(FLAGS, True),
        "aws_s3_bucket_ownership_controls.state": {"rule": [{"object_ownership": "BucketOwnerEnforced"}]},
        "aws_s3_bucket_versioning.state": {"versioning_configuration": [{"status": "Enabled"}]},
        "aws_s3_bucket_server_side_encryption_configuration.state": {
            "rule": [{"apply_server_side_encryption_by_default": [{"sse_algorithm": "AES256"}]}]},
        "aws_s3_bucket_policy.state": {"policy": json.dumps({"Version": "2012-10-17", "Statement": [{
            "Sid": "DenyInsecureTransport", "Effect": "Deny", "Principal": "*", "Action": "s3:*",
            "Resource": [f"arn:aws:s3:::{name}", f"arn:aws:s3:::{name}/*"],
            "Condition": {"Bool": {"aws:SecureTransport": "false"}},
        }]})},
    }
    return {
        "terraform_version": "1.16.2", "applyable": True, "complete": True,
        "variables": {"expected_account_id": {"value": ACCOUNT}},
        "resource_changes": [{"address": a, "mode": "managed", "provider_name": "registry.terraform.io/hashicorp/aws",
                              "change": {"actions": ["create"], "before": None, "after": values[a]}} for a in sorted(ADDRESSES)],
        "planned_values": {"outputs": {
            "future_s3_backend": {"value": {"bucket": name, "key": "bootstrap/terraform-state/terraform.tfstate",
                                             "region": "us-east-2", "encrypt": True, "use_lockfile": True}},
            "future_state_keys": {"value": {"bootstrap": "bootstrap/terraform-state/terraform.tfstate",
                                           "github_oidc": "bootstrap/github-oidc/terraform.tfstate"}},
        }},
        "checks": [{"status": "pass"}],
    }


class PlanGateTests(unittest.TestCase):
    def test_expected_plan(self):
        result = check(fixture(), ACCOUNT)
        self.assertEqual((result["add"], result["change"], result["destroy"]), (7, 0, 0))
        self.assertNotIn(ACCOUNT, result["bucket"])

    def test_any_change_other_than_create_rejected(self):
        for actions in [["delete"], ["delete", "create"], ["create", "delete"], ["update"], ["no-op"]]:
            with self.subTest(actions=actions):
                plan = fixture(); plan["resource_changes"][0]["change"]["actions"] = actions
                with self.assertRaisesRegex(ValueError, "NOT_CREATE_ONLY"): check(plan, ACCOUNT)

    def test_iam_or_application_resource_rejected(self):
        for address in ["aws_iam_policy.deploy", "aws_lambda_function.app", "aws_s3_bucket.media"]:
            with self.subTest(address=address):
                plan = fixture(); extra = copy.deepcopy(plan["resource_changes"][0]); extra["address"] = address
                plan["resource_changes"].append(extra)
                with self.assertRaisesRegex(ValueError, "UNEXPECTED_RESOURCE"): check(plan, ACCOUNT)

    def test_import_rejected(self):
        plan = fixture(); plan["resource_changes"][0]["change"]["importing"] = {"id": "existing"}
        with self.assertRaisesRegex(ValueError, "IMPORT_OR_MOVE"): check(plan, ACCOUNT)

    def test_move_rejected(self):
        plan = fixture(); plan["resource_changes"][0]["previous_address"] = "old.address"
        with self.assertRaisesRegex(ValueError, "IMPORT_OR_MOVE"): check(plan, ACCOUNT)

    def test_missing_control_rejected(self):
        plan = fixture(); plan["resource_changes"].pop()
        with self.assertRaisesRegex(ValueError, "RESOURCE_SET"): check(plan, ACCOUNT)

    def test_each_public_access_flag_required_at_both_scopes(self):
        for address in ["aws_s3_account_public_access_block.account", "aws_s3_bucket_public_access_block.state"]:
            for flag in FLAGS:
                with self.subTest(address=address, flag=flag):
                    plan = fixture()
                    next(r for r in plan["resource_changes"] if r["address"] == address)["change"]["after"][flag] = False
                    with self.assertRaisesRegex(ValueError, "PUBLIC_ACCESS"): check(plan, ACCOUNT)

    def test_new_kms_key_rejected(self):
        plan = fixture()
        entry = next(r for r in plan["resource_changes"] if "encryption" in r["address"])
        entry["change"]["after"]["rule"][0]["apply_server_side_encryption_by_default"][0]["sse_algorithm"] = "aws:kms"
        with self.assertRaisesRegex(ValueError, "ENCRYPTION"): check(plan, ACCOUNT)

    def test_allow_public_policy_rejected(self):
        plan = fixture(); entry = next(r for r in plan["resource_changes"] if r["address"] == "aws_s3_bucket_policy.state")
        policy = json.loads(entry["change"]["after"]["policy"]); policy["Statement"][0]["Effect"] = "Allow"
        entry["change"]["after"]["policy"] = json.dumps(policy)
        with self.assertRaisesRegex(ValueError, "POLICY"): check(plan, ACCOUNT)

    def test_disabled_lock_rejected(self):
        plan = fixture(); plan["planned_values"]["outputs"]["future_s3_backend"]["value"]["use_lockfile"] = False
        with self.assertRaisesRegex(ValueError, "BACKEND_CONTRACT"): check(plan, ACCOUNT)

    def test_incomplete_and_drift_rejected(self):
        for key, value in [("complete", False), ("resource_drift", [{"address": "unexpected"}]), ("deferred_changes", [{}])]:
            with self.subTest(key=key):
                plan = fixture(); plan[key] = value
                with self.assertRaises(ValueError): check(plan, ACCOUNT)

    def test_wrong_destination_rejected(self):
        with self.assertRaisesRegex(ValueError, "ACCOUNT"): check(fixture(), "999999999999")


if __name__ == "__main__":
    unittest.main()
