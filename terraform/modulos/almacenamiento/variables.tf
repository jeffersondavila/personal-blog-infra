variable "nombre" {
  type        = string
  description = "Nombre del bucket de medios."
}

variable "origenes_cors" {
  type        = list(string)
  default     = []
  description = "Origenes autorizados a leer medios desde el navegador. Nunca el comodin."
}

variable "dias_para_expirar_versiones" {
  type        = number
  description = "Dias tras los que una version no actual se elimina."
}

variable "forzar_destruccion" {
  type        = bool
  default     = false
  description = <<-DESC
    Permite destruir el bucket con objetos dentro. Es imprescindible en el
    laboratorio, que se reconstruye en cada ciclo. El destino lo declara: no es
    un valor que se herede sin darse cuenta.
  DESC
}
