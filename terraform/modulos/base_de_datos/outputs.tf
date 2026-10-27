output "endpoint" {
  value       = aws_db_instance.this.address
  description = "Nombre DNS de la instancia. Se conecta por nombre, nunca por IP."
}

output "puerto" {
  value       = aws_db_instance.this.port
  description = "Puerto SQL."
}

output "identificador" {
  value       = aws_db_instance.this.identifier
  description = "Identificador de la instancia."
}

output "arn" {
  value       = aws_db_instance.this.arn
  description = "ARN de la instancia. Lo usan los permisos de restore (H-031-7)."
}

output "id_de_recurso" {
  value       = aws_db_instance.this.resource_id
  description = "DbiResourceId: identifica la instancia en los backups automaticos."
}

output "nombre_de_base" {
  value       = aws_db_instance.this.db_name
  description = "Base de datos inicial."
}

output "nombre_del_grupo_de_logs" {
  value       = aws_cloudwatch_log_group.postgresql.name
  description = "Grupo de logs de PostgreSQL."
}

output "nombre_del_parametro_master" {
  value       = aws_ssm_parameter.contrasena_master.name
  description = "NOMBRE del SecureString de la contrasena master. Nunca su valor."
}

# Contrato de VERIFICACION. Ningun campo transporta la contrasena: las pruebas
# afirman tambien que ninguna salida la contiene.
output "configuracion_efectiva" {
  description = "Configuracion declarada de la base de datos, para pruebas y readback."
  value = {
    motor                     = aws_db_instance.this.engine
    version                   = aws_db_instance.this.engine_version
    clase                     = aws_db_instance.this.instance_class
    almacenamiento            = aws_db_instance.this.storage_type
    gib                       = aws_db_instance.this.allocated_storage
    gib_maximos               = aws_db_instance.this.max_allocated_storage
    cifrado                   = aws_db_instance.this.storage_encrypted
    clave_kms                 = var.arn_de_clave_kms
    publica                   = aws_db_instance.this.publicly_accessible
    grupos_de_seguridad       = aws_db_instance.this.vpc_security_group_ids
    multi_az                  = aws_db_instance.this.multi_az
    zona                      = aws_db_instance.this.availability_zone
    ca                        = aws_db_instance.this.ca_cert_identifier
    iam_db_auth               = aws_db_instance.this.iam_database_authentication_enabled
    dias_de_backup            = aws_db_instance.this.backup_retention_period
    ventana_de_backup         = aws_db_instance.this.backup_window
    ventana_de_mantenimiento  = aws_db_instance.this.maintenance_window
    borrar_backups_al_borrar  = aws_db_instance.this.delete_automated_backups
    proteccion_contra_borrado = aws_db_instance.this.deletion_protection
    omitir_snapshot_final     = aws_db_instance.this.skip_final_snapshot
    snapshot_final            = aws_db_instance.this.final_snapshot_identifier
    copiar_tags_a_snapshots   = aws_db_instance.this.copy_tags_to_snapshot
    actualizar_menores        = aws_db_instance.this.auto_minor_version_upgrade
    actualizar_mayores        = aws_db_instance.this.allow_major_version_upgrade
    performance_insights      = aws_db_instance.this.performance_insights_enabled
    intervalo_de_monitoreo    = aws_db_instance.this.monitoring_interval
    exportacion_de_logs       = aws_db_instance.this.enabled_cloudwatch_logs_exports
    soporte_extendido         = aws_db_instance.this.engine_lifecycle_support
    master_administrado       = aws_db_instance.this.manage_master_user_password
    # Solo dice SI el atributo no write-only quedo vacio; nunca expone un valor.
    contrasena_en_texto_ausente = nonsensitive(aws_db_instance.this.password == null)
    usuario_master              = aws_db_instance.this.username
    nombre_de_base              = aws_db_instance.this.db_name
    parametros                  = { for p in aws_db_parameter_group.this.parameter : p.name => { valor = p.value, metodo = p.apply_method } }
    familia                     = aws_db_parameter_group.this.family
    dias_de_logs                = aws_cloudwatch_log_group.postgresql.retention_in_days
    grupo_de_logs               = aws_cloudwatch_log_group.postgresql.name
    # `value` del parametro es computado: con un provider simulado recibiria un
    # valor inventado, asi que su ausencia real se demuestra sobre el plan y el
    # state del laboratorio (H-031-1, DH-2), no aqui.
    parametro_master = {
      nombre = aws_ssm_parameter.contrasena_master.name
      tipo   = aws_ssm_parameter.contrasena_master.type
      clave  = aws_ssm_parameter.contrasena_master.key_id
      nivel  = aws_ssm_parameter.contrasena_master.tier
    }
  }
}
