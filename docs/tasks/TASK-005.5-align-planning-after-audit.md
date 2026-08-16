# TASK-005.5 — Alinear la planificación tras la auditoría global

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/005.5-Alinear-Planificacion-Tras-Auditoria` |
| **Nombre** | Alinear planificación tras auditoría global |
| **Tipo** | **Mantenimiento** de gobierno, planificación y arquitectura documental |
| **Etapa** | Ninguna — **no cuenta dentro de las 41 tareas del roadmap** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de aprobación** | 2026-08-16 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.5-Alinear-Planificacion-Tras-Auditoria` |
| **Repositorios involucrados** | `personal-blog-infra`, `personal-blog-backend`, `personal-blog-frontend` |
| **Dependencias** | `Task/005.4` — **Aprobada** ✔, PR `#10` fusionado y normalizado |
| **Rama** | `Task/005.5-Alinear-Planificacion-Tras-Auditoria` (la misma en los tres repositorios) |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | infra `cc90b96` · backend `db6ab18` · frontend `144a401` |
| **Fecha de inicio** | 2026-08-16 |
| **Última actualización** | 2026-08-16 |

---

## 0. Preparación Git

| # | Comprobación | infra | backend | frontend |
| --- | --- | --- | --- | --- |
| 1 | `main == origin/main` | ✔ `cc90b96` | ✔ `db6ab18` | ✔ `144a401` |
| 2 | Working tree limpio antes de crear la rama | ✔ vacío | ✔ vacío | ✔ vacío |
| 3 | Rama creada **desde `main`** | ✔ | ✔ | ✔ |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | ✔ | ✔ | ✔ |

Verificado además que **no queda ninguna rama `Task/*` remota** tras el `--prune`: la de
`Task/005.4` desapareció al fusionarse el PR `#10`.

```powershell
git fetch --prune origin
git switch main
git pull --ff-only origin main
git status --porcelain          # vacio
git rev-parse main; git rev-parse origin/main

git switch -c Task/005.5-Alinear-Planificacion-Tras-Auditoria

git rev-parse HEAD; git rev-parse main          # coinciden
```

---

## 1. Contexto

Se realizaron **dos auditorías independientes** del proyecto. Ambas coincidieron en que la
arquitectura general es viable —Lambda + FastAPI + PgBouncer + PostgreSQL en VPS,
ADR-006/Floci como estrategia razonable, buen desacoplamiento del backend— y en que **no
hay que replantear la arquitectura**, pero señalaron inconsistencias de **planificación,
*ownership*, secuencia y documentación**.

> **Los reportes de auditoría no se trataron como autoridad automática.** Cada hallazgo
> siguió el ciclo: **reproducir la evidencia → entender la intención vigente → contrastar
> con la fuente canónica → decidir → corregir solo si se justifica → revalidar
> transversalmente**. Dos hallazgos **no se reprodujeron** y se registran como tales.

---

## 2. Dentro del alcance

- [x] Reproducir cada hallazgo contra el estado real de los repositorios.
- [x] Corregir **todas** las reglas operativas vigentes que ordenaban crear ramas Task
      desde `dev`.
- [x] Corregir el *drift* documental posterior a `Task/005.2`, `005.3` y `005.4`.
- [x] Corregir los textos que trataban `images/Infraestructura.png` como autoridad canónica
      vigente de producción, **sin tocar el archivo**.
- [x] Corregir dependencias invertidas de secuencia (`Task/025`, `Task/029`, `Task/021`,
      topología de dominios).
- [x] Asignar propietarios a las cadenas que no los tenían.
- [x] Revalidar las 41 tareas, las decisiones abiertas y los riesgos afectados.
- [x] Ficha y reporte de la tarea.

## 3. Fuera del alcance

| Fuera del alcance | Dónde corresponde |
| --- | --- |
| Instalar frontend o backend; cualquier código funcional | `Task/006`, ETAPA 03 |
| Implementar `ObjectStorage` o `S3Storage` | `Task/010` |
| Crear bucket, IAM, Terraform o recursos cloud | `Task/025`, `Task/030`+ |
| Contratar VPS, instalar PgBouncer, obtener TLS | `Task/029` |
| Ejecutar Floci | `Task/025` |
| Crear GitHub Actions o modificar Docker Compose | ETAPA 06, `Task/007` |
| Implementar SEO o desplegar en AWS/Cloudflare | `Task/016`, ETAPA 10 |
| **Iniciar `Task/006`** | Tras la aprobación y cierre de esta tarea |
| Resolver **D-15** y **D-16** | `Task/011` y `Task/029` |
| Cambiar la estrategia de *rendering* del frontend | Solo con evidencia, en `Task/016`, con ADR propio |

