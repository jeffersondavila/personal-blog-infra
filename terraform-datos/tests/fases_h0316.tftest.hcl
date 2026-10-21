# Pruebas OFFLINE de los modulos de H-031-6 que este root TODAVIA NO llama (Task/031).
#
# H-031-5 espera la cuota de concurrencia de Lambda, asi que el plan revisado de H-031-5 no puede cambiar: los
# modulos de las fases siguientes se prueban aqui por separado (`module { source }` en cada `run`) y entran en el
# root cuando exista la ejecutora. Provider simulado: sin red, sin AWS y sin crear nada.
#
# Lo que NO demuestran: que IAM evalue las condiciones (`s3:if-none-match`, `aws:SourceVpce`), que la regla deje
# pasar el trafico ni que SSM cifre. Eso es AWS-only, con el apply de H-031-6.
#
# Las contrasenas de estas pruebas son CANARIOS, no secretos.

mock_provider "aws" {
  override_during = plan
}

variables {
  nombre                  = "blog-prod"
  nombre_del_rol          = "PersonalBlogEjecutorDatos"
  arn_del_bucket          = "arn:aws:s3:::blog-prod-medios-simulado"
  id_sg_admin             = "sg-admin-simulado"
  prefix_list_s3          = "pl-simulada"
  id_del_endpoint_s3      = "vpce-simulado"
  ruta_base               = "/blog-prod/datos"
  contrasena_blog_migrate = "CanarioMigracionesNoEsSecreto0123456789"
  contrasena_blog_app     = "CanarioAplicacionNoEsSecreto01234567890"
}

# --- exportacion -------------------------------------------------------------

run "exportacion_politica_exacta_y_minima" {
  command = plan

  module {
    source = "../terraform/modulos/exportacion"
  }

  assert {
    condition = aws_iam_role_policy.this.policy == jsonencode({
      Version = "2012-10-17"
      Statement = [{
        Sid      = "EscrituraCondicionalEnElPrefijoDeExportacion"
        Effect   = "Allow"
        Action   = "s3:PutObject"
        Resource = "arn:aws:s3:::blog-prod-medios-simulado/exportaciones/*"
        Condition = {
          StringEquals = {
            "s3:if-none-match" = "*"
            "aws:SourceVpce"   = "vpce-simulado"
          }
        }
      }]
    })
    error_message = "La politica de exportacion debe ser exactamente PutObject condicional en el prefijo, por el endpoint."
  }

  assert {
    condition     = aws_iam_role_policy.this.role == "PersonalBlogEjecutorDatos" && aws_iam_role_policy.this.name == "PersonalBlogEjecutorDatos-exportacion"
    error_message = "La politica va inline en el rol propio de la ejecutora, con nombre estable."
  }

  assert {
    condition     = !strcontains(aws_iam_role_policy.this.policy, "medios/") && !strcontains(aws_iam_role_policy.this.policy, "GetObject") && !strcontains(aws_iam_role_policy.this.policy, "DeleteObject") && !strcontains(aws_iam_role_policy.this.policy, "ListBucket")
    error_message = "Ni el prefijo de medios ni lectura, borrado o listado."
  }

  assert {
    condition     = output.prefijo == "exportaciones/"
    error_message = "El prefijo dedicado es exportaciones/."
  }
}

run "exportacion_salida_https_solo_hacia_la_prefix_list" {
  command = plan

  module {
    source = "../terraform/modulos/exportacion"
  }

  assert {
    condition     = aws_vpc_security_group_egress_rule.admin_a_s3.security_group_id == "sg-admin-simulado" && aws_vpc_security_group_egress_rule.admin_a_s3.prefix_list_id == "pl-simulada"
    error_message = "La regla sale de sg-admin hacia la prefix list del gateway endpoint."
  }

  assert {
    condition     = aws_vpc_security_group_egress_rule.admin_a_s3.ip_protocol == "tcp" && aws_vpc_security_group_egress_rule.admin_a_s3.from_port == 443 && aws_vpc_security_group_egress_rule.admin_a_s3.to_port == 443
    error_message = "Solo TCP 443."
  }

  assert {
    condition     = aws_vpc_security_group_egress_rule.admin_a_s3.cidr_ipv4 == null && aws_vpc_security_group_egress_rule.admin_a_s3.cidr_ipv6 == null && aws_vpc_security_group_egress_rule.admin_a_s3.referenced_security_group_id == null
    error_message = "Nunca un CIDR: solo la prefix list."
  }
}

