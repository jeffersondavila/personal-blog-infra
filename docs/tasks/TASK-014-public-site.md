# TASK-014 — Sitio Público

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/014-Sitio-Publico` |
| **Nombre** | Sitio Público |
| **Etapa** | ETAPA 04 — Experiencia del Usuario |
| **Tipo** | Tarea oficial del roadmap. **Cuenta** dentro de las 41. Frontend **funcional** |
| **Estado** | **Aprobada** ✔ el 2026-09-05 por jeffersondavila |
| **Repositorios involucrados** | `personal-blog-frontend` (funcional) · `personal-blog-infra` (gobierno documental) |
| **Repositorio NO modificado** | `personal-blog-backend` — sin rama y sin cambios. Solo lectura de sus esquemas públicos |
| **Dependencias** | `Task/013-Sistema-de-Diseno` — **Aprobada** ✔ (2026-09-04) |
| **Rama** | `Task/014-Sitio-Publico` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base (frontend)** | `af242845a7d390f0ae6b6c0bdb0aece496b70e50` |
| **SHA base (infra)** | `fec55bb82d4832308456bc86e35755228981cf57` |
| **Fecha de inicio** | 2026-09-04 |
| **Última actualización** | 2026-09-05 — aprobada y cerrada |
| **Reporte** | [`TASK-014-report.md`](../task-reports/TASK-014-report.md) |

> **Estado de las decisiones de esta ficha.** Toda decisión marcada **D-014-x** quedó
> **Vigente** el 2026-09-05, al recibirse `approved: Task/014-Sitio-Publico`
> ([`PROJECT_INSTRUCTIONS`](../claude/PROJECT_INSTRUCTIONS.md) §6 y §8).

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

Preflight ejecutado el 2026-09-04 en los **tres** repositorios, tras `git fetch --prune origin`:

| Repositorio | Rama activa | `main == origin/main` | Árbol limpio | `git diff main dev` | `dev..main` | Ramas Task locales / remotas |
| --- | --- | --- | :---: | :---: | :---: | :---: |
| `personal-blog-frontend` | `main` | ✔ `af24284` | ✔ | vacío | `0` | ninguna / ninguna |
| `personal-blog-infra` | `main` | ✔ `fec55bb` | ✔ | vacío | `0` | ninguna / ninguna |
| `personal-blog-backend` | `main` | ✔ `ce166fb` | ✔ | vacío | `0` | ninguna / ninguna |

Creación de la rama, con validación inmediata:

| # | Comprobación | frontend | infra |
| --- | --- | --- | --- |
| 1 | `main == origin/main` antes de crear | ✔ `af24284` | ✔ `fec55bb` |
| 2 | `git status --porcelain` vacío antes de crear | ✔ | ✔ |
| 3 | Rama creada **desde `main`** con `git switch -c` | ✔ | ✔ |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo después | ✔ idénticos | ✔ idénticos |
| 5 | `git rev-list --count main..HEAD` | ✔ `0` | ✔ `0` |

`personal-blog-backend` **no recibe rama**: la tarea no lo modifica. Sus esquemas públicos
(`app/modules/*/presentation/schemas.py`) se leyeron para confirmar el contrato; no se toca
ni un archivo.

---

## 1. Objetivo

Construir el **sitio público** del blog sobre el sistema de diseño de `Task/013` y la API
pública de `Task/009`/`Task/010`: Inicio, Quién soy, Artículos, Reviews de libros, Videos,
Proyectos y laboratorio, Contacto y enlaces, búsqueda básica, filtro por etiqueta y página
404, con estados de carga, vacío y error reales, HTML semántico y texto alternativo en las
imágenes.

Al terminar, un visitante anónimo puede navegar, paginar, filtrar por etiqueta, buscar y leer
todo el contenido **publicado**, en móvil, tableta y escritorio, sin que el sitio quede nunca
en blanco.

## 2. Contexto

La ETAPA 03 cerró el backend completo del MVP. `Task/013` entregó tokens, fundación global
y las cinco primitivas compartidas, y **deliberadamente no construyó páginas**: su ficha
asigna a `Task/014` el HTML semántico de página (**A-02**), el `alt` en el render público
(**A-04**), las rutas y layouts del sitio, la sanitización del render Markdown (**S-03**,
compartida con `Task/015` y `Task/018`) y el favicon (decisión **D-13.6**).

Fuentes que asignan trabajo **por nombre** a `Task/014`, todas verificadas en esta sesión:
[`MVP_SCOPE`](../product/MVP_SCOPE.md) §2, [`USER_FLOWS`](../product/USER_FLOWS.md) A.1–A.11,
[`STAGE-04`](../stages/STAGE-04-user-experience.md),
[`non-functional-requirements`](../architecture/non-functional-requirements.md) (A-01, A-02,
A-04, S-03, S-12, E-01), [`security-boundaries`](../architecture/security-boundaries.md) §5 y
§7 (lista cerrada de proveedores de video, `rel="noopener noreferrer"`),
[`api-contracts`](../architecture/api-contracts.md) §14.9, [`data-model`](../architecture/data-model.md)
§10 (deuda 6), [`ADR-005`](../adr/ADR-005-markdown-content.md) y las fichas de `Task/009`
(deuda 3: presentación de `reading_time_minutes`), `Task/010` (D-010-N) y `Task/012`
(D-012-R: `Task/014` es dueña del render HTML accesible de la imagen).

---

## 3. Dentro del alcance

- [x] Layout del sitio público: cabecera con navegación principal y buscador, `main`, pie.
      Enlace «saltar al contenido».
- [x] Rutas del MVP confirmadas (§6.B): `/`, `/quien-soy`, `/articulos`, `/articulos/:slug`,
      `/reviews`, `/reviews/:slug`, `/videos`, `/proyectos`, `/proyectos/:slug`, `/contacto`,
      `/buscar` y comodín 404.
- [x] Capa `services/public/`: un adaptador por recurso público, sobre el cliente HTTP común,
      sin reenviar parámetros que el contrato no admita.
- [x] Estados **normal, vacío, cargando y error con reintento** en toda página que consume la
      API. El sitio nunca queda en blanco (A.1).
- [x] Paginación (`?page=`) y filtro por etiqueta (`?tag=`) reflejados en la URL (A.2, A.9).
- [x] Búsqueda básica (`/buscar?q=`) sobre `GET /api/v1/search`, con término mínimo de 2
      caracteres y estado «sin resultados» con sugerencias de navegación (A.8).
- [x] Detalles de artículo, review y proyecto con Markdown **renderizado y sanitizado**
      (ADR-005). Biografía de Quién soy por el **mismo pipeline**.
- [x] Imágenes mediante `access_url` con `alt_text`, `width` y `height` del contrato. Nunca
      `object_key`, nunca URL construida, nunca persistida (A-04, api-contracts §12).
- [x] Videos: listado con miniatura, reproducción por *embed* bajo **lista cerrada de
      proveedores** o enlace externo; **cierra** la deuda 6 de `data-model.md` y la
      pregunta abierta de api-contracts §14.9 (A.6).
- [x] Enlaces externos con `rel="noopener noreferrer"` (S-12).
- [x] Página 404 real con enlaces a Inicio y a las secciones principales (A.11); el `404`
      del API por slug muestra esa misma página sin distinguir «no existe» de «no publicado»
      (A.3).
- [x] Accesibilidad propiedad de esta tarea: **A-02** (HTML semántico) y **A-04** (render
      del `alt`), continuación de **A-01** (teclado: solo controles nativos, enlace de salto,
      `aria-current` en navegación) y consumo —sin redefinir— de A-05, A-06 y A-07.
- [x] `<title>` por página como propiedad básica de accesibilidad (WCAG 2.4.2). **No** es
      el SEO de `Task/016` (E-02 a E-08).
- [x] Favicon real del sitio (D-13.6, deuda 4 de `Task/013`) — ver §6.I.
- [x] Extensión de las guardas de `Task/013` a **todo** CSS Module del árbol, para que las
      páginas no puedan saltarse los tokens ni el foco.
- [x] Sustitución de la pantalla provisional de fundación (`HomePage`) por la portada real.
- [x] Pruebas test-first por comportamiento (§7), compuertas de calidad, validación visual
      integral (deuda 5 de `Task/013`) y gate de consola.
- [x] Documentación: ficha, reporte, `STATUS`, `ROADMAP`, `STAGE-04`, cierre documental de
      la lista de proveedores en `api-contracts` §14.9, `data-model` §10 y
      `security-boundaries` §7, README del frontend, runbook local (fila «Frontend»).

## 4. Fuera del alcance

| Queda fuera | Tarea propietaria o motivo |
| --- | --- |
| Panel administrativo, dashboard, editor Markdown, formularios CRUD, carga de imágenes, vista previa, sesión | `Task/015` |
| **A-03** (labels de formularios administrativos) y **A-08** (errores de formulario anunciados) | `Task/015` |
| Editor Markdown concreto (**D-04**) | `Task/015` |
| `title` y `description` SEO, Open Graph, canonical, sitemap, `robots.txt`, datos estructurados, `og:image` estable (**E-02** a **E-08**) | `Task/016` |
| Auditoría formal de accesibilidad, umbrales de rendimiento, *lazy loading* medido (**P-01**, **P-03**), separación de carga del panel (**P-05**) | `Task/016` (P-05 también `Task/015`) |
| Código HTTP `404` real en rutas inexistentes de la SPA y su `noindex` | El *hosting* estático sirve `index.html` con `200`; es de `Task/016` (`robots`/`noindex`) y `Task/034` (Cloudflare Pages) |
| Auditoría de la sanitización, CORS efectivo, cabeceras de seguridad | `Task/018` |
| URL estable de medios, semántica de caché, TTL productivo del `access_url` (**D-08**) | `Task/030` |
| Semilla de perfil y contenido de ejemplo en local | `Task/022` (y `Task/036` en producción). Hasta entonces `GET /profile` responde `404` (D-009-N) y las páginas lo tratan como estado explícito |
| Restricción del `provider` de video en el backend (`CHECK` o validación) y su selector en el panel | Backend fuera de alcance; el panel es `Task/015`. `Task/014` aplica la lista **en el render**, *fail-closed* |
| Derivar la miniatura de un video desde el proveedor cuando no hay `thumbnail` | Deuda registrada (§18). Implica una petición a un tercero en cada listado; no lo pide ningún flujo |
| Formulario de contacto, newsletter, comentarios, modo oscuro, internacionalización | Fuera del MVP (`MVP_SCOPE` §6) o sin fuente canónica |
| Nuevos tokens, variantes de `Button`, primitivas de formulario | `Task/013` cerrada; `Task/015` para formularios. Solo se crea un componente compartido con **dos consumidores reales** dentro de esta tarea |
| Corregir el índice `docs/task-reports/README.md`, que omite `Task/010`–`Task/013` | **Drift preexistente e independiente**, excluido expresamente de `Task/013.1` por decisión del usuario. Se registra como hallazgo en `STATUS.md`; **no se mezcla** aquí |
| `GET /api/v1/videos/{slug}` | **No existe** en el contrato. No se inventa ni se enlaza |
| Cualquier endpoint `/api/v1/admin/*` | El sitio público es anónimo. No se consume |

**No se toca:** backend, Docker Compose, Terraform, AWS, `src/services/http/*`,
`vite.config.ts`, `tsconfig*.json`, `eslint.config.js`. `package.json` y `package-lock.json`
cambian **únicamente** por las dos dependencias que el usuario autorizó el 2026-09-05
(§6.K). Sobre el entorno local solo se ejecutaron operaciones **aditivas y documentadas**:
`alembic upgrade head` dentro del contenedor del backend —la base local estaba en la
revisión `0001` y el API respondía `500`— y la reconstrucción de la imagen del frontend
(`docker compose build frontend && docker compose up -d frontend`). Ningún `down`, ningún
volumen tocado.

---

## 5. Entregables

| Entregable | Repositorio | Ruta prevista |
| --- | --- | --- |
| Layout del sitio y enlace de salto | frontend | `src/app/SiteLayout.tsx` + `.module.css` |
| Tabla de rutas del MVP | frontend | `src/app/routes.tsx` |
| Proveedor del cliente HTTP compartido | frontend | `src/app/httpClientContext.ts` · `src/app/App.tsx` |
| Adaptadores de la API pública y tipos del contrato | frontend | `src/services/public/` |
| Hook de recurso asíncrono (cargando / éxito / error / no encontrado, cancelación) | frontend | `src/hooks/useAsyncResource.ts` |
| Hook de título de documento | frontend | `src/hooks/useDocumentTitle.ts` |
| Formato de fechas | frontend | `src/lib/format/date.ts` |
| Componentes compartidos nuevos: `Pagination`, `ExternalLink`, `LoadingState`, `EmptyState`, `ErrorState` | frontend | `src/components/<Nombre>/` y `src/components/index.ts` |
| Componentes de entidad: `MediaImage`, `PublishedDate`, `TagLinks`, `Rating`, `ProjectStatusBadge`, `PostCard`, `ReviewCard`, `ProjectCard`, `VideoCard`, proveedores de video | frontend | `src/entities/{media,content,tags,book-reviews,projects,posts,videos}/` |
| Render Markdown sanitizado (pipeline único, reutilizable por `Task/015`) | frontend | `src/features/markdown/MarkdownContent.tsx` |
| Páginas | frontend | `src/pages/{Home,About,Posts,PostDetail,BookReviews,BookReviewDetail,Videos,Projects,ProjectDetail,Contact,Search,NotFound}Page.tsx` |
| Favicon | frontend | `public/favicon.svg` · `index.html` |
| Guardas extendidas | frontend | `src/styles/designSystem.guards.test.ts` |
| Ficha | infra | `docs/tasks/TASK-014-public-site.md` |
| Reporte | infra | `docs/task-reports/TASK-014-report.md` |
| Estado y avance | infra | `STATUS.md`, `ROADMAP.md`, `STAGE-04-user-experience.md` |
| Cierre documental de la lista de proveedores de video | infra | `api-contracts.md` §14.9 · `data-model.md` §10 · `security-boundaries.md` §7 |

---

## 6. Matriz funcional — decision gate

> Esta sección se completó **antes** de escribir código productivo. Todo lo que sigue está
> derivado de las fuentes canónicas; donde una fuente deja la decisión a `Task/014`, se dice
> y se decide aquí como **Propuesta**.

### 6.A Fuentes canónicas y la regla concreta que imponen

| Fuente | Regla o alcance que impone a `Task/014` |
| --- | --- |
| `CLAUDE.md` · `PROJECT_INSTRUCTIONS.md` | Rama desde `main`; una sola tarea; sin commit/push/PR antes de `approved:`; decisiones como *Propuesta*; español en documentación; no tocar repos fuera del alcance |
| `WORKFLOW.md` | Ciclo de vida: marcar `En progreso` en `STATUS` y `ROADMAP` al iniciar; ficha desde la plantilla; reporte al terminar; §6.1: nada de estado transitorio de Git como estado vigente |
| `STATUS.md` | `Task/014` es la siguiente; `Task/013` cerrada; deuda heredada: `VisuallyHidden`/`IconButton` solo con consumidor real, favicon, validación visual integral. Avance 13/41, ETAPA 04 1/3: **no cambian** hasta la aprobación |
| `ROADMAP.md` | Fila `Task/014`: «Inicio. Quién soy. Artículos. Reviews. Videos. Proyectos. Contacto. Página 404», repo `frontend`, depende de `013` |
| `DEFINITION_OF_DONE.md` | Tareas de frontend: lint, type-check, tests, `build`, **sin errores de consola** en las rutas afectadas; criterios 11 (SHA base en la ficha) y 12 (sin estado transitorio) |
| `STAGE-04` | Criterios de salida que esta tarea debe hacer verdaderos: «todas las secciones previstas son navegables», «se ve correctamente en móvil, tableta y escritorio», «la página 404 funciona». Fuera de la etapa: SEO/OG, auditoría formal, rendimiento, despliegue |
| `MVP_SCOPE.md` §2 | Las diez secciones y sus rutas **propuestas** —«se confirman en `Task/014`»—; detalle de proyecto **se decide en `Task/014`**; capacidades: publicado únicamente, slugs, paginación, filtro por etiqueta, búsqueda básica, destacados en Inicio, fechas, imágenes, enlaces externos seguros, videos por enlace o *embed*, responsive. §2.3: solo lectura, sin código del panel, sin identificadores internos. §4: contacto **sin formulario** |
| `USER_FLOWS.md` A.1–A.11 | Datos exactos por flujo (tabla §6.C); A.1 error con reintento; A.2 vacío con mensaje; A.3 `404` indistinguible → página 404; A.6 *embeds* limitados a proveedores permitidos y `rel="noopener noreferrer"`; A.8 mínimo 2 caracteres y sugerencias sin resultados; A.9 filtro en la URL; A.10 `mailto:` y redes; A.11 404 con enlaces |
| `CONTENT_MODEL.md` | Campos conceptuales por tipo; §3.4: «la lista [de proveedores] se cierra en `Task/014`»; `rating` 1..5; `project_status` ≠ `status`; `Profile` siempre visible y singleton |
| `api-contracts.md` | Los **diez** recursos públicos (§3); paginación 12/50 y envoltura (§5); `tag`, `featured`, `sort` cerrados, **parámetros desconocidos → `422`** (§6); modelo de error (§7); `access_url` temporal, nunca `object_key` (§12); §14.9: proveedores de video → `Task/014` |
| `software-architecture.md` §4 | Estructura `app/pages/features/entities/components/services/hooks/lib`; dependencias `pages → features → entities → components`; **solo `services` habla HTTP**; `components` sin dominio; URL del API por variable de build; D-03 vigente |
| `non-functional-requirements.md` | Propiedad de `Task/014`: **A-02**, **A-04** (con `Task/010`), **A-01** (continuación), **S-03** (con 015/018), **S-12**, **E-01**. **No** son suyas: A-03, A-08, E-02..E-08, P-01..P-05 |
| `security-boundaries.md` §5, §7 | XSS del Markdown → sanitización; *embeds* → lista cerrada; enlaces → `rel="noopener noreferrer"`; el frontend **nunca** posee claves de MinIO/S3; C-03 no es límite de seguridad |
| `open-decisions.md` | Ninguna D-xx tiene a `Task/014` como propietaria. **D-03** resuelta (sin biblioteca visual; una dependencia futura debe **justificarse**); **D-04** es de `Task/015`; **D-08** sigue abierta (`Task/030`) |
| `ADR-005` | Markdown se renderiza **en el frontend**, **siempre sanitizado**, con lista de permitidos; sin HTML libre; **mismo pipeline** que la vista previa de `Task/015`; carga diferida del renderizador donde aplique |
| Ficha y reporte `Task/009` | DTO campo a campo (§7.4); `Video` **solo listado**; `featured` no se expone (se filtra); `q` 2..100; `/tags` solo etiquetas con contenido publicado; deuda 3: `reading_time_minutes` lo presenta `Task/014`; D-009-C: **el frontend no reenvía parámetros ajenos** |
| Ficha y reporte `Task/010` | `access_url` es el único campo de acceso, temporal (TTL por configuración, 900 s por defecto), consumible desde el navegador del host; D-010-N: `alt_text` puede ser nulo al cargar |
| Ficha y reporte `Task/012` | D-012-R: al **publicar** se exige `alt_text` en portada/miniatura y el perfil lo exige al editar → todo contenido público con imagen trae `alt_text`; `Task/014` es dueña del render HTML accesible. `provider` se exige presente, **no** perteneciente a una lista |
| Ficha y reporte `Task/013` | Superficie pública `src/components/index.ts`; sin `Link`/`Heading`/`Text`; `Container` (`prose`/`wide`), `Stack`, `Button` (`primary`/`secondary`), `Card`, `Badge` (4 tonos); breakpoints `--breakpoint-md`/`lg` como contrato (literal repetido y citado); D-13.6 favicon → `Task/014`; guardas solo cubren `src/components` |
| `Task/013.1` | Solo estado documental. El drift del índice de reportes queda **fuera** de `Task/014` por decisión del usuario |

### 6.B Rutas confirmadas — **D-014-A**

| # | Sección | Ruta | Fuente | Nota |
| --- | --- | --- | --- | --- |
| 1 | Inicio | `/` | MVP_SCOPE §2.1 | Sustituye a la pantalla provisional de fundación |
| 2 | Quién soy | `/quien-soy` | ídem | |
| 3 | Artículos | `/articulos` | ídem | `?page=`, `?tag=` |
| 4 | Detalle de artículo | `/articulos/:slug` | ídem | |
| 5 | Reviews | `/reviews` | ídem | `?page=`, `?tag=` |
| 6 | Detalle de review | `/reviews/:slug` | ídem | |
| 7 | Videos | `/videos` | ídem | `?page=`, `?tag=`. **Sin detalle**: no existe `GET /videos/{slug}` |
| 8 | Proyectos | `/proyectos` | ídem | `?page=`, `?tag=` |
| 9 | Detalle de proyecto | `/proyectos/:slug` | MVP_SCOPE §2.1 lo deja a `Task/014` | **Se implementa**: `content` Markdown es **obligatorio para publicar** un proyecto (api-contracts §14.5), luego todo proyecto publicado tiene profundidad que mostrar; el DTO detallado y `reading_time_minutes` ya existen |
| 10 | Contacto | `/contacto` | MVP_SCOPE §2.1 | |
| 11 | Búsqueda | `/buscar?q=` | USER_FLOWS A.8; MVP_SCOPE §2.2 «búsqueda básica» y §7.8 | No aparece en la tabla de rutas de §2.1 pero sí como capacidad del sitio público; el buscador vive en la cabecera y esta ruta muestra sus resultados |
| 12 | 404 | `*` | MVP_SCOPE §2.1; A.11 | El comodín sigue siendo la **última** ruta |

`/__design-system` **se conserva** tal cual: registrada solo en desarrollo, ausente del build.

### 6.C Inventario funcional por página

| Página | Ruta | Endpoint(s) | Estado normal | Vacío | Cargando | Error | Responsive | Accesibilidad |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Inicio | `/` | `GET /profile` · `GET /posts?featured=true&page_size=3` · ídem `/book-reviews`, `/videos`, `/projects` | Presentación (nombre, titular, foto) + una sección por tipo con destacados + accesos a secciones | Sección sin destacados: texto «Todavía no hay X destacados» y enlace a la sección. Perfil `404`: se omite el bloque de presentación | Por bloque, `role="status"` | Por bloque, con **Reintentar** (A.1). Nunca en blanco | `Container wide`; rejilla `auto-fit` | `h1` único; `section` con `h2`; landmarks del layout |
| Quién soy | `/quien-soy` | `GET /profile` | Nombre, titular, foto (`alt_text`), biografía **Markdown sanitizado** | Perfil `404`: «El perfil aún no está disponible» | `role="status"` | Reintentar | `Container prose` | `h1` = nombre; `article` |
| Artículos | `/articulos` | `GET /posts?page&tag` (+ `GET /tags?page_size=50` para el filtro) | Tarjetas: título (enlace), resumen, fecha, portada, etiquetas; paginación | «Todavía no hay artículos publicados» (o «con la etiqueta X», con enlace a quitar el filtro) | `role="status"` | Reintentar | `wide`; rejilla `auto-fit` | `h1`; lista `ul > li > article`; `nav` de paginación con `aria-current` |
| Detalle de artículo | `/articulos/:slug` | `GET /posts/{slug}` | Título, fecha, tiempo de lectura, portada, etiquetas, contenido Markdown sanitizado | — | `role="status"` | `404` → página 404 (A.3); otro error → Reintentar | `prose` | `article`; `h1` = título; los `h*` del Markdown se renderizan a partir de `h2` |
| Reviews | `/reviews` | `GET /book-reviews?page&tag` (+ `/tags`) | Igual que artículos + libro, autor y valoración | ídem | ídem | ídem | ídem | Valoración con **texto** («4 de 5»); glifos `aria-hidden` |
| Detalle de review | `/reviews/:slug` | `GET /book-reviews/{slug}` | + `book_title`, `book_author`, `rating`, `external_link` (`rel="noopener noreferrer"`) | — | ídem | ídem | `prose` | ídem |
| Videos | `/videos` | `GET /videos?page&tag` (+ `/tags`) | Tarjetas: título, resumen, miniatura, fecha, duración; **Reproducir** carga el *embed* si el proveedor está permitido; enlace externo siempre | ídem | ídem | ídem | `wide`; `iframe` con `aspect-ratio` | Botón nativo; `iframe` con `title`; proveedor no permitido → solo enlace |
| Proyectos | `/proyectos` | `GET /projects?page&tag` (+ `/tags`) | Tarjetas: título, resumen, tecnologías, estado del trabajo (`Badge` con texto), enlaces repo/demo | ídem | ídem | ídem | `wide` | Estado con texto, no solo color |
| Detalle de proyecto | `/proyectos/:slug` | `GET /projects/{slug}` | + contenido Markdown, tiempo de lectura | — | ídem | `404` → 404 | `prose` | `article` |
| Contacto | `/contacto` | `GET /profile` | `mailto:` del correo y lista de redes (`rel="noopener noreferrer"`) | Perfil `404`: «Los datos de contacto aún no están disponibles» | ídem | Reintentar | `prose` | `h1`; lista `ul` de enlaces |
| Búsqueda | `/buscar?q=` | `GET /search?q&page` | Resultados planos con tipo (`Badge` neutro), título (enlace al detalle o a `/videos#slug`), resumen, fecha; paginación | «Sin resultados para “X”» + enlaces a secciones (A.8) | ídem | Reintentar | `wide` | Formulario en cabecera con `label` visible; `h1` refleja el término; `q` < 2 no llama al API |
| 404 | `*` y `404` de slug | — | Mensaje + enlaces a Inicio y a las seis secciones | — | — | — | `prose` | `h1` con «404»; `title` propio |

### 6.D Contratos API consumidos

Base: `${VITE_API_BASE_URL}/api/v1`. Solo `GET`. Solo estos parámetros; **ningún otro** se
reenvía (D-009-C: un parámetro desconocido produce `422`).

| Método y ruta | Propósito en `Task/014` | DTO (backend) | Parámetros usados | Media | Errores relevantes |
| --- | --- | --- | --- | --- | --- |
| `GET /profile` | Inicio, Quién soy, Contacto | `ProfilePublico`: `full_name`, `headline`, `biography` (Markdown), `contact_email`, `photo`, `seo_*`, `social_links[{label,url}]` | — | `photo` | `404 resource_not_found` sin semilla (D-009-N) → estado explícito, no crash |
| `GET /posts` | Listado, destacados de Inicio | `Pagina<PostDeListado>`: `slug`, `title`, `summary`, `published_at`, `tags[]`, `cover` | `page`, `tag`, `featured=true`, `page_size` (solo en Inicio) | `cover` | `422` si algún parámetro es inválido (no debe ocurrir) |
| `GET /posts/{slug}` | Detalle | `PostDetallado` = listado + `content`, `reading_time_minutes`, `seo_*` | — | `cover` | `404` → página 404, **sin distinguir** borrador de inexistente |
| `GET /book-reviews` | Listado, destacados | `ReviewDeListado` = post + `book_title`, `book_author`, `rating` | ídem posts | `cover` | ídem |
| `GET /book-reviews/{slug}` | Detalle | `ReviewDetallada` + `external_link` | — | `cover` | `404` |
| `GET /videos` | Listado, destacados | `VideoDeListado`: + `thumbnail`, `provider`, `video_url`, `embed_reference`, `duration_seconds` | ídem posts | `thumbnail` | ídem. **No hay detalle** |
| `GET /projects` | Listado, destacados | `ProyectoDeListado`: + `technologies[]`, `repository_url`, `demo_url`, `project_status` (`active`/`paused`/`completed`) | ídem posts | `cover` | ídem |
| `GET /projects/{slug}` | Detalle | `ProyectoDetallado` + `content`, `reading_time_minutes` | — | `cover` | `404` |
| `GET /tags` | Filtro por etiqueta en los cuatro listados | `Pagina<EtiquetaPublica>`: `slug`, `name`, `description` | `page_size=50` (máximo del contrato) | — | Solo etiquetas con contenido publicado (D-009-I) |
| `GET /search` | Búsqueda | `Pagina<ResultadoDeBusqueda>`: `type` (`post`/`book_review`/`video`/`project`), `slug`, `title`, `summary`, `published_at` | `q` (2..100), `page` | — | `422` si `q` inválido: el frontend no llama con `q` < 2 |

Envoltura de colección, idéntica en todos: `{ items, page, page_size, total, pages }`.
Modelo de error: `{ error: { code, message, details, request_id } }`, ya traducido por
`HttpError` (`kind`, `status`, `code`).

**Endpoints que NO existen y no se inventan:** `GET /api/v1/videos/{slug}`. **Endpoints que
existen y NO se consumen:** todo `/api/v1/admin/*`, `/health`, `/ready`.

### 6.E Media — reglas de consumo (**D-014-B**)

| Regla | Cómo se cumple |
| --- | --- |
| Usar `access_url` y solo `access_url` | `MediaImage` recibe `MedioPublico` y emite `<img src={access_url} alt={alt_text} width height>`. Sin `object_key` en ningún tipo del frontend |
| No construir URL hacia MinIO/S3 | Ningún módulo conoce endpoint, bucket ni clave. Prueba: el árbol no contiene `object_key` ni `X-Amz` |
| No persistir `access_url` | Sin `localStorage`, sin caché entre navegaciones; cada visita vuelve a pedir el recurso |
| No asumir permanencia | El TTL es configuración del backend (900 s por defecto). Registrado como riesgo: una pestaña abierta más tiempo que el TTL muestra imágenes rotas hasta recargar; la política es de **D-08** |
| Renderizar `alt_text` del contrato (**A-04**) | Contenido publicado siempre lo trae (D-012-R). Si llegara `null`, la imagen se trata como **decorativa** (`alt=""`); nunca se inventa un texto |
| `access_url` `null` con medio presente | No se renderiza `<img>`; se registra como caso probado |
| Reservar espacio | `width` y `height` del contrato en el `<img>`; CSS `max-width: 100%; height: auto` ya viene de la fundación |

### 6.F Videos — lista cerrada de proveedores (**D-014-C**)

`CONTENT_MODEL` §3.4 nombra un único ejemplo, **YouTube**. La lista inicial cerrada es:

| `provider` | *Embed* | Forma admitida de `embed_reference` |
| --- | --- | --- |
| `youtube` | `https://www.youtube-nocookie.com/embed/{id}` | `^[A-Za-z0-9_-]{11}$` |
| `vimeo` | `https://player.vimeo.com/video/{id}` | `^[0-9]{6,12}$` |

Reglas: comparación de `provider` en minúsculas; `embed_reference` que no cumpla el patrón
**no** produce `iframe`; proveedor fuera de la lista → solo enlace externo a `video_url`
(*fail-closed*). El `iframe` se crea **al pulsar Reproducir** (A.6 «al seleccionar uno»), con
`title` = título del video, `allowfullscreen`, `loading="lazy"` y `referrerpolicy=
"strict-origin-when-cross-origin"`. Sin miniatura: superficie de tarjeta con el título y el
botón; no se deriva la miniatura del proveedor (§4). El backend sigue aceptando cualquier
cadena en `provider`; restringirlo allí y ofrecer el selector en el panel queda registrado
como deuda (§18).

### 6.G Componentes — clasificación

**A. Ya existen (Task/013) — se consumen desde `src/components/index.ts`**

| Primitiva | Uso en `Task/014` |
| --- | --- |
| `Container` | `prose` en detalles, Quién soy, Contacto, 404; `wide` en Inicio, listados y búsqueda |
| `Stack` | Toda separación vertical y horizontal; `wrap` en etiquetas, navegación y acciones |
| `Button` | `primary`: **Reintentar** en `ErrorState`; `secondary`: **Reproducir** en `VideoCard`, «Quitar filtro» |
| `Card` | Elemento de listado de los cuatro tipos; bloque de destacados |
| `Badge` | Etiquetas (`neutral`), tipo de resultado de búsqueda (`neutral`), `project_status` (`success`/`warning`/`neutral`) |

**B. Nuevos compartidos — cada uno con al menos dos consumidores reales en esta tarea**

| Componente | Dónde | Consumidores | Por qué no existe ya |
| --- | --- | --- | --- |
| `Pagination` | `src/components/Pagination/` | 4 listados + búsqueda | Composición de página en `Task/013` (§6.C de su ficha). Enlaces `<a>` con `?page=` —la página es estado de URL compartible—, `nav aria-label`, `aria-current="page"`, `rel="prev"/"next"` |
| `ExternalLink` | `src/components/ExternalLink/` | `external_link` de review, repo/demo de proyecto, redes de contacto, enlace del video | Garantiza **S-12** en un solo sitio. Sin dominio |
| `LoadingState`, `EmptyState`, `ErrorState` | `src/components/` | Todas las páginas con datos | `role="status"` / texto + acción. `ErrorState` recibe `onRetry` y usa `Button` |
| `MediaImage` | `src/entities/media/` | Tarjetas de los cuatro tipos, portada de detalle, foto del perfil | Conoce `MedioPublico`: es de `entities`, no de `components` (**D-014-B**) |
| `PublishedDate` | `src/entities/content/` | Tarjetas, detalles, resultados | `<time dateTime>` con formato `es` desde `lib/format/date.ts` |
| `TagLinks` | `src/entities/tags/` | Tarjetas y detalles | `Badge` dentro de un enlace al listado filtrado del **mismo tipo** (A.9) |
| `PostCard`, `ReviewCard`, `ProjectCard`, `VideoCard` | `src/entities/<tipo>/` | Su listado + destacados de Inicio | Dos consumidores cada una; viven junto a su entidad |
| `Rating` | `src/entities/book-reviews/` | `ReviewCard`, detalle de review | Texto «N de 5» siempre; glifos `aria-hidden` (**A-07**) |
| `ProjectStatusBadge` | `src/entities/projects/` | `ProjectCard`, detalle de proyecto | Mapa cerrado `active`→`success` «Activo», `paused`→`warning` «En pausa», `completed`→`neutral` «Terminado» |
| Proveedores de video (función pura) | `src/entities/videos/providers.ts` | `VideoCard` y sus pruebas | **D-014-C**. Puro y probado exhaustivamente |
| `MarkdownContent` | `src/features/markdown/` | Detalle de artículo, review, proyecto y Quién soy; `Task/015` (vista previa) | **S-03**, ADR-005. Depende de la propuesta de dependencia §6.J |
| `useAsyncResource` | `src/hooks/` | Todas las páginas | `AbortController`, guarda `aborted`, estados `cargando/exito/error/no-encontrado`, `reintentar()`. Generaliza el patrón ya probado de la pantalla de fundación |
| `useDocumentTitle` | `src/hooks/` | Todas las páginas | Título por página, sufijo estático «Blog personal» (el de `index.html`) |
| `SiteLayout` + `SkipLink` | `src/app/` | Ruta *layout* de todas las páginas públicas | Cabecera (`header > nav` con `NavLink` y `aria-current`, formulario de búsqueda), `main id="contenido"`, `footer`. `SkipLink` es **específico del layout**: un solo consumidor, vive dentro de él |
| `HttpClientContext` + `useHttpClient` | `src/app/` | `services` desde cualquier página | La pantalla de fundación lo memorizaba localmente «hasta que haya más de un consumidor»: ahora hay once |

**C. Específicos de página — viven junto a su página, no se elevan**

Bloque de presentación de Inicio, sección de destacados por tipo, cabecera de detalle
(título, fecha, tiempo de lectura, portada), aviso de filtro activo con «Quitar filtro»,
lista de sugerencias de la búsqueda vacía, lista de secciones de la 404.

**No se crean**, por falta de consumidor demostrado: `VisuallyHidden` (todos los textos de
estado son visibles), `IconButton`, `Divider`, `Heading`, `Text`, `Link`, `Input`,
`FormField`, `ValidationMessage`. El único campo de formulario —el buscador— usa `<label>`
visible e `<input type="search">` nativos; A-03/A-08 siguen siendo de `Task/015`.

### 6.H Accesibilidad — qué asume esta tarea

| Criterio | Estado previo | Responsabilidad `Task/014` | Evidencia prevista |
| --- | --- | --- | --- |
| **A-01** Teclado | Iniciado en `Task/013` (primitivas nativas) | **Continúa**: solo `<a>`, `<button>`, `<input>` nativos; enlace de salto; orden de tabulación natural; `aria-current` | Pruebas de roles/nombres accesibles; validación manual con Tab en el navegador |
| **A-02** HTML semántico | No iniciado | **Asume**: `header`, `nav`, `main`, `footer`, `article`, `section`, `ul/li`, `time`; un `h1` por página; jerarquía sin saltos; Markdown desde `h2` | Pruebas por página: `getByRole('main')`, `heading level 1` único, lista presente |
| **A-04** Texto alternativo | Columna y contrato (`Task/010`); exigencia al publicar (`Task/012`) | **Asume el render**: `alt` del contrato en cada `<img>`; `null` → decorativa | Pruebas de `MediaImage` y de cada tarjeta/detalle |
| **A-05** Contraste · **A-06** Foco · **A-07** Color | Asumidos por `Task/013` | **Consume sin redefinir**: sin colores literales, sin `outline`, sin `:focus-visible` propio; texto siempre junto al color | Guardas extendidas a todo `*.module.css` del árbol |
| **A-03** · **A-08** Formularios | — | **No** (`Task/015`) | — |
| WCAG 2.4.2 título de página | — | `<title>` por página, básico | Prueba de `document.title` por página |
| **S-12** Enlaces externos | — | **Asume** vía `ExternalLink` | Prueba: todo enlace externo lleva `rel="noopener noreferrer"` |
| **S-03** Sanitización | — | **Asume el render público** (con `Task/015` y `Task/018`) | Pruebas de `MarkdownContent`: `<script>`, `<iframe>`, `on*`, `javascript:` neutralizados |

**Afirmación permitida:** las páginas usan HTML semántico y los controles nativos que
`Task/013` estiló. **No** se afirma que el producto cumpla WCAG AA: la auditoría es `Task/016`.

### 6.I Responsive (**D-014-D**)

Estrategia **intrínseca**, heredada: `Container` + `clamp` para el gutter, rejillas
`repeat(auto-fit, minmax(16rem, 1fr))` para tarjetas, `Stack wrap` para navegación,
etiquetas y acciones, `aspect-ratio: 16 / 9` para el *embed*, `max-width: 100%` en medios
(fundación). **Objetivo medible:** `scrollWidth == clientWidth` en 320, 390, 768 y 1280 px.

Solo se admite una media query de ancho si una composición de página lo exige de verdad
—candidata: colocar la navegación en una línea con el buscador a partir de
`--breakpoint-md`—; en ese caso el literal `48rem` se repite y se cita el token como origen,
como documenta `tokens.css`. La guarda R-03 sigue prohibiéndolas en `src/components`.

### 6.J Favicon (**D-014-E**, pendiente de insumo del usuario)

| Pregunta | Hallazgo |
| --- | --- |
| ¿Qué se espera? | «Icono real del sitio» (`Task/013` D-13.6 y deuda 4 de `STATUS`). `index.html` hoy declara `href="data:,"` para evitar el `404` de `/favicon.ico` |
| ¿Existe un asset? | **No.** Ningún repositorio contiene un icono; `personal-blog-frontend` no tiene carpeta `public/` |
| ¿Requisitos de marca? | **Ninguno.** `Task/013` §6.A: «ninguna fuente canónica define marca, paleta corporativa ni familia tipográfica» |
| ¿Solo integración? | La integración es trivial (`public/favicon.svg` + `<link rel="icon" type="image/svg+xml">`). Lo que falta es **la imagen** |

**Resuelto el 2026-09-05:** el usuario autorizó el **favicon SVG neutro provisional**.
`public/favicon.svg` es un cuadrado de esquinas redondeadas en `#12467f`
(`--color-interactive`) con un anillo en `#ffffff` (`--color-text-on-interactive`); sin
iniciales, nombre ni tipografía. Los valores van escritos en el asset porque un SVG externo
**no hereda** las Custom Properties de la aplicación: son literalmente los de `tokens.css`,
y una prueba (`src/app/favicon.test.ts`) comprueba que cada color del SVG existe en
`tokens.css`, que `index.html` lo enlaza y que ya no queda el recurso vacío `data:,`. Es
**reemplazable** cuando exista identidad visual real.

### 6.K Dependencias — propuesta, **no instalada** (**D-014-F**)

**Consumidor real:** `MarkdownContent`, con cuatro consumidores en esta tarea —detalle de
artículo, de review, de proyecto y biografía— y un quinto ya asignado (vista previa de
`Task/015`, que ADR-005 exige que sea **el mismo pipeline**).

**Por qué la plataforma no lo resuelve:** el navegador no tiene analizador de Markdown; un
analizador propio sería una superficie de XSS escrita a mano, justo lo que ADR-005 quiere
evitar. La `Sanitizer API` del navegador no tiene soporte universal comprobable desde este
entorno y no cubre el análisis de Markdown. D-03 lo contempla: *«no prohíbe una dependencia
futura para un problema puntual que la plataforma no resuelva: obliga a justificarla»*.

Versiones publicadas consultadas el 2026-09-04 con `npm view` (solo lectura, nada instalado):

| Opción | Paquetes | Cómo cumple ADR-005 | Coste |
| --- | --- | --- | --- |
| **A — recomendada** | `react-markdown@10.1.0` + `rehype-sanitize@6.0.0` | Renderiza a **elementos React**, sin `innerHTML`. El HTML crudo del Markdown **no se renderiza** por defecto (decisión 5). `rehype-sanitize` aplica un **esquema de permitidos** explícito (decisión 4) y neutraliza `javascript:`. Mismo pipeline reutilizable en `Task/015` | ~53 KB + ~21 KB desempaquetados más el árbol `unified/remark/rehype` (transitivo, se medirá al instalar). Se carga **diferido** con `React.lazy`, como pide ADR-005 |
| B | `marked@18.0.11` + `dompurify@3.4.14` | HTML como cadena, sanitizado por DOMPurify y montado con `dangerouslySetInnerHTML` | DOMPurify es el sanitizador de referencia, pero reintroduce el camino `innerHTML` y pesa 1.8 MB desempaquetado (variantes de distribución) |
| C | `markdown-it@15.0.1` + `dompurify` | Igual que B | Igual que B, ~2 MB desempaquetado |

`remark-gfm@4.0.1` (tablas, tachado) **no se propone**: ADR-005 enumera encabezados, listas,
enlaces, imágenes y bloques de código; añadir GFM es ampliar el alcance sin fuente.

**Estado: autorizada por el usuario el 2026-09-05** (opción A) e instalada con versión
exacta: `react-markdown@10.1.0` y `rehype-sanitize@6.0.0`, las **únicas** dos líneas que
cambian en `package.json`. No se instaló `remark-gfm`, `rehype-raw`, `marked`, `dompurify`
ni `markdown-it`. Implementación: `src/features/markdown/` —`esquema.ts` (permitidos y
protocolos), `MarkdownRenderer.tsx` (pipeline) y `MarkdownContent.tsx` (carga diferida con
`React.lazy`)—. El renderizador sale del build como *chunk* aparte (`MarkdownRenderer-*.js`,
121,6 kB / 37,1 kB gzip), que solo descargan las cuatro superficies con Markdown.

### 6.L Otras decisiones de esta fase (Propuestas)

| # | Decisión | Alternativas | Justificación |
| --- | --- | --- | --- |
| **D-014-G** | Retirar `src/services/health/` y la pantalla provisional de fundación al construir la portada real | Conservar el servicio sin consumidor | Su único consumidor desaparece; una capa sin uso contradice **M-06**. El criterio de salida de la ETAPA 02 que cerró (`Task/007`) es historia aprobada y no depende de que el código siga vivo. El *healthcheck* del contenedor del frontend usa `wget /`, no este servicio |
| **D-014-H** | Estado de página en la URL: `?page=`, `?tag=`, `?q=`; ningún estado de listado en memoria | Estado en React | A.9 exige que el filtro sea compartible; la paginación por enlaces es navegación (**D-13.5**: navegar es enlace, no botón) |
| **D-014-I** | `page_size` **no se envía** en listados (12 por defecto del contrato); solo en Inicio (`3`) y `/tags` (`50`) | Enviar siempre | Menos superficie ante D-009-C; los valores por defecto ya están cerrados en `Task/009` |
| **D-014-J** | Resultado de búsqueda de tipo `video` enlaza a `/videos#<slug>`; cada `VideoCard` lleva `id={slug}` | Enlazar a `/videos` sin ancla; inventar detalle | No existe `GET /videos/{slug}`. El ancla lleva al visitante a la tarjeta sin inventar una ruta |
| **D-014-K** | `GET /profile` `404` se trata como **estado explícito de página**, no como página 404 | Página 404; `throw` | La ruta existe; lo que falta es la semilla (D-009-N). Desaparece con `Task/022` |
| **D-014-L** | Enlaces externos abren en la **misma pestaña**, con `rel="noopener noreferrer"` siempre | `target="_blank"` | Abrir pestañas nuevas sin aviso es un problema de accesibilidad conocido; S-12 se cumple igual |
| **D-014-M** | Guardas de `Task/013` extendidas a **todo** `src/**/*.module.css`; excepción explícita y probada: las media queries de ancho permitidas fuera de `src/components` cuando citen el token | Guardar solo `components` | Sin la extensión, una página podría pegar un color literal sin que la suite lo detecte |
| **D-014-N** | Guardas ligeras de forma en `services/public`: la envoltura `Pagina` debe traer `items` como arreglo; si no, `HttpError('invalid_response')` | Biblioteca de validación de esquemas; confiar a ciegas | Misma postura que `Task/007`: sin dependencia para validar; se comprueba lo mínimo que evita una excepción en render |

---

## 7. TDD / Plan test-first

> `Task/014` es **frontend**. La
> [BACKEND TEST-FIRST LAW](../project-management/BACKEND_TESTING_STRATEGY.md) **no aplica**
> como regla de `pytest`, pero se trabaja **comportamiento por comportamiento**, con
> RED demostrado antes de cada implementación, como hizo `Task/013`.

### 7.1 Dónde la prueba tiene señal real

| Sí se prueba (Vitest + Testing Library, `fetch` inyectado, sin red) | No se prueba en JSDOM, y cómo se cubre |
| --- | --- |
| URL exacta y parámetros de cada adaptador; que **no** se envían parámetros ajenos | Layout real, `clamp`, rejillas → validación visual en Chrome a cuatro anchos |
| Estados cargando / vacío / error / reintento / no encontrado por página | Que el anillo de foco «se note» → inspección manual con Tab |
| Cancelación al desmontar (patrón ya probado en la pantalla de fundación) | Reproducción real del *embed* → comprobación manual |
| Roles, nombres accesibles, landmarks, un `h1`, `aria-current`, `document.title` | Comportamiento del *hosting* ante rutas profundas → ya cubierto por `nginx.conf` de `Task/007` |
| `<img>` con `src=access_url`, `alt`, `width`, `height`; ausencia de `object_key` | |
| Sanitización: `<script>`, `<iframe>`, atributos `on*`, `javascript:` no llegan al DOM | |
| Proveedores de video: lista cerrada, patrones de `embed_reference`, *fail-closed* | |
| Enlaces externos con `rel="noopener noreferrer"` | |
| Rutas: las doce registradas, comodín último, `/__design-system` solo en DEV | |
| Guardas del sistema sobre todo CSS Module del árbol | |

### 7.2 Matriz de comportamiento

**Servicios (`src/services/public/*.test.ts`)**

| # | Comportamiento | Verificación |
| --- | --- | --- |
| SV-01 | Cada adaptador pide la ruta exacta bajo `/api/v1` | URL capturada del `fetch` inyectado |
| SV-02 | `page` y `tag` se serializan solo cuando existen; `featured=true` y `page_size=3` en destacados; `page_size=50` en `/tags` | `searchParams` |
| SV-03 | Nunca aparece un parámetro fuera de la lista del contrato | Conjunto exacto de claves |
| SV-04 | `q` se envía tal cual, recortado; la capa superior no llama con menos de 2 caracteres | Prueba del servicio y de la página |
| SV-05 | Un `404` se propaga como `HttpError` con `status 404` y `code resource_not_found` | Rechazo tipado |
| SV-06 | Envoltura sin `items` arreglo → `HttpError('invalid_response')` (**D-014-N**) | Rechazo tipado |

**Hooks (`useAsyncResource`, `useDocumentTitle`)**

| # | Comportamiento | Verificación |
| --- | --- | --- |
| HK-01 | `cargando → exito` con los datos | Estado observado |
| HK-02 | `cargando → error` con mensaje genérico, sin cuerpo crudo | Estado observado; ausencia de texto interno |
| HK-03 | `404` → `no-encontrado`, distinto de `error` | Estado observado |
| HK-04 | Desmontar aborta la petición y no actualiza estado | `signal.aborted`, sin cambio |
| HK-05 | `reintentar()` vuelve a `cargando` y repite la petición | Contador de llamadas |
| HK-06 | El título se fija al montar y se restaura al desmontar | `document.title` |

**Componentes compartidos**

| # | Comportamiento | Verificación |
| --- | --- | --- |
| CP-01 | `Pagination` no se renderiza con `pages <= 1`; con varias, `nav aria-label`, enlaces `?page=`, `aria-current="page"` en la actual, `rel="prev"/"next"` | Roles y atributos |
| CP-02 | `Pagination` conserva `tag` y `q` en los enlaces de página | `href` |
| CP-03 | `ExternalLink` siempre lleva `rel="noopener noreferrer"` y respeta `children` | Atributos |
| CP-04 | `LoadingState` expone `role="status"` con texto | Rol |
| CP-05 | `ErrorState` muestra mensaje genérico y un `button` «Reintentar» que invoca `onRetry` | Clic |
| CP-06 | `EmptyState` muestra el texto y los enlaces que recibe | Texto y roles |

**Entidades**

| # | Comportamiento | Verificación |
| --- | --- | --- |
| EN-01 | `MediaImage` renderiza `src=access_url`, `alt`, `width`, `height` | Atributos |
| EN-02 | `MediaImage` con `alt_text: null` → `alt=""`; con `access_url: null` o medio `null` → nada | DOM |
| EN-03 | `PublishedDate` emite `<time dateTime=ISO>` con texto en español; `null` → nada | Atributos |
| EN-04 | `TagLinks` enlaza cada etiqueta a `/<seccion>?tag=<slug>` del tipo indicado | `href` |
| EN-05 | `Rating` muestra «N de 5» y sus glifos son `aria-hidden`; `null` → nada | Texto |
| EN-06 | `ProjectStatusBadge` mapea los tres valores a texto y tono; valor desconocido → texto crudo en `neutral` | Texto |
| EN-07 | Proveedores: `youtube` con id válido → URL `youtube-nocookie`; `vimeo` con id numérico → `player.vimeo.com`; id malformado o proveedor desconocido → `null` | Función pura, casos límite |
| EN-08 | `VideoCard`: sin `iframe` antes de pulsar; tras **Reproducir** aparece `iframe` con `title` y `src` permitido; proveedor no permitido → sin botón, solo enlace externo | Roles y atributos |
| EN-09 | Las cuatro tarjetas enlazan al detalle correcto (o a `/videos#slug`), muestran fecha, resumen y etiquetas | `href`, texto |

**Markdown (`MarkdownContent`) — tras aprobar la dependencia**

| # | Comportamiento | Verificación |
| --- | --- | --- |
| MD-01 | Encabezados, párrafos, listas, enlaces, énfasis, código en bloque e imágenes se renderizan | Roles/elementos |
| MD-02 | `<script>`, `<iframe>`, `<object>`, atributos `on*` y `style` **no** llegan al DOM | Ausencia |
| MD-03 | `[x](javascript:alert(1))` no produce un `href` ejecutable | `href` ausente o inerte |
| MD-04 | El HTML crudo dentro del Markdown no se interpreta | Texto escapado o ausente |
| MD-05 | Los encabezados del contenido empiezan en `h2` | Niveles |

**Páginas**

| # | Comportamiento | Verificación |
| --- | --- | --- |
| PG-01 | Cada página: un `h1`, `main` del layout, `document.title` propio | Roles |
| PG-02 | Listados: cargando → tarjetas; vacío → mensaje; error → Reintentar repite la llamada | Estados |
| PG-03 | Listados: `?page=2` y `?tag=x` llegan al servicio; con filtro activo aparece «Quitar filtro» | Llamada capturada |
| PG-04 | Detalles: `404` del API → página 404 (mismo contenido que la ruta inexistente); otro error → Reintentar | Roles |
| PG-05 | Inicio: cinco peticiones; perfil `404` omite la presentación sin romper el resto; sección sin destacados muestra su texto y enlace | Estados por bloque |
| PG-06 | Quién soy / Contacto: perfil `404` → mensaje explícito; `mailto:` y redes con `rel` | Atributos |
| PG-07 | Búsqueda: `q` ausente o corto → aviso sin llamar al API; resultados con tipo y enlace correcto por `type`; vacío con sugerencias | Llamadas y roles |
| PG-08 | 404: `h1` con 404, enlaces a Inicio y a las seis secciones | Roles |
| PG-09 | Layout: `header`, `nav` con los siete enlaces, `aria-current` en la activa, enlace de salto al `main`, buscador con `label`, `footer` | Roles |

**Rutas y guardas**

| # | Comportamiento | Verificación |
| --- | --- | --- |
| RT-01 | Las doce rutas están registradas; `*` es la última; `/__design-system` sigue en DEV | Tabla de rutas |
| RT-02 | Navegar a cada ruta renderiza su página sin caer en 404 | Router en memoria |
| GD-01 | Guardas T-01/T-03/F-03 sobre **todo** `src/**/*.module.css` | Suite extendida |
| GD-02 | Ninguna media query de ancho en `src/components`; fuera, solo con el literal del token citado | Suite extendida |

**Regresión**

| # | Comportamiento |
| --- | --- |
| RG-01 | Las 161 pruebas de `Task/013` siguen en verde; solo cambian las de la pantalla de fundación que esta tarea sustituye (`HomePage.test.tsx`, `App.test.tsx`: el doble de `/health` deja de hacer falta), con la justificación registrada |
| RG-02 | `src/services/http/**` sin cambios: `git diff main -- src/services/http` vacío |
| RG-03 | `/__design-system` ausente de `dist/` |
| RG-04 | `package.json`/`package-lock.json` sin cambios salvo la dependencia aprobada |

### 7.3 Integración necesaria

**Ninguna en la suite.** La validación visual y el gate de consola se hacen contra el
entorno local de `Task/007` (Traefik + backend + frontend construido), que **sí** exige
contenido publicado: ver §17.

### 7.4 Casos negativos y de seguridad

`404` indistinguible por slug; `access_url` nulo; `alt_text` nulo; proveedor fuera de lista;
`embed_reference` malformado; Markdown con `<script>`, `on*`, `javascript:`; envoltura
malformada; `q` corto; parámetros ajenos nunca enviados; enlaces externos sin `rel`.

### 7.5 Orden de implementación — mapa RED → GREEN

| Slice | RED esperado | GREEN | Depende de |
| --- | --- | --- | --- |
| 1. `services/public` + tipos | `Failed to resolve import` en cada adaptador | SV-01..06 | — |
| 2. `useAsyncResource`, `useDocumentTitle`, `HttpClientContext` | import no resuelto | HK-01..06 | 1 |
| 3. Rutas + `SiteLayout` + `NotFoundPage` real + páginas esqueleto con `h1` | RT-01/02, PG-08/09 fallan por rutas ausentes | RT, PG-08, PG-09 | 2 |
| 4. `Pagination`, `ExternalLink`, `LoadingState`, `EmptyState`, `ErrorState`; barrel | import no resuelto | CP-01..06 | — |
| 5. `MediaImage`, `PublishedDate`, `TagLinks`, `Rating`, `ProjectStatusBadge`, `providers` | import no resuelto | EN-01..07 | — |
| 6. Listados: `/articulos` → `/reviews` → `/proyectos` → `/videos` (con `VideoCard`) | PG-02/03, EN-08/09 | verde por página | 1–5 |
| 7. **Gate D-014-F** → `MarkdownContent` | MD-01..05 | verde | aprobación de la dependencia |
| 8. Detalles: `/articulos/:slug`, `/reviews/:slug`, `/proyectos/:slug`; `/quien-soy` | PG-04, PG-06 | verde | 6, 7 |
| 9. `/contacto`, `/buscar` | PG-06, PG-07 | verde | 1–5 |
| 10. Inicio (destacados + presentación); retiro de `services/health` (**D-014-G**) | PG-05 | verde | 6 |
| 11. Favicon (**D-014-E**) | prueba de `index.html`/`public` | verde | insumo del usuario o default |
| 12. Guardas extendidas (**D-014-M**), regresión completa, compuertas, validación visual, gate de consola | GD-01/02, RG-01..04 | verde | todo |
| 13. Reporte, `STATUS`, `ROADMAP`, `STAGE-04`, cierre documental de proveedores → **Lista para validación** | — | — | 12 |

Los *slices* 1–6 y 9–10 **no dependen** de la dependencia de Markdown y avanzan aunque la
decisión D-014-F se demore.

**Ejecución real (2026-09-05):** los trece *slices* se ejecutaron en este orden, con RED
demostrado y registrado antes de cada implementación en los *slices* 1 a 10. Los *slices*
11 (favicon) y 12 (guardas) se escribieron junto con su prueba; la guarda extendida se
**falsó** después inyectando un color literal, un `outline: none` y una media query en
`pages/listado.module.css`: las tres violaciones se detectaron y el archivo se restauró.
Evidencia completa en el [reporte](../task-reports/TASK-014-report.md) §3.

---

## 8. Plan de validación

1. Suite completa en verde con las pruebas de §7 y las 161 heredadas.
2. `format:check`, `lint`, `typecheck`, `test:coverage`, `build` sin errores ni *warnings*.
3. `git diff main -- src/services/http vite.config.ts tsconfig*.json eslint.config.js` vacío.
4. `package.json`/`package-lock.json`: solo la dependencia aprobada, si la hay.
5. `/__design-system` ausente de `dist/`.
6. **Validación visual integral** en Chrome sobre el entorno local de `Task/007`
   (`docker compose build frontend && docker compose up -d frontend`): las doce rutas, con
   contenido publicado; `scrollWidth == clientWidth` a 320, 390, 768 y 1280 px; Tab
   recorre navegación, buscador, tarjetas, paginación; foco visible; imágenes con `alt`.
7. **Gate de consola** de la Definition of Done: `console.error`, `window.error` y
   `unhandledrejection` en **0** en todas las rutas, incluida la 404 y un slug inexistente,
   en desarrollo y en *preview* de producción.
8. Comprobación negativa: el árbol del frontend no contiene `object_key`, `X-Amz`, `/admin`
   ni `videos/` como ruta de detalle.

## 9. Comandos de validación

```bash
cd personal-blog-frontend
npm run format:check
npm run lint
npm run typecheck
npm run test:run
npm run test:coverage
npm run build

# Nada fuera del alcance cambio.
git diff --stat main -- src/services/http vite.config.ts tsconfig.json tsconfig.app.json tsconfig.node.json eslint.config.js
git diff --stat main -- package.json package-lock.json      # vacio, o solo la dependencia aprobada

# El sitio publico no conoce el almacenamiento ni el panel.
grep -rn "object_key\|X-Amz\|/api/v1/admin\|/videos/" src/ ; echo "exit=$?"   # sin coincidencias en codigo productivo

# La demostracion sigue fuera de produccion.
grep -ril "design-system" dist/

# Entorno local para la validacion visual (repositorio infra).
cd ../personal-blog-infra
docker compose build frontend
docker compose up -d frontend
```

## 10. Evidencia esperada

- Salida de las seis compuertas y de la suite, con el número de pruebas nuevas.
- Evidencia RED por *slice* (import no resuelto o aserción fallida) y GREEN posterior.
- Tabla de anchos con `scrollWidth`/`clientWidth` por ruta.
- Tabla del gate de consola por ruta y modo.
- Diff vacío sobre cliente HTTP y configuración de build.
- Lista cerrada de proveedores escrita en `api-contracts` §14.9, `data-model` §10 y
  `security-boundaries` §7.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | **Dependencia para Markdown.** No hay equivalente de plataforma; añade peso y es superficie de seguridad | Alto | Propuesta explícita §6.K, esquema de permitidos, carga diferida, pruebas MD-02..04; auditoría en `Task/018`; peso medido en `Task/016`. **No se instala sin aprobación** |
| 2 | **Desarrollo con recarga en caliente contra el API.** El backend **no tiene middleware CORS** (`main.py`: «los orígenes se definen al integrar el frontend y se endurecen en `Task/018`»); `npm run dev` en `5173` no puede consumir `8081`. `Task/007` resolvió el consumo con **mismo origen** vía Traefik sobre la imagen construida | Medio | La suite no toca la red. La validación funcional se hace **reconstruyendo la imagen** (`docker compose build frontend`), flujo ya documentado en el runbook. Un `server.proxy` de Vite solo-desarrollo sería un cambio de `vite.config.ts` que **no se hace por reflejo**: se propone al usuario si el ciclo resulta demasiado lento |
| 3 | **`access_url` caduca** (900 s por defecto) sin `access_expires_at` | Medio | Cada navegación vuelve a pedir el recurso; nada se persiste. Imágenes rotas en una pestaña muy antigua hasta recargar. Política definitiva: **D-08** (`Task/030`) |
| 4 | **Sin semilla local**: `GET /profile` → `404` y listados vacíos hasta `Task/022` | Medio | Estados explícitos probados (D-014-K). La validación visual exige crear y publicar contenido con la API administrativa de `Task/012`; el reporte documentará los pasos |
| 5 | **Proveedor de video no restringido en el backend** | Bajo | *Fail-closed* en el render (D-014-C); deuda para `Task/015` (selector) y backend |
| 6 | **Las guardas de `Task/013` no cubren `pages/`, `entities/`, `features/`** | Medio | D-014-M las extiende antes de escribir CSS de página |
| 7 | **Código HTTP 404 imposible en una SPA estática** (A.11) | Bajo | Página 404 correcta y `title` propio aquí; `noindex`/`robots` en `Task/016`, *hosting* en `Task/034` |
| 8 | Cinco peticiones en Inicio | Bajo | Bloques independientes con su propio estado; sin bloqueo mutuo. Medición en `Task/016` |
| 9 | **Dar `Task/015` o `Task/016` por adelantado**: formularios, SEO, *lazy loading* medido | Medio | §4 enumera qué no se hace y quién lo hace |
| 10 | Declarar «responsive validado» sin verlo | Medio | Medición de desbordamiento a cuatro anchos en Chrome, como en `Task/013` |
| 11 | El buscador introduce un formulario y roza **A-03** (`Task/015`) | Bajo | `label` visible y nativo, sin reclamar A-03; sin validación anunciada (A-08) porque no hay error de formulario: `q` corto solo muestra un aviso |

## 12. Decisiones técnicas

Todas **Vigentes** desde el 2026-09-05, promovidas con la aprobación del usuario. Resumen;
detalle en §6.

| # | Decisión | ¿ADR? |
| --- | --- | --- |
| D-014-A | Doce rutas confirmadas, incluidas `/proyectos/:slug` y `/buscar` | No — confirma la propuesta de `MVP_SCOPE` §2.1 dentro del mandato explícito «se confirman en `Task/014`» |
| D-014-B | Media: `access_url` + `alt_text` + dimensiones; nada más | No |
| D-014-C | Proveedores de video: `youtube`, `vimeo`; *fail-closed*; *embed* al pulsar | No — cierra una pregunta asignada por nombre; se registra en `api-contracts`, `data-model` y `security-boundaries` |
| D-014-D | Responsive intrínseco; media query solo con necesidad demostrada y token citado | No |
| D-014-E | Favicon: asset del usuario o icono neutro provisional derivado de tokens | No |
| D-014-F | Dependencia `react-markdown` + `rehype-sanitize`, **no instalada** | No — D-03 ya prevé justificar una dependencia puntual |
| D-014-G | Retirar `services/health` con la pantalla provisional | No |
| D-014-H..N | Estado en URL; `page_size` mínimo; ancla para videos; perfil `404` como estado; misma pestaña; guardas extendidas; guardas ligeras de forma | No |

## 13. Documentación creada o actualizada

Esta sesión (definición):

- `docs/tasks/TASK-014-public-site.md` — esta ficha (creada).
- `docs/project-management/STATUS.md` — `Task/014` **En progreso**; sección de la tarea;
  distribución por estado; hallazgo independiente del índice de reportes; avance **sin
  cambios**.
- `docs/project-management/ROADMAP.md` — fila de `Task/014` y fecha de actualización.
- `docs/stages/STAGE-04-user-experience.md` — `Task/014` en progreso con enlace a la ficha.

Al terminar la implementación (2026-09-05):

- `docs/task-reports/TASK-014-report.md` — reporte (creado).
- `docs/architecture/api-contracts.md` §14.9 — lista de proveedores **cerrada** (`youtube`,
  `vimeo`), como propuesta pendiente de aprobación.
- `docs/architecture/data-model.md` — fila de responsabilidades y deuda 6 cerradas; queda
  la restricción en el backend como deuda con propietario.
- `docs/architecture/security-boundaries.md` §5 y §7 — Markdown, embeds y enlaces externos
  marcados como implementados; proveedores cerrados.
- `docs/runbooks/local-environment.md` §11 — fila «Frontend» actualizada.
- `personal-blog-frontend/README.md` — estado, estructura, sitio público y reglas.
- `STATUS`, `ROADMAP`, `STAGE-04` — `Task/014` **Lista para validación**; avance **sin
  cambios**.

## 14. Archivos modificados

**Esta sesión**

| Repositorio | Archivo | Acción |
| --- | --- | --- |
| infra | `docs/tasks/TASK-014-public-site.md` | creado |
| infra | `docs/project-management/STATUS.md` | modificado |
| infra | `docs/project-management/ROADMAP.md` | modificado |
| infra | `docs/stages/STAGE-04-user-experience.md` | modificado |
| frontend | — | **ninguno**: rama creada, sin cambios |

**Implementación (frontend, 2026-09-05).** `git status`: **117 archivos creados, 12
modificados, 3 eliminados**. Ninguno de los archivos previstos como *pendiente de
confirmar* quedó sin resolver.

| Acción | Archivos |
| --- | --- |
| Creados — `app/` (7) | `SiteLayout.tsx`, `SiteLayout.module.css`, `SiteLayout.test.tsx`, `httpClientContext.ts`, `httpClientContext.test.tsx`, `routes.test.tsx`, `favicon.test.ts` |
| Creados — `services/public/` (19) | `types.ts`, `pagina.ts`, `listado.ts`, `profile.ts`, `posts.ts`, `bookReviews.ts`, `videos.ts`, `projects.ts`, `tags.ts`, `search.ts`, `index.ts` y sus 8 archivos de prueba |
| Creados — `hooks/` (6) | `useAsyncResource.ts`, `useDocumentTitle.ts`, `useParametrosDeListado.ts` y sus pruebas |
| Creados — `lib/` (7) | `rutas.ts`, `site.ts`, `enlaces.ts`, `format/date.ts`, `format/duration.ts` y las pruebas de formato |
| Creados — `components/` (15) | `Pagination/` (tsx, `paginas.ts`, css, test), `ExternalLink/` (tsx, test), `LoadingState/`, `EmptyState/`, `ErrorState/` (tsx, css, test) |
| Creados — `entities/` (28) | `media/MediaImage`, `content/PublishedDate`, `content/tarjeta.module.css`, `tags/TagLinks`, `tags/TagFilter`, `book-reviews/{Rating,ReviewCard,libro}`, `projects/{ProjectStatusBadge,ProjectCard}`, `posts/PostCard`, `videos/{providers,VideoCard}`, con sus pruebas y CSS Modules |
| Creados — `features/markdown/` (6) | `esquema.ts`, `MarkdownRenderer.tsx`, `MarkdownContent.tsx`, `markdown.module.css` y dos pruebas |
| Creados — `pages/` (24) | `About`, `Posts`, `PostDetail`, `BookReviews`, `BookReviewDetail`, `Videos`, `Projects`, `ProjectDetail`, `Contact`, `Search` (página + prueba cada una), `NotFoundPage.test.tsx`, `HomePage.module.css`, `listado.module.css`, `detalle.module.css` |
| Creados — `test/` (4) y `public/` (1) | `respuestas.ts`, `fixtures.ts`, `renderRuta.tsx`, `precargarMarkdown.ts`; `favicon.svg` |
| Modificados (12) | `src/app/routes.tsx`, `src/app/App.tsx`, `src/app/App.test.tsx`, `src/pages/HomePage.tsx` (reescrita), `src/pages/HomePage.test.tsx` (reescrita), `src/pages/NotFoundPage.tsx`, `src/components/index.ts`, `src/styles/designSystem.guards.test.ts` (extendida, sin tocar las pruebas previas), `index.html` (favicon), `package.json`, `package-lock.json` (solo las dos dependencias autorizadas), `README.md` |
| Eliminados (3, D-014-G) | `src/services/health/healthService.ts`, `healthService.test.ts`, `index.ts` — tras demostrar con `git grep` que su único consumidor productivo era la pantalla provisional |
| **No tocados** (`git diff main` vacío) | `src/services/http/**`, `vite.config.ts`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`, `eslint.config.js`, `src/styles/tokens.css`, `src/styles/foundation.css`, las cinco primitivas de `Task/013`, `src/main.tsx` |

**Infra (2026-09-05):** modificados `STATUS.md`, `ROADMAP.md`, `STAGE-04-user-experience.md`,
`api-contracts.md`, `data-model.md`, `security-boundaries.md`, `runbooks/local-environment.md`;
creados esta ficha y el reporte.

## 15. Resultado de pruebas

Ejecutadas el 2026-09-05 en `personal-blog-frontend`, rama `Task/014-Sitio-Publico`.

| Prueba | Comando | Resultado |
| --- | --- | --- |
| Línea base heredada, **antes** del primer RED | `npm run test:run` | ✔ **161 / 161** en 15 archivos |
| Formato | `npm run format:check` | ✔ *All matched files use Prettier code style* |
| Lint | `npm run lint` | ✔ 0 errores, 0 avisos |
| Tipos | `npm run typecheck` | ✔ sin errores |
| Suite final | `npm run test:run` | ✔ **440 / 440** en 61 archivos (161 heredadas + 279 nuevas). **Estable**: 5 corridas seguidas y 1 bajo carga concurrente, todas en verde |
| Cobertura | `npm run test:coverage` | ✔ sentencias **99,78 %**, ramas **96,61 %**, funciones **100 %**, líneas **99,78 %** |
| Build | `VITE_API_BASE_URL=http://localhost:8081 npm run build` | ✔ 326 módulos, sin *warnings*; `index-*.js` 318,8 kB (99,0 kB gzip), `MarkdownRenderer-*.js` 121,6 kB (37,1 kB gzip) en *chunk* aparte |
| Demostración fuera de producción | `grep -ril "design-system" dist/` | ✔ sin resultados |
| Favicon en el build | `ls dist/favicon.svg`, `<link rel="icon">` en `dist/index.html` | ✔ |
| Archivos protegidos | `git diff --stat main -- src/services/http vite.config.ts tsconfig*.json eslint.config.js` | ✔ vacío |
| Dependencias | `git diff main -- package.json` | ✔ solo `react-markdown` y `rehype-sanitize` |
| Cadenas prohibidas en código productivo | `grep object_key\|X-Amz\|/api/v1/admin src` | ✔ solo en comentarios; ninguna en lógica |
| Secretos | patrones de contraseña, token y claves | ✔ ninguno |
| Guardas extendidas **falsadas** | violación temporal en `pages/listado.module.css` | ✔ **3 fallos detectados** (color literal, `outline: none`, media query sin token); archivo restaurado |
| Validación visual, 14 superficies × 4 anchos | Chrome headless por CDP contra `http://localhost:8081` | ✔ `scrollWidth == clientWidth` en las **56** combinaciones; 1 `h1`, `main#contenido`, `nav` y `footer` en todas |
| Gate de consola | ídem | ✔ **0** excepciones y **0** `console.error`. Únicas entradas: anotaciones de red de Chrome por respuestas `404` **esperadas** (perfil sin semilla; slugs inexistentes visitados a propósito) |
| Teclado | 10 × Tab en `/` y `/articulos` | ✔ salto → marca → 7 enlaces → buscador; anillo `2px solid #0a5ad6` (`--color-focus`) en todos |

La única línea sin cobertura es el camino de éxito de `useAppConfig`
(`src/app/appConfigContext.ts`): su consumidor productivo era la pantalla provisional que
esta tarea retira. Se conserva porque `App` sigue proveyendo la configuración; ver §18.

## 16. Problemas encontrados

| # | Problema | Resolución |
| --- | --- | --- |
| 1 | La base de datos del entorno local estaba en la revisión `0001` mientras la imagen del backend traía `0003`: **todos** los recursos públicos respondían `500` (`relation "profiles" does not exist`). | `docker exec personal-blog-local-backend alembic upgrade head`: operación aditiva y documentada. Tras ella el API responde `200` con colecciones vacías y `404` en el perfil, el estado previo a la semilla de `Task/022`. |
| 2 | Sin administrador ni perfil en la base local (0 filas) y sin mecanismo documentado para crear uno, **no se pudo publicar contenido de prueba** sin inventar credenciales ni modificar el backend. | Los estados con datos —tarjetas, imágenes, embeds, Markdown, paginación— quedan cubiertos por la suite (440 pruebas); en el entorno real se validaron los estados vacíos, el `404` del perfil como estado explícito y la 404 pública. Limitación registrada en §18 y en el reporte. |
| 3 | El comentario JSDoc de `types.ts` contenía la ruta `app/modules/*/presentation`: el `*/` cerraba el comentario y rompía `tsc` (Vitest lo toleró). | Reescrito como `app/modules/<modulo>/presentation`. |
| 4 | `react-hooks/set-state-in-effect`: el hook fijaba `cargando` con `setState` síncrono en el efecto. | La fase `cargando` pasa a **derivarse**: el resultado guarda la clave (`cargar`, `intento`) con la que se obtuvo. Sin `setState` síncrono y sin cambio de comportamiento observable. |
| 5 | `react-refresh/only-export-components`: tres archivos de componente exportaban también funciones o constantes. | Movidas a módulos propios: `lib/enlaces.ts`, `components/Pagination/paginas.ts`, `entities/book-reviews/libro.ts`, `features/markdown/esquema.ts`. |
| 6 | Dos pruebas propias fallaban por el entorno, no por el componente: `.click()` fuera de `act` y un `findByRole` que quedaba con un `h1` desmontado al llegar el perfil. | `fireEvent.click` y espera del estado final. |
| 7 | La primera importación diferida del renderizador Markdown supera el segundo de espera por defecto de Testing Library. | Espera ampliada en esa prueba; es coste del entorno, documentado en el propio archivo. |
| 8 | `Prettier` no infiere un *parser* para `.svg`. | El favicon queda fuera del formateador; su forma la fija `favicon.test.ts`. |
| 9 | **Suite inestable** detectada al ejecutar el cierre: una corrida en `439/440` (63 s) entre seis verdes (~33 s). Cinco pruebas esperaban con límite de reloj la primera importación diferida de `MarkdownRenderer`. | `src/test/precargarMarkdown.ts` deja el módulo resuelto de forma estática; se retiran los cinco `timeout` ampliados. Sin carrera contra el reloj, con el renderizador **real** y **sin tocar** la carga diferida de producción. Detalle y evidencia en el [reporte](../task-reports/TASK-014-report.md) §16. |

Observaciones que **no** son problemas de esta tarea:

1. El índice `docs/task-reports/README.md` omite `Task/010`–`Task/013`. Drift preexistente,
   excluido de `Task/013.1` por el usuario; registrado en `STATUS.md`, **no se corrige aquí**.
2. La tabla «Resumen de etapas» de `ROADMAP.md` se detuvo en la aprobación de `Task/009`
   (ETAPA 03 «2 de 5», ETAPA 04 «0», total «9 de 41 — 22 %») y contradice la cabecera del
   mismo documento (13 de 41 — 32 %). Ya estaba así en `main` (`fec55bb`). Drift
   preexistente e independiente; registrado en `STATUS.md`, **no se corrige aquí**.
3. El runbook local (§6, «Estado de las migraciones») sigue declarando como esperado
   `0001 (head)`, valor de `Task/007`; desde `Task/011` la cabeza es `0003`. Drift
   preexistente e independiente; registrado en `STATUS.md`, **no se corrige aquí**.
4. El backend no tiene middleware CORS (riesgo 2). No es un defecto: es la postura declarada
   hasta `Task/018`.

## 17. Pasos de validación para el usuario

```powershell
cd C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-frontend

