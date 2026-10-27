# Pruebas OFFLINE del root de datos. Provider simulado: no hay red, no hay AWS y
# no se crea nada. Demuestran la configuracion que D-22, D-23 y D-10 fijaron y
# que H-031-1 aprobo, y las guardas que impiden operar en el destino equivocado
# o con la identidad equivocada.
#
# Lo que estas pruebas NO demuestran: que AWS acepte la configuracion, que la
# red aisle de verdad, que TLS se exija, que el cifrado use `aws/rds`, ni que
# exista un backup restaurable. Todo eso es AWS-only (H-031-3 y siguientes).
#
# La contrasena de estas pruebas es un CANARIO, no un secreto: su unica funcion
# es poder buscarla en las salidas y demostrar que no aparece.

mock_provider "aws" {
  override_during = plan

  mock_data "aws_caller_identity" {
    defaults = {
      account_id = "123456789012"
      arn        = "arn:aws:sts::123456789012:assumed-role/PersonalBlogAdministrator/sesion-de-prueba"
    }
  }

  mock_resource "aws_subnet" {
    defaults = {
      availability_zone = "zona-simulada"
    }
  }

  mock_resource "aws_vpc_endpoint" {
    defaults = {
      id             = "vpce-simulado"
      prefix_list_id = "pl-simulada"
    }
  }

  mock_resource "aws_db_instance" {
    defaults = {
      address = "blog-prod-postgres.simulado.invalid"
      port    = 5432
    }
  }
}

# Un ID DISTINTO por grupo. Con un unico valor por omision para el tipo, las tres
# comparaciones de origen y destino serian ciertas por construccion y la prueba
# no demostraria nada.
override_resource {
  target          = module.red.aws_security_group.lambda
  override_during = plan
  values = {
    id = "sg-lambda-simulado"
  }
}

override_resource {
  target          = module.red.aws_security_group.rds
  override_during = plan
  values = {
    id = "sg-rds-simulado"
  }
}

override_resource {
  target          = module.red.aws_security_group.admin
  override_during = plan
  values = {
    id = "sg-admin-simulado"
  }
}

variables {
  region                    = "us-east-2"
  laboratorio               = false
  cuentas_permitidas        = ["123456789012"]
  prefijo                   = "blog-prod"
  arn_del_bucket_de_medios  = "arn:aws:s3:::personal-blog-medios-ejemplo"
  proteccion_contra_borrado = true
  omitir_snapshot_final     = false
  contrasena_master         = "CanarioDeLaPruebaOfflineNoEsSecreto0123456"
  # D-23 (H-031-6): CANARIOS de las credenciales de `blog_migrate` y `blog_app`, tambien efimeras.
  contrasena_blog_migrate = "CanarioMigracionesDeLaRaizNoEsSecreto012345"
  contrasena_blog_app     = "CanarioAplicacionDeLaRaizNoEsSecreto0123456"
  # D-20 (H-031-9): valores SIMULADOS; los del stack real van en el archivo privado del destino.
  integracion_grafana = {
    cuenta      = "999999999999"
    external_id = "1234567"
  }
  # D-24 (H-031-5): artefacto SIMULADO, el mismo de `fases_h0315.tftest.hcl`; el real lo fija `empaquetar_ejecutor.py`.
  zip_de_la_ejecutora = {
    ruta   = "tests/artefacto-simulado.txt"
    sha256 = "22f5495252caeb77a4a36ecc70b36f4186352a2de6a535f6985dcbe44048fc1e"
  }
  etiquetas = {
    Proyecto   = "personal-blog"
    Entorno    = "produccion"
    Gestion    = "terraform"
    Componente = "datos"
    Tarea      = "Task/031"
  }
}

