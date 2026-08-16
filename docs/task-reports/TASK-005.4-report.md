# Reporte — TASK-005.4 · Corregir la base de las ramas Task a `main`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.4-Corregir-Base-Ramas-Task-Main` |
| **Tipo** | **Mantenimiento de gobierno y workflow Git** |
| **Cuenta en el roadmap** | **No.** Avance global y ETAPA 02 **sin cambios** |
| **Estado final** | **Aprobada** ✔ — cerrada el 2026-08-15 |
| **Expresión de aprobación** | `approved: Task/005.4-Corregir-Base-Ramas-Task-Main` |
| **Repositorio** | `personal-blog-infra`, más el `CLAUDE.md` raíz del workspace |
| **Rama** | `Task/005.4-Corregir-Base-Ramas-Task-Main`. **Publicada en el cierre** |
| **Rama base** | **`main`** — **primera tarea del proyecto creada desde `main`** |
| **SHA base** | **`181c63445b5bc595dd74f9dea0ae2f423539b7cd`** |
| **Fecha** | 2026-08-15 |
| **Ficha** | [TASK-005.4](../tasks/TASK-005.4-correct-task-branch-base-main.md) |
| **Commits** | **1**, creado **después** de la aprobación explícita del usuario |
| **Pull request** | `Task/005.4 → main` — **abierto, sin fusionar** |

---

## 1. Normalización posterior al PR `#9`

### 1.1 Verificación del PR

`gh pr view 9 --repo jeffersondavila/personal-blog-infra`:

| Campo | Valor real devuelto |
| --- | --- |
| `number` | **9** |
| `state` | **`MERGED`** ✔ |
| `baseRefName` | **`main`** ✔ |
| `headRefName` | **`Task/005.3-Definir-PostgreSQL-Produccion-en-VPS`** ✔ |
| `mergeCommit.oid` | **`181c63445b5bc595dd74f9dea0ae2f423539b7cd`** |
| `mergedAt` | **`2026-08-16T03:56:08Z`** (UTC) |

**Merge commit real del PR `#9`: `181c634`.** No se asumió: se obtuvo de la API de GitHub.

**Rama remota eliminada**, confirmado sin ejecutar ningún borrado: el `fetch --prune`
inicial reportó `- [deleted] (none) -> origin/Task/005.3-…`, y
`git ls-remote --heads origin "Task/*"` devuelve **vacío**.

### 1.2 Estado antes de normalizar

| Comprobación | Resultado |
| --- | --- |
| `main` local | `5583947` — **4 commits por detrás** de `origin/main` |
| `dev` local | `bf31ebc`, al día con `origin/dev` |
| Working tree | Limpio |

Tras `git pull --ff-only origin main`: **`main` = `181c634` = `origin/main`**.

### 1.3 La normalización SÍ era necesaria

| Comprobación | Resultado |
| --- | --- |
| `git merge-base --is-ancestor main dev` | **NO** — `main` no estaba contenido en `dev` |
| `git log --oneline dev..main` | `181c634` — el merge del PR **faltaba en `dev`** |
| `git log --oneline main..dev` | `bf31ebc` — el merge de integración de la tarea |
| `git diff --stat main dev` | **vacío** — mismo contenido, historiales divergentes |

Patrón esperado: la integración de `Task/005.3` ya estaba en `dev`, pero el **merge commit
creado por GitHub al aceptar el PR existía solo en `main`**.

**Acción ejecutada:**

```
git merge --no-ff main -m "merge: normalizar dev con main despues del PR #9 de Task/005.3"
git push origin dev
```

### 1.4 Estado después

| Comprobación | Resultado |
| --- | --- |
| `main` / `origin/main` | **`181c634`** / **`181c634`** ✔ |
| `dev` / `origin/dev` | **`9dfbc10`** / **`9dfbc10`** ✔ |
| `git merge-base --is-ancestor main dev` | **SI** ✔ |
| Merge `181c634` contenido en `dev` | **SI** ✔ |
| `git log --oneline dev..main` | **vacío** ✔ |
| `git diff --stat main dev` | **vacío** ✔ |
| Ramas `Task/*` locales y remotas | **ninguna** ✔ |
| Publicación | `bf31ebc..9dfbc10 dev -> dev` ✔ |

Después se volvió a `main`, limpio y actualizado.

---

## 2. Evidencia del error documental encontrado

La documentación vigente **ordenaba lo contrario** al invariante correcto:

| Archivo | Línea original | Texto |
| --- | --- | --- |
| `docs/claude/PROJECT_INSTRUCTIONS.md` | §3 | *«Toda rama Task debe crearse desde `dev` actualizado.»* |
| `docs/claude/PROJECT_INSTRUCTIONS.md` | §4, paso 9 | *«Crear la rama Task desde `dev`.»* |
| `docs/claude/PROJECT_INSTRUCTIONS.md` | §4, cierre | **«No comenzar una tarea desde `main`.»** |
| `docs/project-management/WORKFLOW.md` | §2, paso 3 | *«Crear la rama Task desde `dev`»*, con `git switch dev` + `git switch -c Task/<…>` |
| `docs/project-management/WORKFLOW.md` | §3, pasos 1–2 | *«Actualizar `dev` y confirmar que es la base vigente» · «Crear `Task/<nombre>` desde `dev`»* |
| `docs/project-management/WORKFLOW.md` | §4, tabla | Origen de `Task/<…>` = **`dev`** |
| `docs/project-management/TASK_TEMPLATE.md` | Cabecera | *«`Task/<numero>-<nombre>` (creada desde `dev`)»* |
| `CONTRIBUTING.md` | §2, paso 3 | *«Crea la rama `Task/<numero>-<nombre>` **desde `dev`**.»* |
| `CONTRIBUTING.md` | §3, tabla | *«Trabajo aislado de una tarea, creado desde `dev`.»* |
| `README.md` | §7 | *«`Task/<numero>-<nombre>` — trabajo aislado de una tarea, creado desde `dev`.»* |
| `CLAUDE.md` (raíz) | — | **No contenía ningún invariante de ramas**; solo el import. |

La instrucción **«No comenzar una tarea desde `main`»** era la más dañina: no solo omitía
la regla correcta, **prohibía explícitamente** la única base válida.

**Consecuencia:** `Task/002` a `Task/005.3` nacieron de `dev`, siguiendo la documentación.

### Por qué es incorrecto

`dev` acumula **commits de integración** —merges `--no-ff` de tareas anteriores y
normalizaciones `main → dev`— que **no pertenecen a ninguna tarea nueva**. Si una Task nace
de `dev`, su PR `Task → main` puede **heredar historial exclusivo de integración**.

Crear cada Task desde `main` garantiza que el PR contenga **solo la tarea**, que la
ascendencia parta de la **rama estable**, que `dev` siga siendo **exclusivamente
integradora** y que sus commits **no contaminen** futuras Task.

---

## 3. Evidencia: esta tarea nació de `main`

Es la **primera evidencia de la regla que ella misma establece**.

**Precondiciones verificadas antes de crear la rama:**

| Comprobación | Resultado |
| --- | --- |
| Rama activa | **`main`** ✔ |
| `git status --porcelain` | **vacío** ✔ |
| `main` | `181c634` |
| `origin/main` | `181c634` |
| `main == origin/main` | **SI** ✔ |
| Rama `Task/005.4` local o remota preexistente | **ninguna** ✔ |

**Comando y verificación inmediata:**

```
git switch -c Task/005.4-Corregir-Base-Ramas-Task-Main
```

| Comprobación | Resultado |
| --- | --- |
| `git rev-parse HEAD` | **`181c63445b5bc595dd74f9dea0ae2f423539b7cd`** |
| `git rev-parse main` | **`181c63445b5bc595dd74f9dea0ae2f423539b7cd`** |
| **`HEAD == main`** | **SI** ✔ — **la rama nació de `main`** |
| `git rev-parse dev` | `9dfbc10847acab9b25d9fe67a88f8d215b654a41` |
| **`HEAD == dev`** | **NO** ✔ — **no nació de `dev`** |
| `git merge-base HEAD dev` | **`181c634`** = `main`, **no** `dev` ✔ |
| Commits propios frente a `main` | **0** |

---

## 4. Invariante establecido

> **Toda rama `Task/<...>` nace SIEMPRE desde `main` actualizado y limpio.
> `dev` NUNCA es la rama base de una Task.**

```
A. INICIO          origin/main → main actualizado → Task/<nombre>
B. DESARROLLO      trabajo solo en Task/<nombre>
C. APROBACIÓN      approved: Task/<nombre>
D. CIERRE          commit en Task
E. INTEGRACIÓN     Task → dev  ·  push dev
F. PUBLICACIÓN     push Task
G. PULL REQUEST    Task → main
H. USUARIO         revisa, fusiona y decide sobre la rama remota
I. NORMALIZACIÓN   fetch · main actualizado · main → dev · push dev
J. SIGUIENTE TASK  main actualizado → Task/<siguiente>
```

