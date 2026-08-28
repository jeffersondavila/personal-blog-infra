# STATUS — Estado del proyecto Blog Personal

**Última actualización:** 2026-08-27

---

## Vista rápida

| Campo | Valor |
| --- | --- |
| **Etapa actual** | ETAPA 03 — Dominio y Backend — **En curso** (2 de 5). ETAPAS 00, 01 y **02 completadas** |
| **Tarea actual** | `Task/010-Almacenamiento-Compatible-S3` — **Pendiente, no iniciada**. `Task/009` quedó **Aprobada** el 2026-08-27; su pull request `Task/009-API-Publica → main` está **abierto y pendiente de que lo fusione el usuario** |
| **Estado de la tarea** | `Task/009` **Aprobada**. `Task/010` **no se inicia** hasta que el usuario fusione el PR y se complete la normalización `main → dev` |
| **Última tarea aprobada** | `Task/009-API-Publica` — **Aprobada** el 2026-08-27 por jeffersondavila. Los **diez** endpoints públicos del contrato, sobre la implementación **reconstruida test-first** |
| **Tarea aprobada anterior** | `Task/008-Modelo-de-Datos` — **Aprobada** el 2026-08-25. **Primera tarea de la ETAPA 03** y primera sujeta a la **BACKEND TEST-FIRST LAW**: modelo físico completo del MVP en 14 tablas, con migración reversible |
| **Tarea aprobada previa** | `Task/007-Integracion-Local` — **Aprobada** el 2026-08-23. **Completó la ETAPA 02**: frontend, backend, PostgreSQL, MinIO, Traefik v3 y Portainer integrados en un único entorno local |
| **Último mantenimiento aprobado** | `Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` — **Aprobada** el 2026-08-23. Formaliza la arquitectura objetivo de producción y acepta **ADR-008**. No cuenta en las 41 tareas |
| **Mantenimiento anterior** | `Task/006.1-Corregir-Drift-Documental-Post-Merge` — **Aprobada** el 2026-08-21. Cierra el drift documental posterior a la fusión de `Task/006`. No cuenta en las 41 tareas |
| **Mantenimiento previo** | `Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion` — **Aprobada** el 2026-08-16. Hermeticidad del harness y *fail-closed* real de la integración. No cuenta en las 41 tareas |
| **Próxima tarea prevista** | `Task/010-Almacenamiento-Compatible-S3` — **Pendiente, no iniciada**. No se inicia hasta que el usuario fusione el pull request de `Task/009` y se complete la normalización `main → dev`. Al iniciarse, el estado real de Git se verifica **en vivo** y su rama nace desde `main` actualizado y limpio ([WORKFLOW §2.1 y §6.1](WORKFLOW.md)) |
| **Avance global** | **22 %** — 9 de 41 tareas aprobadas |
| **Bloqueos activos** | 0 |
| **Riesgos abiertos** | **40** (R-01 y **R-08** cerrados; **R-29** a **R-35** abiertos desde el 2026-08-15; **R-36** añadido en `Task/005.6`; **R-37** en `Task/005.7`; **R-38** a **R-42** **abiertos** desde el 2026-08-23, `Task/006.2`) |
| **Decisiones abiertas** | **17** — D-05, D-14 y D-01 resueltas; **D-15** y **D-16** añadidas en `Task/005.5`; **D-17** a **D-20** en `Task/006.2` (2026-08-23) |

> El avance se calcula **solo** con tareas `Aprobada`. **`Task/009` ya cuenta**: fue
> aprobada por el usuario el 2026-08-27, lo que lleva el avance a **9 de 41** y la ETAPA 03
> a **2 de 5**. Lo que fija el recuento es **la aprobación del usuario**, no el trámite
> posterior de fusionar el pull request ([WORKFLOW §6.1](WORKFLOW.md)).

---

## Última tarea aprobada — `Task/009-API-Publica`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/009-API-Publica` |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las 41 |
| **Estado** | **Aprobada** el 2026-08-27 |
| **Fecha de inicio** | 2026-08-26 |
| **Expresión de aprobación** | `approved: Task/009-API-Publica` |
| **Depende de** | `Task/008-Modelo-de-Datos` (**Aprobada**) |
| **Repositorios modificados** | `personal-blog-backend` · `personal-blog-infra` (gobierno y documentación) |
| **Repositorio no modificado** | `personal-blog-frontend` — **sin rama y sin cambios** |
| **Ramas base** | **`main`** en ambos: `0ada6a73…` (backend) y `71f56da2…` (infra). `HEAD == main` verificado inmediatamente tras crearlas |
| **Alcance entregado** | Los **diez** endpoints públicos del contrato: perfil, artículos, reviews, videos, proyectos, etiquetas y búsqueda. Paginación compartida, filtros `tag`/`featured`/`sort` con lista cerrada, orden determinista y búsqueda básica sobre contenido publicado |
| **Test-first** | **Cumplido para la implementación aprobada.** En la primera ejecución seis *slices* tuvieron sus pruebas escritas **después** del código; la desviación se detectó **pre-approval**, la tarea **no** se aprobó, y esos seis *slices* se **reconstruyeron test-first** —RED real sobre código inexistente— en un laboratorio limpio nacido del mismo SHA base, antes de cualquier *commit*. Lo aprobado es la implementación reconstruida. Detalle en el reporte §I.2, §I.5 y §I.6 |
| **PostgreSQL real** | `personal_blog_test`, con la guarda *fail-closed* de `Task/005.6`/`005.7` activa. **SQLite no se usó** |
| **Esquema físico** | **No se modifica.** Sin migración nueva; `0002` sigue siendo `head` |
| **Decisiones que cierra** | **D-009-A** a **D-009-R**, todas **Vigentes** desde el 2026-08-27: `page_size` (12 / 50), política de parámetros desconocidos (**se rechazan**), lista cerrada de `sort` y su dirección, desempate por `slug`, semántica de `featured`, `tag` inexistente, visibilidad de `/tags`, forma y campos de `/search`, mecanismo de búsqueda e índices, respuesta de `/profile` sin perfil, y representación pública de una referencia a `MediaAsset` |
| **Decisiones que NO cierra** | Acceso a medios (`Task/010`); autenticación y D-15 (`Task/011`); CRUD y transiciones (`Task/012`); render de Markdown (`Task/014`, `Task/015`); correlation ID de extremo a extremo (`Task/017`) |
| **Fuera del alcance** | API administrativa, autenticación, `ObjectStorage`, frontend, cloud |
| **Suite completa** | **597 pasan, 1 omitida** (`time.tzset` en Windows, preexistente), **0 advertencias** con `-W error`. Cobertura de `app/`: **100 %** |
| **Efecto en el avance** | Avance global **9 de 41 (22 %)**; ETAPA 03 en **2 de 5 (40 %)** |
| **Ficha** | [TASK-009](../tasks/TASK-009-public-api.md) |
| **Reporte** | [TASK-009-report](../task-reports/TASK-009-report.md) |

---

## Tarea aprobada anterior — `Task/008-Modelo-de-Datos`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/008-Modelo-de-Datos` |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las 41 |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-25 |
| **Fecha de aprobación** | 2026-08-25 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/008-Modelo-de-Datos` |
| **Depende de** | `Task/007-Integracion-Local` (**Aprobada**) |
| **Repositorios modificados** | `personal-blog-backend` · `personal-blog-infra` (gobierno y documentación) |
| **Repositorio no modificado** | `personal-blog-frontend` — **sin rama y sin cambios**: la tarea no le afecta |
| **Ramas base** | **`main`** en ambos: `2290a9fb…` (backend) y `b23ad66d…` (infra). `HEAD == main` verificado inmediatamente tras crearlas |
| **Alcance entregado** | Modelo físico completo del MVP: **14 tablas** para los nueve tipos conceptuales; entidades de dominio del ciclo de vida de publicación; escala de valoración; restricciones e índices reales; migración Alembic `0002` reversible |
| **Test-first** | **Demostrado.** Matriz de casos previa en la ficha; RED registrado por *slice*; GREEN; refactor. Suite completa: **250 pasan, 1 omitida** (`time.tzset` no existe en Windows, preexistente), **0 advertencias** con `-W error` |
| **PostgreSQL real** | `personal_blog_test`, con la guarda *fail-closed* de `Task/005.6`/`005.7` activa. **SQLite no se usó** |
| **Decisiones que cierra** | Escala de `rating` (**1..5**), estrategia de clave primaria (**UUID**), semántica final de `published_at`, representación de estados, `social_links`, `technologies`, política de borrado de medios y cascadas de etiquetado. Todas **Vigentes** desde el 2026-08-25 |
| **Decisiones que NO cierra** | Retención de `AuditEvent`; formato y generación del *slug* (`Task/012`); proveedores de vídeo permitidos (`Task/014`); mecanismo de búsqueda y sus índices (`Task/009`) |
| **Fuera del alcance** | API pública (`Task/009`), `ObjectStorage` (`Task/010`), autenticación y auditoría operativa (`Task/011`), CRUD administrativo (`Task/012`), frontend, cloud |
| **Datos sembrados** | **Ninguno.** La migración no contiene `INSERT`: el perfil y el administrador llevan datos personales y una credencial, que no se versionan |
| **Efecto en el avance** | Avance global **8 de 41 (20 %)**; **ETAPA 03 abierta** con 1 de 5 |
| **Ficha** | [TASK-008](../tasks/TASK-008-data-model.md) |
| **Reporte** | [TASK-008-report](../task-reports/TASK-008-report.md) |
| **Modelo físico** | [data-model.md](../architecture/data-model.md) — **Vigente** ✔ |

### Hallazgos corregidos dentro de la tarea

Cuatro defectos reales que la propia práctica test-first sacó a la luz. Ninguno era
funcionalidad nueva; los cuatro dejan su prueba de regresión en la suite.

| # | Hallazgo | Corrección |
| --- | --- | --- |
| 1 | `app/shared/errors/__init__.py` reexportaba los manejadores HTTP, así que **importar una excepción desde el dominio cargaba FastAPI**: la regla de dependencias de ADR-004 se rompía sin que ningún import lo delatara | El paquete exporta solo excepciones; los manejadores se importan de su módulo. Regresión: `tests/unit/test_independencia_del_dominio.py` |
| 2 | `alembic/script.py.mako` no emitía los imports de dialecto de `--autogenerate`: la primera migración con un tipo `JSONB` habría fallado con `NameError` | Se añadió el marcador `${imports}` a la plantilla |
| 3 | `tests/test_database.py` afirmaba `Base.metadata.tables == {}` — "el proyecto no tiene tablas de negocio" —, condenado a caducar exactamente igual que la prueba de migraciones que `Task/005.6` ya tuvo que rehacer | Sustituida por una afirmación que no caduca |
| 4 | El descubrimiento de fixtures del harness usaba `hasattr`, y **`sqlalchemy.func` responde a cualquier atributo**: importarlo en un módulo de integración lo convertía en una "fixture" que no pasaba por la guarda | Se exige además que la marca provenga de pytest. La guarda anti-tautología existente sigue impidiendo que la condición deje fuera fixtures reales |

### Hallazgos de la revisión correctiva pre-approval

Cuatro más, encontrados **después** de la primera declaración `Lista para validación`. La
cronología se deja escrita: es trazabilidad, no un demérito.

| # | Hallazgo | Gravedad | Corrección |
| --- | --- | --- | --- |
| 5 | **El esquema contradecía USER_FLOWS.md B.2.** `book_title`, `book_author`, `provider` y `video_url` eran `NOT NULL`, así que crear un borrador de review o de vídeo obligaba a inventar datos | **Bloqueante** | Las cuatro admiten nulo, con RED → GREEN contra PostgreSQL real y una guarda estructural que recorre las columnas reales |
| 6 | **Estado transitorio persistido como vigente** (WORKFLOW §6.1): `Task/009` aparecía condicionada a que el PR estuviera *"fusionado y normalizado"* | **Bloqueante** | Redacción durable: `Task/009` depende de que `Task/008` esté **Aprobada**; el estado de Git se consulta en vivo |
| 7 | **La garantía de inmutabilidad de `AuditEvent` prometía de más**: el DML masivo del ORM la sortea | Precisión | Garantía reformulada al perímetro real y fijada por prueba en las dos direcciones. El endurecimiento restante es de **`Task/018`** |
| 8 | El *owner* del *bootstrap* de `Profile`/`Administrator` estaba atribuido de forma vaga a *"`Task/012` o posterior"* | Precisión | El ROADMAP ya lo asigna: **`Task/036`** en producción y **`Task/022`** para la semilla local |

---

## Tarea aprobada previa — `Task/007-Integracion-Local`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/007-Integracion-Local` |
| **Etapa** | ETAPA 02 — Fundaciones de las Aplicaciones |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las 41 |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-23 |
| **Fecha de aprobación** | 2026-08-23 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/007-Integracion-Local` |
| **Repositorios modificados** | `personal-blog-infra` · `personal-blog-frontend` |
| **Repositorio leído y NO modificado** | `personal-blog-backend` — la integración se resuelve **solo con configuración**; su `Dockerfile`, su configuración por entorno y `GET /health` sirven sin cambios |
| **Ramas base** | **`main`** en ambos: `a6412f3…` (infra) y `c4af3617…` (frontend) |
| **Alcance entregado** | Compose completo con **Traefik v3**, **frontend** y **backend** sobre la infraestructura existente; enrutado explícito **sin socket de Docker**; red de borde `blog-edge` separada de `blog-data`; arranque encadenado por *healthchecks*; **consumo real de `GET /health`** desde el frontend con el cliente HTTP oficial; runbook y gobierno actualizados |
| **Sitio y API** | **Mismo origen** (`http://localhost:8081`): el navegador no exige CORS y **no se configura ninguno** |
| **Datos** | **3 volúmenes antes y después, 0 eliminados.** `postgres`, `minio` y `portainer` no se recrearon |
| **Backups de `Task/004`** | **Compatibles.** Nombres de contenedor y de volumen intactos; integridad del conjunto existente verificada |
| **Fuera del alcance** | `ObjectStorage` y uso aplicativo de MinIO (`Task/010`), modelo de datos (`Task/008`), API pública (`Task/009`), autenticación (`Task/011`), diseño (`Task/013`+), CI y cualquier recurso cloud |
| **Riesgos nuevos** | **Ninguno.** **R-09 no se agrava**: Traefik **no** recibe el socket de Docker |
| **Efecto en el avance** | Avance global **7 de 41 (17 %)**; **ETAPA 02 completada** (3 de 3) |
| **Ficha** | [TASK-007](../tasks/TASK-007-local-integration.md) |
| **Reporte** | [TASK-007-report](../task-reports/TASK-007-report.md) |

