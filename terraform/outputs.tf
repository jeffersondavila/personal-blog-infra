# ---------------------------------------------------------------------------
# personal-blog-infra — Terraform: salidas (Task/025)
#
# Las salidas no son decoracion: son el contrato que consume el verificador del
# laboratorio. Sin el endpoint no se puede ejercer el camino critico, y sin los
# nombres no se puede comprobar la AUSENCIA de cada recurso tras el destroy.
# ---------------------------------------------------------------------------

output "endpoint_del_api" {
  value       = module.api_http.endpoint
  description = "URL base de la HTTP API. Es donde se hace el GET /health real."
}

output "id_del_api" {
  value       = module.api_http.id
  description = "Identificador de la API."
}

output "nombre_del_stage" {
  value       = module.api_http.nombre_del_stage
  description = "Stage desplegado."
}

output "nombre_de_la_funcion" {
  value       = module.computo.nombre
  description = "Nombre de la funcion Lambda."
}

output "hash_del_codigo_desplegado" {
  value       = module.computo.hash_del_codigo
  description = "Hash del artefacto efectivamente desplegado, registrado como evidencia."
}

output "bucket_de_medios" {
  value       = module.almacenamiento.nombre
  description = "Nombre del bucket de medios."
}

output "grupo_de_logs" {
  value       = module.registro.nombre
  description = "Grupo de logs de la funcion."
}

output "rol_de_ejecucion" {
  value       = module.identidad.nombre
  description = "Nombre del rol de ejecucion."
}

output "parametros" {
  value       = module.parametros.nombres
  description = "Nombres completos de los parametros provisionados."
}
