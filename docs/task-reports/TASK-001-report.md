# Reporte — TASK-001 Inicializar Workspace y Roadmap

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/001-Inicializar-Workspace-y-Roadmap` |
| **Etapa** | ETAPA 00 — Fundación y Gobierno |
| **Estado final** | **Lista para validación** |
| **Fecha** | 2026-07-26 |
| **Repositorios afectados** | los tres |
| **Ficha completa** | [TASK-001](../tasks/TASK-001-initial-workspace-and-roadmap.md) |

---

## 1. Estado encontrado inicialmente

Los tres directorios presentaban un estado idéntico:

| Repositorio | ¿Repo Git? | Rama | Commits | Remoto `origin` | Archivos previos | Cambios locales |
| --- | --- | --- | --- | --- | --- | --- |
| `personal-blog-backend` | Sí | `main` (no nacida) | 0 | `github.com/jeffersondavila/personal-blog-backend.git` | Ninguno | Ninguno |
| `personal-blog-frontend` | Sí | `main` (no nacida) | 0 | `github.com/jeffersondavila/personal-blog-frontend.git` | Ninguno | Ninguno |
| `personal-blog-infra` | Sí | `main` (no nacida) | 0 | `github.com/jeffersondavila/personal-blog-infra.git` | Ninguno | Ninguno |

- Ninguna carpeta necesitó `git init`: las tres ya eran repositorios independientes.
- Los remotos ya existían y **se conservaron sin tocar** sus URL ni sus credenciales.
- Los tres directorios estaban **vacíos** salvo por `.git`: no había archivo alguno que
  conservar, y por tanto **no se eliminó ni sobrescribió nada**.
- `origin/main` figuraba como `[gone]`, lo cual es normal con un remoto vacío o sin
  `fetch` previo. No indica pérdida de datos.

## 2. Rama activa en cada repositorio

| Repositorio | Antes | Después |
| --- | --- | --- |
| `personal-blog-backend` | `main` (sin commits) | `main` (sin commits) — **sin cambios** |
| `personal-blog-frontend` | `main` (sin commits) | `main` (sin commits) — **sin cambios** |
| `personal-blog-infra` | `main` (sin commits) | `main` (sin commits) — **sin cambios** |

**No se creó ninguna rama.** Motivo y solución en la sección 7.

## 3. Archivos creados y modificados

**38 archivos creados. 0 modificados. 0 eliminados.**

### `personal-blog-infra` — 30 archivos

```
README.md
CONTRIBUTING.md
.gitignore
.editorconfig
docs/project-management/ROADMAP.md
docs/project-management/STATUS.md
docs/project-management/WORKFLOW.md
docs/project-management/TASK_TEMPLATE.md
docs/project-management/DEFINITION_OF_DONE.md
docs/stages/STAGE-00-foundation.md
docs/stages/STAGE-01-local-infrastructure.md
docs/stages/STAGE-02-application-foundations.md
docs/stages/STAGE-03-domain-and-backend.md
docs/stages/STAGE-04-user-experience.md
docs/stages/STAGE-05-quality-security.md
docs/stages/STAGE-06-continuous-integration.md
docs/stages/STAGE-07-local-validation.md
docs/stages/STAGE-08-cloud-ready.md
docs/stages/STAGE-09-cloud-accounts.md
docs/stages/STAGE-10-cloud-deployment.md
docs/stages/STAGE-11-deployment-automation.md
docs/stages/STAGE-12-launch-and-operations.md
docs/tasks/TASK-001-initial-workspace-and-roadmap.md
docs/architecture/overview.md
docs/architecture/local-to-cloud-mapping.md
docs/adr/ADR-001-local-first.md
docs/adr/ADR-002-three-repositories.md
docs/adr/ADR-003-serverless-low-cost-cloud.md
docs/task-reports/README.md
docs/task-reports/TASK-001-report.md
```

### `personal-blog-backend` — 4 archivos

```
README.md
CONTRIBUTING.md
.gitignore
.editorconfig
```

### `personal-blog-frontend` — 4 archivos

```
README.md
CONTRIBUTING.md
.gitignore
.editorconfig
```

## 4. Estructura documental

`personal-blog-infra` es la **única fuente de verdad** de la planificación:

| Carpeta | Qué contiene | Archivos |
| --- | --- | --- |
| `docs/project-management/` | Roadmap, estado, proceso, plantilla y definición de terminado. | 5 |
| `docs/stages/` | Una ficha por etapa: objetivo, tareas, criterios de salida, riesgos. | 13 |
| `docs/tasks/` | Ficha viva de cada tarea ejecutada. | 1 |
| `docs/architecture/` | Visión general y correspondencia local → nube. | 2 |
| `docs/adr/` | Decisiones arquitectónicas con contexto, consecuencias y alternativas. | 3 |
| `docs/task-reports/` | Guía de reportes y reporte final por tarea. | 2 |

Los README de frontend y backend **referencian** esta documentación mediante rutas
relativas; **no la duplican**.

## 5. Estado actual del roadmap

- **13 etapas** (00 → 12) y **41 tareas** registradas.
- **Avance global: 0 %** — 0 de 41 tareas aprobadas.

| Estado | Tareas |
| --- | --- |
| `Lista para validación` | 1 — `Task/001` |
| `Pendiente` | 40 — desde `Task/002` hasta `Task/041` |
| `En progreso` | 0 |
| `Aprobada` | **0** |
| `Bloqueada` | 0 |
| `Descartada` | 0 |

| Campo | Valor |
| --- | --- |
| Etapa actual | ETAPA 00 — Fundación y Gobierno |
| Tarea actual | `Task/001-Inicializar-Workspace-y-Roadmap` |
| Última tarea aprobada | Ninguna |
| Próxima tarea prevista | `Task/002-Definir-MVP-y-Arquitectura` |
| Bloqueos activos | 0 |
| Riesgos abiertos | 5 (R-01 a R-05) |

## 6. Validaciones ejecutadas y resultados

| # | Validación | Resultado |
| --- | --- | --- |
| 1 | **Listado recursivo de archivos creados** | 38 archivos (30 infra, 4 backend, 4 frontend). Ningún archivo fuera del workspace. |
| 2 | **`git status` en cada repositorio** | Los tres: `## No commits yet on main...origin/main [gone]` y solo entradas sin seguimiento (`??`). Ninguna entrada de eliminación o modificación. |
| 3 | **`git branch --show-current`** | `main` en los tres. Sin cambios respecto al estado inicial. |
| 4 | **`git remote -v`** | `origin` intacto en los tres, apuntando a los repositorios de GitHub originales. Ninguna URL ni credencial modificada. |
| 5 | **Enlaces relativos de documentación** | 116 enlaces relativos verificados contra el sistema de archivos. **0 rotos.** |
| 6 | **Búsqueda de posibles secretos** | Patrones buscados: `AKIA…`, `ASIA…`, `aws_access_key_id`, `aws_secret_access_key`, `BEGIN … PRIVATE KEY`, `ghp_…`, `github_pat_…`, `xox[baprs]-`, `sk-…` y asignaciones del tipo `password/secret/token/api_key = <valor>`. **0 coincidencias.** |
| 7 | **Ausencia de código funcional** | Patrones buscados: `import React`, `from 'react'`, `FastAPI(`, `APIRouter`, `@app.get`, `@app.post`, `services:`, `resource "aws_`, `provider "aws"`, `CREATE TABLE`, `package.json`. **0 coincidencias en código.** Las 2 únicas coincidencias son menciones en prosa: `package.json` en el README de frontend (declarando que **no** existe) y `docker-compose` en `CONTRIBUTING.md` de infra (describiendo alcance futuro). |
| 8 | **Duplicación innecesaria de documentos** | El roadmap, el estado y los ADR existen **solo** en `personal-blog-infra`. Frontend y backend enlazan a ellos. Sin duplicación. |

