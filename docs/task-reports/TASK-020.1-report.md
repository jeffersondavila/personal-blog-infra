# Reporte — TASK-020.1 · Corregir el drift documental posterior a la fusión de `Task/020`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/020.1-Corregir-Drift-Documental-Post-Merge` |
| **Tipo** | Mantenimiento de gobierno documental posterior a la fusión |
| **Estado** | **Aprobada** ✔ el 2026-09-10 por el usuario |
| **Expresión de aprobación** | `approved: Task/020.1-Corregir-Drift-Documental-Post-Merge` |
| **Fecha** | 2026-09-10 (Guatemala) |
| **Repositorios** | `personal-blog-infra` **únicamente** |
| **Cuenta en el roadmap** | **No.** Avance global (**20 de 41**) y ETAPA 06 (**2 de 3**) **sin cambios** |
| **Ficha** | [TASK-020.1](../tasks/TASK-020.1-correct-post-merge-documentation-drift.md) |

---

## 1. Punto de partida

`Task/020` fue **aprobada** el 2026-09-10. Su cierre creó los pull request `#15`
(backend) y `#36` (infra), ambos `Task/020-CI-Backend → main`, y los dejó
correctamente **sin fusionar** para revisión del usuario.

*Observado el 2026-09-10 UTC:* el usuario los fusionó manualmente y eliminó las
dos ramas Task remotas. La normalización `main → dev` se ejecutó a continuación y
quedó verificada.

| Repositorio | PR | `mergedAt` | Merge commit | Normalización `dev` |
| --- | --- | --- | --- | --- |
| backend | `#15` | 2026-09-10T14:42:42Z | `8055878e415ace2bfc4e7685e0549c5ab8a642ef` | `5fedcb34f8f1542fcfb0957547e58f472529f6f2` |
| infra | `#36` | 2026-09-10T14:42:24Z | `68469dd016514fafc7ce07da120e908fa8873849` | `122c90a5d321d5dd3808d1d38f8c0b60351d9175` |

Comprobado en lectura antes de crear esta rama: `git ls-remote --heads origin
"Task/*"` devuelve **vacío** en los dos repositorios, y `gh pr view` devuelve
**`MERGED`** para ambos.

### Verificación previa de CI sobre `dev`

Antes de crear la rama de esta maintenance se verificó, **solo en lectura**, la
ejecución de `CI Backend` posterior a la normalización. Es la condición que el
prompt de la tarea imponía para poder continuar.

| Campo | Esperado | Observado |
| --- | --- | --- |
| Identificador | 34491446991 | **34491446991** |
| Workflow | `CI Backend` | **`CI Backend`** |
| Evento | `push` | **`push`** |
| Rama | `dev` | **`dev`** |
| Head SHA | `5fedcb34…` | **`5fedcb34f8f1542fcfb0957547e58f472529f6f2`** |
| Estado | `completed` | **`completed`** |
| Conclusión | `success` | **`success`** |

Duración de extremo a extremo **334 s** (14:48:07Z → 14:53:41Z). El único job,
`Backend quality`, concluyó en `success` con sus **21 pasos en verde**, sin
ninguna excepción, y la suite cerró en **`1855 passed in 202.98s`**, **0
omitidas**. Los 19 pasos declarados en el workflow más *Set up job* e *Initialize
containers*, que añade GitHub, son los 21 auditados.

Existía además la evidencia histórica de la ejecución `pull_request`, también
verificada en lectura: run **34489982595**, evento `pull_request`, head
`22af3f18d9fd2f955319ea1131bac7c40e57b3df`, conclusión **`success`**, **21 pasos
en verde**, **1855** pruebas y **0** omitidas.

**El SUCCESS quedó confirmado, así que la maintenance procedió.**

## 2. Regla aplicada

[WORKFLOW §6.1](../project-management/WORKFLOW.md), vigente desde `Task/005.6`:

> Los documentos versionados registran **estado duradero**. El estado transitorio de Git y
> GitHub —PR abierto o fusionado, rama remota, sincronización actual— se **consulta en
> vivo** y solo se archiva como **observación fechada**.

## 3. Causa del drift

