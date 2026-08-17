# Reporte — TASK-005.7 · Cerrar hallazgos finales de certificación

| Campo | Valor |
| --- | --- |
| **Rama** | `Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion` |
| **Estado** | **Aprobada** ✔ el 2026-08-16 por jeffersondavila |
| **Expresión de aprobación** | `approved: Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion` |
| **Fecha** | 2026-08-16 |
| **Repositorios** | `personal-blog-backend`, `personal-blog-infra`, `personal-blog-frontend` |
| **Rama base** | **`main`** en los tres, verificado `HEAD == main` tras crear cada rama |
| **SHA base** | infra `7c98f591` · backend `c36cd44b` · frontend `5d2bef1b` |
| **Cuenta en las 41 tareas** | **No** |
| **Commits** | **0** · **Push:** 0 · **Merge:** 0 · **PR:** 0 |

---

## 1. Estado Git inicial

Verificado en los tres repositorios **antes** de crear ninguna rama:

| Comprobación | infra | backend | frontend |
| --- | --- | --- | --- |
| Rama activa | `main` | `main` | `main` |
| `main == origin/main` | ✔ `7c98f591` | ✔ `c36cd44b` | ✔ `5d2bef1b` |
| `dev == origin/dev` | ✔ `5d7f474c` | ✔ `a9210466` | ✔ `b81c67b3` |
| `main` es ancestro de `dev` | ✔ | ✔ | ✔ |
| `git diff main dev` | vacío | vacío | vacío |
| *Working tree* limpio | ✔ | ✔ | ✔ |
| *Staging* vacío | ✔ | ✔ | ✔ |
| Ramas Task locales | ninguna | ninguna | ninguna |
| Ramas Task remotas | ninguna | ninguna | ninguna |

Los tres SHA coinciden exactamente con los indicados como referencia en el prompt. **No se
detectó ninguna anomalía.**

---

## 2. Matriz de hallazgos

| ID | Origen | Severidad original | Reproducido | Acción | Archivos | Test | Resultado | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **CERT-AUD-001-A** | Claude **MEDIO** · Codex **ALTO** | Discrepancia de severidad; **ambos lo reprodujeron** | **SÍ** — `get_settings()` bajo `configured_process` devolvió `app_name='nombre-intruso'`, `log_level='CRITICAL'`, `app_debug=True` | Bootstrap hermético del proceso de pruebas | `tests/__init__.py` | `test_configured_process_no_hereda_campos_de_un_dotenv` | RED → GREEN | **Cerrado** |
| **CERT-AUD-001-B** | Claude **MEDIO** · Codex **ALTO** | ídem | **SÍ** — *collection* real con `--collect-only`: `app.title='nombre-intruso'`, `app.debug=True` | Bootstrap hermético + import diferido de `app.main` | `tests/__init__.py`, `tests/conftest.py` | `test_la_collection_no_consume_un_dotenv_del_directorio_de_trabajo`, `test_la_collection_no_construye_la_aplicacion` | RED → GREEN | **Cerrado** |
| **CERT-AUD-002** | Claude **MEDIO** · Codex **ALTO** | ídem | **SÍ** — el cuerpo exacto de `database_settings` + `create_database_engine` alcanzó una base `_test` **sin marca** y ejecutó `CREATE TABLE` (`DDL ejecutado: True`) | Resolutor único que verifica **antes** del `yield` | `tests/integration/conftest.py` | `test_la_ruta_mas_baja_no_permite_saltarse_la_guarda` + 4 más | RED → GREEN | **Cerrado** |
| **CERT-AUD-009** | Claude · Codex | Menor | **SÍ** — por inspección: tabla fija, `downgrade base` compartido, mutación de proceso | **Diferido a propósito** | `STATUS.md` (**R-37**) | — | Registrado con propietario `Task/020` | **Diferido** |
| **DOC-1** | Auditoría | Bajo | **SÍ** — 3 apariciones | Corregido | `local-environment.md` | sweep §38 | 0 restantes | **Cerrado** |
| **DOC-2** | Auditoría | Bajo | **SÍ** — línea 18 absoluta vs línea 68 aclaratoria | Acotado el sujeto | `STAGE-11-*.md` | sweep §38 | coherente | **Cerrado** |
| **DOC-3** | Auditoría | Bajo | **SÍ** — `.ps1` crlf vs lf (infra); `.bat`/`.cmd` sin regla (los tres) | Reconciliado | 3 × `.editorconfig` | `git check-attr` | coherente | **Cerrado** |
| **DOC-4** | Auditoría | Bajo | **SÍ** — dos títulos idénticos | Renombrado el anterior | `STATUS.md` | sweep §38 | 1 solo título | **Cerrado** |
| **DOC-5** | Auditoría | Bajo | **SÍ** — línea 279 vs §6.1 regla 3 | Una sola regla vigente | `WORKFLOW.md` | sweep §38 | coherente | **Cerrado** |
| **DOC-6** | Auditoría | Bajo | **SÍ** — 2 comandos históricos | Advertencia visible; **comando conservado** | ficha y reporte `Task/005` | sweep §38 | marcados | **Cerrado** |
| **DOC-7** | Auditoría | Bajo | **SÍ** — absoluto pese a ADR-007 | Reformulado | `overview.md` | sweep §38 | 0 restantes | **Cerrado** |
| **DOC-8** | Encontrado en `005.7` | Bajo | **SÍ** — `README` nombraba `Task/005.4` como último mantenimiento y `005.5` como *en curso* | Actualizado | `README.md` (infra) | sweep §38 | correcto | **Cerrado** |

