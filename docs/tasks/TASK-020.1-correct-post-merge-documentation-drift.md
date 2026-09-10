# TASK-020.1 — Corregir el drift documental posterior a la fusión de `Task/020`

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/020.1-Corregir-Drift-Documental-Post-Merge` |
| **Nombre** | Corregir el drift documental posterior a la fusión de `Task/020` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. No altera el avance global (**20 de 41**, 49 %) ni la ETAPA 06 (**2 de 3**, 67 %) |
| **Estado** | **Aprobada** ✔ el 2026-09-10 por el usuario |
| **Fecha de aprobación** | **2026-09-10** |
| **Expresión de aprobación** | `approved: Task/020.1-Corregir-Drift-Documental-Post-Merge` |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Dependencias** | `Task/020-CI-Backend` — **Aprobada** ✔ el 2026-09-10; PR `#15` y `#36` fusionados y normalización `main → dev` completada |
| **Rama** | `Task/020.1-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | **`68469dd016514fafc7ce07da120e908fa8873849`** (`= main = origin/main` al crearla) |
| **Fecha de inicio** | 2026-09-10 (Guatemala) |
| **Pull request** | `Task/020.1 → main`, creado **durante el cierre aprobado** del 2026-09-10, con base `main` y head esta rama Task. **Su estado se consulta en vivo** (`gh pr list --head Task/020.1-Corregir-Drift-Documental-Post-Merge`), no en este documento: [WORKFLOW §6.1](../project-management/WORKFLOW.md) |
| **Reporte** | [TASK-020.1-report.md](../task-reports/TASK-020.1-report.md) |

---

## 0. Preparación Git

| # | Comprobación | Resultado real |
| --- | --- | --- |
| 1 | `git fetch --prune origin` | Ejecutado en `personal-blog-infra` |
| 2 | `git switch main` · `git pull --ff-only origin main` | `Already up to date` |
| 3 | `main == origin/main` | **`68469dd016514fafc7ce07da120e908fa8873849`** en ambos |
| 4 | `git status --porcelain` | **vacío** |
| 5 | *Staging* | **0 archivos** |
| 6 | Rama `Task/020.1` local y remota | **inexistente** antes de crearla |
| 7 | Pull request previo con ese *head* | **ninguno** |
| 8 | `git switch -c Task/020.1-…` | Creada **desde `main`** |
| 9 | `HEAD == main` inmediatamente después | **coinciden** |
| 10 | `git rev-list --count main..HEAD` | **0** |

Regla permanente: [WORKFLOW §2.1](../project-management/WORKFLOW.md). Ninguna
rama Task nace de `dev`.

## 1. Objetivo

Aplicar el **criterio 12** al contenido durable que dejó `Task/020`, y corregir
las contradicciones documentales que esa tarea detectó pero declaró fuera de su
alcance.

`Task/020` está **cerrada y aprobada**. Esta tarea **no** revisa su
implementación, sus gates, sus decisiones ni su aprobación: solo el texto que la
describe.

## 2. Contexto — por qué existe esta tarea

Por tercera vez en la ETAPA 06 se repite el mismo defecto **estructural** que
[WORKFLOW §6.1](../project-management/WORKFLOW.md) describe: el cierre de una
tarea documenta su propio estado **antes** de que el usuario fusione el pull
request. En ese instante el PR está abierto y la rama remota existe, así que el
documento lo escribe en presente. Ese texto viaja **dentro del propio PR** hacia
`main`. Cuando el usuario fusiona —el paso siguiente e inevitable del flujo— el
documento ya versionado sigue afirmando que el PR queda sin fusionar.

`Task/020` lo dejó en **nueve** afirmaciones de clase **C**, repartidas entre su
ficha §20 y su reporte: los PR «quedan sin fusionar», la rama remota «se
conserva», la normalización `main → dev` «pendiente después de que el usuario
fusione», y el estado pre-aprobación —«sin merge a `dev`, sin PR, sin tocar
`main`»— presentado como resultado final en lugar de como momento fechado.

A ese grupo se suman **ocho** contradicciones de clase **D**. Dos las detectó y
registró `Task/020` durante su cierre, declarándolas expresamente fuera de
alcance y pendientes de autorización:

- **B-020-4** — el registro histórico de `Task/002.1` en STATUS llevaba una fila
  «Avance global» con **44 % — 18 de 41**: un contador vivo dentro de un registro
  histórico, que no era cierto en 2026-07-26 ni después.
- **B-020-5** — **cinco** encabezados «Última tarea aprobada» simultáneos en
  STATUS, porque cada tarea añadía el suyo sin degradar el anterior.

Las otras seis son conteos internos del reporte de `Task/020` que no cuadraban
entre sí: número de ejecuciones de Actions, número de commits del backend,
número de documentos de infra, alcance real del barrido de secretos y la propia
tabla del criterio 12, que declaraba **C = 0** conviviendo con las nueve
afirmaciones de estado vivo.

**Ninguno de los diecisiete hallazgos cuestiona la implementación de
`Task/020`.** Los gates, los *locks*, la CI y la suite estaban y siguen estando
en verde. Todos son defectos del texto que los describe.

## 3. Clasificación aplicada

| Clase | Qué es | Tratamiento |
| --- | --- | --- |
| **A** | Regla permanente de gobierno | Se conserva tal cual |
| **B** | Hecho histórico fechado | Se conserva; si le falta el ancla temporal, se le añade |
| **C** | Estado vivo de Git o GitHub escrito como presente | Se convierte en hecho fechado, o se omite |
| **D** | Contradicción documental | Se corrige |

Una afirmación que era cierta en su fecha **no se borra**: se ancla. Lo que se
elimina es la **pretensión de vigencia**, no la evidencia.

## 4. Alcance

- [x] Verificar en lectura la ejecución **34491446991** de `CI Backend` sobre
      `dev`, posterior a la normalización, antes de crear la rama.
- [x] Reproducir los **nueve** hallazgos **C** y los **ocho** hallazgos **D**
      antes de corregir cualquiera.
- [x] Convertir los nueve **C** en hechos fechados o en estado pre-aprobación
      anclado.
- [x] Corregir los ocho **D**, **B-020-4** y **B-020-5** incluidos.
- [x] Reconstruir el valor histórico real de la fila de `Task/002.1` **desde el
      historial de Git**, sin inventar ningún porcentaje.
- [x] Registrar como evidencia fechada los PR `#15` y `#36`, sus `mergedAt`, sus
      merge commits, los dos merges de normalización y las dos ejecuciones de
      Actions que el cierre produjo.
