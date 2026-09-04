# TASK-012 — API Administrativa · Reporte

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/012-API-Administrativa` |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Estado** | **Aprobada** ✔ el 2026-09-03 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/012-API-Administrativa` |
| **Fecha** | 2026-09-01 · **cierre aprobado el 2026-09-03** (§BP) |
| **Repositorios modificados** | `personal-blog-backend` · `personal-blog-infra` |
| **Repositorio no modificado** | `personal-blog-frontend` |
| **Ficha** | [TASK-012](../tasks/TASK-012-administrative-api.md) |

---

## A. Preflight Git

Verificado **en vivo** antes de crear ninguna rama.

| Comprobación | backend | infra | frontend |
| --- | --- | --- | --- |
| Rama de partida | `main` | `main` | `main` |
| `main` == `origin/main` | `561128b5…` ✔ | `eceb5b35…` ✔ | `fd62f221…` ✔ |
| `git status --porcelain` | vacío | vacío | vacío |
| `main` es ancestro de `dev` | **sí** | **sí** | no aplica |
| `git rev-list --count dev..main` | **0** | **0** | no aplica |
| `git diff main dev` | vacío | vacío | no aplica |

Ningún cambio no reconocido. No se usó `reset`, `restore`, `clean`, `stash` automático ni
`push --force` en ningún momento.

## B. Ramas

| Comprobación | backend | infra |
| --- | --- | --- |
| SHA base (`main` al crear) | `561128b52c50207c7c829e260dd1c8c6d8c9e0e9` | `eceb5b35752ecec6d8c150ea813ae72f14db55ff` |
| `git rev-parse HEAD` == `git rev-parse main` tras crearla | **sí** | **sí** |
| `git rev-list --count main..HEAD` | **0** | **0** |
| ¿Nació alguna rama desde `dev`? | **NO** | **NO** |

`personal-blog-frontend` sigue en `main`, limpio y **sin rama Task**.

## C. Fuentes canónicas leídas

`CLAUDE.md` · `PROJECT_INSTRUCTIONS.md` · `WORKFLOW.md` · `STATUS.md` · `ROADMAP.md` ·
`DEFINITION_OF_DONE.md` · `TASK_TEMPLATE.md` · `BACKEND_TESTING_STRATEGY.md` ·
`STAGE-03-domain-and-backend.md` · `MVP_SCOPE.md` · `USER_FLOWS.md` · `CONTENT_MODEL.md` ·
`api-contracts.md` · `data-model.md` · `software-architecture.md` ·
`security-boundaries.md` · `non-functional-requirements.md` · `open-decisions.md` ·
ADR-003, ADR-004, ADR-005 · fichas y reportes de `Task/008`, `Task/009`, `Task/010` y
`Task/011`.

**Código:** `app/main.py`, los nueve módulos, `app/shared/*`, los modelos ORM, las
consultas existentes, las tres migraciones y el harness de pruebas completo
(`tests/conftest.py`, `tests/integration/conftest.py`, `tests/almacenamiento_de_pruebas.py`).

## D. Contrato administrativo

**23 rutas nuevas**, todas bajo `/api/v1/admin` y todas con sesión obligatoria. Tabla
completa —método, ruta, éxito, errores y auditoría— en la ficha §7.0.1 y, ya como contrato
vigente, en [`api-contracts.md`](../architecture/api-contracts.md) §14.

| Recurso | Operaciones | Auditoría |
| --- | --- | --- |
| `/admin/profile` | `GET`, `PUT` | `profile.updated` |
| `/admin/posts` | `GET`, `POST`, `GET/{id}`, `PUT/{id}`, `POST/{id}/{publish,unpublish,archive}` | `content.*` |
| `/admin/book-reviews` | Igual, **con `unpublish`** | `content.*` |
| `/admin/videos` | Igual, **sin `unpublish`** | `content.*` |
| `/admin/projects` | Igual, **sin `unpublish`** | `content.*` |
| `/admin/tags` | `GET`, `POST`, `PUT/{id}`, `DELETE/{id}` | `tag.*` |
| `/admin/media` | `GET`, `POST` (multipart), `DELETE/{id}` | `media.*` |

**Veinticuatro decisiones**, `D-012-A` a `D-012-X`, cada una con su fuente citada (ficha
§7.0.2). Ninguna sustituye ni modifica una decisión aprobada anterior, así que **no
requiere ADR**.

## E. Protección

| Comprobación | Resultado |
| --- | --- |
| Dependencia de `Task/011` reutilizada | **`requiere_administrador` / `AdministradorRequerido`**, sin copiar ni una línea de autenticación |
| ¿Se reimplementó algo de `Task/011`? | **No.** Se reutilizan además `exigir_origen_permitido`, `sin_cache`, `ContextoDeLaPeticion` y el `request_id` |
| `login` sigue siendo el único administrativo público | **Sí** — comprobado recorriendo OpenAPI |
| Prueba transversal | `test_todo_endpoint_administrativo_exige_sesion` recorre la especificación **entera** |

### E.1 La prueba transversal se verificó de verdad

No basta con que pase: hay que saber que **detecta**. Dos comprobaciones deliberadas:

| Experimento | Resultado | Qué demuestra |
| --- | --- | --- |
| Se retiró `Depends(requiere_administrador)` del router común | **35 pasan** | Correcto: los endpoints declaran además `AdministradorRequerido` en su firma, así que **siguen protegidos**. La prueba mide la protección real, no una forma concreta de declararla |
| Se retiró **también** el parámetro `AdministradorRequerido` de `listar_etiquetas` | **2 fallan** | Detecta el defecto que importa: un endpoint administrativo realmente desprotegido |

## F. Profile

| Aspecto | Resultado |
| --- | --- |
| Contrato | `GET` y `PUT` sobre `/admin/profile`. **Sin `POST` ni `DELETE`** |
| Singleton | Editar **no** crea un segundo perfil; comprobado contando filas |
| **No se crea por API** | `GET` y `PUT` sobre una base sin perfil responden `404` y **no dejan ninguna fila** (D-012-U, `data-model.md` §5) |
| Enlaces sociales | Reemplazo completo; el orden de presentación es **el índice del array** (D-012-Q), de modo que dos enlaces no pueden reclamar la misma posición |
| Validaciones | `full_name` obligatorio y no en blanco; clave desconocida en el cuerpo → `422`; `photo_id` desconocido → `422 unknown_reference` sin tocar el perfil |
| **Texto alternativo** | Una foto **sin `alt_text`** se rechaza con `422 media_without_alt_text`, sin tocar el perfil. El perfil no tiene `status`: asignar la foto **es** usarla (§C) |
| Tests | **20** propios, más los del texto alternativo (§C) |

## G. Post

| Operación | Resultado |
| --- | --- |
| `create` | Nace `draft`, sin fecha, `featured=false`. **Solo `title` es obligatorio** |
| `update` | `PUT` completo. **No cambia el estado**: editar un publicado no lo despublica (B.3) |
| `list` admin | Los **tres** estados, paginado, filtro `status`, orden `updated_at` desc con desempate por `slug` |
| `detail` | Por identificador interno; devuelve borradores; `404` si no existe; `422` si el identificador está malformado |
| `publish` | Fija `published_at` la primera vez; `409 cannot_publish_incomplete_draft` con `details.campos` si falta algo; `409 invalid_post_state` si ya está publicado |
| `unpublish` | Vuelve a `draft` **conservando** `published_at`; republicar **no** la reescribe |
| `archive` | Desde `draft` o `published`; conserva la fecha; repetirlo es `409` |
| `delete` | **No existe**: `405`. `MVP_SCOPE.md` §3.1 no concede *eliminar* al contenido |
| tags | Asociación y reemplazo exacto, sin duplicados; etiqueta desconocida → `422` y **ninguna fila creada** |
| cover | Portada desconocida → `422` y ninguna fila creada; portada válida devuelve `access_url` y **nunca** `object_key` |
| Tests | **60** de integración |

## H. BookReview

Todo lo del artículo, más lo suyo: `book_title`, `book_author` y `rating` **obligatorios
al publicar** (`CONTENT_MODEL.md` §3.3, D-D); escala **1..5** validada por el objeto de
valor `Rating` de `Task/008` —no por un rango repetido aquí—; `external_link` opcional
también al publicar; **sí** admite `unpublish`. **28** tests.

## I. Video

**No tiene `content`**: enviarlo es `422`, y el esquema de respuesta tampoco lo declara.
`video_url` y `provider` son **obligatorios al publicar** —el equivalente del *contenido*
para un tipo sin Markdown—; del proveedor solo se exige que **exista**, porque la lista
cerrada es de `Task/014`. Su imagen es `thumbnail`, no `cover`. **La ruta `/unpublish` no
existe**: responde `404`, y OpenAPI tampoco la anuncia. **19** tests.

## J. Project

`project_status` y `status` son campos distintos y no se mezclan: un proyecto
`completed` puede estar `published`. `technologies` es una lista ordenada en `JSONB`, que
se **reemplaza asignando una lista nueva** —SQLAlchemy no detecta mutaciones en sitio
(deuda 8 de `data-model.md`)—, con sus entradas validadas. `repository_url` y `demo_url`
no impiden publicar. **Sin `unpublish`**. **23** tests.

## K. Tag

| Aspecto | Resultado |
| --- | --- |
| create | Slug derivado del nombre o explícito; duplicado → `409` |
| update | Renombra `name` y `description`. **El `slug` no es un campo del cuerpo** (D-012-S): aparece en las URL de filtro públicas (A.9) |
| delete | `204`. Elimina la etiqueta y **desasocia** el contenido; el contenido **no se borra** (`CASCADE` sobre la tabla puente, D-J) |
| list | Incluye las etiquetas **sin** contenido publicado, al revés que `GET /api/v1/tags` |
| Confirmación previa | Es un paso de **interfaz** (`Task/015`), no un parámetro de la API (D-012-T). La asimetría con los medios está en las propias fuentes: B.5 obliga a **rechazar**, B.11 a **desasociar** |
| Tests | **18** |

## L. Media