> **Sobre la discrepancia de severidad.** Claude la clasificó **MEDIO** y propuso diferir;
> Codex la clasificó **ALTO** y consideró la baseline **no certificada**. `005.7` **no
> arbitra la severidad**: ambos reprodujeron los mismos dos defectos, y eso es lo que se
> corrige. Se adoptó deliberadamente el criterio **más estricto**.

---

## 3. `CERT-AUD-001` — hermeticidad

### 3.1 Reproducción **antes** del fix

*Collection* real, ejecutada desde un directorio temporal con un `.env` intruso
(`BLOG_APP_NAME=nombre-intruso`, `BLOG_LOG_LEVEL=CRITICAL`, `BLOG_APP_DEBUG=true`):

```
PLUGIN >> app.main importado durante collection: True
PLUGIN >> app.title = nombre-intruso
PLUGIN >> app.debug = True
74 tests collected in 0.61s
```

Y por la ruta de integración, con `configured_process` activa:

```
AssertionError: assert 'nombre-intruso' != 'nombre-intruso'
 +  where 'nombre-intruso' = Settings(app_name='nombre-intruso', app_env='local',
    app_debug=True, ..., log_level='CRITICAL', ...).app_name
```

### 3.2 Causa raíz

`Settings` declara `env_file=".env"`, que `pydantic-settings` resuelve **relativo al
directorio de trabajo**. Dos consumidores lo alcanzaban sin *overrides*:

1. `app/main.py` construye la instancia ASGI **al importarse** (`app = create_app()`), como
   exige el arranque *fail-fast* (T-01). `tests/conftest.py` importaba ese módulo en su
   cabecera, así que la aplicación se construía **durante la *collection***.
2. `session_scope`, `get_session` y `alembic/env.py` llaman a `get_settings()`, que construye
   `Settings()` sin *overrides*.

**Por qué ninguna *fixture* podía arreglarlo:** las *fixtures* —incluidas las `autouse`— se
ejecutan **después** de la *collection*. Llegan tarde por definición.

### 3.3 Solución

Dos capas independientes, ambas en `tests/`. **`app/` no se modificó**: el problema estaba en
el harness, y la aplicación real sigue leyendo su `.env` como siempre.

