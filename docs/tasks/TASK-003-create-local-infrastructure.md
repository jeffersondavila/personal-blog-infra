# TASK-003 — Crear Infraestructura Local

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/003-Crear-Infraestructura-Local` |
| **Nombre** | Crear Infraestructura Local |
| **Etapa** | [ETAPA 01 — Infraestructura Local](../stages/STAGE-01-local-infrastructure.md) |
| **Estado** | **Aprobada** |
| **Repositorios involucrados** | `personal-blog-infra` (únicamente) |
| **Dependencias** | `Task/002-Definir-MVP-y-Arquitectura` — **Aprobada** ✔ |
| **Rama** | `Task/003-Crear-Infraestructura-Local`, creada desde `dev` en `personal-blog-infra` |
| **Fecha de inicio** | 2026-07-28 |
| **Fecha de aprobación** | 2026-07-29 |
| **Aprobado por** | jeffersondavila |
| **Última actualización** | 2026-07-29 |

---

## 1. Objetivo

Disponer de un entorno local reproducible, levantable con un solo comando, que provea
**PostgreSQL**, **MinIO** (almacenamiento compatible con S3) y **Portainer CE**
(supervisión de Docker), con datos persistentes en volúmenes nombrados, redes separadas y
healthchecks verificados.

Al terminar, `docker compose up -d` debe dejar los servicios sanos y los datos deben
sobrevivir a `docker compose down` seguido de `up`.

## 2. Contexto

`Task/002` cerró el alcance del MVP y la arquitectura, pero no creó ninguna
infraestructura. La estrategia local-first ([ADR-001](../adr/ADR-001-local-first.md))
exige que la base de datos y el almacenamiento de objetos existan **antes** que las
aplicaciones que los consumen: `Task/005` (backend) y `Task/006` (frontend) no pueden
empezar sin ellos.

Esta es la primera tarea del proyecto que produce artefactos ejecutables en lugar de
documentación.

## 3. Dentro del alcance

- [x] Crear la rama `Task/003` desde `dev`, **solo** en `personal-blog-infra`.
- [x] Docker Compose base del entorno local.
- [x] PostgreSQL con volumen persistente.
- [x] MinIO como almacenamiento compatible con S3, con volumen persistente.
- [x] Portainer CE para supervisión local, con volumen persistente.
- [x] Redes Docker separadas y aislamiento entre servicios.
- [x] Volúmenes nombrados para los tres servicios.
- [x] Healthchecks por servicio, donde la imagen lo permite.
- [x] Archivo `.env.example` con variables documentadas y valores ficticios.
- [x] Fijar versiones de imagen; no usar `latest`.
- [x] Publicar los puertos únicamente en la interfaz de loopback.
- [x] Runbook de arranque, parada, verificación y diagnóstico.
- [x] Registrar la decisión diferida D-05 (reverse proxy local) como propuesta.
- [x] Actualizar la documentación de gestión afectada.

## 4. Fuera del alcance

| Elemento | Dónde corresponde |
| --- | --- |
| Backup y restauración de PostgreSQL | `Task/004` |
| Respaldo de la configuración de Portainer | `Task/004` |
| Procedimiento de reconstrucción con recuperación de datos | `Task/004` |
| Servicio de backend (FastAPI) en el Compose | `Task/005`, `Task/007` |
| Servicio de frontend (React) en el Compose | `Task/006`, `Task/007` |
| Despliegue del reverse proxy | `Task/007` |
| Esquema de base de datos, tablas y migraciones | `Task/008` |
| Creación de buckets de la aplicación e interfaz `ObjectStorage` | `Task/010` |
| Logs JSON, correlation ID y observabilidad | `Task/017` |
| Endurecimiento de imágenes y escaneo de vulnerabilidades | `Task/018` |
| Validación de `docker compose config` en CI | `Task/021` |
| Terraform y cualquier recurso cloud | `Task/025` y Etapas 09–10 |

**Prohibición explícita:** esta tarea **no crea ningún recurso cloud**, no crea cuentas en
ningún proveedor y no ejecuta Terraform. La primera interacción con AWS o Cloudflare
ocurre en la Etapa 09, según [ADR-001](../adr/ADR-001-local-first.md).

## 5. Entregables

| Entregable | Repositorio | Ruta | Acción |
| --- | --- | --- | --- |
| Definición del entorno local | `personal-blog-infra` | `docker-compose.yml` | Creado |
| Variables de ejemplo | `personal-blog-infra` | `.env.example` | Creado |
| Runbook del entorno local | `personal-blog-infra` | `docs/runbooks/local-environment.md` | Creado |
| Índice de runbooks | `personal-blog-infra` | `docs/runbooks/README.md` | Creado |
| Ficha de esta tarea | `personal-blog-infra` | `docs/tasks/TASK-003-create-local-infrastructure.md` | Creado |
| Reporte de esta tarea | `personal-blog-infra` | `docs/task-reports/TASK-003-report.md` | Creado |
| Estado del proyecto | `personal-blog-infra` | `docs/project-management/STATUS.md` | Modificado |
| Roadmap | `personal-blog-infra` | `docs/project-management/ROADMAP.md` | Modificado |
| Ficha de la Etapa 01 | `personal-blog-infra` | `docs/stages/STAGE-01-local-infrastructure.md` | Modificado |
| Decisiones diferidas | `personal-blog-infra` | `docs/architecture/open-decisions.md` | Modificado |
| Índice de reportes | `personal-blog-infra` | `docs/task-reports/README.md` | Modificado |
| README del repositorio | `personal-blog-infra` | `README.md` | Modificado |

**6 creados · 6 modificados · 0 eliminados.**

## 6. Servicios definidos

| Servicio | Imagen | Contenedor | Red | Volumen |
| --- | --- | --- | --- | --- |
| `postgres` | `postgres:17.10-alpine` | `personal-blog-local-postgres` | `blog-data` | `personal-blog-local_postgres_data` |
| `minio` | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | `personal-blog-local-minio` | `blog-data` | `personal-blog-local_minio_data` |
| `portainer` | `portainer/portainer-ce:2.39.5` | `personal-blog-local-portainer` | `blog-management` | `personal-blog-local_portainer_data` |

### Puertos

Todos publicados en `127.0.0.1`, nunca en `0.0.0.0`.

| Servicio | Host | Contenedor | Motivo del puerto elegido |
| --- | --- | --- | --- |
| PostgreSQL | `55432` | `5432` | Evita el choque con PostgreSQL nativo u otro proyecto Docker. |
| MinIO — API S3 | `9000` | `9000` | Puerto estándar de la API S3 de MinIO. |
| MinIO — consola | `9001` | `9001` | Puerto estándar de la consola de MinIO. |
| Portainer | `9444` | `9443` | Evita el choque con otra instancia de Portainer en `9443`. |

### Redes

| Red | Servicios | Motivo |
| --- | --- | --- |
| `personal-blog-local-data` | `postgres`, `minio` | Datos del blog. El backend se unirá en `Task/007`. |
| `personal-blog-local-management` | `portainer` | Portainer no necesita hablar por red con la base de datos ni con el almacenamiento. El aislamiento **de red** impide esa comunicación directa; **no** limita lo que Portainer puede hacer sobre esos contenedores a través del daemon de Docker — ver §6.1. |

### 6.1 Nivel de privilegio de Portainer

`Task/003` monta el socket del daemon de Docker en Portainer:

```yaml
- /var/run/docker.sock:/var/run/docker.sock:ro
```

| Qué **sí** hace `:ro` | Qué **no** hace |
| --- | --- |
| Monta el **archivo** del socket como solo lectura dentro del contenedor: no puede sobrescribirse ni borrarse. `docker inspect` lo refleja como `RW=False`. | **No** convierte la Docker API en una API de solo lectura. **No** restringe los métodos que pueden enviarse por el socket. |

**Consecuencia real, que queda registrada explícitamente:**

- Portainer conserva **capacidad administrativa completa sobre el daemon de Docker**.
- Puede crear, detener, reiniciar, eliminar y modificar **contenedores, redes, volúmenes
  e imágenes** del host, incluidos los de este proyecto y los de cualquier otro proyecto
  de la máquina.
- El aislamiento en `blog-management` impide que Portainer alcance PostgreSQL y MinIO
  **por red**, como cliente. **No impide** que actúe sobre ellos por la Docker API: esas
  acciones no atraviesan la red de datos.
- Quien controla el socket de Docker controla el equipo. Es equivalente a acceso de
  administrador del host, tal como ya establece
  [security-boundaries.md](../architecture/security-boundaries.md) §4.

**El riesgo se acepta únicamente porque:**

1. Portainer es **exclusivamente local** y no se despliega en producción.
2. Se publica **solo en `127.0.0.1:9444`**, nunca en `0.0.0.0`.
3. Exige **autenticación propia**, con administrador creado en el primer acceso.

**Regla de operación:** no exponer Portainer a la red local ni a internet, en ninguna
circunstancia.

**Lo que faltaría para un control real de solo lectura:** un **socket proxy** que filtre
los métodos permitidos de la Docker API, o una política de autorización adicional.
**Queda fuera del alcance de `Task/003`** y no se implementa aquí. Se propone evaluarlo
en `Task/018-Endurecimiento-de-Seguridad`.

### Variables de entorno requeridas

Definidas en `.env.example` y consumidas desde `.env` (ignorado por Git):

`COMPOSE_PROJECT_NAME` · `TZ` · `LOCAL_BIND_ADDRESS` · `POSTGRES_VERSION` ·
`POSTGRES_DB` · `POSTGRES_USER` · `POSTGRES_PASSWORD` · `POSTGRES_HOST_PORT` ·
`MINIO_VERSION` · `MINIO_ROOT_USER` · `MINIO_ROOT_PASSWORD` · `MINIO_API_HOST_PORT` ·
`MINIO_CONSOLE_HOST_PORT` · `PORTAINER_VERSION` · `PORTAINER_HTTPS_HOST_PORT`

Ninguna contiene un valor real: `.env.example` usa credenciales ficticias de desarrollo
marcadas como `change-me-*`.

## 7. Criterios de aceptación

| # | Criterio | Estado |
| --- | --- | --- |
| 1 | `docker compose config` es válido. | Cumplido — validación 1 |
| 2 | Los tres servicios están definidos con imagen fijada, sin `latest`. | Cumplido — validación 2 |
| 3 | `docker compose up -d` levanta los tres servicios. | Cumplido — validación 5 |
| 4 | Los healthchecks de PostgreSQL y MinIO pasan a `healthy`. | Cumplido — validación 6 |
| 5 | Portainer responde en su consola HTTPS local. | Cumplido — validación 9 |
| 6 | PostgreSQL acepta conexiones y devuelve su versión. | Cumplido — validación 7 |
| 7 | MinIO responde en su endpoint de salud y en su consola. | Cumplido — validación 8 |
| 8 | Existen tres volúmenes nombrados, uno por servicio. | Cumplido — validación 11 |
| 9 | Existen dos redes separadas con la pertenencia esperada. | Cumplido — validación 10 |
| 10 | Los servicios de la red de datos se resuelven entre sí por nombre. | Cumplido — validación 10 |
| 11 | Portainer no pertenece a la red de datos. | Cumplido — validación 10 |
| 12 | El montaje del socket de Docker es `:ro` **y su alcance real está documentado sin exagerarlo**. | Cumplido — validación 12 y §6.1 |
| 13 | Los puertos se publican solo en `127.0.0.1`. | Cumplido — validación 13 |
| 14 | Los datos sobreviven a `docker compose down` + `up`. | Cumplido — validación 14 |
| 15 | Los datos sobreviven a `docker compose restart`. | Cumplido — validación 15 |
| 16 | `.env` está ignorado por Git y `.env.example` versionado. | Cumplido — validación 16 |
| 17 | No hay credenciales reales en ningún archivo versionado. | Cumplido — validación 17 |
| 18 | No se creó ningún recurso cloud. | Cumplido — validación 19 |
| 19 | Backend y frontend permanecen intactos. | Cumplido — validación 20 |
| 20 | Existe un runbook de arranque, parada y diagnóstico. | Cumplido — `docs/runbooks/local-environment.md` |
| 21 | Los enlaces relativos resuelven. | Cumplido — validación 21 |
| 22 | La tarea queda `Lista para validación`, nunca `Aprobada` por decisión propia. | Cumplido — aprobada después por el usuario el 2026-07-29 |
| 23 | No se inició `Task/004`. | Cumplido |

## 8. Plan de validación

Cada criterio se comprueba ejecutando el comando correspondiente contra el entorno real,
no por inspección del archivo. Los resultados están en la sección 10 y en el
[reporte](../task-reports/TASK-003-report.md).

## 9. Comandos de validación

```powershell
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

