# TASK-017 — Observabilidad Local

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/017-Observabilidad-Local` |
| **Nombre** | Observabilidad Local |
| **Etapa** | ETAPA 05 — Calidad y Seguridad |
| **Estado** | **Aprobada** el 2026-09-06 por jeffersondavila |
| **Repositorios involucrados** | `personal-blog-backend` (funcional) · `personal-blog-infra` (gobierno, Compose, Traefik, runbook) |
| **Dependencias** | `Task/014` ✔ **Aprobada** (2026-09-05) · `Task/015` ✔ **Aprobada** (2026-09-05) · `Task/016` ✔ **Aprobada** (2026-09-06) |
| **Rama** | `Task/017-Observabilidad-Local` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base backend** | `fa29c3d2e6f6724d352616bb37cfcf9a347970df` |
| **SHA base infra** | `68d2a710683a4fc237b7d4554dbfc60c7df479f9` |
| **Fecha de inicio** | 2026-09-06 |
| **Última actualización** | 2026-09-06 — **Aprobada**; ver [reporte](../task-reports/TASK-017-report.md) |

> **Esta ficha define; no implementa.** Todo lo que sigue es **Propuesta — pendiente de
> aprobación** salvo lo marcado como *medido*, que es estado observado del sistema el
> 2026-09-06 y no una decisión.
>
> **Nota de cierre — 2026-09-06.** La **implementación está terminada** y sus resultados
> están en el [reporte](../task-reports/TASK-017-report.md). Esta ficha conserva el texto de
> definición: es lo que se decidió **antes** de programar, y reescribirla en pasado borraría
> la distinción entre lo previsto y lo obtenido. Dos precisiones que la implementación
> impuso y que el reporte detalla: la sonda de almacenamiento no basta con configurar un
> `timeout` —hubo que exigir **una sola tentativa efectiva**, porque `max_attempts=1` no
> significa eso en el SDK— y `/ready` necesita un **presupuesto total compartido**, no un
> timeout por dependencia, para caber bajo el `timeout: 3s` de Traefik.
>
> **Aprobada el 2026-09-06.** El usuario escribió la expresión exacta de §27. Las decisiones
> de esta ficha dejan de ser propuestas y quedan **Aceptadas y Vigentes**; ver §26 y §27.

### Revisión de definición — 2026-09-06

Tres puntos de diseño corregidos tras la revisión del usuario. **Ninguno introduce código.**

| # | Punto | Qué cambió |
| --- | --- | --- |
| **1** | **BLOCKER — `/ready` no detectaba un bucket inexistente** | §12.2 **reescrita**. `existe()` queda **descartada**: se midió que devuelve `404 Code='404'` idéntico para «clave ausente» y «bucket ausente», así que `/ready` habría respondido `200` con el almacenamiento inutilizable. Sustituida por una **capacidad explícita del puerto** implementada con `ListObjectsV2(Prefix, MaxKeys=1)`, que sí distingue los cinco escenarios exigidos. `R-017-8` pasa de «riesgo tolerado» a **resuelto** |
| **2** | **Semántica del healthcheck de Docker** | §12.4: **retirada la afirmación falsa** de que Docker reinicia un contenedor *unhealthy*. La recomendación **C no cambia**; su justificación pasa a ser **semántica** más el efecto real sobre `depends_on`. `R-017-1` **retirado** y sustituido por `R-017-1b` |
| **3** | **`X-Request-ID` repetida** | §9.3: **retirada la dependencia** de que «Starlette devuelve el primero». Nueva política *fail-safe*: **2 o más ⇒ se descartan todas y se genera uno nuevo** |

Se conserva sin cambio todo lo demás: cabecera `X-Request-ID`, `ContextVar` +
`logging.Filter`, `error.request_id` intacto, `AuditEvent.request_id` poblado, DTO de
auditoría con **exactamente 5 campos**, sin frontend, logs JSON por `stdout`,
`uvicorn.error` conservado y `uvicorn.access` sustituido, `duration_ms` monotónico, sondas
satisfactorias a `DEBUG`, la separación `AuditEvent` ≠ log, la reconciliación de **O-09**
(§6) y **0 dependencias nuevas**.

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

**Instantánea de la preparación, tomada el 2026-09-06.** Registra lo comprobado **al crear
la rama**; no describe el estado operativo actual de ningún repositorio, que se consulta en
vivo (criterio 12 de la Definition of Done).

| # | Comprobación | backend | infra |
| --- | --- | --- | --- |
| 1 | `main == origin/main` | ✔ `fa29c3d2` | ✔ `68d2a710` |
| 2 | Working tree limpio antes de crear la rama | ✔ vacío | ✔ vacío |
| 3 | Rama creada **desde `main`** | ✔ | ✔ |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | ✔ | ✔ |
| 5 | `git rev-list --count main..HEAD` | **0** | **0** |

**`personal-blog-frontend` no participa.** Permanece en `main` (`0f3c9912`), limpio y
**sin** rama `Task/017`. Justificación medida en §4.

---

## 1. Objetivo

Que **cualquier petición al backend pueda localizarse y explicarse de extremo a extremo**
en el entorno local, con un único identificador visible para quien la hizo, presente en
todas las líneas de log de esa petición y —cuando la petición fue una escritura
administrativa— en su evento de auditoría; y que el operador pueda comprobar si el
servicio está **vivo** (`/health`) y si sus **dependencias** están disponibles (`/ready`),
sin que ninguno de esos caminos filtre un secreto.

Cierra **O-01**, **O-02**, **O-04**, **O-07** y **O-08**; verifica **O-03**; conecta
**O-05** con el correlation ID. Cierra el riesgo **R-36** en el plano local.

---

## 2. Fuentes canónicas consultadas

| Documento | Qué aporta |
| --- | --- |
| [`non-functional-requirements.md`](../architecture/non-functional-requirements.md) §5 | Matriz **O-01…O-10** y sus propietarios |
| [`non-functional-requirements.md`](../architecture/non-functional-requirements.md) §2 | **S-07** (no exponer trazas) y **S-08** (no registrar secretos) |
| [`api-contracts.md`](../architecture/api-contracts.md) §2, §7, §8, §9, §11, §15 | `/health`, `/ready`, modelo de error con `request_id`, `503`, correlation ID, **cabecera abierta para `Task/017`**, DTO de auditoría |
| [`data-model.md`](../architecture/data-model.md) §4.10, §5 | `audit_events.request_id` `VARCHAR(64)` *nullable*, índice `ix_audit_events_request_id` |
| [`software-architecture.md`](../architecture/software-architecture.md) §3.1, §3.4, §7 | `/ready` vive en `app/api`; `shared/logging` es «logs JSON y **propagación del correlation ID**» |
| [`security-boundaries.md`](../architecture/security-boundaries.md) §5, §7, §11 | «Campos a redactar en los logs → `Task/017`»; **A-01**, **A-13** |
| [`overview.md`](../architecture/overview.md) §5 principio 9 | **Telemetría portable** — invariante vigente desde `Task/006.2` |
| [`ADR-008`](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) | Frontera con producción; «ninguna tarea puede acoplar el dominio a un destino de telemetría» |
| [`STAGE-05`](../stages/STAGE-05-quality-security.md) | Alcance **exclusivamente local**; criterios de salida de etapa |
| [`ROADMAP.md`](../project-management/ROADMAP.md) L243, L431, L439 | Alcance y mapa de responsabilidades transversales |
| [`STATUS.md`](../project-management/STATUS.md) | **R-36** abierto con propietario `Task/017` y `Task/018` |
| [`CONTENT_MODEL.md`](../product/CONTENT_MODEL.md) §3.9 | **Las lecturas no se auditan**; catálogo cerrado de 15 acciones |
| [`DEFINITION_OF_DONE.md`](../project-management/DEFINITION_OF_DONE.md) §3 | Backend funcional (**B-1…B-12**) **e** infraestructura local |
| [`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md) | Ciclo RED/GREEN/REFACTOR, §4 excepciones, §9 protección de los tests |
| [`local-environment.md`](../runbooks/local-environment.md) §7 | Diagnóstico actual; no responde aún a las preguntas de observabilidad |
| `TASK-005`, `TASK-011`, `TASK-012.1`, `TASK-015`, `TASK-016` | Deuda explícitamente dirigida a `Task/017` |

---

## 3. Dependencias

`Task/014`, `Task/015` y `Task/016`: **las tres Aprobadas**. No hay dependencia bloqueante
pendiente.

---

## 4. Dentro y fuera del alcance

### 4.1 Dentro

- [ ] **O-01** — esquema de log JSON estable, con campos parseables (no una cadena).
- [ ] **O-02** — contrato del correlation ID: cabecera, formato, política de entrada,
      propagación a respuesta y a **todos** los logs de la petición.
- [ ] **O-03** — **verificación** de que `/health` es liveness pura y sigue respondiendo
      con las dependencias caídas.
- [ ] **O-04** — `GET /ready` que ejerce PostgreSQL y `ObjectStorage` de verdad.
- [ ] **O-07** — recorrido diagnóstico reproducible con Docker y **Portainer**.
- [ ] **O-08** — política de redacción: matriz de campos prohibidos, sanitizados y
      permitidos, con pruebas de señuelo. Cierra **R-36** en el plano local.
- [ ] **O-05 (participación)** — que `AuditEvent.request_id` guarde **el mismo** valor que
      el cliente ve y que aparece en los logs, también en el **camino feliz**.
- [ ] Enrutado local de `/ready` en Traefik (infra) y decisión sobre el healthcheck de
      Docker.
- [ ] Sección de observabilidad en [`local-environment.md`](../runbooks/local-environment.md).

### 4.2 Fuera — con su propietario

| Fuera de alcance | Propietario |
| --- | --- |
| **O-06** CloudWatch y su retención (**D-11**) | `Task/031`, `Task/041` |
| **O-09** privacidad de la telemetría **exportada a terceros** | `Task/029`, `Task/018`, `Task/040` |
| **O-10** observabilidad del **VPS** de producción | `Task/029`, validado por `Task/040` |
| Grafana Cloud, **Grafana Alloy**, Prometheus, Loki, Tempo, OpenTelemetry Collector | `Task/029`, `Task/031` — **ADR-008**; nada de esto se instala aquí, ni local ni en producción |
| Cabeceras de seguridad, CORS efectivo, endurecimiento del log | `Task/018` |
| Cualquier cambio en `personal-blog-frontend` | — **No procede**: ver §4.3 |
| Umbrales de rendimiento (**U-1…U-9**) | `Task/016`, ya **Aprobada**; `duration_ms` **no** introduce umbral nuevo |
| Retención, rotación y archivado del historial de auditoría | Operación |

### 4.3 Por qué el frontend no participa — **medido**

`ROADMAP.md` L243 asigna a `Task/017` los repositorios **`backend, infra`**. La
verificación confirma que esa asignación es **suficiente**, no solo formal:

| Comprobación | Resultado medido |
| --- | --- |
| ¿El frontend envía alguna cabecera de correlación? | **No.** `src/services/http/httpClient.ts:189` construye `Headers` solo con `Accept` y, si hay cuerpo, `Content-Type` |
| ¿De dónde lee el frontend el `requestId`? | **Del cuerpo de error**, no de una cabecera: `src/services/http/httpError.ts:109` → `leerTexto(error?.request_id)` |
| ¿Cambia ese contrato esta tarea? | **No.** `error.request_id` ya existe y conserva forma y semántica |
| ¿El panel muestra el `request_id` de un evento de auditoría? | **No, y no debe**: el DTO `v1` no lo transporta (`TASK-015-report` §deuda 8) |

