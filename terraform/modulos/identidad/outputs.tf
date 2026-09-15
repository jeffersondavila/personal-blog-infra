output "arn" {
  value       = aws_iam_role.ejecucion.arn
  description = "ARN del rol de ejecucion, consumido por la funcion Lambda."
}

output "nombre" {
  value       = aws_iam_role.ejecucion.name
  description = "Nombre del rol, usado al verificar su existencia tras el apply."
}