Son dos causas distintas, y conviene no fundirlas.

**La primera es estructural y ya conocida.** El cierre de una tarea documenta su
propio estado **antes** de que el usuario fusione el pull request. En ese instante
el PR está abierto y la rama remota existe, así que el documento lo escribe en
presente. Ese texto viaja **dentro del propio PR** hacia `main`. Cuando el usuario
fusiona —el paso siguiente e inevitable del flujo— el documento ya versionado
sigue afirmando que el PR queda sin fusionar. `Task/019.1` dejó anotada
exactamente esta lección para `Task/020` y `Task/021`; `Task/020` la aplicó a
medias: acertó al no persistir el número de PR ni los SHA vivos, y falló al
describir el resultado del cierre en presente.

**La segunda es aritmética.** El reporte de `Task/020` se escribió y reescribió
en tres fases —implementación, revisión previa a la aprobación y cierre— y varios
conteos quedaron congelados en el valor de una fase anterior: «dos ejecuciones»
cuando ya eran cuatro, «un commit» cuando eran cuatro, «seis documentos» cuando
eran siete. Ninguno afecta a la implementación; todos hacían que el documento se
contradijera consigo mismo a pocas líneas de distancia.

A eso se suman los **dos hallazgos que `Task/020` detectó y declaró fuera de su
alcance**, dejándolos pendientes de autorización expresa: **B-020-4** y
**B-020-5**. Esta maintenance es la autorización que les faltaba.

## 4. Drift encontrado

Los 17 hallazgos se **reprodujeron uno por uno** sobre el texto vigente en `main`
(`68469dd`) antes de corregir cualquiera de ellos.

### Categoría C — nueve, corregidas

| # | Archivo | Texto original reproducido |
| --- | --- | --- |
| **C-1** | `docs/tasks/TASK-020-ci-backend.md` §20 | «los pull request **`Task/020-CI-Backend → main`**, que quedan **sin fusionar**» y «la rama Task local se eliminó con `git branch -d`; la remota **se conserva**» |
| **C-2** | `docs/task-reports/TASK-020-report.md` §Cierre aprobado | «La rama Task **remota se conserva**.» |
| **C-3** | `docs/task-reports/TASK-020-report.md` §Cierre aprobado | «**Los pull request se dejan sin fusionar.**» |
| **C-4** | `docs/task-reports/TASK-020-report.md` §Cierre aprobado | «Pendiente después de que el usuario fusione: la normalización `main → dev` en los dos repositorios.» |
| **C-5** | `docs/task-reports/TASK-020-report.md` §AD | «… en ambos repositorios, **sin fusionar**. Queda para el usuario aceptar o rechazar el PR, y después la normalización `main → dev`» |
| **C-6** | `docs/task-reports/TASK-020-report.md` §Veredicto | «se crearon los pull request `Task/020-CI-Backend → main`, que **quedan sin fusionar**» |
| **C-7** | `docs/task-reports/TASK-020-report.md` §AA y §AB | «árbol limpio, staging vacío, **rama publicada**. Sin merge a `dev`, sin PR» y «siete documentos **sin commit**. Sin push, sin PR» |
| **C-8** | `docs/task-reports/TASK-020-report.md` §Ejecución real de GitHub Actions | «No se integró `dev`, no se creó pull request y no se tocó `main`.» |
| **C-9** | `docs/task-reports/TASK-020-report.md` §Criterion 12, fila C | «**0.** … **no se afirma la existencia de ningún PR**» — contradicho por las ocho anteriores del propio documento |

### Categoría D — ocho, corregidas

