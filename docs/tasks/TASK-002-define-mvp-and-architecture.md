# TASK-002 — Definir MVP y Arquitectura

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/002-Definir-MVP-y-Arquitectura` |
| **Nombre** | Definir MVP y Arquitectura |
| **Etapa** | ETAPA 00 — Fundación y Gobierno |
| **Estado** | **Lista para validación** |
| **Repositorios involucrados** | `personal-blog-infra` (únicamente) |
| **Dependencias** | `Task/001-Inicializar-Workspace-y-Roadmap` — **Aprobada** ✔ |
| **Rama** | `Task/002-Definir-MVP-y-Arquitectura`, creada desde `dev` en `personal-blog-infra` |
| **Fecha de inicio** | 2026-07-26 |
| **Última actualización** | 2026-07-26 |

---

## 1. Objetivo

Definir y documentar completamente el **MVP** del blog personal y la **arquitectura de
software** que guiará todas las tareas posteriores, sin implementar nada.

Al terminar debe estar claro: qué funcionalidades tendrá el MVP y cuáles no, qué tipos de
contenido existirán, qué flujos públicos y administrativos habrá, cómo se reparten las
responsabilidades entre los tres repositorios, cómo se organiza el backend, cómo se
comunica el frontend con él, qué contratos sigue la API, qué requisitos no funcionales
rigen, qué decisiones están tomadas y cuáles quedan diferidas.

## 2. Contexto

`Task/001` estableció el gobierno del proyecto (roadmap, flujo de trabajo, ADR
fundacionales) pero **no definió el producto**. Sin un alcance cerrado, las 39 tareas
restantes no tienen criterio para decidir qué entra y qué no.

Esta tarea es la última puerta antes de tocar infraestructura (`Task/003`) y código
(`Task/005`, `Task/006`).

## 3. Dentro del alcance

- [x] Normalizar el historial de ramas de los tres repositorios (mantenimiento previo).
- [x] Crear `Task/002` desde `dev` **solo** en `personal-blog-infra`.
- [x] Corregir el estado de cierre de `Task/001` y cerrar el bloqueo B-01.
- [x] Definir el alcance funcional del MVP (sitio público, panel, contacto, contenido).
- [x] Definir explícitamente lo que queda **fuera** del MVP.
- [x] Documentar los flujos públicos y administrativos.
- [x] Documentar el modelo conceptual de contenido.
- [x] Documentar la arquitectura de backend (monolito modular).
- [x] Documentar la arquitectura de frontend (orientada a funcionalidades).
- [x] Documentar los contratos generales de API, paginación y modelo de error.
- [x] Documentar la abstracción `ObjectStorage`.
- [x] Documentar los requisitos de autenticación **sin decidir el mecanismo**.
- [x] Documentar los requisitos no funcionales.
- [x] Documentar los límites de seguridad.
- [x] Registrar las decisiones diferidas.
- [x] Crear ADR-004 y ADR-005.
- [x] Actualizar la documentación de gestión afectada.

## 4. Fuera del alcance

| Elemento | Dónde corresponde |
| --- | --- |
| Código React, `package.json` | `Task/006` |
| Código FastAPI, `pyproject.toml` | `Task/005` |
| Migraciones, tablas SQL, índices | `Task/008` |
| `Dockerfile`, Docker Compose | `Task/003`, `Task/005` |
| Levantar PostgreSQL, MinIO, Portainer | `Task/003` |
| Terraform | `Task/025` |
| Workflows de GitHub Actions | Etapa 06 |
| Recursos cloud | Etapas 09 y 10 |
| Elección del proveedor PostgreSQL cloud | `Task/029` |
| Implementación de autenticación | `Task/011` |
| Especificación OpenAPI completa | `Task/009`, `Task/012` |
| Diseño visual de la interfaz | `Task/013` |
| Iniciar `Task/003` | — |

También quedan fuera, **por decisión consciente**, las 13 decisiones registradas en
[open-decisions.md](../architecture/open-decisions.md).

---

## 5. Preparación de ramas (mantenimiento previo)

### 5.1 Situación encontrada

Los pull requests de `Task/001` se integraron **desde la rama `Task/001` directamente
hacia `main`**, no desde `dev`. Resultado: `main` y `dev` tenían **el mismo contenido pero
distintos commits de merge**, y `origin/main` contenía un commit que `dev` no incluía
formalmente.

| Repositorio | `main` antes | `dev` antes | Commit de `main` ausente en `dev` |
| --- | --- | --- | --- |
| `personal-blog-infra` | `8fd61ea` | `f4f32a9` | `8fd61ea` |
| `personal-blog-frontend` | `144a401` | `2d18231` | `144a401` |
| `personal-blog-backend` | `76c09f5` | `e61a848` | `76c09f5` |

### 5.2 Secuencia ejecutada

En cada repositorio:

```bash
git fetch --prune origin
git switch main && git pull --ff-only
git switch dev  && git pull --ff-only
git log --oneline dev..origin/main            # confirma la divergencia
git merge --no-ff origin/main -m "merge: sincronizar dev con main despues de Task/001"
git diff --stat dev origin/main               # vacío: mismo contenido
git push origin dev
git switch main
```

### 5.3 Resultado

| Repositorio | `dev` después | Diferencia de contenido `dev` vs `main` |
| --- | --- | --- |
| `personal-blog-infra` | `cc3aad8` | Ninguna |
| `personal-blog-frontend` | `8823cc3` | Ninguna |
| `personal-blog-backend` | `0f94abb` | Ninguna |

Se publicó **únicamente** esa sincronización de `dev`. Los árboles de trabajo quedaron
limpios y la rama activa volvió a `main` en frontend y backend.

### 5.4 Rama de la tarea

`Task/002-Definir-MVP-y-Arquitectura` se creó desde `dev` **solo en
`personal-blog-infra`**, porque la tarea modifica exclusivamente documentación central.
**No se creó en frontend ni en backend.**

---

## 6. Corrección del estado de `Task/001`

Durante el cierre de `Task/001` no había credenciales de GitHub en el entorno, lo que
generó el bloqueo **B-01**. El usuario lo resolvió después instalando y autenticando
GitHub CLI. La documentación reflejaba el estado bloqueado y se actualizó:

| Documento | Corrección |
| --- | --- |
| `STATUS.md` | Bloqueos activos: 1 → 0. B-01 pasa a **Cerrado** con su resolución. Sección *Estado de los repositorios* reescrita: ramas publicadas, `Task/001` eliminada, sincronización `main`↔`dev` explicada. |
| `TASK-001-*.md` (ficha) | Sección 7.0: publicación **completada**; `Task/001` eliminada local y remotamente. Tabla del flujo de cierre: pasos 7, 8, 9 y 11 pasan de *Bloqueado/Diferido* a *Hecho*. |
| `TASK-001-report.md` | Nota de cierre al inicio de la sección 7.2; sección 8.2 marcada como *ya ejecutada*; sección 10 con el estado remoto resultante (PR `#1` aceptados). |
| `README.md` de infra | Estado de ramas actualizado. |

