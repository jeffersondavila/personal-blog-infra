# TASK-009 — API Pública · Reporte

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/009-API-Publica` |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Estado** | **Aprobada** — 2026-08-27 |
| **Fecha** | 2026-08-26 · **remediación TDD y revalidación: 2026-08-27** · **aprobada: 2026-08-27** |
| **Ficha** | [TASK-009](../tasks/TASK-009-public-api.md) |

> **Aprobada el 2026-08-27.** El usuario escribió `approved: Task/009-API-Publica`. Las
> secciones §A a §X describen el estado **previo a la aprobación** y se conservan tal cual:
> son la evidencia de que nada se publicó antes de aprobar. El estado duradero está en
> **§Y**; el trámite de cierre —commit, integración en `dev`, publicación y pull request—
> es estado **transitorio** y se consulta en Git y GitHub, no aquí.

> **Este reporte cubre dos ejecuciones y las declara como tales.** En la primera se detectó
> —**antes de la aprobación**— una desviación de la
> [BACKEND TEST-FIRST LAW](../project-management/BACKEND_TESTING_STRATEGY.md) en seis
> *slices* (**§I.2**). La tarea **no** se aprobó. Después, y antes de cualquier *commit*,
> *push* o PR, esos seis *slices* se reconstruyeron genuinamente test-first en un
> laboratorio limpio nacido del mismo SHA base (**§I.5**), y esa implementación
> reconstruida —**no** la *post-hoc*— es la que hoy está en el árbol de trabajo del
> repositorio oficial y la candidata a aprobación. **La historia original no se ha borrado
> ni reescrito.**

---

## A. Estado inicial

Reconstruido en vivo desde Git, no leído de un documento
([WORKFLOW §6.1](../project-management/WORKFLOW.md)).

| Repositorio | `main` | `origin/main` | Árbol limpio | Ramas Task previas |
| --- | --- | --- | :---: | :---: |
| `personal-blog-backend` | `0ada6a73aa69d3fa7d401f24e130fee059977aa2` | idéntico | sí | ninguna |
| `personal-blog-infra` | `71f56da2cc0523feae961b54ccbf0322b68826b8` | idéntico | sí | ninguna |
| `personal-blog-frontend` | `fd62f221707591a984cf0fb51a03ea339380ab35` | idéntico | sí | ninguna |

Invariantes de integración, en backend e infra:

| Comprobación | Resultado |
| --- | --- |
| `git merge-base --is-ancestor main dev` | `0` |
| `git rev-list --count dev..main` | `0` |
| `git diff main dev` | vacío |

Los tres SHA coincidieron con los que registró el cierre de `Task/008`. Se comprobaron de
todos modos: el prompt los daba como referencia histórica, no como hecho.

**Baseline de la suite antes de empezar:** `250 pasan, 1 omitida, 0 advertencias` con
`-W error` — exactamente la que documentó `Task/008`.

---

## B. Ramas

| Repositorio | Rama | Base | SHA base | `HEAD == main` al crearla | `main..HEAD` |
| --- | --- | --- | --- | :---: | :---: |
| backend | `Task/009-API-Publica` | **`main`** | `0ada6a73…` | **SÍ** | `0` |
| infra | `Task/009-API-Publica` | **`main`** | `71f56da2…` | **SÍ** | `0` |
| frontend | *ninguna* | — | — | — | — |

**¿Alguna rama nació de `dev`?** **NO.** Ninguna. `dev` no se tocó en ningún repositorio.

---

## C. Fuentes canónicas leídas

**Raíz:** `CLAUDE.md`.

**`personal-blog-infra`:** `docs/claude/PROJECT_INSTRUCTIONS.md` ·
`docs/project-management/WORKFLOW.md` · `STATUS.md` · `ROADMAP.md` ·
`DEFINITION_OF_DONE.md` · `TASK_TEMPLATE.md` · `BACKEND_TESTING_STRATEGY.md` ·
`docs/stages/STAGE-03-domain-and-backend.md` · `docs/product/MVP_SCOPE.md` ·
`USER_FLOWS.md` · `CONTENT_MODEL.md` · `docs/architecture/data-model.md` ·
`api-contracts.md` · `software-architecture.md` · `non-functional-requirements.md` ·
`security-boundaries.md` · `open-decisions.md` · `docs/adr/ADR-004` · `ADR-005` ·
`docs/runbooks/local-environment.md` §9.

**`personal-blog-backend`:** `README.md` · `CONTRIBUTING.md` · `pyproject.toml` ·
`requirements.txt` · `requirements-dev.txt` · `app/main.py` · `app/api/` ·
`app/shared/` (configuración, base de datos, errores, logging) · `app/modules/models.py`
y los nueve módulos de `Task/008` · `alembic.ini` · `alembic/env.py` ·
`alembic/versions/` · `tests/__init__.py` · `tests/conftest.py` ·
`tests/integration/conftest.py` · `tests/test_grafo_de_fixtures_de_integracion.py` ·
`tests/test_openapi.py` · `tests/unit/` · `tests/integration/`.

---

## D. Contrato cerrado

| Endpoint | Query params | Respuesta `200` | `404` | `422` |
| --- | --- | --- | --- | --- |
| `GET /api/v1/profile` | — | `ProfilePublico` | perfil ausente | params no admitidos |
| `GET /api/v1/posts` | `page`, `page_size`, `tag`, `featured`, `sort` | `Pagina[PostDeListado]` | — | params inválidos o no admitidos |
| `GET /api/v1/posts/{slug}` | — | `PostDetallado` | inexistente · `draft` · `archived` | params no admitidos |
| `GET /api/v1/book-reviews` | `page`, `page_size`, `tag`, `featured`, `sort` | `Pagina[ReviewDeListado]` | — | ídem |
| `GET /api/v1/book-reviews/{slug}` | — | `ReviewDetallada` | inexistente · `draft` · `archived` | ídem |
| `GET /api/v1/videos` | `page`, `page_size`, `tag`, `featured`, `sort` | `Pagina[VideoDeListado]` | — | ídem |
| `GET /api/v1/projects` | `page`, `page_size`, `tag`, `featured`, `sort` | `Pagina[ProyectoDeListado]` | — | ídem |
| `GET /api/v1/projects/{slug}` | — | `ProyectoDetallado` | inexistente · `draft` · `archived` | ídem |
| `GET /api/v1/tags` | `page`, `page_size` | `Pagina[EtiquetaPublica]` | — | ídem |
| `GET /api/v1/search` | `q` **(obligatorio)**, `page`, `page_size` | `Pagina[ResultadoDeBusqueda]` | — | `q` ausente o inválido |

**`GET /api/v1/videos/{slug}` no existe.** No está en el contrato canónico y no se
inventó. Hay una prueba que lo comprueba **con un vídeo publicado sembrado**, para que el
`404` no pueda deberse a que no haya contenido.

Envoltura de colección, idéntica en los seis listados y en la búsqueda:

```json
{ "items": [], "page": 1, "page_size": 12, "total": 0, "pages": 0 }
```

---

## E. Decisiones de `Task/009`

Tabla completa, con alternativas y justificación, en la
[ficha §8](../tasks/TASK-009-public-api.md). Resumen de lo cerrado:

| Decisión | Elegida |
| --- | --- |
| `page_size` por defecto | **12** — el de todos los ejemplos canónicos |
| `page_size` máximo | **50** — decidido aquí; por encima **se recorta** |
| Parámetros desconocidos | **Se rechazan** con `422` |
| Lista cerrada de `sort` | `published_at`, `title` |
| Dirección | Prefijo `-` (`sort=-title`) |
| Desempate estable | **`slug` ascendente**; en `/search`, `(type, slug)` |
| `featured` | Filtro booleano completo; solo los literales `true` y `false` |
| `tag` inexistente | `200` con `items` vacío |
| Visibilidad de `/tags` | Solo etiquetas con **al menos un contenido publicado** |
| Forma de `/search` | Colección **plana** con discriminador `type` |
| Campos buscados | `title`, `summary`; además `book_title` y `book_author` en reviews |
| Mecanismo de búsqueda | `ILIKE`, término ligado y comodines escapados |
| Índices nuevos | **Ninguno.** No se modifica el esquema físico |
| `/profile` sin perfil | `404` `resource_not_found` |
| Referencia a `MediaAsset` | `alt_text`, `width`, `height`. **Sin URL y sin `object_key`** |
| Listado vs detalle | DTO separados; el listado no carga el Markdown |
| Capas por módulo | `presentation → infrastructure`, **sin `application` vacía** |
| Consulta por tipo | Una por módulo; duplicación aceptada |

Documentadas de forma durable en
[`api-contracts.md`](../architecture/api-contracts.md) §5, §6 y §11, y en
[`data-model.md`](../architecture/data-model.md) §8.1 y §10.

**Decisiones ajenas:** `open-decisions.md` no registra ninguna cuyo dueño sea `Task/009`.
**No se tocó el documento.**

---

## F. DTO públicos

Matriz campo a campo en la [ficha §7.4](../tasks/TASK-009-public-api.md). Lo que importa
del resultado:

| Campo | ¿Público? | Motivo |
| --- | :---: | --- |
| `slug`, `title`, `summary`, `published_at`, `tags` | **Sí** | Los pide USER_FLOWS A.2–A.7 |
| `content`, SEO, `reading_time_minutes` | **Solo detalle** | Cargar el Markdown de doce filas para pintar resúmenes contradice P-08; el SEO alimenta una página propia, y un elemento de listado no la tiene |
| `id` (UUID) | **No** | El público navega por `slug`. Los identificadores internos son de la API administrativa |
| `status` | **No** | Estar en la API pública ya significa `published`. Un campo constante no informa |
| `featured` | **No** | Ningún flujo lo necesita. **Añadir** un campo después es compatible; quitarlo no. Se omite en la dirección reversible |
| `created_at`, `updated_at` | **No** | Mismo criterio |
| `object_key` | **No** | Invariante 9 de CONTENT_MODEL: nunca claves de objeto sin control |

`Video` tiene **un solo** esquema, el de listado, y lleva `provider`, `video_url`,
`embed_reference`, `duration_seconds` y `thumbnail` precisamente porque no hay detalle
desde donde obtenerlos.

---

## G. Arquitectura

| Módulo | Capas creadas | Por qué existe cada una |
| --- | --- | --- |
| `posts`, `book_reviews`, `projects` | `domain` (ya existía) · `infrastructure` (modelos + **queries**) · `presentation` (router + schemas) | La consulta expresa la regla de visibilidad; el router valida, invoca y serializa |
| `videos` | igual, **sin consulta de detalle** | No existe endpoint de detalle en el contrato |
| `profile` | `infrastructure` (modelos + query) · `presentation` | *Singleton*: ni paginación ni filtros |
| `tags` | `infrastructure` (modelos + query) · `presentation` | Dueño de la etiqueta y de su asociación con contenido |
| `media` | `presentation` (**solo schemas**) | No expone endpoint: solo la forma pública de una referencia |
| `search` | `tipos.py` · `infrastructure` · `presentation` | Transversal: consulta los cuatro tipos y no es dueño de ninguno |
| `app/shared/pagination` | módulo nuevo | Aplazado desde `Task/005` hasta que hubiera duplicación real. Ahora la hay: seis listados y una búsqueda |
| `app/shared/lectura.py` | módulo nuevo | Contar palabras es capacidad técnica, sin regla de negocio |
| `app/api/` | `query_params.py`, `filtros_publicos.py`, `public.py` | Transporte HTTP transversal que no pertenece a ningún módulo |

**No se creó ninguna capa `application`**, y es una decisión, no un olvido
(**D-009-Q**). Un caso de uso de solo lectura sería aquí una función que reenvía sus
argumentos: sin orquestación, sin invariante que proteger y sin límite transaccional
propio. `software-architecture.md` §3.2 prohíbe explícitamente las capas vacías. La regla
de negocio real vive **dentro de la consulta**, que es donde nadie puede saltársela.
`Task/012` trae escritura, validación de publicación y auditoría: entonces `application`
tendrá trabajo que hacer.

**Tampoco se creó** ningún constructor genérico de consultas, repositorio universal,
CQRS, mediador ni DSL de búsqueda.

---

## H. Matriz TDD

La matriz completa —98 casos con su capa— está en la
[ficha §7.6](../tasks/TASK-009-public-api.md), escrita **antes** de tocar implementación.
Reparto por capa:

| Capa | Qué demuestra | Pruebas |
| --- | --- | --- |
| **unitaria** | Lógica pura: cálculo de páginas, recorte de `page_size`, tiempo de lectura | 100 |
| **contrato** (`tests/contract/`) | Forma HTTP: rutas, métodos, códigos, validación, envelope de error, OpenAPI | 188 |
| **integración** (PostgreSQL real) | Semántica: visibilidad, filtros, orden, conteo, búsqueda, N+1 | 178 |

`tests/contract/` se crea aquí: es la primera vez que existe un contrato HTTP que probar
(BACKEND_TESTING_STRATEGY §14.1). Sus pruebas **no tocan la base de datos**, y eso se hace
cumplir: la sesión se sustituye por un objeto que **lanza al primer uso**, de modo que una
prueba de contrato que llegara a consultar algo se pondría roja en lugar de pasar contra
una sesión inerte.

---

## I. Evidencia RED → GREEN → REFACTOR — **y una desviación que hay que declarar**

### I.1 Lo que se hizo bien

| *Slice* | RED | GREEN |
| --- | --- | --- |
| **1 · Primitivas de paginación** | `pytest tests/unit/test_paginacion.py` → `ModuleNotFoundError: No module named 'app.shared.pagination'`. El módulo especificado no existía | `16 passed` |
| **1b · Tiempo de lectura** | `pytest tests/unit/test_tiempo_de_lectura.py` → `ModuleNotFoundError: No module named 'app.shared.lectura'` | `10 passed` |
| **1c · Contrato de parámetros** | `pytest tests/contract` → `138 failed, 3 passed`. Motivo verificado: `assert 404 == 422`, porque ningún endpoint existía todavía | `188 passed` |
| **2 · Artículos** | `pytest tests/integration/test_api_articulos.py` → `24 failed, 4 passed` contra PostgreSQL real | `28 passed` |

**Las 4 pruebas que pasaban en el RED del *slice* 2 se investigaron**, como exige
BACKEND_TESTING_STRATEGY §5.2: eran las de `404` y las de ausencia de `object_key`, que
pasaban porque **sin endpoint** el router de Starlette ya devuelve un `404` con el mismo
`code` y sin cuerpo alguno. No demostraban nada en ese momento; sí lo demuestran ahora,
cuando la ruta existe y el `404` lo produce el endpoint.

### I.2 La desviación, sin adornos

**En los *slices* 3 a 7 —reviews, vídeos, proyectos, perfil, etiquetas y búsqueda— las
pruebas se escribieron DESPUÉS de la implementación.**

**Causa.** Al montar el *slice* 2 cableé `app/api/public.py` para que importara los siete
routers de una vez. A partir de ahí la aplicación no arrancaba —y por tanto ninguna prueba
podía ejecutarse— hasta que los siete módulos existieran. El error fue de secuencia: el
cableado debió ser incremental, un router por *slice*.

**Qué sí se conserva.** La **matriz de casos completa se escribió antes** de cualquier
implementación, y es la especificación de la que salieron esas pruebas: no se escribieron
mirando el código para describir lo que hacía.

**Qué se perdió, y no se recupera.** La garantía de que la implementación fue *conducida*
por la prueba. Reconstruir un RED borrando y reescribiendo código que ya existe sería
teatro, y no se hizo.

> **Actualización — 2026-08-27.** Esa reconstrucción sí se hizo, y no reescribiendo sobre
> el código existente: en un laboratorio limpio nacido del mismo SHA base, donde los seis
> módulos **no existían**. El RED es real, no simulado. Ver **§I.5**. Este párrafo se
> conserva porque describe correctamente el estado en el momento en que se escribió.

### I.3 Verificación por mutación, en lugar de un RED fingido

Lo que sí puede recuperarse de un RED es su parte comprobable: **que la prueba es capaz de
fallar**. Se verificó mutando cada guarda crítica y comprobando que la suite se pone roja.

| Mutación | Resultado |
| --- | --- |
| `posts`: se retira `status == PUBLISHED` de la consulta | **5 fallos**, incluidos los dos de indistinguibilidad del `404` |
| `tags`: se retira la condición de publicación del `EXISTS` | **2 fallos**: la etiqueta usada solo por borrador o archivado aparece |
| `search`: se retira `status == publicado` de las ramas de la unión | **3 fallos**, incluido el que recorre los cuatro tipos |
| `search`: se dejan los comodines de `LIKE` sin escapar | **al principio, 0 fallos** |

**El cuarto caso encontró un defecto real en mi propia prueba.** Buscar `50%` con el
patrón sin escapar sigue encontrando solo el artículo que contiene «50», así que la prueba
pasaba con las dos implementaciones: no distinguía nada. Se reescribió para que **muerda**
—se busca `%z` sobre un contenido que lleva una `z` pero no la secuencia literal `%z`, de
modo que solo la versión sin escapar lo devuelve— y se añadió la mitad complementaria: que
un `%` **literal** sí se encuentre, para que escapar de más tampoco pase inadvertido.
Repetida la mutación: **2 fallos**, como debe ser.

### I.4 Refactor

| Refactor | Motivo | Comportamiento observable |
| --- | --- | --- |
| Consultas reescritas a `_condiciones() -> list[ColumnElement[bool]]` | El conteo y el listado compartían un helper tipado para el modelo, que obligaba a un `type: ignore` y hacía que `mypy` dedujera `Post` donde había un entero. Ahora ambas parten de **la misma lista de condiciones**, que es además lo que garantiza que `total` cuente el conjunto que se está paginando | Sin cambios. Suite verde antes y después |
| Tablas Markdown de tres docstrings convertidas en listas | Superaban los 100 caracteres de línea | Ninguno |

### I.5 Remediación TDD — los seis *slices* se reconstruyeron test-first

**Nada de lo anterior se retracta.** La desviación descrita en §I.2 ocurrió, se detectó
**antes de la aprobación** y queda registrada tal cual. Lo que sigue es lo que se hizo
después, y por qué la implementación que hoy vive en el árbol de trabajo **no** es la
implementación *post-hoc* de §I.2.

**`Task/009` nunca fue aprobada, ni fusionada, ni publicada.** No hubo *commit*, *push*,
*merge* ni pull request en ningún momento de esta historia.

#### Cómo se remedió

Se creó un laboratorio aislado en `C:\Users\jeffe\Task009-remediation\`, fuera del
*workspace*, clonado desde el **mismo SHA base** del repositorio oficial
(`0ada6a73aa69d3fa7d401f24e130fee059977aa2`), con el `pushurl` deshabilitado
(`disabled://push-prohibited`). La implementación *post-hoc* se preservó aparte como
**backup histórico**, explícitamente **no** como fuente de implementación.

