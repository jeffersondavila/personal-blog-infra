# TASK-005 — Fundación del Backend FastAPI

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/005-Fundacion-Backend-FastAPI` |
| **Nombre** | Fundación del Backend FastAPI |
| **Etapa** | [ETAPA 02 — Fundaciones de las Aplicaciones](../stages/STAGE-02-application-foundations.md) |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-backend` (implementación) · `personal-blog-infra` (gobierno documental) |
| **Dependencias** | `Task/004-Backups-y-Recuperacion-Local` — **Aprobada** ✔ (2026-07-31) |
| **Rama** | `Task/005-Fundacion-Backend-FastAPI`, creada desde `dev` en ambos repositorios |
| **Fecha de inicio** | 2026-08-01 |
| **Fecha de aprobación** | 2026-08-12 |
| **Última actualización** | 2026-08-12 — cierre aprobado |

---

## 1. Objetivo

Establecer la base profesional del backend: un proyecto FastAPI reproducible que arranca,
expone un healthcheck y una especificación OpenAPI, lee su configuración de variables de
entorno, registra logs estructurados, traduce sus errores a un modelo común, **se conecta
al PostgreSQL local** y gestiona el esquema con Alembic, con pruebas, lint, formato,
tipado estático e imagen Docker verificados.

Es el **primer código de aplicación del proyecto**: define la estructura sobre la que se
construirán todos los módulos de negocio.

## 2. Contexto

Con la ETAPA 01 completada, el entorno local es reproducible y recuperable, pero **no hay
ninguna aplicación**. `Task/005` abre la ETAPA 02.

La estructura de proyecto, el manejo de configuración y la estrategia de pruebas son
difíciles de cambiar una vez que hay dominio construido encima
([STAGE-02](../stages/STAGE-02-application-foundations.md)): por eso se fijan antes que las
funcionalidades.

`Task/006` hará lo propio con el frontend y `Task/007` integrará ambos con la
infraestructura local.

## 3. Dentro del alcance

- [x] Crear la rama `Task/005` desde `dev` en `personal-blog-backend` y en
      `personal-blog-infra`.
- [x] Proyecto Python 3.12 reproducible, con gestión explícita de dependencias y versiones
      fijadas.
- [x] Estructura de **monolito modular** conforme a
      [ADR-004](../adr/ADR-004-modular-monolith.md), sin capas vacías.
- [x] Punto de entrada de la aplicación (`create_app()` e instancia ASGI).
- [x] Configuración **tipada** por variables de entorno, con validación fail-fast.
- [x] `.env.example` con valores ficticios y sin secretos reales.
- [x] Log **estructurado en JSON**, unificado con el del servidor.
- [x] Manejo **centralizado** de errores con el modelo común de
      [api-contracts.md](../architecture/api-contracts.md), sección 7.
- [x] Endpoint de salud `GET /health`.
- [x] OpenAPI funcional y documentación interactiva.
- [x] Acceso a PostgreSQL con SQLAlchemy 2: base declarativa, motor y sesiones.
- [x] Alembic configurado, con la URL fuera del archivo versionado.
- [x] Migración fundacional, aplicada y revertida contra la base de datos real.
- [x] Suite de pruebas automatizadas, unitarias y de integración.
- [x] Linter, formateador y verificación de tipos configurados y ejecutados.
- [x] `Dockerfile`, imagen construida y contenedor ejecutado y comprobado.
- [x] Documentación de desarrollo en el README del backend.
- [x] Actualizar la documentación de gestión afectada en `personal-blog-infra`.

## 4. Fuera del alcance

| Elemento | Motivo o tarea |
| --- | --- |
| Modelo de datos del blog | `Task/008`. La migración fundacional no crea tablas de negocio. |
| Endpoints de contenido y esquemas de petición y respuesta | `Task/009`, `Task/012`. |
| `GET /ready` (comprobación de dependencias) | Requisito O-04, `Task/017`. |
| Correlation ID propagado por cabecera a todos los logs | Requisito O-02, `Task/017`. |
| Interfaz `ObjectStorage` e integración con MinIO | `Task/010`. |
| Autenticación, usuarios, roles, auditoría | `Task/011`. |
| Paginación (`shared/pagination`) | `Task/009`. |
| CORS configurado | `Task/007` lo necesita; se endurece en `Task/018` y `Task/033`. |
| Backend en el Docker Compose, Traefik, flujo frontend → backend | `Task/007`. |
| Adaptador Lambda y artefacto ZIP | `Task/023`, `Task/024`. |
| Estrategia definitiva de pooling para Lambda | `Task/029` (riesgo R-03). |
| CI (lint, tipos, pruebas y build automatizados) | `Task/020`. |
| Bloqueo de dependencias con hashes resuelto en Linux | `Task/020`. |
| Cualquier recurso cloud, cuenta o Terraform | Etapas 08 a 10. |

**Prohibiciones explícitas de esta tarea, todas respetadas:**

- **No crear ningún recurso cloud** ni cuenta en ningún proveedor.
- **No versionar ningún secreto real.**
- **No ejecutar operaciones destructivas** sobre el entorno local (`docker compose down -v`,
  `docker volume rm`, `docker system prune`, `docker volume prune`).
