terraform {
  required_version = "= 1.16.2"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.64.0"
    }
  }

  # D-06: partial S3 configuration is supplied from the private operator directory.
  # H-030-2 authorizes migration with native S3 locking and no DynamoDB.
  backend "s3" {}
}
