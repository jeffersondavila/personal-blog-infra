variable "nombre" {
  type        = string
  description = "Prefijo de nombres del root de datos, p. ej. `blog-prod`. Nombra la regla del grupo de seguridad."

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}[a-z0-9]$", var.nombre))
    error_message = "El nombre debe ser corto, en minusculas y sin caracteres especiales."
  }
}

variable "nombre_del_rol" {
  type        = string
  description = "Rol de ejecucion PROPIO de la ejecutora (`PersonalBlogEjecutorDatos`). La politica se le anade inline."

  validation {
    condition     = can(regex("^PersonalBlog[A-Za-z]{4,40}$", var.nombre_del_rol))
    error_message = "El rol de la ejecutora sigue el esquema PersonalBlog<Nombre>."
  }
}

variable "arn_del_bucket" {
  type        = string
  description = <<-DESC
    ARN del bucket de medios que administra `terraform-medios`; el root lo recibe por contrato explicito
    (`arn_del_bucket_de_medios`). Sin puntos en el nombre: el modo export usa el estilo de host virtual.
  DESC

  validation {
    condition     = can(regex("^arn:aws:s3:::[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$", var.arn_del_bucket))
    error_message = "Se espera el ARN de un bucket sin puntos, sin comodines ni rutas de objeto."
  }
}

variable "id_sg_admin" {
  type        = string
  description = "`sg-admin` (salida `id_sg_admin` de la red): el unico grupo de la ejecutora."
}

variable "prefix_list_s3" {
  type        = string
  description = "Prefix list del gateway endpoint de S3 (salida `prefix_list_s3` de la red)."

  validation {
    condition     = can(regex("^pl-[0-9a-z]+$", var.prefix_list_s3))
    error_message = "Se espera el ID de una prefix list (pl-...)."
  }
}

variable "id_del_endpoint_s3" {
  type        = string
  description = "Gateway endpoint de S3 (salida `id_endpoint_s3` de la red). Condiciona la politica con `aws:SourceVpce`."

  validation {
    condition     = can(regex("^vpce-[0-9a-z]+$", var.id_del_endpoint_s3))
    error_message = "Se espera el ID de un VPC endpoint (vpce-...)."
  }
}