**Ningún ADR nuevo.** No apareció ninguna decisión arquitectónica independiente: se
corrigieron *ownership* y secuencia, no arquitectura. Fabricar un ADR-008 habría sido
ruido.

---

## 4. Hallazgos y veredictos

Matriz completa con evidencia reproducida en
[`TASK-005.5-report.md`](../task-reports/TASK-005.5-report.md) §3. Resumen:

| Veredicto | Cantidad |
| --- | --- |
| **Confirmado y corregido** | 22 |
| **Confirmado parcialmente** — la regla existía, faltaba el propietario | 5 |
| **No reproducido** — el repositorio ya era correcto | 2 |

### 4.1 Los dos hallazgos **no reproducidos**

| Hallazgo de la auditoría | Qué dice realmente el repositorio |
| --- | --- |
| «**D-01 aparece abierta** pese a estar resuelta» | `open-decisions.md` la marca **Resuelta** correctamente desde `Task/005.3`, con la distinción modelo/proveedor bien hecha. El único error real era el **conteo** en `overview.md` («12 abiertas»), que sí se corrigió. **El hallazgo, tal como se formuló, no se sostiene.** |
| «**R-25 podría estar cerrado** o el *critical path* darse por demostrado» | `aws-local-parity.md` §7 mantiene la matriz **entera en `No evaluada`** y R-25 **Abierto**, con la advertencia explícita de no convertir «Floci documenta soporte» en «demostramos paridad». **Ya era correcto; no se tocó.** |

---

## 5. Decisiones técnicas

| # | Decisión | Alternativa descartada | Por qué |
| --- | --- | --- | --- |
| 1 | `Task/025` depende también de **`Task/024`** | Dejar solo `Task/022` | Sus criterios exigen ejercitar Lambda y API Gateway con un **artefacto real**, que produce `Task/024`. La matriz de paridad ya lo reconocía. |
| 2 | Separar **definición** de **validación** en `Task/029` | Mover `Task/029` después de `Task/032` | Mover la tarea entera rompería la ETAPA 09 —el VPS debe existir antes de desplegar— y arrastraría decisiones que sí pertenecen allí. Solo se movieron los ***gates***. |
| 3 | **D-15** nueva, para la topología lógica | Adelantar `Task/035` entera | El nombre del dominio cuesta dinero y es del usuario; la **topología** no. Separarlas elimina la dependencia invertida sin adelantar gasto. |
| 4 | **D-16** nueva, para la identidad del VPS | Elegir ahora clave de larga vida o IAM Roles Anywhere | Depende del proveedor de VPS, **todavía no seleccionado**. Elegir el mecanismo antes que el host sería inventarlo. |
| 5 | `Task/010` es owner del **código** de `S3Storage` | Dárselo a `Task/030` | `Task/030` vive en `personal-blog-infra`, que **no acepta código de aplicación** (ADR-002). Mover el adaptador allí rompería el límite entre repositorios. |
| 6 | `Task/029` construye el *baseline* de observabilidad del VPS | Dárselo a `Task/031` | `Task/031` es AWS puro y **CloudWatch no observa un host externo**. `Task/029` es quien construye el host. |
| 7 | **Ningún ADR nuevo** | Crear ADR-008 | No hubo decisión arquitectónica independiente. La preferencia declarada era corregir *ownership* sin fabricar ADR. |
| 8 | `Task/021` **no** declara checks de Terraform | Dejarlos como estaban | Serían checks permanentemente verdes por no tener nada que validar: aparentan cobertura. `Task/025` los añade cuando exista IaC. |

---

## 6. Criterios de aceptación

| # | Criterio | Estado |
| --- | --- | --- |
| 1 | **0 reglas operativas vigentes** ordenan crear una Task desde `dev`, en los tres repositorios | Cumplido |
| 2 | `CLAUDE.md`, `PROJECT_INSTRUCTIONS`, `WORKFLOW` y `TASK_TEMPLATE` coherentes entre sí | Cumplido |
| 3 | README y CONTRIBUTING de los tres repositorios no contradicen la regla | Cumplido |
| 4 | ADR-006 y ADR-007 figuran **Aceptadas** en todo texto vigente | Cumplido |
| 5 | Conteo de decisiones abiertas correcto y consistente | Cumplido — **13** |
| 6 | El PNG **no se modifica** y ya no se presenta como autoridad canónica vigente | Cumplido |
| 7 | Ningún texto vigente mantiene el PR de `Task/005.4` abierto | Cumplido |
| 8 | `Task/025` no puede declararse lista sin `Task/024` | Cumplido |
| 9 | `Task/029` no exige evidencia que solo existe tras `Task/030`/`Task/032` | Cumplido |
| 10 | `S3Storage`, backup, identidad del VPS, TLS, observabilidad del VPS, migraciones, medios y CI multi-provider tienen propietario inequívoco | Cumplido |
| 11 | `Task/007` no invade `Task/010` | Cumplido |
| 12 | `Task/021` no promete Terraform inexistente | Cumplido |
| 13 | La topología lógica necesaria para auth y CORS llega antes de `Task/011` | Cumplido — **D-15** |
| 14 | `Task/016` tiene criterios de SEO **verificables** y criterio de reconsideración | Cumplido |
| 15 | `Task/040` valida el VPS además de AWS; `Task/041` contempla su costo | Cumplido |
| 16 | **41 identificadores intactos**, sin huecos, duplicados ni renumeraciones | Cumplido |
| 17 | Avance **5/41**, ETAPA 02 **1/3**, `Task/006` **Pendiente** | Cumplido |
| 18 | **0 código funcional** modificado en backend y frontend | Cumplido |
| 19 | **0 Terraform**, **0 cambios en Compose**, **0 cambios en `images/`** | Cumplido |
| 20 | **0 commits, 0 push, 0 merge, 0 PR** hasta la aprobación | Cumplido — el cierre se ejecutó **después** de `approved:` |