> **Aprobada** por el usuario el 2026-08-23. Con ella **la ETAPA 02 queda completada** y el
> avance pasa a **7 de 41 (17 %)**.
>
> **Comprobación visual de Portainer: completada.** *Observado el 2026-08-25:* el usuario
> validó en la interfaz autenticada de Portainer que los seis contenedores del entorno son
> visibles y están sanos (`backend`, `frontend`, `traefik`, `postgres` y `minio` en
> `healthy`; `portainer` en `running`).
>
> El reporte de `Task/007` sigue diciendo que estaba pendiente, y **eso no se corrige**:
> era un hecho cierto en el momento en que se escribió. Lo que se actualiza aquí es el
> estado **vivo**, con su fecha de observación ([WORKFLOW §6.1](WORKFLOW.md), regla 2).

`Task/008-Modelo-de-Datos` fue **aprobada el 2026-08-25**: es la primera tarea de la
ETAPA 03 y la primera sujeta a la **BACKEND TEST-FIRST LAW**.

---

## Último mantenimiento aprobado — `Task/006.2`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| **Tipo** | **Mantenimiento transversal de arquitectura y planificación** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-23 |
| **Fecha de aprobación** | 2026-08-23 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| **Repositorios afectados** | `personal-blog-infra` (**únicamente**) |
| **Rama** | `Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| **Rama base** | **`main`** — única base permitida. SHA base: `d08fe27711866eabe091a2d139387e2022c95b70`. Verificado `HEAD == main` inmediatamente después de crearla |
| **Origen** | El usuario actualizó manualmente `images/Infraestructura.png` en `main` y normalizó `main → dev`. La documentación textual no describía la arquitectura que la imagen ya mostraba |
| **Alcance entregado** | Documento canónico [target-production-architecture.md](../architecture/target-production-architecture.md) (26 secciones) — **Vigente**; [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) — **Aceptada** ✔; alineación de `overview`, `local-to-cloud-mapping`, `security-boundaries` (**C-16**, **C-17**, §10), `production-postgresql-vps` (§11.1.1, §15.3.1), `non-functional-requirements` (**O-09**, **O-10**), `open-decisions` (**D-17**–**D-20**), `ROADMAP`, `STATUS`, `README` y las fichas de las ETAPAS 02, 05, 09, 10 y 12 |
| **Decisiones que cierra** | Secretos del VPS **cifrados** (herramienta abierta), **CloudWatch mínimo**, **Grafana Cloud** como plano central, **Grafana Alloy** en el VPS, **Terraform no configura el sistema operativo**, **Docker no es runtime de producción** |
| **Decisiones que abre** | **D-17** (herramienta de secretos del VPS, `Task/029`) · **D-18** (configuración del SO, `Task/029`) · **D-19** (plan y costo de Grafana Cloud, `Task/041`) · **D-20** (integración CloudWatch → Grafana, `Task/031`) |
| **Riesgos nuevos** | **R-38** a **R-42**, los cinco **abiertos** |
| **Imagen** | `images/Infraestructura.png` **no modificada**. Sigue siendo el commit `d08fe27` del usuario |
| **Implementación** | **0 funcionalidad.** 0 código, 0 pruebas, 0 Compose, 0 Terraform, 0 recursos cloud, 0 cuentas contratadas |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. **41 identificadores intactos, sin renumerar.** Avance global **6 de 41 (15 %)** y ETAPA 02 **2 de 3** **sin cambios** |
| **Ficha** | [TASK-006.2](../tasks/TASK-006.2-formalize-target-production-architecture.md) |
| **Reporte** | [TASK-006.2-report](../task-reports/TASK-006.2-report.md) |

> **Aprobada** por el usuario el 2026-08-23. **ADR-008** queda **Aceptada** y el documento
> canónico **Vigente**. Lo aceptado antes —ADR-001 a ADR-007— sigue vigente y **no se
> reabre**.
>
> **Aprobar no autoriza a implementar.** Contratar Grafana Cloud, provisionar el VPS,
> instalar Alloy o crear cualquier recurso cloud sigue exigiendo su tarea propietaria y la
> autorización explícita del usuario.

> **Reconciliación previa, ajena a esta tarea.** El 2026-08-23, **antes** de crear la rama,
> se verificó que la normalización `main → dev` del hotfix de la imagen —ejecutada
> manualmente por el usuario— estaba completa. Esa reconciliación **no forma parte del
> alcance de `Task/006.2`**.
>
> El estado vivo de ramas y pull request se consulta en Git y GitHub, no aquí
> ([WORKFLOW §6.1](WORKFLOW.md)).

`Task/007-Integracion-Local` sigue **Pendiente y no iniciada**, y **nacerá desde `main`**,
como toda rama Task.

---

## Último mantenimiento aprobado — `Task/006.1`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/006.1-Corregir-Drift-Documental-Post-Merge` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-19 |
| **Fecha de aprobación** | 2026-08-21 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/006.1-Corregir-Drift-Documental-Post-Merge` |
| **Repositorios afectados** | `personal-blog-infra` (**únicamente**) |
| **Rama** | `Task/006.1-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`**. SHA base: `f434666`. Verificado `HEAD == main` inmediatamente después de crearla |
| **Origen** | Auditoría focalizada del cierre post-merge de `Task/006`: **6 afirmaciones** presentaban como estado vigente un trámite de pull request ya consumado. Incumplimiento de [WORKFLOW §6.1](WORKFLOW.md), vigente desde `Task/005.6` |
| **Alcance entregado** | Las 6 afirmaciones reescritas en forma **duradera** en `STATUS.md` (4), `STAGE-02` (1) y la ficha `TASK-006` (1). Verificación dirigida posterior: **0 apariciones** de estado transitorio presentado como vigente |
| **Historia preservada** | El reporte de `Task/006` y las secciones de `Task/001`–`Task/005.7` **no se reescriben**: son registros fechados |
| **Implementación** | **0 funcionalidad.** 0 código, 0 pruebas, 0 Compose, 0 Terraform, 0 ADR, 0 recursos cloud. `ROADMAP.md` **sin cambios** |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global **6 de 41 (15 %)** y ETAPA 02 **2 de 3** **sin cambios** |
| **Ficha** | [TASK-006.1](../tasks/TASK-006.1-correct-post-merge-documentation-drift.md) |
| **Reporte** | [TASK-006.1-report](../task-reports/TASK-006.1-report.md) |

`Task/007-Integracion-Local` sigue **Pendiente y no iniciada**, y **nacerá desde `main`**,
como toda rama Task.

---

## Última tarea aprobada — `Task/006-Fundacion-Frontend-React`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/006-Fundacion-Frontend-React` |
| **Etapa** | ETAPA 02 — Fundaciones de las Aplicaciones |
| **Estado** | **Aprobada** ✔ |
| **Repositorios** | `personal-blog-frontend` (implementación) · `personal-blog-infra` (gobierno documental) |
| **Rama base** | `main` en ambos: `21cb51d8…` (frontend) y `ccc19473…` (infra) |
| **Fecha de inicio** | 2026-08-18 |
| **Fecha de aprobación** | 2026-08-18 |
| **Ficha** | [TASK-006](../tasks/TASK-006-react-frontend-foundation.md) |
| **Reporte** | [TASK-006-report](../task-reports/TASK-006-report.md) |
| **Efecto en el avance** | Avance global **6 de 41 (15 %)**; ETAPA 02 **2 de 3** |

Qué entrega: la fundación del frontend —React 19, TypeScript 5.9 estricto, Vite 8, router
con *fallback* 404, configuración de entorno validada al arrancar, cliente HTTP común con
modelo de error, suite de 31 pruebas, lint, formato y build de producción reproducible—.

Validaciones, con **códigos de salida reales**: `lint`, `typecheck`, `format:check`,
`test:coverage` y `build` terminan en **0**, tanto en el repositorio como desde una
instalación limpia con `npm ci`, cuyo `dist/` resulta **byte a byte idéntico**. La consola
del navegador queda **sin errores** en la ruta inicial y en una ruta 404, comprobado con
Chrome *headless*.

Su alcance excluye deliberadamente el sistema de diseño (`Task/013`), las páginas del sitio
público (`Task/014`), el panel administrativo (`Task/015`), la autenticación (`Task/011`) y
el consumo real del API (`Task/007`).

> **Cierre completado.** La aprobación quedó registrada, la tarea se integró en `dev`, el
> usuario fusionó los pull request `Task/006 → main` en ambos repositorios y la
> normalización `main → dev` se ejecutó después. `Task/007` sigue **Pendiente y no
> iniciada**, y **nacerá desde `main`**, como toda rama Task.
>
> El estado vivo de ramas y pull request se consulta en Git y GitHub, no aquí
> ([WORKFLOW §6.1](WORKFLOW.md)).

---

## Tarea aprobada anterior — `Task/005-Fundacion-Backend-FastAPI`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005-Fundacion-Backend-FastAPI` |
| **Etapa** | ETAPA 02 — Fundaciones de las Aplicaciones |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-01 |
| **Fecha de aprobación** | 2026-08-12 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005-Fundacion-Backend-FastAPI` |
| **Repositorios afectados** | `personal-blog-backend` (implementación) · `personal-blog-infra` (gobierno documental) |
| **Ramas** | `Task/005-Fundacion-Backend-FastAPI` en ambos repositorios, creadas desde `dev`. **Publicadas en el cierre.** |
| **Alcance entregado** | Proyecto FastAPI con Python 3.12; estructura de monolito modular; configuración tipada fail-fast; log JSON **con marcas de tiempo UTC explícitas**; manejo centralizado de errores; `GET /health`; OpenAPI; SQLAlchemy 2 con psycopg 3; Alembic con migración fundacional; 69 pruebas; `ruff`, `mypy` *strict*; `Dockerfile` construido **sin cache** y ejecutado |
| **Primer código de aplicación** | Sí: es el primer código ejecutable de `personal-blog-backend` |
| **Validaciones** | 38 ejecutadas. 69 pruebas superadas y 1 omitida con motivo, **`pytest -W error` con 0 warnings y sin filtros**, cobertura 99 %, lint, formato y tipado sin errores, imagen construida con `--no-cache`, contenedor `healthy`, ciclo `upgrade`/`downgrade`/reaplicación verificado contra PostgreSQL real, logs UTC comprobados en Windows y en Docker |
| **Correcciones del 2026-08-11** | Revisión previa a la aprobación: **UTC real** en el log (antes dependía del sistema operativo), **advertencia de `TestClient` resuelta** sustituyendo `httpx` por `httpx2` en desarrollo, **rectificada** la afirmación errónea sobre la rotación de la contraseña de PostgreSQL en **R-16**, y confirmada la coherencia del `Dockerfile` con **R-14** |
| **Entorno local** | **Intacto.** No se ejecutó ninguna operación destructiva; los 3 volúmenes principales siguen presentes |
| **Integración en `dev`** | Merge `--no-ff` en ambos repositorios, publicado |
| **Pull request** | `Task/005 → main`: **`#2`** en backend (merge `db6ab18`) y **`#6`** en infra (merge `af8a04c`) — **fusionados por el usuario** el 2026-08-13 |
| **Normalización posterior** | Completada el 2026-08-13: `main` integrada en `dev` con merge `--no-ff` en ambos repositorios y publicada. `dev` = `ce4f1bc` (backend) y `5efd5e0` (infra) |
| **Rama Task** | Eliminada **local y remotamente**. La local con `git branch -d`; la remota, por el usuario desde GitHub |
| **Riesgos nuevos** | **R-14**, **R-15** y **R-16**, los tres **abiertos** |
| **Ficha** | [TASK-005](../tasks/TASK-005-fastapi-backend-foundation.md) |
| **Reporte** | [TASK-005-report](../task-reports/TASK-005-report.md) |

Con esta aprobación el avance global pasa a **5 de 41 (12 %)** y la **ETAPA 02** queda en
**1 de 3** tareas aprobadas.

---

## Tarea aprobada previa — `Task/004-Backups-y-Recuperacion-Local`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/004-Backups-y-Recuperacion-Local` |
| **Etapa** | ETAPA 01 — Infraestructura Local |
| **Estado** | **Aprobada** |
| **Fecha de inicio** | 2026-07-31 |
| **Fecha de aprobación** | 2026-07-31 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/004-Backups-y-Recuperacion-Local` |
| **Repositorios afectados** | `personal-blog-infra` (únicamente) |
| **Rama de cierre** | `Task/004-Backups-y-Recuperacion-Local`, creada desde `dev` |
| **Alcance entregado** | 5 scripts PowerShell de backup, verificación, restauración aislada y limpieza; conjunto de respaldo con manifiesto y checksums SHA-256; inventario de **metadatos y tags** de MinIO y de **configuración de buckets**; runbook de backup y recuperación; `local-backups/` ignorado por Git |
| **Prueba de restauración** | **Ejecutada y superada** en entorno temporal aislado: PostgreSQL, MinIO (contenido, metadatos y tags) y Portainer |
| **Alcance en MinIO** | Versión **actual** de cada objeto: contenido, metadatos y tags. El **historial de versiones** queda fuera del alcance y la **configuración de los buckets** se registra pero no se reaplica; el script lo detecta y aborta salvo `-AllowPartial` |
| **Integración en `dev`** | Merge `--no-ff`, publicado |
| **Pull request** | `Task/004-Backups-y-Recuperacion-Local → main` (`#5`) — **fusionado** por el usuario el 2026-07-31, commit `c86d47e` |
| **Normalización posterior** | `main` integrada en `dev` mediante el merge `5f09e22` el 2026-08-01, al iniciar `Task/005` |
| **Rama Task** | Eliminada **local y remotamente** |
| **Riesgo cerrado** | **R-08** — el entorno local ya tiene copia externa a los volúmenes, verificada y restaurable |
| **Ficha** | [TASK-004](../tasks/TASK-004-local-backups-and-recovery.md) |
| **Reporte** | [TASK-004-report](../task-reports/TASK-004-report.md) |
| **Runbook producido** | [local-backup-and-recovery.md](../runbooks/local-backup-and-recovery.md) — **Vigente** |

Con esta aprobación **la ETAPA 01 queda completada** (2 de 2 tareas).

El PR `#5` fue fusionado por el usuario y la normalización `main → dev` se completó el
2026-08-01, lo que habilitó el inicio de `Task/005`.

---

## Tareas aprobadas previas

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/003-Crear-Infraestructura-Local` |
| **Estado** | **Aprobada y cerrada** |
| **Fecha de aprobación** | 2026-07-29 |
| **Pull request** | `Task/003-Crear-Infraestructura-Local → main` (`#4`) — **fusionado** el 2026-07-31, commit `966db01` |
| **Normalización posterior** | `main` integrada en `dev` mediante el merge `708a71e` |
| **Rama Task** | Eliminada local y remotamente |
| **Decisión promovida** | **D-05 → Resuelta**: Traefik v3 como reverse proxy local, a implementar en `Task/007` |
| **Runbook producido** | [local-environment.md](../runbooks/local-environment.md) — **Vigente** |

