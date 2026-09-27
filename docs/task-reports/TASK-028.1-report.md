# TASK-028.1 — Reporte

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/028.1-Corregir-Drift-Documental-Post-Merge` |
| **Tipo** | Mantenimiento de gobierno documental |
| **Estado** | **Aprobada** ✔ el 2026-09-26 |
| **Expresión de aprobación** | `approved: Task/028.1-Corregir-Drift-Documental-Post-Merge` |
| **Fecha** | 2026-09-26 (Guatemala) |
| **Zona horaria** | Fechas locales en **Guatemala (UTC−6)**; los `timestamp` de GitHub se conservan en **UTC** y se identifican como tales |
| **Repositorio** | `personal-blog-infra`, únicamente |
| **Rama base** | `main` — `e0fa95b9ee367fc0026a15f3e0afad3c5a012c26` |
| **Ficha** | [TASK-028.1-correct-post-merge-documentation-drift.md](../tasks/TASK-028.1-correct-post-merge-documentation-drift.md) |

---

## 1. Punto de partida

`Task/028-GitHub-OIDC-AWS` quedó **Aprobada** el 2026-09-26, el usuario fusionó el **PR #50** y
la normalización `main → dev` se completó. En ese estado quedaban **dos casillas abiertas** que
ya tenían evidencia:

| Archivo | Línea | Casilla |
| --- | --- | --- |
| `docs/tasks/TASK-028-github-oidc-aws.md` | 45 | Reconfirmación postmerge desde `main` (criterio 8) |
| `docs/stages/STAGE-09-cloud-accounts.md` | 185 | **Cuarto criterio asociado a `Task/028`** —trust main-only **y** reconfirmación postmerge—, **séptimo** de la lista global de criterios de salida |

## 2. Causa del drift: es de orden, no de error

El criterio 8 de `Task/028` establece que la reconfirmación postmerge **no es prerrequisito de
la aprobación** pero **sí es obligatoria antes de dar la tarea por integrada**. El workflow
`Verify AWS OIDC` solo se ejecuta en `main` por `workflow_dispatch`, de forma deliberada.

De ahí se sigue, sin remedio, que en el instante de aprobar y fusionar la casilla **tenía que
estar abierta**: la validación aún no podía existir. Cuando existió, la documentación de
`Task/028` ya estaba fusionada y su rama eliminada.

No es un error de `Task/028` ni un descuido: es el desfase que impone el propio orden del
flujo. Por eso se corrige en una tarea de mantenimiento y **no** con un commit directo a `main`
ni reescribiendo historia.

## 3. Evidencia registrada

### 3.1 Reconfirmación postmerge — `Verify AWS OIDC` sobre `main`

Ejecución **`36294958979`**, `workflow_dispatch`, rama `main`, SHA `e0fa95b`, iniciada hacia las
`2026-09-27T04:39Z` **(UTC)** = **2026-09-26 22:39 Guatemala**, **success** en sus dos jobs:

| Job | Resultado |
| --- | --- |
| `no-id-token` | **success** — `GitHub job without id-token: token request unavailable (GitHub-side evidence)` |
| `federation` | **success** |

Salida del verificador, saneada:

```
GetCallerIdentity: expected account and role
iam:ListRoles: AccessDenied (scope: this operation only)
Wrong audience: InvalidIdentityToken (provider/trust chain)
```

Lo que eso acredita, y solo eso:

- **Federación real desde `main`**: la trust main-only acepta el token de `main`, que es lo
  que las ejecuciones premerge **no** podían demostrar.
- **Identidad exacta**: el verificador **falla** si el ARN no es
  `arn:aws:sts::<cuenta>:assumed-role/PersonalBlogGitHubOidcValidation/task028-validation`.
  No se compara a ojo.
- **Sin permisos aplicativos**: `iam:ListRoles` devuelve `AccessDenied`. El propio mensaje
  acota el alcance —«this operation only»—: **no** se deduce ausencia universal de permisos.
- **Cadena de confianza exacta**: un token con audiencia incorrecta se rechaza con
  `InvalidIdentityToken`.

Todas las operaciones son de **solo lectura**: `sts get-caller-identity`, un
`iam list-roles --max-items 1` que debe ser denegado y un `AssumeRoleWithWebIdentity` que debe
fallar. **Cero mutaciones en AWS.**

### 3.2 Workflows del cierre

| Workflow | Evento | Rama | SHA | Resultado | Ejecución |
| --- | --- | --- | --- | --- | --- |
| `CI Infra` | `push` | `main` | `e0fa95b` | **success** | `36294537457` |
| `Verify AWS OIDC` | `workflow_dispatch` | `main` | `e0fa95b` | **success** | `36294958979` |
| `CI Infra` | `push` | `dev` | `ba276e3` | **success** | `36295020774` |

### 3.3 SHA finales verificados

| Referencia | SHA |
| --- | --- |
| `main` = `origin/main` | `e0fa95b9ee367fc0026a15f3e0afad3c5a012c26` |
| `dev` = `origin/dev` | `ba276e325ed296ec97f460c5c2085c8302485b9b` |
| Commit de merge del PR #50 | `e0fa95b9ee367fc0026a15f3e0afad3c5a012c26` |
| Fusionado por / cuándo | `jeffersondavila`, `2026-09-27T04:31:03Z` **(UTC)** = **2026-09-26 22:31:03 Guatemala** |

`main` y `dev` tienen **contenido idéntico** —0 archivos de diferencia— y **0 commits de `main`
ausentes en `dev`**. Los commits que solo están en `dev` son sus propios merges de integración
y normalización, la misma forma de historial que en los cierres anteriores.

### 3.4 Zona horaria: el proyecto fecha en Guatemala

Las fechas documentales de este proyecto son **locales de Guatemala (UTC−6)**. Los hechos del
cierre de `Task/028` ocurrieron de madrugada en UTC, es decir **el 2026-09-26 por la noche en
Guatemala**:

| Hecho | UTC | Guatemala |
| --- | --- | --- |
| Publicación del derivado D-1 | `2026-09-27T01:38Z` aprox. | **2026-09-26** 19:38 |
| Corrección del runtime de Portainer | `2026-09-27T02:05Z` aprox. | **2026-09-26** 20:05 |
| Aprobación y merge del PR #50 | `2026-09-27T04:31:03Z` | **2026-09-26** 22:31:03 |
| Reconfirmación postmerge | `2026-09-27T04:39Z` aprox. | **2026-09-26** 22:39 |

### 3.5 Alcance de la corrección de fechas, y por qué se amplió

El encargo citaba cuatro fechas: inicio de `Task/028.1`, fecha del reporte, cumplimiento de la
reconfirmación y aprobación/merge de `Task/028`. **Se corrigieron todas las del mismo grupo**,
incluidas la publicación del derivado y la corrección del runtime de Portainer, por una razón
concreta: si la aprobación pasaba al **26** y la publicación se quedaba en el **27**, la
documentación afirmaría que el derivado se publicó **después** de aprobarse la tarea, cuando
ocurrió antes. Corregir solo cuatro habría **invertido el orden real de los hechos**.

Los `timestamp` completos de GitHub **se conservan tal cual**, marcados como **UTC**: son
evidencia técnica y su valor no depende de la zona en que se lea.

**No se tocó ninguna fecha anterior** al grupo: las de `2026-09-25` y antes corresponden a otros
eventos y se dejan como están.

## 4. Corrección aplicada

| Archivo | Cambio |
| --- | --- |
| `docs/tasks/TASK-028-github-oidc-aws.md` | Casilla de reconfirmación postmerge marcada, citando ejecución y SHA; el párrafo que la declaraba abierta se actualiza sin borrar su razón; el criterio 8 recibe la anotación **CUMPLIDO** conservando íntegra su redacción original |
| `docs/stages/STAGE-09-cloud-accounts.md` | **Cuarto criterio asociado a `Task/028`** —séptimo de la lista global— marcado, sustituyendo la nota «Mitad cumplida» por la evidencia completa |
| `docs/project-management/STATUS.md` | Entrada de `Task/028.1` en **Lista para validación**, como exige WORKFLOW §6 |
| `docs/project-management/ROADMAP.md` | **Solo** una fecha local corregida; ningún cambio de estado ni de avance |
| `docs/task-reports/TASK-028-report.md` | Fechas locales corregidas y addendum en §27.2 y §27.3 sobre el criterio ya cumplido |
| `docs/tasks/TASK-028.1-correct-post-merge-documentation-drift.md` | **Nuevo** — ficha |
| `docs/task-reports/TASK-028.1-report.md` | **Nuevo** — este reporte |

Nada más. **No se tocó** AWS, Terraform, la implementación OIDC, GHCR, MinIO, workflows,
código, pruebas, secretos ni `Task/029`.

## 5. Verificación de invariantes y contadores

| Comprobación | Resultado |
| --- | --- |
| Casillas abiertas en la ficha de `Task/028` | **0** |
| Casillas marcadas en los criterios de salida de la ETAPA 09 | **7** de **19** |
| Casillas abiertas en los criterios de salida | **12**, todas de `Task/029` |
| Avance global | **28/41 ≈ 68 %**, **sin cambio** |
| ETAPA 09 | **2/3 ≈ 67 %**, **sin cambio** |
| Esta tarea cuenta entre las 41 | **No** |
| Archivos modificados fuera del alcance | **0** |

### 5.1 Gates ejecutados, con conteo capturado

| Gate | Resultado |
| --- | --- |
| `python -B -m unittest discover -s tests/oidc` | `Ran 60 tests` · **OK** (1 omitida) |
| `python -B -m unittest discover -s tests/laboratorio` | `Ran 176 tests` · **OK** |
| `python -B -m unittest discover -s tests/security` | `Ran 88 tests` · **OK** |
| `vulnerability_gate.py --comprobar-coherencia .` | **RESULTADO: CORRECTO** |
| CRLF en los archivos tocados | **0** |
| Caracteres de control | **0** |
| Enlaces relativos rotos | **0** |
| `git diff --check` | sin avisos |
| Archivos fuera del alcance | **0** |
| Árbol de trabajo | cambios **sin commit**, sin `push`, sin PR, sin tocar `dev` |

Esta tarea **no cambia código ni pruebas**: las suites se ejecutan para demostrar que la
edición documental no rompió nada, no porque hubiera algo nuevo que probar. El conteo se
**captura**, no se cita de memoria: en un resumen anterior se declaró «security 88» cuando la
salida mostrada solo acreditaba «OK», y eso es afirmar más de lo medido.

## 6. Lo que esta tarea NO cambia

- **`main` sigue sin protección de rama.** Debe existir antes de habilitar roles de despliegue
  efectivos.
- El rol `PersonalBlogGitHubOidcValidation` **no acredita despliegue**: cero políticas
  gestionadas y cero inline. Permisos mínimos en `Task/038` y `Task/039`; validación integral
  en `Task/040`.
- Lo observado en **Floci** sigue siendo hipótesis hasta la ETAPA 10.
- **D-06** está resuelta en el modelo; el bucket lo materializa `Task/030`.
- **SBOM y procedencia** siguen sin publicarse junto a la imagen; el paquete sigue **privado**.
- **`GHCR_MINIO_READ_TOKEN`** caduca el **2027-09-25** y requiere rotación antes.
- La configuración inicial de Portainer —crear la cuenta de administrador, que esa instalación
  nunca tuvo— es anterior a `Task/028` y ajena a su cierre.
- **`ROADMAP.md`** no recibe cambio de estado ni de avance: WORKFLOW §6 solo lo exige al
  cambiar el estado o el avance de una **etapa**, y aquí no cambia ninguno. Sí se corrige en él
  una **fecha local**, por el motivo del §3.5.

## 7. Aprobación y cierre

**APROBADA** el **2026-09-26** mediante `approved: Task/028.1-Corregir-Drift-Documental-Post-Merge`.

Sin decisiones arquitectónicas: **ningún ADR** se crea, reemplaza ni promueve. Sin cambio de
contadores: **28/41 ≈ 68 %** y **ETAPA 09 2/3 ≈ 67 %**, porque esta tarea no cuenta entre las 41.

Flujo de cierre ejecutado en `personal-blog-infra`, el único repositorio afectado: aprobación
registrada, documentos actualizados, validaciones reejecutadas, commit, integración de la rama
Task en `dev` mediante `merge --no-ff`, publicación de `dev`, pull request
**`Task/028.1 → main`** y eliminación de la rama Task **local** con `git branch -d`.

**El pull request no se acepta ni se fusiona:** es responsabilidad exclusiva del usuario. La
rama Task **remota no se elimina**. No se inicia la tarea siguiente.
