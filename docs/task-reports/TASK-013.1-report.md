# TASK-013.1 — Corregir el drift documental posterior a la fusión de `Task/013` — Reporte

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/013.1-Corregir-Drift-Documental-Post-Merge` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Cuenta en el roadmap** | **No.** Avance global **13 de 41** y ETAPA 04 **1 de 3**, ambos **sin cambios** |
| **Estado** | **Aprobada** ✔ (2026-09-04) |
| **Repositorios** | `personal-blog-infra` (**únicamente**) |
| **Rama** | `Task/013.1-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`** |
| **SHA base** | `38a8cdd4491f65e647aa1e735919d06e00f425ac` |
| **Fecha** | 2026-09-04 · **aprobada** el 2026-09-04 |
| **Ficha** | [`TASK-013.1`](../tasks/TASK-013.1-correct-post-merge-documentation-drift.md) |

---

## 1. Qué se corrigió

Una sola afirmación de categoría **C**: la sección 24 del reporte de `Task/013`
conservaba contadores de Git y GitHub redactados en presente, mientras la cabecera del
mismo documento declara la tarea **Aprobada**.

Se convirtió en **instantánea histórica fechada**. Los valores originales quedan intactos.

---

## 2. Baseline Git

| Comprobación | Resultado |
| --- | --- |
| `main` | `38a8cdd4491f65e647aa1e735919d06e00f425ac` |
| `origin/main` | `38a8cdd4491f65e647aa1e735919d06e00f425ac` |
| `main == origin/main` | ✔ |
| Working tree antes de crear la rama | limpio |
| Ramas Task locales antes | **0** |
| `git rev-parse HEAD` tras crear la rama | `38a8cdd…` |
| `HEAD == main` | ✔ |
| `git rev-list --count main..HEAD` | **0** |

**La rama nació de `main`.** `dev` no intervino como base.

---

## 3. El hallazgo, antes del cambio

`docs/task-reports/TASK-013-report.md`, sección 24:

```markdown
## 24. Estado de Git al cerrar

| Repositorio | Rama | *Staging* | Commits sobre `main` | Push | Merge | PR |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| frontend | `Task/013-Sistema-de-Diseno` | **0** | **0** | **0** | **0** | **0** |
| infra | `Task/013-Sistema-de-Diseno` | **0** | **0** | **0** | **0** | **0** |
| backend | `main` — limpio, 0 cambios | **0** | **0** | **0** | **0** | **0** |

Los cambios están **sin commit**, como corresponde a una tarea no aprobada
([`PROJECT_INSTRUCTIONS`](../claude/PROJECT_INSTRUCTIONS.md) §6).
```

### Por qué era categoría C

1. **Afirma estado operativo de Git y GitHub en presente**: ramas Task activas, `0`
   commits, `0` push, `0` PR. Por la tabla de
   [WORKFLOW §6.1](../project-management/WORKFLOW.md), todo eso es **transitorio** y no se
   versiona como estado vigente.
2. **No llevaba fecha de observación.** El encabezado «al cerrar» marca una fase, no un
   momento; §6.1 punto 2 exige fecha explícita para que *«el paso del tiempo no lo vuelva
   falso»*.
3. **Contradice al propio documento.** La cabecera dice `Estado: Aprobada ✔ (2026-09-04)`
   y la sección 25, inmediatamente posterior, repite `Task/013 — Aprobada`. La frase «como
   corresponde a una tarea **no aprobada**» las contradice a las dos.
4. Leída hoy es **falsa**: los cambios están commiteados (`452c86d`, `213890f`), los PR se
   fusionaron y las ramas Task ya no existen.

Es el mismo patrón que `Task/005.6` corrigió con «Los PR siguen abiertos» y que
`Task/006.1` y `Task/009.1` volvieron a limpiar tras sus respectivas fusiones.

### Una precisión: es una regresión, no una laguna

La forma correcta **ya existía en el proyecto**. Los reportes de `Task/008` y `Task/009`
encabezan su instantánea así:

> **Estado de Git: observación fechada, no estado vigente.** […]
>
> > *Observado el 2026-08-27, **antes** de la aprobación:* …

El reporte de `Task/013` no aplicó ese patrón establecido. Por eso la corrección consiste
en **alinearlo**, no en inventar una convención nueva.

---

## 4. Cambio realizado

### 4.1 `docs/task-reports/TASK-013-report.md`

| Elemento | Antes | Después | Justificación |
| --- | --- | --- | --- |
| Encabezado | `## 24. Estado de Git al cerrar` | `## 24. Estado de Git previo a la aprobación` | «al cerrar» marca una fase; «previo a la aprobación» sitúa la instantánea en el tiempo de forma inequívoca. |
| Marco | *(ninguno)* | Párrafo que declara los contadores **transitorios** y remite a §6.1, más la línea *«Observado el 2026-09-03, **antes** de la aprobación»* | Es la forma canónica de `Task/008` y `Task/009`. |
| Tabla | 3 filas con ceros | **idéntica** | La evidencia no se altera. |
| Cierre | «Los cambios **están** sin commit, como corresponde a una tarea **no aprobada**» | «En esa instantánea los cambios **se encontraban** sin commit, como **correspondía** a una tarea todavía no aprobada […] Es la evidencia de que el trabajo permaneció sin confirmar hasta la aprobación» | Pasado, anclado a la instantánea. Deja de contradecir a la cabecera y conserva el valor probatorio. |

