# TASK-019.1 — Corregir el drift documental posterior a la fusión de `Task/019`

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/019.1-Corregir-Drift-Documental-Post-Merge` |
| **Nombre** | Corregir el drift documental posterior a la fusión de `Task/019` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. No altera el avance global (**19 de 41**, 46 %) ni la ETAPA 06 (**1 de 3**, 33 %) |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Dependencias** | `Task/019-CI-Frontend` — **Aprobada** ✔ el 2026-09-08; PR `#12` y `#34` fusionados y normalización `main → dev` completada |
| **Rama** | `Task/019.1-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | **`32474e5abc5f52aedf84f4231b16f3c868905b79`** (`= main = origin/main` al crearla) |
| **Fecha de inicio** | 2026-09-09 |
| **Fecha de aprobación** | **2026-09-09** |
| **Expresión de aprobación** | `approved: Task/019.1-Corregir-Drift-Documental-Post-Merge` |
| **Pull request** | `Task/019.1 → main`, creado durante el cierre aprobado. **Su número y su estado se consultan en vivo** (`gh pr list --head Task/019.1-Corregir-Drift-Documental-Post-Merge`), no en este documento: [WORKFLOW §6.1](../project-management/WORKFLOW.md) |
| **Reporte** | [TASK-019.1-report.md](../task-reports/TASK-019.1-report.md) |

---

## 0. Preparación Git

| # | Comprobación | Resultado real |
| --- | --- | --- |
| 1 | `main == origin/main` | **Sí** — ambos `32474e5` |
| 2 | Working tree limpio antes de crear la rama | **Sí** — `git status --short` vacío |
| 3 | Rama activa antes de crear = `main` | **Sí** |
| 4 | Rama `Task/019.1` inexistente, local y remota | **Sí** — verificado antes de crearla |
| 5 | Rama creada **desde `main`** | **Sí** |
| 6 | `git rev-parse HEAD` == `git rev-parse main` tras crearla | **Sí** — ambos `32474e5` |
| 7 | Commits propios frente a `main` al crearla | **0** |

---

## 1. Objetivo

Aplicar el **criterio 12** de la Definition of Done al contenido durable que dejó
`Task/019`, y dejarlo en **C = 0** y **D = 0**.

La regla de gobierno aplicable es [WORKFLOW §6.1](../project-management/WORKFLOW.md),
vigente desde `Task/005.6`:

> Los documentos versionados registran **estado duradero**. El estado transitorio de Git y
> GitHub —PR abierto o fusionado, rama remota, sincronización actual— se **consulta en
> vivo** y solo se archiva como **observación fechada**.

## 2. Contexto — por qué existe esta tarea

`Task/019` tenía una particularidad frente a las tareas anteriores: **parte de su evidencia
solo podía obtenerse durante su propio cierre aprobado**. El trigger `pull_request` del
workflow no puede ejecutarse sin un pull request, y crear un PR antes de la aprobación está
prohibido. El verde sobre `dev` tampoco existe hasta integrar.

Sus documentos se redactaron y commitearon **antes** de ese momento, y por eso dejaron
escrito, en presente, que la tarea no aportaba evidencia de una ejecución `pull_request`.
Minutos después el propio flujo aprobado la produjo: la ejecución **34308296565** terminó
en `success`. Desde entonces esas afirmaciones son **falsas**, no imprecisas.

A ese cluster se suma una contradicción distinta: la tabla del criterio 12 del reporte de
`Task/019` seguía describiendo sus decisiones técnicas como *Propuesta — pendiente de
aprobación*, cuando la aprobación del 2026-09-08 ya las había promovido a **vigentes** en
la ficha y en STAGE-06.

Es el mismo patrón que motivó `Task/004.2`, `Task/006.1`, `Task/009.1` y `Task/013.1`.
**No es un defecto del workflow**: es la consecuencia normal de documentar antes de que el
cierre genere su última evidencia, y el criterio 12 existe precisamente para detectarlo.

## 3. Clasificación aplicada

| Clase | Significado | Tratamiento |
| --- | --- | --- |
| **A** | Regla o afirmación permanente | Se conserva |
| **B** | Hecho histórico fechado | Se conserva |
| **C** | Estado operativo de Git/GitHub vivo escrito como presente | **Se convierte en B** |
| **D** | Contradicción documental que no es de Git | **Se corrige** |

No se borra evidencia histórica útil. Se corrige el **tiempo verbal y el anclaje
temporal**, no los hechos. Una afirmación fechada que era cierta en su fecha **se conserva
intacta**: que después ocurriera algo nuevo no la convierte en error.

## 4. Alcance

Únicamente el contenido durable que introdujo o modificó `Task/019`:

- `docs/tasks/TASK-019-ci-frontend.md`
- `docs/task-reports/TASK-019-report.md`
- `docs/stages/STAGE-06-continuous-integration.md`
- `docs/project-management/STATUS.md`
- `docs/task-reports/README.md`

### Fuera de alcance

- **No** se tocan `personal-blog-frontend` ni `personal-blog-backend`.
- **No** se toca `.github/workflows/ci-frontend.yml`, `vite.config.ts`,
  `vite.config.test.ts`, `tsconfig.node.json` ni `CONTRIBUTING.md`.
- **No** se reabre `Task/019` ni se revisa su implementación.
- **No** se repiten `npm ci`, la suite, el build ni `npm audit`: esta tarea es
  **exclusivamente documental**.
- **No** se inicia `Task/020`.
- **No** se repite la normalización de Git, ya completada y verificada.
- **No** se revisan riesgos preexistentes que `Task/019` no introdujo.

## 5. Qué puede y qué no puede persistirse

| Sí puede persistirse | No debe persistirse |
| --- | --- |
| Números de PR (`#12`, `#34`) y su dirección `Task → main` | «El PR está abierto» o «esperando merge» |
| Fechas reales de fusión y `mergedAt` | «La rama remota existe / se conserva» como estado vivo |
| Merge commits `7dce98a` y `32474e5` | Working tree o staging actuales |
| Merges de normalización `b261e65` y `efeb6b8` | SHA de `main` y `dev` como estado vigente |
| Identificadores y conclusión de los runs 34305529115, 34308234554 y 34308296565 | «El workflow está verde ahora» |
| Que la fusión la hizo **manualmente el usuario** | «Task019 no aporta evidencia de `pull_request`» |
| Que en el bootstrap solo estaba acreditado `push`, **fechado** | «Las decisiones quedan como Propuesta» tras la aprobación |

## 6. Criterio de éxito

| # | Criterio |
| --- | --- |
| 1 | Barrido del criterio 12 ejecutado sobre los cinco documentos |
| 2 | Toda afirmación de clase **C** convertida en hecho histórico fechado |
| 3 | Toda contradicción de clase **D** corregida |
| 4 | **C = 0** y **D = 0** |
| 5 | Ninguna evidencia histórica útil eliminada ni reescrita |
| 6 | Los dos momentos —bootstrap y cierre— quedan distinguidos, no fundidos |
| 7 | Avance del roadmap sin cambios: **19 / 41 = 46 %**, ETAPA 06 **1 / 3 = 33 %** |
| 8 | Enlaces documentales verificados |
| 9 | Sin commit, push ni PR mientras la tarea esté pendiente de aprobación |

## 7. Límites

- No se ejecuta ninguna operación destructiva.
- No se marca ningún ADR ni decisión nueva como aceptada.
- Los criterios de salida de STAGE-06 **siguen abiertos**: exigen los tres repositorios.
- El control negativo remoto **sigue sin autorizarse**.
- **R-016-1** sigue abierto: las ejecuciones remotas verdes no lo cierran.
