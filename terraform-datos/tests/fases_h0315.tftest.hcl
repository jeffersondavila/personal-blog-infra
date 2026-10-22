# Pruebas OFFLINE de la ejecutora privada de D-24 (H-031-5) a nivel de MODULO (Task/031).
#
# Origen: el 2026-10-08 el cableado de la ejecutora salio del root `terraform-datos` mientras la cuota de Lambda no
# permitia reservar 1. El 2026-10-18 D-24 se modifico (aprobado el 2026-10-19): la ejecutora usa la
# concurrencia NO reservada, y la exclusion entre operaciones que escriben la hace su advisory lock de PostgreSQL.
# Estas son las aserciones de H-031-5 sobre el modulo, con los valores que le pasa el root.
#
# Lo que NO demuestran: que la ENI se cree ni que la politica autorice de verdad (AWS-only, H-031-5 apply).

mock_provider "aws" {
  override_during = plan
}

variables {
  nombre                    = "blog-prod-ejecutor"
  nombre_del_rol            = "PersonalBlogEjecutorDatos"
  region                    = "us-east-2"
  cuenta                    = "123456789012"
  ids_de_subredes           = ["subnet-a-simulada", "subnet-b-simulada"]
  id_sg_admin               = "sg-admin-simulado"
  dias_de_retencion_de_logs = 14
  # Artefacto SIMULADO: el provider simulado no lo lee; el modulo solo calcula su digest.
  ruta_del_zip   = "tests/artefacto-simulado.txt"
  sha256_del_zip = "22f5495252caeb77a4a36ecc70b36f4186352a2de6a535f6985dcbe44048fc1e"
}

