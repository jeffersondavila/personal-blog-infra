# TASK-012.1 — Exponer la auditoría para el dashboard

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/012.1-Exponer-Auditoria-Para-Dashboard` |
| **Nombre** | Exponer la auditoría para el dashboard |
| **Tipo** | **Mantenimiento funcional de la API administrativa.** **No cuenta** dentro de las 41 tareas y **no altera el avance** |
| **Estado** | **Aprobada** ✔ el 2026-09-05 |
| **Etapa de referencia** | ETAPA 03 — Dominio y Backend (amplía el contrato cerrado allí). Se ejecuta durante la ETAPA 04 |
| **Dependencia** | `Task/012-API-Administrativa` — **Aprobada** ✔ el 2026-09-03 |
| **Motivo** | Desbloquear **B-015-1**: `MVP_SCOPE.md` §3.3 exige que el dashboard muestre los *«últimos eventos de auditoría»* y **ninguna operación HTTP del contrato vigente permite leerlos** |
| **Repositorios involucrados** | `personal-blog-backend` (funcional) · `personal-blog-infra` (gobierno y contratos) |
| **Repositorio NO modificado** | `personal-blog-frontend` — **sin rama y sin cambios** |
| **Rama** | `Task/012.1-Exponer-Auditoria-Para-Dashboard` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base (backend)** | `ce166fb77472d73a142c8ac89942fcf83e52157d` |
| **SHA base (infra)** | `5a8f4c8e0fe6938c9b31905b7540abf1a0d1eb51` |
| **Fecha de inicio** | 2026-09-05 |
| **Última actualización** | 2026-09-05 (aprobación y cierre) |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/012.1-Exponer-Auditoria-Para-Dashboard` |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

Ambas ramas se crearon en **worktrees dedicados**, fuera de los tres repositorios, para no
perturbar el trabajo de definición de `Task/015` que vive en su propia rama:

```
C:\Users\jeffe\Downloads\Blog_Personal\.worktrees\backend-012.1
C:\Users\jeffe\Downloads\Blog_Personal\.worktrees\infra-012.1
```

Preflight ejecutado el 2026-09-05 tras `git fetch --prune origin`:

| Repositorio | `main == origin/main` | Árbol limpio antes de crear | Base usada |
| --- | --- | :---: | --- |
| `personal-blog-backend` | ✔ `ce166fb7` | ✔ | **`main`** |
| `personal-blog-infra` | ✔ `5a8f4c8e` | ✔ (en `main`; el árbol de `Task/015` es otra rama y no se toca) | **`main`** |

Validación inmediata dentro de cada worktree:

| # | Comprobación | backend | infra |
| --- | --- | --- | --- |
| 1 | Rama creada **desde `main`** con `git worktree add -b … main` | ✔ | ✔ |
| 2 | `git rev-parse HEAD` == `git rev-parse main` | ✔ `ce166fb7…` | ✔ `5a8f4c8e…` |
| 3 | `git rev-list --count main..HEAD` | ✔ `0` | ✔ `0` |
| 4 | `git status --short` | ✔ vacío | ✔ vacío |

**No se usó como base** `Task/015-Panel-Administrativo`, `dev`, el worktree con cambios sin
confirmar ni ninguna rama de mantenimiento anterior.

`personal-blog-frontend` **permanece exactamente donde estaba** y no recibe rama.

---

## 1. Objetivo

Exponer **una** operación administrativa autenticada de **solo lectura** que devuelva los
eventos de auditoría más recientes, para que el dashboard mínimo de `MVP_SCOPE.md` §3.3
pueda construirse por completo.

**Nada más.** No es la tarea de observabilidad (`Task/017`), no añade filtros, no añade
escritura y no relaja ninguna invariante de inmutabilidad.

## 2. Contexto

`Task/015-Panel-Administrativo` no puede implementar el dashboard mínimo. El bloqueo
**B-015-1** se reconstruyó contra el código ejecutable y no contra un informe previo.

### 2.1 Decision gate — los ocho puntos, verificados

