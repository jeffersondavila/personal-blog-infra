# Reporte — TASK-003 Crear Infraestructura Local

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/003-Crear-Infraestructura-Local` |
| **Etapa** | [ETAPA 01 — Infraestructura Local](../stages/STAGE-01-local-infrastructure.md) |
| **Estado final** | **Aprobada** |
| **Fecha de ejecución** | 2026-07-28 |
| **Fecha de aprobación** | 2026-07-29 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Repositorios afectados** | `personal-blog-infra` (únicamente) |
| **Ficha completa** | [TASK-003](../tasks/TASK-003-create-local-infrastructure.md) |
| **Runbook producido** | [local-environment.md](../runbooks/local-environment.md) |

---

## 1. Estado inicial encontrado

Verificado con Git antes de tocar nada, sin asumir el estado de sesiones anteriores.

### 1.1 Instrucciones cargadas

`CLAUDE.md` existe en la raíz del workspace e importa
`@personal-blog-infra/docs/claude/PROJECT_INSTRUCTIONS.md`, que también existe y fue
leído íntegramente. Se consultaron además `STATUS.md`, `ROADMAP.md`, `WORKFLOW.md`,
`DEFINITION_OF_DONE.md`, `TASK_TEMPLATE.md`, `CONTRIBUTING.md`, la ficha de la Etapa 01,
ADR-001, `security-boundaries.md`, `local-to-cloud-mapping.md`, `overview.md`,
`open-decisions.md` y la ficha y el reporte de `Task/002`.

### 1.2 Git

| Repositorio | Rama activa | Árbol | `main` | `dev` | Contenido `main` ↔ `dev` |
| --- | --- | --- | --- | --- | --- |
| `personal-blog-infra` | `main` | Limpio | `dbb41aa` | `cca847c` | **Idéntico** |
| `personal-blog-frontend` | `main` | Limpio | `144a401` | `8823cc3` | **Idéntico** |
| `personal-blog-backend` | `main` | Limpio | `76c09f5` | `0f94abb` | **Idéntico** |

- `git fetch --prune origin` ejecutado en los tres repositorios.
- **No existía ninguna rama `Task`**, ni local ni remota, en ninguno de los tres.
  `Task/002.1-Configurar-Claude-Code` estaba correctamente eliminada en ambos lados.
- `dev` tiene 2 commits que `main` no tiene (los merges propios de integración) y `main`
  **0** commits que `dev` no tenga: `git rev-list --count dev..main` = 0 en los tres.
  No hizo falta ninguna normalización previa.
- Avance global: **2 de 41**. Etapa 00 completada. `Task/003` en estado `Pendiente`.

El estado coincidía con lo esperado tras el cierre de `Task/002.1`, así que se continuó
automáticamente.

### 1.3 Divergencia documental corregida

`STATUS.md` describía el PR de `Task/002.1` como *pendiente de revisión y fusión* y
declaraba `main` y `dev` **no** sincronizadas en infra. El estado real de Git demuestra lo
contrario: el PR `#3` fue fusionado (`dbb41aa`) y `dev` normalizada (`cca847c`), con
contenido idéntico. Se actualizó `STATUS.md` conforme al orden de autoridad de
`PROJECT_INSTRUCTIONS.md` §15: **el estado real de Git manda sobre la documentación
histórica**.

### 1.4 Entorno de ejecución

| Componente | Versión |
| --- | --- |
| Docker Desktop | 29.1.3 |
| Docker Compose | v5.0.1 |
| Sistema operativo | Windows 11 Home Single Language 10.0.26200 |

**Hallazgo relevante:** la máquina ya alojaba otro proyecto Docker (`farm-tech-infra`) con
seis contenedores detenidos que publican `5432`, `8000`, `8080` y `1883`, además de un
contenedor llamado `portainer` en `9443`. Esto condicionó la elección de puertos y de
nombres. **Ningún recurso ajeno al proyecto fue detenido, modificado ni eliminado.**

---

## 2. Rama creada

```
Task/003-Crear-Infraestructura-Local
```

- Creada **desde `dev`** en `personal-blog-infra`, según `WORKFLOW.md` §2.
- **No se creó en frontend ni en backend**: `ROADMAP.md`, la ficha de la Etapa 01 y
  `STATUS.md` coinciden en que `Task/003` afecta únicamente a `infra`, y la regla del
  proyecto prohíbe crear ramas en repositorios que no se van a modificar.
