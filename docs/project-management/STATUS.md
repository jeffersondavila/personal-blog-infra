# STATUS — Estado del proyecto Blog Personal

**Última actualización:** 2026-07-26

---

## Vista rápida

| Campo | Valor |
| --- | --- |
| **Etapa actual** | ETAPA 01 — Infraestructura Local (siguiente). ETAPA 00 **completada** |
| **Tarea actual** | Ninguna en ejecución |
| **Estado de la tarea** | — |
| **Última tarea aprobada** | `Task/002-Definir-MVP-y-Arquitectura` — **Aprobada** el 2026-07-26 por jeffersondavila |
| **Próxima tarea prevista** | `Task/003-Crear-Infraestructura-Local` (Pendiente, no iniciada) |
| **Avance global** | **5 %** — 2 de 41 tareas aprobadas |
| **Bloqueos activos** | 0 |
| **Riesgos abiertos** | 6 (R-01 cerrado) |

> El avance se calcula **solo** con tareas `Aprobada`.

---

## Resumen del avance

| Etapa | Tareas | Aprobadas | Avance |
| --- | --- | --- | --- |
| 00 — Fundación y Gobierno | 2 | 2 | **100 %** |
| 01 — Infraestructura Local | 2 | 0 | 0 % |
| 02 — Fundaciones de las Aplicaciones | 3 | 0 | 0 % |
| 03 — Dominio y Backend | 5 | 0 | 0 % |
| 04 — Experiencia del Usuario | 3 | 0 | 0 % |
| 05 — Calidad y Seguridad | 3 | 0 | 0 % |
| 06 — Integración Continua | 3 | 0 | 0 % |
| 07 — Validación Local | 1 | 0 | 0 % |
| 08 — Preparación Cloud sin Cuentas | 4 | 0 | 0 % |
| 09 — Cuentas y Seguridad Cloud | 3 | 0 | 0 % |
| 10 — Despliegue Cloud | 7 | 0 | 0 % |
| 11 — Automatización de Despliegues | 3 | 0 | 0 % |
| 12 — Lanzamiento y Operación | 2 | 0 | 0 % |
| **Total** | **41** | **2** | **5 %** |

Distribución por estado:

| Estado | Tareas |
| --- | --- |
| Pendiente | 39 |
| En progreso | 0 |
| Lista para validación | 0 |
| **Aprobada** | **2** |
| Bloqueada | 0 |
| Descartada | 0 |

---

## Bloqueos

*Ninguno activo.*

| # | Tarea afectada | Motivo | Resolución | Estado |
| --- | --- | --- | --- | --- |
| B-01 | `Task/001` — pasos de publicación del cierre | No había credenciales de GitHub en el entorno y la sesión no podía abrir un diálogo de autenticación, por lo que no se pudo hacer push ni abrir el pull request. | El usuario instaló y autenticó **GitHub CLI** (cuenta `jeffersondavila`, HTTPS, `gh` como proveedor de credenciales de Git). Se completaron los push, se crearon y aceptaron los pull requests (`#1` en cada repositorio) y se eliminaron las ramas `Task/001` local y remotamente. | **Cerrado** (2026-07-26) |

> Todo bloqueo debe registrarse aquí indicando: tarea afectada, motivo del bloqueo y
> acción concreta necesaria para desbloquear.

---

## Riesgos