| # | Punto | Veredicto | Evidencia |
| --- | --- | :---: | --- |
| 1 | La lectura de auditoría forma parte del MVP | **Cierto** | `MVP_SCOPE.md` §3.3: *«Alcance mínimo: conteo de contenido por tipo y estado, últimos elementos modificados y **últimos eventos de auditoría**»* |
| 2 | El modelo ya permite lectura | **Cierto** | `CONTENT_MODEL.md` §3.9: *«solo **se crea y se lee** — nunca se edita ni se elimina desde la aplicación»* |
| 3 | Existe índice adecuado | **Cierto** | `ix_audit_events_occurred_at`, creado en la migración `0002` y justificado en `data-model.md` §5 como *«Listado cronológico del historial»* |
| 4 | Falta la exposición HTTP | **Cierto** | `app/modules/audit/` no tiene capa `presentation`; `RegistroDeAuditoria` declara un solo método, `registrar`; el módulo no tiene `queries.py`; `routers_administrativos()` monta **siete** routers y ninguno es de auditoría |
| 5 | `Task/015` necesita esa exposición | **Cierto** | Sin ella su dashboard no alcanza el alcance mínimo, y `software-architecture.md` §5 prohíbe que el frontend acceda a PostgreSQL |
| 6 | No existe ya otra operación equivalente | **Cierto** | Recuento programático de los ocho routers administrativos: **26 patrones de ruta / 38 operaciones HTTP**, ninguna sobre `audit_events` |
| 7 | No es responsabilidad de `Task/017` | **Cierto** | `ROADMAP.md` le asigna repositorios **`backend, infra`** —sin `frontend`— y dependencias **`014, 015`**: diferirle un entregable de `Task/015` crearía una dependencia circular |
| 8 | No exige migración | **Cierto** | El índice ya existe; no se crea, altera ni elimina ninguna tabla, columna o índice |

Los ocho se sostienen: **`Task/012.1` es válida**.

### 2.2 Por qué esta tarea y no otra

`api-contracts.md` §14 se titula *«API administrativa — **cerrada en `Task/012`**»*.
Ampliar ese contrato es enmendar el entregable de `Task/012`, así que la corrección lleva su
número. Ampliar `Task/015` en su lugar contradiría `STAGE-04`, que declara
`personal-blog-frontend` **repositorio de toda la etapa**, y mezclaría dos Definitions of
Done —frontend y backend funcional con TDD estricto— en una tarea que ya tiene 18
superficies.

### 2.3 Hallazgo: dos afirmaciones vigentes se apoyan en una premisa falsa

**Debe registrarse antes de tocar nada** (`BACKEND_TESTING_STRATEGY.md` §9: *«Cuando se
detecte una contradicción entre requisito, arquitectura y test, hay que detenerse y
documentarla antes de cambiar ninguna expectativa»*).

| Afirmación vigente | Dónde | Premisa que usa | Realidad |
| --- | --- | --- | --- |
| *«Ninguna fuente pide exponer el historial por API en el MVP»* | Docstring de `test_no_se_expone_ninguna_ruta_de_auditoria`, en `tests/contract/test_contrato_administrativo.py` | Que no existe tal fuente | **`MVP_SCOPE.md` §3.3 sí la pide.** La premisa es falsa |
| **B-08** *«La auditoría sigue siendo solo-creación — No existe ninguna ruta `/admin/audit`, en ninguna forma»* | `security-boundaries.md` §12.1 | Mezcla **una invariante** (solo-creación) con **un hecho de superficie** (no hay ruta) | La invariante **sigue siendo cierta y no se toca**; el hecho de superficie deja de serlo |

`Task/012` no se equivocó al no exponerla —no era su alcance—, pero **justificó la ausencia
con una premisa que `MVP_SCOPE.md` contradice**. Esa es exactamente la causa
—`BACKEND_TESTING_STRATEGY.md` §9, motivo **2**: *«El test contradice explícitamente la
documentación vigente»*— que autoriza a modificar el test, y la razón de que la enmienda de
**B-08** sea un entregable de esta ficha y no un efecto colateral silencioso.

**Resultado tras implementar:** la suite completa reveló un **tercer** artefacto con la
misma premisa falsa, `tests/test_openapi.py::test_openapi_no_declara_endpoints_no_implementados`.
Los tres se enmendaron por el motivo canónico correspondiente, y los tres quedaron con un
assert **más restrictivo** que el original. Antes/después en el
[reporte](../task-reports/TASK-012.1-report.md) §7.

---

## 3. Dentro del alcance

- [x] Consulta de lectura en `app/modules/audit/infrastructure/queries.py`.
- [x] DTO administrativo de solo lectura en `app/modules/audit/presentation/schemas_admin.py`.
- [x] Router en `app/modules/audit/presentation/router_admin.py`, creado con
      `router_administrativo()` —sin seguridad nueva—.
- [x] Montaje del router en `routers_administrativos()` de `app/api/admin.py`.
- [x] Suite test-first completa (§7), con integración contra PostgreSQL real.
- [x] Enmienda de los tests vigentes que la nueva ruta invalida — resultaron **tres**, no dos (§2.3).
- [x] Enmienda de **B-08** en `security-boundaries.md`, separando la invariante del hecho de
      superficie.
- [x] Actualización de `api-contracts.md` §4, §11 y §14.1, más una subsección propia.
- [x] Actualización de `software-architecture.md` §3.3 (el módulo `audit` gana capa de
      presentación) y de `data-model.md` donde enumere lectores del historial.
- [x] Gobierno: ficha, reporte, `STATUS`, `ROADMAP`.

## 4. Fuera del alcance

