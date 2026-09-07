# STATUS — Estado del proyecto Blog Personal

**Última actualización:** 2026-09-06

---

## Vista rápida

| Campo | Valor |
| --- | --- |
| **Etapa actual** | **ETAPA 05 — Calidad y Seguridad — En curso** (**2 de 3** aprobadas). ETAPAS 00 a 04 **completadas** |
| **Tarea actual** | **`Task/017-Observabilidad-Local`** — **Aprobada** el 2026-09-06 por jeffersondavila |
| **Estado de la tarea** | `Task/017-Observabilidad-Local` — **Aprobada** mediante `approved: Task/017-Observabilidad-Local`. Correlation ID `X-Request-ID` de extremo a extremo —respuesta, todas las líneas de log de la petición y `audit_events.request_id`—, `GET /ready` con sonda real de PostgreSQL y almacenamiento bajo **presupuesto total** por debajo del `timeout` del proxy, redacción automática de secretos en el log (cierra el plano local de **R-36**) y `healthCheck` de Traefik en `/ready` conservando `/health` como liveness de Docker. **1808** pruebas de backend en verde y **1** omitida (estructural de Windows), con `-W error`. **0 dependencias nuevas**. **O-07** quedó verificado por Docker por el agente; la comprobación en la **interfaz de Portainer** la cubre la aprobación del usuario, y así consta (reporte §22). Detalle en el [reporte](../task-reports/TASK-017-report.md). Cuenta en el avance: **17 de 41** |
| **Tarea aprobada anterior a `Task/017`** | `Task/016-SEO-Accesibilidad-y-Rendimiento` — **Aprobada** mediante `approved: Task/016-SEO-Accesibilidad-y-Rendimiento`. **E-02**, **E-04**, **E-05**, **E-07**, **E-08** cumplidos; **E-03 NO cerrado** y **E-06 parcial**, ambos con su motivo medido. **688** pruebas de frontend y **1631** de backend en verde. **0 dependencias nuevas**. Detalle en el [reporte](../task-reports/TASK-016-report.md). Cuenta en el avance: **16 de 41** |
| **Tarea aprobada anterior a `Task/016`** | `Task/015-Panel-Administrativo` — **Aprobada** el 2026-09-05. **18 superficies**, dashboard completo, sesión administrativa, editor Markdown y medios. **600 pruebas**, cero dependencias nuevas. **D-04 resuelta**; completa ETAPA 04 |
| **Tarea aprobada anterior** | `Task/014-Sitio-Publico` — **Aprobada** el 2026-09-05 por jeffersondavila. **Doce superficies** del sitio público sobre el sistema de diseño y los diez recursos públicos del API, con estados de carga, vacío, error y `404`; estado del listado en la URL; imágenes solo por `access_url` con `alt_text`; **Markdown sanitizado** (ADR-005) en un pipeline único reutilizable por `Task/015`; videos con **lista cerrada** `youtube`/`vimeo` y *fail-closed*; enlaces externos seguros. Asume **A-02** y **A-04**, continúa **A-01**. **440 pruebas** en verde y **dos** dependencias nuevas autorizadas |
| **Tarea aprobada previa** | `Task/012-API-Administrativa` — **Aprobada** el 2026-09-03 por jeffersondavila. Las **23 rutas administrativas** del contrato, validación de publicación por tipo, *slug* estable, transiciones seguras ante concurrencia, **escritura y exigencia del texto alternativo donde se usa la imagen** y auditoría de once acciones nuevas. **Completa la ETAPA 03** |
| **Tarea aprobada de la ETAPA 03** | `Task/011-Autenticacion-Administrativa` — **Aprobada** el 2026-09-01. Los **tres** endpoints de autenticación, **Argon2id**, sesión opaca *server-side*, bloqueo de cuenta seguro ante concurrencia, límite de tasa en PostgreSQL y auditoría sin secretos. Cierra **D-15**, **D-02** y **D-09** |
| **Tarea aprobada anterior de la ETAPA 03** | `Task/010-Almacenamiento-Compatible-S3` — **Aprobada** el 2026-08-28. Interfaz `ObjectStorage` con **dos implementaciones reales** que superan la misma suite de contrato, gestión de imágenes y miniaturas, y cierre de **D-009-O** |
| **Último mantenimiento aprobado** | `Task/004.1-Corregir-Backup-Rutas-Literales` — **Aprobada** el 2026-09-06 por jeffersondavila. Corrige un defecto **demostrado en ejecución** del sistema de respaldo de `Task/004`: una ruta ya resuelta se pasaba a parámetros de PowerShell que interpretan comodines, de modo que una clave de objeto con `[` abortaba el respaldo. El mismo defecto afectaba a la **prueba de restauración**. Respaldo real, verificación y restauración **superados** sobre 64 objetos, 44 de ellos con corchetes. **No cuenta en las 41 tareas** ni altera el avance |
| **Mantenimiento anterior a `Task/004.1`** | `Task/012.1-Exponer-Auditoria-Para-Dashboard` — **Aprobada** el 2026-09-05 por jeffersondavila. Añade **una** operación administrativa de solo lectura, `GET /api/v1/admin/audit-events`, que cierra la laguna entre `MVP_SCOPE.md` §3.3 y la API administrativa. **Sin migración**, sin filtros y sin datos personales; la inmutabilidad de `AuditEvent` queda intacta y leer no audita. **No cuenta en las 41 tareas** ni altera el avance |
| **Mantenimiento anterior** | `Task/013.1-Corregir-Drift-Documental-Post-Merge` — **Aprobada** el 2026-09-04. Convierte en instantánea histórica fechada la sección 24 del reporte de `Task/013`, que conservaba estado operativo de Git redactado en presente. **No cuenta en las 41 tareas** ni altera el avance |
| **Mantenimiento previo** | `Task/009.1-Corregir-Drift-Documental-Post-Merge` — **Aprobada** el 2026-08-27. Cierra el drift documental posterior a la fusión de `Task/009` y añade el **criterio 12** a la Definition of Done. No cuenta en las 41 tareas |
| **Mantenimiento anterior a `Task/009`** | `Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` — **Aprobada** el 2026-08-23. Formaliza la arquitectura objetivo de producción y acepta **ADR-008**. No cuenta en las 41 tareas |
| **Mantenimiento tras `Task/006`** | `Task/006.1-Corregir-Drift-Documental-Post-Merge` — **Aprobada** el 2026-08-21. Cierra el drift documental posterior a la fusión de `Task/006`. No cuenta en las 41 tareas |
| **Próxima tarea prevista** | `Task/018-Endurecimiento-de-Seguridad` — **Pendiente, no iniciada**. **No se inicia** hasta que `Task/017` esté aprobada y normalizada; su rama nace desde `main` actualizado y limpio ([WORKFLOW §2.1 y §6.1](WORKFLOW.md)) |
| **Avance global** | **41 %** — 17 de 41 tareas aprobadas |
| **Bloqueos activos** | **0 que detengan trabajo.** `Task/016` quedó **Aprobada** con **4 limitaciones acotadas**, cada una con propietario: **B-016-1** `og:image` por contenido (**D-08**, `Task/030`) · **B-016-2** Open Graph por URL sin JavaScript (**D-21** / **ADR-009**, sin tarea asignada) · **B-016-3** código HTTP `404` real (`Task/034`) · **B-016-4** evidencia con contenido real (`Task/022`). **B-015-1** sigue **resuelto** por `Task/012.1` |
| **Riesgos abiertos** | **44** (R-01 y **R-08** cerrados; **R-29** a **R-35** abiertos desde el 2026-08-15; **R-36** añadido en `Task/005.6`; **R-37** en `Task/005.7`; **R-38** a **R-42** desde el 2026-08-23, `Task/006.2`; **R-43** a **R-46** desde el 2026-09-01, `Task/011`; **R-016-1** a **R-016-11** desde el 2026-09-05 con la definición de `Task/016`, registrados en su ficha §16) |
| **Decisiones abiertas** | **13** — **D-21** (estrategia de *rendering*) añadida por `Task/016`;  D-05, D-14, D-01 resueltas; **D-15**, **D-02** y **D-09** resueltas en `Task/011` y **Vigentes** desde el 2026-09-01; **D-03** resuelta en `Task/013` y **Vigente** desde el 2026-09-04; **D-04** resuelta en `Task/015` y **Vigente** desde el 2026-09-05; **D-16** añadida en `Task/005.5`; **D-17** a **D-20** en `Task/006.2` |

> **Recuento tras la aprobación de `Task/017`, 2026-09-06:** el avance pasa a
> **17 de 41 — 41 %** y la ETAPA 05 a **2 de 3 — 67 %**. `Task/016`, aprobada el mismo día,
> lo había dejado en 16 de 41 — 39 %. La aprobación del usuario es el hecho que suma avance;
> las tareas de mantenimiento no cuentan en las 41.
>
> **Aprobada con limitaciones declaradas, no con todo cerrado.** **E-03** queda **no
> cerrado** y **E-06 parcial**, ambos con su motivo **medido** en cuatro canales. Lo que se
> aprobó respecto del *rendering* es **haber abierto** la reconsideración: **D-21** sigue
> **Abierta** y **ADR-009** en **Propuesta**.

---

## Última tarea aprobada — `Task/017-Observabilidad-Local`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/017-Observabilidad-Local` |
| **Etapa** | ETAPA 05 — Calidad y Seguridad |
| **Estado** | **Aprobada** el 2026-09-06 por jeffersondavila |
| **Repositorios** | `personal-blog-backend` (funcional) · `personal-blog-infra` (gobierno, Traefik, runbook). **El frontend no participa** |
| **Dependencias** | `Task/014`, `Task/015` y `Task/016`, todas **Aprobadas** |
| **Documentos** | [ficha](../tasks/TASK-017-local-observability.md) · [reporte](../task-reports/TASK-017-report.md) |
| **Pruebas** | **1808** en verde, **1** omitida (`time.tzset` no existe en Windows), `-W error`, con PostgreSQL y MinIO reales. Baseline previo: 1631 |
| **Dependencias nuevas** | **0** |

### Qué entrega

| Requisito | Alcance conseguido |
| --- | --- |
| **O-01** | Logs JSON por `stdout`, una línea por evento; el formato `text` conserva redacción y correlation ID |
| **O-02** | `X-Request-ID` fijada como contrato (api-contracts §9.1–§9.3): 8–64 caracteres de `[A-Za-z0-9_-]`, UUIDv4 al generar, y política *fail-safe* ante cabecera inválida o repetida |
| **O-03** | `/health` **verificado** como liveness: no consulta dependencias |
| **O-04** | `GET /ready` comprueba PostgreSQL y almacenamiento con **presupuesto total** —no una suma de timeouts—, y responde `503` sin nombrar el componente |
| **O-05** | *Participación*: el `AuditEvent` lleva el **mismo** `request_id` que la respuesta y los logs. El requisito lo cumplen `Task/011` y `Task/012` |
| **O-07** | Logs del backend legibles por Docker — **verificado por el agente**. La comprobación en la **interfaz** de Portainer la cubre la aprobación del usuario; no se registra como evidencia del agente porque no lo fue |
| **O-08** | Redacción automática e idempotente por nombre de campo y por forma del valor, aplicada también a la cadena de excepciones |

### Qué NO entrega

**O-06**, **O-09** y **O-10** siguen fuera: son observabilidad **cloud** y del VPS, con
propietarios `Task/029`, `Task/031`, `Task/040` y `Task/041`. El endurecimiento de la
política de redacción sigue siendo de `Task/018`. `Task/017` **no** crea recursos cloud ni
introduce Grafana, Prometheus, Loki, Alloy, CloudWatch ni OpenTelemetry.

### Aprobación

Aprobada con la expresión exacta `approved: Task/017-Observabilidad-Local`.

**Vigentes desde la aprobación:** la cabecera **`X-Request-ID`** y su formato; la política
*fail-safe* ante cabecera inválida o repetida; **no** exponer `request_id` en el DTO del
historial; `/ready` sin nombrar el componente que falló; la sonda por `ListObjectsV2` acotado;
el **presupuesto total** de `/ready` por debajo del `timeout` del proxy; la recomendación **C**
—Docker en `/health`, Traefik en `/ready`—; y el mecanismo de redacción. Detalle en la
[ficha](../tasks/TASK-017-local-observability.md) §26.

**Registro honesto del alcance.** El veredicto previo a la aprobación fue **NO LISTA** por un
único punto: la comprobación **visual** en la interfaz de Portainer, que la sesión de
implementación no pudo producir por no disponer de navegador. **La cubre la aprobación del
usuario**, no una evidencia del agente, y así consta en el [reporte](../task-reports/TASK-017-report.md) §22.

---

## Última tarea aprobada — `Task/016-SEO-Accesibilidad-y-Rendimiento`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/016-SEO-Accesibilidad-y-Rendimiento` |
| **Etapa** | ETAPA 05 — Calidad y Seguridad |
| **Estado** | **Aprobada** el 2026-09-06 por jeffersondavila |
| **Repositorios** | frontend, backend, infra (documentación + ***wiring* local mínimo**) |
| **Dependencias** | `Task/014` y `Task/015`, ambas **Aprobadas** el 2026-09-05 |
| **Documentos** | [ficha](../tasks/TASK-016-seo-accessibility-performance.md) · [reporte](../task-reports/TASK-016-report.md) · [ADR-009](../adr/ADR-009-rendering-strategy-for-crawlers.md) |
| **Avance** | Cuenta en el avance: **16 de 41 — 39 %**. Completa **1 de 3** de la ETAPA 05 |

### Qué entrega

| Requisito | Estado |
| --- | --- |
| **E-02**, **E-04**, **E-07** | **Cumplidos con JavaScript**; parciales sin él |
| **E-03** Open Graph | **NO cerrado** — motivo medido, abajo |
| **E-05** Sitemap | **Cumplido en ambos canales** |
| **E-06** `robots.txt` y `noindex` | **Parcial** — la garantía sin JavaScript es `Task/018` |
| **E-08** | **Cumplido por construcción**, fijado por prueba con PostgreSQL real |
| **A-01…A-08** | Auditados en navegador real. **A-04** bloqueado por falta de contenido |
| **P-01, P-03, P-04, P-05** | Umbrales **U-1 a U-9** fijados y medidos |

### El resultado central: volver a medir después de implementar

`Task/005.5` exigía **comprobar**, no suponer. Se midió en cuatro canales antes y después.

Con JavaScript, las 11 superficies públicas tienen `title`, `description`, `canonical`,
Open Graph y JSON-LD **propios y correctos por URL**. **Sin** JavaScript, un *crawler*
sigue recibiendo **cero** metadatos propios de la URL — igual que antes de escribir el
código.

> **El problema no era falta de código: es el modelo de *rendering*.** Y afecta a **E-03**
> en particular porque su propósito canónico son las redes sociales (`MVP_SCOPE.md` §2.2),
> cuyos *crawlers* no ejecutan JavaScript.

Por eso se abre **D-21** con **ADR-009** en estado **Propuesta**, **sin elegir** SSR, SSG
ni prerender. **ADR-005 sigue Aceptado** y el *stack* no cambia. Es exactamente lo que
`STAGE-05` manda hacer, y donde manda detenerse.

### Dos defectos medidos y corregidos

`GET /robots.txt` y `GET /sitemap.xml` devolvían **HTTP 200 con el `index.html` de la
SPA**. Ahora responden `text/plain` y `application/xml`. Un `200` con contenido no
analizable es peor que un `404`.

### Evidencia de accesibilidad

**139 paradas de teclado** en 10 superficies: **0** sin indicador de foco, **0** problemas
estáticos, **10/10** rutas sin trampa de foco. **40 mediciones** de desbordamiento
(10 superficies × 4 anchos): **0** elementos desbordados — absorbe la deuda 2 de
`Task/015`. **A-08** verificado provocando un error real.

**No se afirma WCAG 2.1 AA del producto:** un recorrido automático cubre una fracción de
los criterios, y **A-04** no puede observarse sin contenido.

### Decisiones tomadas, ninguna vigente todavía

| # | Decisión | Qué **no** decide |
| --- | --- | --- |
| **D-016-A** | `og:image` es un activo **estático** del sitio, versionado en `public/` | Nada de **D-08**: no crea URL estable de medios, ni caché, ni TTL, ni CDN |
| **D-016-B** | El **backend** genera `sitemap.xml` en *runtime* | No amplía el contrato más de lo necesario: `updated_at` no se expone |
| **D-21** | *(abierta, no resuelta)* Estrategia de *rendering* | No elige ninguna opción; ADR-009 queda en **Propuesta** |

### Bloqueos — cuatro, todos parciales

**B-016-1** `og:image` por contenido (**D-08**, `Task/030`) · **B-016-2** Open Graph por
URL sin JavaScript (**D-21**) · **B-016-3** código HTTP `404` (`Task/034`) · **B-016-4**
evidencia con contenido real (`Task/022`). Ninguno impidió entregar.

La base local no tiene contenido **ni administrador**, y **no se fabricó ninguno** para
maquillar evidencia.

### Validaciones

| Repositorio | Resultado |
| --- | --- |
| frontend | `format:check`, `lint`, `typecheck` y `build` en **exit 0**; **688 / 688** pruebas en **72** archivos (desde 600/67); guardas SEO **15/15** y **P-05** **27/27** |
| backend | `ruff`, `ruff format` y `mypy` (strict, 295 archivos) en **exit 0**; **1631 passed, 1 skipped** con PostgreSQL y MinIO reales y `-W error` (desde 1572); imagen Docker construye |
| infra | `docker compose config` **válido** |