---

## Mantenimiento anterior aprobado — `Task/005.5`

> *(Título corregido en `Task/005.7`: esta sección y la de `Task/005.6` se llamaban
> ambas «Último mantenimiento aprobado». El contenido histórico no se altera.)*

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.5-Alinear-Planificacion-Tras-Auditoria` |
| **Tipo** | **Mantenimiento de gobierno, planificación y arquitectura documental** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-16 |
| **Fecha de aprobación** | 2026-08-16 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.5-Alinear-Planificacion-Tras-Auditoria` |
| **Repositorios afectados** | `personal-blog-infra`, `personal-blog-backend`, `personal-blog-frontend` — **solo documentación** |
| **Rama** | `Task/005.5-Alinear-Planificacion-Tras-Auditoria` en los tres repositorios |
| **Rama base** | **`main`** en los tres. SHA base: infra `cc90b96` · backend `db6ab18` · frontend `144a401`. Verificado `HEAD == main` en los tres |
| **Origen** | Dos auditorías independientes del proyecto. **Sus hallazgos no se aceptaron como autoridad automática**: cada uno se reprodujo contra el repositorio antes de decidir |
| **Objetivo** | Eliminar contradicciones entre repositorios, corregir dependencias invertidas, asignar propietarios ausentes y propagar decisiones ya aprobadas |
| **Corrección principal de workflow** | Backend y frontend seguían ordenando crear ramas Task **desde `dev`**, contradiciendo el invariante de `Task/005.4`. **6 reglas operativas corregidas** |
| **Correcciones de secuencia** | `Task/025` pasa a depender también de **`Task/024`** · `Task/029` deja de exigir evidencia que solo existe tras `Task/030`/`Task/032` · `Task/021` deja de prometer Terraform inexistente · la topología de dominios deja de depender de `Task/035` |
| **Propietarios asignados** | `S3Storage` · backup productivo · identidad del VPS hacia AWS · certificado TLS · observabilidad del VPS · migraciones en producción · medios públicos · credenciales CI multi-provider |
| **Decisiones nuevas** | **D-15** (topología lógica de dominios, `Task/011`) y **D-16** (identidad del VPS hacia AWS, `Task/029`). Ambas **abiertas** |
| **ADR** | **Ninguno nuevo.** No apareció ninguna decisión arquitectónica independiente: se corrigieron *ownership* y secuencia, no arquitectura |
| **Arquitectura** | **Sin cambios.** Cloudflare Pages, API Gateway, Lambda, S3, SSM, IAM, CloudWatch, PgBouncer, PostgreSQL en VPS, Terraform, Floci y `ObjectStorage` siguen exactamente igual |
| **Implementación** | **Ninguna.** 0 código funcional, 0 Terraform, 0 Compose, 0 recursos cloud, 0 VPS, 0 GitHub Actions |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. **41 identificadores intactos**, sin renumerar. Avance global y ETAPA 02 **sin cambios** |
| **Imagen de arquitectura** | `images/Infraestructura.png` **intacta**. Se corrigieron los textos que aún la trataban como autoridad canónica de producción |
| **Integración en `dev`** | Merge `--no-ff` en los **tres** repositorios, publicado |
| **Pull request** | `Task/005.5 → main` en los tres repositorios. *Observado el 2026-08-16 con `gh pr list`:* **`#11` infra, `#3` backend y `#2` frontend — `MERGED`**, fusionados por el usuario |
| **Normalización posterior** | **Completada.** *Observado el 2026-08-16:* `main` = `bd0aaf5` (infra), `72c8adc` (backend), `4132a65` (frontend); `main` integrada en `dev` y publicada — `dev` = `2819f6c` · `1e20839` · `7e89d2a`. `git diff main dev` **vacío** y `main` **ancestro de `dev`** en los tres |
| **Rama Task** | Eliminada **local y remotamente** en los tres. *Observado el 2026-08-16:* `git ls-remote --heads origin "Task/*"` **no devuelve nada** |
| **Ficha** | [TASK-005.5](../tasks/TASK-005.5-align-planning-after-audit.md) |
| **Reporte** | [TASK-005.5-report](../task-reports/TASK-005.5-report.md) |

La aprobación de este mantenimiento **no modifica el conteo del roadmap**: el avance global
permanece en **5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas.

Con ella quedan **vigentes**: el invariante de ramas aplicado a **los tres repositorios**,
el **mapa de responsabilidades transversales** del ROADMAP, la dependencia
`Task/025 → Task/024`, la separación entre lo que `Task/029` **define** y lo que solo puede
**validarse** más tarde, y las decisiones **D-15** y **D-16**, ambas **abiertas**.
`Task/006` sigue **Pendiente y no iniciada**.

---

## Mantenimiento aprobado anterior — `Task/005.7`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion` |
| **Tipo** | **Mantenimiento transversal**: hermeticidad del harness de pruebas y *fail-closed* real de la integración |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-16 |
| **Fecha de aprobación** | 2026-08-16 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion` |
| **Repositorios afectados** | `personal-blog-backend`, `personal-blog-infra`, `personal-blog-frontend` |
| **Rama** | `Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion` en los tres |
| **Rama base** | **`main`** en los tres. SHA base: infra `7c98f59` · backend `c36cd44` · frontend `5d2bef1`. Verificado `HEAD == main` inmediatamente después de crearlas |
| **Origen** | Mega auditoría final independiente (Claude y Codex). Ambos reprodujeron los **mismos dos defectos**; discreparon en severidad (Claude: MEDIO, diferir · Codex: ALTO, baseline no certificada). Se adopta **deliberadamente el criterio más estricto**: corregir ahora |
| **CERT-AUD-001** | **Cerrado.** El arranque de la suite ya no consume el `.env` del desarrollador, tampoco durante la *collection*. Dos capas independientes en `tests/` |
| **CERT-AUD-002** | **Cerrado.** Un único resolutor verificado (`destino_de_integracion_verificado`) alimenta todas las fixtures de integración. No queda ruta oficial sin guarda |
| **Comprobación estructural** | Los módulos del harness se **descubren** del directorio `tests/integration/`, no se enumeran a mano: añadir un módulo nuevo no exige recordar registrarlo. *(Corregido durante la validación del usuario: la lista manual fallaba **abierta** y ya omitía dos módulos existentes.)* |
| **CERT-AUD-009** | **Diferido con propietario explícito**: `Task/020-CI-Backend`. Riesgo **R-37**. No se implementa paralelismo ahora |
| **Implementación** | **0 funcionalidad de negocio.** `app/` **sin cambios**. 0 código frontend, 0 Terraform, 0 recursos cloud |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global y ETAPA 02 **sin cambios** |
| **Ficha** | [TASK-005.7](../tasks/TASK-005.7-close-final-certification-findings.md) |
| **Reporte** | [TASK-005.7-report](../task-reports/TASK-005.7-report.md) |

Este mantenimiento **no modifica el conteo del roadmap**: el avance global permanece en
**5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas. `Task/006` sigue
**Pendiente y no iniciada**.

Con esta aprobación quedan **vigentes**: el **arranque hermético** del harness de pruebas
—la suite no consume el `.env` del desarrollador ni durante la *collection*—, la garantía
***fail-closed*** del harness de integración con un **único resolutor verificado**, el
**descubrimiento automático** de los módulos del harness en la comprobación estructural, la
coherencia entre `.gitattributes` y `.editorconfig` en los tres repositorios y las secciones
§8.3.5 – §8.3.7 de [BACKEND_TESTING_STRATEGY](BACKEND_TESTING_STRATEGY.md).

El alcance de la garantía es el **harness oficial**, no Python arbitrario: la documentación
no promete más protección de la que existe.

---

## Mantenimiento anterior aprobado — `Task/005.6`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.6-Cerrar-Fundaciones-Tras-Mega-Auditoria` |
| **Tipo** | **Mantenimiento transversal de fundaciones**: reproducibilidad, aislamiento de pruebas y estado documental |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-16 |
| **Fecha de aprobación** | 2026-08-16 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.6-Cerrar-Fundaciones-Tras-Mega-Auditoria` |
| **Repositorios afectados** | `personal-blog-infra`, `personal-blog-backend`, `personal-blog-frontend` |
| **Rama** | `Task/005.6-Cerrar-Fundaciones-Tras-Mega-Auditoria` en los tres |
| **Rama base** | **`main`** en los tres. SHA base: infra `bd0aaf5` · backend `72c8adc` · frontend `4132a65`. Verificado `HEAD == main` inmediatamente después de crearlas |
| **Origen** | Conciliación de **dos mega auditorías independientes** (Claude y Codex). Ninguna se aceptó como autoridad: cada hallazgo se **reprodujo** contra el repositorio antes de decidir |
| **Conclusión de ambas auditorías** | **No existe defecto arquitectónico.** Arquitectura, Git, roadmap, PostgreSQL, FastAPI, Docker, Alembic y las *boundaries* son reutilizables |
| **Política EOL** | `.gitattributes` en los **tres** repositorios. Causa raíz: `core.autocrlf=true` de nivel *system* convertía el árbol de trabajo a CRLF y `ruff format --check .` fallaba en los 31 archivos Python. **El índice ya era LF**: la corrección produce **0 líneas de diff de contenido** |
| **Aislamiento de pruebas** | `settings_factory` construye con `_env_file=None`: la suite ya no lee el `.env` del desarrollador. Con regresión y guarda anti-tautología |
| **Base de datos de pruebas** | `personal_blog_test`, **dedicada**. Guarda *fail-closed* de dos barreras: sufijo `_test` **y** marca `personal-blog:test-database` **dentro** de la base. `personal_blog` **no se toca** |
| **Skip frente a fail** | Sin variable de entorno → `SKIP`. Con variable y PostgreSQL roto → **`FAIL`**. Ningún error se degrada ya a `skip` |
| **Tests semánticos** | `commit` y `rollback` demuestran **efecto persistente observado desde otra sesión**. Verificados por **mutación**: con `session_scope` roto, ambos se ponen rojos |
| **Migraciones** | Contrato durable: el esquema tras `upgrade` + `downgrade` debe ser idéntico al de antes. Sustituye a la aserción que habría caducado en `Task/008` |
| **Implementación** | **0 funcionalidad de negocio.** `app/` **sin cambios**: `git diff -- app/` vacío. 0 código frontend, 0 Terraform, 0 recursos cloud, 0 cambios en Docker Compose |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global y ETAPA 02 **sin cambios** |
| **Regla de gobierno nueva** | [WORKFLOW §6.1](WORKFLOW.md): los documentos versionados registran **estado duradero**; el estado transitorio de Git/GitHub se consulta **en vivo**. Elimina la necesidad estructural de una tarea de mantenimiento tras cada fusión |
| **ADR** | **Ninguno nuevo.** No apareció ninguna decisión arquitectónica: se corrigieron reproducibilidad, aislamiento de pruebas y precisión documental. **`ADR-001` no cambia su decisión**, solo una cifra frágil por una referencia por etapas |
| **Arquitectura** | **Sin cambios.** Monolito modular, FastAPI, PostgreSQL, MinIO/S3, Cloudflare Pages, API Gateway, Lambda, Terraform, Floci y PgBouncer siguen exactamente igual |
| **Riesgo nuevo** | **R-36** — el log no redacta secretos de forma automática. **Abierto**, con propietario `Task/017` y `Task/018` |
| **Integración en `dev`** | Merge `--no-ff` en los **tres** repositorios, publicado |
| **Pull request** | `Task/005.6 → main` en los tres. Base `main`, head la rama Task. **Ninguno es `dev → main`** y **ninguno lo fusiona Claude** |
| **Ficha** | [TASK-005.6](../tasks/TASK-005.6-close-foundations-after-mega-audit.md) |
| **Reporte** | [TASK-005.6-report](../task-reports/TASK-005.6-report.md) |

Este mantenimiento **no modifica el conteo del roadmap**: el avance global permanece en
**5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas. `Task/006` sigue
**Pendiente y no iniciada**.

Con esta aprobación quedan **vigentes**: la política de finales de línea de los tres
repositorios, la **base de datos de pruebas dedicada** con sus guardas *fail-closed*, la
distinción **skip / fail** de la integración, la verificación **semántica** de
`commit`/`rollback`, el contrato durable de migraciones y la regla de gobierno de
[WORKFLOW §6.1](WORKFLOW.md). El **invariante de ramas no cambia**: toda Task nace de `main`.

---

## Mantenimiento aprobado anterior — `Task/005.4`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.4-Corregir-Base-Ramas-Task-Main` |
| **Tipo** | **Mantenimiento de gobierno y workflow Git** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-15 |
| **Fecha de aprobación** | 2026-08-15 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.4-Corregir-Base-Ramas-Task-Main` |
| **Repositorios afectados** | `personal-blog-infra` **únicamente**, más el `CLAUDE.md` raíz del workspace |
| **Rama** | `Task/005.4-Corregir-Base-Ramas-Task-Main` |
| **Rama base** | **`main`** — **primera tarea del proyecto creada desde `main`** |
| **SHA base** | **`181c634`** (`= main = origin/main` en el momento de crearla). Verificado: `HEAD == main`, distinto de `dev` (`9dfbc10`) |
| **Problema corregido** | La documentación indicaba que las ramas Task debían crearse **desde `dev`**, e incluso prohibía explícitamente partir de `main`. Es incorrecto: `dev` acumula commits de integración que contaminan la ascendencia de una tarea nueva y pueden filtrarse al PR `Task → main` |
| **Invariante establecido** | **Toda rama `Task/<...>` nace desde `main` actualizado y limpio. `dev` NUNCA es base de una Task**; es exclusivamente rama de integración |
| **Qué NO cambia** | La palabra de aprobación, la integración `Task → dev`, el push de `dev`, la publicación de la rama Task, el PR `Task → main`, el merge manual del usuario y la normalización `main → dev`. **Solo cambia de dónde nace la rama** |
| **Alcance** | Gobierno y workflow **exclusivamente**. 0 cambios de arquitectura, 0 implementación |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global y ETAPA 02 **sin cambios** |
| **Historial de tareas anteriores** | **No se reescribe.** `Task/002`–`Task/005.3` nacieron de `dev` por la regla incorrecta; sus fichas y reportes se conservan como registro histórico |
| **Integración en `dev`** | Merge `--no-ff`, publicado |
| **Pull request** | `Task/005.4-Corregir-Base-Ramas-Task-Main → main` (**`#10`**) — **FUSIONADO** por el usuario. Merge commit **`cc90b96`**, `mergedAt = 2026-08-16T04:20:19Z` (UTC) |
| **Normalización posterior** | **Completada.** `main` = `cc90b96`; `main` integrada en `dev` (`f2eb330`, `Merge branch 'main' into dev`), publicado. `git diff main dev` **vacío** y `main` es **ancestro de `dev`**. Verificado el 2026-08-16 al iniciar `Task/005.5` |
| **Rama Task** | Eliminada **local y remotamente**. `git ls-remote --heads origin "Task/*"` **no devuelve nada** |
| **Ficha** | [TASK-005.4](../tasks/TASK-005.4-correct-task-branch-base-main.md) |
| **Reporte** | [TASK-005.4-report](../task-reports/TASK-005.4-report.md) |

