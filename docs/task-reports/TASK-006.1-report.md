# Reporte — TASK-006.1 · Corregir el drift documental posterior a la fusión de `Task/006`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/006.1-Corregir-Drift-Documental-Post-Merge` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Cuenta en el roadmap** | **No.** Avance global y ETAPA 02 **sin cambios** |
| **Estado final** | **Aprobada** ✔ (2026-08-21) |
| **Expresión de aprobación** | `approved: Task/006.1-Corregir-Drift-Documental-Post-Merge` |
| **Repositorio** | `personal-blog-infra` (**únicamente**) |
| **Rama base** | **`main`** — `f434666e0cf829e4ee906621e9cc6f2675455032` |
| **Fecha** | 2026-08-19 · cierre aprobado el 2026-08-21 |
| **Ficha** | [TASK-006.1](../tasks/TASK-006.1-correct-post-merge-documentation-drift.md) |
| **Commits** | **1**, creado **después** de la aprobación explícita del usuario |

---

## 1. Origen del drift

El cierre de `Task/006` se redactó **antes** de que el usuario fusionara los pull request.
Ese texto viajó dentro del propio PR hacia `main`; al fusionarlo, el documento ya versionado
siguió afirmando que el PR estaba pendiente.

[`WORKFLOW.md`](../project-management/WORKFLOW.md) §6.1 ya describe este mecanismo y lo
llama *«una afirmación condenada a ser falsa desde que se escribe»*. **El defecto es un
incumplimiento de una regla vigente desde `Task/005.6`, no un hallazgo nuevo.**

## 2. Las 6 afirmaciones — antes y después

| # | Ubicación | Antes | Después |
| --- | --- | --- | --- |
| 1 | `STATUS.md` · Vista rápida → *Última tarea aprobada* | «Pull request `Task/006 → main` **abiertos** en frontend e infra, pendientes de que el usuario los fusione» | «Fundación del frontend en `personal-blog-frontend`, con su gobierno en `personal-blog-infra`. Cierre e integración completados» |
| 2 | `STATUS.md` · nota bajo Vista rápida | «Que sus pull request **sigan abiertos** no afecta al recuento: el estado de la tarea lo fija la aprobación del usuario, no la fusión» | «Lo que fija el recuento es **la aprobación del usuario**, no el trámite posterior de fusionar el pull request ([WORKFLOW §6.1](../project-management/WORKFLOW.md))» |
| 3 | `STATUS.md` · Vista rápida → *Próxima tarea prevista* | «`Task/007` (Pendiente, no iniciada). **No comienza hasta que el usuario apruebe `Task/006`** y se complete su cierre» | «`Task/007-Integracion-Local` — **Pendiente, no iniciada**. Como toda rama Task, **nacerá desde `main`** actualizado y limpio» |
| 4 | `STATUS.md` · sección *Última tarea aprobada — `Task/006`* | «**Pendiente del usuario:** fusionar los pull request… Hasta que eso ocurra y se complete la normalización `main → dev`, `Task/007` no se inicia» | «**Cierre completado.** …el usuario fusionó los pull request… y la normalización `main → dev` se ejecutó después. `Task/007` sigue **Pendiente y no iniciada**… El estado vivo de ramas y pull request se consulta en Git y GitHub, no aquí» |
| 5 | `STAGE-02` · nota de `Task/006` | «Los pull request `Task/006 → main` —frontend e infra— **quedan abiertos**: fusionarlos es responsabilidad exclusiva del usuario» | «**Aprobada** por el usuario el 2026-08-18 y **fusionada en `main`** en ambos repositorios, con la normalización `main → dev` completada» |
| 6 | Ficha `TASK-006` · §19 | «**No se ha iniciado.** No comienza hasta que el usuario fusione el pull request `Task/006 → main` y se complete la normalización `main → dev`» | «Es la **siguiente tarea oficial del roadmap** y está **Pendiente, no iniciada**. Como toda rama Task, **nacerá desde `main`**…» |