| Capa | Qué hace | Dónde |
| --- | --- | --- |
| **1** | Neutraliza el dotenv para **todo el proceso** (`Settings.model_config["env_file"] = None`) y limpia el entorno, antes de que pytest coleccione nada | `tests/__init__.py` |
| **2** | El import de `app.main` se difiere al interior de la *fixture* `application`: la *collection* ya no construye la aplicación | `tests/conftest.py` |

Ajuste asociado: `_isolated_environment` **repone** la URL ficticia obligatoria tras limpiar
`BLOG_*`, porque `BLOG_DATABASE_URL` es el único campo sin valor por defecto y el import
diferido la necesita.

### 3.4 RED → GREEN

| Prueba | RED (antes) | GREEN (después) |
| --- | --- | --- |
| `test_la_collection_no_consume_un_dotenv_del_directorio_de_trabajo` | FAILED | PASSED |
| `test_la_collection_no_construye_la_aplicacion` | FAILED | PASSED |
| `test_el_aislamiento_no_depende_del_directorio_de_trabajo` | FAILED — `assert 'nombre-intruso' == 'personal-blog-backend'` | PASSED |
| `test_configured_process_no_hereda_campos_de_un_dotenv` | FAILED | PASSED |
| `test_el_dotenv_intruso_si_es_legible_sin_el_bootstrap` *(anti-tautología)* | PASSED | PASSED |

### 3.5 Resultado del subproceso de *collection* (después)

```
PLUGIN >> app.main importado durante collection: False
95 tests collected in 0.86s
```

### 3.6 `configured_process` con dotenv intruso (después)

```
app.title           : personal-blog-backend
app.debug           : False
root logger level   : INFO
CWD                 : ...\scratchpad\repro001     (cwd ajeno al repositorio)
```

Ningún valor no controlado entra. El resultado **no depende del *cwd***: el subproceso se
ejecuta desde un directorio temporal, no desde el repositorio.

---

## 4. `CERT-AUD-002` — *fail-closed* real

### 4.1 Reproducción **antes** del fix

Ejecutando el **cuerpo exacto** de la *fixture* pública `database_settings` seguido de
`create_database_engine`, contra una base descartable terminada en `_test` **sin marca**:

```
base alcanzada : repro_cert_aud_002_test
marca          : None
DDL ejecutado  : True
```

Y por el harness oficial, con el nodo que recorre la ruta más baja:

```
AssertionError: la ruta mas baja del harness entrego un destino sin verificar:
una prueba futura puede saltarse la guarda
  1 passed in 0.18s
assert 0 != 0
```

### 4.2 Grafo de *fixtures* — antes y después

**Antes** — dos caminos, uno verificado y otro no:

```
PERSONAL_BLOG_TEST_DATABASE_URL
   └─ database_settings ─────────────────────► Settings   ⚠️ SIN VERIFICAR (pública)
         └─ database_engine ──[GUARDA]──────► Engine      ✔ verificado
               ├─ tabla_de_pruebas
               └─ configured_process
         └─ alembic_config (database_settings + database_engine)
```

**Después** — un solo camino, verificado antes del `yield`:

```
PERSONAL_BLOG_TEST_DATABASE_URL
   └─ destino_de_integracion_verificado ──[GUARDA antes del yield]──► (Settings, Engine)
         ├─ database_settings ────► Settings   ✔ verificado
         ├─ database_engine ──────► Engine     ✔ verificado
         ├─ configured_process
         ├─ tabla_de_pruebas
         ├─ alembic_config
         └─ motor_administrativo
```

### 4.3 Causa raíz

`Task/005.6` puso la guarda en `database_engine`, pero dejó `database_settings` **pública y
sin verificar**. El harness ofrecía dos rutas y confiaba en que nadie tomara la mala. La suite
existente la evitaba; el harness la permitía.

### 4.4 Solución

