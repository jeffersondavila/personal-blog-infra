output "arns" {
  value       = [for p in aws_ssm_parameter.configuracion : p.arn]
  description = "ARN de cada parametro, para acotar el permiso de lectura del rol."
}

output "nombres" {
  value       = [for p in aws_ssm_parameter.configuracion : p.name]
  description = "Nombres completos, usados al verificar su existencia y su ausencia."
}