- **No iniciar `Task/006`, `Task/007` ni `Task/008`.**

## 5. Arquitectura aplicable

| Documento | Qué impone |
| --- | --- |
| [ADR-004](../adr/ADR-004-modular-monolith.md) | Monolito modular, división por dominio, sin capas vacías, dominio sin framework. |
| [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md) | Destino Lambda: sin estado en memoria, sin procesos residentes, conexiones efímeras. |
| [ADR-005](../adr/ADR-005-markdown-content.md) | Contenido en Markdown. Sin efecto en esta tarea: no hay contenido todavía. |
| [software-architecture.md](../architecture/software-architecture.md) | `app/modules` + `app/shared`; configuración por entorno validada al arrancar. |
| [api-contracts.md](../architecture/api-contracts.md) | `/health` sin dependencias; modelo común de error con `request_id`; JSON UTF-8; `/api/v1` como prefijo del contrato. |
| [security-boundaries.md](../architecture/security-boundaries.md) | PostgreSQL solo accesible desde el backend; ningún secreto en Git. |
| [non-functional-requirements.md](../architecture/non-functional-requirements.md) | S-07, S-08, S-10, P-06, O-01, O-03, T-01, T-02, T-04, M-01, M-02, M-04, M-06. |

### 5.1 Estructura implementada

```
app/
├── main.py                    create_app() e instancia ASGI
├── api/
│   └── health.py              endpoints tecnicos
├── modules/                   vacio: los modulos de negocio llegan en Task/008
└── shared/
    ├── configuration/         configuracion tipada y validada
    ├── logging/               log estructurado JSON
    ├── errors/                jerarquia de errores y traduccion a HTTP
    └── database/              base declarativa, motor y sesiones
```

`shared/storage`, `shared/security` y `shared/pagination` **no se crean**: no tendrían
contenido y las capas vacías están prohibidas (M-06).

## 6. Entregables

| Entregable | Repositorio | Ruta | Acción |
| --- | --- | --- | --- |
| Metadatos, dependencias y configuración de herramientas | backend | `pyproject.toml` | Creado |
| Dependencias de ejecución | backend | `requirements.txt` | Creado |
| Dependencias de desarrollo | backend | `requirements-dev.txt` | Creado |
| Paquete de la aplicación | backend | `app/__init__.py` | Creado |
| Punto de entrada | backend | `app/main.py` | Creado |
| Router técnico | backend | `app/api/__init__.py` | Creado |
| Endpoint de salud | backend | `app/api/health.py` | Creado |
| Límite de los módulos de negocio | backend | `app/modules/__init__.py` | Creado |
| Paquete compartido | backend | `app/shared/__init__.py` | Creado |
| Configuración tipada | backend | `app/shared/configuration/{__init__,settings}.py` | Creado |
| Log estructurado | backend | `app/shared/logging/{__init__,configuration}.py` | Creado |
| Errores y su traducción a HTTP | backend | `app/shared/errors/{__init__,exceptions,handlers}.py` | Creado |
| Acceso a datos | backend | `app/shared/database/{__init__,base,session}.py` | Creado |
| Configuración de Alembic | backend | `alembic.ini` | Creado |
| Entorno de Alembic | backend | `alembic/env.py` | Creado |
| Plantilla de migración | backend | `alembic/script.py.mako` | Creado |
| Migración fundacional | backend | `alembic/versions/20260801_0001_baseline_del_esquema.py` | Creado |
| Pruebas | backend | `tests/` (12 archivos, incluidos `integration/`) | Creado |
| Pruebas del reloj del log | backend | `tests/test_logging_utc.py` | Creado |
| Variables de ejemplo | backend | `.env.example` | Creado |
| Imagen del servicio | backend | `Dockerfile` | Creado |
| Exclusiones del contexto de build | backend | `.dockerignore` | Creado |
| Documentación de desarrollo | backend | `README.md` | Modificado |
| Ficha de esta tarea | infra | `docs/tasks/TASK-005-fastapi-backend-foundation.md` | Creado |
| Reporte de esta tarea | infra | `docs/task-reports/TASK-005-report.md` | Creado |
| Estado del proyecto | infra | `docs/project-management/STATUS.md` | Modificado |
| Roadmap | infra | `docs/project-management/ROADMAP.md` | Modificado |
| Ficha de la Etapa 02 | infra | `docs/stages/STAGE-02-application-foundations.md` | Modificado |
| Índice de reportes | infra | `docs/task-reports/README.md` | Modificado |

**41 creados · 5 modificados · 0 eliminados** — 39 creados y 1 modificado en
`personal-blog-backend`; 2 creados y 4 modificados en `personal-blog-infra`.

Ningún archivo se contabiliza dos veces: los corregidos el 2026-08-11
(`app/shared/logging/configuration.py`, `app/shared/logging/__init__.py`,
`requirements-dev.txt`, `pyproject.toml`) ya figuraban como **creados** por esta misma
tarea y siguen sin confirmar.

## 7. Decisiones técnicas

