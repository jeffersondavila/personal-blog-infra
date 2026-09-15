variable "nombre_de_la_funcion" {
  type        = string
  description = "Nombre de la funcion Lambda cuyo grupo de logs se crea."
}

variable "dias_de_retencion" {
  type        = number
  description = "Retencion en dias. Nunca infinita."
}
