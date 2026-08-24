# TASK-007 — Integración local

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/007-Integracion-Local` |
| **Nombre** | Integración local |
| **Etapa** | ETAPA 02 — Fundaciones de las Aplicaciones |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las 41 |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-infra` · `personal-blog-frontend` |
| **Repositorios leídos y NO modificados** | `personal-blog-backend` |
| **Dependencias** | `Task/005` — Aprobada ✔ (2026-08-12) · `Task/006` — Aprobada ✔ (2026-08-18) |
| **Rama** | `Task/007-Integracion-Local` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base — infra** | `a6412f3a17e0027046b8078d1803c8c2bc8af1c1` |
| **SHA base — frontend** | `c4af3617713e4550c75d63b715db722b69bf2a79` |
| **Fecha de inicio** | 2026-08-23 |
| **Fecha de aprobación** | 2026-08-23 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/007-Integracion-Local` |
| **Efecto en el avance** | **7 de 41 (17 %)**; **ETAPA 02 completada** (3 de 3) |
| **Siguiente tarea** | `Task/008-Modelo-de-Datos` — **Pendiente, no iniciada** |

---

## 0. Preparación Git

Verificado en los **tres** repositorios antes de crear ninguna rama: rama activa `main`,
`main == origin/main`, working tree limpio, staging vacío, **0 ramas Task** locales y
remotas.

Tras crear la rama en los dos repositorios que se modifican:
`git rev-parse HEAD` == `git rev-parse main` y `git rev-list --count main..HEAD` == `0`.
**Ninguna nació de `dev`.**

`personal-blog-backend` **no tiene rama**: no se modifica (§4).

## 1. Objetivo

Cerrar los criterios de salida pendientes de la ETAPA 02 integrando las fundaciones ya
aprobadas —React (`Task/006`) y FastAPI (`Task/005`)— con la infraestructura local
(`Task/003`), tras un reverse proxy y supervisadas desde Portainer.

## 2. Diseño

```
navegador
    |
    v
Traefik v3   127.0.0.1:8081
    |
    +-- /health, /api/, /docs, /openapi.json --> backend  (FastAPI)
    |                                              |
    |                                              +--> postgres
    |                                              |
    |                                              + - > minio  (alcanzable,
    |                                                            sin uso aplicativo)
    +-- resto de rutas ------------------------> frontend (React estatico)

    portainer   supervision, red aparte