| Aspecto | Resultado |
| --- | --- |
| upload | `POST` multipart. Delega en `SubirImagen` de `Task/010`: validación por **decodificación**, miniatura, clave no predecible y compensación |
| delete | Delega en `EliminarMedio`. Medio en uso → `409 media_in_use` con `details.usos` (tipo, `slug`, título) |
| in use | Comprobado desde un artículo **y** desde el perfil: dos de los cinco orígenes que enumera `Task/010` |
| `ObjectStorage` reuse | **Total.** El router no toca Pillow, boto3, MinIO ni SQLAlchemy |
| compensación | No se reimplementa: es la de `Task/010`, y su suite sigue verde |
| `access_url` | Presente y consumible; `object_key` **no sale** en ninguna respuesta ni en la auditoría |
| Persistencia | Comprobado sobre la columna real: `object_key` empieza por `medios/`, sin firma ni `http` |
| Tests | **19**, contra PostgreSQL **y MinIO** reales |

## M. Lifecycle

| Tipo | `draft → published` | `published → draft` | `→ archived` | `archived → *` |
| --- | :---: | :---: | :---: | :---: |
| `Post` | ✔ | ✔ | ✔ | no existe |
| `BookReview` | ✔ | ✔ | ✔ | no existe |
| `Video` | ✔ | **ruta inexistente** | ✔ | no existe |
| `Project` | ✔ | **ruta inexistente** | ✔ | no existe |

`published_at`: se fija en la **primera** publicación, se conserva al despublicar y al
archivar, y **no se reescribe** al republicar. Comprobado por prueba en los cuatro tipos.

**Las transiciones no son idempotentes: repetirlas es `409`.** No lo decide esta tarea —el
dominio aprobado en `Task/008` ya lanzaba— y hacerlas idempotentes habría exigido modificar
dominio aprobado.

## N. Validación de publicación

Tabla completa por entidad y campo en la ficha §7.0.3 y en `api-contracts.md` §14.5.
Resumen:

| Tipo | Exige |
| --- | --- |
| Los cuatro | `title`, `slug` y una descripción SEO **resoluble** (`seo_description` **o** `summary`) |
| `Post`, `BookReview`, `Project` | `content` no vacío |
| `BookReview` | además `book_title`, `book_author`, `rating` |
| `Video` | `video_url` y `provider` |

*«SEO si corresponde»* (B.7) **no** significa exigir los campos SEO: contradiría los
*fallbacks* de `CONTENT_MODEL.md` §2. Significa que la descripción se pueda **resolver**.

## O. Slugs

| Aspecto | Resultado |
| --- | --- |
| creación | Opcional: si falta, **se deriva del título** (B.2). NFKD, minúsculas, colapso en guiones, recorte por separador a 160 |
| edición | Permitida **mientras `published_at` sea nulo**; después, `409 slug_is_immutable` (D-012-F) |
| conflicto | `409 slug_already_exists`, por tipo |
| estabilidad | Un título del que no sale ningún carácter útil produce `422`: **no se inventa** la identidad pública de un contenido |
| etiquetas | Su slug es **inmutable** desde la creación (D-012-S) |

## P. Auditoría

| Aspecto | Resultado |
| --- | --- |
| Acciones | **Once** nuevas, cada una con un productor real: `content.{created,updated,published,unpublished,archived}`, `profile.updated`, `tag.{created,updated,deleted}`, `media.{uploaded,deleted}` |
| Tipo del elemento | Lo dice **`entity_type`**, no el nombre de la acción (D-012-N) |
| Metadatos | Mínimos: el `slug`; los dos estados en una transición; el `original_filename` en medios; **nada** en el perfil |
| Nunca se guarda | Markdown, contraseñas, credenciales, cookies, cabeceras ni claves de objeto — comprobado por prueba |
| `request_id` e IP | Los de `Task/011`. **No hay un segundo mecanismo** |
| Operaciones rechazadas | **No dejan evento**: el historial registra lo que pasó, no lo que se intentó |
| Inmutabilidad | Intacta. **No existe ninguna ruta `/admin/audit`**, y una prueba lo exige recorriendo OpenAPI |
| Borrado de etiqueta | El evento se escribe **antes** de borrar, para que el historial conserve el `slug`; sobrevive a la fila borrada (§6.1 de `data-model.md`) |

## Q. PostgreSQL

| Comprobación | Resultado |
| --- | --- |
| Base de datos | `personal_blog_test` |
| Guarda *fail-closed* | Activa: sufijo `_test` **y** marca `personal-blog:test-database` |
| SQLite | **No se usó** en ninguna forma |
| `personal_blog` tocada | **No.** No se creó ningún administrador ni perfil en ella |
| MinIO | Bucket efímero con prefijo de pruebas, creado y borrado por el harness de `Task/010` |

## R. Migraciones

| Comprobación | Resultado |
| --- | --- |
| ¿Cambia el esquema? | **No** |
| Revisión nueva | **Ninguna** |
| `0001`, `0002`, `0003` | **Intactas** (`git status alembic/` vacío) |
| `alembic heads` | **`0003 (head)`** |
| Ciclo `upgrade`/`downgrade`/re-`upgrade` y `compare_metadata` | Siguen verdes: los ejecuta la suite de integración heredada, sin cambios |

Ninguna necesidad de esquema apareció durante la tarea. Todo lo que `Task/012` necesita
—estado, fechas, claves foráneas, tablas puente, auditoría— ya existía desde `Task/008` y
`Task/011`, que es exactamente lo que aquellas tareas se propusieron dejar listo.

## S. TDD por *slice*

**12 *slices* totales: `SLICE 0` contract-first + 11 *slices* de implementación y
validación.** `SLICE 0` no produce RED porque **no escribe código productivo**: es el
contrato, y su entregable es la ficha §7.0. Los **once** restantes sí registran su RED con
su motivo textual.

**Un test que pasó al escribirse se clasifica como regresión, nunca como evidencia RED.**

| # | *Slice* | RED (motivo exacto) | GREEN | Refactor |
| --- | --- | --- | --- | --- |
| **0** | Contrato administrativo (ficha §7.0) | *No aplica*: sin código productivo | — | — |
| **1** | `slug` | `ModuleNotFoundError: app.shared.slug` | 32 ✔ | No necesario |
| **2** | Validación de publicación ×4 | `ModuleNotFoundError: …book_reviews.domain.publicacion` | 23 ✔ | No necesario |
| **3** | Catálogo de auditoría y puerto del historial | `ImportError: ENTIDAD_ETIQUETA` + 1 fallo: el puerto no estaba en `audit` | 5 ✔ | `RegistroDeAuditoria`, `ContextoDeAuditoria` y el reloj **mudados a su dueño**, con reexportación desde `authentication` |
| **4** | Perfil | **15 fallos**: `404`, las rutas no existían | 20 ✔ | Los enlaces se vacían y se confirman antes de insertar (§T.1) |
| **5** | Artículos | **55 fallos**: `404` | 60 ✔ | `status` pasó a alias del parámetro `status_filtro` (§T.2) |
| **6** | Reviews | **27 fallos**: `404` | 28 ✔ | No necesario |
| **7** | Vídeos | **19 fallos**: `404` | 19 ✔ | No necesario |
| **8** | Proyectos | **18 fallos**: `404` | 23 ✔ | No necesario |
| **9** | Etiquetas | **15 fallos**: `404` | 18 ✔ | No necesario |
| **10** | Medios | **18 fallos**: `404` | 19 ✔ | Prueba de orden reescrita por inestable (§T.3) |
| **11** | OpenAPI y regresión | **8 fallos** en pruebas de `Task/005`, `Task/009` y `Task/011` | Suite completa ✔ | — |

### S.1 Tests que **pasaron al escribirse** — regresión, no RED

Se enumeran uno a uno porque la honestidad del ciclo depende de ello.

| Prueba | Por qué pasó al escribirse |
| --- | --- |
| `test_la_respuesta_administrativa_no_expone_campos_internos` (perfil) | Un cuerpo de `404` tampoco lleva esos campos. Pasaba **por el motivo equivocado** |
| `test_editar_el_perfil_no_crea_un_segundo` | Un `404` no crea nada |
| `test_sin_perfil_la_consulta_responde_404` · `test_sin_perfil_la_edicion_responde_404_y_no_crea_ninguno` | El `404` de ruta inexistente coincide con el `404` del recurso. Solo miden algo desde que la ruta existe |
| `test_una_edicion_rechazada_no_deja_evento` (perfil) | Un `404` no deja evento |
| `test_el_conflicto_de_slug_no_deja_ningun_articulo_a_medias` · `test_editar_un_articulo_inexistente_responde_404` · `test_un_identificador_desconocido_responde_404` (artículos) | Mismo motivo: `404` de ruta |
| `test_una_review_desconocida_responde_404` · `test_un_proyecto_desconocido_responde_404` · `test_eliminar_un_medio_inexistente_responde_404` · `test_renombrar_una_etiqueta_inexistente_responde_404` · `test_eliminar_una_etiqueta_inexistente_responde_404` | Mismo motivo |
| **Las 35 de `test_contrato_administrativo.py`** | El *slice* 11 se escribió **después** de los diez anteriores: sus routers ya existían. Es una suite de **regresión de contrato**, y así se declara. Su capacidad de detección se verificó aparte (§E.1) |
| `test_dos_publicaciones_simultaneas_solo_prosperan_una` | El cerrojo se implementó en el *slice* 5. Su capacidad de detección se verificó retirándolo (§S.2) |
| Las **89** añadidas al cerrar cobertura (§W) | Cubren ramas de código ya escrito. Son regresión por definición |

### S.2 Guardas anti-tautología ejecutadas

Dos pruebas afirman algo que sería fácil creer sin comprobar. Se comprobó.

| Prueba | Experimento | Resultado |
| --- | --- | --- |
| `test_dos_publicaciones_simultaneas_solo_prosperan_una` | Se retiró `with_for_update()` del repositorio | **Falla**: las dos publicaciones responden `200`. Con el cerrojo, `200` y `409` |
| `test_todo_endpoint_administrativo_exige_sesion` | Se dejó un endpoint sin `AdministradorRequerido` | **Falla**, nombrando el endpoint. Ver §E.1 |

**No se usó mutation testing en ninguna forma**, ni como evidencia ni como sustituto.

## T. Defectos encontrados

Ninguno se corrigió en silencio.

### T.1 · Reemplazar los enlaces sociales violaba su restricción única

`PUT /admin/profile` con enlaces nuevos fallaba con `UniqueViolation` sobre
`uq_profile_social_links_profile_id_display_order`. **Causa:** la unidad de trabajo de
SQLAlchemy emite los `INSERT` de una colección **antes** que los `DELETE` de sus
huérfanos, así que el enlace nuevo con `display_order = 0` chocaba con el antiguo, que
todavía lo ocupaba.