Las seis siguen el mismo criterio: en una **superficie viva** el estado de un pull request
se expresa como **hecho duradero** o como **regla permanente**, y lo vivo se consulta en Git
y GitHub.

Conviene no confundir dos formas que se parecen pero no se comportan igual:

| Forma | ¿Envejece? | Ejemplo |
| --- | --- | --- |
| Afirmación **en presente y sin fecha** sobre un trámite | **Sí**, se vuelve falsa | «los pull request **quedan abiertos**» |
| **Observación fechada** | **No.** [WORKFLOW §6.1](../project-management/WORKFLOW.md) punto 2: *«el paso del tiempo no lo vuelve falso»* | «*Observado el 2026-08-19: PR `#5` fusionado*» |

Ambas formas son legítimas; una observación fechada es categoría **A**. Lo corregido aquí es
solo la primera. En las superficies vivas se prefirió la formulación duradera —«cierre e
integración completados»— porque describe el resultado de la tarea sin convertir el
documento en fuente del estado de Git. La trazabilidad fechada de los merges ya existe: vive
en el reporte de `Task/006` y en la sección *Estado de los repositorios* de `STATUS.md`.

## 2.1 Registro de este mantenimiento en `STATUS.md`

[WORKFLOW §6](../project-management/WORKFLOW.md) obliga a actualizar `STATUS.md` **«al
iniciar, al quedar lista y al aprobarse»**, y §6.1 clasifica el **estado de la tarea**
—`Lista para validación` incluido— como **duradero**, con `STATUS.md` entre sus destinos.

Por eso `STATUS.md` registra ahora:

- **Vista rápida** → *Tarea actual*: `Task/006.1`, mantenimiento documental, **Lista para
  validación**, con la nota de que **no cuenta** en las 41 tareas.
- **Vista rápida** → *Estado de la tarea*: **Lista para validación**.
- Sección propia ***Mantenimiento en validación — `Task/006.1`***, con tipo, estado, origen,
  alcance entregado, rama base y el recordatorio de que el avance sigue en **6 de 41** y la
  ETAPA 02 en **2 de 3**.

`Task/006.1` **no** se añadió a las 41 filas oficiales de tareas.

Que ese estado pase después a `Aprobada` mediante un commit autorizado es una **transición
versionada y deliberada**, no drift. El drift es otra cosa: que Git o GitHub cambien por
fuera —un PR que pasa a `MERGED`, una rama remota que desaparece— y el documento siga
afirmando lo contrario.

## 3. Historia preservada

**No se reescribió ninguna observación histórica.** Clasificación de las apariciones que
permanecen:

| Ubicación | Clasificación | Motivo |
| --- | --- | --- |
| `TASK-006-report.md` (4 apariciones) | **A** | El [índice de reportes](README.md) define `docs/task-reports/` como **reporte cerrado**, escrito al finalizar la ejecución. Instantánea fechada, no fuente viva |
| `STATUS.md` · secciones de `Task/001`–`Task/005.7` | **A** | Registros fechados y en pasado de aprobaciones anteriores. El historial **no se reescribe** |
| `STATUS.md` · «`Task/006` sigue Pendiente y no iniciada» (5 apariciones) | **A** | Dentro de las secciones de `Task/005.2`–`005.7`; describen el efecto de aquellos mantenimientos **en su fecha** |
| `STATUS.md` · *Estado de los repositorios* | **A** | Encabezada «**Observado el 2026-08-18**» y precedida por la regla de lectura de WORKFLOW §6.1 |
| `STATUS.md` · WORKFLOW §6.1 y preámbulos | **B** | Reglas duraderas de gobierno |
| `STATUS.md` / `STAGE-02` · riesgos «Abierto» | **B** | Estado de riesgo, no de pull request |

## 4. Verificación

