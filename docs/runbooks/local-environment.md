# Runbook — Entorno local

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/003-Crear-Infraestructura-Local` (2026-07-29) |
| **Fecha** | 2026-07-28 |
| **Última actualización** | 2026-07-29 |
| **Tarea** | `Task/003-Crear-Infraestructura-Local` |
| **Alcance** | PostgreSQL, MinIO y Portainer CE en Docker Compose |

Procedimiento de arranque, parada, verificación y diagnóstico del entorno local del
blog. Todo lo descrito aquí ocurre **únicamente en la máquina de desarrollo**: ninguno
de estos servicios se despliega en la nube
([ADR-001](../adr/ADR-001-local-first.md), [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md)).

---

## 1. Requisitos previos

| Requisito | Detalle |
| --- | --- |
| Docker Desktop | En ejecución, con el backend de Linux (WSL 2 en Windows). |
| Docker Compose | v2 o superior (`docker compose`, no `docker-compose`). |
| Puertos libres | `55432`, `9000`, `9001`, `9444` en `127.0.0.1`. |
| Espacio en disco | Aproximadamente 1 GB para las tres imágenes más los datos. |

Comprobación:

```powershell
docker version
docker compose version
```

---

## 2. Servicios

| Servicio | Imagen | Rol | Red |
| --- | --- | --- | --- |
| `traefik` | `traefik:v3.6.2` | **Reverse proxy local.** Única puerta de entrada del navegador. | `blog-edge` |
| `frontend` | `personal-blog-frontend:local` | Sitio React construido y servido como estático. | `blog-edge` |
| `backend` | `personal-blog-backend:local` | API FastAPI. | `blog-edge`, `blog-data` |
| `postgres` | `postgres:17.10-alpine` | Persistencia relacional del blog. | `blog-data` |
| `minio` | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | Almacenamiento de objetos compatible con S3. | `blog-data` |
| `portainer` | `portainer/portainer-ce:2.39.5` | Supervisión de Docker en local. | `blog-management` |

Las versiones están fijadas en `.env.example`. No se usa `latest` en ningún servicio:
un entorno reproducible no puede depender de una etiqueta móvil.

Las imágenes `personal-blog-backend:local` y `personal-blog-frontend:local` **se
construyen desde los repositorios hermanos** —`BACKEND_CONTEXT` y `FRONTEND_CONTEXT` en el
`.env`—, no se descargan de ningún registro.

> **`traefik`, `frontend` y `backend` se añadieron en `Task/007`.** `postgres`, `minio` y
> `portainer` no cambiaron: mismos nombres, mismas imágenes, mismos volúmenes.

### Topología

```
navegador
    |
    v
Traefik v3   127.0.0.1:8081        <- unico puerto publicado de las aplicaciones
    |
    +-- /health, /api/, /docs, /openapi.json --> backend  :8000
    |                                              |
    |                                              +--> postgres :5432
    |                                              |
    |                                              + - > minio   :9000   (alcanzable;
    |                                                                     sin uso
    |                                                                     aplicativo)
    +-- resto de rutas ------------------------> frontend :8080
```

El sitio y el API **comparten origen**. Es deliberado: el navegador trata las peticiones
del frontend al backend como *same-origin* y **no hace falta CORS**. La topología
definitiva de dominios es **D-15** y se decide en `Task/011`.

### Puertos publicados

Todos se publican en la interfaz de loopback (`127.0.0.1`), nunca en `0.0.0.0`.

| Servicio | Host | Contenedor | Uso |
| --- | --- | --- | --- |
| **Traefik** | `8081` | `8080` | **Sitio y API.** Es la URL que se abre en el navegador. |
| PostgreSQL | `55432` | `5432` | Conexión desde herramientas locales y desde la suite de pruebas. |
| MinIO — API S3 | `9000` | `9000` | Cliente S3 (`ObjectStorage`, `Task/010`). |
| MinIO — consola | `9001` | `9001` | Interfaz web de administración de buckets. |
| Portainer | `9444` | `9443` | Consola HTTPS de supervisión. |

**`backend` y `frontend` no publican ningún puerto en el host.** Solo son alcanzables a
través de Traefik y desde su red de Docker. Es intencionado: una sola puerta de entrada,
igual que en producción.

> **Por qué `55432` y no `5432`:** evita el choque con una instalación nativa de
> PostgreSQL o con otro proyecto Docker en la misma máquina.
> **Por qué `9444` y no `9443`:** evita el choque con otra instancia de Portainer.
> **Por qué `8081` y no `80` ni `8080`:** el `80` exige privilegios en algunas máquinas y
> el `8080` es el puerto que más colisiona con otros proyectos Docker.

### URLs locales

| Qué | URL |
| --- | --- |
| Sitio | `http://localhost:8081/` |
| Vivacidad del API | `http://localhost:8081/health` |
| OpenAPI | `http://localhost:8081/openapi.json` |
| Documentación interactiva del API | `http://localhost:8081/docs` |
| Consola de MinIO | `http://127.0.0.1:9001` |
| Portainer | `https://127.0.0.1:9444` |

> Si cambias `TRAEFIK_HTTP_HOST_PORT`, **reconstruye la imagen del frontend**: Vite
> incrusta `VITE_API_BASE_URL` en tiempo de *build*, no de ejecución.
>
> ```powershell
> docker compose build frontend
> docker compose up -d frontend
> ```

### Redes