run "red_privada_sin_salida_publica" {
  command = plan

  assert {
    condition = (
      module.red.configuracion_efectiva.cidr == "10.40.0.0/16" &&
      module.red.configuracion_efectiva.dns_support &&
      module.red.configuracion_efectiva.dns_hostnames &&
      !module.red.configuracion_efectiva.ipv6
    )
    error_message = "VPC 10.40.0.0/16 con DNS y sin IPv6 (D-22)."
  }

  assert {
    condition = (
      module.red.configuracion_efectiva.subredes["a"].cidr == "10.40.0.0/20" &&
      module.red.configuracion_efectiva.subredes["a"].zona_id == "use2-az1" &&
      module.red.configuracion_efectiva.subredes["b"].cidr == "10.40.16.0/20" &&
      module.red.configuracion_efectiva.subredes["b"].zona_id == "use2-az2" &&
      !module.red.configuracion_efectiva.subredes["a"].ip_publica &&
      !module.red.configuracion_efectiva.subredes["b"].ip_publica
    )
    error_message = "Dos subredes privadas /20 en use2-az1 y use2-az2, sin IP publica (D-22, DH-4)."
  }

  assert {
    condition = (
      module.red.configuracion_efectiva.tipo_de_endpoint == "Gateway" &&
      module.red.configuracion_efectiva.servicio_del_endpoint == "com.amazonaws.us-east-2.s3"
    )
    error_message = "S3 por gateway endpoint, nunca de interfaz (D-22)."
  }

  assert {
    condition = (
      length(jsondecode(module.red.configuracion_efectiva.politica_del_endpoint).Statement) == 2 &&
      jsondecode(module.red.configuracion_efectiva.politica_del_endpoint).Statement[0].Resource == ["arn:aws:s3:::personal-blog-medios-ejemplo/*"] &&
      jsondecode(module.red.configuracion_efectiva.politica_del_endpoint).Statement[0].Action == ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"] &&
      jsondecode(module.red.configuracion_efectiva.politica_del_endpoint).Statement[1].Resource == ["arn:aws:s3:::personal-blog-medios-ejemplo"] &&
      jsondecode(module.red.configuracion_efectiva.politica_del_endpoint).Statement[1].Action == ["s3:ListBucket"]
    )
    error_message = "La politica del endpoint solo alcanza el bucket de medios, con las acciones que se usan (DH-4)."
  }

  assert {
    condition = alltrue([
      for regla in values(module.red.configuracion_efectiva.reglas) : regla.cidr == null
    ])
    error_message = "Ninguna regla de grupo usa CIDR: solo referencia de grupo o prefix list."
  }

  assert {
    condition = (
      module.red.configuracion_efectiva.reglas.rds_desde_lambda.origen == module.red.configuracion_efectiva.grupos.lambda &&
      module.red.configuracion_efectiva.reglas.rds_desde_admin.origen == module.red.configuracion_efectiva.grupos.admin &&
      module.red.configuracion_efectiva.reglas.lambda_a_rds.destino == module.red.configuracion_efectiva.grupos.rds &&
      module.red.configuracion_efectiva.reglas.admin_a_rds.destino == module.red.configuracion_efectiva.grupos.rds &&
      module.red.configuracion_efectiva.reglas.lambda_a_s3.prefix_list == "pl-simulada"
    )
    error_message = "Las cinco reglas deben unir exactamente los grupos de D-22 §3.6."
  }

  assert {
    condition = (
      module.red.configuracion_efectiva.reglas.rds_desde_lambda.puerto == 5432 &&
      module.red.configuracion_efectiva.reglas.rds_desde_admin.puerto == 5432 &&
      module.red.configuracion_efectiva.reglas.lambda_a_rds.puerto == 5432 &&
      module.red.configuracion_efectiva.reglas.admin_a_rds.puerto == 5432 &&
      module.red.configuracion_efectiva.reglas.lambda_a_s3.puerto == 443
    )
    error_message = "PostgreSQL por 5432 y S3 por 443; ningun otro puerto."
  }
}