**No se introdujo** ningún hash actual (`af24284`, `38a8cdd`, `c5edca2`, `7e2369b`), ni el
estado `MERGED` de los PR, ni el borrado de las ramas remotas. Hacerlo habría sustituido un
estado vivo por otro.

### 4.2 `docs/project-management/STATUS.md`

- Fila **Mantenimiento en validación** en la vista rápida.
- Sección propia `## Mantenimiento en validación — Task/013.1`, con qué corrige y **qué no**.
- **Contadores intactos**: avance global **13 de 41 — 32 %**, ETAPA 04 **1 de 3 — 33 %**.

### 4.3 `docs/task-reports/README.md`

- Fila de este mantenimiento, con su enlace al reporte y estado `Lista para validacion`.
- `013.1` añadido a la lista de tareas de mantenimiento que **no cuentan** entre las 41.

Nada más. El índice omite las filas de `Task/010`–`Task/013`; es *drift* preexistente e
**independiente** de este hallazgo, y por decisión del usuario **queda fuera** de este
mantenimiento (ficha §4).

### 4.4 Documentos nuevos

Ficha y este reporte.

### 4.5 Diff resumido

```
docs/project-management/STATUS.md                                |   35 +
docs/task-reports/README.md                                      |    2 +, 1 -
docs/task-reports/TASK-013-report.md                             |   12 +, 4 -
docs/tasks/TASK-013.1-correct-post-merge-documentation-drift.md  |  nuevo
docs/task-reports/TASK-013.1-report.md                           |  nuevo
```

---

## 5. Criterion 12 — barrido posterior a la corrección

| Archivo | Fragmento | Clase | Justificación |
| --- | --- | :---: | --- |
| `TASK-013-report.md` §24 | «Observado el 2026-09-03, **antes** de la aprobación» + tabla + cierre en pasado | **A** | Instantánea fechada. El paso del tiempo ya no la vuelve falsa. **Corregida por esta tarea.** |
| `TASK-013-report.md` §23 | «`Task/013 — Lista para validación` es estado duradero» | **A** | Registro del barrido hecho al cerrar. El **estado de una tarea es duradero** por la tabla de §6.1: no es estado transitorio de Git ni de GitHub. |
| `TASK-013-report.md` §23 | «…ni que haya una normalización en curso» | **A** | Es la **negación** dentro del propio barrido: registra que no había afirmaciones vivas. |
| `TASK-013-report.md` §27 | «`Task/014` no se inicia hasta que `main` y `dev` queden normalizadas» | **B** | Regla de orden avalada literalmente por §6.1 punto 4. No afirma ningún hecho vivo de Git. |
| `TASK-013-report.md` §27 | «La revisión y la fusión del pull request son responsabilidad exclusiva del usuario» | **B** | Regla permanente de reparto de responsabilidades. |
| `TASK-013.1` ficha y reporte | «Aprobada ✔ (2026-09-04)», SHA base `38a8cdd`, instantánea fechada de §7 | **A / B** | Estado de tarea (duradero), SHA base (histórico de creación de rama) y regla permanente de `PROJECT_INSTRUCTIONS` §6. |
| `STATUS.md` §*Estado de los repositorios* | «El estado vivo —si el PR sigue abierto…— no se escribe aquí» | **B** | Enuncia la política del criterio 12. Preexistente. |
| `STATUS.md` §*Task/005* | «*(Corregido en `Task/005.6`: esta viñeta afirmaba «Los PR siguen abiertos»…)*» | **A** | Registro fechado de una corrección histórica. Preexistente. |
| `ROADMAP.md`, `STAGE-04`, `open-decisions.md`, `software-architecture.md` | — | — | **0 apariciones** de categoría C. |

