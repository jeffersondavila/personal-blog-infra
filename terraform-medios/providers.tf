# ---------------------------------------------------------------------------
# Provider del root de medios.
#
# Es el mismo patron que `terraform/providers.tf`: el destino vive AQUI y solo
# aqui, y los recursos son identicos para el laboratorio y para AWS real. Las
# diferencias son las LEGITIMAS de aws-local-parity.md seccion 4.4 —endpoints,
# flags `skip_*`, credenciales y region—, no una bifurcacion del grafo.
#
# Solo se declaran los endpoints que este root puede llegar a usar: `s3`, porque
# es lo que crea, y `sts`, porque es lo que consulta la comprobacion de identidad.
# Declarar los ocho aqui seria copiar una superficie que este root no toca.
#
# Las credenciales no se declaran: las aporta el entorno. Con
# `laboratorio = false` el provider usa la cadena normal del SDK, que en la
# operacion humana de Task/030 es el perfil revisado.
# ---------------------------------------------------------------------------

provider "aws" {
  region = var.region

  allowed_account_ids = var.cuentas_permitidas

  skip_credentials_validation = var.laboratorio
  skip_metadata_api_check     = var.laboratorio
  skip_requesting_account_id  = var.laboratorio
  skip_region_validation      = var.laboratorio
  s3_use_path_style           = var.laboratorio

  endpoints {
    s3  = var.endpoints_aws.s3
    sts = var.endpoints_aws.sts
  }

  # Mecanismo unico de etiquetado, igual que en el grafo de aplicacion: alcanza a
  # todo recurso taggable sin que cada modulo tenga que recibir el mapa.
  default_tags {
    tags = var.etiquetas
  }
}
