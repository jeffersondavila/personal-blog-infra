# TASK-008 — Modelo de Datos — Reporte

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/008-Modelo-de-Datos` |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las 41 |
| **Estado** | **Aprobada** el 2026-08-25 por jeffersondavila |
| **Fecha** | 2026-08-25 · **revisión correctiva pre-approval** el 2026-08-25 |
| **Repositorios modificados** | `personal-blog-backend` · `personal-blog-infra` |
| **Repositorio no modificado** | `personal-blog-frontend` — sin rama, sin cambios |
| **Ficha** | [TASK-008](../tasks/TASK-008-data-model.md) |
| **Modelo físico** | [data-model.md](../architecture/data-model.md) |

---

## 1. Estado inicial verificado

Reconstruido con Git, no leído de ningún documento
([WORKFLOW §6.1](../project-management/WORKFLOW.md), regla 3).

| Repositorio | `main` | `main == origin/main` | Árbol limpio | Ramas Task |
| --- | --- | :---: | :---: | :---: |
| `personal-blog-backend` | `2290a9fbb726f97f6d1cbdb5e4c6b1f1ce147e4c` | sí | sí | 0 |
| `personal-blog-infra` | `b23ad66d171dba2add42c6513f770d9f1de8e15b` | sí | sí | 0 |
| `personal-blog-frontend` | `fd62f221707591a984cf0fb51a03ea339380ab35` | sí | sí | 0 |

Precondiciones confirmadas en la documentación vigente: `Task/007` **Aprobada**, ETAPA 02
**completada** (3/3), avance **7/41**, ETAPA 03 **0/5**, `Task/008` **Pendiente**.
Alembic con cabeza fundacional `0001`; base de pruebas `personal_blog_test` provisionada y
**marcada**; `personal_blog` **sin** la marca; `app/modules` vacío por decisión de
`Task/005`.

## 2. Ramas

| Repositorio | Rama | Base | `HEAD == main` al crearla | `main..HEAD` |
| --- | --- | --- | :---: | :---: |
| backend | `Task/008-Modelo-de-Datos` | **`main`** `2290a9fb…` | sí | **0** |
| infra | `Task/008-Modelo-de-Datos` | **`main`** `b23ad66d…` | sí | **0** |

**Ninguna rama nació de `dev`.** El frontend no recibió rama: la tarea no lo modifica.

## 3. Fuentes canónicas leídas

`CLAUDE.md` · `docs/claude/PROJECT_INSTRUCTIONS.md` · `WORKFLOW.md` · `STATUS.md` ·
`ROADMAP.md` · `DEFINITION_OF_DONE.md` · `TASK_TEMPLATE.md` ·
`BACKEND_TESTING_STRATEGY.md` · `STAGE-03-domain-and-backend.md` · `MVP_SCOPE.md` ·
`USER_FLOWS.md` · `CONTENT_MODEL.md` · `ADR-004` · `ADR-005` · `software-architecture.md` ·
`api-contracts.md` · `non-functional-requirements.md` · `security-boundaries.md` (índice y
§7–§8) · `open-decisions.md` (registro completo de D-01 a D-20) ·
`runbooks/local-environment.md` §9.

En `personal-blog-backend`: `README.md`, `CONTRIBUTING.md`, `pyproject.toml`,
`requirements*.txt`, `app/` completo, `alembic.ini`, `alembic/env.py`,
`alembic/script.py.mako`, `alembic/versions/`, `tests/` completo.

## 4. Decisiones de diseño

Tabla completa con alternativas y justificación en
[`data-model.md`](../architecture/data-model.md) §3. Resumen:

| Decisión | Elegida | Razón en una línea |
| --- | --- | --- |
| Clave primaria | **UUID v4**, generado en Python | La referencia polimórfica de auditoría necesita identificadores que no colisionen entre tipos |
| *Slug* | `VARCHAR(160)`, `UNIQUE` por tabla | Unicidad **por tipo** sin esfuerzo; formato y generación son de `Task/012` |
| Estados | `VARCHAR` + `CHECK` | Un `ENUM` nativo es donde más fácil se rompe el `downgrade` (M-04) |
| `rating` | Entero **1..5**, nulo permitido | Escala reconocible; exigirla al publicar es de `Task/012` |
| `project_status` | `active` · `paused` · `completed` | Los ejemplos del documento conceptual; nada de flujo inventado |
| `social_links` | **Tabla dependiente** | Registro de forma fija con orden restringible; `JSONB` no puede prometerlo |
| `technologies` | **`JSONB`** | Lista que solo se muestra; nadie consulta por tecnología en el MVP |
| Marcas de tiempo | `TIMESTAMPTZ`, reloj de la base | Un solo reloj; `published_at` sí lo fija el caso de uso |
| *Singleton* `Profile` / `Administrator` | Cerrojo booleano único | SQL corriente; garantiza **como máximo uno**, no "exactamente uno" |
| Referencia polimórfica de auditoría | **Sin clave foránea** | Un evento debe sobrevivir a lo que describe |
| Borrado de medios | **`ON DELETE RESTRICT`** + índice | Invariante 5, infranqueable; el mensaje útil es de `Task/010` |
| Etiquetado | 4 puentes, PK compuesta, `CASCADE` | Rechaza duplicados y desasocia sin borrar contenido |
| `reading_time`, `thumbnail_url` | **No se persisten** | Son derivables; persistirlos crea estado que caduca |
| Superentidad `Content` | **Descartada** | Los cuatro tipos tienen semántica distinta |

**Todas quedan marcadas como `Propuesta — pendiente de aprobación`.**

## 5. Evidencia RED → GREEN → REFACTOR

Siete *slices*. En ninguno se escribió implementación antes que su prueba.

> **Por qué el RED del dominio es `NotImplementedError` y no `ImportError`.**
> [`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md) §5.2
> exige que el fallo sea **la razón esperada**, y prohíbe expresamente el `ImportError`. Por
> eso cada *slice* de dominio crea primero el esqueleto —clase, firma y
> `raise NotImplementedError`— y **después** la prueba: así el rojo dice "el comportamiento
> no está", no "el archivo no existe".

