# ROADMAP — Blog Personal

Vista resumida y ordenada de todo el proyecto: 13 etapas (00 → 12) y 41 tareas.

- **Última actualización:** 2026-09-06 (`Task/016-SEO-Accesibilidad-y-Rendimiento` — **Aprobada**. ETAPA 05 **En curso**, **1 de 3**. **41 identificadores intactos**; **D-21** añadida y **Abierta**)
- **Estrategia:** local-first (ver [ADR-001](../adr/ADR-001-local-first.md)), extendida a la
  infraestructura con **AWS Local Parity** — ver
  [aws-local-parity.md](../architecture/aws-local-parity.md) y
  [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) (**Aceptada**)
- **Capa de datos de producción:** PostgreSQL autogestionado en **VPS externo** con
  PgBouncer — ver
  [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) y
  [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) (**Aceptada**)
- **Arquitectura objetivo de producción:** Cloudflare → Pages → API Gateway → Lambda → TLS →
  VPS/PgBouncer/PostgreSQL, con S3, SSM `SecureString`, **CloudWatch mínimo** y **Grafana
  Cloud** (Alloy en el VPS) — ver
  [target-production-architecture.md](../architecture/target-production-architecture.md) y
  [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) (**Aceptada**)
- **Avance global:** **39 %** (16 de 41 tareas aprobadas)

Estados oficiales: `Pendiente` · `En progreso` · `Lista para validación` · `Aprobada` ·
`Bloqueada` · `Descartada`.

> El porcentaje de avance se calcula **solo** con tareas en estado `Aprobada`.
> Ninguna tarea puede marcarse `Aprobada` sin autorización explícita del usuario.

> **Tareas de mantenimiento.** Las tareas con sufijo (`Task/002.1`, `Task/005.1`,
> `Task/005.2`, `Task/005.3`, `Task/005.4`, `Task/005.5`, `Task/005.6`, `Task/005.7`,
> `Task/006.1`, `Task/006.2`, …) son mantenimiento de gobierno: **no forman parte de estas
> 41** y **no alteran el avance**. Su estado se registra en [`STATUS.md`](STATUS.md).

> **Exposición de la auditoría para el dashboard — `Task/012.1` (2026-09-05, aprobada).**
> Mantenimiento **funcional** de la API administrativa, previo a que `Task/015` pueda
> entregar su dashboard. `MVP_SCOPE.md` §3.3 exige como alcance mínimo los *«últimos eventos
> de auditoría»*, y ninguna de las **38 operaciones HTTP** administrativas de entonces los
> leía: el módulo `audit` no tenía capa de presentación y su puerto solo escribía. Añade
> **una** operación de solo lectura —`GET /api/v1/admin/audit-events`—, paginada con la
> envoltura única y sin filtros, con un DTO de cinco campos que **no** incluye
> `ip_address`, `actor_id`, `event_metadata` ni `request_id`. **Sin migración**: el índice
> cronológico ya existe. La inmutabilidad de `AuditEvent` queda intacta y leer no audita,
> comprobado contando filas reales. **1572 pruebas en verde** (+45 sobre el baseline de
> `main`). **No cuenta** dentro
> de las 41, **41 identificadores intactos** y avance **sin cambios**. Ficha:
> [TASK-012.1](../tasks/TASK-012.1-audit-events-for-dashboard.md) · Reporte:
> [TASK-012.1-report.md](../task-reports/TASK-012.1-report.md).

> **Formalización de la arquitectura objetivo de producción — `Task/006.2` (2026-08-23,
> aprobada).**
> Mantenimiento transversal de arquitectura y planificación, previo a `Task/007`. Da
> contraparte **textual** al diagrama `images/Infraestructura.png` que el usuario actualizó
> en `main`, y alinea documentación, roadmap, decisiones y riesgos con él. Cierra el modelo
> de **secretos del VPS**, el **papel de Docker** y la **observabilidad de producción**
> —CloudWatch mínimo + Grafana Cloud con Alloy— y abre **D-17** a **D-20** con propietario.
> **0 funcionalidad**, **0 recursos cloud**, **41 identificadores intactos** y avance **sin
> cambios**. Documento canónico:
> [target-production-architecture.md](../architecture/target-production-architecture.md) —
> **Vigente** ·
> [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) — **Aceptada**.

> **Cierre de los hallazgos finales de certificación — `Task/005.7` (2026-08-16).**
> Mantenimiento transversal previo a `Task/006`, sobre la mega auditoría final de Claude y
> Codex. Ambos reprodujeron los **mismos dos defectos** de la fundación de testing y
> discreparon en severidad; se adoptó **el criterio más estricto**: corregirlos, no
> diferirlos. Queda cerrado que un `.env` del desarrollador no puede alterar la suite **ni
> durante la *collection***, y que las *fixtures* oficiales de integración no entregan acceso
> a PostgreSQL ni a Alembic antes de validar el destino. La concurrencia de la suite queda
> **diferida con propietario explícito** (**R-37**, `Task/020`). **0 funcionalidad nueva**,
> **41 identificadores intactos** y avance **sin cambios**.

