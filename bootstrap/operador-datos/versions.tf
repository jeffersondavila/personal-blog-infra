# ---------------------------------------------------------------------------
# Bootstrap de la IDENTIDAD OPERATIVA de Task/031 — DISENO, NO APLICADO
#
# H-031-1 (DH-3) rechazo operar red y RDS con `PersonalBlogAdministrator`. Este
# root define la identidad humana operativa MINIMA que lo hara:
# `PersonalBlogDataOperator`. La administrativa solo interviene como BOOTSTRAP
# de esta identidad, en el checkpoint separado H-031-IAM; despues, cualquier
# operacion de Task/031 con ella es STOP.
#
# Mismo patron que `bootstrap/github-oidc`: root independiente, state propio en
# el bucket de D-06 (key `bootstrap/operador-datos/terraform.tfstate`), lock
# nativo, sin DynamoDB. NADA de este root se ha aplicado: H-031-1 solo autoriza
# el diseno.
# ---------------------------------------------------------------------------

terraform {
  required_version = "= 1.16.2"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.70.0"
    }
  }
  # D-06: configuracion parcial desde el directorio privado del operador.
  backend "s3" {}
}
