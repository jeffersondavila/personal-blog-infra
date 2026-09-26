# TASK-028 — Checkpoint de implementación local

**Fecha: 2026-09-22. Estado: En progreso.** Diseño de trabajo aceptado por el
usuario; no aprobación de Task/028. Alcance del checkpoint: implementación,
documentación y validaciones locales, sin autorización de operaciones cloud ni
publicación. [Ficha](../tasks/TASK-028-github-oidc-aws.md) ·
[Runbook no ejecutado](../runbooks/github-oidc-bootstrap.md).

## 1. Base y recuperación

Base histórica autorizada el 2026-09-21 y verificada al crear la rama el 2026-09-22:
`65fbf860a7ba47460eecad70431f0ba8f5bcfab1`. Rama de trabajo:
`Task/028-GitHub-OIDC-AWS`, nacida exclusivamente de main limpio/actualizado.
La comprobación inmediata dio HEAD = main = origin/main = base.

En la recuperación del 2026-09-22, antes de editar: misma rama/base, staging
vacío, cero commits main..HEAD. `git ls-remote --heads` no encontró la rama Task
remota; consulta de PR de ese head, todos los estados, devolvió lista vacía.
Backend/frontend estaban limpios en main. No se recreó rama, cambió de rama,
hizo reset ni descartó trabajo.

Estas son observaciones fechadas; Git/GitHub son la fuente viva. No se infiere
ausencia histórica universal de pushes de terceros: **el agente no hizo push**.

## 2. Implementación entregada

Root Terraform independiente `bootstrap/github-oidc/`; CLI 1.16.2, provider AWS
6.64.0 y lock copiado sin alterar desde el root aprobado. No se modificó
`terraform/`, el grafo Task/025 ni código backend/frontend.

| Área | Implementación |
| --- | --- |
| Backend | local parcial; runbook exige path/TF_DATA_DIR externos privados; plan-check vincula metadata/backend al estado esperado |
| Destino | cuenta explícita, región comercial, allowed_account_ids e identidad humana PersonalBlogAdministrator |
| Rol | PersonalBlogGitHubOidcValidation, path /, MaxSessionDuration 3600; cero managed/inline policies; prevent_destroy |
| Provider A | ausencia solo ante NoSuchEntity; recurso administrado, prevent_destroy |
| Provider B | URL GitHub exacta + client list exacta sts.amazonaws.com; solo data source, sin import/ownership |
| Provider C | discrepancia/lectura indeterminada: STOP, sin arreglos ni imports |
| Continuación A | ARN/dirección en estado custodiado conservan ownership; no se reclasifica como compartido B |
| Rol preexistente | sin estado correspondiente: STOP, no adopción silenciosa |
| Guardas | rutas fuera de Git, permisos privados POSIX, variables/phase/expiry, trust exacta, cero policies, planes limitados, errores saneados |
| Automatización | no hay apply, import, destroy ni cambios GitHub implementados en scripts |

No se observó A/B/C en AWS durante este checkpoint: solo fixtures/mocks locales.
El futuro inventario registra el caso real y la propiedad por separado.

## 3. Trust implementada

Principal federado único:
`arn:aws:iam::<CUENTA>:oidc-provider/token.actions.githubusercontent.com`.
Action única `sts:AssumeRoleWithWebIdentity`, aud exacta `sts.amazonaws.com`.

- Temporal explícita: sub
  `repo:jeffersondavila@60154716/personal-blog-infra@1313255836:ref:refs/heads/Task/028-GitHub-OIDC-AWS`;
  DateLessThan aws:CurrentTime literal obligatorio, futuro y máximo dos horas.
- Final por defecto: sub
  `repo:jeffersondavila@60154716/personal-blog-infra@1313255836:ref:refs/heads/main`,
  sin caducidad y sin entrada Task.

Sin wildcards, repo genérico ni environments. La producción usa plantimestamp
solo para **validar** el literal; nunca genera/renueva la caducidad. El test mock
positivo sí crea un valor sintético relativo a su reloj, limitado al archivo de tests.
El plan-check permite la transición Task → main, no renovación/reapertura automática.

## 4. Workflows

`verify-aws-oidc.yml`: push exclusivamente Task/028 y workflow_dispatch de main,
con comprobaciones de repositorio/owner ID/ref/evento; sin PR, dev ni tags.
Permisos globales vacíos; job de federación solo contents:read + id-token:write,
otro sin id-token. Checkout fijado por SHA, sin credenciales Git persistidas.
Timeouts 3/5 minutos; sesiones STS 900 s. Sin artifacts ni secretos AWS.

`security/oidc-validation.json` expresa la expectativa de Task (SUCCESS inicialmente,
DENIED cuando se autorice la segunda publicación futura). Main exige SUCCESS.
El script comprueba claims sin imprimirlos, STS valida firma, GetCallerIdentity
valida cuenta/rol y ListRoles exige AccessDenied. Audiencia incorrecta exige
InvalidIdentityToken; un fallo arbitrario no cuenta como evidencia.

**CI Infra sí quedó actualizado**, con un paso offline que verifica lock versionado,
fmt -check -recursive del bootstrap, init -backend=false -input=false -lockfile=readonly,
validate, test mock y tests/oidc. Conserva contents:read, sin id-token ni AWS real.
Las pruebas OIDC incluyen controles estáticos del workflow y seguridad. No se
ejecutó ningún workflow remoto.

## 5. Pruebas y gates locales

Evidencia histórica de la primera ejecución: 35 tests OIDC, OK con un skip POSIX
en Windows. En la recuperación se repitieron validate y los ocho tests Terraform
originales: **8 passed / 0 failed**, antes de ampliar la cobertura.

| Gate final | Resultado y alcance |
| --- | --- |
| Terraform fmt -check -recursive | PASS, root bootstrap |
| Terraform init -backend=false -input=false -lockfile=readonly | PASS; descarga/uso del provider, sin inicializar backend ni AWS |
| Terraform validate | PASS |
| Terraform test | **9 passed / 0 failed**, provider mock, todos command=plan |
| OIDC Windows | **38 tests: 37 PASS + 1 skip POSIX esperado** |
| OIDC Linux | **38/38 PASS**, contenedor local sin red, mount solo lectura; cero skips |
| tests/security | **64/64 PASS** |
| tests/laboratorio | **176/176 PASS** |
| actionlint | **1.7.12 PASS**, ambos workflows; archivo y ejecutable verificados |
| Parser YAML | **2 workflows PASS**, PyYAML 6.0.3 temporal; eventos/permisos/acciones/gates comprobados |
| Python compile | **35 archivos PASS**, sin escribir bytecode |
| git diff --check | PASS |
| Conteo canónico de tareas | **41 = 27 Aprobadas + 1 En progreso + 13 Pendientes** |
| Conteo índice decisiones | **21 = 10 Resueltas + 11 Abiertas** |
| Gitleaks / enlaces / criterio 12 | Resultado final registrado en §11 |

