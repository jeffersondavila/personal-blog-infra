output "nombre" {
  value       = aws_lambda_function.this.function_name
  description = "Nombre de la ejecutora: se invoca por el plano de control (`lambda:InvokeFunction`)."
}

output "arn" {
  value       = aws_lambda_function.this.arn
  description = "ARN de la ejecutora. Contrato de Task/038, cuyo rol de despliegue la invocara."
}

# Contrato de VERIFICACION, como el de la red y el de la base de datos: permite a
# las pruebas offline y al readback afirmar sobre lo declarado. No lleva secretos:
# la ejecutora de H-031-5 no tiene ninguno.
output "configuracion_efectiva" {
  description = "Configuracion declarada de la ejecutora, para pruebas y readback."
  value = {
    funcion = {
      nombre                 = aws_lambda_function.this.function_name
      runtime                = aws_lambda_function.this.runtime
      arquitecturas          = aws_lambda_function.this.architectures
      handler                = aws_lambda_function.this.handler
      paquete                = aws_lambda_function.this.package_type
      memoria                = aws_lambda_function.this.memory_size
      timeout                = aws_lambda_function.this.timeout
      publicar               = aws_lambda_function.this.publish
      concurrencia_reservada = aws_lambda_function.this.reserved_concurrent_executions
      hash_del_codigo        = aws_lambda_function.this.source_code_hash
      subredes               = toset(aws_lambda_function.this.vpc_config[0].subnet_ids)
      grupos                 = toset(aws_lambda_function.this.vpc_config[0].security_group_ids)
      ipv6                   = aws_lambda_function.this.vpc_config[0].ipv6_allowed_for_dual_stack
      variables_de_entorno   = length(aws_lambda_function.this.environment)
      capas                  = try(length(aws_lambda_function.this.layers), 0)
    }
    rol = {
      nombre        = aws_iam_role.this.name
      ruta          = aws_iam_role.this.path
      sesion_maxima = aws_iam_role.this.max_session_duration
      limite        = aws_iam_role.this.permissions_boundary
      confianza     = jsondecode(aws_iam_role.this.assume_role_policy)
      permisos      = jsondecode(aws_iam_role_policy.this.policy)
    }
    logs = {
      nombre    = aws_cloudwatch_log_group.this.name
      retencion = aws_cloudwatch_log_group.this.retention_in_days
    }
  }
}
output "nombre_del_rol" {
  value       = aws_iam_role.this.name
  description = "Rol propio al que H-031-6 adjunta la politica restringida de exportacion."
}