| # | Decisión | Alternativas consideradas | Justificación | ¿ADR? |
| --- | --- | --- | --- | --- |
| 1 | **Python 3.12**, fijado en `requires-python`. | 3.11; 3.13. | Es la versión instalada en la máquina de desarrollo y una de las soportadas por el *runtime* de AWS Lambda. Fijarla evita que la CI y el contenedor usen otra. | No |
| 2 | **SQLAlchemy síncrono** con **psycopg 3**. | SQLAlchemy asíncrono con `asyncpg`. | En Lambda una invocación atiende una petición: la asincronía no aporta concurrencia real y complica el código y las pruebas. Revisable si el modelo de ejecución cambia. | No |
| 3 | **`pydantic-settings`** para la configuración. | Leer `os.environ` a mano; `dynaconf`. | Da tipado, validación y mensajes de error en un solo sitio, y ya viene con Pydantic, que FastAPI arrastra. | No |
| 4 | **Prefijo `BLOG_`** en todas las variables. | Nombres sin prefijo. | Evita colisiones con variables del sistema y de otros proyectos, y hace evidente en el `.env` qué pertenece al backend. | No |
| 5 | **`extra="forbid"`** en la configuración. | Ignorar variables desconocidas. | Una variable mal escrita se convierte en un fallo de arranque en lugar de en un valor por defecto silencioso. | No |
| 6 | **`env_file_encoding="utf-8-sig"`**. | `utf-8`. | En Windows es habitual guardar el `.env` con BOM; con `utf-8` el BOM se pega al nombre de la primera variable. Se materializó durante la tarea (problema 1). | No |
| 7 | **`/health` fuera de `/api/v1`**. | `/api/v1/health`. | El prefijo versiona el contrato de datos con el frontend; la sonda la consume la plataforma y no debe cambiar de ruta al pasar a `v2`. [api-contracts.md](../architecture/api-contracts.md) §2 la lista aparte de los recursos versionados. | No |
| 8 | **`/health` no consulta la base de datos.** | Comprobar PostgreSQL en `/health`. | Un healthcheck que consulta la base reinicia el contenedor cuando el problema está en la base. La comprobación de dependencias es `/ready` (O-04, `Task/017`). | No |
| 9 | **Migración fundacional sin objetos.** | Crear ya tablas técnicas o parte del modelo. | El modelo de datos es `Task/008`; crear tablas aquí sería trabajo desechable. La migración establece `alembic_version` y la cadena de revisiones, y el ciclo `upgrade`/`downgrade`/reaplicación se verifica igualmente (M-04). | No |
| 10 | **La URL de la base de datos no vive en `alembic.ini`.** | Declararla en el `.ini`. | `alembic.ini` se versiona y la URL lleva la contraseña. `env.py` la obtiene de la configuración de la aplicación (S-10). | No |
| 11 | **Convención de nombres en `MetaData`.** | Nombres implícitos de PostgreSQL. | Sin ella, los índices y restricciones reciben nombres generados y los `downgrade` no saben qué borrar: las migraciones dejarían de ser reversibles (M-04). | No |
| 12 | **Sin middleware de CORS.** | Configurarlo ya con `localhost`. | Ningún navegador consume esta API todavía. No configurarlo es lo seguro: el navegador deniega por defecto y `*` está prohibido (S-04). Se define por ambiente en `Task/007` y se endurece en `Task/018`. | No |
| 13 | **`request_id` generado en el manejador de error.** | Middleware completo de correlación. | El modelo común de error exige `request_id` desde ya; la propagación por cabecera a **todos** los logs de la petición es O-02 y corresponde a `Task/017`. | No |
| 14 | **Log JSON con la biblioteca estándar.** | `structlog`; `python-json-logger`. | Un formateador de 40 líneas cubre el requisito O-01 sin añadir una dependencia al artefacto que acabará en Lambda. | No |
| 15 | **Uvicorn queda bajo el mismo formateador.** | Dejar el formato propio de uvicorn. | Con dos formatos, la mitad de las líneas no son parseables y el requisito O-01 queda a medias. | No |
| 16 | **`ruff` para lint y formato**; `mypy` en modo *strict*. | `black` + `flake8` + `isort`. | Una sola herramienta para lint y formato, ya fijada en `CONTRIBUTING.md`. `strict` es exigible en un proyecto que empieza de cero (M-02). | No |
| 17 | **Pruebas de integración que se omiten sin base de datos.** | Fallar; o no tenerlas. | La suite debe poder ejecutarse sin Docker. Se omiten con motivo explícito, nunca se declaran superadas sin ejecutarse. | No |
| 18 | **`requirements.txt` además de `pyproject.toml`.** | Solo `pyproject.toml`. | El Dockerfile instala desde `requirements.txt` sin necesitar el proyecto completo, y la capa se reaprovecha entre construcciones. | No |
| 19 | **Imagen multi-etapa, usuario no root, versión de parche fija.** | Imagen única; `python:3.12-slim`. | Menor superficie, sin herramientas de construcción en la imagen final, y una etiqueta móvil cambiaría de parche sin aviso (misma regla que el Compose de infra). | No |
| 20 | **`HEALTHCHECK` con la biblioteca estándar de Python.** | Instalar `curl` o `wget`. | Añadir un binario solo para la sonda amplía la superficie de ataque de la imagen. | No |
| 21 | **UTC explícito en el log**, con `datetime.fromtimestamp(created, tz=UTC)` y `converter = time.gmtime`. | Dejar `formatTime` como estaba; fijar `TZ=UTC` en el contenedor. | `formatTime` convierte con `time.localtime`: el mismo código emitía `-0600` en Windows y `+0000` en Docker. Fijar `TZ` solo arreglaría el contenedor y dejaría el desarrollo en hora local; además, una variable de entorno no es una garantía del código. | No |
| 22 | **`httpx2==2.10.0` sustituye a `httpx` como dependencia de pruebas.** | Seguir con `httpx` y silenciar el aviso; esperar a `Task/020`. | Desde Starlette 1.3, `starlette.testclient` pide `httpx2` y avisa con `StarletteDeprecationWarning`. Es el mismo proyecto renombrado (`github.com/pydantic/httpx2`, *Production/Stable*), solo se usa en las pruebas y no entra ni en la imagen ni en el artefacto Lambda. Resolverlo en origen evita normalizar un warning silenciado. | No |
| 23 | **`pip install -r requirements.txt` en el Dockerfile, sin `--require-hashes` ni `--no-deps`.** | Instalar con hashes y sin resolución de dependencias. | `requirements.txt` fija solo las **directas** con `==` y **no contiene hashes**: `--require-hashes` fallaría y `--no-deps` dejaría la imagen sin las transitivas. La instalación coherente con el archivo real es la simple; el bloqueo con hashes llega con `Task/020` (R-14, abierto). | No |

