# STATUS — Estado del proyecto Blog Personal

**Última actualización:** 2026-08-15

---

## Vista rápida

| Campo | Valor |
| --- | --- |
| **Etapa actual** | ETAPA 02 — Fundaciones de las Aplicaciones — **En curso** (1 de 3 aprobadas). ETAPAS 00 y 01 **completadas** |
| **Tarea actual** | Ninguna en ejecución. `Task/005.4` **aprobada** y cerrada; `Task/006` **no iniciada** |
| **Estado de la tarea** | — |
| **Última tarea aprobada** | `Task/005-Fundacion-Backend-FastAPI` — **Aprobada** el 2026-08-12 por jeffersondavila; PR `#2` (backend) y `#6` (infra) **fusionados** el 2026-08-13 y normalizados |
| **Último mantenimiento aprobado** | `Task/005.4-Corregir-Base-Ramas-Task-Main` — **Aprobada** el 2026-08-15; PR `Task/005.4 → main` **abierto, sin fusionar**. **Primera tarea creada desde `main`.** No cuenta en las 41 tareas |
| **Mantenimiento anterior** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` — **Aprobada** el 2026-08-15; PR `#9` **fusionado**, merge `181c634`, normalizado |
| **Próxima tarea prevista** | `Task/006-Fundacion-Frontend-React` (Pendiente, **no iniciada**; **espera** la fusión del PR de `Task/005.4` y la normalización `main → dev`). **Nacerá desde `main`** |
| **Avance global** | **12 %** — 5 de 41 tareas aprobadas |
| **Bloqueos activos** | 0 |
| **Riesgos abiertos** | **33** (R-01 y **R-08** cerrados; **R-29** a **R-35** abiertos desde el 2026-08-15) |

> El avance se calcula **solo** con tareas `Aprobada`. `Task/005` ya cuenta: fue aprobada
> por el usuario el 2026-08-12.

---

## Última tarea aprobada

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005-Fundacion-Backend-FastAPI` |
| **Etapa** | ETAPA 02 — Fundaciones de las Aplicaciones |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-01 |
| **Fecha de aprobación** | 2026-08-12 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005-Fundacion-Backend-FastAPI` |
| **Repositorios afectados** | `personal-blog-backend` (implementación) · `personal-blog-infra` (gobierno documental) |
| **Ramas** | `Task/005-Fundacion-Backend-FastAPI` en ambos repositorios, creadas desde `dev`. **Publicadas en el cierre.** |
| **Alcance entregado** | Proyecto FastAPI con Python 3.12; estructura de monolito modular; configuración tipada fail-fast; log JSON **con marcas de tiempo UTC explícitas**; manejo centralizado de errores; `GET /health`; OpenAPI; SQLAlchemy 2 con psycopg 3; Alembic con migración fundacional; 69 pruebas; `ruff`, `mypy` *strict*; `Dockerfile` construido **sin cache** y ejecutado |
| **Primer código de aplicación** | Sí: es el primer código ejecutable de `personal-blog-backend` |
| **Validaciones** | 38 ejecutadas. 69 pruebas superadas y 1 omitida con motivo, **`pytest -W error` con 0 warnings y sin filtros**, cobertura 99 %, lint, formato y tipado sin errores, imagen construida con `--no-cache`, contenedor `healthy`, ciclo `upgrade`/`downgrade`/reaplicación verificado contra PostgreSQL real, logs UTC comprobados en Windows y en Docker |
| **Correcciones del 2026-08-11** | Revisión previa a la aprobación: **UTC real** en el log (antes dependía del sistema operativo), **advertencia de `TestClient` resuelta** sustituyendo `httpx` por `httpx2` en desarrollo, **rectificada** la afirmación errónea sobre la rotación de la contraseña de PostgreSQL en **R-16**, y confirmada la coherencia del `Dockerfile` con **R-14** |
| **Entorno local** | **Intacto.** No se ejecutó ninguna operación destructiva; los 3 volúmenes principales siguen presentes |
| **Integración en `dev`** | Merge `--no-ff` en ambos repositorios, publicado |
| **Pull request** | `Task/005 → main`: **`#2`** en backend (merge `db6ab18`) y **`#6`** en infra (merge `af8a04c`) — **fusionados por el usuario** el 2026-08-13 |
| **Normalización posterior** | Completada el 2026-08-13: `main` integrada en `dev` con merge `--no-ff` en ambos repositorios y publicada. `dev` = `ce4f1bc` (backend) y `5efd5e0` (infra) |
| **Rama Task** | Eliminada **local y remotamente**. La local con `git branch -d`; la remota, por el usuario desde GitHub |
| **Riesgos nuevos** | **R-14**, **R-15** y **R-16**, los tres **abiertos** |
| **Ficha** | [TASK-005](../tasks/TASK-005-fastapi-backend-foundation.md) |
| **Reporte** | [TASK-005-report](../task-reports/TASK-005-report.md) |

Con esta aprobación el avance global pasa a **5 de 41 (12 %)** y la **ETAPA 02** queda en
**1 de 3** tareas aprobadas.

---

## Tarea aprobada anterior

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/004-Backups-y-Recuperacion-Local` |
| **Etapa** | ETAPA 01 — Infraestructura Local |
| **Estado** | **Aprobada** |
| **Fecha de inicio** | 2026-07-31 |
| **Fecha de aprobación** | 2026-07-31 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/004-Backups-y-Recuperacion-Local` |
| **Repositorios afectados** | `personal-blog-infra` (únicamente) |
| **Rama de cierre** | `Task/004-Backups-y-Recuperacion-Local`, creada desde `dev` |
| **Alcance entregado** | 5 scripts PowerShell de backup, verificación, restauración aislada y limpieza; conjunto de respaldo con manifiesto y checksums SHA-256; inventario de **metadatos y tags** de MinIO y de **configuración de buckets**; runbook de backup y recuperación; `local-backups/` ignorado por Git |
| **Prueba de restauración** | **Ejecutada y superada** en entorno temporal aislado: PostgreSQL, MinIO (contenido, metadatos y tags) y Portainer |
| **Alcance en MinIO** | Versión **actual** de cada objeto: contenido, metadatos y tags. El **historial de versiones** queda fuera del alcance y la **configuración de los buckets** se registra pero no se reaplica; el script lo detecta y aborta salvo `-AllowPartial` |
| **Integración en `dev`** | Merge `--no-ff`, publicado |
| **Pull request** | `Task/004-Backups-y-Recuperacion-Local → main` (`#5`) — **fusionado** por el usuario el 2026-07-31, commit `c86d47e` |
| **Normalización posterior** | `main` integrada en `dev` mediante el merge `5f09e22` el 2026-08-01, al iniciar `Task/005` |
| **Rama Task** | Eliminada **local y remotamente** |
| **Riesgo cerrado** | **R-08** — el entorno local ya tiene copia externa a los volúmenes, verificada y restaurable |
| **Ficha** | [TASK-004](../tasks/TASK-004-local-backups-and-recovery.md) |
| **Reporte** | [TASK-004-report](../task-reports/TASK-004-report.md) |
| **Runbook producido** | [local-backup-and-recovery.md](../runbooks/local-backup-and-recovery.md) — **Vigente** |

Con esta aprobación **la ETAPA 01 queda completada** (2 de 2 tareas).

El PR `#5` fue fusionado por el usuario y la normalización `main → dev` se completó el
2026-08-01, lo que habilitó el inicio de `Task/005`.

---

