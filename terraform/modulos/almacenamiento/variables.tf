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

variable "etiquetas" {
  type        = map(string)
  default     = {}
  description = <<-DESC
    Etiquetas del bucket. Anadida en la enmienda de Task/030.

    Por que explicitas y no solo `default_tags` del provider: `default_tags` sigue
    activo y alcanza a todo recurso taggable del root, pero **un provider
    simulado no lo propaga**, de modo que las etiquetas no serian demostrables en
    una prueba offline. Pasarlas por variable las vuelve un valor conocido en
    tiempo de plan y por tanto comprobable. El valor por omision es `{}`, asi que
    el grafo de aplicacion no cambia de comportamiento: sigue etiquetando por
    `default_tags`.

    Solo el bucket las recibe: los recursos de configuracion de S3 —versionado,
    cifrado, BPA, ownership, policy, lifecycle y CORS— no son taggables.
  DESC
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
