variable "nombre" {
  type        = string
  description = "Nombre de la funcion, p. ej. `blog-prod-ejecutor`. Tambien nombra su grupo de logs."

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,40}-ejecutor$", var.nombre))
    error_message = "El nombre de la ejecutora es `<prefijo>-ejecutor`, en minusculas."
  }
}

variable "nombre_del_rol" {
  type        = string
  description = "Rol de ejecucion PROPIO de la ejecutora (D-24 §8.2): `PersonalBlogEjecutorDatos`."

  validation {
    condition     = can(regex("^PersonalBlog[A-Za-z]{4,40}$", var.nombre_del_rol))
    error_message = "El rol de la ejecutora sigue el esquema PersonalBlog<Nombre>."
  }
}

variable "region" {
  type        = string
  description = "Region de la funcion. Construye los ARN de la politica, para que el plan la muestre completa."
}

variable "cuenta" {
  type        = string
  description = "Cuenta verificada por la guarda de identidad del root. Construye los ARN de la politica."

  validation {
    condition     = can(regex("^[0-9]{12}$", var.cuenta))
    error_message = "Se espera un Account ID de 12 digitos."
  }
}

variable "ids_de_subredes" {
  type        = list(string)
  description = "Las DOS subredes privadas del root de datos (salida `ids_de_subredes` de la red)."

  validation {
    condition     = length(var.ids_de_subredes) == 2 && length(distinct(var.ids_de_subredes)) == 2
    error_message = "La ejecutora va en exactamente las dos subredes privadas, distintas."
  }
}

variable "id_sg_admin" {
  type        = string
  description = "`sg-admin` (salida `id_sg_admin` de la red). Es el UNICO grupo de la ejecutora: nunca `sg-lambda` ni el grupo por omision."
}

variable "ruta_del_zip" {
  type        = string
  description = <<-DESC
    Ruta del ZIP que construye `scripts/terraform_datos/empaquetar_ejecutor.py`. Entrada EXPLICITA: este
    repositorio versiona la fuente y el pin, no el ZIP.
  DESC
}

variable "sha256_del_zip" {
  type        = string
  description = "SHA-256 esperado del ZIP, en hexadecimal. Si el archivo no coincide, el plan se detiene."

  validation {
    condition     = can(regex("^[0-9a-f]{64}$", var.sha256_del_zip))
    error_message = "Se espera un SHA-256 en hexadecimal, 64 caracteres en minusculas."
  }
}

variable "dias_de_retencion_de_logs" {
  type        = number
  description = "Retencion del grupo de logs de la ejecutora: el baseline de D-11 del root (14 dias)."

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30], var.dias_de_retencion_de_logs)
    error_message = "Retencion corta y explicita: 1, 3, 5, 7, 14 o 30 dias. Nunca infinita."
  }
}
