# ---------------------------------------------------------------------------
# personal-blog-infra — root de ALMACENAMIENTO DE MEDIOS
#
# Enmienda de Task/030 al diseno de Task/025 (autorizada como
# `H-030-4-root-medios`). El bucket de medios deja de pertenecer al lifecycle y
# al state del grafo de aplicacion y pasa a este root propio.
#
# Por que un root y no un modulo mas del grafo de aplicacion
#   El bucket es almacenamiento PERSISTENTE: sobrevive a cada despliegue de la
#   funcion, de la API y de los parametros, y su destruccion accidental pierde
#   datos que ningun `apply` reconstruye. Compartir state con recursos que se
#   recrean en cada ciclo acopla dos lifecycles que no tienen nada que ver.
#
# Que NO es esto
#   No es una segunda definicion del bucket. Este root **reutiliza** el modulo
#   `../terraform/modulos/almacenamiento` por `source`: los recursos `aws_s3_*`
#   existen una sola vez en el repositorio. Local y AWS real usan ESTE mismo root
#   con el mismo modulo; lo unico que cambia es el archivo de destino.
#
# Aqui NO hay bloque `backend`: su TIPO no se puede cambiar con
# -backend-config, asi que se genera junto a este archivo antes de `init`, igual
# que en el grafo de aplicacion (decision D-06). Para AWS real el destino es el
# backend S3 del bucket de state, con la key `application/media/terraform.tfstate`.
# ---------------------------------------------------------------------------

terraform {
  required_version = "= 1.16.2"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.64.0"
    }
  }
}
