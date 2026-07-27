# TASK-001 — Inicializar Workspace y Roadmap

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/001-Inicializar-Workspace-y-Roadmap` |
| **Nombre** | Inicializar Workspace y Roadmap |
| **Etapa** | ETAPA 00 — Fundación y Gobierno |
| **Estado** | **Aprobada** |
| **Repositorios involucrados** | `personal-blog-infra`, `personal-blog-frontend`, `personal-blog-backend` |
| **Dependencias** | Ninguna |
| **Rama** | `Task/001-Inicializar-Workspace-y-Roadmap` (creada desde `dev` — ver sección 7) |
| **Fecha de inicio** | 2026-07-26 |
| **Fecha de aprobación** | 2026-07-26 |
| **Aprobado por** | jeffersondavila |
| **Última actualización** | 2026-07-26 |

---

## 1. Objetivo

Preparar los tres repositorios, establecer las reglas de trabajo y crear un sistema
documental que permita conocer en todo momento qué etapas existen, qué tareas contiene
cada una, cuáles están pendientes, cuál está en ejecución, cuáles esperan validación,
cuáles fueron aprobadas, qué bloqueos hay, qué decisiones arquitectónicas se tomaron y
qué evidencia respalda cada validación.

## 2. Contexto

Primera tarea del proyecto. Sin gobierno explícito, un proyecto de 41 tareas repartidas
en 3 repositorios y 2 entornos deriva en alcance difuso y trabajo perdido. Esta tarea fija
dónde vive la verdad documental, cómo se nombran las ramas, qué significa "terminado" y
quién aprueba.

No implementa ninguna funcionalidad del blog ni levanta servicio alguno.

---

## 3. Estado inicial encontrado

Inspección realizada el 2026-07-26 sobre `C:\Users\jeffe\Downloads\Blog_Personal`.

### 3.1 Resumen

| Repositorio | ¿Es repo Git? | Rama activa | Commits | Remoto | Cambios locales | Archivos previos |
| --- | --- | --- | --- | --- | --- | --- |
| `personal-blog-backend` | Sí | `main` (no nacida) | 0 | `origin` → GitHub | Ninguno | Ninguno |
| `personal-blog-frontend` | Sí | `main` (no nacida) | 0 | `origin` → GitHub | Ninguno | Ninguno |
| `personal-blog-infra` | Sí | `main` (no nacida) | 0 | `origin` → GitHub | Ninguno | Ninguno |

### 3.2 Detalle por repositorio

Los tres presentaban exactamente el mismo estado:

```
git status --porcelain -b   →  ## No commits yet on main...origin/main [gone]
git branch --show-current   →  main
git branch -a               →  (vacío: no existe ninguna referencia de rama)
git log --oneline           →  (vacío)
git rev-list --all --count  →  0
```

Remotos encontrados y **conservados sin modificación**:

| Repositorio | `origin` |
| --- | --- |
| `personal-blog-backend` | `https://github.com/jeffersondavila/personal-blog-backend.git` |
| `personal-blog-frontend` | `https://github.com/jeffersondavila/personal-blog-frontend.git` |
| `personal-blog-infra` | `https://github.com/jeffersondavila/personal-blog-infra.git` |

Cada repositorio tenía además configurado el seguimiento `branch.main.remote=origin` y
`branch.main.merge=refs/heads/main`. La marca `[gone]` indica únicamente que `origin/main`
no existe todavía en el remoto o no ha sido traído localmente; **no** implica pérdida de
información.

### 3.3 Archivos que debían conservarse

**Ninguno.** Los tres directorios estaban vacíos salvo por su carpeta `.git`. Por tanto:

- No se eliminó ningún archivo.
- No se sobrescribió ningún archivo.
- Todos los archivos listados en la sección 6 son **nuevos**.

### 3.4 Conclusión de la inspección

Ninguna carpeta necesitó `git init`: las tres ya eran repositorios Git independientes con
su remoto configurado. Se conservaron tal cual.

---

## 4. Dentro del alcance