# Definición
docker compose config --quiet
docker compose config --services
docker compose config --volumes
docker compose config --images

# Arranque
docker compose pull
docker compose up -d
docker compose ps

# Salud
docker inspect --format "{{.State.Health.Status}}" personal-blog-local-postgres
docker inspect --format "{{.State.Health.Status}}" personal-blog-local-minio

# Acceso
docker compose exec postgres psql -U blog_local -d personal_blog -c "SELECT version();"
Invoke-WebRequest -Uri "http://127.0.0.1:9000/minio/health/live" -UseBasicParsing
Invoke-WebRequest -Uri "http://127.0.0.1:9001" -UseBasicParsing

# Redes y aislamiento
docker network inspect personal-blog-local-data --format "{{range .Containers}}{{.Name}} {{end}}"
docker network inspect personal-blog-local-management --format "{{range .Containers}}{{.Name}} {{end}}"

# Persistencia
docker compose down
docker compose up -d

# Git
git status --porcelain -b
git diff --check
```

## 10. Resultado de las validaciones

Ejecutadas el 2026-07-28 sobre Docker Desktop 29.1.3 y Docker Compose v5.0.1 en
Windows 11.

| # | Validación | Comando | Resultado real |
| --- | --- | --- | --- |
| 1 | Sintaxis del Compose | `docker compose config --quiet` | **OK.** Sin errores ni advertencias. |
| 2 | Servicios e imágenes | `docker compose config --services` / `--images` | 3 servicios: `minio`, `portainer`, `postgres`. Imágenes: `postgres:17.10-alpine`, `minio/minio:RELEASE.2025-09-07T16-13-09Z`, `portainer/portainer-ce:2.39.5`. **Ninguna `latest`.** |
| 3 | Volúmenes declarados | `docker compose config --volumes` | `minio_data`, `portainer_data`, `postgres_data`. |
| 4 | Descarga de imágenes | `docker compose pull` | **OK** tras corregir dos etiquetas (sección 12). Tamaños: PostgreSQL 424 MB, MinIO 241 MB, Portainer 187 MB. |
| 5 | Arranque | `docker compose up -d` | 2 redes, 3 volúmenes y 3 contenedores creados e iniciados. |
| 6 | Healthchecks | `docker inspect --format "{{.State.Health.Status}}"` | `postgres=healthy`, `minio=healthy` en menos de 20 s. `portainer` sin healthcheck, por diseño (sección 11). |
| 7 | PostgreSQL | `psql -c "SELECT version();"` | `PostgreSQL 17.10 on x86_64-pc-linux-musl`. Base `personal_blog`, usuario `blog_local`. Puerto `55432` del host responde (`TcpTestSucceeded=True`). |
| 8 | MinIO | `Invoke-WebRequest` | `/minio/health/live` → **HTTP 200**. Consola en `9001` → **HTTP 200**. |
| 9 | Portainer | `Invoke-WebRequest https://127.0.0.1:9444` | Interfaz → **HTTP 200** (14 202 bytes). `/api/status` → **HTTP 200**, `{"Version":"2.39.5", ...}`. |
| 10 | Redes y aislamiento | `docker network inspect` | `...-data` → `postgres`, `minio`. `...-management` → `portainer`. DNS interno verificado: `getent hosts minio` desde `postgres` devuelve `172.20.0.3`, y `http://minio:9000/minio/health/live` es alcanzable desde `postgres`. **`portainer` no pertenece a la red de datos.** |
| 11 | Volúmenes creados | `docker volume ls` | `personal-blog-local_postgres_data`, `personal-blog-local_minio_data`, `personal-blog-local_portainer_data`. |
| 12 | Socket de Docker | `docker inspect` (montajes) | `/var/run/docker.sock → /var/run/docker.sock` con **`RW=False`**. Eso aplica al **archivo** del socket, **no** a la Docker API: Portainer conserva capacidad administrativa sobre el daemon. Documentado en §6.1 y en el runbook §2.1. |
| 13 | Publicación de puertos | `docker compose ps` | `127.0.0.1:55432->5432`, `127.0.0.1:9000-9001->9000-9001`, `127.0.0.1:9444->9443`. **Ninguno en `0.0.0.0`.** |
| 14 | Persistencia tras `down` + `up` | Escritura, `down`, `up`, lectura | **Superada.** La fila insertada en PostgreSQL y el objeto de 29 B en MinIO siguen presentes tras destruir y recrear los contenedores. Los tres volúmenes sobreviven a `docker compose down`. |
| 15 | Persistencia tras `restart` | `docker compose restart` | **Superada.** Ambos servicios vuelven a `healthy`; los datos siguen. Portainer conserva su `InstanceID`, lo que confirma que su volumen persiste. |
| 16 | `.env` ignorado | `git check-ignore -v .env` | Ignorado por la regla `.gitignore:9:*.env`. `git status` solo muestra `.env.example`. |
| 17 | Búsqueda de secretos | Búsqueda de patrones en los archivos versionados | **0 credenciales reales.** Los únicos valores son los marcadores ficticios `change-me-local-postgres` y `change-me-local-minio` de `.env.example`. |
| 18 | `git diff --check` | `git diff --check` | Sin errores de espacios en blanco. |
| 19 | Ausencia de recursos cloud | Revisión de archivos y comandos | **Ninguno.** Sin `*.tf`, sin llamadas a AWS o Cloudflare, sin cuentas creadas. |
| 20 | Backend y frontend intactos | `git status` en ambos repositorios | Ambos en `main`, **árboles limpios**, sin rama `Task/003`. |
| 21 | Enlaces Markdown relativos | Verificación de destinos | **277 verificados, 0 rotos** en la primera ronda; **282 verificados, 0 rotos** tras las correcciones (sección 18.5). |