**Corrección:** vaciar la colección y **confirmar ese vaciado** antes de insertar.
**Regresión:** `test_los_enlaces_sociales_se_reemplazan_por_completo`, que es la prueba
que lo encontró. Ningún doble lo habría mostrado: hacía falta la restricción real.

### T.2 · El filtro se llamaba `status_filtro` en la URL

El parámetro de Python no puede llamarse `status` en un archivo que importa
`fastapi.status`, y FastAPI usa el nombre del parámetro como nombre del parámetro de
consulta. El contrato exige `status` (`api-contracts.md` §6).

**Corrección:** `Query(alias="status")`. **Regresión:**
`test_el_listado_administrativo_filtra_por_estado` y la comprobación de OpenAPI que exige
que **solo** los cuatro listados administrativos declaren `status`.

### T.3 · Una prueba propia era inestable, no el código

`test_el_listado_de_medios_va_del_mas_reciente_al_mas_antiguo` subía dos imágenes seguidas
y afirmaba su orden. **`created_at` lo pone `now()` de PostgreSQL, que es la hora de inicio
de la transacción**: las dos cargas de una misma prueba comparten marca, y el resultado lo
decidía el desempate por `object_key`, que es azar.

**Se detectó ejecutándola seis veces antes de darla por buena: falló 4 de 6.** La prueba se
reescribió con fechas fijadas a mano —el `medio()` del harness gana un parámetro
`cargado_el`— y volvió a ejecutarse cinco veces seguidas en verde. La expectativa **no
cambió**; cambió el escenario, que era incapaz de distinguir nada.

Se aplicó el mismo criterio a la prueba de orden del listado administrativo de artículos,
que depende de `updated_at` por la misma razón.

### T.4 · Drift documental preexistente, corregido de paso

| Documento | Qué decía | Corrección |
| --- | --- | --- |
| `STATUS.md`, tabla completa de tareas | `Task/010` figuraba como **Pendiente** | **Aprobada**, como dice el resto del mismo documento |
| `README.md` del backend | *«fundación implementada, sin funcionalidad de negocio»* — cierto en `Task/005`, falso desde `Task/008` | Encabezado actualizado, con nota de la corrección |

## U. OpenAPI

| Comprobación | Resultado |
| --- | --- |
| Rutas públicas | **11** (10 del contrato + `/health`), **intactas** |
| Rutas de autenticación | **3**, intactas |
| Rutas administrativas nuevas | **23** |
| Endpoints administrativos **sin** autenticación | **0**, salvo `login` (que debe serlo) |
| Rutas públicas que declaran seguridad | **0** |
| Métodos distintos de `GET` fuera de `/admin` | **0** |
| Rutas de tareas futuras (`/ready`, auditoría, `Task/013`+) | **0** |
| Esquema de seguridad | `sesionAdministrativa`, `apiKey` en cookie `blog_admin_session` — el real |

Verificado además **contra el contenedor recreado**: 26 rutas administrativas, una sola sin
seguridad (`POST /admin/auth/login`), 11 públicas.

## V. Regresión

| Tarea | Resultado |
| --- | --- |
| **`Task/009`** | Verde. Los diez endpoints públicos, su contrato, su paginación y sus filtros. Añadido: tras publicar, el contenido **aparece** en la API pública; tras despublicar o archivar, vuelve a `404` indistinguible de inexistente |
| **`Task/010`** | Verde. Contrato de `ObjectStorage` (13 casos × 2 implementaciones), `access_url`, comprobación de uso y compensación. **No se reimplementó ninguna de sus pruebas** |
| **`Task/011`** | Verde. Login, logout, `/me`, bloqueo, límite de tasa, política de cookie y CSRF. Añadido: **todos** los endpoints nuevos rechazan el acceso sin sesión |
| **`Task/008`** | Verde. Inmutabilidad de `AuditEvent`, migraciones y esquema físico |

### V.1 Pruebas previas actualizadas — y por qué

Ocho pruebas afirmaban que el CRUD administrativo **no existía todavía**. Es el supuesto 1
de `BACKEND_TESTING_STRATEGY.md` §9 —**el requisito cambió**—, y las ocho lo anotaban por
escrito. Ninguna se relajó: se **estrecharon** al alcance del que su afirmación sigue
siendo cierta.

| Prueba | Antes | Ahora |
| --- | --- | --- |
| `test_openapi_no_declara_endpoints_no_implementados` | Las administrativas eran exactamente las 3 de acceso | `/ready` no existe y **la auditoría no se expone** |
| `test_la_especificacion_declara_exactamente_las_rutas_del_contrato` | Todas las rutas | Las **públicas**; el conjunto administrativo se comprueba, igual de cerrado, en su propio módulo |
| `test_lo_unico_administrativo_declarado_es_la_autenticacion` | Solo existía `/admin/auth` | Renombrada: `/admin/auth` sigue siendo **esas tres**, sin `register` ni `reset-password` |
| `test_la_api_publica_es_de_solo_lectura` | Excluía tres rutas por nombre | Excluye por **prefijo** |
| `test_ningun_endpoint_declara_el_parametro_status` | Recorría todo | Recorre lo **público**; que los administrativos sean exactamente cuatro se comprueba aparte |
| `test_la_especificacion_declara_los_tres_endpoints_de_autenticacion` | Comparaba con **todas** las administrativas | Compara con el subárbol `/admin/auth` |
| `test_no_se_declara_ningun_crud_administrativo` | Exigía que **no** existiera | Renombrada: los siete recursos existen **y exigen sesión** |
| `test_el_catalogo_de_acciones_de_autenticacion_tiene_cuatro_entradas` | Miraba la enumeración entera | Mira las de prefijo `authentication.` |

**Ninguna se modificó para acomodar una implementación incorrecta** (criterio B-12).

## W. Dependencias

**Una nueva:** `python-multipart==0.0.32`.

| Campo | Valor |
| --- | --- |
| Propósito | Analizar `multipart/form-data`. **FastAPI la exige** para declarar `UploadFile`: sin ella, la ruta de carga no puede definirse |
| Alternativa evaluada | Recibir el cuerpo **crudo** con el nombre del archivo en un parámetro de consulta. **Descartada**: `original_filename` es `NOT NULL` y acabaría en la URL —y por tanto en los logs de acceso—, y el `alt_text` viajaría por el mismo sitio |
| Impacto en Lambda | **Mínimo.** Rueda `py3-none-any` —Python puro, sin extensión compilada—, ~164 KB, **sin dependencias transitivas** (P-07). Verificado descargando la rueda |
| Registrada en | `pyproject.toml` y `requirements.txt`, con su justificación |

**No** se añadió ningún *framework* de administración, CMS, GraphQL, CQRS, bus de eventos,
Redis ni Celery.

## X. Quality gates

Todos ejecutados con los comandos reales del repositorio.

| Puerta | Comando | Resultado |
| --- | --- | --- |
| Lint | `ruff check .` | **All checks passed** |
| Formato | `ruff format --check .` | **272 files already formatted** |
| Tipos | `mypy .` | **Success: no issues found in 274 source files** |
| Unitarias | `pytest tests/unit -q` | **417 passed** |
| Contrato | `pytest tests/contract -q` | **270 passed** |
| Integración | `pytest -m integration -q` | **703 passed** |
| Suite completa | `pytest -q -W error` | **1466 passed, 1 skipped** |
| Advertencias | `-W error` | **0** |
| Cobertura | `pytest --cov -q` | **`app/` al 100 %** (4357 sentencias, 446 ramas, 0 sin cubrir) |
| Dependencias | `pip check` | **No broken requirements found** |
| Espacios | `git diff --check` | limpio |
| Migraciones | `alembic heads` | **`0003 (head)`** |

La única omisión es `time.tzset`, que **no existe en Windows** y es preexistente desde
`Task/005`.

### X.1 Cobertura: cómo se llegó al 100 %

La primera medición dio **97 %**. No se ajustó el umbral: se cerraron los huecos, que eran
reales.

| Hueco | Corrección |
| --- | --- |
| Cuerpos de `Protocol` escritos en una línea (`def f(...) -> T: ...`) | La exclusión de cobertura del proyecto reconoce `...` **en su propia línea**. Se normalizaron a la forma que ya usaba `posts`, con su docstring |
| Ramas de validación de publicación no probadas en tres de los cuatro tipos | Tabla parametrizada que recorre **los cuatro**: cada tipo tiene su propia función, así que *"funciona en artículos"* no dice nada de los demás |
| Detalle, filtro de estado, estabilidad del slug, etiquetas y portada, probados solo en artículos | Nuevo módulo `test_api_admin_contenido_comun.py`, que recorre los cuatro con la misma tabla |
| Recorte de slug sin separador; tecnologías en blanco o desmesuradas; renombrar una etiqueta con nombre en blanco | Casos explícitos |

## Y. Docker y host

| Comprobación | Resultado |
| --- | --- |
| ¿Se recreó Docker? | **Solo el servicio `backend`**, y con motivo: la dependencia nueva es necesaria **al definir la ruta**, así que sin ella el contenedor no arranca |
| Comandos ejecutados | `docker compose build backend`, `docker compose up -d backend` |
| `down` / `down -v` / `prune` | **No.** Ninguno, en ninguna forma |
| ¿Se recreó PostgreSQL? | **No** |
| ¿Se recreó MinIO? | **No** |
| Puertos | Sin cambios |
| WinNAT / WSL / Windows | **No se tocó nada** |
| Estado tras la recreación | `personal-blog-local-backend` **Up (healthy)**; 26 rutas administrativas, una sola pública |

## Z. Documentación

| Documento | Qué cambió |
| --- | --- |
| `docs/tasks/TASK-012-administrative-api.md` | **Creada**: contrato completo, 23 decisiones, matriz de casos y plan test-first |
| `docs/task-reports/TASK-012-report.md` | **Creado**: este reporte |
| `docs/project-management/STATUS.md` | Tarea en curso, defectos, deuda; tabla de tareas. **El avance no sube** |
| `docs/project-management/ROADMAP.md` | `Task/012` pasa a *Lista para validación*; el avance global sigue en 11 de 41 |
| `docs/stages/STAGE-03-domain-and-backend.md` | Estado de la tarea. **La etapa sigue en 4 de 5** |
| `docs/architecture/api-contracts.md` | **§14 nueva**: contrato administrativo cerrado. §4 y §11 dejan de declararlo abierto |
| `docs/architecture/data-model.md` | Invariantes **8**, **12**, **17** y **18** cerradas; deuda 7 resuelta; §5 confirmada |
| `docs/architecture/software-architecture.md` | **§3.10 nueva**: dónde vive cada pieza, las dos mudanzas, el límite transaccional y la dependencia nueva |
| `docs/architecture/security-boundaries.md` | **§12 nueva**: trece reglas explícitas y lo que **no** se afirma |
| `docs/product/CONTENT_MODEL.md` | §3.3 y §3.9: valoración exigida al publicar y catálogo de auditoría cerrado |
| `docs/product/USER_FLOWS.md` | B.1 y B.7 dejan de remitir a una decisión pendiente |
| `personal-blog-backend/README.md` | Encabezado y estructura de módulos actualizados |

