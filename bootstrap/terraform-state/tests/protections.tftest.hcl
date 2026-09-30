mock_provider "aws" {
  override_during = plan
  mock_data "aws_caller_identity" {
    defaults = {
      account_id = "123456789012"
      arn        = "arn:aws:sts::123456789012:assumed-role/PersonalBlogAdministrator/mock"
    }
  }
}

variables {
  expected_account_id = "123456789012"
}

run "private_recoverable_bootstrap" {
  command = plan
  assert {
    condition = alltrue([
      aws_s3_account_public_access_block.account.block_public_acls,
      aws_s3_account_public_access_block.account.block_public_policy,
      aws_s3_account_public_access_block.account.ignore_public_acls,
      aws_s3_account_public_access_block.account.restrict_public_buckets,
      aws_s3_bucket_public_access_block.state.block_public_acls,
      aws_s3_bucket_public_access_block.state.block_public_policy,
      aws_s3_bucket_public_access_block.state.ignore_public_acls,
      aws_s3_bucket_public_access_block.state.restrict_public_buckets,
    ])
    error_message = "Both scopes require all four public access protections."
  }
  assert {
    condition = (
      !aws_s3_bucket.state.force_destroy &&
      aws_s3_bucket_versioning.state.versioning_configuration[0].status == "Enabled" &&
      one(aws_s3_bucket_ownership_controls.state.rule).object_ownership == "BucketOwnerEnforced" &&
      one(one(aws_s3_bucket_server_side_encryption_configuration.state.rule).apply_server_side_encryption_by_default).sse_algorithm == "AES256"
    )
    error_message = "State must be recoverable, private, encrypted with SSE-S3 and without ACLs."
  }
  assert {
    condition = (
      output.future_s3_backend.use_lockfile && output.future_s3_backend.encrypt &&
      output.future_s3_backend.region == "us-east-2" &&
      output.future_state_keys.bootstrap != output.future_state_keys.github_oidc &&
      output.future_state_keys.github_oidc == "bootstrap/github-oidc/terraform.tfstate" &&
      !strcontains(output.future_s3_backend.bucket, var.expected_account_id)
    )
    error_message = "Backend destinations must preserve D-06 and separate the two roots."
  }
  assert {
    condition = (
      length(jsondecode(aws_s3_bucket_policy.state.policy).Statement) == 1 &&
      jsondecode(aws_s3_bucket_policy.state.policy).Statement[0].Effect == "Deny" &&
      jsondecode(aws_s3_bucket_policy.state.policy).Statement[0].Condition.Bool["aws:SecureTransport"] == "false"
    )
    error_message = "Policy must deny non-TLS access and must not grant public access."
  }
}

run "validation_role_rejected" {
  command = plan
  override_data {
    target = data.aws_caller_identity.human
    values = {
      account_id = "123456789012"
      arn        = "arn:aws:sts::123456789012:assumed-role/PersonalBlogGitHubOidcValidation/mock"
    }
  }
  expect_failures = [data.aws_caller_identity.human]
}

run "root_rejected" {
  command = plan
  override_data {
    target = data.aws_caller_identity.human
    values = {
      account_id = "123456789012"
      arn        = "arn:aws:iam::123456789012:root"
    }
  }
  expect_failures = [data.aws_caller_identity.human]
}

run "other_account_rejected" {
  command = plan
  override_data {
    target = data.aws_caller_identity.human
    values = {
      account_id = "999999999999"
      arn        = "arn:aws:sts::999999999999:assumed-role/PersonalBlogAdministrator/mock"
    }
  }
  expect_failures = [data.aws_caller_identity.human]
}

run "invalid_account_rejected" {
  command = plan
  variables { expected_account_id = "000000000000" }
  expect_failures = [var.expected_account_id]
}
