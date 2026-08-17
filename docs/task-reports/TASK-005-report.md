# Reporte — TASK-005 Fundación del Backend FastAPI

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005-Fundacion-Backend-FastAPI` |
| **Etapa** | [ETAPA 02 — Fundaciones de las Aplicaciones](../stages/STAGE-02-application-foundations.md) |
| **Estado final** | **Aprobada** ✔ (2026-08-12) |
| **Fecha** | 2026-08-01 · corregido el 2026-08-11 tras la revisión · **aprobado el 2026-08-12** |
| **Repositorios modificados** | `personal-blog-backend`, `personal-blog-infra` |
| **Ficha** | [TASK-005](../tasks/TASK-005-fastapi-backend-foundation.md) |
| **Commits** | **Ninguno.** Los cambios están sin confirmar, a la espera de aprobación. |

---

## 1. Estado inicial encontrado

Verificado con Git, no supuesto.

| Repositorio | Rama activa | HEAD | Árbol |
| --- | --- | --- | --- |
| `personal-blog-infra` | `main` | `c86d47e` | Limpio |
| `personal-blog-frontend` | `main` | `144a401` | Limpio |
| `personal-blog-backend` | `main` | `76c09f5` | Limpio |

- **PR `#5`**: `MERGED`, base `main`, head `Task/004-Backups-y-Recuperacion-Local`, commit de
  merge **`c86d47e79faba2bf54720bdb4ecd5981556d3985`**, fusionado el 2026-07-31.
- **Rama `Task/004`**: no existe ni local ni remotamente. Las únicas ramas remotas de los
  tres repositorios son `origin/main` y `origin/dev`.
- **`local-backups/`**: ignorado por `.gitignore:48:local-backups/`, no aparece en
  `git status` y su contenido permanece intacto. **No se tocó.**
- El backend contenía **solo** archivos base: `README.md`, `CONTRIBUTING.md`, `.gitignore`
  y `.editorconfig`. Ningún código.

### 1.1 Normalización ejecutada

| Repositorio | Acción | Resultado |
| --- | --- | --- |
| `personal-blog-infra` | `dev` no contenía el merge `c86d47e`, aunque el contenido era idéntico. Se integró con `git merge --no-ff main` y se publicó. | `dev` = **`5f09e22`**, publicada. `git log dev..main` **vacío**; `git diff --stat main dev` **vacío**. |
| `personal-blog-frontend` | `main` y `dev` ya estaban sincronizadas (`dev..main` vacío). Solo `pull --ff-only`. | Sin cambios. `main` = `144a401`, `dev` = `8823cc3`. |
| `personal-blog-backend` | `main` y `dev` ya estaban sincronizadas (`dev..main` vacío). Solo `pull --ff-only`. | Sin cambios. `main` = `76c09f5`, `dev` = `0f94abb`. |

## 2. Ramas creadas

| Repositorio | Rama | Creada desde | Publicada |
| --- | --- | --- | --- |
| `personal-blog-backend` | `Task/005-Fundacion-Backend-FastAPI` | `dev` = `0f94abb` | **No** |
| `personal-blog-infra` | `Task/005-Fundacion-Backend-FastAPI` | `dev` = `5f09e22` (ya normalizada) | **No** |

No se creó rama en `personal-blog-frontend`: la tarea no lo modifica.
Se comprobó antes que no existía ninguna rama `Task/005` previa, local ni remota.

## 3. Qué se construyó

### 3.1 Arquitectura

Monolito modular conforme a [ADR-004](../adr/ADR-004-modular-monolith.md):

```
app/
├── main.py                    create_app() e instancia ASGI
├── api/health.py              endpoints tecnicos
├── modules/                   vacio: los modulos de negocio llegan en Task/008
└── shared/
    ├── configuration/         configuracion tipada y validada (fail-fast)
    ├── logging/               log estructurado JSON
    ├── errors/                jerarquia de errores y traduccion a HTTP
    └── database/              base declarativa, motor y sesiones
```

`shared/storage`, `shared/security` y `shared/pagination` **no se crearon**: no tendrían
contenido y las capas vacías están prohibidas (M-06). El dominio no importa FastAPI: hay
una prueba que analiza los `import` del módulo de errores y lo verifica.

### 3.2 Dependencias

Todas con versión exacta.