Sobre ese laboratorio se reconstruyó la base ya válida —paginación, tiempo de lectura,
contrato de parámetros, *envelope* de error, OpenAPI, artículos y el *harness*—, se dejó
`app/api/public.py` **registrando únicamente el router de Posts**, y a partir de ahí cada
uno de los seis *slices* afectados se rehízo en el orden estricto
**especificación → test → RED observado → implementación mínima → registrar el router →
GREEN → refactor → regresión vecina**.

| *Slice* | Especificación previa | RED real | GREEN | Refactor | Regresión vecina |
| --- | :---: | --- | --- | --- | ---: |
| **3 · Profile** | ✔ | `4 failed`, *exit* `1` — `/api/v1/profile` sin registrar; falla incluso el control positivo de perfil existente | `4 passed` | Exports, tipos y presentación mínima | `47 passed` |
| **4 · BookReviews** | ✔ | `7 failed`, *exit* `1` — ruta inexistente, con controles positivos | `7 passed` | Reutilización de filtros públicos | `54 passed` |
| **5 · Videos** | ✔ | `5 failed`, *exit* `1` — listado inexistente; el control positivo impide aceptar un GREEN por `404` universal | `5 passed` | Solo listado; **no** se creó detalle | `59 passed` |
| **6 · Projects** | ✔ | `7 failed`, *exit* `1` — listado y detalle inexistentes, con controles `published` positivos | `7 passed` | DTO y consultas mínimas | `66 passed` |
| **7 · Tags** | ✔ | `7 failed`, *exit* `1` — *endpoint* inexistente; los controles de etiqueta publicada descartan un falso GREEN por `404` o por vacío universal | `7 passed` | Cuatro ramas `EXISTS` explícitas con condición `published` | `73 passed` |
| **8 · Search** | ✔ | `12 failed`, *exit* `1` — *endpoint* y consulta inexistentes; controles `published` para los cuatro tipos y casos que distinguen el escape literal de `%` y `_` | `12 passed` | Unión tipada de cuatro ramas, orden estable, `RowMapping` explícito | `85 passed` |

