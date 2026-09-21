# ROADMAP — Blog Personal

> **2026-09-21 — Addendum Floci de Task/027.1: APROBADO** por el usuario mediante
> `approved: Task/027.1-Corregir-Regresion-S09-MinIO`. Sus decisiones pasan a **Aceptadas
> y Vigentes**, sin ADR nuevo. La primera aprobación MinIO del 2026-09-20 se conserva
> como historia. Floci **2.1.0** por digest, baseline **70 → 2, −68/+0**; **H-025-1
> cerrada técnicamente**, H-025-6 abierta con dos identidades. S-11 revalidado, con cold
> start, parser API y aislamiento DNS desde Lambda real. **240 pruebas**, S-09 **126
> exactas, 0 nuevas**; MinIO **99/99** y BuildKit intactos.
>
> **Task/027 Aprobada; avance vigente 27/41 ≈ 66 %; Stage09 / ETAPA 09 1/3 ≈ 33 %.**
> Task/027.1 es mantenimiento: **no cuenta entre las 41 y no altera el avance**.
> Task/028 permanece **Pendiente, no iniciada**.
> La aprobación humana determina el avance, independientemente de la rama y del PR.
>
> Observado el **2026-09-21**: el usuario cerró sin merge #47 y #48 el
> `2026-09-21T02:38:32Z` y `2026-09-21T02:38:38Z`. GitHub es la fuente viva. Ese mismo
> día, con una autorización posterior y separada, `Task/027.1` quedó **consolidada íntegra
> dentro de `Task/027` mediante `merge --no-ff`**, con su historial completo y sin
> *squash*, *rebase* ni *cherry-pick* selectivo. **`Task/027` es la única rama de entrega**
> y el destino del **único PR nuevo** `Task/027 → main`, cuyo número y estado se consultan
> en GitHub. **#47 y #48 no se reabren y no representan la entrega final.** `dev` no se
> modifica en esta fase y **solo el usuario fusiona hacia `main`**.
> [Evidencia y cierre por fases](../task-reports/TASK-027.1-report.md#15-reconciliación-documental-y-estrategia-de-cierre--2026-09-21)
> · [Consolidación](../task-reports/TASK-027.1-report.md#17-consolidación-en-task027--2026-09-21).

Vista resumida y ordenada de todo el proyecto: 13 etapas (00 → 12) y 41 tareas.

- **Aprobación del addendum Floci:** 2026-09-21 — el usuario aprobó mediante `approved: Task/027.1-Corregir-Regresion-S09-MinIO` el **addendum Floci** del mantenimiento `Task/027.1-Corregir-Regresion-S09-MinIO`, descubierto durante su propio cierre y ampliado por instrucción expresa siguiendo el precedente de `Task/020.3`. **No cuenta entre las 41 tareas** y **no altera el avance**: sigue en **27/41 ≈ 66 %**, ETAPA 09 **1/3 ≈ 33 %**, por la aprobación de `Task/027` del 2026-09-17. Entrega **Floci 2.0.1 → 2.1.0** con el digest del índice OCI verificado remotamente y plataforma `linux/amd64` explícita; **healthcheck sin curl ni paquetes nuevos** (Bash `/dev/tcp`, HTTP 200 y seis servicios `running`) con controles negativos por estado HTTP, servicio ausente, detenido e inexistente; **baseline 70 → 2 por intersección exacta** con las identidades históricas —**68 retiradas, 0 añadidas**—, de modo que las siete regresiones de 2.0.1 desaparecen y **ninguna se acepta**; **H-025-1 cerrada técnicamente** —`PutParameter` conserva Tags y el segundo plan da **exit 0**, y se retira del lanzador la tolerancia a `tags_all`, con regresión que vuelve a fallar—; **parser de API Gateway** aislado y compatible con camelCase/PascalCase, *fail-closed* ante JSON/HTTP inválido; **S-11 revalidado de verdad**: plan/apply de **21 recursos**, readback, **Lambda cold real** y segunda invocación, API → Lambda, Logs, aislamiento, `destroy` y ausencia verificada incluyendo API Gateway. Hallazgo adicional propio: **el DNS de Floci reenviaba consultas externas desde Lambda**; el Compose confina los resolutores a loopback IPv6, desactiva el fallback público y se comprueba **desde el contenedor Lambda real**, no con una sonda genérica de red. Gates: **240 pruebas** (64 seguridad + 176 laboratorio), **S-09 CORRECTO con 126 identidades exactas y 0 nuevas**, **Gitleaks 8.30.1 en 0 hallazgos**, ambos Compose válidos y enlaces Markdown sin roturas. **MinIO no se reconstruye ni se republica:** **99/99**, mismo OCI, mismo digest de GHCR, paquete **privado** y visibilidad **sin modificar**; BuildKit de `df3ba33` intacto. **H-025-6 sigue ABIERTA** con dos identidades (`CVE-2026-4878` en `libcap`, `CVE-2026-54369` en `libacl`); **H-025-7** conserva sus nueve; **R-018-3 sigue ABIERTO**. **Floci sigue siendo laboratorio local**, nunca se despliega a AWS, y **no se declara paridad completa**: lo observado en el emulador es hipótesis hasta la ETAPA 10 (ADR-006). El cierre se detiene tras publicar la rama: **sin PR, sin integración en `dev`, sin cambiar a `Task/027` y sin iniciar `Task/028`**. [Ficha §21](../tasks/TASK-027.1-fix-s09-minio-regression.md) · [Reporte §14–§16](../task-reports/TASK-027.1-report.md).
- **Primera aprobación histórica (alcance MinIO):** 2026-09-20 — mantenimiento `Task/027.1-Corregir-Regresion-S09-MinIO` **Aprobado** mediante `approved: Task/027.1-Corregir-Regresion-S09-MinIO`. Sus decisiones **D-027.1-A** a **D-027.1-F** pasan a **Aceptadas y Vigentes**, sin ADR nuevo. **No cuenta entre las 41 tareas** y **no altera el avance**: el valor vigente es **27/41 ≈ 66 %** por la aprobación de Task/027; **26/41** corresponde solo al main histórico tras Task/026. Corrige la única identidad **accionable y corregible** que quedaba del residual de MinIO —`CVE-2026-79921` en `github.com/rabbitmq/amqp091-go v1.10.0`— reconstruyendo `/usr/bin/minio` desde el **commit exacto** del mismo release `RELEASE.2025-09-07T16-13-09Z` con `amqp091-go v1.13.0`. La imagen pasa a ser un **derivado reproducible de upstream**: el runtime oficial se conserva byte a byte y solo cambia ese archivo, verificado *layer* a *layer* contra `docker/minio/build-manifest.json`. **El residual baja de 100 a 99 identidades, 0 nuevas**; `amqp091-go` queda en **0** hallazgos. **`R-018-3` sigue ABIERTO.** **La tolerancia cero de `postgres` y `traefik` no se toca** y el atestado de identidad es **nominal**: `accepted-baseline` **no** se generaliza a las imágenes propias. Gates locales de `CI Infra` sobre el estado final **todos en verde**, incluidos Terraform `fmt`/`init`/`validate` con el lanzador fijado del proyecto, **45** pruebas de seguridad, **162** del laboratorio, gate **S-09** `CORRECTO` con **194** accionables comparados y **Gitleaks 8.30.1** en **0** hallazgos. **Publicación en GHCR: HECHA y verificada** el 2026-09-19 bajo autorización acotada que **no** aprueba la tarea: se publicó **exactamente el OCI validado, sin reconstruir**, y `sha256:84c67632…059129` es a la vez el manifiesto OCI local **y el RepoDigest remoto** —el manifiesto crudo descargado de GHCR reproduce ese `sha256`, el registro conservó `mediaType` OCI, config y los 10 layers—. **S-09 repetido contra la referencia remota**: `CORRECTO`, MinIO **99/99**, **0 nuevas**, `amqp091-go v1.13.0`, `CVE-2026-79921` ausente; `.env.example` **resuelve**. **El paquete se publicó PRIVADO y su visibilidad no se modificó**. Antes de la primera aprobación, el material correspondiente esencial de AGPL aún no estaba versionado; el cierre del 2026-09-20 lo publicó, como se registra a continuación. Durante la fase previa a la aprobación: **cero commit, push de Git, merge y PR**; con la aprobación, el cierre hizo *commit*, integró en `dev` con `--no-ff`, publicó `dev` y la rama Task y abrió el PR **`Task/027.1 → main`**, **sin fusionarlo**. El *push* deja el **código correspondiente de AGPL** versionado en este repositorio **público**; **SBOM y procedencia aún no se publican junto a la imagen**. `Task/027` conserva su aprobación del 2026-09-17; `Task/028` no se inicia. Los cierres posteriores sin merge de #47/#48 quedan fechados en la cabecera. [Ficha](../tasks/TASK-027.1-fix-s09-minio-regression.md) · [Reporte](../task-reports/TASK-027.1-report.md).
- **Aprobación de la tarea canónica:** 2026-09-17 — `Task/027-Configurar-Cuentas-y-Presupuestos` **Aprobada** mediante `approved: Task/027-Configurar-Cuentas-y-Presupuestos`. Gates A–E y DoD completos con evidencia saneada. **D-13 resuelta:** USD 20/mes global y USD 5/mes AWS. El presupuesto mensual y cuatro alertas porcentuales están verificados, con un EMAIL privado por alerta, cero SNS y cero Budget Actions. El usuario conservó conscientemente el par CAD predeterminado 1/1 sin cambios; su origen automático es inferido. Billing Home mostró Free Plan activo y créditos/días restantes positivos tras la creación, sin upgrade; cero access keys y sesiones AWS cerradas. El usuario atestó cero recursos de aplicación atribuibles a Task/027. La validación local de Git, enlaces y patrones de secretos pasó. ETAPA 09 sigue **En progreso, 1/3 (≈ 33 %)** y el proyecto **27/41 ≈ 66 %**; Task/028 permanece Pendiente hasta el cierre Git de Task/027. [Ficha](../tasks/TASK-027-cloud-accounts-and-budgets.md) · [Reporte](../task-reports/TASK-027-report.md).
- **Actualización anterior:** 2026-09-15 — `Task/026-Runbooks-de-Despliegue` **Aprobada** mediante `approved: Task/026-Runbooks-de-Despliegue`. El avance pasa a **26/41 ≈ 63 %** y la **ETAPA 08** queda **Completada** con **4 de 4 — 100 %** y sus **17 criterios de salida cumplidos**. Rama creada sólo en infra desde `main` actualizado y limpio (`940a5318…`); backend y frontend en solo lectura. Se implementan cinco runbooks, destino explícito, binding fail-closed de Floci, aprobación humana ligada al SHA-256 del plan, inventario con `boto3` desde el ZIP canónico y drift controlado. Ciclo real contra el laboratorio: 21 recursos, `GET /health` **200**, drift introducido y reconciliado, dos `destroy` con ausencia verificada por API y reconstrucción intermedia; **0 residuos Docker**. **202/202** pruebas y gates estáticos en verde, incluidos Compose, enlaces Markdown y **Gitleaks 8.30.1 en 0 hallazgos**. **DEF-026-1** y **DEF-026-2**, encontrados durante la ejecución real, corregidos con regresión. **Rollback NO ejecutado: precondición ausente**, registrado sin fingir éxito y convertido en deuda con propietario. Sus decisiones **D-026-A** a **D-026-J** pasan a **Aceptadas y Vigentes** sin ADR nuevo, y los **cinco runbooks** de despliegue pasan a **Vigentes**. **Cero AWS real, cero credenciales reales:** el modo `production` sigue bloqueado y el bucket S3 de estado no existe. [Ficha](../tasks/TASK-026-deployment-runbooks.md) · [Reporte](../task-reports/TASK-026-report.md).
- **Actualización anterior:** 2026-09-14 — `Task/025-Terraform-Cloud` **Aprobada** mediante `approved: Task/025-Terraform-Cloud`. El avance pasa a **25/41 ≈ 61 %** y la **ETAPA 08** queda **En progreso** con **3 de 4 — 75 %**: **no está completada**. Entrega Terraform **portable** con un **solo grafo de 21 recursos** —provider oficial `hashicorp/aws = 6.64.0`, CLI `= 1.16.2`, lock **versionado** para `linux_amd64` y `windows_amd64`— y lo **ejecuta de verdad** contra el laboratorio AWS local: `apply`, pruebas funcionales, idempotencia, `destroy` con ausencia verificada, reconstrucción y segundo `destroy`. **Camino crítico demostrado** (R-25), **D-06 RESUELTA**, cero recursos AWS reales y excepciones humanas H-025-1/H-025-6/H-025-7 conservadas sin declararlas resueltas. [Ficha](../tasks/TASK-025-terraform-cloud.md) · [Reporte](../task-reports/TASK-025-report.md).
- **Actualización de la fase previa a la aprobación:** 2026-09-14 — `Task/025-Terraform-Cloud` **Lista para validación**, **no aprobada**. El avance **no cambia**: sigue en **24/41 ≈ 59 %** y la **ETAPA 08** en **2 de 4 — 50 %**, porque una tarea En progreso no cuenta. Entrega Terraform **portable** con un **solo grafo de 21 recursos** —provider oficial `hashicorp/aws = 6.64.0`, CLI `= 1.16.2`, lock **versionado** para `linux_amd64` y `windows_amd64`— y lo **ejecuta de verdad** contra el laboratorio AWS local: `apply`, pruebas funcionales de S3, SSM, IAM, Lambda y Logs, idempotencia, `destroy` con **ausencia verificada por API**, **reconstrucción**, *smoke* y segundo `destroy`. **Camino crítico demostrado** (R-25): `GET /health` por HTTP real API Gateway v2 → Lambda → *handler* devolvió **200** con el **mismo cuerpo** que el entorno local. Matriz de paridad rellenada con evidencia real y **sin ninguna celda de «paridad completa»**; tres limitaciones del emulador registradas sin disimular. **D-06** queda como **propuesta de resolución, pendiente de aprobación**. **Cero recursos AWS reales.** **S-09 decidido el 2026-09-14:** el usuario autorizó una excepción **temporal y limitada** de **79 identidades** (70 del emulador ligadas a su digest, 9 de Terraform), registrada en el baseline canónico y revalidada con prueba positiva y ocho controles negativos. **H-025-6** y **H-025-7** dejan de ser bloqueantes, **sin** declararse resueltos. El criterio de aceptación **7** **no se cumple literalmente** (**H-025-1**) y el usuario **aceptó esa divergencia como excepción del laboratorio**: **11 PASS literal + 1 PASS con excepción humana**, ningún FAIL. **Revisión final superada, sin bloqueos.** **D-11**, **D-12** y **H-023-3** siguen abiertos. Corregidas **D-025-1**, **D-025-2** y **C-025-1**.
- **Actualización anterior:** 2026-09-13 — `Task/024-Artefacto-ZIP-Lambda` **Aprobada** mediante `approved: Task/024-Artefacto-ZIP-Lambda`. El avance pasa a **24/41 ≈ 59 %** y la **ETAPA 08** queda **En progreso** con **2 de 4 — 50 %**: **no está completada**, `Task/025` y `Task/026` siguen Pendientes. Entrega el artefacto ZIP **reproducible byte a byte** —mismo SHA-256 en construcciones independientes—, construido dentro de la imagen oficial del runtime de Lambda fijada por digest, con **41/41** distribuciones de ejecución y **0** de desarrollo, y el *handler* **ejecutado desde el ZIP** en un proceso Linux aislado con tres controles negativos. **T-04 Satisfecho y Vigente**; **P-06 conservado**; **P-07** con la evidencia del tramo de artefacto y el arranque real pendiente de `Task/032`. **D-12 ABIERTA**; **H-023-3** sigue **abierto y no diagnosticado**. **D-024-A a D-024-K Aceptadas y Vigentes**, sin ADR nuevo. Corregidas **D-024-1**, **D-024-2** y **D-024-3**.
- **Actualización previa:** 2026-09-13 — `Task/023-Compatibilidad-FastAPI-Lambda` **Aprobada** mediante `approved: Task/023-Compatibilidad-FastAPI-Lambda`. El avance pasa a **23/41 ≈ 56 %** y la **ETAPA 08** queda **En progreso** con **1 de 4 — 25 %**: **no está completada**, `Task/024`, `Task/025` y `Task/026` siguen Pendientes. **T-04 Satisfecho y Vigente**; **P-06 revalidado/conservado**; **P-07 no tocado**. **H-023-3** sigue **abierto y no diagnosticado**. Ramas creadas desde `main` en **backend** e **infra**; **frontend en solo lectura, sin rama**. Corregida la columna *Repos* de la fila de `Task/023` (**D-023-1**).
- **Actualización anterior:** 2026-09-12 — `Task/022-Validacion-Local-Production-Like` **Aprobada** mediante `approved: Task/022-Validacion-Local-Production-Like`. Con ella la **ETAPA 07 queda Completada** (1/1, 100 %) y el avance pasa a **22/41 ≈ 54 %**. Los **ocho** criterios de salida cumplidos, **T-07 Satisfecho** y **siete** defectos de los runbooks corregidos y revalidados con una reconstrucción y una recuperación reales. Siguiente: **ETAPA 08 — Preparación Cloud + AWS Local Parity**, **sin cuentas cloud**. **D-21**, **R-018-3**, **R-021-1** y **R-018-4** siguen abiertos.
- **Anterior:** 2026-09-12 — Task020.3 **Aprobada** mediante `approved: Task/020.3-Corregir-Registro-MinIO-CI-Backend`; con ella la **ETAPA 06 queda Completada**. Task020 y Task021 siguen **Aprobadas**; el avance permanece en **21/41 ≈ 51 %** porque el mantenimiento **no cuenta** entre las 41. La descarga MinIO quedó reparada y **B-020.3-C resuelto**: el gate Trivy de la imagen backend pasó de 12 accionables a **0**, con la política S-09 intacta. Siguiente: **ETAPA 07 — Validación Local**, con `Task/022` **Pendiente, no iniciada**. S-09 conserva su definición y verificaciones canónicas en [NFR](../architecture/non-functional-requirements.md)
- **Estrategia:** local-first (ver [ADR-001](../adr/ADR-001-local-first.md)), extendida a la
  infraestructura con **AWS Local Parity** — ver
  [aws-local-parity.md](../architecture/aws-local-parity.md) y
  [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) (**Aceptada**)
- **Capa de datos de producción:** PostgreSQL autogestionado en **VPS externo** con
  PgBouncer — ver
  [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) y
  [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) (**Aceptada**)
- **Arquitectura objetivo de producción:** Cloudflare → Pages → API Gateway → Lambda → TLS →
  VPS/PgBouncer/PostgreSQL, con S3, SSM `SecureString`, **CloudWatch mínimo** y **Grafana
  Cloud** (Alloy en el VPS) — ver
  [target-production-architecture.md](../architecture/target-production-architecture.md) y
  [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) (**Aceptada**)
- **Avance global:** **27/41 ≈ 66 %** (27 de 41 tareas aprobadas)

> **Corrección de `Task/025` (D-025-2), 2026-09-14.** Esta viñeta es un **dato vigente**, no un registro fechado, y declaraba **54 % (22 de 41)**: el valor que quedó al aprobarse `Task/022`, sin actualizar cuando se aprobaron `Task/023` y `Task/024`. Las entradas fechadas de arriba ya decían **24/41 ≈ 59 %**, así que el documento se contradecía consigo mismo. **Las entradas fechadas no se tocan**: eran correctas en su fecha.

Estados oficiales: `Pendiente` · `En progreso` · `Lista para validación` · `Aprobada` ·
`Bloqueada` · `Descartada`.

> El porcentaje de avance se calcula **solo** con tareas en estado `Aprobada`.
> Ninguna tarea puede marcarse `Aprobada` sin autorización explícita del usuario.

> **Tareas de mantenimiento.** Las tareas con sufijo (`Task/002.1`, `Task/005.1`,
> `Task/005.2`, `Task/005.3`, `Task/005.4`, `Task/005.5`, `Task/005.6`, `Task/005.7`,
> `Task/006.1`, `Task/006.2`, …) son mantenimiento de gobierno: **no forman parte de estas
> 41** y **no alteran el avance**. Su estado se registra en [`STATUS.md`](STATUS.md).

> **Exposición de la auditoría para el dashboard — `Task/012.1` (2026-09-05, aprobada).**
> Mantenimiento **funcional** de la API administrativa, previo a que `Task/015` pueda
> entregar su dashboard. `MVP_SCOPE.md` §3.3 exige como alcance mínimo los *«últimos eventos
> de auditoría»*, y ninguna de las **38 operaciones HTTP** administrativas de entonces los
> leía: el módulo `audit` no tenía capa de presentación y su puerto solo escribía. Añade
> **una** operación de solo lectura —`GET /api/v1/admin/audit-events`—, paginada con la
> envoltura única y sin filtros, con un DTO de cinco campos que **no** incluye
> `ip_address`, `actor_id`, `event_metadata` ni `request_id`. **Sin migración**: el índice
> cronológico ya existe. La inmutabilidad de `AuditEvent` queda intacta y leer no audita,
> comprobado contando filas reales. **1572 pruebas en verde** (+45 sobre el baseline de
> `main`). **No cuenta** dentro
> de las 41, **41 identificadores intactos** y avance **sin cambios**. Ficha:
> [TASK-012.1](../tasks/TASK-012.1-audit-events-for-dashboard.md) · Reporte:
> [TASK-012.1-report.md](../task-reports/TASK-012.1-report.md).

> **Formalización de la arquitectura objetivo de producción — `Task/006.2` (2026-08-23,
> aprobada).**
> Mantenimiento transversal de arquitectura y planificación, previo a `Task/007`. Da
> contraparte **textual** al diagrama `images/Infraestructura.png` que el usuario actualizó
> en `main`, y alinea documentación, roadmap, decisiones y riesgos con él. Cierra el modelo
> de **secretos del VPS**, el **papel de Docker** y la **observabilidad de producción**
> —CloudWatch mínimo + Grafana Cloud con Alloy— y abre **D-17** a **D-20** con propietario.
> **0 funcionalidad**, **0 recursos cloud**, **41 identificadores intactos** y avance **sin
> cambios**. Documento canónico:
> [target-production-architecture.md](../architecture/target-production-architecture.md) —
> **Vigente** ·
> [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) — **Aceptada**.

> **Cierre de los hallazgos finales de certificación — `Task/005.7` (2026-08-16).**
> Mantenimiento transversal previo a `Task/006`, sobre la mega auditoría final de Claude y
> Codex. Ambos reprodujeron los **mismos dos defectos** de la fundación de testing y
> discreparon en severidad; se adoptó **el criterio más estricto**: corregirlos, no
> diferirlos. Queda cerrado que un `.env` del desarrollador no puede alterar la suite **ni
> durante la *collection***, y que las *fixtures* oficiales de integración no entregan acceso
> a PostgreSQL ni a Alembic antes de validar el destino. La concurrencia de la suite queda
> **diferida con propietario explícito** (**R-37**, `Task/020`). **0 funcionalidad nueva**,
> **41 identificadores intactos** y avance **sin cambios**.

> **Cierre de fundaciones — `Task/005.6` (2026-08-16).** Mantenimiento transversal previo a
> `Task/006`: política de finales de línea en los tres repositorios, aislamiento de la suite
> frente al `.env` del desarrollador, base de datos de pruebas dedicada con guardas
> *fail-closed*, verificación semántica de `commit`/`rollback` y corrección del estado
> documental. **0 funcionalidad nueva**, **41 identificadores intactos** y avance **sin
> cambios**. Añade la regla de gobierno de
> [WORKFLOW §6.1](WORKFLOW.md): los documentos versionados registran estado **duradero**; el
> estado transitorio de Git y GitHub se consulta **en vivo**.

> **Alineación posterior a la auditoría — `Task/005.5` (2026-08-16).** Se corrigieron
> dependencias invertidas, propietarios ausentes y *gates* que exigían recursos futuros.
> **Los 41 identificadores, sus nombres y su orden no cambian**; no se añadió, eliminó ni
> renumeró ninguna tarea. Ver el *mapa de responsabilidades transversales* al final de este
> documento.

---

## Resumen de etapas

| # | Etapa | Tareas | Aprobadas | Avance | Estado | Depende de |
| --- | --- | --- | --- | --- | --- | --- |
| 00 | Fundación y Gobierno | 2 | 2 | 100 % | **Completada** | — |
| 01 | Infraestructura Local | 2 | 2 | **100 %** | **Completada** | 00 ✔ |
| 02 | Fundaciones de las Aplicaciones | 3 | 3 | **100 %** | **Completada** | 01 ✔ |
| 03 | Dominio y Backend | 5 | **5** | **100 %** | **Completada** | 02 ✔ |
| 04 | Experiencia del Usuario | 3 | **3** | **100 %** | **Completada** | 03 ✔ |
| 05 | Calidad y Seguridad | 3 | **3** | **100 %** | **Completada** | 04 ✔ |
| 06 | Integración Continua | 3 | **3** | **100 %** | **Completada** | 05 ✔ |
| 07 | Validación Local | 1 | **1** | **100 %** | **Completada** | 06 ✔ |
| 08 | Preparación Cloud + AWS Local Parity | 4 | **4** | **100 %** | **Completada** | 07 ✔ |
| 09 | Cuentas y Seguridad Cloud | 3 | **1** | **≈ 33 %** | **En progreso** | 08 ✔ |
| 10 | Despliegue Cloud | 7 | 0 | 0 % | Pendiente | 09 |
| 11 | Automatización de Despliegues | 3 | 0 | 0 % | Pendiente | 10 |
| 12 | Lanzamiento y Operación | 2 | 0 | 0 % | Pendiente | 11 |
| | **Total** | **41** | **27** | **≈ 66 %** | | |

---

## ETAPA 00 — Fundación y Gobierno

**Objetivo:** dejar los tres repositorios preparados, con reglas de trabajo, sistema
documental de seguimiento y un MVP y arquitectura acordados antes de escribir código.

**Dependencias:** ninguna.
**Hito que completa:** *Gobierno del proyecto establecido y alcance del MVP cerrado.* ✔
**Completada:** 2026-07-26.
**Ficha:** [STAGE-00-foundation.md](../stages/STAGE-00-foundation.md)
**Documentos producidos:** [MVP_SCOPE](../product/MVP_SCOPE.md) ·
[USER_FLOWS](../product/USER_FLOWS.md) · [CONTENT_MODEL](../product/CONTENT_MODEL.md) ·
[software-architecture](../architecture/software-architecture.md) ·
[api-contracts](../architecture/api-contracts.md) ·
[non-functional-requirements](../architecture/non-functional-requirements.md) ·
[security-boundaries](../architecture/security-boundaries.md) ·
[open-decisions](../architecture/open-decisions.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/001-Inicializar-Workspace-y-Roadmap` | Preparar repositorios, documentación y seguimiento. | infra, frontend, backend | — | **Aprobada** (2026-07-26) |
| `Task/002-Definir-MVP-y-Arquitectura` | Definir requerimientos funcionales, arquitectura de software, contratos generales y límites del MVP. | infra | 001 | **Aprobada** (2026-07-26) |

---

## ETAPA 01 — Infraestructura Local

**Objetivo:** disponer de un entorno local reproducible con Docker Compose, con datos
persistentes y capacidad de respaldo y recuperación.

**Dependencias:** Etapa 00.
**Hito que completa:** *Entorno local reproducible y recuperable.* ✔
**Completada:** 2026-07-31.
**Ficha:** [STAGE-01-local-infrastructure.md](../stages/STAGE-01-local-infrastructure.md)
**Documentos producidos:** [local-environment.md](../runbooks/local-environment.md) ·
[local-backup-and-recovery.md](../runbooks/local-backup-and-recovery.md) ·
[scripts/backup/](../../scripts/backup/README.md)
**Decisiones resueltas:** D-05 — **Traefik v3** como reverse proxy local, a implementar en
`Task/007` (ver [open-decisions.md](../architecture/open-decisions.md)).

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/003-Crear-Infraestructura-Local` | Docker Compose. PostgreSQL. MinIO. Portainer. Redes. Volúmenes. Healthchecks. | infra | 002 | **Aprobada** (2026-07-29) |
| `Task/004-Backups-y-Recuperacion-Local` | Backup y restauración de PostgreSQL. Objetos, metadatos y tags de MinIO. Respaldo de Portainer. Reconstrucción del entorno. | infra | 003 | **Aprobada** (2026-07-31) |

---

## ETAPA 02 — Fundaciones de las Aplicaciones

**Objetivo:** establecer la base profesional de backend y frontend e integrarlos con la
infraestructura local.

**Dependencias:** Etapa 01.
**Hito que completa:** *Frontend y backend arrancan e integran contra PostgreSQL y MinIO.*
**Ficha:** [STAGE-02-application-foundations.md](../stages/STAGE-02-application-foundations.md)
**Estado:** **Completada** el 2026-08-23. **3 de 3** tareas aprobadas.
**Hito alcanzado:** *Frontend y backend arrancan e integran contra PostgreSQL y MinIO.* ✔

> **Guardrail de `Task/007` — añadido en `Task/006.2`, aprobada.** La arquitectura objetivo
> de producción es **Cloudflare Pages → API Gateway → Lambda/FastAPI → TLS →
> VPS/PgBouncer/PostgreSQL**; **S3** para object storage; **SSM `SecureString`** para los
> secretos de la Lambda; **CloudWatch mínimo + Grafana Cloud** para observabilidad; **Alloy**
> en el VPS.
>
> **`Task/007` NO implementa estos servicios productivos**, pero **tampoco debe crear
> acoplamientos locales que impidan sustituir MinIO, PostgreSQL o el proxy local por sus
> implementaciones productivas.** Su naturaleza **no cambia**: sigue siendo integración
> **local**. Detalle:
> [target-production-architecture.md](../architecture/target-production-architecture.md) §24.

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/005-Fundacion-Backend-FastAPI` | Base profesional de FastAPI. Configuración. Logging. PostgreSQL. Alembic. Pruebas. Dockerfile. | backend, infra (documentación) | 004 | **Aprobada** (2026-08-12) |
| `Task/006-Fundacion-Frontend-React` | React. TypeScript. Vite. Router. Cliente HTTP. Pruebas. Build. | frontend, infra (documentación) | 004 | **Aprobada** (2026-08-18) |
| `Task/007-Integracion-Local` | Integrar frontend, backend, PostgreSQL y MinIO **a nivel de infraestructura**: contenedores, red, nombres de servicio, configuración disponible y healthchecks. Reverse proxy **Traefik v3**. Docker Compose completo. Supervisión desde Portainer. **No implementa lógica de objetos ni acceso directo de FastAPI a MinIO**: eso es `Task/010`. | infra, frontend | 005, 006 | **Aprobada** (2026-08-23) |

---

## ETAPA 03 — Dominio y Backend

**Objetivo:** modelar el dominio del blog y exponer las APIs pública y administrativa
con almacenamiento de archivos y autenticación.

**Dependencias:** Etapa 02.
**Avance:** **5 de 5 aprobadas** (`Task/008`, el 2026-08-25; `Task/009`, el 2026-08-27; `Task/010`, el 2026-08-28; `Task/011`, el 2026-09-01; `Task/012`, el 2026-09-03).
**Hito que completa:** *Backend funcionalmente completo para el MVP.*
**Ficha:** [STAGE-03-domain-and-backend.md](../stages/STAGE-03-domain-and-backend.md)
**Estado:** **Completada** el 2026-09-03. **5 de 5** tareas aprobadas.
**Hito alcanzado:** *Backend funcionalmente completo para el MVP.* ✔

> **Test-first obligatorio en toda la etapa.** `Task/008` a `Task/012` construyen el backend
> funcional: cada comportamiento nuevo empieza por una prueba que falla
> (**RED → GREEN → REFACTOR**), con matriz de casos previa y evidencia registrada en el
> reporte. Regla completa: [`BACKEND_TESTING_STRATEGY.md`](BACKEND_TESTING_STRATEGY.md).

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/008-Modelo-de-Datos` | Perfil. Artículos. Reviews de libros. Videos. Proyectos. Etiquetas. Medios. Administrador. Auditoría. **Test-first**: invariantes y transiciones; migraciones validadas con integración real. | backend, infra (documentación) | 007 | **Aprobada** (2026-08-25) |
| `Task/009-API-Publica` | Consultas públicas. Paginación. Filtros. Búsqueda. Contenido publicado. **Test-first**: contrato HTTP y el caso negativo de contenido no publicado. | backend, infra (documentación) | 008 | **Aprobada** (2026-08-27) |
| `Task/010-Almacenamiento-Compatible-S3` | Interfaz `ObjectStorage`, `MinIOStorage` **y el código de `S3Storage`**, con pruebas de contrato comunes — **sin AWS real**. Imágenes y miniaturas. Persiste **claves de objeto**, nunca URLs prefirmadas. **Test-first**: contrato primero, después integración con MinIO. | backend, infra (documentación y Compose) | 008 | **Aprobada** (2026-08-28) |
| `Task/011-Autenticacion-Administrativa` | Login. **Sesión opaca *server-side* con cookie `HttpOnly`**. Protección reutilizable de endpoints. **Rate limiting en PostgreSQL**. Auditoría. **Resuelve D-15, D-02 y D-09**. Migración `0003`. **Test-first**: casos negativos de acceso dentro del alcance. | backend, infra (documentación) | 008 | **Aprobada** (2026-09-01) |
| `Task/012-API-Administrativa` | CRUD. Borradores. Publicación. Archivado. Gestión de imágenes. **23 rutas administrativas**, todas autenticadas. Cierra la forma de las transiciones, los campos mínimos para publicar, el formato del *slug*, la **escritura y exigencia del texto alternativo donde se usa la imagen** y el catálogo de auditoría del CRUD. **Sin migración nueva.** **Test-first**: matriz de transiciones antes del caso de uso. | backend, infra (documentación) | 009, 010, 011 | **Aprobada** (2026-09-03) |

---

## ETAPA 04 — Experiencia del Usuario

**Estado:** **Completada** el 2026-09-05 — **3 de 3 aprobadas, 100 %**.

**Objetivo:** construir el sistema de diseño, el sitio público y el panel administrativo.

**Dependencias:** Etapa 03.
**Hito que completa:** *Blog usable de extremo a extremo en local.*
**Ficha:** [STAGE-04-user-experience.md](../stages/STAGE-04-user-experience.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/013-Sistema-de-Diseno` | Tokens semánticos. Fundación global y estrategia única de foco. Tipografía. Responsive intrínseco. Primitivas `Container`, `Stack`, `Button`, `Card`, `Badge`. Accesibilidad base: **A-05**, **A-06**, **A-07** e inicio de **A-01**. **Resuelve D-03**: CSS Modules más CSS Custom Properties, sin biblioteca visual de terceros. | frontend, infra (documentación) | 012 | **Aprobada** (2026-09-04) |
| `Task/014-Sitio-Publico` | Inicio. Quién soy. Artículos y detalle. Reviews y detalle. Videos. Proyectos y detalle. Contacto. Búsqueda y filtro por etiqueta. Página 404. Estados de carga, vacío y error. Markdown sanitizado (ADR-005). Imágenes por `access_url` con `alt_text`. **Asume A-02 y A-04**, continúa **A-01**; **cierra la lista de proveedores de video**. Sin SEO (`Task/016`) ni panel (`Task/015`). | frontend, infra (documentación) | 013 | **Aprobada** (2026-09-05) |
| `Task/015-Panel-Administrativo` | Acceso y sesión administrativa sobre la cookie `HttpOnly` de `Task/011`. Dashboard básico. Listados y formularios de los cuatro tipos publicables. Editor Markdown y **vista previa con el mismo pipeline sanitizado** de `Task/014` (**resuelve D-04**, sin dependencias nuevas). Carga y selección de imágenes. Etiquetas y perfil. Transiciones de publicación. **Asume A-03, A-08, S-03 en la vista previa y P-05.** Sin SEO ni auditoría de accesibilidad (`Task/016`), sin CORS ni cabeceras (`Task/018`). | frontend, infra (documentación) | 013, 014 | **Aprobada** (2026-09-05) — **sin bloqueos**. **18 superficies**, **600 pruebas** en verde y **0 dependencias nuevas**. Su dashboard consume además `GET /api/v1/admin/audit-events`, que entregó `Task/012.1` |

---

## ETAPA 05 — Calidad y Seguridad

**Objetivo:** elevar el producto a estándar publicable: SEO, accesibilidad, rendimiento,
observabilidad y endurecimiento de seguridad.

**Dependencias:** Etapa 04 — **Completada** ✔ (2026-09-05).
**Estado:** **Completada** el 2026-09-08 — **3 de 3** aprobadas, **100 %**.
Se conservan las limitaciones declaradas de rendering (**D-21**) y los riesgos
residuales de imágenes registrados en [STAGE-05](../stages/STAGE-05-quality-security.md).
**Hito que completa:** *Producto con calidad y seguridad verificables.*
**Ficha:** [STAGE-05-quality-security.md](../stages/STAGE-05-quality-security.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/016-SEO-Accesibilidad-y-Rendimiento` | Metadatos. Open Graph. Sitemap. Robots. Optimización. Accesibilidad. **Verificación comprobable** del *rendering* de la SPA por URL directa y ante *crawlers*, con **criterio explícito de reconsideración** si no se satisface. `og:image` con URL estable, no expirable. **El backend participa** por el `sitemap.xml` derivado de contenido publicado y por la exposición de la miniatura (deuda 2 de `Task/010`). | frontend, backend, infra (documentación + wiring local mínimo) | 014, 015 | **Aprobada** (2026-09-06) — **E-02**, **E-04**, **E-05**, **E-07** y **E-08** cumplidos; **E-03 NO cerrado** y **E-06 parcial**. Volver a medir tras implementar demostró que un *crawler* sin JavaScript sigue sin recibir metadatos por URL: no era falta de código, así que se abre **D-21** con **ADR-009** en *Propuesta*, sin elegir estrategia. **688** pruebas de frontend y **1631** de backend en verde, **0 dependencias nuevas**. En `infra`, además de la documentación, **tres líneas de *wiring* local** autorizadas: dos variables del Compose y el enrutado de `/sitemap.xml` en Traefik |
| `Task/017-Observabilidad-Local` | Logs JSON. Correlation ID. Healthchecks. Auditoría. Diagnóstico con Portainer. **Solo entorno local: no es owner del monitoreo del VPS productivo** (`Task/029`, `Task/040`). **La telemetría debe ser portable**: el dominio no se acopla a CloudWatch, Grafana, Loki ni Prometheus — es el **principio 9** de [`overview.md`](../architecture/overview.md) §5 y [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md), **no O-09**. | backend, infra | 014, 015 | **Aprobada** ✔ (2026-09-06) |
| `Task/018-Endurecimiento-de-Seguridad` | Dependencias. Imágenes Docker. Secretos. CORS. Headers. Archivos. Autenticación. | infra, frontend, backend | 016, 017 | **Aprobada** (2026-09-08). **E-06 cerrado** por HTTP; riesgos residuales documentados |

---

## ETAPA 06 — Integración Continua

**Objetivo:** automatizar verificación de calidad en cada cambio, en los tres repositorios.

**Dependencias:** Etapa 05.
**Hito que completa:** *CI verde en los tres repositorios.*
**Ficha:** [STAGE-06-continuous-integration.md](../stages/STAGE-06-continuous-integration.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/019-CI-Frontend` | Lint. Type-check. Tests. Build. Formato y auditoría npm (S-09 frontend). | frontend, infra (documentación) | 018 | **Aprobada** (2026-09-08) — workflow `CI Frontend` en cada `push` y `pull_request`, un job en `ubuntu-24.04` con Node 22.23.2, build antes de las pruebas para no omitir las guardas SEO/P-05, y `npm audit` sin umbral. Ejecución **34305529115** en `success`: **704** pruebas, **0** vulnerabilidades. *En la fecha de esa aprobación*, **S-09 global** esperaba backend en `Task/020`, infra y escaneo del historial en `Task/021` |
| `Task/020-CI-Backend` | Ruff. MyPy. Pytest. Migraciones. Build Docker. Escaneo. | backend, infra (documentación) | 018 | **Aprobada** (2026-09-10) — workflow `CI Backend` en cada `push` y `pull_request`, un job secuencial en `ubuntu-24.04` con Python 3.12.14, PostgreSQL y MinIO efímeros del runner, suite completa con `-W error` y escaneo con política fail-closed. **R-14 resuelto** con dos *locks* transitivos con hashes e instalación `--require-hashes`, más detección de desfase. **S-09 backend satisfecho**; *en la fecha de esa aprobación*, **S-09 global** esperaba `Task/021`. Hallazgos heredados STAGE-06 y B-020-1/2/3 resueltos con autorización durante el preflight. [Reporte](../task-reports/TASK-020-report.md) |
| `Task/021-CI-Infraestructura` | Docker Compose config. Validación de scripts. Escaneo de secretos. *(Hasta `Task/025` esta celda decía «**Terraform todavía no existe** (llega en `Task/025`)», cierto cuando se escribió. **C-025-1 (2026-09-14, antes de su aprobación):** `Task/025` introdujo los primeros `.tf` y amplía este workflow con `fmt`, `init -lockfile=readonly`, `validate`, las pruebas de las guardas del laboratorio y la validación de su Compose. La guarda de alcance se invirtió: ahora falla si los `.tf` **desaparecen**.)* | infra | 018 | **Aprobada** (2026-09-12) — MinIO pasa a **Quay** con el **mismo release y el mismo digest**, contenido OCI idéntico y **100/100** identidades; baseline no regenerado. CI `34670245277` sobre `a3434eb`, por `push`, **`completed/success`** en **42 s** con **19/19** pasos, **116** identidades exactas, **0** fuera del baseline y **0** secretos. **S-09 infraestructura** satisfecho por ese gate; el residual de MinIO **no se resolvió** y **R-018-3** sigue **ABIERTO**. Con ella la ETAPA 06 alcanza **3 de 3 tareas aprobadas**; al registrar esa aprobación, el **cierre de la etapa quedó pendiente** de la evidencia global restante; seguimiento posterior en Task020.3. **Historia preservada:** la CI final `34663425054` sobre `94c5e67` terminó en failure en dos intentos porque el acceso **anónimo** a ese manifiesto devolvió **HTTP 401**. **Antecedente previo al bloqueo:** D-021-A/B e identidad corregidas; revisión humana explícita de tres severidades, 13/13 regresiones, local y nuevo run `34636624843` sobre `43c1bf2` verdes: 56 s, 19 pasos success, 116 coincidencias exactas, 0 fuera del baseline. No aprobada. Evidencia anterior a la revisión: workflow `CI Infra` en cada `push` y `pull_request`: Compose con los 7 servicios, 26 variables, 6 scripts PowerShell, 3 Python, historial completo de secretos con Gitleaks 8.30.1 y gate S-09 con **baseline exacto de riesgo aceptado** para las imágenes third-party. Ejecución histórica **34604423915** sobre `4808d7c`, por `push` en **`success`** en **51 s**, 15 de 15 pasos. **B-021-1/2/3 resueltos** con autorización explícita. [Reporte](../task-reports/TASK-021-report.md) |

---

**Mantenimiento Task020.3 — Aprobada (2026-09-12).** No forma
parte de las 41 tareas y no altera el avance. Recupera CI Backend cambiando el registro de MinIO a
Quay, con el mismo release y digest. `34491446991` **attempt 1** fue success
el 2026-09-10; **attempt 2** falló el 2026-09-12 al descargar desde Docker Hub.
La evidencia posterior de STAGE-06 y el resultado de este mantenimiento se
registran en su [reporte](../task-reports/TASK-020.3-report.md).
*Observado el 2026-09-12 UTC:* run **34713222925**, push, `e8693eb`, attempt 1,
**completed/failure**, 291 s. MinIO desde Quay y 1855 tests en verde; gate
Trivy de la imagen backend falla con **12 accionables (9 HIGH, 3 CRITICAL)**.
La sesión se detuvo y pidió autorización: **B-020.3-C** era un defecto
independiente del cambio de registro.
*Observado el 2026-09-12 UTC, tras autorizar la corrección:* run
**34719123905**, push, `32c3992`, attempt 1, **completed/success**, 296 s,
**25 de 25 pasos en success**; inventario Trivy **149** en Debian 13.7 con
**CRITICAL 0** y gate accionable **0**. **B-020.3-C resuelto** aplicando las
actualizaciones de seguridad de Debian en la etapa `runtime` del Dockerfile,
sin tocar Python, distribución base, digest del `FROM`, locks ni la política
S-09. Con su aprobación el mismo 2026-09-12, la **ETAPA 06 quedó Completada**.
Task022 quedó **iniciada y aprobada el 2026-09-12**, con los ocho criterios de salida de la
ETAPA 07 cumplidos y **T-07 Satisfecho**. El avance pasó a **22/41 ≈ 54 %**.

## ETAPA 07 — Validación Local

**Objetivo:** validar el sistema completo en condiciones similares a producción, desde
cero y con datos reales de prueba.

**Dependencias:** Etapa 06.
**Hito que completa:** *Blog validado íntegramente en local. Puerta de entrada a la nube.*
**Ficha:** [STAGE-07-local-validation.md](../stages/STAGE-07-local-validation.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/022-Validacion-Local-Production-Like` | Reconstrucción completa. Migraciones. Seed. Flujo administrativo. Publicación. Persistencia. Backups. Revisión en Portainer. | backend, infra (frontend en solo lectura) | 019, 020, 021 | **Aprobada** (2026-09-12) — los **8** criterios de salida cumplidos y **T-07 Satisfecho**; **7** defectos de los runbooks corregidos y revalidados. Semilla local con TDD completo. **H-8 Resuelto**: defecto adicional de invocación detectado por CI durante la integración aprobada y corregido sin relajar pruebas; ejecución posterior **34730284072 GREEN 25/25** (2026-09-13 UTC). Suite final backend **Windows: 1875 passed, 1 skipped; CI Linux: 1876 passed**; **704** pruebas de frontend en verde. [Detalle](../task-reports/TASK-022-report.md#14-h-8--defecto-del-entregable-descubierto-por-la-ci-durante-el-cierre) |

---

## ETAPA 08 — Preparación Cloud + AWS Local Parity

**Objetivo:** dejar todo listo para la nube **sin crear cuentas ni recursos reales**, y
**validar la IaC ejecutándola** contra un laboratorio AWS local.

**Dependencias:** Etapa 07.
**Hito que completa:** *Artefactos e IaC listos y **ejecutados** en un laboratorio AWS local.*
**Ficha:** [STAGE-08-cloud-ready.md](../stages/STAGE-08-cloud-ready.md)

> **AWS Local Parity.** Desde `Task/005.2` (2026-08-15), esta etapa deja de limitarse a
> `terraform fmt` + `validate` —que comprueban sintaxis, no comportamiento— e incorpora
> `plan`, `apply`, inspección, *drift* controlado, `destroy` y reconstrucción **contra un
> emulador AWS local**, con **una sola definición de Terraform** para ambos destinos y
> **cero recursos AWS reales**. Los **4 identificadores y nombres de tarea no cambian**.
> Estrategia: [aws-local-parity.md](../architecture/aws-local-parity.md) ·
> [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) (**Aceptada**).

> **Corrección de la columna *Repos* — 2026-09-13 (`Task/023`).** La fila de `Task/023`
> declaraba solo `backend`, omitiendo el repositorio de documentación. No era una
> excepción deliberada: [`WORKFLOW.md`](WORKFLOW.md) §6 obliga a actualizar `STATUS.md`,
> `ROADMAP.md`, la ficha y el reporte en **cada** tarea, y §7 sitúa esos documentos
> **solo** en `personal-blog-infra`. Las tareas comparables ya lo declaraban así
> —`Task/019` «frontend, infra (documentación)», `Task/020` «backend, infra
> (documentación)», `Task/022` «backend, infra»—. La **propiedad funcional de `Task/023`
> sigue siendo `backend`**. La fila de `Task/024` arrastraba la misma omisión y quedó
> anotada para su propio preflight.
>
> **Cierre de esa anotación — 2026-09-13 (`Task/024`, D-024-1).** La fila de `Task/024`
> declara ya «backend, infra (documentación)». Su **propiedad funcional sigue siendo
> `backend`**: lo que faltaba era el repositorio donde viven ficha, reporte, `STATUS.md`,
> `ROADMAP.md` y la ficha de etapa. `personal-blog-frontend` **no participa**.

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/023-Compatibilidad-FastAPI-Lambda` | Adaptador de FastAPI para API Gateway HTTP API y Lambda. Compatible además con la Lambda emulada del laboratorio. | backend, infra (documentación) | 022 ✔ | **Aprobada** (2026-09-13) — `app/lambda_handler.py` sobre `mangum==0.22.0` con `lifespan="off"`; **T-04 Satisfecho y Vigente**; 42 pruebas nuevas y flujo administrativo real a través del *handler*. **H-023-3** sigue **abierto y no diagnosticado** |
| `Task/024-Artefacto-ZIP-Lambda` | Paquete Linux reproducible. Validación de tamaño. Checksums. **Artefacto validable ejecutándolo** en el laboratorio. | backend, infra (documentación) | 023 ✔ | **Aprobada** (2026-09-13) — ZIP reproducible byte a byte (`6580410109207f33…`) construido en la imagen oficial del runtime de Lambda fijada por digest; **41/41** distribuciones de ejecución y **0** de desarrollo; **41,28 MiB** comprimido y **108,80 MiB** descomprimido; *handler* ejecutado **desde el ZIP** en un proceso Linux aislado, con cargas nativas y **tres controles negativos** de aislamiento. Lleva el avance a **24 de 41 — 59 %** y la ETAPA 08 a **2 de 4 — 50 %**. [Reporte](../task-reports/TASK-024-report.md) |
| `Task/025-Terraform-Cloud` | Terraform **portable**: módulos compartidos, provider AWS oficial, destino local y destino real. `plan`/`apply`/`destroy` **ejecutados en local**. Matriz de paridad. Guardas *fail-closed*. Resuelve **D-06**. **Amplía el CI de `Task/021` con `terraform fmt` y `validate`.** Sin recursos reales. | infra | 022, **024** | **Aprobada** (2026-09-14) — Ciclo completo ejecutado contra el laboratorio local y **camino crítico demostrado** (`GET /health` → **200** por API Gateway v2 → Lambda). **Resultado histórico del 2026-09-14 sobre 2.0.1:** 11 PASS literal + 1 con excepción humana (H-025-1); 79 identidades S-09 aceptadas temporalmente (H-025-6/H-025-7). El addendum 027.1, **aprobado el 2026-09-21**, cierra técnicamente H-025-1 y reduce H-025-6 a dos identidades; H-025-7 permanece en nueve. **D-06 RESUELTA**; el bucket de estado **no existe**. [Ficha](../tasks/TASK-025-terraform-cloud.md) · [Reporte](../task-reports/TASK-025-report.md) |
| `Task/026-Runbooks-de-Despliegue` | Creación. Validación del destino. Rollback. *Drift*. Destrucción. Recuperación. Transición a AWS. | infra | 024, 025 | **Aprobada** (2026-09-15) — cinco runbooks **Vigentes**, guardas *fail-closed* endurecidas y ciclo real completo contra el laboratorio; **rollback real no ejecutado** por precondición ausente, registrado como deuda sin fingir evidencia. Completó la **ETAPA 08** (4/4) y llevó el avance histórico del 2026-09-15 a **26/41 ≈ 63 %**, antes de la aprobación de Task/027. Sin AWS real. [Ficha](../tasks/TASK-026-deployment-runbooks.md) · [Reporte](../task-reports/TASK-026-report.md) |

---

## ETAPA 09 — Cuentas y Seguridad Cloud

**Estado: En progreso, 1/3 ≈ 33 %.** Task/027 aprobada el 2026-09-17; Task/028 no iniciada.

**Objetivo:** crear las cuentas cloud con controles de costo y acceso **antes** de
desplegar nada.

**Dependencias:** Etapa 08.
**Hito que completa:** *Cuentas cloud seguras, con presupuesto y **acceso de GitHub Actions a
AWS sin credenciales permanentes** (OIDC, `Task/028`).* La identidad del **VPS hacia AWS**
sigue abierta en **D-16** (`Task/029`), y **Cloudflare y el proveedor del VPS** pueden exigir
otro modelo (`Task/039`). Acotado en `Task/005.6`.
**Ficha:** [STAGE-09-cloud-accounts.md](../stages/STAGE-09-cloud-accounts.md)

> **`Task/029` cambia de alcance, no de número.** Desde `Task/005.3` (2026-08-15,
> **aprobada**) la base de datos de producción deja de ser un servicio administrado y pasa
> a ser **PostgreSQL autogestionado en un VPS externo, con PgBouncer delante**, mientras el
> backend permanece en AWS Lambda. **El identificador `029` no cambia** y el roadmap sigue
> teniendo **41 tareas**. Estrategia:
> [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) ·
> [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md).

> **`Task/029` define y prepara; no valida contra recursos que todavía no existen**
> (aclarado en `Task/005.5`). Los *gates* que exigen S3 (`Task/030`) o la Lambda real
> (`Task/032`) se validan en su tarea propietaria y, definitivamente, en `Task/040`. Ver
> [STAGE-09](../stages/STAGE-09-cloud-accounts.md).

> **`Task/029` absorbe tres materias más — `Task/006.2` (2026-08-23, aprobada).** El
> **identificador `029` no cambia** y el roadmap sigue teniendo **41 tareas**. Se le confirma
> el *ownership* de: **el mecanismo de secretos cifrados del host** (**D-17**; SOPS + age es
> candidato, no decisión), **el mecanismo de configuración del sistema operativo** (**D-18**;
> Ansible, cloud-init o scripts idempotentes — **nunca Terraform**) y **la instalación y
> configuración de Grafana Alloy** como agente del *baseline* de observabilidad que ya tenía
> asignado. Detalle:
> [target-production-architecture.md](../architecture/target-production-architecture.md) §9,
> §11 y §17.

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/027-Configurar-Cuentas-y-Presupuestos` | AWS. Cloudflare. MFA. Presupuestos. Alertas. | infra | 026 | **Aprobada** (2026-09-17) — Gates A–E y DoD completos; D-13 resuelta: USD 20 global/USD 5 AWS. Free Plan/créditos preservados; cero access keys, Organizations, Identity Center, SNS y Budget Actions; CAD 1/1 conservado sin cambios. [Ficha](../tasks/TASK-027-cloud-accounts-and-budgets.md) · [Reporte](../task-reports/TASK-027-report.md) **Su rama es la entrega consolidada:** integra además el mantenimiento `Task/027.1-Corregir-Regresion-S09-MinIO` mediante `merge --no-ff`, que **no cuenta entre las 41** y **no altera el avance**. [Ficha 027.1](../tasks/TASK-027.1-fix-s09-minio-regression.md) · [Reporte 027.1](../task-reports/TASK-027.1-report.md) |
| `Task/028-GitHub-OIDC-AWS` | Roles temporales de **GitHub Actions → AWS**. Sin credenciales AWS permanentes. **No cubre la identidad del VPS** (**D-16**, `Task/029`). | infra | 027 | Pendiente |
| `Task/029-Preparar-PostgreSQL-Produccion-en-VPS` | Selección del VPS por costo, región y RTT **medido**. PgBouncer. TLS, **ciclo de vida del certificado** y SCRAM. Firewall y SSH. Usuarios, roles y límites de conexión. Backup **fuera del host** y **restore demostrado** contra un destino disponible entonces. **Baseline de observabilidad del VPS con Grafana Alloy.** **Mecanismo de secretos cifrados del host** (**D-17**) y **mecanismo de configuración del sistema operativo** (**D-18**). Decide **D-16** (identidad del VPS hacia AWS). | infra | 027 | Pendiente |

---

## ETAPA 10 — Despliegue Cloud

**Objetivo:** desplegar el blog en la nube y publicar el primer contenido real.

**Dependencias:** Etapa 09.
**Hito que completa:** *Blog en línea y accesible por dominio propio.*
**Ficha:** [STAGE-10-cloud-deployment.md](../stages/STAGE-10-cloud-deployment.md)

> **Reutiliza, no reinventa.** `Task/030`–`Task/033` materializan contra AWS real los
> **módulos ya construidos y validados en `Task/025`**. Aquí se documenta qué funcionó sin
> cambios, qué exigió otra configuración, qué exigió adaptación y qué no era simulable en
> local, y se actualiza la
> [matriz de paridad](../architecture/aws-local-parity.md) con evidencia real. **AWS real es
> la autoridad final.**

> **Observabilidad — precisado en `Task/006.2`, aprobada.** `Task/031` mantiene
> **CloudWatch en modo mínimo** —retención corta y explícita, alarmas imprescindibles— y
> **decide D-20**: con qué mecanismo IAM de **solo lectura** accederá Grafana Cloud a
> CloudWatch. **Sigue siendo solo AWS: no observa el VPS**, cuya telemetría la envía
> **Grafana Alloy** desde `Task/029`.

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/030-Desplegar-Amazon-S3` | Bucket. CORS. Políticas. URLs prefirmadas. Lifecycle. Object storage y medios. **Destino, política, retención y *lifecycle* de los backups del VPS** —**owner único de ese tramo**; el mecanismo de backup es de `Task/029`— y **materialización de la identidad decidida en D-16**. Valida `S3Storage` contra S3 real. Resuelve **D-08**. | infra | 029 | Pendiente |
| `Task/031-Desplegar-SSM-y-CloudWatch` | **SSM `SecureString`** para los secretos de la Lambda, con permisos IAM mínimos. **CloudWatch mínimo**: logs y métricas nativas, retención corta y explícita (**D-11**), alarmas mínimas. **Base de la integración AWS → Grafana Cloud**: decide **D-20** y su modelo IAM de solo lectura. **Solo AWS: no observa el VPS.** | infra | 029 | Pendiente |
| `Task/032-Desplegar-AWS-Lambda` | Función FastAPI en Lambda por **artefacto ZIP**. IAM. **Configuración no secreta por variables de entorno y secretos desde SSM.** `DATABASE_URL` apuntando a **PgBouncer**, con **TLS** hacia el VPS. Límites (**D-12**). **Reserved Concurrency** coherente con el pool de PgBouncer. *Wiring* de `S3Storage`. **Logging compatible con la observabilidad elegida.** | infra | 030, 031 | Pendiente |
| `Task/033-Desplegar-API-Gateway` | **HTTP API**. Rutas hacia la Lambda. CORS. Throttling. Dominio del API si corresponde. | infra | 032 | Pendiente |
| `Task/034-Desplegar-Cloudflare-Pages` | **Cloudflare Pages**: build de React, variables del build y publicación de la SPA. **Owner del despliegue del frontend**; DNS, CDN y WAF son de `Task/035`. | infra, frontend | 033 | Pendiente |
| `Task/035-Configurar-DNS` | Dominio principal, `www`, `api` y `media` si corresponde. **DNS, CDN y WAF de Cloudflare.** Resuelve **D-07**; la topología lógica ya viene fijada por **D-15** (`Task/011`). | infra | 034 | Pendiente |
| `Task/036-Publicar-Primer-Contenido` | **Primera ejecución de las migraciones en producción.** Administrador. Perfil. Artículo. Review. Video. Imágenes. | backend, frontend | 035 | Pendiente |

---

## ETAPA 11 — Automatización de Despliegues

**Objetivo:** que cada cambio aprobado llegue a la nube de forma automática y controlada.

**Dependencias:** Etapa 10.
**Hito que completa:** *CD operativo, sin acciones destructivas automáticas.*
**Ficha:** [STAGE-11-deployment-automation.md](../stages/STAGE-11-deployment-automation.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/037-Deploy-Automatico-Frontend` | GitHub Actions hacia Cloudflare Pages. | frontend | 036 | Pendiente |
| `Task/038-Deploy-Automatico-Backend` | GitHub Actions hacia Lambda usando OIDC. **Canal repetible de migraciones en producción**: quién las ejecuta, desde dónde, con qué credencial, en qué orden respecto al despliegue, cómo se revierte y qué impide una ejecución accidental. | backend | 036 | Pendiente |
| `Task/039-Automatizar-Terraform` | Plan revisable. Apply protegido. Sin destrucción automática. Validación de IaC en CI sobre emulador **efímero**, sin credenciales cloud. **Credenciales, rotación, *scopes*, entornos protegidos y guardas de destino para los tres providers: AWS, Cloudflare y VPS.** **Terraform no sustituye a Ansible, cloud-init ni a los scripts idempotentes** en la configuración del sistema operativo del VPS (**D-18**, `Task/029`). | infra | 037, 038 | Pendiente |

---

## ETAPA 12 — Lanzamiento y Operación

**Objetivo:** validar producción de extremo a extremo y proteger el costo de forma
permanente.

**Dependencias:** Etapa 11.
**Hito que completa:** *Blog lanzado, operado y con costo bajo control.*
**Ficha:** [STAGE-12-launch-and-operations.md](../stages/STAGE-12-launch-and-operations.md)

| Tarea | Descripción | Repos | Depende de | Estado |
| --- | --- | --- | --- | --- |
| `Task/040-Validacion-Final-Produccion` | Comprobación **end-to-end** de lo realmente implementado: **Cloudflare** (DNS, CDN, WAF), **Pages**, **API Gateway**, **Lambda**, **S3**, **SSM**, HTTPS, dominio, login, contenido, SEO, responsive y rollback. **Y la capa de datos: conexión a PgBouncer, PostgreSQL, disponibilidad y disco del VPS, TLS y vigencia del certificado, backup reciente y restore vigente, runbooks.** **Y la observabilidad: CloudWatch mínimo, Grafana Cloud y Alloy operando de verdad**, más la integración de **D-20** si existe. | infra, frontend, backend | 039 | Pendiente |
| `Task/041-Proteccion-de-Costos` | Presupuestos. Alarmas. Retención. Límites. Revisión periódica. **Todos los recursos productivos que cuestan dinero, no solo AWS: VPS, dominio, IPv4 si aplica, almacenamiento de backups, snapshots, transferencia, Cloudflare si aplica y Grafana Cloud** (**D-19**). Precios **vigentes en el momento**, nunca heredados, y **confirmación de que los tiers gratuitos siguen siendo aplicables** (**R-38**). | infra | 040 | Pendiente |

---

## Mapa de responsabilidades transversales

Registrado en `Task/005.5` tras la auditoría. Resuelve las cadenas que atraviesan varias
tareas y que antes no tenían un propietario inequívoco. **No añade tareas ni cambia
identificadores.**

| Cadena | Define / construye | Materializa | Valida antes del lanzamiento |
| --- | --- | --- | --- |
| **`S3Storage`** | `Task/010` — interfaz, `MinIOStorage`, código de `S3Storage`, pruebas de contrato | `Task/030` — bucket, políticas, CORS, *lifecycle*, prefirmadas · `Task/032` — *wiring* | `Task/040` |
| **Backup productivo** | `Task/029` — mecanismo, cifrado, retención, RPO/RTO y **restore demostrado** off-host | `Task/030` — destino S3, política, permisos y retención definitiva | `Task/040` — backup reciente y **restore vigente** |
| **Identidad del VPS hacia AWS** (**D-16**) | `Task/029` — **decide** el mecanismo y sus restricciones de seguridad | `Task/030` — crea el principal, la política y el destino | `Task/040` |
| **Certificado TLS de PgBouncer** | `Task/029` — emisión, CA, *hostname*, instalación, renovación y confianza desde el cliente | `Task/029` | `Task/040` — validación real desde Lambda y vigencia |
| **Observabilidad del VPS** | `Task/029` — *baseline*: uptime, CPU, RAM, disco, PostgreSQL, PgBouncer, fallo de backup, caducidad de certificado | `Task/029` | `Task/040` |
| **Migraciones en producción** | `Task/036` — **primera** ejecución | `Task/038` — canal repetible, credencial, orden, *rollback* y protección | `Task/040` |
| **Medios públicos y URLs** (**D-08**) | `Task/010` — persiste **claves de objeto** · `Task/016` — `og:image` estable | `Task/030` — resuelve **D-08** | `Task/040` |
| **Credenciales CI multi-provider** | `Task/028` — **solo** GitHub → AWS | `Task/039` — AWS, Cloudflare y VPS: rotación, *scopes*, entornos protegidos y guardas de destino | `Task/040` |
| **Topología lógica de dominios** (**D-15**) | `Task/011` — mismo *site*, subdominios o dominios separados; cookies y CORS | `Task/018` — CORS efectivo | `Task/035` — dominio concreto y DNS (**D-07**) |
| **Observabilidad de producción** (`Task/006.2`) | `Task/029` — **Grafana Alloy** y el *baseline* del VPS · `Task/031` — **CloudWatch mínimo** y la base de **D-20** | `Task/029`, `Task/031` | `Task/040` — que **opera de verdad**, no que está configurada |
| **Telemetría portable de la aplicación** (`Task/006.2`) | `Task/017` — logs JSON y correlation ID, **sin acoplar el dominio a ningún destino** | `Task/018` — redacción y endurecimiento | `Task/040` |
| **Secretos del VPS** (**D-17**, `Task/006.2`) | `Task/029` — herramienta, custodia y rotación de la clave | `Task/029` | `Task/040` |
| **Configuración del sistema operativo del VPS** (**D-18**, `Task/006.2`) | `Task/029` — mecanismo y *drift* | `Task/029` · `Task/039` no lo sustituye con Terraform | `Task/040` |
| **Costo de la observabilidad** (**D-19**, `Task/006.2`) | `Task/027` — presupuesto (**D-13**) | `Task/031`, `Task/029` | `Task/041` — **precios reales del momento** |

**Reglas que esto fija:**

- **Ninguna tarea exige como evidencia final algo que solo existe después de ella.**
- `Task/017` es observabilidad **local**; `Task/031` es **solo AWS**. Ninguna de las dos
  observa el VPS: eso es de `Task/029` con **Grafana Alloy**, verificado por `Task/040`.
- **El backup tiene un único owner por tramo**: mecanismo en `Task/029`, destino y retención
  en `Task/030`, verificación en `Task/040`. **No se duplica.**
- `Task/029` **define y prepara**; `Task/030`/`Task/032` **materializan**; `Task/040`
  **verifica**, no implementa.

---

## Cálculo del avance

```
avance_etapa  = tareas_aprobadas_en_etapa / tareas_totales_en_etapa
avance_global = tareas_aprobadas_totales  / 41
```

Actualmente: **27/41 ≈ 66 %**. ETAPA 09: **1/3 ≈ 33 %**.

> **Corrección de *drift* documental, 2026-09-06.** Este bloque afirmaba `9 / 41 = 22 %`
> mientras [STATUS.md](STATUS.md) registraba **16 / 41**: el cálculo había dejado de
> actualizarse en aprobaciones anteriores. El valor canónico es y era el de `STATUS.md`.
> **No lo causó `Task/017` y no contó como trabajo funcional suyo**; se corrigió aquí porque
> la tarea ya modificaba este documento para su propio estado. El **17.º** del numerador es
> `Task/017`, aprobada el 2026-09-06 — eso sí es avance.

**Precisión sobre O-09.** La fila de `Task/017` ligaba la *telemetría portable* a **O-09**.
Son cosas distintas y ambas se conservan intactas: la portabilidad es el **principio 9** de
[`overview.md`](../architecture/overview.md) §5, cerrado por `Task/006.2` con
[ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md); **O-09** es la
privacidad de la telemetría **exportada a un tercero**, y sus propietarios siguen siendo
`Task/029`, `Task/018` y `Task/040`. `Task/017` **no** es owner de O-09.

Las tareas de mantenimiento (`Task/002.1`, `Task/005.1`, `Task/005.2`, `Task/005.3`,
`Task/005.4`, `Task/005.5`, `Task/005.6`, `Task/005.7`, `Task/006.1`, `Task/006.2`) **no
entran en el numerador ni en el denominador**.

> **Precisión de `Task/027.1`, 2026-09-18.** Esa enumeración es **ilustrativa, no
> exhaustiva**: se escribió cuando los mantenimientos llegaban hasta `Task/006.2` y no se
> amplió después. La regla es la que manda y **no depende de la lista**: **ninguna tarea con
> numeración `NNN.M` entra en el numerador ni en el denominador**, incluidas
> `Task/009.1`, `Task/012.1`, `Task/013.1`, `Task/019.1`, `Task/020.1`, `Task/020.2`,
> `Task/020.3`, `Task/026.1` y **`Task/027.1-Corregir-Regresion-S09-MinIO`**.
> Esta última recibió su primera aprobación para MinIO el 2026-09-20 y la del addendum
> Floci el 2026-09-21. **Ninguna de las dos altera el avance.** El denominador sigue
> siendo **41** y el numerador solo lo mueve la aprobación de una tarea canónica.

Ver estado vigente en [STATUS.md](STATUS.md).