| Red | Contiene | Motivo |
| --- | --- | --- |
| `personal-blog-local-data` | `postgres`, `minio`, `backend` | Datos del blog. **Solo el backend** entra aquí desde el borde: es el único servicio con credenciales de base de datos. |
| `personal-blog-local-edge` | `traefik`, `frontend`, `backend` | Borde HTTP. Por aquí entra el tráfico del navegador. **Ni Traefik ni el frontend alcanzan PostgreSQL o MinIO.** |
| `personal-blog-local-management` | `portainer` | Portainer está **aislado por red** de PostgreSQL y MinIO: no puede alcanzarlos como cliente. Esa separación **no limita** lo que Portainer puede hacer sobre esos contenedores a través del daemon de Docker — ver sección 3.1. |

**El backend es el único servicio con un pie en cada red.** Es exactamente el papel que
tendrá la Lambda en producción: recibe HTTP por el borde y es lo único que habla con la
capa de datos.

### Volúmenes

| Volumen | Montaje | Contiene |
| --- | --- | --- |
| `personal-blog-local_postgres_data` | `/var/lib/postgresql/data` | Base de datos. |
| `personal-blog-local_minio_data` | `/data` | Objetos y buckets. |
| `personal-blog-local_portainer_data` | `/data` | Configuración y usuarios de Portainer. |

Son volúmenes gestionados por Docker, no *bind mounts*: sobreviven a
`docker compose down` y evitan los problemas de permisos y rendimiento de los
*bind mounts* en Windows.

**`Task/007` no añadió ningún volumen.** `traefik`, `frontend` y `backend` no guardan
estado: se reconstruyen enteros desde su imagen. Los únicos montajes nuevos son los dos
archivos de configuración de Traefik, en **solo lectura**.

---

## 2.1 Nivel de privilegio de Portainer

> **Portainer es el componente más privilegiado de este entorno.** Léelo antes de
> exponerlo o de darle acceso a alguien más.

Portainer recibe el socket del daemon de Docker:

```yaml
- /var/run/docker.sock:/var/run/docker.sock:ro
```

**Qué hace y qué no hace ese `:ro`:**

| | |
| --- | --- |
| **Sí hace** | Monta el **archivo** del socket como solo lectura dentro del contenedor: Portainer no puede sobrescribirlo ni borrarlo. `docker inspect` lo refleja como `RW=False`. |
| **No hace** | **No** convierte la Docker API en una API de solo lectura. **No** restringe los métodos que pueden enviarse por el socket. |

**Consecuencia real:** Portainer conserva **capacidad administrativa completa sobre el
daemon de Docker**. Puede crear, detener, reiniciar, eliminar y modificar contenedores,
redes, volúmenes e imágenes — los de este proyecto y **los de cualquier otro proyecto de
la máquina**. Quien controla el socket de Docker controla el equipo: es equivalente a
acceso de administrador del host
([security-boundaries.md](../architecture/security-boundaries.md), sección 4).

**La separación de redes no lo mitiga.** `blog-management` impide que Portainer alcance
PostgreSQL y MinIO **por red**, como cliente. Las acciones que Portainer envía por la
Docker API **no atraviesan la red de datos**: puede detener o eliminar esos contenedores
y sus volúmenes sin necesidad de alcanzarlos por red.

**Por qué se acepta este riesgo en `Task/003`:**

1. Portainer es **exclusivamente local** y no se despliega en producción
   ([ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md)).
2. Se publica **solo en `127.0.0.1:9444`**, nunca en `0.0.0.0`.
3. Exige **autenticación propia**, con un administrador creado en el primer acceso.

**Reglas de operación derivadas:**

- **No expongas Portainer** a la red local ni a internet. No cambies
  `LOCAL_BIND_ADDRESS`, no publiques el puerto en otra interfaz y no lo pongas detrás
  de un túnel accesible desde fuera.
- Trata un compromiso de Portainer como un incidente de **nivel host**, no de nivel
  aplicación.
- Usa una contraseña fuerte para su administrador, aunque sea "solo local".

**Lo que haría falta para un acceso realmente de solo lectura:** un **socket proxy**
(un intermediario que filtre los métodos permitidos de la Docker API) o una política de
autorización adicional. **Queda fuera del alcance de `Task/003`** y no se implementa
aquí.

---

## 3. Variables de entorno

El entorno se configura mediante un archivo `.env` en la raíz del repositorio.
**`.env` está ignorado por Git**; el archivo versionado es `.env.example`, con valores
ficticios.

| Variable | Propósito |
| --- | --- |
| `COMPOSE_PROJECT_NAME` | Prefijo de contenedores, redes y volúmenes. |
| `TZ` | Zona horaria de los contenedores. El proyecto usa UTC. |
| `LOCAL_BIND_ADDRESS` | Interfaz de publicación. **Debe permanecer en `127.0.0.1`.** |
| `POSTGRES_VERSION` | Etiqueta de la imagen de PostgreSQL. |
| `POSTGRES_DB` | Nombre de la base de datos. |
| `POSTGRES_USER` | Usuario de la base de datos. |
| `POSTGRES_PASSWORD` | Contraseña local. **Cámbiala en tu `.env`.** |
| `POSTGRES_HOST_PORT` | Puerto publicado en el host. |
| `MINIO_VERSION` | Etiqueta de la imagen de MinIO. |
| `MINIO_ROOT_USER` | Usuario administrador de MinIO. |
| `MINIO_ROOT_PASSWORD` | Contraseña local, mínimo 8 caracteres. **Cámbiala en tu `.env`.** |
| `MINIO_API_HOST_PORT` | Puerto de la API S3. |
| `MINIO_CONSOLE_HOST_PORT` | Puerto de la consola web. |
| `PORTAINER_VERSION` | Etiqueta de la imagen de Portainer CE. |
| `PORTAINER_HTTPS_HOST_PORT` | Puerto HTTPS de la consola. |
| `BACKEND_CONTEXT` | Ruta al repositorio del backend, usada como contexto de construcción. |
| `FRONTEND_CONTEXT` | Ruta al repositorio del frontend, usada como contexto de construcción. |
| `BLOG_APP_NAME` | Nombre del servicio backend, visible en `/health` y en los logs. |
| `BLOG_LOG_LEVEL` | Nivel de registro del backend. |
| `TRAEFIK_VERSION` | Etiqueta de la imagen de Traefik. |
| `TRAEFIK_HTTP_HOST_PORT` | **Puerto del sitio y del API.** Cambiarlo obliga a reconstruir el frontend. |

