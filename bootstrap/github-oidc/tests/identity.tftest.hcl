mock_provider "aws" {
  override_during = plan
  mock_data "aws_caller_identity" {
    defaults = {
      account_id = "123456789012"
      arn        = "arn:aws:sts::123456789012:assumed-role/PersonalBlogAdministrator/mock"
    }
  }
  mock_data "aws_iam_openid_connect_provider" {
    defaults = {
      url            = "token.actions.githubusercontent.com"
      client_id_list = ["sts.amazonaws.com"]
    }
  }
}

variables {
  expected_account_id = "123456789012"
  aws_region          = "us-east-1"
  provider_mode       = "create"
}

run "absent_main" {
  command = plan
  assert {
    condition     = length(aws_iam_openid_connect_provider.github) == 1 && aws_iam_role.validation.max_session_duration == 3600
    error_message = "Case A must create one provider and one validation role."
  }
  assert {
    condition     = jsondecode(aws_iam_role.validation.assume_role_policy).Statement[0].Condition.StringEquals["token.actions.githubusercontent.com:sub"] == "repo:jeffersondavila@60154716/personal-blog-infra@1313255836:ref:refs/heads/main"
    error_message = "Final trust must name only main."
  }
}

run "existing_reference" {
  command = plan
  variables { provider_mode = "existing" }
  assert {
    condition     = length(aws_iam_openid_connect_provider.github) == 0 && length(data.aws_iam_openid_connect_provider.existing) == 1
    error_message = "Case B must never own the existing provider."
  }
}

run "discrepant_provider" {
  command = plan
  variables { provider_mode = "existing" }
  override_data {
    target = data.aws_iam_openid_connect_provider.existing[0]
    values = {
      url            = "token.actions.githubusercontent.com"
      client_id_list = ["sts.amazonaws.com", "unexpected"]
    }
  }
  expect_failures = [data.aws_iam_openid_connect_provider.existing]
}

run "wrong_human" {
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

run "missing_expiry" {
  command = plan
  variables { trust_phase = "task" }
  expect_failures = [aws_iam_role.validation]
}

run "expired" {
  command = plan
  variables {
    trust_phase     = "task"
    task_expires_at = "2020-01-01T00:00:00Z"
  }
  expect_failures = [aws_iam_role.validation]
}

run "excessive_expiry" {
  command = plan
  variables {
    trust_phase     = "task"
    task_expires_at = "2099-01-01T00:00:00Z"
  }
  expect_failures = [aws_iam_role.validation]
}

run "main_cannot_keep_expiry" {
  command = plan
  variables { task_expires_at = "2099-01-01T00:00:00Z" }
  expect_failures = [aws_iam_role.validation]
}

run "temporary_literal_trust" {
  command = plan
  # Synthetic test input only. Production never computes or renews the expiry.
  variables {
    trust_phase     = "task"
    task_expires_at = timeadd(timestamp(), "1h")
  }
  assert {
    condition = (
      jsondecode(aws_iam_role.validation.assume_role_policy).Statement[0].Condition.DateLessThan["aws:CurrentTime"] == var.task_expires_at &&
      endswith(jsondecode(aws_iam_role.validation.assume_role_policy).Statement[0].Condition.StringEquals["token.actions.githubusercontent.com:sub"], ":ref:refs/heads/Task/028-GitHub-OIDC-AWS")
    )
    error_message = "Temporary trust must preserve exactly the supplied expiry and Task subject."
  }
}
