locals {
  provider_url = "https://token.actions.githubusercontent.com"
  provider_arn = format("arn:aws:iam::%s:oidc-provider/token.actions.githubusercontent.com", var.expected_account_id)
  ref          = var.trust_phase == "task" ? "Task/028-GitHub-OIDC-AWS" : "main"
  subject      = format("repo:jeffersondavila@60154716/personal-blog-infra@1313255836:ref:refs/heads/%s", local.ref)
  trust = {
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = local.provider_arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = merge({
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          "token.actions.githubusercontent.com:sub" = local.subject
        }
        }, var.trust_phase == "task" ? {
        DateLessThan = { "aws:CurrentTime" = var.task_expires_at }
      } : {})
    }]
  }
}

# Case B: no import and no managed ownership of an existing/shared provider.
data "aws_iam_openid_connect_provider" "existing" {
  count = var.provider_mode == "existing" ? 1 : 0
  arn   = local.provider_arn
  lifecycle {
    postcondition {
      condition = (
        contains([local.provider_url, trimprefix(local.provider_url, "https://")], self.url) &&
        toset(self.client_id_list) == toset(["sts.amazonaws.com"])
      )
      error_message = "STOP: provider differs; do not modify, import or repair."
    }
  }
}

# Case A only, or continuation with this exact resource already in trusted state.
# GitHub uses AWS's trusted CA validation; no thumbprint is invented or overwritten.
resource "aws_iam_openid_connect_provider" "github" {
  count          = var.provider_mode == "create" ? 1 : 0
  url            = local.provider_url
  client_id_list = ["sts.amazonaws.com"]
  depends_on     = [data.aws_caller_identity.human]
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_iam_role" "validation" {
  name                 = "PersonalBlogGitHubOidcValidation"
  path                 = "/"
  description          = "Task028 federation validation only; no resource permissions"
  max_session_duration = 3600
  assume_role_policy   = jsonencode(local.trust)
  depends_on = [
    data.aws_caller_identity.human,
    data.aws_iam_openid_connect_provider.existing,
    aws_iam_openid_connect_provider.github,
  ]
  # No inline policy, attachment, permissions boundary or application permission.
  # Readback checks absence of out-of-band grants before and after each mutation.
  lifecycle {
    prevent_destroy = true
    precondition {
      condition = var.trust_phase == "main" ? var.task_expires_at == null : try(
        timecmp(var.task_expires_at, plantimestamp()) > 0 &&
        timecmp(var.task_expires_at, timeadd(plantimestamp(), "2h")) <= 0,
        false
      )
      error_message = "Task requires literal future expiry <= 2h; main requires null."
    }
  }
}