**Conclusión:** con el ID **generado en el servidor**, el frontend funciona sin un solo
cambio, y con el ID **aceptado del cliente** tampoco cambia, porque no envía ninguno y cae
en el *fallback*. **No se crea rama en `personal-blog-frontend`.**

---

## 5. Matriz O-01…O-10 — estado antes de `Task/017`

Estado **medido** el 2026-09-06 contra el stack local en marcha y el código de
`main`.

| # | Requisito | Owner canónico | Estado **antes** | Qué debe demostrar `Task/017` | Fuera |
| --- | --- | --- | --- | --- | --- |
| **O-01** | Logs en JSON, estructurados y parseables | `Task/017` | **Parcial.** 2 272/2 272 líneas son JSON válido y `configure_logging` ya unifica el formato de Uvicorn. **Pero** el 98,1 % de las líneas son `uvicorn.access`, cuyo método, ruta, estado y dirección viajan **dentro de la cadena `message`**: JSON válido, **no parseable por campos** | Un evento por petición con `method`, `path`, `status_code`, `duration_ms` y `request_id` como **campos propios**; una línea JSON por evento | Formato de los logs de Traefik, PostgreSQL y MinIO |
| **O-02** | Correlation ID en cada petición, propagado a todos sus logs y a la respuesta | `Task/017` | **No cumplido.** No hay middleware. `request_id_de()` (`app/shared/errors/handlers.py:71`) solo se invoca en la ruta de **error** y en `contexto_de_la_peticion`. **Ninguna** respuesta lleva cabecera de correlación —verificado en 7 rutas—. La línea `uvicorn.access` de la misma petición **no lleva el ID** | Cabecera fijada; ID en respuesta de **toda** petición (2xx, 4xx, 5xx, `/health`, `/ready`); mismo ID en todos los logs de esa petición | Propagación a servicios externos |
| **O-03** | `/health` refleja la vivacidad del proceso | `Task/005` ✔, `Task/017` | **Cumplido, sin verificar bajo fallo.** `GET /health` → `200`, `application/json`, `{"status":"ok","service":…,"version":…}`. No toca DB ni almacenamiento; el motor es perezoso (`session.py`) | Que sigue respondiendo `200` con PostgreSQL **y** MinIO caídos, y que **no** se convierte en readiness | Cambiar su contrato |
| **O-04** | `/ready` comprueba base de datos y almacenamiento | `Task/017` | **No existe.** `GET /ready` por Traefik devuelve **`200` con el `index.html` de la SPA** (2 406 bytes, `Server: nginx`): la ruta no está en `routes.yml` y cae en el *fallback* del frontend. Mismo defecto de clase que `Task/016` corrigió en `robots.txt` y `sitemap.xml` | `200` con ambas listas; `503` si alguna falla — **incluido el bucket inexistente** (§12.2, casos 42a–42e); sin mutar nada; sin filtrar detalles | Readiness del VPS o de la nube |
| **O-05** | Auditoría administrativa de toda acción que modifica datos | `Task/011` ✔, `Task/012` ✔ | **Cumplido en su alcance.** 15 acciones, historial inmutable, lecturas no auditadas. `request_id` **ya se escribe**: comprobado extremo a extremo — respuesta `89be982d-…` = `audit_events.request_id` = `request_id` del log | Que el ID sea **alcanzable también en el camino feliz**, no solo cuando la petición acaba en error | Nuevas acciones, filtros, retención |
| **O-06** | CloudWatch mínimo con retención explícita | **`Task/031`, `Task/041`** | No aplica en local | **Nada.** No se absorbe | Todo |
| **O-07** | Logs locales visibles por Docker y Portainer | `Task/003` ✔, `Task/017` | **Parcial.** Van a `stdout`, Docker los captura y Portainer los muestra. **Pero no se puede filtrar una petición por su ID**, porque la línea de acceso no lo lleva | Recorrido diagnóstico reproducible de 6 pasos (§13) | Instalar otra UI; cambiar el privilegio de Portainer |
| **O-08** | Los logs no contienen contraseñas, tokens, secretos ni datos personales innecesarios | `Task/017`, `Task/018` | **Se cumple hoy por disciplina, no por mecanismo** (**R-36**, Abierto). Medido: la **query string** entra al log (`GET /api/v1/posts?page_size=1`), la **dirección del par** entra en cada línea, y `context` emite **todo** atributo propio del `LogRecord` — incluido `color_message` de Uvicorn, con secuencias ANSI | Matriz de campos, redacción efectiva y pruebas de señuelo que fallen si la redacción se rompe | Endurecimiento global de cabeceras (`Task/018`) |
| **O-09** | La telemetría **exportada a un tercero** no lleva secretos ni datos personales innecesarios | **`Task/029`, `Task/018`, `Task/040`** | No aplica: en local **no se exporta** telemetría a ningún tercero | **Nada.** No se absorbe. Ver §6 | Todo |
| **O-10** | La observabilidad del VPS **sale del host** | **`Task/029`, `Task/040`** | No aplica | **Nada.** Negado explícitamente en 4 documentos desde `Task/005.5` (AUD-FIX-022) | Todo |

---

## 6. Reconciliación: «telemetría portable» ↔ **O-09**

### 6.1 La divergencia, tal como está escrita

`ROADMAP.md` L243 dice, de `Task/017`:

> «**La telemetría debe ser portable**: el dominio no se acopla a CloudWatch, Grafana, Loki
> ni Prometheus (**O-09**).»

`non-functional-requirements.md` L142 define **O-09** como otra cosa:

> «**La telemetría enviada fuera del proyecto** […] **no contiene secretos ni datos
> personales innecesarios**», con propietarios **`Task/029`, `Task/018`, `Task/040`**.

Son **dos invariantes distintas**: una de **portabilidad**, otra de **privacidad**.

### 6.2 Qué demuestra la investigación

| Pregunta de §8 del encargo | Respuesta | Evidencia |
| --- | --- | --- |
| **A)** ¿La neutralidad de proveedor ya es otra invariante existente? | **Sí.** Es el **principio 9 de `overview.md` §5, «Telemetría portable»**, vigente desde `Task/006.2` (aprobada 2026-08-23) | `overview.md:171-174`, con la misma redacción literal — «no se acopla a CloudWatch, Grafana, Loki ni Prometheus; los destinos los absorben la infraestructura y sus adaptadores» |
| ¿Está respaldada por una decisión aceptada? | **Sí.** `ADR-008` la enuncia en *«Qué NO decide este ADR»* y la convierte en regla en *«Cumplimiento»*: «Ninguna tarea puede **acoplar el dominio de la aplicación** a un destino concreto de telemetría» | `ADR-008` L112-115 y §Cumplimiento |
| **B)** ¿`ROADMAP` usa **O-09** como referencia imprecisa? | **Sí.** Cita **O-09** para una afirmación de **portabilidad**, cuando el requisito **O-09** vigente es de **privacidad al exportar** y **no tiene a `Task/017` entre sus propietarios** | `ROADMAP.md:243` frente a `non-functional-requirements.md:142` |
| **C)** ¿Hace falta una precisión documental? | **Sí, y solo eso.** Corregir la **referencia** de `ROADMAP.md` L243: la portabilidad es el **principio 9 de `overview.md`** y **ADR-008**, no **O-09** | — |
| **D)** ¿Hace falta una decisión nueva? | **No.** No hay decisión arquitectónica nueva: `ADR-008` ya decidió, y está **Aceptada**. Abrir un ADR aquí duplicaría una decisión vigente y contradiría ADR-004 («sin abstracciones ni capas sin uso demostrado») | — |

### 6.3 Resultado — **las dos invariantes se preservan**

1. **Privacidad al exportar (O-09)** conserva su definición y sus propietarios
   `Task/029`, `Task/018`, `Task/040`. `Task/017` **no la absorbe**.
2. **Neutralidad de proveedor (principio 9 + ADR-008)** sigue siendo obligatoria y **sí**
   aplica a `Task/017`: el log JSON sale por `stdout` y **ningún** módulo de la aplicación
   importa un SDK de destino de telemetría.

**Ninguna definición se sobrescribe.** La única corrección propuesta es de **referencia
cruzada**, en una línea de `ROADMAP.md`, y queda como **Propuesta** hasta la aprobación.

> **Nota adicional, no bloqueante.** `api-contracts.md:811` cita **O-09** para justificar
> que `ip_address` no entre en el DTO de auditoría. Ese uso es **adyacente pero no
> idéntico**: `ip_address` en una respuesta del API no es «telemetría exportada a un
> tercero». La razón sólida de esa exclusión es **A-13** de `security-boundaries.md`, que
> el mismo párrafo ya cita. Se registra como observación; **no** se propone cambiarlo aquí:
> el DTO de auditoría es superficie de `Task/012.1`, ya aprobada.

---

## 7. Baseline de logging — **medido** el 2026-09-06

### 7.1 Qué existe

`app/shared/logging/configuration.py` (de `Task/005`) ya aporta más de lo esperado:

| Elemento | Estado |
| --- | --- |
| `JsonLogFormatter` | Existe. Emite `timestamp`, `level`, `logger`, `message`, `module`, `line`, más `context`, `exception` y `stack` cuando los hay |
| Destino | `logging.StreamHandler(stream=sys.stdout)` — **solo `stdout`**, nunca archivo |
| Reloj | **UTC explícito**, con `timezone.utc` y `time.gmtime`; sufijo `Z` y precisión de milisegundos |
| Idempotencia | `configure_logging` **reemplaza** los manejadores en lugar de añadirlos |
| Uvicorn | `uvicorn`, `uvicorn.error` y `uvicorn.access` quedan con `handlers.clear()` y `propagate = True` |
| Formato configurable | `BLOG_LOG_FORMAT` (`json` por defecto) y `BLOG_LOG_LEVEL` (`INFO`) |

### 7.2 Qué se midió en el contenedor real

Sobre `docker compose logs backend` completo — **2 272 líneas**:

| Métrica | Valor |
| --- | --- |
| Líneas JSON válidas | **2 272 / 2 272 (100 %)** — 0 no parseables |
| Campos de nivel raíz observados | `timestamp`, `level`, `logger`, `message`, `module`, `line`, `context` |
| Líneas de `uvicorn.access` | **2 228 (98,1 %)** |
| De ellas, `GET /health` | **2 061 — el 90,8 % del log total es ruido de sondas** |
| Líneas de `uvicorn.error` | 4 (todas de arranque) |
| Líneas de la aplicación (`app.*`) | **39** |
| Líneas con `request_id` | **38** — todas emitidas por `app.shared.errors.handlers` |
| Líneas con `color_message` (ANSI de Uvicorn filtrado a `context`) | 2 |

### 7.3 Respuestas exactas a las preguntas del encargo