- [x] Inspeccionar los tres repositorios (Git, rama, historial, archivos, remotos, cambios).
- [x] Documentar la estrategia de ramas y determinar cómo prepararlas de forma segura.
- [x] Crear el sistema documental completo en `personal-blog-infra`.
- [x] Registrar el roadmap con 13 etapas y 41 tareas.
- [x] Crear `STATUS.md` con el estado vigente y la tabla completa de tareas.
- [x] Crear `WORKFLOW.md` con el proceso y el protocolo de aprobación.
- [x] Crear `TASK_TEMPLATE.md` reutilizable.
- [x] Crear `DEFINITION_OF_DONE.md`.
- [x] Crear las 13 fichas de etapa.
- [x] Crear los 3 ADR fundacionales.
- [x] Crear la visión general de arquitectura y el mapeo local → nube.
- [x] Crear `README.md`, `.gitignore`, `.editorconfig` y `CONTRIBUTING.md` en los tres repositorios.
- [x] Crear esta ficha y el reporte final de la tarea.
- [x] Ejecutar y registrar las validaciones.

## 5. Fuera del alcance

| Elemento | Dónde corresponde |
| --- | --- |
| Requerimientos funcionales y contratos de API | `Task/002` |
| Docker Compose, PostgreSQL, MinIO, Portainer | `Task/003` |
| Código FastAPI | `Task/005` |
| Código React | `Task/006` |
| Modelos de base de datos y migraciones | `Task/008` |
| Autenticación | `Task/011` |
| GitHub Actions | Etapa 06 |
| Terraform | `Task/025` |
| Cuentas y recursos cloud | Etapas 09 y 10 |

Además, **fuera de alcance por regla explícita de la tarea**: commits, merges, pull
requests, pushes, creación de remotos y avanzar a `Task/002`.

---

## 6. Entregables

### `personal-blog-infra` (30 archivos, todos nuevos)

| Entregable | Ruta |
| --- | --- |
| README del repositorio | `README.md` |
| Reglas de contribución | `CONTRIBUTING.md` |
| Exclusiones de Git | `.gitignore` |
| Estilo de edición | `.editorconfig` |
| Roadmap | `docs/project-management/ROADMAP.md` |
| Estado del proyecto | `docs/project-management/STATUS.md` |
| Proceso de trabajo | `docs/project-management/WORKFLOW.md` |
| Plantilla de tarea | `docs/project-management/TASK_TEMPLATE.md` |
| Definición de terminado | `docs/project-management/DEFINITION_OF_DONE.md` |
| Fichas de etapa (13) | `docs/stages/STAGE-00-foundation.md` … `docs/stages/STAGE-12-launch-and-operations.md` |
| Ficha de esta tarea | `docs/tasks/TASK-001-initial-workspace-and-roadmap.md` |
| Visión general de arquitectura | `docs/architecture/overview.md` |
| Mapeo local → nube | `docs/architecture/local-to-cloud-mapping.md` |
| ADR local-first | `docs/adr/ADR-001-local-first.md` |
| ADR tres repositorios | `docs/adr/ADR-002-three-repositories.md` |
| ADR nube serverless de bajo costo | `docs/adr/ADR-003-serverless-low-cost-cloud.md` |
| Guía de reportes | `docs/task-reports/README.md` |
| Reporte de esta tarea | `docs/task-reports/TASK-001-report.md` |

### `personal-blog-backend` (4 archivos, todos nuevos)

`README.md`, `CONTRIBUTING.md`, `.gitignore`, `.editorconfig`

### `personal-blog-frontend` (4 archivos, todos nuevos)

`README.md`, `CONTRIBUTING.md`, `.gitignore`, `.editorconfig`

---

## 7. Estado de ramas

> **Resuelto el 2026-07-26 durante la aprobación.** El usuario eligió la **opción A**.
> Las tres ramas existen ya en los tres repositorios. El detalle histórico se conserva
> abajo porque explica por qué el arranque requirió un paso explícito.

### 7.0 Resultado final

En cada uno de los tres repositorios:

| Rama | Estado final |
| --- | --- |
| `main` | Contiene el trabajo de `Task/001`, integrado mediante pull request aceptado por el usuario. Publicada. |
| `dev` | Trabajo de `Task/001` integrado con merge `--no-ff`. Publicada. |
| `Task/001-Inicializar-Workspace-y-Roadmap` | **Eliminada** local y remotamente tras integrarse. |

> **Publicación completada.** El push y el pull request quedaron temporalmente bloqueados
> por falta de credenciales de GitHub en el entorno (bloqueo **B-01**). El usuario instaló
> y autenticó GitHub CLI, completó los push y aceptó los pull requests (`#1` en cada
> repositorio). **B-01 cerrado.**

### 7.1 Situación técnica encontrada (histórico)

La estrategia prevista es `main` → `dev` → `Task/<numero>-<nombre>`. **No fue posible
prepararla durante la ejecución de la tarea**, por una limitación de Git, no por una
decisión de diseño:

- En los tres repositorios, `main` es una **rama no nacida**: `HEAD` apunta a
  `refs/heads/main`, pero esa referencia no existe porque no hay ningún commit.
- Git no puede crear `dev` ni `Task/001-...` con `git branch` o `git switch -c`, porque
  ambas necesitan un commit de partida. El intento falla con
  *"not a valid object name: 'main'"*.
- Git solo admite **una** rama no nacida a la vez, la apuntada por `HEAD`.

Conforme a las reglas de la tarea (no improvisar commits, no hacer commit, merge ni push),
**no se creó ninguna rama ni ningún commit**. Los tres repositorios siguen en `main` sin
commits, exactamente como se encontraron.

### 7.2 Secuencia ejecutada durante la aprobación (opción A)

Al recibir `approved: Task/001-Inicializar-Workspace-y-Roadmap`, se ejecutó en **cada uno
de los tres repositorios** la siguiente secuencia. El primer comando es el paso de
arranque que no podía darse sin autorización: un **commit inicial vacío** que hace nacer
`main` sin introducir contenido de la tarea en la rama estable.

```bash
# 1. Hacer nacer `main` sin contenido de la tarea
git commit --allow-empty -m "chore: commit inicial del repositorio"

# 2. Crear `dev` desde `main`
git branch dev main

# 3. Crear la rama de la tarea desde `dev`
git switch -c Task/001-Inicializar-Workspace-y-Roadmap dev

# 4. Confirmar el trabajo de la tarea en su propia rama
git add -A
git commit -m "docs: inicializar workspace, roadmap y sistema documental

Task/001-Inicializar-Workspace-y-Roadmap"

# 5. Integrar en `dev`
git switch dev
git merge --no-ff Task/001-Inicializar-Workspace-y-Roadmap

# 6. Publicar (solo tras autorización)
git push -u origin dev
git push -u origin Task/001-Inicializar-Workspace-y-Roadmap

# 7. Pull request `dev` → `main` (NO se hace merge automático)
# 8. Volver a `main`, actualizar referencias y limpiar la rama local de la tarea
```

> **Nota histórica añadida en `Task/002.1`:** el paso 7 conserva el plan de
> cierre documentado entonces. El historial de Git confirma que los PR `#1`
> reales usaron `Task/001-Inicializar-Workspace-y-Roadmap` como head, no `dev`.
> Desde `Task/002.1`, el flujo oficial exige siempre `Task/<nombre> → main`.

Ventaja de esta secuencia: `main` nace limpia, el trabajo vive en la rama `Task/*` y la
integración hacia `main` conserva la puerta del pull request definida en
[WORKFLOW.md](../project-management/WORKFLOW.md).

La alternativa descartada era `git switch --orphan Task/001-...`, que evitaba el commit
vacío pero habría llevado el contenido de la tarea a `main` sin pasar por pull request.
El usuario optó por la **opción A**.

---

## 8. Criterios de aceptación

| # | Criterio | Estado |
| --- | --- | --- |
| 1 | Los tres repositorios inspeccionados. | Cumplido — sección 3 |
| 2 | No se eliminó contenido preexistente. | Cumplido — no existía contenido |
| 3 | Responsabilidades de cada repositorio documentadas. | Cumplido — README y ADR-002 |
| 4 | `personal-blog-infra` contiene el roadmap completo. | Cumplido |
| 5 | Todas las etapas y tareas registradas. | Cumplido — 13 etapas, 41 tareas |
| 6 | `STATUS.md` identifica etapa, tarea, avance, pendientes y próxima tarea. | Cumplido |
| 7 | Existe plantilla reutilizable de tarea. | Cumplido |
| 8 | Existe definición clara de terminado. | Cumplido |
| 9 | Existe documentación de la estrategia local-first. | Cumplido — ADR-001 |
| 10 | Existe documentación de la arquitectura serverless de bajo costo. | Cumplido — ADR-003 |
| 11 | Existe documentación de la correspondencia local-cloud. | Cumplido |
| 12 | Los README de los tres repositorios son coherentes. | Cumplido |
| 13 | No se implementó código funcional del blog. | Cumplido — verificado por búsqueda |
| 14 | No se creó ningún recurso cloud. | Cumplido |
| 15 | No se agregaron secretos. | Cumplido — verificado por búsqueda |
| 16 | `Task/001` quedó `Lista para validación` al terminar la ejecución, nunca marcada `Aprobada` de forma automática. | Cumplido — aprobada después por el usuario el 2026-07-26 |
| 17 | `Task/002` y posteriores quedan `Pendiente`. | Cumplido — 40 tareas `Pendiente` |

