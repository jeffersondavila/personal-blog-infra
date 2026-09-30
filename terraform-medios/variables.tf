variable "region" {
  type        = string
  description = "Region del bucket de medios. En produccion, us-east-2 (Task/029)."

  validation {
    condition     = can(regex("^(us|eu|ap|sa|ca|me|af|il|mx)-(east|west|north|south|central|northeast|southeast)-[1-9]$", var.region))
    error_message = "Se exige una region comercial explicita de AWS."
  }
}

variable "laboratorio" {
  type        = bool
  description = <<-DESC
    `true` solo para el laboratorio local. Activa las banderas `skip_*` y el
    direccionamiento por ruta que el emulador necesita. En AWS real es `false` y
    el provider se comporta como de costumbre.
  DESC
}

variable "cuentas_permitidas" {
  type        = list(string)
  default     = []
  description = <<-DESC
    Cuentas en las que este root acepta operar. Lista vacia = sin restriccion,
    que es lo unico viable en el laboratorio, donde la cuenta es ficticia y el
    emulador no implementa la validacion. Contra AWS real se declara la cuenta
    verificada: es una guarda fail-closed contra aplicar en el destino equivocado.
  DESC
}

variable "endpoints_aws" {
  type = object({
    s3  = optional(string)
    sts = optional(string)
  })
  default     = {}
  description = <<-DESC
    Endpoints alternativos del emulador. Con los atributos sin declarar el
    provider resuelve los de AWS, exactamente igual que si el bloque no
    existiera: el destino es un valor, no una bifurcacion del codigo (R-26).
  DESC
}

variable "etiquetas" {
  type        = map(string)
  default     = {}
  description = "Etiquetas aplicadas por `default_tags` a todo recurso taggable."
}

variable "nombre_del_bucket" {
  type        = string
  description = "Nombre del bucket de medios. Global en AWS."

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.nombre_del_bucket))
    error_message = "El nombre del bucket debe cumplir las reglas de S3: 3 a 63 caracteres, minusculas."
  }
}

variable "origenes_cors" {
  type        = list(string)
  default     = []
  description = <<-DESC
    Origenes autorizados a leer medios desde el navegador. **Nunca el comodin.**

    D-08, resuelta para el MVP el 2026-09-28, fija la lista **vacia**: el consumo
    real es `<img src>` y S3 solo interviene en CORS ante peticiones cross-origin
    de JavaScript. Con la lista vacia el modulo no crea el recurso, que es lo
    correcto y no una omision.

    Disparador de reconsideracion: que el frontend pase a leer pixeles con
    `fetch`, `XMLHttpRequest`, `canvas` o un `<img crossorigin>`.
  DESC

  validation {
    condition     = !contains(var.origenes_cors, "*")
    error_message = "El comodin no se admite como origen CORS."
  }
}

variable "dias_para_expirar_versiones" {
  type        = number
  default     = 30
  description = "Dias tras los que una version no actual se elimina. D-08 MVP: 30."

  validation {
    condition     = var.dias_para_expirar_versiones >= 1
    error_message = "La expiracion debe ser de al menos un dia."
  }
}

variable "forzar_destruccion" {
  type        = bool
  default     = false
  description = <<-DESC
    Permite destruir el bucket con objetos dentro. Imprescindible en el
    laboratorio, que se reconstruye en cada ciclo. **En produccion es `false`**
    (D-08 MVP): el destino lo declara y no se hereda sin darse cuenta.
  DESC
}
