# Modelo de datos físico — Blog Personal

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/008-Modelo-de-Datos` (2026-08-25) |
| **Fecha** | 2026-08-25 · **Fecha de aprobación** 2026-08-25 · §8 y §10 completadas por `Task/009-API-Publica` (2026-08-26) |
| **Nivel** | **Físico.** Tablas, columnas, tipos, claves, restricciones e índices. |
| **Migración** | `0002` (`personal-blog-backend/alembic/versions/*_0002_*.py`) |

> **Relación con el modelo conceptual.** El nivel conceptual —qué tipos existen, qué
> significan y qué atributos tienen— vive en
> [`CONTENT_MODEL.md`](../product/CONTENT_MODEL.md) y **no se duplica aquí**. Este
> documento responde a la otra pregunta: **cómo se materializa** en PostgreSQL.

Relacionados: [CONTENT_MODEL.md](../product/CONTENT_MODEL.md) ·
[MVP_SCOPE.md](../product/MVP_SCOPE.md) · [USER_FLOWS.md](../product/USER_FLOWS.md) ·
[ADR-004](../adr/ADR-004-modular-monolith.md) · [ADR-005](../adr/ADR-005-markdown-content.md) ·
[software-architecture.md](software-architecture.md)

---

## 1. Alcance

`Task/008` entrega el **esquema y las invariantes de dominio**. No entrega
comportamiento de aplicación:

| Aquí | Más tarde |
| --- | --- |
| Tablas, columnas, tipos, claves, restricciones, índices | — |
| Entidades de dominio del ciclo de vida de publicación | — |
| Escala de valoración de reviews | — |
| Migración `0002`, reversible | — |
| — | Endpoints públicos, paginación, filtros, búsqueda → **`Task/009`** *(entregado el 2026-08-26; no modifica el esquema físico)* |
| — | `ObjectStorage`, MinIO, S3, subida, URL prefirmadas → **`Task/010`** |
| — | Login, sesión, *hashing*, *rate limiting* → **`Task/011`** |
| — | Servicio de auditoría y catálogo de acciones → **`Task/011`**, **`Task/012`** |
| — | CRUD administrativo y validación de publicación → **`Task/012`** |
| — | Generación y normalización de *slug* → **`Task/012`** |
| — | Lista cerrada de proveedores de video → **`Task/014`** |
| — | Render y sanitización de Markdown → **`Task/014`**, **`Task/015`** |

**No se siembra ningún dato.** La migración no contiene `INSERT` ni `bulk_insert`.

---

## 2. Diagrama entidad-relación

```
                              ┌────────────────┐
                              │  media_assets  │
                              └────────┬───────┘
                                       │
        photo_id · cover_id · thumbnail_id   (FK, NULL, ON DELETE RESTRICT)
        ┌──────────┬────────────┬───────┴────┬────────────┐
        │          │            │            │            │
   ┌────┴─────┐ ┌──┴────┐ ┌─────┴────────┐ ┌─┴──────┐ ┌───┴──────┐
   │ profiles │ │ posts │ │ book_reviews │ │ videos │ │ projects │
   └────┬─────┘ └──┬────┘ └─────┬────────┘ └─┬──────┘ └───┬──────┘
        │          │            │            │            │
        │ CASCADE  │ post_tags  │ book_      │ video_     │ project_
        │          │            │ review_    │ tags       │ tags
        │          │            │ tags       │            │
        │          └──────┬─────┴─────┬──────┴─────┬──────┘
        │                 │           │            │
        │                 │  (PK compuesta, CASCADE en ambos lados)
        │                 └───────────┴────────────┘
        │                              │
        │                        ┌─────┴──────┐
        │                        │    tags    │
        │                        └────────────┘
   ┌────┴──────────────────┐
   │ profile_social_links  │
   └───────────────────────┘


   ┌────────────────┐   actor_id (FK, NULL, RESTRICT)   ┌──────────────┐
   │ administrators │ ◄─────────────────────────────────│ audit_events │
   └────────────────┘                                   └──────┬───────┘
                                                               │
                                          entity_type + entity_id
                                          referencia polimórfica, SIN clave foránea
```

**14 tablas:** 9 para los tipos conceptuales, 4 puentes de etiquetado y 1 dependiente
(`profile_social_links`).

---

## 3. Decisiones de diseño

| # | Decisión | Alternativas | Elegida | Por qué |
| --- | --- | --- | --- | --- |
| D-A | **Clave primaria** | `BIGSERIAL` · UUIDv4 · UUIDv7 | **`UUID` v4, generado en Python** | `audit_events` referencia cualquier tipo con `entity_type` + `entity_id` **sin** clave foránea. Con enteros secuenciales, el `5` existe en artículos, vídeos y etiquetas a la vez: un `entity_type` equivocado apuntaría en silencio a una fila real de otra tabla. Con UUID no encuentra nada. Además, la API administrativa opera sobre identificadores internos y no conviene que sean enumerables. `uuid` es un tipo del **núcleo** de PostgreSQL (T-02). UUIDv7 exigiría una dependencia nueva sin beneficio real a este volumen. |
| D-B | **Slug** | `VARCHAR` · `CITEXT` | **`VARCHAR(160)`, `NOT NULL`, `UNIQUE` por tabla** | La unicidad **por tipo** sale gratis: cada tipo tiene su tabla. `/articulos/docker` y `/videos/docker` son URL distintas y legítimas. El índice único sirve además el acceso por slug (`GET /posts/{slug}`). `CITEXT` es una extensión, prohibida por T-02. **El formato y la generación del slug son de `Task/012`** (USER_FLOWS.md B.2). |
| D-C | **Estado de publicación** | `ENUM` nativo · `VARCHAR` + `CHECK` · tabla de estados | **`VARCHAR(32)` + `CHECK`** | Un `ENUM` nativo es un objeto de esquema aparte: extenderlo exige `ALTER TYPE`, reducirlo es imposible sin recrearlo, y el `downgrade` de una migración tiene que acordarse de soltarlo o deja basura. M-04 exige que **toda** migración revierta, y ahí es donde el `ENUM` nativo falla. Un `CHECK` da la misma integridad, se lee sin consultar el catálogo y desaparece con la tabla. |
| D-D | **Escala de `rating`** | 1–5 · 1–10 · medias estrellas · decimal | **Entero 1..5, ambos inclusive** | Es la escala que el lector reconoce sin leyenda y la que el listado público muestra (A.4). 1–10 obliga a explicar si un 7 es bueno. **Nulo permitido**: un borrador puede existir antes de que su autor decida la nota (B.2 solo exige el título); que una review **publicada** deba tenerla es validación de publicación, de `Task/012`. |
| D-E | **`project_status`** | `VARCHAR` + `CHECK` con 3 valores · flujo de estados completo | **`active` · `paused` · `completed`, `VARCHAR` + `CHECK`, por defecto `active`** | Son los ejemplos que da CONTENT_MODEL.md y el producto no ha pedido más. Columna **separada** de `status`: publicación y marcha del trabajo son ortogonales —un proyecto terminado puede estar publicado— y CONTENT_MODEL.md advierte explícitamente de no mezclarlos. |
| D-F | **`social_links`** | Tabla dependiente · `JSONB` · array | **Tabla dependiente `profile_social_links`** | Cada enlace es un registro de forma fija —etiqueta, URL, orden—, no un documento libre. `NOT NULL` impide un enlace sin etiqueta o sin URL, y `UNIQUE (profile_id, display_order)` impide dos en la misma posición. Un `JSONB` no puede prometer ninguna de las dos cosas. La tabla es diminuta: hay un solo perfil. |
| D-G | **`technologies`** | Tabla puente · `JSONB` · `TEXT[]` | **`JSONB`, lista de cadenas, `NOT NULL DEFAULT '[]'`** | Es una lista ordenada de etiquetas **que solo se muestra** (A.7). En el MVP nadie consulta por tecnología: el filtro público es por `Tag` (A.9). Una tabla puente añadiría tabla, clave foránea y una unión para algo que jamás se une. El orden se conserva sin columna extra. `JSONB` es tipo del núcleo, no extensión. **Trade-off aceptado:** no hay integridad sobre el contenido de la lista ni consulta relacional; si aparece "filtrar por tecnología", `Tag` ya lo cubre y normalizar después es una migración sencilla. |
| D-H | **Marcas de tiempo** | `TIMESTAMP` · `TIMESTAMPTZ`; reloj de app · reloj de base | **`TIMESTAMP WITH TIME ZONE`, valor de la base (`now()`)** | Invariante 10 de CONTENT_MODEL.md: todo se almacena en UTC. Un reloj único para todos los escritores es inmune al desfase del servidor de aplicación. **`now()` es la hora de inicio de la transacción**, así que lo escrito en una misma transacción comparte marca: es lo correcto —los cambios de una transacción ocurren lógicamente a la vez— y está comprobado. `clock_timestamp()` se descartó por ser propio de PostgreSQL. `published_at`, en cambio, es un momento **de negocio** que fija el caso de uso con su reloj inyectado. |
| D-I | **Referencias a `MediaAsset`** | `RESTRICT` · `SET NULL` · `CASCADE` | **`ON DELETE RESTRICT`, columna nula, indexada** | Invariante 5: un medio en uso **no** puede eliminarse. `CASCADE` borraría el artículo al borrar su portada; `SET NULL` lo dejaría sin portada en silencio. `RESTRICT` es la última línea de defensa; el mensaje que dice **dónde** se usa lo construye `Task/010` (B.5). Índice en cada columna porque esa comprobación de uso consulta justo por ella y PostgreSQL no indexa las claves foráneas por su cuenta. |
| D-J | **Etiquetado** | Tabla puente por tipo · tabla polimórfica única | **Cuatro tablas puente, PK compuesta, `CASCADE` en ambos lados** | La PK compuesta es lo que rechaza una asociación duplicada. `CASCADE` retira **filas de asociación**, nunca contenido: eliminar una etiqueta desasocia (B.11). Una tabla polimórfica única no podría tener clave foránea hacia el contenido, y aquí sí se puede y se debe. |
| D-K | ***Singleton* de `Profile`** | Cerrojo booleano · `CHECK (id = <uuid fijo>)` · *trigger* | **Columna `is_singleton` `NOT NULL DEFAULT TRUE`, `UNIQUE`, `CHECK (... IS TRUE)`** | SQL corriente, sin código de servidor. Garantiza **como máximo uno**. Ver §5. |
| D-L | ***Singleton* de `Administrator`** | igual que D-K | **Mismo cerrojo, más `UNIQUE (email)`** | El cerrojo acota **cuántas** filas hay; el único sobre `email` garantiza que el identificador de acceso es **único**, que es lo que seguirá haciendo falta si algún día hay más de un administrador. Se elige `email` sobre `username`: el propietario ya lo usa y sirve además como vía de recuperación. |
| D-M | **Referencia polimórfica de `AuditEvent`** | Sin FK · supertabla `content` · una FK nula por tipo | **`entity_type` + `entity_id`, sin clave foránea** | Un evento debe **sobrevivir** a lo que describe; una FK lo borraría o bloquearía el borrado del elemento. Una supertabla sería la superentidad que este modelo descarta. Varias FK nulas no sabrían expresar "solo una está rellena". Ver §6 para el precio exacto. |
| D-N | **Inmutabilidad de `AuditEvent`** | *Trigger* · revocar privilegios · guarda en el ORM | **Guarda en el *mapper* (`before_update`, `before_delete`)** | Invariante 8. Enganchada al *mapper* y no a un caso de uso, para que la garantía no dependa de que nadie se olvide. **Alcance exacto y medido en §6.2**: cierra la ruta normal de escritura del ORM; **no** cierra el DML masivo ni las sentencias Core. Revocar `UPDATE`/`DELETE` al rol es privilegio mínimo (S-01) y pertenece a `Task/018`. |
| D-O | **`reading_time` y `thumbnail_url`** | Persistir · derivar | **No se persisten** | Ambos son derivables: el tiempo de lectura del contenido, la miniatura del proveedor de `provider` + `embed_reference`. Persistirlos crea un segundo estado que queda obsoleto en cuanto se edita el original. Se calculan al servir (`Task/009`, `Task/014`). |
| D-P | **Sin superentidad `Content`** | Herencia (STI/JTI) · tabla `content` única · EAV | **Una tabla por tipo, columnas repetidas** | `Post`, `BookReview`, `Video` y `Project` tienen semántica distinta —`Video` no tiene `content` en Markdown; `BookReview` tiene libro y valoración; `Project` tiene un segundo estado—. La repetición de unas cuantas columnas es más barata que una jerarquía que después hay que deshacer. Solo se comparten *mixins* **técnicos**: identidad y marcas de tiempo. |

---

## 4. Tablas

Convención de nombres vigente desde `Task/005`: `pk_<tabla>`, `uq_<tabla>_<col>`,
`ck_<tabla>_<nombre>`, `fk_<tabla>_<col>_<tabla_referida>`, `ix_<tabla>_<col>`.

Todas las tablas de contenido comparten: `id UUID PK`, `created_at TIMESTAMPTZ NOT NULL`,
`updated_at TIMESTAMPTZ NOT NULL`.

### 4.1 `media_assets`

Metadatos y **clave del objeto**, nunca el binario y nunca una URL prefirmada.

| Columna | Tipo | Nulo | Notas |
| --- | --- | :---: | --- |
| `id` | `UUID` | no | PK |
| `object_key` | `VARCHAR(512)` | no | **`UNIQUE`**: dos filas no pueden reclamar el mismo objeto |
| `original_filename` | `VARCHAR(255)` | no | informativo |
| `mime_type` | `VARCHAR(127)` | no | validación de tipo: `Task/010` |
| `size_bytes` | `BIGINT` | no | `CHECK > 0` |
| `width`, `height` | `INTEGER` | sí | `CHECK NULL OR > 0` |
| `alt_text` | `VARCHAR(255)` | sí | accesibilidad (A-04); exigirlo es de `Task/010` |
| `checksum` | `VARCHAR(64)` | sí | SHA-256 hex; **indexado** para detectar duplicados |
| `created_at` | `TIMESTAMPTZ` | no | sin `updated_at`: CONTENT_MODEL.md solo declara la fecha de carga |

**Checks:** `ck_media_assets_tamano_positivo`, `ck_media_assets_ancho_positivo`,
`ck_media_assets_alto_positivo`. **Índices:** `ix_media_assets_checksum`.

### 4.2 `tags`

| Columna | Tipo | Nulo | Notas |
| --- | --- | :---: | --- |
| `slug` | `VARCHAR(160)` | no | **`UNIQUE`** |
| `name` | `VARCHAR(80)` | no | nombre visible |
| `description` | `VARCHAR(500)` | sí | |

### 4.3 `profiles`

| Columna | Tipo | Nulo | Notas |
| --- | --- | :---: | --- |
| `is_singleton` | `BOOLEAN` | no | `DEFAULT TRUE`, **`UNIQUE`**, `CHECK IS TRUE` — cerrojo |
| `full_name` | `VARCHAR(120)` | no | |
| `headline` | `VARCHAR(200)` | sí | |
| `biography` | `TEXT` | no | Markdown fuente, `DEFAULT ''` |
| `contact_email` | `VARCHAR(254)` | sí | |
| `photo_id` | `UUID` | sí | → `media_assets`, `RESTRICT`, indexado |
| `seo_title` | `VARCHAR(70)` | sí | |
| `seo_description` | `VARCHAR(160)` | sí | |

**Sin `status` ni `published_at`**: el perfil siempre existe y siempre está visible.

### 4.4 `profile_social_links`

| Columna | Tipo | Nulo | Notas |
| --- | --- | :---: | --- |
| `profile_id` | `UUID` | no | → `profiles`, **`CASCADE`**, indexado |
| `label` | `VARCHAR(60)` | no | |
| `url` | `VARCHAR(2048)` | no | |
| `display_order` | `SMALLINT` | no | `CHECK >= 0`; `UNIQUE (profile_id, display_order)` |

`display_order` y no `position`: `position` es también una función de SQL.
Es la **única** cascada del modelo que arrastra entidades, y lo hace porque un enlace
social no existe fuera de su perfil.

### 4.4.1 Qué puede exigir el esquema al crear un borrador

USER_FLOWS.md B.2 es la fuente, y es taxativo:

> *Introduce título; el **slug se propone automáticamente** y es editable. El contenido
> nace en estado `draft`. Se registran `created_at` y `updated_at`.*
> **Validación:** slug único por tipo de contenido; título obligatorio.

En ese instante existen **dos** valores de negocio: el título que escribe la persona y el
slug que propone la aplicación. Cualquier otra columna `NOT NULL` sin default obligaría a
**inventar** un dato, y un valor inventado en la base es peor que un nulo: parece real.

| Tipo | Obligatorio al `INSERT` de un borrador | Fuente que lo justifica |
| --- | --- | --- |
| **Los cuatro** | `id` | lo genera la aplicación antes de persistir (D-A) |
| **Los cuatro** | `slug` | B.2: la aplicación lo propone |
| **Los cuatro** | `title` | B.2: *"título obligatorio"* |
| **Los cuatro** | `status` → default `draft` | B.2: *"el contenido nace en estado `draft`"* |
| **Los cuatro** | `created_at`, `updated_at` → default `now()` | B.2: *"se registran"* |
| **Los cuatro** | `featured` → default `false` | un contenido nuevo no está destacado |
| `Post`, `BookReview`, `Project` | `content` → default `''` | un borrador sin cuerpo **es** una cadena vacía |
| `Project` | `project_status` → default `active` | un proyecto recién creado está activo |
| `Project` | `technologies` → default `'[]'` | la lista todavía está vacía, y eso es cierto |

**Nada más.** Todo lo demás admite nulo. Los defaults de esta tabla son valores
**semánticamente reales**, no rellenos para esquivar un `NOT NULL`.

Qué campos debe tener un contenido **para publicarse** es otra pregunta —USER_FLOWS.md
B.7: *"se validan los campos mínimos"*— y su dueña es **`Task/012`**. El esquema tiene que
poder **representar** un borrador incompleto; impedir que se publique así es otra capa.

> **Detectado en la revisión pre-approval de `Task/008`.** `book_reviews.book_title`,
> `book_reviews.book_author`, `videos.provider` y `videos.video_url` eran `NOT NULL`:
> crear un borrador de review o de vídeo era **imposible** sin inventar datos. La guarda
> que impide que el defecto reaparezca por otra columna vive en
> `tests/integration/test_borrador_minimo.py`, y recorre las columnas reales en lugar de
> una lista escrita a mano.

### 4.5 `posts`

| Columna | Tipo | Nulo | Notas |
| --- | --- | :---: | --- |
| `slug` | `VARCHAR(160)` | no | **`UNIQUE`** |
| `title` | `VARCHAR(200)` | no | |
| `summary` | `VARCHAR(500)` | sí | fallback de `seo_description` |
| `content` | `TEXT` | no | Markdown fuente, `DEFAULT ''` |
| `status` | `VARCHAR(32)` | no | `CHECK IN ('draft','published','archived')`, `DEFAULT 'draft'` |
| `published_at` | `TIMESTAMPTZ` | sí | fecha de la **primera** publicación |
| `featured` | `BOOLEAN` | no | `DEFAULT FALSE` |
| `cover_id` | `UUID` | sí | → `media_assets`, `RESTRICT`, indexado |
| `seo_title` | `VARCHAR(70)` | sí | |
| `seo_description` | `VARCHAR(160)` | sí | |

**Checks:** `ck_posts_post_status`, `ck_posts_publicado_exige_fecha`.
**Índices:** `ix_posts_status_published_at`, `ix_posts_cover_id`.

### 4.6 `book_reviews`

Todo lo de `posts`, más:

| Columna | Tipo | Nulo | Notas |
| --- | --- | :---: | --- |
| `book_title` | `VARCHAR(200)` | **sí** | puede diferir de `title`; nulo en un borrador recién creado |
| `book_author` | `VARCHAR(200)` | **sí** | nulo en un borrador recién creado |
| `rating` | `SMALLINT` | sí | `CHECK rating >= 1 AND rating <= 5` |
| `external_link` | `VARCHAR(2048)` | sí | |

### 4.7 `videos`

Sin `content`: el contenido principal es el vídeo externo (ADR-005, decisión 7).

| Columna | Tipo | Nulo | Notas |
| --- | --- | :---: | --- |
| `provider` | `VARCHAR(32)` | **sí** | **sin `CHECK`**: la lista cerrada es de `Task/014`; nulo en un borrador |
| `video_url` | `VARCHAR(2048)` | **sí** | nulo hasta que se pegue la URL (B.3) |
| `embed_reference` | `VARCHAR(255)` | sí | |
| `duration_seconds` | `INTEGER` | sí | `CHECK NULL OR > 0` |
| `thumbnail_id` | `UUID` | sí | → `media_assets`, `RESTRICT`, indexado |

### 4.8 `projects`

Todo lo de `posts`, más:

| Columna | Tipo | Nulo | Notas |
| --- | --- | :---: | --- |
| `project_status` | `VARCHAR(32)` | no | `CHECK IN ('active','paused','completed')`, `DEFAULT 'active'` |
| `technologies` | `JSONB` | no | lista de cadenas, `DEFAULT '[]'` |
| `repository_url` | `VARCHAR(2048)` | sí | |
| `demo_url` | `VARCHAR(2048)` | sí | |

### 4.9 `administrators`

| Columna | Tipo | Nulo | Notas |
| --- | --- | :---: | --- |
| `is_singleton` | `BOOLEAN` | no | cerrojo, igual que `profiles` |
| `email` | `VARCHAR(254)` | no | **`UNIQUE`** |
| `password_hash` | `VARCHAR(255)` | no | **columna, no credencial**: el algoritmo es de `Task/011` |
| `display_name` | `VARCHAR(120)` | no | |
| `last_login_at` | `TIMESTAMPTZ` | sí | lo escribe `Task/011` |
| `failed_login_attempts` | `INTEGER` | no | `DEFAULT 0`, `CHECK >= 0` |
| `locked_until` | `TIMESTAMPTZ` | sí | lo escribe `Task/011` |

### 4.10 `audit_events`

| Columna | Tipo | Nulo | Notas |
| --- | --- | :---: | --- |
| `occurred_at` | `TIMESTAMPTZ` | no | `DEFAULT now()`, **indexado** |
| `actor_id` | `UUID` | sí | → `administrators`, `RESTRICT`, indexado. Nulo: un intento de acceso fallido se audita sin actor conocido |
| `action` | `VARCHAR(64)` | no | **sin `CHECK`**: el catálogo es de `Task/011`/`Task/012` |
| `entity_type` | `VARCHAR(64)` | no | parte de la referencia polimórfica |
| `entity_id` | `UUID` | sí | nulo: iniciar sesión no afecta a ningún elemento |
| `request_id` | `VARCHAR(64)` | sí | correlation ID; **indexado** |
| `metadata` | `JSONB` | no | `DEFAULT '{}'` · atributo Python `event_metadata` |
| `ip_address` | `VARCHAR(45)` | sí | IPv6 y formas IPv4 mapeadas |

**Sin `updated_at`**, y la ausencia es el diseño: lo que no se modifica no necesita
fecharse.

### 4.11 Tablas puente

`post_tags`, `book_review_tags`, `video_tags`, `project_tags`.

| Columna | Tipo | Notas |
| --- | --- | --- |
| `<contenido>_id` | `UUID` | → tabla de contenido, **`CASCADE`**, parte de la PK |
| `tag_id` | `UUID` | → `tags`, **`CASCADE`**, parte de la PK, **indexado aparte** |

El índice de la PK empieza por la columna de contenido y no sirve para la consulta
inversa —"qué contenido lleva esta etiqueta"—, que es el filtro público por etiqueta.

---

## 5. Estrategia *singleton*: qué garantiza el esquema y qué no

La distinción importa y se registra sin adornos.

| Afirmación | Quién la garantiza | Cómo |
| --- | --- | --- |
| **Como máximo un** `Profile` | **PostgreSQL** | `UNIQUE (is_singleton)` + `CHECK (is_singleton IS TRUE)` |
| **Como máximo un** `Administrator` | **PostgreSQL** | igual |
| El correo del administrador es único | **PostgreSQL** | `UNIQUE (email)` |
| **Exactamente un** `Profile` y un `Administrator` en **producción** | **`Task/036-Publicar-Primer-Contenido`** | enumera explícitamente "migraciones, **administrador**, **perfil**, artículo, review, video, imágenes" |
| Datos **semilla** en el entorno local | **`Task/022-Validacion-Local-Production-Like`** | incluye la "carga de datos semilla" |
| El perfil no se crea ni se elimina por API | **`Task/012`** | solo expone lectura y edición |

**Por qué el esquema no puede prometer "exactamente uno".** Una base recién migrada está
vacía, y garantizarlo exigiría sembrar una fila. Esa fila contendría el nombre real, el
correo y el hash de contraseña del propietario: datos personales y una credencial, que
**no se versionan** (requisito S-10).

**Los dos propietarios están asignados en el ROADMAP; no se inventan aquí.**
`Task/036-Publicar-Primer-Contenido` es la tarea que crea el administrador y el perfil
reales en producción, y `Task/022-Validacion-Local-Production-Like` la que carga los datos
semilla en local. `Task/012` es dueña de **editar** el perfil por API, que no es lo mismo
que crearlo por primera vez.

> *Corregido en la revisión pre-approval de `Task/008`:* aquí se leía "el *bootstrap* del
> entorno … `Task/012` o posterior", una atribución vaga que además apuntaba a la tarea
> equivocada.

---

## 6. Ownership de invariantes

Cada invariante tiene **un** dueño principal. Donde hay dos, cada capa protege de algo
distinto, y eso se declara.

| # | Invariante | Dominio | PostgreSQL | Tarea futura | Por qué ahí |
| --- | --- | :---: | :---: | :---: | --- |
| 1 | Un contenido `published` tiene `published_at` | **sí** | **sí** | — | El dominio lo hace irrepresentable y da un error de aplicación; la base defiende de cualquier camino que no pase por el dominio |
| 2 | Un `draft` **puede** tener `published_at` | **sí** | — | — | Ausencia deliberada de restricción: es el resultado de despublicar |
| 3 | Qué transiciones son válidas | **sí** | — | — | Es una regla de comportamiento; SQL no sabe expresar "de dónde vengo" |
| 4 | `published → draft` solo en `Post` y `BookReview` | **sí** | — | — | Se expresa por **ausencia** del método en `Video` y `Project` |
| 5 | `archived` es terminal en el MVP | **sí** | — | `Task/012`+ | Restaurar no es obligatorio en el MVP; no se implementa por anticipado |
| 6 | `rating` entre 1 y 5 | **sí** | **sí** | — | Dominio: rechazo inmediato y sin base de datos. Base: última línea frente a cargas manuales |
| 7 | `slug` único por tipo | — | **sí** | — | Es unicidad, exactamente lo que un índice único garantiza |
| 8 | Formato y generación del `slug` | — | — | **`Task/012`** | El slug se propone desde el título al crear el borrador (B.2) |
| 9 | `status` dentro del contrato cerrado | **sí** | **sí** | — | El tipo lo impone en Python; el `CHECK`, en la base |
| 10 | Asociación a etiqueta sin duplicados | — | **sí** | — | Clave primaria compuesta |
| 11 | Eliminar `Tag` desasocia, no borra contenido | — | **sí** | — | `ON DELETE CASCADE` sobre la tabla puente |
| 12 | Un `MediaAsset` en uso no se elimina | — | **sí** | **`Task/010`** | Base: `RESTRICT`, infranqueable. `Task/010`: comprobación previa que dice **dónde** se usa (B.5) |
| 13 | La base guarda claves de objeto, no binarios ni URL prefirmadas | — | **sí** | **`Task/010`** | El esquema no tiene columna binaria ni de URL; generarla al servir es de `Task/010` |
| 14 | Como máximo un `Profile` / `Administrator` | — | **sí** | — | Cerrojo único |
| 15 | Exactamente uno en operación | — | — | *bootstrap* | Ver §5 |
| 16 | La **ruta normal del ORM** no modifica ni elimina un `AuditEvent` | — | — | **persistencia** (`Task/008`) | Guarda en el *mapper*, con el perímetro fijado por prueba (§6.2) |
| 16b | **Ninguna** ruta puede modificarlo ni eliminarlo | — | — | **`Task/018`** | Solo se consigue retirando `UPDATE`/`DELETE` al rol de base de datos (S-01) |
| 17 | La auditoría no guarda secretos | — | — | **`Task/011`**, **`Task/012`** | Es una decisión sobre **qué se escribe**; el esquema no puede saberlo |
| 18 | Campos mínimos para publicar | — | — | **`Task/012`** | Es validación de publicación (B.7) |
| 19 | Contenido no publicado nunca sale al público | — | — | **`Task/009`** ✔ | Es una regla de consulta, no de esquema. **Implementada el 2026-08-26**: la condición vive dentro de cada consulta de lectura, no en el router, de modo que ningún camino puede saltársela. Cubierta por caso negativo en los cuatro tipos, en listados, detalles, filtro por etiqueta, catálogo de etiquetas y búsqueda |
| 20 | Toda fecha en UTC | — | **sí** | — | `TIMESTAMP WITH TIME ZONE` en todas las columnas de fecha |

### 6.0 Qué garantiza exactamente la inmutabilidad de `AuditEvent`

Se midió, no se supuso. Contra PostgreSQL real, sobre `audit_events`:

| Ruta de escritura | ¿La guarda la detiene? |
| --- | :---: |
| `evento.action = …` + `flush` (unidad de trabajo del ORM) | **sí** |
| `session.delete(evento)` + `flush` | **sí** |
| `session.execute(update(AuditEvent)…)` — DML masivo del ORM | **no** |
| `session.execute(delete(AuditEvent)…)` — DML masivo del ORM | **no** |
| Sentencia de nivel Core sobre la tabla, o SQL escrito a mano | **no** |

**La formulación correcta, y la única que se sostiene:** *la ruta normal de
escritura del ORM está cerrada*. Decir "la aplicación no puede modificar un
evento" sería **falso**, porque una sentencia masiva del ORM es código de
aplicación perfectamente válido y la sortea.

Esto **no se cierra con más enganches** —siempre queda una ruta más—, sino
retirando `UPDATE` y `DELETE` sobre `audit_events` al rol de base de datos de la
aplicación: privilegio mínimo (requisito S-01), propiedad de **`Task/018`**.

El perímetro está fijado por prueba en `tests/integration/test_auditoria.py`, que
comprueba **las dos mitades**: lo que se bloquea y lo que no. Ese segundo grupo
está escrito para **ponerse rojo el día que el hueco se cierre**, de modo que la
documentación no pueda quedarse afirmando de menos.

> **Detectado en la revisión pre-approval de `Task/008`.** La primera redacción
> de este documento decía que la aplicación no podía modificar un evento. Era
> más de lo que el código entrega.

### 6.1 El precio de la referencia polimórfica

`entity_type` + `entity_id` **no tienen clave foránea**, así que la base **no puede
garantizar** que apunten a algo que exista. Es integridad que el esquema no ofrece, y
quien lea el historial debe contar con referencias a elementos ya eliminados.

Se acepta porque un registro histórico describe **lo que pasó**, no lo que sigue
existiendo: una clave foránea o borraría el historial con el elemento, o impediría
borrarlo. Los UUID acotan el daño —una referencia con el tipo equivocado no coincide con
ninguna fila de ninguna tabla—, cosa que no ocurriría con enteros secuenciales.

---

## 7. Ciclo de vida del contenido

```
draft ──publicar──> published ──archivar──> archived
  ^                     │                       │
  └────despublicar──────┘                       │
       (solo Post y BookReview)                 │
  ^                                             │
  └──────────restaurar: fuera del MVP───────────┘
```

| Tipo | `draft → published` | `published → draft` | `→ archived` | `archived → *` |
| --- | :---: | :---: | :---: | :---: |
| `Post` | sí | **sí** | sí | no (fuera del MVP) |
| `BookReview` | sí | **sí** | sí | no |
| `Video` | sí | **no** | sí | no |
| `Project` | sí | **no** | sí | no |
| `Profile` | no aplica: sin estado | | | |

### Semántica final de `published_at`

Reconcilia dos redacciones que podían leerse como contradictorias:

1. Un contenido que **nunca** se ha publicado tiene `published_at = NULL`.
2. Al publicarlo **por primera vez**, se fija.
3. Al **despublicarlo**, `published_at` **se conserva** como referencia histórica (B.8).
4. Por tanto **un `draft` previamente publicado puede tener `published_at`**, y eso es
   correcto.
5. Al **volver a publicar**, la fecha original **no** se reescribe: es la fecha de la
   primera publicación, no de la última.

**Restricción segura:** `status = 'published' → published_at IS NOT NULL`.
**Restricción prohibida:** `status = 'draft' → published_at IS NULL`, que rompería la
despublicación prevista.

La tabla de CONTENT_MODEL.md §2 decía de forma abreviada «nulo mientras sea `draft`». Se
lee como *«nulo mientras no se haya publicado nunca»*: describe el caso normal, no una
restricción.

---

## 8. Índices y la consulta que justifica cada uno

Se diseñan por consulta prevista, no por intuición (requisito P-08).

| Índice | Consulta que lo justifica |
| --- | --- |
| `uq_<tipo>_slug` (5) | `GET /api/v1/{tipo}/{slug}` — acceso por slug (A.3, A.5, A.7) |
| `ix_<tipo>_status_published_at` (4) | Listado público: `status = 'published' ORDER BY published_at DESC` (A.2, api-contracts §6) |
| `ix_<tipo>_cover_id` · `ix_videos_thumbnail_id` · `ix_profiles_photo_id` (5) | Comprobación de uso previa al borrado de un medio (B.5). PostgreSQL **no** indexa las claves foráneas por su cuenta |
| `ix_<puente>_tag_id` (4) | Filtro público por etiqueta (A.9): el índice de la PK empieza por la columna de contenido |
| `ix_media_assets_checksum` | Detección de duplicados al subir (CONTENT_MODEL.md §3.7) |
| `ix_profile_social_links_profile_id` | Enlaces de un perfil |
| `ix_audit_events_occurred_at` | Listado cronológico del historial |
| `ix_audit_events_entity_type_entity_id` | "Qué le pasó a este elemento": la única forma de recorrer la referencia polimórfica sin escanear |
| `ix_audit_events_request_id` | Trazabilidad extremo a extremo por correlation ID (api-contracts §9) |
| `ix_audit_events_actor_id` | Clave foránea `RESTRICT`; evita escaneo al comprobarla |

**Índices considerados y NO creados**, con su razón:

| Candidato | Por qué no |
| --- | --- |
| `featured` | Los listados de destacados son diminutos y siempre van combinados con `status`. `Task/009` implementó las consultas reales y **confirmó la decisión**: el filtro se resuelve siempre junto a `status`, que ya está indexado |
| Búsqueda de texto completo | **Resuelto en `Task/009`**: no se crea ninguno. Ver abajo |
| `slug` en las tablas puente | No existe esa columna: el puente se recorre por identificador |

### 8.1 Búsqueda: mecanismo elegido y por qué no lleva índice

> **Cerrado en `Task/009-API-Publica`** (2026-08-26). `Task/008` dejó abiertos el
> mecanismo de búsqueda **y** los índices que ese mecanismo necesitara. Los dos se
> deciden juntos, porque el segundo depende del primero.

**Mecanismo: `ILIKE '%término%'`**, con el término ligado como parámetro y sus comodines
(`%`, `_`, `\`) escapados. Las alternativas se descartaron con motivo:

| Alternativa | Por qué no |
| --- | --- |
| `pg_trgm` | Es una **extensión**, y el requisito T-02 restringe el proyecto al núcleo de PostgreSQL |
| *Full-text* nativo (`tsvector`) | Obligaría a elegir configuración de idioma y aplica *stemming*, y **no encuentra subcadenas**: «doc» no encontraría «docker», que es justo lo que espera quien teclea en un buscador |
| Elasticsearch, OpenSearch, Meilisearch, Algolia | Un servicio más que operar y pagar, para un blog personal. Fuera del MVP |

**Índices: ninguno, y esa es la decisión.** Ningún índice B-tree sirve a un `LIKE` con
comodín inicial; el que serviría exige `pg_trgm`, que está prohibido, o cambiar de
mecanismo a `tsvector`. **Crear un índice que el planificador no va a usar es peor que no
crearlo**: ocupa espacio, encarece cada escritura y sugiere una garantía de rendimiento
que no existe.

**Por tanto `Task/009` no modifica el esquema físico.** No añade migración: la revisión
`0002` sigue siendo `head`.

**Disparador de revisión.** La decisión es correcta para el volumen previsto —decenas de
filas, donde el escaneo secuencial es irrelevante—, no para siempre. Se revisa cuando el
contenido publicado supere el orden de **unos pocos miles de filas** o cuando la búsqueda
aparezca como consulta lenta en observabilidad (`Task/017`). El camino en ese caso es
`tsvector` con un índice GIN, ambos del **núcleo** de PostgreSQL, aceptando entonces de
forma explícita el cambio de semántica: se ganan lexemas y se pierden las subcadenas.

---

## 9. Markdown

Se almacena **Markdown fuente** en `profiles.biography`, `posts.content`,
`book_reviews.content` y `projects.content`. `videos` **no** tiene contenido Markdown.

**No se almacena HTML renderizado en ninguna forma.** El render y la sanitización ocurren
en el frontend (ADR-005, decisiones 2 a 4) y son de `Task/014` y `Task/015`.

---

## 10. Deuda y límites conocidos

| # | Límite | Dueño |
| --- | --- | --- |
| 1 | `updated_at` solo avanza en escrituras que pasan por el ORM. Un `UPDATE` a mano no la actualiza: haría falta un *trigger*, que es código de servidor que el proyecto evita | — (aceptado y documentado) |
| 2 | La referencia polimórfica de auditoría no tiene integridad referencial (§6.1) | — (aceptado) |
| 3 | `technologies` no tiene integridad sobre su contenido ni consulta relacional (D-G) | **Revisado en `Task/009`: se mantiene.** La API pública lo transporta como lista de cadenas y **nadie consulta por tecnología**; el filtro público es por `Tag`, y funciona. Normalizarlo sigue siendo una migración sencilla el día que aparezca «filtrar por tecnología» |
| 4 | La retención de `AuditEvent` sigue sin decidirse | `Task/011`, operación |
| 5 | El perfil y el administrador reales no existen todavía | `Task/036` (producción) · `Task/022` (semilla local) |
| 6 | La lista de proveedores de vídeo permitidos está abierta | `Task/014` |
| 7 | El formato y la generación del *slug* no están implementados | `Task/012` |
| 8 | SQLAlchemy no detecta mutaciones **en sitio** de un `JSONB`: hay que asignar un valor nuevo | — (documentado en el modelo) |
| 9 | La búsqueda es `ILIKE` sin índice: correcta al volumen actual, revisable con su disparador (§8.1) | revisión futura |
| 10 | Las referencias públicas a `MediaAsset` viajan **sin campo de acceso**: `alt_text`, `width` y `height`, nunca `object_key` ni una URL | **`Task/010`**, que añade el acceso como campo compatible |
