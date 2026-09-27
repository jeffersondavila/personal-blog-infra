"""GitHub federation probe: no credentials, tokens or response bodies are logged."""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from .guards import AUDIENCE, PREFIX, REGION, ROLE, TASK, Stop, require, utcnow, instant

WRONG_AUDIENCE = "urn:personal-blog:task028:negative-audience"
NAMESPACE = {"s": "https://sts.amazonaws.com/doc/2011-06-15/"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Stop("HTTP_REDIRECT")


def exchange(request):
    # No inherited HTTP proxy; HTTPS certificate verification stays enabled.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=25) as response:
            return response.status, response.read(131073)
    except urllib.error.HTTPError as error:
        return error.code, error.read(131073)


def context(config, environment):
    require(config == {"schema_version": 1, "task_expectation": config.get("task_expectation")} and
            config["task_expectation"] in ("SUCCESS", "DENIED"), "EXPECTATION")
    require(environment.get("GITHUB_REPOSITORY") == "jeffersondavila/personal-blog-infra" and
            environment.get("GITHUB_REPOSITORY_ID") == "1313255836" and
            environment.get("GITHUB_REPOSITORY_OWNER_ID") == "60154716", "REPOSITORY")
    ref, event = environment.get("GITHUB_REF"), environment.get("GITHUB_EVENT_NAME")
    require(environment.get("GITHUB_REF_TYPE") == "branch", "REF_TYPE")
    if ref == f"refs/heads/{TASK}" and event == "push":
        return config["task_expectation"]
    require(ref == "refs/heads/main" and event == "workflow_dispatch", "CONTEXT")
    return "SUCCESS"


def jwt_for(audience, environment):
    endpoint = environment.get("ACTIONS_ID_TOKEN_REQUEST_URL", "")
    bearer = environment.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")
    parsed = urllib.parse.urlsplit(endpoint)
    require(parsed.scheme == "https" and parsed.hostname and
            parsed.hostname.endswith(".actions.githubusercontent.com") and
            not parsed.username and not parsed.password and parsed.port in (None, 443) and
            not parsed.fragment and bearer, "OIDC_ENDPOINT")
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query = [(key, value) for key, value in query if key != "audience"]
    query.append(("audience", audience))
    url = urllib.parse.urlunsplit(parsed._replace(query=urllib.parse.urlencode(query)))
    status, body = exchange(urllib.request.Request(url, headers={"Authorization": "Bearer " + bearer}))
    require(status == 200 and len(body) <= 131072, "OIDC_HTTP")
    token = json.loads(body)["value"]
    require(isinstance(token, str) and len(token) < 65536, "OIDC_RESPONSE")
    parts = token.split(".")
    require(len(parts) == 3, "OIDC_TOKEN")
    claims = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
    # Decoding is an early assertion, NOT signature verification. STS verifies.
    require(claims.get("iss") == "https://token.actions.githubusercontent.com" and
            claims.get("aud") == audience and
            claims.get("sub") == f"{PREFIX}:ref:{environment['GITHUB_REF']}", "OIDC_CLAIMS")
    return token


def assume(token, role_arn, region):
    body = urllib.parse.urlencode({
        "Action": "AssumeRoleWithWebIdentity", "Version": "2011-06-15",
        "RoleArn": role_arn, "RoleSessionName": "task028-validation",
        "DurationSeconds": "900", "WebIdentityToken": token,
    }).encode()
    status, response = exchange(urllib.request.Request(
        f"https://sts.{region}.amazonaws.com/", data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"}))
    require(len(response) <= 131072, "STS_SIZE")
    root = ET.fromstring(response)
    if status != 200:
        code = root.findtext("s:Error/s:Code", namespaces=NAMESPACE)
        require(status in (400, 403) and code in ("AccessDenied", "InvalidIdentityToken"), "STS_UNEXPECTED_ERROR")
        return code, None
    credentials = root.find("s:AssumeRoleWithWebIdentityResult/s:Credentials", NAMESPACE)
    require(credentials is not None, "STS_CREDENTIALS")
    values = {key: credentials.findtext("s:" + key, namespaces=NAMESPACE)
              for key in ("AccessKeyId", "SecretAccessKey", "SessionToken", "Expiration")}
    require(all(isinstance(value, str) and value for value in values.values()), "STS_CREDENTIALS")
    remaining = (instant(values["Expiration"]) - utcnow()).total_seconds()
    require(0 < remaining <= 930, "STS_DURATION")
    return "SUCCESS", values


def aws_with_session(arguments, credentials, region):
    # Credentials only in this child process environment; never GITHUB_ENV,
    # command arguments, artifacts, disk or parent environment.
    environment = {key: value for key, value in os.environ.items()
                   if key in ("PATH", "SYSTEMROOT", "HOME", "LANG", "TMPDIR")}
    environment.update(
        AWS_ACCESS_KEY_ID=credentials["AccessKeyId"],
        AWS_SECRET_ACCESS_KEY=credentials["SecretAccessKey"],
        AWS_SESSION_TOKEN=credentials["SessionToken"],
        AWS_CONFIG_FILE=os.devnull, AWS_SHARED_CREDENTIALS_FILE=os.devnull,
        AWS_EC2_METADATA_DISABLED="true", AWS_CLI_AUTO_PROMPT="off", AWS_PAGER="",
    )
    result = subprocess.run(["aws", *arguments, "--region", region, "--output", "json", "--no-cli-pager"],
                            capture_output=True, text=True, timeout=25, env=environment, check=False)
    if result.returncode:
        match = re.search(r"An error occurred \(([A-Za-z0-9]+)\)", result.stderr)
        require(match is not None and match.group(1) == "AccessDenied", "AWS_UNEXPECTED_ERROR")
        return "AccessDenied", None
    return "SUCCESS", json.loads(result.stdout)


def verify(config, environment):
    expected = context(config, environment)
    require(not any(environment.get(key) for key in (
        "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
        "AWS_PROFILE", "AWS_WEB_IDENTITY_TOKEN_FILE")), "STATIC_CREDENTIALS")
    account, region, role_arn = (environment.get(key, "") for key in
                               ("AWS_EXPECTED_ACCOUNT_ID", "AWS_REGION", "AWS_OIDC_ROLE_ARN"))
    require(re.fullmatch(r"\d{12}", account) and account != "000000000000" and
            re.fullmatch(REGION, region) and role_arn == f"arn:aws:iam::{account}:role/{ROLE}", "DESTINATION")
    outcome, credentials = assume(jwt_for(AUDIENCE, environment), role_arn, region)
    if expected == "DENIED":
        require(outcome == "AccessDenied", "TASK_REJECTION_REQUIRED")
        return ["Task fresh-token STS: AccessDenied (expected)"]
    require(outcome == "SUCCESS", "FEDERATION_REQUIRED")
    status, identity = aws_with_session(["sts", "get-caller-identity"], credentials, region)
    require(status == "SUCCESS" and identity.get("Account") == account and
            identity.get("Arn") == f"arn:aws:sts::{account}:assumed-role/{ROLE}/task028-validation", "CALLER_IDENTITY")
    denied, _ = aws_with_session(["iam", "list-roles", "--max-items", "1"], credentials, region)
    require(denied == "AccessDenied", "NEGATIVE_IAM_REQUIRED")
    wrong, _ = assume(jwt_for(WRONG_AUDIENCE, environment), role_arn, region)
    require(wrong == "InvalidIdentityToken", "NEGATIVE_AUDIENCE_REQUIRED")
    return ["GetCallerIdentity: expected account and role",
            "iam:ListRoles: AccessDenied (scope: this operation only)",
            "Wrong audience: InvalidIdentityToken (provider/trust chain)"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="security/oidc-validation.json")
    parser.add_argument("--no-id-token", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.no_id_token:
            require(not os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN") and
                    not os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL"), "ID_TOKEN_AVAILABLE")
            print("GitHub job without id-token: token request unavailable (GitHub-side evidence)")
        else:
            config = json.loads(Path(args.config).read_text(encoding="utf-8"))
            for line in verify(config, dict(os.environ)):
                print(line)
        return 0
    except Exception:
        print("STOP: OIDC verification failed; no raw response or credential emitted.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
