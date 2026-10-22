# Alarmas de D-11 para la instancia productiva (Task/031 H-031-8; senales minimas de §9.2 de las decisiones de RDS).
#
# Ocho alarmas, dentro de las 10 gratuitas de CloudWatch. Estadistico, periodo, puntos y comparador siguen la guia
# de AWS "Recommended alarms" para Amazon RDS (descargada el 2026-10-07); los umbrales que la guia deja "segun tu caso"
# se derivan de la clase fijada por D-22 (db.t4g.micro, 1 GiB) y del presupuesto de conexiones de D-12 §6.2.
#
# Sin acciones ni destinatarios: SNS, correo o paginacion no estan aprobados (D-11 deja abiertos los destinatarios).
# Las alarmas cambian de estado y se ven en la consola y, con D-20, en Grafana. `actions_enabled = false` lo deja
# explicito: anadir un destinatario sera una decision y un cambio revisado, no un efecto lateral.
#
# El fallo de backup de D-11 NO esta aqui: RDS no publica una metrica de CloudWatch para eso; lo comunica como evento,
# y llevar ese evento a una alarma exige EventBridge y otro destino, servicios no aprobados. Decision pendiente.
#
# NO lo llama ningun root todavia: entra en `terraform-datos` cuando se pueda aplicar ese root (H-031-5 espera la cuota
# de concurrencia de Lambda).

locals {
  # db.t4g.micro (D-22): 1 GiB. max_connections = LEAST(DBInstanceClassMemory/9531392, 5000) = 112 (D-12 §6.2).
  memoria_bytes  = 1073741824
  max_conexiones = 112

  alarmas = {
    cpu = {
      metrica = "CPUUtilization", estadistico = "Average", percentil = null, periodo = 60, puntos = 5,
      umbral  = 90, operador = "GreaterThanThreshold"
      razon   = "CPU media por encima del 90 % durante 5 minutos seguidos: saturacion sostenida (umbral recomendado por AWS para RDS)."
    }
    conexiones = {
      metrica = "DatabaseConnections", estadistico = "Average", percentil = null, periodo = 60, puntos = 5,
      umbral  = floor(local.max_conexiones * 0.9), operador = "GreaterThanThreshold"
      razon   = "Mas de 100 conexiones durante 5 minutos: 90 % de max_connections = 112 de db.t4g.micro (D-12 §6.2; AWS recomienda 90-95 %)."
    }
    memoria = {
      metrica = "FreeableMemory", estadistico = "Average", percentil = null, periodo = 60, puntos = 15,
      umbral  = floor(local.memoria_bytes * 0.25), operador = "LessThanThreshold"
      razon   = "Memoria liberable por debajo del 25 % de 1 GiB durante 15 minutos (criterio de AWS para RDS); revisar con historial real."
    }
    almacenamiento = {
      metrica = "FreeStorageSpace", estadistico = "Minimum", percentil = null, periodo = 60, puntos = 5,
      umbral  = 1073741824, operador = "LessThanThreshold"
      razon   = "Menos de 1 GiB libre durante 5 minutos: por debajo del disparo del autoscaling (10 % de lo asignado), avisa solo si no alcanza (techo de 50 GiB o espera entre ampliaciones)."
    }
    xid = {
      metrica = "MaximumUsedTransactionIDs", estadistico = "Average", percentil = null, periodo = 60, puntos = 1,
      umbral  = 1000000000, operador = "GreaterThanThreshold"
      razon   = "Mil millones de transaction IDs usados: autovacuum no contiene el envejecimiento; margen antes del wraparound (umbral recomendado por AWS)."
    }
    lectura = {
      metrica = "ReadLatency", estadistico = null, percentil = "p90", periodo = 60, puntos = 5,
      umbral  = 0.02, operador = "GreaterThanThreshold"
      razon   = "Latencia de lectura p90 por encima de 20 ms durante 5 minutos (criterio de AWS para RDS): el almacenamiento no da abasto."
    }
    escritura = {
      metrica = "WriteLatency", estadistico = null, percentil = "p90", periodo = 60, puntos = 5,
      umbral  = 0.02, operador = "GreaterThanThreshold"
      razon   = "Latencia de escritura p90 por encima de 20 ms durante 5 minutos (criterio de AWS para RDS): el almacenamiento no da abasto."
    }
    creditos = {
      metrica = "CPUCreditBalance", estadistico = "Minimum", percentil = null, periodo = 300, puntos = 3,
      umbral  = 29, operador = "LessThanThreshold"
      razon   = "Saldo de creditos de CPU por debajo de 29 durante 15 minutos: 10 % del maximo de 288 de una t4g.micro (modelo burstable); a confirmar con la metrica real."
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "this" {
  for_each = local.alarmas

  alarm_name          = "${var.nombre}-rds-${each.key}"
  alarm_description   = each.value.razon
  namespace           = "AWS/RDS"
  metric_name         = each.value.metrica
  dimensions          = { DBInstanceIdentifier = var.identificador_de_la_instancia }
  statistic           = each.value.estadistico
  extended_statistic  = each.value.percentil
  period              = each.value.periodo
  evaluation_periods  = each.value.puntos
  datapoints_to_alarm = each.value.puntos
  threshold           = each.value.umbral
  comparison_operator = each.value.operador
  treat_missing_data  = "missing"

  actions_enabled           = false
  alarm_actions             = []
  ok_actions                = []
  insufficient_data_actions = []

  tags = {
    Name = "${var.nombre}-rds-${each.key}"
  }
}