| # | Archivo | Contradicción reproducida |
| --- | --- | --- |
| **D-1** *(B-020-4)* | `docs/project-management/STATUS.md` §Mantenimiento de gobierno anterior | El registro histórico de `Task/002.1` —aprobado el 2026-07-26— llevaba «**Avance global** — **44 %** — 18 de 41»: un contador vivo dentro de un registro histórico, falso para esa fecha y para el presente |
| **D-2** *(B-020-5)* | `docs/project-management/STATUS.md` | **Cinco** encabezados `## Última tarea aprobada` simultáneos: Task/020 (línea 107), Task/016 (313), Task/015 (457), Task/013 (832) y Task/006 (1258) |
| **D-3** | `TASK-020-report.md` §Criterion 12 y `STAGE-06` | Ambos declaraban **C = 0 · D = 0** conviviendo con las nueve **C** de arriba y con **B-020-4** / **B-020-5** sin corregir |
| **D-4** | `TASK-020-report.md` §Criterion 12, fila B | «escaneos y **dos ejecuciones reales**», cuando el propio reporte documenta cuatro `push` y, tras el cierre, una `pull_request` |
| **D-5** | `TASK-020-report.md` §Ejecución real de GitHub Actions | «se observaron **dos** ejecuciones reales» seguido, dos líneas después, de «**Las cuatro** son del workflow `CI Backend`» |
| **D-6** | `TASK-020-report.md` §Auditoría paso a paso | «sobre las 2 448 y 2 447 líneas de log de **las dos ejecuciones**: 0 coincidencias», presentado como si el barrido cubriera todas las ejecuciones |
| **D-7** | `TASK-020-report.md` §Criterion 12, fila A | «sin merge a `dev`, sin PR, sin tocar `main`» presentado como resultado final, contradiciendo el cierre aprobado descrito en el mismo documento |
| **D-8** | `docs/tasks/TASK-020-ci-backend.md` §14 | «Backend, **en un commit**» e «Infra: **seis documentos**, **sin commit**», cuando el backend tuvo **4 commits** y el commit documental de infra abarcó **7 documentos** |

### Categoría B — conservadas sin cambios

- Todo el preflight de `Task/020` del 2026-09-09, con sus SHA base y sus
  comprobaciones. Está fechado y era cierto.
- El baseline: exit 4 de `pytest -W error`, la deriva de `anyio`, la tabla de
  bisección `anyio`/`starlette` y el `1 failed, 1854 passed`.
- Las tres vulnerabilidades de `httpx2` con sus CVE, vectores CVSS y versiones
  corregidas, y la detención que motivaron.
- Los **7** controles negativos de gates y los **3** del escáner, con sus exit
  codes, y la nota del control 7 sobre los digest múltiples.
- Los conteos de Trivy —173 de inventario, 0 con corrección— y la auditoría paso
  a paso de la segunda ejecución.
- Los identificadores 34481253970, 34481957688, 34485074950 y 34488083060 con sus
  duraciones y sus suites.
- **B-020-1**, **B-020-2** y **B-020-3A/B** del preflight, y **D-020-1**,
  **D-020-2** y **D-020-3** de la revisión previa a la aprobación, con su
  clasificación, su evidencia y su autorización.
- La observación histórica del 2026-09-09 que dice «Infra: **seis** documentos …
  sin commit»: era exacta en ese instante, **antes** de que la corrección de
  B-020-3 añadiera el séptimo. Se conserva intacta, y su fecha es lo que la
  mantiene verdadera.
- Las **276 referencias relativas, 0 rotas** medidas el 2026-09-09 sobre los seis
  documentos de entonces.

### Categoría A — conservadas sin cambios

- La regla de que aceptar o rechazar un PR hacia `main`, y decidir si se elimina
  la rama remota, es **responsabilidad exclusiva del usuario**.
- La regla de que antes de la aprobación no se integra `dev`, no se crea PR y no
  se toca `main`. Se conserva **como regla**, separada del estado que describía.
- El diseño del workflow, sus gates, su orden y sus 19 pasos declarados.
- Las decisiones **D-020-A** a **D-020-H**, **vigentes** desde la aprobación.
- **R-14 cerrado**; **R-15**, **R-17** y **R-37** abiertos con su estado.
- El reparto de **S-09** entre Task019, Task020 y Task021, y la asignación del
  escaneo del historial de secretos a `Task/021`.
- Los criterios de salida de STAGE-06, que **siguen sin marcar**: exigen los tres
  repositorios.
- La no autorización del control negativo **remoto**.

### Coincidencias descartadas tras clasificación semántica

