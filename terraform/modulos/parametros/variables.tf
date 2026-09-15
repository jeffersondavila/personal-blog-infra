variable "prefijo_de_ruta" {
  type        = string
  description = "Prefijo de la ruta jerarquica de los parametros."
}

variable "parametros" {
  type = map(object({
    valor  = string
    seguro = optional(bool, false)
  }))
  default     = {}
  description = "Parametros a provisionar. Solo valores ficticios en el laboratorio."
}
