# TASK-017 — Observabilidad Local — Reporte

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/017-Observabilidad-Local` |
| **Etapa** | ETAPA 05 — Calidad y Seguridad |
| **Estado** | **Aprobada** el 2026-09-06 por jeffersondavila |
| **Fecha del reporte** | 2026-09-06 |
| **Repositorios** | `personal-blog-backend` (funcional) · `personal-blog-infra` (gobierno, Traefik, runbook) |
| **Frontend** | **No participa.** Permanece en `main`, limpio y sin rama `Task/017` |
| **Rama base** | `main` en ambos repositorios |
| **Pruebas de backend** | **1808** en verde · **1** omitida · `-W error` · PostgreSQL y MinIO **reales** |
| **Dependencias nuevas** | **0** |
| **Aprobación** | `approved: Task/017-Observabilidad-Local` — **2026-09-06** |

> **Aprobada el 2026-09-06.** Este reporte registra lo verificado durante la implementación.
> Las secciones §20 y §21 conservan el bloqueo tal como se reportó **antes** de la aprobación:
> es evidencia histórica fechada y no se reescribe. Su resolución consta en §22.

---

## 1. Objetivo y resultado

Que cualquier petición al backend pueda **localizarse y explicarse de extremo a extremo** en
el entorno local con un único identificador, y que el operador distinga un proceso **vivo**
(`/health`) de un servicio **capaz de atender** (`/ready`), sin que ninguno de esos caminos
filtre un secreto.

**Conseguido**, con una excepción declarada en su momento: la comprobación **visual** de los
logs en la interfaz de Portainer no pudo ejecutarla la sesión de implementación. Detalle en
§20 y resolución en §22.

---

## 2. Requisitos: qué se cubre y qué no

| # | Resultado | Alcance |
| --- | --- | --- |
| **O-01** | **Cubierto en local** | Logs JSON por `stdout`, una línea por evento. El formato `text` conserva redacción y correlation ID |
| **O-02** | **Cubierto en local** | `X-Request-ID` fijada como contrato; presente en respuesta, en **todas** las líneas de log de la petición, en `error.request_id` y en `audit_events.request_id` |
| **O-03** | **Verificado** | `/health` responde a la vivacidad **sin** consultar dependencias. No se reimplementa |
| **O-04** | **Cubierto en local** | `GET /ready` con sonda real de PostgreSQL y de almacenamiento bajo presupuesto acotado |
| **O-05** | **Participación, no cierre** | El requisito lo cumplen `Task/011` y `Task/012`. `Task/017` aporta el `request_id` **compartido** entre respuesta, logs y `AuditEvent` |
| **O-07** | **Docker verificado por el agente**; la interfaz de Portainer la cubre la aprobación del usuario | §20 y §22 |
| **O-08** | **Cubierto en local** | Redacción automática por nombre de campo y por forma del valor, incluida la cadena de excepciones. Cierra el plano local de **R-36** |

**Fuera de alcance, y no se afirma lo contrario:** **O-06** (CloudWatch, `Task/031` y
`Task/041`), **O-09** (telemetría **exportada** a terceros: `Task/029`, `Task/018`,
`Task/040`) y **O-10** (observabilidad del VPS: `Task/029`, `Task/040`). `Task/017` **no
resuelve la observabilidad en la nube** y no crea ningún recurso cloud.

---

## 3. Los siete fallos heredados del handoff

La sesión anterior dejó la implementación terminada y la suite completa ejecutada con
dependencias reales: **1801 passed, 7 failed, 1 skipped**. Los siete se corrigieron sin
tocar el código productivo.

### 3.1 Cinco fallos de inventario OpenAPI — caso legítimo de **B-12**

`Task/017` **implementa `GET /ready`**. Cinco pruebas heredadas afirmaban lo contrario,
porque se escribieron cuando esa ruta pertenecía a una tarea futura. Es el **primer
supuesto** de `BACKEND_TESTING_STRATEGY.md` §9 —*el requisito cambió*—, no una prueba
acomodada al código.

| # | Prueba | Causa | Corrección |
| --- | --- | --- | --- |
| 1 | `test_contrato_administrativo.py::test_la_especificacion_declara_exactamente_las_rutas_del_contrato` | `RUTAS_PUBLICAS` no incluía `/ready` | `/ready` añadida al conjunto **cerrado** |
| 2 | `test_contrato_administrativo.py::test_el_contrato_publico_de_task_009_no_cambia` | Mismo conjunto | Misma corrección; el docstring precisa que `Task/017` **añade** superficie de plataforma sin tocar las diez rutas de contrato |
| 3 | `test_contrato_de_autenticacion.py::test_el_contrato_publico_no_cambia` | Literal de rutas sin `/ready` | `/ready` añadida; se documenta que es **anónima** a propósito: Traefik la consulta sin credenciales |
| 4 | `test_openapi_publica.py::test_la_especificacion_declara_exactamente_las_rutas_del_contrato` | `RUTAS_ESPERADAS` sin `/ready` | `/ready` añadida con el comentario de por qué vive fuera del prefijo versionado |
| 7 | `test_openapi.py::test_openapi_no_declara_endpoints_no_implementados` | Contenía `assert "/ready" not in rutas` y un comentario diciendo que la sonda *«es de `Task/017`»* | La expectativa se sustituye por una **más fuerte**: `/ready` **debe** estar declarada **y** no admitir escritura |

**Lo que no se hizo, y es lo que importa:**

- **No** se relajó ningún `assert conjunto == esperado` a un `esperado <= conjunto`.
- **No** se filtró `/ready` ni ningún otro endpoint técnico del recorrido.
- **No** se derivó ninguna lista de la aplicación: los conjuntos siguen escritos a mano, así
  que una ruta nueva sigue teniendo que anotarse para pasar.
- Los docstrings heredados que afirmaban *«`/ready` es de `Task/017` y no debe existir
  todavía»* se corrigieron **explicando el cambio**, con el mismo formato que usaron
  `Task/011`, `Task/012`, `Task/012.1` y `Task/016`. La intención histórica se conserva.

**Conteo derivado del OpenAPI real**, no supuesto: **40 patrones de ruta** (13 públicas
—diez de contrato, dos sondas y el sitemap—, 3 de autenticación y 24 administrativas) y
**52 operaciones**. El docstring que decía *«11 públicas»* y *«26 a 27 patrones»* quedaba de
antes de `Task/016`; se corrigió con el valor medido.

### 3.2 Dos fallos de la guarda del grafo de fixtures — **CERT-AUD-002 intacta**

| # | Prueba | Causa |
| --- | --- | --- |
| 5 | `test_grafo_de_fixtures_de_integracion.py::…[bucket_exclusivo_de_sonda]` | No alcanzaba `destino_de_integracion_verificado` |
| 6 | `test_grafo_de_fixtures_de_integracion.py::…[cliente_de_inspeccion]` | Ídem |

**La guarda no se tocó.** No se añadió ninguna excepción, ninguna lista de exentos y ningún
filtro. Se corrigió **lo señalado**, que era el grafo.

De los dos remedios que el propio mensaje de fallo admite se eligió **(a) derivarla del
resolutor**, y no (b) sacar el módulo del harness:

- Estas pruebas hablan con **MinIO real** contra un bucket descartable. `tests/integration/`
  es exactamente el lugar donde vive ese tipo de prueba; moverlas solo para esquivar la
  comprobación habría **debilitado** la garantía en lugar de satisfacerla.
- El patrón ya existe y es canónico en este harness: `alembic_config` depende de
  `database_engine` *«a propósito, aunque no lo use: es la cadena que pasa por la guarda
  fail-closed»*. Y dentro de esta misma tarea, `configuracion_real` de
  `test_readiness_dependencias.py` ya pedía el resolutor.

**Cambio mínimo:** una sola arista. `cliente_de_inspeccion` pide ahora
`destino_de_integracion_verificado`; `bucket_exclusivo_de_sonda` lo alcanza de forma
transitiva porque ya dependía de `cliente_de_inspeccion`. **No se ejecuta ninguna operación
adicional sobre PostgreSQL**: el resolutor tiene alcance de sesión y ya había conectado.

**Refuerzo adicional.** Los tres módulos y las cuatro fixtures que `Task/017` añade se
registraron en `MODULOS_CONOCIDOS` y `FIXTURES_CONOCIDAS`. Esas listas son las guardas
anti-tautología del descubrimiento —impiden que la comprobación se quede verde inspeccionando
un conjunto vacío—, así que ampliarlas **endurece** la prueba.

---

## 4. Gates estáticos

| Gate | Resultado |
| --- | --- |
| `ruff check .` | **All checks passed!** |
| `ruff format --check .` | **308 files already formatted** |
| `mypy` | **Success: no issues found in 306 source files** |

El tipado de `app/shared/storage/minio.py` no se rediseñó: seguía verde y los cambios de
esta sesión no lo tocaron.

> **Incidencia menor, resuelta.** La primera edición de los archivos de prueba los dejó con
> finales de línea CRLF, y el proyecto fija `line-ending = "lf"` en `pyproject.toml`.
> `ruff format --check` lo detectó y los seis archivos se normalizaron a LF. No hubo cambio
> de contenido.

---

## 5. Suite completa

```
1808 passed, 1 skipped in 358.68s (0:05:58)
```

| Aspecto | Valor |
| --- | --- |
| **Comando** | `pytest -W error -q` |
| **Dependencias** | PostgreSQL y MinIO **reales**, configurados explícitamente |
| **Pasadas** | **1808** |
| **Fallidas** | **0** |
| **Omitidas** | **1** — `tests/test_logging_utc.py:133: time.tzset no existe en Windows`. Estructural de la plataforma, único skip admitido |
| **Warnings** | **0** no controlados: la suite corre con `-W error`, así que un warning habría sido un fallo |
| **Baseline previo a `Task/017`** | 1631 passed, 1 skipped |
| **Delta** | **+177 pruebas** |

No hubo cientos de omitidas: la integración se ejecutó de verdad.

**Módulos nuevos:** `test_correlacion.py` (14), `test_middleware_correlacion.py` (30),
`test_logging_redaccion.py` (24), `test_readiness.py` (15),
`integration/test_readiness_almacenamiento.py` (12),
`integration/test_readiness_dependencias.py` (14),
`integration/test_auditoria_correlacion.py` (17).

---

## 6. Correlation ID

### 6.1 Contrato — cerrado

`api-contracts.md` §11 dejaba la cabecera **abierta para `Task/017`**. Queda fijada:

| Elemento | Valor |
| --- | --- |
| **Cabecera** | `X-Request-ID`, en petición y respuesta |
| **Longitud** | 8 a 64 caracteres |
| **Alfabeto** | `A-Za-z0-9-_` |
| **Generación** | UUIDv4 |

Se descartó `traceparent`: es la cabecera de W3C Trace Context y adoptarla anunciaría una
semántica de trazas distribuidas que el proyecto no implementa.

### 6.2 Política de entrada — *fail-safe*

| Cabeceras recibidas | Resultado |
| --- | --- |
| 0 | Se **genera** |
| 1 válida | Se **reutiliza** |
| 1 inválida | Se **descarta** y se genera |
| 2 o más | Se **descartan todas** y se genera |

El último caso no depende del comportamiento de ningún servidor intermedio: ante cabeceras
repetidas no hay forma de saber cuál es legítima, así que ninguna se cree. El valor del
cliente es entrada no confiable y **nunca** llega a un log ni a la base sin validarse.

### 6.3 Alcance verificado

- **2xx, 4xx y 5xx** llevan la cabecera. El caso en que hace falta es justamente el fallo.
- **Concurrencia:** el identificador vive en un `ContextVar`, así que peticiones simultáneas
  no se mezclan. Comprobado con peticiones concurrentes, no por inspección.
- **`error.request_id`** de la envoltura común lleva el mismo valor.

### 6.4 `uvicorn.error` — defecto encontrado y corregido

La validación HTTP real destapó un defecto que la inspección no había visto: **`uvicorn.error`
registra la excepción *después* de que el middleware haya restaurado el `ContextVar`**, de
modo que esa línea —justo la de un `500`— perdía el identificador.

Se escribió primero la prueba RED
(`test_uvicorn_error_conserva_el_id_despues_de_salir_del_middleware`) y luego el GREEN. La
solución conserva el identificador **en el boundary de la excepción**, no dejando vivo el
contexto. Se cumplen **las dos** condiciones a la vez:

- `request_id_actual()` es `None` después de salir de la petición — el `ContextVar` **sí** se
  restaura.
- `uvicorn.error` conserva el identificador **de esa** excepción.

---

## 7. Logging y privacidad

| Aspecto | Resultado |
| --- | --- |
| **JSON** | Una línea por evento, con `timestamp`, `level`, `logger`, `module`, `line` y `context` |
| **`text`** | Redacta **también**, y **también** lleva el correlation ID. Eran dos defectos reales del formato de desarrollo, corregidos |
| **Redacción por nombre** | `password`, `passwd`, `secret`, `token`, `authorization`, `cookie`, `session`, `credential`, `access_key`, `api_key`, `private`, `signature`, `database_url`, `dsn`, `email`, `body` |
| **Redacción por forma** | DSN con contraseña, parámetros de firma, esquema de autorización, correo |
| **Excepciones** | Se redacta la **cadena**: mensaje, causa, traza y pila. Es la vía que **R-36** describía —*«una excepción de driver puede filtrar una credencial»*— |
| **Idempotencia** | Redactar dos veces da el mismo resultado |
| **Cuerpos en `bytes`** | Cubiertos: un `body` binario ya no escapa por no ser `str` |
| **DSN ya saneada** | Conserva host y puerto en lugar de perderlos. Redactar no puede destruir el diagnóstico |
| **`/ready` en 503** | Se registra a **WARNING**, no a ERROR: una dependencia caída no es un fallo del código |
| **Campos operativos** | `request_id`, `method`, `path`, `status_code`, `duration_ms` y `error_code` **nunca** se tocan |

**Pruebas de señuelo:** se siembra un valor sensible reconocible y se exige que **no**
aparezca en la salida. Es lo que impide que la redacción se demuestre con un caso amable.
**29 pruebas** de redacción; **46** en el delta de logging y readiness.

`text` no está desatendido a propósito: es el formato de desarrollo, y un secreto filtrado
en la consola del desarrollador está igual de filtrado.

---

## 8. Readiness

### 8.1 Los cinco escenarios, medidos

| Escenario | Resultado | Tiempo |
| --- | --- | --- |
| Base de datos inalcanzable | `503` | **2.058 s** |
| Endpoint de almacenamiento inalcanzable | `503` | **1.558 s** |
| Bucket inexistente | `503` | **0.069 s** |
| Credenciales inválidas | `503` | **0.056 s** |
| **Ambas dependencias caídas** | `503` | **2.517 s** |

### 8.2 Presupuesto total, no suma de timeouts

El caso de las dos dependencias caídas es el que justifica el diseño. Una implementación con
un timeout por sonda tardaba **~6.05 s** —por encima del `timeout: 3s` de Traefik—, que es
como se convierte un almacenamiento caído en un proxy colgado.

`/ready` tiene ahora un **presupuesto HTTP total de 2.5 s** compartido por ambas sondas, con
0.5 s de margen para el transporte. La relación que se mantiene es:

```
presupuesto de /ready (2.5 s)  <  timeout de Traefik (3 s)
```

**El timeout de Traefik no se aumentó**: aumentarlo habría escondido el problema en vez de
resolverlo. Los drivers síncronos no se cancelan desde asyncio, así que las plazas del
ejecutor se retienen hasta que el driver termina, y una sonda que vence el plazo no deja
trabajo acumulándose.

### 8.3 Lo que `/ready` no dice

El cuerpo es `{"status": "not_ready"}` y **no nombra el componente**: `/ready` es anónimo, y
decirle a un cliente cualquiera qué parte de la infraestructura está caída es reconocimiento
gratuito (`api-contracts.md` §2). El **log** sí lo distingue, ya saneado.

---

## 9. Almacenamiento

### 9.1 Por qué una operación nueva del puerto

`ObjectStorage` pasa de cinco a **seis** operaciones. Ninguna de las cinco anteriores servía:
`guardar` y `eliminar` **mutan**; `obtener` descarga bytes; `acceso_temporal` firma **en
local**, sin viajar a la red, así que funcionaría con el almacenamiento caído; y `existe`
devuelve `404 Code='404'` **idéntico** para *«el bucket está y la clave no»* y *«el bucket no
está»* —medido contra MinIO real—, de modo que `/ready` habría respondido `200` con el bucket
ausente.

### 9.2 Forma de la sonda

`ListObjectsV2` con `Bucket`, `Prefix="_readiness/"` y `MaxKeys=1`. **No** se usa
`HeadObject`, ni `HeadBucket` como sustituto, ni `existe()`, ni un objeto centinela, ni
`PutObject`. El prefijo no es cosmético: permite que `Task/030` conceda `s3:ListBucket` con
una condición sobre `s3:prefix`, de modo que un compromiso de la Lambda no habilite listar
los medios del blog.

### 9.3 Una sola tentativa efectiva

`max_attempts=1` **no** garantiza una única tentativa según la semántica del SDK. La
implementación se corrigió para exigir una tentativa real, y hay una prueba que lo comprueba
contando las peticiones emitidas en `before-send.s3.ListObjectsV2`: `len(intentos) == 1`, con
el mensaje *«una sonda informa, no reintenta»*.

### 9.4 No mutación

Cinco escenarios × dos proveedores (`MinIOStorage` y `S3Storage`) comparan el inventario
**antes y después**: mismas claves, mismos `ETag`, mismos `LastModified`. Se comprueba además
que la sonda emite **exactamente una** `ListObjectsV2` con `Bucket`, `Prefix` y `MaxKeys`
correctos.

> **Precisión sobre `EncodingType`.** Botocore añade `EncodingType="url"` por su cuenta al
> evento interno de parámetros. La expectativa se acotó a las **tres** restricciones que la
> aplicación impone, en lugar de exigir una igualdad ingenua del diccionario: ese campo
> automático no significa que la aplicación haga otra operación. **No volver a exigir esa
> igualdad ingenua.** Último resultado dirigido: **26 passed**.

---

## 10. Auditoría

| Elemento | Verificado |
| --- | --- |
| Cabecera de respuesta | `X-Request-ID` presente |
| Logs | El mismo identificador en todas las líneas de la petición |
| `AuditEvent.request_id` | El mismo identificador, persistido |
| DTO de `GET /api/v1/admin/audit-events` | **Sin cambios**: `id`, `occurred_at`, `action`, `entity_type`, `entity_id` |

**`request_id` no se expone en el DTO.** Que se almacene no significa que se publique:
cruzarlo con los logs es trabajo de operador, y publicarlo lo convertiría en contrato `v1`,
del que ya no podría retirarse.

Evidencia de esta sesión, con el identificador `task017-claude-portainer-final`:

```
POST /api/v1/admin/auth/login -> 401, X-Request-ID devuelto
log  app.peticion: status_code=401, duration_ms=258.4, nivel WARNING
BD   audit_events: task017-claude-portainer-final | authentication.login_failed
```

El evento se generó contra un correo señuelo en `example.invalid` —dominio reservado por RFC
2606, no resoluble—, que es la operación auditada menos invasiva. **No se borra**:
`AuditEvent` es inmutable por diseño y esta tarea no relaja esa garantía ni para limpiar su
propio rastro.

---

## 11. Infraestructura

| Cambio | Estado |
| --- | --- |
| `docker/traefik/dynamic/routes.yml`: regla del router backend | Incluye ``Path(`/ready`)`` |
| `docker/traefik/dynamic/routes.yml`: `healthCheck` del servicio backend | `path: /ready`, `interval: 10s`, `timeout: 3s` |
| `Dockerfile` del backend: `HEALTHCHECK` | **Sigue en `/health`**, sin cambio |
| `docker compose config` | Válido |

**Por qué Docker conserva `/health` y Traefik pasa a `/ready`:** son dos preguntas con dos
consecuencias. La de Traefik es **retirar de rotación** un backend que no puede servir, y esa
es la pregunta de readiness. La de Docker es sobre el contenedor: durante un incidente de
dependencias interesa que siga **sano y en marcha**, porque es lo que mantiene sus logs
consultables desde Portainer.

> Al aplicar el cambio, la primera comprobación devolvió el HTML del frontend porque Traefik
> aún no había recargado el archivo dinámico. Se recreó **solo** Traefik y el enrutado quedó
> aplicado. No se repitieron recreaciones innecesarias.

---

## 12. Stack real

Peticiones a través de Traefik (`http://localhost:8081`), en esta sesión:

