# TASK-014 — Sitio Público — Reporte

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/014-Sitio-Publico` |
| **Etapa** | ETAPA 04 — Experiencia del Usuario |
| **Estado** | **Aprobada** ✔ el 2026-09-05 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/014-Sitio-Publico` |
| **Fecha** | Definición 2026-09-04 · implementación y **aprobación** 2026-09-05 |
| **Repositorios** | `personal-blog-frontend` (funcional) · `personal-blog-infra` (documentación) |
| **Repositorio no modificado** | `personal-blog-backend` — en `main`, limpio, sin rama |
| **Ficha** | [`TASK-014-public-site.md`](../tasks/TASK-014-public-site.md) |
| **SHA base frontend** | `af242845a7d390f0ae6b6c0bdb0aece496b70e50` |
| **SHA base infra** | `fec55bb82d4832308456bc86e35755228981cf57` |

> **Aprobada el 2026-09-05.** El usuario escribió `approved: Task/014-Sitio-Publico`. Las
> secciones §1 a §14 describen el estado **previo a la aprobación** y se conservan tal cual:
> son la evidencia de que nada se publicó antes de aprobar. El estado duradero está en §15
> y §20; el trámite de cierre —commits, integración en `dev`, publicación y pull request— es
> estado **transitorio** y se consulta en Git y GitHub, no aquí
> ([WORKFLOW §6.1](../project-management/WORKFLOW.md)).

---

## 1. Qué se entregó

El **sitio público completo** del blog sobre las primitivas de `Task/013` y los diez
recursos públicos de `Task/009`/`Task/010`:

- **Doce superficies**: Inicio, Quién soy, Artículos y su detalle, Reviews y su detalle,
  Videos, Proyectos y su detalle, Contacto, Búsqueda y página 404, dentro de un layout con
  cabecera, navegación principal, buscador nativo, enlace de salto, `main` y pie.
- **Estados reales** en toda página con datos: cargando, normal, vacío, error con
  reintento; `404` del API por slug → la misma 404 pública; `404` del perfil → «aún no
  disponible» (D-014-K).
- **Estado en la URL**: `?page=`, `?tag=`, `?q=`; paginación por enlaces con
  `aria-current`; filtro por etiqueta compartible con «Quitar filtro» como navegación.
- **Media** solo por `access_url`, con `alt_text`, `width` y `height` del contrato.
- **Markdown sanitizado** con `react-markdown` + `rehype-sanitize` (ADR-005), sin HTML
  crudo ni `innerHTML`, cargado en diferido; pipeline único para la vista previa de
  `Task/015`.
- **Videos**: lista cerrada `youtube` y `vimeo`, *embed* solo al pulsar «Reproducir»,
  *fail-closed* para lo demás, enlace externo siempre.
- **Enlaces externos** con `rel="noopener noreferrer"`, misma pestaña, solo `http(s)`.
- **A-02** y **A-04** asumidas, **A-01** continuada, título de documento por página,
  favicon neutro provisional, guardas del sistema extendidas a todo CSS Module.
- **Retiro** de la pantalla provisional de fundación y de `services/health` (D-014-G).

---

## 2. Estado inicial y preflight

Verificado en vivo antes de escribir código (2026-09-05):

| Repositorio | Rama | `HEAD` | Estado |
| --- | --- | --- | --- |
| frontend | `Task/014-Sitio-Publico` | `af24284` = `main` | árbol limpio, sin commits propios |
| infra | `Task/014-Sitio-Publico` | `fec55bb` = `main` | cambios documentales de la definición **preservados**, sin commit |
| backend | `main` | `ce166fb` | limpio, sin rama |

**Línea base real**: `npm run test:run` → **161 / 161** en 15 archivos, **antes** del primer
RED. Ninguna prueba heredada fallaba.

---

## 3. RED → GREEN por *slice*

