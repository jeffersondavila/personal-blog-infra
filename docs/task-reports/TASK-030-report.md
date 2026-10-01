# TASK-030 — Reporte de ejecución

**Aprobada — 2026-09-29**, mediante `approved: Task/030-Desplegar-Amazon-S3` (§28). Llegó
como **`Task/030 — READY FOR FINAL APPROVAL`** el mismo día. Bucket de
medios creado, verificado y convergente —**0/0/0, `resource_drift = 0`**—; DEF-030-1,
DEF-030-2 y DEF-030-3 corregidos; ciclo real, `crear`, `validar` y `destruir` reales sobre los
dos roots; laboratorio retirado sin residuos; contexto productivo de `terraform-medios`
restaurado sin migrar ningún state; gates en verde. El entregable final del backend incluye
también la reparación de CI MinIO/GHCR y urllib3 **2.8.0** con excepción de índice por
paquete: **6 archivos, +222 / −14**. Checkpoint técnico en §27; aprobación e inventario
final en §28.

*Cabecera anterior, conservada como historia:*
**En progreso. H-030-1 completado; H-030-4-refresh-apply completado y verificado.**
El usuario autorizó aplicar el binario refresh-only exacto de §13. Aplicado una
sola vez, sin cambios de infraestructura; nueva versión S3, mismo lineage y serial
1→2. El nuevo plan normal terminó **exit 0, 0/0/0 y cero resource_drift** (§14).
Primer bootstrap remoto técnicamente validado. **Parada antes de OIDC**, por orden
humana; H-030-2 completo sigue pendiente. Originales/backups intactos; sin recovery.
Inicio local **2026-09-27, America/Guatemala**. Reanudación y cierre de esta fase:
**2026-09-28**, America/Guatemala; evidencia técnica fechada en UTC.
[Ficha](../tasks/TASK-030-deploy-amazon-s3.md) ·
[Runbook](../runbooks/terraform-state-bootstrap.md) ·
[Investigación/auditoría](TASK-030-research.md).

## 1. Cronología y autorizaciones

1. Preflight de los tres repositorios: limpios/sincronizados, sin Task/030;
   Task/029 y 029.1 integradas; main/dev de infra normalizados.
2. Rama creada desde main `db6e9c7804cbf8f8afcb5fcbd8b7ec8cd8dfd485`.
   Backend/frontend permanecen en main; cero commits de Task.
3. **BLOCKER de sesión:** STS devolvió sesión expirada. Se detuvo el trabajo AWS.
   El usuario renovó `personal-blog` y autorizó continuar la primera fase.
4. STS confirmó el rol humano esperado. ListBuckets vacío;
   `GetPublicAccessBlock` de cuenta devolvió `NoSuchPublicAccessBlockConfiguration`.
5. **H-030-4:** se presentó la diferencia frente al control cuenta+bucket de STAGE-10.
   El usuario eligió **opción 1** y autorizó añadir `aws_s3_account_public_access_block`
   al **diseño y plan solamente**, con las cuatro flags en true. Sin mutaciones.
6. Inventario restante y comparación OIDC con state custodiado; investigación
   oficial; bootstrap, pruebas, custodia privada del plan y documentación.
7. Plan real del root independiente: **7 add / 0 change / 0 destroy**, código 2,
   cero warnings de Terraform; guarda offline `PLAN_OK`.
8. Reanudación desde el árbol local existente: 20 archivos, HEAD/base sin cambios,
   sin commits ni rama remota ni PR de Task/030. Backend/frontend limpios. Una nueva
   expiración STS produjo BLOCKER; el usuario renovó la sesión y autorizó continuar.
9. El 2026-09-28 se verificaron otra vez identidad/inventario y se repitieron los gates.
   El snapshot del plan original coincide byte a byte con los cinco `.tf` y el lock;
   las variables coinciden, y el backend sigue local con ruta externa explícita.
10. Se conserva el candidato original y se genera otro plan real con nombre distinto,
    sesión renovada y configuración final; resultado idéntico 7/0/0, sin warnings.
11. Parada inicial H-030-1: todavía sin autorización de apply/migración/publicación.
12. El usuario escribió `authorize: Task/030 H-030-1` y autorizó únicamente aplicar
    el binario identificado. Preflight repetido y apply completado; readback independiente
    de AWS/state, sin recursos adicionales. Detalles y siguiente checkpoint en §§7–8.

## 2. Inventario read-only e identidad

**Snapshot previo al apply**; inventario posterior en §7.

| Elemento | Observación real |
| --- | --- |
| Identidad | Perfil `personal-blog`; sesión STS `PersonalBlogAdministrator/personal-blog-entry-admin`, cuenta esperada comparada privadamente |
| Región | `us-east-2` explícita en CLI y fija en el provider |
| Buckets S3 de la cuenta | **0** en ListBuckets |
| BPA de cuenta | Ausente; hallazgo H-030-4 aceptado para diseño/plan |
| DynamoDB Ohio | **0 tablas**; no se infiere ausencia en otras regiones |
| Rol OIDC | `PersonalBlogGitHubOidcValidation`; 3600 s; **0 attached, 0 inline**, sin permissions boundary |
| Trust OIDC | Igual al state custodiado; subject exclusivo `main`, audiencia `sts.amazonaws.com` |
| Proveedor OIDC | `token.actions.githubusercontent.com`, client ID `sts.amazonaws.com` |
| State OIDC | Local externo; serial **6**, **2 recursos administrados + 1 data source**, Terraform 1.16.2; hash intacto |
| SHA-256 state OIDC | `8fc01b3e797298bc7eec4eb7b36dcc72b805ae61886a287e7e9186c5f8e872aa` |
| Nombre propuesto | HeadBucket **404**, verificado de nuevo `2026-09-28T14:19:18.707984+00:00`; no reservado |

Último inventario completo: `2026-09-28T14:19:18.707984+00:00`.
La identidad se comprobó antes de cada operación de inventario y antes del plan.
STS acredita identidad, no acredita por sí mismo MFA; el login fue humano.
No se ejecutó inventario general de todos los servicios/cuentas/regiones.
Los únicos recursos preexistentes pertinentes observados son proveedor/rol OIDC;
se usó la sesión del rol administrativo ya existente, sin modificarlo.

## 3. H-030-1 — autorización de bootstrap D-06

**Checkpoint histórico presentado antes del apply**; autorización/ejecución en §7.

Nombre: **`personal-blog-tfstate-us-east-2-9bcb34ac5bcf`**, generado con el hash
determinístico descrito en el runbook. Región: **us-east-2**.

Direcciones exactas del plan, todas con acción **create**:

```text
aws_s3_account_public_access_block.account
aws_s3_bucket.state
aws_s3_bucket_ownership_controls.state
aws_s3_bucket_policy.state
aws_s3_bucket_public_access_block.state
aws_s3_bucket_server_side_encryption_configuration.state
aws_s3_bucket_versioning.state
```

**Alcance GLOBAL de cuenta** del primer recurso: cuatro flags `true`, para todas las
regiones y buckets presentes/futuros. Las mismas cuatro flags están explícitas en el
bucket: `block_public_acls`, `block_public_policy`, `ignore_public_acls`,
`restrict_public_buckets`. No es un control limitado a Ohio.

Versionado **Enabled**; cifrado **SSE-S3/AES256**; ownership **BucketOwnerEnforced**,
ACL deshabilitadas. Policy: una denegación `s3:*` para transporte no TLS sobre el
bucket y sus objetos, sin Allow público ni SourceVpce. Sin CORS ni lifecycle de
expiración; todas las versiones se conservan. Siete `prevent_destroy=true` y
`force_destroy=false` en bucket. Tags: Proyecto/Entorno/Gestion/Componente/Tarea,
con valores exactos en el runbook. **Sin DynamoDB, KMS ni recursos IAM**.

Outputs: nombre del bucket, región, dos keys futuras y mapa de configuración S3
con `encrypt=true`, `use_lockfile=true`. Ese mapa **no es aún el backend activo**.

State del bootstrap: backend **local** inicializado con ruta externa privada,
ACL solo usuario/SYSTEM; el state operacional todavía **no existe**.
Destino futuro `bootstrap/terraform-state/terraform.tfstate`; OIDC conserva
`bootstrap/github-oidc/terraform.tfstate`. H-030-2 revisará/autorizará cada migración
secuencial y la recuperación. **EX-028-C7 no extinguida**.

