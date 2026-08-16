# TASK-005.4 — Corregir la base de las ramas Task a `main`

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/005.4-Corregir-Base-Ramas-Task-Main` |
| **Nombre** | Corregir la base de las ramas Task a `main` |
| **Tipo** | **Mantenimiento de gobierno y workflow Git** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. No altera el avance global (**5 de 41**) ni la ETAPA 02 (**1 de 3**) |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**), más el `CLAUDE.md` raíz del workspace |
| **Dependencias** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` — **Aprobada** ✔, PR `#9` **fusionado** (merge `181c634`) y normalización `main → dev` completada |
| **Rama** | `Task/005.4-Corregir-Base-Ramas-Task-Main`. **Publicada en el cierre** |
| **Rama base** | **`main`** — **primera tarea del proyecto creada desde `main`** |
| **SHA base** | **`181c63445b5bc595dd74f9dea0ae2f423539b7cd`** (`= main = origin/main` al crearla) |
| **Fecha de inicio** | 2026-08-15 |
| **Fecha de aprobación** | 2026-08-15 |
| **Última actualización** | 2026-08-15 — cierre aprobado |
| **Próxima tarea** | `Task/006-Fundacion-Frontend-React` — **Pendiente, no iniciada** |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** Esta tarea es, además, **la primera evidencia de la
regla que ella misma establece**.

| # | Comprobación | Resultado real |
| --- | --- | --- |
| 1 | `main == origin/main` | **Sí** — ambos `181c634` |
| 2 | Working tree limpio antes de crear la rama | **Sí** — `git status --porcelain` vacío |
| 3 | Rama activa antes de crear = `main` | **Sí** |
| 4 | Rama creada **desde `main`** | **Sí** |
| 5 | `git rev-parse HEAD` == `git rev-parse main` tras crearla | **Sí** — ambos `181c634` |
| 6 | `HEAD` distinto de `dev` | **Sí** — `dev` = `9dfbc10` |
| 7 | `git merge-base HEAD dev` | **`181c634`** = `main`, **no** `dev` |
| 8 | Commits propios frente a `main` al crearla | **0** |

```powershell
git fetch --prune origin
git switch main
git pull --ff-only origin main
git status --porcelain                          # vacio
git rev-parse main; git rev-parse origin/main   # 181c634 / 181c634

git switch -c Task/005.4-Corregir-Base-Ramas-Task-Main

git rev-parse HEAD; git rev-parse main          # 181c634 / 181c634
```

---

## 1. Objetivo

Corregir el invariante Git del proyecto y dejarlo escrito de forma inequívoca:

> **Toda rama `Task/<...>` nace SIEMPRE desde `main` actualizado y limpio.
> `dev` NUNCA es la rama base de una Task.**

## 2. Contexto — el problema encontrado

La documentación vigente ordenaba lo contrario. `PROJECT_INSTRUCTIONS.md` §3 decía
literalmente *«Toda rama Task debe crearse desde `dev` actualizado»* y su §4 cerraba con
**«No comenzar una tarea desde `main`»**. `WORKFLOW.md` §2 daba el comando
`git switch dev` seguido de `git switch -c Task/<...>`, y su §3 listaba como paso 1
*«Actualizar `dev` y confirmar que es la base vigente»*.

Como consecuencia, **`Task/002` a `Task/005.3` nacieron de `dev`**.

### Por qué es incorrecto

`dev` acumula **commits de integración** —los merges `--no-ff` de tareas anteriores y las
normalizaciones `main → dev`— que **no pertenecen a ninguna tarea nueva**.

Si una Task nace de `dev`, su pull request `Task → main` puede **heredar historial
exclusivo de integración**, ajeno al trabajo de la tarea.

Crear cada Task desde `main` garantiza que:

| # | Garantía |
| --- | --- |
| 1 | El pull request contiene **únicamente** la tarea correspondiente. |
| 2 | La ascendencia del trabajo parte de la **rama estable**. |
| 3 | `dev` conserva su función **exclusivamente integradora**. |
| 4 | Los commits de integración de `dev` **no contaminan** futuras Task. |

## 3. Dentro del alcance

- [x] Normalizar `main → dev` tras la fusión del PR `#9` de `Task/005.3`.
- [x] Verificar que la rama remota `Task/005.3` ya no existe y obtener el **merge commit
      real** del PR `#9`, sin asumirlo.
- [x] **Crear esta rama desde `main`**, probando la base con SHA.
- [x] Buscar **globalmente** toda regla operativa que ordene crear una Task desde `dev`.
- [x] Añadir el **invariante crítico** al `CLAUDE.md` raíz del workspace, de forma visible
      y compacta, conservando las importaciones existentes.