| Petición | Código | `Content-Type` | `X-Request-ID` |
| --- | --- | --- | --- |
| `GET /health` | **200** | `application/json` | ✔ |
| `GET /ready` | **200** | `application/json` | ✔ |
| `GET /api/v1/posts` | **200** | `application/json` | ✔ |
| `GET /api/v1/no-existe-task017` | **404** | `application/json` | ✔ |
| `POST /api/v1/admin/auth/login` (fallido) | **401** | `application/json` | ✔ |

**`/ready` ya no cae en el frontend.** Los logs de Traefik confirman `RouterName:
backend@file` para esa ruta. Los cuatro `GET` reutilizaron el identificador enviado por el
cliente, que es la política de §6.2 para una cabecera válida.

### 12.1 Validación del `500` real

Se comprobó con una ruta temporal **fuera del código productivo**, montada solo para
provocar una excepción no controlada:

```
HTTP 500 · request_id = task017-runtime-exception
```

El mismo identificador apareció en `app.task017.validacion`, `app.peticion`,
`app.shared.errors.handlers` y **`uvicorn.error`**. Los señuelos no aparecieron en ninguna
línea, y el manejador y `uvicorn.error` conservaron el **tipo** de la excepción y el de su
causa: redactar no destruye el diagnóstico.

**La ruta temporal no forma parte del producto.** El backend quedó en
`uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1`, sin montajes. Verificado en
esta sesión: `Cmd` correcto y **0 mounts**.