**Sin migración nueva:** ni el sitemap ni la miniatura tocan el esquema físico.

### Cero dependencias nuevas, verificado

`react-helmet` y `react-helmet-async` se descartaron **por medición**: React 19.2.8 iza
`<title>`, `<meta>` y `<link>` al `<head>` de forma nativa. `axe`, `lighthouse` y
`playwright` también: el arnés de Chrome *headless* por CDP de `Task/013` y `Task/014`
cubrió teclado, foco, semántica, LCP, CLS, red y responsive con **0** dependencias.

### Riesgo vivo registrado

**R-016-1** — la suite del frontend es sensible a la carga de la máquina. Ya fallaba de
forma intermitente **antes** de esta tarea. Mitigado calibrando el techo de espera de
Testing Library a 4000 ms, número **derivado de medir** la suite entera
(p50 = 5 ms, p95 = 494 ms, p99 = 1050 ms, máximo = 1879 ms), no elegido. Relevante para
`Task/019`.

### Aprobación — 2026-09-06

Aprobada con la expresión exacta `approved: Task/016-SEO-Accesibilidad-y-Rendimiento`.

**Vigentes desde la aprobación:** **D-016-A** (`og:image` estático), **D-016-B** (sitemap
en el backend), los umbrales **U-1 a U-9** de `non-functional-requirements.md` §2, el
contrato de `GET /sitemap.xml`, el campo `thumbnail_access_url` y la clasificación
`infra (documentación + wiring local mínimo)`.

**Lo que la aprobación NO decide.** Es la distinción más importante de esta tarea:

| Elemento | Estado | Por qué |
| --- | --- | --- |
| **D-21** | **Abierta** | Se aprobó **haber abierto** la reconsideración con evidencia, no haber elegido estrategia |
| **ADR-009** | **Propuesta** | Documenta una decisión **todavía no tomada**: no hay nada que aceptar |
| **ADR-005** | **Aceptado**, intacto | El Markdown se sigue renderizando en cliente |
| **E-03** | **No cerrado** | Por URL exige que el *crawler* ejecute JavaScript |
| **E-06** | **Parcial** | La garantía sin JavaScript es `X-Robots-Tag`, de `Task/018` |
| **D-08** | **Abierta** | Se respondió qué URL usa `og:image`; no se cerró la decisión |

### Excepciones autorizadas al rol de `infra`

`infra` entró como repositorio **documental**. El usuario autorizó expresamente **tres
líneas de *wiring* local**, cada una por separado y todas necesarias para que la tarea
funcionara en local:

| # | Archivo | Qué añade |
| --- | --- | --- |
| 1 | `docker-compose.yml` | `BLOG_PUBLIC_SITE_BASE_URL` en el servicio `backend` |
| 2 | `docker/traefik/dynamic/routes.yml` | El enrutado de `/sitemap.xml` hacia el backend |
| 3 | `docker-compose.yml` | `VITE_SITE_BASE_URL` en `build.args` del `frontend` |

Por eso la clasificación durable de la tarea es
**`infra (documentación + wiring local mínimo)`**, y no `infra (documentación)`. **No** la
convierte en una tarea de infraestructura funcional: Nginx y su compresión, CORS,
cabeceras, `X-Robots-Tag` y Cloudflare Pages siguen fuera, con su propietario.

La línea 2 no hace falta en producción: el `Sitemap:` apunta al dominio del API, servido
por API Gateway sin Traefik de por medio. La 3 evita que `canonical`, `og:url` y
`og:image` queden acoplados a un puerto fijo, y se verificó **sin tocar `.env`**: al
resolver la configuración con `TRAEFIK_HTTP_HOST_PORT=9317`, ambos argumentos de build
pasan a `http://localhost:9317`.

---

## Última tarea aprobada — `Task/015-Panel-Administrativo`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/015-Panel-Administrativo` |
| **Etapa** | ETAPA 04 — Experiencia del Usuario |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las **15 de 41 aprobadas** |
| **Estado** | **Aprobada** el 2026-09-05 por jeffersondavila mediante `approved: Task/015-Panel-Administrativo`. **Sin bloqueos canónicos** |
| **Repositorios** | `personal-blog-frontend` (funcional) · `personal-blog-infra` (gobierno documental). `personal-blog-backend` **sin rama y sin cambios** |
| **Rama** | `Task/015-Panel-Administrativo`, nacida de `main` con `HEAD == main` verificado y actualizada por avance rápido al `main` que incorpora `Task/012.1` |
| **Dependencias** | `Task/013` y `Task/014` — **Aprobadas** ✔; contratos de `Task/010`, `Task/011`, `Task/012` y `Task/012.1` — **Aprobados** ✔ |
| **Ficha** | [TASK-015](../tasks/TASK-015-admin-panel.md) |
| **Reporte** | [TASK-015-report.md](../task-reports/TASK-015-report.md) |

### Qué construye

Las **18 superficies** del panel administrativo —acceso, dashboard, listados y formularios de
los cuatro tipos publicables, etiquetas, biblioteca de medios, perfil y 404 del panel— sobre
las primitivas de `Task/013` y los **27 patrones de ruta / 39 operaciones HTTP** cerrados por
`Task/011`, `Task/012` y `Task/012.1`. Incluye sesión administrativa sobre la cookie
`HttpOnly`, editor Markdown con **vista previa por el mismo pipeline sanitizado** de
`Task/014`, carga y selección de imágenes, y las transiciones de publicación como
subrecursos.

### Qué asume y qué difiere

Asume **A-03** (labels asociadas), **A-08** (errores anunciados), **S-03** en la vista previa
y **P-05** (el panel no viaja en el código público). Continúa **A-01** y **A-02**; preserva
**A-04** a **A-07**. **No** hace auditoría de accesibilidad ni SEO (`Task/016`), ni CORS ni
cabeceras (`Task/018`), ni toca el backend.

### Dashboard mínimo — las tres piezas, ya construibles

`Task/012.1` cerró la laguna que impedía la tercera. `MVP_SCOPE.md` §3.3 queda completo
dentro de `Task/015`:

| Pieza | Fuente de datos |
| --- | --- |
| Conteo por tipo y estado | `GET /admin/{recurso}?status={estado}&page_size=1`, leyendo `total` |
| Últimos elementos modificados | `GET /admin/{recurso}?page_size=5`, ya ordenado `updated_at` desc |
| **Últimos eventos de auditoría** | **`GET /api/v1/admin/audit-events`** — `Task/012.1`, **Aprobada** |

### Decisiones vigentes

