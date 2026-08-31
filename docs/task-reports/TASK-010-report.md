# Task/010-Almacenamiento-Compatible-S3 — Aprobada

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/010-Almacenamiento-Compatible-S3` |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Tipo** | Tarea oficial del roadmap. **Cuenta** dentro de las 41 |
| **Estado** | **Aprobada** el 2026-08-28 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/010-Almacenamiento-Compatible-S3` |
| **Depende de** | `Task/008-Modelo-de-Datos` (**Aprobada**) |
| **Ficha** | [TASK-010](../tasks/TASK-010-s3-compatible-storage.md) |

> **Revisión externa y corrección (2026-08-28).** La primera entrega fue devuelta
> con dos bloqueantes técnicos y una corrección de trazabilidad. Los tres están
> resueltos y documentados en este mismo reporte:
>
> | # | Hallazgo de la revisión | Dónde se resuelve |
> | --- | --- | --- |
> | 1 | El `access_url` local se firmaba contra `minio:9000`, inalcanzable para el navegador del host | **§S.1 y §S.2** — separación de endpoints, con ciclo RED → GREEN → REFACTOR |
> | 2 | El backend en Docker no se había recreado con la configuración nueva | **§W.1** — reconstruido, recreado y verificado extremo a extremo |
> | 3 | El reporte afirmaba que la mutación «sustituye al RED histórico» | **§K.2 y §Y** — afirmación retirada; clasificación honesta de las pruebas |
>
> La implementación general **no se rehízo**: la corrección es aditiva.

---

## A. Preflight Git

Ejecutado antes de crear ninguna rama, en los tres repositorios.

**BACKEND**

| Comprobación | Resultado |
| --- | --- |
| `main` | `81347758dcc01eda55938a3bf0a298684c6c8a08` |
| `origin/main` | `81347758dcc01eda55938a3bf0a298684c6c8a08` — **coinciden** |
| Working tree limpio | **Sí** (`git status --porcelain` vacío) |
| `merge-base --is-ancestor main dev` | exit `0` |
| `rev-list --count dev..main` | `0` |
| `diff main dev` | vacío |

**INFRA**

| Comprobación | Resultado |
| --- | --- |
| `main` | `64e237cde43a91c27ad41fb78b46cd17acf6a6f8` |
| `origin/main` | `64e237cde43a91c27ad41fb78b46cd17acf6a6f8` — **coinciden** |
| Working tree limpio | **Sí** |
| `merge-base --is-ancestor main dev` | exit `0` |
| `rev-list --count dev..main` | `0` |
| `diff main dev` | vacío |

**FRONTEND**

| Comprobación | Resultado |
| --- | --- |
| `main` | `fd62f221707591a984cf0fb51a03ea339380ab35` |
| `origin/main` | idéntico — **coinciden** |
| Working tree limpio | **Sí** |

No se encontró ninguna rama Task inesperada. No se ejecutó ningún `reset`,
`restore`, `clean` ni `stash`.

---

## B. Ramas

| Repositorio | SHA base | Rama base | `HEAD == main` al crearla | `rev-list --count main..HEAD` |
| --- | --- | --- | :---: | :---: |
| backend | `81347758dcc01eda55938a3bf0a298684c6c8a08` | **`main`** | **SÍ** | `0` |
| infra | `64e237cde43a91c27ad41fb78b46cd17acf6a6f8` | **`main`** | **SÍ** | `0` |
| frontend | — | — | — | sin rama |

**¿Alguna nació desde `dev`?** **NO.** Ninguna. El comando ejecutado fue
`git switch main` → `git pull --ff-only origin main` → `git switch -c
Task/010-Almacenamiento-Compatible-S3`, con la verificación inmediata posterior.

---

## C. Fuentes canónicas leídas

**Raíz:** `CLAUDE.md`.

**Infra — gobierno:** `docs/claude/PROJECT_INSTRUCTIONS.md`,
`project-management/WORKFLOW.md` (§2.1 y §6.1), `STATUS.md`, `ROADMAP.md`,
`DEFINITION_OF_DONE.md`, `TASK_TEMPLATE.md`, `BACKEND_TESTING_STRATEGY.md`
(completo).

**Infra — producto y arquitectura:** `stages/STAGE-03-domain-and-backend.md`,
`product/MVP_SCOPE.md`, `product/USER_FLOWS.md` (B.4 y B.5),
`product/CONTENT_MODEL.md` (§3.7 e invariantes), `architecture/data-model.md`
(§4.1, §7, §10), `architecture/api-contracts.md` (§3, §6, §8, §10, §11),
`architecture/software-architecture.md` (§3.4, §3.5, §3.7),
`architecture/security-boundaries.md`,
`architecture/non-functional-requirements.md`,
`architecture/open-decisions.md` (**D-08** completo).

**ADR:** ADR-004 (monolito modular), ADR-005 (Markdown), ADR-006 (paridad local
AWS), ADR-007 (PostgreSQL en VPS).

**Tareas previas:** fichas y reportes de `Task/008`, `Task/009` y `Task/009.1`.
En particular la decisión **D-009-O** y su justificación.

**Backend:** `README.md`, `CONTRIBUTING.md`, `pyproject.toml`,
`requirements*.txt`, `.env.example`, `app/main.py`, `app/api/`,
`app/shared/` completo, `app/modules/media/`, y los módulos `posts`,
`book_reviews`, `videos`, `projects`, `profile`; `tests/` completo, con especial
atención a `tests/conftest.py`, `tests/__init__.py`,
`tests/integration/conftest.py`, `tests/test_grafo_de_fixtures_de_integracion.py`
y `tests/unit/test_independencia_del_dominio.py`; `alembic/`.

**Infra local:** `docker-compose.yml`, `.env.example`,
`docs/runbooks/local-environment.md`.

---

## D. Scope definitivo

### Qué implementó `Task/010`

| Elemento | Dónde |
| --- | --- |
| Interfaz `ObjectStorage` y tipos de resultado propios | `app/shared/storage/contrato.py` |
| Jerarquía mínima de errores de almacenamiento | `app/shared/storage/errores.py` |
| Traducción del SDK al contrato | `app/shared/storage/s3_compatible.py` |
| `MinIOStorage` (local) | `app/shared/storage/minio.py` |
| `S3Storage` (producción, **código real**) | `app/shared/storage/s3.py` |
| Selector por entorno | `app/shared/storage/fabrica.py` |
| Configuración validada y *fail-fast* | `app/shared/configuration/settings.py` |
| Claves de objeto no predecibles | `app/modules/media/domain/claves.py` |
| Validación de imagen por decodificación | `app/modules/media/domain/validacion.py` |
| Miniaturas | `app/modules/media/domain/miniaturas.py` |
| Errores del dominio de medios | `app/modules/media/domain/errores.py` |
| Contrato de persistencia | `app/modules/media/application/repositorio.py` |
| Caso de uso `SubirImagen`, con compensación | `app/modules/media/application/subir_imagen.py` |
| Caso de uso `EliminarMedio`, con comprobación de uso | `app/modules/media/application/eliminar_medio.py` |
| Repositorio sobre SQLAlchemy | `app/modules/media/infrastructure/repositorio.py` |
| Emisión del enlace público | `app/modules/media/presentation/acceso.py` |
| Campo `access_url` (**D-009-O**) | `app/modules/media/presentation/schemas.py` + los 5 DTO que lo anidan |
| Suite de contrato común | `tests/contract/test_contrato_de_object_storage.py` |
| Harness de almacenamiento *fail-closed* | `tests/almacenamiento_de_pruebas.py` |

### Qué quedó para otras tareas

| Queda para | Qué |
| --- | --- |
| **`Task/030`** | Bucket real de S3, políticas, CORS, *lifecycle*, **valor productivo del TTL**, semántica de caché, CDN y **D-08** completa. Ejecución de `S3Storage` contra Amazon S3 real |
| **`Task/032`** | *Wiring* productivo de `S3Storage` en la Lambda; origen de la configuración en SSM |
| **`Task/012`** | Endpoints `POST`/`GET`/`DELETE /api/v1/admin/media`; biblioteca de medios; presentación de duplicados por `checksum`; referencia estable de imágenes dentro del Markdown |
| **`Task/018`** | Endurecimiento de la subida: límites definitivos, CORS efectivo, cualquier análisis adicional del contenido |
| **`Task/016`** | `og:image` y exposición de la miniatura en los listados |
| **`Task/011`** | Autenticación de las rutas administrativas |

**No se creó ningún recurso AWS. No se usó ninguna credencial AWS. No se escribió
Terraform. No se tocó SSM, Lambda, API Gateway ni el frontend.**

---

## E. Contrato de `ObjectStorage`

| Operación | Input | Output | Error | Idempotencia | Razón de existir |
| --- | --- | --- | --- | --- | --- |
| `guardar` | `clave`, `contenido: bytes`, `tipo_de_contenido` | `ObjetoAlmacenado` | `FalloDelProveedor…` | **Sí** — sobrescribe la misma clave (D-010-D) | Subir el original y su miniatura |
| `obtener` | `clave` | `ContenidoDeObjeto` | `ObjetoNoEncontradoError` si no existe; `FalloDelProveedor…` en lo demás | Sí, es lectura | Recuperar el binario |
| `existe` | `clave` | `bool` | `FalloDelProveedor…` | Sí, es lectura | Comprobar sin descargar |
| `eliminar` | `clave` | `None` | `FalloDelProveedor…`; **nunca** por ausencia | **Sí** — no lanza si no existía (D-010-C) | Compensar y borrar |
| `acceso_temporal` | `clave`, `duracion` | `AccesoTemporal(url, expira_en)` | `FalloDelProveedor…` | Sí — la firma es local | Emitir el enlace público |