**`BLOG_DATABASE_URL` no aparece en el `.env`.** La compone el propio Compose a partir de
`POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB`, apuntando al host interno
`postgres:5432`. Así no hay dos sitios donde mantener la misma credencial sincronizada.

> **Variables del host frente a variables del contenedor.** `POSTGRES_HOST_PORT=55432` es
> el puerto **publicado en tu máquina**; dentro de la red de Docker el puerto es `5432` y
> el host es `postgres`. Apuntar el backend a `127.0.0.1:55432` desde dentro de un
> contenedor lo haría hablar consigo mismo, no con PostgreSQL.

---

## 4. Arranque

Desde la raíz de `personal-blog-infra`:

```powershell
# 1. Crear el archivo de configuración local (solo la primera vez)
Copy-Item .env.example .env

# 2. Validar la definición antes de levantar nada
docker compose config --quiet

# 3. Descargar las imágenes de terceros
docker compose pull postgres minio portainer traefik

# 4. Construir las imágenes de las aplicaciones
#    Requiere que personal-blog-backend y personal-blog-frontend esten
#    clonados como carpetas hermanas de este repositorio.
docker compose build

# 5. Levantar el entorno
docker compose up -d

# 6. Comprobar el estado
docker compose ps
```

Estado esperado tras 30–60 segundos:

```
NAME                            STATUS
personal-blog-local-backend     Up (healthy)
personal-blog-local-frontend    Up (healthy)
personal-blog-local-minio       Up (healthy)
personal-blog-local-portainer   Up
personal-blog-local-postgres    Up (healthy)
personal-blog-local-traefik     Up (healthy)
```

`portainer` aparece como `Up` sin sufijo de salud: su imagen es *distroless* y no
contiene ningún binario con el que sondearla desde dentro. Se verifica desde el host
(sección 6).

El arranque está **encadenado por salud**, no por tiempo. Toda la cadena de dependencias
usa `service_healthy`, sin ningún `service_started` ni espera fija:

```
PostgreSQL healthy         -> backend habilitado
backend healthy            -> frontend habilitado
backend + frontend healthy -> Traefik habilitado
```

Compruébalo cuando quieras sin levantar nada:

```powershell
docker compose config | Select-String -Pattern "service_healthy" -Context 1,0
```

Al terminar, abre **`http://localhost:8081/`**.

### Reconstruir tras un cambio de código

```powershell
# Backend: cambio en personal-blog-backend
docker compose build backend
docker compose up -d backend

# Frontend: cambio en personal-blog-frontend, o cambio de TRAEFIK_HTTP_HOST_PORT
docker compose build frontend
docker compose up -d frontend

# Traefik: cambio en docker/traefik/traefik.yml (configuracion ESTATICA)
docker compose restart traefik
```

> **`docker/traefik/dynamic/routes.yml` se recarga solo.** La configuración **estática**
> (`traefik.yml`) solo se lee al arrancar: un `docker compose up -d` no basta si el
> contenedor ya existe, hay que **reiniciarlo**.

---

## 5. Parada

```powershell
# Detener sin eliminar contenedores
docker compose stop

# Detener y eliminar contenedores y redes — LOS DATOS SE CONSERVAN
docker compose down

# Reiniciar los servicios en marcha
docker compose restart
```

> **Reconstruir un contenedor no destruye datos.** `traefik`, `frontend` y `backend` no
> tienen volúmenes: se pueden eliminar y recrear sin ninguna precaución. Los datos viven
> únicamente en los tres volúmenes de `postgres`, `minio` y `portainer`.

> **Nunca ejecutes `docker compose down -v` salvo que quieras destruir los datos.**
> La bandera `-v` elimina los volúmenes: base de datos, objetos de MinIO y
> configuración de Portainer. Antes de hacerlo, **toma una copia** con el procedimiento de
> [local-backup-and-recovery.md](local-backup-and-recovery.md) (`Task/004`, aprobada).
> *(Corregido en `Task/005.7`: aquí se leía «hasta entonces, no hay backup».)*

---

## 6. Verificación

### 6.1 Estado y salud

```powershell
docker compose ps
docker inspect --format "{{.State.Health.Status}}" personal-blog-local-postgres
docker inspect --format "{{.State.Health.Status}}" personal-blog-local-minio
docker inspect --format "{{.State.Health.Status}}" personal-blog-local-backend
docker inspect --format "{{.State.Health.Status}}" personal-blog-local-frontend
docker inspect --format "{{.State.Health.Status}}" personal-blog-local-traefik
```

Los cinco deben responder `healthy`. `portainer` no tiene sonda: se verifica en 6.4.

### 6.2 PostgreSQL

