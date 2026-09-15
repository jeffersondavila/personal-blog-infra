# ---------------------------------------------------------------------------
# personal-blog-infra — Terraform: variables de entrada (Task/025)
#
# Todo lo que distingue un destino de otro entra por aqui. `laboratorio` y
# `region` no tienen valor por omision a proposito: olvidarlos debe romper el
# plan, no producir un despliegue silencioso contra un destino cualquiera.
# ---------------------------------------------------------------------------

variable "region" {
  type        = string
  description = "Region AWS declarada al firmar y al construir ARN."

  validation {
    condition     = can(regex("^[a-z]{2}(-[a-z]+)+-[0-9]$", var.region))
    error_message = "La region debe tener la forma de una region AWS, por ejemplo us-east-1."
  }
}

variable "laboratorio" {
  type        = bool
  description = <<-DESC
    true cuando el destino es el laboratorio AWS local. Activa los flags del
    provider que el emulador necesita y NO cambia ningun recurso.
    Sin valor por omision: el destino se declara siempre.
  DESC
}

variable "endpoints_aws" {
  type = object({
    apigatewayv2 = optional(string)
    cloudwatch   = optional(string)
    iam          = optional(string)
    lambda       = optional(string)
    logs         = optional(string)
    s3           = optional(string)
    ssm          = optional(string)
    sts          = optional(string)
  })
  default     = {}
  description = <<-DESC
    Endpoints por servicio. Vacio contra AWS real: el provider resuelve los
    suyos. En el laboratorio los ocho apuntan al emulador, y el lanzador los
    valida antes de invocar a Terraform (guarda G-02).
  DESC
}

variable "prefijo" {
  type        = string
  description = "Prefijo de los nombres de recurso, para distinguir entornos."

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{1,30}[a-z0-9]$", var.prefijo))
    error_message = "El prefijo admite minusculas, digitos y guiones, entre 3 y 32 caracteres."
  }
}

variable "etiquetas" {
  type        = map(string)
  default     = {}
  description = "Etiquetas aplicadas por omision a todo recurso que las admita."
}

# --- S3: bucket de medios --------------------------------------------------

variable "bucket_de_medios" {
  type        = string
  description = <<-DESC
    Nombre del bucket de medios. Es el unico bucket que crea esta tarea: el
    paquete Lambda se carga directamente, asi que no hace falta un bucket de
    despliegue, y el de backups del VPS pertenece a Task/029 y Task/030.
  DESC

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.bucket_de_medios))
    error_message = "El nombre del bucket debe cumplir las reglas de S3: 3 a 63 caracteres, minusculas."
  }
}

variable "origenes_cors" {
  type        = list(string)
  default     = []
  description = <<-DESC
    Origenes autorizados a leer medios desde el navegador. Nunca el comodin: el
    backend ya lo rechaza para el panel (requisito S-04) y un bucket de medios no
    necesita ser legible desde cualquier origen.
  DESC

  validation {
    condition     = !contains(var.origenes_cors, "*")
    error_message = "El comodin no se admite como origen CORS."
  }
}

variable "dias_para_expirar_versiones" {
  type        = number
  default     = 30
  description = <<-DESC
    Dias tras los que una version no actual de un objeto se elimina. Valor de
    laboratorio: la politica definitiva de medios es de Task/030 (D-08).
  DESC

  validation {
    condition     = var.dias_para_expirar_versiones >= 1
    error_message = "La expiracion debe ser de al menos un dia."
  }
}

variable "prefijo_de_medios" {
  type        = string
  default     = "medios/"
  description = <<-DESC
    Prefijo real de las claves de medios, tal como lo genera el backend en
    app/modules/media/domain/claves.py. El permiso de objeto se acota a este
    prefijo, no al bucket entero.
  DESC
}

variable "prefijo_de_sonda" {
  type        = string
  default     = "_readiness/"
  description = <<-DESC
    Prefijo que usa la sonda de disponibilidad del backend
    (app/shared/storage/s3_compatible.py). Existe como variable porque el
    permiso s3:ListBucket se condiciona a el en lugar de concederse sobre todo
    el bucket.
  DESC
}

# --- Lambda ----------------------------------------------------------------