### Qué NO cambia

La palabra de aprobación exacta · `Task → dev` · push de `dev` · publicación de la rama
Task · PR `Task → main` · merge manual por el usuario · borrado remoto decidido por el
usuario · normalización `main → dev` · prohibición de merge automático a `main`.

**Solo cambia de dónde nace la rama Task. Respuesta: `main`.**

---

## 5. Archivos corregidos

**2 creados · 9 modificados · 0 eliminados — 11 archivos.**
10 en `personal-blog-infra` y **1 en la raíz del workspace**.

### Creados

| Archivo | Contenido |
| --- | --- |
| `docs/tasks/TASK-005.4-correct-task-branch-base-main.md` | Ficha de la tarea. |
| `docs/task-reports/TASK-005.4-report.md` | Este reporte. |

### Modificados

| Archivo | Cambio |
| --- | --- |
| `../CLAUDE.md` *(raíz, no versionado)* | Nueva sección **CRITICAL GIT INVARIANT** al principio, con los comandos de validación. **Se conserva el import** de `PROJECT_INSTRUCTIONS.md`. |
| `docs/claude/PROJECT_INSTRUCTIONS.md` | §3: tabla de ramas con `main` como única base y **INVARIANTE CRÍTICO**. §4 reescrita: comandos, validaciones `main == origin/main` y `HEAD == main`, **bloque «Prohibido»** con el flujo desde `dev`, motivo y nota histórica. |
| `docs/project-management/WORKFLOW.md` | Aviso de invariante en la cabecera; §2 paso 3 reescrito con validaciones y prohibición; **nueva §2.1** con el ciclo A→J, la frase «dev nunca es la rama base de una Task» y el **porqué**; §3 pasos 1–2; §4 tabla y reglas. |
| `docs/project-management/TASK_TEMPLATE.md` | Cabecera con **`Rama base = main`** y **SHA base dinámico**; **nueva §0 «Preparación Git»** con 4 comprobaciones y los comandos. |
| `docs/project-management/DEFINITION_OF_DONE.md` | **Criterio 11**: la rama Task nació de `main`, con el SHA registrado. En §2, comprobación de **base y head del PR** antes de crearlo. Sin duplicar el workflow. |
| `docs/project-management/STATUS.md` | Vista rápida; sección «Mantenimiento en curso»; cierre real de `Task/005.3` con el PR `#9`; estado de los repositorios; nota del invariante corregido. |
| `CONTRIBUTING.md` | §2 paso 3 y §3 tabla, con aviso del invariante. |
| `README.md` | §7 «Estrategia de ramas» con el invariante y el diagrama del ciclo. |
| `docs/task-reports/README.md` | Índice con `Task/005.4`. |

> **Documentos históricos no tocados.** Las fichas y reportes de `Task/001` a `Task/005.3`
> y las notas de `STATUS.md` sobre tareas pasadas dicen «creada desde `dev`» porque **así
> ocurrió**. Son registro histórico y **no se reescriben**.

---

## 6. Validaciones ejecutadas

Ejecutadas el 2026-08-15. **Ninguna se declara sin haberse ejecutado.**

