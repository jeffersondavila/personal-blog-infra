# ---------------------------------------------------------------------------
# personal-blog-infra — root de DATOS: red privada + RDS PostgreSQL
#
# Task/031 (`H-031-1`, DH-1). Segundo lifecycle extraido del grafo de
# aplicacion, con el mismo criterio que `terraform-medios` (aws-local-parity.md
# §4.1.1): la red y la base de datos son infraestructura PERSISTENTE —la base
# lleva deletion protection y sus datos no los reconstruye ningun `apply`— y su
# ciclo de vida no es el de la funcion ni el de la API, que se redespliegan.
#
# Enmienda a §12.2 del paquete de decisiones de Task/029, que preveia anadir los
# modulos a `terraform/main.tf`. Ese texto es anterior a §4.1.1 y hoy no es
# viable: planear red y RDS en el root de aplicacion crearia tambien la Lambda y
# la API de Task/032/033, y `-target` esta prohibido. Los modulos conservan los
# nombres del contrato de §12.1 (`modulos/red`, `modulos/base_de_datos`) y viven
# bajo `terraform/modulos/`, igual que el de almacenamiento.
#
# Este root es el UNICO duenno de: VPC, subredes, tablas de rutas, gateway
# endpoint de S3, grupos de seguridad, DB subnet group, parameter group, grupo
# de logs de RDS, instancia RDS y el SecureString de la contrasena master.
#
# Aqui NO hay bloque `backend`: su TIPO no se puede cambiar con
# -backend-config, asi que se genera junto a este archivo antes de `init`
# (decision D-06). En AWS real: backend S3 del bucket de state, key
# `application/data/terraform.tfstate`, `use_lockfile = true`, sin DynamoDB.
# ---------------------------------------------------------------------------

terraform {
  required_version = "= 1.16.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.70.0"
    }
  }
}
