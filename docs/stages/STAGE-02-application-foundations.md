# ETAPA 02 — Fundaciones de las Aplicaciones

| Campo | Valor |
| --- | --- |
| **Número** | 02 |
| **Estado** | Pendiente |
| **Dependencias** | [ETAPA 01](STAGE-01-local-infrastructure.md) |
| **Tareas** | 3 |
| **Aprobadas** | 0 |
| **Avance** | 0 % |
| **Hito que completa** | Frontend y backend arrancan e integran contra PostgreSQL y MinIO. |

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

### `Task/005-Fundacion-Backend-FastAPI` — *Pendiente*

- Estructura de proyecto FastAPI por capas.
- Configuración por variables de entorno.
- Logging estructurado.
- Conexión a PostgreSQL.
- Alembic para migraciones.
- Suite de pruebas base (`pytest`).
- `Dockerfile` del backend.

**Depende de:** `Task/004`. **Repositorio:** `personal-blog-backend`.

### `Task/006-Fundacion-Frontend-React` — *Pendiente*

- React + TypeScript + Vite.
- Router.
- Cliente HTTP con manejo de errores.
- Suite de pruebas base.
- Build de producción.

**Depende de:** `Task/004`. **Repositorio:** `personal-blog-frontend`.

### `Task/007-Integracion-Local` — *Pendiente*

- Integrar frontend, backend, PostgreSQL y MinIO en un único Compose.
- Reverse proxy local con rutas para sitio y API.
- Supervisión del conjunto desde Portainer.

**Depende de:** `Task/005` y `Task/006`.
**Repositorios:** `personal-blog-infra`, `personal-blog-frontend`, `personal-blog-backend`.

## Criterios de salida de la etapa

- [ ] El backend arranca, expone un healthcheck y se conecta a PostgreSQL.
- [ ] Las migraciones se aplican y revierten.
- [ ] El frontend construye y se sirve tras el reverse proxy.
- [ ] El frontend consume un endpoint real del backend.
- [ ] Todo el conjunto es visible y sano en Portainer.
- [ ] Las pruebas base pasan en ambos repositorios.

## Fuera del alcance de la etapa

- Modelo de datos del blog (Etapa 03).
- Autenticación (Etapa 03).
- Diseño visual definitivo (Etapa 04).
- CI (Etapa 06).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| El patrón de conexión a PostgreSQL puede no ser compatible con Lambda. | Considerar desde ya conexiones cortas / pooling externo; se cierra en `Task/029`. |
| Divergencia de configuración entre local y contenedor. | Una sola fuente de configuración por variables de entorno. |
| Acoplar el backend a MinIO en vez de a una interfaz. | La abstracción `ObjectStorage` se introduce en `Task/010`. |

## Siguiente etapa

[ETAPA 03 — Dominio y Backend](STAGE-03-domain-and-backend.md)
