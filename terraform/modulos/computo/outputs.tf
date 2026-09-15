output "nombre" {
  value       = aws_lambda_function.backend.function_name
  description = "Nombre de la funcion."
}

output "arn" {
  value       = aws_lambda_function.backend.arn
  description = "ARN de la funcion, consumido por la integracion de API Gateway."
}

output "arn_de_invocacion" {
  value       = aws_lambda_function.backend.invoke_arn
  description = "ARN de invocacion que exige la integracion AWS_PROXY."
}

output "hash_del_codigo" {
  value       = aws_lambda_function.backend.source_code_hash
  description = "Hash del artefacto desplegado, registrado como evidencia."
}
