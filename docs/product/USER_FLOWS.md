# Flujos de usuario — Blog Personal

| Campo | Valor |
| --- | --- |
| **Estado** | Propuesta de `Task/002-Definir-MVP-y-Arquitectura` — Lista para validación |
| **Fecha** | 2026-07-26 |

Describe **qué puede hacer cada tipo de usuario** y en qué orden. Es la fuente que
justifica los endpoints de [api-contracts.md](../architecture/api-contracts.md) y las
pantallas de las Etapas 04 y 05.

Alcance de referencia: [MVP_SCOPE.md](MVP_SCOPE.md).

---

## Actores

| Actor | Quién es | Autenticación |
| --- | --- | --- |
| **Visitante** | Cualquier persona que llega al sitio público. | Ninguna |
| **Administrador** | El propietario del blog. Único administrador del MVP. | Obligatoria |

---

# Parte A — Flujos públicos

Todos son de **solo lectura** y **no requieren autenticación**. Ninguno expone contenido
en estado `draft` o `archived`.

## A.1 Visitar Inicio

1. El visitante abre `/`.
2. El frontend solicita el perfil y el contenido destacado.
3. Se muestran: presentación breve, contenido destacado y accesos a las secciones.
4. Los metadatos de la página se establecen para compartir en redes.

**Datos:** `GET /api/v1/profile`, listados con `featured=true`.
**Error:** si falla la carga, se muestra un estado de error con reintento; el sitio no
queda en blanco.

## A.2 Explorar artículos

1. El visitante abre `/articulos`.
2. Se muestra la primera página de artículos publicados, ordenados por `published_at`
   descendente.
3. Cada elemento muestra título, resumen, fecha, portada y etiquetas.
4. El visitante navega entre páginas.

**Datos:** `GET /api/v1/posts?page=1&page_size=12`.
**Vacío:** si no hay artículos, se muestra un mensaje explicativo, no una lista vacía.

## A.3 Leer un artículo

1. El visitante selecciona un artículo o entra directo por su URL con slug.
2. Se muestran título, fecha, portada, etiquetas y contenido Markdown renderizado.
3. El contenido se renderiza **sanitizado** (ver [ADR-005](../adr/ADR-005-markdown-content.md)).
4. Se establecen `title`, `description`, canonical y Open Graph propios.

**Datos:** `GET /api/v1/posts/{slug}`.
**Error:** un slug inexistente, un borrador o un archivado devuelven `404` y muestran la
página 404. **No se distingue** "no existe" de "no publicado", para no filtrar la
existencia de borradores.

## A.4 Explorar reviews

Igual que A.2, sobre `/reviews`. Cada elemento muestra además autor del libro y
valoración.

**Datos:** `GET /api/v1/book-reviews?page=1&page_size=12`.

## A.5 Consultar una review

Igual que A.3, sobre `/reviews/{slug}`, mostrando además título del libro, autor,
valoración y enlace externo si existe.

**Datos:** `GET /api/v1/book-reviews/{slug}`.

## A.6 Consultar videos

1. El visitante abre `/videos`.
2. Se muestran los videos publicados con título, descripción, miniatura y fecha.
3. Al seleccionar uno, se reproduce mediante **embed** o se abre el **enlace externo**.
4. El sitio **no aloja archivos de video**.

**Datos:** `GET /api/v1/videos?page=1&page_size=12`.
**Seguridad:** los embeds se limitan a proveedores permitidos; los enlaces externos usan
`rel="noopener noreferrer"`.

## A.7 Consultar proyectos

1. El visitante abre `/proyectos`.
2. Se muestran los proyectos publicados con título, resumen, tecnologías y enlaces
   (repositorio, demo).
3. Si el proyecto tiene detalle, se accede por `/proyectos/{slug}`.

**Datos:** `GET /api/v1/projects`, `GET /api/v1/projects/{slug}`.

## A.8 Buscar contenido

1. El visitante escribe un término en el buscador.
2. Se consulta la búsqueda básica sobre contenido publicado.
3. Se muestran resultados agrupados o etiquetados por tipo, con paginación.
4. Sin resultados, se muestra un mensaje y sugerencias de navegación.

**Datos:** `GET /api/v1/search?q={termino}&page=1&page_size=12`.
**Reglas:** término mínimo de 2 caracteres; la búsqueda **nunca** alcanza borradores ni
archivados; el término se trata como dato, jamás se interpola en una consulta.

## A.9 Filtrar por etiquetas