| # | Validación | Resultado real |
| --- | --- | --- |
| 1 | PR `#9` y rama remota | **`MERGED`**, base `main`, head `Task/005.3`, merge **`181c634`**, `mergedAt 2026-08-16T03:56:08Z`. `git ls-remote --heads origin "Task/*"` **vacío**. Ningún borrado ejecutado por la sesión. |
| 2 | Normalización `main → dev` | **Era necesaria** y **se completó**: `main` = `181c634`, `dev` = `9dfbc10`, `main` **es ancestro de `dev`**, `dev..main` **vacío**, `git diff main dev` **vacío**, publicado. |
| 3 | **Base de `Task/005.4`** | **`HEAD == main == 181c634`**; `dev` = `9dfbc10`, distinto; `merge-base(HEAD, dev)` = `181c634` = `main`. **0 commits propios.** |
| 4 | Búsqueda global de reglas incorrectas | **0 reglas operativas vigentes** que ordenen crear una Task desde `dev`. Las 5 apariciones restantes en documentos de gobierno son: 1 prohibición en `CLAUDE.md`, 1 prohibición en `CONTRIBUTING.md`, 1 ejemplo **marcado como prohibido** en `PROJECT_INSTRUCTIONS.md` §4, 1 ejemplo **marcado con ❌** en `WORKFLOW.md` §2 y 1 frase explicativa del **porqué** en `WORKFLOW.md` §2.1. |
| 5 | `CLAUDE.md` raíz | **Contiene el invariante crítico** al principio, con comandos de validación. **El import de `PROJECT_INSTRUCTIONS.md` se conserva.** |
| 6 | `PROJECT_INSTRUCTIONS.md` | **`main` declarada única base permitida**; §4 con validaciones obligatorias y **bloque «Prohibido»** explícito. |
| 7 | `WORKFLOW.md` | Ciclo **A→J** en §2.1, frase «**dev nunca es la rama base de una Task**», motivo documentado, y §4 con `main` como origen de `Task/*`. |
| 8 | `TASK_TEMPLATE.md` | **`Rama base = main`**, **SHA base dinámico** —no fijo— y §0 con 4 comprobaciones. |
| 9 | `DEFINITION_OF_DONE.md` | **Criterio 11** añadido y comprobación de base/head del PR. **No duplica** el workflow: remite a `WORKFLOW.md` §2.1. |
| 10 | Resto del workflow | **Sin cambios**: palabra de aprobación, `Task → dev`, push `dev`, publicación de la rama, PR `Task → main`, merge manual del usuario, borrado remoto por el usuario, normalización `main → dev` y prohibición de merge automático. |
| 11 | Historial de tareas anteriores | **No reescrito.** Sin `rebase`, `reset` ni alteración de PR fusionados. Las menciones «creada desde `dev`» en fichas y reportes de `Task/001`–`Task/005.3` **se conservan**. |
| 12 | Recuento del roadmap | **41 filas** en `ROADMAP.md` y **41** en `STATUS.md`; IDs `001`–`041`, sin huecos ni duplicados. Avance **5 de 41 (12 %)**, ETAPA 02 **1 de 3**, `Task/006` **Pendiente**. Ninguna tarea añadida ni renumerada; **no se creó `Task/042`**. |
| 13 | Implementación | **0 cambios** en `personal-blog-backend`, `personal-blog-frontend`, `docker-compose.yml`, Terraform y arquitectura funcional. **0 archivos `.tf`** en el workspace. |
| 14 | Enlaces Markdown relativos | Barrido de los archivos afectados: **0 rotos**. |
| 15 | Higiene | `git diff --check` **sin errores**; **0 mojibake**; **0 secretos**. |
| 16 | Límites Git | Hasta la aprobación: **0 commits propios**, **0 push**, **0 merge de la rama Task**, **0 PR**. Tras la aprobación explícita, el cierre autorizado creó 1 commit, integró en `dev`, publicó la rama y abrió el PR. |
| 17 | Staging del cierre | **10 archivos** en `personal-blog-infra`: **8 modificados + 2 nuevos**, con contenido real y nada inesperado. El `CLAUDE.md` raíz **no se versiona** —la raíz del workspace no es un repositorio Git—, por eso son 11 archivos afectados pero **10 en el commit**. |

---

## 7. Riesgos

**Ninguno nuevo.** Esta tarea **reduce** un riesgo operativo real: que un pull request
`Task → main` arrastrara historial de integración ajeno a la tarea.

Los riesgos vigentes **R-02** a **R-35** quedan **sin cambios**; **ninguno se cierra**.

---

## 8. Problemas encontrados

| # | Problema | Resolución |
| --- | --- | --- |
| 1 | La regla incorrecta estaba **repartida en 6 documentos** —`PROJECT_INSTRUCTIONS`, `WORKFLOW`, `TASK_TEMPLATE`, `CONTRIBUTING`, `README` y la ausencia en `CLAUDE.md`—, no en uno solo. Corregir solo la fuente canónica habría dejado contradicciones vivas. | Búsqueda **global** en todos los `.md` del repositorio y del workspace, clasificando cada aparición como **regla operativa vigente** —corregida— o **registro histórico** —conservado—. |
| 2 | `PROJECT_INSTRUCTIONS.md` §4 no solo indicaba `dev`: **prohibía explícitamente** partir de `main`. Una corrección parcial habría dejado en pie la prohibición contraria al invariante. | Se reescribió la sección completa, sustituyendo la prohibición por la **regla correcta** y añadiendo el bloque «Prohibido» con el flujo desde `dev`. |
| 3 | Riesgo de que la corrección se leyera como una condena del trabajo anterior. | Se registró como **antecedente breve** con nota histórica en `WORKFLOW.md` §2.1 y `PROJECT_INSTRUCTIONS.md` §4, dejando claro que **el historial no se reescribe** y que la corrección **aplica hacia adelante**. |

