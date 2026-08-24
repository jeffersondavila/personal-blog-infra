# TASK-007 — Reporte de ejecución

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/007-Integracion-Local` |
| **Etapa** | ETAPA 02 — Fundaciones de las Aplicaciones |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las 41 |
| **Estado final** | **Aprobada** ✔ (2026-08-23) |
| **Repositorios modificados** | `personal-blog-infra` · `personal-blog-frontend` |
| **Repositorio leído y NO modificado** | `personal-blog-backend` |
| **Fecha** | 2026-08-23 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/007-Integracion-Local` |
| **Ficha** | [TASK-007](../tasks/TASK-007-local-integration.md) |

---

## 1. Estado inicial

| Repositorio | `main` | `origin/main` | Worktree | Ramas Task |
| --- | --- | --- | --- | --- |
| `personal-blog-infra` | `a6412f3a17e0027046b8078d1803c8c2bc8af1c1` | idéntico | limpio | 0 / 0 |
| `personal-blog-frontend` | `c4af3617713e4550c75d63b715db722b69bf2a79` | idéntico | limpio | 0 / 0 |
| `personal-blog-backend` | `2290a9fbb726f97f6d1cbdb5e4c6b1f1ce147e4c` | idéntico | limpio | 0 / 0 |

Entorno vivo encontrado: `postgres`, `minio` y `portainer` levantados desde hacía 4 días,
con sus 3 volúmenes. Conviven en la máquina contenedores de otro proyecto (`farm-*` y una
segunda instancia de Portainer) que **no se tocaron**, y que ocupan los puertos `8000` y
`8080` — motivo por el que Traefik usa el `8081`.

## 2. Decisión de alcance por repositorio

| Repositorio | ¿Se modifica? | Razón |
| --- | --- | --- |
| `personal-blog-infra` | **Sí** | Compose, configuración de Traefik, `.env.example`, runbook y gobierno. |
| `personal-blog-frontend` | **Sí** | `Dockerfile` y servidor estático para el entorno local, y el **consumo real** del backend. |
| `personal-blog-backend` | **No** | Toda la integración se resuelve con configuración. Evidencia en §3. |

## 3. Por qué el backend no se modifica

Se comprobó punto por punto, antes de decidir:

| Necesidad | ¿Exige cambio? | Evidencia obtenida |
| --- | --- | --- |
| Ejecutarse en contenedor | **No** | `docker compose build backend` termina en **0** con el `Dockerfile` de `Task/005`; el contenedor alcanza `healthy` con su propio `HEALTHCHECK`. |
| Conectar al PostgreSQL del Compose | **No** | `BLOG_DATABASE_URL` se inyecta desde el Compose. Comprobado dentro del contenedor: `postgresql://blog_local:***@postgres:5432/personal_blog`, `server_version` `17.10`, `inet_server_addr` `172.20.0.3` — la IP del contenedor `postgres`. |
| Endpoint real para el frontend | **No** | `GET /health` ya existe y está fuera de `/api/v1` por diseño. |
| CORS | **No** | Sitio y API comparten origen. `main.py` preveía decidirlo en `Task/007`; **la decisión es no añadirlo**, que es la opción segura. |
| Migraciones | **No** | `alembic current` dentro del contenedor → `0001 (head)`; `alembic upgrade head` → exit **0**. |

**Ninguna rama Task se creó en `personal-blog-backend`**, y su `git status` sigue vacío.

## 4. Cambios realizados

### 4.1 `personal-blog-infra`

