# TASK-006.1 — Corregir el drift documental posterior a la fusión de `Task/006`

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/006.1-Corregir-Drift-Documental-Post-Merge` |
| **Nombre** | Corregir el drift documental posterior a la fusión de `Task/006` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. No altera el avance global (**6 de 41**) ni la ETAPA 02 (**2 de 3**) |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Dependencias** | `Task/006-Fundacion-Frontend-React` — **Aprobada** ✔ (2026-08-18), fusionada y normalizada |
| **Rama** | `Task/006.1-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | `f434666e0cf829e4ee906621e9cc6f2675455032` |
| **Fecha de inicio** | 2026-08-19 |
| **Fecha de aprobación** | 2026-08-21 |
| **Última actualización** | 2026-08-21 — cierre aprobado |
| **Próxima tarea** | `Task/007-Integracion-Local` — **Pendiente, no iniciada** |

---

## 0. Preparación Git

Verificado antes de crear la rama: `main == origin/main` (`f434666`), working tree limpio,
staging vacío, `main` ancestro de `dev`, `git diff main dev` vacío, 0 ramas Task locales y
0 remotas. Tras crearla: `git rev-parse HEAD` == `git rev-parse main` y
`git rev-list --count main..HEAD` == 0.

## 1. Objetivo

Eliminar las **6 afirmaciones** que la documentación de gobierno todavía presenta como
estado vigente y que la fusión de `Task/006` ya volvió falsas.

## 2. Contexto — origen del drift

El cierre de `Task/006` se redactó **antes** de que el usuario fusionara los pull request.
En ese instante los PR estaban abiertos, y así se escribió. Ese texto viajó **dentro del
propio PR** hacia `main`; al fusionarlo, el documento ya versionado siguió afirmando que el
PR estaba pendiente.

[`WORKFLOW.md`](../project-management/WORKFLOW.md) §6.1 —vigente desde `Task/005.6`— ya
describe este mecanismo con precisión y lo llama *«una afirmación condenada a ser falsa
desde que se escribe»*. **El defecto no es un descubrimiento nuevo: es un incumplimiento de
una regla que ya existía.** Su punto 1 es explícito: `STATUS.md` no escribe «el PR sigue
abierto» ni «pendiente de fusionar» como situación vigente. Su punto 4 añade que ningún
documento condiciona el inicio de la siguiente tarea a un hecho transitorio ya ocurrido.

Detectado durante el cierre post-merge de `Task/006`, en una auditoría focalizada que
clasificó cada aparición como **A** (histórica válida), **B** (regla duradera) o **C**
(estado transitorio stale). Resultado: **6 apariciones de categoría C**.

## 3. Dentro del alcance

- [x] Corregir las 6 afirmaciones de categoría C.
- [x] Reescribirlas en forma **duradera** en las superficies vivas, en lugar de como una
      afirmación en presente y sin fecha sobre un trámite.
- [x] Registrar este mantenimiento en `STATUS.md` con estado **`Lista para validación`**,
      como exige [WORKFLOW §6](../project-management/WORKFLOW.md), y **fuera** de las 41
      filas oficiales.
- [x] Ficha y reporte de este mantenimiento.

## 4. Fuera del alcance

| Excluido | Razón |
| --- | --- |
| `ROADMAP.md` | La auditoría encontró **0 apariciones de categoría C**. No se toca por simetría |
| `TASK-006-report.md` | Es una **instantánea cerrada** por definición ([índice de reportes](../task-reports/README.md)). Categoría **A** |
| Secciones históricas de `Task/001`–`Task/005.7` en `STATUS.md` | Registro histórico fechado. **El historial no se reescribe** |
| Contadores de avance | Este mantenimiento **no cuenta**: siguen **6 de 41** y ETAPA 02 **2 de 3** |
| `personal-blog-frontend`, `personal-blog-backend` | Sin cambios. No se crea rama en ellos |
| Código, pruebas, Compose, Terraform, ADR, riesgos, decisiones | Tarea **exclusivamente documental** |

## 5. Entregables

| Entregable | Ruta |
| --- | --- |
| Vista rápida y sección de `Task/006` corregidas, más el registro de este mantenimiento en validación | `docs/project-management/STATUS.md` |
| Nota de `Task/006` corregida | `docs/stages/STAGE-02-application-foundations.md` |
| §19 corregida | `docs/tasks/TASK-006-react-frontend-foundation.md` |
| Ficha de este mantenimiento | `docs/tasks/TASK-006.1-correct-post-merge-documentation-drift.md` |
| Reporte | `docs/task-reports/TASK-006.1-report.md` |
| Índice de reportes | `docs/task-reports/README.md` |

## 6. Criterios de aceptación

