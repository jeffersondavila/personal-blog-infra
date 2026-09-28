# TASK-029.1 — Corregir-Drift-Documental-Post-Merge

| Campo | Valor |
| --- | --- |
| Identificador | `Task/029.1-Corregir-Drift-Documental-Post-Merge` |
| Tipo | **Mantenimiento documental.** **No cuenta entre las 41** y **no altera el avance** |
| Estado | **Aprobada** — 2026-09-28 mediante `approved: Task/029.1-Corregir-Drift-Documental-Post-Merge` |
| Repositorios | `personal-blog-infra`. **Solo documentación** |
| Rama base | `main` actualizado y limpio; **nunca** `dev` |
| SHA base | `ce53ec93e1a4e78e635eeaa3740f249f5dfc18f1` |
| Avance | **29/41 ≈ 71 %** — **sin cambios**. ETAPA 09 **3/3**, sin cambios |

## 0. Preparación Git

| Validación | Resultado |
| --- | --- |
| `git fetch --prune origin` | Sin cambios pendientes |
| `git switch main` · `git pull --ff-only origin main` | `Already up to date` |
| `git rev-parse main` vs `origin/main` | **Coinciden**: `ce53ec93e1a4e78e635eeaa3740f249f5dfc18f1` |
| `git status --porcelain` | **Vacío** en los tres repositorios |
| `dev` normalizado | `076b2f5f86498de3990d772a8c35b76443d1a0d9` = `origin/dev`; `git diff main dev` **vacío**; `dev..main` = **0** |
| `Task/029.1` preexistente | **No**: 0 coincidencias locales y 0 remotas |
| `git switch -c Task/029.1-…` | Creada **desde `main`**, nunca desde `dev` |
| `HEAD` vs `main` | **Idénticos** (`ce53ec9`) — rama bien creada |

## 1. Objetivo

Corregir el **drift documental post-merge** de `Task/029`: afirmaciones que eran ciertas
mientras la tarea estaba *Lista para validación* y que el cierre aprobado invalidó.
**No se reabre `Task/029`**, no se toca su arquitectura y no se altera ninguna decisión.

## 2. Contexto — por qué existe esta tarea

`Task/029` quedó **aprobada, fusionada y normalizada** el 2026-09-27: PR **#53** `MERGED`,
`main` en `ce53ec9`, `dev` en `076b2f5`, CI Infra **success** en ambos SHA.

Su reporte y su ficha se redactaron **antes** de la aprobación. Al cerrarse el flujo —dos
commits, publicación de la rama, PR, merge manual del usuario y normalización `main → dev`—
varias frases de estado quedaron **falsas**, y dos cifras de gates quedaron **inconsistentes
entre sí**. Es el mismo tipo de mantenimiento que `Task/028.1`, `Task/026.1`, `Task/020.1` y
cinco más.

## 3. Principio de corrección aplicado

**Preservar la historia, no sustituirla.** Una afirmación que fue cierta en su momento no se
borra: se **fecha** y se acompaña del estado posterior. Donde había una única frase se
distinguen ahora **dos fases** —pre-aprobación y post-aprobación—, cada una con su estado real
de Git.

Para las cifras de gates se conserva **el valor que `Task/029` midió de verdad** en su
ejecución de cierre —**530 enlaces, 0 rotos**, el mismo que registra el mensaje del commit
`a3de55d`—, y **no** se persigue el número que arroja el árbol después de esta corrección: eso
falsearía lo que aquella tarea comprobó.

## 4. Alcance

**Nueve correcciones.** Ocho en los cuatro archivos ya existentes, más una en el propio reporte
de esta tarea —la n.º 9, detectada por el usuario en la revisión—. Nada más.