---

## 7. TDD / Plan test-first

**No aplica.** Tarea exclusivamente documental: no introduce comportamiento funcional en
`personal-blog-backend`. La BACKEND TEST-FIRST LAW
([`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md) §4)
contempla esta excepción — y **una excepción a TDD no es una excepción a validar**: las
validaciones mecánicas se ejecutaron y se registran en el reporte §6.

---

## 8. Riesgos

| # | Riesgo | Mitigación |
| --- | --- | --- |
| 1 | Corregir *strings* sin entender las relaciones entre documentos | Cada corrección se hizo tras leer qué **consume** y qué **produce** cada tarea; el mapa de responsabilidades transversales del ROADMAP centraliza el resultado en un solo lugar |
| 2 | Convertir incertidumbres futuras en decisiones prematuras | **D-15** y **D-16** se dejan **abiertas** con propietario y momento, no resueltas |
| 3 | Que la corrección de ownership se lea como cambio de arquitectura | Declarado explícitamente en la ficha, el reporte y `STATUS.md`: **0 cambios de arquitectura**, 0 ADR nuevos |
| 4 | Que un riesgo se dé por cerrado porque ahora tiene owner | **Ningún riesgo se cerró.** Solo se corrigieron owners incorrectos (R-32) y texto obsoleto (R-03) |

**Deuda pendiente declarada:** **D-15** y **D-16** siguen abiertas por diseño; el
*ownership* futuro está asignado, la decisión no.

---

## 9. Pasos de validación para el usuario

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal

# 1. Ninguna regla operativa vigente ordena crear Task desde dev
Select-String -Path personal-blog-*\README.md, personal-blog-*\CONTRIBUTING.md `
  -Pattern 'creado desde .dev.|desde .dev.\*\*\.' 

# 2. Las tres ramas nacieron de main y no hay commits propios
foreach ($r in 'personal-blog-infra','personal-blog-backend','personal-blog-frontend') {
  Push-Location $r
  git rev-parse --abbrev-ref HEAD
  git log --oneline main..HEAD      # vacio
  git status --short
  Pop-Location
}

# 3. El PNG esta intacto
cd personal-blog-infra
git status --porcelain -- images/   # vacio
```

Revisar después: [ROADMAP](../project-management/ROADMAP.md) *Mapa de responsabilidades
transversales* · [open-decisions](../architecture/open-decisions.md) **D-15** y **D-16** ·
[STAGE-09](../stages/STAGE-09-cloud-accounts.md) *Qué `Task/029` define y qué no puede
validar todavía* · [STAGE-12](../stages/STAGE-12-launch-and-operations.md).

---

## 10. Próxima tarea propuesta

`Task/006-Fundacion-Frontend-React` — **Pendiente**. **GO** una vez aprobada y cerrada esta
tarea: sus dependencias (`Task/004`) están aprobadas, `main` y `dev` están normalizadas y
ninguna corrección de esta tarea afecta al alcance de `Task/006`.

## 11. Límites respetados

Durante la ejecución, y **hasta recibir la aprobación**: **0 commits · 0 push · 0 merge ·
0 PR · 0 recursos cloud · 0 código funcional · `Task/006` no iniciada.**

El usuario aprobó la tarea el **2026-08-16** con la expresión exacta
`approved: Task/005.5-Alinear-Planificacion-Tras-Auditoria`, lo que autorizó el flujo de
cierre de [`WORKFLOW.md`](../project-management/WORKFLOW.md) §3: commit, integración en
`dev`, publicación y pull request `Task/005.5 → main`.

**La fusión del pull request sigue siendo responsabilidad exclusiva del usuario.**
`Task/006` **no se inicia** hasta que el PR se fusione y se normalice `main → dev`.