- [x] Convertir `PROJECT_INSTRUCTIONS.md` en la **fuente canónica detallada**, con los
      comandos, las validaciones obligatorias y la **prohibición explícita**.
- [x] Reescribir el ciclo oficial en `WORKFLOW.md` (§2, §2.1, §3, §4), con el diagrama
      A→J y la frase «`dev` nunca es la rama base de una Task».
- [x] Documentar **por qué** en `WORKFLOW.md` §2.1.
- [x] Fijar `Rama base = main` y las comprobaciones en `TASK_TEMPLATE.md`, con **SHA
      obtenido dinámicamente**.
- [x] Añadir a la Definition of Done el criterio **11** y la comprobación de base/head del
      PR, **sin duplicar** el workflow.
- [x] Corregir `CONTRIBUTING.md` y `README.md`.
- [x] Registrar en `STATUS.md` la normalización posterior al PR `#9` y esta tarea.
- [x] Crear ficha y reporte, y actualizar el índice de reportes.

## 4. Fuera del alcance

| Elemento | Motivo |
| --- | --- |
| Modificar la arquitectura PostgreSQL/VPS, **ADR-007** o **D-01** | `Task/005.3` está cerrada. Solo se tocan referencias indispensables — ninguna resultó necesaria. |
| Reescribir el historial de `Task/002`–`Task/005.3` | **Prohibido.** Sin `rebase`, `reset` ni alteración de PR ya fusionados. La corrección aplica **hacia adelante**. |
| Corregir retrospectivamente ramas ya fusionadas | Mismo motivo. |
| Cambiar el resto del workflow | La palabra de aprobación, `Task → dev`, push de `dev`, publicación de la rama, PR `Task → main`, merge manual del usuario, borrado remoto por el usuario y normalización `main → dev` **no cambian**. |
| Tocar backend, frontend o Docker Compose | 0 cambios. |
| Crear Terraform, instalar Floci o implementar cualquier feature | 0 implementación. |
| Añadir `Task/005.4` al conteo de 41 o crear `Task/042` | Es mantenimiento; el roadmap no cambia. |
| Iniciar `Task/006` | No se inicia la tarea siguiente sin cerrar la actual. |

## 5. Entregables

| Entregable | Ruta | Acción |
| --- | --- | --- |
| Invariante crítico visible en el arranque de sesión | `../../CLAUDE.md` *(raíz del workspace)* | Modificado |
| Fuente canónica detallada del procedimiento | `docs/claude/PROJECT_INSTRUCTIONS.md` | Modificado |
| Ciclo oficial de ramas y el porqué | `docs/project-management/WORKFLOW.md` | Modificado |
| Plantilla con `Rama base = main` y comprobaciones | `docs/project-management/TASK_TEMPLATE.md` | Modificado |
| Criterio 11 e higiene de PR | `docs/project-management/DEFINITION_OF_DONE.md` | Modificado |
| Estado del proyecto | `docs/project-management/STATUS.md` | Modificado |
| Guía de contribución | `CONTRIBUTING.md` | Modificado |
| README del repositorio | `README.md` | Modificado |
| Ficha de esta tarea | `docs/tasks/TASK-005.4-correct-task-branch-base-main.md` | **Creado** |
| Reporte de esta tarea | `docs/task-reports/TASK-005.4-report.md` | **Creado** |
| Índice de reportes | `docs/task-reports/README.md` | Modificado |

**2 creados · 9 modificados · 0 eliminados — 11 archivos afectados.**
10 en `personal-blog-infra` y **1 en la raíz del workspace** (`CLAUDE.md`, no versionado).
**0 archivos** en `personal-blog-backend` y **0** en `personal-blog-frontend`.

## 6. Criterios de aceptación

