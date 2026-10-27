# TASK-031 — Reporte

| Campo | Valor |
| --- | --- |
| Tarea | `Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch` |
| Estado | **Aprobada — 2026-10-21**, mediante `approved: Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`, con la aceptación expresa de las excepciones 5, 6 y 8 ([§52](#52-aprobación-y-cierre-2026-10-21)). Cierre técnico en §51; matriz final en §51.16. *Estado anterior, conservado como historia:* **En progreso** — H-031-1 completado; **H-031-1A READY FOR H-031-IAM** (2026-10-03), tras un primer ciclo rechazado por drift no declarado (§14.5) y su resolución demostrada (§15); H-031-IAM: plan revisado (§16) y **aplicado** —8 recursos IAM creados, readback verde—, pero **BLOQUEADO en la simulación** por S-10 (§17). Corrección S-10 diseñada y simulada en verde; su plan de reparación (0/1/0) quedó bloqueado por `resource_drift` de metadatos (§18). Plan refresh-only preparado (§19) y aplicado: **exit 1** por `templatefile` inconsistente, pero el state **sí** quedó escrito con exactamente los cinco metadatos (§20); el usuario lo **aceptó** por esa evidencia. State aceptado y nuevo plan (§21). S-10 aplicada y verificada (§22); preparación del login detenida (§23). **H-031-IAM COMPLETE** (§24): por **decisión operacional del usuario**, las operaciones restantes usan `personal-blog` / `PersonalBlogAdministrator` y `personal-blog-datos` no se configura. **H-031-2-ALIGN READY** (§25): `terraform-datos` y su guarda exigen exactamente `PersonalBlogAdministrator`; procedimiento de la contraseña efímera definido. **H-031-2 PLAN READY FOR APPLY REVIEW** (§26): plan 21/0/0, `PLAN_OK`, sin drift, `SECRET_ABSENT`; sin apply |
| Rama | `Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`, desde `main` `6c31d1d` |
| Ficha | [TASK-031](../tasks/TASK-031-deploy-network-rds-ssm-cloudwatch.md) |

## 1. Resumen histórico de H-031-1

Trabajo **exclusivamente offline**, como autorizó el usuario: módulos `red` y `base_de_datos`,
root `terraform-datos`, pruebas, guarda del plan, control negativo de DH-2, laboratorio de
**tres roots** ejecutado de verdad contra Floci, diseño exacto de la identidad operativa mínima
en código **no aplicado**, CI y documentación durable.

**No se hizo**: ninguna llamada mutante a AWS, ningún STS operativo, ningún IAM, ningún `init`
remoto, ningún state ni `.tflock` remoto, ninguna contraseña real, ningún plan contra AWS,
ningún apply. Ni commit, ni push, ni PR. Backend y frontend intactos.

## 2. Preparación Git (2026-10-01)

`fetch --prune`, `switch main`, `pull --ff-only`: `main == origin/main == 6c31d1d`, árbol limpio,
`dev` contenía a `main` (0 commits de `main` ausentes en `dev`) y `git diff main dev` vacío. Rama
creada desde `main`; `HEAD == main`. Backend `9692796` y frontend `7dce98a` en `main == origin/main`,
limpios. Sin ramas Task ni PR abiertos.

## 3. Autorización H-031-1 (2026-10-03)

| Decisión | Resolución del usuario |
| --- | --- |
| DH-1 | **Aprobada**: root `terraform-datos`, dueño único de VPC, subredes, rutas, endpoint, grupos, DB subnet group, *parameter group*, grupo de logs, instancia y SecureString; key `application/data/terraform.tfstate`; sin `terraform_remote_state`; orden medios → datos → aplicación; documentar la enmienda a §12.2 |
| DH-2 | **Aprobada**: variable efímera, `password_wo`, `password_wo_version`, SecureString con `value_wo` y `aws/ssm`; demostrarlo offline antes de H-031-2 |
| DH-3 | **Modificada**: no a `PersonalBlogAdministrator`; diseñar la identidad operativa mínima; nuevo checkpoint **H-031-IAM** |
| DH-4 | **Aprobada con condiciones** (orderabilidad en H-031-2, endpoint compatible con el `export` de D-24, sin `SourceVpce` en el bucket, sin IGW/NAT/EIP/IPv4 pública, 14 días como baseline de D-11) |
| DH-5 | **Aprobada**: laboratorio antes de H-031-3, sin tratar Floci como evidencia de RDS |
| DH-6 | **Aprobada con frontera**: la ejecutora es de Task/031, solo en H-031-5 |

## 4. Archivos

**Nuevos (34)**

| Ruta | Qué |
| --- | --- |
| `terraform/modulos/red/{main,variables,outputs}.tf` | VPC, SG por omisión no gestionado ni usado (H-031-1A), 2 subredes, 2 tablas y asociaciones, gateway endpoint S3 con política acotada, 3 grupos, 5 reglas |
| `terraform/modulos/base_de_datos/{main,variables,outputs}.tf` | DB subnet group, *parameter group* `postgres17`, grupo de logs, instancia, SecureString |
| `terraform-datos/{versions,providers,variables,main,outputs}.tf` | Root de datos, guarda de identidad, validaciones |
| `terraform-datos/.terraform.lock.hcl` | Lock idéntico al de los otros roots (6.64.0, Linux y Windows) |
| `terraform-datos/backend-s3.tfbackend.example` | Key `application/data/terraform.tfstate` |
| `terraform-datos/entornos/{local/local.tfvars,produccion/produccion.tfvars.example}` | Destinos |
| `terraform-datos/tests/datos.tftest.hcl` | 22 pruebas offline |
| `scripts/terraform_datos/check_plan.py` | Guarda offline del plan de H-031-3 |
| `scripts/terraform_datos/check_plan_operador.py` · `tests/terraform_datos/test_check_plan_operador.py` | Guarda del plan de H-031-IAM y sus 28 regresiones (§16.1) |
| `scripts/terraform_datos/check_plan_operador_repair.py` · `tests/terraform_datos/test_check_plan_operador_repair.py` | Guarda separada de la reparación S-10 y sus 15 regresiones (§18) |
| `scripts/terraform_datos/historico/fase-1-red.h031iam-aplicada.json.tftpl` | Copia intacta de la política Red aplicada en H-031-IAM (§18.3) |
| `tests/terraform_datos/{simulacion_de_politicas,test_simulacion_de_politicas}.py` | Evaluador offline y matriz de 62 casos compartida con `simulate-custom-policy` (§18.3) |
| `scripts/terraform_datos/check_plan_operador_refresh.py` · `tests/terraform_datos/test_check_plan_operador_refresh.py` | Guarda separada del refresh-only y sus 19 regresiones (§19.4) |
| `tests/terraform_datos/{test_check_plan,test_secretos,test_grupo_por_omision}.py` | 27 pruebas de la guarda, 5 de no uso del grupo por omisión y control negativo de DH-2 |
| `bootstrap/operador-datos/{versions,providers,variables,main,outputs}.tf` | Identidad operativa, **no aplicada** |
| `bootstrap/operador-datos/politicas/fase-1-{red,rds-y-custodia,denegaciones}.json.tftpl` | Texto exacto de los permisos |
| `bootstrap/operador-datos/{.terraform.lock.hcl,backend-s3.tfbackend.example,tests/operador.tftest.hcl}` | Lock, key `bootstrap/operador-datos/terraform.tfstate`, 7 pruebas |
| `docs/architecture/identidad-operativa-datos.md` | Diseño exacto y propuesta de H-031-IAM |
| `docs/tasks/TASK-031-…md`, este reporte | Ficha y reporte |

**Modificados (20 + STATUS/ROADMAP/STAGE-10)**: `.gitignore`, `ci-infra.yml`, Compose del
laboratorio, `scripts/laboratorio/{destino,inventario,laboratorio,verificacion}.py`, cuatro
archivos de `tests/laboratorio/`, `aws-local-parity.md`, `open-decisions.md`, el paquete de
decisiones, el runbook del bucket de estado y los cinco runbooks del laboratorio.

## 5. Root y propiedad del state

| Root | Key | Dueño de | Recibe | Publica |
| --- | --- | --- | --- | --- |
| `terraform-medios` | `application/media/terraform.tfstate` | Bucket de medios | — | Nombre y ARN |
| **`terraform-datos`** | **`application/data/terraform.tfstate`** | Los 21 recursos de §6 | `arn_del_bucket_de_medios` | VPC, subredes, `sg-lambda`/`sg-admin`/`sg-rds`, endpoint, prefix list, endpoint y ARN de RDS, nombre del SecureString |
| `terraform` (aplicación) | por fijar | Lambda, API, parámetros, logs, rol | Contrato de medios; el de datos en Task/032 | — |
| **`bootstrap/operador-datos`** | **`bootstrap/operador-datos/terraform.tfstate`** | Rol operativo, 3 políticas, 3 adjuntos y, si falta, el rol vinculado de RDS | — | ARN del rol, huellas de las políticas |

El lanzador comprueba sobre los states reales que ningún recurso está en dos states y que red y
RDS solo los administra datos.

## 6. Recursos previstos del primer apply vigente (21, H-031-1A)

`aws_vpc`, 2 `aws_subnet`, 2 `aws_route_table`,
2 `aws_route_table_association`, `aws_vpc_endpoint` (Gateway S3), 3 `aws_security_group`,
2 `aws_vpc_security_group_ingress_rule`, 3 `aws_vpc_security_group_egress_rule`,
`aws_db_subnet_group`, `aws_db_parameter_group`, `aws_cloudwatch_log_group`, `aws_db_instance`,
`aws_ssm_parameter`. Ningún IGW, NAT, EIP, endpoint de interfaz, CMK, Proxy ni IAM.

El grupo por omisión no se gestiona, etiqueta, vacía ni referencia: aislamiento por **no uso**.
RDS lleva exclusivamente `sg-rds`; Task/032 adjuntará explícitamente `sg-lambda` y H-031-5,
`sg-admin`. El endpoint S3 es Gateway, sin `security_group_ids` ni `subnet_ids`.

## 7. DH-2 — la contraseña no sale por ningún camino

| Capa | Evidencia |
| --- | --- |
| Diseño | Variable `ephemeral` y `sensitive`; solo alimenta `password_wo` y `value_wo` |
| Estructural | `test_secretos.py`: cuatro fugas deliberadas —salida sin marcar, salida sensible, atributo no *write-only*, local hacia una salida— **rechazadas por Terraform**; la copia sin fuga valida |
| Plan real (Floci) | La variable **no aparece** en `variables` del plan JSON; `password`, `password_wo` y `value_wo` nulos. Canario **ausente** del plan JSON y del plan binario |
| State real (Floci) | Canario **ausente** del archivo de state, de `show -json` y de `output -json`; `value` del SecureString vacío |
| Ciclo del laboratorio | El lanzador busca el canario tras cada plan y cada apply del root de datos; dos aplicaciones completas sin abortar |
| Guarda productiva | `check_plan.py` rechaza `EPHEMERAL_LEAK` y `SECRET_IN_PLAN` |

## 8. Hallazgos históricos de H-031-1 y cómo se resolvieron

| # | Hallazgo | Resolución, sin deformar el diseño de AWS |
| --- | --- | --- |
| 1 | Floci 2.1.0 lanza un contenedor `postgres:16-alpine` **por etiqueta** al crear RDS: descarga fuera del perímetro y sin digest | `FLOCI_SERVICES_RDS_MOCK=true` en el Compose: plano de control sin motor |
| 2 | Floci publica los ID de zona como `us-east-1-az1`; AWS, como `use1-az1` | Valor en `local.tfvars`; validación ampliada a los dos formatos. **Cambio de configuración** en la matriz |
| 3 | Con `skip_requesting_account_id` las reglas guardaban `000000000000/sg-…` y el plan nunca convergía | El root de datos pide su cuenta también en el laboratorio: se parece **más** a AWS |
| 4 | Floci **no aplica** `RevokeSecurityGroupEgress`: los cuatro grupos gestionados entonces conservaban `0.0.0.0/0` de salida (historia H-031-1; H-031-1A gestiona solo los tres explícitos) | El provider la revoca siempre (código v6.64.0). **AWS-only**: se demuestra en el readback de H-031-3 |
| 5 | Floci con RDS *mock* no devuelve 7 atributos de la instancia, los parámetros del grupo ni `KeyId`/`Tier` del SecureString | Tolerados por tipo y atributo en el verificador del laboratorio (`DIFERENCIAS_DEL_DESTINO_LOCAL_DE_DATOS`), **nunca** `ignore_changes`. En AWS se exige 0/0/0 |
| 6 | Al aplicar un plan guardado, Terraform **exige volver a aportar la variable efímera** y rechaza repetir las demás | Archivo propio de efímeras en el laboratorio. **En producción, `TF_VAR_contrasena_master` en el plan y otra vez en el apply** |
| 7 | La política única de la identidad medía 10 610 caracteres; el límite agregado de las inline es 10 240 | Tres políticas administradas, cada sentencia idéntica: 4 446, 4 015 y 2 225 caracteres |
| 8 | Una validación indexaba `["b"]` y fallaba con un mapa de una sola subred | Validación por `distinct`, robusta para cualquier mapa |
| 9 | El provider simulado genera valores distintos en plan y apply | La búsqueda del canario pasó al control negativo estructural y al laboratorio |
| 10 | En el laboratorio, el segundo plan muestra `resource_drift` en los tres grupos (`ingress`/`egress` reflejan las reglas gestionadas aparte) | Observación exclusiva de Floci; no predice el drift de AWS. Si AWS demuestra `resource_drift`, se aplica el procedimiento condicionado de DN-2 |

## 9. Guarda del plan productivo

`check_plan.py` exige: Terraform 1.16.2, plan completo, sin drift ni diferidos; variables de
producción —región, cuenta, rol operativo, prefijo, contrato de medios, protecciones, red,
etiquetas, sin endpoints alternativos— y la efímera ausente; guarda de identidad en `pass`; las
**21 direcciones exactas**, solo `create`, sin import ni move; **ningún** `0.0.0.0/0` ni `::/0` en
ningún atributo; los valores de D-22/D-23/D-10/DH-4 de la instancia, el *parameter group*, el
grupo de logs, el endpoint y su política, las reglas y el SecureString; salidas no sensibles.
**27 pruebas** con controles negativos. H-031-1A inspecciona `configuration` y exige el
wiring RDS → `var.id_sg_rds` → `module.red.id_sg_rds` → `aws_security_group.rds.id`,
sin referencias adicionales, y rechaza el grupo por omisión o SG/subredes en el endpoint.
La prueba estática complementa las referencias JSON comprobando la lista literal única de RDS.
En H-031-1 la guarda anterior aceptó el plan real del laboratorio traducido mecánicamente
a valores de producción; esa evidencia histórica no sustituye los gates de H-031-1A.

## 10. Laboratorio histórico de tres roots — H-031-1, antes del hardening

**Exploración controlada** (scratchpad, fuera del repo): 22 altas, apply, segundo plan, state
inspeccionado, 22 bajas; de ahí los hallazgos 1 a 5 y 10.

**Ciclo completo real** con el lanzador modificado, el 2026-10-03, con el ZIP de Task/030
(`sha256 0234fcc4…09764a`, ruta ignorada del backend):

| Fase | Resultado |
| --- | --- |
| Primer intento | Medios aplicado (8); el apply de datos se detuvo antes de crear nada por el hallazgo 6. Corregido |
| Creación | Medios sin cambios; datos **22** altas; aplicación **13** altas |
| Ownership | Disjunto en los tres states: aplicación no administra S3, red ni RDS |
| Servicios | Camino crítico `GET /health` **HTTP 200**; SDK `boto3/1.43.82` |
| Idempotencia | Medios **exit 0**; aplicación **exit 0**; datos **exit 2 solo** por las 10 diferencias declaradas del emulador |
| Drift controlado | SSM ficticio retirado y reconciliado (1 alta) |
| Primer destroy | 13 → 22 → 8, en orden inverso; ausencia en **12** categorías de los tres roots |
| Reconstrucción | 8 + 22 + 13; *smoke* HTTP 200 |
| Segundo destroy | 13 → 22 → 8; ausencia en 12 categorías |
| Canario | No apareció en ningún plan, state ni salida del root de datos |
| Retirada | `bajar`: cero contenedores, redes y volúmenes del laboratorio y del emulador |

**Lo que el laboratorio NO demuestra**: aislamiento de red, revocación de salidas, TLS, KMS,
backups, PITR, IAM ni permisos efectivos. Matriz de paridad actualizada en consecuencia.

## 11. Gates históricos de H-031-1

| Gate | Resultado |
| --- | --- |
| `fmt -check` en los seis roots y en `terraform/modulos` | OK |
| `init -backend=false -lockfile=readonly` y `validate` en los seis roots | OK; locks existentes sin cambios |
| `terraform test` | datos **22/22**, operador **7/7**, medios 7/7, terraform-state 5/5, github-oidc 9/9 |
| Python | laboratorio **263 OK**, terraform_datos **24 OK**, terraform_state 12 OK, oidc 60 OK (1 *skip* de plataforma), security 88 OK |
| Acciones IAM | Las de las tres políticas **existen** en la referencia de servicios de AWS (2026-10-03) |
| Gitleaks 8.30.1 (ZIP verificado contra el SHA del repo) | Sin hallazgos en 324 archivos del entregable; control positivo detectado |
| Cuentas reales | Ningún ID de 12 dígitos salvo los ficticios |
| `git diff --check`, CRLF, espacios finales | Limpio |

## 12. Decisiones humanas nuevas

| ID | Decisión | Recomendación |
| --- | --- | --- |
| **DN-1** | Autorizar **H-031-IAM** con el diseño de [identidad-operativa-datos.md](../architecture/identidad-operativa-datos.md): rol `PersonalBlogDataOperator`, trust al usuario de entrada **sin modificarlo**, tres políticas administradas bajo `/personal-blog/`, rol vinculado de RDS creado por el bootstrap si falta, key `bootstrap/operador-datos/terraform.tfstate` | Autorizar |
| **DN-2** | Preferencia registrada: **refresh-only solo si AWS demuestra `resource_drift`** en H-031-3. STOP, capturar evidencia, generar el plan refresh-only, revisar su JSON y pedir autorización explícita antes de aplicarlo. Meta: **0/0/0 y `resource_drift = 0`** | **No autorizado por adelantado**; Floci no predice qué drift habrá en AWS |
| **DN-3** | **Cerrada por eliminación del problema** en H-031-1A: grupo por omisión no gestionado ni usado; sentencia de reclamación ausente y sin `RevokeSecurityGroupIngress` en Allow | Eliminada por diseño; **no hay aceptación del riesgo anterior** |

## 13. Estado

En progreso. **H-031-1A READY FOR H-031-IAM** (§15.7). Historia conservada: un primer
ciclo se **rechazó** por `domain_dns_ips: null → []` no declarado (§14.5); no se amplió
ninguna tolerancia de forma automática; se investigó la causa (§15.1) y solo después se adoptó
la resolución demostrada, con un ciclo nuevo y todos los gates en verde.
H-031-IAM: plan guardado de 8 creates revisado (§16) y **aplicado** con autorización explícita
(§17): readback verde, **simulación en STOP por S-10**. La corrección está diseñada y simulada en
verde, pero su plan de reparación quedó bloqueado por `resource_drift` de metadatos (§18). El plan
refresh-only (§19) se aplicó: terminó con **exit 1** (`templatefile` inconsistente), pero persistió
el state con exactamente los cinco metadatos, verificado por comparación de versiones (§20). El
usuario aceptó ese state y hay un **nuevo plan S-10** (0/1/0, solo Red, `resource_drift = 0`,
`REPAIR_PLAN_OK`) (§21), **aplicado** con autorización explícita (§22): Red corregida viva, simulación
contra el rol real 62/62, Access Analyzer sin hallazgos y convergencia 0/0/0 sin drift.
**H-031-IAM COMPLETE** (§24): el usuario decidió no configurar `personal-blog-datos` y continuar Task/031 con
`personal-blog` / `PersonalBlogAdministrator`; el operador se conserva creado y validado, sin uso operativo. **H-031-2-ALIGN READY** (§25): `terraform-datos` y
`check_plan.py` exigen ya exactamente `PersonalBlogAdministrator`, y el procedimiento de la contraseña efímera está
definido. **H-031-2 PLAN READY FOR APPLY REVIEW** (§26): plan guardado 21/0/0 con `PLAN_OK`, sin drift y
sin apply. **H-031-3 BLOQUEADO antes del apply** (§27): la orderability volvió a mostrar solo `us-east-2c`;
no se generó la contraseña real ni se aplicó nada. El diagnóstico de solo lectura (§27.3) dio
**STABLE FOR TARGET AZ**: 6/6 en `us-east-2a`, la zona fijada por el código. Reintento con el gate corregido:
**H-031-3 APPLY FAILED / RECOVERY REVIEW REQUIRED** (§27.4). Se crearon 20 de 21 recursos y la instancia RDS no:
RDS no permite modificar `superuser_reserved_connections`. **H-031-3-RECOVERY** (§28): D-22 corregida (seis parámetros
explícitos, preflight del catálogo), plan de recuperación 2/0/1 con la contraseña ya custodiada y SSM `no-op`;
**DN-2 DRIFT REVIEW REQUIRED** por `resource_drift = 4`. Sin apply. **H-031-3-RECOVERY-DN2** (§29): el refresh-only
cumple los cuatro drift exactos y conserva el taint, pero su guarda lo **rechaza por `OUTPUTS`** (seis salidas de RDS).
Sin apply. **H-031-3-RECOVERY-DN2-OUTPUTS** (§30): contrato de salidas ampliado por decisión del usuario; el mismo plan
da `DN2_REFRESH_PLAN_OK` → **H-031-3 DN-2 REFRESH PLAN READY**. Sin apply. **§31**: refresh-only aplicado (solo state,
serial 2, taint conservado, AWS sin cambios) y nuevo plan de recuperación 2/0/1 con `RECOVERY_PLAN_OK` y drift 0 →
**H-031-3 DN-2 REFRESH APPLIED / RECOVERY PLAN READY**. Sin recovery apply. **§32**: recovery apply **exit 1**: parameter
group reemplazado, pero `CreateDBInstance` rechazado por `FreeTierRestrictionError` (retención de backups) →
**H-031-3 RECOVERY APPLY FAILED / REVIEW REQUIRED**; 20/21, sin taint, sin RDS. **§33**: cuenta en plan `FREE`
(`ACTIVE`, expira 2027-03-15, 120 USD); `FREE_PLAN_RETENTION_MAX = UNKNOWN`; parameter group reducido a cuatro
parámetros con tres invariantes de sistema verificadas → **H-031-3 RECOVERY-2 DECISION READY**. **§34**: cuenta en FREE
con retención temporal de 1 día; plan 1/1/0 sin destroy ni replace, pero `resource_drift = 1` (representación de dos
invariantes) → **RECOVERY-3-FREE DRIFT REVIEW REQUIRED**. Sin apply. **§35**: excepción exacta de ese único drift en la
guarda; el mismo plan da `RECOVERY_3_FREE_PLAN_OK` → **H-031-3 RECOVERY-3-FREE PLAN READY**. Sin apply. **§36**: apply
interrumpido por `ExpiredToken`; **RDS existe y está `available`**, pero el state remoto sigue en serial 3 sin ella
(`errored.tfstate` local, instancia `tainted`) y el lock quedó retenido → **RECOVERY-3-FREE APPLY FAILED / REVIEW REQUIRED**.
**§37**: lock liberado y state restaurado con `state push` sin `-force` (21/21, serial 6); readback 39/40 por el registro
incompleto de la instancia → **untaint retenido**, revisión requerida. **§38**: plan refresh-only que completa exactamente
36 atributos de la instancia contra AWS, sin cambios de infraestructura y conservando el taint →
**TAINTED INSTANCE REFRESH PLAN READY**. Sin apply. **§39**: STOP de frescura antes del apply, porque
`latest_restorable_time` avanza solo y la guarda exige igualdad con el describe fresco; nada cambió. **§40**: contrato
móvil para ese único atributo y criterio `ACTIONABLE_CONVERGENCE_OK`; el mismo plan da `INSTANCE_REFRESH_PLAN_OK` con un
describe fresco → **MOVING ATTRIBUTE CONTRACT READY**. Sin apply. **§41**: refresh-only aplicado (exit 0, state completo,
taint conservado), readback 40/40, custodia demostrada y untaint (0 taints); el plan de convergencia tiene la forma del
caso B, pero la guarda lo rechazó con `INCOMPLETE` por exigir `applyable = true` → **STATE REFRESHED / CONVERGENCE
REVIEW REQUIRED**. **§42**: guarda corregida con TDD (`applyable is False`); el **mismo** JSON da
`ACTIONABLE_CONVERGENCE_OK`, **caso B** (`resource_drift = 1`, solo `latest_restorable_time`); sin apply. **§43**:
pin durable nuevo para la gate de enlaces (`markdown-it-py` 4.2.0 y `mdurl` 0.1.2, con SHA-256, en
`scripts/security/requirements-markdown-links.txt`); gate completa con **0 enlaces rotos**, seguridad y regresión en
verde, sin cambios en AWS, state ni plan de convergencia → **H-031-3 COMPLETE**. **§44**: H-031-5 por fases; la
ejecutora privada (*shell* sin base de datos, solo `sg-admin`, IAM mínimo, RC=1) está implementada y probada
offline, sin plan productivo porque la cuota de Lambda sigue en 10 y la solicitud no se envió (rol vinculado
pendiente de decisión) → **H-031-5 IMPLEMENTATION READY / LAMBDA QUOTA PENDING**. **§45**: rol vinculado de Service
Quotas creado; AWS rechazó la solicitud a 101 porque exige un valor mayor que el por omisión (1000) →
**LAMBDA QUOTA REQUEST REJECTED / DECISION REQUIRED**. **§46**: REMAINDER; H-031-6 a H-031-9 preparados offline —ejecutora h0316 con `verify`, `identidades`, `sintetico` y `export`, integración local real, operador, restore PITR, alarmas de D-11 y rol de D-20 sin cablear, todo con pruebas— y ninguna llamada a AWS, porque la cuota de Lambda sigue bloqueando el root → **BLOCKERS REMAINING**. **§47**: con `terraform-datos` reordenado por decisión del usuario (ejecutora fuera del root hasta la cuota), las 8 alarmas de D-11 y el rol de D-20 se aplicaron en AWS. Hubo excepción puntual de la ventana móvil, dos refresh-only guardados aprobados y convergencia con las guardas originales. State en serial 12, 31/31; D-19 verificado para integrar; la alarma `memoria` en `ALARM` es un hallazgo de calibración; «Save & test» de Grafana: API de métricas validada y logs denegados por diseño; Explore con métricas reales de RDS: PASS → **H-031-8 y H-031-9 APLICADOS Y CONVERGENTES / BLOCKERS REMAINING** (B1, B3 y B4). **§48**: decisiones del usuario del 2026-10-16. B1: una única solicitud de cuota (1001); AWS abrió un caso (**CASE_OPENED**). B3: supervisión manual de solo lectura, con TDD y ejecución real en OK. B4: R-12 sigue abierto y documentado, con seguimiento en Task/040. H-031-5 preparado offline: guarda con la línea base real, fase `h0315`, refresh-only y recableado validado → **BLOCKERS REMAINING** (B1). La aprobación final sigue siendo
exclusivamente `approved: Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`.

## 14. H-031-1A — reanudación y hardening offline (2026-10-03)

### 14.1 Estado encontrado y trabajo conservado

Al retomar, la rama era la esperada y `HEAD == main == origin/main == 6c31d1d`;
ningún commit de Task/031. Había **23 archivos modificados y 34 nuevos**, sin staging.
Backend y frontend estaban en `main`, limpios. El bootstrap del operador no tenía backend
inicializado; el root de datos estaba configurado con backend **local**.
No se encontró evidencia local de ejecución de H-031-IAM ni de AWS real en H-031-1A.

Claude había dejado la eliminación del recurso de SG por omisión, la política IAM endurecida,
las pruebas estáticas y Terraform, la guarda de 21 direcciones y el flujo de simulación desde
bootstrap. Faltaba reconciliar documentos y completar la validación integral.

Su log `ciclo-h0311a.log` terminaba en **`[killed]`**. No quedaba proceso escritor activo;
Docker conservaba el emulador y dos redes. Los states registraban **medios 8, datos 20,
aplicación 0**; la API local sí mostraba RDS, aún sin instancia en el state. Este era un
**apply interrumpido**, no un ciclo aprobado ni un nuevo conteo esperado. Se conservaron
inventario, logs y states en custodia local ignorada y se retiró el laboratorio. El lock
`laboratorio.lock` conservaba el PID ya inexistente del proceso interrumpido: se archivó
tras verificar su ausencia; no se forzó un lock remoto.

### 14.2 Qué se completó y qué falló durante la revalidación

- Se reconciliaron ficha, reporte, STATUS, ROADMAP, etapa, arquitectura y runbooks. Los
  **22 recursos históricos** de H-031-1 permanecen identificados como historia; el estado
  vigente tiene **21**. La fila canónica de STATUS todavía decía Pendiente y ahora coincide
  con **En progreso**. Avance intacto: **30/41 ≈ 73 %**, ETAPA 10 **1/7 ≈ 14 %**.
- La guarda solo comparaba la primera referencia en dos tramos del wiring de SG. Una
  referencia adicional pasaba inadvertida. La nueva regresión falló en ambos tramos y
  pasa tras exigir las expresiones de referencia exactas. **27 pruebas de la guarda**.
  El plan real de creación local también pasó la comprobación de las **21 direcciones**,
  acciones `create` y wiring de SG; no se presentó como plan de AWS.
- La prueba positiva del healthcheck falló por una carrera de su servidor HTTP: cerraba
  tras un solo `recv`, aunque Bash aún enviaba la petición. Se reprodujo **3/20** veces
  (`SIGPIPE`). El servidor de prueba ahora lee hasta el final de las cabeceras; además
  rechaza salidas anómalas de Bash como resultado válido de un caso negativo. Resultado:
  **20/20** repeticiones y **7/7** casos pasan, sin cambiar la sonda de producción.
- Un intento del ciclo nuevo terminó por **timeout de RDS local**. Windows entró en
  suspensión/hibernación: los eventos del sistema y los saltos del log de Terraform
  (2 minutos → 40 → 242) lo acreditan. El último estado de RDS era `available`, pero el
  contexto del provider había vencido. Se conservaron el intento y sus states; no se
  aumentaron timeouts ni se relajaron pruebas. La recuperación usa destroy local con
  las guardas existentes y verificación de ausencia. El ensayo posterior mantiene una
  solicitud temporal contra suspensión automática, liberada al terminar.

### 14.3 Contrato vigente de red e IAM

El **default SG no se gestiona, etiqueta, vacía ni referencia**. Su aislamiento es por
**no uso**. Solo se gestionan `sg-lambda`, `sg-admin` y `sg-rds`; RDS lleva exclusivamente
`sg-rds`. Task/032 debe adjuntar explícitamente `sg-lambda`; H-031-5, `sg-admin`. El
endpoint S3 es Gateway, sin SG ni `subnet_ids`. La prueba estática comprueba la lista
única de RDS y la guarda comprueba sus referencias reales en `configuration`.

| Política de fase 1 | Sentencias | Caracteres renderizados |
| --- | ---: | ---: |
| Red | 6 | **3964** |
| RDS y custodia | 9 | **4015** |
| Denegaciones | 7 | **2225** |

**68 acciones Allow distintas, ninguna de IAM**. Ausentes la sentencia
`ReclamarElGrupoPorOmisionDeLaVpcNueva`, `Null` como condición y
`ec2:RevokeSecurityGroupIngress` en Allow. `ec2:RevokeSecurityGroupEgress` permanece
acotada a recursos propios para retirar la salida inicial de los tres SG explícitos.
Etiquetar un SG preexistente requiere pertenencia previa; el permiso de etiquetado al
crear exige `ec2:CreateAction` y las etiquetas del proyecto.

Los **128 nombres/patrones de acciones** se comprobaron sin red: referencia oficial de
servicios descargada el 2026-10-03 para todas las acciones Allow y los Deny disponibles;
los dos Deny sin archivo de referencia local (`sts:AssumeRole` y
`secretsmanager:CreateSecret`) se contrastaron con los modelos oficiales de botocore ya
incluidos en el ZIP canónico. Los patrones de IAM Deny tienen coincidencias en su catálogo.
Esto valida nombres, no autorización efectiva. Esta última sigue pendiente de H-031-IAM.

**Control negativo IAM:** reinyectar la sentencia original de reclamación en una copia
aislada produjo el **fallo de aserción esperado**, tanto por reclamar recursos sin
pertenencia como por depender de ausencia de etiquetas. La fuente entregable conservó
su política correcta. Los tests Terraform también comprueban tamaños menores que 6144.

**Simulación:** `PersonalBlogAdministrator` ejecutará `simulate-principal-policy` contra
`arn:aws:iam::<CUENTA>:role/PersonalBlogDataOperator` antes del cambio de contexto.
El operador no recibe `iam:SimulatePrincipalPolicy`, `iam:Get*` ni `iam:List*` para probarse.
Después solo se admiten STS, lecturas necesarias, dry-run y pruebas negativas que no
puedan mutar. La inexistencia de sus objetivos se verifica antes de las pruebas pertinentes.

**DN-2:** preferencia por refresh-only **si AWS demuestra drift**, no autorización previa.
En H-031-3: STOP → evidencia → plan refresh-only → revisión JSON → autorización explícita
→ apply de ese plan. Meta **0/0/0, `resource_drift = 0`**. No se extrapola Floci a AWS.
**DN-3:** cerrada por eliminación del problema; no queda un riesgo aceptado de reclamación.

### 14.4 Gates nuevos de H-031-1A

| Gate | Resultado verificado |
| --- | --- |
| Seis roots: fmt, init sin backend y lock readonly, validate | **PASS**; metadatos aislados y locks sin cambios |
| `terraform/modulos` fmt recursivo | **PASS** |
| Terraform tests | datos **22/22**, operador **7/7**, medios **7/7**, terraform-state **5/5**, github-oidc **9/9**; aplicación ejecuta test con **0 casos definidos** |
| Python | laboratorio **263 OK**, terraform_datos **34 OK** (27 guarda + 5 SG + 2 DH-2 con cuatro fugas), terraform_state **12 OK**, security **88 OK**, oidc **60 ejecutadas, 1 skip de plataforma** |
| Acciones, límites IAM y control negativo | **PASS**, con alcance de §14.3 |
| Compose del laboratorio | **PASS** |
| Gitleaks 8.30.1: entregable e historial local completo | **0 hallazgos**; control positivo detectado con exit esperado **7** |
| Account ID real en el entregable | **0**; solo IDs ficticios permitidos |
| Enlaces Markdown, UTF-8/LF, whitespace y diff-check | **PASS**: 176 documentos, 2035 enlaces relativos, **0 rotos**; 57 archivos del entregable revisados |
| Segundo plan real de datos, incluida `resource_drift` | **FAIL** (histórico): atributo no declarado; detalle en §14.5. Resuelto en §15 |
| Revisión de CI offline | Gates de datos y operador presentes; discovery cubre tres roots y nuevas pruebas Python; permisos `contents: read` y referencias a secretos sin cambios |

El ciclo de Floci se ejecuta **localmente**. CI comprueba sus guardas y topología con
fixtures; automatizar el ciclo del emulador en CI sigue siendo de Task/039. No se lanzó CI
remoto ni se concedieron credenciales nuevas.

### 14.5 Ciclo final y punto de detención

> **Histórico — ciclo RECHAZADO.** Se conserva tal como se registró. La causa se diagnosticó
> después, la guarda se corrigió y un ciclo nuevo se ejecutó en §15; este ciclo **no** cuenta
> como aprobado.

**STOP — H-031-1A NO READY FOR H-031-IAM.** Los conteos observados son correctos,
pero el segundo plan contiene drift no declarado. No se amplió ninguna tolerancia ni se
cambió una expectativa para aceptar el resultado.

| Comprobación del ciclo local | Resultado observado |
| --- | --- |
| Estado inicial | Inventario vacío en las 12 categorías |
| Primera creación | **8 → 21 → 13**, sin updates ni deletes |
| Ownership y SG | Tres states disjuntos; RDS solo `sg-rds`; ningún default SG administrado |
| Canario | Ausente del plan, state y outputs de datos; control negativo DH-2 también pasó |
| Smoke inicial y reconstruido | **GET /health HTTP 200** en ambos |
| Segundo plan | Medios/aplicación exit 0; datos exit 2: **rechazado por drift no declarado** |
| Drift controlado de aplicación | Un parámetro SSM ficticio eliminado y recreado; presencia final demostrada |
| Primer destroy | **13 → 21 → 8**; ausencia por API en las 12 categorías |
| Reconstrucción | **8 → 21 → 13**, sin updates ni deletes |
| Segundo destroy | **13 → 21 → 8**; ausencia por API en las 12 categorías |
| Limpieza final | Tres states sin recursos ni outputs; **0 contenedores, redes y volúmenes** del laboratorio/emulador; sin lock de escritura |

Floci **2.1.0**, RDS mock, provider AWS **6.64.0**, Terraform **1.16.2**; ejecución
exclusivamente contra loopback con credenciales ficticias. ZIP canónico ignorado del
backend, SHA-256 `0234fcc4ebd937b3a1c0a6f599031970823a4dcdb51fbf0f2fbd6eb1ef09764a`.

El JSON real contiene las diez diferencias declaradas en `resource_changes` y, además,
cinco entradas en `resource_drift`:

| Recurso | Atributos que difieren en `resource_drift` |
| --- | --- |
| `module.base_de_datos.aws_db_instance.this` | **`domain_dns_ips`: `null → []`**, además de `enabled_cloudwatch_logs_exports` |
| `module.base_de_datos.aws_db_parameter_group.this` | `parameter` |
| `module.red.aws_security_group.admin` | `egress` |
| `module.red.aws_security_group.lambda` | `egress` |
| `module.red.aws_security_group.rds` | `ingress` |

`domain_dns_ips` no está en las diferencias declaradas. La forma observada parece una
normalización de lista vacía, pero **no se ha demostrado su causa ni autorizado su
aceptación**. El log histórico muestra `[]` al destruir; eso no demuestra que el segundo
plan anterior tuviera este mismo delta ni que se hubiera revisado.

**Defecto identificado:** `scripts/laboratorio/inventario.py::exigir_sin_cambios` inspecciona
solo `resource_changes`. Reproducir la llamada sobre el JSON real devuelve éxito a pesar
del drift adicional. Las suites existentes no cubren esta omisión; sus resultados verdes
no sustituyen el gate del ciclo. El observador suplementario rechazó el plan y la revisión
del JSON aisló el atributo no declarado. Cuando llegó el resultado, el lanzador ya había
avanzado a reconstrucción; se dejó terminar su limpieza local para conservar el state.
Su mensaje automático «CICLO COMPLETO» no se acepta como aprobación del ensayo.

Evidencia privada conservada bajo `tmp/h0311a/` (ignorada): `real-second-plan.json`,
`second-plan-rejection.json`, planes de creación, state capturado tras crear datos y logs
completos. SHA-256 del JSON rechazado:
`a5c1c5b5baf58fef3d85c5f099e6e6049db6284a2e4cd6f7e09d24395321f180`.

**Pendiente para retomar:** explicar el delta con evidencia, resolver su tratamiento sin
silenciar drift, incorporar una comprobación de `resource_drift` con regresiones negativas
y repetir los gates y el ciclo limpio. No se introdujo `ignore_changes`, refresh-only ni
configuración de dominio RDS para forzar un resultado verde. H-031-IAM sigue sin autorizar.

### 14.6 Propuesta exacta de H-031-IAM — no ejecutada

Alcance exclusivo: `PersonalBlogDataOperator`, tres políticas bajo `/personal-blog/`,
tres adjuntos, `AWSServiceRoleForRDS` solo si falta y el state dedicado
`bootstrap/operador-datos/terraform.tfstate`. **No autoriza red, RDS, SSM productivo ni
CloudWatch productivo**. La propuesta completa, casos y condiciones viven en
[identidad operativa §10](../architecture/identidad-operativa-datos.md#10-checkpoint-h-031-iam--propuesta-exacta).

1. Verificar la identidad bootstrap.
2. Preflight sin mutar, con colisiones e inexistencia de objetivos comprobadas.
3. Access Analyzer: políticas renderizadas y trust.
4. Init, plan guardado y guarda: **7 creates**, u **8** si falta el rol vinculado; nada más.
5. Revisión humana y autorización del binario exacto.
6. Apply de ese plan.
7. Readback de rol, trust, tres políticas y adjuntos; ninguna inline ni access key nueva.
8. Simulación **desde bootstrap** contra el ARN del operador, con los casos de §10.1.
9. Cambio a `personal-blog-datos`.
10. STS y pruebas reales no mutantes, dry-run y AccessDenied de §10.2, sin permisos extra.
11. Convergencia del bootstrap **0/0/0**.

H-031-IAM y H-031-2 permanecen **sin ejecutar**. Task/031 sigue **En progreso**, sin
aprobación final, commit, push ni PR. Backend y frontend se conservan intactos.

### 14.7 Inventario final del entregable

**23 modificados + 34 nuevos = 57 archivos**, incluidos todos los cambios conservados
de H-031-1 y H-031-1A. Evidencia privada, mirrors, planes, states y logs bajo rutas ignoradas;
el ZIP canónico permanece ignorado en el backend. Ninguno se añade a Git.

<details>
<summary>Rutas exactas modificadas y nuevas</summary>

| Estado | Archivo |
| --- | --- |
| Modificado | `.github/workflows/ci-infra.yml` |
| Modificado | `.gitignore` |
| Modificado | `docs/architecture/aws-local-parity.md` |
| Modificado | `docs/architecture/open-decisions.md` |
| Modificado | `docs/architecture/production-postgresql-rds-decisions.md` |
| Modificado | `docs/project-management/ROADMAP.md` |
| Modificado | `docs/project-management/STATUS.md` |
| Modificado | `docs/runbooks/deployment-create.md` |
| Modificado | `docs/runbooks/deployment-destroy.md` |
| Modificado | `docs/runbooks/deployment-recovery.md` |
| Modificado | `docs/runbooks/deployment-rollback.md` |
| Modificado | `docs/runbooks/deployment-validate.md` |
| Modificado | `docs/runbooks/terraform-state-bootstrap.md` |
| Modificado | `docs/stages/STAGE-10-cloud-deployment.md` |
| Modificado | `laboratorio/docker-compose.laboratorio.yml` |
| Modificado | `scripts/laboratorio/destino.py` |
| Modificado | `scripts/laboratorio/inventario.py` |
| Modificado | `scripts/laboratorio/laboratorio.py` |
| Modificado | `scripts/laboratorio/verificacion.py` |
| Modificado | `tests/laboratorio/test_healthcheck.py` |
| Modificado | `tests/laboratorio/test_inventario.py` |
| Modificado | `tests/laboratorio/test_topologia_de_roots.py` |
| Modificado | `tests/laboratorio/test_verificacion.py` |
| Nuevo | `bootstrap/operador-datos/.terraform.lock.hcl` |
| Nuevo | `bootstrap/operador-datos/backend-s3.tfbackend.example` |
| Nuevo | `bootstrap/operador-datos/main.tf` |
| Nuevo | `bootstrap/operador-datos/outputs.tf` |
| Nuevo | `bootstrap/operador-datos/politicas/fase-1-denegaciones.json.tftpl` |
| Nuevo | `bootstrap/operador-datos/politicas/fase-1-rds-y-custodia.json.tftpl` |
| Nuevo | `bootstrap/operador-datos/politicas/fase-1-red.json.tftpl` |
| Nuevo | `bootstrap/operador-datos/providers.tf` |
| Nuevo | `bootstrap/operador-datos/tests/operador.tftest.hcl` |
| Nuevo | `bootstrap/operador-datos/variables.tf` |
| Nuevo | `bootstrap/operador-datos/versions.tf` |
| Nuevo | `docs/architecture/identidad-operativa-datos.md` |
| Nuevo | `docs/task-reports/TASK-031-report.md` |
| Nuevo | `docs/tasks/TASK-031-deploy-network-rds-ssm-cloudwatch.md` |
| Nuevo | `scripts/terraform_datos/check_plan.py` |
| Nuevo | `terraform-datos/.terraform.lock.hcl` |
| Nuevo | `terraform-datos/backend-s3.tfbackend.example` |
| Nuevo | `terraform-datos/entornos/local/local.tfvars` |
| Nuevo | `terraform-datos/entornos/produccion/produccion.tfvars.example` |
| Nuevo | `terraform-datos/main.tf` |
| Nuevo | `terraform-datos/outputs.tf` |
| Nuevo | `terraform-datos/providers.tf` |
| Nuevo | `terraform-datos/tests/datos.tftest.hcl` |
| Nuevo | `terraform-datos/variables.tf` |
| Nuevo | `terraform-datos/versions.tf` |
| Nuevo | `terraform/modulos/base_de_datos/main.tf` |
| Nuevo | `terraform/modulos/base_de_datos/outputs.tf` |
| Nuevo | `terraform/modulos/base_de_datos/variables.tf` |
| Nuevo | `terraform/modulos/red/main.tf` |
| Nuevo | `terraform/modulos/red/outputs.tf` |
| Nuevo | `terraform/modulos/red/variables.tf` |
| Nuevo | `tests/terraform_datos/test_check_plan.py` |
| Nuevo | `tests/terraform_datos/test_grupo_por_omision.py` |
| Nuevo | `tests/terraform_datos/test_secretos.py` |

</details>

## 15. H-031-1A — resolución del bloqueo de `domain_dns_ips` (2026-10-03)

Reanudación desde el estado real de §14.5, sin reiniciar H-031-1 ni revertir H-031-1A: rama
`Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`, `HEAD == main == origin/main == 6c31d1d`, sin
staging ni commit. Ningún proceso huérfano de la sesión anterior (solo el servidor de lenguaje
Terraform del editor) y ningún contenedor, red ni volumen del laboratorio. **El ciclo de §14.5
se conserva como RECHAZADO**; nada de esta sección lo reinterpreta.

### 15.1 Causa exacta de `domain_dns_ips: null → []`

Diagnóstico **sin AWS**: schema real del provider, código fuente público de las versiones
fijadas, state capturado tras el apply local y el JSON rechazado.

| Evidencia | Resultado |
| --- | --- |
| Schema real (`providers schema -json`, `hashicorp/aws` 6.64.0) | `list(string)`, **optional**, **no** `computed`, no sensible. En el código: `MinItems: 2`, `MaxItems: 2`, IP válidas, `ConflictsWith` `domain` y `domain_iam_role_name`; **no** `ForceNew` |
| Lectura del provider (`internal/service/rds/instance.go` v6.64.0, SHA-256 `6d25e2b2…`, líneas 2006-2021) | Si `DomainMemberships` está vacío —toda instancia sin Active Directory—, Read ejecuta **siempre** `d.Set("domain_dns_ips", nil)`, que el SDKv2 materializa como lista vacía |
| Escritura del provider (líneas 2573-2580) | Solo envía `DomainDnsIps` a la API si la lista tiene elementos: `null` y `[]` son la misma intención |
| SDKv2 2.40.1 del provider (`helper/schema/grpc_provider.go`, SHA-256 `9b271e9b…`) | `normalizeNullValues` preserva el `null` **planificado** frente a una colección vacía **solo** con `apply=true` (líneas 2361-2371): así lo llama el apply (línea 1535); el refresh lo llama con `apply=false` (línea 946) y gana `[]` |
| Terraform 1.16.2 (`internal/terraform/context_plan.go`, SHA-256 `4ba1fc5f…`, línea 1204) | El drift se decide con `RawEquals`: `null` y `[]` difieren y se reportan como `update` en `resource_drift` |
| State tras el apply local | `domain_dns_ips = null`, mientras los cinco atributos `domain*` de tipo cadena valen `""`: Read sí se ejecutó; solo la colección conservó el `null` |
| Segundo plan rechazado | `resource_drift`: `null → []`. `resource_changes`: `[] → []`, **ningún cambio planificado** |
| Contraste | `warning_event_categories`, colección opcional que Read **no** escribe: `null` antes y después, sin drift |
| Renderizado humano de Terraform | Lo oculta («73 unchanged attributes hidden»): su propio *differ* trata `null`/`[]` como iguales; solo el JSON lo expone |
| Precedente en AWS real | Task/030 observó la misma familia contra AWS: `tags: null → {}` en `resource_drift` del bucket de estado ([reporte de Task/030 §12.3](TASK-030-report.md#123-diferencia-saneada-encontrada)) |
| ¿Hay configuración correcta que fijar? | `terraform validate` offline con el provider cacheado: `domain_dns_ips = []` es **rechazado** («Not enough list items… 2 item minimum»); dos IP validan, pero unirían la instancia a un AD autogestionado: cambio funcional no deseado. `ignore_changes` sigue prohibido |

**Conclusión.** Es una diferencia de **representación** del SDKv2 del provider, determinista
por código: apply y refresh normalizan la colección vacía de forma distinta y Terraform
compara en bruto. **No es del emulador**: lo único que aporta Floci —una instancia sin
dominio— es idéntico en AWS. Tampoco viene de nuestra configuración, que no declara ningún
atributo `domain*`; no cambia red, DNS, conectividad ni seguridad, y no produce ningún cambio
planificado. **Consecuencia para AWS (hipótesis fundada en el código, no en Floci; AWS es la
autoridad):** es probable que el primer plan de convergencia de H-031-3 muestre esta misma
entrada. El gate productivo **la rechazará** y se aplicará DN-2 —STOP, evidencia, plan
refresh-only, revisión del JSON, autorización explícita—; nada queda preautorizado.

### 15.2 Regla de decisión aplicada

| Condición exigida para tolerarlo en el laboratorio | Cumplimiento |
| --- | --- |
| Diferencia exclusiva del emulador **o de representación** | De representación del SDKv2 (§15.1); **no** del emulador, y así se declara |
| No viene de nuestra configuración | Ningún `domain*` en módulos ni root |
| No es un cambio funcional deseado | `resource_changes` `[] → []`; el provider no envía listas vacías |
| No cambia red, DNS, conectividad ni seguridad | Solo describe los DNS de un AD al que la instancia no pertenece |
| No existe configuración Terraform correcta que fijar | `[]` es inválido; dos IP cambiarían la función |
| Determinista y reproducible | Código de tres versiones fijadas; observado en el ciclo rechazado y otra vez en el final (§15.5) |
| Acotada exactamente | `module.base_de_datos.aws_db_instance.this`, tipo `aws_db_instance`, acción `update`, transición `null → []` **en ese sentido**, solo en `resource_drift` y con el conjunto exacto de atributos de la entrada |

### 15.3 Guarda fail-closed de `resource_drift` — cambio exacto

**Defecto.** `exigir_sin_cambios` juzgaba solo `resource_changes`; un `exit 0` no se leía y un
`exit 2` se justificaba por otros cambios. **RED demostrado** con el código anterior sobre el
fixture del plan observado: aceptaba el `exit 2` con `domain_dns_ips` sin declarar y un
`exit 0` con drift en `aws_vpc`.

| Archivo | Cambio |
| --- | --- |
| `scripts/laboratorio/inventario.py` | `DriftDelDestino` (dirección, tipo, acciones exactas, transiciones con forma cerrada, motivo; valida su propia declaración) y `revisar_drift`: `deferred_changes` vacío; cada entrada de `resource_drift` debe estar declarada por **dirección y tipo**, con **acciones idénticas**, conjunto de atributos **exactamente igual** —no subconjunto— y cada transición con su forma: `nulo_a_lista_vacia`, `lista_a_vacia` o `agrega_reglas_separadas` (el grupo gana, sin perder nada, exactamente las reglas `aws_vpc_security_group_*_rule` del mismo plan, en su representación en línea). `exigir_sin_cambios` lo invoca **siempre** que recibe el plan —también con `exit 0`— y rechaza un `exit 0` cuyo JSON contiene cambios |
| `scripts/laboratorio/laboratorio.py` | `DRIFT_DEL_DESTINO_LOCAL_DE_DATOS`: cinco entradas cerradas, con motivos que separan lo del SDKv2 (`domain_dns_ips`) de lo de Floci (logs exportados, parámetros, reglas reflejadas en `sg-admin`/`sg-lambda` egress y `sg-rds` ingress). El segundo plan de datos es **un único** plan guardado con `-detailed-exitcode` y su JSON se lee **siempre**. Las diez diferencias de `resource_changes` no cambian: `domain_dns_ips` **no** se añadió allí |
| `tests/laboratorio/drift_observado.py` | Fixture con la estructura del JSON real (ID sintéticos, sin cuenta ni canario) |
| `tests/laboratorio/test_drift_del_destino.py` | **34 regresiones** |
| `tests/terraform_datos/test_check_plan.py` | Regresión: el mismo drift que tolera el laboratorio es **rechazado** por la guarda productiva |

**Controles negativos que detienen el ciclo**: otro atributo de la instancia (`port`); más
atributos (`storage_type`) y menos (sin `enabled_cloudwatch_logs_exports`); otro valor de
`domain_dns_ips` (dos IP, sentido inverso `[] → null`, lista con IP a vacía, cadena vacía);
otros logs exportados; parámetros devueltos con valores; otro tipo en la misma dirección
(`aws_rds_cluster`); otras acciones (`delete`, `create`, reemplazo, acción duplicada); drift en
un recurso no autorizado (`aws_vpc`, una subred); `sg-rds` que gana una regla abierta no
gestionada; un grupo que pierde una regla; la regla separada ausente o con otro puerto; drift
de salida en `sg-rds`; otro atributo de un grupo; `deferred_changes`; `resource_drift` ilegible,
`mode = data` o dirección repetida; `exit 0` con drift no declarado; `exit 0` que contradice su
JSON; `exit 1`; y el canario en el plan.

Sobre el **JSON real rechazado** (`a5c1c5b5…`): con la lista cerrada pasa; sin la transición
de `domain_dns_ips`, o sin lista de drift, se rechaza nombrando la entrada. Las reglas en
línea reconstruidas coinciden con las del provider sin excepción.

### 15.4 La guarda productiva no se relajó

`scripts/terraform_datos/check_plan.py` **no cambió**: sigue exigiendo `resource_drift` y
`deferred_changes` vacíos (`DRIFT_OR_DEFERRED`). La nueva regresión le entrega exactamente la
entrada `domain_dns_ips: null → []` que el laboratorio tolera y comprueba que la rechaza. En
AWS la meta sigue siendo **0/0/0 con `resource_drift = 0`**. Ni `ignore_changes`, ni
tolerancia en módulos, ni atributos arbitrarios.

### 15.5 Ciclo final limpio — aprobable

Ejecutado el 2026-10-03 de 18:52 a 19:10, **un solo ciclo nuevo**, con el lanzador corregido,
Floci 2.1.0 con RDS mock, provider 6.64.0, Terraform 1.16.2, loopback y credenciales ficticias;
ZIP de Task/030 `0234fcc4…09764a`; solicitud temporal contra suspensión, liberada al terminar.
Un observador de solo lectura capturó cada plan del root de datos y buscó el canario en su
JSON y en su binario. Precondiciones: sin residuos, states vacíos y lock ausente.

| Comprobación | Resultado |
| --- | --- |
| `levantar` / inventario inicial | exit 0 / vacío en las **12** categorías |
| Primera creación | **8 → 21 → 13**, solo `create`; plan de datos `{'create': 21, 'update': 0}` |
| Plan de creación de datos (JSON) | 21 direcciones; ningún `aws_default_security_group`; RDS referencia **solo** `var.id_sg_rds` |
| Ownership | Disjunto en los tres states: aplicación no administra S3, red ni RDS |
| Canario | **Ausente** del plan, del state y de las salidas de datos en las dos creaciones, y del JSON y binario de los tres planes capturados de este ciclo |
| Servicios | Cuatro SSM, rol IAM y camino crítico `GET /health` **HTTP 200**; SDK `boto3/1.43.82` |
| Segundo plan | Medios **exit 0**; aplicación **exit 0**; datos **exit 2** |
| Datos — `resource_changes` | **Solo** las diez diferencias declaradas del emulador; `domain_dns_ips` `[] → []` |
| Datos — `resource_drift` | **Solo** las cinco entradas declaradas, con atributos y transición exactos: instancia `domain_dns_ips` **`null → []`** y `enabled_cloudwatch_logs_exports` `["postgresql"] → []`; *parameter group* `parameter`; `sg-admin` y `sg-lambda` `egress`; `sg-rds` `ingress`. `deferred_changes` ausente |
| Drift controlado | `/blog-lab/local/storage_region` retirado por API y recreado: 1 alta y 1 actualización dependiente declarada; presencia final demostrada |
| Primer destroy | **13 → 21 → 8**; states sin recursos ni salidas; ausencia por API en **12** categorías |
| Reconstrucción | **8 + 21 + 13**; *smoke* `GET /health` **HTTP 200** `{"status":"ok"}` |
| Segundo destroy | **13 → 21 → 8**; ausencia por API en **12** categorías |
| `bajar` y estado final | exit 0; tres states sin recursos ni salidas; **lock ausente**; **0** contenedores, redes y volúmenes del laboratorio y del emulador |

`domain_dns_ips: null → []` apareció **otra vez**, idéntico: la causa de §15.1 es
reproducible. Ninguna diferencia nueva. Evidencia privada e ignorada en
`tmp/h0311a/ciclo-final/`: logs de las tres fases, planes JSON del root de datos (segundo plan
`plan-datos-3.json`, SHA-256 `8745acee39ca3c92df5187da41d43bd00de1c553c97a396d900f97f204b35bbe`)
y pre/postcondiciones. La del ciclo rechazado permanece intacta en `tmp/h0311a/`.

### 15.6 Gates finales, repetidos después del ciclo

| Gate | Resultado |
| --- | --- |
| Seis roots: `fmt -check`, `init -backend=false -lockfile=readonly`, `validate` | **PASS**; metadatos aislados; locks sin cambios (hash antes y después) |
| `terraform/modulos` fmt recursivo | **PASS** |
| `terraform test` | datos **22/22**, operador **7/7**, medios **7/7**, terraform-state **5/5**, github-oidc **9/9**; aplicación sin regresión (**0 casos definidos**, igual que antes) |
| Python, invocación exacta del CI | laboratorio **297 OK** (263 + 34 nuevas), terraform_datos **35 OK** (34 + 1 nueva), terraform_state **12 OK**, security **88 OK**, oidc **60 ejecutadas, 1 skip** de plataforma. Ninguna suite disminuyó |
| Compose del laboratorio | **PASS** |
| `scripts/terraform_datos/check_plan.py` | **Sin cambios**: SHA-256 `43d8abbc7ba7fc45dcb8431681d4fda75aaed5f05aed0ca106e88ea875d3f9ce`, modificado por última vez antes del rechazo |
| Gitleaks 8.30.1 (binario verificado contra el ZIP previo) | Entregable de 329 archivos: **0**; historial local, 108 commits: **0**; control positivo **detectado** (exit esperado 7) |
| Account ID real | **0** apariciones; solo los ficticios permitidos |
| Enlaces Markdown y UTF-8/LF/whitespace | 176 documentos, **2044** enlaces relativos, **0 rotos**, anclas nuevas incluidas; 59 archivos cambiados revisados |
| `git diff --check` | **PASS** |
| CI | Permisos y referencias a credenciales **sin cambios**; las suites nuevas entran por el *discovery* existente |

### 15.7 Estado vigente — H-031-1A READY FOR H-031-IAM

Se mantienen **21 recursos** en datos (los **22** son historia de H-031-1); SG por omisión no
gestionado ni usado; RDS solo `sg-rds`; Task/032 adjuntará `sg-lambda` y H-031-5, `sg-admin`.
**DN-3 cerrada**; **DN-2 condicionada**: refresh-only solo si AWS demuestra `resource_drift`,
con STOP, evidencia, plan guardado, revisión del JSON y autorización explícita; y el
diagnóstico de §15.1 anticipa que `domain_dns_ips` probablemente lo active. **Cero AWS real**:
ni STS, ni IAM, ni `init` o state remoto, ni `.tflock`, ni plan o apply contra AWS, ni
contraseña productiva. H-031-IAM, H-031-2 y siguientes **no se ejecutaron**; su propuesta
sigue siendo la de §14.6.

Entregable: **59 archivos** —los 57 de §14.7 más `tests/laboratorio/drift_observado.py` y
`tests/laboratorio/test_drift_del_destino.py`, nuevos—, sin staging, commit, push ni PR.
Planes, states, logs y evidencia siguen en rutas ignoradas.

## 16. H-031-IAM — plan guardado, SIN apply (2026-10-03)

Autorización del usuario: **H-031-IAM PLAN ONLY**, hasta el plan guardado real y su revisión.
**No autoriza el apply.** H-031-1A quedó aceptado como READY FOR H-031-IAM. Configuración,
plan, JSON, `TF_DATA_DIR` y evidencia viven en el directorio privado del operador, **fuera
del checkout**; aquí solo aparecen nombres lógicos, conteos y huellas.

### 16.1 Guarda nueva del plan del operador

El diseño (identidad operativa §10, paso 4) exigía una guarda que **no existía**. Se añadió
`scripts/terraform_datos/check_plan_operador.py`, junto a la guarda de datos para que el
*discovery* existente del CI la recoja sin tocar el workflow. Exige versión 1.16.2, plan
completo y no `errored`, `resource_drift` y `deferred_changes` vacíos, variables exactas
—incluida `crear_rol_vinculado_de_rds` igual al resultado del preflight—, la postcondición de
identidad en `pass`, las **7 u 8 direcciones exactas**, solo `create`, sin import ni move; trust
exacto con MFA; las tres políticas **iguales a un render propio en Python** de las plantillas
versionadas, con 6/9/7 sentencias y 68 acciones Allow, ninguna de IAM ni con comodín;
adjuntos al rol con `policy_arn` desconocido y procedente solo de esas políticas; configuración
sin `inline_policy`, `managed_policy_arns` ni boundary; salidas no sensibles; y ningún
`AdministratorAccess`. **RED**: sin implementación, el módulo no importaba; **GREEN**: 28
regresiones en `tests/terraform_datos/test_check_plan_operador.py`. El render en Python se
comparó offline con `templatefile` de Terraform 1.16.2: **idéntico** en las tres políticas y en
el bucket. Sin regresiones: `terraform_datos` **63 OK** (35 + 28), operador **7/7**.

### 16.2 Identidad y preflight — solo lectura

| Comprobación | Resultado |
| --- | --- |
| STS (perfil `personal-blog`, renovado por el usuario) | Sesión `assumed-role/PersonalBlogAdministrator/…`, cuenta esperada, región `us-east-2`. Un primer intento devolvió `ExpiredToken` sin ninguna otra llamada |
| `PersonalBlogDataOperator` | **Ausente** (`NoSuchEntity`) |
| Políticas administradas locales | **0** en la cuenta; ninguna bajo `/personal-blog/`; **0 colisiones** con los tres nombres previstos |
| `AWSServiceRoleForRDS` | **Ausente** (`NoSuchEntity`; contrastado con la lista de roles vinculados) → `crear_rol_vinculado_de_rds = true` → **CASO B** |
| Usuario de entrada del trust | Existe: el principal es válido |
| Key `bootstrap/operador-datos/terraform.tfstate` | **Ausente**: `head-object` 404, sin versiones ni *delete markers* bajo el prefijo |
| `blog-prod-postgres` / `/blog-prod/datos/blogadmin` | **Ausentes** (`DBInstanceNotFound` / `describe-parameters` vacío) |

### 16.3 Access Analyzer

`validate-policy` sobre los documentos renderizados: trust como `RESOURCE_POLICY` de tipo
`AWS::IAM::AssumeRolePolicyDocument`, y las tres políticas como `IDENTITY_POLICY`.

| Documento | Caracteres | ERROR | SECURITY_WARNING | WARNING | SUGGESTION |
| --- | ---: | ---: | ---: | ---: | ---: |
| Trust | 252 | 0 | 0 | 0 | 0 |
| `fase-1-red` | 3964 | 0 | 0 | 0 | 0 |
| `fase-1-rds-y-custodia` | 4015 | 0 | 0 | 0 | 0 |
| `fase-1-denegaciones` | 2225 | 0 | 0 | 0 | 0 |

Ningún hallazgo que explicar; no se modificó ninguna política. Los cuatro documentos validados
son **semánticamente idénticos** a los del plan (§16.5).

### 16.4 Backend, plan guardado y guarda

| Paso | Resultado |
| --- | --- |
| `init` | Solo `bootstrap/operador-datos`; backend `s3` con la key dedicada, `use_lockfile = true`, **sin DynamoDB**, workspace `default`; **sin migración** ni reutilización de keys; sin `terraform_remote_state`; `-lockfile=readonly` con el lock de providers intacto (provider desde el directorio local, verificado contra los hashes del lock); state aún ausente tras el `init` |
| Plan guardado | **exit 2 — `8 to add, 0 to change, 0 to destroy`**; 0 *replace*, 0 import, 0 move. SHA-256 del binario `4d39f25bd6a3764488b5406be03310c21d9e0e5b36311a0e30d45db38c2ecd64`; del JSON `8633ba7f3295c28ef8ad811ab7f87f15c5865a431d5eb2123c27336ca16a0c93` |
| Guarda | **`PLAN_OK`**: 8 direcciones, 6/9/7 sentencias, 68 acciones Allow, **0 de IAM**. La guarda no se modificó tras ver el plan |

Las ocho direcciones del CASO B: `aws_iam_role.operador_datos`; `aws_iam_policy.fase_1["Red"]`,
`["RdsYCustodia"]` y `["Denegaciones"]`; `aws_iam_role_policy_attachment.fase_1` con esas
mismas tres claves; y `aws_iam_service_linked_role.rds[0]`.

### 16.5 Revisión del JSON

| Punto | Resultado |
| --- | --- |
| Versión / completo / `errored` / `applyable` | 1.16.2 / sí / no / sí |
| `resource_drift` / `deferred_changes` | **0 / 0** |
| `prior_state` | Solo `data.aws_caller_identity.bootstrap`: ningún recurso gestionado previo |
| Tipos | 1 `aws_iam_role`, 3 `aws_iam_policy`, 3 `aws_iam_role_policy_attachment`, 1 `aws_iam_service_linked_role`. **Ninguna** access key, usuario, grupo, *instance profile*, rol o política adicional ni política inline; ningún recurso de red, RDS, SSM, CloudWatch ni Lambda |
| Trust | Una sentencia: `Allow` `sts:AssumeRole` al usuario `personal-blog-entry-admin` de la misma cuenta, por ARN exacto, con `aws:MultiFactorAuthPresent = true` |
| Rol | Ruta `/`, sesión máxima 3600 s, sin *permissions boundary*, `force_detach_policies = false`; la configuración solo declara nombre, ruta, descripción, sesión, trust y etiquetas |
| Políticas | Ruta `/personal-blog/`. Red: 6 sentencias, 14 acciones Allow. RDS y custodia: 9 sentencias, 54 Allow. Denegaciones: 7 sentencias, todas `Deny`. **68 Allow distintas, ninguna de IAM**; sin `iam:SimulatePrincipalPolicy` ni lecturas IAM para probarse; sin comodines en Allow; `Resource: "*"` solo en lecturas |
| Adjuntos | Tres, al rol operativo, cada uno a su política de fase 1 |
| Rol vinculado | `rds.amazonaws.com`, sin sufijo ni descripción, **solo** porque el preflight demostró que falta |
| `AdministratorAccess` | Ausente de todo el plan |
| Checks | Postcondición de identidad y validaciones de variables en `pass` |

### 16.6 Prueba de que NO hubo apply

Después del plan, consultando AWS en modo lectura: la key del state sigue **ausente**, el
`.tflock` **ausente**, `PersonalBlogDataOperator` **no existe**, ninguna de las tres políticas
existe y `AWSServiceRoleForRDS` sigue sin existir. Ningún `.terraform` en el checkout. No se
ejecutó `terraform apply` ni se creó IAM a mano. La simulación de políticas pertenece al
post-apply, porque necesita el rol creado.

### 16.7 Estado — H-031-IAM PLAN READY FOR APPLY REVIEW

El plan guardado espera la revisión humana y una autorización explícita del apply de **ese**
binario. Cualquier plan nuevo exigiría repetir la guarda y la revisión. H-031-2 y siguientes
**no se ejecutaron**; no se tocaron red, RDS, SSM ni CloudWatch productivos. Entregable:
**61 archivos** —los 59 de §15.7 más la guarda y sus pruebas—, sin staging, commit, push ni PR.

## 17. H-031-IAM — apply ejecutado; STOP en la simulación (2026-10-03)

Autorización del usuario: **H-031-IAM APPLY** del único binario revisado (SHA-256
`4d39f25bd6a3764488b5406be03310c21d9e0e5b36311a0e30d45db38c2ecd64`), con readback, simulación
desde el bootstrap, validación del operador y convergencia. **No** autoriza H-031-2 ni ningún
recurso de datos.

### 17.1 Freshness gate, apply y post-apply

| Paso | Resultado |
| --- | --- |
| STS | `assumed-role/PersonalBlogAdministrator`, cuenta esperada, `us-east-2` |
| Ausencias antes de mutar | Operador, tres políticas, `AWSServiceRoleForRDS`, state y `.tflock`: **ausentes** |
| Binario | SHA-256 **igual** al autorizado; el JSON regenerado desde el binario es **idéntico** al revisado; guarda `PLAN_OK` 8/0/0, sin modificarla |
| Apply | `terraform apply <plan exacto>`, mismo `TF_DATA_DIR`, workspace `default`, `AWS_PROFILE=personal-blog`: **exit 0 — 8 added, 0 changed, 0 destroyed**; exactamente las ocho direcciones de §16.4; sin errores ni avisos |
| Post-apply | State remoto **presente** en la key dedicada; `.tflock` **ausente**; `state list` = 8 recursos gestionados más el data source de identidad; nada escrito en el checkout |

### 17.2 Readback IAM — verde

| Recurso | Resultado |
| --- | --- |
| `PersonalBlogDataOperator` | Nombre, ruta `/`, sesión máxima 3600 s, etiquetas exactas; trust **idéntico** al aprobado —usuario de entrada por ARN exacto y MFA obligatorio—; sin *permissions boundary*, sin políticas inline, sin *instance profiles* |
| Políticas | Exactamente tres bajo `/personal-blog/`, cada una con **una** versión, la *default*, y un adjunto; documento **semánticamente idéntico** a la plantilla y al validado por Access Analyzer; etiquetas exactas |
| Adjuntos | El rol tiene exactamente esas tres políticas, ninguna más |
| `AWSServiceRoleForRDS` | Existe, ruta `/aws-service-role/rds.amazonaws.com/`, confianza solo en `rds.amazonaws.com`, con `AmazonRDSServiceRolePolicy`; no se usa para nada más |

### 17.3 Simulación desde el bootstrap — **STOP**

`iam simulate-principal-policy` ejecutado por `PersonalBlogAdministrator` contra el ARN exacto
del operador, con los 21 casos de [identidad operativa §10.1](../architecture/identidad-operativa-datos.md#101-casos-de-la-simulación-paso-8)
—25 evaluaciones—. Contexto: `aws:RequestedRegion = us-east-2` y las etiquetas
`Proyecto = personal-blog` y `Componente = datos`, tanto de petición (`aws:RequestTag/*`,
`aws:TagKeys`) como de recurso (`aws:ResourceTag/*`), salvo donde el caso dice otra cosa.

**24 de 25 como se esperaba**: los ocho `allowed` (S-01 a S-08); `explicitDeny` en S-09, S-15
a S-18 y S-21; `implicitDeny` en S-11 a S-14, S-19 y S-20. **Difiere S-10**:
`ec2:CreateVpcEndpoint` sobre `vpc-endpoint/*` con `ec2:VpceServiceName =
com.amazonaws.us-east-2.ssm` → esperado `implicitDeny`, obtenido **`allowed`**.

**Diagnóstico** (simulaciones adicionales de solo lectura):

| Variante | Decisión |
| --- | --- |
| Servicio SSM, solo etiquetas de petición | `implicitDeny`, como pretende el diseño |
| Cualquier servicio, sin `ec2:VpceServiceName`, con `aws:ResourceTag` del proyecto | **`allowed`** |
| Servicio S3, solo etiquetas de petición | `allowed`, por la sentencia prevista |

La concede la sentencia **`OperarSoloRecursosPropios`** de la política Red: incluye
`ec2:CreateVpcEndpoint` sobre `vpc-endpoint/*` condicionada **solo** por `aws:ResourceTag` y la
región, sin `ec2:VpceServiceName`. La referencia oficial de servicios lista `aws:ResourceTag`
como clave válida del tipo `vpc-endpoint` para esa acción, pero no aclara si EC2 la evalúa con las
etiquetas de la petición sobre un endpoint que se está creando. Por tanto, la restricción «solo el
*gateway endpoint* de S3» **no es robusta**: depende de un comportamiento de AWS no demostrado. Un
endpoint de interfaz contradiría además la regla de no adoptar endpoints por inercia
(PRODUCTION DATABASE LAW, punto 6) y el presupuesto D-13. Las pruebas offline no lo
detectaban porque ninguna aserción relacionaba esa sentencia con `ec2:VpceServiceName`.

**No se cambió ninguna política, no se añadieron permisos y no se repitió la simulación con otro
contexto para «hacerla pasar».** Tampoco se ejecutaron las pruebas del operador ni el plan de
convergencia: ambos exigen la simulación en verde.

### 17.4 Perfil `personal-blog-datos`

Solo existe el perfil `personal-blog`, una `login_session` de la sesión
`assumed-role/PersonalBlogAdministrator/personal-blog-entry-admin`. **`personal-blog-datos` no
existe.** Desde una sesión de `PersonalBlogAdministrator` no se puede encadenar al operador,
porque el trust exige al **usuario** de entrada con MFA. Configurarlo es un paso humano
posterior, que no se hizo ni se pidió todavía. Mientras tanto nadie puede asumir el rol.

### 17.5 Estado — H-031-IAM APLICADO, BLOQUEADO en la simulación (S-10)

En AWS existen los **8 recursos** del plan autorizado, con el state en su key dedicada. El
readback está en verde; la simulación, **no**. H-031-IAM **no está completo** ni verificado.
La corrección de la política requiere decisión y autorización explícitas del usuario, con su
propio plan (`update` de la política Red), guarda, Access Analyzer, apply, readback y una
simulación que cubra también el caso con `aws:ResourceTag`. H-031-2 **no se inició**.

## 18. H-031-IAM S10 FIX — diseño, simulación y plan; STOP por `resource_drift` (2026-10-03)

Autorización del usuario: **H-031-IAM-S10-FIX PLAN ONLY**: diseñar, implementar en el
workspace, validar y generar un plan guardado de corrección. **No** autoriza aplicarla.
Contexto: S-10 se descubrió **después** del apply (§17). El rol quedó deliberadamente
**inutilizable para operación humana**, porque `personal-blog-datos` todavía no existe. Ninguno
de los 8 recursos se destruyó ni se recreó.

### 18.1 Causa raíz y modelo de autorización de `CreateVpcEndpoint`

`OperarSoloRecursosPropios` concedía `ec2:CreateVpcEndpoint` sobre `vpc-endpoint/*` exigiendo
solo `aws:ResourceTag`, y no `ec2:VpceServiceName`. Con esa clave en el contexto, el simulador
permitía cualquier servicio.

La referencia oficial de servicios de AWS (JSON de EC2, idéntico a la copia del 2026-10-03, SHA-256
`e4ef8c6a…5184`) indica **por acción y por tipo de recurso** las claves que se evalúan:

| `ec2:CreateVpcEndpoint` sobre | Claves admitidas | ¿Interviene en un gateway de S3? |
| --- | --- | --- |
| `vpc-endpoint` (el nuevo) | `aws:RequestTag/*`, `aws:TagKeys`, `ec2:VpceServiceName`, `ec2:VpceServiceOwner`/`Region`/`MultiRegion`, `ec2:VpcePrivateDns*`. **No** `aws:ResourceTag` | Sí, siempre |
| `vpc` | `aws:ResourceTag/*`, `ec2:ResourceTag/*`, `ec2:VpcID`. **No** `ec2:VpceServiceName` | Sí (`VpcId`) |
| `route-table` | `aws:ResourceTag/*`, `ec2:ResourceTag/*`, `ec2:RouteTableID` | Sí (`RouteTableIds`) |
| `subnet` / `security-group` | `aws:ResourceTag/*`, `ec2:ResourceTag/*` y su ID | No: solo interfaz y GWLB |

Para `ec2:ModifyVpcEndpoint`, el tipo `vpc-endpoint` admite `aws:ResourceTag` y **no**
`ec2:VpceServiceName`. `aws:RequestedRegion` es global. Conclusión: en una llamada real AWS no
aportaría `aws:ResourceTag` sobre un endpoint que se está creando, pero la política dependía de
esa propiedad implícita y el simulador la exponía. La corrección elimina esa dependencia.

### 18.2 Política Red: antes y después

| | Aplicada en H-031-IAM | Corregida (workspace) |
| --- | --- | --- |
| Sentencias | 6 | **8** |
| Acciones Allow distintas | 14 | **14**: ninguna nueva ni retirada; 68 en total, 0 de IAM |
| Caracteres | 3964 | 4561 (< 6144) |
| `CreateVpcEndpoint` sobre `vpc-endpoint/*` | `CrearSoloElGatewayEndpointDeS3` (S3 + `RequestTag`) **y** `OperarSoloRecursosPropios` (solo `ResourceTag`) | **Solo** `CrearSoloElGatewayEndpointDeS3` |
| `CreateVpcEndpoint` sobre los padres | Vía `OperarSoloRecursosPropios`, también `subnet` y `security-group` | `GatewayDeS3SobreVpcYTablasPropias`: **solo** `vpc/*` y `route-table/*` con `ResourceTag` |
| `ModifyVpcEndpoint` | Vía `OperarSoloRecursosPropios`, incluidas subredes y grupos | `ModificarSoloEndpointsPropios`: **solo** `vpc-endpoint/*` y `route-table/*` con `ResourceTag` |

**Por qué ya no permite otros servicios.** EC2 autoriza **cada** recurso de la petición, y el
endpoint nuevo solo puede autorizarlo una sentencia que exige `ec2:VpceServiceName =
com.amazonaws.us-east-2.s3`: ninguna otra cubre `vpc-endpoint/*` para crear. Sin subredes ni grupos
autorizados, tampoco se pueden crear ni ampliar endpoints de interfaz con ENI. **Límite declarado:**
EC2 no ofrece una clave de condición por tipo de endpoint; un endpoint de interfaz **de S3** sin
subredes no queda excluido por clave, pero no tendría ninguna ENI ni podría recibirla.

**Deny defensivo: evaluado y no adoptado.** Un `Deny` de `CreateVpcEndpoint` con servicio distinto
de S3 está documentado en la referencia, pero su semántica real no se puede demostrar sin una sesión
del operador. Además exigiría cambiar Denegaciones —una segunda política— o mezclar un `Deny` en
Red. El `Allow` positivo ya basta.

### 18.3 Pruebas offline

| Pieza | Resultado |
| --- | --- |
| `tests/terraform_datos/simulacion_de_politicas.py` | Evaluador offline de los operadores que usan las tres políticas —aborta ante cualquier otro, `NotAction` o `NotResource`— y **matriz única de 62 casos**: los 21 de §10.1 (S-18 y S-19 por acción), S-10 con petición, con recurso y con ambos, Secrets Manager, RDS, servicio arbitrario, sin `VpceServiceName`, otra región, etiquetas incorrectas o claves ajenas, recurso de otra cuenta, padres ajenos, `subnet` y `security-group`, endpoint ajeno; y 18 positivos —gateway de S3, sus padres, modificar el endpoint propio y las operaciones de red que la corrección no debe romper— |
| `tests/terraform_datos/test_simulacion_de_politicas.py` | **RED** contra la plantilla aplicada: S-10, S-10b, E-01 a E-04, E-12, E-13, E-16 y E-17 permitidos. **GREEN** tras la corrección. Comprueba además que cada sentencia de endpoint solo usa claves que la referencia admite para su acción y recurso |
| `bootstrap/operador-datos/tests/operador.tftest.hcl` | Dos aserciones nuevas sobre `CreateVpcEndpoint` y `ModifyVpcEndpoint`. **7/7**; con la plantilla aplicada fallan las dos (control negativo) |
| `scripts/terraform_datos/historico/fase-1-red.h031iam-aplicada.json.tftpl` | Copia exacta de la plantilla aplicada (SHA-256 `03109689…75e2`); su render es igual a la política viva |
| `check_plan_operador.py` | Sin relajar: solo fija **8** sentencias para Red en lugar de 6, porque la plantilla cambió. Sigue siendo *create-only* de 7/8 |
| `check_plan_operador_repair.py` + 15 regresiones | Guarda **separada** de la reparación (§18.6) |

### 18.4 Simulación de la política propuesta y Access Analyzer

`iam simulate-custom-policy`, ejecutado por `PersonalBlogAdministrator` con **las tres políticas
propuestas** y sin tocar la viva: **62/62 casos con AWS == evaluador offline == esperado**. Como
contraste, con la Red aplicada AWS y el evaluador coinciden también 62/62, y ambos muestran los 10
casos indebidos de la versión viva.

Access Analyzer: Red corregida (4561), RdsYCustodia (4015), Denegaciones (2225) y trust (252) con
**0 ERROR, 0 SECURITY_WARNING, 0 WARNING y 0 SUGGESTION**.

### 18.5 Preflight en vivo — solo lectura

Los 8 recursos existen. Rol, trust, etiquetas, 0 inline y 3 adjuntos, igual que tras el apply.
Exactamente 3 políticas locales, cada una con **1 versión** y 1 adjunto. Red viva == Red aplicada
(nadie la modificó fuera de Terraform); RdsYCustodia y Denegaciones == plantillas. Rol vinculado
presente, state presente, `.tflock` ausente.

### 18.6 Plan de reparación — **STOP**

| Punto | Resultado |
| --- | --- |
| Plan guardado nuevo | **exit 2 — `0 to add, 1 to change, 0 to destroy`**: solo `aws_iam_policy.fase_1["Red"]`, *update in-place*. SHA-256 del binario `6d3556875d369fc38e8bbd0ea06feb8a568dcf5518a0d3fd55eb879788a46b81`; del JSON `d6ee676f…3f10` |
| Guarda de reparación | **Rechazado: `DRIFT_OR_DEFERRED`** |
| `resource_drift` | **5 entradas**, todas de **metadatos del state**: `attachment_count 0 → 1` en las tres políticas (se crearon antes que sus adjuntos); `managed_policy_arns` del rol, de 0 a 3 elementos (atributo espejo); `tags null → {}` del rol vinculado (normalización del SDKv2, la familia de `domain_dns_ips`). `resource_changes` deja los siete recursos en `no-op` |
| `deferred_changes` / `errored` | 0 / no |
| Diagnóstico, no aceptación | Quitando `resource_drift` **solo en memoria**, la guarda confirma el resto: único cambio en Red, `before` = política aplicada, `after` = plantilla corregida, solo cambia el documento, 6 → 8 sentencias, 14 → 14 acciones Allow, 0 nuevas, 0 de IAM, salidas coherentes |
| Política viva tras el plan | Intacta: 1 versión, documento de H-031-IAM; `.tflock` ausente. **No hubo apply** |

### 18.7 Estado — H-031-IAM S10 FIX: corrección diseñada y simulada; plan BLOQUEADO por drift

Corrección diseñada, implementada en el workspace, simulada en verde y validada por Access
Analyzer. El plan de reparación tiene el contenido correcto, pero no puede declararse listo
mientras `resource_drift` no sea 0. Ese drift no es de infraestructura: es el primer refresh
tras crear. Reconciliarlo exige una decisión explícita del usuario —refresh-only revisado y
autorizado, como DN-2 y el precedente de Task/030—, después de la cual el plan actual quedaría
obsoleto y habría que generar otro. H-031-IAM **no está completo**; H-031-2 no se inició.

## 19. H-031-IAM STATE REFRESH — plan refresh-only preparado, SIN apply (2026-10-04)

Autorización del usuario: **H-031-IAM-STATE-REFRESH PLAN ONLY**. Se trata de preparar, generar
y revisar un plan refresh-only guardado de `bootstrap/operador-datos` para reconciliar **solo**
los metadatos posteriores a la creación. **No** autoriza aplicarlo ni aplicar el plan S-10.
Historia que se conserva: apply inicial (§17), hallazgo S-10, corrección (§18) y plan 0/1/0
rechazado por drift (§18.6).

### 19.1 Freshness y plan S-10 obsoleto

STS de `PersonalBlogAdministrator`, cuenta y región esperadas. Los 8 recursos, sin cambios
respecto al post-apply: rol, trust, etiquetas, 0 inline y 3 adjuntos; 3 políticas, cada una con
**1 versión**; **Red viva == Red aplicada**, no la corregida; `AWSServiceRoleForRDS` para
`rds.amazonaws.com` con `AmazonRDSServiceRolePolicy`. State presente, `.tflock` ausente. Se
registró la versión del objeto de state.

El plan S-10 `6d3556875d36…` y su JSON se renombraron en privado como
**`OBSOLETO-DO-NOT-APPLY`**, sin borrarlos y con su SHA-256 intacto. Se conservan solo como
evidencia: tras el refresh-only no se aplicarán nunca.

### 19.2 Por qué el plan se generó con la plantilla Red APLICADA

Un plan refresh-only **reevalúa las salidas desde la configuración**: comprobado offline, con
backend local y sin provider. Con la plantilla corregida de S-10 en el workspace,
`politicas_fase_1_sha256["Red"]` habría sido un **sexto cambio** que guardaría en el state la
huella de una política que no está viva. Por eso, durante el plan, el root llevó la copia
histórica byte a byte (SHA-256 `03109689…75e2`), que describe la política viva, y la corregida
(`0ae6703d…5a0c`) se restauró al terminar y se verificó. También se comprobó offline que
`apply <plan>` usa la **configuración guardada dentro del plan**, no la del directorio: el futuro
apply de este refresh no depende del archivo del workspace.

> **Corrección del 2026-10-04 (§20).** La última frase es **incorrecta**. Los `.tf` salen del plan,
> pero `templatefile()` vuelve a leer el archivo en el apply y exige el mismo resultado. El experimento
> solo usaba salidas literales.

### 19.3 Plan refresh-only y su revisión

Mismo root, backend, key, workspace `default`, `TF_DATA_DIR` privado y perfil de bootstrap:
`terraform plan -refresh-only -out=<plan>`, sin `-target`, `-replace`, import, `state rm/mv` ni
`force-unlock`.

| Punto | Resultado |
| --- | --- |
| Exit / aplicabilidad | **2**; `applyable` true, `complete` true, `errored` false |
| SHA-256 | Binario `80c71d2f8d4e71e0f4c2817ae80076b7d938cc28cbd41f5bace2cb8c7d47e5f6`; JSON `e50745262e70acb6e7ddcba5d912efb927547e747c33ed6ff8fb1688c12bf2f1` |
| `resource_changes` | **0**: ningún create, update, destroy, *replace*, import ni move |
| `deferred_changes` | **0** |
| `resource_drift` | **5**, todas `update` sobre el state: `attachment_count 0 → 1` en las políticas Red, RdsYCustodia y Denegaciones; `managed_policy_arns` del rol, de `[]` a exactamente las tres políticas de `/personal-blog/`; `tags null → {}` del rol vinculado |
| Salidas | Las tres `no-op` |
| Checks | Todos en `pass` |

Son **solo metadatos**: ningún documento de política, trust, nombre, ruta, etiqueta propia,
adjunto ni versión IAM cambia. Aplicarlo solo escribiría esos cinco valores en el state.

### 19.4 Guarda fail-closed del refresh

`scripts/terraform_datos/check_plan_operador_refresh.py`, separada; las guardas del bootstrap y de la
reparación no se tocaron. Exige direcciones, tipos y acciones exactos; el **único** atributo que
puede diferir en cada entrada, con su antes y su después; los documentos vivos —Red aplicada y las
otras dos según su plantilla—; el trust aprobado; ningún `resource_changes`, ningún diferido y
salidas `no-op`. **19 regresiones** —RED sin el módulo, GREEN con él—: otra política, recurso de red,
RDS o SSM, entrada que falta, otro tipo o acción, `attachment_count` distinto, cuarta ARN o ARN
ajena o de otra cuenta, `tags` con contenido, trust o documento cambiados, documento vivo que no es
el aplicado, otros atributos, salida que cambia (el sexto cambio), diferidos y `resource_changes` de
cualquier acción. Validada además con las cinco entradas reales del plan S-10: falla por `OUTPUTS`
con su salida real y pasa con salidas `no-op`. Sobre el plan refresh-only real: **`REFRESH_PLAN_OK`**.

### 19.5 Prueba de que NO hubo apply

Tras el plan, la **versión del objeto de state es la misma** que antes, el `.tflock` está ausente,
la política Red viva sigue con 1 versión y el documento de H-031-IAM, y el workspace conserva la
plantilla corregida. No se ejecutó `terraform apply` de ningún plan.

### 19.6 Estado — H-031-IAM REFRESH PLAN READY

El plan refresh-only guardado está listo para revisión y espera la autorización explícita de su
apply. **El state todavía no está reconciliado, S-10 no está aplicada y H-031-IAM no está
completo.** Después del refresh, la reparación S-10 necesitará un plan **nuevo**, su guarda y su
propia autorización. `personal-blog-datos` sigue sin configurar; H-031-2 no se inició.

## 20. H-031-IAM STATE REFRESH APPLY — exit 1 con state persistido; STOP (2026-10-04)

Autorización del usuario: aplicar **solo** el refresh-only `80c71d2f…e5f6`, verificar la
reconciliación y, después, generar y revisar un plan S-10 **nuevo**, sin aplicarlo. Con la
condición expresa de **no** reemplazar archivos para el apply.

### 20.1 Freshness y apply

Freshness verde: STS de `PersonalBlogAdministrator`; los 8 recursos sin cambios; Red viva == aplicada,
con 1 versión; rol vinculado correcto; state presente sin `.tflock`; SHA-256 del binario igual al
autorizado; JSON regenerado desde el binario igual al revisado; guarda `REFRESH_PLAN_OK`; plan S-10
viejo solo como obsoleto.

`terraform apply <plan refresh-only exacto>`, con la plantilla Red **corregida** en el workspace,
tal como se autorizó. Resultado: **exit 1**, `Error in function call` en el `templatefile` de las
políticas: «function returned an inconsistent result».

**Causa.** Terraform toma los `.tf` del plan, pero en el apply `templatefile()` **vuelve a leer** el
archivo del directorio y exige el mismo resultado que en el plan. El plan se generó con la plantilla
aplicada y el workspace tenía la corregida. **La afirmación de §19.2 de que el apply no dependía
del archivo del workspace era incorrecta**: el experimento offline usaba salidas literales y no
cubría funciones que leen archivos.

### 20.2 Qué quedó escrito — verificado, no supuesto

| Comprobación | Resultado |
| --- | --- |
| Versión del objeto de state | **Nueva**: el apply fallido **sí persistió** el state; serial 1 → 2, mismo lineage |
| Comparación profunda de ambas versiones (en local y privada) | Solo difieren **los cinco atributos autorizados**: `attachment_count 0 → 1` en las tres políticas, `managed_policy_arns` de 0 a 3, `tags null → {}` del rol vinculado. Ningún otro atributo ni campo; mismas instancias |
| Salidas en el state | **Idénticas** a las previas: la huella de Red sigue siendo la de la política aplicada |
| `check_results` | Mismos cuatro checks; la postcondición de identidad pasa de `unknown` a `pass` por la relectura |
| `.tflock` | Liberado |
| AWS | Sin cambios: los 8 recursos idénticos, Red viva == aplicada con 1 versión |
| Workspace / binarios | Plantilla corregida intacta; binario refresh intacto, ahora **obsoleto** (el state cambió de serial) y marcado en privado como consumido; plan S-10 viejo sigue `OBSOLETO-DO-NOT-APPLY` |

El contenido del state coincide exactamente con lo que el plan refresh-only autorizado pretendía
guardar. Pero el apply **no terminó con exit 0**, que era la condición exigida.

### 20.3 Estado — STOP

No se ejecutaron la convergencia de comprobación, el nuevo plan S-10, la simulación ni Access
Analyzer de esta sesión: dependen de un refresh terminado limpiamente y el usuario debe decidir
antes. S-10 **sigue sin aplicar**, la política Red viva sigue sin corregir, `personal-blog-datos`
no existe y H-031-2 no se inició.

## 21. H-031-IAM — state aceptado y nuevo plan S-10, SIN apply (2026-10-04)

Autorización del usuario: **H-031-IAM-ACCEPT-REFRESH-STATE + S10 REPLAN ONLY**. El usuario **aceptó
como reconciliado** el state resultante del refresh de §20, que **terminó con exit 1**. Lo aceptó por
la evidencia posterior: AWS sin cambios; mismo lineage, serial 1 → 2 y mismas instancias; salidas y
documentos idénticos; solo los cinco atributos autorizados distintos. El paso de `check_results` de
`data.aws_caller_identity.bootstrap` de `unknown` a `pass` se acepta como **metadata derivada de la
reevaluación**, no como cambio de infraestructura. No hubo rollback, segundo refresh ni `state push`.
El plan refresh `80c71d2f…` queda **CONSUMED / STALE / DO NOT APPLY** y el plan S-10 `6d355687…`
sigue **OBSOLETO / DO NOT APPLY**. La historia correcta sigue siendo: exit 1, state persistido y
reconciliación aceptada por evidencia posterior.

Un primer intento se detuvo en STS porque la sesión había caducado; no se hizo ninguna otra llamada.

### 21.1 Freshness — PASS

STS de `PersonalBlogAdministrator`, cuenta esperada, `us-east-2`. Los 8 recursos intactos: rol,
trust y etiquetas correctos, 0 inline, 3 adjuntos, 3 políticas con **1 versión**; Red viva == aplicada;
RdsYCustodia y Denegaciones según plantilla; `AWSServiceRoleForRDS` correcto. State presente,
`.tflock` ausente. Lectura privada del state: **idéntico byte a byte a la versión aceptada**, con el
mismo lineage, serial 2, las mismas instancias, los cinco metadatos reconciliados y las salidas de la
Red aplicada. Plantilla corregida en el workspace; planes anteriores obsoletos. **Sin cambios
temporales de plantilla en todo el checkpoint.**

### 21.2 Nuevo plan S-10

Plan **normal** guardado, desde el workspace vigente y con el mismo backend, key, workspace,
`TF_DATA_DIR` y perfil de bootstrap.

| Punto | Resultado |
| --- | --- |
| Resumen | **exit 2 — `0 to add, 1 to change, 0 to destroy`**; 0 *replace*, 0 import, 0 move |
| SHA-256 | Binario `327a3168f1ada5a0a1beb871c25cf427653d33867eafb445309c279cac62f69d`; JSON `82746bfc3e665116b2909a7ccc65ca92371c3eb3e7cab7302d40e9441f5d00a6` |
| Cambio | Solo `aws_iam_policy.fase_1["Red"]`, *update in-place* y solo su documento; los otros siete recursos, `no-op` |
| `resource_drift` / `deferred_changes` | **0 / 0**: evidencia final de que el state quedó reconciliado |
| Salidas | Solo cambia `politicas_fase_1_sha256["Red"]`, consecuencia del cambio intencional; `arn_del_rol_operativo` y `bucket_de_estado` en `no-op` |
| Guarda de reparación, sin modificar | **`REPAIR_PLAN_OK`**: 0/1/0, Red 6 → 8 sentencias, Allow de Red 14 → 14, 68 en total, 0 nuevas, 0 de IAM |

### 21.3 Simulación y Access Analyzer

`simulate-custom-policy` con las tres políticas propuestas: **62/62, AWS == evaluador offline ==
esperado**. Incluye S-10 y sus variantes, SSM, Secrets Manager, RDS, servicio arbitrario, ausencia de
`ec2:VpceServiceName`, región y etiquetas incorrectas, recursos ajenos, `subnet` y `security-group`, y
los positivos de S3. Contra la Red **viva**, solo como evidencia y sin mutarla: AWS == offline 62/62, y
la política antigua sigue permitiendo los mismos 10 casos indebidos (S-10, S-10b, E-01 a E-04, E-12,
E-13, E-16 y E-17). Access Analyzer sobre la Red corregida (4561), RdsYCustodia (4015), Denegaciones
(2225) y trust (252): **0 ERROR, 0 SECURITY_WARNING, 0 WARNING, 0 SUGGESTION**.

### 21.4 Post y estado — H-031-IAM STATE ACCEPTED / S10 FIX PLAN READY

La versión del state **no cambió** durante la sesión; `.tflock` ausente; la Red viva sigue **original**,
con 1 versión. **S-10 no está aplicada.** El nuevo plan queda en la ruta privada a la espera de la
autorización explícita de su apply. `personal-blog-datos` sigue sin configurar; H-031-2 no se inició.

## 22. H-031-IAM S10 FIX — aplicada y verificada; login del operador pendiente (2026-10-04)

Autorización del usuario: **H-031-IAM S10 FIX APPLY** del único binario revisado (SHA-256
`327a3168f1ada5a0a1beb871c25cf427653d33867eafb445309c279cac62f69d`, JSON
`82746bfc…00a6`), con readback, simulación contra el rol vivo, Access Analyzer, convergencia e
inspección **solo de lectura** del perfil `personal-blog-datos`. Se conserva toda la historia: §17
apply inicial, §18 hallazgo y corrección, §19 plan refresh, §20 refresh con exit 1 y §21 state
aceptado y nuevo plan.

### 22.1 Freshness, apply y state

| Paso | Resultado |
| --- | --- |
| Freshness | STS de `PersonalBlogAdministrator`, cuenta y `us-east-2`; los 8 recursos intactos; Red viva == original con **1 versión**; SLR correcto; state **byte a byte** igual al aceptado en §21; plantilla corregida; SHA-256 del binario y del JSON iguales a los autorizados; JSON regenerado desde el binario == revisado; `REPAIR_PLAN_OK` 0/1/0 solo Red, drift 0 y diferidos 0 |
| Apply | `terraform apply <plan exacto>`, sin cambios temporales de archivos: **exit 0 — `0 added, 1 changed, 0 destroyed`**; único recurso tocado `aws_iam_policy.fase_1["Red"]` |
| Verificación inmediata, aplicada aunque el apply terminó bien | Versión nueva del state, **mismo lineage, serial 2 → 3**; `.tflock` liberado; Red con 2 versiones y la *default* es la corregida |
| State post-apply (lectura privada) | La salida de huellas es **exactamente la planificada** (Red = corregida; las otras dos, iguales); los cinco metadatos de §20 siguen correctos; mismas instancias |

### 22.2 Readback IAM

| Recurso | Resultado |
| --- | --- |
| Política Red | Mismo nombre, ruta `/personal-blog/`, adjunto y etiquetas. **Ciclo de versiones observado:** 2 versiones; la **nueva *default*** contiene la política corregida —8 sentencias, 14 acciones Allow, 0 de IAM, `CreateVpcEndpoint` y `ModifyVpcEndpoint` fuera de `OperarSoloRecursosPropios`— y la **anterior, no *default***, la original de 6 sentencias. No se borró ninguna versión a mano |
| RdsYCustodia / Denegaciones | 1 versión cada una, documento == plantilla |
| Rol operativo | Trust, etiquetas y sesión de 3600 s sin cambios; 0 inline; exactamente 3 adjuntos |
| `AWSServiceRoleForRDS` | Correcto |

### 22.3 Simulación contra el rol vivo, Access Analyzer y convergencia

| Prueba | Resultado |
| --- | --- |
| `iam simulate-principal-policy`, por `PersonalBlogAdministrator` contra el ARN de `PersonalBlogDataOperator` con sus políticas reales adjuntas, sin dar al operador `iam:SimulatePrincipalPolicy` | **62/62, AWS == evaluador offline == esperado**: S-10, S-10a, S-10b, SSM, Secrets Manager, RDS, servicio arbitrario, sin `VpceServiceName`, región y etiquetas incorrectas, recurso ajeno, `subnet` y `security-group` en `implicitDeny`; el gateway de S3 y las operaciones aprobadas, `allowed` |
| Access Analyzer sobre los documentos **vivos** —Red *default*, RdsYCustodia, Denegaciones, trust—, idénticos a los revisados | **0 ERROR, 0 SECURITY_WARNING, 0 WARNING, 0 SUGGESTION** |
| Plan normal de convergencia con la plantilla corregida, no aplicado | **exit 0, «No changes»**: los 8 recursos `no-op`, **`resource_drift = 0`**, diferidos 0, salidas `no-op`; el state no se escribió |

### 22.4 Perfil `personal-blog-datos` — inspección de solo lectura

Solo existe `personal-blog`: región `us-east-2` y `login_session` de la sesión de consola
`assumed-role/PersonalBlogAdministrator/personal-blog-entry-admin`. **`personal-blog-datos` no
existe.** No se tocó `~/.aws` ni se creó ninguna clave.

`aws login` obtiene credenciales de **la sesión de consola seleccionada** (ayuda local de AWS CLI
2.37.1). AWS publica para ello la política administrada `SignInLocalDevelopmentAccess` (v3):
`signin:AuthorizeOAuth2Access` y `signin:CreateOAuth2Token` sobre `oauth2/public-client/*`. Una
simulación de solo lectura desde el bootstrap da **`implicitDeny`** para ambas acciones sobre el
operador: con sus permisos actuales, `aws login` desde una sesión del operador **muy probablemente
fallaría**. La vía que preveía §3 del diseño —un `source_profile` con `aws login` del usuario de
entrada— choca con el mismo requisito y, además, exigiría modificar a ese usuario, algo que el diseño
prohíbe.

> **Corrección (§23).** La frase anterior es **incorrecta**: el usuario de entrada ya tiene `signin` por una
> inline no documentada (`PersonalBlogLocalDevelopmentSignIn`). La vía del diseño §3 no queda descartada. Configurar el perfil necesita, por tanto, una **decisión** y, probablemente, un permiso nuevo
y acotado del servicio `signin` con su propio checkpoint de IAM. No se añadió nada.

### 22.5 Estado — H-031-IAM S10 FIX APPLIED / OPERATOR LOGIN PENDING

La corrección S-10 está **aplicada y viva** en AWS, verificada por readback, simulación contra el rol
real, Access Analyzer y convergencia 0/0/0 sin drift. **H-031-IAM no está completo**: faltan el
contexto `personal-blog-datos` y las pruebas reales de §10.2 con el operador. H-031-2 no se inició.

## 23. H-031-IAM LOGIN PREP — STOP: el usuario de entrada ya tiene permisos `signin` (2026-10-04)

Autorización del usuario: **H-031-IAM-LOGIN-PREP PLAN ONLY**. Su §2 exige verificar en solo lectura
al usuario de entrada **antes** de tocar Terraform y detenerse si ya tiene los permisos de
`aws login`. Los tiene. No se modificó Terraform, IAM, el usuario ni `~/.aws`, y no se generó
ningún plan.

### 23.1 Usuario de entrada — verificación real

| Comprobación | Resultado |
| --- | --- |
| Usuario `personal-blog-entry-admin` | Existe; sin *permissions boundary*; **0** políticas administradas; **0** grupos; **0** access keys; **1** dispositivo MFA |
| Inline `AssumePersonalBlogAdministratorOnly` | La de Task/027: `sts:AssumeRole` solo sobre `PersonalBlogAdministrator` |
| Inline **`PersonalBlogLocalDevelopmentSignIn`** | **No documentada** en Task/027 ni en este repositorio: `signin:AuthorizeOAuth2Access` y `signin:CreateOAuth2Token` sobre `arn:aws:signin:*:*:oauth2/public-client/*`, que incluye `remote`, cualquier región y cualquier cuenta |
| Simulación del usuario | `allowed` para las dos acciones, sobre `public-client/localhost` y sobre `public-client/remote` en `us-east-2` |

**Corrección de §22.4 y del diseño §3.** Allí se afirmó que el usuario de entrada tampoco tenía
permisos `signin`, «por diseño». **Era incorrecto**: se dedujo de una descripción y no se verificó. La
simulación sobre el **operador** (`implicitDeny`) sigue siendo cierta.

### 23.2 Lo que no se pudo demostrar

`simulate-principal-policy` del usuario contra `sts:AssumeRole` sobre `PersonalBlogDataOperator`,
pasando el trust real como política de recurso y con `aws:MultiFactorAuthPresent` `true` o `false`,
devolvió `implicitDeny` **sin ninguna sentencia coincidente**: el simulador no evaluó el trust. Es
**inconcluso**. No demuestra ni que el usuario pueda asumir el rol —el diseño §3 se apoya en que, en
la misma cuenta, un trust que nombra al usuario basta— ni que no pueda. Además, su inline actual solo
le concede `sts:AssumeRole` sobre la administrativa. Solo un intento real lo resolverá.

### 23.3 Vías más simples, sin cambios de IAM

1. **La del diseño §3**, que §22.4 descartó por error. Un perfil del usuario creado con `aws login`
   **sin** cambiar de rol en la consola —el usuario ya tiene `signin`— y `personal-blog-datos` con
   `role_arn`, `source_profile` y `mfa_serial`.
2. **Cambio de rol en la consola** a `PersonalBlogDataOperator` y `aws login` sobre esa sesión, como
   `personal-blog`. Funcionaría solo si AWS evalúa `signin` sobre la identidad de inicio de sesión (el
   usuario) y no sobre la sesión del rol (el operador, sin permisos).

Las dos dependen de que el trust baste para que el usuario asuma el operador (§23.2). Son pasos
humanos que no mutan AWS y se verifican con `sts get-caller-identity`. Si funcionan, la política
`AccesoLocal` del operador **no hace falta**.

### 23.4 Estado — STOP antes del plan

H-031-IAM sigue **S10 FIX APPLIED / OPERATOR LOGIN PENDING**. Queda registrado un hallazgo de
gobierno: la inline `PersonalBlogLocalDevelopmentSignIn` del usuario es más amplia que lo que este
checkpoint consideraba aceptable y no consta en la historia de Task/027. No se tocó. H-031-2 no se
inició.

## 24. H-031-IAM — COMPLETE por decisión operacional del usuario (2026-10-04)

Autorización del usuario: **H-031-IAM — CLOSE WITH ADMIN OPERATIONAL DECISION**. Es una decisión
humana nueva y autoritativa. **No es una limitación técnica.**

### 24.1 La decisión

- Originalmente se diseñó `PersonalBlogDataOperator` por mínimo privilegio (DH-3 modificada). Se creó
  y se validó: §16 a §22.
- Durante H-031-IAM, el flujo humano local para usarlo —`aws login`, permisos `signin`, encadenamiento
  desde el usuario de entrada— añadió una complejidad que el usuario consideró innecesaria (§22.4, §23).
- **El usuario decidió** continuar las operaciones reales restantes de Task/031 con
  **`PersonalBlogAdministrator` mediante el perfil existente `personal-blog`**.
- **No** se crea `personal-blog-datos`, **no** se amplían permisos `signin`, **no** se crea la
  política `AccesoLocal` ni ninguna otra, y **no** se modifica `personal-blog-entry-admin` ni su inline
  `PersonalBlogLocalDevelopmentSignIn`. No se toca `~/.aws` ni se crean access keys.
- `PersonalBlogDataOperator`, sus tres políticas, sus tres adjuntos y `AWSServiceRoleForRDS` **se
  conservan** como infraestructura creada y validada, **sin** eliminarlos, modificarlos ni usarlos como
  contexto operativo activo.

### 24.2 Verificación final

| Comprobación | Resultado |
| --- | --- |
| `sts get-caller-identity --profile personal-blog` | `assumed-role/PersonalBlogAdministrator/…`, cuenta esperada; región del perfil `us-east-2` |
| Readback | S-10 sigue aplicada: Red con 2 versiones, *default* corregida (8 sentencias, 14 Allow, 0 IAM) y la original no *default*; RdsYCustodia y Denegaciones con 1 versión según plantilla; rol, trust, etiquetas, 0 inline y 3 adjuntos sin cambios; `AWSServiceRoleForRDS` correcto |
| Plan normal de convergencia de `bootstrap/operador-datos`, no aplicado | **exit 0 — 0/0/0**: los 8 recursos `no-op`, **`resource_drift = 0`**, **`deferred_changes = 0`**, salidas `no-op`; versión del state sin cambios; `.tflock` ausente |
| IAM adicional | **Ninguno** |

### 24.3 Consecuencia para H-031-2 — pendiente de autorización

El root `terraform-datos` y su guarda están hoy construidos para **rechazar** la identidad
administrativa:

- validación de `var.rol_operativo`, que no admite `PersonalBlogAdministrator`;
- postcondición de `data.aws_caller_identity.operador`, que exige `assumed-role/<rol_operativo>/`;
- `scripts/terraform_datos/check_plan.py`, que exige `rol_operativo = PersonalBlogDataOperator` (`OPERATOR_ROLE`);
- las pruebas de Terraform y Python que fijan ese rechazo, y el ejemplo `produccion.tfvars.example`.

Operar H-031-2 con `personal-blog` exige **alinear** primero esas piezas con la decisión, sin debilitar
la guarda de identidad, que pasaría a exigir exactamente `PersonalBlogAdministrator` en la cuenta
verificada. Es un cambio de código del alcance de Task/031 que requiere su propia autorización. **No se
hizo.**

### 24.4 Estado — H-031-IAM COMPLETE

H-031-IAM queda **cerrado**. La ejecución operativa usa `personal-blog` / `PersonalBlogAdministrator`
**por decisión del usuario**. La historia de §16 a §23 se conserva tal cual: el exit 1 del refresh
(§20) no se reescribe como éxito. H-031-2 **no se inició**.

## 25. H-031-2-ALIGN — `terraform-datos` exige `PersonalBlogAdministrator` (2026-10-04)

Autorización del usuario: **H-031-2-ALIGN**. Se trata de alinear **offline** `terraform-datos`, su guarda,
pruebas y documentación con la decisión de §24. **Cero llamadas a AWS**: sin STS, `init` remoto, plan
ni apply. El operador IAM existente no se tocó.

### 25.1 Cambio

| Archivo | Cambio |
| --- | --- |
| `terraform-datos/variables.tf` | `rol_operativo`: valor por defecto **`PersonalBlogAdministrator`** y validación **`var.rol_operativo == "PersonalBlogAdministrator"`**, con un solo valor admitido. Se conserva la variable: el plan sigue mostrando la identidad exigida y la guarda la comprueba sin cambiar el contrato de variables. La descripción de `contrasena_master` ya no habla de custodia en disco (§25.4) |
| `terraform-datos/main.tf` | Solo el comentario. La postcondición de `data.aws_caller_identity.operador` no cambia de forma: exige la cuenta en `cuentas_permitidas` y un ARN que empiece por `arn:aws:sts::<CUENTA>:assumed-role/<rol_operativo>/`; el `/` final impide nombres parecidos. Bypass solo con `var.laboratorio` |
| `terraform-datos/entornos/produccion/produccion.tfvars.example` | `rol_operativo = "PersonalBlogAdministrator"` |
| `scripts/terraform_datos/check_plan.py` | `ROL_OPERATIVO = "PersonalBlogAdministrator"`; `OPERATOR_ROLE` se conserva y exige igualdad exacta: no hay lista de roles |
| `terraform-datos/tests/datos.tftest.hcl` | Identidad por omisión del provider simulado: la administrativa. Sustituye «administrativa rechazada» y «no configurable» por siete casos (§25.2) |
| `tests/terraform_datos/test_check_plan.py` | Fixture con la administrativa; `test_rol_operativo_exacto` |
| Documentación vigente | Ficha (objetivo, archivos y pasos), STATUS, ROADMAP, STAGE-10, diseño de identidad, runbook del bucket de state y `target-production-architecture.md` |

### 25.2 Pruebas — RED y GREEN

**RED**: con las pruebas nuevas y el código anterior, la primera ejecución de `terraform test` falla en la
postcondición de identidad y el resto se omite; `test_check_plan` falla en 59 puntos porque
`OPERATOR_ROLE` salta antes que cualquier otra comprobación.

**GREEN** (`terraform test` 27/27; antes 22, con 2 sustituidas y 7 añadidas):

| Caso | Resultado |
| --- | --- |
| A. Producción + variable `PersonalBlogAdministrator` | **Pasa** |
| B. Producción + variable `PersonalBlogDataOperator` | **Falla** en `var.rol_operativo` |
| C. Producción + rol arbitrario | **Falla** en `var.rol_operativo` |
| D. Sesión `assumed-role/PersonalBlogAdministrator/<sesión>` | **Pasa** |
| E. Sesión `assumed-role/PersonalBlogDataOperator/<sesión>` | **Falla** en la postcondición |
| Sesión de un rol arbitrario y sesión `PersonalBlogAdministratorX` | **Fallan** |
| F. Cuenta ajena con la sesión administrativa | **Falla** |
| Usuario IAM directo | **Falla** |
| Laboratorio con identidad ficticia y `laboratorio = true` | **Pasa**, con los mismos módulos |

`check_plan`: el plan esperado con la administrativa da `PLAN_OK` (21 altas); `PersonalBlogDataOperator`,
`OtroRol`, `PersonalBlogAdministratorX`, cadena vacía, nulo y la lista de los dos roles dan
**`OPERATOR_ROLE`**.

### 25.3 Lo que no cambió

El primer plan de datos sigue fijado en **21 recursos** (`check_plan` y `terraform test`). El grupo por
omisión sigue sin gestionar; RDS solo `sg-rds`; el gateway de S3 sin grupos; las guardas de canario,
`resource_drift` y `deferred_changes` siguen siendo fail-closed; DN-2 condicionada y DN-3 cerrada.
**Ninguna guarda se debilitó** y las de `bootstrap/operador-datos` (bootstrap, reparación y refresh) no se
tocaron. `PersonalBlogDataOperator`, sus políticas, adjuntos, trust, state y salidas siguen intactos.

### 25.4 Contraseña master efímera — procedimiento para H-031-2 y H-031-3

**Hecho comprobado offline** (Terraform 1.16.2, raíz efímera sin provider ni AWS, con valores de prueba
que no son secretos):
- al aplicar un plan guardado, una variable efímera usada en el plan es **obligatoria** («must be set»);
- **no necesita el mismo valor**: el apply con otro valor terminó bien;
- el valor no aparece ni en el plan ni en el state.

En este root, además, el plan **no depende** del valor: la contraseña solo alimenta `password_wo` y
`value_wo` (*write-only*), `password_wo_version` sale de otra variable y `check_plan` rechaza su presencia
(`EPHEMERAL_LEAK`, `SECRET_IN_PLAN`). Por eso no hace falta conservar ningún valor entre H-031-2 y
H-031-3, y no se inventa ninguna custodia intermedia.

| Checkpoint | Procedimiento |
| --- | --- |
| **H-031-2** (plan) | El runner de Python que ejecuta `terraform plan` genera **en memoria** un valor **desechable** con `secrets`: 48 caracteres alfanuméricos, dentro de la validación de 32 a 64. Lo pasa **solo** en el entorno del proceso hijo de Terraform (`TF_VAR_contrasena_master`), nunca en la línea de comandos. Antes de terminar busca ese valor en el plan binario, el JSON y los logs, y debe estar ausente. Después lo descarta: no se reutiliza nunca |
| **H-031-3** (apply del plan exacto) | El runner genera **en ese momento** la contraseña **real** de la misma forma y la pasa solo por el entorno del `terraform apply <plan>`. Terraform la escribe en RDS (`password_wo`) y en el SecureString `/blog-prod/datos/blogadmin` (`value_wo`, `aws/ssm`), que es su **única custodia** (DH-2/D-23). Antes de terminar, el runner comprueba —solo con un resultado booleano— que el SecureString coincide y que el valor no aparece en el state, las salidas ni los logs. Después lo descarta |
| Interfaz humana | En PowerShell solo se invoca el runner. **El valor nunca se teclea, se imprime ni pasa por argumentos**: no queda en el historial de la consola. Nada va a tfvars, archivos temporales, logs, Git ni documentación. Cada invocación es un proceso propio, así que el entorno desaparece al terminar |

**Límites declarados.** Las cadenas de Python no se pueden borrar de memoria de forma garantizada: se
libera la referencia y el proceso termina. Mientras dura la ejecución, otro proceso del mismo usuario
podría leer el entorno. Si el apply falla después de crear la instancia y antes de escribir el
SecureString, la contraseña se pierde: es STOP, y se recupera rotándola (nuevo valor y
`version_de_la_contrasena + 1`) con su propio plan autorizado.

### 25.5 Estado — H-031-2-ALIGN READY

`terraform-datos` y su guarda exigen exactamente `PersonalBlogAdministrator`. H-031-2 **no se inició**: ni
STS, ni `init` remoto, ni plan, ni contraseña real.

## 26. H-031-2 — plan guardado de red y RDS, SIN apply (2026-10-04)

Autorización del usuario: **H-031-2 PLAN ONLY**, con `personal-blog` / `PersonalBlogAdministrator`, y
después la decisión **CONTINUE AFTER ORDERABILITY ANOMALY**. Configuración, planes y evidencia están en
`%LOCALAPPDATA%/PersonalBlog/application/data/`, **fuera del checkout**. Un primer intento se detuvo en
STS porque la sesión había caducado; no se hizo ninguna otra llamada.

### 26.1 Preflight y anomalía de orderabilidad

La **primera** ejecución del preflight recibió de `DescribeOrderableDBInstanceOptions` (PostgreSQL 17.11,
`db.t4g.micro`, VPC) las cuatro opciones de almacenamiento **solo en `us-east-2c`**, y se detuvo. Las
consultas exactas repetidas devolvieron `us-east-2a`, `us-east-2b` y `us-east-2c`. Esa primera respuesta
se conserva en privado como **anomalía histórica**; **no se conoce su causa**. El diseño no cambió.

Con la decisión del usuario se ejecutó un **gate extra**: dos consultas exactas consecutivas, guardadas en
privado. Ambas dieron **PASS**: una sola opción gp3, mínimo 20 y máximo 6144 GiB, cifrado admitido,
zonas `us-east-2a` y `us-east-2b` (además de `us-east-2c`).

Preflight completo, solo de lectura: STS correcto; **ninguno de los 21 recursos existe** —VPC por
etiquetas y por el CIDR 10.40.0.0/16, subredes, tablas, grupos por etiquetas y por nombre, reglas,
endpoint, instancia, subnet group, parameter group, snapshot final, grupo de logs y SecureString—;
`use2-az1` y `use2-az2` disponibles; PostgreSQL 17.11 con familia `postgres17`; la key
`application/data/terraform.tfstate` no existe, sin versiones ni *delete markers*, y no hay `.tflock`.

### 26.2 Contrato de medios, init y plan

| Paso | Resultado |
| --- | --- |
| Contrato de medios | Solo las salidas `arn_del_bucket` y `nombre_del_bucket` del state remoto de `terraform-medios`, leídas en memoria: coherentes con el bucket revisado y accesible. tfvars operativo y variables de la guarda escritos solo en el directorio privado, sin secretos |
| `init` | `backend.generado.tf` regenerado con `backend "s3" {}` (ignorado por Git), como en `terraform-medios` (runbook del bucket de state §3). Backend S3, key `application/data/terraform.tfstate`, `use_lockfile` y `encrypt`, sin DynamoDB, workspace `default`, `TF_DATA_DIR` privado; sin migración ni copia de state local; lock de providers intacto; state remoto todavía ausente |
| Contraseña del plan | **Desechable**, según §25.4: 48 alfanuméricos con `secrets`, solo en memoria y en el entorno del subproceso de Terraform; descartada al terminar y **no** conservada para H-031-3 |
| Plan guardado | STS repetido; **exit 2 — `21 to add, 0 to change, 0 to destroy`**; 0 *replace*, 0 import, 0 move. SHA-256 del binario `25f2e889f1e7e65905a633df8103a28ed2f16363e37aa64ad97e94cb1c016f76`; del JSON `97cc1a76edb27316b343b49fa3ecc8aa66907f380e19286fecc1f203603f968a` |
| `resource_drift` / `deferred_changes` | **0 / 0** |
| `check_plan.py`, sin modificar | **`PLAN_OK`**: las 21 direcciones exactas, solo `create` |
| Búsqueda del secreto | **`SECRET_ABSENT = true`**: el valor desechable no aparece en el plan binario, el JSON, los logs ni el checkout, y no hay state |

### 26.3 Revisión

Terraform 1.16.2; completo, `applyable`, sin errores. Postcondición de identidad `pass` con
`PersonalBlogAdministrator` exacto; la variable efímera no figura en el plan. Ningún
`aws_default_security_group`, IAM, NAT, IGW, EIP ni Lambda; nada de checkpoints posteriores. Grupos
`blog-prod-lambda`, `blog-prod-admin` y `blog-prod-rds`; **RDS solo con `var.id_sg_rds`**. Instancia:
PostgreSQL **17.11**, **`db.t4g.micro`**, **gp3 20 GiB** con máximo 50, cifrada, **no pública**,
**Single-AZ**, `deletion_protection = true`, snapshot final `blog-prod-postgres-final` conservado, Extended
Support deshabilitado, sin `password` ni `password_wo` en el plan. Endpoint **Gateway**
`com.amazonaws.us-east-2.s3`, **sin** grupos ni `subnet_ids`. SecureString `/blog-prod/datos/blogadmin`
estándar con `alias/aws/ssm`, sin `value` ni `value_wo` en el plan.

### 26.4 Post-plan y estado — H-031-2 PLAN READY FOR APPLY REVIEW

Ninguna VPC, grupo, instancia RDS ni SecureString creados; state de datos todavía ausente; `.tflock`
ausente. Plan y JSON solo en la ruta privada. **Sin apply.** H-031-3 aplicará ese binario exacto si se
autoriza, con la contraseña **real** generada entonces según §25.4. DN-2 sigue condicionada.

## 27. H-031-3 — apply autorizado, detenido por orderability antes de aplicar (2026-10-04)

Autorización del usuario: **H-031-3 — APPLY EXACT SAVED PLAN**, solo para el binario
`25f2e889f1e7e65905a633df8103a28ed2f16363e37aa64ad97e94cb1c016f76`. El runner propio de H-031-3 vive
fuera de Git; el de H-031-2 no se tocó. Antes de los gates en AWS, una prueba offline del readback con
respuestas simuladas dio PASS en el caso ideal y detectó los 14 defectos inyectados.

### 27.1 Gates previos

| Gate | Resultado |
| --- | --- |
| STS | `assumed-role/PersonalBlogAdministrator/<sesión>`, cuenta esperada, us-east-2 |
| Plan | SHA-256 exacto. La configuración del root y de los dos módulos, y el lock de providers, son idénticos a la instantánea guardada dentro del plan. `show -json` vuelve a dar el SHA revisado; 21/0/0 con las mismas 21 direcciones, `resource_drift = 0`, `deferred_changes = 0`, `PLAN_OK` |
| State | Key ausente y sin versiones; `.tflock` ausente. Bajo el prefijo solo está el rastro del lock del plan de H-031-2 (una versión no vigente y un *delete marker* del `.tflock`, 2026-10-04 23:01:05–23:01:13 UTC). El bucket está versionado, así que ese rastro es lo esperado y el runner lo fija con exactitud |
| Ausencia | Ninguno de los 21 recursos existe |
| **Orderability 1/2** | **FAIL**: las cuatro opciones de almacenamiento (gp2, gp3, io1, io2) aparecen **solo en `us-east-2c`**. gp3 sigue con mínimo 20, máximo 6144 y cifrado |

### 27.2 STOP y estado

El runner se detuvo en la primera consulta, **antes de generar la contraseña productiva**. No hubo
segunda consulta, ni contraseña real, ni `terraform apply`, ni ningún otro cambio. La lectura posterior
confirma que el state de datos sigue ausente, que no hay `.tflock` ni instancia RDS y que el SHA del plan
no cambió. Clase, versión, almacenamiento y zonas **no se cambiaron**.

Es la **segunda** respuesta con esta forma exacta: la primera fue en H-031-2 (§26.1), mientras que las tres
consultas intermedias devolvieron `us-east-2a`, `us-east-2b` y `us-east-2c`. **No se declara la causa.**
Las dos respuestas se conservan en el directorio privado. H-031-3 queda **bloqueado** hasta una nueva
decisión del usuario. El plan revisado sigue siendo el único autorizado y no se generó ningún sustituto.

### 27.3 H-031-3-ORDERABILITY-DIAG — solo lectura (2026-10-05)

Autorización del usuario: **H-031-3-ORDERABILITY-DIAG — READ ONLY**. Sin plan ni apply, sin contraseña y
sin cambios de código. El primer intento se detuvo en STS porque la sesión había caducado; se repitió
tras renovarla.

**Contrato de zona, sacado del código real y confirmado en el JSON del plan revisado:**

| Eslabón | Código |
| --- | --- |
| Subredes | `subredes.a.zona_id = use2-az1`, `subredes.b.zona_id = use2-az2` (variables y tfvars privado) |
| Salida de `red` | `zonas_de_subredes = { for clave, subred in aws_subnet.privada : clave => subred.availability_zone }` |
| Root | `module.base_de_datos.zona = module.red.zonas_de_subredes["a"]` |
| Instancia | `aws_db_instance.this.availability_zone = var.zona`, con `multi_az = false` |
| Subnet group | `aws_db_subnet_group.this.subnet_ids = var.ids_de_subredes` ← `module.red.ids_de_subredes` (a y b) |

Conclusión:
- La instancia Single-AZ queda **fijada a la AZ de `use2-az1`**, cuyo nombre se resuelve en el apply.
- El DB subnet group lleva las subredes de `use2-az1` y `use2-az2`.
- El gate de orderability **de la instancia** debe demostrar `us-east-2a`. `us-east-2b` sigue siendo
  necesaria para el subnet group: se comprueba que existe y está `available`, pero no hace falta que
  `db.t4g.micro` sea contratable allí.

**Mapeo vigente** (`describe-availability-zones`, 2026-10-05 00:39:24 UTC): `use2-az1 → us-east-2a`,
`use2-az2 → us-east-2b` y `use2-az3 → us-east-2c`, las tres `available`.

**Seis muestras exactas** (`postgres` 17.11, `db.t4g.micro`, `--vpc`, `--no-paginate`), con unos 30 s
entre una y otra. Todas devolvieron 4 opciones, sin `Marker`, con una sola opción gp3: mínimo 20,
máximo 6144 GiB y cifrado admitido.

| # | UTC | Zonas de gp3 | `us-east-2a` |
| --- | --- | --- | --- |
| 1 | 00:39:24 | a, b, c | PASS |
| 2 | 00:39:57 | a, b, c | PASS |
| 3 | 00:40:29 | a, b, c | PASS |
| 4 | 00:41:00 | a, b, c | PASS |
| 5 | 00:41:31 | a, b, c | PASS |
| 6 | 00:42:03 | a, b, c | PASS |

**Control de paginación.** En las muestras 1 y 6 se lanzó, justo después, la misma consulta sin
`--no-paginate`. Ambos modos devolvieron respuestas equivalentes una vez ordenadas: la paginación del
AWS CLI no explica la diferencia.

**Historial completo guardado.** Hay 13 respuestas exactas en el directorio privado. Dos de ellas tienen
la forma anómala, con las cuatro opciones **solo en `us-east-2c`**: la primera de H-031-2 (2026-10-04
22:50 UTC) y la de H-031-3 (23:40 UTC). Las otras once incluyen a, b y c: la repetición y los dos gates
de H-031-2, y las seis muestras y los dos controles de este diagnóstico. **La causa sigue sin
declararse.** Seis aciertos en unos tres minutos no excluyen que se repita.

**Resultado: H-031-3 ORDERABILITY DIAG — STABLE FOR TARGET AZ.** El diseño, el runner, el plan y el state
no cambiaron, y no se hizo ninguna llamada que mute recursos.

### 27.4 H-031-3 — reintento: apply fallido en el parameter group (2026-10-05)

Autorización del usuario: **H-031-3 — RETRY APPLY WITH CORRECT TARGET-AZ GATE**, sobre el mismo binario
`25f2e889…6f76`.

**Corrección del gate.** Solo cambió `orderability()` del runner privado, más dos imports:
- lee el mapeo de zonas en el momento y exige `use2-az1 → us-east-2a` y `use2-az2 → us-east-2b`, ambas
  `available`;
- hace dos consultas exactas con `--no-paginate`, separadas unos 30 s, que exigen una sola opción gp3,
  20 GiB contratables, cifrado, `us-east-2a` y ningún `Marker`. `us-east-2b` solo se registra.

Offline dio el resultado esperado en 13/13 casos. Los artefactos privados del primer intento se copiaron
a una subcarpeta propia para que el reintento no los sobrescribiera. Este gate refleja la arquitectura
real; el primero exigía a y b a la vez.

**Gates en verde:**
- STS correcto, y otra vez antes de generar la contraseña.
- Plan: SHA exacto, configuración y lock idénticos, `show -json` igual al revisado, 21/0/0, `PLAN_OK`,
  sin drift ni diferidos.
- State ausente y sin `.tflock`; ninguno de los 21 recursos existía.
- Mapeo vigente correcto. Orderability **PASS** a las 01:19:10 y a las 01:19:42 UTC (a, b y c).

**Apply.** La contraseña productiva se generó después de los gates y solo viajó en el entorno del
subproceso. `terraform apply -input=false -no-color <binario>` terminó con **exit 1**. Se crearon 20
recursos: VPC, subredes, tablas, asociaciones, los tres grupos y sus cinco reglas, el endpoint, el subnet
group, el grupo de logs y el SecureString. Después falló la configuración del parameter group:

```text
Error: modifying RDS DB Parameter Group (blog-prod-postgres17): operation error RDS: ModifyDBParameterGroup,
https response error StatusCode: 400, api error InvalidParameterValue:
The parameter superuser_reserved_connections cannot be modified.
```

La instancia depende del parameter group y **no llegó a intentarse**.

**Inspección de solo lectura:**

| Punto | Resultado |
| --- | --- |
| Lock | Liberado |
| State | Existe, serial 1, con **20 de 21** direcciones; falta `aws_db_instance.this`. El parameter group está **`tainted`** |
| Existencia real | Coincide con el state: 1 VPC, 2 subredes, 2 tablas, 3 grupos, 5 reglas, 1 endpoint, subnet group, parameter group, grupo de logs y SecureString. **RDS no existe** y el snapshot final tampoco |
| Parameter group en AWS (`source=user`) | Solo `log_connections`, `log_disconnections`, `log_min_duration_statement` y `log_statement` |
| Catálogo `postgres17` (`describe-engine-default-parameters`) | `superuser_reserved_connections`: **`IsModifiable = false`**, estático, valor de sistema **3**. `rds.force_ssl` (sistema 1) y `ssl_min_protocol_version` (sistema TLSv1.2) son modificables, igual que los cuatro `log_*` |
| SecureString | Existe; **`SSM_PASSWORD_MATCH = true`** |
| Secreto | **`PRODUCTION_SECRET_ABSENT = true`**: 3 buffers en memoria y 18 771 archivos (privado + checkout sin `.git`), sin ilegibles. Se omitieron por tamaño los binarios del provider, un JSONL de planes simulados y `trivy.db` |
| **PASSWORD ROTATION REQUIRED** | **No**: la instancia no existe. El SecureString guarda una contraseña que ninguna base de datos usa |

**Causa demostrada por el error de la API y el catálogo.** D-22 §3.8 declara `superuser_reserved_connections
= 3` como parámetro explícito, y RDS no permite modificarlo. El valor que se quería, 3, es el valor de
sistema.

**Por qué no se detectó antes:**
1. El comentario del módulo prometía que H-031-2 confirmaría el tipo real de cada parámetro con
   `describe-engine-default-parameters` antes del plan. **Esa comprobación nunca se ejecutó**: es una omisión
   de H-031-2.
2. `check_plan.py` exige ese parámetro, así que no podía detectarlo.
3. Floci aceptó el parameter group sin validar `IsModifiable`. Es una diferencia de paridad que hay que
   registrar.

**Costo.** Ninguno de los 20 recursos tiene cargo por hora: VPC, subredes, tablas, grupos, gateway endpoint de
S3, subnet group, parameter group, grupo de logs sin ingesta y SecureString Standard.

**No se hizo:** ningún reintento, reparación ni destroy; ningún segundo plan; ningún `taint` o `untaint`;
ninguna manipulación del state.

**Recuperación propuesta, sin ejecutar y pendiente de decisión del usuario:**
1. **Cambio de decisión D-22 §3.8.** Retirar `superuser_reserved_connections` de los parámetros explícitos.
   El valor 3 sigue vigente como valor de sistema no modificable y el presupuesto de conexiones no cambia.
   Afecta al módulo, `check_plan.py`, las pruebas y el fixture del laboratorio. Además, el preflight
   ganaría una guarda que exija `IsModifiable = true` y un `ApplyType` coherente con `apply_method` en cada
   parámetro explícito.
2. **Contraseña.** El plan de recuperación debe subir `version_de_la_contrasena` a 2, para que RDS (al
   crearse) y el SecureString (actualizado en sitio) reciban el mismo valor nuevo. Con la versión en 1, RDS
   nacería con un valor nuevo y el SecureString conservaría el anterior, porque `value_wo` solo se reenvía
   cuando cambia su versión.
3. **Plan de recuperación desde el state actual,** sin destruir lo creado. Lo esperado: reemplazo del parameter
   group `tainted` (con seis parámetros), creación de la instancia, actualización del SecureString y el
   resto sin cambios. Necesita su propia guarda, porque `check_plan.py` solo valida el plan inicial, y una
   revisión DN-2 si el refresh de los recursos creados muestra `resource_drift`.

Estado: **H-031-3 APPLY FAILED / RECOVERY REVIEW REQUIRED.**

## 28. H-031-3-RECOVERY — corrección de D-22 y plan de recuperación (2026-10-05)

Autorización del usuario: **H-031-3-RECOVERY — FIX + PLAN ONLY**. Acepta el diagnóstico de §27.4 y prohíbe
el apply, destruir lo existente, rotar la contraseña y cualquier `untaint`, `state rm`, `import` o
`state mv`. El runner privado es propio (`tmp/h0313r/`, evidencia con prefijo `h0313r-`) y no tiene fase
de apply.

### 28.1 Corrección offline

| Archivo | Cambio |
| --- | --- |
| `terraform/modulos/base_de_datos/main.tf` | `superuser_reserved_connections` sale de `local.parametros`: quedan **seis** parámetros explícitos. El comentario documenta `Source = system`, `IsModifiable = false` y el valor de sistema 3 |
| `scripts/terraform_datos/check_plan.py` | `PARAMETROS` con los seis valores y `PARAMETROS_DE_SISTEMA = {"superuser_reserved_connections": "3"}`, que no se gestiona. La guarda del primer despliegue no se debilita: sigue exigiendo el conjunto exacto |
| `scripts/terraform_datos/check_parametros.py` (**nuevo**) | Preflight **antes de planificar**. Contra el catálogo real de `postgres17` exige que cada parámetro explícito exista, tenga `IsModifiable = true` y declare el `apply_method` de su `ApplyType` (`dynamic` → `immediate`, `static` → `pending-reboot`); que ningún parámetro de sistema se gestione; y que el catálogo siga declarando `superuser_reserved_connections = 3` con `Source = system` e `IsModifiable = false` |
| `scripts/terraform_datos/check_plan_recuperacion.py` (**nuevo**) | Guarda **separada** del plan de recuperación (§28.4) |
| `terraform-datos/tests/datos.tftest.hcl` | Exige los seis parámetros |
| `tests/terraform_datos/test_check_parametros.py` (**nuevo**, 24) · `test_check_plan.py` (+1) · `test_check_plan_recuperacion.py` (**nuevo**, 36) | Incluyen la regresión de H-031-3: el conjunto de siete se rechaza con `PARAM_NOT_MODIFIABLE superuser_reserved_connections`, y un plan que vuelva a gestionarlo da `PARAMETERS` |
| `tests/laboratorio/drift_observado.py` | El fixture de la observación del laboratorio lleva los seis parámetros vigentes, con una nota de por qué |
| `production-postgresql-rds-decisions.md` (D-22 §3.8) y `aws-local-parity.md` | Corrección de D-22 y hallazgo de paridad: Floci aceptó el parámetro no modificable |

**RED → GREEN.**
- **RED de las pruebas nuevas, antes de implementar:**
  - el preflight no existía (`ModuleNotFoundError`);
  - `check_plan` aún exigía 7 parámetros (`7 != 6`);
  - la guarda de recuperación no existía.
- **Correcciones durante el GREEN:**
  - **Código:** la prueba de regresión exigía `PARAM_NOT_MODIFIABLE`, pero la implementación evaluaba antes la lista de parámetros de sistema y devolvía otro código. Se corrigió el orden en el código, no la prueba.
  - **Fixture:** el fixture de recuperación compartía por referencia el `values` del state previo y el `before` del no-op, y la prueba de la zona alteraba el `before` sin quererlo. Se corrigió el fixture para que la zona cambie de forma coherente en ambos sitios; la intención de la prueba no cambió.

### 28.2 Catálogo real y preflight del state parcial

El **primer** intento se detuvo con `FAMILY` antes de planificar. Al paginar solo, el AWS CLI fusiona las
437 entradas pero **descarta `DBParameterGroupFamily`**, así que la guarda no podía demostrar la familia.
La guarda **no se relajó**:
- el runner lee las **páginas crudas** (`--no-paginate` y `--marker`): 5 páginas, todas de `postgres17`;
- la guarda exige la familia **en cada página** y que solo la última llegue sin `Marker`;
- la salida fusionada del CLI se sigue rechazando, con su propia prueba (RED de 6 errores y después GREEN).

El primer catálogo se conserva en privado.

**`check_parametros`: `PARAMETERS_OK`.**

| Parámetro | `IsModifiable` | `ApplyType` | `apply_method` |
| --- | --- | --- | --- |
| `log_connections` | true | dynamic | immediate |
| `log_disconnections` | true | dynamic | immediate |
| `log_min_duration_statement` | true | dynamic | immediate |
| `log_statement` | true | dynamic | immediate |
| `rds.force_ssl` | true | dynamic | immediate |
| `ssl_min_protocol_version` | true | dynamic | immediate |
| `superuser_reserved_connections` (**no gestionado**) | **false** | static | — (valor de sistema **3**, `Source = system`) |

**Preflight, solo lectura:**
- STS correcto.
- State en serial 1, con **20 de 21** recursos: falta solo `aws_db_instance.this` y únicamente el parameter group está `tainted`.
- RDS y snapshot final ausentes; no hay `.tflock`.
- SecureString en versión 1, tipo SecureString, Standard y `alias/aws/ssm`.
- Lo que existe en AWS coincide con el state, ID por ID: VPC, 2 subredes, 2 tablas, 2 asociaciones, 3 grupos, 5 reglas, endpoint, subnet group, parameter group y grupo de logs.

### 28.3 Plan de recuperación — sin apply

- **Contraseña:** **no se rotó**. `version_de_la_contrasena` sigue en 1 y el tfvars privado no la fija. El runner leyó `/blog-prod/datos/blogadmin` con `--with-decryption` **solo en memoria** y la pasó únicamente por `TF_VAR_contrasena_master`.
- **Plan:** **exit 2 — `Plan: 2 to add, 0 to change, 1 to destroy.`**, generado desde el state real. No se reutilizó `h0312.tfplan`, que sigue intacto.
- **SHA-256:** del binario `73c41d50f3e16f55e82b3ea05c24f36aec3fb532fec4763fadfc53576af13d42`; del JSON `13a854e2ba79172f8ee314f9952bdd5be21a2b47c7256422a26f5383512b124d`.

| Recurso | Acción |
| --- | --- |
| `module.base_de_datos.aws_db_parameter_group.this` | **`["delete", "create"]`**, `action_reason = replace_because_tainted`: de los 7 parámetros del state a los **6** |
| `module.base_de_datos.aws_db_instance.this` | **`create`** |
| `module.base_de_datos.aws_ssm_parameter.contrasena_master` | **`no-op`** (`before == after`, `value_wo_version = 1`) |
| Los otros 18 recursos existentes | **`no-op`** |
| Salidas | `create` solo para `arn_rds`, `endpoint_rds` e `id_de_recurso_rds`; el resto, `no-op` |

**Semántica del reemplazo.**
- Es *delete-then-create*, sin `create_before_destroy`.
- El nombre es fijo y ninguna instancia usa el grupo, así que el borrado no tiene dependencias que lo bloqueen.
- Terraform crea después el grupo con los seis parámetros y luego la instancia que lo referencia.

**RDS en el plan:**
- **Motor y capacidad:** PostgreSQL **17.11**, `db.t4g.micro`, gp3 de **20 GiB** con máximo **50**, cifrada.
- **Ubicación y red:** **Single-AZ** en `us-east-2a` (subred `a` = `use2-az1`, leída del state), `publicly_accessible = false` y `vpc_security_group_ids` = **solo** el `sg-rds` del state.
- **Protección y snapshot final:** `deletion_protection = true`, `skip_final_snapshot = false` y `blog-prod-postgres-final`.
- **Backups y mantenimiento:** retención de 7 días, ventanas `07:00-07:30` y `sun:08:00-sun:09:00`.
- **Grupos:** subnet group `blog-prod-postgres` y parameter group `blog-prod-postgres17`.
- **Logs y certificado:** logs `postgresql`, CA `rds-ca-rsa2048-g1`, Extended Support deshabilitado.
- **Contraseña:** `password_wo_version = 1`; ni `password` ni `password_wo` aparecen en el plan.

**Secreto: `RECOVERY_SECRET_ABSENT = true`.** Se buscó en la salida del plan y en el state, ambos en
memoria, y en 19 237 archivos del directorio privado y del checkout sin `.git`, plan y JSON incluidos. No
hubo ilegibles; solo se omitieron por tamaño los binarios del provider, `trivy.db` y un JSONL de planes
simulados. El valor se descartó al terminar.

### 28.4 Guarda de recuperación — `DRIFT_OR_DEFERRED` → DN-2

`check_plan_recuperacion.py` admite **únicamente**:
- el reemplazo del parameter group exacto, solo por `tainted` y borrando antes de crear;
- el `create` de la instancia con el contrato de D-22, D-23 y D-10, en la zona de `use2-az1`, con `sg-rds`
  y `password_wo_version = 1`;
- `no-op` con `before == after` en los otros 19 recursos, incluido el SecureString;
- ningún recurso nuevo, IAM, NAT ni IGW, ninguna salida de red alterada y ningún CIDR abierto.

`resource_drift` y `deferred_changes` son fail-closed. El plan real dio `deferred_changes = 0`, pero
**`resource_drift = 4`**, y la guarda lo **rechazó**:

| Dirección | Atributos (antes → después del refresh) | `relevant_attributes` |
| --- | --- | --- |
| `module.red.aws_security_group.admin` | `egress: [] →` la regla gestionada aparte `admin_a_rds` (5432 → `sg-rds`) | solo `id` |
| `module.red.aws_security_group.lambda` | `egress: [] →` `lambda_a_s3` (443 → prefix list de S3) y `lambda_a_rds` (5432 → `sg-rds`) | solo `id` |
| `module.red.aws_security_group.rds` | `ingress: [] →` `rds_desde_lambda` y `rds_desde_admin` (5432) | solo `id` |
| `module.base_de_datos.aws_db_parameter_group.this` (tainted) | `name_prefix: null → ""`; `parameter`: `rds.force_ssl` y `ssl_min_protocol_version` pasan de `apply_method = immediate` a **`pending-reboot`**, con los mismos valores | `family`, `parameter`, `name` (se reemplaza) |

**Comparación con el laboratorio (§14 y §15), sin suponer que AWS es Floci:**
- **Grupos de seguridad:** el reflejo de las reglas gestionadas aparte tiene la **misma forma**
  (`agrega_reglas_separadas`). La diferencia está en el `before`: en Floci incluía la salida por omisión; en
  AWS está **vacío**, porque Terraform retiró esa regla al crear cada grupo.
- **Parameter group:** Floci mostraba `parameter → []`, porque no devuelve parámetros de usuario. AWS
  devuelve el conjunto con otro `apply_method` en los dos parámetros cuyo valor coincide con el de sistema,
  y añade `name_prefix: null → ""`.
- **`domain_dns_ips`:** no aplica todavía, porque la instancia no existe.

**Post, solo lectura.** La sesión caducó (`ExpiredToken`) durante la primera lectura posterior del state;
se repitió tras renovarla:
- el state sigue en serial 1, con una sola versión y 20/21 recursos, y solo el grupo está `tainted`;
- no hay `.tflock`; RDS y el snapshot final siguen ausentes;
- el parameter group está sin tocar: en `source=user` solo tiene los cuatro `log_*`;
- el SecureString sigue en versión 1.

### 28.5 Estado y propuesta DN-2 — sin ejecutar

**H-031-3-RECOVERY — DN-2 DRIFT REVIEW REQUIRED.** El plan cumple la forma esperada (un único reemplazo, un
único create, SSM `no-op` y el resto `no-op`), pero la guarda es fail-closed ante el drift y **no se adaptó**.

**Propuesta: refresh-only PLAN ONLY.**
- Se genera un plan refresh-only guardado desde el state actual, con una guarda exacta propia que admite solo esas cuatro direcciones:
  - los tres grupos, con `ingress`/`egress` iguales a las cinco reglas gestionadas;
  - el grupo `tainted`, con `name_prefix` y el `apply_method` de esos dos parámetros.
- Exige además cero cambios de recursos y salidas `no-op`.
- Si se autoriza su apply, se regenera el plan de recuperación, que debería quedar en 2/0/1 con `resource_drift = 0` y `RECOVERY_PLAN_OK`.

**Riesgo a vigilar.** Si tras reemplazar el grupo AWS sigue devolviendo `pending-reboot` para `rds.force_ssl` y
`ssl_min_protocol_version`, el plan de convergencia posterior al apply podría mostrar una actualización
recurrente del grupo. Se capturará y no se tolerará.

## 29. H-031-3-RECOVERY-DN2 — refresh-only PLAN ONLY, rechazado por las salidas (2026-10-05)

Autorización del usuario: **H-031-3-RECOVERY-DN2 — REFRESH-ONLY PLAN ONLY**, con el contrato exacto del
drift fijado antes de ver el plan. Prohíbe aplicar el refresh-only y el plan de recuperación, crear RDS,
reemplazar el parameter group y tocar AWS a mano.

### 29.1 Sesión, preflight y API

- **Sesión.** `aws login` se renovó a las 02:26:42 UTC y el runner arrancó a las 02:42:10, dentro de la ventana de unos 30 minutos.
- **Preflight** (el mismo de §28; su evidencia previa se copió aparte):
  - STS correcto;
  - state en serial 1, con **20 de 21** recursos: falta solo `aws_db_instance.this` y únicamente el parameter group está `tainted`;
  - no hay `.tflock`; RDS y el snapshot final siguen ausentes;
  - SecureString en versión 1;
  - lo que existe en AWS coincide con el state, ID por ID, sin recursos adicionales.
- **API real del parameter group.** `rds.force_ssl` vale **1** y `ssl_min_protocol_version` **TLSv1.2**, los valores aprobados. Ambos con `ApplyMethod = pending-reboot`, `Source = system` e `IsModifiable = true`.

### 29.2 Plan refresh-only

- **Contraseña.** Como en §28, la custodiada en SSM se usó solo en memoria y solo por `TF_VAR_contrasena_master`; `version_de_la_contrasena` sigue en 1.
- **Plan.** `terraform plan -refresh-only -detailed-exitcode` terminó con **exit 2**, y `terraform show` del binario lo declara *refresh-only plan*.
- **SHA-256:** del binario `13eb811955cefaee8556d5973337661db35d330ec365612e5cdaaef8d9a3edfc`; del JSON `68eebb1e9f3e4d02dcc889e2ac8fc670ea2aafe14412c38ea9f127cd80cf5d51`.

| Elemento | Resultado |
| --- | --- |
| `resource_changes` | **0**: ninguna acción de infraestructura |
| `resource_drift` | **4**, exactamente las del contrato (§28.4) |
| `deferred_changes` | **0** |
| Taint | El `prior_state` del plan conserva `aws_db_parameter_group.this` **`tainted`**: el refresh-only no lo limpia, y el reemplazo posterior sigue garantizado |
| **`output_changes`** | **6 cambian** (§29.3) |
| `DN2_SECRET_ABSENT` | **true**: se buscó en 5 buffers en memoria (salida del plan, `show` en texto y state) y en 19 720 archivos, sin ilegibles |

**Post, solo lectura:**
- el state remoto quedó intacto: misma huella, serial 1, 20/21 y el mismo taint;
- `.tflock` liberado; RDS ausente;
- el SecureString sigue en versión 1;
- el plan de recuperación `h0313r.tfplan` sigue intacto.

### 29.3 Guarda `check_plan_dn2.py` — `OUTPUTS`

Guarda **nueva y separada**: `check_plan.py` y `check_plan_recuperacion.py` no se tocaron. Sus 23 pruebas
(RED antes de implementarla y luego GREEN) cubren el caso positivo y los negativos pedidos: quinta
dirección, regla extra, CIDR abierto, cambio del valor TLS, `name_prefix` distinto, create, update y
delete, diferidos, import y move. Además: taint perdido, salida por omisión restaurada, otro
`apply_method` y salidas cambiadas.

El reflejo de cada grupo se deriva de las **cinco** reglas gestionadas aparte y de la prefix list del
endpoint. Las salidas se comprueban **al final**, a propósito.

**Contra el plan real, la guarda rechazó con `OUTPUTS`.** Como es el último control, todo lo anterior se
cumple:
- exactamente los 4 drift;
- el reflejo exacto de las 5 reglas, sin CIDR y sin salida por omisión;
- el parameter group con solo `name_prefix` y el `apply_method` de los dos parámetros, sin cambio de valor;
- el taint conservado;
- cero cambios y cero diferidos.

Lo confirmó un diagnóstico **en memoria** con las salidas neutralizadas en una copia. No se modificaron ni
la guarda ni los artefactos, y ese diagnóstico **no** es una aceptación.

Las salidas que cambian son las seis que dependen de la instancia, que no existe. El refresh-only las
reevalúa desde la configuración:

| Salida | Acción | Antes → después |
| --- | --- | --- |
| `arn_rds`, `endpoint_rds`, `id_de_recurso_rds` | `create` | ausente → desconocido |
| `identificador_rds` | `update` | `blog-prod-postgres` → desconocido |
| `nombre_de_base` | `update` | `personal_blog` → desconocido |
| `puerto_rds` | `update` | `5432` → desconocido |

Las tres últimas están en el state porque el apply fallido de H-031-3 guardó las salidas conocidas en el
plan. Aplicar este refresh-only escribiría en el state esas seis salidas, **además** de los cuatro drift.
El contrato lo prohíbe.

### 29.4 Estado — STOP, decisión del usuario

**H-031-3-RECOVERY-DN2: REFRESH PLAN REJECTED (`OUTPUTS`).** No hubo apply. El plan refresh-only queda
guardado en privado solo como evidencia. Opciones, ninguna ejecutada:
1. **Ampliar el contrato DN-2** con una excepción declarada y exacta para estas seis salidas, que dependen
   solo de la instancia y que el apply de recuperación recalculará; la guarda de recuperación ya las admite.
2. **No aplicar ningún refresh-only** y decidir DN-2 dentro del plan de recuperación, declarando
   exactamente esos cuatro drift en su guarda. Eso cambia una regla fail-closed y exige decisión explícita.
3. **Otra decisión** del usuario.

## 30. H-031-3-RECOVERY-DN2-OUTPUTS — alineación de la guarda DN-2 (2026-10-05)

Autorización del usuario: **H-031-3-RECOVERY-DN2-OUTPUTS — GUARD ALIGNMENT ONLY**. Acepta el diagnóstico de
§29 y amplía **exclusivamente** el contrato de `check_plan_dn2.py` para admitir las seis salidas
observadas. La razón: la instancia RDS todavía no existe y el refresh-only reevalúa las salidas que
dependen de ella. No autoriza ningún apply, ningún plan nuevo ni ningún cambio de infraestructura.
`check_plan.py` y `check_plan_recuperacion.py` no se tocaron.

### 30.1 Contrato ampliado

| Salida | `actions` | `before` | `after` | `after_unknown` | Sensible |
| --- | --- | --- | --- | --- | --- |
| `arn_rds`, `endpoint_rds`, `id_de_recurso_rds` | `["create"]` | `null`, y ausente del state previo | `null` | `true` | no |
| `identificador_rds` | `["update"]` | `"blog-prod-postgres"`, igual al del state previo | `null` | `true` | no |
| `nombre_de_base` | `["update"]` | `"personal_blog"`, igual al del state previo | `null` | `true` | no |
| `puerto_rds` | `["update"]` | `5432` (número), igual al del state previo | `null` | `true` | no |
| Las otras nueve (VPC, subredes, grupos, endpoint, prefix list, grupo de logs, parámetro master) | `["no-op"]` | `before == after` | — | no `true` | no |

Se exigen tipo y valor exactos. Las seis tienen que estar y con esa forma; una de ellas como `no-op`, una
séptima salida o cualquier otra acción se rechazan. El resto del contrato DN-2 de §29 no cambió.

### 30.2 Pruebas — RED → GREEN

- **Fixture.** El del plan válido pasa a llevar las seis transiciones exactas observadas.
- **Prueba existente ajustada.** `test_salida_que_cambia_rechazada` usaba `arn_rds=create` e `identificador_rds=update` como ejemplos de rechazo. Como el requisito cambió por decisión del usuario, ahora usa `update` y `create` respectivamente, que quedan fuera del contrato; su intención no cambió.
- **Pruebas nuevas (12).** Cubren:
  - el caso válido;
  - que falte una de las seis o aparezca como `no-op`;
  - una séptima salida;
  - `arn_rds=update` e `identificador_rds=create`;
  - un `before` incorrecto, en tipo o en valor;
  - un `after` conocido y `after_unknown=false`;
  - una salida sensible;
  - una salida de red que deja de ser `no-op`;
  - incoherencias con el state previo.
- **RED:** `ImportError`, porque `SALIDAS_RDS` no existía. **GREEN:** **35/35**, las 23 de §29 y las 12 nuevas.

### 30.3 Reevaluación del mismo plan y frescura

- **No se generó un plan nuevo.** El binario `13eb8119…fdc` y el JSON `68eebb1e…5d51` conservan exactamente su SHA-256.
- **Frescura del state, solo lectura, después de STS correcto:**
  - el state remoto sigue en serial 1, con 20/21 y solo el parameter group `tainted`;
  - el objeto del state tiene **una sola versión** y ningún *delete marker*: no se ha reescrito desde el apply parcial;
  - no hay `.tflock`, RDS sigue ausente y el SecureString sigue en versión 1.
- **Lineage.** Su comparación con la entrada `tfstate` del plan coincide (mismo lineage y serial 1). Una primera comparación usó por error `tfstate-prev`, que Terraform guarda sin lineage ni serial; el plan de recuperación tiene la misma forma, así que no indica ningún cambio.

**`check_plan_dn2.py` sobre `h0313r-dn2-plan.json`: `DN2_REFRESH_PLAN_OK`.**

| Elemento | Resultado |
| --- | --- |
| `resource_changes` | 0 |
| `resource_drift` | 4: SG `admin` (`egress`), SG `lambda` (`egress`), SG `rds` (`ingress`) y parameter group (`name_prefix`, `parameter`) |
| `deferred_changes` | 0 |
| Taint | Parameter group, conservado |
| Salidas excepcionales | Exactamente las 6 |
| Otras salidas | 9, todas `no-op` |
| `DN2_SECRET_ABSENT` | true (§29.2) |

**Estado: H-031-3 DN-2 REFRESH PLAN READY.** Sin apply.

## 31. H-031-3 DN-2 — refresh-only aplicado y nuevo plan de recuperación (2026-10-05)

Autorización del usuario: **H-031-3 DN-2 — APPLY EXACT REFRESH-ONLY PLAN**, solo el binario `13eb8119…fdc`,
y después un **nuevo** plan de recuperación **sin aplicarlo**. El runner privado es propio
(`tmp/h0313r/dn2_apply.py`) y no tiene fase de recovery apply. `aws login` se renovó a las 14:38 UTC y el
runner arrancó a las 14:46.

### 31.1 Frescura, guarda y apply del refresh-only

- **Frescura.**
  - STS correcto.
  - Plan y JSON con su SHA exacto.
  - La configuración del root y de los dos módulos, y el lock de providers, son idénticos a la instantanea guardada dentro del plan.
  - State en serial 1, con el mismo lineage y serial que la entrada `tfstate` del plan, 20/21 y el parameter group `tainted`; el objeto del state tiene una sola versión.
  - RDS ausente, SecureString en versión 1 y sin `.tflock`.
  - Lo que existe en AWS coincide con el state.
- **Guarda.** `check_plan_dn2.py` sobre el mismo JSON dio **`DN2_REFRESH_PLAN_OK`**: 0 cambios, 4 drift, 0 diferidos y exactamente las seis salidas de RDS de §30.
- **Apply.** `terraform apply -input=false -no-color <refresh plan>` dio **exit 0, `Apply complete! Resources: 0 added, 0 changed, 0 destroyed.`** La contraseña custodiada viajó solo en memoria y por `TF_VAR_contrasena_master`, porque Terraform exige la variable efímera al aplicar un plan guardado.

### 31.2 State reconciliado, sin mutación en AWS

| Comprobación | Resultado |
| --- | --- |
| Serial | **1 → 2**, mismo lineage |
| Recursos | 20/21; sigue faltando solo `aws_db_instance.this` |
| Taint | **Conservado**: `aws_db_parameter_group.this` sigue `tainted`, así que el reemplazo posterior sigue garantizado |
| Grupos | `admin`: 1 regla en `egress` y ninguna en `ingress`; `lambda`: 2 en `egress` y ninguna en `ingress`; `rds`: 2 en `ingress` y ninguna en `egress` |
| Parameter group | `name_prefix = ""`; `rds.force_ssl` y `ssl_min_protocol_version` con `pending-reboot` |
| Otros 16 recursos | Atributos idénticos a los de antes del apply |
| Salidas | Las seis de RDS quedan **nulas** en el state; las otras nueve, sin cambio |
| AWS | **Sin cambios**: reglas, grupos, tablas y rutas, endpoint, parámetros de usuario del grupo, SecureString (versión 1), RDS (ausente) y grupo de logs, comparados con la foto previa |
| `.tflock` | Liberado |

### 31.3 Nuevo plan de recuperación — sin apply

- **Plan.** Generado desde el state reconciliado, con la misma contraseña custodiada en memoria y `version_de_la_contrasena = 1`: **exit 2, `Plan: 2 to add, 0 to change, 1 to destroy.`**
- **SHA-256:** del binario `6875aa8de3da40d77ea6699542f0446aa0e9f5f9abf4870d7692afd6a690cece`; del JSON `d112095dea515ae241074082ecb012328084ac07a92cf274370b81f000afa5f4`.

| Recurso | Acción |
| --- | --- |
| `module.base_de_datos.aws_db_parameter_group.this` | **`["delete", "create"]`**, `replace_because_tainted`, con los **seis** parámetros y `apply_method = immediate` |
| `module.base_de_datos.aws_db_instance.this` | **`create`**: `us-east-2a`, `multi_az = false`, `publicly_accessible = false`, parameter group `blog-prod-postgres17`, `password_wo_version = 1` y el resto del contrato de §28.3 |
| `module.base_de_datos.aws_ssm_parameter.contrasena_master` | **`no-op`**, `before == after` |
| Los otros 18 | **`no-op`** |
| Salidas de RDS | `update` desde nulo: `arn_rds`, `endpoint_rds` e `id_de_recurso_rds` a desconocido; `identificador_rds`, `nombre_de_base` y `puerto_rds` a `blog-prod-postgres`, `personal_blog` y `5432` |

**Resultados:**
- `resource_drift = 0`; `deferred_changes = 0`.
- `check_plan_recuperacion.py`: **`RECOVERY_PLAN_OK`**.
- El state quedó intacto tras el plan, `.tflock` liberado y AWS sin cambios.
- **`SECRET_ABSENT = true`**: se buscó en 6 buffers en memoria (salidas del apply y del plan, y state) y en 20 676 archivos, sin ilegibles.

**Estado: H-031-3 DN-2 REFRESH APPLIED / RECOVERY PLAN READY.** Sin recovery apply: RDS no existe. Al
aplicar el plan de recuperación, el riesgo de §28.5 (un `pending-reboot` recurrente en dos parámetros) se
comprobará en la convergencia posterior.

## 32. H-031-3 — recovery apply fallido: restricción del plan gratuito de la cuenta (2026-10-05)

Autorización del usuario: **H-031-3 — RECOVERY APPLY EXACT SAVED PLAN**, solo el binario
`6875aa8de3da40d77ea6699542f0446aa0e9f5f9abf4870d7692afd6a690cece`. El runner privado es
`tmp/h0313r/rec_apply.py`. La sesión estaba recién renovada: arrancó a las 14:58 UTC.

### 32.1 Gates y apply

- **Frescura, toda en verde:**
  - STS correcto; plan y JSON con su SHA exacto;
  - configuración y lock idénticos a la instantanea del plan;
  - state en serial 2, igual al del plan, con 20/21 y el parameter group `tainted`;
  - RDS ausente, SecureString en versión 1 y sin `.tflock`.
- **Guarda:** `check_plan_recuperacion.py` dio **`RECOVERY_PLAN_OK`**, con drift 0 y diferidos 0.
- **Apply:** `terraform apply -input=false -no-color <plan>`, con la contraseña custodiada solo en memoria y `version_de_la_contrasena = 1`, terminó con **exit 1**.
  1. `aws_db_parameter_group.this`: *Destroying* y *Destruction complete*; luego *Creating* y *Creation complete*. **El reemplazo se completó.**
  2. `aws_db_instance.this`: *Creating*, y la API rechazó la llamada inicial:

```text
Error: creating RDS DB Instance (blog-prod-postgres): operation error RDS: CreateDBInstance,
https response error StatusCode: 400, api error FreeTierRestrictionError:
The specified backup retention period exceeds the maximum available to free tier customers.
To remove all limitations, upgrade your account plan.
```

### 32.2 Inspección de solo lectura

| Punto | Resultado |
| --- | --- |
| Lock | Liberado |
| State | Serial **3** (tres versiones del objeto), **20/21**, falta solo `aws_db_instance.this`, **sin recursos `tainted`** |
| Parameter group en el state | Los **seis** parámetros, `apply_method = immediate` |
| Parameter group en AWS | `source=user`: solo los cuatro `log_*`. `rds.force_ssl` (1), `ssl_min_protocol_version` (TLSv1.2) y `superuser_reserved_connections` (3) aparecen con **`Source = system`** y `ApplyMethod = pending-reboot` |
| RDS | **No existe** |
| Snapshot final | No existe |
| SecureString | Versión 1 |
| Salidas | `identificador_rds`, `nombre_de_base` y `puerto_rds` con valor, porque el apply fallido guardó las conocidas; `arn_rds`, `endpoint_rds` e `id_de_recurso_rds` siguen nulas |
| `PRODUCTION_SECRET_ABSENT` | **true**: se buscó en los buffers en memoria y en 21 153 archivos, sin ilegibles |
| Rotación de contraseña | **No hace falta**: ninguna instancia existe y el SecureString conserva el valor custodiado, que no se modificó |

**No se hizo:** ningún reintento, segundo plan, reparación ni destroy; ningún `untaint`, `state rm`,
`import` o `state mv`; ninguna acción manual en AWS.

### 32.3 Hallazgos

1. **Plan de cuenta.** La API declara que la cuenta tiene **restricciones de plan gratuito**: el periodo de
   retención de backups de D-22/D-23 (7 días) supera el máximo permitido. Las cuentas abiertas después del
   15 de julio de 2025 eligen entre un plan *Free* y uno *Paid*; pasar al *Paid* elimina las limitaciones
   y los créditos se siguen aplicando ([AWS — RDS free](https://aws.amazon.com/rds/free/)).
   - En esta sesión **no se comprobó** el tipo de plan de la cuenta ni el máximo exacto de retención:
     es una restricción de AWS real que Floci no emula.
2. **Representación del parameter group, ya confirmada (riesgo de §28.5).** Recién creado y con los seis
   parámetros enviados, AWS sigue reportando `rds.force_ssl` y `ssl_min_protocol_version` como **de
   sistema y `pending-reboot`**, porque su valor coincide con el de sistema. El siguiente plan normal
   detectará drift en el grupo y propondrá un *update* en sitio que AWS no conservará: una diferencia
   **recurrente**. Hace falta una decisión de diseño antes de volver a planificar.

### 32.4 Estado — RECOVERY APPLY FAILED / REVIEW REQUIRED

**Decisiones pendientes del usuario. Nada ejecutado.**
- **Retención de backups:**
  - **(a)** pasar la cuenta al plan *Paid*, que es una decisión de facturación de la cuenta; o
  - **(b)** cambiar D-22/D-23 a la retención que permita el plan gratuito, sacrificando PITR de 7 días.
  - Antes de decidir, un diagnóstico de solo lectura del plan de la cuenta y del límite exacto.
- **Parameter group:**
  - **(c)** retirar `rds.force_ssl` y `ssl_min_protocol_version` de los explícitos y verificar sus valores de sistema en `check_parametros.py`, como ya se hace con `superuser_reserved_connections`; o
  - **(d)** declararlos con `apply_method = pending-reboot`, igual que AWS los representa, lo que cambia la regla `dynamic → immediate` del preflight.

Después haría falta un plan de recuperación **nuevo**: create de RDS, el tratamiento elegido del grupo y
SSM `no-op`, con su guarda y la revisión de drift.

## 33. H-031-3-RECOVERY-2 — plan de cuenta y parameter group de cuatro parámetros (2026-10-05)

Autorización del usuario: **H-031-3-RECOVERY-2 — ACCOUNT DIAG + PARAMETER GROUP DESIGN FIX / PLAN ONLY**.
Acepta §32 y adopta la opción **(c)** para el parameter group. Prohíbe:
- aplicar nada, crear RDS y generar un plan de recuperación;
- cambiar el plan de facturación o pasar de `FREE` a `PAID`;
- cambiar `backup_retention_period`.

### 33.1 Plan de la cuenta, solo lectura

`aws freetier get-account-plan-state` (AWS CLI 2.37.1). Solo se registran estos campos; el Account ID que
devuelve la API no se imprime:

| Campo | Valor |
| --- | --- |
| `accountPlanType` | **`FREE`** |
| `accountPlanStatus` | **`ACTIVE`** |
| `accountPlanExpirationDate` | **2027-03-15T23:42:03Z** |
| `accountPlanRemainingCredits` | **120.0 USD** |

**Retención máxima del plan Free: `FREE_PLAN_RETENTION_MAX = UNKNOWN`.** Ni la Free Tier API ni la
documentación oficial publican el máximo de retención de backups de RDS para este plan.
- La guía de RDS admite de 0 a 35 días en general
  ([Backup retention period](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.BackupRetention.html)).
- La página «Choosing a plan» no menciona límites de retención
  ([AWS Billing — Choosing a plan](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html)).
- **No se probó por tanteo** ni se hizo ningún `CreateDBInstance` de prueba.

**Hecho relevante para la decisión, según esa misma página oficial:**
- El plan Free termina **a los seis meses o al agotar los créditos**, lo que ocurra antes.
- Al terminar, **la cuenta se cierra automáticamente** y se pierde el acceso a los recursos y datos. AWS
  conserva el contenido 90 días, plazo en el que se puede pasar al plan *Paid*.
- Al pasar al *Paid*, los créditos restantes se aplican a las facturas siguientes.

### 33.2 Parameter group — opción (c)

| Elemento | Cambio |
| --- | --- |
| Gestionados por Terraform | **Cuatro**: `log_connections = 1`, `log_disconnections = 1`, `log_min_duration_statement = 1000` y `log_statement = ddl`. Todos modificables, dinámicos, `immediate` |
| Invariantes de sistema, **no gestionadas** | `superuser_reserved_connections = 3` (`Source = system`, `IsModifiable = false`), `rds.force_ssl = 1` y `ssl_min_protocol_version = TLSv1.2` (ambos `Source = system`) |
| `check_parametros.py` | Antes de cada plan productivo exige esos tres valores con `Source = system`, y `IsModifiable = false` en `superuser_reserved_connections`. Si alguno vuelve al conjunto explícito, `PARAM_SYSTEM_MANAGED`; cualquier diferencia, STOP |
| `check_plan.py` / `check_plan_recuperacion.py` | `PARAMETROS` con los cuatro; un plan que vuelva a gestionar cualquiera de los tres se rechaza con `PARAMETERS`. La lógica de las guardas no cambió |
| Módulo, `terraform test`, fixture del laboratorio | Cuatro parámetros, con comentario. Sin `ignore_changes` |
| D-22/D-23 | Segunda corrección en `production-postgresql-rds-decisions.md`; anotaciones en `production-postgresql-rds.md` y `open-decisions.md` |

**TDD:**
- **RED de 18 fallos**, todos del requisito nuevo.
- **GREEN: 135/135** en las cuatro suites de las guardas.
- **Fixtures históricos explícitos:** las pruebas de las guardas ya consumidas (recuperación y DN-2) declaran el grupo histórico de siete parámetros de forma explícita, para no depender del conjunto vigente.
- **Regresiones nuevas.** Las tres invariantes:
  - quedan fuera de Terraform;
  - se verifican antes del plan;
  - cada una falla si cambia su valor (`rds.force_ssl ≠ 1`, `ssl_min_protocol_version ≠ TLSv1.2`, `superuser_reserved_connections ≠ 3`), si deja de ser de sistema o si falta del catálogo;
  - `superuser_reserved_connections` falla además si pasa a ser modificable;
  - y vuelven a fallar si reaparecen en el grupo de Terraform, tanto en el preflight como en el plan.

**Verificación real, solo lectura:**
- **Catálogo:** 5 páginas crudas, 437 parámetros. `check_parametros`: **`PARAMETERS_OK`**.
- **Grupo vivo `blog-prod-postgres17`:**
  - las tres invariantes tienen el valor esperado con `Source = system`;
  - sus parámetros `source=user` son **exactamente los cuatro** explícitos.

**Floci** aceptó los tres parámetros sin reproducir ni el `IsModifiable = false` ni la representación de
sistema (matriz de paridad).

### 33.3 Estado AWS, sin mutaciones

- STS correcto.
- State en serial 3, 20/21; falta solo `aws_db_instance.this` y no hay ningún recurso `tainted`.
- RDS y el snapshot final siguen ausentes.
- El parameter group existe y el SecureString sigue en versión 1. No hay `.tflock`.

Solo hubo lecturas: STS, `freetier get-account-plan-state` y `describe-*`. **No se generó ningún plan.**

### 33.4 Estado — RECOVERY-2 DECISION READY

**H-031-3 RECOVERY-2 DECISION READY.** Decisión pendiente del usuario:
- **A.** Conservar el plan Free y adaptar la retención, con su máximo **desconocido**.
- **B.** Pasar voluntariamente al plan *Paid* y conservar el PITR de 7 días.

Ninguna se tomó ni se ejecutó. Después hará falta un plan de recuperación nuevo con su propia guarda: el
grupo ya no está `tainted`, así que el siguiente plan tendrá otra forma (actualización del grupo y create
de RDS).

## 34. H-031-3-RECOVERY-3-FREE — retención temporal de 1 día y plan de recuperación (2026-10-05)

Autorización del usuario: **H-031-3-RECOVERY-3-FREE — RETENTION 1 DAY / PLAN ONLY**.
- La cuenta **se mantiene en FREE**: ni *Paid* ni `upgrade-account-plan`.
- `backup_retention_period = 1` como **excepción temporal**; el objetivo sigue siendo 7. `0` está prohibido.
- Plan nuevo, **sin apply**.

### 34.1 Modelado de la excepción, sin deuda oculta

| Archivo | Cambio |
| --- | --- |
| `terraform-datos/variables.tf` | Se reutiliza `dias_de_retencion_de_backups`: default **7** (objetivo, plan PAID) y validación **`{1, 7}`**, cuyo mensaje explica que 1 es la excepción temporal del plan FREE y que 0 nunca se admite |
| `entornos/produccion/produccion.tfvars.example` | `dias_de_retencion_de_backups = 1` explícito, con comentario: excepción temporal, no es el máximo del plan FREE, se borra al pasar a PAID, snapshot manual antes de cambios destructivos. El tfvars privado lleva el mismo valor; su versión anterior se conserva en privado |
| `scripts/terraform_datos/check_plan.py` | `RETENCION_OBJETIVO = 7` y `RETENCION_PLAN_FREE = 1`; la guarda del primer despliegue sigue exigiendo 7 |
| `terraform-datos/tests/datos.tftest.hcl` | Pruebas nuevas: 1 se acepta; 3 y 35 se rechazan; el rechazo de 0 ya existía |
| D-10/D-22 y runbook | Excepción temporal en D-10, anotaciones en la validación y el resumen, y `deployment-recovery.md` §8 con el *snapshot* manual antes de migraciones o cambios destructivos, sin autorizarlo ahora ni automatizarlo |

**`terraform test` de datos:** RED (3 aceptado por la validación anterior) → GREEN **30/30**.

### 34.2 Preflight, solo lectura

- Plan de cuenta **`FREE` / `ACTIVE`**, expira 2027-03-15, 120 USD; STS correcto.
- State en serial 3, 20/21; falta solo `aws_db_instance.this`, sin taint y sin `.tflock`.
- RDS y el snapshot final siguen ausentes; parameter group existente; SecureString en versión 1.
- AWS coincide con el state ID por ID: VPC, subredes, tablas, grupos, reglas, endpoint, subnet group, parameter group y grupo de logs.
- Mapeo `use2-az1 → us-east-2a` y `use2-az2 → us-east-2b`, ambas `available`.
- Orderability **2/2 PASS** (16:14:22 y 16:14:53 UTC).
- `check_parametros`: **`PARAMETERS_OK`**, con los cuatro explícitos y las tres invariantes de sistema verificadas en el grupo vivo.

### 34.3 Plan nuevo — sin apply

- **Contraseña.** La custodiada en SSM se usó solo en memoria y solo por `TF_VAR_contrasena_master`; `version_de_la_contrasena = 1`, sin rotación.
- **Plan.** **exit 2 — `Plan: 1 to add, 1 to change, 0 to destroy.`**
- **SHA-256:** del binario `ab0abb94fefd9838600361133959737f8058a239967dd0988f0038b580ca4809`; del JSON `403151ca5fafa3bf5eaf84b374faaedbcf4d718d86836eb070fa6b44efa65ae5`.

| Recurso | Acción |
| --- | --- |
| `module.base_de_datos.aws_db_instance.this` | **`create`** |
| `module.base_de_datos.aws_db_parameter_group.this` | **`update` en sitio**, sin `action_reason` de reemplazo. Solo cambia `parameter`: de los cuatro explícitos más `rds.force_ssl=1` y `ssl_min_protocol_version=TLSv1.2` (`pending-reboot`), a **exactamente los cuatro** |
| SecureString | `no-op`, `before == after` |
| Red y resto, 18 | `no-op` |
| Salidas | `update` de `arn_rds`, `endpoint_rds` e `id_de_recurso_rds`; las demás, `no-op` |

**Valores del create de RDS:**
- **Motor y capacidad:** PostgreSQL **17.11**, `db.t4g.micro`, gp3 de **20 GiB** con máximo **50**, cifrada.
- **Ubicación y red:** **Single-AZ** en `us-east-2a`, `publicly_accessible = false` y solo el `sg-rds` del state.
- **Protección:** `deletion_protection = true` y snapshot final `blog-prod-postgres-final`.
- **Backups:** **`backup_retention_period = 1`**, ventana `07:00-07:30`.
- **Logs y certificado:** logs `postgresql`, CA `rds-ca-rsa2048-g1`, Extended Support deshabilitado.
- **Grupos:** subnet group `blog-prod-postgres` y parameter group `blog-prod-postgres17`.
- **Base y credenciales:** base `personal_blog`, usuario `blogadmin`, `password_wo_version = 1`; ni `password` ni `password_wo` aparecen en el plan.

Tras el plan, el state quedó intacto y el `.tflock` liberado. **`PRODUCTION_SECRET_ABSENT = true`**: se buscó
en 3 buffers y 22 023 archivos, sin ilegibles.

**Drift: `resource_drift = 1`; `deferred_changes = 0`.**

| Dirección | Transición del refresh |
| --- | --- |
| `module.base_de_datos.aws_db_parameter_group.this` | `parameter`: `rds.force_ssl` y `ssl_min_protocol_version` pasan de `apply_method = immediate` a **`pending-reboot`**, con los **mismos valores** (1 y TLSv1.2). No cambia ningún otro atributo |

El state conserva esos dos nombres porque el apply de §32 creó el grupo con los seis de entonces. El refresh
los lee con la representación de sistema de AWS, y **el mismo plan los saca del conjunto**: el `update` deja
los cuatro. **Que no sea recurrente es una hipótesis y no se da por demostrada**: solo la probaría el plan de
convergencia posterior a un apply.

### 34.4 Guarda `check_plan_recuperacion_free.py` — `DRIFT_OR_DEFERRED`

Guarda **nueva y separada**, escrita para la forma real y fail-closed. Sus **23** pruebas pasaron de RED a
GREEN y rechazan:
- una retención distinta de 1, en la instancia o en la variable;
- un destroy o un replace del grupo;
- un grupo que vuelva a gestionar un parámetro de sistema o pierda uno explícito;
- otra transición u otro atributo del grupo;
- un cambio en SSM o en la red;
- IAM, NAT o IGW;
- un taint previo, un import o un move;
- secretos en el plan o en las variables;
- drift o diferidos.

El drift y los diferidos se comprueban **al final**. Contra el plan real la guarda rechazó con
**`DRIFT_OR_DEFERRED`**, así que todo lo anterior cumple: retención 1, create de RDS con su contrato, `update`
en sitio exacto del grupo, cero destroy y cero replace, SSM y red `no-op`, y ningún recurso ajeno.

### 34.5 Estado — RECOVERY-3-FREE DRIFT REVIEW REQUIRED

**No hubo apply. AWS sin mutaciones**: solo lecturas y el plan, que no escribió el state. Opciones para el
usuario, ninguna ejecutada:
1. **Excepción declarada y exacta** en `check_plan_recuperacion_free.py` para esta única transición de
   representación: la misma dirección, los mismos dos parámetros, los mismos valores e `immediate` a
   `pending-reboot`. Se aplicaría este mismo plan, y el plan de convergencia posterior demostraría que no se
   repite; si se repitiera, STOP.
2. **Refresh-only previo al estilo DN-2**, con su guarda: guardar la representación y regenerar el plan con
   drift 0. Son dos checkpoints AWS más sin cambio material.

## 35. H-031-3-RECOVERY-3-FREE-DRIFT — excepción exacta de drift en la guarda (2026-10-05)

Autorización del usuario: **H-031-3-RECOVERY-3-FREE-DRIFT — GUARD ALIGNMENT ONLY**. Admite una excepción
**exclusiva y exacta** en `check_plan_recuperacion_free.py` para el único `resource_drift` observado en §34.
No autoriza ninguna tolerancia genérica de drift, ningún plan nuevo, refresh-only ni apply.

### 35.1 Excepción admitida

| Condición | Exigida |
| --- | --- |
| `resource_drift` | **Exactamente 1** entrada. Si falta o hay más, `DRIFT_EXCEPTION` |
| Dirección, tipo y acción | `module.base_de_datos.aws_db_parameter_group.this`, `aws_db_parameter_group`, `["update"]`, sin import, move ni valores desconocidos |
| Atributos | Solo `parameter` |
| Parámetros | Los mismos seis nombres antes y después. Solo cambian `rds.force_ssl` (`"1"`) y `ssl_min_protocol_version` (`"TLSv1.2"`), y solo de `immediate` a `pending-reboot`, **sin cambio de valor** |
| Coherencia | El `after` del drift es el state refrescado del plan: el `before` del cambio del grupo y el `prior_state` |
| `deferred_changes` | 0 (`DRIFT_OR_DEFERRED`) |

Justificación, según el usuario: es una **representación histórica y transitoria**. El state conserva
ambos parámetros por el apply de §32, AWS los devuelve como `Source = system` con `pending-reboot`, y el
mismo plan los retira del conjunto gestionado. **No demuestra que no sea recurrente**: después del apply
será obligatorio demostrar con un plan de convergencia que `resource_drift` vuelve a 0.

Ninguna otra validación de la guarda se debilitó. Sigue exigiendo:
- retención 1 y create únicamente de RDS;
- update en sitio solo del grupo, sin destroy ni replace;
- SSM, red y los otros 19 recursos en `no-op`;
- sin IAM, NAT ni IGW, sin import, move ni taint, y sin secretos.

### 35.2 TDD

- **RED:** 19 fallos, todos del requisito nuevo.
- **GREEN:** **36/36**, con las 23 previas y 13 nuevas.
- **Pruebas previas ajustadas porque el requisito cambió:**
  - el caso válido pasa a incluir el drift exacto;
  - «el drift observado se rechaza» pasa a «sin el drift exacto se rechaza», porque ahora se exige exactamente 1.
- **Pruebas nuevas.** El drift exacto pasa. Fallan:
  - otra dirección, en vez del grupo o además de él;
  - otro atributo del grupo;
  - un cambio de valor en `rds.force_ssl` o en `ssl_min_protocol_version`;
  - que falte uno de los dos;
  - un tercer parámetro;
  - `pending-reboot` → `immediate`;
  - otra acción;
  - diferidos;
  - import, move o valores desconocidos;
  - incoherencias con el plan.
- **Fixture corregido:** ponía en `prior_state` el state sin refrescar. El JSON real demuestra que
  `prior_state` es el state refrescado, igual al `after` del drift y al `before` del cambio.

### 35.3 Reevaluación del mismo plan — sin plan nuevo

- **Frescura, solo lectura, en verde:**
  - STS correcto; cuenta en **`FREE` / `ACTIVE`**;
  - state en serial 3, con el mismo lineage y serial que la entrada `tfstate` del plan; 20/21, falta solo `aws_db_instance.this` y no hay taint;
  - RDS y el snapshot final ausentes, SecureString en versión 1 y sin `.tflock`.
- **SHA-256 exactos:** del plan `ab0abb94fefd9838600361133959737f8058a239967dd0988f0038b580ca4809`; del JSON `403151ca5fafa3bf5eaf84b374faaedbcf4d718d86836eb070fa6b44efa65ae5`.

**`check_plan_recuperacion_free.py`: `RECOVERY_3_FREE_PLAN_OK`.**
- **Acciones:** 1 add / 1 change / 0 destroy, sin ningún replace.
  - create: `aws_db_instance.this`, con `backup_retention_period = 1`;
  - update en sitio: el parameter group;
  - 19 `no-op`, entre ellos SSM y toda la red.
- **Drift:** el único admitido es el del parameter group (`rds.force_ssl` y `ssl_min_protocol_version`); `deferred_changes = 0`.
- **Secreto:** `PRODUCTION_SECRET_ABSENT = true`, de §34; el plan no ha cambiado.

**Estado: H-031-3 RECOVERY-3-FREE PLAN READY.** Sin apply. Al aplicarlo, la convergencia posterior deberá
dar **0/0/0 con `resource_drift = 0`**; si la representación de esos dos parámetros reaparece, STOP.

## 36. H-031-3-RECOVERY-3-FREE — apply interrumpido por credenciales caducadas (2026-10-05)

Autorización del usuario: **H-031-3-RECOVERY-3-FREE — APPLY EXACT SAVED PLAN** (`ab0abb94…4809`). El runner
privado es `tmp/h0313r/rec3_apply.py`. La sesión se había renovado a las 17:06:44 UTC y el runner arrancó a
las 17:08:16.

### 36.1 Gates y apply

- **Frescura, toda en verde:**
  - STS correcto; cuenta en `FREE` / `ACTIVE`;
  - SHA exactos; configuración idéntica a la instantanea del plan;
  - state en serial 3, con el mismo lineage que el plan; 20/21 y sin taint;
  - RDS y el snapshot final ausentes, SecureString en versión 1 y sin `.tflock`.
- **Guarda:** **`RECOVERY_3_FREE_PLAN_OK`**, 1/1/0, sin ningún replace.
- **Apply:** `terraform apply -input=false -no-color <plan>` terminó con **exit 1**.
  1. `aws_db_parameter_group.this`: *Modifying* y *Modifications complete after 1s*.
  2. `aws_db_instance.this`: *Creating*, y *Still creating…* durante 2m10s.
  3. `ExpiredToken` en `DescribeDBInstances`: Terraform no pudo seguir esperando.
  4. `ExpiredToken` en el `PutObject` del state: **«Failed to persist state to backend»**. Terraform escribió el state en local, en `terraform-datos/errored.tfstate`.
  5. `ExpiredToken` al liberar el lock: **«Error releasing the state lock»**.

### 36.2 Inspección de solo lectura, tras renovar la sesión

| Punto | Resultado |
| --- | --- |
| State remoto | **Sin cambios**: serial 3 (tres versiones, la última de las 14:59 UTC), 20/21, sin `aws_db_instance.this`, sin taint; el grupo conserva los seis parámetros del apply de §32 |
| `errored.tfstate` (local, ignorado por Git, no tocado) | Serial **5**, **mismo lineage** que el remoto, **21/21**; `aws_db_instance.this` **`tainted`**; el grupo con los cuatro parámetros |
| Lock | **`.tflock` PRESENTE**: `OperationTypeApply`, creado a las 17:08:56 UTC por este apply y no liberado |
| RDS en AWS | **EXISTE y está `available`**, creada a las 17:12:57 UTC. 17.11, `db.t4g.micro`, `us-east-2a`, Single-AZ, no pública, cifrada, `deletion_protection = true`, **retención 1**, grupo de seguridad activo, parameter group `blog-prod-postgres17` `in-sync`, sin modificaciones pendientes |
| Snapshot final | Ausente |
| Parameter group en AWS | `source=user`: exactamente los cuatro explícitos con sus valores |
| SecureString | Versión 1 |
| Rotación de contraseña | **No hace falta**: la instancia se creó con el valor custodiado en el SecureString, que no cambió |
| `PRODUCTION_SECRET_ABSENT` | **true**: el valor no aparece en el log del apply, en `errored.tfstate` ni en ningún archivo del directorio privado o del checkout |

**No se hizo:** ningún reintento, plan nuevo ni refresh-only; ni `state push`, `force-unlock`, `untaint`,
`state rm` o `import`; ningún destroy ni cambio manual en AWS, ningún paso a *Paid* y ninguna otra retención.

**Causa de la caducidad: no determinada.** El perfil usa `login_session` directamente, sin asumir rol. El
token de la CLI en caché declaraba caducar a las 17:21:44, después del fallo. Antes de otra operación larga
de Terraform hay que validar cómo obtiene y renueva las credenciales de `login_session`.

### 36.3 Estado — RECOVERY-3-FREE APPLY FAILED / REVIEW REQUIRED

La instancia productiva **existe y es sana**, pero el state remoto no la registra. Como existe, consume
créditos del plan FREE. Recuperación propuesta, sin ejecutar; cada paso exige autorización explícita:
1. **`terraform force-unlock <ID>`** del lock que dejó este apply. El ID está en el log privado.
2. **`terraform state push terraform-datos/errored.tfstate`**: mismo lineage y serial mayor, así que
   Terraform registra lo que realmente creó.
3. **Taint de una instancia sana.** Con `deletion_protection` activo y la instancia `available`, conservarlo
   haría que el siguiente plan propusiera reemplazar la base productiva. La opción coherente es un `untaint`
   tras un readback completo en verde.
4. Después: readback completo, `SSM_PASSWORD_MATCH`, plan de convergencia 0/0/0 con `resource_drift = 0`, y
   gates.

## 37. H-031-3-RECOVERY-STATE — lock liberado y state restaurado; untaint retenido (2026-10-05)

Autorización del usuario: **H-031-3-RECOVERY-STATE — RESTORE REMOTE STATE + UNTAINT + CONVERGENCE**.
Recuperación **solo del state**; ningún cambio deliberado de infraestructura. El runner privado es
`tmp/h0313r/state_rec.py`. La sesión se había renovado a las 18:05:50 UTC.

### 37.1 Backup, comparación y readback previo

- **Primer arranque: STOP antes de mutar nada.** El control propio «`state pull` = objeto S3» falló porque
  Terraform serializa `check_results` sin orden fijo: mismos 20 elementos, otro orden. Se corrigió el control
  para comparar `check_results` sin tener en cuenta el orden; no se relajó nada más.
- **Backups privados** (fuera del checkout): el objeto S3 del state, el `state pull`, `errored.tfstate` y el
  `.tflock`, con su SHA-256. El contenido no se imprimió.
- **Remoto:** serial 3, 20/21, falta solo `aws_db_instance.this`, sin taint.
- **`errored.tfstate`:** serial 5, 21/21, mismo lineage, solo la instancia `tainted`.
- **Comparación dirección por dirección:** solo las diferencias permitidas.
  - **A:** la instancia, que solo está en `errored`.
  - **B:** el parameter group, con 6 parámetros históricos frente a los 4 explícitos.
  - Las otras 19 direcciones, el data source y las salidas son idénticos. Solo cambian los metadatos de escritura (`check_results`).
- **Readback previo:** **PASS** en RDS, el parameter group (exactamente cuatro de usuario), las tres
  invariantes y el SecureString en versión 1.
- **Lock:** `OperationTypeApply`, Terraform 1.16.2, creado a las 17:08:56 UTC, sin ningún `terraform.exe`
  activo. El único proceso relacionado era el servidor de lenguaje del editor.

### 37.2 Mutaciones del state

| Paso | Resultado |
| --- | --- |
| `terraform force-unlock -force <ID del lock real>` | exit 0; `.tflock` ausente |
| `terraform state push errored.tfstate`, **sin `-force`** | exit 0: mismo lineage y serial mayor |
| `state pull` posterior | Serial 6, 21/21, mismo lineage, solo la instancia `tainted`, grupo con cuatro parámetros, **equivalente** a `errored.tfstate`, sin `.tflock` |

### 37.3 Readback completo antes del untaint — 39/40: untaint RETENIDO

Todo lo que se lee de AWS está en verde:
- **RDS:** `available`, 17.11, `db.t4g.micro`, gp3 de 20 GiB con máximo 50, Single-AZ en `us-east-2a`, no
  pública, cifrada con `aws/rds`, `deletion_protection`, retención 1, ventana `07:00-07:30`, logs `postgresql`,
  CA aprobada y Extended Support deshabilitado.
- **Conexión y grupos:** `personal_blog` / `blogadmin`, endpoint en el puerto 5432, solo `sg-rds`, subnet group
  con las dos subredes, parameter group `in-sync` y sin modificaciones pendientes.
- **Parameter group:** exactamente cuatro parámetros de usuario y las tres invariantes de sistema.
- **Red:** intacta; la única ENI de la VPC lleva solo `sg-rds`.
- **State:** el snapshot final está configurado, sin `password` ni `password_wo`.
- **SecureString:** versión 1.

**El único FAIL: «state = AWS (`DbiResourceId`)».** El registro de la instancia en el state está
**incompleto**. Terraform perdió las credenciales justo después de `CreateDBInstance` y antes de la lectura
posterior a la creación, así que `errored.tfstate` guardó la instancia con **47 atributos calculados vacíos**
(`resource_id`, `arn`, `endpoint`, `address`, `status`, `kms_key_id`, `engine_version_actual`…). El
`identifier` sí coincide con AWS.

Según la regla de la autorización, **la instancia queda `tainted`**: no se hizo `untaint` ni plan de
convergencia.

| Punto | Resultado |
| --- | --- |
| `PASSWORD_CUSTODY_CHAIN_PASS` | No se evaluó: el runner se detuvo antes. Los hechos que la sostienen siguen en pie: SecureString en versión 1, sin rotación, e instancia creada durante el apply que recibió su valor |
| `PRODUCTION_SECRET_ABSENT` | **true**: se buscó en los states leídos en memoria y en 23 405 archivos, `errored.tfstate` y los backups incluidos |
| AWS | **Sin mutaciones**: solo el `.tflock` del propio apply fallido y el objeto state, ambos del backend |

### 37.4 Estado — revisión requerida

El state está **recuperado**, con el lock liberado y 21/21. La instancia sigue `tainted`, con un registro
incompleto. Propuesta, sin ejecutar:
1. **Plan refresh-only con su propia guarda exacta**, sin aplicar. Solo puede **completar los atributos
   calculados vacíos** de `aws_db_instance.this` con los valores que ya da el readback, conservar el taint y
   dejar todo lo demás sin drift.
2. Si se autoriza su apply: readback completo con **40/40**, `untaint` exacto, plan de convergencia (0/0/0, drift
   0, diferidos 0) y gates.
3. Hay que esperar `output_changes` en `arn_rds`, `endpoint_rds` e `id_de_recurso_rds`: siguen nulos en el state
   y solo los registra un apply.

## 38. H-031-3-RECOVERY-STATE-REFRESH — plan refresh-only de la instancia tainted (2026-10-05)

Autorización del usuario: **H-031-3-RECOVERY-STATE-REFRESH — REFRESH-ONLY PLAN ONLY**. El objetivo es completar
en el state el registro de `aws_db_instance.this` que el apply de §36 dejó incompleto, sin tocar la
infraestructura. Prohíbe el apply y el `untaint`. El runner privado es `tmp/h0313r/refresh_inst.py`; la sesión
se había renovado a las 19:20 UTC.

### 38.1 Preflight y foto

- **Cuenta y state:** STS correcto; cuenta en `FREE` / `ACTIVE`. State remoto en serial 6, 21/21, solo la
  instancia `tainted`, grupo con cuatro parámetros y sin `.tflock`. Backup privado del state con su SHA-256.
- **AWS:** RDS `available` con la identidad y la configuración esperadas (17.11, `db.t4g.micro`, gp3 de 20 GiB
  con máximo 50, Single-AZ en `us-east-2a`, privada, cifrada, `deletion_protection`, retención 1 y solo
  `sg-rds`). Parameter group `in-sync`, sin modificaciones pendientes y SecureString en versión 1.
- **Atributos vacíos o nulos de la instancia en el state, recalculados: 47.** Entre ellos `resource_id`, `arn`,
  `address`, `endpoint`, `hosted_zone_id`, `status`, `latest_restorable_time`, `kms_key_id` y
  `engine_version_actual`; el resto son opcionales sin valor.

### 38.2 Plan refresh-only

- **Contraseña.** La custodiada se usó solo en memoria y solo por `TF_VAR_contrasena_master`, porque Terraform
  la exige para evaluar la configuración.
- **Plan.** `terraform plan -refresh-only -input=false -no-color -lock=true -lock-timeout=30s
  -var-file=<privado> -out=<privado>` terminó con **exit 2**, y `terraform show` lo declara *refresh-only plan*.
- **SHA-256:** del binario `bd79612754b5f507a7ff0933fcaba28f5b67f8246c66a8b03962d7d8d972d228`; del JSON
  `94efaeaed36eb990ddc5000ef29385942452fc48a1c5a08bdbaeb0edf94384e2`.

| Elemento | Resultado |
| --- | --- |
| `resource_changes` | **0**: ninguna mutación de infraestructura |
| `resource_drift` | **1**: solo `module.base_de_datos.aws_db_instance.this`, `update` |
| `deferred_changes` | 0 |
| Parameter group, red y SSM | Sin drift |
| Salidas | `arn_rds`, `endpoint_rds` e `id_de_recurso_rds` pasan de `null` al valor real de AWS; `identificador_rds`, `nombre_de_base` y `puerto_rds` se conservan; las demás, `no-op` |

**Atributos del drift: exactamente 36.**
- **18 atributos calculados que pasan de `null` al valor de `describe-db-instances` de la misma instancia**:
  `resource_id`, `arn`, `address`, `endpoint`, `hosted_zone_id`, `status` (`available`), `kms_key_id`,
  `engine_version_actual`, `license_model`, `option_group_name`, `iops`, `storage_throughput`,
  `performance_insights_retention_period`, `database_insights_mode`, `backup_target`,
  `latest_restorable_time`, `customer_owned_ip_enabled` y `upgrade_rollout_order`. Todos coinciden con AWS.
- **18 normalizaciones de forma**, de `null` a `""` o `[]`, como `domain_dns_ips` (la ya conocida del SDKv2).
- **Identidad estable:** identifier, base, usuario, motor y versión, clase, retención, AZ, subnet group,
  parameter group, solo `sg-rds`, almacenamiento, protección, snapshot final, `password_wo_version`, logs,
  Extended Support y puerto no cambian.

**Taint, demostrado.**
- El estado refrescado que guarda el binario (su entrada `tfstate`) —que es lo que un refresh-only apply
  persiste— lleva `aws_db_instance.this` como `tainted`. También el `prior_state` del JSON.
- El plan no modificó el state remoto.
- **El refresh-only apply conservaría el taint**: la recuperación no se convierte en una autorización de
  reemplazo.

### 38.3 Guarda `check_plan_refresh_instancia.py` — `INSTANCE_REFRESH_PLAN_OK`

**Guarda nueva y separada**, fail-closed. Construida sobre la forma real y contrastada contra
`describe-db-instances`, que recibe como segunda entrada:
- contrato cerrado de 36 atributos, sin aceptar «cualquier atributo calculado»;
- identidad igual al contrato y a AWS;
- taint solo en la instancia;
- parameter group con cuatro parámetros;
- coherencia entre el drift y el `prior_state`;
- salidas exactas;
- ningún secreto.

**TDD:**
- **RED:** el módulo no existía. **GREEN:** **21/21**.
- La prueba de un `latest_restorable_time` ilegible destapó que el parseo devolvía otro error en lugar de
  `DRIFT_VALUE`. Se corrigió la guarda, no la prueba.
- **Casos que fallan:**
  - segundo drift u otra dirección;
  - identidad distinta, en el state o en AWS: identifier, motor, versión, AZ, retención, SG, parameter group,
    subnet group, clase, usuario o base;
  - un atributo conocido que cambia, o un calculado no contratado;
  - create, update, delete o replace;
  - salida extra o salida con un valor distinto del de AWS;
  - diferidos;
  - secretos;
  - un valor completado distinto de AWS, o que ya tenía valor;
  - un estado que no es `available`;
  - una forma distinta;
  - taint perdido o trasladado;
  - incoherencias con el `prior_state`.

**Contra el plan real: `INSTANCE_REFRESH_PLAN_OK`.**

| Punto | Resultado |
| --- | --- |
| `PRODUCTION_SECRET_ABSENT` | **true**: se buscó en 6 buffers y 23 783 archivos |
| Post del plan | State intacto (serial 6, 21/21, instancia `tainted`), `.tflock` liberado, RDS `available` y SecureString en versión 1 |

**Estado: H-031-3 TAINTED INSTANCE REFRESH PLAN READY.** Sin apply ni `untaint`.

## 39. H-031-3-RECOVERY-STATE-REFRESH APPLY — STOP de frescura antes del apply (2026-10-05)

Autorización del usuario: **APPLY EXACT REFRESH + READBACK + UNTAINT + CONVERGENCE**, con una condición previa:
volver a ejecutar `check_plan_refresh_instancia.py` contra un `describe-db-instances` **fresco** y obtener
`INSTANCE_REFRESH_PLAN_OK`; si cualquier condición ha cambiado, STOP.

### 39.1 Resultado

- **Previo:** STS correcto, con la sesión renovada a las 20:09 UTC. Plan `bd796127…d228` y JSON `94efaeae…84e2` con
  su SHA exacto.
- **Describe fresco** (guardado en privado): respecto al del momento del plan, **solo cambió
  `LatestRestorableTime`**, de 19:16:49 a 20:06:50 UTC. AWS lo hace avanzar cada pocos minutos mientras la
  instancia tenga backups automáticos.
- **Guarda contra el describe fresco: rechazo con `DRIFT_VALUE`.** El contrato exige que el
  `latest_restorable_time` refrescado en el plan sea **igual** al de AWS.
- **Diagnóstico en memoria**, sin modificar la guarda ni los artefactos y sin valor de aceptación: con el
  describe fresco y solo `LatestRestorableTime` devuelto a su valor del momento del plan, **todo lo demás
  cumple**.
- **STOP:** ningún apply, readback, untaint ni plan de convergencia. El state sigue en serial 6, 21/21, con la
  instancia `tainted`. AWS sin cambios.

### 39.2 Hallazgo y consecuencia

`latest_restorable_time` es un **atributo que se mueve solo**. Ninguna comparación de igualdad con un describe
posterior puede pasar, salvo que plan, guarda y apply ocurran dentro de la misma ventana de unos minutos. La
misma propiedad afectará al **plan de convergencia**: es probable que cualquier plan normal posterior muestre
`resource_drift` en `aws_db_instance.this` por ese atributo. Es una hipótesis todavía no observada en un plan
normal con el registro completo.

### 39.3 Opciones, ninguna ejecutada

1. **Contrato de atributo móvil, en la guarda refresh y en la convergencia.** Para `latest_restorable_time`, y
   solo para él, exigir un instante válido, que no sea posterior al de AWS fresco y que esté dentro de la
   ventana de retención (1 día). El resto, igualdad exacta. En la convergencia, admitir como único drift ese
   atributo de esa dirección, avanzando, sin ningún cambio de recurso.
2. **Plan, guarda y apply en una misma ejecución de pocos minutos.** Exigiría autorizar el apply de un plan que
   solo revisaría la guarda.
3. **Otra decisión del usuario.**

## 40. H-031-3-MOVING-ATTRIBUTE — contrato del atributo móvil y criterio de convergencia (2026-10-05)

Autorización del usuario: **H-031-3-MOVING-ATTRIBUTE — GUARD ALIGNMENT ONLY**. `latest_restorable_time` se
clasifica como **atributo móvil calculado por AWS**: no es configuración gestionable. No hay `ignore_changes` ni
tolerancia genérica de drift. Sin apply, untaint, plan nuevo ni cambios en AWS.

### 40.1 Contrato móvil en `check_plan_refresh_instancia.py`

Solo cambia el tratamiento de `latest_restorable_time`. Con `instante_movil`, compartido con la guarda de
convergencia, se exige:
- el instante del plan y el de AWS fresco, ambos ISO-8601 válidos, con zona horaria y no nulos;
- **plan ≤ AWS fresco**;
- una diferencia **de 0 a 24 h**, porque la retención productiva es de 1 día;
- **ninguno en el futuro** respecto al reloj. Sin tolerancia: el proyecto no tiene ninguna convención de *clock
  skew* y no se inventa una.

Los otros 17 valores, las 18 formas y la identidad siguen exigiendo **igualdad exacta** con el describe fresco. El
código del fallo es `MOVING_ATTRIBUTE`.

### 40.2 Criterio de convergencia — `check_plan_convergencia.py`

Guarda **nueva**, solo diseñada: **todavía no se ejecuta contra ningún plan real**. Devuelve
**`ACTIONABLE_CONVERGENCE_OK`** si se cumplen todas estas condiciones:
- las 21 direcciones están en `no-op` con `before == after`, sin import ni move;
- no hay diferidos y todas las salidas están en `no-op`;
- el state previo es 21/21 sin taint, la retención es 1, la versión de la contraseña es 1 y la variable efímera no
  está en el plan;
- `resource_drift` es **vacío** (caso A) o **exactamente una** entrada: `aws_db_instance.this`, `update`, cuya
  **única** diferencia es `latest_restorable_time`, con el contrato temporal (caso B).

En el caso B la guarda informa **`resource_drift = 1`** y el drift móvil, **nunca `resource_drift = 0`**.

### 40.3 TDD

- **RED:** 71 errores. `check()` aún no aceptaba el reloj y la guarda de convergencia no existía.
- **GREEN:** **48/48**: 31 de la guarda de refresh (21 previas y 10 nuevas) y 17 de convergencia.
- **Prueba previa ajustada porque cambió el requisito:** «valor completado distinto de AWS» deja fuera
  `latest_restorable_time`, que ahora tiene su contrato propio; ningún otro test se relajó.
- **Nuevos — PASS:** el mismo instante; AWS avanzó unos minutos; AWS avanzó varias horas, menos de 24.
- **Nuevos — FAIL:**
  - plan posterior a AWS o diferencia de más de 24 h;
  - instante inválido o nulo, en el plan o en AWS;
  - instantes en el futuro;
  - cualquier otro atributo de AWS que cambie.
- **Convergencia — PASS:** casos A y B.
- **Convergencia — FAIL:**
  - drift hacia atrás, de más de 24 h, inválido o futuro;
  - drift con otro atributo, de otra dirección, con dos entradas o con otra acción;
  - cualquier cambio de recurso, o un `no-op` con valores distintos;
  - cualquier salida que cambie, incluidas las tres de RDS;
  - diferidos, taint, retención distinta o la variable efímera.

### 40.4 Reevaluación del mismo plan — sin plan nuevo

- **SHA-256 exactos:** el plan `bd796127…d228` y el JSON `94efaeae…84e2` no cambiaron.
- **Describe fresco** (guardado en privado): AWS avanzó `LatestRestorableTime` **3301 s** desde el plan.

**`check_plan_refresh_instancia.py`: `INSTANCE_REFRESH_PLAN_OK`.**

| Elemento | Resultado |
| --- | --- |
| `resource_changes` | 0 |
| `resource_drift` | Solo la instancia |
| Atributos del drift | Los mismos 36: 17 valores de AWS exactos, `latest_restorable_time` con `MOVING_ATTRIBUTE_OK` y 18 formas exactas |
| `deferred_changes` | 0 |
| Salidas | Las tres de RDS al valor real; el resto, `no-op` |
| Taint | Conservado |

**Frescura posterior, solo lectura:**
- state en serial 6, 21/21, solo la instancia `tainted`, sin `.tflock`;
- RDS `available`; parámetros de usuario = los cuatro; las tres invariantes en verde; SecureString en versión 1.

**`PRODUCTION_SECRET_ABSENT = true`:** se buscó en 24 584 archivos y en el state, en memoria.

**Estado: H-031-3 MOVING ATTRIBUTE CONTRACT READY.** Sin apply ni untaint.

## 41. H-031-3 — refresh-only aplicado, readback 40/40 y untaint; convergencia en revisión (2026-10-06)

Autorización del usuario: **APPLY EXACT REFRESH + READBACK + UNTAINT + ACTIONABLE CONVERGENCE**. Sustituye
el criterio `resource_drift = 0` por `ACTIONABLE_CONVERGENCE_OK` (§40) y prohíbe aplicar la convergencia. Esta
sesión de Claude Code es nueva, así que antes de operar se verificó el estado local: rama y HEAD, ningún
`terraform.exe` activo, SHA del plan y del JSON exactos, ningún refresh apply previo y 156 pruebas de las guardas en
verde. El runner privado es `tmp/h0313r/ri_apply.py`; la sesión AWS se había renovado a las 01:53 UTC y hubo STS
antes de cada operación.

### 41.1 Pre-apply

- STS correcto y cuenta en `FREE` / `ACTIVE`.
- Plan `bd796127…d228` y JSON `94efaeae…84e2` exactos, con configuración y lock idénticos a la instantanea.
- State en serial **6**, igual al del plan, mismo lineage, 21/21, solo la instancia `tainted` y sin `.tflock`.
- AWS: RDS `available`, con identidad, retención 1 y `sg-rds`; grupo `in-sync`; sin modificaciones pendientes;
  SecureString en versión 1.
- **`check_plan_refresh_instancia.py` con describe fresco: `INSTANCE_REFRESH_PLAN_OK`**:
  - 0 cambios y drift solo en la instancia;
  - 36 atributos (18 + 18), con `latest_restorable_time` en `MOVING_ATTRIBUTE_OK` (AWS +23 704 s);
  - 0 diferidos, las tres salidas de RDS y el taint conservado.

### 41.2 Refresh-only aplicado

- `terraform apply -input=false -no-color <refresh plan>`: **exit 0, `Apply complete! Resources: 0 added, 0
  changed, 0 destroyed.`**
- **Post-refresh:**
  - serial 6 → 7, mismo lineage, 21/21, sin `.tflock`;
  - **taint conservado**;
  - los 18 atributos calculados **poblados** (17 iguales al describe y `latest_restorable_time` con su valor del
    plan) y las 18 formas exactas;
  - salidas `arn_rds`, `endpoint_rds` e `id_de_recurso_rds` **pobladas** y coherentes con AWS;
    `identificador_rds`, `nombre_de_base` y `puerto_rds` intactas;
  - **AWS sin cambios** respecto a la foto previa.

### 41.3 Readback, custodia y untaint

- **Readback: 40/40 PASS**, más 5/5 comprobaciones adicionales del state frente a AWS: `DbiResourceId`, ARN,
  endpoint, KMS, status e identifier. Incluye RDS, subnet group, SG, parameter group, parámetros, invariantes, KMS,
  red, retención, `deletion_protection`, logs, snapshot final, ausencia de `password` y `password_wo`, y SSM en
  versión 1.
- **`PASSWORD_CUSTODY_CHAIN_PASS = true`.** Se apoya en estos hechos:
  - el SecureString está en versión 1 y se modificó por última vez antes del apply de creación;
  - ese apply lanzó `CreateDBInstance`;
  - su runner leyó el SecureString solo en memoria y lo pasó solo por `TF_VAR_contrasena_master`;
  - la instancia se creó después de iniciarse ese apply.

  **No es una prueba de autenticación PostgreSQL**, y no se afirma `SSM_PASSWORD_MATCH`.
- **Untaint exacto:** `terraform untaint module.base_de_datos.aws_db_instance.this` terminó con **exit 0**.
  Serial 8, 21/21, **ningún recurso `tainted`**, mismo lineage, sin `.tflock` y AWS sin cambios.

### 41.4 Plan de convergencia — no se aplica

- `terraform plan` normal, con retención 1 y la contraseña custodiada solo en memoria: **exit 0, «No changes.
  Your infrastructure matches the configuration.»**
- **SHA-256:** del binario `bdbaa8ea3b158abeb11f35d85ded547c6f96334ad88ec406ff01f61c2a4da2bb`; del JSON
  `d206e7dc062cffacf567e721ebe452e768a26d2d4291235e95a2e8c986fd81aa`. State intacto y `.tflock` liberado.

| Elemento | Resultado |
| --- | --- |
| `resource_changes` | 21, todos `no-op` |
| `deferred_changes` | 0 |
| `output_changes` | Todas `no-op` |
| `resource_drift` | **1**: `aws_db_instance.this`, `update`, **solo `latest_restorable_time`** (de 2026-10-05T19:16:49Z a 2026-10-06T01:51:53Z, unas 6,6 h). Es la forma del **caso B** |
| JSON | `applyable = false`, `complete = true`, `errored = false` |

**`check_plan_convergencia.py`: rechazo `INCOMPLETE`.** La guarda exige `applyable = true`, condición que
heredó de las guardas de planes **con cambios**. Pero Terraform marca `applyable = false` precisamente cuando un
plan **no tiene nada que aplicar**, que es la definición de convergencia: es un **error de diseño de la guarda**
(§40), no del plan. Un diagnóstico **en memoria**, sobre una copia con `applyable = true` y sin modificar la guarda
ni los artefactos ni darlo por aceptado, devuelve `ACTIONABLE_CONVERGENCE_OK`, **caso B**: `resource_drift = 1` y
drift móvil `latest_restorable_time`.

Siguiendo la regla de la autorización, **STOP**: no hubo apply, `ignore_changes`, excepción, refresh-only ni
cambio en la guarda. **`PRODUCTION_SECRET_ABSENT = true`.**

### 41.5 Estado — STATE REFRESHED / CONVERGENCE REVIEW REQUIRED

Recuperación del state **completa**: instancia registrada y sana, 21/21, sin taint y AWS sin cambios. Falta el
criterio formal de convergencia.

**Propuesta, sin ejecutar:** corregir la precondición de `check_plan_convergencia.py` con TDD, exigiendo
**`applyable = false`** (un plan convergente no tiene nada que aplicar), `complete = true` y `errored = false`, sin
cambiar nada más. Después, reevaluar **este mismo JSON**, sin plan nuevo.

**Nota de entorno (corregida en §42):** la búsqueda del secreto recorrió menos archivos que en los checkpoints
anteriores porque **el usuario eliminó deliberadamente**, durante un mantenimiento de espacio en disco, carpetas
históricas de `tmp/` —entre ellas `tmp/task030`, `tmp/task0302`, `tmp/h0312-align`, `tmp/h0312`,
`tmp/task021-revalidation`, `tmp/task018`, `tmp/h031iam` y `tmp/task028`— y limpió las cachés de Docker/BuildKit y
Trivy. **Los runners de H-031-3 no fueron responsables.** No afecta al resultado: el secreto no aparece en nada de
lo que existe.

## 42. H-031-3-CONVERGENCE-GUARD-FIX — guarda corregida y el mismo JSON aceptado (2026-10-06)

Autorización del usuario: **H-031-3-CONVERGENCE-GUARD-FIX — TDD + REEVALUATE SAME JSON + CLOSE H-031-3**.
Corrige **solo** la precondición defectuosa de `check_plan_convergencia.py` (§41). Prohíbe cualquier apply, un
plan nuevo, cambios en AWS, mutaciones del state, `ignore_changes`, ampliar el contrato de drift e iniciar
H-031-5.

### 42.1 Estado base, solo lectura

- Rama `Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`, HEAD `6c31d1d`, sin staging.
- STS todavía válido, sin pedir otra renovación.
- State en serial 8, 21/21, 0 taints, sin `.tflock`, con su última escritura en el untaint.
- RDS `available` y SecureString en versión 1.
- Plan de convergencia `bdbaa8ea…a2bb` y JSON `d206e7dc…81aa` intactos.

### 42.2 Corrección — TDD

- **Defecto:** la guarda exigía `applyable = true`, condición heredada de las guardas de planes con cambios. Un
  plan **convergente** no tiene nada que aplicar y Terraform lo marca **`applyable = false`**; el JSON real de §41
  trae `applyable = false`, `complete = true` y `errored = false`.
- **Cambio mínimo:**
  - `applyable is False`; si no, `APPLYABLE`;
  - `complete is True` y `errored is False`, ambos explícitos; si no, `INCOMPLETE`.
  - No se tocó ninguna otra condición, y la semántica quedó documentada en la guarda.
- **RED:** con el fixture en la semántica real (`applyable = false`), **26 fallos**. La guarda rechazaba todo con
  `INCOMPLETE` antes de llegar a sus controles.
- **GREEN:** **24/24**, y 203 pruebas de las demás guardas sin cambios.
- **Pruebas nuevas:**
  - PASS: casos A y B con la semántica real;
  - FAIL: `applyable` verdadero, ausente o nulo; `complete` falso, ausente o nulo; `errored` verdadero, ausente o nulo.
- **Siguen en verde** las que rechazan: un cambio de recurso; un segundo drift, otro atributo, otra dirección u otra
  acción; un cambio de salida; diferidos; taint; otra retención; el secreto; y un instante inválido, futuro, hacia
  atrás o de más de 24 h.

### 42.3 Reevaluación del MISMO JSON, sin plan nuevo

`check_plan_convergencia.py` sobre `h0313r-ria-convergencia.json`, con su SHA exacto:
**`ACTIONABLE_CONVERGENCE_OK`, CASO B**.

| Elemento | Resultado |
| --- | --- |
| Acciones | 0 add / 0 change / 0 destroy |
| `resource_drift` | **1**: solo `module.base_de_datos.aws_db_instance.this`, `["update"]`, y único atributo distinto `latest_restorable_time` |
| `deferred_changes` | 0 |
| Salidas | `no-op` |

**El plan de convergencia no se aplicó.**

**Sin mutaciones:**
- binario y JSON de convergencia sin cambios;
- state en serial 8, mismo lineage recuperado, 21/21, 0 taints, sin `.tflock`, y su última escritura sigue siendo
  la del untaint;
- describe de RDS idéntico al posterior al untaint, salvo el atributo móvil;
- SecureString en versión 1.

**`PRODUCTION_SECRET_ABSENT = true`**, sobre el conjunto **actual** de archivos (13 048).

### 42.4 H-031-3 — cadena completa

1. El refresh-only exacto terminó con exit 0 y **0/0/0**; state completo y taint conservado (§41).
2. Readback **40/40 PASS + 5/5**.
3. **`PASSWORD_CUSTODY_CHAIN_PASS = true`**. No es una prueba de autenticación PostgreSQL.
4. Untaint exacto con exit 0: **serial 8, 21/21, 0 taints**.
5. El plan de convergencia original, **sin regenerar**, cumple **`ACTIONABLE_CONVERGENCE_OK`, caso B**, con
   `resource_drift = 1` exclusivamente en `latest_restorable_time`. Nunca se informa `resource_drift = 0`.

### 42.5 Gates

| Gate | Resultado |
| --- | --- |
| Offline: Terraform fmt, validate y test de los seis roots, suites Python, compose y `diff --check` | **ALL OFFLINE GATES PASSED**. `terraform_datos` 311, `terraform test` de datos 30/30, laboratorio 297, seguridad 88, OIDC 60 y state 12. Reutilizó la caché de providers de la ejecución anterior, sin copias nuevas |
| Gitleaks | Reconstruido con el **pin durable**: 8.30.1, zip de Windows `d29144de…` según los reportes de Task/021 y Task/028; el ejecutable coincide byte a byte con el miembro del zip. Detalle de entregable, historial y control positivo en §42.6 |
| Account ID, espacios y codificación, permisos y credenciales del CI | §42.6 |
| **Enlaces Markdown** | **NO EJECUTADA.** Su parser, `markdown-it-py`, vivía en `tmp/task018`, que el usuario eliminó, y **no tiene definición durable** en el proyecto: ni en la documentación y el CI de infra, ni en los lockfiles del backend; el frontend no usa `markdown-it` y el Python global no lo tiene. Según la autorización, no se inventa una versión ni se debilita la gate |

### 42.6 Resultado de la gate de seguridad y documentación

Script de auditoría local, igual al de los checkpoints anteriores salvo las dos dependencias de carpetas eliminadas.

| Comprobación | Resultado |
| --- | --- |
| Gitleaks 8.30.1, entregable (350 archivos de `git ls-files`) | **0** hallazgos |
| Gitleaks 8.30.1, historial completo | **0** hallazgos |
| Control positivo de Gitleaks | Detectado (exit **7**) |
| Account ID real en el entregable | **0** |
| Espacios, finales de línea y codificación de los 82 archivos cambiados | **PASS** |
| Permisos y referencias a credenciales del CI | **Sin cambios** |
| `git diff --check` | **0** |
| Enlaces Markdown (176 archivos) | **NOT RUN**: `markdown-it-py` sin definición durable |

### 42.7 Estado

La recuperación y la **convergencia de H-031-3 quedan aceptadas** con la guarda corregida. El cierre formal de
H-031-3 queda **pendiente de la gate de enlaces**, bloqueada por una herramienta sin definición durable. No hubo
apply, plan nuevo ni cambios en AWS, y no se inició H-031-5.

**Actualización (§43):** la gate de enlaces se ejecutó completa con un pin durable nuevo y H-031-3 quedó **COMPLETE**.

## 43. H-031-3-MARKDOWN-LINK-GATE — pin durable de la gate de enlaces y cierre de H-031-3 (2026-10-06)

Autorización del usuario: **H-031-3-MARKDOWN-LINK-GATE — DURABLE PIN + EXACT LINK GATE + CLOSE H-031-3**. Resuelve
**solo** el último bloqueo de H-031-3: la gate de enlaces Markdown que quedó **NOT RUN** en §42. Prohíbe cambios en
AWS, apply, plan nuevo, refresh-only, untaint, operaciones de state, `force-unlock`, cambios al contrato de
convergencia, iniciar H-031-5, commit, staging, push y PR.

### 43.1 Decisión durable nueva

- **La versión histórica de `markdown-it-py` es desconocida.** La gate la cargaba desde `tmp/task018/audit-venv`, que
  el usuario eliminó deliberadamente al liberar disco, y **nunca estuvo fijada de forma durable**. No se reconstruye
  ni se afirma cuál era.
- **Decisión NUEVA del usuario, no reconstrucción histórica:** la gate de enlaces usa **`markdown-it-py` 4.2.0** con
  **`mdurl` 0.1.2**, ambos con versión y SHA-256 durables.
- Antes de usarlos se verificó cada wheel:
  - nombre exacto;
  - SHA-256 local igual al autorizado **y** al que publica PyPI;
  - versión en `METADATA` y etiqueta `py3-none-any`;
  - ninguno retirado (*yanked*).

| Wheel | SHA-256 | `METADATA` |
| --- | --- | --- |
| `markdown_it_py-4.2.0-py3-none-any.whl` | `9f7ebbcd14fe59494226453aed97c1070d83f8d24b6fc3a3bcf9a38092641c4a` | `Version: 4.2.0` y `Requires-Python: >=3.10`. Su única dependencia sin extras es `mdurl~=0.1`, **compatible con 0.1.2** |
| `mdurl-0.1.2-py3-none-any.whl` | `84008a41e51615a49fc9966191ff91509e3c40b939176e643fd50a5c2196b8f8` | `Version: 0.1.2` y `Requires-Python: >=3.7`, sin dependencias |

### 43.2 Pin versionado fuera de `tmp/`

- [`scripts/security/requirements-markdown-links.txt`](../../scripts/security/requirements-markdown-links.txt) fija
  ambas dependencias con `==` y `--hash=sha256:`, y es compatible con `pip install --require-hashes -r`.
- Es **solo tooling de auditoría de documentación**. No entra en las dependencias de runtime del backend, del
  frontend ni de la aplicación, y el CI no cambia.
- Su cabecera explica por qué existe: la gate de enlaces **no debe volver a depender de un venv efímero bajo `tmp/`**.

### 43.3 Entorno temporal

- Venv **nuevo y descartable** en `tmp/h0313r/link-audit-venv`, ignorado por Git y creado **sin pip** para que solo
  contenga la herramienta.
- Los dos wheels se descargaron de la URL que publica PyPI y se verificaron (§43.1). Se instalaron desde esos mismos
  archivos con `--require-hashes`, `--only-binary=:all:` y `--no-index`, y pip volvió a comprobar cada hash contra el
  archivo versionado.
- Contenido final: exactamente `markdown-it-py==4.2.0` y `mdurl==0.1.2`, en 1,7 MB; `markdown_it.__version__` es
  `4.2.0` y `mdurl.__version__` es `0.1.2`.
- No se recreó `tmp/task018` ni se copió ningún provider de Terraform.

### 43.4 Gate de enlaces, con la misma semántica

- Es el mismo script de auditoría de los checkpoints anteriores, y su lógica de enlaces es **byte a byte idéntica** a
  la histórica; se comprobó antes de ejecutarla:
  - `MarkdownIt('commonmark').enable('table')`;
  - enlaces e imágenes relativos, con sus fragmentos;
  - archivos inexistentes;
  - anclas de encabezados con sus duplicados, y anclas HTML explícitas.
- Solo cambia el **origen** de dos herramientas:
  - `markdown-it-py` sale del pin versionado. La gate exige que el pin declare exactamente esas versiones y hashes, y
    que el parser importado sea el del venv;
  - Gitleaks sale del mismo pin durable de §42.
- Se ejecutó completa sobre el conjunto del entregable dos veces: antes de documentar, con **2187** enlaces relativos y
  **0 rotos**, y como gate final después de documentar:

| Gate de enlaces final | Resultado |
| --- | --- |
| Archivos Markdown | 176 |
| `relative_links` | **2194** |
| `broken_links` | **0** |

### 43.5 Seguridad y documentación, ejecución final

| Comprobación | Resultado |
| --- | --- |
| Enlaces Markdown | **PASS**: 2194 enlaces relativos y **0 rotos** |
| Gitleaks 8.30.1, entregable (351 archivos de `git ls-files`) | **0** hallazgos |
| Gitleaks 8.30.1, historial completo | **0** hallazgos |
| Control positivo de Gitleaks | Detectado (exit **7**) |
| Account ID real en el entregable | **0** |
| Espacios, finales de línea y codificación de los 83 archivos cambiados | **PASS** |
| Permisos y referencias a credenciales del CI | **Sin cambios** |
| `git diff --check` | **0** |

### 43.6 Regresión

| Gate | Resultado |
| --- | --- |
| `test_check_plan_convergencia` | **24/24** |
| `terraform_datos`, suite completa | **311** |
| `terraform test` de `terraform-datos` | **30/30** |
| Laboratorio | **297** |
| Seguridad | **88** |
| OIDC | **60**, con la misma omisión de siempre en Windows: los permisos POSIX se comprueban en el CI Linux |
| `terraform_state` | **12** |
| `fmt`, `validate` y `test` de los seis roots, compose del laboratorio y `git diff --check` | **ALL OFFLINE GATES PASSED**, exit real 0 |

Reutilizó el `TF_DATA_DIR` existente, idéntico antes y después (21 archivos y 5 217 461 698 bytes): ninguna copia
nueva de providers.

### 43.7 Infraestructura, solo lectura

Verificado con STS válido, antes de documentar y otra vez al final:

| Elemento | Resultado |
| --- | --- |
| State | Serial **8**, 21/21, **0 taints**, mismo lineage recuperado y sin `.tflock`. Sin escrituras nuevas: la última sigue siendo la del untaint |
| RDS | `available`; el describe es idéntico al posterior al untaint, salvo el atributo móvil: **sin cambios de configuración** |
| SecureString | Versión **1** |
| Plan de convergencia | El mismo plan (`bdbaa8ea…a2bb`) y el mismo JSON (`d206e7dc…81aa`), **sin regenerar ni aplicar**: **`ACTIONABLE_CONVERGENCE_OK`, caso B**, con 0 add / 0 change / 0 destroy, `resource_drift = 1` exclusivamente en `latest_restorable_time`, 0 diferidos y salidas `no-op` |

**`PRODUCTION_SECRET_ABSENT = true`** sobre el conjunto **actual** de archivos.

### 43.8 Estado — H-031-3 COMPLETE

Con la gate de enlaces ejecutada completa, **H-031-3 queda COMPLETE**. La cadena es la de §42.4: refresh-only exacto
(0/0/0), readback 40/40 + 5/5, `PASSWORD_CUSTODY_CHAIN_PASS = true`, untaint (serial 8, 21/21, 0 taints) y
convergencia aceptada en el caso B.

En este checkpoint no hubo apply, plan nuevo, refresh-only, untaint, operaciones de state ni cambios en AWS. Tampoco
hubo staging, commit, push ni PR, y backend y frontend siguen intactos. **H-031-5 no se inició.** Task/031 sigue
**En progreso**; su aprobación final es exclusivamente `approved: Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`.

## 44. H-031-5 — ejecutora privada de D-24 por fases: implementación offline y cuota Lambda (2026-10-06)

Autorización del usuario: **H-031-5-DESIGN-RESOLUTION — PHASED EXECUTOR + QUOTA REQUEST + OFFLINE
IMPLEMENTATION**. Sustituye las opciones C/c del STOP anterior (§44.1). Prohíbe el apply de `terraform-datos`,
mutar el state, iniciar H-031-6, commit, staging, push y PR. La única mutación de cuenta autorizada es
**solicitar** la cuota de concurrencia de Lambda a **101**.

### 44.1 STOP previo y decisiones del usuario

La primera autorización de H-031-5 pedía que la ejecutora leyera el SecureString en *runtime* a partir de una
referencia. Antes de implementar se detuvo por dos contradicciones materiales:

- **Entrega del secreto.** D-23 decidió entrega en despliegue, sin lector en *runtime* ni endpoint de SSM
  ([decisiones §5.3](../architecture/production-postgresql-rds-decisions.md#53-credenciales-y-almacén-de-secretos)),
  mientras el contrato de módulo de D-24 recibía `arns_de_parametros` (§12.1) y §13 hablaba de una
  `BLOG_DATABASE_URL` propia. Con la red de D-22, `sg-admin` solo sale a RDS: según la guía de Lambda, «When you
  attach your function to a VPC, it can only access resources available within that VPC».
- **Serialización.** D-24 fija concurrencia reservada 1, y la cuenta tenía una cuota de **10** ejecuciones
  concurrentes. AWS: «You can reserve up to the Unreserved account concurrency value minus 100». El apply
  crearía la función y fallaría en `PutFunctionConcurrency`.

| Tema | Decisión del usuario (2026-10-06) |
| --- | --- |
| Credenciales | **Diferidas a H-031-6**, de forma explícita y revisable. En H-031-5: sin endpoint de SSM, NAT ni Internet; sin `ssm:GetParameter` ni `kms:Decrypt`; sin contraseña en el entorno ni en el payload; sin `DATABASE_URL`, secreto en el ZIP ni conexión a PostgreSQL. La contradicción D-23/D-24 queda **documentada y abierta**, no resuelta |
| Fases | **H-031-5:** infraestructura Lambda privada, IAM mínimo, red, RC=1 cuando la cuota lo permita, logs, artefacto mínimo, contrato de invocación, salida saneada y prueba sin base de datos. **H-031-6:** `psycopg` e integridad, CA, credenciales, identidad SQL, `verify-full` real y los modos con PostgreSQL —como mínimo `verify`; `export` si hace falta para cerrar Task/031—. **`Task/036`:** Alembic, migraciones, `upgrade`/`downgrade` y `purge` |
| Código | Python 3.12, solo biblioteca estándar; `selfcheck` interno; los modos de D-24 enumerados por contrato y respondiendo `NOT_IMPLEMENTED` |
| Red | Subredes privadas y **solo `sg-admin`**. La regla `sg-admin -> S3:443` **no** se crea hasta que un modo la use |
| IAM | Rol propio dentro de `modulos/ejecutor_privado`, `PersonalBlogEjecutorDatos`; trust del principal de Lambda; solo ENI de VPC y logs. `PersonalBlogDataOperator` no se modifica |
| Concurrencia | **RC=1 se mantiene.** Sin excepción temporal y sin sustituirla por un *advisory lock*, que será defensa adicional cuando exista base de datos. Solicitar la cuota a 101. **Gate:** sin plan productivo final mientras la cuota sea menor que 101 |

### 44.2 Estado de partida, solo lectura

Revalidado el **2026-10-07 a las 02:40 UTC** con STS válido, sin pedir otra sesión: **BASELINE_OK**.

- `PersonalBlogAdministrator` en la cuenta verificada, us-east-2; plan de la cuenta FREE / ACTIVE, que expira el
  2027-03-15.
- State en serial **8**, 21/21, **0 taints**, mismo lineage, sin `.tflock` y sin escrituras desde el untaint.
- RDS `available`, retención 1, sin cambios respecto del describe posterior al untaint; SecureString en versión **1**.
- Convergencia de H-031-3 intacta: mismo plan y mismo JSON, `ACTIONABLE_CONVERGENCE_OK`, caso B.
- Red y grupos intactos (`red_intacta.py`): las 5 reglas de AWS son exactamente las del state; `sg-admin` solo sale a
  `sg-rds:5432`; RDS lleva solo `sg-rds`.
- Lambda: `ConcurrentExecutions = 10`, `UnreservedConcurrentExecutions = 10` y ninguna función en la cuenta.

### 44.3 Diseño implementado

**Inventario cerrado de H-031-5: 4 recursos nuevos** y 2 salidas nuevas, frente a los **21 existentes**, que no
cambian.

| Dirección | Tipo AWS | Propósito | Depende de | Por qué es de H-031-5 |
| --- | --- | --- | --- | --- |
| `module.ejecutor_privado.aws_cloudwatch_log_group.this` | Grupo de logs `/aws/lambda/blog-prod-ejecutor`, 14 días | Logs de la ejecutora con retención declarada; si lo creara Lambda nacería con retención infinita | — | D-24 §12.1 y baseline D-11 de DH-4 |
| `module.ejecutor_privado.aws_iam_role.this` | Rol IAM `PersonalBlogEjecutorDatos` | Rol de ejecución propio | — | D-24 §8.2 y §12.3 |
| `module.ejecutor_privado.aws_iam_role_policy.this` | Política en línea `PersonalBlogEjecutorDatos-ejecucion` | ENI de Lambda en VPC, su Deny desde el código y logs del grupo propio | Rol | Mínimo privilegio de H-031-5 |
| `module.ejecutor_privado.aws_lambda_function.this` | Lambda `blog-prod-ejecutor` | Shell de D-24 | Rol, política, grupo; subredes y `sg-admin` de `module.red` | D-24 §12.1 |

Salidas nuevas del root, no sensibles: `nombre_de_la_ejecutora` y `arn_de_la_ejecutora`, contrato de H-031-6 y del
rol de despliegue de Task/038. **No se crean**: `aws_lambda_permission`, URL de función, disparadores, la regla
`sg-admin -> S3`, endpoints de interfaz, NAT, alarmas (H-031-8) ni permisos de SSM, KMS o S3.

- **Función.** `python3.12`, `x86_64` (la única arquitectura autorizada, Task/024), handler `ejecutor.manejar`,
  128 MB, 30 s, sin versiones publicadas, **concurrencia reservada 1 como literal**, sin variables de entorno ni
  capas. Va en las dos subredes privadas y **solo con `sg-admin`**, sin IPv6. RDS sigue solo con `sg-rds`, y la
  regla `sg-admin -> sg-rds:5432` no cambia.
- **IAM.** El trust nombra solo `lambda.amazonaws.com`. AWS documenta así el rol de ejecución, y `aws:SourceArn`
  «applies only to policies where your Lambda function is the target resource». La política en línea tiene tres
  sentencias:
  - **ENI de Lambda en VPC.** Seis acciones sobre `Resource: "*"`, porque la guía de Lambda lo exige («allow them on
    all resources»). Según la referencia de IAM, `DescribeNetworkInterfaces` y `DescribeSubnets` no admiten
    recurso; las otras cuatro las ejecuta el servicio Lambda en nombre de la función.
  - **Deny desde el código.** Es la práctica que recomienda AWS: con `lambda:SourceFunctionArn` igual a la
    función, el código no puede llamar a esas APIs de EC2. El servicio sí puede, porque sus llamadas de ENI no
    llevan esa clave.
  - **Logs.** `logs:CreateLogStream` y `logs:PutLogEvents` evalúan contra el recurso `log-stream` en la referencia
    de IAM, así que se conceden solo sobre `<grupo>:log-stream:*`, sin `CreateLogGroup`.
- **Contrato de invocación.** El payload es un objeto con la única clave `modo`.
  - `selfcheck` devuelve el contrato, la versión de Python y los modos de D-24 como `NOT_IMPLEMENTED`.
  - `verify` y `export` responden `NOT_IMPLEMENTED` con fase H-031-6; `upgrade`, `downgrade` y `purge`, con
    Task/036. `downgrade` forma parte del modo Alembic de D-24 §8.2.
  - Cualquier otra cosa es `INVALID_PAYLOAD`, sin repetir el evento. Un error interno devuelve `INTERNAL_ERROR`,
    sin detalle ni traza.
  - Una línea de registro por invocación, con las mismas tres claves siempre.
- **Artefacto.** `scripts/terraform_datos/empaquetar_ejecutor.py` construye un ZIP **determinista**:
  - una sola entrada `ejecutor.py`, sin compresión, fecha fija, permisos `0644` y origen Unix;
  - 2543 bytes, con SHA-256 **`e27fe735…23bd`**;
  - el pin queda versionado en el empaquetador. La raíz exige que el archivo coincida con el digest declarado
    —validación de la variable y precondición del módulo— y la guarda exige que ese digest sea el pin.

### 44.4 TDD

| Componente | RED | GREEN |
| --- | --- | --- |
| Código de la ejecutora y empaquetado | 14 errores: `ejecutor.py` y el empaquetador no existían | **23/23**. Hasta fijar el pin del artefacto real fallaban las dos pruebas que lo exigen |
| `terraform test` del root | `validate` rechazó el `expect_failures` sobre un recurso del módulo hijo: Terraform solo admite objetos del root | **33/33** (30 + 3). El rechazo del digest pasó a la validación de la variable del root, primera barrera; la precondición del módulo es la segunda |
| Pruebas estáticas del módulo y el cableado | 14 fallos: módulo y cableado inexistentes | **15/15** |
| Guarda del plan, `check_plan_ejecutor.py` | Módulo inexistente | **29/29**. El primer GREEN destapó un defecto de la **guarda**: trataba `vpc_id`, que es calculado, como red desconocida. Se corrigió la guarda, no la prueba |
| Laboratorio | 5 de 7 en rojo | **7/7** |

- `test_secretos.py` solo cambió su preparación: la copia temporal necesita el módulo nuevo para el `init` (RED:
  «Unreadable module directory»). Sus aserciones no cambian.
- `test_grupo_por_omision.py` revisa ahora también las fuentes del módulo nuevo.
- REFACTOR innecesario: el código es mínimo.

### 44.5 Guarda del plan

`scripts/terraform_datos/check_plan_ejecutor.py` (`EXECUTOR_PLAN_OK`) valida una **lista cerrada**:

- **Plan:** versión 1.16.2, `applyable`, completo y sin errores.
- **Variables:** las de H-031-3 (identidad, cuenta, región, protecciones, red, etiquetas, sin endpoints
  alternativos y sin la efímera), contraseña en versión 1, retención 1 y **artefacto igual al pin**.
- **Checks y state previo:** todos los checks en `pass`; state previo 21/21 sin taint.
- **Existentes:** los 21 en `no-op` con `before == after`.
- **Nuevos:** exactamente los 4, en `create`. La función, el rol, la política y el grupo se comprueban atributo a
  atributo.
- **Cableado y salidas:** cableado desde `module.red` y grupo por omisión sin uso; sin diferidos; las 15 salidas
  existentes en `no-op` y exactamente las 2 nuevas, no sensibles.
- **Drift:** `resource_drift` en el caso A o en el caso B de §40.

Se probó con fixtures, porque **el plan productivo no se generó**: la cuota está por debajo de 101 (§44.7).

### 44.6 Laboratorio y paridad

Un solo root y dos destinos. El lanzador del laboratorio:
- envía `iam` y `lambda` al root de datos;
- construye el artefacto con el **mismo** empaquetador y exige su pin antes de escribir variables;
- trata la función y su grupo de logs como recursos **vivos** de datos, y como residuo una vez destruido datos.

**El ciclo contra Floci no se ejecutó en H-031-5.** La matriz de paridad registra la ejecutora como `No
evaluada`. La cuota de la cuenta, la ENI real y la evaluación de IAM son AWS-only.

### 44.7 Cuota de concurrencia de Lambda

Descubrimiento de solo lectura con Service Quotas:

| Dato | Valor |
| --- | --- |
| Cuota | `Concurrent executions`, código `L-B99A9384`, servicio `lambda`, unidad `Count` |
| Región | us-east-2, según el ARN de la cuota |
| Ajustable / global | Sí / no |
| Valor aplicado | **10**, igual que `lambda get-account-settings` (sin reservar: 10) |
| Valor por omisión de AWS | 1000 |
| Solicitudes previas | Ninguna |
| Costo | Service Quotas «is available to all AWS customers at no additional cost», y la concurrencia reservada tampoco se cobra: «Configuring reserved concurrency for a function incurs no additional charges» |

**La solicitud NO se envió: STOP antes de mutar.** El rol vinculado `AWSServiceRoleForServiceQuotas` **no existe**
en la cuenta (`NoSuchEntity`). Según la documentación de Service Quotas, pedir un aumento por la API exige darle
«the necessary permission to create a support case on your behalf», que se concede con `iam:CreateServiceLinkedRole`.
Es decir, la primera solicitud **crea** ese rol vinculado, con la política administrada
`ServiceQuotasServiceRolePolicy` (`support:CreateCase`, `support:DescribeCases` y `support:ResolveCase`). La
autorización cubría solo la solicitud, no la creación de un rol IAM, así que el runner se detuvo sin enviar nada.

Estado: **cuota en 10, solicitud no enviada, decisión del usuario pendiente sobre el rol vinculado.**

### 44.8 Gates

| Gate | Resultado |
| --- | --- |
| Offline: `fmt`, `init`, `validate` y `test` de los seis roots, suites Python, compose y `diff --check` | **ALL OFFLINE GATES PASSED**, exit real 0. `terraform_datos` 378 (311 + 67 nuevas), `terraform test` de datos **33/33**, laboratorio 304, seguridad 88, OIDC 60 (la omisión POSIX de siempre) y state 12. Reutilizó el `TF_DATA_DIR`, idéntico antes y después: ninguna copia nueva de providers |
| Seguridad y documentación | **PASS** con la gate durable de enlaces: 2208 enlaces relativos y **0 rotos** en 176 Markdown. Gitleaks 8.30.1: entregable de 363 archivos con 0 hallazgos e historial con 0, y control positivo detectado (exit 7). Account ID real: 0. Espacios, finales de línea y codificación de los 96 archivos cambiados: PASS. Permisos y referencias a credenciales del CI: sin cambios. `git diff --check`: 0 |
| Secreto productivo | **`PRODUCTION_SECRET_ABSENT = true`**: valor del SecureString leído solo en memoria y buscado en el state leído, el directorio privado y el checkout sin `.git` (14 885 archivos), incluido el ZIP real de la ejecutora, con el SHA-256 del pin |

### 44.9 Estado

**Task/031 — H-031-5 IMPLEMENTATION READY / LAMBDA QUOTA PENDING.**

- La implementación offline está completa y en verde: módulo, código, empaquetador con pin, guarda con fixtures,
  laboratorio y documentación.
- **No hay plan productivo**: la cuota de concurrencia sigue en 10 y la solicitud a 101 no se envió, porque
  requiere crear el rol vinculado de Service Quotas.
- **Sin mutaciones en AWS ni en el state.** Los 21 recursos existentes siguen intactos; del módulo `red` solo cambió
  un comentario.
- Backend y frontend intactos. Sin staging, commit, push ni PR.
- H-031-5 no está completo y **no se inició H-031-6**.

**Actualización (§45):** el rol vinculado de Service Quotas se creó con autorización, y AWS rechazó la solicitud a 101.

## 45. H-031-5-LAMBDA-QUOTA — rol vinculado creado; solicitud a 101 rechazada por AWS (2026-10-07)

Autorización del usuario: **H-031-5-LAMBDA-QUOTA — SERVICE-LINKED ROLE + REQUEST 101 ONLY**. Autoriza **solo**
crear `AWSServiceRoleForServiceQuotas` para `servicequotas.amazonaws.com`, si AWS lo requiere, y enviar **una**
solicitud: `lambda`, `Concurrent executions` (`L-B99A9384`), **101**, us-east-2. Ninguna otra mutación de AWS.

### 45.1 Preflight, solo lectura

- **Primer intento (03:01 UTC):** se detuvo en STS por `ExpiredToken`, sin ejecutar nada. Tras renovar la sesión, el
  runner privado `tmp/h0315/cuota_101.py` corrió a las 03:05 UTC.
- **STS:** `PersonalBlogAdministrator`, cuenta esperada, us-east-2.
- **Baseline: BASELINE_OK.**
  - Cuenta FREE / ACTIVE.
  - State en serial 8, 21/21, 0 taints, mismo lineage, sin `.tflock` y sin escrituras nuevas.
  - RDS `available`, con retención 1 y sin cambios.
  - SecureString en versión 1; convergencia de H-031-3 intacta.
- **Lambda:** `ConcurrentExecutions = 10` y `UnreservedConcurrentExecutions = 10`.
- **Cuota:** `Concurrent executions` (`L-B99A9384`, `lambda`, us-east-2), ajustable, no global, aplicada en 10, sin
  solicitudes previas.

### 45.2 Rol vinculado de Service Quotas: creado

- **Creación.** No existía, así que se creó con `iam create-service-linked-role --aws-service-name
  servicequotas.amazonaws.com`. Es la única mutación de IAM de este checkpoint.
- **Readback:**
  - nombre `AWSServiceRoleForServiceQuotas` y path `/aws-service-role/servicequotas.amazonaws.com/`;
  - trust solo para `servicequotas.amazonaws.com`, con `sts:AssumeRole`;
  - una única política adjunta, `ServiceQuotasServiceRolePolicy`, administrada por AWS;
  - sin políticas en línea.
- **Gestión.** El rol no se modificó a mano. Es un rol de AWS, fuera de Terraform y de cualquier state del proyecto.

### 45.3 Solicitud de cuota: rechazada, sin reintento

- Se envió **una** llamada `request-service-quota-increase` con `lambda`, `L-B99A9384` y 101. AWS respondió
  `IllegalArgumentException`: «You must provide a quota value greater than the default quota value of 1000.0».
- **No quedó ninguna solicitud registrada**: el historial de la cuota tiene 0 entradas. La cuota aplicada sigue en
  10, igual que Lambda (10 y 10 sin reservar).
- **Causa, según la guía de Lambda:** «New AWS accounts have reduced concurrency and memory quotas for Lambda
  Functions [...] AWS raises these quotas automatically based on your usage». El valor por omisión de `Concurrent
  executions` es 1,000, y la API de Service Quotas no admite pedir un valor intermedio entre la cuota reducida de la
  cuenta y el valor por omisión.
- Conforme a la autorización —una sola solicitud y nunca más de 101—, **no se reintentó ni se cambió el valor**.

### 45.4 Estado

- **H-031-5 sigue IMPLEMENTATION READY, bloqueado solo por la cuota.** La vía autorizada, 101 por Service Quotas, no
  la acepta AWS, así que hace falta una decisión del usuario.
- Única mutación en AWS: el rol vinculado. State en serial 8, 21/21, 0 taints y sin lock; RDS y SecureString
  intactos.
- No se creó la Lambda, no se generó plan productivo, RC=1 sigue en el diseño y no se inició H-031-6.
- Sin staging, commit, push ni PR; backend y frontend intactos.

## 46. REMAINDER — H-031-6 a H-031-9 preparados offline; AWS bloqueado por la cuota de Lambda (2026-10-07)

Autorización del usuario: **Task/031 REMAINDER — COMPLETE H-031-5 THROUGH H-031-9 + FINAL READINESS, STOP ONLY ON
MATERIAL BLOCKERS**, mantenida en la continuación del 2026-10-07, que añade tres reglas:

- **No volver a solicitar 101.**
- **No pedir 1001 ni otro valor sin autorización explícita.**
- **No quitar RC=1** ni sustituirlo por una excepción temporal.

Sin staging, commit, push, PR ni merge; backend y frontend intactos.

### 46.1 Punto de partida y regla de fases

- **H-031-5 sigue IMPLEMENTATION READY**, bloqueado por la cuota de concurrencia de Lambda (10). AWS rechaza pedir 101
  ([§45](#45-h-031-5-lambda-quota--rol-vinculado-creado-solicitud-a-101-rechazada-por-aws-2026-10-07)).
- **Ninguna fase AWS es independiente de la ejecutora.**
  - H-031-6 y H-031-7 la usan: es el único canal privado a RDS (D-24).
  - Las alarmas de H-031-8 y el rol de D-20 vivirían en `terraform-datos`. Cualquier apply de ese root incluye la
    ejecutora, con RC=1.
  - Por eso **no se hizo ninguna llamada a AWS** en esta continuación.
- **Regla aplicada.** La raíz `terraform-datos` se queda **exactamente** en el plan de H-031-5 (4 recursos nuevos).
  - Cada fase posterior queda como módulo **no cableado**, con pruebas a nivel de módulo (`run` con
    `module { source }`), y como artefacto propio con pin.
  - El cableado de cada fase está descrito en §46.8. Se hace cuando el root pueda aplicarse, con su plan y su guarda.

### 46.2 H-031-6 — mecanismo de credenciales

**Propuesta — pendiente de aprobación.**

La contradicción abierta en H-031-5 (decisiones de RDS §8.2) se resuelve **sin cambiar ninguna decisión durable**:

- D-23 §5.3 (entrega en despliegue) trata de la Lambda **de aplicación**.
- La ejecutora no tiene ruta a SSM (D-22: sin NAT ni interface endpoint).
- `arns_de_parametros` ya no existía (§12.1, enmienda de H-031-5).

**Mecanismo propuesto.** El operador autorizado (`PersonalBlogAdministrator`, H-031-IAM):

- lee en memoria, de su SecureString, **solo** las credenciales que necesita el modo;
- las entrega en el evento de **una invocación síncrona** (`RequestResponse`, `LogType=None`).

La función las usa y las descarta. Script: `scripts/terraform_datos/operar_ejecutora.py`.

| Requisito | Cumplimiento |
| --- | --- |
| DH-2 | Nada en plan ni state: la ejecutora no recibe ningún valor de Terraform; las contraseñas nuevas se custodian con `value_wo` |
| D-22 | Sin NAT, sin interface endpoint de SSM: la función no lee SSM |
| D-23 | SSM SecureString sigue siendo la **única** custodia; `verify-full`; sin Secrets Manager ni CMK nueva |
| D-24 | Invocación por el plano de control con identidad humana autorizada; salida saneada |
| Cero secreto persistente | Ni variables de entorno, ni ZIP, ni log de la función, ni disco ni argumentos del operador |
| Mínimo privilegio | El rol de la ejecutora no tiene `ssm:*` ni `kms:*`; el operador lee solo lo que el modo usa |
| Presupuesto | Costo 0: ni endpoint, ni servicio nuevo |

**`identidades` recibe verificadores SCRAM-SHA-256**, calculados por el operador (`scripts/terraform_datos/scram.py`,
probado contra el vector de RFC 7677). Las contraseñas de `blog_migrate` y `blog_app` **nunca viajan**.

**Hallazgo, demostrado en la integración local.** Con `log_statement = ddl`, el **verificador** queda en el log de
PostgreSQL, que RDS exporta a CloudWatch con 14 días de retención.

- Medición: 4 de 4 verificadores en el log y 0 de 6 contraseñas.
- Un verificador no es la contraseña. Con 48 caracteres aleatorios, el ataque offline es inviable, y `StoredKey` no
  autentica sin observar un intercambio, que va cifrado por TLS.
- Medidas: D-20 **sin** `logs:*` (§46.6), retención acotada y rotación disponible.

**CloudTrail:** `Invoke` es un *data event* (desactivado por omisión) y no registra el payload. Verificar en AWS que no
hay selectores de datos de Lambda es un paso pendiente de la ráfaga final (§46.10).

### 46.3 H-031-6 — ejecutora h0316, identidades SQL y TLS

**Modos fuera de los cuatro de D-24 — Propuesta — pendiente de aprobación.** D-24 §8.2 admite un modo nuevo
«justificado». El `selfcheck` los separa de los modos de D-24 (`modos_d24` frente a `modos_de_task031`).

- `identidades`: la creación inicial con `blogadmin` por el canal privado, que D-23 §5.3 reserva a ese canal.
- `sintetico`: el marcador de H-031-7, que `verify` no puede sembrar porque es de solo lectura.

| Modo | Identidad SQL | Efecto |
| --- | --- | --- |
| `selfcheck` | — | Contrato y versión; ninguna conexión |
| `verify` | `blogadmin`, `blog_migrate` o `blog_app` | Solo lectura: TLS, servidor e identidad. Con `blog_app`, el `CREATE TABLE` de §9.2 **debe** fallar (se revierte siempre). Con `blog_migrate`, el marcador de una restaurada. Controles negativos opcionales |
| `identidades` | `blogadmin` | `CREATE`/`ALTER ROLE` con verificadores, privilegios de D-23 y límites de D-12 (5 y 89). Relectura **antes** de confirmar: si no coincide, revierte |
| `sintetico` | `blog_migrate` | Siembra o retira el marcador no sensible en `verificacion.marcador` |
| `export` | `blog_migrate` | §46.4 |
| `upgrade`, `downgrade`, `purge` | — | `NOT_IMPLEMENTED` (Task/036) |

**Controles negativos de `verify`.** Nunca usan la contraseña real.

| Control | Qué se intenta | Rechazo esperado |
| --- | --- | --- |
| `sin_tls` | `sslmode=disable` | El servidor, por `rds.force_ssl = 1` |
| `host_distinto` | La IP del mismo servidor | `verify-full`, por nombre |
| `ca_ajena` | `verify-full` contra el almacén del sistema | Este no contiene la CA privada de RDS |

**Hallazgos de PostgreSQL 16+**, demostrados contra 17.11 con un `CREATEROLE` no superusuario
(`tmp/h0316/evidencia/exploracion_roles_pg17.json`):

| Operación de `blogadmin` | Resultado | Consecuencia |
| --- | --- | --- |
| `ALTER DEFAULT PRIVILEGES FOR ROLE blog_migrate` sin membresía | `permission denied to change default privileges` | Hace falta actuar con los privilegios de `blog_migrate` |
| La misma, con `SET TRUE, INHERIT FALSE` | Denegada | `SET` solo no basta para `FOR ROLE` |
| La misma, bajo `SET ROLE blog_migrate` | Permitida | Solución adoptada |
| `CREATE SCHEMA … AUTHORIZATION blog_migrate` sin membresía | `must be able to SET ROLE` | Basta `SET TRUE` |
| `ALTER ROLE … NOSUPERUSER …` | «Only roles with the SUPERUSER attribute may change the SUPERUSER attribute» | El ajuste omite `SUPERUSER`, `REPLICATION` y `BYPASSRLS`; la relectura exige `false` |

**Solución adoptada:**
- una membresía `GRANT blog_migrate TO CURRENT_USER WITH INHERIT FALSE, SET TRUE` **transitoria**: `SET ROLE` →
  privilegios por omisión → `RESET ROLE` → esquema `verificacion` → `REVOKE`, en la misma transacción;
- **no queda privilegio nuevo**: el readback muestra solo el ADMIN automático de PostgreSQL;
- RDS añade `rds_superuser` al master. Las diferencias de RDS real se verán en AWS: un fallo revierte la transacción
  completa.

**Privilegios resultantes, en la integración:**
- la base de datos sin entradas `PUBLIC`: `blog_migrate=c` y `blog_app=c`;
- `public` con `blog_migrate=UC` y `blog_app=U`; `PUBLIC` solo con `U`, el valor por omisión de PostgreSQL 15+;
- `verificacion`, propiedad de `blog_migrate`, sin ACL extra;
- privilegios por omisión `blog_app=arwd/blog_migrate`, y `\dp` de una tabla de prueba con `blog_app=arwd`.

`blog_app`:
- puede hacer DML;
- no puede `DROP`, `CREATE`, tablas temporales ni leer `verificacion`;
- `blog_migrate` no puede `CREATE ROLE`.

**Artefacto h0316.** Lo construye `scripts/terraform_datos/empaquetar_ejecutor.py --fase h0316`.

- **Fuentes** (`codigo_h0316/`): `ejecutor.py`, `operaciones.py`, `exportacion.py` y `rds-ca-us-east-2.pem`. El bundle
  regional tiene 3 raíces y SHA-256 `d46e1bdfda05c8e7644e50930806a19b139a222542bf0348082fb59ece2b5fa5`.
- **Dependencias:** 10 ruedas fijadas en `scripts/terraform_datos/requirements-ejecutor-h0316.txt`.
  - Son psycopg 3.3.4, psycopg-binary 3.3.4 (cp312 manylinux2014 x86_64), typing-extensions 4.16.0 y la cadena de
    boto3 1.43.82 / botocore 1.43.91.
  - Mismas versiones y **hashes de rueda que el lock del backend**, verificados por `pip --require-hashes` y otra vez
    por el empaquetador.
- **El empaquetador rechaza** una rueda ausente, alterada o sobrante, rutas inseguras y `.data/` distinto de `scripts/`.
  Los scripts de consola (`jmespath`) se omiten porque no son código importable.
- **Pin:** `SHA256_ESPERADO_H0316 = 02cf270dd4f2cafab5607c460e3066768fc44c53ed11c1e41e276992aff88ddf`, con 42 999 616
  bytes y 2302 entradas. Está por debajo de los 50 MiB de subida directa a Lambda.
- El pin de H-031-5 (`e27fe735…23bd`) no cambia.
- **Nota para Task/036.** Sin compresión quedan unos 7 MiB de margen. Alembic y SQLAlchemy probablemente obligarán a
  subir por S3 o a comprimir; esa decisión es de esa tarea.

**Integración local — no es AWS.** Arnés privado: `tmp/h0316/integracion/integracion.py`; evidencia:
`tmp/h0316/evidencia/integracion.json`.

- **Montaje:** red Docker **interna** con tres piezas.
  - PostgreSQL 17.11, la imagen fijada del proyecto, con TLS de una PKI desechable, solo `hostssl`,
    `log_statement=ddl` y `blogadmin` no superusuario.
  - MinIO, la imagen fijada del proyecto, versionado.
  - El **ZIP real**, extraído con sus permisos en la imagen base de Lambda python3.12 (AL2023, glibc 2.34), como
    usuario no root, con **128 MB** y el emulador de Lambda.
- **Única sustitución:** la CA de prueba en lugar del bundle de RDS.

| Escenario | Resultado |
| --- | --- |
| `selfcheck` | OK, Python 3.12 |
| `verify` de `blogadmin` con controles | OK, TLSv1.3 `TLS_AES_256_GCM_SHA384`; `sin_tls`, `host_distinto` y `ca_ajena` rechazados |
| `identidades` (creación) y relectura | OK |
| `verify` de `blog_app` | OK, `ddl_rechazado: true` |
| `sintetico` → `verify` en el alias de restaurada | La misma huella |
| `identidades` (rotación, ruta `ALTER`) | OK; clave nueva aceptada, clave vieja `AUTENTICACION_FALLIDA` |
| `export` | §46.4 |
| Payload inválido | `INVALID_PAYLOAD`, sin conexión |

**Comprobaciones:**
- respuestas y log de la función: 0 secretos, 0 hosts y 0 nombres de bucket;
- 15 líneas de contrato, todas con exactamente `contrato`, `estado` y `modo`;
- PostgreSQL: 0 contraseñas en el log, 12 conexiones TCP autorizadas y las 12 con TLS, y 1 rechazo por falta de
  cifrado;
- sin OOM con 128 MB.

**Qué no prueba:** RDS real (`rds_superuser`, CA y certificado de RDS), la VPC, IAM, el gateway endpoint ni CloudTrail.

**Pruebas Python.**

| Archivo | Pruebas |
| --- | --- |
| `test_ejecutor_h0316.py` | 43 |
| `test_empaquetar_ejecutor_h0316.py` | 17, más las 10 de H-031-5, intactas |
| `test_scram.py` | 8 |
| `test_operar_ejecutora.py` | 16 |

RED → GREEN de cada cambio en `tmp/h0316/evidencia/`.

**Errores de prueba corregidos, demostrados:**
- el vector de RFC 7677 usa una contraseña fuera de la política;
- `zipfile` en Windows normaliza `\` al escribir;
- tipos `list` frente a tupla y `map` frente a objeto en dos aserciones de Terraform.

**Custodia nueva — no cableada.** `terraform/modulos/credenciales_sql` crea dos SecureString estándar, con
`alias/aws/ssm` y `value_wo`:
- `/<prefijo>/datos/blog_migrate`;
- `/<prefijo>/datos/blog_app`.

Tienen versión independiente cada una (D-23: rotación independiente). Las contraseñas se generan en memoria en el
proceso que ejecuta Terraform, como la master.

### 46.4 H-031-6 — `export` (D-10 §10.1)

**`exportacion.py`, con `blog_migrate`.**
- **Lectura:** en **una** instantánea `REPEATABLE READ, READ ONLY`, por cada tabla de `public` (nombres
  `[a-z_][a-z0-9_]*`):
  - `SELECT count(*)`;
  - `COPY … TO STDOUT WITH (FORMAT csv, HEADER true)`.
- **Escritura:**
  - cada CSV en `exportaciones/<marca>/<esquema>.<tabla>.csv`;
  - **al final**, el manifiesto `exportaciones/<marca>/manifiesto.json`, con formato, marca y, por tabla, filas,
    bytes y SHA-256. Sin manifiesto, la exportación no cuenta.
- **Cada `PutObject`:**
  - lleva `IfNoneMatch="*"`: una exportación nunca pisa otra;
  - lleva `ChecksumSHA256`: S3 rechaza lo que no llegue íntegro.
- **Respuesta:** prefijo, manifiesto, filas por tabla y bytes. **Nunca** los datos ni el bucket.
- **Límite:** 16 MiB. Si no cabe, `EXPORTACION_DEMASIADO_GRANDE` sin escribir nada: se pide una decisión, no se
  trocea.
- **Cliente:** boto3 **fijado en el artefacto**, no el del runtime de Lambda.

**Integración con MinIO:**
- el CSV es **idéntico byte a byte** al `COPY` de `psql`, con comas, comillas, saltos de línea y tildes;
- el SHA-256 coincide con el manifiesto;
- la misma marca da `EXPORTACION_YA_EXISTE`, porque la escritura condicional se aplicó;
- un bucket inexistente da `S3_FALLIDO`.

**Permisos y red — no cableados.** `terraform/modulos/exportacion`:
- una política inline en `PersonalBlogEjecutorDatos` con **solo** `s3:PutObject` sobre `<bucket de medios>/exportaciones/*`;
- con las condiciones `s3:if-none-match = *` (la condición existe en la referencia oficial de S3) y
  `aws:SourceVpce = <gateway endpoint>`;
- la salida `sg-admin → prefix list de S3` por TCP 443.

**Controles de esa política:**
- ni el prefijo `medios/` de la aplicación, ni lectura, ni listado, ni borrado;
- el prefijo es el mismo literal que en el código, y lo exige una prueba;
- la política vive en una **plantilla** que comparten Terraform y la simulación offline.

**Pruebas.** Matriz IAM offline (`test_politicas_de_las_fases.py`): 1 positivo y 11 controles negativos.

**Responsabilidades.** `Task/040` demuestra que lo exportado es restaurable fuera de AWS (D-10 §10.1). Aquí solo
existe el modo y su permiso.

### 46.5 H-031-7 — restore sintético con PITR

**Orquestador:** `scripts/terraform_datos/restore_sintetico.py`, con 16 pruebas. El manifiesto local de cada corrida
no lleva host, cuenta ni ARN.

| Fase | Qué hace |
| --- | --- |
| `preflight` | Solo lectura: productiva `available`, retención ≥ 1, retraso de PITR ≤ 15 min, cifrada, privada; ninguna temporal previa |
| `sembrar` | Marcador por la ejecutora: id UUID, instante, huella y t0 |
| `restaurar` | **Registra el identificador** `blog-prod-restore-h0317-AAAAMMDDhhmmss` **antes de crear**. Espera a que LatestRestorableTime cubra t0 + 60 s y restaura a esa marca. Espera `available`, relee y mide. El `DbiResourceId` queda registrado en cuanto aparece la instancia |
| `verificar` | `verify` con `blog_migrate` en la restaurada: misma huella o `INTEGRIDAD_FALLIDA` |
| `limpiar` | Solo la temporal de **esta** corrida (identificador, `DbiResourceId` y etiquetas `Temporal=true` y `Proposito`), distinta de la productiva. Lista lo que borra, borra sin snapshot final ni backups, demuestra la ausencia por API, sin backups restantes y con la productiva intacta, y retira el marcador |
| `informe` | Espera hasta el PITR, restore hasta `available`, verificación y total. **RPO observado** = solicitud − instante restaurado; **RTO observado** = solicitud → verificada. Objetivos de D-10: 15 min y 4 h |

**Parámetros de la temporal.** La red y la configuración salen de la productiva:
- misma clase, subnet group, grupo de RDS y parameter group;
- `PubliclyAccessible=false`, Single-AZ;
- `BackupRetentionPeriod=0`, `DeletionProtection=false`;
- `EnableCloudwatchLogsExports=[]`, para que no nazca un grupo de logs con retención infinita;
- sin IAM DB auth;
- las etiquetas productivas, con `Gestion=manual-H-031-7`.

**Costo estimado:** una `db.t4g.micro` y 20 GiB durante menos de una hora; céntimos, contra créditos.

**Pendiente.** Todo AWS, y depende de la ejecutora (B1) para sembrar y verificar el marcador.

### 46.6 H-031-8 — alarmas de D-11

**Módulo no cableado** `terraform/modulos/alarmas_rds`:
- 8 alarmas `blog-prod-rds-<señal>`, dentro de las 10 gratuitas (Price List de us-east-2, publicación del 2026-10-07);
- dimensión `DBInstanceIdentifier`, `treat_missing_data = missing`;
- **sin acciones** (`actions_enabled = false`): SNS o correo no están aprobados.

La fuente de estadístico, periodo y puntos es la guía de AWS «Recommended alarms», sección de Amazon RDS, descargada el
2026-10-07.

| Alarma | Métrica | Estadístico | Periodo × puntos | Umbral | Justificación |
| --- | --- | --- | --- | --- | --- |
| `cpu` | CPUUtilization | Average | 60 s × 5 | > 90 % | Umbral recomendado por AWS |
| `conexiones` | DatabaseConnections | Average | 60 s × 5 | > 100 | 90 % de `max_connections` = 112 (D-12 §6.2); AWS: 90-95 % |
| `memoria` | FreeableMemory | Average | 60 s × 15 | < 256 MiB | 25 % de 1 GiB, criterio de AWS; revisar con historial real |
| `almacenamiento` | FreeStorageSpace | Minimum | 60 s × 5 | < 1 GiB | Por debajo del disparo del *autoscaling* (10 % de lo asignado): AWS desaconseja el 10 % con *autoscaling* activo (20 → 50 GiB) |
| `xid` | MaximumUsedTransactionIDs | Average | 60 s × 1 | > 1e9 | Umbral recomendado por AWS |
| `lectura` | ReadLatency | p90 | 60 s × 5 | > 20 ms | Criterio de AWS |
| `escritura` | WriteLatency | p90 | 60 s × 5 | > 20 ms | Criterio de AWS |
| `creditos` | CPUCreditBalance | Minimum | 300 s × 3 | < 29 | 10 % del máximo de 288 de una t4g.micro. **La guía no trae recomendación para RDS: confirmar con la métrica real** |

**Pruebas y mutaciones.** 2 runs; las mutaciones de umbral, acciones y estadístico se detectan.

**Hueco — decisión requerida: «fallo de backup».** RDS no publica una métrica de CloudWatch para eso; lo comunica como
**evento**. Convertirlo en alarma exige EventBridge más otro destino, servicios no aprobados. No se implementa.

### 46.7 H-031-9 — D-19 y D-20

**Gate de D-19 — no demostrado.** Hace falta información de la cuenta Grafana Cloud del usuario:
- plan real, límites y costo;
- la cuenta AWS de Grafana;
- el ExternalId del stack.

Regla de redacción de D-19: no se persisten cifras comerciales de Grafana.

**Dato de AWS verificado, que corrige la nota de Task/029 en D-19.** `GetMetricData` **se cobra siempre**: USD 0.01
por 1.000 métricas en us-east-2, según el Price List del 2026-10-07. La página de precios dice: «1 Million API requests
(not including GetMetricData, GetInsightRuleReport and GetMetricWidgetImage: these 3 operations are always charged)».

| Uso de 8 métricas | Métricas al mes | Costo bruto |
| --- | --- | --- |
| Sondeo cada 1 min | ≈ 350 000 | ≈ USD 3.50 |
| Sondeo cada 5 min | ≈ 70 000 | ≈ USD 0.70 |
| Paneles bajo demanda (≈ 100 cargas al mes) | ≈ 800 | ≈ USD 0.01 |

**Propuesta para D-19 y D-20:**
- consultas **bajo demanda** desde Grafana;
- las **alarmas de CloudWatch** (gratuitas) como fuente de alertas, sin reglas de Grafana que sondeen.

**D-20 — mecanismo. Propuesta — pendiente de aprobación.** Rol IAM asumible con ExternalId.

| Opción | Veredicto |
| --- | --- |
| Rol asumible con ExternalId | **Propuesta**: credenciales temporales; ninguna clave estática en un tercero |
| Clave IAM de solo lectura | Descartada: credencial permanente en manos de un tercero |
| *Push* (Metric Streams y Firehose) | Descartada: servicios y costo nuevos no aprobados |

**Módulo PREPARADO, no implementado:** `terraform/modulos/lectura_grafana`, rol `PersonalBlogLecturaGrafana`.
- **Confianza:** solo `arn:aws:iam::<cuenta de Grafana>:root` con `sts:ExternalId`; la cuenta de Grafana debe ser
  distinta de la del proyecto.
- **Permisos:**
  - `cloudwatch:GetMetricData` y `cloudwatch:ListMetrics`, con `aws:RequestedRegion = us-east-2`;
  - `cloudwatch:DescribeAlarms`, solo sobre `alarm:<prefijo>-*`.
- **Fuera:** `logs:*`, por los verificadores del log de PostgreSQL y R-39, y toda escritura.
- **Salidas:** solo el nombre, nunca un ARN con la cuenta.

**Pruebas.**
- 4 runs de Terraform.
- Matriz IAM offline: 3 positivos y 17 controles negativos (escrituras de CloudWatch, logs, RDS, SSM, S3, Lambda, IAM,
  STS y KMS).
- Mutaciones detectadas: sin ExternalId, con logs, todas las alarmas.

**Hallazgo y corrección.** `regex()` de Terraform es RE2 y no admite `{2,1224}`: la validación del ExternalId rechazaba
todo. Lo detectó `terraform validate`; el rango va ahora con `length()`.

### 46.8 Cableado de cada fase cuando el root pueda aplicarse

| Fase | Cambio en `terraform-datos` | Plan esperado |
| --- | --- | --- |
| H-031-5 | Ninguno: el plan revisado de §44 | 4 add, 0 change, 0 destroy |
| H-031-6 | `module "credenciales_sql"` y `module "exportacion"` (salidas `id_sg_admin`, `prefix_list_s3` e `id_endpoint_s3` de `red`; `arn_del_bucket_de_medios`). Variables efímeras de las dos contraseñas. `zip_de_la_ejecutora` con el artefacto h0316 y su pin. Laboratorio: construir el h0316 con las ruedas fijadas | 4 add (2 SecureString, política y regla) y 1 update en sitio (el código de la función) |
| H-031-7 | Ninguno: recursos temporales por API, fuera del state | — |
| H-031-8 | `module "alarmas_rds"` | 8 add |
| H-031-9 | `module "lectura_grafana"`, solo tras D-19, con cuenta de Grafana y ExternalId por variables no versionadas | 2 add |

Cada plan necesita su guarda de lista cerrada, como `check_plan_ejecutor.py`, y convergencia después del apply. Las
guardas de H-031-6, H-031-8 y H-031-9 se escriben contra el plan real de cada fase, no se adelantan contra un JSON
inventado.

> **Actualización del 2026-10-08 ([§47.3](#473-reordenamiento-de-terraform-datos)).** Por decisión del usuario,
> la ejecutora salió del root hasta la cuota, y H-031-8 y H-031-9 se cablearon y aplicaron antes que H-031-5.
> Las filas de H-031-5 y H-031-6 de esta tabla siguen siendo el plan de regreso.

### 46.9 R-12 — custodia de los respaldos locales

**Propuesta — pendiente de aprobación.**

> **Corrección y decisión del 2026-10-16 ([§48](#48-bloqueos-b1-b3-y-b4--decisiones-del-usuario-del-2026-10-16)).**
> Leer «protección activa» fue una **inferencia**. El valor 1 de ese indicador del shell no está documentado
> oficialmente y no sustituye a una verificación elevada (`manage-bde -status C:` o `Get-BitLockerVolume`).
> El usuario decidió mantener R-12 **abierto**, con seguimiento en `Task/040`. Esta propuesta queda sustituida.

**Hechos, en solo lectura:**
- `local-backups/` sigue ignorado por Git (`.gitignore:107`) y vive en el volumen C:;
- en el shell de Windows, sin administrador, `System.Volume.BitLockerProtection` de C: vale **1**, es decir,
  protección activa (cifrado de dispositivo o BitLocker);
- esto incluye las copias de 2026-07-31 a 2026-09-08 y lo que `export` descargue en el futuro (D-10 §10.1).

**Propuesta: cerrar R-12 con estas cuatro condiciones.**
1. `local-backups/` permanece ignorado por Git, en un volumen con BitLocker activo.
2. Cualquier copia fuera de ese volumen —USB o nube— se cifra con su propia clave o no se hace.
3. Los respaldos locales no son el mecanismo de recuperación de producción.
4. El estado de BitLocker se vuelve a comprobar antes de cada respaldo.

Riesgo residual aceptado: con la sesión abierta, un proceso del usuario puede leerlos.

### 46.10 Gates, seguridad y estado

**Gates offline:** `tmp/h0316/gates/`, el mismo runner de §44, que reutiliza `tmp/h0313r/gates-ma/tfdata` sin copias
nuevas de providers. Resultado: **ALL OFFLINE GATES PASSED**.

| Ámbito | Resultado |
| --- | --- |
| Terraform: 6 roots, `fmt`, `init`, `validate` y `test` | `terraform-datos` 48 (33 + 9 de H-031-6 + 2 de H-031-8 + 4 de H-031-9); `terraform-medios` 7; bootstrap 5, 9 y 7 |
| Python `terraform_datos` | 483 |
| Python `laboratorio` | 304 |
| Python `security` | 88 |
| Python `oidc` | 60, 1 omitida |
| Python `terraform_state` | 12 |
| `docker compose config` del laboratorio y `git diff --check` | OK |

**Mutaciones:** las 11 mutaciones de los módulos no cableados se detectan, cada una con su corrida de control. Por
ejemplo:
- sin escritura condicional;
- `export` con lectura o en todo el bucket;
- puertos abiertos y otra clave KMS;
- umbral de CPU, acciones habilitadas y estadístico;
- D-20 sin ExternalId, con logs o con todas las alarmas.

Evidencia en `tmp/h0316/evidencia/`. Hallazgo de método: en Windows, `terraform test -filter` exige `\`; con `/`
ejecuta 0 pruebas y sale con 0.

**Seguridad y documentación:** tabla de §46.12, con la corrida final.

**AWS:**
- **ninguna llamada mutante ni de lectura con éxito** en esta continuación;
- el único intento, una lectura de identidad, devolvió sesión caducada;
- el último readback sigue siendo el de §45.1: state en serial 8, 21/21, 0 taints y sin lock; RDS `available`;
  SecureString v1; cuota de Lambda 10;
- no se creó la Lambda ni ningún recurso, y no se repitió la solicitud de cuota.

### 46.11 Bloqueos que requieren intervención humana

| Tipo | Bloqueo | Qué falta exactamente |
| --- | --- | --- |
| Externo AWS | **B1 — cuota de concurrencia de Lambda = 10.** RC=1 (D-24) no se puede reservar, y Service Quotas solo admite pedir más de 1000. Sin la ejecutora no se aplica `terraform-datos`, y con ello todo lo de AWS de H-031-5 a H-031-9 | Una de dos: (a) autorización explícita para una vía que AWS acepte —una solicitud de más de 1000 por Service Quotas, o un caso de aumento desde Support Center—, y su aprobación por AWS; (b) una decisión que cambie D-24, no propuesta aquí. Luego: preflight de solo lectura, plan y guarda de H-031-5, apply y las fases siguientes con su plan, guarda y convergencia |
| Costo e insumo externo | **B2 — gate de D-19.** Faltan el plan, los límites y el costo reales de la cuenta Grafana Cloud del usuario, la cuenta AWS de Grafana y el ExternalId del stack. `GetMetricData` se cobra siempre | Esos datos y la decisión de uso: bajo demanda y alarmas de CloudWatch (propuesta), o sondeo con su costo. Sin D-19 no se implementa D-20 |
| Decisión arquitectónica | **B3 — fallo de *backup* sin métrica.** D-11 lo pide; RDS lo emite como evento | Elegir: aceptar el hueco con revisión manual, aprobar EventBridge → CloudWatch Logs con filtro de métrica (servicios nuevos, costo ≈ 0) u otra vía |
| Decisión arquitectónica | **B4 — R-12** | Aceptar o rechazar la propuesta de §46.9 |

**Sin bloqueos de secreto ni de IAM, y sin fallos técnicos abiertos.**

**Se consolidan con la aprobación, como propuestas:**
- el mecanismo de credenciales y los modos de provisión;
- la custodia SSM de `blog_migrate` y `blog_app`;
- los umbrales de D-11;
- el rol de D-20.

### 46.12 Seguridad y documentación

**Corrida:** la gate de §43, regenerada por `tmp/h0313r/preparar_gates_lg.py` en `tmp/h0313r/security-h0316b`, tras documentar. La
lógica de enlaces es idéntica byte a byte y el SHA-256 de la variante es `105a0461…816af`.

| Gate | Resultado |
| --- | --- |
| Gitleaks del entregable, 395 archivos | 0 hallazgos |
| Gitleaks del historial | 0 hallazgos |
| Control positivo de Gitleaks | 7 hallazgos: la herramienta detecta |
| Enlaces relativos de Markdown | 2234, **0 rotos** (176 archivos) |
| Account ID reales | 0 |
| Espacios y codificación | PASS |
| Permisos y referencias a credenciales del CI | Sin cambios |
| `git diff --check` | 0 |

**`PRODUCTION_SECRET_ABSENT`.**
- **Esta continuación no lo re-verificó por lectura**, porque no hubo sesión AWS. La búsqueda exige leer el
  SecureString en memoria.
- **Por construcción, ningún proceso de esta continuación tuvo el valor:** ni el código, ni las pruebas, ni la
  integración (contraseñas aleatorias de un solo uso, solo en memoria), ni los ZIP.
- El último resultado con el valor real es `true` (§44.8, 2026-10-06).
- La búsqueda que incluye el artefacto h0316 queda lista en `tmp/h0316/secreto.py` para la próxima ráfaga AWS.

### 46.13 Estado

- **H-031-5:** IMPLEMENTATION READY, bloqueado por la cuota (B1); sin solicitud nueva.
- **H-031-6, H-031-7 y H-031-8:** preparados offline y probados. **No COMPLETE**: les falta la evidencia de AWS
  real.
- **H-031-9:** D-19 sin verificar (B2); D-20 preparado y no implementado.
- **Cierre:** paridad, runbook, decisiones, reporte y propuesta de R-12 documentados.
- **Resultado:** `Task/031 — BLOCKERS REMAINING`.
- **Git:** sin staging, commit, push ni PR; backend y frontend intactos.

## 47. H-031-8 y H-031-9 — alarmas de D-11 y rol de D-20 aplicados y convergentes (2026-10-08 a 2026-10-15)

**Contexto.** El usuario creó su stack de Grafana Cloud y abrió la configuración manual del origen de datos
CloudWatch, que muestra:
- *Authentication Provider* «Grafana Assume Role»;
- región por omisión us-east-2;
- la cuenta AWS de Grafana y el ExternalId del stack;
- el *Assume Role ARN* pendiente, que se crea con Terraform.

Pidió continuar D-19 y D-20 con estos requisitos:
- confianza restringida a la cuenta exacta de Grafana, con `sts:ExternalId`;
- solo lectura de métricas y alarmas autorizadas, sin logs de PostgreSQL;
- ninguna modificación de AWS, ni SQL, ni secretos, ni despliegues, ni IAM;
- gestión por Terraform;
- verificación de D-19 antes de integrar.

Se mantienen los controles de REMAINDER.

**Valores del stack.** La cuenta de Grafana y el ExternalId **no se persisten en documentación**. Viven en el tfvars
privado del destino y en el runner privado.

### 47.1 Decisiones del usuario

| Fecha | Decisión | Resolución |
| --- | --- | --- |
| 2026-10-08 | Cómo desbloquear D-20 | **Reordenar `terraform-datos`.** La ejecutora sale del root hasta la cuota (módulo, artefacto, RC=1 y guarda intactos). Entran las alarmas (H-031-8) y D-20 (H-031-9). Dos applies, cada uno con plan, guarda y convergencia |
| 2026-10-08 | Método de pago en Grafana Cloud | **Ninguno registrado**: el trial no puede generar cargos al terminar |
| 2026-10-13 | `latest_restorable_time` fuera de la ventana de 24 h en el plan de H-031-8 | **Excepción puntual** solo para H-031-8 y solo para el instante del state (§47.5) |
| 2026-10-15 | Deriva `null` → `[]` de las listas de acciones de las 8 alarmas tras crearlas | **Refresh-only guardado** con guarda propia; la convergencia, con la guarda original (§47.7) |
| 2026-10-15 | Deriva de `inline_policy` y `tags` del rol de D-20 tras crearlo | **Refresh-only guardado**, el mismo patrón (§47.9) |

### 47.2 D-19 — verificación previa a integrar

| Punto | Resultado | Fuente |
| --- | --- | --- |
| Plan de Grafana Cloud | Trial de 14 días en curso (interfaz del usuario); plan objetivo Free. La página pública lo describe como gratuito y sin tarjeta. **Límites y cifras de Grafana: verificar en Task/041 / antes de contratar** (regla de redacción de D-19) | Usuario; grafana.com/pricing, consultada el 2026-10-08 |
| Cargos al terminar el trial | **No pueden producirse**: no hay método de pago | Usuario, 2026-10-08 |
| Mecanismo de autenticación | «Grafana Assume Role»: solo en Grafana Cloud, para CloudWatch. La cuenta compartida de Grafana es el *principal* y `sts:ExternalId` lo restringe al stack. Quitar la condición dejaría asumir el rol a cualquier cliente de Grafana | Documentación oficial «AWS authentication», consultada el 2026-10-08 |
| Consumo del plan de Grafana | Ninguno de ingesta: el origen de datos consulta CloudWatch en vivo, sin series ni logs almacenados en Grafana | Ídem |
| Costo AWS de la integración | `GetMetricData` **se cobra siempre**: USD 0.01 por 1.000 métricas en us-east-2, sin *free tier*. `ListMetrics` y `DescribeAlarms` entran en el millón gratuito; STS no cuesta | Price List de CloudWatch us-east-2 (2026-10-07) y página de precios (§46.7) |
| Política de uso | Paneles bajo demanda, sin *auto-refresh* agresivo; **sin reglas de alerta de Grafana sobre CloudWatch**. Las alertas son las 8 alarmas de CloudWatch, gratuitas | Esta sección |
| Estimación | Céntimos al mes con uso bajo demanda; un sondeo cada minuto de 8 métricas costaría ≈ USD 3.50 al mes y queda fuera de la política | §46.7 |
| Compatibilidad con D-13 | Sí: costo de Grafana USD 0 y costo AWS acotado por la política | — |

**Pendiente con fecha** (≈ 2026-10-22, fin del trial):
- comprobar en el portal que el stack queda en Free sin cargos;
- comprobar que «Save & test» sigue respondiendo con Grafana Assume Role;
- Task/041 revisa el consumo real de `GetMetricData` (tipo de uso `USE2-CW:GMD-Metrics`).

**Resultado: gate de D-19 para integrar SUPERADO** en costo y mecanismo, con la verificación posterior al trial pendiente.

### 47.3 Reordenamiento de `terraform-datos`

**Root.** Ningún recurso existente cambia.

| Pieza | Antes | Después |
| --- | --- | --- |
| Ejecutora de D-24 | `module "ejecutor_privado"` cableado | **Fuera del root**. En su lugar, un comentario con el contrato de regreso: `sg-admin` y subredes de `module.red`, `zip_de_la_ejecutora` con su pin, RC=1, `tests/fases_h0315.tftest.hcl` y este §47. El módulo, los artefactos h0315/h0316, RC=1 y `check_plan_ejecutor.py` no cambian |
| H-031-8 | Módulo sin cablear | `module "alarmas_rds"`, con `identificador_de_la_instancia = module.base_de_datos.identificador` |
| H-031-9 | Módulo sin cablear | `module "lectura_grafana"`: rol `PersonalBlogLecturaGrafana`, cuenta del operador, región, prefijo y `var.integracion_grafana` |
| Variables | `zip_de_la_ejecutora` | Sale. Entra `integracion_grafana` (cuenta de Grafana y ExternalId), **obligatoria, sin valor por omisión** y solo en el tfvars privado. `endpoints_aws` gana `cloudwatch` |
| Salidas | Las de la ejecutora | Salen. Entran `alarmas_de_rds` (los 8 nombres) y `rol_de_grafana`, **solo el nombre**: el ARN lleva la cuenta |

**Guardas nuevas.** Todas de lista cerrada y escritas con pruebas primero.

| Guarda | Gate | Exige |
| --- | --- | --- |
| `check_plan_alarmas.py` | `ALARMS_PLAN_OK` | Los 21 recursos en `no-op` con `before == after`. Exactamente 8 `create` del catálogo, sin acciones. Ejecutora ausente del root. Salidas existentes en `no-op` más `alarmas_de_rds`. Como mucho 10 alarmas en la cuenta. Deriva en el caso A o B de §40 |
| `check_plan_grafana.py` | `GRAFANA_ROLE_PLAN_OK` | Los 29 recursos en `no-op`. Exactamente el rol y su política en línea, con confianza y permisos exactos. Salida solo con el nombre. Deriva A/B |
| `check_plan_convergencia.py --fase` | `ACTIONABLE_CONVERGENCE_OK` | Inventario por fase: `h0313` (21), `h0318` (29) y `h0319` (31) |

**Runner privado.** Retira D-20 temporalmente, con copia y SHA-256, para que el plan de H-031-8 tenga solo las alarmas;
la prueba offline del retiro restaura los tres archivos byte a byte.

**Laboratorio (Floci).**
- Mismo root y mismos módulos.
- El endpoint `cloudwatch` es obligatorio (fail-closed).
- La integración de Grafana del laboratorio es ficticia.
- El inventario incluye las alarmas y el rol de D-20.

**Pruebas offline.** Todas en verde:
- `terraform test` de `terraform-datos`: 50 pruebas.
- Python: `terraform_datos` 514, `laboratorio` 308, `security` 88, `oidc` 60 y `terraform_state` 12.
- `docker compose config` del laboratorio y `git diff --check`: sin errores.

### 47.4 Guarda de sesión: el límite real es la sesión de rol de la consola

**Hallazgo (2026-10-09).** La guarda de margen medía mal la sesión:
- leía el `Expiration` de `aws configure export-credentials`, que es el token de 15 min y se renueva solo;
- con ese dato, el margen de 35 min no podía cumplirse nunca.

`aws login` se engancha a la sesión de rol de consola activa y caduca con ella: 1 h después del último `SwitchRole` o
`RenewRole` (MaxSessionDuration 3600). CloudTrail lo demuestra con el incidente del 2026-10-05: `RenewRole` a las
16:11:07 UTC, login a las 17:06:44 y `ExpiredToken` a mitad de apply hacia las 17:11, justo una hora después.

**Corrección.**
- `fin_de_sesion()` calcula el fin desde CloudTrail (`signin.amazonaws.com`): último `AuthorizeOAuth2Access`, último
  cambio o renovación de rol no posterior a él, más 1 h.
- Si CloudTrail aún no muestra el login, el cálculo sale anterior al real y la guarda se detiene: es conservadora.
- El margen exigido sigue en **35 min**, y ahora antes de cada fase, de **cada plan** (retiene el lock) y de cada apply.

**Intento denegado.** Para aprovechar una sesión de 24 min, el agente bajó el margen a 10/3/4 min. El clasificador de
permisos de Claude Code **denegó** la ejecución como relajación de guarda. No se ejecutó nada y el margen volvió a
35 min.

### 47.5 H-031-8 — excepción puntual de la ventana móvil (aprobada el 2026-10-13)

**Rechazo.** Primer plan del 2026-10-14: 8 `create`, 21 `no-op`, 0 `destroy`. `check_plan_alarmas` lo rechazó con
`MOVING_ATTRIBUTE`, y era la única condición que fallaba (diagnóstico offline sobre una copia en memoria). El motivo:
- el state no se escribía desde el 2026-10-05;
- `latest_restorable_time` difería 8 d 8 h entre el state (2026-10-05T19:16:49Z) y AWS, por encima de la ventana de
  24 h de §40.

**Decisión del usuario: excepción puntual** solo en la guarda de H-031-8.
- Se activa con `--excepcion-ventana-movil` y admite **solo** el instante `2026-10-05T19:16:49Z`, fijado en el código.
  Otro valor da `MOVING_EXCEPTION`.
- AWS sigue sin poder ser anterior al state ni futuro, ni tener más de 24 h.
- Cualquier otra deriva o cambio de recurso se sigue rechazando.
- El `_deriva` compartido solo gana un parámetro opcional que, por omisión, hace lo mismo que antes. La convergencia,
  H-031-9 y las demás guardas conservan la ventana de §40, y una prueba lo exige.

**Pruebas primero.**
- RED: 14 errores y 2 fallos por la razón esperada.
- GREEN: 31 pruebas de la guarda; suite `terraform_datos` con 529.
- Sobre el plan real rechazado: sin la excepción, `MOVING_ATTRIBUTE`; con ella, `ALARMS_PLAN_OK`.

El plan rechazado y su evidencia se conservan con el sufijo `rechazado-ventana`.

### 47.6 H-031-8 — apply, readback y convergencia (2026-10-15)

**Preflight.**
- Sesión: 54 min.
- Plan de cuenta: FREE / ACTIVE.
- State: serial 8, 21/21, 0 taints y sin lock.
- RDS: `available`, retención 1, privada y protegida.
- SecureString: v1.
- Ejecutora y su rol: ausentes. Cuota de Lambda: 10 (B1, sin cambios).
- Alarmas en la cuenta: 0. Rol de D-20: ausente.

**Plan nuevo y apply.**
- Plan: `8 to add, 0 to change, 0 to destroy`.
- Guarda: `ALARMS_PLAN_OK`, con `excepcion_ventana_movil = 2026-10-05T19:16:49Z` y deriva solo en
  `latest_restorable_time`.
- Apply del plan exacto: `Apply complete! Resources: 8 added, 0 changed, 0 destroyed.`
- State: **serial 9**, 29/29, 0 taints y sin lock. `PRODUCTION_SECRET_ABSENT = true`.

**Readback.**
- *Hallazgo:* el primer readback falló porque la AWS CLI de Windows escribe cp1252 fuera del modo UTF-8, y las
  descripciones llevan «§». Se comprobó en solo lectura: con `PYTHONUTF8=1` la salida es UTF-8 válida. El runner lo
  fija para todos los subprocesos.
- Relectura: **8/8 alarmas con la configuración exacta del catálogo y sin acciones**.

**Convergencia.** El plan dio `No changes` (exit 0), pero la guarda rechazó con `DRIFT`:
- las 8 alarmas cambian `alarm_actions`, `ok_actions` e `insufficient_data_actions` de `null` a `[]`;
- es normalización del provider tras crear, con la misma semántica y ninguna acción;
- la guarda de H-031-9 también la habría heredado.

### 47.7 H-031-8 — refresh-only guardado de las listas de acciones (aprobado el 2026-10-15)

**Decisión del usuario.** Un refresh-only guardado, que solo escribe el state. La convergencia y H-031-9 conservan
sus guardas originales, sin modificarlas. Hay precedente en §38 y §41.

**Guarda nueva `check_plan_refresh_alarmas.py`**, gate `ALARMS_REFRESH_OK`. Lista cerrada:
- cero `resource_changes` y cero diferidos;
- `prior_state` refrescado con 29/29 recursos y sin taint;
- las 8 alarmas, una vez cada una, con **exactamente** esas 3 listas de `null` a `[]` y el `prior_state` igual al
  valor refrescado;
- como mucho, el atributo móvil de RDS en el caso B de §40 (24 h y **sin** la excepción de §47.5);
- configuración sin la ejecutora ni D-20, y las 16 salidas en `no-op`.

**Pruebas primero.** RED: el módulo no existía. GREEN: 24 pruebas; suite `terraform_datos` con 553; `git diff
--check` limpio.

**Sesión renovada.** Hizo falta renovar la sesión de rol de la consola. Un primer intento solo repitió `aws login`
sobre la sesión anterior, y CloudTrail no mostraba ningún `SwitchRole` ni `RenewRole` nuevo. La guarda lo detectó y
no se lanzó nada. Después hubo `RenewRole` a las 03:21:30 UTC y login a las 03:21:30: la sesión acababa a las 04:21:30.

**Ejecución (`h0318-refresh`, 2026-10-15).**

| Paso | Resultado |
| --- | --- |
| Preflight | Sesión con 57 min; state en serial 9, 29/29, 0 taints y sin lock |
| Plan refresh-only guardado (archivo nuevo) | exit 2 |
| Guarda | `ALARMS_REFRESH_OK`: 0 `resource_changes` y 9 derivas, las 24 normalizaciones de las 8 alarmas más `latest_restorable_time` |
| Apply del plan exacto | `Apply complete! Resources: 0 added, 0 changed, 0 destroyed.` |
| State | Serial **9 → 10**, mismo lineage, 29/29 |
| Readback | 8/8 alarmas exactas y sin acciones; AWS no cambia |
| Convergencia con la guarda **original** | `No changes`; `ACTIONABLE_CONVERGENCE_OK` en la fase `h0318`: 29 recursos, deriva 0 |
| Secreto | `PRODUCTION_SECRET_ABSENT = true`; D-20 restaurado byte a byte |

**H-031-8: APLICADO Y CONVERGENTE.**

### 47.8 Hallazgo de calibración: alarma `memoria` en `ALARM`

Lectura del 2026-10-15, de solo lectura:
- `blog-prod-rds-memoria` está en **`ALARM`** desde su primera evaluación: `FreeableMemory` ronda 155 672 576 bytes
  (≈ 148 MiB) en 15 de 15 datapoints, por debajo del umbral de 256 MiB (25 % de 1 GiB, criterio de AWS);
- las otras 7 alarmas están en `OK`.

**Interpretación.** No es una avería: es el consumo en reposo de una `db.t4g.micro` de 1 GiB con PostgreSQL. La
alarma no tiene acciones, así que no notifica a nadie. Pero, tal como está, **no discrimina**.

**Sin cambios.** No se modifica el umbral ni el tamaño de RDS sin una decisión específica. Queda como hallazgo para
D-11: recalibrar con historial real, en la línea de la nota de §46.6.

### 47.9 H-031-9 — rol de D-20 en AWS (2026-10-15)

Se ejecutó en la misma sesión, con la guarda **original** de 24 h y sin la excepción de §47.5.

| Paso | Resultado |
| --- | --- |
| Preflight | Plan de cuenta FREE / ACTIVE; state en serial 10, 29/29; RDS y SecureString como antes; 8 alarmas del proyecto; rol de D-20 ausente |
| Variables | `integracion_grafana` escrita solo en el tfvars privado |
| Plan guardado | `Plan: 2 to add, 0 to change, 0 to destroy.` |
| Guarda | `GRAFANA_ROLE_PLAN_OK`: el rol y su política en línea, y nada más; deriva 0 |
| Apply del plan exacto | `Apply complete! Resources: 2 added, 0 changed, 0 destroyed.` |
| State | Serial **11**, 31/31, 0 taints y sin lock |
| Readback IAM | Confianza **exacta**: cuenta de Grafana y `sts:ExternalId` del stack. Path `/`, sesión de 3600 s y sin límite de permisos. Una sola política en línea, **exacta**, y ninguna adjunta |
| Simulación IAM | **20/20** como se esperaba (tabla siguiente) |

| Acción | Recurso | Decisión |
| --- | --- | --- |
| `cloudwatch:GetMetricData` y `cloudwatch:ListMetrics` | `*`, en us-east-2 | `allowed` |
| `cloudwatch:DescribeAlarms` | `alarm:blog-prod-rds-cpu` | `allowed` |
| `GetMetricData` en us-east-1; `ListMetrics` sin región | `*` | `implicitDeny` |
| `DescribeAlarms` | alarma de otro prefijo | `implicitDeny` |
| `PutMetricAlarm`, `DeleteAlarms`, `SetAlarmState` y `PutMetricData` | — | `implicitDeny` |
| `logs:GetLogEvents`, `logs:StartQuery` y `logs:FilterLogEvents` | — | `implicitDeny` |
| `rds:ModifyDBInstance`, `ssm:GetParameter`, `s3:GetObject`, `lambda:InvokeFunction`, `iam:PassRole`, `sts:AssumeRole` y `kms:Decrypt` | — | `implicitDeny` |

**Convergencia: segundo refresh-only aprobado.** El plan dio `No changes`, pero la guarda original rechazó con
`DRIFT`. En el rol:
- `inline_policy` pasa de `[]` a la política en línea, idéntica a la esperada: es el atributo calculado que refleja el
  recurso `aws_iam_role_policy`;
- `tags` pasa de `null` a `{}`.

El usuario aprobó el mismo patrón que en H-031-8. Guarda nueva `check_plan_refresh_grafana.py`, gate
`GRAFANA_ROLE_REFRESH_OK`, de lista cerrada:
- en el rol, **exactamente** esos dos atributos, con la única política esperada (nombre y contenido idénticos a
  `permisos`), sin desconocidos y coherente con el `prior_state`;
- como mucho, el atributo móvil de RDS en el caso B de §40;
- cero cambios, 31/31 sin taint y las 17 salidas en `no-op`.

Pruebas primero: RED porque el módulo no existía; GREEN con 22 pruebas. El diagnóstico offline sobre la deriva real,
en una copia en memoria con forma refresh-only, dio `GRAFANA_ROLE_REFRESH_OK` antes de lanzarlo.

| Paso (`h0319-refresh`) | Resultado |
| --- | --- |
| Preflight | Sesión con 42 min; state en serial 11, 31/31, 0 taints y sin lock |
| Plan refresh-only guardado | exit 2 |
| Guarda | `GRAFANA_ROLE_REFRESH_OK`: 0 `resource_changes`; deriva del rol (`inline_policy` y `tags`) y `latest_restorable_time` |
| Apply del plan exacto | `Apply complete! Resources: 0 added, 0 changed, 0 destroyed.` |
| State | Serial **11 → 12**, mismo lineage, 31/31 |
| Readback IAM | Confianza y política exactas |
| Convergencia con la guarda **original** | `No changes`; `ACTIONABLE_CONVERGENCE_OK` en la fase `h0319`: 31 recursos, deriva 0 |
| Secreto | `PRODUCTION_SECRET_ABSENT = true` |

**ARN.** Se entregó al usuario en la conversación para «Save & test». **No se persiste**, porque lleva la cuenta. Se
lee con el comando del [runbook](../runbooks/grafana-cloudwatch.md) §2.

**H-031-9: D-20 APLICADO, VALIDADO Y CONVERGENTE.**

**Validación manual en Grafana Cloud (resultado comunicado por el usuario el 2026-10-16).** El origen de datos
CloudWatch está configurado con «Grafana Assume Role», el ARN del rol y us-east-2. «Save & test» devolvió:

| Prueba | Resultado | Lectura |
| --- | --- | --- |
| «Successfully queried the CloudWatch metrics API» | **PASS** | **La conexión con la API de métricas queda validada desde Grafana Cloud** |
| Consulta de logs de CloudWatch | `AccessDeniedException` en `logs:DescribeLogGroups` | **Denegación prevista por D-20**: el rol no tiene `logs:*` (R-39) |

La prueba combinada sale **en rojo solo por esa denegación prevista de logs**. No se amplía ningún permiso IAM ni se
concede `logs:*`: la política sigue siendo de solo lectura de métricas y alarmas.

**CloudTrail, en solo lectura (paso 4 del runbook, 2026-10-16).**
- Hubo tres `AssumeRole` del rol: el 2026-10-15 a las 04:02:41 UTC y dos el 2026-10-16 a las 13:35:17.
- Todos vienen **de la cuenta de Grafana, con el ExternalId del stack** y sin error. Se comparó con los valores
  privados sin imprimirlos.
- Ningún otro principal asumió el rol.
- La sesión del rol recibió `AccessDenied` en `DescribeLogGroups`: es la denegación del «Save & test».

**Métricas reales de RDS en Explore: PASS** (consulta manual del usuario, comunicada el 2026-10-16).

| Parámetro | Valor |
| --- | --- |
| Origen de datos | `cloudwatch` (Grafana Assume Role) |
| Región y namespace | us-east-2, `AWS/RDS` |
| Métrica y estadístico | `CPUUtilization`, `Average` |
| Dimensión | `DBInstanceIdentifier = blog-prod-postgres` |
| Periodo y ventana | 300 s; últimas 3 horas |
| Resultado | Gráfica temporal y tabla con valores reales, entre ≈ 4.1 % y 5.2 % |

Esto **valida la ruta real Grafana Cloud → `AssumeRole` → CloudWatch → métricas de RDS**. CloudTrail registra el
`AssumeRole` correspondiente a las 13:50:35 UTC, desde la cuenta de Grafana, con su ExternalId y sin error. La
consulta respetó la política de uso de §47.2: bajo demanda, sin *dashboards*, alertas ni refresco automático.

**Estados de alarma: una validación distinta, no hecha.**
- El rol concede `cloudwatch:DescribeAlarms` solo sobre `alarm:blog-prod-*`. La simulación IAM da `allowed`, pero
  Grafana no lo ha ejercitado.
- Grafana muestra las alarmas como **anotaciones**. Según su documentación, consultada el 2026-10-16, las anotaciones
  siempre usan `cloudwatch:DescribeAlarmHistory`, y además `DescribeAlarmsForMetric` (por métrica) o `DescribeAlarms`
  (por prefijo).
- El rol **no** concede `DescribeAlarmHistory` ni `DescribeAlarmsForMetric`: la simulación de solo lectura del
  2026-10-16 da `implicitDeny` en ambas. Por tanto, las anotaciones de alarmas en Grafana **fallarían con acceso
  denegado**.
- **No se amplía nada.** Ver los estados de alarma en Grafana exigiría una decisión específica que modifique D-20.
  Mientras tanto, el estado de las 8 alarmas se consulta en CloudWatch; además, no tienen acciones.

**Queda pendiente:** la comprobación al terminar el trial (D-19).

### 47.10 Pruebas, gates y seguridad

**Gates offline:** `tmp/h0318/gates-final/`, con el mismo runner de §46 en un directorio nuevo y sin copias nuevas de
providers. Resultado: **ALL OFFLINE GATES PASSED**.

| Ámbito | Resultado |
| --- | --- |
| Terraform: 6 roots, `fmt`, `init`, `validate` y `test` | `terraform-datos` 50; `terraform-medios` 7; bootstrap 5, 9 y 7 |
| Python `terraform_datos` | **575** (514 + 15 de la excepción de §47.5 + 24 y 22 de los dos refresh-only); repetida al final: 575 OK |
| Python `laboratorio` | 308 |
| Python `security` | 88 |
| Python `oidc` | 60, 1 omitida |
| Python `terraform_state` | 12 |
| `docker compose config` del laboratorio y `git diff --check` | OK |

**Seguridad y documentación:** la gate de §43, regenerada en `tmp/h0313r/security-h0318b` y repetida con resultados
idénticos en tres momentos: tras documentar (`security-h0318c`), tras registrar «Save & test» el 2026-10-16
(`security-h0318d`) y tras registrar Explore ese mismo día (`security-h0318e`). La lógica de enlaces es idéntica byte a byte; SHA-256 de
la variante `105a0461…816af`.

| Gate | Resultado |
| --- | --- |
| Gitleaks del entregable, 406 archivos | 0 hallazgos |
| Gitleaks del historial | 0 hallazgos |
| Control positivo de Gitleaks | 7 hallazgos: la herramienta detecta |
| Enlaces relativos de Markdown | 2259, **0 rotos** (177 archivos) |
| Account ID reales | **0**: el ARN del rol no está en ningún archivo |
| Espacios y codificación | PASS |
| Permisos y referencias a credenciales del CI | Sin cambios |
| `git diff --check` | 0 |

**Hallazgo de la gate.** La primera corrida (`security-h0318a`) se detuvo por dos valores sintéticos de 12 dígitos
fuera de la lista permitida, en pruebas negativas de «otra cuenta»:
- `test_check_plan_grafana.py`, del 2026-10-08, que aún no había pasado esta gate;
- `test_check_plan_refresh_grafana.py`.

Pasaron a `000000000000`, que es de la lista permitida y distinto de las cuentas de prueba del proyecto y de Grafana.
Lo que prueba cada caso no cambia: las 32 pruebas siguen en verde.

**Higiene de la sesión:**
- una edición del reporte con `write_text` de Python lo dejó en CRLF; se restauró a LF (política `eol=lf`) y se
  comprobó que los 140 archivos cambiados están en LF;
- `PRODUCTION_SECRET_ABSENT = true` en cada fase con AWS.

### 47.11 Bloqueos que requieren intervención humana

| Tipo | Bloqueo | Qué falta exactamente |
| --- | --- | --- |
| Externo AWS | **B1 — cuota de concurrencia de Lambda = 10**, sin cambios el 2026-10-15. RC=1 (D-24) no se puede reservar. La ejecutora sigue fuera del root, con su módulo, artefacto, RC=1 y guarda intactos | Autorización explícita de una vía que AWS acepte —más de 1000 por Service Quotas o un caso de Support— y su aprobación; o una decisión que cambie D-24. Sin ella, H-031-5, H-031-6 y H-031-7 no tienen evidencia de AWS |
| Decisión arquitectónica | **B3 — fallo de *backup* sin métrica** (D-11) | Aceptar el hueco con revisión manual, o aprobar EventBridge → CloudWatch Logs con filtro de métrica (servicios nuevos, costo ≈ 0), u otra vía |
| Decisión arquitectónica | **B4 — R-12** | Aceptar o rechazar la propuesta de §46.9 |

**Pendientes con fecha o decisión, que no bloquean:**
- **D-19:** comprobar el plan Free y «Save & test» al terminar el trial (≈ 2026-10-22).
- **D-11:** calibrar `memoria` (§47.8).
- **D-20:** las métricas están validadas de extremo a extremo: «Save & test» y Explore, ambos PASS, con el
  `AssumeRole` comprobado en CloudTrail (§47.9). Ver estados de alarma en Grafana exigiría
  `DescribeAlarmHistory`/`DescribeAlarmsForMetric`, que no se conceden: solo con una decisión que modifique D-20.

### 47.12 Estado

- **H-031-8:** **APLICADO Y CONVERGENTE** (§47.6 y §47.7). D-11 sigue **Abierta**: B3 y la calibración de `memoria`.
- **H-031-9:** D-19 **verificado para integrar** (§47.2), con la comprobación posterior al trial pendiente. D-20
  **APLICADO, VALIDADO Y CONVERGENTE** (§47.9).
  - API de métricas validada desde Grafana Cloud.
  - Logs denegados por diseño.
  - `AssumeRole` solo desde la cuenta de Grafana con su ExternalId.
  - Explore con métricas reales de RDS: **PASS**, así que la ruta de métricas queda validada.
  - Estados de alarma en Grafana: no probados. Sus anotaciones requieren permisos que no se conceden.
- **State de `terraform-datos`:** serial 12, 31/31, 0 taints y sin lock.
- **AWS:** 8 alarmas sin acciones y un rol IAM con su política en línea. Ningún otro recurso. Sin cambios en RDS, red,
  SSM ni la cuota.
- **H-031-5, H-031-6 y H-031-7:** sin cambios. Preparados offline y bloqueados por B1.
- **Propuestas pendientes de aprobación:** se consolidan con el `approved`.
  - las de §46.11;
  - la excepción puntual de §47.5 y los dos refresh-only de §47.7 y §47.9, ya ejecutados con aprobación expresa;
  - el reordenamiento de §47.3.
- **Resultado:** `Task/031 — BLOCKERS REMAINING`.

## 48. Bloqueos B1, B3 y B4 — decisiones del usuario del 2026-10-16

### 48.1 Decisiones

Tras la matriz de decisión basada en documentación oficial y lecturas de AWS, el usuario autorizó lo siguiente:

| Bloqueo | Decisión |
| --- | --- |
| B1 — cuota de Lambda | **Una única** solicitud por Service Quotas: `lambda` / `L-B99A9384`, us-east-2, **1001**. Sin cambiar el plan FREE, sin soporte de pago, sin tocar D-24 ni RC=1 y sin segunda solicitud automática |
| B1 — canal | La API no admite texto de justificación. El usuario eligió **Service Quotas con caso permitido** (`SupportCaseAllowed=true`) |
| B3 — fallo de backup | **Opción A**: diagnóstico manual de solo lectura, con TDD y runbook. Sin EventBridge, SNS, métricas personalizadas ni alarmas nuevas |
| B4 — R-12 | **Abierto y documentado**, con seguimiento en `Task/040`. Los respaldos existentes no se borran, mueven, cifran ni recrean |
| D-20 | Permisos IAM sin cambios. La lectura de métricas está validada; las anotaciones de alarmas quedan fuera del alcance actual |

**Hechos verificados para B1 (2026-10-16).**
- La cuota aplicada es 10, ajustable y a nivel de cuenta; el valor por omisión es 1000.
- La guía de Lambda dice: «New AWS accounts have reduced concurrency and memory quotas […] AWS raises these quotas
  automatically based on your usage». La concurrencia reservada admite como máximo la no reservada menos 100, así que
  **RC=1 exige al menos 101**.
- Las solicitudes de aumento de cuota están «available to all AWS customers»: la cuenta solo tiene soporte Basic
  (`SubscriptionRequiredException`), y le alcanza.
- La documentación del plan FREE no menciona restricciones de cuota.
- El plan FREE termina el 2027-03-15 o al agotar los créditos (USD 135.19), y entonces la cuenta se cierra: es una
  decisión aparte (D-13).

### 48.2 B1 — solicitud de cuota

**Preflight de solo lectura (runner privado `tmp/h0318/solicitud_cuota.py`):**
- identidad `PersonalBlogAdministrator` en la cuenta esperada, en us-east-2;
- cuota aplicada 10, ajustable, de cuenta, con 1000 por omisión;
- Lambda 10/10;
- historial de la cuota vacío.

| Campo | Valor |
| --- | --- |
| Enviada | 2026-10-16 14:47:50 UTC, **una sola** llamada |
| Petición | `L-B99A9384` = **1001**, `--support-case-allowed` |
| Respuesta de la API | Aceptada: estado **`PENDING`** |
| Estado posterior | **`CASE_OPENED`** a las 14:48:11 UTC: AWS abrió un caso de soporte gratuito. El identificador está en la evidencia privada. Cuota aplicada todavía en 10 (15:02 UTC) |
| Identificador de la solicitud | `1f91578bce6f41f49a18c6069edb07a41qSpLYAn` |
| Salvaguarda | El marcador `tmp/h0318/b1-solicitud.marcador` impide un segundo envío; nunca se reintenta |

**Seguimiento (solo lectura):**

```bash
aws service-quotas get-requested-service-quota-change --request-id 1f91578bce6f41f49a18c6069edb07a41qSpLYAn \
  --profile personal-blog --region us-east-2
```

AWS abrió el caso. Con soporte Basic, la explicación solo se puede añadir **a mano desde Support Center**: es la
acción pendiente del usuario. Texto preparado:

> We need to enable a single private PostgreSQL administration Lambda function in us-east-2 with
> `reserved_concurrent_executions = 1`, used only to serialize manual administrative operations (no bulk or
> high-throughput workloads). The account concurrency limit is 10 and Lambda keeps 100 unreserved, so we cannot
> reserve 1. The default quota of 1000 (or at least 101) would allow it.

### 48.3 B3 — supervisión manual de los backups (opción A)

**Por qué solo puede ser por ausencia.** El catálogo de eventos de RDS no tiene ningún evento de «backup fallido»
para instancias. Solo hay:
- `RDS-EVENT-0001` y `RDS-EVENT-0002`, el inicio y el fin del backup;
- `RDS-EVENT-0028`, backups desactivados;
- la categoría `failure`.

En la cuenta, el par inicio/fin aparece a diario hacia las 07:12 y 07:15 UTC desde el 2026-10-05.

**Implementación.** `scripts/terraform_datos/diagnostico_backups.py`, de solo lectura con la AWS CLI en modo UTF-8:

| Comprobación | Umbral | Justificación |
| --- | --- | --- |
| Instancia | `available` | — |
| Retención | 1 día | Excepción FREE de §34; 0 significa backups desactivados |
| Último backup terminado | 26 h como máximo | Uno al día en la ventana 07:00-07:30 UTC, más la duración y el retraso de los eventos |
| Backup iniciado sin terminar | 2 h como máximo | Los observados tardan de 2 a 5 min |
| Retraso de `LatestRestorableTime` | 15 min como máximo | Objetivo de RPO de D-10 |
| Eventos `0028` o `failure` | Ninguno en 14 días | Es lo que guarda RDS |

- **Datos ausentes:** sin eventos o sin `LatestRestorableTime`, el resultado es FALLO, nunca OK.
- **Códigos de salida:** 0 OK; 1 FALLO; 3 error de AWS o de la CLI, sin repetir su mensaje; 4 credenciales
  caducadas; 5 identidad no autorizada.
- **Privacidad:** nunca imprime cuentas ni ARN.

**Pruebas primero.**
- RED: el módulo no existía. Hubo que corregir un error de la propia prueba: comparaba 8 elementos con una lista de 7.
- GREEN: **25 pruebas**, entre ellas:
  - positivas y límites exactos;
  - negativas: instancia, retención, sin eventos, antigüedad, atasco, desactivación, fallo, PITR y reloj;
  - errores de la CLI: código reconocido, desconocido, CLI ausente y salida ilegible;
  - cuatro formas de credenciales caducadas;
  - identidad;
  - la cuenta nunca en la salida.
- REFACTOR: los umbrales del informe salen de las constantes.

**Ejecución real (2026-10-16 14:48 UTC): OK, salida 0.**
- Instancia `available`, retención 1.
- Último backup terminado a las 07:15:15 UTC, hace 7,5 h.
- `LatestRestorableTime` con 6,3 min de retraso.
- 30 eventos, sin hallazgos.

Evidencia en `tmp/h0318/evidencia/b3-diagnostico-real-2026-10-16.json`. Operación en el
[runbook de supervisión de backups](../runbooks/rds-backup-supervision.md).

**Límites aceptados.** No avisa a nadie: detecta solo cuando se ejecuta. La alternativa automática (EventBridge →
Logs → filtro de métrica → alarma) queda como mejora posterior y requiere su propia aprobación.

### 48.4 B4 — R-12 abierto y documentado

| Control | Estado |
| --- | --- |
| Ignorado por Git | **Demostrado**: `.gitignore:107` |
| Ausente del historial | **Demostrado**: 0 commits con `local-backups`; Gitleaks del historial, 0 hallazgos |
| Fuera de OneDrive | **Demostrado**: `Downloads` no está redirigido; OneDrive solo sincroniza `Documentos` |
| BitLocker | **Pendiente de verificación elevada** (`manage-bde -status C:`) |
| Custodia de otras copias | **No demostrada**: hace falta la confirmación del usuario |
| Comprobar el cifrado antes de generar o trasladar respaldos | **Regla manual**, no automatizada |

Inventario: 80 archivos de 2026-07-31 y de 2026-09-06 a 08, todos del entorno **local**.

La lectura de §46.9 («protección activa») fue una inferencia: el valor 1 del indicador del shell no está documentado
oficialmente. Se anotó la corrección en §46.9, en la ficha y en STATUS. Detalle operativo en el
[runbook de respaldos locales §3.2](../runbooks/local-backup-and-recovery.md#32-custodia-y-estado-de-r-12).

### 48.5 H-031-5 — preparación offline, sin crear recursos

| Pieza | Cambio | Pruebas |
| --- | --- | --- |
| `check_plan_ejecutor.py` | Línea base REAL tras H-031-9: estado previo de **31** recursos y **17** salidas en `no-op`. Los inventarios se importan dentro de la función para evitar un ciclo de importación | RED: `PRIOR_STATE` con la línea base nueva. GREEN: 31 pruebas, entre ellas «la línea base de H-031-3 ya no basta» y «las alarmas y el rol de D-20 no pueden cambiar» |
| `check_plan_convergencia.py` | Fase **`h0315`**: 35 recursos | RED: fase desconocida. GREEN: los conjuntos de cada fase, convergencia y rechazos |
| `check_plan_refresh_ejecutor.py` (nueva) | Refresh-only de la ejecutora, preparado ANTES del apply (lección de §47.7 y §47.9). Solo dos formas: `null` → `[]` / `{}` y el reflejo `inline_policy` idéntico a la política del state. Más el caso B de RDS | RED: el módulo no existía. GREEN: 20 pruebas. Se corrigió una prueba que trataba la política de la ejecutora como un recurso ajeno |
| Recableado (`tmp/h0318/cablear_ejecutora.py`) | El cableado exacto del contrato de regreso: la llamada, `zip_de_la_ejecutora` y las dos salidas | Offline: `init`, `validate` y `fmt` en 0 y restauración byte a byte |

**Pendiente al recablear de verdad:**
- las corridas de `datos.tftest.hcl` con el ZIP y la ejecutora;
- el laboratorio: construir el artefacto e inventariarlo;
- la fase del runner (preflight con concurrencia sin reservar de al menos 101).

**Corrección menor:** en `variables.tf`, la cabecera de la ejecutora quedaba sobre `integracion_grafana`.

### 48.6 Pruebas, gates y seguridad

**Gates offline:** `tmp/h0318/gates-b1b3b4/`, el mismo runner de §47.10, sin copias nuevas de providers. Resultado:
**ALL OFFLINE GATES PASSED**.

| Ámbito | Resultado |
| --- | --- |
| Terraform: 6 roots, `fmt`, `init`, `validate` y `test` | `terraform-datos` 50; `terraform-medios` 7; bootstrap 5, 9 y 7 |
| Python `terraform_datos` | **622**: 575, más 25 del diagnóstico de B3, 2 de la línea base de la ejecutora y 20 del refresh-only de la ejecutora |
| Python `laboratorio` | 308 |
| Python `security` | 88 |
| Python `oidc` | 60, 1 omitida |
| Python `terraform_state` | 12 |
| `docker compose config` del laboratorio y `git diff --check` | OK |

**Seguridad y documentación:** la gate de §43, en `tmp/h0313r/security-h0318f` y, tras completar esta sección, en
`security-h0318g`, con resultados idénticos. La lógica de enlaces es idéntica byte a byte; SHA-256 de la variante
`105a0461…816af`.

| Gate | Resultado |
| --- | --- |
| Gitleaks del entregable, 411 archivos | 0 hallazgos |
| Gitleaks del historial | 0 hallazgos |
| Control positivo de Gitleaks | 7 hallazgos: la herramienta detecta |
| Enlaces relativos de Markdown | 2277, **0 rotos** (178 archivos) |
| Account ID reales | **0** |
| Espacios y codificación | PASS; todos los archivos cambiados en LF |
| Permisos y referencias a credenciales del CI | Sin cambios |
| `git diff --check` | 0 |

**AWS, todo de solo lectura salvo la solicitud de cuota:**
- state en serial 12, 31/31, sin taints ni lock (lectura del 2026-10-16);
- diagnóstico de B3 en OK;
- la solicitud quedó en `CASE_OPENED`, con la cuota aplicada todavía en 10.

### 48.7 Condiciones restantes para H-031-5, H-031-6 y H-031-7

1. **AWS concede una concurrencia de al menos 101.** La solicitud está en `CASE_OPENED`. Sin esto no hay RC=1, y D-24 y
   RC=1 no cambian.
2. **H-031-5:**
   - recablear y completar las pruebas y el laboratorio (§48.5);
   - preflight y plan con `EXECUTOR_PLAN_OK`;
   - apply;
   - readback de RC=1, `sg-admin` y la red;
   - refresh-only con `EXECUTOR_REFRESH_OK` si el provider normaliza;
   - convergencia `--fase h0315`.
   Requiere la autorización del apply y sesiones con 35 min de margen.
3. **H-031-6:**
   - cablear `credenciales_sql` y `exportacion`;
   - actualizar el código al artefacto h0316;
   - escribir su guarda contra el plan real (§46.8);
   - ejecutar `identidades`, `verify` con TLS `verify-full` y `export`.
4. **H-031-7:**
   - marcador sintético por la ejecutora;
   - PITR a una instancia temporal y verificación;
   - limpieza autorizada e informe de RPO/RTO.
   Costo: una `db.t4g.micro` temporal durante unos minutos. **No verificado:** si el plan FREE admite el restore.
   Riesgo de `FreeTierRestrictionError`, como en §32.

### 48.8 Desviaciones respecto de los criterios de aceptación originales (ficha §6)

| Criterio | Estado | Desviación o pendiente |
| --- | --- | --- |
| 1. Red y RDS privados | Cumplido (H-031-3) | `sg-admin` se adjunta con H-031-5: pendiente (B1) |
| 2. TLS | `rds.force_ssl = 1` y CA registrados | La conexión `verify-full` desde un cliente real queda para H-031-6 (B1) |
| 3. Cifrado `aws/rds` | Cumplido | — |
| 4. Contraseña master ausente | Cumplido | `PRODUCTION_SECRET_ABSENT = true` en cada fase |
| 5. Backups | **Desviación** | Retención de **1 día**, no 7: excepción temporal del plan FREE (§34). PITR activo y `LatestRestorableTime` avanzando, demostrado por el diagnóstico de B3 |
| 6. Identidad operativa mínima | **Desviación** | Por decisión del usuario (§24) se opera con `PersonalBlogAdministrator` y la identidad de datos no se configura |
| 7. Restore sintético y PITR | **Pendiente** | No demostrado: depende de la ejecutora (B1) |
| 8. CloudWatch D-11 y D-20 | Cumplido con desviaciones | 8 alarmas **sin acciones** (SNS no aprobado). Fallo de backup **sin alarma**: supervisión manual (B3). `memoria` en `ALARM` en reposo: calibración pendiente. D-20 **solo métricas**: anotaciones de alarmas fuera del alcance. D-19: comprobación al terminar el trial pendiente |
| 9. Convergencia 0/0/0 y paridad | Cumplido en H-031-3, H-031-8 y H-031-9 | Con la excepción puntual de la ventana móvil (§47.5) y dos refresh-only aprobados (§47.7 y §47.9). Paridad sin declararse completa |

**Orden de las fases:** H-031-8 y H-031-9 se aplicaron antes que H-031-5, por la decisión del 2026-10-08 (§47.3).

### 48.9 Estado

- **B1:** solicitud enviada y caso abierto por AWS (**`CASE_OPENED`**). Falta que el usuario añada la explicación
  en Support Center. H-031-5, H-031-6 y H-031-7 siguen sin evidencia de AWS.
- **B3:** resuelto por decisión del usuario (opción A), implementado con TDD y con la ejecución real en OK.
- **B4:** resuelto por decisión del usuario: R-12 sigue **abierto**, documentado, con seguimiento en `Task/040`.
- **AWS:** la única acción fue la solicitud de cuota. Sin applies, sin cambios de infraestructura ni del plan de la
  cuenta. State sin cambios (serial 12, 31/31).
- **Resultado:** `Task/031 — BLOCKERS REMAINING`. **No** es READY FOR USER APPROVAL: faltan las pruebas productivas
  de H-031-5, H-031-6 y H-031-7, que dependen de B1.

## 49. D-24 modificada y plan de H-031-5 (2026-10-18)

Decisión del usuario del 2026-10-18 para desbloquear la ejecutora privada. Todo lo decidido aquí es una **Propuesta —
pendiente de aprobación**. No hubo apply, staging, commit, push, PR ni merge. H-031-8 y H-031-9 no se repitieron. La
solicitud de cuota a 1001 sigue abierta: no se canceló ni se presentó otra.

### 49.1 Decisiones del usuario

| Decisión | Contenido |
| --- | --- |
| **D-24 simplificada** | La ejecutora sigue siendo una Lambda privada, pero con concurrencia **no reservada**: ni RC=1 ni RC=0, y sin concurrencia provisionada. Red privada, TLS, IAM mínimo, credenciales, VPC, subredes, grupos y protecciones de RDS intactos. Invocación manual y autenticada; sin Function URL, API Gateway, SQS, DynamoDB, NAT ni servicios nuevos |
| **Exclusión en la aplicación** | Un bloqueo de aviso de PostgreSQL para las operaciones SQL administrativas críticas. Requisitos: la misma conexión toda la operación; rechazo de una segunda operación incompatible; liberación al terminar o al cerrarse la conexión; ninguna reejecución destructiva tras un error; sin restricciones innecesarias a los modos de lectura. **No** se presenta como protección de operaciones de AWS |
| **Contrato móvil de §40** | Respuesta del usuario: «Cambiar el contrato §40». Se conserva «valor de AWS no anterior al del state ni posterior a ahora». El límite de 24 h pasa a medir la **frescura del valor de AWS** (PITR vivo) en lugar de la antigüedad del state. Con TDD; las demás condiciones no cambian |
| **Cuota** | La solicitud a 1001 sigue abierta y deja de ser requisito. Ni cancelarla ni presentar otra |
| **Sin apply** | El usuario revisará primero el plan completo |
| **Plan real de H-031-5** (2026-10-19) | Autorización «H-031-5 REAL PLAN ONLY»: preflight de solo lectura, el runner preparado, plan guardado sin aplicar, guarda `EXECUTOR_PLAN_OK` y evidencias en §49.7 y §49.8. Sin apply, refresh-only, untaint, import ni escrituras del state o de AWS; sin tocar la cuota ni el caso de soporte |

### 49.2 Cambios y justificación

| Pieza | Cambio | Justificación |
| --- | --- | --- |
| `terraform/modulos/ejecutor_privado/main.tf` | `reserved_concurrent_executions = 1` eliminado. El atributo se omite a propósito, y AWS lo informa como `-1` | RC=1 exige una concurrencia no reservada de al menos 101 («You can reserve up to the Unreserved account concurrency value minus 100»), y la cuenta tiene 10. `0` apagaría la función; la provisionada es costo fijo sin necesidad |
| `codigo_h0316/operaciones.py` | `_exclusion(cursor)`: `set_config` local de `statement_timeout` = 20 s e `idle_in_transaction_session_timeout` = 60 s, y después `pg_try_advisory_xact_lock(3364, 1)`. Es la primera sentencia de la transacción de `identidades` y de `sintetico`; si la clave está ocupada, `Fallo("OPERACION_EN_CURSO")` | La exclusión pasa de Lambda a PostgreSQL (§49.3) |
| `scripts/terraform_datos/operar_ejecutora.py` | El cliente de Lambda usa `total_max_attempts = 1` y `read_timeout = 70` s; la función tiene 30 s | Con el modo `standard`, botocore reintenta los errores transitorios y los *timeouts* de lectura. Una invocación síncrona reintentada sería una **reejecución** |
| `scripts/terraform_datos/restore_sintetico.py` | `_clientes()` devuelve los del operador | El orquestador de restore hereda la misma política sin reintentos |
| `scripts/terraform_datos/empaquetar_ejecutor.py` | Pin h0316 nuevo: `98f41bfd…8e43`, 43 001 155 bytes. El anterior, `02cf270d…8ddf` (42 999 616 bytes), queda anotado. El pin h0315, `e27fe735…23bd`, no cambia | El código h0316 cambió. Determinismo comprobado con dos construcciones idénticas antes de fijarlo |
| `terraform-datos`: `main.tf`, `variables.tf` y `outputs.tf` | Vuelve la llamada `module "ejecutor_privado"` con el contrato de regreso del 2026-10-08: solo `sg-admin`, las dos subredes de `module.red`, la cuenta del operador y la variable `zip_de_la_ejecutora` (`{ruta, sha256}`, sin valor por omisión). Salidas `nombre_de_la_ejecutora` y `arn_de_la_ejecutora`, no sensibles | La cuota deja de bloquear: la ejecutora vuelve al root sin cambiar su diseño |
| `check_plan_ejecutor.py` | Exige `reserved_concurrent_executions == -1` (`CONCURRENCY`). El resto, sin cambios: 31 recursos en `no-op`, exactamente 4 `create`, pin, red, IAM exacto, salidas y deriva A/B | Adaptar la guarda al contrato nuevo sin relajar secretos, deriva, recursos existentes ni destrucciones |
| `check_plan_refresh_instancia.py` (`instante_movil`) | La ventana de 24 h mide `ahora - AWS` en lugar de `AWS - state` (§49.4) | Decisión del usuario |
| Laboratorio (`scripts/laboratorio/laboratorio.py`) | Construye el artefacto, comprueba el pin, declara `zip_de_la_ejecutora` e inventaria la función, su grupo de logs y los dos roles de datos | El laboratorio sigue al root |
| Pruebas | Las que exigían RC=1 exigen `-1` o la ausencia del atributo. Más pruebas de exclusión, de no reejecución, del cableado y de §40 (§49.5) | Con TDD |
| Documentación | D-24 modificada como Propuesta: decisiones §8.2 y tabla resumen, fuente de la ley, `open-decisions` (fila y sección), runbook, identidad operativa, paridad, ficha (criterio 10, riesgo y deuda), STATUS, ROADMAP y STAGE-10 | Registro explícito de la modificación y de su criterio de aceptación |

**Hallazgo.** La fila original de D-24 contaba con «el bloqueo de aviso propio de Alembic». Ese control **no existe**:
el `alembic/env.py` del backend no toma ningún bloqueo de aviso (verificado el 2026-10-18). Por eso el criterio de
aceptación nuevo lo hereda `Task/036` para `upgrade`, `downgrade` y `purge`.

### 49.3 Exclusión mutua: diseño y límites

- **Clave única de escrituras administrativas: `(3364, 1)`.** 3364 = `0x0D24`, por D-24; 1 es la clase de las
  escrituras administrativas. Todas las escrituras críticas son incompatibles entre sí y comparten la clase.
- **Misma conexión, primera sentencia.** El bloqueo se toma dentro de la transacción que escribe, antes de escribir.
  La ejecutora abre una sola conexión por invocación y no tiene *pool*.
- **Sin espera.** `pg_try_…` no hace cola ni crea *deadlocks*. Una segunda operación responde `OPERACION_EN_CURSO`
  sin haber escrito nada.
- **De transacción.** Lo liberan `COMMIT`, `ROLLBACK` o el fin de la sesión. No hay `pg_advisory_unlock` que olvidar.
  Si la función muere a mitad, el servidor termina la sesión inactiva en transacción a los 60 s como máximo y el
  bloqueo se libera.
- **Sin reejecuciones.** El operador hace un único intento síncrono y Lambda no reintenta las invocaciones síncronas.
  `OPERACION_EN_CURSO` y cualquier error son finales: se investigan y nunca se repiten a ciegas.
- **Lectura sin bloqueo.** `verify` y `export` no lo toman: leen datos confirmados (MVCC) y no se restringen.
- **Lo que no protege.** Las operaciones de AWS: restore, PITR, *snapshots*, modificación o borrado de instancias.
  Conservan sus protecciones: las guardas del orquestador de restore (§46), la protección contra borrado de la
  productiva y la identidad que las ejecuta. El bloqueo solo ordena SQL dentro de una instancia.
- **En H-031-5 no interviene.** H-031-5 despliega el *shell* h0315, que no conecta con PostgreSQL. El bloqueo llega
  con el código h0316 en H-031-6, y antes de ese despliegue no puede haber escrituras.

### 49.4 Contrato del atributo móvil (§40) enmendado

| | Antes | Desde el 2026-10-18 (Propuesta) |
| --- | --- | --- |
| Condición | `state ≤ AWS ≤ ahora` y `AWS − state ≤ 24 h` | `state ≤ AWS ≤ ahora` y `ahora − AWS ≤ 24 h` |
| Qué mide la ventana | La antigüedad del state | La frescura del valor de AWS: PITR vivo |

**Por qué.** El state no se escribe desde la convergencia de H-031-9 (serial 12). Cualquier plan de hoy vería una
diferencia de varios días entre el state y AWS y saldría `MOVING_ATTRIBUTE` sin que nada estuviera mal: la misma
situación que obligó a la excepción puntual de §47.5. La antigüedad del state no es una propiedad de seguridad. La
frescura del valor de AWS sí lo es: si los *backups* se detienen, `latest_restorable_time` deja de avanzar y, pasadas
24 h, toda guarda rechaza el plan.

**Alcance.** Todas las guardas que importan `instante_movil`: convergencia, ejecutora, alarmas sin la excepción,
D-20 y los tres refresh-only. La excepción de §47.5 no cambia: queda como historia y es más estricta que el contrato
nuevo, porque además exige el instante aprobado. Se mantiene todo lo demás: instantes válidos y con zona, no nulos,
AWS no anterior al state, nada en el futuro, sin tolerancia de *clock skew* y el resto de atributos con igualdad
exacta.

### 49.5 Pruebas con TDD

| Cambio | RED, por la razón esperada | GREEN |
| --- | --- | --- |
| Exclusión mutua (`test_ejecutor_h0316`, clase `ExclusionMutua`, 5 pruebas) | 3 fallos y 2 errores: sin `pg_try_advisory_xact_lock`; `identidades` y `sintetico` escribían con la clave ocupada | 48/48 |
| Sin RC (`check_plan_ejecutor`, `test_modulo_ejecutor_privado` y `fases_h0315.tftest.hcl`) | `CONCURRENCY` en los positivos; el atributo seguía en el módulo; `terraform test` 1 de 2 | 71/71; `terraform test` 2/2 |
| Operador sin reintentos (`SinReinvocaciones`) | El cliente no existía con esa configuración | 17/17 |
| Restore con los clientes del operador (`ClientesSinReinvocaciones`) | El orquestador construía sus propios clientes e importaba `boto3` | 17/17 |
| Cableado del root (`CableadoDesdeElRoot` y `datos.tftest.hcl`) | No existía el bloque `module "ejecutor_privado"`; `terraform test` con «Reference to undeclared module» | 14/14. La primera corrida tuvo 1 fallo de la propia prueba: buscaba la subcadena `count`, que aparece en `account_id`; corregida con un regex de línea. `terraform test` 51/51 |
| Laboratorio (`test_ejecutora_en_el_laboratorio`) | `KeyError: 'zip_de_la_ejecutora'` y un solo rol de datos en el inventario | 14/14; suite del laboratorio 311 |
| §40 (`ContratoDeFrescura`, 8 pruebas, más 2 por cada guarda afectada) | 18 de 200: 8 `MOVING_ATTRIBUTE` con un state antiguo y AWS fresco, y 10 «no se lanzó» con AWS de más de 24 h, más el CLI de las alarmas | 200/200 en las nueve suites de guardas |
| Regresión de §40 | 6 errores: tres archivos con reloj del 2026-10-08 usaban el valor de AWS por omisión del 2026-10-05, que con el contrato nuevo describe un PITR parado. Se les dio un valor fresco respecto a su reloj; la intención de cada prueba («el caso B pasa») no cambió | **`terraform_datos`: 644 OK** |

**Pruebas modificadas porque cambió el requisito.** Las que exigían RC=1 y las que fijaban la semántica anterior de
§40: `test_delta_mayor_de_24h`, `test_drift_movil_mayor_de_24h_rechazado`, `test_atributo_movil_fuera_de_24_h`
(ejecutora y D-20), `test_atributo_movil_fuera_de_24_h_sin_excepcion` (alarmas),
`test_sin_la_excepcion_la_ventana_de_24_h_sigue_rechazando` y el CLI de las alarmas. Cada una se sustituyó por la
pareja «state antiguo con AWS fresco pasa» y «AWS de más de 24 h se rechaza». Ninguna se relajó para acomodar el
código. La REFACTOR no hizo falta: el cambio es una sola expresión.

### 49.6 Integración real con PostgreSQL

Con el artefacto h0316 exacto (`98f41bfd…8e43`), PostgreSQL 17.11 y MinIO locales, y la imagen base de Lambda, sin
AWS:

| Escenario | Resultado |
| --- | --- |
| `selfcheck` e `identidades` inicial | OK |
| Otra sesión sostiene `(3364, 1)`: `identidades` y `sintetico` | `OPERACION_EN_CURSO`, sin escribir: el marcador no se sembró |
| Con la clave ocupada: `verify` (como `blogadmin` y como `blog_migrate`) y `export` | OK: la lectura no se restringe |
| Tras el `COMMIT` de la otra sesión | `identidades` y `sintetico` OK |
| La otra sesión se termina con la clave tomada | Liberada al cerrarse la sesión; `identidades` OK después |
| Error a mitad (`PERMISO_DENEGADO` sin `CREATEROLE`) | Clave libre tras el error; tras restaurar el permiso, OK |
| Bloqueos de aviso al final | 0 |

### 49.7 Red sin NAT: dependencias de la ejecutora

Inventario del código: h0315 no tiene clientes de red (`selfcheck` no abre conexiones). En h0316 hay dos: psycopg
contra el endpoint de RDS y `boto3` S3, solo en `export`. No hay llamadas a STS, SSM, KMS ni Secrets Manager:
las credenciales llegan en el evento y la CA va dentro del ZIP. Los logs los entrega el servicio Lambda, no la ENI.

| Dependencia | Fase | Vía en la VPC | Configuración |
| --- | --- | --- | --- |
| Ninguna | H-031-5 (h0315) | — | ENI de Lambda en las subredes privadas con `sg-admin` |
| PostgreSQL 5432 | H-031-6 | Ruta `local` | `sg-admin → sg-rds:5432` y `sg-rds ← sg-admin`; DNS de la VPC activo; RDS no pública |
| S3 (`export`) | H-031-6 | Gateway endpoint: prefix list → `vpce` en las dos tablas | Falta `sg-admin → S3:443`, que añade el módulo `exportacion` en H-031-6. Su ausencia en H-031-5 es deliberada y está probada |

**Verificación en AWS, de solo lectura (2026-10-19, fase `red` del runner privado): VERIFICADA.**

| Comprobación | Resultado |
| --- | --- |
| VPC | `enableDnsSupport` y `enableDnsHostnames` activos |
| Tablas de rutas | 3 en la VPC: las 2 privadas y la principal. Ninguna ruta a `0.0.0.0/0` ni `::/0`, ni a NAT, IGW, EIGW, *transit gateway* o *peering*. Cada tabla privada lleva solo `local` y el prefix list de S3 hacia el gateway endpoint, y está asociada solo a su subred |
| Salida a Internet | 0 IGW, 0 NAT y 0 EIGW en la VPC |
| Endpoint de S3 | Uno solo: `Gateway`, `com.amazonaws.us-east-2.s3`, `available`, en las 2 tablas privadas, sin subredes ni grupos |
| `sg-admin` | Exactamente una regla: salida TCP 5432 → `sg-rds`. Sin entradas y sin `sg-admin → S3:443`, que añade H-031-6 |
| `sg-rds` | Exactamente dos entradas TCP 5432, desde `sg-admin` y desde `sg-lambda`, y ninguna salida |
| `sg-lambda` | Salidas a `sg-rds:5432` y al prefix list de S3 por 443, como en H-031-3 |
| Subredes | 2, sin IP pública al lanzar ni IPv6, con 4090 y 4091 direcciones libres para la ENI |
| NACL | La por omisión, que permite el tráfico en ambos sentidos |
| RDS | No pública, solo `sg-rds`, en las 2 subredes, puerto 5432. Su endpoint resuelve a 1 dirección dentro de `10.40.0.0/16` |

**Conclusión:** sin NAT ni salida a Internet, la ejecutora alcanza por la VPC todo lo que usa:
- nada en H-031-5;
- PostgreSQL por la ruta local en H-031-6;
- S3 por el gateway endpoint en `export`, cuando H-031-6 añada la regla de salida.

### 49.8 Plan guardado de H-031-5

**Autorización del usuario: «Task/031 — H-031-5 REAL PLAN ONLY».** Se ejecutó el 2026-10-19 con
`python -B tmp/h0320/fase_h0315.py plan`, sin apply, refresh-only, untaint, import ni ninguna escritura del state o
de AWS. La única escritura en el backend fue el bloqueo nativo propio de todo plan, tomado y liberado.

1. **Sesión.** STS respondió como `assumed-role/PersonalBlogAdministrator` en la cuenta esperada y en us-east-2.
   CloudTrail tardó unos minutos en mostrar el nuevo cambio de rol: la sonda de solo lectura esperó, y la fase empezó
   con **57 min** de margen (mínimo 35). Antes del plan quedaban 55.
2. **State remoto.** Serial 12, 31/31, 0 taints, sin `.tflock`.
3. **Red:** verificada (§49.7).
4. **Preflight:**
   - plan de cuenta FREE/ACTIVE hasta el 2027-03-15, con 134.12 USD de créditos;
   - RDS `available`, retención 1, privada y protegida, y SSM en la versión 1;
   - la ejecutora, su rol y su grupo de logs, **ausentes**.
5. **Artefacto.** El ZIP h0315 copiado al directorio privado con su pin y declarado en `zip_de_la_ejecutora` del
   tfvars privado.
6. **`init` y `validate`:** OK.
7. **Plan guardado:** exit 2, `Plan: 4 to add, 0 to change, 0 to destroy.`
8. **Guarda:** `check_plan_ejecutor` → **`EXECUTOR_PLAN_OK`**.
9. **State después del plan:** el mismo serial, lineage y SHA-256, sin `.tflock`. El plan no lo escribió.
10. **Secreto:** `PRODUCTION_SECRET_ABSENT = true`. Se revisaron 4 *buffers* en memoria y 24 439 archivos, sin
    ninguna coincidencia.

| Artefacto | SHA-256 |
| --- | --- |
| Plan guardado `h0315.tfplan` (privado) | `c440ded886a56875ab2d75c47196be8623c0bc2c98a906e3634bfd778da61bcb` |
| JSON del plan (privado) | `c83bdaf5010297a43a63d7151a672ca59e7a3277c86d2844e043f1db3bca1e5b` |
| ZIP h0315 que se despliega | `e27fe7354fbbb616693cd7ba59eb20cad2dcf902b98be6df11b2016fe1e723bd` |
| State remoto, antes y después del plan | `ff720e83ccc44eb4a684f5e65afca534f61ee6b93c8278ca4fb6ec1fc2c35ba8` |

**Contenido del plan:**
- Terraform 1.16.2; `applyable`, `complete`, sin errores ni diferidos.
- 35 checks en `pass`, incluida la identidad.
- La variable efímera no aparece en el plan.

| Aspecto | Resultado |
| --- | --- |
| Recursos existentes | **31 en `no-op`** |
| Recursos nuevos | **4 `create`** (tabla siguiente) |
| Cambios, destrucciones y reemplazos | **0, 0 y 0** |
| Salidas | 17 en `no-op` y 2 nuevas: `nombre_de_la_ejecutora` y `arn_de_la_ejecutora`, no sensibles |
| `resource_drift` | Caso B: solo `latest_restorable_time` de RDS, de `2026-10-15T03:31:48Z` (state) a `2026-10-19T00:41:48Z` (AWS), unos 10 min antes del plan. **Con el contrato anterior de §40 este plan habría salido `MOVING_ATTRIBUTE`**: la diferencia entre el state y AWS era de 3 d 21 h |

| Recurso | Valores del plan |
| --- | --- |
| `aws_cloudwatch_log_group` | `/aws/lambda/blog-prod-ejecutor`, 14 días, sin KMS, etiqueta `Name` |
| `aws_iam_role` | `PersonalBlogEjecutorDatos`, ruta `/`, 3600 s, sin *boundary*. Confianza: solo `lambda.amazonaws.com` con `sts:AssumeRole` |
| `aws_iam_role_policy` | `PersonalBlogEjecutorDatos-ejecucion`. `Allow` de las 6 acciones de ENI. `Deny` de esas 6 y de `ec2:DetachNetworkInterface` cuando `lambda:SourceFunctionArn` es la propia función. `Allow` de `logs:CreateLogStream` y `logs:PutLogEvents` solo en los *streams* de su grupo |
| `aws_lambda_function` | `blog-prod-ejecutor`, `python3.12`, `x86_64`, `ejecutor.manejar`, 128 MB, 30 s, `publish = false`, ZIP. **`reserved_concurrent_executions = -1`**. Entorno vacío, sin capas ni KMS. `source_code_hash` igual al pin h0315. `vpc_config`: 1 grupo (`sg-admin`), 2 subredes, sin IPv6. `depends_on` del grupo de logs y de la política |

**Hallazgo informativo: la cuota de Lambda ya es 1000.**
- `get-account-settings` devolvió `ConcurrentExecutions = 1000` y `UnreservedConcurrentExecutions = 1000`; el
  2026-10-16 eran 10.
- No se consultó el estado de la solicitud ni del caso de soporte: no estaba autorizado.
- D-24 modificada sigue como Propuesta. RC=1 vuelve a ser técnicamente posible (§49.14).

### 49.9 Riesgos residuales aceptables para un blog personal

| Riesgo | Por qué es aceptable | Mitigación |
| --- | --- | --- |
| Dos escrituras administrativas simultáneas | La segunda se rechaza sin efectos; las invocaciones son manuales y esporádicas | `OPERACION_EN_CURSO`; repetirla a mano solo tras comprobar que la primera terminó |
| Lectura concurrente con una escritura | MVCC: la lectura ve datos confirmados | Ninguna necesaria |
| La función muere con la transacción abierta | El bloqueo y la transacción se liberan en 60 s como máximo | `idle_in_transaction_session_timeout` |
| Un error transitorio exige reinvocar a mano | Es el precio de no reejecutar nunca de forma automática | Diagnóstico por la salida saneada y el runbook |
| La ejecutora comparte la concurrencia no reservada de la cuenta: 10 hasta el 2026-10-16 y **1000** el 2026-10-19 | Con 1000 el *throttling* es casi imposible, y sería visible (`TooManyRequestsException`), nunca silencioso | Reintento manual |
| Lambda ya no limita el número de conexiones de la ejecutora | Las invocaciones son manuales, síncronas y de una identidad autorizada: en la práctica, una a la vez. Con la cuota de 1000 el límite de la cuenta ya no acota nada | El rechazo inmediato de las escrituras por el bloqueo; `max_connections` de RDS como techo |
| El bloqueo no cubre operaciones de AWS | Nunca se presentó como tal | Las guardas del restore, la protección contra borrado y la identidad |

**Para tareas futuras, sin bloquear `Task/031`:**
- `Task/036` debe tomar `(3364, 1)` en `upgrade`, `downgrade` y `purge`, porque Alembic no aporta bloqueo propio.
- `Task/032`: D-12 propone RC=20 para la Lambda de aplicación. Con la cuota de 10 era imposible; con la de 1000
  observada el 2026-10-19 cabe, hasta 900 reservables. Esa tarea lo confirmará con `get-account-settings`.

**Riesgos del apply de H-031-5:**
- **Propagación de IAM al crear la función.** La función depende de la política y del grupo de logs, y el provider
  reintenta los errores de propagación. Si aun así fallara, quedaría un apply parcial de 3 de 4 recursos: STOP, sin
  reintento, y plan nuevo.
- **Normalizaciones del provider tras crear** (`null` → `[]` o `{}`). Son previsibles y `check_plan_refresh_ejecutor`
  está preparada, pero el refresh-only exige autorización.
- **Validez del plan guardado.** Solo vale mientras el state siga en el serial 12 con la misma huella y el ZIP privado
  no cambie. La contraseña efímera se vuelve a pasar en el apply.
- **Costo:** la función y su grupo de logs, con uso esporádico, quedan dentro del *free tier*.

### 49.10 Estado de H-031-5 a H-031-7

| Fase | Estado |
| --- | --- |
| **H-031-5** | **DESPLEGADA Y CONVERGENTE** el 2026-10-19 (§49.15): apply exacto, *readback*, `selfcheck`, refresh-only preautorizado y convergencia 0/0/0 |
| **H-031-6** | Preparado offline: artefacto h0316 `98f41bfd…8e43` con el bloqueo e integración local real. Faltan H-031-5 aplicado, el cableado de `credenciales_sql` y `exportacion`, su guarda y la autorización |
| **H-031-7** | Preparado offline. Depende de H-031-6. Costo de una `db.t4g.micro` temporal y riesgo **no verificado** de que el plan FREE rechace el restore (`FreeTierRestrictionError`, §32) |

### 49.11 Bloqueos reales

1. ~~Sesión y autorización del apply de H-031-5~~: resueltos el 2026-10-19 (§49.15).
2. ~~Decisión sobre D-24 y §40~~: aprobadas por el usuario el 2026-10-19; se consolidan con la aprobación de la tarea.
3. **Después de H-031-5:** H-031-6 (cableado, guarda y apply) y H-031-7 (restore con el riesgo del plan FREE).

Ya **no** son bloqueos: la cuota de Lambda (solicitud abierta y no requerida; la cuota aplicada ya es 1000), B3 y B4
(§48).

### 49.12 Pruebas, gates y seguridad

**Gates offline:** `tmp/h0320/gates-d24/`, el mismo runner de §47.10 y §48.6, sin copias nuevas de providers. Resultado:
**ALL OFFLINE GATES PASSED**, 32 de 32.

| Ámbito | Resultado |
| --- | --- |
| Terraform: 6 roots, `fmt`, `init`, `validate` y `test` | `terraform-datos` 51, con la ejecutora cableada; `terraform-medios` 7; bootstrap 5, 9 y 7 |
| Python `terraform_datos` | **644**: 628 tras los cambios de D-24 (622 de §48.6 más 6) y 16 más de §40 |
| Python `laboratorio` | 311 |
| Python `security` | 88 |
| Python `oidc` | 60, 1 omitida |
| Python `terraform_state` | 12 |
| `docker compose config` del laboratorio y `git diff --check` | OK |

**Seguridad y documentación:** la gate de §43, en `tmp/h0313r/security-h0320a` y, tras completar esta sección, en
`security-h0320b`, con resultados idénticos. La lógica es idéntica byte a byte a la de §48.6; SHA-256 de la variante
`105a0461…`.
Tras documentar el plan real (§49.7 y §49.8), la misma gate en `security-h0320c` y `security-h0320d`: 2292
enlaces, 0 rotos y el resto idéntico.

| Gate | Resultado |
| --- | --- |
| Gitleaks del entregable, 411 archivos | 0 hallazgos |
| Gitleaks del historial | 0 hallazgos |
| Control positivo de Gitleaks | 7 hallazgos: la herramienta detecta |
| Enlaces relativos de Markdown | 2291, **0 rotos** (178 archivos) |
| Account ID reales | **0** |
| Espacios y codificación | PASS; todos los archivos cambiados en LF |
| Permisos y referencias a credenciales del CI | Sin cambios |
| `git diff --check` | 0 |

### 49.13 Estado

- **Código, pruebas y documentación:** completos y en verde offline (§49.12).
- **AWS:** solo lecturas, el plan guardado y su bloqueo nativo. Ningún apply ni escritura del state: serial 12 con la
  misma huella antes y después.
- **Resultado:** `Task/031 — H-031-5 DEPLOYED + CONVERGENT` (§49.15). **No** es READY FOR USER APPROVAL: faltan las
  pruebas productivas de H-031-6 y H-031-7.

### 49.14 Recomendación para el despliegue de H-031-5

**GO técnico**, con estas condiciones en la autorización del apply:
1. **Aplicar el plan EXACTO** `h0315.tfplan` (`c440ded8…61bcb`), tras comprobar tres cosas: el state sigue en el
   serial 12 con la huella `ff720e83…35ba8`, el ZIP privado conserva su pin y la sesión tiene 35 min de margen. Si
   algo cambió: STOP y plan nuevo.
2. **Después del apply:**
   - *readback* de la función (`Active`, sin concurrencia reservada, solo `sg-admin` y las dos subredes), del rol, de
     la política y del grupo de logs;
   - convergencia con `check_plan_convergencia --fase h0315`, sobre 35 recursos.
3. **Preautorizar el refresh-only guardado** (`check_plan_refresh_ejecutor` → `EXECUTOR_REFRESH_OK`) por si el
   provider normaliza atributos al crear, como en H-031-8 y H-031-9. Sin esa autorización, la convergencia se
   detendría y haría falta otra ronda.
4. **Opcional:** una invocación síncrona `selfcheck`, que prueba el contrato y la ENI sin tocar la base de datos.

**NO-GO** si el state, el ZIP o la sesión no cumplen el punto 1, o si el usuario prefiere volver a RC=1 ahora que la
cuota es 1000.

**Sobre RC=1, decisión del usuario.** Con la cuota de 1000 vuelve a ser posible, pero no es necesario:
- la exclusión real la da el bloqueo de PostgreSQL en los dos diseños;
- RC=1 serializaría también `verify` y `export`, y el usuario pidió no restringir la lectura.

Recomiendo **mantener la D-24 modificada**. Si se rechazara más adelante, `reserved_concurrent_executions` se cambia
en sitio, sin reemplazar la función, con un plan y una guarda nuevos.

### 49.15 Aprobación de D-24 y §40 y apply de H-031-5 (2026-10-19)

**Decisiones del usuario del 2026-10-19** («APPROVE D-24 / §40 + H-031-5 EXACT APPLY»):
- **Modificación de D-24, aprobada:**
  - Lambda privada sin concurrencia reservada (`-1`);
  - exclusión con bloqueos de aviso de PostgreSQL en las escrituras administrativas;
  - protecciones propias para PITR, restores y demás operaciones fuera de PostgreSQL;
  - invocaciones manuales, autenticadas y sin reintentos automáticos.

  Aunque la cuota ya es 1000, **no** se vuelve a RC=1 en esta fase.
- **Nueva semántica de §40, aprobada.** Las demás guardas de deriva no se relajan ni admiten otros atributos.
- Las dos decisiones se consolidan con la aprobación de `Task/031`.
- **Apply EXACTO autorizado** del plan `c440ded8…61bcb`, con sus condiciones. Además, un refresh-only guardado
  preautorizado, solo para las normalizaciones conocidas y con `EXECUTOR_REFRESH_OK`.

**Sesión.** Los `aws login` de las 01:36Z y 01:43Z se engancharon a la sesión de rol de consola de las 00:45:52Z y
caducaron con ella a las 01:45:52Z: STS falló a las 01:47:00Z. Tras el nuevo cambio de rol del usuario, STS volvió a
responder a las 01:48:34Z, pero CloudTrail entregó el evento del rol a las 01:50:40Z. Hasta entonces, la sonda usaba
el RenewRole anterior y **subestimaba** el margen. La fase empezó con 56 min de margen, sobre un mínimo de 35.

**Fase `apply`** (`python -B tmp/h0320/fase_h0315.py apply`, de las 01:50:44Z a las 01:59:50Z):

| Paso | Resultado |
| --- | --- |
| STS y sesión | `PersonalBlogAdministrator`, cuenta esperada, us-east-2; 56 min de margen |
| State antes | Serial 12, 31/31, 0 taints, sin lock y con el SHA-256 autorizado `ff720e83…` |
| Red | Verificada de nuevo, igual que en §49.7 |
| Preflight | Igual que en §49.8: FREE/ACTIVE, RDS, SSM, ausencias y cuota de 1000 |
| Plan autorizado | SHA-256 `c440ded8…` exacto; el JSON derivado, idéntico (`c83bdaf5…`); el ZIP y el tfvars del pin; `EXECUTOR_PLAN_OK` 4/0/0 |
| Apply | Con 55 min de margen: `Apply complete! Resources: 4 added, 0 changed, 0 destroyed.` La función tardó 3 min 12 s por las ENI Hyperplane |
| State después | Serial 14, mismo lineage, 35/35, 0 taints, sin lock |
| *Readback* de la función | `Active` y `Successful`, con el código del pin y sin concurrencia reservada; solo `sg-admin` en las 2 subredes. Sin URL, política de recurso, disparadores, configuración asíncrona, versiones ni alias |
| *Readback* de IAM, logs y red | Rol, confianza y política exactos, sin políticas administradas. Grupo de logs a 14 días. 2 ENI Hyperplane privadas, solo con `sg-admin` |
| `selfcheck` | Una invocación síncrona, sin reintentos del SDK: `StatusCode 200`, sin `FunctionError`. Respuesta EXACTA del contrato `d24-ejecutor-h0315-v1`, y su línea de log visible. Sin conexiones ni PostgreSQL |
| Convergencia | Plan «No changes», exit 0. La guarda lo rechazó con `DRIFT`: las normalizaciones previstas |
| Refresh-only preautorizado | Plan exit 2, con 0 `resource_changes` y `EXECUTOR_REFRESH_OK`, que admitió 3 derivas (tabla siguiente). Apply: 0 added, 0 changed, 0 destroyed. State en serial 15, mismo lineage |
| *Readback* tras el refresh-only | Idéntico |
| Convergencia final | «No changes», exit 0: **`ACTIONABLE_CONVERGENCE_OK` 0/0/0, caso A (sin deriva), fase `h0315`** |
| Secreto | `PRODUCTION_SECRET_ABSENT = true`: 15 *buffers* y 25 337 archivos, sin coincidencias |

Derivas que admitió el refresh-only:

| Recurso | Atributo | Cambio |
| --- | --- | --- |
| Rol de la ejecutora | `inline_policy` | De `[]` al reflejo idéntico de su política |
| Función | `layers` | De `null` a `[]` |
| RDS | `latest_restorable_time` (atributo móvil) | De las 00:41:48Z a las 01:51:53Z |

| Plan posterior al apply | SHA-256 |
| --- | --- |
| Convergencia | `6f33aff5461a8d1c99e6408d59a92fa7d5dc80aa819e94a5e0e8043b43aacad6` |
| Refresh-only | `25dcf24035b0ae876ae6d900a0644edd298d4866168082e81c899cd56a831e2e` |
| Convergencia tras el refresh-only | `e280ee96b6fbb74167d6a997b7b67ff16121272072718cb5db0eaf032f5ba22a` |

En el log del runner, la redacción de identificadores de cuenta enmascaró un tramo de 12 dígitos de este último hash.
Se recalculó del archivo y no contiene la cuenta.

**Criterios de la ficha:**
- el criterio 1 queda completo: H-031-5 adjunta `sg-admin`, leído de la API;
- el criterio 9 suma una convergencia 0/0/0 más.

**Resultado: H-031-5 DESPLEGADA Y CONVERGENTE.** La ejecutora existe como *shell* sin base de datos. El bloqueo de
PostgreSQL y los modos que usan la base de datos llegan con el código h0316 en H-031-6.

## 50. Trabajo de Codex retomado, laboratorio completo y preparación de H-031-6 y H-031-7 (2026-10-19 y 2026-10-20)

Instrucción del usuario: retomar Task/031 desde el *working tree* que dejó Codex al agotar su límite, sin descartar
nada. Prioridades:
1. resolver el fallo del ciclo completo del laboratorio sin relajar controles de deriva injustificadamente;
2. repetir las gates;
3. preparar el plan real guardado de H-031-6 sobre la línea base de 35 recursos, sin aplicar;
4. dejar H-031-7 listo para una autorización consolidada.

Sin apply, refresh-only ni restore productivos, sin cambios de recursos de AWS, y sin staging, commit, push, PR ni
merge. H-031-5, H-031-8 y H-031-9 no se repitieron.

### 50.1 Punto de partida: lo que hizo Codex

Codex trabajó el 2026-10-18 entre las 20:27 y las 20:47, hora local, sobre las pruebas RED de H-031-6 de esta misma
sesión. Su evidencia está en `tmp/h0316-codex/`.

| Pieza | Trabajo de Codex |
| --- | --- |
| Root y módulos | Cableado de `credenciales_sql` y `exportacion`; contraseñas efímeras y versiones; salida `nombres_de_credenciales_sql`; salidas `nombre_del_rol` de la ejecutora y `configuracion_efectiva` de `exportacion`; descripción de la función neutral de fase |
| Guardas | `check_plan_h0316.py` (lista cerrada: 35 en `no-op`, 4 `create` y 1 `update` en sitio del código); `check_plan_refresh_h0316.py` (solo dos transiciones: el reflejo `inline_policy` del rol de 1 a 2 políticas y el `egress` de `sg-admin` con la regla nueva); fase `h0316` de la convergencia (39) |
| Operador y restore | Cliente de RDS sin reintentos; restore con registro previo a cada escritura, paginación, detección de una productiva reemplazada o de una temporal recreada y borrado idempotente (8 pruebas nuevas) |
| Laboratorio | Artefacto h0316 copiado de `PERSONAL_BLOG_EJECUTOR_ZIP` con su pin, tres canarios y tres SecureString de datos; alarmas admitidas en la revisión del plan |
| Pruebas | Con RED y GREEN en `tmp/h0316-codex/red-*.txt`. Sus 32 gates pasaron a las 20:36 |
| AWS | Una lectura del state remoto: serial 15, 35/35, sin taints ni lock |

**El ciclo completo del laboratorio falló dos veces:**
1. la revisión del plan no admitía `aws_cloudwatch_metric_alarm` (Codex lo corrigió);
2. el segundo plan del root de datos traía deriva no declarada, y ahí se detuvo.

### 50.2 Revisión del trabajo de Codex: dos falsos positivos que habrían bloqueado el plan real

Se conserva el diseño. Se corrigieron dos defectos de `check_plan_h0316.py`, contrastados con planes REALES:

| Defecto | Forma real | Efecto con el plan real | Corrección |
| --- | --- | --- | --- |
| `_sin_secretos` exigía `value = null` en todo SecureString | Con `value_wo`, el provider deja `value = ""` en el state: la master del plan real de H-031-5 lo tiene, comprobado solo por longitud | `SECRET_IN_PLAN` en cualquier plan con la master | Solo `""` o `null`; `value_wo` e `insecure_value`, estrictamente `null`. Un valor no vacío sigue rechazándose (prueba nueva). Es la regla de `check_plan.py` desde H-031-2 |
| La política de `export` solo admitía `id` desconocido | En el plan real de H-031-5, un `aws_iam_role_policy` nuevo traía `name_prefix` desconocido | `UNVERIFIABLE` | `name_prefix` pasa a la lista cerrada de calculados |

**RED y GREEN:**
- con las formas reales en el *fixture*, 34 pruebas dieron 47 fallos de subprueba y 3 errores, todos por
  `SECRET_IN_PLAN`;
- ese control se evalúa antes y ocultaba el segundo defecto, que se demostró aislado: con la forma real, la regla
  anterior da `UNVERIFIABLE` y la nueva la acepta;
- GREEN: 42/42 entre la guarda, sus límites, el refresh-only y la convergencia.

El primer defecto también lo arrastraba la fase `h0316` de la convergencia, que usa la misma función: el fallo se
habría repetido después del apply. Lo compartía además el *fixture* de esta sesión. La lección es que los fixtures
copian formas de planes reales.

**Sin regresión:** el JSON REAL de la convergencia de H-031-5 sigue dando `ACTIONABLE_CONVERGENCE_OK` 0/0/0 con el
código actual.

**Riesgo operativo encontrado:**
- El laboratorio reutiliza el directorio del root y deja `terraform-datos/backend.generado.tf` con `backend "local"`.
- La producción usa su propio `TF_DATA_DIR` privado (S3, key de datos, `us-east-2`, `encrypt`, lock nativo), pero el
  bloque `backend` vive en ese archivo compartido.
- Con `local`, un `init` productivo falla de forma segura.
- El runner de H-031-6 regenera `backend "s3" {}` y verifica la metadata antes de operar, como prescribe el runbook
  para el root de medios.

### 50.3 Laboratorio: causa y corrección del fallo del ciclo completo

**Causa.** Desde H-031-1A, el gate de idempotencia del root de datos acepta `resource_drift` solo por declaración
exacta: dirección, acciones, atributos y forma de la transición. Los recursos de H-031-8, H-031-9, H-031-5 y H-031-6
nunca habían pasado un ciclo completo, así que nadie había declarado su deriva.

**Diagnóstico sobre el JSON real del plan que detuvo el ciclo:** 16 entradas de deriva y 13 cambios planificados.

| Entrada | Transición | Naturaleza | Evidencia |
| --- | --- | --- | --- |
| 8 alarmas (deriva) | `alarm_actions`, `ok_actions` e `insufficient_data_actions`: `null → []` | Representación del provider | La misma en AWS real (§47.7) |
| Rol de la ejecutora (deriva) | `inline_policy`: `[] →` reflejo de sus 2 políticas del state | Provider | AWS real (§49.15). Comprobado en el JSON real: reflejo idéntico en nombre y contenido |
| Función (deriva) | `layers`: `null → []` | Provider (SDKv2) | AWS real (§49.15) |
| Rol de Grafana (deriva) | Reflejo de su política y `tags`: `null → {}` | Provider | AWS real (§47.9) |
| 8 alarmas (cambio) | `datapoints_to_alarm` 0 → N; `extended_statistic` en las p90 | **Floci** | `DescribeAlarms` directo contra el emulador: no devuelve `DatapointsToAlarm` en ninguna ni `ExtendedStatistic` en las p90. AWS sí (*readback* 8/8 de H-031-8) |
| RDS, *parameter group*, grupos y SSM `key_id`/`tier` | — | Ya declaradas en H-031-1 y H-031-1A | — |

**Corrección, con la misma estrechez de H-031-1A:**
- dos formas nuevas en `scripts/laboratorio/inventario.py`, cada una con el antes y el después fijos:
  - `refleja_politicas_en_linea`: `[]` → EXACTAMENTE las políticas en línea que el `prior_state` asigna a ese rol,
    por nombre y contenido. Es la misma idea que `agrega_reglas_separadas` para los grupos;
  - `nulo_a_mapa_vacio`;
- 11 declaraciones de deriva por dirección y 2 diferencias del destino por tipo y atributo, cada una con su motivo y
  su origen;
- **ningún control productivo cambia**: la convergencia productiva sigue exigiendo deriva 0, y nada viaja a los
  módulos como `ignore_changes`.

**TDD:**
- *fixture* `tests/laboratorio/drift_observado_h0316.py`: la estructura del JSON real, con ID sintéticos;
- `tests/laboratorio/test_drift_h0316.py`: 14 pruebas. RED: 14. GREEN: 14;
- los controles negativos fallan por la razón correcta: un atributo de más, una política ajena o alterada, una lista
  de acciones no vacía, otras etiquetas o un cambio planificado no declarado;
- **el JSON real del plan que detuvo el ciclo** pasa ahora el gate completo: 16/16 derivas y 12 clases de diferencia,
  con su recuento exacto.

**Ciclo real contra Floci 2.1.0:** `bajar` limpio, `levantar` (aislamiento demostrado) y `ciclo`. El primer intento
cayó por la codificación de la consola (`UnicodeEncodeError` en cp1252, antes de cualquier apply); con
`PYTHONUTF8=1`:

| Etapa | Resultado |
| --- | --- |
| Apply | Medios 8, **datos 39** (con H-031-6 y la ejecutora h0316) y aplicación 13 |
| Funcional | S3, SSM, IAM y Lambda; `GET /health` por HTTP real; imagen real del runtime; CloudWatch Logs |
| Idempotencia | Medios exit 0. **Datos exit 2 solo por lo declarado**: 12 clases de diferencia y 16 entradas de deriva. Aplicación sin cambios |
| Deriva controlada | SSM ficticio retirado y reconciliado |
| Dos destroys y una reconstrucción | Ausencia comprobada por API (0 recursos en los states); *smoke* de la reconstrucción HTTP 200 |
| Canarios | Ausentes en el plan, el state y las salidas |
| Resultado | **`CICLO COMPLETO`**, exit 0 |

### 50.4 Operador: la sesión de `aws login` exige `botocore[crt]`

La fase `preflight` de H-031-7 falló con `MissingDependencyException`: el proveedor de credenciales de `aws login`
de botocore 1.43.91 exige su extra `crt`, que fija `awscrt==0.36.0`. Sin él, ninguna fase de AWS del operador ni del
orquestador del restore puede autenticarse.

**Corrección:**
- `awscrt==0.36.0` se fija en `requirements-operador.txt` con los SHA-256 de las ruedas abi3 de Windows y Linux;
- la de Windows se descargó a un directorio aislado y su SHA-256 coincidió con el de la API JSON de PyPI;
- licencia Apache-2.0; solo la usa el operador: no va en el artefacto;
- prueba `tests/terraform_datos/test_requisitos_del_operador.py` (RED → GREEN, 3/3).

**Comprobación real, de solo lectura:** el `preflight` de H-031-7 dio OK.
- Productiva disponible, cifrada y privada, con retención 1.
- Retraso del PITR: 329 s, con un objetivo de 900.
- Ninguna temporal previa.

**Otras lecturas de solo lectura del 2026-10-19:**
- cuotas de RDS: instancias 1/40, almacenamiento 20/100 000 GiB, *snapshots* manuales 0/100;
- las credenciales SQL no existen; el rol tiene solo `-ejecucion`; `exportaciones/` está vacío;
- PITR activo con ventana de 24 h; ningún *snapshot* manual;
- **CloudTrail: 0 trails**, así que ningún selector de datos de Lambda registra los *payloads*. Este paso estaba
  pendiente desde §46.10.

### 50.5 H-031-7: reanudar sin un segundo restore

**Problema.** La sesión de `aws login` vive lo que la sesión de rol de la consola, como mucho 1 h. Un PITR a una
`db.t4g.micro` tarda minutos. Si la sesión caducaba durante la espera:
- `restaurar` daba `TEMPORAL_YA_REGISTRADA`;
- `verificar` exigía `t_disponible` y daba `SIN_RESTAURADA`;
- si el corte llegaba antes de registrar el `DbiResourceId`, `limpiar` se negaba a borrar la temporal, que se quedaba
  facturando hasta una intervención manual.

**Contrato nuevo de `restaurar`.** Nunca hay un segundo restore. `t_solicitud` se guarda ANTES de la llamada a la
API.

| Situación | Comportamiento |
| --- | --- |
| Solicitud registrada y temporal presente, con el mismo identificador, sus etiquetas y el `DbiResourceId` registrado | Reanuda la espera, registra el `DbiResourceId` si faltaba y completa el *readback*. Queda `reanudado: true` |
| Solicitud registrada y temporal ausente | `RESTAURACION_INCIERTA`: lo decide una persona |
| Temporal con otras etiquetas u otro `DbiResourceId` | `RESTAURADA_NO_CONFORME` |
| Corte antes de pedir el restore (sin `t_solicitud`) | Continúa: no salió ninguna solicitud |
| Otro identificador o una restauración ya completa | `IDENTIFICADOR_NO_ADMITIDO` o `TEMPORAL_YA_REGISTRADA` |

**TDD:** `tests/terraform_datos/test_restore_reanudacion.py`, 7 pruebas.
- RED de las 6 primeras: 4 fallos y 1 error, por la razón esperada. La de una restauración completa ya pasaba.
- La séptima, el corte antes de pedir el restore, se añadió antes del GREEN. Su RED se demostró después contra la
  lógica anterior reconstruida literalmente: fallan 3 de 3.
- GREEN, con la regresión del restore completa: 32/32.

### 50.6 Decisiones aprobadas

El usuario aprobó el 2026-10-19 la modificación de D-24 y la semántica nueva de §40 (§49.15).
- Las notas de la documentación y los comentarios de `scripts/`, `tests/` y los `.tf` quedaron como «aprobada».
- Se consolidan con la aprobación de `Task/031`.
- Se conservan dos menciones a propósito:
  - el comentario de `codigo_h0316/operaciones.py`, porque cambiarlo cambiaría el pin del artefacto ya integrado y
    probado;
  - la «Propuesta» del mecanismo de credenciales (§46.2), que sigue pendiente.
- No se tocó la descripción del rol de la ejecutora: es un atributo desplegado y cambiaría el plan.

### 50.7 Pruebas, gates y seguridad

**Gates offline:** `tmp/h0320/gates-h0316-final/`, el mismo runner de §48.6 y §49.12, ejecutado sobre el código ya
final. Resultado: **ALL OFFLINE GATES PASSED**, 32 de 32. Una primera corrida en `gates-h0316/` también pasó, pero el
restore cambió mientras corría y por eso se repitió.

| Ámbito | Resultado |
| --- | --- |
| Terraform: 6 roots, `fmt`, `init`, `validate` y `test` | `terraform-datos` 54; `terraform-medios` 7; bootstrap 5, 9 y 7 |
| Python `terraform_datos` | **711** |
| Python `laboratorio` | **329** |
| Python `security` | 88 |
| Python `oidc` | 60, 1 omitida |
| Python `terraform_state` | 12 |
| `docker compose config` del laboratorio y `git diff --check` | OK |

**Seguridad y documentación:** la gate de §43, en `tmp/h0313r/security-h0320e` y, tras completar esta sección, en
`security-h0320f`, con resultados idénticos.

| Gate | Resultado |
| --- | --- |
| Gitleaks del entregable, 424 archivos | 0 hallazgos |
| Gitleaks del historial | 0 hallazgos |
| Control positivo de Gitleaks | 7 hallazgos: la herramienta detecta |
| Enlaces relativos de Markdown | 2307, **0 rotos** (178 archivos) |
| Account ID reales | **0** |
| Espacios y codificación | PASS; todos los archivos cambiados en LF |
| Permisos y referencias a credenciales del CI | Sin cambios |
| `git diff --check` | 0 |

### 50.8 H-031-6: plan real guardado — VERIFICADO el 2026-10-20

**Resultado (02:52:35Z): `H0316_PLAN_OK`, `Plan: 4 to add, 1 to change, 0 to destroy.`** Sin apply. El detalle y la
sesión, en §50.12. Antes, la sesión de AWS había caducado: la sonda de solo lectura del 2026-10-20 a las 00:32Z
devolvió «STS fallo».

**Para renovarla, en este orden:**
1. **Switch back** y **Switch role** a `PersonalBlogAdministrator` en la consola;
2. después, `aws login --profile personal-blog --region us-east-2`.

Un `aws login` sin un cambio de rol nuevo se engancha a la sesión de consola anterior y caduca con ella. Pasó el
2026-10-19.

**Runner preparado:** `python -B tmp/h0320/fase_h0316.py plan`. Es privado, no tiene ruta de apply y se detiene ante
el primer fallo.
1. Sesión con 35 min de margen.
2. Backend: regenera `backend "s3" {}`, hace el `init` en el `TF_DATA_DIR` privado y verifica la metadata.
3. State: serial 15, 35/35, sin taints ni lock; deja registrada su huella.
4. Red de solo lectura, con las comprobaciones de §49.7 sobre la línea base de 35: `sg-admin` todavía SOLO hacia
   `sg-rds`.
5. Preflight:
   - plan FREE/ACTIVE y RDS conforme;
   - la master en v1 y las dos credenciales AUSENTES;
   - el rol con solo `-ejecucion`;
   - la función `Active` con el código h0315 y sin reserva;
   - `exportaciones/` vacío.
6. Artefacto h0316 copiado al directorio privado con su pin; `zip_de_la_ejecutora` apunta a él.
7. Secretos: la master se lee de SSM en memoria. Las contraseñas de `blog_migrate` y `blog_app` del PLAN son
   desechables y se generan en memoria (§25.4: el plan no depende del valor *write-only*).
8. Plan con exit 2 → **`check_plan_h0316` → `H0316_PLAN_OK`** con 4/1/0.
9. `terraform show` legible y resumen saneado; el state queda intacto; búsqueda de los tres valores.

**Plan esperado:**
- 34 recursos en `no-op` y la función en `update` en sitio: el código pasa al pin h0316 (`98f41bfd…8e43`), y cambian
  también `filename` y `description`;
- **4 `create`:**
  - `/blog-prod/datos/blog_migrate` y `/blog-prod/datos/blog_app`: SecureString estándar con `alias/aws/ssm`,
    `value_wo` en la versión 1;
  - la política `PersonalBlogEjecutorDatos-exportacion`: solo `s3:PutObject` en `exportaciones/*`, con
    `If-None-Match` y solo por el gateway endpoint;
  - la regla `sg-admin → S3:443` por la prefix list;
- 0 destrucciones;
- las 19 salidas actuales en `no-op` y una nueva, `nombres_de_credenciales_sql`;
- deriva en el caso A o B.

### 50.9 Autorización consolidada propuesta para H-031-6 y H-031-7

Se pide DESPUÉS de revisar el plan real de §50.8. Cada paso que modifica algo exige 35 min de sesión al empezar y se
detiene ante cualquier desviación, sin reintentos a ciegas.

**Fase A — H-031-6 en AWS:**

| Paso | Qué hace | Recursos y costo |
| --- | --- | --- |
| A1. Apply exacto | Del `h0316.tfplan` revisado: SHA-256 `8d1a73078720e7a697d71f25648d4b83fdaf3753b16624d3d3fa0b0371b57a6d` (§50.12). Exige el state con la huella del plan, el ZIP con su pin y `H0316_PLAN_OK`. Las contraseñas REALES de `blog_migrate` y `blog_app` se generan en memoria en ese momento; su única custodia es SSM (`value_wo`) | 4 recursos y el código de la función. Costo fijo **0**: SSM estándar, IAM y la regla no tienen cargo |
| A2. *Readback* | SSM: tipo, nivel, clave, versión 1 y coincidencia **booleana** con los valores en memoria. Política y regla exactas. Función `Active` con el pin h0316 y sin reserva. `selfcheck` con el contrato `d24-ejecutor-h0316-v1` | Solo lectura y 1 invocación |
| A3. Convergencia | `--fase h0316`, 39 recursos. Refresh-only guardado (`H0316_REFRESH_OK`), solo si hace falta y preautorizado: los dos reflejos (rol de 1 a 2 políticas y `sg-admin` con una regla más) y el atributo móvil | Escribe solo el state |
| A4. SQL por la ejecutora | `identidades` con `blogadmin`: crea `blog_migrate` y `blog_app` con verificadores SCRAM, los privilegios de D-23 y los límites de D-12, bajo el bloqueo `(3364, 1)`. `verify` con `blogadmin` y sus tres controles negativos, con `blog_migrate` y con `blog_app` (DDL rechazado). `export` con `blog_migrate` a `exportaciones/<marca>/`: hoy no hay tablas de aplicación, así que probablemente solo un manifiesto | **Escrituras en la base productiva**: roles, privilegios y el esquema `verificacion`. Un objeto en S3. Lambda y S3, céntimos o menos |

Limpieza de la fase A: ninguna obligatoria, porque los recursos son permanentes. La exportación queda en
`exportaciones/`, con escritura condicional; su retención la decide `Task/040`.

**Fase B — H-031-7, restore sintético con PITR** (`restore_sintetico.py`, con el operador):

| Paso | Qué hace |
| --- | --- |
| B1. `preflight` | Solo lectura |
| B2. `sembrar` | Un marcador NO sensible en `verificacion.marcador` de la productiva, con `blog_migrate` |
| B3. `restaurar` | PITR a `blog-prod-restore-h0317-<AAAAMMDDhhmmss>`: `db.t4g.micro`, gp3 de 20 GiB, Single-AZ, privada, solo `sg-rds`, mismo *subnet group* y *parameter group*, sin backups, sin exportar logs, sin protección de borrado y etiquetada como temporal. Reanudable sin un segundo restore (§50.5) |
| B4. `verificar` | `verify` con `blog_migrate` en la temporal: la misma huella |
| B5. `limpiar` | Borra SOLO esa temporal, sin *snapshot* final ni backups automáticos. Demuestra la ausencia por API y que la productiva sigue intacta, y retira el marcador. **Se autoriza siempre, aunque B4 falle** |
| B6. `informe` | RPO y RTO observados frente a 15 min y 4 h (D-10) |

**Costo de la fase B:** unos 0.019 USD/h por la temporal (0.016 de la instancia más 20 GiB de gp3). Con 1 a 2 h,
unos 0.02–0.04 USD, contra los 134.12 USD de créditos. Sin *snapshots* ni backups residuales.

**Riesgos de la fase B:**
- que el plan FREE rechace el restore (`FreeTierRestrictionError`). No se puede verificar sin intentarlo; si pasa,
  STOP sin recursos creados;
- cuota de instancias: 1 de 40, sin problema;
- sesiones de 1 h: B3 a B5 pueden repartirse en dos sesiones gracias a la reanudación.

**Sesiones previstas:**
1. el plan de H-031-6, de solo lectura y sin apply;
2. la revisión del usuario y la autorización consolidada;
3. la fase A;
4. la fase B, en una o dos sesiones.

### 50.10 Bloqueos reales y pendiente para cerrar Task/031

**Bloqueos:**
1. ~~Sesión de AWS caducada~~: renovada; plan real verificado el 2026-10-20 (§50.12).
2. **Revisión del plan de H-031-6 y autorización consolidada** de las fases A y B (§50.9). Sin ella no hay apply,
   SQL productivo ni restore.
3. **H-031-7 en el plan FREE.** El riesgo no verificado de `FreeTierRestrictionError` solo se resuelve intentándolo,
   dentro de la fase B autorizada.

**Pendiente para cerrar Task/031, además de H-031-6 y H-031-7:**
- **Criterios de la ficha con desviación documentada** (§48.8), que el usuario debe aceptar al aprobar:
  - backups de 1 día en el plan FREE, no 7;
  - identidad operativa: `PersonalBlogAdministrator` (§24);
  - alarmas sin acciones, con la calibración de `memoria` pendiente;
  - D-19: la comprobación al terminar el trial.
- **Abiertos que no bloquean:**
  - R-12, con seguimiento en `Task/040`;
  - la solicitud de cuota a 1001, abierta y no requerida;
  - la calibración de la alarma `memoria`.
- **Cierre formal:** solo con `approved: Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`. Entonces se hacen los commits,
  la integración en `dev`, la publicación y el PR `Task/031 → main`.

### 50.11 Estado

- **Código, laboratorio y gates:** en verde. Ciclo completo del laboratorio: **CICLO COMPLETO**. Gates: 32/32.
- **AWS:** lecturas y el plan guardado de H-031-6, con su bloqueo nativo. Ningún apply, refresh-only ni restore
  productivo; ningún recurso creado ni modificado. El state sigue en el serial 15, 35/35, con la misma huella.
- **Resultado:** `Task/031 — LABORATORIO COMPLETO / H-031-6 PLAN READY FOR APPLY REVIEW / H-031-7 LISTO PARA
  AUTORIZACIÓN CONSOLIDADA`. **No** es READY FOR USER APPROVAL.

### 50.12 Plan real de H-031-6 (2026-10-20)

**Sesión.** Tres renovaciones fallaron:
- dos por el margen;
- una porque la consola reutilizó la sesión de rol vigente: no hubo SwitchRole ni RenewRole nuevos, y el `aws login`
  se enganchó a la sesión anterior.

La prueba fiable fue correlacionar la clave en uso (solo enmascarada) con el
`sessionContext.attributes.creationDate` de sus propias llamadas `GetCallerIdentity`, que CloudTrail mostró en
alrededor de 1 min. Tras un cierre completo de la consola, el inicio con MFA y el cambio de rol, la clave `ASIA…HQ62`
firmó con una sesión creada a las **02:45:06Z**. El runner calculó 56 min y su regla de 35 no se tocó. Script privado:
`tmp/h0320/esperar_y_planificar.py`, con un solo bucle acotado.

**Runner** `tmp/h0320/fase_h0316.py plan`, entre las 02:48 y las 02:52Z, sin apply:

| Paso | Resultado |
| --- | --- |
| Backend | `backend "s3" {}` regenerado sobre el `local` del laboratorio; `init` y `validate` OK; metadata: s3, key de datos, `us-east-2`, `encrypt` y lock nativo, sin DynamoDB ni KMS |
| State antes y después | Serial 15, 35/35, 0 taints, sin lock; SHA-256 `5484a78f878fcae28cb6932c651e9b18ae0a7a54d8d9763c6fc17e87655ea4a2`, idéntico |
| Red | Sin NAT, IGW ni EIGW; un único endpoint de S3; `sg-admin` solo hacia `sg-rds:5432` |
| Preflight | FREE/ACTIVE, con 153.66 USD de créditos; RDS conforme; la master en v1 y las credenciales ausentes; el rol con solo `-ejecucion`; la función `Active` con h0315 y sin reserva; `exportaciones/` vacío |
| Artefacto | h0316 `98f41bfd…8e43`, con su pin, en el directorio privado |
| Plan | Exit 2: `Plan: 4 to add, 1 to change, 0 to destroy.` |
| Guarda | **`H0316_PLAN_OK`**: 4 add, 1 change, 0 destroy; deriva del caso B |
| Secretos | La master y las dos contraseñas desechables: `PRODUCTION_SECRET_ABSENT = true` las tres veces (26 467 archivos y 4 *buffers*) |

| Artefacto | SHA-256 |
| --- | --- |
| Plan guardado `h0316.tfplan` (privado) | `8d1a73078720e7a697d71f25648d4b83fdaf3753b16624d3d3fa0b0371b57a6d` |
| JSON del plan (privado) | `a7e85e3143b87d8fb6dcac9783cb80b6bad50c775321ddcf9167e8acb838fb10` |
| ZIP h0316 | `98f41bfd3a1d2c9ac97f1686d803f8eba40c3cf450bb8e7b491fa9fef5ff8e43` |

**Cambios exactos.** 34 recursos en `no-op`. Identificadores y bucket, enmascarados.

| Acción | Recurso | Valores |
| --- | --- | --- |
| `update` en sitio | `module.ejecutor_privado.aws_lambda_function.this` | `source_code_hash` del pin h0315 (`4n/nNU…I70=`) al h0316 (`mPQb/T…jkM=`); `filename` de `ejecutor-h0315.zip` a `ejecutor-h0316.zip`; `description` de «Ejecutora privada D-24 (Task/031 H-031-5): shell sin base de datos» a «Ejecutora privada de administracion de datos (D-24).». Solo `last_modified` queda desconocido |
| `create` | `module.credenciales_sql.aws_ssm_parameter.blog_migrate` | `/blog-prod/datos/blog_migrate`, SecureString, Standard, `alias/aws/ssm`, `value_wo_version` 1; sin valor en el plan |
| `create` | `module.credenciales_sql.aws_ssm_parameter.blog_app` | `/blog-prod/datos/blog_app`, con los mismos contratos |
| `create` | `module.exportacion.aws_iam_role_policy.this` | `PersonalBlogEjecutorDatos-exportacion` en `PersonalBlogEjecutorDatos`: `s3:PutObject` solo en `<bucket-de-medios>/exportaciones/*`, con `s3:if-none-match = *` y `aws:SourceVpce` del endpoint. `name_prefix` desconocido |
| `create` | `module.exportacion.aws_vpc_security_group_egress_rule.admin_a_s3` | Sale de `sg-admin` hacia la prefix list de S3, TCP 443, sin CIDR |

- **Salidas:** las 19 actuales en `no-op`; nueva `nombres_de_credenciales_sql`, con las dos rutas.
- **Deriva:** caso B, solo `latest_restorable_time` de RDS, del 2026-10-19T01:51:53Z (state) al 2026-10-20T02:41:56Z
  (AWS, unos 11 min antes del plan).
- **Variables:** ninguna contraseña efímera en el plan; versiones de las credenciales: 1 y 1.

**El plan real confirma las dos correcciones de §50.2:**
- la política llega con `name_prefix` desconocido;
- la master conserva `value = ""` en el state.

Con la guarda original de Codex, este plan se habría rechazado.

## 51. H-031-6 aplicada y verificada, y H-031-7 completa (2026-10-20 y 2026-10-21)

Autorización del usuario del 2026-10-20, «AUTORIZACIÓN CONDICIONADA H-031-6 + H-031-7», tras revisar el plan real
de §50.12:
- **fase A (H-031-6):** el apply exacto del plan `8d1a7307…7a6d`, con 4 creaciones, 1 actualización en sitio y 0
  destrucciones. Las contraseñas reales se generan solo en memoria y su única custodia es SSM. Después:
  - readback, `selfcheck` y la convergencia 0/0/0 sobre 39 recursos;
  - el refresh-only, solo con `H0316_REFRESH_OK`;
  - `blog_migrate` y `blog_app` con sus privilegios mínimos, las pruebas TLS y la exportación controlada a S3.
- **fase B (H-031-7):** el PITR sintético de §50.9, solo después de una fase A correcta, con un tope de costo de
  USD 0.50.

Condiciones generales:
- ninguna destrucción, reemplazo ni modificación no prevista;
- ninguna operación mutadora repetida si su resultado es incierto;
- STOP ante un fallo parcial, conservando la evidencia;
- 35 min de sesión.

La autorización **no** equivale a `approved: Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`. Sin staging, commit, push,
PR ni merge.

### 51.1 Runners protegidos y validación sin conexión

Los runners son privados y no se versionan: `tmp/h0320/fase_h0316.py`, `fase_h0317.py` y `esperar_y_lanzar.py`.

- **`fase_h0316.py`.** Fases `apply`, `convergencia` y `sql`; la fase `plan` conserva su comportamiento.
  - **Antes de aplicar:** la configuración del root y de sus módulos debe ser idéntica a la instantánea guardada en el
    plan: los 28 archivos `.tf` y el lock, ningún `.tf` nuevo y nada modificado después del plan, plantillas
    incluidas. El backend no se reescribe. Motivo: Terraform relee las plantillas al aplicar.
  - **Fase `sql`:** cada escritura queda registrada **antes** de invocarse y nunca se repite si su resultado es
    incierto. Las lecturas sí pueden repetirse.
- **`fase_h0317.py`.** Orquesta `restore_sintetico.py`. Si se interrumpe, se reanuda sin repetir el restore ni el
  delete.
- **`esperar_y_lanzar.py`.** Antes de lanzar nada, demuestra la sesión de las credenciales en uso: correlaciona la
  clave con `sessionContext.attributes.creationDate`.
- **Validación sin conexión:** 51/51 casos, más la verificación del plan guardado en solo lectura:
  - el SHA es el autorizado;
  - el JSON derivado coincide byte a byte con el revisado (`a7e85e31…`);
  - la guarda devuelve `H0316_PLAN_OK` 4/1/0/0.

### 51.2 Sesiones

Todas las horas, en UTC según CloudTrail y STS. La sesión de `aws login` caduca con la sesión de rol de la consola.

| Hora | Hecho | Consecuencia |
| --- | --- | --- |
| 03:51:43Z | STS `expired`: el login de las 03:35Z quedó invalidado por el cierre de sesión de la consola | Nada lanzado |
| 04:01:42Z | `RenewRole`: sesión nueva, demostrada a las 04:04:38Z con 57 min | Fase `apply` |
| 04:36:30Z y 04:58:02Z | `aws login` enganchados a la sesión de las 04:01:42Z, sin `SwitchRole` ni `RenewRole` nuevos | STOP a las 04:46:33Z y a las 04:59:55Z; nada lanzado |
| 05:02:07Z | `ExpiredToken`: la sesión de las 04:01:42Z caducó y aún no había un login nuevo | Nada lanzado |
| 05:01:57Z | `RenewRole`: sesión nueva, demostrada a las 05:13:33Z con 48 min | Fase `sql` y preflight de H-031-7 |
| 05:49:52Z, 05:54:51Z y 06:00:23Z | `aws login` enganchados a la sesión de las 05:01:57Z, antes de que caducara | STOP sin lanzar nada, las tres veces |
| 06:03:24Z | Sesión nueva, demostrada a las 06:06:07Z con 57 min | Preflight y PITR de H-031-7 (§51.8) |
| 2026-10-21, 02:16:07Z | Sesión nueva, demostrada a las 02:26:08Z con 49 min | Reanudación de la limpieza y cierre de H-031-7 (§51.9 y §51.10) |

Lección: un `aws login` hecho mientras la sesión de rol anterior sigue vigente se engancha a ella, aunque se vuelva a
iniciar sesión en la consola. Lo fiable fue esperar a que caducara y cambiar de rol después.

### 51.3 H-031-6: apply, readback y convergencia (04:04–04:15Z)

`python -B tmp/h0320/esperar_y_lanzar.py fase_h0316.py apply sql`:

| Paso | Resultado |
| --- | --- |
| Sesión | Creada a las 04:01:42Z; 57 min al empezar |
| Configuración | Idéntica a la instantánea del plan: 28 archivos, ningún `.tf` nuevo y nada posterior al plan en 8 directorios |
| State antes | Serial 15, 35/35, 0 taints, sin lock; SHA-256 `5484a78f…a4a2`, el autorizado |
| Red y preflight | Como en el plan. FREE/ACTIVE con 153.51 USD de créditos; credenciales ausentes; función con h0315 y sin reserva; `exportaciones/` vacío |
| Plan | SHA-256 `8d1a7307…7a6d`; JSON derivado idéntico al revisado; ZIP h0316 del pin; tfvars del plan; `H0316_PLAN_OK` 4/1/0/0 |
| Apply | Con 56 min: `Apply complete! Resources: 4 added, 1 changed, 0 destroyed.` La función tardó 1 min 19 s; los dos SSM, la política y la regla, 1 s cada uno |
| State después | Serial 17, mismo lineage, 39/39, 0 taints, sin lock |
| *Readback* de SSM | Master en v1, intacta. `/blog_migrate` y `/blog_app`: SecureString, Standard, `alias/aws/ssm`, v1, con la descripción y las etiquetas del contrato. El valor custodiado coincide con el generado en memoria en las dos (comparación **booleana**, sin imprimirlos) |
| *Readback* de IAM | Rol y confianza intactos; `-ejecucion` intacta; `-exportacion` EXACTA (`s3:PutObject` solo en `exportaciones/*`, con `s3:if-none-match` y `aws:SourceVpce` del endpoint); ninguna política administrada |
| *Readback* de reglas | `sg-admin` sale EXACTAMENTE hacia `sg-rds:5432` y hacia la prefix list de S3 por el 443, con la descripción y las etiquetas del contrato; `sg-rds` y `sg-lambda` intactos |
| *Readback* de la función | `Active` y `Successful` con el pin h0316 (`mPQb/T…jkM=`) y la descripción de D-24; sin concurrencia reservada; solo `sg-admin` en 2 subredes; sin URL, política de recurso, disparadores, configuración asíncrona, versiones ni alias; 2 ENI Hyperplane privadas |
| `selfcheck` | `StatusCode 200`, sin `FunctionError`; respuesta EXACTA del contrato `d24-ejecutor-h0316-v1`, con `verify` y `export` en `IMPLEMENTED`; línea de log visible |
| Convergencia | «No changes», exit 0. La guarda la rechazó con `DRIFT`, por las normalizaciones previstas |
| Refresh-only preautorizado | Plan exit 2; `H0316_REFRESH_OK` con 3 derivas: `inline_policy` del rol (de 1 a 2 políticas), `egress` de `sg-admin` (de 1 a 2 reglas) y `latest_restorable_time` de RDS. Apply 0/0/0; state en el serial 18 |
| *Readback* tras el refresh-only | Idéntico |
| Convergencia final | «No changes», exit 0: **`ACTIONABLE_CONVERGENCE_OK` 0/0/0, fase `h0316`, 39 recursos, sin deriva** |
| Secretos | Master y las dos contraseñas reales: `PRODUCTION_SECRET_ABSENT = true` las tres veces (15 *buffers* y unos 26 980 archivos) |

| Plan posterior al apply | SHA-256 |
| --- | --- |
| Convergencia | `cd47196ee51b89968a061c1318920025e59a367df7c3ebe31775175b13e3df26` |
| Refresh-only | `857c709affa748f742d5d634ec6904cf272aeb8cac21df15df244baf94076215` |
| Convergencia tras el refresh-only | `7c79312b0831144475f4da203f109d501318c8e7de90c25fba5ae4117ad7dd9e` |

### 51.4 H-031-6: el primer intento SQL se detuvo sin escribir nada (04:15:50–04:16:03Z)

El `selfcheck` por el operador fue conforme. El `verify` de `blogadmin` respondió `OK`:
- TLSv1.3, `verify-full` y 256 bits; PostgreSQL 17.11;
- los tres controles negativos, rechazados.

Pero `servidor.rds_force_ssl` llegó **`null`**, y el validador del runner exigía `"1"`: STOP **antes** de
`identidades`. No hubo ninguna escritura en la base ni en S3.

**Causa:** el defecto estaba en el validador, no en la base.
- En una sesión de RDS, `current_setting('rds.force_ssl', true)` devuelve NULL.
- La API de RDS, en solo lectura, confirmó `rds.force_ssl = 1` (`system`, dinámico), con
  `blog-prod-postgres17` `in-sync`, `ssl = 1` y `ssl_min_protocol_version = TLSv1.2`.
- El servidor ya había rechazado la conexión sin TLS.

**Corrección autorizada por el usuario el mismo día**, solo en el validador del runner privado. `rds_force_ssl = null`
se acepta solo si en la misma corrida se demuestran las tres condiciones:
1. la API confirma `rds.force_ssl = 1` con el grupo `in-sync`. Es una precondición nueva de la fase `sql`;
2. el servidor rechaza explícitamente la conexión sin TLS. Para `blogadmin` lo prueba su propio control. Para
   `blog_migrate` y `blog_app`, el `verify` de `blogadmin` de esa corrida, que por eso **siempre** se repite;
3. la conexión verificada usa TLS con `verify-full`.

Cualquier otro valor (`"0"`, `"on"`, vacío u otro tipo), la falta de evidencia o un control inconcluso producen STOP.

- **Pruebas:** 44/44 (4 positivas, 23 negativas, 9 de la precondición por la API y 8 de flujo).
- **RED:** el contrato no existía. El RED real fue el STOP de las 04:16Z con la respuesta auténtica.
- **Evidencia conservada:**
  - copias íntegras del intento no conforme;
  - el `historial` del progreso;
  - un log por invocación.
- **Sin cambios** en el ZIP ni en su hash, en la infraestructura, en las guardas de Terraform, ni nuevos apply o
  refresh-only.

### 51.5 H-031-6: SQL conforme (05:13:48–05:14:35Z)

Lanzado con `tmp/h0320/sesion_nueva_y_sql.py`, que se detiene en cuanto la clave en uso firma con una sesión anterior.
Sesión creada a las 05:01:57Z, con 48 min tanto por la correlación como por el runner.

| Paso | Resultado |
| --- | --- |
| TLS forzado según la API | `blog-prod-postgres17` `in-sync`, con `rds.force_ssl = 1` (`system`) |
| `selfcheck` | Conforme desde las 04:15:52Z; no se repite |
| `verify` de `blogadmin` (repetido) | TLSv1.3, `TLS_AES_256_GCM_SHA384`, 256 bits, `verify-full`; 17.11; `personal_blog`. `rds_force_ssl` nulo, aceptado con las tres evidencias. Controles: `sin_tls` → `RECHAZADO_POR_EL_SERVIDOR`; `host_distinto` y `ca_ajena` → `RECHAZADO_POR_TLS`. `blogadmin` no es superusuario |
| `identidades` (escritura, con el bloqueo `(3364, 1)`) | `blog_migrate` (límite 5) y `blog_app` (límite 89): LOGIN; sin superusuario, CREATEROLE, CREATEDB, REPLICATION, BYPASSRLS ni herencia. `CONNECT` para los dos y no para `PUBLIC`; `PUBLIC` sin `TEMPORARY`. En `public`: `blog_migrate` con USAGE y CREATE, `blog_app` solo con USAGE y `PUBLIC` sin CREATE. Privilegios por omisión `arwd` para `blog_app` sobre las tablas de `blog_migrate`. La relectura coincide EXACTAMENTE con el contrato desplegado |
| `verify` de `blog_migrate` | TLSv1.3 con `verify-full`; identidad exacta, límite 5 |
| `verify` de `blog_app` | TLSv1.3 con `verify-full`; identidad exacta, límite 89; **DDL rechazado** |
| `export` (escritura en S3) | Marca `20261020T051414Z`; 0 tablas de aplicación, 0 bytes |
| *Readback* de la exportación | En `exportaciones/` solo está `exportaciones/20261020T051414Z/manifiesto.json`: `application/json`, `ChecksumSHA256` verificado, cifrado `AES256`, formato `d24-export-v1` sin tablas |
| Secretos tras el SQL | Master, `blog_migrate` y `blog_app`, leídas solo en memoria desde SSM: ausentes de los 27 033 archivos |

**H-031-6 queda COMPLETA y CONFORME.**

### 51.6 H-031-7: controles de recuperación, ajustados antes del PITR

A petición del usuario, se ajustó y probó el tratamiento del rechazo `FreeTierRestrictionError`. El marcador sintético
se retira solo cuando está demostrado que no se creó ninguna temporal.

**Hallazgo: CloudTrail no registra los rechazos del plan FREE.**
- El 2026-10-05, entre las 14:59:10Z y las 14:59:17Z, el historial de RDS muestra incluso las lecturas fallidas, como
  `DescribeDBInstances` con `DBInstanceNotFoundFault`.
- En cambio, falta el `CreateDBInstance` que la API rechazó con HTTP 400 `FreeTierRestrictionError` (§32).
- Una guarda que exigiera ver el rechazo en CloudTrail nunca se cumpliría.

**Cambio en el orquestador versionado** `scripts/terraform_datos/restore_sintetico.py`:
- una respuesta HTTP 4xx con código queda en el manifiesto como `temporal.rechazo` (`codigo`, `http`, `t_rechazo`) y
  la salida es `RESTORE_RECHAZADO`;
- relanzar `restaurar` nunca repite la llamada;
- sin respuesta HTTP, o con un 5xx, el resultado sigue siendo incierto;
- el mensaje de AWS, que lleva ARN y cuenta, no se conserva.

Pruebas en `tests/terraform_datos/test_restore_rechazo.py`:
- **RED:** 3 de 7, por el motivo esperado (`ERROR_DEL_OPERADOR` o `RESTAURACION_INCIERTA` en lugar de
  `RESTORE_RECHAZADO`).
- **GREEN:** 7 de 7.
- **Regresión:** 39/39 en las suites del orquestador y 718/718 en `tests/terraform_datos`, con la invocación del CI.

**Protocolo del runner ante el rechazo FREE.** El marcador se retira solo si se cumplen las cinco condiciones:
1. el manifiesto registra el rechazo `FreeTierRestrictionError`;
2. la API no encuentra la temporal en dos lecturas separadas por 60 s;
3. no hay instancias, backups automáticos, snapshots ni grupos de logs del prefijo;
4. CloudTrail no muestra ninguna llamada **aceptada** para esa temporal;
5. la productiva sigue igual que en su línea base.

El retiro queda registrado antes de invocarse, se confirma con una lectura independiente (`verify --marcador` con
`blog_migrate`) y nunca se repite.

**Temporal en estado incierto:** se detiene sin borrar nada y deja en el log el procedimiento de recuperación y el
costo posible (0.0192 USD/h; unos 0.46 USD al día). Son inciertos los estados:
- `creating` o fallido;
- sin la identidad, el `DbiResourceId` o las etiquetas registrados;
- con un borrado incierto.

La limpieza autorizada aunque falle la verificación solo se lanza sobre la temporal registrada, `available` y con sus
etiquetas. Resultado: 32/32 casos sin conexión.

### 51.7 H-031-7: preflight (05:14:51–05:15:03Z, solo lectura)

| Punto | Resultado |
| --- | --- |
| Sesión y cuenta | 47 min; FREE/ACTIVE, 153.51 USD de créditos |
| H-031-6 | Completa: apply convergente y los 6 pasos SQL conformes |
| Productiva | `available`, `db.t4g.micro`, 17.11, cifrada, privada, retención de 1 día, PITR con 189 s de retraso (límite: 900) |
| Temporales y residuos | Ninguna temporal previa y ningún residuo del prefijo |
| Costo estimado | Cota superior: 0.067 USD, frente al límite de 0.50 |

El usuario revisó estas evidencias y dio su visto bueno al PITR de H-031-7, con nueve condiciones.

### 51.8 H-031-7: PITR real (2026-10-20, 06:06–06:29Z)

Lanzado con `tmp/h0320/sesion_nueva_y_h0317.py`. Sesión creada a las 06:03:24Z, con 57 min. Antes hubo tres intentos
con la sesión anterior, detenidos sin lanzar nada (§51.2). Se ejecutaron el preflight de nuevo y después `restore`.

| Paso | Hora (UTC) | Resultado |
| --- | --- | --- |
| Preflight | 06:06:22Z | OK; línea base de la productiva registrada (`DbiResourceId`, creación, clase, almacenamiento, red, parámetros y el endpoint por hash) |
| `sembrar` | 06:06:37Z | Marcador `eb193cfb-6e54-458a-8b72-d555df8e9d2b` en `verificacion.marcador` de la productiva, con `blog_migrate`. t0: 06:06:47Z |
| Registro de la temporal | 06:06:50Z | `blog-prod-restore-h0317-20261020060647`, registrado ANTES de crear nada |
| Espera del PITR | 06:14:54Z | `LatestRestorableTime` cubre el marcador con 60 s de margen |
| Restore | 06:14:54Z | Una sola llamada (CloudTrail: 06:14:58Z, aceptada) al punto 06:11:54Z. **El plan FREE no rechazó el restore** |
| `available` | 06:27:36Z | *Readback* conforme: cifrada, privada, Single-AZ, misma clase, mismos grupos y *subnet group*, sin backups, sin exportar logs, sin protección de borrado y etiquetada como temporal |
| `verificar` | 06:27:48Z | **Integridad `true`**: la ejecutora leyó en la restaurada la misma huella que en la productiva |
| `limpiar` | 06:27:51Z | **Un solo** `DeleteDBInstance`, aceptado, sin *snapshot* final y borrando los backups automáticos; temporal ausente por API. Después: STOP por el incidente de §51.9 |

**Tiempos e informe del orquestador:**

| Medida | Observado | Objetivo (D-10) |
| --- | --- | --- |
| RPO (del punto restaurado a la solicitud) | **180 s** | 900 s |
| RTO (de la solicitud a la verificación) | **774 s** | 14 400 s |
| Espera hasta que el PITR cubre el marcador | 487 s | — |
| Del restore a `available` | 762 s | — |
| Verificación | 12 s | — |
| Total, del marcador a la verificación | 1261 s | — |

**Costo de la temporal:** existió unos 13 min, entre 0.0041 y 0.0046 USD, según
`db.t4g.micro` más 20 GiB de gp3 (0.0192 USD/h). El límite autorizado era 0.50 USD.

### 51.9 Incidente: el 404 `DBInstanceAutomatedBackupNotFound` detuvo la limpieza

**Qué pasó.** Tras el borrado, el orquestador consultó los backups automáticos de la temporal. Cuando no hay ninguno,
`DescribeDBInstanceAutomatedBackups` no devuelve una lista vacía, sino HTTP 404
`DBInstanceAutomatedBackupNotFound`; botocore lo modela como `DBInstanceAutomatedBackupNotFoundFault`.

`limpiar` lo trató como un error del operador y se detuvo después del borrado y **antes** de retirar el marcador. El
runner se detuvo sin repetir nada y dejó en el log el procedimiento de recuperación y el costo.

**Por qué no lo vieron las pruebas.** El RDS simulado devolvía una lista vacía, y no la forma real de la API.

**Diagnóstico** (06:31Z, solo lectura):
- la temporal, ausente;
- sus backups, el 404;
- 0 instancias, backups automáticos, *snapshots* y grupos de logs del prefijo;
- en CloudTrail, un único `DeleteDBInstance` aceptado;
- la productiva, idéntica a su línea base;
- el marcador, todavía presente y con su huella.

**Corrección**, con TDD, en `scripts/terraform_datos/restore_sintetico.py`:
- `_backups_automaticos` cuenta como cero **exactamente** ese 404;
- cualquier otro error sigue siendo error;
- un backup retenido sigue siendo `LIMPIEZA_INCOMPLETA`.

Pruebas en `tests/terraform_datos/test_restore_limpieza_backups.py`:
- **RED:** 2 de 5, los dos casos del 404.
- **GREEN:** 5 de 5, con la forma real de la API.
- **Regresión:** 723/723 en `tests/terraform_datos`.

**Fase de reanudación**, autorizada por el usuario solo para esta limpieza: `fase_h0317.py limpieza`.
- Exige el checkpoint: borrado pedido y retiro todavía no pedido.
- Conserva copias del manifiesto y de la línea base.
- Antes de escribir, comprueba en solo lectura:
  - la temporal, ausente;
  - sus backups, una lista vacía o exactamente el 404;
  - ningún residuo;
  - la productiva, IDÉNTICA a su línea base;
  - el marcador, con el id y la huella del manifiesto.
- Reanuda `limpiar`, que registra el retiro antes de invocarlo y no vuelve a pedir el borrado.
- Confirma la ausencia del marcador con una verificación independiente.
- No ejecuta preflight, siembra, PITR ni `DeleteDBInstance`.
- Pruebas: 26/26, de ellas 16 casos de STOP sin mutaciones.

**Reanudación** (2026-10-21, 02:24–02:27Z): sesión nueva, creada a las 02:16:07Z, con 49 min.

| Paso | Resultado |
| --- | --- |
| Checkpoints | Copias `.checkpoint-limpieza-20261021T022613Z.json` del manifiesto y de la línea base |
| Antes de escribir | Temporal ausente; 0 backups suyos; 0 residuos; productiva idéntica a su línea base; marcador presente con la huella del manifiesto |
| `limpiar` | OK: `ausente_por_api`, `productiva_intacta` y `marcador_retirado`; ningún segundo borrado |
| Verificación independiente | Marcador ausente (`verify --marcador` con `blog_migrate`) |
| Comprobación final | Productiva `available` e igual a su línea base; sin instancias, backups automáticos, *snapshots* ni grupos de logs de la temporal |
| Informe | Integridad `true`; RPO 180 s y RTO 774 s, ambos dentro del objetivo |

### 51.10 H-031-7: cierre técnico, con comprobaciones independientes (2026-10-21, 02:28Z)

Solo lectura, con `tmp/h0320/cierre_h0317.py`:
- **CloudTrail:** exactamente un `RestoreDBInstanceToPointInTime` (06:14:58Z) y un `DeleteDBInstance` (06:27:51Z) a la
  temporal, los dos aceptados.
- **State de `terraform-datos`:** serial 18, 39/39, sin taints ni lock; es el de la convergencia final de H-031-6.
  SHA-256 `8abda37e6192172ac706076c37e909f71fe27bc671502f307c072c0126034196`. H-031-7 no tocó nada gestionado por
  Terraform.
- **Productiva:** `available`, privada, con protección de borrado, sin cambios pendientes, el mismo `DbiResourceId` y
  la misma configuración que su línea base.
- **Temporal y residuos:** temporal ausente; 0 instancias, backups automáticos, *snapshots* y grupos de logs del
  prefijo.
- **Manifiesto final:**
  - `borrado_solicitado`, `ausente_por_api`, `retiro_solicitado`, `productiva_intacta` y `marcador_retirado` en
    `true`;
  - 0 backups automáticos restantes;
  - integridad `true`.

En la productiva sigue la tabla `verificacion.marcador`, **vacía**, en el esquema `verificacion` que `identidades`
crea para `blog_migrate`. No es un residuo de la temporal: forma parte del diseño de verificación de D-23.

**H-031-7 queda COMPLETA.** El informe final está en `h0317-informe-final.json`, en el directorio privado.

### 51.11 Restricciones del plan AWS FREE y alcance real de la validación

- **Retención de backups de 1 día, no de 7.** El plan FREE rechazó 7 días con `FreeTierRestrictionError` (§32). El
  criterio 5 de la ficha queda con desviación documentada, que el usuario debe aceptar. Con 1 día, PITR funciona: lo
  demuestra H-031-7.
- **El restore sintético sí está permitido en el plan FREE.** La llamada se aceptó y la temporal llegó a `available`.
  El riesgo de §50.9 no se materializó.
- **CloudTrail no registra los rechazos del plan FREE.** La prueba del rechazo es la respuesta 4xx síncrona, que el
  orquestador guarda como `temporal.rechazo` (§51.6). Ese camino quedó probado y no hizo falta.
- **La exportación a S3 se validó sin tablas de aplicación:**
  - el manifiesto `d24-export-v1` sin tablas;
  - 0 bytes de datos;
  - `ChecksumSHA256` verificado y cifrado `AES256`.

  La ruta completa con datos reales y su retención quedan para `Task/036` y `Task/040`.
- **Identidad operativa:** `PersonalBlogAdministrator` (§24), no una identidad mínima dedicada.
- **Sesiones de 1 h:** cada fase exigió 35 min de margen; un PITR puede repartirse entre sesiones, porque se reanuda
  sin repetir nada.

### 51.12 Pruebas y validaciones de esta sección

| Prueba | Resultado |
| --- | --- |
| Runner de H-031-6, sin conexión | 51/51; verificación del plan guardado en solo lectura |
| Validador SQL corregido | 44/44 |
| Runner de H-031-7 con el protocolo FREE | 32/32 |
| Fase `limpieza` de H-031-7 | 26/26 |
| `test_restore_rechazo.py` (nuevo, versionado) | RED 3 de 7, GREEN 7 de 7 |
| `test_restore_limpieza_backups.py` (nuevo, versionado) | RED 2 de 5, GREEN 5 de 5 |
| `tests/terraform_datos`, con la invocación del CI | 723/723 |
| Búsqueda de secretos tras el apply y tras el SQL | Master, `blog_migrate` y `blog_app` ausentes, sin coincidencias |

Las validaciones finales del repositorio están en §51.13.

### 51.13 Validación final del repositorio (2026-10-21)

Se ejecutó solo lo que podían afectar los cambios posteriores a la última gate verde (§50.7): el orquestador, dos
archivos de pruebas nuevos y la documentación. No ha cambiado ningún archivo de Terraform: lo prueba la comprobación
de configuración del apply (§51.3).

| Validación | Resultado |
| --- | --- |
| `tests/terraform_datos`, con la invocación del CI | 723/723 |
| `tests/security` | 88/88 |
| Compilación de `scripts/`, como el paso del CI | 41 archivos, 0 fallos |
| `git diff --check` | Limpio; los archivos nuevos, con LF y sin espacios finales |
| Enlaces y anclas de los 7 documentos editados | 716 enlaces, 0 rotos |
| Gitleaks sobre el entregable (427 archivos: `git ls-files` y los no ignorados) | Sin fugas |
| Terraform (`fmt`, `init`, `validate` y `test` de los 6 roots), `tests/laboratorio`, `oidc`, `terraform_state` y `compose` | No se repitieron: sin cambios desde su última corrida verde (32/32) |

**Git** (sin staging ni commits):
- **Rama:** `Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`, solo en `personal-blog-infra`.
- **Cambios:** 28 archivos modificados y 23 entradas nuevas.
- **Ignorados, como corresponde:** `tmp/`, `errored.tfstate`, `.terraform/`, `backend.generado.tf` y `generado/`.
- **Resuelto el 2026-10-21** (§51.15): `terraform/modulos/ejecutor_privado/codigo_h0316/rds-ca-us-east-2.pem`
  estaba ignorado por la regla `*.pem`.
  - Es la CA **pública** de RDS: 3 certificados y ninguna clave privada.
  - Es una de las 4 fuentes del ZIP fijado.
  - Sin ella, `test_empaquetar_ejecutor_h0316.py` fallaría en un checkout limpio.
  - Se añadió la excepción exacta `!terraform/modulos/ejecutor_privado/codigo_h0316/rds-ca-us-east-2.pem`, con
    la autorización del usuario.

### 51.14 Estado

- **AWS:** ninguna operación pendiente; ninguna temporal, backup, *snapshot* ni grupo de logs de H-031-7; ningún
  costo en curso.
- **Terraform:** `terraform-datos` en el serial 18 con 39/39; la última convergencia fue 0/0/0.
- **Traspaso a una nueva sesión:** [TASK-031-handover.md](TASK-031-handover.md).
- **Resultado: CIERRE TÉCNICO COMPLETADO — Lista para validación.**

Pendientes:
- la revisión del usuario;
- la aceptación de las excepciones de §51.16;
- `approved: Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`.

**No** es la aprobación de la tarea.

### 51.15 Versionado de la CA pública de RDS (2026-10-21)

Autorización del usuario del 2026-10-21: añadir **solo** la excepción exacta al `.gitignore`, sin tocar `*.pem`, sin
otras excepciones y sin operaciones de AWS.

**Contenido, integridad y procedencia** (sin red ni AWS):

| Comprobación | Resultado |
| --- | --- |
| Tipos PEM | 3 bloques `CERTIFICATE` y nada fuera de ellos; ninguna clave privada |
| Certificados | Raíces autofirmadas de `O=Amazon Web Services, Inc.`, `OU=Amazon RDS`: `Amazon RDS us-east-2 Root CA RSA2048 G1` (2021–2061), `RSA4096 G1` (2021–2121) y `ECC384 G1` (2021–2121). Todas con `CA:TRUE` y la firma válida, verificada de forma aislada, sin el almacén del sistema |
| Integridad | SHA-256 `d46e1bdfda05c8e7644e50930806a19b139a222542bf0348082fb59ece2b5fa5`: el fijado en este reporte y en `test_bundle_de_la_ca_empaquetado_y_fijado` |
| Procedencia | El bundle regional `us-east-2-bundle.pem` de `truststore.pki.rds.amazonaws.com`, según las decisiones de RDS (§5.1) |
| Prueba funcional | En H-031-6, las sesiones `verify-full` contra la productiva, cuya CA es `rds-ca-rsa2048-g1`, validaron con este bundle; con el almacén del sistema (`ca_ajena`), el TLS se rechazó. El original no se volvió a descargar: la autorización excluía operaciones de AWS |

**`.gitignore`.** Una sola línea nueva, con su comentario, al final del bloque de secretos:
`!terraform/modulos/ejecutor_privado/codigo_h0316/rds-ca-us-east-2.pem`. `*.pem` sigue intacta.
- `git check-ignore`: el archivo **no** está ignorado; lo que coincide es la negación de la línea 20.
- `git status`: `??`, es decir, versionable.
- Un `.pem` en la raíz, otro en el mismo directorio o uno con el mismo nombre en otro directorio **siguen ignorados**.

**Checkout limpio** (`tmp/h0320/checkout_limpio_h0316.py`). Se probó sobre una copia de exactamente el entregable: 428
archivos, sin ningún ZIP ni ninguna rueda.
- El empaquetado h0316 desde la copia, con las ruedas fijadas que el empaquetador verifica por SHA-256, produce
  `98f41bfd3a1d2c9ac97f1686d803f8eba40c3cf450bb8e7b491fa9fef5ff8e43`. Es **igual al pin y al ZIP desplegado**.
- **Control negativo:** sin el `.pem`, el empaquetado falla (`FileNotFoundError`) y no escribe ningún ZIP.
- **Pruebas en la copia:** las de empaquetado 75/75 y `tests/terraform_datos` 723/723, sin fallos ni omisiones.

**Seguridad.**
- Gitleaks sobre los 428 archivos del entregable, incluido el `.pem`: sin fugas.
- `git diff --check`: limpio.

**Inventario pendiente de versionar.** Sin staging: 163 archivos, 28 modificados y 135 nuevos.

| Área | Modificados | Nuevos |
| --- | --- | --- |
| Documentación | 17 | 6 |
| Pruebas `terraform_datos` | 0 | 41 |
| Módulos Terraform (incluido el `.pem`) | 0 | 29 |
| Scripts `terraform_datos` | 0 | 26 |
| Root `terraform-datos` | 0 | 15 |
| Bootstrap `operador-datos` | 0 | 11 |
| Pruebas del laboratorio | 4 | 6 |
| Scripts del laboratorio | 4 | 0 |
| Scripts de seguridad | 0 | 1 |
| Laboratorio (`compose`), CI y `.gitignore` | 3 | 0 |

Revisado archivo por archivo:
- **Excluido:** ningún ZIP, rueda, state, plan, log, `.env`, `__pycache__` ni clave.
- **Versionable por diseño:** `terraform-datos/entornos/local/local.tfvars`, sin secretos, como los de `terraform` y
  `terraform-medios`, que ya están versionados.
- **Fuera del entregable, privados e ignorados:** `tmp/`, `errored.tfstate`, `.terraform/`, `backend.generado.tf` y
  `generado/`.

### 51.16 Matriz final de aceptación, excepciones y evidencia del cierre (2026-10-21)

La tabla de §48.8 se conserva como foto del 2026-10-16. Esta es la matriz **final** de los criterios de la ficha (§6):
- «Cumplido» significa demostrado con la evidencia citada.
- «Con excepción» significa que el criterio **no se cumple tal como se redactó**: tiene una desviación respecto
  del requisito original y solo se cierra con la aceptación expresa del usuario al aprobar.
- No se declara cumplido nada que no se haya probado.

| # | Criterio | Estado final | Evidencia | Desviación aplicable |
| --- | --- | --- | --- | --- |
| 1 | Red y RDS privados | **Cumplido** | Red leída de la API antes de H-031-5 y de H-031-6 (§49.7 y §51.3): sin IGW, NAT, EIGW ni EIP; rutas solo `local` y el *gateway endpoint* de S3; `sg-rds` sin salidas y con entradas por referencia; subredes sin IP pública; RDS no pública y solo en `sg-rds` (§37.3). H-031-5 adjuntó `sg-admin` (§49.15). `sg-lambda` existe y lo adjunta `Task/032`, por diseño | — |
| 2 | TLS | **Cumplido** | `rds.force_ssl = 1` (`system`) en `blog-prod-postgres17`, con el grupo `in-sync`, leído por la API (§51.4). CA `rds-ca-rsa2048-g1` (§37.3). `ValidTill` de la CA registrado con `describe-certificates`, y el del certificado de servidor con `describe-db-instances` (ver la nota bajo la tabla). Sesiones `verify-full` reales, con TLSv1.3 y los tres controles negativos (§51.5) | En una sesión de RDS el ajuste no se lee con `current_setting`, que devuelve NULL. Se demuestra por la API y por el rechazo del servidor (validador autorizado el 2026-10-20, §51.4) |
| 3 | Cifrado `aws/rds` | **Cumplido** | RDS cifrada con `aws/rds` (§37.3); ninguna prueba deshabilita ni programa el borrado de una clave | — |
| 4 | Master ausente | **Cumplido** | `PRODUCTION_SECRET_ABSENT = true` en cada fase, en plan, state, salidas y archivos; también para `blog_migrate` y `blog_app` (§51.3 y §51.5) | — |
| 5 | Backups de 7 días, PITR activo | **Con excepción** | PITR activo y `LatestRestorableTime` avanzando: diagnóstico de B3 (§48.3) y preflights de H-031-7, con 189 a 281 s de retraso. PITR real con integridad (§51.8) | Retención de **1 día**: excepción temporal del plan FREE (§34); objetivo de 7 días al pasar al plan PAID |
| 6 | Identidad operativa mínima | **Con excepción** | Se opera con `PersonalBlogAdministrator` (§24). La identidad mínima `PersonalBlogDataOperator` se **creó y validó** en H-031-IAM con su bootstrap `bootstrap/operador-datos/`: 8 recursos, S-10 aplicada, simulación contra el rol real 62/62 y convergencia 0/0/0 (§17 a §24). Se conserva **sin uso operativo** | La identidad mínima no es el contexto operativo, por decisión del usuario del 2026-10-04 |
| 7 | Restore sintético y PITR | **Cumplido** | §51.8 a §51.10 y los registros de «Evidencia del cierre definitivo de H-031-7» | — |
| 8 | CloudWatch D-11; D-20 tras D-19 | **Con excepción** | Retención explícita de 14 días en los grupos de logs de PostgreSQL y de la ejecutora, confirmada por la convergencia (el refresh lee el valor real) y, en la ejecutora, por readback (§49.15). 8 alarmas, dentro del límite de 10, con readback 8/8 (§47). D-20 aplicado tras verificar D-19 para integrarlo (§47) | Alarmas sin acciones, **sin alertamiento efectivo**; fallo de backup con supervisión manual (B3); `memoria` en `ALARM` en reposo; D-20 solo con métricas. El alertamiento efectivo y la calibración de `memoria`, en `Task/040`, con **D-11 abierta**; **D-19 abierta**, con la comprobación al terminar el trial en `Task/041` |
| 9 | Convergencia 0/0/0 y paridad | **Cumplido, en los términos del criterio** | 0/0/0 tras cada apply en AWS: H-031-3 (§42.4), H-031-8 y H-031-9 (§47), H-031-5 (§49.15) y H-031-6 (§51.3). Matriz de paridad actualizada **sin declarar paridad completa** | No es una declaración de paridad; ver «Alcance real del criterio 9» |
| 10 | Serialización de D-24 | **Cumplido** | `pg_try_advisory_xact_lock(3364, 1)` en `identidades` y `sintetico`. En la integración local, otra sesión que tiene el bloqueo produce `OPERACION_EN_CURSO` sin escribir (§49). `identidades` lo tomó en producción (§51.5) | — |

**Nota sobre el criterio 2: vigencias, según el procedimiento de la decisión de arquitectura.** Son dos vigencias
distintas.
- **CA `rds-ca-rsa2048-g1`.** Se leyó con `describe-certificates`, en solo lectura, el 2026-10-21 a las 04:19Z;
  el resultado se guarda en privado como `h0320-describe-certificates-rds-ca-rsa2048-g1.json`.
  - Tipo `CA`, `ValidFrom` `2021-05-21T23:04:44Z` y **`ValidTill` `2061-05-22T00:04:44Z`**.
  - `Thumbprint` `8cf85e3e2bdbcbe2c4a34c1e85828fb29833e87f`.
  - Sin *override* de cliente; es la CA por omisión de los lanzamientos nuevos.
  - **Coincide exactamente** con la raíz `Amazon RDS us-east-2 Root CA RSA2048 G1` del bundle fijado (§51.15):
    mismas fechas y misma huella SHA-1.
- **Certificado de servidor de la instancia**, firmado por esa CA: `ValidTill` `2027-10-05T17:11:10Z`. Sale del
  `CertificateDetails` de `describe-db-instances` del 2026-10-20 a las 04:05Z (`h0320-h6-rds.json`, privado). RDS
  lo renueva automáticamente: no es la vigencia de la CA.

**Alcance real del criterio 9.**
- **Demostrado en AWS:** la convergencia 0/0/0 tras cada apply. Las normalizaciones del provider se absorbieron con
  refresh-only preautorizados y guardas cerradas (§47.7, §47.9, §49.15 y §51.3), y la deriva móvil de RDS, con la
  semántica aprobada de §40.
- **Demostrado en local (Floci):** el plano de control de la misma definición de Terraform. Se crea, es idempotente
  salvo las diferencias declaradas y se destruye.
- **Estado en la matriz de paridad** (`docs/architecture/aws-local-parity.md`), para los componentes de Task/031:

  | Estado | Componentes |
  | --- | --- |
  | `Paridad parcial` | SSM, Terraform, RDS (*mock*) y VPC |
  | `Compatible local` | CloudWatch Logs |
  | `AWS-only` | KMS, TLS, backups, PITR y restore |
  | `No evaluada` | Alarmas de D-11, ejecutora de D-24, ejecutora h0316 y rol de D-20 |

- **No demostrado, por estar fuera de alcance o ser imposible en local:**
  - el motor de RDS en Floci, que es un *mock* sin motor;
  - TLS, KMS, PITR y restore en local;
  - la equivalencia entre local y AWS de los componentes `No evaluada`;
  - el *failover*: la instancia es Single-AZ por diseño (ADR-010) y no se probó en ningún entorno.

  **No se declara paridad completa.**

**Excepciones que el usuario acepta al aprobar, y su seguimiento.**

| Excepción | Motivo | Impacto | Seguimiento |
| --- | --- | --- | --- |
| Backups de 1 día (criterio 5) | El plan FREE rechaza más de 1 día (`FreeTierRestrictionError`, §32 y §34) | PITR limitado a las últimas 24 h; el RPO no cambia | Excepción **temporal**: volver a 7 días al pasar al plan PAID (validación de `dias_de_retencion_de_backups` y `produccion.tfvars.example`, §34.1) |
| `PersonalBlogAdministrator` como identidad operativa (criterio 6) | Decisión del usuario del 2026-10-04 (§24) | Más privilegios que el mínimo diseñado; los mitigan las guardas cerradas, las sesiones de 1 h con MFA y la operación manual | Identidad autorizada; sin tarea abierta |
| Alarmas sin acciones, fallo de backup con supervisión manual y calibración de `memoria` pendiente (criterio 8) | SNS no está aprobado; RDS no publica un evento de backup fallido (B3, opción A, §48.3); `memoria` está en `ALARM` en reposo (§47.8) | Las alarmas no avisan; el fallo de backup se detecta a mano ([runbook](../runbooks/rds-backup-supervision.md)); `memoria` no discrimina | **D-11 sigue abierta** hasta que **`Task/040`** ([STAGE-12](../stages/STAGE-12-launch-and-operations.md)) implemente y verifique el alertamiento efectivo (canales aprobados, alarmas conectadas y recepción demostrada en una prueba segura) y la calibración de `memoria`, por decisiones del usuario del 2026-10-21 (§51.17). La supervisión manual sigue vigente |
| D-19 abierta (criterio 8) | El trial de Grafana Cloud no ha terminado | D-20 opera; los límites y el costo reales del plan gratuito están por confirmar | **`Task/041`**: la comprobación al terminar el trial |
| Exportación a S3 sin tablas de aplicación (limitación de la prueba) | Aún no hay migraciones (`Task/036`) | Probados el manifiesto, la escritura condicional, el *checksum* y el cifrado; **no** probada la exportación de datos reales | **`Task/036`**, con las primeras tablas, y **`Task/040`**, en la verificación final |

Además se consolidan con el `approved` estas decisiones ya aprobadas:
- D-24 modificada;
- la semántica de §40;
- el validador TLS (§51.4);
- R-12, con seguimiento en `Task/040` (§48.4);
- el orden de las fases (§47.3);
- la excepción del `.gitignore` (§51.15).

**Evidencia del cierre definitivo de H-031-7.** Registros locales sin versionar: los de `tmp/h0320/evidencia/` y, como
privados, los del directorio de datos de la aplicación.

| Hecho | Registro |
| --- | --- |
| Marcador retirado | `h0320-h0317-limpiar-20261021T022650Z.log` (privado): `limpiar` OK con `marcador_retirado: true`. `h0317-manifiesto.json`: `retiro_solicitado` y `marcador_retirado` en `true`, `t_limpieza` 2026-10-21T02:26:50Z |
| Marcador verificado ausente | `h0320-h0317-limpieza-verify-despues-20261021T022655Z.log` (privado): `verify --marcador` con `blog_migrate`, `presente: false`. También en `h0317-limpieza-1.log` |
| Cero temporales y residuos | `h0317-limpieza-1.log` (antes de escribir y comprobación final), `h0317-cierre.log` (02:28Z) y `h0317-cierre-confirmacion.log` (03:05Z): 0 instancias, backups automáticos, *snapshots* y grupos de logs. CloudTrail: un restore y un `DeleteDBInstance`, los dos aceptados |
| Productiva idéntica a su línea base | Los mismos tres registros. La línea base está en `h0317-linea-base.json` (privado), con su copia `.checkpoint-limpieza-20261021T022613Z.json` |
| Integridad, RPO y RTO | `h0317-informe-final.json` (privado): integridad `true`; RPO 180 s (objetivo 900); RTO 774 s (objetivo 14 400); costo de 0.0041 a 0.0046 USD; residuos 0. También `h0320-h0317-verificar-20261020T062748Z.log` y `h0320-h0317-informe-20261021T022703Z.log` |
| Manifiesto final | `h0317-manifiesto.json` (privado): `borrado_solicitado`, `ausente_por_api`, `retiro_solicitado`, `productiva_intacta` y `marcador_retirado` en `true`; `backups_automaticos_restantes = 0`; `verificacion.integridad = true`. La versión previa a la limpieza se conserva como `.checkpoint-limpieza-20261021T022613Z.json` |

**No repetido:** la ausencia del marcador no se volvió a comprobar después de las 02:27Z, para no invocar otra vez la
ejecutora. Todo lo demás se reconfirmó en solo lectura a las 03:05Z.

### 51.17 Alertamiento efectivo de RDS: traslado a `Task/040` (2026-10-21)

**Decisión del usuario del 2026-10-21.** El alertamiento efectivo de RDS pasa a ser responsabilidad de `Task/040`,
dentro de D-11:
- implementar destinatarios o canales de notificación aprobados;
- conectar las alarmas de RDS con esos canales;
- demostrar en una prueba segura la recepción efectiva de las alertas.

`Task/040` conserva también la calibración de `memoria` (§51.16). **D-11 sigue abierta** hasta que ambas capacidades
estén implementadas y verificadas. **D-19** sigue con su comprobación en `Task/041`.

**Dónde queda asumido:**
- [STAGE-12](../stages/STAGE-12-launch-and-operations.md), en la sección de `Task/040`: el alcance, la evidencia requerida y los criterios de
  aceptación de los dos asuntos, y dos criterios de salida nuevos de la etapa;
- la fila de `Task/040` del ROADMAP;
- la fila y la sección de D-11 en `open-decisions.md`.

No se modificó ninguna alarma ni ningún recurso en AWS, y no se promovió ninguna decisión que deba seguir abierta.

## 52. Aprobación y cierre (2026-10-21)

El usuario escribió **`approved: Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch`** después de revisar el cierre técnico,
las evidencias de H-031-6 y H-031-7, la matriz de aceptación (§51.16) y las excepciones documentadas. La fecha es
UTC, como el resto del cierre de la tarea; en America/Guatemala era la noche del 2026-10-20.

**Aceptación expresa de las excepciones.** El usuario aceptó las excepciones de los criterios **5**, **6** y **8**,
con sus restricciones, responsables y tareas de seguimiento tal como quedaron documentados en §51.16. Dejó escrito
que esa aceptación:
- **no cierra D-11 ni D-19**;
- **no autoriza cambios adicionales en AWS**.

**Comprobaciones previas al cierre:**
- la rama `Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch` existe y es la activa; nació de `main` `6c31d1d`, que
  coincide con `origin/main`, y no tenía commits propios;
- el entregable son 164 archivos —29 modificados y 135 nuevos—, sin cambios ajenos mezclados;
- **repositorio afectado:** solo `personal-blog-infra`; backend y frontend, **sin rama** e intactos en `main`;
- validaciones del entregable, todas en verde:
  - las 32 gates sin conexión: Terraform `fmt`, `init`, `validate` y `test` en los seis roots, las suites de
    Python, el Compose del laboratorio y `git diff --check`;
  - Gitleaks 8.30.1 sin hallazgos sobre los 428 archivos del entregable, con un control positivo de 3/3;
  - el ID de cuenta real, la cuenta de Grafana y el `ExternalId` del tfvars privado: 0 apariciones;
  - 2337 enlaces Markdown, 0 rotos;
  - todos los archivos en LF y sin BOM.

**Corrección de formato antes del commit.** `git diff --cached --check` detectó una línea en blanco sobrante al
final de tres archivos nuevos: `terraform-datos/outputs.tf`, `terraform/modulos/ejecutor_privado/outputs.tf` y
`terraform/modulos/exportacion/outputs.tf`. La gate `diff-check` no la veía: compara sin `--cached`, y los
archivos nuevos no estaban en el índice. Se quitó ese salto de línea sobrante. `terraform fmt -check` acepta las
dos variantes y la configuración no cambia. Después se repitieron las 32 gates, otra vez en verde.

**Lo que la aprobación promueve:**

| Elemento | Estado |
| --- | --- |
| **D-20** — integración `CloudWatch → Grafana Cloud` | **Resuelta**: rol `PersonalBlogLecturaGrafana`, con `sts:ExternalId` y solo métricas. `Task/040` valida datos y alertas |
| **D-11** | Sigue **Abierta**. Las notas de H-031-1 y H-031-8 quedan aceptadas; el alertamiento efectivo y la calibración de `memoria` son de `Task/040` (§51.17) |
| **D-19** | Sigue **Abierta**. La verificación previa a integrar queda aceptada; la comprobación al terminar el trial es de `Task/041` |
| Registro de decisiones | **5 abiertas** —D-07, D-11, D-12, D-19 y D-21—, **16 resueltas** y 3 cerradas por no aplicabilidad |
| Notas de `Task/031` en el [paquete de decisiones RDS](../architecture/production-postgresql-rds-decisions.md): custodia de `blog_migrate` y `blog_app`, entrega de credenciales, alarmas y enmienda a §12.2 | **Aceptadas** |
| §4.1.1.1 de [aws-local-parity](../architecture/aws-local-parity.md): `terraform-datos` como segundo *lifecycle* | **Vigente** |
| Runbooks [grafana-cloudwatch](../runbooks/grafana-cloudwatch.md) y [rds-backup-supervision](../runbooks/rds-backup-supervision.md) | **Vigentes** |
| Ampliaciones de `Task/031` en los cinco runbooks del laboratorio, en [rds-private-administration](../runbooks/rds-private-administration.md) y en la custodia de R-12 de [local-backup-and-recovery](../runbooks/local-backup-and-recovery.md) | **Aprobadas**; los runbooks siguen **Vigentes** |
| [identidad-operativa-datos.md](../architecture/identidad-operativa-datos.md) | **Implementada sin uso operativo**: la identidad operativa es `PersonalBlogAdministrator` (excepción 6) |
| ADR | **Ninguno nuevo** ni modificado |

Se consolidan también, ya aprobadas antes: D-24 modificada (2026-10-19), la semántica de §40, el validador TLS
(§51.4), R-12 con seguimiento en `Task/040` (§48.4), el orden de las fases (§47.3) y la excepción del `.gitignore`
(§51.15).

**Correcciones documentales al registrar la aprobación.** Ninguna cambia un criterio, una excepción ni un estado
aceptado:
1. **§51.16, fila del criterio 6, columna «Evidencia».** Decía que el bootstrap de la identidad de datos «no se
   aplicó». Era **inexacto**: `PersonalBlogDataOperator` se creó y validó en H-031-IAM (§17 a §24) y se conserva
   sin uso operativo. El estado «Con excepción» y la excepción aceptada no cambian.
2. **`identidad-operativa-datos.md`:** «Código (no aplicado)» pasa a «aplicado en H-031-IAM; sin uso operativo».
3. **`terraform-state-bootstrap.md` §3:** las filas de `terraform-datos` y `bootstrap/operador-datos` seguían en el
   estado de H-031-2 («state todavía ausente», «sin inicializar»); ahora registran el del cierre.
4. **`rds-private-administration.md` y el índice de runbooks** decían «no ejecutado» y que no existían RDS ni
   ejecutor; ahora registran lo ejecutado en H-031-6 y H-031-7.
5. **Ficha:** H-031-2 se marca completa —H-031-3 se autorizó sobre su plan guardado exacto (§27)—, igual que el
   cierre.
6. **STAGE-10** marca dos criterios de salida: **D-20 decidida** y los **runbooks ampliados a red y RDS antes de
   operar**. **No** marca, por falta de evidencia completa:
   - RDS no pública: no hubo un caso negativo activo de conexión;
   - TLS desde la Lambda de la aplicación (`Task/032`);
   - credenciales ausentes de los logs de CloudWatch;
   - la clave KMS de la temporal del PITR (`KmsKeyId`): solo se comprobó el cifrado activo.

**Avance:** **31/41 ≈ 76 %**. **ETAPA 10: 2/7 ≈ 29 %**. Quedan **10 pendientes**, de `Task/032` a `Task/041`.

**Seguimientos que siguen vivos** (§51.16):
- el alertamiento efectivo de RDS y la calibración de `memoria`, en `Task/040`, con **D-11 abierta**;
- D-19, en `Task/041`;
- R-12, en `Task/040`;
- la exportación con datos reales, en `Task/036` y `Task/040`;
- la retención de 7 días, al pasar al plan PAID;
- la supervisión manual de los backups (B3), vigente.

**La aprobación no crea recursos.** Tras ella no se ejecutó Terraform, ninguna operación de AWS ni la restauración
PITR.

**Flujo Git**, solo en `personal-blog-infra`, según [PROJECT_INSTRUCTIONS §8](../claude/PROJECT_INSTRUCTIONS.md):
1. un commit del entregable validado y un segundo commit que registra esta aprobación;
2. `dev` actualizado con `pull --ff-only` e integración de la rama Task con `merge --no-ff`;
3. publicación de `dev` y de la rama Task;
4. pull request **`Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch → main`** —nunca `dev → main`—, sin aceptarlo ni
   fusionarlo: eso es exclusivo del usuario;
5. vuelta a `main`, `fetch --prune`, `pull --ff-only` y `git branch -d` de la rama Task local, sin `-D` y sin
   tocar la rama remota.

La URL del PR y el estado final se entregan al usuario al terminar; GitHub es su fuente viva. `Task/032` **no se
inicia**: como toda Task, nace de `main` actualizado y limpio tras la normalización `main → dev`.

## 53. Mantenimiento de CI tras la aprobación (2026-10-22 a 2026-10-26)

**Por qué existe esta sección.** El primer CI del PR #57 (`Task/031 → main`) falló en S-09: la base de
vulnerabilidades de Trivy había publicado CVE nuevas de Go y de paquetes de sistema que afectaban al provider AWS
6.64.0, a la CLI de Terraform 1.16.2, a Traefik, a Floci 2.1.0, al derivado de MinIO y a Portainer. Ningún recurso de
AWS cambió: es mantenimiento de la cadena de suministro, en la **misma rama** y el **mismo PR**, sin tarea nueva. El
usuario fue autorizando cada decisión; ninguna aceptación se añadió sin su aprobación expresa.

**Lo que no cambia.** Ningún apply, refresh-only, destroy ni PITR en AWS. D-11 y D-19 siguen abiertas. Los commits
`0d137c5` y `e5daf78` se conservan; `terraform-datos/backend.generado.tf` sigue intacto y fuera de Git. `Task/032` no
se inicia.

### 53.1 Correcciones, una por causa

| Causa en S-09 | Corrección | Aceptaciones |
| --- | --- | --- |
| Provider AWS 6.64.0 (Go) | **6.70.0** en los seis roots, locks con los 16 `zh:` del `SHA256SUMS` firmado (`9ef4b34`) | ninguna |
| CLI de Terraform 1.16.2 (Go) | **1.16.7**, firma GPG de HashiCorp verificada; pines, hashes, `required_version` y guardas operativas. Las guardas de fases cerradas validan evidencia histórica y conservan 1.16.2 | **retira 9** del baseline |
| Traefik v3.7.13 | **v3.7.16** por digest; rutas y *healthchecks* idénticos | ninguna (tolerancia cero) |
| Floci 2.1.0 | **2.3.0** por digest, con la adaptación del laboratorio de §53.2 | **retira 2** del baseline |
| Derivado de MinIO: 18 identidades nuevas | **Contrato v3** (§53.3): pcre2 dentro del derivado, Go 1.27.3, `x/net` v0.60.0 y `klauspost/compress` v1.18.7 | ninguna; siguen las **10** de siempre |
| Portainer 2.45.1: 6 identidades nuevas | **2.45.3** y aceptación **temporal** de CVE-2026-95837 (§53.4) | **1 temporal**, con caducidad que hace cumplir la gate |

El baseline retira 11 identidades ya corregidas y añade exactamente una, temporal. Su diff de Terraform y Floci se
revisó antes de aplicarlo y se regeneró byte a byte (`2532b387…`) para comprobar que era el aprobado.

### 53.2 Floci 2.3.0: tres cambios de comportamiento, detectados fallando cerrado

El ciclo completo con 2.3.0 se detuvo tres veces, siempre en un control y nunca por un resultado dudoso:
1. **ID de zona:** `CreateSubnet` rechazó `us-east-1-az1`. 2.3.0 publica el formato de AWS (`use1-az1`, PR #5486).
   Cambia solo el valor de `terraform-datos/entornos/local/local.tfvars`.
2. **Runtime fijado:** no se observó ningún contenedor de Lambda. 2.3.0 los nombra `floci-aws-<función>-<id>`
   (PR #4273). `PREFIJO_DEL_EMULADOR` pasa a `floci-aws-` con la misma estrechez, y una prueba nueva rechaza los
   nombres de 2.1.0.
3. **Idempotencia de datos:** la deriva de `aws_db_instance` cambió. Ya no difiere `enabled_cloudwatch_logs_exports`,
   que 2.3.0 devuelve, y avanza `latest_restorable_time`, como en AWS. Además dejaron de ocurrir 6 de las 12 clases
   de `resource_changes`. Dos controles negativos existentes, `test_menos_atributos_que_los_declarados` y
   `test_otro_atributo_de_la_instancia_rds`, describían justo ese rechazo.

Con la autorización del usuario y el diff revisado (`d955b19d…`, regenerado byte a byte antes de aplicarlo):
- la entrada de `aws_db_instance` exige `latest_restorable_time` con la forma nueva `instante_movil`, que replica el
  contrato temporal aprobado para AWS (§40): `antes ≤ después ≤ ahora` y frescura de un día. Una prueba exige que
  las dos implementaciones decidan igual;
- las 6 tolerancias que ya no ocurren se **retiran**;
- 6 pruebas nuevas cubren los casos negativos del instante móvil y el atributo aprobado.

El plan real del 2026-10-24 se acepta evaluado en su momento y se rechaza evaluado días después, porque deja de ser
fresco.

**Ciclo completo final (2026-10-26), en una copia aislada:** CICLO COMPLETO con exit 0.
- Creación de los tres roots e idempotencia: aplicación con exit 0; datos con exit 2 y **solo** las 6 clases y las
  16 entradas declaradas.
- Deriva controlada.
- Dos *destroy* con ausencia comprobada por API, reconstrucción y *smoke* HTTP 200.
- El contenedor del runtime fijado se observó.

Los states locales, que conservaban entradas de los ciclos interrumpidos, quedaron **reconciliados a 0 recursos por el
propio ciclo**, sin borrar ningún archivo de state.

### 53.3 MinIO: contrato v3 del derivado reproducible

- **pcre2 dentro del derivado, sin cambiar la base.** Una etapa `paquetes` sobre `ubi9/ubi` fijada por digest
  descarga `pcre2` y `pcre2-syntax` 10.40-7.el9_8 por URL fija y verifica el SHA-256 y la firma de Red Hat (release
  key 2). Después aplica `rpm --root -Uvh --noscripts --excludedocs`.
- **Determinismo sin `libfaketime`.** `rpm` 4.16 honra `SOURCE_DATE_EPOCH` de forma nativa: `INSTALLTID` = epoch e
  `INSTALLTIME` = epoch + orden en la transacción. La primera versión del diseño congelaba el reloj con
  `libfaketime`. La aserción de determinismo detectó un segundo de diferencia, que resultó ser ese comportamiento
  nativo; el diseño final lo usa y retira `libfaketime`, su RPM de EPEL y su clave.
- **Una capa declarada, exacta.** La transacción se mide antes y después. La delta (`269386…`, 10 entradas) se fija
  por hash, y la etapa final aplica exactamente esa delta. El manifiesto declara los **17 miembros** de la capa:
  archivos con hash y tamaño, enlaces con destino, dos *whiteouts* y sus antecesores, todos con modo y propietario.
- **Go:** toolchain 1.27.3 y dos parches incrementales. La resolución de módulos cambió **solo** `x/net` y
  `klauspost/compress`, sin arrastrar ninguna otra dependencia. `libcap` y `libacl` no se actualizan: siguen
  aceptadas.
- **Verificador v3** (`scripts/minio/artifact.py`). Exige:
  - las 9 capas heredadas, la de paquetes con sus miembros exactos y una capa por binario;
  - que la receta aplique los RPM, el medidor y la delta declarados.

  El atestado incorpora el resumen de paquetes, y la gate S-09 lo compara contra constantes escritas en ella.
  Hay 17 pruebas nuevas con controles negativos.
- **Reproducibilidad.** Dos construcciones independientes del candidato, sin caché y con el BuildKit de CI, dieron el
  mismo manifiesto `sha256:95b28f31…` y el mismo OCI byte a byte. La receta del repositorio, construida otras dos
  veces como en CI, dio el mismo digest y el mismo OCI (`a3767049…`); `verify` y `compare` del contrato v3 en verde.
- **Prueba funcional y S-09.** El contenedor desechable pasó versiones, `coreutils` con la `libpcre2` nueva,
  *health* y el ciclo real de bucket y objeto. S-09 dio 0 identidades nuevas y las 10 aceptadas, idénticas.
- **Publicación en GHCR**, autorizada y condicionada a lo anterior: hecha el 2026-10-26 por la API de distribución
  con los bytes validados, sin reconstruir.
  - 9 blobs ya estaban y se subieron 4.
  - El manifiesto, de 2844 bytes, es idéntico al leerlo de vuelta.
  - `docker pull` sin copia local devuelve `sha256:95b28f31…`.
  - Las identidades de Task/027.1 y Task/028 siguen intactas, y el paquete sigue privado.

  `.env.example` apunta a la identidad nueva por etiqueta y digest.

La identidad de Task/028 pasa a `supersedes` con la de Task/027.1 anidada tal cual: ninguna se mueve ni se
sobrescribe.

### 53.4 Portainer 2.45.3 y caducidad técnica de las excepciones temporales

**Verificación previa (2026-10-26):**
- No hay versión posterior a 2.45.3: `sts`, `lts` y `latest` apuntan al índice
  `sha256:3609c307943bca8e5c492f69ddd6965df177208b50678a4cff28391c8dd4e96e`.
- `containerd/v2` sigue en v2.2.5, indirecta, en 2.45.3 y en `develop`.
- El binario, extraído sin ejecutarlo, es el ya analizado (`14826671…`). Ninguno de sus 19 paquetes de
  `containerd/v2` es CRI: `internal/cri`, `pkg/cri`, `plugins/cri`, `k8s.io/cri-api`, `RuntimeService` y `go-criu`
  tienen 0 apariciones, con un control positivo que demuestra que el método las encontraría.
- El despliegue escucha solo en `127.0.0.1:9444`, con `cap_drop: ALL`, `no-new-privileges` y raíz de solo lectura.
- El host no tiene Kubernetes ni el modo experimental de Docker.

**Aceptación temporal, opción (b) del usuario.** Se acepta **solo** la identidad exacta de CVE-2026-95837
(`containerd/v2` v2.2.5, corregida en 2.2.7 y 2.3.4), con `temporary: true`, `review_on: 2026-11-06` y
`expires_after: 2026-11-30`. Las 4 aceptaciones históricas de Portainer no cambian.

**La caducidad la hace cumplir la gate**, no un proceso:
- `scripts/security/vulnerability_gate.py` falla si una aceptación temporal venció, si falta una fecha, si una
  fecha es inválida, si la revisión es posterior al vencimiento o si hay fechas sin `temporary: true`;
- el día del vencimiento todavía vale, y desde el siguiente bloquea CI aunque el hallazgo ya no aparezca;
- las aceptaciones históricas no se ven afectadas.

Hay 13 pruebas positivas y negativas, y una más fija que la del baseline real es la única temporal.

### 53.5 Validaciones del entregable

| Validación | Resultado |
| --- | --- |
| 32 gates sin conexión: `fmt`, `init`, `validate` y `test` de los seis roots con la CLI 1.16.7 y el provider 6.70.0, las cinco suites de Python con la invocación de CI, el Compose del laboratorio y `git diff --check` | **ALL OFFLINE GATES PASSED**. `terraform test`: datos 54, medios 7, `github-oidc` 9, `terraform-state` 5 y `operador-datos` 7. Python: `terraform_datos` 725, laboratorio 335, seguridad 120, OIDC 62, con la omisión POSIX de siempre en Windows, y `terraform_state` 12 |
| Laboratorio completo con Floci 2.3.0, en una copia aislada | **CICLO COMPLETO**, exit 0 (§53.2), y states reconciliados a 0 |
| S-09 como CI, con la base de Trivy del 2026-10-25. Portainer y Floci se escanearon desde el registro, MinIO desde el OCI construido y atestado, y Postgres y Traefik reconstruidos como CI | **RESULTADO: CORRECTO**: 15 hallazgos comparados y 0 nuevos. La comprobación de coherencia también es correcta. El provider 6.70.0 tiene 0 accionables |
| Derivado MinIO | Cuatro construcciones con el mismo digest, `verify`, `compare`, `attest`, prueba funcional y publicación verificada (§53.3) |
| Gitleaks 8.30.1 sobre los 431 archivos del entregable | Sin hallazgos |
| ID de cuenta real, cuenta de Grafana y `ExternalId` | 0 apariciones |
| Enlaces Markdown de los siete documentos modificados | 444 enlaces, 0 rotos |
| Finales de línea | Los 49 archivos cambiados o nuevos, en LF y sin BOM |

El único valor privado del tfvars que aparece en el entregable es el ARN del bucket de medios, en el reporte de
Task/030. Es preexistente en `main`, y este mantenimiento no lo toca.

### 53.6 Publicación

**Flujo Git**, en la misma rama y el mismo PR, según
[PROJECT_INSTRUCTIONS §6 a §8](../claude/PROJECT_INSTRUCTIONS.md) y el permiso expreso del usuario:
1. Cinco commits incrementales sobre `9ef4b34`:
   - versiones y baseline de Terraform y Floci, con la adaptación del laboratorio;
   - caducidad técnica de la gate;
   - derivado MinIO v3;
   - Portainer 2.45.3;
   - este registro.
2. Push normal de la rama, sin *force*, y revisión de todos los checks del PR #57, tanto `push` como
   `pull_request`.
3. Integración en `dev` con `merge --no-ff` y publicación de `dev`.
4. El PR #57 sigue abierto: su fusión hacia `main` es exclusiva del usuario. Después viene la normalización
   `main → dev`.

GitHub es la fuente viva del estado de los checks.

> **Complemento del 2026-10-27 (`Task/031.1`).** El punto 4 describía el estado que se observó al escribir este
> registro, el 2026-10-26. Según [WORKFLOW §6.1](../project-management/WORKFLOW.md#61-estado-duradero-frente-a-estado-transitorio),
> el estado vivo de un PR no se versiona como vigente, así que se conserva aquí solo como esa observación. Las fechas
> son UTC, como el resto del cierre ([§52](#52-aprobación-y-cierre-2026-10-21)).
>
> *Observado el 2026-10-27:* el PR #57 se fusionó en `main` con el merge `1fdc843`, la normalización
> `main → dev` es `f833014` y la rama Task031 se eliminó en local y en remoto. El CI de `main` y el de `dev`
> terminaron en `success`.
