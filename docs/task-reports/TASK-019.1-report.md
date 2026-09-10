# Reporte — TASK-019.1 · Corregir el drift documental posterior a la fusión de `Task/019`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/019.1-Corregir-Drift-Documental-Post-Merge` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Cuenta en el roadmap** | **No.** Avance global (**19 de 41**) y ETAPA 06 (**1 de 3**) **sin cambios** |
| **Estado final** | **Aprobada** ✔ — cerrada el 2026-09-09 |
| **Expresión de aprobación** | `approved: Task/019.1-Corregir-Drift-Documental-Post-Merge` |
| **Repositorio** | `personal-blog-infra` (**únicamente**) |
| **Rama** | `Task/019.1-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`** |
| **SHA base** | **`32474e5abc5f52aedf84f4231b16f3c868905b79`** |
| **Fecha** | 2026-09-09 |
| **Ficha** | [TASK-019.1](../tasks/TASK-019.1-correct-post-merge-documentation-drift.md) |
| **Commits** | **1**, creado **después** de la aprobación explícita del usuario |
| **Pull request** | `Task/019.1 → main`, creado durante el cierre aprobado. **Su número y su estado se consultan en vivo** (`gh pr list --head Task/019.1-Corregir-Drift-Documental-Post-Merge`), no en este documento: [WORKFLOW §6.1](../project-management/WORKFLOW.md) |

---

## 1. Punto de partida

`Task/019` fue **aprobada** el 2026-09-08. Su cierre creó los pull request `#12`
(frontend) y `#34` (infra), ambos `Task/019-CI-Frontend → main`, y los dejó
correctamente **sin fusionar**.

*Observado el 2026-09-09 UTC:* el usuario los fusionó manualmente y eliminó las dos ramas
Task remotas. La normalización `main → dev` se ejecutó a continuación y quedó verificada.

| Repositorio | PR | `mergedAt` | Merge commit | Normalización `dev` |
| --- | --- | --- | --- | --- |
| frontend | `#12` | 2026-09-09T03:50:31Z | `7dce98a` | `b261e65` |
| infra | `#34` | 2026-09-09T03:50:13Z | `32474e5` | `efeb6b8` |

**La normalización de Git no forma parte de esta tarea** y no se repite: ya está
completada y verificada. Esta tarea es exclusivamente documental.

## 2. Regla aplicada

[WORKFLOW §6.1](../project-management/WORKFLOW.md), vigente desde `Task/005.6`:

> Los documentos versionados registran **estado duradero**. El estado transitorio de Git y
> GitHub —PR abierto o fusionado, rama remota, sincronización actual— se **consulta en
> vivo** y solo se archiva como **observación fechada**.

## 3. Causa del drift

`Task/019` se diferencia de las tareas anteriores en un punto concreto: **parte de su
evidencia solo podía existir durante su propio cierre aprobado**.

El trigger `pull_request` del workflow no se ejecuta sin un pull request, y crear un PR
antes de la aprobación está prohibido. El verde sobre `dev` no existe hasta integrar. Así
que, cuando se redactó y commiteó la documentación, lo único acreditado era el trigger
`push` mediante la ejecución de bootstrap. Los documentos lo dijeron **en presente**.

Minutos después, el propio flujo aprobado produjo la evidencia que faltaba. Desde ese
momento, decir «Task019 no aporta evidencia de `pull_request`» pasó a ser **falso**.

No es un defecto del workflow ni una omisión: es la consecuencia esperable de documentar
antes de que el cierre genere su última evidencia. El criterio 12 existe para detectarlo, y
lo detectó en la normalización.

A ese cluster se sumó una contradicción de otra naturaleza: la tabla del criterio 12 del
reporte de `Task/019` seguía calificando sus decisiones técnicas de *Propuesta — pendiente
de aprobación*, cuando la aprobación ya las había promovido a **vigentes** en la ficha §12
y en STAGE-06. Es contradicción documental, no estado de Git, y por eso se clasifica
aparte como **D**.

## 4. Drift encontrado

### Categoría C — corregidas

| # | Archivo | Texto original |
| --- | --- | --- |
| **C-1** | `docs/stages/STAGE-06-continuous-integration.md` | «el trigger `pull_request` está declarado en el YAML, pero **Task019 no aporta evidencia de ninguna ejecución con ese evento**: se comprueba en el cierre ordinario autorizado» |
| **C-2** | `docs/stages/STAGE-06-continuous-integration.md` | «la ejecución real de `pull_request` y el verde sobre `dev` **se comprueban** en el cierre ordinario autorizado» |
| **C-3** | `docs/task-reports/TASK-019-report.md` §J | «El trigger `pull_request` está declarado en el YAML y fue inspeccionado, pero **Task019 no aporta evidencia de ninguna ejecución con ese evento**» |
| **C-4** | `docs/task-reports/TASK-019-report.md` §P | «Lo siguiente **sigue sin estar validado por Task019**: … **Normalización `main → dev`** posterior a la fusión, que solo puede ocurrir después de que el usuario acepte el pull request» |
| **C-5** | `docs/tasks/TASK-019-ci-frontend.md` §4 | «La ejecución real del trigger `pull_request` y el verde sobre `dev` **se validan** durante el cierre autorizado» |
| **C-6** | `docs/tasks/TASK-019-ci-frontend.md` §17 | «El trigger PR **se comprueba** en el cierre ordinario» |
| **C-7** | `docs/tasks/TASK-019-ci-frontend.md` §18 | «En el cierre autorizado de Task019: ejecución `pull_request` y verde sobre dev» — listado como **deuda pendiente** |
| **C-8** | `docs/project-management/STATUS.md` | «El cierre **integra** cada rama en `dev` … **abre** el pull request … Las ramas Task locales **se eliminan** … las remotas **se conservan**» |