## Tareas aprobadas previas

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/003-Crear-Infraestructura-Local` |
| **Estado** | **Aprobada y cerrada** |
| **Fecha de aprobación** | 2026-07-29 |
| **Pull request** | `Task/003-Crear-Infraestructura-Local → main` (`#4`) — **fusionado** el 2026-07-31, commit `966db01` |
| **Normalización posterior** | `main` integrada en `dev` mediante el merge `708a71e` |
| **Rama Task** | Eliminada local y remotamente |
| **Decisión promovida** | **D-05 → Resuelta**: Traefik v3 como reverse proxy local, a implementar en `Task/007` |
| **Runbook producido** | [local-environment.md](../runbooks/local-environment.md) — **Vigente** |

---

## Último mantenimiento aprobado

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.4-Corregir-Base-Ramas-Task-Main` |
| **Tipo** | **Mantenimiento de gobierno y workflow Git** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-15 |
| **Fecha de aprobación** | 2026-08-15 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.4-Corregir-Base-Ramas-Task-Main` |
| **Repositorios afectados** | `personal-blog-infra` **únicamente**, más el `CLAUDE.md` raíz del workspace |
| **Rama** | `Task/005.4-Corregir-Base-Ramas-Task-Main` |
| **Rama base** | **`main`** — **primera tarea del proyecto creada desde `main`** |
| **SHA base** | **`181c634`** (`= main = origin/main` en el momento de crearla). Verificado: `HEAD == main`, distinto de `dev` (`9dfbc10`) |
| **Problema corregido** | La documentación indicaba que las ramas Task debían crearse **desde `dev`**, e incluso prohibía explícitamente partir de `main`. Es incorrecto: `dev` acumula commits de integración que contaminan la ascendencia de una tarea nueva y pueden filtrarse al PR `Task → main` |
| **Invariante establecido** | **Toda rama `Task/<...>` nace desde `main` actualizado y limpio. `dev` NUNCA es base de una Task**; es exclusivamente rama de integración |
| **Qué NO cambia** | La palabra de aprobación, la integración `Task → dev`, el push de `dev`, la publicación de la rama Task, el PR `Task → main`, el merge manual del usuario y la normalización `main → dev`. **Solo cambia de dónde nace la rama** |
| **Alcance** | Gobierno y workflow **exclusivamente**. 0 cambios de arquitectura, 0 implementación |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global y ETAPA 02 **sin cambios** |
| **Historial de tareas anteriores** | **No se reescribe.** `Task/002`–`Task/005.3` nacieron de `dev` por la regla incorrecta; sus fichas y reportes se conservan como registro histórico |
| **Integración en `dev`** | Merge `--no-ff`, publicado |
| **Pull request** | `Task/005.4-Corregir-Base-Ramas-Task-Main → main` — **abierto, sin fusionar**. La fusión es responsabilidad del usuario |
| **Rama Task** | Eliminada **localmente** con `git branch -d`; **conservada en `origin`** mientras el PR siga abierto |
| **Ficha** | [TASK-005.4](../tasks/TASK-005.4-correct-task-branch-base-main.md) |
| **Reporte** | [TASK-005.4-report](../task-reports/TASK-005.4-report.md) |

La aprobación de este mantenimiento **no modifica el conteo del roadmap**: el avance global
permanece en **5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas.

Con ella, el **invariante de ramas** queda **vigente y de cumplimiento obligatorio**:
**toda rama `Task/<...>` nace desde `main` actualizado y limpio; `dev` nunca es base de una
Task.** `Task/006` sigue **Pendiente y no iniciada**, y **nacerá desde `main`**.

---

## Mantenimiento aprobado anterior — `Task/005.3`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` |
| **Tipo** | **Mantenimiento de arquitectura y gobierno documental** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-15 |
| **Fecha de aprobación** | 2026-08-15 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` |
| **Repositorios afectados** | `personal-blog-infra` **únicamente** |
| **Rama** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS`, creada desde `dev` (`a563de6`). **Publicada en el cierre** |
| **Objetivo** | Cambiar el destino de la capa de datos de producción: de **PostgreSQL administrado** a **PostgreSQL autogestionado en un VPS externo**, con **PgBouncer** delante, manteniendo FastAPI en **AWS Lambda** |
| **Motivación** | **Costo** —evitar que la base de datos domine la factura de una arquitectura que escala a cero— más aprendizaje operacional real y mayor control |
| **Alcance entregado** | Documento canónico [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) (**Vigente**); [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) (**Aceptada**); **D-01 Resuelta** en cuanto al modelo; `Task/029` redefinida conservando su ID; nueva §9 y componentes **C-13**, **C-14**, **C-15** en límites de seguridad; **PRODUCTION DATABASE LAW** en `PROJECT_INSTRUCTIONS.md` §16; actualización de ETAPA 08, ETAPA 09, mapping, paridad AWS y README |
| **Qué NO cambia** | FastAPI sigue en **Lambda**; API Gateway, S3, SSM, CloudWatch, IAM, Terraform, Floci y Cloudflare Pages **sin cambios**; el entorno local **sin cambios** |
| **Implementación** | **Ninguna.** 0 VPS contratados, 0 PostgreSQL instalado, 0 PgBouncer instalado, 0 archivos Terraform, 0 recursos AWS, 0 RDS, 0 NAT Gateway, 0 cambios en backend, frontend y Docker Compose |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global y ETAPA 02 **sin cambios** |
| **Decisiones que NO resuelve** | Proveedor, región y tamaño del VPS (`Task/029`); **D-06** (backend de estado de Terraform, `Task/025`); tamaños de pool y `max_connections`; frecuencia y retención de backups (**D-10**); si se adopta mTLS; si se implementa PITR |
| **Riesgos nuevos** | **R-29** a **R-35**, los siete **abiertos** |
| **Imagen de arquitectura** | `images/Infraestructura.png` **intacta**: no modificada, no regenerada, no movida, no reemplazada. Pasa a tratarse como *arquitectura objetivo inicial, anterior a esta decisión* |
| **Integración en `dev`** | Merge `--no-ff`, publicado |
| **Pull request** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS → main` (**`#9`**) — **FUSIONADO** por el usuario. Merge commit **`181c634`**, `mergedAt = 2026-08-16T03:56:08Z` (UTC) |
| **Rama Task** | Eliminada **local y remotamente**. La local con `git branch -d` en el cierre; la remota, por el usuario desde GitHub |
| **Normalización posterior** | **Completada el 2026-08-15.** `main` = `181c634`; `main` integrada en `dev` con merge `--no-ff` **`9dfbc10`**, publicado. `git diff main dev` vacío y `main` es ancestro de `dev` |
| **Ficha** | [TASK-005.3](../tasks/TASK-005.3-define-production-postgresql-vps.md) |
| **Reporte** | [TASK-005.3-report](../task-reports/TASK-005.3-report.md) |

La aprobación de este mantenimiento **no modifica el conteo del roadmap**: el avance global
permanece en **5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas.

Con ella, `ADR-007` pasa a **Aceptada**, **D-01** a **Resuelta** en cuanto al **modelo**
—el proveedor sigue en `Task/029`—, `production-postgresql-vps.md` y la **PRODUCTION
DATABASE LAW** pasan a **vigentes**, y los riesgos **R-29** a **R-35** a **Abiertos**.
`Task/006` sigue **Pendiente y no iniciada**.

---