Pruebas añadidas: provider A/B/C e inconcluso; ownership/rol previo; identidad
humana/destino erróneos; rutas privadas y POSIX; temporal válida, ausente, vencida,
excesiva y main con caducidad; planes create/transición y rechazo de permisos,
imports, destroy/replacement, destinos/endpoints/datos desconocidos; contextos
GitHub válidos y forks/PR/dev/tags inválidos; exactitud de errores negativos;
sanitización y ausencia de credenciales en argumentos.

Herramientas de seguridad reutilizadas, sin actualizar versiones:

- Actionlint Windows zip SHA-256:
  `6e7241b51e6817ea6a047693d8e6fed13b31819c9a0dd6c5a726e1592d22f6e9`.
- Gitleaks **8.30.1**, Windows zip SHA-256:
  `d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e`.

Se comprobó también que cada ejecutable coincide byte a byte con el miembro del
zip validado. PyYAML está solo bajo tmp ignorado, sin dependencia nueva de producto.
No se repitió build/escaneo de imágenes S-09: imágenes, digests, Dockerfiles,
baseline y comparadores no se modificaron. Sus regresiones unitarias sí pasaron.
No se ejecutó ciclo Terraform de aplicación, emulador ni AWS.

## 6. Incidencias corregidas

1. Auditoría detectó que una respuesta vacía del proveedor podía convertirse en
   ausencia por truthiness; corregido a identidad `is None`, con regresión.
2. Terraform representa unknowns de listas como `[false]`: una comprobación
   booleana simple bloqueaba incorrectamente client_id_list conocido. Detectado
   inspeccionando planes **mock** reales; evaluación recursiva y regresión positiva
   [false]/negativa [true].
3. Se reforzó binding del plan a variables, provider sin endpoints alternativos y
   backend privado; rechazo de expressions que pudieran conceder políticas.
4. Vista rápida STATUS aún presentaba Task/028 como próxima/Pendiente después de
   la primera reconciliación; corregida sin alterar entradas históricas.

`tmp/task028/reconcile.py` cumplió su función y fue **eliminado** al continuar.
No forma parte de entregables ni se convirtió en código de producto.

## 7. Reconciliación documental

**D-06 Resuelta y Vigente desde Task/025 (2026-09-14)**; corregidos drift vigente
de PROJECT_INSTRUCTIONS, target-production-architecture y riesgo STAGE-08.
D-06 retirada de la tabla vigente de decisiones abiertas. Contadores STATUS /
open-decisions ahora 11 abiertas y 10 resueltas, concordantes con el índice.
Mecanismo resuelto no significa bucket materializado; referencias históricas de
Task/005 y Task/025 preaprobación permanecen como historia.

**STAGE-09:** Task/028 En progreso; federación/autenticación real pendiente,
sin atribuir permisos de despliegue al rol validador. Task/038 define mínimos
backend, Task/039 Terraform y Task/040 validación integral. Main protegida antes
de esos roles efectivos, fuera de Task/028. Avance sigue **27/41 ≈ 66 %** y
ETAPA 09 **1/3 ≈ 33 %**.

**STAGE-10 / Task/030:** reutilización Task/025 para aplicación conservada.
Excepción explícita del bootstrap D-06: bucket exclusivo de estado, privado,
versionado, cifrado, public access block, use_lockfile=true, sin DynamoDB,
separado de medios/backups; migración OIDC por init -migrate-state y custodia/
migración del estado del propio bootstrap. El backend debe preexistir al grafo
que inicializa; no duplica el grafo de aplicación. ROADMAP y D-06 asignan lo mismo.
La ficha Task/030 recogerá estos entregables al abrirse; no se inició esa tarea.

**EX-028-C7:** solo root OIDC, local externo protegido, 0700/0600, un escritor/lock,
snapshots antes/después y tras fallo, backups cifrados externos recuperados de
prueba; revisión 30 días desde creación cloud, extinción Task/030 antes del primer
apply de aplicación. No autoriza cloud ni es PASS literal de C-7.

## 8. DoD y límites de evidencia

| Criterios | Evaluación del checkpoint |
| --- | --- |
| General 1 y tarea CI ejecutada remotamente | Pendientes: federación real/publicaciones/postmerge no autorizados |
| General 2–11 | Entrega local acotada, sintaxis/pruebas/docs/riesgos/secretos revisados; base main demostrada |
| General 12 | Auditoría dirigida en §11; historia fechada o reglas duraderas |
| C-1 | PASS local |
| C-2/C-3 | Guardas implementadas/probadas offline; ejecución real pendiente |
| C-4 | Planes mock verificados; **plan AWS pendiente**, no PASS real |
| C-5/C-6 | Diferenciación explícita; paridad actualizada sin marcar AWS validado |
| C-7 | EX-028-C7, **no cumplimiento literal** |
| C-8 | Ningún recurso creado en este checkpoint |
| C-9 | Inventario real pendiente; recursos creados por este trabajo: cero |
| C-10 | Estimación IAM/STS y fuentes actuales en runbook; sin servicios de aplicación |
| C-11 | Ningún secreto versionado ni credencial AWS real utilizada |

Pruebas locales no demuestran federación AWS. Evidencia real exigida: cero
managed policies, cero inline policies, trust exacta, GetCallerIdentity correcto y
operaciones negativas elegidas con AccessDenied. **No prueban universalmente que
ninguna resource-based policy de la cuenta otorgue alguna capacidad**. El inventario
de esas policies del script está vacío; toda inspección adicional se acota al
inventario realmente comprobado.

## 9. Riesgos y autorizaciones futuras

Riesgos abiertos: custodia y pérdida de estado local; proveedor compartido;
discrepancias AWS/mocks; cambios de subject GitHub; sesiones emitidas que sobreviven
a cambios de trust; políticas de recursos no inventariadas; main sin protección;
caducidad temporal durante pruebas; recovery real todavía no ejecutado.

