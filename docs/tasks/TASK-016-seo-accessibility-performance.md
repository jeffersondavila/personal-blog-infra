# TASK-016 — SEO, Accesibilidad y Rendimiento

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/016-SEO-Accesibilidad-y-Rendimiento` |
| **Nombre** | SEO, Accesibilidad y Rendimiento |
| **Etapa** | ETAPA 05 — Calidad y Seguridad |
| **Estado** | **Aprobada** — 2026-09-06 |
| **Repositorios involucrados** | `personal-blog-frontend`, `personal-blog-backend`, `personal-blog-infra` (documentación + ***wiring* local mínimo**) |
| **Dependencias** | `Task/014` — **Aprobada** (2026-09-05) · `Task/015` — **Aprobada** (2026-09-05) |
| **Rama** | `Task/016-SEO-Accesibilidad-y-Rendimiento` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base — frontend** | `1c5e2f329bcbc68afc73ef3b0b3b5b0e399c35ab` |
| **SHA base — backend** | `d278d849b4a4d506b838213a9572d97d9eed80da` |
| **SHA base — infra** | `6c57f7bd8b3480443d51605b5bcce23c14494425` |
| **Fecha de inicio** | 2026-09-05 |
| **Última actualización** | 2026-09-06 |

> **Naturaleza de este documento.** Recoge la **definición** de la tarea: alcance
> reconciliado contra las fuentes canónicas, *baseline* medido, contradicciones
> localizadas y plan de implementación. Lo **ejecutado** —y lo que la ejecución
> obligó a corregir de esta ficha— está en el
> [reporte](../task-reports/TASK-016-report.md).
>
> **Cinco puntos de esta ficha quedaron corregidos al implementar**, siempre por
> medición y no por conveniencia. Están marcados en línea con **CORREGIDO** y
> recogidos juntos en la §12 del reporte.
>
> **Aprobada el 2026-09-06** mediante la expresión exacta
> `approved: Task/016-SEO-Accesibilidad-y-Rendimiento`.
>
> Las decisiones **D-016-A** y **D-016-B** quedan **Vigentes**, y los umbrales
> **U-1 a U-9** pasan a formar parte de
> [`non-functional-requirements.md`](../architecture/non-functional-requirements.md) §2.
>
> **Lo que la aprobación NO convierte en decidido.** **D-21** sigue **Abierta** y
> [**ADR-009**](../adr/ADR-009-rendering-strategy-for-crawlers.md) sigue en
> **Propuesta**: lo aprobado es **haber abierto** la reconsideración con evidencia, no
> haber elegido una estrategia de *rendering*. Tampoco cambian **E-03** (no cerrado),
> **E-06** (parcial) ni **D-08** (abierta).

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

| # | Comprobación | frontend | backend | infra |
| --- | --- | :---: | :---: | :---: |
| 1 | `main == origin/main` antes de crear la rama | ✔ | ✔ | ✔ |
| 2 | `dev == origin/dev` | ✔ | ✔ | ✔ |
| 3 | `git diff main dev` vacío | ✔ | ✔ | ✔ |
| 4 | `git rev-list --count dev..main` = 0 | ✔ | ✔ | ✔ |
| 5 | Working tree limpio antes de crear la rama | ✔ | ✔ | ✔ |
| 6 | Sin ramas `Task/*` previas, locales ni remotas | ✔ | ✔ | ✔ |
| 7 | Un solo *worktree* por repositorio | ✔ | ✔ | ✔ |
| 8 | Rama creada **desde `main`** | ✔ | ✔ | ✔ |
| 9 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | ✔ | ✔ | ✔ |
| 10 | `git rev-list --count main..HEAD` = 0 | ✔ | ✔ | ✔ |

El SHA base de cada repositorio está en la tabla de encabezado, obtenido dinámicamente al
crear la rama (criterio 11 de la
[Definition of Done](../project-management/DEFINITION_OF_DONE.md)).

---

## 1. Objetivo

Elevar el sitio público a estándar publicable en tres ejes verificables:

1. **SEO** — cerrar **E-02** a **E-08**; verificar **E-01** como regresión.
2. **Accesibilidad** — **auditar** formalmente **A-01** a **A-08**, corregir únicamente
   los *gaps* demostrados y cerrar **A-01**.
3. **Rendimiento** — fijar los **umbrales numéricos** que
   [`non-functional-requirements.md`](../architecture/non-functional-requirements.md) §2
   delega expresamente en esta tarea, y verificar **P-01**, **P-03**, **P-04** y **P-05**.

El objetivo transversal —y lo que distingue esta tarea de una lista de cambios mecánicos—
es el que fijó `Task/005.5`: **verificación comprobable, no suposición**. Escribir el
código de los metadatos no demuestra que el SEO funcione.

---

## 2. Contexto y dependencias

`Task/014` entregó **12 superficies públicas** y `Task/015` **18 administrativas**, ambas
**Aprobadas** el 2026-09-05. Entre las dos dejaron diferido a esta tarea lo que sigue, y
esa herencia **es** el alcance:

| Origen | Deuda trasladada a `Task/016` |
| --- | --- |
| `Task/010` deuda 2 | La miniatura se almacena pero **no se expone** en la API pública |
| `Task/013` deuda 6 | Auditoría formal de accesibilidad y umbrales de rendimiento |
| `Task/014` deuda 3 | `noindex` de la 404 (el **código HTTP** es de `Task/034`) |
| `Task/014` deuda 4 | `description`, Open Graph y canonical por página |
| `Task/014` deuda 5 | Medir el peso del renderizador Markdown y el *lazy loading* |
| `Task/014` riesgo 8 | Cinco peticiones en Inicio: medición |
| `Task/015` deuda 5 y 7 | `noindex` del panel (**E-06**) |
| `Task/015` deuda 2 | Validación visual a 320, 390, 768 y 1280 px |
| `ADR-005` | Comprobar que el SEO es suficiente pese al render en cliente |

**Dos precisiones de ownership que esta tarea no invade:**

- **`Task/034`** es propietaria del **código HTTP `404`** real, porque depende del
  *hosting*. `Task/016` solo aporta el `noindex`.
- **`Task/030`** es propietaria de **D-08** y, con ella, de la existencia de una **URL
  estable de medios**. `Task/016` decide **qué URL usa `og:image`**, que es cosa
  distinta (§8).

---

## 3. Fuentes canónicas

Reconstruidas y contrastadas entre sí. Ante contradicción se aplica el orden de autoridad
de [`PROJECT_INSTRUCTIONS.md`](../claude/PROJECT_INSTRUCTIONS.md) §18.

| Documento | Qué aporta |
| --- | --- |
| [`non-functional-requirements.md`](../architecture/non-functional-requirements.md) | **Fuente literal de E-01…E-08, A-01…A-08 y P-01…P-08.** §2 delega los umbrales en `Task/016` |
| [`STAGE-05-quality-security.md`](../stages/STAGE-05-quality-security.md) | Las **6 comprobaciones obligatorias** y el **criterio de reconsideración** |
| [`ROADMAP.md`](../project-management/ROADMAP.md) | Alcance de una línea, dependencias y repositorios |
| [`ADR-005`](../adr/ADR-005-markdown-content.md) | Markdown en cliente; el SEO *«se gestiona aparte (`Task/016`)»*; si no basta, **se reconsidera con un ADR** |
| [`open-decisions.md`](../architecture/open-decisions.md) | **D-08** abierta (medios y CDN) · **D-07** abierta (dominio) · **D-15** resuelta (mismo *site*) |
| [`api-contracts.md`](../architecture/api-contracts.md) | Contrato público real: §3 recursos, §5 paginación, §12 medios, §14.5 validación de publicación |
| [`CONTENT_MODEL.md`](../product/CONTENT_MODEL.md) | *Fallbacks* `seo_title → title` y `seo_description → summary` |
| [`data-model.md`](../architecture/data-model.md) | **D-D**: escala de `rating` **entero 1..5** |
| [`USER_FLOWS.md`](../product/USER_FLOWS.md) | A.3 exige `title`, `description`, canonical y OG · A.11 exige *«el código HTTP correcto para no ser indexada»* |
| [`MVP_SCOPE.md`](../product/MVP_SCOPE.md) | §2.2: *«Compartir páginas mediante metadatos Open Graph»* — el propósito de **E-03** son **las redes sociales** |
| [`security-boundaries.md`](../architecture/security-boundaries.md) | Las **cabeceras HTTP** son de `Task/018`; `robots.txt` no es control de acceso |
| [`DEFINITION_OF_DONE.md`](../project-management/DEFINITION_OF_DONE.md) | Compuertas por tipo de tarea; **B-1…B-12** para backend funcional |
| [`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md) | Ley test-first del backend |

### 3.1 Precedencia resuelta — repositorios participantes

`ROADMAP.md` y `STAGE-05` declaran los repositorios de `Task/016` como
**`frontend`, `backend`**, y **omiten `infra`**. Las tres tareas anteriores se declararon
como `frontend, infra (documentación)`.

**La omisión es un defecto de esa fila, no una regla.** `WORKFLOW.md` §6 obliga a
actualizar `STATUS.md`, `ROADMAP.md`, la ficha y el reporte en **cada** tarea, y §7 fija
que roadmap, estado y decisiones viven **solo** en `personal-blog-infra`. Una tarea no
puede cumplir §6 sin escribir en `infra`.

**Resolución:** los tres repositorios participan, con papeles distintos.

| Repositorio | Papel | Justificación |
| --- | --- | --- |
| `personal-blog-frontend` | **Funcional** | Metadatos, OG, canonical, JSON-LD, `robots.txt`, `noindex`, correcciones de accesibilidad y de rendimiento |
| `personal-blog-backend` | **Funcional** | `sitemap.xml` derivado de contenido publicado (§9) y exposición de la miniatura (§12) |
| `personal-blog-infra` | **Documentación + *wiring* local mínimo** | `STATUS`, `ROADMAP`, `STAGE-05`, esta ficha, el reporte y los documentos de arquitectura afectados, **más tres líneas de *wiring*** autorizadas expresamente (§3.2) |

**Propuesta — pendiente de aprobación:** corregir la fila de `Task/016` en `ROADMAP.md`
para que diga `frontend, backend, infra (documentación + wiring local mínimo)`. **No** es `infra (documentación)` a secas,
como en `Task/013`–`Task/015`: esta tarea sí tocó tres líneas funcionales de infra (§3.2).

### 3.2 Las tres líneas de *wiring* local, autorizadas una a una

El papel de `infra` empezó siendo **solo documentación**. Durante la implementación
aparecieron tres puntos en los que la tarea **no podía funcionar en local** sin tocar
infraestructura, y **cada uno se sometió al usuario antes de ejecutarlo**:

| # | Archivo | Cambio | Por qué era imprescindible |
| --- | --- | --- | --- |
| 1 | `docker-compose.yml` | `BLOG_PUBLIC_SITE_BASE_URL` en el servicio `backend` | La variable es obligatoria; sin ella el backend **no arranca** en Docker, lo que rompería el entorno de `Task/003` y `Task/007` (criterio 10 de la DoD) |
| 2 | `docker/traefik/dynamic/routes.yml` | Un término más en la regla del router `backend`, para `/sitemap.xml` | Sin ella `/sitemap.xml` caía en el frontend y devolvía el `index.html` de la SPA, así que `robots.txt` declaraba un sitemap que respondía HTML |
| 3 | `docker-compose.yml` | `VITE_SITE_BASE_URL` en `build.args` del `frontend` | `TRAEFIK_HTTP_HOST_PORT` es configurable: `canonical`, `og:url` y `og:image` no pueden quedar acoplados al valor por defecto del `Dockerfile` |

**Lo que esta clasificación NO autoriza.** No convierte a `Task/016` en una tarea de
infraestructura funcional. Quedan expresamente fuera, y siguen con su propietario:
Nginx y su compresión, CORS, cabeceras de seguridad y `X-Robots-Tag` (`Task/018`),
Cloudflare Pages (`Task/034`) y cualquier recurso cloud.

---

## 4. Dentro del alcance

### 4.1 SEO

- [ ] `title` y `description` propios y correctos **por URL** en las 12 superficies
      públicas (**E-02**).
- [ ] `canonical` absoluto en cada página pública (**E-04**).
- [ ] Open Graph completo, con `og:image` de **URL estable y no expirable** (**E-03**),
      con el alcance y la limitación de §8.
- [ ] `sitemap.xml` derivado **exclusivamente** de contenido `published` (**E-05**,
      **E-08**).
- [ ] `robots.txt` coherente, con el panel no indexable (**E-06**).
- [ ] `<meta name="robots" content="noindex,follow">` en `/admin/*` y en la 404.
- [ ] Datos estructurados JSON-LD donde el DTO real los alimente (**E-07**, §10).
- [ ] **E-01** verificado como regresión: slugs legibles y estables.

### 4.2 Verificación del *rendering* — obligación de `Task/005.5`

- [ ] Las **6 comprobaciones** de `STAGE-05` ejecutadas y registradas con evidencia.
- [ ] Medición diferenciada de: navegador con JS, petición HTTP directa, *crawler* sin JS
      y *user-agent* de *crawler* conocido.
- [ ] **Criterio de reconsideración** evaluado y su resultado registrado (§7).

### 4.3 Accesibilidad

- [ ] Auditoría formal **A-01…A-08** sobre superficies reales, con la matriz de §11.
- [ ] Corrección de **los *gaps* demostrados y solo de esos**.
- [ ] Cierre formal de **A-01**: teclado completo en sitio público **y** panel.
- [ ] Deuda visual de `Task/015` a 320, 390, 768 y 1280 px absorbida como auditoría.

### 4.4 Rendimiento

- [ ] Umbrales numéricos fijados con baseline, herramienta, entorno y racional (§12).
- [ ] **P-01**, **P-03** y **P-04** verificados; **P-05** preservado y medido en runtime.
- [ ] Exposición de la miniatura en la API pública (deuda 2 de `Task/010`).

### 4.5 Gobierno

- [ ] `STATUS.md`, `ROADMAP.md`, `STAGE-05`, ficha y reporte actualizados.
- [ ] Umbrales incorporados a `non-functional-requirements.md` §2.
- [ ] Nota en `open-decisions.md` sobre qué aportó `Task/016` a **D-08**, **sin cerrarla**.

---

## 5. Fuera del alcance

| Fuera | Propietario |
| --- | --- |
| **Cambiar la estrategia de *rendering*** (SSR, SSG, prerender) | Decisión nueva con **ADR propio**. `Task/016` solo puede **abrir** la reconsideración (`STAGE-05`) |
| **Código HTTP `404` real** de la SPA | `Task/034` — frontera exacta en §9.4 |
| **Cerrar D-08**: URL estable de medios, semántica de caché, TTL productivo, CDN | `Task/030` |
| **`og:image` personalizado por contenido** | Bloqueado por D-08 → `Task/030` (§8) |
| **Cabeceras HTTP de respuesta**, incluida `X-Robots-Tag` | `Task/018` (**S-05**) |
| **CORS efectivo** | `Task/018` |
| Auditoría de la configuración de sanitización | `Task/018` |
| Logs JSON, correlation ID, healthchecks | `Task/017` |
| Dominio concreto y DNS (**D-07**) | `Task/035` |
| Automatización de estas verificaciones en CI | `Task/019`–`Task/021` |
| Validación con **contenido real publicado** | `Task/022` (semilla local) |
| Core Web Vitals **de campo** | Ninguno en el MVP: exige tráfico real |
| Restringir `provider` en el backend | Sin propietario; candidata `Task/018` |
| Modo oscuro, rediseño visual, nueva identidad | Sin tarea: no lo pide ninguna fuente |

---

## 6. Matriz SEO — E-01 a E-08

Estado medido el 2026-09-05 sobre el entorno local (`http://localhost:8081`, Compose de
`Task/007`) y sobre `dist/` recién construido. Detalle de la medición en §13.

| # | Requisito (literal de NFR §4) | Owner | Estado medido | Superficies | Repo | Evidencia necesaria | Cambio previsto |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **E-01** | Slugs legibles y estables en todo el contenido público | `Task/008`, `Task/014` | **Cumplido.** Las rutas de detalle son `/articulos/:slug`, `/reviews/:slug`, `/proyectos/:slug`; `slug` es `UNIQUE NOT NULL` | 3 rutas de detalle | — | Regresión: la tabla de rutas sigue usando slug y no id | **Ninguno** |
| **E-02** | `title` y `description` propios por página | **`Task/016`** | **Parcial.** `title` correcto por URL **con JS** (11/11 medidas). `description` **ausente en todas**. Sin JS, `title` es siempre `Blog personal` | 12 públicas | frontend | `title` y `description` por URL, verificados con y sin JS | `description` nuevo; `title` conservado |
| **E-03** | Open Graph para compartir en redes | **`Task/016`** | **Ausente.** 0 etiquetas `og:*` en las 16 URL medidas, con y sin JS | 12 públicas | frontend | OG completo; `og:image` estable | OG nuevo. **Limitación estructural en §7** |
| **E-04** | Canonical URL en cada página pública | **`Task/016`** | **Ausente.** 0 `link[rel=canonical]` | 12 públicas | frontend | Canonical absoluto y correcto por URL | Canonical nuevo; exige origen configurable (§6.1) |
| **E-05** | Sitemap generado a partir del contenido publicado | **`Task/016`** | **Ausente y defectuoso.** `GET /sitemap.xml` responde **HTTP 200 con el `index.html` de la SPA**, no un 404 ni un sitemap | ruta propia | backend + frontend | Sitemap válido, solo `published` | Endpoint nuevo (§9) |
| **E-06** | `robots.txt` coherente; el panel no se indexa | **`Task/016`** | **Ausente y defectuoso.** `GET /robots.txt` responde **HTTP 200 con el `index.html` de la SPA**. `/admin/acceso` no tiene `meta robots` | raíz + `/admin/*` | frontend | `robots.txt` real servido como `text/plain`; `noindex` en el panel | `robots.txt` nuevo y `noindex` (§9.3) |
| **E-07** | Datos estructurados cuando corresponda | **`Task/016`** | **Ausente.** 0 bloques `application/ld+json` | 5 superficies (§10) | frontend | JSON-LD válido, solo con campos que el DTO trae | JSON-LD nuevo, acotado por §10 |
| **E-08** | El contenido no publicado **nunca** aparece en sitemap ni es indexable | **`Task/016`** | **Vacuamente cierto** hoy: no hay sitemap. Debe garantizarse por construcción al crearlo | sitemap | backend | Prueba de que un `draft` y un `archived` no aparecen | Garantía por diseño (§9.2) |

### 6.1 Dependencia transversal — el origen público absoluto

**E-04**, `og:url` y **E-05** exigen **URL absolutas**. Hoy el frontend solo conoce
`VITE_API_BASE_URL`; **no conoce su propio origen**. Y **D-07** (dominio concreto) está
**abierta** hasta `Task/035`, así que el valor real no puede fijarse aquí.

**Propuesta — pendiente de aprobación.** El origen público es **configuración**, no una
constante:

- Frontend: nueva variable de build `VITE_SITE_BASE_URL`, validada en `readAppConfig` con
  el mismo rigor que `VITE_API_BASE_URL` (absoluta, `http`/`https`, sin barra final).
- Backend: nueva variable `BLOG_PUBLIC_SITE_BASE_URL`, validada al arrancar (**T-01**),
  necesaria para que el sitemap emita URL del **sitio**, no del API.
- Ninguna de las dos codifica un dominio. `.env.example` lleva el valor local
  (`http://localhost:8081`) y `Task/034`/`Task/035` fijan el productivo.

Esto **no** adelanta D-07: nombra la variable, no el dominio.

### 6.2 Inventario SEO ruta por ruta

Partiendo de las rutas públicas **reales** que entregó `Task/014` (decisión D-014-A,
`src/lib/rutas.ts` y la tabla de rutas). **No existe `/videos/:slug`**: el contrato no
tiene detalle de video, y un resultado de búsqueda de tipo `video` va al listado con un
ancla (D-014-J).

Convenciones de la tabla: `SITE` = `NOMBRE_DEL_SITIO` (`Blog personal`); `BASE` =
`VITE_SITE_BASE_URL`; `·` es el separador de título ya vigente en `useDocumentTitle`.

| Ruta | `title` | `description` | `canonical` | `robots` | `og:type` | `og:title` | `og:description` | `og:url` | `og:image` | JSON-LD | Fuente de datos | Estados loading / error / 404 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `/` | `SITE` | Fija, propia del sitio | `BASE/` | *(índice)* | `website` | `SITE` | = `description` | `BASE/` | Estática de sitio | `WebSite` + `SearchAction` | Estático + 5 bloques destacados | Cada bloque con su estado propio; ninguno bloquea al otro |
| `/quien-soy` | `Quién soy · SITE` | `profile.seo_description ?? headline` | `BASE/quien-soy` | *(índice)* | `profile` | `profile.seo_title ?? full_name` | = `description` | `BASE/quien-soy` | Estática de sitio | `Person` | `GET /profile` | `404` de perfil = estado explícito (**D-009-N**); sin perfil **no** se emite `Person` |
| `/articulos` | `Artículos · SITE` | Fija de sección | `BASE/articulos` | *(índice)* | `website` | `Artículos · SITE` | = `description` | `BASE/articulos` | Estática de sitio | — | `GET /posts`, `GET /tags` | loading / vacío / error ya entregados |
| `/articulos/:slug` | `post.seo_title ?? post.title · SITE` | `post.seo_description ?? post.summary` — **resoluble garantizada** (§14.5 del contrato) | `BASE/articulos/<slug>` | *(índice)* | `article` | = `title` | = `description` | canonical | Estática de sitio — **§8**: la portada está bloqueada por **D-08** | `Article` + `BreadcrumbList` | `GET /posts/{slug}` | `404` → la 404 fija su propio `title` y **`noindex`** |
| `/reviews` | `Reviews de libros · SITE` | Fija de sección | `BASE/reviews` | *(índice)* | `website` | ídem sección | = `description` | `BASE/reviews` | Estática de sitio | — | `GET /book-reviews`, `GET /tags` | ídem listados |
| `/reviews/:slug` | `review.seo_title ?? title · SITE` | `seo_description ?? summary` | `BASE/reviews/<slug>` | *(índice)* | `article` | = `title` | = `description` | canonical | Estática de sitio | `Review` de `Book` + `BreadcrumbList` | `GET /book-reviews/{slug}` | `404` → 404 con `noindex` |
| `/videos` | `Videos · SITE` | Fija de sección | `BASE/videos` | *(índice)* | `website` | ídem sección | = `description` | `BASE/videos` | Estática de sitio | — *(§10: `VideoObject` descartado)* | `GET /videos`, `GET /tags` | ídem listados |
| `/proyectos` | `Proyectos y laboratorio · SITE` | Fija de sección | `BASE/proyectos` | *(índice)* | `website` | ídem sección | = `description` | `BASE/proyectos` | Estática de sitio | — | `GET /projects`, `GET /tags` | ídem listados |
| `/proyectos/:slug` | `proyecto.seo_title ?? title · SITE` | `seo_description ?? summary` | `BASE/proyectos/<slug>` | *(índice)* | `article` | = `title` | = `description` | canonical | Estática de sitio | `Article` + `BreadcrumbList` | `GET /projects/{slug}` | `404` → 404 con `noindex` |
| `/contacto` | `Contacto · SITE` | Fija de sección | `BASE/contacto` | *(índice)* | `website` | ídem sección | = `description` | `BASE/contacto` | Estática de sitio | — | `GET /profile` | `404` de perfil = estado explícito |
| `/buscar?q=` | `Resultados para «q» · SITE` | Fija, **no** derivada de `q` | **Ninguno** — CORREGIDO | **`noindex,follow`** | `website` | Fija | Fija | `BASE/buscar` | Estática de sitio | — | `GET /search` | loading / vacío / aviso si `q` es corto |
| **404** | `Página no encontrada · SITE` | Fija | **Ninguno** | **`noindex,follow`** | — | — | — | — | — | — | Ninguna | Es el estado |
| `/admin/*` (18) | Ya lo fija `Task/015` | **Ninguna** | **Ninguno** | **`noindex,follow`** — CORREGIDO | — | — | — | — | — | — | Contrato administrativo | Ya entregados |

**Cinco decisiones de esta tabla, con su motivo:**

1. **`/buscar` es `noindex` y NO emite `canonical`.** Una página de resultados por término
   genera infinitas URL de contenido duplicado, y `noindex,follow` ya lo resuelve.
   **CORREGIDO al implementar:** esta ficha proponía además un `canonical` a `/buscar` sin
   `q`; declarar canónica una URL que se pide **no** indexar son señales contradictorias, y
   el componente `Seo` no emite `canonical` en ninguna página no indexable.
2. **Ninguna `description` se deriva de `q`** ni de texto que escriba un visitante: sería
   inyectar entrada de usuario en un metadato.
3. **Los detalles tienen `description` garantizada.** No es optimismo: `api-contracts.md`
   §14.5 impide publicar sin una descripción SEO **resoluble**. Por eso el *fallback*
   `seo_description ?? summary` **nunca** queda vacío en contenido publicado.
4. **`og:type=article`** en los tres detalles y `website` en el resto. Para `/quien-soy` se
   usa `profile`, que es el tipo que Open Graph define para una persona.
5. **`og:image` es la misma imagen estática en todas.** No es una simplificación: es la
   consecuencia directa de **B-016-1** (§8.5).

---

## 7. Estrategia *crawler* / *rendering* y criterio de reconsideración

### 7.1 Lo que se midió, no lo que se supone

`STAGE-05` prohíbe expresamente dar el SEO por bueno *«por estar el código escrito»*, y
el prompt de esta fase prohíbe la prueba tautológica sobre el DOM ya hidratado. Se midió
en **cuatro canales distintos** el 2026-09-05.

| Canal | Método | Resultado |
| --- | --- | --- |
| 1. Petición HTTP directa | `curl` a 16 URL, incluidas rutas profundas | **Las 16 devuelven HTTP 200 y el mismo cuerpo de 785 bytes**: `dist/index.html` |
| 2. *Crawler* sin ejecutar JS | El mismo cuerpo, analizado sin motor JS | `title` = `Blog personal` en **todas**. `description`, `canonical`, `og:*`, `meta robots` y JSON-LD: **0 en todas** |
| 3. *User-agent* de *crawler* conocido | `Googlebot/2.1`, `facebookexternalhit/1.1`, `Twitterbot/1.0` | **Respuesta idéntica** a la de `curl` sin UA especial. El servidor no diferencia |
| 4. Navegador real con JS | Chrome 152 *headless* por CDP, 11 rutas, tras hidratar | `title` **correcto y propio por URL** (11/11) y `h1` único correcto. `description`, `canonical`, `og:*`, `meta robots`, JSON-LD: **0 en todas** |

**Conclusión de la medición: hay dos problemas distintos, y confundirlos sería el error.**

### 7.2 Problema A — falta de implementación (resoluble aquí)

`description`, `canonical`, Open Graph y JSON-LD **no están escritos**. Es trabajo normal
de esta tarea y se resuelve en el cliente. Para el canal 4 —y para Googlebot, que **sí**
renderiza JavaScript— esto basta.

### 7.3 Problema B — limitación estructural del *rendering* en cliente

Aunque se implemente **perfectamente** en el cliente, el canal 2 seguirá recibiendo un
documento sin metadatos: un *crawler* que no ejecuta JavaScript no puede ver etiquetas que
solo existen después de hidratar. Esto **no** se arregla escribiendo mejor el código.

Y afecta de lleno a **E-03**, porque el propósito canónico de E-03 no es genérico:

> `MVP_SCOPE.md` §2.2 — *«Compartir páginas mediante **metadatos Open Graph**»*.
> `STAGE-05` — *«muchos *crawlers* de redes sociales **no ejecutan JavaScript**»*.

Los consumidores de Open Graph son exactamente los agentes que no ejecutan JS. Por tanto:

> **La inyección de Open Graph en cliente no puede satisfacer E-03 por URL.** No es una
> preferencia de *stack*: es el resultado de la medición contrastado con el propósito
> declarado del requisito.

### 7.4 Qué sí puede entregar `Task/016` sin cambiar la estrategia

`dist/index.html` es **un solo documento** compartido por las 12 rutas, así que puede
llevar **un** juego de metadatos, no doce.

| Alcance | Sin JS | Con JS |
| --- | --- | --- |
| Metadatos **de sitio** en `index.html` — **CORREGIDO**: solo `og:site_name`, `og:image` (con sus dimensiones y `alt`) y `twitter:card` | ✔ correctos para **cualquier** URL | ✔ |
| Metadatos **por URL**: `title`, `description`, `canonical`, `og:*` por página, JSON-LD | ✘ | ✔ |
| `robots.txt` como archivo estático real | ✔ | ✔ |
| `sitemap.xml` desde el backend | ✔ | ✔ |
| `noindex` de `/admin/*` y de la 404 | ✘ en el marcado; ✔ vía `robots.txt` para `/admin/` | ✔ |

> **CORREGIDO al implementar.** Esta ficha proponía llevar también `description` y
> `og:title` de sitio a `index.html`. **Se midió y se descartó:** React 19 iza los
> metadatos al `<head>` pero **no deduplica**, así que una etiqueta estática y otra
> dinámica con el mismo `name`/`property` **coexisten**. Declarar allí algo que `Seo`
> también emite produciría duplicados contradictorios en toda página. En `index.html`
> queda **solo lo constante por sitio**, que además es información correcta para
> cualquier URL. Evidencia en el [reporte §3.2](../task-reports/TASK-016-report.md).

### 7.5 CRITERIO DE RECONSIDERACIÓN

Redactado a partir de `STAGE-05` y `ADR-005`, no copiado de un enunciado externo.

> **Criterio.** Si, tras implementar los metadatos en cliente, un *crawler* que **no
> ejecuta JavaScript** no recibe `title`, `description`, `canonical` y Open Graph
> **propios de la URL solicitada**, entonces el *rendering* exclusivamente en cliente
> **no satisface E-02, E-03, E-04 ni E-07 para ese canal**, y `Task/016` debe:
>
> 1. **Registrar la limitación** con la evidencia de los cuatro canales.
> 2. **Abrir la reconsideración** de la estrategia de *rendering* —prerender, SSG o SSR—
>    como **decisión nueva con su propio ADR**.
> 3. **No resolverla aquí.** `STAGE-05` lo excluye del alcance de la etapa y `ADR-005`
>    sigue **Aceptado** mientras no se reemplace.
> 4. **No cambiar el *stack* por reflejo.** Vite y `ADR-005` siguen vigentes.

**Evaluación con el baseline ya medido: el criterio se cumple, es decir, el *rendering* en
cliente NO satisface el canal 2.** Está demostrado antes de escribir una línea, porque el
documento servido es idéntico para las 16 URL. La implementación en cliente puede mejorar
los canales 1, 3 y 4, pero **no puede** cambiar el canal 2.

**Consecuencia para la ejecución:** `Task/016` debe **abrir** la reconsideración con un
ADR en estado **Propuesta**, y **no** declarar E-03 cerrado. Detalle del bloqueo en §16.

---

## 8. `og:image` frente a D-08

### 8.1 La tensión, exacta

| Fuente | Qué exige o reserva |
| --- | --- |
| `ROADMAP.md` y `STAGE-05` | `og:image` con **URL estable, no expirable**. Owner: `Task/016` |
| `open-decisions.md` D-08 | *«Qué URL usa `og:image`, que un crawler debe poder leer sin autenticación y sin que caduque»* — pregunta abierta, cuyo **contexto** (URL estable de medios, semántica de caché, CDN, TTL) resuelve `Task/030` |
| `api-contracts.md` §12 | `access_url` es **enlace temporal**, se genera al servir y **caduca**. `object_key` **no** es campo del contrato |
| Regla vigente en D-08, que **no espera** a D-08 | *«Nunca se persiste una URL prefirmada como dato canónico»* |
| `Task/015` D-015-E | *«No se insertan URLs `access_url` caducables. La URL estable de medios continúa en D-08 / `Task/030`»* |

### 8.2 Lo que queda descartado por las fuentes, no por preferencia

- **`access_url` como `og:image`: prohibido.** Caduca (900 s por defecto) y publicarlo en
  una etiqueta que un *crawler* leerá días después produce una imagen rota. Contradice la
  regla vigente y el requisito de no expirable.
- **Derivar una URL desde `object_key`: imposible y prohibido.** El contrato no transporta
  `object_key`, y el bucket es privado.
- **Crear una URL pública de medios aquí: robar alcance.** Es literalmente la pregunta de
  D-08 que `Task/030` resuelve.

### 8.3 Alternativas comparadas

| Alternativa | E-03 | No expirable | Personalización por contenido | Impacto en D-08 | Impacto en `Task/030` |
| --- | :---: | :---: | :---: | --- | --- |
| **A.** `access_url` de la portada | ✔ formal | **✘** | ✔ | **Contradice** la regla vigente | Crea deuda a corregir |
| **B.** Imagen OG **estática del sitio**, versionada en `public/` del frontend | ✔ a nivel de sitio | **✔** por construcción: activo estático del mismo origen | **✘** | **Ninguno**: no toca medios ni CDN | Ninguno: `Task/030` podrá añadir la personalizada |
| **C.** Endpoint backend que redirija a la imagen | ✔ | Depende | ✔ | **Decide** semántica de caché → **es** D-08 | Invade |
| **D.** No emitir `og:image` | **✘** | — | ✘ | Ninguno | Ninguno |

### 8.4 Decisión D-016-A — **Vigente** (2026-09-06)

> **Vigente** desde la aprobación de `Task/016`. Alternativa **B**: `og:image` apunta a una
> **imagen estática propia del sitio**, versionada en `personal-blog-frontend/public/`,
> servida desde el mismo origen que el sitio.
>
> **Por qué.** Es la única que satisface *«URL estable y no expirable»* **sin** decidir
> nada de lo que D-08 reserva a `Task/030`. Un activo estático del propio sitio no tiene
> expiración, no necesita autenticación y su semántica de caché es la de `dist/`, ya
> fijada por `Task/007`.
>
> **Precedente.** Es exactamente el criterio con el que `Task/014` resolvió el favicon
> (**D-014-E**): una marca geométrica neutra con los tokens del sistema de diseño, sin
> inventar identidad visual que el producto no ha definido.
>
> **Qué NO decide.** No dice si existe una URL pública estable para los **medios**, ni su
> semántica de caché, ni el TTL productivo, ni la CDN. **D-08 sigue abierta.**

### 8.5 Lo que queda bloqueado, declarado sin maquillar

> **B-016-1 — `og:image` personalizado por contenido: BLOQUEADO por D-08.**
>
> Una vista previa social que muestre **la portada del artículo compartido** exige una URL
> de medio pública y estable que **hoy no existe** y cuya existencia es la pregunta
> abierta de D-08, propiedad de `Task/030`.
>
> `Task/016` entrega la imagen de sitio (§8.4) y **declara la limitación**. No la disimula
> con un `access_url`, y no cierra D-08 para desbloquearse.

---

## 9. Sitemap, `robots.txt` y 404

### 9.1 Sitemap — alternativas comparadas

Contrastadas contra el contrato público **real**: `api-contracts.md` §5 —*«toda colección
está paginada; no existe ningún endpoint que devuelva todo»*, `page_size` máximo **50**,
parámetros desconocidos rechazados con `422`— y §3 —los recursos públicos **nunca**
devuelven `draft` ni `archived`.

| Criterio | **A. Frontend en build** | **B. Backend en runtime** | **C. Híbrido / prerender** | **D. Sin sitemap** |
| --- | --- | --- | --- | --- |
| Fuente de verdad | El API **en el instante del build** | La base de datos, **siempre actual** | El API en el build | — |
| Actualización al publicar | **No.** Exige reconstruir; Cloudflare Pages construye con un *push* de Git, no al publicar contenido | **Sí**, inmediata | **No** | — |
| Compatibilidad local | Rompe una propiedad vigente: hoy `npm run build` **no necesita red** | ✔ Ya hay backend local | Rompe la misma propiedad | ✔ |
| Cloudflare Pages + API | Frágil: obligaría a un *webhook* de reconstrucción, que nadie ha decidido | ✔ Sirve desde el API; se referencia desde `robots.txt` | Frágil | ✔ |
| **T-05** *(build estático estándar)* | **Lo compromete**: el build pasaría a depender de un servicio | ✔ Intacto | Lo compromete | ✔ |
| Costo y complejidad | Script de prebuild + paginación de 4 colecciones | Endpoint nuevo, test-first | Alta: es la decisión de *rendering* diferida | Nulo |
| **E-08** garantizado | Por confianza en el cliente | **Por construcción**: los repositorios solo leen `published` | Por confianza | Vacuo |
| Tests | Unitarios sobre el script; sin datos reales | Unidad + **integración con PostgreSQL real** (B-6) | — | — |
| Veredicto | Descartada | **Recomendada** | Fuera de alcance (§5) | Incumple **E-05** |

### 9.2 Decisión D-016-B — **Vigente** (2026-09-06)

> **Vigente** desde la aprobación de `Task/016`. Alternativa **B**: el **backend** genera el
> sitemap en *runtime*.
>
> **Por qué.** Es la única en la que **E-08 se cumple por construcción** y no por
> confianza: reutiliza los mismos repositorios que ya garantizan que un `draft` o un
> `archived` nunca salen por la API pública, propiedad fijada por prueba en `Task/009`. Y
> es la única que no degrada **T-05**.
>
> **Contrato propuesto** (a cerrar test-first, §14):
> - Ruta: **`GET /sitemap.xml`**, **fuera** del prefijo `/api/v1`, con el mismo criterio
>   con el que `/health` vive fuera: no es contrato de datos versionado, es un artefacto
>   de protocolo web.
> - `Content-Type: application/xml`.
> - Contiene: `/`, `/quien-soy`, `/articulos`, `/reviews`, `/videos`, `/proyectos`,
>   `/contacto`, más una entrada por cada contenido `published` de los **tres** tipos con
>   ruta de detalle. **No** `/buscar`, **no** `/admin/*`, **no** la 404, **no**
>   `/videos/:slug` — que no existe.
> - `<lastmod>` ← `published_at`. **No** `updated_at`: no está en el DTO público, y
>   `Task/016` no amplía el contrato para un dato que ninguna fuente pide.
> - Las URL son del **sitio**, construidas con `BLOG_PUBLIC_SITE_BASE_URL` (§6.1).
> - Sin paginación: el sitemap no es una colección de la API. Si algún día supera los
>   límites del protocolo (50 000 URL / 50 MB), se parte en índice — deuda declarada, no
>   resuelta ahora.

### 9.3 `robots.txt` — E-06

`robots.txt` **debe** servirse desde la raíz del origen del sitio: es un requisito del
protocolo, no una preferencia. Por tanto es un archivo **estático del frontend**, no del
backend.

| Pieza | Dónde | Qué hace | Owner |
| --- | --- | --- | --- |
| `robots.txt` | `personal-blog-frontend/public/robots.txt` | `Disallow: /admin/`; `Sitemap:` apuntando al sitemap | **`Task/016`** |
| `<meta name="robots" content="noindex,follow">` | Marcado de `/admin/*` y de la 404 | Refuerza en el canal que **sí** ejecuta JS | **`Task/016`** |
| `X-Robots-Tag` | Cabecera HTTP de respuesta | Sería el único canal fiable sin JS para el panel | **`Task/018`** (**S-05**) |

**Tres precisiones que no se pueden omitir:**

1. **`robots.txt` no protege nada.** Es una petición a agentes que colaboran. El control
   de acceso al panel es la sesión de `Task/011` y las guardas de `Task/015`, y lo sigue
   siendo. Confundirlos sería un defecto de seguridad.
2. **La línea `Sitemap:` necesita una URL absoluta**, y **D-07 está abierta**. Propuesta:
   generar `robots.txt` en el build desde `VITE_SITE_BASE_URL` y, **si no está definida,
   omitir la línea `Sitemap:`** en lugar de emitir una URL falsa.
3. **Sitemap en otro *host*.** Con **D-15** el sitio vive en el dominio raíz y el API en
   un subdominio, así que un sitemap servido por el API es **cross-host**. La vía estándar
   y aceptada es declararlo en el `robots.txt` del sitio, y **el protocolo no exige que
   sitio y sitemap compartan *host***.

   > **CORREGIDO.** Esta ficha registraba como deuda que `Task/034` hiciera que
   > compartieran *host* mediante una reescritura en Cloudflare Pages. **No es un
   > requisito del protocolo**, así que esa deuda se **retira**: no era una dependencia
   > real de `Task/034`, que conserva únicamente sus responsabilidades de *hosting* y del
   > código HTTP `404`.
   >
   > La URL del `Sitemap:` se compone con `VITE_API_BASE_URL`, que ya representa el origen
   > del API: **no se añade una tercera variable** por comodidad.

### 9.4 404 — frontera exacta con `Task/034`

Medido: el `nginx.conf` local resuelve `try_files $uri $uri/ /index.html`, así que
**cualquier** ruta inexistente responde **HTTP 200**. `USER_FLOWS.md` A.11 exige *«el
código HTTP correcto para no ser indexada»*.

| Elemento | Puede garantizarlo `Task/016` | Por qué |
| --- | :---: | --- |
| Página 404 correcta, con navegación y `title` propio | **Ya entregado** por `Task/014` | — |
| `<meta name="robots" content="noindex">` en la 404 | **Sí** | Marcado del cliente; verificable en local |
| La 404 **excluida** del sitemap | **Sí** | Por construcción: el sitemap se enumera, no se descubre |
| `Disallow` coherente en `robots.txt` | **Sí** | Archivo estático |
| **HTTP 404 real** en una ruta inexistente | **No** | Un servidor estático no puede distinguir `/articulos/slug-real` de `/ruta-inventada` sin conocer los slugs. Enumerar prefijos rompería los slugs; resolverlo de verdad es prerender o configuración del *hosting* |
| HTTP 404 en Cloudflare Pages | **No — es `Task/034`** | Depende del proveedor |

> **`Task/016` no absorbe `Task/034`.** Entrega el `noindex` y la coherencia de
> `robots.txt`; el **código HTTP** sigue siendo de `Task/034`, y la deuda 3 de `Task/014`
> permanece abierta en su mitad de *hosting*.

---

## 10. Datos estructurados — E-07

**Regla que gobierna esta sección:** no se emite ninguna propiedad que el DTO público real
no alimente. Un JSON-LD con datos inventados es peor que ninguno.

Habilita el diseño una garantía del contrato: `api-contracts.md` §14.5 exige, **al
publicar**, `title`, `slug` y una descripción SEO **resoluble** (`seo_description` **o**
`summary`), y para `BookReview` además `book_title`, `book_author` y `rating`. Es decir:
**todo contenido publicado tiene los campos que estos esquemas necesitan.**

| Tipo | Ruta | Campos obligatorios | Campo del DTO que lo alimenta | Opcionales incluidos | Si falta | Riesgo de dato ficticio |
| --- | --- | --- | --- | --- | --- | --- |
| `WebSite` | `/` | `name`, `url` | `NOMBRE_DEL_SITIO`, `VITE_SITE_BASE_URL` | `potentialAction` → `SearchAction` sobre `/buscar?q=` | — | **Nulo**: la ruta de búsqueda existe |
| `Person` | `/quien-soy` | `name` | `ProfilePublico.full_name` | `description` ← `headline`; `sameAs` ← `social_links[].url` | Si `/profile` responde `404` (D-009-N), **no se emite** | **Nulo**. `jobTitle` **no** se emite: `headline` es un lema, no un cargo |
| `Article` | `/articulos/:slug` | `headline` | `title` | `description` ← `seo_description ?? summary`; `datePublished` ← `published_at`; `keywords` ← `tags[].name` | Fail-closed: sin `title` no se emite | `dateModified` **no** se emite: `updated_at` no está en el DTO. `image` y `author`: §10.1 |
| `Review` de `Book` | `/reviews/:slug` | `itemReviewed`, `reviewRating` | `book_title`, `book_author`, `rating` — los tres **garantizados** al publicar | `reviewBody` ← `summary`; `datePublished` | Si alguno es `null`, **no se emite** el bloque completo | **Nulo.** `bestRating: 5` y `worstRating: 1` están en **D-D** de `data-model.md`, no inventados |
| `BreadcrumbList` | 3 rutas de detalle | `itemListElement` | La jerarquía real de rutas de `lib/rutas.ts` | — | — | **Nulo** |

**No se emiten** —y la razón importa más que la lista—:

- `Project` como `SoftwareApplication` o `CreativeWork`: ninguna fuente lo pide y el DTO no
  trae los campos que esos tipos esperan.
- `ItemList` / `CollectionPage` en los listados: aportan poco y obligarían a decidir cómo
  se representa la paginación.
- `VideoObject` en `/videos`: exigiría `contentUrl` o `embedUrl` **y** `thumbnailUrl` y
  `uploadDate`; la miniatura solo está disponible como `access_url` **caducable** (§8) y no
  hay detalle de video.
- `Organization`: el sitio es una persona, no una organización.

### 10.1 Dos limitaciones honestas de `Article`

1. **`image`.** Los *rich results* de artículo de Google piden imagen. La única imagen del
   artículo es su portada, accesible solo por `access_url` **caducable** → prohibido (§8).
   Se emite sin `image`, o con la imagen estática de sitio, y **se declara** que el *rich
   result* completo depende de **D-08**.
2. **`author`.** Exigiría una petición extra a `GET /profile` en cada detalle, que hoy no
   se hace, con costo en **P-01**. **Propuesta:** no añadir la petición; emitir `author`
   solo si el perfil ya está en memoria. Alternativa a decidir en la implementación con la
   medición delante.

---

## 11. Matriz de accesibilidad — A-01 a A-08

`Task/016` **no reimplementa** lo que `Task/013`–`Task/015` ya entregaron: **audita, mide,
detecta *gaps* reales y corrige solo los demostrados**. Estado medido el 2026-09-05 con
Chrome 152 *headless* por CDP sobre 4 superficies reales.

| # | Requisito | Owner original | Evidencia heredada | Evidencia nueva necesaria | Herramienta | Rutas | Resultado baseline | *Gap* | Corrección |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **A-01** | Navegación con teclado completa | `Task/013`–**`016`** | Iniciada en `013`, continuada en `014` y `015`; solo controles nativos | **Recorrido real con `Tab`/`Shift+Tab`** en sitio y panel | CDP `Input.dispatchKeyEvent` | 4 medidas; ampliar a las 12 públicas + panel | **Excelente.** 58 paradas medidas: **0 sin indicador de foco**; anillo `2px solid rgb(10,90,214)` en el 100 %; enlace de salto **primero** en las 4; orden lógico; **sin trampas**: el recorrido vuelve a `body`; `Shift+Tab` invierte correctamente | **Ninguno detectado** en lo medido | Ampliar cobertura y **cerrar A-01** |
| **A-02** | HTML semántico | `Task/014` | `header`/`nav`/`main`/`footer`, un `h1` por página | Jerarquía sin saltos en las 12 | CDP + pruebas | 4 medidas | **Cumple.** 1 `h1` por página; **0 saltos** de nivel; `main` presente en las 4 | Ninguno | — |
| **A-03** | Labels en formularios | `Task/015` | `<label htmlFor>` en los 9 formularios | Ningún control sin nombre accesible | CDP | `/admin/*`, `/buscar` | **Cumple.** **0 controles** sin `label`, `aria-label` o `aria-labelledby` | Ninguno | — |
| **A-04** | Texto alternativo | `Task/010`, `Task/014` | `alt_text` en `MediaAsset`; `MediaImage` lo renderiza; exigido al publicar | Con **imágenes reales** | CDP | detalles y listados | **No medible**: 0 imágenes renderizadas, la base está vacía | **Evidencia bloqueada** por falta de semilla (`Task/022`) | Medir con contenido; declarar si sigue bloqueado |
| **A-05** | Contraste adecuado | `Task/013` | 22 pares verificados por prueba sobre `tokens.css` | Contraste **en composición real**, no solo en tokens | Cálculo sobre estilos computados | 12 públicas | Heredado; no vuelto a medir en esta fase | Por determinar | Solo si aparece un par real que falle |
| **A-06** | Foco visible | `Task/013` | `:focus-visible` global y guarda que prohíbe `outline: none` | Foco visible en **cada parada real** | CDP | 4 medidas | **Cumple.** 0 de 58 paradas sin indicador | Ninguno | — |
| **A-07** | Sin dependencia exclusiva del color | `Task/013` | `Badge` con texto y glifo de silueta distinta | Revisión en composición | Inspección | 12 públicas | Heredado | Por determinar | Solo *gaps* demostrados |
| **A-08** | Errores de formulario anunciados | `Task/015` | `FormFeedback` con `role="alert"`/`"status"`; `aria-invalid` y `aria-describedby` en `FormField` | Con un error **realmente provocado** | CDP + pruebas | `/admin/*` | **No medible en reposo**: 0 regiones vivas presentes porque **no había error activo**. El código las emite condicionalmente | **Evidencia bloqueada** hasta provocar el error | Provocar error real y medir |

### 11.1 La afirmación que `Task/016` podrá hacer, y la que no

`Task/013`, `Task/014` y `Task/015` declararon las tres, con idéntica formulación, que
**no** afirman WCAG 2.1 AA del producto y que la auditoría es de `Task/016`. Esta tarea es
la primera que puede cerrarla — pero con un límite:

> **No se afirmará WCAG 2.1 AA porque una herramienta marque cero hallazgos.** Un
> analizador automático cubre una fracción de los criterios. La afirmación se acotará a
> **A-01…A-08 tal como NFR §3 los enuncia**, con la evidencia de cada uno y con los
> *gaps* bloqueados declarados. Los criterios cuya evidencia dependa de contenido real
> (**A-04**, **A-08**) se cerrarán o se declararán **bloqueados hasta `Task/022`**.

---

## 12. Matriz de rendimiento — P-01, P-03, P-04, P-05

### 12.1 Requisitos y estado

| # | Requisito | Owner | Estado medido | *Gap* |
| --- | --- | --- | --- | --- |
| **P-01** | Carga inicial razonable en las páginas públicas | **`Task/016`** | **Medido**, sin umbral. LCP lab **820–980 ms**; grafo inicial público = **2 recursos** (`index.js` + `index.css`) | Falta **fijar el umbral** |
| **P-03** | *Lazy loading* de imágenes fuera del área visible inicial | **`Task/016`** | **Implementado** por `Task/014`: `MediaImage` emite `loading="lazy"` salvo `prioridad="alta"`; `MarkdownRenderer` y `VideoCard` también | **Medición** bloqueada: 0 imágenes sin contenido |
| **P-04** | Imágenes optimizadas; **miniaturas para listados** | `Task/010`, **`Task/016`** | **Parcial.** `width`/`height` se emiten cuando el DTO los trae. La **miniatura no se expone** en la API pública | Exponer la miniatura (deuda 2 de `Task/010`) |
| **P-05** | Sin contenido administrativo en páginas públicas | `Task/015`, **`Task/016`** | **Cumplido y reverificado en runtime**: las rutas públicas cargan solo `index.js` + `index.css`; `admin-*.js` solo aparece en `/admin/*` | Ninguno: **preservar** y medir |

### 12.2 *Baseline* de tamaños — build determinista

De `vite build` sobre el SHA base del frontend. Los tamaños *gzip* del propio informe son
la magnitud **independiente del entorno**, y por eso son la base de los umbrales de peso.

| Artefacto | Crudo | *gzip* | ¿Grafo inicial público? |
| --- | ---: | ---: | :---: |
| `index-*.js` (entrada) | 323,09 kB | **100,33 kB** | **Sí** |
| `index-*.css` | 13,21 kB | **3,15 kB** | **Sí** |
| `MarkdownRenderer-*.js` | 121,62 kB | 37,11 kB | No — diferido |
| `MarkdownRenderer-*.css` | 1,15 kB | 0,35 kB | No |
| `admin-*.js` | 41,13 kB | 11,25 kB | No — solo `/admin/*` |
| `admin-*.css` | 3,51 kB | 0,94 kB | No |
| `index.html` | 0,78 kB | 0,48 kB | Sí |

### 12.3 *Baseline* de tiempos — laboratorio, declarado como tal

Chrome 152 *headless* por CDP contra `http://localhost:8081`, red emulada **10 Mbps /
40 ms RTT**, CPU **4×** de estrangulamiento, caché deshabilitada.

| Ruta | LCP | CLS | DCL | Load | Recursos | Transferido |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `/` | 820 ms | **0,0359** | 557 ms | 558 ms | 8 | 332,1 kB |
| `/articulos` | 932 ms | 0,0000 | 648 ms | 649 ms | 5 | 330,9 kB |
| `/quien-soy` | 980 ms | 0,0000 | 640 ms | 642 ms | 4 | 330,7 kB |
| `/admin/acceso` | 1252 ms | 0,0000 | 692 ms | 787 ms | 6 | 374,5 kB |

**Cuatro advertencias que impiden leer mal esta tabla:**

1. **Son métricas de laboratorio.** No son Core Web Vitals de campo y no se presentarán
   como tales, en línea con la exigencia de no afirmar campo desde laboratorio.
2. **El entorno local NO comprime.** `docker/nginx.conf` no tiene ninguna directiva
   `gzip`; se verificó que la respuesta del *bundle* llega con
   `Content-Length: 322874` y **sin** `Content-Encoding`. Lo transferido es ~3× lo que
   entregaría un *hosting* que comprima. Por eso los umbrales de **peso** se fijan sobre
   el *gzip* del build, no sobre lo transferido en local.
3. **`FCP` no se pudo capturar** con este arnés: la entrada de *paint* no estaba
   disponible. Se declara ausente en lugar de estimarla.
4. **El *chunk* de Markdown no se cargó en ninguna ruta medida**, porque no hay contenido:
   su peso está medido en el build, pero su carga en *runtime* **no**.

### 12.4 Umbrales propuestos

**Vigentes** desde la aprobación de `Task/016`. Ninguno es arbitrario: todos se anclan al
baseline con holgura explícita, y cada uno declara **qué lo haría fallar** — un umbral que
nada puede violar no es un umbral.

| # | Métrica | Herramienta | Entorno | Página | Baseline | **Umbral** | Racional | Qué lo haría fallar |
| --- | --- | --- | --- | --- | ---: | ---: | --- | --- |
| U-1 | JS del grafo inicial público, *gzip* | Informe de `vite build` | Determinista | Entrada | 100,33 kB | **≤ 120 kB** | ~20 % de holgura | Que el panel o el Markdown entren en el grafo inicial |
| U-2 | CSS del grafo inicial público, *gzip* | Informe de `vite build` | Determinista | Entrada | 3,15 kB | **≤ 6 kB** | Holgura amplia sobre una hoja pequeña | Un CSS de página sin `import` diferido |
| U-3 | *Chunk* Markdown | `vite build` + grafo de `dist/` | Determinista | — | 37,11 kB | **≤ 45 kB y fuera del grafo inicial** | `ADR-005` exige carga diferida; el umbral protege la **exigencia** | Importar `MarkdownContent` de forma estática |
| U-4 | *Chunk* administrativo | `vite build` + grafo de `dist/` | Determinista | — | 11,25 kB | **≤ 15 kB y fuera del grafo inicial** | **P-05** | Un `import` estático del panel |
| U-5 | Recursos del grafo inicial | CDP `Network` | Lab declarado | Rutas públicas | 4–8 | **≤ 12** | Acota cascadas; Inicio ya hace 5 peticiones (riesgo 8 de `Task/014`) | Añadir peticiones en serie |
| U-6 | LCP | CDP, `PerformanceObserver` | 10 Mbps / 40 ms / CPU 4× | Rutas públicas | 820–980 ms | **≤ 2000 ms** | ~2× el peor valor medido; margen para contenido real, que hoy no existe | Una imagen de portada grande sin dimensiones |
| U-7 | CLS | CDP, `PerformanceObserver` | ídem | Rutas públicas | 0,0000–0,0359 | **≤ 0,10** | Umbral «bueno» de Core Web Vitals; el baseline ya lo cumple | Imágenes sin `width`/`height` |
| U-8 | Imágenes fuera del *viewport* inicial con `loading="lazy"` | Prueba + CDP | — | Listados y detalles | 100 % en código | **100 %** | **P-03** | Un `<img>` nuevo sin pasar por `MediaImage` |
| U-9 | Imágenes con `width` y `height` | Prueba + CDP | — | Listados y detalles | 100 % de los que el DTO los trae | **100 %** | **P-04**, y protege U-7 | Renderizar sin dimensiones |

**No se propone umbral de INP ni de TBT.** INP es una métrica **de campo** y no se
afirmará desde laboratorio. TBT sería un *proxy* de laboratorio legítimo, pero **no se
midió** en esta fase: proponer un número sin baseline sería exactamente lo que esta ficha
prohíbe. Se mide primero, y solo entonces se decide si merece umbral.

### 12.5 Hallazgo de infraestructura local

El entorno local sirve **sin compresión**, así que ninguna medición local de bytes
transferidos representa producción, donde Cloudflare Pages comprime.

**CORREGIDO — no se ejecuta.** El usuario no autorizó tocar la configuración del servidor
local en esta tarea, así que **no se modificó nada**. Y la deuda **no se asigna a
`Task/018`**: ninguna fuente canónica la hace propietaria de la compresión del servidor
estático local. Queda registrada **sin propietario**.

La consecuencia práctica ya está aplicada: los umbrales de **peso** se fijan sobre el
*gzip* del *build* —independiente del entorno— y no sobre los bytes transferidos en local.

---

## 13. *Baseline* medido — 2026-09-05

### 13.1 Compuertas del frontend

| Compuerta | Comando | Resultado |
| --- | --- | --- |
| Formato | `npm run format:check` | ✔ **exit 0** — todos los archivos con estilo Prettier |
| Lint | `npm run lint` | ✔ **exit 0** — sin hallazgos |
| Tipado | `npm run typecheck` | ✔ **exit 0** |
| Pruebas | `npm run test:run` | ✔ **600 / 600** en **67** archivos — coincide con lo heredado de `Task/015` |
| Build | `VITE_API_BASE_URL=... npm run build` | ✔ **exit 0** en 813 ms, sin *warnings* |
| **P-05** heredado | `vitest run p05.guards / rutasDelPanel / favicon` con `dist/` presente | ✔ **27 / 27** |

> **Incidencia real, registrada sin adornos.** La **primera** ejecución completa de la
> suite terminó **`3 failed | 597 passed`** en 69,60 s: un caso de `routes.test.tsx` y dos
> de `formularios.test.tsx`. Los tres fallaron por **espera agotada** en `findBy*`
> (8127 ms, 5696 ms, 1170 ms), no por una aserción de comportamiento.
>
> Se comprobó, sin tocar ni un test: (1) los dos archivos **en aislamiento** dan
> **31 / 31**; (2) la **segunda** ejecución completa da **600 / 600** en 39,33 s.
>
> **Diagnóstico: inestabilidad por carga de la máquina, no regresión.** La primera
> ejecución competía con otras mediciones de esta misma sesión. El baseline vigente es
> **600 / 600 en verde**. Queda registrada como **R-016-1** (§16): una suite cuyo
> resultado depende de la carga es un problema real para CI (`Task/019`).

### 13.2 Compuertas del backend

| Compuerta | Comando | Resultado |
| --- | --- | --- |
| Lint | `ruff check .` | ✔ **exit 0** — *All checks passed* |
| Formato | `ruff format --check .` | ✔ **exit 0** — 286 archivos ya formateados |
| Tipado | `mypy` | ✔ **exit 0** — sin hallazgos en **284** archivos, modo *strict* |
| Pruebas, sin integración | `pytest -W error -q` | ✔ **788 passed, 785 skipped** |
| Pruebas, **con PostgreSQL y MinIO reales** | `pytest -W error -q` con `PERSONAL_BLOG_TEST_DATABASE_URL` y las tres de almacenamiento | ✔ **1572 passed, 1 skipped** en 190,84 s. El único omitido es `time.tzset` en Windows |

**Cero *warnings*:** la suite corre con `-W error`.

### 13.3 *Baseline* SEO por canal

Resumen en §7.1. Dos hallazgos merecen destacarse porque son **defectos**, no ausencias:

1. **`GET /robots.txt` → HTTP 200 con HTML.** Un *crawler* que pida `robots.txt` recibe el
   `index.html` de la SPA. Es peor que un `404`: una respuesta `200` con contenido no
   analizable puede interpretarse como un `robots.txt` inválido.
2. **`GET /sitemap.xml` → HTTP 200 con HTML.** Idéntico problema.

Ambos son consecuencia del `try_files ... /index.html` del *fallback* de la SPA, y ambos se
resuelven con archivos reales en `public/` y una ruta de backend.

### 13.4 Evidencia bloqueada por falta de contenido

La base de datos local está **vacía** y `GET /api/v1/profile` responde **404**
(**D-009-N**), porque la semilla es de `Task/022`.

| Evidencia | ¿Medible ahora? | Motivo |
| --- | :---: | --- |
| Metadatos de rutas **estáticas** (7 rutas) | **Sí** | No dependen de datos |
| Metadatos de rutas de **detalle** (3 rutas) | **No** | No hay contenido publicado |
| Sitemap con entradas reales | **No** | Se validará con listas vacías y con dobles de prueba en la suite |
| **E-08** con un `draft` real | **Parcial** | Demostrable en integración creando un `draft` en la base **de pruebas**; no hay que fabricar contenido en la base de desarrollo |
| `og:image` renderizado por un *crawler* real | **No** | Exige dominio público — `Task/035` |
| **A-04** con imágenes reales | **No** | 0 imágenes renderizadas |
| **A-08** con un error real | **Sí, provocándolo** | El error se puede provocar sin semilla |
| Peso del *chunk* Markdown en *runtime* | **No** | Solo carga en una página de detalle con contenido |

**No se fabricará contenido publicado** en la base de desarrollo para maquillar evidencia.
Lo que no pueda medirse se declarará bloqueado.

---

## 14. TDD y estrategia de pruebas

### 14.1 Backend — BACKEND TEST-FIRST LAW, sin excepción

El sitemap y la exposición de la miniatura son **comportamiento funcional nuevo** de la API
pública: aplican **B-1 a B-12** de la Definition of Done y
[`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md).

**Matriz de casos — se escribe y se ejecuta en RED antes de implementar.**

| # | Caso | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| S-01 | `GET /sitemap.xml` sin contenido | Base vacía | `200`, XML válido, solo las 7 URL estáticas | API |
| S-02 | Un `post` publicado aparece | 1 `post` `published` | Su URL de detalle presente, con `lastmod` = `published_at` | API + integración |
| S-03 | Un `draft` **no** aparece | 1 `post` `draft` | Su URL **ausente** (**E-08**) | Integración, PostgreSQL real |
| S-04 | Un `archived` **no** aparece | 1 `post` `archived` | Su URL **ausente** (**E-08**) | Integración, PostgreSQL real |
| S-05 | Los tres tipos con detalle aparecen | 1 publicado de cada | 3 URL, con su prefijo correcto | Integración |
| S-06 | Los videos **no** generan URL de detalle | 1 `video` publicado | Solo `/videos`; **no** `/videos/<slug>` | API |
| S-07 | `Content-Type` correcto | — | `application/xml` | API |
| S-08 | Sin `BLOG_PUBLIC_SITE_BASE_URL` | Variable ausente | **Fallo al arrancar**, como el resto de la configuración (**T-01**) | Configuración |
| S-09 | Las URL son del **sitio**, no del API | Variable definida | Ninguna URL contiene el origen del API | API |
| S-10 | `/admin/*`, `/buscar` y la 404 **nunca** aparecen | — | Ausentes | API |
| S-11 | Slug con caracteres que exigen escape | Slug con `&` | XML válido, entidad escapada | API |
| S-12 | **Anti-tautología**: la prueba de E-08 falla si el filtro se retira | Mutación temporal del repositorio | S-03 y S-04 **deben** pasar a rojo | Verificación de la prueba |
| M-01 | La miniatura se expone en `MedioPublico` | Medio con miniatura | Campo presente y utilizable | API |
| M-02 | `object_key` **no** se filtra | ídem | El JSON completo, sin los enlaces firmados, no contiene la clave | Integración, MinIO real |
| M-03 | Un medio sin miniatura no rompe el contrato | Medio sin miniatura | Campo nulo, sin error | API |

**S-12 no es decorativa.** Sin ella, S-03 y S-04 pasarían también si el sitemap no
enumerara nada en absoluto: una ausencia total satisface *«el borrador no aparece»* de la
peor manera posible. Es el mismo criterio con el que `Task/015` diseñó P-05-3.

**Integración obligatoria (B-6):** E-08 depende de PostgreSQL, así que S-03, S-04 y S-05
se ejecutan contra **PostgreSQL real**, nunca SQLite. M-02 contra **MinIO real**.

### 14.2 Frontend

| Área | Estrategia |
| --- | --- |
| Metadatos por página | Pruebas que rendericen la ruta y comprueben lo que llega a `document.head`, no lo que el componente devuelve |
| `canonical` y `og:url` | Prueba de que se construyen desde la configuración y **nunca** con un origen codificado |
| `og:image` | Prueba de que el valor **no** procede de un `access_url`. Es la regla vigente de D-08 convertida en guarda automática |
| JSON-LD | Prueba de que ninguna propiedad se emite con valor inventado cuando el DTO trae `null` |
| `robots.txt` y `sitemap.xml` | Guarda sobre `dist/`: `robots.txt` **existe** y **no** es HTML |
| `noindex` | Prueba de que `/admin/*` y la 404 lo emiten, y de que **ninguna** ruta pública lo emite |
| **Anti-tautología** | Falsar cada guarda nueva con una violación temporal y comprobar que **falla**, como hizo `Task/014` con las guardas de CSS |
| Accesibilidad | Arnés CDP: recorrido de teclado, foco, jerarquía, labels, `alt`, regiones vivas |
| Rendimiento | Arnés CDP para LCP/CLS y grafo de red; informe de `vite build` para los pesos |

### 14.3 Regla que no se relaja

Los tests **no** se modifican para acomodar la implementación. Si un requisito, la
arquitectura y un test se contradicen, **se detiene la tarea y se documenta**
(`BACKEND_TESTING_STRATEGY` §9). Y ningún defecto se corrige sin dejar antes su prueba de
regresión en rojo.

---

## 15. Plan de implementación

Ocho fases. Cada una termina con sus compuertas en verde antes de abrir la siguiente.

| Fase | Contenido | Repo | Depende de |
| --- | --- | --- | --- |
| **F0** | Definición: esta ficha. **Completada** | infra | — |
| **F1** | Origen público como configuración (§6.1): `VITE_SITE_BASE_URL` y `BLOG_PUBLIC_SITE_BASE_URL`, validadas, con `.env.example` | frontend, backend | F0 |
| **F2** | Metadatos por página: `title` conservado, `description`, `canonical`, Open Graph, `noindex` de `/admin/*` y de la 404. **Sin dependencias nuevas** (§18) | frontend | F1 |
| **F3** | `og:image` estático del sitio y su guarda anti-`access_url` (§8) | frontend | F2 |
| **F4** | `robots.txt` real, generado en build, y su guarda sobre `dist/` (§9.3) | frontend | F1 |
| **F5** | `GET /sitemap.xml` **test-first**: matriz, RED, GREEN, refactor, integración con PostgreSQL real (§14.1) | backend | F1 |
| **F6** | JSON-LD acotado a §10, con fail-closed ante `null` | frontend | F2 |
| **F7** | Auditoría de accesibilidad (§11) y corrección de **solo** los *gaps* demostrados | frontend | F2 |
| **F8** | Medición de rendimiento, fijación de umbrales (§12), exposición de la miniatura **test-first**, y cierre documental | frontend, backend, infra | F5, F7 |

**Orden deliberado.** F1 va primero porque canonical, `og:url` y el sitemap dependen del
origen configurable; sin él, F2, F4 y F5 codificarían un dominio que **D-07** no ha
decidido. F7 va después de F2 porque los metadatos añaden marcado que la auditoría debe
ver.

---

## 16. Riesgos y bloqueos

### 16.1 Bloqueos

| # | Bloqueo | Alcance | Propietario de la resolución | Efecto |
| --- | --- | --- | --- | --- |
| **B-016-1** | **`og:image` personalizado por contenido**: exige una URL de medio pública y estable que hoy no existe; es la pregunta abierta de **D-08** | Solo la personalización. La imagen de sitio (§8.4) **sí** se entrega | **`Task/030`** (D-08) | **Parcial.** No detiene la tarea; acota E-03 |
| **B-016-2** | **Open Graph por URL para *crawlers* sin JS**: estructuralmente imposible con *rendering* en cliente (§7.3). Y el propósito canónico de E-03 son las redes sociales, que no ejecutan JS | **E-03** por URL | **ADR nuevo** de estrategia de *rendering*. `Task/016` solo lo **abre** | **E-03 no podrá declararse cerrado.** Se entrega el nivel de sitio y se abre la reconsideración |
| **B-016-3** | **HTTP `404` real** en rutas inexistentes: un servidor estático no puede distinguirlas de un slug válido | Código HTTP de la 404 | **`Task/034`** | El `noindex` **sí** se entrega |
| **B-016-4** | **Evidencia dinámica**: sin semilla no hay contenido publicado que medir (§13.4) | A-04, A-08 con datos, metadatos de detalle en navegador, peso del *chunk* Markdown en *runtime* | **`Task/022`** | Parte de la evidencia se produce con la suite y con la base **de pruebas**; el resto se declara bloqueado |

### 16.2 Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| **R-016-1** | **La suite del frontend es sensible a la carga de la máquina**: 3 fallos por espera agotada en la primera ejecución, 0 en la segunda (§13.1) | Medio | Registrado con evidencia. No se toca ningún test en esta fase. Relevante para `Task/019` |
| **R-016-2** | Declarar **WCAG 2.1 AA** porque una herramienta marque cero | Alto: afirmación falsa | La afirmación se acota a A-01…A-08 con su evidencia; §11.1 |
| **R-016-3** | Publicar un `access_url` caducable como `og:image` o en JSON-LD | Alto: vista previa rota y contradicción con D-08 | Guarda automática (§14.2) que **falla** si el valor procede del contrato de medios |
| **R-016-4** | Fabricar propiedades de JSON-LD que el DTO no trae | Medio: datos falsos publicados | §10 mapea cada propiedad a su campo; fail-closed ante `null` |
| **R-016-5** | Codificar un dominio, invadiendo **D-07** | Medio | Origen como configuración (§6.1); prueba de que no hay origen literal |
| **R-016-6** | Absorber `Task/034` al perseguir el `404` | Medio: rompe la secuencia | Frontera escrita en §9.4 |
| **R-016-7** | Cerrar **D-08** para desbloquear `og:image` | Alto: invade `Task/030` | §8.4 declara qué **no** decide |
| **R-016-8** | Fijar umbrales «que se ven bien» sin baseline | Medio: umbral inútil | §12.4 exige baseline, herramienta, entorno y qué lo haría fallar. Sin baseline, **no hay umbral** (INP y TBT) |
| **R-016-9** | Que el sitemap crezca hasta los límites del protocolo | Bajo | Deuda declarada en §9.2 |
| **R-016-10** | Añadir una dependencia por comodidad | Medio: peso y superficie | §18: cero dependencias, con la alternativa de plataforma verificada |
| **R-016-11** | Que un metadato nuevo entre en el grafo inicial y degrade **P-05** o **P-01** | Medio | U-1 a U-4 lo detectan |

---

## 17. Deuda explícitamente diferida

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | `og:image` personalizado por contenido (**B-016-1**) | `Task/030` (D-08) |
| 2 | Estrategia de *rendering* para *crawlers* sin JS (**B-016-2**) | ADR nuevo |
| 3 | Código HTTP `404` real (**B-016-3**) | `Task/034` |
| 4 | Que sitio y sitemap compartan *host* mediante reescritura en Cloudflare Pages | `Task/034` |
| 5 | `X-Robots-Tag` como refuerzo sin JS del `noindex` del panel | `Task/018` |
| 6 | Compresión del servidor estático local (§12.5) — **CORREGIDO**: no se ejecuta en esta tarea y **no se asigna a `Task/018`**, porque ninguna fuente canónica la hace propietaria | **Sin propietario** |
| 7 | Umbral de TBT, una vez medido | `Task/016` en su fase de ejecución |
| 8 | `dateModified` en `Article`: exigiría exponer `updated_at` | Sin propietario; ninguna fuente lo pide |
| 9 | `author` en `Article` sin una petición extra (§10.1) | `Task/016` en su fase de ejecución |
| 10 | Índice de sitemaps si se superan los límites del protocolo | Sin propietario |
| 11 | Automatizar estas verificaciones en CI | `Task/019` |
| 12 | Evidencia con contenido real (**B-016-4**) | `Task/022` |

---

## 18. Dependencias nuevas

**Ninguna. Cero.** Y no por austeridad: porque se verificó que la plataforma actual basta.

### 18.1 Verificación que sostiene la conclusión

**Sondeo ejecutado el 2026-09-05** en el propio entorno de pruebas del proyecto, con
React **19.2.8**. Se renderizó un componente que emite `<title>`, `<meta name>`,
`<meta property>`, `<link rel="canonical">` y `<script type="application/ld+json">`, y se
inspeccionó dónde acabó cada etiqueta. El sondeo se **eliminó** tras medir; el árbol de
trabajo quedó limpio.

| Etiqueta emitida desde un componente | ¿Acaba en `document.head`? |
| --- | :---: |
| `<title>` | **Sí** — y `document.title` se actualiza |
| `<meta name="description">` | **Sí** |
| `<meta property="og:title">` | **Sí** |
| `<link rel="canonical">` | **Sí** |
| `<script type="application/ld+json">` | **No** — permanece en el `<body>` |

**Consecuencias:**

1. **`react-helmet` y `react-helmet-async` son innecesarios.** React 19 iza los metadatos
   de documento de forma nativa. Añadir una de esas bibliotecas sería peso y
   mantenimiento para resolver un problema que la plataforma ya resuelve — y contradiría
   **M-06**.
2. **El JSON-LD se queda en el `<body>`**, que es **válido**: `application/ld+json` no
   exige estar en `<head>`. Se documenta el hecho medido en lugar de suponerlo.

### 18.2 Dependencias evaluadas y descartadas

| Candidata | Problema que resolvería | Por qué **no** |
| --- | --- | --- |
| `react-helmet` / `react-helmet-async` | Metadatos en `<head>` | **Verificado innecesario** (§18.1). Peso y mantenimiento a cambio de nada |
| `axe-core` | Reglas de accesibilidad automáticas | El arnés CDP ya mide los 8 criterios de NFR §3, que es el alcance real. **Precedente D-13.8**: `Task/013` verificó contraste con prueba propia en lugar de una biblioteca. **Coste aceptado y declarado:** `axe` cubriría más reglas que las 8; a cambio, «axe en cero» no es WCAG AA y podría invitar a esa afirmación falsa (**R-016-2**) |
| `lighthouse` | LCP, CLS, informes | Ya se obtienen LCP y CLS por CDP con **0** dependencias, y el resultado es el mismo tipo de dato de laboratorio. Lighthouse arrastra un árbol grande para uso puntual |
| `playwright` / `puppeteer` | Automatización de navegador | **Ya resuelto sin dependencia**: `Task/013` y `Task/014` usaron Chrome *headless* por CDP, y esta fase lo ha reutilizado con `fetch` y `WebSocket` nativos de Node |
| Biblioteca de *prerender* o *framework* SSR | Problema B (§7.3) | **Prohibido aquí**: cambiar el *rendering* exige un ADR propio (`STAGE-05`) |
| Biblioteca de esquemas `schema.org` | Construir JSON-LD | Son objetos JSON literales acotados por §10. Una biblioteca invitaría a emitir propiedades sin respaldo en el DTO (**R-016-4**) |
| Generador de sitemap | XML del sitemap | La biblioteca estándar de Python genera el XML. Añadir una dependencia para concatenar `<url>` sería injustificable |

Si durante la ejecución apareciera una necesidad real, se propondrá con problema, peso,
alternativas, impacto en **P-01**/**P-05**, mantenimiento y licencia — y **no se instalará
sin aprobación**.