**Tipos propios, no del SDK:** `ObjetoAlmacenado`, `ContenidoDeObjeto`,
`AccesoTemporal`. Ningún `dict` de `boto3` ni `StreamingBody` cruza la interfaz.

**El módulo del contrato importa solo `abc`, `dataclasses` y `datetime`.** No
carga FastAPI, SQLAlchemy, `boto3` ni `botocore`, y hay una prueba en subproceso
que lo comprueba.

**Operaciones deliberadamente ausentes:** `listar`, `copiar` y `metadatos`. Las
pedirá `Task/012`; tenerlas muertas ahora obligaría a implementarlas dos veces y
a probarlas sin consumidor.

---

## F. SDK y dependencias

| Dependencia | Versión | Uso | Alternativas evaluadas | Justificación |
| --- | --- | --- | --- | --- |
| `boto3` | `1.43.82` | Cliente S3 de **las dos** implementaciones | SDK oficial de MinIO para `MinIOStorage`; cliente HTTP propio con firma SigV4 | El SDK de MinIO arrastra `pycryptodome` y `argon2-cffi` al **único** `requirements.txt` —y por tanto al artefacto de Lambda (P-07)— para código que allí no se ejecuta jamás, y duplica la superficie a auditar (S-09). MinIO implementa el protocolo S3, así que `boto3` lo ejerce de verdad. Firmar a mano estaba descartado: criptografía propia sin ninguna ventaja |
| `pillow` | `12.3.0` | Decodificación, validación real, dimensiones y miniaturas | Parser propio de JPEG/PNG; `imagesize` (solo dimensiones, sin validar); no generar miniaturas | Un parser binario casero es exactamente lo que la ficha prohíbe. `imagesize` lee cabeceras, que es lo que **no** basta: una cabecera perfecta con datos truncados pasaría |
| `boto3-stubs[s3]` | `1.43.82` | **Solo tipado** (dev) | `Any` en la frontera del SDK | `mypy` corre en `strict`. Es dependencia de desarrollo: no entra en la imagen ni en el artefacto de despliegue |

**No se instaló** AWS CLI, Terraform, LocalStack, Moto, Floci, ningún framework
de inyección de dependencias ni ninguno de CQRS.

`pip check`: **No broken requirements found.**

### Por qué un solo SDK no convierte a `MinIOStorage` en un alias vacío

Es la objeción evidente y se resolvió con **invariantes**, no con duplicación de
código:

| | `MinIOStorage` | `S3Storage` |
| --- | --- | --- |
| Endpoint | **Obligatorio**; sin él no se construye | **Opcional**; sin él, `boto3` resuelve el de AWS |
| Endpoint de AWS | **Rechazado al construir** | Es el caso normal |
| Direccionamiento | Siempre por ruta | Virtual contra AWS; por ruta con endpoint propio |
| Crear bucket | — | **Nunca**, ni al arrancar ni al operar |
| Credenciales | Obligatorias | Opcionales: en producción, el rol de ejecución |

Cada fila tiene su prueba (M-02, M-03, S-02, S-04), y la mutación que las
elimina las pone rojas.

---

## G. Configuración

| Variable | Obligatoria | Por defecto | Notas |
| --- | :---: | --- | --- |
| `BLOG_STORAGE_PROVIDER` | No | `minio` | Tipo cerrado `minio` \| `s3`. **Prohibido `minio` con `BLOG_APP_ENV=production`** |
| `BLOG_STORAGE_BUCKET` | **Sí** | — | Sin ella el proceso no arranca |
| `BLOG_STORAGE_REGION` | No | `us-east-1` | |
| `BLOG_STORAGE_ENDPOINT_URL` | Con `minio` | — | |
| `BLOG_STORAGE_ACCESS_KEY` | Con `minio` | — | `repr=False` |
| `BLOG_STORAGE_SECRET_KEY` | Con `minio` | — | `SecretStr` **y** `repr=False` |
| `BLOG_STORAGE_ACCESS_TTL_SECONDS` | No | `900` | Rango `60..604800` |

**Fail-fast:** la validación ocurre al construir `Settings`, es decir, al
importar `app.main`. Un proveedor desconocido, un bucket ausente o un `minio` sin
endpoint impiden el arranque, no la primera subida.

**Un solo sistema de configuración.** Se ampliaron los `Settings` existentes; no
se creó un segundo mecanismo paralelo.

**Manejo de secretos:** el secreto es `SecretStr` y está fuera de `repr`. Se
comprueba por prueba que no aparece en `repr(settings)`, ni en `str(settings)`,
ni en el mensaje de `ConfigurationError`, ni en la URL prefirmada emitida. Y una
**guarda anti-tautología** comprueba que sigue siendo legible por quien lo
necesita: ocultarlo no puede significar perderlo.

**Selector:** `app/shared/storage/fabrica.py`, único punto del proyecto que sabe
que existe más de una implementación. No hay ningún `if app_env == ...` repartido
por la aplicación. Se memoriza por configuración (`lru_cache`), así que no se
construye un cliente del SDK por petición; y hay una guarda que comprueba que dos
configuraciones distintas **no** comparten instancia.

---

## H. `MinIOStorage`

| Campo | Valor |
| --- | --- |
| SDK | `boto3`, direccionamiento por ruta, firma `s3v4` |
| Endpoint de prueba | `http://127.0.0.1:9000` — el MinIO del Compose de `Task/007` |
| Suite de contrato | **13 casos, todos verdes** |
| Integración real | **Sí.** No hay ningún doble en el camino del contrato |
| Aislamiento del bucket | Bucket **creado por la suite**, nombre `personal-blog-test-<12 hex>` |
| Aislamiento entre pruebas | Prefijo de clave único por prueba |
| Limpieza | Vacía y borra **solo** su bucket, y vuelve a comprobar el prefijo antes de hacerlo |

---

## I. `S3Storage`

| Campo | Valor |
| --- | --- |
| SDK | `boto3`, firma `s3v4`; direccionamiento **derivado** del endpoint |
| Cómo se prueba sin AWS | Contra el **mismo endpoint S3-compatible local**. Es el código real del adaptador ejercitando el protocolo real |
| Suite de contrato | **Los mismos 13 casos, todos verdes** |
| Invariantes propias | Se construye sin endpoint y resuelve el de AWS; **nunca** llama a `create_bucket` |
| Qué falta para `Task/030` | Bucket real, política, CORS, *lifecycle*, permisos IAM, TTL productivo y la ejecución contra Amazon S3 real |

**Lo que aquí se demuestra y lo que no.** Se demuestra que `S3Storage` habla el
protocolo S3 correctamente. **No** se demuestra que la configuración de AWS —
bucket, política, permisos— vaya a ser la correcta: eso solo lo valida AWS real,
y es de `Task/030`. La distinción es la misma que exige el criterio **C-5** de la
Definition of Done para infraestructura cloud, y se declara aquí para no
confundir emulación con validación.

---

## J. Matriz TDD ejecutada

La matriz completa está en la ficha §7.2. Resumen de cobertura:

| Bloque | Casos | Capa | Provider | Estado |
| --- | :---: | --- | --- | --- |
| **A.** Contrato `ObjectStorage` (OS-01…OS-13) | 13 × 2 = 26 | contrato | MinIO **y** S3 | Verde |
| **B.** Invariantes de cada adaptador (M-02, M-03, S-02, S-04) | 12 | unitaria | por adaptador | Verde |
| **B'.** Traducción de errores del SDK (S-03) | 14 | unitaria | MinIO | Verde |
| **C.** Configuración y selector (C-01…C-07) | 13 | unitaria | — | Verde |
| **D.** Claves de objeto (K-01…K-06) | 15 | unitaria | — | Verde |
| **E.** Validación de imagen (I-01…I-11) | 18 | unitaria | — | Verde |
| **F.** Miniaturas (T-01…T-06) | 13 | unitaria | — | Verde |
| **G.** Persistencia y compensación (P-01…P-08) | 11 | aplicación | dobles de frontera | Verde |
| **G'.** Persistencia real | 8 | integración | PostgreSQL + MinIO | Verde |
| **H.** Borrado y medio en uso (D-01…D-07) | 9 | integración + unitaria | PostgreSQL + MinIO | Verde |
| **I.** Acceso público (A-01…A-07) | 20 | integración + contrato | PostgreSQL + MinIO | Verde |
| **Guarda del harness** | 18 | estructural | — | Verde |

### Refinamientos de la matriz, y por qué

Dos casos se precisaron **al escribir la prueba**, antes de implementar nada. Se
registran porque la matriz previa decía otra cosa:

| Caso | Decía | Dice | Por qué |
| --- | --- | --- | --- |
| **I-05** | GIF y SVG → `TipoDeImagenNoPermitidoError` | GIF → `TipoDeImagenNoPermitidoError`; **SVG → `ImagenInvalidaError`** | Un GIF se decodifica sin problema y lo rechaza la **política**. Un SVG no es un formato rasterizado: ni siquiera se identifica como imagen. Es la consecuencia directa de validar decodificando, y forzar el otro error exigiría un caso especial que solo serviría para que la matriz tuviera razón. Lo que importa —que **no se almacena**— se comprueba igual |
| **A-02** | `object_key` nunca aparece en la respuesta | `object_key` no es **campo** del contrato y no aparece **fuera del enlace firmado** | Ver §S. Es el hallazgo principal de la tarea |