- Base: `cca847c`. Rama activa confirmada, árbol limpio al crearla.

---

## 3. Archivos creados y modificados

**6 creados · 6 modificados · 0 eliminados.** Todos en `personal-blog-infra`.

### Creados

```
docker-compose.yml                                   definición del entorno local
.env.example                                         15 variables con valores ficticios
docs/runbooks/README.md                              índice y reglas de los runbooks
docs/runbooks/local-environment.md                   operación del entorno local
docs/tasks/TASK-003-create-local-infrastructure.md   ficha de la tarea
docs/task-reports/TASK-003-report.md                 este reporte
```

### Modificados

```
README.md                                       estado del repositorio y entorno local
docs/project-management/STATUS.md               Task/003 lista para validación, R-08/09/10
docs/project-management/ROADMAP.md              Etapa 01 en curso, Task/003
docs/stages/STAGE-01-local-infrastructure.md    estado, criterios de salida, riesgos
docs/architecture/open-decisions.md             D-05 con propuesta pendiente
docs/task-reports/README.md                     índice de reportes
```

### No creados a propósito

Sin archivos `.tf`, sin `Dockerfile`, sin código de aplicación, sin workflows de CI y sin
ningún ADR nuevo. Nada de eso pertenece a esta tarea.

---

## 4. Servicios locales configurados

| Servicio | Imagen | Contenedor | Red | Volumen | Healthcheck |
| --- | --- | --- | --- | --- | --- |
| `postgres` | `postgres:17.10-alpine` | `personal-blog-local-postgres` | `...-data` | `..._postgres_data` | `pg_isready` |
| `minio` | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | `personal-blog-local-minio` | `...-data` | `..._minio_data` | `mc ready local` |
| `portainer` | `portainer/portainer-ce:2.39.5` | `personal-blog-local-portainer` | `...-management` | `..._portainer_data` | **Ninguno** — ver §7 |

### Puertos

| Servicio | Publicado en | Contenedor | Motivo |
| --- | --- | --- | --- |
| PostgreSQL | `127.0.0.1:55432` | `5432` | `5432` ya está ocupado en esta máquina. |
| MinIO — API S3 | `127.0.0.1:9000` | `9000` | Puerto estándar, libre. |
| MinIO — consola | `127.0.0.1:9001` | `9001` | Puerto estándar, libre. |
| Portainer | `127.0.0.1:9444` | `9443` | `9443` ya está ocupado por otra instancia de Portainer. |

**Ningún puerto se publica en `0.0.0.0`.** La interfaz es configurable por
`LOCAL_BIND_ADDRESS`, documentada con la advertencia explícita de no cambiarla.

### Redes

| Red | Servicios |
| --- | --- |
| `personal-blog-local-data` | `postgres`, `minio` |
| `personal-blog-local-management` | `portainer` |

La separación impide que Portainer alcance PostgreSQL y MinIO **por red**. **No es un
control de privilegios**: Portainer conserva capacidad administrativa sobre esos
contenedores a través del daemon de Docker — ver §4.1. El backend se unirá a `data` en
`Task/007`.

### 4.1 Nivel de privilegio de Portainer

Portainer recibe el socket del daemon de Docker montado como
`/var/run/docker.sock:/var/run/docker.sock:ro`.

| Qué **sí** hace `:ro` | Qué **no** hace |
| --- | --- |
| Monta el **archivo** del socket como solo lectura dentro del contenedor: no puede sobrescribirse ni borrarse. `docker inspect` lo refleja como `RW=False`. | **No** convierte la Docker API en una API de solo lectura. **No** restringe los métodos que pueden enviarse por el socket. |

Queda registrado explícitamente:

- Portainer **conserva capacidad administrativa completa sobre el daemon de Docker**.
- Puede crear, detener, reiniciar, eliminar y modificar **contenedores, redes, volúmenes
  e imágenes** del host — los de este proyecto y los de cualquier otro de la máquina.
- El aislamiento en `blog-management` impide la comunicación **directa por red** con
  PostgreSQL y MinIO. **No impide** actuar sobre ellos por la Docker API: esas acciones
  no atraviesan la red de datos.
- Quien controla el socket de Docker controla el equipo: es equivalente a acceso de
  administrador del host, tal como ya establece
  [security-boundaries.md](../architecture/security-boundaries.md) §4.