| # | Archivo | Qué decía | Qué dice ahora |
| --- | --- | --- | --- |
| 1 | `docs/task-reports/TASK-029-report.md` §13 | «Sin commit, sin push, sin PR, sin merge» | **§13.1 nueva** con las dos fases: pre-aprobación sin commit ni PR; post-aprobación con `d98c03c`, `a3de55d`, `affacaa`, PR #53, `ce53ec9` y `076b2f5`, más el CI por SHA |
| 2 | `docs/task-reports/TASK-029-report.md` §9 | «**526** enlaces» | «**530** enlaces» |
| 3 | `docs/tasks/TASK-029-…md` §6, criterio 10 | «**497** enlaces con 0 rotos» | «**530** enlaces con 0 rotos» |
| 4 | `docs/tasks/TASK-029-…md` §9 | «**526** enlaces» | «**530** enlaces» |
| 5 | `docs/project-management/STATUS.md` — nota de aporte a la tabla de riesgos | «Aporte de `Task/029`, 2026-09-27 — **Propuesta pendiente de aprobación**» | «Aporte de `Task/029`, **aprobada** el 2026-09-27» |
| 6 | `docs/project-management/STATUS.md` — intro de **R-47** | «Añadido el 2026-09-27, con `Task/029` **Lista para validación**» | «Añadido el 2026-09-27, **cuando** `Task/029` estaba Lista para validación; la tarea quedó **aprobada** ese mismo día y **R-47 sigue Abierto**» |
| 7 | `docs/project-management/STATUS.md` — *Vista rápida* | «Entrega D-22, D-23, D-24 y D-10 **como Propuesta**» | «Dejó D-22, D-23, D-24 y D-10 **Resueltas** y **EX-029-D13** Aceptada y Vigente; D-12 **sigue abierta**» |
| 8 | `docs/project-management/ROADMAP.md` — fila de `Task/029` | «D-22, D-23, D-24 y D-10 **entregadas como Propuesta**» | «**quedaron Resueltas**; D-12 **sigue abierta**» |
| **9** | `docs/task-reports/TASK-029.1-report.md` §5 — **este propio mantenimiento** | «gate de texto **OK — 5 archivos**» | «**6 archivos** del entregable definitivo (4 modificados + 2 nuevos)». El 5 venía de una ejecución **anterior a la creación de ese mismo archivo**. **Detectada por el usuario** en la revisión previa a la aprobación |

Las correcciones 5 a 8 **no cambian ninguna decisión**: alinean STATUS y ROADMAP con lo que el
[registro de decisiones](../architecture/open-decisions.md) ya declara desde la aprobación.

### Fuera del alcance

D-10, D-22, D-23, D-24 y **EX-029-D13** · el contenido sustantivo de **R-47** · los contadores
**29/41** y **ETAPA 09 3/3** · `terraform/` · AWS · *state* · `personal-blog-backend` y
`personal-blog-frontend` · el inicio de `Task/030`.

## 5. Criterios de aceptación

1. El reporte de `Task/029` distingue **pre-aprobación** y **post-aprobación** con los SHA
   reales, **sin borrar** la afirmación original.
2. Las tres cifras de enlaces coinciden entre sí y con lo que midió `Task/029`: **530**.
3. Ninguna salida de `Task/029` figura como **Propuesta** en STATUS ni en ROADMAP.
4. **Auditoría con C = 0**: ninguna aparición de drift real sobre `Task/029`.
5. **Historia ajena intacta**: ni una línea de `Task/028`, `Task/028.2`, `Task/005.3` o
   `Task/001` modificada.
6. Contadores **29/41** y **ETAPA 09 3/3** sin cambios.
7. `terraform/` sin cambios; cero AWS; *state* intacto; backend y frontend intactos.
8. Gates aplicables en verde y árbol limpio, **sin commit, sin push, sin PR y sin tocar
   `dev`**.
9. `Task/030` sigue **Pendiente y no iniciada**.
10. Estado de salida **Lista para validación**; nunca autoaprobación.

## 6. Estado

**Aprobada** el 2026-09-28. El mantenimiento **no cuenta entre las 41** y **no alteró el avance**:
sigue en **29/41 ≈ 71 %** con ETAPA 09 en **3/3**. **Ninguna decisión se tocó.**

| Campo | Valor |
| --- | --- |
| Fecha de aprobación | **2026-09-28** |
| Aprobado por | **El usuario**, con la expresión exacta requerida |
| Expresión requerida | `approved: Task/029.1-Corregir-Drift-Documental-Post-Merge` |

Reporte: [TASK-029.1-report.md](../task-reports/TASK-029.1-report.md).
