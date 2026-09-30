# ---------------------------------------------------------------------------
# Root de almacenamiento de medios — UNA SOLA llamada al modulo compartido.
#
# `source` apunta al modulo del grafo de aplicacion: no se copia, no se
# bifurca y no se reimplementa ningun recurso `aws_s3_*`. Si el modulo cambia,
# cambia para los dos destinos y para los dos roots a la vez, que es lo que la
# regla de paridad protege de verdad.
#
# Este root NO crea IAM, ni parametros, ni logs, ni funcion, ni API: el rol de
# ejecucion y su politica minima siguen en el grafo de aplicacion y son de la
# tarea que los despliegue. Aqui solo vive el almacenamiento persistente.
# ---------------------------------------------------------------------------

module "almacenamiento" {
  source = "../terraform/modulos/almacenamiento"

  nombre                      = var.nombre_del_bucket
  origenes_cors               = var.origenes_cors
  dias_para_expirar_versiones = var.dias_para_expirar_versiones
  forzar_destruccion          = var.forzar_destruccion

  # Explicitas, ademas de `default_tags`: un provider simulado no propaga
  # `default_tags`, asi que sin esto el etiquetado no seria demostrable offline.
  etiquetas = var.etiquetas
}