Búsqueda dirigida sobre `STATUS.md`, `STAGE-02` y la ficha `TASK-006`, con 11 patrones de
estado transitorio presentado como vigente:

| Patrón | Coincidencias |
| --- | --- |
| «quedan abiertos», «sigan abiertos», «siguen abiertos», «está abierto», «abierto, sin fusionar» | **0** |
| «Pendiente del usuario», «pendientes de que el usuario» | **0** |
| «hasta que el usuario fusione», «hasta que el usuario apruebe», «no se inicia hasta» | **0** |
| «no comienza hasta» | **1** — dentro de la sección histórica de `Task/005.2`, referida al PR **de aquella tarea**. Categoría **A** |

**Total categoría C: 0.**

## 5. Límites respetados

| Límite | Cumplimiento |
| --- | --- |
| Solo `personal-blog-infra` | ✔ 0 cambios en frontend y backend; sin rama Task en ellos |
| `ROADMAP.md` sin tocar | ✔ Tuvo 0 apariciones de categoría C |
| Contadores sin cambiar | ✔ **6 de 41 (15 %)**, ETAPA 02 **2 de 3 (67 %)** |
| 41 identificadores intactos | ✔ `Task/006.1` **no** aparece entre las 41 filas |
| Historia no reescrita | ✔ Ver §3 |
| Sin cambios funcionales | ✔ 0 código, pruebas, Compose, Terraform, ADR, riesgos y decisiones |
| Commits solo tras la aprobación | ✔ 0 antes de `approved`; 1 en el cierre |
| Sin merge hacia `main` | ✔ Solo integración en `dev`; `main` lo modifica el usuario al fusionar el pull request |
| Pull request `Task → main` | ✔ Base `main`, *head* la rama Task. **Nunca `dev → main`**, y **Claude no lo fusiona** |
| `Task/007` no iniciada | ✔ |
| Aprobación solo del usuario | ✔ Expresión exacta recibida el 2026-08-21 |

## 5.1 Cierre aprobado (2026-08-21)

Ejecutado según [PROJECT_INSTRUCTIONS](../claude/PROJECT_INSTRUCTIONS.md) §8, en el único
repositorio afectado:

1. Aprobación registrada en la ficha, este reporte, `STATUS.md` y el índice.
2. **Ningún ADR cambia de estado**: la tarea no produjo decisiones estructurales.
3. Contadores **sin cambios**: **6 de 41 (15 %)** y ETAPA 02 **2 de 3**. Este mantenimiento
   **no cuenta** dentro de las 41 tareas.
4. Validaciones finales repetidas antes de comprometer los cambios.
5. **Un commit.**
6-9. `dev` actualizado con `pull --ff-only` e integrada la rama Task con merge `--no-ff`;
   `dev` publicado.
10. Rama Task publicada en `origin`.
11-12. Pull request **`Task/006.1-Corregir-Drift-Documental-Post-Merge → main`**.
13. **No fusionado por Claude.**
14-16. Vuelta a `main`, `fetch --prune`, `pull --ff-only` y borrado de la rama Task local con
   `git branch -d` (nunca `-D`). La rama Task remota **no se elimina**: es decisión del
   usuario.

Los SHA, la URL del pull request y el estado vivo de las ramas se entregaron al usuario en el
reporte de cierre y se consultan en Git y GitHub, no aquí
([WORKFLOW §6.1](../project-management/WORKFLOW.md)).

## 6. Instrucciones de validación para el usuario

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra
git switch main
git log --oneline -3
git show --stat HEAD
```

Revisar que ninguna de las seis frases corregidas afirme el estado vivo de un pull request o
de una rama, y que las secciones históricas no hayan cambiado.

## 7. Próxima tarea

`Task/007-Integracion-Local` — **Pendiente, no iniciada**. No se inicia dentro de esta
tarea. Como toda rama Task, nacerá desde `main` actualizado y limpio.
