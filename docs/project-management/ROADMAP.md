# ROADMAP — Blog Personal

Vista resumida y ordenada de todo el proyecto: 13 etapas (00 → 12) y 41 tareas.

- **Última actualización:** 2026-08-15
- **Estrategia:** local-first (ver [ADR-001](../adr/ADR-001-local-first.md)), extendida a la
  infraestructura con **AWS Local Parity** — ver
  [aws-local-parity.md](../architecture/aws-local-parity.md) y
  [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) (**Aceptada**)
- **Capa de datos de producción:** PostgreSQL autogestionado en **VPS externo** con
  PgBouncer — ver
  [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) y
  [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) (**Aceptada**)
- **Avance global:** **12 %** (5 de 41 tareas aprobadas)

Estados oficiales: `Pendiente` · `En progreso` · `Lista para validación` · `Aprobada` ·
`Bloqueada` · `Descartada`.

> El porcentaje de avance se calcula **solo** con tareas en estado `Aprobada`.
> Ninguna tarea puede marcarse `Aprobada` sin autorización explícita del usuario.

> **Tareas de mantenimiento.** Las tareas con sufijo (`Task/002.1`, `Task/005.1`,
> `Task/005.2`, `Task/005.3`, …) son mantenimiento de gobierno: **no forman parte de estas
> 41** y **no alteran el avance**. Su estado se registra en [`STATUS.md`](STATUS.md).

---

## Resumen de etapas

| # | Etapa | Tareas | Aprobadas | Avance | Estado | Depende de |
| --- | --- | --- | --- | --- | --- | --- |
| 00 | Fundación y Gobierno | 2 | 2 | 100 % | **Completada** | — |
| 01 | Infraestructura Local | 2 | 2 | **100 %** | **Completada** | 00 ✔ |
| 02 | Fundaciones de las Aplicaciones | 3 | 1 | **33 %** | **En curso** | 01 ✔ |
| 03 | Dominio y Backend | 5 | 0 | 0 % | Pendiente | 02 |
| 04 | Experiencia del Usuario | 3 | 0 | 0 % | Pendiente | 03 |
| 05 | Calidad y Seguridad | 3 | 0 | 0 % | Pendiente | 04 |
| 06 | Integración Continua | 3 | 0 | 0 % | Pendiente | 05 |
| 07 | Validación Local | 1 | 0 | 0 % | Pendiente | 06 |
| 08 | Preparación Cloud sin Cuentas | 4 | 0 | 0 % | Pendiente | 07 |
| 09 | Cuentas y Seguridad Cloud | 3 | 0 | 0 % | Pendiente | 08 |
| 10 | Despliegue Cloud | 7 | 0 | 0 % | Pendiente | 09 |
| 11 | Automatización de Despliegues | 3 | 0 | 0 % | Pendiente | 10 |
| 12 | Lanzamiento y Operación | 2 | 0 | 0 % | Pendiente | 11 |
| | **Total** | **41** | **5** | **12 %** | | |

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
**Estado:** **En curso** desde el 2026-08-01. **1 de 3** tareas aprobadas.

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/005-Fundacion-Backend-FastAPI` | Base profesional de FastAPI. Configuración. Logging. PostgreSQL. Alembic. Pruebas. Dockerfile. | backend, infra (documentación) | 004 | **Aprobada** (2026-08-12) |
| `Task/006-Fundacion-Frontend-React` | React. TypeScript. Vite. Router. Cliente HTTP. Pruebas. Build. | frontend | 004 | Pendiente |
| `Task/007-Integracion-Local` | Integrar frontend, backend, PostgreSQL y MinIO. Reverse proxy. Docker Compose completo. Supervisión desde Portainer. | infra, frontend, backend | 005, 006 | Pendiente |

---

## ETAPA 03 — Dominio y Backend

**Objetivo:** modelar el dominio del blog y exponer las APIs pública y administrativa
con almacenamiento de archivos y autenticación.

**Dependencias:** Etapa 02.
**Hito que completa:** *Backend funcionalmente completo para el MVP.*
**Ficha:** [STAGE-03-domain-and-backend.md](../stages/STAGE-03-domain-and-backend.md)

> **Test-first obligatorio en toda la etapa.** `Task/008` a `Task/012` construyen el backend
> funcional: cada comportamiento nuevo empieza por una prueba que falla
> (**RED → GREEN → REFACTOR**), con matriz de casos previa y evidencia registrada en el
> reporte. Regla completa: [`BACKEND_TESTING_STRATEGY.md`](BACKEND_TESTING_STRATEGY.md).

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/008-Modelo-de-Datos` | Perfil. Artículos. Reviews de libros. Videos. Proyectos. Etiquetas. Medios. Administrador. Auditoría. **Test-first**: invariantes y transiciones; migraciones validadas con integración real. | backend | 007 | Pendiente |
| `Task/009-API-Publica` | Consultas públicas. Paginación. Filtros. Búsqueda. Contenido publicado. **Test-first**: contrato HTTP y el caso negativo de contenido no publicado. | backend | 008 | Pendiente |
| `Task/010-Almacenamiento-Compatible-S3` | Interfaz `ObjectStorage`. MinIO local. Adaptador futuro para Amazon S3. Imágenes y miniaturas. **Test-first**: contrato primero, después integración con MinIO. | backend | 008 | Pendiente |
| `Task/011-Autenticacion-Administrativa` | Login. Sesiones o tokens. Protección de endpoints. Rate limiting. Auditoría. **Test-first**: casos negativos de acceso dentro del alcance. | backend | 008 | Pendiente |
| `Task/012-API-Administrativa` | CRUD. Borradores. Publicación. Archivado. Gestión de imágenes. **Test-first**: matriz de transiciones antes del caso de uso. | backend | 009, 010, 011 | Pendiente |