**Se conservó el registro histórico del bloqueo.** El reporte sigue describiendo que B-01
ocurrió y por qué; lo que se añadió es la nota de cierre. No se reescribió para simular
que nunca sucedió.

---

## 7. Entregables

| Entregable | Ruta | Acción |
| --- | --- | --- |
| Alcance del MVP | `docs/product/MVP_SCOPE.md` | Creado |
| Flujos de usuario | `docs/product/USER_FLOWS.md` | Creado |
| Modelo de contenido | `docs/product/CONTENT_MODEL.md` | Creado |
| Arquitectura de software | `docs/architecture/software-architecture.md` | Creado |
| Contratos de API | `docs/architecture/api-contracts.md` | Creado |
| Requisitos no funcionales | `docs/architecture/non-functional-requirements.md` | Creado |
| Límites de seguridad | `docs/architecture/security-boundaries.md` | Creado |
| Decisiones diferidas | `docs/architecture/open-decisions.md` | Creado |
| ADR monolito modular | `docs/adr/ADR-004-modular-monolith.md` | Creado |
| ADR contenido Markdown | `docs/adr/ADR-005-markdown-content.md` | Creado |
| Ficha de esta tarea | `docs/tasks/TASK-002-define-mvp-and-architecture.md` | Creado |
| Reporte de esta tarea | `docs/task-reports/TASK-002-report.md` | Creado |
| Estado del proyecto | `docs/project-management/STATUS.md` | Modificado |
| Roadmap | `docs/project-management/ROADMAP.md` | Modificado |
| Ficha de etapa 00 | `docs/stages/STAGE-00-foundation.md` | Modificado |
| Visión general | `docs/architecture/overview.md` | Modificado |
| Mapeo local → nube | `docs/architecture/local-to-cloud-mapping.md` | Modificado |
| Índice de reportes | `docs/task-reports/README.md` | Modificado |
| README de infra | `README.md` | Modificado |
| Ficha de `Task/001` | `docs/tasks/TASK-001-initial-workspace-and-roadmap.md` | Modificado |
| Reporte de `Task/001` | `docs/task-reports/TASK-001-report.md` | Modificado |

