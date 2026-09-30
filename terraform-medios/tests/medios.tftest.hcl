# Pruebas OFFLINE del root de medios. Provider simulado: no hay red, no hay AWS
# y no se crea nada. Demuestran la configuracion que D-08 fijo para el MVP y las
# guardas que impiden aplicar en el destino equivocado.
#
# Lo que estas pruebas NO demuestran: que AWS acepte la configuracion, que el
# bucket sea realmente privado ni que la regla de lifecycle expire una version.
# Eso es AWS-only y pertenece al apply autorizado de H-030-3.

mock_provider "aws" {
  override_during = plan

  # Sin estos valores el `id` y el `arn` del bucket son desconocidos durante el
  # plan y ninguna asercion sobre las salidas podria evaluarse. Son datos
  # ficticios: su unico papel es hacer comprobable el cableado modulo -> salidas.
  mock_resource "aws_s3_bucket" {
    defaults = {
      id     = "bucket-simulado"
      arn    = "arn:aws:s3:::bucket-simulado"
      bucket = "bucket-simulado"
    }
  }
}

variables {
  region             = "us-east-2"
  laboratorio        = false
  nombre_del_bucket  = "personal-blog-medios-us-east-2-ejemplo"
  cuentas_permitidas = ["123456789012"]
  etiquetas = {
    Proyecto   = "personal-blog"
    Entorno    = "produccion"
    Gestion    = "terraform"
    Componente = "medios"
    Tarea      = "Task/030"
  }
  origenes_cors               = []
  dias_para_expirar_versiones = 30
  forzar_destruccion          = false
}

run "produccion_privada_y_recuperable" {
  command = plan

  assert {
    condition = alltrue([
      module.almacenamiento.configuracion_efectiva.bpa.block_public_acls,
      module.almacenamiento.configuracion_efectiva.bpa.block_public_policy,
      module.almacenamiento.configuracion_efectiva.bpa.ignore_public_acls,
      module.almacenamiento.configuracion_efectiva.bpa.restrict_public_buckets,
    ])
    error_message = "El bucket de medios exige las cuatro protecciones de acceso publico."
  }

  assert {
    condition     = module.almacenamiento.configuracion_efectiva.ownership == "BucketOwnerEnforced"
    error_message = "Ownership debe ser BucketOwnerEnforced: las ACL quedan desactivadas."
  }

  assert {
    condition     = module.almacenamiento.configuracion_efectiva.versionado == "Enabled"
    error_message = "El versionado del bucket de medios debe estar habilitado."
  }

  assert {
    condition     = module.almacenamiento.configuracion_efectiva.cifrado == "AES256"
    error_message = "El cifrado en reposo debe ser SSE-S3 con AES256, sin KMS."
  }

  assert {
    condition     = module.almacenamiento.configuracion_efectiva.force_destroy == false
    error_message = "En produccion force_destroy debe ser false (D-08 MVP, decision 12)."
  }

  assert {
    condition = (
      length(jsondecode(module.almacenamiento.configuracion_efectiva.policy).Statement) == 1 &&
      jsondecode(module.almacenamiento.configuracion_efectiva.policy).Statement[0].Effect == "Deny" &&
      jsondecode(module.almacenamiento.configuracion_efectiva.policy).Statement[0].Condition.Bool["aws:SecureTransport"] == "false"
    )
    error_message = "La policy debe NEGAR transporte no TLS y no conceder acceso a nadie."
  }

  assert {
    condition = (
      module.almacenamiento.configuracion_efectiva.lifecycle.dias_de_versiones_no_actuales == 30 &&
      module.almacenamiento.configuracion_efectiva.lifecycle.dias_para_abortar_multipart == 7
    )
    error_message = "Lifecycle de D-08 MVP: 30 dias de versiones no actuales y 7 para multipart."
  }

  assert {
    condition     = module.almacenamiento.configuracion_efectiva.reglas_cors == 0
    error_message = "Con origenes_cors = [] no debe crearse ninguna configuracion CORS."
  }

  assert {
    condition = (
      module.almacenamiento.configuracion_efectiva.tags["Proyecto"] == "personal-blog" &&
      module.almacenamiento.configuracion_efectiva.tags["Componente"] == "medios" &&
      module.almacenamiento.configuracion_efectiva.tags["Tarea"] == "Task/030"
    )
    error_message = "Las etiquetas del proyecto deben llegar al bucket por default_tags."
  }

  assert {
    condition = (
      output.nombre_del_bucket != "" &&
      can(regex("^arn:aws:s3:::", output.arn_del_bucket)) &&
      output.nombre_del_bucket == module.almacenamiento.configuracion_efectiva.nombre
    )
    error_message = "El root debe publicar nombre y ARN: son el contrato del grafo de aplicacion."
  }
}

run "cors_se_crea_solo_si_hay_origenes" {
  command = plan
  variables {
    origenes_cors = ["https://ejemplo.invalid"]
  }
  assert {
    condition     = module.almacenamiento.configuracion_efectiva.reglas_cors == 1
    error_message = "Con una lista no vacia debe crearse exactamente una configuracion CORS."
  }
}

run "comodin_cors_rechazado" {
  command = plan
  variables {
    origenes_cors = ["*"]
  }
  expect_failures = [var.origenes_cors]
}

run "region_no_comercial_rechazada" {
  command = plan
  variables {
    region = "local-1"
  }
  expect_failures = [var.region]
}

run "nombre_de_bucket_invalido_rechazado" {
  command = plan
  variables {
    nombre_del_bucket = "NoValido_Mayusculas"
  }
  expect_failures = [var.nombre_del_bucket]
}

run "expiracion_menor_que_un_dia_rechazada" {
  command = plan
  variables {
    dias_para_expirar_versiones = 0
  }
  expect_failures = [var.dias_para_expirar_versiones]
}

run "laboratorio_usa_el_mismo_modulo" {
  command = plan
  variables {
    region                      = "us-east-1"
    laboratorio                 = true
    cuentas_permitidas          = []
    nombre_del_bucket           = "blog-lab-medios"
    forzar_destruccion          = true
    dias_para_expirar_versiones = 1
    endpoints_aws = {
      s3  = "http://127.0.0.1:4566"
      sts = "http://127.0.0.1:4566"
    }
  }
  assert {
    condition = (
      module.almacenamiento.configuracion_efectiva.ownership == "BucketOwnerEnforced" &&
      module.almacenamiento.configuracion_efectiva.versionado == "Enabled" &&
      module.almacenamiento.configuracion_efectiva.cifrado == "AES256" &&
      module.almacenamiento.configuracion_efectiva.bpa.restrict_public_buckets
    )
    error_message = "El laboratorio debe usar el MISMO modulo y las mismas protecciones que produccion."
  }
  assert {
    condition     = module.almacenamiento.configuracion_efectiva.force_destroy
    error_message = "El laboratorio necesita force_destroy para reconstruirse en cada ciclo."
  }
}