**El riesgo se acepta únicamente porque** Portainer es local, se publica solo en
`127.0.0.1:9444` y exige autenticación propia.

**Regla de operación:** **no exponer Portainer** a la red local ni a internet, en ninguna
circunstancia.

**Lo que faltaría para un control real de solo lectura:** un **socket proxy** que filtre
los métodos permitidos de la Docker API, o una política de autorización adicional.
**Fuera del alcance de `Task/003`**; se propone evaluarlo en `Task/018`.

### Volúmenes

`personal-blog-local_postgres_data` · `personal-blog-local_minio_data` ·
`personal-blog-local_portainer_data`

Volúmenes gestionados por Docker, no *bind mounts*: evitan los problemas de permisos y
rendimiento en Windows y mantienen los datos fuera del árbol de Git.

### Variables de entorno requeridas

`COMPOSE_PROJECT_NAME` · `TZ` · `LOCAL_BIND_ADDRESS` · `POSTGRES_VERSION` ·
`POSTGRES_DB` · `POSTGRES_USER` · `POSTGRES_PASSWORD` · `POSTGRES_HOST_PORT` ·
`MINIO_VERSION` · `MINIO_ROOT_USER` · `MINIO_ROOT_PASSWORD` · `MINIO_API_HOST_PORT` ·
`MINIO_CONSOLE_HOST_PORT` · `PORTAINER_VERSION` · `PORTAINER_HTTPS_HOST_PORT`

---

## 5. Comandos de operación

```powershell
Copy-Item .env.example .env      # solo la primera vez
docker compose config --quiet    # validar
docker compose pull              # descargar imágenes
docker compose up -d             # levantar
docker compose ps                # estado
docker compose logs -f postgres  # logs
docker compose restart           # reiniciar
docker compose stop              # detener sin eliminar
docker compose down              # eliminar contenedores; LOS DATOS SE CONSERVAN
docker compose down -v           # DESTRUCTIVO: elimina también los volúmenes
```

Procedimiento completo, con resultados esperados y tabla de diagnóstico:
[local-environment.md](../runbooks/local-environment.md).

---

## 6. Validaciones ejecutadas y resultados reales

Todas ejecutadas contra el entorno real levantado en esta máquina el 2026-07-28. **Ninguna
se declara aprobada sin haberse ejecutado.**

