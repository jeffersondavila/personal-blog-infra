variable "nombre" {
  type        = string
  description = "Prefijo de los nombres de la red, p. ej. `blog-prod`. Va en la etiqueta Name."
}

variable "cidr" {
  type        = string
  description = "CIDR de la VPC dedicada. D-22: `10.40.0.0/16`."
}

variable "subredes" {
  type = map(object({
    cidr    = string
    zona_id = string
  }))
  description = <<-DESC
    Subredes PRIVADAS, por clave estable (`a`, `b`). La zona se fija por **ID**
    (`use2-az1`), no por nombre: el nombre de una AZ cambia de una cuenta a otra
    y el ID no. D-22 exige dos, en dos AZ distintas, porque el DB subnet group
    las necesita incluso para una instancia Single-AZ.
  DESC
}

variable "nombre_del_servicio_s3" {
  type        = string
  description = "Nombre del servicio del gateway endpoint, `com.amazonaws.<region>.s3`."
}

variable "arns_de_buckets_permitidos" {
  type        = list(string)
  description = <<-DESC
    Buckets alcanzables a traves del gateway endpoint. Hoy, solo el de medios:
    lo usa la aplicacion (Task/032) y el modo `export` de la ejecutora (D-24,
    prefijo dedicado dentro del mismo bucket). Cualquier otro bucket queda fuera
    del endpoint, que es la defensa contra exfiltracion desde la VPC.
  DESC
}

variable "puerto_de_la_base" {
  type        = number
  default     = 5432
  description = "Puerto SQL que abren las reglas entre grupos."
}