```powershell
# Desde el contenedor
docker compose exec postgres psql -U blog_local -d personal_blog -c "SELECT version();"

# El puerto responde en el host
Test-NetConnection -ComputerName 127.0.0.1 -Port 55432
```

Cadena de conexión para el backend (`Task/005`), con los valores de tu `.env`:

```
postgresql://<POSTGRES_USER>:<POSTGRES_PASSWORD>@127.0.0.1:55432/<POSTGRES_DB>
```

Desde otro contenedor de la red `blog-data`, el host es `postgres` y el puerto `5432`.

### 6.3 MinIO

```powershell
# Salud de la API S3
Invoke-WebRequest -Uri "http://127.0.0.1:9000/minio/health/live" -UseBasicParsing

# Consola web
Start-Process "http://127.0.0.1:9001"
```

El cliente `mc` viene incluido en la imagen. Su configuración vive **fuera** del
volumen de datos, así que el alias debe reestablecerse cada vez que el contenedor se
recrea:

```powershell
docker compose exec minio sh -c 'mc alias set local http://127.0.0.1:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"'
docker compose exec minio mc ls local
```

> En PowerShell, usa comillas **simples** para el argumento de `sh -c`: con comillas
> dobles, PowerShell expande `$MINIO_ROOT_USER` antes de enviarlo al contenedor y el
> comando falla con `Invalid access key`.

### 6.4 Portainer

```powershell
Start-Process "https://127.0.0.1:9444"
```

En el primer acceso, Portainer pide crear el usuario administrador inicial. Ese
usuario:

- Es **de Portainer**, no del blog. No comparte nada con el panel administrativo
  (`/admin`) del sitio.
- Se guarda en el volumen `personal-blog-local_portainer_data`.
- Debe crearse en los primeros minutos tras el arranque; si no, Portainer bloquea la
  inicialización por seguridad y hay que reiniciar el contenedor.
- **Es la única barrera** frente a la capacidad administrativa de Portainer sobre el
  daemon de Docker (sección 2.1). Usa una contraseña fuerte.

El certificado HTTPS es autofirmado: el navegador mostrará un aviso. Es esperado.

### 6.5 Aislamiento de red

```powershell
docker network inspect personal-blog-local-data --format "{{range .Containers}}{{.Name}} {{end}}"
docker network inspect personal-blog-local-edge --format "{{range .Containers}}{{.Name}} {{end}}"
docker network inspect personal-blog-local-management --format "{{range .Containers}}{{.Name}} {{end}}"
```

`portainer` debe aparecer **solo** en `management`; `postgres` y `minio` **solo** en
`data`; `traefik` y `frontend` **solo** en `edge`; y `backend` en **ambas**, `data` y
`edge`.

Comprobación activa de que el frontend **no** alcanza la capa de datos: debe fallar.

```powershell
docker compose exec frontend sh -c "nc -z -w3 postgres 5432"   # error esperado
docker compose exec frontend sh -c "nc -z -w3 minio 9000"      # error esperado
docker compose exec traefik  sh -c "nc -z -w3 postgres 5432"   # error esperado
```

> Esto confirma el aislamiento **de red**. No confirma —ni pretende confirmar— una
> limitación de privilegios: Portainer sigue pudiendo administrar esos contenedores a
> través del daemon de Docker. Ver sección 2.1.

### 6.6 Persistencia

```powershell
# Escribir
docker compose exec postgres psql -U blog_local -d personal_blog -c "CREATE TABLE IF NOT EXISTS prueba (id serial primary key, nota text);"
docker compose exec postgres psql -U blog_local -d personal_blog -c "INSERT INTO prueba (nota) VALUES ('persistencia');"

# Reiniciar destruyendo los contenedores, sin tocar los volúmenes
docker compose down
docker compose up -d

# Leer
docker compose exec postgres psql -U blog_local -d personal_blog -c "SELECT * FROM prueba;"

# Limpiar
docker compose exec postgres psql -U blog_local -d personal_blog -c "DROP TABLE prueba;"
```

### 6.7 Sitio y API a través del proxy

Es la comprobación que cierra la ETAPA 02: el navegador solo habla con Traefik.

```powershell
# Sitio -> 200, HTML
curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:8081/

# API -> 200, JSON del backend real
curl.exe -s http://localhost:8081/health

# Fallback de la SPA: cualquier ruta devuelve index.html, no un 404 del servidor
curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:8081/una-ruta-inexistente

# OpenAPI del backend, tambien por el proxy
curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:8081/openapi.json
```

Respuesta esperada de `/health`:

```json
{"status":"ok","service":"personal-blog-backend","version":"0.1.0"}
```

**Comprobación visual (la que de verdad demuestra el criterio):** abre
`http://localhost:8081/` en el navegador. Bajo *Estado del backend* debe leerse
**«Backend disponible»**, con el nombre del servicio y la versión que devolvió el API. Si
dice **«Backend sin respuesta»**, el sitio se está sirviendo pero el API no responde: mira
los logs del backend (sección 7).

Qué ruta sirvió cada petición, según Traefik:

```powershell
docker compose logs traefik | Select-String '"RouterName"' | Select-Object -Last 5
```

`RouterName` debe ser `backend@file` para `/health` y `frontend@file` para el resto.

### 6.8 Backend contra PostgreSQL

```powershell
# A que host y base se conecta, con la contrasena enmascarada
docker compose exec backend python -c "from app.shared.configuration import get_settings; print(get_settings().database_url_safe)"

# Estado de las migraciones desde el entorno integrado
docker compose exec backend alembic current
```