| Slice | Test RED | Motivo esperado (observado) | GREEN | Refactor |
| --- | --- | --- | --- | --- |
| 1. `services/public` + tipos | 8 archivos de prueba | `Failed to resolve import "./posts"` (y 7 más) | 8 archivos, **33** pruebas | `pedirListado` / `pedirDetalle` compartidos desde el inicio; sin refactor posterior |
| 2. `useAsyncResource`, `useDocumentTitle`, `HttpClientContext` | 3 archivos | import no resuelto (`./useAsyncResource`, `../lib/site`, `./httpClientContext`) | 3 archivos, **13** pruebas | Fase `cargando` **derivada** de la clave del resultado, para eliminar el `setState` síncrono en el efecto que lint señaló (sin cambio observable; la suite siguió en verde) |
| 3. Rutas, `SiteLayout`, 404 real, esqueletos | `routes.test`, `SiteLayout.test`, `NotFoundPage.test` | **19 fallos**: `Unable to find role="heading"` por página, `navigation` principal ausente, detalles cayendo en el comodín | 3 archivos, **19** pruebas | Una prueba heredada de `App.test` ajustada con justificación (§10) |
| 4. `Pagination`, `ExternalLink`, `LoadingState`, `EmptyState`, `ErrorState` | 5 archivos | import no resuelto ×5 | 5 archivos, **20** pruebas | Ventana de páginas y clasificación de esquemas movidas a módulos puros (`paginas.ts`, `lib/enlaces.ts`) por la regla de *fast refresh* |
| 5. Entidades, proveedores, formato | 13 archivos | import no resuelto ×13 | 13 archivos, **68** pruebas | `describirLibro` a `libro.ts`; dos aserciones de prueba corregidas (`li` externo, `fireEvent`) |
| 6. Listados y `useParametrosDeListado` | 5 archivos | **16 fallos** (páginas esqueleto sin lista, vacío ni error) + import del hook | 5 archivos, **36** pruebas (con rutas) | — |
| 7. `MarkdownRenderer` / `MarkdownContent` | 2 archivos | import no resuelto ×2 (dependencias ya instaladas) | **13** + 1 pruebas; el envoltorio diferido necesitó ampliar la espera del entorno | Esquema a `esquema.ts`; `node` descartado explícitamente |
| 8. Detalles y Quién soy | 4 archivos | **11 fallos**: sin `article`, sin 404 por slug, sin reintento | 4 archivos, **11** pruebas | `useDocumentTitle(undefined)` para delegar el título a la 404 montada |
| 9. Contacto y Búsqueda | 2 archivos | **9 fallos** (2 pasaban trivialmente por el esqueleto) | 2 archivos, **11** pruebas | — |
| 10. Inicio real + retiro de `health` | `HomePage.test` reescrita, `App.test` ajustada | **9 fallos**: `main` duplicado, 0 peticiones, sin regiones de destacados | **7** + 4 pruebas; `git grep` demostró que el único consumidor de `services/health` era la pantalla provisional | Prueba de `App` esperando el estado final del `h1` |
| 11. Favicon | `favicon.test.ts` | escrito junto con el asset (sin RED separado) | **3** pruebas | — |
| 12. Guardas extendidas | `designSystem.guards.test.ts` (ampliado) | escrito junto con la extensión; **falsado** después: 3 violaciones inyectadas → **3 fallos**, restaurado | **95** pruebas de guardas en total | — |
| 13. Cobertura final | `libro.test.ts`, caso protocolo-relativo en Markdown | — | **440 / 440** | — |

Cada RED se **ejecutó** y su salida se observó antes de implementar; los dos *slices* sin
RED separado (11 y 12) están declarados como tales.

---

## 4. Rutas

Las doce superficies, verificadas por prueba (`routes.test.tsx`) y en Chrome contra el build
del Compose (`http://localhost:8081`):

