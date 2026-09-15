variable "nombre" {
  type        = string
  description = "Nombre de la HTTP API."
}

variable "nombre_de_la_funcion" {
  type        = string
  description = "Nombre de la funcion a invocar."
}

variable "arn_de_invocacion_de_la_funcion" {
  type        = string
  description = "invoke_arn de la funcion, que es lo que exige AWS_PROXY."
}

variable "nombre_del_stage" {
  type        = string
  description = "Stage de la API. Valor de laboratorio; produccion es de Task/033."
}

variable "timeout_ms" {
  type        = number
  default     = 30000
  description = <<-DESC
    Timeout de la integracion. El maximo de una HTTP API son 30 s, que es tambien
    el timeout de laboratorio de la funcion: si la funcion agota su tiempo, la
    API responde 504 en lugar de esperar indefinidamente.
  DESC

  validation {
    condition     = var.timeout_ms >= 50 && var.timeout_ms <= 30000
    error_message = "El timeout de integracion de una HTTP API va de 50 a 30000 ms."
  }
}
