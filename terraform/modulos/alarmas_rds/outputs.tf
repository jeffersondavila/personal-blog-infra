output "nombres" {
  description = "Nombre estable de cada alarma, por senal."
  value       = { for clave, alarma in aws_cloudwatch_metric_alarm.this : clave => alarma.alarm_name }
}

output "numero_de_alarmas" {
  description = "Alarmas que cuentan contra las 10 gratuitas de CloudWatch."
  value       = length(aws_cloudwatch_metric_alarm.this)
}

output "configuracion_efectiva" {
  description = "Contrato de verificacion: por senal, nombre, metrica, dimension, umbral y si tiene acciones."
  value = { for clave, alarma in aws_cloudwatch_metric_alarm.this : clave => {
    nombre    = alarma.alarm_name
    metrica   = alarma.metric_name
    dimension = alarma.dimensions["DBInstanceIdentifier"]
    umbral    = alarma.threshold
    acciones  = alarma.actions_enabled
  } }
}