| Pregunta | Respuesta **medida** |
| --- | --- |
| Qué logs existen | Arranque (`app.main`), ciclo de vida de Uvicorn (`uvicorn.error`), acceso por petición (`uvicorn.access`), errores (`app.shared.errors.handlers`) y subida de imagen (`app.modules.media.application.subir_imagen`). **Nada más**: solo hay **3** `get_logger` en toda la aplicación |
| En qué formato | **JSON, una línea por evento**, `ensure_ascii=False`, `default=str` |
| Qué campos | Los 6 fijos + `context` + `exception`/`stack` |
| Qué sale por `stdout`/`stderr` | **Todo por `stdout`.** Un único `StreamHandler`; nada por `stderr` |
| ¿Uvicorn emite un segundo formato? | **No.** `configure_logging` gana la carrera y limpia sus manejadores: `uvicorn.access` sale ya en JSON. **No hay doble formato** |
| ¿Hay un log por petición? | **Sí**, pero es el de `uvicorn.access` y **no sirve para diagnóstico**: `"172.22.0.4:35932 - \"GET /health HTTP/1.1\" 200"` en una sola cadena, **sin** `request_id` ni `duration_ms` |
| ¿Las excepciones llevan contexto? | **Sí**: `handle_unexpected_error` usa `_logger.exception` con `request_id`, `path` y `method`, y el `JsonLogFormatter` serializa la traza en `exception` |
| ¿`request_id` existe en *runtime*? | **Sí, pero solo en dos caminos**: los manejadores de error y `contexto_de_la_peticion` (`Task/011`). Se memoriza en `request.state.request_id` |
| ¿Aparece en las respuestas? | **No.** Ninguna cabecera de correlación en ninguna de las 7 rutas medidas |
| ¿Aparece en el cuerpo de error? | **Sí**, como `error.request_id`, en `401`, `403`, `404` y `422` — verificado |
| ¿Se guarda en `AuditEvent`? | **Sí** — ver §11 |

### 7.4 El hueco exacto

> El sistema **ya genera** un identificador correcto y **ya lo persiste** en auditoría.
> Lo que falta es que **salga**: no llega al cliente, no llega al log de la petición, y en
> una escritura administrativa **exitosa** el valor queda escrito en `audit_events` sin que
> nadie pueda conocerlo. Es un identificador **inalcanzable en el camino feliz**.

---

## 8. Uvicorn y logs duplicados

### 8.1 Diagnóstico — no hay duplicación de formato, sí de evento

Medido: **no** coexisten un log JSON propio y un access log textual. `configure_logging`
ya resolvió eso en `Task/005`. Lo que sí ocurre:

1. Una petición con error produce **dos líneas**: la del manejador de error
   (con `request_id`) y la de `uvicorn.access` (**sin** `request_id`). **No se pueden
   cruzar.**
2. `uvicorn.access` filtra `color_message` con secuencias ANSI dentro de `context`.
3. El 90,8 % del log son sondas a `/health`.

### 8.2 Estrategia propuesta

**Sustituir el access log de Uvicorn por el evento de petición propio.** Es decir:
desactivar **únicamente** `uvicorn.access` —poniéndolo por encima de `INFO`, o pasando
`--no-access-log`— y emitir desde el middleware propio un evento con los mismos datos
**como campos**, más `request_id` y `duration_ms`.

| Se conserva | Se retira |
| --- | --- |
| `uvicorn.error` **íntegro** (arranque, apagado y **errores de servidor**) | Solo `uvicorn.access` |
| El formato JSON unificado | La cadena `"ip:puerto - \"MÉTODO RUTA HTTP/1.1\" ESTADO"` |

**Por qué no al revés.** Adaptar `uvicorn.access` a campos estructurados exigiría un filtro
que reconstruya lo que Uvicorn ya aplanó en una cadena, y aun así no podría añadir
`request_id` —que Uvicorn no conoce— ni `duration_ms`. Sustituirlo cuesta menos y da más.

**Riesgo y su guarda:** perder errores del servidor. `uvicorn.error` **no se toca**, y la
matriz TDD (§15) incluye un caso que lo demuestra.

### 8.3 El ruido de las sondas

Medido: `/health` recibe **~8 peticiones/minuto** de dos fuentes independientes —el
`HEALTHCHECK` del `Dockerfile` cada 30 s y el `healthCheck` de Traefik cada 10 s—, es decir
**~11 500 líneas/día** idénticas. Propuesta: el evento de petición de `/health` y `/ready`
se emite a **`DEBUG`** cuando el resultado es satisfactorio, y a **`WARNING`/`ERROR`**
cuando no lo es. Un fallo de sonda **nunca** se silencia; el éxito repetido sí.

---

## 9. Contrato del correlation ID — **propuesta**

### 9.1 La cabecera: `X-Request-ID`

Comparación pedida, resuelta con evidencia del propio proyecto y no por costumbre:

| Criterio | `X-Request-ID` | `X-Correlation-ID` |
| --- | --- | --- |
| Nombre ya usado en el contrato | **`error.request_id`** (`api-contracts.md` §7) | — |
| Nombre en la base de datos | **`audit_events.request_id`**, con índice `ix_audit_events_request_id` | — |
| Nombre en el frontend | **`HttpError.requestId`** | — |
| Nombre en el código | `request_id_de()`, `new_request_id()`, `ContextoDeLaPeticion.request_id` | — |
| Compatibilidad API Gateway / Lambda | Encaja con `requestId` del contexto de API Gateway | Sin correspondencia |

**Decisión propuesta: `X-Request-ID`.** Es el **único** nombre que el proyecto ya usa en
las cuatro capas. Elegir `X-Correlation-ID` obligaría a que la cabecera se llamara distinto
del campo del cuerpo, de la columna y del atributo del frontend, sin ganar nada.

### 9.2 Formato y validación

| Aspecto | Propuesta | Por qué |
| --- | --- | --- |
| Formato generado | **UUID v4 canónico**, 36 caracteres | Es lo que `new_request_id()` ya produce; no cambia el valor que hoy ve el cliente |
| Longitud máxima aceptada | **64 caracteres** | **No es una elección**: `audit_events.request_id` es `VARCHAR(64)`. Un valor más largo provocaría un fallo de escritura *en la auditoría*, es decir, al final de una operación ya ejecutada |
| Alfabeto aceptado | `A-Z a-z 0-9 - _` | Excluye por construcción `\r`, `\n`, espacios, `:` y todo lo que pueda romper una cabecera o inyectar una línea de log falsa |
| Longitud mínima | **8 caracteres** | Un ID de un carácter no discrimina nada en una búsqueda |

### 9.3 Política de entrada — **aceptar si es válido, generar si no**

`api-contracts.md` §9 ya lo fija: *«se acepta el que envíe el cliente en una cabecera
acordada **o se genera uno**»*. La política propuesta respeta esa frase:

| # de cabeceras `X-Request-ID` | Comportamiento | Razón |
| --- | --- | --- |
| **0** | **Se genera** un UUID v4 | Caso normal; es lo que hace el frontend hoy |
| **Exactamente 1, válida** | **Se reutiliza** | Permite correlacionar desde `curl` o un cliente futuro |
| **Exactamente 1, inválida** (larga, con caracteres prohibidos, vacía) | **Se descarta y se genera uno nuevo.** La petición **no** se rechaza | Rechazar con `400` convertiría una cabecera de diagnóstico en una superficie de denegación de servicio trivial |
| **2 o más** | **Se descartan TODAS** —aunque alguna sea válida— **y se genera uno nuevo** | Ver abajo |

> **Corrección de diseño (2026-09-06).** La versión anterior decía «se toma una sola»
> apoyándose en que *«Starlette devuelve el primer valor»*. **Esa premisa se retira:** hacer
> depender la identidad de una petición de la política *first-wins* / *last-wins* de un
> framework —o de la de un proxy intermedio, que puede ser la contraria— produce
> exactamente la ambigüedad que un correlation ID existe para eliminar.
>
> **Una petición tiene exactamente un correlation ID.** Si llegan varios candidatos, no hay
> forma no arbitraria de elegir, así que **no se elige ninguno**: se descartan todos y se
> genera uno propio. Es *fail-safe* —la petición siempre acaba con un ID válido y único— y
> el resultado **no depende** de qué componente de la cadena resolvió la repetición.
>
> La detección se hace con `request.headers.getlist("x-request-id")` y contando: leer la
> cabecera de la forma habitual devolvería un solo valor y **ocultaría** la repetición.

**Un valor entrante nunca se registra tal cual.** Cuando se descarta —por inválido o por
repetido— el log registra únicamente un booleano:

```json
{"incoming_request_id_discarded": true}
```

**Nunca el valor ni los valores rechazados.** Escribirlos sería exactamente la inyección de
log que la validación evita.

### 9.4 Alcance de la propagación

Debe cubrir **toda** petición sin excepción: `2xx`, `4xx`, `5xx`, `404`, `422`, `/health`,
`/ready`, `/sitemap.xml`, `/docs`, pública y administrativa. Y aparecer, como mínimo, en:

1. **La cabecera de respuesta** `X-Request-ID` — incluidas las respuestas satisfactorias.
2. **Todos los logs** de esa petición.
3. **`error.request_id`**, sin cambio de forma (contrato ya publicado).
4. **`AuditEvent.request_id`**, cuando la petición produzca un evento.

### 9.5 Cómo se integra con `error.request_id`

**Sin romper nada.** `request_id_de(request)` ya memoriza en `request.state.request_id`, y
su propio *docstring* anticipa este cambio: *«cambiará **el origen** del valor sin tocar a
quien lo consume»*. El middleware pasa a ser quien **siembra** `request.state.request_id`
antes de que se ejecute nada; `request_id_de` lo encuentra ya puesto y lo devuelve. Los
manejadores de error, `contexto_de_la_peticion` y el frontend **no cambian**.

---

## 10. Contexto de logging — sin contaminar las firmas

**Propuesta: un `contextvars.ContextVar[str | None]` en `app/shared/logging/`**, sembrado
por el middleware y leído por un `logging.Filter` que inyecta `request_id` en cada
`LogRecord`.

| Regla | Cómo se cumple |
| --- | --- |
| Disponible en toda la petición sin pasar parámetros | El `ContextVar` es implícito para todo lo que corra en esa tarea |
| `domain` no depende del logger, del middleware ni de ningún proveedor | El dominio **no lee el `ContextVar`**: no emite logs. Sigue vigente el principio 9 de `overview.md` |
| No contaminar las firmas de los casos de uso | **Ninguna firma cambia.** `ContextoDeLaPeticion` ya transporta `request_id` para auditoría y **seguirá haciéndolo**: es un dato de negocio del evento, no logging |
| `stdlib` únicamente | `contextvars` y `logging` son biblioteca estándar |

**Por qué un `Filter` y no un `Formatter` propio:** el filtro añade el atributo al
`LogRecord`, así que el `request_id` aparece **también** en el formato `text`, y el
`JsonLogFormatter` no necesita conocer el concepto de petición.

---

## 11. Auditoría y `request_id` — **medido**, no supuesto

### 11.1 Quién crea `AuditEvent` hoy

`RegistroSqlDeAuditoria.registrar()` (`app/modules/audit/infrastructure/registro.py`),
que implementa el puerto `RegistroDeAuditoria` del dominio de `audit`. Añade y hace `flush`;
**no confirma**: el evento se hace duradero con la operación que lo produjo.

### 11.2 Cómo recibe actor, IP y `request_id`

`contexto_de_la_peticion` (`app/modules/authentication/presentation/dependencias.py:107`)
construye un `ContextoDeLaPeticion(origen, request_id)`, con `request_id = request_id_de(peticion)`.
Los **nueve** casos de uso administrativos lo propagan como `request_id=contexto.request_id`.

### 11.3 ¿Se escribe hoy? — **sí, y está comprobado**

Prueba de trazabilidad ejecutada el 2026-09-06 con un intento de acceso fallido contra un
correo inexistente (la operación auditada menos invasiva: no toca contenido ni ninguna
cuenta):

| Punto de observación | Valor |
| --- | --- |
| `error.request_id` de la respuesta `401` | `89be982d-13ab-4bb8-bac8-092344a16f6e` |
| `context.request_id` del log `WARNING` | `89be982d-13ab-4bb8-bac8-092344a16f6e` |
| `audit_events.request_id` en PostgreSQL | `89be982d-13ab-4bb8-bac8-092344a16f6e` |

**Los tres coinciden.** La cadena `request → log → AuditEvent` **ya funciona** cuando la
petición termina en error.

