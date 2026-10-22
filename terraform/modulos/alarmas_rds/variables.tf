variable "nombre" {
  type        = string
  description = "Prefijo de nombres del root de datos, p. ej. `blog-prod`. Las alarmas se llaman `<prefijo>-rds-<senal>`."

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}[a-z0-9]$", var.nombre))
    error_message = "El nombre debe ser corto, en minusculas y sin caracteres especiales."
  }
}

variable "identificador_de_la_instancia" {
  type        = string
  description = "Identificador de la instancia productiva (`<prefijo>-postgres`). Nunca una restaurada temporal."

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}[a-z0-9]-postgres$", var.identificador_de_la_instancia))
    error_message = "Las alarmas de D-11 vigilan la instancia productiva <prefijo>-postgres."
  }
}