---

## K. Evidencia RED → GREEN → REFACTOR

Diez *slices*. En todos, el test se escribió **primero**, se ejecutó y falló
**por la razón esperada**: el comportamiento no existía.

### Slice 1 — Contrato de `ObjectStorage`

| | |
| --- | --- |
| **Test** | `tests/contract/test_contrato_de_object_storage.py` (13 casos × 2 proveedores) |
| **Comando RED** | `pytest tests/contract/test_contrato_de_object_storage.py -q` |
| **RED** | `1 error in 0.28s` |
| **Motivo** | `ModuleNotFoundError: No module named 'app.shared.storage'` |
| **Implementación** | `contrato.py`, `errores.py`, `s3_compatible.py`, `minio.py`, `s3.py`, `__init__.py` |
| **GREEN** | `26 passed in 1.88s` |
| **Refactor** | La base compartida `AlmacenamientoCompatibleS3` **es** el refactor: se extrajo la traducción del SDK, común a las dos, dejando en cada subclase solo su política de cliente |

### Slice 2 y 3 — Invariantes de `MinIOStorage` y `S3Storage`

| | |
| --- | --- |
| **Test** | `tests/unit/test_adaptadores_de_almacenamiento.py` |
| **Comando RED** | `pytest tests/unit/test_adaptadores_de_almacenamiento.py -q` |
| **RED** | `7 failed, 5 passed in 0.44s` |
| **Motivo** | `Failed: DID NOT RAISE ConfiguracionDeAlmacenamientoInvalidaError` — la guarda de endpoint no existía |
| **Implementación** | `MinIOStorage._verificar_el_endpoint` |
| **GREEN** | `12 passed in 0.38s` |
| **Refactor** | No necesario: una función estática de ocho líneas, invocada desde el constructor |

> **Los 5 que ya pasaban se clasifican aparte, en §K.2.** No son evidencia de
> RED y no se presentan como tal.

### Slice 4 — Configuración y selector

| | |
| --- | --- |
| **Test** | `tests/unit/test_configuracion_de_almacenamiento.py` |
| **RED** | `1 error in 0.16s` — `ModuleNotFoundError: No module named 'app.shared.storage.fabrica'` |
| **Implementación** | Siete campos en `Settings`, dos validadores, y `fabrica.py` |
| **GREEN** | `13 passed in 0.05s` |
| **Refactor** | No necesario |

> **Consecuencia sobre el harness.** `BLOG_STORAGE_BUCKET` es obligatoria, así
> que el proceso de pruebas dejó de poder construir `Settings`: `14 failed, 169
> passed, 213 errors`. Se repuso en `tests/__init__.py` y en la *fixture*
> `_isolated_environment`, exactamente como ya se hacía con `BLOG_DATABASE_URL`,
> con un anfitrión `.invalid` que por definición nunca resuelve. Tres pruebas
> preexistentes necesitaron ajuste; están justificadas en §K.1.

### Slice 5 — Claves de objeto

| | |
| --- | --- |
| **Test** | `tests/unit/test_claves_de_medios.py` |
| **RED** | `1 error` — `ModuleNotFoundError: No module named 'app.modules.media.domain'` |
| **GREEN** | `15 passed in 0.04s` |
| **Refactor** | No necesario |

### Slice 6 — Validación de imagen

| | |
| --- | --- |
| **Test** | `tests/unit/test_validacion_de_imagenes.py` |
| **RED** | `1 error` — `ModuleNotFoundError: No module named 'app.modules.media.domain.errores'` |
| **Implementación** | `errores.py`, `validacion.py`, y dos errores base nuevos en `app/shared/errors/exceptions.py` (`415` y `413`, códigos que el manejador HTTP **ya** conocía) |
| **GREEN** | `18 passed in 0.40s` |
| **Refactor** | No necesario |

### Slice 7 — Miniaturas

| | |
| --- | --- |
| **Test** | `tests/unit/test_miniaturas.py` |
| **RED** | `1 error` — `ModuleNotFoundError: No module named 'app.modules.media.domain.miniaturas'` |
| **GREEN** | `10 passed in 2.34s` (13 tras cubrir modos de paleta y grises) |
| **Refactor** | Se extrajo `_preparar`, que agrupa orientación EXIF y conversión de modo |

### Slice 8 — Subida y compensación

| | |
| --- | --- |
| **Test** | `tests/unit/test_subir_imagen.py` |
| **RED** | `1 error` — `ModuleNotFoundError: No module named 'app.modules.media.application.repositorio'` |
| **GREEN** | `11 passed in 0.26s` |
| **Refactor** | Se extrajo `_compensar`, que unifica el deshacer de los dos puntos de fallo |

> Dos pruebas fallaron después del GREEN inicial con
> `TypeError: vars() argument must have __dict__ attribute`: un `dataclass` con
> `slots=True` no tiene `__dict__`. **Defecto de la prueba, no de la
> implementación**; se corrigió con `dataclasses.asdict` sin tocar el
> comportamiento ni relajar la aserción.

### Slice 9 — Persistencia real y borrado

| | |
| --- | --- |
| **Test** | `tests/integration/test_medios_persistidos.py` |
| **RED** | `1 error` — `ModuleNotFoundError: No module named 'app.modules.media.application.eliminar_medio'` |
| **Implementación** | `infrastructure/repositorio.py` y `application/eliminar_medio.py` |
| **GREEN** | `15 passed in 4.86s` (16 tras cubrir el borrado idempotente del repositorio) |
| **Refactor** | No necesario |

### Slice 10 — Acceso público (**D-009-O**)

| | |
| --- | --- |
| **Test** | `tests/integration/test_acceso_publico_a_medios.py` |
| **RED** | `7 failed, 11 passed` — `KeyError: 'access_url'`; el campo no existía |
| **Implementación** | `presentation/acceso.py`, `access_url` en `MedioPublico`, y la dependencia propagada a los 5 DTO y sus routers |
| **GREEN** | Verde tras resolver el hallazgo de §S |
| **Refactor** | El alias `AccesoAMediosDependencia` evita repetir la anotación completa en siete endpoints |

### K.2 Clasificación honesta de la evidencia TDD

Lo que sigue es la descripción exacta de qué se escribió antes y qué después.
No se maquilla y no se reconstruye nada en laboratorio: no hace falta, porque el
comportamiento funcional sí nació dirigido por pruebas.

**Slice 1 — el contrato común: test-first, sin matices.** Las 13 pruebas de
contrato se escribieron **antes** de que existieran `ObjectStorage`,
`MinIOStorage` y `S3Storage`. RED registrado (`ModuleNotFoundError: No module
named 'app.shared.storage'`), y GREEN con **26 verdes** = 13 casos × 2
adaptadores. Es decir: **el comportamiento funcional común de los dos
adaptadores nació test-first**, y es el grueso de lo que hacen.

**Slices 2 y 3 — invariantes propias de cada adaptador.** Se escribieron
**después** del slice 1, y ahí hay dos grupos distintos:

| Grupo | Cuántos | Qué pasó | Cómo se clasifica |
| --- | :---: | --- | --- |
| Guardas de endpoint de `MinIOStorage` | **7** | **RED real** por `DID NOT RAISE`: la validación no existía, se implementó y pasaron a verde | **Evidencia RED · TDD** |
| Guardas de ausencia y política | **5** | **Pasaron al escribirse**: `S3Storage` funciona sin endpoint, no crea buckets y la firma es local | **Regresión / política — NO evidencia RED** |

Las cinco del segundo grupo afirman propiedades que el diseño construido bajo el
contrato del slice 1 **ya tenía**. Obtener un RED sobre ellas habría exigido
escribir primero el código incorrecto a propósito —crear el bucket, exigir el
endpoint— para después corregirlo. Eso no es TDD: es fabricar historia. No se
hizo, y estas cinco **no se cuentan como evidencia de RED**. Su función es
impedir que una refactorización futura introduzca esos defectos.

**Corrección posterior — separación de endpoints.** El defecto de
alcanzabilidad del enlace (§S.1) se corrigió con un ciclo completo y real:
**RED → GREEN → REFACTOR**, con el RED registrado en §S.2 sobre código que no
existía. Se suma a la evidencia del slice 1.

**Resumen sin adornos:** los diez *slices* funcionales tuvieron su
comportamiento dirigido por pruebas antes de la implementación correspondiente.
En los slices 2 y 3, **siete** guardas produjeron RED propio y **cinco** guardas
adicionales de ausencia o política se añadieron después de existir los
adaptadores y pasaron al escribirse; esas cinco se clasifican como **regresión,
no como evidencia RED**. La mutación es evidencia **complementaria** de
sensibilidad y **nunca** sustituto del RED.

### K.1 Pruebas preexistentes modificadas, y su justificación

`BACKEND_TESTING_STRATEGY.md` §9 solo admite cuatro motivos. Todos los cambios
caen en el primero —**el requisito cambió**— y ninguno relaja una aserción:

| Prueba | Cambio | Motivo |
| --- | --- | --- |
| `test_configuration.py::test_una_configuracion_de_produccion_valida_se_construye` | Añade `storage_provider="s3"` | Una configuración de producción válida incluye ahora almacenamiento de producción. La prueba sigue afirmando lo mismo: que lo seguro **se acepta** |
| `test_hermeticidad.py` (sonda `_SIN_BOOTSTRAP`) | Fija el mínimo obligatorio, ahora mayor | La prueba mide si llegan los valores **intrusos**, no si la aplicación arranca. Lo que se amplió es el andamiaje |
| `test_openapi_publica.py::test_la_referencia_a_un_medio_no_promete_todavia_una_url` | Renombrada; ahora exige `{alt_text, width, height, access_url}` | La prueba de `Task/009` existía, literalmente, *"para que el día que `Task/010` lo añada sea una decisión consciente y no un efecto colateral"*. Esa es la condición que se cumple. **El conjunto sigue siendo cerrado**: no se relajó a «contiene `access_url`», que dejaría de detectar un campo de más |
| 5 pruebas de integración con `assert medio == {...}` exacto | Comparan la parte estable campo a campo y el enlace por separado | El valor del enlace lleva firma y marca de tiempo: no puede escribirse literal. Se **añadió** además la comprobación del conjunto cerrado de campos |
| `test_api_articulos.py::test_la_portada_no_expone_la_clave_del_objeto` | Reformulada | Ver §S. Es el hallazgo, no un ajuste |

También se **ampliaron** dos guardas anti-tautología existentes, de forma
puramente aditiva: `MODULOS_CONOCIDOS` (dos módulos nuevos de integración) y
`DOMINIOS_CONOCIDOS` (`app.modules.media.domain`).

---

## L. Claves de objeto

| Aspecto | Decisión |
| --- | --- |
| **Formato** | `medios/<uuid4>/original.<ext>` y `medios/<uuid4>/thumbnail.webp` |
| **Fuente de entropía** | UUID v4 — **122 bits aleatorios** |
| **Nombre del archivo** | **No participa.** `generar_claves` ni siquiera lo recibe |
| **Path traversal** | Imposible por construcción: no hay entrada del usuario que sanear |
| **Duplicidad** | Dos cargas del mismo archivo producen claves distintas; probado con 1000 generaciones sin colisión |
| **Longitud** | ~55 caracteres; el límite de la columna es 512 |

La prueba de nombres hostiles cubre `../../etc/passwd`,
`..\\..\\windows\\system32\\config\\sam`, `C:\\Users\\victima\\secreto.png`,
`a/b/c.png`, un nombre con byte nulo y uno con codificación doble.

**Por qué no se sanea el nombre.** Sanear obliga a razonar sobre travesía de
rutas, separadores de Windows, bytes nulos y codificaciones dobles, y a acertar
en las cuatro. No aceptarlo elimina la categoría entera. El nombre original **sí**
se conserva, como metadato informativo, en `media_assets.original_filename`.

---

## M. Validación de imagen

| Aspecto | Decisión |
| --- | --- |
| **MIME permitidos** | `image/jpeg`, `image/png`, `image/webp` |
| **Método de detección** | **Decodificación completa** con Pillow. Ni extensión, ni `Content-Type` declarado, ni firma de los primeros bytes |
| **Máximo de bytes** | **5 MiB** (5 242 880) |
| **Máximo de píxeles** | **40 000 000**, independiente del anterior |
| **Corruptas** | Rechazadas: la cabecera puede ser perfecta, y solo `load()` lo detecta |
| **MIME falso** | El contenido manda. Un PNG llamado `foto.jpg` se registra como `image/png` |
| **Dimensiones** | Leídas de la imagen real |
| **EXIF** | Ver §N |

**Los dos límites son independientes y ninguno sustituye al otro.** El de bytes
acota lo que viaja por la red; el de píxeles, lo que ocupa al descomprimirse. La
prueba lo demuestra con un PNG de **68 bytes** que declara 80 millones de
píxeles: pasa holgadamente el límite de tamaño y agotaría la memoria.

**Límite exacto probado en su valor y en el valor más uno.** El PNG de tamaño
exacto se construye con un fragmento auxiliar privado (`prVt`), que el estándar
obliga a ignorar: la imagen sigue siendo válida y decodificable.

**SVG queda fuera por seguridad**: es XML con capacidad de script. **GIF queda
fuera** porque la animación complica la miniatura y ningún flujo la pide.

---

## N. Miniaturas

| Aspecto | Decisión |
| --- | --- |
| **Cuándo** | **Siempre** al subir |
| **Dimensiones** | Caja de **480 × 480** |
| **Aspect ratio** | **Conservado** |
| **Upscale** | **Nunca** |
| **Formato** | **WebP** |
| **Calidad** | **82** |
| **Clave** | `medios/<uuid>/thumbnail.webp`, **derivada** de la del original |
| **Persistencia** | **Ninguna fila y ninguna columna** |

**Orientación EXIF: se aplica.** Una fotografía horizontal con orientación 6
produce una miniatura vertical. Ignorarla deja las fotos de móvil tumbadas en el
listado, que es un defecto visible.

**EXIF del original: no se copia.** Lleva modelo de cámara y a menudo GPS, y la
miniatura se sirve públicamente.

**Modos de imagen.** PNG admite paleta (`P`) y escala de grises (`L`), que WebP
no escribe directamente. Se convierten antes, conservando el alfa si lo hay. Sin
esa conversión, subir una captura de pantalla indexada —caso normal, no raro—
rompería la subida entera con un error del decodificador.

**Por qué no hay tabla ni columna nueva.** La clave se deriva de `object_key`, así
que persistirla crearía el segundo estado que **D-O** de `data-model.md` rechaza.
Hay una prueba que borra un medio y comprueba que **la miniatura también
desaparece**, conociendo solo el `object_key`: si la derivación se rompiera, esa
prueba se pondría roja.

---

## O. Checksum

| Aspecto | Valor |
| --- | --- |
| **Algoritmo** | SHA-256 en hexadecimal, 64 caracteres |
| **Sobre qué** | Los **bytes almacenados**, nunca el nombre |
| **Deduplicación** | **No** |

**Decisión D-010-J.** El esquema reserva la columna y su índice para *detectar*
duplicados. Detectar y **reutilizar** son decisiones distintas: reutilizar en
silencio haría que borrar un medio afectara a contenidos que nunca lo subieron, y
convertiría una operación de limpieza en un daño invisible. Dos subidas del mismo
archivo producen dos filas con el **mismo** checksum y claves distintas, y hay una
prueba que lo fija. Presentar el duplicado al administrador es de `Task/012`.

---

## P. `MediaAsset`

| | |
| --- | --- |
| **Qué persiste** | `object_key`, `original_filename`, `mime_type`, `size_bytes`, `width`, `height`, `checksum`, `alt_text` (nulo) |
| **Qué NO persiste** | Binarios, URL de ninguna clase, respuestas del SDK, clave de la miniatura |
| **PostgreSQL real** | `personal_blog_test`, guarda *fail-closed* activa. **SQLite no se usó** |
| **Cambio de esquema** | **Ninguno** |

Hay dos pruebas independientes sobre la ausencia de binarios y URL: una sobre la
estructura que se pasa al repositorio, y otra sobre las **columnas reales** de la
fila después de haber servido una respuesta con enlace.

`alt_text` sigue admitiendo nulo al subir (**D-010-N**): `data-model.md` dice que
se escribe *al usar* la imagen, no al cargarla, y el flujo B.4 no lo pide.
Exigirlo aquí obligaría a inventar un texto alternativo antes de saber en qué
contenido va a aparecer la imagen.

---

## Q. Consistencia entre almacenamiento y PostgreSQL

**No existe transacción entre los dos sistemas.** No es un detalle a posponer: es
la propiedad que decide el diseño.

**Orden de la subida:**

```
validar → derivar miniatura → guardar original → guardar miniatura → persistir
```

| Punto de fallo | Comportamiento | Prueba |
| --- | --- | --- |
| Validación | Se propaga. **Cero llamadas** al almacenamiento | P-07 |
| Guardar el original | Se propaga. **No** hay fila | P-04 |
| Guardar la miniatura | Se propaga. **Se elimina el original** | P-05 |
| Persistir en la base | Se propaga. **Se eliminan las dos claves** | P-03 |
| **La compensación también falla** | Se propaga el error **original**; el fallo de la limpieza se **registra** | P-06 |

**Por qué persistir al final.** De los dos estados a medias posibles hay que
elegir el tolerable: un objeto sin fila es basura que ocupa espacio; una fila sin
objeto es **una imagen rota en el blog publicado**. Se elige el primero.

**El borrado aplica la misma asimetría al revés**: primero la fila, después los
objetos, con su prueba dedicada.

**El fallo de compensación no se oculta.** No se propaga —taparía la causa real y
el diagnóstico apuntaría al sitio equivocado— pero se registra con
`logger.exception`, la clave huérfana y el tipo del error original. Hay una prueba
que comprueba que ese registro se emite: es la única pista de que quedó basura en
el bucket.

---

## R. Borrado y «medio en uso»

**Propietario: `Task/010`**, y no por interpretación. `data-model.md`,
invariante 12, lo asigna por nombre: *«Base: `RESTRICT`, infranqueable.
`Task/010`: comprobación previa que dice **dónde** se usa (B.5)»*.

| Nivel | Qué hace | Dónde |
| --- | --- | --- |
| **Técnico** | `ObjectStorage.eliminar(clave)`, que no sabe nada de referencias | `app/shared/storage/` |
| **Aplicación** | `EliminarMedio`: busca, consulta los cinco orígenes, rechaza o borra | `app/modules/media/application/` |
| **Base de datos** | `ON DELETE RESTRICT` en las cinco claves foráneas | `Task/008` |