| Ruta | Página | Resultado en el entorno real (sin semilla) |
| --- | --- | --- |
| `/` | Inicio | `h1` = nombre del sitio (perfil `404`), cuatro secciones con «Todavía no hay … destacados» |
| `/quien-soy` | Quién soy | «El perfil aún no está disponible» |
| `/articulos` | Artículos | «Todavía no hay artículos publicados» |
| `/articulos/:slug` | Detalle | `404` del API → página 404 pública |
| `/reviews` · `/reviews/:slug` | Reviews | ídem |
| `/videos` | Videos | «Todavía no hay videos publicados»; **no existe** `/videos/:slug` (→ 404) |
| `/proyectos` · `/proyectos/:slug` | Proyectos | ídem |
| `/contacto` | Contacto | «Los datos de contacto aún no están disponibles» |
| `/buscar?q=` | Búsqueda | `q` corto: aviso sin llamada; `q=docker`: «Sin resultados» con secciones |
| `*` | 404 | dentro del layout, con enlaces a Inicio y seis secciones |
| `/__design-system` | — | registrada solo en `DEV`; en el build responde la **404** |

El comodín `*` sigue siendo la última ruta de la tabla.

---

## 5. API consumida

| Endpoint | Parámetros realmente enviados | Dónde |
| --- | --- | --- |
| `GET /api/v1/profile` | ninguno | Inicio, Quién soy, Contacto |
| `GET /api/v1/posts` | `page`, `tag` (solo si existen); `featured=true&page_size=3` en Inicio | Artículos, Inicio |
| `GET /api/v1/posts/{slug}` | ninguno (slug codificado en la ruta) | Detalle |
| `GET /api/v1/book-reviews` · `/{slug}` | ídem | Reviews |
| `GET /api/v1/videos` | ídem listado | Videos, Inicio |
| `GET /api/v1/projects` · `/{slug}` | ídem | Proyectos |
| `GET /api/v1/tags` | `page_size=50` | Filtro de los cuatro listados |
| `GET /api/v1/search` | `q` (recortado, ≥ 2), `page` | Búsqueda |

Fijado por prueba: ningún parámetro fuera de esa lista sale hacia el API (`utm_source` en la
URL no se reenvía); `page` inválido se ignora; nada consulta `/health`, `/ready` ni
`/api/v1/admin/*`. La envoltura se comprueba de forma ligera (D-014-N): sin `items`
arreglo → `HttpError('invalid_response')`.

---

## 6. Markdown

- **Dependencias instaladas** (autorizadas el 2026-09-05): `react-markdown@10.1.0`,
  `rehype-sanitize@6.0.0`. No: `remark-gfm`, `rehype-raw`, `marked`, `dompurify`,
  `markdown-it`.
- **Pipeline**: Markdown → `react-markdown` (`skipHtml`) → árbol React → `rehype-sanitize`
  con esquema explícito (`esquema.ts`: `defaultSchema` restringido a `href` `http`/`https`/
  `mailto` y `src` `http`/`https`, `clobberPrefix` para los `id`) → componentes propios para
  `a`, `img` y `h1`–`h6`. Nunca `dangerouslySetInnerHTML`.
- **Casos maliciosos probados** (`MarkdownRenderer.test.tsx`, 14 pruebas): `<script>` no
  se interpreta ni deja su texto; `<iframe>`, `onclick`, `onerror` no llegan al DOM;
  `javascript:`, `data:` y `vbscript:` en enlaces no producen `<a>`; `data:image/svg+xml`
  en imagen no produce `<img>`; `style` y `class` del contenido no se aplican.
- **Enlaces**: `/ruta` interna → `Link` del router sin `rel`; `#ancla` y `mailto:` →
  `<a>`; `http(s)://` → `ExternalLink` con `rel="noopener noreferrer"` y sin `target`;
  `//host` y protocolos no permitidos → solo texto.
- **Encabezados** bajan un nivel (`#` → `h2`): el `h1` es el título de la página.
- **Carga diferida**: `MarkdownContent` usa `React.lazy`; el build emite
  `MarkdownRenderer-*.js` (121,6 kB / 37,1 kB gzip) aparte del bundle principal.

---

## 7. Videos