Un **único resolutor**, `destino_de_integracion_verificado`, que convierte la variable de
entorno en configuración y motor, ejecuta la guarda y **solo entonces** hace `yield`. Todo lo
demás se deriva de él. No quedan dos caminos entre los que haya que acordarse de elegir.

### 4.5 Pruebas de rechazo

| Caso | Resultado | Evidencia |
| --- | --- | --- |
| Base `_test` **sin marca** | **FAIL** | `test_una_base_test_sin_marca_se_rechaza_antes_de_cualquier_ddl` · mensaje «no lleva la marca» |
| Base **sin sufijo** `_test` | **FAIL** | `test_una_base_sin_el_sufijo_se_rechaza_antes_de_cualquier_ddl` · mensaje «no termina en '_test'» |
| `personal_blog` | **FAIL** | `test_la_base_de_desarrollo_no_puede_ser_destino_y_queda_intacta` |
| Ruta más baja del harness sobre base sin marca | **FAIL** | `test_la_ruta_mas_baja_no_permite_saltarse_la_guarda` |
| Grafo completo de *fixtures* | **estructural** | `test_toda_fixture_de_integracion_pasa_por_la_guarda`, parametrizado sobre **todas** las *fixtures* de los módulos **descubiertos** en `tests/integration/` |

### 4.6 Confirmación de que el DDL **no** ocurre

Las pruebas apuntan a propósito un nodo que **haría DDL** —`tabla_de_pruebas` ejecuta
`CREATE TABLE`— y comprueban después que la tabla `prueba_transaccional_005_6`
**no existe** en el destino rechazado. El rechazo ocurre en la *fixture*, antes de que el
cuerpo de la prueba llegue a ejecutarse.

Contra `personal_blog` **no se ejecuta ningún `downgrade`**: se comprueba el rechazo y se
compara el esquema y la revisión de Alembic antes y después.

### 4.7 Descubrimiento automático de los módulos del harness

**Corregido tras la revisión del usuario del 2026-08-16.** La primera versión de la
comprobación estructural enumeraba los módulos a inspeccionar en una tupla escrita a mano.
Eso fallaba **abierta**: omitía ya dos módulos existentes
(`test_database_connection`, `test_hermeticidad_de_la_integracion`) y, sobre todo, un
`tests/integration/test_articles.py` creado por `Task/008` con una *fixture* insegura **no
se habría detectado** si nadie recordaba editar la lista. Es exactamente la convención
humana que `CERT-AUD-002` existe para eliminar, reintroducida en la prueba que debía
impedirla.

**Estrategia elegida:** descubrimiento por `pathlib.rglob` sobre el directorio del harness,
con el nombre de módulo derivado de la ruta relativa e `importlib` para cargarlo. Sin
dependencias nuevas, determinista (orden alfabético), y `rglob` cubre subdirectorios que hoy
no existen. Se excluyen `__init__.py` y `__pycache__`; **todo lo demás se inspecciona**,
tenga o no *fixtures* hoy.

Se descartó `pkgutil.iter_modules` por no recorrer subpaquetes sin trabajo extra, y la
introspección del registro de *fixtures* de pytest por depender de API interna.

**Módulos descubiertos (5):** `conftest`, `test_database_connection`,
`test_guarda_del_destino`, `test_hermeticidad_de_la_integracion`, `test_migrations`.

**Fixtures descubiertas (9):** `alembic_config`, `base_sin_marca`, `base_sin_sufijo`,
`configured_process`, `database_engine`, `database_settings`,
`destino_de_integracion_verificado`, `motor_administrativo`, `tabla_de_pruebas`.

#### Regresión adversarial

Se creó temporalmente `tests/integration/test_modulo_adversarial_temporal.py` con una
*fixture* `configuracion_insegura_de_articulos` que resuelve el destino por su cuenta, **sin
registrarla en ninguna lista**:

```
FAILED test_toda_fixture_de_integracion_pasa_por_la_guarda[configuracion_insegura_de_articulos]
AssertionError: la fixture 'configuracion_insegura_de_articulos' del harness de integracion
no depende de 'destino_de_integracion_verificado' ...
1 failed, 12 passed
```

El módulo se eliminó por completo y la prueba volvió a **12 passed**. No quedan archivos
temporales.

#### Guardas anti-tautología

La prueba **no puede ponerse verde porque el descubrimiento deje de encontrar archivos**.
Verificado rompiendo cada guarda de forma controlada, sin modificar el archivo —hash SHA-256
idéntico antes y después—:

| Rotura simulada | Resultado |
| --- | --- |
| Directorio del harness inexistente | **ROJO** — «el directorio del harness de integracion no existe» |
| pytest cambia cómo marca las *fixtures* (conjunto vacío) | **ROJO** — «la inspeccion no encontro [...]» |
| El resolutor desaparece o se renombra | **ROJO** — «el harness de integracion ya no define [...]» |

El mensaje de fallo nombra los **remedios legítimos** —derivar la *fixture* del resolutor, o
sacarla de `tests/integration/` si de verdad no toca la base— y declara explícitamente que
rebajar la comprobación no es uno de ellos.

**Alcance, sin sobreafirmar:** lo garantizado es que **toda *fixture* definida en un módulo
de `tests/integration/` entra en la comprobación automáticamente**. No se afirma nada sobre
*fixtures* definidas fuera de ese directorio, que por definición no forman parte del harness
de integración.

---

## 5. Base de datos de desarrollo — antes y después

| Elemento | Antes | Después | Idéntico |
| --- | --- | --- | --- |
| Tablas públicas de `personal_blog` | `alembic_version` | `alembic_version` | ✔ |
| Revisión de Alembic | `0001` | `0001` | ✔ |
| Comentario de la base | *(sin comentario)* | *(sin comentario)* | ✔ |
| `personal_blog_test` — marca | `personal-blog:test-database …` | `personal-blog:test-database …` | ✔ |

**`personal_blog` quedó intacta.** Las bases descartables creadas durante las pruebas
(`personal_blog_guarda_005_7_test`, `personal_blog_guarda_005_7_dev`,
`repro_cert_aud_002_test`) se eliminaron.

---

## 6. Contratos de `Task/005.6` — siguen vigentes

| Caso | Exigido | Observado |
| --- | --- | --- |
| Sin `PERSONAL_BLOG_TEST_DATABASE_URL` | `SKIP` | ✔ 17 *skipped* con motivo |
| Variable definida y PostgreSQL roto | `FAIL` | ✔ «PostgreSQL no responde: ConnectionTimeout» |
| Base sin `_test` | `FAIL` | ✔ «no termina en `_test`» |
| Base `_test` sin marca | `FAIL` | ✔ «no lleva la marca» |
| Base válida | `PASS` | ✔ `1 passed` |
| *Commit* | Persistencia visible desde otra sesión | ✔ |
| *Rollback* | Dato no persistido | ✔ |
| Alembic | `upgrade` → `downgrade` → `upgrade` | ✔ |

### 6.1 *Mutation test*

| Mutación | Prueba | Resultado |
| --- | --- | --- |
| Eliminar `session.commit()` | `test_session_scope_confirma_y_el_dato_persiste` | **ROJO** — `assert None == 'confirmado'` |
| `session.rollback()` → `session.commit()` | `test_session_scope_revierte_y_el_dato_no_persiste` | **ROJO** — `assert 1 == 0` |

`app/shared/database/session.py` restaurado con el **mismo hash SHA-256**
(`E7378E7F…A167CE`) y `git status -- app/` vacío. No queda ningún andamiaje de mutación.

---

## 7. *Quality gates*

