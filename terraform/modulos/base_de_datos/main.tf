# ---------------------------------------------------------------------------
# Modulo: base_de_datos — Amazon RDS for PostgreSQL privado
#
# Que crea y por que existe
#   La base de datos productiva de ADR-010 con los valores que Task/029 fijo en
#   D-22, D-23 y D-10: PostgreSQL 17.11, `db.t4g.micro`, gp3 20 GiB con techo de
#   50, Single-AZ, cifrado con `aws/rds`, TLS obligatorio, backups de 7 dias con
#   PITR, deletion protection y snapshot final. Mas el DB subnet group, un
#   parameter group propio, el grupo de logs con retencion explicita y el
#   SecureString que custodia la contrasena master.
#
# Lo que NO crea, a proposito
#   RDS Proxy (D-12), Multi-AZ (R-29 aceptado), IAM DB authentication (D-23),
#   Secrets Manager (D-23), clave KMS propia (D-23), Enhanced Monitoring ni
#   Performance Insights (D-11). Tampoco usuarios SQL: `blog_app` y
#   `blog_migrate` se crean por la ejecutora privada en H-031-6.
#
# La contrasena master
#   Entra por una variable EFIMERA y solo alimenta atributos write-only:
#   `password_wo` de la instancia y `value_wo` del parametro. Terraform no la
#   escribe ni en el plan ni en el state (DH-2). Rotarla es incrementar
#   `version_de_la_contrasena`.
#
# De que depende
#   Del modulo `red`: subredes privadas y `sg-rds`.
#
# Diferencia conocida con AWS real
#   KMS, TLS verificado, backups administrados, PITR y restore son AWS-only: el
#   laboratorio no prueba ninguno (aws-local-parity.md §8.4).
# ---------------------------------------------------------------------------

locals {
  # Valores explicitos de D-22 §3.8. Viven en el modulo, no en el destino: son
  # contrato de seguridad, y el laboratorio y AWS real deben declarar los
  # mismos. `max_connections` NO se toca: queda la formula de la clase (112), y
  # el presupuesto de conexiones sigue abierto en D-12, owner Task/032.
  #
  # `apply_method` sigue el tipo del parametro: los dinamicos se aplican al
  # momento. Antes de cada plan productivo, `scripts/terraform_datos/check_parametros.py`
  # exige contra el catalogo real (`describe-engine-default-parameters`) que cada
  # uno sea modificable y que su metodo case con su `ApplyType`.
  #
  # INVARIANTES DE SISTEMA, que este modulo NO gestiona (Task/031 §27.4, §32 y §33):
  # - `superuser_reserved_connections` = 3: `IsModifiable = false`; declararlo
  #   rompio el apply real de H-031-3. El presupuesto de conexiones lo sigue restando.
  # - `rds.force_ssl` = 1 y `ssl_min_protocol_version` = TLSv1.2: coinciden con el
  #   valor de sistema y AWS los devuelve como `Source = system` / `pending-reboot`
  #   aunque se declaren, asi que declararlos no converge.
  # El preflight `check_parametros.py` exige esos tres valores, con `Source = system`,
  # contra el catalogo real antes de cada plan productivo. Sin `ignore_changes`.
  parametros = {
    "log_statement" = {
      valor  = "ddl"
      metodo = "immediate"
    }
    "log_min_duration_statement" = {
      valor  = "1000"
      metodo = "immediate"
    }
    "log_connections" = {
      valor  = "1"
      metodo = "immediate"
    }
    "log_disconnections" = {
      valor  = "1"
      metodo = "immediate"
    }
  }

  # CA por omision de RDS, con rotacion automatica del certificado de servidor
  # (D-23). El cliente valida con el bundle regional y `verify-full`, Task/032.
  ca = "rds-ca-rsa2048-g1"
}

resource "aws_db_subnet_group" "this" {
  name        = var.nombre
  description = "Subredes privadas de ${var.nombre}"
  subnet_ids  = var.ids_de_subredes

  tags = {
    Name = var.nombre
  }
}

