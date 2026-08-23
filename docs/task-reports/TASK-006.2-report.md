# TASK-006.2 — Reporte de ejecución

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| **Tipo** | **Mantenimiento transversal de arquitectura y planificación** |
| **Estado final** | **Aprobada** ✔ (2026-08-23) |
| **Cuenta en el roadmap** | **No.** No forma parte de las 41 tareas |
| **Repositorios modificados** | `personal-blog-infra` (**únicamente**) |
| **Rama** | `Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| **Rama base** | **`main`** — SHA `d08fe27711866eabe091a2d139387e2022c95b70` |
| **Fecha** | 2026-08-23 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| **Ficha** | [TASK-006.2](../tasks/TASK-006.2-formalize-target-production-architecture.md) |

---

## 1. Estado inicial encontrado

### 1.1 Reconciliación previa del hotfix — verificada, no ejecutada

El usuario había actualizado manualmente `images/Infraestructura.png` en `main` (commit
`d08fe27`) y había normalizado `main → dev` por su cuenta. **Esta tarea no repitió esa
normalización**: solo la verificó.

| Comprobación | Resultado |
| --- | --- |
| `main` / `origin/main` | `d08fe27711866eabe091a2d139387e2022c95b70` — coinciden |
| `dev` / `origin/dev` | `dbc13fc386438e27bc4f42e72471013237e53f38` — coinciden |
| `git merge-base --is-ancestor d08fe27 main` | exit **0** |
| `git merge-base --is-ancestor d08fe27 dev` | exit **0** |
| `git merge-base --is-ancestor main dev` | exit **0** |
| `git rev-list --count dev..main` | **0** |
| `git diff main dev` | **vacío** |
| Working tree / staging (infra) | limpios |
| Ramas Task locales / remotas | **0 / 0** |
| `personal-blog-frontend` | `main`, limpio, 0 ramas Task |
| `personal-blog-backend` | `main`, limpio, 0 ramas Task |

**Conclusión:** la reconciliación manual del usuario quedó **validada**. Se procedió.

### 1.2 Rama creada

```
git switch main
git pull --ff-only origin main      # Already up to date
git switch -c Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion
```

`git rev-parse HEAD` == `git rev-parse main` == `d08fe27711866eabe091a2d139387e2022c95b70`;
`git rev-list --count main..HEAD` == **0**. Creada desde **`main`**, nunca desde `dev`.

### 1.3 Defecto documental encontrado

`overview.md` §4 y `README.md` §4 describían `images/Infraestructura.png` como *«la
arquitectura objetivo inicial, anterior a `Task/005.3`»*, conservada como **registro
histórico**. Era cierto **hasta** el commit `d08fe27`; **dejó de serlo** cuando el usuario
actualizó la imagen. Es la única **contradicción viva** que la auditoría encontró, y se
corrigió.

Además, `production-postgresql-vps.md` §15.3.1 registraba explícitamente un hueco abierto:
*«No se decide aquí la herramienta»* para la observabilidad del VPS. Esta tarea lo cierra.

## 2. Cambios realizados

### 2.1 Documentos creados

| Archivo | Contenido |
| --- | --- |
| [`docs/architecture/target-production-architecture.md`](../architecture/target-production-architecture.md) | **Documento canónico.** 26 secciones: propósito, diagrama, arquitectura productiva, flujos, object storage, secretos de Lambda y del VPS, observabilidad AWS/VPS/Grafana, integración CloudWatch→Grafana, PostgreSQL/PgBouncer, backups, Terraform, configuración del VPS, papel de Docker, diferencias local/producción, *trust boundaries*, decisiones cerradas y abiertas, ownership por tarea, qué no debe adelantar un agente, supuestos de costo y regla de mantenimiento |
| [`docs/adr/ADR-008-observability-grafana-cloud-and-alloy.md`](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) | **Aceptada** ✔ (2026-08-23). Observabilidad: CloudWatch mínimo + Grafana Cloud + Alloy. Contexto, decisión en 4 puntos, qué no decide, 5 alternativas comparadas, consecuencias, costo, seguridad, operación y cumplimiento |
| [`docs/tasks/TASK-006.2-...md`](../tasks/TASK-006.2-formalize-target-production-architecture.md) | Ficha de la tarea |
| `docs/task-reports/TASK-006.2-report.md` | Este reporte |

### 2.2 Documentos modificados

| Archivo | Qué cambió |
| --- | --- |
| `docs/architecture/overview.md` | Nota de la PNG corregida (era **la contradicción viva**); componentes de supervisión y agente de telemetría; diagrama Mermaid con Alloy y Grafana Cloud; principios 9 y 10; conteo de decisiones abiertas **13 → 17** |
| `docs/architecture/local-to-cloud-mapping.md` | Filas de métricas, agente, supervisión, papel de Docker y secretos del host; §Logs reescrita como «Logs y observabilidad»; §Ejecución ampliada con el papel de Docker; diferencia 8 corregida |
| `docs/architecture/security-boundaries.md` | **C-16** (Alloy) y **C-17** (Grafana Cloud); 3 comunicaciones permitidas y 4 prohibidas; **§10** nueva con topología, 11 controles (G-01…G-11) y el porqué del agente frente al *stack* |
| `docs/architecture/production-postgresql-vps.md` | **§11.1.1** — los secretos del VPS son un plano distinto de SSM; **§15.3.1** — la herramienta ya está decidida (Alloy → Grafana Cloud); diagrama y tabla «Qué NO cambia» precisados |
| `docs/architecture/non-functional-requirements.md` | **O-06** precisado; **O-09** y **O-10** nuevos; totales **57 → 59**, Observabilidad **8 → 10** |
| `docs/architecture/open-decisions.md` | **D-17**–**D-20** en el índice y con cuerpo completo; conteo **13 → 17**; bloque de decisiones **propuestas** por `Task/006.2` |
| `docs/adr/ADR-003-...md` | Nota de vigencia y marca ⚠️ en la fila «Logs y métricas»; **el ADR sigue Aceptado y su decisión original no desaparece** |
| `docs/project-management/ROADMAP.md` | Guardrail de `Task/007`; alcance conceptual de 10 tareas; nota de `Task/029`; nota de observabilidad de la ETAPA 10; 6 filas nuevas en el mapa transversal; `Task/006.1` y `Task/006.2` en las listas de mantenimiento |
| `docs/project-management/STATUS.md` | Vista rápida; sección «Mantenimiento en curso — `Task/006.2`»; riesgos **R-38**–**R-42**; conteos de riesgos y decisiones; 2 notas de estado |
| `docs/stages/STAGE-02-...md` | Guardrail de arquitectura objetivo para `Task/007` |
| `docs/stages/STAGE-05-...md` | «Fuera del alcance» precisa que `Task/017` no observa el VPS |
| `docs/stages/STAGE-09-...md` | 3 bloques nuevos en el alcance de `Task/029`; 4 criterios de salida; 3 riesgos |
| `docs/stages/STAGE-10-...md` | Alcance de `Task/031`; 2 criterios de salida; 1 riesgo |
| `docs/stages/STAGE-11-...md` | Terraform no configura el sistema operativo del VPS |
| `docs/stages/STAGE-12-...md` | Ámbito de observabilidad en `Task/040`; costo de Grafana en `Task/041`; 4 criterios de salida; 1 riesgo |
| `README.md` | Tabla cloud con las 3 filas de observabilidad y secretos; nota de la PNG corregida; secciones «Observabilidad de producción» y «Papel de Docker»; índice de documentos |

### 2.3 Lo que NO se tocó

- **`images/Infraestructura.png`** — no aparece en `git status`. Sigue siendo el commit
  `d08fe27` del usuario.
- **`personal-blog-frontend` y `personal-blog-backend`** — leídos, no modificados, **0 ramas
  Task creadas**.
- **Los 41 identificadores del roadmap** — intactos, sin renumerar, sin añadir ni eliminar.
- **`docker-compose.yml`, `scripts/`, `local-backups/`** — sin cambios.
- **Reportes y fichas de tareas anteriores** — son registros fechados; **no se reescriben**.

## 3. Decisiones formalizadas

### 3.1 Cerradas — **vigentes desde el 2026-08-23**

**Reiteradas** —ya aceptadas antes, no se reabren—: React SPA en Cloudflare Pages sin
servidor permanente · FastAPI en Lambda tras API Gateway HTTP API · empaquetado **ZIP**, sin
ECR · S3 en producción y MinIO en local tras `ObjectStorage` · PostgreSQL autogestionado en
VPS con PgBouncer, sin RDS · TLS a PgBouncer con la Lambda **fuera de VPC**, sin NAT Gateway.

**Nuevas**, registradas en ADR-008 o en el documento canónico:

| Decisión |
| --- |
| **Secretos de Lambda:** SSM `SecureString`; configuración no secreta por variables de entorno |
| **Secretos del VPS:** cifrados, clave **fuera del repositorio**, descifrado local seguro. **Herramienta abierta (D-17)** |
| **CloudWatch se mantiene, en modo mínimo**, con retención corta y explícita |
| **Grafana Cloud** como plano central; tier gratuito **como preferencia presupuestaria**, no como dependencia |
| **Grafana Alloy** como agente del VPS; **no se autohospedan Grafana, Prometheus ni Loki** |
| **Integración `CloudWatch → Grafana Cloud` contemplada, no implementada** (D-20) |
| **Backups cifrados y fuera del VPS**, con retención, *lifecycle* y restore probado |
| **Terraform** es la fuente de verdad declarativa, **pero no configura el sistema operativo** |
| **Configuración interna del VPS separada de Terraform**. **Mecanismo abierto (D-18)** |
| **Docker es desarrollo, integración local y *build*/test. Producción no depende de Docker como runtime** |

### 3.2 Abiertas, con propietario — ninguna crea una tarea nueva

| # | Decisión | Owner |
| --- | --- | --- |
| **D-17** | Herramienta de secretos cifrados del VPS (SOPS + age es **candidato**, no decisión) | `Task/029` |
| **D-18** | Mecanismo de configuración interna del VPS (Ansible, cloud-init, scripts) | `Task/029` |
| **D-19** | Plan, límites y costo reales de Grafana Cloud | `Task/041`, con aporte de `Task/027` |
| **D-20** | Mecanismo de integración `CloudWatch → Grafana Cloud` y su modelo IAM | `Task/031` decide · `Task/040` valida |

Se confirmó que las ya existentes **siguen abiertas y no se duplican**: proveedor, región y
tamaño del VPS (**D-01**), backup y retención (**D-10**), retención de CloudWatch
(**D-11**), pool y `max_connections` y mTLS (alcance de `Task/029`), dominio (**D-07**),
presupuesto (**D-13**).

## 4. Riesgos

**Nuevos, abiertos desde la aprobación:** **R-38** (dependencia de un tier gratuito de terceros) · **R-39**
(telemetría con secretos o PII saliendo del perímetro) · **R-40** (secretos del VPS mal
gestionados) · **R-41** (el agente compite por los recursos de PostgreSQL) · **R-42**
(*drift* de configuración del VPS).

**Cobertura confirmada sin duplicar** para los escenarios exigidos: SPOF del VPS (**R-29**),
exposición pública de PgBouncer (**R-30**), agotamiento de conexiones desde Lambda
(**R-03**/**R-33**), fallo de backups y restore no probado (**R-31**), agotamiento de disco
(**R-32**), error humano de operación (**R-35**), redacción de secretos en el log de
aplicación (**R-36**), costo cloud imprevisto (**R-02**).

## 5. Validaciones ejecutadas

| # | Validación | Resultado |
| --- | --- | --- |
| 1 | `git diff --check` | **Sin errores** |
| 2 | Finales de línea en los 20 Markdown creados o modificados | **LF** en todos; 0 archivos con CRLF |
| 3 | `images/Infraestructura.png` en `git status` | **Ausente** — no modificada |
| 4 | La imagen existe y se lee | Sí — PNG 1671×941, 1 661 252 bytes |
| 5 | Enlaces relativos de los documentos nuevos y modificados | **Todos resuelven** |
| 6 | Identificadores del roadmap | **41**, intactos, sin renumerar |
| 7 | Tareas aprobadas | **6** — sin cambios |
| 8 | Avance global / ETAPA 02 | **6 / 41 (15 %)** · **2 / 3 (67 %)** — sin cambios |
| 9 | `Task/006.2` dentro de las 41 filas | **No** — registrada aparte |
| 10 | Búsqueda de secretos | **Sin hallazgos** |
| 11 | Auditoría de consistencia terminológica | **0 contradicciones vivas** (§6) |
| 12 | Repositorios frontend y backend | `main`, limpios, **0 ramas Task** |

**Criterios 3 y 4 de la [Definition of Done](../project-management/DEFINITION_OF_DONE.md)
—compilación y pruebas— no aplican:** tarea exclusivamente documental. No se modificó código,
Compose, scripts ni Terraform, por lo que no había suite que ejecutar.

## 6. Auditoría de consistencia

Cada aparición se clasificó como **A** (histórica válida), **B** (alternativa descartada,
claramente marcada) o **C** (contradicción viva).

| Término auditado | A | B | C |
| --- | --- | --- | --- |
| **RDS / PostgreSQL administrado en AWS** | 2 | 14 | **0** |
| **CloudWatch como única observabilidad** | 3 | 0 | **1 → corregida** |
| **Grafana / Prometheus / Loki autohospedados** | 0 | 9 | **0** |
| **Lambda por imagen de contenedor / ECR** | 0 | 4 | **0** |
| **Docker obligatorio en producción** | 0 | 5 | **0** |
| **MinIO en producción** | 0 | 0 | **0** |
| **PostgreSQL 5432 público** | 0 | 3 | **0** |
| **Secretos en Git / `.env` real** | 0 | 6 | **0** |
| **Terraform configurando el sistema operativo** | 0 | 7 | **0** |
| **SSM sustituido por los secretos del VPS** | 0 | 3 | **0** |

**La única categoría C** eran las notas de `overview.md` §4 y `README.md` §4 que
presentaban la PNG como registro histórico desactualizado. **Corregidas**, dejando constancia
fechada de qué decían antes y por qué dejó de ser cierto.

**Resultado final: C = 0.**

## 7. Problemas encontrados

Ninguno bloqueante. Dos observaciones:

1. **`ROADMAP.md` omitía `Task/006.1`** en sus dos listas de tareas de mantenimiento, pese a
   estar **aprobada** desde el 2026-08-21. Se añadió, junto con `Task/006.2`.
2. **Los conteos de requisitos no funcionales** aparecían en cuatro sitios. Los de
   `TASK-002` —ficha y reporte— **no se tocaron**: son registros fechados de lo que aquella
   tarea entregó. Los conteos **vivos** —`non-functional-requirements.md`, `overview.md` y
   `README.md`— se actualizaron a **59**, y en `overview.md` se distinguió explícitamente
   *«57 definidos en `Task/002`; 59 vigentes»*.

## 8. Estado Git final

| Campo | Valor |
| --- | --- |
| Rama activa (infra) | `Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| Staging | **Vacío** |
| Commits de `Task/006.2` | **0** |
| Push de `Task/006.2` | **0** |
| Merge de `Task/006.2` | **0** |
| Pull request | **0** |
| Frontend / Backend | `main`, limpios, **0 ramas Task** |