| Fuera | Propietario |
| --- | --- |
| Filtros por `action`, `entity_type`, `entity_id`, actor o rango de fechas | Nadie lo pide; ampliable de forma compatible más adelante |
| Paginación por cursor, búsqueda, orden configurable | Fuera del MVP (`api-contracts.md` §5) |
| Exponer `ip_address`, `actor_id` o `event_metadata` | §5.2; revisable con un consumidor demostrado |
| Resolver el nombre del actor con `JOIN` a `administrators` | Sin consumidor: hay **un** administrador en el MVP |
| Cualquier escritura, modificación o borrado de `AuditEvent` | **Prohibido** — invariantes 16 y 16b |
| Cambiar cómo, cuándo o qué se audita | `Task/011` y `Task/012`, ya aprobadas |
| Correlation ID: cabecera concreta y propagación completa | `Task/017` |
| Retención, rotación o archivado del historial | Operación; sin propietario asignado |
| Privilegio mínimo sobre `audit_events` (invariante 16b) | `Task/018` |
| CORS efectivo y cabeceras de seguridad | `Task/018` |
| El dashboard React que lo consumirá | `Task/015` |
| Migraciones, modelos ORM, escritura de auditoría, módulos de contenido, auth | **No se tocan** |
| Frontend, Terraform, Docker Compose, MinIO, S3 | **No se tocan** |

---

## 5. Contrato propuesto

### 5.1 La operación

```http
GET /api/v1/admin/audit-events?page=1&page_size=12
```

| Aspecto | Valor | Fuente |
| --- | --- | --- |
| Método | **`GET` y solo `GET`** | Invariantes 16 y 16b: no hay `POST`, `PUT`, `PATCH` ni `DELETE` |
| Autenticación | **Sesión obligatoria** | `security-boundaries.md` B-01; `login` sigue siendo el único endpoint administrativo público |
| Postura común | La de `router_administrativo()`: `requiere_administrador`, `exigir_origen_permitido`, `sin_cache`, `rechazar_parametros_desconocidos` | `app/api/admin.py`. **No se inventa seguridad nueva** |
| `Origin` | **No se exige en `GET`.** `origen_permitido()` solo comprueba `POST`, `PUT`, `PATCH` y `DELETE`; un `GET` pasa por definición | `app/shared/security/origen.py`, `METODOS_QUE_CAMBIAN_ESTADO` |
| Caché | `Cache-Control: no-store` | `security-boundaries.md` B-13 |
| Query params | **Solo `page` y `page_size`**, con los valores ya vigentes (12 por defecto, 50 máximo, recorte sin error) | `api-contracts.md` §5; `ParametrosDePagina` |
| Parámetro desconocido | `422`, derivado de la propia operación | `app/api/query_params.py` (**D-009-C**) |
| Respuesta | `200` `Pagina[EventoDeAuditoria]` | `api-contracts.md` §5, envoltura única |
| Errores | `401 unauthenticated` · `422 validation_error` | `api-contracts.md` §7, §13.4 |

**Nombre de la ruta — `audit-events`, en `kebab-case` plural.** `api-contracts.md` §1 fija
*«Rutas: `kebab-case` en plural (`/book-reviews`)»*, y el recurso conceptual de
`CONTENT_MODEL.md` §3.9 es `AuditEvent`. **No colisiona** con ninguno de los 26 patrones
existentes. Se descartó `/admin/audit` —singular y no es el nombre del recurso— y se
descartó `/admin/dashboard`, que sería inventar un recurso que ninguna fuente define y que
acoplaría el contrato a una pantalla.

**Códigos que no se declaran**: `403` no puede darse en un `GET` (no hay comprobación de
`Origin`); `404` no aplica a una colección; `409` no existe sin escritura.

### 5.2 DTO — `EventoDeAuditoria`

Superficie **mínima**, campo a campo. Cada campo del contrato `v1` es permanente:
`api-contracts.md` §10 regla 2 impide retirarlo, y la regla 3 permite añadir uno opcional
más adelante. La asimetría manda: **ante la duda, fuera**. Es el mismo criterio con el que
§12 rechazó `access_expires_at`.

| Campo | Tipo | Nullable | Fuente | Por qué se expone |
| --- | --- | :---: | --- | --- |
| `id` | `UUID` | no | `audit_events.id` | Identidad estable de cada evento: el panel necesita una clave de lista que no dependa de la posición ni del texto. `CONTENT_MODEL.md` §3.9 ya lo declara atributo del recurso |
| `occurred_at` | `datetime` ISO 8601 UTC | no | `audit_events.occurred_at` | **Es «últimos»**: sin la fecha no hay orden cronológico que mostrar. `api-contracts.md` §1 fija el formato |
| `action` | `str` | no | `audit_events.action` | **Es «qué pasó»**. Catálogo cerrado de 15 acciones (`CONTENT_MODEL.md` §3.9) que el panel traduce a texto |
| `entity_type` | `str` | no | `audit_events.entity_type` | **Es «sobre qué»**. `content.*` no dice el tipo: lo dice esta columna (**D-012-N**) |
| `entity_id` | `UUID` | **sí** | `audit_events.entity_id` | Permite enlazar el evento con el elemento en el panel. Nulo en los eventos de sesión, que no afectan a ningún elemento |

