# TASK-012 — API Administrativa

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/012-API-Administrativa` |
| **Nombre** | API Administrativa |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Estado** | **Aprobada** ✔ el 2026-09-03 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/012-API-Administrativa` |
| **Repositorios involucrados** | `personal-blog-backend` (funcional) · `personal-blog-infra` (gobierno y contratos) |
| **Repositorio NO modificado** | `personal-blog-frontend` — sin rama y sin cambios |
| **Dependencias** | `Task/009` (**Aprobada**) · `Task/010` (**Aprobada**) · `Task/011` (**Aprobada**) |
| **Rama** | `Task/012-API-Administrativa` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base (backend)** | `561128b52c50207c7c829e260dd1c8c6d8c9e0e9` |
| **SHA base (infra)** | `eceb5b35752ecec6d8c150ea813ae72f14db55ff` |
| **Fecha de inicio** | 2026-09-01 |
| **Última actualización** | 2026-09-03 (aprobación y cierre) |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

| # | Comprobación | backend | infra |
| --- | --- | --- | --- |
| 1 | `main == origin/main` | `561128b5…` = `561128b5…` ✔ | `eceb5b35…` = `eceb5b35…` ✔ |
| 2 | Working tree limpio antes de crear la rama | ✔ (vacío) | ✔ (vacío) |
| 3 | Rama creada **desde `main`** | ✔ | ✔ |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | ✔ | ✔ |
| 5 | `git rev-list --count main..HEAD` | **0** | **0** |
| 6 | `main` es ancestro de `dev`; `dev..main` = 0; `diff main dev` vacío | ✔ | ✔ |

`personal-blog-frontend` permanece en `main`, limpio y **sin rama Task**.

---

## 1. Objetivo

Entregar la **API administrativa del MVP**: las operaciones autenticadas con las que el
administrador crea, edita, publica, despublica y archiva contenido, gestiona etiquetas y
administra la biblioteca de medios, sobre los contratos y el modelo ya aprobados en
`Task/008`, `Task/009`, `Task/010` y `Task/011`.

## 2. Contexto

Es la **quinta y última** tarea de la ETAPA 03. `Task/008` dejó el esquema y el ciclo de
vida de publicación en el dominio; `Task/009`, los diez endpoints públicos; `Task/010`, el
almacenamiento de objetos y los casos de uso de medios; `Task/011`, la autenticación y la
protección reutilizable `AdministradorRequerido`.

Varias fuentes canónicas dejan **explícitamente** materia abierta para esta tarea:

| Materia abierta | Fuente que la asigna |
| --- | --- |
| Esquemas de petición y respuesta administrativos | `api-contracts.md` §4 y §11 |
| **Forma exacta de las transiciones de estado** | `api-contracts.md` §4 y §11 · `USER_FLOWS.md` B.7 |
| **Campos mínimos para publicar** | `data-model.md` §6, invariante 18 · `USER_FLOWS.md` B.7 |
| **Formato y generación del `slug`** | `data-model.md` §6 invariante 8 y §10 deuda 7 · `USER_FLOWS.md` B.2 |
| `rating` obligatorio al publicar una review | `CONTENT_MODEL.md` §3.3 · `data-model.md` D-D |
| Exposición HTTP del borrado de medios con comprobación de uso | `data-model.md` §6, invariante 12 |
| Endpoints administrativos de medios | `api-contracts.md` §4 · `USER_FLOWS.md` B.4 y B.5 |
| Catálogo de acciones auditadas del CRUD | `CONTENT_MODEL.md` §3.9 · `data-model.md` §4.10 |
| Edición del perfil singleton por API | `data-model.md` §5 |

---

## 3. Dentro del alcance

- [x] Contrato administrativo completo derivado de las fuentes canónicas (§7.0).
- [x] Protección de **todos** los endpoints nuevos con `AdministradorRequerido` (`Task/011`).
- [x] `GET` y `PUT /api/v1/admin/profile` (singleton, con enlaces sociales).
- [x] CRUD administrativo de artículos, reviews, vídeos y proyectos.
- [x] Transiciones de estado como **subrecursos** (`publish`, `unpublish`, `archive`).
- [x] Validación de publicación por tipo (campos mínimos).
- [x] Generación y validación de `slug`, con su regla de estabilidad.
- [x] Gestión de asociaciones M:N con etiquetas, transaccional.
- [x] Gestión administrativa de etiquetas.
- [x] Endpoints administrativos de medios: carga, listado y borrado con comprobación de uso,
      **reutilizando** los casos de uso de `Task/010`.
- [x] Catálogo de acciones auditadas del CRUD y su emisión.
- [x] Prueba transversal que recorre OpenAPI y exige autenticación en todo `/admin/*` salvo
      `login`.
- [x] Documentación: ficha, reporte, `STATUS`, `ROADMAP`, `STAGE-03`, `api-contracts`,
      `data-model`, `software-architecture`, `security-boundaries`.

## 4. Fuera del alcance

| Fuera | Propietario |
| --- | --- |
| Panel React, dashboard, editor Markdown, vista previa, UI de carga | `Task/015` |
| Render y sanitización de Markdown | `Task/014`, `Task/015` |
| Lista cerrada de proveedores de vídeo permitidos | `Task/014` |
| `og:image` y URL estable de medios | `Task/016`, `Task/030` (**D-08**) |
| CORS efectivo y cabeceras de seguridad | `Task/018` |
| Privilegio mínimo sobre `audit_events` (invariante 16b) | `Task/018` |
| Retención del historial de auditoría | operación |
| Semilla local del perfil y del administrador | `Task/022` |
| Perfil y administrador **reales de producción** | `Task/036` |
| `register`, roles, RBAC, cambio o recuperación de contraseña | **ninguno**: fuera del MVP |
| Restaurar desde `archived` | fuera del MVP (`data-model.md` §6, invariante 5) |
| Cualquier recurso AWS, Terraform o Cloudflare | ETAPAS 08–10 |

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Utilidad de `slug` | backend | `app/shared/slug.py` |
| Catálogo de acciones del CRUD | backend | `app/modules/audit/domain/acciones.py` |
| Validación de publicación (4 tipos) | backend | `app/modules/<tipo>/domain/publicacion.py` |
| Casos de uso administrativos | backend | `app/modules/<modulo>/application/administracion.py` |
| Repositorios administrativos | backend | `app/modules/<modulo>/infrastructure/repositorio.py` |
| Consultas administrativas | backend | `app/modules/<modulo>/infrastructure/queries.py` |
| Esquemas HTTP administrativos | backend | `app/modules/<modulo>/presentation/schemas_admin.py` |
| Routers administrativos | backend | `app/modules/<modulo>/presentation/router_admin.py` |
| Montaje | backend | `app/api/admin.py`, `app/main.py` |
| Ficha y reporte | infra | `docs/tasks/`, `docs/task-reports/` |

