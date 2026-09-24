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