### Categoría D — corregida

| # | Archivo | Texto original |
| --- | --- | --- |
| **D-1** | `docs/task-reports/TASK-019-report.md` §N | «Las decisiones técnicas quedan como **Propuesta — pendiente de aprobación**», ya contradicho por la ficha §12 y por STAGE-06, donde figuran como **vigentes** desde el 2026-09-08 |

### Categoría B — conservadas sin cambios

- El preflight de la ficha §0 y del reporte §A: «Observado el 2026-09-08 … `HEAD == main`,
  cero commits adicionales y árbol limpio». Está fechado y era cierto.
- El baseline con **702 de 703** y el timeout de `formularios.test.tsx`, con su fecha.
- Los controles negativos locales, sus exit codes, hashes y duraciones.
- La ejecución **34305529115** y todos sus datos.
- La autorización excepcional de bootstrap del 2026-09-08.
- La frase, ahora explícita, de que **al redactarse el bootstrap solo estaba acreditado
  `push`**: es un hecho fechado correcto y se conserva, reforzando su anclaje temporal.

### Categoría A — conservadas sin cambios

- El diseño del workflow, sus gates y su orden.
- El reparto de responsabilidades de S-09 entre Task019, Task020 y Task021.
- La asignación del escaneo del historial de secretos a Task021.
- Los criterios de salida de STAGE-06, que **siguen sin marcar**: exigen los tres
  repositorios y Task019 solo acredita el frontend.
- La regla de que aceptar un PR y borrar la rama remota es responsabilidad exclusiva del
  usuario, separada ahora del hecho fechado de que lo hizo.

### Coincidencias descartadas tras clasificación semántica

| Coincidencia | Por qué no es drift |
| --- | --- |
| Reporte §B, «Verde sobre dev en los tres repositorios / Cierres aprobados y salida global de STAGE-06» | Sigue siendo cierto: faltan Task020 y Task021 |
| Reporte §F, fila «Triggers: `push` y `pull_request`» | Descripción del diseño, clase A |
| Reporte §K, «No hay `pull_request_target`» | Afirmación de seguridad del YAML, clase A |
| STAGE-06, «el escaneo del historial … se comprueba al cerrar la etapa» | Sigue pendiente de verdad, propiedad de Task021 |
| STAGE-06, los cuatro criterios de salida sin marcar | Correctamente abiertos |
| STATUS §Task/018, «Avance: **18/41 — 44 %**» | Hecho fechado del cierre de Task018 |
| ROADMAP, fila de Task019 citando la ejecución 34305529115 | Cita una ejecución real; no niega las otras |
| Menciones a **ADR-009 en Propuesta** y **D-21 abierta** | Ajenas a Task019; siguen siendo ciertas |

## 5. Corrección aplicada

**C-1 y C-2 → B.** STAGE-06 conserva la ejecución de bootstrap como evidencia del trigger
`push` y añade una observación fechada del 2026-09-09 UTC con las ejecuciones
**34308296565** (`pull_request`) y **34308234554** (`push` sobre `dev`), ambas `success`.
Se conserva que el control negativo remoto sigue sin autorizarse y que ninguna de esas
observaciones completa la etapa por sí sola.

**C-3 → B, separando los dos momentos.** El §J del reporte de `Task/019` ahora dice
explícitamente que **al redactarse el bootstrap** solo estaba acreditado `push`, y añade
una tabla fechada con los tres runs. Los dos momentos quedan distinguidos, que es
exactamente lo que el texto anterior fundía.

**C-4 → B.** El §P incorpora los datos de la fusión y de la normalización como hechos
fechados, y reduce la lista de pendientes a lo que sigue realmente abierto: el verde de los
tres workflows sobre `dev`, el control negativo remoto y **R-016-1**.

**C-5, C-6 y C-7 → B.** La ficha de `Task/019` fecha en §4 la obtención de ambas
evidencias, precisa en §17 que el trigger `pull_request` no se comprobó antes de aprobar
sino en el cierre, y retira de §18 la deuda ya saldada dejando constancia de por qué dejó
de serlo. Lo que sigue siendo deuda permanece.