---

## 19. Pasos de validación

### 19.1 Comandos, no destructivos

```powershell
# --- frontend ---
cd personal-blog-frontend
npm run format:check
npm run lint
npm run typecheck
npm run test:run
$env:VITE_API_BASE_URL="http://localhost:8081"; npm run build

# --- backend ---
cd ..\personal-blog-backend
.\.venv\Scripts\Activate.ps1
ruff check .
ruff format --check .
mypy
pytest -W error -q
# Integracion: exige el Compose local levantado y la base DE PRUEBAS
$env:PERSONAL_BLOG_TEST_DATABASE_URL = "postgresql://<usuario>:<clave>@127.0.0.1:55432/personal_blog_test"
pytest -W error -q
```

### 19.2 Comprobaciones observables por el usuario

Con el Compose local levantado, sobre `http://localhost:8081`:

| # | Qué mirar | Criterio |
| --- | --- | --- |
| 1 | `curl http://localhost:8081/robots.txt` | Devuelve **texto plano**, no HTML, y contiene `Disallow: /admin/` |
| 2 | `curl http://localhost:8081/sitemap.xml` | Devuelve **XML**; ninguna URL de `/admin`, `/buscar` ni de contenido no publicado |
| 3 | Ver el código fuente de una ruta profunda **sin JavaScript** | Lleva los metadatos **de sitio**; se documenta que los **por URL** exigen JS (**B-016-2**) |
| 4 | Con JavaScript, en 3 rutas distintas | `title`, `description` y `canonical` **distintos y correctos** en cada una |
| 5 | Inspeccionar `og:image` | Es una URL del **propio sitio**, sin `X-Amz-` ni parámetros de firma |
| 6 | `/admin/acceso` | Lleva `<meta name="robots" content="noindex,follow">` |
| 7 | Recorrido con `Tab` en `/` y en `/admin/acceso` | Enlace de salto primero, foco visible en cada parada, sin trampas |
| 8 | `dist/assets` tras el build | El *chunk* administrativo existe y **no** está en el grafo inicial |

