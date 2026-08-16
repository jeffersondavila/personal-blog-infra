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
| Docker Compose del entorno local | Tests unitarios de frontend/backend |
| Terraform de la nube *(futuro)* | Secretos, credenciales o `.env` reales |
| Runbooks de despliegue y recuperación *(futuro)* | Artefactos compilados |

Repositorios hermanos:

- `personal-blog-frontend` — React + TypeScript + Vite.
- `personal-blog-backend` — FastAPI + PostgreSQL.

---

## 2. Estado actual del proyecto

- **ETAPA 00 — Fundación y Gobierno: completada** (2 de 2 tareas aprobadas).
- **ETAPA 01 — Infraestructura Local: completada** (2 de 2 tareas aprobadas).
- **Etapa siguiente:** ETAPA 02 — Fundaciones de las Aplicaciones.
- **Última tarea aprobada:** `Task/004-Backups-y-Recuperacion-Local` (2026-07-31). Su PR
  `Task/004 → main` queda pendiente de revisión y fusión del usuario.
- **Próxima tarea:** `Task/005-Fundacion-Backend-FastAPI` — *Pendiente, no iniciada*.
  Será el **primer código de aplicación** del proyecto.
- **Tareas aprobadas:** 4 de 41 (10 %).

Estado de la implementación:

| Área | Estado |
| --- | --- |
| **Infraestructura local** | **Completa y respaldada.** `docker-compose.yml` con PostgreSQL, MinIO y Portainer CE (`Task/003`), más respaldo y recuperación verificados (`Task/004`). |
| **Backend** (FastAPI) | **No ha comenzado.** Sin código de aplicación. Empieza en `Task/005`. |
| **Frontend** (React) | **No ha comenzado.** Sin código de aplicación. Empieza en `Task/006`. |
| **Terraform e infraestructura cloud** | **No existen.** Sin archivos `.tf`. Empieza en `Task/025`. |
| **Recursos cloud y cuentas** | **Ninguno creado.** Etapas 09 y 10. |

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
| Entrada HTTP | Traefik v3 como reverse proxy local (`Task/007`) |
| Orquestación | Docker Compose |
| Supervisión de contenedores | Portainer CE (**solo local**) |
| Integración continua | GitHub Actions |

### Uso de Portainer

Portainer CE se usa **exclusivamente en el entorno local**, como panel de supervisión
de Docker: ver contenedores, logs, healthchecks, volúmenes y redes durante el
desarrollo y la validación local.

**Portainer no se despliega en producción** y no forma parte de la arquitectura cloud.

> **Advertencia de privilegio.** Portainer accede al socket del daemon de Docker y
> conserva **capacidad administrativa sobre el host**: puede administrar contenedores,
> redes y volúmenes de este y de cualquier otro proyecto de la máquina. El montaje `:ro`
> del socket protege el **archivo**, pero **no** convierte la Docker API en solo lectura,
> y la separación de redes tampoco limita esas acciones. El riesgo se acepta únicamente
> porque es local, se publica en `127.0.0.1` y exige autenticación propia.
> **No lo expongas a la red local ni a internet.** Detalle:
> [runbook §2.1](docs/runbooks/local-environment.md).

### Levantar el entorno local

Entregado por `Task/003`, **aprobado** el 2026-07-29:

```powershell
Copy-Item .env.example .env     # solo la primera vez
docker compose up -d
docker compose ps
```

| Servicio | Acceso local |
| --- | --- |
| PostgreSQL | `127.0.0.1:55432` |
| MinIO — API S3 | `http://127.0.0.1:9000` |
| MinIO — consola | `http://127.0.0.1:9001` |
| Portainer | `https://127.0.0.1:9444` |

Todos los puertos se publican **solo en la interfaz de loopback**. Operación completa,
verificación y diagnóstico: [docs/runbooks/local-environment.md](docs/runbooks/local-environment.md).

### Respaldo del entorno local

Entregado por `Task/004`, **aprobado** el 2026-07-31:

```powershell
cd scripts\backup
.\New-LocalBackup.ps1              # crear el backup
.\Test-LocalBackup.ps1             # verificar su integridad
.\Restore-LocalBackupTest.ps1      # probar la restauracion en aislamiento
```

Respalda PostgreSQL, MinIO y Portainer a archivos **externos a los volúmenes de Docker**,
con manifiesto y checksums SHA-256 por ejecución. En MinIO cubre el **contenido, los
metadatos y los tags** de la versión actual de cada objeto; el historial de versiones
queda fuera del alcance y el script lo detecta en lugar de ignorarlo. Procedimiento
completo y recuperación paso a paso:
[docs/runbooks/local-backup-and-recovery.md](docs/runbooks/local-backup-and-recovery.md) ·
Referencia de los scripts: [scripts/backup/](scripts/backup/README.md).

