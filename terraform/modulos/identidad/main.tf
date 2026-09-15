# ---------------------------------------------------------------------------
# Modulo: identidad — rol de ejecucion de la funcion Lambda
#
# Que crea y por que existe
#   El rol que la funcion asume al ejecutarse, con una politica en linea acotada a
#   lo que el codigo del backend realmente hace. No hay politica gestionada de
#   AWS adjunta: las del catalogo son mas amplias de lo necesario.
#
# De que depende
#   Del bucket (para acotar el permiso de objeto a su ARN), del grupo de logs y de
#   los ARN de los parametros. La funcion depende de este modulo.
#
# ADVERTENCIA DE PARIDAD — la mas importante de esta tarea
#   El emulador NO aplica politicas IAM por omision: acepta cualesquiera
#   credenciales y deja pasar las peticiones independientemente de lo que diga la
#   politica adjunta (aws-local-parity.md 6.5, riesgo R-28).
#
#   Consecuencia directa: el laboratorio demuestra que este rol SE CREA y que la
#   politica SE ADJUNTA. NO demuestra que autorice correctamente. Un rol con
#   permisos insuficientes —o excesivos— funcionaria igual aqui.
#
#   La verificacion de minimo privilegio es AWS-only y pertenece a Task/028 y
#   Task/032. Este modulo se escribe con minimo privilegio de todas formas,
#   porque es lo que se desplegara en AWS real; pero no se afirma que este
#   probado.
# ---------------------------------------------------------------------------

# Politica de confianza: solo el servicio Lambda puede asumir este rol. Sin
# cuentas externas, sin comodines y sin condiciones que lo ensanchen.
data "aws_iam_policy_document" "confianza" {
  statement {
    sid     = "PermitirQueLambdaAsumaElRol"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ejecucion" {
  name               = var.nombre_del_rol
  description        = "Rol de ejecucion de la funcion del backend del blog."
  assume_role_policy = data.aws_iam_policy_document.confianza.json
}

# Permisos, uno a uno, derivados del codigo del backend. Lo que no esta aqui es
# porque el codigo no lo hace: la funcion no administra IAM, no crea buckets, no
# administra API Gateway, no lee el estado de Terraform y no se despliega a si
# misma.
data "aws_iam_policy_document" "permisos" {
  # Medios: el backend escribe, lee y borra bajo un unico prefijo
  # (app/modules/media/domain/claves.py genera `medios/<uuid4>/...`).
  statement {
    sid    = "ObjetosDeMedios"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
    ]
    resources = ["${var.arn_del_bucket}/${var.prefijo_de_medios}*"]
  }

  # La sonda de disponibilidad de /ready hace ListObjectsV2 con un prefijo fijo
  # (app/shared/storage/s3_compatible.py). El permiso se condiciona a ese
  # prefijo: sin la condicion habria que permitir enumerar el bucket entero, que
  # es precisamente la razon por la que el backend eligio ListObjectsV2 y no
  # HeadBucket.
  statement {
    sid       = "SondaDeDisponibilidad"
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = [var.arn_del_bucket]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["${var.prefijo_de_sonda}*"]
    }
  }

  # Logs: la funcion escribe en su propio grupo. No necesita crear grupos —lo
  # hace Terraform, mas arriba— ni describir los de nadie.
  statement {
    sid    = "EscrituraDeLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["${var.arn_del_grupo_de_logs}:*"]
  }

  # SSM: lectura de los parametros CONCRETOS, nombrados uno a uno. Nunca por
  # comodin sobre una ruta entera.
  #
  # Nota importante: la aplicacion NO lee SSM hoy. Este permiso existe porque los
  # parametros se provisionan y se inspeccionan en el laboratorio, y porque es el
  # permiso que necesitaria el dia que exista un lector. Esta tarea no inventa
  # ese lector.
  dynamic "statement" {
    for_each = length(var.arns_de_parametros) > 0 ? [1] : []

    content {
      sid    = "LecturaDeParametros"
      effect = "Allow"
      actions = [
        "ssm:GetParameter",
        "ssm:GetParameters",
      ]
      resources = var.arns_de_parametros
    }
  }
}

resource "aws_iam_role_policy" "permisos" {
  name   = "${var.nombre_del_rol}-permisos"
  role   = aws_iam_role.ejecucion.id
  policy = data.aws_iam_policy_document.permisos.json
}
