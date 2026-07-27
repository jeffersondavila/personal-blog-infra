# Contratos generales de API

| Campo | Valor |
| --- | --- |
| **Estado** | Propuesta de `Task/002-Definir-MVP-y-Arquitectura` — Lista para validación |
| **Fecha** | 2026-07-26 |
| **Nivel** | **Convenciones conceptuales.** No es una especificación OpenAPI. |

> **Límite explícito.** Este documento fija **convenciones** que toda la API debe
> respetar. **No** es una especificación OpenAPI completa ni código a implementar. Los
> esquemas concretos de petición y respuesta se definen al implementar `Task/009`
> (API pública) y `Task/012` (API administrativa).

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
| `page_size` | Elementos por página. | Valor por defecto y **máximo** definidos en implementación. |

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

> La paginación por cursor queda fuera del MVP. Si el volumen lo justifica, se
> reconsidera con un ADR.

---

## 6. Filtros y orden

| Parámetro | Aplica a | Significado |
| --- | --- | --- |
| `tag` | Listados de contenido | Filtra por slug de etiqueta. |
| `featured` | Listados de contenido | Solo contenido destacado. |
| `q` | `/search` | Término de búsqueda. |
| `status` | **Solo administrativo** | Filtra por `draft`, `published`, `archived`. |
| `sort` | Listados | Campo de ordenación alternativo. Opcional. |

Reglas:

- **Orden por defecto: `published_at` descendente.**
- Los campos de ordenación permitidos son una **lista cerrada**; cualquier otro valor
  devuelve `422`.
- `status` **no existe** en la API pública: los listados públicos son siempre
  `published`.
- Los filtros desconocidos se ignoran o se rechazan de forma consistente; la decisión se
  fija en `Task/009`.

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

| Elemento | Tarea |
| --- | --- |
| Esquemas concretos de petición y respuesta | `Task/009`, `Task/012` |
| Valores por defecto y máximos de `page_size` | `Task/009` |
| Forma exacta de las transiciones de estado | `Task/012` |
| Cabecera concreta del correlation ID | `Task/017` |
| Mecanismo de autenticación y forma de la sesión | `Task/011` |
| Límites de tamaño y tipos MIME permitidos | `Task/010`, `Task/018` |
| Configuración concreta de rate limiting | `Task/011`, `Task/018` |
| Especificación OpenAPI generada | Resultado de `Task/009` y `Task/012` |
