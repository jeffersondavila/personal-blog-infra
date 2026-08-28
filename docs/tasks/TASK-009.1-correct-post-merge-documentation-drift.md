# TASK-009.1 — Corregir el drift documental posterior a la fusión de `Task/009`

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/009.1-Corregir-Drift-Documental-Post-Merge` |
| **Nombre** | Corregir el drift documental posterior a la fusión de `Task/009` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. No altera el avance global (**9 de 41**) ni la ETAPA 03 (**2 de 5**) |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Dependencias** | `Task/009-API-Publica` — **Aprobada** ✔ (2026-08-27) |
| **Rama** | `Task/009.1-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | `e034e7591d113b658c3a29d853f55a07912cd7b8` |
| **Fecha de inicio** | 2026-08-27 |
| **Fecha de aprobación** | 2026-08-27 |
| **Última actualización** | 2026-08-27 — cierre aprobado |
| **Próxima tarea** | `Task/010-Almacenamiento-Compatible-S3` — **Pendiente, no iniciada** |

---

## 0. Preparación Git

Verificado **antes** de crear la rama, en los tres repositorios: rama `main`,
`main == origin/main`, working tree limpio, staging vacío, 0 ramas Task locales y 0 remotas.
En `personal-blog-infra` y `personal-blog-backend`, además: `main` ancestro de `dev`,
`git rev-list --count dev..main` = `0` y `git diff main dev` vacío.

Tras crearla en infra: `git rev-parse HEAD` == `git rev-parse main` (`e034e75`) y
`git rev-list --count main..HEAD` == `0`.

**La rama nació de `main`.** `dev` no interviene como base
([WORKFLOW §2.1](../project-management/WORKFLOW.md)).

`personal-blog-backend` y `personal-blog-frontend`: **solo lectura**, sin rama.

## 1. Objetivo

Eliminar las **6 afirmaciones** que la documentación de gobierno todavía presenta como
estado vigente y que la fusión de `Task/009` y su normalización ya volvieron falsas, más
**1 estado durable obsoleto** detectado en el mismo barrido.

## 2. Contexto — origen del drift

El cierre de `Task/009` se redactó **antes** de que el usuario fusionara los pull request.
En ese instante los PR estaban abiertos y la normalización `main → dev` no se había
ejecutado, y así se escribió. Ese texto viajó **dentro del propio PR** hacia `main`; al
fusionarlo, el documento ya versionado siguió afirmando que el PR estaba pendiente.

Es exactamente el defecto estructural que describe
[WORKFLOW §6.1](../project-management/WORKFLOW.md), vigente desde `Task/005.6`, y el mismo
patrón que ya corrigió `Task/006.1` tras `Task/006`. La regla existe; lo que falló fue su
aplicación al redactar el cierre.

**No hay regla nueva que escribir.** §6.1 ya cubre el caso, incluido su punto 4:

> Ningún documento condiciona el inicio de la siguiente tarea a un hecho transitorio ya
> ocurrido. La condición se expresa como regla permanente y no como estado.

## 3. Dentro del alcance

- [x] Corregir las **6 afirmaciones** de categoría C.
- [x] Reescribirlas en forma **duradera**: estado de la tarea, dependencia del ROADMAP y
      regla permanente de ramas, en lugar de un trámite en presente y sin fecha.
- [x] Corregir el **estado durable obsoleto** de `Task/009` en la *Tabla completa de tareas*
      de `STATUS.md`, que seguía en `Lista para validación`.
- [x] Registrar este mantenimiento en `STATUS.md`, como exige
      [WORKFLOW §6](../project-management/WORKFLOW.md) —«al iniciar, al quedar lista y al
      aprobarse»— y **fuera** de las 41 filas oficiales.
- [x] Barrido §6.1 sobre los **8** documentos que `Task/009` modificó, con clasificación
      A / B / C explícita.
- [x] Añadir la comprobación que faltaba al checklist de cierre existente §1 de la
      [Definition of Done](../project-management/DEFINITION_OF_DONE.md), sin duplicar la
      regla de WORKFLOW §6.1 (ver §12).
