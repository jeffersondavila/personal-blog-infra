# Reporte — TASK-004.2 · Corregir el drift documental posterior a la fusión de `Task/004.1`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/004.2-Corregir-Drift-Documental-Post-Merge` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Cuenta en el roadmap** | **No.** Avance global (**17 de 41**) y ETAPA 05 (**2 de 3**) **sin cambios** |
| **Estado final** | **Aprobada** ✔ — cerrada el 2026-09-06 |
| **Expresión de aprobación** | `approved: Task/004.2-Corregir-Drift-Documental-Post-Merge` |
| **Repositorio** | `personal-blog-infra` (**únicamente**) |
| **Rama** | `Task/004.2-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`** |
| **SHA base** | **`a90cc55f4683d2d31df63ff4890f47f90f478d1f`** |
| **Fecha** | 2026-09-06 |
| **Ficha** | [TASK-004.2](../tasks/TASK-004.2-correct-post-merge-documentation-drift.md) |
| **Commits** | **1**, creado **después** de la aprobación explícita del usuario |
| **Pull request** | `Task/004.2 → main`, creado durante el cierre aprobado. **Su número y su estado se consultan en vivo** (`gh pr list --head Task/004.2-Corregir-Drift-Documental-Post-Merge`), no en este documento: [WORKFLOW §6.1](../project-management/WORKFLOW.md) |

---

## 1. Punto de partida

`Task/004.1` fue **aprobada** el 2026-09-06. Su cierre creó el pull request `#31`
`Task/004.1 → main` y lo dejó, correctamente, **sin fusionar**: aceptar un PR es
responsabilidad exclusiva del usuario.

El usuario lo fusionó el 2026-09-07 y eliminó la rama remota. La normalización `main → dev`
se ejecutó a continuación.

Desde ese momento, las afirmaciones que los documentos de `Task/004.1` hacían **en
presente** sobre el estado del PR dejaron de ser ciertas.

## 2. Regla aplicada

[WORKFLOW §6.1](../project-management/WORKFLOW.md), vigente desde `Task/005.6`:

> Los documentos versionados registran **estado duradero**. El estado transitorio de Git y
> GitHub —PR abierto o fusionado, rama remota, sincronización actual— se **consulta en
> vivo** y solo se archiva como **observación fechada**.

`Task/004.1` cumplió el invariante de ramas y el flujo de aprobación, pero **no** esta
regla: persistió estado vivo.

## 3. Drift encontrado

Barrido sobre los cuatro documentos, buscando `abierto`, `sin fusionar`, `rama remota`,
`esperando`, `working tree`, `sin commit`, `sin push`, `sin PR`, `HEAD`, `origin/` y
`estado actual`. Las coincidencias se clasificaron **semánticamente**, no por
coincidencia literal.

### Categoría C — corregidas

| # | Documento | Texto original | Por qué era C |
| --- | --- | --- | --- |
| C-1 | `TASK-004.1-report.md`, tabla de cabecera | «**Pull request** — `Task/004.1 → main` — **abierto, sin fusionar**» | Estado vivo del PR. Tras la fusión del 2026-09-07 es **falso** |
| C-2 | `TASK-004.1-report.md` §16, tabla de límites | «commit, rama publicada, PR `Task/004.1 → main` **abierto**» | Misma afirmación en presente dentro de una tabla que, por lo demás, es histórica |
| C-3 | `TASK-004.1-report.md` §17, estado final | «El pull request `Task/004.1 → main` queda **abierto y sin fusionar**: aceptarlo es responsabilidad exclusiva del usuario» | Mezcla una **regla permanente** (clase A: la fusión es del usuario) con un **estado vivo** (clase C). Al fusionarse, el conjunto pasó a leerse como falso |
| C-4 | `TASK-004.1-fix-backup-literal-paths.md` §5, criterio 11 | «Sin commit, push ni PR» | Redactado como criterio en presente. La ficha declara la tarea **Aprobada**, y tras la aprobación sí hubo commit, push y PR: el criterio se contradecía con su propia cabecera |

### Categoría B — conservadas sin cambios

Hechos históricos ya fechados o inequívocamente pasados:

- SHA base `0ec1231`, resultados del preflight y `rev-list --count main..HEAD = 0`.
- «Rama publicada **en el cierre**».
- Resultados de validación: RED, GREEN, conjunto `20260907-020539`, verificación,
  restauración, ausencia de secretos.
- «Sin commit, push ni PR **antes** de la aprobación» en la tabla de límites.
- Los dos hallazgos abiertos, que siguen **Abiertos** y están registrados como tales.

### Categoría A — conservadas sin cambios

Reglas y referencias permanentes: que aceptar un PR es responsabilidad exclusiva del
usuario, el comentario del comodín deliberado en el código, y las referencias cruzadas
entre secciones.

### Coincidencias descartadas tras clasificación semántica

| Coincidencia | Clase | Motivo |
| --- | --- | --- |
| «RED de la extracción **pendiente**» | B | Describe la fase RED del propio relato, no estado de Git |
| «**Queda** documentado en el propio código» | A | Afirmación permanente sobre el código |
| «Pendiente de investigar… **no se borran todavía**» | B | Hallazgo abierto real, registrado como **Abierto** en `STATUS.md`. Sigue siendo cierto |
| «**Queda** desbloqueado el trabajo operativo… reset de Portainer» | B | Sigue siendo cierto: el reset no se ha ejecutado |
| Registro de riesgos `R-01`…`R-46` en `STATUS.md` | — | **Preexistente**, no lo introdujo `Task/004.1`. Fuera de alcance |