| Ejecución | Versión | | Desarrollo | Versión |
| --- | --- | --- | --- | --- |
| `fastapi` | 0.141.1 | | `pytest` | 9.1.1 |
| `uvicorn[standard]` | 0.52.1 | | `pytest-cov` | 7.1.0 |
| `pydantic` | 2.13.4 | | `httpx2` | 2.10.0 |
| `pydantic-settings` | 2.14.2 | | `ruff` | 0.16.1 |
| `sqlalchemy` | 2.0.51 | | `mypy` | 2.3.0 |
| `psycopg[binary]` | 3.3.4 | | | |
| `alembic` | 1.18.5 | | | |

Python **3.12** (3.12.10 en la máquina, 3.12.13 en la imagen).

Solo las **directas** están fijadas; las transitivas las resuelve `pip`. Es el riesgo
**R-14**, abierto hasta `Task/020`, y se manifestó de forma medible: la imagen del
2026-08-11 trae `starlette 1.6.0` y el entorno de Windows del 2026-08-01 tiene
`starlette 1.3.1`. Coherentemente, el `Dockerfile` instala con
`pip install -r requirements.txt`, **sin** `--require-hashes` (el archivo no lleva hashes) y
**sin** `--no-deps` (no enumera las transitivas). Ver ficha §7.1.

### 3.3 Variables de entorno

Prefijo `BLOG_`, validadas al arrancar. Una sola obligatoria: **`BLOG_DATABASE_URL`**.
El resto tiene valores por defecto seguros —`APP_DEBUG=false`, `DATABASE_ECHO=false`,
`LOG_FORMAT=json`— y `production` rechaza activar depuración o registro de SQL.
Referencia completa con valores ficticios en `.env.example`.

### 3.4 Endpoints

| Método | Ruta | Respuesta |
| --- | --- | --- |
| `GET` | `/health` | `200` · `{"status":"ok","service":"personal-blog-backend","version":"0.1.0"}` |
| `GET` | `/openapi.json` | `200` · OpenAPI 3.1.0 |
| `GET` | `/docs` | `200` · documentación interactiva |

`/health` queda fuera de `/api/v1` y no consulta dependencias. `GET /ready` es `Task/017`.

### 3.5 Errores

Modelo común de [api-contracts.md](../architecture/api-contracts.md) §7 en **todas** las
respuestas de error, con `code` estable, `message` para humanos, `details` y `request_id`.
Un fallo no previsto devuelve `500` opaco: la traza va al log, nunca al cliente.

### 3.6 PostgreSQL y migraciones

Se usa el PostgreSQL local ya aprobado (`personal-blog-local-postgres`, base
`personal_blog`). **No se creó ninguna base, ni se destruyó ningún volumen.**

La migración `0001` es fundacional: establece `alembic_version` y la cadena de revisiones
**sin crear objetos de negocio**, que corresponden a `Task/008`.

## 4. Archivos

| Repositorio | Creados | Modificados | Eliminados |
| --- | ---: | ---: | ---: |
| `personal-blog-backend` | 39 | 1 (`README.md`) | 0 |
| `personal-blog-infra` | 2 | 4 | 0 |
| **Total** | **41** | **5** | **0** |

Respecto al recuento del 2026-08-01 se suma **`tests/test_logging_utc.py`**. Los archivos
retocados el 2026-08-11 —`app/shared/logging/configuration.py`,
`app/shared/logging/__init__.py`, `requirements-dev.txt` y `pyproject.toml`— ya se contaban
como **creados** por esta tarea y siguen sin confirmar, así que no cambian de columna.

Detalle completo en la [ficha](../tasks/TASK-005-fastapi-backend-foundation.md), sección 6.

Además quedan en el directorio del backend, **ignorados por Git y sin versionar**:

| Archivo | Qué es | Por qué se conserva |
| --- | --- | --- |
| `.venv/` | Entorno virtual con las dependencias instaladas. | Permite reproducir las validaciones sin volver a instalar. Ignorado por `.gitignore`. |
| `.env` | Configuración local, con la contraseña del PostgreSQL local. | Necesario para arrancar el backend. Ignorado por `.gitignore:6`; verificado con `git check-ignore`. Se puede regenerar desde `.env.example`. |

Ninguno de los dos aparece en `git status` y ninguno se versionará.

## 5. Validaciones ejecutadas

**38 validaciones, todas ejecutadas realmente.** Resultado completo en la
[ficha](../tasks/TASK-005-fastapi-backend-foundation.md), sección 10. Resumen, con los
valores de la ejecución del **2026-08-11**:

| Bloque | Resultado |
| --- | --- |
| Instalación limpia y coherencia de dependencias | **OK** · `pip check`: `No broken requirements found.` |
| Pruebas | **69 superadas, 1 omitida, 0 fallos** (`time.tzset` no existe en Windows; en Docker se ejecutan las 70) |
| Cobertura | **99 %** — 249 sentencias, 0 sin cubrir, 1 rama parcial |
| Warnings estrictos (`-W error`) | **0 warnings y sin ningún filtro**, tanto en **Windows** como dentro de la **imagen final** — ver §5.4 |
| Lint (`ruff check`) | **`All checks passed!`** |
| Formato (`ruff format --check`) | **32 archivos ya formateados** |
| Tipado (`mypy`, modo *strict*) | **`Success: no issues found in 30 source files`** |
| Arranque real del servidor | **OK** en `127.0.0.1:8011`, log JSON unificado y **en UTC** |
| `/health`, `/openapi.json`, `/docs` | **200** los tres, contra el servidor real y contra el contenedor |
| Errores contra el servidor real | `404` `resource_not_found` · `405` `method_not_allowed`, con `request_id` |
| Migraciones por CLI | `upgrade head` → `0001 (head)` · `downgrade base` → vacío · reaplicación → `0001 (head)` |
| Construcción de la imagen | **OK** · `docker build --no-cache` · `personal-blog-backend:task005-final`, **315 MB** |
| Contenedor | **`Up (healthy)`** · usuario `uid=1001(blog)` · `HEALTHCHECK` con código 0 |
| Conexión del contenedor a PostgreSQL | **OK** · `alembic current` = `0001 (head)` desde la red `personal-blog-local-data` |
| Búsqueda de secretos | **0 credenciales nuevas** versionadas |
| Entorno local | **Intacto**: 3 servicios en marcha, 3 volúmenes presentes |

### 5.1 Prueba de que la validación fail-fast funciona

No es una afirmación teórica: al arrancar sin `BLOG_DATABASE_URL`, el proceso **abortó**
con `Configuracion invalida o incompleta -> database_url: Field required`.

### 5.2 Prueba de que la contraseña no se filtra

El log de arranque, tanto en el host como dentro del contenedor, registra:

```
"database": "postgresql://blog_local:***@personal-blog-local-postgres:5432/personal_blog"
```

Hay pruebas que verifican que la contraseña no aparece en `repr(settings)`, ni en el
mensaje de un error de configuración, ni en la salida estándar.

### 5.3 Los logs son UTC de verdad, no por casualidad

**El problema.** El formateador declaraba emitir UTC, pero construía la marca con
`logging.Formatter.formatTime`, que convierte usando `time.localtime`. El resultado dependía
del sistema operativo: en Windows salía la hora local con offset `-0600`; dentro del
contenedor salía `+0000`, pero **solo porque su entorno ya estaba en UTC**. Bastaba cambiar
la zona del host —o desplegar donde `TZ` no fuera UTC— para que el log dejara de ser
correlacionable.

**La corrección.** La conversión pasa a ser explícita en
`app/shared/logging/configuration.py`:

- `format_utc_timestamp()` construye la marca con
  `datetime.fromtimestamp(created, tz=UTC)` y devuelve siempre la forma
  **`2026-08-11T20:15:30.123Z`**: ISO 8601, milisegundos y sufijo `Z`.
- `UtcClockFormatter` define `converter = time.gmtime`, y de ella heredan tanto
  `JsonLogFormatter` como el formato de texto (`UtcTextFormatter`), que documentaba UTC y
  antes tampoco lo cumplía.

Ni la zona del sistema ni la variable `TZ` pueden desplazar el resultado.

**La prueba en Windows.** El host está en **UTC−6**. Durante el arranque real de `uvicorn`:

| Reloj | Valor |
| --- | --- |
| Hora local del host | `2026-08-11T22:56:10-06:00` |
| UTC del host | `2026-08-12T04:56:10Z` |
| Marca emitida en el log | `2026-08-12T04:56:06.894Z` |

Antes de la corrección esa línea habría dicho `2026-08-11T22:56:06-0600`.

**La prueba en Docker.** El contenedor final registró
`"timestamp": "2026-08-12T04:54:52.851Z"`, coincidente con el UTC del host.