**Cinco campos.** Con ellos una línea del dashboard se renderiza entera: *«2026-09-05 14:30
— se publicó un artículo — [abrir]»*.

#### Campos deliberadamente **no** expuestos

| Campo | Por qué no |
| --- | --- |
| `ip_address` | Dato personal y operativo que el dashboard no necesita para listar. **O-09** exige no exportar datos personales innecesarios y `security-boundaries.md` A-13 mantiene el historial libre de datos de terceros. Exponerlo ampliaría la superficie sin consumidor |
| `actor_id` | El MVP tiene **un** administrador (`MVP_SCOPE.md` §3): mostrar su propio identificador no informa de nada. Resolver el nombre exigiría un `JOIN` sin consumidor. Añadirlo el día que existan varios administradores es **compatible** |
| `event_metadata` | Aunque **D-012-O** garantiza metadatos mínimos y no sensibles, es un objeto **de forma libre**: fijarlo en `v1` congelaría una estructura que hoy varía por acción. `action` + `entity_type` + `entity_id` + `occurred_at` bastan para la línea del dashboard. No se exponen estructuras «por si acaso» |
| `request_id` | **Decisión ajustada, registrada como pregunta abierta** (§11). `api-contracts.md` §9 le da un propósito real —trazar una petición extremo a extremo—, pero ese propósito es de `Task/017`, que además todavía no ha fijado la cabecera, y hoy la columna es **nullable**. Añadirlo después es compatible; retirarlo, no. Se deja **fuera** salvo que el usuario indique lo contrario |

**Ningún campo del DTO transporta secretos, contraseñas, credenciales, tokens, huellas ni
claves de objeto.**

### 5.3 Paginación

La del proyecto, sin variante: `Pagina[EventoDeAuditoria]` con `items`, `page`, `page_size`,
`total`, `pages`; `page_size` 12 por defecto y **recorte** a 50, nunca error; `page` fuera de
rango devuelve `items` vacío con `200`; `total = 0` produce `pages = 0`.

### 5.4 Orden — `occurred_at DESC, id ASC`

**Por qué hace falta un desempate.** `occurred_at` tiene `server_default=func.now()`, y en
PostgreSQL `now()` es la marca de **inicio de la transacción**: dos eventos escritos en la
misma transacción comparten el instante exacto. Es la misma razón por la que la biblioteca
de medios desempata `created_at` (**D-H**) y por la que los listados desempatan
`published_at` (**D-009-F**): un `LIMIT`/`OFFSET` sobre un orden **no total** puede repetir u
omitir filas entre páginas.

**Por qué `id` y por qué ascendente.** `id` es la clave primaria: `UNIQUE NOT NULL`, que es
justo lo que convierte el orden en total. La dirección **ascendente** no es cosmética: es la
convención ya establecida en las tres decisiones previas —`published_at DESC, slug ASC`
(D-009-F), `updated_at DESC, slug ASC` (D-012-L), `created_at DESC, object_key ASC`
(medios)—. Como `id` es **UUID v4 generado en Python**, no es monótono y ninguna dirección
transporta significado cronológico; entre dos opciones equivalentes se elige la que ya usa
el proyecto. **Se descarta `id DESC`** por introducir una cuarta convención sin ganar nada.

### 5.5 Índice y migración — **ninguna**

| Comprobación | Resultado |
| --- | --- |
| ¿Existe índice para el orden principal? | **Sí**: `ix_audit_events_occurred_at`, creado en `alembic/versions/20260826_0002_modelo_de_datos_del_mvp.py` y justificado en `data-model.md` §5 como *«Listado cronológico del historial»* |
| ¿Sirve un índice ascendente para `ORDER BY … DESC`? | **Sí**: PostgreSQL recorre un B-tree en sentido inverso sin coste añadido |
| ¿Hace falta un índice compuesto `(occurred_at, id)`? | **No.** El desempate solo actúa entre filas que comparten instante —unas pocas—, y ordenarlas cuesta lo mismo que compararlas. Añadir un índice preventivo sería optimizar sin medir |
| ¿Se crea, altera o elimina alguna tabla, columna o índice? | **No** |

**Conclusión: sin Alembic, sin migración, sin índice nuevo.** Si durante la implementación
apareciera una razón medida para lo contrario, sería un hallazgo que se documenta **antes**
de ampliar el alcance.

---

## 6. Arquitectura

### 6.1 Precedente reutilizado, no inventado