run "exportacion_bucket_con_puntos_rechazado" {
  command = plan

  module {
    source = "../terraform/modulos/exportacion"
  }

  variables {
    arn_del_bucket = "arn:aws:s3:::blog.prod.medios"
  }

  expect_failures = [var.arn_del_bucket]
}

run "exportacion_ruta_de_objeto_rechazada" {
  command = plan

  module {
    source = "../terraform/modulos/exportacion"
  }

  variables {
    arn_del_bucket = "arn:aws:s3:::blog-prod-medios-simulado/*"
  }

  expect_failures = [var.arn_del_bucket]
}

run "exportacion_endpoint_y_prefix_list_validados" {
  command = plan

  module {
    source = "../terraform/modulos/exportacion"
  }

  variables {
    prefix_list_s3     = "0.0.0.0/0"
    id_del_endpoint_s3 = "cualquiera"
  }

  expect_failures = [var.prefix_list_s3, var.id_del_endpoint_s3]
}

# --- credenciales_sql --------------------------------------------------------

run "credenciales_sql_custodia_como_la_master" {
  command = plan

  module {
    source = "../terraform/modulos/credenciales_sql"
  }

  assert {
    condition     = aws_ssm_parameter.blog_migrate.name == "/blog-prod/datos/blog_migrate" && aws_ssm_parameter.blog_app.name == "/blog-prod/datos/blog_app"
    error_message = "Rutas exactas junto a la master: /<prefijo>/datos/<identidad>."
  }

  assert {
    condition = alltrue([for p in [aws_ssm_parameter.blog_migrate, aws_ssm_parameter.blog_app] :
    p.type == "SecureString" && p.tier == "Standard" && p.key_id == "alias/aws/ssm"])
    error_message = "SecureString estandar con la clave administrada aws/ssm: sin costo y sin CMK nueva."
  }

  assert {
    condition     = aws_ssm_parameter.blog_migrate.value_wo_version == 1 && aws_ssm_parameter.blog_app.value_wo_version == 1
    error_message = "La escritura write-only arranca en la version 1."
  }

  assert {
    condition     = output.nombres_de_los_parametros == { blog_migrate = "/blog-prod/datos/blog_migrate", blog_app = "/blog-prod/datos/blog_app" }
    error_message = "Las salidas dan rutas, nunca valores."
  }
}

run "credenciales_sql_rotacion_independiente" {
  command = plan

  module {
    source = "../terraform/modulos/credenciales_sql"
  }

  variables {
    version_de_blog_app = 2
  }

  assert {
    condition     = aws_ssm_parameter.blog_app.value_wo_version == 2 && aws_ssm_parameter.blog_migrate.value_wo_version == 1
    error_message = "Rotar blog_app no toca blog_migrate (D-23: rotacion independiente)."
  }
}

run "credenciales_sql_contrasenas_fuera_de_politica" {
  command = plan

  module {
    source = "../terraform/modulos/credenciales_sql"
  }

  variables {
    contrasena_blog_migrate = "corta"
    contrasena_blog_app     = "con-guiones-y-simbolos-no-admitidos-!!!!"
  }

  expect_failures = [var.contrasena_blog_migrate, var.contrasena_blog_app]
}

run "credenciales_sql_version_y_ruta_validadas" {
  command = plan

  module {
    source = "../terraform/modulos/credenciales_sql"
  }

  variables {
    version_de_blog_migrate = 0
    ruta_base               = "/blog-prod/datos/"
  }

  expect_failures = [var.version_de_blog_migrate, var.ruta_base]
}