## Mantenimiento aprobado previo — `Task/005.2`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` |
| **Tipo** | **Mantenimiento de arquitectura y gobierno documental** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-15 |
| **Fecha de aprobación** | 2026-08-15 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.2-Documentar-Estrategia-Floci-IaC-Local` |
| **Repositorios afectados** | `personal-blog-infra` **únicamente** |
| **Rama** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local`, creada desde `dev` normalizado (`4e6bfaa`). **Publicada en el cierre** |
| **Objetivo** | Formalizar que la infraestructura AWS pueda desarrollarse, aprenderse, provisionarse y destruirse **localmente** antes de gastar en AWS real, con **una sola definición de Terraform** para ambos destinos |
| **Alcance entregado** | Documento canónico [aws-local-parity.md](../architecture/aws-local-parity.md) (**Vigente**); [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) (**Aceptada**); matriz de paridad inicial (entera en `No evaluada`); decisión **D-14 Resuelta**; ampliación del alcance futuro de la ETAPA 08 y de `Task/023`–`Task/026`; reutilización de módulos en la ETAPA 10; encaje del laboratorio en `Task/039`; componente **C-12** y §8 en límites de seguridad; ley compacta en `PROJECT_INSTRUCTIONS.md` §15 |
| **Verificación de Floci** | 2026-08-15, **solo fuentes oficiales** (repositorio y documentación del proyecto). Sin blogs ni terceros |
| **Implementación** | **Ninguna.** 0 archivos Terraform, 0 cambios en Docker Compose, Floci **no instalado**, sin imágenes descargadas, sin contenedores, sin recursos AWS, sin cuentas |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global y ETAPA 02 **sin cambios** |
| **Decisiones que NO resuelve** | **D-01** (PostgreSQL administrado, `Task/029`) y **D-06** (backend de estado de Terraform, `Task/025`), ambas **siguen abiertas** |
| **Riesgos nuevos** | **R-19** a **R-28**, los diez **abiertos** |
| **Imagen de arquitectura** | `images/Infraestructura.png` **intacta**: no modificada, no regenerada, no movida, no reemplazada |
| **Integración en `dev`** | Merge `--no-ff` **`a61ecbf`**, publicado |
| **Pull request** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local → main` (**`#8`**) — **FUSIONADO** por el usuario. Merge commit **`5583947`**, `mergedAt = 2026-08-16T01:23:02Z` (UTC) |
| **Rama Task** | Eliminada **local y remotamente**. La local con `git branch -d` durante el cierre; la remota, por el usuario desde GitHub |
| **Normalización posterior** | **Completada por el usuario.** `main` = `5583947`; `dev` = `a563de6` (`Merge branch 'main' into dev`), publicado. `git diff main dev` vacío y `main` contenida en `dev`. Verificado el 2026-08-15 al iniciar `Task/005.3` |
| **Ficha** | [TASK-005.2](../tasks/TASK-005.2-document-floci-local-iac-strategy.md) |
| **Reporte** | [TASK-005.2-report](../task-reports/TASK-005.2-report.md) |

La aprobación de este mantenimiento **no modifica el conteo del roadmap**: el avance global
permanece en **5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas.

Con ella, `ADR-006` pasa a **Aceptada**, **D-14** a **Resuelta** y los riesgos **R-19** a
**R-28** a **Abiertos**. `Task/006` sigue **Pendiente y no iniciada**: no comienza hasta que
el usuario fusione el PR de `Task/005.2` y se complete la normalización `main → dev`.

---

## Mantenimiento aprobado previo — `Task/005.1`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.1-Formalizar-TDD-Backend` |
| **Tipo** | Mantenimiento de gobierno documental |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-13 |
| **Fecha de aprobación** | 2026-08-13 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.1-Formalizar-TDD-Backend` |
| **Repositorios afectados** | `personal-blog-infra` **únicamente** |
| **Rama** | `Task/005.1-Formalizar-TDD-Backend`, creada desde `dev`. **Publicada en el cierre** |
| **Alcance entregado** | Práctica **test-first** obligatoria del backend: documento canónico [BACKEND_TESTING_STRATEGY](BACKEND_TESTING_STRATEGY.md); ley compacta en `PROJECT_INSTRUCTIONS.md` §14; criterios **B-1 a B-12** en la Definition of Done; sección *TDD / Plan test-first* en la plantilla de tareas; política reflejada en ROADMAP y ETAPA 03 para `Task/008`–`Task/012` |
| **Regla central** | **RED → GREEN → REFACTOR**, con matriz de casos previa y evidencia de RED y GREEN en el reporte de cada tarea de backend funcional |
| **Código modificado** | **Ninguno.** 0 cambios en backend y frontend, 0 dependencias nuevas |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global y ETAPA 02 **sin cambios** |
| **Riesgos nuevos** | **R-17** y **R-18** |
| **Asset versionado en el cierre** | `images/Infraestructura.png` — diagrama de la arquitectura objetivo inicial, **preexistente**, agregado por el usuario el 2026-07-26 y autorizado explícitamente para versionarse en este cierre. **No es un entregable de la tarea** y no se modificó |
| **Integración en `dev`** | Merge `--no-ff`, publicado |
| **Pull request** | `Task/005.1-Formalizar-TDD-Backend → main` (**`#7`**) — **FUSIONADO** por el usuario. Merge commit **`2f56a13`**, `mergedAt = 2026-08-16T00:25:21Z` (UTC) |
| **Rama Task** | Eliminada **local y remotamente**. La local con `git branch -d` durante el cierre; la remota, por el usuario desde GitHub. Verificado: `git ls-remote --heads origin "Task/*"` no devuelve nada |
| **Normalización posterior** | **Completada el 2026-08-15.** `main` = `2f56a13`; `main` integrada en `dev` con merge `--no-ff` **`4e6bfaa`**, publicado. `git diff main dev` vacío y `2f56a13` es ancestro de `dev` |
| **Ficha** | [TASK-005.1](../tasks/TASK-005.1-formalize-backend-tdd.md) |
| **Reporte** | [TASK-005.1-report](../task-reports/TASK-005.1-report.md) |

La aprobación de este mantenimiento **no modifica el conteo del roadmap**: el avance global
permanece en **5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas.

---

## Mantenimiento de gobierno anterior

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/002.1-Configurar-Claude-Code` |
| **Tipo** | Mantenimiento de gobierno |
| **Estado** | **Aprobada y cerrada** |
| **Fecha de aprobación** | 2026-07-26 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/002.1-Configurar-Claude-Code` |
| **Rama de cierre** | `Task/002.1-Configurar-Claude-Code` |
| **Pull request** | `Task/002.1-Configurar-Claude-Code → main` — **fusionado** por el usuario (commit `dbb41aa`) |
| **Normalización posterior** | `main` integrada en `dev` mediante el merge `cca847c`; ambas ramas con contenido idéntico |
| **Rama Task** | Eliminada local y remotamente |
| **Roadmap** | No cuenta dentro de las 41 tareas |
| **Avance global** | Permanece en **2 de 41**, aproximadamente **5 %** |
| **Bloqueos activos** | Ninguno |

La aprobación de este mantenimiento no modificó el conteo del roadmap. La
normalización `main → dev` se completó, lo que habilitó el inicio de `Task/003`.

---

## Resumen del avance

| Etapa | Tareas | Aprobadas | Avance |
| --- | --- | --- | --- |
| 00 — Fundación y Gobierno | 2 | 2 | **100 %** |
| 01 — Infraestructura Local | 2 | 2 | **100 %** |
| 02 — Fundaciones de las Aplicaciones | 3 | 1 | **33 %** — **en curso** |
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
| **Total** | **41** | **5** | **12 %** |

Distribución por estado:

| Estado | Tareas |
| --- | --- |
| Pendiente | 36 |
| En progreso | 0 |
| Lista para validación | 0 |
| **Aprobada** | **5** |
| Bloqueada | 0 |
| Descartada | 0 |

