# ETAPA 02 — Fundaciones de las Aplicaciones

| Campo | Valor |
| --- | --- |
| **Número** | 02 |
| **Estado** | **Completada** ✔ |
| **Dependencias** | [ETAPA 01](STAGE-01-local-infrastructure.md) — **Completada** ✔ (2026-07-31) |
| **Tareas** | 3 |
| **Aprobadas** | 3 |
| **Avance** | **100 %** |
| **Hito que completa** | Frontend y backend arrancan e integran contra PostgreSQL y MinIO. |
| **Inicio** | 2026-08-01 |
| **Fin** | 2026-08-23 |
| **Última actualización** | 2026-08-23 (`Task/007-Integracion-Local` — **Aprobada**; etapa completada) |

---

## Objetivo

Establecer la base profesional de backend y frontend —estructura, configuración,
logging, pruebas y build— e integrarlos con la infraestructura local a través de un
reverse proxy.

## Por qué esta etapa existe

Definir la base técnica antes que las funcionalidades evita retrabajo: la estructura de
proyecto, el manejo de configuración y la estrategia de pruebas son difíciles de cambiar
una vez que hay dominio construido encima.

## Tareas

### `Task/005-Fundacion-Backend-FastAPI` — **Aprobada** ✔ (2026-08-12)

- [x] Estructura de proyecto FastAPI, monolito modular sin capas vacías.
- [x] Configuración tipada por variables de entorno, validada al arrancar.
- [x] Logging estructurado en JSON, unificado con el del servidor y con marcas de tiempo
      **UTC explícitas**, verificadas en Windows y en Docker.
- [x] Manejo centralizado de errores con el modelo común del proyecto.
- [x] Endpoint de salud `GET /health` y especificación OpenAPI.
- [x] Conexión a PostgreSQL con SQLAlchemy 2 y psycopg 3.
- [x] Alembic para migraciones, con migración fundacional aplicada y revertida.
- [x] Suite de pruebas base (`pytest`): 69 pruebas, cobertura 99 %, `-W error` con 0 warnings
      y sin filtros.
- [x] Lint, formato y tipado estático (`ruff`, `mypy` *strict*).
- [x] `Dockerfile` del backend, imagen construida **con `--no-cache`** y contenedor
      comprobado.

**Depende de:** `Task/004` — Aprobada ✔.
**Repositorios:** `personal-blog-backend` (implementación) · `personal-blog-infra`
(documentación de gobierno).
**Ficha:** [TASK-005](../tasks/TASK-005-fastapi-backend-foundation.md) ·
**Reporte:** [TASK-005-report](../task-reports/TASK-005-report.md)

> **Aprobada** por el usuario el 2026-08-12. Los pull request `Task/005 → main` —`#2` en
> backend y `#6` en infra— fueron **fusionados** el 2026-08-13 y la normalización
> `main → dev` está **completada**. Su alcance excluye deliberadamente `/ready`
> (`Task/017`), CORS (`Task/007`), el modelo de datos (`Task/008`) y la autenticación
> (`Task/011`).

### `Task/006-Fundacion-Frontend-React` — **Aprobada** ✔ (2026-08-18)

- [x] React 19 + TypeScript 5.9 (estricto) + Vite 8, con versiones fijadas sin rango y
      `package-lock.json` versionado.
- [x] Router: tabla de rutas central, ruta inicial y *fallback* 404.
- [x] Configuración de entorno tipada (`VITE_API_BASE_URL`), **validada al arrancar**
      (requisito T-01).
- [x] Cliente HTTP común con `fetch` inyectable y modelo de error alineado con
      [api-contracts.md](../architecture/api-contracts.md) §7.
- [x] Suite de pruebas base (Vitest + Testing Library): **31 pruebas**, cobertura de
      *statements* 100 % y de ramas 98.36 %, sin acceso a red.
- [x] Lint (ESLint), formato (Prettier) y tipado estricto, con *scripts* reproducibles.
- [x] Build de producción estático, verificado desde instalación limpia y **byte a byte
      reproducible**.
- [x] Sin errores de consola en la ruta inicial ni en una ruta 404, comprobado con Chrome
      *headless*.

**Depende de:** `Task/004` — Aprobada ✔ · `Task/005` — Aprobada ✔.
**Repositorios:** `personal-blog-frontend` (implementación) · `personal-blog-infra`
(documentación de gobierno).
**Ficha:** [TASK-006](../tasks/TASK-006-react-frontend-foundation.md) ·
**Reporte:** [TASK-006-report](../task-reports/TASK-006-report.md)

> **Aprobada** por el usuario el 2026-08-18 y **fusionada en `main`** en ambos
> repositorios, con la normalización `main → dev` completada. La etapa pasa a **2 de 3**.
> Su alcance excluye deliberadamente el sistema de diseño (`Task/013`), las páginas del
> sitio público (`Task/014`), el panel administrativo (`Task/015`), la autenticación
> (`Task/011`) y el consumo real del API (`Task/007`).

