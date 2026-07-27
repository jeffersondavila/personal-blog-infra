# Modelo de contenido — Blog Personal

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/002-Definir-MVP-y-Arquitectura` (2026-07-26) |
| **Fecha** | 2026-07-26 |
| **Nivel** | **Conceptual.** No es un diseño de base de datos. |

> **Límite explícito de esta tarea.** Aquí se describen tipos, responsabilidades y
> atributos **conceptuales**. **No** se diseñan tablas SQL, migraciones, claves foráneas,
> índices físicos, tipos de columna ni estrategias de clave primaria. Eso corresponde a
> `Task/008-Modelo-de-Datos`.

Relacionados: [MVP_SCOPE.md](MVP_SCOPE.md) · [USER_FLOWS.md](USER_FLOWS.md) ·
[ADR-005 — Contenido en Markdown](../adr/ADR-005-markdown-content.md)

---

## 1. Tipos del dominio

| Tipo | Responsabilidad | ¿Publicable? | Cardinalidad |
| --- | --- | --- | --- |
| `Profile` | Identidad del autor: quién soy, contacto y enlaces. | No aplica | Singleton (exactamente 1) |
| `Post` | Artículo técnico o personal. | Sí | Muchos |
| `BookReview` | Reseña de un libro, con valoración. | Sí | Muchos |
| `Video` | Referencia a un video externo con sus metadatos. | Sí | Muchos |
| `Project` | Proyecto o experimento de laboratorio. | Sí | Muchos |
| `Tag` | Etiqueta de clasificación transversal. | No | Muchos |
| `MediaAsset` | Imagen almacenada en el almacenamiento de objetos. | No | Muchos |
| `Administrator` | Único usuario con acceso al panel. | No | Exactamente 1 en el MVP |
| `AuditEvent` | Registro inmutable de una acción administrativa. | No | Muchos, solo lectura |

---

## 2. Atributos comunes de contenido

Los tipos publicables comparten un conjunto de atributos. **No todos aplican a todos.**

| Atributo | Significado |
| --- | --- |
| `id` | Identificador interno. No se expone si el slug basta. |
| `slug` | Identificador legible, estable y único por tipo. |
| `title` | Título del contenido. |
| `summary` | Resumen breve para listados y metadatos. |
| `content` | Cuerpo principal en Markdown. |
| `status` | `draft`, `published` o `archived`. |
| `cover` / `featured image` | Imagen de portada, referencia a un `MediaAsset`. |
| `seo_title` | Título para buscadores; si falta, se usa `title`. |
| `seo_description` | Descripción para buscadores; si falta, se usa `summary`. |
| `created_at` | Fecha de creación. |
| `updated_at` | Fecha de última modificación. |
| `published_at` | Fecha de primera publicación. Nulo mientras sea `draft`. |

### Aplicabilidad por tipo

| Atributo | Post | BookReview | Video | Project | Profile |
| --- | :---: | :---: | :---: | :---: | :---: |
| `id` | Sí | Sí | Sí | Sí | Sí |
| `slug` | Sí | Sí | Sí | Sí | No |
| `title` | Sí | Sí | Sí | Sí | No (usa `full_name`) |
| `summary` | Sí | Sí | Sí | Sí | No (usa `headline`) |
| `content` (Markdown) | Sí | Sí | **No** | Sí | Sí (biografía) |
| `status` | Sí | Sí | Sí | Sí | **No** |
| `cover` | Sí | Sí | Sí (miniatura) | Sí | Sí (foto) |
| `seo_title` | Sí | Sí | Sí | Sí | Sí |
| `seo_description` | Sí | Sí | Sí | Sí | Sí |
| `created_at` | Sí | Sí | Sí | Sí | Sí |
| `updated_at` | Sí | Sí | Sí | Sí | Sí |
| `published_at` | Sí | Sí | Sí | Sí | **No** |

Notas:

- **`Post`, `BookReview` y `Project` tienen `content` en Markdown**, y por tanto se editan
  con editor Markdown y disponen de **vista previa** en el panel.
- **`Video` no tiene `content` en Markdown.** Su contenido es el video externo; lleva una
  descripción breve. Al no ser Markdown, **no usa editor Markdown ni esa vista previa**.
  Ver [ADR-005](../adr/ADR-005-markdown-content.md).
- **`Profile` no tiene estado ni fecha de publicación**: siempre existe y siempre está
  visible. Su biografía es Markdown.

| Tipo | `content` en Markdown | Editor Markdown y vista previa |
| --- | :---: | :---: |
| `Post` | Sí | **Sí** |
| `BookReview` | Sí | **Sí** |
| `Project` | Sí | **Sí** |
| `Video` | **No** | **No** |

La vista previa **no publica ni expone** el contenido y usa el mismo pipeline de render y
sanitización que el sitio público. Flujo completo en
[USER_FLOWS.md](USER_FLOWS.md), sección B.6.

---

## 3. Detalle por tipo

### 3.1 `Profile`

Identidad del autor. Alimenta *Quién soy*, *Contacto* e *Inicio*.

| Atributo conceptual | Descripción |
| --- | --- |
| `full_name` | Nombre completo. |
| `headline` | Titular breve (rol o descripción de una línea). |
| `biography` | Biografía extensa en Markdown. |
| `photo` | Referencia a un `MediaAsset`. |
| `contact_email` | Correo de contacto público. |
| `social_links` | Colección configurable de enlaces (GitHub, LinkedIn, otros). |
| `seo_title`, `seo_description` | Metadatos. |
| `created_at`, `updated_at` | Fechas. |

Cada enlace social lleva, conceptualmente: etiqueta, URL y orden de presentación.

**Reglas:** es un singleton — no se crea ni se elimina, solo se edita. Su edición requiere
autenticación.

### 3.2 `Post` — artículo

| Atributo conceptual | Descripción |
| --- | --- |
| Comunes | `id`, `slug`, `title`, `summary`, `content`, `status`, `cover`, SEO, fechas. |
| `tags` | Etiquetas asociadas. |
| `featured` | Indica si aparece destacado en Inicio. |
| `reading_time` | Tiempo estimado de lectura, derivado del contenido. Opcional. |

**Reglas:** `slug` único entre artículos; `content` en Markdown; solo visible
públicamente si `status = published`.

### 3.3 `BookReview` — review de libro

| Atributo conceptual | Descripción |
| --- | --- |
| Comunes | `id`, `slug`, `title`, `summary`, `content`, `status`, `cover`, SEO, fechas. |
| `book_title` | Título del libro reseñado. |
| `book_author` | Autor del libro. |
| `rating` | Valoración numérica dentro de una escala definida. |
| `external_link` | Enlace opcional a ficha del libro. |
| `tags` | Etiquetas asociadas. |
| `featured` | Destacado en Inicio. |

**Reglas:** `title` (título de la review) puede diferir de `book_title`. La escala exacta
de `rating` se fija en `Task/008`; el MVP asume un entero acotado.

### 3.4 `Video`

Referencia a un video **alojado externamente**. El sistema nunca almacena archivos de
video.

| Atributo conceptual | Descripción |
| --- | --- |
| `id`, `slug`, `title`, `summary` | Identificación y descripción breve. |
| `status` | `draft`, `published`, `archived`. |
| `provider` | Proveedor del video (por ejemplo YouTube). |
| `video_url` | URL canónica del video. |
| `embed_reference` | Identificador o referencia para incrustar. |
| `thumbnail` | Miniatura: `MediaAsset` propio o URL del proveedor. |
| `duration` | Duración, si se conoce. |
| `tags`, `featured` | Clasificación y destacado. |
| SEO y fechas | Metadatos y fechas comunes. |

**Reglas:** solo se almacenan **URL, proveedor y metadatos**. Los proveedores permitidos
se restringen para acotar los embeds; la lista se cierra en `Task/014`.

### 3.5 `Project`

| Atributo conceptual | Descripción |
| --- | --- |
| Comunes | `id`, `slug`, `title`, `summary`, `content`, `status`, `cover`, SEO, fechas. |
| `technologies` | Tecnologías empleadas. |
| `repository_url` | Enlace al repositorio, opcional. |
| `demo_url` | Enlace a demo, opcional. |
| `project_status` | Estado del proyecto (por ejemplo: activo, pausado, terminado). |
| `tags`, `featured` | Clasificación y destacado. |

**Nota:** `status` (publicación) y `project_status` (estado del trabajo) son conceptos
distintos y no deben mezclarse.

### 3.6 `Tag`

| Atributo conceptual | Descripción |
| --- | --- |
| `id` | Identificador interno. |
| `slug` | Identificador legible para URLs de filtro. |
| `name` | Nombre visible. |
| `description` | Descripción opcional. |
| `created_at`, `updated_at` | Fechas. |

**Reglas:** transversal a artículos, reviews, videos y proyectos. `slug` único. Eliminar
una etiqueta **desasocia** contenido, nunca lo elimina.

### 3.7 `MediaAsset`

Imagen almacenada en el almacenamiento de objetos. **La base de datos guarda metadatos y
la clave del objeto, nunca el binario.**

| Atributo conceptual | Descripción |
| --- | --- |
| `id` | Identificador interno. |
| `object_key` | Clave del objeto en el almacenamiento. No predecible. |
| `original_filename` | Nombre original, solo informativo. |
| `mime_type` | Tipo MIME validado. |
| `size_bytes` | Tamaño validado. |
| `width`, `height` | Dimensiones, si se conocen. |
| `alt_text` | Texto alternativo, necesario para accesibilidad. |
| `checksum` | Suma de verificación, para detectar duplicados. Opcional. |
| `created_at` | Fecha de carga. |

**Reglas:** no se elimina si está en uso; la comprobación de uso es obligatoria antes de
borrar (flujo B.5). El acceso en producción se hace mediante **URL prefirmada** sobre un
bucket privado.

### 3.8 `Administrator`

| Atributo conceptual | Descripción |
| --- | --- |
| `id` | Identificador interno. |
| `username` o `email` | Identificador de acceso. |
| `password_hash` | **Hash** de la contraseña. Nunca la contraseña. |
| `display_name` | Nombre visible en el panel. |
| `last_login_at` | Último acceso correcto. |
| `failed_login_attempts` | Apoyo a la protección contra fuerza bruta. |
| `locked_until` | Bloqueo temporal, si aplica. |
| `created_at`, `updated_at` | Fechas. |

**Reglas:** exactamente un administrador en el MVP. **Nunca** se almacena la contraseña en
claro ni se expone `password_hash` por la API. El algoritmo de hash concreto se fija en
`Task/011`.

### 3.9 `AuditEvent`

Registro **inmutable** de acciones administrativas relevantes.

| Atributo conceptual | Descripción |
| --- | --- |
| `id` | Identificador interno. |
| `occurred_at` | Momento del evento. |
| `actor` | Administrador que lo ejecutó. |
| `action` | Acción realizada (crear, editar, publicar, despublicar, archivar, eliminar, iniciar o cerrar sesión). |
| `entity_type` | Tipo afectado. |
| `entity_id` | Elemento afectado. |
| `request_id` | Correlation ID de la petición. |
| `metadata` | Contexto adicional no sensible. |
| `ip_address` | Origen de la petición, si se decide conservar. |

**Reglas:** solo se crea y se lee — **nunca se edita ni se elimina** desde la aplicación.
No registra contraseñas, tokens ni secretos. Qué acciones exactas se auditan se cierra en
`Task/011` y `Task/012`.

---

## 4. Relaciones conceptuales

```
Profile (1) ──── photo ────> MediaAsset
Profile (1) ──── social_links (colección embebida)