1. El visitante selecciona una etiqueta desde un listado o desde un contenido.
2. Se muestran los elementos publicados con esa etiqueta, paginados.
3. El filtro se refleja en la URL para poder compartirse.

**Datos:** `GET /api/v1/posts?tag={slug}`, `GET /api/v1/tags`.

## A.10 Consultar contacto y enlaces

1. El visitante abre `/contacto`.
2. Se muestran el correo (o enlace `mailto:`) y los enlaces a redes configurables.
3. **No hay formulario** ni envío de datos en el MVP.

**Datos:** `GET /api/v1/profile`.

## A.11 Ruta inexistente

Cualquier ruta no reconocida muestra la página 404, con enlace a Inicio y a las secciones
principales, y responde con el código HTTP correcto para no ser indexada.

---

# Parte B — Flujos administrativos

Todos requieren **autenticación**, salvo el propio inicio de sesión. Todos generan
**auditoría** cuando modifican datos.

## B.1 Iniciar sesión

1. El administrador abre la ruta de acceso al panel.
2. Introduce sus credenciales.
3. El backend verifica la contraseña contra su **hash**.
4. Si son correctas, se establece la sesión y se redirige al dashboard.
5. Si son incorrectas, se muestra un error **genérico** ("credenciales inválidas"), sin
   revelar si el usuario existe.
6. Los intentos fallidos repetidos activan la **protección contra fuerza bruta**.
7. El evento se registra en auditoría (éxito y fallo).

**Datos:** `POST /api/v1/admin/auth/login`, `GET /api/v1/admin/auth/me`.
**Pendiente:** el mecanismo concreto (cookie de sesión o token) se decide en `Task/011`.

## B.2 Crear borrador

1. Desde el panel, el administrador elige el tipo de contenido y crea uno nuevo.
2. Introduce título; el **slug se propone automáticamente** y es editable.
3. El contenido nace en estado `draft`.
4. Se registran `created_at` y `updated_at`.
5. La creación queda en auditoría.

**Datos:** `POST /api/v1/admin/posts` (o el recurso correspondiente).
**Validación:** slug único por tipo de contenido; título obligatorio.

## B.3 Editar borrador

1. El administrador abre un elemento existente.
2. Modifica título, resumen, contenido Markdown, etiquetas, portada o campos SEO.
3. Guarda; se actualiza `updated_at`.
4. La edición queda en auditoría.

**Datos:** `PUT`/`PATCH /api/v1/admin/posts/{id}`.
**Regla:** editar un contenido `published` actualiza el contenido visible; no lo
despublica implícitamente.

## B.4 Cargar imagen

1. El administrador sube una imagen desde el editor o desde la sección de medios.
2. El backend **valida tipo MIME y tamaño**.
3. El archivo se almacena mediante la interfaz `ObjectStorage` (MinIO en local, S3 en
   producción) con un **nombre de objeto no predecible**.
4. En base de datos se guardan **metadatos y la clave del objeto**, nunca el binario.
5. La imagen queda disponible para seleccionarse.

**Datos:** `POST /api/v1/admin/media`.
**Detalle:** [software-architecture.md](../architecture/software-architecture.md),
sección *Almacenamiento de objetos*.

## B.5 Seleccionar y eliminar imágenes

1. El administrador consulta la biblioteca de medios ya cargados.
2. Selecciona una imagen como portada o para insertarla en el contenido.
3. Para eliminar, el sistema **comprueba primero que no esté en uso**.
4. Si está en uso, la eliminación se **rechaza** indicando dónde se usa.
5. Si no lo está, se pide confirmación y se elimina del almacenamiento y de la base de
   datos.
6. La eliminación queda en auditoría.

**Datos:** `GET /api/v1/admin/media`, `DELETE /api/v1/admin/media/{id}`.

## B.6 Previsualizar contenido

1. Desde el editor, el administrador abre la vista previa.
2. El Markdown se renderiza **con el mismo pipeline y la misma sanitización** que el sitio
   público.
3. La vista previa **no publica** el contenido ni lo expone públicamente: no cambia su
   estado, no genera URL pública y no lo hace accesible a visitantes.

**Aplica a:** los tres tipos cuyo contenido principal es Markdown.

| Tipo | Editor Markdown | Vista previa | Motivo |
| --- | :---: | :---: | --- |
| `Post` | Sí | **Sí** | Contenido principal en Markdown. |
| `BookReview` | Sí | **Sí** | Contenido principal en Markdown. |
| `Project` | Sí | **Sí** | Contenido principal en Markdown. |
| `Video` | **No** | **No** | Su contenido principal es el video externo (URL, proveedor y metadatos), no Markdown. |