### `Task/007-Integracion-Local` — **Aprobada** ✔ (2026-08-23)

- [x] Docker Compose único con `traefik`, `frontend`, `backend`, `postgres`, `minio` y
      `portainer`, extendiendo el stack de `Task/003` sin duplicarlo.
- [x] **Traefik v3** (D-05) como única puerta de entrada, con enrutado **explícito por
      archivo** y **sin acceso al socket de Docker**.
- [x] Backend en Compose contra el PostgreSQL local por **DNS interno** (`postgres:5432`),
      no por el puerto publicado en el host.
- [x] Frontend construido y servido como estático detrás del proxy, con *fallback* de SPA.
- [x] **Consumo real de `GET /health`** desde el frontend, con el cliente HTTP común de
      `Task/006`. Sin mocks ni endpoints inventados.
- [x] Red de borde `blog-edge` separada de `blog-data`: **el backend es el único servicio
      con un pie en cada una**.
- [x] Arranque encadenado por *healthchecks*, sin esperas fijas.
- [x] Portainer operativo y sin cambios, **único componente con acceso al daemon de
      Docker**; los seis contenedores del entorno viven en ese mismo daemon. La
      comprobación **visual autenticada** queda para el usuario.
- [x] MinIO **integrado como infraestructura**: sano y alcanzable, con **0 buckets de
      aplicación** y **sin uso aplicativo**.

**Repositorios:** `personal-blog-infra` · `personal-blog-frontend`.
**`personal-blog-backend` no se modifica:** su `Dockerfile`, su configuración por variables
de entorno y `GET /health` sirven sin cambios. Toda la integración es configuración.

**Ficha:** [TASK-007](../tasks/TASK-007-local-integration.md) ·
**Reporte:** [TASK-007-report](../task-reports/TASK-007-report.md)

> **Aprobada** por el usuario el 2026-08-23. Con ella **la etapa queda completada** (3 de
> 3) y el avance global pasa a **7 de 41 (17 %)**.
>
> Su alcance excluye deliberadamente el uso aplicativo de MinIO (`Task/010`), el modelo de
> datos (`Task/008`), la API pública (`Task/009`), la autenticación (`Task/011`) y el
> sistema de diseño (`Task/013`).
>
> **Comprobación que queda en manos del usuario:** la validación **visual autenticada** de
> Portainer.

> **Guardrail de arquitectura objetivo** (añadido en `Task/006.2`, **aprobada** el 2026-08-23). La
> arquitectura objetivo de producción es **Cloudflare Pages → API Gateway →
> Lambda/FastAPI → TLS → VPS/PgBouncer/PostgreSQL**; **S3** para object storage; **SSM
> `SecureString`** para los secretos de la Lambda; **CloudWatch mínimo + Grafana Cloud**
> para observabilidad; **Grafana Alloy** en el VPS.
>
> **`Task/007` NO implementa ninguno de esos servicios productivos** —ni AWS real, ni
> Lambda, ni API Gateway, ni S3, ni SSM, ni Grafana Cloud, ni Alloy, ni VPS, ni Terraform
> cloud, ni Cloudflare Pages real—, **pero tampoco debe crear acoplamientos locales que
> impidan sustituir MinIO, PostgreSQL o el proxy local por sus implementaciones
> productivas.**
>
> **Su naturaleza no cambia: sigue siendo integración local.** Criterio práctico para
> comprobarlo: al terminar, sustituir MinIO por S3, el proxy local por API Gateway y
> PostgreSQL local por PgBouncer **debe ser un cambio de configuración y de adaptador**,
> nunca una reescritura del dominio. Detalle:
> [target-production-architecture.md](../architecture/target-production-architecture.md)
> §24.

> **Límite con `Task/010`** (aclarado en `Task/005.5`). `Task/007` integra MinIO **a nivel
> de infraestructura**: contenedor, red, nombre de servicio, healthcheck y configuración
> **disponible** para el backend. **No exige —ni permite— que el backend implemente lógica
> de objetos**, y **prohíbe** un acceso directo temporal de FastAPI a MinIO que después
> habría que sustituir. El uso aplicativo del almacenamiento llega con la interfaz
> `ObjectStorage`, en `Task/010`.
>
> Criterio práctico: al terminar `Task/007`, MinIO debe estar **levantado, sano y
> alcanzable**; el backend **no debe haber leído ni escrito un solo objeto**.

**Depende de:** `Task/005` y `Task/006`.
**Repositorios:** `personal-blog-infra`, `personal-blog-frontend`, `personal-blog-backend`.

## Criterios de salida de la etapa