> Esta distribución incluye únicamente las 41 tareas del roadmap. La tarea de
> mantenimiento `Task/002.1` se registra por separado.

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
| R-03 | La elección de la base de datos de producción condiciona el diseño de conexiones desde Lambda (pooling, límites). | Medio | Evaluar en `Task/029` y considerar el patrón de conexión desde `Task/005`. **Actualización propuesta el 2026-08-15 (`Task/005.3`):** con PostgreSQL en un VPS, la mitigación concreta pasa a ser **PgBouncer** con pool limitado más *Reserved Concurrency* de Lambda; ver **R-33**. | Abierto |
| R-04 | El roadmap de 41 tareas puede quedar desactualizado si el alcance cambia. | Bajo | `STATUS.md` y `ROADMAP.md` se actualizan en cada cambio de estado, como parte de la Definition of Done. | Abierto |
| R-05 | Los enlaces cruzados entre repositorios asumen que los tres están clonados como carpetas hermanas. | Bajo | Suposición documentada en los README de frontend y backend; alternativa futura: enlazar a las URL de GitHub. | Abierto |
| R-06 | El alcance del MVP puede crecer durante la implementación. | Medio | [MVP_SCOPE.md](../product/MVP_SCOPE.md) §6 lista explícitamente lo excluido; toda incorporación exige un ADR que reemplace la decisión vigente. | Abierto |
| R-07 | El render de Markdown en el cliente puede resultar insuficiente para SEO. | Medio | Metadatos, Open Graph, canonical, sitemap y datos estructurados en `Task/016`; si no basta, se reconsidera [ADR-005](../adr/ADR-005-markdown-content.md). | Abierto |
| R-08 | El entorno local no tiene copia de seguridad: `docker compose down -v` destruye la base de datos y los objetos de MinIO sin recuperación posible. | Alto | **Resuelto** por `Task/004`, aprobada el 2026-07-31: existe un procedimiento de respaldo con integridad verificada por SHA-256 y **restauración demostrada** en entorno aislado para los tres servicios, incluidos metadatos y tags de MinIO. Ver [runbook de backup](../runbooks/local-backup-and-recovery.md). Queda el riesgo residual **R-11**. | **Cerrado** (2026-07-31) |
| R-11 | El backup es **manual**: si nadie lo ejecuta, se pierde todo lo hecho desde la última copia. | Medio | Política de retención en el [runbook](../runbooks/local-backup-and-recovery.md) §11, que exige backup antes de toda operación destructiva. La automatización programada queda fuera del alcance de `Task/004`. | Abierto |
| R-12 | Los artefactos de respaldo son sensibles —incluyen los hashes de autenticación de Portainer— y se guardan **sin cifrar** en el equipo. | Medio | `local-backups/` ignorado por Git y documentado como sensible en el runbook, en `scripts/backup/README.md` y en el `.gitignore`. El cifrado queda fuera del alcance; se revisará en `Task/018`. | Abierto |
| R-13 | La copia de Portainer exige detener su contenedor: una interrupción anómala podría dejarlo parado. | Bajo | El arranque está dentro de un bloque `finally`: se ejecuta aunque la copia falle. Si aun así quedara parado, `docker start personal-blog-local-portainer` lo resuelve. | Abierto |
| R-09 | Portainer tiene acceso al socket del daemon de Docker y conserva **capacidad administrativa sobre el host**: puede crear, detener, eliminar y modificar contenedores, redes y volúmenes de este y de cualquier otro proyecto de la máquina. El montaje `:ro` protege el **archivo** del socket pero **no** convierte la Docker API en solo lectura, y la separación de redes **no** limita las acciones enviadas por el daemon. Agravante: conviven dos instancias de Portainer sobre el mismo daemon. | **Medio** | El riesgo se acepta únicamente porque Portainer es **local**, se publica en **`127.0.0.1`** y exige **autenticación propia**. **Regla vigente: no exponerlo nunca** a la red local ni a internet. Un control real de solo lectura exigiría un **socket proxy** o una política de autorización adicional, fuera del alcance de `Task/003`; se propone evaluarlo en `Task/018`. Detalle: [runbook §2.1](../runbooks/local-environment.md). | Abierto |
| R-10 | Las etiquetas de imagen fijadas envejecen y acumulan vulnerabilidades sin corregir. | Medio | Escaneo de imágenes en `Task/018-Endurecimiento-de-Seguridad`; validación del Compose en cada cambio en `Task/021-CI-Infraestructura`. | Abierto |
| R-14 | Las dependencias **transitivas** del backend no están bloqueadas: dos instalaciones en fechas distintas pueden traer versiones indirectas distintas. **Comprobado el 2026-08-11:** la imagen resolvió `starlette 1.6.0` y el entorno de Windows, instalado el 2026-08-01, tiene `starlette 1.3.1`. | Medio | Las dependencias directas están fijadas con `==` en `pyproject.toml` y `requirements.txt`, y `pip check` forma parte de las validaciones. Mientras el riesgo siga abierto, el `Dockerfile` instala con `pip install -r requirements.txt`, **sin `--require-hashes` ni `--no-deps`**, que serían incoherentes con un archivo sin hashes y sin transitivas. El bloqueo completo con hashes, resuelto en Linux, se añade en `Task/020-CI-Backend`. | Abierto (`Task/005`) |
| R-15 | La imagen base del backend (`python:3.12.13-slim`) envejece y acumula vulnerabilidades sin corregir. | Medio | Misma naturaleza que R-10. Escaneo de la imagen en `Task/018` y verificación en CI en `Task/020`. | Abierto (`Task/005`) |
| R-17 | Una práctica escrita puede no aplicarse: el ciclo **RED → GREEN** es fácil de saltarse si nadie exige la evidencia, y las pruebas acabarían escribiéndose después del código. | Medio | La evidencia de RED y GREEN es un **criterio de la Definition of Done** (B-2 y B-3), no una recomendación: sin ella la tarea no puede marcarse `Lista para validación`. `Task/020-CI-Backend` podrá reforzarlo automáticamente. Detectado en `Task/005.1`. | Abierto |
| R-18 | El coste de escribir primero la prueba puede empujar a **matrices superficiales** que aparenten cumplimiento sin cubrir edge cases ni casos negativos. | Bajo | La matriz obligatoria exige explícitamente edge cases, errores y seguridad ([BACKEND_TESTING_STRATEGY](BACKEND_TESTING_STRATEGY.md) §6), y la revisión del usuario es el control final. Detectado en `Task/005.1`. | Abierto |
| R-16 | El `.env` real del entorno local **conserva las contraseñas de ejemplo** `change-me-local-postgres` y `change-me-local-minio`, publicadas en `.env.example` desde `Task/003`: las credenciales locales de PostgreSQL y MinIO son, de hecho, públicas. | **Bajo** | Acotado porque los tres servicios se publican solo en `127.0.0.1` y no son alcanzables desde la red. Rotar la contraseña de PostgreSQL **no exige recrear el volumen ni la base**: se cambia la del rol existente con `ALTER ROLE` y se actualiza el `.env` de forma coordinada — procedimiento completo en el [reporte de `Task/005`](../task-reports/TASK-005-report.md) §6.1. **MinIO se trata por separado:** su credencial raíz procede de variables de entorno del contenedor, no de un rol almacenado, por lo que su rotación **no** sigue el mismo procedimiento. La rotación **queda a decisión del usuario** y no se ejecutó en `Task/005`. Detectado en `Task/005`. | Abierto |

### Riesgos introducidos por `Task/005.2` — AWS Local Parity