| Archivo | Cambio |
| --- | --- |
| `docker-compose.yml` | Añadidos `backend`, `frontend` y `traefik`; añadida la red `blog-edge`; toda la cadena de arranque encadenada por **`service_healthy`**; `postgres`, `minio`, `portainer` y los 3 volúmenes **sin tocar**. |
| `docker/traefik/traefik.yml` | **Nuevo.** Configuración estática: *entrypoint* `web`, *entrypoint* interno `ping`, proveedor de **archivo**, panel deshabilitado, log de acceso JSON. |
| `docker/traefik/dynamic/routes.yml` | **Nuevo.** Enrutado explícito: API y sitio, con prioridades y *health checks* de servicio. |
| `.env.example` | `BACKEND_CONTEXT`, `FRONTEND_CONTEXT`, `BLOG_APP_NAME`, `BLOG_LOG_LEVEL`, `TRAEFIK_VERSION`, `TRAEFIK_HTTP_HOST_PORT`. |
| `docs/runbooks/local-environment.md` | Topología, servicios, puertos, URLs, redes, arranque, reconstrucción, verificación 6.5–6.8, diagnóstico y límites. |
| `docs/project-management/STATUS.md` | Sección de tarea en curso, tabla de tareas, distribución por estado. |
| `docs/project-management/ROADMAP.md` | Estado y alcance de `Task/007`. |
| `docs/stages/STAGE-02-application-foundations.md` | Alcance entregado y criterios de salida. |
| `README.md` | Accesos locales y topología del entorno. |
| `docs/tasks/TASK-007-local-integration.md` | **Nuevo.** Ficha. |
| `docs/task-reports/TASK-007-report.md` | **Nuevo.** Este reporte. |

### 4.2 `personal-blog-frontend`

| Archivo | Cambio |
| --- | --- |
| `Dockerfile` | **Nuevo.** Multietapa: `node:22.21.1-alpine` construye, `nginx:1.29.3-alpine` sirve. |
| `docker/nginx.conf` | **Nuevo.** Servidor estático con *fallback* de SPA y caché por tipo de recurso. Escucha en `8080` para no depender de un puerto privilegiado; el endurecimiento *non-root* es de `Task/018`. |
| `.dockerignore` | **Nuevo.** |
| `src/services/health/healthService.ts` | **Nuevo.** Consumo tipado de `GET /health` con el cliente HTTP oficial, con `AbortSignal` opcional propagado hasta `fetch`. |
| `src/services/health/index.ts` | **Nuevo.** Superficie pública. |
| `src/services/health/healthService.test.ts` | **Nuevo.** 9 pruebas, incluidas las de propagación del `signal` y del `AbortError`. |
| `src/pages/HomePage.tsx` | Muestra el estado real del backend. |
| `src/pages/HomePage.test.tsx` | **Nuevo.** 10 pruebas, incluidas las de cancelación real al desmontar. |
| `src/app/App.test.tsx` | `fetch` doblado: la suite sigue **sin tocar la red**. |
| `.env.example` | Documenta el valor tras el proxy y por qué es el mismo origen. |

### 4.3 Lo que NO se tocó

`images/Infraestructura.png` · `personal-blog-backend` · `scripts/backup/` ·
`local-backups/` · los 3 volúmenes · los contenedores ajenos al proyecto · la arquitectura
productiva vigente.

## 5. Validaciones ejecutadas

### 5.1 Docker Compose

| Comando | Resultado |
| --- | --- |
| `docker compose config --quiet` | exit **0** |
| `docker compose config --images` | 6 imágenes, **todas con versión fija**, ninguna `latest` |
| `docker compose build backend` | exit **0** |
| `docker compose build frontend` | exit **0** |
| `docker compose up -d` | exit **0** |

**Cadena de dependencias efectiva, configurada por salud de extremo a extremo:**

```
PostgreSQL healthy -> backend habilitado
backend healthy    -> frontend habilitado
backend + frontend healthy -> Traefik habilitado
```

`docker compose config` confirma que Traefik depende de `backend` **y** de `frontend`
mediante `service_healthy`. Ningún servicio depende de `service_started`, y no hay ninguna
espera fija en el Compose.

> **Alcance de esta evidencia.** La revalidación fue **incremental**: solo se reconstruyó
> `frontend`, y Traefik ya estaba ejecutándose. Por tanto **no se presenta como la
> observación de un arranque completo desde cero**. Lo verificado es la **configuración
> efectiva** y el **estado final** de los seis contenedores, no la secuencia entera de un
> arranque en frío.

Estado tras el arranque:

| Contenedor | Estado |
| --- | --- |
| `personal-blog-local-backend` | `Up (healthy)` |
| `personal-blog-local-frontend` | `Up (healthy)` |
| `personal-blog-local-traefik` | `Up (healthy)` |
| `personal-blog-local-postgres` | `Up 4 days (healthy)` — no recreado |
| `personal-blog-local-minio` | `Up 4 days (healthy)` — no recreado |
| `personal-blog-local-portainer` | `Up 4 days` — sin sonda por diseño, no recreado |