### Slice 1 — Ciclo de vida de `Post` (dominio)

| Fase | Detalle |
| --- | --- |
| Test escrito | `tests/unit/test_ciclo_de_vida_de_articulos.py` (15 casos, A-01 a A-15) |
| Comando RED | `pytest tests/unit/test_ciclo_de_vida_de_articulos.py -q` |
| **Resultado RED** | **15 failed** |
| Razón del fallo | `NotImplementedError: Task/008: estado inicial sin implementar` — `app/modules/posts/domain/publication.py:74` |
| Implementación | Invariante `published ⇒ published_at`, `draft()`, `restore()`, `publish()`, `unpublish()`, `archive()` |
| Comando GREEN | el mismo |
| **Resultado GREEN** | **15 passed** |
| Refactor | **No necesario.** El diseño resultante ya es el mínimo: un *dataclass* congelado y tres transiciones guardadas |

### Slice 2 — Ciclo de vida y valoración de `BookReview` (dominio)

| Fase | Detalle |
| --- | --- |
| Tests escritos | `test_ciclo_de_vida_de_reviews.py` (15), `test_valoracion_de_reviews.py` (16, B-01 a B-09) |
| **Resultado RED** | **30 failed, 1 passed** |
| Razón del fallo | `NotImplementedError: Task/008: validacion de tipo sin implementar` — `rating.py:72` |
| **La prueba que ya pasaba** | `test_la_escala_declarada_es_de_uno_a_cinco`. **Investigada, como exige §5.2:** no comprueba comportamiento, comprueba que las constantes `RATING_MINIMO`/`RATING_MAXIMO` valen 1 y 5, y esas constantes son **declarativas** y formaban parte del esqueleto. Se conserva porque fija por escrito la escala que `Task/008` cierra, pero **no cuenta como evidencia de ciclo**: la evidencia son los 30 casos que sí fallaron |
| Implementación | Rango en `__post_init__`; `Rating.of()` valida el tipo y rechaza `bool` explícitamente |
| **Resultado GREEN** | **46 passed** (acumulado de `tests/unit`) |
| Refactor | **No necesario** |

### Slice 3 — `Video` y `Project`: ciclo **sin** despublicación (dominio)

| Fase | Detalle |
| --- | --- |
| Test escrito | `test_ciclo_de_vida_sin_despublicacion.py`, parametrizado sobre los dos tipos (22 casos, incluidos A-16 y A-17) |
| **Resultado RED** | **22 failed** |
| Razón del fallo | `NotImplementedError` — `app/modules/videos/domain/publication.py:54` |
| Implementación | Mismo ciclo **sin** `unpublish`. La prohibición se expresa por **ausencia del método**, no con una comprobación que falle |
| **Resultado GREEN** | **68 passed** (acumulado) |
| Refactor | **No necesario** |

### Slice 3b — Independencia del dominio (regresión de un defecto real)

Este *slice* no estaba planificado: lo abrió un defecto encontrado al escribir el
Slice 1.

| Fase | Detalle |
| --- | --- |
| Defecto | `app/shared/errors/__init__.py` reexportaba `register_error_handlers`, que **importa FastAPI**. Cualquier módulo de dominio que importara una excepción del paquete cargaba el framework entero, rompiendo la regla de dependencias de ADR-004 **sin que ningún import lo delatara** |
| Test escrito | `tests/unit/test_independencia_del_dominio.py` — importa cada paquete `domain` en un intérprete limpio y mira `sys.modules` |
| Comando RED | con el import defectuoso reintroducido a propósito |
| **Resultado RED** | `AssertionError: importar el dominio [...] cargo ['fastapi', 'starlette']` |
| Corrección | El paquete exporta solo excepciones; `app/main.py` importa los manejadores de su módulo |
| **Resultado GREEN** | **3 passed** |
| Guarda anti-tautología | `test_la_comprobacion_detecta_de_verdad_una_dependencia_prohibida` importa `app.shared.database` y **exige** ver `sqlalchemy`: si el subproceso o la detección se rompieran, la prueba principal sería decorativa |

