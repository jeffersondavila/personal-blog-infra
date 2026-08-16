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

## Práctica obligatoria: test-first

> **Las cinco tareas de esta etapa son backend funcional y se desarrollan test-first.**
> Toda regla de negocio nueva empieza por una prueba que falla: **RED → GREEN → REFACTOR**.
> Regla completa y única:
> [`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md).

Cada ficha de tarea de esta etapa debe traer completa la sección *TDD / Plan test-first*
([`TASK_TEMPLATE.md`](../project-management/TASK_TEMPLATE.md) §7) **antes** de implementar,
y su reporte debe conservar la evidencia de RED y de GREEN
([`DEFINITION_OF_DONE.md`](../project-management/DEFINITION_OF_DONE.md), criterios B-1 a
B-12). Formalizado en `Task/005.1-Formalizar-TDD-Backend`.

## Tareas

### `Task/008-Modelo-de-Datos` — *Pendiente*

Perfil, artículos, reviews de libros, videos, proyectos, etiquetas, medios,
administrador y auditoría. Migraciones Alembic.

**Depende de:** `Task/007`.
**Test-first:** invariantes del modelo y transiciones de estado por prueba primero. Las
migraciones se validan con integración real (`upgrade`, `downgrade`, reaplicación) contra el
PostgreSQL local, nunca contra SQLite.

### `Task/009-API-Publica` — *Pendiente*

Consultas públicas, paginación, filtros, búsqueda y exposición exclusiva de contenido
publicado.

**Depende de:** `Task/008`.
**Test-first:** contrato HTTP, paginación y filtros especificados por prueba antes de
implementar. Obligatorio el caso negativo que demuestra que **nunca** se expone contenido no
publicado.

### `Task/010-Almacenamiento-Compatible-S3` — *Pendiente*

Interfaz `ObjectStorage`, implementación MinIO para local, adaptador futuro para
Amazon S3, gestión de imágenes y miniaturas.

**Depende de:** `Task/008`.
**Test-first:** primero las pruebas de **contrato** de `ObjectStorage`; después la
integración real con MinIO.

### `Task/011-Autenticacion-Administrativa` — *Pendiente*

Login, sesiones o tokens, protección de endpoints, rate limiting y auditoría de accesos.

**Depende de:** `Task/008`.
**Test-first:** los casos negativos son parte del alcance, no un extra: no autenticado, sin
permisos y credenciales inválidas se prueban antes de dar por protegido un endpoint.

### `Task/012-API-Administrativa` — *Pendiente*

CRUD de contenido, borradores, publicación, archivado y gestión de imágenes.

**Depende de:** `Task/009`, `Task/010`, `Task/011`.
**Test-first:** las reglas de borrador, publicación y archivado se especifican como matriz de
transiciones antes de escribir el caso de uso.

**Repositorio de toda la etapa:** `personal-blog-backend`.

## Criterios de salida de la etapa

- [ ] El esquema cubre todas las secciones del blog previstas en el MVP.
- [ ] Las migraciones aplican sobre base vacía y revierten.
- [ ] La API pública nunca expone borradores ni contenido archivado.
- [ ] Las imágenes se suben y recuperan desde MinIO a través de `ObjectStorage`.
- [ ] Ningún endpoint administrativo es accesible sin autenticación.
- [ ] Las acciones administrativas quedan registradas en auditoría.
- [ ] Cobertura de pruebas en la lógica de dominio y en los endpoints críticos.
- [ ] **Cada tarea de la etapa demuestra su ciclo test-first**: matriz de casos, evidencia de
      RED, evidencia de GREEN y refactor ejecutado o declarado innecesario.

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
| Pruebas escritas después del código, que documentan lo que hace y no lo que debe hacer. | Práctica test-first obligatoria con evidencia de RED, formalizada en [`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md). |

## Siguiente etapa

[ETAPA 04 — Experiencia del Usuario](STAGE-04-user-experience.md)