**Las pruebas automatizadas.** `tests/test_logging_utc.py` añade **10 pruebas deterministas**
—8 funciones, una parametrizada con 3 instantes—: ninguna lee el reloj, todas fabrican un
`LogRecord` con un instante conocido. Comprueban el
valor exacto, el sufijo `Z`, la ausencia de cualquier offset, que la marca se reinterpreta
como el mismo instante, tres instantes adicionales —uno de ellos cruza de día en UTC−6—, el
formato de texto, y que `TZ` no altera el resultado. Esta última necesita `time.tzset`, que
**no existe en Windows**: allí se omite con motivo explícito y **sí se ejecuta en Docker**,
con `TZ=Pacific/Kiritimati` (UTC+14). Ninguna prueba deja cambiada la zona del proceso.

### 5.4 La advertencia de `TestClient`, resuelta en origen

La suite terminaba con `1 warning`:

```
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated;
install `httpx2` instead.
```

**Qué la causa.** Starlette la emite desde su versión 1.3 al importar
`starlette.testclient`: intenta primero `import httpx2` y, si solo encuentra el `httpx`
clásico, avisa. No la origina el código del proyecto, sino la dependencia de pruebas.

**Qué se hizo.** Sustituir la dependencia **de desarrollo** `httpx==0.28.1` por
**`httpx2==2.10.0`** en `requirements-dev.txt` y en `pyproject.toml`. Es el mismo proyecto
renombrado —`github.com/pydantic/httpx2`, autoría de Tom Christie, clasificado
*Production/Stable*—, **ningún paquete instalado dependía de `httpx`** y el código de
pruebas no lo importa: solo usa `fastapi.testclient.TestClient`. No entra en la imagen ni en
el futuro artefacto Lambda.

**Resultado.** Con las dependencias que declara el repositorio, `pytest -W error` pasa con
**69 superadas, 1 omitida, 0 warnings y ningún filtro**, en los **dos** entornos:

| Entorno | Dependencias | `pytest -W error` |
| --- | --- | --- |
| Windows 11, Python 3.12.10 | `httpx2==2.10.0`; el `httpx` clásico **desinstalado** | **69 superadas, 1 omitida, 0 warnings, código de salida 0** |
| Imagen `personal-blog-backend:task005-final` (Linux) | `httpx2==2.10.0` en el contenedor efímero | **69 superadas, 1 omitida, 0 warnings** |

En Windows la omitida es la de `TZ` (`time.tzset` no existe); en Docker es la que compara con
la hora local, porque allí el host ya opera en UTC. En ambos casos el motivo es explícito.

**Ningún warning quedó oculto.** No hay `filterwarnings` en `pyproject.toml`, ni global ni
específico, y la ejecución final no usó `-W ignore`, `PYTHONWARNINGS` ni filtro alguno. El
`.venv` de Windows quedó alineado con `requirements-dev.txt`:
`pip show httpx` → `Package(s) not found`, `pip check` → `No broken requirements found.`

## 6. Problemas encontrados

Los siete están detallados en la [ficha](../tasks/TASK-005-fastapi-backend-foundation.md),
sección 11. Los dos con consecuencia sobre el código:

1. **`.env` con BOM.** Un `.env` guardado con BOM en Windows rompía el arranque con un
   error que no señalaba la causa. La configuración pasa a leerlo con `utf-8-sig`.
2. **Puerto 8000 ocupado** por otro proyecto de la máquina, cuya API respondía a las
   comprobaciones. Se pasó al puerto 8010 y la verificación comprueba el título de OpenAPI,
   no solo el código HTTP.

Los dos detectados en la **revisión posterior**, corregidos en esta misma rama:

3. **Los logs declaraban UTC sin garantizarlo.** El formateador usaba
   `logging.Formatter.formatTime`, que convierte con `time.localtime`. En Windows emitía la
   hora local (`-0600`) y en el contenedor coincidía con UTC solo porque su entorno ya
   estaba en esa zona: el resultado dependía del sistema operativo. Ahora la conversión es
   explícita. Ver §5.3.
4. **Advertencia de `starlette.testclient`.** La suite terminaba con `1 warning`: Starlette
   1.3 exige `httpx2` en lugar del `httpx` clásico. Resuelto en origen sustituyendo la
   dependencia **de desarrollo**. Ver §5.4.

Y uno que **requiere una decisión del usuario**:

5. **El `.env` del entorno local conserva las contraseñas de ejemplo** `change-me-*`,
   publicadas en `.env.example` desde `Task/003`. No es una filtración de esta tarea, pero
   significa que las credenciales locales son públicas. Registrado como **R-16**, que
   permanece **abierto**. **No se modificó ninguna credencial ni se ejecutó ninguna
   rotación** en esta tarea.

### 6.1 Rotación de credenciales locales — procedimiento correcto

La versión anterior de este reporte afirmaba que *cambiar la contraseña de PostgreSQL exige
recrear su volumen*. **Esa afirmación era incorrecta y queda rectificada.**

PostgreSQL almacena las contraseñas como atributo de un rol existente: rotarlas **no**
requiere eliminar el volumen, ni la base, ni recrear el contenedor. Cuando el usuario decida
hacerlo, el procedimiento es:

1. **Verificar que existe un backup recuperable**, conforme al
   [runbook de backup](../runbooks/local-backup-and-recovery.md). Es una precaución, no un
   requisito del cambio.
2. **Generar una contraseña nueva**, distinta del marcador publicado.
3. **Cambiar la contraseña del rol existente**, conceptualmente:
   `ALTER ROLE <rol> WITH PASSWORD '<nueva-clave>';`
4. **Actualizar el `.env` local de forma coordinada**, en el mismo momento.
5. **Reiniciar o reconectar los consumidores** (backend local, contenedor del backend,
   clientes abiertos): las conexiones ya establecidas siguen vivas hasta reconectar.
6. **Validar el acceso con la credencial nueva.**
7. **Confirmar que la credencial anterior ya no funciona.**

Lo que **no** hace falta: eliminar el volumen, eliminar la base de datos ni recrear
PostgreSQL. No hay pérdida de datos.

> **MinIO se trata por separado.** Su credencial raíz procede de variables de entorno del
> contenedor (`MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`), no de un rol almacenado dentro del
> servicio, de modo que **su rotación no sigue este procedimiento**. Documentarla exige una
> comprobación propia que no forma parte del alcance de `Task/005`.

Ninguno de estos pasos se ejecutó en esta tarea: **no se cambió ninguna credencial real y no
se muestra ninguna contraseña en la documentación.**

## 7. Riesgos

| # | Riesgo | Estado |
| --- | --- | --- |
| R-14 | **Nuevo.** Las dependencias transitivas no están bloqueadas con hashes. **Confirmado con un caso real:** `starlette 1.6.0` en la imagen frente a `1.3.1` en Windows. | Abierto — `Task/020` |
| R-15 | **Nuevo.** La imagen base `python:3.12.13-slim` envejece. | Abierto — `Task/018`, `Task/020` |
| R-16 | **Nuevo.** El `.env` local conserva las contraseñas de ejemplo publicadas. La rotación en PostgreSQL **no destruye datos** (§6.1); MinIO exige otro procedimiento. **No se ejecutó ninguna rotación.** | Abierto — decisión del usuario |
| R-03 | Compatibilidad del patrón de conexión con Lambda. | Abierto — `Task/029` |
| Resto | Riesgos vigentes de tareas anteriores. | Sin cambios |

## 8. Deuda técnica

`/ready`, correlation ID completo, bloqueo de dependencias, escaneo de vulnerabilidades,
CI, estrategia de pooling y CORS. Cada elemento con su tarea asignada en la
[ficha](../tasks/TASK-005-fastapi-backend-foundation.md), sección 13.

## 9. Pasos de validación para el usuario

Con el entorno local de `personal-blog-infra` en marcha:

```powershell
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-backend

# 1. Rama y estado
git branch --show-current          # Task/005-Fundacion-Backend-FastAPI
git status --porcelain -b          # cambios sin confirmar; .env y .venv NO aparecen

# 2. Entorno y dependencias
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check

# 3. Configuracion local (la contrasena es la del .env de personal-blog-infra)
Copy-Item .env.example .env
# edita .env y ajusta BLOG_DATABASE_URL

# 4. Calidad
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy

# 5. Pruebas (con integracion)
#
# ⚠️ HISTÓRICO — NO EJECUTAR ESTA LÍNEA CONTRA LA BASE DE DESARROLLO.
# La línea de abajo apunta a `personal_blog`, tal y como se escribió en Task/005.
# La política vigente desde Task/005.6 exige `personal_blog_test`, con la marca
# `personal-blog:test-database`, y la guarda fail-closed RECHAZA hoy este destino.
# Comando vigente: runbook local-environment.md §9.4.
$env:PERSONAL_BLOG_TEST_DATABASE_URL = "postgresql://blog_local:<clave>@127.0.0.1:55432/personal_blog"
.\.venv\Scripts\python.exe -m pytest --cov

# 5b. Warnings estrictos: debe terminar con 0 warnings y sin ningun filtro.
#     El paso 2 ya instala httpx2, que es lo que exige starlette.testclient.
.\.venv\Scripts\python.exe -m pytest -W error

# 6. Migraciones
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic upgrade head

# 7. Servidor (el puerto 8000 puede estar ocupado por otro proyecto)
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
# en otra terminal:
#   Invoke-WebRequest http://127.0.0.1:8010/health -UseBasicParsing
#   y abre http://127.0.0.1:8010/docs

# 8. Imagen y contenedor (construccion limpia, sin reutilizar capas)
docker build --no-cache -t personal-blog-backend:task005-final .
docker run -d --name prueba-backend `
  --network personal-blog-local-data -p 127.0.0.1:8010:8000 `
  -e "BLOG_DATABASE_URL=postgresql://blog_local:<clave>@personal-blog-local-postgres:5432/personal_blog" `
  personal-blog-backend:task005-final
docker ps --filter name=prueba-backend      # debe decir (healthy)
docker exec prueba-backend id               # uid=1001(blog)
docker logs prueba-backend | Select-Object -First 1   # el timestamp termina en Z
docker rm -f prueba-backend

# 9. El entorno principal sigue intacto
docker compose -f ..\personal-blog-infra\docker-compose.yml ps
docker volume ls --filter name=personal-blog-local
```

Ninguno de estos comandos es destructivo. El paso 8 crea y elimina un contenedor
**temporal**; no toca los volúmenes ni los contenedores del entorno principal.

## 10. Límites respetados

Durante la ejecución, **hasta recibir la aprobación**:

| Límite | Cumplimiento |
| --- | --- |
| Sin commits antes de `approved:` | **Cumplido.** Los cambios permanecieron en el árbol de trabajo hasta el 2026-08-12. |
| Sin merge | **Cumplido.** Salvo la normalización `main → dev` en infra, previa a la tarea y exigida por el workflow. |
| Sin push de la rama Task | **Cumplido.** Ninguna rama `Task/005` existió en `origin` antes del cierre. |
| Sin pull request | **Cumplido.** |
| Sin modificar `main` | **Cumplido.** |
| Sin recursos cloud | **Cumplido.** Ninguna cuenta, ningún recurso, ningún archivo Terraform. |
| Sin secretos versionados | **Cumplido.** Solo marcadores ficticios. |
| Sin operaciones destructivas | **Cumplido.** Ni `down -v`, ni `volume rm`, ni `prune`, ni `git clean`, ni `reset --hard`. |
| `local-backups/` intacto | **Cumplido.** No se leyó, movió ni versionó. |
| Sin marcar `Aprobada` por iniciativa propia | **Cumplido.** El estado cambió solo tras `approved: Task/005-Fundacion-Backend-FastAPI`. |
| `Task/006`, `Task/007`, `Task/008` no iniciadas | **Cumplido.** Ninguna rama las referencia. |

### 10.1 Cierre aprobado (2026-08-12)

Ejecutado tras la autorización explícita del usuario, conforme a
[WORKFLOW.md](../project-management/WORKFLOW.md) §3: commits en la rama Task, integración en
`dev` con merge `--no-ff`, publicación de `dev` y de la rama Task, y pull request
`Task/005-Fundacion-Backend-FastAPI → main` en cada repositorio afectado.

**El pull request no se fusionó:** aceptarlo es responsabilidad exclusiva del usuario. La
rama Task local se eliminó con `git branch -d`; la remota se conserva mientras el PR siga
abierto.

## 11. Próxima tarea

`Task/006-Fundacion-Frontend-React`, en `personal-blog-frontend`. **No se inicia** hasta que
el usuario fusione el pull request de `Task/005` y se complete la normalización
`main → dev` en los repositorios afectados.

---

## 12. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** ✔ |
| **Fecha de aprobación** | 2026-08-12 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005-Fundacion-Backend-FastAPI` |
| **Pull request** | `Task/005-Fundacion-Backend-FastAPI → main` en `personal-blog-backend` y en `personal-blog-infra` — **abiertos, sin fusionar** |

La fusión hacia `main` es responsabilidad exclusiva del usuario.
