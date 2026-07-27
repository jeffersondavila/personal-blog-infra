# ADR-002 — Tres repositorios separados

| Campo | Valor |
| --- | --- |
| **Estado** | Aceptada |
| **Fecha** | 2026-07-26 |
| **Tarea** | `Task/001-Inicializar-Workspace-y-Roadmap` |
| **Reemplaza a** | — |
| **Reemplazada por** | — |

---

## Contexto

El proyecto tiene tres cuerpos de trabajo con ciclos de vida, lenguajes y herramientas
distintos: interfaz de usuario, API de dominio e infraestructura/planificación.

Al iniciar `Task/001` ya existían tres repositorios Git separados, cada uno con su
remoto de GitHub configurado. La decisión consiste en **ratificar** esa separación y
definir sus reglas.

## Decisión

Se mantienen **tres repositorios independientes**:

### `personal-blog-frontend`

| Responsabilidad | Fuera de responsabilidad |
| --- | --- |
| Sitio público y panel administrativo | Lógica de dominio |
| Componentes y sistema de diseño | Acceso a base de datos |
| Cliente HTTP hacia el API | Definición de infraestructura |
| Tests de interfaz | Roadmap y planificación |

React + TypeScript + Vite. Se despliega en Cloudflare Pages.

### `personal-blog-backend`

| Responsabilidad | Fuera de responsabilidad |
| --- | --- |
| API pública y administrativa | Interfaz de usuario |
| Modelo de dominio y persistencia | Terraform y Docker Compose del entorno |
| Migraciones de base de datos | Roadmap y planificación |
| Autenticación y auditoría | |

FastAPI + PostgreSQL. Se despliega en AWS Lambda.

### `personal-blog-infra`

| Responsabilidad | Fuera de responsabilidad |
| --- | --- |
| **Fuente de verdad de la planificación** | Código de aplicación |
| Roadmap, estado, tareas, ADR | Componentes de UI |
| Docker Compose del entorno local | Lógica de negocio |
| Terraform de la nube | |
| Runbooks de despliegue y recuperación | |

## Consecuencias

### Ventajas

- **Responsabilidades explícitas.** El límite entre capas es físico, no una convención
  que se erosiona con el tiempo.
- **CI independiente y rápida.** Cada repositorio ejecuta solo lo que le corresponde
  (Etapa 06), sin construir lo que no cambió.
- **Despliegue independiente.** El frontend puede publicarse sin tocar el backend, y
  viceversa (Etapa 11).
- **Historial legible.** El log de cada repositorio cuenta una sola historia.
- **Permisos y automatización acotados.** El rol OIDC de cada repositorio puede limitarse
  a lo que ese repositorio despliega (`Task/028`).
- **Coherente con los destinos de despliegue**, que ya son plataformas distintas
  (Cloudflare Pages y AWS Lambda).

### Costos de coordinación

- **Cambios que cruzan repositorios.** Un cambio de contrato de API toca backend y
  frontend a la vez.
  *Mitigación:* misma rama `Task/*` en todos los repositorios afectados, y la tarea se
  valida y aprueba como una unidad.
- **Sin refactorización atómica.** No existe un commit único que cambie ambos lados.
  *Mitigación:* los cambios de contrato se hacen compatibles hacia atrás cuando es
  posible; si no, se ordena backend antes que frontend dentro de la misma tarea.
- **Estado disperso.** Saber en qué punto está el proyecto exige un lugar central.
  *Mitigación:* `personal-blog-infra` es la única fuente de verdad; los otros dos
  repositorios la referencian y **no duplican** el roadmap.
- **Configuración repetida.** `.gitignore`, `.editorconfig` y `CONTRIBUTING.md` se
  mantienen en tres sitios.
  *Mitigación:* se crean coherentes desde `Task/001` y se revisan como parte de la
  Definition of Done.

## Sincronización de tareas que afectan varios repositorios

1. La tarea se registra **una sola vez**, en `personal-blog-infra/docs/tasks/`.
2. La ficha declara qué repositorios están involucrados.
3. Se crea **la misma rama** `Task/<numero>-<nombre>` en cada repositorio afectado.
4. Se implementa el alcance en cada repositorio, sin desbordarlo.
5. Las validaciones se ejecutan en todos los repositorios afectados.
6. El reporte único en `docs/task-reports/` consolida el resultado de todos.
7. La aprobación (`approved: Task/<rama>`) cubre la tarea completa y dispara el flujo de
   cierre en cada repositorio afectado.

Tareas multi-repositorio previstas: `Task/001`, `Task/007`, `Task/016`, `Task/017`,
`Task/018`, `Task/022`, `Task/034`, `Task/036`, `Task/040`.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
| --- | --- |
| Monorepo único | Simplificaría los cambios que cruzan capas, pero exigiría herramientas de monorepo (filtros de CI por ruta, versionado selectivo) desproporcionadas para un proyecto de una persona, y no encaja con destinos de despliegue tan distintos. Además, los tres repositorios ya existían con sus remotos configurados; unificarlos implicaría descartar esa estructura sin beneficio claro. |
| Dos repositorios (aplicación + infraestructura) | Mezclaría dos lenguajes y dos pipelines de CI en un mismo repositorio, y acoplaría el despliegue del frontend al del backend. |
| Cuatro o más repositorios | Fragmentación excesiva y coordinación desproporcionada para el tamaño del proyecto. |

## Referencias

- [ADR-001 — Local-first](ADR-001-local-first.md)
- [WORKFLOW.md](../project-management/WORKFLOW.md)
- [Arquitectura — Visión general](../architecture/overview.md)