variable "lambda_zip_path" {
  type        = string
  description = <<-DESC
    Ruta al artefacto ZIP que construye
    personal-blog-backend/scripts/empaquetar_lambda.py (Task/024).
    Se recibe como RUTA EXPLICITA: este repositorio no versiona el artefacto, no
    lo copia y no supone que los repositorios sean carpetas hermanas.
  DESC
}

variable "lambda_handler" {
  type        = string
  default     = "app.lambda_handler.handler"
  description = "Handler fijado por Task/023."
}

variable "lambda_runtime" {
  type        = string
  default     = "python3.12"
  description = "Runtime fijado por Task/024."
}

variable "lambda_arquitectura" {
  type        = string
  default     = "x86_64"
  description = "Arquitectura fijada por Task/024. Ninguna decision autoriza arm64."

  validation {
    condition     = var.lambda_arquitectura == "x86_64"
    error_message = "El proyecto solo autoriza x86_64."
  }
}

variable "lambda_memoria_mb" {
  type        = number
  default     = 512
  description = <<-DESC
    Memoria de la funcion. VALOR DE LABORATORIO, no dimensionamiento: el arranque
    en frio local no es comparable con el de AWS. Los limites reales son D-12, en
    Task/032.
  DESC

  validation {
    condition     = var.lambda_memoria_mb >= 128 && var.lambda_memoria_mb <= 10240
    error_message = "La memoria de Lambda va de 128 a 10240 MB."
  }
}

variable "lambda_timeout_s" {
  type        = number
  default     = 30
  description = "Timeout de la funcion. Valor de laboratorio; D-12 sigue abierta."

  validation {
    condition     = var.lambda_timeout_s >= 1 && var.lambda_timeout_s <= 900
    error_message = "El timeout de Lambda va de 1 a 900 segundos."
  }
}

variable "variables_de_la_aplicacion" {
  type        = map(string)
  default     = {}
  description = <<-DESC
    Variables BLOG_* que recibe el proceso. Es el mecanismo que la aplicacion usa
    HOY (app/shared/configuration/settings.py, env_prefix BLOG_).
    La aplicacion NO lee SSM: esta tarea no inventa ese lector.
  DESC
}

variable "variables_del_sdk" {
  type        = map(string)
  default     = {}
  description = <<-DESC
    Variables que el SDK de AWS necesita dentro del contenedor de la funcion. En
    el laboratorio incluyen el endpoint del emulador visto DESDE la red de
    ejecucion, que no es el mismo anfitrion que ve el host. Vacio en AWS real,
    donde el SDK resuelve sus endpoints y el rol aporta las credenciales.
  DESC
}

# --- CloudWatch Logs -------------------------------------------------------

variable "dias_de_retencion_de_logs" {
  type        = number
  default     = 7
  description = <<-DESC
    Retencion del grupo de logs. Nunca infinita. Valor de laboratorio: la
    retencion exacta de produccion es D-11, en Task/031.
  DESC

  validation {
    condition = contains(
      [1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653],
      var.dias_de_retencion_de_logs
    )
    error_message = "CloudWatch Logs solo admite un conjunto cerrado de valores de retencion."
  }
}

# --- SSM -------------------------------------------------------------------

variable "parametros" {
  type = map(object({
    valor  = string
    seguro = optional(bool, false)
  }))
  default     = {}
  description = <<-DESC
    Parametros de configuracion a provisionar. Los nombres son PROPUESTOS, no
    nombres productivos aprobados.

    En el laboratorio el emulador conserva el tipo SecureString pero NO cifra en
    reposo (aws-local-parity.md 6.4), asi que aqui solo entran valores ficticios:
    ningun secreto real, sin excepcion (control S-07).
  DESC
}

# --- API Gateway -----------------------------------------------------------

variable "nombre_del_stage" {
  type        = string
  default     = "$default"
  description = <<-DESC
    Stage de la HTTP API. El stage por omision sirve la API sin prefijo de ruta,
    lo que simplifica la validacion local.

    SOLO LABORATORIO: la decision de stage y base path de PRODUCCION es de
    Task/033, y este valor no la anticipa.
  DESC
}