---

## 13. Anti-tautología

Diez mutaciones, cada una con su prueba RED, restauración y GREEN:

| Mutación | Prueba | RED | GREEN |
| --- | --- | --- | --- |
| **A** | `test_middleware_correlacion.py::test_cada_peticion_emite_un_evento_con_los_campos_estructurados` | ✔ | ✔ |
| **B** | `test_auditoria_correlacion.py::test_una_escritura_administrativa_correcta_guarda_el_id_que_devuelve` | ✔ | ✔ |
| **C** | `test_readiness_dependencias.py::test_ready_responde_503_con_el_bucket_inexistente` | ✔ | ✔ |
| **C2** | ídem, mutando `s3_compatible.py` | ✔ | ✔ |
| **C3** | `…::test_ready_responde_503_con_credenciales_de_almacenamiento_invalidas` | ✔ | ✔ |
| **D** | `test_logging_redaccion.py::test_una_clave_de_contexto_sensible_se_redacta_por_su_nombre` | ✔ | ✔ |
| **E** | `test_correlacion.py::test_se_rechaza_un_valor_fuera_del_contrato` | ✔ (12 failed) | ✔ (12 passed) |
| **E2** | `test_correlacion.py::test_con_dos_cabeceras_validas_se_descartan_las_dos_no_una` | ✔ | ✔ |
| **F** | `test_middleware_correlacion.py::test_cada_peticion_emite_un_evento_con_los_campos_estructurados` | ✔ | ✔ |
| **G** | `test_middleware_correlacion.py::test_duration_ms_ignora_un_salto_del_reloj_civil` | ✔ | ✔ |

