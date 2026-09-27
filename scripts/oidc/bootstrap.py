"""Manual bootstrap assistance. All AWS reads require --aws-real.

No apply, import, destroy, policy attachment or GitHub mutation is implemented.
Run from repository root with python -B -m scripts.oidc.bootstrap.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

from .guards import (ROLE, ROLE_ADDRESS, Stop, config_check, environment_check,
                     human_check, instant, ownership, plan_check, private_path,
                     provider_arn, provider_case, require, role_check,
                     state_resources, trust, utcnow)

REPO = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def aws_read(arguments, region, absent_ok=False, profile=None):
    require(not any(k.startswith("AWS_ENDPOINT_URL") or k in ("AWS_CA_BUNDLE",) for k in os.environ), "AWS_ENDPOINT_OVERRIDE")
    # The profile travels as an explicit argument, never as inherited environment.
    selector = ["--profile", profile] if profile else []
    result = subprocess.run(
        ["aws", *arguments, "--region", region, *selector, "--output", "json", "--no-cli-pager"],
        capture_output=True, text=True, timeout=45, check=False,
        env=dict(os.environ, AWS_PAGER="", AWS_CLI_AUTO_PROMPT="off"),
    )
    if result.returncode:
        # Never emit AWS stderr: it can contain an identifier or sensitive input.
        match = re.search(r"An error occurred \(([A-Za-z0-9]+)\)", result.stderr)
        if absent_ok and match and match.group(1) == "NoSuchEntity":
            return None
        raise Stop("AWS_READ_FAILED")
    return json.loads(result.stdout)


def write_private(path, document):
    # Refuse symlinks; the parent was checked and is private. Atomic replacement.
    require(not path.is_symlink(), "PATH_SYMLINK")
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("x", encoding="utf-8", newline="\n") as stream:
        if os.name != "nt":
            os.chmod(temporary, 0o600)
        json.dump(document, stream, indent=2)
        stream.write("\n")
    os.replace(temporary, path)


def inventory(config, state, verify_target=False, profile=None):
    account, region = config["expected_account_id"], config["aws_region"]
    human_check(aws_read(["sts", "get-caller-identity"], region, profile=profile), account)
    resources = state_resources(read(state) if state.exists() else None, account)
    provider = aws_read(["iam", "get-open-id-connect-provider", "--open-id-connect-provider-arn", provider_arn(account)], region, True, profile)
    case = provider_case(provider, "NoSuchEntity" if provider is None else None)
    response = aws_read(["iam", "get-role", "--role-name", ROLE], region, True, profile)
    mode = ownership(case, resources, response is not None)
    if response is not None:
        attached = aws_read(["iam", "list-attached-role-policies", "--role-name", ROLE], region, profile=profile)
        inline = aws_read(["iam", "list-role-policies", "--role-name", ROLE], region, profile=profile)
        previous = json.loads(resources[ROLE_ADDRESS]["assume_role_policy"])
        conditions = previous.get("Statement", [{}])[0].get("Condition", {})
        previous_config = dict(config, trust_phase="main", task_expires_at=None)
        if "DateLessThan" in conditions:
            previous_config.update(trust_phase="task", task_expires_at=conditions["DateLessThan"].get("aws:CurrentTime"))
        require(previous == trust(previous_config), "STATE_TRUST")
        role_check(response["Role"], attached["AttachedPolicies"], inline["PolicyNames"],
                   trust(config) if verify_target else previous, account)
    require(not verify_target or response is not None, "READBACK_ROLE_MISSING")
    return {"observed_case": case, "ownership": "owned-A" if mode == "create" and provider else case,
            "provider_mode": mode, "provider_thumbprints": provider.get("ThumbprintList", []) if provider else [],
            "checked_at": utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "state_sha256": digest(state), "config": config,
            "role_present": response is not None, "resource_policy_inventory": []}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("inventory", "plan-check"))
    parser.add_argument("--config", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--plan")
    parser.add_argument("--aws-real", action="store_true")
    parser.add_argument("--aws-profile", default=None,
                        help="Named AWS profile. Required on Windows, refused on CloudShell.")
    parser.add_argument("--verify-target", action="store_true")
    args = parser.parse_args(argv)
    try:
        config_path = private_path(args.config, REPO)
        state = private_path(args.state, REPO, must_exist=False)
        inv_path = private_path(args.inventory, REPO, must_exist=args.operation != "inventory")
        require(config_path != state and inv_path not in (config_path, state), "PATH_COLLISION")
        config = config_check(read(config_path))
        if args.operation == "inventory":
            require(args.aws_real, "EXPLICIT_AWS_REQUIRED")
            environment_check(args.aws_profile)
            data_dir = private_path(os.environ.get("TF_DATA_DIR", ""), REPO, directory=True)
            require(data_dir not in (state.parent, inv_path.parent) and
                    not any(k.startswith("TF_CLI_ARGS") or k in ("TF_LOG", "TF_LOG_PATH")
                            for k in os.environ), "TF_ENVIRONMENT")
            generated = inv_path.parent / "bootstrap.auto.tfvars.json"
            require(generated not in (config_path, state, inv_path), "PATH_COLLISION")
            result = inventory(config, state, args.verify_target, args.aws_profile)
            write_private(inv_path, result)
            write_private(generated, dict(config, provider_mode=result["provider_mode"]))
            print("INVENTORY_OK case=" + result["observed_case"] + " ownership=" + result["ownership"])
        else:
            require(not args.aws_real and args.plan and not args.verify_target
                    and args.aws_profile is None, "PLAN_ARGUMENTS")
            inv = read(inv_path)
            require(inv["config"] == config and inv["state_sha256"] == digest(state), "INVENTORY_BINDING")
            age = (utcnow() - instant(inv["checked_at"])).total_seconds()
            require(0 <= age <= 600, "INVENTORY_STALE")
            plan_path = private_path(args.plan, REPO)
            data_dir = private_path(os.environ.get("TF_DATA_DIR", ""), REPO, directory=True)
            metadata = read(private_path(data_dir / "terraform.tfstate", REPO))
            backend = metadata.get("backend", {})
            require(backend.get("type") == "local" and
                    Path(backend.get("config", {}).get("path", "")).resolve() == state and
                    os.environ.get("TF_WORKSPACE", "default") == "default", "BACKEND_BINDING")
            plan_check(read(plan_path), config, inv["provider_mode"], state_resources(read(state) if state.exists() else None, config["expected_account_id"]))
            print("PLAN_OK json_sha256=" + digest(plan_path))
        return 0
    except Exception:
        # Fixed output even for parser/filesystem/SDK errors: no exception repr.
        print("STOP: OIDC bootstrap guard rejected the operation; inspect privately.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
