# ---------------------------------------------------------------------------
# Modulo: ejecutor_privado — ejecutora administrativa privada de D-24
#
# Que crea y por que existe
#   La Lambda que alcanza RDS sin ruta publica (D-24, Task/029 §8): en las dos
#   subredes privadas, solo con `sg-admin`, con su rol de ejecucion PROPIO, su
#   grupo de logs y la concurrencia NO reservada de la cuenta (D-24 modificada
#   el 2026-10-18 y aprobada el 2026-10-19). H-031-5 desplego el shell sin base
#   de datos; desde H-031-6 ejecuta el artefacto h0316 (`verify`,
#   `identidades`, `sintetico` y `export`). Los modos de Task/036 siguen
#   `NOT_IMPLEMENTED`.
#
# Lo que NO crea, a proposito
#   - Ninguna credencial: sin SSM, sin KMS, sin variables de entorno y sin
#     cadena de conexion. El operador entrega en el evento de UNA invocacion
#     sincrona solo lo que el modo necesita (mecanismo de H-031-6, §46.2).
#   - Ninguna interfaz publica: sin URL de funcion, sin `aws_lambda_permission`,
#     sin API ni disparadores. Se invoca por el plano de control con IAM del
#     llamador, en la misma cuenta.
#   - Ninguna regla de red: la salida `sg-admin -> S3` del modo `export` la crea
#     el modulo `exportacion` (H-031-6), junto con su politica.
#
# Permisos, derivados de la documentacion de AWS
#   - ENI de Lambda en VPC: la guia de Lambda exige estas seis acciones sobre
#     `Resource: "*"`. Dos, `DescribeNetworkInterfaces` y `DescribeSubnets`, no
#     admiten recurso en la referencia de IAM; las otras cuatro las hace el
#     servicio Lambda en nombre de la funcion. Se compensa con el Deny que AWS
#     recomienda: con `lambda:SourceFunctionArn`, el CODIGO de la funcion no
#     puede usar esas APIs; el servicio si, porque sus llamadas de ENI no llevan
#     esa clave.
#   - Logs: `CreateLogStream` y `PutLogEvents` evaluan contra el recurso
#     `log-stream` (referencia de IAM), asi que se conceden solo sobre los
#     streams del grupo propio. El grupo lo crea Terraform: sin `CreateLogGroup`.
#
# Diferencia conocida con AWS real
#   El emulador no aplica politicas IAM ni crea ENI reales: el laboratorio solo
#   demuestra que la configuracion se declara igual (aws-local-parity.md).
# ---------------------------------------------------------------------------

locals {
  grupo_de_logs = "/aws/lambda/${var.nombre}"

  # ARN construidos y no leidos de recursos: asi la politica se conoce entera en
  # el plan y la guarda de H-031-5 la compara texto a texto.
  arn_de_la_funcion = "arn:aws:lambda:${var.region}:${var.cuenta}:function:${var.nombre}"
  arn_del_grupo     = "arn:aws:logs:${var.region}:${var.cuenta}:log-group:${local.grupo_de_logs}"

  acciones_de_red = [
    "ec2:AssignPrivateIpAddresses",
    "ec2:CreateNetworkInterface",
    "ec2:DeleteNetworkInterface",
    "ec2:DescribeNetworkInterfaces",
    "ec2:DescribeSubnets",
    "ec2:UnassignPrivateIpAddresses",
  ]

  confianza = {
    Version = "2012-10-17"
    Statement = [{
      Sid       = "LambdaAsumeElRolDeLaEjecutora"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  }

  permisos = {
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "InterfacesDeRedDeLambdaEnVpc"
        Effect   = "Allow"
        Action   = local.acciones_de_red
        Resource = "*"
      },
      {
        Sid       = "SinApisDeEc2DesdeElCodigo"
        Effect    = "Deny"
        Action    = sort(concat(local.acciones_de_red, ["ec2:DetachNetworkInterface"]))
        Resource  = "*"
        Condition = { ArnEquals = { "lambda:SourceFunctionArn" = local.arn_de_la_funcion } }
      },
      {
        Sid      = "RegistrosDeLaEjecutora"
        Effect   = "Allow"
        Action   = ["logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "${local.arn_del_grupo}:log-stream:*"
      },
    ]
  }
}

# Creado ANTES que la funcion y con el nombre que Lambda usa: si lo creara el
# servicio, naceria con retencion infinita.
resource "aws_cloudwatch_log_group" "this" {
  name              = local.grupo_de_logs
  retention_in_days = var.dias_de_retencion_de_logs

  tags = {
    Name = var.nombre
  }
}

resource "aws_iam_role" "this" {
  name                 = var.nombre_del_rol
  path                 = "/"
  description          = "Task031 H-031-5 rol de ejecucion propio de la ejecutora privada D-24"
  max_session_duration = 3600
  assume_role_policy   = jsonencode(local.confianza)

  tags = {
    Name = var.nombre_del_rol
  }
}

resource "aws_iam_role_policy" "this" {
  name   = "${var.nombre_del_rol}-ejecucion"
  role   = aws_iam_role.this.id
  policy = jsonencode(local.permisos)
}

resource "aws_lambda_function" "this" {
  function_name = var.nombre
  description   = "Ejecutora privada de administracion de datos (D-24)."
  role          = aws_iam_role.this.arn

  package_type     = "Zip"
  filename         = var.ruta_del_zip
  source_code_hash = filebase64sha256(var.ruta_del_zip)

  handler       = "ejecutor.manejar"
  runtime       = "python3.12"
  architectures = ["x86_64"]
  memory_size   = 128
  timeout       = 30
  publish       = false

  # D-24, modificada el 2026-10-18 (aprobada el 2026-10-19): SIN
  # concurrencia reservada. `reserved_concurrent_executions` se omite a
  # proposito, asi que la funcion usa la concurrencia NO reservada de la cuenta
  # (-1). Ni 0, que la apagaria, ni concurrencia provisionada. La exclusion entre
  # operaciones que escriben la hace la ejecutora con un advisory lock de
  # PostgreSQL (codigo_h0316/operaciones.py); Lambda ya no serializa.

  vpc_config {
    subnet_ids                  = var.ids_de_subredes
    security_group_ids          = [var.id_sg_admin]
    ipv6_allowed_for_dual_stack = false
  }

  tags = {
    Name = var.nombre
  }

  lifecycle {
    precondition {
      condition     = filesha256(var.ruta_del_zip) == var.sha256_del_zip
      error_message = "STOP: el ZIP de la ejecutora no es el artefacto declarado (SHA-256 distinto)."
    }
  }

  # La politica debe existir antes de crear la funcion: Lambda comprueba los
  # permisos de ENI al crearla en la VPC.
  depends_on = [aws_cloudwatch_log_group.this, aws_iam_role_policy.this]
}