> **Nota sobre la mutación E.** El primer *runner* interpretó mal su resultado: había **12
> fallos semánticos** en lugar de un único resumen. **Se corrigió el runner, no la prueba.**
> Cambiar la prueba para que el runner la entendiera habría sido exactamente lo que este
> ejercicio existe para detectar.

**Restauración verificada en esta sesión, no supuesta.** Se recalculó el SHA-256 de los siete
archivos mutados y **los siete coinciden byte a byte** con el hash registrado tras la
restauración: `app/api/readiness.py`, `app/modules/audit/infrastructure/registro.py`,
`app/shared/logging/configuration.py`, `app/shared/logging/contexto.py`,
`app/shared/logging/middleware.py`, `app/shared/logging/redaccion.py` y
`app/shared/storage/s3_compatible.py`. Con la suite completa en verde, no hizo falta repetir
las mutaciones.

---

## 14. `docker build`

`docker compose build backend` — **correcto**. La imagen se construyó sin errores.

Los cambios posteriores de esta sesión son de **pruebas y documentación**, así que no exigen
reconstruir. No se ejecutó `docker compose down`, `down -v`, `system prune` ni
`volume prune`, y no se recrearon PostgreSQL ni MinIO.

---

## 15. Dependencias

**0 nuevas.** `requirements.txt`, `requirements-dev.txt` y `pyproject.toml` **idénticos a
`main`**; nada instalado. Todo se resolvió con la biblioteca estándar y lo ya presente:
`ContextVar`, `logging.Filter`, `boto3` y SQLAlchemy.