## 6. Criterios de aceptación

1. Todo endpoint bajo `/api/v1/admin/*` exige sesión válida, **excepto `login`**.
2. La API pública sigue siendo anónima y su contrato no cambia.
3. El perfil se lee y se edita, y **no** se crea ni se elimina por API.
4. Los cuatro tipos publicables se crean, editan, listan, consultan, publican y archivan;
   artículos y reviews además se despublican.
5. Publicar un borrador incompleto se **rechaza** con el campo que falta.
6. `published_at` es la fecha de la **primera** publicación y no se reescribe.
7. Un `slug` duplicado produce `409`; el `slug` deja de ser mutable tras la primera publicación.
8. Las asociaciones con etiquetas son atómicas.
9. Un medio en uso no puede eliminarse y el rechazo dice dónde se usa.
10. La auditoría registra las acciones del catálogo, sin secretos, y sigue siendo inmutable.
11. Ninguna respuesta expone modelos ORM ni campos internos.
12. La integración se ejecuta contra PostgreSQL real (`personal_blog_test`).

---

## 7. TDD / Plan test-first

### 7.0 SLICE 0 — Contrato administrativo (contract-first)

> Se completa **antes** de escribir el primer test y la primera línea de implementación.
> Todo lo de aquí sale de una fuente canónica citada; nada se decide por uniformidad.

#### 7.0.1 Superficie: 23 rutas nuevas

Prefijo `/api/v1/admin`. **Todas** exigen sesión (`AdministradorRequerido`).

| # | Método y ruta | Éxito | Errores | Auditoría |
| --- | --- | --- | --- | --- |
| 1 | `GET /admin/profile` | `200` `PerfilAdministrativo` | `401`, `404` | — |
| 2 | `PUT /admin/profile` | `200` `PerfilAdministrativo` | `401`, `403`, `404`, `422` | `profile.updated` |
| 3 | `GET /admin/posts` | `200` `Pagina[ArticuloDeListadoAdmin]` | `401`, `422` | — |
| 4 | `POST /admin/posts` | `201` `ArticuloAdministrativo` | `401`, `403`, `409`, `422` | `content.created` |
| 5 | `GET /admin/posts/{post_id}` | `200` `ArticuloAdministrativo` | `401`, `404` | — |
| 6 | `PUT /admin/posts/{post_id}` | `200` `ArticuloAdministrativo` | `401`, `403`, `404`, `409`, `422` | `content.updated` |
| 7 | `POST /admin/posts/{post_id}/publish` | `200` `ArticuloAdministrativo` | `401`, `403`, `404`, `409` | `content.published` |
| 8 | `POST /admin/posts/{post_id}/unpublish` | `200` `ArticuloAdministrativo` | `401`, `403`, `404`, `409` | `content.unpublished` |
| 9 | `POST /admin/posts/{post_id}/archive` | `200` `ArticuloAdministrativo` | `401`, `403`, `404`, `409` | `content.archived` |
| 10–16 | Idem 3–9 sobre `/admin/book-reviews` | | | |
| 17–21 | Idem 3–7 y 9 sobre `/admin/videos` — **sin `unpublish`** | | | |
| 22–26 | Idem sobre `/admin/projects` — **sin `unpublish`** | | | |
| 27 | `GET /admin/tags` | `200` `Pagina[EtiquetaAdministrativa]` | `401`, `422` | — |
| 28 | `POST /admin/tags` | `201` `EtiquetaAdministrativa` | `401`, `403`, `409`, `422` | `tag.created` |
| 29 | `PUT /admin/tags/{tag_id}` | `200` `EtiquetaAdministrativa` | `401`, `403`, `404`, `422` | `tag.updated` |
| 30 | `DELETE /admin/tags/{tag_id}` | `204` | `401`, `403`, `404` | `tag.deleted` |
| 31 | `GET /admin/media` | `200` `Pagina[MedioAdministrativo]` | `401`, `422` | — |
| 32 | `POST /admin/media` | `201` `MedioAdministrativo` | `401`, `403`, `413`, `415`, `422` | `media.uploaded` |
| 33 | `DELETE /admin/media/{media_id}` | `204` | `401`, `403`, `404`, `409` | `media.deleted` |

Rutas OpenAPI resultantes (23): `/admin/profile`; `/admin/{posts,book-reviews,videos,projects}`
y `/{id}` y `/{id}/publish` y `/{id}/archive` (+ `/{id}/unpublish` en posts y book-reviews);
`/admin/tags` y `/admin/tags/{tag_id}`; `/admin/media` y `/admin/media/{media_id}`.

`403` aparece en los métodos que cambian estado porque la validación de `Origin` de
`Task/011` (defensa CSRF, D-011-K) se aplica también a este router: es la misma regla, no
una nueva.

#### 7.0.2 Decisiones del contrato