# 1. Compuertas de calidad.
npm run format:check
npm run lint
npm run typecheck
npm run test:run          # 440 en verde, 61 archivos
npm run test:coverage
$env:VITE_API_BASE_URL = "http://localhost:8081"; npm run build   # sin warnings

# 2. Nada fuera del alcance cambio (salida vacia).
git diff --stat main -- src/services/http vite.config.ts tsconfig.json tsconfig.app.json tsconfig.node.json eslint.config.js
git diff main -- package.json          # solo react-markdown y rehype-sanitize

# 3. La demostracion no viaja a produccion (sin resultados) y el favicon si.
Select-String -Path dist\assets\* -Pattern "design-system" -List
Get-Item dist\favicon.svg
```

**Ver el sitio en el navegador** (entorno local de `Task/007`, ya reconstruido con esta
rama; si lo reconstruyes tú, desde `personal-blog-infra`: `docker compose build frontend;
docker compose up -d frontend`). Abrir `http://localhost:8081/` y comprobar:

1. **Navegación por teclado**: el primer Tab enfoca «Saltar al contenido»; siguen la marca,
   los siete enlaces de la navegación y el buscador, todos con el anillo de foco.
2. **Las doce rutas**: `/`, `/quien-soy`, `/articulos`, `/reviews`, `/videos`,
   `/proyectos`, `/contacto`, `/buscar?q=docker`, y una ruta inexistente. Sin semilla, los
   listados muestran «Todavía no hay …», Quién soy y Contacto «aún no está disponible», y
   `/articulos/lo-que-sea` muestra la 404 con enlaces a las secciones.