---

## 16. Documentación actualizada

### `personal-blog-infra`

| Documento | Cambio |
| --- | --- |
| `docs/architecture/api-contracts.md` | §2: `/health` y `/ready` **implementados**, con la forma de sus respuestas. **§9.1–§9.3 nuevas**: cabecera, formato, política *fail-safe* y alcance. §11, §13 y §14: la fila *«Cabecera concreta del correlation ID»* pasa de **Abierto** a **Cerrada**. §15.3: el motivo de no exponer `request_id` deja de ser *«`Task/017` aún no ha fijado la cabecera»* y pasa a ser una decisión propia |
| `docs/architecture/software-architecture.md` | `ObjectStorage` pasa de **cinco a seis** operaciones, con el porqué, la forma de la sonda y **lo que no demuestra** (permisos de escritura: `Task/030`) |
| `docs/architecture/non-functional-requirements.md` | **§5.1 nueva**: estado de O-01…O-08 tras `Task/017` y, con el mismo detalle, **lo que no cubre** (O-06, O-09, O-10 y el endurecimiento de `Task/018`) |
| `docs/architecture/security-boundaries.md` | La fila *«Logs — Filtración de secretos»* pasa de *«lista de campos a redactar»* a **mecanismo implementado**, con su lista y sus patrones. *«Campos a redactar en los logs»* deja de ser pregunta abierta |
| `docs/runbooks/local-environment.md` | **§6.9 nueva**: `/health` vs `/ready`, interpretar un `503`, seguir una petición con `X-Request-ID` por `docker compose logs` y por Portainer, y cruzarlo con `audit_events` |
| `docs/project-management/STATUS.md` | `Task/017` deja de figurar como *pendiente, no iniciada* y pasa a **tarea actual — Lista para validación**; bloque propio con lo que entrega y lo que no; **R-36** pasa a *mitigado en local, pendiente de aprobación*; próxima tarea prevista, `Task/018` |
| `docs/project-management/ROADMAP.md` | **Dos correcciones**: la referencia que ligaba *telemetría portable* a **O-09** —es el **principio 9** de `overview.md` §5 y **ADR-008**; O-09 conserva su significado y sus propietarios— y el *drift* del cálculo de avance, de `9 / 41 = 22 %` a **`16 / 41 = 39 %`** |
| `docs/stages/STAGE-05-quality-security.md` | `Task/017` pasa a **Lista para validación**. **Avance sin cambio: 1 de 3 — 33 %** |
| `docs/tasks/TASK-017-local-observability.md` | Estado a **Lista para validación**; nota de cierre con las dos precisiones que impuso la implementación; §26 con pruebas y dependencias |
| `docs/task-reports/TASK-017-report.md` | Este documento |