### Validaciones de la ronda de corrección (2026-07-28)

| # | Validación | Comando | Resultado real |
| --- | --- | --- | --- |
| 22 | Compose tras fijar el parche | `docker compose config --quiet` | **OK.** |
| 23 | Imagen efectiva declarada | `docker compose config --images` | `postgres:17.10-alpine`, `minio/minio:RELEASE.2025-09-07T16-13-09Z`, `portainer/portainer-ce:2.39.5`. |
| 24 | Descarga y recreación | `docker compose pull postgres` · `up -d postgres` | Imagen descargada; contenedor **recreado**, no eliminado el volumen. |
| 25 | Imagen efectiva del contenedor | `docker inspect --format "{{.Config.Image}}"` | **`postgres:17.10-alpine`.** |
| 26 | Motor y salud | `SELECT version()` | `PostgreSQL 17.10 on x86_64-pc-linux-musl`. Estado **`healthy`**. |
| 27 | Volúmenes conservados | `docker volume ls --filter name=personal-blog-local` | **3 de 3 presentes.** El contenedor recreado remontó `personal-blog-local_postgres_data`. Los volúmenes ajenos al proyecto también intactos. **No se usó `docker compose down -v`.** |

## 11. Decisiones técnicas

| # | Decisión | Alternativas consideradas | Justificación | ¿ADR? |
| --- | --- | --- | --- | --- |
| 1 | `docker-compose.yml` en la raíz del repositorio. | Carpeta `local/` o `infra/local/`. | El criterio de salida de la Etapa 01 es que `docker compose up -d` funcione; en la raíz no hace falta `-f` ni `--project-directory`. | No |
| 2 | Versiones de imagen fijadas por etiqueta. | `latest`. | Un entorno reproducible no puede depender de una etiqueta móvil. `latest` haría que dos máquinas levantaran versiones distintas. | No |
| 3 | `postgres:17.10-alpine`. | `postgres:17` (Debian); `postgres:17-alpine`. | Alpine da una imagen menor con compatibilidad de motor idéntica. Se fija la **versión de parche completa**: `17-alpine` es una etiqueta móvil dentro de la serie 17 y cambiaría de parche sin aviso, lo que contradice el requisito de reproducibilidad. | No |
| 4 | Puerto `55432` para PostgreSQL. | `5432` estándar. | En esta máquina ya existe otro proyecto Docker que publica `5432`. El puerto es configurable por `.env`. | No |
| 5 | Puerto `9444` para Portainer. | `9443` estándar. | Ya existe otra instancia de Portainer en la máquina publicando `9443`. Configurable por `.env`. | No |
| 6 | Publicación en `127.0.0.1`, no en `0.0.0.0`. | Publicación en todas las interfaces. | [security-boundaries.md](../architecture/security-boundaries.md) exige que Portainer nunca sea alcanzable desde fuera del equipo; se aplica el mismo criterio a la base de datos y al almacenamiento. | No |
| 7 | Dos redes: `blog-data` y `blog-management`. | Una sola red. | Portainer no necesita alcanzar PostgreSQL ni MinIO **por red**. Separarlas elimina esa vía de comunicación directa. **No es un control de privilegios**: no afecta a lo que Portainer puede hacer por la Docker API (§6.1). | No |
| 8 | Montaje del socket de Docker con `:ro`. | Montaje sin `:ro`; socket proxy. | `:ro` protege el **archivo** del socket dentro del contenedor, y no cuesta nada. **No aporta un control de solo lectura sobre la Docker API** y no se presenta como tal. El socket proxy, que sí lo daría, queda fuera del alcance de esta tarea y se propone para `Task/018`. | No |
| 9 | Volúmenes nombrados en lugar de *bind mounts*. | `./data/postgres`, etc. | Evita problemas de permisos y de rendimiento en Windows, y mantiene los datos fuera del árbol de trabajo de Git. | No |
| 10 | Sin healthcheck en Portainer. | Healthcheck con `curl` o `wget`. | La imagen `portainer-ce` es *distroless*: su único binario es `/portainer`, sin shell ni cliente HTTP. **Verificado empíricamente**: `exec` de `/bin/sh` y `/usr/bin/env` falla con `no such file or directory`. Se verifica desde el host. | No |
| 11 | `POSTGRES_INITDB_ARGS` con `--lc-collate=C --lc-ctype=C`. | Locale por defecto del host. | Impide que el locale de la máquina altere el ordenamiento y produzca resultados distintos entre equipos. | No |
| 12 | No se crea ningún bucket de la aplicación. | Servicio auxiliar con `mc mb`. | La creación de buckets pertenece a `Task/010-Almacenamiento-Compatible-S3`, junto con la interfaz `ObjectStorage`. Adelantarlo sería alcance fuera de esta tarea. | No |