| # | Validación | Resultado real |
| --- | --- | --- |
| 1 | `docker compose config --quiet` | **OK.** Sin errores ni advertencias. |
| 2 | `docker compose config --services` | `minio`, `portainer`, `postgres`. |
| 3 | `docker compose config --volumes` | `minio_data`, `portainer_data`, `postgres_data`. |
| 4 | `docker compose config --images` | Tres imágenes con etiqueta fija. **Ninguna `latest`.** |
| 5 | `docker compose pull` | **OK.** PostgreSQL 424 MB, MinIO 241 MB, Portainer 187 MB. Requirió corregir dos etiquetas — §7. |
| 6 | `docker compose up -d` | 2 redes, 3 volúmenes y 3 contenedores creados e iniciados. |
| 7 | Healthchecks | `postgres=healthy`, `minio=healthy` en menos de 20 s. |
| 8 | PostgreSQL — motor | `SELECT version()` → `PostgreSQL 17.10 on x86_64-pc-linux-musl`. Base `personal_blog`, usuario `blog_local`. |
| 9 | PostgreSQL — puerto del host | `Test-NetConnection 127.0.0.1 -Port 55432` → `TcpTestSucceeded=True`. |
| 10 | MinIO — API S3 | `http://127.0.0.1:9000/minio/health/live` → **HTTP 200**. |
| 11 | MinIO — consola | `http://127.0.0.1:9001` → **HTTP 200**. |
| 12 | Portainer — interfaz | `https://127.0.0.1:9444` → **HTTP 200**, 14 202 bytes. |
| 13 | Portainer — API | `/api/status` → **HTTP 200**, `{"Version":"2.39.5", ...}`. |
| 14 | Pertenencia a redes | `data` → `postgres`, `minio`. `management` → `portainer`. |
| 15 | DNS interno y conectividad | Desde `postgres`: `getent hosts minio` → `172.20.0.3`; `http://minio:9000/minio/health/live` alcanzable. |
| 16 | Aislamiento de red de Portainer | `portainer` pertenece **solo** a `management`. No tiene ruta **de red** hacia PostgreSQL ni MinIO. **No implica** limitación de privilegios — §4.1. |
| 17 | Socket de Docker | Montado como `/var/run/docker.sock` con **`RW=False`**. Aplica al **archivo** del socket, **no** a la Docker API: Portainer conserva capacidad administrativa sobre el daemon — §4.1. |
| 18 | Publicación de puertos | `127.0.0.1:55432->5432`, `127.0.0.1:9000-9001->9000-9001`, `127.0.0.1:9444->9443`. **Ninguno en `0.0.0.0`.** |
| 19 | **Persistencia tras `down` + `up`** | **Superada.** Se insertó una fila en PostgreSQL y se subió un objeto de 29 B a un bucket de MinIO; se ejecutó `docker compose down` (los tres volúmenes sobrevivieron) y `up -d`; **ambos datos seguían presentes** tras recrear los contenedores. |
| 20 | **Persistencia tras `restart`** | **Superada.** Ambos servicios vuelven a `healthy`; los datos siguen; Portainer conserva su `InstanceID`, lo que confirma que su volumen persiste. |
| 21 | Limpieza de los datos de prueba | Tabla eliminada (`\dt` → *Did not find any relations*) y bucket eliminado (`mc ls local` → vacío). El entorno queda limpio y en marcha. |
| 22 | `.env` ignorado por Git | `git check-ignore -v .env` → `.gitignore:9:*.env`. `git status` **no** lo muestra. |
| 23 | Búsqueda de secretos | **0 credenciales reales** en los archivos versionados. Los únicos valores son los marcadores ficticios `change-me-local-postgres` y `change-me-local-minio` de `.env.example`. |
| 24 | `git diff --check` | Sin errores de espacios en blanco. |
| 25 | Ausencia de recursos cloud | **Ninguno.** Sin `*.tf`, sin llamadas a AWS ni Cloudflare, sin cuentas, sin Terraform ejecutado. |
| 26 | Backend y frontend intactos | Ambos en `main`, **árboles limpios**, sin rama `Task/003`, sin archivos modificados. |
| 27 | Enlaces Markdown relativos | **277 verificados, 0 rotos** en la primera ronda; **282 verificados, 0 rotos** tras las correcciones. |

### Contenedores levantados — estado final

```
NAME                            STATUS               PORTS
personal-blog-local-minio       Up (healthy)         127.0.0.1:9000-9001->9000-9001/tcp
personal-blog-local-portainer   Up                   127.0.0.1:9444->9443/tcp
personal-blog-local-postgres    Up (healthy)         127.0.0.1:55432->5432/tcp
```

Los tres quedan **en marcha** para que el usuario pueda validarlos.

---

## 7. Problemas encontrados y cómo se resolvieron

| # | Problema | Resolución |
| --- | --- | --- |
| 1 | **Etiqueta de Portainer inexistente.** `portainer/portainer-ce:2.34.1` falló con `not found`. | Se consultaron las etiquetas publicadas y se fijó **2.39.5**, la publicación más recientemente actualizada. Descarga verificada. |
| 2 | **Etiqueta de MinIO inexistente.** La etiqueta `RELEASE.2025-04-22...` del primer intento no correspondía a ninguna publicación. | Se fijó **`RELEASE.2025-09-07T16-13-09Z`**, la última publicada. Descarga verificada. |
| 3 | **Portainer no admite healthcheck.** Se comprobó ejecutando `/bin/sh` y `/usr/bin/env` dentro de la imagen: ambos fallan con `no such file or directory`. Es una imagen *distroless* cuyo único binario es `/portainer`. | Se omite el healthcheck, con el motivo escrito en el propio Compose, y se verifica desde el host contra `/api/status`. Registrado como deuda: si una versión futura incorpora un binario de sondeo, se añadirá. |
| 4 | **`mc` devolvió `Access Denied` tras recrear el contenedor de MinIO.** | **No era pérdida de datos.** La configuración de `mc` vive en el sistema de archivos del contenedor, fuera del volumen `/data`. Al reestablecer el alias, el bucket y el objeto seguían intactos. Documentado en el runbook §6.3. |
| 5 | **PowerShell interfiere al pasar comandos al contenedor.** Con comillas dobles expande `$MINIO_ROOT_USER` antes de enviarlo (MinIO responde `Invalid access key`), e intercepta la redirección `>`. | Usar comillas **simples** para el argumento de `sh -c` y `mc pipe` en lugar de redirecciones. Documentado en el runbook §6.3 para que no vuelva a costar tiempo. |
| 6 | **Otro proyecto Docker ocupa puertos en la máquina.** | Se eligieron `55432` y `9444`, y todos los recursos llevan el prefijo `personal-blog-local-`. Ningún recurso ajeno fue tocado. |
| 7 | **`STATUS.md` describía un estado de ramas que Git desmiente.** | Corregido conforme al orden de autoridad de `PROJECT_INSTRUCTIONS.md` §15 — ver §1.3. |

