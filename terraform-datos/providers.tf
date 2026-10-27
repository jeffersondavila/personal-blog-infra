# ---------------------------------------------------------------------------
# Provider del root de datos.
#
# Mismo patron que `terraform/providers.tf` y `terraform-medios/providers.tf`:
# el destino vive AQUI y solo aqui. Las diferencias son las legitimas de
# aws-local-parity.md §4.4 —endpoints, flags `skip_*`, credenciales y region—,
# no una bifurcacion del grafo.
#
# Solo se declaran los endpoints que este root usa: `ec2` (VPC, subredes, rutas,
# grupos y endpoint se crean por la API de EC2), `rds`, `ssm` (custodia de la
# contrasena master), `logs` (grupos de PostgreSQL y de la ejecutora), `sts`
# (comprobacion de identidad), desde H-031-5 `iam` y `lambda` (la ejecutora
# privada de D-24, fuera del root hasta la cuota de Lambda) y desde H-031-8
# `cloudwatch` (alarmas de D-11). `iam` sirve tambien al rol de D-20.
#
# Las credenciales no se declaran: las aporta el entorno. Contra AWS real, la
# identidad debe ser una sesion del rol operativo minimo de Task/031, nunca la
# administrativa (H-031-1, DH-3): lo exige la postcondicion de `main.tf`.
# ---------------------------------------------------------------------------

provider "aws" {
  region = var.region

  allowed_account_ids = var.cuentas_permitidas

  skip_credentials_validation = var.laboratorio
  skip_metadata_api_check     = var.laboratorio
  skip_region_validation      = var.laboratorio

  # A diferencia de los otros dos roots, este SI pide su cuenta tambien en el
  # laboratorio (el STS del emulador responde). Sin ella, el provider no puede
  # saber que el grupo referenciado por una regla es de la misma cuenta y lo
  # escribe como `<cuenta>/sg-...`: un drift perpetuo que AWS real no tiene.
  # Hallazgo de H-031-1; asi el laboratorio se parece MAS a produccion.
  skip_requesting_account_id = false

  endpoints {
    ec2        = var.endpoints_aws.ec2
    rds        = var.endpoints_aws.rds
    ssm        = var.endpoints_aws.ssm
    logs       = var.endpoints_aws.logs
    sts        = var.endpoints_aws.sts
    iam        = var.endpoints_aws.iam
    lambda     = var.endpoints_aws.lambda
    cloudwatch = var.endpoints_aws.cloudwatch
  }

  default_tags {
    tags = var.etiquetas
  }
}
