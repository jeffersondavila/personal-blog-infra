# TASK-013.1 — Corregir el drift documental posterior a la fusión de `Task/013`

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/013.1-Corregir-Drift-Documental-Post-Merge` |
| **Nombre** | Corregir el drift documental posterior a la fusión de `Task/013` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. No altera el avance global (**13 de 41**) ni la ETAPA 04 (**1 de 3**) |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Dependencias** | `Task/013-Sistema-de-Diseno` — **Aprobada** ✔ (2026-09-04) |
| **Rama** | `Task/013.1-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | `38a8cdd4491f65e647aa1e735919d06e00f425ac` |
| **Fecha de inicio** | 2026-09-04 |
| **Fecha de aprobación** | **2026-09-04** |
| **Última actualización** | 2026-09-04 |
| **Próxima tarea** | `Task/014-Sitio-Publico` — **Pendiente, no iniciada** |

---

## 0. Preparación Git

Verificado **antes** de crear la rama: rama `main`, `main == origin/main`
(`38a8cdd`), working tree limpio, staging vacío y 0 ramas Task locales.

Tras crearla: `git rev-parse HEAD` == `git rev-parse main` (`38a8cdd`) y
`git rev-list --count main..HEAD` == `0`.

**La rama nació de `main`.** `dev` no interviene como base
([WORKFLOW §2.1](../project-management/WORKFLOW.md)).

`personal-blog-frontend` y `personal-blog-backend`: **solo lectura**, sin rama.

---

## 1. Objetivo

Convertir en **instantánea histórica fechada** la única afirmación de categoría **C** que
el barrido post-merge de `Task/013` encontró: la sección 24 de su reporte, que conserva
estado operativo de Git y GitHub redactado en presente.

---

## 2. Contexto — origen del drift

El reporte de `Task/013` se redactó **antes** de la aprobación. En ese momento no había
commits, ni push, ni pull request, y así se escribió la sección 24. Ese texto viajó
**dentro del propio PR** hacia `main`; al fusionarlo, el documento ya versionado siguió
afirmando en presente que los cambios estaban sin commit y que la tarea no estaba
aprobada — mientras su **propia cabecera** y su sección 25, inmediatamente posterior, la
declaran **Aprobada** el 2026-09-04.

Es el defecto estructural que describe
[WORKFLOW §6.1](../project-management/WORKFLOW.md), vigente desde `Task/005.6`, y el mismo
patrón que ya corrigieron `Task/006.1` y `Task/009.1`.

**No hay regla nueva que escribir.** §6.1 ya cubre el caso, y su punto 2 fija además la
forma correcta:

> Los datos históricos se marcan como históricos, con su fecha de observación. […]
> Escrito así, el paso del tiempo **no lo vuelve falso**.

### Por qué esto es una regresión, no una laguna

La forma canónica **ya existía en el proyecto** antes de `Task/013`: los reportes de
`Task/008` (§575) y `Task/009` (§882) encabezan su instantánea de Git con
*«Observado el `<fecha>`, **antes** de la aprobación»* y explican que los contadores son
transitorios por definición. El reporte de `Task/013` **no aplicó** ese patrón ya
establecido. La corrección consiste en alinearlo, no en inventar una convención.

---

## 3. Dentro del alcance

- [x] Convertir la sección 24 del reporte de `Task/013` en instantánea histórica:
      encabezado explícitamente histórico, marca de observación fechada y redacción en
      pasado.
- [x] **Preservar íntegros los valores originales** de la instantánea (ramas Task activas,
      contadores en `0`), sin sustituirlos por el estado actual.
- [x] Registrar este mantenimiento en `STATUS.md`, como exige
      [WORKFLOW §6](../project-management/WORKFLOW.md) —«al iniciar, al quedar lista y al
      aprobarse»— y **fuera** de las 41 filas oficiales.
- [x] Añadirlo al índice de reportes.
- [x] Barrido §6.1 con clasificación A / B / C explícita sobre la documentación de
      `Task/013` y los documentos de gobierno.
- [x] Ficha y reporte de este mantenimiento.

## 4. Fuera del alcance