Esperado: `postgresql://blog_local:***@postgres:5432/personal_blog` y `0001 (head)`.

> **Nunca imprimas `BLOG_DATABASE_URL` completa.** Lleva la contraseña. `database_url_safe`
> existe justo para esto (requisito S-08).

### 6.9 Observabilidad: sondas y correlation ID (`Task/017`)

#### `/health` y `/ready` no responden a la misma pregunta

| Sonda | Pregunta | Consulta dependencias | Quién la consume |
| --- | --- | --- | --- |
| `GET /health` | ¿El **proceso** está vivo? | **No** | `HEALTHCHECK` del `Dockerfile` del backend |
| `GET /ready` | ¿Puede **atender tráfico** con sus dependencias? | **Sí**: PostgreSQL y almacenamiento | `healthCheck` del servicio backend en Traefik |

La separación es deliberada. Durante un incidente de dependencias, `/health` sigue en `200`
y el contenedor sigue **sano y en marcha**, así que sus logs siguen siendo consultables
desde Portainer; `/ready` pasa a `503` y Traefik retira el backend de rotación. Si Docker
sondara `/ready`, un PostgreSQL caído marcaría el backend como *unhealthy* y complicaría
justamente el diagnóstico.

```powershell
curl.exe -s http://localhost:8081/health
curl.exe -s http://localhost:8081/ready
```

Respuestas esperadas:

```json
{"status":"ok","service":"personal-blog-backend","version":"0.1.0"}
{"status":"ready"}
```

#### Interpretar un `503` de `/ready`

`{"status":"not_ready"}` con código `503`. **El cuerpo no dice qué componente falló**, y es
a propósito: `/ready` es anónimo y decir *«la base de datos está caída»* a un cliente
cualquiera es reconocimiento gratuito (api-contracts §2). **El log sí lo dice**, ya
saneado — ahí es donde mira el operador:

```powershell
docker compose logs backend | Select-String "Dependencia no disponible"
```

La línea lleva `componente` (`base_de_datos` o `almacenamiento`) y un `motivo` sin
credenciales ni cadena de conexión. `/ready` tiene un **presupuesto total** por debajo del
`timeout` del `healthCheck` de Traefik, así que dos dependencias caídas no suman dos
esperas: responde dentro del presupuesto o registra que lo agotó.

#### Seguir una petición con `X-Request-ID`

Toda respuesta —`2xx`, `4xx` y `5xx`— lleva `X-Request-ID`. Si envías uno válido (8–64
caracteres de `A-Za-z0-9-_`) se reutiliza; si no, el backend genera un UUIDv4.

```powershell
# Se ve la cabecera de respuesta
curl.exe -si http://localhost:8081/api/v1/posts | Select-String "x-request-id"

# O se impone uno propio, comodo para buscarlo despues
curl.exe -s -o NUL -H "X-Request-ID: diagnostico-local-001" http://localhost:8081/api/v1/posts
```

Buscarlo en los logs del contenedor:

```powershell
docker compose logs backend | Select-String "diagnostico-local-001"
```

Aparece en **todas** las líneas de esa petición: el evento `app.peticion` —con `method`,
`path`, `status_code` y `duration_ms`—, el manejador de errores si lo hubo, y `uvicorn.error`
si la petición terminó en excepción.

> Las sondas satisfactorias (`/health` y `/ready` en `200`) se registran a `DEBUG` para no
> ahogar el log: Traefik las ejecuta cada diez segundos. No las busques a nivel `INFO`.

#### Lo mismo desde Portainer

Portainer lee **el mismo flujo** que `docker compose logs`; no es otra fuente.

1. Abre `https://localhost:9444` e inicia sesión.
2. *Containers* → **`personal-blog-local-backend`** → **Logs**.
3. Marca *Wrap lines* y escribe el identificador en el buscador (**Search**).
4. Cada línea es un JSON con `context.request_id`, `method`, `path`, `status_code` y
   `duration_ms`.

#### Cruzarlo con el historial de auditoría

Cuando la petición fue una **escritura administrativa** —o un intento de acceso—, el mismo
identificador queda en `audit_events.request_id`:

```powershell
docker compose exec postgres psql -U blog_local -d personal_blog -c "SELECT occurred_at, action, entity_type, request_id FROM audit_events WHERE request_id = 'diagnostico-local-001';"
```

Es lo que permite responder *«qué pasó exactamente en esa petición»* con una sola cadena:
respuesta HTTP, líneas de log y evento de auditoría comparten valor. El identificador **no**
se publica en el DTO de `GET /api/v1/admin/audit-events`: cruzarlo es trabajo de operador.

---

## 7. Diagnóstico

| Síntoma | Comprobación | Causa habitual |
| --- | --- | --- |
| `docker compose up` falla al crear el contenedor | `docker compose config --quiet` | `.env` ausente o variable sin definir. |
| `bind: address already in use` | `Get-NetTCPConnection -State Listen \| Where-Object LocalPort -eq 55432` | Puerto ocupado por otro proceso o proyecto. Cambia el puerto en `.env`. |
| `postgres` se queda en `health: starting` | `docker compose logs postgres` | Volumen con datos de una versión mayor distinta de PostgreSQL. |
| `minio` no pasa el healthcheck | `docker compose logs minio` | `MINIO_ROOT_PASSWORD` con menos de 8 caracteres. |
| Portainer muestra "instance timed out" | `docker compose restart portainer` | Pasaron más de 5 minutos desde el arranque sin crear el administrador. |
| `mc` responde `Access Denied` | `mc alias set local ...` | El alias se perdió al recrear el contenedor. No es pérdida de datos. |

