variable "nombre" {
  type        = string
  description = "Prefijo de nombres del root de datos, p. ej. `blog-prod`."

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}[a-z0-9]$", var.nombre))
    error_message = "El nombre debe ser corto, en minusculas y sin caracteres especiales."
  }
}

variable "ruta_base" {
  type        = string
  description = "Ruta SSM de las credenciales de datos, la misma de la master: `/<prefijo>/datos`."

  validation {
    condition     = can(regex("^/[a-z][a-z0-9-]{2,20}[a-z0-9]/datos$", var.ruta_base))
    error_message = "Se espera /<prefijo>/datos, sin barra final."
  }
}

variable "contrasena_blog_migrate" {
  type        = string
  sensitive   = true
  ephemeral   = true
  description = "Contrasena de `blog_migrate`. EFIMERA: ni plan ni state; se aporta en cada plan y al aplicarlo."

  validation {
    condition     = can(regex("^[A-Za-z0-9]{32,64}$", var.contrasena_blog_migrate))
    error_message = "La contrasena debe tener entre 32 y 64 caracteres alfanumericos."
  }
}

variable "contrasena_blog_app" {
  type        = string
  sensitive   = true
  ephemeral   = true
  description = "Contrasena de `blog_app`. EFIMERA: ni plan ni state; se aporta en cada plan y al aplicarlo."

  validation {
    condition     = can(regex("^[A-Za-z0-9]{32,64}$", var.contrasena_blog_app))
    error_message = "La contrasena debe tener entre 32 y 64 caracteres alfanumericos."
  }
}

variable "version_de_blog_migrate" {
  type        = number
  default     = 1
  description = "Incrementarla rota la contrasena de `blog_migrate`: es lo que dispara la escritura write-only."

  validation {
    condition     = var.version_de_blog_migrate >= 1 && floor(var.version_de_blog_migrate) == var.version_de_blog_migrate
    error_message = "La version es un entero positivo."
  }
}

variable "version_de_blog_app" {
  type        = number
  default     = 1
  description = "Incrementarla rota la contrasena de `blog_app`: es lo que dispara la escritura write-only."

  validation {
    condition     = var.version_de_blog_app >= 1 && floor(var.version_de_blog_app) == var.version_de_blog_app
    error_message = "La version es un entero positivo."
  }
}