| # | Decisión | Alternativas | Elegida | Fuente y razón |
| --- | --- | --- | --- | --- |
| **D-012-A** | **Forma de las transiciones** | subrecurso dedicado · campo `status` en `PUT` | **Subrecurso `POST /{id}/publish`, `/unpublish`, `/archive`** | `api-contracts.md` §4 y `USER_FLOWS.md` B.7 dejan la elección aquí. Una transición tiene **precondición**, validación propia (campos mínimos), error propio (`409`) y acción de auditoría propia; un `status` dentro del `PUT` mezclaría edición y ciclo de vida, y B.3 los separa explícitamente —*"editar un contenido `published`… no lo despublica implícitamente"*—. Además, `Video` y `Project` **no** admiten `published → draft`, y `Task/008` expresó esa diferencia por **ausencia del método** en el dominio: con subrecursos la ruta sencillamente no existe, y OpenAPI lo dice. **Consecuencia:** `status` **no** es escribible en `POST`/`PUT`; todo contenido nace `draft` (B.2) |
| **D-012-B** | **Idempotencia de las transiciones** | idempotente · `409` | **`409 Conflict`** | No es una elección libre: el dominio aprobado en `Task/008` ya lo decidió —`publish()` sobre algo no-`draft` y `archive()` sobre algo ya archivado lanzan `Invalid…StateError`—. Hacerlas idempotentes exigiría **modificar dominio aprobado** y borraría la diferencia entre "lo archivé yo" y "ya estaba" |
| **D-012-C** | **Verbo de edición** | `PUT` (representación completa) · `PATCH` (parcial) | **`PUT`, representación completa** | La matriz flujo→recurso de `USER_FLOWS.md` dice `POST`/`PUT`, y B.10 fija `PUT` para el perfil. Dos verbos serían dos contratos. Un `PATCH` parcial además no sabe expresar "vacía este campo" sin inventar un centinela. **Coste aceptado y documentado:** omitir un campo opcional lo deja nulo — que es lo que `PUT` significa |
| **D-012-D** | **Eliminar contenido** | `DELETE` físico · `archived` · `deleted_at` | **No existe `DELETE` de contenido** | `MVP_SCOPE.md` §3.1 enumera las capacidades por tipo —*crear, editar, previsualizar, publicar, despublicar, archivar*— y **no incluye eliminar**. La invariante 3 de `CONTENT_MODEL.md` dice que `archived` **se conserva**. No se introduce `deleted_at`: ninguna fuente lo pide. `DELETE` existe solo donde una fuente lo asigna: etiquetas (B.11) y medios (B.5) |
| **D-012-E** | **Generación del `slug`** | siempre automático · siempre manual · **propuesto y editable** | **Opcional en la petición; si falta se deriva del título** | B.2 es literal: *"Introduce título; el **slug se propone automáticamente** y es editable"*. `data-model.md` §6 invariante 8 asigna aquí formato y generación |
| **D-012-F** | **Estabilidad del `slug`** | siempre mutable · inmutable · **mutable hasta la primera publicación** | **Mutable mientras `published_at IS NULL`; después `409 slug_is_immutable`** | `api-contracts.md` §4: *"el slug **puede cambiar mientras se edita un borrador**"*. Invariante 4 de `CONTENT_MODEL.md`: los slugs son *"estables: cambiarlos rompe URLs y SEO"*. La frontera exacta no es `status`, es **haber sido público alguna vez**: un `draft` despublicado ya tuvo URL indexada, y `published_at` es justamente la marca de que la tuvo |
| **D-012-G** | **Formato del `slug`** | libre · restringido | **`[a-z0-9]` y `-`, sin guion inicial ni final ni repetido, 1–160** | 160 es el ancho de la columna (`data-model.md` D-B). El resto es lo que hace que el slug funcione en una URL sin escapado. La derivación normaliza a NFKD, retira diacríticos, pasa a minúsculas y colapsa lo demás en `-`. Un título del que no salga ningún carácter útil produce `422` pidiendo un slug explícito: **inventar uno sería inventar la identidad pública del contenido** |
| **D-012-H** | **Código de "no se puede publicar"** | `422` · `409` | **`409 cannot_publish_incomplete_draft`**, con `details.campos` | La petición está bien formada y vacía: lo que falla no es la petición sino el **estado del recurso**, y `api-contracts.md` §8 reserva `409` para *"conflicto de estado"*. Mismo criterio que la transición inválida |
| **D-012-I** | **Identidad en las rutas** | `slug` · `id` | **`id` (UUID)** | `api-contracts.md` §4: *"Los recursos administrativos operan sobre **identificadores internos**, no sobre slugs: el slug puede cambiar mientras se edita un borrador"* |
| **D-012-J** | **Referencias a etiquetas y portada** | slug · **id** | **`tag_ids: [UUID]`, `cover_id: UUID \| null`** | Coherente con D-012-I. Un identificador desconocido produce `422` con la lista en `details`: la petición está bien formada pero referencia algo que no existe, y un `404` no diría **cuál** de los recursos falta |
| **D-012-K** | **Paginación administrativa** | propia · **la del proyecto** | **La misma `Pagina[T]`, `page`/`page_size`, 12 y 50** | `api-contracts.md` §5 no restringe su envoltura a lo público y exige que **toda** colección esté paginada. Un segundo formato sería un segundo contrato sin ninguna fuente que lo pida |
| **D-012-L** | **Orden del listado administrativo** | `published_at` desc · **`updated_at` desc** | **`updated_at` descendente, desempate `slug` ascendente** | El orden público no sirve aquí: un borrador **no tiene** `published_at` y todos quedarían agrupados en un extremo. `MVP_SCOPE.md` §3.3 describe el dashboard como *"últimos elementos modificados"*. El desempate por `slug` es la misma razón que D-009-F: `LIMIT`/`OFFSET` sobre un orden no total puede repetir u omitir filas |
| **D-012-M** | **Filtros administrativos** | `status` · `status`+`tag`+`featured` | **Solo `status`** | `api-contracts.md` §6 marca `status` como *"solo administrativo"*, y esa es la única fuente que asigna un filtro a este lado. `tag` y `featured` no los pide ningún flujo administrativo; añadirlos después es compatible (§10, regla 3) |
| **D-012-N** | **Prefijo de las acciones auditadas** | `posts.*`, `videos.*`… · **`content.*`** | **`content.created/updated/published/unpublished/archived` + `entity_type`** | `audit_events` ya tiene la columna `entity_type` para decir **de qué tipo** es el elemento (`data-model.md` D-M). Repetirlo dentro de `action` daría dos fuentes para el mismo hecho, que pueden discrepar, y obligaría a conocer cuatro literales para responder *"qué se publicó este mes"*. El prefijo sigue diciendo de qué clase de módulo viene la entrada, que es lo que pedía la nota de `acciones.py` |
| **D-012-O** | **Metadatos de auditoría** | diff campo a campo · **mínimos** | `{"slug"}` en contenido y etiquetas; `{"estado_anterior","estado_nuevo"}` en transiciones; `{"original_filename"}` en medios; nada en el perfil | `CONTENT_MODEL.md` §3.9: *"contexto adicional **no sensible**"*. Un diff campo a campo es control de versiones, que nadie ha pedido, y arrastraría Markdown al historial — expresamente prohibido |
| **D-012-P** | **Concurrencia en las transiciones** | nada · **`SELECT … FOR UPDATE`** | **Cerrojo de fila al cargar el contenido para una transición** | Es una lectura-modificación-escritura sobre el estado: sin cerrojo, dos publicaciones simultáneas ganan las dos y emiten dos eventos con `published_at` distintos. Es el mismo mecanismo que `Task/011` usó para el bloqueo de cuenta (A-08), no uno nuevo. **No** se añade cerrojo optimista a la edición: exigiría una columna de versión —cambio de esquema— para un MVP con **un** administrador. Se registra como deuda |
| **D-012-Q** | **Orden de los enlaces sociales** | `display_order` explícito · **índice del array** | **Derivado del índice del array** | `uq_profile_social_links_profile_id_display_order` haría fallar dos enlaces con el mismo orden. Derivarlo del array hace ese estado **irrepresentable** en lugar de detectarlo con un error |
| **D-012-R** | **`alt_text` donde se usa la imagen** | no exigirlo · exigirlo al cargar · **exigirlo donde se usa** | **Se exige donde se usa: al publicar los cuatro tipos, y al editar el perfil.** `Task/010` **no** lo exige al cargar (D-010-N, intacta); `Task/012` lo exige donde la imagen pasa a tener lectores; `Task/014` sigue siendo dueña del render HTML accesible | **La obligación es anterior a esta tarea y se le asigna por nombre.** `data-model.md` §4.1: *"Exigirlo donde se usa es de `Task/012` y `Task/014`"*; ficha de `Task/010`, **D-010-N**: *"la accesibilidad se garantiza donde se usa el medio (`Task/012`, `Task/014`), no en el almacén"*. Una imagen se **usa** cuando un contenido la referencia **y ese contenido es visible**: al publicar en los cuatro publicables, y al editar en el perfil, que no tiene `status` y *"siempre está visible"* (CONTENT_MODEL.md §2). **No se exige al cargar**: eso revertiría D-010-N, que está aprobada. `non-functional-requirements.md` no contradice nada: su tabla asigna el **requisito** A-04 a `Task/010` (la columna) y `Task/014` (el render); `data-model.md` asigna la **exigencia** |
| **D-012-Y** | **Quién escribe `alt_text`** | solo al cargar · endpoint de actualización de medios · **el primer uso lo escribe** | **El primer uso lo escribe**, en la misma transacción en la que se establece la referencia | Comprobar que el texto existe **no es escribirlo**. `data-model.md` §4.1 y **D-010-N** dicen que *«se escribe al **usar** la imagen, no al cargarla»*: si el único momento posible fuera la carga, esa frase sería falsa y el administrador tendría que anticipar el texto sin saber en qué contenido va a aparecer la imagen — justo lo que `Task/010` rechazó. **No se añade un `PUT`/`PATCH` de medios**: el contrato concede a `/admin/media` carga, listado y borrado, y no hace falta ampliarlo. Los DTO administrativos ganan `cover_alt_text`, `thumbnail_alt_text` y `photo_alt_text`; la regla —cuándo escribir, cuándo reutilizar y cuándo rechazar— vive en el módulo `media`, que es el dueño de `alt_text` |
| **D-012-Z** | **Un texto distinto del que la imagen ya tiene** | sobrescribir · ignorar en silencio · **rechazar** | **`409 alt_text_conflict`**, sin sobrescribir | **Ninguna fuente vigente define esta semántica**; se comprobó una por una. Lo que sí existe es el riesgo, descrito por **D-010-J** para el caso análogo de la deduplicación: *«reutilizar en silencio haría que borrar un medio afectara a contenidos que nunca lo subieron»*. Sobrescribir tendría la misma forma: cambiaría el texto que ya usa otro contenido. Rechazar **también es una decisión de comportamiento**, no la ausencia de una. Ante la ausencia de una semántica canónica previa, `Task/012` adopta para el MVP la política conservadora de rechazar una sobrescritura diferente. **La revisión externa acepta D-012-Z.** La política es explícita, reversible y evita modificar en silencio un `MediaAsset` que puede estar siendo utilizado por otro contenido. **RESUELTA / ACEPTADA PARA EL MVP** |
| **D-012-AA** | **Dos primeros usos simultáneos de la misma imagen** | dejar la carrera · cerrojo en memoria · **`SELECT … FOR UPDATE` sobre la fila del medio** · `UPDATE` condicional | La lectura de la decisión bloquea la fila de `media_assets` | La decisión *set-on-first-use* es una **lectura-decisión-escritura**, y sin exclusión D-012-Z es falsa bajo concurrencia: se demostró con dos transacciones reales que ambas terminaban en `ok` y el segundo `UPDATE` pisaba al primero. El cerrojo lo da **el motor**, así que vale con varios *workers* y varias instancias, al contrario que cualquier cerrojo de proceso —mismo criterio que **A-08** de `Task/011` y que **D-012-P**—. En **READ COMMITTED** quien llega segundo espera y **relee la última versión confirmada**, así que ve el texto del ganador y la regla del dominio decide: `409` si es distinto, no-op si es el mismo. **La igualdad no se convierte en conflicto.** No se bloquea ninguna lectura pública ni la de validación de publicación: la exclusión existe solo en la operación que decide y escribe `alt_text`. Sin Redis, sin cerrojos distribuidos, sin tabla ni migración nuevas |
| **D-012-X** | **Orden de la auditoría al borrar un medio** | borrar y después auditar · **auditar y después borrar** | **Auditar primero** | PostgreSQL revierte y el almacenamiento **no**. `EliminarMedio` borra la fila —solo con `flush`— y **después** los objetos; si la auditoría fallara después, la transacción devolvería la fila mientras los objetos ya no estarían: exactamente la *"fila sin objetos — imagen rota en el blog publicado"* que **D-010-P** eligió su orden para evitar. Auditando antes, un fallo del historial ocurre **antes de tocar nada**. La corrección vive en la frontera de composición de `Task/012`; **`Task/010` no se toca**. Mismo orden, y por la misma razón, que `EliminarEtiqueta` |
| **D-012-S** | **`slug` de una etiqueta** | mutable · **inmutable** | **Inmutable tras la creación; `PUT` cambia `name` y `description`** | B.11 dice *"renombra"*, que es el nombre visible. El slug de una etiqueta aparece en URL públicas compartibles (A.9) y la invariante 4 lo declara estable |
| **D-012-T** | **Confirmación al borrar una etiqueta en uso** | parámetro en la API · **paso de interfaz** | **Paso de interfaz (`Task/015`)**; la API borra y desasocia | La asimetría está en las propias fuentes: en B.5 el backend debe **rechazar** un medio en uso; en B.11 debe **desasociar**. *"El frontend presenta y valida por usabilidad; el backend decide"* (`software-architecture.md` §2) |
| **D-012-U** | **Crear el perfil por API** | permitirlo · **no** | **`PUT` sobre un perfil inexistente → `404`** | `data-model.md` §5 lo asigna por nombre: *"El perfil no se crea ni se elimina por API — **`Task/012`** — solo expone lectura y edición"*. La creación real es de `Task/022` (semilla local) y `Task/036` (producción) |
| **D-012-V** | **Límite transaccional** | transacción propia por caso de uso · **la de la petición** | **`get_session`: la petición es la unidad de trabajo** | Crear un contenido, asociar sus etiquetas, resolver su portada y auditar deben ser atómicos (§29). `session_scope` ya confirma al salir y revierte ante cualquier excepción. `Task/011` confirma dentro del caso de uso **solo** porque su camino de fallo debe persistir estado defensivo; aquí un fallo debe revertirlo todo |