> **`docker compose down -v` destruye la base de datos y los objetos.** Haz un backup
> antes. Los conjuntos se guardan en `local-backups/`, que está **ignorado por Git** y
> contiene información sensible: no los versiones ni los compartas.

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

La arquitectura objetivo está representada en el diagrama versionado
[`images/Infraestructura.png`](images/Infraestructura.png).

### AWS Local Parity — laboratorio local de infraestructura

Antes de crear un solo recurso real, la infraestructura se desarrolla, se aprende, se
provisiona y se destruye **localmente**: la misma definición de Terraform se aplica contra
un emulador AWS local, sin cuenta y sin costo. **No sustituye** al entorno local de
desarrollo (Docker Compose, PostgreSQL, MinIO, Portainer) y **AWS real sigue siendo la
autoridad final**.

Estrategia completa:
[`docs/architecture/aws-local-parity.md`](docs/architecture/aws-local-parity.md) ·
[ADR-006](docs/adr/ADR-006-local-aws-parity-with-floci.md) — **Aceptada** (2026-08-15).

La estrategia está aprobada; **la implementación llega en `Task/025`**.

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

## 4.1 Alcance del producto

El alcance del MVP, los flujos de usuario y el modelo de contenido están definidos en
[`docs/product/`](docs/product/):

- [MVP_SCOPE.md](docs/product/MVP_SCOPE.md) — qué construimos y qué queda fuera.
- [USER_FLOWS.md](docs/product/USER_FLOWS.md) — flujos públicos y administrativos.
- [CONTENT_MODEL.md](docs/product/CONTENT_MODEL.md) — tipos de contenido (conceptual).

La arquitectura de software está en
[`docs/architecture/software-architecture.md`](docs/architecture/software-architecture.md)
y las convenciones de API en
[`docs/architecture/api-contracts.md`](docs/architecture/api-contracts.md).

---

## 5. Dónde está el roadmap

```
docker-compose.yml                     ← entorno local: PostgreSQL, MinIO, Portainer
.env.example                           ← variables del entorno local (valores ficticios)
scripts/
└── backup/                            ← respaldo, verificación y restauración local
docs/
├── runbooks/
│   ├── local-environment.md           ← arranque, parada, verificación, diagnóstico
│   └── local-backup-and-recovery.md   ← respaldo y recuperación
├── project-management/
│   ├── ROADMAP.md                     ← etapas, tareas, dependencias y avance
│   ├── STATUS.md                      ← estado vigente (fuente rápida de consulta)
│   ├── WORKFLOW.md                    ← proceso de trabajo y cierre de tareas
│   ├── TASK_TEMPLATE.md               ← plantilla reutilizable de tarea
│   └── DEFINITION_OF_DONE.md          ← criterios de "terminado"
├── product/
│   ├── MVP_SCOPE.md                   ← qué construimos y qué no
│   ├── USER_FLOWS.md                  ← flujos públicos y administrativos
│   └── CONTENT_MODEL.md               ← tipos de contenido (conceptual)
├── stages/                            ← una ficha por etapa (STAGE-00 … STAGE-12)
├── tasks/                             ← ficha detallada de cada tarea ejecutada
├── architecture/
│   ├── overview.md                    ← visión de conjunto
│   ├── software-architecture.md       ← organización de backend y frontend
│   ├── api-contracts.md               ← convenciones de API
│   ├── non-functional-requirements.md ← 57 requisitos: seguridad, rendimiento, SEO…
│   ├── security-boundaries.md         ← qué puede hablar con qué
│   ├── open-decisions.md              ← decisiones diferidas
│   ├── local-to-cloud-mapping.md      ← correspondencia local → nube
│   └── aws-local-parity.md            ← estrategia de IaC local (AWS Local Parity)
├── adr/                               ← decisiones arquitectónicas
└── task-reports/                      ← reportes finales de ejecución
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

`main` y `dev` existen y están publicadas en los tres repositorios. En
`personal-blog-infra`, `dev` contiene además `Task/004` mientras su pull request hacia
`main` espera la decisión del usuario. Estado vigente de las ramas en
[`docs/project-management/STATUS.md`](docs/project-management/STATUS.md), sección
*Estado de los repositorios*.

---

## 8. Contribución

Ver [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Instrucciones para Claude Code

- [Guía de configuración y restauración](docs/claude/README.md)
- [Instrucciones versionadas del proyecto](docs/claude/PROJECT_INSTRUCTIONS.md)

El workspace utiliza un `CLAUDE.md` raíz no versionado que importa las
instrucciones persistentes y versionadas de este repositorio.