**No se crea capa `application`.** El precedente es explícito y está escrito en el propio
código: `app/modules/media/infrastructure/queries.py` abre con *«Solo lectura, así que no
pasan por la capa `application`: mismo criterio **D-009-Q** que `Task/009` aplicó a las
consultas públicas»*. Una capa de aplicación que solo reenviara la llamada sería una
abstracción vacía, prohibida por **ADR-004** y por **M-06**.

**No se crea repositorio genérico.** Los módulos que se leen usan funciones de consulta
sueltas sobre la `Session`, no un repositorio: el repositorio existe donde hay escritura.

**No se toca la escritura.** `audit/domain/puertos.py`, `audit/domain/acciones.py`,
`audit/infrastructure/registro.py` y `audit/infrastructure/models.py` quedan **intactos**.

### 6.2 Archivos previstos

| Archivo | Acción | Precedente que copia |
| --- | --- | --- |
| `app/modules/audit/infrastructure/queries.py` | **Crear** | `app/modules/media/infrastructure/queries.py` — `contar_*` + `listar_*` con `ParametrosDePagina` |
| `app/modules/audit/presentation/__init__.py` | **Crear** | Los siete módulos con presentación |
| `app/modules/audit/presentation/schemas_admin.py` | **Crear** | `media/presentation/schemas_admin.py` — DTO Pydantic con `de_modelo()` |
| `app/modules/audit/presentation/router_admin.py` | **Crear** | `tags/presentation/router_admin.py`, cuyo `GET ""` es exactamente esta forma |
| `app/api/admin.py` | **Modificar** | Añadir el router a `routers_administrativos()`. Es el montaje central, y ampliarlo es parte natural del contrato |
| `tests/integration/test_api_admin_auditoria.py` | **Crear** | `tests/integration/test_api_admin_etiquetas.py` |
| `tests/contract/test_contrato_administrativo.py` | **Modificar** | Ver §7.4 |

**Nada más.** En particular no se tocan: modelos ORM, migraciones, escritura de auditoría,
módulos de contenido, `authentication`, CORS, cabeceras globales, frontend, Terraform,
Docker Compose, MinIO ni S3.

---

## 7. Seguridad e invariantes

### 7.1 Lo que queda explícito

| # | Invariante | Cómo se sostiene |
| --- | --- | --- |
| 1 | `AuditEvent` sigue siendo **inmutable** | Las guardas de `before_update` y `before_delete` de `Task/008` no se tocan. Invariantes 16 y 16b intactas |
| 2 | Esta tarea **solo añade lectura** | Una operación, `GET`. Sin `POST`, `PUT`, `PATCH` ni `DELETE` |
| 3 | **Leer auditoría no genera un `AuditEvent`** | `CONTENT_MODEL.md` §3.9: *«Las lecturas no se auditan»*; `USER_FLOWS.md` audita *«todo flujo administrativo que **modifica** datos»*. El router no recibe `RegistroDeAuditoria` |
| 4 | **No se crean eventos manualmente** por API | No existe ningún `POST`. Las escrituras siguen ocurriendo solo desde los casos de uso de `Task/011` y `Task/012` |
| 5 | **No se exponen secretos** | El DTO tiene cinco campos y ninguno los transporta. `security-boundaries.md` B-07 sigue garantizando que tampoco los guarda |
| 6 | **No se expone `ip_address`** | Excluido del DTO por diseño (§5.2), con prueba de contrato que lo fija |
| 7 | La sesión es obligatoria | `router_administrativo()`. Una prueba transversal recorre OpenAPI entera (B-01, B-02) |
| 8 | Respuestas **no cacheables** | `Cache-Control: no-store` (B-13) |
| 9 | El frontend **no accede a PostgreSQL** | Precisamente por eso existe esta operación (`software-architecture.md` §5) |

### 7.2 Enmienda de **B-08** — entregable, no efecto colateral

`security-boundaries.md` §12.1 B-08 dice hoy:

> **La auditoría sigue siendo solo-creación** — No existe ninguna ruta `/admin/audit`, en
> ninguna forma. Las guardas de inmutabilidad de `Task/008` quedan intactas.

Empaqueta **una invariante** con **un hecho de superficie**. La enmienda separa las dos:
la invariante —solo-creación, sin `PUT`, `PATCH`, `DELETE` ni `POST`, guardas intactas—
**se conserva palabra por palabra**; el hecho de superficie se sustituye por la descripción
exacta de lo que existe: **una** operación de solo lectura, autenticada, sin filtros y sin
`ip_address`.

**No se relaja ninguna regla de seguridad.** Se corrige una afirmación que dejó de ser
cierta, y se explica por qué la invariante que la motivaba sigue intacta.

`docs/task-reports/TASK-012-report.md` contiene la misma afirmación como **registro
histórico fechado**: no se reescribe (`WORKFLOW.md` §6.1).

---

## 8. Matriz test-first

