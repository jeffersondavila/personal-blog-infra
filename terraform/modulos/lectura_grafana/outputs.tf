output "nombre_del_rol" {
  description = "Rol que Grafana Cloud asume. Sin ARN en las salidas: lleva la cuenta; se toma de la consola al configurar."
  value       = aws_iam_role.this.name
}

output "configuracion_efectiva" {
  description = "Contrato de verificacion: nombre, confianza y permisos efectivos, ya decodificados."
  value = {
    nombre        = aws_iam_role.this.name
    sesion_maxima = aws_iam_role.this.max_session_duration
    confianza     = local.confianza
    permisos      = local.politica
  }
}