> **Abiertos y vigentes** desde la aprobación de `Task/005.2` el 2026-08-15. Ninguno está
> cerrado. Detalle completo:
> [aws-local-parity.md](../architecture/aws-local-parity.md) §14.

| # | Riesgo | Impacto | Mitigación prevista | Tarea que lo valida | Estado |
| --- | --- | --- | --- | --- | --- |
| R-19 | El comportamiento del emulador AWS local difiere del de AWS real en detalles que solo aparecerían en producción. | Medio | La matriz de paridad nace entera en `No evaluada`; toda diferencia observada se registra; **AWS real es la autoridad final**. | `Task/025` → ETAPA 10 | **Abierto** |
| R-20 | **Falsa sensación de paridad:** un laboratorio en verde convence de que la nube funcionará, y la ETAPA 10 se aborda con exceso de confianza. | **Alto** | El estado «paridad completa» **no existe** en la matriz, a propósito. Vocabulario obligatorio que distingue *emulado* de *validado*. La pregunta «¿qué diferencia hay respecto a AWS real?» es obligatoria en cada bloque de infraestructura. | ETAPA 10 | **Abierto** |
| R-21 | Una actualización del emulador rompe la compatibilidad ya validada. | Medio | Versión **fijada**, nunca `latest` ni `nightly`. Actualizar se trata como cambio de infraestructura: revisar CHANGELOG y revalidar la matriz. | `Task/025`, `Task/026` | **Abierto** |
| R-22 | El emulador necesita **acceso al socket de Docker** para ejecutar Lambda: privilegio de nivel host, junto a Portainer. **Agrava R-09.** | **Alto** | Mismo tratamiento que **R-09**: solo local, nunca expuesto, compromiso = incidente de nivel **host**. Revisión del *networking* de Docker antes de implementar. Componente **C-12** en [security-boundaries](../architecture/security-boundaries.md) §8. | `Task/025`, `Task/018` | **Abierto** |
| R-23 | El endpoint local (puerto 4566 y rangos auxiliares) queda expuesto a la LAN o a internet por descuido. | **Alto** | Publicación restringida a `127.0.0.1`; prohibición explícita de exponerlo; verificación incluida en los runbooks de `Task/026`. | `Task/025`, `Task/026` | **Abierto** |
| R-24 | Un comando pensado para el laboratorio acaba ejecutándose **contra AWS real** por faltar el endpoint, o se usan credenciales AWS reales contra el emulador. Un `destroy` en ese estado sería el fallo más caro posible. | **Alto** | Guardas ***fail-closed*** obligatorias antes del primer `apply`: entorno explícito, endpoint explícito, verificación de *account id*, rechazo de credenciales reales y validación bloqueante del destino. Prohibido usar credenciales AWS reales contra el emulador. | `Task/025`, `Task/026` | **Abierto** |
| R-25 | El **camino crítico del proyecto** —Terraform + API Gateway v2 + Lambda + CloudWatch Logs— **no está cubierto por la suite oficial de compatibilidad Terraform del emulador**, verificado el 2026-08-15. Los servicios están documentados por separado; su combinación con Terraform no está demostrada upstream. | **Alto** | Es el objetivo explícito de `Task/025`. Si no se logra con fidelidad suficiente, esos recursos pasan a `AWS-only` en la matriz y se documenta la limitación, **sin fabricar sustitutos locales**. | `Task/025` | **Abierto** |
| R-26 | Acumular condicionales por entorno acaba creando **dos IaC distintas** disfrazadas de una sola. | Medio | Tabla **cerrada** de diferencias legítimas ([aws-local-parity](../architecture/aws-local-parity.md) §4.4). Cualquier diferencia fuera de ella se trata como defecto de diseño, no como configuración. | `Task/025`, revisión del usuario | **Abierto** |
| R-27 | Dependencia excesiva del emulador: se aplaza indefinidamente la validación contra AWS real. | Medio | El laboratorio es una **puerta**, no un destino. La ETAPA 10 sigue siendo obligatoria y sus criterios de salida no se relajan. | ETAPA 10 | **Abierto** |
| R-28 | **El emulador no aplica políticas IAM por omisión**: acepta cualquier credencial y deja pasar toda petición. Un rol puede validarse en local y ser incorrecto —insuficiente o excesivo— en AWS. | **Alto** | El laboratorio valida que un rol **se crea y se adjunta**, nunca que **autoriza**. La verificación de **mínimo privilegio** queda declarada **AWS-only**. | `Task/028`, `Task/032` | **Abierto** |

### Riesgos introducidos por `Task/005.3` — PostgreSQL de producción en VPS

> **Abiertos y vigentes** desde la aprobación de `Task/005.3` el 2026-08-15. **Ninguno está
> cerrado**: son consecuencia asumida de la decisión, no defectos pendientes. Detalle
> completo:
> [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) §16.

| # | Riesgo | Impacto | Mitigación prevista | Tarea que lo valida | Estado |
| --- | --- | --- | --- | --- | --- |
| R-29 | ***Single point of failure*.** Un solo VPS: si cae el host, el blog pierde su base de datos y queda sin contenido dinámico hasta la recuperación manual. | Medio | **Aceptado conscientemente.** Mitigado con backups fuera del host, restore probado, infraestructura reproducible y runbook de recuperación. **No se introduce alta disponibilidad**: su costo y complejidad no se justifican para un blog personal. | `Task/029`, `Task/026` | **Abierto** |
| R-30 | **Nueva superficie de ataque expuesta a Internet:** PgBouncer publicado y SSH en el host, más software —SO, PostgreSQL, PgBouncer— que envejece y acumula vulnerabilidades sin parchear. **El compromiso del VPS implica exposición de todos los datos del blog.** | **Alto** | Firewall *deny-by-default*; SSH solo por llave; servicios mínimos; **PostgreSQL nunca público**; TLS obligatorio con validación de certificado y **SCRAM-SHA-256**; política de parcheo definida en `Task/029`. Prohibido apoyarse en *security through obscurity*. Ver [security-boundaries](../architecture/security-boundaries.md) §9. | `Task/029`, `Task/018` | **Abierto** |
| R-31 | **Backup inexistente, corrupto o no restaurable.** El fallo silencioso clásico: existe un archivo, nadie lo ha restaurado nunca y el día del incidente no sirve. | **Alto** | Regla obligatoria: **un backup no está validado hasta haberse restaurado**. Verificación de integridad, restore en entorno controlado y procedimiento documentado — mismo estándar que `Task/004` alcanzó en local. | `Task/029`, `Task/026` | **Abierto** |
| R-32 | **Pérdida del VPS o del disco**, o **agotamiento de recursos**: un disco lleno detiene PostgreSQL y puede impedir el propio backup. | **Alto** | Backups **fuera del host** — una copia que solo vive en el VPS no protege de esto. Monitoreo de espacio y de recursos con alertas; dimensionamiento y política de crecimiento en `Task/029`. | `Task/029`, `Task/017` | **Abierto** |
| R-33 | **Agotamiento de conexiones**: una ráfaga de concurrencia de Lambda supera `max_connections` de PostgreSQL. Es la materialización de **R-03** en esta topología. | Medio | **PgBouncer** con pool limitado más ***Reserved Concurrency*** de Lambda aguas arriba. Los tres números —concurrencia, pool y `max_connections`— se derivan de **pruebas**, no de intuición. | `Task/029`, `Task/032` | **Abierto** |
| R-34 | **Latencia `Lambda ↔ VPS`.** La base de datos deja de estar en la misma región que el cómputo; cada consulta paga el RTT y una petición HTTP suele hacer varias. | Medio | Selección de región del VPS teniendo en cuenta la región AWS, con **RTT medido**, no estimado. Regla explícita: no elegir un VPS lejano por ahorrar poco al mes. | `Task/029`, `Task/040` | **Abierto** |
| R-35 | **Error humano de operación.** Sin consola administrada que ponga barreras, un comando equivocado puede borrar datos, exponer un puerto o dejar el servicio caído. | Medio | Infraestructura reproducible con Terraform; runbooks escritos para cada operación; backups fuera del host como red de seguridad; regla vigente de no ejecutar operaciones destructivas sin autorización explícita. | `Task/026`, `Task/029` | **Abierto** |