---

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** |
| **Expresión recibida** | `approved: Task/016-SEO-Accesibilidad-y-Rendimiento` |
| **Fecha de aprobación** | **2026-09-06** |

### Qué queda Vigente con la aprobación

| Decisión | Estado |
| --- | --- |
| **D-016-A** — `og:image` es un activo estático del sitio, versionado en `public/` | **Vigente** |
| **D-016-B** — el backend genera `sitemap.xml` en *runtime* | **Vigente** |
| Umbrales **U-1 a U-9** | **Vigentes**, en `non-functional-requirements.md` §2 |
| Contrato de `GET /sitemap.xml` y campo `thumbnail_access_url` | **Vigentes**, en `api-contracts.md` |
| Clasificación `infra (documentación + wiring local mínimo)` | **Vigente** |

### Qué NO queda decidido, pese a la aprobación

Esta distinción es el resultado central de la tarea y no debe difuminarse:

| Elemento | Estado tras la aprobación | Por qué |
| --- | --- | --- |
| **D-21** | **Abierta** | Lo aprobado es **haber abierto** la reconsideración con evidencia, no haber elegido una estrategia |
| [**ADR-009**](../adr/ADR-009-rendering-strategy-for-crawlers.md) | **Propuesta** | Documenta una decisión **todavía no tomada**. No hay nada que aceptar |
| **ADR-005** | **Aceptado**, sin cambios | El Markdown se sigue renderizando en cliente |
| **E-03** | **NO cerrado** | Por URL exige que el *crawler* ejecute JavaScript |
| **E-06** | **Parcial** | La garantía sin JavaScript es `X-Robots-Tag`, de `Task/018` |
| **D-08** | **Abierta** | `Task/016` respondió qué URL usa `og:image`; no la cerró |
| **A-04** | **Evidencia bloqueada** | Sin contenido no hay imágenes que auditar (`Task/022`) |
| Código HTTP `404` real | Pendiente | `Task/034` |

**Estado del avance:** con la aprobación, **16 de 41 (39 %)** y la ETAPA 05 **1 de 3 (33 %)**.

### Nota de gobierno — criterio 12

Este documento no persiste estado transitorio de Git ni de GitHub. Los SHA base son
**estado duradero** exigido por el criterio 11. El estado de ramas remotas y pull requests
se consulta en vivo, según [`WORKFLOW.md`](../project-management/WORKFLOW.md) §6.1.
