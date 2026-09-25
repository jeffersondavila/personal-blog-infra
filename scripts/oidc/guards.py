"""Pure fail-closed checks. Errors contain fixed codes, never input values."""
import datetime as dt
import json
import os
from pathlib import Path
import re
import stat
import sys

ROLE = "PersonalBlogGitHubOidcValidation"
HUMAN = "PersonalBlogAdministrator"
HOST = "token.actions.githubusercontent.com"
AUDIENCE = "sts.amazonaws.com"
PREFIX = "repo:jeffersondavila@60154716/personal-blog-infra@1313255836"
TASK = "Task/028-GitHub-OIDC-AWS"
ROLE_ADDRESS = "aws_iam_role.validation"
PROVIDER_ADDRESS = "aws_iam_openid_connect_provider.github[0]"
REGION = r"(us|eu|ap|sa|ca|me|af|il|mx)-(east|west|north|south|central|northeast|southeast)-[1-9]"
# Two operator environments are supported, both explicit: AWS CloudShell (Linux,
# ambient container credentials) and the human Windows workstation (named profile
# refreshed by `aws login`). Nothing else, and never an implicit default profile.
EXPECTED_PROFILE = "personal-blog"


class Stop(ValueError):
    """Only use fixed, non-sensitive error codes."""


def require(condition, code):
    if not condition:
        raise Stop(code)


def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def instant(value):
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", value), "EXPIRY_FORMAT")
    try:
        return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        raise Stop("EXPIRY_FORMAT") from None


def config_check(config, now=None, check_future=True):
    require(set(config) == {"expected_account_id", "aws_region", "trust_phase", "task_expires_at"}, "CONFIG_FIELDS")
    account = config["expected_account_id"]
    require(isinstance(account, str) and re.fullmatch(r"\d{12}", account) and account != "000000000000", "ACCOUNT")
    require(isinstance(config["aws_region"], str) and re.fullmatch(REGION, config["aws_region"]), "REGION")
    require(config["trust_phase"] in ("task", "main"), "PHASE")
    if config["trust_phase"] == "main":
        require(config["task_expires_at"] is None, "MAIN_EXPIRY")
    else:
        expiry = instant(config["task_expires_at"])
        if check_future:
            remaining = expiry - (now or utcnow())
            require(dt.timedelta(0) < remaining <= dt.timedelta(hours=2), "EXPIRY_WINDOW")
    return config


def environment_check(profile, platform=None, environ=None):
    """Bind real AWS work to one of the two supported, explicit environments.

    Linux means CloudShell and its ambient session: a named profile there would
    silently pick another identity, so it is refused. Windows means the human
    workstation, where the profile must be named explicitly. In both cases an
    inherited AWS_PROFILE is refused, because it would decide the destination
    without appearing in the command that was reviewed.
    """
    platform = sys.platform if platform is None else platform
    environ = os.environ if environ is None else environ
    require(platform in ("linux", "win32"), "UNSUPPORTED_PLATFORM")
    if platform == "linux":
        require(profile is None, "CLOUDSHELL_PROFILE_FORBIDDEN")
    else:
        require(profile == EXPECTED_PROFILE, "LOCAL_PROFILE_REQUIRED")
    require(not environ.get("AWS_PROFILE") and not environ.get("AWS_DEFAULT_PROFILE"),
            "IMPLICIT_PROFILE")
    if environ.get("AWS_ACCESS_KEY_ID"):
        require(environ["AWS_ACCESS_KEY_ID"].startswith("ASIA")
                and bool(environ.get("AWS_SESSION_TOKEN")), "STATIC_CREDENTIALS")
    return platform


def provider_arn(account):
    return f"arn:aws:iam::{account}:oidc-provider/{HOST}"


def trust(config):
    config_check(config, check_future=False)
    branch = TASK if config["trust_phase"] == "task" else "main"
    condition = {"StringEquals": {f"{HOST}:aud": AUDIENCE, f"{HOST}:sub": f"{PREFIX}:ref:refs/heads/{branch}"}}
    if config["trust_phase"] == "task":
        condition["DateLessThan"] = {"aws:CurrentTime": config["task_expires_at"]}
    return {"Version": "2012-10-17", "Statement": [{
        "Effect": "Allow", "Principal": {"Federated": provider_arn(config["expected_account_id"])},
        "Action": "sts:AssumeRoleWithWebIdentity", "Condition": condition,
    }]}


def human_check(identity, account):
    require(identity.get("Account") == account and
            re.fullmatch(f"arn:aws:sts::{account}:assumed-role/{HUMAN}/[^/]+", identity.get("Arn", "")), "HUMAN_IDENTITY")


