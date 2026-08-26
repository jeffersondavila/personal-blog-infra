# TASK-008 — Modelo de Datos

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/008-Modelo-de-Datos` |
| **Nombre** | Modelo de Datos |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Estado** | **Aprobada** |
| **Repositorios involucrados** | personal-blog-backend · personal-blog-infra (gobierno y documentación) |
| **Dependencias** | `Task/007-Integracion-Local` (**Aprobada**) |
| **Rama** | `Task/008-Modelo-de-Datos` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base (backend)** | `2290a9fbb726f97f6d1cbdb5e4c6b1f1ce147e4c` |
| **SHA base (infra)** | `b23ad66d171dba2add42c6513f770d9f1de8e15b` |
| **Fecha de inicio** | 2026-08-25 |
| **Última actualización** | 2026-08-25 (aprobada tras la revisión correctiva) |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

| # | Comprobación | backend | infra |
| --- | --- | --- | --- |
| 1 | `main == origin/main` | Sí | Sí |
| 2 | Working tree limpio antes de crear la rama | Sí | Sí |
| 3 | Rama creada **desde `main`** | Sí | Sí |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | Sí | Sí |
| 5 | `git rev-list --count main..HEAD` == 0 | Sí | Sí |

`personal-blog-frontend` **no recibe rama**: la tarea no lo modifica.

---

## 1. Objetivo

Convertir el modelo conceptual aprobado en `Task/002`
([`CONTENT_MODEL.md`](../product/CONTENT_MODEL.md)) en un **modelo físico**
completo, mínimo y suficiente para el MVP: entidades de dominio con sus
invariantes de ciclo de vida, modelos ORM, restricciones e índices reales en
PostgreSQL y una migración Alembic que **aplica y revierte**.

## 2. Contexto

`Task/007` cerró la ETAPA 02 dejando el entorno local integrado y sano.
`Task/008` abre la ETAPA 03 y es la **primera tarea funcional del backend**
sujeta a la [BACKEND TEST-FIRST LAW](../project-management/BACKEND_TESTING_STRATEGY.md).

Todo lo que viene después depende de este esquema: `Task/009` consulta,
`Task/010` almacena medios, `Task/011` autentica y audita, `Task/012` administra.

## 3. Dentro del alcance

- [x] Entidades de dominio del **ciclo de vida de publicación** (`Post`,
      `BookReview`, `Video`, `Project`) con sus transiciones e invariantes.
- [x] *Value object* `Rating` de `BookReview`, con escala **1..5** cerrada.
- [x] Modelos ORM de los nueve tipos conceptuales: `Profile`, `Post`,
      `BookReview`, `Video`, `Project`, `Tag`, `MediaAsset`, `Administrator`,
      `AuditEvent`.
- [x] Tablas puente `Post/BookReview/Video/Project ↔ Tag`.
- [x] Tabla dependiente `profile_social_links`.
- [x] Restricciones reales: unicidad de *slug* por tipo, rango de `rating`,
      `published ⇒ published_at`, *singleton* de `Profile` y `Administrator`,
      política `ON DELETE` de `MediaAsset` y de `Tag`.
- [x] Índices justificados por consultas ya previstas.
- [x] Migración Alembic `0002`, con `downgrade` completo.
- [x] Documento durable del modelo físico en `personal-blog-infra`.
- [x] Ficha, reporte y actualización de gobierno.

## 4. Fuera del alcance

| Elemento | Tarea propietaria |
| --- | --- |
| Endpoints públicos, paginación, filtros, búsqueda, serializadores | `Task/009` |
| `ObjectStorage`, `MinIOStorage`, `S3Storage`, subida, URL prefirmadas | `Task/010` |
| Login, sesiones, JWT, *hashing* de contraseñas, *rate limiting* | `Task/011` |
| Auditoría operativa, *middleware*, catálogo de acciones | `Task/011`, `Task/012` |
| CRUD administrativo, endpoints de publicar/archivar | `Task/012` |
| Lista cerrada de proveedores de video | `Task/014` |
| Render y sanitización de Markdown | `Task/014`, `Task/015` |
| Generación automática de *slug* a partir del título | `Task/012` |
| Cualquier cambio en `personal-blog-frontend` | — |
| Cualquier recurso cloud, Terraform, Floci, VPS | ETAPAS 08+ |

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Entidades de dominio del ciclo de vida | backend | `app/modules/{posts,book_reviews,videos,projects}/domain/` |
| Modelos ORM | backend | `app/modules/*/infrastructure/models.py` |
| *Mixins* técnicos y tipo enumerado persistido | backend | `app/shared/database/{mixins,types}.py` |
| Migración | backend | `alembic/versions/*_0002_*.py` |
| Pruebas de dominio | backend | `tests/unit/` |
| Pruebas de integración | backend | `tests/integration/` |
| Documento del modelo físico | infra | `docs/architecture/data-model.md` |
| Ficha y reporte | infra | `docs/tasks/`, `docs/task-reports/` |

## 6. Criterios de aceptación

1. Existe modelo físico completo del MVP para los nueve tipos conceptuales.
2. El dominio es Python plano: no importa FastAPI, SQLAlchemy ni Alembic.
3. Los modelos ORM no se exponen como contrato HTTP.
4. `published_at` es coherente con la despublicación: nulo hasta la primera
   publicación y **conservado** al despublicar.
5. `rating` tiene escala concreta **1..5** y *check constraint* real.
6. Los *slug* son únicos **por tipo**.
7. La relación muchos a muchos con `Tag` funciona y rechaza duplicados.
8. Eliminar un `Tag` desasocia, **nunca** elimina contenido.
9. Un `MediaAsset` referenciado no puede eliminarse.
10. `Profile` y `Administrator` tienen estrategia *singleton* explícita.
11. La **ruta normal de escritura del ORM** no puede modificar ni eliminar un
    `AuditEvent`, y el perímetro exacto de esa garantía está fijado por prueba.
    *(Reformulado en la revisión pre-approval: la redacción anterior — "inmutable
    desde la aplicación" — prometía más de lo que el código entrega. Cerrar el
    resto exige retirar privilegios al rol de base de datos, que es `Task/018`.)*
12. La migración aplica, revierte y reaplica contra PostgreSQL **real**.
13. No se sembraron datos reales.
13-bis. El esquema permite persistir el **borrador mínimo** de los cuatro tipos
    publicables —solo título y slug— sin inventar valores (USER_FLOWS.md B.2).
14. La suite completa del backend pasa.
15. Existe evidencia RED → GREEN → REFACTOR.

---

## 7. TDD / Plan test-first

### 7.1 Comportamientos a construir

1. Un contenido nace en `draft` sin fecha de publicación.
2. Publicar fija `published_at` **la primera vez** y la conserva después.
3. Despublicar (`published → draft`) **conserva** `published_at`.
4. Despublicar solo existe para `Post` y `BookReview`.
5. Archivar retira el contenido conservando el registro; `archived` es terminal
   en el MVP.
6. Un estado `published` sin `published_at` es irrepresentable.
7. Una valoración de review está entre 1 y 5, ambos inclusive.
8. El esquema garantiza unicidad de *slug* por tipo.
9. El esquema rechaza asociaciones duplicadas a `Tag`.
10. Eliminar un `Tag` desasocia sin borrar contenido.
11. El esquema impide eliminar un `MediaAsset` referenciado.
12. El esquema admite como máximo un `Profile` y un `Administrator`.
13. Un `AuditEvent` no puede modificarse ni eliminarse desde la aplicación.
14. La migración `0002` aplica, revierte y reaplica.

### 7.2 Matriz de casos

> Construida **antes** de escribir implementación.

#### A. Ciclo de vida — dominio (`unit`)

| # | Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- | --- |
| A-01 | Un artículo nace en borrador | `draft()` | — | `status=draft`, `published_at=None` | dominio |
| A-02 | Publicar un borrador fija la fecha | `publish(now=T)` | `draft`, sin fecha | `status=published`, `published_at=T` | dominio |
| A-03 | Publicar conserva la primera fecha | `publish(now=T2)` | `draft` con `published_at=T1` | `published_at=T1` | dominio |
| A-04 | Publicar exige una fecha con zona horaria | `publish(now=ingenua)` | `draft` | error de estado | dominio |
| A-05 | Publicar lo ya publicado es inválido | `publish` | `published` | error de estado | dominio |
| A-06 | Publicar lo archivado es inválido | `publish` | `archived` | error de estado | dominio |
| A-07 | Despublicar conserva la fecha | `unpublish()` | `published` con `T1` | `status=draft`, `published_at=T1` | dominio |
| A-08 | Despublicar un borrador es inválido | `unpublish()` | `draft` | error de estado | dominio |
| A-09 | Despublicar lo archivado es inválido | `unpublish()` | `archived` | error de estado | dominio |
| A-10 | Archivar un borrador | `archive()` | `draft` | `archived` | dominio |
| A-11 | Archivar un publicado conserva la fecha | `archive()` | `published` con `T1` | `archived`, `published_at=T1` | dominio |
| A-12 | Archivar lo archivado es inválido | `archive()` | `archived` | error de estado | dominio |
| A-13 | `published` sin fecha es irrepresentable | `restore(published, None)` | — | error de estado | dominio |
| A-14 | Un borrador previamente publicado es válido | `restore(draft, T1)` | — | objeto válido | dominio |
| A-15 | El estado de publicación es inmutable | asignar atributo | — | error de asignación | dominio |

Se aplica a `Post` y `BookReview` (A-01 … A-15) y a `Video` y `Project`
(A-01 … A-06, A-10 … A-15, **sin** A-07/A-08/A-09).

| # | Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- | --- |
| A-16 | `Video` no admite despublicación | contrato del tipo | — | no existe `unpublish` | dominio |
| A-17 | `Project` no admite despublicación | contrato del tipo | — | no existe `unpublish` | dominio |

#### B. Valoración de reviews — dominio (`unit`)

| # | Caso | Entrada | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| B-01 | Mínimo permitido | `1` | válido | dominio |
| B-02 | Máximo permitido | `5` | válido | dominio |
| B-03 | Valor intermedio | `3` | válido | dominio |
| B-04 | Por debajo del mínimo | `0` | error de validación | dominio |
| B-05 | Negativo | `-1` | error de validación | dominio |
| B-06 | Por encima del máximo | `6` | error de validación | dominio |
| B-07 | No entero | `3.5` | error de validación | dominio |
| B-08 | Booleano disfrazado de entero | `True` | error de validación | dominio |
| B-09 | La valoración es inmutable | asignar atributo | error de asignación | dominio |

#### C. Esquema de contenido — PostgreSQL real (`integration`)

| # | Caso | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| C-01 | *Slug* duplicado en el mismo tipo | ya existe `posts.slug='x'` | `IntegrityError` (unique) | integración |
| C-02 | Mismo *slug* en tipos distintos | `posts.slug='x'` | `videos.slug='x'` se acepta | integración |
| C-03 | Estado fuera del contrato | `status='borrador'` | `IntegrityError` (check) | integración |
| C-04 | `published` sin `published_at` | — | `IntegrityError` (check) | integración |
| C-05 | `draft` **con** `published_at` | contenido despublicado | se acepta | integración |
| C-06 | `rating` por debajo | `0` | `IntegrityError` (check) | integración |
| C-07 | `rating` por encima | `6` | `IntegrityError` (check) | integración |
| C-08 | `rating` en los extremos | `1` y `5` | se aceptan | integración |
| C-09 | `rating` ausente en un borrador | `NULL` | se acepta | integración |
| C-10 | `project_status` fuera del conjunto | `'zombi'` | `IntegrityError` (check) | integración |
| C-11 | Marcas de tiempo con zona horaria | fila recién creada | `created_at.tzinfo is not None` | integración |
| C-12 | `updated_at` avanza al modificar | fila existente | `updated_at > created_at` | integración |

#### D. Etiquetas y relaciones — PostgreSQL real (`integration`)

| # | Caso | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| D-01 | Asociación muchos a muchos | post + 2 tags | el post devuelve las 2 etiquetas | integración |
| D-02 | Asociación duplicada | ya asociado | `IntegrityError` (PK compuesta) | integración |
| D-03 | Eliminar un `Tag` desasocia | post etiquetado | el post **sigue existiendo**, sin la asociación | integración |
| D-04 | Eliminar contenido desasocia | post etiquetado | el `Tag` **sigue existiendo** | integración |
| D-05 | Etiqueta inexistente | `tag_id` desconocido | `IntegrityError` (FK) | integración |
| D-06 | *Slug* de etiqueta duplicado | ya existe | `IntegrityError` (unique) | integración |

#### E. Medios — PostgreSQL real (`integration`)

| # | Caso | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| E-01 | `object_key` duplicada | ya existe | `IntegrityError` (unique) | integración |
| E-02 | Eliminar un medio referenciado | usado como portada | `IntegrityError` (FK RESTRICT) | integración |
| E-03 | Eliminar un medio libre | sin referencias | se elimina | integración |
| E-04 | Portada inexistente | `cover_id` desconocido | `IntegrityError` (FK) | integración |
| E-05 | Contenido sin portada | `cover_id NULL` | se acepta | integración |
| E-06 | Tamaño no positivo | `size_bytes=0` | `IntegrityError` (check) | integración |

#### F. *Singletons* — PostgreSQL real (`integration`)

| # | Caso | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| F-01 | Segundo `Profile` | ya existe uno | `IntegrityError` (unique del cerrojo) | integración |
| F-02 | Primer `Profile` | base vacía | se acepta | integración |
| F-03 | Segundo `Administrator` | ya existe uno | `IntegrityError` | integración |
| F-04 | Correo de administrador duplicado | ya existe | `IntegrityError` (unique) | integración |
| F-05 | Enlaces sociales ordenados | perfil con 2 enlaces | se devuelven por `display_order` | integración |
| F-06 | Orden duplicado en enlaces | mismo `display_order` | `IntegrityError` (unique compuesto) | integración |
| F-07 | Eliminar el perfil arrastra sus enlaces | perfil con enlaces | los enlaces desaparecen | integración |

#### G. Auditoría — PostgreSQL real (`integration`)

| # | Caso | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| G-01 | Registrar un evento con actor | administrador existente | se persiste | integración |
| G-02 | Evento sin actor identificado | `actor_id NULL` | se acepta (login fallido) | integración |
| G-03 | Referencia polimórfica | `entity_type` + `entity_id` | se persiste sin FK | integración |
| G-04 | Actor inexistente | `actor_id` desconocido | `IntegrityError` (FK) | integración |
| G-05 | Modificar un evento | evento persistido | error de inmutabilidad | integración |
| G-06 | Eliminar un evento | evento persistido | error de inmutabilidad | integración |
| G-07 | Eliminar el administrador con historial | evento que lo referencia | `IntegrityError` (FK RESTRICT) | integración |
| G-08 | `metadata` es contexto estructurado | diccionario | se persiste y se recupera | integración |

#### I. Borrador mínimo — PostgreSQL real (`integration`)

> **Añadida en la revisión correctiva pre-approval.** Un defecto funcional
> encontrado después de la primera declaración `Lista para validación`: el
> esquema exigía campos específicos de `BookReview` y `Video` al crear un
> borrador, contradiciendo USER_FLOWS.md B.2.

| # | Caso | Entrada | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| I-01 | Artículo mínimo | `slug` + `title` | se persiste; `draft`, sin fecha | integración |
| I-02 | Review mínima | `slug` + `title` | se persiste **sin** `book_title`, `book_author` ni `rating` | integración |
| I-03 | Vídeo mínimo | `slug` + `title` | se persiste **sin** `provider`, `video_url`, `embed_reference` ni duración | integración |
| I-04 | Proyecto mínimo | `slug` + `title` | se persiste con `project_status='active'` y `technologies=[]` | integración |
| I-05 | Guarda estructural | columnas reales de los 4 tipos | ninguna columna `NOT NULL` sin default fuera de `id`, `slug`, `title` | integración |

#### H. Migración — PostgreSQL real (`integration`)

| # | Caso | Resultado esperado | Capa |
| --- | --- | --- | --- |
| H-01 | `upgrade head` | la revisión aplicada es `head` | migración |
| H-02 | Todas las tablas del MVP existen | inspección física | migración |
| H-03 | Restricciones e índices declarados existen | inspección física | migración |
| H-04 | `downgrade` a la revisión anterior | ninguna tabla de negocio queda | migración |
| H-05 | Reaplicación | vuelve a `head` sin residuos | migración |
| H-06 | Sin *drift* entre metadata y esquema | `compare_metadata` vacío | migración |

### 7.3 Tests RED esperados

| Test | Capa | Motivo de fallo esperado |
| --- | --- | --- |
| `test_un_articulo_nace_como_borrador` y resto de A-* | dominio | `NotImplementedError`: el comportamiento aún no está implementado |
| `test_la_valoracion_minima_es_uno` y resto de B-* | dominio | `NotImplementedError` |
| C-*, D-*, E-*, F-*, G-* | integración | `ProgrammingError: relation "…" does not exist`: la tabla aún no existe |
| H-* | migración | la revisión `0002` no existe / faltan tablas |

> **Sin `ImportError` como RED.** El esqueleto del módulo (clase, firma y
> `NotImplementedError`) se crea antes de ejecutar la prueba, para que el fallo
> sea la **ausencia del comportamiento** y no la ausencia del archivo
> ([`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md) §5.2).

### 7.4 Integración necesaria

**PostgreSQL real**, base dedicada `personal_blog_test` con la marca
`personal-blog:test-database`. El comportamiento probado depende de
*constraints*, claves foráneas, `ON DELETE`, unicidad, tipos con zona horaria y
del ciclo real de migraciones: nada de eso lo demuestra otro motor.
**Prohibido SQLite** (§8.3 de la estrategia).

MinIO **no** se usa: `Task/008` no toca almacenamiento de objetos.

### 7.5 Casos negativos y de seguridad

- Estados fuera del contrato cerrado (C-03) y `project_status` inválido (C-10).
- Valoraciones fuera de escala (B-04 … B-08, C-06, C-07).
- Claves foráneas inexistentes (D-05, E-04, G-04).
- Duplicados (C-01, D-02, D-06, E-01, F-01, F-03, F-04, F-06).
- Eliminación de un medio en uso (E-02) y de un administrador con historial (G-07).
- Modificación y borrado de un registro de auditoría (G-05, G-06).
- **Ningún dato real** en migraciones ni en pruebas: nombres, correos y claves de
  objeto son ficticios; `password_hash` es una cadena de relleno, no un hash real.

### 7.6 Regresiones relevantes

- `tests/integration/test_migrations.py` — el contrato durable de M-04 debe
  seguir en verde con tablas de negocio presentes.
- `tests/test_grafo_de_fixtures_de_integracion.py` — toda fixture nueva del
  harness debe seguir dependiendo de `destino_de_integracion_verificado`.
- `tests/test_hermeticidad*.py` — la suite sigue sin leer el `.env` del
  desarrollador.
- `tests/test_openapi.py`, `tests/test_health.py` — la aplicación sigue
  arrancando sin tocar la base de datos.

---

## 8. Plan de validación

| Criterio | Cómo se comprueba |
| --- | --- |
| 1, 2, 3 | Inspección de la estructura de módulos y de los imports del dominio. |
| 4 | A-02, A-03, A-07, A-11, C-04, C-05. |
| 5 | B-01 … B-08, C-06 … C-09. |
| 6 | C-01, C-02, D-06. |
| 7 | D-01, D-02. |
| 8 | D-03, D-04. |
| 9 | E-02, E-03. |
| 10 | F-01 … F-04. |
| 11 | G-05, G-06, G-07. |
| 12 | H-01 … H-06 y `test_migrations.py`. |
| 13 | Lectura de la migración: sin `op.bulk_insert` ni `INSERT`. |
| 14 | `pytest` completo. |
| 15 | Reporte de la tarea, sección de evidencia por *slice*. |

## 9. Comandos de validación

```powershell
# Entorno de integracion (la URL nunca se imprime)
$env:PERSONAL_BLOG_TEST_DATABASE_URL = "postgresql://<usuario>:<clave>@127.0.0.1:55432/personal_blog_test"

ruff check .
ruff format --check .
mypy
pytest -q
pytest -m integration -q
pytest -W error -q
pytest --cov -q
pip check

alembic current
alembic history --verbose
```

## 10. Evidencia esperada

- Salida RED y GREEN de cada *slice*.
- Inspección física de tablas, restricciones e índices.
- Ciclo `upgrade` → `downgrade` → `upgrade` contra PostgreSQL real.
- Suite completa con su recuento real.
- `docker compose ps` con los servicios sanos.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | Sobreingeniería del modelo (superentidad `Content`, EAV, herencia) | Alto | Prohibido explícitamente; cada tipo tiene su tabla y sus columnas. |
| 2 | Rigidez del esquema ante tipos futuros | Medio | Etiquetas y medios genéricos; decisiones registradas. |
| 3 | Migración irreversible | Alto | `downgrade` completo y probado; convención de nombres ya vigente. |
| 4 | Pruebas destructivas contra la base de desarrollo | Crítico | Guarda *fail-closed* de `Task/005.6`/`005.7`, ya vigente. |
| 5 | Invariantes duplicadas en dominio y base sin propósito | Medio | Matriz de *ownership* explícita; cada capa prueba lo que posee. |
| 6 | Deriva entre metadata y esquema | Medio | H-06 compara metadata contra el esquema real. |

## 12. Decisiones técnicas

Catorce decisiones (D-A a D-P) con sus alternativas y justificación en
[`data-model.md`](../architecture/data-model.md) §3; resumen en el
[reporte](../task-reports/TASK-008-report.md) §4.

**Todas quedan marcadas como `Propuesta — pendiente de aprobación`.** Ninguna crea ni
reemplaza un ADR: son decisiones de diseño **dentro** de la arquitectura ya aceptada
(ADR-004 y ADR-005), no cambios a ella.

## 13. Documentación creada o actualizada

- `docs/architecture/data-model.md` — **creado**: modelo físico del MVP.
- `docs/product/CONTENT_MODEL.md` — cierre de las decisiones que dejaba abiertas.
- `docs/project-management/STATUS.md`, `ROADMAP.md`,
  `docs/stages/STAGE-03-domain-and-backend.md` — gobierno.
- `docs/tasks/TASK-008-data-model.md`, `docs/task-reports/TASK-008-report.md`.
- `personal-blog-backend/README.md` — modelo de datos y migración `0002`.

## 14. Archivos modificados

| Repositorio | Archivos | Acción |
| --- | ---: | --- |
| backend | 21 | creados |
| backend | 10 | modificados |
| infra | 3 | creados (modelo físico, ficha, reporte) |
| infra | 5 | modificados (gobierno y documentación) |
| frontend | 0 | **sin rama y sin cambios** |

Detalle por archivo: [reporte](../task-reports/TASK-008-report.md) §14.

## 15. Resultado de pruebas

| Prueba | Comando | Resultado | Exit code |
| --- | --- | --- | :---: |
| Lint | `ruff check .` | `All checks passed!` | 0 |
| Formato | `ruff format --check .` | 88 archivos ya formateados | 0 |
| Tipado | `mypy` | sin incidencias en 86 archivos | 0 |
| Dominio | `pytest tests/unit -q` | **74 passed** | 0 |
| Integración | `pytest -m integration -q` | **95 passed** | 0 |
| Suite completa | `pytest -q -W error` | **250 passed, 1 skipped, 0 warnings** | 0 |
| Cobertura | `pytest --cov -q` | **100 %** (722 sentencias, 62 ramas) | 0 |
| Dependencias | `pip check` | sin requisitos rotos | 0 |

La única omisión es **preexistente**: `time.tzset` no existe en Windows.

## 16. Problemas encontrados

Siete defectos reales, todos corregidos y con su regresión en la suite. Ninguno se resolvió
debilitando una prueba. Detalle completo en el
[reporte](../task-reports/TASK-008-report.md) §6:

1. El dominio cargaba FastAPI al importar una excepción del paquete `shared.errors`.
2. La plantilla de Alembic no emitía los imports de dialecto de `--autogenerate`.
3. Una prueba de `Task/005` afirmaba que el proyecto no tiene tablas de negocio.
4. El descubrimiento de fixtures confundía `sqlalchemy.func` con una fixture.
5. `now()` es la hora de inicio de transacción: una prueba partía de una premisa irreal.
6. La sesión transaccional del harness emitía `SAWarning`.
7. Dos pruebas esperaban el rechazo en el `flush` en lugar del `execute`.

Y cuatro más en la **revisión correctiva pre-approval**, después de la primera
declaración `Lista para validación`:

8. **Bloqueante.** El esquema exigía `book_title`, `book_author`, `provider` y
   `video_url` al crear un borrador, contradiciendo USER_FLOWS.md B.2.
9. **Bloqueante.** `STATUS.md` y el reporte condicionaban `Task/009` a que el PR
   estuviera fusionado y normalizado: estado transitorio persistido como vigente,
   prohibido por WORKFLOW §6.1.
10. La garantía de inmutabilidad de `AuditEvent` estaba **sobredimensionada**: el
    DML masivo del ORM la sortea.
11. El *owner* del *bootstrap* de `Profile`/`Administrator` estaba atribuido de
    forma vaga a "`Task/012` o posterior"; el ROADMAP ya lo asigna a `Task/036` y
    a `Task/022`.

## 17. Pasos de validación para el usuario

Comandos exactos en el [reporte](../task-reports/TASK-008-report.md) §15.

## 18. Deuda técnica pendiente

Doce elementos, con dueño asignado, en el
[reporte](../task-reports/TASK-008-report.md) §16. **Riesgos nuevos: ninguno.**

## 19. Próxima tarea

`Task/009-API-Publica` — consultas públicas, paginación, filtros y búsqueda
sobre el modelo que esta tarea define. **Pendiente, no iniciada.**

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | 2026-08-25 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/008-Modelo-de-Datos` |
| **Efecto en el avance** | 8 / 41 (**20 %**); ETAPA 03 pasa a 1 / 5 (20 %) |

> Aprobada por el usuario tras la revisión correctiva pre-approval, que corrigió
> dos hallazgos bloqueantes —el borrador mínimo de `BookReview` y `Video`, y el
> estado transitorio persistido contra WORKFLOW §6.1— y dos de precisión —el
> alcance real de la inmutabilidad de `AuditEvent` y el *owner* canónico del
> *bootstrap*—.
