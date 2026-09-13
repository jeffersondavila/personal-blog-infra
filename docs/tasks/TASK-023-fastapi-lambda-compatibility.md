# TASK-023 — Compatibilidad FastAPI ↔ Lambda

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/023-Compatibilidad-FastAPI-Lambda` |
| **Nombre** | Compatibilidad FastAPI ↔ Lambda |
| **Etapa** | ETAPA 08 — Preparación Cloud + AWS Local Parity |
| **Estado** | **Aprobada** el 2026-09-13 |
| **Repositorios involucrados** | `personal-blog-backend` (propiedad funcional) · `personal-blog-infra` (documentación y gobierno). `personal-blog-frontend`: **solo lectura, sin rama** |
| **Dependencias** | `Task/022-Validacion-Local-Production-Like` — **Aprobada** el 2026-09-12 |
| **Rama** | `Task/023-Compatibilidad-FastAPI-Lambda` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | backend `e0e3c08479d850ae8c13ff5e4c76a6b76f8d17de` · infra `f8a64b4892461e8eddab95b3a562066bd6254cdd` |
| **Fecha de inicio** | 2026-09-13 |
| **Fecha de aprobación** | 2026-09-13 |
| **Última actualización** | 2026-09-13 |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

| # | Comprobación | Resultado |
| --- | --- | --- |
| 1 | `main == origin/main` | **Sí** en ambos repos. backend `e0e3c08…`; infra `f8a64b4…` |
| 2 | Working tree limpio antes de crear la rama | **Sí**, `git status --porcelain` vacío en ambos |
| 3 | Rama creada **desde `main`** | **Sí**, `git switch -c` desde `main` en ambos |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | **Sí** en ambos |

*Observado el 2026-09-13, antes de crear las ramas:* tras `git fetch --prune origin` no
había ninguna rama `Task/*` remota ni ningún pull request abierto en los tres
repositorios, y `main` y `dev` tenían contenido idéntico. Frontend en `main`
(`7dce98aff239d61ae3ae15213d9a3f5ebf0fb8ce`), sin rama y sin modificaciones. El estado
vivo de Git y GitHub **no se versiona como vigente**: se consulta en el momento
([WORKFLOW §6.1](../project-management/WORKFLOW.md)).

```powershell
git fetch --prune origin
git switch main
git pull --ff-only origin main
git status --porcelain                          # vacio
git rev-parse main; git rev-parse origin/main   # deben coincidir

git switch -c Task/023-Compatibilidad-FastAPI-Lambda

git rev-parse HEAD; git rev-parse main          # deben coincidir
```

---

## 1. Objetivo

Permitir que **la misma** aplicación FastAPI que hoy sirve uvicorn se ejecute bajo AWS
Lambda con eventos de **API Gateway HTTP API v2 (*payload format* 2.0)**, mediante un
adaptador **fino y removible**, sin alterar la ejecución local y sin que el código de
negocio conozca Lambda.

## 2. Contexto

Abre la **ETAPA 08**, que prepara la nube **sin crear cuentas ni recursos reales**. La
precede `Task/022`, que cerró la ETAPA 07 dejando el blog validado íntegramente en local.

El backend se diseñó desde `Task/005` con esta tarea a la vista: `app/main.py` ya documenta
que `create_app()` construye la aplicación y que «el adaptador será una capa fina que
envuelve **esta misma** instancia», y `app/shared/database/session.py` eligió motor
síncrono y creación perezosa razonando explícitamente sobre Lambda. Esta tarea recoge esa
preparación y la hace ejecutable.

La consumen `Task/024` (artefacto ZIP, que necesita un *handler* al que apuntar) y
`Task/025` (laboratorio local, que necesita algo que desplegar).

## 3. Dentro del alcance

- [x] Módulo `app/lambda_handler.py` con `crear_handler(aplicacion)` y el `handler`
      productivo de módulo.
- [x] Dependencia de ejecución `mangum==0.22.0`, con regeneración de ambos *locks*.
- [x] Decisión y verificación del modo de `lifespan` sobre la **versión fijada**.
- [x] Guarda permanente que obligue a revisar esa decisión si la aplicación adquiere
      *lifecycle* explícito.
- [x] Suite test-first de la matriz §7.2: contrato del evento v2, equivalencia con la
      ejecución ASGI local, modelo de error, cookies, `sourceIp`, hermeticidad.
- [x] Integración real contra PostgreSQL del **flujo administrativo completo** a través del
      *handler*: `login` → cookie → `me`.
- [x] Gobierno documental en infra: esta ficha, reporte, STATUS, ROADMAP, STAGE-08.

## 4. Fuera del alcance

| Elemento | Propietario |
| --- | --- |
| Artefacto ZIP, tamaño, *checksums* | `Task/024` |
| Terraform, Floci, Lambda emulada, `plan`/`apply`/`destroy`, matriz de paridad | `Task/025` |
| Runbooks de despliegue | `Task/026` |
| **Provisión y configuración de API Gateway**, incluido qué *stage* y qué *base path* tendrá producción | `Task/033` |
| Medición de arranque en frío (**P-07**) y límites de Lambda (**D-12**) | `Task/024`, `Task/032` |
| *Pooling* de conexiones y PgBouncer | `Task/029` |
| Rediseño del *rate limiting*, de `trusted_proxy_hop_count` o de la correlación | Ninguno: política vigente, no se toca |
| Cuentas, credenciales o recursos AWS reales | ETAPA 09 y 10 |
| Cambios en el frontend | No aplica: el contrato HTTP del producto no cambia |

**Precisión expresa sobre el *stage*.** Esta tarea **no decide** que producción use el
*stage* `$default`. Solo registra que un *stage* nombrado puede exigir tratamiento
explícito del *base path*, y **no introduce configuración nueva** para anticipar esa
decisión, que es de `Task/033`.

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Adaptador Lambda | backend | `app/lambda_handler.py` |
| Dependencia fijada | backend | `pyproject.toml` |
| *Locks* regenerados | backend | `requirements.lock`, `requirements-dev.lock` |
| Contrato del evento v2 y equivalencia | backend | `tests/contract/test_handler_lambda.py` |
| Guardas estructurales | backend | `tests/unit/test_guarda_del_adaptador_lambda.py` |
| Integración del flujo administrativo real | backend | `tests/integration/test_handler_lambda_sesion_administrativa.py` |
| Ficha | infra | `docs/tasks/TASK-023-fastapi-lambda-compatibility.md` |
| Reporte | infra | `docs/task-reports/TASK-023-report.md` |
| Estado y roadmap | infra | `STATUS.md`, `ROADMAP.md`, `STAGE-08-cloud-ready.md` |

## 6. Criterios de aceptación

1. Existe un módulo importable que expone un *callable* `(event, context)`.
2. Envuelve **la misma instancia** de FastAPI que ejecuta uvicorn: no hay una segunda
   aplicación, ni rutas, *middleware*, manejadores de error, configuración o *logging*
   duplicados.
3. Un evento HTTP API **v2** produce la respuesta correcta: `statusCode`, cuerpo JSON,
   cabeceras de seguridad de `Task/018` y `X-Request-ID`.
4. El modelo común de error del proyecto sobrevive al adaptador: `404` y `405` salen con
   la forma `{"error": {...}}`.
5. `Set-Cookie` sale por el array `cookies` del formato v2, **no** colapsado en `headers`,
   y la **sesión administrativa real** sobrevive a un ciclo completo a través del *handler*.
6. `requestContext.http.sourceIp` llega a `scope["client"]` y de ahí al código existente
   que consume `request.client.host`, **sin modificar** la política de confianza vigente.
7. La ejecución local no cambia: `uvicorn app.main:app` sigue siendo el punto de entrada y
   el `CMD` del Dockerfile no se toca.
8. El adaptador es **removible**: eliminar un archivo y una dependencia devuelve el backend
   a su estado previo.
9. La suite sigue siendo hermética: `test_la_collection_no_construye_la_aplicacion` en
   verde. **CERT-AUD-001 intacto.**
10. Ningún recurso AWS real, ninguna credencial AWS, ningún Terraform, ningún Floci.

## 7. TDD / Plan test-first

Tarea de **backend funcional**: cambia el camino de entrada HTTP. Sección obligatoria,
completada **antes** de escribir implementación
([`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md)).

### 7.1 Comportamientos a construir

- Un evento de API Gateway HTTP API v2 se traduce al *scope* ASGI que la aplicación actual
  ya sabe atender.
- La respuesta ASGI se traduce al formato de respuesta v2, incluido el array `cookies`.
- La aplicación servida por el adaptador es **la misma** que sirve uvicorn.
- El adaptador no introduce estado de negocio en memoria entre invocaciones (**P-06**) ni
  dependencia del código de negocio respecto de Lambda (**T-04**).

### 7.2 Matriz de casos

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| **L-01** | `import` del módulo del *handler* | — | Expone un *callable* que acepta `(event, context)` | unitario |
| **L-02** | `crear_handler(app)` | — | El *handler* envuelve **esa misma** instancia; el `handler` de módulo envuelve `app.main.app` | unitario |
| **L-03** | Evento v2 `GET /health` | — | `statusCode == 200` | contrato |
| **L-04** | Mismo evento vs. `TestClient` sobre la misma app | — | Cuerpo JSON **idéntico** por ambos caminos | contrato |
| **L-05** | Evento v2 `GET /health` | — | Cabeceras de `Task/018` presentes: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `Content-Security-Policy` | contrato |
| **L-06** | Evento v2 con y sin `X-Request-ID` entrante | — | La respuesta siempre trae `X-Request-ID`; si entra uno válido, se conserva | contrato |
| **L-07** | `rawQueryString` no vacío | — | Llega íntegro a `scope["query_string"]`; observable como `422` de validación en una ruta real con restricción de consulta | contrato |
| **L-08** | `requestContext.http.path` con segmento variable | — | Llega íntegro a `scope["path"]` | contrato |
| **L-09** | Evento v2 hacia una ruta inexistente | — | `statusCode == 404` | contrato |
| **L-10** | La respuesta de L-09 | — | Cuerpo con la forma `{"error": {"code", "message", ...}}` del proyecto | contrato |
| **L-11** | Evento v2 `POST /health` | — | `statusCode == 405` | contrato |
| **L-12** | Respuesta con dos `Set-Cookie` | — | Ambas en `cookies[]`; **ninguna** en `headers` | contrato |
| **L-13** | `cookies: ["a=1", "b=2"]` en el evento | — | Llegan como **una sola** cabecera `cookie` a la aplicación | contrato |
| **L-14** | `requestContext.http.sourceIp` | `trusted_proxy_hop_count = 0` | `scope["client"] == (sourceIp, 0)` y `direccion_del_cliente()` devuelve esa IP | contrato |
| **L-15** | La aplicación construida por `create_app()` | — | **No declara** manejadores de *lifespan*: la premisa de `lifespan="off"` sigue siendo cierta | unitario |
| **L-16** | Invocación del *handler* sin variables `AWS_*` ni red | — | Responde `200` igualmente | unitario |
| **L-17** | `pytest --collect-only` sobre la suite completa | — | `app.main` **no** está importado al terminar la *collection* | unitario |
| **L-18** | `login` → cookie → `me` a través del *handler* | PostgreSQL real | `200` con cookie en `cookies[]`; reutilizarla en `/me` devuelve `200` con el administrador | **integración** |

**L-18 es el caso que de verdad protege el producto.** Una mini aplicación artificial
demuestra la mecánica de `Set-Cookie`, pero el riesgo real es que la **sesión
administrativa** se rompa en silencio. Por eso el ciclo se ejercita contra el flujo
auténtico —`POST /api/v1/admin/auth/login` y `GET /api/v1/admin/auth/me`, rutas existentes
del contrato— sobre PostgreSQL real.

**Descartado con motivo:** un caso propio para `isBase64Encoded`. El backend no emite
respuestas binarias ni *streaming*; su única respuesta no-JSON es `/sitemap.xml` con
`application/xml`, que está en los tipos de texto por omisión del adaptador. Queda cubierto
dentro de L-04 sin inventar un caso que no corresponde al alcance.

### 7.3 Tests RED esperados

| Test | Capa | Motivo de fallo esperado |
| --- | --- | --- |
| `test_el_modulo_del_handler_expone_un_callable` | unitario | `ModuleNotFoundError: app.lambda_handler` |
| `test_el_handler_envuelve_la_misma_aplicacion` | unitario | `ModuleNotFoundError` |
| `test_un_evento_v2_de_health_responde_200` | contrato | `ModuleNotFoundError` |
| `test_el_cuerpo_es_identico_al_de_la_ejecucion_asgi_local` | contrato | `ModuleNotFoundError` |
| `test_la_respuesta_lambda_conserva_las_cabeceras_de_seguridad` | contrato | `ModuleNotFoundError` |
| `test_la_respuesta_lambda_siempre_trae_el_correlation_id` | contrato | `ModuleNotFoundError` |
| `test_la_query_string_del_evento_llega_a_la_aplicacion` | contrato | `ModuleNotFoundError` |
| `test_el_path_del_evento_llega_intacto_a_la_aplicacion` | contrato | `ModuleNotFoundError` |
| `test_una_ruta_inexistente_responde_404` | contrato | `ModuleNotFoundError` |
| `test_el_error_conserva_el_modelo_comun_del_proyecto` | contrato | `ModuleNotFoundError` |
| `test_un_metodo_no_permitido_responde_405` | contrato | `ModuleNotFoundError` |
| `test_las_cookies_salen_en_el_array_cookies_y_no_en_headers` | contrato | `ModuleNotFoundError` |
| `test_las_cookies_del_evento_llegan_como_una_sola_cabecera` | contrato | `ModuleNotFoundError` |
| `test_la_direccion_de_origen_sobrevive_al_adaptador` | contrato | `ModuleNotFoundError` |
| `test_la_aplicacion_no_declara_lifecycle_explicito` | unitario | Guarda de la decisión; nace **verde** y su valor es fallar en el futuro |
| `test_invocar_el_handler_no_exige_credenciales_aws` | unitario | `ModuleNotFoundError` |
| `test_la_sesion_administrativa_sobrevive_al_handler` | integración | `ModuleNotFoundError` |

> **Sobre el RED.** `ModuleNotFoundError` es el RED legítimo del **primer *slice***, no la
> acreditación de toda la matriz. Cada comportamiento posterior demuestra su propio RED
> cuando su aserción —no su import— es lo que falla. La evidencia real, comando y salida,
> va al reporte.
>
> **L-15 es la excepción declarada y el motivo se escribe aquí:** es una guarda, no un
> comportamiento nuevo. Nace en verde porque la premisa que protege ya es cierta hoy; su
> utilidad es ponerse en rojo el día que deje de serlo. Forzar un RED artificial no
> demostraría nada.

### 7.4 Integración necesaria

**PostgreSQL real** para L-18, y solo para L-18: es el único caso cuyo comportamiento
—autenticar, emitir una sesión opaca *server-side*, recuperarla en la petición siguiente—
no existe sin base de datos. Se respetan íntegras las guardas vigentes:

- `PERSONAL_BLOG_TEST_DATABASE_URL` **no definida** → `SKIP` con motivo.
- Definida → cualquier fallo es **`FAIL`**. Nunca se degrada un fallo a *skip*.
- Toda fixture nueva deriva de `destino_de_integracion_verificado` (**CERT-AUD-002**), que
  `tests/test_grafo_de_fixtures_de_integracion.py` comprueba recorriendo el grafo.

**MinIO no se necesita.** Ningún caso de la matriz ejercita almacenamiento de objetos.

### 7.5 Casos negativos y de seguridad

- Ruta inexistente (L-09) y método no permitido (L-11), con el modelo de error del proyecto
  (L-10): el adaptador no puede filtrar trazas ni cambiar la forma del error.
- Cabeceras de seguridad de `Task/018` presentes también por el camino Lambda (L-05): una
  respuesta que las pierda sería una regresión de seguridad silenciosa.
- `Set-Cookie` correctamente separado (L-12, L-18): colapsarlo rompería la sesión
  administrativa sin error visible.
- Dirección de origen preservada (L-14): perderla mandaría auditoría y límite de tasa a la
  partición compartida `unknown`.
- Hermeticidad (L-17): ninguna prueba nueva puede reabrir **CERT-AUD-001**.

### 7.6 Regresiones relevantes

| Prueba existente | Por qué importa aquí |
| --- | --- |
| `tests/test_hermeticidad.py::test_la_collection_no_construye_la_aplicacion` | **CERT-AUD-001.** Un `import` del *handler* a nivel de módulo en cualquier test lo pondría en rojo |
| `tests/test_hermeticidad.py::test_la_collection_no_consume_un_dotenv_del_directorio_de_trabajo` | El `.env` del desarrollador no puede entrar en la suite |
| `tests/test_grafo_de_fixtures_de_integracion.py` | **CERT-AUD-002.** Descubre los módulos del harness por directorio: la fixture nueva de L-18 entra en la comprobación por existir |
| Suite completa de `Task/018` (cabeceras, CORS, límite de subida) | El adaptador envuelve el mismo *stack*; ninguna debe cambiar |
| Suite completa de `Task/011` y `Task/012` | La sesión administrativa y la API admin no cambian de contrato |

## 8. Plan de validación

| Criterio | Cómo se comprueba |
| --- | --- |
| 1, 2 | L-01, L-02 |
| 3 | L-03, L-04, L-05, L-06 |
| 4 | L-09, L-10, L-11 |
| 5 | L-12, L-13, **L-18** |
| 6 | L-14 |
| 7 | `git diff` sobre `Dockerfile` y `app/main.py` vacío en lo que respecta al `CMD` y al entrypoint; arranque de uvicorn |
| 8 | El adaptador vive en un archivo y una línea de `pyproject.toml`; `app/` no importa `mangum` en ningún otro sitio |
| 9 | L-17 y la suite completa |
| 10 | L-16; ausencia de Terraform, Floci, AWS CLI y credenciales en el diff |

## 9. Comandos de validación

```bash
# Gates canónicos del backend (CONTRIBUTING.md seccion 5)
ruff format --check .
ruff check .
mypy .
pytest -W error

# Locks: regeneracion canonica y comprobacion de desfase
sh scripts/generar-locks.sh
git diff --stat -- requirements.lock requirements-dev.lock
pip check

# S-09: auditoria de dependencias con la version canonica de la CI
uv tool run --from "pip-audit==2.10.1" pip-audit --strict --requirement requirements.lock
uv tool run --from "pip-audit==2.10.1" pip-audit --strict --requirement requirements-dev.lock

# Integracion real (L-18) y migraciones
$env:PERSONAL_BLOG_TEST_DATABASE_URL = "<url de la base _test>"
pytest -W error -m integration

# El entrypoint local no cambia
docker build -t personal-blog-backend:task023 .
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## 10. Evidencia esperada

- Salida real de RED y GREEN por *slice*, con su comando.
- Verificación reproducible de la semántica de `lifespan` sobre la **rueda fijada** de
  `mangum==0.22.0`, con su `sha256` comprobado contra PyPI.
- `git diff` de ambos *locks*, con el recuento exacto de distribuciones nuevas.
- Salida de `pip-audit --strict` sobre los dos *locks*.
- Suite completa con `-W error`, incluidos *skips* con su motivo.
- Resultado de la integración L-18 contra PostgreSQL real.
- `git status` y archivos modificados por repositorio.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | La traducción de `Set-Cookie` rompe la sesión administrativa en silencio | **Alto**: el panel deja de entrar en producción sin error visible | L-12 y, sobre todo, **L-18** contra el flujo real |
| 2 | Se pierde `sourceIp` y todo cae en la partición `unknown` | **Alto**: auditoría inútil y límite de tasa sin particionar | L-14 |
| 3 | `lifespan` ejecutándose **por invocación** | Medio: coste por petición sin beneficio | `lifespan="off"` verificado sobre 0.22.0, con la guarda L-15 |
| 4 | Un *stage* nombrado de API Gateway añade prefijo al *path* | Medio, **diferido** | Se registra como restricción conocida; la decisión es de `Task/033`. No se añade configuración nueva |
| 5 | Reapertura de **CERT-AUD-001** por un *import* mal colocado | Alto: la suite volvería a depender del `.env` local | L-17, y el patrón de *import* dentro de fixture ya establecido |
| 6 | El *lock* arrastra cambios no explicados | Medio | Se compara el diff; si aparece algo no explicado, **se detiene** antes de aceptarlo |
| 7 | Madurez de la dependencia: versión reciente, mantenedor único | Bajo-medio | Versión exacta, *hashes* en el *lock*, superficie de uso de una sola clase, capa removible por diseño |

## 12. Decisiones técnicas

| Decisión | Alternativas consideradas | Justificación | ¿ADR? |
| --- | --- | --- | --- |
| **Adoptar `mangum==0.22.0`** como dependencia de **ejecución** | Adaptador propio; `aws-lambda-powertools`; `asgi-lambda` | Lo que habría que escribir no es lógica del proyecto sino fontanería de protocolo: traducción evento↔*scope*, cabeceras multivalor, `rawQueryString`, separación de `set-cookie` al array `cookies` de v2, decisión base64 por tipo MIME y el protocolo ASGI de *lifespan*. Un error sutil ahí rompe la sesión administrativa en silencio. Es Python puro (`py3-none-any`), trae `py.typed`, y su única dependencia declarada —`typing-extensions`— **ya está** en ambos *locks* | **No.** Autorizada como decisión técnica de `Task/023` |
| **`lifespan="off"`** | `"auto"` (valor por omisión); `"on"` | Verificado sobre la rueda fijada: `LifespanCycle` se instancia **dentro de `Mangum.__call__`**, es decir **una vez por invocación**; y `"auto"` solo degrada si la aplicación **no** implementa el protocolo, cosa que Starlette **sí** implementa. Como `create_app()` no declara ningún manejador de *lifespan*, `"auto"` pagaría un ciclo completo por petición a cambio de cero trabajo. `"auto"` tampoco es el modo seguro de cara al futuro: un *startup* que calentara un *pool* se ejecutaría y destruiría en **cada** petición | No |
| **Guarda L-15** de la premisa anterior | Dejar la decisión sin proteger; comprobar con `grep` | La decisión se apoya en un hecho que puede dejar de ser cierto. La guarda es **semántica** —interroga el enrutador de la aplicación, no el texto del archivo ni detalles privados de Starlette— y falla el día que aparezca *lifecycle* explícito | No |
| **Fábrica `crear_handler(aplicacion)`** más el `handler` de módulo | Solo `handler = Mangum(app)` | Replica el patrón que `create_app(settings=…)` ya estableció para que las pruebas monten la aplicación con configuración propia. El comportamiento productivo es el `handler` de módulo, idéntico al que habría sin fábrica: **no se modifica producción para facilitar la suite** | No |
| **No fijar el *stage* de producción** | Decidir `$default` ahora | `Task/023` no es propietaria de la provisión de API Gateway. Se registra que un *stage* nombrado puede exigir tratamiento explícito del *base path*, sin introducir configuración para anticiparlo | No |

**Por qué ninguna exige ADR.** Ninguna modifica una decisión arquitectónica aceptada.
[ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md) ya decidió Lambda + API Gateway y
**previó expresamente** este adaptador —«el adaptador Lambda es una capa fina y removible
(`Task/023`)»—; [ADR-004](../adr/ADR-004-modular-monolith.md) y
[`software-architecture.md`](../architecture/software-architecture.md) dicen lo mismo.
Esta tarea **implementa** lo ya decidido. Lo que sí es nuevo —qué biblioteca y qué versión—
es una decisión técnica, y ningún documento vigente nombra a Mangum: la arquitectura
restringe la **forma** del adaptador, no la biblioteca.

## 13. Documentación creada o actualizada

- `docs/tasks/TASK-023-fastapi-lambda-compatibility.md` — ficha (nueva).
- `docs/task-reports/TASK-023-report.md` — reporte (nuevo).
- `docs/project-management/STATUS.md` — tarea y etapa en curso.
- `docs/project-management/ROADMAP.md` — estado de `Task/023` y de la ETAPA 08; corrección
  **D-023-1** en la columna *Repos* de la fila de `Task/023`.
- `docs/stages/STAGE-08-cloud-ready.md` — estado de la etapa y de `Task/023`; corrección
  **D-023-2** en su campo *Repositorio*.

## 14. Archivos modificados

**9** en backend (5 creados, 4 modificados) y **5** en infra (2 creados, 3 modificados).
**Ninguno** en frontend. Inventario completo en el
[reporte](../task-reports/TASK-023-report.md) §14.

Sin cambios, y eso forma parte del entregable: `app/main.py`, `Dockerfile`, el Compose
local y el workflow de CI.

## 15. Resultado de pruebas

| Prueba | Resultado |
| --- | --- |
| `ruff format --check .` | 322 archivos ya formateados |
| `ruff check .` | All checks passed |
| `mypy .` | Success, 320 archivos |
| `pytest -W error` con PostgreSQL y MinIO reales | **1918 passed, 1 skipped** |
| `pip-audit --strict` sobre ambos *locks* | No known vulnerabilities found |
| `docker build` + arranque de `uvicorn` | Imagen construida; `GET /health` → 200 |

La única omisión es la estructural de Windows (`time.tzset`), preexistente. Salidas
literales en el [reporte](../task-reports/TASK-023-report.md) §9.

## 16. Problemas encontrados

Cuatro hallazgos, detallados en el [reporte](../task-reports/TASK-023-report.md) §5 a §8:

| # | Hallazgo | Estado |
| --- | --- | --- |
| H-023-0 | La primera guarda de *lifespan* medía un detalle interno de FastAPI (`_merge_lifespan_context`) | **Resuelto** — sustituida por tres capas |
| H-023-1 | `DeprecationWarning` al construir el adaptador en Python 3.12 con `-W error` | **Resuelto** sin silenciar, con regresión permanente |
| H-023-2 | `mypy --strict` rechaza `ASGIApp` frente al protocolo del adaptador | **Resuelto** sin `type: ignore` |
| H-023-3 | Un fallo de un test de concurrencia **no reproducido** en 8 intentos posteriores | **Abierto, no diagnosticado.** No se declara resuelto ni descartado, y **no se atribuye al adaptador**. No existe defecto bloqueante demostrado atribuible a `Task/023`; se **vigilará en la CI del cierre** y, si se reproduce, el cierre **debe detenerse** |

## 17. Pasos de validación para el usuario

```powershell
cd personal-blog-backend
git switch Task/023-Compatibilidad-FastAPI-Lambda

ruff format --check .; ruff check .; mypy .
pytest -W error

# Integracion real (opcional, exige la base _test provisionada)
$env:PERSONAL_BLOG_TEST_DATABASE_URL = "<url de la base _test>"
pytest -W error -m integration

# La ejecucion local no cambia
uvicorn app.main:app --host 127.0.0.1 --port 8000
# y en otra terminal:
curl http://127.0.0.1:8000/health
```

## 18. Deuda técnica pendiente

| Elemento | Destino |
| --- | --- |
| Tratamiento del *base path* si producción usa un *stage* nombrado | `Task/033` |
| Medición de arranque en frío y tamaño del artefacto (**P-07**) | `Task/024`, `Task/032` |
| **Observación heredada:** la fila de `Task/024` en ROADMAP y su campo *Repositorio* en STAGE-08 arrastran la misma omisión que **D-023-1/D-023-2**. **No se corrige aquí** y `Task/023` **no audita** `Task/024` | Preflight de `Task/024` |
| **H-023-3**, observación abierta **no diagnosticada**: vigilar `test_dos_publicaciones_simultaneas_solo_prosperan_una` en la CI. Si se reproduce, **detener el cierre** y analizarlo | CI del cierre de `Task/023` |

## 19. Próxima tarea

`Task/024-Artefacto-ZIP-Lambda` — paquete ZIP reproducible para Linux, validación de tamaño
frente a los límites de Lambda y *checksums*. Depende de esta tarea.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-13** |
| **Aprobado por** | **El usuario** (`jeffersondavila`) |
| **Expresión de aprobación** | `approved: Task/023-Compatibilidad-FastAPI-Lambda` |

> Esta sección solo se completa cuando el usuario autoriza explícitamente la aprobación.
> Claude nunca la completa por iniciativa propia.

Con esta aprobación `Task/023` **cuenta en las 41 tareas**: el avance pasa de **22/41 ≈ 54 %**
a **23/41 ≈ 56 %**, y la **ETAPA 08** queda **En progreso** con **1 de 4 tareas aprobadas**
(25 %). **La etapa no se completa aquí:** `Task/024`, `Task/025` y `Task/026` siguen
**Pendientes**, y `Task/024` **no se inicia** en este cierre.

**T-04** pasa de *Satisfecho técnicamente* a **Satisfecho y Vigente**. **P-06** queda
**Revalidado / Conservado** —la base es de `Task/005`, esta tarea no la inventa—. **P-07**
**no se toca**: es de `Task/024` y `Task/032`.

**H-023-3 sigue ABIERTO y NO DIAGNOSTICADO.** La aprobación de la tarea **no lo convierte
en resuelto**: no se reprodujo en los ocho intentos locales posteriores, pero tampoco se
explicó. Debe vigilarse expresamente en la CI remota del cierre y, si reaparece, **el cierre
se detiene** y se analiza antes de publicar ningún pull request.