def provider_case(document, error=None):
    if error == "NoSuchEntity" and document is None:
        return "A"
    require(error is None and isinstance(document, dict), "PROVIDER_INCONCLUSIVE")
    require(document.get("Url") in (HOST, f"https://{HOST}") and
            document.get("ClientIDList") == [AUDIENCE], "PROVIDER_DISCREPANT_C")
    # TLS for GitHub is validated with AWS root CAs. Thumbprints are recorded,
    # not rewritten; IAM trust conditions belong to the role, not the provider.
    return "B"


def private_path(value, repo, directory=False, must_exist=True):
    path = Path(value)
    require(path.is_absolute(), "PATH_ABSOLUTE")
    require(not path.absolute().is_relative_to(Path(repo).absolute()), "PATH_IN_REPO")
    resolved = path.resolve()
    require(not resolved.is_relative_to(Path(repo).resolve()), "PATH_IN_REPO")
    # Reject every other Git checkout too, even ignored paths.
    for parent in (resolved, *resolved.parents):
        require(not (parent / ".git").exists(), "PATH_IN_GIT")
    require(not path.is_symlink(), "PATH_SYMLINK")
    require(not must_exist or resolved.exists(), "PATH_MISSING")
    anchor = resolved if resolved.exists() else resolved.parent
    require(anchor.exists(), "PATH_PARENT")
    if resolved.exists():
        require(resolved.is_dir() if directory else resolved.is_file(), "PATH_TYPE")
    if os.name != "nt":
        # Immediate private root and leaf; ancestors such as /home may be 0755.
        for item in {anchor, anchor if anchor.is_dir() else anchor.parent}:
            mode = item.stat()
            require(mode.st_uid == os.getuid() and mode.st_mode & 0o077 == 0, "PATH_PERMISSIONS")
    else:
        # Windows has no POSIX mode. The per-user LOCALAPPDATA tree is the private
        # root the operator protects by ACL; junctions and symlinks could redirect
        # a checked path elsewhere, so a reparse point is refused outright. This is
        # a scope guard, not a full ACL audit: the ACL itself stays operator-owned.
        local = os.environ.get("LOCALAPPDATA", "")
        require(bool(local), "WINDOWS_PRIVATE_ROOT")
        require(resolved.is_relative_to(Path(local).resolve()), "WINDOWS_PRIVATE_ROOT")
        for item in {anchor, anchor if anchor.is_dir() else anchor.parent}:
            attributes = getattr(os.lstat(item), "st_file_attributes", 0)
            require(not attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT, "PATH_REPARSE")
    return resolved


def state_resources(document, account):
    if document is None:
        return {}
    require(document.get("version") == 4 and document.get("lineage") and
            isinstance(document.get("serial"), int), "STATE_FORMAT")
    result = {}
    for resource in document.get("resources", []):
        if resource.get("mode") == "data":
            continue
        base = f"{resource.get('type')}.{resource.get('name')}"
        require(not resource.get("module"), "STATE_MODULE")
        for instance in resource.get("instances", []):
            address = base + (f"[{instance['index_key']}]" if "index_key" in instance else "")
            require(address in (ROLE_ADDRESS, PROVIDER_ADDRESS) and address not in result and
                    not instance.get("deposed"), "STATE_RESOURCE")
            attributes = instance.get("attributes", {})
            expected = provider_arn(account) if address == PROVIDER_ADDRESS else f"arn:aws:iam::{account}:role/{ROLE}"
            require(attributes.get("arn") == expected, "STATE_DESTINATION")
            result[address] = attributes
    return result


def ownership(case, resources, role_exists):
    owns = PROVIDER_ADDRESS in resources
    require(not (case == "A" and owns), "PROVIDER_MISSING_OWNED")
    require(role_exists == (ROLE_ADDRESS in resources), "ROLE_OWNERSHIP")
    return "create" if case == "A" or owns else "existing"


def role_check(role, attached, inline, expected_trust, account):
    require(role.get("Arn") == f"arn:aws:iam::{account}:role/{ROLE}" and role.get("RoleName") == ROLE and
            role.get("Path") == "/" and role.get("MaxSessionDuration") == 3600, "ROLE_PROPERTIES")
    require(attached == [] and inline == [] and not role.get("PermissionsBoundary"), "ROLE_POLICIES")
    require(role.get("AssumeRolePolicyDocument") == expected_trust, "ROLE_TRUST")


def has_unknown(value):
    """Terraform's unknown markers preserve nested list/object shapes."""
    if isinstance(value, dict):
        return any(has_unknown(item) for item in value.values())
    if isinstance(value, list):
        return any(has_unknown(item) for item in value)
    require(value is None or isinstance(value, bool), "PLAN_UNKNOWN_FORMAT")
    return value is True


