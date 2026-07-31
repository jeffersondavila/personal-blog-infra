# STATUS — Estado del proyecto Blog Personal

**Última actualización:** 2026-07-31

---

## Vista rápida

| Campo | Valor |
| --- | --- |
| **Etapa actual** | ETAPA 02 — Fundaciones de las Aplicaciones (siguiente). ETAPAS 00 y 01 **completadas** |
| **Tarea actual** | `Task/004-Backups-y-Recuperacion-Local` — cerrada; PR pendiente de revisión en `main` |
| **Estado de la tarea** | **Aprobada** — cierre autorizado el 2026-07-31 |
| **Última tarea aprobada** | `Task/004-Backups-y-Recuperacion-Local` — **Aprobada** el 2026-07-31 por jeffersondavila |
| **Último mantenimiento aprobado** | `Task/002.1-Configurar-Claude-Code` — **Aprobada** el 2026-07-26; PR `#3` fusionado por el usuario |
| **Próxima tarea prevista** | `Task/005-Fundacion-Backend-FastAPI` (Pendiente, no iniciada) |
| **Avance global** | **10 %** — 4 de 41 tareas aprobadas |
| **Bloqueos activos** | 0 |
| **Riesgos abiertos** | 11 (R-01 y **R-08** cerrados) |

> El avance se calcula **solo** con tareas `Aprobada`.

---

## Última tarea cerrada

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
| **Pull request** | `Task/004-Backups-y-Recuperacion-Local → main` — **abierto, sin fusionar**. Pendiente de revisión y decisión del usuario |
| **Rama Task** | Local **eliminada** con `git branch -d`; remota **conservada** mientras exista el PR |
| **Riesgo cerrado** | **R-08** — el entorno local ya tiene copia externa a los volúmenes, verificada y restaurable |
| **Ficha** | [TASK-004](../tasks/TASK-004-local-backups-and-recovery.md) |
| **Reporte** | [TASK-004-report](../task-reports/TASK-004-report.md) |
| **Runbook producido** | [local-backup-and-recovery.md](../runbooks/local-backup-and-recovery.md) — **Vigente** |

Con esta aprobación **la ETAPA 01 queda completada** (2 de 2 tareas).

`Task/005` **no puede iniciarse** hasta que el usuario fusione el PR y se complete la
normalización posterior `main → dev`.

---

## Tarea aprobada anterior

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

## Mantenimiento de gobierno

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
| 02 — Fundaciones de las Aplicaciones | 3 | 0 | 0 % |
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
| **Total** | **41** | **4** | **10 %** |

Distribución por estado:

| Estado | Tareas |
| --- | --- |
| Pendiente | 37 |
| En progreso | 0 |
| Lista para validación | 0 |
| **Aprobada** | **4** |
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

---

## Tabla completa de tareas

| Tarea | Etapa | Repos | Estado |
| --- | --- | --- | --- |
| `Task/001-Inicializar-Workspace-y-Roadmap` | 00 | infra, frontend, backend | **Aprobada** |
| `Task/002-Definir-MVP-y-Arquitectura` | 00 | infra | **Aprobada** |
| `Task/003-Crear-Infraestructura-Local` | 01 | infra | **Aprobada** |
| `Task/004-Backups-y-Recuperacion-Local` | 01 | infra | **Aprobada** |
| `Task/005-Fundacion-Backend-FastAPI` | 02 | backend | Pendiente |
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

| Repositorio | Ramas | Rama activa | `main` y `dev` sincronizadas |
| --- | --- | --- | --- |
| `personal-blog-infra` | `main`, `dev`, `Task/004-Backups-y-Recuperacion-Local` (remota durante el PR) | `main` tras completar el cierre local | No; `dev` contiene `Task/004` mientras el PR espera al usuario |
| `personal-blog-frontend` | `main`, `dev` | `main` | Sí |
| `personal-blog-backend` | `main`, `dev` | `main` | Sí |

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
  abrió el PR `Task/004 → main` **sin fusionarlo**. La rama Task local se eliminó con
  `git branch -d`; la remota se conserva mientras el PR espera al usuario.
- Frontend y backend permanecen en `main` con el árbol limpio y sin rama `Task/004`.

---

## Notas de estado

- **La implementación del blog no ha comenzado.** No existe código React ni FastAPI en
  ningún repositorio.
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
- **No existe Terraform** en ningún repositorio.
- **No se ha creado ningún recurso cloud** ni ninguna cuenta en proveedores.
- `Task/002` definió el **alcance del MVP y la arquitectura**, y fue **aprobada**. Con
  ella, la **ETAPA 00 queda completada** (2 de 2 tareas).
- ADR-001 a ADR-005 están todos en estado **Aceptada**. Ni `Task/003` ni `Task/004`
  crearon ADR nuevos: sus decisiones son de implementación local y reversibles. D-05
  quedó **Resuelta** con **Traefik v3** al aprobarse `Task/003`.
- **Decisiones diferidas: 12 abiertas** (eran 13; D-05 resuelta el 2026-07-29).
- `Task/002.1-Configurar-Claude-Code` es mantenimiento de gobierno, está **Aprobada** y
  cerrada, y no forma parte de las 41 tareas del roadmap.
- La **ETAPA 01 está completada** (2 de 2 tareas aprobadas). La siguiente es la
  **ETAPA 02 — Fundaciones de las Aplicaciones**, que empieza con `Task/005` en
  `personal-blog-backend`: será el **primer código de aplicación** del proyecto.
- `Task/005` **no ha sido iniciada**.

Detalle completo: [ROADMAP.md](ROADMAP.md) ·
[TASK-001](../tasks/TASK-001-initial-workspace-and-roadmap.md) ·
[Reporte TASK-001](../task-reports/TASK-001-report.md) ·
[TASK-002](../tasks/TASK-002-define-mvp-and-architecture.md) ·
[Reporte TASK-002](../task-reports/TASK-002-report.md) ·
[TASK-003](../tasks/TASK-003-create-local-infrastructure.md) ·
[Reporte TASK-003](../task-reports/TASK-003-report.md) ·
[TASK-004](../tasks/TASK-004-local-backups-and-recovery.md) ·
[Reporte TASK-004](../task-reports/TASK-004-report.md)

Documentos de producto y arquitectura producidos por `Task/002`:
[MVP_SCOPE](../product/MVP_SCOPE.md) · [USER_FLOWS](../product/USER_FLOWS.md) ·
[CONTENT_MODEL](../product/CONTENT_MODEL.md) ·
[software-architecture](../architecture/software-architecture.md) ·
[api-contracts](../architecture/api-contracts.md) ·
[non-functional-requirements](../architecture/non-functional-requirements.md) ·
[security-boundaries](../architecture/security-boundaries.md) ·
[open-decisions](../architecture/open-decisions.md)
