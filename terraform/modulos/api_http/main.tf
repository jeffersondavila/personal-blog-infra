# ---------------------------------------------------------------------------
# Modulo: api_http — API Gateway HTTP API (v2) delante de la funcion
#
# Que crea y por que existe
#   La puerta de entrada HTTP del backend en la nube. Es el equivalente
#   productivo de Traefik en el entorno local: mismo papel, distinto componente
#   (docs/architecture/local-to-cloud-mapping.md).
#
# Por que HTTP API (v2) y no REST API (v1)
#   ADR-003 la fija por costo: la HTTP API es sensiblemente mas barata y el
#   proyecto no usa nada exclusivo de v1. El adaptador de Task/023 traduce el
#   payload format 2.0, que es el de v2.
#
# Los cuatro recursos y su razon
#   api          - el contenedor logico de la API
#   integration  - AWS_PROXY: entrega el evento entero al handler, sin plantillas
#   route        - $default: toda ruta va a la misma integracion, porque quien
#                  enruta de verdad es FastAPI dentro de la funcion
#   stage        - el despliegue al que se llega por HTTP
#   permission   - sin ella API Gateway no puede invocar la funcion
#
# ESTE ES EL CAMINO CRITICO DEL PROYECTO
#   La suite oficial de compatibilidad del emulador NO cubre aws_lambda_function
#   ni los recursos aws_apigatewayv2_* ni aws_cloudwatch_log_group
#   (aws-local-parity.md 6.8, riesgo R-25). Que esta combinacion funcione es
#   exactamente lo que Task/025 tiene que demostrar, no algo que se pueda dar por
#   supuesto.
#
# SOLO LABORATORIO: el stage por omision y la ruta $default simplifican la
# validacion local. La decision de stage y base path de PRODUCCION es de
# Task/033. Esto no la anticipa.
# ---------------------------------------------------------------------------

resource "aws_apigatewayv2_api" "backend" {
  name          = var.nombre
  protocol_type = "HTTP"
  description   = "Puerta de entrada HTTP del backend del blog."
}

resource "aws_apigatewayv2_integration" "backend" {
  api_id = aws_apigatewayv2_api.backend.id

  integration_type = "AWS_PROXY"
  integration_uri  = var.arn_de_invocacion_de_la_funcion

  # 2.0 es el formato que el adaptador de Task/023 traduce. Fijarlo evita que un
  # cambio del valor por omision del provider altere el evento en silencio.
  payload_format_version = "2.0"
  integration_method     = "POST"
  timeout_milliseconds   = var.timeout_ms
}

# Ruta comodin: FastAPI ya enruta. Declarar aqui cada ruta del backend
# duplicaria el enrutado en dos sitios que se desincronizarian.
resource "aws_apigatewayv2_route" "predeterminada" {
  api_id    = aws_apigatewayv2_api.backend.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.backend.id}"
}

resource "aws_apigatewayv2_stage" "principal" {
  api_id      = aws_apigatewayv2_api.backend.id
  name        = var.nombre_del_stage
  auto_deploy = true
}

# Politica de recurso de la funcion: sin ella la invocacion falla con 500 y el
# motivo no aparece en los logs de la funcion, porque la funcion no llega a
# ejecutarse.
#
# `source_arn` acota quien puede invocar: esta API y ninguna otra.
resource "aws_lambda_permission" "api" {
  statement_id  = "PermitirInvocacionDesdeApiGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.nombre_de_la_funcion
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.backend.execution_arn}/*/*"
}