Ningún comando destructivo fue ejecutado.

## 7. Riesgos y decisiones pendientes

### Decisión pendiente que requiere al usuario

**Cómo hacer nacer las ramas.** Los tres repositorios tienen `main` como rama **no
nacida** (0 commits). Git no permite crear `dev` ni `Task/001-...` sin un commit de
partida, y solo admite una rama no nacida a la vez. Conforme a las reglas de la tarea, no
se improvisó ningún commit ni se creó ninguna rama.

Se proponen dos secuencias de arranque, a ejecutar **durante la aprobación**:

| Opción | Cómo | Consecuencia |
| --- | --- | --- |
| **A (recomendada)** | Commit inicial vacío en `main` → `dev` desde `main` → `Task/001` desde `dev` → confirmar el trabajo en la rama de la tarea. | `main` nace limpia y la integración hacia ella conserva la puerta del pull request. Cuesta un commit vacío. |
| **B** | `git switch --orphan Task/001-...` → confirmar el trabajo allí → crear `dev` y `main` desde ese commit. | Sin commit vacío, pero `main` incorpora el contenido de la tarea sin pasar por pull request. |

Comandos completos en la
[ficha de la tarea, sección 7](../tasks/TASK-001-initial-workspace-and-roadmap.md).

### Riesgos abiertos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-01 | Las ramas `dev` y `Task/*` no pueden existir sin commit inicial. | Medio | Secuencia de arranque acordada en la aprobación. |
| R-02 | Costo cloud imprevisto en la Etapa 10. | Alto | Presupuestos y alarmas obligatorios en `Task/027`, antes del primer recurso. |
| R-03 | PostgreSQL administrado condiciona las conexiones desde Lambda. | Medio | Evaluación en `Task/029`; patrón de conexión previsto desde `Task/005`. |
| R-04 | El roadmap puede desactualizarse si cambia el alcance. | Bajo | Actualización de `STATUS.md` y `ROADMAP.md` como parte de la Definition of Done. |
| R-05 | Los enlaces entre repositorios asumen carpetas hermanas. | Bajo | Suposición documentada en ambos README. |