- [x] Barrido amplio del criterio 12 sobre el conjunto documental afectado.
- [x] Ficha, reporte e índice de reportes de esta maintenance.

### Fuera de alcance

- **No** se modifica `personal-blog-backend` ni `personal-blog-frontend`.
- **No** se toca código, tests, workflows, *locks*, `Dockerfile`, Terraform, ni
  la configuración de GitHub.
- **No** se ejecuta la suite del backend, ni Docker, ni CI nueva.
- **No** se destruye el laboratorio `task020-*`: eliminar contenedores es una
  operación destructiva y requiere autorización expresa.
- **No** se reabre `Task/020`, que sigue **Aprobada**.
- **No** se reabre **R-14**, que sigue **Cerrado**, ni se retira **S-09
  backend**, que sigue satisfecho.
- **No** se cierra la ETAPA 06, que sigue en **2/3** y exige `Task/021`.
- **No** se crea ni se promueve ningún ADR ni decisión nueva.
- **No** se repite la normalización de Git, ya completada y verificada.
- **No** se inicia `Task/021`.
- **ROADMAP no se modifica:** se auditó y no contiene ninguna contradicción
  vigente.

## 5. Qué puede y qué no puede persistirse

| Sí puede persistirse | No debe persistirse |
| --- | --- |
| Números de PR (`#15`, `#36`) y su dirección `Task → main` | «El PR está abierto» o «esperando merge» |
| Fechas reales de fusión y `mergedAt` | «La rama remota existe / se conserva» como estado vivo |
| Merge commits `8055878` y `68469dd` | Working tree o *staging* actuales |
| Merges de normalización `5fedcb3` y `122c90a` | SHA de `main` y `dev` como estado vigente |
| Identificadores y conclusión de los runs 34481253970, 34481957688, 34485074950, 34488083060, 34489982595 y 34491446991 | «El workflow está verde ahora» |
| Que la fusión y el borrado de las ramas remotas los hizo **el usuario** | «Queda para el usuario fusionar» como pendiente vigente |
| El estado pre-aprobación, **fechado y nombrado como tal** | El estado pre-aprobación presentado como resultado final |
| Un contador histórico **probado** para su fecha | Un contador vivo dentro de un registro histórico |

**Sobre esta propia maintenance:** sus documentos **no** describen el estado
operativo de su propia rama, PR o normalización. No dicen que estén pendientes ni
que hayan ocurrido: simplemente lo **omiten**. Así el post-merge de `Task/020.1`
es Git-only y no genera una `Task/020.2`.

## 6. Criterio de éxito

| # | Criterio |
| --- | --- |
| 1 | Los 17 hallazgos reproducidos **antes** de corregirlos |
| 2 | Toda afirmación de clase **C** convertida en hecho fechado o en estado pre-aprobación anclado |
| 3 | Toda contradicción de clase **D** corregida |
| 4 | **C = 0** y **D = 0**, verificados sobre el texto vigente |
| 5 | Ninguna evidencia histórica útil eliminada ni reescrita |
| 6 | Los dos momentos —pre-aprobación y post-fusión— quedan distinguidos, no fundidos |
| 7 | Valor histórico de `Task/002.1` **probado en Git**, no inventado |
| 8 | `grep -c "^## Última tarea aprobada"` en STATUS = **1** |
| 9 | Avance del roadmap sin cambios: **20 / 41 = 49 %**, ETAPA 06 **2 / 3 = 67 %** |
| 10 | Enlaces documentales verificados, 0 rotos |
| 11 | 0 patrones de secreto |
| 12 | Sin commit, push ni PR mientras la tarea esté pendiente de aprobación |

## 7. Límites

- No se ejecuta ninguna operación destructiva.
- No se marca ningún ADR ni decisión nueva como aceptada.
- Los criterios de salida de STAGE-06 **siguen abiertos**: exigen los tres
  repositorios y `Task/021` sigue pendiente.
- El control negativo **remoto** sigue sin autorizarse.
- **R-15**, **R-17** y **R-37** siguen abiertos, sin cambio.
- **D-020-H** sigue anotada como decisión abierta: el `.venv` de Windows no
  reproduce el árbol bloqueado.