| Coincidencia | Por qué no es drift |
| --- | --- |
| `TASK-020-report.md` §B-020-3, «El pull request hacia main queda abierto» | **Cita** del texto defectuoso que `Task/020` corrigió en el reporte de `Task/019`. Es el hallazgo, no una afirmación propia |
| `TASK-019-report.md` §R, «se dejaron sin fusionar para revisión del usuario» | Ya anclado por `Task/020` como hecho del cierre, con la fusión del 2026-09-09 registrada aparte |
| STATUS §Task/006, «las **remotas se conservan**» | Dentro de «**Observado el 2026-08-18**». Hecho fechado, correcto para su día |
| STATUS §Task/018 y §Task/019, «Avance: 18/41 — 44 %» y «19/41 — 46 %» | Contribución histórica de cada tarea a su fecha |
| STATUS §Task/019.1, «no se alteró ningún contador: 19/41 — 46 %» | Correcto para el 2026-09-09 |
| `TASK-019-ci-frontend.md` §4, «el avance aprobado se conserva en 18/41 — 44 %» | Estado al iniciar `Task/019`, correcto entonces |
| «los **seis contenedores** del entorno local» | Es el entorno Docker local, no el conteo de documentos |
| ROADMAP entero | Auditado: 20/41 ≈ 49 %, ETAPA 06 2/3, Task021 Pendiente. **Sin contradicción vigente, no se modifica** |
| Criterios de salida de STAGE-06 sin marcar | Correctamente abiertos: falta `Task/021` |
| «Recursos temporales que siguen en la máquina» | Estado de contenedores Docker locales, no estado de Git ni de GitHub. Fuera de la clase C, y el laboratorio **no se toca** |

## 5. Corrección aplicada

**C-1 → B.** La ficha §20 conserva que el cierre creó los PR y los dejó para
revisión manual del usuario, y añade una observación fechada del 2026-09-10 UTC
con la fusión de `#15` y `#36`, sus merge commits, el borrado de las ramas remotas
por el usuario y los dos merges de normalización. La frase «la remota se
conserva» desaparece como estado; el borrado queda registrado como acto del
usuario.

**C-2, C-3, C-4 y C-6 → B.** En el reporte, la sección de cierre pasa a decir que
al terminar el cierre la rama remota **seguía publicada** —hecho de ese momento— y
que los PR **se dejaron** para revisión manual, que es la regla. La normalización
deja de figurar como pendiente. El veredicto final incorpora la observación
fechada de la fusión en lugar de afirmar que los PR quedan sin fusionar.

**C-5 → B.** La fila **AD** se renombra de «Pendientes post-approved» a «Cierre y
normalización» y pasa a registrar el resultado completo con fechas, merge commits
y merges de normalización, cerrando con «**Nada pendiente** de este flujo».

**C-7 y C-8 → B.** Las filas **AA** y **AB** y el párrafo de la ejecución real se
abren con «*Estado observado antes de la aprobación*» / «*Estado pre-aprobación*»
y remiten explícitamente a las secciones del cierre. No se elimina nada: eran
ciertas, y ahora dicen **cuándo**.

**C-9 → corregida.** La fila C del criterio 12 enumera lo que sí es hecho fechado
—números de PR, `mergedAt`, merge commits, SHA, identificadores de ejecución— y
lo que el documento **no** afirma: ningún PR abierto, ninguna rama remota vigente,
ningún estado actual de `main` o `dev`.

**D-1 corregida sin inventar ningún número.** El valor histórico se **reconstruyó
desde el historial durable**, no se estimó. El commit `700be94`, que es el propio
cierre de `Task/002.1` del 2026-07-26, registraba en esa misma fila «Permanece en
**2 de 41**, aproximadamente **5 %**», y la tabla de avance de ese mismo commit
cierra en «Total **41 · 2 · 5 %**». Las dos fuentes concuerdan, así que el valor
queda **probado** y se restaura fechado, con la etiqueta «Avance global en su
fecha» y la frase durable de que este mantenimiento no cuenta dentro de las 41 ni
alteró el avance canónico. Se documenta además el origen exacto del defecto: el
commit `83cffe4` del 2026-09-08, del cierre de `Task/018`, actualizó el contador
global y alcanzó también este registro histórico.

