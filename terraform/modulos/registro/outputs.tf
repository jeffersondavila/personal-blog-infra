output "nombre" {
  value       = aws_cloudwatch_log_group.funcion.name
  description = "Nombre del grupo de logs."
}

output "arn" {
  value       = aws_cloudwatch_log_group.funcion.arn
  description = "ARN del grupo, para acotar el permiso de escritura del rol."
}