### 5.2 End-to-end por el proxy

| Petición | Resultado |
| --- | --- |
| `GET http://127.0.0.1:8081/` | **200**, `text/html` |
| `GET http://127.0.0.1:8081/health` | **200**, `{"status":"ok","service":"personal-blog-backend","version":"0.1.0"}` |
| `GET http://127.0.0.1:8081/openapi.json` | **200** |
| `GET http://127.0.0.1:8081/una-ruta-inexistente` | **200** — *fallback* de la SPA, no 404 del servidor |

**Ejecución real en navegador (Chrome *headless* 151):** el DOM renderizado contiene
**«Backend disponible»**, `<code>personal-blog-backend</code>` y `<code>0.1.0</code>` — es
decir, el navegador ejecutó la SPA, llamó al backend por el proxy y pintó **la respuesta
real del API**. Sin errores de consola inesperados. La ruta `/ruta-que-no-existe` renderiza
`<h1>404 — pagina no encontrada</h1>`, la página 404 de la SPA.

Log de acceso de Traefik, que confirma el enrutado:

```
GET /health                    -> backend@file   200
GET /ruta-que-no-existe        -> frontend@file  200
GET /assets/index-BcVENnXE.js  -> frontend@file  200
GET /assets/index-D8Wt32uA.css -> frontend@file  200
```

### 5.3 PostgreSQL y migraciones

`host = postgres`, `puerto = 5432`, `base = personal_blog`, `usuario = blog_local`; URL
mostrada **enmascarada** (`:***@`). `server_version` `17.10`, `current_database`
`personal_blog`, `inet_server_addr` `172.20.0.3` (el contenedor `postgres`).
`alembic current` → `0001 (head)`; `alembic upgrade head` → exit **0**, sin cambios.

**Ninguna tabla de negocio creada:** el esquema sigue exactamente como lo dejó `Task/005`.

### 5.4 Redes

| Contenedor | Redes |
| --- | --- |
| `postgres`, `minio` | `data` |
| `backend` | `data` + `edge` |
| `frontend`, `traefik` | `edge` |
| `portainer` | `management` |

Comprobación **activa**, no solo declarativa:

| Prueba | Resultado |
| --- | --- |
| `frontend` → `postgres:5432` | **falla** (`bad address`) — correcto |
| `frontend` → `minio:9000` | **falla** — correcto |
| `traefik` → `postgres:5432` | **falla** — correcto |
| `backend` → `postgres:5432` | conecta — correcto |
| `backend` → `minio:9000` | conecta — correcto (infraestructura alcanzable) |

### 5.5 MinIO — sin adelantar `Task/010`

`healthy`; `GET /minio/health/live` → **200**; alcanzable desde el backend.
**0 buckets de aplicación** (`/data` solo contiene `.minio.sys`).

En `personal-blog-backend`: **0** coincidencias de `ObjectStorage`, `MinIOStorage` o
`S3Storage`; **0** dependencias de `boto3`/SDK de S3; **un único** endpoint registrado,
`/health`. **El backend no leyó ni escribió un solo objeto.**

### 5.6 Portainer

**Demostrado técnicamente:** contenedor `running`; consola HTTPS responde (**307**,
redirección normal a su SPA); sigue siendo el **único** contenedor con
`/var/run/docker.sock` montado —verificado uno por uno en los seis—; y los **seis
contenedores del entorno existen en el mismo daemon** que Portainer administra.

> **Lo que NO se ha comprobado: la validación visual autenticada.** Nadie ha iniciado
> sesión en `https://127.0.0.1:9444` para ver los seis contenedores en su interfaz. Esa
> comprobación **sigue pendiente del usuario**: exigiría credenciales que **no se piden, no
> se extraen y no se restablecen**.
>
> Que los contenedores existan en el daemon es un hecho verificado; que se vean en la
> interfaz de Portainer es una inferencia razonable, **no una observación**.

### 5.7 Persistencia y backups

