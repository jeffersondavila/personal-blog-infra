variable "expected_account_id" {
  type        = string
  description = "Cuenta verificada; se aporta en privado y nunca se versiona."
  validation {
    condition     = can(regex("^[0-9]{12}$", var.expected_account_id)) && var.expected_account_id != "000000000000"
    error_message = "Se exige una cuenta AWS real, no un marcador."
  }
}

variable "aws_region" {
  type        = string
  default     = "us-east-2"
  description = "Region de la red y RDS de Task/031. La politica la fija: no es configurable."
  validation {
    condition     = var.aws_region == "us-east-2"
    error_message = "La identidad operativa de Task/031 solo opera en us-east-2 (H-1)."
  }
}

variable "usuario_de_entrada" {
  type        = string
  default     = "personal-blog-entry-admin"
  description = <<-DESC
    Usuario IAM de entrada de Task/027: sin permisos propios, sin access keys y
    con MFA. El trust lo nombra por ARN exacto. No se modifica: en la misma
    cuenta, el trust que nombra al usuario basta para asumir el rol.
  DESC
  validation {
    condition     = can(regex("^[A-Za-z0-9+=,.@_-]{1,64}$", var.usuario_de_entrada))
    error_message = "Nombre de usuario IAM invalido."
  }
}

variable "crear_rol_vinculado_de_rds" {
  type        = bool
  description = <<-DESC
    `true` solo si el preflight de H-031-IAM demuestra que `AWSServiceRoleForRDS`
    NO existe. Si existe, no se gestiona ni se importa: se registra. Sin el rol
    vinculado, el primer `CreateDBInstance` pediria `iam:CreateServiceLinkedRole`
    al operador, que no lo tiene a proposito.
  DESC
}