| Excluido | Razón |
| --- | --- |
| La frase «`Task/014-Sitio-Publico` no se inicia hasta que `main` y `dev` queden normalizadas» (sección 27 del reporte de `Task/013`) | Clasificada **B** en el barrido post-merge: expresa la **regla de orden** que [WORKFLOW §6.1](../project-management/WORKFLOW.md) punto 4 avala textualmente. No afirma ningún hecho vivo de Git |
| Sección 23 del reporte de `Task/013` | Registro del barrido hecho al cerrar. El **estado de una tarea es duradero** por la tabla de §6.1, no transitorio: no es categoría C. Ver §9 |
| Tabla de la sección 24 | **Se conserva literalmente.** Sustituir sus ceros por el estado de hoy cambiaría un estado vivo por otro y volvería a violar el criterio 12 |
| Referencias históricas fechadas a PR anteriores en `STATUS.md` | Historia válida. **El historial no se reescribe** |
| Filas ausentes de `Task/010`–`Task/013` en el índice de reportes | *Drift* preexistente e **independiente**, arrastrado desde el cierre de esas tareas. **Decisión del usuario:** no se mezcla con este mantenimiento; se evaluará por separado si amerita una tarea propia. Aquí el índice solo registra `Task/013.1` |
| `ROADMAP.md`, `STAGE-04-user-experience.md`, `open-decisions.md`, `software-architecture.md` | El barrido encontró **0 apariciones de categoría C** |
| Contadores de avance | Este mantenimiento **no cuenta**: siguen **13 de 41** y ETAPA 04 **1 de 3** |
| **D-03** | Sigue **Resuelta** y **Vigente**. No cambia |
| Sistema de diseño, tokens, componentes, pruebas | Sin cambios. Tarea **exclusivamente documental** |
| `personal-blog-frontend`, `personal-blog-backend` | Sin cambios. No se crea rama en ellos |

### Alineación con el precedente `Task/009.1`

`Task/006.1` protegió el reporte de `Task/006` por ser una **instantánea cerrada**;
`Task/009.1` sí corrigió dos frases del de `Task/009`, por ser **condiciones vivas
orientadas al futuro**. Este caso es un tercer supuesto y conviene nombrarlo:

Aquí **sí** se toca una instantánea, pero **no para cambiar lo observado**. Los valores
permanecen intactos; lo que se corrige es que la instantánea **no estaba marcada como
tal** y su cierre estaba redactado en presente, contradiciendo a la cabecera del propio
documento. Se protege exactamente lo que `Task/006.1` protegía —la observación— y se
elimina lo que la hacía leerse como estado vigente.

---

## 5. Entregables

| Entregable | Ruta |
| --- | --- |
| Sección 24 convertida en instantánea histórica fechada | `docs/task-reports/TASK-013-report.md` |
| Registro de este mantenimiento | `docs/project-management/STATUS.md` |
| Índice de reportes: fila de este mantenimiento | `docs/task-reports/README.md` |
| Ficha de este mantenimiento | `docs/tasks/TASK-013.1-correct-post-merge-documentation-drift.md` |
| Reporte | `docs/task-reports/TASK-013.1-report.md` |

---

## 6. Criterios de aceptación

1. La rama nació de `main` actualizado y limpio; `HEAD == main` y `main..HEAD == 0`.
2. La sección 24 del reporte de `Task/013` lleva encabezado histórico y marca de
   observación fechada.
3. Su frase final está en **pasado** y no contradice la cabecera del documento.
4. Los valores originales de la instantánea se conservan **sin alterar**.
5. La instantánea **no** incorpora hashes ni estados actuales.
6. Barrido §6.1 con **C = 0**.
7. Los enlaces relativos de los documentos tocados resuelven.
8. El avance global sigue en **13 de 41** y la ETAPA 04 en **1 de 3**.
9. `personal-blog-frontend` y `personal-blog-backend` intactos.
10. Sin commit, push, merge ni pull request antes de la aprobación del usuario.

---

## 7. TDD / Plan test-first

**No aplica.** Tarea exclusivamente documental: no introduce comportamiento funcional de
backend ni de frontend. Criterio declarado según
[DEFINITION_OF_DONE](../project-management/DEFINITION_OF_DONE.md) §1.

---

## 8. Comandos de validación

```bash
# Barrido de estado transitorio en la documentacion tocada.
grep -niE "PR (abierto|pendiente)|pendiente de fusionar|esperando merge|sin commit|no aprobada" \
  docs/task-reports/TASK-013-report.md

# Resolucion de enlaces relativos.
# Contraste entre la cabecera del reporte y su seccion 24.
sed -n '1,13p' docs/task-reports/TASK-013-report.md
sed -n '/^## 24\./,/^## 25\./p' docs/task-reports/TASK-013-report.md
```