**BACKEND TEST-FIRST LAW aplica íntegra** (`CLAUDE.md` §14;
`DEFINITION_OF_DONE.md` B-1…B-12): la matriz se cierra antes de escribir código, cada caso
demuestra **RED por la razón esperada** antes de la implementación mínima, y la suite entera
se ejecuta antes de declarar nada.

**En esta sesión no se escribe ninguna prueba.** Solo se define.

### 8.1 Contrato — sobre la especificación OpenAPI

| # | Caso | RED esperado | GREEN esperado |
| --- | --- | --- | --- |
| C-01 | La ruta `/api/v1/admin/audit-events` existe | `KeyError`: la ruta no está en `paths` | Presente |
| C-02 | Declara **solo** `get` | La ruta no existe | `{"get"}` |
| C-03 | Declara `security` | La ruta no existe | La declara, y la prueba transversal B-01 sigue verde |
| C-04 | Los query params declarados son exactamente `page` y `page_size` | La ruta no existe | Exactamente esos dos |
| C-05 | El esquema `EventoDeAuditoria` tiene **exactamente** los cinco campos aprobados | El esquema no existe | `{id, occurred_at, action, entity_type, entity_id}` |
| C-06 | El esquema **no** menciona `ip_address` | El esquema no existe | Ausente |
| C-07 | El esquema **no** menciona `metadata`, `event_metadata`, `actor_id` ni `request_id` | El esquema no existe | Ausentes |
| C-08 | La respuesta usa la envoltura `Pagina` del proyecto | El esquema no existe | `items`, `page`, `page_size`, `total`, `pages` |
| C-09 | Documenta la envoltura de error común | La ruta no existe | La documenta, como el resto del prefijo |
| C-10 | El conjunto de rutas es el del contrato **ampliado en una** | La ruta falta en el conjunto esperado | 11 públicas + 3 de acceso + **24** administrativas |

### 8.2 Autenticación

| # | Caso | RED | GREEN |
| --- | --- | --- | --- |
| A-01 | Petición anónima | `404` (la ruta no existe) | **`401 unauthenticated`** |
| A-02 | Cookie desconocida, caducada o revocada | `404` | `401 unauthenticated` |
| A-03 | Sesión válida | `404` | `200` |
| A-04 | La prueba transversal «todo `/admin/*` exige sesión» sigue verde | — | Verde, ahora recorriendo también esta ruta |

### 8.3 Datos — integración contra PostgreSQL real

| # | Caso | Precondición | Resultado esperado |
| --- | --- | --- | --- |
| D-01 | Sin eventos | tabla vacía — sesión preparada **sin** iniciar sesión, para que el acceso no audite | `200`, `items` vacío, `page = 1`, `page_size = 12`, `total = 0`, `pages = 0`. Verificado contra el endpoint real, con `count(*) == 0` comprobado antes del `GET` |
| D-02 | Un evento | 1 fila | `items` con 1, `total = 1`, `pages = 1` |
| D-03 | Varios eventos | 5 filas con instantes distintos | Orden **`occurred_at` descendente** |
| D-04 | Empate de instante | 3 filas con el **mismo** `occurred_at` | Desempate **`id` ascendente**, determinista y repetible |
| D-05 | Paginación estable con empates | 25 filas, varias empatadas | Las páginas 1 y 2 **no repiten ni omiten** ninguna fila |
| D-06 | `page_size` por defecto | 20 filas, sin parámetro | 12 elementos |
| D-07 | `page_size` por encima del máximo | `page_size=500` | **Se recorta a 50**, `200`, no error |
| D-08 | `page_size` inválido | `page_size=0` | `422` |
| D-09 | `page` inválido | `page=0`, `page=abc` | `422` |
| D-10 | Página fuera de rango | 3 filas, `page=99` | `200` con `items` vacío |
| D-11 | `total` y `pages` coherentes | 13 filas, `page_size=12` | `total = 13`, `pages = 2` |
| D-12 | Evento sin `entity_id` | evento de sesión | `entity_id` nulo, sin fallo de serialización |
| D-13 | Parámetro desconocido | `?actor=…` | `422` |
| D-14 | Eventos reales de los casos de uso vigentes | publicar un artículo y luego leer | El evento `content.published` aparece el primero |

### 8.4 Seguridad y ausencia de efectos

| # | Caso | Resultado esperado |
| --- | --- | --- |
| S-01 | **La lectura no produce un nuevo `AuditEvent`** | `SELECT count(*) FROM audit_events` **idéntico** antes y después del `GET` |
| S-02 | El cuerpo no contiene `ip_address` | Comprobado sobre el JSON entero, no solo sobre el esquema |
| S-03 | El cuerpo no contiene `actor_id`, `metadata` ni `request_id` | Ausentes en el JSON |
| S-04 | `Cache-Control: no-store` | Presente en la respuesta |
| S-05 | Un `GET` **sin** cabecera `Origin` funciona | `200`: la política vigente no exige `Origin` en lecturas |
| S-06 | Un `GET` con `Origin` no permitido funciona | `200`, por la misma razón. Documenta la política, no la cambia |
| S-07 | La inmutabilidad sigue garantizada | Las pruebas de `test_auditoria.py` siguen verdes, sin tocarlas |
| S-08 | No existe `POST`, `PUT`, `PATCH` ni `DELETE` en la ruta | `405` |