#### 7.0.3 Validación de publicación — tabla por entidad y campo

> `USER_FLOWS.md` B.7: *"Se validan los campos mínimos (título, slug, contenido, y SEO si
> corresponde)"*. Se traduce campo a campo, con la fuente de cada fila.

**Regla común de SEO.** `CONTENT_MODEL.md` §2 define los *fallbacks*: `seo_title` cae en
`title`, y `seo_description` cae en `summary`. Por eso "SEO si corresponde" **no** significa
exigir los campos SEO —contradiría el *fallback*—, sino que la descripción SEO **se pueda
resolver**: `seo_description` **o** `summary` no vacío. El título siempre se resuelve porque
`title` es obligatorio.

| Entidad | Campo | ¿Obligatorio en `draft`? | ¿Obligatorio al publicar? | Fuente |
| --- | --- | :---: | :---: | --- |
| **Los cuatro** | `title` | **sí** | **sí** | B.2 *"título obligatorio"*; B.7 |
| **Los cuatro** | `slug` | **sí** (derivado) | **sí** | B.2; B.7 |
| **Los cuatro** | `seo_description` **o** `summary` | no | **sí** | B.7 *"y SEO si corresponde"* + *fallbacks* de `CONTENT_MODEL.md` §2 |
| **Los cuatro** | `cover` / `thumbnail` | no | no | Ninguna fuente lo exige; `MedioPublico` es opcional en el contrato público |
| **Los cuatro** | `tags` | no | no | Ninguna fuente lo exige |
| **Los cuatro** | `featured` | no (`false`) | no | `data-model.md` §4.4.1 |
| `Post` | `content` | no (`''`) | **sí, no vacío** | B.7 *"contenido"*; `CONTENT_MODEL.md` §2: el cuerpo principal es Markdown |
| `BookReview` | `content` | no (`''`) | **sí, no vacío** | igual que `Post` |
| `BookReview` | `book_title` | no | **sí** | A.4 y A.5 muestran autor y libro; `data-model.md` §4.6 los declara nulos *"en un borrador recién creado"* |
| `BookReview` | `book_author` | no | **sí** | igual |
| `BookReview` | `rating` | no | **sí (1–5)** | `CONTENT_MODEL.md` §3.3: *"exigirla para **publicar** es una validación de publicación y pertenece a `Task/012`"*; `data-model.md` D-D |
| `BookReview` | `external_link` | no | no | `CONTENT_MODEL.md` §3.3: *"enlace opcional"*; A.5: *"si existe"* |
| `Video` | `content` | **no existe** | — | `CONTENT_MODEL.md` §2 y ADR-005: el vídeo no tiene Markdown |
| `Video` | `video_url` | no | **sí** | A.6: se reproduce por *embed* o enlace externo; `data-model.md` §4.7: *"nulo hasta que se pegue la URL"*. Es el equivalente de "contenido" de B.7 para este tipo |
| `Video` | `provider` | no | **sí** | `CONTENT_MODEL.md` §3.4: *"solo se almacenan URL, **proveedor** y metadatos"*. **Se exige presencia, no pertenencia a una lista**: la lista cerrada es de `Task/014` |
| `Video` | `embed_reference`, `duration_seconds` | no | no | Opcionales en el modelo |
| `Project` | `content` | no (`''`) | **sí, no vacío** | igual que `Post` |
| `Project` | `technologies` | no (`[]`) | no | Lista que solo se muestra (D-G) |
| `Project` | `repository_url`, `demo_url` | no | no | `CONTENT_MODEL.md` §3.5: *"opcional"* |
| `Project` | `project_status` | no (`active`) | no | Tiene *default* real (D-E) |
| `Profile` | — | no aplica | **no aplica** | Sin `status` ni `published_at` (`CONTENT_MODEL.md` §2) |