---

## Tabla completa de tareas

| Tarea | Etapa | Repos | Estado |
| --- | --- | --- | --- |
| `Task/001-Inicializar-Workspace-y-Roadmap` | 00 | infra, frontend, backend | **Aprobada** |
| `Task/002-Definir-MVP-y-Arquitectura` | 00 | infra | **Aprobada** |
| `Task/003-Crear-Infraestructura-Local` | 01 | infra | **Aprobada** |
| `Task/004-Backups-y-Recuperacion-Local` | 01 | infra | **Aprobada** |
| `Task/005-Fundacion-Backend-FastAPI` | 02 | backend, infra (documentación) | **Aprobada** |
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
| `Task/029-Preparar-PostgreSQL-Produccion-en-VPS` | 09 | infra | Pendiente |
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

Estado verificado el **2026-08-15**.

| Repositorio | Ramas locales | Ramas remotas | Rama activa | `main` y `dev` sincronizadas |
| --- | --- | --- | --- | --- |
| `personal-blog-infra` | `main`, `dev` — la rama Task se eliminó localmente en el cierre | `main`, `dev`, `origin/Task/005.4-Corregir-Base-Ramas-Task-Main` (**con PR abierto**) | `main` | **No todavía** — se normaliza cuando el usuario fusione el PR de `Task/005.4` |
| `personal-blog-frontend` | `main` (`144a401`), `dev` (`8823cc3`) | `main`, `dev` | `main` | Sí — sin cambios |
| `personal-blog-backend` | `main` (`db6ab18`), `dev` (`ce4f1bc`) | `main`, `dev` | `main` | Sí — normalizadas el 2026-08-13 con el merge `ce4f1bc` |

- `main` y `dev` están **publicadas** en GitHub en los tres repositorios y
  contienen el mismo contenido.
- Las ramas `Task/001-Inicializar-Workspace-y-Roadmap` fueron **eliminadas** local y
  remotamente tras integrarse mediante los pull requests `#1`.
- Los PR de `Task/001` se integraron desde la rama `Task/001` directamente hacia `main`,
  lo que dejó `main` y `dev` con el mismo contenido pero distintos commits de merge. Esa
  divergencia formal se **normalizó al inicio de `Task/002`** con un merge `--no-ff` de
  `origin/main` dentro de `dev`, publicado en los tres repositorios.
- `Task/002` se ejecutó **solo en `personal-blog-infra`**. Tras su aprobación se
  integró en `dev`; el PR `#2` histórico usó `dev → main`, fue fusionado por el
  usuario y después se normalizó `dev`.
- A partir de `Task/002.1`, el flujo vigente cambia: cada PR de cierre debe usar
  `Task/<nombre> → main`; `dev → main` deja de ser el flujo ordinario.
- `Task/002.1-Configurar-Claude-Code` fue aprobada explícitamente por el usuario.
  Su PR `#3` fue **fusionado** por el usuario (commit `dbb41aa`) y la rama Task se
  eliminó local y remotamente. La normalización posterior integró `main` en `dev`
  mediante el merge `cca847c`.
- `Task/003-Crear-Infraestructura-Local` se creó desde `dev` **solo en
  `personal-blog-infra`**: la tarea no modifica frontend ni backend.
- `Task/003` fue **aprobada** el 2026-07-29. Su PR `#4` fue **fusionado** por el usuario el
  2026-07-31 (commit `966db01`), la rama Task se eliminó local y remotamente, y la
  normalización posterior integró `main` en `dev` mediante el merge `708a71e`.
- `Task/004-Backups-y-Recuperacion-Local` se creó desde `dev` **solo en
  `personal-blog-infra`**: la tarea no modifica frontend ni backend. Fue **aprobada** el
  2026-07-31; su cierre la integró en `dev` con merge `--no-ff`, publicó la rama Task y
  abrió el PR `Task/004 → main`. El usuario **fusionó** ese PR (`#5`, commit `c86d47e`) y
  eliminó la rama remota. La rama Task ya no existe ni local ni remotamente.
- La **normalización posterior** se ejecutó el 2026-08-01: `main` se integró en `dev` con el
  merge `5f09e22` y se publicó. `dev` y `main` tienen ahora el mismo contenido y el commit
  de `main` forma parte del historial de `dev`.
- `Task/005-Fundacion-Backend-FastAPI` se creó el 2026-08-01 desde `dev` en
  **`personal-blog-backend`** (implementación) y en **`personal-blog-infra`** (solo
  documentación de gobierno). Fue **aprobada** el 2026-08-12; su cierre creó los commits,
  integró la rama en `dev` con merge `--no-ff`, publicó `dev` y la rama Task, y abrió el
  pull request `Task/005 → main` en cada repositorio. **Los PR siguen abiertos**: fusionarlos
  es responsabilidad del usuario. La rama Task local se eliminó con `git branch -d`.
- **No se creó rama `Task/005` en `personal-blog-frontend`**: la tarea no lo modifica. El
  frontend permanece en `main`, con el árbol limpio.
- **Normalización completada el 2026-08-13.** El usuario fusionó los PR `#2` (backend, merge
  `db6ab18`) y `#6` (infra, merge `af8a04c`) y eliminó las ramas remotas. Después se integró
  `main` en `dev` con merge `--no-ff` en ambos repositorios y se publicó: `main` y `dev`
  tienen el mismo contenido y el commit de merge de `main` forma parte del historial de `dev`.
- `Task/005.1-Formalizar-TDD-Backend` se creó el 2026-08-13 desde `dev` **solo en
  `personal-blog-infra`**. Es mantenimiento documental, **no cuenta** en las 41 tareas y no
  modifica ningún otro repositorio. Fue **aprobada** el 2026-08-13; su cierre creó el commit,
  integró la rama en `dev` con merge `--no-ff`, publicó `dev` y la rama Task, y abrió el
  pull request `Task/005.1 → main`. La rama Task local se eliminó con `git branch -d`.
- El diagrama `images/Infraestructura.png`, **preexistente y agregado por el usuario**, se
  versionó durante ese cierre con su autorización explícita. No es un entregable de
  `Task/005.1` y no se modificó. **Versionar un diagrama no crea ningún recurso cloud.**
- **PR `#7` fusionado y normalización completada (2026-08-15).** El usuario fusionó
  `Task/005.1 → main` (merge commit **`2f56a13`**, `mergedAt = 2026-08-16T00:25:21Z` UTC) y
  eliminó la rama remota. Verificado con `gh pr view 7` y con
  `git ls-remote --heads origin "Task/*"`, que **no devuelve ninguna rama**. Después se
  integró `main` en `dev` con el merge `--no-ff` **`4e6bfaa`** y se publicó: `git diff main dev`
  está **vacío** y `2f56a13` es **ancestro de `dev`**.
- **Backend y frontend verificados el 2026-08-15**, sin modificarlos: `fetch --prune`,
  `main` y `dev` ya al día, `dev..main` **vacío** en ambos, `git diff main dev` **vacío**,
  árboles limpios y rama activa `main`. **No se creó rama `Task/005.2` en ninguno de los
  dos:** la tarea no los modifica.