- **Proveedores**: `youtube` (`https://www.youtube-nocookie.com/embed/{id}`,
  `^[A-Za-z0-9_-]{11}$`) y `vimeo` (`https://player.vimeo.com/video/{id}`,
  `^[0-9]{6,12}$`). Comparación sin mayúsculas ni espacios.
- **Fail-closed**: proveedor fuera de la lista o `embed_reference` malformada → sin botón
  y sin `iframe`; solo el enlace externo. 12 casos negativos en `providers.test.ts`.
- **Embed por acción explícita**: la tarjeta muestra la miniatura y «Reproducir»; el
  `iframe` (`title`, `allowfullscreen`, `loading="lazy"`,
  `referrerpolicy="strict-origin-when-cross-origin"`) aparece al pulsar.
- **Enlace externo siempre**: «Ver en YouTube» / «Ver en Vimeo» / «Ver el video», con
  `rel="noopener noreferrer"`.
- Cada `VideoCard` lleva `id={slug}`; la búsqueda enlaza a `/videos#<slug>`.
- Cierre documental en `api-contracts.md` §14.9, `data-model.md` §10 y
  `security-boundaries.md` §5/§7; **Vigente** desde la aprobación del 2026-09-05.

---

## 8. Accesibilidad

| Criterio | Estado final |
| --- | --- |
| **A-01** teclado | Continuado: solo `<a>`, `<button>`, `<input>` nativos; enlace de salto primero; orden natural. Verificado en Chrome: 10 Tabs recorren salto → marca → 7 enlaces → buscador, con anillo `2px solid #0a5ad6` en todos |
| **A-02** HTML semántico | **Asumido**: `header`, `nav[aria-label]`, `main#contenido`, `footer`, `article`, `section[aria-labelledby]`, `ul > li > article`, `time[datetime]`; **un** `h1` por página (56 combinaciones verificadas); Markdown desde `h2` |
| **A-04** texto alternativo | **Asumido en el render**: `alt` del contrato en cada `<img>`; `alt_text` nulo → decorativa (`alt=""`), nunca texto inventado; medio sin `access_url` → sin imagen |
| **A-05 / A-06 / A-07** | **Preservados**: guardas extendidas a todo `*.module.css` (0 colores literales, 0 `outline` suprimido, 0 `:focus-visible` propio, 0 media queries de ancho); `Badge` con texto para estados; paginación actual con relleno y peso además del color |
| Título de documento | Por página (`useDocumentTitle`): «Artículos · Blog personal», título del contenido en detalles, «Página no encontrada · Blog personal» en la 404 |
| **S-12** | `ExternalLink` en redes, repositorio, demo, ficha del libro, enlace del video y enlaces del Markdown |
| **S-03** | Render público sanitizado (§6) |

No se afirma cumplimiento WCAG AA del producto: la auditoría es `Task/016`. A-03 y A-08
siguen siendo de `Task/015`.

---

## 9. Responsive

Chrome headless (CDP, `Emulation.setDeviceMetricsOverride`) contra el build servido por el
Compose, **14 superficies × 4 anchos = 56 mediciones**:

| Ancho | `scrollWidth == clientWidth` | Elementos que sobresalen | Notas |
| --- | :---: | :---: | --- |
| 320 px | ✔ 14 / 14 | 0 | Navegación y buscador envuelven en varias líneas |
| 390 px | ✔ 14 / 14 | 0 | |
| 768 px | ✔ 14 / 14 | 0 | En `/`, 753/753 (barra de desplazamiento vertical presente) |
| 1280 px | ✔ 14 / 14 | 0 | En `/`, 1265/1265 (ídem) |

Sin media queries de ancho en todo el árbol: `clamp()`, `min()`, `flex-wrap`, rejillas
`auto-fit`/`minmax(min(18rem, 100%), 1fr)` y `aspect-ratio`. **Limitación:** sin contenido
publicado, las rejillas de tarjetas, las imágenes y los *embeds* no se observaron en el
navegador real; su estructura está fijada por prueba.