| # | Riesgo | Impacto | Mitigación prevista | Estado |
| --- | --- | --- | --- | --- |
| R-01 | Los tres repositorios no tenían commit inicial, por lo que `dev` y las ramas `Task/*` no podían existir como referencias Git. | Medio | **Resuelto** el 2026-07-26 durante la aprobación de `Task/001`: commit inicial vacío en `main`, `dev` creada desde `main` y `Task/001` creada desde `dev` en los tres repositorios. | **Cerrado** |
| R-02 | Costo cloud imprevisto al llegar a la Etapa 10. | Alto | Presupuestos y alarmas obligatorios en `Task/027`, antes de cualquier despliegue; refuerzo en `Task/041`. | Abierto |
| R-03 | La elección de PostgreSQL administrado puede condicionar el diseño de conexiones desde Lambda (pooling, límites). | Medio | Evaluar en `Task/029` y considerar el patrón de conexión desde `Task/005`. | Abierto |
| R-04 | El roadmap de 41 tareas puede quedar desactualizado si el alcance cambia. | Bajo | `STATUS.md` y `ROADMAP.md` se actualizan en cada cambio de estado, como parte de la Definition of Done. | Abierto |
| R-05 | Los enlaces cruzados entre repositorios asumen que los tres están clonados como carpetas hermanas. | Bajo | Suposición documentada en los README de frontend y backend; alternativa futura: enlazar a las URL de GitHub. | Abierto |
| R-06 | El alcance del MVP puede crecer durante la implementación. | Medio | [MVP_SCOPE.md](../product/MVP_SCOPE.md) §6 lista explícitamente lo excluido; toda incorporación exige un ADR que reemplace la decisión vigente. | Abierto |
| R-07 | El render de Markdown en el cliente puede resultar insuficiente para SEO. | Medio | Metadatos, Open Graph, canonical, sitemap y datos estructurados en `Task/016`; si no basta, se reconsidera [ADR-005](../adr/ADR-005-markdown-content.md). | Abierto |

---

## Tabla completa de tareas

| Tarea | Etapa | Repos | Estado |
| --- | --- | --- | --- |
| `Task/001-Inicializar-Workspace-y-Roadmap` | 00 | infra, frontend, backend | **Aprobada** |
| `Task/002-Definir-MVP-y-Arquitectura` | 00 | infra | **Aprobada** |
| `Task/003-Crear-Infraestructura-Local` | 01 | infra | Pendiente |
| `Task/004-Backups-y-Recuperacion-Local` | 01 | infra | Pendiente |
| `Task/005-Fundacion-Backend-FastAPI` | 02 | backend | Pendiente |
| `Task/006-Fundacion-Frontend-React` | 02 | frontend | Pendiente |
| `Task/007-Integracion-Local` | 02 | infra, frontend, backend | Pendiente |
| `Task/008-Modelo-de-Datos` | 03 | backend | Pendiente |
| `Task/009-API-Publica` | 03 | backend | Pendiente |
| `Task/010-Almacenamiento-Compatible-S3` | 03 | backend | Pendiente |
| `Task/011-Autenticacion-Administrativa` | 03 | backend | Pendiente |
| `Task/012-API-Administrativa` | 03 | backend | Pendiente |
| `Task/013-Sistema-de-Diseno` | 04 | frontend | Pendiente |
| `Task/014-Sitio-Publico` | 04 | frontend | Pendiente |
| `Task/015-Panel-Administrativo` | 04 | frontend | Pendiente |
| `Task/016-SEO-Accesibilidad-y-Rendimiento` | 05 | frontend, backend | Pendiente |
| `Task/017-Observabilidad-Local` | 05 | backend, infra | Pendiente |
| `Task/018-Endurecimiento-de-Seguridad` | 05 | infra, frontend, backend | Pendiente |
| `Task/019-CI-Frontend` | 06 | frontend | Pendiente |
| `Task/020-CI-Backend` | 06 | backend | Pendiente |
| `Task/021-CI-Infraestructura` | 06 | infra | Pendiente |
| `Task/022-Validacion-Local-Production-Like` | 07 | infra, frontend, backend | Pendiente |
| `Task/023-Compatibilidad-FastAPI-Lambda` | 08 | backend | Pendiente |
| `Task/024-Artefacto-ZIP-Lambda` | 08 | backend | Pendiente |
| `Task/025-Terraform-Cloud` | 08 | infra | Pendiente |
| `Task/026-Runbooks-de-Despliegue` | 08 | infra | Pendiente |
| `Task/027-Configurar-Cuentas-y-Presupuestos` | 09 | infra | Pendiente |
| `Task/028-GitHub-OIDC-AWS` | 09 | infra | Pendiente |
| `Task/029-Seleccionar-PostgreSQL-Administrado` | 09 | infra | Pendiente |
| `Task/030-Desplegar-Amazon-S3` | 10 | infra | Pendiente |
| `Task/031-Desplegar-SSM-y-CloudWatch` | 10 | infra | Pendiente |
| `Task/032-Desplegar-AWS-Lambda` | 10 | infra | Pendiente |
| `Task/033-Desplegar-API-Gateway` | 10 | infra | Pendiente |
| `Task/034-Desplegar-Cloudflare-Pages` | 10 | infra, frontend | Pendiente |
| `Task/035-Configurar-DNS` | 10 | infra | Pendiente |
| `Task/036-Publicar-Primer-Contenido` | 10 | backend, frontend | Pendiente |
| `Task/037-Deploy-Automatico-Frontend` | 11 | frontend | Pendiente |
| `Task/038-Deploy-Automatico-Backend` | 11 | backend | Pendiente |
| `Task/039-Automatizar-Terraform` | 11 | infra | Pendiente |
| `Task/040-Validacion-Final-Produccion` | 12 | infra, frontend, backend | Pendiente |
| `Task/041-Proteccion-de-Costos` | 12 | infra | Pendiente |

