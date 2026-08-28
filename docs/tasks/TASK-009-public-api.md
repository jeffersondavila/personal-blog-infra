# TASK-009 — API Pública

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/009-API-Publica` |
| **Nombre** | API Pública |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Estado** | **Aprobada** (2026-08-27) |
| **Repositorios involucrados** | `personal-blog-backend` · `personal-blog-infra` |
| **Repositorio NO modificado** | `personal-blog-frontend` — sin rama y sin cambios |
| **Dependencias** | `Task/008-Modelo-de-Datos` (**Aprobada** el 2026-08-25) |
| **Rama** | `Task/009-API-Publica` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base (backend)** | `0ada6a73aa69d3fa7d401f24e130fee059977aa2` |
| **SHA base (infra)** | `71f56da2cc0523feae961b54ccbf0322b68826b8` |
| **Fecha de inicio** | 2026-08-26 |
| **Última actualización** | 2026-08-27 — remediación TDD, revalidación y **aprobación** |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

| # | Comprobación | backend | infra |
| --- | --- | --- | --- |
| 1 | `main == origin/main` | ✔ `0ada6a73` | ✔ `71f56da2` |
| 2 | Working tree limpio antes de crear la rama | ✔ vacío | ✔ vacío |
| 3 | Rama creada **desde `main`** | ✔ | ✔ |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | ✔ idénticos | ✔ idénticos |
| 5 | `git rev-list --count main..HEAD` | ✔ `0` | ✔ `0` |

`personal-blog-frontend`: **sin rama**. `main` en `fd62f221…`, árbol limpio.

Invariantes de integración verificados antes de empezar, en backend e infra:
`git merge-base --is-ancestor main dev` → `0`; `git rev-list --count dev..main` → `0`;
`git diff main dev` → vacío.

---

## 1. Objetivo

Implementar la **API pública de solo lectura** del MVP sobre el modelo aprobado por
`Task/008`: perfil, artículos, reviews, videos, proyectos, etiquetas y búsqueda, con
paginación, filtros, orden determinista y la garantía verificable de que **nunca** se
expone contenido `draft` ni `archived`.

## 2. Contexto

`Task/008` dejó el esquema físico y las invariantes de dominio, pero ninguna consulta.
La invariante 19 de [`data-model.md`](../architecture/data-model.md) §6 —«contenido no
publicado nunca sale al público»— está explícitamente asignada a **`Task/009`**: es una
regla de **consulta**, no de esquema, y hasta ahora no existía consulta que pudiera
cumplirla o romperla.

[`api-contracts.md`](../architecture/api-contracts.md) §11 asigna a `Task/009` los
esquemas concretos de respuesta, los valores por defecto y máximos de `page_size`, la
política de filtros desconocidos y la especificación OpenAPI resultante.

## 3. Dentro del alcance

- [x] `GET /api/v1/profile`
- [x] `GET /api/v1/posts` · `GET /api/v1/posts/{slug}`
- [x] `GET /api/v1/book-reviews` · `GET /api/v1/book-reviews/{slug}`
- [x] `GET /api/v1/videos`
- [x] `GET /api/v1/projects` · `GET /api/v1/projects/{slug}`
- [x] `GET /api/v1/tags`
- [x] `GET /api/v1/search`
- [x] Paginación compartida (`app/shared/pagination`), aplazada explícitamente hasta aquí
- [x] Filtros `tag`, `featured` y `sort` con lista cerrada
- [x] Búsqueda básica sobre contenido publicado
- [x] DTO públicos explícitos, sin exponer modelos ORM
- [x] Suite `tests/contract/` — primera vez que hay contrato HTTP que probar
- [x] Cierre documental de las decisiones que `api-contracts.md` dejó abiertas

## 4. Fuera del alcance

| Excluido | Dueño |
| --- | --- |
| `GET /api/v1/videos/{slug}` | **No existe en el contrato canónico.** No se inventa |
| `ObjectStorage`, `MinIOStorage`, `S3Storage`, boto3, URL prefirmadas, subidas | `Task/010` |
| Autenticación, sesión, hashing, rate limiting, `/api/v1/admin/*` | `Task/011` |
| `POST`/`PUT`/`PATCH`/`DELETE` de contenido, publicar, archivar, CRUD de etiquetas | `Task/012` |
| Render y sanitización de Markdown a HTML | `Task/014`, `Task/015` |
| Meta tags, canonical, Open Graph, sitemap | `Task/016` |
| `GET /ready`, correlation ID de extremo a extremo, observabilidad | `Task/017` |
| Auditoría de lecturas | **Ninguno**: los flujos públicos no escriben (USER_FLOWS, reglas transversales 1) |
| Frontend, cloud, Terraform | Etapas posteriores |

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Paginación y orden compartidos | backend | `app/shared/pagination/` |
| Rechazo de query params desconocidos | backend | `app/api/query_params.py` |
| Routers, esquemas y consultas por módulo | backend | `app/modules/{posts,book_reviews,videos,projects,profile,tags,search}/` |
| Suite de contrato HTTP | backend | `tests/contract/` |
| Suite de integración de la API | backend | `tests/integration/test_api_*.py` |
| Ficha y reporte | infra | `docs/tasks/`, `docs/task-reports/` |
| Cierre de decisiones abiertas | infra | `docs/architecture/api-contracts.md`, `data-model.md` |

## 6. Criterios de aceptación

1. Los **diez** endpoints públicos del contrato existen y responden.
2. No existe `GET /videos/{slug}`.
3. Toda colección está paginada; ninguna devuelve "todo".
4. Página fuera de rango produce `200` con `items` vacío, nunca `404`.
5. `page_size` por encima del máximo se recorta; no es error.
6. `page=0`, `page=abc`, `page_size=0` y `sort` desconocido producen `422` con el envelope común.
7. Orden por defecto `published_at DESC`, **determinista** ante empates.
8. `tag` filtra por las asociaciones reales de `Task/008`.
9. Listados, detalles y búsqueda **solo** ven `published`.
10. `draft` y `archived` no son enumerables: mismo `404` que un slug inexistente.
11. Ningún DTO devuelve un modelo ORM ni expone identidad interna sin justificación.
12. OpenAPI documenta exactamente estos endpoints y ninguno administrativo.
13. Ciclo test-first demostrado por *slice*, con PostgreSQL real. Nunca SQLite.
    **Estado: cumplido para la implementación candidata**, tras la remediación descrita en
    §12.1 — no en la primera ejecución.
14. `personal-blog-frontend` intacto.

---

## 7. TDD / Plan test-first

### 7.1 Contrato cerrado — endpoint a esquema

| Endpoint | Query params | Respuesta `200` | `404` | `422` |
| --- | --- | --- | --- | --- |
| `GET /profile` | *(ninguno)* | `ProfilePublico` | perfil no existe | — |
| `GET /posts` | `page`, `page_size`, `tag`, `featured`, `sort` | `Pagina[PostDeListado]` | — | params inválidos |
| `GET /posts/{slug}` | *(ninguno)* | `PostDetallado` | inexistente · `draft` · `archived` | — |
| `GET /book-reviews` | `page`, `page_size`, `tag`, `featured`, `sort` | `Pagina[ReviewDeListado]` | — | params inválidos |
| `GET /book-reviews/{slug}` | *(ninguno)* | `ReviewDetallada` | inexistente · `draft` · `archived` | — |
| `GET /videos` | `page`, `page_size`, `tag`, `featured`, `sort` | `Pagina[VideoDeListado]` | — | params inválidos |
| `GET /projects` | `page`, `page_size`, `tag`, `featured`, `sort` | `Pagina[ProyectoDeListado]` | — | params inválidos |
| `GET /projects/{slug}` | *(ninguno)* | `ProyectoDetallado` | inexistente · `draft` · `archived` | — |
| `GET /tags` | `page`, `page_size` | `Pagina[EtiquetaPublica]` | — | params inválidos |
| `GET /search` | `q` **(obligatorio)**, `page`, `page_size` | `Pagina[ResultadoDeBusqueda]` | — | `q` ausente o inválido |

### 7.2 Contrato cerrado — query params

| Parámetro | Tipo | Regla | Inválido |
| --- | --- | --- | --- |
| `page` | entero | `>= 1`, por defecto `1`. Fuera de rango produce `200` vacío | `422` |
| `page_size` | entero | `>= 1`, por defecto **12**, máximo **50**; por encima **se recorta** | `422` solo si es menor que 1 o no es entero |
| `tag` | cadena | Slug de etiqueta. Inexistente produce `200` vacío | — |
| `featured` | `true` \| `false` | Literal exacto. `true` solo destacados; `false` solo no destacados; ausente sin filtro | `422` |
| `sort` | cadena | Lista cerrada: `published_at`, `-published_at`, `title`, `-title` | `422` |
| `q` | cadena | Obligatorio, 2..100 tras recortar espacios | `422` |
| *cualquier otro* | — | **Se rechaza** | `422` |

`status` **no existe** como parámetro público: no aparece en OpenAPI y, por la política de
parámetros desconocidos, enviarlo produce `422`. No hay forma de pedir `draft` ni `archived`.

### 7.3 Envoltura de colección

```json
{ "items": [], "page": 1, "page_size": 12, "total": 0, "pages": 0 }
```

`page_size` es el **aplicado** (recortado). `pages = ceil(total / page_size)`, y `0` si
`total = 0`.

### 7.4 DTO públicos — campo por campo

Leyenda: **L** listado · **D** detalle.

#### `Post`

| Campo | L | D | Motivo |
| --- | :---: | :---: | --- |
| `slug` | ✔ | ✔ | Identidad pública (api-contracts §1) |
| `title` | ✔ | ✔ | A.2, A.3 |
| `summary` | ✔ | ✔ | A.2 "resumen" |
| `published_at` | ✔ | ✔ | A.2, A.3 "fecha" |
| `tags` | ✔ | ✔ | A.2, A.3 "etiquetas" |
| `cover` | ✔ | ✔ | A.2, A.3 "portada" |
| `content` | — | ✔ | Markdown fuente (A.3). No se carga en listados: P-08 |
| `reading_time_minutes` | — | ✔ | Derivado de `content` (D-O). Solo donde `content` viaja |
| `seo_title`, `seo_description` | — | ✔ | A.3 "title, description"; un listado no tiene página propia |
| `id`, `status`, `featured`, `created_at`, `updated_at` | — | — | Ver §7.5 |

#### `BookReview`

Todo lo de `Post`, más:

| Campo | L | D | Motivo |
| --- | :---: | :---: | --- |
| `book_author` | ✔ | ✔ | A.4 "autor del libro"; A.5 |
| `rating` | ✔ | ✔ | A.4 "valoración"; A.5 |
| `book_title` | ✔ | ✔ | A.5. En listado porque la búsqueda lo consulta: el término debe verse |
| `external_link` | — | ✔ | A.5 "enlace externo si existe" |

#### `Video` — **solo listado**, no hay endpoint de detalle

| Campo | L | Motivo |
| --- | :---: | --- |
| `slug`, `title`, `summary`, `published_at`, `tags` | ✔ | A.6 "título, descripción … fecha" |
| `thumbnail` | ✔ | A.6 "miniatura" |
| `provider`, `video_url`, `embed_reference` | ✔ | A.6 "embed o enlace externo": sin detalle, el listado debe bastar |
| `duration_seconds` | ✔ | CONTENT_MODEL §3.4 "duración, si se conoce" |
| `seo_*` | — | No existe página de detalle de vídeo que documentar |
| `content` | — | **No existe** en el modelo (ADR-005, decisión 7) |

#### `Project`

| Campo | L | D | Motivo |
| --- | :---: | :---: | --- |
| `slug`, `title`, `summary`, `published_at`, `tags`, `cover` | ✔ | ✔ | A.7 |
| `technologies` | ✔ | ✔ | A.7 "tecnologías" |
| `repository_url`, `demo_url` | ✔ | ✔ | A.7 "enlaces (repositorio, demo)" |
| `project_status` | ✔ | ✔ | CONTENT_MODEL §3.5; ortogonal a `status` |
| `content`, `reading_time_minutes`, `seo_*` | — | ✔ | Igual que `Post` |

#### `Profile`

`full_name`, `headline`, `biography` (Markdown), `contact_email`, `photo`, `seo_title`,
`seo_description`, `social_links[{label, url}]` en su orden configurado.
**No** se exponen `id`, `is_singleton`, `created_at`, `updated_at` ni `display_order`
—el orden lo transporta el propio array—.

#### `Tag`

`slug`, `name`, `description`.

#### Referencia a `MediaAsset` (`cover`, `thumbnail`, `photo`)

`alt_text`, `width`, `height`. **Sin URL y sin `object_key`** — ver decisión **D-009-O**.
`null` cuando no hay medio asociado.

#### `ResultadoDeBusqueda`

`type` (`post` \| `book_review` \| `video` \| `project`), `slug`, `title`, `summary`,
`published_at`.

### 7.5 Campos deliberadamente NO expuestos

| Campo | Por qué no |
| --- | --- |
| `id` (UUID) | El público navega por `slug` (api-contracts §1). Los identificadores internos son de la API administrativa (§4). Exponerlos acoplaría el contrato v1 a la identidad interna sin ninguna necesidad demostrada |
| `status` | Estar en la API pública **ya significa** `published`. Un campo constante no informa y sugiere que existen otros valores alcanzables |
| `featured` | Ningún flujo lo necesita: A.1 lo obtiene filtrando. Añadir un campo después es compatible (api-contracts §10.3); quitarlo **no** lo es. Se omite en la dirección reversible |
| `created_at`, `updated_at` | Ningún flujo público los pide. Mismo criterio de reversibilidad |
| `object_key` | Invariante 9 de CONTENT_MODEL: nunca claves de objeto "sin control". Su forma pública es de `Task/010` |
| `password_hash`, `AuditEvent`, `Administrator` | No tienen recurso público alguno |

### 7.6 Matriz de casos

Capas: **C** contrato HTTP (sin base de datos) · **I** integración PostgreSQL real ·
**U** unitaria pura.

| # | Caso | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | :---: |
| **A. Profile** | | | | |
| A-01 | `GET /profile` con perfil existente | 1 perfil | `200`, campos públicos | I |
| A-02 | `GET /profile` sin perfil | base vacía | `404` `resource_not_found` | I |
| A-03 | `social_links` en su orden | 3 enlaces desordenados | orden por `display_order` | I |
| A-04 | El perfil no expone identidad interna | 1 perfil | sin `id`, `is_singleton`, fechas | I |
| **B. Posts — listado** | | | | |
| B-01 | Solo `published` | mezcla de los 3 estados | únicamente publicados | I |
| B-02 | `draft` excluido | 1 draft | ausente | I |
| B-03 | `archived` excluido | 1 archived | ausente | I |
| B-04 | Orden por defecto | fechas distintas | `published_at DESC` | I |
| B-05 | Desempate estable | misma `published_at` | orden por `slug` ASC, estable entre páginas | I |
| B-06 | Paginación | 5 publicados, `page_size=2` | 3 páginas coherentes, sin repetir ni perder | I |
| B-07 | Página fuera de rango | `page=99` | `200`, `items=[]` | I |
| B-08 | Filtro `tag` | 2 con etiqueta, 1 sin | solo los 2 | I |
| B-09 | `featured=true` / `featured=false` | mezcla | subconjunto correcto | I |
| B-10 | `sort=title` / `sort=-title` | títulos distintos | orden alfabético asc/desc | I |
| B-11 | `sort` inválido | `sort=id` | `422` | C |
| B-12 | `tag` inexistente | — | `200`, `items=[]` | I |
| B-13 | `tag` asociado a un draft | draft y published comparten etiqueta | solo el published | I |
| B-14 | Listado sin N+1 | 2 filas vs 10 filas, ambas con etiquetas y portada | mismo número de consultas | I |
| **C. Post — detalle** | | | | |
| C-01 | Slug publicado | — | `200`, incluye `content` y SEO | I |
| C-02 | Slug inexistente | — | `404` `resource_not_found` | I |
| C-03 | Slug de un `draft` | — | **mismo** `404`, cuerpo indistinguible de C-02 | I |
| C-04 | Slug de un `archived` | — | **mismo** `404`, cuerpo indistinguible de C-02 | I |
| C-05 | `reading_time_minutes` | contenido conocido | valor calculado correcto | U |
| **D. BookReviews** | | | | |
| D-01..D-04 | Visibilidad y detalle | como B-01..B-03, C-01..C-04 | idéntico | I |
| D-05 | Campos propios | `rating`, `book_title`, `book_author` | presentes en listado y detalle | I |
| D-06 | `external_link` solo en detalle | — | ausente en listado | I |
| **E. Videos** | | | | |
| E-01 | Solo listado | — | no existe `/videos/{slug}` | C |
| E-02..E-04 | Visibilidad | los 3 estados | solo `published` | I |
| E-05 | Metadata propia | `provider`, `video_url`, `embed_reference`, `duration_seconds`, `thumbnail` | presentes | I |
| **F. Projects** | | | | |
| F-01..F-04 | Listado, detalle y visibilidad | — | idéntico a `Post` | I |
| F-05 | `project_status` y `technologies` | proyecto `paused` con 2 tecnologías | presentes y correctos | I |
| **G. Tags** | | | | |
| G-01 | Paginación | 3 etiquetas | envoltura correcta | I |
| G-02 | Solo etiquetas con contenido publicado | etiqueta usada por published | presente | I |
| G-03 | Etiqueta sin contenido | huérfana | **ausente** | I |
| G-04 | Etiqueta usada solo por `draft` | — | **ausente**: no se infiere contenido no publicado | I |
| G-05 | Etiqueta usada solo por `archived` | — | **ausente** | I |
| G-06 | Etiqueta usada por cualquiera de los 4 tipos | vídeo publicado con etiqueta | presente | I |
| **H. Search** | | | | |
| H-01 | `q` encuentra contenido publicado | término en el título | aparece | I |
| H-02 | `draft` con coincidencia exacta | término solo en un draft | **no aparece** | I |
| H-03 | `archived` con coincidencia exacta | término solo en un archived | **no aparece** | I |
| H-04 | Resultados identificables por tipo | un match de cada tipo | `type` correcto en cada uno | I |
| H-05 | Paginación | 5 coincidencias, `page_size=2` | coherente | I |
| H-06 | Orden | fechas distintas | `published_at DESC`, desempate `(type, slug)` | I |
| H-07 | `q` ausente, vacío o de 1 carácter | — | `422` | C |
| H-08 | Cero resultados | término inexistente | `200`, `items=[]` | I |
| H-09 | Insensible a mayúsculas | `DOCKER` vs `docker` | encuentra | I |
| H-10 | Comodines tratados como dato | `q=%` | no es comodín: no devuelve todo | I |
| H-11 | Campos consultados | término solo en `content` | **no** aparece; solo en `summary` sí | I |
| H-12 | `book_title`/`book_author` consultados | término solo en el autor del libro | aparece | I |
| **I. Paginación** | | | | |
| I-01 | `page` por defecto | sin params | `page=1`, `page_size=12` | C |
| I-02 | `page=0`, `page=-1`, `page=abc` | — | `422` | C |
| I-03 | `page_size` sobre el máximo | `page_size=500` | recortado a `50`, `200` | I |
| I-04 | `page_size=0` o negativo | — | `422` | C |
| I-05 | `total` cuenta el filtro completo | 5 filas, `page_size=2` | `total=5`, no `2` | I |
| I-06 | `pages` correcto | 5 filas, `page_size=2` | `pages=3` | I |
| I-07 | `total=0` | base vacía | `pages=0` | I |
| I-08 | Cálculo de `pages` | tabla de casos | función pura correcta | U |
| **J. Query params** | | | | |
| J-01 | Parámetro desconocido | `?foo=1` | `422` `validation_error` | C |
| J-02 | `status` público | `?status=draft` | `422`: no es un parámetro admitido | C |
| J-03 | Campo arbitrario en `sort` | `sort=content`, `sort=id; DROP TABLE` | `422`, nunca se interpola | C |
| J-04 | La lista de admitidos sale de la ruta | añadir un param lo admite solo | derivación correcta | C |
| **K. Contrato de error** | | | | |
| K-01 | Envelope de `404` | — | `error.{code,message,details,request_id}` | C |
| K-02 | Envelope de `422` | — | mismo envelope, `code=validation_error` | C |
| K-03 | `request_id` presente | — | no vacío | C |
| K-04 | Sin detalles internos | — | sin SQL, traza, ruta ni nombre de clase | C |
| **L. OpenAPI** | | | | |
| L-01 | Rutas exactas | — | las 10 públicas más `/health` | C |
| L-02 | Sin endpoints administrativos | — | ningún `/admin` | C |
| L-03 | Sin `/videos/{slug}` | — | ausente | C |
| L-04 | Solo `GET` | — | ningún `POST`/`PUT`/`PATCH`/`DELETE` | C |
| L-05 | Esquemas documentados | — | modelos de respuesta y `422` | C |
| L-06 | `status` no aparece como parámetro | — | ausente en toda la especificación | C |

### 7.7 Integración necesaria

PostgreSQL real, base `personal_blog_test`, con la guarda *fail-closed* de
`Task/005.6`/`005.7`. Lo exigen: filtros, `JOIN` de etiquetado, orden, conteo,
paginación, `ILIKE` y la propia regla de visibilidad. **SQLite queda prohibido**
(BACKEND_TESTING_STRATEGY §8.3).

### 7.8 Casos negativos y de seguridad

Recurso inexistente, contenido no publicado indistinguible del inexistente, parámetros
inválidos y desconocidos, `sort` arbitrario, comodines de `ILIKE` tratados como dato, y
ausencia de campos internos en toda respuesta.

### 7.9 Regresiones que deben seguir pasando

`tests/test_openapi.py` afirma hoy `list(document["paths"]) == ["/health"]`. **Esa
expectativa cambia legítimamente**: la tarea cuyo objeto es publicar endpoints los añade.
Es el supuesto 1 de BACKEND_TESTING_STRATEGY §9 —el requisito cambió— y se sustituye por
una afirmación equivalente pero exacta sobre el conjunto nuevo, no por una más débil.
El resto de la suite (250 pasan, 1 omitida) debe seguir en verde sin tocarse.

---

## 8. Decisiones de `Task/009`

**Estado de todas las decisiones de esta tabla: `Vigentes`** — promovidas desde
`Propuesta` con la aprobación del 2026-08-27.

| # | Decisión | Alternativas | Elegida | Justificación | Fuente |
| --- | --- | --- | --- | --- | --- |
| **D-009-A** | `page_size` por defecto | 10 · 12 · 20 · 25 | **12** | Es el valor que usan **todos** los ejemplos canónicos: USER_FLOWS A.2, A.4, A.6 y A.8, y la envoltura de api-contracts §5. No se hereda de FastAPI: se declara | USER_FLOWS · api-contracts §5 |
| **D-009-B** | `page_size` máximo | 24 · **50** · 100 · sin límite | **50** | Ninguna fuente lo fija; la decide `Task/009`. 50 son algo más de 4 páginas por defecto: holgura real para un cliente que quiera menos viajes, y cota superior de la consulta (P-02, P-08). "Sin límite" está prohibido: no puede existir un endpoint que devuelva todo | Decisión propia · api-contracts §5 |
| **D-009-C** | Query params desconocidos | Ignorar · **Rechazar** | **Rechazar con `422`** | El proyecto ya es estricto de forma consistente ante claves desconocidas: `Settings` usa `extra="forbid"`, y pytest, `--strict-markers`/`--strict-config`. Ignorar convierte una errata del cliente (`?tagg=docker`) en un listado silenciosamente sin filtrar. Rechazar hace que OpenAPI **sea** el contrato en lugar de describirlo. **Coste aceptado:** un parámetro de analítica añadido a la URL de la API produciría `422`; el frontend no debe reenviarlos, y queda registrado | api-contracts §6 lo delega aquí |
| **D-009-D** | Lista cerrada de `sort` | Solo `published_at` · **`published_at` + `title`** · añadir `rating`, `created_at` | **`published_at`, `title`** | Uniforme en los cuatro listados. `title` es el único orden alternativo con sentido para un visitante. `rating` no lo pide ningún flujo y crearía una divergencia por tipo; añadirlo después es compatible | api-contracts §6 |
| **D-009-E** | Sintaxis asc/desc | `sort=campo&order=desc` · **prefijo `-`** | **`sort=campo` asc, `sort=-campo` desc** | api-contracts §6 declara `sort` como **un** parámetro. El prefijo `-` no necesita un segundo parámetro ni admite un estado inválido ("`order` sin `sort`"). La lista cerrada enumera las cuatro cadenas admitidas, así que no hay gramática que analizar | api-contracts §6 |
| **D-009-F** | Desempate estable | `id` · `created_at` · **`slug`** | **`slug` ASC** | Dos filas pueden compartir `published_at`, y un `LIMIT/OFFSET` sin desempate total puede repetir u omitir filas entre páginas. `slug` es `UNIQUE NOT NULL` en las cuatro tablas: da orden **total**. Frente a `id`, es estable, explicable y ya es la identidad pública. En `/search`, donde `slug` no es único entre tipos, el desempate es `(type, slug)` | data-model §4 · decisión propia |
| **D-009-G** | Semántica de `featured` | Solo `true` significativo · **filtro booleano** | **`true` solo destacados; `false` solo no destacados; ausente sin filtro** | api-contracts §6 describe el caso `true` ("solo contenido destacado") y no define `false`. Un parámetro cuyo `false` no hace nada es una trampa. Se aceptan **únicamente** los literales `true` y `false`: `1`, `yes`, `on` producen `422`, para no depender de coerciones ambiguas | api-contracts §6 · USER_FLOWS A.1 |
| **D-009-H** | `tag` inexistente | `404` · **`200` vacío** | **`200` con `items=[]`** | `tag` es un **filtro de colección**, no un segmento de ruta. api-contracts §5 ya establece que una colección sin resultados devuelve `200` vacío. Además hace indistinguible "la etiqueta no existe" de "la etiqueta no tiene contenido publicado", que es la misma postura de no filtración de §3 | api-contracts §5 |
| **D-009-I** | Visibilidad de `/tags` | Catálogo completo · **solo etiquetas con contenido publicado** | **Solo las asociadas a al menos un contenido `published`** de cualquiera de los cuatro tipos | El propósito del endpoint es la navegación (A.9): ofrecer etiquetas en las que hay algo que ver. Devolver una etiqueta usada solo por borradores presentaría un filtro que da cero resultados **y revelaría que existe contenido no publicado con esa etiqueta** — exactamente el canal de inferencia que hay que cerrar. Una etiqueta huérfana tampoco es "disponible" | USER_FLOWS A.9 · CONTENT_MODEL invariante 2 |
| **D-009-J** | Forma de `/search` | Agrupada por tipo · **plana con discriminador** | **Colección plana; cada elemento lleva `type`** | USER_FLOWS A.8 admite "agrupados **o** etiquetados por tipo" y exige paginación. Una respuesta agrupada no encaja en la envoltura única de api-contracts §5 sin inventar una segunda forma de paginar. Plana conserva **una sola** envoltura en toda la API; agrupar es trivial en el cliente | USER_FLOWS A.8 · api-contracts §5 |
| **D-009-K** | Campos consultados | Todo el Markdown · **`title` + `summary`** más los del libro | **`title`, `summary`; y además `book_title`, `book_author` en reviews** | Criterio: **un resultado debe mostrar dónde coincidió**. El resultado de búsqueda muestra título y resumen, así que una coincidencia en ellos es visible. `content` no se muestra: una coincidencia enterrada en el Markdown produce un resultado que al visitante le parece un error, y es además la columna más grande. `book_title` y `book_author` **sí** se muestran en el listado de reviews (A.4, A.5), así que entran por el mismo criterio, no por excepción | USER_FLOWS A.4, A.5, A.8 |
| **D-009-L** | Mecanismo de búsqueda | `=` · **`ILIKE`** · *full-text* `tsvector` · `pg_trgm` · servicio externo | **`ILIKE` con patrón `%término%`, parámetro ligado y comodines escapados** | `pg_trgm` es una **extensión**, prohibida por T-02. El *full-text* nativo obligaría a elegir configuración de idioma y aplica *stemming*, y no encuentra subcadenas: "doc" no encontraría "docker", que es justo lo que espera quien teclea en un buscador. Con el volumen de un blog personal el escaneo es trivial. Ningún servicio externo entra en el MVP. El término viaja **ligado**, nunca interpolado (A.8) | T-02 · USER_FLOWS A.8 |
| **D-009-M** | Índices adicionales | Crear índice de búsqueda · **ninguno** | **Ninguno. `Task/009` no modifica el esquema físico** | Ningún índice B-tree sirve a un `ILIKE` con comodín inicial; el que serviría exige `pg_trgm` (extensión prohibida) o cambiar de mecanismo a `tsvector`. Crear un índice inútil es peor que no crearlo. Para `featured` sigue vigente lo que ya razonó data-model §8: los listados de destacados son diminutos y van siempre combinados con `status`, que ya tiene índice. **Disparador de revisión** registrado en `data-model.md` §10 | data-model §8 · P-08 |
| **D-009-N** | `/profile` sin perfil | `200` con campos vacíos · `503` · **`404`** | **`404` `resource_not_found`** | Devolver `200` obligaría a inventar una identidad —prohibido: son datos personales que no se versionan—. `503` afirmaría que el servicio no está disponible, que es falso y contradiría `/ready`. El recurso **realmente no existe**, que es literalmente lo que api-contracts §8 asigna al `404`. Es un estado transitorio del *bootstrap*: `Task/022` (semilla local) y `Task/036` (producción) lo hacen desaparecer | api-contracts §8 · data-model §5 |
| **D-009-O** | Representación de `MediaAsset` | Exponer `object_key` · construir URL · omitir el medio · **objeto extensible sin URL** | **Objeto anidado con `alt_text`, `width`, `height`; sin campo de acceso** | La invariante 9 de CONTENT_MODEL prohíbe exponer claves de objeto "sin control", y la forma pública del acceso —URL prefirmada, bucket privado, expiración— es **de `Task/010`**. Concatenar una URL sería inventarla. Lo que sí es público y útil hoy: texto alternativo (A-04) y dimensiones. `Task/010` añadirá el campo de acceso, que es un cambio **compatible** (api-contracts §10.3) | CONTENT_MODEL §3.7 e invariante 9 · STAGE-03 |
| **D-009-P** | Listado frente a detalle | Un DTO único · **dos DTO** | **`…DeListado` y `…Detallado` separados** | El listado no carga `content`: cargar el Markdown completo de 12 filas para mostrar un resumen contradice P-08. SEO y `reading_time_minutes` solo tienen sentido donde hay página propia. `Video` tiene **solo** listado, y ese listado lleva los datos de reproducción precisamente porque no hay detalle donde ponerlos | P-08 · USER_FLOWS A.2 a A.7 |
| **D-009-Q** | Capas por módulo | `presentation → application → infrastructure` · **`presentation → infrastructure`** | **Sin capa `application` en `Task/009`** | software-architecture §3.2 dice que **no** todos los módulos necesitan las cuatro capas y que **crear capas vacías está prohibido**. Un "caso de uso" de solo lectura sería aquí una función que reenvía argumentos: sin orquestación, sin invariante que proteger y sin límite transaccional propio. La regla de negocio real —invariante 19— vive **dentro de la consulta** (`WHERE status = 'published'`), que es donde debe expresarse. `Task/012` introduce escritura, validación de publicación y auditoría: ahí `application` deja de estar vacía | ADR-004 · software-architecture §3.2, §3.5 |
| **D-009-R** | Consulta compartida entre los cuatro tipos | Constructor genérico en `shared` · **una consulta por módulo** | **Una por módulo, con duplicación aceptada** | Un constructor genérico tendría que conocer `status`, `published_at`, `featured` y las tablas puente: metería **reglas de negocio en `shared`**, que las tiene prohibidas, y crearía el "repositorio genérico universal" descartado por ADR-004. Es el mismo criterio que `Task/008` ya aplicó a los modelos (D-P) y a los *mixins*. Lo que sí se comparte es lo genuinamente agnóstico: paginación y resolución de orden | software-architecture §3.4 · data-model D-P |

**Decisiones ajenas que `Task/009` NO toca:** `open-decisions.md` no registra ninguna
decisión cuyo dueño sea `Task/009`. D-02, D-09 y D-15 son de `Task/011`; D-08 es de
`Task/030`. Ninguna se modifica.

---

## 9. Plan de validación

| Criterio | Cómo se comprueba |
| --- | --- |
| 1 a 3, 12 | `tests/contract/test_openapi_publica.py` sobre la especificación generada |
| 4 a 6 | `tests/contract/` (validación) e `tests/integration/` (recorte y rango) |
| 7 a 8 | `tests/integration/test_api_*` con datos sembrados en el harness aislado |
| 9 a 10 | Casos B-01..B-03, C-02..C-04 y H-02..H-03, replicados por tipo |
| 11 | Aserciones explícitas de **ausencia** de campo en cada DTO |
| 13 | Evidencia RED/GREEN por *slice* en el reporte |
| 14 | `git status` en `personal-blog-frontend` |

## 10. Comandos de validación

```bash
ruff check .
ruff format --check .
mypy .
pytest tests/unit -q
pytest tests/contract -q
pytest -m integration -q
pytest -q -W error
pytest --cov -q
pip check
```

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | Una consulta futura olvida `status = 'published'` y filtra borradores | **Alto** | El filtro vive en la consulta, no en el router; caso negativo obligatorio por tipo y por endpoint, incluidos `/search` y `/tags` |
| 2 | Rechazar parámetros desconocidos rompe un cliente que añade parámetros de analítica | Medio | Registrado como coste aceptado en **D-009-C**; el frontend no debe reenviarlos |
| 3 | La derivación de parámetros admitidos depende de la estructura interna de FastAPI | Medio | Prueba J-04: si la derivación deja de funcionar, la suite se pone roja en lugar de rechazarlo todo |
| 4 | `ILIKE` deja de ser suficiente al crecer el contenido | Bajo hoy | Disparador de revisión documentado en `data-model.md` §10, con el camino (`tsvector` más GIN, ambos del núcleo) |
| 5 | N+1 en listados con etiquetas y portada | Medio | Carga explícita (`selectinload`/`joinedload`) y prueba B-14, que compara el número de consultas entre 2 y 10 filas |

## 12. Deuda técnica que `Task/009` deja registrada

| # | Deuda | Dueño |
| --- | --- | --- |
| 1 | Las referencias a medios no llevan campo de acceso | `Task/010` |
| 2 | El mecanismo de búsqueda se revisa si el volumen lo justifica | Revisión futura, con disparador escrito |
| 3 | `reading_time_minutes` se calcula al servir; su presentación es del frontend | `Task/014` |

## 12.1 Resultado de las validaciones

Ejecutadas en el repositorio oficial el **2026-08-27**, después de la remediación TDD,
contra `personal_blog_test` en PostgreSQL real.

| Comando | Resultado |
| --- | --- |
| `ruff check .` | `All checks passed!` |
| `ruff format --check .` | `148 files already formatted` |
| `mypy .` | `Success: no issues found in 146 source files` |
| `pytest tests/unit -q` | `100 passed` |
| `pytest tests/contract -q` | `188 passed` |
| `pytest -m integration -q` | `227 passed, 371 deselected` |
| `pytest -q -W error` | **`597 passed, 1 skipped`**, 0 advertencias |
| `pytest --cov -q` | `app/` al **100 %**, ramas incluidas |
| `pip check` | `No broken requirements found.` |
| `alembic heads` | `0002 (head)` — **sin migración nueva** |

La única omisión es la preexistente: `time.tzset` no existe en Windows.

**Desviación registrada, y remediada antes de aprobar.** En la primera ejecución, los
*slices* de reviews, vídeos, proyectos, perfil, etiquetas y búsqueda tuvieron sus pruebas
escritas **después** de la implementación, por un error de secuencia en el cableado de los
routers. La desviación se detectó **pre-approval**; la tarea **no** se aprobó.

Antes de cualquier *commit*, *push* o pull request, esos **seis *slices* se reconstruyeron
genuinamente test-first** en un laboratorio limpio nacido del mismo SHA base: especificación
previa, **RED observado sobre código inexistente**, GREEN y refactor por *slice*. La
implementación que hoy está en el árbol de trabajo del backend oficial es **la reconstruida**,
y es la candidata a aprobación; la *post-hoc* se conserva solo como *backup* histórico. El
*mutation testing* se mantiene como evidencia **complementaria**, no como sustituto del RED.

**Estado del criterio 29 — «contratos HTTP cubiertos test-first»: CUMPLIDO para la
implementación candidata.** No se afirma que `Task/009` cumpliera TDD a la primera: no lo
hizo. Detalle completo, y la historia original sin borrar, en el
[reporte §I.2, §I.5 y §I.6](../task-reports/TASK-009-report.md).

## 13. Próxima tarea

`Task/010-Almacenamiento-Compatible-S3` — interfaz `ObjectStorage`, `MinIOStorage` y
`S3Storage`. **No se inicia** hasta que `Task/009` esté aprobada y normalizada.

## 14. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-08-27** |
| **Aprobado por** | **El usuario** |
| **Expresión de aprobación** | `approved: Task/009-API-Publica` — recibida literalmente |

La aprobación se otorgó sobre la **implementación remediada test-first** descrita en §12.1,
revalidada en el repositorio oficial. Las decisiones **D-009-A** a **D-009-R** quedan
**Vigentes**.