| Comprobación | Resultado |
| --- | --- |
| Volúmenes antes | 3 (`postgres_data`, `minio_data`, `portainer_data`) |
| Volúmenes después | **los mismos 3** |
| Volúmenes eliminados | **0** |
| Contenedores de datos recreados | **0** — los tres siguen `Up 4 days` |
| Nombres que esperan los scripts de `Task/004` | **intactos** |
| `Test-LocalBackup.ps1 -All` | **INTEGRIDAD CORRECTA — 8 archivos**, 0 problemas, exit **0** |

**No se ejecutó ningún `down -v`, `volume rm`, `volume prune` ni `system prune`.** No se
repitió el restore destructivo completo: no había motivo y el prompt lo desaconseja.

### 5.8 Suite del frontend

| Comando | Exit | Resultado |
| --- | --- | --- |
| `npm run lint` | **0** | Sin hallazgos |
| `npm run typecheck` | **0** | Sin errores |
| `npm run format:check` | **0** | Todo con estilo Prettier |
| `npm run test:coverage` | **0** | **50 pruebas, 50 pasadas, 0 fallos** (antes 31) |
| `npm run build` | **0** | `dist/` generado |

Cobertura: *statements* **100 %**, ramas **98.76 %**, funciones **100 %**, líneas
**100 %**. La única rama sin cubrir está en `httpError.ts`, preexistente de `Task/006`.
`HomePage.tsx` y `healthService.ts` quedan **completamente cubiertos**, incluidas la
propagación del `signal`, el aborto real al desmontar y la carrera en la que la respuesta
llega justo después de cancelar.

### 5.9 Suite del backend — regresión

`git status` de `personal-blog-backend`: **vacío**.

| Ejecución | Exit | Resultado |
| --- | --- | --- |
| Suite por defecto | **0** | **79 pasadas, 17 omitidas** (16 de integración por falta de la variable, 1 propia de Windows) |
| Suite completa con integración | **0** | **95 pasadas, 1 omitida** (`time.tzset` no existe en Windows) |

La integración se ejecutó contra `personal_blog_test`, la base **dedicada y marcada**
(`personal-blog:test-database`). La base de desarrollo quedó intacta: `alembic current`
sigue en `0001 (head)`. **No se habilitó ejecución paralela**; **R-37** sigue siendo de
`Task/020`.

### 5.10 Seguridad

| Comprobación | Resultado |
| --- | --- |
| Puertos en `0.0.0.0` | **0** — todos en `127.0.0.1` |
| Puertos publicados por `backend` y `frontend` | **ninguno** |
| `/var/run/docker.sock` montado | **solo en `portainer`** |
| `/ping` de Traefik alcanzable desde el navegador | **no** — vive en un *entrypoint* interno no publicado |
| Panel de Traefik | **deshabilitado** |
| CORS | **no configurado** — innecesario con mismo origen |
| Secretos versionados | **0** |
| `BLOG_DATABASE_URL` en documentación o reportes | siempre **enmascarada** |

## 5.11 Correcciones aplicadas en la revisión pre-approval

Tres inconsistencias detectadas al revisar la tarea, corregidas antes de la aprobación:

| # | Defecto | Corrección |
| --- | --- | --- |
| 1 | El Compose declaraba `frontend: service_started` para Traefik, mientras la documentación afirmaba que **toda** la cadena iba por salud. La afirmación era falsa. | `frontend: service_healthy`. El frontend ya tenía sonda válida; no hizo falta tocar ningún healthcheck ni añadir esperas. |
| 2 | El `AbortController` de `HomePage` **no cancelaba la petición**: su `signal` nunca llegaba a `fetch`. Solo servía de guarda contra `setState` tras el desmontaje —y los comentarios lo describían como cancelación—. | `fetchBackendHealth(client, signal?)` propaga el `signal` por `HttpRequestOptions.signal`, capacidad que el cliente HTTP **ya tenía**. Comentarios corregidos. Sin tocar el cliente común, sin nuevas abstracciones ni dependencias. |
| 3 | `docker/nginx.conf` afirmaba que se usaba el puerto 8080 porque *«el proceso corre sin privilegios»*. **Falso**: la imagen oficial de nginx arranca su maestro como `root`. Un puerto alto solo evita necesitar privilegios **para el bind**. | Comentario reescrito con la razón correcta, remitiendo el endurecimiento *non-root* a `Task/018`. **No se cambió de imagen ni se adelantó `Task/018`.** |

