# ---------------------------------------------------------------------------
# personal-blog-infra — Terraform: configuracion del provider (Task/025)
#
# Este archivo es el UNICO lugar donde el destino cambia. Los modulos y los
# recursos son identicos para el laboratorio local y para AWS real: es la regla
# de portabilidad de docs/architecture/aws-local-parity.md, seccion 4.
#
# Las diferencias que viven aqui estan en la tabla de diferencias LEGITIMAS de
# ese documento (seccion 4.4, filas 1, 2, 3 y 5):
#
#   1. bloque `endpoints`  -> null contra AWS; endpoint local en el laboratorio
#   2. flags `skip_*`      -> solo en el laboratorio
#   3. credenciales        -> por entorno, nunca en Git
#   5. region              -> variable
#
# Las credenciales NO se declaran aqui: las aporta el entorno que construye
# scripts/laboratorio/destino.py, con valores ficticios exactos para el
# laboratorio (controles S-04 y S-05). Con `laboratorio = false` el provider usa
# la cadena de credenciales normal del SDK, que en produccion es el rol que
# corresponda.
# ---------------------------------------------------------------------------

provider "aws" {
  region = var.region

  # Contra AWS real las cinco quedan en false y el provider se comporta como de
  # costumbre. En el laboratorio se activan porque el emulador no implementa la
  # validacion de credenciales, no expone metadata de instancia y direcciona S3
  # por ruta.
  skip_credentials_validation = var.laboratorio
  skip_metadata_api_check     = var.laboratorio
  skip_requesting_account_id  = var.laboratorio
  skip_region_validation      = var.laboratorio
  s3_use_path_style           = var.laboratorio

  # Un unico bloque `endpoints`: con todos los atributos en null el provider
  # resuelve los endpoints de AWS igual que si el bloque no existiera. Asi el
  # destino es un valor de variable y no una bifurcacion del codigo, que es lo
  # que prohibe el riesgo R-26.
  endpoints {
    apigatewayv2 = var.endpoints_aws.apigatewayv2
    cloudwatch   = var.endpoints_aws.cloudwatch
    iam          = var.endpoints_aws.iam
    lambda       = var.endpoints_aws.lambda
    logs         = var.endpoints_aws.logs
    s3           = var.endpoints_aws.s3
    ssm          = var.endpoints_aws.ssm
    sts          = var.endpoints_aws.sts
  }

  default_tags {
    tags = var.etiquetas
  }
}
