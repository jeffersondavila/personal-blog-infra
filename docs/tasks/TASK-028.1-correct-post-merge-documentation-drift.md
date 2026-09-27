# TASK-028.1 — Corregir el drift documental posterior a la fusión de `Task/028`

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/028.1-Corregir-Drift-Documental-Post-Merge` |
| **Nombre** | Corregir el drift documental posterior a la fusión de `Task/028` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. **No altera el avance global** (**28 de 41**, ≈ 68 %) ni la **ETAPA 09** (**2 de 3**, ≈ 67 %, En progreso) |
| **Estado** | **Aprobada** ✔ el 2026-09-26 por el usuario |
| **Fecha de aprobación** | **2026-09-26** (Guatemala) |
| **Expresión de aprobación** | `approved: Task/028.1-Corregir-Drift-Documental-Post-Merge` |
| **Zona horaria de las fechas** | **Guatemala (UTC−6)**. Los `timestamp` completos de GitHub se conservan en **UTC** y se identifican como tales |
| **Fecha de inicio** | 2026-09-26 (Guatemala) |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Dependencias** | `Task/028-GitHub-OIDC-AWS` — **Aprobada** ✔ el 2026-09-26; PR `#50` fusionado por el usuario y normalización `main → dev` completada |
| **Rama** | `Task/028.1-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | **`e0fa95b9ee367fc0026a15f3e0afad3c5a012c26`** (`= main = origin/main` al crearla) |
| **Reporte** | [TASK-028.1-report.md](../task-reports/TASK-028.1-report.md) |

---

## 0. Preparación Git

| # | Comprobación | Resultado real |
| --- | --- | --- |
| 1 | `git fetch --prune origin` | Ejecutado |
| 2 | `git switch main` | `main` activa |
| 3 | `git pull --ff-only origin main` | `Already up to date` |
| 4 | `git status --porcelain` | **vacío** |
| 5 | `git rev-parse main` | `e0fa95b9ee367fc0026a15f3e0afad3c5a012c26` |
| 6 | `git rev-parse origin/main` | `e0fa95b9ee367fc0026a15f3e0afad3c5a012c26` — **coinciden** |
| 7 | `git switch -c Task/028.1-Corregir-Drift-Documental-Post-Merge` | Rama creada |
| 8 | `git rev-parse HEAD` vs `git rev-parse main` | **coinciden** |
| 9 | La base **no** es `dev` ni derivada de `dev` | **Confirmado**: `HEAD ≠ dev` |
| 10 | Otros repositorios | `personal-blog-backend` y `personal-blog-frontend` en `main`, limpios y **sin rama** |

Invariante respetado: **toda rama Task nace de `main` actualizado y limpio**.

---

## 1. Objetivo

Cerrar el **único** drift documental que dejó la fusión de `Task/028`: dos casillas
declaraban pendiente la **reconfirmación postmerge** cuando su evidencia ya existía, porque
esa validación **solo puede ejecutarse después del merge humano** y, por tanto, después de
que la documentación de `Task/028` estuviera ya fusionada.

No corrige ningún error de contenido de `Task/028`: corrige un **desfase temporal
inevitable** por el orden en que el flujo obliga a hacer las cosas.

---

## 2. Contexto — por qué existe esta tarea

El criterio 8 de `Task/028` dice literalmente que la reconfirmación postmerge **no es
prerrequisito de la aprobación**, pero **sí es una validación postmerge obligatoria antes de
dar por integrada la tarea**. El workflow `Verify AWS OIDC` está configurado para que en
`main` solo se ejecute por `workflow_dispatch`, precisamente para que sea un acto explícito.

Consecuencia: en el momento de aprobar y fusionar, la casilla **tenía que estar abierta**. Una
vez ejecutada la validación, quedó abierta por desfase y no por falta de evidencia. Marcarla
exigía un commit versionado, y la rama de `Task/028` ya no existía.

No se hizo commit directo a `main` y **no se reescribe historia**: se corrige aquí.

---

## 3. Principio de corrección aplicado

1. **Solo se marcan casillas cuya evidencia ya existe y está identificada** por número de
   ejecución y SHA. Nada se marca por inferencia.
2. **No se reescribe la historia** de `Task/028`: su ficha y su reporte conservan lo que
   decían, y las marcas nuevas **dicen quién las registró y cuándo**.
3. **No se altera ningún contador**: esta tarea no cuenta entre las 41 y no mueve el avance.
4. **Alcance mínimo**: dos archivos de gobierno, más la ficha y el reporte de esta tarea.

---

## 4. Alcance

### Dentro

- [x] `docs/tasks/TASK-028-github-oidc-aws.md`: marcar la reconfirmación postmerge y anotar
      el cumplimiento del criterio 8.
- [x] `docs/stages/STAGE-09-cloud-accounts.md`: marcar la mitad que faltaba del **cuarto
      criterio asociado a `Task/028`** —el de **trust final y reconfirmación postmerge**—, que
      en la lista global de criterios de salida de la etapa es el **séptimo**.
- [x] Registrar la evidencia: `CI Infra` en `main`, `Verify AWS OIDC` en `main`, `CI Infra`
      en `dev` normalizado, y los SHA finales de `main` y `dev`.
- [x] `docs/project-management/STATUS.md`: registrar `Task/028.1` en **Lista para validación**,
      como exige [WORKFLOW §6](../project-management/WORKFLOW.md) —«al iniciar, al quedar lista
      y al aprobarse»— y §6.1, que clasifica el **estado de la tarea** como estado **duradero**.
- [x] Ficha y reporte de esta tarea.

### Fuera — explícitamente no se toca

AWS, Terraform, la implementación OIDC, GHCR, MinIO, workflows, código, pruebas, secretos y
`Task/029`.

**`ROADMAP.md`** no recibe cambio de estado ni de avance: [WORKFLOW §6](../project-management/WORKFLOW.md)
solo lo exige «al cambiar el estado o el avance de una etapa», y aquí no cambia ninguno —
`Task/028.1` no cuenta entre las 41 y la ETAPA 09 sigue en **2/3 ≈ 67 %**. Sí se corrige en él
**una fecha local**, junto con las de los demás documentos, por el motivo del apartado
siguiente.

**Corrección de una afirmación previa de esta misma ficha.** Antes decía que `STATUS.md`
quedaba fuera del alcance y requería autorización aparte. **Era incorrecto:** WORKFLOW §6
obliga a actualizarlo al quedar la tarea lista, y §6.1 clasifica el estado de la tarea como
**duradero**, no transitorio. Se corrige aquí.

---

## 5. Criterios de aceptación

| # | Criterio |
| --- | --- |
| 1 | La casilla de reconfirmación postmerge de `Task/028` queda marcada, con ejecución y SHA identificados |
| 2 | El criterio 8 de `Task/028` queda anotado como **CUMPLIDO**, sin borrar su redacción original |
| 3 | El **cuarto criterio asociado a `Task/028`** —trust final y reconfirmación postmerge—, **séptimo** de la lista global, queda marcado; los otros tres de la tarea ya lo estaban |
| 4 | Las **12** casillas abiertas que quedan en la etapa son **todas de `Task/029`** |
| 5 | Ninguna casilla se marca sin evidencia citada |
| 6 | El avance global sigue en **28/41 ≈ 68 %** y la ETAPA 09 en **2/3 ≈ 67 %** |
| 7 | Ningún archivo fuera del alcance cambia; el `git diff` lo demuestra |
| 8 | `STATUS.md` registra `Task/028.1` en **Lista para validación** |
| 9 | Las fechas locales usan **Guatemala (UTC−6)**; los `timestamp` de GitHub se conservan en UTC e identificados |
| 10 | Ningún criterio se describe como «cuarto de la ETAPA 09»: es el cuarto **de `Task/028`** y el séptimo global |
| 11 | Gates aplicables en verde y árbol de trabajo limpio, **sin commit, sin push, sin PR y sin tocar `dev`** |

---

## 6. Estado

**APROBADA** el **2026-09-26** mediante la expresión exacta:

```
approved: Task/028.1-Corregir-Drift-Documental-Post-Merge
```

Esta tarea **no toma ninguna decisión arquitectónica**: no crea, reemplaza ni promueve ningún
ADR, y no hay decisiones propias que pasar de propuesta a aceptada. Es mantenimiento de
gobierno documental.

**No altera ningún contador.** El avance global sigue en **28/41 ≈ 68 %** y la **ETAPA 09** en
**2/3 ≈ 67 %**: `Task/028.1` no cuenta entre las 41.

`ROADMAP.md` no recibe cambio de estado ni de avance, conforme a
[WORKFLOW §6](../project-management/WORKFLOW.md), que solo lo exige al cambiar el estado o el
avance de una **etapa**.

El merge del pull request hacia `main` es **responsabilidad exclusiva del usuario**.
