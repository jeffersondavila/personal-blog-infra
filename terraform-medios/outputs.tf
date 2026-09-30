# ---------------------------------------------------------------------------
# Salidas — el CONTRATO que consume el grafo de aplicacion.
#
# El grafo de aplicacion recibe estos dos valores como INPUTS explicitos
# (`nombre_del_bucket_de_medios` y `arn_del_bucket_de_medios`). Deliberadamente
# NO se usa `terraform_remote_state` desde el otro lado: eso acoplaria el root de
# aplicacion a la ubicacion y al formato del state de este root, y le exigiria
# permiso de lectura sobre el. Dos variables resuelven la dependencia sin crear
# ese acoplamiento, y el orquestador es quien las transporta.
# ---------------------------------------------------------------------------

output "nombre_del_bucket" {
  value       = module.almacenamiento.nombre
  description = "Nombre del bucket de medios. Entrada del grafo de aplicacion."
}

output "arn_del_bucket" {
  value       = module.almacenamiento.arn
  description = "ARN del bucket. Lo consume la politica del rol de ejecucion."
}