run "rds_privado_cifrado_y_protegido" {
  command = plan

  assert {
    condition = (
      module.base_de_datos.configuracion_efectiva.motor == "postgres" &&
      module.base_de_datos.configuracion_efectiva.version == "17.11" &&
      module.base_de_datos.configuracion_efectiva.clase == "db.t4g.micro" &&
      module.base_de_datos.configuracion_efectiva.almacenamiento == "gp3" &&
      module.base_de_datos.configuracion_efectiva.gib == 20 &&
      module.base_de_datos.configuracion_efectiva.gib_maximos == 50
    )
    error_message = "PostgreSQL 17.11, db.t4g.micro, gp3 20 GiB con techo de 50 (D-22)."
  }

  assert {
    condition = (
      module.base_de_datos.configuracion_efectiva.publica == false &&
      module.base_de_datos.configuracion_efectiva.multi_az == false &&
      module.base_de_datos.configuracion_efectiva.zona == "zona-simulada"
    )
    error_message = "Privada, Single-AZ y en la AZ de la subred a."
  }

  assert {
    condition     = module.base_de_datos.configuracion_efectiva.grupos_de_seguridad == toset(["sg-rds-simulado"])
    error_message = "La instancia lleva EXACTAMENTE sg-rds: ni el grupo por omision ni otro (H-031-1A)."
  }

  assert {
    condition = (
      module.base_de_datos.configuracion_efectiva.cifrado &&
      module.base_de_datos.configuracion_efectiva.clave_kms == null &&
      module.base_de_datos.configuracion_efectiva.ca == "rds-ca-rsa2048-g1" &&
      module.base_de_datos.configuracion_efectiva.iam_db_auth == false
    )
    error_message = "Cifrado con aws/rds, CA por omision y sin IAM DB auth (D-23)."
  }

  assert {
    condition = (
      module.base_de_datos.configuracion_efectiva.dias_de_backup == 7 &&
      module.base_de_datos.configuracion_efectiva.ventana_de_backup == "07:00-07:30" &&
      module.base_de_datos.configuracion_efectiva.ventana_de_mantenimiento == "sun:08:00-sun:09:00" &&
      module.base_de_datos.configuracion_efectiva.borrar_backups_al_borrar == false &&
      module.base_de_datos.configuracion_efectiva.copiar_tags_a_snapshots
    )
    error_message = "Backups de 7 dias con PITR, ventanas de D-22 y backups conservados al borrar (DH-4)."
  }

  assert {
    condition = (
      module.base_de_datos.configuracion_efectiva.proteccion_contra_borrado &&
      module.base_de_datos.configuracion_efectiva.omitir_snapshot_final == false &&
      module.base_de_datos.configuracion_efectiva.snapshot_final == "blog-prod-postgres-final"
    )
    error_message = "Produccion exige deletion protection y snapshot final (D-10)."
  }

  assert {
    condition = (
      module.base_de_datos.configuracion_efectiva.actualizar_menores &&
      module.base_de_datos.configuracion_efectiva.actualizar_mayores == false &&
      module.base_de_datos.configuracion_efectiva.soporte_extendido == "open-source-rds-extended-support-disabled"
    )
    error_message = "Menores automaticas, mayores nunca y Extended Support deshabilitado (DH-4)."
  }

  assert {
    condition = (
      module.base_de_datos.configuracion_efectiva.performance_insights == false &&
      module.base_de_datos.configuracion_efectiva.intervalo_de_monitoreo == 0 &&
      module.base_de_datos.configuracion_efectiva.exportacion_de_logs == toset(["postgresql"]) &&
      module.base_de_datos.configuracion_efectiva.dias_de_logs == 14 &&
      module.base_de_datos.configuracion_efectiva.grupo_de_logs == "/aws/rds/instance/blog-prod-postgres/postgresql"
    )
    error_message = "Sin PI ni Enhanced Monitoring; logs de PostgreSQL con 14 dias (D-11 baseline)."
  }

  assert {
    condition = (
      module.base_de_datos.configuracion_efectiva.familia == "postgres17" &&
      module.base_de_datos.configuracion_efectiva.parametros == {
        "log_statement"              = { valor = "ddl", metodo = "immediate" }
        "log_min_duration_statement" = { valor = "1000", metodo = "immediate" }
        "log_connections"            = { valor = "1", metodo = "immediate" }
        "log_disconnections"         = { valor = "1", metodo = "immediate" }
      }
    )
    # Ni `superuser_reserved_connections` (IsModifiable=false, §27.4) ni `rds.force_ssl` ni
    # `ssl_min_protocol_version` (AWS los representa como Source=system, §32/§33) se gestionan:
    # check_parametros.py verifica sus valores de sistema contra el catalogo antes de cada plan.
    error_message = "Parameter group propio con exactamente los cuatro valores explicitos de D-22 §3.8 (RECOVERY-2)."
  }

  assert {
    condition = (
      module.base_de_datos.configuracion_efectiva.usuario_master == "blogadmin" &&
      module.base_de_datos.configuracion_efectiva.nombre_de_base == "personal_blog" &&
      module.base_de_datos.configuracion_efectiva.master_administrado != true
    )
    error_message = "Master blogadmin, base personal_blog y sin Secrets Manager administrado (D-23)."
  }
}