1. Las 6 afirmaciones de categoría C quedan corregidas.
2. Una nueva auditoría sobre `STATUS.md`, `STAGE-02` y la ficha `TASK-006` da **C = 0**.
3. Ninguna observación histórica fechada se reescribe.
4. `ROADMAP.md` no se modifica.
5. Los contadores siguen en **6 de 41 (15 %)** y ETAPA 02 **2 de 3 (67 %)**.
6. **41 identificadores** intactos; `Task/006.1` queda registrado en `STATUS.md` como
   mantenimiento en validación, **fuera** de esas 41 filas.
7. `Task/007` sigue **Pendiente y no iniciada**.
8. 0 cambios funcionales en los tres repositorios.

## 7. TDD / Plan test-first

**No aplica.** Tarea exclusivamente documental: no introduce comportamiento ejecutable en
`personal-blog-backend` ni en ningún otro repositorio
([BACKEND_TESTING_STRATEGY](../project-management/BACKEND_TESTING_STRATEGY.md) §4). La
validación equivalente es la auditoría dirigida del criterio 2.

## 8. Comandos de validación

```powershell
# C = 0 sobre los tres documentos corregidos
Select-String -Path docs/project-management/STATUS.md, `
  docs/stages/STAGE-02-application-foundations.md, `
  docs/tasks/TASK-006-react-frontend-foundation.md `
  -Pattern 'quedan abiertos|sigan abiertos|Pendiente del usuario|hasta que el usuario fusione'

# Contadores intactos
Select-String -Path docs/project-management/ROADMAP.md -Pattern '6 de 41|41'

git diff --check
```

## 9. Decisiones técnicas

| Decisión | Alternativas | Justificación | ¿ADR? |
| --- | --- | --- | --- |
| En las **superficies vivas**, formular el cierre como hecho duradero | Escribir allí una observación fechada del merge | Ambas formas son válidas: una observación fechada **no envejece** ([WORKFLOW §6.1](../project-management/WORKFLOW.md) punto 2). Se elige la duradera porque describe el resultado de la tarea sin convertir `STATUS.md` en fuente del estado de Git; la trazabilidad fechada ya vive en el reporte de `Task/006` y en *Estado de los repositorios* | No |
| No tocar el reporte de `Task/006` | Corregirlo también | Un reporte es una instantánea cerrada; corregirlo destruiría la trazabilidad de lo que se sabía al cerrarlo | No |
| **Registrar `Task/006.1` en `STATUS.md` como `Lista para validación`** | No registrarlo hasta la aprobación | [WORKFLOW §6](../project-management/WORKFLOW.md) obliga a actualizar `STATUS.md` **«al iniciar, al quedar lista y al aprobarse»**, y §6.1 clasifica el **estado de la tarea** —`Lista para validación` incluido— como **duradero**, con `STATUS.md` entre sus destinos. Que después pase a `Aprobada` mediante un commit autorizado es una **transición versionada y deliberada**, no drift | No |
| Registrarlo **fuera** de las 41 filas oficiales | Añadirlo a la tabla de tareas | Es mantenimiento de gobierno y no altera el conteo del roadmap, igual que `002.1` y `005.1`–`005.7` | No |

## 10. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | El drift se repita en el cierre de `Task/007` | Medio | La causa está descrita en WORKFLOW §6.1 y ahora también aquí; el patrón correcto queda visible en los textos corregidos |
| 2 | Confundir historia válida con drift y borrar trazabilidad | Medio | Clasificación A/B/C explícita antes de tocar nada; solo se editan las 6 apariciones **C** |

## 11. Documentación creada o actualizada

- `docs/project-management/STATUS.md` — 4 correcciones de categoría C, más el registro de
  este mantenimiento como `Lista para validación`.
- `docs/stages/STAGE-02-application-foundations.md` — 1 corrección.
- `docs/tasks/TASK-006-react-frontend-foundation.md` — 1 corrección (§19).
- `docs/tasks/TASK-006.1-correct-post-merge-documentation-drift.md` — nueva.
- `docs/task-reports/TASK-006.1-report.md` — nuevo.
- `docs/task-reports/README.md` — índice.

## 12. Deuda pendiente

Ninguna. El drift estructural que hace posible este defecto ya tiene regla propia
(WORKFLOW §6.1); esta tarea solo aplica esa regla a los textos que la incumplían.

## 13. Próxima tarea

`Task/007-Integracion-Local` — **Pendiente, no iniciada**. Como toda rama Task, **nacerá
desde `main`** actualizado y limpio.

## 14. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | 2026-08-21 |
| **Aprobado por** | jeffersondavila |
| **Expresión de aprobación** | `approved: Task/006.1-Corregir-Drift-Documental-Post-Merge` |

> Esta sección solo se completa cuando el usuario autoriza explícitamente la aprobación.
> Claude nunca la completa por iniciativa propia.

El usuario autorizó la aprobación el 2026-08-21 con la expresión exacta. **El avance no
cambia**: este mantenimiento no forma parte de las 41 tareas, así que el proyecto sigue en
**6 de 41 (15 %)** y la ETAPA 02 en **2 de 3**. **Ningún ADR cambia de estado**: las cuatro
decisiones de §9 son de aplicación del gobierno vigente, no decisiones estructurales.