> **Cierre de fundaciones — `Task/005.6` (2026-08-16).** Mantenimiento transversal previo a
> `Task/006`: política de finales de línea en los tres repositorios, aislamiento de la suite
> frente al `.env` del desarrollador, base de datos de pruebas dedicada con guardas
> *fail-closed*, verificación semántica de `commit`/`rollback` y corrección del estado
> documental. **0 funcionalidad nueva**, **41 identificadores intactos** y avance **sin
> cambios**. Añade la regla de gobierno de
> [WORKFLOW §6.1](WORKFLOW.md): los documentos versionados registran estado **duradero**; el
> estado transitorio de Git y GitHub se consulta **en vivo**.

> **Alineación posterior a la auditoría — `Task/005.5` (2026-08-16).** Se corrigieron
> dependencias invertidas, propietarios ausentes y *gates* que exigían recursos futuros.
> **Los 41 identificadores, sus nombres y su orden no cambian**; no se añadió, eliminó ni
> renumeró ninguna tarea. Ver el *mapa de responsabilidades transversales* al final de este
> documento.

---

## Resumen de etapas

| # | Etapa | Tareas | Aprobadas | Avance | Estado | Depende de |
| --- | --- | --- | --- | --- | --- | --- |
| 00 | Fundación y Gobierno | 2 | 2 | 100 % | **Completada** | — |
| 01 | Infraestructura Local | 2 | 2 | **100 %** | **Completada** | 00 ✔ |
| 02 | Fundaciones de las Aplicaciones | 3 | 3 | **100 %** | **Completada** | 01 ✔ |
| 03 | Dominio y Backend | 5 | **5** | **100 %** | **Completada** | 02 ✔ |
| 04 | Experiencia del Usuario | 3 | **3** | **100 %** | **Completada** | 03 ✔ |
| 05 | Calidad y Seguridad | 3 | 0 | 0 % | Pendiente | 04 ✔ |
| 06 | Integración Continua | 3 | 0 | 0 % | Pendiente | 05 |
| 07 | Validación Local | 1 | 0 | 0 % | Pendiente | 06 |
| 08 | Preparación Cloud sin Cuentas | 4 | 0 | 0 % | Pendiente | 07 |
| 09 | Cuentas y Seguridad Cloud | 3 | 0 | 0 % | Pendiente | 08 |
| 10 | Despliegue Cloud | 7 | 0 | 0 % | Pendiente | 09 |
| 11 | Automatización de Despliegues | 3 | 0 | 0 % | Pendiente | 10 |
| 12 | Lanzamiento y Operación | 2 | 0 | 0 % | Pendiente | 11 |
| | **Total** | **41** | **15** | **37 %** | | |

---

## ETAPA 00 — Fundación y Gobierno

**Objetivo:** dejar los tres repositorios preparados, con reglas de trabajo, sistema
documental de seguimiento y un MVP y arquitectura acordados antes de escribir código.

