# --- Destino ----------------------------------------------------------------

variable "region" {
  type        = string
  description = "Region de la red y de la base de datos. En produccion, us-east-2 (Task/029, H-1)."

  validation {
    condition     = can(regex("^(us|eu|ap|sa|ca|me|af|il|mx)-(east|west|north|south|central|northeast|southeast)-[1-9]$", var.region))
    error_message = "Se exige una region comercial explicita de AWS."
  }
}

variable "laboratorio" {
  type        = bool
  description = <<-DESC
    `true` solo para el laboratorio local: activa las banderas `skip_*` que el
    emulador necesita y relaja las guardas de identidad, cuyo destino es ficticio.
    En AWS real es `false` y todas las guardas de produccion se aplican.
  DESC
}

variable "cuentas_permitidas" {
  type        = list(string)
  default     = []
  description = <<-DESC
    Cuentas en las que este root acepta operar. Vacia solo en el laboratorio.
    Contra AWS real es exactamente la cuenta verificada: guarda fail-closed.
  DESC

  validation {
    condition     = var.laboratorio || length(var.cuentas_permitidas) == 1
    error_message = "Fuera del laboratorio se exige exactamente una cuenta verificada."
  }
}

variable "rol_operativo" {
  type        = string
  default     = "PersonalBlogAdministrator"
  description = <<-DESC
    Rol cuya sesion debe operar este root en AWS real. UNA identidad exacta:
    `PersonalBlogAdministrator`, por decision operacional del usuario (Task/031
    §24, H-031-2-ALIGN). El operador `PersonalBlogDataOperator` creado en
    H-031-IAM se conserva, pero aqui se RECHAZA. Se mantiene como variable para
    que el plan muestre la identidad exigida y la guarda la compruebe.
  DESC

  validation {
    condition     = var.rol_operativo == "PersonalBlogAdministrator"
    error_message = "El root de datos solo se opera con PersonalBlogAdministrator (decision de Task/031 §24)."
  }
}

variable "endpoints_aws" {
  type = object({
    ec2        = optional(string)
    rds        = optional(string)
    ssm        = optional(string)
    logs       = optional(string)
    sts        = optional(string)
    iam        = optional(string)
    lambda     = optional(string)
    cloudwatch = optional(string)
  })
  default     = {}
  description = <<-DESC
    Endpoints alternativos del emulador. Sin declarar, el provider resuelve los
    de AWS igual que si el bloque no existiera: el destino es un valor, no una
    bifurcacion del codigo (R-26).
  DESC
}

variable "etiquetas" {
  type        = map(string)
  default     = {}
  description = "Etiquetas aplicadas por `default_tags` a todo recurso taggable."
}

variable "prefijo" {
  type        = string
  description = "Prefijo de los nombres: `blog-prod` en AWS real, `blog-lab` en el laboratorio."

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}[a-z0-9]$", var.prefijo))
    error_message = "El prefijo debe ser corto, en minusculas y sin caracteres especiales."
  }
}

# --- Red (D-22) -------------------------------------------------------------

variable "cidr_de_la_vpc" {
  type        = string
  default     = "10.40.0.0/16"
  description = "CIDR de la VPC dedicada. D-22: no solapa con Docker local ni con rangos de ejemplo."

  validation {
    condition     = can(cidrhost(var.cidr_de_la_vpc, 0)) && endswith(var.cidr_de_la_vpc, "/16")
    error_message = "La VPC debe declararse con un CIDR /16 valido."
  }
}

variable "subredes" {
  type = map(object({
    cidr    = string
    zona_id = string
  }))
  default = {
    a = { cidr = "10.40.0.0/20", zona_id = "use2-az1" }
    b = { cidr = "10.40.16.0/20", zona_id = "use2-az2" }
  }
  description = "Dos subredes privadas, `a` y `b`, en dos AZ distintas, fijadas por ID."

  validation {
    condition     = toset(keys(var.subredes)) == toset(["a", "b"])
    error_message = "Se exigen exactamente las subredes `a` y `b`: el DB subnet group necesita dos AZ."
  }

  validation {
    condition = (
      length(distinct([for s in values(var.subredes) : s.zona_id])) == length(var.subredes) &&
      length(distinct([for s in values(var.subredes) : s.cidr])) == length(var.subredes)
    )
    error_message = "Las dos subredes deben estar en AZ distintas y no compartir CIDR."
  }

  validation {
    # Dos formatos de ID: el de AWS (`use2-az1`) y el que publicaba el emulador
    # hasta Floci 2.1.0 (`us-east-1-az1`), un VALOR del destino local y no un
    # diseno distinto (hallazgo de H-031-1, matriz de paridad); desde 2.3.0 el
    # emulador publica el de AWS. Un nombre de AZ como `us-east-2a` sigue
    # rechazado: depende de la cuenta.
    condition     = alltrue([for s in values(var.subredes) : can(cidrhost(s.cidr, 0)) && can(regex("^([a-z]{3,5}[0-9]|[a-z]{2}-[a-z]+-[0-9])-az[0-9]+$", s.zona_id))])
    error_message = "Cada subred necesita un CIDR valido y un ID de AZ (p. ej. use2-az1), no un nombre."
  }
}