| Validación | Resultado | Código de salida |
| --- | --- | --- |
| `python --version` | 3.12.10 | 0 |
| `pip check` | *No broken requirements found* | 0 |
| `pytest` **con** integración real | **95 passed, 1 skipped** | 0 |
| `pytest -W error` | **95 passed, 1 skipped** — 0 *warnings*, sin filtros | 0 |
| `pytest` **sin** integración | **79 passed, 17 skipped** | 0 |
| `pytest --cov --cov-report=term-missing` | **100 %** · 249 sentencias, 0 sin cubrir · 22 ramas, 0 parciales | 0 |
| `ruff check .` | *All checks passed!* | 0 |
| `ruff format --check .` | 36 archivos ya formateados | 0 |
| `mypy` (*strict*) | *Success: no issues found in 34 source files* | 0 |

El único `skipped` sin integración adicional es `test_logging_utc.py` — `time.tzset` no existe
en Windows, omisión preexistente y documentada.

**Sin integración se omiten únicamente las pruebas que requieren PostgreSQL.** La comprobación
estructural del grafo de *fixtures* vive fuera de `tests/integration/` **a propósito**: se
ejecuta siempre, también cuando no hay base de datos.

### 7.1 Docker

| Comprobación | Resultado |
| --- | --- |
| `docker build` | **OK**, código de salida 0 |
| Usuario del proceso | `uid=1001(blog) gid=1001(blog)` — **no root** |
| `GET /health` | **200** · `{"status":"ok","service":"personal-blog-backend","version":"0.1.0"}` |
| `GET /openapi.json` | **200** · 1 130 bytes |
| Logs | Sin secretos: la URL aparece enmascarada como `postgresql://u:***@…` |

Se eliminaron **solo** los recursos creados por esta tarea (imagen `task-005-7` y contenedor
`pb-smoke-005-7`). Las imágenes históricas `mega-audit`, `task005-final` y `local`
**siguen presentes**.

---

## 8. Correcciones documentales

| # | Archivo | Corrección |
| --- | --- | --- |
| 1 | `docs/runbooks/local-environment.md` | Backup local **disponible** (`Task/004` aprobada), en la tabla de límites y en los dos avisos de `down -v` |
| 2 | `docs/stages/STAGE-11-deployment-automation.md` | Sujeto explícito: «sin credenciales permanentes **en el canal GitHub Actions → AWS**». **D-16 sigue abierta**; no se resuelve |
| 3 | `.editorconfig` × 3 | `*.ps1`/`*.psm1`/`*.psd1` → **LF** (era `crlf` en infra); `*.bat`/`*.cmd` → **CRLF** en los tres, que antes caían bajo el `[*]` LF |
| 4 | `docs/project-management/STATUS.md` | La sección de `005.5` pasa a «Mantenimiento **anterior** aprobado». Historia intacta |
| 5 | `docs/project-management/WORKFLOW.md` | Fuente viva única: **Git/GitHub** para estado transitorio, documentación para estado duradero |
| 6 | ficha y reporte de `Task/005` | Advertencia **HISTÓRICO — NO EJECUTAR** sobre los comandos que apuntan a `personal_blog`. **Los comandos se conservan** |
| 7 | `docs/architecture/overview.md` | «Evitar todo costo fijo **innecesario**», con el **VPS PostgreSQL como excepción consciente y presupuestada** (ADR-007). **ADR-007 no se modifica** |
| 8 | `README.md` (infra) | Último mantenimiento aprobado: `Task/005.6`; en curso: `Task/005.7` |

### 8.1 Coherencia EOL verificada

`git check-attr` y `git ls-files --eol` confirman que Git y EditorConfig dicen ahora lo mismo:

| Extensión | `.gitattributes` | `.editorconfig` | Coherente |
| --- | --- | --- | --- |
| `*.ps1`, `*.psm1`, `*.psd1` | `eol=lf` | `end_of_line = lf` | ✔ |
| `*.bat`, `*.cmd` | `eol=crlf` | `end_of_line = crlf` | ✔ |

