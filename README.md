# personal-blog-infra

Repositorio de **infraestructura, planificación y gobierno** del proyecto Blog Personal.

Este repositorio es la **fuente de verdad documental**: aquí viven el roadmap, el estado
del proyecto, las tareas, las decisiones arquitectónicas y (más adelante) la definición
de la infraestructura local y cloud.

---

## 1. Propósito del repositorio

| Sí pertenece aquí | No pertenece aquí |
| --- | --- |
| Roadmap, etapas y tareas | Código React / TypeScript del sitio |
| Estado del proyecto (`STATUS.md`) | Código FastAPI / Python del API |
| Flujo de trabajo y Definition of Done | Migraciones de base de datos |
| ADR (decisiones arquitectónicas) | Componentes de UI |
| Diagramas y mapeo local → nube | Lógica de negocio del blog |
| Docker Compose del entorno local *(futuro)* | Tests unitarios de frontend/backend |
| Terraform de la nube *(futuro)* | Secretos, credenciales o `.env` reales |
| Runbooks de despliegue y recuperación *(futuro)* | Artefactos compilados |

Repositorios hermanos:

- `personal-blog-frontend` — React + TypeScript + Vite.
- `personal-blog-backend` — FastAPI + PostgreSQL.

---

## 2. Estado actual del proyecto

- **Etapa actual:** ETAPA 00 — Fundación y Gobierno.
- **Tarea actual:** `Task/001-Inicializar-Workspace-y-Roadmap` — *Lista para validación*.
- **Tareas aprobadas:** 0 de 41 (0 %).
- **Implementación:** **no ha comenzado**. No existe código de aplicación, ni
  Docker Compose, ni Terraform, ni recursos cloud creados.

Consulta siempre [`docs/project-management/STATUS.md`](docs/project-management/STATUS.md)
para el estado vigente.

---

## 3. Arquitectura local prevista

Estrategia **local-first**: todo debe funcionar y validarse en local antes de crear
cualquier cuenta o recurso en la nube (ver [ADR-001](docs/adr/ADR-001-local-first.md)).

| Componente | Tecnología prevista |
| --- | --- |
| Frontend | React + TypeScript + Vite |
| Backend | FastAPI (Python) |
| Base de datos | PostgreSQL en contenedor |
| Almacenamiento de objetos | MinIO (compatible con S3) |
| Entrada HTTP | Reverse proxy local |
| Orquestación | Docker Compose |
| Supervisión de contenedores | Portainer CE (**solo local**) |
| Integración continua | GitHub Actions |

### Uso de Portainer

Portainer CE se usa **exclusivamente en el entorno local**, como panel de supervisión
de Docker: ver contenedores, logs, healthchecks, volúmenes y redes durante el
desarrollo y la validación local.

**Portainer no se despliega en producción** y no forma parte de la arquitectura cloud.

---

## 4. Arquitectura cloud objetivo (bajo costo)

| Responsabilidad | Servicio previsto |
| --- | --- |
| Frontend | Cloudflare Pages |
| Entrada HTTP | Amazon API Gateway (HTTP API) |
| Backend | AWS Lambda ejecutando FastAPI |
| Archivos e imágenes | Amazon S3 |
| Base de datos | PostgreSQL administrado |
| Configuración | AWS SSM Parameter Store |
| Logs y métricas | Amazon CloudWatch (retención y uso limitados) |
| CI/CD | GitHub Actions |
| Infraestructura como código | Terraform |

Detalle y justificación: [ADR-003](docs/adr/ADR-003-serverless-low-cost-cloud.md) y
[docs/architecture/local-to-cloud-mapping.md](docs/architecture/local-to-cloud-mapping.md).

### Servicios que NO usaremos inicialmente

- Amazon EC2
- Amazon ECR
- Amazon ECS Fargate
- Amazon EKS
- Application Load Balancer
- NAT Gateway
- Portainer en producción

Motivo: costo fijo mensual y complejidad operativa desproporcionados para un blog
personal de bajo tráfico.

---

## 5. Dónde está el roadmap

```
docs/
├── project-management/
│   ├── ROADMAP.md               ← etapas, tareas, dependencias y avance
│   ├── STATUS.md                ← estado vigente (fuente rápida de consulta)
│   ├── WORKFLOW.md              ← proceso de trabajo y cierre de tareas
│   ├── TASK_TEMPLATE.md         ← plantilla reutilizable de tarea
│   └── DEFINITION_OF_DONE.md    ← criterios de "terminado"
├── stages/                      ← una ficha por etapa (STAGE-00 … STAGE-12)
├── tasks/                       ← ficha detallada de cada tarea ejecutada
├── architecture/                ← visión general y mapeo local → nube
├── adr/                         ← decisiones arquitectónicas
└── task-reports/                ← reportes finales de ejecución
```

---

## 6. Cómo consultar las tareas pendientes

1. Abre [`docs/project-management/STATUS.md`](docs/project-management/STATUS.md):
   contiene la tabla completa de las 41 tareas con su estado.
2. Filtra por estado `Pendiente`.
3. Verifica las dependencias de la tarea en
   [`docs/project-management/ROADMAP.md`](docs/project-management/ROADMAP.md).
4. Lee la ficha de la etapa correspondiente en [`docs/stages/`](docs/stages/).

Estados oficiales: `Pendiente`, `En progreso`, `Lista para validación`, `Aprobada`,
`Bloqueada`, `Descartada`.

> Una tarea **solo puede quedar `Aprobada` cuando el usuario lo autoriza explícitamente**.

---

## 7. Estrategia de ramas

- `main` — versión estable o liberable.
- `dev` — integración de tareas aprobadas.
- `Task/<numero>-<nombre>` — trabajo aislado de una tarea, creado desde `dev`.

Estado actual de las ramas: ver
[`docs/tasks/TASK-001-initial-workspace-and-roadmap.md`](docs/tasks/TASK-001-initial-workspace-and-roadmap.md),
sección *Estado de ramas*. En este momento el repositorio **no tiene commits**, por lo
que `dev` y la rama `Task/001` todavía no pueden existir como referencias Git.

---

## 8. Contribución

Ver [CONTRIBUTING.md](CONTRIBUTING.md).
