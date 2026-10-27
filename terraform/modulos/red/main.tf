# ---------------------------------------------------------------------------
# Modulo: red — VPC privada para RDS y para las Lambdas que la alcancen
#
# Que crea y por que existe
#   La red dedicada de D-22 (Task/029): una VPC, dos subredes PRIVADAS en dos AZ,
#   una tabla de rutas por subred, el gateway endpoint de S3 y los tres grupos de
#   seguridad que separan a quien llama a la base de datos de la base de datos.
#   ADR-010 exige PostgreSQL privado; esta es la red que lo hace posible.
#
# Lo que NO crea, a proposito
#   Internet Gateway, NAT Gateway, Elastic IP, subredes publicas, IPv6 ni rutas
#   0.0.0.0/0. El inventario A-E de Task/029 dejo la clase D —Internet publico—
#   VACIA: no hay destino que justifique salida. Las tablas de rutas solo tienen
#   la ruta `local` y la que anade el endpoint de S3.
#
# De que depende
#   De nada dentro del grafo. Recibe por variable el ARN del bucket de medios,
#   que administra OTRO root (`terraform-medios`): contrato explicito, sin
#   `terraform_remote_state`.
#
# Que produce
#   Los identificadores que consumen la base de datos (subredes y `sg-rds`), la
#   ejecutora de D-24 (`sg-admin`, Task/031 H-031-5) y la Lambda de aplicacion
#   (`sg-lambda`, Task/032). Crear `sg-lambda` aqui NO conecta ninguna funcion a
#   la VPC: eso es `vpc_config`, y es de Task/032.
#
# Diferencia conocida con AWS real
#   Ninguna regla de este modulo prueba aislamiento en el laboratorio: un
#   emulador acepta la definicion sin evaluar el trafico. El aislamiento real es
#   AWS-only (matriz de paridad, aws-local-parity.md §7).
# ---------------------------------------------------------------------------

resource "aws_vpc" "this" {
  cidr_block = var.cidr

  # El endpoint de RDS se resuelve por DNS y su IP privada puede cambiar tras un
  # failover o un restore: la documentacion de RDS desaconseja conectar por IP.
  enable_dns_support   = true
  enable_dns_hostnames = true

  # Explicito: sin IPv6 (D-22 §4). Lambda solo saldria por IPv6 con todas sus
  # subredes dual-stack, y eso anade superficie para un problema que no existe.
  assign_generated_ipv6_cidr_block = false

  tags = {
    Name = "${var.nombre}-vpc"
  }
}

# El grupo POR OMISION de la VPC no se gestiona (H-031-1A). AWS lo crea con la
# VPC y permite el trafico entre sus miembros, pero NADA lo usa: RDS lleva
# `sg-rds`, y las dos Lambdas llevaran `sg-lambda` (Task/032) y `sg-admin`
# (H-031-5), siempre de forma explicita. El aislamiento se preserva por NO USO.
#
# Gestionarlo exigia al rol operativo etiquetar un grupo sin etiquetas del
# proyecto y retirarle reglas: un permiso sobre recursos que no son propios, que
# el usuario rechazo. Las pruebas y la guarda del plan exigen que ningun recurso
# del proyecto lo referencie.

resource "aws_subnet" "privada" {
  for_each = var.subredes

  vpc_id               = aws_vpc.this.id
  cidr_block           = each.value.cidr
  availability_zone_id = each.value.zona_id

  # Explicito aunque sea el valor por omision: una subred privada no reparte IP
  # publicas, y sin Internet Gateway tampoco tendrian adonde ir.
  map_public_ip_on_launch = false

  tags = {
    Name = "${var.nombre}-privada-${each.key}"
  }
}

# Sin bloques `route`: el atributo es computado, y declararlo vacio haria que
# Terraform retirara las rutas que el gateway endpoint anade a estas tablas.
# Ninguna tabla lleva ruta por defecto.
resource "aws_route_table" "privada" {
  for_each = var.subredes

  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.nombre}-privada-${each.key}"
  }
}

resource "aws_route_table_association" "privada" {
  for_each = var.subredes

  subnet_id      = aws_subnet.privada[each.key].id
  route_table_id = aws_route_table.privada[each.key].id
}

# Gateway endpoint de S3: el unico camino de la VPC hacia S3, sin tarifa de
# endpoint y sin NAT. Su politica limita QUE buckets se alcanzan por el; los
# permisos de cada identidad siguen siendo los de su propia politica IAM.
#
# No toca la politica del bucket de medios. Un `Deny` por `aws:SourceVpce` en el
# bucket romperia las URL prefirmadas del navegador, que no entra por la VPC
# (D-08, Task/030): por eso la restriccion vive aqui y no alli.
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.this.id
  service_name      = var.nombre_del_servicio_s3
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [for clave in sort(keys(var.subredes)) : aws_route_table.privada[clave].id]
  policy            = jsonencode(local.politica_del_endpoint)

  tags = {
    Name = "${var.nombre}-s3"
  }
}

