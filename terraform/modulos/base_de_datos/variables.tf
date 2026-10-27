variable "nombre" {
  type        = string
  description = "Identificador de la instancia, p. ej. `blog-prod-postgres`. Prefija el resto de nombres."
}

variable "ids_de_subredes" {
  type        = list(string)
  description = "Subredes privadas del DB subnet group. Dos, en dos AZ (D-22)."
}

variable "id_sg_rds" {
  type        = string
  description = "Grupo de seguridad de la base de datos, del modulo `red`."
}

variable "zona" {
  type        = string
  description = "Nombre de la AZ de la instancia. Single-AZ, fijada a la subred `a` (DH-4)."
}

variable "clase" {
  type        = string
  description = "Clase de instancia. D-22: `db.t4g.micro`."
}

variable "version_del_motor" {
  type        = string
  description = "Version exacta de PostgreSQL. D-22: `17.11`, la misma que local y el CI del backend."
}

variable "familia_del_parametro" {
  type        = string
  description = "Familia del parameter group, coherente con el major: `postgres17`."
}

variable "gib" {
  type        = number
  description = "Almacenamiento gp3 inicial, en GiB. D-22: 20."
}

variable "gib_maximos" {
  type        = number
  description = "Techo del autoscaling de almacenamiento, en GiB. D-22: 50."
}

variable "dias_de_retencion" {
  type        = number
  description = "Retencion de backups automaticos y ventana de PITR. D-10: 7. Nunca 0."
}

variable "ventana_de_backup" {
  type        = string
  description = "Ventana diaria de backup en UTC. D-22: `07:00-07:30`."
}

variable "ventana_de_mantenimiento" {
  type        = string
  description = "Ventana semanal de mantenimiento en UTC. D-22: `sun:08:00-sun:09:00`."
}

variable "arn_de_clave_kms" {
  type        = string
  default     = null
  description = "Clave de cifrado en reposo. `null` = clave administrada por AWS `aws/rds` (D-23)."
}

variable "nombre_de_base" {
  type        = string
  description = "Base de datos inicial. La misma que en local: `personal_blog`."
}

variable "usuario_master" {
  type        = string
  description = "Usuario master. D-23: `blogadmin`, solo para recuperacion."
}

variable "contrasena_master" {
  type        = string
  sensitive   = true
  ephemeral   = true
  description = <<-DESC
    Contrasena master. **Efimera**: solo alimenta atributos write-only
    (`password_wo` y `value_wo`), asi que no llega ni al plan ni al state (DH-2).
  DESC
}

variable "version_de_la_contrasena" {
  type        = number
  description = "Se incrementa para rotar la contrasena master: es lo que dispara la escritura."
}

variable "ruta_del_parametro_master" {
  type        = string
  description = "Nombre del SecureString que custodia la contrasena master."
}

variable "proteccion_contra_borrado" {
  type        = bool
  description = "`deletion_protection`. En produccion, `true` (D-10); el root lo exige."
}

variable "omitir_snapshot_final" {
  type        = bool
  description = "`skip_final_snapshot`. En produccion, `false` (D-10); el root lo exige."
}

variable "dias_de_retencion_de_logs" {
  type        = number
  description = "Retencion del grupo de logs de PostgreSQL. Baseline de D-11: 14."
}