**D-2 corregida.** Los cuatro encabezados heredados —Task/016, Task/015,
Task/013 y Task/006— pasan a `## Tarea aprobada anterior — …`, la convención que
STATUS ya usaba para Task/019, Task/018, Task/017 y Task/014. **Solo se cambió la
línea del encabezado: ningún contenido histórico se tocó.** Queda **un único**
`## Última tarea aprobada`, el de `Task/020`.

**D-3 recalculada, no borrada.** Las afirmaciones **C = 0 · D = 0** se conservan y
se acompañan de una nota que dice **cuándo se recalcularon y por qué eran
prematuras**: se escribieron durante el cierre, antes de que la fusión existiera.
Tras las correcciones de esta maintenance vuelven a ser ciertas, y ahora sí
verificadas sobre el texto vigente. La misma nota se añade en STAGE-06.

**D-4 corregida con el desglose por evento.** La fila B del criterio 12 pasa a
declarar **cuatro** ejecuciones `push` sobre la rama Task, **una** `pull_request`
y **una** `push` sobre `dev` tras la normalización: **seis en total**, todas
`success`, cada una con su identificador. No se habla de «total» sin decir el
evento y el contexto.

**D-5 corregida cronológicamente.** El párrafo pasa a «Se observaron **cuatro**
ejecuciones … las dos primeras durante la implementación y las dos últimas tras
los commits de la revisión previa a la aprobación». Los cuatro identificadores
reales se conservan.

**D-6 acotada.** El barrido queda declarado con su alcance exacto: se ejecutó
sobre los logs completos de **dos** ejecuciones concretas, la primera y la
segunda, de 2 448 y 2 447 líneas, y **no se extrapola**. Los barridos de la
tercera y la cuarta siguen en su propio párrafo, y los de las dos ejecuciones
posteriores al cierre se registran con sus propias cifras, medidas en esta
maintenance.

**D-7 anclada.** La fila A del criterio 12 separa la **regla permanente** —antes
de aprobar no se integra `dev`, no se crea PR y no se toca `main`— del **estado
pre-aprobación observado**, y remite al cierre aprobado para el resultado final.

**D-8 corregida contra Git.** Antes de escribir se comprobó el historial:

| Comprobación | Comando | Resultado |
| --- | --- | --- |
| Commits del backend en el PR `#15` | `git log --oneline --no-merges 8055878~1..8055878` | **4**: `557ca7e`, `f2b3d85`, `81ce14c`, `22af3f1` |
| Commit documental de infra | `git log --oneline --no-merges 68469dd~1..68469dd` | **1**: `6bc80e8` |
| Documentos de ese commit | `git show --stat 6bc80e8` | **7 archivos**, 1127 inserciones, 38 supresiones |

La ficha §14 pasa a declarar los cuatro commits del backend con sus SHA y los
siete documentos de infra con el SHA del commit documental. Las menciones
paralelas de §13, §17 y de la sección Documentación del reporte se alinean con
el mismo conteo.

### Correcciones adicionales, misma clase, dentro del mismo conjunto

La auditoría amplia del §12 del prompt destapó tres inconsistencias más de la
**misma naturaleza** que las anteriores, estrictamente documentales y directamente
relacionadas con la coherencia que esta maintenance certifica:

| Hallazgo | Archivo | Corrección |
| --- | --- | --- |
| **Tres** encabezados `## Último mantenimiento aprobado` simultáneos —Task/019.1 (2026-09-09), Task/012.1 (2026-09-05) y Task/004.2 (2026-09-06)—, y en la vista rápida la etiqueta «Último mantenimiento aprobado» sobre `Task/004.2` mientras `Task/019.1`, **posterior**, figuraba solo como «Último mantenimiento» | `STATUS.md` | Es exactamente el defecto que **B-020-5** nombra, en la familia de encabezados vecina. Queda **un único** «Último mantenimiento aprobado», el de `Task/019.1`, que es el más reciente **aprobado**. `Task/012.1` pasa a «Mantenimiento funcional anterior» y `Task/004.2` a «Mantenimiento aprobado anterior», ambas convenciones ya presentes en el documento. Contenido histórico intacto |
| La ficha §17 mandaba comprobar «los **19** pasos» de la ejecución, pero la ejecución muestra **21**, y STATUS y el reporte hablaban de 21 | `TASK-020-ci-backend.md`, `TASK-020-report.md` | Se distingue de forma explícita: **19 pasos declarados** en el YAML y **21** en la ejecución, porque GitHub añade *Set up job* e *Initialize containers*. Verificado contando `- name:` en el workflow de `main`: **19** |
| La fila de `Task/019.1` en el índice de reportes carecía del marcador *(mantenimiento)* que llevan las demás, aunque la nota al pie sí la lista como mantenimiento | `docs/task-reports/README.md` | Marcador añadido |