---

## 8. Riesgos y decisiones pendientes

### Riesgos nuevos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-08 | El entorno local **no tiene copia de seguridad**: `docker compose down -v` destruye base de datos y objetos sin recuperación. | **Alto** | `Task/004` es la tarea inmediatamente siguiente. El runbook marca `-v` como destructivo en dos lugares. |
| R-09 | Portainer tiene acceso al socket del daemon de Docker y, por tanto, **capacidad administrativa sobre el host**: puede administrar contenedores, redes y volúmenes de este y de cualquier otro proyecto. `:ro` **no** limita la Docker API y la separación de redes tampoco. Agravante: conviven dos instancias de Portainer sobre el mismo daemon. | **Medio** | Se acepta solo porque es local, se publica en `127.0.0.1` y exige autenticación propia. **Regla: no exponerlo nunca** a la red local ni a internet. Socket proxy fuera de alcance; se propone para `Task/018`. |
| R-10 | Las etiquetas de imagen fijadas envejecen y acumulan vulnerabilidades. | Medio | Escaneo en `Task/018`; validación del Compose en CI en `Task/021`. |

Riesgos anteriores (R-02 a R-07) siguen abiertos sin cambios. R-01 sigue cerrado.

### Decisión pendiente — D-05

`open-decisions.md` asigna a `Task/003` la decisión **D-05 — Reverse proxy local
concreto**, pero la Etapa 01 deja el reverse proxy con aplicaciones reales para la
Etapa 02 y esta tarea no despliega ninguna aplicación a la que enrutar.

**Resolución adoptada:** se elige la tecnología sin desplegarla. La propuesta es
**Traefik v3**, con la comparación frente a Nginx y Caddy registrada en
[open-decisions.md](../architecture/open-decisions.md). El servicio se implementará en
`Task/007-Integracion-Local`.

**Estado: `Propuesta — pendiente de aprobación`.** No se marcó como resuelta ni se creó
ningún ADR. **Aprobar `Task/003` implica también aceptar Traefik v3** como reverse proxy
local: en ese momento D-05 pasará a *Resuelta* y el servicio se implementará en
`Task/007`.

### Deuda técnica

Sin backup (`Task/004`) · sin buckets de la aplicación (`Task/010`) · base de datos vacía,
sin esquema ni migraciones (`Task/008`) · sin reverse proxy desplegado (`Task/007`) · sin
validación automatizada del Compose (`Task/021`) · Portainer sin healthcheck, por
limitación de la imagen · **sin control de solo lectura sobre la Docker API** (requiere un
socket proxy; se propone para `Task/018`).

---

## 9. Pasos exactos para validar

```powershell
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

# a) Rama activa y cambios sin confirmar
git status --porcelain -b
git branch -vv

# b) La definición es válida y no usa `latest`
docker compose config --quiet
docker compose config --images

# c) Estado de los servicios (deben estar ya en marcha)
docker compose ps

# d) Salud
docker inspect --format "{{.State.Health.Status}}" personal-blog-local-postgres
docker inspect --format "{{.State.Health.Status}}" personal-blog-local-minio

# e) PostgreSQL responde
docker compose exec postgres psql -U blog_local -d personal_blog -c "SELECT version();"

# f) MinIO responde
Invoke-WebRequest -Uri "http://127.0.0.1:9000/minio/health/live" -UseBasicParsing

# g) Consolas web
Start-Process "http://127.0.0.1:9001"     # MinIO
Start-Process "https://127.0.0.1:9444"    # Portainer (certificado autofirmado)

# h) Aislamiento de red: portainer NO debe aparecer en la red de datos
docker network inspect personal-blog-local-data --format "{{range .Containers}}{{.Name}} {{end}}"
docker network inspect personal-blog-local-management --format "{{range .Containers}}{{.Name}} {{end}}"

# i) Los puertos están solo en loopback
docker compose ps --format "{{.Service}} | {{.Ports}}"

# j) `.env` está ignorado y `.env.example` versionado
git check-ignore -v .env
git status --porcelain

# k) Backend y frontend intactos
git -C ..\personal-blog-backend status --porcelain -b
git -C ..\personal-blog-frontend status --porcelain -b
```

