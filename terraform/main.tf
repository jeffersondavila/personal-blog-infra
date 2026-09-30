# ---------------------------------------------------------------------------
# personal-blog-infra — Terraform: grafo de recursos (Task/025)
#
# UN SOLO GRAFO. Este archivo es identico para el laboratorio local y para AWS
# real: no hay `count` por entorno, ni modulos alternativos, ni recursos que solo
# existan en un destino. Lo unico que cambia entre destinos es el archivo .tfvars
# y la configuracion del provider.
#
# Esa es la regla de portabilidad de docs/architecture/aws-local-parity.md
# seccion 4, y el riesgo R-26 es precisamente lo contrario: acumular
# condicionales hasta acabar con dos infraestructuras disfrazadas de una.
#
# Orden de dependencias
#
#   registro ───┐
#               ├─> identidad ─> computo ─> api_http
#   parametros ─┘
#
#   El rol necesita el ARN del grupo de logs y de los parametros para acotar sus
#   permisos, mas el ARN del bucket de medios que este root RECIBE como entrada;
#   la funcion necesita el rol; la API necesita la funcion. Terraform deduce el
#   orden de estas referencias: no hace falta ningun `depends_on` a nivel de
#   modulo.
#
# ENMIENDA DE Task/030 (`H-030-4-root-medios`)
#   El bucket de medios YA NO SE DECLARA AQUI. Es almacenamiento persistente: su
#   lifecycle no es el de la funcion, la API y los parametros, que se recrean en
#   cada despliegue, y compartir state con ellos acoplaba dos ciclos de vida
#   ajenos. Vive ahora en el root propio `../terraform-medios`, que reutiliza
#   EL MISMO modulo `./modulos/almacenamiento`.
#
#   Este root lo consume por CONTRATO EXPLICITO: dos variables de entrada,
#   `nombre_del_bucket_de_medios` y `arn_del_bucket_de_medios`. Deliberadamente
#   no se usa `terraform_remote_state`: acoplaria este root a la ubicacion y al
#   formato del state del otro y le exigiria permiso de lectura sobre el, cuando
#   dos variables resuelven la dependencia sin ninguna de esas dos cosas.
#
#   Invariante que esto protege: NINGUN recurso queda administrado por dos states.
#   El bucket tiene exactamente un propietario, y es `terraform-medios`.
# ---------------------------------------------------------------------------

module "parametros" {
  source = "./modulos/parametros"

  prefijo_de_ruta = "/${var.prefijo}"
  parametros      = var.parametros
}

module "registro" {
  source = "./modulos/registro"

  nombre_de_la_funcion = local.nombre_de_la_funcion
  dias_de_retencion    = var.dias_de_retencion_de_logs
}

module "identidad" {
  source = "./modulos/identidad"

  nombre_del_rol = "${var.prefijo}-lambda"

  # ARN recibido, no administrado: este root no crea ni modifica el bucket.
  arn_del_bucket        = var.arn_del_bucket_de_medios
  prefijo_de_medios     = var.prefijo_de_medios
  prefijo_de_sonda      = var.prefijo_de_sonda
  arn_del_grupo_de_logs = module.registro.arn
  arns_de_parametros    = module.parametros.arns
}

module "computo" {
  source = "./modulos/computo"

  nombre       = local.nombre_de_la_funcion
  arn_del_rol  = module.identidad.arn
  handler      = var.lambda_handler
  runtime      = var.lambda_runtime
  arquitectura = var.lambda_arquitectura
  memoria_mb   = var.lambda_memoria_mb
  timeout_s    = var.lambda_timeout_s

  lambda_zip_path = var.lambda_zip_path

  variables_de_la_aplicacion = var.variables_de_la_aplicacion
  variables_del_sdk          = var.variables_del_sdk

  dependencia_del_grupo_de_logs = module.registro.arn
}

module "api_http" {
  source = "./modulos/api_http"

  nombre                          = "${var.prefijo}-api"
  nombre_de_la_funcion            = module.computo.nombre
  arn_de_invocacion_de_la_funcion = module.computo.arn_de_invocacion
  nombre_del_stage                = var.nombre_del_stage

  # La integracion no puede esperar mas que la propia funcion: si lo hiciera, la
  # API seguiria esperando una respuesta que ya nunca llegara.
  timeout_ms = var.lambda_timeout_s * 1000
}

locals {
  nombre_de_la_funcion = "${var.prefijo}-backend"
}