- `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` se creó el 2026-08-15 desde `dev`
  normalizado (`4e6bfaa`), **solo en `personal-blog-infra`**. Es mantenimiento de
  arquitectura y gobierno documental: **no cuenta** en las 41 tareas y **no altera el
  avance**. Fue **aprobada** el 2026-08-15; su cierre creó el commit, integró la rama en
  `dev` con merge `--no-ff` (`a61ecbf`), publicó `dev` y la rama Task, y abrió el pull
  request `Task/005.2 → main` (**`#8`**). La rama Task local se eliminó con `git branch -d`.
- **PR `#8` fusionado y normalización completada (2026-08-15), por el usuario.** Merge commit
  **`5583947`**, `mergedAt = 2026-08-16T01:23:02Z` UTC; rama remota eliminada. El usuario
  sincronizó `main` y `dev` y publicó `dev` (`a563de6`, `Merge branch 'main' into dev`).
  **Verificado el 2026-08-15 al iniciar `Task/005.3`:** `gh pr view 8` devuelve `MERGED`,
  `git ls-remote --heads origin "Task/*"` **no devuelve nada**, `dev..main` está **vacío** y
  `git diff main dev` está **vacío**.
- **Backend y frontend verificados de nuevo el 2026-08-15**, sin modificarlos: `fetch --prune`,
  `main` y `dev` al día, `dev..main` **vacío** en ambos, `git diff main dev` **vacío**, árboles
  limpios y rama activa `main`. **No se creó rama `Task/005.3` en ninguno de los dos.**
- `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` se creó el 2026-08-15 desde `dev`
  normalizado (**`a563de6`**), **solo en `personal-blog-infra`**. Es mantenimiento de
  arquitectura y gobierno documental: **no cuenta** en las 41 tareas y **no altera el
  avance**. Fue **aprobada** el 2026-08-15; su cierre creó el commit, integró la rama en
  `dev` con merge `--no-ff` (`bf31ebc`), publicó `dev` y la rama Task, y abrió el pull
  request `Task/005.3 → main` (**`#9`**). La rama Task local se eliminó con `git branch -d`.
- **PR `#9` fusionado y normalización completada (2026-08-15).** El usuario fusionó
  `Task/005.3 → main` (merge commit **`181c634`**, `mergedAt = 2026-08-16T03:56:08Z` UTC) y
  eliminó la rama remota. Verificado con `gh pr view 9` y `git ls-remote --heads origin
  "Task/*"`, que **no devuelve ninguna rama**. Como el merge del PR existía **solo en
  `main`**, se integró `main` en `dev` con el merge `--no-ff` **`9dfbc10`** y se publicó:
  `main` es **ancestro de `dev`** y `git diff main dev` está **vacío**.
- `Task/005.4-Corregir-Base-Ramas-Task-Main` se creó el 2026-08-15 **desde `main`**
  (**`181c634`**), **solo en `personal-blog-infra`**. Es **la primera rama Task del
  proyecto creada desde `main`** y la evidencia del invariante que ella misma establece:
  al crearla, `HEAD == main == 181c634`, distinto de `dev` (`9dfbc10`). Es mantenimiento de
  gobierno: **no cuenta** en las 41 tareas y **no altera el avance**. Fue **aprobada** el
  2026-08-15; su cierre creó el commit, integró la rama en `dev` con merge `--no-ff`, publicó
  `dev` y la rama Task, y abrió el pull request `Task/005.4 → main`, que **sigue abierto**.
  La rama Task local se eliminó con `git branch -d`; la remota se conserva mientras el PR
  siga abierto.

---

## Notas de estado

- **`Task/005` produce el primer código de aplicación del proyecto:** `personal-blog-backend`
  ya contiene una aplicación FastAPI que arranca, expone `/health` y OpenAPI, se conecta al
  PostgreSQL local y gestiona su esquema con Alembic. Está **`Aprobada`** desde el
  2026-08-12. **No existe todavía código React.**
- **Correcciones del 2026-08-11, en la misma rama y sin commit:** el log emite ahora UTC
  explícito —antes el formato dependía del sistema operativo— con 9 pruebas deterministas
  comprobadas en Windows y en Docker; la advertencia de `starlette.testclient` se resolvió
  cambiando `httpx` por `httpx2` en las dependencias de desarrollo, sin silenciar nada en
  `pyproject.toml`, de modo que `pytest -W error` termina con **0 warnings y sin ningún
  filtro** en los dos entornos; se rectificó la afirmación errónea de que rotar la contraseña de
  PostgreSQL obliga a recrear su volumen; y se verificó que el `Dockerfile` es coherente con
  **R-14**. **El avance global no cambia.**
- **La funcionalidad del blog sigue sin empezar:** no hay modelo de datos, ni endpoints de
  contenido, ni autenticación. Llegan a partir de `Task/008`.
- **`Task/003` produjo el primer artefacto ejecutable del proyecto:** un
  `docker-compose.yml` con PostgreSQL, MinIO y Portainer CE, **aprobado** y fusionado en
  `main`.
- **`Task/004` añade el respaldo y la recuperación local:** 5 scripts PowerShell y un
  runbook, **aprobados**. La restauración se **probó realmente** en un entorno temporal
  aislado y los tres servicios se recuperaron con sus datos íntegros. En MinIO se
  verifican **contenido, metadatos y tags** de la versión actual de cada objeto; el
  historial de versiones queda fuera del alcance y se detecta explícitamente.
- Con `Task/004`, la **ETAPA 01 queda completada** (2 de 2 tareas) y el avance global
  pasa a **4 de 41 (10 %)**.
- **Ningún backup real se versiona:** `local-backups/` está ignorado por Git.
- **No existe Terraform** en ningún repositorio. Ni `Task/005.2` ni `Task/005.3` crearon
  ningún archivo `.tf`: solo documentan cómo se escribirá en `Task/025` y `Task/029`.
- **No se ha creado ningún recurso cloud** ni ninguna cuenta en proveedores. **`Task/005.3`
  no contrató ningún VPS**, no instaló PostgreSQL ni PgBouncer, no creó certificados, claves,
  usuarios SSH ni reglas de firewall, y no ejecutó `pg_dump`.
- **Floci no está instalado.** `Task/005.2` y `Task/005.3` son documentales: no se descargó
  ninguna imagen, no se levantó ningún contenedor, no se modificó `docker-compose.yml` y no
  se ejecutó ningún comando de Terraform ni de AWS CLI.
- **El backend y el frontend no se han tocado en ninguno de los dos mantenimientos.**
  `Task/005.3` **no modifica** `DATABASE_URL`, SQLAlchemy ni psycopg: la abstracción ya
  existente es precisamente lo que permite cambiar el destino de la base de datos **sin tocar
  código**.
- `Task/002` definió el **alcance del MVP y la arquitectura**, y fue **aprobada**. Con
  ella, la **ETAPA 00 queda completada** (2 de 2 tareas).
- ADR-001 a ADR-005 están todos en estado **Aceptada**. Ni `Task/003` ni `Task/004`
  crearon ADR nuevos: sus decisiones son de implementación local y reversibles. D-05
  quedó **Resuelta** con **Traefik v3** al aprobarse `Task/003`.
- **`ADR-007` está `Aceptada`** desde el 2026-08-15, al aprobarse `Task/005.3`. Es el
  séptimo ADR del proyecto. Cambia el destino de la **capa de datos de producción**: de
  PostgreSQL administrado a **PostgreSQL autogestionado en un VPS externo**, con
  **PgBouncer** delante y **PostgreSQL nunca expuesto a Internet**. **FastAPI permanece en
  AWS Lambda** y toda la arquitectura AWS sigue igual. Motivo principal: **costo**. Ver
  [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) —
  **Vigente**.