En Portainer, el primer acceso pide crear un usuario administrador. Ese usuario es **de
Portainer**, no del blog, y debe crearse en los primeros minutos tras el arranque; si no,
Portainer bloquea la inicialización y hay que reiniciar el contenedor.

**Qué revisar con atención:** si los puertos elegidos te convienen, si la separación de
redes te parece correcta, si la propuesta de Traefik para D-05 te convence, y si el
runbook es suficiente para operar el entorno sin ayuda.

---

## 10. Estado Git final

| Repositorio | Rama activa | Estado del árbol |
| --- | --- | --- |
| `personal-blog-infra` | `Task/003-Crear-Infraestructura-Local` | 6 modificados + 6 nuevos, **sin confirmar** |
| `personal-blog-frontend` | `main` | **Limpio** |
| `personal-blog-backend` | `main` | **Limpio** |

Salida real de `git status --porcelain -b` al cierre de la ronda de corrección:

```
## Task/003-Crear-Infraestructura-Local
 A .env.example
 M README.md
 A docker-compose.yml
 M docs/architecture/open-decisions.md
 M docs/project-management/ROADMAP.md
 M docs/project-management/STATUS.md
 A docs/runbooks/README.md
 A docs/runbooks/local-environment.md
 M docs/stages/STAGE-01-local-infrastructure.md
 M docs/task-reports/README.md
 A docs/task-reports/TASK-003-report.md
 A docs/tasks/TASK-003-create-local-infrastructure.md
```

> **Nota sobre las marcas ` A `.** En la primera ronda los seis archivos nuevos aparecían
> como `??` (sin seguimiento). Ahora figuran como ` A `, es decir, con *intent-to-add* en
> el índice — el estado que deja `git add -N`, típico de la integración de Git del editor
> al calcular el diff de un archivo nuevo. **No es un commit ni un `git add` de
> contenido**, y se comprobó explícitamente:
>
> - `git rev-parse --short HEAD` → **`cca847c`**, el mismo commit base de `dev`. Sin
>   commits nuevos.
> - `git diff --cached --name-status HEAD` → **vacío**. Nada preparado para confirmar.
> - `git reflog` → la última operación de la rama es el `checkout` de su creación.
>
> El contenido de los doce archivos sigue **íntegramente sin confirmar**. No se ejecutó
> ningún `git add` ni `git commit` desde esta sesión.

El archivo `.env` existe en el árbol de trabajo (es necesario para levantar el entorno)
pero **está ignorado por Git** y no aparece en `git status`.

El archivo `.env` existe en el árbol de trabajo (es necesario para levantar el entorno)
pero **está ignorado por Git** y no aparece en `git status`.

---

## 11. Confirmación de límites respetados **durante la ejecución** (antes de la aprobación)

- **No se hizo ningún commit.** `HEAD` sigue en `cca847c` y `git diff --cached HEAD` está
  vacío. Los cambios quedan sin confirmar, según `PROJECT_INSTRUCTIONS.md` §6.
- **No se hizo merge** hacia `dev` ni hacia `main`.
- **No se hizo push** de ninguna rama.
- **No se creó ningún pull request.**
- **No se modificó `main`.**
- **No se eliminó ninguna rama.**
- **No se marcó ninguna tarea como `Aprobada`.**
- **No se aceptó ningún ADR** ni se creó uno nuevo. D-05 queda como
  `Propuesta — pendiente de aprobación`.
- **No se creó ningún recurso cloud** ni ninguna cuenta en ningún proveedor.
- **No se ejecutó Terraform** ni existe ningún archivo `.tf`.
- **No se agregó ningún secreto**: `.env.example` solo contiene marcadores ficticios.
- **No se modificó `personal-blog-backend` ni `personal-blog-frontend`.**
- **No se tocó ningún recurso Docker ajeno al proyecto.**
- **No se ejecutó ningún comando destructivo.** No se usó `docker compose down -v`,
  `git reset --hard`, `git clean -fd`, `git push --force` ni `git branch -D`.