Post        ──── cover ────> MediaAsset
Post        ──── tags  ────> Tag        (muchos a muchos)

BookReview  ──── cover ────> MediaAsset
BookReview  ──── tags  ────> Tag        (muchos a muchos)

Video       ──── thumbnail ────> MediaAsset (opcional)
Video       ──── tags      ────> Tag

Project     ──── cover ────> MediaAsset
Project     ──── tags  ────> Tag

Administrator (1) ──── ejecuta ────> AuditEvent (muchos)
AuditEvent        ──── referencia ─> cualquier tipo (por entity_type + entity_id)
```

> Cómo se materializan estas relaciones (tablas puente, claves foráneas, cascadas) es
> decisión de `Task/008`.

---

## 5. Invariantes del modelo

1. Un contenido `published` **debe** tener `published_at`.
2. Un contenido `draft` **no** aparece en ninguna respuesta pública.
3. Un contenido `archived` **no** aparece en ninguna respuesta pública, pero se conserva.
4. Los `slug` son **únicos por tipo** y estables: cambiarlos rompe URLs y SEO.
5. `MediaAsset` en uso **no** puede eliminarse.
6. `Profile` existe siempre y es único.
7. Existe exactamente un `Administrator` en el MVP.
8. Un `AuditEvent` nunca se modifica ni se elimina.
9. Ningún tipo expone `password_hash` ni claves internas de objeto sin control.
10. Toda fecha se almacena y se expone en **UTC, formato ISO 8601**.

---

## 6. Qué queda para `Task/008`

- Tablas, columnas, tipos y restricciones.
- Estrategia de clave primaria (entero secuencial o UUID).
- Índices, incluidos los de búsqueda.
- Implementación de la relación muchos a muchos con `Tag`.
- Escala concreta de `rating`.
- Política de retención de `AuditEvent`.
- Migraciones Alembic.
