"""Offline H-030-1 gate. Reads a private plan JSON; never calls AWS or applies it."""
import argparse
import hashlib
import json
from pathlib import Path

ADDRESSES = {
    "aws_s3_account_public_access_block.account",
    "aws_s3_bucket.state",
    "aws_s3_bucket_public_access_block.state",
    "aws_s3_bucket_ownership_controls.state",
    "aws_s3_bucket_versioning.state",
    "aws_s3_bucket_server_side_encryption_configuration.state",
    "aws_s3_bucket_policy.state",
}
FLAGS = ("block_public_acls", "block_public_policy", "ignore_public_acls", "restrict_public_buckets")
TAGS = {"Proyecto": "personal-blog", "Entorno": "produccion", "Gestion": "terraform",
        "Componente": "terraform-state", "Tarea": "Task/030"}


def require(condition, code):
    if not condition:
        raise ValueError(code)


def bucket_name(account):
    suffix = hashlib.sha256(f"personal-blog:terraform-state:{account}:us-east-2".encode()).hexdigest()[:12]
    return f"personal-blog-tfstate-us-east-2-{suffix}"


def check(plan, account):
    require(plan.get("terraform_version") == "1.16.2", "VERSION")
    require(plan.get("applyable") is True and plan.get("complete") is True and not plan.get("errored"), "INCOMPLETE")
    require(not plan.get("resource_drift") and not plan.get("deferred_changes"), "DRIFT_OR_DEFERRED")
    require(plan["variables"]["expected_account_id"]["value"] == account, "ACCOUNT")
    changes = plan.get("resource_changes", [])
    resources = {}
    for item in changes:
        change = item["change"]
        require(not change.get("importing") and not item.get("previous_address"), "IMPORT_OR_MOVE")
        if item["mode"] == "data":
            require(item["address"] == "data.aws_caller_identity.human" and change["actions"] == ["no-op"], "DATA_SOURCE")
            continue
        require(item["address"] in ADDRESSES and item["address"] not in resources, "UNEXPECTED_RESOURCE")
        require(change["actions"] == ["create"] and change.get("before") is None, "NOT_CREATE_ONLY")
        require(item["provider_name"] == "registry.terraform.io/hashicorp/aws", "PROVIDER")
        resources[item["address"]] = change["after"]
    require(set(resources) == ADDRESSES, "RESOURCE_SET")
    name = bucket_name(account)
    bucket = resources["aws_s3_bucket.state"]
    require(bucket["bucket"] == name and bucket["force_destroy"] is False, "BUCKET")
    require(bucket["tags_all"] == TAGS and bucket.get("region") == "us-east-2", "TAGS_OR_REGION")
    for address in ("aws_s3_account_public_access_block.account", "aws_s3_bucket_public_access_block.state"):
        require(all(resources[address].get(flag) is True for flag in FLAGS), "PUBLIC_ACCESS")
    require(resources["aws_s3_account_public_access_block.account"]["account_id"] == account, "GLOBAL_ACCOUNT")
    require(resources["aws_s3_bucket_ownership_controls.state"]["rule"] == [{"object_ownership": "BucketOwnerEnforced"}], "OWNERSHIP")
    require(resources["aws_s3_bucket_versioning.state"]["versioning_configuration"][0]["status"] == "Enabled", "VERSIONING")
    encryption = resources["aws_s3_bucket_server_side_encryption_configuration.state"]["rule"]
    require(len(encryption) == 1, "ENCRYPTION")
    default = encryption[0]["apply_server_side_encryption_by_default"][0]
    require(default["sse_algorithm"] == "AES256" and not default.get("kms_master_key_id"), "ENCRYPTION")
    policy = json.loads(resources["aws_s3_bucket_policy.state"]["policy"])
    require(policy == {"Version": "2012-10-17", "Statement": [{
        "Sid": "DenyInsecureTransport", "Effect": "Deny", "Principal": "*", "Action": "s3:*",
        "Resource": [f"arn:aws:s3:::{name}", f"arn:aws:s3:::{name}/*"],
        "Condition": {"Bool": {"aws:SecureTransport": "false"}},
    }]}, "POLICY")
    outputs = plan["planned_values"]["outputs"]
    require(outputs["future_s3_backend"]["value"] == {
        "bucket": name, "key": "bootstrap/terraform-state/terraform.tfstate",
        "region": "us-east-2", "encrypt": True, "use_lockfile": True,
    }, "BACKEND_CONTRACT")
    require(outputs["future_state_keys"]["value"] == {
        "bootstrap": "bootstrap/terraform-state/terraform.tfstate",
        "github_oidc": "bootstrap/github-oidc/terraform.tfstate",
    }, "KEYS")
    require(all(c["status"] == "pass" for c in plan.get("checks", [])), "CHECKS")
    return {"add": len(resources), "change": 0, "destroy": 0, "bucket": name,
            "addresses": sorted(resources)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan_json", type=Path)
    parser.add_argument("--variables", required=True, type=Path)
    args = parser.parse_args()
    try:
        raw = args.plan_json.read_bytes()
        account = json.loads(args.variables.read_text(encoding="utf-8"))["expected_account_id"]
        result = check(json.loads(raw), account)
    except (ValueError, KeyError, TypeError, IndexError, OSError):
        raise SystemExit("H-030-4: plan rejected; inspect privately. No apply authorized.") from None
    print(json.dumps({"gate": "PLAN_OK", "json_sha256": hashlib.sha256(raw).hexdigest(), **result}))


if __name__ == "__main__":
    main()