- **`Task/004-Backups-y-Recuperacion-Local` NO fue iniciada.**
- El avance global permanece en **2 de 41 (5 %)**.

---

## 11.b Correcciones aplicadas tras la revisión del usuario

Ronda del 2026-07-28, sobre la misma rama, **sin cambiar el alcance**. La tarea permanece
`Lista para validación`. No hubo commit, merge, push ni pull request.

### C-1 — Semántica del socket de Docker (afirmación técnica incorrecta)

**Lo que decía la documentación:** que montar `/var/run/docker.sock` con `:ro` dejaba a
Portainer con capacidad de **solo observar**, y que la separación de redes impedía que
actuara sobre PostgreSQL y MinIO.

**Por qué era falso:** `:ro` aplica al **archivo** del socket dentro del contenedor —
impide sobrescribirlo o borrarlo, y `docker inspect` lo refleja como `RW=False`. **No**
convierte la Docker API en una API de solo lectura ni restringe los métodos que pueden
enviarse por ella. Portainer conserva **capacidad administrativa completa sobre el
daemon**, y sus acciones por la Docker API **no atraviesan la red de datos**, por lo que
el aislamiento en `blog-management` no las limita.

**Qué se hizo:** el montaje `:ro` se **conserva** —protege el archivo del socket y no
cuesta nada— pero deja de presentarse como un control de privilegios. Se corrigió en
**7 archivos**:

| Archivo | Corrección |
| --- | --- |
| `docker-compose.yml` | Bloque de comentarios de `portainer` reescrito con la advertencia de privilegio; comentarios del montaje y de la red `blog-management` corregidos. |
| `docs/runbooks/local-environment.md` | Nueva sección **2.1 — Nivel de privilegio de Portainer**; tabla de redes corregida; nota en la verificación de aislamiento; advertencia en el usuario administrador; nueva fila en los límites vigentes. |
| `docs/tasks/TASK-003-*.md` | Nueva sección 6.1; criterio 12 reformulado; validación 12 corregida; decisiones 7 y 8 reescritas; R-09 elevado a **Medio**; deuda ampliada; sección 18 de correcciones. |
| `docs/task-reports/TASK-003-report.md` | Nueva sección 4.1; validaciones 16 y 17 corregidas; R-09 reescrito; deuda ampliada; esta sección. |
| `docs/project-management/STATUS.md` | **R-09 reescrito** por completo y elevado de Bajo a **Medio**. |
| `docs/stages/STAGE-01-local-infrastructure.md` | Criterio de salida de Portainer corregido; nueva fila de riesgo. |
| `README.md` | Advertencia de privilegio en *Uso de Portainer*. |

**No se implementó ningún socket proxy** y **no se ejecutó ninguna acción destructiva
desde Portainer**, conforme a la instrucción recibida.

### C-2 — PostgreSQL fijado a versión de parche

`POSTGRES_VERSION=17-alpine` era una etiqueta **móvil** dentro de la serie 17 y
contradecía la afirmación de que todas las versiones estaban fijadas.

Cambiado a **`17.10-alpine`** en `.env.example` y en el `.env` local ignorado por Git, y
propagado a todas las tablas documentales.

**Verificado en ejecución real, sin destruir datos:**

| Comprobación | Resultado |
| --- | --- |
| `docker compose config --quiet` | **OK** |
| `docker compose config --images` | `postgres:17.10-alpine` |
| `docker compose pull postgres` | Imagen descargada |
| `docker compose up -d postgres` | Contenedor **recreado** (`Recreate` → `Recreated` → `Started`) |
| Imagen efectiva del contenedor | **`postgres:17.10-alpine`** |
| `SELECT version()` | `PostgreSQL 17.10 on x86_64-pc-linux-musl` |
| Estado de salud | **`healthy`** |
| Volumen montado | `personal-blog-local_postgres_data` — **el mismo de antes** |
| Volúmenes del proyecto | **3 de 3 presentes** |
| Puerto `55432` | `TcpTestSucceeded=True` |
| MinIO y Portainer | **Intactos**, sin reiniciar (`Up 29 minutes` en ese momento) |

