import base64
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.oidc import verify
from scripts.oidc.guards import PREFIX, ROLE, TASK, Stop

ENV = {"GITHUB_REPOSITORY": "jeffersondavila/personal-blog-infra",
       "GITHUB_REPOSITORY_ID": "1313255836", "GITHUB_REPOSITORY_OWNER_ID": "60154716",
       "GITHUB_REF_TYPE": "branch", "GITHUB_REF": f"refs/heads/{TASK}", "GITHUB_EVENT_NAME": "push",
       "AWS_EXPECTED_ACCOUNT_ID": "123456789012", "AWS_REGION": "us-east-1",
       "AWS_OIDC_ROLE_ARN": f"arn:aws:iam::123456789012:role/{ROLE}"}
CONFIG = {"schema_version": 1, "task_expectation": "SUCCESS"}


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.network = patch.object(verify, "exchange", side_effect=AssertionError("NO_NETWORK_ALLOWED"))
        self.network.start()
        self.addCleanup(self.network.stop)

    def test_context_task_main(self):
        self.assertEqual(verify.context(CONFIG, ENV), "SUCCESS")
        self.assertEqual(verify.context(dict(CONFIG, task_expectation="DENIED"), ENV), "DENIED")
        self.assertEqual(verify.context(dict(CONFIG, task_expectation="DENIED"),
                                       dict(ENV, GITHUB_REF="refs/heads/main", GITHUB_EVENT_NAME="workflow_dispatch")), "SUCCESS")

    def test_other_contexts_rejected(self):
        for changes in ({"GITHUB_REF": "refs/heads/dev"}, {"GITHUB_REF": "refs/tags/v1"},
                        {"GITHUB_EVENT_NAME": "pull_request"}, {"GITHUB_EVENT_NAME": "pull_request_target"},
                        {"GITHUB_REPOSITORY_ID": "other"}, {"GITHUB_REPOSITORY_OWNER_ID": "other"},
                        {"GITHUB_REPOSITORY": "fork/repo"}, {"GITHUB_EVENT_NAME": "workflow_dispatch"}):
            with self.subTest(changes=changes), self.assertRaises(Stop):
                verify.context(CONFIG, dict(ENV, **changes))

    def test_positive_and_negative_operations(self):
        identity = {"Account": "123456789012", "Arn": f"arn:aws:sts::123456789012:assumed-role/{ROLE}/task028-validation"}
        with patch.object(verify, "jwt_for", return_value="synthetic") as jwt, patch.object(
                verify, "assume", side_effect=[("SUCCESS", {}), ("InvalidIdentityToken", None)]), patch.object(
                verify, "aws_with_session", side_effect=[("SUCCESS", identity), ("AccessDenied", None)]):
            messages = verify.verify(CONFIG, ENV)
            self.assertEqual(len(messages), 3)
            self.assertEqual(jwt.call_args_list[1].args[0], verify.WRONG_AUDIENCE)

    def test_task_denied_exact_error_only(self):
        for result in ("AccessDenied", "InvalidIdentityToken", "SUCCESS"):
            with patch.object(verify, "jwt_for", return_value="synthetic"), patch.object(verify, "assume", return_value=(result, None)):
                if result == "AccessDenied":
                    self.assertEqual(len(verify.verify(dict(CONFIG, task_expectation="DENIED"), ENV)), 1)
                else:
                    with self.assertRaises(Stop):
                        verify.verify(dict(CONFIG, task_expectation="DENIED"), ENV)

    def test_static_credentials_fail_before_token(self):
        with patch.object(verify, "jwt_for") as jwt, self.assertRaises(Stop):
            verify.verify(CONFIG, dict(ENV, AWS_PROFILE="unexpected"))
        jwt.assert_not_called()

    def test_wrong_destination_fail_before_token(self):
        with patch.object(verify, "jwt_for") as jwt, self.assertRaises(Stop):
            verify.verify(CONFIG, dict(ENV, AWS_OIDC_ROLE_ARN="arn:aws:iam::999999999999:role/other"))
        jwt.assert_not_called()

    def test_github_claims_checked_without_logging(self):
        claims = {"iss": "https://token.actions.githubusercontent.com", "aud": "sts.amazonaws.com",
                  "sub": f"{PREFIX}:ref:{ENV['GITHUB_REF']}"}
        encoded = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
        fake = "synthetic." + encoded + ".unsigned"
        environment = dict(ENV, ACTIONS_ID_TOKEN_REQUEST_URL="https://example.actions.githubusercontent.com/token",
                           ACTIONS_ID_TOKEN_REQUEST_TOKEN="synthetic-bearer")
        with patch.object(verify, "exchange", return_value=(200, json.dumps({"value": fake}).encode())) as exchange:
            self.assertEqual(verify.jwt_for("sts.amazonaws.com", environment), fake)
            self.assertIn("audience=sts.amazonaws.com", exchange.call_args.args[0].full_url)
            with self.assertRaises(Stop):
                verify.jwt_for("unexpected", environment)

    def test_token_endpoint_cannot_redirect_or_use_http(self):
        for endpoint in ("http://example.actions.githubusercontent.com/token", "https://evil.example/token",
                         "https://example.actions.githubusercontent.com.evil.example/token"):
            with self.assertRaises(Stop):
                verify.jwt_for("sts.amazonaws.com", dict(ENV, ACTIONS_ID_TOKEN_REQUEST_URL=endpoint, ACTIONS_ID_TOKEN_REQUEST_TOKEN="synthetic"))
        with self.assertRaises(Stop):
            verify.NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.example")

    def test_sts_error_classification(self):
        for code in ("AccessDenied", "InvalidIdentityToken", "ExpiredToken", "ServiceUnavailable"):
            xml = f'<ErrorResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/"><Error><Code>{code}</Code><Message>PRIVATE</Message></Error></ErrorResponse>'.encode()
            with patch.object(verify, "exchange", return_value=(403, xml)):
                if code in ("AccessDenied", "InvalidIdentityToken"):
                    self.assertEqual(verify.assume("synthetic", ENV["AWS_OIDC_ROLE_ARN"], "us-east-1")[0], code)
                else:
                    with self.assertRaises(Stop):
                        verify.assume("synthetic", ENV["AWS_OIDC_ROLE_ARN"], "us-east-1")

    def test_cli_captures_errors_without_credentials_in_arguments(self):
        credentials = dict.fromkeys(("AccessKeyId", "SecretAccessKey", "SessionToken"), "PRIVATE_SENTINEL")
        result = type("Result", (), {"returncode": 1, "stderr": "An error occurred (AccessDenied) PRIVATE_SENTINEL"})
        with patch("subprocess.run", return_value=result) as run:
            self.assertEqual(verify.aws_with_session(["iam", "list-roles"], credentials, "us-east-1"), ("AccessDenied", None))
            self.assertNotIn("PRIVATE_SENTINEL", repr(run.call_args.args))
            self.assertTrue(run.call_args.kwargs["capture_output"])
            self.assertNotIn("ACTIONS_ID_TOKEN_REQUEST_TOKEN", run.call_args.kwargs["env"])

    def test_network_failure_is_not_denial(self):
        with patch.object(verify, "jwt_for", side_effect=TimeoutError("PRIVATE_SENTINEL")), patch(
                "sys.stderr", new_callable=io.StringIO) as output, patch.dict("os.environ", ENV, clear=True):
            self.assertEqual(verify.main([]), 1)
            self.assertNotIn("PRIVATE_SENTINEL", output.getvalue())

    def test_no_token_capability(self):
        with patch.dict("os.environ", {}, clear=True), patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(verify.main(["--no-id-token"]), 0)
        with patch.dict("os.environ", {"ACTIONS_ID_TOKEN_REQUEST_TOKEN": "private"}, clear=True), patch("sys.stderr", new_callable=io.StringIO) as output:
            self.assertEqual(verify.main(["--no-id-token"]), 1)
            self.assertNotIn("private", output.getvalue())

    def test_workflow_has_no_secret_artifacts_or_extra_events(self):
        workflow = Path(".github/workflows/verify-aws-oidc.yml").read_text()
        self.assertNotIn("pull_request", workflow)
        self.assertNotIn("upload-artifact", workflow)
        self.assertNotIn("secrets.", workflow)
        self.assertNotIn("environment:", workflow)
        self.assertEqual(workflow.count("id-token: write"), 1)
        self.assertIn("permissions: {}", workflow)


if __name__ == "__main__":
    unittest.main()
