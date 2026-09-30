output "nombre" {
  value       = aws_s3_bucket.medios.id
  description = "Nombre del bucket de medios."
}

output "arn" {
  value       = aws_s3_bucket.medios.arn
  description = "ARN del bucket, consumido por la politica del rol de ejecucion."
}

# Contrato de VERIFICACION. Existe para que las pruebas offline puedan afirmar
# sobre la configuracion realmente aplicada sin alcanzar recursos internos del
# modulo, que no estan en el ambito del root. No transporta ningun secreto: son
# los mismos valores que ya viven en el codigo.
output "configuracion_efectiva" {
  description = "Configuracion aplicada al bucket, para las pruebas y el readback."
  value = {
    nombre        = aws_s3_bucket.medios.id
    force_destroy = aws_s3_bucket.medios.force_destroy
    tags          = aws_s3_bucket.medios.tags
    versionado    = aws_s3_bucket_versioning.medios.versioning_configuration[0].status
    cifrado       = one(one(aws_s3_bucket_server_side_encryption_configuration.medios.rule).apply_server_side_encryption_by_default).sse_algorithm
    ownership     = one(aws_s3_bucket_ownership_controls.medios.rule).object_ownership
    bpa = {
      block_public_acls       = aws_s3_bucket_public_access_block.medios.block_public_acls
      block_public_policy     = aws_s3_bucket_public_access_block.medios.block_public_policy
      ignore_public_acls      = aws_s3_bucket_public_access_block.medios.ignore_public_acls
      restrict_public_buckets = aws_s3_bucket_public_access_block.medios.restrict_public_buckets
    }
    policy = aws_s3_bucket_policy.medios.policy
    lifecycle = {
      dias_de_versiones_no_actuales = one(one(aws_s3_bucket_lifecycle_configuration.medios.rule).noncurrent_version_expiration).noncurrent_days
      dias_para_abortar_multipart   = one(one(aws_s3_bucket_lifecycle_configuration.medios.rule).abort_incomplete_multipart_upload).days_after_initiation
    }
    reglas_cors = length(aws_s3_bucket_cors_configuration.medios)
  }
}
