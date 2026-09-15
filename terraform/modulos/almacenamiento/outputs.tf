output "nombre" {
  value       = aws_s3_bucket.medios.id
  description = "Nombre del bucket de medios."
}

output "arn" {
  value       = aws_s3_bucket.medios.arn
  description = "ARN del bucket, consumido por la politica del rol de ejecucion."
}
