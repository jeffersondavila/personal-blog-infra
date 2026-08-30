# TASK-010 — Almacenamiento Compatible con S3

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/010-Almacenamiento-Compatible-S3` |
| **Nombre** | Almacenamiento compatible con S3 |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Estado** | **Aprobada** |
| **Repositorios involucrados** | `personal-blog-backend` (funcional) · `personal-blog-infra` (gobierno y documentación) |
| **Dependencias** | `Task/008-Modelo-de-Datos` (**Aprobada**) |
| **Rama** | `Task/010-Almacenamiento-Compatible-S3` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base backend** | `81347758dcc01eda55938a3bf0a298684c6c8a08` |
| **SHA base infra** | `64e237cde43a91c27ad41fb78b46cd17acf6a6f8` |
| **Fecha de inicio** | 2026-08-28 |
| **Última actualización** | 2026-08-28 |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

| # | Comprobación | Resultado |
| --- | --- | --- |
| 1 | `main == origin/main` | **Sí**, en los tres repositorios |
| 2 | Working tree limpio antes de crear la rama | **Sí**, en los tres repositorios |
| 3 | Rama creada **desde `main`** | **Sí**, en backend e infra |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | **Sí**; `git rev-list --count main..HEAD` = `0` |

`personal-blog-frontend` queda en `main`, **sin rama y sin cambios**: la tarea no le afecta.

---

## 1. Objetivo

Dotar al backend de una capa de almacenamiento de objetos **agnóstica del proveedor**: la
interfaz `ObjectStorage`, sus dos implementaciones reales —`MinIOStorage` y `S3Storage`—,
las pruebas de contrato **comunes** a ambas, la configuración que selecciona una u otra por
entorno, y la gestión de imágenes (validación, claves no predecibles, miniaturas y
persistencia de metadatos) que `Task/012` consumirá por HTTP.

## 2. Contexto

`Task/008` creó `media_assets` con `object_key` pero **sin nada que la escribiera**: la
propia ficha lo declaró («aquí no hay ni SDK ni cliente de almacenamiento»). `Task/009`
expuso `MediaAsset` públicamente con `alt_text`, `width` y `height` y **sin campo de
acceso**, dejando explícito en **D-009-O** que ese campo lo añade `Task/010`.

Tres documentos vigentes asignan a esta tarea el mismo pendiente:
[`api-contracts.md`](../architecture/api-contracts.md) §11,
[`data-model.md`](../architecture/data-model.md) §10 punto 10 y
[STAGE-03](../stages/STAGE-03-domain-and-backend.md). Esta tarea lo cierra en la parte que
le corresponde, y **solo** en esa parte: la política cloud concreta sigue siendo **D-08**,
de `Task/030`.

## 3. Dentro del alcance

- [x] Interfaz `ObjectStorage`, provider-neutral, en `app/shared/storage/`.
- [x] Tipos de resultado propios: no se devuelve ningún objeto del SDK.
- [x] Jerarquía mínima de errores de almacenamiento, sin filtrar credenciales.
- [x] `MinIOStorage` — implementación local, con guarda *fail-closed* contra AWS.
- [x] `S3Storage` — implementación de producción, **con código real**.
- [x] Suite de **contrato común** ejecutada contra **las dos** implementaciones.
- [x] Integración real contra el MinIO del entorno local, con bucket de prueba aislado.
- [x] Configuración de almacenamiento validada y *fail-fast*, y **selector por entorno**.
- [x] Generación de claves de objeto **no predecibles**.
- [x] Validación de imagen sobre el **contenido real**, no sobre la extensión ni el MIME
      declarado.
- [x] Generación de miniaturas con política documentada.
- [x] Caso de uso de subida: valida, almacena, persiste `MediaAsset` y **compensa** ante un
      fallo parcial.
- [x] Caso de uso de borrado con comprobación previa de uso que dice **dónde** se usa
      (invariante 12 de `data-model.md`, flujo B.5).
- [x] Campo de acceso en la representación pública de `MediaAsset` (**D-009-O**), compatible.

## 4. Fuera del alcance

| Excluido | Propietario |
| --- | --- |
| Bucket real de Amazon S3, políticas, CORS, *lifecycle*, expiración productiva de prefirmadas, **D-08** | `Task/030` |
| Ejecutar `S3Storage` contra Amazon S3 **real** | `Task/030` |
| *Wiring* productivo de `S3Storage` en Lambda | `Task/032` |
| Endpoints HTTP administrativos de medios (`POST`/`GET`/`DELETE /api/v1/admin/media`) | `Task/012` |
| Autenticación y protección de rutas administrativas | `Task/011` |
| Endurecimiento avanzado de la subida (antivirus, límites finales, CORS efectivo) | `Task/018` |
| `og:image` y estrategia de URL estable para SEO | `Task/016` |
| Terraform, SSM, recursos cloud de cualquier tipo | `Task/025`, `Task/030`+ |
| Frontend | ETAPA 04 |

**No se crea ningún recurso AWS. No se usan credenciales AWS reales.**

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Interfaz, tipos y errores | backend | `app/shared/storage/contrato.py`, `errores.py` |
| Base compartida sobre el SDK | backend | `app/shared/storage/s3_compatible.py` |
| Implementaciones | backend | `app/shared/storage/minio.py`, `s3.py` |
| Selector por entorno | backend | `app/shared/storage/fabrica.py` |
| Configuración | backend | `app/shared/configuration/settings.py`, `.env.example` |
| Separación de endpoints operativo / de acceso | backend | `app/shared/storage/s3_compatible.py`, `minio.py`, `s3.py` |
| Wiring del endpoint de acceso en local | infra | `docker-compose.yml`, `.env.example`, runbook §10 |
| Dominio de medios | backend | `app/modules/media/domain/` |
| Casos de uso | backend | `app/modules/media/application/` |
| Contrato de persistencia | backend | `app/modules/media/application/repositorio.py` |
| Repositorio y consulta de uso | backend | `app/modules/media/infrastructure/repositorio.py` |
| Emisión del enlace público | backend | `app/modules/media/presentation/acceso.py` |
| Campo de acceso público | backend | `app/modules/media/presentation/schemas.py` y los 5 DTO que lo anidan |
| Contrato de `ObjectStorage` | backend | `tests/contract/test_contrato_de_object_storage.py` |
| Harness de almacenamiento | backend | `tests/almacenamiento_de_pruebas.py`, registrado desde `tests/conftest.py` |
| Constructores de imágenes de prueba | backend | `tests/imagenes.py` |
| Guarda estructural del harness | backend | `tests/test_guarda_del_almacenamiento_de_pruebas.py` |
| Ficha y reporte | infra | `docs/tasks/TASK-010-*`, `docs/task-reports/TASK-010-report.md` |

## 6. Criterios de aceptación

1. `ObjectStorage` existe, es provider-neutral y su módulo de contrato no importa FastAPI,
   SQLAlchemy ni el SDK.
2. `MinIOStorage` y `S3Storage` existen **con código real** y superan **la misma** suite de
   contrato.
3. `MinIOStorage` se prueba contra el **MinIO real** del entorno local.
4. `S3Storage` se prueba **sin AWS real**, contra el endpoint S3-compatible local.
5. La integración de almacenamiento es *fail-closed*: no puede apuntar a un destino que no
   sea demostrablemente de pruebas.
6. La configuración selecciona el proveedor de forma centralizada y falla rápido cuando es
   inválida o incompleta.
7. Ningún secreto aparece en `repr`, logs ni mensajes de error.
8. La base de datos guarda `object_key` y metadatos; **nunca** binarios ni URL prefirmadas.
9. Las claves de objeto son no predecibles y un nombre de archivo hostil no las controla.
10. El MIME se valida contra el **contenido real** del archivo.
11. El límite de tamaño está definido y probado, incluido el límite exacto.
12. Las miniaturas cumplen una política documentada y probada.
13. Un fallo parcial no deja objetos huérfanos: la compensación está probada.
14. **Ningún campo del contrato público transporta `object_key`**, no aparece fuera del
    enlace firmado, y ninguna URL se persiste (**D-010-Q**).
15. La suite de `Task/009` sigue completa y verde; el esquema físico no cambia.
16. **El `access_url` que emite el backend en Docker es consumible desde el host**:
    firmado contra el endpoint de acceso desde el principio, sin reescrituras, y
    verificado con un `GET` real que devuelve `200` y los bytes correctos.

---

## 7. TDD / Plan test-first

### 7.1 Comportamientos a construir

1. Guardar, recuperar, comprobar, eliminar y generar acceso temporal sobre objetos, con
   semántica **idéntica** en las dos implementaciones.
2. Construir cada implementación desde la configuración, y rechazar la configuración
   inválida antes de que exista un cliente.
3. Derivar una clave de objeto no predecible a partir del formato validado.
4. Aceptar o rechazar un archivo según su contenido real.
5. Derivar una miniatura de una imagen válida.
6. Subir una imagen: validar, almacenar, persistir y compensar.
7. Eliminar un medio solo si no está en uso, diciendo dónde se usa cuando lo está.
8. Exponer públicamente un enlace de acceso al medio sin revelar su clave.

### 7.2 Matriz de casos

> Construida **antes** de escribir implementación. `MinIO` y `S3` en la columna *Provider*
> significan que el mismo caso se ejecuta contra **las dos** implementaciones.

#### A. Contrato de `ObjectStorage`

| Caso | Precondición | Operación | Resultado esperado | Capa | Provider |
| --- | --- | --- | --- | --- | --- |
| OS-01 | bucket de prueba vacío | `guardar` + `obtener` | los bytes recuperados son **idénticos**, incluido binario no textual | contrato | MinIO · S3 |
| OS-02 | objeto guardado | `existe` | `True` | contrato | MinIO · S3 |
| OS-03 | clave inexistente | `existe` | `False` | contrato | MinIO · S3 |
| OS-04 | objeto guardado | `eliminar` | deja de existir | contrato | MinIO · S3 |
| OS-05 | clave inexistente | `obtener` | `ObjetoNoEncontradoError` | contrato | MinIO · S3 |
| OS-06 | clave inexistente | `eliminar` | **no lanza**: la operación es idempotente | contrato | MinIO · S3 |
| OS-07 | objeto guardado con `image/png` | `obtener` | `tipo_de_contenido` preservado y `tamano_bytes` correcto | contrato | MinIO · S3 |
| OS-08 | clave con prefijos `a/b/c/…` | `guardar` + `obtener` | funciona; la clave se devuelve tal cual | contrato | MinIO · S3 |
| OS-09 | objeto guardado | `guardar` de nuevo con la misma clave | **sobrescribe**; `obtener` devuelve el contenido nuevo | contrato | MinIO · S3 |
| OS-10 | objeto guardado | `acceso_temporal` | URL absoluta que **descarga los mismos bytes** sin credenciales | contrato | MinIO · S3 |
| OS-11 | objeto guardado | `acceso_temporal` | la URL **no** contiene la clave secreta | contrato | MinIO · S3 |
| OS-12 | objeto guardado | `acceso_temporal(duracion)` | `expira_en` coherente con la duración pedida | contrato | MinIO · S3 |
| OS-13 | payload con los 256 valores de byte | `guardar` + `obtener` | ningún byte se corrompe | contrato | MinIO · S3 |

#### B. Implementaciones

| Caso | Precondición | Operación | Resultado esperado | Capa | Provider |
| --- | --- | --- | --- | --- | --- |
| M-01 | endpoint del MinIO local | suite OS-01..OS-13 | verde | integración | MinIO |
| M-02 | endpoint de AWS | construir `MinIOStorage` | `ConfiguracionDeAlmacenamientoInvalidaError`: el adaptador local **no puede** hablar con AWS | unitaria | MinIO |
| M-03 | sin endpoint | construir `MinIOStorage` | `ConfiguracionDeAlmacenamientoInvalidaError` | unitaria | MinIO |
| S-01 | endpoint S3-compatible local | suite OS-01..OS-13 | verde | integración | S3 |
| S-02 | sin endpoint declarado | construir `S3Storage` | se construye; resuelve el endpoint de AWS por su cuenta | unitaria | S3 |
| S-03 | bucket inexistente | `obtener` | `FalloDelProveedorDeAlmacenamientoError`, **sin** credenciales en el mensaje | integración | S3 |
| S-04 | — | inspección de `S3Storage` | **no** crea el bucket al construirse ni al operar | unitaria | S3 |

#### B'. Separación de endpoints (operativo frente a acceso)

> Añadido tras la revisión externa: el enlace local no era consumible.

| Caso | Precondición | Operación | Resultado esperado | Capa | Provider |
| --- | --- | --- | --- | --- | --- |
| E-01 | operativo `minio:9000`, acceso `localhost:9000` | `acceso_temporal` | la URL empieza por el endpoint **de acceso**; `minio:9000` no aparece | unitaria | MinIO |
| E-02 | igual | inspección de los clientes | el operativo apunta al interno y el de firma al externo | unitaria | MinIO |
| E-03 | sin endpoint de acceso | `acceso_temporal` | se firma contra el operativo; **es el mismo objeto cliente** | unitaria | MinIO |
| E-04 | endpoint de acceso malformado | construir | `ConfiguracionDeAlmacenamientoInvalidaError` | unitaria | MinIO |
| E-05 | endpoint de acceso de AWS | construir `MinIOStorage` | rechazado, igual que el operativo | unitaria | MinIO |
| E-06 | `S3Storage` sin endpoints | `acceso_temporal` | firma contra el endpoint de AWS resuelto por el SDK | unitaria | S3 |
| E-07 | `S3Storage` con los dos endpoints | `acceso_temporal` | usa el de acceso; las operaciones, el operativo | unitaria | S3 |
| E-08 | configuración del Compose | `crear_almacenamiento` | los dos endpoints llegan al adaptador | unitaria | — |
| E-09 | configuración del Compose | `acceso_temporal` | la URL apunta al host, no a `minio:9000` | unitaria | — |
| E-10 | endpoint de acceso malformado en `Settings` | arrancar | `ConfigurationError` *fail-fast* | unitaria | — |
| E-11 | producción sin endpoints | arrancar y firmar | funciona; **no** hay configuración nueva obligatoria | unitaria | S3 |
| **E-12** | objeto guardado por el endpoint operativo | firmar contra el de acceso y **descargar la URL exacta** | **`200`** y bytes idénticos, sin modificar la URL | contrato | MinIO · S3 |
| **E-13** | enlace ya firmado | reescribir el anfitrión y descargar | **`403`** — fija por qué la separación ocurre antes de firmar | contrato | MinIO · S3 |

#### C. Configuración y selector

| Caso | Precondición | Operación | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| C-01 | `storage_provider=minio` | `crear_almacenamiento` | instancia de `MinIOStorage` | unitaria |
| C-02 | `storage_provider=s3` | `crear_almacenamiento` | instancia de `S3Storage` | unitaria |
| C-03 | `storage_provider=azure` | construir `Settings` | `ConfigurationError` | unitaria |
| C-04 | falta `storage_bucket` | construir `Settings` | `ConfigurationError` que **nombra** el campo | unitaria |
| C-05 | configuración completa | `repr(settings)` y el texto de `ConfigurationError` | **no** aparece la clave secreta | unitaria |
| C-06 | `app_env=production` + `storage_provider=minio` | construir `Settings` | rechazado: MinIO es local | unitaria |
| C-07 | dos llamadas con la misma configuración | `obtener_almacenamiento` | devuelve la **misma** instancia: no se reconstruye el cliente por petición | unitaria |

#### D. Claves de objeto

| Caso | Precondición | Operación | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| K-01 | — | generar muchas claves | todas distintas; el componente aleatorio tiene ≥ 122 bits | unitaria |
| K-02 | mismo `foto.png` dos veces | generar clave | claves **distintas** | unitaria |
| K-03 | `../../etc/passwd`, `C:\x\y.png`, `a/b.png` | generar clave | la clave **no** contiene el nombre; nunca aparece `..` ni `\` | unitaria |
| K-04 | formato validado `image/png` | generar clave | termina en `.png`, derivado del **formato**, no de la extensión declarada | unitaria |
| K-05 | — | longitud de la clave | ≤ 512, el límite de la columna | unitaria |
| K-06 | clave de un original | derivar la de su miniatura | comparten prefijo y se distinguen por el nombre del objeto | unitaria |

#### E. Validación de imagen

| Caso | Precondición | Operación | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| I-01 | PNG válido | validar | acepta; `mime_type=image/png`, `width`/`height` reales | unitaria |
| I-02 | `b"esto no es una imagen"` | validar | `ImagenInvalidaError` | unitaria |
| I-03 | PNG válido con nombre `foto.jpg` | validar | el MIME resultante es `image/png`: manda el **contenido** | unitaria |
| I-04 | PNG truncado | validar | `ImagenInvalidaError` | unitaria |
| I-05a | GIF válido | validar | `TipoDeImagenNoPermitidoError` | unitaria |
| I-05b | SVG con `<script>` | validar | `ImagenInvalidaError` — **refinado al escribir la prueba**: un SVG no es un formato rasterizado y ni siquiera se identifica como imagen. Lo que fija el caso es que **no se almacena** | unitaria |
| I-06 | bytes = límite + 1 | validar | `ImagenDemasiadoGrandeError` | unitaria |
| I-07 | bytes = límite exacto | validar | acepta | unitaria |
| I-08 | contenido vacío | validar | `ImagenInvalidaError` | unitaria |
| I-09 | imagen con más píxeles que el límite | validar | `ImagenDemasiadoGrandeError` (guarda anti *decompression bomb*) | unitaria |
| I-10 | JPEG, PNG y WebP válidos | validar | los tres se aceptan | unitaria |
| I-11 | PNG válido | validar | `checksum` = SHA-256 **de los bytes**, no del nombre | unitaria |

#### F. Miniaturas

| Caso | Precondición | Operación | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| T-01 | imagen 1200×800 | miniatura | WebP válido y decodificable | unitaria |
| T-02 | imagen 1200×800 | miniatura | cabe en 480×480 y conserva la proporción | unitaria |
| T-03 | imagen 100×80 | miniatura | **no** se amplía: sigue siendo 100×80 | unitaria |
| T-04 | JPEG con EXIF *orientation* = 6 | miniatura | las dimensiones salen **rotadas** según la orientación | unitaria |
| T-05 | JPEG con EXIF | miniatura | el derivado **no** conserva el bloque EXIF | unitaria |
| T-06 | PNG con transparencia | miniatura | conserva el canal alfa | unitaria |

#### G. Persistencia y compensación

| Caso | Precondición | Operación | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| P-01 | PNG válido | `SubirImagen` | existen el original y la miniatura en el almacén, y **una** fila `MediaAsset` | integración (PostgreSQL + MinIO) |
| P-02 | tras P-01 | inspección de la fila | guarda `object_key`, `mime_type`, `size_bytes`, `width`, `height`, `checksum`; **ningún** binario ni URL | integración |
| P-03 | la persistencia falla | `SubirImagen` | se propaga el error y **no queda ningún objeto** en el almacén | aplicación |
| P-04 | el almacenamiento falla al guardar el original | `SubirImagen` | se propaga; **no** hay fila en la base | aplicación |
| P-05 | la miniatura falla al guardarse | `SubirImagen` | se propaga; el original **se elimina** | aplicación |
| P-06 | la compensación **también** falla | `SubirImagen` | se propaga el error **original**; el fallo de compensación se registra sin ocultarse | aplicación |
| P-07 | imagen inválida | `SubirImagen` | falla **antes** de tocar el almacén: cero llamadas al almacenamiento | aplicación |
| P-08 | dos subidas del **mismo** archivo | `SubirImagen` | dos filas distintas con claves distintas: **no** hay deduplicación implícita | integración |

#### H. Borrado y medio en uso

| Caso | Precondición | Operación | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| D-01 | medio usado como portada de un artículo | `EliminarMedio` | `MedioEnUsoError` que nombra el tipo y el `slug`; la fila y los objetos **siguen** | integración |
| D-02 | medio usado como foto de perfil | `EliminarMedio` | `MedioEnUsoError` | integración |
| D-03 | medio usado como miniatura de vídeo | `EliminarMedio` | `MedioEnUsoError` | integración |
| D-04 | medio usado en review y en proyecto | `EliminarMedio` | el error enumera **los dos** usos | integración |
| D-05 | medio sin referencias | `EliminarMedio` | desaparecen la fila, el original y la miniatura | integración |
| D-06 | medio inexistente | `EliminarMedio` | `ResourceNotFoundError` | integración |
| D-07 | — | inspección de `app/shared/storage/` | **ningún** módulo de almacenamiento importa modelos ni SQLAlchemy | unitaria |

#### I. Acceso público al medio (**D-009-O**)

| Caso | Precondición | Operación | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| A-01 | artículo publicado con portada | `GET /api/v1/posts/{slug}` | `cover.access_url` presente y utilizable | integración |
| A-02 | cualquier respuesta pública | inspección del JSON completo, **tras retirar los enlaces firmados** | `object_key` **no es campo del contrato** y no aparece fuera del enlace firmado — **refinado**: ver **D-010-Q** y el reporte §S | integración |
| A-03 | tras A-01 | inspección de `media_assets` | ninguna columna guarda la URL emitida | integración |
| A-04 | contenido sin portada | listados y detalles | `cover` sigue siendo `null` | integración |
| A-05 | los 5 DTO que anidan un medio | respuesta | los cinco llevan el mismo campo de acceso | integración |
| A-06 | suite completa de `Task/009` | ejecución | verde: paginación, filtros, orden, búsqueda y 404 de borradores intactos | integración |
| A-07 | OpenAPI | inspección | `MedioPublico` gana **un** campo; no aparecen `object_key`, bucket ni región | contrato |

### 7.3 Tests RED esperados

| Test | Capa | Motivo de fallo esperado |
| --- | --- | --- |
| `test_guardar_y_obtener_devuelve_los_mismos_bytes` | contrato | no existe `app.shared.storage` |
| `test_minio_storage_rechaza_un_endpoint_de_aws` | unitaria | no existe `MinIOStorage` |
| `test_la_fabrica_devuelve_minio_para_el_proveedor_local` | unitaria | no existe la fábrica ni el campo de configuración |
| `test_dos_cargas_del_mismo_nombre_producen_claves_distintas` | unitaria | no existe el generador de claves |
| `test_un_archivo_que_no_es_imagen_se_rechaza` | unitaria | no existe el validador |
| `test_la_miniatura_no_amplia_una_imagen_pequena` | unitaria | no existe el generador de miniaturas |
| `test_si_la_persistencia_falla_no_queda_ningun_objeto` | aplicación | no existe `SubirImagen` |
| `test_no_se_elimina_un_medio_en_uso` | integración | no existe `EliminarMedio` |
| `test_la_portada_publica_trae_enlace_de_acceso` | integración | `MedioPublico` no tiene campo de acceso |

### 7.4 Integración necesaria

| Dependencia | Por qué el comportamiento la exige |
| --- | --- |
| **MinIO real** (entorno local, `Task/007`) | La semántica de `guardar`/`obtener`/`eliminar`/prefirmar es del **protocolo S3**, no del código: un doble la afirmaría en lugar de demostrarla. Es además el único modo de ejecutar `S3Storage` sin AWS. |
| **PostgreSQL real** (`personal_blog_test`) | La comprobación de uso depende de claves foráneas reales con `ON DELETE RESTRICT`, y la unicidad de `object_key` es un índice. SQLite **no** se usa. |

### 7.5 Casos negativos y de seguridad

Entrada inválida (I-02, I-04, I-05, I-06, I-08, I-09), nombre de archivo hostil (K-03),
clave no predecible (K-01, K-02), no filtración de `object_key` (A-02), no filtración de
credenciales (OS-11, C-05, S-03), destino de pruebas *fail-closed* (§7.6), adaptador local
que no puede alcanzar AWS (M-02) y ausencia de creación automática de buckets en producción
(S-04).

### 7.6 Guarda *fail-closed* del almacenamiento de pruebas

Misma filosofía que la guarda de PostgreSQL de `Task/005.6`/`005.7`: **no se comprueba que
el destino sea peligroso, se exige demostrar que es seguro.**

| Barrera | Regla |
| --- | --- |
| 1 | El endpoint debe estar declarado y ser **local**. Cualquier host de AWS → `FAIL`. |
| 2 | El bucket lo **crea la propia suite**, con un nombre único y prefijo inequívoco de prueba. |
| 3 | La limpieza **solo** borra el bucket que la suite creó, y solo si su nombre lleva ese prefijo. |
| 4 | Sin la variable de entorno del endpoint → `SKIP` con motivo. Con ella → cualquier fallo es `FAIL`, nunca `skip`. |
| 5 | El bucket de desarrollo configurado en `.env` **nunca** es destino de la suite. |

### 7.7 Regresiones relevantes

- Los **diez** endpoints públicos de `Task/009` y sus pruebas.
- `tests/integration/test_politica_de_medios.py` (`Task/008`).
- Hermeticidad del harness (`Task/005.7`) y grafo de fixtures de integración.
- Independencia del dominio (ADR-004): `app/modules/media/domain/` no puede arrastrar
  FastAPI, SQLAlchemy ni el SDK.

---

## 8. Plan de validación

Cada criterio de §6 se comprueba con la prueba que lo nombra en la matriz de §7.2, más los
*quality gates* de §9 y el *smoke* manual de §17.

## 9. Comandos de validación

```bash
ruff check .
ruff format --check .
mypy .
pytest tests/unit -q
pytest tests/contract -q
pytest -m integration -q
pytest -q -W error
pytest --cov -q
pip check
git diff --check
```

## 10. Evidencia esperada

RED y GREEN por *slice*, salida real de cada *gate*, cobertura, y el *smoke* de MinIO con
recuento de objetos residuales.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | Una prueba destructiva de almacenamiento apunta a un bucket real | Alto | Guarda *fail-closed* de §7.6, con su propia prueba estructural |
| 2 | `MinIOStorage` acaba siendo un alias vacío de `S3Storage` | Medio | Cada una tiene invariantes propias y probadas (M-02, M-03, S-02, S-04) |
| 3 | Generar una URL por elemento introduce una llamada de red por medio | Medio | La firma es **local**: se prueba que prefirmar no hace E/S |
| 4 | La URL prefirmada local apunta a un host que el navegador no alcanza | Bajo hoy | Ningún cliente consume medios todavía; se registra como deuda con propietario |
| 5 | Pillow decodifica una imagen maliciosa | Medio | Límite de píxeles explícito, formatos cerrados; `Task/018` endurece |

## 12. Decisiones técnicas

| # | Decisión | Alternativas | Justificación | ¿ADR? |
| --- | --- | --- | --- | --- |
| **D-010-A** | **Un solo SDK: `boto3`** para las dos implementaciones | SDK oficial de MinIO para `MinIOStorage` + `boto3` para `S3Storage`; cliente HTTP propio | El SDK de MinIO arrastra `pycryptodome` y `argon2-cffi` al **único** `requirements.txt`, y por tanto al artefacto de Lambda, para código que jamás se ejecuta en producción (P-07); además duplica la superficie a auditar (S-09). MinIO implementa el protocolo S3, así que `boto3` lo ejerce de verdad. **Lo que evita el alias vacío no es el SDK, sino las invariantes**: cada clase tiene las suyas y sus propias pruebas | No |
| **D-010-B** | `ObjectStorage` expone **cinco** operaciones | añadir `listar`, `copiar`, `metadatos` | Son las cinco que los casos de uso de esta tarea ejercen. `listar` lo pedirá la biblioteca de medios de `Task/012`, y añadirlo entonces es trivial; tenerlo muerto ahora no lo es | No |
| **D-010-C** | `eliminar` es **idempotente** | lanzar si no existe | Es la semántica de `DeleteObject` en S3 y la que necesita la compensación: al deshacer un fallo parcial no se sabe con certeza qué llegó a escribirse, y un borrado que lanza convertiría la limpieza en un segundo error | No |
| **D-010-D** | `guardar` **sobrescribe** la misma clave | rechazar duplicados | Es la semántica de `PutObject`. Las claves son no predecibles y de un solo uso, así que la colisión no ocurre en el flujo real; declararlo evita que las dos implementaciones difieran en silencio | No |
| **D-010-E** | Tipos MIME aceptados: **`image/jpeg`, `image/png`, `image/webp`** | añadir GIF; añadir SVG; aceptar cualquier `image/*` | Cubren todo lo que el MVP publica. **SVG queda fuera por seguridad**: es XML con capacidad de script. GIF queda fuera porque la animación complica la miniatura sin que ningún flujo la pida. `Task/018` es propietaria de endurecer, no de abrir | No |
| **D-010-F** | Tamaño máximo **5 MiB**; píxeles máximos **40 millones** | 2 MiB; 10 MiB; sin límite de píxeles | 5 MiB admite una fotografía de portada holgada y acota el cuerpo de la petición. El límite de píxeles es la guarda contra la *decompression bomb*: un PNG de pocos KB puede declarar 40000 × 40000 | No |
| **D-010-G** | Clave: `medios/<uuid4>/original.<ext>` | `<año>/<mes>/<uuid>`; nombre original *sanitizado*; hash del contenido | El UUID v4 aporta 122 bits aleatorios: conocer una clave no permite adivinar otra (software-architecture §3.7). El nombre original **no** participa, así que ningún nombre hostil puede influir en la clave. Un prefijo por fecha solo sirve a un *lifecycle* que aún no existe (`Task/030`) | No |
| **D-010-H** | Miniatura: **siempre**, WebP calidad 82, caja **480 × 480**, proporción conservada, **sin ampliar** | generar bajo demanda; JPEG; conservar el formato original | Ninguna fuente canónica fija dimensiones, así que las fija esta tarea (P-04). «Siempre» evita un estado en el que unos medios tienen miniatura y otros no. WebP comprime mejor y admite alfa. Ampliar produciría un archivo más pesado y más borroso que el original | No |
| **D-010-I** | La miniatura **no** es una fila `MediaAsset` ni una columna nueva | tabla `media_thumbnails`; columna `thumbnail_key`; segundo `MediaAsset` | Su clave se **deriva** de la del original, así que persistirla crearía el segundo estado que `data-model.md` D-O rechaza. **`Task/010` no modifica el esquema físico**: `0002` sigue siendo `head` | No |
| **D-010-J** | Se calcula `checksum` SHA-256; **no** hay deduplicación | no calcularlo; deduplicar automáticamente | El esquema ya reserva la columna y el índice para *detectar* duplicados. Detectar y **reutilizar** son decisiones distintas: reutilizar en silencio haría que borrar un medio afectara a contenidos que nunca lo subieron. Presentar el duplicado al administrador es de `Task/012` | No |
| **D-010-K** | La orientación EXIF se **normaliza**; el bloque EXIF **no** se copia al derivado | ignorar la orientación; conservar el EXIF | Ignorarla produce miniaturas giradas, que es un defecto visible. Copiar el EXIF arrastraría GPS y modelo de cámara a un archivo que se sirve públicamente | No |
| **D-010-L** | Campo público **`access_url`**, y **solo** ese | añadir `access_expires_at`; exponer `object_key`; URL construida a mano | Cierra **D-009-O** con el mínimo compatible (api-contracts §10.3). `access_expires_at` describiría la **semántica de caché**, que es literalmente una de las preguntas de **D-08**, propiedad de `Task/030` | No |
| **D-010-M** | El TTL del acceso es **configuración** (`BLOG_STORAGE_ACCESS_TTL_SECONDS`, 900 s por defecto) | constante en el adaptador; TTL fijo de producción | La política productiva de expiración es de `Task/030`. Enterrarla en el adaptador la haría inamovible sin tocar código | No |
| **D-010-N** | `alt_text` sigue admitiendo nulo al subir | exigirlo en la subida | `data-model.md` dice «se escribe al usar la imagen, no al subirla». El flujo B.4 no lo pide y B.5 asocia después. La accesibilidad se garantiza donde se **usa** el medio (`Task/012`, `Task/014`), no en el almacén | No |
| **D-010-O** | El caso de uso de borrado con comprobación de uso **es de `Task/010`** | dejarlo entero a `Task/012` | `data-model.md` invariante 12 se lo asigna por nombre: «`Task/010`: comprobación previa que dice **dónde** se usa (B.5)». `Task/012` expone el endpoint HTTP; aquí vive el comportamiento | No |
| **D-010-R** | **Dos endpoints separados**: uno **operativo**, que usa el backend, y otro **de acceso**, contra el que se firma el enlace temporal. El adaptador mantiene dos clientes | un solo endpoint; reescribir el anfitrion de la URL despues de firmarla; servir los medios a traves de Traefik o de un endpoint propio del backend | El consumidor del enlace es el **navegador del host**, que no resuelve el nombre de servicio de Docker con el que opera el backend. Y no se arregla despues: el `Host` entra en la peticion canonica de **SigV4**, asi que reescribirlo invalida la firma —comprobado contra MinIO real: `200` con la URL original, `403 SignatureDoesNotMatch` con el anfitrion cambiado—. Firmar exige un cliente configurado con el anfitrion externo, y construirlo no cuesta ninguna peticion de red porque prefirmar es aritmetica local. Un proxy de medios inventaria superficie que ninguna fuente pide y contradiria el limite C-01 -> C-08. **Opcional**: omitido, se firma contra el operativo, asi que produccion no queda obligada a configurar nada nuevo | No |
| **D-010-Q** | **Precisión de la invariante 9 de CONTENT_MODEL.md**: la garantía es que **ningún campo del contrato transporta `object_key`** y que fuera del enlace firmado no aparece — no que la cadena no exista en el cuerpo | exponer la clave como campo; servir los medios por un endpoint propio del backend; renunciar al campo de acceso | Una URL prefirmada **es** `<endpoint>/<bucket>/<object_key>?X-Amz-...`: la clave es la ruta del recurso que se firma y **no hay variante del mecanismo que la omita**. El mecanismo tampoco es opcional: CONTENT_MODEL §3.7 y security-boundaries lo imponen. La invariante prohíbe exponerla *«sin control»*, y una URL firmada, caducable y sobre bucket privado **es** la exposición controlada; además las claves no son predecibles, así que ver una no permite adivinar otra. Un endpoint propio inventaría superficie que ninguna fuente pide y contradiría el límite C-01→C-08 | No |
| **D-010-P** | Orden: validar → guardar original → guardar miniatura → persistir; compensación en orden inverso | persistir primero; transacción distribuida | No existe transacción entre PostgreSQL y S3. Validar primero evita tocar el almacén con basura. Persistir al final deja la fila —el índice de lo que existe— como último paso, así que un fallo previo no deja **nunca** una fila que apunte a un objeto ausente | No |

Ninguna decisión modifica una decisión arquitectónica aceptada, así que **no se crea ningún
ADR**. Todas viven aquí y en el reporte, y las que afectan a un contrato público se anotan
en `api-contracts.md` y `data-model.md`.

## 13. Documentación creada o actualizada

- `docs/tasks/TASK-010-s3-compatible-storage.md` — esta ficha.
- `docs/task-reports/TASK-010-report.md` — reporte.
- `docs/project-management/STATUS.md` — estado de la tarea.
- `docs/project-management/ROADMAP.md` — estado de la tarea.
- `docs/stages/STAGE-03-domain-and-backend.md` — alcance entregado.
- `docs/architecture/api-contracts.md` — cierre del campo de acceso (§11).
- `docs/architecture/data-model.md` — cierre del punto 10 de §10 y de la invariante 12.
- `docs/architecture/software-architecture.md` — §3.7 con lo realmente implementado.
- `docs/architecture/open-decisions.md` — qué parte de **D-08** queda y qué se cerró aquí.
- `docs/architecture/security-boundaries.md` — tipos MIME y tamaños definidos.
- `personal-blog-backend/README.md` y `.env.example` — variables nuevas.

## 14. Archivos modificados

Se completa en el reporte, §AA.

## 15. Resultado de pruebas

Se registra en el reporte, §Y, con la salida real.

## 16. Problemas encontrados

Se registran en el reporte.

## 17. Pasos de validación para el usuario

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra
docker compose ps                    # minio debe estar healthy

cd ..\personal-blog-backend
$env:PERSONAL_BLOG_TEST_DATABASE_URL="postgresql://<usuario>:<clave>@127.0.0.1:55432/personal_blog_test"
$env:PERSONAL_BLOG_TEST_STORAGE_ENDPOINT_URL="http://127.0.0.1:9000"
$env:PERSONAL_BLOG_TEST_STORAGE_ACCESS_KEY="<MINIO_ROOT_USER del .env de infra>"
$env:PERSONAL_BLOG_TEST_STORAGE_SECRET_KEY="<MINIO_ROOT_PASSWORD del .env de infra>"

.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q -W error
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy .
```

## 18. Deuda técnica pendiente

Se enumera en el reporte, §R y §S, con propietario explícito.

## 19. Próxima tarea

`Task/011-Autenticacion-Administrativa` — **Pendiente, no iniciada**.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-08-28** |
| **Aprobado por** | **jeffersondavila** (usuario) |
| **Expresión de aprobación** | `approved: Task/010-Almacenamiento-Compatible-S3` |

Las decisiones **D-010-A** a **D-010-R** de §12 quedan **Vigentes** desde el
2026-08-28. Ninguna crea ni modifica un ADR: no alteran ninguna decisión
arquitectónica aceptada, y así se razonó al tomarlas.