**AWS requiere autorización posterior:** abrir CloudShell/sesión humana; lecturas
autenticadas/inventario; copias privadas/recuperación; plan real; apply de recursos
A/rol o solo rol B; transición trust main; readback; contingencias/revocación si
fueran necesarias. Task/030 necesita autorización propia para S3/migración.

**GitHub/Git requieren autorización posterior:** tres variables no secretas, cada
commit/push de las dos publicaciones premerge, ejecuciones de verificación, PR,
merge humano y reconfirmación postmerge desde main. No cambiar subject, crear
secrets AWS ni convertir el validador en rol de despliegue.

Secuencia futura: publicación Task SUCCESS con trust temporal → transición humana
main → segunda publicación Task DENIED con JWT nuevo → después del merge,
main SUCCESS obligatorio. **Ninguna publicación se preparó o ejecutó aquí**.
No se solicita autorización de apply en este checkpoint.

## 10. Inventario y Git del checkpoint

La captura final de §11 contiene status completo, diff --stat y lista de archivos
nuevos. `git diff --stat` convencional **no incluye archivos untracked**; estos
se enumeran aparte sin staging.

## 11. Evidencia final

Captura del **2026-09-22**, después de la implementación y los gates. La tarea
continúa **En progreso**, todo sin commit y sin staging.

**Gitleaks 8.30.1: cero hallazgos**, sobre copia del worktree de todos los
247 archivos tracked/no ignorados, incluidos los nuevos; no se incluyeron
temporales ignorados ni archivos privados. Búsqueda dirigida de claves privadas,
PAT, access keys y JWT: cero coincidencias. No es una auditoría universal de
secretos externos o archivos ignorados del usuario.

**Enlaces: PASS**, AST Markdown (fences/inline code excluidos), 15 documentos
tocados, 520 enlaces: 500 relativos/anclas comprobados, cero rotos; 20 URLs
externas inventariadas, sin afirmar disponibilidad HTTP de todas.

**Criterio 12: PASS**, búsqueda dirigida y revisión de contexto/diff: menciones
nuevas a ramas/PR/publicaciones son reglas del procedimiento o capturas fechadas;
no se declara un trámite Git/GitHub como condición viva de una tarea futura.
La cabecera de consolidación Task/027 se identifica como historia; las referencias
Task/005 y Task/025 preaprobación no se reescribieron. La búsqueda de D-06 abierta
en pasajes vigentes no dejó coincidencias; el hallazgo de STATUS dentro de historia
Task/005.3 se conservó deliberadamente.

La guarda aceptó además los resource_changes realmente emitidos por Terraform
mock para casos A/B, con envelope sintético de variables/configuración; esto
comprueba el formato de unknowns, **no un plan AWS real**.

**Inventario completo: 14 modificados + 18 nuevos = 32 archivos.**
`M` = modificado sin staging; `??` = nuevo sin tracking. La captura usa
`git status --short --untracked-files=all` para enumerar cada archivo:

```text
 M .github/workflows/ci-infra.yml
 M .gitignore
 M docs/architecture/aws-local-parity.md
 M docs/architecture/open-decisions.md
 M docs/architecture/security-boundaries.md
 M docs/architecture/target-production-architecture.md
 M docs/claude/PROJECT_INSTRUCTIONS.md
 M docs/project-management/ROADMAP.md
 M docs/project-management/STATUS.md
 M docs/runbooks/README.md
 M docs/stages/STAGE-08-cloud-ready.md
 M docs/stages/STAGE-09-cloud-accounts.md
 M docs/stages/STAGE-10-cloud-deployment.md
 M docs/stages/STAGE-11-deployment-automation.md
?? .github/workflows/verify-aws-oidc.yml
?? bootstrap/github-oidc/.terraform.lock.hcl
?? bootstrap/github-oidc/main.tf
?? bootstrap/github-oidc/outputs.tf
?? bootstrap/github-oidc/providers.tf
?? bootstrap/github-oidc/tests/identity.tftest.hcl
?? bootstrap/github-oidc/variables.tf
?? bootstrap/github-oidc/versions.tf
?? docs/runbooks/github-oidc-bootstrap.md
?? docs/task-reports/TASK-028-report.md
?? docs/tasks/TASK-028-github-oidc-aws.md
?? scripts/oidc/__init__.py
?? scripts/oidc/bootstrap.py
?? scripts/oidc/guards.py
?? scripts/oidc/verify.py
?? security/oidc-validation.json
?? tests/oidc/test_guards.py
?? tests/oidc/test_verify.py
```

`git diff --stat=120`, completo para archivos tracked; los 18 nuevos de arriba
quedan fuera por semántica de Git, sin añadirlos al staging:

```text
 .github/workflows/ci-infra.yml                      | 11 +++++++++++
 .gitignore                                          |  5 +++++
 docs/architecture/aws-local-parity.md               | 17 +++++++++++++++--
 docs/architecture/open-decisions.md                 | 28 +++++++++++++++++++++++++---
 docs/architecture/security-boundaries.md            | 21 ++++++++++++++++++++-
 docs/architecture/target-production-architecture.md |  5 +++--
 docs/claude/PROJECT_INSTRUCTIONS.md                 |  9 ++++++---
 docs/project-management/ROADMAP.md                  | 24 +++++++++++++++++++-----
 docs/project-management/STATUS.md                   | 30 ++++++++++++++++++++++--------
 docs/runbooks/README.md                             |  2 ++
 docs/stages/STAGE-08-cloud-ready.md                 |  4 ++--
 docs/stages/STAGE-09-cloud-accounts.md              | 26 ++++++++++++++++++++++----
 docs/stages/STAGE-10-cloud-deployment.md            | 24 +++++++++++++++++++++---
 docs/stages/STAGE-11-deployment-automation.md       | 10 ++++++++--
 14 files changed, 181 insertions(+), 35 deletions(-)
```

Comprobaciones finales fechadas:

| Comprobación | Resultado |
| --- | --- |
| Rama | Task/028-GitHub-OIDC-AWS |
| HEAD / main / origin/main | Los tres = 65fbf860a7ba47460eecad70431f0ba8f5bcfab1 |
| git diff --cached --name-only / --stat | Salida vacía |
| git rev-list --count main..HEAD | 0 |
| Rama Task/028 remota | Sin referencia en ls-remote |
| PR del head Task/028, todos los estados | Lista vacía |
| Acciones del agente | Cero commit, push, PR, mutaciones AWS y cambios de configuración GitHub |
| reconcile.py | Retirado; Test-Path = False |
| Backend | main, porcelain vacío, HEAD 4a40364bbd6a444f9469b815d17d2d77a37949ce |
| Frontend | main, porcelain vacío, HEAD 7dce98aff239d61ae3ae15213d9a3f5ebf0fb8ce |
| Terraform aplicación / imágenes / baseline | Sin cambios |

**Detención en checkpoint.** No se abrió CloudShell ni se solicitaron credenciales
o autorización para apply. Las dos publicaciones y reconfirmación main permanecen
como procedimiento futuro, sin preparar ni ejecutar.

## 12. Checkpoint AWS real de solo lectura y plan (2026-09-24)

Fase ejecutada bajo autorización acotada a **solo lectura AWS + plan**: inventario
real, recuperación cifrada verificada, `init`, `plan`, `show` y la guarda oficial
`plan-check`. **Task/028 continúa En progreso.** Esta sección registra evidencia
fechada; Git, GitHub y AWS son la fuente viva de su estado.

| Evidencia | Resultado |
| --- | --- |
| Caso realmente observado en AWS | `INVENTORY_OK case=A ownership=A` |
| Terraform / provider AWS | **1.16.2** / **6.64.0** |
| `terraform plan` / `show` | `TERRAFORM_PLAN_OK=true` · `TERRAFORM_SHOW_OK=true` |
| Guarda oficial | `PLAN_CHECK_RC=0` |
| Cambios administrados | `MANAGED_CHANGE_COUNT=2` |
| `aws_iam_openid_connect_provider.github[0]` | `actions=["create"]` |
| `aws_iam_role.validation` | `actions=["create"]` |
| Mutaciones AWS | `AWS_MUTATIONS=0` |
| Apply | `APPLY_EXECUTED=false` |
| Cierre de la fase | `PLAN_PHASE_COMPLETE=true` · `FINAL_RC=0` |

Digests de la revisión, no secretos:

```text
plan JSON  d2cb84f13c4a83e105bcf4804796572361f7332f336f942ab716f972d108d2cf
plan bin   f36914411a3dea4d479ffc6bb8aa035de743fa29c509508c7a2d519d4784b008
```

**Cualquier apply futuro debe consumir exactamente el plan binario anterior.** El
plan no se regenera en silencio: un plan nuevo produce otro digest y exige otra
revisión humana.

La custodia cifrada quedó verificada **antes** de este plan: snapshot cifrado,
copia independiente en almacenamiento cloud controlado por el usuario, descarga de
vuelta con digest idéntico y **descifrado real** en CloudShell con verificación del
tar contra su referencia y de su contenido contra `SHA256SUMS`. Un intento anterior
en Windows quedó invalidado por un defecto de ejecución, se conservó marcado como
inválido y **no se usa como evidencia**.

### 12.1 Desviaciones operativas registradas

1. El inventario anterior superó el límite de 600 segundos y **se refrescó
   inmediatamente antes del plan**, conforme al runbook §5.
2. Por falta de espacio en CloudShell, los artefactos pesados de Terraform usaron un
   `TF_DATA_DIR` temporal bajo `/tmp`, fuera de todo checkout Git. No cambió el
   estado objetivo, el backend vinculado ni el plan final, y `plan-check` verificó
   la vinculación del backend. **Ese directorio es efímero**: una sesión reciclada
   obliga a repetir `init` antes de consumir el plan revisado, sin regenerarlo.
3. CloudShell recicló su entorno durante el trabajo y revirtió GnuPG a la variante
   mínima; hubo que reinstalar la completa para descifrar. Es una propiedad del
   entorno, no del procedimiento.

### 12.2 Qué no se ejecutó

Apply, creación o modificación de recursos AWS, cambios IAM fuera del plan,
configuración de variables en GitHub, publicación de la rama, ejecución real de
OIDC, commit, push, PR y merge. Ninguna de esas operaciones estaba autorizada.

### 12.3 Gates pendientes antes de *Lista para validación*

| # | Gate | Estado |
| --- | --- | --- |
| G-1 | Ventana de la caducidad temporal todavía abierta al aplicar y al federar | **Verificación obligatoria previa** |
| G-2 | Apply del plan revisado `f3691441…` | No autorizado |
| G-3 | Readback post-apply `inventory --aws-real --verify-target` | Pendiente |
| G-4 | Snapshot, cifrado, copia externa y recuperación **posteriores** a la mutación | Pendiente |
| G-5 | Plan posterior sin cambios | Pendiente |
| G-6 | Relectura de la configuración OIDC del repositorio | Pendiente |
| G-7 | Tres variables no secretas del repositorio | Pendiente |
| G-8 | Primera publicación premerge con expectativa `SUCCESS` | No autorizada |
| G-9 | Transición de trust Task → main con su propio plan y readback | Pendiente |
| G-10 | Segunda publicación premerge con expectativa `DENIED` y JWT nuevo | No autorizada |
| G-11 | Fecha de revisión de EX-028-C7 a 30 días de la primera creación cloud | Se fija al aplicar |
| G-12 | Repetición de gates locales tras los cambios documentales | Pendiente |

La reconfirmación postmerge mediante `workflow_dispatch` desde main es posterior al
merge humano y, por tanto, **posterior a la aprobación**: no la condiciona. Sigue
siendo obligatoria antes de dar por integrada Task/028 y de avanzar a la tarea
siguiente, y si falla el avance se detiene para corregir Task/028.

### 12.4 Restricción crítica de la caducidad

La trust temporal del plan revisado incorpora un literal `DateLessThan` **de un
máximo de dos horas** desde su elección. La guarda
[`plan_check`](../../scripts/oidc/guards.py) solo admite actualizar la trust del rol
en la transición **Task → main**: no existe camino admitido para renovar la
caducidad de un rol ya creado, y `prevent_destroy` impide recrearlo. En
consecuencia, el apply y la primera federación real con éxito deben ocurrir
**dentro de la misma ventana**. Si vence antes, el runbook §6 obliga a detenerse y
abrir una revisión y autorización nuevas; no se renueva automáticamente.

## 13. Primera federación real (2026-09-24)