---

## 10. Validaciones

| Compuerta | Resultado |
| --- | --- |
| `npm run format:check` | ✔ limpio |
| `npm run lint` | ✔ 0 errores, 0 avisos |
| `npm run typecheck` | ✔ sin errores |
| `npm run test:run` | ✔ **440 / 440**, 61 archivos. **Estabilidad verificada** tras corregir la inestabilidad descrita abajo |
| `npm run test:coverage` | ✔ 99,78 % sentencias · 96,61 % ramas · 100 % funciones · 99,78 % líneas |
| `npm run build` (con `VITE_API_BASE_URL`) | ✔ sin *warnings*; 2 *chunks* JS, 2 CSS, `favicon.svg` |
| Consola (Chrome, 56 cargas) | ✔ 0 excepciones, 0 `console.error`; solo anotaciones de red por `404` esperados |
| Guardas CSS | ✔ 95 pruebas; extensión falsada con 3 violaciones detectadas |
| Criterion 12 | ✔ **C = 0** (§13) |
| Enlaces documentales | ✔ comprobados en ficha, reporte y documentos tocados |
| Secretos | ✔ ninguno en `src/`, `public/`, `index.html` |
| `git diff --check` (frontend e infra) | ✔ sin hallazgos |

### Una suite inestable, encontrada y corregida durante el cierre

Al ejecutar las validaciones del cierre aprobado, **una corrida completa terminó en
`439 / 440`** mientras otras seis pasaban. La corrida roja duró **63 s** frente a los ~33 s
de las verdes, y las pruebas implicadas nunca fallaban ejecutadas por separado.

**Causa.** Cinco pruebas esperaban con un **límite de reloj** (`timeout: 15_000`) la primera
importación diferida de `MarkdownRenderer`. Esa importación transforma en ese instante toda
la cadena de `react-markdown` —micromark, mdast, hast—, y en una máquina cargada no cabía en
el límite. El resultado dependía de la ocupación del equipo, no del código: exactamente lo
que `CONTRIBUTING.md` §5 prohíbe cuando exige que ninguna prueba dependa del entorno.

**Corrección, de raíz y no subiendo el límite.** `src/test/precargarMarkdown.ts` importa el
renderizador de forma **estática**, así que cuando `React.lazy` lo pide lo recibe del
registro de módulos en lugar de transformarlo. Los **cinco `timeout` ampliados
desaparecen**: ya no hay ninguna carrera contra el reloj que ganar. El renderizador que se
ejercita sigue siendo el **real**, con su sanitización — no se sustituyó por un doble.

**La carga diferida de producción no se toca.** Es una propiedad del *build* y se comprueba
donde corresponde: `dist/` sigue emitiendo `MarkdownRenderer-*.js` (121,6 kB / 37,1 kB gzip)
como *chunk* aparte, verificado después del cambio.

**Evidencia:** cinco corridas completas seguidas en verde, más una corrida **bajo carga
concurrente** —suite, `typecheck` y `build` a la vez, 55 s, más lenta que la corrida que
había fallado— también en verde.

### Pruebas heredadas modificadas, con justificación

| Archivo | Cambio | Por qué |
| --- | --- | --- |
| `src/app/App.test.tsx` | El doble de `/health` pasa a responder los recursos públicos; «expone la configuración» se comprueba por la URL de las peticiones; «404 ofrece volver al inicio» nombra el enlace propio de la 404; la portada se espera en su estado final | La pantalla provisional que imprimía el origen y consultaba `/health` **es lo que esta tarea sustituye**; la 404 ahora vive dentro del layout, que ya tiene un enlace «Inicio» |
| `src/pages/HomePage.test.tsx` | Reescrita | Prueba de la portada real; la provisional desaparece por diseño (ficha §3, D-014-G) |
| `src/styles/designSystem.guards.test.ts` | **Ampliada** (bloque nuevo) | Las pruebas anteriores no se tocaron; se añaden las mismas reglas sobre todo el árbol |
| `src/services/health/healthService.test.ts` | Eliminada con su módulo | Sin consumidor productivo (`git grep`) |

