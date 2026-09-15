# TASK-026.1 — Corregir el drift documental posterior a la fusión de `Task/026`

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/026.1-Corregir-Drift-Documental-Post-Merge` |
| **Nombre** | Corregir el drift documental posterior a la fusión de `Task/026` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. No altera el avance global (**26 de 41**, ≈ 63 %) ni la ETAPA 08 (**4 de 4**, 100 %, Completada) |
| **Estado** | **Aprobada** ✔ el 2026-09-15 por el usuario |
| **Fecha de inicio** | 2026-09-15 (Guatemala) |
| **Fecha de aprobación** | **2026-09-15** |
| **Expresión de aprobación** | `approved: Task/026.1-Corregir-Drift-Documental-Post-Merge` |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Dependencias** | `Task/026-Runbooks-de-Despliegue` — **Aprobada** ✔ el 2026-09-15; PR `#45` fusionado y normalización `main → dev` completada |
| **Rama** | `Task/026.1-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | **`733caa3c24ea8fb663fcb3ea9633940c2803bfb5`** (`= main = origin/main` al crearla) |
| **Pull request** | `Task/026.1 → main`, creado durante el cierre aprobado del 2026-09-15, con base `main` y head esta rama Task. **Su estado se consulta en vivo** (`gh pr list --head Task/026.1-Corregir-Drift-Documental-Post-Merge`), no en este documento: [WORKFLOW §6.1](../project-management/WORKFLOW.md) |
| **Reporte** | [TASK-026.1-report.md](../task-reports/TASK-026.1-report.md) |

---

## 0. Preparación Git

| # | Comprobación | Resultado real |
| --- | --- | --- |
| 1 | `git fetch --prune origin` | Ejecutado en `personal-blog-infra` |
| 2 | `git switch main` · `git pull --ff-only origin main` | `Already up to date` |
| 3 | `main == origin/main` | **`733caa3c24ea8fb663fcb3ea9633940c2803bfb5`** en ambos |
| 4 | `git status --porcelain` | **vacío** |
| 5 | *Staging* | **0 archivos** |
| 6 | Rama `Task/026.1` local y remota | **inexistente** antes de crearla |
| 7 | Pull request previo con ese *head* | **ninguno** |
| 8 | `git switch -c Task/026.1-Corregir-Drift-Documental-Post-Merge` | Creada **desde `main`** |
| 9 | `HEAD == main` inmediatamente después | **coinciden** (`733caa3c24ea8fb663fcb3ea9633940c2803bfb5`) |
| 10 | `git rev-list --count main..HEAD` | **0** |

Regla permanente: [WORKFLOW §2.1](../project-management/WORKFLOW.md). Ninguna
rama Task nace de `dev`.

Repositorios `personal-blog-backend` y `personal-blog-frontend`: en `main`, limpios, sin rama Task.

## 1. Objetivo

Corregir exclusivamente dos afirmaciones documentales que eran verdaderas durante
la fase previa a la aprobación de `Task/026`, pero quedaron falsas en presente
después de su aprobación, commit, push, PR `#45`, merge y cierre post-merge.

`Task/026` está **cerrada y aprobada**. Esta tarea **no** revisa su
implementación, sus runbooks, sus decisiones ni su aprobación: solo el texto que
la describe.

- **NO** reinterpretar la historia.
- **NO** borrar evidencia histórica.
- **NO** ampliar alcance.

## 2. Contexto — por qué existe esta tarea

El cierre de una tarea documenta su propio estado **antes** de que el usuario
apruebe y fusione el pull request. En ese instante no hay commit en `main`, ni push
ni PR fusionado, por lo que el documento lo describe en tiempo presente.

En `Task/026`, dos frases quedaron formuladas en presente absoluto:

1. `docs/task-reports/TASK-026-report.md` §9: «Cero commit, push, merge, PR o aprobación.»
2. `docs/tasks/TASK-026-deployment-runbooks.md` §10 (Plan de ejecución, paso 9):
   «Reporte final **en progreso**, sin commit, push, PR ni aprobación.»

