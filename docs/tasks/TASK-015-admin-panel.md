# TASK-015 — Panel Administrativo

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/015-Panel-Administrativo` |
| **Nombre** | Panel Administrativo |
| **Tipo** | Tarea oficial del roadmap. Cuenta dentro de las 41 |
| **Etapa** | ETAPA 04 — Experiencia del Usuario |
| **Estado** | **Aprobada** el 2026-09-05 por jeffersondavila |
| **Bloqueo histórico** | **B-015-1**, declarado el 2026-09-05 y **RESUELTO** ese mismo día por `Task/012.1-Exponer-Auditoria-Para-Dashboard` (**Aprobada**). Historia y resolución en §2.1 |
| **Repositorios involucrados** | `personal-blog-frontend` (funcional) · `personal-blog-infra` (gobierno documental) |
| **Repositorio NO modificado** | `personal-blog-backend` — **sin rama y sin cambios** |
| **Dependencias** | `Task/013` (**Aprobada** ✔) · `Task/014` (**Aprobada** ✔) · contratos de `Task/010`, `Task/011`, `Task/012` y `Task/012.1` (**Aprobados** ✔) |
| **Rama** | `Task/015-Panel-Administrativo` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base (frontend)** | `ca29657bbe4807aa8e25affdbc815d4fd7a4c598` |
| **SHA base (infra)** | `5a8f4c8e0fe6938c9b31905b7540abf1a0d1eb51` — actualizado por avance rápido a `189ceb86…` el 2026-09-05, el `main` que incorpora `Task/012.1`. **Observado al actualizar la base el 2026-09-05: 0 commits propios** |
| **Fecha de inicio** | 2026-09-05 |
| **Última actualización** | 2026-09-05 (aprobación del usuario; ver [reporte](../task-reports/TASK-015-report.md)) |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

Preflight ejecutado el 2026-09-05 en los **tres** repositorios, tras `git fetch --prune origin`:

| Repositorio | Rama activa | `main == origin/main` | `dev == origin/dev` | Árbol limpio | `git diff main dev` | `dev..main` | Ramas Task locales / remotas |
| --- | --- | --- | --- | :---: | :---: | :---: | :---: |
| `personal-blog-frontend` | `main` | ✔ `ca29657b` | ✔ `dbad882e` | ✔ | vacío | `0` | ninguna / ninguna |
| `personal-blog-infra` | `main` | ✔ `5a8f4c8e` | ✔ `64ab5eab` | ✔ | vacío | `0` | ninguna / ninguna |
| `personal-blog-backend` | `main` | ✔ `ce166fb7` | ✔ `da1bec59` | ✔ | vacío | `0` | ninguna / ninguna |

Creación de la rama, con validación inmediata (2026-09-05):

| # | Comprobación | frontend | infra |
| --- | --- | --- | --- |
| 1 | `main == origin/main` antes de crear | ✔ `ca29657b` | ✔ `5a8f4c8e` |
| 2 | `git status --porcelain` vacío antes de crear | ✔ | ✔ |
| 3 | Rama creada **desde `main`** con `git switch -c` | ✔ | ✔ |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo después | ✔ idénticos | ✔ idénticos |
| 5 | `git rev-list --count main..HEAD` | ✔ `0` | ✔ `0` |

`personal-blog-backend` **no recibe rama**: la tarea no lo modifica. Sus esquemas y routers
administrativos (`app/modules/*/presentation/schemas_admin.py`, `router_admin.py`,
`app/modules/authentication/presentation/`, `app/api/admin.py`) se leyeron para reconstruir
el contrato campo a campo; no se toca ni un archivo.

---

## 1. Objetivo

Entregar el **panel administrativo del MVP**: la interfaz autenticada con la que el
administrador inicia sesión, consulta un dashboard, crea, edita, publica, despublica y
archiva los cuatro tipos de contenido, edita el perfil, gestiona etiquetas y administra la
biblioteca de medios, sobre el sistema de diseño de `Task/013`, el pipeline de Markdown de
`Task/014` y los **27 patrones de ruta / 39 operaciones HTTP** que `Task/011`, `Task/012` y
`Task/012.1` dejaron cerrados (inventario verificado en §6.C.0).

Con ella la ETAPA 04 puede satisfacer sus criterios de salida pendientes: contenido
gestionable desde el panel, carga de imágenes, vista previa antes de publicar y panel
inaccesible sin sesión válida.

> **Sin bloqueos.** El dashboard mínimo de `MVP_SCOPE.md` §3.3 es construible por completo:
> `Task/012.1` entregó la operación que faltaba. Historia en §2.1.

## 2. Contexto

Es la **tercera y última** tarea de la ETAPA 04. Todo lo que consume ya está aprobado:

| Insumo | Tarea | Qué aporta |
| --- | --- | --- |
| Cinco primitivas y 50 tokens | `Task/013` | `Container`, `Stack`, `Button`, `Card`, `Badge`; foco, contraste y señal no cromática |
| Doce superficies públicas, cinco compartidos y el pipeline Markdown | `Task/014` | `Pagination`, `ExternalLink`, `LoadingState`, `EmptyState`, `ErrorState`, `MediaImage`, `MarkdownContent`, `useAsyncResource`, `useDocumentTitle`, `HttpClientContext` |
| Almacenamiento de objetos y `MediaAsset` | `Task/010` | Límites (5 MiB; JPEG/PNG/WebP), `access_url` temporal, `alt_text` opcional al cargar (**D-010-N**) |
| Autenticación administrativa | `Task/011` | Sesión opaca *server-side* en cookie `HttpOnly`, validación de `Origin`, límite de tasa |
| API administrativa | `Task/012` | 23 patrones de ruta (35 operaciones), transiciones como subrecursos, validación de publicación, `alt_text` al usar |

Materia que las fuentes canónicas dejan **explícitamente** a esta tarea:

| Materia abierta | Fuente que la asigna |
| --- | --- |
| **Editor Markdown concreto (D-04)** | `open-decisions.md` D-04 · `MVP_SCOPE.md` §8 · `software-architecture.md` §7 |
| **A-03** labels de formulario asociadas | `non-functional-requirements.md` §3 |
| **A-08** errores de formulario anunciados de forma accesible | `non-functional-requirements.md` §3 |
| **S-03** sanitización **también en la vista previa** | `non-functional-requirements.md` §1 · ADR-005 · `USER_FLOWS.md` B.6 |
| **P-05** el código del panel no se descarga en las páginas públicas | `non-functional-requirements.md` §2 · `software-architecture.md` §4.4 |
| Paso de **confirmación** al borrar una etiqueta en uso | `api-contracts.md` §14 (**D-012-T**) |
| Selector de proveedor de vídeo de la lista cerrada de `Task/014` | `api-contracts.md` §14.9 · deuda 1 de `Task/014` |
| Rutas del panel | Ninguna fuente las fija: **las confirma esta tarea** (**D-015-A**) |

---

## 2.1 **B-015-1** — bloqueo declarado y **RESUELTO** el 2026-09-05

> **Cerrado.** Se declaró al reconstruir el alcance del panel y lo resolvió
> `Task/012.1-Exponer-Auditoria-Para-Dashboard`, **Aprobada** el 2026-09-05. Esta sección se
> conserva como registro de por qué existió y cómo se cerró; **no describe un bloqueo
> vigente**.

### Lo que la fuente exige

`MVP_SCOPE.md` §3.3, íntegro:

> ### 3.3 Dashboard básico
>
> Alcance mínimo: conteo de contenido por tipo y estado, últimos elementos modificados y
> **últimos eventos de auditoría**. Sin gráficas ni analítica.

Es **alcance mínimo**, no una lista de deseos: las tres partes son obligatorias.

### La prueba de que la tercera parte no era construible entonces

| # | Hecho comprobado el 2026-09-05 sobre `personal-blog-backend` en `main` (`ce166fb7`) | Cómo se comprobó |
| --- | --- | --- |
| 1 | **No existe ningún router de auditoría.** Los routers montados son quince y ninguno pertenece al módulo `audit` | `find app -name 'router*.py'`; `grep -i audit` sobre toda declaración de `APIRouter` — sin resultados |
| 2 | **El módulo `audit` no tiene capa `presentation` ni `application`.** Solo `domain/` e `infrastructure/` | `ls app/modules/audit/` → `domain`, `infrastructure` |
| 3 | **Su puerto de dominio es de solo escritura.** `RegistroDeAuditoria` declara **un** método, `registrar`, y su docstring dice *«Solo **crea**»* | `app/modules/audit/domain/puertos.py` |
| 4 | **No existe ninguna consulta.** El módulo no tiene `queries.py`, al contrario que los siete módulos que sí se leen | `find app/modules/audit -name '*.py'` |
| 5 | **`app/api/admin.py` monta siete routers** —perfil, artículos, reviews, vídeos, proyectos, etiquetas y medios—. La auditoría no está | `routers_administrativos()` |
| 6 | Las **38 operaciones HTTP** administrativas de entonces (§6.C.0) **no incluían ninguna** sobre `audit_events` | Recuento programático de los decoradores de los ocho routers |

El frontend **no puede** alcanzar `audit_events` por ninguna otra vía:
`software-architecture.md` §5 es explícito —*«El frontend **no accede jamás** a PostgreSQL,
MinIO ni S3 directamente»*—, y `PROJECT_INSTRUCTIONS.md` §18 prohíbe inventar contratos.

### Por qué no es un simple descuido de `Task/012`

La capacidad de **lectura** ya es canónica; lo que falta es su exposición HTTP:

- `CONTENT_MODEL.md` §3.9, regla de `AuditEvent`: *«solo **se crea y se lee** — nunca se
  edita ni se elimina desde la aplicación»*. La lectura está prevista por el modelo de
  producto.
- `data-model.md` §5 justifica el índice `ix_audit_events_occurred_at` con el propósito
  *«Listado cronológico del historial»*. `Task/008` **ya creó el índice que esa consulta
  necesita**: no hace falta migración.
- `data-model.md` §6, invariantes 16 y 16b, protegen `UPDATE` y `DELETE`. Un `GET` no las
  toca.
- `CONTENT_MODEL.md` §3.9: *«Las **lecturas no se auditan**»*. Exponer la lectura no
  realimenta el historial.

Es decir: el modelo de datos, el modelo de producto y el índice físico anticipan la
lectura. Lo único que falta es la operación HTTP, y **crearla es modificar el backend**.

### Por qué se retiró **D-015-I** (entregar dos de tres y diferir a `Task/017`)

`ROADMAP.md` define `Task/017-Observabilidad-Local` con **repositorios `backend, infra`** y
**dependencias `014, 015`**. De ahí se siguen tres objeciones, cualquiera de las cuales
basta:

1. **No incluye `frontend`.** Trasladarle una parte de la interfaz de React exigiría
   ampliar su alcance y sus repositorios — es decir, decidir por una tarea ajena.
2. **Depende de `Task/015`.** Diferir a `Task/017` un entregable de `Task/015` crea una
   dependencia circular: `015` no estaría completa hasta `017`, y `017` no empieza hasta
   `015`.
3. **Dejaría la ETAPA 04 cerrada con un criterio de salida incompleto**, sin que ningún
   documento registre por qué.

**Trasladar en silencio una parte de la UI de `Task/015` a `Task/017` no es una
resolución.** `D-015-I` queda **retirada**; el hueco se declara como bloqueo hasta que el
usuario decida la resolución.

### Resolución aplicada — `Task/012.1`

Se evaluaron dos alternativas. Se eligió la **A** y el usuario la aprobó.

| Alternativa | Veredicto |
| --- | --- |
| **A. `Task/012.1-Exponer-Auditoria-Para-Dashboard`**, mantenimiento fuera de las 41 | **ELEGIDA Y EJECUTADA.** El dueño del contrato administrativo es `Task/012` —`api-contracts.md` §14 se titula *«API administrativa, **cerrada en `Task/012`**»*—, así que ampliarlo es enmendar **su** entregable. Respeta *«Repositorio de toda la etapa: `personal-blog-frontend`»* de `STAGE-04`, aísla el contrato backend de la UI y no altera los 41 identificadores ni el avance |
| **B. Ampliar `Task/015` a backend** | **DESCARTADA.** Contradiría la declaración de `STAGE-04` y mezclaría dos Definitions of Done —frontend y backend funcional con TDD estricto— en una tarea que ya son 18 superficies y 9 formularios |

### Qué entregó `Task/012.1` — **Aprobada** el 2026-09-05

Contrato completo en [`api-contracts.md`](../architecture/api-contracts.md) §15. Lo que
`Task/015` puede consumir:

| Aspecto | Valor vigente |
| --- | --- |
| Operación | `GET /api/v1/admin/audit-events` — **solo lectura**, sesión obligatoria |
| Parámetros | **Solo** `page` y `page_size`; 12 por defecto, máximo 50 con recorte. Sin filtros |
| Respuesta | `Pagina[EventoDeAuditoria]`, la envoltura única del proyecto |
| DTO | `id`, `occurred_at`, `action`, `entity_type`, `entity_id` |
| **No disponibles** | `actor_id`, `event_metadata`, `request_id`, `ip_address` |
| Orden | `occurred_at` **DESC**, desempate `id` **ASC** |
| Errores | `401 unauthenticated` · `422 validation_error`. **No** `403`, `404` ni `409` |

**Sin migración**, sin índice nuevo, y la inmutabilidad de `AuditEvent` intacta: leer el
historial no genera un evento.

### Efecto sobre `Task/015`

El bloqueo queda **cerrado**. El dashboard mínimo de `MVP_SCOPE.md` §3.3 se entrega **completo
dentro de `Task/015`**, con sus tres piezas (§6.J). El resto del diseño de esta ficha no
cambió por el bloqueo y sigue vigente tal cual.

`Task/017-Observabilidad-Local` conserva su alcance —`backend, infra`, observabilidad,
correlation ID y auditoría operativa— y **no** es responsable de ninguna interfaz React.

---

## 3. Dentro del alcance

- [x] Árbol de rutas `/admin/*` confirmado (**D-015-A**), montado **antes** del comodín
      público y **cargado en diferido** (P-05).
- [x] `AdminLayout` propio, separado de `SiteLayout`, con navegación, `main` y `h1` por página.
- [x] Sesión administrativa: arranque por `GET /admin/auth/me`, login, logout, expiración,
      protección de rutas y preservación del destino solicitado.
- [x] Página de acceso con formulario accesible y errores genéricos (B.1).
- [x] Dashboard básico **completo** de `MVP_SCOPE.md` §3.3 — conteo por tipo y estado,
      últimos elementos modificados y **últimos eventos de auditoría**, más accesos rápidos.
      Las tres piezas son construibles: la tercera consume
      `GET /api/v1/admin/audit-events` (`Task/012.1`, **Aprobada**).
- [x] Listados administrativos de los cuatro tipos: los tres estados, filtro `status`,
      paginación en la URL, estados de carga, vacío y error.
- [x] Creación y edición de artículos, reviews, vídeos y proyectos (`POST` y `PUT`).
- [x] Editor Markdown y **vista previa** con `MarkdownContent` (artículos, reviews,
      proyectos y biografía del perfil).
- [x] Acciones de publicación: `publish`, `unpublish` (solo artículos y reviews) y `archive`,
      con mapeo de sus `409`.
- [x] Biblioteca de medios: carga, listado, selección como portada/miniatura/foto y borrado
      con confirmación y con lectura de `details.usos`.
- [x] Escritura de `alt_text` **en el primer uso** de la imagen, sin provocar
      `alt_text_conflict`.
- [x] Gestión de etiquetas: listado, creación, renombrado y borrado con **confirmación**
      explícita (**D-012-T**).
- [x] Edición del perfil singleton, con enlaces sociales ordenados por índice.
- [x] Adaptadores HTTP administrativos en `src/services/admin/`, con sus tipos derivados de
      los DTO reales.
- [x] Dos modificaciones mínimas y justificadas del cliente HTTP (**D-015-C** y **D-015-D**).
- [x] Dos componentes compartidos nuevos: `FormField` y `FormFeedback` (**A-03**, **A-08**).
- [x] Responsive intrínseco implementado. La observación visual en navegador a
      320, 390, 768 y 1280 px sigue pendiente y se conserva como limitación aceptada.
- [x] Suite en verde: las **440** pruebas actuales más las nuevas.
- [x] Documentación: ficha, reporte, `STATUS`, `ROADMAP`, `STAGE-04`, `open-decisions` (D-04).

## 4. Fuera del alcance

| Fuera | Propietario |
| --- | --- |
| Auditoría formal de accesibilidad y afirmación de WCAG 2.1 AA | `Task/016` |
| Metadatos SEO, Open Graph, canonical, sitemap y `robots.txt` (incluido el `noindex` del panel, **E-06**) | `Task/016` |
| Optimización de rendimiento y medición de umbrales (P-01, P-03, P-04) | `Task/016` |
| Código HTTP real `404` de la SPA | `Task/016`, `Task/034` |
| **Exponer la lectura de `AuditEvent` por HTTP** — es backend, y esta tarea no toca backend | **Entregado por `Task/012.1`**, mantenimiento fuera de las 41, **Aprobada** el 2026-09-05. `Task/015` solo lo **consume** |
| CORS efectivo y cabeceras de seguridad | `Task/018` |
| Restringir `provider` en el **backend** a la lista cerrada de `Task/014` | Backend: sin propietario (candidata `Task/018`) |
| Endurecimiento de la configuración de sanitización | `Task/018` |
| Semilla local del administrador y del perfil | `Task/022` |
| Insertar imágenes **dentro** del cuerpo Markdown (exige URL estable, **D-08**) | `Task/030` |
| Restaurar desde `archived`; `DELETE` de contenido | Fuera del MVP (`MVP_SCOPE.md` §3.2, **D-012-D**) |
| Registro público, roles, RBAC, cambio o recuperación de contraseña | **Ninguno**: fuera del MVP |
| Cualquier cambio funcional en `personal-blog-backend` | — |
| Cualquier recurso AWS, Terraform o Cloudflare | ETAPAS 08–10 |

---

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Rutas del panel | frontend | `src/lib/rutasAdmin.ts` |
| Sesión administrativa | frontend | `src/app/adminSessionContext.ts`, `src/app/AdminSessionProvider.tsx` |
| Guarda de rutas | frontend | `src/app/RutaProtegida.tsx` |
| Layout del panel | frontend | `src/app/AdminLayout.tsx` (+ `.module.css`) |
| Adaptadores administrativos | frontend | `src/services/admin/` |
| Formulario accesible compartido | frontend | `src/components/FormField/`, `src/components/FormFeedback/` |
| Editor y vista previa | frontend | `src/features/markdown/MarkdownEditor.tsx` |
| Medios | frontend | `src/features/media/` |
| Piezas comunes de contenido | frontend | `src/features/admin-content/` |
| Páginas del panel | frontend | `src/pages/admin/` |
| Ficha y reporte | infra | `docs/tasks/`, `docs/task-reports/` |

---

## 6. Matriz funcional — decision gate

### 6.A Fuentes canónicas y la regla concreta que imponen

| Documento | Regla que impone a `Task/015` |
| --- | --- |
| `CLAUDE.md` · `PROJECT_INSTRUCTIONS.md` | Rama desde `main`; sin commit, push ni PR antes de `approved:`; documentación en español |
| `WORKFLOW.md` §2.1, §6.1 | Base `main`; los documentos no persisten estado vivo de Git (criterio 12) |
| `DEFINITION_OF_DONE.md` §1, §3 | Criterios 1–12; frontend: lint, typecheck, tests, build, sin errores de consola |
| `STATUS.md` · `ROADMAP.md` | Tras la aprobación: **15/41 — 37 %**; ETAPA 04 **3/3 — 100 %** |
| `STAGE-04-user-experience.md` | Los cuatro criterios de salida pendientes son de esta tarea; auditoría y SEO son de la Etapa 05 |
| `MVP_SCOPE.md` §3.1–§3.3, §8 | Capacidades exactas del panel; tres estados; dashboard sin gráficas; **D-04 se resuelve aquí** |
| `USER_FLOWS.md` B.1–B.12 | Los doce flujos administrativos, con sus reglas y su matriz flujo → recurso |
| `CONTENT_MODEL.md` §2, §3.3–§3.5, §3.9 | *Fallbacks* SEO; campos por tipo; `Profile` singleton siempre visible |
| `api-contracts.md` §5–§8, §12, §13, §14 | Envoltura de página, filtros, errores, `MedioPublico`, auth y los 23 patrones de ruta administrativos |
| `software-architecture.md` §4.3, §4.4, §5 | `pages → features → entities → components`; solo `services` habla HTTP; el panel no se descarga en el sitio público; el frontend **no autoriza** |
| `security-boundaries.md` §11, §12 | Sesión opaca, CSRF en dos capas, `login` único endpoint público, sin enumeración |
| `non-functional-requirements.md` | **A-03**, **A-08**, **S-03**, **P-05** son de esta tarea; A-01/A-02 continúan; A-04/A-05/A-06/A-07 se preservan |
| `open-decisions.md` D-04, D-08 | El editor concreto se decide aquí; la URL estable de medios **no** |
| ADR-004 | Sin capas ni abstracciones vacías |
| ADR-005 | Markdown fuente en el backend; render sanitizado en el frontend; **la vista previa usa el mismo pipeline** |
| Fichas y reportes de `Task/010`–`Task/014` | Contratos vigentes de medios, auth, API administrativa, diseño y sitio público |

### 6.B Rutas del panel — **D-015-A** (Vigente — aprobada el 2026-09-05)

Ninguna fuente canónica fija las rutas del panel: `MVP_SCOPE.md` §2.1 solo enumera las
públicas y `USER_FLOWS.md` B.1 dice *«abre la ruta de acceso al panel»* sin nombrarla. Se
confirman aquí, en español como las públicas (`Task/014`, **D-014-A**), bajo el prefijo
`/admin`, que es como `E-06` nombra al panel administrativo.

| # | Ruta | Página | Auth | Endpoints | Objetivo |
| --- | --- | --- | :---: | --- | --- |
| 1 | `/admin/acceso` | `LoginPage` | **No** | `POST /admin/auth/login` | B.1 iniciar sesión |
| 2 | `/admin` | `DashboardPage` | Sí | `GET` de los 4 listados | B.1 §4, MVP_SCOPE §3.3 |
| 3 | `/admin/articulos` | `PostsAdminPage` | Sí | `GET /admin/posts` | Listado con los 3 estados |
| 4 | `/admin/articulos/nuevo` | `PostFormPage` (crear) | Sí | `POST /admin/posts` | B.2 |
| 5 | `/admin/articulos/:id` | `PostFormPage` (editar) | Sí | `GET`/`PUT`/`{publish,unpublish,archive}` | B.3, B.6–B.9 |
| 6–8 | `/admin/reviews`, `/nuevo`, `/:id` | `BookReviewsAdminPage`, `BookReviewFormPage` | Sí | `/admin/book-reviews` | Igual, **con `unpublish`** |
| 9–11 | `/admin/videos`, `/nuevo`, `/:id` | `VideosAdminPage`, `VideoFormPage` | Sí | `/admin/videos` | Igual, **sin `unpublish`** y **sin Markdown** |
| 12–14 | `/admin/proyectos`, `/nuevo`, `/:id` | `ProjectsAdminPage`, `ProjectFormPage` | Sí | `/admin/projects` | Igual, **sin `unpublish`** |
| 15 | `/admin/etiquetas` | `TagsAdminPage` | Sí | `GET`/`POST`/`PUT`/`DELETE /admin/tags` | B.11 |
| 16 | `/admin/medios` | `MediaAdminPage` | Sí | `GET`/`POST`/`DELETE /admin/media` | B.4, B.5 |
| 17 | `/admin/perfil` | `ProfileAdminPage` | Sí | `GET`/`PUT /admin/profile` | B.10 |
| 18 | `/admin/*` | `AdminNotFoundPage` | Sí | — | Ruta desconocida dentro del panel |

**No existe ruta de detalle administrativo separada de la edición.** La edición *es* el
detalle: `GET /admin/{recurso}/{id}` alimenta el formulario. Crear una vista de solo lectura
duplicaría la superficie sin que ninguna fuente la pida.

**No existe `/admin/articulos/:id/preview`.** La vista previa es un estado del editor, no una
ruta: `USER_FLOWS.md` B.6 dice que *«no publica ni expone»* y su matriz la marca **«solo
frontend, sin endpoint propio»**.

**Convivencia con las doce superficies públicas** (`Task/014`, **D-014-A**):

1. El subárbol `/admin` se inserta en `src/app/routes.tsx` **antes** del comodín `*`, que
   sigue siendo la última entrada de la tabla.
2. El subárbol se monta con **carga diferida** (`lazy`), de modo que ninguna página pública
   descarga código del panel — requisito **P-05** y `software-architecture.md` §4.4. La
   ausencia se comprueba sobre los *chunks* de `dist/`.
3. `SiteLayout` **no se toca**. `AdminLayout` es otra ruta de layout, hermana, no anidada.
4. El proveedor de sesión envuelve **solo** el subárbol `/admin`, no el router entero: así un
   visitante anónimo **nunca** dispara `GET /admin/auth/me` y la semántica del sitio público
   no cambia por existir el panel. Es una desviación deliberada del comentario que
   `Task/014` dejó en `App.tsx`, y ese comentario se actualiza.
5. `/__design-system` sigue existiendo **solo** en DEV, con su guarda sobre `dist/` intacta.

### 6.C Contratos administrativos consumidos

Reconstruidos de `api-contracts.md` §13 y §14 y verificados campo a campo contra
`app/modules/*/presentation/schemas_admin.py` y `router_admin.py` del backend en `main`
(`ce166fb7`). **Postura común de todo `/api/v1/admin/*`** (`app/api/admin.py`): sesión
obligatoria, validación de `Origin` en los métodos que cambian estado, `Cache-Control:
no-store` y **rechazo con `422` de cualquier parámetro de consulta desconocido**.

#### 6.C.0 Convención de rutas y terminología inequívoca

**Dos espacios de nombres distintos que empiezan igual.** La ficha usa `/admin/…` para dos
cosas que no deben confundirse:

| Forma | Qué es | Dónde se define | Ejemplos |
| --- | --- | --- | --- |
| `/admin/<algo-en-español>` | **Ruta del panel** en el navegador | §6.B (**D-015-A**) | `/admin/acceso`, `/admin/articulos`, `/admin/medios` |
| `/admin/<recurso-en-inglés>` | **Abreviatura de un path HTTP**; su forma completa es siempre `/api/v1/admin/<recurso>` | `api-contracts.md` §14 | `/admin/posts` ≡ `/api/v1/admin/posts` |

La abreviatura de la segunda fila es **deliberada** y copia la del contrato:
`api-contracts.md` §14.1 declara *«Todas bajo `/api/v1/admin`»* una vez y a partir de ahí
escribe `/admin/posts`. Aquí se hace igual, y **queda dicho aquí** para que no convivan dos
convenciones sin explicación. Los paths canónicos de los recursos que el panel consume son
`posts`, `book-reviews`, `videos`, `projects`, `tags`, `media`, `profile`, `auth/*` y
`audit-events`; no se inventa ninguno.

Un **patrón de ruta** es un *path* del contrato (`/admin/posts/{post_id}`). Una **operación
HTTP** es una combinación **método + patrón** (`GET /admin/posts/{post_id}`). Un patrón
puede soportar varias operaciones, así que las dos cifras **no** coinciden y no deben
usarse como sinónimos.

Recuento programático sobre los ocho routers del backend en `main` (`ce166fb7`), realizado
el 2026-09-05:

| Origen | Recurso | Patrones | Operaciones | Métodos por patrón |
| --- | --- | ---: | ---: | --- |
| `Task/011` | `/admin/auth/login` · `/logout` · `/me` | 3 | 3 | `POST` · `POST` · `GET` |
| `Task/012` | `/admin/profile` | 1 | 2 | `GET`, `PUT` |
| `Task/012` | `/admin/posts` (+`/{id}`, `/publish`, `/unpublish`, `/archive`) | 5 | 7 | `GET`,`POST` · `GET`,`PUT` · `POST` ×3 |
| `Task/012` | `/admin/book-reviews` (ídem) | 5 | 7 | ídem |
| `Task/012` | `/admin/videos` (**sin `unpublish`**) | 4 | 6 | `GET`,`POST` · `GET`,`PUT` · `POST` ×2 |
| `Task/012` | `/admin/projects` (**sin `unpublish`**) | 4 | 6 | ídem |
| `Task/012` | `/admin/tags` (+`/{tag_id}`) | 2 | 4 | `GET`,`POST` · `PUT`,`DELETE` |
| `Task/012` | `/admin/media` (+`/{media_id}`) | 2 | 3 | `GET`,`POST` · `DELETE` |
| **Subtotal `Task/011`** | | **3** | **3** | |
| **Subtotal `Task/012`** | | **23** | **35** | |
| `Task/012.1` | `/admin/audit-events` | 1 | 1 | `GET` |
| **TOTAL consumible por el panel** | | **27** | **39** | |

El **23** de `api-contracts.md` §14.1 —*«Las 23 rutas»*— son **patrones**, y la cifra es
correcta leída así. Las 35 operaciones de `Task/012` no aparecen en ese documento porque
allí se enumeran por recurso, no por combinación método+ruta.

La **39.ª operación**, `GET /api/v1/admin/audit-events`, la añadió `Task/012.1` y es la que
el dashboard usa para su tercera pieza (§6.J).

#### Autenticación (§13)

| UI | Método | Endpoint | Request | Response | Errores que la UI distingue |
| --- | --- | --- | --- | --- | --- |
| Iniciar sesión | `POST` | `/api/v1/admin/auth/login` | `{email, password}` | `200 {id, email, display_name}` | `401 invalid_credentials` · `403 forbidden` · `422 validation_error` · `429 too_many_requests` (+`Retry-After`) |
| Sesión actual | `GET` | `/api/v1/admin/auth/me` | — | `200 {id, email, display_name}` | `401 unauthenticated` |
| Cerrar sesión | `POST` | `/api/v1/admin/auth/logout` | — | `204` sin cuerpo | `401 unauthenticated` · `403 forbidden` |

#### Perfil

| UI | Método | Endpoint | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- |
| Cargar perfil | `GET` | `/admin/profile` | — | `200 PerfilAdministrativo` | `401` · `404 resource_not_found` |
| Guardar perfil | `PUT` | `/admin/profile` | `PerfilParaGuardar` | `200 PerfilAdministrativo` | `401` · `403` · `404` · `409 alt_text_conflict` · `422 media_without_alt_text`, `unknown_reference`, `validation_error` |

`PerfilParaGuardar`: `full_name`\* (1–120), `headline` (≤200), `biography` (Markdown, por
defecto `""`), `contact_email` (≤254), `photo_id` (UUID\|null), `photo_alt_text` (≤255, solo
junto a `photo_id`), `seo_title` (≤70), `seo_description` (≤160), `social_links[]` de
`{label (1–60), url (1–2048)}`, máximo 20. **Sin `display_order`**: el orden es el índice
(**D-012-Q**). `PerfilAdministrativo` añade `id`, `photo` (`MedioAdministrativo`),
`created_at`, `updated_at`.

#### Contenido — los cuatro tipos

| UI | Método | Endpoint | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- |
| Listar | `GET` | `/admin/{recurso}?page&page_size&status` | — | `200 Pagina[<Tipo>Administrativo]` | `401` · `422` |
| Crear | `POST` | `/admin/{recurso}` | `<Tipo>ParaGuardar` | `201 <Tipo>Administrativo` | `401` · `403` · `409 slug_already_exists` · `422` |
| Consultar | `GET` | `/admin/{recurso}/{id}` | — | `200 <Tipo>Administrativo` | `401` · `404` |
| Editar | `PUT` | `/admin/{recurso}/{id}` | `<Tipo>ParaGuardar` | `200 <Tipo>Administrativo` | `401` · `403` · `404` · `409 slug_already_exists`, `slug_is_immutable`, `alt_text_conflict` · `422` |
| Publicar | `POST` | `/admin/{recurso}/{id}/publish` | — | `200 <Tipo>Administrativo` | `401` · `403` · `404` · `409 cannot_publish_incomplete_draft`, `invalid_{tipo}_state` |
| Despublicar | `POST` | `/admin/{posts,book-reviews}/{id}/unpublish` | — | `200` | `401` · `403` · `404` · `409 invalid_{tipo}_state` |
| Archivar | `POST` | `/admin/{recurso}/{id}/archive` | — | `200` | igual que publicar |

`{recurso}` ∈ `posts`, `book-reviews`, `videos`, `projects`. **`unpublish` no existe** en
`videos` ni `projects`: la ruta no está en OpenAPI y el panel **no dibuja el botón**.

Campos comunes de `<Tipo>ParaGuardar` (`extra="forbid"`: cualquier clave desconocida es
`422`): `title`\* (1–200, no en blanco), `slug` (opcional; se deriva del título),
`summary`, `content` (Markdown; **no existe en vídeo**), `featured` (bool), `seo_title`,
`seo_description`, `cover_id`/`thumbnail_id`, `cover_alt_text`/`thumbnail_alt_text` (≤255,
**solo junto a su imagen**), `tag_ids[]` (≤50 UUID, reemplazo completo).

| Tipo | Campos propios de la petición |
| --- | --- |
| `Post` | — |
| `BookReview` | `book_title`, `book_author`, `rating` (1–5; el dominio rechaza `true`), `external_link` |
| `Video` | `provider`, `video_url`, `embed_reference`, `duration_seconds` (>0), `thumbnail_id`, `thumbnail_alt_text`. **Sin `content`** |
| `Project` | `project_status` (`active`\|`paused`\|`completed`), `technologies[]` (≤50, ≤60 c/u, sin blancos), `repository_url`, `demo_url` |

`<Tipo>Administrativo` añade sobre el contrato público: `id`, `status`, `published_at`,
`created_at`, `updated_at`, `content` siempre, y `cover`/`thumbnail` como
**`MedioAdministrativo`**. **`status` y `published_at` no son escribibles** (**D-012-A**):
enviarlos es `422`.

#### Etiquetas y medios

| UI | Método | Endpoint | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- |
| Listar etiquetas | `GET` | `/admin/tags?page&page_size` | — | `200 Pagina[EtiquetaAdministrativa]` | `401` · `422` |
| Crear etiqueta | `POST` | `/admin/tags` | `{name*, slug?, description?}` | `201` | `401` · `403` · `409` · `422` |
| Renombrar | `PUT` | `/admin/tags/{tag_id}` | `{name*, description?}` — **sin `slug`** (**D-012-S**) | `200` | `401` · `403` · `404` · `422` |
| Eliminar | `DELETE` | `/admin/tags/{tag_id}` | — | `204` — **desasocia, no rechaza** | `401` · `403` · `404` |
| Biblioteca | `GET` | `/admin/media?page&page_size` | — | `200 Pagina[MedioAdministrativo]` | `401` · `422` |
| Cargar imagen | `POST` | `/admin/media` | **`multipart/form-data`**: `archivo` (File) + `alt_text` (opcional) | `201 MedioAdministrativo` | `401` · `403` · `413 payload_too_large` · `415 unsupported_image_type` · `422 invalid_image` |
| Eliminar imagen | `DELETE` | `/admin/media/{media_id}` | — | `204` | `401` · `403` · `404` · `409 media_in_use` con `details.usos` |

`MedioAdministrativo`: `id`, `original_filename`, `mime_type`, `size_bytes`, `width`,
`height`, `alt_text`, `checksum`, `created_at`, `access_url`. **Nunca `object_key`.**

#### Historial de auditoría (§15, `Task/012.1`)

| UI | Método | Endpoint | Request | Response | Errores |
| --- | --- | --- | --- | --- | --- |
| Últimos eventos del dashboard | `GET` | `/admin/audit-events?page&page_size` | — | `200 Pagina[EventoDeAuditoria]` | `401 unauthenticated` · `422 validation_error` |

`EventoDeAuditoria`: `id`, `occurred_at`, `action`, `entity_type`, `entity_id` (nulable).
**No transporta** `actor_id`, `event_metadata`, `request_id` ni `ip_address`, así que el
panel **no puede** mostrar autor, contexto, correlation ID ni IP de un evento. **Sin
filtros**: solo `page` y `page_size`. Orden fijo `occurred_at` desc, desempate `id` asc.
**Solo lectura**: `POST`, `PUT`, `PATCH` y `DELETE` responden `405`, y no existe detalle
`/{id}`.

**Ningún endpoint expone eventos de auditoría.** No existe en el contrato y no se inventa.

#### Errores: qué distingue la UI y qué no

| Código | Tratamiento en el panel |
| --- | --- |
| `401 unauthenticated` | **Fin de sesión**: se limpia el estado y se navega a `/admin/acceso` conservando el destino. Los cuatro casos internos son indistinguibles por contrato (§13.4) y no se intenta distinguirlos |
| `401 invalid_credentials` | **Solo en login.** Mensaje genérico único; no se insinúa si el correo existe |
| `403 forbidden` | `Origin` no permitido: es **configuración del backend**, no sesión caducada. Mensaje propio y **sin** redirección a login — redirigir produciría un bucle |
| `404 resource_not_found` | En un listado o un detalle: «no existe». En `GET /admin/profile`: «todavía no hay perfil» (semilla de `Task/022`), no un error |
| `409` | Se ramifica por `code`: `slug_already_exists`, `slug_is_immutable`, `cannot_publish_incomplete_draft` (con `details.campos`), `invalid_{tipo}_state`, `media_in_use` (con `details.usos`), `alt_text_conflict` |
| `413` / `415` / `422 invalid_image` | Mensajes concretos de carga: tamaño (5 MiB), formato (JPEG/PNG/WebP) y archivo ilegible |
| `422` | `validation_error` reparte `details` por campo; `unknown_reference` señala el campo y los valores; `media_without_alt_text` e `invalid_slug` tienen mensaje propio |
| `429 too_many_requests` | Solo en login. Aviso genérico y bloqueo temporal de botón y handler durante los segundos de `Retry-After`; sin reintento automático. Cabecera ausente/inválida: aviso y nuevo intento solo manual, sin inventar duración |
| `500` / fallo de red | Estado de error con «Reintentar». **Nunca** se muestra el cuerpo crudo (S-07) |

`api-contracts.md` §8 declara además `400` y `503`; ningún endpoint administrativo los usa en
su contrato, así que **no** se les da tratamiento especializado: caen en el genérico.

### 6.D Sesión y autenticación — modelo exacto (**D-015-B**)

Derivado de `Task/011` (§13 de `api-contracts.md`, §11 de `security-boundaries.md`) y de
`app/modules/authentication/presentation/cookies.py`.

| Hecho del contrato | Consecuencia para el panel |
| --- | --- |
| La credencial viaja **solo** en la cookie `blog_admin_session`, `HttpOnly` | El frontend **no puede leerla ni la guarda**. No se usa `localStorage` ni `sessionStorage`, ni para la credencial ni para la identidad |
| `Path` = `/api/v1/admin`; `SameSite=Lax`; sin `Domain` | El navegador la envía sola a las rutas administrativas. El panel no manipula cookies |
| La credencial **no aparece en ningún cuerpo** | La única fuente de «¿hay sesión?» es `GET /admin/auth/me` |
| Duración **absoluta** (12 h por defecto), sin renovación deslizante | No hay refresco. La expiración se descubre con el primer `401`, no con un temporizador |
| `login` es el único endpoint administrativo público | `/admin/acceso` es la única ruta del panel sin guarda |
| Validación de `Origin` en `POST`/`PUT`/`DELETE` | El backend local necesita `BLOG_ADMIN_ALLOWED_ORIGINS` con el origen del panel. Ya está documentado en su `.env.example`; **no** exige cambios en el backend |
| El frontend **no autoriza** (`software-architecture.md` §4.4) | La guarda de rutas es comodidad de interfaz. Quien autoriza es el backend, y el panel trata cualquier `401` como autoridad |

Máquina de estados de la sesión:

```
desconocida ──GET /me──▶ autenticada { id, email, display_name }
     │                        │
     │ 401                    │ POST /logout 204  ó  cualquier 401 posterior
     ▼                        ▼
  anonima ◀────────────────────
     │
     │ POST /login 200
     ▼
 autenticada
```

| Flujo | Comportamiento definido |
| --- | --- |
| Entrada al panel | Al montar el subárbol `/admin`, `GET /me`. Mientras la sesión es `desconocida` se muestra `LoadingState`; **no se decide nada** ni se redirige |
| No autenticado | Cualquier ruta protegida con sesión `anonima` navega a `/admin/acceso` con `replace`, guardando el destino en el **estado del router**, nunca en la URL: un `?next=` sería un vector de redirección abierta |
| Login correcto | `200` ⇒ la identidad de la respuesta **es** el estado de sesión (no se repite `/me`). Navega al destino guardado, o a `/admin` si no hay ninguno válido. Solo se acepta `/admin` exacto o un destino que empiece por `/admin/`, nunca prefijos parciales como `/administrator` |
| Credenciales inválidas | `401 invalid_credentials` ⇒ mensaje único y genérico en el resumen de errores, foco al resumen. El campo de contraseña se vacía; el correo se conserva |
| Límite de tasa | `429` ⇒ aviso genérico. `Retry-After` válido fija `esperaHasta`: botón y handler bloqueados hasta vencer, con cleanup del timer al desmontar o sustituir la espera. Sin cabecera válida se permite otro intento manual, sin espera inventada ni retry automático |
| Sesión expirada | Un `401 unauthenticated` en **cualquier** petición administrativa pasa la sesión a `anonima` y navega a `/admin/acceso` conservando el destino. La operación en curso **no se reintenta sola** |
| Logout | `POST /logout` ⇒ `204`. Estado a `anonima` y navegación a `/admin/acceso`. Si `logout` falla con `401`, el resultado observable es el mismo y se trata igual |
| Visitante en el sitio público | **Nunca** se llama a `/me`: el proveedor solo envuelve `/admin` |
| Acceso con sesión ya abierta | `/admin/acceso` con sesión `autenticada` navega a `/admin`: no se muestra un formulario de acceso a quien ya entró |

### 6.E Cliente HTTP — extensiones mínimas, **demostradas**

`src/services/http/` no se toca por reflejo. Se comprobó qué del contrato **no** soporta hoy:

| # | Incompatibilidad demostrada | Fuente que la impone | Cambio mínimo |
| --- | --- | --- | --- |
| **D-015-C** | `construirPeticion` no fija `credentials`, así que `fetch` usa `same-origin`. La topología lógica **D-15** sitúa el API en un **subdominio**: *cross-origin*. Sin `credentials: 'include'` el navegador **no envía la cookie** y ninguna ruta administrativa autentica jamás | `security-boundaries.md` §11.1; `api-contracts.md` §13.5 | Añadir `credentials?: RequestCredentials` a `HttpRequestOptions` y pasarlo solo desde `services/admin`. El sitio público conserva su política de credenciales |
| **D-015-D** | El cuerpo se serializa siempre con `JSON.stringify` y se fuerza `Content-Type: application/json`. `POST /admin/media` es `multipart/form-data` con `archivo` y `alt_text`. Un `FormData` así enviado llegaría como `"[object Object]"` | `api-contracts.md` §14.1; `router_admin.py` de `media` | Si `body instanceof FormData`, pasarlo tal cual y **no** fijar `Content-Type` — el navegador debe poner el `boundary` |

Ambos cambios son aditivos, no alteran ninguna ruta pública y quedan cubiertos por pruebas
propias del cliente.

**Corrección auth (2026-09-05):** `HttpError` añade `retryAfterSeconds`, obtenido en
`httpErrorFromResponse` desde `response.headers.get('Retry-After')` para un `429`. Se
conservan estado, código, detalles, correlation ID y mensaje seguro. El parser acepta
únicamente segundos enteros positivos seguros, no fechas HTTP ni un dato de `details`.
El backend canónico redondea hacia arriba, con mínimo uno, y sus pruebas comprueban
`0 < reintentar <= 300`. Ante cabecera ausente/inválida se devuelve `undefined`: la UI
conserva el aviso genérico y habilita solo un nuevo intento manual. Esta defensa no define
una duración de negocio ni modifica el contrato normal, que sí garantiza la cabecera.
Contrato, RED/GREEN, temporización y mutaciones documentados en el
[reporte, sección 4](../task-reports/TASK-015-report.md#4-arquitectura).

**Lo que no se cambia:** no hay reintentos, ni caché, ni deduplicación (`Task/016`); no hay
progreso de carga —`fetch` no lo expone y el contrato no lo pide; usar `XMLHttpRequest` solo
para eso abriría un segundo camino HTTP—; `VITE_API_BASE_URL` sigue siendo obligatoria y
**no se codifica ningún origen**.

**Consecuencia operativa declarada.** El backend **no tiene middleware CORS** (es de
`Task/018`). Por tanto, en local el panel debe servirse en el **mismo origen** que el API —la
topología Traefik de `Task/007`, que `.env.example` ya describe— o, con `vite dev` contra el
backend directo, `Task/018` deberá haber habilitado CORS con credenciales. Es una condición
del entorno, no un cambio de código.

### 6.F Formularios — matriz campo a campo (**A-03**, **A-08**)

Reglas comunes a **todos** los formularios:

- `<form>` nativo; cada control es `<input>`, `<textarea>`, `<select>` o `<button>` nativo.
- **A-03**: todo control tiene `<label htmlFor>` **visible**. Ningún `placeholder` sustituye
  a una etiqueta. Los grupos relacionados usan `fieldset`/`legend`.
- Obligatoriedad: atributo `required` **más** el texto «(obligatorio)» en la etiqueta —nunca
  solo un asterisco de color (**A-07**).
- **A-08**: un error de campo se anuncia con `aria-invalid="true"` y `aria-describedby`
  apuntando al `id` del mensaje. Un `id` estable por campo lo garantiza `FormField`.
- Resumen de errores en `role="alert"` al principio del formulario, con enlaces a cada campo;
  tras un envío fallido el **foco va al resumen**. El éxito se anuncia en `role="status"`.
- Estados `inactivo → enviando → exito | error`. **Doble envío imposible**: botón `disabled`
  mientras `enviando`, más guarda en el manejador.
- La validación de cliente es **de usabilidad**; el backend decide
  (`software-architecture.md` §2). Solo se replican las restricciones que el contrato fija.

| Formulario | Campos | Required | Validación cliente | Error de servidor | Asociación accesible | Estado de envío |
| --- | --- | --- | --- | --- | --- | --- |
| **Acceso** | `email`, `password` | ambos | no vacío; `maxLength` 254 / 1024 | `401` genérico · `429` con espera · `422` por campo | `label` + `aria-describedby` + resumen | botón «Entrando…», deshabilitado |
| **Contenido común** (4 tipos) | `title`, `slug`, `summary`, `featured`, `seo_title`, `seo_description`, `tag_ids`, portada + su `alt` | `title` | `title` no en blanco; longitudes; slug `^[a-z0-9]+(-[a-z0-9]+)*$` | `409 slug_*`, `422 invalid_slug`, `unknown_reference` | igual | «Guardando…» |
| **Artículo** | + `content` (Markdown) | — | — | — | `label` del `textarea` del editor | — |
| **Review** | + `book_title`, `book_author`, `rating`, `external_link`, `content` | — | `rating` entero 1–5 | `422 invalid_rating` | `select` 1–5 con `label` | — |
| **Vídeo** | + `provider`, `video_url`, `embed_reference`, `duration_seconds`. **Sin `content`** | — | duración > 0 | `422` | `select` de proveedor con `label` | — |
| **Proyecto** | + `content`, `project_status`, `technologies[]`, `repository_url`, `demo_url` | — | tecnología no en blanco, ≤60 | `422` | `fieldset` para la lista | — |
| **Etiqueta (crear)** | `name`, `slug`, `description` | `name` | no en blanco; formato de slug | `409` slug repetido | igual | — |
| **Etiqueta (renombrar)** | `name`, `description` | `name` | no en blanco | `422` | igual | — |
| **Perfil** | `full_name`, `headline`, `biography` (Markdown), `contact_email`, foto + su `alt`, `seo_title`, `seo_description`, `social_links[]` | `full_name` | no en blanco; `label` y `url` no vacíos por enlace | `422 media_without_alt_text` · `409 alt_text_conflict` | `fieldset`/`legend` por enlace social | — |
| **Carga de imagen** | `archivo`, `alt_text` | `archivo` | tipo y tamaño **anunciados**, no impuestos: decide el backend | `413`, `415`, `422 invalid_image` | `label` del `input type="file"` | «Subiendo…» |

**Campos que el panel nunca envía**: `status`, `published_at`, `created_at`, `updated_at`, el
`slug` en el renombrado de una etiqueta, y `cover_alt_text`/`thumbnail_alt_text`/
`photo_alt_text` cuando la imagen **ya tiene** texto (§6.H). Con `extra="forbid"` cualquiera
de ellos sería un `422`.

**Slug inmutable**: si `published_at !== null`, el campo se renderiza deshabilitado con la
explicación visible; el `409 slug_is_immutable` sigue tratándose como respaldo.

### 6.G Markdown — **D-04** resuelta (Vigente — aprobada el 2026-09-05)

**Decisión: `<textarea>` nativo + `MarkdownContent` para la vista previa. Cero dependencias
nuevas.**

Evaluada contra la información que `open-decisions.md` D-04 exige:

| Criterio de D-04 | Resultado |
| --- | --- |
| Necesidad de vista previa en vivo | Cubierta: el valor del `textarea` alimenta `MarkdownContent`. `useDeferredValue` —de React, sin dependencia— evita reprocesar en cada pulsación |
| Inserción de imágenes | **No se ofrece dentro del cuerpo**, y no por falta de editor: `access_url` es temporal y `api-contracts.md` §12 prohíbe almacenarla. Insertar `![alt](access_url)` persistiría un enlace que caduca. La URL estable es **D-08** (`Task/030`). La imagen del contenido se asocia por `cover_id`/`thumbnail_id`/`photo_id`, que **sí** es estable |
| Peso | Cero bytes añadidos. Un editor tipo CodeMirror o TipTap pesa cientos de KiB en el panel |
| Accesibilidad | Un `textarea` es un control nativo, etiquetable y navegable con teclado. Un editor enriquecido exige `contenteditable` y ARIA propios, y arriesga **A-03**, que es criterio de esta tarea |
| Mantenimiento | Ninguna dependencia que seguir |
| Compatibilidad con la sanitización | **Máxima por construcción**: es literalmente el mismo componente, luego el mismo `react-markdown@10.1.0`, el mismo `rehype-sanitize@6.0.0`, el mismo `skipHtml` y el mismo esquema |

```
<textarea> ──valor──▶ useDeferredValue ──▶ MarkdownContent ──▶ vista previa sanitizada
```

- **No** se instala otro parser, **no** se duplica la sanitización, **no** se crea un segundo
  renderizador y **no** se permite HTML crudo.
- La vista previa **no publica ni expone** nada: no cambia estado, no genera URL pública y
  vive dentro de una ruta protegida (B.6).
- Alcance: artículos, reviews, proyectos y la biografía del perfil. **Vídeo no tiene Markdown
  ni vista previa** (`MVP_SCOPE.md` §3.1, `USER_FLOWS.md` B.6).
- Conmutación editor/vista previa con dos `<button>` y `aria-pressed`; en anchos amplios ambos
  paneles caben lado a lado por composición intrínseca. **No** se implementa un patrón ARIA de
  pestañas: sería un widget compuesto sin necesidad demostrada.

### 6.H Medios — render frente a escritura

| Operación | Qué se usa | Regla |
| --- | --- | --- |
| **Mostrar** una imagen (biblioteca, portada actual, foto) | **`access_url`** | Enlace temporal. No se almacena, no se persiste, no se construye ninguna URL de MinIO o S3 |
| **Asociar** una imagen a un contenido | **`id` del `MediaAsset`** en `cover_id` / `thumbnail_id` / `photo_id` | La regla pública «solo `access_url`» es de **lectura**; la escritura administrativa usa el identificador |
| **Eliminar** una imagen | `id` en la ruta | Confirmación previa; `409 media_in_use` se muestra con `details.usos` |

`MediaImage` (de `Task/014`) se reutiliza sin cambios: `MedioAdministrativo` incluye los
cuatro campos de `MedioPublico`.

**Política de `alt_text`, sin redefinir nada** (`api-contracts.md` §14.11, **D-010-N**,
**D-012-Y**, **D-012-Z**):

| Estado de la imagen elegida | Qué hace el panel |
| --- | --- |
| Sin `alt_text` | Muestra un campo **editable**; lo envía junto al `*_id`. Es el **primer uso** y lo fija |
| Con `alt_text` | Muestra el texto **como dato de la imagen, no editable**, y **omite** el campo en la petición. Así nunca se envía uno distinto y `409 alt_text_conflict` no puede producirse por acción del panel |
| Sin imagen | El campo **no existe**: enviar texto sin imagen es `422` |

**No se redefine** la política de conflicto: **D-012-Z** está aceptada para el MVP y corregir
un `alt_text` compartido sigue siendo mejora futura sin propietario. El panel **no** ofrece
esa corrección.

Flujo B.4/B.5 completo: cargar (`multipart`, `alt_text` opcional) → aparece en la biblioteca →
seleccionar como portada desde el formulario → dar el texto en ese uso si falta → publicar. La
validación de publicación (`409` con `cover_alt_text` en `details.campos`) es la última guarda,
no el único mecanismo.

**Límites que el panel anuncia** (de `Task/010`): 5 MiB; JPEG, PNG y WebP. Se anuncian en la
interfaz, pero **decide el backend**: el tipo se valida decodificando el archivo.

### 6.I Estados de publicación — la UI refleja el contrato

| Estado actual | `Post` / `BookReview` | `Video` / `Project` |
| --- | --- | --- |
| `draft` | **Publicar**, **Archivar** | **Publicar**, **Archivar** |
| `published` | **Despublicar**, **Archivar** | **Archivar** |
| `archived` | *(ninguna: `archived → *` no existe)* | *(ninguna)* |

- `status` se muestra con `Badge` **más texto** (**A-07**): `draft` neutral «Borrador»,
  `published` `success` «Publicado», `archived` `warning` «Archivado».
- Repetir una transición es `409`, **no** una operación idempotente (**D-012-B**): el panel no
  la reintenta; recarga el recurso y explica el estado real.
- `409 cannot_publish_incomplete_draft` se presenta con **todos** los campos de
  `details.campos` a la vez, traducidos a las etiquetas del formulario, y el foco va al resumen.
- Editar un contenido publicado **no lo despublica** (B.3). La interfaz no insinúa lo contrario.
- **No hay restauración desde `archived`** ni `DELETE` de contenido: no existen en el contrato.

### 6.J Dashboard — **completo**, las tres piezas

`MVP_SCOPE.md` §3.3 pide tres cosas como **alcance mínimo**. Las tres son construibles con
las **39 operaciones HTTP** vigentes (§6.C.0):

Los paths van **completos** en esta sección, sin la abreviatura de §6.C.0, porque es donde
se cuentan las peticiones una a una y no debe quedar ninguna duda de a qué se llama.

| Pieza | Fuente de datos | Peticiones | Cómo se construye |
| --- | --- | ---: | --- |
| Conteo por tipo y estado | `GET /api/v1/admin/{posts,book-reviews,videos,projects}?status={draft,published,archived}&page_size=1` | **12** | Se lee `total` de la envoltura. `status` es el único filtro administrativo (**D-012-M**) y `page_size=1` es válido porque el mínimo es 1. **4 tipos × 3 estados** |
| Últimos elementos modificados | `GET /api/v1/admin/{posts,book-reviews,videos,projects}?page_size=5` | **4** | Ya viene ordenado `updated_at` desc, desempate `slug` asc (**D-012-L**). Mezclar los cuatro «top 5» y quedarse con los 5 primeros da el top 5 global **exacto**, porque cada lista está ordenada. **1 por tipo** |
| **Últimos eventos de auditoría** | `GET /api/v1/admin/audit-events?page_size=5` | **1** | Ya viene ordenado `occurred_at` desc, desempate `id` asc (`api-contracts.md` §15.4). Se renderiza `occurred_at`, `action` y `entity_type`; `entity_id` enlaza al elemento cuando no es nulo |
| | | **17** | |

**17 peticiones en total** —12 + 4 + 1—, lanzadas en paralelo con estado de carga por
bloque. Se añaden accesos rápidos a las secciones del panel. **Sin gráficas, sin analítica y
sin ningún KPI que no salga de un `total` del contrato.**

No se reduce ese número inventando agregación: no existe un endpoint de dashboard, y crear
uno sería ampliar `Task/015` a backend, que `STAGE-04` no permite. Diecisiete peticiones
pequeñas y paralelas es el coste real de no inventar contrato.

**Lo que el dashboard no puede mostrar de un evento**, porque el DTO `v1` no lo transporta:
quién lo hizo (`actor_id`), su contexto (`event_metadata`), su correlation ID (`request_id`)
ni la IP (`ip_address`). No se inventa ninguno ni se pide por otra vía: `entity_id` nulo se
renderiza como evento sin elemento asociado, que es lo que ocurre en los de sesión.

### 6.K Componentes — clasificación A / B / C

**A. Ya existen — se reutilizan sin modificar**

| Pieza | Origen | Uso en `Task/015` |
| --- | --- | --- |
| `Container`, `Stack`, `Button`, `Card`, `Badge` | `Task/013` | Estructura, acciones y estado de publicación |
| `LoadingState`, `EmptyState`, `ErrorState` | `Task/014` | Listados, dashboard, biblioteca |
| `Pagination` | `Task/014` | Los 4 listados, etiquetas y medios. Conserva el resto de parámetros de la URL, incluido `status` |
| `ExternalLink` | `Task/014` | Enlaces de proyecto, review y vídeo mostrados en el panel (**S-12**) |
| `MediaImage` | `Task/014` | Biblioteca y previsualización de portada: `MedioAdministrativo` satisface `MedioPublico` |
| `MarkdownContent` | `Task/014` | **La vista previa. Es el mismo pipeline** (ADR-005, **S-03**) |
| `useAsyncResource` | `Task/014` | Toda carga del panel, con sus cuatro fases |
| `useDocumentTitle` | `Task/014` | Título por página del panel |
| `HttpClientContext` / `useHttpClient` | `Task/014` | Acceso al cliente desde las páginas del panel |
| `HttpError` | `Task/014` | `status`, `code`, `details`, `requestId` — la base del mapeo de errores |
| `useAppConfig` | `Task/006` / `Task/014` | **Se retira**: el panel no necesita la configuración fuera del cliente HTTP. Cierra la deuda 11 de `Task/014` |

**B. Nuevos compartidos — cada uno con consumidores reales demostrados**

| Componente | Ubicación | Consumidores | Por qué se eleva |
| --- | --- | --- | --- |
| `FormField` | `src/components/FormField/` | **9 formularios**, decenas de campos | Es el único punto donde se generan los `id`, `aria-describedby` y `aria-invalid` que hacen ciertos **A-03** y **A-08**. Repetirlo por campo garantizaría que algún día falte |
| `FormFeedback` | `src/components/FormFeedback/` | Todos los formularios, más las acciones de medios y etiquetas | Resumen `role="alert"` y confirmación `role="status"`, con el foco gestionado en un solo sitio |

**No se crean**, por falta de consumidor o de contrato estable: `Input`, `Textarea`, `Select`,
`Modal`, `Dialog`, `Toast`, `Table`, `IconButton`, `VisuallyHidden`, `Divider`, `Heading`,
`Text`, `DataGrid`. Los controles se usan **nativos** dentro de `FormField`; envolverlos
añadiría una capa sin comportamiento (ADR-004, **M-06**). **No se construye un framework de
formularios**: no hay registro de campos, ni esquema declarativo, ni resolutores; cada
formulario es un `<form>` con estado local.

**C. Específicos del panel — no se elevan a `components`**

| Pieza | Ubicación | Consumidores |
| --- | --- | --- |
| `AdminLayout` (+ navegación y enlace de salto) | `src/app/` | Ruta layout del subárbol |
| `AdminSessionProvider`, `adminSessionContext`, `useAdminSession` | `src/app/` | El subárbol `/admin` |
| `RutaProtegida` | `src/app/` | Las 16 rutas protegidas |
| `MarkdownEditor` | `src/features/markdown/` | 3 formularios de contenido + perfil |
| `MediaPicker`, `MediaUploader` | `src/features/media/` | 4 formularios de contenido + perfil + biblioteca |
| `ContenidoForm` (campos comunes), `PublishActions`, `ListadoAdministrativo`, `TagPicker`, `EstadoBadge` | `src/features/admin-content/` | Los 4 tipos |
| Confirmación en línea de borrado | junto a su página | Medios y etiquetas |

`ContenidoForm`, `ListadoAdministrativo` y `PublishActions` existen porque hay **cuatro**
consumidores casi idénticos, no por simetría: cada tipo compone además sus propios campos.

### 6.L Accesibilidad — matriz A-01…A-08

| Criterio | Heredado / preservado | Propiedad de `Task/015` | Diferido |
| --- | --- | --- | --- |
| **A-01** Teclado | Iniciado en `Task/013`, continuado en `Task/014` | **Continúa** en el panel: solo controles nativos, enlace de salto propio, orden natural, sin trampas de foco | Auditoría formal: `Task/016` |
| **A-02** HTML semántico | Asumido por `Task/014` | **Continúa**: `header`/`nav`/`main`/`footer`, un solo `h1` por página, jerarquía sin saltos, Markdown desde `h2` también en la vista previa | `Task/016` |
| **A-03** Labels en formularios | — | **Asume.** `<label htmlFor>` visible en **todos** los campos de los 9 formularios, `fieldset`/`legend` en los grupos, sin `placeholder` como etiqueta | — |
| **A-04** Texto alternativo | Columna (`Task/010`), exigencia (`Task/012`), render (`Task/014`) | **Continúa**: `MediaImage` en el panel y **escritura del `alt_text` en el primer uso** | — |
| **A-05** Contraste | Asumido por `Task/013` | **Preserva**: sin colores literales; las guardas se aplican a todo `*.module.css` nuevo | — |
| **A-06** Foco visible | Asumido por `Task/013` | **Preserva**: ni un `outline: none` sin reemplazo | — |
| **A-07** Sin depender del color | Asumido por `Task/013` | **Preserva**: estado de publicación con texto, obligatoriedad con texto, errores con texto | — |
| **A-08** Errores anunciados | — | **Asume.** `aria-invalid`, `aria-describedby`, resumen `role="alert"`, foco al resumen tras el fallo, éxito en `role="status"` | — |

**Afirmación permitida:** el panel usa HTML semántico y controles nativos, asocia todas sus
etiquetas y anuncia sus errores de forma programáticamente determinable. **No se afirma que el
producto cumpla WCAG 2.1 AA**: la auditoría es `Task/016`.

### 6.M Seguridad — amenazas y controles reales de esta tarea

| Amenaza | Control en `Task/015` | Fuente |
| --- | --- | --- |
| XSS por Markdown del administrador o de la vista previa | **Mismo** pipeline sanitizado; sin `dangerouslySetInnerHTML`; sin HTML crudo | **S-03**, ADR-005 |
| Robo de la credencial por XSS | El panel **no lee ni guarda** la credencial; sigue en la cookie `HttpOnly` | `security-boundaries.md` §11.2 A-03 |
| CSRF | Ninguna capa nueva: `SameSite=Lax` más la validación de `Origin` del backend. **No se inventa un token CSRF** | A-11, D-011-K |
| Enumeración de cuentas | Mensaje **único y genérico** ante `401 invalid_credentials`; el panel no distingue los tres casos | A-05, §13.4 |
| Redirección abierta tras el login | El destino viaja en el **estado del router**, no en la URL, y solo se acepta si empieza por `/admin` | Decisión de esta tarea |
| Fuga de detalles internos | Nunca se muestra el cuerpo crudo del error; `HttpError` ya descarta la traza | **S-07** |
| Enlaces externos | `ExternalLink` con `rel="noopener noreferrer"` también en el panel | **S-12** |
| Secretos en el bundle | Ninguna variable nueva. Todo `VITE_*` es público por definición | **S-10** |
| Contenido administrativo en páginas públicas | Subárbol `/admin` en diferido; comprobado sobre los *chunks* de `dist/` | **P-05** |
| Suplantación de autorización desde el cliente | La guarda de rutas es comodidad; **el backend autoriza** y cualquier `401`/`403` es autoridad | `software-architecture.md` §4.4 |

**No se inventa** ningún mecanismo criptográfico, ninguna cookie nueva, ningún esquema de
tokens ni ninguna cabecera de seguridad: las cabeceras y el CORS efectivo son de `Task/018`.

### 6.N Responsive

Estrategia **intrínseca** heredada de `Task/013` y `Task/014`: `Container`, `clamp()`,
`min()`, `Stack wrap`, `repeat(auto-fit, minmax(…, 1fr))`. La navegación del panel es una
lista que **envuelve**, no una barra lateral fija: una barra lateral de ancho fijo es la causa
habitual de desbordamiento horizontal en pantallas de 320 px.

El editor y su vista previa se colocan en una rejilla `auto-fit` con un mínimo razonable: en
pantallas estrechas quedan uno debajo de otro sin ninguna media query. Solo se admite una
media query de ancho si una composición lo exige de verdad, con su justificación escrita.

**Objetivo medible:** `scrollWidth == clientWidth` en 320, 390, 768 y 1280 px en las 18
superficies del panel.

### 6.O Dependencias — **ninguna** (**D-015-E**)

No se propone ni se instala ninguna dependencia nueva. **D-04** se resuelve con la plataforma
y con lo que ya existe. Las cinco de producción actuales —`react`, `react-dom`,
`react-markdown@10.1.0`, `react-router@8.3.0`, `rehype-sanitize@6.0.0`— bastan.

Si durante la implementación apareciera una necesidad no cubierta, se registraría con
consumidor real, impacto de bundle, accesibilidad y alternativa sin dependencia, **y no se
instalaría sin autorización del usuario** — el mismo procedimiento de **D-014-F**.

### 6.P Tokens y sistema de diseño

Se consumen los **50 tokens** existentes. **No se crean tokens nuevos por comodidad**; si
alguna superficie del panel exigiera uno, se justificaría en el reporte. No se introduce
Tailwind, MUI, Chakra, Bootstrap, Ant Design ni ninguna otra biblioteca visual: **D-03** sigue
vigente (CSS Modules + CSS Custom Properties). **No hay modo oscuro**: ninguna fuente canónica
nueva lo pide.

---

## 7. TDD / Plan test-first

`BACKEND_TESTING_STRATEGY.md` obliga en el **backend**; esta tarea no lo toca. Aun así se
adopta el ciclo **RED → GREEN** por *slice*, como hizo `Task/014`, y la Definition of Done de
frontend exige lint, typecheck, suite en verde, build y ausencia de errores de consola.

### 7.1 Dónde la prueba tiene señal real

Con `jsdom` y un `fetch` inyectado se prueban de verdad: la máquina de estados de la sesión, la
guarda de rutas, la traducción de errores del contrato a interfaz, la asociación accesible de
etiquetas y mensajes, el foco tras un envío fallido, la prevención del doble envío, el cuerpo
exacto de cada petición (incluido **lo que no se envía**) y la reutilización del pipeline
Markdown. **No** se prueban con `jsdom` el layout real ni el desbordamiento horizontal: eso se
mide en el navegador, como en `Task/014`.

### 7.2 Orden RED → GREEN por *slice*

El orden propuesto en el encargo se acepta con **dos reordenaciones justificadas**: los
componentes de formulario suben **antes** de la página de acceso (el acceso es ya un formulario
y debe nacer cumpliendo A-03/A-08), y los medios se abordan **después** del formulario de
referencia (la selección de portada es un campo de ese formulario, no una superficie previa).

| # | Slice | Criterio de RED | Criterio de GREEN |
| --- | --- | --- | --- |
| 1 | Tipos y adaptadores `services/admin` | El adaptador no existe; la prueba de «cuerpo y ruta exactos» falla | Cada adaptador emite el método, la ruta y el cuerpo del contrato, y **no** envía campos no escribibles |
| 2 | Cliente HTTP: `credentials` y `FormData` (**D-015-C/D**) | El `FormData` llega serializado y no hay `credentials` | Pasa el `FormData` sin `Content-Type` y propaga `credentials`; **las pruebas públicas siguen intactas** |
| 3 | Sesión: contexto, `/me`, login, logout, `401` | No hay proveedor; el estado no existe | Las nueve transiciones de §6.D se comprueban una a una |
| 4 | Router y layout del panel; `RutaProtegida`; 404 del panel | `/admin` no resuelve | Las 18 rutas resuelven; **las doce públicas siguen intactas**; sin sesión se navega a `/admin/acceso` conservando el destino |
| 5 | `FormField` y `FormFeedback` | No existen | `label` asociada, `aria-describedby`, `aria-invalid`, resumen `role="alert"`, foco gestionado |
| 6 | Página de acceso | La ruta está vacía | Login correcto, credenciales inválidas, `429`, `422`, doble envío imposible |
| 7 | Dashboard | No hay página | Las **tres** piezas de `MVP_SCOPE.md` §3.3: conteos por tipo y estado, top 5 global correcto y **últimos eventos de auditoría** desde `GET /admin/audit-events`; estados de carga, vacío y error por bloque |
| 8 | Listados administrativos (4 tipos) | No hay página | Tres estados, filtro `status`, paginación en la URL, vacío, error con reintento |
| 9 | Formulario común + crear y editar `Post` | No hay formulario | `POST` → `201` → navegación a la edición; `PUT` completo; `409`/`422` mapeados; slug bloqueado tras publicar |
| 10 | `MarkdownEditor` y vista previa | No hay editor | El `textarea` alimenta `MarkdownContent`; `<script>`, `on*` y `javascript:` quedan neutralizados **en la vista previa** |
| 11 | Medios: biblioteca, carga, selección, borrado | No hay superficie | `multipart` correcto; `413`/`415`/`422`; `409 media_in_use` con sus usos; confirmación previa |
| 12 | `alt_text` en el primer uso | — | Sin texto ⇒ campo editable y envío; con texto ⇒ campo no editable y **campo ausente** en el cuerpo |
| 13 | Review, vídeo y proyecto | No hay páginas | Campos propios; vídeo **sin** `content` ni vista previa; **`unpublish` ausente** en vídeo y proyecto |
| 14 | Acciones de publicación | No hay acciones | Botones según estado y tipo; `409` de borrador incompleto con todos los campos; `409` de estado inválido |
| 15 | Etiquetas | No hay página | Crear, renombrar **sin `slug`**, borrar con **confirmación** y desasociación |
| 16 | Perfil | No hay página | Carga, guardado, enlaces sociales por índice, `404` sin semilla, `422 media_without_alt_text` |
| 17 | Barrido A-03/A-08 y responsive | — | Toda etiqueta asociada; todo error anunciado; sin desbordamiento a 4 anchos |
| 18 | Regresión y documentación | — | **440** pruebas previas en verde, doce rutas públicas intactas, `/__design-system` solo en DEV, guardas CSS extendidas |

### 7.3 Casos negativos y de seguridad obligatorios

Sin sesión en cada ruta protegida · `401` a mitad de una operación · `403 forbidden` **sin**
redirección a login · `429` con y sin `Retry-After` · `404` de recurso y `404` de perfil sin
semilla · slug duplicado e inmutable · publicación incompleta con varios campos · transición
repetida · medio en uso · `alt_text` distinto **imposible de enviar por construcción** ·
Markdown malicioso en la vista previa · destino de redirección externo rechazado · doble envío
· parámetro de consulta desconocido nunca emitido.

### 7.4 Regresiones vigiladas

Las **440** pruebas actuales; las doce superficies públicas y su comodín; `/__design-system`
ausente de `dist/`; las guardas de `designSystem.guards.test.ts` y de contraste, que descubren
los `*.module.css` recorriendo el árbol y por tanto **abarcan los del panel por el hecho de
existir**; `src/services/public/**` sin cambios.

---

## 8. Plan de validación

1. Compuertas: `npm run format:check`, `npm run lint`, `npm run typecheck`, `npm run test:run`,
   `npm run build`.
2. **Gate P-05** completo, según §8.1 — cinco comprobaciones, no una.
3. Validación visual en Chrome de las 18 superficies del panel a 320, 390, 768 y 1280 px, sin
   desbordamiento horizontal ni `console.error`.
4. Recorrido con teclado: enlace de salto, navegación, formularios, foco tras error.
5. Recorrido funcional en el entorno local, **condicionado** a que exista un administrador
   (riesgo R-A) y con `BLOG_ADMIN_ALLOWED_ORIGINS` declarado en el `.env` local del backend.
6. Verificación de que `personal-blog-backend` no tiene cambios.

### 8.1 Gate P-05 — rediseñado

**La comprobación planteada inicialmente era inválida.** Buscar la cadena
`admin/auth/login` en todo `dist/assets/*.js` y exigir **ausencia** contradice el propio
entregable: el código del panel **tiene que estar** en `dist/`, en *chunks* diferidos. Lo
que **P-05** exige no es que el código no exista, sino que **no pertenezca al grafo de carga
inicial de una página pública**:

> P-05 — *«Sin descargar contenido administrativo en páginas públicas: el código del panel
> se carga solo en el panel.»*

El gate correcto tiene cinco comprobaciones. Las tres primeras son automatizables sobre el
artefacto real de Vite; la cuarta y la quinta se validan en el navegador y en la suite.
**No se modifica `vite.config.ts`** —ni para habilitar `build.manifest`— solo para
facilitar la medición: el análisis se hace sobre `dist/index.html` y los *chunks* emitidos.

| # | Qué demuestra | Mecanismo | Resultado esperado |
| --- | --- | --- | --- |
| **P-05-1** | **Existe separación diferida** del subárbol administrativo | El *chunk* que contiene los marcadores administrativos **no** es el de entrada y se alcanza solo por `import()` dinámico | Al menos un *chunk* distinto del de entrada contiene los marcadores |
| **P-05-2** | **El grafo de carga inicial no contiene el panel** | Prueba de nodo sobre `dist/`: se lee `dist/index.html`, se extraen el `<script type="module" src>` y los `<link rel="modulepreload">`, y desde el *chunk* de entrada se siguen **solo los `import` estáticos** de forma transitiva. Sobre esa clausura se buscan los marcadores | **Cero** coincidencias en la clausura estática |
| **P-05-3** | **Anti-tautología**: la prueba no pasa porque el panel no exista | Los mismos marcadores se buscan en **todo** `dist/assets/*.js` | **Al menos una** coincidencia, y fuera de la clausura de P-05-2 |
| **P-05-4** | **Una visita pública no pide nada del panel** | Prueba con `fetch` instrumentado: se monta el router en `/`, `/articulos`, `/reviews`, `/videos`, `/proyectos`, `/quien-soy`, `/contacto`, `/buscar` y se inspeccionan las URL solicitadas. Se repite en Chrome con la pestaña **Red** | Ninguna petición a `/api/v1/admin/*` —en particular **ninguna a `/admin/auth/me`**— y ningún *chunk* administrativo solicitado. Al navegar después a `/admin`, el *chunk* **sí** aparece en la pestaña Red |
| **P-05-5** | **La demostración sigue fuera de producción** | Búsqueda de `__design-system` en todo `dist/` (comprobación heredada de `Task/014`, que sigue siendo válida porque `import.meta.env.DEV` es `false` literal en el *build*) | **Cero** coincidencias |

**Marcadores administrativos** (deben cumplirse **todos** en P-05-2): el prefijo de ruta
`/api/v1/admin`, la ruta de acceso `/admin/acceso` y el nombre de la cookie de sesión si
llegara a aparecer en el código. Son literales de cadena, que la minificación conserva.

P-05-1 a P-05-3 y P-05-4 (la mitad de `jsdom`) viven en la suite como pruebas permanentes,
de modo que **fallan en el futuro** el día que alguien importe una página del panel desde el
árbol público. P-05-4 en navegador y la evidencia de la pestaña Red se registran en el
reporte.

## 9. Comandos de validación

```powershell
# Compuertas de calidad (personal-blog-frontend)
npm run format:check; npm run lint; npm run typecheck; npm run test:run; npm run build

# P-05-1 a P-05-4 (mitad jsdom): viven en la suite, se ejecutan con `test:run`
# P-05-3 anti-tautologia, comprobacion manual de apoyo: el panel SI esta en dist
Select-String -Path dist/assets/*.js -Pattern "/api/v1/admin" -List

# P-05-5 la demostracion sigue fuera de produccion (sin resultados)
Select-String -Path dist/assets/*.js -Pattern "__design-system" -List

# El backend no cambio (salida vacia)
git -C ..\personal-blog-backend status --porcelain
```

> La comprobación de P-05-2 —la clausura de imports estáticos desde `dist/index.html`— **no
> es un `Select-String`**: es la prueba de nodo descrita en §8.1, porque exige recorrer el
> grafo y no basta con buscar una cadena en todos los archivos.

## 10. Evidencia esperada

Salida real de las cinco compuertas; número final de pruebas y cobertura; descripción de las 18
superficies a los cuatro anchos; resultado de las dos búsquedas sobre `dist/`; listado de
archivos creados y modificados; declaración explícita de lo que **no** pudo validarse en el
navegador y por qué.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-A | **No existe administrador ni perfil en la base local**: la semilla es de `Task/022`. Sin una fila en `administrators` no se puede iniciar sesión en el navegador | El recorrido funcional real queda parcialmente sin validar, igual que le ocurrió a `Task/014` con el contenido | La suite cubre el comportamiento con `fetch` inyectado. Se declara la limitación; si el usuario autoriza crear un administrador local, se documenta el procedimiento como paso de validación, no como código |
| R-B | **El backend no tiene middleware CORS** (es de `Task/018`) | Con `vite dev` en un origen distinto del API, ninguna petición administrativa funciona | Servir el panel en el **mismo origen** que el API (topología Traefik de `Task/007`), que es lo que `.env.example` ya describe. Se documenta como condición de entorno |
| R-C | `BLOG_ADMIN_ALLOWED_ORIGINS` vacío ⇒ **todo método que cambia estado responde `403`** (*fail-closed* deliberado) | El panel parece roto sin motivo aparente | El panel distingue `403 forbidden` con mensaje propio que nombra la causa. Documentado en los pasos de validación |
| R-D | El listado administrativo devuelve el **contenido Markdown completo** de cada elemento | Listados y dashboard más pesados de lo necesario | No se cambia el backend. Se pide `page_size` pequeño donde solo hace falta el `total`. Se registra como deuda |
| R-E | 17 peticiones en el dashboard (12 conteos + 4 listados recientes + 1 de auditoría) | Latencia perceptible en local lento | Se lanzan en paralelo con estados de carga por bloque; ninguna bloquea a las demás |
| R-F | Alcance amplio: cuatro tipos, nueve formularios, dieciocho superficies | Tarea larga; riesgo de inventar abstracciones | Clasificación A/B/C cerrada en §6.K; solo **dos** componentes compartidos nuevos; prohibición explícita de un framework de formularios |
| R-G | Confundir la vista previa con una publicación | Exposición accidental de un borrador | La vista previa vive dentro de una ruta protegida, no cambia estado y no genera URL pública (B.6) |

## 12. Decisiones técnicas

| # | Decisión | Estado |
| --- | --- | --- |
| **D-015-A** | Árbol de 18 rutas `/admin/*` en español, sin detalle administrativo separado de la edición y sin ruta de vista previa | **Vigente — aprobada el 2026-09-05** |
| **D-015-B** | Modelo de sesión: `/me` al montar el subárbol, identidad del login como estado, `401` ⇒ fin de sesión, destino en el estado del router y solo interno | **Vigente — aprobada el 2026-09-05** |
| **D-015-C** | `credentials` opcional en el cliente HTTP, usado **solo** por los adaptadores administrativos | **Vigente — aprobada el 2026-09-05** |
| **D-015-D** | `FormData` se pasa tal cual y sin `Content-Type`, para la carga `multipart` de medios | **Vigente — aprobada el 2026-09-05** |
| **D-015-E** | **D-04 resuelta**: `<textarea>` nativo + `MarkdownContent`. **Cero dependencias nuevas**. Sin inserción de imágenes en el cuerpo mientras **D-08** siga abierta | **Vigente — aprobada el 2026-09-05** |
| **D-015-F** | Solo **dos** componentes compartidos nuevos, `FormField` y `FormFeedback`; el resto es específico del panel | **Vigente — aprobada el 2026-09-05** |
| **D-015-G** | El proveedor de sesión envuelve **solo** `/admin`, no el router entero, para que el sitio público no consulte `/me` | **Vigente — aprobada el 2026-09-05** |
| **D-015-H** | Cuando la imagen ya tiene `alt_text`, el panel **omite** el campo en la petición: `alt_text_conflict` deja de ser alcanzable desde la interfaz | **Vigente — aprobada el 2026-09-05** |
| ~~**D-015-I**~~ | ~~El dashboard entrega **dos** de las tres cosas de MVP_SCOPE §3.3; los eventos de auditoría se difieren a `Task/017` por ausencia de contrato~~ | **RETIRADA el 2026-09-05.** No era una decisión válida: reducía un alcance mínimo canónico por cuenta propia y trasladaba interfaz React a `Task/017`, cuyos repositorios son `backend, infra` y que **depende de `Task/015`**. Sustituida por el **bloqueo B-015-1**, que `Task/012.1` resolvió (§2.1). **No se restaura**: el dashboard mínimo se entrega **completo** dentro de `Task/015` |
| **D-015-J** | El gate **P-05** se verifica sobre el **grafo de carga inicial**, no por ausencia de la cadena en `dist/`: cinco comprobaciones, con anti-tautología, sin tocar `vite.config.ts` (§8.1) | **Vigente — aprobada el 2026-09-05** |
| **D-015-K** | Terminología HTTP inequívoca: **27 patrones de ruta** y **39 operaciones método+ruta**, verificadas programáticamente (§6.C.0). No se usa «endpoints» como sinónimo de ninguna de las dos | **Vigente — aprobada el 2026-09-05** |

## 13. Documentación creada o actualizada

| Documento | Cambio |
| --- | --- |
| `docs/tasks/TASK-015-admin-panel.md` | **Creado** (esta ficha) |
| `docs/project-management/STATUS.md` | Aprobación registrada; **15/41 — 37 %**, ETAPA 04 completada |
| `docs/project-management/ROADMAP.md` | Estado de `Task/015`; columna de repositorios corregida a `frontend, infra (documentación)` |
| `docs/stages/STAGE-04-user-experience.md` | `Task/015` **Aprobada**; etapa **Completada: 3/3 — 100 %**, con limitación visual conservada |
| `docs/architecture/open-decisions.md` | **D-04 Resuelta y Vigente**, por la aprobación de **D-015-E** |
| `docs/task-reports/TASK-015-report.md` | **Creado**, con evidencia de implementación, correcciones y aprobación |

## 14. Archivos esperados

**Crear (frontend):** `src/lib/rutasAdmin.ts`; `src/app/{adminSessionContext.ts,
AdminSessionProvider.tsx, RutaProtegida.tsx, AdminLayout.tsx, AdminLayout.module.css}`;
`src/services/admin/{types.ts, cliente.ts, auth.ts, contenido.ts, posts.ts, bookReviews.ts,
videos.ts, projects.ts, tags.ts, media.ts, profile.ts, index.ts}`;
`src/components/{FormField,FormFeedback}/`; `src/features/markdown/MarkdownEditor.tsx`;
`src/features/media/`; `src/features/admin-content/`; `src/pages/admin/`; y la prueba de cada
uno.

**Modificar (frontend):** `src/app/routes.tsx` (subárbol en diferido antes del comodín);
`src/app/App.tsx` (retirada de `AppConfigContext` si queda sin consumidor, y actualización del
comentario sobre el proveedor de sesión); `src/services/http/httpClient.ts` y su prueba
(**D-015-C**, **D-015-D**); `src/components/index.ts`; `README.md`.

**No tocar:** `src/services/public/**`; `src/app/SiteLayout.tsx` y las once páginas públicas;
`src/entities/**` y `src/features/markdown/{MarkdownContent,MarkdownRenderer,esquema}`;
`src/styles/tokens.css`; `vite.config.ts`; `tsconfig*.json`; `eslint.config.js`; **todo
`personal-blog-backend`**; Terraform, Docker Compose y runbooks de `personal-blog-infra`.

## 15. Resultado de pruebas

Detalle completo en el [reporte](../task-reports/TASK-015-report.md).

| Compuerta | Baseline | Después |
| --- | --- | --- |
| `format:check` · `lint` · `typecheck` | limpio | **limpio** |
| `test:run` | **440 passed**, 61 archivos | **600 passed**, 67 archivos (**+160** respecto de 440; **+43** en la corrección auth) |
| `build` | correcto | **correcto**, con chunk `admin-*` separado |
| Dependencias | 5 + 22 | **idénticas**: `git diff package*.json` vacío |

**RED registrado** en los seis *slices* antes de escribir código productivo. La mutación del
gate **P-05** —un `import` estático del panel desde el grafo público— puso rojas P-05-1 y
P-05-2 y se revirtió por completo.

**Corrección auth (2026-09-05):** 43 pruebas añadidas y una prueba de `429` reemplazada
por la comprobación temporal completa; **79/79** pruebas focalizadas en verde. RED antes
de producción para cabecera, cooldown, submit directo y `/admin`; mutaciones posteriores
detectadas y revertidas. El comando original `npm run test:run` terminó en **600/600**.
El [reporte, sección 12](../task-reports/TASK-015-report.md#12-regresión-final) conserva
también los cinco fallos por plazo de la primera ejecución y las repeticiones sin cambios
de expectativas. Criterio 12: **C = 0**. Avance y bloqueo histórico resuelto sin cambios.

Dos defectos los encontró la suite, no la lectura: las acciones de publicación se dibujaban
con un estado por defecto antes de cargar, y la sincronización de datos en `useEffect`
provocaba renders en cascada. Ambos corregidos.

## 16. Problemas encontrados

1. **`@testing-library/user-event` no está instalado.** Se escribieron las pruebas con
   `fireEvent` + `act`, que es lo que ya usa el resto de la suite: instalarlo habría sido
   una dependencia nueva sin autorización.
2. **`/admin/acceso` no sobrevive al build como literal**, porque `rutasAdmin.ts` lo compone
   con una plantilla. Los marcadores de P-05 son literales que **sí** sobreviven.
3. **Validación visual a cuatro anchos: no ejecutada.** Sin automatización de navegador en
   esta sesión. Declarada como limitación en el reporte §14, con lo que sí se verificó.

## 17. Pasos de validación para el usuario

Comandos exactos y no destructivos en el [reporte](../task-reports/TASK-015-report.md) §17.

## 18. Deuda técnica pendiente

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | ~~Últimos eventos de auditoría en el dashboard~~ — **cerrada**: `Task/012.1`, **Aprobada** el 2026-09-05, entregó `GET /api/v1/admin/audit-events` | — |
| 2 | Insertar imágenes dentro del cuerpo Markdown: exige URL estable (**D-08**) | `Task/030` |
| 3 | El listado administrativo devuelve el `content` completo de cada elemento | Backend, sin propietario asignado |
| 4 | Restringir `provider` en el backend a la lista cerrada de `Task/014` | Backend, candidata `Task/018` |
| 5 | Corregir un `alt_text` ya compartido (**D-012-Z** relajada) | Mejora futura, sin propietario |
| 6 | CORS con credenciales para la topología *cross-origin* de **D-15** | `Task/018` |
| 7 | `noindex` del panel (**E-06**) y código HTTP de la 404 | `Task/016`, `Task/034` |
| 8 | Validación funcional en el navegador con administrador y contenido reales | `Task/022` |

## 19. Próxima tarea

`Task/016-SEO-Accesibilidad-y-Rendimiento`. **No se inicia** hasta que `Task/015` esté
aprobada y la normalización posterior haya concluido.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** — sin bloqueos canónicos activos |
| **Fecha de aprobación** | 2026-09-05 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/015-Panel-Administrativo` |

El usuario emitió la expresión de aprobación el 2026-09-05. **D-015-A** a **D-015-H**,
**D-015-J** y **D-015-K** quedan **Vigentes**; **D-015-I** continúa **retirada**.
**D-04 resuelta**, avance **15/41 — 37 %**, ETAPA 04 **Completada: 3/3 — 100 %**.
El cierre sigue [WORKFLOW §3](../project-management/WORKFLOW.md#3-aprobación-y-cierre);
la fusión hacia `main` corresponde exclusivamente al usuario.