**No se tocó** ningún documento que no cambiara: ADR, runbooks, `DEFINITION_OF_DONE.md`,
`WORKFLOW.md`, `BACKEND_TESTING_STRATEGY.md`, `MVP_SCOPE.md`, `open-decisions.md` —
`Task/012` no resuelve ninguna decisión `D-xx` del registro global— ni las fichas de tareas
anteriores.

## AA. Criterio 12 — estado transitorio

Búsqueda dirigida en los documentos tocados.

| Clase | Cuántas | Ejemplo |
| --- | --- | --- |
| **A. Historia fechada** | Varias | *«Verificado el 2026-09-01: 26 rutas administrativas en el contenedor recreado»* |
| **B. Regla permanente** | Varias | *«La siguiente Task nace de `main` actualizado tras la normalización»* |
| **C. Estado operativo vivo** | **0** | — |

**C = 0.** Ningún documento afirma que exista un PR, que una rama remota esté viva, ni
condiciona nada a una fusión pendiente. El estado de la tarea —*Lista para validación*— es
**duradero**: describe el trabajo, no el trámite.

## AB. Gobierno

| Campo | Valor |
| --- | --- |
| `Task/012-API-Administrativa` | **Lista para validación** |
| Avance global | **11 / 41 — 27 %** (sin cambios) |
| ETAPA 03 | **4 / 5 — 80 %** (sin cambios) |

## AC. Evaluación de los criterios de salida de la ETAPA 03

**Evaluación técnica, no marcado.** La etapa no se cierra hasta que el usuario apruebe.

| # | Criterio | ¿Cumplido técnicamente? | Evidencia |
| --- | --- | :---: | --- |
| 1 | El esquema cubre todas las secciones del blog previstas en el MVP | **SÍ** | 16 tablas (`data-model.md` §2). `Task/012` no necesitó ninguna columna nueva, que es la comprobación más fuerte de que el esquema estaba completo |
| 2 | Las migraciones aplican sobre base vacía y revierten | **SÍ** | `upgrade head` → `downgrade base` → `upgrade head` y `compare_metadata`, en la suite de integración |
| 3 | La API pública nunca expone borradores ni archivado | **SÍ** | `Task/009`, y reverificado de extremo a extremo tras publicar, despublicar y archivar desde el panel |
| 4 | Las imágenes se suben y recuperan desde MinIO por `ObjectStorage` | **SÍ** | `Task/010`, y ahora también por HTTP desde `/admin/media` |
| 5 | `MinIOStorage` y `S3Storage` superan las mismas pruebas de contrato | **SÍ** | `Task/010`, suite intacta |
| 6 | Nada persiste una URL prefirmada | **SÍ** | `Task/010` para la base; **`Task/012` cierra la otra mitad**: el Markdown del contenido viaja y se guarda como fuente, y ninguna respuesta administrativa persiste un enlace |
| 7 | **D-15** resuelta | **SÍ** | `Task/011` |
| 8 | Ningún endpoint administrativo es accesible sin autenticación | **SÍ** | Prueba transversal sobre OpenAPI, con su capacidad de detección verificada (§E.1) |
| 9 | Las acciones administrativas quedan registradas en auditoría | **SÍ** | Once acciones nuevas, con productor real y sin secretos |
| 10 | Cobertura de pruebas en dominio y endpoints críticos | **SÍ** | `app/` al **100 %**, 1418 pruebas |
| 11 | Cada tarea demuestra su ciclo test-first | **SÍ** | Las cinco tareas conservan matriz, RED y GREEN en su reporte |

**Los once criterios se cumplen técnicamente.** Marcar la etapa como completada requiere la
aprobación del usuario.

## AD. Estado de Git al cerrar

| Repositorio | Rama | *Staging* | Commits sobre `main` | Push | Merge | PR |
| --- | --- | :---: | :---: | :---: | :---: | :---: |
| `personal-blog-backend` | `Task/012-API-Administrativa` | **0** | **0** | **0** | **0** | **0** |
| `personal-blog-infra` | `Task/012-API-Administrativa` | **0** | **0** | **0** | **0** | **0** |
| `personal-blog-frontend` | `main`, limpio | — | — | **0** | **0** | **0** |

76 archivos modificados o nuevos en backend y 11 en infra, **todos sin confirmar**.

## AE. Veredicto

| Pregunta | Respuesta |
| --- | --- |
| ¿Contrato administrativo completo y derivado de fuentes canónicas? | **SÍ** |
| ¿Todos los endpoints administrativos protegidos? | **SÍ** |
| ¿`login` sigue siendo el único administrativo público? | **SÍ** |
| ¿API pública intacta y anónima? | **SÍ** |
| ¿Lifecycle correcto en los cuatro tipos? | **SÍ** |
| ¿Validación de publicación correcta? | **SÍ** |
| ¿Medios reutilizan `Task/010` sin duplicarla? | **SÍ** |
| ¿Auditoría correcta e inmutable? | **SÍ** |
| ¿PostgreSQL real? | **SÍ** |
| ¿TDD real, con RED honesto? | **SÍ** |
| ¿Suite verde? | **SÍ** — 1466 pasan, 1 omitida |
| ¿Advertencias 0? | **SÍ** |
| ¿Cobertura conforme al estándar? | **SÍ** — 100 % |
| ¿Criterion 12 con C = 0? | **SÍ** |
| ¿Frontend intacto? | **SÍ** |
| ¿0 commits, push, merge y PR? | **SÍ** |
| ¿Criterios técnicos de la ETAPA 03 evaluados? | **SÍ** — los once, §AC |
| **¿`Task/012` lista para validación?** | **SÍ** |

**No se aprueba, no se hace commit, no se hace push, no se crea PR y no se inicia
`Task/013`.**

---

# Revisión correctiva final (2026-09-01)

Tres puntos, resueltos con diagnóstico previo. **Dos** exigieron cambio productivo.

## AF. Conteo de *slices*

| | |
| --- | --- |
| Texto anterior | *«Once slices»*, en el reporte §S y en la fila *Test-first* de `STATUS.md` |
| Conteo real | **12 totales**: `SLICE 0` contract-first + `SLICE 1`…`SLICE 11` |
| Texto corregido | *«12 slices totales: `SLICE 0` contract-first —sin código productivo, y por tanto sin RED— más 11 de implementación y validación»* |
| Archivos corregidos | `docs/task-reports/TASK-012-report.md`, `docs/project-management/STATUS.md` |

**La historia TDD no se toca.** `SLICE 0` sigue diciendo *«No aplica: sin código
productivo»*, que es lo correcto: no se le inventa un RED.

## AG. `alt_text` — fuentes **anteriores** a `Task/012`

Leídas con `git show main:<archivo>`, **no** del árbol de trabajo: `Task/012` ya había
modificado varios de esos documentos y justificarse con texto propio no habría probado nada.

| Archivo | Sección | Texto relevante | Qué establece |
| --- | --- | --- | --- |
| `data-model.md` | §4.1, tabla `media_assets`, fila `alt_text` | *«accesibilidad (A-04). **`Task/010` decidió no exigirlo al subir** (D-010-N): se escribe al **usar** la imagen, no al cargarla, y el flujo B.4 no lo pide. **Exigirlo donde se usa es de `Task/012` y `Task/014`**»* | **Asigna la exigencia a `Task/012`**, por nombre |
| `docs/tasks/TASK-010-…md` | §12, decisión **D-010-N** | *«`data-model.md` dice “se escribe al usar la imagen, no al subirla”. El flujo B.4 no lo pide y **B.5 asocia después**. **La accesibilidad se garantiza donde se usa el medio (`Task/012`, `Task/014`)**, no en el almacén»* | Lo mismo, y añade que **la asociación es posterior a la carga** |
| `docs/task-reports/TASK-010-report.md` | §Q | *«Exigirlo aquí obligaría a inventar un texto alternativo antes de saber en qué contenido va a aparecer la imagen»* | Por qué **no** se exige al cargar |
| `CONTENT_MODEL.md` | §3.7 | *«`alt_text` — Texto alternativo, **necesario para accesibilidad**»* | Es obligatorio para el fin, no opcional como propiedad |
| `api-contracts.md` | §12 | *«`alt_text` — Texto alternativo (requisito A-04)»* | Es parte del contrato público de un medio |
| `api-contracts.md` | §4 | *«`/api/v1/admin/media` — Carga, listado y borrado controlado de imágenes»* | **Tres** operaciones: no hay actualización |
| `non-functional-requirements.md` | A-04 | *«Texto alternativo en imágenes; `alt_text` es parte de `MediaAsset`. — `Task/010`, `Task/014`»* | Propietarios del **requisito**: la columna y el render |
| `USER_FLOWS.md` | — | **No menciona `alt_text`** | No añade ni quita nada |

**`Task/018` no aparece asociado a `alt_text` en ninguna de las ocho fuentes.** Se comprobó
una por una.

## AH. `alt_text` — resolución

| | |
| --- | --- |
| **Caso** | **A** |
| ¿`Task/012` tenía una obligación pendiente? | **SÍ.** Dos fuentes anteriores le asignan por nombre *exigirlo donde se usa*, y la implementación no lo exigía en ningún sitio |
| ¿Se cambió código? | **SÍ** |
| Propietario final | **`Task/012`** (la exigencia en la API) y **`Task/014`** (el render), tal como estaba escrito desde el principio |

**El traslado a `Task/014`/`Task/018` no tenía base y se retira.** `Task/018` nunca fue
propietaria de esto; `Task/014` es **co-propietaria**, no sustituta. Escribirlo como deuda
ajena era mover un *owner* sin fuente.

### La contradicción aparente, y por qué no lo es