La aprobación de este mantenimiento **no modifica el conteo del roadmap**: el avance global
permanece en **5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas.

Con ella, el **invariante de ramas** queda **vigente y de cumplimiento obligatorio**:
**toda rama `Task/<...>` nace desde `main` actualizado y limpio; `dev` nunca es base de una
Task.** `Task/006` sigue **Pendiente y no iniciada**, y **nacerá desde `main`**.

> **Corrección de alcance registrada en `Task/005.5`.** `Task/005.4` corrigió el invariante
> **solo en `personal-blog-infra` y en el `CLAUDE.md` raíz**. `personal-blog-backend` y
> `personal-blog-frontend` conservaban en su `README.md` y su `CONTRIBUTING.md` la regla
> antigua —*«creado desde `dev`»*—, que seguía siendo **instrucción operativa vigente** en
> esos repositorios. `Task/005.5` cierra ese hueco: **0 reglas operativas** ordenan ya crear
> una Task desde `dev` en ninguno de los tres repositorios.

---

## Mantenimiento aprobado anterior — `Task/005.3`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` |
| **Tipo** | **Mantenimiento de arquitectura y gobierno documental** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-15 |
| **Fecha de aprobación** | 2026-08-15 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` |
| **Repositorios afectados** | `personal-blog-infra` **únicamente** |
| **Rama** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS`, creada desde `dev` (`a563de6`). **Publicada en el cierre** |
| **Objetivo** | Cambiar el destino de la capa de datos de producción: de **PostgreSQL administrado** a **PostgreSQL autogestionado en un VPS externo**, con **PgBouncer** delante, manteniendo FastAPI en **AWS Lambda** |
| **Motivación** | **Costo** —evitar que la base de datos domine la factura de una arquitectura que escala a cero— más aprendizaje operacional real y mayor control |
| **Alcance entregado** | Documento canónico [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) (**Vigente**); [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) (**Aceptada**); **D-01 Resuelta** en cuanto al modelo; `Task/029` redefinida conservando su ID; nueva §9 y componentes **C-13**, **C-14**, **C-15** en límites de seguridad; **PRODUCTION DATABASE LAW** en `PROJECT_INSTRUCTIONS.md` §16; actualización de ETAPA 08, ETAPA 09, mapping, paridad AWS y README |
| **Qué NO cambia** | FastAPI sigue en **Lambda**; API Gateway, S3, SSM, CloudWatch, IAM, Terraform, Floci y Cloudflare Pages **sin cambios**; el entorno local **sin cambios** |
| **Implementación** | **Ninguna.** 0 VPS contratados, 0 PostgreSQL instalado, 0 PgBouncer instalado, 0 archivos Terraform, 0 recursos AWS, 0 RDS, 0 NAT Gateway, 0 cambios en backend, frontend y Docker Compose |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global y ETAPA 02 **sin cambios** |
| **Decisiones que NO resuelve** | Proveedor, región y tamaño del VPS (`Task/029`); **D-06** (backend de estado de Terraform, `Task/025`); tamaños de pool y `max_connections`; frecuencia y retención de backups (**D-10**); si se adopta mTLS; si se implementa PITR |
| **Riesgos nuevos** | **R-29** a **R-35**, los siete **abiertos** |
| **Imagen de arquitectura** | `images/Infraestructura.png` **intacta**: no modificada, no regenerada, no movida, no reemplazada. Pasa a tratarse como *arquitectura objetivo inicial, anterior a esta decisión* |
| **Integración en `dev`** | Merge `--no-ff`, publicado |
| **Pull request** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS → main` (**`#9`**) — **FUSIONADO** por el usuario. Merge commit **`181c634`**, `mergedAt = 2026-08-16T03:56:08Z` (UTC) |
| **Rama Task** | Eliminada **local y remotamente**. La local con `git branch -d` en el cierre; la remota, por el usuario desde GitHub |
| **Normalización posterior** | **Completada el 2026-08-15.** `main` = `181c634`; `main` integrada en `dev` con merge `--no-ff` **`9dfbc10`**, publicado. `git diff main dev` vacío y `main` es ancestro de `dev` |
| **Ficha** | [TASK-005.3](../tasks/TASK-005.3-define-production-postgresql-vps.md) |
| **Reporte** | [TASK-005.3-report](../task-reports/TASK-005.3-report.md) |

La aprobación de este mantenimiento **no modifica el conteo del roadmap**: el avance global
permanece en **5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas.

Con ella, `ADR-007` pasa a **Aceptada**, **D-01** a **Resuelta** en cuanto al **modelo**
—el proveedor sigue en `Task/029`—, `production-postgresql-vps.md` y la **PRODUCTION
DATABASE LAW** pasan a **vigentes**, y los riesgos **R-29** a **R-35** a **Abiertos**.
`Task/006` sigue **Pendiente y no iniciada**.

---

## Mantenimiento aprobado previo — `Task/005.2`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` |
| **Tipo** | **Mantenimiento de arquitectura y gobierno documental** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-15 |
| **Fecha de aprobación** | 2026-08-15 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.2-Documentar-Estrategia-Floci-IaC-Local` |
| **Repositorios afectados** | `personal-blog-infra` **únicamente** |
| **Rama** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local`, creada desde `dev` normalizado (`4e6bfaa`). **Publicada en el cierre** |
| **Objetivo** | Formalizar que la infraestructura AWS pueda desarrollarse, aprenderse, provisionarse y destruirse **localmente** antes de gastar en AWS real, con **una sola definición de Terraform** para ambos destinos |
| **Alcance entregado** | Documento canónico [aws-local-parity.md](../architecture/aws-local-parity.md) (**Vigente**); [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) (**Aceptada**); matriz de paridad inicial (entera en `No evaluada`); decisión **D-14 Resuelta**; ampliación del alcance futuro de la ETAPA 08 y de `Task/023`–`Task/026`; reutilización de módulos en la ETAPA 10; encaje del laboratorio en `Task/039`; componente **C-12** y §8 en límites de seguridad; ley compacta en `PROJECT_INSTRUCTIONS.md` §15 |
| **Verificación de Floci** | 2026-08-15, **solo fuentes oficiales** (repositorio y documentación del proyecto). Sin blogs ni terceros |
| **Implementación** | **Ninguna.** 0 archivos Terraform, 0 cambios en Docker Compose, Floci **no instalado**, sin imágenes descargadas, sin contenedores, sin recursos AWS, sin cuentas |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global y ETAPA 02 **sin cambios** |
| **Decisiones que NO resuelve** | **D-01** (PostgreSQL administrado, `Task/029`) y **D-06** (backend de estado de Terraform, `Task/025`), ambas **siguen abiertas** |
| **Riesgos nuevos** | **R-19** a **R-28**, los diez **abiertos** |
| **Imagen de arquitectura** | `images/Infraestructura.png` **intacta**: no modificada, no regenerada, no movida, no reemplazada |
| **Integración en `dev`** | Merge `--no-ff` **`a61ecbf`**, publicado |
| **Pull request** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local → main` (**`#8`**) — **FUSIONADO** por el usuario. Merge commit **`5583947`**, `mergedAt = 2026-08-16T01:23:02Z` (UTC) |
| **Rama Task** | Eliminada **local y remotamente**. La local con `git branch -d` durante el cierre; la remota, por el usuario desde GitHub |
| **Normalización posterior** | **Completada por el usuario.** `main` = `5583947`; `dev` = `a563de6` (`Merge branch 'main' into dev`), publicado. `git diff main dev` vacío y `main` contenida en `dev`. Verificado el 2026-08-15 al iniciar `Task/005.3` |
| **Ficha** | [TASK-005.2](../tasks/TASK-005.2-document-floci-local-iac-strategy.md) |
| **Reporte** | [TASK-005.2-report](../task-reports/TASK-005.2-report.md) |

La aprobación de este mantenimiento **no modifica el conteo del roadmap**: el avance global
permanece en **5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas.

Con ella, `ADR-006` pasa a **Aceptada**, **D-14** a **Resuelta** y los riesgos **R-19** a
**R-28** a **Abiertos**. `Task/006` sigue **Pendiente y no iniciada**: no comienza hasta que
el usuario fusione el PR de `Task/005.2` y se complete la normalización `main → dev`.

---

## Mantenimiento aprobado previo — `Task/005.1`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.1-Formalizar-TDD-Backend` |
| **Tipo** | Mantenimiento de gobierno documental |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-13 |
| **Fecha de aprobación** | 2026-08-13 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.1-Formalizar-TDD-Backend` |
| **Repositorios afectados** | `personal-blog-infra` **únicamente** |
| **Rama** | `Task/005.1-Formalizar-TDD-Backend`, creada desde `dev`. **Publicada en el cierre** |
| **Alcance entregado** | Práctica **test-first** obligatoria del backend: documento canónico [BACKEND_TESTING_STRATEGY](BACKEND_TESTING_STRATEGY.md); ley compacta en `PROJECT_INSTRUCTIONS.md` §14; criterios **B-1 a B-12** en la Definition of Done; sección *TDD / Plan test-first* en la plantilla de tareas; política reflejada en ROADMAP y ETAPA 03 para `Task/008`–`Task/012` |
| **Regla central** | **RED → GREEN → REFACTOR**, con matriz de casos previa y evidencia de RED y GREEN en el reporte de cada tarea de backend funcional |
| **Código modificado** | **Ninguno.** 0 cambios en backend y frontend, 0 dependencias nuevas |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global y ETAPA 02 **sin cambios** |
| **Riesgos nuevos** | **R-17** y **R-18** |
| **Asset versionado en el cierre** | `images/Infraestructura.png` — diagrama de la arquitectura objetivo inicial, **preexistente**, agregado por el usuario el 2026-07-26 y autorizado explícitamente para versionarse en este cierre. **No es un entregable de la tarea** y no se modificó |
| **Integración en `dev`** | Merge `--no-ff`, publicado |
| **Pull request** | `Task/005.1-Formalizar-TDD-Backend → main` (**`#7`**) — **FUSIONADO** por el usuario. Merge commit **`2f56a13`**, `mergedAt = 2026-08-16T00:25:21Z` (UTC) |
| **Rama Task** | Eliminada **local y remotamente**. La local con `git branch -d` durante el cierre; la remota, por el usuario desde GitHub. Verificado: `git ls-remote --heads origin "Task/*"` no devuelve nada |
| **Normalización posterior** | **Completada el 2026-08-15.** `main` = `2f56a13`; `main` integrada en `dev` con merge `--no-ff` **`4e6bfaa`**, publicado. `git diff main dev` vacío y `2f56a13` es ancestro de `dev` |
| **Ficha** | [TASK-005.1](../tasks/TASK-005.1-formalize-backend-tdd.md) |
| **Reporte** | [TASK-005.1-report](../task-reports/TASK-005.1-report.md) |

La aprobación de este mantenimiento **no modifica el conteo del roadmap**: el avance global
permanece en **5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas.

---

## Mantenimiento de gobierno anterior

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/002.1-Configurar-Claude-Code` |
| **Tipo** | Mantenimiento de gobierno |
| **Estado** | **Aprobada y cerrada** |
| **Fecha de aprobación** | 2026-07-26 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/002.1-Configurar-Claude-Code` |
| **Rama de cierre** | `Task/002.1-Configurar-Claude-Code` |
| **Pull request** | `Task/002.1-Configurar-Claude-Code → main` — **fusionado** por el usuario (commit `dbb41aa`) |
| **Normalización posterior** | `main` integrada en `dev` mediante el merge `cca847c`; ambas ramas con contenido idéntico |
| **Rama Task** | Eliminada local y remotamente |
| **Roadmap** | No cuenta dentro de las 41 tareas |
| **Avance global** | Permanece en **2 de 41**, aproximadamente **5 %** |
| **Bloqueos activos** | Ninguno |

La aprobación de este mantenimiento no modificó el conteo del roadmap. La
normalización `main → dev` se completó, lo que habilitó el inicio de `Task/003`.

---

## Resumen del avance

| Etapa | Tareas | Aprobadas | Avance |
| --- | --- | --- | --- |
| 00 — Fundación y Gobierno | 2 | 2 | **100 %** |
| 01 — Infraestructura Local | 2 | 2 | **100 %** |
| 02 — Fundaciones de las Aplicaciones | 3 | 3 | **100 %** — **completada** |
| 03 — Dominio y Backend | 5 | **2** | **40 %** |
| 04 — Experiencia del Usuario | 3 | 0 | 0 % |
| 05 — Calidad y Seguridad | 3 | 0 | 0 % |
| 06 — Integración Continua | 3 | 0 | 0 % |
| 07 — Validación Local | 1 | 0 | 0 % |
| 08 — Preparación Cloud sin Cuentas | 4 | 0 | 0 % |
| 09 — Cuentas y Seguridad Cloud | 3 | 0 | 0 % |
| 10 — Despliegue Cloud | 7 | 0 | 0 % |
| 11 — Automatización de Despliegues | 3 | 0 | 0 % |
| 12 — Lanzamiento y Operación | 2 | 0 | 0 % |
| **Total** | **41** | **9** | **22 %** |

Distribución por estado:

| Estado | Tareas |
| --- | --- |
| Pendiente | 32 |
| En progreso | 0 |
| Lista para validación | 0 |
| **Aprobada** | **9** |
| Bloqueada | 0 |
| Descartada | 0 |

> Esta distribución incluye únicamente las 41 tareas del roadmap. La tarea de
> mantenimiento `Task/002.1` se registra por separado.

---

## Bloqueos

*Ninguno activo.*

| # | Tarea afectada | Motivo | Resolución | Estado |
| --- | --- | --- | --- | --- |
| B-01 | `Task/001` — pasos de publicación del cierre | No había credenciales de GitHub en el entorno y la sesión no podía abrir un diálogo de autenticación, por lo que no se pudo hacer push ni abrir el pull request. | El usuario instaló y autenticó **GitHub CLI** (cuenta `jeffersondavila`, HTTPS, `gh` como proveedor de credenciales de Git). Se completaron los push, se crearon y aceptaron los pull requests (`#1` en cada repositorio) y se eliminaron las ramas `Task/001` local y remotamente. | **Cerrado** (2026-07-26) |

