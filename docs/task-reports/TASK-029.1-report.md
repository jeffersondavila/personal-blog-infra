# TASK-029.1 — Reporte: corregir el drift documental post-merge de Task/029

| Campo | Valor |
| --- | --- |
| Tarea | `Task/029.1-Corregir-Drift-Documental-Post-Merge` |
| Tipo | **Mantenimiento documental.** **No cuenta entre las 41** y **no altera el avance** |
| Estado | **Aprobada** — 2026-09-28, mediante `approved: Task/029.1-Corregir-Drift-Documental-Post-Merge` |
| Repositorios | **Solo `personal-blog-infra`**, y solo bajo `docs/` |
| Rama | `Task/029.1-Corregir-Drift-Documental-Post-Merge`, creada **desde `main`** |
| SHA base | `ce53ec93e1a4e78e635eeaa3740f249f5dfc18f1` |
| Avance | **29/41 ≈ 71 %** — **sin cambios** · ETAPA 09 **3/3** — sin cambios |

> **Resultado en una frase.** La auditoría encontró **nueve** afirmaciones invalidadas por el
> cierre de `Task/029`, no una: la frase de Git que ya estaba identificada, **tres cifras de
> gates inconsistentes entre sí** y **cuatro estados que seguían diciendo «Propuesta»** después
> de la aprobación —más una cifra de este propio reporte, que detectó el usuario en la revisión
> (§5.2)—. Las nueve corregidas, **preservando la historia**. `C = 0`.

## 1. Estado Git inicial

| Validación | Resultado |
| --- | --- |
| `git fetch --prune origin` | Sin cambios pendientes |
| `main` vs `origin/main` | **Coinciden**: `ce53ec93e1a4e78e635eeaa3740f249f5dfc18f1` |
| Árbol de trabajo | **Vacío** en los tres repositorios |
| `dev` normalizado | `076b2f5f86498de3990d772a8c35b76443d1a0d9` = `origin/dev`; `git diff main dev` **vacío**; `dev..main` = **0** |
| `Task/029.1` preexistente | **No**: 0 local, 0 remota |
| Rama creada | `git switch -c` **desde `main`**, con `HEAD == main` (`ce53ec9`) verificado |

## 2. Archivos modificados

| Archivo | Cambio |
| --- | --- |
| `docs/task-reports/TASK-029-report.md` | **§13.1 nueva** con las dos fases de Git; cifra de enlaces |
| `docs/tasks/TASK-029-prepare-production-postgresql-rds.md` | Dos cifras de enlaces |
| `docs/project-management/STATUS.md` | Nota de aporte a riesgos; intro de **R-47**; *Vista rápida* |
| `docs/project-management/ROADMAP.md` | Fila de `Task/029` |
| `docs/tasks/TASK-029.1-correct-post-merge-documentation-drift.md` | **Nuevo.** Ficha |
| `docs/task-reports/TASK-029.1-report.md` | **Nuevo.** Este reporte |

`git diff --stat` al cierre: **4 archivos versionados, +104 / −9**, más los **2 nuevos** de esta
tarea —que `diff --stat` no cuenta por no estar versionados aún—: **6 en total**. **`terraform/`, `scripts/`,
`bootstrap/`, `docker-compose.yml` y los workflows: sin un solo cambio.**

## 3. Drift corregido

### 3.1 El drift ya identificado

`docs/task-reports/TASK-029-report.md` §13 afirmaba:

> `- **Sin commit, sin push, sin PR, sin merge**, conforme a PROJECT_INSTRUCTIONS §6.`

Cierto mientras la tarea estuvo *Lista para validación*; **falso** tras el cierre. Se sustituye
por una **§13.1** que distingue las dos fases **sin borrar la primera**, con los SHA reales:
`d98c03c`, `a3de55d`, `affacaa`, PR **#53**, `ce53ec9` y `076b2f5`, más el CI por SHA.

### 3.2 Tres cifras de gates que se contradecían

La auditoría destapó algo que no se había detectado: el mismo entregable declaraba **tres
cifras distintas** de enlaces comprobados.

| Ubicación | Decía | Dice |
| --- | --- | --- |
| Ficha §6, criterio 10 | **497** | **530** |
| Ficha §9, tabla de gates | **526** | **530** |
| Reporte §9, tabla de gates | **526** | **530** |