Ver [ADR-005](../adr/ADR-005-markdown-content.md) y
[CONTENT_MODEL.md](CONTENT_MODEL.md).

## B.7 Publicar

1. El administrador pulsa publicar sobre un `draft`.
2. Se validan los campos mínimos (título, slug, contenido, y SEO si corresponde).
3. El estado pasa a `published` y se fija `published_at` si no existía.
4. El contenido aparece de inmediato en el sitio público.
5. La publicación queda en auditoría.

**Datos:** `POST /api/v1/admin/posts/{id}/publish` o actualización de `status`; la forma
exacta se cierra en `Task/012`.

## B.8 Despublicar

1. El administrador despublica un contenido `published`.
2. El estado vuelve a `draft`.
3. Desaparece del sitio público; su URL pasa a responder `404`.
4. Se conserva `published_at` como referencia histórica.
5. Queda en auditoría.

**Aplica a:** artículos y reviews.

## B.9 Archivar

1. El administrador archiva un contenido.
2. El estado pasa a `archived`.
3. Desaparece del sitio público pero **no se elimina**.
4. Sigue siendo consultable y editable desde el panel.
5. Queda en auditoría.

**Aplica a:** artículos, reviews, videos y proyectos.

## B.10 Editar perfil

1. El administrador abre la edición del perfil "Quién soy".
2. Modifica nombre, titular, biografía en Markdown, foto, correo de contacto y enlaces a
   redes.
3. Guarda; el cambio se refleja en `/quien-soy`, `/contacto` e Inicio.
4. Queda en auditoría.

**Datos:** `GET`/`PUT /api/v1/admin/profile`.
**Regla:** el perfil es un **singleton**: existe exactamente uno y no se crea ni elimina.

## B.11 Gestionar etiquetas

1. El administrador consulta, crea, renombra o elimina etiquetas.
2. Eliminar una etiqueta en uso requiere confirmación explícita y desasocia el contenido;
   **no elimina contenido**.
3. Queda en auditoría.

**Datos:** `GET`/`POST`/`PUT`/`DELETE /api/v1/admin/tags`.

## B.12 Cerrar sesión

1. El administrador cierra sesión.
2. La sesión o el token se invalidan **en el servidor**, no solo en el navegador.
3. Cualquier petición administrativa posterior responde `401`.
4. Queda en auditoría.

**Datos:** `POST /api/v1/admin/auth/logout`.

---

## Matriz flujo → recurso de API

| Flujo | Método y recurso |
| --- | --- |
| A.1 Inicio | `GET /api/v1/profile`, listados con destacados |
| A.2 Explorar artículos | `GET /api/v1/posts` |
| A.3 Leer artículo | `GET /api/v1/posts/{slug}` |
| A.4 Explorar reviews | `GET /api/v1/book-reviews` |
| A.5 Consultar review | `GET /api/v1/book-reviews/{slug}` |
| A.6 Consultar videos | `GET /api/v1/videos` |
| A.7 Consultar proyectos | `GET /api/v1/projects`, `GET /api/v1/projects/{slug}` |
| A.8 Buscar | `GET /api/v1/search` |
| A.9 Filtrar por etiqueta | `GET /api/v1/tags`, listados con `tag` |
| A.10 Contacto | `GET /api/v1/profile` |
| B.1 Iniciar sesión | `POST /api/v1/admin/auth/login`, `GET /api/v1/admin/auth/me` |
| B.2–B.3 Crear y editar | `POST`/`PUT` sobre `/api/v1/admin/{recurso}` |
| B.4–B.5 Medios | `POST`/`GET`/`DELETE /api/v1/admin/media` |
| B.6 Vista previa (`Post`, `BookReview`, `Project`) | Solo frontend, sin endpoint propio |
| B.7–B.9 Publicar, despublicar, archivar | Transición de estado en `/api/v1/admin/{recurso}` |
| B.10 Perfil | `GET`/`PUT /api/v1/admin/profile` |
| B.11 Etiquetas | `/api/v1/admin/tags` |
| B.12 Cerrar sesión | `POST /api/v1/admin/auth/logout` |

---

## Reglas transversales

1. Ningún flujo público escribe datos.
2. Ningún flujo público accede a contenido `draft` o `archived`.
3. Todo flujo administrativo que modifica datos genera un `AuditEvent`.
4. Los errores de autenticación son genéricos y no revelan si un usuario existe.
5. Toda lista está paginada; no existe un endpoint que devuelva "todo".
6. Todo contenido Markdown se sanitiza antes de renderizarse, también en la vista previa.