> Todo bloqueo debe registrarse aquí indicando: tarea afectada, motivo del bloqueo y
> acción concreta necesaria para desbloquear.

---

## Riesgos

| # | Riesgo | Impacto | Mitigación prevista | Estado |
| --- | --- | --- | --- | --- |
| R-01 | Los tres repositorios no tenían commit inicial, por lo que `dev` y las ramas `Task/*` no podían existir como referencias Git. | Medio | **Resuelto** el 2026-07-26 durante la aprobación de `Task/001`: commit inicial vacío en `main`, `dev` creada desde `main` y `Task/001` creada desde `dev` en los tres repositorios. | **Cerrado** |
| R-02 | Costo cloud imprevisto al llegar a la Etapa 10. | Alto | Presupuestos y alarmas obligatorios en `Task/027`, antes de cualquier despliegue; refuerzo en `Task/041`. | Abierto |
| R-03 | La elección de la base de datos de producción condiciona el diseño de conexiones desde Lambda (pooling, límites). | Medio | Evaluar en `Task/029` y considerar el patrón de conexión desde `Task/005`. **Actualización vigente desde el 2026-08-15 (`Task/005.3`, aprobada):** con PostgreSQL en un VPS, la mitigación concreta es **PgBouncer** con pool limitado más *Reserved Concurrency* de Lambda, aplicada en `Task/032`; ver **R-33**. | Abierto |
| R-04 | El roadmap de 41 tareas puede quedar desactualizado si el alcance cambia. | Bajo | `STATUS.md` y `ROADMAP.md` se actualizan en cada cambio de estado, como parte de la Definition of Done. | Abierto |
| R-05 | Los enlaces cruzados entre repositorios asumen que los tres están clonados como carpetas hermanas. | Bajo | Suposición documentada en los README de frontend y backend; alternativa futura: enlazar a las URL de GitHub. | Abierto |
| R-06 | El alcance del MVP puede crecer durante la implementación. | Medio | [MVP_SCOPE.md](../product/MVP_SCOPE.md) §6 lista explícitamente lo excluido; toda incorporación exige un ADR que reemplace la decisión vigente. | Abierto |
| R-07 | El render de Markdown en el cliente puede resultar insuficiente para SEO. | Medio | Metadatos, Open Graph, canonical, sitemap y datos estructurados en `Task/016`; si no basta, se reconsidera [ADR-005](../adr/ADR-005-markdown-content.md). | Abierto |
| R-08 | El entorno local no tiene copia de seguridad: `docker compose down -v` destruye la base de datos y los objetos de MinIO sin recuperación posible. | Alto | **Resuelto** por `Task/004`, aprobada el 2026-07-31: existe un procedimiento de respaldo con integridad verificada por SHA-256 y **restauración demostrada** en entorno aislado para los tres servicios, incluidos metadatos y tags de MinIO. Ver [runbook de backup](../runbooks/local-backup-and-recovery.md). Queda el riesgo residual **R-11**. | **Cerrado** (2026-07-31) |
| R-11 | El backup es **manual**: si nadie lo ejecuta, se pierde todo lo hecho desde la última copia. | Medio | Política de retención en el [runbook](../runbooks/local-backup-and-recovery.md) §11, que exige backup antes de toda operación destructiva. La automatización programada queda fuera del alcance de `Task/004`. | Abierto |
| R-12 | Los artefactos de respaldo son sensibles —incluyen los hashes de autenticación de Portainer— y se guardan **sin cifrar** en el equipo. | Medio | `local-backups/` ignorado por Git y documentado como sensible en el runbook, en `scripts/backup/README.md` y en el `.gitignore`. El cifrado queda fuera del alcance; se revisará en `Task/018`. | Abierto |
| R-13 | La copia de Portainer exige detener su contenedor: una interrupción anómala podría dejarlo parado. | Bajo | El arranque está dentro de un bloque `finally`: se ejecuta aunque la copia falle. Si aun así quedara parado, `docker start personal-blog-local-portainer` lo resuelve. | Abierto |
| R-09 | Portainer tiene acceso al socket del daemon de Docker y conserva **capacidad administrativa sobre el host**: puede crear, detener, eliminar y modificar contenedores, redes y volúmenes de este y de cualquier otro proyecto de la máquina. El montaje `:ro` protege el **archivo** del socket pero **no** convierte la Docker API en solo lectura, y la separación de redes **no** limita las acciones enviadas por el daemon. Agravante: conviven dos instancias de Portainer sobre el mismo daemon. | **Medio** | El riesgo se acepta únicamente porque Portainer es **local**, se publica en **`127.0.0.1`** y exige **autenticación propia**. **Regla vigente: no exponerlo nunca** a la red local ni a internet. Un control real de solo lectura exigiría un **socket proxy** o una política de autorización adicional, fuera del alcance de `Task/003`; se propone evaluarlo en `Task/018`. Detalle: [runbook §2.1](../runbooks/local-environment.md). | Abierto |
| R-10 | Las etiquetas de imagen fijadas envejecen y acumulan vulnerabilidades sin corregir. | Medio | Escaneo de imágenes en `Task/018-Endurecimiento-de-Seguridad`; validación del Compose en cada cambio en `Task/021-CI-Infraestructura`. | Abierto |
| R-14 | Las dependencias **transitivas** del backend no están bloqueadas: dos instalaciones en fechas distintas pueden traer versiones indirectas distintas. **Comprobado el 2026-08-11:** la imagen resolvió `starlette 1.6.0` y el entorno de Windows, instalado el 2026-08-01, tiene `starlette 1.3.1`. | Medio | Las dependencias directas están fijadas con `==` en `pyproject.toml` y `requirements.txt`, y `pip check` forma parte de las validaciones. Mientras el riesgo siga abierto, el `Dockerfile` instala con `pip install -r requirements.txt`, **sin `--require-hashes` ni `--no-deps`**, que serían incoherentes con un archivo sin hashes y sin transitivas. El bloqueo completo con hashes, resuelto en Linux, se añade en `Task/020-CI-Backend`. | Abierto (`Task/005`) |
| R-15 | La imagen base del backend (`python:3.12.13-slim`) envejece y acumula vulnerabilidades sin corregir. | Medio | Misma naturaleza que R-10. Escaneo de la imagen en `Task/018` y verificación en CI en `Task/020`. | Abierto (`Task/005`) |
| R-17 | Una práctica escrita puede no aplicarse: el ciclo **RED → GREEN** es fácil de saltarse si nadie exige la evidencia, y las pruebas acabarían escribiéndose después del código. | Medio | La evidencia de RED y GREEN es un **criterio de la Definition of Done** (B-2 y B-3), no una recomendación: sin ella la tarea no puede marcarse `Lista para validación`. `Task/020-CI-Backend` podrá reforzarlo automáticamente. Detectado en `Task/005.1`. | Abierto |
| R-18 | El coste de escribir primero la prueba puede empujar a **matrices superficiales** que aparenten cumplimiento sin cubrir edge cases ni casos negativos. | Bajo | La matriz obligatoria exige explícitamente edge cases, errores y seguridad ([BACKEND_TESTING_STRATEGY](BACKEND_TESTING_STRATEGY.md) §6), y la revisión del usuario es el control final. Detectado en `Task/005.1`. | Abierto |
| R-16 | El `.env` real del entorno local **conserva las contraseñas de ejemplo** `change-me-local-postgres` y `change-me-local-minio`, publicadas en `.env.example` desde `Task/003`: las credenciales locales de PostgreSQL y MinIO son, de hecho, públicas. | **Bajo** | Acotado porque los tres servicios se publican solo en `127.0.0.1` y no son alcanzables desde la red. Rotar la contraseña de PostgreSQL **no exige recrear el volumen ni la base**: se cambia la del rol existente con `ALTER ROLE` y se actualiza el `.env` de forma coordinada — procedimiento completo en el [reporte de `Task/005`](../task-reports/TASK-005-report.md) §6.1. **MinIO se trata por separado:** su credencial raíz procede de variables de entorno del contenedor, no de un rol almacenado, por lo que su rotación **no** sigue el mismo procedimiento. La rotación **queda a decisión del usuario** y no se ejecutó en `Task/005`. Detectado en `Task/005`. | Abierto |

### Riesgo introducido por `Task/005.6` — redacción de secretos en el log

| # | Riesgo | Impacto | Mitigación prevista | Tarea que lo valida | Estado |
| --- | --- | --- | --- | --- | --- |
| R-36 | **El log no tiene redacción automática de secretos.** `JsonLogFormatter` emite en `context` **todo** atributo propio del `LogRecord` y serializa las excepciones completas. La regla S-08 —«los logs no contienen contraseñas, tokens ni cadenas de conexión»— existe y se cumple hoy, pero depende de que **quien registra el evento** no pase un valor sensible: no hay ningún mecanismo que lo impida. Una excepción de driver o un `extra` descuidado pueden filtrar una credencial. Reproducido en `Task/005.6` por inspección del formateador. | Medio | **Deliberadamente NO se corrige en `Task/005.6`**: construir una política de redacción completa —lista de claves sensibles, patrones de token y URL, redacción en mensaje, contexto y traza— es trabajo de observabilidad y endurecimiento, no de cierre de fundaciones. Mitigación vigente: `database_url` está excluida de `repr` y solo se expone por `database_url_safe`, verificado en el contenedor real (`blog_local:***@`); `ConfigurationError` nombra campos, nunca valores. | `Task/017` (observabilidad, correlation ID y política de log) y `Task/018` (endurecimiento de seguridad) | **Abierto** |

### Riesgo introducido por `Task/005.7` — concurrencia de la suite de integración

> **Abierto y vigente** desde la aprobación de `Task/005.7` el 2026-08-16.

| # | Riesgo | Impacto | Mitigación prevista | Tarea que lo valida | Estado |
| --- | --- | --- | --- | --- | --- |
| R-37 | **La suite de integración no es segura para ejecución concurrente sobre la misma base de datos** (`CERT-AUD-009`). Tres causas concretas, reproducidas por inspección en `Task/005.7`: (1) `tabla_de_pruebas` usa un **nombre fijo** —`prueba_transaccional_005_6`—, así que dos procesos se pisan la tabla y el `DROP` de uno rompe al otro; (2) `test_migrations` ejecuta **`alembic downgrade base` sobre el esquema compartido**, que revierte el esquema entero por debajo de cualquier otro test en vuelo; (3) las fixtures **mutan estado de proceso** —`os.environ["BLOG_DATABASE_URL"]`, `get_settings.cache_clear()`, `dispose_engine()`—, que es seguro entre procesos pero no entre hilos. | Medio | **Deliberadamente NO se corrige en `Task/005.7`.** Hoy no hay ejecución paralela oficial: `pytest-xdist` **no está instalado** y el único flujo de integración esperado es secuencial, así que el riesgo **no es explotable en el estado actual**. Construir aislamiento por trabajador —esquema o base por *worker*, nombres de tabla derivados del `worker_id`, aislamiento del estado de proceso— es diseño de CI, no cierre de fundaciones, y hacerlo ahora sería sobrediseñar sin un consumidor real. **Debe revisarse antes de habilitar cualquier ejecución paralela**, y la decisión de habilitarla es lo que activa este riesgo. | `Task/020-CI-Backend` — propietaria de la concurrencia de CI del backend | **Abierto** |

### Riesgos introducidos por `Task/005.2` — AWS Local Parity

> **Abiertos y vigentes** desde la aprobación de `Task/005.2` el 2026-08-15. Ninguno está
> cerrado. Detalle completo:
> [aws-local-parity.md](../architecture/aws-local-parity.md) §14.

| # | Riesgo | Impacto | Mitigación prevista | Tarea que lo valida | Estado |
| --- | --- | --- | --- | --- | --- |
| R-19 | El comportamiento del emulador AWS local difiere del de AWS real en detalles que solo aparecerían en producción. | Medio | La matriz de paridad nace entera en `No evaluada`; toda diferencia observada se registra; **AWS real es la autoridad final**. | `Task/025` → ETAPA 10 | **Abierto** |
| R-20 | **Falsa sensación de paridad:** un laboratorio en verde convence de que la nube funcionará, y la ETAPA 10 se aborda con exceso de confianza. | **Alto** | El estado «paridad completa» **no existe** en la matriz, a propósito. Vocabulario obligatorio que distingue *emulado* de *validado*. La pregunta «¿qué diferencia hay respecto a AWS real?» es obligatoria en cada bloque de infraestructura. | ETAPA 10 | **Abierto** |
| R-21 | Una actualización del emulador rompe la compatibilidad ya validada. | Medio | Versión **fijada**, nunca `latest` ni `nightly`. Actualizar se trata como cambio de infraestructura: revisar CHANGELOG y revalidar la matriz. | `Task/025`, `Task/026` | **Abierto** |
| R-22 | El emulador necesita **acceso al socket de Docker** para ejecutar Lambda: privilegio de nivel host, junto a Portainer. **Agrava R-09.** | **Alto** | Mismo tratamiento que **R-09**: solo local, nunca expuesto, compromiso = incidente de nivel **host**. Revisión del *networking* de Docker antes de implementar. Componente **C-12** en [security-boundaries](../architecture/security-boundaries.md) §8. | `Task/025`, `Task/018` | **Abierto** |
| R-23 | El endpoint local (puerto 4566 y rangos auxiliares) queda expuesto a la LAN o a internet por descuido. | **Alto** | Publicación restringida a `127.0.0.1`; prohibición explícita de exponerlo; verificación incluida en los runbooks de `Task/026`. | `Task/025`, `Task/026` | **Abierto** |
| R-24 | Un comando pensado para el laboratorio acaba ejecutándose **contra AWS real** por faltar el endpoint, o se usan credenciales AWS reales contra el emulador. Un `destroy` en ese estado sería el fallo más caro posible. | **Alto** | Guardas ***fail-closed*** obligatorias antes del primer `apply`: entorno explícito, endpoint explícito, verificación de *account id*, rechazo de credenciales reales y validación bloqueante del destino. Prohibido usar credenciales AWS reales contra el emulador. | `Task/025`, `Task/026` | **Abierto** |
| R-25 | El **camino crítico del proyecto** —Terraform + API Gateway v2 + Lambda + CloudWatch Logs— **no está cubierto por la suite oficial de compatibilidad Terraform del emulador**, verificado el 2026-08-15. Los servicios están documentados por separado; su combinación con Terraform no está demostrada upstream. | **Alto** | Es el objetivo explícito de `Task/025`. Si no se logra con fidelidad suficiente, esos recursos pasan a `AWS-only` en la matriz y se documenta la limitación, **sin fabricar sustitutos locales**. | `Task/025` | **Abierto** |
| R-26 | Acumular condicionales por entorno acaba creando **dos IaC distintas** disfrazadas de una sola. | Medio | Tabla **cerrada** de diferencias legítimas ([aws-local-parity](../architecture/aws-local-parity.md) §4.4). Cualquier diferencia fuera de ella se trata como defecto de diseño, no como configuración. | `Task/025`, revisión del usuario | **Abierto** |
| R-27 | Dependencia excesiva del emulador: se aplaza indefinidamente la validación contra AWS real. | Medio | El laboratorio es una **puerta**, no un destino. La ETAPA 10 sigue siendo obligatoria y sus criterios de salida no se relajan. | ETAPA 10 | **Abierto** |
| R-28 | **El emulador no aplica políticas IAM por omisión**: acepta cualquier credencial y deja pasar toda petición. Un rol puede validarse en local y ser incorrecto —insuficiente o excesivo— en AWS. | **Alto** | El laboratorio valida que un rol **se crea y se adjunta**, nunca que **autoriza**. La verificación de **mínimo privilegio** queda declarada **AWS-only**. | `Task/028`, `Task/032` | **Abierto** |