**C-8 → B.** El bloque de STATUS pasa a pretérito, incorpora los números de PR, y separa la
**regla permanente** —aceptar el PR y borrar la rama remota es del usuario— del **hecho
fechado** de que lo hizo el 2026-09-09 UTC. Se añade un bloque fechado con `mergedAt`,
merge commits, merges de normalización y la verificación de que `main` es ancestro de `dev`
con diff vacío.

**D-1 → corregido.** La fila de clase A de la tabla del criterio 12 del reporte de
`Task/019` ahora dice que las decisiones quedaron **vigentes** con la aprobación del
2026-09-08 y que **antes de ella** se mantuvieron como *Propuesta*. Se conserva el hecho
histórico sin sostener la contradicción. La fila de clase B se amplía para citar las tres
ejecuciones remotas en lugar de solo una.

## 6. Verificación

| Comprobación | Resultado |
| --- | --- |
| Barrido de clase **C** sobre los cinco documentos | **C = 0** |
| Contradicciones de clase **D** | **D = 0** |
| Evidencia histórica eliminada | **Ninguna** |
| Contadores del roadmap alterados | **Ninguno** — 19/41, 46 %, ETAPA 06 1/3, 33 % |
| Archivos de `personal-blog-frontend` o `personal-blog-backend` tocados | **Ninguno** |
| Workflow, configuración de Vite o TypeScript tocados | **Ninguno** |
| `git diff --check` | Limpio |
| Enlaces relativos de los documentos modificados | Verificados |
| Búsqueda de secretos en archivos modificados | Sin hallazgos |
| Finales de línea | LF, conforme a `.gitattributes` |

## 7. Archivos

### Creados

- `docs/tasks/TASK-019.1-correct-post-merge-documentation-drift.md`
- `docs/task-reports/TASK-019.1-report.md`

### Modificados

- `docs/tasks/TASK-019-ci-frontend.md` — §4, §17 y §18.
- `docs/task-reports/TASK-019-report.md` — §J, §N y §P.
- `docs/stages/STAGE-06-continuous-integration.md` — evidencia de la tarea y criterios.
- `docs/project-management/STATUS.md` — bloque de cierre en «Estado de los repositorios»,
  hechos de la fusión y normalización, y fila de tarea en curso.
- `docs/task-reports/README.md` — índice.

`DEFINITION_OF_DONE.md` y `WORKFLOW.md` **no se modifican**.

## 8. Nota sobre la causa estructural

Este es el quinto mantenimiento del mismo tipo, tras `Task/004.2`, `Task/006.1`,
`Task/009.1` y `Task/013.1`. En los anteriores la causa era escribir en presente el estado
de un PR recién creado. **Aquí la causa es distinta y vale la pena registrarla**: `Task/019`
fue la primera tarea cuya evidencia dependía de su propio cierre.

De ahí se deriva una lección aplicable a `Task/020` y `Task/021`, que tendrán exactamente
el mismo problema: **cuando una tarea de CI documente lo que aún no puede ejecutar,
conviene redactarlo desde el principio como «al momento de este reporte no se había
observado X», nunca como «la tarea no aporta evidencia de X»**. La primera forma envejece
sin volverse falsa; la segunda no.

Esta observación **no modifica el WORKFLOW ni la Definition of Done**, y no se propone como
regla nueva: queda registrada para quien redacte `Task/020`.

## 9. Pasos de validación para el usuario

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

# 1. La rama nacio de main y no hay nada publicado
git rev-parse HEAD; git rev-parse main
git rev-list --count main..HEAD
git diff --cached --name-only

# 2. Ya no queda ninguna afirmacion de clase C
Select-String -Path docs/tasks/TASK-019-ci-frontend.md, `
  docs/task-reports/TASK-019-report.md, `
  docs/stages/STAGE-06-continuous-integration.md `
  -Pattern "no aporta evidencia"

# 3. Los contadores siguen intactos
Select-String -Path docs/project-management/STATUS.md -Pattern "19 de 41"
Select-String -Path docs/project-management/ROADMAP.md -Pattern "19 / 41"

# 4. Frontend y backend intactos
git -C ..\personal-blog-frontend status --short
git -C ..\personal-blog-backend status --short
```

## 10. Riesgos y deuda

Esta tarea **no abre riesgos nuevos** y no cierra ninguno existente. **R-016-1** sigue
abierto. Los criterios de salida de STAGE-06 siguen abiertos y son propiedad de `Task/020`
y `Task/021`. El control negativo remoto sigue sin autorizarse.

## 11. Próxima tarea

`Task/020-CI-Backend` — **Pendiente, no iniciada**. No se inicia en esta tarea. Toda nueva
Task nace desde `main` actualizado y limpio.

## 12. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-09** |
| **Aprobado por** | El usuario |
| **Expresión recibida** | `approved: Task/019.1-Corregir-Drift-Documental-Post-Merge` |

El cierre integró la rama en `dev` con merge `--no-ff`, publicó `dev` y la rama Task, y
abrió el pull request `Task/019.1 → main`. **Aceptarlo o rechazarlo es responsabilidad
exclusiva del usuario.** La rama Task local se eliminó con `git branch -d`.