Ninguna implica decisión funcional ni arquitectónica. **No apareció ninguna
contradicción que exigiera detenerse.**

## 6. Evidencia histórica registrada

Queda escrita, fechada y sin estado vivo:

- **PR `#15`** (backend): `MERGED`, `mergedAt = 2026-09-10T14:42:42Z`, merge
  commit `8055878e415ace2bfc4e7685e0549c5ab8a642ef`.
- **PR `#36`** (infra): `MERGED`, `mergedAt = 2026-09-10T14:42:24Z`, merge commit
  `68469dd016514fafc7ce07da120e908fa8873849`.
- Los dos fueron **`Task/020-CI-Backend → main`**. Ninguno usó `dev` como *head*.
- Normalización `main → dev`: `5fedcb34f8f1542fcfb0957547e58f472529f6f2`
  (backend) y `122c90a5d321d5dd3808d1d38f8c0b60351d9175` (infra), los dos merges
  `--no-ff` con mensaje `merge: normalizar main en dev despues de
  Task/020-CI-Backend`.
- Ramas `Task/020`: eliminadas **localmente** durante el cierre con
  `git branch -d`; las **remotas** las eliminó después el usuario.
- **CI `pull_request`:** run **34489982595**, head `22af3f18…`, `success`, **21
  pasos en verde**, **1855** pruebas, **0** omitidas.
- **CI `push` sobre `dev`:** run **34491446991**, head `5fedcb34…`, `success`,
  **21 pasos en verde**, **1855** pruebas, **0** omitidas, 334 s.
- Con ambas, el workflow del backend tiene evidencia real de sus **dos** triggers
  y un verde sobre `dev`. **Eso no completa la ETAPA 06:** sus criterios de salida
  exigen los tres repositorios y `Task/021` sigue pendiente.

## 7. Archivos

### Creados

| Archivo |
| --- |
| `docs/tasks/TASK-020.1-correct-post-merge-documentation-drift.md` |
| `docs/task-reports/TASK-020.1-report.md` |

### Modificados

| Archivo | Qué cambia |
| --- | --- |
| `docs/tasks/TASK-020-ci-backend.md` | §20 con la fusión fechada (**C-1**); §14 con 4 commits y 7 documentos (**D-8**); §13 y §17 alineados con ese conteo y con la distinción 19/21 pasos |
| `docs/task-reports/TASK-020-report.md` | **C-2** a **C-9**; **D-3** a **D-8**; nueva sección «Evidencia posterior al cierre»; estado de **B-020-4** / **B-020-5** actualizado |
| `docs/project-management/STATUS.md` | **D-1** (B-020-4) y **D-2** (B-020-5); `Task/020.1` registrada primero como mantenimiento en curso durante la fase pre-aprobación y promovida a último mantenimiento aprobado durante el cierre; observación fechada del cierre y la fusión de `Task/020`; familia «Último mantenimiento aprobado» normalizada |
| `docs/stages/STAGE-06-continuous-integration.md` | Evidencia fechada de los runs `pull_request` y `push` sobre `dev`; nota de recálculo del criterio 12 |
| `docs/task-reports/README.md` | `Task/020.1` añadida al índice y a la nota de mantenimientos; marcador de `Task/019.1` |

**No se modificó** `ROADMAP.md`: se auditó y no contiene ninguna contradicción
vigente.

## 8. Verificación

