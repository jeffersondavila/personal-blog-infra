# TASK-004.2 — Corregir el drift documental posterior a la fusión de `Task/004.1`

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/004.2-Corregir-Drift-Documental-Post-Merge` |
| **Nombre** | Corregir el drift documental posterior a la fusión de `Task/004.1` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. No altera el avance global (**17 de 41**, 41 %) ni la ETAPA 05 (**2 de 3**, 67 %) |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Dependencias** | `Task/004.1-Corregir-Backup-Rutas-Literales` — **Aprobada** ✔ el 2026-09-06; PR `#31` fusionado y normalización `main → dev` completada |
| **Rama** | `Task/004.2-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | **`a90cc55f4683d2d31df63ff4890f47f90f478d1f`** (`= main = origin/main` al crearla) |
| **Fecha de inicio** | 2026-09-06 |
| **Fecha de aprobación** | **2026-09-06** |
| **Expresión de aprobación** | `approved: Task/004.2-Corregir-Drift-Documental-Post-Merge` |
| **Reporte** | [TASK-004.2-report.md](../task-reports/TASK-004.2-report.md) |
| **Pull request** | `Task/004.2 → main`, creado durante el cierre aprobado. **Su número y su estado se consultan en vivo** (`gh pr list --head Task/004.2-Corregir-Drift-Documental-Post-Merge`), no en este documento: [WORKFLOW §6.1](../project-management/WORKFLOW.md) |

---

## 0. Preparación Git

| # | Comprobación | Resultado real |
| --- | --- | --- |
| 1 | `main == origin/main` | **Sí** — ambos `a90cc55` |
| 2 | Working tree limpio antes de crear la rama | **Sí** — `git status --short` vacío |
| 3 | Rama activa antes de crear = `main` | **Sí** |
| 4 | Rama creada **desde `main`** | **Sí** |
| 5 | `git rev-parse HEAD` == `git rev-parse main` tras crearla | **Sí** — ambos `a90cc55` |
| 6 | Commits propios frente a `main` al crearla | **0** |

---

## 1. Objetivo

Aplicar el **criterio 12** de la Definition of Done al contenido durable que introdujo
`Task/004.1`, y dejarlo en **C = 0**.

La regla de gobierno aplicable es [WORKFLOW §6.1](../project-management/WORKFLOW.md),
vigente desde `Task/005.6`:

> Los documentos versionados registran **estado duradero**. El estado transitorio de Git y
> GitHub —PR abierto o fusionado, rama remota, sincronización actual— se **consulta en
> vivo** y solo se archiva como **observación fechada**.

## 2. Contexto — por qué existe esta tarea

El cierre aprobado de `Task/004.1` se ejecutó cuando el pull request `#31` acababa de
crearse. Sus documentos quedaron afirmando, **en presente**, que el PR estaba «abierto, sin
fusionar».

El usuario fusionó el PR `#31` el 2026-09-07. Desde ese momento esas afirmaciones son
**falsas**: no envejecidas ni imprecisas, sino incorrectas. Es exactamente el patrón que el
criterio 12 existe para detectar, y el mismo que motivó `Task/006.1`, `Task/009.1` y
`Task/013.1`.

## 3. Clasificación aplicada

| Clase | Significado | Tratamiento |
| --- | --- | --- |
| **A** | Regla o afirmación permanente | Se conserva |
| **B** | Hecho histórico fechado | Se conserva |
| **C** | Estado operativo vivo | **Se convierte en B** |

No se borra evidencia histórica útil. Lo que se corrige es el **tiempo verbal y el anclaje
temporal**, no los hechos.

## 4. Alcance

Únicamente el contenido durable introducido por `Task/004.1`:

- `docs/tasks/TASK-004.1-fix-backup-literal-paths.md`
- `docs/task-reports/TASK-004.1-report.md`
- `docs/project-management/STATUS.md`
- `docs/task-reports/README.md`

### Fuera de alcance

- **No** se tocan `personal-blog-backend` ni `personal-blog-frontend`.
- **No** se tocan Docker, Compose ni Portainer.
- **No** se repiten respaldo, verificación ni prueba de restauración: esta tarea es
  **exclusivamente documental**.
- **No** se revisan los riesgos preexistentes del registro (`R-01` … `R-46`): no los
  introdujo `Task/004.1`.

## 5. Qué puede y qué no puede persistirse

| Sí puede persistirse | No debe persistirse |
| --- | --- |
| Número de PR (`#31`) | «El PR está abierto» |
| Dirección `Task → main` | «Esperando merge» |
| Fecha real de fusión y `mergedAt` | «La rama remota existe / no existe» como estado vivo |
| Merge commit `a90cc55` | Working tree actual |
| Que la fusión la hizo **manualmente el usuario** | SHA actuales de `main` y `dev` como estado vivo |
| Commit funcional `27f1696` | Commits pendientes actuales |
| Hechos históricos fechados | Cualquier afirmación en presente sobre Git o GitHub |

La ficha **puede** conservar que la rama fue publicada durante el cierre, siempre que esté
redactado de forma inequívoca como hecho histórico.

## 6. Criterio de éxito

| # | Criterio |
| --- | --- |
| 1 | Barrido del criterio 12 ejecutado sobre los cuatro documentos |
| 2 | Toda afirmación de clase **C** convertida en hecho histórico fechado |
| 3 | **C = 0** |
| 4 | Ninguna evidencia histórica útil eliminada |
| 5 | Enlaces documentales verificados |
| 6 | Avance del roadmap sin cambios: **17 / 41 = 41 %**, ETAPA 05 **2 / 3 = 67 %** |
| 7 | Sin commit, push ni PR **mientras la tarea estuviera pendiente de aprobación** |

## 7. Límites

- No se ejecuta ninguna operación destructiva.
- No se marca ningún ADR ni decisión como aceptada.
- No se inicia `Task/018`.
- No se trabaja sobre Portainer.
