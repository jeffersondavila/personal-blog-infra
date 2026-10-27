variable "nombre_del_rol" {
  type        = string
  description = "Rol PROPIO de la integracion de Grafana (D-20), p. ej. `PersonalBlogLecturaGrafana`."

  validation {
    condition     = can(regex("^PersonalBlog[A-Za-z]{4,40}$", var.nombre_del_rol))
    error_message = "El rol sigue el esquema PersonalBlog<Nombre>."
  }
}

variable "cuenta" {
  type        = string
  description = "Cuenta del proyecto (la verificada por la guarda de identidad del root). Construye el ARN de las alarmas."

  validation {
    condition     = can(regex("^[0-9]{12}$", var.cuenta))
    error_message = "Se espera un Account ID de 12 digitos."
  }
}

variable "region" {
  type        = string
  description = <<-DESC
    Region del destino: la politica no concede lectura en ninguna otra. us-east-2 en AWS real (H-1), que exige la
    guarda del plan productivo; el laboratorio usa la region del emulador con el MISMO modulo.
  DESC

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]$", var.region))
    error_message = "Se espera una region de AWS (p. ej. us-east-2)."
  }
}

variable "prefijo" {
  type        = string
  description = "Prefijo de las alarmas que Grafana puede leer (`<prefijo>-*`)."

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}[a-z0-9]$", var.prefijo))
    error_message = "El prefijo debe ser corto, en minusculas y sin caracteres especiales."
  }
}

variable "cuenta_de_grafana" {
  type        = string
  description = "Cuenta AWS de Grafana Cloud que asume el rol, tal como la muestra el stack. Nunca la del proyecto."

  validation {
    condition     = can(regex("^[0-9]{12}$", var.cuenta_de_grafana)) && var.cuenta_de_grafana != var.cuenta
    error_message = "Se espera la cuenta de Grafana (12 digitos), distinta de la del proyecto."
  }
}

variable "external_id" {
  type        = string
  description = "ExternalId del stack de Grafana Cloud: proteccion contra el confused deputy. No es un secreto."

  # RE2 (el motor de `regex`) no admite repeticiones de mas de 1000: el rango de STS (2 a 1224) va con `length`.
  validation {
    condition     = can(regex("^[A-Za-z0-9+=,.@:/-]+$", var.external_id)) && length(var.external_id) >= 2 && length(var.external_id) <= 1224
    error_message = "ExternalId con el formato que admite STS."
  }
}