- [x] Ficha y reporte de este mantenimiento.

## 4. Fuera del alcance

| Excluido | Razón |
| --- | --- |
| `ROADMAP.md` | El barrido encontró **0 apariciones de categoría C**. `Task/010` ya figura con dependencia `008` y estado `Pendiente`: redacción durable correcta |
| `STAGE-03-domain-and-backend.md` | **0 apariciones de categoría C.** `Task/010` aparece *Pendiente* sin condicionar su inicio a Git ni a GitHub |
| `api-contracts.md`, `data-model.md` | Sus apariciones de «abierto» y «normalización» son decisiones pendientes de otras tareas y generación de *slug*: nada que ver con estado de Git |
| Secciones históricas de `Task/001`–`Task/008` en `STATUS.md` | Registro histórico fechado. **El historial no se reescribe** |
| Historia de la desviación TDD de `Task/009` (§I.2), su remediación (§I.5) y el criterio 29 | Registro histórico válido. **No se toca ni una palabra** |
| Contadores de avance | Este mantenimiento **no cuenta**: siguen **9 de 41** y ETAPA 03 **2 de 5** |
| Decisiones **D-009-A** a **D-009-R** | Ninguna cambia. Siguen **Vigentes** |
| Contrato HTTP, OpenAPI, modelo físico, migraciones | Sin cambios. Tarea **exclusivamente documental** |
| `personal-blog-backend`, `personal-blog-frontend` | Sin cambios. No se crea rama en ellos |

### Divergencia deliberada respecto de `Task/006.1`

`Task/006.1` excluyó de su alcance el reporte de `Task/006`, con el argumento de que un
reporte es una **instantánea cerrada**. Aquí sí se corrigen dos frases del reporte de
`Task/009`, y la diferencia es de naturaleza, no de criterio:

- Lo que `Task/006.1` protegía era la **observación de lo que se sabía al cerrar**. Eso aquí
  también queda intacto: §Y del reporte conserva su bloque *«Observado el 2026-08-27, antes
  de la aprobación…»* sin tocar.
- Las dos frases corregidas **no son observaciones del pasado**: son **condiciones vivas
  orientadas al futuro** —«el laboratorio se conserva **hasta que**…», «`Task/010` **no se
  inicia hasta que**…»—. §6.1 punto 4 prohíbe esa forma en **cualquier** documento, no solo
  en `STATUS.md`.

Una instantánea cerrada describe; no condiciona el futuro. Solo se corrige lo segundo.

## 5. Entregables

| Entregable | Ruta |
| --- | --- |
| Vista rápida corregida (3), estado durable de `Task/009` en la tabla completa (1) y registro de este mantenimiento en validación | `docs/project-management/STATUS.md` |
| Condición del laboratorio (§I.5) y *Próxima tarea* (§Z) corregidas | `docs/task-reports/TASK-009-report.md` |
| *Próxima tarea* (§13) corregida | `docs/tasks/TASK-009-public-api.md` |
| Criterio 12 de cierre añadido al checklist existente | `docs/project-management/DEFINITION_OF_DONE.md` |
| Ficha de este mantenimiento | `docs/tasks/TASK-009.1-correct-post-merge-documentation-drift.md` |
| Reporte | `docs/task-reports/TASK-009.1-report.md` |
| Índice de reportes | `docs/task-reports/README.md` |

## 6. Criterios de aceptación

1. Las **6** afirmaciones de categoría C quedan corregidas.
2. Un nuevo barrido sobre los **8** documentos que `Task/009` modificó da **C = 0**.
3. `STATUS.md` no afirma el estado vivo de ningún PR, rama remota ni normalización.
4. Ni `STATUS.md`, ni el reporte, ni la ficha condicionan `Task/010` a un hecho de Git.
5. El reporte no condiciona la conservación del laboratorio al estado de Git de `Task/009`.
6. La ficha de `Task/009` elimina «normalizada» como condición.
7. Ninguna observación histórica fechada se reescribe.
8. `ROADMAP.md` y `STAGE-03` no se modifican.
9. Los contadores siguen en **9 de 41 (22 %)** y ETAPA 03 **2 de 5 (40 %)**.
10. **41 identificadores** intactos; `Task/009.1` queda registrado en `STATUS.md` como
    mantenimiento, **fuera** de esas 41 filas.