**12 creados · 9 modificados · 0 eliminados.**

---

## 8. Criterios de aceptación

| # | Criterio | Estado |
| --- | --- | --- |
| 1 | `main` y `dev` sincronizadas en los tres repositorios. | Cumplido — sección 5 |
| 2 | Rama `Task/002` desde `dev` solo en `personal-blog-infra`. | Cumplido |
| 3 | Estado real de cierre de `Task/001` actualizado. | Cumplido — sección 6 |
| 4 | Alcance del MVP claramente definido. | Cumplido — `MVP_SCOPE.md` |
| 5 | Fuera de alcance claramente definido. | Cumplido — `MVP_SCOPE.md` §6 |
| 6 | Todos los tipos de contenido documentados. | Cumplido — `CONTENT_MODEL.md` (9 tipos) |
| 7 | Flujos públicos y administrativos documentados. | Cumplido — `USER_FLOWS.md` (11 + 12) |
| 8 | Arquitectura del backend documentada. | Cumplido — `software-architecture.md` §3 |
| 9 | Arquitectura del frontend documentada. | Cumplido — `software-architecture.md` §4 |
| 10 | Responsabilidades de los tres repositorios documentadas. | Cumplido — `software-architecture.md` §2 |
| 11 | Contratos generales de API documentados. | Cumplido — `api-contracts.md` |
| 12 | Modelo común de errores documentado. | Cumplido — `api-contracts.md` §7 |
| 13 | Modelo de paginación documentado. | Cumplido — `api-contracts.md` §5 |
| 14 | Abstracción `ObjectStorage` documentada. | Cumplido — `software-architecture.md` §3.7 |
| 15 | Requisitos de autenticación sin decidir el mecanismo. | Cumplido — `security-boundaries.md` + D-02 |
| 16 | Requisitos no funcionales documentados. | Cumplido — `non-functional-requirements.md` (**57 requisitos** en 7 categorías) |
| 17 | Límites de seguridad documentados. | Cumplido — `security-boundaries.md` (11 componentes) |
| 18 | Decisiones diferidas registradas. | Cumplido — `open-decisions.md` (13) |
| 19 | ADR-004 y ADR-005 existen. | Cumplido — ambos en estado **Propuesta**, pendientes de la aprobación de `Task/002` |
| 20 | No se implementó código funcional. | Cumplido — verificado por búsqueda |
| 21 | No se creó ningún recurso cloud. | Cumplido |
| 22 | No se agregó ningún secreto. | Cumplido — verificado por búsqueda |
| 23 | Todos los enlaces relativos resuelven. | Cumplido — 252 enlaces, 0 rotos |
| 24 | `Task/002` queda `Lista para validación`, nunca `Aprobada`. | Cumplido |
| 25 | No se inició `Task/003`. | Cumplido |

---

## 9. Plan y comandos de validación

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal

# Estado de ramas y sincronización
foreach ($r in @('personal-blog-backend','personal-blog-frontend','personal-blog-infra')) {
  git -C $r status --porcelain -b
  git -C $r branch -vv
  git -C $r branch -r
  git -C $r log --oneline --graph --all -12
}