Revalidación posterior: `docker compose config --quiet` exit **0**; la **configuración
efectiva** declara `backend: service_healthy` y `frontend: service_healthy` como
dependencias de Traefik; los seis contenedores en el estado esperado —`postgres`, `minio`,
`backend`, `frontend` y `traefik` en `healthy`, `portainer` en `running`—; sitio, `/health`
y `/openapi.json` en **200**; Chrome *headless* vuelve a mostrar «Backend disponible» con
`personal-blog-backend` y `0.1.0`, sin errores de consola inesperados; suite del frontend
**50 pruebas, 0 fallos**, todos los comandos en exit **0**.

Esa revalidación fue **incremental** —Traefik seguía en marcha—, así que **no acredita un
arranque completo desde cero**: acredita la configuración y el estado final.

**El backend no se tocó en esta corrección**, así que no se repitió su suite completa:
ninguno de los tres cambios afecta a su integración.

## 6. Problemas encontrados y cómo se resolvieron

1. **El healthcheck de Traefik dejaba el contenedor `unhealthy`.** `traefik healthcheck`
   exige el endpoint `ping` habilitado, y no lo estaba: *«please enable `ping` to use
   health check»*. Se habilitó.
2. **Al habilitarlo, `/ping` quedó accesible desde el puerto del navegador y el comando
   devolvía 400.** Se movió el `ping` a un ***entrypoint* interno** (`:8082`) que **no se
   publica**. Ahora el healthcheck pasa y `/ping` desde fuera cae en el *fallback* de la
   SPA, no en Traefik.
3. **Un cambio en `traefik.yml` no surtía efecto con `up -d`.** La configuración
   **estática** solo se lee al arrancar; solo la dinámica se recarga sola. Se resolvió con
   `restart` y **quedó documentado** en el runbook, con su síntoma en la tabla de
   diagnóstico.
4. **`prettier --check` falló** en un archivo de pruebas nuevo. Se formateó y se volvió a
   verificar.
5. **Dos comprobaciones dieron falsos positivos** durante la auditoría: el patrón `minio`
   coincidía dentro de la palabra «dominio», y un `grep` inexistente dentro del contenedor
   de MinIO. Ambas se rehicieron con patrones exactos.

## 7. Riesgos

**No se introduce ninguno nuevo.** Confirmados sin duplicar: **R-09** (**no se agrava**:
Traefik no recibe el socket), **R-10** (tres imágenes más, todas con versión fija),
**R-12**, **R-16**.

## 8. Estado Git

| Repositorio | Rama | Worktree | Staging | Commits | Push | Merge | PR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `personal-blog-infra` | `Task/007-Integracion-Local` | con cambios | **vacío** | **0** | **0** | **0** | **0** |
| `personal-blog-frontend` | `Task/007-Integracion-Local` | con cambios | **vacío** | **0** | **0** | **0** | **0** |
| `personal-blog-backend` | `main` | **limpio** | vacío | 0 | 0 | 0 | 0 |

## 9. Cómo validar

Ver [la ficha](../tasks/TASK-007-local-integration.md) §9. En resumen: `docker compose up
-d`, abrir `http://localhost:8081/` y comprobar **«Backend disponible»** con el servicio y
la versión; probar una ruta inexistente; y revisar los seis contenedores en Portainer.

## 10. Siguiente tarea

`Task/008-Modelo-de-Datos` — **Pendiente, no iniciada.** Nacerá desde `main`.

## 11. Aprobación y cierre

**Aprobada** por el usuario el 2026-08-23 con la expresión exacta:

```
approved: Task/007-Integracion-Local
```

Efectos registrados en el cierre:

| Elemento | Antes | Después |
| --- | --- | --- |
| `Task/007` | Lista para validación | **Aprobada** ✔ |
| Avance global | 6 / 41 (15 %) | **7 / 41 (17 %)** |
| ETAPA 02 | 2 / 3 — en curso | **3 / 3 — completada** ✔ |
| ETAPA 03 | Pendiente | Pendiente, con su dependencia satisfecha |
| `Task/008` | Pendiente | **Pendiente, siguiente** |

**Sigue pendiente del usuario** la comprobación **visual autenticada** de Portainer: es la
única validación de esta tarea que no se realizó, y deliberadamente.