### Comandos de diagnóstico

```powershell
# Logs
docker compose logs
docker compose logs -f postgres
docker compose logs --tail 50 minio
docker compose logs --tail 50 backend     # log JSON de FastAPI
docker compose logs --tail 50 frontend    # accesos al sitio estatico
docker compose logs --tail 50 traefik     # log de acceso JSON del proxy

# Recursos y estado
docker compose ps -a
docker stats --no-stream

# Detalle de un contenedor
docker inspect personal-blog-local-postgres

# Historial del healthcheck
docker inspect --format "{{json .State.Health}}" personal-blog-local-postgres
```

Los mismos logs, volúmenes y redes son visibles gráficamente en Portainer
(`https://127.0.0.1:9444`), que es precisamente su función en el proyecto. Desde
`Task/007` deben aparecer allí **los seis contenedores** del entorno.

### Síntomas frecuentes

| Síntoma | Causa probable | Qué hacer |
| --- | --- | --- |
| El sitio carga pero dice **«Backend sin respuesta»** | El backend no arranca o no conecta con PostgreSQL. | `docker compose logs backend`; comprobar 6.8. |
| `/health` devuelve 404 por el proxy | Traefik cargó una configuración vieja. | `docker compose restart traefik`. |
| Un cambio en `traefik.yml` no surte efecto | La configuración **estática** solo se lee al arrancar. | `docker compose restart traefik`, no `up -d`. |
| El frontend sigue apuntando al puerto anterior | `VITE_API_BASE_URL` se incrusta en tiempo de *build*. | `docker compose build frontend && docker compose up -d frontend`. |
| `docker compose build` falla al no encontrar el contexto | Los repositorios no están como carpetas hermanas. | Ajustar `BACKEND_CONTEXT` / `FRONTEND_CONTEXT` en el `.env`. |
| El puerto `8081` está ocupado | Otro proyecto lo usa. | Cambiar `TRAEFIK_HTTP_HOST_PORT` **y reconstruir el frontend**. |

---

## 8. Reconstrucción desde cero

> **Destruye todos los datos locales.** El procedimiento completo de respaldo previo y
> recuperación está disponible y validado en
> [local-backup-and-recovery.md](local-backup-and-recovery.md) (`Task/004`, aprobada):
> toma una copia **antes** de ejecutar lo siguiente.
> *(Corregido en `Task/005.7`: aquí se condicionaba la recuperabilidad a que `Task/004`
> estuviera aprobada, cosa que ya ocurrió.)*

```powershell
docker compose down -v
docker compose pull
docker compose up -d
docker compose ps
```

---

## 9. Base de datos de pruebas del backend

> **Vigente desde `Task/005.6`.** Necesaria para ejecutar las pruebas de integración de
> `personal-blog-backend`.

### 9.1 Por qué existe una segunda base

Las pruebas de integración ejecutan el ciclo real de migraciones, que incluye
**`alembic downgrade base`**: revierte el esquema entero. Ejecutarlo contra `personal_blog`
—la base cotidiana de desarrollo— **destruiría los datos** en cuanto `Task/008` cree las
primeras tablas del blog.

Por eso la integración usa una base **dedicada y descartable**, `personal_blog_test`, dentro
del mismo contenedor de PostgreSQL. No hace falta un segundo servicio ni tocar
`docker-compose.yml`: una base adicional es la solución más pequeña que resuelve el problema.

### 9.2 Crear la base (idempotente y no destructivo)

Ninguno de estos comandos toca `personal_blog`, sus datos ni los volúmenes.

```powershell
# 1. ¿Existe ya?
docker exec personal-blog-local-postgres `
  psql -U blog_local -d postgres -tAc `
  "SELECT 1 FROM pg_database WHERE datname='personal_blog_test'"

# 2. Crearla solo si el paso anterior no devolvió nada
docker exec personal-blog-local-postgres `
  psql -U blog_local -d postgres -v ON_ERROR_STOP=1 -c `
  "CREATE DATABASE personal_blog_test OWNER blog_local ENCODING 'UTF8'"
```

### 9.3 Marcarla como base de pruebas — **obligatorio**

Sin esta marca la suite **se niega a ejecutarse**. Es deliberado: la guarda no puede depender
de que alguien escriba bien una URL.

```powershell
docker exec personal-blog-local-postgres `
  psql -U blog_local -d postgres -v ON_ERROR_STOP=1 -c `
  "COMMENT ON DATABASE personal_blog_test IS 'personal-blog:test-database - contenido descartable. Las pruebas de integracion ejecutan alembic downgrade base contra esta base.'"
```

El comentario debe contener la cadena exacta **`personal-blog:test-database`**. La marca vive
**dentro** de la base a propósito: apuntar por error a `personal_blog` no la encuentra, y
`personal_blog` **no debe tener nunca** esta marca.

Verificación:

```powershell
docker exec personal-blog-local-postgres `
  psql -U blog_local -d postgres -tAc `
  "SELECT datname, shobj_description(oid,'pg_database') FROM pg_database WHERE datname LIKE 'personal_blog%' ORDER BY 1"
```

`personal_blog` debe aparecer **sin** comentario.

### 9.4 Apuntar las pruebas a esa base

La variable **no** lleva el prefijo `BLOG_`: la suite limpia ese prefijo del entorno para
aislarse de la configuración de la máquina.

```powershell
$env:PERSONAL_BLOG_TEST_DATABASE_URL = "postgresql://<usuario>:<clave>@127.0.0.1:55432/personal_blog_test"
```

