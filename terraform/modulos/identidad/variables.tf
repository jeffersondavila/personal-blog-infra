variable "nombre_del_rol" {
  type        = string
  description = "Nombre del rol de ejecucion."
}

variable "arn_del_bucket" {
  type        = string
  description = "ARN del bucket de medios, para acotar los permisos de objeto."
}

variable "prefijo_de_medios" {
  type        = string
  description = "Prefijo real de las claves de medios que genera el backend."
}

variable "prefijo_de_sonda" {
  type        = string
  description = "Prefijo que consulta la sonda de disponibilidad de /ready."
}

variable "arn_del_grupo_de_logs" {
  type        = string
  description = "ARN del grupo de logs de la funcion."
}

variable "arns_de_parametros" {
  type        = list(string)
  default     = []
  description = "ARN de los parametros SSM concretos que la funcion podria leer."
}