**No se creó ningún ADR.** Ninguna de estas decisiones altera la arquitectura acordada:
todas son de implementación y reversibles dentro del marco de ADR-003 y ADR-004.

### 7.1 Política de dependencias vigente

| Ámbito | Cómo se declara | Cómo se instala |
| --- | --- | --- |
| Ejecución | `requirements.txt` y `[project].dependencies`, **directas fijadas con `==`**, sin hashes. | Imagen: `pip install -r requirements.txt` (con `PIP_NO_CACHE_DIR=1`). pip resuelve las transitivas. |
| Desarrollo | `requirements-dev.txt` y `[project.optional-dependencies].dev`, también con `==`. | `pip install -r requirements-dev.txt`. No entra en la imagen. |

Las **transitivas no están bloqueadas**: es exactamente el riesgo **R-14**, que permanece
**abierto** y se cierra en `Task/020`. La construcción del 2026-08-11 lo hizo visible: la
imagen resolvió `starlette 1.6.0` mientras el entorno de Windows, instalado días antes,
tiene `starlette 1.3.1`. La misma declaración produjo dos versiones indirectas distintas.

Mientras R-14 siga abierto, el Dockerfile **no debe** usar `--require-hashes` (el archivo no
tiene hashes) ni `--no-deps` (el archivo no enumera las transitivas).

## 8. Criterios de aceptación

| # | Criterio | Estado |
| --- | --- | --- |
| 1 | Las dependencias se instalan en un entorno limpio y son coherentes entre sí. | Cumplido — validaciones 1 y 2 |
| 2 | La aplicación se importa y construye sin errores. | Cumplido — validación 3 |
| 3 | El servidor arranca realmente. | Cumplido — validación 10 |
| 4 | `GET /health` devuelve `200` y el cuerpo esperado. | Cumplido — validaciones 6 y 11 |
| 5 | `/health` no expone entorno ni detalles internos. | Cumplido — validación 6 |
| 6 | La especificación OpenAPI se genera y documenta el endpoint. | Cumplido — validaciones 7 y 12 |
| 7 | La configuración falla rápido si falta una variable obligatoria. | Cumplido — validaciones 4 y 20 |
| 8 | La contraseña de la base de datos no aparece en logs, `repr` ni mensajes de error. | Cumplido — validaciones 4, 8 y 18 |
| 9 | Los errores usan el modelo común con `request_id`. | Cumplido — validaciones 5, 13 y 14 |
| 10 | Un fallo no previsto devuelve `500` sin trazas ni nombres internos. | Cumplido — validación 5 |
| 11 | El backend se conecta al PostgreSQL local. | Cumplido — validación 9 |
| 12 | `alembic upgrade head` aplica la migración fundacional. | Cumplido — validaciones 9 y 15 |
| 13 | `alembic downgrade base` la revierte y la reaplicación funciona. | Cumplido — validaciones 9 y 15 |
| 14 | La migración fundacional no crea tablas de negocio. | Cumplido — validación 9 |
| 15 | La suite de pruebas pasa por completo. | Cumplido — validación 9 |
| 16 | `ruff check` sin errores. | Cumplido — validación 21 |
| 17 | `ruff format --check` sin cambios pendientes. | Cumplido — validación 22 |
| 18 | `mypy` en modo *strict* sin errores. | Cumplido — validación 23 |
| 19 | La imagen Docker se construye. | Cumplido — validación 16 |
| 20 | El contenedor arranca, responde y su `HEALTHCHECK` pasa. | Cumplido — validaciones 17 y 19 |
| 21 | El contenedor ejecuta como usuario sin privilegios. | Cumplido — validación 17 |
| 22 | El contenedor se conecta a PostgreSQL por la red de Docker. | Cumplido — validación 18 |
| 23 | No hay secretos reales en archivos versionados. | Cumplido — validación 24 |
| 24 | `.env` real ignorado por Git. | Cumplido — validación 25 |
| 25 | El entorno local principal queda intacto. | Cumplido — validación 27 |
| 26 | Frontend sin cambios y sin rama `Task/005`. | Cumplido — validación 28 |
| 27 | Cero recursos cloud y cero archivos Terraform. | Cumplido — validación 29 |
| 28 | La tarea queda `Lista para validación`, nunca `Aprobada` por decisión propia. | Cumplido |
| 29 | `Task/006`, `Task/007` y `Task/008` no se inician. | Cumplido — validación 30 |
| 30 | Las marcas de tiempo del log son **UTC reales** en Windows y en Docker, con independencia de la zona del host y de `TZ`. | Cumplido — validaciones 31, 32 y 33 |
| 31 | La imagen se construye **sin cache** y su instalación de dependencias es coherente con lo que `requirements.txt` declara. | Cumplido — validación 34 |
| 32 | La suite no oculta advertencias: pasa con `-W error`, 0 warnings y sin ningún filtro, en Windows y dentro de la imagen final. | Cumplido — validaciones 35 y 36 |