| # | Criterio | Estado |
| --- | --- | --- |
| 1 | PR `#9` verificado como **fusionado**, con su merge commit real obtenido de GitHub. | Cumplido — validación 1 |
| 2 | Rama remota `Task/005.3` **ausente**, sin ejecutar ningún borrado. | Cumplido — validación 1 |
| 3 | `main == origin/main` y `dev == origin/dev`. | Cumplido — validación 2 |
| 4 | `main` es **ancestro de `dev`** y `git diff main dev` está vacío. | Cumplido — validación 2 |
| 5 | **La rama `Task/005.4` nació de `main`**, probado con SHA. | Cumplido — validación 3 |
| 6 | **0 reglas operativas vigentes** que ordenen crear una Task desde `dev`. | Cumplido — validación 4 |
| 7 | Las menciones a `dev` que quedan son **históricas** o **ejemplos marcados como prohibidos**. | Cumplido — validación 4 |
| 8 | El `CLAUDE.md` raíz contiene el invariante crítico y **conserva** sus importaciones. | Cumplido — validación 5 |
| 9 | `PROJECT_INSTRUCTIONS.md` declara `main` como única base y **prohíbe** el flujo desde `dev`. | Cumplido — validación 6 |
| 10 | `WORKFLOW.md` documenta el ciclo A→J y el **porqué**. | Cumplido — validación 7 |
| 11 | `TASK_TEMPLATE.md` fija `Rama base = main` con SHA **dinámico**. | Cumplido — validación 8 |
| 12 | La Definition of Done incorpora la comprobación mínima **sin duplicar** el workflow. | Cumplido — validación 9 |
| 13 | El resto del workflow **no cambia**. | Cumplido — validación 10 |
| 14 | El historial de tareas anteriores **no se reescribe**. | Cumplido — validación 11 |
| 15 | Exactamente **41 tareas**, IDs `001`–`041`, ninguna renumerada; avance **5 de 41**; ETAPA 02 **1 de 3**; `Task/006` **Pendiente**. | Cumplido — validación 12 |
| 16 | 0 cambios en backend, frontend, Docker Compose, Terraform y arquitectura funcional. | Cumplido — validación 13 |
| 17 | Enlaces relativos 0 rotos, `git diff --check` limpio, 0 mojibake, 0 secretos. | Cumplido — validaciones 14 y 15 |
| 18 | Sin commit, sin push, sin merge y sin PR **mientras la tarea no estuvo aprobada**; quedó `Lista para validación`. El commit, la integración en `dev` y el PR se ejecutaron **solo tras la aprobación explícita del usuario**. | Cumplido — validación 16 |

## 7. TDD / Plan test-first

**No aplica.** Tarea de gobierno documental; no introduce comportamiento funcional del
backend. `BACKEND_TESTING_STRATEGY.md` **no se modifica** y la regla
**RED → GREEN → REFACTOR** sigue íntegra.

La verificación equivalente es **el estado real de Git** —comprobado, no asumido— más la
**consistencia documental** y la **ausencia de reglas contradictorias**.

## 8. Comandos de validación

```powershell
$env:PATH = "$env:PATH;C:\Program Files\GitHub CLI"
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

# 1. PR #9 y ramas remotas
gh pr view 9 --repo jeffersondavila/personal-blog-infra --json state,mergeCommit
git ls-remote --heads origin "Task/*"

# 2. Normalizacion
git merge-base --is-ancestor main dev     # exit 0 esperado
git diff --stat main dev                  # vacio

# 3. Base de esta rama
git rev-parse HEAD
git rev-parse main                        # deben coincidir
git rev-parse dev                         # debe diferir

# 4. Busqueda global de reglas incorrectas
Select-String -Path (Get-ChildItem . -Recurse -Filter *.md).FullName -Pattern "desde ``dev``"

# 5. Recuento del roadmap
$bt = [char]96
(Select-String -Path docs\project-management\ROADMAP.md -Pattern ('^\| ' + $bt + 'Task/0')).Count

# 6. Repositorios no implicados
git -C ..\personal-blog-backend  status --porcelain -b
git -C ..\personal-blog-frontend status --porcelain -b

# 7. Higiene
git diff --check
```

## 9. Resultado de las validaciones

Ejecutadas el 2026-08-15. Resultados completos en el
[reporte](../task-reports/TASK-005.4-report.md) §6.

## 10. Decisiones técnicas

| # | Decisión | Alternativas consideradas | Justificación |
| --- | --- | --- | --- |
| 1 | **`main` como única base.** | Mantener `dev`; permitir ambas según el caso. | Una regla con excepciones no es una regla: reaparecería el mismo problema. `main` es la rama estable y no contiene commits de integración. |
| 2 | **No reescribir el historial de `Task/002`–`Task/005.3`.** | `rebase` de las ramas ya fusionadas. | Está publicado y fusionado. Reescribirlo sería destructivo y no aporta nada: la corrección aplica hacia adelante. |
| 3 | **Añadir el invariante al `CLAUDE.md` raíz**, no solo confiar en el import. | Dejarlo únicamente en `PROJECT_INSTRUCTIONS.md`. | El `CLAUDE.md` raíz es lo primero que se carga en cada sesión. Un invariante que solo vive tras un import es más fácil de pasar por alto. |
| 4 | **Conservar los ejemplos prohibidos escritos**, marcados como tales. | Omitirlos. | Nombrar el error exacto —`git switch dev` seguido de `git switch -c`— es más eficaz que describirlo en abstracto. |
| 5 | **Criterio 11 en la Definition of Done, no un procedimiento.** | Copiar el flujo completo en la DoD. | La DoD comprueba hechos; `WORKFLOW.md` describe el procedimiento. Duplicarlo crearía dos fuentes de verdad que divergirían. |
| 6 | **Esta tarea como primera evidencia del invariante.** | Aplicar la regla solo a partir de `Task/006`. | Una regla que su propia tarea correctora incumple no es creíble. El SHA base queda registrado como prueba. |