3. **Estrechar la ventana** hasta el ancho de un móvil: nada se desborda en horizontal.
4. **Buscar** con una sola letra: la página explica el mínimo sin llamar al API; con dos o
   más, muestra «Sin resultados» y las secciones.
5. `/__design-system` debe responder la **404** en el build de producción.

Para ver tarjetas, imágenes con `alt`, *embeds* y Markdown renderizado hace falta contenido
publicado, que **no existe** en local hasta `Task/022` (no hay administrador). Esos estados
están cubiertos por la suite (§15) y pueden verse en `npm run test -- --ui` o leyendo las
pruebas de `src/pages/`.

## 18. Deuda técnica pendiente

| # | Deuda | Tarea propietaria |
| --- | --- | --- |
| 1 | Restringir `provider` en el backend a la lista cerrada de D-014-C y ofrecer el selector en el panel | Backend: sin propietario asignado (candidata `Task/018`); panel: `Task/015` |
| 2 | Derivar la miniatura del proveedor cuando el video no tiene `thumbnail` | Sin propietario; requiere decidir sobre la petición a un tercero |
| 3 | `noindex` y código HTTP para la 404 de la SPA | `Task/016`, `Task/034` |
| 4 | Metadatos `title`/`description` SEO, Open Graph, canonical por página | `Task/016` |
| 5 | Medición de peso del renderizador Markdown y *lazy loading* de imágenes | `Task/016` |
| 6 | Auditoría de la configuración de sanitización | `Task/018` |
| 7 | Proxy de desarrollo de Vite si el ciclo «reconstruir imagen» resulta lento | Decisión del usuario; no se adelanta |
| 8 | Índice de reportes incompleto (`Task/010`–`Task/013`) | Independiente de `Task/014`; a decisión del usuario |
| 9 | Tabla «Resumen de etapas» de `ROADMAP.md` detenida en `Task/009` (9 de 41) | Independiente de `Task/014`; a decisión del usuario |
| 10 | Runbook local §6: el valor esperado de `alembic current` sigue en `0001 (head)`; la cabeza real es `0003` | Independiente de `Task/014`; a decisión del usuario |
| 11 | `useAppConfig` (`src/app/appConfigContext.ts`) queda **sin consumidor productivo** al retirar la pantalla provisional; `App` sigue proveyendo `AppConfigContext`. Retirar el hook o darle uso | `Task/015`, que decide si el panel necesita la configuración fuera del cliente HTTP |
| 12 | Validación visual **con contenido** (tarjetas, imágenes, embeds, Markdown en el navegador real): imposible sin semilla ni administrador local | `Task/022` (semilla local); los estados están cubiertos por la suite |
| 13 | Las respuestas `404` del API por slug inexistente y por perfil sin semilla aparecen como anotaciones de red en la consola de Chrome. No son errores de JavaScript ni evitables desde el frontend | Ninguna: es el contrato de no filtración de `api-contracts.md` §3 |

## 19. Próxima tarea

`Task/015-Panel-Administrativo` — dashboard, editor Markdown (D-04), gestión de contenido,
carga de imágenes y vista previa con **el mismo** `MarkdownContent`. **No se inicia** hasta
que `Task/014` esté aprobada y normalizada.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-05** |
| **Aprobado por** | **jeffersondavila** (el usuario) |
| **Expresión de aprobación** | `approved: Task/014-Sitio-Publico` — recibida literalmente |

La aprobación autorizó el flujo de cierre de
[`WORKFLOW.md`](../project-management/WORKFLOW.md) §3 en `personal-blog-frontend` y
`personal-blog-infra`: promoción de **D-014-A** a **D-014-N** a **Vigentes**, actualización
del gobierno, commits, integración en `dev` mediante merge `--no-ff` y pull request
`Task/014-Sitio-Publico → main`.

**La revisión y la fusión del pull request son responsabilidad exclusiva del usuario.**