Ejecutado bajo autorización acotada: apply del plan revisado, readback, copia local
posterior a la mutación, publicación de la rama y primera ejecución premerge.
**La tarea sigue En progreso.** Evidencia fechada; AWS, Git y GitHub son la fuente
viva de su estado.

### 13.1 Apply y readback

| Evidencia | Resultado |
| --- | --- |
| Caducidad al iniciar | `EXPIRY_WINDOW_VALID=true`, 2384 s restantes |
| Plan consumido | digest `f3691441…84b008`, **el revisado**, sin regenerar |
| Terraform | 1.16.2, `TF_DATA_DIR_MODE=reinit`, `BACKEND_BINDING_OK=true` |
| Apply | `APPLY_RC=0` |
| Readback `--verify-target` | `INVENTORY_OK case=B ownership=owned-A` |
| Copia local posterior | `20260924T034243Z`, tar `3c51a14a…d66b4` |

`case=B ownership=owned-A` es la **continuación de A** definida en el runbook §3: tras
crear el proveedor, `GetOpenIDConnectProvider` ya devuelve documento, y `owned-A`
acredita que el estado custodiado lo posee. **No** es un proveedor compartido y no se
reclasifica. El readback con `--verify-target` comprobó además trust exacta contra
`trust(config)`, cero políticas gestionadas, cero inline y ausencia de permissions
boundary.

### 13.2 C-9 — recursos realmente creados frente a lo planificado

**Creados: exactamente 2.** Coinciden uno a uno con el plan revisado; ningún tercer
recurso, ningún import, ningún reemplazo.

| Dirección | Recurso | Propiedades verificadas en el readback |
| --- | --- | --- |
| `aws_iam_openid_connect_provider.github[0]` | Proveedor IAM OIDC de GitHub | url `https://token.actions.githubusercontent.com`, client list exactamente `["sts.amazonaws.com"]` |
| `aws_iam_role.validation` | Rol `PersonalBlogGitHubOidcValidation` | path `/`, MaxSessionDuration 3600, **0 managed**, **0 inline**, sin permissions boundary, trust exacta |

### 13.3 Primera ejecución premerge

Commit publicado `9afb469`. Ambos workflows en verde el 2026-09-24:
`Verify AWS OIDC` run `35952961378` **success** (03:48:11 → 03:48:30 UTC) y
`CI Infra` run `35952961379` **success**.

Evidencia impresa por el verificador, literal:

```text
GitHub job without id-token: token request unavailable (GitHub-side evidence)
GetCallerIdentity: expected account and role
iam:ListRoles: AccessDenied (scope: this operation only)
Wrong audience: InvalidIdentityToken (provider/trust chain)
```

Esas líneas solo se emiten si pasan las guardas correspondientes: federación STS con
JWT genuino, identidad exacta de cuenta y rol asumido, `iam:ListRoles` con
`AccessDenied` **exacto** y un segundo JWT de audiencia incorrecta con
`InvalidIdentityToken` **exacto**. Un fallo arbitrario no habría contado como
evidencia negativa.

Barrido del log completo: **0 JWT**, **0 access keys AWS**, **0 campos de credencial
STS**, **0 STOP**. El run de evidencia **no se borra ni se altera**.

Límite que esto **no** demuestra: nada sobre las resource-based policies de la cuenta.
El inventario de esas policies sigue vacío y `AccessDenied` en `ListRoles` caracteriza
esa operación, no toda AWS.

### 13.4 D-028-A — identificadores no secretos en logs públicos

Hallazgo de la ejecución real: GitHub vuelca el bloque `env:` del job y **las
variables de Actions no se enmascaran**, a diferencia de los secrets. En un
repositorio público eso deja visibles el Account ID y el ARN del rol. El verificador
no los imprime; la exposición procede del propio runner.

**Decisión del usuario, aceptada el 2026-09-24:** son identificadores, no
credenciales. Se acepta la exposición, **no** se convierten en secrets y **no** se
rediseña el workflow. Se mantiene íntegra la prohibición sobre JWT, access keys,
secret access keys y session tokens. La promesa contraria del runbook §7 quedó
corregida.

### 13.5 EX-028-C7 — fecha de revisión

Primera creación cloud: **2026-09-24**. Revisión a 30 días: **2026-10-24**. La
extinción sigue siendo de Task/030, antes del primer apply de infraestructura de
aplicación.

### 13.6 Convergencia real demostrada

Tras el apply, un `refresh-only` **acotado y validado antes de aplicarse** normalizó
dos atributos calculados que AWS devuelve vacíos: `tags` y `tags_all` de ambos
recursos, de `null` a `{}`. No tocó trust, políticas ni ownership.

Con el estado ya normalizado, Terraform acredita la convergencia por sí mismo:

```text
CONVERGE_PLAN_RC=0        # plan -detailed-exitcode: sin cambios
RESOURCE_DRIFT_COUNT=0    # sin drift detectado
```

**`plan-check` no es el gate de convergencia.** Es la puerta **previa al apply**, y
`plan_check` revalida la ventana de caducidad en cada ejecución
([guards.py:158](../../scripts/oidc/guards.py)). Una vez vencido el literal temporal
rechaza con `EXPIRY_WINDOW` **cualquier** plan de fase task, incluido uno que no
cambia nada. Es comportamiento deliberado, no un defecto: un literal muerto no debe
poder aplicarse. Se reprodujo localmente que el mismo plan convergente **sí** se
acepta mientras el literal está vigente, y quedaron cuatro regresiones que fijan
ambos lados del contrato, además de que la convergencia no relaja el rechazo de
políticas y de que el `url` del proveedor debe conservar su esquema.

### 13.7 Consecuencia operativa

El wrapper privado `recover-plan` **ya no puede volver a ejecutarse**: su `setup()`
exige que el estado no exista (`STATE_PREEXISTING`) y el estado ya existe. Las
operaciones restantes usan los comandos del runbook §5 más la guarda oficial
`plan-check`.

## 14. Segundo entorno de operación (2026-09-24)

El flujo exigía Linux (`EXPLICIT_AWS_CLOUDSHELL_REQUIRED`), lo que ataba toda
operación AWS a CloudShell. Se añadió la **estación Windows** como segundo entorno
explícito, sin relajar ninguna guarda.