### Decisiones diferidas por diseño

- Alcance exacto del MVP y contratos de API → `Task/002`.
- Backend de estado de Terraform → `Task/025`.
- Proveedor de PostgreSQL administrado → `Task/029`.
- Mecanismo de autenticación (cookie de sesión o token) → `Task/011`.

## 8. Instrucciones de validación para el usuario

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal

# a) Confirmar que no hay commits y que los remotos siguen intactos
foreach ($r in @('personal-blog-backend','personal-blog-frontend','personal-blog-infra')) {
  Write-Output "=== $r ==="
  git -C $r status --porcelain -b
  git -C $r branch --show-current
  git -C $r remote -v
  git -C $r rev-list --all --count   # debe imprimir 0
}

# b) Listar los 38 archivos creados
Get-ChildItem -Recurse -File . | Where-Object { $_.FullName -notmatch '\\\.git\\' } |
  ForEach-Object { $_.FullName.Replace((Get-Location).Path + '\','') }

# c) Comprobar que no hay código de aplicación
Get-ChildItem -Recurse -File . -Include *.py,*.ts,*.tsx,*.jsx,*.tf,package.json,docker-compose*.yml |
  Where-Object { $_.FullName -notmatch '\\\.git\\' }   # no debe devolver nada
```

Orden de lectura sugerido:

1. `personal-blog-infra/docs/project-management/STATUS.md`
2. `personal-blog-infra/docs/project-management/ROADMAP.md`
3. `personal-blog-infra/docs/project-management/WORKFLOW.md`
4. `personal-blog-infra/docs/adr/ADR-001-local-first.md`, `ADR-002`, `ADR-003`
5. `personal-blog-infra/docs/architecture/local-to-cloud-mapping.md`
6. Los tres `README.md`
7. [Sección 7 de la ficha](../tasks/TASK-001-initial-workspace-and-roadmap.md) — para
   elegir entre la opción A y la B de arranque de ramas.

## 9. Próxima tarea propuesta

**`Task/002-Definir-MVP-y-Arquitectura`** — definir requerimientos funcionales,
arquitectura de software, contratos generales y límites del MVP.

No se inicia hasta que `Task/001` sea aprobada.

## 10. Confirmación de límites respetados

Durante la ejecución de esta tarea:

- ❌ **No se hizo ningún commit.** Los tres repositorios siguen con 0 commits.
- ❌ **No se hizo ningún merge.**
- ❌ **No se hizo ningún push.**
- ❌ **No se creó ningún pull request.**
- ❌ **No se creó ninguna rama.**
- ❌ **No se creó ni modificó ningún remoto.**
- ❌ **No se creó ningún recurso cloud** ni ninguna cuenta en AWS, Cloudflare, GitHub ni
  ningún otro proveedor.
- ❌ **No se implementó** React, FastAPI, PostgreSQL, MinIO, Portainer, Docker Compose,
  Terraform, GitHub Actions, autenticación, APIs ni modelos de base de datos.
- ❌ **No se eliminó ni sobrescribió** contenido preexistente.
- ❌ **No se agregó ningún secreto.**
- ❌ **No se avanzó a `Task/002`.**
- ❌ **Ninguna tarea quedó `Aprobada`.**
- ✅ Todo el trabajo se realizó dentro de `C:\Users\jeffe\Downloads\Blog_Personal`.
- ✅ `Task/001` queda **Lista para validación**, a la espera de
  `approved: Task/001-Inicializar-Workspace-y-Roadmap`.
