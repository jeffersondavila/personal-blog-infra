locals {
  cuenta = var.expected_account_id
  region = var.aws_region

  # Mismo nombre deterministico que fija `bootstrap/terraform-state`: el bucket
  # de state de D-06. No se pide por variable para que no pueda apuntar a otro.
  bucket_de_estado = format(
    "personal-blog-tfstate-us-east-2-%s",
    substr(sha256("personal-blog:terraform-state:${local.cuenta}:us-east-2"), 0, 12)
  )

  # Las claves de etiqueta que el root de datos aplica: `default_tags` + `Name`.
  claves_de_etiqueta = ["Componente", "Entorno", "Gestion", "Name", "Proyecto", "Tarea"]

  # El trust nombra al usuario de entrada por ARN EXACTO y exige MFA, igual que
  # el de `PersonalBlogAdministrator` (Task/027). Sin raiz de cuenta, sin
  # comodines, sin federacion.
  trust = {
    Version = "2012-10-17"
    Statement = [{
      Sid       = "UsuarioDeEntradaConMfa"
      Effect    = "Allow"
      Principal = { AWS = "arn:aws:iam::${local.cuenta}:user/${var.usuario_de_entrada}" }
      Action    = "sts:AssumeRole"
      Condition = { Bool = { "aws:MultiFactorAuthPresent" = "true" } }
    }]
  }

  # Fase 1 —red y datos—, la UNICA que H-031-IAM concede. Las plantillas son la
  # fuente unica: la revision humana, Terraform y la guarda leen el mismo texto.
  # Las fases 2 a 5 (ejecutora, identidades SQL, restore, alarmas) se anaden en
  # sus propios checkpoints de IAM; ver docs/architecture/identidad-operativa-datos.md.
  #
  # Tres politicas ADMINISTRADAS: H-031-1 superaba el limite agregado de las
  # inline (10 240); H-031-1A conserva la separacion tras reducir permisos. Partirla
  # por servicio mantiene cada sentencia identica —sin comodines nuevos— y cada
  # politica bajo su limite de 6 144. La prueba offline lo vigila.
  variables_de_plantilla = {
    cuenta             = local.cuenta
    region             = local.region
    bucket_de_estado   = local.bucket_de_estado
    claves_de_etiqueta = jsonencode(local.claves_de_etiqueta)
  }
  politicas_fase_1 = {
    for nombre, archivo in {
      Red          = "fase-1-red.json.tftpl"
      RdsYCustodia = "fase-1-rds-y-custodia.json.tftpl"
      Denegaciones = "fase-1-denegaciones.json.tftpl"
    } : nombre => jsondecode(templatefile("${path.module}/politicas/${archivo}", local.variables_de_plantilla))
  }
}

resource "aws_iam_role" "operador_datos" {
  name                 = "PersonalBlogDataOperator"
  path                 = "/"
  description          = "Task031 identidad operativa minima: red y RDS privados en us-east-2"
  max_session_duration = 3600
  assume_role_policy   = jsonencode(local.trust)

  # Sin permissions boundary: este rol no puede crear identidades (lo deniega su
  # propia politica), asi que un boundary no acotaria nada que no este acotado.
  depends_on = [data.aws_caller_identity.bootstrap]

  tags = {
    Proyecto   = "personal-blog"
    Entorno    = "produccion"
    Gestion    = "terraform"
    Componente = "identidad-operativa"
    Tarea      = "Task/031"
  }

  lifecycle {
    prevent_destroy = true
  }
}

# Politicas administradas bajo una ruta propia, adjuntas SOLO a este rol. El rol
# no puede adjuntarlas a otra identidad: la denegacion `iam:Attach*` es suya.
resource "aws_iam_policy" "fase_1" {
  for_each = local.politicas_fase_1

  name        = "PersonalBlogOperadorDatosFase1${each.key}"
  path        = "/personal-blog/"
  description = "Task031 fase 1 (${each.key}) de la identidad operativa minima de red y RDS"
  policy      = jsonencode(each.value)

  tags = {
    Proyecto   = "personal-blog"
    Entorno    = "produccion"
    Gestion    = "terraform"
    Componente = "identidad-operativa"
    Tarea      = "Task/031"
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_iam_role_policy_attachment" "fase_1" {
  for_each = aws_iam_policy.fase_1

  role       = aws_iam_role.operador_datos.name
  policy_arn = each.value.arn

  lifecycle {
    prevent_destroy = true
  }
}

# El primer `CreateDBInstance` de la cuenta crea `AWSServiceRoleForRDS` si no
# existe, y para eso pediria `iam:CreateServiceLinkedRole` al operador. En lugar
# de concederselo, lo crea el bootstrap, de forma explicita y revisada. Si el
# preflight lo encuentra ya creado, no se gestiona ni se importa.
resource "aws_iam_service_linked_role" "rds" {
  count            = var.crear_rol_vinculado_de_rds ? 1 : 0
  aws_service_name = "rds.amazonaws.com"
  depends_on       = [data.aws_caller_identity.bootstrap]

  lifecycle {
    prevent_destroy = true
  }
}