#### 7.0.4 Ciclo de vida por entidad — lo que esta tarea expone

Tomado **sin cambios** de `data-model.md` §7 y `MVP_SCOPE.md` §3.2.

| Tipo | `draft → published` | `published → draft` | `→ archived` | `archived → *` |
| --- | :---: | :---: | :---: | :---: |
| `Post` | `POST /publish` | `POST /unpublish` | `POST /archive` | **no existe** |
| `BookReview` | `POST /publish` | `POST /unpublish` | `POST /archive` | **no existe** |
| `Video` | `POST /publish` | **la ruta no existe** | `POST /archive` | **no existe** |
| `Project` | `POST /publish` | **la ruta no existe** | `POST /archive` | **no existe** |

`published_at`: se fija en la **primera** publicación, se **conserva** al despublicar y al
archivar, y **no se reescribe** al volver a publicar (`data-model.md` §7).

### 7.1 Comportamientos a construir

1. Un `slug` se deriva de un título y se valida.
2. Cada tipo publicable sabe decir qué le falta para poder publicarse.
3. Todo endpoint administrativo rechaza a quien no tiene sesión.
4. El perfil singleton se lee y se edita; no se crea ni se elimina.
5. Los cuatro tipos se crean como borrador, se editan, se listan y se consultan.
6. Las transiciones aplican el ciclo de vida del dominio y persisten su resultado.
7. Las etiquetas se gestionan y se asocian de forma atómica.
8. Los medios se cargan, se listan y se borran con comprobación de uso.
9. Cada operación que modifica datos deja un evento de auditoría sin secretos.

