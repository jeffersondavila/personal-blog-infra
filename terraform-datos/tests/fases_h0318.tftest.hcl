# Pruebas OFFLINE del modulo de alarmas de H-031-8 (D-11), que este root TODAVIA NO llama (Task/031).
#
# Lo que demuestran: el catalogo exacto (8 alarmas, dentro de las 10 gratuitas), cada metrica con su namespace,
# dimension, estadistico, periodo, evaluaciones, umbral y comparador, y que ninguna tiene acciones (sin SNS ni otro
# destinatario: no estan aprobados). Lo que NO demuestran: que CloudWatch evalue, que la metrica exista para la
# instancia ni que una alarma cambie de estado. Eso exige AWS real y tiempo de observacion.

mock_provider "aws" {
  override_during = plan
}

variables {
  nombre                        = "blog-prod"
  identificador_de_la_instancia = "blog-prod-postgres"
}

run "alarmas_d11_catalogo_exacto" {
  command = plan

  module {
    source = "../terraform/modulos/alarmas_rds"
  }

  assert {
    condition     = length(aws_cloudwatch_metric_alarm.this) == 8 && length(aws_cloudwatch_metric_alarm.this) <= 10
    error_message = "Ocho alarmas, dentro de las 10 del free tier de CloudWatch."
  }

  assert {
    condition     = sort(keys(aws_cloudwatch_metric_alarm.this)) == tolist(["almacenamiento", "conexiones", "cpu", "creditos", "escritura", "lectura", "memoria", "xid"])
    error_message = "El catalogo es el de D-11 menos el fallo de backup, que no tiene metrica."
  }

  assert {
    condition = alltrue([for clave, alarma in aws_cloudwatch_metric_alarm.this :
      alarma.alarm_name == "blog-prod-rds-${clave}" && alarma.namespace == "AWS/RDS"
      && alarma.dimensions == tomap({ DBInstanceIdentifier = "blog-prod-postgres" })
    && alarma.treat_missing_data == "missing" && length(alarma.alarm_description) > 40])
    error_message = "Nombre estable, AWS/RDS, la instancia productiva como unica dimension, datos ausentes explicitos y una razon."
  }

  assert {
    condition = alltrue([for alarma in values(aws_cloudwatch_metric_alarm.this) :
      alarma.actions_enabled == false && length(alarma.alarm_actions) == 0 && length(alarma.ok_actions) == 0
    && length(alarma.insufficient_data_actions) == 0])
    error_message = "Sin acciones ni destinatarios: SNS, correo o paginacion no estan aprobados."
  }

  assert {
    condition = { for clave, alarma in aws_cloudwatch_metric_alarm.this : clave => [
      alarma.metric_name, coalesce(alarma.statistic, alarma.extended_statistic), alarma.period,
      alarma.evaluation_periods, alarma.datapoints_to_alarm, alarma.threshold, alarma.comparison_operator] } == {
      cpu            = ["CPUUtilization", "Average", 60, 5, 5, 90, "GreaterThanThreshold"]
      conexiones     = ["DatabaseConnections", "Average", 60, 5, 5, 100, "GreaterThanThreshold"]
      memoria        = ["FreeableMemory", "Average", 60, 15, 15, 268435456, "LessThanThreshold"]
      almacenamiento = ["FreeStorageSpace", "Minimum", 60, 5, 5, 1073741824, "LessThanThreshold"]
      xid            = ["MaximumUsedTransactionIDs", "Average", 60, 1, 1, 1000000000, "GreaterThanThreshold"]
      lectura        = ["ReadLatency", "p90", 60, 5, 5, 0.02, "GreaterThanThreshold"]
      escritura      = ["WriteLatency", "p90", 60, 5, 5, 0.02, "GreaterThanThreshold"]
      creditos       = ["CPUCreditBalance", "Minimum", 300, 3, 3, 29, "LessThanThreshold"]
    }
    error_message = "Cada alarma con la metrica, el estadistico, el periodo, las evaluaciones y el umbral justificados."
  }

  assert {
    condition     = output.numero_de_alarmas == 8
    error_message = "La salida declara cuantas alarmas cuentan contra el free tier."
  }
}

run "alarmas_identificador_validado" {
  command = plan

  module {
    source = "../terraform/modulos/alarmas_rds"
  }

  variables {
    identificador_de_la_instancia = "blog-prod-restore-h0317-20261007120000"
  }

  expect_failures = [var.identificador_de_la_instancia]
}
