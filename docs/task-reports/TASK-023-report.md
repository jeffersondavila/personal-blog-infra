# TASK-023 — Reporte de tarea

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/023-Compatibilidad-FastAPI-Lambda` |
| **Etapa** | ETAPA 08 — Preparación Cloud + AWS Local Parity |
| **Estado** | **Aprobada** el 2026-09-13 mediante `approved: Task/023-Compatibilidad-FastAPI-Lambda` |
| **Fecha** | 2026-09-13 |
| **Ficha** | [TASK-023-fastapi-lambda-compatibility.md](../tasks/TASK-023-fastapi-lambda-compatibility.md) |
| **Repositorios modificados** | `personal-blog-backend`, `personal-blog-infra` |
| **Frontend** | **Sin cambios.** Solo lectura, sin rama |

---

## 1. Ramas y SHA base

*Observado el 2026-09-13, tras `git fetch --prune origin`:*

| Repo | Rama | Base | SHA base | `HEAD == main` |
| --- | --- | --- | --- | --- |
| backend | `Task/023-Compatibilidad-FastAPI-Lambda` | **`main`** | `e0e3c08479d850ae8c13ff5e4c76a6b76f8d17de` | **Sí** |
| infra | `Task/023-Compatibilidad-FastAPI-Lambda` | **`main`** | `f8a64b4892461e8eddab95b3a562066bd6254cdd` | **Sí** |
| frontend | *ninguna* | — | `7dce98aff239d61ae3ae15213d9a3f5ebf0fb8ce` (en `main`) | — |

Antes de crear cada rama: `main == origin/main` y `git status --porcelain` vacío en ambos
repositorios. Ninguna rama nació de `dev`. En ese momento no existía ninguna rama `Task/*`
remota ni ningún pull request abierto, y `main` y `dev` tenían contenido idéntico en los
tres repositorios.

## 2. Verificación de la semántica de `lifespan` sobre la versión **fijada**

No se dio por buena la inspección de la rama `main` del preflight. Se descargó la
distribución exacta y se **comprobó su digest contra PyPI** antes de leer una sola línea:

```
mangum-0.22.0-py3-none-any.whl: OK
sha256 a0595e3cc7a8091b22d8b3997bab5b2ad6aae7a5e40865e19c2015f5c959a93b
```

Ese digest es **el mismo** que uv escribió después en ambos *locks*. Lo leído en
`mangum/adapter.py` y `mangum/protocols/lifespan.py` de **0.22.0**:

| Pregunta | Respuesta verificada |
| --- | --- |
| Modos disponibles | `"auto"` (por omisión), `"on"`, `"off"`. Otro valor → `ConfigurationError` |
| Cuándo se ejecuta `LifespanCycle` | Se instancia y se entra **dentro de `Mangum.__call__`** |
| ¿Por invocación? | **Sí.** Arranque en `__enter__` y apagado en `__exit__`, dentro del `ExitStack` de cada llamada |
| Comportamiento real de `"auto"` | Solo degrada a `UNSUPPORTED` si la aplicación **envía un mensaje antes** de recibir el arranque. Starlette implementa el protocolo, así que **no degrada**: ejecuta el ciclo completo |
| Comportamiento real de `"off"` | No se crea `LifespanCycle` y **no se añade `state` al *scope*** |

**El preflight queda confirmado, no contradicho**, así que se usó `lifespan="off"` según lo
autorizado. Como la premisa —que la aplicación no declara ciclo de vida— puede caducar,
queda protegida por tres capas independientes en
`tests/unit/test_guarda_del_adaptador_lambda.py`.

**Corrección factual al preflight.** El preflight afirmaba que `rawPath` llega a
`scope["path"]`. Leído el código de 0.22.0, para *payload* 2.0 el adaptador toma el camino
de **`requestContext.http.path`**; `rawQueryString` sí es la fuente de
`scope["query_string"]`. Los eventos de prueba llevan ambos campos coherentes y las
aserciones se escribieron sobre el comportamiento real.

## 3. Matriz test-first y su resultado

| Caso | Comportamiento | Capa | Resultado |
| --- | --- | --- | --- |
| L-01 | *Handler* importable y *callable* | unitario | ✔ |
| L-02 | Envuelve la misma aplicación (y el de módulo, la de `uvicorn`) | unitario | ✔ |
| L-03 | Evento v2 `GET /health` → `200` | contrato | ✔ |
| L-04 | Cuerpo idéntico al de la ejecución ASGI local | contrato | ✔ |
| L-05 | Las **cinco** cabeceras de seguridad de `Task/018` | contrato | ✔ |
| L-06 | `X-Request-ID` siempre presente; el entrante se conserva | contrato | ✔ |
| L-07 | `rawQueryString` llega (observable como `422`) y sin alterar al *scope* | contrato | ✔ |
| L-08 | *Path* íntegro, incluido el segmento variable; método y versión HTTP | contrato | ✔ |
| L-09 | Ruta inexistente → `404` | contrato | ✔ |
| L-10 | Modelo común de error, con `request_id` igual al de la cabecera | contrato | ✔ |
| L-11 | Método no permitido → `405` | contrato | ✔ |
| L-12 | `Set-Cookie` en `cookies[]` y **no** en `headers` | contrato | ✔ |
| L-13 | `cookies[]` entrante → **una sola** cabecera `cookie` | contrato | ✔ |
| L-14 | `sourceIp` → `scope["client"]` → `direccion_del_cliente()` | contrato | ✔ |
| L-15 | Guarda de la premisa de `lifespan` (tres capas) | unitario | ✔ |
| L-16 | Sin credenciales AWS ni red | unitario | ✔ |
| L-17 | `CERT-AUD-001` intacto | unitario | ✔ |
| **L-18** | **Sesión administrativa real a través del *handler*** | **integración** | ✔ |

Añadido durante la ejecución, no previsto en la matriz:

| Caso | Comportamiento | Capa | Motivo |
| --- | --- | --- | --- |
| **L-19** | Importar el *handler* con `-W error` no emite ningún aviso | unitario | Regresión de **H-023-1** (§6) |

**42 pruebas nuevas** en cuatro archivos: 25 de contrato, 11 unitarias, 6 de integración.
La suite pasó de **1876** a **1919** casos recolectados: 42 propias **más una generada
automáticamente**, porque `tests/test_grafo_de_fixtures_de_integracion.py` descubre los
módulos del harness por directorio y parametrizó la fixture nueva
`handler_administrativo` sin que nadie la enumerara. **`CERT-AUD-002` cubrió el módulo
nuevo por el hecho de existir**, que es exactamente su diseño.

## 4. RED

**Primer *slice*** — ejecutado con el módulo del adaptador aún inexistente:

```
8 failed, 3 passed, 22 errors in 4.55s
ImportError: cannot import name 'lambda_handler' from 'app'
```

Tras rediseñar la guarda de *lifespan* (§5), el RED definitivo previo a la implementación:

```
7 failed, 5 passed, 6 skipped, 22 errors in 4.14s
```

Los **6 *skipped*** son L-18: `PERSONAL_BLOG_TEST_DATABASE_URL no definida: se omite la
integracion`. La guarda del harness funcionando antes de que existiera el código.

**`ImportError` fue el RED del primer *slice*, no la acreditación de la matriz.** Se
declara con precisión qué demostró cada cual:

| Origen del RED | Casos |
| --- | --- |
| Ausencia del módulo (RED del *slice* inicial) | L-01…L-14, L-16 |
| **Fallo específico de comportamiento** | **L-15** (§5) y **L-19** (§6), ambos descubiertos ejecutando, no previstos |
| Guarda que nace en verde, declarado en la ficha | Las otras dos capas de L-15 |
| Guarda preexistente que debía seguir verde | L-17 |

No existe una implementación intermedia que hubiera puesto L-03…L-14 en rojo por una razón
distinta sin fabricarla: el comportamiento que especifican lo entrega íntegro el adaptador
bajo prueba. Se registra así en lugar de presentar diecisiete REDs equivalentes como si
fueran independientes.

## 5. Hallazgo H-023-0 — la primera guarda de *lifespan* medía lo que no debía

Escrita como *«la aplicación conserva el `lifespan_context` por omisión»*, comparando
contra una `FastAPI()` recién construida. **Falló, y el fallo fue útil:**

```
AssertionError: assert <class 'function'> is <class 'fastapi.routing._DefaultLifespan'>
  where <function _merge_lifespan_context.<locals>.merged_lifespan>
      = <AplicacionSegura>.router.lifespan_context
```

`include_router()` **envuelve** el contexto con `_merge_lifespan_context`, así que ninguna
aplicación que monte routers conserva el de omisión, hagan o no algo. La comprobación medía
un detalle interno de FastAPI, no la premisa de la decisión: exactamente la prueba frágil
que la autorización pedía evitar. Se sustituyó por tres capas:

1. **Superficie pública de registro:** `router.on_startup` y `router.on_shutdown` vacíos.
2. **Semántica en ejecución:** se recorre el protocolo ASGI de `lifespan` tal como lo
   define la especificación y se comprueba que los mensajes son exactamente
   `lifespan.startup.complete` y `lifespan.shutdown.complete` y que el `state` queda
   **vacío** —el canal por el que un ciclo de vida publicaría recursos—.
3. **Declaración en el código propio:** se recorre el árbol sintáctico de `app/` con `ast`
   buscando `lifespan=`, `on_startup=`, `on_shutdown=` y `on_event`. Cubre el hueco de las
   otras dos: un arranque que guardase su recurso en una variable de módulo no dejaría
   rastro observable.

Ninguna depende de un nombre privado de Starlette o de FastAPI. **Limitación declarada:** la
capa 3 mira nuestro código, no el de terceros; la garantía es sobre el ciclo de vida que
declara este proyecto.

## 6. Hallazgo H-023-1 — `DeprecationWarning` al construir el adaptador

Descubierto al pasar a GREEN, con la suite en `-W error`:

```
DeprecationWarning: There is no current event loop
  app/lambda_handler.py -> Mangum(...) -> mangum/adapter.py:65 _setup_event_loop
```

**Causa.** `Mangum.__init__` llama a `asyncio.get_event_loop()` y captura `RuntimeError`
para crear un bucle si no hay. Es correcto en Python **3.14**, donde esa llamada lanza. En
Python **3.12** —la versión que fija el proyecto— **no lanza**: emite el aviso, devuelve un
bucle nuevo y el `except` nunca se ejecuta. Comprobado de forma aislada:

```
python -W error -c "import asyncio; asyncio.get_event_loop()"
-> DeprecationWarning: There is no current event loop
```

**Qué NO se hizo.** No se silenció: el proyecto ya rechazó esa vía con `anyio`/`starlette`
en `Task/020` («el proyecto **no silencia la advertencia**»). No hay `filterwarnings`, ni
`# noqa`, ni versión corregida aguas arriba que adoptar.

**Qué se hizo.** Dejar de tomar el camino deprecado: el adaptador establece el bucle del
proceso **una sola vez**, al importarse, y solo si no hay ya uno en marcha. Se midieron dos
alternativas antes de elegir:

| Alternativa | Aviso | Bucles creados en 3 construcciones |
| --- | --- | --- |
| Forzar la rama `RuntimeError` con `set_event_loop(None)` | No | **3** — un bucle sin cerrar por construcción |
| **Establecer el bucle del proceso** | No | **1** |

Un único bucle por proceso es además el modelo correcto bajo Lambda: vive lo que viva el
entorno de ejecución. Regresión permanente en
`tests/unit/test_arranque_del_handler_lambda.py`, que mide el *import* en un **subproceso
limpio** con `-W error` y trae su propia guarda anti-tautología para demostrar que ese
subproceso escala los avisos de verdad.

## 7. Hallazgo H-023-2 — `mypy --strict` y el tipo del parámetro

`crear_handler` se anotó al principio con `ASGIApp` de Starlette. `mypy --strict` lo
rechazó: `ASGIApp` declara que `__call__` devuelve `Awaitable[None]`, más ancho que el
`Coroutine[Any, Any, None]` que exige el protocolo del adaptador, así que no es asignable.
Se corrigió declarando el tipo real del adaptador **en vez de añadir un `type: ignore`**,
que solo habría tapado una diferencia real.

## 8. Hallazgo H-023-3 — un fallo de concurrencia **no reproducido**

Se reporta tal cual se observó, sin diagnóstico.

*Observado el 2026-09-13:* una ejecución completa de la suite terminó
`1 failed, 1794 passed, 124 skipped in 584.92s`, con
`tests/integration/test_concurrencia_administrativa.py::test_dos_publicaciones_simultaneas_solo_prosperan_una`
en rojo. **No se conservó su traza**, así que no se afirma la causa.

Intentos posteriores de reproducirlo:

| Ejecución | Resultado |
| --- | --- |
| El test aislado, 1 vez | 1 passed |
| El test aislado, 5 veces seguidas | 5/5 passed |
| Solo `tests/integration/` | 770 passed, 87 skipped |
| Suite completa, segunda vez | 1795 passed, 124 skipped en **332,96 s** |
| Suite completa, final con PostgreSQL **y** MinIO | **1918 passed, 1 skipped** |

Lo que sí puede afirmarse, separando el hecho de la interpretación:

| Afirmación | Naturaleza |
| --- | --- |
| Es un test de **carrera entre dos hilos**, con `threading.Barrier(2)` a 10 s y `join(timeout=30)`: sensible al tiempo **por construcción** | **Hecho**, leído en el código del test |
| La ejecución que falló tardó un **76 % más** que la siguiente (584,92 s frente a 332,96 s) | **Hecho medido** |
| El adaptador Lambda **no participa en el camino de código** de este test: construye la aplicación con `create_app` y la conduce con `TestClient` | **Hecho**, leído en el código |
| El comportamiento es **consistente con** contención de recursos durante esa ejecución | **Interpretación.** La diferencia temporal **no demuestra la causa**: es compatible con ella, no prueba de ella |

**H-023-3 no está diagnosticado.** No se declara resuelto, no se declara descartado y **no
se atribuye al adaptador Lambda**. Queda como observación abierta, para **vigilarla en la CI
remota del cierre**. Si la CI lo reproduce, **el cierre debe detenerse y analizarse** antes
de continuar.

## 9. Resultado de las validaciones

| Prueba | Comando | Resultado |
| --- | --- | --- |
| Formato | `ruff format --check .` | **322 files already formatted** |
| Lint | `ruff check .` | **All checks passed!** |
| Tipos | `mypy .` | **Success: no issues found in 320 source files** |
| Suite completa | `pytest -W error` con PostgreSQL **y** MinIO reales | **1918 passed, 1 skipped** en 383,64 s |
| Integración L-18 | `pytest -W error tests/integration/test_handler_lambda_sesion_administrativa.py` | **6 passed** contra PostgreSQL real |
| Dependencias | `pip check` | **No broken requirements found** |
| **S-09** ejecución | `pip-audit --strict --requirement requirements.lock` | **No known vulnerabilities found**, exit 0 |
| **S-09** desarrollo | `pip-audit --strict --requirement requirements-dev.lock` | **No known vulnerabilities found**, exit 0 |
| Reproducibilidad de *locks* | `sh scripts/generar-locks.sh` dos veces | Archivos **idénticos** |
| Imagen | `docker build -t personal-blog-backend:task023 .` | **Construida**, con `--require-hashes` sobre el lock nuevo |
| Entrypoint local | `uvicorn` en el contenedor | PID 1 = `uvicorn app.main:app …`; `GET /health` → **HTTP 200** |
| *Handler* en Linux | `python -W error -c "…handler(evento, None)"` en la imagen | `statusCode: 200`, cuerpo correcto, `isBase64Encoded: False`, `X-Request-ID` presente, **sin avisos** |
| Secretos | Búsqueda sobre los archivos nuevos | **Ninguno** |

**La única omisión de la suite** es `tests/test_logging_utc.py:133 — time.tzset no existe en
Windows`, estructural y preexistente. Es el mismo perfil que el baseline de `Task/022`
(*Windows: 1875 passed, 1 skipped*).

**Limitación del entorno, declarada.** `pip-audit` **no puede ejecutarse sobre Windows**
contra estos *locks*: están resueltos para Linux x86_64 y `uvloop` no publica ninguna
distribución de Windows (README §5.1). Se ejecutó donde el gate es válido —un contenedor
`python:3.12.14-slim` fijado por el mismo digest que usa el `Dockerfile`, con
`pip-audit==2.10.1`, la versión canónica de la CI—. El gate **no se relajó ni se omitió**.

## 10. Dependencia y *locks*

`mangum==0.22.0` añadida a `[project].dependencies` —**ejecución**, no desarrollo: viaja al
artefacto de `Task/024`—.

| Comprobación | Resultado |
| --- | --- |
| Herramienta de generación | `uv 0.12.12`, la versión que exige la CI, descargada y **verificada por digest** (`3d5491…`) |
| `--exclude-newer` | **`2026-09-10T00:00:00Z`, sin tocar.** Mangum 0.22.0 se publicó el 2026-08-22, anterior a esa foto |
| Distribuciones nuevas | **Una sola**: `mangum==0.22.0`, con sus dos *hashes* |
| Transitivas nuevas | **Ninguna.** `typing-extensions==4.16.0` ya estaba; solo gana un consumidor |
| Cambios de versión de cualquier otro paquete | **Ninguno** |
| Diff total | `+5 / -0` en cada *lock* |

Los dos *hashes* que uv escribió coinciden exactamente con los verificados contra PyPI
antes de empezar. **No hubo ningún cambio inexplicado que obligara a detenerse.**

## 11. Impacto en la CI

**El workflow no se modifica.** Ninguna necesidad real lo justifica:

- El paso de desfase de *locks* los regenera y compara; ya se comprobó que la regeneración
  es reproducible.
- `pip-audit --strict` cubre la dependencia nueva por estar en los *locks*.
- El gate Trivy de la imagen se ejecutará sobre la imagen que ya incorpora el paquete.

**No se hizo `push`**, de modo que **no se ha provocado ninguna ejecución remota**. Los
resultados de la CI son, por tanto, **no verificados** hasta que el usuario apruebe y la
rama se publique.

## 12. NFR

| Requisito | Estado | Fundamento |
| --- | --- | --- |
| **T-04** — Backend independiente de Lambda: adaptador fino y removible | **Satisfecho técnicamente**, pendiente de la aprobación de `Task/023` para quedar vigente | El adaptador es **un archivo y una línea de `pyproject.toml`**. `app/main.py`, el `Dockerfile` y el Compose no cambian: su diff es **vacío**. Dos guardas ejecutables recorren `app/` con `ast` y fallan si `mangum` aparece en cualquier otro módulo o si el adaptador deja de vivir en uno solo |
| **P-06** — Backend stateless | **Revalidado / conservado** | `Task/005` estableció la base y esta tarea **no la inventa**: no añade estado de negocio en memoria. Lo único que persiste entre invocaciones es el bucle de eventos, una caché técnica recreable del mismo tipo que el `lru_cache` de `get_settings` |
| **P-07** — Compatible con *cold starts* | **No tocado** | Es de `Task/024` y `Task/032`. No se midió arranque en frío ni se usó ninguna medición local como autoridad |

## 13. Criterion12 — barrido C/D del alcance de `Task/023`

Sobre **todo** lo que esta tarea creó o modificó:

- **C = 0.** Ningún documento afirma estado vivo de Git o GitHub como vigente. Las dos
  referencias a ese estado son **observaciones fechadas** (§1 de este reporte y §0 de la
  ficha), redactadas como registro y acompañadas de la remisión a WORKFLOW §6.1. No se
  escribe que exista un PR, ni una rama remota, ni un SHA «actual».
- **D = 0** dentro del alcance. Las dos contradicciones heredadas que la autorización
  permitía corregir quedaron corregidas **solo en las entradas de `Task/023`**:
  - **D-023-1** — ROADMAP: la columna *Repos* pasa de `backend` a
    `backend, infra (documentación)`, con nota que explica el motivo y cita el precedente
    de `Task/019`, `Task/020` y `Task/022`.
  - **D-023-2** — STAGE-08: el campo *Repositorio* pasa a *Repositorios*, con el mismo
    criterio que STAGE-06 aplica a `Task/020`.
  - En ambos casos la **propiedad funcional sigue siendo `backend`**.

**Observación heredada, explícitamente fuera de alcance.** La fila de `Task/024` en ROADMAP
y su campo *Repositorio* en STAGE-08 arrastran la misma omisión. **No se corrigieron.**
`Task/023` **no ha auditado ni corregido `Task/024`**: solo deja constancia de lo observado
en sus dos entradas, para el preflight de esa tarea. No se afirma nada más sobre ella.

**Examinada y desestimada durante el preflight, sin cambios:** STAGE-08 cita que la matriz
de paridad §7 asigna la fila **Lambda** a `Task/024`, `Task/025` → `Task/032`, mientras
`aws-local-parity` §6.2 incluye además `Task/023`. Verificada §7 directamente, la cita es
exacta: son **campos distintos** —la matriz evalúa el servicio emulado; §6.2 enumera quién
valida la capacidad—, no una contradicción.

## 14. Archivos modificados

### `personal-blog-backend`

| Archivo | Acción |
| --- | --- |
| `app/lambda_handler.py` | **Creado** — el adaptador |
| `pyproject.toml` | Modificado — `mangum==0.22.0` con su justificación |
| `requirements.lock` | Modificado — `+5 / -0` |
| `requirements-dev.lock` | Modificado — `+5 / -0` |
| `tests/eventos_lambda.py` | **Creado** — harness de eventos v2, compartido |
| `tests/contract/test_handler_lambda.py` | **Creado** — 25 pruebas |
| `tests/unit/test_guarda_del_adaptador_lambda.py` | **Creado** — 9 pruebas |
| `tests/unit/test_arranque_del_handler_lambda.py` | **Creado** — 2 pruebas |
| `tests/integration/test_handler_lambda_sesion_administrativa.py` | **Creado** — 6 pruebas |

**Sin cambios, y es parte del entregable:** `app/main.py`, `Dockerfile`, `alembic/`,
`.github/workflows/ci-backend.yml`.

### `personal-blog-infra`

| Archivo | Acción |
| --- | --- |
| `docs/tasks/TASK-023-fastapi-lambda-compatibility.md` | **Creado** |
| `docs/task-reports/TASK-023-report.md` | **Creado** |
| `docs/project-management/STATUS.md` | Modificado |
| `docs/project-management/ROADMAP.md` | Modificado |
| `docs/stages/STAGE-08-cloud-ready.md` | Modificado |

### `personal-blog-frontend`

**Ninguno.** `git status --porcelain` vacío.

## 15. Problemas encontrados

| # | Problema | Estado |
| --- | --- | --- |
| H-023-0 | La primera guarda de *lifespan* medía un detalle interno de FastAPI | **Resuelto**: sustituida por tres capas (§5) |
| H-023-1 | `DeprecationWarning` al construir el adaptador en Python 3.12 con `-W error` | **Resuelto** sin silenciar, con regresión permanente (§6) |
| H-023-2 | `mypy --strict`: `ASGIApp` no es asignable al protocolo del adaptador | **Resuelto** declarando el tipo real, sin `type: ignore` (§7) |
| H-023-3 | Fallo de un test de concurrencia, **no reproducido** en 8 intentos posteriores | **Abierto, sin diagnosticar** (§8) |

## 16. Lo que esta tarea NO hizo

Terraform · Floci · Lambda real o emulada · AWS CLI contra AWS · credenciales o recursos
AWS · ZIP productivo · medición de arranque en frío · provisión de API Gateway · **elección
del *stage* de producción** · rediseño del límite de tasa, de `trusted_proxy_hop_count` o
de la correlación · cambios en el frontend · `commit`, `push`, `merge` o pull request.

**Sobre el *stage*:** el adaptador **no** configura `api_gateway_base_path`. Queda
registrado que un *stage* nombrado haría llegar el prefijo del *stage* en el camino y
exigiría tratamiento explícito; **esa decisión es de `Task/033`** y no se anticipa aquí con
configuración nueva.

## 17. Estado final

| Elemento | Valor |
| --- | --- |
| `Task/023` | **Aprobada** el 2026-09-13 |
| ETAPA 08 | **En progreso — 1 de 4 (25 %)**. **No completada**: `Task/024`, `Task/025` y `Task/026` siguen Pendientes |
| Avance global | **23 de 41 ≈ 56 %** |
| **T-04** | **Satisfecho y Vigente** |
| **P-06** | **Revalidado / conservado** |
| Criterion12 | **C = 0 · D = 0** dentro del alcance de `Task/023` |
| Bloqueos | **No existe defecto bloqueante demostrado atribuible a `Task/023`.** **H-023-3** permanece como **observación abierta no diagnosticada** y será **vigilada en la CI del cierre**. Si la CI lo reproduce, el cierre **debe detenerse** y analizarse |

## 18. Próxima tarea

`Task/024-Artefacto-ZIP-Lambda`. **No se inicia** hasta que el usuario apruebe esta tarea y
se complete el flujo de cierre. Su preflight debe recoger la observación heredada de §13.