variable "arn_del_bucket_de_medios" {
  type        = string
  description = <<-DESC
    ARN del bucket que administra `terraform-medios`. Contrato explicito: este
    root no lo administra, solo limita a el la politica del gateway endpoint. Lo
    usan la aplicacion (Task/032) y el modo `export` de D-24 (prefijo propio).
  DESC

  validation {
    condition     = can(regex("^arn:aws:s3:::[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.arn_del_bucket_de_medios))
    error_message = "Se espera el ARN de un bucket, sin comodines ni rutas de objeto."
  }
}

# --- Base de datos (D-22, D-23, D-10) ---------------------------------------

variable "clase_de_la_instancia" {
  type        = string
  default     = "db.t4g.micro"
  description = "Clase de RDS. Cambiarla exige una decision registrada: duplica el costo fijo."

  validation {
    condition     = var.clase_de_la_instancia == "db.t4g.micro"
    error_message = "D-22 fija db.t4g.micro. Otra clase requiere una decision explicita del usuario."
  }
}

variable "version_del_motor" {
  type        = string
  default     = "17.11"
  description = "Version exacta de PostgreSQL. La de produccion sigue a la de local, no al reves (D-22 §3.2)."

  validation {
    condition     = can(regex("^17\\.[0-9]+$", var.version_del_motor))
    error_message = "Se exige una version menor exacta del major 17."
  }
}

variable "gib" {
  type        = number
  default     = 20
  description = "Almacenamiento gp3 inicial. D-22: 20 GiB, el minimo de gp3."

  validation {
    condition     = var.gib >= 20 && var.gib <= 50
    error_message = "El almacenamiento inicial debe estar entre 20 y 50 GiB."
  }
}

variable "gib_maximos" {
  type        = number
  default     = 50
  description = "Techo del autoscaling. D-22: 50 GiB, decision de presupuesto."

  validation {
    condition     = var.gib_maximos >= var.gib && var.gib_maximos <= 50
    error_message = "El techo debe ser al menos el inicial y no superar 50 GiB sin una decision explicita."
  }
}

variable "dias_de_retencion_de_backups" {
  type        = number
  default     = 7
  description = <<-DESC
    Retencion de backups automaticos y ventana de PITR. OBJETIVO de D-10/D-22: 7 dias
    (el default), con la cuenta en plan PAID. EXCEPCION TEMPORAL: 1 dia mientras la
    cuenta siga en plan FREE, que rechazo 7 con FreeTierRestrictionError (Task/031
    §32-§34); el entorno productivo la fija de forma explicita. Al pasar a PAID se
    restaura 7. El maximo del plan FREE no esta publicado y no se descubre por tanteo.
    Nunca 0: desactivaria los backups automaticos y el PITR.
  DESC

  validation {
    condition     = contains([1, 7], var.dias_de_retencion_de_backups)
    error_message = "Solo 7 (objetivo, plan PAID) o 1 (excepcion temporal del plan FREE). Nunca 0 ni otro valor."
  }
}

variable "ventana_de_backup" {
  type        = string
  default     = "07:00-07:30"
  description = "Ventana diaria de backup, UTC (D-22 §3.8)."

  validation {
    condition     = can(regex("^[0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]$", var.ventana_de_backup))
    error_message = "Formato hh24:mi-hh24:mi en UTC."
  }
}

variable "ventana_de_mantenimiento" {
  type        = string
  default     = "sun:08:00-sun:09:00"
  description = "Ventana semanal de mantenimiento, UTC, sin solapar el backup (D-22 §3.8)."

  validation {
    condition     = can(regex("^(mon|tue|wed|thu|fri|sat|sun):[0-2][0-9]:[0-5][0-9]-(mon|tue|wed|thu|fri|sat|sun):[0-2][0-9]:[0-5][0-9]$", var.ventana_de_mantenimiento))
    error_message = "Formato ddd:hh24:mi-ddd:hh24:mi en UTC."
  }
}

variable "dias_de_retencion_de_logs" {
  type        = number
  default     = 14
  description = "Retencion de los grupos de logs del root: PostgreSQL y la ejecutora de D-24. Baseline de D-11 (H-031-1)."

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30], var.dias_de_retencion_de_logs)
    error_message = "Retencion corta y explicita: 1, 3, 5, 7, 14 o 30 dias. Nunca infinita."
  }
}

