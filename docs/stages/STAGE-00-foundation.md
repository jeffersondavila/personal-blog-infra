# ETAPA 00 — Fundación y Gobierno

| Campo | Valor |
| --- | --- |
| **Número** | 00 |
| **Estado** | En progreso |
| **Dependencias** | Ninguna |
| **Tareas** | 2 |
| **Aprobadas** | 1 |
| **Avance** | 50 % |
| **Hito que completa** | Gobierno del proyecto establecido y alcance del MVP cerrado. |

---

## Objetivo

Dejar los tres repositorios preparados, con reglas de trabajo claras, un sistema
documental de seguimiento y un MVP y una arquitectura acordados **antes** de escribir
una sola línea de código de la aplicación.

## Por qué esta etapa existe

Sin gobierno explícito, un proyecto personal de esta escala (41 tareas, 3 repositorios,
2 entornos) deriva en trabajo perdido y alcance difuso. Esta etapa fija: dónde vive la
verdad, cómo se nombran las ramas, qué significa "terminado" y quién aprueba.

## Tareas

### `Task/001-Inicializar-Workspace-y-Roadmap` — *Aprobada* (2026-07-26)

Preparar repositorios, documentación y seguimiento.

- Inspección de los tres repositorios.
- Sistema documental en `personal-blog-infra`.
- Roadmap con 13 etapas y 41 tareas.
- `STATUS.md`, `WORKFLOW.md`, `TASK_TEMPLATE.md`, `DEFINITION_OF_DONE.md`.
- ADR fundacionales y mapeo local → nube.
- Archivos base de los tres repositorios.

Ficha: [TASK-001](../tasks/TASK-001-initial-workspace-and-roadmap.md)

### `Task/002-Definir-MVP-y-Arquitectura` — *Lista para validación*

Definir requerimientos funcionales, arquitectura de software, contratos generales y
límites del MVP.

- Requerimientos funcionales y no funcionales del MVP.
- Secciones del blog y su contenido mínimo.
- Arquitectura de software (capas, módulos, límites).
- Contratos generales de API (recursos y operaciones, sin implementar).
- Modelo conceptual de dominio (sin esquema físico).
- Qué queda explícitamente fuera del MVP.

**Depende de:** `Task/001` aprobada. ✔

Ficha: [TASK-002](../tasks/TASK-002-define-mvp-and-architecture.md)
Documentos: [MVP_SCOPE](../product/MVP_SCOPE.md) ·
[USER_FLOWS](../product/USER_FLOWS.md) · [CONTENT_MODEL](../product/CONTENT_MODEL.md) ·
[software-architecture](../architecture/software-architecture.md) ·
[api-contracts](../architecture/api-contracts.md) ·
[non-functional-requirements](../architecture/non-functional-requirements.md) ·
[security-boundaries](../architecture/security-boundaries.md) ·
[open-decisions](../architecture/open-decisions.md) ·
[ADR-004](../adr/ADR-004-modular-monolith.md) *(Propuesta)* ·
[ADR-005](../adr/ADR-005-markdown-content.md) *(Propuesta)*

> ADR-004 y ADR-005 están en estado **Propuesta**: serán aceptados cuando el usuario
> apruebe `Task/002`.

## Criterios de salida de la etapa

- [ ] Los tres repositorios tienen README, `.gitignore`, `.editorconfig` y `CONTRIBUTING.md` coherentes.
- [ ] El roadmap completo está registrado y es consultable.
- [ ] Existe plantilla de tarea y definición de terminado.
- [ ] Las decisiones fundacionales están registradas como ADR.
- [ ] El MVP está delimitado y la arquitectura de software acordada.
- [ ] `Task/001` y `Task/002` aprobadas por el usuario.

## Fuera del alcance de la etapa

- Código de aplicación (React, FastAPI).
- Docker Compose, PostgreSQL, MinIO, Portainer.
- Terraform, GitHub Actions.
- Cualquier recurso o cuenta cloud.

## Siguiente etapa

[ETAPA 01 — Infraestructura Local](STAGE-01-local-infrastructure.md)