Las tres capas son complementarias: la de arriba da un mensaje útil, la de abajo
garantiza que ningún camino deja una referencia rota.

**El error dice dónde.** `MedioEnUsoError` lleva en `details.usos` el tipo, el
`slug` y el título de **cada** contenido que referencia el medio —no solo el
primero—, en la forma que `api-contracts.md` §7 reserva para el contexto
estructurado. Probado para portada de artículo, review y proyecto, foto de perfil,
miniatura de vídeo, y el caso de **dos usos simultáneos**.

**Ningún módulo de almacenamiento conoce claves foráneas.** Comprobado con un
import en subproceso limpio.

**Qué queda para `Task/012`:** el endpoint `DELETE /api/v1/admin/media/{id}`, su
autenticación y su auditoría. El comportamiento ya está aquí y probado.

---

## S. Acceso público a los medios — **D-009-O**

### Esquema anterior y nuevo

```jsonc
// Task/009                          // Task/010
{                                    {
  "alt_text": "…",                     "alt_text": "…",
  "width": 1200,                       "width": 1200,
  "height": 800                        "height": 800,
}                                      "access_url": "https://…?X-Amz-Signature=…"
                                     }
```

Cambio **compatible**: añade un campo opcional y no retira ni renombra ninguno
(api-contracts.md §10, regla 3). Los cinco DTO que anidan un medio lo llevan.

| Pregunta | Respuesta |
| --- | --- |
| **Campo de acceso** | `access_url` — enlace **temporal**, generado al servir |
| **¿`object_key` expuesto como campo?** | **NO** |
| **¿URL persistida?** | **NO** — comprobado sobre las columnas reales tras servir la respuesta |
| **TTL** | **Configuración**: `BLOG_STORAGE_ACCESS_TTL_SECONDS`, 900 s por defecto |
| **Política productiva** | **`Task/030`** (**D-08**) |

**Por qué no hay `access_expires_at`.** Se evaluó y se descartó: declarar cuándo
caduca el enlace *es* describir su **semántica de caché**, que es literalmente una
de las preguntas que D-08 deja a `Task/030`. Añadirlo después sería compatible;
retirarlo, no.

### S.1 Defecto corregido: el enlace local no era consumible

**Lo que había.** El backend en Docker opera contra `http://minio:9000`, que es
correcto: es como el contenedor alcanza MinIO. Pero el `access_url` se firmaba
contra **ese mismo** endpoint, y su consumidor no es el backend: es el navegador
del host, que **no resuelve el nombre `minio`**.

Medido con la implementación anterior:

```
endpoint operativo configurado : http://minio:9000
host que aparece en access_url : minio:9000
GET desde el host              : FALLA -> URLError: getaddrinfo failed
```

**Por qué no se arregla reescribiendo la URL.** El `Host` forma parte de la
petición canónica de **AWS Signature Version 4**. Comprobado contra MinIO real:

```
1) URL firmada contra 127.0.0.1, usada TAL CUAL : (200, b'contenido')
2) MISMA URL con el host reescrito a localhost   : (403, 'SignatureDoesNotMatch')
```

Es decir: la corrección tenía que ocurrir **antes** de firmar, no después.

**Diseño.** Se separan dos direcciones hacia el mismo almacenamiento:

| Endpoint | Quién lo ve | Para qué | Valor en Compose |
| --- | --- | --- | --- |
| **Operativo** (`storage_endpoint_url`) | El backend | `put`, `get`, `head`, `delete` | `http://minio:9000` |
| **De acceso** (`storage_access_endpoint_url`) | El consumidor del enlace | Firmar `access_url` | `http://localhost:9000` |

El adaptador mantiene **dos clientes**: el operativo y el de firma, con el mismo
bucket, región y credenciales. `generate_presigned_url` no hace ninguna petición
de red —es un HMAC local—, así que el cliente de firma funciona perfectamente
configurado con un endpoint que el contenedor **no** alcanza. Esa propiedad es
justamente la que hace viable la solución.

**Sin coste para producción.** `storage_access_endpoint_url` es **opcional**.
Omitido, se firma con el cliente operativo, que es lo que ya ocurría. Con
`provider=s3` y sin endpoints declarados, el SDK resuelve el de AWS y firma
contra él. `Task/010` **no impone ninguna configuración productiva nueva**: una
URL estable, un dominio propio o un CDN siguen siendo de `Task/030` (**D-08**).

**El hook es abstracto, no heredado.** `_crear_cliente_de_firma` no tiene
implementación por defecto en la base: un adaptador nuevo está obligado a
decidir si el anfitrión que ve su consumidor coincide con el que ve el backend.
Heredar un `None` silencioso es exactamente cómo se cuela este defecto.

### S.2 Evidencia RED → GREEN → REFACTOR del defecto

Es un defecto real, así que se corrigió con el ciclo completo. **Sin bug fix sin
test de regresión** (`BACKEND_TESTING_STRATEGY.md` §11): las pruebas se quedan.

| | |
| --- | --- |
| **Tests escritos primero** | 9 en `tests/unit/test_adaptadores_de_almacenamiento.py`, 4 en `tests/unit/test_configuracion_de_almacenamiento.py`, 2 en `tests/contract/test_contrato_de_object_storage.py` |
| **Comando RED** | `pytest tests/unit/test_adaptadores_de_almacenamiento.py -q` |
| **RED** | `9 failed, 12 passed in 0.78s` |
| **Razón** | `TypeError: MinIOStorage.__init__() got an unexpected keyword argument 'access_endpoint_url'` y `AttributeError: '_cliente_de_firma'` — la separación no existía |
| **RED (configuración)** | `4 failed, 14 passed` — `AttributeError: 'Settings' object has no attribute 'storage_access_endpoint_url'` |
| **RED (contrato)** | `30 errors` — `TypeError` al construir los adaptadores del harness |
| **Implementación** | `_cliente_de_firma` en la base; `access_endpoint_url` en los dos adaptadores; `storage_access_endpoint_url` en `Settings`, con validación *fail-fast*; propagación en la fábrica |
| **GREEN** | `21 passed` (adaptadores) · `39 passed` (configuración) · **`30 passed`** (contrato, 15 casos × 2) |
| **REFACTOR** | Se extrajo `_construir_cliente(endpoint_url)` en cada adaptador, para que operativo y firma compartan la construcción y no puedan divergir. Y se hizo **abstracto** `_crear_cliente_de_firma` al detectar que su implementación por defecto era código muerto: se eliminó en lugar de excluirla de cobertura |

**La prueba que de verdad cierra el defecto** no comprueba una cadena, sino que
el enlace **sirve**: guarda el objeto por el endpoint operativo, firma contra el
de acceso —que es **otro anfitrión**— y descarga la URL **exactamente como se
emitió**, sin tocar anfitrión, ruta ni cadena de consulta. Espera `200` y bytes
idénticos. La acompaña un control negativo que reescribe el anfitrión y exige
`403`: sin él, alguien podría «simplificar» el diseño reescribiendo la cadena y
la aserción seguiría pareciendo correcta.

Se añadió también una **mutación** (§Y): firmar con el cliente operativo en
lugar del de firma pone rojas 7 pruebas, incluida la descarga real.

---

### Hallazgo: la URL prefirmada contiene `object_key`

Es el hallazgo principal de la tarea y se registra entero, incluido cómo se
resolvió.

**Qué pasó.** Al implementar el campo, la prueba de `Task/009`
`test_la_portada_no_expone_la_clave_del_objeto` se puso roja:

```
assert 'portadas/secreta.png' not in cuerpo
  'portadas/secreta.png' is contained here:
  …/bucket-de-prueba/portadas/secreta.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&…
```

**Qué se hizo.** Se detuvo el trabajo y se contrastaron las fuentes canónicas
**antes** de tocar ninguna expectativa, como exige
`BACKEND_TESTING_STRATEGY.md` §9.

**La contradicción, enunciada con precisión.** Una URL prefirmada **es**
`<endpoint>/<bucket>/<object_key>?X-Amz-...`: la clave es la ruta del recurso que
se firma, y **no existe variante del mecanismo que la omita**. El mecanismo
tampoco es opcional:

- `CONTENT_MODEL.md` §3.7: *«El acceso en producción se hace mediante **URL
  prefirmada** sobre un bucket privado.»*
- `security-boundaries.md`: *«C-01 / C-02 Navegador → C-08 Almacenamiento: sí,
  solo lectura, **únicamente mediante URL prefirmada emitida por el backend**.»*

Las dos exigencias —«URL prefirmada» y «la clave no aparece en la respuesta», en
su lectura más literal— **no pueden cumplirse a la vez**.

**Cómo se resolvió, y por qué así.** La invariante 9 no dice «nunca aparece»:
dice que no se exponen claves de objeto **«sin control»**. Una URL firmada, con
caducidad, sobre un bucket privado **es** la exposición controlada. La garantía
exacta, que es la que ahora fijan las pruebas, es:

1. **Ningún campo del contrato transporta `object_key`** como dato. Eso es lo que
   la convertiría en parte del contrato `v1`, del que ya no podría retirarse.
2. Fuera del enlace firmado, **no aparece** en ninguna respuesta.
3. **Conocerla no da acceso**: el bucket es privado, hace falta la firma, y las
   claves son no predecibles, así que ver una no permite adivinar otra.

**Se descartó** la alternativa de servir los medios por un endpoint propio del
backend: inventaría un endpoint que ninguna fuente vigente pide y contradiría el
límite C-01→C-08 de `security-boundaries.md`.