### 7.2 Matriz de casos

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| **A-01** | Petición sin cookie a cualquier ruta admin | — | `401 unauthenticated` | contrato |
| **A-02** | Cookie desconocida/caducada/revocada | — | `401 unauthenticated` | integración |
| **A-03** | Sesión válida | administrador con sesión | `2xx` | integración |
| **A-04** | OpenAPI recorrido entero | — | toda ruta `/admin/*` salvo `login` declara `security` | contrato |
| **A-05** | OpenAPI recorrido entero | — | ninguna ruta pública declara `security` | contrato |
| **SL-01** | `"Docker en Producción"` | — | `docker-en-produccion` | dominio |
| **SL-02** | `"  ¡Hola,   Mundo!  "` | — | `hola-mundo` | dominio |
| **SL-03** | `"★★★"` | — | error: no se puede derivar | dominio |
| **SL-04** | título de 300 caracteres | — | slug ≤ 160, sin guion final | dominio |
| **SL-05** | slug explícito `Mal Slug!` | — | `422` | dominio |
| **P-01** | `GET /admin/profile` | perfil existe | `200` con enlaces ordenados | integración |
| **P-02** | `PUT /admin/profile` | perfil existe | `200`, cambios persistidos | integración |
| **P-03** | `PUT` con dos enlaces | perfil existe | orden = índice del array | integración |
| **P-04** | `GET`/`PUT` | **no hay perfil** | `404`; **no se crea ninguna fila** | integración |
| **P-05** | `PUT` sin `full_name` | perfil existe | `422` | contrato |
| **P-06** | `PUT` con `photo_id` desconocido | perfil existe | `422` | integración |
| **PO-01** | `POST /admin/posts` mínimo | — | `201`, `status=draft`, `published_at=null` | integración |
| **PO-02** | `POST` sin `slug` | — | slug derivado del título | integración |
| **PO-03** | `POST` con slug existente | ya existe | `409 slug_already_exists` | integración |
| **PO-04** | `PUT` de un borrador | existe | `200`, campos actualizados | integración |
| **PO-05** | `PUT` cambiando el slug, `published_at=null` | borrador nunca publicado | `200` | integración |
| **PO-06** | `PUT` cambiando el slug, `published_at` presente | ya se publicó | `409 slug_is_immutable` | integración |
| **PO-07** | `GET /admin/posts` | 1 draft, 1 published, 1 archived | los **tres** aparecen | integración |
| **PO-08** | `GET /admin/posts?status=draft` | idem | solo el borrador | integración |
| **PO-09** | `GET /admin/posts` | 3 elementos | orden `updated_at` desc | integración |
| **PO-10** | `GET /admin/posts/{id}` desconocido | — | `404` | integración |
| **PO-11** | `publish` de un borrador completo | completo | `200`, `published`, `published_at` fijado | integración |
| **PO-12** | `publish` sin contenido | incompleto | `409 cannot_publish_incomplete_draft`, `details.campos=["content"]` | integración |
| **PO-13** | `publish` sin resumen ni `seo_description` | incompleto | `409`, `details.campos` incluye `summary` | integración |
| **PO-14** | `publish` de algo ya publicado | `published` | `409 invalid_post_state` | integración |
| **PO-15** | `unpublish` de publicado | `published` | `200`, `draft`, **`published_at` conservado** | integración |
| **PO-16** | `publish` de nuevo | `draft` con fecha | `published_at` **no** se reescribe | integración |
| **PO-17** | `archive` de publicado | `published` | `200`, `archived`, fecha conservada | integración |
| **PO-18** | `archive` de archivado | `archived` | `409` | integración |
| **PO-19** | `POST` con `tag_ids` | etiquetas existen | asociaciones creadas | integración |
| **PO-20** | `PUT` con `tag_ids` distinto | tenía otras | reemplazo exacto, sin duplicados | integración |
| **PO-21** | `POST` con `tag_ids` desconocido | — | `422`, **ninguna fila creada** | integración |
| **PO-22** | `POST` con `cover_id` desconocido | — | `422`, ninguna fila creada | integración |
| **PO-23** | `POST` con `cover_id` válido | medio existe | portada con `access_url` en la respuesta | integración |
| **PO-24** | dos `publish` simultáneos | dos conexiones reales | uno `200`, otro `409`; **un solo** evento | integración |
| **PO-25** | respuesta administrativa | — | no lleva `cover_id`, `is_singleton`, `object_key` ni `password_hash` | contrato |
| **BR-01…BR-06** | equivalentes | | incluye `rating` 1–5, `book_title`, `book_author` obligatorios al publicar y `unpublish` | integración |
| **V-01…V-05** | equivalentes | | `video_url` y `provider` obligatorios al publicar; **`unpublish` no existe** (`405`) | integración |
| **PR-01…PR-05** | equivalentes | | `content` obligatorio; `technologies` y `project_status` escribibles; **sin `unpublish`** | integración |
| **T-01** | `POST /admin/tags` | — | `201`, slug derivado del nombre | integración |
| **T-02** | `POST` con slug repetido | existe | `409` | integración |
| **T-03** | `PUT` cambia `name` | existe | `200`; el `slug` **no** cambia aunque se envíe | integración |
| **T-04** | `DELETE` de etiqueta libre | sin uso | `204` | integración |
| **T-05** | `DELETE` de etiqueta en uso | asociada a un post | `204` y el post **sigue existiendo** sin ella | integración |
| **T-06** | `GET /admin/tags` | etiqueta sin contenido publicado | **aparece** (a diferencia del público) | integración |
| **M-01** | `POST /admin/media` PNG válido | — | `201` con `id`, dimensiones y `access_url` | integración |
| **M-02** | `POST` con un archivo que no es imagen | — | `422 invalid_image` | integración |
| **M-03** | `POST` con formato no permitido | — | `415` | integración |
| **M-04** | `DELETE` de medio libre | sin uso | `204`; objeto y miniatura borrados | integración |
| **M-05** | `DELETE` de medio en uso | portada de un post | `409 media_in_use`, `details.usos` con tipo, slug y título | integración |
| **M-06** | `DELETE` desconocido | — | `404` | integración |
| **M-07** | respuesta de medio | — | **no** lleva `object_key` | contrato |
| **AU-01…AU-05** | cada operación anterior | — | evento con acción, `entity_type`, `entity_id`, `request_id`, IP y sin secretos | integración |
| **AU-06** | historial | evento escrito | sigue siendo inmutable por la ruta normal del ORM | integración |
| **RG-01** | API pública tras publicar | — | el contenido aparece | integración |
| **RG-02** | API pública tras despublicar/archivar | — | `404`, indistinguible de inexistente | integración |
| **RG-03** | contrato público | — | rutas, parámetros y esquemas intactos | contrato |