La evolución de `app/api/public.py` se conservó como siete instantáneas —Posts; +Profile;
+BookReviews; +Videos; +Projects; +Tags; +Search—, que demuestran que el cableado fue
incremental y que ningún *slice* pudo apoyarse en un router que aún no le tocaba.

**Una transparencia adicional.** En BookReviews, el primer intento tras implementar quedó
en `1 failed / 6 passed`: una aserción de `featured=true` exigía erróneamente excluir otra
review destacada. Se corrigió **la aserción**, para expresar la combinación `tag + featured`
tal como está documentada. No se relajó `published-only` ni ningún otro requisito.

#### Qué se comparó, y cuándo

La comparación con la implementación *post-hoc* preservada se hizo **solo después** del
primer GREEN y del refactor de los seis *slices*, nunca antes. De los 42 archivos
productivos preservados, 15 resultaron *byte-identical* —la base TDD que estaba permitido
reutilizar— y 27 distintos por reconstrucción independiente. Las diferencias son de
estructura, brevedad de *docstrings* y tipado interno; **no hay ninguna diferencia
observable de contrato**, y **no apareció ningún comportamiento que la reconstrucción
hubiera dejado fuera**. No hubo, por tanto, ninguna incorporación posterior a la
comparación.

#### El *mutation testing* sigue siendo evidencia **complementaria**

