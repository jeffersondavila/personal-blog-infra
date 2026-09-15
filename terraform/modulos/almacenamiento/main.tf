# ---------------------------------------------------------------------------
# Modulo: almacenamiento — bucket S3 de medios
#
# Que crea y por que existe
#   El bucket donde el backend guarda los medios del blog. En local lo sustituye
#   MinIO a traves de la MISMA interfaz ObjectStorage (Task/010), asi que la
#   aplicacion no distingue uno de otro: cambia configuracion, no codigo.
#
# De que depende
#   De nada. Es la hoja del grafo: el rol de la funcion (modulo identidad) y la
#   propia funcion dependen de el, no al contrario.
#
# Que produce
#   El nombre y el ARN del bucket, que consumen el rol de ejecucion —para acotar
#   sus permisos— y las variables de entorno de la funcion.
#
# Diferencia conocida con AWS real
#   El bloqueo de acceso publico a nivel de CUENTA es un control de AWS, no un
#   rasgo del protocolo S3: el emulador puede aceptar la configuracion del bucket
#   sin que exista el control de cuenta detras. La verificacion real es de
#   Task/030.
# ---------------------------------------------------------------------------

resource "aws_s3_bucket" "medios" {
  bucket = var.nombre

  # El laboratorio se destruye y se reconstruye en cada ciclo: sin esto, un
  # bucket con objetos de prueba impediria el destroy y la evidencia de
  # reconstruccion no se podria producir. Contra AWS real este valor se declara
  # en el tfvars del destino y NO tiene por que ser true.
  force_destroy = var.forzar_destruccion
}

# El bucket es privado. No se usa ACL: `BucketOwnerEnforced` las desactiva, que
# es la recomendacion actual de AWS y evita el modo en que un objeto subido por
# otra identidad conserva un dueno distinto.
resource "aws_s3_bucket_ownership_controls" "medios" {
  bucket = aws_s3_bucket.medios.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# Las cuatro banderas, explicitas. No se confia en el valor por omision de la
# cuenta: un bucket de medios nunca debe ser publico, y esto lo deja escrito.
resource "aws_s3_bucket_public_access_block" "medios" {
  bucket = aws_s3_bucket.medios.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "medios" {
  bucket = aws_s3_bucket.medios.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Cifrado en reposo con la clave gestionada por S3. No se introduce KMS: no hay
# ninguna decision que lo autorice y anadirlo tendria costo en AWS real.
resource "aws_s3_bucket_server_side_encryption_configuration" "medios" {
  bucket = aws_s3_bucket.medios.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# CORS explicito: la lista de origenes viene del destino y nunca es el comodin.
# Con la lista vacia no se crea el recurso, que es lo correcto cuando ningun
# navegador va a leer objetos directamente.
resource "aws_s3_bucket_cors_configuration" "medios" {
  count  = length(var.origenes_cors) > 0 ? 1 : 0
  bucket = aws_s3_bucket.medios.id

  cors_rule {
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = var.origenes_cors
    allowed_headers = ["*"]
    expose_headers  = ["ETag", "Content-Length", "Content-Type"]
    max_age_seconds = 300
  }
}

# Politica que NIEGA cualquier acceso sin TLS. Es una regla de bucket, no de
# identidad: aplica tambien a quien tenga permisos.
#
# No concede nada a nadie: los permisos del rol viven en el modulo identidad.
resource "aws_s3_bucket_policy" "medios" {
  bucket = aws_s3_bucket.medios.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "NegarTransporteInseguro"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.medios.arn,
          "${aws_s3_bucket.medios.arn}/*",
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      },
    ]
  })

  # Sin esta dependencia, la politica puede aplicarse antes que el bloqueo de
  # acceso publico y AWS rechazarla.
  depends_on = [aws_s3_bucket_public_access_block.medios]
}

# Ciclo de vida de las versiones antiguas y de las subidas incompletas.
#
# ADVERTENCIA de evidencia: que este recurso exista demuestra que la
# configuracion SE ACEPTA, no que una version haya expirado. Un vencimiento tarda
# dias y no se puede observar en un ciclo de laboratorio; afirmar lo contrario
# seria inventar evidencia.
resource "aws_s3_bucket_lifecycle_configuration" "medios" {
  bucket = aws_s3_bucket.medios.id

  rule {
    id     = "expirar-versiones-antiguas"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = var.dias_para_expirar_versiones
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  depends_on = [aws_s3_bucket_versioning.medios]
}