`non-functional-requirements.md` asigna A-04 a `Task/010` y `Task/014`, sin nombrar a
`Task/012`. No contradice a `data-model.md`: son dos afirmaciones distintas. Aquella tabla
reparte el **requisito** —quién pone la columna, quién pinta el `alt` en el HTML—; la fila
de `data-model.md` reparte la **exigencia**, que es un tercer trabajo y está asignado. Por
eso **no es un CASO C**: las fuentes se complementan.

### Qué significa exactamente «donde se usa», y por qué hay dos puntos

Una imagen se **usa** cuando un contenido la referencia **y ese contenido es visible**.
Los dos puntos los decide el modelo, no una preferencia:

| Dónde | Cuándo | Por qué |
| --- | --- | --- |
| Los cuatro publicables | al **publicar** | Un borrador no lo ve nadie. Y bloquear la **asociación** haría imposible el flujo que la propia D-010-N describe: *«B.5 asocia después»* |
| El **perfil** | al **editar** | No tiene `status`: *«siempre existe y siempre está visible»* (CONTENT_MODEL.md §2). No hay un «publicar» posterior donde exigirlo |

### Contrato final

| Operación | Comportamiento |
| --- | --- |
| `POST /admin/media` | `alt_text` **sigue siendo opcional** — **D-010-N** intacta |
| `POST`/`PUT` de contenido | Un borrador **sí** puede referenciar una imagen sin `alt_text` |
| `POST /{id}/publish` | `409 cannot_publish_incomplete_draft`, con `cover_alt_text` o `thumbnail_alt_text` en `details.campos` |
| `PUT /admin/profile` | `422 media_without_alt_text` con `details.campo = "photo_id"`, sin tocar el perfil |
| Un `alt` en blanco | Cuenta como ausente: para un lector de pantalla no describe nada |

### RED y GREEN

**RED:** `tests/integration/test_api_admin_texto_alternativo.py` — **10 fallos**, cuatro
tipos × (publicar sin texto, texto en blanco) más los dos del perfil. Las 15 restantes
—controles y casos permisivos— pasaron al escribirse y son **regresión**.

**GREEN:** 25 ✔, más **16** casos de dominio en
`tests/unit/test_validacion_de_publicacion.py`.

### Lo que queda abierto, **sin propietario inventado**

Una imagen cargada **sin** `alt_text` no puede ganarlo después: `/admin/media` tiene tres
operaciones y **ninguna fuente asigna a nadie** la capacidad de editarlo. El recorrido está
completo —se indica al cargar, o se borra la imagen y se vuelve a cargar— pero es incómodo.
Se declara **sin propietario** y se somete a revisión externa, en lugar de asignárselo a
`Task/014` o `Task/018` sin base.

## AI. Medios — frontera transaccional real

Trazado sobre el código, no por intuición.

### Carga

| Paso | Qué ocurre |
| --- | --- |
| `SubirImagen` (Task/010) | validar → `guardar(original)` → `guardar(miniatura)` → `repositorio.registrar()` |
| DB | `session.add` + **`flush`**. **Nunca `commit`** |
| Storage | Los dos objetos se escriben **antes** que la fila |
| Compensación | Solo ante excepciones **dentro** de `SubirImagen`: borra en orden inverso, *best effort* |
| Auditoría de `Task/012` | Después, en la misma sesión y transacción |

**Si la auditoría falla después:** la transacción de la petición revierte → **no queda
fila** y **no queda evento**; los dos objetos **permanecen** en MinIO.

**No es un defecto.** Es exactamente el estado que **D-010-P** acepta por escrito: *«un
objeto sin fila es basura que ocupa espacio, y una fila sin objeto es una imagen rota en el
blog publicado»*. La invariante que importa —nunca una fila sin objeto— **se mantiene**.

### Borrado

| Paso | Qué ocurre |
| --- | --- |
| `EliminarMedio` (Task/010) | `buscar` → `usos_de` → `repositorio.eliminar()` → `almacenamiento.eliminar(miniatura)` → `almacenamiento.eliminar(original)` |
| DB | `session.delete` + **`flush`**. **Nunca `commit`** |
| Storage | Los objetos se borran **después** de la fila, e irreversiblemente |
| Auditoría de `Task/012` | **Antes**, desde esta revisión |

**Si la auditoría fallaba después —comportamiento anterior:** la transacción revertía y
**la fila volvía**, mientras los objetos ya no estaban. Resultado: **una fila apuntando a
objetos inexistentes**, y un borrado irreversible **sin evento de auditoría**.

## AJ. Inyección de fallo

Prueba nueva: `tests/integration/test_fallo_de_auditoria_de_medios.py`. **No existía
ninguna equivalente**; se comprobó antes de escribirla.

Ejercita el **caso de uso**, no el endpoint, y modela la transacción de la petición con un
`SAVEPOINT` explícito. La razón está escrita en el módulo: el harness sustituye
`get_session` por la sesión de la prueba, así que **una petición fallida no revierte**;
probarlo por HTTP habría medido lo contrario de lo que ocurre en producción. PostgreSQL y
MinIO **reales**, bucket efímero del harness de `Task/010`. Sin AWS.

### A. Carga + fallo de auditoría

| | Resultado |
| --- | --- |
| RED / GREEN | **Verde desde el principio**: es un **control**, no evidencia RED |
| Estado de PostgreSQL | Sin fila |
| Original y miniatura | **Permanecen** — huérfanos aceptados por D-010-P |
| `AuditEvent` | Ninguno |
| Invariante *ninguna fila sin objeto* | **Se mantiene** |

### B. Borrado + fallo de auditoría

| | Resultado |
| --- | --- |
| RED | **2 fallos**, con el mensaje que los describe: *«la fila volvió con el rollback pero su objeto ya estaba borrado»* y *«el objeto se borró de forma irreversible aunque la operación no llegó a auditarse»* |
| GREEN | **7 ✔** tras la corrección |
| Estado de PostgreSQL | La fila sigue existiendo |
| Storage | Los objetos **siguen existiendo** |
| `AuditEvent` | Ninguno |

## AK. ¿Se encontró defecto?

**SÍ**, uno.

| | |
| --- | --- |
| **Causa** | La composición `Task/010 + auditoría` invertía la garantía de **D-010-P**. `EliminarMedio` borra la fila **con `flush`** y después los objetos; un fallo posterior de la auditoría revertía la fila y dejaba los objetos borrados |
| **Corrección** | **Auditar antes de borrar**, en `EliminarMedioAdministrativo` (decisión **D-012-X**) |
| **Por qué no toca `Task/010` indebidamente** | No se modifica su caso de uso, ni su orden interno, ni su compensación, ni se le inyecta `actor_id`, `request_id` ni IP. El cambio es **una reordenación de dos llamadas** en el envoltorio que introdujo `Task/012`: la frontera de composición más pequeña posible |
| **Precedente** | Es el mismo orden, y por la misma razón, que `EliminarEtiqueta` ya usaba |

### Consecuencia declarada

Con el orden nuevo, un borrado **rechazado** llega a escribir el evento y la transacción lo
deshace. La garantía —*el historial registra lo que pasó, no lo que se intentó*— se
mantiene, pero conviene decir de qué depende: de la **transacción de la petición**, que es
la unidad de atomicidad de **D-012-V** y de la que ya dependían todas las demás operaciones
administrativas. Está fijado por prueba con la transacción modelada.

## AL. Regresión de esta revisión

| Suite | Resultado |
| --- | --- |
| `Task/010` — medios y almacenamiento | **107 ✔** |
| `Task/011` — autenticación y auditoría | **108 ✔** |
| `Task/012` — medios, perfil y fallo de auditoría | **44 ✔** más los nuevos |
| Suite completa | **1466 pasan, 1 omitida**, **0 advertencias** con `-W error` |
| Cobertura | **100 %** (4357 sentencias, 446 ramas) |

**El conteo anterior (1418) queda superado: +48 pruebas.** 25 del texto alternativo, 16 de
dominio y 7 de inyección de fallo.

### Una prueba previa se reformuló, y no para acomodar el código

`test_un_borrado_rechazado_no_deja_evento` medía la sesión **sin** modelar el rollback de la
petición, así que con el orden nuevo veía el evento aún sin confirmar. La expectativa no se
relajó: se **desdobló**, y la cobertura resultante es más fuerte que la anterior.

| Dónde | Qué afirma |
| --- | --- |
| `test_api_admin_medios.py` (HTTP) | `409`, la fila sigue ahí y **no se borró nada** |
| `test_fallo_de_auditoria_de_medios.py` (transacción modelada) | Del intento **no queda evento durable** |

## AM. Puertas de calidad de esta revisión

Hubo cambio productivo, así que se ejecutaron **completas, una sola vez** al final.

| Puerta | Resultado |
| --- | --- |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 278 files already formatted |
| `mypy .` | Success: no issues found in 276 source files |
| `pytest --cov -q -W error` | **1466 passed, 1 skipped**, 0 advertencias, **100 %** |
| `pip check` | No broken requirements found |
| `git diff --check` | limpio |
| `alembic heads` | **`0003 (head)`** — sin migración nueva; `0001`–`0003` intactas |

**Docker no se tocó en esta revisión.** Ni `build`, ni `up`, ni `down`, ni `prune`. Ningún
cambio afecta a la imagen: no hay dependencias nuevas.

## AN. Gobierno tras la revisión

Sin cambios: `Task/012` sigue **Lista para validación**, el avance sigue en **11 / 41
(27 %)** y la ETAPA 03 en **4 / 5 (80 %)**. Cero commits, cero push, cero merge, cero PR.

---

# Corrección final de `alt_text` (2026-09-01)

Un único bloqueador, cerrado. La revisión anterior corrigió **a quién** pertenece la
obligación; esta corrige **qué** obligación era.

## AO. Fuente canónica y por qué el comportamiento anterior seguía incompleto

**Texto PRE-TASK012**, `data-model.md` §4.1 y **D-010-N** de `Task/010`:

> *«se escribe al **usar** la imagen, no al cargarla»* · *«exigirlo donde se usa es de
> `Task/012` y `Task/014`»* · *«B.5 asocia **después**»*

**Interpretación.** La frase contiene **dos** obligaciones, no una: *escribir* y *exigir*.
La revisión anterior cerró la segunda y dejó la primera sin tocar.