### D-05 — Reverse proxy local

[open-decisions.md](../architecture/open-decisions.md) asigna a `Task/003` la decisión
**D-05 — Reverse proxy local concreto**. La Etapa 01, sin embargo, deja explícitamente el
reverse proxy con aplicaciones reales para la Etapa 02, y `Task/003` no despliega ninguna
aplicación a la que enrutar.

**Resolución adoptada:** se registra la **elección de la tecnología** sin desplegarla, y el
servicio se añadirá al Compose en `Task/007-Integracion-Local`, cuando existan backend y
frontend a los que enrutar.

**Propuesta: Traefik v3.**

| Criterio de D-05 | Traefik v3 | Alternativa: Nginx | Alternativa: Caddy |
| --- | --- | --- | --- |
| Simplicidad de configuración | Descubre los servicios por etiquetas del propio Compose; no hay un archivo de rutas que mantener en paralelo. | Requiere mantener un `nginx.conf` sincronizado a mano con el Compose. | Configuración breve, pero también en archivo aparte. |
| Rutas de sitio y de API | Enrutado por prefijo de ruta y por host mediante etiquetas. | Soportado. | Soportado. |
| Equivalencia con API Gateway HTTP API | Alta: enrutado por ruta, middlewares de CORS y de límite de tasa, igual que las capacidades que se usarán en `Task/033`. | Media: exige configurar CORS a mano. | Media. |
| Peso de la imagen | ~200 MB | ~50 MB | ~50 MB |
| Healthchecks | `traefik healthcheck` incluido en la imagen. | Requiere `curl` o `wget` en la imagen. | Endpoint propio. |