---

## Estado de los repositorios

| Repositorio | Ramas | Rama activa | `main` y `dev` sincronizadas |
| --- | --- | --- | --- |
| `personal-blog-infra` | `main`, `dev` | `main` | Ver nota |
| `personal-blog-frontend` | `main`, `dev` | `main` | Sí |
| `personal-blog-backend` | `main`, `dev` | `main` | Sí |

- `main` y `dev` están **publicadas** en GitHub en los tres repositorios y contienen el
  mismo contenido.
- Las ramas `Task/001-Inicializar-Workspace-y-Roadmap` fueron **eliminadas** local y
  remotamente tras integrarse mediante los pull requests `#1`.
- Los PR de `Task/001` se integraron desde la rama `Task/001` directamente hacia `main`,
  lo que dejó `main` y `dev` con el mismo contenido pero distintos commits de merge. Esa
  divergencia formal se **normalizó al inicio de `Task/002`** con un merge `--no-ff` de
  `origin/main` dentro de `dev`, publicado en los tres repositorios.
- `Task/002` se ejecutó **solo en `personal-blog-infra`**, porque únicamente modificaba
  documentación central. Tras su aprobación, la rama `Task/002-Definir-MVP-y-Arquitectura`
  se integró en `dev` con merge `--no-ff`, se publicó y se eliminó localmente. En
  `personal-blog-infra`, `dev` está **por delante de `main`** hasta que se acepte el pull
  request abierto hacia `main`; frontend y backend siguen sincronizados.

---

## Notas de estado

- La **implementación del blog no ha comenzado**. No existe código React, FastAPI,
  Docker Compose ni Terraform en ningún repositorio.
- **No se ha creado ningún recurso cloud** ni ninguna cuenta en proveedores.
- `Task/002` definió el **alcance del MVP y la arquitectura**, y fue **aprobada**. Con
  ella, la **ETAPA 00 queda completada** (2 de 2 tareas).
- ADR-001 a ADR-005 están todos en estado **Aceptada**.
- `Task/003` **no ha sido iniciada**.

Detalle completo: [ROADMAP.md](ROADMAP.md) ·
[TASK-001](../tasks/TASK-001-initial-workspace-and-roadmap.md) ·
[Reporte TASK-001](../task-reports/TASK-001-report.md) ·
[TASK-002](../tasks/TASK-002-define-mvp-and-architecture.md) ·
[Reporte TASK-002](../task-reports/TASK-002-report.md)

Documentos de producto y arquitectura producidos por `Task/002`:
[MVP_SCOPE](../product/MVP_SCOPE.md) · [USER_FLOWS](../product/USER_FLOWS.md) ·
[CONTENT_MODEL](../product/CONTENT_MODEL.md) ·
[software-architecture](../architecture/software-architecture.md) ·
[api-contracts](../architecture/api-contracts.md) ·
[non-functional-requirements](../architecture/non-functional-requirements.md) ·
[security-boundaries](../architecture/security-boundaries.md) ·
[open-decisions](../architecture/open-decisions.md)