```

Sitio y API **comparten origen**, así que el navegador trata las llamadas del frontend al
backend como *same-origin* y **no hace falta CORS**.

## 3. Dentro del alcance

- [x] Docker Compose completo: `traefik`, `frontend`, `backend` añadidos al stack
      existente, sin crear un segundo stack.
- [x] Traefik v3 con enrutado **explícito por archivo**, **sin socket de Docker**.
- [x] Backend en Compose con `BLOG_DATABASE_URL` resuelto por DNS interno
      (`postgres:5432`), no por el puerto del host.
- [x] Frontend construido y servido como estático detrás de Traefik.
- [x] **Consumo real** de `GET /health` desde el frontend, con el cliente HTTP oficial y
      con la petición **cancelable** mediante `AbortSignal`.
- [x] Red de borde `blog-edge`, separada de `blog-data`.
- [x] Arranque encadenado por **`service_healthy`** en toda la cadena, sin esperas fijas.
- [x] Runbook del entorno local actualizado.
- [x] `.env.example` de infra y de frontend actualizados.
- [x] Gobierno: `STATUS`, `ROADMAP`, `STAGE-02`, ficha y reporte.

## 4. Fuera del alcance

- **`personal-blog-backend` no se modifica.** Justificado con evidencia en §5.1.
- **Uso aplicativo de MinIO** — `ObjectStorage`, `MinIOStorage`, `S3Storage`, buckets de
  aplicación, SDK de S3, endpoints de medios: todo es de `Task/010`.
- **Modelo de datos del blog** (`Task/008`) y **API pública** (`Task/009`). La base sigue
  en la migración fundacional `0001`, sin tablas de negocio.
- **Autenticación** (`Task/011`) y **API administrativa** (`Task/012`).
- **Sistema de diseño y páginas reales** (`Task/013`–`Task/015`). La pantalla sigue siendo
  provisional y técnica.
- **Observabilidad formal** (`Task/017`), **endurecimiento** (`Task/018`), **CI**
  (`Task/019`–`Task/021`).
- **Cualquier recurso cloud**: AWS, Cloudflare, Grafana, VPS, Terraform, Floci.
- **Rediseñar backups** (`Task/004`): solo se verifica que siguen siendo compatibles.

## 5. Decisiones técnicas

### 5.1 Por qué `personal-blog-backend` no se modifica

La regla del proyecto es no crear una rama Task en un repositorio que no vaya a
modificarse. Se comprobó, punto por punto, si la integración lo exigía:

| Necesidad de la integración | ¿Exige cambio? | Evidencia |
| --- | --- | --- |
| Ejecutarse en contenedor | **No** | El `Dockerfile` de `Task/005` construye y arranca sin cambios; su `HEALTHCHECK` funciona en Compose. |
| Apuntar a PostgreSQL del Compose | **No** | La configuración es por variables de entorno; `BLOG_DATABASE_URL` se inyecta desde el Compose. |
| Exponer un endpoint real al frontend | **No** | `GET /health` ya existe y está fuera de `/api/v1` por diseño. |
| CORS | **No** | Sitio y API comparten origen tras Traefik. `main.py` ya preveía decidirlo aquí; la decisión es **no añadirlo**, que es la opción segura. |
| Migraciones | **No** | Alembic lee `get_settings()`; `alembic current` responde `0001 (head)` dentro del contenedor. |

**Conclusión:** toda la integración se resuelve con **configuración**, que es exactamente
lo que la fundación de `Task/005` prometía. Añadir cambios al backend solo para que
figurara en la tarea habría sido ruido.

Su suite completa se ejecuta igualmente como **regresión** (§8).

### 5.2 Traefik con proveedor de archivo, no de Docker

**D-05** eligió Traefik v3 y su tabla comparativa citaba el descubrimiento por etiquetas
como ventaja de simplicidad. **No se adopta ese mecanismo**, y conviene ser explícito
sobre por qué.

El descubrimiento por etiquetas exige **montar el socket del daemon de Docker** en
Traefik. Quien controla ese socket controla el host: puede crear, detener y eliminar
contenedores y volúmenes de este y de **cualquier otro proyecto de la máquina**. Hoy solo
Portainer tiene ese privilegio y ya está registrado como **R-09**; el emulador de
`Task/025` lo agravará (**R-22**).

Añadir un **tercer** componente privilegiado para ahorrar un archivo de veinte líneas no
es una compensación razonable, y el entorno tiene **dos rutas** que no cambian solas: el
argumento de «descubrimiento automático» no aporta aquí.

**Costo asumido y documentado:** al añadir un servicio HTTP nuevo hay que declararlo en
`docker/traefik/dynamic/routes.yml`. Es bajo, y el archivo se recarga solo.

**Lo que D-05 decidió —Traefik v3 como reverse proxy local— se cumple íntegramente.** Lo
que cambia es el proveedor de configuración, que D-05 no fijaba.

### 5.3 Nginx dentro del contenedor del frontend

El frontend se sirve con `nginx:1.29.3-alpine` **dentro de su propia imagen**. No
contradice la regla de no añadir un segundo proxy: nginx aquí **no enruta nada**, es el
servidor de archivos estáticos.

Hace falta porque el ***fallback* de la SPA** —devolver `index.html` en cualquier ruta del
router de React, incluida su página 404— no lo puede hacer Traefik. Es el equivalente
local exacto de lo que Cloudflare Pages resuelve por su cuenta en producción.

**Escucha en `8080` para no depender de un puerto privilegiado dentro del contenedor, y
nada más.** Eso **no** implica que el proceso corra sin privilegios: la imagen oficial de
nginx arranca su maestro como `root` y solo baja de usuario en los *workers*. El
endurecimiento real de las imágenes —usuario no privilegiado, capacidades, sistema de
archivos de solo lectura— es de **`Task/018`** y **no se adelanta aquí**.

### 5.4 `VITE_API_BASE_URL` apuntando al mismo origen

Vite incrusta las variables `VITE_*` **en tiempo de build**, así que la URL del API se
pasa como `ARG` de construcción. Se apunta al **mismo origen que sirve el sitio**
(`http://localhost:8081`), no a un puerto del backend.

Dos consecuencias buscadas: el navegador trata las peticiones como *same-origin* —sin
CORS— y **no hace falta tocar la validación de `env.ts`**, que exige una URL absoluta.
La contrapartida, documentada en los dos `.env.example` y en el runbook: cambiar el puerto
obliga a reconstruir la imagen del frontend.

### 5.5 Red de borde separada

Se añade `blog-edge` en lugar de meter todo en `blog-data`. Así el **backend es el único
servicio con un pie en cada red**, que es justo el papel que tendrá la Lambda en
producción. Ni Traefik ni el frontend pueden alcanzar PostgreSQL o MinIO — verificado
activamente (§8).

### 5.6 La cancelación de la consulta es real

`HomePage` crea un `AbortController` y **propaga su `signal` hasta `fetch`** a través de
`fetchBackendHealth(client, signal)` y de `HttpRequestOptions.signal`, que el cliente HTTP
de `Task/006` ya soportaba. Al desmontar, la petición en vuelo **se aborta**; no se queda
corriendo con su resultado descartado.

La comprobación de `signal.aborted` que sigue al `await` **no es redundante**: cubre la
carrera que el abort no puede evitar —que la promesa ya se hubiera resuelto justo antes de
cancelar—. Y un `AbortError` **no** se interpreta como «backend caído».

No se modificó el cliente HTTP: solo se usa una capacidad que ya tenía.

## 6. Correspondencia local → producción