Ninguna expectativa se relajó para acomodar una implementación.

---

## 11. Regresión

- **440 pruebas** en 61 archivos: las 161 heredadas siguen en verde (con las cuatro
  modificaciones justificadas arriba) más 279 nuevas.
- `/__design-system`: registrada en desarrollo (prueba heredada intacta), ausente de `dist/`
  (`grep` sin resultados) y **404 en el build** servido por el Compose.
- Archivos protegidos sin cambios: `git diff --stat main -- src/services/http vite.config.ts
  tsconfig.json tsconfig.app.json tsconfig.node.json eslint.config.js` → vacío.
- `package.json`: solo `react-markdown` y `rehype-sanitize`.
- Primitivas de `Task/013`, `tokens.css` y `foundation.css`: sin cambios.

---

## 12. Entorno local

| Acción | Motivo | Naturaleza |
| --- | --- | --- |
| `docker exec personal-blog-local-backend alembic upgrade head` | La base estaba en `0001`; el API respondía `500` en todo | **Aditiva y documentada** (runbook §6, reporte de `Task/008`). `alembic current` → `0003 (head)` |
| `docker compose build frontend` + `docker compose up -d frontend` | Validar el build real tras Traefik (mismo origen) | Autorizada expresamente |

No se ejecutó `down`, `prune` ni nada que toque volúmenes. **No se creó administrador ni
contenido**: no existe mecanismo documentado y hacerlo exigiría inventar credenciales o
modificar el backend. Por eso la validación en el entorno real cubre los estados vacíos, el
`404` del perfil y la 404 pública; los estados con datos los cubre la suite.

---

## 13. Criterion 12 — estado duradero frente a transitorio

Barrido sobre ficha, reporte, `STATUS`, `ROADMAP`, `STAGE-04`, `api-contracts`,
`data-model`, `security-boundaries`, runbook y README del frontend:

| Clase | Ejemplos |
| --- | --- |
| **A — historia fechada** | «autorizada por el usuario el 2026-09-05»; «`alembic current` → `0003 (head)` el 2026-09-05»; instantánea de §14 |
| **B — regla permanente** | «toda rama Task nace de `main`»; «la tarea solo se aprueba con `approved:`»; «la 404 no puede fijar el código HTTP desde una SPA» |
| **C — estado vivo de Git o GitHub** | **0** |

**C = 0.** Ningún documento afirma que exista un PR, una rama remota, una normalización
pendiente ni una espera al *merge*.

---

## 14. Estado de Git previo a la aprobación

**Observación fechada, no estado vigente.** Los contadores son transitorios por definición;
el estado vivo se consulta en Git y GitHub ([WORKFLOW §6.1](../project-management/WORKFLOW.md)).

> *Observado el 2026-09-05, **antes** de la aprobación:*

| Repositorio | Rama | `main..HEAD` | *Staging* | Cambios sin commit | Push | PR |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| frontend | `Task/014-Sitio-Publico` (base `af24284`) | **0** | **0** | 117 creados, 12 modificados, 3 eliminados | **0** | **0** |
| infra | `Task/014-Sitio-Publico` (base `fec55bb`) | **0** | **0** | 8 modificados, 2 creados | **0** | **0** |
| backend | `main` (`ce166fb`) | — | **0** | **ninguno** | **0** | **0** |

En esa instantánea los cambios se encontraban sin commit, como corresponde a una tarea
todavía no aprobada ([`PROJECT_INSTRUCTIONS`](../claude/PROJECT_INSTRUCTIONS.md) §6).

---

## 15. Gobierno

