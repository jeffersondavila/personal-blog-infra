# Custodia de las credenciales SQL de la aplicacion y de las migraciones (Task/031 H-031-6; D-23 §5.3).
#
# `blog_migrate` y `blog_app` tienen contrasenas distintas y rotacion independiente. Como la master, su UNICA
# custodia es un SecureString estandar con la clave administrada `alias/aws/ssm`, escrito con `value_wo`: el valor no
# llega ni al plan ni al state (DH-2). Se genera en memoria en el proceso que ejecuta Terraform y llega solo por
# entorno; el operador calcula de ese mismo valor el verificador SCRAM que recibe la ejecutora (`identidades`), asi
# que la contrasena tampoco llega a la funcion ni al log de PostgreSQL.
#
# NO lo llama ningun root todavia: entra en `terraform-datos` con H-031-6, cuando exista la ejecutora (H-031-5 espera
# la cuota de concurrencia de Lambda).

resource "aws_ssm_parameter" "blog_migrate" {
  name             = "${var.ruta_base}/blog_migrate"
  description      = "Contrasena de blog_migrate: migraciones, purga y export por la ejecutora de D-24 (D-23)."
  type             = "SecureString"
  tier             = "Standard"
  key_id           = "alias/aws/ssm"
  value_wo         = var.contrasena_blog_migrate
  value_wo_version = var.version_de_blog_migrate

  tags = {
    Name = "${var.nombre}-blog-migrate"
  }
}

resource "aws_ssm_parameter" "blog_app" {
  name             = "${var.ruta_base}/blog_app"
  description      = "Contrasena de blog_app: la aplicacion en Lambda, solo DML (D-23)."
  type             = "SecureString"
  tier             = "Standard"
  key_id           = "alias/aws/ssm"
  value_wo         = var.contrasena_blog_app
  value_wo_version = var.version_de_blog_app

  tags = {
    Name = "${var.nombre}-blog-app"
  }
}