Los 5 scripts PowerShell versionados están en `i/lf w/lf`. **No hizo falta ninguna
normalización masiva**: 0 líneas de diff de contenido.

---

## 9. `CERT-AUD-009` — deuda registrada

| Campo | Valor |
| --- | --- |
| **Riesgo** | **R-37** en [STATUS.md](../project-management/STATUS.md) |
| **Propietario** | **`Task/020-CI-Backend`** — la tarea canónica de CI del backend |
| **Causas registradas** | Tabla auxiliar con nombre fijo · `downgrade base` sobre esquema compartido · mutación de entorno y cachés de proceso |
| **Por qué no se resuelve ahora** | `pytest-xdist` **no está instalado**, no hay ejecución paralela oficial y el flujo de integración es único: el riesgo **no es explotable hoy** |
| **Disparador** | Debe revisarse **antes** de habilitar cualquier ejecución paralela |

**No se implementó paralelismo ni ninguna solución sobredimensionada.**

---

## 10. Validación documental final

Búsquedas ejecutadas al terminar, con las apariciones restantes clasificadas:

| Patrón | Restantes | Clasificación |
| --- | --- | --- |
| «No existen» + backup | 1 | **CORRECTA** — se refiere a los backups de *backend y frontend*, que efectivamente no existen |
| «sin credenciales permanentes» | 6 | **CORRECTAS** — todas con sujeto explícito, más las notas de corrección |
| «estado real» + STATUS | 0 operativas | **CORRECTA** — solo la regla de §6.1 y la nota de corrección |
| «Último mantenimiento aprobado» | 1 título | **CORRECTA** — único, `Task/005.6` |
| `PERSONAL_BLOG_TEST_DATABASE_URL` + `personal_blog` | 2 | **HISTÓRICAS MARCADAS** |
| «sin servicios de costo fijo» | 0 | **CORRECTA** |
| `*.ps1` / `*.bat` en EditorConfig vs Git | 0 contradicciones | **CORRECTA** |

**Apariciones operativas incorrectas: 0.**

---

## 11. Auditoría adversarial posterior al fix

| Ataque | Resultado |
| --- | --- |
| *Collection* desde un *cwd* con `.env` intruso | **Bloqueado** — `app.main` ni siquiera se importa; 95 pruebas coleccionadas |
| Import explícito de `app.main` tras el bootstrap, con `.env` intruso | **Bloqueado** — `personal-blog-backend` / `False` / `INFO` |
| `configured_process` con `.env` intruso | **Bloqueado** — valores controlados |
| Base `_test` sin marca por *fixtures* oficiales | **Rechazado antes del DDL** |
| `personal_blog` por *fixtures* oficiales | **Rechazado antes del DDL**; base intacta |
| Obtener `Settings`/`Engine`/`Config` sin verificar por *fixtures* oficiales | **Imposible** — todas derivan del resolutor verificado |

---

## 12. Archivos modificados

### `personal-blog-backend` — 9 archivos · **`app/` sin cambios**

| Archivo | Cambio |
| --- | --- |
| `tests/__init__.py` | *M* — bootstrap hermético del proceso |
| `tests/conftest.py` | *M* — import diferido de `app.main`; `_isolated_environment` repone la URL |
| `tests/integration/conftest.py` | *M* — resolutor único verificado |
| `tests/test_configuration.py` | *M* — la guarda anti-tautología pide el dotenv de forma explícita |
| `tests/test_hermeticidad.py` | **nuevo** — regresión de `CERT-AUD-001` |
| `tests/test_grafo_de_fixtures_de_integracion.py` | **nuevo** — regresión estructural de `CERT-AUD-002` |
| `tests/integration/test_guarda_del_destino.py` | **nuevo** — regresión de comportamiento de `CERT-AUD-002` |
| `tests/integration/test_hermeticidad_de_la_integracion.py` | **nuevo** — regresión de `CERT-AUD-001-A` |
| `.editorconfig` | *M* — `*.bat`/`*.cmd` |

