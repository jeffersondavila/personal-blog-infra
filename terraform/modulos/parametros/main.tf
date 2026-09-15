# ---------------------------------------------------------------------------
# Modulo: parametros — SSM Parameter Store
#
# Que crea y por que existe
#   Los parametros de configuracion del servicio. En la arquitectura objetivo
#   (ADR-003) SSM es el origen de la configuracion en la nube, igual que el .env
#   lo es en local.
#
# ACLARACION IMPORTANTE, para no exagerar lo que esto demuestra
#   La aplicacion NO lee SSM hoy. `app/shared/configuration/settings.py` lee
#   variables de entorno con prefijo BLOG_ y nada mas. Este modulo PROVISIONA
#   parametros y el laboratorio los lee con el SDK; eso no convierte a la
#   aplicacion en consumidora de SSM, y esta tarea no inventa ese lector.
#
# Los nombres son PROPUESTOS. No son nombres productivos aprobados.
#
# ADVERTENCIA DE SEGURIDAD
#   El emulador conserva el tipo SecureString pero NO cifra el valor en reposo:
#   no hay nada equivalente a KMS (aws-local-parity.md 6.4). Por eso el control
#   S-07 es absoluto: aqui solo entran valores ficticios. Que un parametro figure
#   como SecureString en el laboratorio NO demuestra que este protegido.
# ---------------------------------------------------------------------------

resource "aws_ssm_parameter" "configuracion" {
  for_each = var.parametros

  name  = "${var.prefijo_de_ruta}/${each.key}"
  type  = each.value.seguro ? "SecureString" : "String"
  value = each.value.valor

  # El valor de un parametro no es infraestructura: puede rotarse fuera de
  # Terraform sin que eso sea drift que haya que revertir. Lo que Terraform
  # posee es la EXISTENCIA del parametro y su tipo.
  lifecycle {
    ignore_changes = [value]
  }
}