**Por qué eso todavía era incompleto.** Con la carga como único momento posible de
escritura, el administrador tenía que **anticipar** el texto al subir el archivo, sin saber
aún en qué contenido iba a aparecer la imagen. Es exactamente lo que `Task/010` rechazó al
tomar D-010-N —*«obligaría a inventar un texto alternativo antes de saber en qué contenido
va a aparecer»*—, así que el resultado contradecía la fuente que decía cumplir. Y el único
recorrido de salida documentado, *borrar y volver a cargar*, era la prueba de que la frase
no se estaba cumpliendo.

## AP. Contrato *set-on-first-use* (D-012-Y)

**No se añade ninguna operación a `/admin/media`**: conserva carga, listado y borrado. Lo
que gana un campo es el cuerpo de quien **usa** la imagen.

| Recurso | Campo | Acompaña a |
| --- | --- | --- |
| `/admin/posts`, `/admin/book-reviews`, `/admin/projects` | `cover_alt_text` | `cover_id` |
| `/admin/videos` | `thumbnail_alt_text` | `thumbnail_id` |
| `/admin/profile` | `photo_alt_text` | `photo_id` |

| Imagen | Cuerpo | Resultado |
| --- | --- | --- |
| sin texto | con texto | **Se escribe** en `media_assets`, misma transacción que la referencia |
| sin texto | sin texto | Borrador: permitido. Publicar o perfil: rechazado (§14.5) |
| con texto | sin texto | **Se reutiliza** el existente |
| con texto | el **mismo** | Aceptado, sin escritura |
| con texto | **distinto** | **`409 alt_text_conflict`**, sin sobrescribir |
| **sin imagen** | con texto | **`422`**: combinación inválida, rechazada en lugar de ignorada |

### El caso E, dicho con precisión (D-012-Z)

**Ninguna fuente vigente define qué ocurre con un texto distinto.** Se comprobó archivo por
archivo sobre `main`: `data-model.md`, `CONTENT_MODEL.md`, `USER_FLOWS.md`,
`api-contracts.md`, `non-functional-requirements.md`, la ficha y el reporte de `Task/010`.
Cero coincidencias.

Lo que sí existe es **el riesgo**, descrito por **D-010-J** para el caso análogo de la
deduplicación: *«reutilizar en silencio haría que borrar un medio afectara a contenidos que
nunca lo subieron»*. Sobrescribir el texto tiene esa misma forma.

**Alternativas mínimas, para la decisión externa:**

| # | Alternativa | Coste |
| --- | --- | --- |
| 1 | **Rechazar** — *implementada* | El administrador no puede corregir un texto desde el uso |
| 2 | Sobrescribir siempre | Cambia en silencio el `alt` de contenidos que no lo pidieron. **Irreversible** |
| 3 | Sobrescribir solo si ningún otro contenido usa la imagen | Coherente con el riesgo real, pero el resultado depende de estado oculto y ninguna fuente lo respalda |
| 4 | Copiar la imagen al corregir el texto | Contradice D-010-J: multiplica assets en silencio |

Se implementa la **1**. Rechazar **también es una decisión de comportamiento**, no la
ausencia de una: se elige por conservadora, no por neutral. Es explícita —al contrario que
ignorar—, reversible, y evita modificar en silencio un `MediaAsset` que puede estar siendo
utilizado por otro contenido.

> **Actualización del 2026-09-02.** La revisión externa **acepta D-012-Z**: queda
> **RESUELTA / ACEPTADA PARA EL MVP**. La redacción original de este apartado la
> presentaba como *«la única que no inventa comportamiento»*, y eso era falso; corregido
> arriba y en la sección **AX**.

## AQ. RED

`tests/integration/test_api_admin_texto_alternativo.py`, ampliado: **18 fallos**.

| Caso | Tipos | Fallo |
| --- | --- | --- |
| Escribir en el primer uso al **crear** | 4 | `422`: el DTO no conocía el campo |
| Escribir en el primer uso al **editar** | 4 | ídem |
| Reenviar el **mismo** texto | 4 | ídem |
| Texto **distinto** → `409` | 4 | ídem |
| Perfil: primer uso, texto distinto | 2 | `422`/`409` no llegaban |

Pasaron al escribirse —y son **regresión**— los casos que el código ya cubría: reutilizar
un texto existente, rechazar el texto sin imagen y el rollback.

## AR. GREEN

| Capa | Cambio |
| --- | --- |
| **Dominio** (`media/domain/texto_alternativo.py`, **nuevo**) | La regla pura: qué escribir, qué reutilizar y cuándo rechazar. Vive en `media` porque `alt_text` es metadato **del asset** y ese módulo es su dueño (software-architecture.md §3.3) |
| **Aplicación** (5 módulos) | `_asignar_texto_alternativo`, invocado tras validar referencias y **antes** de escribir la asociación |
| **Infraestructura** (5 repositorios) | `texto_alternativo_del_medio` y `escribir_texto_alternativo`, con `flush` en la sesión de la petición |
| **Presentación** (5 esquemas) | El campo nuevo y un `model_validator` que rechaza el texto sin imagen |

**Quién escribe `MediaAsset.alt_text`:** el repositorio del módulo que establece la
referencia, dentro de la **misma transacción** de la petición (D-012-V). Comprobado con una
prueba de rollback: se provoca un fallo posterior —una etiqueta desconocida— y el texto
**no** queda persistido.

**MinIO no se toca**: esto es metadato de PostgreSQL.

## AS. `Task/010` intacta

No se modificó `SubirImagen`, `EliminarMedio`, `ObjectStorage`, `MinIOStorage`, `S3Storage`
ni **D-010-N**. Subir sin `alt_text` sigue permitido, y hay una prueba que lo fija.

## AT. Regresión

| Suite | Resultado |
| --- | --- |
| Texto alternativo | **56 ✔** |
| Contenido administrativo y perfil | **221 ✔** |
| `Task/010` medios y auditoría de medios | **64 ✔** |
| Contrato | **270 ✔** |
| **Suite completa** | **1512 pasan, 1 omitida**, **0 advertencias** con `-W error` |
| Cobertura | **100 %** |

**+46 sobre 1466**: 31 de integración y 15 de dominio.

## AU. Puertas de calidad finales

| Puerta | Resultado |
| --- | --- |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 280 files already formatted |
| `mypy .` | Success: no issues found in 278 source files |
| `pytest --cov -q -W error` | **1512 passed, 1 skipped**, 0 advertencias, **100 %** |
| `pip check` | No broken requirements found |
| `git diff --check` | limpio |
| `alembic heads` | **`0003 (head)`**; `0001`–`0003` intactas |

**Sin Docker, sin rebuild, sin WinNAT, sin WSL.** Ningún cambio afecta a la imagen.

## AV. Documentación

| Documento | Cambio |
| --- | --- |
| Ficha, **D-012-R** | Ahora dice las tres piezas: `Task/010` no exige al cargar · `Task/012` escribe en el primer uso y exige donde se usa · `Task/014` sigue siendo dueña del render |
| Ficha, **D-012-Y** *(nueva)* | El primer uso escribe. Sin ampliar `/admin/media` |
| Ficha, **D-012-Z** *(nueva)* | Un texto distinto se rechaza; alternativas listadas. **Aceptada para el MVP** el 2026-09-02 (sección AX) |
| Ficha, deuda | **Retirada** la que decía que una imagen no podía ganar texto: ya no es cierta |
| `api-contracts.md` | **§14.11 nueva**; el código `alt_text_conflict` en la tabla de errores |
| `data-model.md` | La fila `alt_text` recoge las **dos** mitades; deuda 6b reformulada |
| `security-boundaries.md` | **B-16** nueva, y lo que sigue sin afirmarse |
| `STATUS.md`, `STAGE-03` | Cifras y hallazgo |

**`Task/018` no recibe ningún *owner*.** **`Task/014`** conserva el suyo: el render HTML
accesible, que es lo que siempre le asignó `non-functional-requirements.md`.

## AW. Veredicto de esta corrección

| Pregunta | Respuesta |
| --- | --- |
| ¿Una imagen puede cargarse sin `alt_text`? | **SÍ** — D-010-N intacta |
| ¿Puede recibirlo **después**, cuando se usa? | **SÍ** |
| ¿Se persiste en `MediaAsset`? | **SÍ**, en la misma transacción |
| ¿La publicación conserva su guarda defensiva? | **SÍ**, como última guarda |
| ¿El perfil puede asignar el texto por primera vez? | **SÍ** |
| ¿Se evita la sobrescritura silenciosa? | **SÍ** — `409`, con alternativas documentadas |
| ¿`Task/010` queda intacta? | **SÍ** |
| ¿`Task/018` recibe un *owner* inventado? | **NO** |
| ¿Se añadió `PUT`/`PATCH` a `/admin/media`? | **NO** — sigue con tres operaciones |
| ¿Suite verde? | **SÍ** — 1512 pasan, 1 omitida |
| ¿Cobertura? | **100 %** |

---

# Endurecimiento de concurrencia (2026-09-02)

Un solo bloqueador, y era real. La revisión anterior dejó `D-012-Z` escrita como regla;
esta comprueba si **se sostiene cuando dos administradores llegan a la vez**. No se
sostenía.

## AX. Redacción de D-012-Z, corregida

La versión anterior decía que rechazar era *«la única respuesta que no inventa
comportamiento»*. **Es falso, y conviene decirlo**: rechazar es también una decisión de
comportamiento — devuelve un `409` que antes no existía y cierra un recorrido al
administrador. Presentarla como la ausencia de una decisión la blindaba de la crítica que
sí merecía.

Redacción vigente, en el dominio, en la ficha y en `api-contracts.md` §14.11:

> Ante la ausencia de una semántica canónica previa, `Task/012` adopta para el MVP la
> política conservadora de rechazar una sobrescritura diferente. La revisión externa acepta
> **D-012-Z**. La política es explícita, reversible y evita modificar en silencio un
> `MediaAsset` que puede estar siendo utilizado por otro contenido.

**D-012-Z: RESUELTA / ACEPTADA PARA EL MVP.** Ya no se declara «pendiente de revisión
externa» en ningún documento. Poder **corregir a propósito** un texto ya fijado queda como
**mejora futura sin propietario ni plazo** — relajación deliberada de una decisión
aceptada, no contradicción de ella. No se implementa `PATCH`/`PUT /admin/media`, ni
copy-on-write, ni versionado.

## AY. Diagnóstico: los cinco repositorios, antes de tocar nada

