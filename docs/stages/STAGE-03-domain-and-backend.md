# ETAPA 03 — Dominio y Backend

| Campo | Valor |
| --- | --- |
| **Número** | 03 |
| **Estado** | **En curso** |
| **Dependencias** | [ETAPA 02](STAGE-02-application-foundations.md) |
| **Tareas** | 5 |
| **Aprobadas** | **3** |
| **Avance** | **60 %** — 3 de 5 |
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

### `Task/008-Modelo-de-Datos` — **Aprobada** (2026-08-25)

Perfil, artículos, reviews de libros, videos, proyectos, etiquetas, medios,
administrador y auditoría. Migraciones Alembic.

**Depende de:** `Task/007`.
**Test-first:** invariantes del modelo y transiciones de estado por prueba primero. Las
migraciones se validan con integración real (`upgrade`, `downgrade`, reaplicación) contra el
PostgreSQL local, nunca contra SQLite.

> **Aprobada el 2026-08-25.** Modelo físico completo del MVP en **14 tablas**, migración
> `0002` reversible, ciclo de vida de publicación en el dominio y escala de valoración
> **1..5**. Documentado en [`data-model.md`](../architecture/data-model.md) — **Vigente**.
> Primera tarea de la etapa aprobada: **1 de 5**.

### `Task/009-API-Publica` — **Aprobada**

Consultas públicas, paginación, filtros, búsqueda y exposición exclusiva de contenido
publicado.

**Depende de:** `Task/008` (**Aprobada**).
**Test-first:** contrato HTTP, paginación y filtros especificados por prueba antes de
implementar. Obligatorio el caso negativo que demuestra que **nunca** se expone contenido no
publicado.

> **Aprobada el 2026-08-27.** Los **diez** endpoints públicos del
> contrato, con paginación (`page_size` 12 por defecto, 50 máximo), filtros `tag`,
> `featured` y `sort` con lista cerrada, orden determinista con desempate por `slug`, y
> búsqueda básica con `ILIKE` sobre contenido publicado. **No modifica el esquema
> físico**: no hay migración nueva y `0002` sigue siendo `head`.
>
> La invariante 19 de [`data-model.md`](../architecture/data-model.md) —*contenido no
> publicado nunca sale al público*— queda implementada **dentro de las consultas** y
> cubierta por caso negativo en los cuatro tipos, en listados, detalles, filtro por
> etiqueta, catálogo de etiquetas y búsqueda.
>
> Suite completa: **597 pasan, 1 omitida** (`time.tzset` en Windows, preexistente), **0
> advertencias** con `-W error`. Cobertura de `app/`: **100 %**.
> Ficha: [TASK-009](../tasks/TASK-009-public-api.md) ·
> Reporte: [TASK-009-report](../task-reports/TASK-009-report.md).
>
> **Remediación TDD antes de aprobar.** En la primera ejecución seis *slices* tuvieron
> sus pruebas escritas después del código; la desviación se detectó **pre-approval** y esos
> seis *slices* se reconstruyeron test-first —RED real sobre código inexistente— antes de
> cualquier *commit*. La implementación aprobada es la reconstruida. Detalle en el
> [reporte §I.2, §I.5 y §I.6](../task-reports/TASK-009-report.md).
>
> **Avance de la etapa: 2 de 5.**

### `Task/010-Almacenamiento-Compatible-S3` — **Aprobada** (2026-08-28)

Interfaz `ObjectStorage`, implementación `MinIOStorage` para local, **implementación
`S3Storage`**, gestión de imágenes y miniaturas.

> **Qué implementa aquí y qué no** (desambiguado en `Task/005.5`; antes decía «adaptador
> futuro para Amazon S3», que podía leerse como que el código llegaba en otra tarea).
>
> | Aquí, en `Task/010` | Más tarde |
> | --- | --- |
> | Interfaz `ObjectStorage` | — |
> | `MinIOStorage` y **`S3Storage`**: **ambas implementaciones, con código real** | — |
> | **Pruebas de contrato comunes** a las dos implementaciones | — |
> | Configuración que selecciona la implementación por entorno | — |
> | — | Bucket, políticas, CORS, *lifecycle* y expiración de prefirmadas → **`Task/030`** |
> | — | Validación de `S3Storage` **contra S3 real** → **`Task/030`** |
> | — | *Wiring* productivo en la Lambda → **`Task/032`** |
>
> **`Task/010` no necesita AWS real ni crea ningún recurso cloud.** Su `S3Storage` se
> prueba por contrato y, cuando aporte valor, contra el S3 emulado del laboratorio.
>
> **Regla de persistencia:** se almacena la **clave del objeto**, nunca una URL prefirmada
> —que expira—. La URL de acceso se genera al servir. Aplica también al Markdown del
> contenido.

