# Reporte — TASK-020.2 · Corregir la autodescripción obsoleta de Task020.1

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/020.2-Corregir-Autodescripcion-Obsoleta-de-Task020.1` |
| **Estado** | **Aprobada** ✔ el 2026-09-10 por el usuario |
| **Expresión de aprobación** | `approved: Task/020.2-Corregir-Autodescripcion-Obsoleta-de-Task020.1` |
| **Tipo / repositorio** | Mantenimiento documental; `personal-blog-infra` únicamente |
| **Cuenta en el roadmap** | No: avance **20/41 — 49 %** y ETAPA 06 **2/3 — 67 %** |
| **Ficha** | [TASK-020.2](../tasks/TASK-020.2-correct-stale-self-description.md) |

## A. Preflight

Durante el preflight del 2026-09-10 se actualizó `main` con `fetch --prune`
y `pull --ff-only`. Se verificaron igualdad con `origin/main`, limpieza,
staging vacío y ausencia local/remota de la rama exacta y de PR previo con
ese head. La rama se creó desde el SHA base registrado en la ficha y se
comprobó inmediatamente la igualdad con `main`, sin commits adicionales.

Incidencia del verificador: `@(ConvertFrom-Json ...)` contó el array JSON
vacío `[]` como un elemento en PowerShell. La guarda detuvo la creación;
se inspeccionó la respuesta, se contó el array deserializado directamente y
se repitieron las precondiciones con resultado correcto antes de crearla.
No era un PR existente ni una contradicción documental del proyecto.

## B. Reproducción exacta del D

Observado el 2026-09-10, antes de editar, en §7 «Archivos», tabla «Modificados»
de [TASK-020.1-report.md](TASK-020.1-report.md), celda de STATUS:

> `Task/020.1` registrada como mantenimiento en curso

Era una descripción final sin ancla temporal. En ese momento, STATUS ya
registraba **Aprobada** y «Último mantenimiento aprobado — `Task/020.1`»;
«Mantenimiento en curso» aparecía **0 veces** en STATUS.
Clasificación inicial del residual: **D = 1**, **C = 0**.

## C. Causa

Al aprobar `Task/020.1` se promovió su registro en STATUS, pero la tabla del
reporte conservó únicamente la descripción de la fase anterior. La omisión
era semántica: no dependía de la existencia de ramas ni del estado de un PR.

## D. Corrección

La celda conserva el registro inicial e incorpora el resultado del cierre:

> `Task/020.1` registrada primero como mantenimiento en curso durante la fase pre-aprobación y promovida a último mantenimiento aprobado durante el cierre

El resto de la fila se conserva. La frase relata una transición documental
histórica y no afirma un estado operativo de Git/GitHub.

## E. Archivos tocados

Todas las rutas son relativas a `personal-blog-infra`.

| Archivo | Acción y propósito |
| --- | --- |
| `docs/task-reports/TASK-020.1-report.md` | Modificado: una celda, único cambio sustantivo |
| `docs/tasks/TASK-020.2-correct-stale-self-description.md` | Creado: ficha, alcance y regla de aprobación durante la fase pre-aprobación; promovido a **Aprobada** durante el cierre |
| `docs/task-reports/TASK-020.2-report.md` | Creado: reproducción, corrección y validación durante la fase pre-aprobación; promovido a **Aprobada** durante el cierre |
| `docs/task-reports/README.md` | Modificado: registro de `Task/020.2` y sufijo en la nota de mantenimientos durante la fase pre-aprobación; estado promovido a **Aprobada (2026-09-10)** durante el cierre |
| `docs/project-management/STATUS.md` | Modificado: `Task/020.2` registrada primero como mantenimiento en fase pre-aprobación y promovida a **último mantenimiento aprobado** durante el cierre, con `Task/020.1` degradada a mantenimiento aprobado anterior; contadores canónicos sin cambios |

Ficha, reporte y STATUS responden a [WORKFLOW §2 y §6](../project-management/WORKFLOW.md);
el índice sigue su convención existente de mantenimientos. ROADMAP y STAGE-06
no requieren actualización: no cambia el estado ni el avance de la etapa.

## F. Coincidencia entre STATUS y reporte

En la validación pre-aprobación del 2026-09-10, STATUS registraba `Task/020.1`
como **Aprobada** y «Último mantenimiento aprobado». La celda corregida
describe su promoción a esa categoría durante el cierre de `Task/020.1`,
preservando la fase pre-aprobación.
La frase original solo se conserva aquí como reproducción histórica del defecto.

## G. Criterion 12

Barrido realizado durante la validación pre-aprobación del 2026-09-10 sobre
los cinco documentos de E; contadores contrastados con ROADMAP y STAGE-06
en lectura. Resultado: **C = 0 · D = 0**. No se detectó otra contradicción
independiente en ese barrido.

| Clase / coincidencia | Clasificación final |
| --- | --- |
| **A — reglas permanentes** | Flujo de aprobación, consulta operativa en Git/GitHub y reglas generales del índice y del recuento canónico |
| **B — hechos históricos** | Preflight fechado, reproducción del defecto y transición de `Task/020.1` entre sus dos fases |
| **C — estado Git/GitHub vivo persistido** | **0** |
| **D — contradicciones documentales** | **0**; la autodescripción coincide con STATUS |
| «Lista para validación» | En `Task/020.2`, siempre anclada a la fase pre-aprobación del 2026-09-10, ya superada: el estado vigente es **Aprobada**. Las demás apariciones son reglas generales, categorías del recuento canónico o historia de revisiones anteriores |
| «En curso» | En la celda corregida, fase pre-aprobación; en B, cita histórica del defecto; en STATUS, registros históricos del avance tras tareas anteriores |
| «sin PR» / «sin push» | En el reporte de `Task/020.1`, reproducción del estado pre-aprobación y observación fechada de §8; en el índice, regla general de contenido |

La frase original tiene **0 apariciones** en el reporte corregido de
`Task/020.1`; se conserva una sola vez en B como evidencia histórica fechada.

## H. Validación documental

Resultados de la validación pre-aprobación del 2026-09-10:

| Comprobación | Resultado |
| --- | --- |
| `git diff --check` | Exit **0**, sin errores |
| Referencias Markdown relativas, excluidos bloques de código | **215 comprobadas, 0 rotas**, con destino y fragmento cuando corresponde |
| Secretos en los cinco documentos completos | **0 coincidencias**: claves privadas, claves AWS, tokens de servicios, JWT, asignaciones sensibles y credenciales en URL |
| Espacios finales, marcadores de conflicto y líneas vacías extra al final, incluidos los dos archivos nuevos | **0** |
| Corrección sustantiva contra la versión base | Sustitución exacta de una frase en una celda; resto de `TASK-020.1-report.md` idéntico |
| Alcance | **5 documentos** de infra: **3 modificados y 2 creados** |
| Encabezados de STATUS | **1** «Última tarea aprobada» y **1** «Último mantenimiento aprobado» |
| Tabla canónica de STATUS | **41 filas**, **20 Aprobadas**, **21 Pendientes**, sin maintenance |

El primer intento de imprimir el barrido dirigido encontró un error de
codificación de consola (`cp1252`, carácter de flecha). Se repitió con salida
UTF-8 y terminó correctamente; no requirió cambiar documentación heredada.

Compilación, pruebas funcionales y TDD no aplican: solo documentación Markdown.

Pasos reproducibles desde la raíz de `personal-blog-infra`:

```powershell
git diff --check
git diff -- docs/task-reports/TASK-020.1-report.md
git status --short
git diff --cached --name-only
git rev-list --count main..HEAD
Select-String -LiteralPath docs/project-management/STATUS.md -Pattern '^## Último mantenimiento aprobado','20/41','2/3'
```

Leer los cinco documentos, resolver sus enlaces relativos y contrastar las
menciones a estados con su contexto temporal o regla general. Leer también
los dos archivos nuevos, que no aparecen en `git diff` hasta ser añadidos.

## I. Límites Git y cierre

Durante la implementación pre-aprobación del 2026-09-10 no se ejecutaron
commit, push, merge a `dev` ni creación de PR. El preflight no necesitó
bootstrap remoto. Las comprobaciones operativas se consultan en Git/GitHub.

Regla para el cierre: tras recibir exactamente
`approved: Task/020.2-Corregir-Autodescripcion-Obsoleta-de-Task020.1`, promover
ficha, reporte, STATUS e índice a **Aprobada** antes del commit. Revisar las
descripciones contra el cambio completo y conservar únicamente hechos
durables. La normalización posterior a la fusión debe ser **Git-only**.

### Cierre aprobado — 2026-09-10

El usuario escribió la expresión exacta de aprobación. Antes del commit se
promovieron a **Aprobada** la ficha, este reporte, el registro de STATUS y el
índice de reportes; `Task/020.1` quedó degradada a mantenimiento aprobado
anterior, de modo que STATUS conserva **un solo** encabezado «Último
mantenimiento aprobado», ahora el de `Task/020.2`. Las descripciones de E se
revisaron contra el cambio completo —incluida la autodescripción de esta misma
tarea, que es el defecto que corrige— y las frases de la fase pre-aprobación
quedaron ancladas a su fecha.

Validación repetida sobre los cinco documentos ya promovidos, el 2026-09-10:

| Comprobación | Resultado |
| --- | --- |
| `git diff --check` | Exit **0**, sin errores |
| Referencias Markdown relativas, excluidos bloques de código | **216 comprobadas, 0 rotas**; una más que en la fase pre-aprobación, por el enlace a WORKFLOW §6.1 añadido al promover |
| Secretos en los cinco documentos completos | **0 coincidencias** |
| Espacios finales y marcadores de conflicto | **0** |
| Encabezados de STATUS | **1** «Última tarea aprobada» y **1** «Último mantenimiento aprobado» |
| Etiquetas de fila de la Vista rápida | **30 filas**, **0 duplicadas** |
| Tabla canónica de STATUS | **41 filas**, **20 Aprobadas**, **21 Pendientes**, sin maintenance |

El cierre siguió el flujo obligatorio: commit, integración en `dev` con merge
`--no-ff`, publicación de `dev` y de la rama Task, y pull request
`Task/020.2-… → main`, que **solo el usuario** fusiona. Conforme a
[WORKFLOW §6.1](../project-management/WORKFLOW.md), el estado vivo de ese PR, de
las ramas remotas y de la sincronía `main`/`dev` **no se persiste aquí**: se
consulta en Git y GitHub.

## J. Contadores, riesgos y alcance

Avance **20/41 ≈ 49 %**; ETAPA 06 **2/3 ≈ 67 %**. `Task/020` y `Task/020.1`
**Aprobadas**; `Task/020.2` es maintenance y **no suma**. `Task/021` permanece
**Pendiente y no iniciada**. No se introducen riesgos, deuda ni decisiones
arquitectónicas. No se modifican backend, frontend, Docker, CI, Terraform,
ADR, ROADMAP, STAGE-06, ficha ni reporte de `Task/020`.

## K. Veredicto

La entrega de la fase pre-aprobación del 2026-09-10 quedó
**TASK020.2 IMPLEMENTADA — LISTA PARA VALIDACIÓN**. El usuario la aprobó ese
mismo día mediante la expresión exacta.

Estado vigente: **TASK020.2 APROBADA Y CERRADA** el 2026-09-10.
`Task/021-CI-Infraestructura` sigue **Pendiente y no iniciada**.