`ROADMAP.md`: **la corrección del *drift* no cuenta como trabajo funcional de `Task/017`**.
Era preexistente, no lo causó esta tarea, y se corrige aquí porque la tarea ya modificaba ese
documento. `Task/017` **no** suma al avance hasta que el usuario la apruebe.

### `personal-blog-backend`

Sin documentación propia que actualizar: el porqué de cada decisión vive en los docstrings de
los módulos, que se escribieron con el código.

---

## 17. Criterion 12

Búsqueda dirigida en todos los documentos modificados. **C = 0.**

No persiste como estado vigente ninguna afirmación sobre: la existencia de una rama, una rama
remota, un pull request abierto, la ausencia de commit o de *push*, la espera de un merge, el
estado del árbol de trabajo o una normalización pendiente.

Lo que sí permanece, porque es admisible: reglas permanentes, evidencia histórica **fechada**,
resultados de pruebas, mediciones y decisiones durables.

---

## 18. Estado de Git

| Repositorio | Rama | Commits sobre `main` | *Staging* | *Push* | PR |
| --- | --- | --- | --- | --- | --- |
| `personal-blog-backend` | `Task/017-Observabilidad-Local` | **0** | **0** | **No** | **No** |
| `personal-blog-infra` | `Task/017-Observabilidad-Local` | **0** | **0** | **No** | **No** |
| `personal-blog-frontend` | `main` | — | limpio | — | — |