### 11.4 Dónde queda `NULL` — y el hueco real

`request_id` es *nullable*, pero **ningún camino de la aplicación lo deja `NULL`**: todos
los llamantes pasan `contexto.request_id`, que siempre tiene valor.

> **El hueco no es que falte el dato: es que el dato es inalcanzable.** En una escritura
> administrativa **exitosa** (`201`, `200`, `204`) el `request_id` se genera, se guarda en
> `audit_events`… y **no se devuelve al cliente ni aparece en ningún log**, porque no hay
> cabecera de respuesta y la única línea de esa petición es la de `uvicorn.access`, que no
> lo lleva. El operador ve una fila de auditoría con un identificador que **no puede
> encontrar en ningún otro sitio**.

### 11.5 La tensión con `Task/012.1` — resuelta como **A**

| Opción | Veredicto |
| --- | --- |
| **A. Solo poblar `AuditEvent.request_id` y hacerlo alcanzable** | **Elegida** |
| **B. Además exponer `request_id` en `GET /admin/audit-events`** | **No se implementa en `Task/017`** |

**Por qué A.** La deuda registrada es *«Exponer `request_id` **una vez** `Task/017` fije la
cabecera»* (`api-contracts.md` §15.7): fijar la cabecera es la **condición**, no la orden.
Y la exclusión de `Task/012.1` no se apoyaba solo en eso: `TASK-012.1` §5.2 registra que
**añadir un campo opcional después es compatible; retirarlo, no** (§10, reglas 2 y 3), y
**Q-1** lo dejó como **decisión del usuario**.

Los cinco requisitos que el encargo exige para ampliar el DTO **no se satisfacen hoy**:

| Requisito | Estado |
| --- | --- |
| Fuente canónica | Existe, pero **condicional** y sin obligar |
| Compatibilidad | ✔ Añadir es compatible |
| **Beneficio real** | ✗ **No hay consumidor.** El frontend **no participa** en `Task/017` y no puede mostrarlo (`TASK-015-report` §deuda 8) |
| Tests | Posibles, pero probarían un campo que nadie lee |
| Impacto contractual | **Irreversible**: retirar un campo de `v1` exigiría `/api/v2` y un ADR |

**Conclusión:** exponerlo ahora sería congelar superficie `v1` permanente **sin consumidor**,
justo lo que `Task/012.1` rechazó para `actor_id`, `event_metadata` e `ip_address`. Queda
como deuda con condición explícita: **cuando exista una tarea de frontend que lo consuma**.

### 11.6 Lo que no cambia

- `AuditEvent` sigue siendo **inmutable**; las guardas de `Task/008` no se tocan.
- **Las lecturas siguen sin auditarse** (`CONTENT_MODEL.md` §3.9).
- El catálogo de **15 acciones** no se amplía.
- **Ningún log va a `audit_events`.** Ver §14.

---

## 12. `/health` y `/ready`

### 12.1 `/health` — liveness, verificación de **O-03**

`Task/017` **no lo modifica**. Lo **verifica**:

| Debe | No debe |
| --- | --- |
| Responder `200` con el proceso HTTP en pie | Consultar **PostgreSQL** |
| `application/json` | Consultar **MinIO/S3** |
| Cuerpo sin entorno, dependencias ni versiones de terceros | Consultar **ningún servicio externo** |
| **Seguir respondiendo `200` con PostgreSQL y MinIO caídos** | Convertirse en readiness |

**La razón vigente es semántica**, la misma de §12.4: `/health` responde *«¿el proceso está
vivo?»*, y la respuesta a esa pregunta **no cambia** porque PostgreSQL se caiga. Mezclarlas
dejaría el sistema sin forma de distinguir un proceso muerto de una dependencia caída.

> **Observación menor, no corregida aquí.** El *docstring* de `app/api/health.py`
> (`Task/005`, aprobada) justifica lo mismo diciendo que *«un healthcheck que consulta la
> base de datos **reinicia el contenedor**»*. Esa premisa **no se sostiene en Docker
> Compose**, que no reinicia por `HEALTHCHECK` (§12.4). **La conclusión del código es
> correcta; solo su razón es imprecisa.** Se registra por honestidad; ajustar ese comentario
> es un cambio cosmético que esta tarea puede hacer al tocar el archivo, **sin** alterar el
> comportamiento de `Task/005`.

La verificación bajo fallo **falta** y es entregable de esta tarea.

### 12.2 `/ready` — diseño propuesto

| Aspecto | Propuesta |
| --- | --- |
| Ruta | **`GET /ready`**, **fuera** de `/api/v1`, junto a `/health` (`software-architecture.md` §3.1) |
| Autenticación | Ninguna (`api-contracts.md` §2) |
| `200` | **Todas** las dependencias comprobadas responden |
| `503` | **Alguna** falla — `service_unavailable`, ya en el catálogo (`api-contracts.md` §8) |
| Cuerpo `200` | `{"status":"ready"}` |
| Cuerpo `503` | `{"status":"not_ready"}` |
| Cacheo | `Cache-Control: no-store` |

**Por qué un cuerpo sin componentes.** Un `{"database":"down"}` le dice a un cliente
anónimo **qué** parte de la infraestructura está caída, que es reconocimiento gratuito.
`api-contracts.md` §2 ya lo exige: *«Ninguno expone detalles internos»*. El operador
obtiene el detalle **del log**, que sí distingue componente y motivo. El código HTTP ya
transporta la única información que el consumidor necesita.

#### PostgreSQL

`SELECT 1` mediante `sqlalchemy.text`, sobre la sesión de petición. Es de solo lectura,
no muta y **ejercita el pool de verdad** —con `pool_pre_ping` activo, valida la conexión—.

#### `ObjectStorage` — decisión **reabierta y corregida** el 2026-09-06

> **La propuesta anterior era insuficiente y queda retirada.** Reutilizar
> `existe(<clave-sonda>)` **no cierra O-04**: no distingue «almacenamiento operativo con el
> objeto ausente» de «bucket configurado inexistente», así que `/ready` podría responder
> `200` con la aplicación incapaz de operar sobre su almacenamiento. Eso contradice
> `api-contracts.md` §2 —*«disponibilidad real: base de datos y almacenamiento
> accesibles»*—. La decisión se reabre y se resuelve **con medición**.

##### El falso positivo, **demostrado** contra MinIO real

Los cuatro métodos restantes se descartan solos: `guardar` y `eliminar` **mutan**;
`obtener` descarga bytes; `acceso_temporal` **firma en local, sin viajar a la red** —el
propio código lo dice: *«esta operación funciona aunque el almacenamiento esté caído»*—,
así que no comprueba nada. Queda `existe()`, y esto es lo que devuelve:

| Escenario | `HeadObject` | Traducción de `_es_ausencia()` |
| --- | --- | --- |
| Bucket **existente**, clave inexistente | `ClientError HTTP=404 Code='404'` | `existe() → False` |
| Bucket **inexistente** | `ClientError HTTP=404 Code='404'` | `existe() → False` |

**Respuestas idénticas, byte a byte.** `_CODIGOS_DE_AUSENCIA` contiene `"404"`, así que las
dos rutas colapsan en el mismo `False`. **El falso positivo es real y está medido**, no es
una hipótesis teórica.

##### Las cuatro alternativas, medidas

Medición ejecutada contra MinIO local con `connect_timeout=3`, `read_timeout=3` y
`max_attempts=1`. **Ninguna operación creó, modificó ni borró nada.**

| Escenario | `head_object` | `head_bucket` | `list_objects_v2(Prefix, MaxKeys=1)` |
| --- | --- | --- | --- |
| Bucket OK, sonda ausente | `404 Code='404'` | **OK** | **OK, `KeyCount=0`** |
| **Bucket inexistente** | `404 Code='404'` ✗ | `404 Code='404'` ✔ | **`404 Code='NoSuchBucket'`** ✔ |
| Credenciales inválidas | `403 Code='403'` | `403 Code='403'` | **`403 Code='InvalidAccessKeyId'`** |
| Endpoint caído | — | `EndpointConnectionError` | `EndpointConnectionError` |

**Diferencia decisiva entre las dos candidatas válidas.** `HeadBucket` es una respuesta
HTTP **sin cuerpo**, así que `botocore` no puede leer el código de error del XML y entrega
`Code='404'` / `Code='403'` —cadenas numéricas sin semántica—. `ListObjectsV2` sí trae
cuerpo, y devuelve **`NoSuchBucket` e `InvalidAccessKeyId`**: códigos que el log puede
registrar como motivo distinguible, que es justo lo que §12.3 exige.

##### Evaluación de las opciones del encargo

| Opción | Veredicto |
| --- | --- |
| **A. Capacidad explícita en el puerto `ObjectStorage`** | **Aceptada como forma.** El uso está **demostrado por O-04** y por la medición: **ningún método existente puede cumplirlo**. `ADR-004`/`M-06` prohíben la abstracción *sin uso demostrado*; aquí el uso está demostrado, así que **ya no son argumento para descartarla** |
| **B. `HeadBucket`** | **Descartada** — semánticamente correcta, pero pierde el código de error (arriba) y, sobre todo, **no admite prefijo**, lo que impide acotar el permiso IAM (siguiente apartado) |
| **C. *Sentinel* conocido** | **Descartada** — ver más abajo |
| **D. Estrategia provider-neutral** | **`ListObjectsV2` con prefijo sonda y `MaxKeys=1`** — es la elegida como **mecanismo** de A |

**Decisión: A + D.** Una capacidad nueva y explícita en el puerto —
`comprobar_disponibilidad()` — implementada en `AlmacenamientoCompatibleS3` con
`ListObjectsV2(Prefix=<prefijo sonda>, MaxKeys=1)`.

| Aspecto | Diseño |
| --- | --- |
| Firma | `comprobar_disponibilidad() -> None` |
| Éxito | Retorna sin valor |
| Fallo | Lanza `FalloDelProveedorDeAlmacenamientoError` mediante el `_fallo()` **ya existente**, que **no filtra credenciales ni trazas** y deja el original en `__cause__` para el log |
| Prefijo sonda | Constante interna, p. ej. `_readiness/`. **Nunca colisiona** con una clave real: las claves de medios son **UUID v4** (`Task/010`) |
| Neutralidad | `ListObjectsV2` es del protocolo S3, implementado por MinIO y S3. El dominio sigue viendo solo `ObjectStorage` (**T-03**, principio 9) |

##### Por qué **no** el *sentinel* (opción C)

| Criterio | Consecuencia |
| --- | --- |
| *Provisioning* local | El runbook §10 ya obliga a crear el bucket a mano; añadir un objeto obligatorio suma un paso frágil más |
| `Task/030` y *lifecycle* | Una regla de expiración podría **borrar el sentinel** sin que nadie lo note |
| Mutación | Crearlo **es** una escritura, justo lo que la sonda debe evitar |
| **Riesgo dominante** | Si el sentinel desaparece, `/ready` responde `503` con el almacenamiento **perfectamente sano**: un **falso negativo**. Y es **peor** que el falso positivo que estamos corrigiendo, porque Traefik retiraría de rotación un backend que sí podía servir |

##### Permisos IAM y mínimo privilegio — consecuencia para `Task/030`

**Esto es una ampliación de permisos y se documenta como tal**, no se introduce en
silencio.

Hoy la aplicación necesita, sobre los **objetos**: `s3:PutObject` (`guardar`),
`s3:GetObject` (`obtener`, `existe`, firma) y `s3:DeleteObject` (`eliminar`).
**Ninguna operación actual necesita `s3:ListBucket`.**

