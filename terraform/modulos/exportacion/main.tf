# Capacidad `export` de la ejecutora privada de D-24 (Task/031 H-031-6; D-10 §10.1, D-24 §8.2).
#
# Dos recursos y nada mas:
# - Una politica inline en el rol PROPIO de la ejecutora: `s3:PutObject` SOLO sobre el prefijo dedicado del bucket
#   de medios, SOLO como escritura condicional (`If-None-Match: *`, una exportacion nunca pisa otra) y SOLO a traves
#   del gateway endpoint de la VPC. Ni lectura, ni listado, ni borrado, ni el prefijo `medios/` de la aplicacion.
# - La salida HTTPS de `sg-admin` hacia S3 por la prefix list del gateway endpoint: sin NAT y sin CIDR.
#
# El prefijo es una constante, no una variable: es el mismo literal que `PREFIJO` en
# `codigo_h0316/exportacion.py`, y una prueba exige que coincidan.
#
# NO lo llama ningun root todavia: entra en `terraform-datos` cuando exista la ejecutora (H-031-5 espera la cuota
# de concurrencia de Lambda). Hasta entonces el plan revisado de H-031-5 no cambia.

locals {
  prefijo = "exportaciones/"

  # La politica vive en una plantilla: la misma que renderizan las pruebas offline para simular sus decisiones
  # (`tests/terraform_datos/test_politicas_de_las_fases.py`) y despues `simulate-custom-policy` contra AWS.
  politica = jsondecode(templatefile("${path.module}/politica.json.tftpl", {
    arn_del_bucket     = var.arn_del_bucket
    prefijo            = local.prefijo
    id_del_endpoint_s3 = var.id_del_endpoint_s3
  }))
}

resource "aws_iam_role_policy" "this" {
  name   = "${var.nombre_del_rol}-exportacion"
  role   = var.nombre_del_rol
  policy = jsonencode(local.politica)
}

resource "aws_vpc_security_group_egress_rule" "admin_a_s3" {
  security_group_id = var.id_sg_admin
  prefix_list_id    = var.prefix_list_s3
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  description       = "HTTPS hacia S3 por el gateway endpoint (modo export de D-24)"

  tags = {
    Name = "${var.nombre}-admin-a-s3"
  }
}