# Que ninguna salida pueda llevar la contrasena no se prueba buscando un canario
# aqui: el provider simulado no es estable entre plan y apply. La garantia es
# ESTRUCTURAL —Terraform rechaza un valor efimero en una salida o en un atributo
# que no sea write-only— y tiene su control negativo en
# tests/terraform_datos/test_secretos.py. La ausencia EMPIRICA en el plan, el
# state y las salidas reales se demuestra en el laboratorio (DH-2).
run "la_contrasena_solo_viaja_por_atributos_write_only" {
  command = plan

  assert {
    condition     = module.base_de_datos.configuracion_efectiva.contrasena_en_texto_ausente
    error_message = "El atributo `password` no write-only debe quedar vacio: solo se usa `password_wo`."
  }

  assert {
    condition = (
      module.base_de_datos.configuracion_efectiva.parametro_master.nombre == "/blog-prod/datos/blogadmin" &&
      module.base_de_datos.configuracion_efectiva.parametro_master.tipo == "SecureString" &&
      module.base_de_datos.configuracion_efectiva.parametro_master.clave == "alias/aws/ssm" &&
      module.base_de_datos.configuracion_efectiva.parametro_master.nivel == "Standard"
    )
    error_message = "La custodia es un SecureString estandar con aws/ssm (DH-2)."
  }

  assert {
    condition     = output.nombre_del_parametro_master == "/blog-prod/datos/blogadmin"
    error_message = "La salida publica el NOMBRE del parametro, nunca su valor."
  }
}

# --- Ejecutora de D-24 (H-031-5), alarmas de D-11 (H-031-8) y rol de D-20 (H-031-9) ---
#
# La ejecutora salio del root el 2026-10-08 mientras la cuota de Lambda no permitia RC=1. VUELVE el 2026-10-18 con
# D-24 modificada (aprobada el 2026-10-19): concurrencia NO reservada, y la exclusion de las escrituras la hace su advisory lock de
# PostgreSQL. Sus pruebas de detalle viven a nivel de modulo (`fases_h0315.tftest.hcl`); aqui, el cableado desde el
# root. Lo que estas pruebas NO demuestran: que la ENI se cree, que CloudWatch evalue, que IAM
# autorice ni que Grafana asuma el rol (AWS-only).