- [x] El backend arranca, expone un healthcheck y se conecta a PostgreSQL. — Verificado en
      `Task/005`, **aprobada** el 2026-08-12.
- [x] Las migraciones se aplican y revierten. — Verificado en `Task/005` (`upgrade`,
      `downgrade` y reaplicación contra PostgreSQL real), **aprobada**.
- [x] El frontend construye y se sirve tras el reverse proxy. — Verificado en `Task/007`
      (**aprobada** el 2026-08-23): Traefik v3 sirve el sitio en `http://localhost:8081/`.
- [x] El frontend consume un endpoint real del backend. — Verificado en `Task/007`
      (**aprobada**): Chrome *headless* renderiza la SPA, que llama a `GET /health` por el
      proxy y muestra el servicio y la versión reales.
- [x] Todo el conjunto es visible y sano en Portainer. — Verificado en `Task/007`
      (**aprobada**): los seis contenedores existen en el mismo daemon que Portainer
      administra, y Portainer sigue operativo. La comprobación **visual autenticada** la
      realiza el usuario: exigiría credenciales que no se piden ni se extraen.
- [x] Las pruebas base pasan en ambos repositorios. — Backend: **69 pruebas superadas** en
      `Task/005` (**aprobada**), más 1 omitida con motivo explícito. Frontend: **31 pruebas
      superadas** en `Task/006` (**aprobada** el 2026-08-18), con cobertura de *statements*
      del 100 %.

> `[~]` significa cumplido solo en parte. Un criterio se marca `[x]` cuando la tarea que lo
> cumple ha sido aprobada por el usuario.

## Fuera del alcance de la etapa

- Modelo de datos del blog (Etapa 03).
- Autenticación (Etapa 03).
- Diseño visual definitivo (Etapa 04).
- CI (Etapa 06).

## Riesgos conocidos

| Riesgo | Mitigación | Estado |
| --- | --- | --- |
| El patrón de conexión a PostgreSQL puede no ser compatible con Lambda. | Considerar desde ya conexiones cortas / pooling externo; se cierra en `Task/029`. | Abierto — R-03 |
| Divergencia de configuración entre local y contenedor. | Una sola fuente de configuración por variables de entorno. En `Task/005` el proceso local y el contenedor usan exactamente la misma configuración tipada. | **Mitigado** |
| Acoplar el backend a MinIO en vez de a una interfaz. | La abstracción `ObjectStorage` se introduce en `Task/010`. `Task/005` no toca almacenamiento. | Abierto |
| Las dependencias transitivas no están bloqueadas. | Directas fijadas con `==` y `pip check`; el `Dockerfile` no usa `--require-hashes` ni `--no-deps` mientras el archivo no los soporte; bloqueo con hashes en `Task/020`. **Observado el 2026-08-11:** `starlette 1.6.0` en la imagen frente a `1.3.1` en Windows. | Abierto — R-14 |
| La imagen base del backend envejece. | Escaneo en `Task/018` y verificación en CI en `Task/020`. | Abierto — R-15 |
| Un tercer componente con acceso al socket de Docker agravaría **R-09**. | **Evitado en `Task/007`:** Traefik usa proveedor de archivo, no de Docker. Portainer sigue siendo el único privilegiado. | **Mitigado** |
| Acoplar el frontend a un puerto o a un nombre de servicio de Docker. | La URL del API vive en `VITE_API_BASE_URL` y apunta al **mismo origen** que sirve el sitio; ningún componente React conoce puertos ni nombres internos. | **Mitigado** |

## Cierre de la etapa

**Completada el 2026-08-23**, al aprobarse `Task/007-Integracion-Local`. Las tres tareas
—`Task/005`, `Task/006` y `Task/007`— están **aprobadas**, y el hito *«Frontend y backend
arrancan e integran contra PostgreSQL y MinIO»* queda alcanzado.

Lo que la etapa deja construido: un entorno local **integrado y reproducible** donde el
navegador entra por **Traefik v3** y encuentra el sitio de React y el API de FastAPI en el
**mismo origen**, con FastAPI hablando con **PostgreSQL** por DNS interno, **MinIO** sano y
alcanzable pero **sin uso aplicativo**, y **Portainer** supervisando el conjunto.

Lo que **no** deja: ninguna funcionalidad del blog. No hay modelo de datos, ni contenido,
ni autenticación, ni diseño. Eso empieza en la ETAPA 03.

## Siguiente etapa

[ETAPA 03 — Dominio y Backend](STAGE-03-domain-and-backend.md) — comienza con
`Task/008-Modelo-de-Datos`, **primera tarea sujeta a la BACKEND TEST-FIRST LAW**
([BACKEND_TESTING_STRATEGY.md](../project-management/BACKEND_TESTING_STRATEGY.md)).
