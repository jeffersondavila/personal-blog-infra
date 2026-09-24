variable "expected_account_id" {
  type        = string
  description = "Verified human destination; supplied privately, never committed."
  validation {
    condition     = can(regex("^[0-9]{12}$", var.expected_account_id)) && var.expected_account_id != "000000000000"
    error_message = "A non-placeholder AWS account is required."
  }
}

variable "aws_region" {
  type = string
  validation {
    condition     = can(regex("^(us|eu|ap|sa|ca|me|af|il|mx)-(east|west|north|south|central|northeast|southeast)-[1-9]$", var.aws_region))
    error_message = "An explicit commercial AWS region is required."
  }
}

variable "provider_mode" {
  type        = string
  description = "create only for A/owned continuation; existing only for compatible B."
  validation {
    condition     = contains(["create", "existing"], var.provider_mode)
    error_message = "Provider ownership must be explicit."
  }
}

variable "trust_phase" {
  type    = string
  default = "main"
  validation {
    condition     = contains(["task", "main"], var.trust_phase)
    error_message = "Only task or main is supported."
  }
}

variable "task_expires_at" {
  type        = string
  default     = null
  nullable    = true
  description = "Literal UTC expiry supplied by human for temporary trust; never generated."
  validation {
    condition     = var.task_expires_at == null ? true : can(regex("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$", var.task_expires_at))
    error_message = "Expiry must be an explicit UTC literal."
  }
}
