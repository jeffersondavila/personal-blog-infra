provider "aws" {
  region              = var.aws_region
  allowed_account_ids = [var.expected_account_id]
}

data "aws_caller_identity" "human" {
  lifecycle {
    postcondition {
      condition = (
        self.account_id == var.expected_account_id &&
        can(regex(format("^arn:aws:sts::%s:assumed-role/PersonalBlogAdministrator/[^/]+$", var.expected_account_id), self.arn))
      )
      error_message = "STOP: expected human administration role and destination required."
    }
  }
}