**No se ejecutan** pruebas de frontend ni de backend, Docker, PostgreSQL ni MinIO: nada
de eso entra en el alcance.

---

## 9. Decisiones técnicas

| # | Decisión | Alternativas | Justificación |
| --- | --- | --- | --- |
| D-13.1.1 | **Fechar la instantánea** en lugar de borrarla. | Eliminar la sección 24; actualizarla al estado de hoy. | Borrarla destruiría la evidencia de que el trabajo permaneció sin confirmar hasta la aprobación. Actualizarla reintroduciría estado vivo: el mismo defecto con otros valores. |
| D-13.1.2 | Adoptar la forma **ya canónica** en el proyecto: *«Observado el `<fecha>`, **antes** de la aprobación»*. | Redactar una fórmula nueva. | Los reportes de `Task/008` y `Task/009` ya la usan. Inventar otra fragmentaría la convención. |
| D-13.1.3 | **No** tocar la sección 23 del reporte. | Fecharla también. | El **estado de una tarea es duradero** según la tabla de [WORKFLOW §6.1](../project-management/WORKFLOW.md); no es estado transitorio de Git ni de GitHub, luego no es categoría C. Ampliar el alcance sin defecto demostrado contradice §5 del ciclo de vida. |
| D-13.1.4 | **No** tocar la frase sobre el inicio de `Task/014`. | Reescribirla. | Clasificada **B** en el barrido post-merge: es la regla de orden que §6.1 punto 4 avala de forma explícita. |

---

## 10. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | Corregir de más y reescribir historia legítima. | Pérdida de trazabilidad. | Alcance acotado a una sección; §4 enumera lo excluido con su razón. |
| 2 | Sustituir un estado vivo por otro. | Vuelve a violar el criterio 12. | Prohibición explícita de introducir hashes o estados actuales en la instantánea. |
| 3 | Que el mantenimiento altere el avance. | Recuento falso del roadmap. | No cuenta en las 41 tareas; los contadores no se tocan. |

---

## 11. Documentación creada o actualizada

- `docs/task-reports/TASK-013-report.md` — sección 24 convertida en instantánea fechada.
- `docs/project-management/STATUS.md` — registro del mantenimiento.
- `docs/task-reports/README.md` — índice.
- `docs/tasks/TASK-013.1-correct-post-merge-documentation-drift.md` — esta ficha.
- `docs/task-reports/TASK-013.1-report.md` — reporte.

---

## 12. Prevención de recurrencia

La regla ya existe ([WORKFLOW §6.1](../project-management/WORKFLOW.md)) y el criterio 12
ya está en la [Definition of Done](../project-management/DEFINITION_OF_DONE.md) desde
`Task/009.1`. **No se añade regla nueva**: lo que falló no fue la norma, sino su
aplicación al redactar una sección de instantánea.

Lo que sí conviene retener, y por eso queda escrito aquí: el barrido del criterio 12 debe
incluir **las secciones de instantánea de Git de los reportes**, no solo las frases que
condicionan tareas futuras. El barrido pre-approval de `Task/013` buscó lo segundo y no
lo primero, y por eso declaró `C = 0` sin detectar su propia sección 24.

---

## 13. Deuda pendiente

Ninguna derivada de este mantenimiento.

---

## 14. Próxima tarea

`Task/014-Sitio-Publico` — **Pendiente, no iniciada.** Es la siguiente tarea funcional del
roadmap y nace de `main` actualizado y limpio.

---

## 15. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-04** |
| **Aprobado por** | **jeffersondavila** (el usuario) |
| **Expresión de aprobación** | `approved: Task/013.1-Corregir-Drift-Documental-Post-Merge` |

La aprobación autorizó el flujo de cierre de
[`WORKFLOW.md`](../project-management/WORKFLOW.md) §3 en `personal-blog-infra`: commit,
integración en `dev` mediante merge `--no-ff` y pull request
`Task/013.1-Corregir-Drift-Documental-Post-Merge → main`.

**La fusión del pull request es decisión exclusiva del usuario.** Este mantenimiento
**no altera el avance**: sigue en **13 de 41** y la ETAPA 04 en **1 de 3**.
