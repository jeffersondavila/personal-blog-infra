# ROADMAP — Blog Personal

Vista resumida y ordenada de todo el proyecto: 13 etapas (00 → 12) y 41 tareas.

- **Última actualización:** 2026-07-31
- **Estrategia:** local-first (ver [ADR-001](../adr/ADR-001-local-first.md))
- **Avance global:** **10 %** (4 de 41 tareas aprobadas)

Estados oficiales: `Pendiente` · `En progreso` · `Lista para validación` · `Aprobada` ·
`Bloqueada` · `Descartada`.

> El porcentaje de avance se calcula **solo** con tareas en estado `Aprobada`.
> Ninguna tarea puede marcarse `Aprobada` sin autorización explícita del usuario.

---

## Resumen de etapas

| # | Etapa | Tareas | Aprobadas | Avance | Estado | Depende de |
| --- | --- | --- | --- | --- | --- | --- |
| 00 | Fundación y Gobierno | 2 | 2 | 100 % | **Completada** | — |
| 01 | Infraestructura Local | 2 | 2 | **100 %** | **Completada** | 00 ✔ |
| 02 | Fundaciones de las Aplicaciones | 3 | 0 | 0 % | **Siguiente** | 01 ✔ |
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
| | **Total** | **41** | **4** | **10 %** | | |

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

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/005-Fundacion-Backend-FastAPI` | Base profesional de FastAPI. Configuración. Logging. PostgreSQL. Alembic. Pruebas. Dockerfile. | backend | 004 | Pendiente |
| `Task/006-Fundacion-Frontend-React` | React. TypeScript. Vite. Router. Cliente HTTP. Pruebas. Build. | frontend | 004 | Pendiente |
| `Task/007-Integracion-Local` | Integrar frontend, backend, PostgreSQL y MinIO. Reverse proxy. Docker Compose completo. Supervisión desde Portainer. | infra, frontend, backend | 005, 006 | Pendiente |

---

## ETAPA 03 — Dominio y Backend

**Objetivo:** modelar el dominio del blog y exponer las APIs pública y administrativa
con almacenamiento de archivos y autenticación.

**Dependencias:** Etapa 02.
**Hito que completa:** *Backend funcionalmente completo para el MVP.*
**Ficha:** [STAGE-03-domain-and-backend.md](../stages/STAGE-03-domain-and-backend.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/008-Modelo-de-Datos` | Perfil. Artículos. Reviews de libros. Videos. Proyectos. Etiquetas. Medios. Administrador. Auditoría. | backend | 007 | Pendiente |
| `Task/009-API-Publica` | Consultas públicas. Paginación. Filtros. Búsqueda. Contenido publicado. | backend | 008 | Pendiente |
| `Task/010-Almacenamiento-Compatible-S3` | Interfaz `ObjectStorage`. MinIO local. Adaptador futuro para Amazon S3. Imágenes y miniaturas. | backend | 008 | Pendiente |
| `Task/011-Autenticacion-Administrativa` | Login. Sesiones o tokens. Protección de endpoints. Rate limiting. Auditoría. | backend | 008 | Pendiente |
| `Task/012-API-Administrativa` | CRUD. Borradores. Publicación. Archivado. Gestión de imágenes. | backend | 009, 010, 011 | Pendiente |

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

## ETAPA 08 — Preparación Cloud sin Cuentas

**Objetivo:** dejar todo listo para la nube **sin crear cuentas ni recursos reales**.

**Dependencias:** Etapa 07.
**Hito que completa:** *Artefactos e IaC listos y validados en seco.*
**Ficha:** [STAGE-08-cloud-ready.md](../stages/STAGE-08-cloud-ready.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/023-Compatibilidad-FastAPI-Lambda` | Adaptador de FastAPI para API Gateway HTTP API y Lambda. | backend | 022 | Pendiente |
| `Task/024-Artefacto-ZIP-Lambda` | Paquete Linux reproducible. Validación de tamaño. Checksums. | backend | 023 | Pendiente |
| `Task/025-Terraform-Cloud` | Módulos para Cloudflare y AWS. Validaciones sin crear recursos reales. | infra | 022 | Pendiente |
| `Task/026-Runbooks-de-Despliegue` | Creación. Validación. Rollback. Destrucción. Recuperación. | infra | 024, 025 | Pendiente |

---

## ETAPA 09 — Cuentas y Seguridad Cloud

**Objetivo:** crear las cuentas cloud con controles de costo y acceso **antes** de
desplegar nada.

**Dependencias:** Etapa 08.
**Hito que completa:** *Cuentas cloud seguras, con presupuesto y acceso sin credenciales permanentes.*
**Ficha:** [STAGE-09-cloud-accounts.md](../stages/STAGE-09-cloud-accounts.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/027-Configurar-Cuentas-y-Presupuestos` | AWS. Cloudflare. MFA. Presupuestos. Alertas. | infra | 026 | Pendiente |
| `Task/028-GitHub-OIDC-AWS` | Roles temporales. Sin credenciales AWS permanentes. | infra | 027 | Pendiente |
| `Task/029-Seleccionar-PostgreSQL-Administrado` | Evaluación por costo. TLS. Backups. Pooling. Compatibilidad con Lambda. | infra | 027 | Pendiente |

---

## ETAPA 10 — Despliegue Cloud

**Objetivo:** desplegar el blog en la nube y publicar el primer contenido real.

**Dependencias:** Etapa 09.
**Hito que completa:** *Blog en línea y accesible por dominio propio.*
**Ficha:** [STAGE-10-cloud-deployment.md](../stages/STAGE-10-cloud-deployment.md)

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
| `Task/039-Automatizar-Terraform` | Plan revisable. Apply protegido. Sin destrucción automática. | infra | 037, 038 | Pendiente |

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

Actualmente: `4 / 41 = 10 %`.

Ver estado vigente en [STATUS.md](STATUS.md).
