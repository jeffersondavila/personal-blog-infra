# TASK-012.1 — Reporte de implementación

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/012.1-Exponer-Auditoria-Para-Dashboard` |
| **Tipo** | Mantenimiento funcional de la API administrativa. **No cuenta** dentro de las 41 |
| **Estado** | **Aprobada** ✔ el 2026-09-05 por jeffersondavila |
| **Repositorios** | `personal-blog-backend` (funcional) · `personal-blog-infra` (contratos y gobierno) |
| **Repositorio no modificado** | `personal-blog-frontend` |
| **Rama** | `Task/012.1-Exponer-Auditoria-Para-Dashboard`, en worktrees dedicados |
| **SHA base** | `ce166fb7…` (backend) · `5a8f4c8e…` (infra) |
| **Ficha** | [TASK-012.1](../tasks/TASK-012.1-audit-events-for-dashboard.md) |

---

## 1. Qué se entregó

**Una** operación administrativa autenticada de solo lectura:

```http
GET /api/v1/admin/audit-events?page=1&page_size=12
```

Devuelve `Pagina[EventoDeAuditoria]` con cinco campos por elemento —`id`, `occurred_at`,
`action`, `entity_type`, `entity_id`—, ordenada por `occurred_at` descendente con desempate
por `id` ascendente. Sin filtros. Sin migración. Sin escritura.

Con ella, el dashboard mínimo de `MVP_SCOPE.md` §3.3 pasa a ser construible por completo, y
el bloqueo **B-015-1** de `Task/015` queda resuelto en cuanto esta tarea se apruebe, fusione
y normalice.

## 2. Baseline antes de tocar nada

Ejecutado en el worktree, sobre `main` (`ce166fb7`), con PostgreSQL y MinIO locales reales:

| Compuerta | Resultado |
| --- | --- |
| `ruff check .` | **All checks passed!** |
| `ruff format --check .` | **281 files already formatted** |
| `mypy .` | **Success: no issues found in 279 source files** |
| `pytest` | **1527 passed, 1 skipped** en 160,69 s |

El único `skip` es `tests/test_logging_utc.py::…`: `time.tzset` no existe en Windows.

> **Nota sobre el baseline.** Un primer intento añadió una cuarta variable de entorno
> —`PERSONAL_BLOG_TEST_STORAGE_ACCESS_ENDPOINT_URL`— que **no está documentada** en el
> repositorio, y produjo 4 fallos en el contrato de `ObjectStorage`. Se descartó y se repitió
> con exactamente las **tres** variables que documentan `README.md` del backend y la ficha de
> `Task/010`. Los fallos eran del ajuste, no del proyecto.

## 3. Ciclo RED → GREEN

### 3.1 RED — contrato

Antes de escribir una sola línea de código productivo:

```
pytest tests/contract/test_contrato_administrativo.py -q
→ 10 failed, 32 passed
```

| Test | Causa exacta del fallo |
| --- | --- |
| `test_la_especificacion_declara_exactamente_las_rutas_del_contrato` | `Extra items in the right set: '/api/v1/admin/audit-events'` |
| `test_la_auditoria_solo_se_expone_para_leerla` | `assert set() == {'/api/v1/admin/audit-events'}` |
| `test_la_paginacion_administrativa_es_la_del_proyecto` | `KeyError: '/api/v1/admin/audit-events'` |
| `test_el_historial_solo_admite_paginacion` | `KeyError: '/api/v1/admin/audit-events'` |
| `test_el_evento_de_auditoria_expone_exactamente_cinco_campos` | `KeyError: 'EventoDeAuditoria'` |
| `test_el_evento_de_auditoria_no_expone_lo_que_no_esta_en_el_contrato` ×5 | `KeyError: 'EventoDeAuditoria'` |

**RED genuino**: los diez fallan porque la ruta y el esquema no existen todavía, no por un
error de sintaxis ni de importación.

### 3.2 GREEN — contrato

Tras los *slices* de consulta, esquema, router y montaje:

```
pytest tests/contract/test_contrato_administrativo.py -q
→ 42 passed
```

### 3.3 GREEN — integración

```
pytest tests/integration/test_api_admin_auditoria.py -q
→ 38 passed
```

## 4. Verificación anti-tautología: tres mutaciones

Un test que no puede fallar no prueba nada. Se mutó la implementación **tres veces**, se
comprobó el rojo esperado y se revirtió cada mutación:

| # | Mutación aplicada | Test que se puso rojo | Revertida |
| --- | --- | --- | :---: |
| 1 | Desempate `id.desc()` en lugar de `id.asc()` | `test_los_eventos_del_mismo_instante_desempatan_por_identificador` | ✔ |
| 2 | El DTO gana `ip_address` y lo serializa | `…no_transporta_campos_internos[ip_address]`, `…exactamente_los_cinco_campos…` y sus dos equivalentes de contrato — **4 rojos** | ✔ |
| 3 | El router escribe un `AuditEvent` al leer | `test_leer_el_historial_no_escribe_en_el_historial` | ✔ |

La tercera es la que importa: demuestra que la garantía *«las lecturas no se auditan»* está
realmente protegida y no es una afirmación del reporte.

## 5. Regresión completa

Comandos canónicos de `CONTRIBUTING.md` §5, contra PostgreSQL y MinIO reales:

| Compuerta | Baseline | Después | Resultado |
| --- | --- | --- | --- |
| `ruff check .` | passed | passed | ✔ |
| `ruff format --check .` | 281 formateados | 286 formateados | ✔ |
| `mypy .` | 279 archivos, 0 problemas | 284 archivos, 0 problemas | ✔ |
| `pytest` | 1527 passed, 1 skipped | **1572 passed, 1 skipped** en 199,23 s | ✔ **+45** |
| `docker build` | — | imagen construida | ✔ |
| `pytest tests/integration/test_migrations.py` | 2 passed | 2 passed | ✔ |

**0 fallos, 0 warnings nuevos.** El único `skip` sigue siendo el de Windows.

Las **45** pruebas nuevas son **38 de integración** y 7 de contrato.

## 6. Migraciones — ninguna

| Comprobación | Resultado |
| --- | --- |
| Migraciones en `alembic/versions/` | **3**, las mismas que antes |
| `git status` sobre `alembic/` | vacío |
| `git status` sobre `audit/infrastructure/models.py`, `audit/domain/`, `registro.py` | vacío |
| Ciclo upgrade/downgrade | 2 pruebas en verde |

El orden se apoya en `ix_audit_events_occurred_at`, creado en `20260826_0002` y justificado
en `data-model.md` §5 como *«listado cronológico del historial»*. **No se añadió índice
compuesto preventivo**: el desempate solo actúa entre las pocas filas que comparten instante.

## 7. Tests históricos enmendados — **tres**, no dos

La definición anticipó dos. La ejecución de la suite completa reveló un **tercero**, con la
misma premisa falsa. Los tres se enmiendan por el motivo **2** de
`BACKEND_TESTING_STRATEGY.md` §9 —*el test contradice explícitamente la documentación
vigente*— salvo donde se indica el motivo **1**.

| # | Test | Antes | Después | Motivo |
| --- | --- | --- | --- | --- |
| 1 | `test_no_se_expone_ninguna_ruta_de_auditoria` → **renombrado** a `test_la_auditoria_solo_se_expone_para_leerla` | `assert "audit" not in ruta` para toda ruta. Docstring: *«Ninguna fuente pide exponer el historial por API en el MVP»* | Existe **exactamente una** ruta de auditoría, es la del contrato y declara **solo `get`** | **2** — `MVP_SCOPE.md` §3.3 sí lo pide |
| 2 | `test_la_especificacion_declara_exactamente_las_rutas_del_contrato` | 23 rutas administrativas | **24** | **1** — el requisito cambió |
| 3 | `test_openapi_no_declara_endpoints_no_implementados` | `assert not [ruta … if "audit" in ruta]` | Una única ruta de auditoría, con `{"get"}` como único método | **2** — misma premisa falsa. Su propio docstring ya registraba dos enmiendas anteriores, en `Task/009` y `Task/012` |

**Ningún assert se debilitó.** Los tres pasan de comprobar una **ausencia** a comprobar una
**superficie exacta**, que es una condición más restrictiva: antes, cualquier ruta de
auditoría con cualquier método habría hecho fallar la prueba; ahora, cualquier ruta de
auditoría distinta de la del contrato, o con cualquier método de escritura, también la hace
fallar. No se usó `skip` ni `xfail`, y no se borró cobertura negativa.

## 8. Un test propio corregido durante la implementación

`test_un_evento_escrito_por_un_caso_de_uso_real_aparece_el_primero` pasaba en aislamiento y
fallaba en la suite completa. La causa **no era la implementación**:

```
assert 'authentication.login_succeeded' == 'content.published'
```

El acceso del administrador y la publicación del artículo ocurren **dentro de la misma
transacción de la prueba**, y `occurred_at` se rellena con `now()`, que en PostgreSQL es la
marca de **inicio de la transacción**. Ambos eventos comparten el instante al microsegundo,
así que quién sale primero lo decide el desempate por `id`, no la cronología.

Es una **confirmación empírica del motivo por el que existe el desempate**. La prueba
afirmaba una posición que el dato no contiene; se corrigió para afirmar lo que sí demuestra
—que el evento real aparece en el historial con los datos correctos— y se renombró a
`…aparece_en_el_historial`. La expectativa cambió porque **era incorrecta**, no para
acomodar el código.

## 8bis. Corrección de validación — la colección vacía no estaba cubierta

**Detectado en la validación del usuario, antes de aprobar.** La prueba
`test_un_historial_vacio_es_una_pagina_vacia` afirmaba en su docstring cubrir
`total = 0` y `pages = 0`, pero preparaba la sesión con `administrador_con_sesion`, que
**inicia sesión de verdad** y por tanto escribe `authentication.login_succeeded`. El
historial nunca estaba vacío: lo que la prueba comprobaba en realidad era `total >= 1` y
`pages == 1`.

Tampoco lo cubría `test_una_pagina_fuera_de_rango_es_una_pagina_vacia`: allí `items`
también viene vacío, pero con `total > 0` y `pages > 0`. **El caso `pages = 0` no estaba
verificado por ninguna prueba.**

### Cómo se preparó una sesión sin auditar

El obstáculo es legítimo: iniciar sesión **debe** auditarse (USER_FLOWS.md B.1). La salida
no es desactivar la auditoría ni borrar el evento, sino **no producirlo**: se construye la
sesión con las mismas funciones de dominio que usa el código real.

Nuevo *helper* `administrador_con_sesion_sin_auditar` en `tests/integration/administracion.py`,
junto a su hermano de siempre. Reutiliza:

| Pieza reutilizada | Origen |
| --- | --- |
| `administrador(sesion)` | `tests/integration/datos_de_autenticacion.py` (`Task/011`) |
| `generar_credencial()` — credencial opaca de 256 bits | `app/modules/authentication/domain/sesion.py` |
| `huella_de_credencial()` — SHA-256, lo único que se persiste (**D-011-B**) | ídem |
| `AdministratorSession` | `app/modules/authentication/infrastructure/models.py` |
| `NOMBRE_DE_LA_COOKIE` | `app/modules/authentication/presentation/cookies.py` |

La fila resultante es **indistinguible** de la que crea `IniciarSesion`, así que las
dependencias administrativas la aceptan sin ninguna concesión.

**Lo que no se hizo, y es lo que hace legítima esta preparación:** ningún endpoint nuevo,
ninguna bandera de producción, ninguna desactivación de auditoría, ningún cambio en el
login, ningún *mock* de la consulta y **ningún borrado de `AuditEvent`** — la invariante de
historial inmutable no necesita relajarse, porque el evento sencillamente no llega a
existir. Es *setup* de integración, no comportamiento productivo.

### Assertions del caso vacío

```python
administrador_con_sesion_sin_auditar(cliente_administrativo, sesion_de_pruebas)