## 9. Comandos de validación

```powershell
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-backend

# Entorno y dependencias
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip check

# Calidad
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy

# Pruebas (la integración necesita PostgreSQL en marcha)
$env:PERSONAL_BLOG_TEST_DATABASE_URL = "postgresql://<usuario>:<clave>@127.0.0.1:55432/personal_blog"
.\.venv\Scripts\python.exe -m pytest --cov --cov-report=term-missing

# Warnings estrictos: ninguna advertencia desconocida puede pasar inadvertida
.\.venv\Scripts\python.exe -m pytest -W error

# Migraciones
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic downgrade base
.\.venv\Scripts\python.exe -m alembic upgrade head

# Servidor
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010

# Imagen y contenedor (construcción sin cache: nada se reaprovecha)
docker build --no-cache -t personal-blog-backend:task005-final .
docker run -d --name personal-blog-backend-task005-final-check `
  --network personal-blog-local-data -p 127.0.0.1:8010:8000 `
  -e "BLOG_DATABASE_URL=postgresql://<usuario>:<clave>@personal-blog-local-postgres:5432/personal_blog" `
  personal-blog-backend:task005-final
docker exec personal-blog-backend-task005-final-check id
docker exec personal-blog-backend-task005-final-check alembic current
docker rm -f personal-blog-backend-task005-final-check   # solo el contenedor temporal