| # | Comprobación | Resultado |
| --- | --- | --- |
| 1 | `git diff --check` | **sin errores**, exit 0 |
| 2 | Referencias relativas de todos los documentos tocados, excluidos los bloques de código | **226 comprobadas, 0 rotas** |
| 3 | Secretos reales en los documentos tocados: material de clave privada, `AKIA…`, tokens `gh*_`, JWT y cualquier `clave = valor` con valor de 12+ caracteres | **0 coincidencias.** Los nombres de patrón aparecen como literales en la prosa que describe los barridos, y eso no es un secreto |
| 4 | Barrido de clase **C** sobre el conjunto documental | **0** afirmaciones de estado vivo |
| 5 | Barrido de clase **D** | **0** contradicciones |
| 6 | `grep -c "^## Última tarea aprobada"` en STATUS | **1** |
| 7 | `grep -c "^## Último mantenimiento aprobado"` en STATUS | **1** |
| 8 | Tabla completa de tareas de STATUS | **41 filas**, ninguna de mantenimiento; `Task/020` Aprobada, `Task/021` Pendiente |
| 9 | Resumen del avance de STATUS | Total **41 · 20 · 49 %**; ETAPA 06 **3 · 2 · 67 %** |
| 10 | ROADMAP | **20/41 ≈ 49 %**, ETAPA 06 **2/3**, sin modificar |
| 11 | Archivos fuera de `personal-blog-infra/docs/` | **ninguno** |
| 12 | `personal-blog-backend` y `personal-blog-frontend` | intactos, en `main`, sin rama Task |
| 13 | Laboratorio `task020-*` | **no se tocó** |

**Límites respetados antes de la aprobación.** *Estado observado el 2026-09-10,
con la tarea en Lista para validación:* `git diff --cached --name-only` vacío,
`git rev-list --count main..HEAD` = **0**, ninguna rama Task de esta tarea en
`origin` y ningún pull request con este *head*. Es decir: **sin commit, sin push,
sin merge a `dev`, sin PR y sin tocar `main`** mientras la tarea estuvo pendiente
de aprobación, como exige el flujo. Los pasos que siguieron se ejecutaron **solo**
después de la aprobación, y constan en §14.

## 9. Criterion 12 final

| Clase | Resultado |
| --- | --- |
| **A — reglas permanentes** | Conservadas: responsabilidad exclusiva del usuario sobre el PR y la rama remota; prohibición de integrar `dev`, crear PR o tocar `main` antes de aprobar; diseño del workflow; decisiones **D-020-A** a **D-020-H** vigentes; criterios de salida de STAGE-06 abiertos |
| **B — hechos históricos fechados** | Ampliados: PR `#15` y `#36` con sus `mergedAt` y merge commits; borrado de las ramas remotas por el usuario; normalizaciones `5fedcb3` y `122c90a`; runs 34489982595 y 34491446991; commits `557ca7e`, `f2b3d85`, `81ce14c`, `22af3f1` y `6bc80e8`; valor histórico **2 de 41 ≈ 5 %** del 2026-07-26, probado en `700be94` |
| **C — estado Git/GitHub vivo persistido** | **0** |
| **D — contradicciones documentales** | **0** |

No se cuenta como **C** una frase como «durante el cierre aprobado se creó el PR
`#15`», ni «*Observado el 2026-09-10 UTC:* el usuario lo fusionó»: son hechos
fechados. No se cuenta como **D** un contador histórico probado y correcto para su
fecha, como el **2 de 41** de `Task/002.1`.

## 10. Lo que esta maintenance NO cambia

- `Task/020` sigue **Aprobada**. No se reabre.
- **R-14** sigue **Cerrado**; **S-09 backend** sigue satisfecho; **S-09 global**
  sigue abierto con `Task/021`.
- **R-15**, **R-17** y **R-37** siguen abiertos, sin cambio. **D-020-H** sigue
  anotada como decisión abierta.
- ETAPA 06 sigue en **2/3 — 67 %** y **sin completarse**.
- Avance global sigue en **20/41 — 49 %**. `Task/020.1` **no suma**.
- `Task/021` sigue **Pendiente y no iniciada**.
- Ningún ADR creado, modificado ni promovido.
- Ningún cambio en código, tests, CI, workflows, *locks*, `Dockerfile`, Terraform
  ni configuración de GitHub.