## 4. Corrección aplicada

### C-1 → B

La fila del pull request pasa a registrar el hecho completo y fechado: número `#31`,
dirección `Task/004.1 → main`, que se creó **durante el cierre aprobado**, que lo **fusionó
manualmente el usuario el 2026-09-07** y el merge commit `a90cc55`.

### C-2 → B

La fila de límites conserva lo que demuestra —que commit, push y PR ocurrieron **solo
después** de `approved:`— y añade el commit concreto `27f1696`, eliminando el adjetivo
«abierto».

### C-3 → B, separando la regla del hecho

El párrafo de cierre separa ahora las dos cosas que estaban mezcladas:

- **Regla permanente (A):** el agente no fusionó el PR, porque aceptarlo es responsabilidad
  exclusiva del usuario.
- **Hecho histórico (B):** el usuario lo fusionó el 2026-09-07, merge commit `a90cc55`, y
  eliminó la rama remota.

### C-4 → B

El criterio 11 de la ficha se ancla temporalmente: «Sin commit, push ni PR **mientras la
tarea estuviera pendiente de aprobación**». Deja de contradecir la cabecera.

### Hechos históricos añadidos

No son correcciones de drift, sino evidencia que faltaba y que la regla **sí** permite
persistir:

| Documento | Añadido |
| --- | --- |
| `TASK-004.1-fix-backup-literal-paths.md` | Fila **Pull request** con `#31`, dirección, fusión manual del usuario el 2026-09-07 y merge commit `a90cc55` |
| `STATUS.md`, sección de `Task/004.1` | Fila **Pull request** con la convención *«Observado el …»* y fila **Normalización posterior** con `main` = `a90cc55`, `dev` = `cc37bf8`, `git diff main dev` vacío y `main` ancestro de `dev` |
| `STATUS.md`, «Estado de los repositorios» | Bloque **«Observado el 2026-09-07»** siguiendo el precedente de `Task/005.2` y `Task/012`: nacimiento desde `main`, commit de cierre, integración en `dev`, PR `#31`, fusión por el usuario, `mergedAt`, eliminación de la rama remota y verificación posterior |

## 5. Verificación

| Comprobación | Resultado |
| --- | --- |
| Afirmaciones de clase **C** restantes en los cuatro documentos | **0** |
| Evidencia histórica eliminada | **Ninguna** |
| Enlaces documentales | Verificados |
| Avance del roadmap | **17 / 41 = 41 %**, ETAPA 05 **2 / 3 = 67 %** — sin cambios |
| Finales de línea | Sin churn; el diff solo contiene las líneas corregidas |
| `personal-blog-backend` / `personal-blog-frontend` | **No tocados** |
| Docker, Compose, Portainer | **No tocados** |

## 6. Archivos

### Creados

| Archivo |
| --- |
| `docs/tasks/TASK-004.2-correct-post-merge-documentation-drift.md` |
| `docs/task-reports/TASK-004.2-report.md` |

### Modificados

| Archivo | Cambio |
| --- | --- |
| `docs/task-reports/TASK-004.1-report.md` | C-1, C-2 y C-3 convertidas en hechos fechados |
| `docs/tasks/TASK-004.1-fix-backup-literal-paths.md` | C-4 anclada temporalmente; fila **Pull request** añadida |
| `docs/project-management/STATUS.md` | Filas **Pull request** y **Normalización posterior**; observación fechada del 2026-09-07 |
| `docs/task-reports/README.md` | Fila de `Task/004.2` en el índice |

## 7. Nota sobre la causa estructural

`Task/005.6` introdujo la regla de WORKFLOW §6.1 precisamente para **dejar de necesitar**
una tarea de mantenimiento después de cada fusión. `Task/004.1` volvió a persistir estado
vivo del PR en su cierre, así que la regla existía pero no se aplicó.

Esto no se corrige con más documentación: es una comprobación que corresponde al **momento
del cierre aprobado**, antes de redactar la cabecera del reporte. Queda anotado como
observación, no como cambio de regla — la regla ya es correcta.

## 8. Cómo se cerró esta tarea, y por qué así

**Aprobada** ✔ el 2026-09-06 mediante
`approved: Task/004.2-Corregir-Drift-Documental-Post-Merge`.

El cierre aplica a sí mismo la regla que esta tarea corrige. `Task/004.1` dejó escrito en su
reporte que el PR estaba «abierto, sin fusionar», y eso fue exactamente el drift que hubo
que reparar. Aquí **no se persiste el estado del pull request**: los documentos registran
que se creó un PR `Task/004.2 → main` durante el cierre y remiten a `gh` para consultarlo.

Su número, su fusión y el merge commit se archivarán como **observación fechada** en la
normalización posterior, que es el momento en que esos hechos ya son históricos. Es el mismo
patrón que el proyecto usó con `Task/005.2`, cuyos datos de fusión se registraron al iniciar
`Task/005.3`.

El trabajo operativo sobre Portainer sigue en espera y no se ha iniciado.