### 7.3 Tests RED esperados

| Test | Capa | Motivo de fallo esperado |
| --- | --- | --- |
| `test_derivar_slug_*` | dominio | `app.shared.slug` no existe |
| `test_no_se_puede_publicar_*_sin_*` | dominio | el módulo de validación no existe |
| `test_todo_endpoint_admin_exige_sesion` | contrato | las rutas no existen |
| `test_el_perfil_se_edita` | integración | `404` de ruta inexistente |
| `test_crear_articulo_*` | integración | `404` de ruta inexistente |
| … | | idem para reviews, vídeos, proyectos, etiquetas y medios |

### 7.4 Integración necesaria

PostgreSQL real (`personal_blog_test`): unicidad de `slug`, `CHECK` de estado y fecha,
claves foráneas `RESTRICT` de medios, tablas puente M:N con `CASCADE`, atomicidad,
`SELECT … FOR UPDATE` con **dos conexiones reales** y persistencia de la auditoría.
MinIO real para la carga y el borrado de medios, con el harness seguro de `Task/010`.

### 7.5 Casos negativos y de seguridad

Sin sesión, sesión inválida, `Origin` ajeno, identificador inexistente, identificador
malformado, transición no permitida, borrador incompleto, slug duplicado, slug inmutable,
etiqueta y medio desconocidos, medio en uso, archivo que no es imagen, formato no permitido
y ausencia de filtraciones en toda respuesta administrativa.

### 7.6 Regresiones relevantes

- `Task/009`: los diez endpoints públicos, su contrato y la invariante 19.
- `Task/010`: contrato de `ObjectStorage`, `access_url`, comprobación de uso.
- `Task/011`: los tres endpoints de autenticación, bloqueo, límite de tasa, cookie y la
  prueba que exige que **ninguna** ruta pública declare seguridad.
- `Task/008`: inmutabilidad de `AuditEvent` y las migraciones `0001`–`0003`.

---

## 8. Plan de validación

Cada criterio de aceptación tiene al menos un caso de la matriz §7.2 y se comprueba con la
suite real, no por inspección.

## 9. Comandos de validación

```powershell
$env:PERSONAL_BLOG_TEST_DATABASE_URL = "postgresql://<usuario>:<clave>@127.0.0.1:55432/personal_blog_test"
ruff check .
ruff format --check .
mypy .
pytest tests/unit -q
pytest tests/contract -q
pytest -m integration -q
pytest -q -W error
pytest --cov -q
pip check
git diff --check
alembic heads
```

## 10. Evidencia esperada

Salida real de cada comando, evidencia RED y GREEN por *slice*, y las respuestas HTTP de los
recorridos administrativos, en el reporte.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | Proteger de más y volver privada la API pública | Alto | Prueba transversal sobre OpenAPI en ambos sentidos |
| 2 | Duplicar autenticación o almacenamiento | Alto | Se reutilizan `AdministradorRequerido`, `SubirImagen` y `EliminarMedio` |
| 3 | Repetición entre los cuatro tipos publicables | Medio | Es la postura documentada (D-P); se comparte solo lo **técnico** (`slug`, paginación) |
| 4 | El perfil no existe y el panel no puede crearlo | Medio | Es la decisión D-012-U; se registra como deuda con propietario (`Task/022`) |
| 5 | Edición concurrente sin cerrojo optimista | Bajo | Un solo administrador en el MVP; se registra como deuda |