Permisos de gestión S3 y state/lock por key, separados de inventario y recuperación:
[runbook §5](../runbooks/terraform-state-bootstrap.md#5-iam-necesario-sin-crear-ni-adjuntar-políticas).
Incluye `s3:PutAccountPublicAccessBlock` de alcance global. No se adjunta ninguna policy.

Costo: **USD 0.1184 ≈ 0.12/mes bruto** en el escenario holgado del
[cálculo](TASK-030-research.md#4-costo-bruto-incremental-del-bootstrap), sin descontar
créditos/franquicia de egress. Sin cargo fijo nuevo; configuración inicial estimada
menor de USD 0.001 bajo el supuesto de requests indicado. Créditos/desembolso separados.

**Plan final:** terminado `2026-09-28T14:21:32.484433+00:00`. Código 2 y `PLAN_OK`.
Fuentes `.tf` y lock del binario comparados byte a byte con el filesystem final;
variables y backend privado verificados. No hubo cambios plan-relevantes durante
la reanudación; se renovó el plan para fecharlo con la sesión/inventario actuales.

| Artefacto privado final | SHA-256 |
| --- | --- |
| `h0301-final-20260928T142104Z.tfplan` | `1b7961fb11cfa39542bb27afef294332b49fbbe4124fc94c8afe72cbc7605cef` |
| `h0301-final-20260928T142104Z.json`, obtenido de ese binario | `1ec611d7f4e0e7b066af6830b1f514a576b9e26e47e897de5a5fd47c18d8b6a0` |

El candidato anterior se conserva **solo como evidencia histórica**, no como plan
final autorizado: `h0301.tfplan`, SHA-256
`6ae0056a2d85ae8c55ddd4891fe2e021899f7855fa7c84a208c0658fe8ddb528`;
`h0301-plan.json`, SHA-256
`d73e05abc767cba637e25a0dcc25e79925f6b7edfabeefae23b1eaa8efa730cf`.

Ubicación privada: `%LOCALAPPDATA%/PersonalBlog/bootstrap/terraform-state/`.
El JSON, log y binario no se publican ni entran en Git/artifacts.

**Resultado:** 7 altas, 0 cambios, 0 destrucciones; 0 reemplazos, 0 importaciones,
0 recursos de aplicación y 0 modificaciones OIDC. Terraform **sin warnings**.
Avisos operativos: BPA global, disponibilidad del nombre no reservada, versiones
sin caducidad y pruebas reales de seguridad/locking/recovery todavía pendientes.
`terraform version -json` informó `terraform_outdated=true`: se conserva la versión
exacta fijada por el proyecto, no se actualiza silenciosamente ni se afirma ausencia de CVE.

**Solicitud presentada y posteriormente autorizada:** `authorize: Task/030 H-030-1`.
Solo el apply de este plan, sujeto
a comprobar hash, fuentes, identidad y ausencia de diferencias. No migración.

## 4. Gates de preparación

Resultados anteriores al apply; el código Terraform y los tests no cambiaron al ejecutarlo.

| Gate | Resultado |
| --- | --- |
| CLI/lock | Terraform 1.16.2, binario idéntico al ZIP oficial con SHA fijado; AWS 6.64.0 instalado con firma HashiCorp; lock Windows/Linux verificado |
| Nuevo bootstrap | fmt e init con lock readonly; validate OK; **5 planes simulados PASS** |
| Guarda del plan | **12 pruebas PASS**; controles negativos de delete/replace/import/IAM/alcance/BPA/TLS/KMS/lock; plan real `PLAN_OK` |
| Terraform aplicación existente | fmt/validate OK; init `-backend=false` en TF_DATA_DIR aislado; no plan ni apply de aplicación |
| Bootstrap OIDC existente | fmt/validate OK; **9 planes simulados PASS**, sin usar su backend operacional |
| Guardas laboratorio | **176 pruebas OK**; la salida de error argparse es una prueba negativa esperada |
| Guardas OIDC | **60 ejecutadas, OK; 1 skip** de plataforma; no se presenta como 60 PASS |
| Backend storage/API | **155 passed**, `-W error`; contratos de ObjectStorage sobre MinIO real local con ambos adaptadores, sin AWS |
| Guardas seguridad | **88 pruebas OK** en `tests/security` |
| CI Infra | Nuevo paso auditado: fmt/init backend=false/validate/test mock y unittest offline; sin identidad AWS, id-token ni despliegue. Ejecutado localmente con archivos de credenciales/config AWS nulos. No se publica ni dispara CI remoto |
| Texto y Git | `git diff --check`, UTF-8/LF, sin BOM/controles y sin archivos privados en los 20 entregables: PASS |
| Enlaces y anclas | **171 documentos Markdown**, enlaces relativos y anchors verificados; 0 errores |
| Encabezados | **29 duplicados heredados en el árbol Markdown completo**, iguales a HEAD; **0 nuevos** |
| Grafo | **41 tareas canónicas**, dependencias existentes/anterioridad, sin ciclos; Task/031 depende de 030 |
| Secretos | Gitleaks **8.30.1**, **103 commits** y snapshot de **279 archivos versionables actuales**, incluidos los **14 nuevos**: **0 hallazgos**, redacción completa |
| Custodia | Plan/JSON/log/state fuera de Git; ACL usuario/SYSTEM y sin reparse points en ancestros; state operacional nuevo ausente; state OIDC sin cambios |
| Lock nuevo | Existe, idéntico al de OIDC, AWS 6.64.0; `.gitignore` lo incluye explícitamente. `??` porque aún no hay staging/commit autorizado; no está perdido ni ignorado |

Incidencias de herramientas locales: una lectura Python falló al imprimir Unicode
en cp1252; se corrigió la salida a UTF-8. El primer wrapper de pytest no encontró
el ejecutable por ruta relativa en Windows; **no ejecutó pruebas**. Repetido con
`sys.executable` absoluto: 155 passed. No hubo fallo de Terraform validate/tests/plan.
En la reanudación, un wrapper buscó `tests/seguridad` en lugar de `tests/security`;
no ejecutó esa suite, que luego pasó con su ruta real (88). Otro comparó el total
de entradas del state con el número de recursos administrados: se corrigió el
filtro a `mode=managed`; eran los mismos 2 recursos más el data source de identidad,
con hash/serial intactos. Ninguno fue un cambio o fallo funcional AWS/backend.

## 5. Entregable y límites

Cambios: root `bootstrap/terraform-state/`, guarda/tests, paso CI **offline**, exclusión
del lock en `.gitignore`, ficha/reporte/investigación/runbook e índices de gobierno.
`terraform/` y root OIDC existentes sin cambios; backend/frontend sin cambios.

Auditoría de VPS/D-16 y drift: [investigación](TASK-030-research.md#1-contrato-recuperado-del-repositorio).
D-06 continúa Resuelta; D-08 abierta; decisiones RDS y EX-029-D13 intactas.
Avance **29/41 ≈ 71 %**, ETAPA 10 **En progreso, 0/7 aprobadas**.

**Hasta presentar H-030-1 hubo cero mutaciones AWS.** Después de autorizarlo se
aplicaron exclusivamente sus siete recursos (§7). Sin migración, import, destroy,
`-target`, operaciones `terraform state`, cambios IAM o Billing.
No se creó VPC/RDS/Lambda/API ni infraestructura de aplicación; Task/031 no iniciada.
No se ha validado aún el backend remoto, el locking, recovery ni S3Storage contra S3 real.
No commit, push, PR o merge; aprobación final pendiente.

## 6. Snapshot Git al presentar H-030-1

Observación fechada **2026-09-28**; no es una condición permanente del repositorio.
Rama `Task/030-Desplegar-Amazon-S3`, HEAD/main/origin-main
`db6e9c7804cbf8f8afcb5fcbd8b7ec8cd8dfd485`. Cero commits nuevos,
sin rama remota de la tarea ni PR asociado. Backend/frontend limpios y sin cambios.

**20 archivos: 6 modificados y 14 nuevos**, ninguno staged. No se usa la cifra
aproximada recuperada de la interfaz. `git diff --stat` muestra solo los tracked:

```text
.github/workflows/ci-infra.yml            | 11 +++++++++++
.gitignore                              |  1 +
docs/project-management/ROADMAP.md        | 12 ++++++++----
docs/project-management/STATUS.md         | 18 ++++++++++++++----
docs/runbooks/README.md                   |  1 +
docs/stages/STAGE-10-cloud-deployment.md   | 14 +++++++++-----
6 files changed, 44 insertions(+), 13 deletions(-)
```

`git status --short --untracked-files=all`, inventario completo del entregable:

```text
 M .github/workflows/ci-infra.yml
 M .gitignore
 M docs/project-management/ROADMAP.md
 M docs/project-management/STATUS.md
 M docs/runbooks/README.md
 M docs/stages/STAGE-10-cloud-deployment.md
?? bootstrap/terraform-state/.terraform.lock.hcl
?? bootstrap/terraform-state/backend-s3.tfbackend.example
?? bootstrap/terraform-state/main.tf
?? bootstrap/terraform-state/outputs.tf
?? bootstrap/terraform-state/providers.tf
?? bootstrap/terraform-state/tests/protections.tftest.hcl
?? bootstrap/terraform-state/variables.tf
?? bootstrap/terraform-state/versions.tf
?? docs/runbooks/terraform-state-bootstrap.md
?? docs/task-reports/TASK-030-report.md
?? docs/task-reports/TASK-030-research.md
?? docs/tasks/TASK-030-deploy-amazon-s3.md
?? scripts/terraform_state/check_plan.py
?? tests/terraform_state/test_plan.py
```

Las 14 altas se contabilizan aparte porque aún no están en el índice. Los archivos
auxiliares de gates/exportación y Gitleaks permanecen bajo `tmp/` ignorado; no son
entregables ni contienen planes o states operacionales. Se conservaron los detalles
históricos de aprobación en STATUS y se corrigió su próxima tarea a 031, pendiente.

## 7. Ejecución autorizada de H-030-1

Autorización humana exacta: `authorize: Task/030 H-030-1`. El usuario restringió la
operación al plan final ya revisado y prohibió migración, medios y publicación.

Antes de aplicar se repitieron STS (cuenta esperada y rol humano), HeadBucket **404**,
SHA-256 binario/JSON, comparación byte a byte de fuentes/lock y guarda 7/0/0.
Backend local externo, state operacional ausente y ACL usuario/SYSTEM comprobados.
Se añadió inventario read-only IAM/KMS para comparar antes/después, sin conceder permisos.

Se ejecutó **una sola vez**, sin regenerar el plan y sin flags de reemplazo/target:

```text
terraform -chdir=bootstrap/terraform-state apply -input=false -no-color -lock-timeout=30s <ruta-privada>/h0301-final-20260928T142104Z.tfplan
```

Inicio `2026-09-28T14:45:25.605971+00:00`; fin `2026-09-28T14:45:38.654856+00:00`. **Código 0**:
**7 added, 0 changed, 0 destroyed**, **0 warnings de Terraform**.
SHA-256 del binario aplicado, intacto:
`1b7961fb11cfa39542bb27afef294332b49fbbe4124fc94c8afe72cbc7605cef`.
Log privado `h0301-apply-20260928T144525Z.log` fuera de Git. El plan de creación ya está consumido;
no se reutiliza para otro apply.

Readback completado `2026-09-28T14:51:51.787969+00:00`, con identidad comprobada antes de cada
API. Los **siete recursos exactos de §3** coinciden con AWS y con el state:

| Control | Evidencia AWS posterior |
| --- | --- |
| Bucket | HeadBucket 200, dueño esperado; LocationConstraint us-east-2; único bucket de la cuenta |
| BPA global | Cuatro flags true; **alcance GLOBAL**, no limitado a Ohio |
| BPA bucket | Cuatro flags true explícitas |
| Versioning | Enabled |
| Cifrado | SSE-S3 / AES256; sin KMSMasterKeyID |
| Ownership/ACL | BucketOwnerEnforced; ACL leída con un solo grant FULL_CONTROL al dueño |
| Policy/TLS | JSON igual al plan: Deny s3:* con aws:SecureTransport=false sobre bucket/objetos |
| Acceso público | GetBucketPolicyStatus: IsPublic=false; no se atribuyen pruebas anónimas de objetos todavía |
| Tags | Proyecto=personal-blog; Entorno=produccion; Gestion=terraform; Componente=terraform-state; Tarea=Task/030 |
| Lifecycle | NoSuchLifecycleConfiguration; sin expiración de versiones |
| Contenido | 0 objetos, 0 versiones, 0 delete markers; aún no hay state ni locks remotos |
| DynamoDB / KMS Ohio | 0 tablas y 0 claves antes/después |
| Inventario IAM global | Mismos 5 roles, 1 usuario, 0 policies locales y 1 proveedor OIDC; conjuntos de identidades iguales |
| Rol OIDC | Trust igual al state custodiado; 0 attached, 0 inline, sin boundary, 3600 s; proveedor OIDC conservado |

State local nuevo: `%LOCALAPPDATA%/PersonalBlog/bootstrap/terraform-state/terraform.tfstate`.
Terraform **1.16.2**, serial **8**, lineage
`4fd2e0b1-9a72-5648-171c-4d6b2f4e95ad`, **7 recursos administrados + 1 data source**.
SHA-256: `d60d661687eeaa39d59bc65a42a020009f1948085734c3a1e16f75b497beb3b6`.
Backend local verificado, sin lock local residual. ACL del state/logs limitada a
usuario/SYSTEM; sin reparse points en ancestros y fuera de los tres repositorios.
No se imprimió contenido del state ni se ejecutaron comandos `terraform state`.
El state OIDC conserva su hash de §2 y serial 6; sus metadatos locales apuntan a la
ruta privada original `github-oidc/terraform-data/`, sin reinicialización.

**Observación del metadata de checks:** `var.expected_account_id=pass`, pero
`data.aws_caller_identity.human=unknown` en el snapshot posterior al apply, sin
mensajes de fallo. La postcondición fue **pass en el plan autorizado**; el data
source está en `prior_state` del plan, sin operación propia en `resource_changes`.
Se verificaron de forma independiente la identidad STS actual y la identidad
persistida (cuenta/rol/sesión coinciden con el plan); workspace default explícito.
No se reescribió el state ni se afirma que ese metadata sea pass. El primer
verificador auxiliar exigía pass a todo check y falló por esa suposición; quedó
corregido para comprobar los valores y registrar este unknown explícitamente.
Esto no implicó cambios en Terraform, el plan, los recursos o sus guardas.
La [implementación oficial de Terraform 1.16.2](https://raw.githubusercontent.com/hashicorp/terraform/v1.16.2/internal/terraform/transform_diff.go)
construye el grafo apply a partir de los cambios; la ausencia de este data source
entre ellos es consistente con que no se reevaluase en ese grafo. Esta última
explicación es una inferencia del código, separada de los hechos verificados.

## 8. H-030-2 — checkpoint previo a migración

**Snapshot histórico anterior a la autorización.** Ejecución y bloqueo actuales en §§9–10.

**Presentado, pendiente de autorización; no iniciado.** Los dos backends siguen
locales. No se cambió ningún bloque backend ni se ejecutó init -migrate-state.

| Root / origen privado autoritativo | Destino en el bucket de state ya creado |
| --- | --- |
| terraform-state/terraform.tfstate; serial 8; 7 recursos | bootstrap/terraform-state/terraform.tfstate |
| github-oidc/terraform.tfstate; serial 6; 2 recursos | bootstrap/github-oidc/terraform.tfstate |

Los destinos están ausentes: el bucket está vacío. En ambos se propone región
us-east-2, encrypt=true, **use_lockfile=true**, perfil humano personal-blog y cuenta
permitida explícita. **Sin DynamoDB, IAM nuevo, KMS ni infraestructura de aplicación.**

La autorización solicitada para la siguiente fase sería secuencial y acotada:

1. Confirmar un único escritor y sesión vigente; capturar nuevamente hashes,
   lineage/serial y destinos. Crear **backups cifrados** de ambos states fuera de
   Git con la custodia humana GPG existente, y demostrar descifrado/integridad.
   Estos backups de migración **todavía no se han creado ni declarado verificados**.
2. Cambiar solo el backend de terraform-state y migrarlo con la configuración
   privada exacta, conservando su TF_DATA_DIR operacional; verificar objeto/version,
   metadata y plan de convergencia sin cambios antes de avanzar.
3. Repetir con OIDC, conservando su TF_DATA_DIR privado y sin cambios de rol/proveedor.
4. Demostrar locking nativo mediante operaciones Terraform controladas y recuperación
   de una versión a una ubicación aislada; sin force-unlock, sin state push/rm/mv,
   sin sustitución destructiva del snapshot autoritativo.
5. Archivar los locales como backups inactivos solo tras verificar el remoto; cerrar
   EX-028-C7 únicamente al completar esas pruebas. Cualquier diferencia abre H-030-4.

**No autorizado aún:** `authorize: Task/030 H-030-2`. H-030-1 no lo sustituye.
Costo incremental de servicios sin cambio respecto del diseño H-030-1; el consumo
S3 pasaría a incluir objetos/versions/locks/requests de state. Sin cambios de Billing.
D-06 continúa Resuelta, D-08 abierta, EX-028-C7 no extinguida, Task/030 En progreso,
29/41 ≈ 71 %, ETAPA 10 0/7 aprobadas. Sin Task/031, bucket de medios, commit, push,
PR ni merge.

## 9. H-030-2: preflight y backups verificados

El usuario autorizó `authorize: Task/030 H-030-2`, con orden secuencial y parada
obligatoria ante cualquier inconsistencia. Dos verificaciones posteriores STS
indicaron sesión expirada y se detuvo sin mutar. Tras renovación humana, STS pasó
el 2026-09-28: perfil personal-blog, rol PersonalBlogAdministrator, cuenta esperada,
región us-east-2. No había otros procesos Terraform locales ni locks locales.
Las operaciones Terraform se ejecutaron por un solo operador y secuencialmente;
no se afirma haber inspeccionado procesos de otras máquinas.

Preflight `2026-09-28T17:16:19.270963+00:00`: bucket/dueño/región correctos; las **dos keys de
state y las dos .tflock** devolvieron 404 antes de escribir. Ambos backends eran
locales y apuntaban a los states privados esperados. OIDC conserva las direcciones
exactas `aws_iam_openid_connect_provider.github[0]` y `aws_iam_role.validation`.

Se prepararon dos snapshots privados, cada uno con state, lock del provider,
configuración Terraform y manifiesto de hashes. Cifrado GnuPG 2.4.9 **AES256**,
con frase introducida exclusivamente por el usuario en pinentry-w32, sin batch,
sin cache de clave y sin frase en argumentos/variables/chat. Descifrado posterior
independiente para cada archivo: **DECRYPTION_OKAY + GOODMDC**, tar byte a byte
idéntico, **7/7 archivos internos** verificados y state igual al original.
Verificación terminada `2026-09-28T17:20:20.952949+00:00`; **antes de init -migrate-state**.
Las copias están fuera de Git bajo el directorio privado protegido del bootstrap:
`h0302-backups/20260928T171739Z/`. No se afirma una copia adicional fuera del equipo.

| Backup cifrado | SHA-256 ciphertext | SHA-256 state verificado al descifrar |
| --- | --- | --- |
| terraform-state.tar.gpg | `dcb4b567d59a338ca55518716fda639b3cc11b373cf4e374930fd8b165c9c078` | `d60d661687eeaa39d59bc65a42a020009f1948085734c3a1e16f75b497beb3b6` |
| github-oidc.tar.gpg | `3e56b27112613002dfa0824c96b55dbf83a5487df75d316a2c6959fe33044715` | `8fc01b3e797298bc7eec4eb7b36dcc72b805ae61886a287e7e9186c5f8e872aa` |

## 10. H-030-4 — metadata diferente tras primera migración

Solo se cambió `bootstrap/terraform-state/versions.tf` a backend S3 parcial y se
creó su configuración privada: bucket previsto, key
`bootstrap/terraform-state/terraform.tfstate`, us-east-2, perfil personal-blog,
cuenta permitida explícita, encrypt=true, use_lockfile=true, sin DynamoDB ni KMS.
Se conservó el TF_DATA_DIR operacional para que Terraform conociera el origen local.

La invocación fue:

```text
terraform -chdir=bootstrap/terraform-state init -migrate-state -input=true -lock-timeout=30s -lockfile=readonly -no-color -backend-config=<configuración-privada>/remote.tfbackend
```

Terraform presentó su pregunta normal para copiar el state. Solo después de
reconocer esa pregunta exacta se respondió yes bajo la autorización H-030-2;
**sin -force-copy, sin -reconfigure**. Inicio `2026-09-28T17:22:44.163473+00:00`;
fin `2026-09-28T17:22:50.320311+00:00`; código **0**, inicialización completada,
**0 warnings**, lock del provider sin cambios. El éxito del comando no se confundió
con la validación de la migración.

El readback descargó la versión S3 concreta y encontró una diferencia de hash.
**Se detuvo antes del plan de convergencia y antes de tocar OIDC.** Comparación
posterior exclusivamente de lectura, `2026-09-28T17:25:43.817540+00:00`:

| Campo | Snapshot local original | Objeto S3 posterior |
| --- | --- | --- |
| SHA-256 | `d60d661687eeaa39d59bc65a42a020009f1948085734c3a1e16f75b497beb3b6` | `23fe10851e8a105c7039a696288a9e874a051b31ada03092ff62a2fcd3868a11` |
| Lineage | `4fd2e0b1-9a72-5648-171c-4d6b2f4e95ad` | `d33d9c1e-bd73-b176-0907-ae7cf352a50b` |
| Serial | **8** | **1** |
| Recursos completos | 7 administrados + data source | **Idénticos** al original |
| Outputs | Originales | **Idénticos** |
| check_results | Originales | **Distintos** |
| Terraform version | 1.16.2 | Igual |

Versión S3: `sobXiO3qAh6OUKjOVTrgaufL.0o1_Cap`; SSE-S3/AES256. Las únicas diferencias
JSON de nivel superior son **check_results, lineage y serial**. No se publican
atributos ni contenido sensible del state. La causa y la aceptación de esta nueva
identidad de snapshot **no se han resuelto automáticamente**. No se editó ningún
state, no se sobrescribió el remoto y no se revirtió el backend.

Estado operativo congelado:

- `terraform-state`: metadata del backend apunta a **S3**; objeto presente, pero
  migración **no aceptada como validada**. Original local y backups conservados.
- `github-oidc`: backend **local** original; serial 6, lineage/hash intactos;
  destino remoto todavía ausente. No se modificó su código ni se migró.
- Ambas keys `.tflock` ausentes. Sin locks residuales observados.
- **No ejecutados:** convergencia, segunda migración, prueba de contención nativa,
  recuperación de versión remota y retiro de los locales como fuentes operativas.
- La descarga de diagnóstico no se presenta como prueba completa de recovery.
- **EX-028-C7 no extinguida.** D-08 y medios sin iniciar; Task/031 no iniciada.
- Sin apply adicional, cambios IAM/Billing, state push/rm/mv, force-unlock,
  import/destroy, commit, push, PR o merge.

**Parada H-030-4.** Conservar todos los artefactos; no aplicar planes previos ni
usar el local como segundo escritor. H-030-2 permanece incompleto y requiere
resolver esta discrepancia antes de continuar. No se atribuye cero drift: el
plan de convergencia no llegó a ejecutarse.

## 11. H-030-4 — DIAGNÓSTICO DE METADATA DE MIGRACIÓN

### 11.1. Dictamen y alcance de la evidencia

**Clasificación B: comportamiento defectuoso presente en Terraform v1.16.2.**
La migración copia el metadata del origen correctamente en memoria, pero la
persistencia posterior lo descarta al volver a consultar una key S3 ausente.
El contenido de recursos y outputs se conserva. La diferencia de check_results
es exclusivamente el orden de dos elementos; no es pérdida ni reevaluación de checks.
No se afirma que el defecto se introdujera en esta versión, sea exclusivo de ella
o esté reconocido mediante un issue de HashiCorp.

El diagnóstico combinó lectura del código oficial fijado, logs y artefactos
privados existentes y consultas STS/S3. **No se ejecutó Terraform**, ni se escribió
en AWS, ni se modificaron configuraciones/backend/state. Solo se agregó evidencia
de diagnóstico fuera de Git y esta documentación. H-030-2 sigue detenido.

Código del tag oficial **v1.16.2**, resuelto al commit
`82e042fb6372443813f6759056308d6adc642fa1`. Se contrastaron byte a byte los seis
archivos principales descargados por tag y por commit; coincidieron. Las fuentes
y sus SHA-256 se conservan en el directorio ignorado
`tmp/task030/source-v1.16.2/`, manifiesto SOURCE-MANIFEST.json. No se usó main.
La [referencia oficial del tag](https://api.github.com/repos/hashicorp/terraform/git/ref/tags/v1.16.2)
permite resolver la misma revisión.

También se comparó, sin ejecutarlo, el terraform.exe usado por el wrapper con el
incluido en el [ZIP oficial 1.16.2 para Windows amd64](https://releases.hashicorp.com/terraform/1.16.2/terraform_1.16.2_windows_amd64.zip):
bytes idénticos. SHA-256 ZIP
`6ef140ce1d399dc43b8315194176ddc2dfb5c21d607968e82ef20a55cfff40d0`;
SHA-256 executable
`d51f533398d3bb2df73ffd85fd5c1af3e8db15433018fe818ce816248290fe96`.

### 11.2. Ruta del código exacto

| Pregunta | Resultado y evidencia oficial v1.16.2 |
| --- | --- |
| ¿El gestor local implementa Migrator? | **Sí.** Local.StateMgr devuelve un Filesystem, no un wrapper que pierda esa interfaz. Filesystem declara la interfaz y StateForMigration devuelve una copia del statefile completo. [backend local, líneas 260–288](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/backend/local/backend.go#L260-L288), [Filesystem, líneas 66–69](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/states/statemgr/filesystem.go#L66-L69) y [405–406](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/states/statemgr/filesystem.go#L405-L406). |
| ¿El gestor S3 implementa Migrator? | **Sí.** S3 devuelve remote.State, que declara Migrator. [S3, líneas 179–187](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/backend/remote-state/s3/backend_state.go#L179-L187), [remote.State, líneas 51–53](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/states/remote/state.go#L51-L53). |
| ¿Qué hace Migrate con ambos gestores? | Lee StateForMigration del origen y llama WriteStateForMigration del destino, con copia de lineage/serial. No se toma el fallback que copia solo State. La persistencia corresponde al llamador. [statemgr.Migrate, líneas 41–70](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/states/statemgr/migrate.go#L41-L70). El true interno de esta API no es un uso de -force-copy por el operador. |
| ¿Qué hace init después? | Carga/refresca ambos gestores, bloquea ambos, refresca nuevamente, solicita confirmación, llama Migrate y luego PersistState(nil). [meta_backend_migrate.go, líneas 264–468](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/command/meta_backend_migrate.go#L264-L468). |
| ¿S3 crea primero un state vacío? | Hay una rama que lo hace para un workspace no listado, bajo lock. **No ocurrió para default:** Workspaces incluye default incondicionalmente; StateMgr calcula exists=true y omite esa rama aunque la key no exista. [Workspaces, línea 62](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/backend/remote-state/s3/backend_state.go#L62), [StateMgr, líneas 196–255](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/backend/remote-state/s3/backend_state.go#L196-L255). |

El punto de pérdida está en **remote.State**:

1. WriteStateForMigration asigna state, lineage y serial del origen, pero no
   establece readState. Para este destino nuevo, readState sigue nil.
2. PersistState entra por la rama de readState nil y vuelve a llamar refreshState.
3. Al faltar la key, Client.Get devuelve payload nil. refreshState conserva el
   contenido transitorio copiado, pero reinicia lineage a vacío y serial a cero.
4. PersistState detecta lineage vacío, genera un UUID, incrementa serial a 1 y
   serializa/guarda el contenido copiado con esos metadatos nuevos.

Referencias: [WriteStateForMigration, líneas 98–124](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/states/remote/state.go#L98-L124),
[refreshState, líneas 137–164](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/states/remote/state.go#L137-L164),
[PersistState, líneas 169–226](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/states/remote/state.go#L169-L226)
y [S3 Client.get, líneas 127–146](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/backend/remote-state/s3/client.go#L127-L146).

La creación de un snapshot vacío no justifica este resultado: en esta ruta no se
creó ninguno. En una ruta que sí inicializara un destino vacío, Migrate igualmente
asignaría después el lineage del origen; PersistState con readState no nil puede
incrementar el serial al guardar. No debería quedarse con el lineage inicial del
destino. Esta distinción evita confundir una serialización nueva con la ruptura
de identidad observada.

### 11.3. Binding del origen y reconstrucción de la ejecución

El origen fue el archivo privado
`%LOCALAPPDATA%/PersonalBlog/bootstrap/terraform-state/terraform.tfstate`, serial 8.
El archivo homónimo bajo terraform-data contiene **configuración del backend**;
no era el state de recursos que se migraba.

El wrapper preservado `tmp/task030/h0302_migrate.py` exige, antes de lanzar init:
hash del original igual al baseline; backend almacenado de tipo local; config.path
resuelto exactamente al archivo privado anterior; ausencia de otro proceso
Terraform local. Usa ese mismo terraform-data como TF_DATA_DIR, fija
TF_WORKSPACE=default y elimina variables heredadas AWS_/TF_, incluidos posibles
TF_CLI_ARGS. No pasa -state/-state-out ni cambia de TF_DATA_DIR. El local.tfbackend
conservado apunta a la misma ruta absoluta. El TAR previo conserva el state exacto
y versions.tf con backend local; el hash coincide con el archivo original actual.

El código recupera el origen mediante savedBackend a partir de la configuración
guardada antes de escribir el nuevo backend S3: [meta_backend.go, líneas 1891–1906](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/command/meta_backend.go#L1891-L1906),
[savedBackend, líneas 1972–2006](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/command/meta_backend.go#L1972-L2006).
Local.Configure usa config.path; para default, StatePaths usa esa ruta;
Filesystem.refreshState lee el archivo correspondiente.
[Configure](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/backend/local/backend.go#L169-L192),
[StatePaths](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/backend/local/backend.go#L417-L450),
[Filesystem.refreshState](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/states/statemgr/filesystem.go#L254-L306).

No se conservó un TF_LOG=TRACE ni una copia independiente del antiguo archivo de
metadata del backend. La verificación del binding se basa en las guardas ejecutadas
del wrapper, el baseline, el TAR y la ruta del código; no se inventa un trace.
El log confirma origen local no vacío y destino S3 vacío. Además, migrar un origen
vacío habría retornado antes de copiar recursos. Los siete recursos y cuatro
outputs completos del remoto coinciden con ese original, no con un state vacío.
**No hay evidencia de la clasificación C.**

| Momento UTC, 2026-09-28 | Evidencia o transición reconstruida |
| --- | --- |
| 17:16:19 | Baseline: serial 8/lineage original; ambos destinos y locks ausentes. |
| 17:20:20 | Ambos backups cifrados verificados mediante descifrado, hash y contenido del TAR. |
| 17:22:44–17:22:50 | Una sola invocación init -migrate-state; pregunta normal confirmada; exit 0 y cero warnings. |
| Antes de persistir | El workspace default evita crear un objeto vacío; Migrate copia origen serial 8 en memoria; PersistState reinicia su metadata al releer la key ausente. Estas llamadas internas se reconstruyen del código, no de un trace inexistente. |
| 17:22:47 | S3 conserva una versión histórica del lock de la migración. |
| 17:22:48 | Única versión del objeto state, con recursos completos y metadata nuevo. El lock recibe delete marker en el mismo segundo. |
| 17:25:43 | Readback anterior confirma diferencias y parada antes del plan/OIDC. |
| 18:09:04 | Diagnóstico nuevo: STS válido, misma cuenta/rol, us-east-2; misma versión/hash remotos, originales y backups conservados. |

El log privado original tiene SHA-256
`c3405ed1f0f15de62f38aff95fb31b9023e71b5c214b8697fa0fd191e3f6a777`.
ListObjectVersions muestra **una sola versión del state**, 12 531 bytes, y ningún
delete marker para esa key. VersionId
`sobXiO3qAh6OUKjOVTrgaufL.0o1_Cap`, SSE-S3/AES256, sigue siendo la actual.
El lock histórico tiene VersionId `yHS0v7Pw9qTHH0jw7UzBVq13C04VuEYC`; su delete
marker actual es `IFyLvlu8a5U9vNPPGnbe8NFULLtlVlH5`. HeadObject de ese lock devuelve
404. Su historia demuestra actividad del init previo, **no una nueva prueba de
contención**. OIDC state/lock remotos siguen ausentes.

### 11.4. Comparación saneada y explicación exacta de los checks

| Campo | Local original | S3, versión actual conservada |
| --- | --- | --- |
| version | 4 | 4 |
| terraform_version | 1.16.2 | 1.16.2 |
| lineage | 4fd2e0b1-9a72-5648-171c-4d6b2f4e95ad | d33d9c1e-bd73-b176-0907-ae7cf352a50b |
| serial | 8 | 1 |
| Recursos administrados | 7 instancias | Mismas direcciones y contenido JSON completo |
| Data sources | data.aws_caller_identity.human | Mismo contenido JSON completo |
| Outputs | 4 | Iguales en nombre, valor, tipo y marca sensitive |
| check_results | resource unknown, luego var pass | var pass, luego resource unknown; mismos dos elementos completos |
| SHA-256 | d60d661687eeaa39d59bc65a42a020009f1948085734c3a1e16f75b497beb3b6 | 23fe10851e8a105c7039a696288a9e874a051b31ada03092ff62a2fcd3868a11 |

Direcciones administradas comparadas, sin imprimir atributos:

- aws_s3_account_public_access_block.account
- aws_s3_bucket.state
- aws_s3_bucket_ownership_controls.state
- aws_s3_bucket_policy.state
- aws_s3_bucket_public_access_block.state
- aws_s3_bucket_server_side_encryption_configuration.state
- aws_s3_bucket_versioning.state

Outputs: future_s3_backend, future_state_keys, state_bucket_name,
state_bucket_region. No se publican sus valores ni los atributos del data source.

Los dos checks son data.aws_caller_identity.human con agregado/objeto **unknown**
y var.expected_account_id con agregado/objeto **pass**; ambos tienen cero mensajes
de fallo. Se verificó igualdad de los elementos completos al ordenar por
object_kind/config_addr, y que la lista remota es exactamente la inversa de la
local. El unknown preexistía: esta migración no lo creó ni lo convirtió a pass.

decodeCheckResultsV4 reconstruye un mapa y encodeCheckResultsV4 recorre sus Elems
sin ordenarlos. Elems es un mapa Go; su iteración no conserva necesariamente el
orden del JSON leído. normalize ordena recursos e instancias, **no check_results**.
Por eso leer y volver a serializar los mismos checks puede invertir la lista y
cambiar el SHA-256 sin alterar resultados.
[Decodificador/codificador v1.16.2](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/states/statefile/version4.go#L507-L599),
[normalize](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/states/statefile/version4.go#L679-L684),
[mapa de direcciones](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/addrs/map.go#L21-L28).

La exigencia auxiliar de hash byte a byte idéntico era demasiado estricta para
una reserialización con este orden variable. No se cambió esa guarda ni se
continuó: aun comparando checks semánticamente, lineage/serial siguen cambiados
y justifican H-030-4. Hash de backup/restauración sí debe seguir siendo idéntico
cuando se comprueban copias exactas del mismo objeto o archivo.

### 11.5. Aceptación, alternativas y siguiente operación propuesta

**El objeto actual no se acepta todavía como migración validada.** No se ha perdido
contenido observado y podría conservarse como inicio explícito de una nueva cadena
de snapshots, pero eso requiere aceptación humana de la discontinuidad y validación
de convergencia. No se ha demostrado cero drift. Un serial 1 de otro lineage no es
una versión anterior comparable al serial 8: son historias diferentes.

| Alternativa | Condiciones y mutaciones futuras; ninguna ejecutada |
| --- | --- |
| **Recomendada: conservar exactamente el objeto actual y aceptar condicionalmente el nuevo lineage** | Excepción humana explícita a la continuidad, manteniendo el original y backups como evidencia. Validar primero solo terraform-state mediante plan sin cambios. No exige reemplazar ni editar el state S3. Los locks del plan sí escriben/borran una key S3 y necesitan nueva autorización. |
| Conservar el lineage original como requisito obligatorio | Mantener el bloqueo y preparar una corrección probada con un caso sintético, mediante herramienta/procedimiento revisado que preserve metadata. No hay una versión corregida verificada en este diagnóstico. Restaurar la continuidad requeriría escribir una nueva versión del state bajo exclusión mutua; debe presentarse y autorizarse por separado. No se propone un push forzado ni una edición manual como arreglo automático. |
| Posponer la decisión | Mantener ambos artefactos congelados y OIDC local. Sin nuevas mutaciones; H-030-2 y EX-028-C7 permanecen abiertos. |

**Siguiente operación exacta recomendada, solo tras nueva autorización acotada:**
plan de convergencia del primer root usando el backend S3 ya configurado. Antes,
revalidar STS/cuenta/región, exclusividad, VersionId/hash y ausencia de lock.
Mantener el mismo TF_DATA_DIR privado, TF_WORKSPACE=default, AWS_PROFILE=personal-blog,
sin variables heredadas que inyecten argumentos o credenciales.

```text
terraform -chdir=bootstrap/terraform-state plan -input=false -no-color -lock=true -lock-timeout=30s -detailed-exitcode -var-file=<privado-terraform-state>/bootstrap.tfvars.json -out=<privado-terraform-state>/h0304-convergence.tfplan
```

El artefacto de salida debe ser nuevo, sin sobrescribir planes previos. Exigir
exit 0, 0 add/change/destroy, sin drift/import/replace y readback de la misma versión
del state después; detenerse ante cualquier diferencia. **No ejecutado.** La nueva
autorización tendría que permitir exclusivamente esa evaluación y el ciclo nativo
PutObject/DeleteObject de .tflock; no apply, escritura del objeto state ni OIDC.
La decisión de aceptar el lineage sería condicional al resultado, no una declaración
anticipada de éxito. Ni siquiera un plan correcto completaría por sí solo H-030-2.

No se recomienda repetir init: el backend efectivo ya es S3 y repetir el flujo no
restablece por sí mismo el origen serial 8. Para OIDC, el mismo patrón de destino
default ausente obliga a decidir previamente cómo tratar este comportamiento;
no se trasladó ni se relajó su criterio automáticamente.

### 11.6. Custodia y parada mantenida

Evidencia nueva fuera de Git:
`%LOCALAPPDATA%/PersonalBlog/bootstrap/terraform-state/h0304-diagnosis-20260928T180903Z/`.
Contiene copia descargada de la versión existente, inventario S3 saneado,
comparación saneada y manifiesto de preservación. Se comprobaron **16 archivos
preexistentes sin modificación**, incluidos states originales, metadata de ambos
backends, descarga previa, log de migración y archivos de ambos backups cifrados.
Los hashes de los dos ciphertext coinciden también con la verificación anterior.
Las nuevas copias privadas heredan la protección del directorio custodio.

Clasificaciones descartadas: **A** para la pérdida de metadata, pues contradice
la transferencia completa que sí realiza Migrate; **C**, sin evidencia de origen
incorrecto; **D**, sin otra causa necesaria; **E**, pues la ruta que produce el
resultado queda identificada. El orden de checks sí es un efecto de serialización
explicable e independiente. La conclusión no sustituye un reconocimiento del
defecto por el proveedor ni una validación operativa pendiente.

**H-030-4 permanece bloqueado.** Cero mutaciones AWS durante este diagnóstico;
cero ejecuciones Terraform. Se conservan el objeto/VersionId, el original local,
ambos backups y logs. Sin migración OIDC, init, reversión de backend, state push/rm/mv,
force-unlock, pruebas nuevas de locking/recovery, medios, IAM/Billing, commit,
push, PR o merge. La descarga de comparación no se declara prueba de recuperación.

## 12. H-030-4-convergence — plan autorizado y nueva parada H-030-4

### 12.1. Autorización y preflight

El usuario escribió `authorize: Task/030 H-030-4-convergence`: aceptación
**condicional** del lineage nuevo y autorización para un único plan de convergencia,
permitiendo exclusivamente su ciclo normal de creación/eliminación de .tflock.
No autorizó corregir, sobrescribir ni reemplazar el objeto state. Exigió cero
resource drift y parada ante cualquier diferencia, aunque el plan tuviera exit 0.

Preflight `2026-09-28T19:00:15.994112+00:00`: STS válido; perfil personal-blog,
rol/sesión PersonalBlogAdministrator/personal-blog-entry-admin y cuenta esperada
comparada privadamente; bucket us-east-2. Backend S3 efectivo con bucket/key
previstos, encrypt=true, use_lockfile=true y cuenta permitida explícita, sin
DynamoDB/KMS/credenciales almacenadas en su configuración. Se usó el mismo
TF_DATA_DIR operacional y TF_WORKSPACE=default, sin argumentos TF_ heredados.

La versión S3 actual y su hash coincidían con el diagnóstico. Ambos locks y el
destino OIDC estaban ausentes. Los **16 archivos protegidos** coincidían con el
manifiesto previo; ambos ciphertext coincidían además con la verificación de
backups original. No había otro proceso Terraform local. Los cuatro archivos de
recursos/provider/variables/outputs y el lock del provider coincidían con el TAR
previo; se mantuvo el backend S3 ya configurado. Binario 1.16.2 con SHA verificado.
Los artefactos de salida no existían: no se sobrescribió un plan anterior.

### 12.2. Ejecución y gates

Se ejecutó **una sola vez**, sin init ni apply:

```text
terraform -chdir=bootstrap/terraform-state plan -input=false -no-color -lock=true -lock-timeout=30s -detailed-exitcode -var-file=<privado>/bootstrap.tfvars.json -out=<privado>/h0304-convergence.tfplan
```

Inicio `2026-09-28T19:00:41.903646+00:00`; fin
`2026-09-28T19:00:54.782909+00:00`. El JSON se obtuvo mediante show del plan guardado,
sin ejecutar otro plan. Log, binario y JSON permanecen privados fuera de Git.

| Gate | Resultado |
| --- | --- |
| Exit code del plan | **0** |
| Add / change / destroy | **0 / 0 / 0** |
| resource_changes | Todas las acciones no-op |
| Recursos administrados | Exactamente los siete previstos, listados en §11.4 |
| Imports / moves / replaces / deferred changes | **0** |
| Outputs | Los cuatro no-op |
| Checks | Los dos agregados y sus instancias **pass**, cero problemas |
| Warnings | **0** |
| resource_drift | **1: aws_s3_bucket.state, actions=[update] — FALLA** |
| Backend / locking | S3 efectivo, use_lockfile=true, configuración intacta |
| Objeto state | VersionId, SHA-256 e historial de versiones sin cambios |
| .tflock final | Ausente, HeadObject 404 |
| Originales/backups/configuración | Íntegros por hash antes/después |
| OIDC remoto | State y lock ausentes; local sin cambios |

La salida humana anunció ausencia de cambios de infraestructura, pero el JSON
contiene una diferencia detectada durante refresh. **Exit 0 no demuestra por sí
solo cero drift.** No se rebajó el gate ni se reinterpretó la aceptación condicional.

### 12.3. Diferencia saneada encontrada

Se inspeccionó exclusivamente el JSON ya guardado, sin otra consulta Terraform
ni nueva operación AWS después de completar el postflight del plan.

| Campo de aws_s3_bucket.state en resource_drift | Before | After |
| --- | --- | --- |
| policy | Cadena vacía | Policy no vacía; JSON equivalente a la del recurso separado aws_s3_bucket_policy.state |
| versioning[0].enabled | false | true; el recurso separado aws_s3_bucket_versioning.state conserva Enabled |
| tags | null | Objeto vacío `{}` |

Esos son los únicos atributos distintos del recurso en resource_drift. No se
publica el contenido de la policy ni atributos sensibles. **tags_all no cambió**;
tags vacío no se presenta como eliminación de los tags efectivos del bucket.
resource_changes para ese mismo bucket conserva **no-op**, igual que los otros
seis recursos. La evidencia es consistente con diferencias de la representación
refrescada del bucket frente al snapshot anterior, pero no se declara inocua ni
se resuelve automáticamente: el criterio humano fue **cero resource drift**.

Checks del plan: data.aws_caller_identity.human=pass y var.expected_account_id=pass,
con sus instancias pass y cero problemas. Es el resultado de esta evaluación;
no se persistió sobre el state remoto, cuyo contenido continúa exactamente igual.

### 12.4. Custodia, escrituras permitidas y resultado

Bucket: personal-blog-tfstate-us-east-2-9bcb34ac5bcf.
Key: bootstrap/terraform-state/terraform.tfstate.
VersionId antes/después: **sobXiO3qAh6OUKjOVTrgaufL.0o1_Cap**.
SHA-256 antes/después:
`23fe10851e8a105c7039a696288a9e874a051b31ada03092ff62a2fcd3868a11`.
Lineage/serial conservados: d33d9c1e-bd73-b176-0907-ae7cf352a50b / 1.
**No se reescribió el objeto state ni se creó otra versión suya.**

El inventario S3 previo/posterior registró únicamente el ciclo del lock autorizado:

- Versión .tflock `Dm6lLSfPdMRq3tbSiGTj9gKQ2zVT9vNZ`, 19:00:45 UTC.
- Delete marker .tflock `Zkfz4Bes0hTNZ85CQIXH6FDursdVCymx`, 19:00:55 UTC.
- Lock actual ausente. El historial de lock permanece por el versioning del bucket;
  no se borraron versiones históricas ni se usó force-unlock.

Se conservan h0304-convergence-preflight.json, h0304-convergence.tfplan,
h0304-convergence.json, h0304-convergence.log, h0304-convergence-result.json,
h0304-convergence-drift-sanitized.json y descargas privadas antes/después del mismo
objeto. Hash del plan binario:
`52948a5999f0fc7c1d09d128a080fd37e742ba87df04e3791beb432aa88b5fc5`;
JSON: `2734e40af02095cdf9f35349e14cca0bc2b1678a9762beff64fc9a0c50e42750`;
log: `c78fba17cc0dba561edba367b4f7a45c0cab9358cc8ae7b3967ec6cbd680defe`.

**Parada nuevamente como H-030-4.** La aceptación condicional no se materializa
como validación técnica del candidato autoritativo: falló el gate de cero drift.
No se modificó el state para reflejar refresh ni se repitió el plan. H-030-2 sigue
incompleto, OIDC local intacto y EX-028-C7 no extinguida. Sin apply, init,
state push/rm/mv, force, corrección de metadata, migración OIDC, recovery, prueba
adicional de locking, medios, IAM/Billing, commit, push, PR o merge.

## 13. H-030-4 — REFRESH-ONLY PLAN

### 13.1. Alcance autorizado y ejecución

El usuario mantuvo H-030-4 y autorizó únicamente preparar/ejecutar un plan
refresh-only e inspeccionar su JSON, con locking normal. **No autorizó apply**, ni
terraform refresh, escrituras manuales del state, migración OIDC o recuperación.
El objetivo fue evaluar la reconciliación del snapshot con el readback ya identificado.

Preflight `2026-09-28T19:15:02.292392+00:00`: STS correcto, perfil personal-blog,
rol/sesión PersonalBlogAdministrator/personal-blog-entry-admin, cuenta esperada
verificada privadamente y us-east-2. Backend S3, encrypt=true, use_lockfile=true,
misma key, sin DynamoDB/KMS ni cambio de configuración. Misma versión/hash del
state; locks ausentes; 16 archivos protegidos y ambos backups cifrados íntegros.
Un solo operador Terraform local observado. OIDC local conservado; destino ausente.
Se revalidaron también hashes del binario fijado, provider lock y entradas del plan.

Se ejecutó **una sola vez**:

```text
terraform -chdir=bootstrap/terraform-state plan -refresh-only -input=false -no-color -lock=true -lock-timeout=30s -detailed-exitcode -var-file=<privado>/bootstrap.tfvars.json -out=<privado>/h0304-refresh-only.tfplan
```

Inicio `2026-09-28T19:15:54.491464+00:00`; fin
`2026-09-28T19:16:06.676563+00:00`; **exit code 2**, que señala diferencias propuestas
de state en este modo. Inspección posterior mediante `terraform show -json` del
binario guardado, sin repetir el plan. Complete=true, applyable=true, errored=false,
cero warnings. Que sea aplicable no equivale a autorización para aplicarlo.
El [modo refresh-only oficial](https://developer.hashicorp.com/terraform/cli/commands/plan#planning-modes)
prepara reconciliación de state y outputs sin proponer cambios de objetos remotos.

### 13.2. Cambios exactos propuestos y operaciones de infraestructura

| Campo del state para aws_s3_bucket.state | Persistido | Refrescado en el plan |
| --- | --- | --- |
| policy | Cadena vacía | Policy TLS existente, JSON equivalente al de aws_s3_bucket_policy.state |
| versioning[0].enabled | false | true; coincide con Enabled en aws_s3_bucket_versioning.state |
| tags | null | `{}` |

Son los **únicos tres campos de atributos** que cambian. La comparación completa
de los recursos del snapshot persistido contra el snapshot refrescado embebido
en el plan confirma que los otros seis administrados y el data source conservan
su contenido, incluidos los metadatos de instancias. Las siete direcciones son
exactamente las documentadas en §11.4. Ningún recurso IAM forma parte del root.

| Criterio | Resultado |
| --- | --- |
| Add / change / destroy de infraestructura | **0 / 0 / 0** |
| resource_changes | **0**; no create/update/delete de recursos AWS |
| resource_drift | **1**, aws_s3_bucket.state, actions=[update]; idéntico al observado en convergencia |
| Imports / moves / replaces / acciones diferidas o invocaciones | **0** |
| Recursos en snapshot refrescado | **7 administrados + 1 data source**, sin pérdidas ni adiciones |
| Outputs | Los cuatro no-op; nombres/valores/tipos/marcas sin cambios |
| Checks | Ambos agregados/instancias pass; cero fallos o problemas |
| IAM / backend / migraciones | Sin operaciones ni cambios |
| Configuración y provider lock | Sin cambios por hash |

El update de resource_drift describe la diferencia **observada por lectura**;
no es una operación Update programada contra AWS. El plan refrescado coincide
con todos los valores del prior_state del plan de convergencia anterior. No se
detectó un cambio adicional al refresh ya identificado.

En metadata de checks, data.aws_caller_identity.human pasaría de unknown en el
state persistido a pass; var.expected_account_id conserva pass. Sus objetos
tienen los mismos resultados que los agregados. Terraform guarda los checks del
plan por separado del snapshot base embebido y, al aplicar un refresh-only, copia
esos resultados al nuevo state. No se propone dejar check_results vacío:
[Terraform v1.16.2, context_apply.go, líneas 258–270](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/terraform/context_apply.go#L258-L270).
Esto describe una aplicación **futura, no ejecutada**.

El snapshot base del plan conserva lineage d33d9c1e-bd73-b176-0907-ae7cf352a50b
y serial 1. Un apply autorizado persistiría una nueva versión del state y avanzaría
el serial; este PLAN no lo hizo. No se promete un hash futuro ni se presenta el
snapshot interno como un state ya aplicado.

### 13.3. Por qué policy, versioning y tags se reflejan así

La policy refrescada coincide al decodificar ambos JSON con la del recurso
separado aws_s3_bucket_policy.state. Sigue describiendo DenyInsecureTransport,
aws:SecureTransport=false y denegación para bucket/objetos; no hay ampliación
de acceso. La lectura del bucket en el provider también recopila esa policy.
Del mismo modo, enabled=true coincide con el recurso separado de versioning.
El [provider AWS v6.64.0, bucket.go](https://github.com/hashicorp/terraform-provider-aws/blob/v6.64.0/internal/service/s3/bucket.go#L886-L910)
lee la policy, y [recopila versioning](https://github.com/hashicorp/terraform-provider-aws/blob/v6.64.0/internal/service/s3/bucket.go#L991-L1011)
en el recurso general del bucket. Sus representaciones previas estaban sin
reconciliar con ese readback; no se propone modificar los recursos separados.

**tags null → {} no significa quitar tags al bucket.** Este recurso no configura
tags propios; providers.tf aporta los cinco mediante default_tags. En el Read,
el interceptor separa los tags propios de los defaults, los materializa como mapa
y guarda los tags efectivos en tags_all. ResolveDuplicates retira defaults no
declarados explícitamente en el recurso; Map construye un mapa vacío cuando no
quedan tags propios. Por eso se normaliza null a `{}`. **tags_all conserva
exactamente los mismos cinco tags**, sin diferencias de valores.
[Interceptor SDKv2 v6.64.0](https://github.com/hashicorp/terraform-provider-aws/blob/v6.64.0/internal/provider/sdkv2/tags_interceptor.go#L78-L112),
[ResolveDuplicates](https://github.com/hashicorp/terraform-provider-aws/blob/v6.64.0/internal/tags/key_value_tags.go#L847-L875),
[Map](https://github.com/hashicorp/terraform-provider-aws/blob/v6.64.0/internal/tags/key_value_tags.go#L326-L338).

### 13.4. Inspección del formato de plan y evidencia preservada

El primer verificador auxiliar esperaba encontrar recursos en planned_values,
igual que en el plan normal. Señaló dos comprobaciones estructurales fallidas:
ubicación de recursos y comparación de esos valores; **no descubrió un drift
adicional**. Se conservó ese resultado original y se inspeccionó el mismo JSON
y el ZIP del plan de forma read-only, sin cambiar ni regenerar el binario.

En refresh-only, Terraform exige que Changes.Resources esté vacío y el render
de planned_values se deriva de Changes. Por eso su root_module no enumera aquí
los recursos; **prior_state sí contiene los siete más el data source**.
[Guarda v1.16.2 de refresh-only](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/terraform/context_plan.go#L515-L540),
[render de planned_values](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/command/jsonplan/plan.go#L801-L814).

Se comprobó además el tfstate embebido en el binario: recursos completos,
únicamente los tres atributos señalados distintos del remoto y outputs iguales.
El tfstate-prev conserva los recursos previos; no se extrajo ni editó un state
para aplicarlo manualmente. El formato del archivo guarda ambos snapshots:
[planfile/writer.go v1.16.2](https://github.com/hashicorp/terraform/blob/v1.16.2/internal/plans/planfile/writer.go#L24-L35).
El análisis complementario h0304-refresh-only-review.json registra la validación
del alcance, preservando h0304-refresh-only-result.json y sus observaciones iniciales.

Artefactos privados bajo `%LOCALAPPDATA%/PersonalBlog/bootstrap/terraform-state/`:
h0304-refresh-only.tfplan, h0304-refresh-only.json, log, preflight, resultado,
revisión y descargas antes/después. Todos fuera de Git y con custodia privada.

| Artefacto | SHA-256 |
| --- | --- |
| Plan binario | `91d2dab91f8e5d084edb5aa9f1eee13be4c21dca016870fc44019cf530cc5432` |
| JSON del plan | `c0c7c50520ae31c661de2b1bdeaf98ec59b9889a86751306ca73fb43a137a0d4` |
| Log del plan | `3d6481b2abb00a0cd284b28f1eb9eefc46c3cf7db4129366ca4c7b3a19e6b838` |

### 13.5. State autoritativo, lock y recomendación

| Evidencia del state remoto | Antes del PLAN | Después del PLAN |
| --- | --- | --- |
| VersionId | sobXiO3qAh6OUKjOVTrgaufL.0o1_Cap | El mismo |
| SHA-256 | 23fe10851e8a105c7039a696288a9e874a051b31ada03092ff62a2fcd3868a11 | El mismo |
| Lineage / serial | d33d9c1e-bd73-b176-0907-ae7cf352a50b / 1 | Los mismos |
| Historial de versiones de la key state | Una versión | Sin cambios |
| .tflock actual | Ausente | Ausente, 404 |
| Originales y ambos backups cifrados | Íntegros | Íntegros |

**No hubo mutación de infraestructura AWS ni del objeto state autoritativo.**
Sí ocurrió el ciclo normal de escritura/eliminación de .tflock autorizado por el
plan con locking; no se afirma cero escrituras S3. Nueva versión de lock
KJjZ6FzXF56uzZa10QeWUD7L5ZQkbfm5, 19:15:58 UTC; delete marker
2exwu4h67Wyv8UulPS02konGyRT7jnhc, 19:16:07 UTC. Sin lock residual ni otras nuevas
versiones en el inventario de keys de bootstrap. OIDC local y remoto sin cambios.

**Recomendación: el plan guardado es técnicamente adecuado para aplicar únicamente
esta reconciliación de state, bajo una nueva autorización humana explícita.**
Antes de una aplicación autorizada deben coincidir nuevamente identidad, backend,
versión/hash del state y hash exacto de este plan, con exclusividad y lock normal.
La futura mutación sería una nueva versión S3 del state más el ciclo de lock,
sin cambios de infraestructura. No sustituirlo por terraform refresh ni regenerar
otro plan para aplicarlo bajo la autorización de este binario.

**Parada H-030-4 — REFRESH-ONLY PLAN.** No aplicado. No se considera extinguida
EX-028-C7 ni validado H-030-2. Sin state push/rm/mv, force, edición manual,
migración OIDC, recovery, medios, commit, push, PR o merge.

## 14. H-030-4-refresh-apply — reconciliación aplicada y convergencia limpia

### 14.1. Autorización exacta y preflight

El usuario escribió `authorize: Task/030 H-030-4-refresh-apply`, autorizando solo
aplicar el binario refresh-only con SHA-256
`91d2dab91f8e5d084edb5aa9f1eee13be4c21dca016870fc44019cf530cc5432`.
También autorizó, únicamente después de verificar el apply, un nuevo plan normal
de convergencia. **No autorizó cambios de infraestructura, OIDC, recovery ni medios.**

Preflight `2026-09-28T19:32:02.370283+00:00`: STS válido, perfil personal-blog,
rol/sesión PersonalBlogAdministrator/personal-blog-entry-admin, cuenta esperada
comparada privadamente y región us-east-2. Backend efectivo S3, use_lockfile=true,
encrypt=true, mismo bucket/key; sin DynamoDB/KMS ni cambio de configuración.
Un solo operador Terraform local observado; locks local/remoto ausentes.
Los 16 artefactos protegidos y ambos ciphertext coinciden con sus hashes previos.
OIDC conserva su state/backend local; destino remoto y lock ausentes.

Se verificaron nuevamente el VersionId/hash actuales autorizados, el hash del
plan guardado y el del JSON revisado, el binario Terraform 1.16.2, provider lock y
configuración. Los cinco archivos Terraform y el provider lock coinciden también
con los embebidos en el plan. **No se regeneró el plan antes de aplicar.**
Inmediatamente antes del apply se repitieron identidad/guardas y se descargó otra
vez la versión exacta: mismo VersionId/SHA-256 e historial S3 que en el preflight.

### 14.2. Apply exclusivo del binario guardado

Única invocación de apply en esta autorización:

```text
terraform -chdir=bootstrap/terraform-state apply -input=false -no-color -lock=true -lock-timeout=30s <privado>/h0304-refresh-only.tfplan
```

El modo refresh-only proviene del binario ya revisado. No se usaron terraform
refresh, un nuevo plan implícito, force, import ni comandos state push/rm/mv.
Se conservó el TF_DATA_DIR privado, workspace default y perfil humano esperado.

Inicio `2026-09-28T19:32:31.869835+00:00`; fin
`2026-09-28T19:32:39.225701+00:00`; **exit 0**, cero warnings. La salida del apply
confirmó **0 recursos añadidos, 0 cambiados, 0 destruidos**. Se escribió una sola
nueva versión del state, con el contenido del refresh autorizado.

| Evidencia | Antes | Después del apply |
| --- | --- | --- |
| VersionId S3 | sobXiO3qAh6OUKjOVTrgaufL.0o1_Cap | **pjvyHqNzxTObDUSOcwVbuXSwAD3I4RM2** |
| SHA-256 state | 23fe10851e8a105c7039a696288a9e874a051b31ada03092ff62a2fcd3868a11 | **65c96bb06ba2688d054de63fdc44f4950c1b2c264de18ccfe49094b5995a4eb0** |
| Lineage | d33d9c1e-bd73-b176-0907-ae7cf352a50b | **El mismo** |
| Serial | 1 | **2**, un avance para una nueva versión |
| Recursos | 7 administrados + data source | Mismas direcciones; contenido exactamente igual al snapshot refrescado del plan revisado |
| Outputs | Cuatro | Íntegros |
| tags_all del bucket | Cinco tags | Mismos cinco, valores iguales |
| Backend / encryption | S3, encrypt=true, lockfile=true, AES256 | Sin cambios |
| Originales/backups | Íntegros | Íntegros |
| .tflock final | Ausente | Ausente |

Las diferencias de contenido corresponden solo a los tres atributos autorizados
del bucket: policy vacía→TLS existente, versioning.enabled false→true, tags null→{}.
Policy y versioning coinciden con sus recursos separados. El check de identidad
pasó de unknown a pass; el check de variable conserva pass. Ambos agregados y
objetos tienen cero mensajes de fallo. Los demás metadatos de nivel superior
permanecen iguales, salvo serial y check_results según lo autorizado.

El VersionId anterior se conserva. Las únicas nuevas entradas de historial S3
fueron la versión del state y el ciclo de lock: versión .tflock
qxeaWKsNMf5QXZOs7e7A3tRqx8daiQ1n (19:32:35 UTC), delete marker
kZKBBRcJbJzbFsGsaJ235MpgNzKdZuGz (19:32:40 UTC). Sin lock residual ni escritura OIDC.
Se completaron todas estas verificaciones **antes** de iniciar la convergencia.

### 14.3. Nuevo plan normal de convergencia

Tras validar el apply, se revalidaron identidad, exclusividad, backend,
VersionId/hash nuevos, ausencia de lock, custodia y ausencia de cambios en el
historial S3. Se generó un archivo nuevo, sin sobrescribir ni reutilizar planes:

```text
terraform -chdir=bootstrap/terraform-state plan -input=false -no-color -lock=true -lock-timeout=30s -detailed-exitcode -var-file=<privado>/bootstrap.tfvars.json -out=<privado>/h0304-post-refresh-convergence.tfplan
```

Inicio `2026-09-28T19:33:05.782592+00:00`; fin
`2026-09-28T19:33:16.213534+00:00`. Inspección mediante show -json del plan guardado.

| Gate requerido | Resultado |
| --- | --- |
| Exit code | **0** |
| Add / change / destroy | **0 / 0 / 0** |
| resource_drift | **0** |
| Recursos administrados | Exactamente siete, todos no-op; direcciones de §11.4 |
| Outputs | Cuatro no-op |
| Checks | Ambos agregados e instancias pass, cero problemas |
| Imports / moves / replaces / deferred / action invocations | **0** |
| Warnings | **0** |
| Estado del plan | Complete=true, errored=false, applyable=false por ausencia de cambios |
| State remoto reescrito por el plan | **No**: mismo VersionId, SHA-256, serial y contenido |
| Historial de versiones de la key state | Sin cambios durante el plan |
| .tflock final | Ausente, 404 |
| Backend / originales / backups / entradas | Intactos por hash |
| OIDC | Local intacto; state/lock remotos ausentes |

Antes y después del plan normal: VersionId pjvyHqNzxTObDUSOcwVbuXSwAD3I4RM2,
SHA-256 65c96bb06ba2688d054de63fdc44f4950c1b2c264de18ccfe49094b5995a4eb0,
lineage d33d9c1e-bd73-b176-0907-ae7cf352a50b y serial 2. Ese plan no se aplicó.
Su único ciclo nuevo de lock fue la versión uusblDfzGN7aM0bk1vYtuOhZfyodXaHp
(19:33:08 UTC) y el delete marker pKHdeAHnSENccgFq8M.bvlRPaCMUk0DT
(19:33:17 UTC). No se borraron versiones históricas del lock.

### 14.4. Evidencia y parada final de este alcance

| Artefacto privado | SHA-256 |
| --- | --- |
| Binario refresh-only aplicado | 91d2dab91f8e5d084edb5aa9f1eee13be4c21dca016870fc44019cf530cc5432 |
| Log apply | 58f7f8bd22553f55226e5dd4889a11b46db63d9fe591a6d02ac2f35b78fa3d8c |
| Nuevo plan normal | 2255566451f44e3de3a67574d4e8bcd08fc39313a095c3dda795d50677cd600e |
| JSON nuevo plan normal | 25382406242068309d6046a069063201f0e1ea38b0da86afd6ff90d6a328400c |
| Log nuevo plan normal | 60c2305420542f2ce5c6a0a473f734430c1bcc3038f4e7ffbd4fecc16a7d3e93 |

Custodia fuera de Git bajo el directorio privado existente: familias
h0304-refresh-apply-* y h0304-post-refresh-convergence*, con preflight, ejecución,
logs, descargas de versiones concretas y resultados saneados. Planes, originales
y ambos backups cifrados anteriores se conservan sin alteración. El primer state
local serial 8 no se reutilizó como escritor ni se editó manualmente.

**Resultado: discrepancia del primer bootstrap resuelta dentro de esta autorización.**
La nueva cadena remota queda técnicamente validada: refresh acotado aplicado,
lineage preservado y convergencia real limpia. No hubo creación/modificación/
destrucción de infraestructura AWS. Las mutaciones autorizadas fueron únicamente
la nueva versión S3 del state y los ciclos normales de lock de apply/plan.
PersonalBlogGitHubOidcValidation no fue tocado.

**Parada solicitada, antes de OIDC.** H-030-2 completo sigue pendiente de la segunda
migración, prueba controlada de contención y recuperación; estos ciclos de lock
no sustituyen dicha prueba. EX-028-C7 no extinguida. Sin recovery, medios, D-08,
Task/031, commit, push, PR ni merge. No se autoriza ni ejecuta la siguiente fase
por el éxito de este checkpoint; la tarea continúa En progreso, sin aprobación.

## 15. H-030-2 — MIGRACIÓN DEL STATE OIDC

### 15.1. Autorización y preflight

Continuación de `authorize: Task/030 H-030-2`, ya concedida y vigente para la
migración secuencial. **No se pidió una autorización nueva** porque el estado real
coincide con esa continuidad: primer bootstrap validado en §14 y OIDC todavía local.
La única operación de esta fase fue migrar `bootstrap/github-oidc` a la key
`bootstrap/github-oidc/terraform.tfstate`.

Preflight del 2026-09-28, todo verificado **antes** de mutar:

| Comprobación | Resultado |
| --- | --- |
| STS | perfil personal-blog, `assumed-role/PersonalBlogAdministrator/personal-blog-entry-admin`, cuenta esperada comparada privadamente, us-east-2 |
| Operador único | **0 procesos Terraform**; 0 archivos `.lock.info` en el directorio privado y en el checkout |
| State local OIDC | SHA-256 `8fc01b3e797298bc7eec4eb7b36dcc72b805ae61886a287e7e9186c5f8e872aa`, **idéntico** al de §9; serial **6**; lineage de Task/028 |
| Direcciones administradas | exactamente `aws_iam_openid_connect_provider.github[0]` y `aws_iam_role.validation`, más un data source |
| Backup cifrado | ciphertext `3e56b271…33044715`, **igual** al de §9; tar en claro byte a byte igual al descifrado verificado; state embebido con el SHA-256 del original |
| Configuración | los cinco `.tf` y el provider lock del checkout coinciden **byte a byte** con las copias embebidas en el backup |
| Binario | Terraform 1.16.2, SHA-256 `d51f5333…8290fe96`, idéntico en las dos rutas de herramientas |
| Destino remoto | `bootstrap/github-oidc/terraform.tfstate` y su `.tflock` devolvieron **404**; el bucket solo contenía la key del primer bootstrap |
| Cadena del primer bootstrap | VersionId `pjvyHqNzxTObDUSOcwVbuXSwAD3I4RM2`, 12 864 bytes: intacta |

**Drift IAM previo descartado por dos vías.** Comparación atributo por atributo del
state contra AWS real: **0 diferencias** en nombre, path, ARN, `unique_id`,
descripción, `max_session_duration`, boundary, políticas, tags, documento de trust,
y en URL, `client_id_list`, ARN, número de thumbprints y tags del proveedor. Y el
plan de convergencia de Task/028 (`converge-20260925T190328Z`) ya registraba dos
recursos no-op, `resource_drift = 0`, outputs no-op y checks pass.

`PersonalBlogGitHubOidcValidation` en AWS real, antes de migrar: **cero políticas
gestionadas, cero inline, cero instance profiles, sin permissions boundary**, trust
con una sola condición `StringEquals`, audiencia `sts.amazonaws.com` y subject de
`refs/heads/main` —la fase `main`, sin `DateLessThan`—. Proveedor con URL
`token.actions.githubusercontent.com`, lista de clientes exactamente
`["sts.amazonaws.com"]` y un thumbprint. **No se amplió ni se usó ese rol como
identidad de Terraform: sigue VALIDATION-ONLY.**

### 15.2. Cambio de backend y sonda previa

Se creó la configuración privada `remote.tfbackend` derivada de la del primer
bootstrap, cambiando **solo la key**: mismo bucket, us-east-2, perfil
personal-blog, cuenta permitida explícita, `encrypt=true`, `use_lockfile=true`,
**sin DynamoDB ni KMS**. En `bootstrap/github-oidc/versions.tf` se sustituyó
`backend "local" {}` por `backend "s3" {}`; es el **único** archivo versionado que
esta fase modifica, con finales de línea LF conservados. Se preservó el
`TF_DATA_DIR` privado para que Terraform siguiera conociendo el origen local.

Antes de consentir la copia se ejecutó una **sonda con `-input=false`**, que no
puede escribir el state. Terraform informó del cambio de backend de `local` a `s3`
y rechazó la aprobación por estar deshabilitada la entrada interactiva.

La sonda confirmó la migración exacta esperada y se detuvo. Readback posterior:
destino **404**, metadata de backend sin cambios, state local con su hash intacto.
**Corrección de un dato propio:** al verificar la sonda se afirmó que no había
escrito nada en ningún sitio. El historial de versiones mostró después que sí
abrió y cerró un **lock nativo** en la key destino (`vKn0bSK8SAW2dvlPWRr0Seu…`,
20:06:35 UTC). No escribió el state —eso se comprobó— pero el ciclo de lock existió
y queda registrado aquí.

### 15.3. Migración ejecutada

```text
terraform -chdir=bootstrap/github-oidc init -migrate-state -input=true -no-color
  -lock-timeout=30s -lockfile=readonly -backend-config=<privado>/remote.tfbackend
```

Inicio `2026-09-28T20:07:22.437789+00:00`; fin `2026-09-28T20:07:28.851310+00:00`;
**exit 0**, cero warnings, provider reutilizado del lock sin cambios. El prompt fue
**exactamente** el esperado —la pregunta normal de copia del state—, declarando
state preexistente en el backend `local` y **ninguno** en el `s3` recién
configurado. Solo entonces se respondió `yes`. **Sin `-force-copy`, sin
`-reconfigure`**, sin `state push`, `state rm`, `state mv`, `force-unlock`, `import`
ni `destroy`.

### 15.4. Readback remoto: el patrón conocido de Terraform 1.16.2

VersionId `Dl7AxGe7qj28P703ZFJwh_qsRzY2ViHI`, 5 840 bytes, SSE-S3/AES256, **una
sola versión** de la key. Se descargó **esa versión concreta** a un directorio
privado aislado, sin conectarla como backend.

| Campo | State local original | Versión S3 descargada |
| --- | --- | --- |
| version / terraform_version | 4 / 1.16.2 | **Iguales** |
| Claves de nivel superior | siete | **Iguales** |
| Recursos | 2 administrados + 1 data source | **Idénticos**, mismo hash del bloque completo |
| Direcciones | `aws_iam_openid_connect_provider.github[0]`, `aws_iam_role.validation` | **Idénticas** |
| Outputs | `managed-A`, `main` | **Idénticos** |
| check_results | ocho entradas | **Idénticos** |
| Lineage | `5e5042e1-…-b2fa14584132` | **Regenerado** |
| Serial | **6** | **1** |

Las **únicas** diferencias son `lineage` y `serial`: el comportamiento ya
diagnosticado en §§11–13 contra el código de Terraform v1.16.2 al copiar por primera
vez hacia una key S3 inexistente. Aquí el patrón es **más estrecho** que en el
primer bootstrap, donde además cambiaron los `check_results`. **No se perdió ningún
recurso ni output.** Conforme a lo acordado, **no se intentó corregir el lineage**:
sin `state push`, sin force y sin edición manual.

AWS real **no cambió**: las respuestas de `GetRole` y `GetOpenIDConnectProvider`
son idénticas antes y después, comparadas como JSON normalizado —descartando solo
`RoleLastUsed`, que es telemetría de uso, no configuración—. Siguen en cero las
políticas gestionadas, las inline y los instance profiles; sigue ausente el
permissions boundary; trust, audiencia, subject y proveedor intactos.

### 15.5. Plan normal de convergencia

Un **primer intento falló** por invocación, no por Terraform ni por AWS: el bloque
`provider "aws"` no declara `profile`, y el perfil `personal-blog` se resuelve por
`login_session` sin perfil `default`, de modo que el provider no encontró
credenciales. Exit 1, planificación fallida, **state no escrito**, VersionId sin
cambios y lock liberado con normalidad; el artefacto de plan errado se conservó
aparte como `h0302-oidc-convergence-errored-nocreds.tfplan`. El backend sí llevaba
su `profile` explícito, y por eso el `init` anterior había funcionado. Se repitió
aportando `AWS_PROFILE=personal-blog` como fuente de credenciales del provider; el
destino sigue siendo fail-closed por `allowed_account_ids` y por la postcondición de
identidad. **El runbook del bootstrap no registra esta variable: queda como hueco
documental a corregir.**

```text
terraform -chdir=bootstrap/github-oidc plan -input=false -no-color -lock=true
  -lock-timeout=30s -detailed-exitcode -var-file=<privado>/bootstrap.auto.tfvars.json
  -out=<privado>/h0302-oidc-convergence.tfplan
```

Inicio `2026-09-28T20:10:41.201036+00:00`; fin `2026-09-28T20:10:48.525124+00:00`.

| Gate requerido | Resultado |
| --- | --- |
| Exit code | **0** — sin cambios |
| Add / change / destroy | **0 / 0 / 0** |
| `resource_drift` | **0** |
| Recursos administrados | **dos**, ambos no-op, con las direcciones esperadas |
| Outputs | dos no-op |
| Checks | **ocho pass, cero problemas** |
| Imports / moves / replaces / deferred / action invocations | **0** |
| Warnings | **0** |
| Estado del plan | `complete=true`, `errored=false`, `applyable=false` |
| State reescrito por el plan | **No**: mismo VersionId, longitud y contenido |
| Versiones de la key state | **1** |
| `.tflock` final | **Ausente, 404** |

**Por tanto no hace falta un refresh-only para OIDC.** El primer bootstrap lo
necesitó porque su plan reveló un `resource_drift`; aquí el drift es cero y la
convergencia ya está limpia contra el backend S3. No se propone ni se ejecuta apply.

### 15.6. Locking, custodia y gates

Cuatro ciclos de lock nativo, **todos cerrados**: sonda (20:06:35), migración
(20:07:24), plan fallido (20:09:30) y plan de convergencia (20:10:4x). Cuatro
versiones `.tflock` y cuatro delete markers; **ningún lock residual** y ninguna
versión histórica borrada. **Estos son ciclos normales: no sustituyen la prueba de
contención**, que sigue pendiente.

Custodia intacta: state local OIDC y su `.backup` byte a byte iguales a sus
snapshots previos —el `.backup` conserva el serial 4 histórico de Task/028—; state
local del primer bootstrap y **ambos ciphertext** con sus hashes de §9; provider
lock del checkout sin cambios. Evidencia nueva bajo el directorio privado del
bootstrap OIDC, **fuera de todo checkout Git**: log de migración, plan binario,
JSON, log, descarga de la versión concreta, readbacks IAM y
`h0302-oidc-migration-evidence.json`. Se añadió `H0302-STATUS.txt`, que **deja sin
efecto** el marcador `H0302-BLOCKED.txt` del primer bootstrap: describía un bloqueo
ya resuelto en §14 y podía leerse como parada activa.

| Artefacto privado | SHA-256 |
| --- | --- |
| Log de `init -migrate-state` | `c3405ed1f0f15de62f38aff95fb31b9023e71b5c214b8697fa0fd191e3f6a777` |
| Plan de convergencia | `433bef24bf8615dc0e18041ac8ccea958370d0a35545088cdb9f9b0271c1cd96` |
| JSON del plan | `ed88cb42f8e4207f01a0e4beb7f3f959824aefad3851eff96ef799fc1fd5a2ae` |
| Log del plan | `5289ca23bb3995965d14bff39df61993713ce5e3080aca910419c748c9a2ec56` |
| Versión S3 descargada | `cb16264b308a2feadf133dc2ad1504bc5c2452a26b4d4417fc7901c6621fb524` |

Gates offline reejecutados con un `TF_DATA_DIR` de validación **aislado**, para no
tocar la metadata operativa: `fmt -check -recursive`, `init -backend=false`,
`validate`, `terraform test` **9/9**, `tests/oidc` **60 ejecutadas, 1 omitida**,
`tests/terraform_state` **12/12**, `git diff --check` limpio y provider lock sin
cambios. Ningún test fija el backend local, de modo que el cambio no rompe el CI.

### 15.7. Estado y parada

Ambos roots de bootstrap operan ya contra S3 con lock nativo y sin DynamoDB:
`bootstrap/terraform-state` en serial 2 y `bootstrap/github-oidc` en serial 1, los
dos con convergencia 0/0/0 y `resource_drift = 0`. Las únicas mutaciones de esta
fase fueron **la primera versión del state OIDC en S3** y los ciclos normales de
lock. **Cero cambios de infraestructura AWS.**

**Pendiente dentro de H-030-2**, cada cosa con su autorización: prueba controlada
de **contención de locking**, prueba de **recovery** desde una versión concreta,
archivado de los locales como backups inactivos protegidos y **extinción de
EX-028-C7**, que **no se extingue aquí**. Fuera de alcance y no iniciados: D-08,
bucket de medios, `S3Storage` real, H-030-3 y Task/031. Sin commit, push, PR ni
merge; Task/030 sigue **En progreso** y **sin aprobación**.

## 16. H-030-2 — CONTENCIÓN DE LOCKING Y RECOVERY

El usuario aceptó la migración OIDC de §15 como técnicamente validada y ordenó
continuar con el cierre de H-030-2. Esta fase cubre **solo** el preflight, la prueba
de contención y la prueba de recuperación. **La retirada de los states locales como
fuentes operativas y la extinción de EX-028-C7 no se ejecutaron**: las instrucciones
de esos dos puntos llegaron truncadas y se detuvo antes de tocarlos. Ninguna
migración se reabrió ni se repitió.

### 16.1. Preflight

| Comprobación | Resultado |
| --- | --- |
| STS | perfil personal-blog, `assumed-role/PersonalBlogAdministrator/personal-blog-entry-admin`, cuenta esperada, us-east-2 |
| Operador único | **0 procesos Terraform**, 0 archivos `.lock.info` en el directorio privado y en el checkout |
| Backends efectivos | **los dos en S3**, `use_lockfile=true`, `encrypt=true`, **sin DynamoDB ni KMS**; `versions.tf` de ambos roots declara `backend "s3" {}` |
| `.tflock` | **ambas ausentes (404)** antes de empezar |
| `bootstrap/terraform-state` | VersionId `pjvyHqNzxTObDUSOcwVbuXSwAD3I4RM2`, 12 864 bytes, SHA-256 `65c96bb0…5a4eb0`, lineage `d33d9c1e-…-ae7cf352a50b`, **serial 2**, 7 administrados + 1 data source, 4 outputs |
| `bootstrap/github-oidc` | VersionId `Dl7AxGe7qj28P703ZFJwh_qsRzY2ViHI`, 5 840 bytes, SHA-256 `cb16264b…1fb524`, lineage `973e160f-…-c4b0449a4633`, **serial 1**, 2 administrados + 1 data source, 2 outputs |
| Originales locales y ciphertexts | los cinco hashes coinciden con §§9 y 15 |
| Plan normal `terraform-state` | exit **0**, 0/0/0, `resource_drift = 0`, siete no-op, dos checks pass, 0 warnings |
| Plan normal `github-oidc` | exit **0**, 0/0/0, `resource_drift = 0`, dos no-op, ocho checks pass, 0 warnings |
| Rol de validación | **cero políticas gestionadas, cero inline, cero instance profiles**, sin permissions boundary, trust con una sola condición `StringEquals`, aud `sts.amazonaws.com`, subject de `refs/heads/main`: sigue **VALIDATION-ONLY** |

Sin drift ni inconsistencias: no se abrió H-030-4.

### 16.2. Prueba de contención del lock nativo

Root elegido: `bootstrap/terraform-state`, ya convergente. Operación **no
destructiva y sin apply** en los dos lados: `plan`. Para que la contención fuese
entre **dos operadores reales sobre la misma key**, se inicializó un **segundo
`TF_DATA_DIR`** contra esa misma configuración privada de backend. Ese `init`
terminó en exit 0, **sin pregunta de migración** —no había origen que copiar—, sin
escribir el state y sin crear lock.

Secuencia, con T0 `2026-09-28T20:48:49.571622+00:00`:

1. **OP1**: `plan -lock=true -lock-timeout=30s -detailed-exitcode` con el
   `TF_DATA_DIR` operacional.
2. **Lock confirmado por lectura**, no supuesto: `head-object` encontró la key
   `.tflock` en el segundo intento, `2026-09-28T20:48:52.226306+00:00`. Se descargó
   su cuerpo mientras estaba retenido: versión `ZgFk7UAbL.rJs_u6ZAyZJbngbOkTv3rh`,
   `Operation = OperationTypePlan`, `Version = 1.16.2`, `Path` igual a
   bucket más key, ID con prefijo `954b2040`.
3. **OP2**, concurrente, contra la **misma key**, con el segundo `TF_DATA_DIR` y
   `-lock-timeout=5s`.

Resultados:

| Gate requerido | Resultado |
| --- | --- |
| OP1 | **exit 0**, `No changes`, 0/0/0, `resource_drift = 0`, siete no-op, checks pass, `applyable=false` |
| OP2 | **exit 1**, rechazada con `Error: Error acquiring the state lock` |
| Mecanismo del rechazo | `S3 PutObject` **412 PreconditionFailed**: la escritura condicional de `use_lockfile`. El error citó el **Lock Info de OP1**, con su ID, `Path`, `Operation` y `Created` |
| ¿Falló por auth, backend, provider o variables? | **No.** Cero coincidencias de esas cuatro familias de error en su log; la única línea `Error:` es la del lock |
| Cambios de infraestructura | **ninguno**: OP1 no propuso nada y OP2 no llegó a planificar |
| State modificado por la prueba | **No**: VersionId `pjvyHqNzxTObDUSOcwVbuXSwAD3I4RM2` y `LastModified` **19:32:39 UTC** intactos; dos versiones, **cero delete markers** |
| Versiones `.tflock` creadas por las dos operaciones | **una sola.** El `PutObject` de OP2 fue rechazado, así que no generó versión: es prueba adicional de que la condición se respetó en lugar de sobrescribir |
| `.tflock` final | **Ausente (404)**, liberado por terminación normal de OP1 |
| `force-unlock` | **jamás invocado**; ninguna aparición en los logs |
| Lock fabricado | **ninguno**: el único lock lo creó Terraform |
| Objetos borrados | **cero** |
| Artefacto de plan de OP2 | **no se creó** |

**Veredicto: PASS.** El solapamiento fue real, observado por lectura y demostrado
por el propio mensaje de Terraform, no inferido de tiempos.

### 16.3. Prueba de recovery por versión

Para cada key se descargó una VersionId concreta **con lectura versionada** a un
directorio privado **aislado**, que **no se inicializó como backend**: ambos
directorios quedaron sin `.terraform`, sin `terraform-data` y sin `init`. No se
reemplazó ningún state autoritativo.

| Caso | VersionId | Resultado |
| --- | --- | --- |
| `terraform-state`, autoritativa actual | `pjvyHqNzxTObDUSOcwVbuXSwAD3I4RM2` | 12 864 bytes, AES256, SHA-256 `65c96bb0…5a4eb0`, version 4, 1.16.2, lineage `d33d9c1e-…`, **serial 2**, 7 administrados + 1 data source, 4 outputs |
| `terraform-state`, **versión anterior** | `sobXiO3qAh6OUKjOVTrgaufL.0o1_Cap` | 12 531 bytes, AES256, SHA-256 `23fe1085…3868a11`, version 4, 1.16.2, mismo lineage, **serial 1**, mismos siete recursos y outputs |
| `github-oidc`, autoritativa actual | `Dl7AxGe7qj28P703ZFJwh_qsRzY2ViHI` | 5 840 bytes, AES256, SHA-256 `cb16264b…1fb524`, version 4, 1.16.2, lineage `973e160f-…`, **serial 1**, 2 administrados + 1 data source, 2 outputs |

Comparación contra la metadata autoritativa esperada —hash, `version`,
`terraform_version`, `lineage`, `serial`, direcciones de recursos y outputs—:
**0 desviaciones en los tres casos**. La recuperación de la versión anterior del
primer bootstrap es la que demuestra que esto es **recuperación punto en el tiempo**
de verdad y no una simple lectura de la última versión: devolvió el snapshot de
serial 1, previo al refresh-only autorizado, con su hash exacto.

Después de las tres lecturas:

- conteo de versiones **idéntico**: dos en `terraform-state`, una en `github-oidc`;
- **cero delete markers** en ambas keys;
- mismos VersionId y `LastModified` que antes: **ninguna versión nueva** creada por
  leer;
- ambas `.tflock` ausentes;
- **sin** `state push`, `state mv`, `state rm`, `import`, restauración encima del
  state activo ni borrado de objetos o versiones.

**Veredicto: PASS.** La recuperación es lectura y verificación, y así se ejecutó.

### 16.4. Custodia y parada

Tras las dos pruebas, los cinco artefactos de custodia conservan sus hashes: los
states locales de ambos roots, el `.backup` histórico de OIDC y los **dos**
ciphertext GPG. El bucket sigue conteniendo exactamente las dos keys de state.
Ningún proceso Terraform quedó vivo y no hay `.lock.info` residual.

Evidencia saneada en `h0302-close-abc-evidence.json`, más los logs y planes de la
prueba y las descargas aisladas, todo bajo los directorios privados **fuera de
cualquier checkout Git**. El cuerpo del lock capturado contiene el identificador de
máquina y usuario del operador: **no se transcribe aquí**.

**Parada.** Quedan los dos últimos puntos del cierre de H-030-2 —retirar los states
locales como fuentes operativas y **extinguir EX-028-C7**—, cuyas instrucciones
llegaron truncadas: no se ejecutan por iniciativa propia. EX-028-C7 sigue **viva**
y los locales siguen presentes tal cual. Sin D-08, bucket de medios, `S3Storage`
real, H-030-3, Task/031, commit, push, PR ni merge. Task/030 sigue **En progreso**
y **sin aprobación**.

## 17. H-030-2 — CIERRE: RETIRADA DE LOCALES Y EXTINCIÓN DE EX-028-C7

El usuario aceptó como PASS la migración, la convergencia, la contención del locking
y el recovery, y autorizó exactamente los dos puntos que faltaban por truncamiento:
retirar los states locales como fuentes operativas y extinguir EX-028-C7 si los
gates finales seguían verdes. No se reabrió ninguna migración, no se repitió
`init -migrate-state` y **no se cambió ningún recurso AWS**.

### 17.1. Preflight de la retirada

| Comprobación | Resultado |
| --- | --- |
| STS | perfil personal-blog, `assumed-role/PersonalBlogAdministrator/personal-blog-entry-admin`, us-east-2 |
| Procesos Terraform | **0** |
| `.tflock` | **ambas ausentes (404)** |
| Plan `bootstrap/terraform-state` | exit **0**, 0/0/0, `resource_drift = 0`, siete no-op, dos checks pass |
| Plan `bootstrap/github-oidc` | exit **0**, 0/0/0, `resource_drift = 0`, dos no-op, ocho checks pass |
| Remoto `terraform-state` | `pjvyHqNzxTObDUSOcwVbuXSwAD3I4RM2`, sha `65c96bb0…5a4eb0`, lineage `d33d9c1e-…`, **serial 2** |
| Remoto `github-oidc` | `Dl7AxGe7qj28P703ZFJwh_qsRzY2ViHI`, sha `cb16264b…1fb524`, lineage `973e160f-…`, **serial 1** |
| Ciphertext GPG | `dcb4b567…c9c078` y `3e56b271…33044715`, ambos con su hash de §9 |
| States locales originales | `d60d6616…beb3b6`, `8fc01b3e…e872aa` y el `.backup` `25690c0e…64f509a` |

Nada había cambiado: no se abrió H-030-4. `bootstrap/terraform-state` nunca tuvo
`terraform.tfstate.backup`; se hace constar en lugar de inventarlo.

### 17.2. Archivo de los locales como backups inactivos

Destino, fuera de todo checkout Git:
`%LOCALAPPDATA%\PersonalBlog\bootstrap-backups\INACTIVE-HISTORICAL-STATES\`, con un
subdirectorio por root. Cada nivel lleva el marcador literal
**INACTIVE / HISTORICAL BACKUP - NOT AN OPERATIONAL BACKEND**, que enumera lo
prohibido: apuntar un backend a esos archivos, `state push`/`mv`/`rm`, `import`,
restaurar encima del state activo y borrar versiones S3.

Los movimientos fueron `mv` —renombrado, sin borrar nada— y los hashes son idénticos
antes y después:

| Archivo archivado | SHA-256 | Metadata conservada |
| --- | --- | --- |
| `terraform-state/terraform.tfstate` | `d60d6616…beb3b6` | serial **8**, lineage `4fd2e0b1-…-4d6b2f4e95ad`, 7 administrados + 1 data source, 4 outputs |
| `github-oidc/terraform.tfstate` | `8fc01b3e…e872aa` | serial **6**, lineage `5e5042e1-…-b2fa14584132`, 2 administrados + 1 data source, 2 outputs |
| `github-oidc/terraform.tfstate.backup` | `25690c0e…64f509a` | serial **4**, mismo lineage local |

Los dos lineage locales son los **antiguos**, distintos de los remotos: ninguna de
estas copias puede confundirse con la cadena autoritativa.

Cada root recibió un `MANIFEST.json` con hash, bytes, `mtime`, versión de state,
versión de Terraform, lineage, serial, recursos, outputs, ruta operativa de origen,
tarea que lo creó, fuente autoritativa actual con su VersionId y **referencia al
ciphertext GPG correspondiente con su SHA-256**.

Se retiró de las rutas operativas todo lo que permitiera volver al backend local: los
dos `local.tfbackend` se movieron al archivo renombrados a
`local.tfbackend.RETIRED-DO-NOT-USE`, conservados como evidencia de lo retirado.

**No se borró** `terraform-data/terraform.tfstate` de ningún `TF_DATA_DIR` operativo:
ese archivo es **metadata del backend inicializado**, no el state de recursos, y se
verificó que sigue describiendo S3.

### 17.3. Tres snapshots históricos marcados en sitio

Un barrido del árbol privado encontró otros tres archivos llamados exactamente
`terraform.tfstate` que **sí** son state de recursos: `restore-staging/` y los dos
`snapshots/…20260925T190328Z/` del bootstrap OIDC. Son snapshots de `Task/028` y
llevan el lineage local antiguo `5e5042e1-…`; ninguno fue nunca la ruta del backend
operativo.

No se movieron: cada directorio trae su propio `SHA256SUMS`, y desplazar los archivos
rompería la verificación de integridad en sitio. Se marcaron **en su lugar** con el
mismo texto de backup inactivo, y la verificación sigue pasando: **6, 5 y 6 archivos
OK, 0 fallos**.

Esto corrige una afirmación demasiado amplia hecha durante la ejecución, que dio por
metadata de backend a todos los `terraform.tfstate` restantes del árbol privado. Tras
la retirada, bajo ese árbol hay **exactamente dos** registros de backend, los dos
`s3` y los dos sin `resources`, y **tres** states de recursos, todos históricos,
inactivos y marcados.

### 17.4. Retirada del scaffolding de la prueba de contención

`lockprobe-tfdata` era el segundo `TF_DATA_DIR` creado solo para la prueba. Antes de
eliminarlo se comprobó que **no contenía state autoritativo propio**: su
`terraform.tfstate` tenía únicamente las claves `backend`, `terraform_version` y
`version`, **sin `resources` y sin `outputs`**. Su registro de backend sí apuntaba a
la key real, y por eso era un operador concurrente accidental en potencia.

Se conservaron en `h0302-lockprobe-removal-evidence.json` el inventario de sus cuatro
archivos con hashes, la constatación de que era solo metadata y el **resultado PASS**
completo de la prueba. Después se eliminó por entero.

Verificado tras la eliminación: `lockprobe-tfdata` **ausente**; los dos
`TF_DATA_DIR` operacionales **intactos y en `s3`**; y **ningún otro** registro de
backend `s3` en el árbol privado. Los seis directorios de validación offline no
tienen registro de backend —se crearon con `init -backend=false`— y por tanto no
pueden operar contra S3.

### 17.5. Postcondiciones de la retirada

| Comprobación | Resultado |
| --- | --- |
| `versions.tf` de ambos roots | `backend "s3" {}` |
| `TF_DATA_DIR` operacionales | los dos en `s3`, con su key correcta |
| `use_lockfile` | **true** en ambos; `encrypt=true`; `dynamodb_table=None` |
| `local.tfbackend` operativo | **ninguno** |
| `terraform.tfstate` histórico activo en ruta reutilizable como backend local | **ninguno**: el del backend operativo se archivó y los tres snapshots quedaron marcados como inactivos |
| Backups históricos recuperables | sí, con manifiesto legible y hashes verificados |
| Ciphertext GPG | intactos |

### 17.6. Custodia local: hallazgo inicial **erróneo** y su corrección

Esta subsección contenía una afirmación **falsa** y queda corregida aquí. Lo que se
dijo: que el runbook del bootstrap mentía al declarar «ACL NTFS comprobada: herencia
deshabilitada y acceso solo al usuario propietario y `SYSTEM`».

**El runbook tenía razón.** La medición se hizo sobre el directorio equivocado
—`%LOCALAPPDATA%\PersonalBlog`, el ancestro— en lugar de sobre el directorio que ese
runbook describe. Medido el 2026-09-28 sobre el directorio correcto:

| Ruta | Herencia | ACEs | `CodexSandboxUsers` |
| --- | --- | --- | --- |
| `%LOCALAPPDATA%\PersonalBlog\bootstrap\terraform-state` | **deshabilitada** | **2**, explícitas | **sin acceso** |

Sus dos ACEs son exactamente `NT AUTHORITY\SYSTEM` FullControl y `jeff\jeffe`
FullControl, heredables a archivos y subdirectorios. Los 30 artefactos de ese subárbol
—incluidos los **dos ciphertext GPG** y los tars en claro— **no** son legibles por
`CodexSandboxUsers`. El contrato documentado se cumplía.

**El hueco real estaba en otro sitio**: `%LOCALAPPDATA%` lleva un ACE
`jeff\CodexSandboxUsers: ReadAndExecute` puesto por la instalación de Codex, y lo
heredaban `bootstrap\github-oidc` y `bootstrap-backups`, es decir el root de custodia
de EX-028-C7 y el archivo histórico creado en §17.2. Ahí sí había una promesa
incumplida: la propia excepción exigía `umask 077`, `0700/0600` y propietario.

Ese hueco se cerró bajo la autorización `Task/030 H-030-2-custodia-local`; el
procedimiento, su alcance exacto y la ACL final medida están en §18.

### 17.7. Extinción de EX-028-C7

**EX-028-C7 queda Extinguida el 2026-09-28.** La justificación es estrictamente
factual:

- los dos states de bootstrap están en S3;
- los dos convergen **0/0/0** con `resource_drift = 0`;
- el **locking nativo** quedó probado por **contención real**, no por inferencia;
- el **recovery versionado** quedó probado en ambas keys;
- **S3 es la única fuente operacional**;
- los states locales quedan **solo** como backups históricos inactivos;
- **no existe ningún segundo backend local activo**.

Se distingue lo que ya estaba cerrado de lo que se cierra ahora: la **custodia** de
EX-028-C7 quedó cerrada en `Task/028` con copias cifradas y recuperación verificada;
la **excepción** se extingue aquí. Esa distinción la exigía el reporte de
`Task/028.2`.

Documentos actualizados en su estado **canónico y actual**: registro de decisiones
abiertas —fila de excepciones vigentes y addendum de `Task/028`—,
`PROJECT_INSTRUCTIONS` §§15–16, ficha y reporte de Task/030, runbook del bootstrap de
state, runbook del bootstrap OIDC, índice de runbooks, STATUS, ROADMAP y STAGE-10,
donde su criterio de aceptación pasa a marcado.

**No se reescribió la historia.** Las referencias que describen correctamente fases
anteriores se conservan: la §2 del runbook OIDC mantiene el contrato completo de la
excepción, ahora encabezado por su estado extinguido; el reporte y la ficha de
`Task/028`, STAGE-08, STAGE-09 y los reportes de `Task/028.2` y `Task/029` quedan
intactos. La revisión a 30 días que preveía la excepción queda **sin objeto**, no
cancelada: la excepción ya no existe.

**H-030-2 queda COMPLETO.** Esto **no** significa que Task/030 esté aprobada ni
cerrada: restan **D-08** y el **S3 de medios** con sus pruebas reales, y la
aprobación final sigue dependiendo exclusivamente del usuario.

## 18. H-030-2-custodia-local — ACL corregida y endurecimiento dirigido

Autorización exacta: `Task/030 H-030-2-custodia-local`. Alcance concedido: corregir la
deuda documental de §17.6 y ejecutar una variante **estricta** del endurecimiento.
**No** se autorizó endurecer el root completo `bootstrap/github-oidc` ni tocar la ACL
de ninguno de los dos `terraform-data` operativos; ninguno de los dos se tocó.
Tampoco se cambió AWS, ni GPG, ni contenido de archivos, ni owner, ni la membresía de
`CodexSandboxUsers`, ni se borró o movió nada.

### 18.1. Deuda documental corregida

La afirmación de §17.6 era **falsa** y quedó rectificada allí mismo, además de en §18
de la ficha, en el runbook del bootstrap de state —donde el contrato de ACL queda
**reconfirmado** por medición— y en los marcadores y la evidencia privados.
`bootstrap/terraform-state` **sí** cumple lo documentado: herencia deshabilitada, dos
ACEs explícitas (`NT AUTHORITY\SYSTEM` y `jeff\jeffe`, ambas FullControl) y
**sin acceso** de `CodexSandboxUsers`. No se alteró historia ajena a Task/030.

### 18.2. Diagnóstico de solo lectura previo

| Medida | Resultado |
| --- | --- |
| Origen del ACE | `%LOCALAPPDATA%` lleva `jeff\CodexSandboxUsers: ReadAndExecute`, puesto por la instalación de Codex; lo heredaban `bootstrap\github-oidc` y `bootstrap-backups` |
| Miembros del grupo | exactamente dos cuentas locales: `jeff\CodexSandboxOffline` y `jeff\CodexSandboxOnline` |
| Credenciales o secretos en los states | **ninguno** |
| `sensitive_attributes` no vacíos | **ninguno**; el campo existe en 3 y 8 instancias, vacío en todas |
| Outputs marcados `sensitive` | **ninguno** |
| Lo que sí contienen | Account ID, ARNs, documento de trust, `client_id_list`, `thumbprint_list`, nombre y policy del bucket: **topología de identidad**, no material de autenticación |
| Redundancia | 28 states sueltos con solo **8 contenidos únicos** |

### 18.3. Alcance endurecido

Modelo aplicado, idéntico al ya probado en `bootstrap/terraform-state`: herencia
deshabilitada y **únicamente** `jeff\jeffe` FullControl y `NT AUTHORITY\SYSTEM`
FullControl, heredables en directorios.

Seis directorios: `github-oidc/h0302-close-preflight`,
`github-oidc/h0302-oidc-readback`, `github-oidc/h0302-recovery-isolated`,
`github-oidc/restore-staging`, `github-oidc/snapshots` y
`bootstrap-backups/INACTIVE-HISTORICAL-STATES`.

Tres states sueltos que viven **directamente** en el root del bootstrap OIDC
—`h0302-oidc-conv-state-before.tfstate`, `h0302-oidc-state-backup-before.tfstate` y
`h0302-oidc-state-before.tfstate`— se endurecieron **por archivo**, porque su
directorio contenedor es justo el root que no se autorizó tocar.

Veintitrés artefactos más del mismo root, también por archivo, porque se demostró que
son **evidencia de state**: siete planes JSON con `prior_state` y 98 campos de
atributos cada uno, ocho binarios `.tfplan` que embeben ese mismo state comprimido,
los dos readbacks IAM con trust y ARN reales, y seis logs de plan con cuenta y ARN.

El subárbol del archivo histórico se fijó con ACL **explícita en sus trece objetos**,
no heredada: su protección ya no depende de las ACLs que el `mv` de §17.2 conservó por
accidente.

### 18.4. Clasificación final, que es el punto importante

| Clase | Qué es | Legible por `CodexSandboxUsers` |
| --- | --- | --- |
| **Resource state en plaintext** | 28 `.tfstate`/`.backup` con `resources` y `lineage`, más 7 tars en claro que los contienen | **0 de 35** |
| **Evidencia de state OIDC** | 7 planes JSON, 8 binarios de plan, 2 readbacks IAM, 6 logs con ARN | **0 de 23** |
| **Metadata de backend (`terraform-data`)** | `{backend, terraform_version, version}`; **sin `resources`, sin `outputs`** | `github-oidc` **sí**, `terraform-state` no |
| **Configuración operacional** | `remote.tfbackend`, `bootstrap.auto.tfvars.json`, `config.private.json`, `inventory.private.json`: llevan Account ID, **no** resource state | **sí**, no tocados por orden expresa |

Queda explícito: **dejar `terraform-data` accesible no deja accesible ningún resource
state histórico.** Ese archivo describe *dónde* vive el state y con qué opciones de
backend; no contiene ni un recurso administrado. El resource state histórico y su
evidencia están, sin excepción, fuera del alcance de `CodexSandboxUsers`.

El residuo legible se declara en lugar de ocultarse: cuatro archivos de configuración
operacional y la metadata de backend del root OIDC, todos con Account ID y nombre de
bucket, ninguno con state. Cerrarlos exigiría tocar configuración que la autorización
excluía.

### 18.5. Verificación posterior

| Gate | Resultado |
| --- | --- |
| Ambos `terraform-data` presentes | **sí**, sin cambios de ACL |
| Ambos describen backend S3 | **sí**: `use_lockfile=true`, `encrypt=true`, sin DynamoDB, key correcta |
| Resource state histórico legible por Codex | **0 de 35** |
| Evidencia de state OIDC legible por Codex | **0 de 23** |
| `SHA256SUMS` históricos | **6, 5 y 6 archivos OK, 0 fallos** |
| Manifiestos del archivo | íntegros y legibles |
| Ciphertext GPG | `dcb4b567…c9c078` y `3e56b271…33044715`, intactos |
| States archivados | `d60d6616…`, `8fc01b3e…`, `25690c0e…`, intactos |
| Owner | `JEFF\jeffe` en todos los objetos tocados, sin cambios |
| Acceso de `jeffe` | comprobado leyendo contenido real tras endurecer |
| `fmt` / `validate` / `test` | OK en ambos roots; **9/9** y **5/5** |
| Suites Python | `oidc` 60 (1 omitida), `terraform_state` 12, `laboratorio` 176, `security` 88: OK |
| Gitleaks 8.30.1 | 279 archivos versionables, **0 hallazgos** |
| Enlaces, `git diff --check`, provider locks | 1865 destinos sin roturas reales; limpio; intactos |
| Sin Account ID ni identificador de operador en Git | confirmado |

### 18.6. Interrupción por sesión expirada y revalidación AWS completada

La sesión AWS expiró durante la primera verificación y tres gates quedaron sin
comprobar, de modo que **H-030-2 no se declaró cerrado en ese momento**. Los dos
planes fallaron en la **resolución de credenciales del backend**, antes de emitir
petición alguna a S3: `No valid credential sources found` y
`login session has expired`. No se creó artefacto de plan, no quedó lock local y los
dos `terraform-data` siguieron describiendo S3.

Tras la renovación humana del perfil, la revalidación se ejecutó **el 2026-09-28** y
pasó por completo. Confirmación adicional de que aquellos dos intentos nunca llegaron
a S3: el historial de `.tflock` **no registra ningún ciclo suyo**.

| Gate revalidado | Resultado |
| --- | --- |
| Identidad | `assumed-role/PersonalBlogAdministrator/personal-blog-entry-admin`, perfil personal-blog, us-east-2 |
| `.tflock` de ambas keys | **ausentes (404)**; historial emparejado, **9 versiones / 9 delete markers** en state y **7 / 7** en OIDC: ningún lock abierto |
| `bootstrap/terraform-state` remoto | VersionId `pjvyHqNzxTObDUSOcwVbuXSwAD3I4RM2`, 12 864 bytes, AES256, SHA-256 `65c96bb0…5a4eb0`, lineage `d33d9c1e-…`, **serial 2**, siete recursos y un data source, cuatro outputs: **0 desviaciones** |
| `bootstrap/github-oidc` remoto | VersionId `Dl7AxGe7qj28P703ZFJwh_qsRzY2ViHI`, 5 840 bytes, AES256, SHA-256 `cb16264b…1fb524`, lineage `973e160f-…`, **serial 1**, dos recursos y un data source, dos outputs: **0 desviaciones** |
| Plan normal `terraform-state` | exit **0**, 0/0/0, `resource_drift = 0`, **siete** no-op, cuatro outputs no-op, dos checks pass, 0 imports/moves/replaces, `applyable=false`, cero warnings |
| Plan normal `github-oidc` | exit **0**, 0/0/0, `resource_drift = 0`, **dos** no-op, dos outputs no-op, ocho checks pass, 0 imports/moves/replaces, `applyable=false`, cero warnings |
| State tras los planes | VersionId, longitud, `LastModified` y **SHA-256 reverificado por descarga**: idénticos. Ningún plan se aplicó |
| `.tflock` tras los planes | **ausentes (404)** |
| `PersonalBlogGitHubOidcValidation` | **cero** managed, **cero** inline, **cero** instance profiles, **sin** permissions boundary, `max_session_duration` 3600, trust con una sola condición `StringEquals`, `Allow` sobre `sts:AssumeRoleWithWebIdentity`, audiencia `sts.amazonaws.com`, subject de `refs/heads/main` |
| Proveedor OIDC | `token.actions.githubusercontent.com`, `ClientIDList` exactamente `["sts.amazonaws.com"]`, un thumbprint |

Los planes se ejecutaron con los `TF_DATA_DIR` **operativos** de cada root, cuya ACL
no se tocó, y sus artefactos se escribieron dentro de directorios **ya protegidos**:
los ocho archivos nuevos heredaron las dos ACEs y **ninguno** quedó legible por
`CodexSandboxUsers`, sin modificar un solo permiso. El endurecimiento sostiene también
la evidencia futura.

No se escribió ni reemplazó ningún state, no se modificó IAM y no se repitió el
endurecimiento de ACL.

**H-030-2 queda COMPLETO**, con la custodia local alineada con el contrato
documentado. **EX-028-C7 permanece Extinguida.** Task/030 sigue **En progreso**:
restan **D-08** y el **S3 de medios**, y **no existe aprobación final**.

## 19. H-030-D08 — DISEÑO DE ACCESO A MEDIOS

> **Propuesta — pendiente de aprobación.** No crea ni modifica infraestructura AWS, no
> ejecuta `apply`, no toca H-030-2 y no inicia H-030-3. D-08 sigue **Abierta** hasta que
> el usuario decida los puntos de §19.9.

### 19.1. Estado actual real del código, verificado

| Pieza | Estado medido |
| --- | --- |
| Puerto `ObjectStorage` | Cinco operaciones más la sonda: `guardar`, `obtener`, `existe`, `eliminar`, `comprobar_disponibilidad`, `acceso_temporal`. **No existe `listar`** |
| Adaptadores | `S3Storage` (producción) y `MinIOStorage` (local), misma interfaz; `access_endpoint_url` existe y en producción **se omite** |
| Claves | `medios/<uuid4>/original.<ext>` y `medios/<uuid4>/thumbnail.webp`; UUID v4, **122 bits**, nombre original nunca participa; la miniatura **se deriva** |
| Subida | **Mediada por el backend**: `UploadFile`, validación por **decodificación** real, JPEG/PNG/WebP, **5 MiB**, 40 Mpx. **No hay PUT directo del navegador** |
| Escritura de metadatos | `put_object` escribe **solo `ContentType`**. **No se escribe `Cache-Control`** |
| Acceso público | `access_url` y `thumbnail_access_url`, prefirmadas, **generadas al servir**, nunca persistidas; `object_key` no es campo del contrato |
| TTL | `BLOG_STORAGE_ACCESS_TTL_SECONDS`, defecto **900 s**, rango declarado 60…604800 |
| Consumo en el frontend | **Únicamente `<img src={access_url}>`** vía `MediaImage`. No hay `fetch`/XHR/canvas contra el almacenamiento |
| Imágenes en el cuerpo | **No existen.** El editor no inserta imágenes; el medio se asocia por `cover_id`, `thumbnail_id` o `photo_id` |
| Consumidores de medios | `posts.cover_id`, `book_reviews.cover_id`, `projects.cover_id`, `videos.thumbnail_id`, `profile.photo_id` |
| Separación publicado/borrador | La impone la **consulta**: los repositorios públicos filtran `status = 'published'` (invariante 19). El módulo `media` **no conoce** el estado |
| `og:image` | Imagen **estática del sitio** en `public/`, absoluta, sin firma (D-016-A). El `og:image` por contenido está **bloqueado**: `B-016-1` |
| CORS del bucket local | **No hay** configuración CORS en MinIO local |
| Terraform de medios | `terraform/modulos/almacenamiento/` **ya existe** (Task/025): bucket privado, ownership `BucketOwnerEnforced`, BPA con cuatro flags, versionado, SSE-S3, policy que niega no-TLS, lifecycle de versiones no actuales y aborto de multipart, y **CORS condicional que no se crea si la lista de orígenes está vacía** |

### 19.2. Contratos que no se pueden romper

1. **Nunca se persiste una URL prefirmada como dato canónico.** Regla ya vigente de D-08.
   La base guarda `object_key`; la URL se genera al servir.
2. **Ningún campo del contrato transporta `object_key`.** Fijado por prueba.
3. `access_url` y `thumbnail_access_url` son **temporales** y no valen como `og:image`.
4. **`access_expires_at` no se expone**, deliberadamente: declarar la caducidad es describir
   la semántica de caché, que es justo lo que D-08 decide.
5. D-15 **resuelta**: same-site, panel en `/admin`, API en `api.<dominio>`, CORS con lista
   explícita y comodín prohibido.
6. **D-07 sigue abierta** (`Task/035`): el dominio y sus subdominios —incluido un posible
   `media`— no existen todavía.
7. **El BPA de cuenta está aplicado** con sus cuatro flags (H-030-1): ningún bucket de la
   cuenta puede volverse público sin retirar ese control.

### 19.3. Hechos verificados contra documentación oficial

| Hecho | Consecuencia de diseño |
| --- | --- |
| Una URL prefirmada creada con **credenciales temporales caduca cuando caduca la credencial**, aunque se pida más tiempo. Con `AssumeRole` la sesión son **60 min** por defecto; EC2/ECS rotan en 1–6 h | **Desde Lambda es imposible una prefirmada estable de días.** El límite superior de 604800 s que admite la configuración es **inalcanzable en producción**: es un rango engañoso |
| El máximo con credenciales de usuario IAM y SigV4 son **7 días** | Requeriría una **clave de larga vida**, prohibida por S-01. Descartado |
| Una prefirmada es un **bearer token**: quien la tenga accede | El TTL es el control de exposición, no la autenticación |
| **CORS de S3 solo interviene en peticiones cross-origin de JavaScript** (preflight). Cargar un objeto con `<img>` **no** es un escenario CORS | **El bucket de medios no necesita CORS** con el consumo actual. El módulo ya lo deja sin crear cuando la lista está vacía: ese es el valor correcto |
| Lambda limita la invocación síncrona a **6 MB de petición y 6 MB de respuesta** | Una imagen de **5 MiB** en base64 ocupa ≈ **6,67 MB** y **excede el límite**. Un proxy del **original** por Lambda + API Gateway **no es viable** para el tamaño máximo permitido |
| CloudFront tiene tramo **siempre gratuito**: **1 TB/mes** de salida y **10 M** peticiones HTTP/HTTPS, ya sin la restricción de 12 meses | Un CDN delante del bucket **no añadiría coste** a la escala de este blog |
| Tarifas S3 Ohio reconsultadas el 2026-09-28: almacenamiento **0,023 USD/GB-mes**; PUT/LIST **0,005/1.000**; GET **0,0004/1.000**; egress facturable **0,09 USD/GB**, con **100 GB/mes** globales sin cargo | El coste de medios a esta escala es de **céntimos**; lo que manda es no introducir coste **fijo** |

### 19.4. Los nueve casos, resueltos

**A. Subida de administración.** Autorización por la sesión administrativa existente
(cookie `HttpOnly`, D-011-B) sobre `POST` admin. **Sigue siendo mediada**: el contenido se
valida decodificándolo, y eso es incompatible con un PUT directo del navegador, que
entregaría al almacenamiento bytes que nadie ha inspeccionado. `Content-Type` **no se
cree**: se deriva del formato validado. Límites 5 MiB y 40 Mpx. Clave generada por el
dominio, nunca por el cliente. `guardar` **sobrescribe** por contrato, pero la clave es un
UUID nuevo por subida, así que en la práctica no hay colisión ni sobreescritura. **Propuesta:
no se introduce PUT prefirmado.** Evita CORS de escritura, evita validar después de escribir
y mantiene la única puerta de entrada.

**B. Medios de borrador.** Los emite únicamente el endpoint administrativo, autenticado.
**Propuesta: siguen siendo prefirmadas y con TTL corto**, y no obtienen nunca ruta estable.
Al expirar, el panel vuelve a pedir el recurso y recibe un enlace nuevo; la vista previa del
editor usa el mismo mecanismo. Se declara sin adornos: mientras el enlace vive es un bearer
token, de modo que un borrador compartido por error es legible durante el TTL. Ese es el
argumento para **no** alargarlo.

**C. Medios publicados.** Hoy el sitio público los consume con `<img src=access_url>`, con
un enlace nuevo en cada respuesta del API. Funciona, pero **la URL cambia en cada carga**, lo
que anula la caché del navegador: cada visita vuelve a descargar los bytes. No es un defecto
de corrección, es coste y latencia. **Propuesta en dos partes**: (i) mantener el objeto
privado y la prefirmada como vía de lectura en página, y (ii) **cuantizar la firma** —firmar
con una caducidad redondeada a una ventana— para que dentro de esa ventana el API devuelva
**la misma URL** y el navegador pueda reutilizar su caché. Es un cambio **solo de código**,
sin infraestructura nueva y sin tocar el contrato.

**D. `og:image` y crawlers.** Es el caso que **no** admite prefirmada: Meta, X y LinkedIn
recrawlean días o semanas después, y cualquier TTL alcanzable desde Lambda habrá expirado.
Hoy se resuelve con una imagen estática de sitio (D-016-A) y el `og:image` por contenido está
bloqueado por `B-016-1`. **Propuesta: una *tarjeta social* derivada, publicada
explícitamente.** Al publicar un contenido con portada, el backend deriva un objeto propio
bajo un prefijo **distinto y deliberadamente legible**, por ejemplo
`publico/social/<content-uuid>.jpg`, y **solo ese prefijo** se sirve por una ruta estable. El
prefijo `medios/` conserva intacta su garantía actual. Lo que se persiste sigue siendo un
identificador estable, nunca una URL firmada.

**E. Borrado y reemplazo.** Ya resuelto en el código y no se cambia: el borrado comprueba
uso previo, el orden de compensación deja como peor caso **objetos huérfanos** y nunca una
fila que apunte a un objeto ausente. Reemplazar una imagen es **subir un medio nuevo** y
reapuntar `cover_id`: la clave antigua no se sobrescribe, así que ninguna referencia viva se
rompe. El versionado del bucket protege frente a sobreescrituras accidentales y el lifecycle
ya escrito expira **versiones no actuales**, no objetos actuales. **Propuesta**: fijar
`dias_para_expirar_versiones` en **30** y mantener el aborto de multipart en 7 días; añadir
a la deuda una **recolección de huérfanos** con inventario previo, nunca un borrado
automático. Si se adopta la tarjeta social, su objeto se **regenera** al republicar y se
**borra** al despublicar.

**F. CORS.** Con el consumo actual —`<img>` y nada más— **el bucket no necesita CORS**, y el
módulo de Terraform ya no crea el recurso cuando la lista está vacía. **Propuesta: lista
vacía en producción**, y documentar el disparador que obligaría a revisarlo: que el frontend
pase a leer píxeles con `fetch`, `canvas` o `crossorigin`. En local tampoco hay CORS en
MinIO, así que producción y local coinciden. Esto no cambia el CORS del **API**, que es D-15
y sigue con su lista explícita.

**G. Caché.** Hoy los objetos **no llevan `Cache-Control`**, así que ningún intermediario
sabe qué hacer con ellos. **Propuesta por clase**: originales y miniaturas
`public, max-age=31536000, immutable` —son inmutables de verdad: la clave contiene un UUID y
un reemplazo crea otra clave—; tarjetas sociales `public, max-age=86400` porque sí se
regeneran. `ETag` lo entrega S3 sin configuración. **Invalidación**: no hace falta, porque
nada se sobrescribe bajo la misma clave; ese es el beneficio real de una clave
*content-addressed* por UUID. Requiere un cambio de código: `guardar` debe poder escribir
`Cache-Control`. Sin la cuantización de firma del caso C, ese `max-age` no se aprovecha en
página, porque la URL cambia; las dos piezas van juntas.

**H. Seguridad.** Se conserva todo lo que ya está escrito: bucket privado, BPA con cuatro
flags, `BucketOwnerEnforced`, policy que niega transporte no TLS, SSE-S3. **IAM mínimo
propuesto**, por función y sobre el ARN exacto del bucket: la Lambda de aplicación necesita
`s3:PutObject`, `s3:GetObject` y `s3:DeleteObject` sobre `medios/*`; **no** necesita
`s3:ListBucket`, porque el puerto no tiene `listar` y la biblioteca de medios se pagina
desde PostgreSQL. Esa ausencia es la que impide enumerar el bucket desde la aplicación.
Si se adopta la tarjeta social, añade `s3:PutObject` y `s3:DeleteObject` sobre
`publico/social/*`. La identidad de CI es de `Task/038`/`Task/039` y **no** se mezcla. El rol
de validación OIDC sigue sin políticas. **Se declara el cambio de garantía**: hoy *«conocer
la clave no da acceso»*; con cualquier ruta estable, conocer la URL **sí** da acceso a lo que
esa ruta cubra, y por eso la propuesta la acota a un prefijo que solo contiene material ya
publicado.

**I. Coste.** Escenario holgado para un blog personal: 1 GB almacenado, 2.000 PUT y 50.000
GET al mes, 5 GB de egress. Almacenamiento 0,023 USD; PUT 0,010 USD; GET 0,020 USD; egress
**0 USD** dentro de los 100 GB globales sin cargo, o 0,45 USD si no quedara franquicia.
Total: **entre 0,05 y 0,50 USD/mes**, dentro del sublímite de D-13. **Coste fijo nuevo: cero
en todas las alternativas que se proponen.** CloudFront no añadiría coste a esta escala por
su tramo siempre gratuito, pero **sí añade un servicio** que hay que declarar, versionar y
operar. La caché del navegador que habilita C+G reduce GET y egress; el proxy por Lambda los
aumentaría, porque añade invocación y duración por imagen.

### 19.5. Alternativas comparadas

**1. Bucket privado + prefirmada para todo (statu quo).** Seguridad alta: nada legible sin
firma. URL **inestable** por diseño. **Incompatible con `og:image`**: ningún TTL alcanzable
sobrevive a un recrawl. Caché mala salvo que se cuantice la firma. Complejidad **cero**:
ya funciona. Coste mínimo. Cero impacto en backend, frontend y Terraform. Migrable después
sin fricción. **Deja `B-016-1` abierto.**

**2. Bucket privado + ruta estable servida por el backend.** Seguridad alta: el gating vive
en código y respeta `status = 'published'`. URL **estable**. Compatible con `og:image`.
Caché controlable por cabeceras propias. **Bloqueo demostrado: el límite de 6 MB de respuesta
de Lambda es menor que una imagen de 5 MiB en base64 (≈6,67 MB)**, así que no sirve para el
original en su tamaño máximo; sí para miniaturas y tarjetas sociales, que son pequeñas.
Añade invocación, duración y doble transferencia por imagen. Con la Lambda en VPC según
ADR-010 exige además un **endpoint de S3** —gratuito, pero decisión de `Task/031`—, mientras
que **firmar no necesita red alguna**. Impacto: backend sí, frontend leve, Terraform leve.

**3. Bucket privado + CloudFront con OAC.** Seguridad: el bucket sigue privado y solo
CloudFront lo lee; **lo que el CDN cubra pasa a ser legible por URL**, sin firma. URL
**estable**. `og:image` **compatible**. Caché **la mejor**: es un CDN de verdad. Coste
**0 USD** a esta escala por el tramo siempre gratuito de 1 TB y 10 M peticiones, sin coste
fijo. Complejidad media: **servicio nuevo**, distribución, OAC, política de caché y, para un
dominio propio, certificado y DNS que dependen de **D-07**. Mientras D-07 no exista puede
usarse el dominio `cloudfront.net`. **Riesgo a declarar**: si se apunta a todo `medios/`,
expone también portadas de borradores a quien conozca la clave, debilitando una garantía hoy
escrita. Migrable: sí, y es la evolución natural de la alternativa 5.

**4. Bucket o prefijo público.** **Foreclosada por la propia cuenta**: el BPA de cuenta
aplicado en H-030-1 tiene `block_public_policy` y `restrict_public_buckets` en `true`, así
que una policy pública sería rechazada. Habilitarla exigiría **retirar un control de
seguridad ya aplicado**. Se descarta y no se propone. Como corolario, **Cloudflare no puede
servir este bucket sin un Worker que firme**, porque no hay origen público que consumir: el
Worker está excluido salvo decisión explícita.

**5. Combinación distinta para borrador y publicado.** Es la que **se propone**. Borrador y
lectura en página: prefirmada con TTL corto, como hoy. Material explícitamente publicado
—la tarjeta social— en un prefijo separado con ruta estable. Seguridad: conserva intacta la
garantía de `medios/` y expone solo lo que ya es público por decisión editorial. URL estable
donde hace falta. `og:image` **resuelto**. Caché buena en el prefijo público y aceptable en
página con la firma cuantizada. Complejidad contenida. Coste en céntimos. Migrable a la
alternativa 3 sin rehacer nada: cambia el *vehículo* de la ruta estable, no el contrato.

### 19.6. Contrato de datos propuesto

Se **confirma y refuerza** lo que el proyecto ya hace:

| Qué | Dónde vive | Naturaleza |
| --- | --- | --- |
| `object_key` del original | `media_assets.object_key` | **Persistido, estable, no expuesto** |
| Clave de la miniatura | **Derivada** de la del original | No persistida |
| `access_url`, `thumbnail_access_url` | Generadas al servir | **Temporales, nunca persistidas** |
| Referencia del contenido a su imagen | `cover_id`, `thumbnail_id`, `photo_id` | **Persistida, estable** |
| Clave de la tarjeta social *(propuesta)* | **Derivada** del identificador del contenido | No persistida; el objeto existe solo si el contenido está publicado |
| URL de la tarjeta social *(propuesta)* | Compuesta al servir, a partir de una **base configurable** | No persistida |

**Ninguna URL se convierte en dato canónico**, tampoco la estable: se **compone** de una base
de configuración más una clave derivada, para que cambiar de vehículo —backend hoy, CDN
mañana— no exija migrar datos. **El código actual no contradice nada de esto**; el único
hueco real es que `guardar` no puede escribir `Cache-Control`.

### 19.7. Cambios necesarios si se aprueba la propuesta

**Backend.** Ampliar `guardar` para aceptar `Cache-Control` —con su caso de prueba en el
contrato de ambos adaptadores—. Cuantizar la caducidad de la firma en `AccesoAMedios` para
que la URL sea estable dentro de una ventana. Derivar, publicar y retirar la tarjeta social
en los casos de uso de publicación y despublicación. Añadir la base configurable de la ruta
estable. Todo ello es **comportamiento funcional nuevo**, así que entra íntegro en la
**BACKEND TEST-FIRST LAW**: matriz de comportamiento, RED demostrado, GREEN mínimo,
regresión completa.

**Frontend.** Consumir la tarjeta social como `og:image` por contenido, sustituyendo la
imagen de sitio cuando exista, y **retirar `B-016-1`** al cerrarse. Los guardas de SEO que
hoy prohíben cualquier `og:image` caducable **se conservan**: la tarjeta no caduca. No hay
cambios en `MediaImage`.

**Terraform.** El módulo de medios **ya está escrito**. Valores a fijar en el destino:
`origenes_cors = []`, `dias_para_expirar_versiones = 30`, `forzar_destruccion = false`. La
política IAM mínima de §19.4-H va al módulo de identidad. Si se elige la alternativa 3, se
añade distribución, OAC y política de caché, y la política del bucket gana un `Allow` para el
*service principal* de CloudFront acotado por `AWS:SourceArn`.

**Contrato API.** El cambio es **compatible**: añadir un campo opcional con la URL estable de
la tarjeta social no retira ni renombra nada. **No** se expone `object_key` y **no** se
expone `access_expires_at`.

### 19.8. Pruebas de aceptación propuestas

Contra AWS real, en H-030-3: que el objeto **no** sea legible sin firma; que la prefirmada
funcione y **deje de funcionar** al expirar; que una prefirmada emitida para un borrador no
aparezca en ninguna respuesta pública; que `Cache-Control` viaje en la respuesta de S3; que
la URL en página **se repita** dentro de la ventana de cuantización y cambie al cruzarla; que
la tarjeta social responda **200 sin credenciales** y sin firma; que `HeadBucket` y un `GET`
de clave inexistente devuelvan lo esperado; controles negativos de IAM que demuestren que la
identidad de aplicación **no puede** listar el bucket ni leer fuera de su prefijo; que la
regla de lifecycle esté **aceptada**, sin afirmar que una versión haya expirado; y que
`S3Storage` pase el mismo contrato que MinIO. Todo con evidencia saneada y sin snapshots.

### 19.9. Decisiones humanas requeridas — H-030-D08

| # | Decisión | Por qué no la tomo yo |
| --- | --- | --- |
| 1 | ¿Se acepta la **tarjeta social derivada** en un prefijo legible, como vía para el `og:image` por contenido? | Cambia la garantía *«conocer la clave no da acceso»* para ese prefijo y crea objetos nuevos |
| 2 | Vehículo de la ruta estable: **backend** ahora o **CloudFront con OAC** | CloudFront es un **servicio AWS nuevo**; sin coste a esta escala, pero con operación y Terraform propios |
| 3 | ¿Se acepta el **cambio de contrato API compatible** que añade la URL estable de la tarjeta? | Un campo de `v1` ya no se retira |
| 4 | **TTL productivo** y ventana de cuantización | Es el control de exposición de los borradores; propongo 900 s con ventana de 300 s |
| 5 | ¿Se acepta **modificar el backend** —`Cache-Control`, firma cuantizada, derivación de la tarjeta— dentro de Task/030, o se traslada a una tarea propia? | Es comportamiento funcional nuevo bajo la ley test-first, y la ficha declara *«no cambiar código backend/frontend»* |
| 6 | `dias_para_expirar_versiones = 30` y recolección de huérfanos como deuda con propietario | Política de retención y de borrado |
| 7 | Si se rechazan 1 y 2: ¿se **acepta formalmente** quedarse sin `og:image` por contenido y mantener `B-016-1` abierto? | Es una renuncia de producto, no técnica |

**Lo que la propuesta NO requiere**, y se hace constar: **no** requiere Cloudflare, **ni**
Worker, **ni** Lambda@Edge, **ni** API Gateway adicional, **ni** bucket o prefijo público
—foreclosado por el BPA de cuenta—, **ni** KMS, **ni** DynamoDB, **ni** NAT Gateway, **ni**
ningún coste fijo. CloudFront aparece **solo** como opción explícita de la decisión 2.

**Parada.** D-08 sigue **Abierta**. No se crea bucket, no se ejecuta `apply`, no se cambia
IAM, no se inicia H-030-3 ni `Task/031`, y no hay commit, push, PR ni merge. Task/030 sigue
**En progreso** y sin aprobación.

## 20. H-030-D08-MVP — D-08 RESUELTA para el MVP

El usuario escribió `authorize: Task/030 H-030-D08-MVP` y fijó una política
**deliberadamente conservadora**: se resuelve D-08 con lo que ya existe y **no se introduce
ningún servicio nuevo**. Quedan expresamente **rechazadas** la tarjeta social derivada,
CloudFront, Cloudflare o Worker, la ruta estable servida por el backend, el cambio de
contrato API, cualquier cambio funcional de backend o frontend y la firma cuantizada. Las
trece decisiones íntegras están en el registro canónico,
[open-decisions §D-08](../architecture/open-decisions.md).

| # | Decisión del MVP |
| --- | --- |
| 1 | Bucket de medios **privado** |
| 2 | Borrador **y** publicado: **presigned GET generado dinámicamente** |
| 3 | La base persiste **solo `object_key`** y referencias estables; **nunca** una prefirmada |
| 4 | **No existe URL pública estable por contenido** |
| 5 | `og:image` sigue siendo la **imagen estática del sitio** (D-016-A) |
| 6 | **`B-016-1` permanece abierto**: limitación de producto **aceptada**, no bloqueo de Task/030 |
| 7 | **Sin CDN** en Task/030; si hiciera falta, se **reabre** con tarea y decisión propias |
| 8 | TTL productivo **900 s** |
| 9 | **Sin firma cuantizada** |
| 10 | CORS **`origenes_cors = []`**, con disparador de reconsideración documentado |
| 11 | *Lifecycle*: versiones no actuales **30 días**, *multipart* **7 días**; sin *lifecycle* de objetos actuales; sin borrado automático de huérfanos, que queda **deuda con propietario** |
| 12 | `forzar_destruccion = false` |
| 13 | **Sin** KMS, DynamoDB, NAT, CloudFront, servicio adicional ni coste fijo |

**Disparador del CORS**, escrito para que nadie lo revise por inercia: que el frontend pase
a leer píxeles con `fetch`, `XMLHttpRequest`, `canvas` o `<img crossorigin>`. Mientras el
consumo sea `<img src>` sin `crossorigin`, S3 **no interviene en ningún preflight** y la
lista vacía es la configuración correcta, no un olvido.

**`B-016-1` queda abierto por construcción.** La decisión 4 niega justamente la URL estable
que ese bloqueo necesita. Resolver D-08 **no** lo desbloquea, y eso es intencionado.

Documentación vigente actualizada: registro canónico —fila de D-08, cabecera de recuentos
(**6 abiertas**, **15 resueltas**) y sección propia con la resolución y su historia—,
`api-contracts` §12 —la tabla de preguntas abiertas pasa a tabla de respuestas, dejando
constancia de que **el contrato público no cambia**—, ficha de Task/030, STATUS, ROADMAP y
STAGE-10. La historia previa de D-08 y de `Task/016` se conserva íntegra.

## 21. H-030-4 — H-030-3 BLOQUEADO: el grafo único no admite un plan solo de medios

Tras cerrar D-08 se preparó H-030-3. **Se detiene como H-030-4 antes de generar cualquier
plan real**, porque el bloqueo es estructural y afecta al diseño vigente, no a un valor de
configuración. **No se creó ningún recurso**: la cuenta sigue con **un solo bucket**, el de
state.

### 21.1. El bloqueo, con su evidencia

**1. `terraform/` es UN SOLO GRAFO, por decisión escrita.** Su `main.tf` declara seis
módulos encadenados —`almacenamiento`, `parametros`, `registro`, `identidad`, `computo`,
`api_http`— y dice literalmente *«UN SOLO GRAFO … no hay `count` por entorno, ni módulos
alternativos, ni recursos que solo existan en un destino»*. Es la regla de portabilidad de
[aws-local-parity](../architecture/aws-local-parity.md) §4, y el riesgo **R-26** es
exactamente lo contrario. La **AWS LOCAL PARITY LAW** lo repite: *«No duplicar módulos.
Una sola definición, un solo grafo de recursos»*.

**2. Planificar ese root traería servicios fuera de Task/030.** El grafo crea, además del
bucket: parámetros SSM y grupo de logs de CloudWatch —**Task/031**, y su retención es
**D-11**, todavía abierta—, la función Lambda —**Task/032**, que además exige
`lambda_zip_path`, el artefacto de `Task/024`— y la HTTP API —**Task/033**, cuyo
`nombre_del_stage` sigue sin decidir—. STAGE-10 lo confirma: la red y RDS de `Task/031` van
*«en el mismo grafo»*. Cualquiera de esos recursos **dispara la parada obligatoria** que el
propio checkpoint fijó: *«servicio fuera de Task/030»*.

**3. `-target` está prohibido** por el runbook del bootstrap: *«No usar `-target`,
`-replace`, import, operaciones `terraform state` ni flags de desbloqueo para sortear un
fallo»*. Es la única vía que Terraform ofrece para planificar un subconjunto de un root, y
no está disponible.

**4. El lanzador rechaza `production`, y además declara no haberlo implementado.**
`scripts/laboratorio/destino.py` lanza `ErrorDeDestino` dos veces: primero *«el modo
'production' esta rechazado: no existe autorizacion …»* y, **aunque se autorizara**,
*«el modo 'production' no esta implementado en este lanzador»*. Y `escribir_backend` en
`scripts/laboratorio/laboratorio.py` emite **siempre** `backend "local" {}`, para cualquier
modo. El grafo de aplicación, por tanto, **no puede inicializarse contra AWS real con las
herramientas del proyecto**, y no existe key de backend remoto decidida para su state: el
runbook reserva ese punto —*«Aplicación: se fijará en su checkpoint; nunca una de las dos
keys de bootstrap»*—.

**5. Dos gaps menores del propio módulo, medidos.** `modulos/almacenamiento` **no acepta ni
aplica etiquetas**: la variable `etiquetas` existe en el root y **no se usa en ningún
módulo**, así que el requisito de *tags* del checkpoint no es configurable, exige tocar
código. Y el grafo de aplicación **no tiene ningún `*.tftest.hcl`**, de modo que el gate
`terraform test` no puede ejercerse sobre él —los bootstrap sí los tienen y siguen en verde,
9/9 y 5/5—.

### 21.2. Lo que sí quedó verificado

El módulo existente **ya cumple** las decisiones del MVP sin cambiarlo: bucket privado,
`BucketOwnerEnforced`, BPA con las cuatro flags explícitas, versionado, SSE-S3 `AES256`,
policy que **niega** transporte no TLS, *lifecycle* con `noncurrent_version_expiration`
parametrizable y `abort_incomplete_multipart_upload` fijo en **7 días**, y **CORS
condicional que no crea el recurso cuando la lista está vacía** —que es precisamente el
valor decidido—. `forzar_destruccion` se deriva de `var.laboratorio`, así que con
`laboratorio = false` ya vale `false`.

El **IAM mínimo** también está escrito y se verificó contra el código real:
`s3:GetObject`, `s3:PutObject` y `s3:DeleteObject` acotados a
`<arn-del-bucket>/<prefijo-de-medios>*`, y un **único** `s3:ListBucket` **condicionado** a
`s3:prefix` del prefijo de la sonda. Esa condición está justificada: `comprobar_disponibilidad`
ejecuta `list_objects_v2(Bucket, Prefix="_readiness/", MaxKeys=1)` —constante
`PREFIJO_DE_LA_SONDA` en `app/shared/storage/s3_compatible.py`—, no `HeadBucket`. Sin la
condición habría que permitir enumerar el bucket entero. **No hay `ListBucket` sin acotar**,
y la ausencia de `listar` en el puerto `ObjectStorage` es lo que lo hace innecesario.

**Gates locales, todos verdes:** `fmt` en los tres roots; `init -backend=false` y `validate`
del grafo de aplicación en **exit 0**; `terraform test` **9/9** y **5/5** en los bootstrap;
`tests/oidc` 60 con 1 omitida, `tests/terraform_state` 12, `tests/laboratorio` 176 y
`tests/security` 88, todas OK; provider locks versionados intactos; `git diff --check`
limpio; **Gitleaks 8.30.1 sobre 279 archivos, 0 hallazgos**; 1866 enlaces relativos sin
roturas reales; sin Account ID ni secretos en el entregable.

**H-030-2 sin regresión:** STS correcto; `bootstrap/terraform-state` en
`pjvyHqNzxTObDUSOcwVbuXSwAD3I4RM2` con 12 864 bytes y `bootstrap/github-oidc` en
`Dl7AxGe7qj28P703ZFJwh_qsRzY2ViHI` con 5 840; ambas `.tflock` ausentes; **dos** keys en el
bucket; el rol de validación con cero políticas; y **un solo bucket en la cuenta**.

### 21.3. Vías de recuperación, ninguna ejecutada

| Vía | Qué implicaría | Coste de diseño |
| --- | --- | --- |
| **A. Root propio para el bucket de medios**, reutilizando `./modulos/almacenamiento` por `source` y con su propia key de state | Es el patrón ya probado con los dos bootstrap. **No duplica el módulo**, pero sí crea un **segundo root**, y habría que retirar `module.almacenamiento` del grafo de aplicación y pasar a consumir su nombre/ARN por `terraform_remote_state` o variable, para que dos roots no reclamen el mismo bucket | Modifica el entregable de `Task/025` y su regla de grafo único |
| **B. Implementar el modo `production` del lanzador** y planificar el grafo completo | Desbloquea el camino oficial, pero arrastra `Task/031`, `Task/032` y `Task/033` a `Task/030`: SSM, CloudWatch con D-11 abierta, Lambda con su ZIP, API con su stage, VPC por ADR-010 | Rompe las fronteras de tarea y el alcance autorizado |
| **C. Aceptar que H-030-3 no aplica en `Task/030`** | `Task/030` cierra con D-06 materializado, D-08 resuelta y el diseño del bucket validado **offline**; el `apply` del bucket se traslada a la tarea que primero disponga del grafo completo | Cambia el alcance declarado de `Task/030` y traslada la validación real de `S3Storage` |
| **D. `-target`** | — | **Descartada**: prohibida por el runbook |

**Recomendación técnica: A**, por ser la única que respeta las fronteras de tarea y ya tiene
precedente funcionando en este mismo repositorio; su coste es una enmienda explícita al
diseño de `Task/025`, que debe decidirse, no deducirse.

**Parada H-030-4.** Sin plan real, sin `apply`, sin bucket, sin IAM nuevo, sin servicios de
otras tareas y sin tocar el bootstrap ni su state. D-08 queda **Resuelta para el MVP** y
`B-016-1` **abierto**. Task/030 sigue **En progreso**, sin commit, push, PR ni merge.

## 22. H-030-4-root-medios y H-030-3 — ENMIENDA APLICADA Y PLAN REAL LISTO

Autorización exacta: `authorize: Task/030 H-030-4-root-medios`, vía **A**. El bloqueo de §21
queda resuelto: el almacenamiento de medios sale del *lifecycle* y del state del grafo de
aplicación y pasa a un **root propio** que **reutiliza** el módulo de `Task/025`.

### 22.1. La enmienda, y qué significa ahora la regla de paridad

La regla de §4.1 de [aws-local-parity](../architecture/aws-local-parity.md) —«un solo grafo de
recursos»— se había leído como «un solo **root**». `Task/030` demostró que esa lectura era
demasiado estrecha. Queda **precisada** en su nueva §4.1.1, y en la **AWS LOCAL PARITY LAW**
de `PROJECT_INSTRUCTIONS` §15:

1. **Una sola definición** de cada recurso y de cada módulo.
2. **La misma topología de roots en local y en AWS real.**
3. **Varios roots son legítimos** cuando representan *lifecycles* y *state ownership* distintos.
4. **Ningún recurso queda administrado por dos states.**
5. **El almacenamiento es el primer *lifecycle* extraído**, por ser persistente.
6. **El grafo de aplicación consume por contrato explícito** lo que no administra: variables,
   **no** `terraform_remote_state`.

**La historia no se reescribe.** `Task/025` decidió un único root y un único state con un
razonamiento correcto para lo que existía entonces —evitar dos IaC divergentes—, y su
`main.tf` original, su reporte y su ficha se conservan intactos. **R-26 no se relaja**: sigue
vigilando la acumulación de condicionales por entorno, que es otra cosa; separar *state
ownership* no introduce ningún condicional por destino.

### 22.2. Roots y propiedad, medidos

| Root | State | Módulos que instancia | Propiedad |
| --- | --- | --- | --- |
| `terraform/` | propio | `api_http`, `computo`, `identidad`, `parametros`, `registro` | Lambda, API, SSM, logs y rol. **No** el bucket |
| `terraform-medios/` | propio | `almacenamiento` | **El bucket de medios, en exclusiva** |
| `bootstrap/terraform-state/` | propio | — | Bucket de state y BPA de cuenta |
| `bootstrap/github-oidc/` | propio | — | Proveedor OIDC y rol de validación |

Comprobado, no supuesto:

- **Una sola definición**: `resource "aws_s3_*"` del bucket de medios existe únicamente en
  `terraform/modulos/almacenamiento/main.tf`, y ese módulo lo referencia **un solo** root,
  `terraform-medios/main.tf`, por `source = "../terraform/modulos/almacenamiento"`.
- **El root de aplicación no puede crearlo**: `module "almacenamiento"` aparece **0 veces** en
  él, y su manifiesto de módulos tras un `init` limpio lista exactamente `api_http`, `computo`,
  `identidad`, `parametros` y `registro`. Excluyendo el módulo compartido, sus tipos de
  recurso no contienen ningún `aws_s3_*`.
- **Contrato explícito**: recibe `nombre_del_bucket_de_medios` y `arn_del_bucket_de_medios`, y
  `module.identidad` consume `var.arn_del_bucket_de_medios`. **No existe ningún
  `data "terraform_remote_state"`** en ningún root: los tres hits del grep son comentarios que
  explican por qué no se usa.
- **Matiz declarado**: el módulo sigue viviendo físicamente bajo `terraform/`, así que un
  barrido por directorio lo cuenta ahí. No lo instancia: Terraform solo crea los módulos que
  un root llama. Se deja escrito para que nadie lo lea como doble propiedad.

### 22.3. Paridad local

El laboratorio usa **el mismo root y el mismo módulo** que producción; lo único que cambia son
los valores del destino. Se rechazó explícitamente la variante «en local el bucket va dentro
del grafo de aplicación», que es la divergencia que la regla prohíbe.

La orquestación de `scripts/laboratorio/laboratorio.py` pasa a dos roots con un descriptor
`RootDeTerraform`, y el orden es el de las dependencias: **medios primero** —porque el grafo
de aplicación recibe su nombre y su ARN—, se leen sus salidas, se inyectan en el tfvars
generado del grafo y después continúa el ciclo. La destrucción va en **orden inverso**.
Cada root recibe su **propio subdirectorio de estado**, que es lo que impide compartir archivo
de state. Las salidas del root de medios viajan por el tfvars generado, igual que
`lambda_zip_path`, y no con `-var` en cada invocación.

**Límite declarado sin adornos:** el lanzador compila, sus **176 pruebas** siguen en verde y
la secuencia está escrita, pero **no se ha ejecutado un ciclo real del laboratorio** en esta
enmienda: exige Docker, Floci y el ciclo completo, que es una operación aparte. La paridad
queda **preservada por construcción y por pruebas unitarias**, **no demostrada por un ciclo**.
Ejecutarlo es requisito antes de volver a confiar en el laboratorio.

### 22.4. Gates locales

| Gate | Resultado |
| --- | --- |
| `fmt -check -recursive` | **OK** en los cuatro roots |
| `validate` | OK en `terraform` y en `terraform-medios` |
| `terraform test` | `terraform-medios` **7/7**, `bootstrap/github-oidc` **9/9**, `bootstrap/terraform-state` **5/5** |
| `init -backend=false -lockfile=readonly` | OK en los dos roots de aplicación/medios |
| Provider lock del root nuevo | `hashicorp/aws 6.64.0`, constraint exacta, **2 hashes h1** y 16 `zh`, **byte a byte idéntico** a los otros tres |
| Suites Python | `laboratorio` **176**, `oidc` **60** (1 omitida), `terraform_state` **12**, `security` **88** — todas OK |
| Scripts Python | 18 compilan, 0 fallos |
| `git diff --check` | limpio |
| Gitleaks 8.30.1 | **289** archivos versionables, **0 hallazgos** |
| Enlaces | 1868 destinos relativos, **0 roturas reales** (6 avisos conocidos: ejemplos Markdown en *code spans* de archivos no tocados) |
| Account ID / credenciales en el entregable | ninguno |

No existe ningún `review_gates` en este repositorio; los gates ejercidos son los que el CI
ejecuta de verdad más los añadidos por esta tarea.

Las pruebas del root nuevo demuestran **offline**: BPA con las cuatro flags,
`BucketOwnerEnforced`, versionado `Enabled`, SSE-S3 `AES256`, policy con **un solo** `Deny` de
transporte no TLS, *lifecycle* 30/7, **CORS ausente con la lista vacía** y presente con una
lista no vacía, comodín CORS rechazado, región no comercial rechazada, nombre de bucket
inválido rechazado, expiración menor que un día rechazada, `force_destroy=false` en
producción, **tags** y las dos salidas de contrato. Más un caso que ejerce el destino
**laboratorio** contra el mismo módulo.

### 22.5. Backend remoto del root de medios

Key dedicada **`application/media/terraform.tfstate`**, en el bucket de state ya existente,
`us-east-2`, `encrypt=true`, `use_lockfile=true`, perfil humano, **sin DynamoDB y sin KMS**.
**No reutiliza ninguna key de bootstrap.**

Antes del `init`: identidad `assumed-role/PersonalBlogAdministrator/personal-blog-entry-admin`;
la key y su `.tflock` **ausentes (404)**; los dos states de bootstrap intactos y sin lock; el
bucket de state con exactamente dos claves.

El `init` terminó en **exit 0**, resolvió el módulo compartido
(`almacenamiento in ..\terraform\modulos\almacenamiento`), **no pidió migración** —no había
origen que copiar— y, verificado después, **no creó el objeto de state ni ningún lock**.

Nombre del bucket de medios: **`personal-blog-medios-us-east-2-2ee5dbd5dc68`**, 43
caracteres. Sufijo determinístico de 12 hex de SHA-256 sobre
`personal-blog:medios:<cuenta>:us-east-2`, la misma convención del bucket de state: sin
aleatoriedad, reproducible y **sin revelar la cuenta**. `HeadBucket` previo dio **404**: libre
y sin colisión. Ese 404 no reserva el nombre.

El tfvars operativo vive **fuera de Git**, en el directorio privado del operador, con la
cuenta verificada, y su plantilla versionada no lleva ningún valor real.

### 22.6. Plan real — H-030-3

```text
terraform -chdir=terraform-medios plan -input=false -no-color -lock=true -lock-timeout=30s
  -detailed-exitcode -var-file=<privado>/produccion.tfvars.json -out=<privado>/h0303-medios-<ts>.tfplan
```

Inicio `2026-09-29T01:06:07.925051+00:00`; fin `2026-09-29T01:06:19.915792+00:00`;
`-detailed-exitcode` = **2**, que es lo que corresponde a una creación.

| Gate | Resultado |
| --- | --- |
| add / change / destroy | **7 / 0 / 0** |
| `resource_drift` | **0** |
| Replacements, `replace_paths`, imports, moves | **0 / 0 / 0 / 0** |
| `deferred_changes`, `action_invocations` | **0 / 0** |
| `errored` / `complete` / `applyable` | `false` / `true` / `true` |
| Outputs | dos, ambos `create`, no sensibles |
| Tipos de recurso | **los siete son `aws_s3_*`**; cero tipos no-S3 |
| Servicios fuera de alcance | **ninguno**: sin IAM, SSM, CloudWatch, Lambda, API Gateway, VPC, RDS, NAT, CloudFront ni KMS |
| `aws_s3_bucket_cors_configuration` | **ausente**, como exige `origenes_cors = []` |

Los siete recursos, todos bajo `module.almacenamiento`: `aws_s3_bucket.medios`,
`aws_s3_bucket_ownership_controls.medios`, `aws_s3_bucket_public_access_block.medios`,
`aws_s3_bucket_versioning.medios`,
`aws_s3_bucket_server_side_encryption_configuration.medios`, `aws_s3_bucket_policy.medios` y
`aws_s3_bucket_lifecycle_configuration.medios`.

El módulo define **ocho** recursos y el plan crea **siete**: el octavo es la configuración
CORS, que no se crea con la lista vacía. La diferencia está explicada, no es un hallazgo.

Configuración planificada:

| Aspecto | Valor |
| --- | --- |
| Bucket | `personal-blog-medios-us-east-2-2ee5dbd5dc68` |
| `force_destroy` | **false** |
| Tags | `Proyecto=personal-blog`, `Entorno=produccion`, `Gestion=terraform`, `Componente=medios`, `Tarea=Task/030` |
| BPA | las **cuatro** flags en `true` |
| Ownership | `BucketOwnerEnforced` |
| Versionado | `Enabled` |
| Cifrado | **SSE-S3 `AES256`**, `kms_master_key_id` nulo |
| Policy | **desconocida en plan** por interpolar el ARN del bucket, que aún no existe. Su fuente es un **único `Deny`** de `s3:*` con `aws:SecureTransport=false`, sin ningún `Allow`, y así lo fija la prueba offline |
| Lifecycle | `expirar-versiones-antiguas`, `Enabled`; versiones no actuales **30 días**; multipart abortado a **7 días**; **sin** expiración de objetos actuales y **sin** transiciones |

| Artefacto privado | SHA-256 |
| --- | --- |
| Plan binario | `3422d7f302c935598aa8f326aafe6097851e768fc2fd777fb02d12eb88284bba` |
| JSON del plan | `26e1f31be744dd3adbe9b9653a167522be3f47cf2d7969ede40622ea35e9b8d4` |
| Log del plan | `9b2bb8aa0c4f8d2d63dc1d3db96611ad0beadfd3e0f06a2f8754b0d7195f342d` |

### 22.7. Nada se aplicó

Verificado después del plan: la key `application/media/terraform.tfstate` y su `.tflock`
siguen **ausentes**; el único ciclo de lock de esa key está **cerrado**, una versión y un
delete marker; los dos states de bootstrap conservan VersionId, longitud y `LastModified`; la
cuenta sigue con **un solo bucket**, el de state, y `HeadBucket` del bucket de medios devuelve
**404**; IAM sin cambios, con cinco roles —tres de servicio de AWS, el humano y el de
validación con cero políticas— y **ningún rol de ejecución**, así que `Task/032` no se ha
adelantado.

**Coste estimado** del bucket de medios, escenario holgado —1 GB, 2.000 PUT, 50.000 GET, 5 GB
de egress—: **entre 0,05 y 0,50 USD/mes** según quede o no franquicia de los 100 GB globales.
**Cero coste fijo nuevo.** Dentro del sublímite de D-13.

**H-030-3 — READY FOR APPLY.** El apply exige autorización humana explícita y no se ejecuta
aquí. Task/030 sigue **En progreso**, sin commit, push, PR ni merge.

## 23. H-030-3 — APPLY EJECUTADO, y parada H-030-4 por `resource_drift = 1`

Autorización exacta: `authorize: Task/030 H-030-3`. Se aplicó **solo** el plan guardado y
aprobado. El apply salió limpio y el readback AWS es correcto en sus diez puntos, pero el
plan de convergencia posterior devolvió **`resource_drift = 1`**, y la sección E del
checkpoint exige **0**. Se detiene ahí, antes de F.

### 23.1. Preflight, retomado tras la renovación de sesión

El intento anterior se paró en A.3: la sesión AWS había expirado. Nada se mutó entonces.
Tras la renovación humana, medido de nuevo:

| Comprobación | Resultado |
| --- | --- |
| Rama / commits | `Task/030-Desplegar-Amazon-S3`, **0** commits sobre `main`, `HEAD == main == origin/main` |
| Backend / frontend | limpios en `main` |
| Procesos Terraform / `.lock.info` | **0 / 0** |
| STS | `assumed-role/PersonalBlogAdministrator/personal-blog-entry-admin`, us-east-2 |
| Bucket de medios | **no existía** (404) |
| `application/media/terraform.tfstate` y su `.tflock` | **ausentes** (404) |
| Bootstrap | `pjvyHqNzxTObDUSOcwVbuXSwAD3I4RM2`/12 864 y `Dl7AxGe7qj28P703ZFJwh_qsRzY2ViHI`/5 840, sin locks |
| BPA de cuenta (H-030-1) | las **cuatro** flags en `true` |
| SHA-256 del plan guardado | `3422d7f3…88284bba`, **idéntico** al de §22, recalculado justo antes |
| Contenido del plan, releído del binario | **12/12 gates PASS**: 7/0/0, drift 0, sin replacements, imports ni moves, solo `aws_s3_*`, sin CORS |

Ninguna configuración Terraform cambió después de crearse el plan: su `mtime` es `01:06:19Z`
y el archivo de configuración más reciente es anterior.

### 23.2. Apply

```text
terraform -chdir=terraform-medios apply -input=false -no-color -lock=true -lock-timeout=30s
  <privado>/h0303-medios-20260929T010559Z.tfplan
```

Inicio `2026-09-29T01:24:44.985622+00:00`; fin `2026-09-29T01:25:56.055508+00:00`;
**exit 0**, **cero warnings**. Sin `-target`, sin `-replace`, sin regenerar el plan, sin
`import` y sin operaciones `state`.

**`Apply complete! Resources: 7 added, 0 changed, 0 destroyed.`**

Outputs publicados: `nombre_del_bucket` y
`arn_del_bucket = arn:aws:s3:::personal-blog-medios-us-east-2-2ee5dbd5dc68`.
El `lifecycle_configuration` tardó 57 s en converger, que es el comportamiento normal de esa
API de S3.

Log del apply: SHA-256 `096336dc23893d587eac4c365e6b7c8ecf5d3c05eab3df65fd653a26b86ce015`.

### 23.3. State remoto de medios

| Comprobación | Resultado |
| --- | --- |
| Objeto | existe: VersionId `afWaujpRxNG_H57C1sDSvDIQf8YmgtCO`, 12 707 bytes, **AES256** |
| `.tflock` final | **ausente (404)**; dos ciclos —plan y apply—, **2 versiones y 2 delete markers**, emparejados |
| Backend efectivo | `s3`, key `application/media/terraform.tfstate`, us-east-2, `encrypt=true`, `use_lockfile=true`, **sin DynamoDB y sin KMS** |
| Recursos administrados | **exactamente 7**, todos `module.almacenamiento.aws_s3_*`; **0** data sources; **cero** tipos no-S3 |
| Outputs | `nombre_del_bucket` y `arn_del_bucket` |
| Metadata | lineage `60fff430-…`, serial **2**, Terraform 1.16.2. SHA-256 `6fca00bf…5517486` |
| Bootstrap | los dos states con VersionId, longitud y `LastModified` **idénticos**: intactos |

Las dos keys de bootstrap **no se tocaron** en ningún momento.

### 23.4. Readback AWS del bucket — diez de diez

| # | Comprobación | Observado |
| --- | --- | --- |
| 1 | Existe y región | `HeadBucket` 200; `LocationConstraint` **us-east-2** |
| 2 | `force_destroy` | **false** en el state |
| 3 | Block Public Access del bucket | `BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, `RestrictPublicBuckets` = **true** |
| 4 | Object Ownership | **`BucketOwnerEnforced`**; ACL con un único grant `FULL_CONTROL` al dueño |
| 5 | Versionado | **`Enabled`** |
| 6 | Cifrado | **SSE-S3 `AES256`**, sin KMS. AWS añade `BucketKeyEnabled=false` y bloquea `SSE-C`, ambos por omisión del servicio |
| 7 | Policy | **un solo statement**: `NegarTransporteInseguro`, `Deny`, `s3:*`, `Condition Bool aws:SecureTransport=false`. **Ningún `Allow`**, y `PolicyStatus.IsPublic = False` |
| 8 | Lifecycle | `expirar-versiones-antiguas`, `Enabled`, `NoncurrentDays 30`, `AbortIncompleteMultipartUpload 7`, **sin** `Expiration` de objetos actuales y sin transiciones |
| 9 | CORS | **ausente**: `NoSuchCORSConfiguration`, como exige `origenes_cors = []` |
| 10 | Tags | los cinco exactos: `Proyecto`, `Entorno`, `Gestion`, `Componente`, `Tarea` |

El **BPA de cuenta** de H-030-1 sigue con sus cuatro flags en `true`.

### 23.5. Plan de convergencia: converge en infraestructura, pero `resource_drift = 1`

`-detailed-exitcode` = **0**, «No changes», **0 add / 0 change / 0 destroy**, los **siete**
recursos `no-op`, outputs `no-op`, `applyable=false`, `errored=false`, **cero warnings**, el
state **no se reescribió** —mismo VersionId— y el `.tflock` quedó ausente.

Pero `resource_drift = 1`, y la sección E exige `0`. **Se detiene como H-030-4.**

**Diagnóstico, con el patrón ya conocido de este proyecto.** El drift es una sola entrada,
`module.almacenamiento.aws_s3_bucket.medios`, y afecta a **tres atributos espejo obsoletos**
del recurso `aws_s3_bucket`:

| Atributo espejo | En el state | Observado en AWS | Quién es la fuente de verdad |
| --- | --- | --- | --- |
| `versioning[0].enabled` | `false` | `true` | `aws_s3_bucket_versioning.medios` |
| `policy` | `""` | la policy de deny TLS | `aws_s3_bucket_policy.medios` |
| `lifecycle_rule` | `[]` | la regla 30/7 | `aws_s3_bucket_lifecycle_configuration.medios` |

**Causa exacta**: el bucket se crea primero, y su entrada de state se escribe **antes** de que
existan sus recursos hermanos. Cuando el refresh pregunta a AWS, esos tres atributos —que el
provider conserva por compatibilidad y que los recursos separados han sustituido— ya reportan
el valor real, así que dejan de coincidir con lo almacenado. Los tres recursos que de verdad
configuran esas propiedades **están en el state** y el plan los deja `no-op`.

Es **el mismo patrón** que §13.3 y §14.2 documentaron para el bucket de state, donde afectó a
`policy`, `versioning` y `tags`; aquí `tags` no aparece porque se declaran explícitamente en
el recurso, y en cambio aparece `lifecycle_rule`, que ese bootstrap no tiene.

**No es drift de infraestructura.** AWS tiene exactamente lo que el código pide: el readback
de §23.4 lo confirma punto por punto. Es una diferencia de **metadata del state**.

### 23.6. Plan refresh-only preparado, NO aplicado

Siguiendo el precedente de H-030-4-refresh-apply, se generó un plan **refresh-only** para
revisión humana. **No se aplicó.**

| Gate | Resultado |
| --- | --- |
| `-detailed-exitcode` | **2**: propone actualizar el state |
| Cambios de **infraestructura** | **0 add / 0 change / 0 destroy** |
| `resource_drift` que reconciliaría | **1**, exactamente `aws_s3_bucket.medios`, campos `lifecycle_rule`, `policy`, `versioning` |
| `applyable` / `errored` | `true` / `false` |
| State escrito por este plan | **No**: mismo VersionId |
| `.tflock` tras el plan | **ausente** |

| Artefacto privado | SHA-256 |
| --- | --- |
| Plan refresh-only | `07b4629f17ba1b4289fa227f552e183283ca45d387b0309adc6a51bf346b0f8e` |
| JSON del refresh-only | `3dd6ba95a10a780dad9666a5db03d6d471aec4dd7ab1c0bc1f221675d843db9d` |
| Plan de convergencia | `45b2d9c24358d0484f16db1001a7dde8a2e46b3f0e928067389bb831b43c3559` |
| JSON de convergencia | `dbace955d543684a90d83b148d07e8dc31f743be9a5415cf4b6b86004c573e4f` |

### 23.7. Lo que NO se ejecutó

**Parada H-030-4** antes de la sección F. No se ejecutaron: la prueba real de `S3Storage`, la
limpieza de objetos de prueba —no se creó ninguno—, el ciclo del laboratorio, los gates
finales ni el cierre documental de Task/030.

No se creó ningún rol de ejecución Lambda: `Task/032` sigue sin adelantarse, y el rol de
validación OIDC conserva cero políticas. `Task/031` y `Task/033` no se iniciaron. **D-08**
permanece **Resuelta (MVP)** y **`B-016-1` abierto**. Sin commit, push, PR ni merge.

**Estado real de la infraestructura**: el bucket de medios **existe y está correctamente
configurado**; su state remoto es operativo; la única cuestión abierta es la reconciliación de
esos tres atributos espejo en el state, que requiere autorización humana explícita para
aplicar el binario refresh-only ya revisado.

## 24. H-030-4-refresh-media-state aplicado, y DEF-030-1: las prefirmadas no funcionan contra AWS real

Autorización exacta: `authorize: Task/030 H-030-4-refresh-media-state`. El refresh-only se
aplicó y la convergencia quedó limpia. Después, la validación funcional de `S3Storage` contra
el bucket real **encontró un defecto bloqueante del adaptador**, ajeno a la infraestructura.
Se detiene en F y **no se declara Task/030 lista para aprobación**.

### 24.1. Refresh-only del state

Preflight: rama y Git correctos, backend/frontend limpios, STS
`assumed-role/PersonalBlogAdministrator/personal-blog-entry-admin`, `.tflock` ausente,
readback del bucket correcto, y SHA-256 del binario recalculado
`07b4629f17ba1b4289fa227f552e183283ca45d387b0309adc6a51bf346b0f8e`, **idéntico al
autorizado**. Relectura del binario: **10/10 gates** —refresh-only, infraestructura 0/0/0, una
sola entrada de drift en `aws_s3_bucket.medios`, únicamente `lifecycle_rule`, `policy` y
`versioning`, sin imports, moves ni replacements—.

Apply `2026-09-29T01:35:47.918512+00:00` → `01:35:55.098471+00:00`, **exit 0**:
**`0 added, 0 changed, 0 destroyed`**. Nueva versión del state
`G9iYVw9i9h15VNedSmrhl1EgwkibKz39`, 13 558 bytes, AES256; `.tflock` ausente.
Log: SHA-256 `dab795eea5b7493debc5ed27bd2339336aa67565b970fc0f711bf18c48d9c68a`.

**Convergencia obligatoria, lograda**: exit **0**, **0/0/0**, **`resource_drift = 0`**, los
**siete** recursos no-op, outputs no-op, `applyable=false`, 0 replacements/imports/moves,
**0 warnings**, el state no se reescribió y el `.tflock` quedó ausente. El readback confirmó
que el refresh-only **no alteró nada** en AWS: BPA, ownership, versionado, cifrado, policy,
lifecycle, CORS y tags idénticos.

### 24.2. `S3Storage` real: nueve de trece comprobaciones, y un defecto

Prueba ejecutada con la **identidad humana** `personal-blog` como operador, contra el bucket
real, con objetos bajo el prefijo inequívoco `_task030-prueba-<sello>/`. El adaptador se
importó **sin modificar el backend** y sin claves explícitas: las credenciales llegaron por la
**cadena por defecto de boto3**, que es el camino de producción.

| Comprobación | Resultado |
| --- | --- |
| `comprobar_disponibilidad` | **OK** — retorna sin valor; el almacenamiento es utilizable |
| `guardar` | **OK** — clave, 67 bytes y `image/png` correctos |
| `existe` tras guardar | **OK** — `True` |
| `obtener`, bytes exactos | **OK** — byte a byte |
| `obtener`, `Content-Type` | **OK** — `image/png` |
| **GET con URL prefirmada** | **FALLA — HTTP 403 `SignatureDoesNotMatch`** |
| GET **sin firma** sobre objeto privado | **OK** — HTTP **403 Forbidden**: el objeto no es público |
| Prefirmada de TTL corto, antes de expirar | **FALLA** — por la misma causa que la anterior |
| Prefirmada de TTL corto, después de 8 s | **OK** — HTTP 403 |
| `eliminar` → `existe` | **OK** — `False` |
| `eliminar` → `obtener` | **OK** — `ObjetoNoEncontradoError` |
| `eliminar` idempotente | **OK** — el segundo no lanza |
| Objeto borrado inaccesible | **Inconcluso** — devolvió 403 y no 404, por la misma firma inválida. **No es un hallazgo de seguridad** |

Los tres resultados no verdes tienen **una sola causa raíz**, y no es el bucket.

### 24.3. DEF-030-1 — causa raíz, aislada y reproducible

**Síntoma.** `acceso_temporal` emite una URL cuyo host es
`<bucket>.s3.amazonaws.com` —el endpoint **global**— mientras la firma tiene alcance
`us-east-2`. S3 responde **403 `SignatureDoesNotMatch`**, y su cuerpo confirma que el
`CanonicalRequest` que recibe no es el que se firmó.

**Causa.** `AlmacenamientoCompatibleS3._construir_cliente` declara `addressing_style`
**solo** cuando hay `endpoint_url`. Contra AWS real no lo hay, así que no se declara ninguno,
y **botocore 1.43.82 construye el host global** al generar la prefirmada aunque el
`endpoint_url` resuelto del cliente sea el regional correcto.

**Aislamiento, medido en el mismo entorno y contra el mismo objeto:**

| Variante | Host de la prefirmada | Resultado |
| --- | --- | --- |
| Adaptador tal cual (sin `addressing_style`, sin endpoint) | `<bucket>.s3.amazonaws.com` | **403 SignatureDoesNotMatch** |
| `boto3.client("s3", region_name="us-east-2")` **sin `Config`** | `<bucket>.s3.amazonaws.com` | igual de roto |
| `Config(signature_version="s3v4")` a secas | `<bucket>.s3.amazonaws.com` | igual de roto |
| `Config(s3={"addressing_style": "virtual"})` | `<bucket>.s3.us-east-2.amazonaws.com` | **HTTP 200** |
| `Config(s3={"addressing_style": "path"})` | `s3.us-east-2.amazonaws.com` | **HTTP 200** |
| `endpoint_url` regional explícito, vía `access_endpoint_url` del adaptador | `s3.us-east-2.amazonaws.com` | **HTTP 200** |
| **AWS CLI** `s3 presign` | `<bucket>.s3.us-east-2.amazonaws.com` | **HTTP 200** |

El cliente del adaptador resuelve `endpoint_url = https://s3.us-east-2.amazonaws.com` y
`region_name = us-east-2`: la configuración del proyecto es correcta. El host global lo
introduce la generación de la prefirmada cuando el estilo de direccionamiento queda sin
declarar. No hay nada en `~/.aws/config` ni en el entorno que lo fuerce: solo `region` y la
sesión del perfil.

**Impacto.** El mecanismo que D-08 fijó para el MVP —**presigned GET dinámico para borrador y
publicado**— **no funciona contra AWS real** con el adaptador actual. Es exactamente lo que
STAGE-10 encarga a `Task/030` comprobar, y es la razón por la que un plan verde y un bucket
correcto no bastan como evidencia.

**Lo que el defecto NO es.** No es un problema del bucket: su readback es correcto en los diez
puntos. No es una fuga de seguridad: el objeto privado devolvió **403 sin firma**, que es el
comportamiento deseado. No es un fallo de la enmienda de roots ni del state.

**Arreglo previsible y por qué no se aplica aquí.** Una línea en
`app/shared/storage/s3_compatible.py`: declarar el estilo de direccionamiento también cuando
no hay `endpoint_url`. Pero eso es **código del backend**, que la ficha de `Task/030` excluye
expresamente de su alcance, y es **comportamiento funcional**, de modo que entra íntegro en la
**BACKEND TEST-FIRST LAW**: matriz de comportamiento, RED demostrado —que aquí ya existe, en
forma de 403 real—, GREEN mínimo, refactor y regresión completa, más una prueba que habría
cazado esto. No se parchea sobre la marcha.

### 24.4. Limpieza, completada

El inventario con versiones y delete markers listó **7 artefactos**, todos bajo prefijos
`_task030-` y **ninguno ajeno**. Se eliminaron los **7** —3 versiones y 4 delete markers— y el
bucket quedó **sin ninguna versión y sin ningún delete marker**: completamente vacío.

Nota de método: un primer bucle de borrado reportó fallos falsos porque la CLI consumía el
`stdin` del propio bucle; se resolvió con una única llamada `delete-objects`, que devolvió
**6 eliminados y 0 errores** sobre lo que quedaba.

Tras la limpieza, readback de nuevo: BPA con las cuatro flags, `BucketOwnerEnforced`,
versionado `Enabled`, `AES256`, `IsPublic=False`, lifecycle 30/7, CORS ausente y los cinco
tags. **Convergencia otra vez 0/0/0 con `resource_drift = 0`**, siete no-op,
`applyable=false`, sin lock.

### 24.5. Frontera IAM, respetada

**No se creó ningún rol de ejecución Lambda.** La cuenta conserva cinco roles: tres de
servicio de AWS, el humano `PersonalBlogAdministrator` y `PersonalBlogGitHubOidcValidation`
con **cero políticas gestionadas y cero inline**. `Task/032` no se adelanta.

El contrato de mínimo privilegio previsto sigue **validado solo offline**:
`s3:GetObject`, `s3:PutObject` y `s3:DeleteObject` acotados a `medios/*`, y `s3:ListBucket`
**condicionado** al prefijo de la sonda. La validación funcional de esta sección se hizo con
el **operador humano**, de modo que **no** acredita ese mínimo privilegio: su *enforcement*
real es gate de `Task/032`. Esa separación es deliberada y no es un fallo de `Task/030`.

### 24.6. Parada

No se ejecutaron: el ciclo real del laboratorio (I), los gates finales (J) ni el cierre
documental de `Task/030` (K). **No se declara `Task/030 — READY FOR FINAL APPROVAL`**: la
tarea tiene como criterio explícito que `S3Storage` funcione contra S3 real, y hoy no
funciona por **DEF-030-1**.

Estado real: el **bucket de medios está creado, correcto y convergente**; su state remoto es
operativo y reconciliado; los dos states de bootstrap intactos; D-08 sigue **Resuelta (MVP)**
y `B-016-1` **abierto**; `Task/031` y `Task/033` sin iniciar. Sin commit, push, PR ni merge.

**Decisión humana requerida:** ampliar el alcance de `Task/030` para corregir el adaptador
bajo la ley test-first, o abrir una tarea propia para DEF-030-1 y cerrar `Task/030` declarando
el defecto como hallazgo con propietario.

## 25. DEF-030-1 corregido bajo la ley test-first

Autorización exacta: `authorize: Task/030 DEF-030-1-backend-fix`. Amplía el alcance de
`Task/030` de forma acotada para corregir **un solo defecto** del adaptador de almacenamiento,
sin features nuevas, sin cambios de API ni de modelo, sin CDN y sin adelantar `Task/031`,
`Task/032` ni `Task/033`. `D-08` no se modifica y `B-016-1` **sigue abierto**.

### 25.1. Rama del backend, creada desde `main` limpio

`personal-blog-backend` no tenía rama de esta tarea porque hasta ahora `Task/030` no tocaba
código. Se creó siguiendo el invariante crítico:

| Comprobación | Resultado |
| --- | --- |
| `git fetch --prune origin` | correcto |
| `main` al día con `origin/main` | `4a40364` en ambos |
| `git status --porcelain` antes de ramificar | vacío |
| Rama creada | `Task/030-Desplegar-Amazon-S3` |
| `HEAD` == `main` inmediatamente después | **coinciden** |
| Commits por delante de `main` al cerrar | **0** — sin commit, como exige el flujo |

La rama **nace de `main`**, nunca de `dev`.

### 25.2. Matriz de comportamiento, escrita antes de tocar el código

`BACKEND TEST-FIRST LAW` §14. El defecto es comportamiento funcional del adaptador, así que
entra íntegro en la ley: nada de parche primero y prueba después.

| # | Caso | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| 1 | Prefirmada contra AWS real | `endpoint_url` ausente, región `X` | el anfitrión **contiene** la región y **no** es el global `<bucket>.s3.amazonaws.com` | unitaria |
| 2 | Alcance de la firma | igual que 1 | `X-Amz-Algorithm` SigV4 y `X-Amz-Credential` con alcance de la región | unitaria |
| 3 | Objeto correcto | igual que 1 | la ruta apunta a la clave pedida | unitaria |
| 4 | MinIO | `endpoint_url` propio | **estilo por ruta** conservado; el bucket no se vuelve subdominio | unitaria |
| 5 | Endpoint compatible genérico | `endpoint_url` propio | estilo por ruta | unitaria |
| 6 | Endpoint de acceso propio | `access_endpoint_url` declarado | la firma se emite **contra él** | unitaria |
| 7 | Regresión completa | PostgreSQL y MinIO reales | ningún caso previo cambia | integración y contrato |

Los casos 1–3 son los que el defecto rompía. Los casos 4–6 son los que el arreglo **no debe
romper**: son la razón por la que el estilo no puede fijarse a `virtual` sin condición.

### 25.3. RED demostrado

Tests añadidos a `tests/unit/test_adaptadores_de_almacenamiento.py` y ejecutados **antes** del
arreglo. Fallaron **por la razón esperada**, no por un error de la prueba:

```
assert 'sa-east-1' in 'bucket-de-produccion.s3.amazonaws.com'
```

Tres fallos, uno por región parametrizada —`us-east-2`, `eu-west-1`, `sa-east-1`—: el anfitrión
generado era el **global** y no contenía la región en ninguno de los tres casos. El RED
coincide exactamente con el 403 `SignatureDoesNotMatch` medido contra AWS real en §24.3, que ya
era, de hecho, un RED de producción.

### 25.4. GREEN mínimo

Un solo cambio de comportamiento en `app/shared/storage/s3.py`, en `_construir_cliente`:

```python
estilo = "path" if endpoint_url is not None else "virtual"
opciones: dict[str, object] = {
    "signature_version": "s3v4",
    "s3": {"addressing_style": estilo},
}
```

Antes, la clave `s3` se añadía **solo** cuando había `endpoint_url`. Contra AWS real no hay
endpoint, así que el estilo quedaba sin declarar y `botocore` construía el anfitrión heredado
global al **generar la prefirmada**, aunque el `endpoint_url` resuelto del cliente fuera el
regional correcto. Ahora se declara siempre, y se **deriva** del endpoint:

- con endpoint propio —MinIO, emulador— el estilo es **por ruta**, porque el virtual
  convertiría el nombre del bucket en un subdominio que la red local no resuelve;
- sin endpoint —AWS real— el estilo es **virtual**, el que Amazon recomienda y el que produce
  el anfitrión regional.

**No se introdujo ningún valor fijo.** No hay bucket, ni `us-east-2`, ni dominio del proyecto
en el código: el anfitrión lo deriva el SDK de la región configurada, y por eso la prueba está
parametrizada con tres regiones distintas.

Diff total de la rama: **2 archivos, +145 / −4**. Ningún cambio de API, de modelo ni de
contrato. Los finales de línea se conservaron en **LF** en los dos archivos.

### 25.5. REFACTOR

**Declarado innecesario, con su razón.** El arreglo eliminó una rama condicional en lugar de
añadirla: el cuerpo del método quedó más corto y con una sola forma de construir las opciones.
No hay duplicación que extraer ni nombre que mejorar. Se actualizó la documentación del método
para que explique de dónde sale el estilo y por qué, que era la parte realmente engañosa.

### 25.6. Regresión y validación funcional contra AWS real

| Validación | Alcance | Resultado |
| --- | --- | --- |
| Tests del adaptador | unitaria | **29/29** |
| Tests de almacenamiento | unitaria | **61/61** |
| Contrato de `ObjectStorage` | **MinIO real** | **48/48** |
| `ruff format --check` | 325 archivos | **exit 0** |
| `ruff check` | repo completo | **exit 0** |
| `mypy` | 319 archivos | **exit 0** — sin incidencias |
| **Suite completa** | **PostgreSQL y MinIO reales** | **1974 passed, 2 skipped, exit 0** |

Los dos *skips* son límites de la plataforma Windows —`time.tzset` no existe y el sistema no
concede el privilegio de crear enlaces simbólicos—, ajenos al arreglo y presentes desde antes.

Nota de método, porque una primera ejecución produjo **842 errores** y no debe leerse como
regresión: la variable apuntaba a `personal_blog`, la base **de desarrollo**. La guarda de la
suite la rechazó —«la base no termina en `_test`»— precisamente porque la integración ejecuta
`alembic downgrade base`. La guarda hizo su trabajo; la invocación era la equivocada. Repetida
contra `personal_blog_test`, con su marca obligatoria `personal-blog:test-database`, la suite
entera pasa. Un `pipe` a `tail` enmascaraba además el código de salida real de `pytest`, y por
eso las ejecuciones definitivas escriben a archivo y comprueban el código sin tubería.

**Revalidación funcional contra el bucket real, 14/14 correctas** —las trece de §24.2 más la
comprobación explícita del anfitrión—, con la identidad **humana** y credenciales por la
**cadena por defecto de boto3**, que es el camino de producción:

| Comprobación | Antes (§24.2) | Ahora |
| --- | --- | --- |
| GET con URL prefirmada | **403 SignatureDoesNotMatch** | **HTTP 200**, bytes idénticos |
| Anfitrión de la prefirmada | `<bucket>.s3.amazonaws.com` | `<bucket>.s3.us-east-2.amazonaws.com` |
| Prefirmada de TTL corto, antes de expirar | fallaba | **HTTP 200** |
| Prefirmada de TTL corto, tras 8 s | 403 por firma inválida | **403 por expiración**, que es la causa correcta |
| GET **sin firma** sobre objeto privado | 403 | **403 AccessDenied** |
| Objeto borrado con URL válida nueva | inconcluso | **404 `NoSuchKey`** — ausencia del objeto, no fallo de firma |

La última fila es la que cierra el hueco de §24.2: el borrado ahora se demuestra con un **404
`NoSuchKey`**, y no con un 403 que podía confundirse con el propio defecto. El **TTL productivo
de 900 s no se cambió**: la duración es argumento del contrato, y la prueba de expiración usa
un valor corto **suyo**.

### 25.7. El artefacto Lambda se reconstruyó para que la prueba fuera real

Los ZIP disponibles se construyeron en `Task/026`, **antes** del arreglo: su
`app/shared/storage/s3.py` es el defectuoso. Ejecutar el ciclo del laboratorio con ellos habría
demostrado el comportamiento del código viejo y se habría reportado como si validara el nuevo.

Se reconstruyó el artefacto por el camino reproducible de `Task/024` —build en Linux dentro de
Docker— en `lambda_package/task030` (ruta ignorada por Git, no entra en el entregable):

| Artefacto | `s3.py` | arreglo presente |
| --- | --- | --- |
| `task026` | `11843192867bfcf6…` | **no** |
| `task030` | `e98f9b640297e656…` | **sí**, idéntico byte a byte al del árbol de trabajo |

`empaquetar_lambda verificar` sobre el nuevo: **artefacto válido**, sha256
`0234fcc4ebd937b3a1c0a6f599031970823a4dcdb51fbf0f2fbd6eb1ef09764a`, 3975 entradas, las 41
distribuciones del lock, y layout, rutas, contenido, binarios, orden, fechas y permisos
correctos.

## 26. Ciclo real del laboratorio, gates finales, y parada H-030-5

### 26.1. El laboratorio, levantado y con su aislamiento demostrado

`laboratorio/.env.laboratorio` no existía. Es configuración local **ignorada por Git**, y su
ejemplo versionado contiene únicamente credenciales ficticias que el emulador exige por diseño
—`test` / `test`, cuya publicidad es el punto— y el digest fijado de Floci. Copiarlo es el paso
de preparación que el propio ejemplo documenta, no un atajo: no se inventó ningún valor.

| Comprobación del arranque | Resultado |
| --- | --- |
| Terraform en caché | **1.16.2**, sha256 coincidente con el publicado por HashiCorp |
| Emulador | Floci **2.1.0 por digest fijado** `sha256:f5aa8c18…`, nunca `latest` |
| Publicación | **`4566/tcp -> 127.0.0.1:4566`**, solo loopback |
| Salida TCP externa | *Network is unreachable* |
| Metadata link-local | *Network is unreachable* |
| DNS externo | sin respuesta |
| Alcance del emulador | sí, por la red interna |
| Identidad del destino | cuenta **ficticia** del emulador, guarda G-03 satisfecha |

### 26.2. La topología de dos roots, demostrada en ejecución real

El ciclo aplicó **primero el root de medios y después el de aplicación**, cada uno con su
propio state, y con las guardas fail-closed R-23/R-24 ejecutadas **antes de cada** `init`,
`plan` y `apply`.

| # | Lo que la enmienda H-030-4 debía demostrar | Evidencia de la ejecución |
| --- | --- | --- |
| 1 | `terraform-medios` va primero | `init` → `fmt` → `validate` → `plan` → `apply` del root de medios **antes** de tocar el de aplicación |
| 2 | State propio por root | medios en `…\estado\local\medios\terraform.tfstate`; aplicación en `…\estado\local\aplicacion\terraform.tfstate`. **Ningún archivo compartido** |
| 3 | Plan y apply del root de medios | **8 to add** → `Apply complete! Resources: 8 added, 0 changed, 0 destroyed` |
| 4 | Salidas del root de medios | `arn_del_bucket = "arn:aws:s3:::blog-lab-medios"`, `nombre_del_bucket = "blog-lab-medios"` |
| 5 | Inyección al root de aplicación | esas dos salidas se leen y se escriben en su `destino.tfvars.json`. **Sin `terraform_remote_state`** |
| 6 | El root de aplicación **no** administra el bucket | su plan y su apply no contienen **ningún** `aws_s3_bucket` ni `module.almacenamiento`: **13 added**, frente a los 21 recursos de un solo grafo |
| 7 | La dependencia cruzada resuelve de verdad | la política IAM del root de aplicación quedó con `arn:aws:s3:::blog-lab-medios/medios/*` y `ListBucket` sobre el bucket **inyectado**; la Lambda con `BLOG_STORAGE_BUCKET=blog-lab-medios` |

**La topología, el orden, la separación de states y el contrato de entradas explícitas quedan
demostrados.** Es el objetivo central de la enmienda y está cumplido.

### 26.3. Camino crítico y servicios: verdes

| Fase | Resultado |
| --- | --- |
| S3 | `put` 200, `get` 200, `delete` 204, `prefirmada` 200, sonda 200, **bytes coinciden** |
| SSM | los **4** parámetros, HTTP 200 |
| IAM | `GetRole blog-lab-lambda` 200; la política de confianza nombra a `lambda.amazonaws.com` |
| Lambda | `python3.12`, `Zip`, 512 MB, 30 s, handler `app.lambda_handler.handler` |
| **Camino crítico** | **`GET /health` → HTTP 200**, `{"status":"ok","service":"personal-blog-backend","version":"0.1.0"}` |

El lanzador declara por sí mismo dos límites del destino, y aquí se repiten porque siguen
siendo ciertos: la lectura **anónima** del objeto devolvió **200 y no 403**, porque el emulador
no aplica la autorización de S3 (`autorizacion_de_s3_verificada: false`), de modo que esto
**no** demuestra que el bucket sea privado, solo que la configuración de privacidad se acepta;
y el emulador **no cifra** los `SecureString` de SSM ni aplica políticas IAM. La privacidad
efectiva del bucket ya está demostrada **contra AWS real** en §24 y §25.6.

### 26.4. Lo que este ciclo **no** demuestra sobre DEF-030-1

Dicho explícitamente para que no se lea de más:

- El `prefirmada: 200` del laboratorio lo genera el **firmador SigV4 propio del lanzador**
  (`scripts/laboratorio/firma_aws.py`), **no** `S3Storage`. No ejercita el adaptador.
- `GET /health` **no toca el almacenamiento**: su handler solo lee configuración. La Lambda
  ejecutó el ZIP **con el arreglo** y respondió 200, lo que demuestra que el código corregido
  se empaqueta, importa y sirve en el runtime de Lambda, no que la ruta de medios funcione ahí.

Lo que sí valida DEF-030-1 es lo de §25.6: **48/48** pruebas de contrato contra **MinIO real**
—que es el caso del estilo por ruta, el que el arreglo podía romper—, 61 pruebas unitarias de
almacenamiento, la suite completa con servicios reales, y **14/14** contra el **bucket real de
AWS**. El laboratorio aporta que el artefacto corregido despliega y sirve; no sustituye a eso.

### 26.5. DEF-030-2 — la enmienda de dos roots no llegó a los subcomandos de runbook

**Esto es una regresión de la enmienda H-030-4, y es la razón de la parada.**

El ciclo abortó antes de su propio destroy (§26.6), así que el teardown se ejecutó con el
subcomando `destruir`. Ahí apareció el defecto:

```
Apply complete! Resources: 0 added, 0 changed, 13 destroyed.
ErrorDeInventario: el destroy no elimino todo; siguen presentes: s3: blog-lab-medios
```

`comando_destruir` destruyó los 13 recursos del root de aplicación y después comprobó que el
inventario del emulador estuviera vacío. No lo estaba: el bucket pertenece ahora al **otro
root**, que ese subcomando no conoce.

Medición del alcance, contando referencias a `ROOT_DE_MEDIOS` en cada subcomando:

| Subcomando | Consciente de dos roots |
| --- | --- |
| `ciclo` | **sí** — 12 referencias |
| `crear` | **no** |
| `validar` | **no** |
| `rollback` | **no** |
| `destruir` | **no** — además consulta la salida `bucket_de_medios` para vaciar el bucket, y ya no la obtiene del root que lo administra |
| `recuperar` | **no** |

La enmienda cableó `comando_ciclo` y **dejó los cinco subcomandos de runbook operando sobre un
solo root**. Son precisamente los que los runbooks de recuperación usan en una incidencia, así
que el hueco no es cosmético: `destruir` deja el bucket en pie y falla, y `crear`, `validar`,
`rollback` y `recuperar` operarían sobre un grafo incompleto sin las variables inyectadas.

**No se ha corregido en esta sesión.** La instrucción para este checkpoint es detenerse si el
ciclo falla por una regresión del refactor, y esto lo es. Corregirlo son cinco subcomandos y su
verificación de inventario: un cambio de diseño de la enmienda, no un parche de paso, y
merece su propia autorización y sus propias pruebas en `tests/laboratorio`.

### 26.6. DEF-030-3 — la aserción de identidad del runtime rompe con Docker 29.1.3

El ciclo terminó con **código de salida 1** en la fase que verifica qué imagen ejecutó el
contenedor de Lambda, **después** de que todo lo funcional y el camino crítico pasaran:

```
ErrorDeRuntime: el contenedor pidio la imagen 'sha256:a89893d9…' y el runtime fijado
es 'public.ecr.aws/lambda/python:3.12'
```

Los tres valores que el propio lanzador imprimió inmediatamente antes son **idénticos**:

| Valor | Contenido |
| --- | --- |
| imagen solicitada | `sha256:a89893d9c93a9ffbf9e35ca32d7cadc635cbf3a9aec94480c75ed07150a05daa` |
| image ID real | el mismo |
| runtime fijado por `Task/024` | el mismo |

`confirmar_imagen_del_contenedor` hace **dos** comprobaciones: la del **ID de imagen**, que es
la autoritativa, y una comparación de **cadena de referencia** contra la etiqueta fijada. La
primera **pasa**; la segunda falla porque el contenedor trae en `Config.Image` el ID desnudo y
no la etiqueta.

Evidencia de que es un cambio del entorno y no del proyecto:

- en `Task/025`, con el **mismo** image ID y el **mismo** digest de Floci, esa línea fue
  `imagen solicitada : public.ecr.aws/lambda/python:3.12` —la **etiqueta**—, y la comprobación
  dio `COINCIDE`;
- la imagen local **sí** lleva la etiqueta: sus `RepoTags` incluyen
  `public.ecr.aws/lambda/python:3.12`. No falta nada que el lanzador necesite;
- el host corre **Docker 29.1.3**, y es Floci quien decide con qué referencia crea el
  contenedor;
- ni `scripts/laboratorio/runtime.py` ni `verificar_contenedor_observado` aparecen en el diff
  de `Task/030`.

**No se ha relajado la guarda.** Aflojar una aserción de identidad del runtime para que un
ciclo se ponga verde es exactamente lo que no debe hacerse sin decisión explícita, aunque el
digest coincida. Queda como hallazgo con propietario.

### 26.7. Teardown completo y sin residuos

El teardown se completó, en **orden inverso** —aplicación primero, medios después—, y con el
plan destructivo revisado antes de confirmarlo:

| Paso | Resultado |
| --- | --- |
| Root de aplicación | **13 destroyed** |
| Root de medios | plan `-destroy` revisado: **8 to destroy**, todos `module.almacenamiento.*`, bucket `blog-lab-medios` y **no** el de producción → **8 destroyed** |
| Inventario del emulador | sin lambdas, sin roles, sin APIs, sin parámetros SSM, sin log groups; en S3 solo `awslambda-us-east-1-tasks`, que **crea el propio emulador** |
| State del root de aplicación | serial 31, **0 recursos, 0 outputs** |
| State del root de medios | serial 18, **0 recursos, 0 outputs** |
| `bajar` | **0** contenedores, **0** redes, **0** volúmenes, y 1 recurso creado por el emulador retirado |

La guarda de confirmación del subcomando `destruir` **funcionó como debe**: sin la confirmación
interactiva del sha256 del plan, se detuvo sin destruir nada. La confirmación se dio tras
revisar que los 13 borrados fueran todos recursos `blog-lab-*` del emulador local.

Nota sobre un residuo **histórico**, no activo: `…\estado\local\terraform.tfstate` —la ruta de
antes de la separación por root— conserva **0 recursos** (serial 717, del cierre limpio de
`Task/026`) y su `.backup` los 20 de entonces. Es historia de un emulador efímero que ya no
existe, no un recurso vivo.

**Un efecto de diseño que conviene dejar escrito:** el ciclo del laboratorio reutiliza los
mismos directorios de root que producción y les genera su `backend.generado.tf`, de modo que al
terminar el root de medios queda inicializado contra el backend **local** del laboratorio. Era
ya el comportamiento del root de aplicación desde `Task/025`; ahora aplica también al de
medios. El state remoto en S3 **no se tocó**: el laboratorio solo habla con `127.0.0.1:4566`
bajo cuenta ficticia, y la sesión AWS de esta máquina estaba caducada durante todo el ciclo.
Cualquier operación productiva posterior debe regenerar su backend y reinicializar, que es el
procedimiento ya documentado.

### 26.8. Un gate de CI que faltaba, encontrado y cerrado

La enmienda de §22 creó `terraform-medios` como root propio, y **el CI no lo comprobaba**:
`ci-infra.yml` tenía pasos para `terraform`, `bootstrap/github-oidc` y
`bootstrap/terraform-state`, y ninguna mención de `terraform-medios`. Un root versionado sin
gate es un root cuyo formato, lock y validez nadie comprueba: exactamente el hueco que la
enmienda podía dejar sin que ningún gate existente se pusiera rojo.

Se añadió el paso **«Media storage root static validation and mocked plans»**, con el mismo
patrón offline que los de bootstrap —proveedores simulados, sin credenciales y sin `id-token`—:

```
git ls-files --error-unmatch terraform-medios/.terraform.lock.hcl
terraform -chdir=terraform-medios fmt -check -recursive
terraform -chdir=terraform-medios init -backend=false -input=false -lockfile=readonly
git diff --exit-code -- terraform-medios/.terraform.lock.hcl
terraform -chdir=terraform-medios validate
terraform -chdir=terraform-medios test
```

Incluye la comprobación de que el lock **no cambia**, que los pasos de bootstrap no hacían y
que es lo que convierte `-lockfile=readonly` en una garantía comprobada y no en una intención.

### 26.9. Gates finales, con la invocación del CI y sobre el entregable real

Los gates de Terraform se ejecutaron sobre una **exportación limpia** del entregable —los
archivos versionados **más** los nuevos no ignorados, que es lo que el CI verá cuando esto se
integre—, con `TF_DATA_DIR` aislado para no tocar los `.terraform` operativos. La exportación
deja fuera lo ignorado: se comprobó que `backend.generado.tf`, `.env.laboratorio` y `.env` **no
aparecen** en ella.

| Root | fmt | init `-backend=false -lockfile=readonly` | validate | test | lock intacto |
| --- | --- | --- | --- | --- | --- |
| `terraform` | OK | OK | OK | no tiene `tests/` | OK |
| `terraform-medios` | OK | OK | OK | **7 passed, 0 failed** | OK |
| `bootstrap/github-oidc` | OK | OK | OK | OK | OK |
| `bootstrap/terraform-state` | OK | OK | OK | OK | OK |

Los **cuatro** locks de proveedor son **byte a byte idénticos**: mismo sha256, AWS `6.64.0`
exacta y 16 hashes de plataforma. El root nuevo no introdujo una versión distinta ni una
plataforma menos.

| Gate | Invocación | Resultado |
| --- | --- | --- |
| `fmt -check -recursive` | los 4 roots | **4/4** |
| Suites Python de infra | `unittest discover` como el CI | **336 OK**: oidc 60, terraform_state 12, security 88, laboratorio 176 |
| Compilación de scripts | `compile()` sobre `scripts/**/*.py` | 18 archivos, **0 fallos** |
| Gitleaks 8.30.1 | entregable completo, desde dentro, con `.gitleaks.toml` | **no leaks found** — 289 archivos, 6.03 MB |
| Enlaces Markdown | 171 archivos | **1945 enlaces relativos, 0 rotos** |
| Account ID real | entregable completo | **0 apariciones** |

Las 176 pruebas de `tests/laboratorio` son las que cubren el lanzador, y por tanto el refactor
de dos roots: pasan sin modificar ninguna expectativa.

**Account ID.** Las únicas secuencias de doce dígitos del entregable son ficticias:
`000000000000` (la cuenta del emulador, 28 veces), `123456789012` (los ejemplos de la
documentación de AWS, 23) y `999999999999` (una fixture, 9). El Account ID real **no aparece**.

**Enlaces: método, porque el primer resultado fue falso.** Un verificador ingenuo marcó 54
enlaces como rotos. Ninguno lo estaba: reproducía mal el anclaje de GitHub —que **no colapsa**
los espacios, de modo que una raya «—» eliminada deja sus dos espacios y produce un doble
guion— y trataba como enlaces destinos que viven dentro de tramos de código en línea. Corregido
el verificador, **0 rotos**. Se deja dicho porque el falso positivo es reincidente y confundirlo
con deuda real habría llevado a "arreglar" documentación correcta.

**Gitleaks en el backend: dos hallazgos, y ninguno es un secreto.** El barrido del entregable
del backend reporta 2 coincidencias de `generic-api-key`, ambas en
`tests/test_endurecimiento_redaccion.py` y `tests/test_logging_redaccion.py`: son las cadenas
sintéticas que esas pruebas usan para **demostrar que la redacción de logs funciona**, y su
razón de existir es parecerse a un secreto. Ninguno de los dos archivos fue tocado por
`Task/030`, y el CI del backend **no ejecuta Gitleaks** —sus gates son formato, lint, tipos,
migraciones, pruebas, auditoría de dependencias, imagen y artefacto—, así que el repositorio no
tiene una *allowlist* donde estas fixtures estuvieran declaradas. **No se añadió ninguna**: la
autorización de `DEF-030-1-backend-fix` es acotada y no cubre configurar un gate nuevo. Queda
como observación con propietario, no como hallazgo de seguridad.

### 26.10. Gates del backend

| Gate | Resultado |
| --- | --- |
| `ruff format --check` | **exit 0** — 325 archivos ya formateados |
| `ruff check` | **exit 0** — *All checks passed* |
| `mypy` | **exit 0** — sin incidencias en 319 archivos |
| Suite completa con PostgreSQL y MinIO reales | **1974 passed, 2 skipped, exit 0** |
| Diff de la rama | **2 archivos, +145 / −4** |
| Finales de línea | **LF** en los dos archivos, 0 CRLF |
| Commits | **0** — sin commit, push, PR ni merge |

### 26.11. Parada H-030-5 — `Task/030` **no** se declara lista para aprobación

DEF-030-1 **está corregido y demostrado** contra AWS real, con la ley test-first cumplida de
principio a fin. Pero el ciclo real del laboratorio, que este checkpoint exigía ejecutar,
**encontró una regresión de la enmienda de dos roots** (DEF-030-2) y un segundo defecto de la
aserción de runtime (DEF-030-3). El propio prompt fija la conducta: si el ciclo falla por una
regresión del refactor, **detenerse**. Se detiene.

No se declara `Task/030 — READY FOR FINAL APPROVAL`, y no se inventa un PASS del ciclo: el
ciclo terminó con **código de salida 1**.

**Lo que queda demostrado y cerrado:**

- el bucket de medios de producción, creado, verificado en 10 puntos y **convergente 0/0/0 con
  `resource_drift = 0`**;
- su state remoto, operativo, reconciliado y con lock nativo; los dos states de bootstrap
  intactos; **EX-028-C7 extinguida**;
- **DEF-030-1 corregido**: matriz, RED, GREEN mínimo, refactor justificado, regresión completa
  —**1974 passed** con PostgreSQL y MinIO reales— y **14/14** contra el bucket real;
- la **topología de dos roots**, con orden, states separados e inyección explícita, demostrada
  en ejecución real; el root de aplicación ya **no** administra el bucket;
- el **camino crítico** del laboratorio verde: `GET /health` → **HTTP 200** desde la Lambda que
  ejecuta el artefacto **con el arreglo**;
- teardown completo, ambos states a **0 recursos**, laboratorio retirado sin residuos;
- el **gate de CI que faltaba** para `terraform-medios`, añadido;
- **19/19** gates de Terraform, **336** pruebas Python de infra, sin secretos, **0** enlaces
  rotos, **0** apariciones del Account ID.

**Lo que bloquea el cierre:**

- **DEF-030-2** — `crear`, `validar`, `rollback`, `destruir` y `recuperar` siguen operando sobre
  un solo root. Son los subcomandos de los runbooks de incidencia. Exige decisión y
  autorización propias, con pruebas nuevas en `tests/laboratorio`.
- **DEF-030-3** — la aserción de identidad del runtime compara cadenas de referencia y rompe
  bajo Docker 29.1.3, aunque el image ID coincida exactamente. **No se ha relajado.**

**Estado real, sin adornos.** `D-08` sigue **Resuelta (MVP)** y no se modificó. `B-016-1`
**sigue abierto**. No se creó ningún rol de ejecución Lambda: el IAM de producción es de
`Task/032`. `PersonalBlogGitHubOidcValidation` permanece con **cero políticas**. `Task/031`,
`Task/032` y `Task/033` **sin iniciar**. El frontend **intacto**. En los dos repositorios con
cambios —`personal-blog-infra` y `personal-blog-backend`— **no hay commit, push, PR ni merge**,
y la rama del backend sigue a **0 commits** de `main`.

**Decisión humana requerida:** autorizar la corrección de DEF-030-2 y DEF-030-3 dentro de
`Task/030`, o cerrarla con el bucket y el adaptador ya validados y abrir una tarea propia para
los dos defectos del laboratorio, que son de herramental y no de la infraestructura entregada.

## 27. H-030-5 — DEF-030-2 y DEF-030-3 corregidos, runbooks ejecutados de verdad y READY FOR FINAL APPROVAL

Autorización exacta: `authorize: Task/030 H-030-5-lab-two-roots-runtime`. La decisión humana
de §26.11 fue corregir los dos defectos **dentro** de `Task/030`. Esta sección cierra esa fase
con evidencia; la historia de §26 se conserva tal cual.

### 27.1. DEF-030-2 — los cinco subcomandos, conscientes de los dos roots

Una sola función, `secuencia_de_roots(operacion)`, responde «qué roots y en qué orden», a
partir de `SENTIDO_DE_CADA_OPERACION`. Una operación no declarada **aborta**: no hereda un
orden por omisión. Los cinco subcomandos pasan por `preparar_los_roots_para`, que prepara
siempre medios primero —su contrato hace falta antes de tocar el grafo de aplicación— y
entrega nombre y ARN al root de aplicación por **variables explícitas**, sin
`terraform_remote_state`.

| Subcomando | Root de medios | Root de aplicación |
| --- | --- | --- |
| `crear` | plan solo `create`, revisado y confirmado por SHA-256, apply | plan solo `create`, confirmado por SHA-256, apply |
| `validar` | **lectura**: fmt, validate y contrato; no aplica nada | fmt/validate, ownership disjunto, contrato coherente y validación funcional |
| `rollback` | **lectura**: un medios sano no se reaplica | plan solo `update` que **debe** actualizar `aws_lambda_function`; si no, se rechaza sin aplicar ningún root |
| `recuperar` | crea si falta, no-op sin confirmación si está sano, rechaza un reemplazo antes del apply | después de medios, con el contrato inyectado |
| `destruir` | vaciado del bucket y plan `-destroy` **después** de aplicación | primero: plan `-destroy`, confirmación, apply y state a 0/0 |

Tras cada destroy se exigen state **y** outputs vacíos, y ausencia contra las APIs; mientras el
root de medios vive, su bucket exacto —y solo ese nombre— **no** cuenta como residuo.

Pruebas: `tests/laboratorio/test_topologia_de_roots.py`, **44 pruebas**. Cubren el orden de
creación y de destrucción, subdirectorios de state y de Terraform no compartidos, residuos con
medios vivo, contrato incompleto o incoherente que aborta antes de tocar aplicación, fallo de
medios que impide continuar, fallo de aplicación que no destruye ni vacía medios, `recuperar`
con medios ausente, sano o con reemplazo, y que **ningún** comando llame a un ayudante sin
declarar su root. Tres de ellas son la **guarda de rollback** añadida al final de la fase:
`test_update_de_lambda_demuestra_el_rollback`, `test_lambda_sin_cambio_no_demuestra_rollback`
y `test_actualizar_otro_recurso_no_demuestra_rollback`.

### 27.2. DEF-030-3 — identidad del runtime por lista cerrada, sin relajar el image ID

`confirmar_imagen_del_contenedor` sigue exigiendo **igualdad exacta** del image ID observado
con el esperado, y la sigue comprobando siempre. Lo que cambia es la **representación**:
`Config.Image` ya no tiene que ser textualmente la etiqueta, sino pertenecer a una lista
**cerrada** derivada por completo de la identidad inmutable de `Task/024` —etiqueta fijada,
referencia completa, `repositorio@digest`, digest desnudo e image ID esperado—. No hay
patrones: «parece un sha256» no entra.

Pruebas: `tests/laboratorio/test_identidad_del_runtime.py`, **16 pruebas**: 5 formas
admitidas y 11 rechazos —otra etiqueta, otro repositorio con el digest fijado, otro digest,
un sha256 ajeno, image ID distinto o ausente, representación vacía, ausente o ambigua,
`sha256:` sin valor y el `None` de Docker—.

### 27.3. Ejecución real contra el laboratorio

Destino en todas las ejecuciones: `modo=local`, `us-east-1`, ocho endpoints en
`http://127.0.0.1:4566`, cuenta ficticia `000000000000`, publicación de Floci solo en
loopback y guardas R-23/R-24 antes de cada `init`, `plan`, `apply` y `destroy`. Artefacto
Lambda con el arreglo de DEF-030-1: SHA-256 `0234fcc4…09764a`.

**Ciclo completo** (`h0305-ciclo.log`, `2026-09-29T03:56:42Z`, SHA-256 `03ba3c4e…40223f`):
medios 8 altas → aplicación 13 altas → validación funcional → `GET /health` **HTTP 200** →
runtime → logs → **idempotencia exit 0** → **drift controlado** de
`/blog-lab/local/storage_region`, recreado y reconciliado → primer destroy verificado →
reconstrucción con smoke **HTTP 200** → segundo destroy verificado. Termina con el banner
`CICLO COMPLETO` y su resumen. El código de salida **no queda escrito en el log**: el
envoltorio lo imprimía solo por consola, y la sesión que lo ejecutó registró **exit 0**.

**`crear`** (`h0305-crear.log`, `2026-09-30T02:11:14Z`, SHA-256 `58c779b4…519621e`). Los dos
planes se revisaron **antes** de confirmar:

| Root | Plan revisado | SHA-256 |
| --- | --- | --- |
| medios | backend local, cuenta ficticia, loopback, `blog-lab-medios`, **8 create**, solo `aws_s3_*`, 0 change, 0 destroy | `de5dbdf9…a97c6d08` |
| aplicación | **13 create**, 0 change, 0 destroy, **0 recursos S3**, contrato inyectado | `83872033…e1299f4` |

Después, sobre los states reales: medios **8** administrados; aplicación **13**, ninguno
`aws_s3_*`; states distintos; nombre y ARN inyectados; la política IAM contiene el ARN del
bucket; la Lambda usa el ZIP esperado. `GET /health` **HTTP 200** y runtime **COINCIDE**:
imagen solicitada, image ID real y runtime fijado, los tres
`sha256:a89893d9…07150a05daa`. Termina con `CREAR — completado`.

**`validar`** (`h0305-validar.log`, `2026-09-30T02:13:44Z`, SHA-256 `702bf2cf…c37afb6`):
fmt/validate de los dos roots, ownership disjunto, contrato coherente, S3 dentro de los
límites conocidos del emulador, cuatro SSM HTTP 200, `GetRole` 200, Lambda `python3.12`,
`GET /health` **HTTP 200**, runtime **COINCIDE** —ahora bajo Docker 29.1.3, justo lo que
DEF-030-3 rompía— e inspección con `boto3/1.43.82` desde el ZIP. `recursos_por_root`:
aplicación **15** direcciones —13 administradas y 2 data sources
`aws_iam_policy_document`— y medios **8**.

**`destruir`** (`h0305-destruir.log`, SHA-256 `71da46e7…a8921c4`):

| Paso | Resultado |
| --- | --- |
| Plan `-destroy` de aplicación | **13 delete**, SHA-256 `b0d949d9…e770d80`, confirmado |
| Apply | `0 added, 0 changed, 13 destroyed`; state de aplicación **0/0** (`2026-09-30T02:17:28Z`) |
| Inventario intermedio | solo `blog-lab-medios`, legítimo; Lambda, API, Logs y SSM vacíos |
| Vaciado del bucket | 4 objetos y versiones retirados |
| Plan `-destroy` de medios | **8 delete**, exclusivamente los ocho `aws_s3_*` del módulo, SHA-256 `3bf0da6b…5957a099`, confirmado |
| Apply | `0 added, 0 changed, 8 destroyed`; state de medios **0/0** (`2026-09-30T02:19:55Z`, serial 72) |
| Cierre | `destroy aplicado en los dos roots, en orden inverso, y ausencia demostrada contra las APIs` |

**Corrección de un dato del traspaso.** La sesión anterior se agotó y el traspaso decía que
el destroy de medios **no** se había aplicado y seguía esperando su confirmación. **No era
así**: el log muestra la confirmación y el apply completos, y el state de medios se
reescribió a 0 recursos a las `02:19:55Z`. Al reanudar no quedaba ningún proceso
`laboratorio.py`, `terraform` ni envoltorio vivo; no había nada que confirmar. El plan
guardado conservaba su SHA-256 `3bf0da6b…`, pero **ya estaba consumido** y no se reutilizó.

El código de salida de `destruir` tampoco quedó en el log. El mensaje final solo se imprime
en la rama que termina en `return 0`, **después** de que el propio comando exija state y
outputs vacíos, ausencia en las APIs y ownership disjunto. Aun así se verificó de nuevo, de
forma independiente y sin mutar nada:

| Comprobación independiente | Resultado |
| --- | --- |
| Procesos vivos | ninguno de `laboratorio.py`, `terraform` ni envoltorio |
| State de aplicación | serial 127, **0 recursos, 0 outputs** |
| State de medios | serial 72, **0 recursos, 0 outputs** |
| State histórico de antes de la enmienda | serial 717, **0 / 0** (§26.7) |
| Inventario por API, con guardas de destino y cuenta `000000000000` | S3, Lambda, API Gateway v2, Logs y SSM **vacíos** |
| `laboratorio.lock` | ausente |

### 27.4. Rollback y recuperar: evidencia controlada, no ejecución real

**No se provocó ningún incidente real** para ejercitar estos caminos, y no se declara una
ejecución que no ocurrió.

- **Rollback — pruebas controladas**: exige que el plan actualice de verdad
  `aws_lambda_function`; un plan sin ese update, o que solo actualice otro recurso, se
  rechaza; un rollback rechazado **no aplica ningún root**; un medios sano **no** se recrea;
  el contrato se inyecta a aplicación.
- **Recuperar — pruebas controladas**: si medios falta, se crea **antes** que aplicación; si
  está sano, no se recrea ni pide confirmación; un fallo del root de medios impide tocar
  aplicación; un reemplazo de medios se rechaza antes del apply; el contrato se obtiene
  antes del root de aplicación.

`crear`, `validar` y `destruir` son **ejecución real**; `rollback` y `recuperar`, **pruebas
controladas de integración** con el herramental simulado.

### 27.5. Laboratorio retirado

`python scripts/laboratorio/laboratorio.py --modo local bajar` (`2026-09-30T02:42:19Z`,
**exit 0**, log SHA-256 `f97cd1c2…0109842e8`): contenedor y redes del laboratorio retirados,
y un recurso creado por el emulador, también. **0** contenedores, **0** contenedores del
emulador, **0** redes, **0** volúmenes y **0** volúmenes del emulador.

### 27.6. Contexto productivo de `terraform-medios`, restaurado

El laboratorio dejó `terraform-medios/backend.generado.tf` con `backend "local"`, como
advertía §26.7. Se restauró sin tocar ningún state:

1. `backend.generado.tf` regenerado con `backend "s3" {}`. Es un archivo ignorado por Git.
2. `terraform init -reconfigure -input=false -lockfile=readonly` con
   `-backend-config=<privado>/remote.tfbackend` y el **`TF_DATA_DIR` operativo privado** del
   root, `<privado>/application/media/terraform-data`, el mismo de H-030-3 y H-030-4.
   **Exit 0, cero warnings**, sin petición ni mensaje de migración.
3. Metadata resultante: `s3`, key `application/media/terraform.tfstate`, `us-east-2`,
   `encrypt=true`, `use_lockfile=true`, perfil `personal-blog`, **sin DynamoDB y sin KMS**.

**No** se usaron `-migrate-state`, `state push`, `state mv` ni `state rm`; no se copió ningún
state local; el bootstrap no se tocó. Los tres states remotos conservan VersionId, longitud y
`LastModified` antes y después del `init`.

El `.terraform` **dentro del repositorio** de `terraform-medios` sigue siendo el directorio de
trabajo del laboratorio y apunta a su state local vacío. Es inocuo por construcción: con el
bloque `s3` generado, Terraform se niega a operar sobre esa metadata hasta un `init`
explícito.

### 27.7. AWS final — sin apply

Evidencia privada: `<privado>/application/media/h0305-final-20260930T024529Z`, de
`2026-09-30T02:45:29Z` a `02:47:02Z`.

| Comprobación | Resultado |
| --- | --- |
| STS, **antes** de cualquier consulta | `assumed-role/PersonalBlogAdministrator/personal-blog-entry-admin`, perfil `personal-blog`, `us-east-2`; cuenta igual a la del tfvars privado |
| `bootstrap/terraform-state` | VersionId `pjvyHqNzxTObDUSOcwVbuXSwAD3I4RM2`, 12 864 B, AES256, serial 2, 7 administrados + 1 data source, 4 outputs: **intacto** |
| `bootstrap/github-oidc` | VersionId `Dl7AxGe7qj28P703ZFJwh_qsRzY2ViHI`, 5 840 B, AES256, serial 1, 2 + 1, 2 outputs: **intacto** |
| `application/media` | VersionId `G9iYVw9i9h15VNedSmrhl1EgwkibKz39`, 13 558 B, AES256, serial 3, **7** administrados, todos `aws_s3_*`, 2 outputs: el de §24.1 |
| `.tflock` de las tres keys | **ausentes** antes del `init`, después del `init` y después del plan |
| Readback del bucket de medios | existe en `us-east-2`; BPA 4/4; `BucketOwnerEnforced`; versionado `Enabled`; AES256 sin KMS; policy con **un** `Deny` TLS y **ningún** `Allow`, `IsPublic=false`; lifecycle 30/7 sin expiración de actuales ni transiciones; CORS **ausente**; tags 5/5 exactas; `force_destroy=false` en el state |
| BPA de cuenta | 4/4 `true` |

**Plan NORMAL** de `terraform-medios`, con `-lock=true -lock-timeout=30s -detailed-exitcode`:

| Gate | Resultado |
| --- | --- |
| `-detailed-exitcode` | **0**, «No changes» |
| add / change / destroy | **0 / 0 / 0** |
| `resource_drift` | **0** |
| Recursos | **7/7 no-op** |
| Outputs | **2/2 no-op** |
| `applyable` / `errored` | `false` / `false` |
| Replacements / imports / moves | **0 / 0 / 0** |
| Warnings | **0** en `init`, plan y show |
| State reescrito | **No**: VersionId, longitud y `LastModified` idénticos |
| Plan binario / JSON | `2834e2fd…08418d9` / `490d6bdc…ec199` |

**No se ejecutó ningún apply.**

### 27.8. Gates finales

Infra, sobre el árbol actual y con las invocaciones del CI:

| Gate | Resultado |
| --- | --- |
| `tests/laboratorio`, completa | **236 pruebas, OK**: las 233 previas más las 3 de la guarda de rollback |
| `tests/oidc` | **60, OK**, 1 skip de plataforma: permisos POSIX, que se comprueban en Linux |
| `tests/terraform_state` | **12, OK** |
| `tests/security` | **88, OK** |
| Terraform, 4 roots, exportación limpia y `TF_DATA_DIR` aislado | fmt, `init -backend=false -lockfile=readonly`, validate y test: **16/16 exit 0** |
| `terraform test` | `terraform-medios` **7 passed**; `bootstrap/github-oidc` **9**; `bootstrap/terraform-state` **5**; `terraform` sin `tests/` |
| Locks de proveedor | los 4 **idénticos**, `51998481…`, sin cambios durante los gates; los tres versionados, iguales a `HEAD` |
| Compilación de scripts | 18 archivos, **0 fallos** |
| CI YAML | parseable; el paso de `terraform-medios test`, presente |
| `git diff --check` | limpio |
| Gitleaks 8.30.1 sobre el entregable | **no leaks found**, 6,14 MB, repetido tras documentar |
| Enlaces Markdown, tras documentar | 171 archivos, **1957 enlaces relativos, 0 rotos**, sin encabezados duplicados nuevos |
| Account ID real | **0 apariciones**; solo `000000000000`, `123456789012` y `999999999999` |

Evidencia: `tmp/task030/h0305-gates-20260930T024822Z/`, `tmp/task030/h0305-gates-20260930T030602Z/`
—la repetición tras documentar— y `tmp/task030/h0305-final-*.log`, fuera de Git.

Backend. Se repitieron porque no se podía demostrar la fecha de la última ejecución; el
workspace no cambió desde la suite completa —los mismos 2 archivos, +145 / −4, última
modificación el 2026-09-28—:

| Gate | Resultado |
| --- | --- |
| `test_adaptadores_de_almacenamiento` | **29 passed** |
| `ruff check` / `ruff format --check` | **PASS** / **PASS**, 325 archivos |
| `mypy app/shared/storage/s3.py` | **PASS** |
| `git diff --check` | **PASS** |
| Finales de línea | LF, sin BOM |
| Suite completa, histórica (§26.10) | **1974 passed, 2 skipped** |

### 27.9. Limitación registrada: reanudar un `destruir` interrumpido entre roots

Si `destruir` se interrumpe **después** de destruir el root de aplicación y **antes** de
confirmar el de medios, volver a lanzarlo **no** continúa: el plan `-destroy` de aplicación
sale vacío y la revisión exige al menos un `delete`, así que aborta sin llegar a medios. Falla
cerrado —no destruye nada que no deba—, pero no reanuda. Aquí no hizo falta, porque el
teardown había terminado antes del corte. Queda documentado en el
[runbook de destrucción](../runbooks/deployment-destroy.md) como decisión humana, sin
recrear el root de aplicación, y como deuda del herramental.

### 27.10. Estado final

**`Task/030 — READY FOR FINAL APPROVAL`**, en estado **Lista para validación**. **No está
Aprobada**: la única aprobación válida es `approved: Task/030-Desplegar-Amazon-S3`.

| Frente | Estado |
| --- | --- |
| H-030-1 / H-030-2 | cerrados; EX-028-C7 **Extinguida** |
| D-08 | **Resuelta (MVP)** |
| H-030-3 / H-030-4 | bucket de medios creado, verificado y **0/0/0, drift 0** |
| DEF-030-1 | corregido bajo la ley test-first; 1974 passed; MinIO 48/48; AWS 14/14 |
| DEF-030-2 | **corregido**: 44 pruebas, y `crear`, `validar` y `destruir` reales en dos roots |
| DEF-030-3 | **corregido**: 16 pruebas, y runtime **COINCIDE** en real bajo Docker 29.1.3 |
| H-030-5 | **cerrado**: ciclo, subcomandos, teardown, `bajar`, AWS final y gates en verde |
| `B-016-1` | **sigue abierto** |

Sin commit, push, PR ni merge. `personal-blog-infra` y `personal-blog-backend` en
`Task/030-Desplegar-Amazon-S3`, a **0 commits** de `main`; `personal-blog-frontend` en `main`,
limpio. `Task/031` sin iniciar.

## 28. Aprobación y cierre

El usuario escribió **`approved: Task/030-Desplegar-Amazon-S3`** el 2026-09-29, después de
§27. Antes de ejecutar el cierre se confirmó: la rama existe y es la activa en los dos
repositorios afectados; las validaciones de §27.8 terminaron en verde; no hay cambios ajenos
mezclados; `main` y `dev` estaban normalizados —cero commits de `main` ausentes en `dev` y
mismo contenido— en infra y en backend.

**Repositorios afectados:** `personal-blog-infra` y `personal-blog-backend`.
`personal-blog-frontend` no forma parte del entregable.

**Entregable final del backend: 6 archivos, +222 / −14.** Incluye DEF-030-1, la reparación
de CI MinIO/GHCR y urllib3 **2.8.0** con excepción de índice por paquete:

| Archivo del backend | Resultado durable |
| --- | --- |
| `app/shared/storage/s3.py` | Prefirmadas con anfitrión regional (DEF-030-1) |
| `tests/unit/test_adaptadores_de_almacenamiento.py` | Regresión de DEF-030-1 |
| `.github/workflows/ci-backend.yml` | MinIO desde el espejo privado de GHCR, autenticado mediante `GHCR_MINIO_READ_TOKEN`; manifiesto `linux/amd64` preservado del índice original, misma release y mismos bytes ejecutados |
| `scripts/generar-locks.sh` | Fecha global congelada; excepción temporal de urllib3 mediante `--exclude-newer-package` y `--upgrade-package` |
| `requirements.lock` | urllib3 2.8.0 en el lock de ejecución |
| `requirements-dev.lock` | urllib3 2.8.0 en el lock de desarrollo |

Las cifras **2 archivos, +145 / −4** de §§25–27 describen los checkpoints de DEF-030-1
anteriores a esas dos correcciones adicionales; se preservan como historia y no
representan el inventario final. El consumo actual de MinIO queda descrito en
[STAGE-06](../stages/STAGE-06-continuous-integration.md#estado-actual-de-minio-en-ci-backend).

**Lo que la aprobación promueve:**

| Elemento | Estado |
| --- | --- |
| Diseño del bootstrap D-06 y root `terraform-medios` | **Aceptado**, antes propuesto |
| [terraform-state-bootstrap.md](../runbooks/terraform-state-bootstrap.md) | **Vigente** |
| Runbooks del laboratorio —crear, validar, rollback, destruir, recuperar— | siguen **Vigentes**, con la ampliación a dos roots **aprobada** |
| §4.1.1 de [aws-local-parity](../architecture/aws-local-parity.md) | ya **Vigente** desde el 2026-09-28; sin cambios |
| Fila S3 de la matriz de paridad | evidencia de AWS real **aprobada**; sigue en `Paridad parcial` |
| D-08 | sigue **Resuelta (MVP)**; registro en 6 abiertas y 15 resueltas |
| ADR | **ninguno nuevo** ni modificado |

**Avance:** **30/41 ≈ 73 %**. **ETAPA 10: 1/7 ≈ 14 %**, con cuatro criterios de salida
marcados en [STAGE-10](../stages/STAGE-10-cloud-deployment.md). **Deuda que sigue viva:**
`B-016-1`; la reanudación de un `destruir` interrumpido entre roots (§27.9); la *allowlist*
de las dos *fixtures* del backend; y **DT-030-URLLIB3**, excepción temporal de índice por
paquete, con propietario y criterio de retiro en
[NFR §7.1](../architecture/non-functional-requirements.md#71-deuda-viva-dt-030-urllib3).
**La aprobación no crea recursos**: no se ejecutó ningún apply tras ella.

**Registro histórico del primer cierre tras la aprobación del 2026-09-29.** La lista
siguiente describe aquel checkpoint; la referencia del backend identifica únicamente
DEF-030-1, no el entregable final de seis archivos descrito arriba.

**Flujo Git de aquel checkpoint**, en cada repositorio afectado, según
[PROJECT_INSTRUCTIONS §8](../claude/PROJECT_INSTRUCTIONS.md):

1. commit del entregable validado —infra `160a111`, backend `cc36529`— y, en infra, un segundo
   commit que registra esta aprobación;
2. `dev` actualizado con `pull --ff-only` e integración de la rama Task con `merge --no-ff`;
3. publicación de `dev` y de la rama Task;
4. pull request **`Task/030-Desplegar-Amazon-S3 → main`** —nunca `dev → main`—, sin aceptarlo
   ni fusionarlo: eso es exclusivo del usuario;
5. vuelta a `main`, `fetch --prune`, `pull --ff-only` y `git branch -d` de la rama Task local,
   sin `-D` y sin tocar la rama remota.

Las URL de los PR y el estado final se entregan al usuario al terminar; GitHub es su fuente
viva. `Task/031` **no se inicia**: nacerá de `main` tras la fusión y la normalización
`main → dev`.
