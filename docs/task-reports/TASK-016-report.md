# TASK-016 — Reporte de implementación

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/016-SEO-Accesibilidad-y-Rendimiento` |
| **Etapa** | ETAPA 05 — Calidad y Seguridad |
| **Estado** | **Aprobada** — 2026-09-06 |
| **Repositorios** | `personal-blog-frontend`, `personal-blog-backend`, `personal-blog-infra` (documentación + ***wiring* local mínimo**) |
| **Ficha** | [`TASK-016-seo-accessibility-performance.md`](../tasks/TASK-016-seo-accessibility-performance.md) |
| **SHA base — frontend** | `1c5e2f329bcbc68afc73ef3b0b3b5b0e399c35ab` |
| **SHA base — backend** | `d278d849b4a4d506b838213a9572d97d9eed80da` |
| **SHA base — infra** | `6c57f7bd8b3480443d51605b5bcce23c14494425` |
| **Fecha** | 2026-09-06 |
| **Dependencias nuevas** | **0** |

> **Aprobada el 2026-09-06** mediante `approved: Task/016-SEO-Accesibilidad-y-Rendimiento`.
> **D-016-A**, **D-016-B** y los umbrales **U-1 a U-9** quedan **Vigentes**.
>
> **La aprobación no decide la estrategia de *rendering*.** **D-21** sigue **Abierta** y
> **ADR-009** sigue en **Propuesta**: lo aprobado es haber **abierto** la reconsideración
> con evidencia. **E-03 sigue NO cerrado**, **E-06 parcial** y **D-08 abierta**: los
> motivos están medidos, no supuestos, en §3 y §5.

---

## 1. Qué se entregó

| Requisito | Entregado | Estado |
| --- | --- | --- |
| **E-02** | `title` y `description` propios por URL en las 11 superficies públicas | **Cumplido con JavaScript**; parcial sin él |
| **E-03** | Open Graph completo por URL; `og:image` estático y estable | **NO cerrado** — §3 |
| **E-04** | `canonical` absoluto en toda página indexable | **Cumplido con JavaScript**; parcial sin él |
| **E-05** | `GET /sitemap.xml` generado por el backend desde contenido publicado | **Cumplido en ambos canales** |
| **E-06** | `robots.txt` real, `noindex` en `/admin/*`, en la 404 y en `/buscar` | **Parcial** — §5 |
| **E-07** | JSON-LD `WebSite`, `Person`, `Article`, `Review` y `BreadcrumbList` | **Cumplido con JavaScript** |
| **E-08** | El contenido no publicado nunca aparece en el sitemap | **Cumplido, por construcción** |
| **E-01** | Slugs legibles y estables | **Regresión verificada**: sin cambios |
| **A-01…A-08** | Auditoría formal en navegador real | **§6** |
| **P-01, P-03, P-04, P-05** | Umbrales fijados y medidos | **§7** |

---

## 2. Configuración de origen (F1)

Dos variables nuevas, ambas **obligatorias y validadas al arrancar** (**T-01**),
y ninguna fija un dominio: **D-07 sigue abierta**.

| Variable | Repositorio | Qué es | Fail-closed |
| --- | --- | --- | --- |
| `VITE_SITE_BASE_URL` | frontend | Origen público del **sitio** | La aplicación **no monta** |
| `BLOG_PUBLIC_SITE_BASE_URL` | backend | El mismo, para las URL del sitemap | El proceso **no arranca** |

**Por qué son dos y no una:** con **D-15** el sitio vive en el dominio raíz y el
API en un subdominio. El backend no puede deducir el origen del sitio de la
petición —`Host` lo escribe el cliente y, tras un proxy o API Gateway, nombra el
API—, y el frontend no puede deducirlo de `location`, porque el mismo `dist/` se
sirve en orígenes distintos.

**RED demostrado antes de implementar:**

| Compuerta | Evidencia RED |
| --- | --- |
| frontend | `10 failed \| 7 passed` — `readAppConfig` no devolvía `siteBaseUrl` |
| backend | `7 failed` — `public_site_base_url: Extra inputs are not permitted` |

**GREEN:** `17 / 17` y `13 / 13` respectivamente.

> **Observación honesta sobre el RED del backend.** De los 13 casos, 6 «pasaban»
> antes de implementar, pero **vacuamente**: `extra="forbid"` ya rechazaba el
> campo desconocido, así que no probaban la validación del valor. Solo tras el
> GREEN empezaron a probar lo que dicen probar. Se registra porque un RED parcial
> mal leído es exactamente como se cuela una prueba tautológica.

---

## 3. E-03 y la limitación estructural — el resultado central

### 3.1 Medición en cuatro canales, **después** de implementar

| Canal | `title` | `description` | `canonical` | `og:*` por URL | JSON-LD |
| --- | :---: | :---: | :---: | :---: | :---: |
| Navegador con JavaScript (11 rutas) | ✔ propio | ✔ propio | ✔ | ✔ | ✔ |
| Petición HTTP directa | ✘ genérico | ✘ | ✘ | ✘ | ✘ |
| *Crawler* sin JavaScript | ✘ genérico | ✘ | ✘ | ✘ | ✘ |
| `Googlebot` / `facebookexternalhit` / `Twitterbot` | ✘ genérico | ✘ | ✘ | ✘ | ✘ |

**Esto es lo que la tarea tenía que averiguar.** Antes de implementar, el canal
sin JavaScript recibía cero metadatos; **después de implementarlos y verificarlos
en navegador real, sigue recibiendo cero metadatos propios de la URL**. El
problema no era falta de código.

Y afecta a **E-03** en particular porque su propósito canónico —`MVP_SCOPE.md`
§2.2, *«compartir páginas mediante metadatos Open Graph»*— tiene como
consumidores exactamente a los agentes que no ejecutan JavaScript.

### 3.2 Lo que sí se ganó en el canal sin JavaScript

`index.html` declara ahora el Open Graph **de sitio**, verificado en el artefacto
servido:

```
<meta property="og:site_name" content="Blog personal" />
<meta property="og:image" content="http://localhost:8081/og-imagen.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="Marca de Blog personal" />
<meta name="twitter:card" content="summary_large_image" />
```

**Corrección de la ficha, con su motivo.** La ficha §7.4 anticipaba poner también
`description` y `og:title` de sitio en `index.html`. **Se midió y se descartó:**
React 19 iza los metadatos al `head` pero **no deduplica**. Un sondeo —ejecutado
y después eliminado— comprobó que una etiqueta estática y otra dinámica con el
mismo `name`/`property` **coexisten**:

```
description: ["ESTATICA del sitio", "DINAMICA de la pagina"]
og:title:    ["ESTATICO del sitio", "DINAMICO de la pagina"]
```

Declarar en `index.html` algo que `Seo` también emite produciría **duplicados
contradictorios en toda página**. El reparto quedó por tanto exacto: en
`index.html` solo lo que vale para **todo** el sitio; en `Seo`, solo lo que
**cambia** por página. Hay una guarda automática que lo fija en ambos sentidos
(SEO-7).

### 3.3 Consecuencia de gobierno

Se abre **D-21** con [**ADR-009**](../adr/ADR-009-rendering-strategy-for-crawlers.md),
en estado **Propuesta**. **No se elige** SSR, SSG, prerender ni ningún otro
mecanismo, y **ADR-005 sigue Aceptado**. Es exactamente lo que `STAGE-05` manda
hacer y donde manda detenerse.

---

## 4. Sitemap (F5) — test-first

### 4.1 Contrato entregado

`GET /sitemap.xml`, fuera del prefijo `/api/v1` con el mismo criterio que
`/health`. `Content-Type: application/xml`. Contiene las 7 rutas estáticas más
una entrada por contenido `published` de artículos, reviews y proyectos.
`lastmod` ← `published_at`, normalizado a UTC. **No** incluye `/buscar`,
`/admin/*`, la 404 ni `/videos/{slug}` — que no existe.

### 4.2 RED y GREEN

| Fase | Evidencia |
| --- | --- |
| **RED unidad** | `ModuleNotFoundError: No module named 'app.modules.sitemap'` |
| **RED integración** | `8 failed` — `assert 404 == 200`, `content-type` `application/json`, y `ParseError: not well-formed` al intentar leer como XML el envelope de error |
| **GREEN** | `36 passed` (12 unidad + 24 integración) |

### 4.3 Anti-tautología de E-08, ejecutada

Se **mutó temporalmente** el filtro de estado de la consulta para que los
borradores entraran:

```python
-    ).where(modelo.status == estado_publicado)
+    )  # MUTACION: filtro de estado retirado
```

| Resultado | Detalle |
| --- | --- |
| Con la mutación | **3 failed** — exactamente las tres pruebas de **E-08**: `[draft-borrador]`, `[archived-archivado]` y `test_e08_en_los_tres_tipos_con_detalle_a_la_vez` |
| Reversión | `diff` contra la copia original: **idéntico**, `0` rastros de la mutación |
| Tras revertir | **36 passed** |

Esto demuestra que las pruebas de E-08 **observan el filtro** y no un vacío. La
prueba `test_anti_tautologia_el_sitemap_si_enumera_contenido` cierra el otro
flanco: comprueba que el documento **crece exactamente en 3** al publicar tres
contenidos, de modo que «el borrador no aparece» no pueda satisfacerse con un
sitemap que no enumera nada.

### 4.4 Enrutado local

El endpoint funcionaba pero **Traefik no lo enrutaba**: su regla listaba
`/health`, `/api/`, `/docs` y `/openapi.json`, así que `/sitemap.xml` caía en el
frontend y devolvía el `index.html` de la SPA. Se añadió `|| Path(`/sitemap.xml`)`
a la regla del router `backend`, **con autorización expresa del usuario**.

**En producción esta regla no hace falta:** el `Sitemap:` de `robots.txt` apunta
al dominio del API, servido por API Gateway sin Traefik de por medio.

Verificado tras el cambio: `HTTP 200`, `application/xml`, 7 URL, y el sitio y el
API siguen respondiendo con normalidad.

---

## 5. `robots.txt` y E-06 — por qué queda **parcial**

### 5.1 Dos defectos medidos y corregidos

Antes de esta tarea, `GET /robots.txt` y `GET /sitemap.xml` devolvían **HTTP 200
con el `index.html` de la SPA**, por el *fallback* `try_files` del servidor
estático. Un `200` con contenido no analizable es **peor que un `404`**.

| Recurso | Antes | Después |
| --- | --- | --- |
| `/robots.txt` | `200 text/html` (SPA) | **`200 text/plain`** |
| `/sitemap.xml` | `200 text/html` (SPA) | **`200 application/xml`** |
| `/og-imagen.png` | no existía | **`200 image/png`, 20 593 bytes** |

`robots.txt` se **genera en el build** con un plugin de Vite, porque su línea
`Sitemap:` necesita una URL absoluta y el origen es configuración. Se compone con
`VITE_API_BASE_URL` —el sitemap lo sirve el backend— y **no se añadió una tercera
variable**: la existente ya representa ese origen. Si no hubiera origen válido,
la línea **se omite** en lugar de emitir una URL falsa.

### 5.2 Por qué E-06 no puede declararse cerrada

`Disallow` controla el **rastreo**, no la **indexación**: una URL enlazada desde
fuera puede acabar indexada sin haber sido rastreada. Y el `<meta name="robots">`
existe **después** de hidratar, así que un *crawler* sin JavaScript no lo ve.

> **E-06 queda PARCIAL en `Task/016`:** `robots.txt` correcto más `meta noindex`
> en el render de cliente. La garantía **HTTP / sin JavaScript** exige
> `X-Robots-Tag`, que es una **cabecera de respuesta** y por tanto propiedad de
> **`Task/018`** (requisito **S-05**). No se mueve el propietario canónico del
> requisito: se registra la dependencia real.

Y `robots.txt` **no protege nada**: el control de acceso al panel sigue siendo la
sesión de `Task/011` y las guardas de `Task/015`.

---

## 6. Accesibilidad (F7) — auditoría en navegador real

Chrome 152 *headless* por CDP, **10 superficies**, sin añadir ninguna dependencia.

### 6.1 Resultado

| Medida | Resultado |
| --- | --- |
| Paradas de teclado recorridas con `Tab` | **139** |
| Paradas **sin** indicador de foco visible | **0** |
| Problemas estáticos detectados | **0** |
| Rutas sin trampa de foco (el recorrido vuelve a `body`) | **10 / 10** |
| Primera parada en todas | **«Saltar al contenido»** |
| `Shift+Tab` invierte el orden | ✔ en las 10 |

Los «problemas estáticos» comprobados por ruta son: saltos de nivel de
encabezado, número de `h1`, `img` sin `alt`, controles sin nombre accesible y
enlaces externos sin `noopener`. **Cero** en las 10.

### 6.2 Matriz A-01…A-08

| # | Estado | Evidencia |
| --- | --- | --- |
| **A-01** Teclado | **Cerrado** en lo medible | 139 paradas, 0 sin foco, 0 trampas, enlace de salto primero |
| **A-02** Semántica | **Cumple** | 1 `h1` por página, 0 saltos de nivel, `main`/`nav`/`header`/`footer` presentes |
| **A-03** Labels | **Cumple** | 0 controles sin nombre accesible en las 10 superficies |
| **A-04** Texto alternativo | **BLOQUEADO** | 0 imágenes renderizadas: la base está vacía (`Task/022`). **No se fabricó contenido** |
| **A-05** Contraste | **Heredado de `Task/013`** | 22 pares verificados allí; no se detectó ningún par nuevo que falle |
| **A-06** Foco visible | **Cumple** | 0 de 139 paradas sin indicador; anillo `2px solid rgb(10,90,214)` |
| **A-07** Sin depender del color | **Heredado de `Task/013`** | Sin hallazgos nuevos |
| **A-08** Errores anunciados | **Cumple, con error real provocado** | §6.3 |

### 6.3 A-08 con un error de verdad

Se provocó un fallo real de autenticación en `/admin/acceso` y se midió el DOM
antes y después:

| Momento | Regiones vivas | `aria-invalid` |
| --- | --- | --- |
| Antes de enviar | **0** | 0 |
| Después del fallo | **1**, con `role="alert"` y el texto del error | 0 |

Es la comprobación que el *baseline* de la fase de definición no pudo hacer,
porque en reposo no hay ninguna región viva. **Precisión honesta:** el error que
respondió el backend fue el rechazo de `Origin` de `Task/011`, no un `401` de
credenciales — el navegador de medición no envía el origen esperado. Lo que la
prueba demuestra es **el camino de anuncio accesible del error**, que es
idéntico para ambos.

### 6.4 Responsive — deuda 2 de `Task/015`, absorbida

**10 superficies × 4 anchos = 40 mediciones**, comparando `scrollWidth` con
`clientWidth` y listando todo elemento que sobresalga:

| Ancho | Sin desbordamiento | Elementos desbordados |
| --- | --- | --- |
| 320 px | **10 / 10** | 0 |
| 390 px | **10 / 10** | 0 |
| 768 px | **10 / 10** | 0 |
| 1280 px | **10 / 10** | 0 |

### 6.5 La afirmación que se hace, y la que no

> Se afirma que **A-01, A-02, A-03, A-06 y A-08** se cumplen en las superficies
> medidas, con la evidencia de arriba. **No se afirma que el producto cumpla WCAG
> 2.1 AA**: un recorrido automático cubre una fracción de los criterios, y
> **A-04** sigue sin poder observarse por falta de contenido. Esa parte se cierra
> con `Task/022`.

---

## 7. Rendimiento (F8)

### 7.1 Umbrales y resultado

Laboratorio: Chrome 152 *headless*, red emulada **10 Mbps / 40 ms RTT**, CPU
**4×**, caché deshabilitada. Los pesos salen del informe de `vite build`, que es
**independiente del entorno**.

| # | Métrica | Umbral | Baseline | Final | Veredicto |
| --- | --- | ---: | ---: | ---: | :---: |
| **U-1** | JS del grafo inicial público, *gzip* | ≤ 120 kB | 100,33 kB | **101,94 kB** | **PASS** |
| **U-2** | CSS del grafo inicial público, *gzip* | ≤ 6 kB | 3,15 kB | **3,15 kB** | **PASS** |
| **U-3** | *Chunk* Markdown, *gzip*, fuera del grafo inicial | ≤ 45 kB | 37,11 kB | **37,11 kB**, diferido | **PASS** |
| **U-4** | *Chunk* administrativo, *gzip*, fuera del grafo inicial | ≤ 15 kB | 11,25 kB | **11,24 kB**, diferido | **PASS** |
| **U-5** | Recursos del grafo inicial | ≤ 12 | 4–8 | **4–8** | **PASS** |
| **U-6** | LCP lab, rutas públicas | ≤ 2000 ms | 820–980 ms | **mediana 976 ms** (884–1036) | **PASS** |
| **U-7** | CLS lab, rutas públicas | ≤ 0,10 | 0,0000–0,0359 | **0,0000–0,0359** | **PASS** |
| **U-8** | Imágenes fuera del *viewport* con `loading="lazy"` | 100 % | 100 % en código | **100 % en código**; 0 medibles | **PASS parcial** |
| **U-9** | Imágenes con `width` y `height` | 100 % | ídem | **ídem** | **PASS parcial** |

**U-8 y U-9 son PASS parcial y se declara por qué:** sin contenido no hay
ninguna imagen que renderizar, así que se verifica en el código y en las pruebas,
no en el navegador. Se cierra con `Task/022`.

**El LCP de `/` se midió cuatro veces** (884, 884→1036 ms) porque una primera
lectura dio 1720 ms. Con repeticiones, la mediana es **976 ms**: aquel valor era
un atípico de navegación en frío. Se registra el procedimiento porque una sola
muestra no sostiene una afirmación de rendimiento.

### 7.2 P-05 reverificado en *runtime*

| Ruta | Activos JavaScript cargados |
| --- | --- |
| `/` | solo `index-*.js` |
| `/articulos` | solo `index-*.js` |
| `/quien-soy` | solo `index-*.js` |
| `/admin/acceso` | `index-*.js` **+ `admin-*.js`** |

Es evidencia más fuerte que la guarda sobre `dist/`: mide lo que el navegador
**descarga de verdad**, no lo que el grafo estático sugiere. Las guardas P-05 de
`Task/015` siguen en verde (**27 / 27**).

**Defecto propio detectado y corregido:** al conectar el `noindex` del panel,
`AdminLayout` importaba el *barril* `features/seo`, que arrastra `Seo` y los
constructores de JSON-LD que el panel no usa. Se cambió a un import **directo**
de `NoIndex`. El síntoma fueron 4 pruebas del panel excediendo su espera; en
aislamiento pasaban `51 / 51`. Con el import directo, también en la suite completa.

### 7.3 Miniatura pública — deuda 2 de `Task/010`, cerrada

`MedioPublico` expone ahora `thumbnail_access_url`: un enlace **temporal**, de la
misma naturaleza que `access_url`, hacia la clave **derivada** de la miniatura
(D-010-I). Cambio compatible: añade un campo opcional
(`api-contracts.md` §10, regla 3).

| Fase | Evidencia |
| --- | --- |
| **RED** | `6 failed` — `'MedioPublico' object has no attribute 'thumbnail_access_url'` |
| **GREEN** | `8 passed` en unidad, más 2 pruebas de integración contra **MinIO real** |

**No decide nada de D-08.** No es una URL estable de medios: caduca igual que
`access_url`. La prueba `test_la_clave_de_la_miniatura_no_aparece_como_dato`
extiende la invariante 9 al campo nuevo, y el helper que retira los enlaces
firmados se amplió para no dejar de mirar lo que debe mirar.

**No se exponen las dimensiones de la miniatura:** no se persisten, y `width` y
`height` del original sirven igual para reservar el espacio porque la miniatura
conserva la proporción (D-010-H).

### 7.4 Hallazgo de entorno, sin propietario asignado

El servidor estático local **no comprime** (`Content-Length: 322874`, sin
`Content-Encoding`; ninguna directiva `gzip` en su configuración). Por eso los
umbrales de **peso** se fijaron sobre el *gzip* del *build* y no sobre los bytes
transferidos en local.

**No se modificó nada**: el usuario no autorizó ese cambio en esta tarea. Y **no
se asigna a `Task/018`**, porque ninguna fuente canónica la hace propietaria de
la compresión del servidor local. Queda como deuda **sin propietario**.

---

## 8. Datos estructurados (E-07)

| Tipo | Ruta | Campos, y de dónde salen |
| --- | --- | --- |
| `WebSite` + `SearchAction` | `/` | `name` ← nombre del sitio · `url` · `target` ← la ruta `/buscar?q=` que existe de verdad |
| `Person` | `/quien-soy` | `name` ← `full_name` · `description` ← `seo_description ?? headline` · `sameAs` ← `social_links[].url` |
| `Article` | `/articulos/:slug`, `/proyectos/:slug` | `headline` ← `title` · `description` ← `seo_description ?? summary` · `datePublished` ← `published_at` · `keywords` ← nombres de etiquetas |
| `Review` de `Book` | `/reviews/:slug` | `itemReviewed` ← `book_title` + `book_author` · `reviewRating` ← `rating`, con `bestRating: 5` y `worstRating: 1` |
| `BreadcrumbList` | 3 rutas de detalle | La jerarquía real de `lib/rutas.ts` |

**Nada inventado, y está probado que no:**

- `bestRating`/`worstRating` **no se inventan**: son la decisión **D-D** de
  `data-model.md` —entero 1..5—, impuesta además por un `CHECK` en la base.
- **`dateModified` no se emite**: `updated_at` no está en el DTO público, y esta
  tarea no amplía el contrato para un dato que ninguna fuente pide.
- **`image` no se emite**: la única imagen es la portada, accesible solo por
  `access_url` **caducable**. Es el bloqueo **B-016-1**, de **D-08**.
- **`jobTitle` no se emite**: `headline` es un lema, no un cargo.
- **Fail-closed**: sin `title` no hay `Article`; sin `book_title`, `book_author` o
  `rating` no hay `Review`; sin perfil no hay `Person`. Verificado con pruebas.

Medido en navegador: `/` emite **1** bloque JSON-LD (`WebSite`). `/quien-soy`
emite **0**, que es el comportamiento correcto: `GET /profile` responde `404` sin
semilla (**D-009-N**).

---

## 9. Dependencias — **cero**, verificado

`react-helmet` y `react-helmet-async` se descartaron **por medición**, no por
criterio: React **19.2.8** iza `<title>`, `<meta>` y `<link rel="canonical">` al
`<head>` de forma nativa. El `<script type="application/ld+json">` **no** se iza
y permanece en el `<body>`, donde es válido.

`axe`, `lighthouse` y `playwright` también se descartaron: el arnés de Chrome
*headless* por CDP de `Task/013` y `Task/014` cubrió el recorrido de teclado, el
foco, la semántica, el LCP, el CLS, el grafo de red y el desbordamiento a cuatro
anchos, con **0** dependencias. `defusedxml` tampoco se añadió: el único XML que
se analiza es el que produce este mismo proyecto, en pruebas, y se anotó con
`# noqa: S314` y su motivo.

`npm ls --depth=0` y `requirements*.txt` quedan **sin cambios**.

---

## 10. Validaciones

### 10.1 Frontend

| Compuerta | Comando | Resultado |
| --- | --- | --- |
| Formato | `npm run format:check` | ✔ **exit 0** |
| Lint | `npm run lint` | ✔ **exit 0** |
| Tipado | `npm run typecheck` | ✔ **exit 0** |
| Pruebas | `npm run test:run` | ✔ **688 / 688** en **72** archivos |
| Build | `npm run build` | ✔ **exit 0**, sin *warnings* |
| Guardas SEO sobre `dist/` | `vitest run src/app/seo.guards.test.ts` | ✔ **15 / 15** |
| Guardas **P-05** | `vitest run src/app/p05.guards.test.ts …` | ✔ **27 / 27** |
| Consola del navegador | CDP, 11 rutas | ✔ 0 errores propios; las únicas entradas son los `404` **esperados** de `/profile` sin semilla y un aviso de `HydrateFallback` de `react-router` en el panel |

Baseline heredado: 600 pruebas en 67 archivos → **688 en 72**: **+88** pruebas y
**+5** archivos.

### 10.2 Backend

| Compuerta | Comando | Resultado |
| --- | --- | --- |
| Lint | `ruff check .` | ✔ *All checks passed* |
| Formato | `ruff format --check .` | ✔ 297 archivos ya formateados |
| Tipado | `mypy` | ✔ sin hallazgos en **295** archivos, modo *strict* |
| Pruebas + integración real | `pytest -W error -q` con PostgreSQL y MinIO | ✔ **1631 passed, 1 skipped** |
| Imagen Docker | `docker build` | ✔ construye |
| *Warnings* | `-W error` | ✔ **cero** |

Baseline heredado: 1572 → **1631**: **+59** pruebas. El único omitido es
`time.tzset`, que no existe en Windows.

**Migraciones: no aplica, y se declara.** Ni el sitemap ni la miniatura tocan el
esquema físico: el primero solo lee, y la clave de la miniatura **se deriva** de
`object_key` (D-010-I). **No hay migración nueva** en esta tarea.

### 10.3 Infraestructura

`docker compose config` **válido** tras los dos cambios autorizados.

---

## 11. Pruebas modificadas, y por qué

Ninguna se cambió para acomodar la implementación. Todas responden a un **cambio
de requisito**, que es el primer supuesto que
[`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md)
§9 admite.

| Prueba | Cambio | Motivo |
| --- | --- | --- |
| 3 aserciones del conjunto exacto de campos de `MedioPublico` | Añadido `thumbnail_access_url` | El contrato cambió por **P-04**, de forma compatible |
| 5 filtros `!= "access_url"` en pruebas públicas | Ahora retiran **los dos** enlaces firmados | Hay dos campos de enlace, no uno |
| `_sin_los_enlaces_firmados` | Retira también el nuevo enlace | Si no, dejaría de mirar *«lo que el contrato transporta como dato»* |
| 3 contratos de rutas de OpenAPI | Añadido `/sitemap.xml` | Ruta nueva por **E-05**. El propio archivo documenta que la expectativa ya cambió así en `Task/011` y `Task/012` |
| `test_hermeticidad.py` | El mínimo de arranque incluye la variable nueva | Mismo patrón que usó `Task/010` al añadir el almacenamiento |
| `NotFoundPage.test.tsx` | Envuelve en `AppConfigContext` | La 404 emite metadatos y necesita el origen del sitio |
| `Seo.test.tsx` | `og:image`/`og:site_name`/`twitter:card` pasan a comprobarse en `index.html` | Consecuencia del reparto de §3.2, decidido **por medición** |

### 11.1 Un ajuste que merece explicación: `asyncUtilTimeout`

El techo de espera de Testing Library pasó de **1000 ms** (por defecto) a
**4000 ms**, en un único punto global. **No es inflar un tiempo para tapar un
fallo**, y la diferencia importa:

1. Con un techo alto para **observar**, las **688** pruebas pasan. El producto
   renderiza correctamente.
2. Se midieron las duraciones reales de toda la suite: **p50 = 5 ms**,
   **p95 = 494 ms**, **p99 = 1050 ms**, **máximo = 1879 ms**.
3. Las cuatro más lentas —1686 a 1879 ms— son las que montan el **subárbol del
   panel**, que llega por `import()` diferido: en la suite no hay *bundle*, así
   que ese import transforma y carga un grafo de módulos **durante** la prueba.
   Mil milisegundos nunca fue un presupuesto realista para eso.
4. **Ya fallaban antes de esta tarea.** La primera ejecución del *baseline*, sobre
   `main` sin tocar, dio `3 failed | 597 passed` con esperas agotadas de 8127,
   5696 y 1170 ms; la segunda dio `600 / 600`. Es el riesgo **R-016-1**.

4000 ms es **algo más del doble del máximo medido**: da margen a una máquina
cargada y sigue fallando rápido ante un cuelgue real. No se tocó ningún
`findBy*` en particular.

---

## 12. Correcciones a la ficha, detectadas al implementar

| # | Lo que decía la ficha | Lo que se hizo, y por qué |
| --- | --- | --- |
| 1 | `/buscar` con `canonical` **y** `noindex` (§6.2) | Solo `noindex`. Declarar canónica una URL que se pide no indexar son señales contradictorias, y `noindex,follow` ya resuelve el duplicado por término |
| 2 | `description` y `og:title` de sitio en `index.html` (§7.4) | **Descartado por medición**: React 19 no deduplica y produciría duplicados contradictorios (§3.2). Solo va lo constante por sitio |
| 3 | `/admin/*` con `noindex,nofollow` (§6.2) | `noindex,follow`, como indicó el usuario: se pide no indexar la página, no dejar de seguir sus enlaces |
| 4 | Deuda «que Cloudflare Pages reescriba `/sitemap.xml`» (§9.3) | **Retirada.** El protocolo **no** exige que sitio y sitemap compartan *host*; `robots.txt` puede declararlo en otro anfitrión controlado. No era una dependencia real de `Task/034` |
| 5 | Compresión local como deuda de `Task/018` (§17) | Reasignada a **sin propietario**: ninguna fuente canónica hace a `Task/018` propietaria de la compresión del servidor local |

---

## 13. Bloqueos y deuda

### 13.1 Bloqueos, todos parciales

| # | Bloqueo | Propietario |
| --- | --- | --- |
| **B-016-1** | `og:image` **por contenido**: exige una URL de medio estable que hoy no existe | `Task/030` (**D-08**) |
| **B-016-2** | Open Graph **por URL** para *crawlers* sin JavaScript | **D-21 / ADR-009**, sin tarea asignada |
| **B-016-3** | Código HTTP `404` real | `Task/034` |
| **B-016-4** | Evidencia con contenido real: **A-04**, metadatos de detalle en navegador, peso del *chunk* Markdown en *runtime*, panel autenticado | `Task/022` |

Ninguno impidió entregar. Sobre **B-016-4**: la base local no tiene contenido
**ni administrador** (`administrators = 0`, `posts = 0`, `profiles = 0`), y **no
se fabricó ninguno** para maquillar evidencia.

### 13.2 Deuda

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | `og:image` personalizado por contenido | `Task/030` |
| 2 | Estrategia de *rendering* | **D-21 / ADR-009** |
| 3 | `X-Robots-Tag` para la garantía sin JavaScript de **E-06** | `Task/018` (**S-05**) |
| 4 | HTTP `404` real | `Task/034` |
| 5 | Compresión del servidor estático local | **Sin propietario** |
| 6 | Umbral de TBT, una vez medido | Futura |
| 7 | `dateModified` en `Article` | Sin propietario: ninguna fuente lo pide |
| 8 | `author` en `Article` sin una petición extra | Futura |
| 9 | Índice de sitemaps si se superan los límites del protocolo | Sin propietario |
| 10 | Automatizar estas verificaciones en CI | `Task/019` |
| 11 | Evidencia con contenido real | `Task/022` |

### 13.3 Riesgo vivo

**R-016-1** — la suite del frontend es sensible a la carga de la máquina.
Mitigado con el techo calibrado de §11.1, **no ocultado**. Relevante para
`Task/019`.

---

## 14. Archivos

### 14.1 `personal-blog-frontend`

**Nuevos:** `src/features/seo/{Seo.tsx, NoIndex.tsx, metadatos.ts, esquemas.ts,
index.ts}` y sus pruebas · `src/app/seo.guards.test.ts` · `robots.config.ts` y
`robots.config.test.ts` · `public/og-imagen.png`.

**Modificados:** `index.html` · `vite.config.ts` · `tsconfig.node.json` ·
`Dockerfile` · `.env.example` · `src/vite-env.d.ts` · `src/main.tsx` ·
`src/lib/config/env.ts` y su prueba · `src/app/AdminLayout.tsx` ·
`src/test/{setup.ts, renderRuta.tsx}` · las **11** páginas públicas ·
`src/pages/NotFoundPage.test.tsx` · `src/app/App.test.tsx`.

### 14.2 `personal-blog-backend`

**Nuevos:** `app/modules/sitemap/**` (6 archivos) ·
`tests/unit/{test_documento_de_sitemap.py, test_miniatura_publica.py,
test_configuracion_del_sitio_publico.py}` · `tests/integration/test_api_sitemap.py`.

**Modificados:** `app/main.py` · `app/shared/configuration/settings.py` ·
`app/modules/media/presentation/{acceso.py, schemas.py}` · `.env.example` ·
`tests/__init__.py` · `tests/test_hermeticidad.py` · 3 contratos · 5 pruebas de
integración.

### 13.4 Las tres líneas de *wiring* en `infra`

`infra` entró como repositorio **documental**. Tres puntos exigieron tocar
infraestructura para que la tarea funcionara en local, y **cada uno se autorizó por
separado** antes de ejecutarse:

| # | Archivo | Qué añade |
| --- | --- | --- |
| 1 | `docker-compose.yml` | `BLOG_PUBLIC_SITE_BASE_URL` en el servicio `backend` |
| 2 | `docker/traefik/dynamic/routes.yml` | Un término más en la regla del router `backend`, para `/sitemap.xml` |
| 3 | `docker-compose.yml` | `VITE_SITE_BASE_URL` en `build.args` del `frontend` |

Por eso la clasificación durable de `Task/016` es
**`infra (documentación + wiring local mínimo)`**, y no `infra (documentación)`. **No**
la convierte en una tarea de infraestructura funcional: Nginx y su compresión, CORS,
cabeceras, `X-Robots-Tag` y Cloudflare Pages siguen fuera, con su propietario.

**El tercer punto se verificó de forma no tautológica.** Que el argumento de build
proviene de `TRAEFIK_HTTP_HOST_PORT` —y no del valor por defecto del `Dockerfile`— se
demostró resolviendo la configuración con un puerto distinto, **sin tocar `.env` ni
ningún dato**:

| Resolución | `VITE_API_BASE_URL` | `VITE_SITE_BASE_URL` |
| --- | --- | --- |
| Con el `.env` actual (`8081`) | `http://localhost:8081` | `http://localhost:8081` |
| Con `TRAEFIK_HTTP_HOST_PORT=9317` solo en el entorno del comando | `http://localhost:9317` | **`http://localhost:9317`** |

Ambas siguen al puerto configurado. El `.env` quedó intacto, y el valor por defecto del
`Dockerfile` —`8081`— no es el que se usa al construir por Compose.

### 14.3 `personal-blog-infra`

**Nuevos:** esta ficha, este reporte,
[ADR-009](../adr/ADR-009-rendering-strategy-for-crawlers.md).

**Modificados:** `STATUS.md` · `ROADMAP.md` · `STAGE-05-quality-security.md` ·
`open-decisions.md` · `non-functional-requirements.md` · `api-contracts.md` ·
`docker-compose.yml` **(2 líneas, autorizadas)** ·
`docker/traefik/dynamic/routes.yml` **(1 línea, autorizada)**.

---

## 15. Pasos de validación para el usuario

Con el Compose local levantado:

```powershell
# 1. robots.txt: texto plano real, ya no el index.html de la SPA
curl.exe -i http://localhost:8081/robots.txt

# 2. sitemap.xml: XML servido por el backend
curl.exe -i http://localhost:8081/sitemap.xml

# 3. Lo que ve un crawler SIN JavaScript: solo el Open Graph de SITIO
curl.exe -s http://localhost:8081/articulos/lo-que-sea | Select-String "og:"

# 4. La imagen Open Graph existe y es un PNG
curl.exe -I http://localhost:8081/og-imagen.png
```

En el navegador, con JavaScript, comprobar en tres rutas distintas
—`/articulos`, `/reviews`, `/contacto`— que `title`, `description` y `canonical`
son **distintos y correctos** en cada una; y en `/admin/acceso` y en una ruta
inexistente, que aparece `<meta name="robots" content="noindex,follow">`.

Compuertas:

```powershell
cd personal-blog-frontend
npm run format:check; npm run lint; npm run typecheck; npm run test:run
$env:VITE_API_BASE_URL="http://localhost:8081"; $env:VITE_SITE_BASE_URL="http://localhost:8081"; npm run build

cd ..\personal-blog-backend
.\.venv\Scripts\Activate.ps1
ruff check .; ruff format --check .; mypy; pytest -W error -q
```

---

## 16. Estado

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** |
| **Expresión recibida** | `approved: Task/016-SEO-Accesibilidad-y-Rendimiento` |
| **Fecha** | **2026-09-06** |
| **Avance** | **16 de 41 — 39 %** |
| **ETAPA 05** | **1 de 3 — 33 %** |

**Vigentes con la aprobación:** **D-016-A**, **D-016-B**, los umbrales **U-1 a U-9**, el
contrato de `GET /sitemap.xml`, el campo `thumbnail_access_url` y la clasificación
`infra (documentación + wiring local mínimo)`.

**Sin cambiar, y a propósito:** **D-08 abierta** · **D-21 abierta** · **ADR-009 en
Propuesta** —documenta una decisión que **no se ha tomado**, así que no hay nada que
aceptar— · **ADR-005 Aceptado** · **E-03 no cerrado** · **E-06 parcial** · **A-04** con
evidencia bloqueada por `Task/022` · HTTP `404` real pendiente de `Task/034` ·
`X-Robots-Tag` pendiente de `Task/018`.

### Nota de gobierno — criterio 12

Este documento no persiste estado transitorio de Git ni de GitHub. Los SHA base
son estado duradero exigido por el criterio 11. El estado de ramas remotas y
*pull requests* se consulta en vivo
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §6.1).