**No se usó `docker compose down -v`.** No se eliminó ningún volumen, ni del proyecto ni
ajeno.

### C-3 — Estado de implementación en el README

El README afirmaba de forma general que la implementación *no ha comenzado*, cuando
`Task/003` ya produce infraestructura local ejecutable. Sustituido por una tabla que
distingue por área: infraestructura local **comenzada** con `Task/003`; backend y frontend
**no comenzados**; Terraform y recursos cloud **inexistentes**.

### C-4 — D-05 sin cambios

La propuesta de **Traefik v3** se conserva intacta, en estado
`Propuesta — pendiente de aprobación de Task/003`. Queda constancia de que aprobar
`Task/003` implica también aceptar Traefik v3 como reverse proxy local, para
implementarlo en `Task/007`.

---

## 12. Próxima tarea prevista

**`Task/004-Backups-y-Recuperacion-Local`** — backup y restauración de PostgreSQL,
verificación de la persistencia de MinIO, respaldo de la configuración de Portainer y
procedimiento de reconstrucción completa del entorno.

**No ha sido iniciada** y no puede iniciarse hasta que `Task/003` sea aprobada y su cierre
esté completo.

---

## 13. Cierre aprobado (2026-07-29)

El usuario autorizó el cierre con `approved: Task/003-Crear-Infraestructura-Local`.
A partir de ese momento se ejecutó el flujo de cierre de
[`WORKFLOW.md`](../project-management/WORKFLOW.md) §3.

### 13.1 Promociones documentales

| Elemento | De | A |
| --- | --- | --- |
| `Task/003` | Lista para validación | **Aprobada** |
| **D-05 — Reverse proxy local** | Propuesta — pendiente de aprobación | **Resuelta: Traefik v3** |
| Runbook `local-environment.md` | Propuesta | **Vigente** |
| Avance global | 2 de 41 (5 %) | **3 de 41 (7 %)** |
| ETAPA 01 | 0 de 2 (0 %) | **1 de 2 (50 %)** |

**No se creó ningún ADR.** D-05 es una decisión local y reversible, y el propio
[open-decisions.md](../architecture/open-decisions.md) establece que no lo exige.
ADR-001 a ADR-005 siguen en **Aceptada**, sin cambios.

### 13.2 Operaciones de Git ejecutadas

| # | Paso | Resultado |
| --- | --- | --- |
| 1 | Commits en la rama Task | **2 commits** — ver sección 13.3 |
| 2 | `git switch dev` + `pull --ff-only origin dev` | `dev` actualizada, sin cambios remotos nuevos |
| 3 | `git merge --no-ff Task/003-Crear-Infraestructura-Local` | Integrada en `dev` |
| 4 | `git push origin dev` | Publicada |
| 5 | `git push -u origin Task/003-Crear-Infraestructura-Local` | Rama Task publicada |
| 6 | `gh pr create --base main --head Task/003-Crear-Infraestructura-Local` | **PR abierto** |
| 7 | Merge del PR | **NO ejecutado** — corresponde exclusivamente al usuario |
| 8 | `git switch main` + `fetch --prune` + `pull --ff-only` | `main` actualizada, **sin modificar** |
| 9 | `git branch -d Task/003-Crear-Infraestructura-Local` | Rama local eliminada (**nunca `-D`**) |
| 10 | Rama Task remota | **Conservada** mientras exista el PR |

### 13.3 Pull request

| Campo | Valor |
| --- | --- |
| **Dirección** | **`Task/003-Crear-Infraestructura-Local` → `main`** |
| **Base** | `main` |
| **Head** | `Task/003-Crear-Infraestructura-Local` |
| **Estado** | **Abierto, sin fusionar** |

Se respetó la regla crítica del proyecto: **no se creó ningún PR `dev → main`**. La
integración en `dev` y el pull request hacia `main` fueron operaciones separadas.

### 13.4 Qué corresponde ahora al usuario

1. Revisar el pull request.
2. Aceptarlo o rechazarlo. **Solo el usuario fusiona hacia `main`.**
3. Decidir si elimina la rama Task remota desde GitHub.

Cuando confirmes que fusionaste el PR, se ejecutará la normalización `main → dev` en
`personal-blog-infra` descrita en `PROJECT_INSTRUCTIONS.md` §10. **`Task/004` no puede
iniciarse antes de completar esa normalización.**