**A = 5 · B = 3 · C = 0**

> **C = 0.** Ningún documento presenta estado operativo vivo de Git o GitHub como verdad
> durable.

---

## 6. Validaciones ejecutadas

| Validación | Resultado |
| --- | --- |
| Barrido de patrones transitorios sobre los documentos tocados | **0** de categoría C |
| Inspección en contexto de cada coincidencia | 8 coincidencias revisadas y clasificadas |
| Coherencia cabecera ↔ sección 24 del reporte de `Task/013` | ✔ sin contradicción |
| Enlaces relativos de los documentos tocados | comprobados, **0 rotos** |
| `git diff --check` | sin hallazgos |
| Contadores de avance | **sin cambios**: 13/41 y 1/3 |

**No ejecutadas, y por qué:** pruebas de frontend y de backend, cobertura, build, Docker,
PostgreSQL y MinIO. Esta tarea **no toca código**; ejecutarlas no aportaría señal.

---

## 7. Estado de Git

**Observación fechada, no estado vigente.** Los contadores de abajo son **transitorios**
por definición —el flujo de cierre los modifica en cuanto hay aprobación—; el estado vivo
se consulta en el momento ([`WORKFLOW`](../project-management/WORKFLOW.md) §6.1).

Se redacta así **a propósito**: escribir «los cambios están sin commit» en presente es
exactamente el defecto que este mantenimiento corrige, y repetirlo aquí lo reintroduciría
en cuanto el usuario aprobara la tarea.

> *Observado el 2026-09-04, **antes** de la aprobación:* rama activa
> `Task/013.1-Corregir-Drift-Documental-Post-Merge` en `personal-blog-infra`, nacida de
> `main` (`38a8cdd`); `git rev-list --count main..HEAD` = **0**, staging **vacío**,
> ningún push y ningún pull request. `personal-blog-frontend` y `personal-blog-backend`,
> en `main` y sin rama. Los cambios permanecían **sin commit**, como correspondía a una
> tarea todavía no aprobada
> ([`PROJECT_INSTRUCTIONS`](../claude/PROJECT_INSTRUCTIONS.md) §6).

---

## 8. Alcance

| Repositorio | Estado |
| --- | --- |
| `personal-blog-infra` | **Único modificado.** 5 archivos |
| `personal-blog-frontend` | **No modificado.** Sin rama |
| `personal-blog-backend` | **No modificado.** Sin rama |

`Task/014-Sitio-Publico` **no iniciada**: sigue **Pendiente**.

---

## 9. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-04** |
| **Aprobado por** | **jeffersondavila** (el usuario) |
| **Expresión de aprobación** | `approved: Task/013.1-Corregir-Drift-Documental-Post-Merge` |

Recibida la aprobación se ejecutó el cierre de
[`WORKFLOW.md`](../project-management/WORKFLOW.md) §3 en `personal-blog-infra`: commit,
integración en `dev` mediante merge `--no-ff` y pull request
`Task/013.1-Corregir-Drift-Documental-Post-Merge → main`.

**La revisión y la fusión del pull request son responsabilidad exclusiva del usuario.**