Tanto `HeadBucket` como `ListObjectsV2` exigen **`s3:ListBucket`** sobre el recurso
**bucket**. La diferencia está en si ese permiso puede acotarse:

| Operación | Permiso | ¿Acotable? | Enumeración que concede |
| --- | --- | --- | --- |
| `HeadBucket` | `s3:ListBucket` | **No.** No envía prefijo, así que una `Condition` sobre `s3:prefix` **denegaría la propia sonda** | **Todo el bucket** |
| **`ListObjectsV2(Prefix=…)`** | `s3:ListBucket` | **Sí**, con `Condition: StringEquals: {"s3:prefix": "_readiness/"}` | **Solo** bajo el prefijo sonda, que está **vacío por diseño** |

> **Consecuencia registrada para `Task/030`:** la política del bucket debe conceder
> `s3:ListBucket` **condicionado al prefijo de la sonda**. Así, un compromiso de la Lambda
> **no** permite enumerar los medios del blog — que es exactamente lo que `HeadBucket`
> sí habría permitido. `Task/030` es owner de la política; aquí queda **la restricción que
> debe aplicar y su razón**, no la política.

##### Lo que esta decisión sí y no comprueba

| Comprueba | No comprueba |
| --- | --- |
| Que el endpoint responde | Que se pueda **escribir** (exigiría mutar) |
| Que las credenciales son válidas y la firma correcta | La cuota o el espacio disponible |
| Que **el bucket configurado existe** | La política completa de la Lambda |

### 12.3 Timeouts y degradación

Estado **medido** de los timeouts actuales:

| Dependencia | Timeout hoy | Riesgo |
| --- | --- | --- |
| PostgreSQL | `connect_timeout` = **10 s** (`BLOG_DATABASE_CONNECT_TIMEOUT_SECONDS`), configurable | Cubre la **conexión**. **No hay `statement_timeout`**: una consulta sobre una conexión ya abierta puede colgarse indefinidamente |
| `ObjectStorage` | **Ninguno configurado.** `Config` solo fija `signature_version` y `addressing_style` | Se heredan los **valores por defecto de botocore**, que además **reintenta**. Un MinIO inalcanzable puede bloquear la sonda **decenas de segundos** |

> **Este es el hallazgo que impide diseñar `/ready` «a ojo».** Con los defaults actuales,
> `/ready` podría tardar más que el `timeout` del propio healthcheck que lo consulta,
> produciendo exactamente la *probe cascade* que hay que evitar.

**Qué debe fijar la implementación:**

1. Un **presupuesto total de readiness** menor que el `timeout` de quien la consume — el
   `healthCheck` de Traefik usa hoy `timeout: 3s`.
2. Timeouts **explícitos y acotados** para la sonda de almacenamiento, con **reintentos
   desactivados**: una sonda no reintenta, informa. La medición de §12.2 se ejecutó con
   `connect_timeout=3`, `read_timeout=3` y `retries={"max_attempts": 1}`, y con esos
   valores los cuatro escenarios —incluido **endpoint caído**— resolvieron sin colgarse.
   Son el **punto de partida verificado**, no un valor inventado; la implementación los
   confirma o los ajusta con su propia medición.
3. **Qué excepción se captura**: `ErrorDeAlmacenamiento` y sus derivadas para el
   almacenamiento; `SQLAlchemyError` para la base. **Nunca un `except Exception` mudo.**
4. **Qué se registra**: componente, resultado, duración y **motivo sanitizado** — el código
   semántico (`NoSuchBucket`, `InvalidAccessKeyId`) que `ListObjectsV2` sí entrega.
5. **Qué se devuelve**: solo `not_ready` y `503`.
6. **Un cliente de sonda con su propia configuración de timeouts**, separado del cliente de
   operación: acortar el timeout general degradaría una subida legítima de imagen.

**La excepción detallada vive en el log sanitizado, nunca en la respuesta HTTP.**

### 12.4 Healthcheck de Docker — recomendación **C**

> **Corrección de una premisa equivocada (2026-09-06).** Una versión anterior de esta
> sección justificaba la recomendación afirmando que, con `restart: unless-stopped`, un
> contenedor *unhealthy* sería **reiniciado en bucle** por Docker. **Eso es falso.**
> Docker Compose **no reinicia un contenedor por el resultado de su `HEALTHCHECK`**: la
> política `restart` reacciona a que el **proceso termine**, no a que la sonda falle. Un
> contenedor puede permanecer indefinidamente en `running (unhealthy)`. El reinicio
> automático por healthcheck es comportamiento de **Docker Swarm**, que este proyecto no
> usa. **La recomendación no cambia; su justificación sí, y pasa a ser semántica.**

**La distinción de fondo:**

```text
/health  = ¿el PROCESO está vivo?
/ready   = ¿puede ATENDER TRÁFICO usando sus dependencias?
```

Son **dos preguntas distintas**, con **dos consumidores distintos** y **dos consecuencias
distintas**. Poner la misma sonda en ambos sitios destruye precisamente la separación que
**O-03** y **O-04** existen para crear.

| Opción | Efecto |
| --- | --- |
| A. Docker sigue con `/health`, Traefik también | El proxy **sigue enrutando** hacia un backend que no puede servir: `/ready` no tendría consumidor y **O-04 quedaría decorativo** |
| B. Docker pasa a `/ready` | **Descartada por dos efectos reales, ninguno de ellos «reinicio en bucle»** — ver abajo |
| **C. Cada sonda en su sitio** | **Recomendada** |

**Por qué se descarta B —efectos verificables en este Compose, sin especular:**

1. **Rompe el arranque en frío del proxy.** `traefik` declara
   `depends_on: backend: condition: service_healthy`. Si el `HEALTHCHECK` del backend
   dependiera de PostgreSQL y MinIO, un fallo de cualquiera de los dos dejaría al backend
   *unhealthy* y **Traefik no arrancaría** — el sitio entero caería por una dependencia
   que solo afecta a una parte del API.
2. **Confunde dos estados en el único indicador que Docker y Portainer muestran.** La
   columna de salud de `docker compose ps` y la vista de Portainer pasarían a decir
   *unhealthy* tanto si el proceso murió como si PostgreSQL está caído. El operador pierde
   de un vistazo la distinción que esta tarea construye — y O-07 es precisamente
   **diagnóstico por Portainer**.

**Recomendación C, en detalle:**

- **`HEALTHCHECK` del `Dockerfile` → sigue en `/health`.** Responde a *«¿el proceso está en
  pie?»*, que es la pregunta que Docker sabe formular sobre un contenedor. Es también la
  única sonda que debe seguir respondiendo `200` durante un incidente de dependencias, para
  que el contenedor permanezca en marcha **y sus logs sigan siendo consultables**.
- **`healthCheck` de Traefik → pasa a `/ready`.** Su consumidor es el proxy y su
  consecuencia **sí es de rotación**: retirar del *pool* un backend que no puede atender.
  Aquí `/ready` es la pregunta correcta, y Traefik es su consumidor natural.
- **`depends_on` no cambia.** Ya espera a `postgres` y `minio` con `service_healthy`.

**Traefik necesita además una regla nueva**, sin la cual `/ready` no existe desde fuera:
hoy `routes.yml` enruta al backend `/health`, `/api/`, `/docs`, `/openapi.json` y
`/sitemap.xml` — **`/ready` no está**, y por eso cae en el *fallback* de la SPA.

**Nada de esto se toca hasta que la definición se apruebe.**

---

## 13. O-07 — Docker y Portainer

`Task/017` **no instala ninguna UI**: Portainer CE 2.39.5 ya está en el Compose desde
`Task/003`. Sus límites **no cambian**: solo local, en la red `blog-management`, fuera de
`/admin`, no productivo, y **privilegiado por `docker.sock`** (`local-environment.md` §2.1).

### 13.1 Lo que hay que demostrar

| # | Afirmación | Cómo se demuestra |
| --- | --- | --- |
| 1 | Los logs del backend van a `stdout`/`stderr` | Un único `StreamHandler(sys.stdout)`; **ya verificado** |
| 2 | Docker los captura | `docker compose logs backend` devuelve 2 272 líneas; **ya verificado** |
| 3 | Portainer puede mostrarlos | Vista *Logs* del contenedor `personal-blog-local-backend` |
| 4 | **El operador puede filtrar una petición por su `request_id`** | **Es lo que hoy NO se puede hacer** y el entregable central de O-07 |

### 13.2 Recorrido diagnóstico propuesto — 6 pasos

1. Ejecutar una petición contra el stack local.
2. **Copiar el `X-Request-ID` de la cabecera de respuesta** — hoy imposible: no existe.
3. Abrir Portainer (`https://127.0.0.1:9444`) → contenedor `…-backend` → *Logs*.
4. Buscar ese identificador en el filtro de texto.
5. Encontrar el **evento de la petición** con `method`, `path`, `status_code` y
   `duration_ms`, y cualquier error asociado.
6. Si fue una **escritura administrativa**, cruzarlo con
   `SELECT … FROM audit_events WHERE request_id = '<id>'`.

El paso 6 **ya funciona** (§11.3). Los pasos 2, 4 y 5 son lo que esta tarea construye.

---

## 14. Fronteras que no se cruzan

### 14.1 Nada de Grafana, Prometheus, Loki, Alloy, CloudWatch ni OpenTelemetry

**Ni local, ni de producción.** ADR-008 gobierna producción y está **Aceptada**; su
*Cumplimiento* prohíbe autohospedar Grafana, Prometheus o Loki sin un ADR que lo reemplace,
y sus *Consecuencias neutras* dicen literalmente: *«El entorno local no cambia. Docker,
Portainer y `Task/017` siguen igual: Alloy y Grafana Cloud son exclusivamente de
producción»*.

**Análisis de necesidad — resultado: ninguno hace falta.** Cada capacidad exigida se
satisface con lo que ya existe:

| Necesidad local | Se satisface con |
| --- | --- |
| Ver los logs | `stdout` + Docker + Portainer |
| Localizar una petición | Correlation ID + búsqueda de texto |
| Saber si el proceso vive | `/health` |
| Saber si las dependencias responden | `/ready` |
| Reconstruir qué hizo un administrador | `AuditEvent` + `request_id` |

### 14.2 Métricas y trazas — **fuera de alcance, con fuente**

| Elemento | Dentro | Fuente |
| --- | --- | --- |
| Endpoint de métricas Prometheus | **NO** | No aparece en **O-01…O-10**, ni en `STAGE-05`, ni en `api-contracts.md`. ADR-008 descarta el *stack* autohospedado |
| *Tracing* distribuido / OTLP | **NO** | Ningún documento vigente lo pide. Con **un** servicio y **un** proceso no hay traza distribuida que reconstruir; `Task/023` decidirá si Lambda cambia eso |
| `duration_ms` por petición | **SÍ** | Es un **campo de log**, no un sistema de métricas |

**`duration_ms` no introduce ningún umbral.** Los umbrales **U-1…U-9** son de `Task/016`,
ya Aprobada, y son de frontend. Esta tarea **mide y registra**; no evalúa contra un límite.

---

## 15. O-08 — política de privacidad y redacción

### 15.1 Matriz de clasificación — **propuesta**