variable "contrasena_master" {
  type        = string
  sensitive   = true
  ephemeral   = true
  description = <<-DESC
    Contrasena master de `blogadmin`. EFIMERA: no se guarda en el plan ni en el
    state y debe aportarse otra vez al aplicar un plan guardado. Nunca toca el
    disco: se genera en memoria dentro del proceso que ejecuta Terraform y se le
    pasa solo por entorno. Su UNICA custodia es el SecureString que este root
    escribe con `value_wo` (DH-2, D-23). Procedimiento: Task/031 §25.
  DESC

  validation {
    condition     = can(regex("^[A-Za-z0-9]{32,64}$", var.contrasena_master))
    error_message = "La contrasena master debe tener entre 32 y 64 caracteres alfanumericos."
  }
}

variable "version_de_la_contrasena" {
  type        = number
  default     = 1
  description = "Incrementarla rota la contrasena master: es lo que dispara la escritura write-only."

  validation {
    condition     = var.version_de_la_contrasena >= 1 && floor(var.version_de_la_contrasena) == var.version_de_la_contrasena
    error_message = "La version de la contrasena es un entero positivo."
  }
}

# --- Ejecutora privada de D-24 (H-031-5) -------------------------------------

variable "zip_de_la_ejecutora" {
  type = object({
    ruta   = string
    sha256 = string
  })
  description = "Artefacto de la ejecutora de D-24 (H-031-5): ruta del ZIP y su SHA-256, el pin de empaquetar_ejecutor.py. La ruta vive en el archivo de variables del destino."
}

# --- Integracion CloudWatch -> Grafana Cloud de D-20 (H-031-9) ----------------

variable "integracion_grafana" {
  type = object({
    cuenta      = string
    external_id = string
  })
  description = <<-DESC
    D-20 (H-031-9): la cuenta AWS de Grafana Cloud que asume el rol y el ExternalId de su stack, tal como los muestra
    la configuracion del origen de datos CloudWatch ("Grafana Assume Role"). Ninguno es un secreto, pero son datos de
    la cuenta del usuario: van en el archivo de variables PRIVADO del destino, nunca en Git. El modulo los valida y
    rechaza la cuenta del propio proyecto.
  DESC
}

variable "proteccion_contra_borrado" {
  type        = bool
  description = "`deletion_protection`. Solo el laboratorio, que se reconstruye en cada ciclo, puede desactivarla."

  validation {
    condition     = var.laboratorio || var.proteccion_contra_borrado
    error_message = "Fuera del laboratorio la base de datos exige deletion protection (D-10, R-35)."
  }
}

variable "omitir_snapshot_final" {
  type        = bool
  description = "`skip_final_snapshot`. Solo el laboratorio puede omitir el snapshot final."

  validation {
    condition     = var.laboratorio || !var.omitir_snapshot_final
    error_message = "Fuera del laboratorio se exige snapshot final al borrar (D-10)."
  }
}

# H-031-6: valores efimeros y versiones de rotacion independientes.
variable "contrasena_blog_migrate" {
  type        = string
  sensitive   = true
  ephemeral   = true
  description = "Contrasena de `blog_migrate`. EFIMERA: ni plan ni state; se aporta en cada plan y al aplicarlo."

  validation {
    condition     = can(regex("^[A-Za-z0-9]{32,64}$", var.contrasena_blog_migrate))
    error_message = "La contrasena debe tener entre 32 y 64 caracteres alfanumericos."
  }
}

variable "contrasena_blog_app" {
  type        = string
  sensitive   = true
  ephemeral   = true
  description = "Contrasena de `blog_app`. EFIMERA: ni plan ni state; se aporta en cada plan y al aplicarlo."

  validation {
    condition     = can(regex("^[A-Za-z0-9]{32,64}$", var.contrasena_blog_app))
    error_message = "La contrasena debe tener entre 32 y 64 caracteres alfanumericos."
  }
}

variable "version_de_blog_migrate" {
  type        = number
  default     = 1
  description = "Incrementarla rota la contrasena de `blog_migrate`: es lo que dispara la escritura write-only."

  validation {
    condition     = var.version_de_blog_migrate >= 1 && floor(var.version_de_blog_migrate) == var.version_de_blog_migrate
    error_message = "La version es un entero positivo."
  }
}

variable "version_de_blog_app" {
  type        = number
  default     = 1
  description = "Incrementarla rota la contrasena de `blog_app`: es lo que dispara la escritura write-only."

  validation {
    condition     = var.version_de_blog_app >= 1 && floor(var.version_de_blog_app) == var.version_de_blog_app
    error_message = "La version es un entero positivo."
  }
}