> El merge y el push de la normalización `main → dev` del hotfix son **anteriores a esta
> tarea** y los ejecutó el usuario. **Esta tarea no produjo ninguna operación remota.**

## 9. Cómo validar

1. `git status --porcelain` en `personal-blog-infra`: **16 modificados, 4 nuevos**, y
   **`images/Infraestructura.png` no aparece**.
2. Leer
   [`target-production-architecture.md`](../architecture/target-production-architecture.md)
   con la imagen delante: deben describir lo mismo.
3. Revisar [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md): quedó
   **Aceptada** el 2026-08-23, con su fecha, su aprobador y su expresión de aprobación.
4. Comprobar en [`ROADMAP.md`](../project-management/ROADMAP.md) que hay **41 tareas** con
   los mismos identificadores y orden.
5. Comprobar en [`open-decisions.md`](../architecture/open-decisions.md) que **D-17**–**D-20**
   tienen propietario y que ninguna inventa una tarea.
6. Confirmar que `Task/007` sigue siendo **integración local**.

## 10. Próxima tarea

`Task/007-Integracion-Local` — **Pendiente, no iniciada**. **No se inició nada de ella.**
Nacerá desde `main` actualizado, como toda rama Task.

## 11. Aprobación y cierre

**Aprobada** por el usuario el 2026-08-23 con la expresión exacta:

```
approved: Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion
```

Efectos registrados en el cierre:

| Elemento | Antes | Después |
| --- | --- | --- |
| `Task/006.2` | Lista para validación | **Aprobada** ✔ |
| **ADR-008** | Propuesta | **Aceptada** ✔ |
| `target-production-architecture.md` | Propuesta | **Vigente** ✔ |
| `security-boundaries.md` §10 | Propuesta | **Vigente** ✔ |
| `production-postgresql-vps.md` §11.1.1 y §15.3.1 | Propuestas | **Vigentes** ✔ |
| **D-17**–**D-20** | Propuestas | **Abiertas**, con propietario |
| **R-38**–**R-42** | Propuestos | **Abiertos** |
| Avance del roadmap | 6 / 41 (15 %) | **6 / 41 (15 %)** — sin cambios |

**Aprobar no autoriza a implementar.** Cada pieza de la arquitectura sigue exigiendo su
tarea propietaria y la autorización explícita del usuario.

`Task/007-Integracion-Local` sigue **Pendiente y no iniciada**.