Los cambios quedan **sin commit**, que es el comportamiento por defecto antes de la
aprobación. El frontend no tiene rama `Task/017` porque no participa.

---

## 19. Deuda real restante

| # | Deuda | Propietario |
| --- | --- | --- |
| **1** | Endurecimiento de la política de redacción: más patrones, cabeceras y superficies | `Task/018` |
| **2** | Privacidad de la telemetría **exportada** a terceros (**O-09**) | `Task/029`, `Task/018`, `Task/040` |
| **3** | Observabilidad de producción: CloudWatch (**O-06**) y *baseline* del VPS (**O-10**) | `Task/031`, `Task/041`, `Task/029`, `Task/040` |
| **4** | Permisos de `s3:ListBucket` acotados por `s3:prefix` para la sonda en producción | `Task/030` |
| **5** | `BLOG_ADMIN_ALLOWED_ORIGINS` no está definida en el Compose: un `POST` con `Origin` desde el navegador recibe `403`. Hallazgo de infraestructura local, **fuera del alcance** de esta tarea | `Task/018` (owner de CORS) |

La comprobación visual de Portainer **deja de ser deuda**: la cubrió la aprobación del
usuario (§22).

---

## 20. Bloqueo: comprobación visual en Portainer

**O-07 está verificado por Docker, y NO está verificado visualmente en Portainer.**

| Lo verificado | Cómo |
| --- | --- |
| Los logs del backend son JSON, una línea por evento | `docker logs personal-blog-local-backend` |
| El correlation ID es localizable en ese flujo | Búsqueda de `task017-claude-portainer-final` en los logs del contenedor |
| La cadena `respuesta → log → AuditEvent` comparte identificador | Cabecera HTTP, logs y consulta a PostgreSQL |
| Portainer está en marcha y es alcanzable | `https://localhost:9444` responde `200`; su API declara la versión **2.39.5** |