# Ausencia de archivos fuera de alcance
Get-ChildItem -Recurse -File . -Include *.py,*.ts,*.tsx,*.jsx,*.tf,*.tfvars,`
  package.json,pyproject.toml,Dockerfile,docker-compose*.yml |
  Where-Object { $_.FullName -notmatch '\\\.git\\' }
```

---

## 10. Resultado de las validaciones

| # | Validación | Resultado |
| --- | --- | --- |
| 1 | `git status` ×3 | Frontend y backend limpios en `main`. Infra en `Task/002` con **9 modificados** y **10 entradas sin seguimiento**, que representan **12 archivos nuevos** porque Git agrupa `docs/product/` como una sola entrada de directorio (contiene 3 archivos). Todo es documentación `.md`. |
| 2 | `git branch -vv` ×3 | `main` y `dev` con seguimiento correcto. `Task/002` solo en infra. |
| 3 | `git branch -r` ×3 | `origin/main` y `origin/dev` en los tres. Ninguna rama `Task/001` remota. |
| 4 | `git log --graph` | Historial esperado en los tres: commit inicial → trabajo → merge en `dev` → PR a `main` → sincronización. |
| 5 | `main` y `dev` con el mismo contenido | `git diff --stat dev origin/main` **vacío** en los tres. |
| 6 | Archivos creados y modificados | **12 creados, 9 modificados, 0 eliminados.** Todos `.md`. Aparecen como 10 entradas sin seguimiento por la agrupación de `docs/product/`. |
| 7 | Enlaces Markdown relativos | **254 verificados, 0 rotos.** |
| 8 | Búsqueda de secretos | 0 coincidencias reales. La única aparición es la lista de patrones citada en el reporte de `Task/001`. |
| 9 | Archivos de código o infraestructura | **Ninguno.** Sin `*.py`, `*.ts`, `*.tsx`, `*.tf`, `package.json`, `pyproject.toml`, `Dockerfile` ni `docker-compose*.yml`. |
| 10 | Coherencia entre documentos | Verificada — sección 11. |
| 11 | Decisiones que debían diferirse | Ninguna tomada — sección 12. |

---

## 11. Revisión de coherencia entre documentos

| Verificación | Resultado |
| --- | --- |
| Cada sección del sitio en `MVP_SCOPE` tiene un flujo en `USER_FLOWS`. | 10 secciones ↔ 11 flujos públicos (el 11.º es la página 404). |
| Cada capacidad del panel en `MVP_SCOPE` tiene un flujo administrativo. | 17 capacidades cubiertas por 12 flujos. |
| Cada flujo referencia un recurso existente en `api-contracts`. | Sí — matriz flujo → recurso en `USER_FLOWS`. |
| Cada tipo de `CONTENT_MODEL` tiene un módulo en `software-architecture`. | 9 tipos ↔ 9 módulos. |
| Cada recurso público de `api-contracts` corresponde a un tipo publicable. | Sí. |
| Los estados `draft`/`published`/`archived` son idénticos en los cuatro documentos. | Sí. |
| `ObjectStorage` se describe igual en arquitectura, modelo y seguridad. | Sí. |
| Editor Markdown y vista previa: mismos tipos en `MVP_SCOPE`, `USER_FLOWS`, `CONTENT_MODEL` y ADR-005. | Sí, tras la corrección — `Post`, `BookReview` y `Project` sí; `Video` no. |
| Los tipos con `content` en Markdown coinciden con los que tienen vista previa. | Sí — los tres mismos. |
| Las exclusiones del MVP coinciden con las de ADR-003 y ADR-004. | Sí. |
| Toda decisión diferida citada en algún documento aparece en `open-decisions`. | Sí — 13 de 13. |

---

## 12. Decisiones tomadas y decisiones respetadas como diferidas

### Propuestas en esta tarea

> **Ninguna es firme todavía.** `Task/002` está `Lista para validación`; estas decisiones
> están **propuestas y documentadas**, y pasarán a ser aceptadas cuando el usuario escriba
> `approved: Task/002-Definir-MVP-y-Arquitectura`. ADR-004 y ADR-005 llevan estado
> **Propuesta** por ese motivo.