Las mutaciones de §I.3 se repitieron sobre la implementación reconstruida y siguen
mordiendo: `posts` `published` → `5 failed / 23 passed`; `tags` `published` →
`3 failed / 4 passed`; `search` `published` → `3 failed / 9 passed`; escape de comodines de
`search` → `2 failed / 10 passed`, exactamente los dos discriminadores. Cada mutación se
restauró verificando el SHA-256 previo del archivo, y la regresión conjunta restaurada
volvió a `47 passed` con `git diff --check` limpio.

**Esto no sustituye al RED.** Un *mutation test* demuestra que la prueba **puede** fallar;
solo un RED anterior al código demuestra que la prueba **condujo** la implementación. Ahora
existen las dos cosas, y son cosas distintas.

#### Traslado al repositorio oficial

La implementación reconstruida se trasladó archivo a archivo al repositorio oficial y se
revalidó **allí** (§P). El laboratorio se conserva íntegro —reconstrucción, evidencia y
*backup* histórico— hasta que `Task/009` sea aprobada, fusionada y normalizada.

### I.6 Causa raíz y guarda para las tareas siguientes

**Causa raíz.** `app/api/public.py` importó los siete routers de una sola vez. A partir de
ese momento la aplicación no arrancaba hasta que los siete módulos existieran, y la
secuencia dejó de ser divisible: no había forma de observar el RED de un *slice* sin que
los demás estuvieran ya implementados. **El defecto fue de cableado, no de disciplina de
pruebas** — y por eso se pudo remediar reconstruyendo el cableado incremental.

**Guarda para `Task/010` en adelante.** Cuando una tarea añada varios *routers* o *slices*,
el agregador se construye **incrementalmente**:

1. registrar únicamente los *routers* ya implementados;
2. escribir el test del *slice* siguiente;
3. ejecutar y **observar el RED**, con al menos un control positivo que impida aceptar un
   falso GREEN por `404` o por conjunto vacío universal;
4. implementar lo mínimo suficiente;
5. registrar el *router* en el agregador;
6. ejecutar y observar el GREEN;
7. refactorizar y continuar con el *slice* siguiente.

Un agregador que importa todo de golpe convierte «la aplicación no arranca» en «ninguna
prueba puede ejecutarse», y eso hace **imposible** el RED por construcción.

---

## J. Visibilidad pública — comprobado por tipo

Cada tipo tiene su **propia** consulta (D-009-R), así que la comprobación se repite tipo
por tipo y no se da por buena por analogía.

| Tipo | `published` | `draft` | `archived` |
| --- | :---: | :---: | :---: |
| `Post` | **visible** | **invisible** | **invisible** |
| `BookReview` | **visible** | **invisible** | **invisible** |
| `Video` | **visible** | **invisible** | **invisible** |
| `Project` | **visible** | **invisible** | **invisible** |

Casos adicionales que cubren los agujeros no obvios:

- **Borrador previamente publicado.** Despublicar conserva `published_at` (B.8), así que
  una consulta que filtrara por «tiene fecha» lo dejaría escapar. Filtra por `status`, y
  hay prueba.
- **Etiqueta compartida** entre un publicado y un borrador: solo sale el publicado, en los
  cuatro tipos.
- **Catálogo de etiquetas:** una etiqueta usada solo por borrador o por archivado **no
  aparece**.
- **Búsqueda:** el término se siembra **solo** en el contenido oculto, de modo que
  cualquier resultado sería necesariamente una fuga.

---

## K. No filtración en los detalles

