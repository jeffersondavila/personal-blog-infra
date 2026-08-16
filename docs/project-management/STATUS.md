# STATUS — Estado del proyecto Blog Personal

**Última actualización:** 2026-08-15

---

## Vista rápida

| Campo | Valor |
| --- | --- |
| **Etapa actual** | ETAPA 02 — Fundaciones de las Aplicaciones — **En curso** (1 de 3 aprobadas). ETAPAS 00 y 01 **completadas** |
| **Tarea actual** | Ninguna en ejecución. `Task/005.2` **aprobada** y cerrada; `Task/006` **no iniciada** |
| **Estado de la tarea** | — |
| **Última tarea aprobada** | `Task/005-Fundacion-Backend-FastAPI` — **Aprobada** el 2026-08-12 por jeffersondavila; PR `#2` (backend) y `#6` (infra) **fusionados** el 2026-08-13 y normalizados |
| **Último mantenimiento aprobado** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` — **Aprobada** el 2026-08-15; PR `Task/005.2 → main` **abierto, sin fusionar**. No cuenta en las 41 tareas |
| **Mantenimiento anterior** | `Task/005.1-Formalizar-TDD-Backend` — **Aprobada** el 2026-08-13; PR `#7` **fusionado** por el usuario (`2026-08-16T00:25:21Z` UTC), rama remota eliminada y normalización `main → dev` completada el 2026-08-15 |
| **Próxima tarea prevista** | `Task/006-Fundacion-Frontend-React` (Pendiente, **no iniciada**; **espera** la fusión del PR de `Task/005.2` y la normalización `main → dev`) |
| **Avance global** | **12 %** — 5 de 41 tareas aprobadas |
| **Bloqueos activos** | 0 |
| **Riesgos abiertos** | **26** (R-01 y **R-08** cerrados; **R-19** a **R-28** abiertos desde el 2026-08-15) |

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
| **Integración en `dev`** | Merge `--no-ff`, publicado |
| **Pull request** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local → main` — **abierto, sin fusionar**. La fusión es responsabilidad del usuario |
| **Rama Task** | Eliminada **localmente** con `git branch -d`; **conservada en `origin`** mientras el PR siga abierto |
| **Ficha** | [TASK-005.2](../tasks/TASK-005.2-document-floci-local-iac-strategy.md) |
| **Reporte** | [TASK-005.2-report](../task-reports/TASK-005.2-report.md) |

La aprobación de este mantenimiento **no modifica el conteo del roadmap**: el avance global
permanece en **5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas.

Con ella, `ADR-006` pasa a **Aceptada**, **D-14** a **Resuelta** y los riesgos **R-19** a
**R-28** a **Abiertos**. `Task/006` sigue **Pendiente y no iniciada**: no comienza hasta que
el usuario fusione el PR de `Task/005.2` y se complete la normalización `main → dev`.

---

## Mantenimiento aprobado anterior

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
| R-03 | La elección de PostgreSQL administrado puede condicionar el diseño de conexiones desde Lambda (pooling, límites). | Medio | Evaluar en `Task/029` y considerar el patrón de conexión desde `Task/005`. | Abierto |
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
| `Task/029-Seleccionar-PostgreSQL-Administrado` | 09 | infra | Pendiente |
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
| `personal-blog-infra` | `main`, `dev` — la rama Task se eliminó localmente en el cierre | `main`, `dev`, `origin/Task/005.2-Documentar-Estrategia-Floci-IaC-Local` (**con PR abierto**) | `main` | **No todavía** — se normaliza cuando el usuario fusione el PR de `Task/005.2` |
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
  `dev` con merge `--no-ff`, publicó `dev` y la rama Task, y abrió el pull request
  `Task/005.2 → main`, que **sigue abierto**. La rama Task local se eliminó con
  `git branch -d`; la remota se conserva mientras el PR siga abierto.

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
- **No existe Terraform** en ningún repositorio. `Task/005.2` **no creó ningún archivo
  `.tf`**: solo documenta cómo se escribirá en `Task/025`.
- **No se ha creado ningún recurso cloud** ni ninguna cuenta en proveedores.
- **Floci no está instalado.** `Task/005.2` es documental: no se descargó ninguna imagen, no
  se levantó ningún contenedor, no se modificó `docker-compose.yml` y no se ejecutó ningún
  comando de Terraform ni de AWS CLI.
- `Task/002` definió el **alcance del MVP y la arquitectura**, y fue **aprobada**. Con
  ella, la **ETAPA 00 queda completada** (2 de 2 tareas).
- ADR-001 a ADR-005 están todos en estado **Aceptada**. Ni `Task/003` ni `Task/004`
  crearon ADR nuevos: sus decisiones son de implementación local y reversibles. D-05
  quedó **Resuelta** con **Traefik v3** al aprobarse `Task/003`.
- **`ADR-006` está `Aceptada`** desde el 2026-08-15, al aprobarse `Task/005.2`. Es el sexto
  ADR del proyecto y el primero sobre estrategia de infraestructura.
- **Decisiones diferidas: 12 abiertas.** Resueltas: **D-05** (2026-07-29, Traefik v3) y
  **D-14** (2026-08-15, **Floci** como laboratorio AWS local). **D-01** y **D-06 siguen
  abiertas: `Task/005.2` no las tocó.**
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
- `Task/006` y `Task/007` siguen **Pendientes** y **no se han iniciado**. `Task/005.1` está
  aprobada, fusionada y normalizada; `Task/005.2` está **aprobada** con su PR **abierto**.
  `Task/006` no empieza hasta que el usuario fusione ese PR y se complete la normalización
  `main → dev`.
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
[Reporte TASK-005.2](../task-reports/TASK-005.2-report.md)

Estrategia de infraestructura local aprobada en `Task/005.2`:
[aws-local-parity](../architecture/aws-local-parity.md) (**Vigente**) ·
[ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) (**Aceptada**)

Documentos de producto y arquitectura producidos por `Task/002`:
[MVP_SCOPE](../product/MVP_SCOPE.md) · [USER_FLOWS](../product/USER_FLOWS.md) ·
[CONTENT_MODEL](../product/CONTENT_MODEL.md) ·
[software-architecture](../architecture/software-architecture.md) ·
[api-contracts](../architecture/api-contracts.md) ·
[non-functional-requirements](../architecture/non-functional-requirements.md) ·
[security-boundaries](../architecture/security-boundaries.md) ·
[open-decisions](../architecture/open-decisions.md)