Usuario y clave son los de `POSTGRES_USER` y `POSTGRES_PASSWORD` del `.env` local. **No se
versiona ningún valor real**: aquí solo hay marcadores de posición.

### 9.5 Comportamiento esperado

| Situación | Resultado |
| --- | --- |
| Variable **no definida** | La integración se **omite** (`SKIP`) con motivo explícito. |
| Variable definida y base correcta | La integración **se ejecuta**. |
| Variable definida y PostgreSQL caído o credenciales incorrectas | **FAIL.** Nunca `skip`. |
| Destino sin sufijo `_test` | **FAIL** antes de ejecutar nada. |
| Destino sin la marca de §9.3 | **FAIL** antes de ejecutar nada. |

Regla completa:
[BACKEND_TESTING_STRATEGY §8.3](../project-management/BACKEND_TESTING_STRATEGY.md).

### 9.6 Eliminar la base de pruebas

Es descartable: se puede borrar y volver a crear con §9.2 y §9.3 cuando haga falta.

```powershell
docker exec personal-blog-local-postgres `
  psql -U blog_local -d postgres -c "DROP DATABASE IF EXISTS personal_blog_test"
```

> Comprobar el nombre antes de ejecutarlo. `personal_blog` y `personal_blog_test` se
> diferencian en un sufijo.

---

## 10. Bucket de medios del backend

> **Vigente desde `Task/010`.** Necesario para que el backend pueda guardar
> imágenes en el entorno local.

### 10.1 Por qué hay que crearlo a mano

**Ni `MinIOStorage` ni `S3Storage` crean buckets.** No es un olvido: crear un
bucket es una operación de **infraestructura**, y en producción la hace
Terraform (`Task/030`). Un adaptador que creara su bucket al arrancar
convertiría un despliegue en una operación de infraestructura silenciosa, fuera
de la fuente de verdad (AWS LOCAL PARITY LAW).

En local, por tanto, se crea una vez y ya está.

> **No hace falta para ejecutar las pruebas.** La suite crea y destruye **su
> propio** bucket, con el prefijo `personal-blog-test-`. Este bucket es para
> usar la aplicación, no para probarla.

### 10.2 Crearlo

Desde la consola web de MinIO, en `http://localhost:9001`, con las credenciales
`MINIO_ROOT_USER` y `MINIO_ROOT_PASSWORD` del `.env`: **Buckets → Create
Bucket**, nombre `personal-blog-media`. **Sin acceso público**: el bucket es
privado por diseño (security-boundaries.md, C-08) y las imágenes se sirven con
URL prefirmada.

O desde la línea de comandos, con el cliente que la propia imagen ya trae:

```powershell
docker compose exec minio sh -c 'mc alias set local http://127.0.0.1:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" && mc mb --ignore-existing local/personal-blog-media'
```

Comprobar:

```powershell
docker compose exec minio sh -c 'mc alias set local http://127.0.0.1:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null && mc ls local'
```

El nombre debe coincidir con `BLOG_STORAGE_BUCKET`. Si no coincide, el backend
arranca igual —el cliente se crea de forma perezosa— y falla en la primera
subida.

### 10.3 Los dos endpoints de MinIO, y por qué son dos

El backend usa **dos direcciones** hacia el mismo MinIO, y no es una duplicación:

| Variable | Valor en Compose | Quién lo usa |
| --- | --- | --- |
| `BLOG_STORAGE_ENDPOINT_URL` | `http://minio:9000` | El **backend**, para leer y escribir |
| `BLOG_STORAGE_ACCESS_ENDPOINT_URL` | `http://localhost:9000` | Aparece en el enlace temporal que devuelve la API, y lo consume el **navegador del host** |

El contenedor del backend alcanza MinIO por el nombre de servicio de la red de
Docker; el navegador de la persona, no —`minio` no resuelve fuera de esa red—.

**Y el enlace no se puede corregir después de emitirlo.** El anfitrión forma
parte de la firma AWS Signature Version 4: cambiarlo en la URL ya firmada
produce `403 SignatureDoesNotMatch`. Por eso el enlace se firma directamente
contra el endpoint de acceso.

El puerto sale de `MINIO_API_HOST_PORT`, así que cambiarlo ajusta los dos a la
vez. **Si cambias cualquiera de las dos variables, recrea el backend:**

```powershell
docker compose up -d --build backend
```

Nunca con `down -v`: eso destruiría los volúmenes de PostgreSQL y de MinIO.

Ejecutando el backend **directamente en el host** —fuera de Compose— los dos
coinciden y `BLOG_STORAGE_ACCESS_ENDPOINT_URL` se puede omitir.

### 10.4 Buckets residuales de pruebas

La suite borra su bucket al terminar, pero esa limpieza vive en un `finally` y
**no sobrevive a un `SIGKILL`**: si se corta la ejecución, queda el bucket con
sus objetos. Es inofensivo y reconocible por el prefijo. Para purgarlos:

```powershell
docker compose exec minio sh -c 'mc alias set local http://127.0.0.1:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null && mc ls local | grep personal-blog-test-'
```

Borrar **solo** los que lleven ese prefijo. `personal-blog-media` es el bucket
de desarrollo y no se toca.

---

### 10.5 PostgreSQL no arranca: «ports are not available»

Síntoma, tras reiniciar Docker Desktop o el equipo:

```
ports are not available: exposing port TCP 127.0.0.1:55432 -> ...
bind: An attempt was made to access a socket in a way forbidden by its
access permissions.
```