**Estado de la decisión:** `Propuesta — pendiente de aprobación`. Se marcará como resuelta
en `open-decisions.md` únicamente si el usuario aprueba esta tarea, y el servicio se
implementará en `Task/007`. No requiere ADR: es local y reversible, tal como registra la
propia D-05.

## 12. Problemas encontrados

| # | Problema | Resolución |
| --- | --- | --- |
| 1 | **Etiqueta de Portainer inexistente.** El primer intento fijó `portainer/portainer-ce:2.34.1`; `docker compose pull` falló con `not found`. | Se consultaron las etiquetas publicadas y se fijó **2.39.5**, la publicación más recientemente actualizada del repositorio. Descarga verificada. |
| 2 | **Etiqueta de MinIO desactualizada.** El primer intento fijó una etiqueta `RELEASE.2025-04-22...` que no correspondía a una publicación existente. | Se fijó **`RELEASE.2025-09-07T16-13-09Z`**, la última publicada. Descarga verificada. |
| 3 | **Portainer no admite healthcheck.** Su imagen es *distroless* y no contiene shell ni cliente HTTP con el que sondearla. | Se omite el healthcheck, se documenta el motivo en el propio Compose y se verifica el servicio desde el host contra `/api/status`. |
| 4 | **El alias de `mc` no persiste.** Tras recrear el contenedor de MinIO, `mc ls` devolvió `Access Denied`. | **No es pérdida de datos**: la configuración de `mc` vive en el sistema de archivos del contenedor, fuera del volumen `/data`. Reestablecido el alias, el bucket y el objeto seguían intactos. Documentado en el runbook, sección 6.3. |
| 5 | **Interferencia de PowerShell al pasar comandos al contenedor.** `sh -c "... $MINIO_ROOT_USER ..."` con comillas dobles hace que PowerShell expanda la variable **antes** de enviarla, y MinIO responde `Invalid access key`. Lo mismo ocurre con la redirección `>`. | Usar comillas **simples** para el argumento de `sh -c`, y `mc pipe` en lugar de redirecciones. Documentado en el runbook, sección 6.3. |
| 6 | **Otro proyecto Docker ocupa puertos en esta máquina.** Existen contenedores de un proyecto ajeno que publican `5432`, `8000`, `8080` y `9443`, además de una instancia de Portainer llamada `portainer`. | Se eligieron `55432` y `9444`, y todos los contenedores llevan el prefijo `personal-blog-local-`. Ningún recurso ajeno fue detenido, modificado ni eliminado. |
| 7 | **Afirmación técnica incorrecta sobre el socket de Docker**, detectada por el usuario en la revisión: se presentaba `:ro` como si dejara a Portainer con capacidad de solo observar. | Corregido en 7 archivos. El montaje se conserva, pero deja de presentarse como control de privilegios. R-09 reescrito y elevado a **Medio**. Detalle en la sección 18.1. |
| 8 | **`POSTGRES_VERSION=17-alpine` era una etiqueta móvil**, detectado por el usuario: contradecía la afirmación de que todas las versiones estaban fijadas. | Fijado a `17.10-alpine` y verificado en ejecución real, conservando el volumen. Detalle en la sección 18.2. |
| 9 | **El README declaraba que la implementación no había comenzado**, detectado por el usuario, cuando `Task/003` ya produce infraestructura ejecutable. | Sustituido por una tabla por área. Detalle en la sección 18.3. |