| Campo / dato | Clasificación | Justificación |
| --- | --- | --- |
| `Authorization` | **Nunca loguear** | S-08 |
| `Cookie`, `Set-Cookie` | **Nunca loguear** | Transporta la sesión opaca: equivale a la credencial (`Task/011`) |
| Contraseña y `password_hash` | **Nunca loguear** | **A-01**: *«la contraseña nunca se almacena, se registra ni se devuelve»* |
| Identificador de sesión | **Nunca loguear** | Es la credencial |
| Claves `BLOG_STORAGE_ACCESS_KEY` / `SECRET_KEY` | **Nunca loguear** | S-08, S-10 |
| `DATABASE_URL` completa | **Nunca loguear** | S-08. Ya mitigado: `repr=False` y `database_url_safe` |
| **URL prefirmada completa** | **Nunca loguear** | La firma **es** la credencial: quien la lee accede al objeto |
| Token o secreto en cualquier forma | **Nunca loguear** | S-08 |
| **Cuerpo de petición** | **Nunca loguear por defecto** | Contiene contraseñas en `login` y Markdown completo en el CRUD |
| **Cuerpo de respuesta** | **Nunca loguear por defecto** | Puede contener `access_url` prefirmadas |
| **Correo intentado en un login fallido** | **Nunca loguear** | **A-13** lo prohíbe **ya en la auditoría**: *«sería recolectar datos personales de terceros»*. El log no puede ser más laxo que la auditoría |
| Traza de excepción | **Sanitizado** | Va al log, **nunca** a la respuesta (S-07). Debe pasar por el redactor |
| **Query string** | **Sanitizado** | **Medido: hoy entra tal cual.** Lista de permitidos de parámetros conocidos, o redacción por patrón |
| **Dirección del cliente** | **Sanitizado, y solo donde aporte** | Hoy se registra en **cada** línea. En local es la IP de Traefik (`172.22.0.4`), inútil para atribución; `trusted_proxy_hop_count = 0` ignora `X-Forwarded-For` a propósito |
| `User-Agent`, `Referer` | **No loguear** | No aportan al diagnóstico local y `Referer` puede llevar una URL sensible |
| `request_id` | **Loguear** | Es el propósito de la tarea |
| `method`, `path` (sin query) | **Loguear** | Núcleo del diagnóstico |
| `status_code`, `duration_ms` | **Loguear** | Núcleo del diagnóstico |
| `actor_id`, `entity_id` (UUID) | **Loguear si aporta** | Opacos y no enumerables |
| `error_code` | **Loguear** | Estable y público |

### 15.2 Qué se decide sobre cada elemento del encargo

| Elemento | Decisión | Fuente |
| --- | --- | --- |
| Query string | **No por defecto** | Medido como fuga real; el propio `pyproject.toml` ya advertía que un nombre de archivo en la URL *«acabaría en los logs de acceso»* |
| Cuerpo de petición / respuesta | **No** | S-08, A-01 |
| Dirección del cliente | **No en el evento de petición** | Hoy es la IP del proxy; `AuditEvent.ip_address` ya cubre la atribución administrativa |
| `User-Agent` / `Referer` | **No** | Sin valor diagnóstico local |
| `actor_id` / `entity_id` | **Sí**, cuando el evento los tenga | Opacos |
| Excepción y traza | **Sí, sanitizadas, solo en `ERROR`** | S-07 |

### 15.3 Mecanismo de redacción — cierra **R-36**

R-36 está **Abierto** con propietario `Task/017` y `Task/018`. Su causa medida: *«`context`
emite **todo** atributo propio del `LogRecord`»* — y la prueba viva es el `color_message`
de Uvicorn, con secuencias ANSI, llegando al JSON.

Propuesta, **con `stdlib` y sin dependencias**:

1. **Lista de claves sensibles** por nombre, insensible a mayúsculas.
2. **Patrones** para valores con forma de credencial: URL con `Signature=`/`X-Amz-`, DSN
   con contraseña, cadenas tipo *bearer*.
3. **Lista de atributos internos ignorados**, empezando por `color_message`.
4. Aplicación **en los tres sitios**: `message`, `context` y `exception`.
5. **Valor sustituido por un marcador fijo**, nunca truncado —un truncado filtra prefijo.

### 15.4 Pruebas de señuelo

Cada categoría prohibida se inyecta con un **valor único e improbable** y se comprueba que
**no aparece en ninguna línea de log**, incluidas las de error. La prueba busca el señuelo
en la **salida completa capturada**, no en un campo concreto: un señuelo que se filtre por
`message` en vez de por `context` debe fallar igual.

---

## 16. Niveles de log por tipo de resultado

| Situación | Nivel | Razón |
| --- | --- | --- |
| `2xx` | **INFO** | Operación normal |
| `2xx` de `/health` y `/ready` | **DEBUG** | 90,8 % del log medido; el éxito repetido no informa |
| `/ready` en `503` | **WARNING** | Un fallo de sonda **nunca** se silencia |
| `401`, `403` | **WARNING** | Seguridad: interesa el patrón |
| `404` | **INFO** | Esperado en una API pública; no es un defecto |
| `409` | **INFO** | Conflicto de estado legítimo |
| `422` | **INFO** | Validación: cliente mal formado, servidor correcto |
| `429` | **WARNING** | Señal de abuso |
| `413`, `415` | **INFO** | Rechazo correcto de una entrada inválida |
| `5xx` no controlado | **ERROR** con `exc_info` | Es un defecto |
| Excepción de base de datos | **ERROR** | Fallo de infraestructura |
| Excepción de almacenamiento | **ERROR** | Fallo de infraestructura |

**No todo `4xx` es `ERROR`.** Un `404` en una API pública es funcionamiento correcto.

**Doble registro de la misma excepción: prohibido salvo justificación.** Los manejadores de
`app/shared/errors/handlers.py` **ya registran** cada error con su `request_id`. El
middleware **no vuelve a registrar la excepción**: emite el evento de petición con
`status_code` y `duration_ms`, que es información distinta. La única excepción admisible es
un fallo **antes o después** de la cadena de manejadores, donde no hay nadie más que lo
registre.

---

## 17. Duración de las peticiones

| Aspecto | Propuesta |
| --- | --- |
| Reloj | **`time.perf_counter()`** — monotónico. **Nunca `datetime.now()`**: un ajuste de reloj o el horario de verano produciría duraciones negativas o disparatadas |
| Campo | `duration_ms` |
| Representación | **Número**, no cadena: un campo numérico es ordenable y agregable |
| Precisión | Milisegundos con **un decimal**. Las respuestas medidas van de 7 ms a 448 ms; el milisegundo entero perdería resolución en el extremo bajo |
| Umbral | **Ninguno.** `Task/016` es owner de **U-1…U-9** |

---

## 18. `AuditEvent` ≠ log de aplicación

La separación es conceptual y **no se relaja**:

| | `AuditEvent` | Log JSON |
| --- | --- | --- |
| Qué es | Registro **persistente e inmutable** de acciones administrativas | Diagnóstico **operacional y efímero** |
| Dónde vive | PostgreSQL, tabla `audit_events` | `stdout` → Docker → Portainer |
| Quién lo lee | El administrador, por el API | El operador, por Portainer |
| Qué lo une | **El mismo `request_id`** | |

Reglas explícitas: **ningún log va a `audit_events`**; **las lecturas no se auditan**
(`CONTENT_MODEL.md` §3.9); el catálogo de 15 acciones **no se amplía**; un evento de
auditoría **no sustituye** a una línea de log ni al revés.

---

## 19. Dependencias nuevas — **cero previstas**

| Candidata | Veredicto |
| --- | --- |
| `structlog` | **No.** `JsonLogFormatter` ya existe, funciona y está probado. `contextvars` cubre el contexto y es `stdlib`. Sustituirlo reescribiría código en verde para ganar API |
| `python-json-logger` | **No.** Duplicaría exactamente lo que `JsonLogFormatter` hace |
| OpenTelemetry SDK | **No.** Sin requisito canónico (§14.2), y **acoplaría** la aplicación a un ecosistema de telemetría contra el principio 9 y ADR-008 |
| `prometheus-client` | **No.** Métricas fuera de alcance (§14.2) |
| `asgi-correlation-id` | **No.** Un middleware de correlación son decenas de líneas de `stdlib`, y la política de validación es **propia** |

Criterios aplicados: problema real, capacidad de `stdlib`, peso, **impacto en Lambda**
(**P-07**), portabilidad (principio 9), mantenimiento y seguridad.

> **Resultado esperado: 0 dependencias nuevas.** Toda la tarea es `logging`, `contextvars`,
> `time`, `uuid` y `re` — biblioteca estándar — más SQLAlchemy y `ObjectStorage`, ya
> presentes.

---

## 20. TDD — matriz RED/GREEN

> **Obligatoria**: es tarea de **backend funcional**. `BACKEND_TESTING_STRATEGY.md`, con
> **B-1…B-12** de la DoD. La matriz se completa **antes** de escribir implementación; los
> tests se escriben primero y se conserva la evidencia de RED.

### 20.1 Correlation ID

| # | Caso | Resultado esperado | Capa |
| --- | --- | --- | --- |
| 1 | Petición sin cabecera | Se genera un ID y la respuesta lleva `X-Request-ID` | HTTP |
| 2 | Respuesta `2xx` | Lleva la cabecera | HTTP |
| 3 | Todos los logs de una petición | Llevan **el mismo** `request_id` | HTTP |
| 4 | Log de error | Lleva **el mismo** ID que la cabecera y que `error.request_id` | HTTP |
| 5 | `404` | Lleva ID en cabecera **y** en cuerpo | HTTP |
| 6 | `422` | Lleva ID en cabecera **y** en cuerpo | HTTP |
| 7 | `5xx` no controlado | Lleva ID en cabecera **y** en cuerpo | HTTP |
| 8 | `X-Request-ID` válido entrante | **Se reutiliza** tal cual | HTTP |
| 9 | Entrante con `\r\n` | **Se descarta**, se genera uno nuevo, **sin registrar el valor** | HTTP |
| 10 | Entrante de **65** caracteres | Se descarta (límite `VARCHAR(64)`) | HTTP |
| 11 | Entrante de **64** caracteres | **Se acepta** — límite exacto, no aproximado | HTTP |
| 12 | Entrante con caracteres fuera del alfabeto | Se descarta | HTTP |
| 13 | Entrante vacío | Se descarta | HTTP |
| **14** | **Dos cabeceras, ambas válidas** | **Se descartan LAS DOS**; el ID final **no es ninguna** de ellas | HTTP |
| **14b** | **Dos cabeceras, una válida y una inválida** | Se descartan **las dos**; el ID final **no es la válida** | HTTP |
| **14c** | **Tres o más cabeceras** | Se descartan todas y se genera uno nuevo | HTTP |
| **14d** | Cualquier descarte (casos 9–14c) | El log lleva `incoming_request_id_discarded = true` **y ningún valor rechazado** | HTTP |
| 15 | `/health` y `/ready` | **También** llevan ID | HTTP |
| 16 | Dos peticiones consecutivas | **IDs distintos** | HTTP |

### 20.2 Logs JSON

| # | Caso | Resultado esperado | Capa |
| --- | --- | --- | --- |
| 17 | Cada línea emitida | Es JSON **parseable de forma independiente** | Unitaria |
| 18 | `timestamp` | ISO 8601 **UTC** con `Z` | Unitaria |
| 19 | `level` | Presente y correcto | Unitaria |
| 20 | Evento de petición | `request_id`, `method`, `path`, `status_code`, `duration_ms` como **campos**, no dentro de `message` | HTTP |
| 21 | `duration_ms` | **Número** ≥ 0 | HTTP |
| 22 | Excepción | Estructurada en `exception`, no concatenada en `message` | Unitaria |
| 23 | `uvicorn.access` | **No** emite su línea para una petición ya cubierta | HTTP |
| 24 | `uvicorn.error` | **Sigue** emitiendo errores de servidor | HTTP |
| 25 | `color_message` | **No** aparece en el JSON | Unitaria |

### 20.3 Privacidad (O-08) — señuelos

