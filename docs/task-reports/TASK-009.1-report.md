# TASK-009.1 — Corregir el drift documental posterior a la fusión de `Task/009` · Reporte

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/009.1-Corregir-Drift-Documental-Post-Merge` |
| **Tipo** | **Mantenimiento de gobierno documental** — **no cuenta** en las 41 tareas |
| **Estado** | **Aprobada** — 2026-08-27 |
| **Fecha** | 2026-08-27 |
| **Repositorios modificados** | `personal-blog-infra` (**únicamente**) |
| **Ficha** | [TASK-009.1](../tasks/TASK-009.1-correct-post-merge-documentation-drift.md) |

> **0 funcionalidad.** Ni una línea de código, prueba, Compose, Terraform o ADR. El contrato
> HTTP, el modelo físico y las decisiones **D-009-A** a **D-009-R** quedan intactos. El
> avance sigue en **9 de 41 (22 %)** y la ETAPA 03 en **2 de 5 (40 %)**.

---

## 1. Estado inicial

Reconstruido en vivo desde Git, no leído de un documento
([WORKFLOW §6.1](../project-management/WORKFLOW.md) punto 3).

| Repositorio | Rama | `main` | `main == origin/main` | Árbol | Ramas Task |
| --- | --- | --- | :---: | :---: | :---: |
| `personal-blog-infra` | `main` | `e034e7591d113b658c3a29d853f55a07912cd7b8` | ✔ | limpio | 0 local · 0 remota |
| `personal-blog-backend` | `main` | `81347758dcc01eda55938a3bf0a298684c6c8a08` | ✔ | limpio | 0 local · 0 remota |
| `personal-blog-frontend` | `main` | `fd62f221707591a984cf0fb51a03ea339380ab35` | ✔ | limpio | 0 local · 0 remota |

Invariantes de integración en infra y backend: `main` ancestro de `dev`,
`git rev-list --count dev..main` = `0`, `git diff main dev` vacío.

## 2. Rama

| Campo | Valor |
| --- | --- |
| Nombre | `Task/009.1-Corregir-Drift-Documental-Post-Merge` |
| Repositorio | `personal-blog-infra` (**únicamente**) |
| Base | **`main`** |
| SHA base | `e034e7591d113b658c3a29d853f55a07912cd7b8` |
| `HEAD == main` al crearla | **SÍ**, idénticos |
| `git rev-list --count main..HEAD` | **0** |
| ¿Nació de `dev`? | **NO** |

`personal-blog-backend` y `personal-blog-frontend`: **sin rama**, solo lectura.

## 3. Origen del drift

El cierre de `Task/009` se redactó **antes** de que el usuario fusionara los pull request y
antes de la normalización `main → dev`. En ese instante el PR estaba abierto, y así se
escribió. Ese texto viajó **dentro del propio PR** hacia `main`; al fusionarlo, el documento
ya versionado siguió afirmando un trámite que ya había ocurrido.

Es el defecto estructural que describe [WORKFLOW §6.1](../project-management/WORKFLOW.md),
vigente desde `Task/005.6`, y el mismo patrón que `Task/006.1` corrigió tras `Task/006`.
**La regla no falló: falló su aplicación al redactar el cierre.** Es la segunda reincidencia.

## 4. Los seis hallazgos, y uno más

Clasificación según §6.1: **A** historia fechada · **B** regla permanente · **C** estado
vivo o precondición transitoria (**drift**).

| # | Archivo | Texto anterior | Clase | Motivo |
| --- | --- | --- | :---: | --- |
| 1 | `STATUS.md` *Vista rápida · Tarea actual* | «su pull request `Task/009-API-Publica → main` está **abierto y pendiente de que lo fusione el usuario**» | **C** | §6.1 «Cómo se aplica» punto 1 lo prohíbe literalmente: `STATUS.md` no afirma el estado vivo de un PR. Ya era **falso**: el PR está `MERGED` |
| 2 | `STATUS.md` *Vista rápida · Estado de la tarea* | «`Task/010` **no se inicia** hasta que el usuario fusione el PR y se complete la normalización `main → dev`» | **C** | §6.1 punto 4: condiciona el inicio de la tarea siguiente a hechos transitorios ya consumados |
| 3 | `STATUS.md` *Vista rápida · Próxima tarea prevista* | «No se inicia hasta que el usuario fusione el pull request de `Task/009` y se complete la normalización `main → dev`» | **C** | Igual que #2. **La segunda mitad de la celda era correcta** —regla permanente sobre verificar Git en vivo y nacer de `main`— y **se conserva** |
| 4 | `TASK-009-report.md` §I.5 | «El laboratorio se conserva íntegro […] **hasta que** `Task/009` sea aprobada, fusionada y normalizada» | **C** *(menor)* | Condición viva sobre estado de Git ya consumado. Los tres hechos ocurrieron, así que la frase quedó obsoleta |
| 5 | `TASK-009-report.md` §Z | «**no se inicia** hasta que el usuario fusione el pull request de `Task/009` y se complete la normalización `main → dev`» | **C** | §6.1 punto 4 |
| 6 | `TASK-009-public-api.md` §13 | «**No se inicia** hasta que `Task/009` esté aprobada **y normalizada**» | **C** *(mixta)* | «aprobada» es **durable y válido**; «normalizada» es transitorio y sobra |
| **7** | `STATUS.md` *Tabla completa de tareas* | `Task/009-API-Publica` … **Lista para validación** | — | **No es drift de §6.1: es estado durable obsoleto.** Contradecía la vista rápida del mismo documento, que ya decía `Aprobada`. Detectado en este barrido y corregido aquí |

El hallazgo 7 **no estaba en la auditoría original**. Apareció al barrer el documento
completo en lugar de solo las tres celdas conocidas.

## 5. Redacción corregida

| # | Archivo | Redacción final | Por qué ahora es durable |
| --- | --- | --- | --- |
| 1 | `STATUS.md` *Tarea actual* | «`Task/010-Almacenamiento-Compatible-S3` — **Pendiente, no iniciada**» | Registra un **estado de tarea**, que §6.1 clasifica como duradero. No menciona ningún PR. *(Durante la ejecución esta celda registró `Task/009.1` como mantenimiento en validación, según [WORKFLOW §6](../project-management/WORKFLOW.md); al aprobarse pasó a la fila de mantenimientos.)* |
| 2 | `STATUS.md` *Estado de la tarea* | «**Pendiente, no iniciada.** La ETAPA 03 sigue **En curso**: `Task/010`, `Task/011` y `Task/012` quedan por aprobar» | Describe el estado de las tareas, que §6.1 clasifica como duradero. Ninguna referencia a PR, rama remota ni normalización |
| 3 | `STATUS.md` *Próxima tarea prevista* | «`Task/010-…` — **Pendiente, no iniciada**. Depende de `Task/008-Modelo-de-Datos` (**Aprobada**), según el ROADMAP. Al iniciarse, el estado real de Git se verifica **en vivo** y su rama nace desde `main` actualizado y limpio» | La dependencia sale de su **fuente canónica**; la condición se expresa como **regla permanente**, que es exactamente la forma que §6.1 punto 4 prescribe |
| 4 | `TASK-009-report.md` §I.5 | «El laboratorio […] se preserva como respaldo de esta remediación. **Su eliminación requiere una decisión operativa explícita del usuario** y no forma parte de las dependencias de ninguna tarea siguiente» | Describe una política estable, no un trámite. El paso del tiempo no la vuelve falsa |
| 5 | `TASK-009-report.md` §Z | «Permanece **Pendiente y no iniciada**; su dependencia es la que fija el ROADMAP. Cuando se inicie, el estado real de Git se verifica **en vivo** y su rama **nace desde `main`** actualizado y limpio» | Igual que #3 |
| 6 | `TASK-009-public-api.md` §13 | «Permanece **Pendiente y no iniciada**; su dependencia es la que fija el ROADMAP. Cuando se inicie, el estado real de Git se verifica **en vivo** y su rama **nace desde `main`** actualizado y limpio» | Se elimina «normalizada»; se conserva la dependencia real y se alinea con el owner canónico |
| 7 | `STATUS.md` *Tabla completa* | `Task/009-API-Publica` … **Aprobada** | Refleja el estado durable real y elimina la contradicción interna del documento |

## 6. Corrección del reporte de `Task/009` — por qué aquí sí

`Task/006.1` excluyó deliberadamente el reporte de `Task/006`, con el argumento de que un
reporte es una **instantánea cerrada**. Aquí se tocan dos frases del reporte de `Task/009`,
y la diferencia es de naturaleza:

- Lo que aquel criterio protegía —**la observación de lo que se sabía al cerrar**— queda
  intacto. §Y conserva literalmente su bloque *«Observado el 2026-08-27, antes de la
  aprobación: `git rev-list --count main..HEAD` = 0, staging vacío…»*.
- Las dos frases corregidas **no describen el pasado**: son **condiciones hacia el futuro**
  —«se conserva **hasta que**…», «**no se inicia hasta que**…»—. §6.1 punto 4 prohíbe esa
  forma en **cualquier** documento.

Una instantánea cerrada describe; no condiciona el futuro. Solo se corrigió lo segundo.

## 7. Historia preservada

**No se tocó ni una palabra** de:

- **§I.2** — la desviación de la BACKEND TEST-FIRST LAW en seis *slices*, tal como se
  escribió, incluido «Qué se perdió, y no se recupera» y su nota de actualización.
- **§I.3** — el *mutation testing* como evidencia complementaria.
- **§I.5** salvo el párrafo del laboratorio — la remediación completa, la tabla RED/GREEN por
  *slice*, la transparencia sobre BookReviews y la comparación con la implementación
  preservada.
- **§I.6** — causa raíz y guarda para tareas siguientes.
- **§P**, **§X** — resultados de las validaciones y el criterio 29 con sus dos momentos.
- **§U** y **§Y** — la observación fechada del estado Git pre-approval.
- Las secciones de `Task/001` a `Task/008` en `STATUS.md`.
- Las decisiones **D-009-A** a **D-009-R**, que siguen **Vigentes**.

## 8. Barrido §6.1 final

Se barrieron los **8** documentos que `Task/009` modificó, no solo los tres con hallazgos.

| Documento | A — historia | B — regla | C — drift |
| --- | :---: | :---: | :---: |
| `docs/project-management/STATUS.md` | muchas | 3 | **0** |
| `docs/project-management/ROADMAP.md` | — | — | **0** |
| `docs/stages/STAGE-03-domain-and-backend.md` | 1 | — | **0** |
| `docs/task-reports/TASK-009-report.md` | 6 | 2 | **0** |
| `docs/tasks/TASK-009-public-api.md` | 2 | 1 | **0** |
| `docs/task-reports/README.md` | 1 | — | **0** |
| `docs/architecture/api-contracts.md` | — | — | **0** |
| `docs/architecture/data-model.md` | — | — | **0** |
| **Total C** | | | **0** ✔ |

### Falsos positivos revisados y descartados

| Aparición | Por qué no es drift |
| --- | --- |
| `api-contracts.md` §11, `data-model.md` §10, `ROADMAP.md` D-16 — «Abierto» | Son **decisiones pendientes** con dueño futuro, no estado de Git |
| `data-model.md` — «normalización de *slug*» | Otro sentido de la palabra: pertenece a `Task/012` |
| `STATUS.md:13` — «Esperando `approved: …-Post-Merge`» | Coincidió con el patrón por el **nombre de la rama**, no por semántica. El estado de tarea y su expresión de aprobación son duraderos |
| `TASK-009-report.md` §U, §Y, criterio 39 — «sin PR», «PR fusionado es del usuario» | Observación **fechada** y **regla permanente**. §6.1 punto 2 las declara válidas |
| `STATUS.md` *Estado de los repositorios* | Encabezada por su propia advertencia: «*Lo de abajo es una observación fechada, no una afirmación permanente*» |

### Una aparición fuera de alcance, reportada y no corregida

`STATUS.md:1149`, en *Notas de estado*: «`Task/005.4` y `Task/005.5` están aprobadas,
fusionadas y normalizadas».

Es una narración histórica sobre tareas cerradas hace semanas, **anterior a `Task/009`** y
no introducida por su cierre. No es falsa —esas fusiones ocurrieron— y la ficha excluye
explícitamente las secciones históricas de `Task/001`–`Task/008`. Se **reporta** en lugar de
editarse, para no reescribir historia ajena al alcance. Si se quisiera endurecer, bastaría
con fecharla; no es urgente ni es drift de este cierre.

## 9. Prevención de recurrencia

**Se añadió el criterio 12 a la [Definition of Done](../project-management/DEFINITION_OF_DONE.md) §1.**

La justificación es que el hueco era real: el criterio 5 exige que «la documentación esté
actualizada», pero **ningún** criterio obligaba a comprobar que además no persistiera estado
transitorio. Existía un checklist de cierre natural, y le faltaba esa fila.

El criterio nuevo **comprueba el hecho y apunta a la regla**, exactamente como el criterio
11 hace con WORKFLOW §2.1. No reescribe §6.1.

> **12 — La documentación no persiste estado transitorio de Git o GitHub.** *Búsqueda
> dirigida en los documentos tocados: toda mención a un PR, una rama remota o una
> normalización es historia fechada o regla permanente, nunca estado vigente ni condición de
> la tarea siguiente.*

**Lo que deliberadamente no se hizo:** no se tocó `TASK_TEMPLATE.md` —sería una tercera
copia de la misma regla, prohibida por
[WORKFLOW §7](../project-management/WORKFLOW.md)— y no se creó *linter*, *hook*, script ni
paso de CI, que sería *scope creep* de una tarea documental.

**Si el defecto reaparece tras `Task/010` pese al criterio 12**, la conclusión ya no será que
falta documentación, sino que hace falta una comprobación **ejecutable**. Eso merecerá su
propia tarea, con su alcance y su decisión.

## 10. Archivos

### `personal-blog-infra`

| Archivo | Cambio |
| --- | --- |
| `docs/project-management/STATUS.md` | 3 correcciones **C**, 1 estado durable obsoleto, y sección *Mantenimiento en validación — `Task/009.1`* |
| `docs/task-reports/TASK-009-report.md` | 2 correcciones **C** (§I.5 y §Z) |
| `docs/tasks/TASK-009-public-api.md` | 1 corrección **C** (§13) |
| `docs/project-management/DEFINITION_OF_DONE.md` | Criterio 12 y su nota al pie |
| `docs/tasks/TASK-009.1-correct-post-merge-documentation-drift.md` | **Creado** |
| `docs/task-reports/TASK-009.1-report.md` | **Creado** — este archivo |
| `docs/task-reports/README.md` | Índice |

**No se modifican:** `ROADMAP.md`, `STAGE-03-domain-and-backend.md`, `api-contracts.md`,
`data-model.md`, ningún ADR. **Ningún archivo eliminado.**

### `personal-blog-backend` y `personal-blog-frontend`

**Sin rama, sin cambios, sin tocar.** `git status` vacío en `main` en ambos.

## 11. Validaciones

| Comprobación | Resultado |
| --- | --- |
| `git diff --check` | limpio |
| Barrido §6.1 sobre los 8 documentos | **C = 0** |
| Enlaces relativos nuevos resuelven | ✔ |
| Identificadores del roadmap | **41**, intactos |
| Tareas aprobadas | **9** |
| Avance global | **9 / 41 — 22 %** |
| ETAPA 03 | **2 / 5 — 40 %** |
| `Task/010` | **Pendiente** |
| `Task/009.1` dentro de las 41 filas | **NO** — registrado aparte |
| Secretos | 0 hallazgos |

**Criterios de la Definition of Done que no aplican:** el 3 y el 4 (compilación y pruebas),
por tratarse de una tarea exclusivamente documental
([BACKEND_TESTING_STRATEGY](../project-management/BACKEND_TESTING_STRATEGY.md) §4).

## 12. Pasos de validación para el usuario

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

# 1. La rama nacio de main y no hay nada publicado
git log --oneline -1 main
git rev-list --count main..HEAD    # 0 antes del commit de cierre
git status --short

# 2. C = 0 en los ocho documentos que Task/009 modifico
Select-String -Path docs/project-management/STATUS.md, `
  docs/project-management/ROADMAP.md, `
  docs/stages/STAGE-03-domain-and-backend.md, `
  docs/task-reports/TASK-009-report.md, `
  docs/task-reports/README.md, `
  docs/tasks/TASK-009-public-api.md, `
  docs/architecture/api-contracts.md, `
  docs/architecture/data-model.md `
  -Pattern 'no se inicia hasta|hasta que el usuario fusione|abierto y pendiente|pendiente de fusionar|y normalizada'

# 3. La historia de Task/009 sigue intacta
Select-String -Path docs/task-reports/TASK-009-report.md `
  -Pattern 'La desviación, sin adornos|Remediación TDD|Causa raíz|Observado el 2026-08-27'

