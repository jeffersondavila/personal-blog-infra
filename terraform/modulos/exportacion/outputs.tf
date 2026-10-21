output "prefijo" {
  description = "Prefijo dedicado de exportacion dentro del bucket de medios."
  value       = local.prefijo
}

output "nombre_de_la_politica" {
  description = "Politica inline de exportacion en el rol de la ejecutora."
  value       = aws_iam_role_policy.this.name
}

output "id_de_la_regla" {
  description = "Regla de salida HTTPS de `sg-admin` hacia S3."
  value       = aws_vpc_security_group_egress_rule.admin_a_s3.id
}
output "configuracion_efectiva" {
  description = "Contrato no sensible para comprobar el cableado de export desde el root."
  value = {
    rol      = aws_iam_role_policy.this.role
    politica = jsondecode(aws_iam_role_policy.this.policy)
    regla = {
      grupo       = aws_vpc_security_group_egress_rule.admin_a_s3.security_group_id
      prefix_list = aws_vpc_security_group_egress_rule.admin_a_s3.prefix_list_id
      protocolo   = aws_vpc_security_group_egress_rule.admin_a_s3.ip_protocol
      desde       = aws_vpc_security_group_egress_rule.admin_a_s3.from_port
      hasta       = aws_vpc_security_group_egress_rule.admin_a_s3.to_port
    }
  }
}