| # | Caso | Resultado esperado | Capa |
| --- | --- | --- | --- |
| 26 | `Authorization` con señuelo | **No** aparece en ninguna línea | HTTP |
| 27 | `Cookie` con señuelo | **No** aparece | HTTP |
| 28 | `login` con contraseña señuelo | **No** aparece **ni en el fallo** | Integración |
| 29 | Correo intentado en `login` fallido | **No** aparece (A-13) | Integración |
| 30 | Cuerpo de petición señuelo | **No** aparece | HTTP |
| 31 | Query string con señuelo | **No** aparece | HTTP |
| 32 | Excepción con `DATABASE_URL` en el mensaje | Contraseña **redactada** | Unitaria |
| 33 | URL prefirmada completa en un contexto | **Redactada** | Unitaria |
| 34 | `extra` con clave `password`/`token`/`secret` | **Redactado** | Unitaria |
| 35 | Señuelo en la traza de un `500` | **No** aparece | HTTP |

### 20.4 `/health` — liveness

| # | Caso | Resultado esperado | Capa |
| --- | --- | --- | --- |
| 36 | Proceso vivo | `200` y cuerpo esperado | HTTP |
| 37 | **Base de datos inalcanzable** | **Sigue** `200` | Integración |
| 38 | **Almacenamiento inalcanzable** | **Sigue** `200` | Integración |
| 39 | Ninguna consulta emitida | Verificado por instrumentación del motor | Integración |

### 20.5 `/ready` — readiness

| # | Caso | Resultado esperado | Capa |
| --- | --- | --- | --- |
| 40 | DB y almacenamiento disponibles | `200` `{"status":"ready"}` | Integración |
| 41 | **Base de datos caída** | `503` `{"status":"not_ready"}` | Integración |
| 42 | **Almacenamiento caído** | `503` `{"status":"not_ready"}` | Integración |
| 43 | Ambos caídos | `503`, **sin colgarse** | Integración |
| 44 | Cuerpo del `503` | **Sin** DSN, host, bucket, credencial, excepción cruda ni traza | Integración |
| 45 | Efecto sobre la base | **Cero** filas creadas, modificadas o borradas | Integración |
| 46 | Efecto sobre el almacenamiento | **Cero** objetos creados, modificados o borrados | Integración |
| 47 | Fallo registrado | El log **sí** dice qué componente y por qué | Integración |
| 48 | Ruta | Fuera de `/api/v1` | HTTP |
| 49 | Métodos no permitidos | `405` | HTTP |

#### 20.5.1 Los cinco escenarios exigidos del almacenamiento — **criterio obligatorio**

Cada uno se prueba contra **MinIO real**. Son los casos que la estrategia anterior no podía
distinguir; **el 42b es el que cierra el blocker**.

| # | Escenario | Resultado exigido |
| --- | --- | --- |
| **42a** | **Endpoint caído** (puerto sin servicio) | **`503` `not_ready`** |
| **42b** | **Bucket inexistente**, endpoint y credenciales correctos | **`503` `not_ready`** — el caso que `existe()` resolvía como `ready` |
| **42c** | **Credenciales inválidas** | **`503` `not_ready`** |
| **42d** | **Bucket existente y vacío** | **`200` `ready`** |
| **42e** | **Bucket existente con objetos** | **`200` `ready`** — el objeto lo crea la *fixture*, **nunca la sonda** |

**Y en los cinco, sin excepción:**

| Invariante | Cómo se comprueba |
| --- | --- |
| **0 objetos creados** | Inventario del bucket **antes y después** de la sonda: idéntico |
| **0 objetos modificados** | Comparación de `ETag` y `LastModified` de cada clave preexistente |
| **0 objetos eliminados** | Recuento y conjunto de claves idénticos |

| # | Caso adicional | Resultado esperado | Capa |
| --- | --- | --- | --- |
| **42f** | Un `403` de la sonda **no** se confunde con `ready` | `503` | Integración |
| **42g** | El log del fallo registra el **código semántico** (`NoSuchBucket`, `InvalidAccessKeyId`) | Presente y distinguible por escenario | Integración |
| **42h** | El log del fallo **no** contiene la clave de acceso ni el secreto | Señuelo ausente en toda la salida | Integración |
| **42i** | La sonda **no enumera el bucket**: solo consulta bajo su prefijo | Verificado sobre un bucket con objetos fuera del prefijo | Integración |

### 20.6 `AuditEvent`

| # | Caso | Resultado esperado | Capa |
| --- | --- | --- | --- |
| 50 | Escritura administrativa **exitosa** | `audit_events.request_id` == `X-Request-ID` de la respuesta | Integración |
| 51 | El mismo ID en el log de esa petición | Coincide | Integración |
| 52 | `login` fallido | Mismo ID en cuerpo de error, log y `AuditEvent` | Integración |
| 53 | Lecturas | **Siguen sin auditarse**: recuento de filas idéntico antes y después | Integración |
| 54 | Inmutabilidad | Las guardas de `Task/008` siguen activas | Integración |
| 55 | DTO público de auditoría | **Sigue con 5 campos**, sin `request_id` | Integración |

### 20.7 Portainer / Docker — **validación integrada, no *unit test***

| # | Caso | Cómo |
| --- | --- | --- |
| 56 | El recorrido de 6 pasos es reproducible | Ejecución manual documentada con evidencia |
| 57 | Un ID copiado de una respuesta se **encuentra** en los logs del contenedor | `docker compose logs backend \| grep <id>` y filtro de Portainer |
| 58 | La escritura admin se cruza con su `AuditEvent` | `SELECT … WHERE request_id = '<id>'` |

> **No se escribe un *unit test* tautológico** del tipo «Portainer existe». La evidencia es
> el recorrido ejecutado sobre el stack real.

### 20.8 Integración necesaria

**PostgreSQL real** (`PERSONAL_BLOG_TEST_DATABASE_URL`) para auditoría y readiness de base;
**MinIO real** (`PERSONAL_BLOG_TEST_STORAGE_*`) para readiness de almacenamiento.
**Nunca SQLite como sustituto** (B-6).

---

## 21. Anti-tautología

Mutaciones controladas para demostrar que las pruebas **detectan** la rotura. Se ejecutan
**después** de GREEN, y cada una se **revierte byte a byte**.

| # | Mutación | Debe poner en rojo |
| --- | --- | --- |
| **A** | El middleware deja de adjuntar `request_id` al log | 3, 4, 20 |
| **B** | `AuditEvent` deja de guardar `request_id` (se pasa `None`) | 50, 52 |
| **C** | `/ready` deja de consultar el almacenamiento | 42, 42a–42e, 43 |
| **C2** | **La sonda vuelve a `existe(<clave>)`** en lugar de `ListObjectsV2` | **42b** — es la mutación que reproduce el blocker: si 42b no se pone en rojo, la prueba no protege contra el falso positivo del bucket |
| **C3** | La sonda trata el `403` de credenciales como `ready` | 42c, 42f |
| **D** | El redactor deja pasar una clave sensible | 32, 34 y el señuelo correspondiente |
| **E** | La validación de entrada acepta cualquier longitud | 10 |
| **E2** | Ante cabeceras repetidas se **toma la primera** en vez de descartarlas | 14, 14b |
| **F** | El evento de petición vuelve a poner los datos dentro de `message` | 20 |
| **G** | `duration_ms` pasa a `datetime.now()` | 21, bajo salto de reloj simulado |

Si una mutación **no** pone nada en rojo, la prueba correspondiente es tautológica y **se
corrige antes de cerrar la tarea**.

---

## 22. Cambios potenciales por repositorio

> **Previsión, no compromiso.** Ningún archivo se toca hasta que la definición se apruebe.

### `personal-blog-backend`

| Archivo | Acción prevista |
| --- | --- |
| `app/shared/logging/contexto.py` | **Crear** — `ContextVar` del `request_id` |
| `app/shared/logging/redaccion.py` | **Crear** — política de redacción (R-36) |
| `app/shared/logging/configuration.py` | **Modificar** — filtro de `request_id`, redactor, ignorar `color_message`, silenciar `uvicorn.access` |
| `app/shared/logging/middleware.py` | **Crear** — correlación y evento de petición |
| `app/shared/logging/__init__.py` | **Modificar** — exportaciones |
| `app/api/readiness.py` | **Crear** — `GET /ready` |
| `app/api/__init__.py` | **Modificar** — montar el router |
| `app/main.py` | **Modificar** — registrar el middleware |
| `app/shared/storage/contrato.py` | **Modificar** — añadir `comprobar_disponibilidad()` al puerto `ObjectStorage` (§12.2) |
| `app/shared/storage/s3_compatible.py` | **Modificar** — implementarla con `ListObjectsV2(Prefix, MaxKeys=1)` y su cliente de sonda con timeouts propios |
| `tests/contract/test_contrato_de_object_storage.py` | **Modificar** — el método nuevo entra en el contrato que **ambas** implementaciones deben satisfacer |
| `app/shared/configuration/settings.py` | **Modificar** si hacen falta timeouts de sonda |
| `.env.example` | **Modificar** — variables nuevas con valores ficticios |
| `tests/test_correlacion.py`, `test_logging_redaccion.py`, `test_readiness.py` | **Crear** |
| `tests/integration/test_readiness_dependencias.py`, `test_auditoria_correlacion.py` | **Crear** |
| `tests/test_logging.py`, `tests/test_health.py` | **Modificar** — casos nuevos, **sin relajar** los existentes |

### `personal-blog-infra`

| Archivo | Acción prevista |
| --- | --- |
| `docs/tasks/TASK-017-local-observability.md` | **Este archivo** |
| `docs/task-reports/TASK-017-report.md` | **Crear al implementar** |
| `docker/traefik/dynamic/routes.yml` | **Modificar** — añadir `/ready` y apuntar el `healthCheck` del servicio a `/ready` |
| `docker-compose.yml` | **Modificar solo si** la decisión §12.4 lo exige |
| `docs/runbooks/local-environment.md` | **Modificar** — sección de observabilidad con las 7 preguntas |
| `docs/architecture/api-contracts.md` | **Modificar** — §9 y §11: cerrar «cabecera concreta del correlation ID»; documentar `/ready` |
| `docs/architecture/non-functional-requirements.md` | **Modificar** — estado de O-01…O-04, O-07, O-08 |
| `docs/architecture/software-architecture.md` | **Modificar** — `/ready`, el middleware y §7: `ObjectStorage` pasa de **cinco** a **seis** operaciones (L220) |
| `docs/architecture/security-boundaries.md` | **Modificar** — cerrar «campos a redactar en los logs» |
| `docs/project-management/ROADMAP.md` | **Modificar** — estado y **corrección de la referencia O-09** (§6) |
| `docs/project-management/STATUS.md` | **Modificar** — estado, avance y **R-36** |
| `docs/stages/STAGE-05-quality-security.md` | **Modificar** — dos criterios de salida |

### `personal-blog-frontend`

**Ningún archivo.** Sin rama. Justificación medida en §4.3.

---

## 23. Baseline de validación — **medido** el 2026-09-06

| Comprobación | Comando | Resultado |
| --- | --- | --- |
| Lint | `ruff check .` | **All checks passed!** |
| Formato | `ruff format --check .` | **297 files already formatted** |
| Tipos | `mypy` | **Success: no issues found in 295 source files** |
| Suite **sin** integración | `pytest -W error -q` | **832 passed, 800 skipped** en 55,63 s |
| Suite **con** PostgreSQL y MinIO reales | `pytest -W error -q` con `PERSONAL_BLOG_TEST_*` | **1631 passed, 1 skipped** en 176,64 s |