# 4. Contadores intactos
Select-String -Path docs/project-management/ROADMAP.md -Pattern '9 de 41|9 / 41'

# 5. Backend y frontend intactos
git -C ..\personal-blog-backend status --short
git -C ..\personal-blog-frontend status --short
```

## 13. Riesgos y deuda

| # | Riesgo | Estado |
| --- | --- | --- |
| 1 | El drift se repita en el cierre de `Task/010` | Mitigado con el criterio 12 de la Definition of Done. **Segunda reincidencia**: si hay una tercera, la mitigación deja de ser documental |
| 2 | Confundir historia válida con drift | Mitigado: clasificación A/B/C explícita antes de editar; los falsos positivos quedan documentados en §8 |

**Riesgos nuevos: ninguno.** Ningún riesgo existente se agrava. **Deuda nueva: ninguna.**

## 14. Gobierno

**Estado duradero** ([WORKFLOW §6.1](../project-management/WORKFLOW.md)):

| Campo | Valor |
| --- | --- |
| `Task/009.1` | **Aprobada** el 2026-08-27 |
| Expresión de aprobación | `approved: Task/009.1-Corregir-Drift-Documental-Post-Merge` |
| Cuenta en las 41 | **NO** |
| `Task/009` | **Aprobada** el 2026-08-27 |
| Avance global | **9 / 41 — 22 %** — sin cambios |
| ETAPA 03 | **2 / 5 — 40 %** — sin cambios |
| `Task/010` | **Pendiente, no iniciada** |

> *Observado el 2026-08-27, **antes** de la aprobación:* en `personal-blog-infra`,
> `git rev-list --count main..HEAD` = **0**, staging **vacío** y ninguna rama `Task/009.1`
> en `origin`. En `personal-blog-backend` y `personal-blog-frontend`, `main` limpio y sin
> rama. Es la evidencia de que el trabajo permaneció sin confirmar hasta la aprobación.
>
> El trámite de cierre —commit, integración en `dev`, publicación y pull request— es estado
> **transitorio** y **no se registra aquí**: se consulta en Git y GitHub. **Aceptar y
> fusionar el pull request es responsabilidad exclusiva del usuario.**

## 15. Próxima tarea

`Task/010-Almacenamiento-Compatible-S3` — interfaz `ObjectStorage`, `MinIOStorage` y el
código de `S3Storage`, con pruebas de contrato comunes y sin AWS real. Permanece
**Pendiente y no iniciada**; su dependencia es la que fija el
[ROADMAP](../project-management/ROADMAP.md).

Cuando se inicie, el estado real de Git se verifica **en vivo** y su rama **nace desde
`main`** actualizado y limpio, como toda rama Task
([WORKFLOW §2.1 y §6.1](../project-management/WORKFLOW.md)).
