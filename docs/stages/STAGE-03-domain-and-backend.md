# ETAPA 03 — Dominio y Backend

| Campo | Valor |
| --- | --- |
| **Número** | 03 |
| **Estado** | Pendiente |
| **Dependencias** | [ETAPA 02](STAGE-02-application-foundations.md) |
| **Tareas** | 5 |
| **Aprobadas** | 0 |
| **Avance** | 0 % |
| **Hito que completa** | Backend funcionalmente completo para el MVP. |

---

## Objetivo

Modelar el dominio del blog y exponer las APIs pública y administrativa, con
almacenamiento de archivos compatible con S3 y autenticación del administrador.

## Por qué esta etapa existe

Es el núcleo funcional del producto. Construir el backend antes que la interfaz permite
que el frontend se desarrolle contra contratos ya estables.

## Tareas

### `Task/008-Modelo-de-Datos` — *Pendiente*

Perfil, artículos, reviews de libros, videos, proyectos, etiquetas, medios,
administrador y auditoría. Migraciones Alembic.

**Depende de:** `Task/007`.

### `Task/009-API-Publica` — *Pendiente*

Consultas públicas, paginación, filtros, búsqueda y exposición exclusiva de contenido
publicado.

**Depende de:** `Task/008`.

### `Task/010-Almacenamiento-Compatible-S3` — *Pendiente*

Interfaz `ObjectStorage`, implementación MinIO para local, adaptador futuro para
Amazon S3, gestión de imágenes y miniaturas.

**Depende de:** `Task/008`.

### `Task/011-Autenticacion-Administrativa` — *Pendiente*

Login, sesiones o tokens, protección de endpoints, rate limiting y auditoría de accesos.

**Depende de:** `Task/008`.

### `Task/012-API-Administrativa` — *Pendiente*

CRUD de contenido, borradores, publicación, archivado y gestión de imágenes.

**Depende de:** `Task/009`, `Task/010`, `Task/011`.

**Repositorio de toda la etapa:** `personal-blog-backend`.

## Criterios de salida de la etapa

- [ ] El esquema cubre todas las secciones del blog previstas en el MVP.
- [ ] Las migraciones aplican sobre base vacía y revierten.
- [ ] La API pública nunca expone borradores ni contenido archivado.
- [ ] Las imágenes se suben y recuperan desde MinIO a través de `ObjectStorage`.
- [ ] Ningún endpoint administrativo es accesible sin autenticación.
- [ ] Las acciones administrativas quedan registradas en auditoría.
- [ ] Cobertura de pruebas en la lógica de dominio y en los endpoints críticos.

## Fuera del alcance de la etapa

- Interfaz de usuario (Etapa 04).
- SEO y rendimiento (Etapa 05).
- Adaptador real de Amazon S3 en ejecución cloud (Etapa 10).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Modelo de datos demasiado rígido para tipos de contenido futuros. | Etiquetas y medios genéricos; decisiones registradas como ADR. |
| Acoplamiento directo a MinIO. | Toda la escritura y lectura pasa por la interfaz `ObjectStorage`. |
| Autenticación insegura por simplicidad. | Endurecimiento revisado en `Task/018`. |
| Búsqueda ineficiente al crecer el contenido. | Índices explícitos y paginación obligatoria. |

## Siguiente etapa

[ETAPA 04 — Experiencia del Usuario](STAGE-04-user-experience.md)