### Slice 4 — Esquema de contenido y *singletons* (PostgreSQL real)

| Fase | Detalle |
| --- | --- |
| Tests escritos | `test_esquema_de_contenido.py` (matriz C), `test_singletons.py` (matriz F) |
| **Resultado RED** | **31 failed, 1 passed** |
| Razón del fallo | `psycopg.errors.UndefinedTable: relation "profiles" does not exist` — el esquema **no existe**, así que ninguna de las garantías probadas se cumple |
| **La prueba que ya pasaba** | `test_un_articulo_sin_titulo_se_rechaza`. **Investigada:** aceptaba `(IntegrityError, DBAPIError)`, y `UndefinedTable` **es** un `DBAPIError`: la aserción era demasiado laxa y habría pasado por el motivo equivocado. Se estrechó a `IntegrityError`, que es lo que produce una violación de `NOT NULL` |
| Implementación | *Mixins* técnicos, tipo enumerado persistido, 9 modelos ORM, migración `0002` |
| **Resultado GREEN** | **33 passed**, `-W error`, **0 advertencias** |
| Refactor | **Sí, y necesario.** Ver §6, hallazgos 5 y 6 |

### Slice 5 — Relaciones: etiquetado y medios (PostgreSQL real)

| Fase | Detalle |
| --- | --- |
| Tests escritos | `test_relaciones_de_etiquetas.py` (matriz D), `test_politica_de_medios.py` (matriz E) |
| **Resultado RED** | **11 failed, 7 passed** |
| Razón del fallo | `UndefinedColumn: column "cover_id" of relation "posts" does not exist` y `UndefinedTable: relation "post_tags" does not exist` |
| **Las 7 que ya pasaban** | Comprueban garantías **ya entregadas en el Slice 4** —unicidad de `tags.slug` y de `object_key`, tamaño y dimensiones positivos, ausencia de columna binaria— y quedaron aquí por afinidad temática, no por ser comportamiento nuevo |
| Implementación | 4 tablas puente con PK compuesta y `CASCADE`; `cover_id`/`thumbnail_id`/`photo_id` con `RESTRICT` e índice; migración regenerada |
| **Resultado GREEN** | **67 passed** en `tests/integration` |
| Refactor | Las cuatro tablas puente se construyen desde **una sola definición** (`_tabla_de_asociacion`), para que no puedan divergir por descuido |

### Slice 6 — Auditoría (PostgreSQL real), con **dos** rojos

| Fase | Detalle |
| --- | --- |
| Test escrito | `test_auditoria.py` (matriz G) |
| **RED 1** | **9 failed, 1 passed** — `UndefinedTable: relation "audit_events" does not exist` |
| Implementación 1 | Modelo `AuditEvent` y migración regenerada |
| **RED 2** | **2 failed, 8 passed** — `DID NOT RAISE AuditEventIsImmutableError`. La tabla ya existía; lo que **seguía sin existir** era la inmutabilidad |
| Implementación 2 | Guardas `before_update` y `before_delete` en el *mapper* |
| **Resultado GREEN** | **77 passed** en `tests/integration` |
| Refactor | **No necesario** |

> El segundo rojo es la parte que más importa de este *slice*: separa "la tabla no está" de
> "la garantía no está", y demuestra la segunda por sí sola.

### Slice 7 — Inspección física y ausencia de *drift*