---

## ETAPA 04 — Experiencia del Usuario

**Objetivo:** construir el sistema de diseño, el sitio público y el panel administrativo.

**Dependencias:** Etapa 03.
**Hito que completa:** *Blog usable de extremo a extremo en local.*
**Ficha:** [STAGE-04-user-experience.md](../stages/STAGE-04-user-experience.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/013-Sistema-de-Diseno` | Tokens. Componentes. Tipografía. Responsive. Accesibilidad base. | frontend | 012 | Pendiente |
| `Task/014-Sitio-Publico` | Inicio. Quién soy. Artículos. Reviews. Videos. Proyectos. Contacto. Página 404. | frontend | 013 | Pendiente |
| `Task/015-Panel-Administrativo` | Dashboard. Editor Markdown. Gestión de contenido. Carga de imágenes. Vista previa. | frontend | 013 | Pendiente |

---

## ETAPA 05 — Calidad y Seguridad

**Objetivo:** elevar el producto a estándar publicable: SEO, accesibilidad, rendimiento,
observabilidad y endurecimiento de seguridad.

**Dependencias:** Etapa 04.
**Hito que completa:** *Producto con calidad y seguridad verificables.*
**Ficha:** [STAGE-05-quality-security.md](../stages/STAGE-05-quality-security.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/016-SEO-Accesibilidad-y-Rendimiento` | Metadatos. Open Graph. Sitemap. Robots. Optimización. Accesibilidad. | frontend, backend | 014, 015 | Pendiente |
| `Task/017-Observabilidad-Local` | Logs JSON. Correlation ID. Healthchecks. Auditoría. Diagnóstico con Portainer. | backend, infra | 014, 015 | Pendiente |
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
| `Task/021-CI-Infraestructura` | Docker Compose config. Validación de scripts. Terraform fmt y validate. Escaneo de secretos. | infra | 018 | Pendiente |

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
| `Task/025-Terraform-Cloud` | Terraform **portable**: módulos compartidos, provider AWS oficial, destino local y destino real. `plan`/`apply`/`destroy` **ejecutados en local**. Matriz de paridad. Guardas *fail-closed*. Resuelve **D-06**. Sin recursos reales. | infra | 022 | Pendiente |
| `Task/026-Runbooks-de-Despliegue` | Creación. Validación del destino. Rollback. *Drift*. Destrucción. Recuperación. Transición a AWS. | infra | 024, 025 | Pendiente |

---

## ETAPA 09 — Cuentas y Seguridad Cloud

**Objetivo:** crear las cuentas cloud con controles de costo y acceso **antes** de
desplegar nada.

**Dependencias:** Etapa 08.
**Hito que completa:** *Cuentas cloud seguras, con presupuesto y acceso sin credenciales permanentes.*
**Ficha:** [STAGE-09-cloud-accounts.md](../stages/STAGE-09-cloud-accounts.md)

> **`Task/029` cambia de alcance, no de número.** Desde `Task/005.3` (2026-08-15,
> **propuesta**) la base de datos de producción deja de ser un servicio administrado y pasa
> a ser **PostgreSQL autogestionado en un VPS externo, con PgBouncer delante**, mientras el
> backend permanece en AWS Lambda. **El identificador `029` no cambia** y el roadmap sigue
> teniendo **41 tareas**. Estrategia:
> [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) ·
> [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md).

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/027-Configurar-Cuentas-y-Presupuestos` | AWS. Cloudflare. MFA. Presupuestos. Alertas. | infra | 026 | Pendiente |
| `Task/028-GitHub-OIDC-AWS` | Roles temporales. Sin credenciales AWS permanentes. | infra | 027 | Pendiente |
| `Task/029-Preparar-PostgreSQL-Produccion-en-VPS` | Selección del VPS por costo, región y RTT. PgBouncer. TLS y SCRAM. Firewall y SSH. Backups fuera del host y restore probado. | infra | 027 | Pendiente |

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

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/030-Desplegar-Amazon-S3` | Bucket. CORS. Políticas. URLs prefirmadas. Lifecycle. | infra | 029 | Pendiente |
| `Task/031-Desplegar-SSM-y-CloudWatch` | Parámetros. Logs. Retención. Alarmas mínimas. | infra | 029 | Pendiente |
| `Task/032-Desplegar-AWS-Lambda` | Función. IAM. Configuración. Límites. | infra | 030, 031 | Pendiente |
| `Task/033-Desplegar-API-Gateway` | HTTP API. Rutas. CORS. Throttling. | infra | 032 | Pendiente |
| `Task/034-Desplegar-Cloudflare-Pages` | React. Variables. Dominio. | infra, frontend | 033 | Pendiente |
| `Task/035-Configurar-DNS` | Dominio principal. `www`. `api`. `media` si corresponde. | infra | 034 | Pendiente |
| `Task/036-Publicar-Primer-Contenido` | Migraciones. Administrador. Perfil. Artículo. Review. Video. Imágenes. | backend, frontend | 035 | Pendiente |

---

## ETAPA 11 — Automatización de Despliegues

**Objetivo:** que cada cambio aprobado llegue a la nube de forma automática y controlada.

**Dependencias:** Etapa 10.
**Hito que completa:** *CD operativo, sin acciones destructivas automáticas.*
**Ficha:** [STAGE-11-deployment-automation.md](../stages/STAGE-11-deployment-automation.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/037-Deploy-Automatico-Frontend` | GitHub Actions hacia Cloudflare Pages. | frontend | 036 | Pendiente |
| `Task/038-Deploy-Automatico-Backend` | GitHub Actions hacia Lambda usando OIDC. | backend | 036 | Pendiente |
| `Task/039-Automatizar-Terraform` | Plan revisable. Apply protegido. Sin destrucción automática. Validación de IaC en CI sobre emulador **efímero**, sin credenciales cloud. | infra | 037, 038 | Pendiente |

---

## ETAPA 12 — Lanzamiento y Operación

**Objetivo:** validar producción de extremo a extremo y proteger el costo de forma
permanente.

**Dependencias:** Etapa 11.
**Hito que completa:** *Blog lanzado, operado y con costo bajo control.*
**Ficha:** [STAGE-12-launch-and-operations.md](../stages/STAGE-12-launch-and-operations.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/040-Validacion-Final-Produccion` | HTTPS. Dominio. API. Login. Contenido. Logs. SEO. Responsive. Rollback. | infra, frontend, backend | 039 | Pendiente |
| `Task/041-Proteccion-de-Costos` | Presupuestos. Alarmas. Retención. Límites. Revisión periódica de recursos. | infra | 040 | Pendiente |

---

## Cálculo del avance

```
avance_etapa  = tareas_aprobadas_en_etapa / tareas_totales_en_etapa
avance_global = tareas_aprobadas_totales  / 41
```

Actualmente: `5 / 41 = 12 %`.

Las tareas de mantenimiento (`Task/002.1`, `Task/005.1`, `Task/005.2`, `Task/005.3`) **no
entran en el numerador ni en el denominador**.

Ver estado vigente en [STATUS.md](STATUS.md).