## 11. Pasos de validación para el usuario

```powershell
# 1. Solo se toco documentacion de infra
git -C personal-blog-infra show --stat HEAD                  # solo docs/

# 2. Un solo encabezado vigente de cada familia
Select-String -Path docs/project-management/STATUS.md -Pattern "^## Ultima tarea aprobada" | Measure-Object

# 3. Los contadores siguen intactos
Select-String -Path docs/project-management/ROADMAP.md -Pattern "20 / 41"
Select-String -Path docs/project-management/STATUS.md -Pattern "49 %"

# 4. Backend y frontend intactos
git -C personal-blog-backend status --short
git -C personal-blog-frontend status --short
```

Y en lectura, la evidencia histórica que este reporte afirma:

```powershell
gh pr view 15 --repo jeffersondavila/personal-blog-backend --json state,mergedAt,mergeCommit
gh pr view 36 --repo jeffersondavila/personal-blog-infra   --json state,mergedAt,mergeCommit
gh run view 34491446991 --repo jeffersondavila/personal-blog-backend
```

## 12. Riesgos y deuda

Ninguno nuevo. Esta maintenance no introduce funcionalidad, dependencias ni
decisiones. La deuda estructural que la origina —documentar el cierre antes de
que la fusión ocurra— **no se cierra aquí**: se contiene omitiendo el estado
operativo de esta propia tarea, tal como exige [WORKFLOW
§6.1](../project-management/WORKFLOW.md). Por eso los documentos de `Task/020.1`
no dicen nada del estado de su rama, su PR o su normalización, y su post-merge
debería ser **Git-only**, sin generar una `Task/020.2`.

## 13. Próxima tarea

`Task/021-CI-Infraestructura` sigue **Pendiente y no iniciada**. **No se inicia
aquí.** Debe nacer de `main` actualizado y limpio tras la normalización que exige
[WORKFLOW §2.1 y §6.1](../project-management/WORKFLOW.md).

## 14. Cierre aprobado

**Aprobada el 2026-09-10** por jeffersondavila (usuario), mediante la expresión
exacta `approved: Task/020.1-Corregir-Drift-Documental-Post-Merge`.

Antes de ejecutar nada se comprobó lo que exige el flujo: la rama existe y es la
rama activa; las validaciones de §8 terminaron correctamente; los siete archivos
tocados están **todos** bajo `docs/` de `personal-blog-infra`, sin cambios ajenos
mezclados; y ni `personal-blog-backend` ni `personal-blog-frontend` participan.

Pasos ejecutados en el único repositorio afectado: registro documental de la
aprobación, actualización de STATUS, ficha, reporte e índice, validaciones
finales, commit de los cambios pendientes, integración en `dev` mediante merge
**`--no-ff`**, publicación de `dev` y de la rama Task, creación del pull request
con base `main` y head `Task/020.1-Corregir-Drift-Documental-Post-Merge`, y
borrado de la rama Task **local** con `git branch -d`.

**No hay ADR ni decisión técnica que promover:** esta maintenance no produjo
ninguna. Nada que mover de *Propuesta* a *Vigente*.

Aceptar o rechazar el pull request, y decidir si se elimina la rama remota, es
**responsabilidad exclusiva del usuario**. Este documento registra estado
**duradero**; el estado operativo se consulta en Git y GitHub
([WORKFLOW §6.1](../project-management/WORKFLOW.md)).

**`Task/021` no se inicia en esta tarea.**

## 15. Veredicto

**TASK020.1 APROBADA Y CERRADA.**

Aprobada por el usuario el 2026-09-10. Avance **20/41 — 49 %** y ETAPA 06
**2/3 — 67 %**, **ambos intactos**: esta maintenance **no cuenta** dentro de las
41 tareas. `Task/020` sigue **Aprobada**, **R-14** sigue **Cerrado** y la ETAPA 06
sigue **sin completarse**. Criterion 12 cierra en **C = 0 · D = 0**. **`Task/021`
permanece Pendiente y no iniciada.**