---

## 9. Validaciones realizadas

| # | Validación | Comando / método | Resultado |
| --- | --- | --- | --- |
| 1 | Listado recursivo de archivos creados | `Get-ChildItem -Recurse` excluyendo `.git` | 38 archivos: 30 en infra, 4 en backend, 4 en frontend |
| 2 | Estado de Git | `git status --porcelain -b` en los tres repos | Solo archivos sin seguimiento (`??`); 0 commits; ningún archivo eliminado ni modificado |
| 3 | Rama activa | `git branch --show-current` | `main` en los tres |
| 4 | Remotos | `git remote -v` | `origin` intacto en los tres, apuntando a GitHub |
| 5 | Enlaces relativos | Verificación de cada enlace Markdown contra el sistema de archivos | 116 enlaces relativos, 0 rotos |
| 6 | Búsqueda de secretos | Patrones `AKIA…`, `ASIA…`, `BEGIN … PRIVATE KEY`, `ghp_`, `github_pat_`, `xox…`, `sk-…`, `password/secret/token/api_key = valor` | 0 coincidencias |
| 7 | Ausencia de código funcional | Patrones `import React`, `from 'react'`, `FastAPI(`, `APIRouter`, `@app.get/post`, `services:`, `resource "aws_`, `provider "aws"`, `CREATE TABLE` | 0 coincidencias en código; solo 2 menciones en prosa (`package.json` en el README de frontend y `docker-compose` en `CONTRIBUTING.md` de infra) |
| 8 | Duplicación de documentos | Revisión manual de contenido entre repositorios | El roadmap existe solo en `personal-blog-infra`; frontend y backend lo referencian |

Detalle de resultados: [reporte de la tarea](../task-reports/TASK-001-report.md).

---

## 10. Problemas encontrados

| # | Problema | Resolución |
| --- | --- | --- |
| 1 | Los tres repositorios no tenían commit inicial, por lo que Git no permitía crear `dev` ni `Task/001`. | No se improvisó ningún commit durante la ejecución. Se documentó el estado y la secuencia requerida (sección 7). **Resuelto el 2026-07-26** durante la aprobación, con la opción A autorizada por el usuario. Riesgo R-01 cerrado. |
| 2 | `origin/main` figura como `[gone]` en los tres repositorios. | Es el comportamiento esperado cuando el remoto está vacío o no se ha hecho `fetch`. No se modificó ninguna configuración de remoto. Sin impacto. |
| 3 | Los enlaces cruzados entre repositorios (`../personal-blog-infra/...`) solo resuelven si los tres se clonan como carpetas hermanas. | Se documentó explícitamente esa suposición en los README de frontend y backend. |

---

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-01 | Sin commit inicial, el flujo de ramas no podía aplicarse. | Medio | **Cerrado el 2026-07-26.** Ejecutada la opción A: commit inicial vacío en `main`, `dev` desde `main` y `Task/001` desde `dev`, en los tres repositorios. |
| R-02 | Costo cloud imprevisto al llegar a la Etapa 10. | Alto | Presupuestos y alarmas obligatorios en `Task/027`, antes de cualquier despliegue. |
| R-03 | La elección de PostgreSQL administrado condiciona el diseño de conexiones desde Lambda. | Medio | Se evalúa en `Task/029`; el patrón de conexión se considera ya desde `Task/005`. |
| R-04 | El roadmap de 41 tareas puede quedar desactualizado si el alcance cambia. | Bajo | `STATUS.md` y `ROADMAP.md` se actualizan en cada cambio de estado, como parte de la Definition of Done. |
| R-05 | Los enlaces entre repositorios dependen de la disposición de carpetas hermanas. | Bajo | Suposición documentada; alternativa futura: enlazar a las URL de GitHub una vez publicados. |

---

## 12. Decisiones técnicas

| Decisión | Alternativas consideradas | Justificación | ADR |
| --- | --- | --- | --- |
| Estrategia local-first | Cloud-first; híbrido con base de datos administrada desde el inicio | Costo cero durante el desarrollo; iteración rápida; sin riesgo de factura mientras el alcance cambia | [ADR-001](../adr/ADR-001-local-first.md) |
| Tres repositorios separados | Monorepo; dos repositorios; cuatro o más | Responsabilidades explícitas, CI y despliegue independientes; los tres repositorios ya existían con sus remotos | [ADR-002](../adr/ADR-002-three-repositories.md) |
| Nube serverless de bajo costo | ECS Fargate + ALB; EC2; blog estático sin panel; PaaS | Escalado a cero; sin costo fijo salvo la base de datos; el panel administrativo es requisito | [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md) |
| `personal-blog-infra` como única fuente de verdad documental | Duplicar el roadmap en los tres repositorios | Evita divergencia; los otros dos repositorios referencian, no copian | ADR-002 |
| No crear ramas ni commits en esta tarea | Crear un commit inicial por iniciativa propia; usar `git switch --orphan` | Las reglas de la tarea prohíben commits e improvisación; el estado se documenta y se resuelve en la aprobación | — |