| Decisión | Registro |
| --- | --- |
| Monolito modular con Clean Architecture pragmática; sin microservicios. | [ADR-004](../adr/ADR-004-modular-monolith.md) |
| Contenido principal en Markdown, almacenado en origen y sanitizado al renderizar. | [ADR-005](../adr/ADR-005-markdown-content.md) |
| Alcance del MVP y su fuera de alcance. | [MVP_SCOPE.md](../product/MVP_SCOPE.md) |
| Convenciones de API, paginación (`page`/`page_size`) y modelo común de error. | [api-contracts.md](../architecture/api-contracts.md) |
| Estructura de módulos del backend y de carpetas del frontend. | [software-architecture.md](../architecture/software-architecture.md) |
| Requisitos no funcionales (**57**, en 7 categorías). | [non-functional-requirements.md](../architecture/non-functional-requirements.md) |
| Límites de seguridad y reglas de Portainer. | [security-boundaries.md](../architecture/security-boundaries.md) |

### Respetadas como diferidas (no decididas aquí)

Mecanismo de autenticación · duración de sesión · estrategia CSRF · herramienta de rate
limiting · proveedor de PostgreSQL administrado · biblioteca de componentes visuales ·
editor Markdown · reverse proxy local · backend de estado de Terraform · dominio ·
estrategia de CDN · estrategia de backups cloud · retención de CloudWatch · límites de
Lambda · presupuesto mensual.

Registro completo: [open-decisions.md](../architecture/open-decisions.md).

---

## 13. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-02 | Costo cloud imprevisto en la Etapa 10. | Alto | `Task/027`; presupuesto es D-13. |
| R-03 | PostgreSQL administrado condiciona las conexiones desde Lambda. | Medio | D-01, `Task/029`. |
| R-04 | El roadmap puede desactualizarse si cambia el alcance. | Bajo | `MVP_SCOPE.md` es ahora el criterio de referencia. |
| R-05 | Los enlaces entre repositorios asumen carpetas hermanas. | Bajo | Documentado en los README. |
| R-06 | **Nuevo.** El alcance del MVP puede crecer durante la implementación. | Medio | `MVP_SCOPE.md` §6 lista explícitamente lo excluido; toda incorporación exige un ADR. |
| R-07 | **Nuevo.** El render de Markdown en cliente puede resultar insuficiente para SEO. | Medio | Metadatos y datos estructurados en `Task/016`; si no basta, se reconsidera ADR-005. |

R-01 y el bloqueo B-01 quedan **cerrados**.

---

## 14. Problemas encontrados

| # | Problema | Resolución |
| --- | --- | --- |
| 1 | `main` y `dev` tenían el mismo contenido pero distintos commits de merge, por integrarse los PR desde `Task/001` hacia `main`. | Normalizado con merge `--no-ff` de `origin/main` en `dev`, publicado (sección 5). |
| 2 | La documentación de `Task/001` describía un bloqueo B-01 ya resuelto. | Actualizada conservando el registro histórico (sección 6). |
| 3 | `gh` está instalado pero no en el `PATH` de la shell de trabajo. | No afecta: el helper de credenciales de Git lo invoca por ruta absoluta y las operaciones remotas funcionan. |
| 4 | **Contradicción sobre la vista previa de `Project`.** ADR-005 incluía `Project` entre los tipos con contenido Markdown y establecía editor y vista previa para el contenido Markdown, pero `USER_FLOWS` limitaba la vista previa a artículos y reviews y `MVP_SCOPE` describía los proyectos como contenido estructurado sin vista previa. | Corregido — sección 18. |
| 5 | **Total de requisitos no funcionales incorrecto.** Se declaraban 43 cuando la suma real de las categorías (12+8+8+8+8+7+6) es **57**. | Corregido — sección 18. |
| 6 | **Resultados de validación imprecisos.** Se citaban "8 sin seguimiento" y, en una versión previa, "226 enlaces". | Corregido — sección 18. |

---

## 15. Pasos de validación para el usuario

Ver [reporte de la tarea](../task-reports/TASK-002-report.md), sección 15.

---

## 16. Deuda técnica pendiente

