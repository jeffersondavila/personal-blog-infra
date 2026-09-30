# Bootstrap D-06 — bucket de estado Terraform

**Runbook de Task/030; tarea Lista para validación (2026-09-29) y aprobación final pendiente.**
El usuario autorizó `authorize: Task/030 H-030-1`: el plan revisado quedó **aplicado
y verificado el 2026-09-28**, con siete recursos y sin cambios/destrucciones.
H-030-2 se detuvo por metadata y drift del primer state migrado. Después del
diagnóstico y plan revisado, **H-030-4-refresh-apply autorizó aplicar únicamente
ese binario**: state actualizado, mismo lineage y serial 1→2, infraestructura 0/0/0.
Nuevo plan normal exit 0, 0/0/0, drift 0, checks pass. **El state OIDC se migró
después bajo la misma autorización H-030-2** y quedó validado sin necesidad de
refresh-only: convergencia exit 0, 0/0/0, drift 0, ocho checks pass e IAM real
intacto (§15 del reporte). Después se demostraron la **contención del locking
nativo** y el **recovery por versión** de ambas keys, con 0 desviaciones y sin crear
versiones nuevas (§16). Después se retiraron los states locales como fuentes
operativas, se eliminó el scaffolding de la prueba y **EX-028-C7 quedó Extinguida el
2026-09-28**: S3 es la única fuente operacional de ambos roots y **H-030-2 está
COMPLETO** (§17). No repetir/revertir ninguna migración ni ejecutar nuevos applies.
Evidencia en el [reporte](../task-reports/TASK-030-report.md#7-ejecución-autorizada-de-h-030-1).
Inicio: **2026-09-27, America/Guatemala**. Revalidación de esta propuesta: **2026-09-28**.

## 1. Propiedad y alcance

Root único: [bootstrap/terraform-state](../../bootstrap/terraform-state/main.tf).
Terraform **1.16.2**, provider oficial **6.64.0**, lock de Windows/Linux igual al
bootstrap OIDC. No se invoca el grafo de aplicación ni su lanzador `production`.
D-06 sigue **Resuelta desde Task/025**: aquí se materializa, no se redefine.

| Recurso | Dirección Terraform | Protección aplicada y verificada |
| --- | --- | --- |
| BPA de cuenta | `aws_s3_account_public_access_block.account` | **GLOBAL**, todas las regiones; cuatro flags `true` |
| Bucket dedicado | `aws_s3_bucket.state` | `force_destroy=false`; solo Terraform state |
| BPA de bucket | `aws_s3_bucket_public_access_block.state` | Cuatro flags `true` explícitas |
| Ownership | `aws_s3_bucket_ownership_controls.state` | `BucketOwnerEnforced`, ACL deshabilitadas |
| Versionado | `aws_s3_bucket_versioning.state` | `Enabled` |
| Cifrado | `aws_s3_bucket_server_side_encryption_configuration.state` | SSE-S3, `AES256` explícito |
| Policy | `aws_s3_bucket_policy.state` | Deny `s3:*` con `aws:SecureTransport=false`, bucket y objetos |

Los siete recursos tienen `prevent_destroy=true`. Es una guarda de Terraform,
no una prohibición IAM de borrado ni protección contra retirar la declaración del código.
No hay recursos IAM, KMS, DynamoDB, CORS, objetos S3 ni lifecycle de expiración.
No se aplica el lifecycle de medios de Task/025 al state. Se conservan todas las
versiones; Task/041 revisará crecimiento y costo, sin borrado automático.

Las cuatro flags, en ambos niveles, son `block_public_acls`, `block_public_policy`,
`ignore_public_acls` y `restrict_public_buckets`. El bucket depende del BPA de cuenta.
La policy solo **deniega** HTTP; no concede acceso ni exige `SourceVpce`.
La autorización sigue dependiendo de IAM. No se introduce una policy pública.

Tags del **bucket**: `Proyecto=personal-blog`, `Entorno=produccion`,
`Gestion=terraform`, `Componente=terraform-state`, `Tarea=Task/030`.
Los recursos de configuración y el BPA global no tienen tags independientes.

## 2. Nombre y destino

Región del bucket y provider: **us-east-2**, fijada en el root, sin endpoint alternativo.
Bucket creado: **`personal-blog-tfstate-us-east-2-9bcb34ac5bcf`**.
Sufijo: primeros 12 caracteres hexadecimales de SHA-256 de
`personal-blog:terraform-state:<cuenta-verificada>:us-east-2`.
Es determinístico, sin aleatoriedad ni datos personales en el nombre. No se publica
el Account ID para conseguir unicidad; el hash tampoco se presenta como un secreto.
Antes del apply autorizado, `HeadBucket` dio **404**; no reservaba el nombre.
Después dio **200** con el dueño esperado y región Ohio. La regla de precreación
era detenerse ante 200, 301, 403 ambiguo o colisión, sin probar sufijos.
No volver a aplicar el plan de creación: ya quedó consumido.

Identidad humana: perfil `personal-blog`, sesión STS de `PersonalBlogAdministrator`.
El provider restringe `allowed_account_ids` y una postcondición exige ese rol y
workspace `default`. `PersonalBlogGitHubOidcValidation` nunca opera este root.

## 3. Estado del propio bootstrap y keys

| Root | Backend en esta fase | Destino remoto previsto |
| --- | --- | --- |
| `bootstrap/terraform-state` | S3 efectivo y validado; convergencia 0/0/0, drift 0, serial 2 | `bootstrap/terraform-state/terraform.tfstate`, nueva versión tras refresh-only autorizado |
| `bootstrap/github-oidc` | S3 efectivo y validado; convergencia 0/0/0, drift 0, serial 1 | `bootstrap/github-oidc/terraform.tfstate`, primera y única versión |
| `terraform-medios` | S3 efectivo; plan normal 0/0/0, drift 0 (2026-09-29) | `application/media/terraform.tfstate`; nunca una de las dos keys de bootstrap |
| Aplicación | Sin inicializar contra AWS en esta fase | Se fijará en su checkpoint; nunca una de las dos keys de bootstrap |

**Root de medios: volver del laboratorio sin tocar su state.** El laboratorio reutiliza
el directorio `terraform-medios/` y le genera `backend.generado.tf` con `backend "local"`.
Antes de cualquier operación productiva sobre ese root:

1. STS con el perfil `personal-blog` en `us-east-2`. Si falla, **parar** y renovar con
   `aws login --profile personal-blog --region us-east-2`.
2. Regenerar `terraform-medios/backend.generado.tf` con solo `terraform { backend "s3" {} }`.
   Es un archivo ignorado por Git.
3. Con `TF_DATA_DIR` en `%LOCALAPPDATA%/PersonalBlog/application/media/terraform-data`,
   `TF_WORKSPACE=default` y `AWS_PROFILE=personal-blog`:
   `terraform -chdir=terraform-medios init -reconfigure -input=false -lockfile=readonly`
   con `-backend-config=` apuntando al `remote.tfbackend` de ese directorio privado.
4. Comprobar la metadata —`s3`, key `application/media/terraform.tfstate`, `us-east-2`,
   `encrypt`, `use_lockfile`, sin DynamoDB ni KMS— y que las tres keys conservan VersionId
   y no tienen `.tflock`.
5. Plan normal esperado: **0/0/0 con `resource_drift = 0`**.

Aquí `-reconfigure` es lo correcto porque **no hay nada que migrar**: el state del
laboratorio pertenece a otro destino. Nunca `-migrate-state`, `-force-copy`, `state push`,
`state mv` ni `state rm`, ni aceptar una copia del state local del laboratorio a S3.
Aplicado el 2026-09-29: §27.6 del [reporte](../task-reports/TASK-030-report.md).

Directorio privado del bootstrap:
`%LOCALAPPDATA%/PersonalBlog/bootstrap/terraform-state/`.
El state local original `terraform.tfstate` se conserva como evidencia protegida;
`terraform-data/` contiene metadatos/providers y apunta a S3. **Parada humana
tras validar el primer bootstrap:** no usar la copia local como segundo backend.
Plan binario, JSON y logs están en este mismo directorio,
**fuera de todos los checkouts Git**, incluso los ignorados.

ACL NTFS comprobada: herencia deshabilitada y acceso solo al usuario propietario
y `SYSTEM`, heredable a archivos/subdirectorios. Se rechazan rutas con reparse points.
**Reconfirmado el 2026-09-28** por medición directa: herencia deshabilitada, dos ACEs
explícitas (`SYSTEM` y el propietario) y **sin acceso** de `CodexSandboxUsers`. Un
informe anterior de esta tarea afirmó lo contrario por medir el directorio ancestro;
quedó rectificado en §17.6 del reporte. El root del bootstrap OIDC **sí** heredaba ese
acceso y se endureció aparte (§18 del reporte).
La ACL es control de acceso, **no prueba cifrado de disco**; BitLocker/EFS no se
declaran verificados. Nunca se escriben credenciales en HCL, tfvars o backend config.
La configuración privada contiene solo el Account ID esperado, no credenciales.
El apply creó el state local de **serial 8**, siete recursos administrados y un
data source. H-030-2 copió recursos/outputs a S3 con otro lineage y serial 1.
Tras el diagnóstico y autorización humana, el refresh-only actualizó únicamente
el state remoto a **serial 2**, conservó ese lineage y dejó convergencia sin drift.
La cadena remota está técnicamente validada; historia y versiones en el reporte.
El state OIDC repitió el mismo reinicio de lineage/serial al copiarse —serial 6
local, 1 remoto— con recursos, outputs y check_results idénticos, y **no requirió
refresh-only**: su plan de convergencia ya salió sin drift.

H-030-1 escribió el primer state local, conservado en la ruta privada. H-030-2 creó
backups AES256 de ambos roots mediante GPG con frase humana privada: descifrado,
integridad y hashes idénticos demostrados antes de migrar. Se conservan las copias
y la evidencia; la validación del primer bootstrap no sustituye esos backups. Un fallo parcial obliga a conservar
ese state y capturar su backup; no se repite el apply ni se crea otro backend a ciegas.
El state local OIDC dejó de ser el backend operativo al migrarse, pero **se conserva
intacto** en su ruta privada junto a su `.backup` histórico; su archivado formal como
backup inactivo pertenece al cierre de H-030-2.

## 4. Comandos de la fase de preparación

Esta fase preparatoria ya se ejecutó; los comandos se conservan como referencia,
no como instrucción para repetir el apply. Desde la raíz de infra, con sesión humana
vigente. Las variables siguientes son
rutas, no secretos. El directorio privado, su ACL y `bootstrap.tfvars.json` deben
existir y estar verificados; no usar `init` sin la configuración local explícita.

```powershell
$Task030Private = Join-Path $env:LOCALAPPDATA 'PersonalBlog/bootstrap/terraform-state'
$Task030Terraform = Join-Path $env:LOCALAPPDATA 'personal-blog-infra/herramientas/terraform-1.16.2/windows_amd64/terraform.exe'
$Task030Aws = 'C:\Program Files\Amazon\AWSCLIV2\aws.exe'
$env:TF_DATA_DIR = Join-Path $Task030Private 'terraform-data'
$env:TF_WORKSPACE = 'default'
$env:TF_IN_AUTOMATION = '1'
$env:CHECKPOINT_DISABLE = '1'
$env:AWS_EC2_METADATA_DISABLED = 'true'
$env:AWS_IGNORE_CONFIGURED_ENDPOINT_URLS = 'true'
# El bloque provider no declara profile y el perfil se resuelve por login_session,
# sin perfil default: sin esta variable el provider no encuentra credenciales.
# El destino sigue acotado por allowed_account_ids y la postcondicion de identidad.
$env:AWS_PROFILE = 'personal-blog'

& $Task030Aws sts get-caller-identity --profile personal-blog --region us-east-2
& $Task030Terraform -chdir=bootstrap/terraform-state fmt -check -recursive
& $Task030Terraform -chdir=bootstrap/terraform-state init -input=false -lockfile=readonly "-backend-config=$Task030Private/local.tfbackend"
& $Task030Terraform -chdir=bootstrap/terraform-state validate
& $Task030Terraform -chdir=bootstrap/terraform-state test
```

`local.tfbackend` contiene únicamente `path` con la ruta absoluta privada del
state futuro. La sesión AWS la resuelve el perfil, nunca ese archivo.
Para generar un plan **nuevo** —no sobrescribir el plan revisado—:

```powershell
& $Task030Aws sts get-caller-identity --profile personal-blog --region us-east-2
& $Task030Terraform -chdir=bootstrap/terraform-state plan -input=false -no-color -lock-timeout=30s -detailed-exitcode "-var-file=$Task030Private/bootstrap.tfvars.json" "-out=$Task030Private/review-new.tfplan"
```

Código 2 significa cambios propuestos, **no aplicación**. Código 1 es fallo.
El JSON se obtiene con `terraform show -json` y se escribe directamente como UTF-8
en un archivo privado, sin imprimirlo ni usar la redirección UTF-16 de PowerShell 5.
La [guarda offline](../../scripts/terraform_state/check_plan.py) verifica su contenido:

```powershell
python -B scripts/terraform_state/check_plan.py "$Task030Private/h0301-final-20260928T142104Z.json" --variables "$Task030Private/bootstrap.tfvars.json"
```

El resultado se vincula al SHA-256 del binario que produjo ese JSON. Antes de un
apply autorizado se regenera el JSON **desde ese binario**, se verifica el hash,
fuentes, identidad, inventario y vigencia. Cualquier diferencia se presenta al usuario.
No usar `-target`, `-replace`, import, operaciones `terraform state` ni flags de
desbloqueo para sortear un fallo. Esta fase no ofrece un comando de apply automático.

## 5. IAM necesario, sin crear ni adjuntar políticas

La sesión actual es el rol humano existente; esta fase **no modifica IAM**. La
lista es el contrato mínimo operativo por función, no evidencia de que un principal
con una policy nueva haya sido probado. H-030-1 ejerció las operaciones de gestión
S3 con el rol humano existente; permisos sobre objetos state/lock y recuperación
se verificarán en H-030-2, sin ampliar IAM automáticamente.

| Función | Acciones | Alcance |
| --- | --- | --- |
| Control global | `s3:GetAccountPublicAccessBlock`, `s3:PutAccountPublicAccessBlock` | `Resource="*"`; operación sobre la cuenta verificada; no es permiso sobre cualquier bucket |
| Crear/configurar bucket | `s3:CreateBucket`, `s3:PutBucketTagging`, `s3:PutBucketVersioning`, `s3:PutBucketOwnershipControls`, `s3:PutBucketPublicAccessBlock`, `s3:PutEncryptionConfiguration`, `s3:PutBucketPolicy` | ARN exacto del bucket; creación en `us-east-2` |
| Lecturas del provider y verificación | `s3:ListBucket`, `s3:GetBucketLocation`, `s3:GetBucketTagging`, `s3:GetBucketVersioning`, `s3:GetBucketOwnershipControls`, `s3:GetBucketPublicAccessBlock`, `s3:GetEncryptionConfiguration`, `s3:GetBucketPolicy`, `s3:GetBucketPolicyStatus`, `s3:GetBucketAcl` | Mismo ARN exacto |
| Lecturas adicionales del recurso `aws_s3_bucket` 6.64.0 | `s3:GetAccelerateConfiguration`, `s3:GetLifecycleConfiguration`, `s3:GetBucketRequestPayment`, `s3:GetBucketWebsite`, `s3:GetBucketCORS`, `s3:GetBucketLogging`, `s3:GetBucketObjectLockConfiguration`, `s3:GetReplicationConfiguration` | Mismo ARN; el provider consulta controles aunque no se creen |
| State, por root | `s3:GetObject`, `s3:PutObject` | Solo su key exacta |
| Lock, por root | `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` | Solo `<key>.tflock` |
| Descubrimiento del backend | `s3:ListBucket` | Prefix de su estado y listado `env:/` que usa Terraform para descubrir workspaces; solo `default` operativo |
| Recuperación autorizada | `s3:ListBucketVersions`, `s3:GetObjectVersion` | Bucket/key correspondientes; lectura de versiones sin borrarlas |

No hace falta `s3:DeleteObject` sobre el **state**, `s3:DeleteObjectVersion`,
`s3:DeleteBucket`, DynamoDB ni KMS para operar este diseño. No ampliar IAM por
comodidad si una acción falla: registrar la acción y abrir H-030-4.
Cada identidad futura de CI tendrá permisos sobre su propia key; los roles de
Task/038/039 son distintos del rol de validación.

Inventario de esta fase, separado de provisión: `s3:ListAllMyBuckets`,
`dynamodb:ListTables` en Ohio y las lecturas IAM `GetRole`, `ListRolePolicies`,
`ListAttachedRolePolicies`, `GetOpenIDConnectProvider`. No se concede ninguna aquí.

## 6. H-030-2: migración parcial y procedimiento pendiente

H-030-1 y su readback están completos. **H-030-2 incompleto**: backups verificados
y **ambos** bootstrap remotos validados —el primero tras el refresh-only autorizado,
el OIDC sin necesitarlo—, los dos con convergencia 0/0/0 y drift 0. **No ejecutar
los pasos siguientes sin nueva instrucción humana**. La prueba de contención y el
recovery **ya se ejecutaron y pasaron** (§16 del reporte): dos operadores sobre la
misma key, lock confirmado por lectura, segunda operación rechazada por error de
adquisición del state lock con `PutObject` 412 `PreconditionFailed`, una sola versión
de `.tflock` para las dos operaciones, liberación normal y state intacto.
Los ciclos normales de lock de init/apply/plan nunca sustituyeron esa prueba.
El procedimiento acordado, conservado como referencia, exige:
Congelar escrituras, confirmar un solo operador y ningún proceso Terraform,
inventariar serial/lineage/recursos, crear backups cifrados verificables fuera de
Git y comprobar que las keys de destino estén ausentes o expliquen su contenido.

Ambas migraciones ya se ejecutaron **secuencialmente**, primero este bootstrap y
después OIDC; los comandos se conservan como referencia, no para repetirlos.
Para cada root,
reemplazar el bloque `backend "local" {}` por `backend "s3" {}`, conservando su
`TF_DATA_DIR` previo y, por tanto, la referencia al origen. Usar la
[plantilla sin credenciales](../../bootstrap/terraform-state/backend-s3.tfbackend.example)
en configuración privada con cuenta/bucket/key verificados.
Comandos previstos, que **no están autorizados en H-030-1**:

```powershell
# Solo tras authorize: Task/030 H-030-2 y revisión de los dos comandos completos.
& $Task030Terraform -chdir=bootstrap/terraform-state init -migrate-state -lockfile=readonly "-backend-config=$Task030Private/remote.tfbackend"
# Cambiar TF_DATA_DIR al directorio efectivo OIDC verificado en H-030-2.
# Su backend config debe usar bootstrap/github-oidc/terraform.tfstate.
& $Task030Terraform -chdir=bootstrap/github-oidc init -migrate-state -lockfile=readonly "-backend-config=$Task030OidcPrivate/remote.tfbackend"
```

No `-force-copy`, no `-reconfigure` para eludir la migración, ni edición manual
del JSON de state. Cada migración exige comparar lineage/serial/direcciones/hash,
versión S3 y plan de convergencia; el OIDC debe seguir con sus dos recursos y cero drift.
Un plan no vacío después de migrar exige H-030-4. La regla de no cerrar EX-028-C7
prematuramente se respetó: la excepción se extinguió **después** de verificar
convergencia, contención de locking y recovery.

**Rollback si falla:** suspender ambos operadores; conservar estados de origen,
remoto y backups, con metadatos. Si el destino no se escribió, conservar el origen
como único backend activo y diagnosticar antes de reintentar. Si pudo escribirse,
no volver automáticamente al local: comparar lineage/serial/recursos y escoger un
único autoritativo mediante H-030-4. Nunca ejecutar dos backends a la vez.

**Recuperación y locking, ya demostrados en H-030-2 (§16); el procedimiento se
conserva como referencia operativa:** descargar una versión concreta a
una ubicación privada aislada, verificar hash/lineage/serial/direcciones y lectura
del snapshot sin conectarlo como backend activo. Para demostrar contención, mantener
un lock nativo de Terraform en una operación controlada y observar que otra falla
por lock; liberar por terminación normal de la primera. El procedimiento exacto y
sus escrituras `.tflock` se revisan en H-030-2. No `force-unlock` ni locks fabricados.
Verificar ausencia del lock actual al terminar y existencia de versiones recuperables.
La prueba de recuperación no borra ni sustituye versiones autoritativas.

Solo después de verificar remoto, convergencia, locking y recuperación se archivan
los locales como **backups inactivos protegidos**, se retira su configuración operativa
y se extingue EX-028-C7. Las cuatro verificaciones y las dos acciones **ya están
hechas** (2026-09-28, §17): los locales viven en
`%LOCALAPPDATA%\PersonalBlog\bootstrap-backups\INACTIVE-HISTORICAL-STATES\` con
manifiesto y marcador, sus `local.tfbackend` quedaron retirados y renombrados, y la
excepción está **Extinguida**. Sigue sin haber **ningún apply de aplicación**, que es
alcance de tareas posteriores.

## 7. Costos y fuentes

Investigación oficial y cálculo reproducible:
[TASK-030-research.md](../task-reports/TASK-030-research.md).
Reserva estimada del backend operativo: **USD 0.12/mes bruto**, escenario de
1 GB total de versiones, 1.000 PUT/LIST, 1.000 GET y 1 GB de egress facturable.
No es una cuota fija ni el costo del futuro bucket de medios. El bucket vacío no
consume almacenamiento; sus requests de configuración sí deben considerarse.
No se altera D-13, EX-029-D13, Billing ni el plan de cuenta.

## 8. Verificación visual futura

H-030-1 ya materializó los controles bajo autorización. Inspección opcional en AWS Console:

| Ruta | Valor esperado |
| --- | --- |
| S3 → Block Public Access settings for this account | Cuatro opciones activadas; alcance global |
| S3 → Buckets → nombre revisado → Properties | Región Ohio, versionado Enabled, SSE-S3 |
| Mismo bucket → Permissions → Block public access | Cuatro opciones activadas |
| Permissions → Object Ownership | Bucket owner enforced; ACL deshabilitadas |
| Permissions → Bucket policy | Una denegación de transporte no TLS, sin Allow público |
| Management → Lifecycle rules | Sin reglas de expiración |
| Objects | Vacío tras H-030-1; keys de bootstrap solo después de H-030-2 |

Es inspección: no editar opciones ni crear objetos manualmente. Login/MFA lo
completa el usuario; no se muestran snapshots ni valores sensibles en capturas.