11. `Task/010` sigue **Pendiente y no iniciada**.
12. Decisiones **D-009**, contrato HTTP y modelo físico: **0 cambios**.
13. La Definition of Done gana el criterio 12 sin duplicar WORKFLOW §6.1.
14. 0 cambios funcionales en los tres repositorios.

## 7. TDD / Plan test-first

**No aplica.** Tarea exclusivamente documental: no introduce comportamiento ejecutable en
`personal-blog-backend` ni en ningún otro repositorio
([BACKEND_TESTING_STRATEGY](../project-management/BACKEND_TESTING_STRATEGY.md) §4). La
validación equivalente es el barrido dirigido del criterio 2.

## 8. Comandos de validación

```powershell
# C = 0 sobre los ocho documentos que Task/009 modifico
Select-String -Path docs/project-management/STATUS.md, `
  docs/project-management/ROADMAP.md, `
  docs/stages/STAGE-03-domain-and-backend.md, `
  docs/task-reports/TASK-009-report.md, `
  docs/task-reports/README.md, `
  docs/tasks/TASK-009-public-api.md, `
  docs/architecture/api-contracts.md, `
  docs/architecture/data-model.md `
  -Pattern 'no se inicia hasta|hasta que el usuario fusione|abierto y pendiente|pendiente de fusionar|y normalizada'

# Contadores y roadmap intactos
Select-String -Path docs/project-management/ROADMAP.md -Pattern '9 de 41|9 / 41|41'

git diff --check
```

## 9. Decisiones técnicas

| Decisión | Alternativas | Justificación | ¿ADR? |
| --- | --- | --- | --- |
| Formular el cierre como **hecho duradero** en las superficies vivas | Escribir allí una observación fechada del merge | Ambas son válidas ([WORKFLOW §6.1](../project-management/WORKFLOW.md) punto 2). Se elige la duradera para no convertir `STATUS.md` en fuente del estado de Git; la trazabilidad fechada ya vive en §Y del reporte de `Task/009` y en *Estado de los repositorios*. Es además lo que decidió `Task/006.1` | No |
| Corregir **dos frases** del reporte de `Task/009`, apartándose de `Task/006.1` | No tocar el reporte | Son condiciones vivas hacia el futuro, no observaciones del pasado; §6.1 punto 4 las prohíbe en cualquier documento. La instantánea de lo observado (§Y) queda intacta. Razonamiento completo en §4 | No |
| Corregir el estado de `Task/009` en la *Tabla completa de tareas* | Dejarlo para otra tarea | Es **estado durable obsoleto**, no drift transitorio: contradice la vista rápida del mismo documento. Corregirlo aquí evita un tercer mantenimiento por una sola celda | No |
| **Registrar `Task/009.1` en `STATUS.md` como `Lista para validación`** | No registrarlo hasta la aprobación | [WORKFLOW §6](../project-management/WORKFLOW.md) obliga a actualizar `STATUS.md` «al iniciar, al quedar lista y al aprobarse», y §6.1 clasifica el **estado de la tarea** como **duradero**. Que después pase a `Aprobada` es una transición versionada y deliberada, no drift | No |
| Registrarlo **fuera** de las 41 filas oficiales | Añadirlo a la tabla de tareas | Es mantenimiento de gobierno y no altera el conteo, igual que `002.1`, `005.1`–`005.7`, `006.1` y `006.2` | No |
| **Añadir el criterio 12 a la Definition of Done**, y no tocar `TASK_TEMPLATE.md` | No tocar ningún checklist · tocar los dos · crear un *linter* o un *hook* | El checklist de cierre existía y tenía un hueco real: ningún criterio verificaba §6.1. La fila nueva **comprueba el hecho y apunta a la regla**, igual que el criterio 11 hace con §2.1, así que no duplica. Tocar además `TASK_TEMPLATE.md` sí sería una tercera copia. Razonamiento completo en §12 | No |

