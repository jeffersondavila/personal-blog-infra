# ---------------------------------------------------------------------------
# Salidas — el CONTRATO que consumiran la ejecutora (H-031-5) y la Lambda de
# aplicacion (Task/032), siempre como variables de entrada de su propio root.
#
# Ninguna salida es sensible y ninguna lleva la contrasena master: solo el
# NOMBRE del SecureString que la custodia. Las pruebas offline lo afirman.
# ---------------------------------------------------------------------------

output "id_de_vpc" {
  value       = module.red.id_de_vpc
  description = "VPC dedicada."
}

output "ids_de_subredes" {
  value       = module.red.ids_de_subredes
  description = "Subredes privadas (a, b)."
}

output "id_sg_lambda" {
  value       = module.red.id_sg_lambda
  description = "Grupo de la Lambda de aplicacion. Task/032 lo adjunta EXPLICITAMENTE; nunca el grupo por omision."
}

output "id_sg_admin" {
  value       = module.red.id_sg_admin
  description = "Grupo de la ejecutora privada. H-031-5 lo adjunta EXPLICITAMENTE; nunca el grupo por omision."
}

output "id_sg_rds" {
  value       = module.red.id_sg_rds
  description = "Grupo de la base de datos: el unico que lleva la instancia."
}

output "id_endpoint_s3" {
  value       = module.red.id_endpoint_s3
  description = "Gateway endpoint de S3."
}

output "prefix_list_s3" {
  value       = module.red.prefix_list_s3
  description = "Prefix list de S3, destino de las reglas HTTPS de salida."
}

output "endpoint_rds" {
  value       = module.base_de_datos.endpoint
  description = "Nombre DNS de la instancia."
}

output "puerto_rds" {
  value       = module.base_de_datos.puerto
  description = "Puerto SQL."
}

output "nombre_de_base" {
  value       = module.base_de_datos.nombre_de_base
  description = "Base de datos inicial."
}

output "identificador_rds" {
  value       = module.base_de_datos.identificador
  description = "Identificador de la instancia."
}

output "arn_rds" {
  value       = module.base_de_datos.arn
  description = "ARN de la instancia."
}

output "id_de_recurso_rds" {
  value       = module.base_de_datos.id_de_recurso
  description = "DbiResourceId de la instancia."
}

output "nombre_del_parametro_master" {
  value       = module.base_de_datos.nombre_del_parametro_master
  description = "Nombre del SecureString de la contrasena master. Nunca su valor."
}

output "grupo_de_logs_rds" {
  value       = module.base_de_datos.nombre_del_grupo_de_logs
  description = "Grupo de logs de PostgreSQL."
}

output "nombre_de_la_ejecutora" {
  value       = module.ejecutor_privado.nombre
  description = "Ejecutora privada de D-24 (H-031-5): se invoca por el plano de control (`lambda:InvokeFunction`)."
}

output "arn_de_la_ejecutora" {
  value       = module.ejecutor_privado.arn
  description = "ARN de la ejecutora. Contrato de Task/038, cuyo rol de despliegue la invocara."
}

output "alarmas_de_rds" {
  value       = module.alarmas_rds.nombres
  description = "Alarmas de D-11 (H-031-8), por senal."
}

output "rol_de_grafana" {
  value       = module.lectura_grafana.nombre_del_rol
  description = "Rol que Grafana Cloud asume (D-20). Solo el NOMBRE: el ARN lleva la cuenta y se lee de IAM al configurar."
}
output "nombres_de_credenciales_sql" {
  value       = module.credenciales_sql.nombres_de_los_parametros
  description = "Nombres SSM de las dos credenciales SQL, nunca sus valores."
}
