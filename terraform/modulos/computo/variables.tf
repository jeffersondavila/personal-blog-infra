variable "nombre" {
  type        = string
  description = "Nombre de la funcion."
}

variable "arn_del_rol" {
  type        = string
  description = "ARN del rol de ejecucion."
}

variable "lambda_zip_path" {
  type        = string
  description = "Ruta explicita al artefacto ZIP de Task/024."
}

variable "handler" {
  type        = string
  description = "Punto de entrada, fijado por Task/023."
}

variable "runtime" {
  type        = string
  description = "Runtime, fijado por Task/024."
}

variable "arquitectura" {
  type        = string
  description = "Arquitectura de ejecucion."
}

variable "memoria_mb" {
  type        = number
  description = "Memoria. Valor de laboratorio; D-12 sigue abierta."
}

variable "timeout_s" {
  type        = number
  description = "Timeout. Valor de laboratorio; D-12 sigue abierta."
}

variable "variables_de_la_aplicacion" {
  type        = map(string)
  default     = {}
  description = "Variables BLOG_* que lee la aplicacion."
}

variable "variables_del_sdk" {
  type        = map(string)
  default     = {}
  description = "Variables que el SDK necesita dentro del contenedor."
}

variable "dependencia_del_grupo_de_logs" {
  type        = any
  description = <<-DESC
    Referencia al grupo de logs, usada solo para ordenar la creacion. Se pasa
    como valor y no como `depends_on` del modulo para que la dependencia quede
    explicita en el grafo sin acoplar los modulos entre si.
  DESC
}