**D-015-A** a **D-015-H**, más **D-015-J** y **D-015-K**, **Vigentes** por la aprobación
del usuario del 2026-09-05. **D-04 queda resuelta**: `<textarea>` nativo más
`MarkdownContent`, con **cero dependencias nuevas**. Registro en
[open-decisions.md](../architecture/open-decisions.md#d-04--editor-markdown--resuelta).

**D-015-I quedó retirada** el 2026-09-05 y **no se restaura**. Proponía entregar dos de las
tres partes del dashboard y diferir los eventos de auditoría a `Task/017`, cuyos repositorios
son `backend, infra` —sin `frontend`— y que **depende de `Task/015`**. La resolución real fue
`Task/012.1`.

### Qué se validó (2026-09-05)

| Aspecto | Resultado |
| --- | --- |
| Pruebas | **600 / 600** en 67 archivos. Baseline heredado: **440**. **+160** nuevas (**+43** en la corrección auth) |
| Compuertas | `format:check`, `lint`, `typecheck` y `build` sin errores |
| Dependencias | **0 nuevas**: `package.json` y el lockfile **sin cambios** |
| **P-05** | Las cinco comprobaciones en verde sobre `dist/` real, con **mutación** que las pone rojas y se revierte |
| Dashboard | **17 peticiones** —12 + 4 + 1— fijadas por prueba, y las tres piezas de `MVP_SCOPE.md` §3.3 |
| A-03 / A-08 | Etiquetas asociadas y errores anunciados, con prueba por superficie |
| Backend | **Sin rama y sin cambios** |

**Limitación declarada:** no se ejecutó la validación visual a 320, 390, 768 y 1280 px —esta
sesión no dispone de automatización de navegador—, y sin administrador ni perfil en la base
local (`Task/022`) el recorrido funcional real no puede completarse. Detalle en el
[reporte](../task-reports/TASK-015-report.md) §14.

### Limitaciones declaradas

1. **No se pueden insertar imágenes dentro del cuerpo Markdown**: `access_url` caduca y no
   debe almacenarse (`api-contracts.md` §12). La URL estable es **D-08** (`Task/030`).
2. **No hay administrador ni perfil en la base local**: la semilla es de `Task/022`, así que
   el recorrido funcional en el navegador quedará parcialmente sin validar.
3. **El backend no tiene middleware CORS** (`Task/018`): en local el panel debe servirse en
   el mismo origen que el API.
4. **`request_id` no está en el DTO del historial** (`v1` de `Task/012.1`): el panel no puede
   mostrar el correlation ID de un evento hasta que `Task/017` fije su cabecera.

---

## Último mantenimiento aprobado — `Task/012.1-Exponer-Auditoria-Para-Dashboard`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/012.1-Exponer-Auditoria-Para-Dashboard` |
| **Tipo** | **Mantenimiento funcional de la API administrativa.** **No cuenta** dentro de las 41 y **no altera el avance** |
| **Estado** | **Aprobada** ✔ el 2026-09-05 por jeffersondavila (definición e implementación el mismo día) |
| **Dependencia** | `Task/012-API-Administrativa` — **Aprobada** ✔ |
| **Repositorios** | `personal-blog-backend` (funcional) · `personal-blog-infra` (gobierno y contratos). `personal-blog-frontend` **sin rama y sin cambios** |
| **Rama** | `Task/012.1-Exponer-Auditoria-Para-Dashboard`, nacida de `main` en **worktrees dedicados**, con `HEAD == main` verificado: `ce166fb7…` (backend) · `5a8f4c8e…` (infra) |
| **Ficha** | [TASK-012.1](../tasks/TASK-012.1-audit-events-for-dashboard.md) |
| **Reporte** | [TASK-012.1-report.md](../task-reports/TASK-012.1-report.md) |

### Por qué existe

`MVP_SCOPE.md` §3.3 fija como **alcance mínimo** del dashboard tres cosas: conteo por tipo y
estado, últimos elementos modificados y **últimos eventos de auditoría**. Las dos primeras ya
se construían con el contrato de `Task/012`; la tercera **no**: ninguna de las **38
operaciones HTTP** administrativas de entonces leía `audit_events`. El módulo `audit` del
backend no tenía capa `presentation`, su puerto de dominio declaraba un solo método
—`registrar`— y no existía ninguna consulta. El frontend tampoco podía alcanzar la tabla:
`software-architecture.md` §5 lo prohíbe expresamente.

Con esta tarea el inventario administrativo pasa a **27 patrones de ruta / 39 operaciones
HTTP**, y la operación 39.ª es justamente la que faltaba.

Es una **laguna del contrato**, detectada al reconstruir el alcance del panel administrativo,
y bloquea que ese panel entregue su dashboard mínimo.

### Qué entrega

**Una** operación administrativa autenticada de solo lectura —`GET
/api/v1/admin/audit-events`—, paginada con la envoltura única del proyecto, ordenada por
`occurred_at` descendente con desempate por `id` ascendente, **sin filtros** y con un DTO de
**cinco** campos: `id`, `occurred_at`, `action`, `entity_type` y `entity_id`.

**No expone** `ip_address`, `actor_id`, `event_metadata` ni `request_id`. **No requiere
migración**: `ix_audit_events_occurred_at` ya existe desde la migración `0002`, creado
—según `data-model.md` §5— justamente para el *«listado cronológico del historial»*.

### Qué NO cambia

La inmutabilidad de `AuditEvent` sigue intacta: no hay `POST`, `PUT`, `PATCH` ni `DELETE`, y
las guardas de `Task/008` no se tocan. **Leer el historial no genera un evento nuevo**
(`CONTENT_MODEL.md` §3.9). No se modifica cómo, cuándo ni qué se audita.

### Hallazgo registrado antes de tocar nada

Dos afirmaciones vigentes se apoyan en la premisa *«ninguna fuente pide exponer el historial
por API en el MVP»*, que `MVP_SCOPE.md` §3.3 contradice: el test de contrato
`test_no_se_expone_ninguna_ruta_de_auditoria` y la regla **B-08** de
`security-boundaries.md` §12.1. Ambas se enmiendan **como entregable declarado**, con el
motivo canónico de `BACKEND_TESTING_STRATEGY.md` §9. La **invariante** de solo-creación que
motivaba B-08 se conserva palabra por palabra; lo que se corrige es el hecho de superficie.

### Qué se validó (2026-09-05)

| Aspecto | Resultado |
| --- | --- |
| Pruebas | **1572 / 1572** en verde, 1 `skip` de Windows. Baseline de `main`: 1527. **+45** nuevas: **38 de integración** y 7 de contrato |
| Ciclo | **RED** de 10 fallos de contrato registrado antes de escribir código productivo; **GREEN** tras los cuatro *slices*; refactor declarado **innecesario** con su razón |
| Anti-tautología | **Tres mutaciones** de la implementación produjeron el rojo esperado y se revirtieron: desempate invertido, DTO filtrando `ip_address` y lectura que audita |
| Compuertas | `ruff check`, `ruff format --check`, `mypy` y `docker build` sin errores ni *warnings* |
| Integración | PostgreSQL y MinIO **reales**. Nunca SQLite |
| Migraciones | **Ninguna nueva.** Siguen siendo tres y el ciclo upgrade/downgrade sigue en verde |
| Tests históricos | **Tres** enmendados —uno más de los dos previstos—, todos con motivo canónico de `BACKEND_TESTING_STRATEGY.md` §9 y con un assert **más restrictivo** que el original |

### Hallazgo registrado — anomalía preexistente del harness

Con ciertas combinaciones explícitas de archivos en la línea de comandos, pytest no carga
`tests/integration/conftest.py` para el último argumento. Se reprodujo **sin ningún archivo
de esta tarea** y **no ocurre** en la invocación canónica `pytest`. Se reporta y **no se
repara**: es ajeno a este mantenimiento.

### Efecto en el avance

**Ninguno.** **B-015-1 RESUELTO** por `Task/012.1`; la aprobación de `Task/015` del
2026-09-05 lleva el avance a **15 de 41 — 37 %** y ETAPA 04 a **3 de 3 — 100 %**.
**41 identificadores intactos.**

---

## Tarea aprobada anterior — `Task/014-Sitio-Publico`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/014-Sitio-Publico` |
| **Etapa** | ETAPA 04 — Experiencia del Usuario |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las 41: **14 de 41** |
| **Estado** | **Aprobada** ✔ el 2026-09-05 por jeffersondavila (definición el 2026-09-04, implementación el 2026-09-05) |
| **Repositorios** | `personal-blog-frontend` (funcional) · `personal-blog-infra` (gobierno documental). `personal-blog-backend` **sin rama y sin cambios** |
| **Rama** | `Task/014-Sitio-Publico`, nacida de `main` con `HEAD == main` verificado: `af242845…` (frontend) · `fec55bb8…` (infra) |
| **Dependencia** | `Task/013-Sistema-de-Diseno` — **Aprobada** ✔ |
| **Ficha** | [TASK-014](../tasks/TASK-014-public-site.md) |
| **Reporte** | [TASK-014-report.md](../task-reports/TASK-014-report.md) |

### Qué construye

Las doce rutas del sitio público —Inicio, Quién soy, Artículos y su detalle, Reviews y su
detalle, Videos, Proyectos y su detalle, Contacto, búsqueda y 404— sobre las cinco primitivas
de `Task/013` y los **diez** recursos públicos de `Task/009`/`Task/010`, con estados de carga,
vacío y error, paginación y filtro por etiqueta en la URL, imágenes por `access_url` con
`alt_text`, Markdown **sanitizado** (ADR-005) y enlaces externos seguros (S-12). Asume
**A-02** y **A-04**, continúa **A-01** y **cierra la lista de proveedores de video**
(api-contracts §14.9, data-model deuda 6). **No** hace SEO (`Task/016`), formularios ni
panel (`Task/015`).

### Qué se validó (2026-09-05)

| Aspecto | Resultado |
| --- | --- |
| Pruebas | **440 / 440** en 61 archivos (161 heredadas + 279 nuevas), RED → GREEN por *slice* |
| Cobertura | 99,78 % sentencias · 96,61 % ramas · 100 % funciones |
| Compuertas | `format:check`, `lint`, `typecheck` y `build` sin errores ni *warnings* |
| Dependencias | **Solo** `react-markdown@10.1.0` y `rehype-sanitize@6.0.0`, autorizadas por el usuario (D-014-F) |
| Favicon | SVG neutro provisional derivado de los tokens, autorizado por el usuario (D-014-E) |
| Visual | 14 superficies × 4 anchos (320, 390, 768, 1280) sin desbordamiento; 0 excepciones ni `console.error`; Tab recorre salto, navegación y buscador con el anillo de foco |
| Archivos protegidos | `src/services/http`, `vite.config.ts`, `tsconfig*.json`, `eslint.config.js`: **sin cambios** |
| Entorno local | Solo operaciones aditivas: `alembic upgrade head` en el backend (la base estaba en `0001` y el API respondía `500`) y reconstrucción de la imagen del frontend |

**Limitación declarada:** sin administrador ni perfil en la base local no se pudo publicar
contenido de prueba; en el navegador real se validaron los estados vacíos y los `404`, y los
estados con datos los cubre la suite. La semilla es de `Task/022`.

### Decisiones cerradas

Las decisiones de la ficha (**D-014-A** a **D-014-N**) quedaron **Vigentes** el 2026-09-05
con la aprobación del usuario. La más visible fuera del frontend: la **lista cerrada de
proveedores de video** —`youtube` y `vimeo`, *fail-closed*—, que `CONTENT_MODEL` §3.4
asignaba por nombre a esta tarea y que queda registrada en `api-contracts.md` §14.9,
`data-model.md` y `security-boundaries.md` §5 y §7.

**Ninguna decisión diferida (`D-xx`) cambia:** `Task/014` no era propietaria de ninguna.
**D-04** (editor Markdown) sigue abierta y es de `Task/015`; **D-08** sigue abierta y es de
`Task/030`.

### Deuda registrada

| # | Deuda | Tarea propietaria |
| --- | --- | --- |
| 1 | Restringir `provider` a la lista cerrada en el backend y ofrecer el selector en el panel. | Backend: sin propietario (candidata `Task/018`) · panel: `Task/015` |
| 2 | `noindex`, código HTTP `404` real de la SPA, `description`, Open Graph y canonical. | `Task/016`, `Task/034` |
| 3 | Auditoría de la configuración de sanitización del Markdown. | `Task/018` |
| 4 | `useAppConfig` queda sin consumidor productivo al retirar la pantalla provisional. | `Task/015` |
| 5 | Validación visual **con contenido publicado** en el navegador real: no hay semilla ni administrador local. | `Task/022` |

### Hallazgos independientes registrados, fuera del alcance

Tres *drifts* documentales **preexistentes en `main`**, ajenos a `Task/014`, que **no se
corrigen aquí** y quedan a la espera de que el usuario decida si ameritan un mantenimiento
propio:

1. El índice [`docs/task-reports/README.md`](../task-reports/README.md) **omite** las filas de
   `Task/010`, `Task/011`, `Task/012` y `Task/013`. Arrastrado desde los cierres de esas
   tareas; **excluido expresamente de `Task/013.1` por decisión del usuario**.
2. La tabla **«Resumen de etapas»** de [`ROADMAP.md`](ROADMAP.md) se detuvo en la aprobación
   de `Task/009`: declara ETAPA 03 «**2** de 5 — 40 % — En curso», ETAPA 04 «0 — Pendiente»
   y total «**9** de 41 — 22 %», mientras la cabecera del mismo documento, sus secciones por
   etapa, `STAGE-03`, `STAGE-04` y esta página registran **13 de 41 (32 %)**, ETAPA 03
   **completada** y ETAPA 04 **en curso (1 de 3)**. Los valores correctos son los de la
   cabecera y de `STATUS.md`. Detectado el 2026-09-04 al iniciar `Task/014`.
3. El [runbook local](../runbooks/local-environment.md) §6 declara como valor esperado de
   `alembic current` el `0001 (head)` de `Task/007`; la cabeza real es `0003` desde
   `Task/011`. Detectado el 2026-09-05 al diagnosticar el `500` del API local, cuya base
   seguía en `0001`.

---

## Último mantenimiento aprobado — `Task/004.1`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/004.1-Corregir-Backup-Rutas-Literales` |
| **Tipo** | Mantenimiento correctivo de `Task/004` |
| **Estado** | **Aprobada** ✔ el 2026-09-06 por jeffersondavila |
| **Cuenta en las 41 tareas** | **No.** Avance global y ETAPA 05 **sin cambios** |
| **Repositorios** | `personal-blog-infra` únicamente |
| **Rama** | `Task/004.1-Corregir-Backup-Rutas-Literales`, nacida de `main` |
| **Ficha** | [TASK-004.1](../tasks/TASK-004.1-fix-backup-literal-paths.md) |
| **Reporte** | [TASK-004.1-report.md](../task-reports/TASK-004.1-report.md) |

### Qué corrige

Un respaldo real abortó con `No se encuentra la propiedad 'Hash' en este objeto`. La causa
no era MinIO: los scripts pasaban rutas del sistema de archivos **ya resueltas** a
parámetros de PowerShell que interpretan comodines. Como `[...]` es una clase de
caracteres, una clave de objeto con corchetes dejaba de casar consigo misma, el cmdlet
devolvía `$null` y `Set-StrictMode` abortaba. Sin StrictMode el fallo habría sido
**silencioso**.

El defecto existía desde `Task/004` y se volvió alcanzable el 2026-08-31, cuando los tests
de integración dejaron en MinIO objetos con `[minio]` y `[s3]` en la clave. El último
respaldo correcto, del 2026-07-31, es anterior a esos objetos: por eso `Task/004` se validó
sin detectarlo.

La corrección consume como literal toda ruta ya resuelta (43 conversiones en cuatro
scripts), unifica en `Get-FileHashMap` el bucle que estaba **duplicado** en respaldo y
restauración, y añade `Assert-NoWildcardInPath` como guarda *fail-closed*, porque
`Compress-Archive` de Windows PowerShell 5.1 falla con `[` en su ruta **incluso con**
`-LiteralPath` y eso no se puede corregir desde el script.

**La restauración también estaba rota.** Contenía el defecto idéntico. La prueba de
restauración aislada se ejecutó por primera vez contra un conjunto con claves entre
corchetes y quedó verificada: 17 tablas, 64 objetos con SHA-256 coincidente y Portainer con
`InstanceID` correcto.

### Hallazgos abiertos que deja registrados

| # | Hallazgo | Estado |
| --- | --- | --- |
| 1 | Los tests de integración del backend dejan buckets `personal-blog-test-*` persistentes en el MinIO local. Hay dos, del 2026-08-31 y del 2026-09-02, con 64 objetos. **No se borran**: son el escenario real de regresión de esta corrección | **Abierto** — investigar por qué el *teardown* no los elimina |
| 2 | La restauración recrea los buckets a partir de sus objetos, así que **un bucket vacío no se restaura**. Detectado con `personal-blog-media`. Hueco **preexistente** de `Task/004`, sin relación con el defecto de rutas | **Abierto** — decidir aparte |

---

## Mantenimiento documental anterior — `Task/013.1`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/013.1-Corregir-Drift-Documental-Post-Merge` |
| **Tipo** | Mantenimiento de gobierno documental |
| **Estado** | **Aprobada** ✔ el 2026-09-04 por jeffersondavila |
| **Cuenta en las 41 tareas** | **No.** Avance global y ETAPA 04 **sin cambios** |
| **Repositorios** | `personal-blog-infra` únicamente |
| **Rama** | `Task/013.1-Corregir-Drift-Documental-Post-Merge`, nacida de `main` |
| **Ficha** | [TASK-013.1](../tasks/TASK-013.1-correct-post-merge-documentation-drift.md) |
| **Reporte** | [TASK-013.1-report.md](../task-reports/TASK-013.1-report.md) |

### Qué corrige

El barrido del criterio 12 posterior a la fusión de `Task/013` encontró **una** afirmación
de categoría C: la sección 24 de su reporte conservaba contadores de Git y GitHub
redactados en presente —«los cambios están sin commit, como corresponde a una tarea no
aprobada»— mientras la cabecera del mismo documento declara la tarea **Aprobada**.

La corrección **no borra ni actualiza** la instantánea: la marca como observación fechada
del 2026-09-03 y la redacta en pasado, conservando sus valores originales. Es la forma que
los reportes de `Task/008` y `Task/009` ya usaban y que el de `Task/013` no aplicó.

### Qué NO se corrige, y por qué

- La frase sobre el inicio de `Task/014` (sección 27 del reporte): es la **regla de orden**
  que [WORKFLOW §6.1](WORKFLOW.md) punto 4 avala. Categoría **B**.
- La sección 23 del reporte: el **estado de una tarea es duradero** por la tabla de §6.1,
  no transitorio. No es categoría C.
- El historial fechado de `Task/001`–`Task/012`. **El historial no se reescribe.**

---

## Última tarea aprobada — `Task/013-Sistema-de-Diseno`

**Estado:** **Aprobada** ✔ el 2026-09-04 por jeffersondavila. Cuenta en el avance: **13 de 41**.

Abre la **ETAPA 04**. Entrega la base visual y de componentes que `Task/014` y `Task/015`
consumirán, para que ninguna de las dos invente por su cuenta colores, espaciados,
tipografía, radios, foco, botones, superficies ni semántica de estado.

| Aspecto | Resultado |
| --- | --- |
| Repositorios | `personal-blog-frontend` (funcional) · `personal-blog-infra` (documentación) |
| Tokens | **50** CSS Custom Properties semánticas en `src/styles/tokens.css` |
| Primitivas | `Container`, `Stack`, `Button`, `Card`, `Badge` |
| Estrategia CSS | **CSS Modules + CSS Custom Properties**, **cero dependencias nuevas** |
| Accesibilidad asumida | **A-05**, **A-06**, **A-07**; **A-01** iniciada |
| Pruebas | 161 en verde (50 previas + **111 nuevas**), cobertura 100 % líneas |
| Build | Producción en verde, sin *warnings* |

### Qué asume y qué no

`Task/013` afirma que **la paleta y los pares de contraste que define y verifica** cumplen
WCAG 2.1 AA — 22 pares comprobados por prueba sobre los valores reales de `tokens.css`.
**No** afirma que el producto cumpla AA: esa auditoría es `Task/016`. **A-02**, **A-03**,
**A-04** y **A-08** siguen siendo de `Task/014` y `Task/015`.

### Decisión cerrada

**D-03 — biblioteca de componentes visuales.** **Resuelta** y **Vigente** desde el
2026-09-04: **no se adopta ninguna biblioteca de terceros**. CSS Modules más CSS Custom
Properties, con cero dependencias nuevas.

### Deuda registrada

| # | Deuda | Tarea propietaria |
| --- | --- | --- |
| 1 | Variantes `danger` y silenciosa de `Button`, y tamaños alternativos: sin consumidor todavía. | `Task/015` |
| 2 | Primitivas de formulario (`Input`, `FormField`, `ValidationMessage`) con **A-03** y **A-08**. | `Task/015` |
| 3 | `VisuallyHidden` e `IconButton`: se crearán con su primer consumidor real. | `Task/014`, `Task/015` |
| 4 | Icono real del sitio (favicon): es identidad visual del sitio público. | `Task/014` |
| 5 | La validación visual **integral** requiere páginas reales. | `Task/014`, `Task/015` |

---

## Tarea aprobada anterior — `Task/012-API-Administrativa`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/012-API-Administrativa` |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las 41 |
| **Estado** | **Aprobada** ✔ el 2026-09-03 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/012-API-Administrativa` |
| **Fecha de inicio** | 2026-09-01 |
| **Depende de** | `Task/009`, `Task/010` y `Task/011` — **las tres Aprobadas** |
| **Repositorios modificados** | `personal-blog-backend` · `personal-blog-infra` (gobierno, arquitectura y contratos) |
| **Repositorio no modificado** | `personal-blog-frontend` — **sin rama y sin cambios** |
| **Ramas base** | **`main`** en ambos: `561128b5…` (backend) y `eceb5b35…` (infra). `HEAD == main` verificado inmediatamente tras crearlas |
| **Alcance entregado** | Las **23 rutas administrativas** del contrato: perfil singleton, CRUD y ciclo de vida de artículos, reviews, vídeos y proyectos, gestión de etiquetas y biblioteca de medios. Validación de publicación por tipo, generación y estabilidad del *slug*, asociaciones M:N transaccionales, transiciones seguras ante concurrencia, **exigencia del texto alternativo donde se usa la imagen** (requisito A-04) y auditoría de **once** acciones nuevas |
| **Decisiones que cierra** | **D-012-A** a **D-012-AA** en la ficha, y con ellas cinco materias que las fuentes canónicas asignaban por nombre: forma de las transiciones (`api-contracts.md` §4), campos mínimos para publicar (invariante 18), formato y generación del *slug* (invariante 8, deuda 7), **exigencia del texto alternativo donde se usa la imagen** (`data-model.md` §4.1) y catálogo de auditoría del CRUD (`CONTENT_MODEL.md` §3.9) |
| **Decisiones que NO cierra** | Proveedores de vídeo permitidos (`Task/014`); modificar el `alt_text` de una imagen ya cargada (`Task/014`/`Task/018`); CORS efectivo y cabeceras (`Task/018`); privilegio mínimo sobre `audit_events` (`Task/018`); correlation ID de extremo a extremo (`Task/017`); **D-08** (`Task/030`) |
| **Test-first** | **12 *slices* totales: `SLICE 0` contract-first —sin código productivo, y por tanto sin RED— más **11** *slices* de implementación y validación, cada uno con su RED registrado y su motivo textual.** Las pruebas que pasaron al escribirse se declaran **regresión, no evidencia RED**, y se enumeran una a una en el reporte §S. **No se usó mutation testing** en ninguna forma |
| **PostgreSQL real** | `personal_blog_test`, con la guarda *fail-closed* activa. **SQLite no se usó.** `personal_blog` **no se tocó**: no se creó ningún administrador ni perfil en ella |
| **Esquema físico** | **No se modifica.** No hay migración nueva; `0003` sigue siendo `head` y `0001`–`0003` quedan intactas |
| **Dependencias** | **Una nueva**: `python-multipart==0.0.32`, que FastAPI exige para leer un archivo subido. Python puro, ~164 KB, sin dependencias transitivas |
| **Docker** | Imagen del backend **reconstruida y contenedor recreado** durante la integración, justificado: sin la dependencia nueva FastAPI falla al definir la ruta de carga y el contenedor no arrancaría. En el endurecimiento de concurrencia se usó además `docker exec` **de solo lectura** para consultar `SHOW default_transaction_isolation` y `pg_constraint`. **No** se ejecutó `down`, `down -v`, `restart` ni ningún `prune`; PostgreSQL y MinIO no se tocaron |
| **AWS** | **Ninguno.** Sin cuenta, sin credenciales, sin recursos |
| **Fuera del alcance** | Panel React y dashboard (`Task/015`), render de Markdown (`Task/014`, `Task/015`), semilla local (`Task/022`), perfil y administrador de producción (`Task/036`) |
| **Suite completa** | **1527 pasan, 1 omitida** (`time.tzset` en Windows, preexistente), **0 advertencias** con `-W error`. Cobertura de `app/`: **100 %** |
| **Efecto en el avance** | Avance global **12 de 41 (29 %)**; ETAPA 03 en **5 de 5 (100 %)** — **etapa completada** |
| **Ficha** | [TASK-012](../tasks/TASK-012-administrative-api.md) |
| **Reporte** | [TASK-012-report](../task-reports/TASK-012-report.md) |

### Defectos encontrados durante la integración

| # | Defecto | Cómo se detectó |
| --- | --- | --- |
| 1 | Reemplazar los enlaces sociales del perfil violaba `uq_profile_social_links_profile_id_display_order`: la unidad de trabajo emite los `INSERT` antes que los `DELETE` de los huérfanos | Prueba de integración contra PostgreSQL real. Ningún doble lo habría mostrado |
| 2 | La primera versión de la prueba de orden de la biblioteca de medios era **inestable**: `created_at` es la hora de inicio de la transacción, así que dos cargas de la misma prueba la comparten y decidía el desempate. Fallaba 4 de cada 6 ejecuciones | Se ejecutó seis veces seguidas antes de darla por buena |
| 3 | **Borrar un medio podía dejar la fila apuntando a objetos inexistentes.** `EliminarMedio` borra la fila con `flush` y después los objetos; si la auditoría fallaba justo después, la transacción devolvía la fila y los objetos ya no volvían — la *«imagen rota en el blog publicado»* que **D-010-P** eligió su orden para evitar. Corregido auditando **antes** de borrar (**D-012-X**), en la frontera de composición y sin tocar `Task/010` | Inyección de fallo en la auditoría, contra PostgreSQL y MinIO reales (revisión correctiva) |
| 4 | **`alt_text` no se exigía en ninguna parte**, y la deuda se había trasladado a `Task/014`/`Task/018` sin base: las fuentes anteriores a `Task/012` le asignan a **ella** *exigirlo donde se usa*, y `Task/018` nunca fue propietaria. Corregido: se exige al publicar y, en el perfil, al editar | Relectura de las fuentes **desde `main`**, no del árbol de trabajo (revisión correctiva) |
| 5 | **Exigir el texto no era escribirlo.** Las fuentes dicen que `alt_text` *«se escribe al usar la imagen, no al cargarla»*, y no existía ningún momento posterior a la carga en el que pudiera escribirse: en la práctica obligaba a anticiparlo al subir, justo lo contrario. Corregido: el **primer uso** lo escribe (D-012-Y), sin ampliar `/admin/media` | Segunda revisión externa |
| 6 | **La escritura en el primer uso tenía una carrera.** Es una lectura-decisión-escritura, y se demostró con dos transacciones reales que **ambas** terminaban en éxito con textos distintos: *last-write-wins*, y con ello **D-012-Z era falsa bajo concurrencia**. Corregido: la decisión se serializa sobre la fila `MediaAsset` con `SELECT … FOR UPDATE` (**D-012-AA**), en los cinco consumidores y sin bloquear ninguna lectura pública | Tercera revisión externa |

### Deuda registrada

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | Sin semilla, `GET`/`PUT /admin/profile` responden `404`: el perfil **no se crea por API** (D-012-U) | `Task/022` (local) · `Task/036` (producción) |
| 2 | **Corregir a propósito** un `alt_text` ya escrito y compartido. Fijarlo por primera vez **ya funciona** (D-012-Y), y **D-012-Z** —rechazar un texto distinto— está **aceptada para el MVP**: la revisión externa la aceptó. Relajarla sería una mejora deliberada, no una contradicción | **mejora futura**, sin propietario ni plazo |
| 3 | La edición concurrente no tiene cerrojo optimista (*last-write-wins*) | revisión futura |

---

## Tarea aprobada previa — `Task/011-Autenticacion-Administrativa`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/011-Autenticacion-Administrativa` |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las 41 |
| **Estado** | **Aprobada** ✔ el 2026-09-01 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/011-Autenticacion-Administrativa` |
| **Fecha de inicio** | 2026-08-30 |
| **Depende de** | `Task/008-Modelo-de-Datos` (**Aprobada**) |
| **Repositorios modificados** | `personal-blog-backend` · `personal-blog-infra` (gobierno, arquitectura y documentación) |
| **Repositorio no modificado** | `personal-blog-frontend` — **sin rama y sin cambios** |
| **Ramas base** | **`main`** en ambos: `c1bc0c8b…` (backend) y `90469ecf…` (infra). `HEAD == main` verificado inmediatamente tras crearlas |
| **Alcance entregado** | Los **tres** endpoints de autenticación del contrato; **Argon2id**; sesión opaca con credencial CSPRNG de 256 bits y huella SHA-256; bloqueo de cuenta seguro ante concurrencia; límite de tasa compartido en PostgreSQL; auditoría de cuatro acciones sin secretos; cookie `HttpOnly` con política completa; defensa CSRF en dos capas; y la protección reutilizable `AdministradorRequerido` para `Task/012` |
| **Decisiones que cierra** | **D-15** (topología lógica: mismo *site*, API en subdominio), **D-02** (sesión opaca *server-side* con cookie `HttpOnly`) y **D-09** (contador de ventana fija en PostgreSQL, por IP), más **D-011-A** a **D-011-R** en la ficha. Todas **Vigentes** desde el 2026-09-01 |
| **Decisiones que NO cierra** | **D-07** (dominio real y DNS) sigue en `Task/035`; **D-08**, en `Task/030`; el CORS efectivo y las cabeceras de seguridad, en `Task/018`; el *throttling* del borde, en `Task/033` |
| **Test-first** | **Demostrado, con su clasificación exacta.** Doce *slices*, cada uno con su RED registrado antes de existir la implementación y su motivo textual. **Quince pruebas pasaron al escribirse y se declaran regresión, no evidencia RED**, enumeradas una a una en el reporte §S. **No se usó mutation testing** en ninguna forma |
| **PostgreSQL real** | `personal_blog_test`, con la guarda *fail-closed* activa. **SQLite no se usó.** `personal_blog` **no se tocó** |
| **Esquema físico** | **Modificado**: migración **`0003`** con `administrator_sessions` y `login_rate_limits`. `upgrade` → `downgrade` → `upgrade` y `compare_metadata` verificados. `0001` y `0002` **intactas** |
| **Docker** | **No se recreó nada.** Ni `down`, ni `up --build`, ni `prune`. La imagen del backend **no se reconstruyó**: se verificó en su lugar que existe rueda `manylinux` de `argon2-cffi` para el destino Linux/Lambda |
| **AWS** | **Ninguno.** Sin cuenta, sin credenciales, sin recursos |
| **Fuera del alcance** | CRUD administrativo (`Task/012`), panel React (`Task/015`), CORS efectivo y cabeceras (`Task/018`), dominio real (`Task/035`), administrador de producción (`Task/036`), semilla local (`Task/022`), SSM (`Task/032`) |
| **Suite completa** | **1046 pasan, 1 omitida** (`time.tzset` en Windows, preexistente), **0 advertencias** con `-W error`. Cobertura de `app/`: **100 %** |
| **Efecto en el avance** | Avance global **11 de 41 (27 %)**; ETAPA 03 en **4 de 5 (80 %)** |
| **Ficha** | [TASK-011](../tasks/TASK-011-administrative-authentication.md) |
| **Reporte** | [TASK-011-report](../task-reports/TASK-011-report.md) |

### Por qué la decisión de D-02 no fue «lo más simple»

El contrato vigente —USER_FLOWS.md B.12— exige que cerrar sesión **invalide en el
servidor**. Un JWT no puede hacerlo por construcción: es una afirmación autocontenida y
válida hasta su expiración. Cumplirlo con JWT obliga a consultar una lista de revocación
en cada petición, y en ese momento el JWT **ha perdido su única ventaja** —no consultar
estado compartido— y **conserva todos sus costes**: un secreto de firma que custodiar y
rotar, y *claims* que este proyecto no necesita porque hay **un solo administrador sin
roles**.

### Defectos encontrados durante la integración

| # | Defecto | Resolución |
| --- | --- | --- |
| 1 | **Contaminación entre pruebas.** La primera suite completa dio **48 fallos que no aparecían al ejecutar los módulos por separado**: la limpieza borraba el administrador **antes** que sus eventos de auditoría, la clave foránea `ON DELETE RESTRICT` de `Task/008` lo rechazaba dentro de un `finally`, y la fila superviviente bloqueaba —por el `UNIQUE` del *singleton*— a todas las pruebas posteriores | Helper `limpiar_autenticacion`, que borra en orden de dependencias. **Es un defecto del andamiaje, no del código productivo**, y lo que demuestra es que el `RESTRICT` funciona |
| 2 | **Un nombre de cookie configurable habría hecho mentir a OpenAPI**: FastAPI construye el esquema de seguridad al definir las rutas, así que un despliegue que cambiara la variable publicaría una especificación que declara una cookie distinta de la que el servidor usa | El nombre pasó a **constante** y la variable se retiró |
| 3 | **Una prueba de partición del límite de tasa mezclaba los dos alcances** de protección y no medía lo que decía medir | El atacante usa un correo inexistente, aislando la partición del bloqueo de cuenta |
| 4 | **Dos aserciones afirmaban cosas que el almacenamiento no garantiza**: el orden de dos eventos de la misma transacción y una IP que en realidad no es una IP | Sustituidas por comprobaciones de lo que sí está garantizado |

### Deuda registrada

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | **Las tablas de estado de autenticación no se purgan** (**R-44**). `login_rate_limits` crece por **dirección IP observada** y es la fuente de crecimiento potencialmente mayor; `administrator_sessions` crece por **inicio de sesión con éxito**, y las filas caducadas o revocadas permanecen. No hay procesos residentes que las limpien; el volumen es despreciable con un único administrador, pero el crecimiento es monótono | `Task/018` o `Task/029` |
| 2 | **La imagen Docker no se reconstruyó** tras añadir `argon2-cffi`, que es una dependencia binaria. La rueda `manylinux_2_17_x86_64` **existe y se verificó descargándola**; falta la construcción real | Comprobación del usuario · `Task/024`/`Task/032` |
| 3 | **El inicio de sesión desde navegador en local exige DOS variables, todavía no cableadas en el Compose local.** (A) **`BLOG_ADMIN_ALLOWED_ORIGINS`** con el origen real del panel: es *fail-closed*, y sin él la validación de `Origin` rechaza los `POST` del navegador. (B) **`BLOG_AUTH_COOKIE_SECURE=false`**, porque el entorno local actual sirve por **HTTP** y una cookie `Secure` no se conserva ni se reenvía sobre HTTP. **Hacen falta las dos**: con una sola, el inicio de sesión desde navegador sigue sin funcionar. No se añaden aquí porque el consumidor real del contrato todavía no existe | `Task/015` |
| 4 | **La resistencia al análisis temporal no está medida.** Se garantiza que no queda ningún camino que evite el trabajo criptográfico; nada más se afirma | `Task/018`, si algún día se mide |
| 5 | **Los saltos de proxy de confianza no están fijados** para Traefik ni para API Gateway. El mecanismo existe, con el valor seguro por defecto (`0`, que ignora `X-Forwarded-For`) | Runbook local · `Task/033` |

---

## Tarea aprobada de la ETAPA 03 — `Task/010-Almacenamiento-Compatible-S3`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/010-Almacenamiento-Compatible-S3` |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las 41 |
| **Estado** | **Aprobada** ✔ el 2026-08-28 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/010-Almacenamiento-Compatible-S3` |
| **Fecha de inicio** | 2026-08-28 |
| **Depende de** | `Task/008-Modelo-de-Datos` (**Aprobada**) |
| **Repositorios modificados** | `personal-blog-backend` · `personal-blog-infra` (gobierno, documentación y `docker-compose.yml`) |
| **Repositorio no modificado** | `personal-blog-frontend` — **sin rama y sin cambios** |
| **Ramas base** | **`main`** en ambos: `81347758…` (backend) y `64e237cd…` (infra). `HEAD == main` verificado inmediatamente tras crearlas |
| **Alcance entregado** | Interfaz `ObjectStorage` con cinco operaciones; `MinIOStorage` y `S3Storage` **ambas con código real**; suite de contrato **común** de 13 casos ejecutada contra las dos; configuración y selector por entorno; claves de objeto no predecibles; validación de imagen por **decodificación**; miniaturas WebP derivadas; caso de uso de subida con **compensación**; caso de uso de borrado con comprobación de uso; campo público `access_url` |
| **Test-first** | **Demostrado, con su clasificación exacta.** Diez *slices*, cada uno con RED registrado antes de existir la implementación; el defecto corregido tras la revisión llevó su propio ciclo RED → GREEN → REFACTOR. En los *slices* 2/3, **siete** guardas produjeron RED propio y **cinco** guardas de ausencia se añadieron después y pasaron al escribirse: esas cinco se declaran **regresión, no evidencia RED**. **Seis comprobaciones de mutación** son evidencia **complementaria** de sensibilidad; **nunca** sustituto del RED |
| **PostgreSQL real** | `personal_blog_test`, con la guarda *fail-closed* de `Task/005.6`/`005.7` activa. **SQLite no se usó** |
| **MinIO real** | Entorno local de `Task/007`, con una guarda *fail-closed* **nueva**: solo anfitriones locales, bucket creado por la suite con prefijo `personal-blog-test-`, y borrado que vuelve a comprobar el prefijo |
| **Docker verificado** | El backend se **reconstruyó y recreó** con la configuración nueva (`up -d --build backend`, sin `down -v`) y quedó `healthy`. Un *smoke* desde el contenedor emite un enlace que el **host descarga con `200`** y bytes idénticos |
| **AWS** | **Ninguno.** Sin cuenta, sin credenciales, sin recursos. `S3Storage` se ejerce contra el endpoint S3-compatible local |
| **Esquema físico** | **No se modifica.** Sin migración nueva; `0002` sigue siendo `head` |
| **Decisiones que cierra** | **D-010-A** a **D-010-R** (ficha §12), todas **Vigentes** desde el 2026-08-28. Cierra **D-009-O** en la parte que le corresponde y precisa la **invariante 9** de CONTENT_MODEL.md |
| **Decisiones que NO cierra** | **D-08** (política cloud, caché, TTL productivo y CDN) sigue en `Task/030`; el *wiring* en Lambda, en `Task/032`; los endpoints administrativos de medios, en `Task/012`; el endurecimiento de la subida, en `Task/018` |
| **Fuera del alcance** | Recursos AWS, Terraform, SSM, Lambda, frontend, autenticación, API administrativa |
| **Suite completa** | **792 pasan, 1 omitida** (`time.tzset` en Windows, preexistente), **0 advertencias** con `-W error`. Cobertura de `app/`: **100 %** |
| **Efecto en el avance** | Avance global **10 de 41 (24 %)**; ETAPA 03 en **3 de 5 (60 %)** |
| **Ficha** | [TASK-010](../tasks/TASK-010-s3-compatible-storage.md) |
| **Reporte** | [TASK-010-report](../task-reports/TASK-010-report.md) |

### Hallazgo resuelto dentro de la tarea

| # | Hallazgo | Resolución |
| --- | --- | --- |
| 2 | **El `access_url` local no era consumible.** Se firmaba contra `http://minio:9000` —correcto para el backend, inalcanzable para el navegador del host— y el anfitrión forma parte de la firma SigV4, así que reescribirlo produce `403`. Detectado por la **revisión externa** antes de aprobar | Se separaron el endpoint **operativo** y el **de acceso** (decisión **D-010-R**), con ciclo RED → GREEN → REFACTOR completo. El enlace se firma contra el externo **desde el principio**, sin reescrituras. Verificado con un `GET` real desde el host: `200` y bytes idénticos, más un control negativo que devuelve `403` al reescribir el anfitrión |
| 1 | **Una URL prefirmada contiene `object_key` en su ruta.** La prueba de `Task/009` `test_la_portada_no_expone_la_clave_del_objeto` afirmaba que la clave no aparecía en el cuerpo, y esa afirmación deja de poder sostenerse en cuanto existe el campo de acceso que **la propia `Task/009` encargó a `Task/010`** | Se detuvo el trabajo y se contrastó con las fuentes canónicas antes de tocar ninguna expectativa. `CONTENT_MODEL.md` §3.7 y `security-boundaries.md` **imponen** la URL prefirmada, y no existe variante del mecanismo que omita la clave. La invariante 9 prohíbe exponerla *«sin control»*, y una URL firmada y con caducidad **es** la exposición controlada. Se precisó la invariante (decisión **D-010-Q**), se reescribió la prueba para afirmar la garantía real —ningún **campo** del contrato la transporta, y fuera del enlace firmado no aparece— y se documentó en `api-contracts.md` §12 |

### Deuda registrada

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | La limpieza del bucket de pruebas vive en un `finally` y **no sobrevive a un `SIGKILL`**: un corte por tiempo de espera deja el bucket. Observado durante la propia tarea. No corrompe nada y el prefijo `personal-blog-test-` lo hace inequívocamente descartable; purgarlo es una línea, documentada en el harness | Aceptado y documentado |
| ~~2~~ | ~~La URL prefirmada local no es alcanzable desde el host~~ — **CERRADA dentro de `Task/010`**: era un defecto, no deuda. No se traslada a `Task/015` ni a `Task/016` | — |
| 3 | La miniatura se almacena pero **no se expone** en la API pública: `Task/009` dejó pendiente **un** campo de acceso y añadir más sería ampliar el contrato por encima de lo que ninguna fuente vigente pide. Su clave se deriva de `object_key`, así que exponerla después es compatible | `Task/016` (rendimiento de listados) |

---

## Tarea aprobada anterior de la ETAPA 03 — `Task/009-API-Publica`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/009-API-Publica` |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las 41 |
| **Estado** | **Aprobada** el 2026-08-27 |
| **Fecha de inicio** | 2026-08-26 |
| **Expresión de aprobación** | `approved: Task/009-API-Publica` |
| **Depende de** | `Task/008-Modelo-de-Datos` (**Aprobada**) |
| **Repositorios modificados** | `personal-blog-backend` · `personal-blog-infra` (gobierno y documentación) |
| **Repositorio no modificado** | `personal-blog-frontend` — **sin rama y sin cambios** |
| **Ramas base** | **`main`** en ambos: `0ada6a73…` (backend) y `71f56da2…` (infra). `HEAD == main` verificado inmediatamente tras crearlas |
| **Alcance entregado** | Los **diez** endpoints públicos del contrato: perfil, artículos, reviews, videos, proyectos, etiquetas y búsqueda. Paginación compartida, filtros `tag`/`featured`/`sort` con lista cerrada, orden determinista y búsqueda básica sobre contenido publicado |
| **Test-first** | **Cumplido para la implementación aprobada.** En la primera ejecución seis *slices* tuvieron sus pruebas escritas **después** del código; la desviación se detectó **pre-approval**, la tarea **no** se aprobó, y esos seis *slices* se **reconstruyeron test-first** —RED real sobre código inexistente— en un laboratorio limpio nacido del mismo SHA base, antes de cualquier *commit*. Lo aprobado es la implementación reconstruida. Detalle en el reporte §I.2, §I.5 y §I.6 |
| **PostgreSQL real** | `personal_blog_test`, con la guarda *fail-closed* de `Task/005.6`/`005.7` activa. **SQLite no se usó** |
| **Esquema físico** | **No se modifica.** Sin migración nueva; `0002` sigue siendo `head` |
| **Decisiones que cierra** | **D-009-A** a **D-009-R**, todas **Vigentes** desde el 2026-08-27: `page_size` (12 / 50), política de parámetros desconocidos (**se rechazan**), lista cerrada de `sort` y su dirección, desempate por `slug`, semántica de `featured`, `tag` inexistente, visibilidad de `/tags`, forma y campos de `/search`, mecanismo de búsqueda e índices, respuesta de `/profile` sin perfil, y representación pública de una referencia a `MediaAsset` |
| **Decisiones que NO cierra** | Acceso a medios (`Task/010`); autenticación y D-15 (`Task/011`); CRUD y transiciones (`Task/012`); render de Markdown (`Task/014`, `Task/015`); correlation ID de extremo a extremo (`Task/017`) |
| **Fuera del alcance** | API administrativa, autenticación, `ObjectStorage`, frontend, cloud |
| **Suite completa** | **597 pasan, 1 omitida** (`time.tzset` en Windows, preexistente), **0 advertencias** con `-W error`. Cobertura de `app/`: **100 %** |
| **Efecto en el avance** | Avance global **9 de 41 (22 %)**; ETAPA 03 en **2 de 5 (40 %)** |
| **Ficha** | [TASK-009](../tasks/TASK-009-public-api.md) |
| **Reporte** | [TASK-009-report](../task-reports/TASK-009-report.md) |

---

## Primera tarea aprobada de la ETAPA 03 — `Task/008-Modelo-de-Datos`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/008-Modelo-de-Datos` |
| **Etapa** | ETAPA 03 — Dominio y Backend |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las 41 |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-25 |
| **Fecha de aprobación** | 2026-08-25 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/008-Modelo-de-Datos` |
| **Depende de** | `Task/007-Integracion-Local` (**Aprobada**) |
| **Repositorios modificados** | `personal-blog-backend` · `personal-blog-infra` (gobierno y documentación) |
| **Repositorio no modificado** | `personal-blog-frontend` — **sin rama y sin cambios**: la tarea no le afecta |
| **Ramas base** | **`main`** en ambos: `2290a9fb…` (backend) y `b23ad66d…` (infra). `HEAD == main` verificado inmediatamente tras crearlas |
| **Alcance entregado** | Modelo físico completo del MVP: **14 tablas** para los nueve tipos conceptuales; entidades de dominio del ciclo de vida de publicación; escala de valoración; restricciones e índices reales; migración Alembic `0002` reversible |
| **Test-first** | **Demostrado.** Matriz de casos previa en la ficha; RED registrado por *slice*; GREEN; refactor. Suite completa: **250 pasan, 1 omitida** (`time.tzset` no existe en Windows, preexistente), **0 advertencias** con `-W error` |
| **PostgreSQL real** | `personal_blog_test`, con la guarda *fail-closed* de `Task/005.6`/`005.7` activa. **SQLite no se usó** |
| **Decisiones que cierra** | Escala de `rating` (**1..5**), estrategia de clave primaria (**UUID**), semántica final de `published_at`, representación de estados, `social_links`, `technologies`, política de borrado de medios y cascadas de etiquetado. Todas **Vigentes** desde el 2026-08-25 |
| **Decisiones que NO cierra** | Retención de `AuditEvent`; formato y generación del *slug* (`Task/012`); proveedores de vídeo permitidos (`Task/014`); mecanismo de búsqueda y sus índices (`Task/009`) |
| **Fuera del alcance** | API pública (`Task/009`), `ObjectStorage` (`Task/010`), autenticación y auditoría operativa (`Task/011`), CRUD administrativo (`Task/012`), frontend, cloud |
| **Datos sembrados** | **Ninguno.** La migración no contiene `INSERT`: el perfil y el administrador llevan datos personales y una credencial, que no se versionan |
| **Efecto en el avance** | Avance global **8 de 41 (20 %)**; **ETAPA 03 abierta** con 1 de 5 |
| **Ficha** | [TASK-008](../tasks/TASK-008-data-model.md) |
| **Reporte** | [TASK-008-report](../task-reports/TASK-008-report.md) |
| **Modelo físico** | [data-model.md](../architecture/data-model.md) — **Vigente** ✔ |

### Hallazgos corregidos dentro de la tarea

Cuatro defectos reales que la propia práctica test-first sacó a la luz. Ninguno era
funcionalidad nueva; los cuatro dejan su prueba de regresión en la suite.

| # | Hallazgo | Corrección |
| --- | --- | --- |
| 1 | `app/shared/errors/__init__.py` reexportaba los manejadores HTTP, así que **importar una excepción desde el dominio cargaba FastAPI**: la regla de dependencias de ADR-004 se rompía sin que ningún import lo delatara | El paquete exporta solo excepciones; los manejadores se importan de su módulo. Regresión: `tests/unit/test_independencia_del_dominio.py` |
| 2 | `alembic/script.py.mako` no emitía los imports de dialecto de `--autogenerate`: la primera migración con un tipo `JSONB` habría fallado con `NameError` | Se añadió el marcador `${imports}` a la plantilla |
| 3 | `tests/test_database.py` afirmaba `Base.metadata.tables == {}` — "el proyecto no tiene tablas de negocio" —, condenado a caducar exactamente igual que la prueba de migraciones que `Task/005.6` ya tuvo que rehacer | Sustituida por una afirmación que no caduca |
| 4 | El descubrimiento de fixtures del harness usaba `hasattr`, y **`sqlalchemy.func` responde a cualquier atributo**: importarlo en un módulo de integración lo convertía en una "fixture" que no pasaba por la guarda | Se exige además que la marca provenga de pytest. La guarda anti-tautología existente sigue impidiendo que la condición deje fuera fixtures reales |

### Hallazgos de la revisión correctiva pre-approval

Cuatro más, encontrados **después** de la primera declaración `Lista para validación`. La
cronología se deja escrita: es trazabilidad, no un demérito.

| # | Hallazgo | Gravedad | Corrección |
| --- | --- | --- | --- |
| 5 | **El esquema contradecía USER_FLOWS.md B.2.** `book_title`, `book_author`, `provider` y `video_url` eran `NOT NULL`, así que crear un borrador de review o de vídeo obligaba a inventar datos | **Bloqueante** | Las cuatro admiten nulo, con RED → GREEN contra PostgreSQL real y una guarda estructural que recorre las columnas reales |
| 6 | **Estado transitorio persistido como vigente** (WORKFLOW §6.1): `Task/009` aparecía condicionada a que el PR estuviera *"fusionado y normalizado"* | **Bloqueante** | Redacción durable: `Task/009` depende de que `Task/008` esté **Aprobada**; el estado de Git se consulta en vivo |
| 7 | **La garantía de inmutabilidad de `AuditEvent` prometía de más**: el DML masivo del ORM la sortea | Precisión | Garantía reformulada al perímetro real y fijada por prueba en las dos direcciones. El endurecimiento restante es de **`Task/018`** |
| 8 | El *owner* del *bootstrap* de `Profile`/`Administrator` estaba atribuido de forma vaga a *"`Task/012` o posterior"* | Precisión | El ROADMAP ya lo asigna: **`Task/036`** en producción y **`Task/022`** para la semilla local |

---

## Tarea aprobada de la ETAPA 02 — `Task/007-Integracion-Local`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/007-Integracion-Local` |
| **Etapa** | ETAPA 02 — Fundaciones de las Aplicaciones |
| **Tipo** | **Tarea oficial del roadmap.** Cuenta dentro de las 41 |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-23 |
| **Fecha de aprobación** | 2026-08-23 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/007-Integracion-Local` |
| **Repositorios modificados** | `personal-blog-infra` · `personal-blog-frontend` |
| **Repositorio leído y NO modificado** | `personal-blog-backend` — la integración se resuelve **solo con configuración**; su `Dockerfile`, su configuración por entorno y `GET /health` sirven sin cambios |
| **Ramas base** | **`main`** en ambos: `a6412f3…` (infra) y `c4af3617…` (frontend) |
| **Alcance entregado** | Compose completo con **Traefik v3**, **frontend** y **backend** sobre la infraestructura existente; enrutado explícito **sin socket de Docker**; red de borde `blog-edge` separada de `blog-data`; arranque encadenado por *healthchecks*; **consumo real de `GET /health`** desde el frontend con el cliente HTTP oficial; runbook y gobierno actualizados |
| **Sitio y API** | **Mismo origen** (`http://localhost:8081`): el navegador no exige CORS y **no se configura ninguno** |
| **Datos** | **3 volúmenes antes y después, 0 eliminados.** `postgres`, `minio` y `portainer` no se recrearon |
| **Backups de `Task/004`** | **Compatibles.** Nombres de contenedor y de volumen intactos; integridad del conjunto existente verificada |
| **Fuera del alcance** | `ObjectStorage` y uso aplicativo de MinIO (`Task/010`), modelo de datos (`Task/008`), API pública (`Task/009`), autenticación (`Task/011`), diseño (`Task/013`+), CI y cualquier recurso cloud |
| **Riesgos nuevos** | **Ninguno.** **R-09 no se agrava**: Traefik **no** recibe el socket de Docker |
| **Efecto en el avance** | Avance global **7 de 41 (17 %)**; **ETAPA 02 completada** (3 de 3) |
| **Ficha** | [TASK-007](../tasks/TASK-007-local-integration.md) |
| **Reporte** | [TASK-007-report](../task-reports/TASK-007-report.md) |

> **Aprobada** por el usuario el 2026-08-23. Con ella **la ETAPA 02 queda completada** y el
> avance pasa a **7 de 41 (17 %)**.
>
> **Comprobación visual de Portainer: completada.** *Observado el 2026-08-25:* el usuario
> validó en la interfaz autenticada de Portainer que los seis contenedores del entorno son
> visibles y están sanos (`backend`, `frontend`, `traefik`, `postgres` y `minio` en
> `healthy`; `portainer` en `running`).
>
> El reporte de `Task/007` sigue diciendo que estaba pendiente, y **eso no se corrige**:
> era un hecho cierto en el momento en que se escribió. Lo que se actualiza aquí es el
> estado **vivo**, con su fecha de observación ([WORKFLOW §6.1](WORKFLOW.md), regla 2).

`Task/008-Modelo-de-Datos` fue **aprobada el 2026-08-25**: es la primera tarea de la
ETAPA 03 y la primera sujeta a la **BACKEND TEST-FIRST LAW**.

---

## Mantenimiento aprobado anterior — `Task/009.1`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/009.1-Corregir-Drift-Documental-Post-Merge` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-27 |
| **Fecha de aprobación** | 2026-08-27 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/009.1-Corregir-Drift-Documental-Post-Merge` |
| **Repositorios afectados** | `personal-blog-infra` (**únicamente**) |
| **Rama** | `Task/009.1-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`**. SHA base: `e034e75`. Verificado `HEAD == main` inmediatamente después de crearla |
| **Origen** | Auditoría focalizada del cierre post-merge de `Task/009`: **6 afirmaciones** presentaban como estado vigente un trámite de pull request y una normalización ya consumados, y **1 más** conservaba un estado durable obsoleto. Incumplimiento de [WORKFLOW §6.1](WORKFLOW.md), vigente desde `Task/005.6` |
| **Alcance entregado** | Las 6 afirmaciones reescritas en forma **duradera** en `STATUS.md` (3), el reporte de `Task/009` (2) y su ficha (1); además, el estado de `Task/009` corregido a **Aprobada** en la tabla completa de tareas. Barrido posterior sobre los 8 documentos que `Task/009` modificó: **0 apariciones** de estado transitorio presentado como vigente |
| **Prevención** | **Criterio 12** añadido a la [Definition of Done](DEFINITION_OF_DONE.md) §1: el cierre comprueba que la documentación no persista estado transitorio de Git o GitHub. Sigue el patrón del criterio 11 —comprobar el hecho y apuntar a la regla—, sin duplicar [WORKFLOW §6.1](WORKFLOW.md). `TASK_TEMPLATE.md` **no se toca** |
| **Historia preservada** | La desviación TDD de `Task/009`, su remediación, el criterio 29 y las observaciones fechadas **no se reescriben**: son registros históricos válidos |
| **Implementación** | **0 funcionalidad.** 0 código, 0 pruebas, 0 Compose, 0 Terraform, 0 ADR, 0 recursos cloud. `ROADMAP.md` y `STAGE-03` **sin cambios** |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global **9 de 41 (22 %)** y ETAPA 03 **2 de 5 (40 %)** **sin cambios** |
| **Ficha** | [TASK-009.1](../tasks/TASK-009.1-correct-post-merge-documentation-drift.md) |
| **Reporte** | [TASK-009.1-report](../task-reports/TASK-009.1-report.md) |

`Task/010-Almacenamiento-Compatible-S3` sigue **Pendiente y no iniciada**, y **nacerá desde
`main`**, como toda rama Task.

---

## Mantenimiento aprobado previo — `Task/006.2`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| **Tipo** | **Mantenimiento transversal de arquitectura y planificación** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-23 |
| **Fecha de aprobación** | 2026-08-23 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| **Repositorios afectados** | `personal-blog-infra` (**únicamente**) |
| **Rama** | `Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` |
| **Rama base** | **`main`** — única base permitida. SHA base: `d08fe27711866eabe091a2d139387e2022c95b70`. Verificado `HEAD == main` inmediatamente después de crearla |
| **Origen** | El usuario actualizó manualmente `images/Infraestructura.png` en `main` y normalizó `main → dev`. La documentación textual no describía la arquitectura que la imagen ya mostraba |
| **Alcance entregado** | Documento canónico [target-production-architecture.md](../architecture/target-production-architecture.md) (26 secciones) — **Vigente**; [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) — **Aceptada** ✔; alineación de `overview`, `local-to-cloud-mapping`, `security-boundaries` (**C-16**, **C-17**, §10), `production-postgresql-vps` (§11.1.1, §15.3.1), `non-functional-requirements` (**O-09**, **O-10**), `open-decisions` (**D-17**–**D-20**), `ROADMAP`, `STATUS`, `README` y las fichas de las ETAPAS 02, 05, 09, 10 y 12 |
| **Decisiones que cierra** | Secretos del VPS **cifrados** (herramienta abierta), **CloudWatch mínimo**, **Grafana Cloud** como plano central, **Grafana Alloy** en el VPS, **Terraform no configura el sistema operativo**, **Docker no es runtime de producción** |
| **Decisiones que abre** | **D-17** (herramienta de secretos del VPS, `Task/029`) · **D-18** (configuración del SO, `Task/029`) · **D-19** (plan y costo de Grafana Cloud, `Task/041`) · **D-20** (integración CloudWatch → Grafana, `Task/031`) |
| **Riesgos nuevos** | **R-38** a **R-42**, los cinco **abiertos** |
| **Imagen** | `images/Infraestructura.png` **no modificada**. Sigue siendo el commit `d08fe27` del usuario |
| **Implementación** | **0 funcionalidad.** 0 código, 0 pruebas, 0 Compose, 0 Terraform, 0 recursos cloud, 0 cuentas contratadas |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. **41 identificadores intactos, sin renumerar.** Avance global **6 de 41 (15 %)** y ETAPA 02 **2 de 3** **sin cambios** |
| **Ficha** | [TASK-006.2](../tasks/TASK-006.2-formalize-target-production-architecture.md) |
| **Reporte** | [TASK-006.2-report](../task-reports/TASK-006.2-report.md) |

> **Aprobada** por el usuario el 2026-08-23. **ADR-008** queda **Aceptada** y el documento
> canónico **Vigente**. Lo aceptado antes —ADR-001 a ADR-007— sigue vigente y **no se
> reabre**.
>
> **Aprobar no autoriza a implementar.** Contratar Grafana Cloud, provisionar el VPS,
> instalar Alloy o crear cualquier recurso cloud sigue exigiendo su tarea propietaria y la
> autorización explícita del usuario.

> **Reconciliación previa, ajena a esta tarea.** El 2026-08-23, **antes** de crear la rama,
> se verificó que la normalización `main → dev` del hotfix de la imagen —ejecutada
> manualmente por el usuario— estaba completa. Esa reconciliación **no forma parte del
> alcance de `Task/006.2`**.
>
> El estado vivo de ramas y pull request se consulta en Git y GitHub, no aquí
> ([WORKFLOW §6.1](WORKFLOW.md)).

`Task/007-Integracion-Local` sigue **Pendiente y no iniciada**, y **nacerá desde `main`**,
como toda rama Task.

---

## Mantenimiento aprobado tras `Task/006` — `Task/006.1`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/006.1-Corregir-Drift-Documental-Post-Merge` |
| **Tipo** | **Mantenimiento de gobierno documental** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-19 |
| **Fecha de aprobación** | 2026-08-21 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/006.1-Corregir-Drift-Documental-Post-Merge` |
| **Repositorios afectados** | `personal-blog-infra` (**únicamente**) |
| **Rama** | `Task/006.1-Corregir-Drift-Documental-Post-Merge` |
| **Rama base** | **`main`**. SHA base: `f434666`. Verificado `HEAD == main` inmediatamente después de crearla |
| **Origen** | Auditoría focalizada del cierre post-merge de `Task/006`: **6 afirmaciones** presentaban como estado vigente un trámite de pull request ya consumado. Incumplimiento de [WORKFLOW §6.1](WORKFLOW.md), vigente desde `Task/005.6` |
| **Alcance entregado** | Las 6 afirmaciones reescritas en forma **duradera** en `STATUS.md` (4), `STAGE-02` (1) y la ficha `TASK-006` (1). Verificación dirigida posterior: **0 apariciones** de estado transitorio presentado como vigente |
| **Historia preservada** | El reporte de `Task/006` y las secciones de `Task/001`–`Task/005.7` **no se reescriben**: son registros fechados |
| **Implementación** | **0 funcionalidad.** 0 código, 0 pruebas, 0 Compose, 0 Terraform, 0 ADR, 0 recursos cloud. `ROADMAP.md` **sin cambios** |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global **6 de 41 (15 %)** y ETAPA 02 **2 de 3** **sin cambios** |
| **Ficha** | [TASK-006.1](../tasks/TASK-006.1-correct-post-merge-documentation-drift.md) |
| **Reporte** | [TASK-006.1-report](../task-reports/TASK-006.1-report.md) |

`Task/007-Integracion-Local` sigue **Pendiente y no iniciada**, y **nacerá desde `main`**,
como toda rama Task.

---

## Última tarea aprobada — `Task/006-Fundacion-Frontend-React`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/006-Fundacion-Frontend-React` |
| **Etapa** | ETAPA 02 — Fundaciones de las Aplicaciones |
| **Estado** | **Aprobada** ✔ |
| **Repositorios** | `personal-blog-frontend` (implementación) · `personal-blog-infra` (gobierno documental) |
| **Rama base** | `main` en ambos: `21cb51d8…` (frontend) y `ccc19473…` (infra) |
| **Fecha de inicio** | 2026-08-18 |
| **Fecha de aprobación** | 2026-08-18 |
| **Ficha** | [TASK-006](../tasks/TASK-006-react-frontend-foundation.md) |
| **Reporte** | [TASK-006-report](../task-reports/TASK-006-report.md) |
| **Efecto en el avance** | Avance global **6 de 41 (15 %)**; ETAPA 02 **2 de 3** |

Qué entrega: la fundación del frontend —React 19, TypeScript 5.9 estricto, Vite 8, router
con *fallback* 404, configuración de entorno validada al arrancar, cliente HTTP común con
modelo de error, suite de 31 pruebas, lint, formato y build de producción reproducible—.

Validaciones, con **códigos de salida reales**: `lint`, `typecheck`, `format:check`,
`test:coverage` y `build` terminan en **0**, tanto en el repositorio como desde una
instalación limpia con `npm ci`, cuyo `dist/` resulta **byte a byte idéntico**. La consola
del navegador queda **sin errores** en la ruta inicial y en una ruta 404, comprobado con
Chrome *headless*.

Su alcance excluye deliberadamente el sistema de diseño (`Task/013`), las páginas del sitio
público (`Task/014`), el panel administrativo (`Task/015`), la autenticación (`Task/011`) y
el consumo real del API (`Task/007`).

> **Cierre completado.** La aprobación quedó registrada, la tarea se integró en `dev`, el
> usuario fusionó los pull request `Task/006 → main` en ambos repositorios y la
> normalización `main → dev` se ejecutó después. `Task/007` sigue **Pendiente y no
> iniciada**, y **nacerá desde `main`**, como toda rama Task.
>
> El estado vivo de ramas y pull request se consulta en Git y GitHub, no aquí
> ([WORKFLOW §6.1](WORKFLOW.md)).

---

## Tarea aprobada anterior — `Task/005-Fundacion-Backend-FastAPI`

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

## Tarea aprobada previa — `Task/004-Backups-y-Recuperacion-Local`

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

## Mantenimiento anterior aprobado — `Task/005.5`

> *(Título corregido en `Task/005.7`: esta sección y la de `Task/005.6` se llamaban
> ambas «Último mantenimiento aprobado». El contenido histórico no se altera.)*

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.5-Alinear-Planificacion-Tras-Auditoria` |
| **Tipo** | **Mantenimiento de gobierno, planificación y arquitectura documental** |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-16 |
| **Fecha de aprobación** | 2026-08-16 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.5-Alinear-Planificacion-Tras-Auditoria` |
| **Repositorios afectados** | `personal-blog-infra`, `personal-blog-backend`, `personal-blog-frontend` — **solo documentación** |
| **Rama** | `Task/005.5-Alinear-Planificacion-Tras-Auditoria` en los tres repositorios |
| **Rama base** | **`main`** en los tres. SHA base: infra `cc90b96` · backend `db6ab18` · frontend `144a401`. Verificado `HEAD == main` en los tres |
| **Origen** | Dos auditorías independientes del proyecto. **Sus hallazgos no se aceptaron como autoridad automática**: cada uno se reprodujo contra el repositorio antes de decidir |
| **Objetivo** | Eliminar contradicciones entre repositorios, corregir dependencias invertidas, asignar propietarios ausentes y propagar decisiones ya aprobadas |
| **Corrección principal de workflow** | Backend y frontend seguían ordenando crear ramas Task **desde `dev`**, contradiciendo el invariante de `Task/005.4`. **6 reglas operativas corregidas** |
| **Correcciones de secuencia** | `Task/025` pasa a depender también de **`Task/024`** · `Task/029` deja de exigir evidencia que solo existe tras `Task/030`/`Task/032` · `Task/021` deja de prometer Terraform inexistente · la topología de dominios deja de depender de `Task/035` |
| **Propietarios asignados** | `S3Storage` · backup productivo · identidad del VPS hacia AWS · certificado TLS · observabilidad del VPS · migraciones en producción · medios públicos · credenciales CI multi-provider |
| **Decisiones nuevas** | **D-15** (topología lógica de dominios, `Task/011`) y **D-16** (identidad del VPS hacia AWS, `Task/029`). *Observado el 2026-08-16: ambas abiertas.* **D-15 quedó resuelta en `Task/011`** (2026-09-01); **D-16 sigue abierta** |
| **ADR** | **Ninguno nuevo.** No apareció ninguna decisión arquitectónica independiente: se corrigieron *ownership* y secuencia, no arquitectura |
| **Arquitectura** | **Sin cambios.** Cloudflare Pages, API Gateway, Lambda, S3, SSM, IAM, CloudWatch, PgBouncer, PostgreSQL en VPS, Terraform, Floci y `ObjectStorage` siguen exactamente igual |
| **Implementación** | **Ninguna.** 0 código funcional, 0 Terraform, 0 Compose, 0 recursos cloud, 0 VPS, 0 GitHub Actions |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. **41 identificadores intactos**, sin renumerar. Avance global y ETAPA 02 **sin cambios** |
| **Imagen de arquitectura** | `images/Infraestructura.png` **intacta**. Se corrigieron los textos que aún la trataban como autoridad canónica de producción |
| **Integración en `dev`** | Merge `--no-ff` en los **tres** repositorios, publicado |
| **Pull request** | `Task/005.5 → main` en los tres repositorios. *Observado el 2026-08-16 con `gh pr list`:* **`#11` infra, `#3` backend y `#2` frontend — `MERGED`**, fusionados por el usuario |
| **Normalización posterior** | **Completada.** *Observado el 2026-08-16:* `main` = `bd0aaf5` (infra), `72c8adc` (backend), `4132a65` (frontend); `main` integrada en `dev` y publicada — `dev` = `2819f6c` · `1e20839` · `7e89d2a`. `git diff main dev` **vacío** y `main` **ancestro de `dev`** en los tres |
| **Rama Task** | Eliminada **local y remotamente** en los tres. *Observado el 2026-08-16:* `git ls-remote --heads origin "Task/*"` **no devuelve nada** |
| **Ficha** | [TASK-005.5](../tasks/TASK-005.5-align-planning-after-audit.md) |
| **Reporte** | [TASK-005.5-report](../task-reports/TASK-005.5-report.md) |

La aprobación de este mantenimiento **no modifica el conteo del roadmap**: el avance global
permanece en **5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas.

Con ella quedan **vigentes**: el invariante de ramas aplicado a **los tres repositorios**,
el **mapa de responsabilidades transversales** del ROADMAP, la dependencia
`Task/025 → Task/024`, la separación entre lo que `Task/029` **define** y lo que solo puede
**validarse** más tarde, y las decisiones **D-15** y **D-16**, ambas **abiertas**.
`Task/006` sigue **Pendiente y no iniciada**.

---

## Mantenimiento aprobado anterior — `Task/005.7`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion` |
| **Tipo** | **Mantenimiento transversal**: hermeticidad del harness de pruebas y *fail-closed* real de la integración |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-16 |
| **Fecha de aprobación** | 2026-08-16 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion` |
| **Repositorios afectados** | `personal-blog-backend`, `personal-blog-infra`, `personal-blog-frontend` |
| **Rama** | `Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion` en los tres |
| **Rama base** | **`main`** en los tres. SHA base: infra `7c98f59` · backend `c36cd44` · frontend `5d2bef1`. Verificado `HEAD == main` inmediatamente después de crearlas |
| **Origen** | Mega auditoría final independiente (Claude y Codex). Ambos reprodujeron los **mismos dos defectos**; discreparon en severidad (Claude: MEDIO, diferir · Codex: ALTO, baseline no certificada). Se adopta **deliberadamente el criterio más estricto**: corregir ahora |
| **CERT-AUD-001** | **Cerrado.** El arranque de la suite ya no consume el `.env` del desarrollador, tampoco durante la *collection*. Dos capas independientes en `tests/` |
| **CERT-AUD-002** | **Cerrado.** Un único resolutor verificado (`destino_de_integracion_verificado`) alimenta todas las fixtures de integración. No queda ruta oficial sin guarda |
| **Comprobación estructural** | Los módulos del harness se **descubren** del directorio `tests/integration/`, no se enumeran a mano: añadir un módulo nuevo no exige recordar registrarlo. *(Corregido durante la validación del usuario: la lista manual fallaba **abierta** y ya omitía dos módulos existentes.)* |
| **CERT-AUD-009** | **Diferido con propietario explícito**: `Task/020-CI-Backend`. Riesgo **R-37**. No se implementa paralelismo ahora |
| **Implementación** | **0 funcionalidad de negocio.** `app/` **sin cambios**. 0 código frontend, 0 Terraform, 0 recursos cloud |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global y ETAPA 02 **sin cambios** |
| **Ficha** | [TASK-005.7](../tasks/TASK-005.7-close-final-certification-findings.md) |
| **Reporte** | [TASK-005.7-report](../task-reports/TASK-005.7-report.md) |

Este mantenimiento **no modifica el conteo del roadmap**: el avance global permanece en
**5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas. `Task/006` sigue
**Pendiente y no iniciada**.

Con esta aprobación quedan **vigentes**: el **arranque hermético** del harness de pruebas
—la suite no consume el `.env` del desarrollador ni durante la *collection*—, la garantía
***fail-closed*** del harness de integración con un **único resolutor verificado**, el
**descubrimiento automático** de los módulos del harness en la comprobación estructural, la
coherencia entre `.gitattributes` y `.editorconfig` en los tres repositorios y las secciones
§8.3.5 – §8.3.7 de [BACKEND_TESTING_STRATEGY](BACKEND_TESTING_STRATEGY.md).

El alcance de la garantía es el **harness oficial**, no Python arbitrario: la documentación
no promete más protección de la que existe.

---

## Mantenimiento anterior aprobado — `Task/005.6`

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.6-Cerrar-Fundaciones-Tras-Mega-Auditoria` |
| **Tipo** | **Mantenimiento transversal de fundaciones**: reproducibilidad, aislamiento de pruebas y estado documental |
| **Estado** | **Aprobada** ✔ |
| **Fecha de inicio** | 2026-08-16 |
| **Fecha de aprobación** | 2026-08-16 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.6-Cerrar-Fundaciones-Tras-Mega-Auditoria` |
| **Repositorios afectados** | `personal-blog-infra`, `personal-blog-backend`, `personal-blog-frontend` |
| **Rama** | `Task/005.6-Cerrar-Fundaciones-Tras-Mega-Auditoria` en los tres |
| **Rama base** | **`main`** en los tres. SHA base: infra `bd0aaf5` · backend `72c8adc` · frontend `4132a65`. Verificado `HEAD == main` inmediatamente después de crearlas |
| **Origen** | Conciliación de **dos mega auditorías independientes** (Claude y Codex). Ninguna se aceptó como autoridad: cada hallazgo se **reprodujo** contra el repositorio antes de decidir |
| **Conclusión de ambas auditorías** | **No existe defecto arquitectónico.** Arquitectura, Git, roadmap, PostgreSQL, FastAPI, Docker, Alembic y las *boundaries* son reutilizables |
| **Política EOL** | `.gitattributes` en los **tres** repositorios. Causa raíz: `core.autocrlf=true` de nivel *system* convertía el árbol de trabajo a CRLF y `ruff format --check .` fallaba en los 31 archivos Python. **El índice ya era LF**: la corrección produce **0 líneas de diff de contenido** |
| **Aislamiento de pruebas** | `settings_factory` construye con `_env_file=None`: la suite ya no lee el `.env` del desarrollador. Con regresión y guarda anti-tautología |
| **Base de datos de pruebas** | `personal_blog_test`, **dedicada**. Guarda *fail-closed* de dos barreras: sufijo `_test` **y** marca `personal-blog:test-database` **dentro** de la base. `personal_blog` **no se toca** |
| **Skip frente a fail** | Sin variable de entorno → `SKIP`. Con variable y PostgreSQL roto → **`FAIL`**. Ningún error se degrada ya a `skip` |
| **Tests semánticos** | `commit` y `rollback` demuestran **efecto persistente observado desde otra sesión**. Verificados por **mutación**: con `session_scope` roto, ambos se ponen rojos |
| **Migraciones** | Contrato durable: el esquema tras `upgrade` + `downgrade` debe ser idéntico al de antes. Sustituye a la aserción que habría caducado en `Task/008` |
| **Implementación** | **0 funcionalidad de negocio.** `app/` **sin cambios**: `git diff -- app/` vacío. 0 código frontend, 0 Terraform, 0 recursos cloud, 0 cambios en Docker Compose |
| **Roadmap** | **No cuenta** dentro de las 41 tareas. Avance global y ETAPA 02 **sin cambios** |
| **Regla de gobierno nueva** | [WORKFLOW §6.1](WORKFLOW.md): los documentos versionados registran **estado duradero**; el estado transitorio de Git/GitHub se consulta **en vivo**. Elimina la necesidad estructural de una tarea de mantenimiento tras cada fusión |
| **ADR** | **Ninguno nuevo.** No apareció ninguna decisión arquitectónica: se corrigieron reproducibilidad, aislamiento de pruebas y precisión documental. **`ADR-001` no cambia su decisión**, solo una cifra frágil por una referencia por etapas |
| **Arquitectura** | **Sin cambios.** Monolito modular, FastAPI, PostgreSQL, MinIO/S3, Cloudflare Pages, API Gateway, Lambda, Terraform, Floci y PgBouncer siguen exactamente igual |
| **Riesgo nuevo** | **R-36** — el log no redacta secretos de forma automática. **Abierto** cuando `Task/005.6` lo registró, con propietario `Task/017` y `Task/018`. Su plano local queda **cerrado por `Task/017`**, **Aprobada** el 2026-09-06; ver el registro de riesgos |
| **Integración en `dev`** | Merge `--no-ff` en los **tres** repositorios, publicado |
| **Pull request** | `Task/005.6 → main` en los tres. Base `main`, head la rama Task. **Ninguno es `dev → main`** y **ninguno lo fusiona Claude** |
| **Ficha** | [TASK-005.6](../tasks/TASK-005.6-close-foundations-after-mega-audit.md) |
| **Reporte** | [TASK-005.6-report](../task-reports/TASK-005.6-report.md) |

Este mantenimiento **no modifica el conteo del roadmap**: el avance global permanece en
**5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas. `Task/006` sigue
**Pendiente y no iniciada**.

Con esta aprobación quedan **vigentes**: la política de finales de línea de los tres
repositorios, la **base de datos de pruebas dedicada** con sus guardas *fail-closed*, la
distinción **skip / fail** de la integración, la verificación **semántica** de
`commit`/`rollback`, el contrato durable de migraciones y la regla de gobierno de
[WORKFLOW §6.1](WORKFLOW.md). El **invariante de ramas no cambia**: toda Task nace de `main`.

---

## Mantenimiento aprobado anterior — `Task/005.4`

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
| **Pull request** | `Task/005.4-Corregir-Base-Ramas-Task-Main → main` (**`#10`**) — **FUSIONADO** por el usuario. Merge commit **`cc90b96`**, `mergedAt = 2026-08-16T04:20:19Z` (UTC) |
| **Normalización posterior** | **Completada.** `main` = `cc90b96`; `main` integrada en `dev` (`f2eb330`, `Merge branch 'main' into dev`), publicado. `git diff main dev` **vacío** y `main` es **ancestro de `dev`**. Verificado el 2026-08-16 al iniciar `Task/005.5` |
| **Rama Task** | Eliminada **local y remotamente**. `git ls-remote --heads origin "Task/*"` **no devuelve nada** |
| **Ficha** | [TASK-005.4](../tasks/TASK-005.4-correct-task-branch-base-main.md) |
| **Reporte** | [TASK-005.4-report](../task-reports/TASK-005.4-report.md) |

La aprobación de este mantenimiento **no modifica el conteo del roadmap**: el avance global
permanece en **5 de 41 (12 %)** y la ETAPA 02 en **1 de 3** tareas aprobadas.

Con ella, el **invariante de ramas** queda **vigente y de cumplimiento obligatorio**:
**toda rama `Task/<...>` nace desde `main` actualizado y limpio; `dev` nunca es base de una
Task.** `Task/006` sigue **Pendiente y no iniciada**, y **nacerá desde `main`**.

> **Corrección de alcance registrada en `Task/005.5`.** `Task/005.4` corrigió el invariante
> **solo en `personal-blog-infra` y en el `CLAUDE.md` raíz**. `personal-blog-backend` y
> `personal-blog-frontend` conservaban en su `README.md` y su `CONTRIBUTING.md` la regla
> antigua —*«creado desde `dev`»*—, que seguía siendo **instrucción operativa vigente** en
> esos repositorios. `Task/005.5` cierra ese hueco: **0 reglas operativas** ordenan ya crear
> una Task desde `dev` en ninguno de los tres repositorios.

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
| 02 — Fundaciones de las Aplicaciones | 3 | 3 | **100 %** — **completada** |
| 03 — Dominio y Backend | 5 | **5** | **100 %** — **completada** |
| 04 — Experiencia del Usuario | 3 | **3** | **100 %** — **completada** |
| 05 — Calidad y Seguridad | 3 | 0 | 0 % |
| 06 — Integración Continua | 3 | 0 | 0 % |
| 07 — Validación Local | 1 | 0 | 0 % |
| 08 — Preparación Cloud sin Cuentas | 4 | 0 | 0 % |
| 09 — Cuentas y Seguridad Cloud | 3 | 0 | 0 % |
| 10 — Despliegue Cloud | 7 | 0 | 0 % |
| 11 — Automatización de Despliegues | 3 | 0 | 0 % |
| 12 — Lanzamiento y Operación | 2 | 0 | 0 % |
| **Total** | **41** | **15** | **37 %** |

Distribución por estado:

| Estado | Tareas |
| --- | --- |
| Pendiente | **26** |
| En progreso | 0 |
| Lista para validación | **0** |
| **Aprobada** | **15** |
| Bloqueada | 0 |
| Descartada | 0 |
| **Total** | **41** |

> `Lista para validación` **no suma avance**: el porcentaje solo cuenta tareas
> `Aprobada`, y solo el usuario aprueba.

> `Lista para validación` **no** suma al avance: el recuento de la tabla de
> arriba solo cuenta tareas `Aprobada`, y quien aprueba es el usuario.

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
| R-03 | La elección de la base de datos de producción condiciona el diseño de conexiones desde Lambda (pooling, límites). | Medio | Evaluar en `Task/029` y considerar el patrón de conexión desde `Task/005`. **Actualización vigente desde el 2026-08-15 (`Task/005.3`, aprobada):** con PostgreSQL en un VPS, la mitigación concreta es **PgBouncer** con pool limitado más *Reserved Concurrency* de Lambda, aplicada en `Task/032`; ver **R-33**. | Abierto |
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

### Riesgos introducidos por `Task/011` — autenticación administrativa

> **Abiertos** desde la aprobación de `Task/011`, el 2026-09-01.

| # | Riesgo | Impacto | Mitigación prevista | Tarea que lo valida | Estado |
| --- | --- | --- | --- | --- | --- |
| R-43 | **El bloqueo de cuenta puede dejar fuera al único administrador.** Cinco fallos consecutivos bloquean la cuenta quince minutos, y durante ese tiempo la API responde **exactamente igual** que ante unas credenciales inválidas —decisión deliberada, porque distinguirlo permitiría averiguar que ese correo existe—. El propietario que se equivoque cinco veces verá «credenciales inválidas» sin saber por qué. | Medio | El bloqueo es **temporal y no se alarga**: un intento durante el bloqueo no desplaza `locked_until`, así que nadie puede mantenerlo indefinidamente. Umbral y duración son configurables. El motivo real queda en la auditoría (`authentication.account_locked`) y en el log, que es donde el operador puede consultarlo. | `Task/018` (endurecimiento) · `Task/022` (validación local *production-like*) | **Abierto** |
| R-44 | **Las tablas de estado de autenticación crecen de forma monótona.** **Ninguna** tiene purga productiva: no hay procesos residentes, porque el backend debe funcionar igual en Lambda (software-architecture.md §6). (a) **`login_rate_limits`** —**la fuente de crecimiento potencialmente mayor**— escribe una fila por dirección IP observada, así que con tráfico hostil sostenido acumula filas indefinidamente. (b) **`administrator_sessions`** escribe una fila por **inicio de sesión con éxito**, y las caducadas o revocadas **no desaparecen**: `RepositorioSqlDeSesiones` solo crea, busca la vigente y revoca. | Bajo | El volumen es despreciable en un blog personal —una dirección por fila en (a); con un único administrador, la tasa de (b) es pequeña— y ninguna de las dos tablas alimenta un listado. La purga es una sentencia periódica sobre filas caducadas o revocadas; corresponde a operación, no a la aplicación. | `Task/018` o `Task/029` (operación) | **Abierto** |
| R-45 | **La imagen de despliegue incorpora una dependencia binaria nueva.** `argon2-cffi` no es Python puro: necesita una rueda compilada para el destino Linux/Lambda. Un empaquetado en una plataforma equivocada produciría un artefacto que **no arranca en producción**, y el fallo aparecería en el despliegue, no en el desarrollo. | Medio | Verificado en `Task/011` que **existe rueda `manylinux_2_17_x86_64`** para Python 3.12 —`argon2_cffi_bindings-…-cp36-abi3-manylinux…whl`, 86 KB, `abi3`, por tanto independiente de la versión concreta de CPython—, descargándola explícitamente con `--platform`. **La imagen no se reconstruyó** en esta tarea. | Comprobación del usuario · `Task/024` y `Task/032` al empaquetar | **Abierto** |
| R-46 | **La confianza en proxies no está fijada para ningún despliegue real.** `BLOG_TRUSTED_PROXY_HOP_COUNT` vale `0` por defecto, lo que **ignora `X-Forwarded-For`** y usa la dirección del par TCP. Detrás de Traefik o de API Gateway esa dirección es la del proxy, así que **todo el tráfico caería en una única partición** del límite de tasa y la auditoría registraría siempre la misma IP. | Medio | El valor por defecto es el **seguro**: creerse la cabecera sin proxy de confianza permitiría falsificar una dirección por intento y anular el límite. El mecanismo existe y está probado en ambos sentidos; lo que falta es **decidir el número de saltos** de cada despliegue. | Runbook del entorno local · `Task/033` (API Gateway) | **Abierto** |

---

### Riesgo introducido por `Task/005.6` — redacción de secretos en el log

| # | Riesgo | Impacto | Mitigación prevista | Tarea que lo valida | Estado |
| --- | --- | --- | --- | --- | --- |
| R-36 | **El log no tiene redacción automática de secretos.** `JsonLogFormatter` emite en `context` **todo** atributo propio del `LogRecord` y serializa las excepciones completas. La regla S-08 —«los logs no contienen contraseñas, tokens ni cadenas de conexión»— existe y se cumple hoy, pero depende de que **quien registra el evento** no pase un valor sensible: no hay ningún mecanismo que lo impida. Una excepción de driver o un `extra` descuidado pueden filtrar una credencial. Reproducido en `Task/005.6` por inspección del formateador. | Medio | **Deliberadamente NO se corrige en `Task/005.6`**: construir una política de redacción completa —lista de claves sensibles, patrones de token y URL, redacción en mensaje, contexto y traza— es trabajo de observabilidad y endurecimiento, no de cierre de fundaciones. Mitigación vigente: `database_url` está excluida de `repr` y solo se expone por `database_url_safe`, verificado en el contenedor real (`blog_local:***@`); `ConfigurationError` nombra campos, nunca valores. | `Task/017` (observabilidad, correlation ID y política de log) y `Task/018` (endurecimiento de seguridad) | **Cerrado en el plano local** por `Task/017`, **Aprobada** el 2026-09-06. El mecanismo existe y está probado: redacción por **nombre de campo** y por **forma del valor**, aplicada al mensaje, al contexto y a la **cadena de excepciones**, en `json` y en `text`, idempotente y sin destruir el diagnóstico —la DSN conserva esquema, anfitrión, puerto y base; la excepción conserva su tipo—. Las pruebas siembran un señuelo y exigen que no aparezca en la salida. La causa que abrió el riesgo —*«depende de que quien registra el evento no pase un valor sensible»*— **deja de sostenerse en el plano local**. **Sigue abierto** para el endurecimiento de la política (`Task/018`) y para la telemetría **exportada**, que es **O-09** y no este riesgo (`Task/029`, `Task/040`) | **Abierto** — solo para `Task/018` |

### Riesgo introducido por `Task/005.7` — concurrencia de la suite de integración

> **Abierto y vigente** desde la aprobación de `Task/005.7` el 2026-08-16.

| # | Riesgo | Impacto | Mitigación prevista | Tarea que lo valida | Estado |
| --- | --- | --- | --- | --- | --- |
| R-37 | **La suite de integración no es segura para ejecución concurrente sobre la misma base de datos** (`CERT-AUD-009`). Tres causas concretas, reproducidas por inspección en `Task/005.7`: (1) `tabla_de_pruebas` usa un **nombre fijo** —`prueba_transaccional_005_6`—, así que dos procesos se pisan la tabla y el `DROP` de uno rompe al otro; (2) `test_migrations` ejecuta **`alembic downgrade base` sobre el esquema compartido**, que revierte el esquema entero por debajo de cualquier otro test en vuelo; (3) las fixtures **mutan estado de proceso** —`os.environ["BLOG_DATABASE_URL"]`, `get_settings.cache_clear()`, `dispose_engine()`—, que es seguro entre procesos pero no entre hilos. | Medio | **Deliberadamente NO se corrige en `Task/005.7`.** Hoy no hay ejecución paralela oficial: `pytest-xdist` **no está instalado** y el único flujo de integración esperado es secuencial, así que el riesgo **no es explotable en el estado actual**. Construir aislamiento por trabajador —esquema o base por *worker*, nombres de tabla derivados del `worker_id`, aislamiento del estado de proceso— es diseño de CI, no cierre de fundaciones, y hacerlo ahora sería sobrediseñar sin un consumidor real. **Debe revisarse antes de habilitar cualquier ejecución paralela**, y la decisión de habilitarla es lo que activa este riesgo. | `Task/020-CI-Backend` — propietaria de la concurrencia de CI del backend | **Abierto** |

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
| R-32 | **Pérdida del VPS o del disco**, o **agotamiento de recursos**: un disco lleno detiene PostgreSQL y puede impedir el propio backup. | **Alto** | Backups **fuera del host** — una copia que solo vive en el VPS no protege de esto. Monitoreo de espacio y de recursos con alertas; dimensionamiento y política de crecimiento en `Task/029`. **Owner corregido en `Task/005.5`:** `Task/017` es observabilidad **local** y no cubre el VPS; el *baseline* lo construye `Task/029` y lo verifica `Task/040`. | `Task/029`, `Task/040` | **Abierto** |
| R-33 | **Agotamiento de conexiones**: una ráfaga de concurrencia de Lambda supera `max_connections` de PostgreSQL. Es la materialización de **R-03** en esta topología. | Medio | **PgBouncer** con pool limitado más ***Reserved Concurrency*** de Lambda aguas arriba. Los tres números —concurrencia, pool y `max_connections`— se derivan de **pruebas**, no de intuición. | `Task/029`, `Task/032` | **Abierto** |
| R-34 | **Latencia `Lambda ↔ VPS`.** La base de datos deja de estar en la misma región que el cómputo; cada consulta paga el RTT y una petición HTTP suele hacer varias. | Medio | Selección de región del VPS teniendo en cuenta la región AWS, con **RTT medido**, no estimado. Regla explícita: no elegir un VPS lejano por ahorrar poco al mes. | `Task/029`, `Task/040` | **Abierto** |
| R-35 | **Error humano de operación.** Sin consola administrada que ponga barreras, un comando equivocado puede borrar datos, exponer un puerto o dejar el servicio caído. | Medio | Infraestructura reproducible con Terraform; runbooks escritos para cada operación; backups fuera del host como red de seguridad; regla vigente de no ejecutar operaciones destructivas sin autorización explícita. | `Task/026`, `Task/029` | **Abierto** |

### Riesgos introducidos por `Task/006.2` — arquitectura objetivo de producción

> **Abiertos y vigentes** desde la aprobación de `Task/006.2` el 2026-08-23. **Ninguno está
> cerrado**: son consecuencia asumida de las decisiones de observabilidad y de operación del
> VPS, no defectos pendientes. Detalle:
> [target-production-architecture.md](../architecture/target-production-architecture.md) —
> **Vigente** ·
> [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) — **Aceptada**.

| # | Riesgo | Impacto | Mitigación prevista | Tarea que lo valida | Estado |
| --- | --- | --- | --- | --- | --- |
| R-38 | **Dependencia de un tier gratuito de terceros.** El plano central de observabilidad es **Grafana Cloud**, y el objetivo inicial es su tier gratuito. Los límites y precios de un plan gratuito **cambian**, y pueden dejar de ser suficientes justo cuando el sistema ya depende de ellos para diagnosticar incidentes. | Medio | **Declarado explícitamente como preferencia presupuestaria, no como dependencia arquitectónica**: si deja de servir, se paga, se reduce el volumen de telemetría o se cambia de destino, **sin romper la arquitectura**. **Ninguna cifra comercial se persiste** en la documentación; las que se registren se marcan *«verificar en `Task/041` / antes de contratar»*. **D-19**. | `Task/041`, con aporte de `Task/027` | **Abierto** |
| R-39 | **La telemetría sale del perímetro del proyecto y puede llevar lo que no debe.** Alloy recolecta logs del host y de PostgreSQL y los envía a un tercero. Un log de driver, una consulta con parámetros o un volcado de error pueden contener credenciales o datos personales. **Es la misma familia que R-36, en otro plano y con destino externo.** | **Alto** | **Qué se recolecta es parte del diseño, no configuración** (**O-09**). Selección explícita de fuentes, sin recolección indiscriminada; regla **O-08** aplicada también aquí; verificación por muestreo en `Task/040`. La redacción en el log de aplicación sigue siendo de `Task/017` y `Task/018` (**R-36**). | `Task/029`, `Task/018`, `Task/040` | **Abierto** |
| R-40 | **Secretos del VPS mal gestionados.** El host necesita sus propios secretos —contraseñas de PostgreSQL y PgBouncer, clave privada del certificado, credencial de backup y credencial de Alloy— y **la herramienta todavía no está elegida** (**D-17**). Sin cifrado, custodia y rotación definidos, el compromiso del VPS entrega todo de golpe. | **Alto** | Modelo **ya cerrado**: cifrados, **clave fuera del repositorio**, descifrado local seguro, **nada versionado en claro** (regla V-08). La herramienta y la rotación se deciden en `Task/029`. **Mientras D-17 siga abierta no se instala nada ni se generan claves.** | `Task/029`, `Task/018` | **Abierto** |
| R-41 | **El agente de observabilidad compite por los recursos de PostgreSQL.** Alloy consume RAM, CPU y disco en la misma máquina que la base de datos, que es el componente que no puede degradarse (**R-32**). | Bajo | **Agente, no *stack***: se descarta autohospedar Grafana, Prometheus o Loki en el VPS. El dimensionamiento de `Task/029` contempla el consumo del agente, y `Task/040` verifica que el host sigue holgado. | `Task/029`, `Task/040` | **Abierto** |
| R-42 | ***Drift* de configuración del VPS.** Terraform **no configura el sistema operativo** por decisión (**D-18**), así que lo que hay dentro del host puede alejarse en silencio de lo documentado. Un cambio manual «temporal» sobrevive hasta el día de la reconstrucción, cuando ya nadie recuerda que existía. | Medio | Mecanismo **idempotente y reproducible** decidido en `Task/029` —Ansible, cloud-init o scripts—, runbooks escritos (`Task/026`), y verificación de que el host reconstruido coincide con lo documentado (`Task/040`). Refuerza la mitigación de **R-35**. | `Task/029`, `Task/026`, `Task/040` | **Abierto** |

---

## Tabla completa de tareas

| Tarea | Etapa | Repos | Estado |
| --- | --- | --- | --- |
| `Task/001-Inicializar-Workspace-y-Roadmap` | 00 | infra, frontend, backend | **Aprobada** |
| `Task/002-Definir-MVP-y-Arquitectura` | 00 | infra | **Aprobada** |
| `Task/003-Crear-Infraestructura-Local` | 01 | infra | **Aprobada** |
| `Task/004-Backups-y-Recuperacion-Local` | 01 | infra | **Aprobada** |
| `Task/005-Fundacion-Backend-FastAPI` | 02 | backend, infra (documentación) | **Aprobada** |
| `Task/006-Fundacion-Frontend-React` | 02 | frontend, infra (documentación) | **Aprobada** |
| `Task/007-Integracion-Local` | 02 | infra, frontend | **Aprobada** |
| `Task/008-Modelo-de-Datos` | 03 | backend, infra (documentación) | **Aprobada** |
| `Task/009-API-Publica` | 03 | backend, infra (documentación) | **Aprobada** |
| `Task/010-Almacenamiento-Compatible-S3` | 03 | backend, infra (documentación) | **Aprobada** |
| `Task/011-Autenticacion-Administrativa` | 03 | backend, infra | **Aprobada** |
| `Task/012-API-Administrativa` | 03 | backend, infra | **Aprobada** (2026-09-03) |
| `Task/013-Sistema-de-Diseno` | 04 | frontend, infra (documentación) | **Aprobada** (2026-09-04) |
| `Task/014-Sitio-Publico` | 04 | frontend, infra (documentación) | **Aprobada** (2026-09-05) |
| `Task/015-Panel-Administrativo` | 04 | frontend, infra (documentación) | **Aprobada** (2026-09-05) |
| `Task/016-SEO-Accesibilidad-y-Rendimiento` | 05 | frontend, backend, infra (documentación + wiring local mínimo) | **Aprobada** (2026-09-06) |
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

> **Cómo leer esta sección** (regla de [WORKFLOW §6.1](WORKFLOW.md), vigente desde
> `Task/005.6`). Lo de abajo es una **observación fechada**, no una afirmación permanente.
> El estado vivo de ramas y PR se consulta en Git y GitHub —`git fetch --prune`,
> `git ls-remote --heads origin "Task/*"`, `gh pr list`—, nunca leyendo este documento.

**Observado el 2026-09-03**, al ejecutar el cierre aprobado de `Task/012`:

- Las dos ramas `Task/012-API-Administrativa` —backend e infra— nacieron **desde `main`**,
  con `HEAD == main` verificado inmediatamente después de crearlas: `561128b5…` (backend) y
  `eceb5b35…` (infra).
- Antes del commit de cierre, ninguna de las dos tenía commits propios sobre `main`
  (`git rev-list --count main..HEAD` = **0**) ni nada en *staging*.
- `personal-blog-frontend` **no participó**: en `main`, worktree limpio, sin rama Task.
- El cierre integra cada rama en `dev` con merge `--no-ff`, publica `dev` y la rama Task, y
  abre el pull request **`Task/012-API-Administrativa → main`**. **Ningún PR usa `dev` como
  *head*** y **ninguno lo fusiona Claude**.
- **El estado vivo** —si el PR sigue abierto o ya se fusionó, si la rama remota existe, los
  SHA concretos— **no se escribe aquí**: se consulta con `git fetch --prune`,
  `git ls-remote --heads origin "Task/*"` y `gh pr list`
  ([WORKFLOW §6.1](WORKFLOW.md)).

**Observado el 2026-08-18**, tras el cierre aprobado de `Task/006`:

- Las dos ramas `Task/006` —frontend e infra— nacieron **desde `main`**, con `HEAD == main`
  verificado inmediatamente después de crearlas.
- Ambas se integraron en `dev` con merge `--no-ff` y se publicaron en `origin`.
- Los pull request son **`Task/006-Fundacion-Frontend-React → main`** en los dos
  repositorios. **Ninguno usa `dev` como *head*** y **ninguno lo fusionó Claude**.
- Las ramas Task **locales** se eliminaron con `git branch -d`; las **remotas se conservan**:
  eliminarlas es decisión del usuario.
- `personal-blog-backend` **no participó**: sin rama Task, worktree limpio, en `main`.

Los SHA y las URL concretas se consultan en vivo con `git fetch --prune`,
`git ls-remote --heads origin "Task/*"` y `gh pr list`, según
[WORKFLOW §6.1](WORKFLOW.md).

**Observado el 2026-08-16**, tras la fusión de los PR de `Task/005.5` y su normalización, y
al crear las ramas de `Task/005.6`:

| Repositorio | Ramas locales | Ramas remotas | `main` | `dev` | `main` y `dev` |
| --- | --- | --- | --- | --- | --- |
| `personal-blog-infra` | `main`, `dev`, `Task/005.6-...` | `main`, `dev` — **ninguna rama `Task/*`** | `bd0aaf5` | `2819f6c` | **Sincronizadas** — `git diff main dev` vacío |
| `personal-blog-backend` | `main`, `dev`, `Task/005.6-...` | `main`, `dev` — **ninguna rama `Task/*`** | `72c8adc` | `1e20839` | **Sincronizadas** — `git diff main dev` vacío |
| `personal-blog-frontend` | `main`, `dev`, `Task/005.6-...` | `main`, `dev` — **ninguna rama `Task/*`** | `4132a65` | `7e89d2a` | **Sincronizadas** — `git diff main dev` vacío |

Las tres ramas `Task/005.5` se crearon **desde `main`**, con `HEAD == main` verificado
inmediatamente después. Los tres pull request fueron **`Task/005.5 → main`**; **ninguno fue
`dev → main`** y **ninguno lo fusionó Claude**. Las tres ramas `Task/005.6` se crearon
igualmente **desde `main`**, con `HEAD == main` verificado.

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
  pull request `Task/005 → main` en cada repositorio. La rama Task local se eliminó con
  `git branch -d`. *(Corregido en `Task/005.6`: esta viñeta afirmaba «**Los PR siguen
  abiertos**», contradiciendo a la viñeta siguiente y a la tabla de `Task/005`, que
  registran su fusión el 2026-08-13. Se elimina la contradicción, no la historia: el
  desenlace real está en la viñeta siguiente.)*
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
  `dev` y la rama Task, y abrió el pull request `Task/005.4 → main` (**`#10`**).
- **PR `#10` fusionado y normalización completada (2026-08-16).** El usuario fusionó
  `Task/005.4 → main` (merge commit **`cc90b96`**, `mergedAt = 2026-08-16T04:20:19Z` UTC) y
  eliminó la rama remota. Verificado con `gh pr view 10` —devuelve `MERGED`— y con
  `git ls-remote --heads origin "Task/*"`, que **no devuelve ninguna rama**. `main` está
  integrada en `dev` (`f2eb330`): `git diff main dev` **vacío** y `main` **ancestro de
  `dev`**.
- `Task/005.5-Alinear-Planificacion-Tras-Auditoria` se creó el 2026-08-16 **desde `main`**
  en **los tres repositorios** —infra (`cc90b96`), backend (`db6ab18`) y frontend
  (`144a401`)—, con `HEAD == main` verificado en cada uno. Es la **segunda tarea creada
  desde `main`** y la primera que aplica el invariante en los tres repositorios a la vez.
  Es mantenimiento de gobierno y planificación: **no cuenta** en las 41 tareas y **no altera
  el avance**. Fue **aprobada** el 2026-08-16; su cierre creó el commit en cada repositorio,
  integró la rama en `dev` con merge `--no-ff`, publicó `dev` y la rama Task, y abrió el
  pull request `Task/005.5 → main` en los tres. La rama Task local se eliminó con
  `git branch -d`.
- **Los tres PR de `Task/005.5` fueron fusionados por el usuario.** *Observado el
  2026-08-16 con `gh pr list`:* `#11` (infra), `#3` (backend) y `#2` (frontend), los tres
  `MERGED`. `main` quedó en `bd0aaf5` · `72c8adc` · `4132a65`, se integró en `dev` y se
  publicó (`2819f6c` · `1e20839` · `7e89d2a`). `git ls-remote --heads origin "Task/*"` **no
  devuelve ninguna rama**, `git diff main dev` está **vacío** y `main` es **ancestro de
  `dev`** en los tres repositorios.
- `Task/005.6-Cerrar-Fundaciones-Tras-Mega-Auditoria` se creó el 2026-08-16 **desde `main`**
  en **los tres repositorios** —infra (`bd0aaf5`), backend (`72c8adc`) y frontend
  (`4132a65`)—, con `HEAD == main` verificado en cada uno. Es la **tercera tarea creada
  desde `main`**. Es mantenimiento transversal de fundaciones: **no cuenta** en las 41
  tareas y **no altera el avance**. Fue **aprobada** el 2026-08-16; su cierre creó el commit
  en cada repositorio, integró la rama en `dev` con merge `--no-ff`, publicó `dev` y la rama
  Task, y abrió el pull request `Task/005.6 → main` en los tres. La rama Task local se
  eliminó con `git branch -d`.

---

## Notas de estado

- **`Task/014-Sitio-Publico` quedó `Aprobada` el 2026-09-05.** La sesión del 2026-09-04 fue
  de **definición** (preflight, ramas desde `main`, ficha con matriz funcional) y la del
  2026-09-05 de **implementación**: doce superficies del sitio público, capa
  `services/public`, Markdown sanitizado con las dos dependencias autorizadas, videos con
  lista cerrada, favicon provisional, guardas extendidas y 440 pruebas. El avance sube a
  **14 de 41** y la ETAPA 04 a **2 de 3**. Los hallazgos independientes —índice de reportes,
  tabla resumen del ROADMAP y valor esperado de `alembic current` en el runbook— quedan
  registrados en su sección **sin corregirse aquí**.
- **`Task/005` produce el primer código de aplicación del proyecto:** `personal-blog-backend`
  ya contiene una aplicación FastAPI que arranca, expone `/health` y OpenAPI, se conecta al
  PostgreSQL local y gestiona su esquema con Alembic. Está **`Aprobada`** desde el
  2026-08-12. *(El código React llegó después, con `Task/006`; ver la nota siguiente.)*
- **Correcciones del 2026-08-11, en la misma rama y sin commit:** el log emite ahora UTC
  explícito —antes el formato dependía del sistema operativo— con 9 pruebas deterministas
  comprobadas en Windows y en Docker; la advertencia de `starlette.testclient` se resolvió
  cambiando `httpx` por `httpx2` en las dependencias de desarrollo, sin silenciar nada en
  `pyproject.toml`, de modo que `pytest -W error` termina con **0 warnings y sin ningún
  filtro** en los dos entornos; se rectificó la afirmación errónea de que rotar la contraseña de
  PostgreSQL obliga a recrear su volumen; y se verificó que el `Dockerfile` es coherente con
  **R-14**. **El avance global no cambia.**
- **`Task/006` produce el primer código de interfaz del proyecto:**
  `personal-blog-frontend` ya contiene una aplicación React que monta, enruta, valida su
  configuración de entorno al arrancar y dispone de un cliente HTTP común con modelo de
  error. Está **`Aprobada`** desde el 2026-08-18, lo que lleva el avance a **6 de 41 (15 %)**
  y la ETAPA 02 a **2 de 3**. Su alcance **no** incluye sistema de diseño, páginas del sitio
  público, panel administrativo, autenticación ni consumo real del API.
- **Defecto corregido durante la revisión de `Task/006`:** el cliente HTTP declaraba `304`
  entre los estados exitosos sin cuerpo, pero el flujo evalúa `!response.ok` antes de
  consultarlos, así que `304` —que no es 2xx— jamás llegaba allí. La entrada era
  inalcanzable y describía un comportamiento inexistente. `304` no figura en
  [api-contracts.md](../architecture/api-contracts.md) §8 y el proyecto no hace peticiones
  condicionales: se retiró del conjunto y quedó **prueba de regresión permanente**.
- **`Task/011` cierra la autenticación administrativa del backend:** `personal-blog-backend`
  tiene los tres endpoints del contrato, **Argon2id**, sesión opaca *server-side* con cookie
  `HttpOnly`, bloqueo de cuenta seguro ante concurrencia, límite de tasa compartido en
  PostgreSQL y auditoría sin secretos, más la protección reutilizable `AdministradorRequerido`
  que consumirá `Task/012`. Está **`Aprobada`** desde el 2026-09-01, lo que lleva el avance a
  **11 de 41 (27 %)** y la ETAPA 03 a **4 de 5 (80 %)**. Resuelve **D-15**, **D-02** y **D-09**.
  Su alcance **no** incluye CRUD administrativo, panel React, CORS efectivo ni dominio real.
- **La funcionalidad del blog ya no está sin empezar.** *(Corregido al aprobar `Task/011`:
  esta nota afirmaba «no hay modelo de datos, ni endpoints de contenido, ni autenticación»,
  lo que dejó de ser cierto con `Task/008`, `Task/009` y `Task/011`.)* Existen el modelo de
  datos (`Task/008`), los diez endpoints públicos (`Task/009`), el almacenamiento de objetos
  (`Task/010`) y la autenticación administrativa (`Task/011`). **Sigue faltando** el CRUD
  administrativo, que es `Task/012`.
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
- **`Task/006.2` tampoco crea nada.** Es documental: **0 recursos AWS, 0 recursos Cloudflare,
  0 cuentas de Grafana Cloud, 0 VPS, 0 buckets, 0 parámetros SSM, 0 roles IAM, 0 Terraform**.
  **No se instaló Grafana Alloy, ni Ansible, ni SOPS, ni age**, y **no se generó ninguna
  clave de cifrado**. La imagen `images/Infraestructura.png` **no se modificó**: sigue siendo
  la que el usuario publicó en el commit `d08fe27`.
- **`ADR-008` está `Aceptada`** desde el 2026-08-23, al aprobarse `Task/006.2`. Es el
  **octavo ADR** del proyecto. Registra la observabilidad de producción —**CloudWatch
  mínimo** + **Grafana Cloud** con **Grafana Alloy** en el VPS— y modifica **una sola fila**
  de `ADR-003`, la de «Logs y métricas»; el resto de ADR-003 permanece **íntegro y
  vigente**, incluida la exclusión de **ECR** y el empaquetado de Lambda por **ZIP**.
- **Aceptar ADR-008 no autoriza a implementarlo.** No existe cuenta de Grafana Cloud, ni
  Alloy instalado, ni integración con CloudWatch: cada pieza es de su tarea propietaria
  —`Task/029`, `Task/031`, `Task/040`, `Task/041`— y exige autorización explícita del
  usuario.
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
- **Decisiones diferidas: 13 abiertas** desde `Task/005.5`, que añadió **D-15** —topología
  lógica de dominios, `Task/011`— y **D-16** —identidad del VPS hacia AWS, `Task/029`—.
  Resueltas: **D-05** (2026-07-29, Traefik v3),
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
- **`Task/006` está `Aprobada`** desde el 2026-08-18; `Task/007` sigue **Pendiente** y
  **no se ha iniciado**. `Task/005.1`, `Task/005.2`, `Task/005.3`,
  **`Task/005.4`** y **`Task/005.5`** están aprobadas, fusionadas y normalizadas.
  **`Task/005.6`** y **`Task/005.7`** están **aprobadas**. Las ramas `Task/006` de frontend
  e infra nacieron **desde `main`**, con `HEAD == main` verificado inmediatamente.
- **Cierre de fundaciones (`Task/005.6`, 2026-08-16, aprobada).** Se
  conciliaron **dos mega auditorías independientes** y se reprodujo cada hallazgo antes de
  decidir. Corregido: la política de finales de línea de los tres repositorios
  (`.gitattributes`, causa raíz `core.autocrlf=true` de nivel *system*); el aislamiento de
  la suite frente al `.env` del desarrollador; una **base de datos de pruebas dedicada** con
  guarda *fail-closed* de dos barreras; la distinción **skip / fail** de la integración; la
  verificación **semántica** de `commit` y `rollback`; el test de migraciones que habría
  caducado en `Task/008`; la cobertura de una configuración `production` **válida**; y el
  estado documental posterior a `Task/005.5`. **Ningún defecto arquitectónico**, **0
  funcionalidad nueva** y **`app/` sin cambios**. Deuda diferida con propietario:
  **R-36**.
- **Regla de gobierno nueva ([WORKFLOW §6.1](WORKFLOW.md), `Task/005.6`).** Los documentos
  versionados registran **estado duradero**; el estado transitorio de Git y GitHub —PR
  abierto o fusionado, rama remota, sincronización actual— se **consulta en vivo** y solo se
  archiva como **observación fechada**. Corrige la causa estructural por la que `STATUS.md`
  quedaba obsoleto tras cada fusión y evita tener que crear una tarea de mantenimiento
  (`006.1`, `007.1`, …) después de cada PR. **El invariante de ramas y el flujo de
  aprobación manual no cambian.**
- **Alineación posterior a la auditoría (`Task/005.5`, 2026-08-16, aprobada).**
  Se reprodujeron los hallazgos de dos auditorías independientes contra el repositorio, y se
  corrigieron los que se sostuvieron: la regla de ramas en backend y frontend, el estado
  documental de ADR-006 y ADR-007, el conteo de decisiones, la dependencia de `Task/025`
  respecto a `Task/024`, los *gates* de `Task/029` que exigían recursos futuros, el
  Terraform prometido en `Task/021`, la topología de dominios diferida hasta `Task/035`, y
  los propietarios ausentes de `S3Storage`, backup, identidad del VPS, certificado TLS,
  observabilidad del VPS, migraciones productivas, medios públicos y credenciales CI
  multi-provider. **No se creó ningún ADR nuevo, no se renumeró ninguna tarea y la
  arquitectura no cambió.** Decisiones nuevas: **D-15** y **D-16**, ambas **abiertas**.
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
[Reporte TASK-005.4](../task-reports/TASK-005.4-report.md) ·
[TASK-005.5](../tasks/TASK-005.5-align-planning-after-audit.md) ·
[Reporte TASK-005.5](../task-reports/TASK-005.5-report.md)

Estrategia de infraestructura local aprobada en `Task/005.2`:
[aws-local-parity](../architecture/aws-local-parity.md) (**Vigente**) ·
[ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) (**Aceptada**)

Capa de datos de producción aprobada en `Task/005.3`:
[production-postgresql-vps](../architecture/production-postgresql-vps.md) (**Vigente**) ·
[ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) (**Aceptada**)

Documentos de producto y arquitectura producidos por `Task/002`:
[MVP_SCOPE](../product/MVP_SCOPE.md) · [USER_FLOWS](../product/USER_FLOWS.md) ·
[CONTENT_MODEL](../product/CONTENT_MODEL.md) ·
[software-architecture](../architecture/software-architecture.md) ·
[api-contracts](../architecture/api-contracts.md) ·
[non-functional-requirements](../architecture/non-functional-requirements.md) ·
[security-boundaries](../architecture/security-boundaries.md) ·
[open-decisions](../architecture/open-decisions.md)