run "ejecutora_cableada_solo_con_sg_admin_y_sin_reserva" {
  command = plan

  assert {
    condition = (
      module.ejecutor_privado.configuracion_efectiva.funcion.grupos == toset([module.red.id_sg_admin]) &&
      module.ejecutor_privado.configuracion_efectiva.funcion.subredes == toset(module.red.ids_de_subredes)
    )
    error_message = "La ejecutora va SOLO con sg-admin, en las dos subredes privadas de la red de este root."
  }

  assert {
    condition     = coalesce(module.ejecutor_privado.configuracion_efectiva.funcion.concurrencia_reservada, -1) == -1
    error_message = "D-24 modificada el 2026-10-18 (aprobada el 2026-10-19): concurrencia NO reservada, ni 0 ni una reserva."
  }

  assert {
    condition     = output.nombre_de_la_ejecutora == "blog-prod-ejecutor" && module.ejecutor_privado.configuracion_efectiva.rol.nombre == "PersonalBlogEjecutorDatos"
    error_message = "Nombre de la funcion por prefijo y rol de ejecucion propio."
  }
}

# --- H-031-6: credenciales SQL de D-23 y modo `export` de D-24 ---------------------------------------------------
#
# Los detalles de cada modulo se prueban en `fases_h0316.tftest.hcl`; aqui, que ESTE root los cablea: las rutas junto
# a la master, la politica en el rol de la propia ejecutora y la salida desde su `sg-admin` hacia la prefix list de
# SU endpoint. Lo que NO demuestran: que SSM cifre, que IAM evalue las condiciones ni que la regla deje pasar el
# trafico (AWS-only, con el apply de H-031-6).

run "credenciales_sql_y_exportacion_cableadas" {
  command = plan

  assert {
    condition = (
      length(output.nombres_de_credenciales_sql) == 2 &&
      output.nombres_de_credenciales_sql.blog_migrate == "/blog-prod/datos/blog_migrate" &&
      output.nombres_de_credenciales_sql.blog_app == "/blog-prod/datos/blog_app"
    )
    error_message = "La salida publica los NOMBRES de las dos credenciales, junto a la master; nunca su valor."
  }

  assert {
    condition     = module.credenciales_sql.versiones.blog_migrate == 1 && module.credenciales_sql.versiones.blog_app == 1
    error_message = "Version write-only 1 para las dos credenciales."
  }

  assert {
    condition = (
      module.exportacion.configuracion_efectiva.rol == "PersonalBlogEjecutorDatos" &&
      module.exportacion.nombre_de_la_politica == "PersonalBlogEjecutorDatos-exportacion"
    )
    error_message = "La politica de export va inline en el rol que crea la propia ejecutora."
  }

  assert {
    condition = (
      module.exportacion.configuracion_efectiva.regla.grupo == "sg-admin-simulado" &&
      module.exportacion.configuracion_efectiva.regla.prefix_list == "pl-simulada" &&
      module.exportacion.configuracion_efectiva.regla.protocolo == "tcp" &&
      module.exportacion.configuracion_efectiva.regla.desde == 443 &&
      module.exportacion.configuracion_efectiva.regla.hasta == 443
    )
    error_message = "La salida de export sale de sg-admin hacia la prefix list del endpoint de ESTE root, solo por 443."
  }

  assert {
    condition = (
      module.exportacion.configuracion_efectiva.politica.Statement[0].Resource == "arn:aws:s3:::personal-blog-medios-ejemplo/exportaciones/*" &&
      module.exportacion.configuracion_efectiva.politica.Statement[0].Condition.StringEquals["aws:SourceVpce"] == "vpce-simulado"
    )
    error_message = "El export solo escribe en exportaciones/ del bucket del contrato, y solo por el endpoint de este root."
  }
}

run "contrasena_de_blog_migrate_debil_rechazada" {
  command = plan
  variables {
    contrasena_blog_migrate = "corta"
  }
  expect_failures = [var.contrasena_blog_migrate]
}

run "contrasena_de_blog_app_debil_rechazada" {
  command = plan
  variables {
    contrasena_blog_app = "con-guiones-no-alfanumerica-0123456789abcdef"
  }
  expect_failures = [var.contrasena_blog_app]
}