locals {
  # Acciones que hoy hacen red hacia S3 desde la VPC: las de `S3Storage`
  # (put/get/head/delete y la sonda `ListObjectsV2` de `/ready`) y la escritura
  # del modo `export` de D-24. `HeadObject` se autoriza con `s3:GetObject`.
  politica_del_endpoint = {
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "ObjetosDeLosBucketsDelProyecto"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource  = [for arn in var.arns_de_buckets_permitidos : "${arn}/*"]
      },
      {
        Sid       = "ListadoDeLosBucketsDelProyecto"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:ListBucket"]
        Resource  = var.arns_de_buckets_permitidos
      },
    ]
  }
}

# --- Grupos de seguridad ----------------------------------------------------
#
# Tres grupos y reglas SOLO por referencia de grupo o por prefix list. Nunca un
# CIDR y nunca 0.0.0.0/0: si las subredes cambian la regla sigue siendo
# correcta, y ningun rango entra por coincidencia de direcciones.
#
# Terraform retira la regla de salida "todo permitido" que AWS anade a un grupo
# nuevo, asi que `sg-rds` queda sin ninguna salida: una base de datos no inicia
# conexiones.

resource "aws_security_group" "lambda" {
  name        = "${var.nombre}-lambda"
  description = "Lambda de aplicacion (Task/032): sale a RDS y a S3, no recibe nada"
  vpc_id      = aws_vpc.this.id

  tags = {
    Name = "${var.nombre}-lambda"
  }
}

resource "aws_security_group" "rds" {
  name        = "${var.nombre}-rds"
  description = "RDS PostgreSQL privado: solo recibe 5432 desde lambda y admin"
  vpc_id      = aws_vpc.this.id

  tags = {
    Name = "${var.nombre}-rds"
  }
}

resource "aws_security_group" "admin" {
  name        = "${var.nombre}-admin"
  description = "Ejecutora privada D-24 (Task/031 H-031-5): sale a RDS"
  vpc_id      = aws_vpc.this.id

  tags = {
    Name = "${var.nombre}-admin"
  }
}

resource "aws_vpc_security_group_ingress_rule" "rds_desde_lambda" {
  security_group_id            = aws_security_group.rds.id
  referenced_security_group_id = aws_security_group.lambda.id
  ip_protocol                  = "tcp"
  from_port                    = var.puerto_de_la_base
  to_port                      = var.puerto_de_la_base
  description                  = "PostgreSQL desde la Lambda de aplicacion"

  tags = {
    Name = "${var.nombre}-rds-desde-lambda"
  }
}

resource "aws_vpc_security_group_ingress_rule" "rds_desde_admin" {
  security_group_id            = aws_security_group.rds.id
  referenced_security_group_id = aws_security_group.admin.id
  ip_protocol                  = "tcp"
  from_port                    = var.puerto_de_la_base
  to_port                      = var.puerto_de_la_base
  description                  = "PostgreSQL desde la ejecutora privada"

  tags = {
    Name = "${var.nombre}-rds-desde-admin"
  }
}

resource "aws_vpc_security_group_egress_rule" "lambda_a_rds" {
  security_group_id            = aws_security_group.lambda.id
  referenced_security_group_id = aws_security_group.rds.id
  ip_protocol                  = "tcp"
  from_port                    = var.puerto_de_la_base
  to_port                      = var.puerto_de_la_base
  description                  = "PostgreSQL hacia RDS"

  tags = {
    Name = "${var.nombre}-lambda-a-rds"
  }
}

resource "aws_vpc_security_group_egress_rule" "lambda_a_s3" {
  security_group_id = aws_security_group.lambda.id
  prefix_list_id    = aws_vpc_endpoint.s3.prefix_list_id
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  description       = "HTTPS hacia S3 por el gateway endpoint"

  tags = {
    Name = "${var.nombre}-lambda-a-s3"
  }
}

resource "aws_vpc_security_group_egress_rule" "admin_a_rds" {
  security_group_id            = aws_security_group.admin.id
  referenced_security_group_id = aws_security_group.rds.id
  ip_protocol                  = "tcp"
  from_port                    = var.puerto_de_la_base
  to_port                      = var.puerto_de_la_base
  description                  = "PostgreSQL hacia RDS"

  tags = {
    Name = "${var.nombre}-admin-a-rds"
  }
}

# La salida HTTPS de `sg-admin` hacia S3, que necesitara el modo `export`, NO va
# aqui. H-031-1 la asigno a H-031-5, y H-031-5 la difirio al checkpoint que
# implemente `export`: no se concede conectividad antes de que un modo real la
# use (Task/031, reporte §44).