**Lo que falta:** localizar esa misma línea **en la interfaz de Portainer** y comprobar
visualmente `request_id`, `method`, `path`, `status_code` y `duration_ms`.

**Motivo:** esta sesión **no dispone de superficie de navegador ni de control del escritorio**.
No hay forma de abrir la interfaz, y las credenciales de Portainer no se piden ni se
modifican. Sustituir esa comprobación por una prueba automática **no sería lo mismo**: el
criterio dice *interfaz de Portainer*, y Docker ya está cubierto por otra vía.

**Cómo cerrarlo — la evidencia ya está sembrada:**

1. Abrir `https://localhost:9444` con la sesión existente.
2. *Containers* → **`personal-blog-local-backend`** → **Logs**.
3. Buscar **`task017-claude-portainer-final`**.
4. Debe aparecer, entre otras, esta línea:

```json
{"timestamp": "2026-09-07T00:01:57.459Z", "level": "WARNING", "logger": "app.peticion",
 "message": "Peticion completada", "module": "middleware", "line": 181,
 "context": {"request_id": "task017-claude-portainer-final", "method": "POST",
             "path": "/api/v1/admin/auth/login", "status_code": 401, "duration_ms": 258.4}}
```

Con esa confirmación, **O-07 queda cubierto** y la tarea pasa a **Lista para validación** sin
ningún otro cambio: todos los demás criterios están cumplidos.

---

## 21. Veredicto

> ### TASK017 NO LISTA — REQUIERE CORRECCIÓN
>
> Único punto pendiente: la **comprobación visual en Portainer** (§20), que exige una
> superficie de navegador de la que esta sesión no dispone. Todos los demás criterios están
> cumplidos y verificados: gates estáticos en verde, **1808** pruebas en verde con
> dependencias reales, correlation ID de extremo a extremo, `/ready` medido en sus cinco
> escenarios bajo presupuesto, no mutación del almacenamiento demostrada, redacción probada
> con señuelos, infraestructura aplicada y **0 dependencias nuevas**.

**La aprobación es exclusiva del usuario.** Este reporte no aprueba: registra. La aprobación
llegó después, y consta en §22.

---

## 22. Cierre — aprobación del 2026-09-06

| Campo | Valor |
| --- | --- |
| **Expresión recibida** | `approved: Task/017-Observabilidad-Local` |
| **Fecha** | 2026-09-06 |
| **Aprobado por** | jeffersondavila |
| **Avance global** | **16 / 41 → 17 / 41 — 41 %** |
| **ETAPA 05** | **1 / 3 → 2 / 3 — 67 %** |

### Cómo se resolvió el bloqueo de §20

El veredicto de §21 fue **NO LISTA** por un único punto: la comprobación **visual** en la
interfaz de Portainer. La sesión de implementación **no la produjo** —no disponía de
superficie de navegador— y así se reportó, sin sustituirla por una prueba automática ni
darla por hecha.

**La cubre la aprobación del usuario**, que es quien tiene acceso a esa interfaz y a quien
corresponde en exclusiva aprobar una tarea (`PROJECT_INSTRUCTIONS.md` §9). Queda constancia
de la distinción, porque importa para cualquier auditoría futura:

| Evidencia | Origen |
| --- | --- |
| O-07 por **Docker**: logs JSON, correlation ID localizable en el flujo del contenedor | **Verificada por el agente**, reproducible con `docker logs` |
| O-07 por la **interfaz de Portainer** | **No generada por el agente.** Cubierta por la aprobación del usuario |

Las demás verificaciones de este reporte —gates estáticos, 1808 pruebas, mediciones de
readiness, no mutación, señuelos de redacción, cadena de auditoría, stack real— **sí** las
produjo el agente y son reproducibles.

### Decisiones promovidas

Las ocho decisiones de la ficha pasan de **`Propuesta — pendiente de aprobación`** a
**Aceptadas y Vigentes**. Se enumeran en la ficha §26.

### Riesgo R-36

Su plano **local** queda **cerrado**: el mecanismo de redacción existe, está probado con
señuelos y la causa que abrió el riesgo —*«depende de que quien registra el evento no pase un
valor sensible»*— ya no se sostiene. **Sigue abierto** para el endurecimiento de la política
(`Task/018`) y, en otro plano, para la telemetría **exportada**, que es **O-09** y no este
riesgo (`Task/029`, `Task/018`, `Task/040`).