Se fija **530**, que es **lo que el gate de cierre de `Task/029` midió de verdad** y lo que
registra el mensaje del commit `a3de55d`. **No** se usa el número que arroja el árbol después de
esta corrección: eso falsearía lo que aquella tarea comprobó.

**Causa raíz:** las cifras se escribieron en rondas sucesivas y solo se actualizaron algunas
ocurrencias cada vez. El **497** quedó de la primera ronda y los **526** de la segunda,
mientras el valor real subía a 530 al añadirse los enlaces de la aprobación.

### 3.3 Cuatro estados que seguían diciendo «Propuesta»

Al aprobarse `Task/029` se promovieron las decisiones en el registro canónico, pero **cuatro
afirmaciones en STATUS y ROADMAP no se actualizaron**:

| Ubicación | Decía | Dice |
| --- | --- | --- |
| STATUS — nota de aporte a la tabla de riesgos | «Aporte de `Task/029`, 2026-09-27 — **Propuesta pendiente de aprobación**» | «Aporte de `Task/029`, **aprobada** el 2026-09-27» |
| STATUS — intro de **R-47** | «Añadido el 2026-09-27, con `Task/029` **Lista para validación**» | «Añadido el 2026-09-27, **cuando** estaba Lista para validación; la tarea quedó **aprobada** ese mismo día y **R-47 sigue Abierto**» |
| STATUS — *Vista rápida* | «Entrega D-22, D-23, D-24 y D-10 **como Propuesta**» | «Dejó D-22, D-23, D-24 y D-10 **Resueltas** y **EX-029-D13** Aceptada y Vigente; D-12 **sigue abierta**» |
| ROADMAP — fila de `Task/029` | «**entregadas como Propuesta**» | «**quedaron Resueltas**; D-12 **sigue abierta**» |

**No cambian ninguna decisión**: alinean STATUS y ROADMAP con lo que
[open-decisions.md](../architecture/open-decisions.md) ya declaraba desde la aprobación. La de
**R-47** es estrictamente documental: el riesgo conserva severidad **Alta**, sigue **Abierto** y
su mitigación no se toca.

## 4. Auditoría A / B / C

Barrido sobre **todo `docs/`** con coincidencia **por límite de palabra**, no por subcadena:
`sin commit`, `sin push`, `sin PR`, `sin merge`, `Lista para validación`, `pendiente de
aprobación`, `PR #53`, `rama Task/029`, `no fusionado`, `Task/029.1`.

**Precisión necesaria:** el primer intento buscaba `sin PR` como subcadena y capturaba «sin
**Pro**xy», «sin **pro**pietario», «sin **pro**cesos residentes» y «sin **pro**visionar» —cuatro
falsos positivos—. Con límite de palabra: **414 → 48** apariciones en contexto de `Task/029`.

| Clase | Recuento | Qué son |
| --- | --- | --- |
| **A — historia válida** | **36** | Entradas fechadas de `Task/028`, `Task/028.2`, `Task/005.3` y `Task/001`; la auditoría de referencias de `Task/028.2`; los criterios de `Task/028.1`; la entrada fechada de la ronda 1 de `Task/029`, que el proyecto conserva por convención |
| **B — estado actual válido** | **4** | Cabeceras de ficha y reporte que ya dicen **Aprobada**; la fila de *Última tarea canónica aprobada*; el criterio 10 de la ficha, que enuncia el **estado de salida exigido**, no un estado actual |
| **C — drift real** | **9 → 0** | Las ocho de la §3 más la cifra de la §5.2, todas corregidas |

**Historia ajena intacta:** ni una línea de `Task/028`, `Task/028.2`, `Task/005.3` o
`Task/001` modificada. Verificado: el `git diff` solo toca los cuatro archivos de la §2.

## 5. Gates