> **Aviso sobre el baseline heredado.** El encargo cita *«1631 passed, 1 skipped»*. Esa
> cifra **solo se reproduce con las variables de integración definidas**. Sin ellas, 800
> pruebas se omiten con su motivo y el resultado es **832 passed / 800 skipped** — no es un
> fallo, es una suite distinta. La cifra se **midió**, no se heredó.

### 23.1 Resultado con integración real — **medido** el 2026-09-06

```text
1631 passed, 1 skipped in 176.64s (0:02:56)
```

**El único `skip` está justificado y es estructural:**
`tests/test_logging_utc.py:133` — *«`time.tzset` no existe en Windows»*.

**Cero fallos. Cero *warnings*.** La suite corre con `-W error`, así que cualquier
*warning* habría abortado la ejecución (DoD: *«cero warnings no documentados»*).

**Entorno de la medición:**

| Elemento | Valor |
| --- | --- |
| `PERSONAL_BLOG_TEST_DATABASE_URL` | `personal_blog_test` en `127.0.0.1:55432`, con la marca `personal-blog:test-database` **verificada** en el comentario de PostgreSQL |
| `PERSONAL_BLOG_TEST_STORAGE_ENDPOINT_URL` | `http://127.0.0.1:9000` (MinIO local) |
| Base de datos de desarrollo | **Intacta.** La guarda de la suite impide apuntar a `personal_blog` |

**Este es el baseline que `Task/017` debe conservar**: cualquier regresión sobre 1631/1 es
un defecto de la tarea.

### 23.2 `docker build` del backend

La DoD de backend exige que la imagen construya. Se verifica al implementar, no en la fase
de definición: el `Dockerfile` **no se ha tocado**.

---

## 24. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| ~~R-017-1~~ | ~~El healthcheck de Docker pasa a `/ready` y una dependencia caída **reinicia el backend en bucle**~~ | — | **RETIRADO (2026-09-06): la premisa era falsa.** Docker Compose **no** reinicia por `HEALTHCHECK` *unhealthy*; la política `restart` reacciona a la terminación del proceso. Ver la corrección de §12.4. Sustituido por **R-017-1b** |
| **R-017-1b** | Si el `HEALTHCHECK` de Docker pasara a `/ready`, una dependencia caída dejaría al backend *unhealthy* y **Traefik no arrancaría** (`depends_on: service_healthy`), además de confundir «proceso muerto» con «dependencia caída» en la única columna de salud que ven Docker y Portainer | **Alto** | Recomendación **C** (§12.4), justificada por **semántica y por el efecto real sobre `depends_on`**, no por reinicios |
| R-017-2 | `/ready` se cuelga por los **timeouts por defecto de botocore** | **Alto** — *probe cascade* | Presupuesto de readiness explícito y **reintentos desactivados**; valores verificados en la medición de §12.2 |
| R-017-3 | Silenciar `uvicorn.access` oculta también errores de servidor | Medio | Solo se silencia `uvicorn.access`; `uvicorn.error` intacto; caso 24 lo prueba |
| R-017-4 | Un `X-Request-ID` hostil **inyecta una línea de log falsa** | Medio | Alfabeto cerrado sin `\r\n`, límite 64, y **ningún valor descartado se registra** |
| **R-017-4b** | Una cabecera `X-Request-ID` **repetida** produce un ID **ambiguo** según qué componente la resuelva | Medio | **Descartar todas y regenerar** (§9.3); casos 14, 14b, 14c |
| R-017-5 | El redactor **rompe** un log útil por exceso de celo | Bajo | Marcador fijo, nunca truncado; pruebas de que lo permitido sí aparece |
| R-017-6 | Un ID > 64 caracteres **rompe la escritura de auditoría** | Medio | Límite alineado con `VARCHAR(64)`; casos 10 y 11 |
| R-017-7 | Añadir un log por petición **multiplica el ruido** ya medido (90,8 % sondas) | Medio | Sondas satisfactorias a `DEBUG` (§8.3) |
| ~~R-017-8~~ | ~~`existe()` no distingue «bucket ausente» de «clave ausente»~~ | — | **RESUELTO (2026-09-06)**: era el **blocker**, no un riesgo tolerable. `existe()` queda descartada; la sonda pasa a `ListObjectsV2` con prefijo, que sí distingue. Casos 42a–42e |
| **R-017-8b** | La sonda exige **`s3:ListBucket`**, un permiso que la aplicación hoy no necesita | Medio | Acotado con `Condition: s3:prefix` al prefijo de la sonda, que está vacío por diseño: **no concede enumerar los medios**. Consecuencia registrada para `Task/030` (§12.2) |
| R-017-9 | Tocar `routes.yml` afecta al enrutado del sitio | Bajo | Regla aditiva; se revalida el recorrido completo de `local-environment.md` §6.7 |

---

## 25. Bloqueos y decisiones abiertas

| # | Asunto | ¿Bloquea? |
| --- | --- | --- |
| 1 | **Cabecera concreta del correlation ID** | **No.** `api-contracts.md` §11 la deja explícitamente abierta **para `Task/017`**: decidirla es el encargo, no un bloqueo |
| 2 | **Referencia O-09 en `ROADMAP.md` L243** | **No.** Precisión documental; ambas invariantes se preservan (§6) |
| 3 | **Exponer `request_id` en el DTO de auditoría** | **No.** `Task/012.1` **Q-1** lo dejó como decisión del usuario; §11.5 recomienda **no** hacerlo ahora |
| 4 | **D-21 / ADR-009** (rendering ante *crawlers*) | **No.** Frontend y SEO; sin relación con observabilidad |
| 5 | **D-08** (acceso a medios públicos) | **No.** `Task/030` |
| 6 | **D-11, D-19, D-20** | **No.** Producción; fuera de alcance |
| 7 | Conteo de avance en `ROADMAP.md` §Cálculo dice *«9 / 41 = 22 %»* frente a **16 / 41** en `STATUS.md` | **No bloquea `Task/017`.** Ver §25.1 |
| 8 | `BLOG_ADMIN_ALLOWED_ORIGINS` **no está definida** en el Compose: un `POST` con `Origin` desde el navegador recibe `403` | **No bloquea la definición.** Observación de infraestructura local hallada al medir; **fuera del alcance** de `Task/017` (`Task/018` es owner de CORS y `Origin`). Se reporta al usuario |

**Ninguno impide implementar `Task/017`.**

### 25.1 *Drift* preexistente del `ROADMAP` — corrección, no trabajo funcional

**Hallazgo:** `ROADMAP.md` §*Cálculo del avance* afirma *«Actualmente: `9 / 41 = 22 %`»*.
`STATUS.md` registra **16 / 41 — 39 %** tras la aprobación de `Task/016`.

| Aspecto | Resolución |
| --- | --- |
| **Valor canónico vigente** | **`16 / 41 = 39 %`** |
| Origen | *Drift* **preexistente**: el bloque de cálculo dejó de actualizarse en aprobaciones anteriores. **No lo causó `Task/017`** |
| Quién lo corrige | **`Task/017`, durante la implementación**, porque la tarea **ya modifica `ROADMAP.md`** para su propio estado. Abrir una tarea de mantenimiento solo para una línea sería desproporcionado |
| **Cómo se contabiliza** | **NO cuenta como trabajo funcional de `Task/017`.** Se registra en el reporte como *«corrección de *drift* documental preexistente, descubierta durante la definición»*, separada de los entregables |
| Qué **no** se hace | **No** se crea una tarea de mantenimiento adicional. **No** se altera el avance real: `Task/017` sigue sin sumar hasta su aprobación |

### 25.2 Evento de auditoría creado durante la medición del *baseline*

Medir la trazabilidad extremo a extremo (§11.3) exigió una petición que **produjera** un
evento de auditoría real. Se eligió la operación auditada menos invasiva: un intento de
acceso fallido contra el correo señuelo
`baseline-task017-no-existe@example.invalid` —dominio `.invalid`, reservado por RFC 2606 y
por tanto **no resoluble**—.

| Hecho | Valor |
| --- | --- |
| Evento generado | **1** × `authentication.login_failed` |
| `request_id` | `89be982d-13ab-4bb8-bac8-092344a16f6e` |
| `actor_id` | `NULL` — ningún administrador existente fue afectado |
| Contenido tocado | **Ninguno** |

**Se conserva como hecho histórico de la medición.** No se borra: `AuditEvent` es
**inmutable** por diseño (invariantes 16 y 16b de `data-model.md`, guardas de `Task/008`), y
esta tarea **no relaja esa garantía ni siquiera para limpiar su propio rastro**. Tampoco se
crean eventos adicionales para «compensarlo»: escribir en el historial para maquillar el
historial sería exactamente lo que la auditoría existe para impedir.

---

## 26. Gobierno

| Campo | Valor |
| --- | --- |
| **Estado de `Task/017`** | **Aprobada** el 2026-09-06 por jeffersondavila |
| **Avance global** | **17 / 41 — 41 %** |
| **ETAPA 05** | **2 / 3 — 67 %** |
| **Criterion 12** | **C = 0** |
| **Pruebas de backend** | **1808** en verde, **1** omitida (`time.tzset` no existe en Windows), `-W error`, con PostgreSQL y MinIO reales |
| **Dependencias nuevas** | **0** |
| **Estado durable** | La rama actual, la ausencia de PR, la ausencia de *push* y la limpieza del árbol **no** son estado durable y **no se persisten** |

Las decisiones de esta ficha estuvieron en estado **`Propuesta — pendiente de aprobación`**
hasta la aprobación del usuario, y desde el 2026-09-06 quedan **Aceptadas y Vigentes**:

| Decisión | Estado |
| --- | --- |
| Cabecera del correlation ID: **`X-Request-ID`**, 8–64 caracteres de `[A-Za-z0-9_-]`, UUIDv4 al generar | **Vigente** — `api-contracts.md` §9.1 |
| Política de entrada *fail-safe*: **2 o más cabeceras ⇒ se descartan todas** | **Vigente** — `api-contracts.md` §9.2 |
| `request_id` **no** se expone en el DTO del historial de auditoría | **Vigente** — `api-contracts.md` §15.3 |
| `GET /ready` no nombra el componente que falló; el log sí, ya saneado | **Vigente** — `api-contracts.md` §2 |
| Sonda de almacenamiento por **`ListObjectsV2(Prefix, MaxKeys=1)`**; `existe()` descartada por falso positivo medido | **Vigente** — `software-architecture.md` |
| Presupuesto **total** de `/ready` (2.5 s) por debajo del `timeout` de Traefik (3 s), no un timeout por dependencia | **Vigente** |
| **Recomendación C**: Docker conserva `/health`; Traefik pasa a `/ready` | **Vigente** — `routes.yml`, runbook §6.9 |
| Mecanismo de redacción por **nombre de campo** y por **forma del valor**, incluida la cadena de excepciones | **Vigente** — `security-boundaries.md` |

---

## 27. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-06** |
| **Aprobado por** | **jeffersondavila** |
| **Expresión de aprobación** | `approved: Task/017-Observabilidad-Local` |

**Alcance de la aprobación, con precisión.** La sesión de implementación verificó **O-07 por
Docker** —los logs del backend son JSON y el correlation ID se localiza en ellos— pero **no
produjo la comprobación visual en la interfaz de Portainer**: no disponía de superficie de
navegador. Ese punto quedó registrado como bloqueo en el reporte §20 y **lo cubre la
aprobación del usuario**, que es quien tiene acceso a esa interfaz y a quien corresponde en
exclusiva aprobar (`PROJECT_INSTRUCTIONS.md` §9). **No se registra como evidencia generada
por el agente**, porque no lo fue.
