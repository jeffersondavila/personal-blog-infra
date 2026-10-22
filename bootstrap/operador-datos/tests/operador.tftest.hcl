# Pruebas OFFLINE del diseno de la identidad operativa minima (H-031-1, DH-3).
# Provider simulado: no hay red, no hay AWS y no se crea ningun IAM.
#
# Lo que NO demuestran: que AWS evalue la politica como aqui se lee, que el trust
# permita asumir el rol con la sesion real del usuario de entrada, ni que cada
# accion que Terraform necesita este concedida. Eso se comprueba en H-031-IAM con
# el simulador de politicas de IAM y con el readback, y cualquier AccessDenied
# durante H-031-2/H-031-3 es STOP, nunca una ampliacion por conveniencia.

mock_provider "aws" {
  override_during = plan
  mock_data "aws_caller_identity" {
    defaults = {
      account_id = "123456789012"
      arn        = "arn:aws:sts::123456789012:assumed-role/PersonalBlogAdministrator/bootstrap"
    }
  }
}

variables {
  expected_account_id        = "123456789012"
  crear_rol_vinculado_de_rds = true
}

run "trust_exacto_con_mfa_y_sesion_corta" {
  command = plan

  assert {
    condition = (
      aws_iam_role.operador_datos.name == "PersonalBlogDataOperator" &&
      aws_iam_role.operador_datos.max_session_duration == 3600
    )
    error_message = "El rol operativo se llama PersonalBlogDataOperator y su sesion dura como maximo 3600 s."
  }

  assert {
    condition = jsondecode(aws_iam_role.operador_datos.assume_role_policy) == {
      Version = "2012-10-17"
      Statement = [{
        Sid       = "UsuarioDeEntradaConMfa"
        Effect    = "Allow"
        Principal = { AWS = "arn:aws:iam::123456789012:user/personal-blog-entry-admin" }
        Action    = "sts:AssumeRole"
        Condition = { Bool = { "aws:MultiFactorAuthPresent" = "true" } }
      }]
    }
    error_message = "El trust solo admite al usuario de entrada, por ARN exacto y con MFA."
  }
}

