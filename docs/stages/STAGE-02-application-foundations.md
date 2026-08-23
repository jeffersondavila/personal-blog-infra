# ETAPA 02 — Fundaciones de las Aplicaciones

| Campo | Valor |
| --- | --- |
| **Número** | 02 |
| **Estado** | **En curso** |
| **Dependencias** | [ETAPA 01](STAGE-01-local-infrastructure.md) — **Completada** ✔ (2026-07-31) |
| **Tareas** | 3 |
| **Aprobadas** | 2 |
| **Avance** | 67 % |
| **Hito que completa** | Frontend y backend arrancan e integran contra PostgreSQL y MinIO. |
| **Inicio** | 2026-08-01 |
| **Última actualización** | 2026-08-18 |

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

### `Task/007-Integracion-Local` — *Pendiente*

- Integrar frontend, backend, PostgreSQL y MinIO en un único Compose.
- Reverse proxy local con rutas para sitio y API.
- Supervisión del conjunto desde Portainer.

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
- [ ] El frontend construye y se sirve tras el reverse proxy. — `Task/006`, `Task/007`.
- [ ] El frontend consume un endpoint real del backend. — `Task/007`.
- [ ] Todo el conjunto es visible y sano en Portainer. — `Task/007`.
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

## Siguiente etapa

[ETAPA 03 — Dominio y Backend](STAGE-03-domain-and-backend.md)
