# Pruebas OFFLINE del rol de D-20 (H-031-9), PREPARADO y NO implementado: este root no lo llama.
#
# D-20 no se aplica hasta demostrar el gate de D-19. Estas pruebas fijan la confianza (solo la cuenta de Grafana, solo
# con su ExternalId) y la politica de solo lectura (metricas y estados de alarma, sin logs ni escritura). Las
# decisiones de IAM se simulan offline en `tests/terraform_datos/test_politicas_de_las_fases.py`; la simulacion contra
# AWS (`simulate-custom-policy`) y el readback del rol son de la implementacion, despues de D-19.

mock_provider "aws" {
  override_during = plan
}

variables {
  nombre_del_rol    = "PersonalBlogLecturaGrafana"
  cuenta            = "123456789012"
  region            = "us-east-2"
  prefijo           = "blog-prod"
  cuenta_de_grafana = "999999999999"
  external_id       = "stack-simulado-12345"
}

run "d20_confianza_solo_grafana_con_external_id" {
  command = plan

  module {
    source = "../terraform/modulos/lectura_grafana"
  }

  assert {
    condition = aws_iam_role.this.assume_role_policy == jsonencode({
      Version = "2012-10-17"
      Statement = [{
        Sid       = "GrafanaCloudConExternalId"
        Effect    = "Allow"
        Principal = { AWS = "arn:aws:iam::999999999999:root" }
        Action    = "sts:AssumeRole"
        Condition = { StringEquals = { "sts:ExternalId" = "stack-simulado-12345" } }
      }]
    })
    error_message = "Solo la cuenta de Grafana, solo con el ExternalId de su stack."
  }

  assert {
    condition     = aws_iam_role.this.name == "PersonalBlogLecturaGrafana" && aws_iam_role.this.max_session_duration == 3600 && aws_iam_role.this.path == "/"
    error_message = "Rol propio, sesiones de una hora."
  }
}

run "d20_politica_solo_lectura_de_metricas" {
  command = plan

  module {
    source = "../terraform/modulos/lectura_grafana"
  }

  assert {
    condition = aws_iam_role_policy.this.policy == jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Sid       = "MetricasSoloLectura"
          Effect    = "Allow"
          Action    = ["cloudwatch:GetMetricData", "cloudwatch:ListMetrics"]
          Resource  = "*"
          Condition = { StringEquals = { "aws:RequestedRegion" = "us-east-2" } }
        },
        {
          Sid       = "EstadosDeLasAlarmasDelProyecto"
          Effect    = "Allow"
          Action    = "cloudwatch:DescribeAlarms"
          Resource  = "arn:aws:cloudwatch:us-east-2:123456789012:alarm:blog-prod-*"
          Condition = { StringEquals = { "aws:RequestedRegion" = "us-east-2" } }
        },
      ]
    })
    error_message = "Metricas y estados de alarma del proyecto, en us-east-2, y nada mas."
  }

  assert {
    condition     = !strcontains(aws_iam_role_policy.this.policy, "logs:") && !strcontains(aws_iam_role_policy.this.policy, "Put") && !strcontains(aws_iam_role_policy.this.policy, "Delete") && !strcontains(aws_iam_role_policy.this.policy, "Set")
    error_message = "Ni logs ni ninguna accion de escritura."
  }

  assert {
    condition     = output.nombre_del_rol == "PersonalBlogLecturaGrafana"
    error_message = "La salida da el nombre del rol, nunca un ARN con la cuenta."
  }
}

run "d20_cuenta_de_grafana_distinta_de_la_del_proyecto" {
  command = plan

  module {
    source = "../terraform/modulos/lectura_grafana"
  }

  variables {
    cuenta_de_grafana = "123456789012"
  }

  expect_failures = [var.cuenta_de_grafana]
}

# La region exacta (us-east-2) la exige la guarda del plan productivo: el laboratorio usa la del emulador con el
# MISMO modulo. Aqui solo se rechaza lo que no es una region.
run "d20_region_y_external_id_validados" {
  command = plan

  module {
    source = "../terraform/modulos/lectura_grafana"
  }

  variables {
    region      = "global"
    external_id = "con espacios"
  }

  expect_failures = [var.region, var.external_id]
}

run "d20_mismo_modulo_en_la_region_del_laboratorio" {
  command = plan

  module {
    source = "../terraform/modulos/lectura_grafana"
  }

  variables {
    region = "us-east-1"
    cuenta = "000000000000"
  }

  assert {
    condition     = output.configuracion_efectiva.permisos.Statement[1].Resource == "arn:aws:cloudwatch:us-east-1:000000000000:alarm:blog-prod-*"
    error_message = "El mismo modulo en el laboratorio: solo cambian los valores del destino."
  }
}