**Dónde queda escrito.** Decisión **D-010-Q** en la ficha §12;
`api-contracts.md` §12 nuevo; precisión de la invariante 9 en `CONTENT_MODEL.md`,
fechada y atribuida, con el mismo formato que `Task/008` usó para la invariante 1.

**Cómo se comprueba.** Las pruebas serializan el JSON **entero**, retiran los
valores de `access_url` y exigen que ni la clave ni la cadena `object_key` ni el
prefijo `medios/` ni la palabra `bucket` aparezcan en lo que queda. Se aplica a
los ocho recursos públicos que pueden llevar un medio. Y tiene guarda
anti-tautología doble: se comprueba que el medio **sí** llega a la respuesta y
que la clave **sí** está dentro del enlace, para que retirarlo no vacíe la prueba.

### Eficiencia

Emitir un enlace por elemento **no** cuesta una llamada de red: prefirmar es un
HMAC sobre la petición canónica, aritmética local. Está afirmado por prueba
apuntando a un **puerto cerrado** (`127.0.0.1:1`): si hubiera E/S, fallaría. No
se introdujo ningún N+1: el medio ya venía cargado por las consultas de
`Task/009`.

---

## T. Regresión de la API pública

| Comprobación | Resultado |
| --- | --- |
| Los **diez** endpoints públicos | **Verdes** |
| Suite completa de `Task/009` | **Verde** |
| Borradores y archivados siguen sin salir | **Verde** |
| Paginación, filtros, orden y búsqueda | **Verdes**, sin cambios |
| `404` idéntico para inexistente y no publicado | **Verde** |
| `MediaAsset` nulo sigue siendo `null` | **Verde** |
| Fuga de `object_key` como campo | **Ninguna** |

Se añadió cobertura para los medios en los ocho recursos que pueden llevarlos,
incluidos `thumbnail` de vídeo y `photo` de perfil, que son los dos que faltaban
por ejercitar con un medio real.

---

## U. OpenAPI

| Comprobación | Resultado |
| --- | --- |
| Cambios en el esquema | **Uno**: `MedioPublico` gana `access_url` |
| Rutas declaradas | Las **once** de siempre (10 públicas + `/health`), sin cambios |
| Endpoints administrativos | **0** |
| Endpoint de subida | **0** |
| `object_key`, `bucket`, `region`, `aws`, `minio`, `s3` en el esquema del medio | **Ninguno** — prueba dedicada |

La prueba del conjunto de campos sigue siendo **cerrada** (`==`, no «contiene»),
así que un campo de más se detecta.

---

## V. PostgreSQL

| Campo | Valor |
| --- | --- |
| Base de pruebas | `personal_blog_test` |
| Guarda | Sufijo `_test` **y** marca `personal-blog:test-database` dentro de la base |
| Fixtures nuevas en `tests/integration/` | **Ninguna** — las pruebas nuevas usan las existentes, así que la cadena hasta el resolutor verificado se mantiene intacta |
| Comprobación estructural del grafo | **Verde**, con los dos módulos nuevos registrados |
| SQLite | **NO** |

---

## W. MinIO

| Campo | Valor |
| --- | --- |
| Estado antes | `minio Up 40 hours (healthy)` |
| Estado después | `healthy`, **sin reinicios ni recreaciones**: solo se recreó el backend |
| Bucket de pruebas | Creado y destruido por la suite, `personal-blog-test-<hex>` |
| Bucket de smoke | `personal-blog-test-smoke-f1400a0b`, creado y destruido |
| Roundtrip | **Correcto en las dos implementaciones** |
| Objetos residuales | **0** |
| Buckets de prueba residuales | **0** |
| Bucket de desarrollo | `personal-blog-media`, vacío y **privado** — infraestructura, no residuo |

**Smoke técnico, ejecutado a través de `ObjectStorage`:**

```
--- MinIOStorage ---                    --- S3Storage ---
  guardar        : 2048 bytes             guardar        : 2048 bytes
  existe         : True                   existe         : True
  bytes identicos: True                   bytes identicos: True
  acceso temporal: firmado=True           acceso temporal: firmado=True
                   secreto_fuera=True                      secreto_fuera=True
  eliminar       : existe=False           eliminar       : existe=False
                   no encontrado=SI                        no encontrado=SI

bucket de smoke eliminado. Buckets restantes: []
```

No se ejecutó `docker compose down -v`, ni `docker volume rm`, ni
`volume prune`, ni `system prune`. No se usaron datos reales.

### W.1 El backend en Docker ejecuta de verdad esta implementación

La primera entrega dejaba el contenedor sin recrear, así que la configuración
nueva no estaba en marcha. Corregido, sin destruir nada:

```
docker compose up -d --build backend
```

Sin `down -v`, sin tocar volúmenes, sin recrear PostgreSQL ni MinIO —los dos
siguen con **40 horas** de *uptime*—.

| Servicio | Estado |
| --- | --- |
| **backend** | **Recreado y reconstruido** · `Up (healthy)` |
| minio | `Up 40 hours (healthy)` — no se tocó |
| postgres | `Up 40 hours (healthy)` — no se tocó |
| traefik | `Up 40 hours (healthy)` |
| frontend | `Up 40 hours (healthy)` |
| portainer | `Up` |

Configuración **realmente presente dentro del contenedor** (`env` del proceso,
con el secreto oculto):

```
BLOG_STORAGE_PROVIDER=minio
BLOG_STORAGE_BUCKET=personal-blog-media
BLOG_STORAGE_REGION=us-east-1
BLOG_STORAGE_ENDPOINT_URL=http://minio:9000
BLOG_STORAGE_ACCESS_ENDPOINT_URL=http://localhost:9000
BLOG_STORAGE_ACCESS_KEY=blog_minio_local
BLOG_STORAGE_ACCESS_TTL_SECONDS=900
BLOG_STORAGE_SECRET_KEY=<oculto>
```

### W.2 Smoke extremo a extremo desde el contenedor recreado

Ejecutado **dentro** del contenedor, con `get_settings()`, la fábrica real y la
dependencia real que emite el enlace —el mismo camino de código que usa el
endpoint HTTP—:

| Paso | Resultado |
| --- | --- |
| Endpoint operativo leído del contenedor | `http://minio:9000` |
| Endpoint de acceso leído del contenedor | `http://localhost:9000` |
| Subida de una imagen real (`SubirImagen`) | Correcta: original + miniatura |
| Anfitrión del `access_url` emitido | **`localhost:9000`** |
| Enlace firmado | Sí (`X-Amz-Signature`) |
| **`GET` desde el HOST con la URL exacta** | **`200`** |
| URL modificada después de firmar | **NO** |
| `Content-Type` | `image/png` |
| Bytes | **666 = 666**, SHA-256 idéntico |
| Control negativo: mismo enlace con el anfitrión reescrito | **`403 SignatureDoesNotMatch`** |

**No se tocó `personal_blog`.** El `MediaAsset` se construyó en memoria, sin
persistir: lo que este smoke demuestra es la **configuración del contenedor**, y
la persistencia ya está probada contra `personal_blog_test`. Es la opción más
segura de las dos que la revisión admitía, y no deja contenido ficticio en la
base de desarrollo.

**Limpieza:** los dos objetos se borraron desde el propio contenedor; el bucket
`personal-blog-media` quedó **vacío** y **privado**; los archivos temporales se
eliminaron del host y del contenedor.

### W.3 Bucket de desarrollo

`personal-blog-media` **existe**, creado con el procedimiento del runbook §10, y
su permiso de acceso anónimo es **`private`** (verificado con `mc anonymous
get`). No es un residuo: es infraestructura local de desarrollo, y no se usa
como destino de pruebas — la suite sigue creando y destruyendo únicamente
buckets `personal-blog-test-*`.

### Incidencia observada y resuelta

Un bucket de pruebas quedó huérfano tras cortar por tiempo de espera una
ejecución de cobertura: la limpieza vive en un `finally` y **no sobrevive a un
`SIGKILL`**. Se purgó **por la ruta con guarda** —`_vaciar_y_borrar_el_bucket`,
que vuelve a comprobar el prefijo— y quedó documentado en el harness y en el
runbook §10.3. No se corrige con un manejador de señales: añadiría una ruta de
código difícil de probar para un caso que no corrompe nada, y el prefijo ya hace
el residuo inequívocamente descartable.

---

## X. Migraciones

| Campo | Valor |
| --- | --- |
| **¿Se cambió el esquema?** | **NO** |
| `head` | **`0002`**, sin cambios |
| `0001` y `0002` | **Intactas.** No se tocó ni un byte |
| Migración nueva | **Ninguna** |

**Por qué no hizo falta.** Todo lo que `Task/010` necesita persistir ya cabe en
`media_assets`: `object_key`, `mime_type`, `size_bytes`, `width`, `height` y
`checksum` existen desde `Task/008`. La miniatura no necesita columna porque su
clave se **deriva**, y una URL prefirmada no se persiste por definición.

---

## Y. Quality gates

Todos ejecutados con PostgreSQL y MinIO reales disponibles.