### `personal-blog-infra` — 13 archivos

`.editorconfig` · `README.md` · `docs/architecture/overview.md` ·
`docs/project-management/BACKEND_TESTING_STRATEGY.md` ·
`docs/project-management/STATUS.md` · `docs/project-management/WORKFLOW.md` ·
`docs/runbooks/local-environment.md` · `docs/stages/STAGE-11-deployment-automation.md` ·
`docs/task-reports/README.md` · `docs/task-reports/TASK-005-report.md` ·
`docs/tasks/TASK-005-fastapi-backend-foundation.md` ·
**nuevos:** ficha y reporte de `Task/005.7`

### `personal-blog-frontend` — 1 archivo

`.editorconfig` — sección `[*.{bat,cmd}]`. **Cambio real y necesario**: sin él,
`.gitattributes` exigía CRLF y EditorConfig imponía LF para el mismo archivo. **No se creó
`package.json`, ni `src/`, ni React, ni TypeScript, ni Vite.**

---

## 13. Seguridad

| Comprobación | Resultado |
| --- | --- |
| Contraseña real de PostgreSQL en los cambios | **No** |
| Contraseña real de MinIO en los cambios | **No** |
| Tokens `ghp_`, `github_pat_`, `xox…` | **Ninguno** |
| Claves AWS `AKIA…` | **Ninguna** |
| Claves privadas | **Ninguna** |
| `.env` real versionado | **No** — sigue ignorado |
| URLs en documentación | **Marcadores de posición** (`<usuario>`, `<clave>`, `***`) |
| `git diff --check` | Limpio en los tres repositorios |

---

## 14. Confirmaciones de alcance

| Confirmación | Estado |
| --- | --- |
| Funcionalidad de negocio nueva en el backend | **0** — `git diff -- app/` vacío |
| Frontend funcional nuevo | **0** |
| Arquitectura productiva nueva | **0** |
| Recursos cloud creados | **0** |
| Terraform, Floci, AWS, VPS, PgBouncer, Cloudflare, CI/CD | **0** |
| Avance del roadmap | **5 / 41 (12 %)** — sin cambios |
| ETAPA 02 | **1 / 3** — sin cambios |
| `Task/006` | **Pendiente, no iniciada** |
| `005.7` cuenta en las 41 | **No** |

---

## 15. Cierre aprobado

Aprobada el **2026-08-16** por jeffersondavila con la expresión
`approved: Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion`.

Flujo de cierre ejecutado en los **tres** repositorios, conforme a
[PROJECT_INSTRUCTIONS §8](../claude/PROJECT_INSTRUCTIONS.md):

| Paso | Estado |
| --- | --- |
| Aprobación registrada en ficha, reporte y STATUS | ✔ |
| **R-37** promovido de *propuesto* a **Abierto** y vigente | ✔ |
| Validaciones finales repetidas | ✔ |
| *Commit* creado en cada repositorio afectado | ✔ |
| Integración en `dev` con merge `--no-ff` | ✔ |
| `dev` publicada | ✔ |
| Rama Task publicada en `origin` | ✔ |
| Pull request **`Task/005.7 → main`** creado | ✔ |
| PR **no fusionado** — es responsabilidad exclusiva del usuario | ✔ |
| Rama Task local eliminada con `git branch -d` | ✔ |
| Rama Task remota **conservada** | ✔ |
| `Task/006` **no iniciada** | ✔ |

Los identificadores concretos —SHA de los *commits*, de los *merge* y URL de cada pull
request— se detallan en el reporte de cierre entregado al usuario. La normalización
`main → dev` se ejecuta **después** de que el usuario fusione los PR
([PROJECT_INSTRUCTIONS §10](../claude/PROJECT_INSTRUCTIONS.md)).