| Recurso | Inexistente | `draft` | `archived` |
| --- | --- | --- | --- |
| `Post` | `404` `resource_not_found` | **mismo** `404` | **mismo** `404` |
| `BookReview` | `404` `resource_not_found` | **mismo** `404` | **mismo** `404` |
| `Project` | `404` `resource_not_found` | **mismo** `404` | **mismo** `404` |

**No basta con que coincida el código.** Las pruebas comparan el **cuerpo completo** de
las dos respuestas, descartando solo `request_id`, que cambia en cada petición por diseño.
Un mensaje distinto bastaría para enumerar borradores probando slugs.

La consulta de detalle lleva el estado **en su condición**: un borrador ni siquiera se
carga. No hay un punto en el código donde exista la fila y se decida no devolverla.

---

## L. Paginación

| Aspecto | Resultado |
| --- | --- |
| `page` por defecto | `1` |
| `page_size` por defecto | `12`, documentado en OpenAPI |
| `page_size` máximo | `50` |
| Recorte | `page_size=550` → `200`, y la respuesta declara `page_size: 50` |
| Página fuera de rango | `page=99` → `200` con `items: []` y `total` correcto |
| `total` | Cuenta el conjunto **filtrado completo**: 5 filas con `page_size=2` → `total: 5` |
| `pages` | `5 / 2` → `3` |
| `total = 0` | `pages: 0`, no `1` |
| Orden estable | Con **todas** las fechas iguales, tres páginas de un conjunto de 5 devuelven 5 elementos distintos: ninguno repetido, ninguno perdido |

---

## M. Búsqueda

| Aspecto | Resultado |
| --- | --- |
| Alcance | **Solo publicado**, comprobado con el término sembrado únicamente en contenido oculto |
| Tipos | Los cuatro, cada resultado con su `type` |
| Subcadenas | `ocke` encuentra `Docker` — el motivo de elegir `ILIKE` |
| Mayúsculas | `docker`, `DOCKER` y `DoCkEr` dan el mismo resultado |
| Campos | `title` y `summary`; además `book_title` y `book_author`. **`content` no**, y hay prueba |
| Comodines | `%` y `_` se tratan como texto; un `%` literal **sí** se encuentra |
| Espacios | El término se recorta antes de buscar |
| Validación | `q` obligatorio, 2..100 tras recortar |
| Sin resultados | `200` con `items: []`, `total: 0`, `pages: 0` |
| Orden | `published_at DESC`, desempate `(type, slug)` |

---

## N. PostgreSQL real

- Base **`personal_blog_test`**, con la guarda *fail-closed* de `Task/005.6`/`005.7`
  activa: sufijo `_test` **y** marca `personal-blog:test-database` dentro de la base.
- **SQLite no se usó en ningún momento.**
- La guarda **no se debilitó**. El cliente HTTP de integración se deriva de
  `database_settings` y `sesion_de_pruebas`, ambas del resolutor verificado, y
  `tests/test_grafo_de_fixtures_de_integracion.py` lo comprueba recorriendo el grafo.
- Los cuatro módulos de integración nuevos y la *fixture* `cliente_de_la_api` se
  registraron en las guardas anti-tautología de esa prueba.

### Defecto encontrado en el propio harness

La *fixture* de integración comparte la sesión entre la prueba y la aplicación. Eso hacía
que los objetos recién creados siguieran en el *identity map* con sus colecciones ya
pobladas: **la API no llegaba a consultar PostgreSQL**. El `order_by` de una relación no se
aplicaba, la estrategia de carga explícita no se ejercitaba y una regresión de N+1 habría
pasado inadvertida porque no habría consultas que contar.

Se detectó porque la prueba del orden de los enlaces sociales falló: devolvía el orden de
inserción. **En producción no ocurre** —cada petición abre su propia sesión y siempre lee
de la base—, así que era un defecto de la prueba, no del código.

Corregido en el harness y no prueba a prueba: el cliente invalida el estado en memoria
**antes de cada petición**, de modo que toda prueba de integración lee de PostgreSQL como
lo hace una petición real. Se añadió además una guarda: la prueba de N+1 exige un mínimo de
consultas observadas, para que la igualdad que comprueba no pueda cumplirse por no haber
medido nada.

---

## O. Esquema físico

> **`Task/009` no modifica el esquema físico.**

No hay migración nueva. `alembic heads` → **`0002 (head)`**, la misma revisión que dejó
`Task/008`. Las migraciones existentes **no se tocaron**.

El motivo está razonado y documentado en
[`data-model.md` §8.1](../architecture/data-model.md): ningún índice B-tree sirve a un
`LIKE` con comodín inicial, y el que serviría exige `pg_trgm` —una extensión, prohibida por
T-02— o cambiar de mecanismo a `tsvector`. **Crear un índice que el planificador no usaría
es peor que no crearlo.** Queda escrito el disparador para revisarlo.

Por tanto **no se ejecutó el ritual de migración** (`upgrade`/`downgrade`/`upgrade`): no
hay migración nueva que validar. El ciclo M-04 de la revisión `0002` lo sigue cubriendo
`tests/integration/test_migrations.py`, que pasa.

---

## P. Resultados de las validaciones

Ejecutadas con los comandos reales del repositorio, **sobre el repositorio oficial y
después del traslado descrito en §I.5**, contra `personal_blog_test` en PostgreSQL real.

| Comando | Resultado | Exit code |
| --- | --- | :---: |
| `ruff check .` | `All checks passed!` | `0` |
| `ruff format --check .` | `148 files already formatted` | `0` |
| `mypy .` | `Success: no issues found in 146 source files` | `0` |
| `pytest tests/unit -q` | `100 passed` | `0` |
| `pytest tests/contract -q` | `188 passed` | `0` |
| `pytest -m integration -q` | `227 passed, 371 deselected` | `0` |
| `pytest -q -W error` | **`597 passed, 1 skipped`** | `0` |
| `pytest --cov -q` | `597 passed, 1 skipped` · **`app/` al 100 %** | `0` |
| `pip check` | `No broken requirements found.` | `0` |
| `alembic heads` | `0002 (head)` | `0` |

### Suite completa

| Métrica | Antes (`Task/008`) | Ahora | Δ |
| --- | ---: | ---: | ---: |
| Recolectadas | 251 | 598 | **+347** |
| Pasan | 250 | **597** | +347 |
| Fallan | 0 | **0** | — |
| Omitidas | 1 | **1** | — |
| Advertencias | 0 | **0** | — |