run "alarmas_d11_sobre_la_instancia_de_este_root" {
  command = plan

  assert {
    condition     = module.alarmas_rds.numero_de_alarmas == 8 && length(output.alarmas_de_rds) == 8
    error_message = "Las 8 alarmas de D-11, dentro de las 10 gratuitas, publicadas por nombre."
  }

  assert {
    condition = alltrue([for clave, alarma in module.alarmas_rds.configuracion_efectiva :
    alarma.dimension == "blog-prod-postgres" && alarma.acciones == false && alarma.nombre == "blog-prod-rds-${clave}"])
    error_message = "Cada alarma vigila la instancia que crea este root, sin acciones ni destinatarios."
  }
}

run "rol_de_grafana_con_la_cuenta_verificada" {
  command = plan

  assert {
    condition = (
      module.lectura_grafana.configuracion_efectiva.confianza.Statement[0].Principal.AWS == "arn:aws:iam::999999999999:root" &&
      module.lectura_grafana.configuracion_efectiva.confianza.Statement[0].Condition.StringEquals["sts:ExternalId"] == "1234567"
    )
    error_message = "Confianza solo para la cuenta de Grafana del destino y con su ExternalId."
  }

  assert {
    condition     = module.lectura_grafana.configuracion_efectiva.permisos.Statement[1].Resource == "arn:aws:cloudwatch:us-east-2:123456789012:alarm:blog-prod-*"
    error_message = "Las alarmas legibles son las del proyecto, en la cuenta verificada por la guarda de identidad."
  }

  assert {
    condition     = output.rol_de_grafana == "PersonalBlogLecturaGrafana"
    error_message = "La salida da el NOMBRE del rol; nunca un ARN con la cuenta."
  }
}

# --- Guardas de destino e identidad ----------------------------------------

# Decision operacional del usuario (Task/031 §24, H-031-2-ALIGN): el root de datos se
# opera con UNA identidad exacta, `PersonalBlogAdministrator`. El operador creado en
# H-031-IAM se conserva, pero ya no es la identidad aceptada aqui.
run "identidad_administrativa_aceptada" {
  command = plan

  override_data {
    target = data.aws_caller_identity.operador
    values = {
      account_id = "123456789012"
      arn        = "arn:aws:sts::123456789012:assumed-role/PersonalBlogAdministrator/sesion"
    }
  }

  assert {
    condition     = startswith(data.aws_caller_identity.operador.arn, "arn:aws:sts::123456789012:assumed-role/PersonalBlogAdministrator/")
    error_message = "La sesion de PersonalBlogAdministrator en la cuenta verificada debe poder planificar."
  }
}

run "identidad_del_operador_rechazada" {
  command = plan

  override_data {
    target = data.aws_caller_identity.operador
    values = {
      account_id = "123456789012"
      arn        = "arn:aws:sts::123456789012:assumed-role/PersonalBlogDataOperator/sesion"
    }
  }

  expect_failures = [data.aws_caller_identity.operador]
}

run "identidad_de_un_rol_arbitrario_rechazada" {
  command = plan

  override_data {
    target = data.aws_caller_identity.operador
    values = {
      account_id = "123456789012"
      arn        = "arn:aws:sts::123456789012:assumed-role/OtroRol/sesion"
    }
  }

  expect_failures = [data.aws_caller_identity.operador]
}

run "prefijo_parecido_al_administrativo_rechazado" {
  command = plan

  override_data {
    target = data.aws_caller_identity.operador
    values = {
      account_id = "123456789012"
      arn        = "arn:aws:sts::123456789012:assumed-role/PersonalBlogAdministratorX/sesion"
    }
  }

  expect_failures = [data.aws_caller_identity.operador]
}

run "cuenta_ajena_rechazada" {
  command = plan

  override_data {
    target = data.aws_caller_identity.operador
    values = {
      account_id = "999999999999"
      arn        = "arn:aws:sts::999999999999:assumed-role/PersonalBlogAdministrator/sesion"
    }
  }

  expect_failures = [data.aws_caller_identity.operador]
}

run "usuario_iam_directo_rechazado" {
  command = plan

  override_data {
    target = data.aws_caller_identity.operador
    values = {
      account_id = "123456789012"
      arn        = "arn:aws:iam::123456789012:user/personal-blog-entry-admin"
    }
  }

  expect_failures = [data.aws_caller_identity.operador]
}