- 13 decisiones diferidas, todas con tarea asignada.
- Las rutas públicas exactas del sitio son una propuesta; se confirman en `Task/014`.
- La forma exacta de las transiciones de estado en la API se cierra en `Task/012`.
- La restauración desde `archived` no es obligatoria en el MVP; si no se implementa en
  `Task/012`, se registra como deuda.

---

## 17. Próxima tarea

`Task/003-Crear-Infraestructura-Local` — Docker Compose, PostgreSQL, MinIO, Portainer,
redes, volúmenes y healthchecks.

**No se inicia hasta que `Task/002` sea aprobada.**

---

## 18. Correcciones aplicadas tras la revisión del usuario

Ronda de corrección del 2026-07-26, sobre la misma rama y **sin cambiar el alcance
general**. La tarea permanece `Lista para validación`.

### 18.1 Vista previa de `Project`

**Contradicción:** ADR-005 incluía `Project` entre los tipos con contenido principal en
Markdown y establecía editor y vista previa para ese contenido, pero `USER_FLOWS` limitaba
la vista previa a artículos y reviews y `MVP_SCOPE` describía los proyectos como contenido
estructurado que no la requería.

**Resolución — queda establecido en todos los documentos:**

| Tipo | Contenido principal | Editor Markdown | Vista previa |
| --- | --- | :---: | :---: |
| `Post` | Markdown | Sí | **Sí** |
| `BookReview` | Markdown | Sí | **Sí** |
| `Project` | Markdown | Sí | **Sí** |
| `Video` | URL, proveedor y metadatos | **No** | **No** |

Además, en los cuatro documentos:

- La vista previa **no publica** el contenido ni lo expone: no cambia su estado, no genera
  URL pública y no lo hace accesible a visitantes.
- La vista previa usa **el mismo pipeline de render y sanitización que el sitio público**.
- La diferencia de ciclo de vida entre tipos es la **despublicación** (solo artículos y
  reviews), **no** la vista previa.

Documentos corregidos: `MVP_SCOPE.md` (§3.1), `USER_FLOWS.md` (B.6 y matriz),
`CONTENT_MODEL.md` (§2, notas), `ADR-005-markdown-content.md` (decisión 6), esta ficha y
el reporte.

### 18.2 Total de requisitos no funcionales

**Error:** se declaraban **43** requisitos. La suma real de las categorías es
`12 + 8 + 8 + 8 + 8 + 7 + 6 = 57`.

**Resolución:** el total correcto es **57**. No se eliminó ni fusionó ningún requisito
individual: no había duplicaciones, solo un total mal sumado. Se añadió una tabla de
recuento por categoría en `non-functional-requirements.md` para que el total sea
verificable.

Documentos corregidos: `non-functional-requirements.md`, esta ficha, el reporte,
`README.md` y `overview.md`.

### 18.3 Resultados finales de validación

| Métrica | Valor final |
| --- | --- |
| Archivos creados | **12** |
| Archivos modificados | **9** |
| Archivos eliminados | **0** |
| Entradas sin seguimiento en `git status` | **10** |
| Enlaces Markdown relativos verificados | **254** |
| Enlaces rotos | **0** |

> El recuento de enlaces pasó de 252 a **254** en esta ronda de corrección: los dos
> enlaces cruzados nuevos entre `USER_FLOWS.md` y `CONTENT_MODEL.md`, añadidos para que
> ambos documentos apunten a la definición de la vista previa. Ninguno está roto.

**Aclaración sobre 10 vs 12:** `git status` muestra **10 entradas** sin seguimiento para
**12 archivos nuevos** porque Git agrupa `docs/product/` como una **sola entrada de
directorio**, y ese directorio contiene 3 archivos. Son 9 entradas individuales más 3
archivos dentro de `docs/product/`.

Se corrigieron las referencias previas a "8 sin seguimiento" y "226 enlaces".

---

## 19. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | *(pendiente)* |
| **Aprobado por** | *(pendiente — solo el usuario)* |
| **Expresión de aprobación** | `approved: Task/002-Definir-MVP-y-Arquitectura` |

> Esta tarea está **Lista para validación**. No está aprobada y no puede marcarse como
> aprobada sin autorización explícita del usuario.