### Riesgos introducidos por `Task/005.3` — PostgreSQL de producción en VPS

> **Abiertos y vigentes** desde la aprobación de `Task/005.3` el 2026-08-15. **Ninguno está
> cerrado**: son consecuencia asumida de la decisión, no defectos pendientes. Detalle
> completo:
> [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) §16.

| # | Riesgo | Impacto | Mitigación prevista | Tarea que lo valida | Estado |
| --- | --- | --- | --- | --- | --- |
| R-29 | ***Single point of failure*.** Un solo VPS: si cae el host, el blog pierde su base de datos y queda sin contenido dinámico hasta la recuperación manual. | Medio | **Aceptado conscientemente.** Mitigado con backups fuera del host, restore probado, infraestructura reproducible y runbook de recuperación. **No se introduce alta disponibilidad**: su costo y complejidad no se justifican para un blog personal. | `Task/029`, `Task/026` | **Abierto** |
| R-30 | **Nueva superficie de ataque expuesta a Internet:** PgBouncer publicado y SSH en el host, más software —SO, PostgreSQL, PgBouncer— que envejece y acumula vulnerabilidades sin parchear. **El compromiso del VPS implica exposición de todos los datos del blog.** | **Alto** | Firewall *deny-by-default*; SSH solo por llave; servicios mínimos; **PostgreSQL nunca público**; TLS obligatorio con validación de certificado y **SCRAM-SHA-256**; política de parcheo definida en `Task/029`. Prohibido apoyarse en *security through obscurity*. Ver [security-boundaries](../architecture/security-boundaries.md) §9. | `Task/029`, `Task/018` | **Abierto** |
| R-31 | **Backup inexistente, corrupto o no restaurable.** El fallo silencioso clásico: existe un archivo, nadie lo ha restaurado nunca y el día del incidente no sirve. | **Alto** | Regla obligatoria: **un backup no está validado hasta haberse restaurado**. Verificación de integridad, restore en entorno controlado y procedimiento documentado — mismo estándar que `Task/004` alcanzó en local. | `Task/029`, `Task/026` | **Abierto** |
| R-32 | **Pérdida del VPS o del disco**, o **agotamiento de recursos**: un disco lleno detiene PostgreSQL y puede impedir el propio backup. | **Alto** | Backups **fuera del host** — una copia que solo vive en el VPS no protege de esto. Monitoreo de espacio y de recursos con alertas; dimensionamiento y política de crecimiento en `Task/029`. **Owner corregido en `Task/005.5`:** `Task/017` es observabilidad **local** y no cubre el VPS; el *baseline* lo construye `Task/029` y lo verifica `Task/040`. | `Task/029`, `Task/040` | **Abierto** |
| R-33 | **Agotamiento de conexiones**: una ráfaga de concurrencia de Lambda supera `max_connections` de PostgreSQL. Es la materialización de **R-03** en esta topología. | Medio | **PgBouncer** con pool limitado más ***Reserved Concurrency*** de Lambda aguas arriba. Los tres números —concurrencia, pool y `max_connections`— se derivan de **pruebas**, no de intuición. | `Task/029`, `Task/032` | **Abierto** |
| R-34 | **Latencia `Lambda ↔ VPS`.** La base de datos deja de estar en la misma región que el cómputo; cada consulta paga el RTT y una petición HTTP suele hacer varias. | Medio | Selección de región del VPS teniendo en cuenta la región AWS, con **RTT medido**, no estimado. Regla explícita: no elegir un VPS lejano por ahorrar poco al mes. | `Task/029`, `Task/040` | **Abierto** |
| R-35 | **Error humano de operación.** Sin consola administrada que ponga barreras, un comando equivocado puede borrar datos, exponer un puerto o dejar el servicio caído. | Medio | Infraestructura reproducible con Terraform; runbooks escritos para cada operación; backups fuera del host como red de seguridad; regla vigente de no ejecutar operaciones destructivas sin autorización explícita. | `Task/026`, `Task/029` | **Abierto** |

### Riesgos introducidos por `Task/006.2` — arquitectura objetivo de producción

> **Abiertos y vigentes** desde la aprobación de `Task/006.2` el 2026-08-23. **Ninguno está
> cerrado**: son consecuencia asumida de las decisiones de observabilidad y de operación del
> VPS, no defectos pendientes. Detalle:
> [target-production-architecture.md](../architecture/target-production-architecture.md) —
> **Vigente** ·
> [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) — **Aceptada**.

| # | Riesgo | Impacto | Mitigación prevista | Tarea que lo valida | Estado |
| --- | --- | --- | --- | --- | --- |
| R-38 | **Dependencia de un tier gratuito de terceros.** El plano central de observabilidad es **Grafana Cloud**, y el objetivo inicial es su tier gratuito. Los límites y precios de un plan gratuito **cambian**, y pueden dejar de ser suficientes justo cuando el sistema ya depende de ellos para diagnosticar incidentes. | Medio | **Declarado explícitamente como preferencia presupuestaria, no como dependencia arquitectónica**: si deja de servir, se paga, se reduce el volumen de telemetría o se cambia de destino, **sin romper la arquitectura**. **Ninguna cifra comercial se persiste** en la documentación; las que se registren se marcan *«verificar en `Task/041` / antes de contratar»*. **D-19**. | `Task/041`, con aporte de `Task/027` | **Abierto** |
| R-39 | **La telemetría sale del perímetro del proyecto y puede llevar lo que no debe.** Alloy recolecta logs del host y de PostgreSQL y los envía a un tercero. Un log de driver, una consulta con parámetros o un volcado de error pueden contener credenciales o datos personales. **Es la misma familia que R-36, en otro plano y con destino externo.** | **Alto** | **Qué se recolecta es parte del diseño, no configuración** (**O-09**). Selección explícita de fuentes, sin recolección indiscriminada; regla **O-08** aplicada también aquí; verificación por muestreo en `Task/040`. La redacción en el log de aplicación sigue siendo de `Task/017` y `Task/018` (**R-36**). | `Task/029`, `Task/018`, `Task/040` | **Abierto** |
| R-40 | **Secretos del VPS mal gestionados.** El host necesita sus propios secretos —contraseñas de PostgreSQL y PgBouncer, clave privada del certificado, credencial de backup y credencial de Alloy— y **la herramienta todavía no está elegida** (**D-17**). Sin cifrado, custodia y rotación definidos, el compromiso del VPS entrega todo de golpe. | **Alto** | Modelo **ya cerrado**: cifrados, **clave fuera del repositorio**, descifrado local seguro, **nada versionado en claro** (regla V-08). La herramienta y la rotación se deciden en `Task/029`. **Mientras D-17 siga abierta no se instala nada ni se generan claves.** | `Task/029`, `Task/018` | **Abierto** |
| R-41 | **El agente de observabilidad compite por los recursos de PostgreSQL.** Alloy consume RAM, CPU y disco en la misma máquina que la base de datos, que es el componente que no puede degradarse (**R-32**). | Bajo | **Agente, no *stack***: se descarta autohospedar Grafana, Prometheus o Loki en el VPS. El dimensionamiento de `Task/029` contempla el consumo del agente, y `Task/040` verifica que el host sigue holgado. | `Task/029`, `Task/040` | **Abierto** |
| R-42 | ***Drift* de configuración del VPS.** Terraform **no configura el sistema operativo** por decisión (**D-18**), así que lo que hay dentro del host puede alejarse en silencio de lo documentado. Un cambio manual «temporal» sobrevive hasta el día de la reconstrucción, cuando ya nadie recuerda que existía. | Medio | Mecanismo **idempotente y reproducible** decidido en `Task/029` —Ansible, cloud-init o scripts—, runbooks escritos (`Task/026`), y verificación de que el host reconstruido coincide con lo documentado (`Task/040`). Refuerza la mitigación de **R-35**. | `Task/029`, `Task/026`, `Task/040` | **Abierto** |

---

## Tabla completa de tareas

| Tarea | Etapa | Repos | Estado |
| --- | --- | --- | --- |
| `Task/001-Inicializar-Workspace-y-Roadmap` | 00 | infra, frontend, backend | **Aprobada** |
| `Task/002-Definir-MVP-y-Arquitectura` | 00 | infra | **Aprobada** |
| `Task/003-Crear-Infraestructura-Local` | 01 | infra | **Aprobada** |
| `Task/004-Backups-y-Recuperacion-Local` | 01 | infra | **Aprobada** |
| `Task/005-Fundacion-Backend-FastAPI` | 02 | backend, infra (documentación) | **Aprobada** |
| `Task/006-Fundacion-Frontend-React` | 02 | frontend, infra (documentación) | **Aprobada** |
| `Task/007-Integracion-Local` | 02 | infra, frontend | **Aprobada** |
| `Task/008-Modelo-de-Datos` | 03 | backend, infra (documentación) | **Aprobada** |
| `Task/009-API-Publica` | 03 | backend, infra (documentación) | **Lista para validación** |
| `Task/010-Almacenamiento-Compatible-S3` | 03 | backend | Pendiente |
| `Task/011-Autenticacion-Administrativa` | 03 | backend | Pendiente |
| `Task/012-API-Administrativa` | 03 | backend | Pendiente |
| `Task/013-Sistema-de-Diseno` | 04 | frontend | Pendiente |
| `Task/014-Sitio-Publico` | 04 | frontend | Pendiente |
| `Task/015-Panel-Administrativo` | 04 | frontend | Pendiente |
| `Task/016-SEO-Accesibilidad-y-Rendimiento` | 05 | frontend, backend | Pendiente |
| `Task/017-Observabilidad-Local` | 05 | backend, infra | Pendiente |
| `Task/018-Endurecimiento-de-Seguridad` | 05 | infra, frontend, backend | Pendiente |
| `Task/019-CI-Frontend` | 06 | frontend | Pendiente |
| `Task/020-CI-Backend` | 06 | backend | Pendiente |
| `Task/021-CI-Infraestructura` | 06 | infra | Pendiente |
| `Task/022-Validacion-Local-Production-Like` | 07 | infra, frontend, backend | Pendiente |
| `Task/023-Compatibilidad-FastAPI-Lambda` | 08 | backend | Pendiente |
| `Task/024-Artefacto-ZIP-Lambda` | 08 | backend | Pendiente |
| `Task/025-Terraform-Cloud` | 08 | infra | Pendiente |
| `Task/026-Runbooks-de-Despliegue` | 08 | infra | Pendiente |
| `Task/027-Configurar-Cuentas-y-Presupuestos` | 09 | infra | Pendiente |
| `Task/028-GitHub-OIDC-AWS` | 09 | infra | Pendiente |
| `Task/029-Preparar-PostgreSQL-Produccion-en-VPS` | 09 | infra | Pendiente |
| `Task/030-Desplegar-Amazon-S3` | 10 | infra | Pendiente |
| `Task/031-Desplegar-SSM-y-CloudWatch` | 10 | infra | Pendiente |
| `Task/032-Desplegar-AWS-Lambda` | 10 | infra | Pendiente |
| `Task/033-Desplegar-API-Gateway` | 10 | infra | Pendiente |
| `Task/034-Desplegar-Cloudflare-Pages` | 10 | infra, frontend | Pendiente |
| `Task/035-Configurar-DNS` | 10 | infra | Pendiente |
| `Task/036-Publicar-Primer-Contenido` | 10 | backend, frontend | Pendiente |
| `Task/037-Deploy-Automatico-Frontend` | 11 | frontend | Pendiente |
| `Task/038-Deploy-Automatico-Backend` | 11 | backend | Pendiente |
| `Task/039-Automatizar-Terraform` | 11 | infra | Pendiente |
| `Task/040-Validacion-Final-Produccion` | 12 | infra, frontend, backend | Pendiente |
| `Task/041-Proteccion-de-Costos` | 12 | infra | Pendiente |

---

## Estado de los repositorios

> **Cómo leer esta sección** (regla de [WORKFLOW §6.1](WORKFLOW.md), vigente desde
> `Task/005.6`). Lo de abajo es una **observación fechada**, no una afirmación permanente.
> El estado vivo de ramas y PR se consulta en Git y GitHub —`git fetch --prune`,
> `git ls-remote --heads origin "Task/*"`, `gh pr list`—, nunca leyendo este documento.

**Observado el 2026-08-18**, tras el cierre aprobado de `Task/006`:

- Las dos ramas `Task/006` —frontend e infra— nacieron **desde `main`**, con `HEAD == main`
  verificado inmediatamente después de crearlas.
- Ambas se integraron en `dev` con merge `--no-ff` y se publicaron en `origin`.
- Los pull request son **`Task/006-Fundacion-Frontend-React → main`** en los dos
  repositorios. **Ninguno usa `dev` como *head*** y **ninguno lo fusionó Claude**.
- Las ramas Task **locales** se eliminaron con `git branch -d`; las **remotas se conservan**:
  eliminarlas es decisión del usuario.
- `personal-blog-backend` **no participó**: sin rama Task, worktree limpio, en `main`.

Los SHA y las URL concretas se consultan en vivo con `git fetch --prune`,
`git ls-remote --heads origin "Task/*"` y `gh pr list`, según
[WORKFLOW §6.1](WORKFLOW.md).

**Observado el 2026-08-16**, tras la fusión de los PR de `Task/005.5` y su normalización, y
al crear las ramas de `Task/005.6`:

| Repositorio | Ramas locales | Ramas remotas | `main` | `dev` | `main` y `dev` |
| --- | --- | --- | --- | --- | --- |
| `personal-blog-infra` | `main`, `dev`, `Task/005.6-...` | `main`, `dev` — **ninguna rama `Task/*`** | `bd0aaf5` | `2819f6c` | **Sincronizadas** — `git diff main dev` vacío |
| `personal-blog-backend` | `main`, `dev`, `Task/005.6-...` | `main`, `dev` — **ninguna rama `Task/*`** | `72c8adc` | `1e20839` | **Sincronizadas** — `git diff main dev` vacío |
| `personal-blog-frontend` | `main`, `dev`, `Task/005.6-...` | `main`, `dev` — **ninguna rama `Task/*`** | `4132a65` | `7e89d2a` | **Sincronizadas** — `git diff main dev` vacío |

Las tres ramas `Task/005.5` se crearon **desde `main`**, con `HEAD == main` verificado
inmediatamente después. Los tres pull request fueron **`Task/005.5 → main`**; **ninguno fue
`dev → main`** y **ninguno lo fusionó Claude**. Las tres ramas `Task/005.6` se crearon
igualmente **desde `main`**, con `HEAD == main` verificado.

- `main` y `dev` están **publicadas** en GitHub en los tres repositorios y
  contienen el mismo contenido.
- Las ramas `Task/001-Inicializar-Workspace-y-Roadmap` fueron **eliminadas** local y
  remotamente tras integrarse mediante los pull requests `#1`.
- Los PR de `Task/001` se integraron desde la rama `Task/001` directamente hacia `main`,
  lo que dejó `main` y `dev` con el mismo contenido pero distintos commits de merge. Esa
  divergencia formal se **normalizó al inicio de `Task/002`** con un merge `--no-ff` de
  `origin/main` dentro de `dev`, publicado en los tres repositorios.
- `Task/002` se ejecutó **solo en `personal-blog-infra`**. Tras su aprobación se
  integró en `dev`; el PR `#2` histórico usó `dev → main`, fue fusionado por el
  usuario y después se normalizó `dev`.
- A partir de `Task/002.1`, el flujo vigente cambia: cada PR de cierre debe usar
  `Task/<nombre> → main`; `dev → main` deja de ser el flujo ordinario.
- `Task/002.1-Configurar-Claude-Code` fue aprobada explícitamente por el usuario.
  Su PR `#3` fue **fusionado** por el usuario (commit `dbb41aa`) y la rama Task se
  eliminó local y remotamente. La normalización posterior integró `main` en `dev`
  mediante el merge `cca847c`.
- `Task/003-Crear-Infraestructura-Local` se creó desde `dev` **solo en
  `personal-blog-infra`**: la tarea no modifica frontend ni backend.
- `Task/003` fue **aprobada** el 2026-07-29. Su PR `#4` fue **fusionado** por el usuario el
  2026-07-31 (commit `966db01`), la rama Task se eliminó local y remotamente, y la
  normalización posterior integró `main` en `dev` mediante el merge `708a71e`.
- `Task/004-Backups-y-Recuperacion-Local` se creó desde `dev` **solo en
  `personal-blog-infra`**: la tarea no modifica frontend ni backend. Fue **aprobada** el
  2026-07-31; su cierre la integró en `dev` con merge `--no-ff`, publicó la rama Task y
  abrió el PR `Task/004 → main`. El usuario **fusionó** ese PR (`#5`, commit `c86d47e`) y
  eliminó la rama remota. La rama Task ya no existe ni local ni remotamente.
- La **normalización posterior** se ejecutó el 2026-08-01: `main` se integró en `dev` con el
  merge `5f09e22` y se publicó. `dev` y `main` tienen ahora el mismo contenido y el commit
  de `main` forma parte del historial de `dev`.
- `Task/005-Fundacion-Backend-FastAPI` se creó el 2026-08-01 desde `dev` en
  **`personal-blog-backend`** (implementación) y en **`personal-blog-infra`** (solo
  documentación de gobierno). Fue **aprobada** el 2026-08-12; su cierre creó los commits,
  integró la rama en `dev` con merge `--no-ff`, publicó `dev` y la rama Task, y abrió el
  pull request `Task/005 → main` en cada repositorio. La rama Task local se eliminó con
  `git branch -d`. *(Corregido en `Task/005.6`: esta viñeta afirmaba «**Los PR siguen
  abiertos**», contradiciendo a la viñeta siguiente y a la tabla de `Task/005`, que
  registran su fusión el 2026-08-13. Se elimina la contradicción, no la historia: el
  desenlace real está en la viñeta siguiente.)*
- **No se creó rama `Task/005` en `personal-blog-frontend`**: la tarea no lo modifica. El
  frontend permanece en `main`, con el árbol limpio.
- **Normalización completada el 2026-08-13.** El usuario fusionó los PR `#2` (backend, merge
  `db6ab18`) y `#6` (infra, merge `af8a04c`) y eliminó las ramas remotas. Después se integró
  `main` en `dev` con merge `--no-ff` en ambos repositorios y se publicó: `main` y `dev`
  tienen el mismo contenido y el commit de merge de `main` forma parte del historial de `dev`.
- `Task/005.1-Formalizar-TDD-Backend` se creó el 2026-08-13 desde `dev` **solo en
  `personal-blog-infra`**. Es mantenimiento documental, **no cuenta** en las 41 tareas y no
  modifica ningún otro repositorio. Fue **aprobada** el 2026-08-13; su cierre creó el commit,
  integró la rama en `dev` con merge `--no-ff`, publicó `dev` y la rama Task, y abrió el
  pull request `Task/005.1 → main`. La rama Task local se eliminó con `git branch -d`.
- El diagrama `images/Infraestructura.png`, **preexistente y agregado por el usuario**, se
  versionó durante ese cierre con su autorización explícita. No es un entregable de
  `Task/005.1` y no se modificó. **Versionar un diagrama no crea ningún recurso cloud.**
- **PR `#7` fusionado y normalización completada (2026-08-15).** El usuario fusionó
  `Task/005.1 → main` (merge commit **`2f56a13`**, `mergedAt = 2026-08-16T00:25:21Z` UTC) y
  eliminó la rama remota. Verificado con `gh pr view 7` y con
  `git ls-remote --heads origin "Task/*"`, que **no devuelve ninguna rama**. Después se
  integró `main` en `dev` con el merge `--no-ff` **`4e6bfaa`** y se publicó: `git diff main dev`
  está **vacío** y `2f56a13` es **ancestro de `dev`**.
- **Backend y frontend verificados el 2026-08-15**, sin modificarlos: `fetch --prune`,
  `main` y `dev` ya al día, `dev..main` **vacío** en ambos, `git diff main dev` **vacío**,
  árboles limpios y rama activa `main`. **No se creó rama `Task/005.2` en ninguno de los
  dos:** la tarea no los modifica.
- `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` se creó el 2026-08-15 desde `dev`
  normalizado (`4e6bfaa`), **solo en `personal-blog-infra`**. Es mantenimiento de
  arquitectura y gobierno documental: **no cuenta** en las 41 tareas y **no altera el
  avance**. Fue **aprobada** el 2026-08-15; su cierre creó el commit, integró la rama en
  `dev` con merge `--no-ff` (`a61ecbf`), publicó `dev` y la rama Task, y abrió el pull
  request `Task/005.2 → main` (**`#8`**). La rama Task local se eliminó con `git branch -d`.
- **PR `#8` fusionado y normalización completada (2026-08-15), por el usuario.** Merge commit
  **`5583947`**, `mergedAt = 2026-08-16T01:23:02Z` UTC; rama remota eliminada. El usuario
  sincronizó `main` y `dev` y publicó `dev` (`a563de6`, `Merge branch 'main' into dev`).
  **Verificado el 2026-08-15 al iniciar `Task/005.3`:** `gh pr view 8` devuelve `MERGED`,
  `git ls-remote --heads origin "Task/*"` **no devuelve nada**, `dev..main` está **vacío** y
  `git diff main dev` está **vacío**.
- **Backend y frontend verificados de nuevo el 2026-08-15**, sin modificarlos: `fetch --prune`,
  `main` y `dev` al día, `dev..main` **vacío** en ambos, `git diff main dev` **vacío**, árboles
  limpios y rama activa `main`. **No se creó rama `Task/005.3` en ninguno de los dos.**
- `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` se creó el 2026-08-15 desde `dev`
  normalizado (**`a563de6`**), **solo en `personal-blog-infra`**. Es mantenimiento de
  arquitectura y gobierno documental: **no cuenta** en las 41 tareas y **no altera el
  avance**. Fue **aprobada** el 2026-08-15; su cierre creó el commit, integró la rama en
  `dev` con merge `--no-ff` (`bf31ebc`), publicó `dev` y la rama Task, y abrió el pull
  request `Task/005.3 → main` (**`#9`**). La rama Task local se eliminó con `git branch -d`.
- **PR `#9` fusionado y normalización completada (2026-08-15).** El usuario fusionó
  `Task/005.3 → main` (merge commit **`181c634`**, `mergedAt = 2026-08-16T03:56:08Z` UTC) y
  eliminó la rama remota. Verificado con `gh pr view 9` y `git ls-remote --heads origin
  "Task/*"`, que **no devuelve ninguna rama**. Como el merge del PR existía **solo en
  `main`**, se integró `main` en `dev` con el merge `--no-ff` **`9dfbc10`** y se publicó:
  `main` es **ancestro de `dev`** y `git diff main dev` está **vacío**.
- `Task/005.4-Corregir-Base-Ramas-Task-Main` se creó el 2026-08-15 **desde `main`**
  (**`181c634`**), **solo en `personal-blog-infra`**. Es **la primera rama Task del
  proyecto creada desde `main`** y la evidencia del invariante que ella misma establece:
  al crearla, `HEAD == main == 181c634`, distinto de `dev` (`9dfbc10`). Es mantenimiento de
  gobierno: **no cuenta** en las 41 tareas y **no altera el avance**. Fue **aprobada** el
  2026-08-15; su cierre creó el commit, integró la rama en `dev` con merge `--no-ff`, publicó
  `dev` y la rama Task, y abrió el pull request `Task/005.4 → main` (**`#10`**).
- **PR `#10` fusionado y normalización completada (2026-08-16).** El usuario fusionó
  `Task/005.4 → main` (merge commit **`cc90b96`**, `mergedAt = 2026-08-16T04:20:19Z` UTC) y
  eliminó la rama remota. Verificado con `gh pr view 10` —devuelve `MERGED`— y con
  `git ls-remote --heads origin "Task/*"`, que **no devuelve ninguna rama**. `main` está
  integrada en `dev` (`f2eb330`): `git diff main dev` **vacío** y `main` **ancestro de
  `dev`**.
- `Task/005.5-Alinear-Planificacion-Tras-Auditoria` se creó el 2026-08-16 **desde `main`**
  en **los tres repositorios** —infra (`cc90b96`), backend (`db6ab18`) y frontend
  (`144a401`)—, con `HEAD == main` verificado en cada uno. Es la **segunda tarea creada
  desde `main`** y la primera que aplica el invariante en los tres repositorios a la vez.
  Es mantenimiento de gobierno y planificación: **no cuenta** en las 41 tareas y **no altera
  el avance**. Fue **aprobada** el 2026-08-16; su cierre creó el commit en cada repositorio,
  integró la rama en `dev` con merge `--no-ff`, publicó `dev` y la rama Task, y abrió el
  pull request `Task/005.5 → main` en los tres. La rama Task local se eliminó con
  `git branch -d`.
- **Los tres PR de `Task/005.5` fueron fusionados por el usuario.** *Observado el
  2026-08-16 con `gh pr list`:* `#11` (infra), `#3` (backend) y `#2` (frontend), los tres
  `MERGED`. `main` quedó en `bd0aaf5` · `72c8adc` · `4132a65`, se integró en `dev` y se
  publicó (`2819f6c` · `1e20839` · `7e89d2a`). `git ls-remote --heads origin "Task/*"` **no
  devuelve ninguna rama**, `git diff main dev` está **vacío** y `main` es **ancestro de
  `dev`** en los tres repositorios.
- `Task/005.6-Cerrar-Fundaciones-Tras-Mega-Auditoria` se creó el 2026-08-16 **desde `main`**
  en **los tres repositorios** —infra (`bd0aaf5`), backend (`72c8adc`) y frontend
  (`4132a65`)—, con `HEAD == main` verificado en cada uno. Es la **tercera tarea creada
  desde `main`**. Es mantenimiento transversal de fundaciones: **no cuenta** en las 41
  tareas y **no altera el avance**. Fue **aprobada** el 2026-08-16; su cierre creó el commit
  en cada repositorio, integró la rama en `dev` con merge `--no-ff`, publicó `dev` y la rama
  Task, y abrió el pull request `Task/005.6 → main` en los tres. La rama Task local se
  eliminó con `git branch -d`.

---

## Notas de estado

- **`Task/005` produce el primer código de aplicación del proyecto:** `personal-blog-backend`
  ya contiene una aplicación FastAPI que arranca, expone `/health` y OpenAPI, se conecta al
  PostgreSQL local y gestiona su esquema con Alembic. Está **`Aprobada`** desde el
  2026-08-12. *(El código React llegó después, con `Task/006`; ver la nota siguiente.)*
- **Correcciones del 2026-08-11, en la misma rama y sin commit:** el log emite ahora UTC
  explícito —antes el formato dependía del sistema operativo— con 9 pruebas deterministas
  comprobadas en Windows y en Docker; la advertencia de `starlette.testclient` se resolvió
  cambiando `httpx` por `httpx2` en las dependencias de desarrollo, sin silenciar nada en
  `pyproject.toml`, de modo que `pytest -W error` termina con **0 warnings y sin ningún
  filtro** en los dos entornos; se rectificó la afirmación errónea de que rotar la contraseña de
  PostgreSQL obliga a recrear su volumen; y se verificó que el `Dockerfile` es coherente con
  **R-14**. **El avance global no cambia.**
- **`Task/006` produce el primer código de interfaz del proyecto:**
  `personal-blog-frontend` ya contiene una aplicación React que monta, enruta, valida su
  configuración de entorno al arrancar y dispone de un cliente HTTP común con modelo de
  error. Está **`Aprobada`** desde el 2026-08-18, lo que lleva el avance a **6 de 41 (15 %)**
  y la ETAPA 02 a **2 de 3**. Su alcance **no** incluye sistema de diseño, páginas del sitio
  público, panel administrativo, autenticación ni consumo real del API.
- **Defecto corregido durante la revisión de `Task/006`:** el cliente HTTP declaraba `304`
  entre los estados exitosos sin cuerpo, pero el flujo evalúa `!response.ok` antes de
  consultarlos, así que `304` —que no es 2xx— jamás llegaba allí. La entrada era
  inalcanzable y describía un comportamiento inexistente. `304` no figura en
  [api-contracts.md](../architecture/api-contracts.md) §8 y el proyecto no hace peticiones
  condicionales: se retiró del conjunto y quedó **prueba de regresión permanente**.