## 12. Decisiones técnicas

Las **veintisiete** decisiones **D-012-A** a **D-012-AA** están en §7.0.2 con su fuente.
**D-012-Y**, **D-012-Z** y **D-012-AA** se añadieron en las revisiones correctivas previas
a la aprobación; **D-012-Z** queda **RESUELTA / ACEPTADA PARA EL MVP**.
Ninguna sustituye ni modifica una decisión aprobada anterior, así que **no requiere ADR**:
son decisiones de implementación dentro de contratos ya aceptados.

**D-012-W — dependencia nueva.** `python-multipart==0.0.32`, la única de la tarea. La
exige FastAPI para declarar `UploadFile`: sin ella la ruta de carga no puede definirse. La
alternativa —cuerpo crudo con el nombre del archivo en un parámetro de consulta— se
descartó porque `original_filename` es `NOT NULL` y acabaría en la URL, y por tanto en los
logs de acceso. Rueda `py3-none-any`, ~164 KB, sin dependencias transitivas.

## 13. Documentación creada o actualizada

- `docs/tasks/TASK-012-administrative-api.md` — esta ficha.
- `docs/task-reports/TASK-012-report.md` — reporte.
- `docs/project-management/STATUS.md`, `ROADMAP.md` — gobierno.
- `docs/stages/STAGE-03-domain-and-backend.md` — estado de la tarea y criterios de salida.
- `docs/architecture/api-contracts.md` — §14: contrato administrativo cerrado.
- `docs/architecture/data-model.md` — invariantes 8, 12 y 18; deuda 7.
- `docs/architecture/software-architecture.md` — §3.10.
- `docs/architecture/security-boundaries.md` — §12.

## 14. Archivos modificados

Recuento **final**, tras las tres revisiones correctivas y el micro-cierre: **88** en
`personal-blog-backend` y **12** en `personal-blog-infra`, reunidos en **un solo commit de
cierre por repositorio** el 2026-09-03. `personal-blog-frontend`: **cero**.

El [reporte §AD](../task-reports/TASK-012-report.md) registra **76 y 11**: era el estado
del 2026-09-01, antes de que las revisiones correctivas añadieran archivos. Se conserva
como historia fechada, no se reescribe. Detalle por documento en el
[reporte §Z](../task-reports/TASK-012-report.md).

## 15. Resultado de pruebas

**1527 pasan, 1 omitida** (`time.tzset` en Windows, preexistente), **0 advertencias** con
`-W error`. Cobertura de `app/`: **100 %**. Tabla completa de puertas en el
[reporte §X](../task-reports/TASK-012-report.md).

## 16. Problemas encontrados

Cuatro, ninguno corregido en silencio: la restricción única de los enlaces sociales, el
nombre del parámetro de filtro, una prueba propia inestable y drift documental preexistente.
Detalle en el [reporte §T](../task-reports/TASK-012-report.md).

## 17. Pasos de validación para el usuario

```powershell
# 1. Entorno de integración (PostgreSQL y MinIO ya levantados)
$env:PERSONAL_BLOG_TEST_DATABASE_URL = "postgresql://blog_local:<clave>@127.0.0.1:55432/personal_blog_test"
$env:PERSONAL_BLOG_TEST_STORAGE_ENDPOINT_URL = "http://127.0.0.1:9000"
$env:PERSONAL_BLOG_TEST_STORAGE_ACCESS_KEY = "<clave del .env>"
$env:PERSONAL_BLOG_TEST_STORAGE_SECRET_KEY = "<secreto del .env>"

# 2. Puertas de calidad, en el repositorio del backend
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy .
.\.venv\Scripts\python.exe -m pytest -q -W error
.\.venv\Scripts\python.exe -m pytest --cov -q
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m alembic heads      # debe decir 0003 (head)

# 3. La superficie administrativa, contra el contenedor ya recreado
docker exec personal-blog-local-backend python -c "import json,urllib.request; d=json.load(urllib.request.urlopen('http://127.0.0.1:8000/openapi.json')); a=[r for r in d['paths'] if r.startswith('/api/v1/admin')]; print('admin:',len(a)); print('sin seguridad:',[f'{m.upper()} {r}' for r in a for m,o in d['paths'][r].items() if 'security' not in o])"
# Esperado: admin: 26 · sin seguridad: ['POST /api/v1/admin/auth/login']

# 4. Estado de Git: sin commits, sin push, sin PR
git -C personal-blog-backend status --short | Measure-Object -Line
git -C personal-blog-infra   log --oneline main..HEAD    # vacio
git -C personal-blog-frontend status --short             # vacio
```

**Nota.** El panel no puede editar el perfil hasta que exista uno: `Task/012` **no lo
crea** por diseño (D-012-U). Sembrarlo en local es de `Task/022`.

## 18. Deuda técnica pendiente

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | El perfil no se crea por API: sin semilla, el panel recibe `404` | `Task/022` (local), `Task/036` (producción) |
| 2 | **Corregir a propósito** un `alt_text` ya escrito —no fijarlo: eso funciona desde D-012-Y—. **D-012-Z está aceptada para el MVP** y rechaza la sobrescritura; poder relajarla de forma deliberada es una **mejora futura**, no una obligación de `Task/012` ni una contradicción de la decisión | **mejora futura**, sin propietario ni plazo |
| 3 | Sin cerrojo optimista en la edición (D-012-P) | revisión futura |
| 4 | Lista cerrada de proveedores de vídeo | `Task/014` |
| 5 | Privilegio mínimo sobre `audit_events` | `Task/018` |

## 19. Próxima tarea

`Task/013-Sistema-de-Diseno` — tokens, componentes, tipografía, responsive y accesibilidad
base del frontend. **No se inicia hasta que el usuario apruebe esta tarea.**

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | *(pendiente)* |
| **Aprobado por** | *(pendiente — solo el usuario)* |
| **Expresión de aprobación** | `approved: Task/012-API-Administrativa` |