Ambas eran ciertas durante la ejecución previa al cierre. Al ser aprobada la tarea,
fusionado el PR `#45` en `main` y normalizado `main → dev`, ambas afirmaciones
perdieron su contexto temporal. El criterio 12 ([WORKFLOW §6.1](../project-management/WORKFLOW.md))
exige acotarlas temporalmente para que sigan siendo verdaderas como hechos históricos.

## 3. Principio de corrección y clasificación aplicada

| Clase | Qué es | Tratamiento |
| --- | --- | --- |
| **A** | Regla permanente de gobierno | Se conserva tal cual |
| **B** | Hecho histórico fechado | Se conserva; si le falta el ancla temporal, se le añade |
| **C** | Estado transitorio de Git/GitHub escrito en presente | Se convierte en hecho histórico de la fase previa a la aprobación |
| **D** | Contradicción documental | Se corrige preservando el hecho histórico |

Una afirmación que era cierta en su fecha **no se borra**: se ancla temporalmente.
Lo que se elimina es la **pretensión de vigencia presente**, no la evidencia histórica.

## 4. Alcance

- [x] Ejecutar precheck riguroso de Git en los tres repositorios.
- [x] Crear la rama `Task/026.1-Corregir-Drift-Documental-Post-Merge` desde `main` limpio en `personal-blog-infra`.
- [x] Corregir la afirmación de `docs/task-reports/TASK-026-report.md` §9 acotándola a la fase previa a la aprobación.
- [x] Corregir el paso 9 de `docs/tasks/TASK-026-deployment-runbooks.md` §10 acotándolo a la ejecución previa a la aprobación.
- [x] Crear esta ficha de especificación `docs/tasks/TASK-026.1-correct-post-merge-documentation-drift.md`.
- [x] Crear el reporte `docs/task-reports/TASK-026.1-report.md`.
- [x] Validar que no existen enlaces rotos Markdown en los documentos intervenidos.
- [x] Validar `git diff --check` con exit 0.
- [x] Mantener estado `Lista para validación`, sin commit, sin push, sin merge y sin PR.

### Fuera de alcance

- **No** se modifica `personal-blog-backend` ni `personal-blog-frontend`.
- **No** se tocan `scripts/laboratorio/`, `tests/`, `terraform/`, `laboratorio/`, `.github/workflows/`, `security/`, ni los runbooks operativos `deployment-*.md`.
- **No** se modifican decisiones (`D-026-A` a `D-026-J` permanecen Aceptadas y Vigentes).
- **No** se modifican contadores ni avance: avance **26/41 ≈ 63 %** y ETAPA 08 **Completada (4/4, 100 %)** intactos.
- **No** se reabre `Task/026`, que sigue **Aprobada** y cerrada post-merge.
- **No** se inicia `Task/027`, que permanece **Pendiente, no iniciada**.
- **No** se ejecuta Terraform, Docker, Floci ni suites del laboratorio. Cero recursos cloud reales.

## 5. Criterios de aceptación

| # | Criterio |
| --- | --- |
| 1 | Las dos frases originales ya no existen como afirmaciones vigentes absolutas |
| 2 | La nueva redacción las conserva como hechos históricos de la fase previa a la aprobación |
| 3 | `Task/026` = Aprobada y cerrada post-merge |
| 4 | ETAPA 08 = Completada (4/4, 100 %) |
| 5 | Avance global del proyecto = 26/41 ≈ 63 % |
| 6 | `Task/027` = Pendiente, no iniciada |
| 7 | Decisiones `D-026-A` a `D-026-J` = Aceptadas y Vigentes |
| 8 | Los cinco runbooks de despliegue = Vigentes |
| 9 | Enlaces Markdown en documentos tocados = 0 rotos |
| 10 | `git diff --check` = exit 0 |
| 11 | Finales de línea en LF y sin caracteres de control anómalos |
| 12 | 0 secretos introducidos |
| 13 | Tarea en estado `Lista para validación`, sin commit, sin push, sin merge, sin PR |