# Git
git status --porcelain -b
git check-ignore -v .env
git diff --check
```

## 10. Resultado de las validaciones

Ejecutadas el 2026-08-01 sobre Windows 11, Python 3.12.10, Docker 29.1.3 y Docker Compose
v5.0.1, contra el entorno local de `personal-blog-infra` en marcha.
**Ninguna validación se declara sin haberse ejecutado.**

Las validaciones **1 a 30** son las de la ejecución original. Las marcadas *(2026-08-11)* se
**repitieron** tras las correcciones de la revisión; las **31 a 38** son nuevas.

| # | Validación | Resultado real |
| --- | --- | --- |
| 1 | Instalación limpia de dependencias | **OK.** Entorno virtual nuevo; 7 paquetes directos de ejecución y 5 de desarrollo instalados con sus transitivas. |
| 2 | Coherencia de dependencias (`pip check`) | **`No broken requirements found.`** |
| 3 | Importación y construcción de la aplicación | **OK.** `create_app()` se ejecuta al importar `app.main`. |
| 4 | Configuración fail-fast | **Verificada realmente**: sin `BLOG_DATABASE_URL` el arranque falla con `Configuracion invalida o incompleta -> database_url: Field required`. |
| 5 | Manejo de errores | 10 pruebas: modelo común en 404, 405, 422, 409, 503 y 500; `500` sin traza, sin `RuntimeError` y sin el texto interno; `request_id` distinto en cada respuesta. |
| 6 | `GET /health` | **200** con `{"status":"ok","service":"personal-blog-backend","version":"0.1.0"}`. Solo esas tres claves. |
| 7 | OpenAPI | **200**, `openapi 3.1.0`, título y versión correctos, `paths` = `['/health']`. `/docs` responde **200**. |
| 8 | Log estructurado | 10 pruebas: JSON válido por línea, contexto aparte, excepción incluida, valores no serializables no rompen el formato, `configure_logging` idempotente. |
| 9 | Suite completa con cobertura *(2026-08-11)* | **69 pruebas superadas, 1 omitida, 0 fallos.** Cobertura **99 %** (249 sentencias, 0 sin cubrir; 1 rama parcial). Incluye las 8 de integración contra PostgreSQL real. La omitida es la de `TZ`, que necesita `time.tzset` y **no existe en Windows**; sí se ejecuta en Docker (validación 33). |
| 10 | Arranque real del servidor | **OK.** `uvicorn` en `127.0.0.1:8010`; log JSON unificado con el del servidor. |
| 11 | Endpoints contra el servidor real | `/health` **200**; `/docs` **200**; `/no-existe` **404** con `resource_not_found`; `POST /health` **405** con `method_not_allowed`. |
| 12 | OpenAPI del servidor real | **200**, un único path `/health`. |
| 13 | `request_id` correlacionado | El `request_id` del cuerpo de error (`d3b31fa4-…`) aparece en la línea de log correspondiente. |
| 14 | Ausencia de filtración en errores | Ni trazas, ni SQL, ni rutas, ni nombres de clase en ninguna respuesta. |
| 15 | Ciclo de migraciones por CLI | `upgrade head` → `current` = **`0001 (head)`**; `downgrade base` → `current` **vacío**; `upgrade head` → **`0001 (head)`** de nuevo. |
| 16 | Construcción de la imagen *(2026-08-11)* | **OK.** `docker build --no-cache -t personal-blog-backend:task005-final .` — **315 MB**, base `python:3.12.13-slim`, Python **3.12.13**. Ver validación 34. |
| 17 | Ejecución del contenedor *(2026-08-11)* | **`Up (healthy)`**. `id` dentro del contenedor: **`uid=1001(blog) gid=1001(blog)`** — sin privilegios. Python **3.12.13**. |
| 18 | Conexión del contenedor a PostgreSQL *(2026-08-11)* | **OK.** `alembic current` dentro del contenedor devuelve **`0001 (head)`** conectando a `personal-blog-local-postgres:5432` por la red `personal-blog-local-data`. |
| 19 | `HEALTHCHECK` de Docker *(2026-08-11)* | **`healthy`**, código de salida **0**. |
| 20 | Log del contenedor *(2026-08-11)* | JSON, con la URL **enmascarada**: `postgresql://blog_local:***@personal-blog-local-postgres:5432/personal_blog`. |
| 21 | `ruff check` *(2026-08-11)* | **`All checks passed!`** |
| 22 | `ruff format --check` *(2026-08-11)* | **`32 files already formatted`**. |
| 23 | `mypy` (modo *strict*) *(2026-08-11)* | **`Success: no issues found in 30 source files`**. |
| 24 | Búsqueda de secretos | **0 credenciales nuevas** en archivos versionados de los dos repositorios. Las únicas coincidencias son los marcadores ficticios `change-me-*`, ya versionados desde `Task/003`. **Observación:** el `.env` real del entorno local **conserva esos mismos valores de ejemplo** — ver §11, problema 7. |
| 25 | `.env` real ignorado | `git check-ignore -v .env` → `.gitignore:6:.env`. No aparece en `git status`. |
| 26 | `git diff --check` | **Sin errores** de espacios en blanco en ninguno de los dos repositorios. En el backend Git emite el aviso habitual de Windows `LF will be replaced by CRLF` sobre `README.md`; es una advertencia de normalización de finales de línea, preexistente y sin efecto sobre el contenido. |
| 27 | Entorno local principal | **Intacto.** `postgres` y `minio` **healthy**, `portainer` up; **3 de 3 volúmenes** presentes. Solo se eliminó el contenedor temporal creado por la prueba. |
| 28 | Frontend | **Sin cambios.** En `main`, árbol limpio, sin rama `Task/005`. |
| 29 | Recursos cloud y Terraform | **Ninguno.** Sin cuentas, sin llamadas a AWS ni Cloudflare, sin archivos `*.tf`. |
| 30 | `Task/006`, `Task/007`, `Task/008` | **No iniciadas.** Ninguna rama las referencia. |
| 31 | **Log en UTC — Windows** *(nueva)* | **OK.** Host en **UTC−6**: hora local `2026-08-11T22:56:10-06:00`. El arranque real de `uvicorn` registró `"timestamp": "2026-08-12T04:56:06.894Z"`. Es **UTC real**, no la hora local. |
| 32 | **Log en UTC — contenedor** *(nueva)* | **OK.** El contenedor final registró `"timestamp": "2026-08-12T04:54:52.851Z"`, coincidente con el UTC del host en ese momento. |
| 33 | **Pruebas de UTC deterministas** *(nueva)* | **10 pruebas** con instantes conocidos, sin leer el reloj. Verifican el valor exacto (`2026-08-11T20:15:30.123Z`), el sufijo `Z`, la ausencia de cualquier offset, la reinterpretación como el mismo instante, tres instantes adicionales —incluido un cruce de día en UTC−6—, el formato de texto y que `TZ` no altera el resultado. **Windows: 9 ejecutadas, 1 omitida** (`time.tzset` no existe). **Dentro de la imagen final: 10 de 10 ejecutadas**, incluida la de `TZ=Pacific/Kiritimati` (UTC+14). |
| 34 | **`docker build --no-cache`** *(nueva)* | **OK.** La única capa `CACHED` es la imagen base ya descargada (`FROM`); la instalación de dependencias **se ejecutó realmente** (23 s, descargas visibles, `Successfully installed …`). **No falló por hashes** y **sí instaló las transitivas** (`starlette`, `anyio`, `pydantic-core`, `psycopg-binary`, `greenlet`, `uvloop`, `watchfiles`…). Imagen `personal-blog-backend:task005-final`, **315 MB**, Python **3.12.13**, usuario efectivo **`uid=1001(blog)`**. |
| 35 | **Suite dentro de la imagen final** *(nueva)* | **69 pruebas superadas, 1 omitida**, con **`pytest -W error` y sin ningún filtro**. Ejecutada en un contenedor efímero de `personal-blog-backend:task005-final` con `tests/` montado en solo lectura y `pytest`/`httpx2` instalados **en el contenedor, no en la imagen**. La omitida es la que compara con la hora local: allí el host **ya opera en UTC**. |
| 36 | **Warnings estrictos en Windows** *(nueva)* | **`pytest -W error` → 69 superadas, 1 omitida, 0 warnings, código de salida 0.** **Sin ningún filtro**: ni `-W ignore`, ni `filterwarnings` en `pyproject.toml`, ni `PYTHONWARNINGS`. Ejecutada con el `.venv` ya alineado con `requirements-dev.txt`: `httpx2==2.10.0` instalado, `httpx` clásico **desinstalado** (`pip show httpx` → `Package(s) not found`) y `pip check` → `No broken requirements found.` La omitida es la de `TZ`, porque `time.tzset` no existe en Windows; en Docker sí se ejecuta (validación 33). |
| 37 | **Entorno principal tras las correcciones** *(nueva)* | **Intacto.** `personal-blog-local-postgres` **healthy**, `personal-blog-local-minio` **healthy**, `personal-blog-local-portainer` up. Los **3 volúmenes** presentes. Solo se creó y eliminó el contenedor temporal `personal-blog-backend-task005-final-check`. La imagen anterior `personal-blog-backend:local` **se conservó**. |
| 38 | **Enlaces Markdown** *(nueva)* | **0 enlaces relativos rotos** en los seis documentos de `personal-blog-infra` tocados por la tarea. |