## 11. Riesgos

**Ninguno nuevo.** Esta tarea **reduce** un riesgo operativo existente: que un pull request
`Task → main` arrastrara historial de integración ajeno a la tarea.

Los riesgos vigentes **R-02** a **R-35** quedan **sin cambios**; ninguno se cierra.

## 12. Documentación creada o actualizada

Ver sección 5. **11 archivos**.

## 13. Resultado de pruebas

**No aplica en el sentido habitual:** la tarea no ejecuta código. Su equivalente son las
**16 validaciones** de estado de Git y consistencia documental del
[reporte](../task-reports/TASK-005.4-report.md) §6, todas ejecutadas.

## 14. Pasos de validación para el usuario

```powershell
$env:PATH = "$env:PATH;C:\Program Files\GitHub CLI"
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

# 1. Esta rama nacio de main
git rev-parse HEAD    # 181c634 al crearla
git rev-parse main    # 181c634
git rev-parse dev     # 9dfbc10 - distinto

# 2. main y dev normalizadas
git merge-base --is-ancestor main dev; if ($?) { "main es ancestro de dev" }
git diff --stat main dev                 # vacio

# 3. La regla quedo escrita
code ..\CLAUDE.md
code docs\project-management\WORKFLOW.md
Select-String -Path docs\claude\PROJECT_INSTRUCTIONS.md -Pattern "INVARIANTE"

# 4. 41 tareas y avance sin cambios
Select-String -Path docs\project-management\ROADMAP.md -Pattern "5 de 41"

# 5. Nada mas se toco
git -C ..\personal-blog-backend  status --porcelain -b
git -C ..\personal-blog-frontend status --porcelain -b
```

Ningún comando es destructivo.

## 15. Deuda pendiente

- **La regla es documental, no automática.** Nada impide técnicamente crear una rama desde
  `dev`; depende de que la validación `HEAD == main` se ejecute. Un *hook* que lo verifique
  podría evaluarse en `Task/021-CI-Infraestructura`.
- **Las tareas `Task/002`–`Task/005.3` conservan su ascendencia desde `dev`.** Es histórico
  y no se corrige.

## 16. Próxima tarea

`Task/006-Fundacion-Frontend-React` — **Pendiente, no iniciada**. No comienza hasta que el
usuario fusione el PR de `Task/005.4` y se complete la normalización `main → dev`.
**Nacerá desde `main`**, aplicando ya el invariante que esta tarea establece.

## 17. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** ✔ |
| **Fecha de aprobación** | 2026-08-15 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.4-Corregir-Base-Ramas-Task-Main` |
| **Efecto en el avance** | **Ninguno.** Es mantenimiento: no cuenta dentro de las 41 tareas. Avance global **5 de 41 (12 %)**; ETAPA 02 **1 de 3**; `Task/006` **Pendiente** |

Qué queda **vigente** con la aprobación:

| Elemento | Estado |
| --- | --- |
| **Invariante: toda rama `Task/<...>` nace de `main`** | **Vigente y de cumplimiento obligatorio** ✔ |
| **`dev` nunca es base de una Task** | **Vigente** ✔ |
| `CLAUDE.md` raíz — *CRITICAL GIT INVARIANT* | **Vigente** ✔ |
| `PROJECT_INSTRUCTIONS.md` §3 y §4 | **Vigentes** ✔ |
| `WORKFLOW.md` §2, §2.1, §3, §4 | **Vigentes** ✔ |
| `TASK_TEMPLATE.md` — `Rama base = main` | **Vigente** ✔ |
| `DEFINITION_OF_DONE.md` — criterio **11** | **Vigente** ✔ |
| Resto del workflow | **Sin cambios** |
| Historial de `Task/002`–`Task/005.3` | **No reescrito** |

> El usuario autorizó explícitamente el cierre con la expresión exacta requerida por
> [WORKFLOW.md](../project-management/WORKFLOW.md) §3, y autorizó el flujo completo: commit,
> integración en `dev`, publicación de la rama y creación del pull request
> `Task/005.4 → main`. **La fusión del PR sigue siendo responsabilidad exclusiva del
> usuario.**