| Fase | Detalle |
| --- | --- |
| Test escrito | `test_esquema_fisico.py` (matriz H, 11 casos) |
| **Resultado primera ejecución** | **11 passed** |
| **Declarado sin rodeos** | Estas pruebas **no demostraron un rojo previo**, y no lo pretenden: verifican el contrato que los *slices* 4 a 6 ya construyeron bajo RED. Es el caso que [`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md) §4 contempla para migraciones estructurales, donde la prueba correcta es una **validación de integración**, no un ciclo unitario. Su valor es de **regresión**, no de especificación |
| Guarda anti-tautología | Se **demostró** que la detección de *drift* no es decorativa: al añadir una columna al modelo sin migrarla, la prueba falló con `[('add_column', None, 'tags', Column('columna_intrusa_de_prueba', …))]`. Retirada la columna, volvió a verde |
| Refactor | **No necesario** |

### Slice 8 — Borrador mínimo (revisión correctiva pre-approval)

Un defecto **funcional** encontrado en la revisión, **después** de la primera declaración
`Lista para validación`. Se registra tal cual: la trazabilidad de cuándo se detecta algo
vale más que la apariencia de haberlo hecho bien a la primera.

**El defecto.** USER_FLOWS.md B.2 crea un borrador con **solo** título y slug. Pero el
esquema exigía `book_reviews.book_title`, `book_reviews.book_author`, `videos.provider` y
`videos.video_url`. Crear un borrador de review o de vídeo era **imposible** sin inventar
un autor o una URL que nadie había escrito. El principio ya estaba bien aplicado a
`rating`; no se había aplicado de forma consistente al resto.

| Fase | Detalle |
| --- | --- |
| Test escrito | `tests/integration/test_borrador_minimo.py` (5 casos, matriz I) |
| Comando RED | `pytest tests/integration/test_borrador_minimo.py -q` |
| **Resultado RED** | **3 failed, 2 passed** — `Post` y `Project` ya lo cumplían |
| Razón exacta (`BookReview`) | `psycopg.errors.NotNullViolation: null value in column "book_title" of relation "book_reviews" violates not-null constraint` |
| Razón exacta (`Video`) | `psycopg.errors.NotNullViolation: null value in column "provider" of relation "videos" violates not-null constraint` |
| Razón exacta (guarda estructural) | `estas columnas obligan a inventar un valor al crear un borrador: {'book_reviews': ['book_author', 'book_title'], 'videos': ['provider', 'video_url']}` |
| Implementación | Las cuatro columnas pasan a admitir nulo, en el modelo ORM y en la **misma revisión `0002`** — la tarea no está comprometida, así que no procede una `0003` |
| **Resultado GREEN** | **5 passed** |
| Refactor | **No necesario** |

**No se añadió ningún default de relleno.** Ni `"pendiente"`, ni `"N/A"`, ni una URL
ficticia: eso habría puesto las pruebas en verde sin arreglar nada, porque el defecto es
justamente que el esquema **obligaba** a inventar el valor.

**Tampoco se añadió un `CHECK` condicional** del estilo `status <> 'published' OR
book_title IS NOT NULL`. Ninguna fuente canónica vigente lo exige, y qué campos hacen falta
**para publicar** es validación de publicación (B.7), propiedad de `Task/012`.

**La guarda que impide la reaparición** (`I-05`) recorre las columnas reales de los cuatro
modelos en lugar de una lista escrita a mano: una columna `NOT NULL` nueva entra en la
comprobación por el hecho de existir.

#### Barrido completo, no solo los cuatro campos señalados

Se auditó **toda** columna `NOT NULL` de los cuatro tipos publicables contra la pregunta
*"¿existe este valor en el momento de B.2?"*. Resultado: además de las cuatro corregidas,
**ninguna otra** falla la prueba. Lo que queda obligatorio es exactamente lo que B.2
proporciona —`id`, `slug`, `title`— más defaults **semánticamente reales**: `draft`,
`false`, `''`, `'active'`, `'[]'` y `now()`. Matriz completa en
[`data-model.md`](../architecture/data-model.md) §4.4.1.

## 6. Hallazgos corregidos durante la tarea

Seis defectos reales. **Ninguno se resolvió debilitando una prueba.**

| # | Hallazgo | Cómo salió | Corrección | Regresión |
| --- | --- | --- | --- | --- |
| 1 | El dominio cargaba FastAPI al importar una excepción | Al escribir el Slice 1 | `app/shared/errors/__init__.py` exporta solo excepciones | `test_independencia_del_dominio.py` |
| 2 | `alembic/script.py.mako` no emitía los imports de dialecto de `--autogenerate` | Primera migración con `JSONB`: habría fallado con `NameError` | Marcador `${imports}` en la plantilla | El propio ciclo de migraciones |
| 3 | `test_la_base_declarativa_no_declara_todavia_ninguna_tabla` (de `Task/005`) afirmaba `Base.metadata.tables == {}` | Se puso roja al aparecer la primera tabla legítima | **El requisito cambió** ([§9.1](../project-management/BACKEND_TESTING_STRATEGY.md)): sustituida por una afirmación que no caduca. Es el mismo defecto de diseño que `Task/005.6` ya tuvo que corregir en la prueba de migraciones | `test_la_base_declarativa_reune_las_tablas_del_modelo` |
| 4 | El descubrimiento de fixtures del harness usaba `hasattr`, y **`sqlalchemy.func` responde a cualquier atributo**: importarlo en un módulo de integración creaba una "fixture" llamada `func` que no pasaba por la guarda | La suite se puso roja por un import correcto | Se exige además que la marca provenga de pytest. La guarda anti-tautología existente sigue impidiendo que la condición excluya fixtures reales | `test_la_inspeccion_encuentra_las_fixtures_del_harness` |
| 5 | `test_actualizar_una_fila_avanza_su_marca_de_modificacion` fallaba | `now()` en PostgreSQL es la hora de **inicio de la transacción**: crear y editar dentro de una misma transacción comparten marca | **Error demostrado en la prueba**, no en el código: su premisa era irreal. Se partió en dos —una comprueba que dentro de una transacción coinciden; otra edita en **otra transacción**, que es lo que ocurre de verdad—. Se descartó `clock_timestamp()` por ser propio de PostgreSQL (T-02) | Las dos pruebas quedan en la suite |
| 6 | La sesión transaccional del harness emitía `SAWarning: transaction already deassociated from connection` | `pytest -W error`, que el proyecto exige en verde | `join_transaction_mode="create_savepoint"`: la sesión trabaja dentro de un `SAVEPOINT` y la transacción externa sigue siendo de la fixture | La suite completa con `-W error` |
| 7 | Dos pruebas esperaban el rechazo en el `flush` posterior | El `execute()` directo viaja al motor en el acto | **Error demostrado en la prueba.** Expectativa corregida al punto donde la sentencia se envía | — |

### 6.1 Hallazgos de la revisión correctiva pre-approval

Cuatro más, encontrados **después** de la primera declaración `Lista para validación`. Se
dejan registrados con esa cronología a propósito.

| # | Hallazgo | Gravedad | Corrección |
| --- | --- | --- | --- |
| 8 | **El esquema contradecía USER_FLOWS.md B.2**: exigía `book_title`, `book_author`, `provider` y `video_url` al crear un borrador | **Bloqueante** | Las cuatro columnas admiten nulo. RED → GREEN en §5, *slice* 8. Guarda estructural sobre las columnas reales |
| 9 | **Estado transitorio persistido como vigente**, contra WORKFLOW §6.1: `STATUS.md` y este reporte condicionaban `Task/009` a que el PR estuviera *"fusionado y normalizado"* | **Bloqueante** | Redacción durable: `Task/009` depende de que `Task/008` esté **Aprobada**; el estado de Git se verifica en vivo. Los contadores de Git pasan a ser **observación fechada** (§17) |
| 10 | **La garantía de inmutabilidad de `AuditEvent` prometía de más**: el DML masivo del ORM la sortea | Precisión | Garantía reformulada al perímetro real y **fijada por prueba en las dos direcciones** (§8.1) |
| 11 | El *owner* del *bootstrap* de `Profile`/`Administrator` decía *"`Task/012` o posterior"*, atribución vaga y además equivocada | Precisión | El ROADMAP ya lo asigna: **`Task/036`** en producción y **`Task/022`** para la semilla local (§9.1) |

## 7. PostgreSQL real y guardas

| Comprobación | Resultado |
| --- | --- |
| Base utilizada | `personal_blog_test` (base **dedicada** de pruebas) |
| Sufijo `_test` verificado | sí |
| Marca `personal-blog:test-database` dentro de la base | sí |
| `personal_blog` lleva la marca | **no** — y así debe seguir |
| Guarda *fail-closed* activa antes de cualquier `downgrade` | sí (`Task/005.6`/`005.7`, sin modificar) |
| **SQLite usado** | **NO** |
| `downgrade base` sobre la base de desarrollo | **NO** |
| Volúmenes eliminados | **0** |

Ninguna credencial aparece en este reporte, en la ficha, en el código ni en los registros.

## 8. Alembic

| Paso | Resultado |
| --- | --- |
| Cabeza inicial | `0001` |
| Revisión creada | **`0002`** — `alembic/versions/20260826_0002_modelo_de_datos_del_mvp.py` |
| `down_revision` | `0001` |
| `upgrade head` | correcto |
| `current` | `0002 (head)` |
| `downgrade 0001` | correcto |
| Estado tras `downgrade` | `current` = `0001`; **1** tabla en `public` (solo `alembic_version`): las 14 tablas de negocio desaparecieron |
| `upgrade head` de nuevo | correcto; `current` = `0002 (head)` |
| Ciclo `head → base → head` | verde en `tests/integration/test_migrations.py` |
| **Comprobación de *drift*** | `compare_metadata` devuelve `[]` |
| `downgrade` vacío | **no**: revierte las 14 tablas y sus índices |
| Migración `0001` | **intacta** |

> **Sobre la fecha del nombre de archivo.** Es `20260826` y no `20260825` porque
> `alembic.ini` fija `timezone = UTC` y la generación ocurrió a las 03:07 UTC. Es la
> convención del proyecto funcionando, no un descuadre.

### 8.1 Inmutabilidad de `AuditEvent`: la garantía exacta

Medida contra PostgreSQL real, no supuesta:

| Ruta de escritura sobre `audit_events` | ¿La guarda la detiene? |
| --- | :---: |
| `evento.action = …` + `flush` (unidad de trabajo del ORM) | **sí** |
| `session.delete(evento)` + `flush` | **sí** |
| `session.execute(update(AuditEvent)…)` — DML masivo del ORM | **no** |
| `session.execute(delete(AuditEvent)…)` — DML masivo del ORM | **no** |
| Sentencia de nivel Core sobre la tabla, o SQL a mano | **no** |

**Qué protege:** la ruta normal de escritura del ORM —cargar, modificar, `flush`—, que es
por donde escribe el código de aplicación en el 100 % de los casos previstos.

**Qué NO protege:** el DML masivo del ORM y cualquier sentencia Core. Eso **es** código de
aplicación, así que decir *"la aplicación no puede modificar un evento"* sería **falso**.
La primera redacción de este reporte lo decía; se corrige.

**Owner del endurecimiento restante: `Task/018`.** Cerrar el resto no se consigue con más
enganches —siempre queda una ruta más— sino retirando `UPDATE` y `DELETE` sobre
`audit_events` al rol de base de datos de la aplicación: privilegio mínimo (requisito
S-01).

**El perímetro está fijado por prueba**, en las dos direcciones. Los casos que documentan
el hueco están escritos para **ponerse rojos el día que se cierre**, de modo que la
documentación no pueda quedarse afirmando de menos.

> **Discrepancia declarada, no escondida.** El criterio de aceptación 11 decía
> *"`AuditEvent` es inmutable desde la aplicación"*. Esa garantía **no puede entregarse**
> sin invadir `Task/018`. El criterio se ha reformulado a la garantía real y la diferencia
> queda escrita aquí para que el usuario la valore en la aprobación.

## 9. Restricciones probadas contra el motor

| Caso | Resultado |
| --- | --- |
| *Slug* duplicado en el mismo tipo | **rechazado** |
| Mismo *slug* en tipos distintos | **aceptado** (unicidad por tipo) |
| Estado fuera del contrato cerrado | **rechazado** |
| `published` sin `published_at` (los 4 tipos) | **rechazado** |
| `draft` **con** `published_at` | **aceptado** (despublicación) |
| `rating` = 0, −1, 6, 100 | **rechazado** |
| `rating` = 1, 3, 5 | **aceptado** |
| `rating` nulo | **aceptado** |
| `project_status` inválido | **rechazado** |
| Asociación duplicada a etiqueta | **rechazado** |
| Etiqueta inexistente | **rechazado** |
| **Eliminar `Tag`** | contenido **intacto**, asociación retirada |
| **Eliminar contenido** | etiqueta **intacta** |
| Eliminar medio usado como portada, miniatura o foto | **rechazado** (`RESTRICT`) |
| Eliminar medio sin referencias | **aceptado** |
| `cover_id` inexistente | **rechazado** |
| `object_key` duplicada | **rechazado** |
| `size_bytes` ≤ 0, dimensiones ≤ 0 | **rechazado** |
| Segundo `Profile` / segundo `Administrator` | **rechazado** |
| Correo de administrador duplicado | **rechazado** |
| Dos enlaces sociales con el mismo orden | **rechazado** |
| Eliminar el perfil | sus enlaces desaparecen |
| Actor de auditoría inexistente | **rechazado** |
| Eliminar administrador con historial | **rechazado** (`RESTRICT`) |
| Modificar o eliminar un `AuditEvent` | **rechazado** (`AuditEventIsImmutableError`) |
| Referencia polimórfica a un elemento inexistente | **aceptada** — límite declarado en `data-model.md` §6.1 |

### 9.1 Owner del *bootstrap* de `Profile` y `Administrator`

Verificado contra el ROADMAP y las fichas de etapa, **no deducido**:

| Trabajo | Owner canónico | Cita |
| --- | --- | --- |
| Administrador y perfil **reales en producción** | **`Task/036-Publicar-Primer-Contenido`** (ETAPA 10) | *"Primera ejecución de las migraciones en producción. **Administrador. Perfil.** Artículo. Review. Video. Imágenes."* |
| **Datos semilla** del entorno local | **`Task/022-Validacion-Local-Production-Like`** (ETAPA 07) | *"Reconstrucción completa. Migraciones. **Seed.** Flujo administrativo…"* |
| **Editar** el perfil por API | `Task/012-API-Administrativa` | edición, que no es lo mismo que la creación inicial |

> **Corregido en la revisión pre-approval.** Antes se decía *"`Task/012` o posterior"*:
> vago y además equivocado. `Task/012` es dueña de la API administrativa —incluida la
> edición del perfil—, pero eso no la convierte en dueña de la carga inicial de datos
> reales. El owner ya existía en el roadmap; solo había que leerlo.

## 10. Esquema resultante

| Elemento | Cantidad |
| --- | ---: |
| Tablas de negocio | **14** |
| Restricciones `CHECK` | 18 |
| Claves foráneas | 15 |
| Claves primarias | 15 |
| Restricciones `UNIQUE` | 10 |
| Índices | 44 |

Cada índice y la consulta que lo justifica: [`data-model.md`](../architecture/data-model.md) §8.
Se enumeran también los índices **considerados y no creados** (`featured`, búsqueda de texto
completo) con su razón, para que la ausencia sea una decisión y no un olvido.

## 11. Resultado de las validaciones

| Prueba | Comando | Resultado | Exit code |
| --- | --- | --- | :---: |
| Lint | `ruff check .` | `All checks passed!` | **0** |
| Formato | `ruff format --check .` | `88 files already formatted` | **0** |
| Tipado | `mypy` | `Success: no issues found in 86 source files` | **0** |
| Dominio | `pytest tests/unit -q` | **74 passed** | **0** |
| Integración | `pytest -m integration -q` | **95 passed**, 156 deselected | **0** |
| **Suite completa** | `pytest -q -W error` | **250 passed, 1 skipped**, **0 warnings** | **0** |
| Suite sin entorno de integración | `pytest -q` sin la variable | **156 passed, 95 skipped** con motivo explícito | **0** |
| Cobertura | `pytest --cov -q` | **100 %** — 722 sentencias, 62 ramas, 0 sin cubrir | **0** |
| Higiene del diff | `git diff --check` | sin espacios sobrantes ni marcadores de conflicto | **0** |
| Dependencias | `pip check` | `No broken requirements found` | **0** |

**Omisiones, explicadas y no escondidas:**

| Omisión | Motivo |
| --- | --- |
| `tests/test_logging_utc.py::…` (1) | **Preexistente.** `time.tzset` no existe en Windows. No la introduce esta tarea |
| 95 pruebas de integración cuando `PERSONAL_BLOG_TEST_DATABASE_URL` no está definida | Es el **caso 1** de la política vigente: no hay entorno de integración que ejecutar. Con la variable definida, un fallo de PostgreSQL es `FAIL`, nunca `skip` |

**Sobre la cobertura:** el 100 % es una señal, no la especificación
([§12](../project-management/BACKEND_TESTING_STRATEGY.md)). Lo que sostiene esta tarea no es
el porcentaje sino la matriz: cada rama de negocio nueva tiene su caso explícito, y los
casos negativos —transiciones inválidas, valores fuera de escala, duplicados, referencias
rotas, borrados prohibidos— son mayoría. No se añadió ninguna prueba trivial para subir el
número ni se excluyó ninguna línea.

## 12. Stack local

Verificado de forma **no destructiva** (`docker compose ps`):

| Servicio | Estado |
| --- | --- |
| `backend` | Up (healthy) |
| `frontend` | Up (healthy) |
| `traefik` | Up (healthy) |
| `postgres` | Up (healthy) |
| `minio` | Up (healthy) |
| `portainer` | Up (running) |

**Volúmenes: 3 antes, 3 después, 0 eliminados.** No se ejecutó `docker compose down -v`,
`volume rm`, `volume prune` ni `system prune`. **No se tocó ningún otro proyecto Docker.**

> **La base de desarrollo `personal_blog` sigue en la revisión `0001`.** La migración se
> validó contra `personal_blog_test`. Aplicarla al entorno de desarrollo es un paso del
> usuario, incluido en §15.

## 13. Guarda de alcance

| Comprobación | Resultado |
| --- | :---: |
| Endpoints públicos implementados (`Task/009`) | **0** |
| `ObjectStorage`, `MinIOStorage`, `S3Storage`, boto3, SDK de S3 | **NO** |
| Subida, descarga, URL prefirmadas, miniaturas | **NO** |
| Login, sesiones, JWT, cookies, *hashing*, *rate limiting* (`Task/011`) | **NO** |
| Servicio de auditoría, *middleware*, catálogo de acciones | **NO** |
| CRUD administrativo, endpoints de publicar/archivar (`Task/012`) | **NO** |
| Render o sanitización de Markdown | **NO** |
| Cambios en `personal-blog-frontend` | **NINGUNO** |
| AWS, Terraform, Floci, Grafana, VPS, PgBouncer | **NO** |
| `pytest-xdist` o ejecución paralela (**R-37** sigue siendo de `Task/020`) | **NO** |
| Datos personales, credenciales o contenido sembrado | **NINGUNO** |
| Hipótesis marcadas como decisiones aceptadas | **NINGUNA** |

## 14. Archivos

### `personal-blog-backend` (rama `Task/008-Modelo-de-Datos`)

**Creados (22):** `alembic/versions/20260826_0002_modelo_de_datos_del_mvp.py` ·
`app/modules/models.py` · `app/shared/database/mixins.py` · `app/shared/database/types.py` ·
`app/modules/{posts,book_reviews,videos,projects}/domain/` ·
`app/modules/{posts,book_reviews,videos,projects,profile,tags,media,authentication,audit}/infrastructure/models.py` ·
`tests/unit/` (5 módulos) · `tests/integration/{test_esquema_de_contenido,test_esquema_fisico,test_relaciones_de_etiquetas,test_politica_de_medios,test_singletons,test_auditoria,test_borrador_minimo}.py`

**Modificados (10):** `README.md` · `alembic/env.py` · `alembic/script.py.mako` ·
`app/main.py` · `app/modules/__init__.py` · `app/shared/errors/__init__.py` ·
`tests/integration/conftest.py` · `tests/integration/test_migrations.py` ·
`tests/test_database.py` · `tests/test_grafo_de_fixtures_de_integracion.py`

### `personal-blog-infra` (rama `Task/008-Modelo-de-Datos`)

**Creados (2):** `docs/architecture/data-model.md` · `docs/tasks/TASK-008-data-model.md`
(este reporte es el tercero).

**Modificados (5):** `docs/product/CONTENT_MODEL.md` ·
`docs/project-management/BACKEND_TESTING_STRATEGY.md` ·
`docs/project-management/ROADMAP.md` · `docs/project-management/STATUS.md` ·
`docs/stages/STAGE-03-domain-and-backend.md`

### `personal-blog-frontend`

**Sin rama y sin cambios.**

## 15. Pasos de validación para el usuario

```powershell
# 1. Estado de las ramas (deben ser Task/008 en backend e infra; main en frontend)
cd C:\Users\jeffe\Downloads\Blog_Personal
git -C personal-blog-backend  status -sb
git -C personal-blog-infra    status -sb
git -C personal-blog-frontend status -sb   # limpio, sin rama Task

# 2. Backend: entorno de integracion
cd personal-blog-backend
.\.venv\Scripts\Activate.ps1
$env:PERSONAL_BLOG_TEST_DATABASE_URL = "postgresql://<usuario>:<clave>@127.0.0.1:55432/personal_blog_test"

# 3. Calidad
ruff check .
ruff format --check .
mypy
pytest -q -W error
pytest --cov -q

# 4. Ciclo real de migraciones contra la base de PRUEBAS
$env:BLOG_DATABASE_URL = $env:PERSONAL_BLOG_TEST_DATABASE_URL
alembic current          # 0002 (head)
alembic downgrade 0001
alembic current          # 0001
alembic upgrade head
alembic current          # 0002 (head)

# 5. Inspeccion del esquema
docker exec personal-blog-local-postgres psql -U blog_local -d personal_blog_test -c "\dt"

# 6. Stack local intacto
cd ..\personal-blog-infra
docker compose ps
docker volume ls | Select-String personal-blog    # deben seguir siendo 3
```

**Opcional, y decisión del usuario:** aplicar `0002` también a la base de **desarrollo**
`personal_blog`. La tarea no lo hizo por sí sola.

```powershell
cd ..\personal-blog-backend
$env:BLOG_DATABASE_URL = "postgresql://<usuario>:<clave>@127.0.0.1:55432/personal_blog"
alembic upgrade head
```

> **Nunca** apuntes `PERSONAL_BLOG_TEST_DATABASE_URL` a `personal_blog`: las pruebas de
> integración ejecutan `downgrade base`. La guarda lo rechazaría, pero la regla se recuerda
> igual.

## 16. Deuda técnica pendiente

| # | Deuda | Dueño |
| --- | --- | --- |
| 1 | `updated_at` solo avanza en escrituras que pasan por el ORM | aceptada y documentada |
| 2 | La referencia polimórfica de auditoría no tiene integridad referencial | aceptada (`data-model.md` §6.1) |
| 3 | `technologies` no tiene integridad sobre su contenido | revisable en `Task/009` |
| 4 | Retención de `AuditEvent` sin decidir | `Task/011` y operación |
| 5 | El perfil y el administrador reales no existen todavía | `Task/036` (producción) · `Task/022` (semilla local) |
| 6 | Formato y generación del *slug* | `Task/012` |
| 7 | Lista cerrada de proveedores de vídeo | `Task/014` |
| 8 | Índices de búsqueda | `Task/009` |
| 9 | El DML masivo del ORM y las sentencias Core sortean la guarda de inmutabilidad de auditoría (§8.1) | `Task/018` — retirar `UPDATE`/`DELETE` al rol |
| 10 | `tests/contract/` todavía no existe | `Task/009`, `Task/010` |
| 11 | **R-37** (concurrencia del harness) sigue abierto y sin agravarse | `Task/020` |
| 12 | Qué campos debe tener un contenido **para publicarse** (autor, proveedor, URL, valoración) | `Task/012` |

**Riesgos nuevos: ninguno.** Ningún riesgo existente se agrava.

## 17. Gobierno

**Estado duradero** de la tarea ([WORKFLOW §6.1](../project-management/WORKFLOW.md)):

| Campo | Valor |
| --- | --- |
| `Task/008` | **Aprobada** el 2026-08-25 |
| Expresión de aprobación | `approved: Task/008-Modelo-de-Datos` |
| Avance global | **8 / 41 — 20 %** |
| ETAPA 03 | **1 / 5 — 20 %** |
| `Task/009` | **Pendiente, no iniciada.** Es la siguiente del roadmap |

**Estado de Git: observación fechada, no estado vigente.** Estos cuatro contadores son
**transitorios** por definición —el flujo de cierre los cambia en cuanto haya aprobación—,
así que se registran como lo que son: lo que se observó al terminar la tarea. Quien
necesite el estado real lo consulta en Git y GitHub, no aquí.

> *Observado el 2026-08-25, **antes** de la aprobación:* en `personal-blog-backend` y
> `personal-blog-infra`, `git rev-list --count main..HEAD` = **0**, staging **vacío**,
> `git ls-remote --heads origin "Task/*"` **sin resultados** y `gh pr list` **sin pull
> requests**. Es la evidencia de que el trabajo permaneció sin confirmar hasta la
> aprobación, que es lo que la Definition of Done exige comprobar.
>
> El flujo de cierre —commit, integración en `dev`, publicación y pull request— se ejecutó
> **después** de recibir `approved: Task/008-Modelo-de-Datos`. Su resultado es estado
> transitorio y **no se registra aquí**: se consulta en Git y GitHub.

## 18. Próxima tarea

`Task/009-API-Publica` — consultas públicas, paginación, filtros y búsqueda sobre el modelo
que esta tarea define. Permanece **Pendiente y no iniciada**; depende de `Task/008`, que
debe estar **Aprobada**.

Cuando se inicie, el estado real de Git se verifica **en vivo** y su rama nace desde `main`
actualizado y limpio, como toda rama Task
([WORKFLOW §2.1 y §6.1](../project-management/WORKFLOW.md)). Este documento no afirma en qué
punto del trámite de cierre se encuentra `Task/008`: eso es estado transitorio y se consulta
donde vive.