| Gate | Resultado |
| --- | --- |
| `git diff --check` | **OK** — sin hallazgos |
| UTF-8 / LF / controles / BOM | **OK** — **6 archivos** del entregable definitivo (4 modificados + 2 nuevos), 0 CRLF, 0 CR sueltos, 0 controles, 0 BOM |
| Enlaces y anclas en **todo `docs/`** | **OK** — **1.867** enlaces relativos, **0 rotos** |
| Encabezados duplicados | **13**, todos **preexistentes en `main`** e **idénticos sin mis cambios**: 10 en STATUS, 2 en `TASK-024-report.md`, 1 en `open-decisions.md`. **Ninguno** en los archivos de esta tarea. Fuera de alcance: son historia de otras tareas |
| Auditoría de referencias | **OK** — **C = 0** |
| Grafo de tareas | **OK** — 0 ciclos, 0 dependencias hacia una tarea posterior |
| Gitleaks 8.30.1 | **OK** — 0 *leaks* sobre el entregable versionado |
| `terraform/` | **Sin cambios** |
| Backend / frontend | **Intactos**: `main`, 0 cambios, `4a40364` / `7dce98a` |
| Contadores | **29/41 ≈ 71 %** y **ETAPA 09 3/3** sin cambios |
| `Task/030` | **Pendiente, no iniciada** |

### 5.1 Un falso positivo corregido en el propio gate

La primera ejecución reportó **39** encabezados duplicados, con slugs **vacíos** repetidos. Era
un defecto del gate, no de la documentación: calculaba el *slug* sobre el texto **ya despojado de
los *code spans***, así que un encabezado como ``### `GET /api/posts` `` quedaba vacío. **GitHub
conserva el contenido del *code span***, y el *slug* real es `get-apiposts`.

La corrección separa dos limpiezas que no son intercambiables: **para buscar enlaces** se quitan
fences **y** *code spans* —un `[x](y)` dentro de comillas no es un enlace—; **para calcular
anclas** se quitan **solo** los fences. Con eso: **39 → 13**, y los 13 son reales y
preexistentes.

### 5.2 Una cifra de este propio reporte también derivó

Este reporte afirmaba que el gate de texto verificó **5 archivos**. Era el resultado de una
ejecución **intermedia**, anterior a la creación de este mismo archivo: al añadirse, el
entregable pasó a **6**. Corregido a **6 archivos (4 modificados + 2 nuevos)**, con el desglose
explícito para que el número no pueda volver a quedar huérfano de su contexto.

Es la **tercera** cifra de gate que deriva en esta cadena de tareas —tras el 497 y el 526 de
`Task/029`—, y la causa es siempre la misma: **anotar el resultado de un gate antes de que el
entregable esté cerrado**. Regla que queda: **las cifras de gates se escriben en la última
ejecución, no en la primera**, y se acompañan del desglose que las hace verificables.

## 6. Límites

- **Cero recursos AWS.** Cero `apply`, `import`, `destroy`, `-target`; *state* intacto.
- **Cero secretos.** Billing sin tocar.
- **`terraform/` sin un solo cambio.**
- **`Task/029` no se reabre:** no se toca ninguna decisión, ni **D-10**, ni **D-22**, ni
  **D-23**, ni **D-24**, ni **EX-029-D13**. El contenido sustantivo de **R-47** no cambia.
- **Contadores intactos:** 29/41 y ETAPA 09 3/3.
- **`Task/030` no iniciada.**
- **Backend y frontend intactos**, sin rama.
- **Pre-aprobación:** sin commit, sin push, sin PR ni merge, y `dev` sin tocar. **Post-aprobación:**
  flujo de cierre de §8 ejecutado el 2026-09-28, con su propio PR `Task/029.1-… → main`.

## 7. Aprobación

| Campo | Valor |
| --- | --- |
| Estado | **Aprobada** |
| Fecha de aprobación | **2026-09-28** |
| Aprobado por | **El usuario**, con la expresión exacta requerida |
| Expresión requerida | `approved: Task/029.1-Corregir-Drift-Documental-Post-Merge` |

**Aprobada el 2026-09-28.** El mantenimiento **no cuenta entre las 41** y **no alteró el avance**:
**29/41 ≈ 71 %** y ETAPA 09 **3/3**, sin cambios. **Ninguna decisión se tocó** —D-10, D-22, D-23,
D-24, EX-029-D13 y el fondo de R-47 intactos— y **cero recursos AWS**. Ficha:
[TASK-029.1-correct-post-merge-documentation-drift.md](../tasks/TASK-029.1-correct-post-merge-documentation-drift.md).