### 8.5 Regresión

Suite completa del backend; las pruebas de `Task/011` y `Task/012` intactas; la
especificación OpenAPI válida; `ruff` y `mypy` sin errores; migraciones aplican y revierten
**sin cambios** (no hay ninguna nueva).

### 8.6 Los dos tests vigentes que se enmiendan

| Test | Qué le pasa | Motivo autorizado |
| --- | --- | --- |
| `test_no_se_expone_ninguna_ruta_de_auditoria` | Afirma `"audit" not in ruta` para toda ruta. Su docstring dice *«Ninguna fuente pide exponer el historial por API en el MVP»* | **§9, motivo 2**: contradice `MVP_SCOPE.md` §3.3. **Se reemplaza, no se borra**, por una prueba más fuerte: la única ruta con `audit` es `/api/v1/admin/audit-events` y **declara exclusivamente `get`** |
| `test_la_especificacion_declara_exactamente_las_rutas_del_contrato` | `RUTAS_ADMINISTRATIVAS` no incluye la nueva | **§9, motivo 1**: el requisito cambió. Se añade **una** entrada; el resto del conjunto no se toca |

**Ningún assert se debilita.** El primero pasa de «no existe ninguna» a «existe exactamente
una y es de solo lectura», que es una condición **más** restrictiva sobre la superficie real.

---

## 9. Definition of Done

`DEFINITION_OF_DONE.md` §1 criterios 1–12, §3 *Tareas de backend* y §3 *Tareas de backend
funcional* (**B-1…B-12**):

| Criterio | Cómo se satisface |
| --- | --- |
| `ruff` y `mypy` sin errores | Compuerta obligatoria |
| `pytest` en verde | Suite entera, no solo la nueva |
| Migraciones aplican y revierten | **Sin migración nueva**; se comprueba que siguen funcionando |
| Imagen Docker construye | Compuerta obligatoria |
| `.env.example` | **Sin variables nuevas** |
| Cero *warnings* no documentados | Compuerta obligatoria |
| B-1 matriz previa | §8, cerrada antes de implementar |
| B-2 / B-3 evidencia RED y GREEN | Registrada en el reporte, caso por caso |
| B-4 refactor | Ejecutado o declarado innecesario con su razón |
| B-6 integración real | PostgreSQL real (`personal_blog_test`). **Nunca SQLite** |
| B-7 regresión completa | Suite entera antes de declarar la tarea lista |
| B-9 casos negativos | §8.2 y D-08, D-09, D-10, D-13 |
| B-10 seguridad | §8.4 |
| B-12 tests no modificados para acomodar código | §8.6: los dos cambios están justificados por motivo canónico y **refuerzan** el assert |
| Criterio 12 | Ningún documento persiste estado vivo de Git o GitHub |

---

## 10. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-1 | Enmendar una regla vigente de `security-boundaries.md` (**B-08**) puede leerse como relajar la seguridad | Pérdida de confianza en el documento | La invariante se conserva literal; solo cambia el hecho de superficie. La enmienda va acompañada de la prueba que la sostiene (§8.4 S-01, S-08) |
| R-2 | Modificar dos tests aprobados | Sospecha de acomodar el código | Motivo canónico citado (§9, motivos 1 y 2), y el assert resultante es **más** restrictivo, no menos |
| R-3 | Tentación de añadir filtros «ya que estamos» | Superficie `v1` permanente e irreversible | Alcance cerrado en §4; los filtros son ampliación compatible posterior |
| R-4 | La tabla `audit_events` crece sin límite y el listado se degrada | Latencia futura | Fuera de alcance por diseño: la retención es de operación. El índice cronológico existe y `LIMIT`/`OFFSET` acotan la consulta |
| R-5 | `Task/015` sigue bloqueada mientras esta tarea no se apruebe y fusione | Retraso de la ETAPA 04 | Alcance deliberadamente mínimo: una operación, cinco campos, sin migración |
| R-6 | Sin semilla local no hay administrador con el que probar en el navegador | Validación manual limitada | La integración se ejecuta contra PostgreSQL real con datos creados por la propia prueba. La semilla es de `Task/022` |

## 11. Preguntas abiertas