assert _contar(sesion_de_pruebas) == 0          # PostgreSQL real, antes del GET

respuesta = cliente_administrativo.get(HISTORIAL)
cuerpo = respuesta.json()

assert respuesta.status_code == 200
assert cuerpo["items"] == []
assert cuerpo["page"] == 1
assert cuerpo["page_size"] == 12
assert cuerpo["total"] == 0
assert cuerpo["pages"] == 0
```

El `assert` previo sobre la tabla real evita la tautología: sin él, un `total` de cero
podría venir de un filtro accidental en lugar de una colección realmente vacía.

El caso «hay filas» no se perdió: se conserva en `test_la_envoltura_declara_el_total_real`,
que es lo que la prueba anterior comprobaba de verdad, ahora con nombre honesto.

### Anti-tautología del caso

`numero_de_paginas` mutada a `max(1, -(-total // page_size))` —es decir, `pages` nunca cero—:

```
pytest tests/integration/test_api_admin_auditoria.py -k historial_vacio
→ E  assert 1 == 0
   1 failed
```

Mutación **revertida**; `git diff app/shared/pagination/` vacío. **Ningún código productivo
cambió** en esta corrección: solo pruebas y su *helper*, así que no procede repetir el
`docker build` ni las migraciones.

**Ahora puede afirmarse literalmente:** colección con `total = 0` verificada contra el
endpoint real, con `items = []` y `pages = 0`.

## 9. Refactor gate

Revisado solo el código añadido:

| Pregunta | Respuesta |
| --- | --- |
| ¿Duplicación real? | No. `queries.py` sigue el patrón de `media/infrastructure/queries.py`; es la convención del proyecto, no copia que deba extraerse |
| ¿Abstracción vacía? | No. **Sin capa `application`** (**D-009-Q**) y **sin repositorio**: no hay escritura que justifique ninguno |
| ¿Imports cruzando capas? | No. El router importa consultas de `infrastructure`, su DTO de `presentation` y las dependencias compartidas, igual que los siete routers existentes |
| ¿Lógica de negocio en `presentation`? | No. El router cuenta, lista y serializa |
| ¿`queries.py` hace de más? | No. Dos funciones, ambas usadas, sin filtros ni relaciones cargadas |
| ¿El esquema expone de más? | No. Cinco campos, fijados por prueba de contrato y de respuesta real |

**Refactor declarado innecesario.** Los únicos ajustes fueron de formato: tres líneas de
docstring por encima de 100 caracteres y una comprensión de lista, señaladas por `ruff`.

## 10. Archivos

### Backend — creados

| Archivo | Responsabilidad |
| --- | --- |
| `app/modules/audit/infrastructure/queries.py` | `contar_eventos_de_auditoria` y `listar_eventos_de_auditoria` |
| `app/modules/audit/presentation/__init__.py` | Paquete de presentación del módulo |
| `app/modules/audit/presentation/schemas_admin.py` | `EventoDeAuditoria`, cinco campos declarados uno a uno |
| `app/modules/audit/presentation/router_admin.py` | `GET /admin/audit-events` |
| `tests/integration/test_api_admin_auditoria.py` | 37 pruebas contra PostgreSQL real |

### Backend — modificados

| Archivo | Cambio |
| --- | --- |
| `app/api/admin.py` | Monta el router de auditoría en `routers_administrativos()`. Nada más |
| `tests/contract/test_contrato_administrativo.py` | Inventario a 24, test de auditoría reemplazado, 3 pruebas nuevas de superficie |
| `tests/test_openapi.py` | Tercera enmienda histórica (§7) |
| `tests/integration/administracion.py` | Nuevo *helper* `administrador_con_sesion_sin_auditar` (§8bis). El existente `administrador_con_sesion` no se toca |

### Backend — deliberadamente intactos

`audit/domain/**`, `audit/infrastructure/models.py`, `audit/infrastructure/registro.py`,
`alembic/**`, los siete módulos de contenido, `authentication`, la configuración, el
`Dockerfile` y `.env.example`.

### Infra — documentación

| Archivo | Cambio |
| --- | --- |
| `docs/architecture/api-contracts.md` | §4 y §11 actualizadas; §14.1 pasa a **24 patrones** con la distinción patrón/operación; **§15 nueva** con el contrato completo |
| `docs/architecture/security-boundaries.md` | **B-08 enmendada**, **B-08b añadida**, **§12.4 nueva** con el porqué |
| `docs/architecture/software-architecture.md` | El módulo `audit` gana capa de presentación; inventario de archivos ampliado |
| `docs/architecture/data-model.md` | `ix_audit_events_occurred_at` registra su consumidor real y que no hizo falta índice nuevo |
| `docs/project-management/STATUS.md` · `ROADMAP.md` | Mantenimiento registrado; contadores intactos |
| `docs/tasks/TASK-012.1-…md` | Estado y resultados |

## 11. Inventario HTTP resultante

| Origen | Patrones | Operaciones |
| --- | ---: | ---: |
| `Task/011` — autenticación | 3 | 3 |
| `Task/012` — CRUD administrativo | 23 | 35 |
| **`Task/012.1` — historial** | **1** | **1** |
| **Total administrativo y de acceso** | **27** | **39** |

Más las 11 públicas, el documento OpenAPI declara **38 patrones de ruta**.

## 12. Seguridad — lo comprobado, no lo afirmado

| Garantía | Cómo se comprueba |
| --- | --- |
| Sin sesión, `401 unauthenticated` | Prueba propia, más la transversal que recorre OpenAPI entera |
| Sesión válida, `200` | Prueba propia |
| `Cache-Control: no-store` | Sobre la respuesta real |
| `GET` no exige `Origin` | Petición con `Origin: https://evil.invalid` que responde `200`. **No se añadió ninguna excepción**: se deriva de que `origen_permitido()` solo cubre `POST`, `PUT`, `PATCH` y `DELETE` |
| Sin escritura | `POST`, `PUT`, `PATCH` y `DELETE` responden `405`; no existe detalle `/{id}` (`404`) |
| **Leer no audita** | `count(*)` real antes y después del `GET`, sin *mock*. Mutación 3 confirma que la prueba puede fallar |
| Privacidad del DTO | `actor_id`, `event_metadata`, `metadata`, `request_id` e `ip_address` ausentes del esquema **y** del JSON real, con el evento escrito **con** esos datos rellenos |
| Parámetro desconocido | `?foo`, `?action`, `?entity_type`, `?actor_id`, `?status` → `422` |

## 13. Incidencia registrada — anomalía **preexistente** del harness

Con ciertas combinaciones explícitas de archivos en la línea de comandos —una ruta de
`tests/integration/`, seguida de `tests/test_openapi.py`, seguida de otra de
`tests/integration/`—, pytest no carga `tests/integration/conftest.py` para el tercer
argumento y sus pruebas fallan con `fixture 'sesion_de_pruebas' not found`.

**No la introduce esta tarea.** Se reprodujo con **cero** archivos de `Task/012.1`:

```
pytest tests/integration/test_auditoria_de_autenticacion.py tests/test_openapi.py \
       tests/integration/test_auditoria.py -q
→ 21 passed, 11 errors
```

**No ocurre en la invocación canónica** (`pytest`, que es la que exige la Definition of Done)
ni al seleccionar directorios completos. Se reporta como hallazgo y **no se repara**:
arreglar el harness ajeno dentro de esta maintenance mezclaría alcances.

## 14. Lo que esta tarea NO hace

- No modifica cómo, cuándo ni qué se audita.
- No relaja ninguna invariante: `AuditEvent` sigue sin poder modificarse ni eliminarse.
- No añade filtros, ni detalle, ni endpoint de dashboard.
- No expone datos personales.
- No crea migraciones ni índices.
- No toca el frontend, Terraform, Docker Compose, MinIO ni S3.
- **No desbloquea `Task/015`**: eso ocurre cuando esta tarea se apruebe, se fusione y se
  normalice.

## 15. Deuda técnica pendiente

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | Filtros del historial por acción, tipo, elemento o fechas | Sin propietario; ampliación compatible |
| 2 | Resolver el nombre del actor cuando exista más de un administrador | Sin propietario; fuera del MVP |
| 3 | Exponer `request_id` cuando `Task/017` fije la cabecera del correlation ID | `Task/017` |
| 4 | Retención, rotación y archivado del historial | Operación |
| 5 | Privilegio mínimo sobre `audit_events` (invariante 16b) | `Task/018` |
| 6 | Anomalía de carga de `conftest` descrita en §13 | Sin propietario; candidata a una maintenance del harness |

## 16. Pasos de validación para el usuario

Desde el worktree `\.worktrees\backend-012.1`, con el entorno local en marcha:

```powershell
$env:PERSONAL_BLOG_TEST_DATABASE_URL = "postgresql://<usuario>:<clave>@127.0.0.1:55432/personal_blog_test"
$env:PERSONAL_BLOG_TEST_STORAGE_ENDPOINT_URL = "http://127.0.0.1:9000"
$env:PERSONAL_BLOG_TEST_STORAGE_ACCESS_KEY = "<MINIO_ROOT_USER del .env de infra>"
$env:PERSONAL_BLOG_TEST_STORAGE_SECRET_KEY = "<MINIO_ROOT_PASSWORD del .env de infra>"

ruff check .
ruff format --check .
mypy .
pytest

# La ruta existe, es la unica de auditoria y solo admite GET
pytest tests/contract/test_contrato_administrativo.py -k auditoria -v

# La lectura no escribe en el historial
pytest tests/integration/test_api_admin_auditoria.py -k no_escribe -v

# No hay migracion nueva: siguen siendo tres
Get-ChildItem alembic/versions/*.py | Measure-Object
```

## 17. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** ✔ |
| **Fecha de aprobación** | **2026-09-05** |
| **Aprobado por** | **jeffersondavila** (el usuario) |
| **Expresión de aprobación** | `approved: Task/012.1-Exponer-Auditoria-Para-Dashboard` — recibida literalmente |

La aprobación autorizó el flujo de cierre de
[`WORKFLOW.md`](../project-management/WORKFLOW.md) §3 en `personal-blog-backend` y
`personal-blog-infra`: promoción de las decisiones a **Vigentes**, commits, integración en
`dev` mediante merge `--no-ff` y pull request
`Task/012.1-Exponer-Auditoria-Para-Dashboard → main`.

**La revisión y la fusión del pull request son responsabilidad exclusiva del usuario.**