## 10. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | El drift se repita en el cierre de `Task/010` | Medio | La causa y su patrón correcto ya están en WORKFLOW §6.1, y ahora el cierre tiene una comprobación propia: **criterio 12** de la Definition of Done (ver §12). Es la **segunda** reincidencia: si vuelve a ocurrir, la mitigación siguiente ya no es documental |
| 2 | Confundir historia válida con drift y borrar trazabilidad | Medio | Clasificación A/B/C explícita antes de tocar nada; solo se editan las apariciones **C** |
| 3 | Corregir el reporte de `Task/009` erosione la instantánea de su cierre | Bajo | Solo se tocan dos frases condicionales; §I.2, §I.5, §I.6, §P, §X y §Y quedan literalmente intactas |

## 11. Documentación creada o actualizada

- `docs/project-management/STATUS.md` — 3 correcciones de categoría C, 1 estado durable
  obsoleto y el registro de este mantenimiento como `Lista para validación`.
- `docs/task-reports/TASK-009-report.md` — 2 correcciones (§I.5 y §Z).
- `docs/tasks/TASK-009-public-api.md` — 1 corrección (§13).
- `docs/project-management/DEFINITION_OF_DONE.md` — criterio 12 y su nota al pie.
- `docs/tasks/TASK-009.1-correct-post-merge-documentation-drift.md` — nueva.
- `docs/task-reports/TASK-009.1-report.md` — nuevo.
- `docs/task-reports/README.md` — índice.

## 12. Prevención de recurrencia

La regla existe —[WORKFLOW §6.1](../project-management/WORKFLOW.md), con su tabla
duradero/transitorio y sus cuatro puntos de aplicación— y **no falló**. Lo que falló fue su
aplicación al redactar el cierre, por segunda vez (`006.1` fue la primera).

**Comprobación:** la [Definition of Done](../project-management/DEFINITION_OF_DONE.md) §1
no tenía ningún criterio que la verificara. El criterio 5 exige que «la documentación esté
actualizada», pero nada obligaba a comprobar que además no persistiera estado transitorio.
Existía por tanto un **checklist de cierre natural con un hueco real**.

**Cambio mínimo aplicado:** una fila nueva en esa tabla, redactada exactamente con el patrón
del criterio 11 —comprobar el hecho y **apuntar** a la regla, sin reescribirla—:

> **12.** La documentación no persiste estado transitorio de Git o GitHub. *Búsqueda dirigida
> en los documentos tocados: toda mención a un PR, una rama remota o una normalización es
> historia fechada o regla permanente, nunca estado vigente ni condición de la tarea
> siguiente.*

Más su nota al pie, que remite a WORKFLOW §6.1 igual que la del criterio 11 remite a §2.1.

**Lo que deliberadamente NO se hace.** No se toca `TASK_TEMPLATE.md`: sería una tercera copia
de la misma regla y [WORKFLOW §7](../project-management/WORKFLOW.md) —principio de no
duplicación— lo prohíbe. No se crea *linter*, *hook*, script ni paso de CI: sería *scope
creep* de una tarea documental.

Si el defecto reaparece tras `Task/010` pese al criterio 12, la conclusión ya no será que
falta documentación, sino que hace falta una comprobación **ejecutable** — y eso merecerá su
propia tarea, con su alcance y su decisión, no un añadido improvisado aquí.

## 13. Deuda pendiente

Ninguna nueva. Queda registrado en §10 el patrón de reincidencia, para que la decisión sobre
una comprobación ejecutable se tome con evidencia y no por impulso.

## 14. Próxima tarea

`Task/010-Almacenamiento-Compatible-S3` — **Pendiente, no iniciada**; su dependencia es la
que fija el [ROADMAP](../project-management/ROADMAP.md). Como toda rama Task, **nacerá desde
`main`** actualizado y limpio.

## 15. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | 2026-08-27 |
| **Aprobado por** | jeffersondavila |
| **Expresión de aprobación** | `approved: Task/009.1-Corregir-Drift-Documental-Post-Merge` |
