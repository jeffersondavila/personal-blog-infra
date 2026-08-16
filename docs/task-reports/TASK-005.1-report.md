# Reporte — TASK-005.1 Formalizar TDD en el backend

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.1-Formalizar-TDD-Backend` |
| **Tipo** | Mantenimiento de gobierno documental — **no cuenta** en las 41 tareas del roadmap |
| **Estado final** | **Aprobada** ✔ (2026-08-13) |
| **Fecha** | 2026-08-13 |
| **Repositorios modificados** | `personal-blog-infra` (**únicamente**) |
| **Ficha** | [TASK-005.1](../tasks/TASK-005.1-formalize-backend-tdd.md) |
| **Efecto en el avance** | **Ninguno.** Mantenimiento: avance global **5 de 41**, ETAPA 02 **1 de 3** |

---

## 1. Estado inicial encontrado

Verificado con Git y GitHub, no supuesto.

### 1.1 Merges de `Task/005` confirmados

| Repositorio | PR | Estado | Commit de merge | Fusionado |
| --- | --- | --- | --- | --- |
| `personal-blog-backend` | [#2](https://github.com/jeffersondavila/personal-blog-backend/pull/2) | **MERGED** | `db6ab18c182263207927b83ecb0f2c1b58985802` | 2026-08-13T04:48:04Z |
| `personal-blog-infra` | [#6](https://github.com/jeffersondavila/personal-blog-infra/pull/6) | **MERGED** | `af8a04c909a5fa8b104d7366f2b82cb9c38ba8df` | 2026-08-13T04:47:28Z |

Ambos con base `main` y head `Task/005-Fundacion-Backend-FastAPI`. Las ramas remotas fueron
eliminadas por el usuario: `git fetch --prune` las retiró de la copia local.

### 1.2 Normalización ejecutada (FASE A)

En ambos repositorios el **contenido** de `main` y `dev` ya era idéntico, pero los
**historiales** divergían: `main` tenía el commit de merge del PR y `dev` el suyo propio.

| Repositorio | Acción | Resultado |
| --- | --- | --- |
| `personal-blog-backend` | `git merge --no-ff main` en `dev` y publicación | `dev` = **`ce4f1bc`** · `main` = **`db6ab18`** · `dev..main` **vacío** · `diff main dev` **vacío** · el merge `db6ab18` es ancestro de `dev` |
| `personal-blog-infra` | `git merge --no-ff main` en `dev` y publicación | `dev` = **`5efd5e0`** · `main` = **`af8a04c`** · `dev..main` **vacío** · `diff main dev` **vacío** · el merge `af8a04c` es ancestro de `dev` |
| `personal-blog-frontend` | Solo `fetch --prune` y `pull --ff-only` | Sin cambios. `main` = `144a401` · `dev` = `8823cc3` · árbol limpio |

Las ramas `Task/005` **locales** ya no existían: se eliminaron con `git branch -d` durante el
cierre aprobado. **No se usó `git branch -D` ni `git push --delete` en ningún momento.**

### 1.3 Estado documental posterior a `Task/005`

Confirmado en `STATUS.md`: `Task/005` **Aprobada**, avance global **5 de 41**, ETAPA 02
**1 de 3** aprobadas, `Task/006` y `Task/007` **Pendientes**.

## 2. Rama creada

| Repositorio | Rama | Creada desde | Publicada |
| --- | --- | --- | --- |
| `personal-blog-infra` | `Task/005.1-Formalizar-TDD-Backend` | `dev` = `5efd5e0` (ya normalizada) | **No** |

**No se creó rama en `personal-blog-backend` ni en `personal-blog-frontend`:** la tarea es
documental y su fuente de verdad vive en `infra`. Ningún archivo de esos repositorios
necesitaba cambiar.

## 3. Documentos inspeccionados

`CLAUDE.md`, `PROJECT_INSTRUCTIONS.md`, `WORKFLOW.md`, `STATUS.md`, `ROADMAP.md`,
`DEFINITION_OF_DONE.md`, `TASK_TEMPLATE.md`, `STAGE-02`, `STAGE-03`, la ficha y el reporte de
`Task/005`, y el índice de reportes.

## 4. Qué se construyó

### 4.1 Documento canónico

**`docs/project-management/BACKEND_TESTING_STRATEGY.md`** — fuente **única y completa** de la
práctica, en 16 secciones. Los demás documentos la **referencian**; no la repiten.

### 4.2 La regla

> Todo comportamiento funcional **nuevo** del backend empieza por una prueba que **falla**.
> El ciclo obligatorio es **RED → GREEN → REFACTOR**.

Las pruebas cumplen cinco funciones declaradas: especificación ejecutable, red de regresión,
contrato de comportamiento, **límite para los agentes de programación** y documentación
técnica del dominio.

### 4.3 El ciclo

| Fase | Exigencia |
| --- | --- |
| **ESPECIFICAR** | Criterio de aceptación → comportamiento observable → matriz de casos → invariantes, happy path, edge cases, errores y seguridad → capa de cada caso. |
| **RED** | Test primero; ejecutarlo; que **falle**; que falle **por la razón esperada**. Evidencia obligatoria en el reporte. Un test que ya pasa antes de implementar no demuestra el ciclo y debe investigarse. |
| **GREEN** | Implementación **mínima suficiente**, sin comportamiento futuro no pedido. |
| **REFACTOR** | Diseño, duplicación, nombres y límites arquitectónicos, **sin cambiar el comportamiento observable**. Después, reejecutar lo afectado. Si no hace falta, se declara. |

### 4.4 Protección de los tests

Una implementación incorrecta **no** se resuelve modificando el test. Un test solo puede
cambiar si el requisito cambió, si contradice la documentación vigente, si contiene un error
demostrado o si una decisión documentada redefinió el comportamiento. Ante una contradicción
entre requisito, arquitectura y test: **detenerse y documentarla**.

Prohibido: reducir *asserts* para obtener GREEN, borrar edge cases que fallan, usar `skip`
sin justificación, usar `xfail` para ocultar defectos, mockear hasta que el comportamiento
real deje de probarse, y cambiar los datos esperados para acomodar una implementación
incorrecta. **Aplica por igual a personas y agentes.**

### 4.5 Tipos de prueba

| Tipo | Para qué | Restricción |
| --- | --- | --- |
| **Dominio** | Reglas puras, invariantes, *value objects*, transiciones, validaciones. | Rápidas; sin base de datos, sin FastAPI, sin Docker. |
| **Casos de uso** | Orquestación, repositorios abstractos, permisos funcionales. | Mocks/fakes solo en límites claros. |
| **PostgreSQL real** | SQL, constraints, índices, transacciones, consultas, concurrencia. | **Prohibido sustituirlo por SQLite** para aparentar integración. |
| **HTTP / FastAPI** | Códigos, contrato JSON, errores, paginación, filtros, autenticación, no exposición de borradores. | — |
| **ObjectStorage** | Contrato primero; después MinIO y S3-compatible. | — |
| **Seguridad** | Casos negativos deliberados. | Un endpoint no está probado hasta que se demuestra que **rechaza** al no autorizado. |

Se define además la **pirámide** —muchas pruebas de dominio, pocas E2E— explícitamente
**sin proporciones numéricas**, para no empujar a escribir pruebas que cuadren una
estadística.

### 4.6 Mocks, regresión y cobertura

- **Mocks solo en boundaries.** No mockear los internals de la unidad bajo prueba; preferir
  un *fake* simple cuando exprese mejor el contrato; no acoplar las pruebas a detalles
  privados.
- **No bug fix without regression test.** Reproducir el defecto con una prueba que falla,
  corregir, y dejar esa prueba permanentemente. Excepción solo si es técnicamente imposible,
  documentándolo.
- **«Coverage is a signal, not the specification.»** Todo *branch* significativo de negocio
  nuevo cubierto por un caso explícito; **sin umbral de CI**, que corresponde a `Task/020`.

### 4.7 Property-based testing y estructura

*Hypothesis* queda registrada como incorporación **futura** —slugs, paginación,
normalización, límites, serialización, sanitización, invariantes— **sin añadir la
dependencia ahora** y sin usarla por obligación cuando bastan ejemplos explícitos.

La estructura objetivo `tests/unit|integration|contract` queda definida pero **no se aplica
todavía**: los tests de `Task/005` no se reorganizan por estética.

## 5. Dónde queda registrada la regla

| Documento | Qué se añadió |
| --- | --- |
| `PROJECT_INSTRUCTIONS.md` | Nueva sección **14. BACKEND TEST-FIRST LAW**: versión compacta y accionable, con enlace a la estrategia. Las secciones 15 y 16 se renumeraron. |
| `DEFINITION_OF_DONE.md` | Bloque *Tareas de backend funcional* con los criterios **B-1 a B-12**; exigencia de **cero warnings no documentados**; dos causas nuevas de invalidación: pruebas escritas después de la implementación y tests modificados para acomodar código incorrecto. |
| `TASK_TEMPLATE.md` | Nueva sección **7. TDD / Plan test-first** (comportamientos, matriz, tests RED esperados, integración necesaria, casos negativos y regresiones). Renumeración a 8–20. |
| `ROADMAP.md` | Nota de etapa en ETAPA 03 y política concreta en la fila de cada tarea `008`–`012`. |
| `STAGE-03` | Sección *Práctica obligatoria: test-first*, aplicación por tarea, criterio de salida nuevo y riesgo nuevo. |
| `STATUS.md` | Normalización posterior a `Task/005` y registro de este mantenimiento. |

## 6. Pruebas de consistencia ejecutadas

Las 14 validaciones están en la [ficha](../tasks/TASK-005.1-formalize-backend-tdd.md) §10.
Resumen:

| Comprobación | Resultado |
| --- | --- |
| Términos TDD/test-first en los documentos actualizados | **Presentes** en los 6 documentos |
| Coherencia entre `PROJECT_INSTRUCTIONS`, DoD, `TASK_TEMPLATE`, `ROADMAP` y `STAGE-03` | **Coherentes**, todos apuntan al documento canónico |
| `Task/008`–`Task/012` referencian la estrategia | **Las cinco** |
| Renumeración de tareas | **Ninguna** |
| Total de tareas del roadmap | **41** |
| Avance global | **5 de 41 (12 %)** |
| ETAPA 02 | **1 de 3 aprobadas** |
| Enlaces Markdown relativos | **0 rotos** |
| `git diff --check` | **Sin errores** |
| Secretos | **0** |
| Cambios en backend / frontend | **0 / 0** |
| Archivos Terraform | **0** |
| Floci | **No incorporado**: 0 ADR, 0 versiones concretas, 0 documentos de arquitectura o cloud tocados. Solo aparece el nombre de la futura `Task/005.2` y el handoff de §11 |
| `Task/006` y `Task/005.2` | **No iniciadas** |

## 7. Ausencia de código funcional

Esta tarea **no** ejecuta ni modifica código:

- **0 archivos** modificados en `personal-blog-backend`; su árbol sigue limpio en `main`.
- **0 archivos** modificados en `personal-blog-frontend`.
- **0 dependencias** añadidas o cambiadas.
- **0 recursos cloud**, **0 archivos Terraform**.
- La suite del backend **no se reejecutó**: sus 69 pruebas fueron validadas y aprobadas en
  `Task/005` y nada de lo tocado aquí puede alterarlas.

## 8. Decisiones

Las siete decisiones están en la [ficha](../tasks/TASK-005.1-formalize-backend-tdd.md) §12.
Las tres con más consecuencia:

1. **Un solo documento canónico, todo lo demás lo referencia.** Cinco copias de la misma
   regla divergen en cuanto una cambia.
2. **Sin ADR.** Los ADR del proyecto registran arquitectura del sistema; esto es una norma de
   trabajo, revisable sin tocar la arquitectura.
3. **Sin umbral de cobertura.** La política de CI es de `Task/020`; fijar un número aquí
   crearía una segunda fuente de verdad.

## 9. Problemas encontrados

1. **Renumerar `TASK_TEMPLATE.md` con un reemplazo masivo en PowerShell corrompió el
   archivo**: los reemplazos encadenados colisionaron y la reescritura dañó la codificación
   de todos los acentos. Se restauró ese único archivo desde `HEAD` —su contenido original
   estaba íntegro— y la renumeración se rehízo sección por sección, de la más alta a la más
   baja. Verificado después: numeración 1–20 correcta, **0 secuencias de mojibake**. No se
   perdió trabajo de ninguna otra tarea.
2. **Directorio `images/` sin rastrear en `personal-blog-infra`**, con `Infraestructura.png`
   (2 MB, fechado el 2026-07-26). No lo creó esta tarea. Se informó al usuario, que lo
   confirmó como parte del proyecto y autorizó versionarlo en este cierre. Ver §9.1.

### 9.1 Asset de arquitectura versionado durante el cierre

`images/Infraestructura.png` es un **asset de arquitectura preexistente agregado por el
usuario y autorizado explícitamente para versionarse durante este cierre**. Representa la
arquitectura objetivo inicial: Cloudflare, Cloudflare Pages + React, API Gateway HTTP API,
AWS Lambda + FastAPI, Amazon S3, PostgreSQL administrado, SSM Parameter Store, CloudWatch,
Terraform y GitHub Actions.

**No es un entregable de `Task/005.1`** y no se contabiliza como archivo creado por ella. No
se modificó, ni se regeneró, ni se movió, ni se alteró su contenido: se versionó tal cual.

Es coherente con la arquitectura vigente ([ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md)
y [local-to-cloud-mapping](../architecture/local-to-cloud-mapping.md)). **Versionar un
diagrama no crea ningún recurso cloud ni adelanta ninguna decisión**: las etapas 08 a 10
siguen intactas.

## 10. Límites respetados

Durante la ejecución, **hasta recibir la aprobación**:

| Límite | Cumplimiento |
| --- | --- |
| Sin commits antes de `approved:` | **Cumplido.** Los cambios permanecieron en el árbol de trabajo hasta el 2026-08-13. |
| Sin push | **Cumplido.** La rama `Task/005.1` no existió en `origin` antes del cierre. |
| Sin merge | **Cumplido.** Salvo la normalización `main → dev` de la FASE A, exigida por el workflow y previa a esta tarea. |
| Sin pull request | **Cumplido.** |
| Sin modificar `main` | **Cumplido.** |
| Sin tocar backend ni frontend | **Cumplido.** Ambos limpios en `main`. |
| Sin dependencias nuevas | **Cumplido.** |
| Sin recursos cloud ni Terraform | **Cumplido.** |
| Sin secretos | **Cumplido.** |
| Sin alterar el conteo del roadmap | **Cumplido.** 41 tareas, avance 5 de 41. |
| Sin marcar `Aprobada` por iniciativa propia | **Cumplido.** El estado cambió solo tras `approved: Task/005.1-Formalizar-TDD-Backend`. |
| `Task/006` y `Task/005.2` no iniciadas | **Cumplido.** |

### 10.1 Cierre aprobado (2026-08-13)

Ejecutado tras la autorización explícita del usuario, conforme a
[WORKFLOW.md](../project-management/WORKFLOW.md) §3: commit en la rama Task —incluido el
asset autorizado de §9.1—, integración en `dev` con merge `--no-ff`, publicación de `dev` y de
la rama Task, y pull request `Task/005.1-Formalizar-TDD-Backend → main`.

**El pull request no se fusionó:** aceptarlo es responsabilidad exclusiva del usuario. La
rama Task local se eliminó con `git branch -d`; la remota se conserva mientras el PR siga
abierto.

**El avance no cambia:** al ser mantenimiento, `Task/005.1` no entra en las 41 tareas. Avance
global **5 de 41 (12 %)**, ETAPA 02 **1 de 3**.

## 11. Preparación para Task/005.2

`Task/005.2-Documentar-Estrategia-Floci-IaC-Local` **no se ha iniciado**: no hay rama, ficha,
documento ni mención versionada. Esta sección solo anticipa qué habrá que leer.

**Documentos que esa tarea deberá revisar antes de escribir nada:**

- [`ROADMAP.md`](../project-management/ROADMAP.md) — etapas 08 a 11, donde vive la
  preparación y el despliegue cloud.
- [STAGE-08 — Preparación Cloud sin Cuentas](../stages/STAGE-08-cloud-ready.md).
- [`local-to-cloud-mapping.md`](../architecture/local-to-cloud-mapping.md) — correspondencia
  entre el entorno local y el cloud.
- [`open-decisions.md`](../architecture/open-decisions.md) — decisiones diferidas abiertas.
- [`security-boundaries.md`](../architecture/security-boundaries.md).
- Los **ADR existentes**, en especial [ADR-001](../adr/ADR-001-local-first.md) (local-first) y
  [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md) (serverless de bajo costo).
- Las fichas de etapa relacionadas con Terraform y despliegue cloud.

**Intención futura a documentar** (no decidida todavía): Terraform portable, Floci, paridad
local con AWS y AWS real como validación final.

**En esta tarea no se creó ningún ADR, no se nombró ninguna versión concreta de Floci y no se
modificó ninguno de esos documentos.**

---

## 12. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** ✔ |
| **Fecha de aprobación** | 2026-08-13 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.1-Formalizar-TDD-Backend` |
| **Pull request** | `Task/005.1-Formalizar-TDD-Backend → main` en `personal-blog-infra` — **abierto, sin fusionar** |
| **Efecto en el avance** | **Ninguno.** Mantenimiento: 5 de 41 y ETAPA 02 1 de 3, sin cambios |

La fusión hacia `main` es responsabilidad exclusiva del usuario.