## 13. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-08 | **Nuevo.** El entorno local no tiene copia de seguridad: `docker compose down -v` destruye la base de datos y los objetos sin recuperación posible. | Alto | `Task/004-Backups-y-Recuperacion-Local` es la tarea inmediatamente siguiente. Mientras tanto, el runbook marca `-v` como destructivo en dos lugares. |
| R-09 | **Nuevo.** Portainer tiene acceso al socket del daemon de Docker y, por tanto, **capacidad administrativa sobre el host**: puede administrar contenedores, redes y volúmenes de este y de cualquier otro proyecto de la máquina. El montaje `:ro` **no** limita la Docker API, y la separación de redes tampoco. Agravante: conviven dos instancias de Portainer sobre el mismo daemon. | **Medio** | Se acepta solo porque es local, se publica en `127.0.0.1` y exige autenticación propia. **Regla:** no exponerlo nunca a la red local ni a internet. Un control real de solo lectura exigiría un socket proxy, fuera del alcance de esta tarea; se propone evaluarlo en `Task/018`. |
| R-10 | **Nuevo.** Las etiquetas de imagen fijadas envejecen y acumulan vulnerabilidades sin corregir. | Medio | `Task/018-Endurecimiento-de-Seguridad` incorpora el escaneo de imágenes; `Task/021-CI-Infraestructura` valida el Compose en cada cambio. |
| R-05 | Los enlaces cruzados entre repositorios asumen carpetas hermanas. | Bajo | Sin cambios. Documentado en los README. |
| R-02, R-03, R-04, R-06, R-07 | Riesgos vigentes de tareas anteriores. | — | Sin cambios en esta tarea. |

## 14. Documentación creada o actualizada

- `docker-compose.yml` — **creado**: definición del entorno local.
- `.env.example` — **creado**: 15 variables documentadas con valores ficticios.
- `docs/runbooks/local-environment.md` — **creado**: operación del entorno.
- `docs/runbooks/README.md` — **creado**: índice y reglas de los runbooks.
- `docs/tasks/TASK-003-create-local-infrastructure.md` — **creado**: esta ficha.
- `docs/task-reports/TASK-003-report.md` — **creado**: reporte de ejecución.
- `docs/project-management/STATUS.md` — `Task/003` en progreso → lista para validación.
- `docs/project-management/ROADMAP.md` — estado de la Etapa 01 y de `Task/003`.
- `docs/stages/STAGE-01-local-infrastructure.md` — estado y criterios de salida.
- `docs/architecture/open-decisions.md` — D-05 con propuesta pendiente de aprobación.
- `docs/task-reports/README.md` — índice de reportes.
- `README.md` — estado del repositorio y sección del entorno local.

## 15. Pasos de validación para el usuario

Ver [reporte de la tarea](../task-reports/TASK-003-report.md), sección 9.

## 16. Deuda técnica pendiente

- **Sin backup.** Es la razón de ser de `Task/004`, la tarea siguiente.
- **Sin buckets de la aplicación.** MinIO está vacío; los buckets se crean en `Task/010`.
- **Base de datos vacía.** Sin esquema ni migraciones hasta `Task/008`.
- **Sin reverse proxy desplegado.** D-05 queda propuesta; el servicio se añade en
  `Task/007`.
- **Sin validación automatizada del Compose.** Se añade en `Task/021`.
- **Portainer sin healthcheck.** Limitación de la imagen, no de la configuración. Si una
  versión futura incorpora un binario de sondeo, se añadirá.