Y una variante más engañosa: el contenedor aparece **`Up (healthy)`** pero
`docker compose ps` muestra `5432/tcp` **sin** `127.0.0.1:55432->`, así que el
backend en Docker funciona y todo lo que ataque la base **desde el host** —las
pruebas de integración, `psql`, un cliente gráfico— falla con *connection
timeout*. Ocurre cuando el contenedor se creó mientras el puerto estaba libre y
Docker ya no pudo re-establecer el enlace al reiniciarse.

**Causa.** Windows reserva rangos de puertos dinámicos para Hyper-V y WSL, y
uno de ellos puede acabar conteniendo el 55432. Comprobarlo:

```powershell
netsh interface ipv4 show excludedportrange protocol=tcp
```

Si aparece un intervalo que contiene 55432 —por ejemplo `55396–55495`—, el
puerto no es de Docker mientras esa reserva exista.

**Remedio**, en PowerShell **como administrador**:

```powershell
net stop winnat
net start winnat
```

Después, sin privilegios:

```powershell
docker compose up -d postgres
docker compose ps        # debe mostrar 127.0.0.1:55432->5432/tcp
```

**No hace falta `down -v`, y no debe usarse.** Los datos viven en el volumen con
nombre `personal-blog-local_postgres_data`, que sobrevive a recrear el
contenedor; `down -v` sí los destruiría.

> Observado el 2026-08-30 durante `Task/010`. Si la reserva reaparece a menudo,
> la alternativa sin administrador es publicar PostgreSQL en un puerto fuera de
> los rangos reservados, lo que obliga a actualizar `POSTGRES_HOST_PORT` y las
> referencias documentadas.

## 11. Límites vigentes de este entorno

| Elemento | Estado | Dónde se aborda |
| --- | --- | --- |
| Backend (FastAPI) | **Integrado** en el Compose. Expone `/health` y los diez recursos públicos (`Task/009`). Desde `Task/010` habla con MinIO a través de `ObjectStorage` y necesita el bucket de §10. | — |
| Frontend (React) | **Integrado** en el Compose (`Task/007`). Desde `Task/014` sirve el **sitio público completo** —doce rutas— consumiendo los diez recursos públicos del API (`Task/009`); ya **no** consulta `/health`. Sin semilla local (`Task/022`) el perfil responde `404` y los listados están vacíos: el sitio lo muestra como estados explícitos, no como error. | `Task/015` (panel), `Task/022` (semilla) |
| Reverse proxy | **Desplegado**: **Traefik v3** con enrutado explícito por archivo (D-05, `Task/003`; implementado en `Task/007`). | — |
| Uso aplicativo de MinIO | **No existe.** MinIO está levantado y es alcanzable desde el backend, pero el backend **no lee ni escribe un solo objeto**: no hay `ObjectStorage`, ni SDK de S3, ni buckets de aplicación. | `Task/010` |
| CORS | **No configurado, y es correcto.** Sitio y API comparten origen tras Traefik, así que el navegador no lo exige. La política de orígenes se decide en `Task/011` (**D-15**). | `Task/011`, `Task/018` |
| Autenticación | No existe. Ningún endpoint está protegido. | `Task/011` |
| Esquema de base de datos y migraciones | Existe la **migración fundacional** de `Task/005`: `personal_blog` tiene `alembic_version` y **ninguna tabla de negocio**. El modelo del blog llega en `Task/008`. *(Corregido en `Task/005.6`: aquí se leía «No existen. La base está vacía».)* | `Task/008` |
| Base de datos de pruebas | `personal_blog_test`, dedicada y descartable (sección 9). | `Task/005.6` |
| Buckets de la aplicación | No se crea ninguno. | `Task/010` |
| Backup y restauración | **Disponibles en local.** `Task/004` está aprobada: `scripts/backup/` genera copias de PostgreSQL, MinIO y Portainer, y el procedimiento de restauración está validado. Ver [local-backup-and-recovery.md](local-backup-and-recovery.md). **No cubre producción**, que llega con `Task/029` y la ETAPA 10. *(Corregido en `Task/005.7`: aquí se leía «No existen», que dejó de ser cierto al aprobarse `Task/004`.)* | `Task/004` (local) |
| TLS real | No hay. Portainer usa un certificado autofirmado. | No aplica en local |
| Control de solo lectura sobre la Docker API | **No existe.** El `:ro` del socket no lo proporciona (sección 2.1). Requeriría un socket proxy o una política adicional. | Fuera del alcance actual; a evaluar en `Task/018` |
| Recursos cloud | **Ninguno.** | Etapas 09 y 10 |

---

## 12. Documentos relacionados

- [ADR-001 — Estrategia local-first](../adr/ADR-001-local-first.md)
- [ADR-003 — Nube serverless de bajo costo](../adr/ADR-003-serverless-low-cost-cloud.md)
- [security-boundaries.md](../architecture/security-boundaries.md) — reglas de Portainer.
- [local-to-cloud-mapping.md](../architecture/local-to-cloud-mapping.md) — equivalencia con la nube.
- [target-production-architecture.md](../architecture/target-production-architecture.md) — arquitectura objetivo de producción, y a qué corresponde cada pieza local.
- [ETAPA 01 — Infraestructura Local](../stages/STAGE-01-local-infrastructure.md)
- [ETAPA 02 — Fundaciones de las Aplicaciones](../stages/STAGE-02-application-foundations.md)
- [TASK-003](../tasks/TASK-003-create-local-infrastructure.md) — ficha de la infraestructura local.
- [TASK-007](../tasks/TASK-007-local-integration.md) — ficha de la integración local.