| Pregunta | Respuesta comprobada |
| --- | --- |
| Nivel de aislamiento | **READ COMMITTED**. `SHOW default_transaction_isolation` → `read committed`; no hay ningún ajuste de aislamiento en `app/shared/database/` ni en `app/shared/configuration/` |
| `SELECT` de la decisión | `select(MediaAsset.alt_text).where(MediaAsset.id == …)` — **sin** `with_for_update()`, idéntico en los cinco |
| Cerrojo de fila | **Ninguno** |
| `UPDATE` | `fila.alt_text = texto` + `flush()` → **incondicional**, sin `WHERE alt_text IS NULL` |
| Restricción que lo impidiera | **Ninguna.** `pg_constraint` sobre `media_assets`: `pk_media_assets`, `uq_media_assets_object_key` y tres `CHECK` de tamaños |
| `COMMIT` | Solo en `session_scope` y en el commit defensivo de `Task/011`. **Ninguno** en estos repositorios |

**Conclusión del diagnóstico: la carrera era real.** Nada serializaba la secuencia
leer-decidir-escribir.

> **Cómo se comprobaron las dos primeras filas.** Con `docker exec` de **solo lectura**
> contra el contenedor `personal-blog-local-postgres` (`psql` → `SHOW
> default_transaction_isolation` y consulta a `pg_constraint`). Es el único uso de Docker
> de esta ronda; no modificó nada. Ver la nota de la sección BG.

## AZ. RED

`tests/integration/test_concurrencia_del_texto_alternativo.py`, **nuevo**. PostgreSQL real
sobre `personal_blog_test`, dos `Session` independientes en dos hilos alineados con un
`threading.Barrier(2)`. Sin SQLite, sin *mocks*, sin `pytest-xdist`. MinIO no participa.

```
assert sorted(resultados) == ["conflicto", "ok"]
E       assert ['ok', 'ok'] == ['conflicto', 'ok']

assert len([... eventos de contenido ...]) == 1
E       AssertionError: assert 2 == 1
```

**15 fallos**, los cinco consumidores. Las dos transacciones prosperaban, el segundo
`UPDATE` pisaba al primero y quedaban **dos** eventos de auditoría. *Last-write-wins*
exacto — lo que la revisión prohíbe.

## BA. GREEN — D-012-AA

**La lectura que decide bloquea la fila del medio.**

```python
def bloquear_texto_alternativo(self, identificador: uuid.UUID) -> str | None:
    return self._sesion.execute(
        select(MediaAsset.alt_text).where(MediaAsset.id == identificador).with_for_update()
    ).scalar_one_or_none()
```

**Por qué elimina la carrera, y no por gusto.** En `READ COMMITTED`, `SELECT … FOR UPDATE`
hace dos cosas a la vez: quien llega segundo **espera** al cerrojo de fila, y al obtenerlo
**relee la última versión confirmada** —no la instantánea con la que empezó—. Así ve el
texto del ganador, y la regla pura del dominio decide sin cambiar una línea: `409` si es
distinto, no-op si resulta ser el mismo. **La igualdad no se convierte en conflicto.**

**Por qué vale fuera de este proceso.** El cerrojo lo mantiene **el motor**, no el
intérprete: no depende del GIL, ni de que haya un solo *worker*, ni de que haya una sola
instancia de Lambda. Es el mismo criterio de **A-08** en `Task/011` y de **D-012-P**.

**Por qué no la alternativa condicional.** Un `UPDATE … WHERE alt_text IS NULL` es igual de
atómico, pero al devolver *0 filas* no distingue *«otro escribió lo mismo»* de *«otro
escribió algo distinto»*: obliga a una segunda lectura y a duplicar fuera del dominio la
decisión que `texto_a_escribir` ya toma. Más piezas para la misma garantía.

| Capa | Cambio |
| --- | --- |
| **Infraestructura** (5 repositorios) | `bloquear_texto_alternativo`, la lectura con cerrojo |
| **Aplicación** (5 puertos y 5 casos de uso) | `_asignar_texto_alternativo` la usa en lugar de la lectura simple |
| **Dominio** | **Sin cambios.** La regla pura ya era correcta; lo que faltaba era llegar a ella en exclusión |

**Sin Redis, sin cerrojos distribuidos, sin *advisory locks* globales, sin tabla nueva, sin
migración nueva.** `alembic heads` sigue en `0003`.

## BB. Las lecturas que **no** se bloquean

La exclusión existe **solo** en la operación que decide y escribe `alt_text`:

| Lectura | Cerrojo |
| --- | --- |
| `GET` público de cualquier tipo | **no** |
| Biblioteca `GET /admin/media` y `access_url` | **no** |
| `texto_alternativo_del_medio`, validación de publicación | **no** |
| `bloquear_texto_alternativo`, decisión *set-on-first-use* | **sí** |

`Task/009` no se tocó. `Task/010` tampoco: `SubirImagen`, `EliminarMedio`, `ObjectStorage`,
`MinIOStorage`, `S3Storage` y **D-010-N** siguen intactos.

**Sin interbloqueo, y comprobado por inspección del orden de adquisición:** crear y
actualizar bloquean **solo** la fila de `media_assets`; las transiciones de publicación
bloquean **solo** la fila del contenido y no tocan `alt_text`. Ninguna ruta toma el cerrojo
del contenido y después el del medio, así que no hay ciclo posible.

## BC. Los cinco consumidores, con evidencia

La prueba está parametrizada sobre un `Consumidor` que invoca el **caso de uso real** de
cada módulo con su propio DTO — no una abstracción común que pudiera esconder que solo uno
está protegido:

| Consumidor | Campo | Distinto | Ganador único | Mismo texto |
| --- | --- | --- | --- | --- |
| `POST /admin/posts` | `cover_alt_text` | ✔ | ✔ | ✔ |
| `POST /admin/book-reviews` | `cover_alt_text` | ✔ | ✔ | ✔ |
| `POST /admin/videos` | `thumbnail_alt_text` | ✔ | ✔ | ✔ |
| `POST /admin/projects` | `cover_alt_text` | ✔ | ✔ | ✔ |
| `PUT /admin/profile` | `photo_alt_text` | ✔ | ✔ | ✔ |

**15 pruebas, 15 verdes.** Y en las tres dimensiones que la revisión exigió: una sola
política gana, el valor final es **exactamente** el del ganador —nunca un tercer estado—,
y queda **un** único evento de auditoría. El control de texto idéntico confirma que la
igualdad sigue siendo aceptación, no conflicto.

## BD. REFACTOR

Retirado `texto_alternativo_del_medio` del módulo `profile`, puerto y repositorio: se quedó
sin llamadores. El perfil no tiene publicación —*«siempre existe y siempre está visible»*—,
así que no hay una segunda lectura de validación como en los cuatro tipos publicables:
asignar la foto **es** usarla, y esa misma lectura decide. Lo detectó la cobertura al bajar
a 99 %. En los otros cuatro módulos el método **se conserva**: ahí sí lo usa la validación
de publicación, que no debe bloquear.

Sin refactor mayor: cinco métodos explícitos de tres líneas, con la misma forma, frente a
una abstracción compartida que habría cruzado el límite entre módulos por estética.

## BE. Lo que la corrección **no** rompió

| Propiedad | Estado |
| --- | --- |
| Texto y asociación en la **misma transacción** (D-012-V) | intacta |
| *Rollback* ante etiqueta desconocida: no persiste el texto | intacta |
| `COMMIT` solo en la unidad de trabajo, nunca en el repositorio | intacta |
| Auditoría y validación de publicación | intactas |
| `Task/009` y `Task/010` | sin tocar |

## BF. Regresión focalizada

| Suite | Resultado |
| --- | --- |
| Concurrencia del texto alternativo (**nueva**) | **15 ✔** |
| Texto alternativo, concurrencia administrativa, contenido y perfil | **362 ✔** |
| Medios de `Task/010` y auditoría de medios | **26 ✔** |

## BG. Ronda completa final

| Puerta | Resultado |
| --- | --- |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 281 files already formatted |
| `mypy .` | Success: no issues found in 279 source files |
| `pytest --cov -q -W error` | **1527 passed, 1 skipped**, 0 advertencias, **100 %** |
| `pip check` | No broken requirements found |
| `git diff --check` | limpio |
| `alembic heads` | **`0003 (head)`** — **ninguna migración nueva** |

**1527, quince más que las 1512 de la ronda anterior.** Sin *rebuild*, sin WSL, sin
WinNAT. Ningún cambio afecta a la imagen.

**Docker CLI sí se utilizó en esta ronda**, y conviene decirlo con precisión: únicamente
mediante `docker exec` de **solo lectura** contra el PostgreSQL de pruebas, para consultar
`SHOW default_transaction_isolation` y `pg_constraint` —las dos comprobaciones del
diagnóstico de la sección AY—. **No hubo** cambios de *lifecycle*, *rebuild*, `restart`,
`up`/`down`, `prune`, volúmenes ni configuración de contenedores.

## BH. Documentación

| Documento | Cambio |
| --- | --- |
| `media/domain/texto_alternativo.py` | Redacción corregida; D-012-Z aceptada para el MVP |
| Ficha, **D-012-Z** | **RESUELTA / ACEPTADA PARA EL MVP** |
| Ficha, **D-012-AA** *(nueva)* | Estrategia de atomicidad, con las alternativas descartadas |
| Ficha y `STATUS`, pendiente 2 | De «abierto, sin propietario» a **mejora futura** |
| `api-contracts.md` §14.11 | Redacción corregida y apartado *La decisión es atómica* |
| `data-model.md` deuda 6b | Reformulada como mejora futura |
| `security-boundaries.md` | **B-17** nueva; dos afirmaciones que se siguen sin hacer |
| `STATUS.md`, `STAGE-03` | Hallazgo 6 y cifras |

## BI. Veredicto

| Pregunta | Respuesta |
| --- | --- |
| ¿Existía la carrera? | **SÍ** — demostrada, no supuesta |
| ¿Pueden dos primeros usos fijar textos distintos? | **NO** |
| ¿El valor final es exactamente el del ganador? | **SÍ** |
| ¿Un texto idéntico produce conflicto? | **NO** |
| ¿La garantía cubre los cinco consumidores? | **SÍ**, con evidencia por consumidor |
| ¿Se bloquea alguna lectura pública? | **NO** |
| ¿Hay `COMMIT` en el repositorio? | **NO** |
| ¿Migración nueva? | **NO** — `0003` sigue siendo *head* |
| ¿`Task/009` o `Task/010` modificadas? | **NO** |
| ¿Suite verde? | **SÍ** — 1527 pasan, 1 omitida, **100 %** |

---

# Micro-cierre final (2026-09-03)