---

## 13. Documentación creada o actualizada

Todos los archivos de la sección 6 son **creados**. No se actualizó ningún documento
preexistente porque no existía ninguno.

---

## 14. Resultado de pruebas

No aplica en el sentido de suite automatizada: esta tarea es exclusivamente documental y
no introduce código compilable ni ejecutable. Las verificaciones realizadas son las ocho
validaciones de la sección 9, todas con resultado satisfactorio.

---

## 15. Pasos de validación para el usuario

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal

# 1. Confirmar que no se hizo ningún commit y que los remotos están intactos
foreach ($r in @('personal-blog-backend','personal-blog-frontend','personal-blog-infra')) {
  Write-Output "=== $r ==="
  git -C $r status --porcelain -b
  git -C $r branch --show-current
  git -C $r remote -v
  git -C $r rev-list --all --count   # debe imprimir 0
}

# 2. Ver los archivos creados
Get-ChildItem -Recurse -File . | Where-Object { $_.FullName -notmatch '\\\.git\\' } |
  ForEach-Object { $_.FullName.Replace((Get-Location).Path + '\','') }
```

Luego revisa, en este orden:

1. `personal-blog-infra/docs/project-management/STATUS.md` — estado vigente.
2. `personal-blog-infra/docs/project-management/ROADMAP.md` — las 13 etapas y 41 tareas.
3. `personal-blog-infra/docs/project-management/WORKFLOW.md` — proceso y aprobación.
4. `personal-blog-infra/docs/adr/` — las tres decisiones fundacionales.
5. `personal-blog-infra/docs/architecture/local-to-cloud-mapping.md` — correspondencia.
6. Los tres `README.md` — coherencia entre repositorios.
7. La sección 7 de esta ficha — decide qué secuencia de arranque de ramas prefieres.

---

## 16. Deuda técnica pendiente

- ~~Las ramas `dev` y `Task/001-...` no existen todavía (R-01).~~ **Resuelto el 2026-07-26.**
- Los enlaces entre repositorios son relativos a carpetas hermanas (R-05).
- Los criterios de salida de las fichas de etapa se irán marcando conforme avance el
  proyecto.

---

## 17. Próxima tarea

`Task/002-Definir-MVP-y-Arquitectura` — definir requerimientos funcionales, arquitectura
de software, contratos generales y límites del MVP.

**No se inicia hasta que `Task/001` sea aprobada.**

---

## 18. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** |
| **Fecha de aprobación** | 2026-07-26 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/001-Inicializar-Workspace-y-Roadmap` |
| **Opción de arranque de ramas elegida** | **A** — commit inicial vacío en `main` |

### Flujo de cierre ejecutado

En los tres repositorios:

| # | Paso | Resultado |
| --- | --- | --- |
| 1 | Commit inicial vacío en `main`. | Hecho |
| 2 | `dev` creada desde `main`. | Hecho |
| 3 | `Task/001-Inicializar-Workspace-y-Roadmap` creada desde `dev`. | Hecho |
| 4 | Trabajo documental confirmado en la rama de la tarea. | Hecho |
| 5 | Documentación de aprobación actualizada y confirmada. | Hecho |
| 6 | Rama de la tarea integrada en `dev` con merge `--no-ff`. | Hecho |
| 7 | Push de `main` y `dev` al remoto. | Hecho (tras cerrar B-01) |
| 8 | Publicación de la rama de la tarea. | Hecho (tras cerrar B-01) |
| 9 | Pull request hacia `main`, sin merge automático. | Hecho — `#1` en cada repositorio, **aceptado por el usuario** |
| 10 | Vuelta a `main`. | Hecho |
| 11 | Eliminación de la rama de la tarea. | Hecho, local y remotamente |

`Task/002-Definir-MVP-y-Arquitectura` **no fue iniciada durante esta tarea**; se inició
después por instrucción del usuario.

Resultado detallado: [reporte de la tarea](../task-reports/TASK-001-report.md).