| Guarda nueva | Efecto |
| --- | --- |
| `UNSUPPORTED_PLATFORM` | solo `linux` y `win32`; cualquier otro se rechaza |
| `CLOUDSHELL_PROFILE_FORBIDDEN` | en CloudShell un perfil nombrado se rechaza: elegiría otra identidad |
| `LOCAL_PROFILE_REQUIRED` | en Windows `--aws-profile personal-blog` es obligatorio |
| `IMPLICIT_PROFILE` | `AWS_PROFILE`/`AWS_DEFAULT_PROFILE` heredados se rechazan |
| `STATIC_CREDENTIALS` | claves de larga vida rechazadas; de sesión solo con su token |
| `WINDOWS_PRIVATE_ROOT` | rutas privadas bajo `%LOCALAPPDATA%` |
| `PATH_REPARSE` | junctions y symlinks rechazados en Windows |

El perfil viaja como argumento explícito a cada llamada `aws`; nunca por entorno.
Identidad humana, destino de cuenta, rechazo de root, estado, trust, proveedor,
políticas y la prohibición de destroy/import/target son **idénticos** en ambos
entornos: lo que cambia es dónde se opera, no qué se permite.

**Dos límites declarados, no disimulados.** En Windows la guarda de privacidad es
de *ámbito* —directorio bajo `%LOCALAPPDATA%` y ausencia de reparse point—, no una
auditoría de ACL; la ACL sigue siendo responsabilidad del operador. Y el código **no
prueba** que el perfil `personal-blog` se alimente de `aws login`: determinarlo
exigiría leer credenciales o la caché de sesión, prohibido por diseño. Lo que sí
queda demostrado es que la identidad efectiva es una **sesión STS asumida** de
`PersonalBlogAdministrator`; una clave IAM de larga vida produce un ARN
`iam::…:user/…` y la guarda de identidad la rechaza, con su regresión.

**El estado de Terraform no se duplica.** Sigue siendo único y vive donde se creó;
el segundo entorno no lo copia ni lo migra (D-028-B).

Cobertura: `tests/oidc/test_local_env.py`, 20 pruebas — entornos, perfil explícito,
perfil heredado, claves de larga vida, root, principal inesperado, cuenta
equivocada, ausencia de material de credencial en la línea de comandos, y que
CloudShell sigue comportándose exactamente igual.

## 15. Defecto PLAN_PROVIDER en la transicion (2026-09-25)

El primer intento de transicion Task → main se detuvo en `STOP_PHASE=PRE_APPLY` con
`PLAN_PROVIDER`. **No hubo apply, ni mutacion AWS, ni refresh-only**: el estado
quedo intacto.

### 15.1 Causa

Dos partes del mismo codigo discrepaban sobre la representacion canonica del URL del
proveedor. `provider_case` aceptaba **ambas** —con y sin esquema—, tal y como el
runbook §3 ya declaraba, pero `plan_check` exigia literalmente `https://…`:

```python
require(after.get("url") == f"https://{HOST}" and …, "PLAN_PROVIDER")
```

En el plan de **creacion** el valor procedia de la configuracion y llevaba esquema,
asi que paso. En el plan de **transicion** el proveedor es `no-op` y su `after`
procede del estado refrescado, es decir de lo que devuelve IAM.

### 15.2 Evidencia real, no supuesta

`GetOpenIDConnectProvider` contra la cuenta real, el 2026-09-25:

```text
Url            = 'token.actions.githubusercontent.com'   # sin esquema
ClientIDList   = ['sts.amazonaws.com']
Tags           = []
```

El proveedor AWS 6.64.0 suprime la diferencia de esquema al comparar, por eso
Terraform lo considera `no-op`, pero conserva el valor que IAM devuelve. La guarda
rechazaba un plan correcto.

### 15.3 Correccion

Un helper explicito, `provider_url_ok`, compara **semanticamente** ese unico campo:
el host debe ser exactamente `token.actions.githubusercontent.com`, el prefijo
`https://` es opcional y **nada mas pasa** —ni `http://`, ni puerto, ni ruta, ni un
host que lo contenga como sufijo—. `provider_case` reutiliza el mismo helper, de modo
que ahora existe una sola definicion.

Lo demas de `PLAN_PROVIDER` no se toca: `client_id_list` exactamente
`["sts.amazonaws.com"]`, cero tags, cero `tags_all`, proveedor en `create` o `no-op`
y sin valores desconocidos.

**Una prueba anterior codificaba la expectativa equivocada** —exigia el esquema— y se
sustituyo por tener un error demostrado: la ejecucion real la refuto y la API de IAM
confirmo la representacion. Quedan tres regresiones: ambas representaciones aceptadas,
nueve formas rechazadas y el helper probado aisladamente.

### 15.4 Entorno local verificado

| Comprobacion | Resultado |
| --- | --- |
| Identidad AWS local | `assumed-role/PersonalBlogAdministrator/…`, sin root ni usuario IAM |
| Terraform `windows_amd64` | 1.16.2, zip verificado contra el `SHA256SUMS` oficial de HashiCorp |
| `init -backend=false -lockfile=readonly` | PASS; **el lock no cambio** |
| `fmt -check -recursive` / `validate` / `test` | PASS / PASS / **9 passed, 0 failed** |
| API de CloudShell en la CLI | **no existe**: sus operaciones son internas de la consola |

## 16. Cutover de custodia y transicion a trust main (2026-09-25)

### 16.1 Cambio de custodia, no segundo estado

El estado autoritativo vivia en el HOME de CloudShell us-east-2, lo que ataba cada
operacion a esa consola. **No existe ruta oficial** para recuperarlo por API: la CLI
v2.37.1 no expone el servicio `cloudshell` —`ParamValidation: invalid choice`, cero
modelos botocore— porque `DescribeEnvironments` y `GetFileDownloadUrls` son API
interna de la consola. El archivo se transfirio por la interfaz, en una sola accion.

Lo transferido fue `pre-main-20260925T145118Z.tar`, creado **antes** del intento que
se detuvo en `PRE_APPLY`, de modo que contiene el estado previo a cualquier posible
mutacion. Verificacion antes de usarlo:

| Comprobacion | Resultado |
| --- | --- |
| `SHA256SUMS` interno | **6/6** |
| Estado | version 4, serial 4, `terraform_version` 1.16.2, lineage presente |
| Recursos administrados | **exactamente** rol + proveedor |
| `deposed` | ninguno |
| Binding de cuenta | coincide con la sesion viva |
| `provider.lock.hcl` | **identico** al del repositorio |