run "rol_operativo_administrativo_aceptado" {
  command = plan
  variables {
    rol_operativo = "PersonalBlogAdministrator"
  }
  assert {
    condition     = var.rol_operativo == "PersonalBlogAdministrator"
    error_message = "El unico rol operativo admitido es PersonalBlogAdministrator."
  }
}

run "rol_operativo_del_operador_rechazado" {
  command = plan
  variables {
    rol_operativo = "PersonalBlogDataOperator"
  }
  expect_failures = [var.rol_operativo]
}

run "rol_operativo_arbitrario_rechazado" {
  command = plan
  variables {
    rol_operativo = "OtroRol"
  }
  expect_failures = [var.rol_operativo]
}

run "produccion_sin_cuenta_rechazada" {
  command = plan
  variables {
    cuentas_permitidas = []
  }
  expect_failures = [var.cuentas_permitidas]
}

# --- Protecciones que solo el laboratorio puede relajar ---------------------

run "produccion_sin_deletion_protection_rechazada" {
  command = plan
  variables {
    proteccion_contra_borrado = false
  }
  expect_failures = [var.proteccion_contra_borrado]
}

run "produccion_sin_snapshot_final_rechazada" {
  command = plan
  variables {
    omitir_snapshot_final = true
  }
  expect_failures = [var.omitir_snapshot_final]
}

# --- Decisiones de D-22/D-10 que no cambian sin decision explicita ---------

run "otra_clase_rechazada" {
  command = plan
  variables {
    clase_de_la_instancia = "db.t4g.small"
  }
  expect_failures = [var.clase_de_la_instancia]
}

run "otro_major_rechazado" {
  command = plan
  variables {
    version_del_motor = "18.6"
  }
  expect_failures = [var.version_del_motor]
}

run "backups_desactivados_rechazados" {
  command = plan
  variables {
    dias_de_retencion_de_backups = 0
  }
  expect_failures = [var.dias_de_retencion_de_backups]
}

# H-031-3-RECOVERY-3-FREE (Task/031 §34): contrato de retencion. Objetivo de D-10/D-22 = 7 dias
# (plan PAID); EXCEPCION TEMPORAL = 1 dia mientras la cuenta siga en plan FREE, que rechazo 7 con
# FreeTierRestrictionError. Ningun otro valor, y nunca 0.
run "retencion_temporal_del_plan_free_aceptada" {
  command = plan
  variables {
    dias_de_retencion_de_backups = 1
  }
  assert {
    condition     = module.base_de_datos.configuracion_efectiva.dias_de_backup == 1
    error_message = "La excepcion temporal del plan FREE es exactamente 1 dia."
  }
}

run "retencion_fuera_del_contrato_rechazada" {
  command = plan
  variables {
    dias_de_retencion_de_backups = 3
  }
  expect_failures = [var.dias_de_retencion_de_backups]
}

run "retencion_maxima_de_rds_fuera_del_contrato_rechazada" {
  command = plan
  variables {
    dias_de_retencion_de_backups = 35
  }
  expect_failures = [var.dias_de_retencion_de_backups]
}

run "techo_de_almacenamiento_ampliado_rechazado" {
  command = plan
  variables {
    gib_maximos = 100
  }
  expect_failures = [var.gib_maximos]
}

run "retencion_de_logs_no_admitida_rechazada" {
  command = plan
  variables {
    dias_de_retencion_de_logs = 0
  }
  expect_failures = [var.dias_de_retencion_de_logs]
}

run "una_sola_subred_rechazada" {
  command = plan
  variables {
    subredes = {
      a = { cidr = "10.40.0.0/20", zona_id = "use2-az1" }
    }
  }
  expect_failures = [var.subredes]
}

