terraform {
  required_version = "= 1.16.2"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.64.0"
    }
  }
  # EX-028-C7: init requires a private, external path from the runbook.
  # Never initialize this backend without -backend-config.
  backend "local" {}
}