Ninguna operación falló. **No se ejecutó ninguna acción destructiva.**

---

## 9. Confirmación explícita de límites respetados

> **Dos momentos distintos.** Hasta la aprobación no hubo commit, push, merge ni PR. El
> usuario aprobó con la expresión exacta y autorizó el flujo completo; las operaciones de Git
> posteriores son **parte del cierre autorizado**, no una excepción a los límites.

| Límite | Antes de la aprobación | Tras la aprobación |
| --- | --- | --- |
| Commits | **0** | **1**, autorizado |
| Push de la rama `Task/005.4` | **0** — no publicada | Publicada, autorizado |
| Merge de `Task/005.4` **en `dev`** | **0** | Merge `--no-ff`, autorizado |
| Pull request | **0** | **1**, `Task/005.4 → main`, **abierto** |
| **Fusión del PR hacia `main`** | — | **NO ejecutada.** Responsabilidad exclusiva del usuario |
| Modificación directa de `main` | **0** — solo `pull --ff-only` | **0** |
| Reescritura de historial (`rebase`, `reset`, `push --force`) | **0** | **0** |
| Alteración del PR `#9` o de commits fusionados | **0** | **0** |

Límites que se cumplen **igual antes y después** del cierre:

| Límite | Cumplimiento |
| --- | --- |
| Borrado de ramas remotas | **0** — la de `Task/005.3` ya la había eliminado el usuario |
| Cambios en la arquitectura PostgreSQL/VPS, **ADR-007** o **D-01** | **0** — ni una referencia resultó necesaria |
| Cambios en `personal-blog-backend` | **0 archivos** |
| Cambios en `personal-blog-frontend` | **0 archivos** |
| Cambios en `docker-compose.yml` | **0** |
| Archivos Terraform | **0** en todo el workspace |
| Floci instalado | **No** |
| Features implementadas | **0** |
| Tareas del roadmap | **41**, ninguna añadida, eliminada ni renumerada; **sin `Task/042`** |
| Avance global | **5 de 41 (12 %)** — sin cambios |
| ETAPA 02 | **1 de 3** — sin cambios |
| `Task/006` | **Pendiente, no iniciada** |
| Riesgos cerrados | **0** |
| Secretos versionados | **0** |
| Operaciones destructivas | **0** |

---

## 10. Instrucciones de validación para el usuario

Ver [ficha §14](../tasks/TASK-005.4-correct-task-branch-base-main.md). Resumen mínimo:

```powershell
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

git rev-parse HEAD    # 181c634 - la rama nacio de main
git rev-parse main    # 181c634
git rev-parse dev     # 9dfbc10 - distinto

git merge-base --is-ancestor main dev; if ($?) { "main es ancestro de dev" }
git diff --stat main dev     # vacio

code ..\CLAUDE.md
code docs\project-management\WORKFLOW.md
```

Ningún comando es destructivo.

---

## 11. Próxima tarea

`Task/006-Fundacion-Frontend-React` — **Pendiente, no iniciada**. No comienza hasta que el
usuario fusione el PR de `Task/005.4` y se complete la normalización `main → dev`.
**Nacerá desde `main`**, y será la primera tarea del roadmap oficial en aplicar el
invariante desde el principio.

---

## 12. Estado final

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.4-Corregir-Base-Ramas-Task-Main` |
| **Estado** | **Aprobada** ✔ |
| **Fecha de aprobación** | 2026-08-15 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.4-Corregir-Base-Ramas-Task-Main` |
| **Efecto en el avance** | **Ninguno.** Avance global **5 de 41 (12 %)**; ETAPA 02 **1 de 3**; `Task/006` **Pendiente** |
| **Invariante** | **Vigente y de cumplimiento obligatorio** desde el 2026-08-15 |

> La tarea quedó `Lista para validación` **sin commit, sin push, sin merge y sin PR**. El
> usuario la aprobó con la expresión exacta requerida por
> [WORKFLOW.md](../project-management/WORKFLOW.md) §3 y autorizó el flujo completo de cierre.
> Solo **entonces** se creó el commit, se integró la rama en `dev`, se publicó y se abrió el
> pull request. **La fusión del PR hacia `main` sigue siendo responsabilidad exclusiva del
> usuario y no se ejecutó.**
