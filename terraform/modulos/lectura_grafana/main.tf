# D-20 (Task/031 H-031-9): rol de SOLO LECTURA que Grafana Cloud asume para consultar CloudWatch.
#
# PREPARADO, NO IMPLEMENTADO. No lo llama ningun root: D-20 no se aplica hasta demostrar el gate de D-19 (plan,
# limites y costo reales de Grafana Cloud, con datos de la cuenta del usuario) y hasta tener la cuenta AWS de Grafana y
# el ExternalId de su stack. Propuesta de mecanismo, pendiente de aprobacion: rol asumible con ExternalId (sin clave
# estatica en manos de un tercero, sin push ni servicios nuevos).
#
# Solo metricas y estados de alarma:
# - `cloudwatch:GetMetricData` y `cloudwatch:ListMetrics`, en la region del proyecto.
# - `cloudwatch:DescribeAlarms`, solo sobre las alarmas `<prefijo>-*`.
# Sin `logs:*`: el log de PostgreSQL puede contener verificadores SCRAM y sentencias DDL (H-031-6; R-39), y D-11 ya
# advierte que lo que llega a CloudWatch viajaria a un tercero. Sin escritura, IAM, SQL, S3, despliegue ni RDS.
#
# Costo: `GetMetricData` se cobra SIEMPRE (USD 0.01 por 1.000 metricas en us-east-2; no entra en el millon de peticiones
# gratuitas). Por eso D-19 debe fijar consultas bajo demanda y las alarmas de CloudWatch como fuente de alertas, no un
# sondeo continuo.

locals {
  confianza = jsondecode(templatefile("${path.module}/confianza.json.tftpl", {
    cuenta_de_grafana = var.cuenta_de_grafana
    external_id       = var.external_id
  }))

  politica = jsondecode(templatefile("${path.module}/politica.json.tftpl", {
    cuenta  = var.cuenta
    region  = var.region
    prefijo = var.prefijo
  }))
}

resource "aws_iam_role" "this" {
  name                 = var.nombre_del_rol
  path                 = "/"
  description          = "D-20: lectura de metricas y estados de alarma de CloudWatch para Grafana Cloud. Sin logs ni escritura."
  max_session_duration = 3600
  assume_role_policy   = jsonencode(local.confianza)
}

resource "aws_iam_role_policy" "this" {
  name   = "${var.nombre_del_rol}-lectura"
  role   = aws_iam_role.this.name
  policy = jsonencode(local.politica)
}
