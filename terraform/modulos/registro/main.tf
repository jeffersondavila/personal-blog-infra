# ---------------------------------------------------------------------------
# Modulo: registro — grupo de CloudWatch Logs de la funcion
#
# Que crea y por que existe
#   El grupo con el nombre EXACTO que Lambda usa por convencion,
#   `/aws/lambda/<funcion>`. Crearlo con Terraform y no dejar que lo cree Lambda
#   tiene una consecuencia concreta: asi tiene retencion declarada desde el
#   primer dia. Un grupo creado por el servicio nace con retencion INFINITA, que
#   en AWS real es una factura que crece sola.
#
# De que depende
#   De nada. La funcion y el rol dependen de el: el rol acota su permiso de
#   escritura a este ARN, y la funcion necesita que exista antes de escribir.
#
# Diferencia conocida con AWS real
#   Los filtros de suscripcion se almacenan pero NO se entregan al destino, y
#   Logs Insights degrada en silencio ante sintaxis no soportada
#   (aws-local-parity.md 6.6). Este modulo no crea ninguno de los dos, asi que la
#   diferencia no afecta a lo que aqui se despliega; se registra porque afecta a
#   como se diagnostica.
# ---------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "funcion" {
  name              = "/aws/lambda/${var.nombre_de_la_funcion}"
  retention_in_days = var.dias_de_retencion
}