**Por qué la suite creció respecto de la primera ejecución de `Task/009`** (`555 passed`).
La remediación de §I.5 produjo **seis módulos de integración nuevos** —los que sí nacieron
antes del código— y los módulos *post-hoc* originales **no se eliminaron**: ambos conjuntos
tienen valor de regresión y la suite aprobada los incluye a los dos. El aumento es
`+42` pruebas de integración y **no** proviene de ningún cambio de comportamiento: los
recuentos de `unit` (`100`) y `contract` (`188`) son idénticos a los de la primera
ejecución, porque el contrato HTTP no se movió.

La única omisión es la preexistente y es **exactamente la misma**:
`tests/test_logging_utc.py:133 — time.tzset no existe en Windows`. Está justificada: es una
función que la biblioteca estándar no expone en esta plataforma.

**Cero advertencias nuevas.** La suite se ejecuta con `-W error`, así que una advertencia
sería un fallo.

### Cobertura

**100 % de `app/`**, ramas incluidas. No es el objetivo en sí —la cobertura es una señal,
no la especificación—, pero sí sirvió para encontrar algo real: mostró sin recorrer el
filtro `featured` de reviews, vídeos y proyectos, y el filtro `tag` de proyectos. Como cada
tipo tiene su propia consulta, ese último era un camino de fuga sin probar. Se añadieron
los casos.

---

## Q. Smoke HTTP

Contra la aplicación real (`app.main:app`) y PostgreSQL real, **solo lecturas**:

| Petición | Respuesta |
| --- | --- |
| `GET /health` | `200` `{"status":"ok",…}` |
| `GET /api/v1/profile` | `404` `resource_not_found` — la base no tiene perfil, y es el contrato |
| `GET /api/v1/posts` · `book-reviews` · `videos` · `projects` · `tags` | `200` `{"items":[],"page":1,"page_size":12,"total":0,"pages":0}` |
| `GET /api/v1/search?q=docker` | `200`, colección vacía |
| `GET /api/v1/posts/no-existe` | `404` `resource_not_found` |
| `GET /api/v1/videos/lo-que-sea` | `404` — la ruta no existe |
| `GET /api/v1/posts?foo=1` | `422` `validation_error` |
| `GET /api/v1/posts?status=draft` | `422` — `status` no es público |
| `GET /api/v1/posts?page=0` | `422` |
| `GET /api/v1/posts?sort=id` | `422` |

**No se insertó ningún dato para el smoke.** Un listado vacío con `200` es la respuesta
correcta cuando no hay contenido, y falsificar contenido para que la salida «se vea mejor»
no demostraría nada.

### Por qué el smoke no se hizo contra la base de desarrollo

`personal_blog` —la base cotidiana— está en la revisión **`0001`** y tiene **una sola
tabla**: la migración `0002` de `Task/008` nunca se aplicó ahí. Un smoke contra ella habría
fallado por falta de tablas, no por un defecto de la API.

**No la migré**, y la decisión es deliberada
([PROJECT_INSTRUCTIONS](../claude/PROJECT_INSTRUCTIONS.md), y §56 del prompt): avanzar el
esquema de la base de desarrollo es una operación sobre datos locales del usuario que no
pertenece al alcance de esta tarea. Los propietarios de poblar el entorno local son
`Task/022` (datos semilla) y, en producción, `Task/036`. **Queda como observación para el
usuario, no como acción ejecutada.**

Se comprobó después: `personal_blog` sigue en `0001`, intacta.

### Observación sobre `get_session`

Al preparar el smoke se confirmó que `get_session` resuelve la configuración **global** del
proceso, no la que recibe `create_app(settings=…)`. Es el diseño de `Task/005` —está
documentado en `session.py`— y **no es un defecto en producción**, donde hay un proceso y
una configuración. Se registra porque `Task/009` es la primera tarea cuyos endpoints usan
realmente esa dependencia, y porque explica por qué el harness de integración sustituye
`get_session` en lugar de la configuración.

---

## R. Entorno local

Comprobado de forma **no destructiva**:

| Servicio | Estado |
| --- | --- |
| `backend` | `Up (healthy)` |
| `frontend` | `Up (healthy)` |
| `traefik` | `Up (healthy)` |
| `postgres` | `Up (healthy)` |
| `minio` | `Up (healthy)` |
| `portainer` | `Up` |

**3 volúmenes antes y 3 después; 0 eliminados.** No se ejecutó `down -v`, ni
`volume rm`, ni `volume prune`, ni `system prune`. No se tocó Farm Tech.

**El contenedor `backend` sirve la imagen anterior a `Task/009`** y no se reconstruyó: su
base de datos es `personal_blog`, que está en `0001`, así que un smoke a través del
contenedor habría medido el estado de la base y no el de la API. El smoke se hizo contra la
aplicación real por el camino que sí demuestra algo.

---

## S. Scope guard

| Elemento | Estado |
| --- | :---: |
| API pública de solo lectura | **SÍ** |
| Lectura contra PostgreSQL real | **SÍ** |
| Paginación · Filtros · Búsqueda | **SÍ** |
| Pruebas de contrato | **SÍ** |
| API administrativa | **NO** |
| Autenticación | **NO** |
| `ObjectStorage`, MinIO SDK, S3, boto3 | **NO** |
| Render o sanitización de Markdown | **NO** |
| Auditoría de lecturas | **NO** |
| Frontend | **NO** — sin rama y sin cambios |
| Cloud, Terraform, Grafana, VPS | **NO** |
| Migraciones nuevas | **NO** |
| Dependencias nuevas | **NO** — ni una |

**No se añadió ninguna dependencia.** FastAPI, Pydantic y SQLAlchemy resolvían todo:
la paginación no necesitaba biblioteca y la búsqueda se resuelve con PostgreSQL.

---

## T. Archivos

### `personal-blog-backend`

**Creados (34):** `app/api/query_params.py` · `app/api/filtros_publicos.py` ·
`app/api/public.py` · `app/shared/lectura.py` · `app/shared/errors/schemas.py` ·
`app/shared/pagination/` (4 archivos) · `queries.py` en `posts`, `book_reviews`, `videos`,
`projects`, `profile`, `tags` · `presentation/` en `posts`, `book_reviews`, `videos`,
`projects`, `profile`, `tags`, `media` · `app/modules/search/` completo ·
`tests/contract/` (4 archivos) · `tests/integration/datos.py` y 4 módulos
`test_api_*.py` · `tests/unit/test_paginacion.py` y `test_tiempo_de_lectura.py`.

**Creados por la remediación (6):** los módulos de integración escritos **antes** del
código en el laboratorio (§I.5). Se trasladaron al repositorio oficial con nombres
orientados al dominio, para que `tests/integration/` conserve su convención `test_api_*` y
no arrastre vocabulario del proceso histórico. El renombre es posterior a la escritura y
**no** altera que estos tests precedieron a la implementación:

| Archivo de evidencia TDD (laboratorio) | Archivo final (`personal-blog-backend`) |
| --- | --- |
| `tests/integration/test_remediacion_profile.py` | `tests/integration/test_api_perfil_publico.py` |
| `tests/integration/test_remediacion_book_reviews.py` | `tests/integration/test_api_reviews_publicas.py` |
| `tests/integration/test_remediacion_videos.py` | `tests/integration/test_api_videos_publicos.py` |
| `tests/integration/test_remediacion_projects.py` | `tests/integration/test_api_proyectos_publicos.py` |
| `tests/integration/test_remediacion_tags.py` | `tests/integration/test_api_etiquetas_publicas.py` |
| `tests/integration/test_remediacion_search.py` | `tests/integration/test_api_busqueda_publica.py` |

Los cuatro módulos `test_api_*.py` originales **se conservan sin tocar**: en el laboratorio
se habían renombrado a `test_paridad_original_*` para poder distinguirlos, y al trasladarlos
recuperaron su nombre oficial. Su contenido es *byte-identical* al de la primera ejecución.
No se eliminó ninguna prueba: los dos conjuntos tienen valor de regresión.

**Modificados (4):**

| Archivo | Cambio |
| --- | --- |
| `app/main.py` | Monta los routers públicos bajo el prefijo versionado; descripción de OpenAPI actualizada |
| `tests/integration/conftest.py` | *Fixture* `cliente_de_la_api`, derivada del resolutor verificado |
| `tests/test_grafo_de_fixtures_de_integracion.py` | Módulos y *fixture* nuevos añadidos a las guardas anti-tautología; tras la remediación, los seis módulos nuevos también quedan registrados en `MODULOS_CONOCIDOS` |
| `tests/test_openapi.py` | Expectativa actualizada: ver abajo |

**Ningún archivo eliminado. Ninguna migración tocada.**

### La única expectativa de prueba modificada

`tests/test_openapi.py` afirmaba `list(document["paths"]) == ["/health"]`. La tarea cuyo
objeto es publicar endpoints los añade, así que la expectativa cambió **por un cambio de
requisito** — el primero de los cuatro supuestos que BACKEND_TESTING_STRATEGY §9 admite.

**No se debilitó.** Se sustituyó por una afirmación que sigue protegiendo lo mismo —que no
se documente lo que no existe— sobre lo que corresponde a las tareas siguientes: `/ready`
(`Task/017`) y los endpoints administrativos (`Task/011`, `Task/012`). La comprobación
**exacta** del conjunto de rutas se hace ahora en `tests/contract/test_openapi_publica.py`,
contra una lista escrita a mano: derivarla de la aplicación haría que la prueba se adaptase
sola a cualquier ruta nueva, que es justo lo que no debe hacer.

### `personal-blog-infra`

| Archivo | Cambio |
| --- | --- |
| `docs/tasks/TASK-009-public-api.md` | **Creado** |
| `docs/task-reports/TASK-009-report.md` | **Creado** — este archivo |
| `docs/architecture/api-contracts.md` | §5, §6 y §11: cierre de las decisiones que el propio documento delegaba en `Task/009` |
| `docs/architecture/data-model.md` | §8.1 nueva (mecanismo de búsqueda e índices); §10 (deuda) y §6 (invariante 19) actualizadas |
| `docs/project-management/STATUS.md` | Tarea en validación; el avance **no** se mueve |
| `docs/project-management/ROADMAP.md` | Estado de `Task/009`; el recuento **no** se mueve |
| `docs/stages/STAGE-03-domain-and-backend.md` | Estado de `Task/009` y criterio de salida de visibilidad |

`CONTENT_MODEL.md` **no se reescribió**: ninguna decisión conceptual cambió.
`open-decisions.md` **no se tocó**: no registra ninguna decisión cuyo dueño sea `Task/009`.

### `personal-blog-frontend`

**Sin rama, sin cambios, sin tocar.** `git status` vacío en `main`.

---

## U. Estado Git — pre-approval

| Comprobación | backend | infra | frontend |
| --- | :---: | :---: | :---: |
| Rama activa | `Task/009-API-Publica` | `Task/009-API-Publica` | `main` |
| Nació de `main` | **SÍ** | **SÍ** | — |
| Commits sobre `main` | **0** | **0** | **0** |
| Staging | **vacío** | **vacío** | **vacío** |
| *Push* de la rama Task | **NO** | **NO** | — |
| Merge hacia `dev` | **NO** | **NO** | — |
| Pull request | **NO** | **NO** | — |
| Ramas Task en `origin` | **ninguna** | **ninguna** | **ninguna** |

Todos los cambios están **sin commit**, en el árbol de trabajo, como exige el flujo previo
a la aprobación.

---

## V. Riesgos y deuda

| # | Riesgo | Mitigación aplicada |
| --- | --- | --- |
| 1 | Una consulta futura olvida la condición de publicación | La condición vive **en la consulta**, no en el router. Caso negativo por tipo y por endpoint, y capacidad de fallar verificada por mutación |
| 2 | Rechazar parámetros desconocidos rompe un cliente que añade parámetros de analítica | Coste **aceptado y registrado** en D-009-C. El frontend no debe reenviarlos |
| 3 | La derivación de parámetros admitidos usa la estructura interna de FastAPI | Guarda explícita: si dejara de funcionar, la API rechazaría todo y una prueba se pone roja en lugar de quedarse verde |
| 4 | `ILIKE` deja de bastar al crecer el contenido | Disparador de revisión escrito en `data-model.md` §10, con el camino (`tsvector` + GIN, ambos del núcleo) |
| 5 | N+1 en listados con etiquetas y portada | Carga explícita y prueba que compara el número de consultas entre 2 y 10 filas, con guarda anti-tautología |

**Ningún riesgo nuevo** para el registro global de `STATUS.md`.

| Deuda que queda | Dueño |
| --- | --- |
| Las referencias a medios no llevan campo de acceso | `Task/010` |
| El mecanismo de búsqueda, revisable con su disparador | Revisión futura |
| `reading_time_minutes` se calcula al servir; su presentación es del frontend | `Task/014` |
| La base de desarrollo local sigue en `0001` y sin datos | `Task/022` |

---

## W. Pasos de validación para el usuario

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-backend

# 1. La rama nacio de main y no hay nada publicado
git branch --show-current                 # Task/009-API-Publica
git rev-list --count main..HEAD           # 0
git status --short                        # cambios sin commit, staging vacio