## 11. Problemas encontrados

| # | Problema | Resolución |
| --- | --- | --- |
| 1 | **El `.env` con BOM rompía el arranque.** Escrito con `Set-Content -Encoding utf8` en PowerShell 5.1, el archivo lleva BOM; con `env_file_encoding="utf-8"` el BOM se pega al nombre de la primera variable y, con `extra="forbid"`, el proceso aborta con `blog_app_name: Extra inputs are not permitted` — un error que no señala la causa real. | La configuración pasa a leer el archivo con **`utf-8-sig`**, que interpreta correctamente el `.env` lleve BOM o no. El caso quedó documentado en el código. |
| 2 | **El puerto 8000 estaba ocupado** por otro proyecto de la máquina, cuya API respondía a las comprobaciones y podía haberse confundido con la del blog. | Las pruebas manuales pasaron al puerto **8010** y la comprobación verifica el `title` de OpenAPI, no solo el código HTTP. |
| 3 | **`mypy` rechazaba `PostgresDsn.password`**, atributo que existe en ejecución pero no en las anotaciones del tipo. | El enmascarado pasa a hacerse con una expresión regular sobre la URL, sin depender de atributos no tipados. |
| 4 | **`caplog` no capturaba el log de arranque**: `configure_logging` reemplaza los manejadores del logger raíz, incluido el que instala pytest. | La prueba pasa a capturar la **salida estándar** con `capsys` y a interpretar la línea JSON, que es exactamente lo que verá Docker o CloudWatch. |
| 5 | **`Session.is_active` seguía en `True`** tras cerrar la sesión, lo que hacía fallar la comprobación del contexto transaccional. | La prueba comprueba `in_transaction()`, que es la propiedad que refleja de verdad si queda una transacción viva. |
| 6 | **Alembic advertía de configuración obsoleta** (`No path_separator found in configuration`). | Añadida la opción `path_separator = os` a `alembic.ini`. |
| 7 | **Hallazgo colateral, ajeno al alcance:** al comparar los archivos versionados contra las credenciales reales del entorno local se comprobó que el `.env` de `personal-blog-infra` **conserva los valores de ejemplo** `change-me-local-postgres` y `change-me-local-minio`, que están publicados en `.env.example` desde `Task/003`. No es una filtración causada por esta tarea —esos textos ya estaban versionados como marcadores ficticios— pero significa que las contraseñas del entorno local son públicas. | **No se modifica el `.env` del usuario:** la rotación es una decisión suya y no forma parte del alcance de esta tarea. Se registra como riesgo **R-16**, que permanece **abierto**. El impacto está acotado: los servicios se publican solo en `127.0.0.1`. El procedimiento correcto de rotación —que **no** destruye datos— está en el [reporte](../task-reports/TASK-005-report.md) §6.1. |
| 8 | **Los logs declaraban UTC pero no lo garantizaban.** `JsonLogFormatter` delegaba la marca de tiempo en `logging.Formatter.formatTime`, que convierte con `time.localtime`: en Windows producía la hora local (`-0600`) y dentro del contenedor coincidía con UTC solo porque su entorno ya estaba en esa zona. El formato dependía del sistema operativo. Detectado en la revisión posterior. | La conversión pasa a ser **explícita**: `format_utc_timestamp` usa `datetime.fromtimestamp(created, tz=UTC)` y emite `2026-08-11T20:15:30.123Z`; el formato de texto hereda de `UtcClockFormatter`, cuyo `converter` es `time.gmtime`. Se añaden **10 pruebas deterministas** —8 funciones, una de ellas parametrizada con 3 instantes— con marcas de tiempo conocidas, ejecutadas en Windows y dentro de la imagen Docker. Ver §10, validaciones 31 a 34. |
| 9 | **Advertencia de `starlette.testclient`.** La suite terminaba con `1 warning`: desde Starlette 1.3, `TestClient` con el `httpx` clásico emite `StarletteDeprecationWarning` y pide `httpx2`. Con `-W error` la suite ni siquiera podía importar `conftest.py`. | Se sustituye la dependencia **de desarrollo** `httpx==0.28.1` por **`httpx2==2.10.0`** (el mismo proyecto renombrado: `github.com/pydantic/httpx2`, autor Tom Christie, estado *Production/Stable*). No entra en la imagen ni en el artefacto Lambda. Con ella, `pytest -W error` pasa **con 0 warnings y sin ningún filtro** en **Windows** y dentro de la **imagen final**. El `httpx` clásico quedó **desinstalado** del entorno de Windows. Ver §10, validaciones 35 y 36. |

