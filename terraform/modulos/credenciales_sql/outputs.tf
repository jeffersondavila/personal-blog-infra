output "nombres_de_los_parametros" {
  description = "Rutas SSM de las credenciales: el operador las lee en memoria; nunca su valor."
  value = {
    blog_migrate = aws_ssm_parameter.blog_migrate.name
    blog_app     = aws_ssm_parameter.blog_app.name
  }
}

output "versiones" {
  description = "Version write-only vigente de cada credencial."
  value = {
    blog_migrate = aws_ssm_parameter.blog_migrate.value_wo_version
    blog_app     = aws_ssm_parameter.blog_app.value_wo_version
  }
}
