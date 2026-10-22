output "arn_del_rol_operativo" {
  value       = aws_iam_role.operador_datos.arn
  description = "ARN que el perfil `personal-blog-datos` asume (role_arn), con MFA."
}

output "politicas_fase_1_sha256" {
  value       = { for nombre, politica in local.politicas_fase_1 : nombre => sha256(jsonencode(politica)) }
  description = "Huella de cada politica revisada: la guarda de H-031-IAM las compara con el plan."
}

output "bucket_de_estado" {
  value       = local.bucket_de_estado
  description = "Bucket de D-06 al que el rol puede escribir SOLO la key del root de datos."
}
