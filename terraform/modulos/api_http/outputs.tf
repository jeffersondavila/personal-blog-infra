output "id" {
  value       = aws_apigatewayv2_api.backend.id
  description = "Identificador de la API, usado al verificar su ausencia tras el destroy."
}

output "endpoint" {
  value       = aws_apigatewayv2_api.backend.api_endpoint
  description = "Endpoint que devuelve el destino. Es la URL del smoke del camino critico."
}

output "nombre_del_stage" {
  value       = aws_apigatewayv2_stage.principal.name
  description = "Stage desplegado."
}

output "arn_de_ejecucion" {
  value       = aws_apigatewayv2_api.backend.execution_arn
  description = "ARN de ejecucion, base del source_arn del permiso de invocacion."
}