El archivo original se conserva en `snapshots/` como **copia de referencia preservada
con SHA256 verificado**: no se ha implementado ninguna propiedad de inmutabilidad —ni
WORM, ni versionado, ni ACL de solo lectura—, y afirmarlo seria inexacto. La copia operativa
pasa a `%LOCALAPPDATA%/PersonalBlog/bootstrap/github-oidc/`.

**Esto es una transferencia de custodia bajo EX-028-C7, no un segundo estado activo.**
La copia que permanece fisicamente en CloudShell queda como **backup inactivo** y no
debe volver a usarse para plan ni apply: el unico escritor es ahora el local.

### 16.2 Perfil explicito tambien para Terraform

Los helpers reciben `--aws-profile personal-blog`. El proveedor de Terraform no lee
ese argumento y fallo con *No valid credential sources found*, intentando incluso el
IMDS de EC2. Se resolvio pasando el perfil **acotado a cada invocacion** de Terraform,
nunca fijado en la sesion: sigue apareciendo en el comando que se revisa, que es la
propiedad que la guarda `IMPLICIT_PROFILE` protege. `allowed_account_ids` mantiene el
binding de cuenta con independencia de eso.

### 16.3 Transicion aplicada

| Evidencia | Resultado |
| --- | --- |
| Plan de transicion | `007559b22220b9632e7f5edcda56f0d27b9b983cf5bd1d400aa420d2dc8072a5` |
| Cambios | proveedor `no-op`, rol `update`, drift 0 |
| `plan-check` | `PLAN_OK json_sha256=6a7b7e2b…065965` |
| Compuerta de transicion | `TRANSITION_OK=true`, unico atributo `assume_role_policy` |
| Revalidacion previa al apply | digest sin cambios, ambas compuertas repetidas |
| Apply | `APPLY_MAIN_RC=0` |
| Readback `--verify-target` | `INVENTORY_OK case=B ownership=owned-A` |

Lectura directa de IAM despues del apply:

```text
STATEMENT_COUNT=1          HAS_DATELESSTHAN=False
AUD=sts.amazonaws.com      SUB_ENDS_WITH=refs/heads/main
MAX_SESSION_DURATION=3600  PATH=/   PERMISSIONS_BOUNDARY=None
MANAGED_POLICIES=0         INLINE_POLICIES=0
```

### 16.4 Convergencia

```text
CONVERGE_MAIN_RC=0
RESOURCE_DRIFT_COUNT=0
aws_iam_openid_connect_provider.github[0]  no-op
aws_iam_role.validation                    no-op
```

No hubo drift de `tags`, asi que **no se ejecuto refresh-only**.

## 17. Segunda publicacion DENIED y estado de los gates (2026-09-25)

### 17.1 Rechazo demostrado

`security/oidc-validation.json` paso a `DENIED` y la rama se publico en `49fed29`.
`Verify AWS OIDC` run `36177780350`: **success**, ambos jobs en verde.

```text
GitHub job without id-token: token request unavailable (GitHub-side evidence)
Task fresh-token STS: AccessDenied (expected)
```

La segunda linea solo se imprime si STS devolvio **exactamente** `AccessDenied` con
un JWT **nuevo** pedido en esa misma ejecucion: `InvalidIdentityToken`, un token
caducado, un fallo de red o una variable ausente habrian detenido el job con
`TASK_REJECTION_REQUIRED`. GitHub sigue emitiendo token para la rama Task; quien
rechaza es STS, porque la trust ya solo acepta `refs/heads/main`.

Barrido del log: **0 JWT**, **0 access keys**, **0 campos de credencial**, **0 STOP**.

### 17.2 H-028-1 — CI Infra bloqueado por un cambio externo del registro

`CI Infra` run `36177780346` termino en **failure**, y no por Task/028.

**Los 23 gates anteriores pasaron**, incluidos todos los que esta tarea toca:
Terraform `fmt`/`init`/`validate`, validacion estatica OIDC y planes mock, compilacion
Python, Compose, comparador de baseline y **Gitleaks sobre el historial completo**.

El unico paso fallido es *Build the project images*:

```text
ERROR: failed to build: unexpected status from HEAD request to
https://quay.io/v2/minio/minio/manifests/sha256:a1a8bd4a…cbaba2: 401 Unauthorized
```

Los seis pasos siguientes quedaron **skipped**, no fallidos.

Diagnostico, con evidencia:

- `git diff --name-only 9afb469..HEAD -- docker/ docker-compose.yml .github/workflows/ci-infra.yml`
  esta **vacio**: ningun commit de esta fase toca imagenes, Compose ni el workflow.
- El mismo paso paso en verde el 2026-09-24 con el mismo digest fijado.
- Sonda directa al registro: el endpoint de autenticacion responde 200 pero **no
  entrega token**, y el manifiesto devuelve `401 UNAUTHORIZED`. quay.io dejo de
  permitir el acceso anonimo a `minio/minio`.
- Un reintento de los jobs fallidos reprodujo el mismo error: **no es transitorio**.

**Fuera del alcance de Task/028.** Corregirlo exigiria cambiar el origen de la imagen
de MinIO o introducir credenciales de registro: lo primero invalidaria la procedencia
verificada de Task/027.1 y su baseline S-09, lo segundo esta prohibido. Queda
registrado como **H-028-1, abierto**, con propietario en el area de imagenes.

### 17.3 Custodia externa pendiente

Tres copias locales esperan cifrado y custodia externa con recuperacion verificada:

| Snapshot | Rol |
| --- | --- |
| `pre-main-20260925T145118Z.tar` | estado previo a la mutacion, transferido desde CloudShell |
| `local-pre-main-20260925T190328Z.tar` | copia local inmediatamente anterior al apply |
| `post-main-20260925T190328Z.tar` | **copia final autoritativa**, posterior a la transicion |

El cifrado simetrico exige una frase que el agente no debe conocer ni manejar, y el
destino externo exige una sesion de navegador. Ambas cosas son del operador.

## 18. Cierre de EX-028-C7: custodia externa con recuperacion verificada (2026-09-25)

### 18.1 Defecto propio corregido en el camino

