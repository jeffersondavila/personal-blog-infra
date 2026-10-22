provider "aws" {
  region              = var.aws_region
  allowed_account_ids = [var.expected_account_id]
}

# Este root es el UNICO lugar donde la identidad administrativa puede operar en
# Task/031: crea la identidad operativa y nada mas (H-031-IAM).
data "aws_caller_identity" "bootstrap" {
  lifecycle {
    postcondition {
      condition = (
        self.account_id == var.expected_account_id &&
        can(regex(format("^arn:aws:sts::%s:assumed-role/PersonalBlogAdministrator/[^/]+$", var.expected_account_id), self.arn))
      )
      error_message = "STOP: el bootstrap de la identidad operativa solo lo ejecuta PersonalBlogAdministrator, en la cuenta verificada."
    }
  }
}