**Depende de:** `Task/008` (**Aprobada**).
**Test-first:** primero las pruebas de **contrato** de `ObjectStorage`; después la
integración real con MinIO.

> **En progreso** desde el 2026-08-28. Interfaz `ObjectStorage` con cinco
> operaciones, `MinIOStorage` y `S3Storage` **ambas con código real**, y una
> suite de contrato de **13 casos ejecutada contra las dos** (26 ejecuciones)
> contra el MinIO local. `S3Storage` se prueba contra ese mismo endpoint
> S3-compatible: **sin AWS real y sin ningún recurso cloud**.
>
> Añade además la gestión de imágenes: validación por **decodificación** del
> contenido, claves no predecibles, miniaturas WebP derivadas, persistencia de
> `MediaAsset` con compensación ante fallo parcial, y el caso de uso de borrado
> que dice **dónde** se usa un medio.
>
> **Cierra D-009-O**: `MedioPublico` gana `access_url`, un enlace temporal
> generado al servir y nunca persistido, **y realmente consumible**: el
> adaptador separa el endpoint **operativo** —el que usa el backend— del de
> **acceso** —el que aparece en el enlace—, porque el anfitrión forma parte de
> la firma SigV4 y no puede corregirse después. Verificado con un `GET` real
> desde el host contra el backend recreado en Docker. La política cloud
> concreta —**D-08**— sigue siendo de `Task/030`.
>
> **No modifica el esquema físico**: `0002` sigue siendo `head`.
>
> Ficha: [TASK-010](../tasks/TASK-010-s3-compatible-storage.md) ·
> Reporte: [TASK-010-report](../task-reports/TASK-010-report.md).
>
> Devuelta una vez por la revisión externa con dos bloqueantes —el enlace local
> no era consumible y el backend en Docker no se había recreado— y una
> corrección de trazabilidad TDD. Los tres se resolvieron antes de aprobar;
> detalle en el [reporte §S.1, §W.1 y §K.2](../task-reports/TASK-010-report.md).
>
> **Avance de la etapa: 3 de 5.**

### `Task/011-Autenticacion-Administrativa` — *Pendiente*

Login, sesiones o tokens, protección de endpoints, rate limiting y auditoría de accesos.

> **Resuelve D-15 — topología lógica de dominios** (asignado en `Task/005.5`). No se puede
> elegir entre cookie de sesión y *token*, ni definir la estrategia CSRF, sin saber si el
> sitio y el API compartirán dominio. Antes se decía que eso dependía de `Task/035`, que
> ocurre **veinticuatro tareas después**: una dependencia invertida.
>
> Aquí se decide la **topología lógica** —mismo *site*, subdominio de API o dominios
> separados—, la naturaleza de las cookies —*first-party* o *cross-site*— y la política
> CORS resultante. **No se elige el dominio comercial real**: eso sigue siendo `Task/035`
> (**D-07**), que materializa DNS y certificados sobre la topología ya decidida.

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
- [x] La API pública nunca expone borradores ni contenido archivado. *(`Task/009`, **Aprobada** el 2026-08-27.)*
- [x] Las imágenes se suben y recuperan desde MinIO a través de `ObjectStorage`. *(`Task/010`, **Aprobada** el 2026-08-28.)* *(Entregado en `Task/010`; se marca al aprobarse.)*
- [x] **`MinIOStorage` y `S3Storage` existen y superan las mismas pruebas de contrato.** *(`Task/010`: 15 casos × 2 implementaciones.)* *(Entregado en `Task/010`; se marca al aprobarse.)*
- [x] **Nada persiste una URL prefirmada**: la base de datos y el Markdown guardan claves
      de objeto. *(`Task/010`; comprobado sobre las columnas reales.)* *(Entregado en `Task/010` para la base de datos, fijado por prueba sobre
      las columnas reales; el Markdown del contenido es de `Task/012`.)*
- [ ] **D-15 resuelta**: topología lógica de dominios y política de cookies/CORS decidida.
- [ ] Ningún endpoint administrativo es accesible sin autenticación.
- [ ] Las acciones administrativas quedan registradas en auditoría.
- [ ] Cobertura de pruebas en la lógica de dominio y en los endpoints críticos.
- [ ] **Cada tarea de la etapa demuestra su ciclo test-first**: matriz de casos, evidencia de
      RED, evidencia de GREEN y refactor ejecutado o declarado innecesario.

## Fuera del alcance de la etapa

- Interfaz de usuario (Etapa 04).
- SEO y rendimiento (Etapa 05).
- **Recursos de Amazon S3 y la ejecución de `S3Storage` contra AWS real** (`Task/030`). El
  **código** de `S3Storage` sí pertenece a `Task/010`.
- **Dominio concreto, DNS y certificados** (`Task/035`, **D-07**). Aquí solo se decide la
  **topología lógica** (**D-15**).

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