**Dependencias:** ninguna.
**Hito que completa:** *Gobierno del proyecto establecido y alcance del MVP cerrado.* ✔
**Completada:** 2026-07-26.
**Ficha:** [STAGE-00-foundation.md](../stages/STAGE-00-foundation.md)
**Documentos producidos:** [MVP_SCOPE](../product/MVP_SCOPE.md) ·
[USER_FLOWS](../product/USER_FLOWS.md) · [CONTENT_MODEL](../product/CONTENT_MODEL.md) ·
[software-architecture](../architecture/software-architecture.md) ·
[api-contracts](../architecture/api-contracts.md) ·
[non-functional-requirements](../architecture/non-functional-requirements.md) ·
[security-boundaries](../architecture/security-boundaries.md) ·
[open-decisions](../architecture/open-decisions.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/001-Inicializar-Workspace-y-Roadmap` | Preparar repositorios, documentación y seguimiento. | infra, frontend, backend | — | **Aprobada** (2026-07-26) |
| `Task/002-Definir-MVP-y-Arquitectura` | Definir requerimientos funcionales, arquitectura de software, contratos generales y límites del MVP. | infra | 001 | **Aprobada** (2026-07-26) |

---

## ETAPA 01 — Infraestructura Local

**Objetivo:** disponer de un entorno local reproducible con Docker Compose, con datos
persistentes y capacidad de respaldo y recuperación.

**Dependencias:** Etapa 00.
**Hito que completa:** *Entorno local reproducible y recuperable.* ✔
**Completada:** 2026-07-31.
**Ficha:** [STAGE-01-local-infrastructure.md](../stages/STAGE-01-local-infrastructure.md)
**Documentos producidos:** [local-environment.md](../runbooks/local-environment.md) ·
[local-backup-and-recovery.md](../runbooks/local-backup-and-recovery.md) ·
[scripts/backup/](../../scripts/backup/README.md)
**Decisiones resueltas:** D-05 — **Traefik v3** como reverse proxy local, a implementar en
`Task/007` (ver [open-decisions.md](../architecture/open-decisions.md)).

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/003-Crear-Infraestructura-Local` | Docker Compose. PostgreSQL. MinIO. Portainer. Redes. Volúmenes. Healthchecks. | infra | 002 | **Aprobada** (2026-07-29) |
| `Task/004-Backups-y-Recuperacion-Local` | Backup y restauración de PostgreSQL. Objetos, metadatos y tags de MinIO. Respaldo de Portainer. Reconstrucción del entorno. | infra | 003 | **Aprobada** (2026-07-31) |

---

## ETAPA 02 — Fundaciones de las Aplicaciones

**Objetivo:** establecer la base profesional de backend y frontend e integrarlos con la
infraestructura local.

**Dependencias:** Etapa 01.
**Hito que completa:** *Frontend y backend arrancan e integran contra PostgreSQL y MinIO.*
**Ficha:** [STAGE-02-application-foundations.md](../stages/STAGE-02-application-foundations.md)
**Estado:** **Completada** el 2026-08-23. **3 de 3** tareas aprobadas.
**Hito alcanzado:** *Frontend y backend arrancan e integran contra PostgreSQL y MinIO.* ✔

> **Guardrail de `Task/007` — añadido en `Task/006.2`, aprobada.** La arquitectura objetivo
> de producción es **Cloudflare Pages → API Gateway → Lambda/FastAPI → TLS →
> VPS/PgBouncer/PostgreSQL**; **S3** para object storage; **SSM `SecureString`** para los
> secretos de la Lambda; **CloudWatch mínimo + Grafana Cloud** para observabilidad; **Alloy**
> en el VPS.
>
> **`Task/007` NO implementa estos servicios productivos**, pero **tampoco debe crear
> acoplamientos locales que impidan sustituir MinIO, PostgreSQL o el proxy local por sus
> implementaciones productivas.** Su naturaleza **no cambia**: sigue siendo integración
> **local**. Detalle:
> [target-production-architecture.md](../architecture/target-production-architecture.md) §24.

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/005-Fundacion-Backend-FastAPI` | Base profesional de FastAPI. Configuración. Logging. PostgreSQL. Alembic. Pruebas. Dockerfile. | backend, infra (documentación) | 004 | **Aprobada** (2026-08-12) |
| `Task/006-Fundacion-Frontend-React` | React. TypeScript. Vite. Router. Cliente HTTP. Pruebas. Build. | frontend, infra (documentación) | 004 | **Aprobada** (2026-08-18) |
| `Task/007-Integracion-Local` | Integrar frontend, backend, PostgreSQL y MinIO **a nivel de infraestructura**: contenedores, red, nombres de servicio, configuración disponible y healthchecks. Reverse proxy **Traefik v3**. Docker Compose completo. Supervisión desde Portainer. **No implementa lógica de objetos ni acceso directo de FastAPI a MinIO**: eso es `Task/010`. | infra, frontend | 005, 006 | **Aprobada** (2026-08-23) |

---

## ETAPA 03 — Dominio y Backend

**Objetivo:** modelar el dominio del blog y exponer las APIs pública y administrativa
con almacenamiento de archivos y autenticación.

**Dependencias:** Etapa 02.
**Avance:** **5 de 5 aprobadas** (`Task/008`, el 2026-08-25; `Task/009`, el 2026-08-27; `Task/010`, el 2026-08-28; `Task/011`, el 2026-09-01; `Task/012`, el 2026-09-03).
**Hito que completa:** *Backend funcionalmente completo para el MVP.*
**Ficha:** [STAGE-03-domain-and-backend.md](../stages/STAGE-03-domain-and-backend.md)
**Estado:** **Completada** el 2026-09-03. **5 de 5** tareas aprobadas.
**Hito alcanzado:** *Backend funcionalmente completo para el MVP.* ✔

> **Test-first obligatorio en toda la etapa.** `Task/008` a `Task/012` construyen el backend
> funcional: cada comportamiento nuevo empieza por una prueba que falla
> (**RED → GREEN → REFACTOR**), con matriz de casos previa y evidencia registrada en el
> reporte. Regla completa: [`BACKEND_TESTING_STRATEGY.md`](BACKEND_TESTING_STRATEGY.md).

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/008-Modelo-de-Datos` | Perfil. Artículos. Reviews de libros. Videos. Proyectos. Etiquetas. Medios. Administrador. Auditoría. **Test-first**: invariantes y transiciones; migraciones validadas con integración real. | backend, infra (documentación) | 007 | **Aprobada** (2026-08-25) |
| `Task/009-API-Publica` | Consultas públicas. Paginación. Filtros. Búsqueda. Contenido publicado. **Test-first**: contrato HTTP y el caso negativo de contenido no publicado. | backend, infra (documentación) | 008 | **Aprobada** (2026-08-27) |
| `Task/010-Almacenamiento-Compatible-S3` | Interfaz `ObjectStorage`, `MinIOStorage` **y el código de `S3Storage`**, con pruebas de contrato comunes — **sin AWS real**. Imágenes y miniaturas. Persiste **claves de objeto**, nunca URLs prefirmadas. **Test-first**: contrato primero, después integración con MinIO. | backend, infra (documentación y Compose) | 008 | **Aprobada** (2026-08-28) |
| `Task/011-Autenticacion-Administrativa` | Login. **Sesión opaca *server-side* con cookie `HttpOnly`**. Protección reutilizable de endpoints. **Rate limiting en PostgreSQL**. Auditoría. **Resuelve D-15, D-02 y D-09**. Migración `0003`. **Test-first**: casos negativos de acceso dentro del alcance. | backend, infra (documentación) | 008 | **Aprobada** (2026-09-01) |
| `Task/012-API-Administrativa` | CRUD. Borradores. Publicación. Archivado. Gestión de imágenes. **23 rutas administrativas**, todas autenticadas. Cierra la forma de las transiciones, los campos mínimos para publicar, el formato del *slug*, la **escritura y exigencia del texto alternativo donde se usa la imagen** y el catálogo de auditoría del CRUD. **Sin migración nueva.** **Test-first**: matriz de transiciones antes del caso de uso. | backend, infra (documentación) | 009, 010, 011 | **Aprobada** (2026-09-03) |

---

## ETAPA 04 — Experiencia del Usuario

**Estado:** **Completada** el 2026-09-05 — **3 de 3 aprobadas, 100 %**.

**Objetivo:** construir el sistema de diseño, el sitio público y el panel administrativo.

**Dependencias:** Etapa 03.
**Hito que completa:** *Blog usable de extremo a extremo en local.*
**Ficha:** [STAGE-04-user-experience.md](../stages/STAGE-04-user-experience.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/013-Sistema-de-Diseno` | Tokens semánticos. Fundación global y estrategia única de foco. Tipografía. Responsive intrínseco. Primitivas `Container`, `Stack`, `Button`, `Card`, `Badge`. Accesibilidad base: **A-05**, **A-06**, **A-07** e inicio de **A-01**. **Resuelve D-03**: CSS Modules más CSS Custom Properties, sin biblioteca visual de terceros. | frontend, infra (documentación) | 012 | **Aprobada** (2026-09-04) |
| `Task/014-Sitio-Publico` | Inicio. Quién soy. Artículos y detalle. Reviews y detalle. Videos. Proyectos y detalle. Contacto. Búsqueda y filtro por etiqueta. Página 404. Estados de carga, vacío y error. Markdown sanitizado (ADR-005). Imágenes por `access_url` con `alt_text`. **Asume A-02 y A-04**, continúa **A-01**; **cierra la lista de proveedores de video**. Sin SEO (`Task/016`) ni panel (`Task/015`). | frontend, infra (documentación) | 013 | **Aprobada** (2026-09-05) |
| `Task/015-Panel-Administrativo` | Acceso y sesión administrativa sobre la cookie `HttpOnly` de `Task/011`. Dashboard básico. Listados y formularios de los cuatro tipos publicables. Editor Markdown y **vista previa con el mismo pipeline sanitizado** de `Task/014` (**resuelve D-04**, sin dependencias nuevas). Carga y selección de imágenes. Etiquetas y perfil. Transiciones de publicación. **Asume A-03, A-08, S-03 en la vista previa y P-05.** Sin SEO ni auditoría de accesibilidad (`Task/016`), sin CORS ni cabeceras (`Task/018`). | frontend, infra (documentación) | 013, 014 | **Aprobada** (2026-09-05) — **sin bloqueos**. **18 superficies**, **600 pruebas** en verde y **0 dependencias nuevas**. Su dashboard consume además `GET /api/v1/admin/audit-events`, que entregó `Task/012.1` |

---

## ETAPA 05 — Calidad y Seguridad

**Objetivo:** elevar el producto a estándar publicable: SEO, accesibilidad, rendimiento,
observabilidad y endurecimiento de seguridad.

**Dependencias:** Etapa 04 — **Completada** ✔ (2026-09-05).
**Estado:** **En curso** — **1 de 3** aprobadas.
**Hito que completa:** *Producto con calidad y seguridad verificables.*
**Ficha:** [STAGE-05-quality-security.md](../stages/STAGE-05-quality-security.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/016-SEO-Accesibilidad-y-Rendimiento` | Metadatos. Open Graph. Sitemap. Robots. Optimización. Accesibilidad. **Verificación comprobable** del *rendering* de la SPA por URL directa y ante *crawlers*, con **criterio explícito de reconsideración** si no se satisface. `og:image` con URL estable, no expirable. **El backend participa** por el `sitemap.xml` derivado de contenido publicado y por la exposición de la miniatura (deuda 2 de `Task/010`). | frontend, backend, infra (documentación + wiring local mínimo) | 014, 015 | **Aprobada** (2026-09-06) — **E-02**, **E-04**, **E-05**, **E-07** y **E-08** cumplidos; **E-03 NO cerrado** y **E-06 parcial**. Volver a medir tras implementar demostró que un *crawler* sin JavaScript sigue sin recibir metadatos por URL: no era falta de código, así que se abre **D-21** con **ADR-009** en *Propuesta*, sin elegir estrategia. **688** pruebas de frontend y **1631** de backend en verde, **0 dependencias nuevas**. En `infra`, además de la documentación, **tres líneas de *wiring* local** autorizadas: dos variables del Compose y el enrutado de `/sitemap.xml` en Traefik |
| `Task/017-Observabilidad-Local` | Logs JSON. Correlation ID. Healthchecks. Auditoría. Diagnóstico con Portainer. **Solo entorno local: no es owner del monitoreo del VPS productivo** (`Task/029`, `Task/040`). **La telemetría debe ser portable**: el dominio no se acopla a CloudWatch, Grafana, Loki ni Prometheus — es el **principio 9** de [`overview.md`](../architecture/overview.md) §5 y [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md), **no O-09**. | backend, infra | 014, 015 | **Aprobada** ✔ (2026-09-06) |
| `Task/018-Endurecimiento-de-Seguridad` | Dependencias. Imágenes Docker. Secretos. CORS. Headers. Archivos. Autenticación. | infra, frontend, backend | 016, 017 | Pendiente |

---

## ETAPA 06 — Integración Continua

**Objetivo:** automatizar verificación de calidad en cada cambio, en los tres repositorios.

**Dependencias:** Etapa 05.
**Hito que completa:** *CI verde en los tres repositorios.*
**Ficha:** [STAGE-06-continuous-integration.md](../stages/STAGE-06-continuous-integration.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/019-CI-Frontend` | Lint. Type-check. Tests. Build. | frontend | 018 | Pendiente |
| `Task/020-CI-Backend` | Ruff. MyPy. Pytest. Migraciones. Build Docker. Escaneo. | backend | 018 | Pendiente |
| `Task/021-CI-Infraestructura` | Docker Compose config. Validación de scripts. Escaneo de secretos. **Terraform todavía no existe** (llega en `Task/025`): sus verificaciones **no se declaran aquí como checks vacíos**; `Task/025` amplía este workflow con `fmt` y `validate`. | infra | 018 | Pendiente |

---

## ETAPA 07 — Validación Local

**Objetivo:** validar el sistema completo en condiciones similares a producción, desde
cero y con datos reales de prueba.

**Dependencias:** Etapa 06.
**Hito que completa:** *Blog validado íntegramente en local. Puerta de entrada a la nube.*
**Ficha:** [STAGE-07-local-validation.md](../stages/STAGE-07-local-validation.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/022-Validacion-Local-Production-Like` | Reconstrucción completa. Migraciones. Seed. Flujo administrativo. Publicación. Persistencia. Backups. Revisión en Portainer. | infra, frontend, backend | 019, 020, 021 | Pendiente |

---

## ETAPA 08 — Preparación Cloud + AWS Local Parity

**Objetivo:** dejar todo listo para la nube **sin crear cuentas ni recursos reales**, y
**validar la IaC ejecutándola** contra un laboratorio AWS local.

**Dependencias:** Etapa 07.
**Hito que completa:** *Artefactos e IaC listos y **ejecutados** en un laboratorio AWS local.*
**Ficha:** [STAGE-08-cloud-ready.md](../stages/STAGE-08-cloud-ready.md)

> **AWS Local Parity.** Desde `Task/005.2` (2026-08-15), esta etapa deja de limitarse a
> `terraform fmt` + `validate` —que comprueban sintaxis, no comportamiento— e incorpora
> `plan`, `apply`, inspección, *drift* controlado, `destroy` y reconstrucción **contra un
> emulador AWS local**, con **una sola definición de Terraform** para ambos destinos y
> **cero recursos AWS reales**. Los **4 identificadores y nombres de tarea no cambian**.
> Estrategia: [aws-local-parity.md](../architecture/aws-local-parity.md) ·
> [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) (**Aceptada**).

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/023-Compatibilidad-FastAPI-Lambda` | Adaptador de FastAPI para API Gateway HTTP API y Lambda. Compatible además con la Lambda emulada del laboratorio. | backend | 022 | Pendiente |
| `Task/024-Artefacto-ZIP-Lambda` | Paquete Linux reproducible. Validación de tamaño. Checksums. **Artefacto validable ejecutándolo** en el laboratorio. | backend | 023 | Pendiente |
| `Task/025-Terraform-Cloud` | Terraform **portable**: módulos compartidos, provider AWS oficial, destino local y destino real. `plan`/`apply`/`destroy` **ejecutados en local**. Matriz de paridad. Guardas *fail-closed*. Resuelve **D-06**. **Amplía el CI de `Task/021` con `terraform fmt` y `validate`.** Sin recursos reales. | infra | 022, **024** | Pendiente |
| `Task/026-Runbooks-de-Despliegue` | Creación. Validación del destino. Rollback. *Drift*. Destrucción. Recuperación. Transición a AWS. | infra | 024, 025 | Pendiente |

---

## ETAPA 09 — Cuentas y Seguridad Cloud

**Objetivo:** crear las cuentas cloud con controles de costo y acceso **antes** de
desplegar nada.

**Dependencias:** Etapa 08.
**Hito que completa:** *Cuentas cloud seguras, con presupuesto y **acceso de GitHub Actions a
AWS sin credenciales permanentes** (OIDC, `Task/028`).* La identidad del **VPS hacia AWS**
sigue abierta en **D-16** (`Task/029`), y **Cloudflare y el proveedor del VPS** pueden exigir
otro modelo (`Task/039`). Acotado en `Task/005.6`.
**Ficha:** [STAGE-09-cloud-accounts.md](../stages/STAGE-09-cloud-accounts.md)

> **`Task/029` cambia de alcance, no de número.** Desde `Task/005.3` (2026-08-15,
> **aprobada**) la base de datos de producción deja de ser un servicio administrado y pasa
> a ser **PostgreSQL autogestionado en un VPS externo, con PgBouncer delante**, mientras el
> backend permanece en AWS Lambda. **El identificador `029` no cambia** y el roadmap sigue
> teniendo **41 tareas**. Estrategia:
> [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) ·
> [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md).

> **`Task/029` define y prepara; no valida contra recursos que todavía no existen**
> (aclarado en `Task/005.5`). Los *gates* que exigen S3 (`Task/030`) o la Lambda real
> (`Task/032`) se validan en su tarea propietaria y, definitivamente, en `Task/040`. Ver
> [STAGE-09](../stages/STAGE-09-cloud-accounts.md).

> **`Task/029` absorbe tres materias más — `Task/006.2` (2026-08-23, aprobada).** El
> **identificador `029` no cambia** y el roadmap sigue teniendo **41 tareas**. Se le confirma
> el *ownership* de: **el mecanismo de secretos cifrados del host** (**D-17**; SOPS + age es
> candidato, no decisión), **el mecanismo de configuración del sistema operativo** (**D-18**;
> Ansible, cloud-init o scripts idempotentes — **nunca Terraform**) y **la instalación y
> configuración de Grafana Alloy** como agente del *baseline* de observabilidad que ya tenía
> asignado. Detalle:
> [target-production-architecture.md](../architecture/target-production-architecture.md) §9,
> §11 y §17.

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/027-Configurar-Cuentas-y-Presupuestos` | AWS. Cloudflare. MFA. Presupuestos. Alertas. | infra | 026 | Pendiente |
| `Task/028-GitHub-OIDC-AWS` | Roles temporales de **GitHub Actions → AWS**. Sin credenciales AWS permanentes. **No cubre la identidad del VPS** (**D-16**, `Task/029`). | infra | 027 | Pendiente |
| `Task/029-Preparar-PostgreSQL-Produccion-en-VPS` | Selección del VPS por costo, región y RTT **medido**. PgBouncer. TLS, **ciclo de vida del certificado** y SCRAM. Firewall y SSH. Usuarios, roles y límites de conexión. Backup **fuera del host** y **restore demostrado** contra un destino disponible entonces. **Baseline de observabilidad del VPS con Grafana Alloy.** **Mecanismo de secretos cifrados del host** (**D-17**) y **mecanismo de configuración del sistema operativo** (**D-18**). Decide **D-16** (identidad del VPS hacia AWS). | infra | 027 | Pendiente |

---

## ETAPA 10 — Despliegue Cloud

**Objetivo:** desplegar el blog en la nube y publicar el primer contenido real.

**Dependencias:** Etapa 09.
**Hito que completa:** *Blog en línea y accesible por dominio propio.*
**Ficha:** [STAGE-10-cloud-deployment.md](../stages/STAGE-10-cloud-deployment.md)

> **Reutiliza, no reinventa.** `Task/030`–`Task/033` materializan contra AWS real los
> **módulos ya construidos y validados en `Task/025`**. Aquí se documenta qué funcionó sin
> cambios, qué exigió otra configuración, qué exigió adaptación y qué no era simulable en
> local, y se actualiza la
> [matriz de paridad](../architecture/aws-local-parity.md) con evidencia real. **AWS real es
> la autoridad final.**

> **Observabilidad — precisado en `Task/006.2`, aprobada.** `Task/031` mantiene
> **CloudWatch en modo mínimo** —retención corta y explícita, alarmas imprescindibles— y
> **decide D-20**: con qué mecanismo IAM de **solo lectura** accederá Grafana Cloud a
> CloudWatch. **Sigue siendo solo AWS: no observa el VPS**, cuya telemetría la envía
> **Grafana Alloy** desde `Task/029`.

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/030-Desplegar-Amazon-S3` | Bucket. CORS. Políticas. URLs prefirmadas. Lifecycle. Object storage y medios. **Destino, política, retención y *lifecycle* de los backups del VPS** —**owner único de ese tramo**; el mecanismo de backup es de `Task/029`— y **materialización de la identidad decidida en D-16**. Valida `S3Storage` contra S3 real. Resuelve **D-08**. | infra | 029 | Pendiente |
| `Task/031-Desplegar-SSM-y-CloudWatch` | **SSM `SecureString`** para los secretos de la Lambda, con permisos IAM mínimos. **CloudWatch mínimo**: logs y métricas nativas, retención corta y explícita (**D-11**), alarmas mínimas. **Base de la integración AWS → Grafana Cloud**: decide **D-20** y su modelo IAM de solo lectura. **Solo AWS: no observa el VPS.** | infra | 029 | Pendiente |
| `Task/032-Desplegar-AWS-Lambda` | Función FastAPI en Lambda por **artefacto ZIP**. IAM. **Configuración no secreta por variables de entorno y secretos desde SSM.** `DATABASE_URL` apuntando a **PgBouncer**, con **TLS** hacia el VPS. Límites (**D-12**). **Reserved Concurrency** coherente con el pool de PgBouncer. *Wiring* de `S3Storage`. **Logging compatible con la observabilidad elegida.** | infra | 030, 031 | Pendiente |
| `Task/033-Desplegar-API-Gateway` | **HTTP API**. Rutas hacia la Lambda. CORS. Throttling. Dominio del API si corresponde. | infra | 032 | Pendiente |
| `Task/034-Desplegar-Cloudflare-Pages` | **Cloudflare Pages**: build de React, variables del build y publicación de la SPA. **Owner del despliegue del frontend**; DNS, CDN y WAF son de `Task/035`. | infra, frontend | 033 | Pendiente |
| `Task/035-Configurar-DNS` | Dominio principal, `www`, `api` y `media` si corresponde. **DNS, CDN y WAF de Cloudflare.** Resuelve **D-07**; la topología lógica ya viene fijada por **D-15** (`Task/011`). | infra | 034 | Pendiente |
| `Task/036-Publicar-Primer-Contenido` | **Primera ejecución de las migraciones en producción.** Administrador. Perfil. Artículo. Review. Video. Imágenes. | backend, frontend | 035 | Pendiente |

---

## ETAPA 11 — Automatización de Despliegues

**Objetivo:** que cada cambio aprobado llegue a la nube de forma automática y controlada.

**Dependencias:** Etapa 10.
**Hito que completa:** *CD operativo, sin acciones destructivas automáticas.*
**Ficha:** [STAGE-11-deployment-automation.md](../stages/STAGE-11-deployment-automation.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/037-Deploy-Automatico-Frontend` | GitHub Actions hacia Cloudflare Pages. | frontend | 036 | Pendiente |
| `Task/038-Deploy-Automatico-Backend` | GitHub Actions hacia Lambda usando OIDC. **Canal repetible de migraciones en producción**: quién las ejecuta, desde dónde, con qué credencial, en qué orden respecto al despliegue, cómo se revierte y qué impide una ejecución accidental. | backend | 036 | Pendiente |
| `Task/039-Automatizar-Terraform` | Plan revisable. Apply protegido. Sin destrucción automática. Validación de IaC en CI sobre emulador **efímero**, sin credenciales cloud. **Credenciales, rotación, *scopes*, entornos protegidos y guardas de destino para los tres providers: AWS, Cloudflare y VPS.** **Terraform no sustituye a Ansible, cloud-init ni a los scripts idempotentes** en la configuración del sistema operativo del VPS (**D-18**, `Task/029`). | infra | 037, 038 | Pendiente |

---

## ETAPA 12 — Lanzamiento y Operación

**Objetivo:** validar producción de extremo a extremo y proteger el costo de forma
permanente.

**Dependencias:** Etapa 11.
**Hito que completa:** *Blog lanzado, operado y con costo bajo control.*
**Ficha:** [STAGE-12-launch-and-operations.md](../stages/STAGE-12-launch-and-operations.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/040-Validacion-Final-Produccion` | Comprobación **end-to-end** de lo realmente implementado: **Cloudflare** (DNS, CDN, WAF), **Pages**, **API Gateway**, **Lambda**, **S3**, **SSM**, HTTPS, dominio, login, contenido, SEO, responsive y rollback. **Y la capa de datos: conexión a PgBouncer, PostgreSQL, disponibilidad y disco del VPS, TLS y vigencia del certificado, backup reciente y restore vigente, runbooks.** **Y la observabilidad: CloudWatch mínimo, Grafana Cloud y Alloy operando de verdad**, más la integración de **D-20** si existe. | infra, frontend, backend | 039 | Pendiente |
| `Task/041-Proteccion-de-Costos` | Presupuestos. Alarmas. Retención. Límites. Revisión periódica. **Todos los recursos productivos que cuestan dinero, no solo AWS: VPS, dominio, IPv4 si aplica, almacenamiento de backups, snapshots, transferencia, Cloudflare si aplica y Grafana Cloud** (**D-19**). Precios **vigentes en el momento**, nunca heredados, y **confirmación de que los tiers gratuitos siguen siendo aplicables** (**R-38**). | infra | 040 | Pendiente |

---

## Mapa de responsabilidades transversales

Registrado en `Task/005.5` tras la auditoría. Resuelve las cadenas que atraviesan varias
tareas y que antes no tenían un propietario inequívoco. **No añade tareas ni cambia
identificadores.**

| Cadena | Define / construye | Materializa | Valida antes del lanzamiento |
| --- | --- | --- | --- |
| **`S3Storage`** | `Task/010` — interfaz, `MinIOStorage`, código de `S3Storage`, pruebas de contrato | `Task/030` — bucket, políticas, CORS, *lifecycle*, prefirmadas · `Task/032` — *wiring* | `Task/040` |
| **Backup productivo** | `Task/029` — mecanismo, cifrado, retención, RPO/RTO y **restore demostrado** off-host | `Task/030` — destino S3, política, permisos y retención definitiva | `Task/040` — backup reciente y **restore vigente** |
| **Identidad del VPS hacia AWS** (**D-16**) | `Task/029` — **decide** el mecanismo y sus restricciones de seguridad | `Task/030` — crea el principal, la política y el destino | `Task/040` |
| **Certificado TLS de PgBouncer** | `Task/029` — emisión, CA, *hostname*, instalación, renovación y confianza desde el cliente | `Task/029` | `Task/040` — validación real desde Lambda y vigencia |
| **Observabilidad del VPS** | `Task/029` — *baseline*: uptime, CPU, RAM, disco, PostgreSQL, PgBouncer, fallo de backup, caducidad de certificado | `Task/029` | `Task/040` |
| **Migraciones en producción** | `Task/036` — **primera** ejecución | `Task/038` — canal repetible, credencial, orden, *rollback* y protección | `Task/040` |
| **Medios públicos y URLs** (**D-08**) | `Task/010` — persiste **claves de objeto** · `Task/016` — `og:image` estable | `Task/030` — resuelve **D-08** | `Task/040` |
| **Credenciales CI multi-provider** | `Task/028` — **solo** GitHub → AWS | `Task/039` — AWS, Cloudflare y VPS: rotación, *scopes*, entornos protegidos y guardas de destino | `Task/040` |
| **Topología lógica de dominios** (**D-15**) | `Task/011` — mismo *site*, subdominios o dominios separados; cookies y CORS | `Task/018` — CORS efectivo | `Task/035` — dominio concreto y DNS (**D-07**) |
| **Observabilidad de producción** (`Task/006.2`) | `Task/029` — **Grafana Alloy** y el *baseline* del VPS · `Task/031` — **CloudWatch mínimo** y la base de **D-20** | `Task/029`, `Task/031` | `Task/040` — que **opera de verdad**, no que está configurada |
| **Telemetría portable de la aplicación** (`Task/006.2`) | `Task/017` — logs JSON y correlation ID, **sin acoplar el dominio a ningún destino** | `Task/018` — redacción y endurecimiento | `Task/040` |
| **Secretos del VPS** (**D-17**, `Task/006.2`) | `Task/029` — herramienta, custodia y rotación de la clave | `Task/029` | `Task/040` |
| **Configuración del sistema operativo del VPS** (**D-18**, `Task/006.2`) | `Task/029` — mecanismo y *drift* | `Task/029` · `Task/039` no lo sustituye con Terraform | `Task/040` |
| **Costo de la observabilidad** (**D-19**, `Task/006.2`) | `Task/027` — presupuesto (**D-13**) | `Task/031`, `Task/029` | `Task/041` — **precios reales del momento** |

**Reglas que esto fija:**

- **Ninguna tarea exige como evidencia final algo que solo existe después de ella.**
- `Task/017` es observabilidad **local**; `Task/031` es **solo AWS**. Ninguna de las dos
  observa el VPS: eso es de `Task/029` con **Grafana Alloy**, verificado por `Task/040`.
- **El backup tiene un único owner por tramo**: mecanismo en `Task/029`, destino y retención
  en `Task/030`, verificación en `Task/040`. **No se duplica.**
- `Task/029` **define y prepara**; `Task/030`/`Task/032` **materializan**; `Task/040`
  **verifica**, no implementa.

---

## Cálculo del avance

```
avance_etapa  = tareas_aprobadas_en_etapa / tareas_totales_en_etapa
avance_global = tareas_aprobadas_totales  / 41
```

Actualmente: `17 / 41 = 41 %`.

> **Corrección de *drift* documental, 2026-09-06.** Este bloque afirmaba `9 / 41 = 22 %`
> mientras [STATUS.md](STATUS.md) registraba **16 / 41**: el cálculo había dejado de
> actualizarse en aprobaciones anteriores. El valor canónico es y era el de `STATUS.md`.
> **No lo causó `Task/017` y no contó como trabajo funcional suyo**; se corrigió aquí porque
> la tarea ya modificaba este documento para su propio estado. El **17.º** del numerador es
> `Task/017`, aprobada el 2026-09-06 — eso sí es avance.

**Precisión sobre O-09.** La fila de `Task/017` ligaba la *telemetría portable* a **O-09**.
Son cosas distintas y ambas se conservan intactas: la portabilidad es el **principio 9** de
[`overview.md`](../architecture/overview.md) §5, cerrado por `Task/006.2` con
[ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md); **O-09** es la
privacidad de la telemetría **exportada a un tercero**, y sus propietarios siguen siendo
`Task/029`, `Task/018` y `Task/040`. `Task/017` **no** es owner de O-09.

Las tareas de mantenimiento (`Task/002.1`, `Task/005.1`, `Task/005.2`, `Task/005.3`,
`Task/005.4`, `Task/005.5`, `Task/005.6`, `Task/005.7`, `Task/006.1`, `Task/006.2`) **no
entran en el numerador ni en el denominador**.

Ver estado vigente en [STATUS.md](STATUS.md).