| Gate | Comando | Resultado |
| --- | --- | --- |
| Lint | `ruff check .` | **All checks passed!** |
| Formato | `ruff format --check .` | **179 files already formatted** |
| Tipado | `mypy .` | **Success: no issues found in 177 source files** |
| Unitarias | `pytest tests/unit -q` | **212 passed** |
| Contrato | `pytest tests/contract -q` | **219 passed** |
| Integración | `pytest -m integration -q` | **291 passed, 502 deselected** |
| **Suite completa** | `pytest -q` | **792 passed, 1 skipped** |
| **Advertencias** | `pytest -q -W error` | **792 passed, 1 skipped** — **0 warnings** |
| **Cobertura** | `pytest --cov -q` | **TOTAL 1835 sentencias, 0 sin cubrir, 150 ramas, 0 parciales — 100 %** |
| Dependencias | `pip check` | **No broken requirements found** |
| Espacios | `git diff --check` | limpio en ambos repositorios |
| Compose | `docker compose config` | **válido** |
| Migraciones | `alembic heads` | **`0002 (head)`** — sin cambios |

**La única omisión** es `tests/test_logging_utc.py::…`, por `time.tzset` inexistente
en Windows. Es **preexistente** desde `Task/005` y no tiene relación con esta tarea.

**Comparación con el baseline de `Task/009`:** 597 → **792** pruebas (+195), con
cobertura de `app/` en **100 %** en ambos casos.

### Exclusión de cobertura añadida

**Una sola**, justificada en el propio `pyproject.toml`: el cuerpo `...` de un
método de `Protocol`. No es código ejecutable —el `...` solo existe porque Python exige un
cuerpo— y quien implementa el protocolo **sí** se ejecuta y se prueba contra
PostgreSQL real. Contarlo empujaría a escribir una prueba que instancia el
protocolo, que no comprobaría nada.

### Comprobaciones de mutación

Seis mutaciones **temporales**, todas restauradas inmediatamente. Demuestran que
las pruebas muerden donde importa:

| # | Mutación | Resultado |
| --- | --- | --- |
| 1 | Clave de objeto predecible (`medios/uploads` fijo) | **2 rojas** — `test_las_claves_no_son_predecibles`, `test_dos_cargas_del_mismo_nombre_producen_claves_distintas` |
| 2 | Sin compensación tras fallo de base de datos | **2 rojas** — `test_si_la_persistencia_falla_no_queda_ningun_objeto`, `test_el_fallo_de_la_compensacion_se_registra` |
| 3 | `object_key` expuesto como campo público | **14 rojas**, incluidas las de OpenAPI y las de no filtración |
| 4 | Se confía en la cabecera y no se decodifica | **1 roja** — `test_una_imagen_truncada_se_rechaza` |
| 5 | Guarda *fail-closed* del destino desactivada | **4 rojas** en `test_un_endpoint_que_no_es_local_se_rechaza` |
| 6 | El enlace se firma con el cliente **operativo** en vez del de acceso | **7 rojas**, incluidas las dos descargas reales del contrato |

Tras restaurar cada una, las suites afectadas volvieron a verde.

> **La mutación no sustituye al RED, en ningún caso.** Demuestra una cosa
> distinta y más estrecha: que una prueba **es sensible** al defecto que dice
> vigilar. No dice nada sobre *cuándo* se escribió esa prueba, que es lo único
> que el ciclo RED → GREEN acredita. Donde no hubo RED —las cinco guardas del
> §K.2— no hubo RED, y la mutación no lo repara: solo confirma que esas guardas
> sirven como red de regresión. Fabricar un RED escribiendo código incorrecto a
> propósito para después «corregirlo» sería falsificar la historia, y no se
> hizo.

---

## Z. Dependencias externas

| Elemento | Usado |
| --- | --- |
| AWS real | **NO** |
| Amazon S3 real | **NO** |
| Credenciales AWS | **NO** |
| Terraform | **NO** |
| Floci | **NO** |
| LocalStack / Moto | **NO** |
| SSM / Lambda / API Gateway | **NO** |
| Recursos cloud de cualquier tipo | **NINGUNO** |

`S3Storage` se ejerció exclusivamente contra el endpoint S3-compatible del MinIO
local del entorno de `Task/007`.

---

## AA. Documentación y archivos

### Backend — creados

`app/shared/storage/` (`__init__`, `contrato`, `errores`, `s3_compatible`,
`minio`, `s3`, `fabrica`) · `app/modules/media/domain/` (`__init__`, `claves`,
`errores`, `validacion`, `miniaturas`) · `app/modules/media/application/`
(`__init__`, `repositorio`, `subir_imagen`, `eliminar_medio`) ·
`app/modules/media/infrastructure/repositorio.py` ·
`app/modules/media/presentation/acceso.py` · `tests/almacenamiento_de_pruebas.py`
· `tests/imagenes.py` · `tests/contract/test_contrato_de_object_storage.py` ·
`tests/integration/test_medios_persistidos.py` ·
`tests/integration/test_acceso_publico_a_medios.py` ·
`tests/test_guarda_del_almacenamiento_de_pruebas.py` · y seis módulos en
`tests/unit/` (`test_adaptadores_de_almacenamiento`,
`test_configuracion_de_almacenamiento`, `test_errores_del_almacenamiento`,
`test_claves_de_medios`, `test_validacion_de_imagenes`, `test_miniaturas`,
`test_subir_imagen`).

### Backend — modificados

`app/shared/configuration/settings.py` (7 campos, 2 validadores) ·
`app/shared/errors/exceptions.py` (2 errores base) ·
`app/modules/media/presentation/schemas.py` · los 5 pares router/schemas que
anidan un medio · `pyproject.toml` · `requirements.txt` · `requirements-dev.txt`
· `.env.example` · `README.md` · `tests/__init__.py` · `tests/conftest.py` · y
las 8 pruebas de §K.1.

### Infra — modificados

`docs/tasks/TASK-010-s3-compatible-storage.md` *(creado)* ·
`docs/task-reports/TASK-010-report.md` *(este)* ·
`docs/project-management/STATUS.md` · `docs/project-management/ROADMAP.md` ·
`docs/stages/STAGE-03-domain-and-backend.md` ·
`docs/architecture/api-contracts.md` (§11 y §12 nuevo) ·
`docs/architecture/data-model.md` (§4.1, §7 invariantes 10/12/13, §10) ·
`docs/architecture/software-architecture.md` (§3.7) ·
`docs/architecture/security-boundaries.md` ·
`docs/architecture/open-decisions.md` (**D-08**) ·
`docs/product/CONTENT_MODEL.md` (invariante 9 y §3.7) ·
`docs/runbooks/local-environment.md` (§10 nuevo) · `docker-compose.yml` ·
`.env.example`.

### Cambio de infraestructura local, y por qué

`docker-compose.yml` gana las siete variables `BLOG_STORAGE_*` del servicio
`backend` y un `depends_on: minio: service_healthy`. **No es un cambio por
reflejo:** `BLOG_STORAGE_BUCKET` es obligatoria, así que sin ellas el backend
**no arranca**. Las credenciales **no se duplican**: se reutilizan
`MINIO_ROOT_USER` y `MINIO_ROOT_PASSWORD`, para que no puedan quedar
descuadradas. El endpoint es `http://minio:9000` —nombre de servicio y puerto
interno—, con el mismo razonamiento que ya estaba escrito para PostgreSQL.

No se creó ningún servicio nuevo ni se tocó ningún volumen.

### Archivos tocados por la corrección posterior a la revisión

**Backend:** `app/shared/storage/s3_compatible.py` (cliente de firma),
`minio.py` y `s3.py` (endpoint de acceso y `_construir_cliente`),
`app/shared/configuration/settings.py` (`storage_access_endpoint_url` y su
validador), `app/shared/storage/fabrica.py` (propagación), `.env.example`,
`tests/almacenamiento_de_pruebas.py` (endpoint de acceso en el harness, con la
guarda aplicada también a él), y las tres suites con las 15 pruebas nuevas.

**Infra:** `docker-compose.yml` (`BLOG_STORAGE_ACCESS_ENDPOINT_URL`),
`.env.example`, `docs/runbooks/local-environment.md`,
`docs/architecture/software-architecture.md`, ficha y este reporte.

### Incidencia de entorno durante el cierre (no es un defecto de la tarea)

Al revalidar antes de los *commits*, la integración pasó de verde a **260
errores**. La causa no estaba en el código: **Windows había reservado el rango
TCP `55396–55495`**, que contiene el `55432` de PostgreSQL, así que Docker no
podía publicar el puerto y la base era inalcanzable **desde el host**.

Merece registrarse por dos motivos:

1. **La guarda *fail-closed* de `Task/005.6` se comportó exactamente como debía.**
   Con `PERSONAL_BLOG_TEST_DATABASE_URL` definida, el fallo de conexión fue
   `FAIL`, no `skip`. Una suite que hubiera degradado eso a omisión habría
   quedado «verde» con la base caída, que es el único momento en que esas
   pruebas tenían algo que decir.
2. **El síntoma es engañoso.** El contenedor figuraba `Up (healthy)` porque el
   proceso estaba sano; lo que faltaba era la publicación del puerto.

Resuelto liberando la reserva (`net stop winnat` / `net start winnat`, con
privilegios de administrador del usuario) y levantando el contenedor. **No se
usó `down -v`**: el volumen `personal-blog-local_postgres_data` se conservó
—misma fecha de creación, `2026-07-28T01:38:21Z`— y la marca
`personal-blog:test-database` seguía en su sitio. Procedimiento documentado en
el [runbook §10.5](../runbooks/local-environment.md).

Tras restaurarlo, la suite volvió a **792 pasan, 1 omitida**, con **100 %** de
cobertura.

### Corrección incidental