run "politica_minima_de_la_fase_1" {
  command = plan

  assert {
    condition = (
      toset(keys(aws_iam_policy.fase_1)) == toset(["Red", "RdsYCustodia", "Denegaciones"]) &&
      toset(keys(aws_iam_role_policy_attachment.fase_1)) == toset(["Red", "RdsYCustodia", "Denegaciones"]) &&
      alltrue([for a in aws_iam_role_policy_attachment.fase_1 : a.role == "PersonalBlogDataOperator"])
    )
    error_message = "Tres politicas administradas, adjuntas solo al rol operativo."
  }

  assert {
    condition     = alltrue([for p in aws_iam_policy.fase_1 : length(p.policy) < 6144 && p.path == "/personal-blog/"])
    error_message = "Cada politica administrada debe caber en el limite de 6 144 caracteres de IAM."
  }

  assert {
    condition = alltrue([
      for s in flatten([for p in aws_iam_policy.fase_1 : jsondecode(p.policy).Statement]) :
      s.Effect == "Deny" || alltrue([for a in flatten([s.Action]) : !endswith(a, "*")])
    ])
    error_message = "Ningun Allow concede acciones con comodin."
  }

  assert {
    condition = alltrue([
      for s in flatten([for p in aws_iam_policy.fase_1 : jsondecode(p.policy).Statement]) :
      s.Effect == "Deny" || alltrue([for a in flatten([s.Action]) : contains(["ec2", "rds", "ssm", "logs", "s3"], split(":", a)[0])])
    ])
    error_message = "La fase 1 solo concede EC2, RDS, SSM, Logs y el state en S3: nada de IAM, STS, KMS, Lambda ni CloudWatch."
  }

  assert {
    condition = alltrue([
      for s in flatten([for p in aws_iam_policy.fase_1 : jsondecode(p.policy).Statement]) :
      s.Effect == "Deny" || flatten([s.Resource]) != ["*"] || alltrue([for a in flatten([s.Action]) : can(regex("^[a-z0-9]+:(Describe|List)", a))])
    ])
    error_message = "Resource \"*\" solo se admite para lecturas Describe/List que AWS no permite acotar por recurso."
  }

  assert {
    condition = alltrue([
      for s in flatten([for p in aws_iam_policy.fase_1 : jsondecode(p.policy).Statement]) :
      s.Effect == "Deny" || startswith(flatten([s.Action])[0], "s3:") || try(s.Condition.StringEquals["aws:RequestedRegion"], "") == "us-east-2"
    ])
    error_message = "Todo Allow regional exige aws:RequestedRegion = us-east-2."
  }

  assert {
    condition = alltrue([
      for s in flatten([for p in aws_iam_policy.fase_1 : jsondecode(p.policy).Statement]) :
      s.Effect == "Deny" || !startswith(flatten([s.Action])[0], "s3:") || alltrue([
        for r in flatten([s.Resource]) : contains([
          "arn:aws:s3:::${output.bucket_de_estado}",
          "arn:aws:s3:::${output.bucket_de_estado}/application/data/terraform.tfstate",
          "arn:aws:s3:::${output.bucket_de_estado}/application/data/terraform.tfstate.tflock",
        ], r)
      ])
    ])
    error_message = "En S3 solo el bucket de state y la key del root de datos con su lock."
  }

  assert {
    condition     = output.bucket_de_estado == "personal-blog-tfstate-us-east-2-${substr(sha256("personal-blog:terraform-state:123456789012:us-east-2"), 0, 12)}"
    error_message = "El bucket de state se deriva igual que en bootstrap/terraform-state."
  }

  assert {
    condition = toset([for s in flatten([for p in aws_iam_policy.fase_1 : jsondecode(p.policy).Statement]) : s.Sid if s.Effect == "Deny"]) == toset([
      "SinSalidaPublicaNiComputo",
      "SinBorradoDeProduccion",
      "SinBorrarLaInstanciaProductiva",
      "SinRdsPublico",
      "SinSecretsManagerAdministrado",
      "SinServiciosRdsExcluidos",
      "SinIdentidadesNiClavesNuevas",
    ])
    error_message = "Las siete denegaciones explicitas deben estar presentes."
  }

  assert {
    condition = alltrue([
      for s in flatten([for p in aws_iam_policy.fase_1 : jsondecode(p.policy).Statement]) :
      s.Effect == "Deny" || alltrue([for a in flatten([s.Action]) : !startswith(a, "iam:")])
    ])
    error_message = "El operador no recibe NINGUNA accion IAM, ni de lectura ni iam:SimulatePrincipalPolicy: la simulacion se hace desde el bootstrap (H-031-1A)."
  }

  assert {
    condition = alltrue([
      for s in flatten([for p in aws_iam_policy.fase_1 : jsondecode(p.policy).Statement]) :
      s.Effect == "Deny" || !contains(flatten([s.Action]), "ec2:CreateTags") ||
      can(s.Condition.StringEquals["ec2:CreateAction"]) || can(s.Condition.StringEquals["aws:ResourceTag/Componente"])
    ])
    error_message = "Etiquetar solo al crear o sobre recursos ya propios: nada de reclamar recursos sin etiquetas (H-031-1A)."
  }

  assert {
    condition = alltrue([
      for s in flatten([for p in aws_iam_policy.fase_1 : jsondecode(p.policy).Statement]) : !can(s.Condition.Null)
    ]) && !contains([for s in flatten([for p in aws_iam_policy.fase_1 : jsondecode(p.policy).Statement]) : s.Sid], "ReclamarElGrupoPorOmisionDeLaVpcNueva")
    error_message = "Ninguna sentencia puede depender de la AUSENCIA de etiquetas (H-031-1A)."
  }

  assert {
    condition = alltrue([
      for s in flatten([for p in aws_iam_policy.fase_1 : jsondecode(p.policy).Statement]) :
      s.Effect == "Deny" || !contains(flatten([s.Action]), "ec2:RevokeSecurityGroupIngress")
    ])
    error_message = "La fase 1 no revoca reglas de entrada: solo lo exigia el grupo por omision, que ya no se gestiona."
  }

  assert {
    condition     = alltrue([for p in aws_iam_policy.fase_1 : !strcontains(p.policy, "iam:PassRole")])
    error_message = "La fase 1 no concede PassRole: llega en H-031-5, acotado al rol de la ejecutora."
  }

  assert {
    condition = alltrue([
      for s in flatten([for p in aws_iam_policy.fase_1 : jsondecode(p.policy).Statement]) :
      s.Effect == "Deny" || !contains(flatten([s.Action]), "ec2:CreateVpcEndpoint") || (
        flatten([s.Action]) == ["ec2:CreateVpcEndpoint"] && (
          (
            flatten([s.Resource]) == ["arn:aws:ec2:us-east-2:123456789012:vpc-endpoint/*"] &&
            try(s.Condition.StringEquals["ec2:VpceServiceName"], "") == "com.amazonaws.us-east-2.s3"
          ) ||
          (
            alltrue([for r in flatten([s.Resource]) : can(regex(":(vpc|route-table)/\\*$", r))]) &&
            try(s.Condition.StringEquals["aws:ResourceTag/Componente"], "") == "datos"
          )
        )
      )
    ])
    error_message = "CreateVpcEndpoint solo en sentencias propias: el endpoint nuevo exige el servicio S3 y la VPC y las tablas deben ser propias (S-10)."
  }

  assert {
    condition = alltrue([
      for s in flatten([for p in aws_iam_policy.fase_1 : jsondecode(p.policy).Statement]) :
      s.Effect == "Deny" || !contains(flatten([s.Action]), "ec2:ModifyVpcEndpoint") ||
      alltrue([for r in flatten([s.Resource]) : can(regex(":(vpc-endpoint|route-table)/\\*$", r))])
    ])
    error_message = "ModifyVpcEndpoint solo sobre endpoints y tablas de rutas propias, sin subredes ni grupos (S-10)."
  }
}

run "rol_vinculado_solo_si_falta" {
  command = plan
  variables {
    crear_rol_vinculado_de_rds = false
  }
  assert {
    condition     = length(aws_iam_service_linked_role.rds) == 0
    error_message = "Si AWSServiceRoleForRDS ya existe no se gestiona ni se importa."
  }
}

run "rol_vinculado_creado_explicitamente" {
  command = plan
  assert {
    condition     = length(aws_iam_service_linked_role.rds) == 1 && aws_iam_service_linked_role.rds[0].aws_service_name == "rds.amazonaws.com"
    error_message = "Sin el rol vinculado, el primer CreateDBInstance pediria iam:CreateServiceLinkedRole al operador."
  }
}

run "solo_la_identidad_administrativa_hace_el_bootstrap" {
  command = plan
  override_data {
    target = data.aws_caller_identity.bootstrap
    values = {
      account_id = "123456789012"
      arn        = "arn:aws:sts::123456789012:assumed-role/PersonalBlogDataOperator/sesion"
    }
  }
  expect_failures = [data.aws_caller_identity.bootstrap]
}

run "otra_region_rechazada" {
  command = plan
  variables {
    aws_region = "us-east-1"
  }
  expect_failures = [var.aws_region]
}

run "cuenta_marcador_rechazada" {
  command = plan
  variables {
    expected_account_id = "000000000000"
  }
  expect_failures = [var.expected_account_id]
}