| # | Pregunta | Recomendación |
| --- | --- | --- |
| Q-1 | ¿`request_id` entra en el DTO `v1`? `api-contracts.md` §9 le da un propósito real —trazar extremo a extremo—, pero la cabecera concreta es de `Task/017`, la columna es nullable y **añadirlo después es compatible mientras que retirarlo no** | **No incluirlo ahora.** Decisión del usuario |

## 12. Deuda técnica pendiente

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | Filtros del historial por acción, tipo, elemento o rango de fechas | Sin propietario; ampliación compatible |
| 2 | Resolver el nombre del actor cuando exista más de un administrador | Sin propietario; fuera del MVP |
| 3 | Retención, rotación y archivado del historial | Operación |
| 4 | Privilegio mínimo sobre `audit_events` (invariante 16b) | `Task/018` |
| 5 | Cabecera concreta del correlation ID y su propagación | `Task/017` |

## 13. Archivos esperados

**Crear (backend):** `app/modules/audit/infrastructure/queries.py`;
`app/modules/audit/presentation/{__init__.py, schemas_admin.py, router_admin.py}`;
`tests/integration/test_api_admin_auditoria.py`.

**Modificar (backend):** `app/api/admin.py` (montaje);
`tests/contract/test_contrato_administrativo.py` (§8.6).

**Crear/modificar (infra):** esta ficha; `docs/task-reports/TASK-012.1-report.md`;
`docs/project-management/{STATUS.md, ROADMAP.md}`;
`docs/architecture/{api-contracts.md, security-boundaries.md, software-architecture.md,
data-model.md}`.

**No tocar:** `app/modules/audit/{domain/**, infrastructure/models.py,
infrastructure/registro.py}`; `alembic/**`; los siete módulos de contenido y
`authentication`; **todo `personal-blog-frontend`**; Terraform, Docker Compose y runbooks.

## 14. Resultado de pruebas

Detalle completo en el [reporte](../task-reports/TASK-012.1-report.md).

| Compuerta | Baseline (`main`) | Después |
| --- | --- | --- |
| `ruff check .` | passed | passed |
| `ruff format --check .` | 281 formateados | 286 formateados |
| `mypy .` | 279 archivos, 0 problemas | 284 archivos, 0 problemas |
| `pytest` | **1527 passed**, 1 skipped | **1572 passed**, 1 skipped (**+45**) |
| `docker build` | — | imagen construida |
| Migraciones | 3 | **3** — ninguna nueva |

La **colección vacía** quedó cubierta tras la validación del usuario: la primera versión de
`test_un_historial_vacio_es_una_pagina_vacia` preparaba la sesión con un login real, que
audita, así que nunca observaba `total = 0`. Detalle en el
[reporte](../task-reports/TASK-012.1-report.md) §8bis.

**RED registrado** antes de escribir código productivo: 10 fallos de contrato, todos por
inexistencia de la ruta y del esquema. **GREEN** tras los cuatro *slices*. Tres
**mutaciones** confirmaron que las pruebas críticas pueden fallar.

**Se enmendaron tres tests históricos, no dos.** La suite completa reveló que
`tests/test_openapi.py::test_openapi_no_declara_endpoints_no_implementados` se apoyaba en la
misma premisa falsa. Motivo canónico y antes/después en el reporte, §7.

## 15. Pasos de validación para el usuario

Comandos exactos y no destructivos en el [reporte](../task-reports/TASK-012.1-report.md) §16.

## 16. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** ✔ |
| **Fecha de aprobación** | **2026-09-05** |
| **Aprobado por** | **jeffersondavila** (el usuario) |
| **Expresión de aprobación** | `approved: Task/012.1-Exponer-Auditoria-Para-Dashboard` — recibida literalmente |

La aprobación autorizó el flujo de cierre de
[`WORKFLOW.md`](../project-management/WORKFLOW.md) §3 en `personal-blog-backend` y
`personal-blog-infra`: promoción de las decisiones de esta ficha de **Propuesta** a
**Vigentes**, actualización del gobierno, commits, integración en `dev` mediante merge
`--no-ff` y pull request `Task/012.1-Exponer-Auditoria-Para-Dashboard → main`.

**La revisión y la fusión del pull request son responsabilidad exclusiva del usuario.**

Las decisiones que esta tarea deja **Vigentes**:

| Decisión | Estado |
| --- | --- |
| `GET /api/v1/admin/audit-events` como única exposición del historial, de solo lectura | **Vigente** |
| DTO de cinco campos: `id`, `occurred_at`, `action`, `entity_type`, `entity_id` | **Vigente** |
| Exclusión de `actor_id`, `event_metadata`, `request_id` e `ip_address` de `v1` | **Vigente** |
| Orden `occurred_at DESC, id ASC` | **Vigente** |
| Sin filtros, sin detalle, sin migración | **Vigente** |
| **B-08 enmendada** y **B-08b** añadida en `security-boundaries.md` §12.1 | **Vigente** |
| La lectura del historial **no** genera un `AuditEvent` | **Vigente** |