Ninguna decisión de esta tarea contradice la arquitectura objetivo
([target-production-architecture.md](../architecture/target-production-architecture.md)):

| Local (`Task/007`) | Producción |
| --- | --- |
| React servido por nginx en Compose | **Cloudflare Pages** |
| FastAPI en contenedor | **AWS Lambda**, artefacto **ZIP** (no esta imagen) |
| MinIO | **Amazon S3** |
| PostgreSQL en Docker | **PostgreSQL en VPS**, tras **PgBouncer** |
| Traefik v3 | **Cloudflare + API Gateway HTTP API** |
| Portainer | **Nada.** Solo local |

**La sustitución sigue siendo un cambio de configuración y de adaptador**, nunca una
reescritura: la aplicación solo conoce `DATABASE_URL` y `VITE_API_BASE_URL`.

## 7. Riesgos

No se introduce ningún riesgo nuevo. Se confirma que siguen vigentes:

| # | Riesgo | Efecto de `Task/007` |
| --- | --- | --- |
| **R-09** | Portainer conserva capacidad administrativa sobre el host. | **No se agrava**: Traefik **no** recibe el socket (§5.2). Sigue siendo el único componente privilegiado. |
| **R-10** | Las etiquetas de imagen fijadas envejecen. | Se añaden tres imágenes más, todas **con versión fija**. Escaneo en `Task/018`. |
| **R-12** | Los artefactos de respaldo son sensibles. | Sin cambios: `Task/007` no toca `local-backups/`. |
| **R-16** | El `.env` local conserva las contraseñas de ejemplo. | Sin cambios. La contraseña no se duplica: el Compose compone `BLOG_DATABASE_URL` a partir de las variables ya existentes. |

## 8. Validaciones

Todas ejecutadas realmente; los resultados y códigos de salida están en el
[reporte](../task-reports/TASK-007-report.md).

| Ámbito | Validación |
| --- | --- |
| Compose | `config --quiet`, `config --images`, `build`, `up -d`, `ps` |
| Salud | `backend`, `frontend`, `traefik`, `postgres`, `minio` en `healthy`; `portainer` `running` |
| End-to-end | Sitio, `/health`, `/openapi.json` y *fallback* de la SPA por el proxy |
| Navegador | **Chrome headless** renderiza la SPA y muestra «Backend disponible» con el servicio y la versión reales |
| Cancelación | El `signal` entregado a `fetch` es el del controlador, y queda abortado al desmontar |
| Enrutado | Log de acceso de Traefik: `backend@file` para `/health`, `frontend@file` para el resto |
| PostgreSQL | Conexión real desde el backend; `alembic current` == `0001 (head)` |
| Redes | El frontend y Traefik **no** alcanzan PostgreSQL ni MinIO |
| MinIO | `healthy`, alcanzable desde el backend, **0 buckets de aplicación** |
| Portainer | Operativo; consola HTTPS responde |
| Persistencia | 3 volúmenes antes y después; **0 eliminados** |
| Backups | `Test-LocalBackup.ps1 -All` → integridad correcta |
| Frontend | `lint`, `typecheck`, `format:check`, `test:coverage`, `build` |
| Backend | Suite completa, incluida integración |
| Seguridad | 0 binds en `0.0.0.0`; solo Portainer tiene el socket de Docker |

## 9. Pasos de validación para el usuario

1. Levantar el entorno: `docker compose up -d` y comprobar `docker compose ps`.
2. Abrir **`http://localhost:8081/`**. Bajo *Estado del backend* debe leerse **«Backend
   disponible»**, con el nombre del servicio y la versión.
3. Abrir `http://localhost:8081/health` — JSON del backend real.
4. Abrir `http://localhost:8081/una-ruta-inexistente` — la página 404 **de la SPA**, no un
   error del servidor.
5. Abrir **Portainer** (`https://127.0.0.1:9444`) e iniciar sesión: deben verse los
   **seis** contenedores del entorno, sanos. **Esta comprobación está pendiente de ti**:
   no se realizó, porque exige credenciales que no se piden ni se extraen.
6. Comprobar que la base sigue intacta:
   `docker compose exec backend alembic current` → `0001 (head)`.
7. Comprobar que MinIO no tiene buckets de aplicación.

## 10. Aprobación

**Aprobada** por el usuario el 2026-08-23 con la expresión exacta requerida por
[WORKFLOW.md](../project-management/WORKFLOW.md):

```
approved: Task/007-Integracion-Local
```

Con ella, la **ETAPA 02 queda completada** (3 de 3) y el avance global pasa a
**7 de 41 (17 %)**.

> **Comprobación que sigue en manos del usuario:** la validación **visual autenticada** de
> Portainer (§9, paso 5). Lo verificado técnicamente es que Portainer está operativo, que
> es el único contenedor con el socket de Docker y que los seis contenedores existen en ese
> mismo daemon.

`Task/008-Modelo-de-Datos` es la siguiente: **Pendiente, no iniciada**, y nacerá desde
`main`.