El primer cifrado se ejecuto con `--batch`, que **suprime la confirmacion por
repeticion** de la frase simetrica. Un error de tecleo quedaba grabado sin aviso, y el
descifrado de verificacion fallo con `Bad session key`. Los tres ciphertexts quedaron
**preservados** con sufijo `.UNVERIFIABLE-20260925T2151Z` —no se borraron— y el cifrado
se repitio sin `--batch`, de modo que GnuPG exige la frase dos veces y rechaza cualquier
discrepancia. Los tres `.tar` originales se comprobaron **sin cambios** antes y despues.

Leccion aplicada: la verificacion por descifrado se hizo **en local, antes** de la
custodia externa, para no descubrir un fallo de frase despues de un viaje completo.

### 18.2 Cadena de custodia completa

| Artefacto | Rol | SHA256 del ciphertext |
| --- | --- | --- |
| `pre-main-20260925T145118Z.tar.gpg` | estado previo a la mutacion | `d08a51b3…6f2d7c1d` |
| `local-pre-main-20260925T190328Z.tar.gpg` | copia local anterior al apply | `2694da95…f8c1e923` |
| `post-main-20260925T190328Z.tar.gpg` | **copia final autoritativa** | `e6cdc1a0…101c8ec5` |

Cifrado simetrico **AES256** con frase confirmada, sin cache de clave. Los tres
descifraron en local devolviendo su `.tar` **byte a byte**. Los tres viajaron al
almacenamiento externo del operador.

### 18.3 Recuperacion real de la copia autoritativa

Descargada de vuelta desde el destino externo y verificada de extremo a extremo:

| Comprobacion | Resultado |
| --- | --- |
| SHA256 del ciphertext recuperado | **identico** a `e6cdc1a0…101c8ec5` |
| Descifrado GnuPG | correcto |
| SHA256 del tar recuperado | **identico** a `cd4a735d…c169ab23` |
| `SHA256SUMS` interno | **6/6** |
| Estado | version 4, serial 6, lineage **coincide** con el operativo |
| Recursos administrados | **exactamente** rol + proveedor |
| `deposed` | ninguno |
| Binding de cuenta | correcto |
| Trust del estado recuperado | **main-only, sin `DateLessThan`** |

El plaintext temporal de verificacion se retiro; los `.tar` locales se conservan.

**EX-028-C7 queda satisfecha en su exigencia de custodia:** copias antes y despues de
cada mutacion, cifradas, fuera del equipo y con recuperacion **demostrada**, no
supuesta. Su revision sigue fijada al **2026-10-24** y su extincion sigue siendo de
Task/030, antes del primer apply de infraestructura de aplicacion.

### 18.4 Estado de la tarea

**Task/028 — Lista para validacion.**
**Bloqueo externo para integracion/merge: H-028-1.**

La implementacion esta completa y verificada contra AWS y GitHub reales. `CI Infra`
sigue en rojo por el cambio de politica de quay.io sobre la imagen de MinIO: **no se
oculta ni se minimiza**, y debera resolverse fuera del alcance de Task/028 antes de
considerar sano el pipeline de integracion. No se ha creado pull request, no se ha
fusionado nada y `dev` no se ha tocado.

## 19. H-028-1: causa raiz del fallo de `CI Infra` (2026-09-26)

Por decision del usuario, H-028-1 se resuelve **dentro de Task/028**. La tarea vuelve a
**En progreso** hasta recuperar `CI Infra` en verde. Nada de AWS, OIDC, estado o
custodia se reabre.

### 19.1 Evidencia recogida

| Sonda | Resultado |
| --- | --- |
| `quay.io` token anonimo para `minio/minio` | **emitido** (200) |
| `quay.io` manifiesto por tag y por digest | **401 UNAUTHORIZED** en ambos |
| `quay.io` API del repositorio `minio/minio` | **401** *Requires authentication* |
| `quay.io` API del namespace `minio`, repos publicos | **69 publicos**, y `minio/minio` **no esta** entre ellos |
| Namespace `minio` hoy | publica la linea comercial `aistor/*` (28 repos) |
| Docker Hub `minio/minio` | **404** *object not found* |
| `registry.min.io/minio/minio` | 401 |
| `quay.io/minio/aistor/minio` por ese digest | 404 |
| `public.ecr.aws`, `mirror.gcr.io` | 404 |
| Cache Docker local | conserva la base: **los 9 `diff_ids` coinciden** con `build-manifest.json` |
| `ghcr.io` derivado propio, anonimo | **401**, el paquete sigue privado |
| Token `gh` disponible | `gist, read:org, repo, workflow` — **sin** `read:packages` ni `write:packages` |

### 19.2 Causa

**Caso A: la imagen upstream fue retirada de la distribucion publica.**
`minio/minio` paso a privada en quay.io y desaparecio de Docker Hub, coincidiendo con el
giro del proyecto a su linea comercial AIStor.

Queda descartado:

- **B, cambio de autenticacion de quay.io:** otros **69** repositorios del mismo
  namespace siguen siendo publicos y anonimamente accesibles.
- **C, cambio de repositorio oficial:** ninguna ubicacion oficial sirve ese digest.
  `aistor/minio` es **otro producto**, con otra licencia, y no responde a ese digest.
- **D, ruta incorrecta en CI:** una sonda limpia contra el mismo digest reproduce el
  401 exacto, sin intervencion del workflow.

No es un fallo transitorio: dos reintentos de CI y varias sondas directas lo reproducen.

### 19.3 Lo que si conservamos

El artefacto exacto **no se ha perdido**. La cache local conserva la base con sus nueve
`diff_ids` identicos a los registrados, y el derivado completo sigue publicado en GHCR
con el digest que `Task/027.1` verifico. El problema no es de integridad ni de
procedencia: es de **accesibilidad anonima** desde el runner.

### 19.4 Por que la correccion no puede aplicarse sin una decision

Toda ruta que conserve la garantia de `Task/027.1` —imagen identificada de forma
reproducible y verificable, mismo producto, pin por digest, sin tags moviles— pasa por
servir esa base desde una ubicacion que el runner pueda leer. La unica que controlamos
es GHCR, y hoy:

- el paquete es **privado** y el token disponible **no tiene** `read:packages`;
- publicar un espejo exige `write:packages`, es decir una credencial nueva;
- hacerlo **publico** redistribuiria una imagen que su autor retiro deliberadamente de
  la distribucion publica. La AGPL lo permite, pero es una decision con consecuencias
  externas que no corresponde tomar por iniciativa propia.
