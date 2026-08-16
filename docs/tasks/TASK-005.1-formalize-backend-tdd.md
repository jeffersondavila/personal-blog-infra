# TASK-005.1 — Formalizar TDD en el backend

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/005.1-Formalizar-TDD-Backend` |
| **Nombre** | Formalizar TDD en el backend |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas. No altera el avance global (**5 de 41**) ni la ETAPA 02 (**1 de 3**) |
| **Etapa de referencia** | Afecta a la [ETAPA 03](../stages/STAGE-03-domain-and-backend.md), donde empieza a aplicarse |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-infra` (**únicamente**) |
| **Dependencias** | `Task/005-Fundacion-Backend-FastAPI` — **Aprobada** ✔ (2026-08-12), fusionada y normalizada |
| **Rama** | `Task/005.1-Formalizar-TDD-Backend`, creada desde `dev` |
| **Fecha de inicio** | 2026-08-13 |
| **Fecha de aprobación** | 2026-08-13 |
| **Última actualización** | 2026-08-13 — cierre aprobado |

---

## 1. Objetivo

Convertir el desarrollo **test-first** del backend en una regla del proyecto, escrita,
versionada y verificable, **antes** de que `Task/008` introduzca la primera regla de negocio.

El resultado es un documento canónico —
[`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md) — y las
referencias necesarias en instrucciones, Definition of Done, plantilla de tareas, roadmap y
ficha de la ETAPA 03.

## 2. Contexto

`Task/005` dejó el backend con estructura, configuración, logging, errores, acceso a datos y
69 pruebas, pero **sin una sola regla de negocio**. Desde `Task/008` empieza el dominio real.

Es el momento exacto de fijar la práctica: después habría código sobre el que cambiar de
método resulta caro, y las pruebas escritas a posteriori documentan lo que el código **hace**
en lugar de lo que **debe hacer**.

La regla también funciona como **límite para los agentes de programación**: sin ella, un
agente que no logra pasar una prueba puede "resolverlo" cambiando la prueba.

## 3. Dentro del alcance

- [x] Crear el documento canónico de la estrategia de pruebas del backend.
- [x] Definir la regla central **RED → GREEN → REFACTOR** y su evidencia obligatoria.
- [x] Delimitar dónde TDD es obligatorio y qué excepciones son razonables.
- [x] Formalizar la **protección de los tests** frente a implementaciones incorrectas.
- [x] Definir la matriz de comportamiento previa a la implementación.
- [x] Definir la pirámide de pruebas y los tipos de prueba del backend.
- [x] Fijar la política de **PostgreSQL real** y la de **mocks solo en boundaries**.
- [x] Formalizar la regla de **regresión** y la interpretación de la **cobertura**.
- [x] Registrar *property-based testing* como incorporación futura, sin añadir dependencias.
- [x] Definir nomenclatura y estructura objetivo de `tests/`.
- [x] Añadir la sección **BACKEND TEST-FIRST LAW** a `PROJECT_INSTRUCTIONS.md`.
- [x] Ampliar `DEFINITION_OF_DONE.md` con los criterios B-1 a B-12.
- [x] Añadir la sección *TDD / Plan test-first* a `TASK_TEMPLATE.md`.
- [x] Reflejar la política en `ROADMAP.md` y en la ficha de la ETAPA 03, para `Task/008` a
      `Task/012`.
- [x] Registrar en `STATUS.md` la normalización posterior a `Task/005` y esta tarea de
      mantenimiento.
- [x] Crear ficha y reporte de la tarea y actualizar el índice de reportes.

## 4. Fuera del alcance

| Elemento | Motivo o tarea |
| --- | --- |
| Reorganizar `tests/` de `Task/005` en `unit/`, `integration/` y `contract/` | La estructura evoluciona cuando `Task/008` aporte volumen. Reorganizar ahora sería movimiento sin beneficio sobre una tarea ya aprobada. |
| Añadir `hypothesis` o cualquier dependencia de pruebas | La estrategia la contempla como futura; la dependencia se añade en la tarea que la necesite. |
| Fijar un umbral de cobertura para CI | Corresponde a `Task/020-CI-Backend`. |
| Escribir pruebas nuevas del backend | Esta tarea no toca `personal-blog-backend`. |
| Modificar código productivo | Ninguno. Tarea exclusivamente documental. |
| `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` | Siguiente mantenimiento, **no iniciado**. |
| Crear ADR | Ninguna decisión aquí altera la arquitectura acordada: es práctica de ingeniería, no estructura del sistema. |

## 5. Entregables

| Entregable | Repositorio | Ruta | Acción |
| --- | --- | --- | --- |
| Estrategia canónica de pruebas | infra | `docs/project-management/BACKEND_TESTING_STRATEGY.md` | **Creado** |
| Ficha de esta tarea | infra | `docs/tasks/TASK-005.1-formalize-backend-tdd.md` | **Creado** |
| Reporte de esta tarea | infra | `docs/task-reports/TASK-005.1-report.md` | **Creado** |
| Ley test-first para las sesiones de Claude | infra | `docs/claude/PROJECT_INSTRUCTIONS.md` | Modificado |
| Definition of Done | infra | `docs/project-management/DEFINITION_OF_DONE.md` | Modificado |
| Plantilla de tareas | infra | `docs/project-management/TASK_TEMPLATE.md` | Modificado |
| Roadmap | infra | `docs/project-management/ROADMAP.md` | Modificado |
| Ficha de la ETAPA 03 | infra | `docs/stages/STAGE-03-domain-and-backend.md` | Modificado |
| Estado del proyecto | infra | `docs/project-management/STATUS.md` | Modificado |
| Índice de reportes | infra | `docs/task-reports/README.md` | Modificado |

**3 creados · 7 modificados · 0 eliminados.** Todos en `personal-blog-infra`.
**0 archivos** en `personal-blog-backend` y **0** en `personal-blog-frontend`.

### 5.1 Asset versionado durante el cierre

| Archivo | Origen | Autorización |
| --- | --- | --- |
| `images/Infraestructura.png` | **Asset de arquitectura preexistente agregado por el usuario** el 2026-07-26. **No lo produjo esta tarea.** | El usuario lo confirmó como parte del proyecto y **autorizó explícitamente su versionado durante este cierre**, el 2026-08-13. |

Representa la arquitectura objetivo inicial del blog: Cloudflare, Cloudflare Pages + React,
API Gateway HTTP API, AWS Lambda + FastAPI, Amazon S3, PostgreSQL administrado, SSM Parameter
Store, CloudWatch, Terraform y GitHub Actions.

**No se modificó, ni se regeneró, ni se movió, ni se alteró su contenido.** Se versiona tal
como estaba. No cuenta como entregable de `Task/005.1`.

## 6. Criterios de aceptación

| # | Criterio | Estado |
| --- | --- | --- |
| 1 | Existe un único documento canónico con la práctica completa. | Cumplido — validación 1 |
| 2 | La regla central es explícita: RED → GREEN → REFACTOR. | Cumplido — validación 2 |
| 3 | Está definido dónde TDD es obligatorio y qué excepciones se admiten. | Cumplido — validación 2 |
| 4 | La protección de los tests está formalizada y es aplicable a agentes. | Cumplido — validación 3 |
| 5 | La matriz de comportamiento es obligatoria antes de implementar. | Cumplido — validaciones 2 y 6 |
| 6 | La política de PostgreSQL real prohíbe sustituirlo por SQLite. | Cumplido — validación 4 |
| 7 | La política de mocks limita su uso a los *boundaries*. | Cumplido — validación 4 |
| 8 | Existe la regla «sin bug fix sin test de regresión». | Cumplido — validación 4 |
| 9 | La cobertura queda declarada como señal, no como especificación. | Cumplido — validación 4 |
| 10 | `PROJECT_INSTRUCTIONS.md` contiene la ley compacta y enlaza a la estrategia. | Cumplido — validaciones 5 y 9 |
| 11 | La Definition of Done exige evidencia de RED y GREEN. | Cumplido — validación 5 |
| 12 | La plantilla de tareas incluye la sección *TDD / Plan test-first*. | Cumplido — validación 6 |
| 13 | `Task/008` a `Task/012` referencian la política en ROADMAP y ETAPA 03. | Cumplido — validación 7 |
| 14 | No se renumeró ninguna tarea y siguen siendo exactamente 41. | Cumplido — validación 8 |
| 15 | El avance global permanece en 5 de 41 y la ETAPA 02 en 1 de 3. | Cumplido — validación 8 |
| 16 | Todos los enlaces relativos resuelven. | Cumplido — validación 9 |
| 17 | Cero cambios en `personal-blog-backend` y en `personal-blog-frontend`. | Cumplido — validación 11 |
| 18 | Ningún secreto versionado, ningún archivo Terraform, Floci no incorporado. | Cumplido — validaciones 10 y 12 |
| 19 | La tarea queda `Lista para validación`, nunca `Aprobada` por decisión propia. | Cumplido |
| 20 | `Task/006` y `Task/005.2` no se inician. | Cumplido — validación 13 |

## 7. TDD / Plan test-first

**No aplica.** Esta tarea no introduce comportamiento funcional del backend: es
documentación de gobierno. Su verificación equivalente es la **consistencia entre
documentos**, comprobada en la sección 10.

Es, además, la tarea que **crea** la obligación para las demás: desde `Task/008`, ninguna
tarea de backend funcional podrá escribir `No aplica` en esta sección.

## 8. Plan de validación

Cada criterio se comprueba por búsqueda de términos en los documentos afectados, por
verificación de enlaces relativos y por recuento de las tareas del roadmap.

## 9. Comandos de validación

```powershell
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

# Presencia de la practica en los documentos actualizados
Select-String -Path docs\claude\PROJECT_INSTRUCTIONS.md -Pattern "TEST-FIRST|RED|GREEN"
Select-String -Path docs\project-management\DEFINITION_OF_DONE.md -Pattern "RED|GREEN|regresion"
Select-String -Path docs\project-management\TASK_TEMPLATE.md -Pattern "test-first"

# Recuento del roadmap: deben seguir siendo 41
Select-String -Path docs\project-management\ROADMAP.md -Pattern "^\| ``Task/0" | Measure-Object

# Git
git status --porcelain -b
git diff --check
```

## 10. Resultado de las validaciones

Ejecutadas el 2026-08-13. **Ninguna se declara sin haberse ejecutado.**

| # | Validación | Resultado real |
| --- | --- | --- |
| 1 | Documento canónico | **Creado.** `BACKEND_TESTING_STRATEGY.md`, 16 secciones, declarado fuente única. |
| 2 | Regla central, ámbito y excepciones | **Presentes.** §2 la regla; §3 las áreas obligatorias; §4 las excepciones, con la advertencia de que una excepción a TDD no lo es a validar. |
| 3 | Protección de los tests | **Presente** en §9, con las 4 causas admitidas de cambio y las 6 prácticas prohibidas. Replicada en forma compacta en `PROJECT_INSTRUCTIONS.md` §14. |
| 4 | PostgreSQL real, mocks, regresión y cobertura | **Presentes** en §8.3, §10, §11 y §12. Incluye la prohibición explícita de sustituir PostgreSQL por SQLite y la frase «Coverage is a signal, not the specification». |
| 5 | `PROJECT_INSTRUCTIONS.md` y Definition of Done | **Actualizados.** Nueva sección **14. BACKEND TEST-FIRST LAW** (con renumeración de las secciones 15 y 16) y criterios **B-1 a B-12** para tareas de backend funcional, más dos causas nuevas de invalidación. |
| 6 | `TASK_TEMPLATE.md` | **Actualizada.** Nueva sección **7. TDD / Plan test-first** con 6 subsecciones; las secciones siguientes se renumeraron de 8 a 20 sin pérdida de contenido. |
| 7 | `Task/008` a `Task/012` | **Las cinco** referencian la política, en `ROADMAP.md` y en la ficha de la ETAPA 03, con la aplicación concreta a cada tarea. |
| 8 | Recuento e integridad del roadmap | **41 tareas**, sin renumerar ninguna. Avance global **5 de 41 (12 %)**; ETAPA 02 **1 de 3**; ETAPA 03 **0 de 5**. |
| 9 | Enlaces Markdown relativos | **0 rotos** en los 9 documentos afectados. |
| 10 | Búsqueda de secretos | **0 credenciales.** Los documentos nuevos no contienen valores sensibles. |
| 11 | Repositorios no implicados | **`personal-blog-backend`: 0 cambios**, árbol limpio en `main`. **`personal-blog-frontend`: 0 cambios**, árbol limpio en `main`. |
| 12 | Terraform y Floci | **0 archivos `*.tf`** en todo el workspace. **Floci no incorporado:** sin ADR, sin versión concreta, sin cambios en documentos de arquitectura ni de cloud. Solo se nombra en el identificador de la futura `Task/005.2` y en la sección de handoff del reporte. |
| 13 | Tareas no iniciadas | **`Task/006`** y **`Task/005.2`** siguen sin rama, sin ficha y sin cambios. |
| 14 | `git diff --check` | **Sin errores** de espacios en blanco. |

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-17 | **Nuevo.** Una regla escrita puede no aplicarse: el ciclo RED→GREEN es fácil de saltarse si nadie exige la evidencia. | Medio | La evidencia es un **criterio de la Definition of Done** (B-2 y B-3), no una recomendación: sin ella la tarea no puede marcarse `Lista para validación`. `Task/020` podrá reforzarlo en CI. |
| R-18 | **Nuevo.** El coste de escribir primero la prueba puede empujar a matrices superficiales que aparenten cumplimiento. | Bajo | La matriz exige explícitamente edge cases, errores y casos de seguridad, y la revisión del usuario es el control final. |
| R-14 | Las dependencias transitivas del backend siguen sin bloquear. | Medio | Sin cambios. `Task/020`. |
| R-16 | El `.env` local conserva las contraseñas de ejemplo. | Bajo | Sin cambios. Decisión del usuario. |

## 12. Decisiones técnicas

| # | Decisión | Alternativas consideradas | Justificación | ¿ADR? |
| --- | --- | --- | --- | --- |
| 1 | **Documento canónico en `docs/project-management/`.** | `docs/architecture/`; dentro de `CONTRIBUTING.md` del backend. | Es una práctica de **proceso**, no una decisión de estructura del sistema: convive con `WORKFLOW.md`, `DEFINITION_OF_DONE.md` y `TASK_TEMPLATE.md`, que son quienes la exigen. Además debe vivir en `infra`, la fuente de verdad del gobierno. | No |
| 2 | **Referenciar, no duplicar.** | Repetir la regla completa en cada documento. | Cinco copias divergen en cuanto una cambia. Cada documento enuncia lo mínimo operativo y enlaza a la fuente única. | No |
| 3 | **Sin ADR.** | Crear un ADR de práctica de pruebas. | Los ADR del proyecto registran decisiones de arquitectura del sistema (ADR-001 a ADR-005). Esta es una norma de trabajo, revisable sin alterar la arquitectura. | No |
| 4 | **Sin umbral de cobertura.** | Fijar aquí un mínimo, por ejemplo 90 %. | El roadmap reserva la política de CI a `Task/020`. Fijar un número aquí crearía dos fuentes de verdad y empujaría a escribir pruebas para cuadrar la estadística. | No |
| 5 | **No reorganizar `tests/` ahora.** | Migrar ya a `unit/`, `integration/`, `contract/`. | `Task/005` está aprobada y fusionada; mover archivos sin necesidad genera ruido en el historial sin beneficio. La estructura se adopta cuando haya volumen (`Task/008`). | No |
| 6 | **No añadir `hypothesis`.** | Incorporar *property-based testing* ya. | Una dependencia sin uso real es deuda. Se documenta como incorporación futura, con sus casos candidatos. | No |
| 7 | **Renumerar `TASK_TEMPLATE.md` en lugar de añadir la sección al final.** | Añadir *TDD* como sección 20. | El plan test-first debe leerse **antes** del plan de validación, porque se completa antes de implementar. El orden del documento refleja el orden del trabajo. | No |

## 13. Documentación creada o actualizada

- `docs/project-management/BACKEND_TESTING_STRATEGY.md` — **creado**: práctica completa.
- `docs/claude/PROJECT_INSTRUCTIONS.md` — nueva sección 14 con la ley compacta.
- `docs/project-management/DEFINITION_OF_DONE.md` — criterios B-1 a B-12 y dos causas nuevas
  de invalidación.
- `docs/project-management/TASK_TEMPLATE.md` — nueva sección 7 y renumeración.
- `docs/project-management/ROADMAP.md` — nota de etapa y política por tarea en `008`–`012`.
- `docs/stages/STAGE-03-domain-and-backend.md` — práctica obligatoria, aplicación por tarea,
  criterio de salida y riesgo nuevo.
- `docs/project-management/STATUS.md` — normalización de `Task/005` y registro de este
  mantenimiento.
- `docs/task-reports/README.md` — índice.

## 14. Archivos modificados

Ver sección 5. **10 archivos**, todos en `personal-blog-infra`.

## 15. Resultado de pruebas

**No aplica en el sentido habitual:** la tarea no ejecuta código. Su equivalente son las
14 validaciones de consistencia documental de la sección 10, todas ejecutadas.

La suite del backend **no se reejecutó**: esta tarea no toca `personal-blog-backend`, cuyo
árbol permanece limpio en `main` con las 69 pruebas ya validadas y aprobadas en `Task/005`.

## 16. Problemas encontrados

| # | Problema | Resolución |
| --- | --- | --- |
| 1 | **La renumeración de `TASK_TEMPLATE.md` con un reemplazo masivo en PowerShell corrompió el archivo:** los reemplazos encadenados colisionaron entre sí y la reescritura alteró la codificación de todos los acentos (`aceptación` → `aceptaciÃ³n`). | El archivo se restauró desde `HEAD` con `git checkout --` sobre **ese único archivo**, cuyo contenido era el original íntegro, y la renumeración se rehízo sección por sección con la herramienta de edición, de la más alta a la más baja para evitar colisiones. Se verificó después: numeración 1–20 correcta y **0 secuencias de mojibake**. No se perdió trabajo de ninguna otra tarea. |
| 2 | **Directorio `images/` sin rastrear** en `personal-blog-infra`, con `Infraestructura.png` (2 MB, del 2026-07-26). No lo creó esta tarea. | Se informó al usuario, que lo **confirmó como parte del proyecto** —diagrama de la arquitectura objetivo inicial— y **autorizó explícitamente versionarlo durante el cierre**. Se incluye en el commit **sin modificarlo, regenerarlo ni moverlo**, y se registra como asset preexistente, no como entregable de esta tarea. Ver §5.1. |

## 17. Pasos de validación para el usuario

```powershell
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

# 1. Rama y estado
git branch --show-current            # Task/005.1-Formalizar-TDD-Backend
git status --porcelain -b            # cambios sin confirmar

# 2. Lee la estrategia completa
code docs\project-management\BACKEND_TESTING_STRATEGY.md

# 3. Comprueba que la regla llega a quien debe aplicarla
Select-String -Path docs\claude\PROJECT_INSTRUCTIONS.md -Pattern "TEST-FIRST LAW"
Select-String -Path docs\project-management\DEFINITION_OF_DONE.md -Pattern "Evidencia RED"
Select-String -Path docs\project-management\TASK_TEMPLATE.md -Pattern "7. TDD"

# 4. El roadmap sigue teniendo 41 tareas y nadie fue renumerado
Select-String -Path docs\project-management\ROADMAP.md -Pattern "5 de 41"

# 5. Los otros repositorios no se tocaron
git -C ..\personal-blog-backend status --porcelain -b
git -C ..\personal-blog-frontend status --porcelain -b
```

Ningún comando es destructivo.

## 18. Deuda técnica pendiente

- **La estructura `tests/unit|integration|contract` está definida pero no adoptada.** Se
  aplicará en `Task/008`.
- **Sin verificación automática de la práctica.** Que exista evidencia de RED se comprueba
  hoy por revisión humana; `Task/020` puede reforzarlo en CI.
- **Sin *property-based testing*.** Documentado como futuro, sin dependencia añadida.

## 19. Próxima tarea

`Task/005.2-Documentar-Estrategia-Floci-IaC-Local` — mantenimiento documental, **no
iniciado**. No comienza hasta que `Task/005.1` sea aprobada, fusionada y normalizada.

Después, el roadmap continúa por `Task/006-Fundacion-Frontend-React`.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** ✔ |
| **Fecha de aprobación** | 2026-08-13 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.1-Formalizar-TDD-Backend` |
| **Efecto en el avance** | **Ninguno.** Es mantenimiento: no cuenta dentro de las 41 tareas. Avance global **5 de 41 (12 %)**; ETAPA 02 **1 de 3** |

> El usuario autorizó explícitamente el cierre con la expresión exacta requerida por
> [WORKFLOW.md](../project-management/WORKFLOW.md) §3, y autorizó por separado versionar el
> asset `images/Infraestructura.png` (§5.1).
