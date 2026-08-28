# Contratos generales de API

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/002-Definir-MVP-y-Arquitectura` (2026-07-26) |
| **Fecha** | 2026-07-26 · §5, §6 y §11 completadas por `Task/009-API-Publica` (2026-08-26) |
| **Nivel** | **Convenciones conceptuales.** No es una especificación OpenAPI. |

> **Límite explícito.** Este documento fija **convenciones** que toda la API debe
> respetar. **No** es una especificación OpenAPI completa ni código a implementar. Los
> esquemas concretos de petición y respuesta se definen al implementar `Task/009`
> (API pública) y `Task/012` (API administrativa).
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

---

## 4. Recursos administrativos (conceptuales)

Todos requieren autenticación **excepto `login`**.

| Recurso | Propósito |
| --- | --- |
| `POST /api/v1/admin/auth/login` | Iniciar sesión. Único endpoint administrativo público. |
| `POST /api/v1/admin/auth/logout` | Cerrar sesión e invalidarla en el servidor. |
| `GET /api/v1/admin/auth/me` | Consultar la sesión actual. |
| `/api/v1/admin/profile` | Consultar y editar el perfil. |
| `/api/v1/admin/posts` | Gestión completa de artículos. |
| `/api/v1/admin/book-reviews` | Gestión completa de reviews. |
| `/api/v1/admin/videos` | Gestión completa de videos. |
| `/api/v1/admin/projects` | Gestión completa de proyectos. |
| `/api/v1/admin/tags` | Gestión de etiquetas. |
| `/api/v1/admin/media` | Carga, listado y borrado controlado de imágenes. |

Los recursos administrativos operan sobre **identificadores internos**, no sobre slugs:
el slug puede cambiar mientras se edita un borrador.

La forma exacta de las transiciones de estado (publicar, despublicar, archivar) —
subrecurso dedicado o actualización del campo `status` — se decide en `Task/012`.

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
| Esquemas de petición y respuesta **administrativas** | `Task/012` | Abierto |
| Valores por defecto y máximos de `page_size` | `Task/009` | **Cerrado** (2026-08-26) — 12 y 50 |
| Política de parámetros desconocidos | `Task/009` | **Cerrado** (2026-08-26) — se rechazan |
| Lista cerrada de `sort` y su dirección | `Task/009` | **Cerrado** (2026-08-26) |
| Forma de los resultados de `/search` | `Task/009` | **Cerrado** (2026-08-26) — colección plana con `type` |
| Forma exacta de las transiciones de estado | `Task/012` | Abierto |
| Cabecera concreta del correlation ID | `Task/017` | Abierto |
| Mecanismo de autenticación y forma de la sesión | `Task/011` | Abierto |
| Límites de tamaño y tipos MIME permitidos | `Task/010`, `Task/018` | Abierto |
| Configuración concreta de rate limiting | `Task/011`, `Task/018` | Abierto |
| **Representación pública de una referencia a `MediaAsset`** | `Task/010` | Parcial — `Task/009` expone `alt_text`, `width` y `height`; el campo de acceso lo añade `Task/010` |
| Especificación OpenAPI generada | `Task/009` y `Task/012` | Parcial — la parte pública ya se genera |