run "dos_subredes_en_la_misma_zona_rechazadas" {
  command = plan
  variables {
    subredes = {
      a = { cidr = "10.40.0.0/20", zona_id = "use2-az1" }
      b = { cidr = "10.40.16.0/20", zona_id = "use2-az1" }
    }
  }
  expect_failures = [var.subredes]
}

run "zona_por_nombre_rechazada" {
  command = plan
  variables {
    subredes = {
      a = { cidr = "10.40.0.0/20", zona_id = "us-east-2a" }
      b = { cidr = "10.40.16.0/20", zona_id = "us-east-2b" }
    }
  }
  expect_failures = [var.subredes]
}

run "arn_de_medios_con_comodin_rechazado" {
  command = plan
  variables {
    arn_del_bucket_de_medios = "arn:aws:s3:::*"
  }
  expect_failures = [var.arn_del_bucket_de_medios]
}

run "contrasena_debil_rechazada" {
  command = plan
  variables {
    contrasena_master = "corta"
  }
  expect_failures = [var.contrasena_master]
}

run "region_no_comercial_rechazada" {
  command = plan
  variables {
    region = "local-1"
  }
  expect_failures = [var.region]
}

# --- El laboratorio usa los MISMOS modulos ----------------------------------

run "laboratorio_usa_los_mismos_modulos" {
  command = plan

  override_data {
    target = data.aws_caller_identity.operador
    values = {
      account_id = "000000000000"
      arn        = "arn:aws:iam::000000000000:root"
    }
  }

  variables {
    region                    = "us-east-1"
    laboratorio               = true
    cuentas_permitidas        = []
    prefijo                   = "blog-lab"
    arn_del_bucket_de_medios  = "arn:aws:s3:::blog-lab-medios"
    proteccion_contra_borrado = false
    omitir_snapshot_final     = true
    subredes = {
      a = { cidr = "10.40.0.0/20", zona_id = "use1-az1" }
      b = { cidr = "10.40.16.0/20", zona_id = "use1-az2" }
    }
    endpoints_aws = {
      ec2        = "http://127.0.0.1:4566"
      rds        = "http://127.0.0.1:4566"
      ssm        = "http://127.0.0.1:4566"
      logs       = "http://127.0.0.1:4566"
      sts        = "http://127.0.0.1:4566"
      iam        = "http://127.0.0.1:4566"
      lambda     = "http://127.0.0.1:4566"
      cloudwatch = "http://127.0.0.1:4566"
    }
  }

  assert {
    condition = (
      module.alarmas_rds.configuracion_efectiva.cpu.dimension == "blog-lab-postgres" &&
      module.alarmas_rds.configuracion_efectiva.cpu.acciones == false &&
      module.lectura_grafana.configuracion_efectiva.permisos.Statement[1].Resource == "arn:aws:cloudwatch:us-east-1:000000000000:alarm:blog-lab-*"
    )
    error_message = "El laboratorio usa las MISMAS alarmas y el MISMO rol de D-20, con los valores de su destino."
  }

  assert {
    condition = (
      module.base_de_datos.configuracion_efectiva.publica == false &&
      module.base_de_datos.configuracion_efectiva.cifrado &&
      module.base_de_datos.configuracion_efectiva.version == "17.11" &&
      module.base_de_datos.configuracion_efectiva.clase == "db.t4g.micro" &&
      module.red.configuracion_efectiva.tipo_de_endpoint == "Gateway" &&
      alltrue([for regla in values(module.red.configuracion_efectiva.reglas) : regla.cidr == null])
    )
    error_message = "El laboratorio debe usar los MISMOS modulos y los mismos controles que produccion."
  }

  assert {
    condition = (
      module.base_de_datos.configuracion_efectiva.proteccion_contra_borrado == false &&
      module.base_de_datos.configuracion_efectiva.omitir_snapshot_final &&
      module.base_de_datos.configuracion_efectiva.snapshot_final == null
    )
    error_message = "Solo el laboratorio relaja la proteccion, para poder reconstruirse en cada ciclo."
  }
}