- **`ADR-007` modifica parcialmente a `ADR-003`**, solo su fila «Base de datos». ADR-003
  sigue **Aceptado y vigente**, y ADR-007 **refuerza** su exclusión de NAT Gateway. **Amazon
  RDS queda excluido** como destino de producción. Precisión registrada con documentación
  oficial de AWS: **NAT Gateway no es una consecuencia inherente de RDS** — aparece solo si
  una Lambda ya dentro de una VPC necesita salida IPv4 a Internet.
- **`ADR-006` está `Aceptada`** desde el 2026-08-15, al aprobarse `Task/005.2`. Es el sexto
  ADR del proyecto y el primero sobre estrategia de infraestructura.
- **Decisiones diferidas: 11 abiertas.** Resueltas: **D-05** (2026-07-29, Traefik v3),
  **D-14** (2026-08-15, **Floci** como laboratorio AWS local) y **D-01** (2026-08-15,
  PostgreSQL **autogestionado en VPS externo**). **D-01 se resolvió solo en cuanto al
  *modelo***: la selección de **proveedor, región y tamaño sigue pendiente** en `Task/029`.
  **D-06 sigue abierta:** `Task/005.3` no la toca. **D-10** amplía su alcance: el proyecto
  asume backup y restore completos.
- `Task/002.1-Configurar-Claude-Code` es mantenimiento de gobierno, está **Aprobada** y
  cerrada, y no forma parte de las 41 tareas del roadmap.
- **La ETAPA 08 amplía su alcance sin añadir tareas.** `Task/005.2`, **aprobada**, la reformula de
  *«Preparación Cloud sin Cuentas»* a **«Preparación Cloud + AWS Local Parity»**: la IaC
  pasará a ejecutarse de verdad contra un emulador AWS local en lugar de quedarse en
  `terraform fmt` + `validate`. **Los 4 identificadores y nombres de `Task/023`–`Task/026`
  no cambian**, el roadmap sigue teniendo **41 tareas** y **ninguna se renumeró**.
  Estrategia: [aws-local-parity](../architecture/aws-local-parity.md).
- La **ETAPA 01 está completada** (2 de 2 tareas aprobadas). La **ETAPA 02 — Fundaciones de
  las Aplicaciones** está **en curso**: **1 de 3** tareas aprobadas, tras la aprobación de
  `Task/005`.
- **`Task/029` cambia de alcance, no de número** (`Task/005.3`, aprobada). Pasa de
  `Task/029-Seleccionar-PostgreSQL-Administrado` a
  **`Task/029-Preparar-PostgreSQL-Produccion-en-VPS`**: selección del VPS con precios
  actuales, región y **RTT medido**, PgBouncer, TLS y SCRAM, firewall y SSH, backups fuera
  del host y restore probado. **El identificador `029` no cambia**, el roadmap sigue teniendo
  **41 tareas** y **ninguna se renumeró**.
- **Invariante Git corregido y VIGENTE desde el 2026-08-15 (`Task/005.4`, aprobada).** La documentación indicaba que
  las ramas Task debían crearse **desde `dev`**, e incluso prohibía partir de `main`. La
  regla vigente es la contraria: **toda rama `Task/<...>` nace desde `main` actualizado y
  limpio; `dev` NUNCA es base de una Task**, solo rama de integración. Motivo: `dev` acumula
  commits de integración que contaminarían la ascendencia de una tarea nueva y podrían
  filtrarse al PR `Task → main`. **El resto del workflow no cambia.** El historial de las
  tareas anteriores **no se reescribe**. Detalle:
  [WORKFLOW.md](WORKFLOW.md) §2.1.
- `Task/006` y `Task/007` siguen **Pendientes** y **no se han iniciado**. `Task/005.1`,
  `Task/005.2` y `Task/005.3` están aprobadas, fusionadas y normalizadas; `Task/005.4` está
  **aprobada** con su PR **abierto**. `Task/006` no empieza hasta que el usuario fusione ese
  PR y se complete la normalización `main → dev`, y **nacerá desde `main`**.
- **El backend se desarrollará test-first a partir de `Task/008`.** `Task/005.1` formaliza la
  regla **RED → GREEN → REFACTOR** en
  [BACKEND_TESTING_STRATEGY](BACKEND_TESTING_STRATEGY.md), con matriz de casos previa,
  evidencia obligatoria y protección explícita de los tests frente a implementaciones
  incorrectas. Es mantenimiento: **no altera el avance**.
- **Ningún secreto nuevo se ha versionado.** Se detectó, en cambio, que el `.env` local
  conserva las contraseñas de ejemplo publicadas: riesgo **R-16**, a decisión del usuario.
  Rotar la contraseña de PostgreSQL **no destruye datos**: se hace con `ALTER ROLE` sobre el
  rol existente, sin recrear el volumen. La rotación **no se ejecutó** en `Task/005`.

Detalle completo: [ROADMAP.md](ROADMAP.md) ·
[TASK-001](../tasks/TASK-001-initial-workspace-and-roadmap.md) ·
[Reporte TASK-001](../task-reports/TASK-001-report.md) ·
[TASK-002](../tasks/TASK-002-define-mvp-and-architecture.md) ·
[Reporte TASK-002](../task-reports/TASK-002-report.md) ·
[TASK-003](../tasks/TASK-003-create-local-infrastructure.md) ·
[Reporte TASK-003](../task-reports/TASK-003-report.md) ·
[TASK-004](../tasks/TASK-004-local-backups-and-recovery.md) ·
[Reporte TASK-004](../task-reports/TASK-004-report.md) ·
[TASK-005](../tasks/TASK-005-fastapi-backend-foundation.md) ·
[Reporte TASK-005](../task-reports/TASK-005-report.md) ·
[TASK-005.1](../tasks/TASK-005.1-formalize-backend-tdd.md) ·
[Reporte TASK-005.1](../task-reports/TASK-005.1-report.md) ·
[TASK-005.2](../tasks/TASK-005.2-document-floci-local-iac-strategy.md) ·
[Reporte TASK-005.2](../task-reports/TASK-005.2-report.md) ·
[TASK-005.3](../tasks/TASK-005.3-define-production-postgresql-vps.md) ·
[Reporte TASK-005.3](../task-reports/TASK-005.3-report.md) ·
[TASK-005.4](../tasks/TASK-005.4-correct-task-branch-base-main.md) ·
[Reporte TASK-005.4](../task-reports/TASK-005.4-report.md)

Estrategia de infraestructura local aprobada en `Task/005.2`:
[aws-local-parity](../architecture/aws-local-parity.md) (**Vigente**) ·
[ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) (**Aceptada**)

Capa de datos de producción aprobada en `Task/005.3`:
[production-postgresql-vps](../architecture/production-postgresql-vps.md) ·
[ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) (**Propuesta**)

Documentos de producto y arquitectura producidos por `Task/002`:
[MVP_SCOPE](../product/MVP_SCOPE.md) · [USER_FLOWS](../product/USER_FLOWS.md) ·
[CONTENT_MODEL](../product/CONTENT_MODEL.md) ·
[software-architecture](../architecture/software-architecture.md) ·
[api-contracts](../architecture/api-contracts.md) ·
[non-functional-requirements](../architecture/non-functional-requirements.md) ·
[security-boundaries](../architecture/security-boundaries.md) ·
[open-decisions](../architecture/open-decisions.md)