run "ejecutora_privada_d24" {
  command = plan

  module {
    source = "../terraform/modulos/ejecutor_privado"
  }

  assert {
    condition = (
      output.configuracion_efectiva.funcion.nombre == "blog-prod-ejecutor" &&
      output.configuracion_efectiva.funcion.runtime == "python3.12" &&
      output.configuracion_efectiva.funcion.arquitecturas == tolist(["x86_64"]) &&
      output.configuracion_efectiva.funcion.handler == "ejecutor.manejar" &&
      output.configuracion_efectiva.funcion.paquete == "Zip" &&
      output.configuracion_efectiva.funcion.memoria == 128 &&
      output.configuracion_efectiva.funcion.timeout == 30 &&
      output.configuracion_efectiva.funcion.publicar == false
    )
    error_message = "Ejecutora Python 3.12 x86_64, handler ejecutor.manejar, 128 MB y 30 s, sin versiones publicadas."
  }

  assert {
    # D-24 modificada el 2026-10-18 (aprobada el 2026-10-19): SIN concurrencia reservada. El provider simulado deja `null` el
    # atributo omitido; el real lo pone a -1, el valor nativo sin reserva. Nunca 0 ni un numero de reserva.
    condition     = coalesce(output.configuracion_efectiva.funcion.concurrencia_reservada, -1) == -1
    error_message = "D-24: la ejecutora usa la concurrencia NO reservada; la exclusion de las escrituras la hace su advisory lock."
  }

  assert {
    condition = (
      output.configuracion_efectiva.funcion.subredes == toset(["subnet-a-simulada", "subnet-b-simulada"]) &&
      length(output.configuracion_efectiva.funcion.subredes) == 2 &&
      output.configuracion_efectiva.funcion.grupos == toset(["sg-admin-simulado"]) &&
      output.configuracion_efectiva.funcion.ipv6 == false
    )
    error_message = "La ejecutora va en las dos subredes privadas y EXCLUSIVAMENTE con sg-admin."
  }

  assert {
    condition = (
      output.configuracion_efectiva.funcion.variables_de_entorno == 0 &&
      output.configuracion_efectiva.funcion.capas == 0 &&
      output.configuracion_efectiva.funcion.hash_del_codigo == "IvVJUlLK63eko27McLNvQYY1Ki3mpTX2mF3L5EBI/B4="
    )
    error_message = "Sin variables de entorno ni capas; el codigo desplegado es exactamente el artefacto declarado."
  }

  assert {
    condition = (
      output.configuracion_efectiva.logs.nombre == "/aws/lambda/blog-prod-ejecutor" &&
      output.configuracion_efectiva.logs.retencion == 14
    )
    error_message = "Grupo de logs creado explicitamente, con el nombre que usa Lambda y 14 dias (baseline de D-11)."
  }

  assert {
    condition = (
      output.configuracion_efectiva.rol.nombre == "PersonalBlogEjecutorDatos" &&
      output.configuracion_efectiva.rol.ruta == "/" &&
      output.configuracion_efectiva.rol.sesion_maxima == 3600 &&
      output.configuracion_efectiva.rol.limite == null
    )
    error_message = "Rol de ejecucion PROPIO: PersonalBlogEjecutorDatos."
  }

  assert {
    condition = jsonencode(output.configuracion_efectiva.rol.confianza) == jsonencode({
      Version = "2012-10-17"
      Statement = [{
        Sid       = "LambdaAsumeElRolDeLaEjecutora"
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
        Action    = "sts:AssumeRole"
      }]
    })
    error_message = "Trust: solo el principal de servicio de Lambda, como documenta AWS; sin condiciones que no apliquen."
  }

  assert {
    condition = jsonencode(output.configuracion_efectiva.rol.permisos) == jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Sid      = "InterfacesDeRedDeLambdaEnVpc"
          Effect   = "Allow"
          Action   = ["ec2:AssignPrivateIpAddresses", "ec2:CreateNetworkInterface", "ec2:DeleteNetworkInterface", "ec2:DescribeNetworkInterfaces", "ec2:DescribeSubnets", "ec2:UnassignPrivateIpAddresses"]
          Resource = "*"
        },
        {
          Sid       = "SinApisDeEc2DesdeElCodigo"
          Effect    = "Deny"
          Action    = ["ec2:AssignPrivateIpAddresses", "ec2:CreateNetworkInterface", "ec2:DeleteNetworkInterface", "ec2:DescribeNetworkInterfaces", "ec2:DescribeSubnets", "ec2:DetachNetworkInterface", "ec2:UnassignPrivateIpAddresses"]
          Resource  = "*"
          Condition = { ArnEquals = { "lambda:SourceFunctionArn" = "arn:aws:lambda:us-east-2:123456789012:function:blog-prod-ejecutor" } }
        },
        {
          Sid      = "RegistrosDeLaEjecutora"
          Effect   = "Allow"
          Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
          Resource = "arn:aws:logs:us-east-2:123456789012:log-group:/aws/lambda/blog-prod-ejecutor:log-stream:*"
        },
      ]
    })
    error_message = "Politica EXACTA de H-031-5: ENI de Lambda en VPC, su Deny desde el codigo y logs del propio grupo. Nada mas."
  }

  assert {
    condition = alltrue(flatten([
      for sentencia in output.configuracion_efectiva.rol.permisos.Statement : [
        for accion in flatten([sentencia.Action]) :
        !anytrue([for prefijo in ["ssm:", "kms:", "s3:", "rds:", "rds-db:", "secretsmanager:", "iam:", "lambda:", "sts:"] : startswith(accion, prefijo)])
      ]
    ]))
    error_message = "H-031-5 no concede SSM, KMS, S3, RDS, Secrets Manager, IAM, Lambda ni STS."
  }

  assert {
    condition     = output.nombre == "blog-prod-ejecutor"
    error_message = "El modulo publica el nombre de la ejecutora, contrato de H-031-6 y Task/038."
  }
}

# Con el cableado fuera del root, la primera barrera contra un artefacto distinto del declarado es la precondicion de
# la funcion; la validacion de la variable del root vuelve con el cableado.
run "ejecutora_zip_con_digest_distinto_rechazado" {
  command = plan

  module {
    source = "../terraform/modulos/ejecutor_privado"
  }

  variables {
    sha256_del_zip = "0000000000000000000000000000000000000000000000000000000000000000"
  }

  expect_failures = [aws_lambda_function.this]
}