- **Sin control de solo lectura sobre la Docker API.** El montaje `:ro` del socket no lo
  proporciona (§6.1). Requeriría un socket proxy o una política de autorización
  adicional. Se propone evaluarlo en `Task/018-Endurecimiento-de-Seguridad`.

## 17. Próxima tarea

`Task/004-Backups-y-Recuperacion-Local` — backup y restauración de PostgreSQL,
verificación de la persistencia de MinIO, respaldo de la configuración de Portainer y
procedimiento de reconstrucción completa del entorno.

**No se inicia hasta que `Task/003` sea aprobada.**

## 18. Correcciones aplicadas tras la revisión del usuario

Ronda de corrección del 2026-07-28, sobre la misma rama y **sin cambiar el alcance**. La
tarea permanece `Lista para validación`. No hubo commit, merge, push ni pull request.

### 18.1 Semántica del socket de Docker — afirmación técnica incorrecta

**Error detectado por el usuario.** La documentación afirmaba que montar
`/var/run/docker.sock` con `:ro` dejaba a Portainer con capacidad de **solo observar** y
que la separación de redes impedía que actuara sobre PostgreSQL y MinIO. **Ambas
afirmaciones son falsas.**

`:ro` aplica al **archivo** del socket dentro del contenedor: impide sobrescribirlo o
borrarlo, y `docker inspect` lo refleja como `RW=False`. **No** convierte la Docker API en
una API de solo lectura ni restringe los métodos que pueden enviarse por ella. Portainer
conserva **capacidad administrativa completa sobre el daemon**, y las acciones que envía
por la Docker API **no atraviesan la red de datos**, por lo que el aislamiento en
`blog-management` no las limita.

**Corrección aplicada.** El montaje `:ro` se **conserva** —protege el archivo del socket
y no cuesta nada— pero deja de presentarse como un control de privilegios. Queda
documentado en todos los archivos afectados que:

- Portainer está aislado de la red de datos para impedir comunicación **directa por red**.
- Conserva **acceso privilegiado al daemon** mediante la Docker API.
- Puede administrar contenedores, redes y volúmenes del host, incluidos los de otros
  proyectos.
- La separación de redes **no** limita las acciones realizadas por el daemon.
- El riesgo se acepta **únicamente** porque Portainer es local, se publica en
  `127.0.0.1` y exige autenticación propia.
- **No debe exponerse** a la red local ni a internet.
- Un control real de solo lectura exigiría un **socket proxy** o una política adicional,
  **fuera del alcance actual**.

| Archivo | Corrección |
| --- | --- |
| `docker-compose.yml` | Bloque de comentarios de `portainer` reescrito con la advertencia de privilegio; comentario del montaje corregido; comentario de la red `blog-management` corregido. |
| `docs/runbooks/local-environment.md` | Nueva sección **2.1 — Nivel de privilegio de Portainer**; tabla de redes corregida; nota en la verificación de aislamiento (§6.5); advertencia en el usuario administrador (§6.4); nueva fila en los límites vigentes (§9). |
| `docs/tasks/TASK-003-*.md` (esta ficha) | Nueva sección **6.1**; criterio de aceptación 12 reformulado; validación 12 corregida; decisiones técnicas 7 y 8 reescritas; R-09 reescrito y elevado de Bajo a **Medio**; deuda técnica ampliada. |
| `docs/task-reports/TASK-003-report.md` | Nueva sección **4.1**; validaciones 16 y 17 corregidas; R-09 reescrito; deuda técnica ampliada. |
| `docs/project-management/STATUS.md` | **R-09 reescrito** por completo y elevado de Bajo a **Medio**. |
| `docs/stages/STAGE-01-local-infrastructure.md` | Criterio de salida de Portainer corregido; nueva fila en la tabla de riesgos. |
| `README.md` | Nueva advertencia de privilegio en la sección *Uso de Portainer*. |

No se implementó ningún socket proxy y no se ejecutó ninguna acción destructiva desde
Portainer.

### 18.2 PostgreSQL fijado a versión de parche

**Error detectado por el usuario.** `POSTGRES_VERSION=17-alpine` es una etiqueta **móvil**
dentro de la serie 17: contradecía la afirmación de que todas las versiones estaban
completamente fijadas.

**Corrección aplicada:** `POSTGRES_VERSION=17.10-alpine` en `.env.example` y en el `.env`
local ignorado por Git. Todas las tablas y referencias documentales pasaron de
`postgres:17-alpine` a `postgres:17.10-alpine`.

**Verificado en ejecución real** (sección 10, validaciones 22–27): imagen efectiva
`postgres:17.10-alpine`, `PostgreSQL 17.10`, contenedor `healthy`, **el volumen existente
se conservó**, puerto `55432` accesible, y MinIO y Portainer intactos. **No se usó
`docker compose down -v`.**

### 18.3 Estado de implementación en el README

**Error detectado por el usuario.** El README afirmaba de forma general que la
implementación *no ha comenzado*, cuando `Task/003` ya produce infraestructura local
ejecutable.

**Corrección aplicada:** sustituido por una tabla que distingue por área — infraestructura
local **comenzada** con `Task/003`; backend y frontend **no comenzados**; Terraform y
recursos cloud **inexistentes**.

### 18.4 D-05 sin cambios