resource "aws_db_parameter_group" "this" {
  name        = "${var.nombre}17"
  family      = var.familia_del_parametro
  description = "Parametros explicitos de ${var.nombre} (D-22)"

  dynamic "parameter" {
    for_each = local.parametros
    content {
      name         = parameter.key
      value        = parameter.value.valor
      apply_method = parameter.value.metodo
    }
  }

  tags = {
    Name = "${var.nombre}17"
  }
}

# Creado ANTES que la instancia y con su nombre exacto. Si lo creara RDS al
# exportar logs, naceria con retencion INFINITA. 14 dias es el baseline de D-11
# aprobado en H-031-1; las alarmas y los umbrales siguen en H-031-8.
resource "aws_cloudwatch_log_group" "postgresql" {
  name              = "/aws/rds/instance/${var.nombre}/postgresql"
  retention_in_days = var.dias_de_retencion_de_logs

  tags = {
    Name = "${var.nombre}-postgresql"
  }
}

resource "aws_db_instance" "this" {
  identifier     = var.nombre
  engine         = "postgres"
  engine_version = var.version_del_motor
  instance_class = var.clase

  storage_type          = "gp3"
  allocated_storage     = var.gib
  max_allocated_storage = var.gib_maximos
  # Bajo 400 GiB gp3 incluye 3000 IOPS y 125 MiB/s y no admite aprovisionar mas:
  # `iops` y `storage_throughput` no se declaran (D-22 §3.4).

  storage_encrypted = true
  kms_key_id        = var.arn_de_clave_kms

  db_name             = var.nombre_de_base
  username            = var.usuario_master
  password_wo         = var.contrasena_master
  password_wo_version = var.version_de_la_contrasena
  port                = 5432

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [var.id_sg_rds]
  parameter_group_name   = aws_db_parameter_group.this.name
  publicly_accessible    = false
  multi_az               = false
  availability_zone      = var.zona
  network_type           = "IPV4"

  ca_cert_identifier                  = local.ca
  iam_database_authentication_enabled = false

  backup_retention_period  = var.dias_de_retencion
  backup_window            = var.ventana_de_backup
  maintenance_window       = var.ventana_de_mantenimiento
  copy_tags_to_snapshot    = true
  delete_automated_backups = false

  deletion_protection       = var.proteccion_contra_borrado
  skip_final_snapshot       = var.omitir_snapshot_final
  final_snapshot_identifier = var.omitir_snapshot_final ? null : "${var.nombre}-final"

  # La version menor la sube AWS en la ventana de mantenimiento. Cuando ocurra,
  # el plan mostrara la diferencia contra `version_del_motor`: se reconcilia en
  # codigo por runbook. No hay `ignore_changes` (DH-4): el drift queda visible.
  auto_minor_version_upgrade  = true
  allow_major_version_upgrade = false
  apply_immediately           = false

  performance_insights_enabled    = false
  monitoring_interval             = 0
  enabled_cloudwatch_logs_exports = ["postgresql"]

  # Guarda de costo: impide la inscripcion automatica en RDS Extended Support,
  # que se cobra por vCPU-hora cuando el major sale del soporte estandar.
  engine_lifecycle_support = "open-source-rds-extended-support-disabled"

  tags = {
    Name = var.nombre
  }

  depends_on = [aws_cloudwatch_log_group.postgresql]
}

# Custodia de la contrasena master: SecureString estandar cifrado con la clave
# administrada `aws/ssm`. Recuperable solo con una identidad autorizada, y sin
# que el valor pase por el state (`value_wo`).
resource "aws_ssm_parameter" "contrasena_master" {
  name             = var.ruta_del_parametro_master
  description      = "Contrasena master de ${var.nombre}. Solo recuperacion (D-23)."
  type             = "SecureString"
  tier             = "Standard"
  key_id           = "alias/aws/ssm"
  value_wo         = var.contrasena_master
  value_wo_version = var.version_de_la_contrasena

  tags = {
    Name = "${var.nombre}-master"
  }
}