# 2. Calidad
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m ruff format --check .
.\.venv\Scripts\python -m mypy .

# 3. Suite completa, con la base de integracion
$env:PERSONAL_BLOG_TEST_DATABASE_URL = "postgresql://<usuario>:<clave>@127.0.0.1:55432/personal_blog_test"
.\.venv\Scripts\python -m pytest -q -W error      # 597 passed, 1 skipped

# 4. El frontend no se ha tocado
git -C ..\personal-blog-frontend status --short   # vacio
```

Para ver la API en marcha, sin escribir nada en ninguna base:

```powershell
$env:BLOG_DATABASE_URL = "postgresql://<usuario>:<clave>@127.0.0.1:55432/personal_blog_test"
.\.venv\Scripts\python -m uvicorn app.main:app --port 8100
# Abrir http://127.0.0.1:8100/docs
```

---

## X. Criterios de aceptación

| # | Criterio | Estado |
| --- | --- | :---: |
| 1–10 | Los diez endpoints públicos implementados | ✔ |
| 11 | No se inventó `/videos/{slug}` | ✔ |
| 12 | Toda colección paginada | ✔ |
| 13 | Página fuera de rango → `200` vacío | ✔ |
| 14 | `page_size` excedido se recorta | ✔ |
| 15 | Parámetros inválidos → `422` con el envelope vigente | ✔ |
| 16 | Orden por defecto `published_at DESC` | ✔ |
| 17 | Orden determinista | ✔ |
| 18 | `sort` con lista cerrada | ✔ |
| 19 | `tag` sobre relaciones reales | ✔ |
| 20 | `featured` con semántica documentada | ✔ |
| 21–23 | Búsqueda, listados y detalles solo ven `published` | ✔ |
| 24 | `draft` y `archived` no enumerables | ✔ |
| 25–26 | DTO explícitos, sin campos internos | ✔ |
| 27 | Frontera de medios con `Task/010` respetada | ✔ |
| 28 | Markdown no se renderiza aquí | ✔ |
| 29 | Contratos HTTP cubiertos test-first | **✔ tras remediación** — ver §I.2 y §I.5 |
| 30–31 | Consultas reales sobre PostgreSQL real; nunca SQLite | ✔ |
| 32 | Suite completa verde | ✔ |
| 33 | OpenAPI representa exactamente `Task/009` | ✔ |
| 34–36 | Sin API administrativa, sin auth, sin `ObjectStorage` | ✔ |
| 37 | Frontend intacto | ✔ |
| 38 | Documentación durable coherente | ✔ |
| 39 | Sin commit, *push* ni PR antes de la aprobación | ✔ |
| 40 | `Task/010`, `011` y `012` siguen sin iniciar | ✔ |

**El criterio 29 tiene dos momentos, y los dos importan.**

**Primera ejecución: Parcial.** El contrato HTTP transversal —paginación, validación,
parámetros desconocidos, *envelope* de error— y el *slice* de artículos sí se construyeron
test-first con RED registrado. Los seis recursos restantes **no**, por lo explicado en
§I.2. Se marcó Parcial a propósito: declararlo cumplido entonces habría sido falso, y el
criterio B-2 de la
[Definition of Done](../project-management/DEFINITION_OF_DONE.md) existe precisamente para
que eso no se pueda dar por bueno en silencio.

**Remediación: los seis *slices* afectados se reconstruyeron genuinamente test-first**
—especificación previa, RED observado sobre código inexistente, GREEN y refactor— **antes
de aprobar o publicar la tarea**, y el resultado se revalidó en el repositorio oficial
(§I.5, §P).

**Estado final del criterio 29: CUMPLIDO para la implementación candidata a aprobación.**

La distinción no es cosmética. **`Task/009` no cumplió TDD a la primera**; lo que se somete
a aprobación es la implementación reconstruida, no la *post-hoc*. Esta última se conserva
únicamente como *backup* histórico y **no** es la que se pretende aprobar.

---

## Y. Gobierno

**Estado duradero** de la tarea ([WORKFLOW §6.1](../project-management/WORKFLOW.md)):

| Campo | Valor |
| --- | --- |
| `Task/009` | **Aprobada** el 2026-08-27 |
| Expresión de aprobación | `approved: Task/009-API-Publica` |
| Implementación aprobada | La **reconstruida test-first** (§I.5), no la *post-hoc* |
| Criterio 29 | **Cumplido para la implementación aprobada**; **no** en la primera ejecución |
| Decisiones **D-009-A** a **D-009-R** | **Vigentes** |
| Avance global | **9 / 41 — 22 %** |
| ETAPA 03 | **2 / 5 — 40 %** |
| `Task/010` | **Pendiente, no iniciada.** Es la siguiente del roadmap |
| `Task/011`, `Task/012` | **Pendientes, no iniciadas** |

**Estado de Git: observación fechada, no estado vigente.** Los contadores de abajo son
**transitorios** por definición —el flujo de cierre los cambia en cuanto hay aprobación—,
así que se registran como lo que son: lo observado al terminar la tarea.

> *Observado el 2026-08-27, **antes** de la aprobación:* en `personal-blog-backend` y
> `personal-blog-infra`, `git rev-list --count main..HEAD` = **0**, staging **vacío**,
> `git ls-remote --heads origin "Task/*"` **sin resultados** y `gh pr list` **sin pull
> requests** para `Task/009`. En `personal-blog-frontend`, `main` limpio y sin rama Task.
> Es la evidencia de que el trabajo —incluida la remediación de §I.5— permaneció sin
> confirmar hasta la aprobación.
>
> El flujo de cierre —commit, integración en `dev`, publicación y pull request
> `Task/009-API-Publica → main`— se ejecutó **después** de recibir
> `approved: Task/009-API-Publica`. Su resultado es estado transitorio y **no se registra
> aquí**: se consulta en Git y GitHub. **Aceptar y fusionar el pull request es
> responsabilidad exclusiva del usuario.**

## Z. Próxima tarea

`Task/010-Almacenamiento-Compatible-S3` — interfaz `ObjectStorage`, `MinIOStorage` y el
código de `S3Storage`, con pruebas de contrato comunes y sin AWS real. Permanece
**Pendiente y no iniciada**, y **no se inicia** hasta que el usuario fusione el pull request
de `Task/009` y se complete la normalización `main → dev`.

Se lleva además la guarda de §I.6: el agregador de routers se construye **incrementalmente**,
un *slice* por vez, para que el RED sea observable.