def plan_check(plan, config, mode, resources):
    config_check(config)
    require(plan.get("format_version") == "1.2" and plan.get("terraform_version") == "1.16.2" and
            not plan.get("errored") and plan.get("complete", True) and
            not plan.get("deferred_changes") and not plan.get("resource_drift"), "PLAN_FORMAT_OR_DRIFT")
    require(mode in ("create", "existing"), "PLAN_MODE")
    variables = plan.get("variables", {})
    require({key: value.get("value") for key, value in variables.items()} ==
            dict(config, provider_mode=mode), "PLAN_VARIABLES")
    configuration = plan.get("configuration", {})
    root = configuration.get("root_module", {})
    require(not root.get("module_calls"), "PLAN_MODULES")
    providers = configuration.get("provider_config", {})
    require(set(providers) == {"aws"} and providers["aws"].get("full_name") == "registry.terraform.io/hashicorp/aws" and
            set(providers["aws"].get("expressions", {})) == {"region", "allowed_account_ids"}, "PLAN_PROVIDER_CONFIG")
    # Computed policy collections can be unknown on a newly created IAM role.
    # They are allowed only if absent from configuration; no expression may grant.
    for resource in root.get("resources", []):
        expressions = resource.get("expressions", {})
        if resource.get("mode") == "managed":
            resource_type = resource.get("type")
            allowed = ({"name", "path", "description", "max_session_duration", "assume_role_policy"}
                       if resource_type == "aws_iam_role" else {"url", "client_id_list"})
            require(resource_type in ("aws_iam_role", "aws_iam_openid_connect_provider") and
                    set(expressions) <= allowed, "PLAN_RESOURCE_CONFIG")
    allowed_data = {"data.aws_caller_identity.human", "data.aws_iam_openid_connect_provider.existing[0]"}
    expected = {ROLE_ADDRESS} | ({PROVIDER_ADDRESS} if mode == "create" else set())
    seen = set()
    for item in plan.get("resource_changes", []):
        change = item.get("change", {})
        require(not change.get("importing") and not item.get("previous_address"), "PLAN_ADOPTION")
        address = item.get("address")
        if item.get("mode") == "data":
            require(address in allowed_data and change.get("actions") in (["read"], ["no-op"]), "PLAN_DATA")
            continue
        require(address in expected and address not in seen, "PLAN_RESOURCE")
        seen.add(address)
        actions = change.get("actions")
        require(actions in (["create"], ["update"], ["no-op"]), "PLAN_DESTRUCTIVE")
        require((actions == ["create"]) == (address not in resources), "PLAN_STATE")
        after = change.get("after") or {}
        unknown = change.get("after_unknown", {})
        if address == ROLE_ADDRESS:
            fixed = {"name": ROLE, "path": "/", "max_session_duration": 3600,
                     "description": "Task028 federation validation only; no resource permissions"}
            require(all(after.get(k) == v and not has_unknown(unknown.get(k)) for k, v in fixed.items()), "PLAN_ROLE")
            require(not has_unknown(unknown.get("assume_role_policy")), "PLAN_TRUST_UNKNOWN")
            try:
                actual_trust = json.loads(after.get("assume_role_policy", ""))
            except (ValueError, TypeError):
                raise Stop("PLAN_TRUST") from None
            require(actual_trust == trust(config), "PLAN_TRUST")
            for key in ("managed_policy_arns", "inline_policy", "permissions_boundary", "tags", "tags_all", "force_detach_policies"):
                require(not after.get(key), "PLAN_GRANT")
                # Computed empty collections may be unknown on a fresh role.
                require(actions == ["create"] or not has_unknown(unknown.get(key)), "PLAN_GRANT_UNKNOWN")
            if actions == ["update"]:
                before = change.get("before") or {}
                require(all(before.get(k) == after.get(k) for k in set(before) | set(after)
                            if k != "assume_role_policy"), "PLAN_ROLE_UPDATE")
                # Only Task -> main; expiry renewal/reopening Task requires a new review.
                old = json.loads(before.get("assume_role_policy", "{}"))
                old_config = dict(config, trust_phase="task", task_expires_at=old.get("Statement", [{}])[0].get("Condition", {}).get("DateLessThan", {}).get("aws:CurrentTime"))
                require(config["trust_phase"] == "main" and old == trust(old_config), "PLAN_TRANSITION")
        else:
            require(actions in (["create"], ["no-op"]), "PLAN_PROVIDER_UPDATE")
            require(after.get("url") == f"https://{HOST}" and after.get("client_id_list") == [AUDIENCE] and
                    not after.get("tags") and not after.get("tags_all"), "PLAN_PROVIDER")
            require(not has_unknown(unknown.get("url")) and not has_unknown(unknown.get("client_id_list")), "PLAN_PROVIDER_UNKNOWN")
    require(seen == expected, "PLAN_INCOMPLETE")
