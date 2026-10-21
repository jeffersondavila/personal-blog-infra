# ---------------------------------------------------------------------------
# Root de datos — llamadas a modulos compartidos y una guarda de identidad.
#
# `source` apunta a los modulos del arbol de aplicacion: no se copian ni se
# reimplementan. Local y AWS real usan ESTE mismo root con los mismos modulos;
# solo cambia el archivo de destino (aws-local-parity.md §4.1.1).
#
# Contrato con los otros roots, solo por variables y salidas:
#   - recibe `arn_del_bucket_de_medios` de `terraform-medios`;
#   - publica subredes, grupos y endpoint para la Lambda de aplicacion
#     (Task/032), que los recibira como variables; la ejecutora (H-031-5) y
#     `export` (H-031-6) los consumen dentro de este mismo root.
# Nunca `terraform_remote_state`. Orden: medios -> datos -> aplicacion al crear;
# el inverso al destruir.
# ---------------------------------------------------------------------------

locals {
  nombre_de_la_base   = "${var.prefijo}-postgres"
  ruta_de_la_master   = "/${var.prefijo}/datos/blogadmin"
  ruta_de_datos       = "/${var.prefijo}/datos"
  servicio_s3         = "com.amazonaws.${var.region}.s3"
  identidad_operativa = "assumed-role/${var.rol_operativo}/"
}

# Guarda fail-closed de identidad. Contra AWS real, la sesion debe ser
# EXACTAMENTE `assumed-role/PersonalBlogAdministrator/...` en la cuenta
# verificada, por decision operacional del usuario (Task/031 §24); cualquier otra
# —incluido `PersonalBlogDataOperator`— detiene el plan antes de proponer un solo
# recurso. El prefijo termina en `/`, asi que un rol de nombre parecido tampoco
# pasa. En el laboratorio la identidad es ficticia y la guarda equivalente es la
# del lanzador.
data "aws_caller_identity" "operador" {
  lifecycle {
    postcondition {
      condition = var.laboratorio || (
        contains(var.cuentas_permitidas, self.account_id) &&
        startswith(self.arn, "arn:aws:sts::${self.account_id}:${local.identidad_operativa}")
      )
      error_message = "STOP: el root de datos solo se opera con la sesion del rol operativo minimo, en la cuenta verificada."
    }
  }
}

module "red" {
  source = "../terraform/modulos/red"

  nombre                     = var.prefijo
  cidr                       = var.cidr_de_la_vpc
  subredes                   = var.subredes
  nombre_del_servicio_s3     = local.servicio_s3
  arns_de_buckets_permitidos = [var.arn_del_bucket_de_medios]
}

module "base_de_datos" {
  source = "../terraform/modulos/base_de_datos"

  nombre          = local.nombre_de_la_base
  ids_de_subredes = module.red.ids_de_subredes
  id_sg_rds       = module.red.id_sg_rds
  zona            = module.red.zonas_de_subredes["a"]

  clase                    = var.clase_de_la_instancia
  version_del_motor        = var.version_del_motor
  familia_del_parametro    = "postgres${split(".", var.version_del_motor)[0]}"
  gib                      = var.gib
  gib_maximos              = var.gib_maximos
  dias_de_retencion        = var.dias_de_retencion_de_backups
  ventana_de_backup        = var.ventana_de_backup
  ventana_de_mantenimiento = var.ventana_de_mantenimiento

  nombre_de_base            = "personal_blog"
  usuario_master            = "blogadmin"
  contrasena_master         = var.contrasena_master
  version_de_la_contrasena  = var.version_de_la_contrasena
  ruta_del_parametro_master = local.ruta_de_la_master

  proteccion_contra_borrado = var.proteccion_contra_borrado
  omitir_snapshot_final     = var.omitir_snapshot_final
  dias_de_retencion_de_logs = var.dias_de_retencion_de_logs
}

# Ejecutora privada de D-24 (Task/031 H-031-5): solo `sg-admin`, en las dos subredes privadas de `module.red`, con
# su rol de ejecucion propio y el artefacto fijado por `empaquetar_ejecutor.py`. Salio del root el 2026-10-08 mientras
# la cuota de Lambda no permitia RC=1; VUELVE el 2026-10-18 con D-24 modificada (aprobada el
# 2026-10-19): concurrencia NO reservada, y la exclusion entre escrituras la hace su advisory lock de PostgreSQL
# (reporte de Task/031 §49).
module "ejecutor_privado" {
  source = "../terraform/modulos/ejecutor_privado"

  nombre                    = "${var.prefijo}-ejecutor"
  nombre_del_rol            = "PersonalBlogEjecutorDatos"
  region                    = var.region
  cuenta                    = data.aws_caller_identity.operador.account_id
  ids_de_subredes           = module.red.ids_de_subredes
  id_sg_admin               = module.red.id_sg_admin
  ruta_del_zip              = var.zip_de_la_ejecutora.ruta
  sha256_del_zip            = var.zip_de_la_ejecutora.sha256
  dias_de_retencion_de_logs = var.dias_de_retencion_de_logs
}

# H-031-6: custodia write-only independiente; los valores solo llegan por variables efimeras.
module "credenciales_sql" {
  source = "../terraform/modulos/credenciales_sql"

  nombre                  = var.prefijo
  ruta_base               = local.ruta_de_datos
  contrasena_blog_migrate = var.contrasena_blog_migrate
  contrasena_blog_app     = var.contrasena_blog_app
  version_de_blog_migrate = var.version_de_blog_migrate
  version_de_blog_app     = var.version_de_blog_app
}

module "exportacion" {
  source = "../terraform/modulos/exportacion"

  nombre             = var.prefijo
  nombre_del_rol     = module.ejecutor_privado.nombre_del_rol
  arn_del_bucket     = var.arn_del_bucket_de_medios
  id_sg_admin        = module.red.id_sg_admin
  prefix_list_s3     = module.red.prefix_list_s3
  id_del_endpoint_s3 = module.red.id_endpoint_s3
}

# Alarmas de D-11 (Task/031 H-031-8): ocho, sin acciones ni destinatarios, sobre la instancia de ESTE root.
module "alarmas_rds" {
  source = "../terraform/modulos/alarmas_rds"

  nombre                        = var.prefijo
  identificador_de_la_instancia = module.base_de_datos.identificador
}

# D-20 (Task/031 H-031-9): rol de SOLO LECTURA que Grafana Cloud asume con el ExternalId de su stack ("Grafana Assume
# Role"). Metricas y estados de las alarmas del proyecto; sin logs ni escritura.
module "lectura_grafana" {
  source = "../terraform/modulos/lectura_grafana"

  nombre_del_rol    = "PersonalBlogLecturaGrafana"
  cuenta            = data.aws_caller_identity.operador.account_id
  region            = var.region
  prefijo           = var.prefijo
  cuenta_de_grafana = var.integracion_grafana.cuenta
  external_id       = var.integracion_grafana.external_id
}
