# Contratos generales de API

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/002-Definir-MVP-y-Arquitectura` (2026-07-26) |
| **Fecha** | 2026-07-26 · §5, §6 y §11 completadas por `Task/009-API-Publica` (2026-08-26) · §13 añadida por `Task/011-Autenticacion-Administrativa` (2026-09-01) · §14 añadida por `Task/012-API-Administrativa` (2026-09-01) · §15 añadida por `Task/012.1-Exponer-Auditoria-Para-Dashboard` (2026-09-05) |
| **Nivel** | **Convenciones conceptuales.** No es una especificación OpenAPI. |

> **Límite explícito.** Este documento fija **convenciones** que toda la API debe
> respetar. **No** es una especificación OpenAPI completa ni código a implementar. Los
> esquemas concretos de petición y respuesta se definieron al implementar `Task/009`
> (API pública) y `Task/012` (API administrativa), y viven en sus fichas y en la
> especificación OpenAPI que genera el backend, que es su fuente ejecutable.
>
> **Estado tras `Task/009`.** Las decisiones que este documento dejaba abiertas para la
> API **pública** —valores de `page_size`, política de parámetros desconocidos, lista
> cerrada de `sort` y forma de los resultados de búsqueda— están **cerradas** y anotadas
> abajo. Los esquemas campo a campo no se duplican aquí: viven en la ficha
> [`TASK-009`](../tasks/TASK-009-public-api.md) §7.4 y en la especificación OpenAPI que
> genera el backend, que es su fuente ejecutable.

Relacionados: [USER_FLOWS.md](../product/USER_FLOWS.md) ·
[software-architecture.md](software-architecture.md) ·
[security-boundaries.md](security-boundaries.md)

---

## 1. Convenciones generales

| Aspecto | Convención |
| --- | --- |
| Formato | **JSON** como formato principal, en petición y respuesta. |
| Codificación | **UTF-8**. |
| Fechas | **ISO 8601 en UTC** (`2026-07-26T14:30:00Z`). |
| Identificadores internos | **No se exponen innecesariamente**: la API pública usa slugs. |
| Slugs | **Estables y únicos** por tipo de contenido. |
| Paginación | Basada inicialmente en **`page` y `page_size`**. |
| Orden por defecto | **`published_at` descendente**. |
| Filtros | Mediante **query parameters**. |
| Códigos HTTP | **Coherentes** con el resultado real. |
| Correlación | **Correlation/request ID** en cada petición y respuesta. |
| Versionado | Prefijo de versión en la ruta: `/api/v1`. |
| Nombres de campo | `snake_case`. |
| Rutas | `kebab-case` en plural (`/book-reviews`). |

---

## 2. Base y endpoints técnicos

**Base:** `/api/v1`

| Endpoint | Propósito | Autenticación |
| --- | --- | --- |
| `GET /health` | Vivacidad del servicio. Responde sin comprobar dependencias. | No |
| `GET /ready` | Disponibilidad real: base de datos y almacenamiento accesibles. | No |

`/health` responde afirmativamente si el proceso está en pie. `/ready` puede fallar
mientras las dependencias no estén listas. Ninguno expone detalles internos ni versiones
de dependencias.

---

## 3. Recursos públicos (conceptuales)

Solo lectura. **Nunca** devuelven contenido en estado `draft` o `archived`.

| Recurso | Devuelve |
| --- | --- |
| `GET /api/v1/profile` | Perfil del autor y enlaces. |
| `GET /api/v1/posts` | Colección paginada de artículos publicados. |
| `GET /api/v1/posts/{slug}` | Un artículo publicado. |
| `GET /api/v1/book-reviews` | Colección paginada de reviews publicadas. |
| `GET /api/v1/book-reviews/{slug}` | Una review publicada. |
| `GET /api/v1/videos` | Colección paginada de videos publicados. |
| `GET /api/v1/projects` | Colección paginada de proyectos publicados. |
| `GET /api/v1/projects/{slug}` | Un proyecto publicado. |
| `GET /api/v1/tags` | Etiquetas disponibles. |
| `GET /api/v1/search` | Resultados de búsqueda sobre contenido publicado. |

**Regla de no filtración:** un slug inexistente y un slug existente pero no publicado
devuelven **el mismo `404`**. La API no revela la existencia de borradores.

### `GET /sitemap.xml` — cerrado en `Task/016` (2026-09-06)

> **Vigente** desde la aprobación de `Task/016`.

| Aspecto | Valor |
| --- | --- |
| Ruta | **`/sitemap.xml`**, **fuera** del prefijo `/api/v1` |
| `Content-Type` | `application/xml` |
| Autenticación | Ninguna |
| Paginación | **No**. No es una colección de la API: la consume un *crawler*, y el protocolo de sitemaps define su propio límite |

**Por qué fuera del prefijo versionado**, con el mismo criterio que `/health`: el prefijo
versiona el **contrato de datos** que consume el frontend, y el sitemap es un artefacto del
**protocolo web**. No debe mudarse de ruta cuando el contrato pase a `v2`.

Contiene las 7 rutas estáticas del sitio más una entrada por cada contenido `published` de
**artículos, reviews y proyectos**. **No** incluye `/buscar`, `/admin/*`, la 404 ni
`/videos/{slug}`, que no existe. `<lastmod>` sale de `published_at`, normalizado a UTC;
**no** se expone `updated_at`, que no forma parte del contrato público.

Las URL son del **sitio**, no del API: se componen con `BLOG_PUBLIC_SITE_BASE_URL`, una
variable obligatoria y validada al arrancar. Con **D-15** el sitio vive en el dominio raíz
y el API en un subdominio, así que confundirlos produciría un sitemap falso.

**Requisito E-08 por construcción:** el sitemap reutiliza el mismo filtro `status =
'published'` que protege los listados públicos, así que un borrador o un archivado no
pueden aparecer. Fijado por prueba contra PostgreSQL real, y comprobado con una mutación
temporal del filtro que puso esas pruebas en rojo.

---

## 4. Recursos administrativos (conceptuales)

Todos requieren autenticación **excepto `login`**.

| Recurso | Propósito |
| --- | --- |
| `POST /api/v1/admin/auth/login` | Iniciar sesión. Único endpoint administrativo público. **Contrato cerrado en `Task/011`** (§13). |
| `POST /api/v1/admin/auth/logout` | Cerrar sesión e invalidarla en el servidor. **Contrato cerrado en `Task/011`** (§13). |
| `GET /api/v1/admin/auth/me` | Consultar la sesión actual. **Contrato cerrado en `Task/011`** (§13). |
| `/api/v1/admin/profile` | Consultar y editar el perfil. |
| `/api/v1/admin/posts` | Gestión completa de artículos. |
| `/api/v1/admin/book-reviews` | Gestión completa de reviews. |
| `/api/v1/admin/videos` | Gestión completa de videos. |
| `/api/v1/admin/projects` | Gestión completa de proyectos. |
| `/api/v1/admin/tags` | Gestión de etiquetas. |
| `/api/v1/admin/media` | Carga, listado y borrado controlado de imágenes. |
| `GET /api/v1/admin/audit-events` | Consultar el historial de acciones administrativas. **Solo lectura.** Contrato cerrado en `Task/012.1` (§15). |

Los recursos administrativos operan sobre **identificadores internos**, no sobre slugs:
el slug puede cambiar mientras se edita un borrador.

La forma exacta de las transiciones de estado (publicar, despublicar, archivar) quedó
**cerrada en `Task/012`**: son **subrecursos dedicados** (`POST /{id}/publish`,
`/unpublish`, `/archive`), no una actualización del campo `status`. Detalle y motivo en
§14.

---

## 5. Paginación

Parámetros de entrada:

| Parámetro | Significado | Notas |
| --- | --- | --- |
| `page` | Página solicitada, comenzando en 1. | Por defecto 1. |
| `page_size` | Elementos por página. | Por defecto **12**; máximo **50**. Cerrados en `Task/009`. |

Envoltura conceptual de colección paginada:

```json
{
  "items": [],
  "page": 1,
  "page_size": 12,
  "total": 0,
  "pages": 0
}
```

| Campo | Significado |
| --- | --- |
| `items` | Elementos de la página actual. |
| `page` | Página devuelta. |
| `page_size` | Tamaño de página aplicado (puede diferir del solicitado si excede el máximo). |
| `total` | Total de elementos que cumplen el filtro. |
| `pages` | Número total de páginas. |

Reglas:

- **Toda colección está paginada.** No existe ningún endpoint que devuelva "todo".
- Una página fuera de rango devuelve `items` vacío con `200`, no un error.
- `page_size` por encima del máximo se recorta al máximo; no es un error.
- Los parámetros no válidos (`page=0`, `page=abc`) devuelven `422`.

**Valores cerrados en `Task/009`** (2026-08-26):

| Valor | Elegido | Por qué |
| --- | --- | --- |
| `page_size` por defecto | **12** | Es el que usan todos los ejemplos canónicos: USER_FLOWS.md A.2, A.4, A.6 y A.8, y la envoltura de ejemplo de esta misma sección. |
| `page_size` máximo | **50** | Ninguna fuente lo fijaba. Da holgura a un cliente que quiera menos viajes y acota la consulta (requisitos P-02 y P-08). Por encima **se recorta**; nunca es error. |

> La paginación por cursor queda fuera del MVP. Si el volumen lo justifica, se
> reconsidera con un ADR.

---

## 6. Filtros y orden

| Parámetro | Aplica a | Significado |
| --- | --- | --- |
| `tag` | Listados de contenido | Filtra por slug de etiqueta. |
| `featured` | Listados de contenido | `true`: solo destacados. `false`: solo no destacados. Ausente: sin filtro. |
| `q` | `/search` | Término de búsqueda. |
| `status` | **Solo administrativo** | Filtra por `draft`, `published`, `archived`. |
| `sort` | Listados | Campo de ordenación alternativo. Opcional. |

Reglas:

- **Orden por defecto: `published_at` descendente.**
- Los campos de ordenación permitidos son una **lista cerrada**; cualquier otro valor
  devuelve `422`.
- `status` **no existe** en la API pública: los listados públicos son siempre
  `published`.
- Los parámetros de consulta desconocidos **se rechazan** con `422`. Decisión cerrada en
  `Task/009`; detalle abajo.

### Decisiones cerradas en `Task/009` (2026-08-26)

| Aspecto | Decisión | Por qué |
| --- | --- | --- |
| **Parámetros desconocidos** | **Se rechazan** con `422` y el envelope común | El proyecto ya es estricto de forma consistente ante claves desconocidas (`extra="forbid"` en la configuración). Ignorar convierte una errata del cliente —`?tagg=docker`— en un listado silenciosamente **sin filtrar**. Rechazar hace además que OpenAPI **sea** el contrato en lugar de describirlo, y cierra `status` por construcción: `?status=draft` no se ignora, se rechaza. **Coste aceptado:** un parámetro de analítica añadido a la URL de la API produciría `422`; el frontend no debe reenviarlos |
| **Campos ordenables** | Lista cerrada: **`published_at` y `title`** | Uniforme en los cuatro listados. `title` es el único orden alternativo con sentido para un visitante; `rating` no lo pide ningún flujo y crearía una divergencia por tipo. Añadir un campo después es compatible |
| **Dirección** | Prefijo `-`: `sort=title` ascendente, `sort=-title` descendente | `sort` es **un** parámetro. Un segundo parámetro `order` admitiría el estado inválido «dirección sin campo» |
| **Desempate** | **`slug` ascendente** | `published_at` puede repetirse, y un `LIMIT`/`OFFSET` sobre un orden no total puede repetir u omitir filas entre páginas. `slug` es `UNIQUE NOT NULL` en las cuatro tablas: da orden total, es estable y es la identidad pública |
| **`featured`** | Filtro booleano completo; solo los literales `true` y `false` | Un parámetro cuyo `false` no hiciera nada sería una trampa. Se rechazan `1`, `yes` y `on` para no heredar coerciones ambiguas |
| **`tag` inexistente** | `200` con `items` vacío | Es un **filtro de colección**, no un segmento de ruta. Hace además indistinguible «la etiqueta no existe» de «no tiene contenido publicado», que es la misma postura de no filtración de §3 |
| **`GET /tags`** | Solo etiquetas con **al menos un contenido publicado** | El endpoint existe para navegar. Devolver una etiqueta usada solo por borradores ofrecería un filtro vacío **y revelaría que existe contenido no publicado con ella** |
| **Forma de `/search`** | Colección **plana**; cada elemento declara su `type` | USER_FLOWS.md A.8 admite agrupados **o** etiquetados por tipo. Agrupar no encaja en la envoltura única de §5 sin inventar una segunda forma de paginar. Plana, toda la API conserva una sola envoltura |
| **Campos buscados** | `title` y `summary`; además `book_title` y `book_author` en reviews | Criterio: un resultado debe **mostrar dónde coincidió**. `content` queda fuera: una coincidencia enterrada en el Markdown produce un resultado en el que el visitante no ve el término por ninguna parte |
| **Mecanismo de búsqueda** | `ILIKE`, con el término ligado y sus comodines escapados | `pg_trgm` es una extensión (prohibida por T-02); el *full-text* nativo no encuentra subcadenas —«doc» no encontraría «docker»—. Ningún servicio externo entra en el MVP |
| **`GET /profile` sin perfil** | `404` `resource_not_found` | El recurso realmente no existe todavía. `200` con campos vacíos obligaría a inventar una identidad; `503` afirmaría que el servicio no funciona. Desaparece con `Task/022` (semilla local) y `Task/036` (producción) |

---

## 7. Modelo común de errores

Toda respuesta de error usa esta forma conceptual:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {},
    "request_id": "string"
  }
}
```

| Campo | Significado |
| --- | --- |
| `code` | Código estable y legible por máquina (`resource_not_found`, `validation_error`). |
| `message` | Mensaje breve para humanos. **Nunca** incluye trazas ni detalles internos. |
| `details` | Contexto estructurado adicional; en validación, los campos afectados. |
| `request_id` | Correlation ID, para localizar la petición en los logs. |

Reglas:

- **Nunca** se devuelven trazas de pila, consultas SQL, rutas de archivo ni nombres de
  clase.
- `code` es estable: el frontend puede reaccionar a él. `message` puede cambiar de
  redacción.
- Los errores de autenticación son **genéricos**: no revelan si el usuario existe.
- Todo error lleva `request_id`, y ese mismo identificador aparece en los logs.

---

## 8. Códigos HTTP

| Código | Cuándo |
| --- | --- |
| `200 OK` | Lectura o actualización correcta. |
| `201 Created` | Recurso creado. |
| `204 No Content` | Eliminación correcta o respuesta sin cuerpo. |
| `400 Bad Request` | Petición mal formada. |
| `401 Unauthorized` | Falta autenticación o es inválida. |
| `403 Forbidden` | Autenticado pero sin permiso para la operación. |
| `404 Not Found` | El recurso no existe **o no es visible** para quien pregunta. |
| `409 Conflict` | Conflicto de estado (por ejemplo, slug duplicado). |
| `413 Payload Too Large` | Archivo por encima del tamaño permitido. |
| `415 Unsupported Media Type` | Tipo MIME no permitido. |
| `422 Unprocessable Entity` | Validación fallida sobre una petición bien formada. |
| `429 Too Many Requests` | Límite de peticiones superado. |
| `500 Internal Server Error` | Fallo no controlado. Sin detalles internos. |
| `503 Service Unavailable` | Dependencia no disponible (`/ready` en fallo). |

---

## 9. Correlation ID

- Cada petición tiene un `request_id`: se acepta el que envíe el cliente en una cabecera
  acordada o se genera uno.
- Se devuelve en la respuesta y se incluye en **todos** los logs de esa petición.
- Aparece en el cuerpo de error como `error.request_id`.
- Se registra en los eventos de auditoría de las operaciones administrativas.

Objetivo: que un problema reportado por el usuario pueda rastrearse extremo a extremo con
un único identificador.

---

## 10. Reglas de compatibilidad

1. La versión vive en la ruta (`/api/v1`).
2. Dentro de una versión, **no** se elimina ni se renombra un campo existente.
3. Añadir campos opcionales **no** es un cambio incompatible.
4. Un cambio incompatible exige `/api/v2` y un ADR.
5. Los valores de `status` (`draft`, `published`, `archived`) son un contrato cerrado.
6. Los `code` de error son estables una vez publicados.

---

## 11. Qué queda para las tareas de implementación

| Elemento | Tarea | Estado |
| --- | --- | --- |
| Esquemas concretos de respuesta **pública** | `Task/009` | **Cerrado** (2026-08-26) — ficha `TASK-009` §7.4 y OpenAPI generada |
| Esquemas de petición y respuesta **administrativas** | `Task/012` | **Cerrado** (2026-09-01) — §14 y ficha `TASK-012` §7.0 |
| Valores por defecto y máximos de `page_size` | `Task/009` | **Cerrado** (2026-08-26) — 12 y 50 |
| Política de parámetros desconocidos | `Task/009` | **Cerrado** (2026-08-26) — se rechazan |
| Lista cerrada de `sort` y su dirección | `Task/009` | **Cerrado** (2026-08-26) |
| Forma de los resultados de `/search` | `Task/009` | **Cerrado** (2026-08-26) — colección plana con `type` |
| Forma exacta de las transiciones de estado | `Task/012` | **Cerrado** (2026-09-01) — **subrecursos dedicados**; ver §14.2 |
| Cabecera concreta del correlation ID | `Task/017` | Abierto |
| Mecanismo de autenticación y forma de la sesión | `Task/011` | **Cerrado** (2026-09-01) — sesión opaca en cookie `HttpOnly`; ver §13 |
| Límites de tamaño y tipos MIME permitidos | `Task/010`, `Task/018` | **Base cerrada** (2026-08-28) — 5 MiB y JPEG/PNG/WebP; `Task/018` endurece |
| Configuración concreta de rate limiting | `Task/011`, `Task/018` | **Cerrada para `login`** (2026-09-01) — 10 intentos / 300 s por IP, con `Retry-After`; `Task/018` endurece |
| **Representación pública de una referencia a `MediaAsset`** | `Task/010` | **Cerrado** (2026-08-28) — `alt_text`, `width`, `height` y **`access_url`**; ver §12 |
| Especificación OpenAPI generada | `Task/009`, `Task/012` y `Task/012.1` | **Completa para el MVP** — 11 rutas públicas, 3 de acceso y **24** administrativas: **38 patrones de ruta** en total, de los cuales **27** son administrativos o de acceso y suman **39 operaciones** método+ruta |


---

## 12. Referencia pública a un medio — cerrada en `Task/010` (2026-08-28)

`Task/009` dejó `MedioPublico` **sin campo de acceso** (**D-009-O**) porque la
forma de ese acceso —bucket privado, URL prefirmada, expiración— correspondía a
`Task/010`. Queda así:

```json
{
  "alt_text": "Texto alternativo",
  "width": 1200,
  "height": 800,
  "access_url": "https://<endpoint>/<bucket>/<clave>?X-Amz-Signature=...",
  "thumbnail_access_url": "https://<endpoint>/<bucket>/<clave-derivada>?X-Amz-Signature=..."
}
```

| Campo | Significado |
| --- | --- |
| `alt_text` | Texto alternativo (requisito A-04). |
| `width`, `height` | Dimensiones **del original**, para reservar el espacio antes de cargar. |
| `access_url` | **Enlace temporal de lectura.** Se genera al servir la respuesta y **caduca**. No es un identificador estable y no debe almacenarse. |
| `thumbnail_access_url` | **Enlace temporal de la miniatura**, para listados (requisito P-04). Añadido en `Task/016`. **Misma naturaleza temporal** que `access_url`. |

> **`thumbnail_access_url` NO es una URL estable de medios.** Caduca igual que
> `access_url`. Que exista una URL estable sigue siendo la pregunta abierta de **D-08**,
> propiedad de `Task/030`, y este campo no la responde: en particular, **no vale como
> `og:image`**.
>
> **No se exponen las dimensiones de la miniatura:** no se persisten —su clave se *deriva*
> de la del original, decisión D-010-I— y `width`/`height` sirven igual para reservar el
> espacio, porque la miniatura conserva la proporción (D-010-H).

Es un cambio **compatible**: añade un campo opcional y no retira ni renombra
ninguno (§10, regla 3).

### `object_key` y la URL prefirmada — precisión de la invariante 9

Una URL prefirmada **es** `<endpoint>/<bucket>/<object_key>?X-Amz-...`: la clave
es la ruta del recurso que se firma, y **no existe ninguna variante del
mecanismo que la omita**. El mecanismo tampoco es opcional:
[CONTENT_MODEL.md](../product/CONTENT_MODEL.md) §3.7 y
[security-boundaries.md](security-boundaries.md) lo imponen —el navegador
alcanza el almacenamiento *«únicamente mediante URL prefirmada emitida por el
backend»*—.

La invariante 9 de CONTENT_MODEL.md prohíbe exponer claves de objeto **«sin
control»**. La garantía exacta, y la única que puede afirmarse, es:

1. **Ningún campo del contrato transporta `object_key`** como dato. Eso es lo
   que la convertiría en parte del contrato `v1`, del que ya no podría
   retirarse (§10, regla 2).
2. Fuera del enlace firmado, la clave **no aparece** en ninguna respuesta.
3. Conocerla **no da acceso**: el bucket es privado, hace falta la firma, y las
   claves son no predecibles, así que ver una no permite adivinar otra.

Está fijado por prueba en `tests/integration/test_acceso_publico_a_medios.py`,
que inspecciona el JSON entero tras retirar los enlaces firmados.

### Qué sigue abierto — **D-08**, `Task/030`

| Pregunta | Propietario |
| --- | --- |
| Si existe además una URL **estable** para los medios del contenido publicado, y por qué vía | `Task/030` |
| **Semántica de caché** de esas URLs y su compatibilidad con un CDN | `Task/030` |
| **Valor productivo** del TTL (aquí es configuración: `BLOG_STORAGE_ACCESS_TTL_SECONDS`, 900 s por defecto) | `Task/030` |
| Política del bucket, CORS y *lifecycle* | `Task/030` |
| Qué URL usa `og:image` | **Respondido por `Task/016`** (2026-09-06, **Vigente**): una **imagen estática del propio sitio**, versionada en `public/`. Es la única opción estable y no expirable que no decide nada de lo que D-08 reserva. El `og:image` **personalizado por contenido** sigue bloqueado por D-08 |

Por eso **no** se expone `access_expires_at`: declarar cuándo caduca el enlace es
describir su semántica de caché, que es literalmente una de las preguntas de
D-08. Añadirlo después sería compatible; retirarlo, no.

---

## 13. Autenticación administrativa — cerrada en `Task/011` (2026-09-01)

### 13.1 Los tres endpoints

| Endpoint | Método | Éxito | Autenticación | Caché |
| --- | --- | --- | --- | --- |
| `/api/v1/admin/auth/login` | `POST` | `200` | **Ninguna** | `no-store` |
| `/api/v1/admin/auth/logout` | `POST` | `204` | Cookie de sesión | `no-store` |
| `/api/v1/admin/auth/me` | `GET` | `200` | Cookie de sesión | `no-store` |

**No existen** `register`, `forgot-password`, `reset-password` ni `change-password`:
ninguna fuente canónica los asigna, y no hay registro público en el producto.

### 13.2 Petición y respuesta

```json
// POST /admin/auth/login
{ "email": "...", "password": "..." }
```

```json
// 200 — login y me. Son EXACTAMENTE estos tres campos.
{ "id": "uuid", "email": "...", "display_name": "..." }
```

**La credencial de sesión no aparece en ningún cuerpo.** Viaja **solo** en la cookie
`HttpOnly`, que es la razón entera de haberla elegido: si estuviera también en el JSON,
JavaScript podría leerla. Tampoco salen `password_hash`, `failed_login_attempts` ni
`locked_until`: el estado defensivo no es asunto del cliente.

`logout` responde `204` **sin cuerpo**.

### 13.3 Cookie de sesión

| Atributo | Valor |
| --- | --- |
| Nombre | `blog_admin_session` |
| `HttpOnly` | Siempre |
| `Secure` | Sí, y **obligatorio en producción** — el proceso no arranca sin él |
| `SameSite` | `Lax` |
| `Path` | El prefijo administrativo (`/api/v1/admin`) |
| `Domain` | **Ausente** → *host-only* |
| `Max-Age` | La duración de la sesión (12 h por defecto) |

### 13.4 Códigos de error

| Código | `code` | Cuándo |
| --- | --- | --- |
| `401` | `invalid_credentials` | Correo inexistente, contraseña incorrecta **o cuenta bloqueada** |
| `401` | `unauthenticated` | Sesión ausente, desconocida, caducada o revocada |
| `403` | `forbidden` | `Origin` no permitido en un método que cambia estado |
| `422` | `validation_error` | Cuerpo inválido, con la envoltura de §7 |
| `429` | `too_many_requests` | Límite de tasa superado. **Lleva `Retry-After`** |

**Los tres casos de `invalid_credentials` son indistinguibles**: mismo estado, mismo
`code` y mismo `message`. Que la cuenta bloqueada no se distinga **es deliberado**: si lo
hiciera, bastaría con enviar el umbral de intentos a un correo para saber si existe.

**Los cuatro casos de `unauthenticated` también.** Cuál ocurrió es estado interno del
servidor, y al cliente le sirve para lo mismo en los cuatro: volver a iniciar sesión.

### 13.5 CORS y `Origin`

La **topología lógica** (**D-15**) sitúa el sitio y el panel en el dominio raíz y el API
en un subdominio: **same-site**, **cross-origin**. La lista de orígenes del panel es
**explícita** y `*` está prohibido junto a credenciales: la configuración **no arranca si
se declara `*` como origen permitido**. Declarar orígenes concretos es el uso previsto.

`Task/011` implementa la **validación de `Origin`** en los métodos que cambian estado
bajo `/admin`; el **middleware CORS efectivo** y las cabeceras de seguridad siguen siendo
de `Task/018`, y el dominio real, de `Task/035` (**D-07**).

### 13.6 Qué sigue abierto

| Pregunta | Propietario |
| --- | --- |
| ~~Esquemas de petición y respuesta del **CRUD administrativo**~~ | **Cerrado** por `Task/012` (§14) |
| Cabecera concreta del correlation ID y su propagación completa | `Task/017` |
| CORS efectivo y cabeceras de seguridad | `Task/018` |
| *Throttling* del borde | `Task/033` |
| Dominio real, DNS y certificados (**D-07**) | `Task/035` |

---

## 14. API administrativa — cerrada en `Task/012` (2026-09-01)

### 14.1 Los 24 patrones de ruta administrativos

Todas bajo `/api/v1/admin`, todas con **sesión obligatoria**. `login` sigue siendo el
único endpoint administrativo público (§13, security-boundaries.md §11.4).

> **Patrón de ruta frente a operación.** Un **patrón de ruta** es un *path* del contrato
> (`/admin/posts/{post_id}`); una **operación** es una combinación **método + patrón**
> (`GET /admin/posts/{post_id}`). Un patrón puede soportar varias operaciones, así que las
> dos cifras no coinciden y no son sinónimos. `Task/012` cerró **23 patrones / 35
> operaciones**; con los 3 patrones y 3 operaciones de autenticación (§13) y el patrón de
> solo lectura que añade `Task/012.1` (§15), el total consumible por el panel es de
> **27 patrones de ruta y 39 operaciones HTTP**.

| Recurso | Operaciones |
| --- | --- |
| `/admin/profile` | `GET`, `PUT` |
| `/admin/posts` | `GET`, `POST` · `/{post_id}`: `GET`, `PUT` · `/{post_id}/{publish,unpublish,archive}`: `POST` |
| `/admin/book-reviews` | Igual que artículos, **incluido `unpublish`** |
| `/admin/videos` | Igual, **sin `unpublish`** |
| `/admin/projects` | Igual, **sin `unpublish`** |
| `/admin/tags` | `GET`, `POST` · `/{tag_id}`: `PUT`, `DELETE` |
| `/admin/media` | `GET`, `POST` (multipart) · `/{media_id}`: `DELETE` (audita **antes** de borrar; ver §14.10) |
| `/admin/audit-events` | **`GET` y solo `GET`** — añadido por `Task/012.1`; ver §15 |

**No existe `DELETE` de contenido.** MVP_SCOPE.md §3.1 enumera las capacidades sobre un
contenido —crear, editar, previsualizar, publicar, despublicar, archivar— y **eliminar no
está**; la invariante 3 de CONTENT_MODEL.md dice además que lo archivado *se conserva*.
El retiro es `archive`, y no se introduce ningún `deleted_at`. `DELETE` existe solo donde
una fuente lo concede: etiquetas (B.11) y medios (B.5).

### 14.2 Transiciones de estado — **subrecursos dedicados**

Cierra la pregunta que §4 y USER_FLOWS.md B.7 dejaban abierta.

```
POST /api/v1/admin/{recurso}/{id}/publish
POST /api/v1/admin/{recurso}/{id}/unpublish     solo artículos y reviews
POST /api/v1/admin/{recurso}/{id}/archive
```

Por qué, y no un campo `status` dentro del `PUT`:

1. Una transición tiene **precondición**, validación propia —los campos mínimos—, error
   propio (`409`) y acción de auditoría propia. Nada de eso encaja en un campo.
2. Mezclarlas con la edición contradiría B.3: *«editar un contenido `published`… no lo
   despublica implícitamente»*.
3. `Video` y `Project` **no** admiten `published → draft`. `Task/008` expresó esa
   diferencia por **ausencia del método** en el dominio; con subrecursos la ruta
   sencillamente no existe, y OpenAPI tampoco la anuncia.

**Consecuencia:** `status` y `published_at` **no son escribibles**. Todo contenido nace
`draft` (B.2), y enviar cualquiera de los dos produce `422`.

**Repetir una transición es `409`, no una operación idempotente.** No lo decide esta
tarea: el dominio aprobado en `Task/008` ya lanza al publicar algo no-`draft` o archivar
algo ya archivado.

### 14.3 Identidad, referencias y campos

| Aspecto | Contrato |
| --- | --- |
| Identidad en la ruta | **`id` (UUID)**, nunca el slug (§4) |
| Etiquetas | `tag_ids: [UUID]`; reemplazo **completo** en cada escritura |
| Portada / miniatura | `cover_id` (`thumbnail_id` en vídeo), `UUID` o `null` |
| Referencia desconocida | `422` `unknown_reference`, con `details.campo` y `details.valores` |
| Verbo de edición | **`PUT`**: representación completa. Omitir un campo opcional lo deja nulo |
| Enlaces sociales del perfil | Array ordenado de `{label, url}`; el orden de presentación es **el índice**, no un campo |

### 14.4 Slug

- **Opcional** en la petición: si falta, se **deriva del título** (B.2).
- Formato: minúsculas ASCII, dígitos y guiones simples, sin guion inicial ni final,
  1–160 caracteres. Un slug explícito mal formado se **rechaza** (`422 invalid_slug`); no
  se corrige en silencio.
- Un título del que no sale ningún carácter útil produce `422`: no se inventa la
  identidad pública de un contenido.
- **Mutable mientras `published_at` sea nulo**; después, `409 slug_is_immutable`. Es la
  lectura conjunta de §4 —*«puede cambiar mientras se edita un borrador»*— y de la
  invariante 4 de CONTENT_MODEL.md. La frontera es **haber sido público alguna vez**: un
  borrador despublicado ya tuvo URL indexada.
- Duplicado: `409 slug_already_exists`. La unicidad es **por tipo**.
- El slug de una **etiqueta** es inmutable desde su creación: aparece en las URL de filtro
  que un visitante puede compartir (A.9).

### 14.5 Validación de publicación

`409 cannot_publish_incomplete_draft`, con los campos que faltan en `details.campos` —
todos a la vez, no de uno en uno. Es `409` y no `422` porque la petición está bien formada
y vacía: lo que impide la operación es el **estado del recurso**.

| Tipo | Exige al publicar |
| --- | --- |
| Los cuatro | `title`, `slug`, y una descripción SEO **resoluble** (`seo_description` **o** `summary`) |
| `Post`, `BookReview`, `Project` | `content` no vacío |
| `BookReview` | además `book_title`, `book_author` y `rating` |
| `Video` | `video_url` y `provider` — su equivalente del *contenido*; **no** tiene Markdown |

*«SEO si corresponde»* (B.7) **no** significa exigir los campos SEO: contradiría los
*fallbacks* de CONTENT_MODEL.md §2. Significa que la descripción SEO se pueda resolver.

**Texto alternativo de la imagen.** Si el contenido referencia una portada o una
miniatura, esa imagen debe tener `alt_text` no vacío: `409` con `cover_alt_text` o
`thumbnail_alt_text` en `details.campos`. Es el requisito **A-04**, exigido **donde se
usa** la imagen, que `data-model.md` §4.1 y la decisión **D-010-N** de `Task/010`
asignaron a `Task/012` y `Task/014`. Un `alt` en blanco cuenta como ausente.

**El perfil lo exige al editar, no al publicar**, y no es una excepción: no tiene
`status` —*«siempre existe y siempre está visible»*, CONTENT_MODEL.md §2—, así que
asignar la foto **es** usarla. `PUT /admin/profile` con una imagen sin `alt_text`
responde `422 media_without_alt_text`.

**Cargar sin `alt_text` sigue permitido** (decisión **D-010-N**, de `Task/010`): se
escribe **al usar** la imagen, no al cargarla — y eso es literal, no una figura: ver
§14.11.

`published_at` se fija en la **primera** publicación, se conserva al despublicar y al
archivar, y **no se reescribe** al volver a publicar (data-model.md §7).

### 14.6 Listados administrativos

| Aspecto | Contrato |
| --- | --- |
| Envoltura | **La misma** de §5: `items`, `page`, `page_size`, `total`, `pages` |
| Estados | Los **tres**. Es lo contrario del listado público |
| Filtro | **Solo `status`**, el único que §6 declara administrativo |
| Orden | `updated_at` descendente, desempate por `slug` ascendente |
| Etiquetas | El listado administrativo incluye las que **no** tienen contenido publicado |
| Medios | `created_at` descendente, desempate por `object_key` |

El orden público no sirve aquí: un borrador **no tiene** `published_at`. MVP_SCOPE.md §3.3
describe el panel por *«últimos elementos modificados»*.

### 14.7 Respuestas administrativas

Añaden sobre el contrato público, y cada adición se justifica: `id` —el panel opera sobre
identificadores internos—, `status`, `created_at` y `updated_at` —MVP_SCOPE.md §3.1 pide
las fechas de gestión—, y un `MedioAdministrativo` con `id`, `original_filename`,
`mime_type`, `size_bytes` y `checksum`, que es lo que permite reconocer y elegir una
imagen de la biblioteca.

**No exponen** `object_key`, `is_singleton`, ninguna clave foránea (`cover_id`,
`photo_id`, `thumbnail_id`), `password_hash`, `token_hash` ni el estado defensivo de la
cuenta. La invariante 9 de CONTENT_MODEL.md no hace excepción para el administrador.

### 14.8 Errores administrativos

| Código | `code` | Cuándo |
| --- | --- | --- |
| `401` | `unauthenticated` | Sin sesión válida |
| `403` | `forbidden` | `Origin` no permitido en un método que cambia estado (§13.5) |
| `404` | `resource_not_found` | El recurso de la ruta no existe |
| `409` | `slug_already_exists` | Otro contenido del mismo tipo usa ese slug |
| `409` | `slug_is_immutable` | El contenido ya se publicó alguna vez |
| `409` | `cannot_publish_incomplete_draft` | Faltan campos mínimos; van en `details.campos` |
| `409` | `invalid_{post,book_review,video,project}_state` | Transición no válida para el estado actual |
| `409` | `media_in_use` | La imagen está referenciada; los usos van en `details.usos` |
| `409` | `alt_text_conflict` | Se propuso un texto alternativo distinto del que la imagen ya tiene. **No se sobrescribe** |
| `413` / `415` | `payload_too_large` / `unsupported_image_type` | Límites de carga (`Task/010`) |
| `422` | `media_without_alt_text` | El perfil referencia una imagen sin texto alternativo, y siempre es visible |
| `422` | `invalid_slug`, `invalid_image`, `invalid_rating`, `unknown_reference`, `validation_error` | Contenido de la petición |

### 14.9 Qué sigue abierto

| Pregunta | Propietario |
| --- | --- |
| ~~Lista cerrada de proveedores de vídeo permitidos~~ | **Cerrada en `Task/014`** (2026-09-05, **Vigente** — aprobada por el usuario): **`youtube`** y **`vimeo`**. El sitio público solo incrusta (*embed*) esos dos proveedores, con `embed_reference` validada por patrón —`^[A-Za-z0-9_-]{11}$` para YouTube y `^[0-9]{6,12}$` para Vimeo— y el `iframe` se crea únicamente por acción del visitante. Cualquier otro proveedor o una referencia malformada es *fail-closed*: solo se ofrece el enlace externo seguro a `video_url`. **El backend no cambia**: sigue exigiendo presencia de `provider`, no pertenencia (§14.5); restringirlo allí y ofrecer el selector en el panel queda como deuda registrada en la ficha de `Task/014` |
| **Corregir a propósito** un `alt_text` ya escrito y compartido por varios contenidos. Fijarlo por primera vez **ya funciona** (§14.11) y **D-012-Z** —rechazar la sobrescritura— está **aceptada para el MVP**: relajarla sería una mejora deliberada, no una corrección | **mejora futura**, sin propietario |
| Cabecera concreta del correlation ID | `Task/017` |
| CORS efectivo y cabeceras de seguridad | `Task/018` |
| URL estable de medios y CDN (**D-08**) | `Task/030` |

### 14.10 Auditoría y almacenamiento: por qué el borrado de un medio audita primero

Es la única operación administrativa que toca **dos sistemas sin transacción común**, y
el orden deja de ser indiferente.

`EliminarMedio` (`Task/010`) borra la fila y **después** los objetos, y eligió ese orden a
propósito (**D-010-P**): de los dos estados a medias posibles, *objetos sin fila* es basura
recuperable y *fila sin objetos* es **una imagen rota en el blog publicado**.

Pero ese borrado de fila queda en un `flush`, no confirmado. Con el orden *borrar y después
auditar*, un fallo del historial haría que la transacción de la petición **devolviera la
fila** mientras los objetos de MinIO ya no estarían: exactamente el estado que aquel orden
existía para evitar, reintroducido por la composición.

Por eso `Task/012` **audita antes de borrar**. Un fallo del historial ocurre entonces antes
de tocar nada; y si lo que falla es el borrado, la transacción se lleva también el evento,
de modo que no queda rastro de algo que no ocurrió. Es el mismo orden, y por la misma
razón, que usa el borrado de una etiqueta.

**La carga no necesita este cuidado.** Allí la fila es el último paso, así que un fallo
posterior de la auditoría revierte la fila y deja, como mucho, objetos huérfanos — el coste
que **D-010-P** acepta por escrito. Está comprobado con inyección de fallo contra
PostgreSQL y MinIO reales.

### 14.11 `alt_text` se escribe **al usar** la imagen

`data-model.md` §4.1 y la decisión **D-010-N** de `Task/010` dicen que `alt_text` *«se
escribe al **usar** la imagen, no al cargarla»*, y que *«exigirlo donde se usa es de
`Task/012` y `Task/014`»*. **Comprobar que existe no es escribirlo**: si el único momento
posible de escritura fuera la carga, esa frase sería falsa y el administrador tendría que
anticipar el texto sin saber todavía en qué contenido va a aparecer la imagen — que es
justo lo que `Task/010` rechazó.

**No se añade ninguna operación a `/admin/media`.** El recurso conserva sus tres
operaciones. Lo que gana un campo es el cuerpo de quien **usa** la imagen:

| Recurso | Campo | Acompaña a |
| --- | --- | --- |
| `/admin/posts`, `/admin/book-reviews`, `/admin/projects` | `cover_alt_text` | `cover_id` |
| `/admin/videos` | `thumbnail_alt_text` | `thumbnail_id` |
| `/admin/profile` | `photo_alt_text` | `photo_id` |

### Reglas

| Estado de la imagen | Cuerpo | Resultado |
| --- | --- | --- |
| sin `alt_text` | con texto | **Se escribe** en `media_assets`, en la misma transacción que la referencia |
| sin `alt_text` | sin texto | Un borrador **sí** puede quedarse así; publicarlo, no (§14.5) |
| con `alt_text` | sin texto | **Se reutiliza** el que hay: el texto es del asset |
| con `alt_text` | el **mismo** | Aceptado, sin escritura. Un panel que devuelve lo que mostró no está pidiendo un cambio |
| con `alt_text` | uno **distinto** | **`409 alt_text_conflict`.** No se sobrescribe |
| sin imagen | con texto | `422`: un texto alternativo sin imagen no describe nada, y aceptarlo en silencio haría creer al panel que guardó algo |

**Por qué un texto distinto se rechaza (decisión D-012-Z, aceptada para el MVP).**
`alt_text` vive en `media_assets`, no en la asociación: cambiarlo cambiaría también el
texto que ya usa otro contenido. Ninguna fuente vigente define qué debe ocurrir; lo que sí
existe es el riesgo, descrito por **D-010-J** para el caso análogo de la deduplicación —
*«reutilizar en silencio haría que borrar un medio afectara a contenidos que nunca lo
subieron»*—.

Rechazar **también es una decisión de comportamiento**, no la ausencia de una. Ante la
ausencia de una semántica canónica previa, `Task/012` adopta para el MVP la política
conservadora de rechazar una sobrescritura diferente. La revisión externa acepta
**D-012-Z**. La política es explícita, reversible y evita modificar en silencio un
`MediaAsset` que puede estar siendo utilizado por otro contenido.

### La decisión es atómica (D-012-AA)

*Set-on-first-use* es una **lectura-decisión-escritura**, así que sin exclusión la regla
anterior sería falsa en cuanto dos administradores usaran la misma imagen a la vez: ambos
leerían `NULL`, ambos se creerían el primero y el segundo `UPDATE` pisaría al primero. Se
comprobó con dos transacciones reales contra PostgreSQL: las dos terminaban en éxito.

La decisión *set-on-first-use* **se serializa sobre la fila `MediaAsset`**: la lectura que
decide es un `SELECT … FOR UPDATE`, por lo que dos primeros usos concurrentes **no pueden
fijar textos distintos**. En `READ COMMITTED` el segundo espera al cerrojo y relee la
última versión confirmada, así que ve el texto del ganador y esta misma tabla decide:
`409` si es distinto, aceptación sin escritura si es el mismo. El cerrojo lo da el motor,
de modo que la garantía sobrevive a varios *workers* y varias instancias.

**Ninguna lectura pública se bloquea.** El `GET` público, el listado de la biblioteca, la
`access_url` y la validación de publicación siguen leyendo sin cerrojo: la exclusión
existe solo en la operación que decide y escribe `alt_text`.

### El recorrido completo, que es lo que estas reglas hacen posible

1. Cargar la imagen **sin** `alt_text` — permitido, D-010-N.
2. Asociarla a un borrador **más tarde** — es lo que describe B.5.
3. Dar el texto **en ese uso** — se persiste en `media_assets`.
4. Publicar — prospera.

La validación de publicación de §14.5 sigue siendo la **última guarda**, no el único
mecanismo: ya no puede ocurrir que un contenido sea impublicable porque nunca hubo forma
de escribir el dato.

---

## 15. Historial administrativo — cerrado en `Task/012.1` (2026-09-05)

`MVP_SCOPE.md` §3.3 fija como **alcance mínimo** del dashboard *«conteo de contenido por
tipo y estado, últimos elementos modificados y **últimos eventos de auditoría**»*. Las 38
operaciones que dejaron `Task/011` y `Task/012` cubren las dos primeras; ninguna lee
`audit_events`. Esta sección cierra esa laguna con **una** operación de solo lectura.

### 15.1 La operación

| Endpoint | Método | Éxito | Autenticación | Caché |
| --- | --- | --- | --- | --- |
| `/api/v1/admin/audit-events` | **`GET`, y solo `GET`** | `200` | Cookie de sesión | `no-store` |

Hereda la postura común de todo `/api/v1/admin` (§14, security-boundaries.md §12.1): sesión
obligatoria, `no-store` y rechazo con `422` de cualquier parámetro de consulta desconocido.
La validación de `Origin` **no aplica**: solo alcanza a los métodos que cambian estado
(§13.5), y un `GET` no lo es.

**No existen `POST`, `PUT`, `PATCH` ni `DELETE`**, y esa ausencia *es* el contrato: un
`AuditEvent` **solo se crea y se lee** (CONTENT_MODEL.md §3.9). Escribirlo sigue siendo
competencia exclusiva de los casos de uso de `Task/011` y `Task/012`. **Tampoco existe
detalle** `/{audit_event_id}`: el dashboard lista, y ninguna fuente pide navegar a un evento
suelto.

### 15.2 Parámetros

**Solo `page` y `page_size`**, con los valores ya vigentes de §5: 12 por defecto, máximo
aplicado 50 —por encima **se recorta**, nunca es error—, `page` fuera de rango devuelve
`items` vacío con `200`, y un valor no válido devuelve `422`.

**Sin filtros.** §3.3 pide *«los últimos»*, nada más. Un filtro por acción, tipo, elemento,
actor o rango de fechas sería superficie `v1` permanente (§10, regla 2); añadirlo más
adelante, con un consumidor real, es compatible (regla 3).

### 15.3 Respuesta — `Pagina[EventoDeAuditoria]`

La envoltura única de §5. Cada elemento tiene **exactamente cinco campos**:

```json
{
  "id": "uuid",
  "occurred_at": "2026-09-05T14:30:00Z",
  "action": "content.published",
  "entity_type": "post",
  "entity_id": "uuid"
}
```

| Campo | Tipo | Nulo | Por qué está |
| --- | --- | :---: | --- |
| `id` | `UUID` | no | Identidad estable del evento |
| `occurred_at` | ISO 8601 UTC | no | **Es «últimos»**: sin fecha no hay orden que mostrar |
| `action` | `string` | no | **Es «qué pasó»**; catálogo cerrado de quince acciones |
| `entity_type` | `string` | no | **Es «sobre qué»**: `content.*` no lo dice, esta columna sí (**D-012-N**) |
| `entity_id` | `UUID` | **sí** | Enlaza el evento con el elemento. Nulo en los eventos de sesión |

**No se exponen `actor_id`, `event_metadata`, `request_id` ni `ip_address`.**
`ip_address` es dato personal que listar el historial no necesita (**O-09**;
security-boundaries.md A-13); `actor_id` no informa con **un** administrador;
`event_metadata` es un objeto de forma libre que congelar en `v1` sería prematuro; y el
propósito de `request_id` —trazabilidad extremo a extremo (§9)— es de `Task/017`, que aún no
ha fijado la cabecera. Los cuatro comparten la misma razón: **añadir un campo opcional
después es compatible; retirarlo, no** (§10, reglas 2 y 3). Es el criterio con el que §12
rechazó `access_expires_at`.

### 15.4 Orden

**`occurred_at` descendente, con desempate por `id` ascendente.**

El desempate no es cosmético: `occurred_at` se rellena con `now()`, que en PostgreSQL es la
marca de **inicio de la transacción**, así que dos eventos escritos en la misma transacción
la comparten al microsegundo. Sobre un orden no total, `LIMIT`/`OFFSET` puede repetir u
omitir filas entre páginas — la misma razón de **D-009-F**, **D-012-L** y del desempate de
la biblioteca de medios. `id` es la clave primaria, `UNIQUE NOT NULL`, y **ascendente** es la
dirección que esas tres decisiones ya fijaron.

### 15.5 Errores

| Código | `code` | Cuándo |
| --- | --- | --- |
| `401` | `unauthenticated` | Sin sesión válida |
| `422` | `validation_error` | Paginación no válida o parámetro de consulta desconocido |

**No se declaran `403`, `404` ni `409`**: la operación no puede producirlos. `403` exigiría
comprobación de `Origin`, que no aplica a un `GET`; `404` no corresponde a una colección; y
sin escritura no hay conflicto de estado posible.

### 15.6 Lo que esta sección **no** cambia

- **`AuditEvent` sigue siendo inmutable.** Las guardas de `Task/008` y las invariantes 16 y
  16b de `data-model.md` quedan intactas.
- **Leer el historial no lo modifica.** *«Las lecturas no se auditan»* (CONTENT_MODEL.md
  §3.9), y está fijado por prueba contando filas reales antes y después del `GET`.
- **Ninguna migración.** `ix_audit_events_occurred_at` ya existía desde la migración `0002`,
  creado —según `data-model.md` §5— para el *«listado cronológico del historial»*.
- **`login` sigue siendo el único endpoint administrativo público.**
- **La API pública no cambia.**

### 15.7 Qué sigue abierto

| Pregunta | Propietario |
| --- | --- |
| Filtros del historial por acción, tipo, elemento o fechas | Sin propietario; ampliación compatible |
| Resolver el nombre del actor cuando exista más de un administrador | Sin propietario; fuera del MVP |
| Exponer `request_id` una vez `Task/017` fije la cabecera del correlation ID | `Task/017` |
| Retención, rotación y archivado del historial | Operación |
| Privilegio mínimo sobre `audit_events` (invariante 16b) | `Task/018` |