- **La funcionalidad del blog sigue sin empezar:** no hay modelo de datos, ni endpoints de
  contenido, ni autenticación. Llegan a partir de `Task/008`.
- **`Task/003` produjo el primer artefacto ejecutable del proyecto:** un
  `docker-compose.yml` con PostgreSQL, MinIO y Portainer CE, **aprobado** y fusionado en
  `main`.
- **`Task/004` añade el respaldo y la recuperación local:** 5 scripts PowerShell y un
  runbook, **aprobados**. La restauración se **probó realmente** en un entorno temporal
  aislado y los tres servicios se recuperaron con sus datos íntegros. En MinIO se
  verifican **contenido, metadatos y tags** de la versión actual de cada objeto; el
  historial de versiones queda fuera del alcance y se detecta explícitamente.
- Con `Task/004`, la **ETAPA 01 queda completada** (2 de 2 tareas) y el avance global
  pasa a **4 de 41 (10 %)**.
- **Ningún backup real se versiona:** `local-backups/` está ignorado por Git.
- **No existe Terraform** en ningún repositorio. Ni `Task/005.2` ni `Task/005.3` crearon
  ningún archivo `.tf`: solo documentan cómo se escribirá en `Task/025` y `Task/029`.
- **No se ha creado ningún recurso cloud** ni ninguna cuenta en proveedores. **`Task/005.3`
  no contrató ningún VPS**, no instaló PostgreSQL ni PgBouncer, no creó certificados, claves,
  usuarios SSH ni reglas de firewall, y no ejecutó `pg_dump`.
- **`Task/006.2` tampoco crea nada.** Es documental: **0 recursos AWS, 0 recursos Cloudflare,
  0 cuentas de Grafana Cloud, 0 VPS, 0 buckets, 0 parámetros SSM, 0 roles IAM, 0 Terraform**.
  **No se instaló Grafana Alloy, ni Ansible, ni SOPS, ni age**, y **no se generó ninguna
  clave de cifrado**. La imagen `images/Infraestructura.png` **no se modificó**: sigue siendo
  la que el usuario publicó en el commit `d08fe27`.
- **`ADR-008` está `Aceptada`** desde el 2026-08-23, al aprobarse `Task/006.2`. Es el
  **octavo ADR** del proyecto. Registra la observabilidad de producción —**CloudWatch
  mínimo** + **Grafana Cloud** con **Grafana Alloy** en el VPS— y modifica **una sola fila**
  de `ADR-003`, la de «Logs y métricas»; el resto de ADR-003 permanece **íntegro y
  vigente**, incluida la exclusión de **ECR** y el empaquetado de Lambda por **ZIP**.
- **Aceptar ADR-008 no autoriza a implementarlo.** No existe cuenta de Grafana Cloud, ni
  Alloy instalado, ni integración con CloudWatch: cada pieza es de su tarea propietaria
  —`Task/029`, `Task/031`, `Task/040`, `Task/041`— y exige autorización explícita del
  usuario.
- **Floci no está instalado.** `Task/005.2` y `Task/005.3` son documentales: no se descargó
  ninguna imagen, no se levantó ningún contenedor, no se modificó `docker-compose.yml` y no
  se ejecutó ningún comando de Terraform ni de AWS CLI.
- **El backend y el frontend no se han tocado en ninguno de los dos mantenimientos.**
  `Task/005.3` **no modifica** `DATABASE_URL`, SQLAlchemy ni psycopg: la abstracción ya
  existente es precisamente lo que permite cambiar el destino de la base de datos **sin tocar
  código**.
- `Task/002` definió el **alcance del MVP y la arquitectura**, y fue **aprobada**. Con
  ella, la **ETAPA 00 queda completada** (2 de 2 tareas).
- ADR-001 a ADR-005 están todos en estado **Aceptada**. Ni `Task/003` ni `Task/004`
  crearon ADR nuevos: sus decisiones son de implementación local y reversibles. D-05
  quedó **Resuelta** con **Traefik v3** al aprobarse `Task/003`.
- **`ADR-007` está `Aceptada`** desde el 2026-08-15, al aprobarse `Task/005.3`. Es el
  séptimo ADR del proyecto. Cambia el destino de la **capa de datos de producción**: de
  PostgreSQL administrado a **PostgreSQL autogestionado en un VPS externo**, con
  **PgBouncer** delante y **PostgreSQL nunca expuesto a Internet**. **FastAPI permanece en
  AWS Lambda** y toda la arquitectura AWS sigue igual. Motivo principal: **costo**. Ver
  [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) —
  **Vigente**.
- **`ADR-007` modifica parcialmente a `ADR-003`**, solo su fila «Base de datos». ADR-003
  sigue **Aceptado y vigente**, y ADR-007 **refuerza** su exclusión de NAT Gateway. **Amazon
  RDS queda excluido** como destino de producción. Precisión registrada con documentación
  oficial de AWS: **NAT Gateway no es una consecuencia inherente de RDS** — aparece solo si
  una Lambda ya dentro de una VPC necesita salida IPv4 a Internet.
- **`ADR-006` está `Aceptada`** desde el 2026-08-15, al aprobarse `Task/005.2`. Es el sexto
  ADR del proyecto y el primero sobre estrategia de infraestructura.
- **Decisiones diferidas: 13 abiertas** desde `Task/005.5`, que añadió **D-15** —topología
  lógica de dominios, `Task/011`— y **D-16** —identidad del VPS hacia AWS, `Task/029`—.
  Resueltas: **D-05** (2026-07-29, Traefik v3),
  **D-14** (2026-08-15, **Floci** como laboratorio AWS local) y **D-01** (2026-08-15,
  PostgreSQL **autogestionado en VPS externo**). **D-01 se resolvió solo en cuanto al
  *modelo***: la selección de **proveedor, región y tamaño sigue pendiente** en `Task/029`.
  **D-06 sigue abierta:** `Task/005.3` no la toca. **D-10** amplía su alcance: el proyecto
  asume backup y restore completos.
- `Task/002.1-Configurar-Claude-Code` es mantenimiento de gobierno, está **Aprobada** y
  cerrada, y no forma parte de las 41 tareas del roadmap.
- **La ETAPA 08 amplía su alcance sin añadir tareas.** `Task/005.2`, **aprobada**, la reformula de
  *«Preparación Cloud sin Cuentas»* a **«Preparación Cloud + AWS Local Parity»**: la IaC
  pasará a ejecutarse de verdad contra un emulador AWS local en lugar de quedarse en
  `terraform fmt` + `validate`. **Los 4 identificadores y nombres de `Task/023`–`Task/026`
  no cambian**, el roadmap sigue teniendo **41 tareas** y **ninguna se renumeró**.
  Estrategia: [aws-local-parity](../architecture/aws-local-parity.md).
- La **ETAPA 01 está completada** (2 de 2 tareas aprobadas). La **ETAPA 02 — Fundaciones de
  las Aplicaciones** está **en curso**: **1 de 3** tareas aprobadas, tras la aprobación de
  `Task/005`.
- **`Task/029` cambia de alcance, no de número** (`Task/005.3`, aprobada). Pasa de
  `Task/029-Seleccionar-PostgreSQL-Administrado` a
  **`Task/029-Preparar-PostgreSQL-Produccion-en-VPS`**: selección del VPS con precios
  actuales, región y **RTT medido**, PgBouncer, TLS y SCRAM, firewall y SSH, backups fuera
  del host y restore probado. **El identificador `029` no cambia**, el roadmap sigue teniendo
  **41 tareas** y **ninguna se renumeró**.
- **Invariante Git corregido y VIGENTE desde el 2026-08-15 (`Task/005.4`, aprobada).** La documentación indicaba que
  las ramas Task debían crearse **desde `dev`**, e incluso prohibía partir de `main`. La
  regla vigente es la contraria: **toda rama `Task/<...>` nace desde `main` actualizado y
  limpio; `dev` NUNCA es base de una Task**, solo rama de integración. Motivo: `dev` acumula
  commits de integración que contaminarían la ascendencia de una tarea nueva y podrían
  filtrarse al PR `Task → main`. **El resto del workflow no cambia.** El historial de las
  tareas anteriores **no se reescribe**. Detalle:
  [WORKFLOW.md](WORKFLOW.md) §2.1.
- **`Task/006` está `Aprobada`** desde el 2026-08-18; `Task/007` sigue **Pendiente** y
  **no se ha iniciado**. `Task/005.1`, `Task/005.2`, `Task/005.3`,
  **`Task/005.4`** y **`Task/005.5`** están aprobadas, fusionadas y normalizadas.
  **`Task/005.6`** y **`Task/005.7`** están **aprobadas**. Las ramas `Task/006` de frontend
  e infra nacieron **desde `main`**, con `HEAD == main` verificado inmediatamente.
- **Cierre de fundaciones (`Task/005.6`, 2026-08-16, aprobada).** Se
  conciliaron **dos mega auditorías independientes** y se reprodujo cada hallazgo antes de
  decidir. Corregido: la política de finales de línea de los tres repositorios
  (`.gitattributes`, causa raíz `core.autocrlf=true` de nivel *system*); el aislamiento de
  la suite frente al `.env` del desarrollador; una **base de datos de pruebas dedicada** con
  guarda *fail-closed* de dos barreras; la distinción **skip / fail** de la integración; la
  verificación **semántica** de `commit` y `rollback`; el test de migraciones que habría
  caducado en `Task/008`; la cobertura de una configuración `production` **válida**; y el
  estado documental posterior a `Task/005.5`. **Ningún defecto arquitectónico**, **0
  funcionalidad nueva** y **`app/` sin cambios**. Deuda diferida con propietario:
  **R-36**.
- **Regla de gobierno nueva ([WORKFLOW §6.1](WORKFLOW.md), `Task/005.6`).** Los documentos
  versionados registran **estado duradero**; el estado transitorio de Git y GitHub —PR
  abierto o fusionado, rama remota, sincronización actual— se **consulta en vivo** y solo se
  archiva como **observación fechada**. Corrige la causa estructural por la que `STATUS.md`
  quedaba obsoleto tras cada fusión y evita tener que crear una tarea de mantenimiento
  (`006.1`, `007.1`, …) después de cada PR. **El invariante de ramas y el flujo de
  aprobación manual no cambian.**
- **Alineación posterior a la auditoría (`Task/005.5`, 2026-08-16, aprobada).**
  Se reprodujeron los hallazgos de dos auditorías independientes contra el repositorio, y se
  corrigieron los que se sostuvieron: la regla de ramas en backend y frontend, el estado
  documental de ADR-006 y ADR-007, el conteo de decisiones, la dependencia de `Task/025`
  respecto a `Task/024`, los *gates* de `Task/029` que exigían recursos futuros, el
  Terraform prometido en `Task/021`, la topología de dominios diferida hasta `Task/035`, y
  los propietarios ausentes de `S3Storage`, backup, identidad del VPS, certificado TLS,
  observabilidad del VPS, migraciones productivas, medios públicos y credenciales CI
  multi-provider. **No se creó ningún ADR nuevo, no se renumeró ninguna tarea y la
  arquitectura no cambió.** Decisiones nuevas: **D-15** y **D-16**, ambas **abiertas**.
- **El backend se desarrollará test-first a partir de `Task/008`.** `Task/005.1` formaliza la
  regla **RED → GREEN → REFACTOR** en
  [BACKEND_TESTING_STRATEGY](BACKEND_TESTING_STRATEGY.md), con matriz de casos previa,
  evidencia obligatoria y protección explícita de los tests frente a implementaciones
  incorrectas. Es mantenimiento: **no altera el avance**.
- **Ningún secreto nuevo se ha versionado.** Se detectó, en cambio, que el `.env` local
  conserva las contraseñas de ejemplo publicadas: riesgo **R-16**, a decisión del usuario.
  Rotar la contraseña de PostgreSQL **no destruye datos**: se hace con `ALTER ROLE` sobre el
  rol existente, sin recrear el volumen. La rotación **no se ejecutó** en `Task/005`.

Detalle completo: [ROADMAP.md](ROADMAP.md) ·
[TASK-001](../tasks/TASK-001-initial-workspace-and-roadmap.md) ·
[Reporte TASK-001](../task-reports/TASK-001-report.md) ·
[TASK-002](../tasks/TASK-002-define-mvp-and-architecture.md) ·
[Reporte TASK-002](../task-reports/TASK-002-report.md) ·
[TASK-003](../tasks/TASK-003-create-local-infrastructure.md) ·
[Reporte TASK-003](../task-reports/TASK-003-report.md) ·
[TASK-004](../tasks/TASK-004-local-backups-and-recovery.md) ·
[Reporte TASK-004](../task-reports/TASK-004-report.md) ·
[TASK-005](../tasks/TASK-005-fastapi-backend-foundation.md) ·
[Reporte TASK-005](../task-reports/TASK-005-report.md) ·
[TASK-005.1](../tasks/TASK-005.1-formalize-backend-tdd.md) ·
[Reporte TASK-005.1](../task-reports/TASK-005.1-report.md) ·
[TASK-005.2](../tasks/TASK-005.2-document-floci-local-iac-strategy.md) ·
[Reporte TASK-005.2](../task-reports/TASK-005.2-report.md) ·
[TASK-005.3](../tasks/TASK-005.3-define-production-postgresql-vps.md) ·
[Reporte TASK-005.3](../task-reports/TASK-005.3-report.md) ·
[TASK-005.4](../tasks/TASK-005.4-correct-task-branch-base-main.md) ·
[Reporte TASK-005.4](../task-reports/TASK-005.4-report.md) ·
[TASK-005.5](../tasks/TASK-005.5-align-planning-after-audit.md) ·
[Reporte TASK-005.5](../task-reports/TASK-005.5-report.md)

Estrategia de infraestructura local aprobada en `Task/005.2`:
[aws-local-parity](../architecture/aws-local-parity.md) (**Vigente**) ·
[ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) (**Aceptada**)

Capa de datos de producción aprobada en `Task/005.3`:
[production-postgresql-vps](../architecture/production-postgresql-vps.md) (**Vigente**) ·
[ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) (**Aceptada**)

Documentos de producto y arquitectura producidos por `Task/002`:
[MVP_SCOPE](../product/MVP_SCOPE.md) · [USER_FLOWS](../product/USER_FLOWS.md) ·
[CONTENT_MODEL](../product/CONTENT_MODEL.md) ·
[software-architecture](../architecture/software-architecture.md) ·
[api-contracts](../architecture/api-contracts.md) ·
[non-functional-requirements](../architecture/non-functional-requirements.md) ·
[security-boundaries](../architecture/security-boundaries.md) ·
[open-decisions](../architecture/open-decisions.md)
