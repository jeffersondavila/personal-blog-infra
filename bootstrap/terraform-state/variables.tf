variable "expected_account_id" {
  description = "Destination verified privately with STS; not a credential. Never use the validation role."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[0-9]{12}$", var.expected_account_id)) && var.expected_account_id != "000000000000"
    error_message = "An explicit, verified AWS account is required."
  }
}

locals {
  region      = "us-east-2"
  name_suffix = substr(sha256("personal-blog:terraform-state:${var.expected_account_id}:${local.region}"), 0, 12)
  bucket_name = "personal-blog-tfstate-${local.region}-${local.name_suffix}"
  state_key   = "bootstrap/terraform-state/terraform.tfstate"
  oidc_key    = "bootstrap/github-oidc/terraform.tfstate"
  tags = {
    Proyecto   = "personal-blog"
    Entorno    = "produccion"
    Gestion    = "terraform"
    Componente = "terraform-state"
    Tarea      = "Task/030"
  }
}
