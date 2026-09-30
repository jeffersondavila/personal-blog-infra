provider "aws" {
  region              = local.region
  profile             = "personal-blog"
  allowed_account_ids = [var.expected_account_id]

  default_tags {
    tags = local.tags
  }
}

data "aws_caller_identity" "human" {
  lifecycle {
    postcondition {
      condition = (
        self.account_id == var.expected_account_id &&
        can(regex("^arn:aws:sts::${var.expected_account_id}:assumed-role/PersonalBlogAdministrator/[^/]+$", self.arn)) &&
        terraform.workspace == "default"
      )
      error_message = "STOP: expected human administration role, account and default workspace required."
    }
  }
}