| Campo | Valor |
| --- | --- |
| **`Task/014`** | **Aprobada** ✔ (2026-09-05) |
| **Avance global** | **14 de 41 — 34 %** |
| **ETAPA 04** | **En curso** — **2 de 3** — **67 %** |
| **Decisiones** | D-014-A a D-014-N: **Vigentes** desde el 2026-09-05 |
| **Documentos actualizados** | ficha, este reporte, `STATUS`, `ROADMAP`, `STAGE-04`, `api-contracts` §14.9, `data-model` (responsabilidades y deuda 6), `security-boundaries` §5 y §7, runbook §11, README del frontend |

Hallazgos independientes registrados en `STATUS.md` y **no corregidos aquí**: índice de
reportes sin `Task/010`–`Task/013`; tabla «Resumen de etapas» del ROADMAP detenida en
`Task/009`; valor esperado de `alembic current` en el runbook detenido en `0001`.

---

## 16. Deuda y limitaciones

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | Restringir `provider` en el backend a `youtube`/`vimeo` y ofrecer el selector en el panel | Backend: sin propietario (candidata `Task/018`) · panel: `Task/015` |
| 2 | Miniatura derivada del proveedor cuando el video no trae `thumbnail` | Sin propietario; implica petición a un tercero |
| 3 | `noindex` y código HTTP para la 404 de la SPA | `Task/016`, `Task/034` |
| 4 | `description`, Open Graph, canonical por página | `Task/016` |
| 5 | Medir el peso del renderizador Markdown y el *lazy loading* de imágenes | `Task/016` |
| 6 | Auditoría de la configuración de sanitización | `Task/018` |
| 7 | Proxy de desarrollo de Vite si reconstruir la imagen resulta lento | Decisión del usuario |
| 8 | `useAppConfig` sin consumidor productivo | `Task/015` |
| 9 | Validación visual **con contenido** en el navegador real | `Task/022` (semilla) |
| 10 | Anotaciones de red por `404` esperados en la consola de Chrome | Ninguna: contrato de no filtración |

---

## 17. Pasos de validación para el usuario

Están en la ficha [`TASK-014`](../tasks/TASK-014-public-site.md), sección 17:
compuertas, diffs de archivos protegidos, comprobaciones sobre `dist/` y el recorrido manual
en `http://localhost:8081` (teclado, doce rutas, anchos, búsqueda corta, 404 de
`/__design-system` en producción).

---

## 18. Próxima tarea

`Task/015-Panel-Administrativo`. **No se inicia** hasta que `Task/014` esté aprobada y
`main` y `dev` normalizadas; su rama nacerá de `main` actualizado y limpio.

---

## 19. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-05** |
| **Aprobado por** | **jeffersondavila** (el usuario) |
| **Expresión de aprobación** | `approved: Task/014-Sitio-Publico` |

Recibida la aprobación se ejecutó el cierre de
[`WORKFLOW.md`](../project-management/WORKFLOW.md) §3 en `personal-blog-frontend` y
`personal-blog-infra`: **D-014-A** a **D-014-N** promovidas a **Vigentes**, gobierno
actualizado, commits creados, rama integrada en `dev` mediante merge `--no-ff` y pull
request `Task/014-Sitio-Publico → main`.

**La revisión y la fusión del pull request son responsabilidad exclusiva del usuario.**

---

## 20. Límites respetados

| Límite | Cumplido |
| --- | :---: |
| Sin commit, push, merge ni PR **antes de la aprobación** | ✔ |
| Sin autoaprobación: la tarea se aprobó con la expresión literal del usuario | ✔ |
| Sin `gh pr merge`: la fusión hacia `main` la decide el usuario | ✔ |
| Backend intacto (`main`, limpio, sin rama) | ✔ |
| Sin recursos cloud | ✔ |
| Sin secretos versionados | ✔ |
| Sin `docker compose down`, `prune`, WSL ni WinNAT | ✔ |
| Sin proxy de Vite ni CORS en el backend | ✔ |
| Solo las dos dependencias autorizadas | ✔ |
| Drifts independientes **no** corregidos aquí | ✔ |
| Sin iniciar `Task/015` | ✔ |
