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
| `postgres` | `postgres:17.10-alpine` | Persistencia relacional del blog. | `blog-data` |
| `minio` | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | Almacenamiento de objetos compatible con S3. | `blog-data` |
| `portainer` | `portainer/portainer-ce:2.39.5` | Supervisión de Docker en local. | `blog-management` |

Las versiones están fijadas en `.env.example`. No se usa `latest` en ningún servicio:
un entorno reproducible no puede depender de una etiqueta móvil.

### Puertos publicados

Todos se publican en la interfaz de loopback (`127.0.0.1`), nunca en `0.0.0.0`.

| Servicio | Host | Contenedor | Uso |
| --- | --- | --- | --- |
| PostgreSQL | `55432` | `5432` | Conexión desde el backend y desde herramientas locales. |
| MinIO — API S3 | `9000` | `9000` | Cliente S3 (`ObjectStorage`, `Task/010`). |
| MinIO — consola | `9001` | `9001` | Interfaz web de administración de buckets. |
| Portainer | `9444` | `9443` | Consola HTTPS de supervisión. |

> **Por qué `55432` y no `5432`:** evita el choque con una instalación nativa de
> PostgreSQL o con otro proyecto Docker en la misma máquina.
> **Por qué `9444` y no `9443`:** evita el choque con otra instancia de Portainer.

### Redes

| Red | Contiene | Motivo |
| --- | --- | --- |
| `personal-blog-local-data` | `postgres`, `minio` | Datos del blog. El backend se unirá en `Task/007`. |
| `personal-blog-local-management` | `portainer` | Portainer está **aislado por red** de PostgreSQL y MinIO: no puede alcanzarlos como cliente. Esa separación **no limita** lo que Portainer puede hacer sobre esos contenedores a través del daemon de Docker — ver sección 3.1. |

### Volúmenes

| Volumen | Montaje | Contiene |
| --- | --- | --- |
| `personal-blog-local_postgres_data` | `/var/lib/postgresql/data` | Base de datos. |
| `personal-blog-local_minio_data` | `/data` | Objetos y buckets. |
| `personal-blog-local_portainer_data` | `/data` | Configuración y usuarios de Portainer. |

Son volúmenes gestionados por Docker, no *bind mounts*: sobreviven a
`docker compose down` y evitan los problemas de permisos y rendimiento de los
*bind mounts* en Windows.

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

---

## 4. Arranque

Desde la raíz de `personal-blog-infra`:

```powershell
# 1. Crear el archivo de configuración local (solo la primera vez)
Copy-Item .env.example .env

# 2. Validar la definición antes de levantar nada
docker compose config --quiet

# 3. Descargar las imágenes
docker compose pull

# 4. Levantar el entorno
docker compose up -d

# 5. Comprobar el estado
docker compose ps
```

Estado esperado tras 20–40 segundos:

```
NAME                            STATUS
personal-blog-local-minio       Up (healthy)
personal-blog-local-portainer   Up
personal-blog-local-postgres    Up (healthy)
```

`portainer` aparece como `Up` sin sufijo de salud: su imagen es *distroless* y no
contiene ningún binario con el que sondearla desde dentro. Se verifica desde el host
(sección 6).

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
```

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
docker network inspect personal-blog-local-management --format "{{range .Containers}}{{.Name}} {{end}}"
```

`portainer` debe aparecer **solo** en `management`; `postgres` y `minio` **solo** en
`data`.

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

# Recursos y estado
docker compose ps -a
docker stats --no-stream

# Detalle de un contenedor
docker inspect personal-blog-local-postgres

# Historial del healthcheck
docker inspect --format "{{json .State.Health}}" personal-blog-local-postgres
```

Los mismos logs, volúmenes y redes son visibles gráficamente en Portainer
(`https://127.0.0.1:9444`), que es precisamente su función en el proyecto.

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

## 10. Límites vigentes de este entorno

| Elemento | Estado | Dónde se aborda |
| --- | --- | --- |
| Backend (FastAPI) | No incluido. | `Task/005`, `Task/007` |
| Frontend (React) | No incluido. | `Task/006`, `Task/007` |
| Reverse proxy | No desplegado. Tecnología ya decidida: **Traefik v3** (D-05, resuelta en `Task/003`). | `Task/007` |
| Esquema de base de datos y migraciones | Existe la **migración fundacional** de `Task/005`: `personal_blog` tiene `alembic_version` y **ninguna tabla de negocio**. El modelo del blog llega en `Task/008`. *(Corregido en `Task/005.6`: aquí se leía «No existen. La base está vacía».)* | `Task/008` |
| Base de datos de pruebas | `personal_blog_test`, dedicada y descartable (sección 9). | `Task/005.6` |
| Buckets de la aplicación | No se crea ninguno. | `Task/010` |
| Backup y restauración | **Disponibles en local.** `Task/004` está aprobada: `scripts/backup/` genera copias de PostgreSQL, MinIO y Portainer, y el procedimiento de restauración está validado. Ver [local-backup-and-recovery.md](local-backup-and-recovery.md). **No cubre producción**, que llega con `Task/029` y la ETAPA 10. *(Corregido en `Task/005.7`: aquí se leía «No existen», que dejó de ser cierto al aprobarse `Task/004`.)* | `Task/004` (local) |
| TLS real | No hay. Portainer usa un certificado autofirmado. | No aplica en local |
| Control de solo lectura sobre la Docker API | **No existe.** El `:ro` del socket no lo proporciona (sección 2.1). Requeriría un socket proxy o una política adicional. | Fuera del alcance actual; a evaluar en `Task/018` |
| Recursos cloud | **Ninguno.** | Etapas 09 y 10 |

---

## 11. Documentos relacionados

- [ADR-001 — Estrategia local-first](../adr/ADR-001-local-first.md)
- [ADR-003 — Nube serverless de bajo costo](../adr/ADR-003-serverless-low-cost-cloud.md)
- [security-boundaries.md](../architecture/security-boundaries.md) — reglas de Portainer.
- [local-to-cloud-mapping.md](../architecture/local-to-cloud-mapping.md) — equivalencia con la nube.
- [ETAPA 01 — Infraestructura Local](../stages/STAGE-01-local-infrastructure.md)
- [TASK-003](../tasks/TASK-003-create-local-infrastructure.md) — ficha de la tarea.