## 12. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-03 | El patrón de conexión a PostgreSQL puede no ser compatible con Lambda (pooling, límites). | Medio | El acceso a datos está aislado en `shared/database`: cambiar la estrategia de conexión no afecta a los módulos de negocio. La decisión se cierra en `Task/029`. |
| R-14 | **Nuevo.** Las dependencias transitivas **no** están bloqueadas: dos instalaciones en fechas distintas pueden traer versiones distintas de las indirectas. **Ya ocurrió:** la imagen construida el 2026-08-11 resolvió `starlette 1.6.0`, mientras que el entorno de Windows, instalado el 2026-08-01, tiene `starlette 1.3.1`. | Medio | Las dependencias directas están fijadas con `==` y `pip check` se ejecuta como validación. El bloqueo completo con hashes, resuelto en Linux, se añade en `Task/020`. Mientras tanto el Dockerfile **no usa** `--require-hashes` ni `--no-deps`, que serían incoherentes con el archivo real (§7.1). |
| R-15 | **Nuevo.** La imagen `python:3.12.13-slim` envejece y acumula vulnerabilidades sin corregir. | Medio | Misma naturaleza que R-10 para las imágenes de infraestructura. Escaneo en `Task/018` y verificación en CI en `Task/020`. |
| R-16 | **Nuevo.** El `.env` del entorno local conserva las contraseñas de ejemplo `change-me-*`, que están publicadas en `.env.example` desde `Task/003`: las credenciales de PostgreSQL y MinIO locales son, de hecho, públicas. | Bajo | Acotado porque los tres servicios se publican solo en `127.0.0.1` y no son alcanzables desde la red. La rotación en PostgreSQL **no destruye datos**: `ALTER ROLE` sobre el rol existente, sin recrear volumen ni base. **MinIO exige un procedimiento distinto.** Ambos **quedan a decisión del usuario** y **no se ejecutaron** en esta tarea. Procedimiento en el [reporte](../task-reports/TASK-005-report.md) §6.1. El riesgo permanece **abierto**. |
| R-10 | Las etiquetas de imagen fijadas envejecen. | Medio | Sin cambios. `Task/018` y `Task/021`. |
| R-02, R-04 a R-07, R-09, R-11 a R-13 | Riesgos vigentes de tareas anteriores. | — | Sin cambios. |

## 13. Deuda técnica pendiente

- **Sin `GET /ready`**: no hay comprobación de dependencias (O-04, `Task/017`).
- **Correlation ID incompleto**: el `request_id` se genera en la respuesta de error, no se
  acepta ni se propaga por cabecera a todos los logs de la petición (O-02, `Task/017`).
- **Sin bloqueo de dependencias transitivas** con hashes (R-14, `Task/020`).
- **Sin escaneo de vulnerabilidades** de dependencias ni de la imagen (`Task/018`,
  `Task/020`).
- **Sin CI**: lint, tipos, pruebas y construcción se ejecutan a mano (`Task/020`).
- **Pool de conexiones provisional**: valores convencionales, válidos en local; la
  estrategia para Lambda se decide en `Task/029`.
- **Sin CORS**: hará falta en cuanto el frontend consuma la API (`Task/007`).
- **La migración fundacional no crea objetos**: el ciclo `upgrade`/`downgrade` se verifica
  sobre `alembic_version`. La primera migración con tablas reales llega en `Task/008`.
- **Cobertura al 99 %**, con una rama parcial sin cubrir en el validador de configuración
  de producción.
- **Correlación de logs entre zonas horarias**: las marcas ya son UTC, pero el proyecto no
  documenta todavía una convención de visualización para el desarrollo local, que ocurre en
  UTC−6. Es un detalle de operación, no de formato.

## 14. Pasos de validación para el usuario

Ver [reporte de la tarea](../task-reports/TASK-005-report.md), sección 9.

## 15. Próxima tarea

`Task/006-Fundacion-Frontend-React` — React, TypeScript, Vite, router, cliente HTTP,
pruebas y build de producción, en `personal-blog-frontend`.

**No se inicia hasta que `Task/005` sea aprobada** y se complete su cierre.

## 16. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** ✔ |
| **Fecha de aprobación** | 2026-08-12 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005-Fundacion-Backend-FastAPI` |

> El usuario autorizó explícitamente el cierre con la expresión exacta requerida por
> [WORKFLOW.md](../project-management/WORKFLOW.md) §3. Esta sección no se completó por
> iniciativa propia.