La tabla *Estado actual* del `README.md` del backend seguía describiendo
`Task/005` —decía que el modelo de datos «no existe todavía»—. Es drift anterior
a esta tarea, que `Task/008` y `Task/009` no corrigieron. Se actualizó, con nota
de la corrección; no era alcance de `Task/010` y se declara como tal.

---

## AB. Criterio 12 — estado duradero

Búsqueda dirigida en **los 14 documentos tocados** de infra, más el `README.md`
del backend, sobre los patrones: *PR abierto*, *pendiente de fusionar*, *hasta
que el usuario fusione*, *hasta completar normalización*, *rama remota
pendiente*, *Task/011 no inicia hasta*.

| Categoría | Recuento |
| --- | :---: |
| **A. Historia fechada** (válida: registro, no estado) | 3 — las notas de `Task/005.4`, `Task/008` y `Task/009` que ya existían |
| **B. Reglas permanentes** (válidas) | 2 — el invariante de ramas en `WORKFLOW`, no modificado |
| **C. Estado transitorio escrito como vigente** | **0** |

Lo que dicen los documentos durables:

- `Task/010`: **Aprobada** el 2026-08-28.
- `Task/011`: **Pendiente, no iniciada**.
- `Task/012`: **Pendiente, no iniciada**.
- Regla permanente ya escrita en `STATUS.md`: *«Al iniciarse, el estado real de
  Git se verifica **en vivo** y su rama nace desde `main` actualizado y limpio.»*

**No se escribió en ningún sitio** que exista un PR, que haya una rama publicada,
ni que `Task/011` dependa de fusionar nada.

---

## AC. Gobierno

| Campo | Valor |
| --- | --- |
| **`Task/010`** | **Aprobada** (2026-08-28) |
| **Avance global** | **9 de 41 — 22 %** *(sin cambios)* |
| **ETAPA 03** | **2 de 5 — 40 %** *(sin cambios)* |
| **`Task/011`** | **Pendiente, no iniciada** |
| **`Task/012`** | **Pendiente, no iniciada** |

El recuento **no** se incrementa: solo la aprobación del usuario lo cambia.

---

## AD. Estado de Git

**BACKEND**

| Campo | Valor |
| --- | --- |
| Rama | `Task/010-Almacenamiento-Compatible-S3` |
| Staging | **0** |
| Commits | **0** |
| Push | **0** |
| Merge | **0** |
| Pull request | **0** |

**INFRA**

| Campo | Valor |
| --- | --- |
| Rama | `Task/010-Almacenamiento-Compatible-S3` |
| Staging | **0** |
| Commits | **0** |
| Push | **0** |
| Merge | **0** |
| Pull request | **0** |

**FRONTEND**

| Campo | Valor |
| --- | --- |
| Rama | `main` |
| Cambios | **0** |
| Rama Task | **No existe** |

**Secretos:** ningún patrón de credencial en los archivos versionables. Las dos
únicas coincidencias de la búsqueda son los **placeholders publicados**
(`change-me-local-minio`, `change-me-local-postgres`), que el `.env` local
conserva sin rotar: es el **riesgo R-16**, preexistente y ya registrado en
`STATUS.md`. `Task/010` no introduce ninguno nuevo. Los `.env` reales siguen
ignorados por Git.

---

## AE. Veredicto

| Pregunta | Respuesta |
| --- | --- |
| ¿`ObjectStorage` completo y provider-neutral? | **SÍ** |
| ¿`MinIOStorage` completo? | **SÍ** |
| ¿`S3Storage` con código real? | **SÍ** |
| ¿Suite de contrato común a las dos? | **SÍ** — 13 casos × 2 |
| ¿MinIO real? | **SÍ** |
| ¿Sin AWS real? | **SÍ** |
| ¿TDD real por *slice*? | **SÍ**, con la clasificación exacta de §K.2: el contrato común y las siete guardas de endpoint tuvieron RED propio; cinco guardas de ausencia se declaran **regresión, no evidencia RED** |
| ¿La mutación se presenta como sustituto del RED? | **NO** — afirmación retirada; es evidencia complementaria de sensibilidad |
| ¿Validación de imagen real? | **SÍ** — por decodificación |
| ¿Claves no predecibles? | **SÍ** — UUID v4, 122 bits |
| ¿Miniaturas? | **SÍ** |
| ¿Consistencia almacenamiento/base? | **SÍ** — compensación probada en los cuatro puntos de fallo |
| ¿`object_key` privado? | **SÍ** — no es campo del contrato; ver §S |
| ¿El `access_url` local es realmente consumible? | **SÍ** — `GET` desde el host con la URL exacta: `200` y bytes idénticos (§W.2) |
| ¿La firma es válida sin reescribir la URL? | **SÍ** — se firma contra el endpoint de acceso desde el principio |
| ¿El backend en Docker ejecuta esta implementación? | **SÍ** — reconstruido, recreado y `healthy`, con la configuración verificada dentro del contenedor |
| ¿URL no persistida? | **SÍ** |
| ¿**D-009-O** cerrado correctamente? | **SÍ** |
| ¿`Task/030` respetada? | **SÍ** — D-08 sigue abierta |
| ¿`Task/012` respetada? | **SÍ** — sin endpoints administrativos |
| ¿`Task/018` respetada? | **SÍ** — solo la validación base |
| ¿`0001`/`0002` intactas? | **SÍ** — sin migración nueva |
| ¿Suite completa verde? | **SÍ** — 792 pasan, 1 omitida preexistente |
| ¿Cero advertencias? | **SÍ** |
| ¿Criterio 12, categoría C? | **0** |
| ¿0 commits / push / merge / PR? | **SÍ** |
| **¿`Task/010` lista para revisión?** | **SÍ** |

---

## AF. Cómo validarlo

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra
docker compose ps                       # minio y postgres: healthy

cd ..\personal-blog-backend
$env:PERSONAL_BLOG_TEST_DATABASE_URL="postgresql://<usuario>:<clave>@127.0.0.1:55432/personal_blog_test"
$env:PERSONAL_BLOG_TEST_STORAGE_ENDPOINT_URL="http://127.0.0.1:9000"
$env:PERSONAL_BLOG_TEST_STORAGE_ACCESS_KEY="<MINIO_ROOT_USER del .env de infra>"
$env:PERSONAL_BLOG_TEST_STORAGE_SECRET_KEY="<MINIO_ROOT_PASSWORD del .env de infra>"

.\.venv\Scripts\python.exe -m pytest -q -W error
.\.venv\Scripts\python.exe -m pytest --cov -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy .
.\.venv\Scripts\python.exe -m pip check
```

Ver solo el contrato ejecutándose contra **las dos** implementaciones:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/contract/test_contrato_de_object_storage.py -v
```

Cada caso aparece dos veces, `[minio]` y `[s3]`.

Comprobar que el backend en Docker ejecuta esta implementación:

```powershell
cd ..\personal-blog-infra
docker compose ps                       # backend healthy
docker compose exec backend sh -c "env | Select-String '^BLOG_STORAGE_(ENDPOINT|ACCESS_ENDPOINT)'"
```

Debe mostrar los **dos** endpoints, distintos:

```
BLOG_STORAGE_ENDPOINT_URL=http://minio:9000
BLOG_STORAGE_ACCESS_ENDPOINT_URL=http://localhost:9000
```

> **Ya está recreado y verificado** (§W.1). Si en el futuro cambian estas
> variables, el contenedor debe recrearse con
> `docker compose up -d --build backend` — nunca con `down -v`.
>
> El bucket `personal-blog-media` **ya existe** y es privado (§W.3). Para
> ejecutar las **pruebas** no hace falta: la suite crea y destruye el suyo.

---

## AG. Deuda registrada

### Deuda **cerrada dentro de la tarea**

| Deuda registrada en la primera entrega | Estado |
| --- | --- |
| *«La URL prefirmada local se firma contra `http://minio:9000`, que un navegador del host no alcanza»* | **CERRADA.** No se traslada a `Task/015` ni a `Task/016`: era un defecto de `Task/010` y se corrigió aquí (§S.1, §S.2, §W.2). Esas tareas consumirán un contrato que ya funciona |

### Deuda que sigue abierta

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | La limpieza del bucket de pruebas no sobrevive a un `SIGKILL`. Inofensiva: el prefijo hace el residuo inequívocamente descartable, y purgarlo está documentado | Aceptada y documentada |
| 2 | La miniatura se almacena pero no se expone en la API pública. Su clave se deriva, así que exponerla después es compatible | `Task/016` |
| 3 | El `checksum` se calcula pero nadie consulta duplicados todavía | `Task/012` |
| 4 | `SubirImagen` y `EliminarMedio` no emiten eventos de auditoría | `Task/012` |

### Lo que sigue siendo de `Task/030` (**D-08**)

Ninguna de estas es deuda de `Task/010`: son decisiones que la tarea no debe
tomar.

- Si existe una **URL estable** para los medios del contenido publicado, y por
  qué vía.
- **Semántica de caché** de esas URLs y su compatibilidad con un CDN.
- **Valor productivo del TTL** — aquí es configuración, no una constante.
- **CORS productivo**, política del bucket y *lifecycle*.
- `og:image`, cuyo propietario vigente es `Task/016`.

---

## AH. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** |
| **Fecha de aprobación** | *(pendiente)* |
| **Aprobado por** | *(pendiente — solo el usuario)* |
| **Expresión de aprobación** | `approved: Task/010-Almacenamiento-Compatible-S3` |

> No se ejecutará ningún commit, push, merge ni pull request hasta recibir esa
> expresión exacta.
