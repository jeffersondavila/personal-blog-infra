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
#   almacenamiento ─┐
#   registro ───────┼─> identidad ─> computo ─> api_http
#   parametros ─────┘
#
#   El rol necesita los ARN del bucket, del grupo de logs y de los parametros
#   para acotar sus permisos; la funcion necesita el rol; la API necesita la
#   funcion. Terraform deduce el orden de estas referencias: no hace falta
#   ningun `depends_on` a nivel de modulo.
# ---------------------------------------------------------------------------

module "almacenamiento" {
  source = "./modulos/almacenamiento"

  nombre                      = var.bucket_de_medios
  origenes_cors               = var.origenes_cors
  dias_para_expirar_versiones = var.dias_para_expirar_versiones

  # El laboratorio se destruye y se reconstruye en cada ciclo, y el bucket lleva
  # objetos de prueba. Contra AWS real este valor se declara en su propio tfvars.
  forzar_destruccion = var.laboratorio
}

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

  nombre_del_rol        = "${var.prefijo}-lambda"
  arn_del_bucket        = module.almacenamiento.arn
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