Dos correcciones de **evidencia**, ninguna de arquitectura. `D-012-Z` y `D-012-AA` quedan
exactamente como estaban; no se tocó código productivo.

## BJ. El control del texto idéntico exigía poco

`test_dos_primeros_usos_con_el_mismo_texto_son_coherentes` comprobaba:

```python
assert "conflicto" not in resultados
```

Eso es una expectativa **débil**: `["ok", "error:DeadlockDetected"]` la habría superado
—no contiene la palabra `conflicto`— y podía además dejar el valor final correcto. La
garantía que la decisión promete es más fuerte: dos primeros usos concurrentes que
proponen **exactamente el mismo texto** deben **completar los dos**.

La expectativa nueva:

```python
assert sorted(resultados) == ["ok", "ok"]
```

más la comprobación que ya existía de que `MediaAsset.alt_text == TEXTO_A`.

`_carrera` **no se modificó**: sigue traduciendo cualquier excepción distinta de
`TextoAlternativoEnConflictoError` a `error:<tipo>`, y ahora ese veredicto hace **fallar**
la prueba en lugar de pasar desapercibido.

| Aspecto | Antes | Ahora |
| --- | --- | --- |
| Expectativa | `"conflicto" not in resultados` | `sorted(resultados) == ["ok", "ok"]` |
| `["ok", "error:DeadlockDetected"]` | **pasaba** | **falla** |
| `["conflicto", "ok"]` | fallaba | falla |
| Valor final `TEXTO_A` | comprobado | comprobado |
| Consumidores cubiertos | 5 | 5 — `Post`, `BookReview`, `Video`, `Project`, `Profile` |

## BK. Validación de esta micro-ronda

Es **solo un endurecimiento de aserción**: no cambia código productivo, ni configuración,
ni dependencias. Por eso no se fabricó un RED productivo nuevo ni se repitió la suite
entera.

| Puerta | Resultado |
| --- | --- |
| `pytest tests/integration/test_concurrencia_del_texto_alternativo.py` sobre `personal_blog_test` | **15 passed** |
| `git diff --check` | limpio |

**Las dos cifras se registran por separado, y no se suman:**

| Ronda | Cifra |
| --- | --- |
| Suite completa previa (sección BG) | **1527 passed, 1 skipped**, 0 advertencias, **100 %** |
| Esta micro-ronda, focalizada | **15 passed** |

La ronda completa de la sección BG **sigue siendo evidencia válida**: nada de lo que
cubre ha cambiado.

## BL. Docker, dicho con precisión

La redacción anterior de la sección BG decía *«Sin Docker»*. **Era incorrecta.** Durante
el endurecimiento de concurrencia **sí se invocó Docker CLI**, aunque solo para leer:

| Pregunta | Respuesta |
| --- | --- |
| `docker exec` histórico | **SÍ** |
| Propósito | Solo lectura: `SHOW default_transaction_isolation` y `pg_constraint` sobre `media_assets` |
| Contenedor | `personal-blog-local-postgres` |
| *Lifecycle* modificado | **NO** |
| `build` / *rebuild* | **NO** |
| `restart` | **NO** |
| `up` / `down` | **NO** |
| `prune` | **NO** |
| Volúmenes o configuración de contenedores | **NO** |
| WSL, WinNAT | **NO** |

Corregidas las secciones **AY** (nota de procedencia del diagnóstico) y **BG** (redacción
durable). **No se ejecutó Docker de nuevo** para demostrarlo: la evidencia ya existía. La
documentación de otras tareas no se modifica.

## BM. Aritmética

No existía en documentación durable la frase *«+15 sobre 1527»* ni ninguna equivalente que
implicara `1527 + 15`: el barrido de *«+15»* en `docs/` no devuelve ninguna. La sección BG
ya decía **«1527, quince más que antes»**; se explicita ahora el punto de partida
—**«1527, quince más que las 1512 de la ronda anterior»**— para que el incremento no
admita otra lectura. El salto correcto es **1512 → 1527**.

## BN. Gobierno

Sin cambios: `Task/012` sigue **Lista para validación**, el avance sigue en **11 / 41
(27 %)** y la ETAPA 03 en **4 / 5 (80 %)**. Cero commits, cero *push*, cero *merge*, cero
PR. `Task/013` no se ha iniciado.

## BO. Veredicto del micro-cierre

| Pregunta | Respuesta |
| --- | --- |
| ¿El control del texto idéntico exige el éxito de **las dos** operaciones? | **SÍ** |
| ¿Un error inesperado hace fallar ahora la prueba? | **SÍ** |
| ¿Cubre los cinco consumidores? | **SÍ** |
| ¿El reporte reconoce el `docker exec` de solo lectura? | **SÍ** |
| ¿Hubo Docker destructivo? | **NO** |
| ¿Se tocó código productivo? | **NO** |
| ¿Se repitió la suite completa? | **NO** — y no se declara como tal |

---

# Cierre aprobado (2026-09-03)

## BP. Aprobación

| Campo | Valor |
| --- | --- |
| **Expresión recibida** | `approved: Task/012-API-Administrativa` |
| **Aprobado por** | jeffersondavila (usuario) |
| **Fecha** | 2026-09-03 |
| **Rama aprobada** | `Task/012-API-Administrativa` — activa en backend e infra, creada **desde `main`** |
| **Repositorios afectados** | `personal-blog-backend` · `personal-blog-infra` |
| **Repositorio no afectado** | `personal-blog-frontend` — en `main`, limpio, **sin rama Task** |
| **Cambios ajenos mezclados** | **Ninguno.** El árbol de trabajo solo contenía lo de `Task/012` |

## BQ. Validaciones finales del cierre

Ejecutadas **después** de la aprobación y **antes** del commit, con PostgreSQL
(`personal_blog_test`) y MinIO reales.

| Puerta | Resultado |
| --- | --- |
| `ruff check .` | All checks passed |
| `ruff format --check .` | 281 files already formatted |
| `mypy .` | Success: no issues found in 279 source files |
| `pytest --cov -q -W error` | **1527 passed, 1 skipped**, 0 advertencias, **100 %** (`TOTAL 4511 sentencias, 0 sin cubrir`) |
| `pip check` | No broken requirements found |
| `alembic heads` | **`0003 (head)`** — ninguna migración nueva |
| `git diff --check` | limpio en los tres repositorios |
| Enlaces relativos de los documentos tocados | **242 comprobados, 0 rotos** |
| Criterion 12 | **C = 0** |
| Búsqueda de secretos | sin hallazgos: ninguna clave, token ni contraseña en el diff |

> **Una primera ejecución de la suite se descartó y se repitió.** Salió sin
> `PERSONAL_BLOG_TEST_STORAGE_*` y omitió las 72 pruebas de MinIO —**1455 passed, 73
> skipped**—. No es una ronda válida y no se cuenta como tal. La cifra buena es la de la
> tabla, con el entorno de integración completo.

## BR. Documentación de la aprobación

| Documento | Cambio |
| --- | --- |
| `STATUS.md` | `Task/012` **Aprobada**; avance **12 / 41 (29 %)**; ETAPA 03 al **100 %**; secciones de tareas reordenadas; observación fechada del cierre |
| `ROADMAP.md` | Estado de `Task/012` y **ETAPA 03 completada** (5 de 5); avance global |
| `STAGE-03-domain-and-backend.md` | Etapa **Completada** ✔; los **once** criterios de salida marcados, cada uno con su evidencia |
| `STAGE-04-user-experience.md` | Dependencia ETAPA 03 **satisfecha** |
| Ficha `TASK-012` | Estado **Aprobada**; §12 corregida de *«veinticuatro, D-012-A a D-012-X»* a **veintisiete, D-012-A a D-012-AA**; §15 corregida de **1418** a **1527** |
| Este reporte | Cabecera y esta sección |

**ADR: ninguno que promover.** `Task/012` no crea ni sustituye ADR —sus decisiones son de
implementación dentro de contratos ya aceptados (ficha §12)—, y ningún ADR estaba en
`Propuesta`. **D-012-Z** queda **RESUELTA / ACEPTADA PARA EL MVP**.

## BS. Flujo de cierre ejecutado

En **backend** e **infra**, en este orden:

1. Commit único de la tarea en la rama `Task/012-API-Administrativa`.
2. `git switch dev` y `git pull --ff-only origin dev`.
3. `git merge --no-ff Task/012-API-Administrativa` dentro de `dev`.
4. `git push origin dev`.
5. `git push -u origin Task/012-API-Administrativa`.
6. `gh pr create --base main --head Task/012-API-Administrativa`, con `--body-file`.
7. `git switch main`, `git fetch --prune`, `git pull --ff-only origin main`.
8. `git branch -d Task/012-API-Administrativa` — **nunca `-D`**.

**El pull request es `Task/012-API-Administrativa → main` en los dos repositorios.**
Ninguno usa `dev` como *head*, ninguno lo fusiona Claude, y **la rama Task remota no se
elimina**: es decisión del usuario.

`personal-blog-frontend` **no participa** en ninguno de estos pasos.

## BT. Lo que el cierre NO hace

| Acción | Estado |
| --- | --- |
| Fusionar el pull request | **NO** — responsabilidad exclusiva del usuario |
| `gh pr merge` | **NO ejecutado** |
| Modificar `main` directamente | **NO** |
| Eliminar la rama Task **remota** | **NO** |
| `git branch -D`, `reset --hard`, `clean -fd`, `push --force` | **NO** |
| Iniciar `Task/013` | **NO** |
| Normalizar `main → dev` | **Todavía no**: corresponde después de que el usuario fusione (PROJECT_INSTRUCTIONS §10) |

## BU. Veredicto del cierre

| Pregunta | Respuesta |
| --- | --- |
| ¿Aprobación explícita del usuario? | **SÍ** — `approved: Task/012-API-Administrativa` |
| ¿Validaciones finales verdes? | **SÍ** — 1527 / 1 omitida / 100 %, con MinIO real |
| ¿Rama Task creada desde `main`? | **SÍ**, verificado al crearla |
| ¿PR con base `main` y head la rama Task? | **SÍ**, en los dos repositorios |
| ¿Algún PR `dev → main`? | **NO** |
| ¿Claude fusionó algo hacia `main`? | **NO** |
| ¿ETAPA 03 completada? | **SÍ** — 5 de 5, con los once criterios de salida evidenciados |
| ¿Avance global? | **12 de 41 — 29 %** |
| ¿`Task/013` iniciada? | **NO** |