La propuesta de **Traefik v3** se **conserva** intacta, en estado
`Propuesta — pendiente de aprobación de Task/003`. Queda constancia de que aprobar
`Task/003` implica también aceptar Traefik v3 como reverse proxy local, para
implementarlo en `Task/007`.

### 18.5 Revalidación completa tras las correcciones

Las 18 comprobaciones solicitadas se ejecutaron de nuevo sobre el entorno real:

| # | Comprobación | Resultado |
| --- | --- | --- |
| 1 | `docker compose config --quiet` | **OK** |
| 2 | `docker compose config --images` | `postgres:17.10-alpine`, `minio/minio:RELEASE.2025-09-07T16-13-09Z`, `portainer/portainer-ce:2.39.5` |
| 3 | `docker compose ps` | Los tres en marcha |
| 4 | Salud | `postgres=healthy`, `minio=healthy` |
| 5 | MinIO HTTP | `/minio/health/live` → **200**; consola → **200** |
| 6 | Portainer HTTPS | Interfaz → **200**; `/api/status` → **200**, `2.39.5` |
| 7 | Imagen efectiva de PostgreSQL | **`postgres:17.10-alpine`**, `PostgreSQL 17.10` |
| 8 | Volúmenes | **3 de 3 presentes** |
| 9 | Puertos | Los tres solo en `127.0.0.1` |
| 10 | Afirmaciones incorrectas residuales | **0 vigentes.** Las coincidencias restantes son las frases correctoras (que niegan el alcance de `:ro`) y el registro histórico del error. Sin `postgres:17-alpine` ni `POSTGRES_VERSION=17-alpine` vigentes. |
| 11 | Enlaces Markdown | **282 verificados, 0 rotos** |
| 12 | Secretos | **2 coincidencias, ambas los marcadores ficticios** `change-me-*` de `.env.example`. `.env` sigue ignorado. |
| 13 | `git diff --check` | Sin errores de espacios en blanco (solo avisos informativos de LF→CRLF) |
| 14 | `git status --porcelain -b` | 6 modificados + 6 nuevos, **sin confirmar** — ver nota siguiente |
| 15 | Backend y frontend | Ambos en `main`, **limpios** |
| 16 | Commits propios de `Task/003` | **0.** `git rev-list --count dev..Task/003` = 0; `HEAD` = `cca847c` |
| 17 | Push / merge / PR | **Ninguno.** La rama no tiene upstream; `origin` solo tiene `main` y `dev` |
| 18 | `Task/004` | **No iniciada.** No existe ninguna rama que la referencie |

**Observación sobre el índice de Git.** En la primera ronda los seis archivos nuevos
aparecían como `??`; ahora figuran como ` A `, el estado de *intent-to-add* que deja
`git add -N` y que produce habitualmente la integración de Git del editor al calcular el
diff de un archivo nuevo. **No es un commit ni un `git add` de contenido:** `HEAD` sigue
en `cca847c`, `git diff --cached --name-status HEAD` está **vacío** y el `reflog` muestra
como última operación el `checkout` de creación de la rama. Desde esta sesión no se
ejecutó ningún `git add` ni `git commit`.

---

## 19. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** |
| **Fecha de aprobación** | 2026-07-29 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/003-Crear-Infraestructura-Local` |

Con esta aprobación:

- **D-05 — Reverse proxy local** pasa de *Propuesta* a **Resuelta**: **Traefik v3** queda
  aceptado como reverse proxy local, para implementarlo en `Task/007-Integracion-Local`.
- El runbook [local-environment.md](../runbooks/local-environment.md) pasa de *Propuesta*
  a **Vigente**.
- El avance global pasa a **3 de 41 (7 %)** y la **ETAPA 01 queda al 50 %** (1 de 2).
- No se creó ningún ADR: D-05 es una decisión local y reversible, tal como registra el
  propio [open-decisions.md](../architecture/open-decisions.md).

### Flujo de cierre ejecutado

| # | Paso | Resultado |
| --- | --- | --- |
| 1 | Aprobación registrada documentalmente. | Hecho |
| 2 | D-05 promovida de *Propuesta* a **Resuelta**; runbook a **Vigente**. | Hecho |
| 3 | STATUS, ROADMAP, ficha de etapa, ficha y reporte actualizados; avance a 3 de 41. | Hecho |
| 4 | Validaciones finales re-ejecutadas. | Hecho |
| 5 | Commits creados en la rama Task. | Hecho |
| 6 | `Task/003` integrada en `dev` con merge `--no-ff`. | Hecho |
| 7 | Push de `dev`. | Hecho |
| 8 | Publicación de la rama `Task/003`. | Hecho |
| 9 | Pull request **`Task/003-Crear-Infraestructura-Local → main`**, sin fusionar. | Hecho — abierto para revisión del usuario |
| 10 | Merge del pull request hacia `main`. | **No ejecutado** — corresponde exclusivamente al usuario |
| 11 | Vuelta a `main`, `fetch --prune` y `pull --ff-only`. | Hecho |
| 12 | Rama Task local eliminada con `git branch -d`. | Hecho |
| 13 | Rama Task remota conservada. | Hecho |
| 14 | `Task/004` iniciada. | **No** — requiere que el usuario fusione el PR y se complete la normalización `main → dev` |

Detalle completo: [reporte de la tarea](../task-reports/TASK-003-report.md).
