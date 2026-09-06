# TASK-015 — Reporte de implementación

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/015-Panel-Administrativo` |
| **Tipo** | Tarea oficial del roadmap. Cuenta dentro de las **15 de 41 aprobadas** |
| **Etapa** | ETAPA 04 — Experiencia del Usuario |
| **Estado** | **Aprobada** el 2026-09-05 por jeffersondavila |
| **Repositorios** | `personal-blog-frontend` (funcional) · `personal-blog-infra` (gobierno). `personal-blog-backend` **sin rama y sin cambios** |
| **Rama** | `Task/015-Panel-Administrativo` |
| **SHA base** | `ca29657b…` (frontend) · `189ceb86…` (infra, tras la normalización de `Task/012.1`) |
| **Ficha** | [TASK-015](../tasks/TASK-015-admin-panel.md) |

---

## 1. Qué se entregó

Las **18 superficies** del panel administrativo, sobre las primitivas de `Task/013`, el
pipeline de Markdown de `Task/014` y los **27 patrones de ruta / 39 operaciones HTTP** que
`Task/011`, `Task/012` y `Task/012.1` dejaron cerrados.

| # | Ruta | Superficie |
| --- | --- | --- |
| 1 | `/admin/acceso` | Acceso — **única sin guarda** |
| 2 | `/admin` | Dashboard, con las tres piezas de `MVP_SCOPE.md` §3.3 |
| 3–5 | `/admin/articulos`, `/nuevo`, `/:id` | Artículos |
| 6–8 | `/admin/reviews`, `/nuevo`, `/:id` | Reviews |
| 9–11 | `/admin/videos`, `/nuevo`, `/:id` | Videos |
| 12–14 | `/admin/proyectos`, `/nuevo`, `/:id` | Proyectos |
| 15 | `/admin/etiquetas` | Etiquetas |
| 16 | `/admin/medios` | Biblioteca de medios |
| 17 | `/admin/perfil` | Perfil singleton |
| 18 | `/admin/*` | 404 **del panel** |

**Cero dependencias nuevas.** `package.json` y `package-lock.json` **sin cambios**.

## 2. Baseline antes de tocar nada

| Compuerta | Resultado |
| --- | --- |
| `npm run format:check` | All matched files use Prettier code style |
| `npm run lint` | Sin errores |
| `npm run typecheck` | Sin errores |
| `npm run test:run` | **440 passed** en 61 archivos |
| `npm run build` | Correcto con `VITE_API_BASE_URL` |

## 3. Ciclo RED → GREEN

| Slice | RED registrado | GREEN |
| --- | --- | --- |
| Cliente HTTP (**D-015-C**, **D-015-D**) | **3 fallos**: sin `credentials`, `FormData` serializado a JSON y `Content-Type` fijado a mano | 22 passed |
| Routing y layout del panel | Las 18 rutas no resolvían | 20 passed |
| Sesión administrativa | No existía el proveedor | 14 passed |
| Dashboard | La página no existía | 9 passed |
| Formularios, medios y perfil | Las superficies no existían | 18 passed |
| Gate **P-05** | Sin `dist/` con panel, el chunk no existía | 4 passed |

**RED genuino en todos los casos**: por ausencia de la superficie, no por error de sintaxis
ni de importación.

## 4. Arquitectura

### Routing y carga diferida

`src/app/rutasDelPanel.tsx` declara las 18 rutas y **todas** llegan a sus componentes por
`import('../pages/admin')`, un import **dinámico** al mismo módulo. Dos consecuencias, y
las dos son P-05: `routes.tsx` no importa nada del panel de forma estática, y Vite emite
**un solo chunk administrativo** en lugar de dieciocho.

```
/admin              AdminLayout      ← aquí vive AdminSessionProvider
  ├─ acceso         LoginPage        ← sin guarda: `login` es público
  └─ (protegidas)   RutaProtegida
       ├─ index     DashboardPage
       ├─ …         las quince restantes
       └─ *         AdminNotFoundPage
```

El subárbol se monta **antes del comodín público**, que sigue siendo la última entrada.
`SiteLayout` **no se tocó**: `AdminLayout` es hermano, no envoltorio.

### Sesión

`AdminSessionProvider` envuelve **solo** `/admin` (decisión **D-015-G**). La consecuencia
está fijada por prueba: **una visita al sitio público no hace ni una petición a
`/api/v1/admin/*`**.

La credencial vive en la cookie `HttpOnly` y el frontend **no la guarda en ningún sitio** —
hay una prueba que espía `Storage.prototype.setItem` y exige cero llamadas—. La única fuente
de verdad es `GET /admin/auth/me`.

### Cliente HTTP — extensiones mínimas

| Decisión | Cambio | Regresión |
| --- | --- | --- |
| **D-015-C** | `credentials?: RequestCredentials` opcional; los adaptadores admin pasan `'include'` | El sitio público **no declara `credentials`**, fijado por prueba |
| **D-015-D** | Un `FormData` viaja tal cual y **sin `Content-Type`**, para que el navegador ponga el `boundary` | El cuerpo JSON sigue igual |
| Corrección de autenticación | `HttpError.retryAfterSeconds` conserva los segundos del header `Retry-After` de un `429` | Conserva `status`, `code`, `details`, `requestId` y el mensaje seguro; no añade reintentos |

### Corrección de autenticación (2026-09-05)

La revisión posterior confirmó dos defectos: el login deshabilitaba el botón tras un
`429` sin leer la cabecera ni reactivarlo, y la guarda de retorno exigía `/admin/` antes de
comprobar `/admin`, haciendo imposible aceptar el dashboard exacto. El handler tampoco
impedía un submit directo durante la espera. Se corrigieron únicamente estas rutas de
autenticación, sus pruebas y esta evidencia documental.

**Contrato verificado, sin cambiar backend.** `api-contracts.md` §13.4 exige
`429 too_many_requests` con `Retry-After`. En el backend:

- `app/modules/authentication/domain/errores.py:76` construye
  `headers={"Retry-After": str(reintentar_en_segundos)}`.
- `app/modules/authentication/infrastructure/limitador.py:104` calcula
  `max(1, math.ceil(restante))`: segundos enteros, redondeados hacia arriba, mínimo uno.
- `tests/integration/test_limite_de_accesos.py:143` lee la cabecera con `int(...)` y la
  línea 144 exige `0 < reintentar <= 300`. Se inspeccionaron estas pruebas; no se
  reejecutó ni reconstruyó el backend.

`httpErrorFromResponse` lee `response.headers.get('Retry-After')` únicamente en un `429`.
Acepta dígitos que representen un entero positivo seguro de JavaScript. No interpreta
fechas HTTP, decimales, signos, notación exponencial ni `details.retry_after`, y no almacena
el conjunto de cabeceras. `httpClient.ts` ya delegaba en esa función y no necesitó otro
cambio por esta corrección.

**Espera y defensa.** `LoginPage` tiene una única fuente de verdad: `esperaHasta`. Tanto el
botón como `alEnviar` bloquean mientras exista. El timer libera el formulario al vencer;
su cleanup lo cancela al desmontar o sustituir la espera. El límite técnico de `setTimeout`
se maneja por tramos sin acortar el periodo recibido. Nunca se envía otra petición por
iniciativa del temporizador.

Ante una cabecera ausente o inválida, `retryAfterSeconds` queda `undefined`: se conserva
«Demasiados intentos. Espera antes de volver a intentarlo.» y se habilita el intento
**manual**, sin temporizador ni duración inventada. Es una defensa del frontend ante una
respuesta fuera del contrato normal; el backend canónico entrega un entero válido.

**Evidencia RED → GREEN.** Antes de modificar producción, la ejecución focalizada tuvo
24 fallos y 55 éxitos. Las respuestas reales `429` con `Retry-After: 2` y `300` no
conservaban el dato; a los 2000 ms el botón seguía deshabilitado; un submit directo produjo
dos llamadas en vez de una; y la guarda devolvió `false` para `/admin`. Después de la
corrección, **79/79** pruebas focalizadas pasan. Con reloj falso: a los **1999 ms** el botón
está deshabilitado, a los **2000 ms** está habilitado y **LOGIN calls = 1** en todo el
intervalo. También pasan el intento manual posterior, un segundo `429` con su propia
espera, el desmontaje y los cuatro casos defensivos de UI.

La prueba de desmontaje despacha primero el `selectionchange` que jsdom programa a 0 ms al
rellenar los inputs, para contar únicamente el timer de espera: uno antes de desmontar y
cero después. El diagnóstico temporal utilizado para distinguir ambos timers fue retirado.

**Destinos.** La guarda acepta `/admin`, `/admin/etiquetas`, `/admin/articulos/123` y
`/admin/etiquetas?page=2`; rechaza `/`, `/articulos`, `/administrator`, `/admin-mal`, URLs
`http://`, `https://`, `//`, cadena vacía y valores no string. `renderPanel` acepta
`InitialEntry`, sin duplicar helpers. Tres integraciones introducen y comprueban realmente
`state.destino`: `/admin` → `/admin`, `/admin/etiquetas` → `/admin/etiquetas` y
`https://example.com/` → `/admin`. La prueba directa distingue la aceptación de `/admin`
del fallback que lleva a la misma ruta.

**Anti-tautología después del GREEN.** Volver a rechazar `/admin` produjo **1 fallo / 41
éxitos**. Ignorar la cabecera produjo **3 fallos**: las dos pruebas del cliente y la prueba
temporal del login. Las mutaciones se revirtieron byte por byte, con hashes SHA-256 de
restauración comprobados; el diff final conserva la lectura del header y la guarda corregida.

## 5. Dashboard — 12 + 4 + 1 = 17

| Pieza | Peticiones | Operación |
| --- | ---: | --- |
| Conteo por tipo y estado | **12** | `GET /api/v1/admin/{posts,book-reviews,videos,projects}?status={draft,published,archived}&page_size=1` |
| Últimos elementos modificados | **4** | `GET /api/v1/admin/{recurso}?page_size=5` |
| Últimos eventos de auditoría | **1** | `GET /api/v1/admin/audit-events?page_size=5` |
| **Total** | **17** | |

Hay una prueba que cuenta los tres grupos por separado **y su suma**: si alguien volviera a
escribir 16, o dejara de pedir la auditoría, se pone roja. Otra comprueba que **ningún
parámetro fuera de `page`, `page_size` y `status`** llega a la URL — el backend responde
`422` a cualquier clave desconocida.

Los tres bloques cargan en paralelo y con estado propio: hay una prueba de que **un bloque
que falla no impide renderizar los otros dos**.

Del historial se renderizan `occurred_at`, `action` y `entity_type`; `entity_id` puede ser
nulo y se renderiza igual. **No se inventan** `actor_id`, `event_metadata`, `request_id` ni
`ip_address`: el DTO `v1` no los transporta.

## 6. Contenido — lo que la interfaz deriva del contrato

`transicionesDisponibles` deriva los botones del recurso y del estado, no de una tabla
escrita a mano. Fijado por prueba:

| Situación | Botones |
| --- | --- |
| Artículo `published` | Despublicar, Archivar |
| **Vídeo `published`** | **Solo Archivar** — `unpublish` no existe en su contrato |
| Cualquiera `archived` | **Ninguno** — `archived → *` no existe |

Otras reglas comprobadas: el cuerpo **nunca** lleva `status` ni `published_at`; un slug
vacío viaja como `null` para que el backend lo derive del título; el slug queda
**deshabilitado** en cuanto `published_at` deja de ser nulo; y un `409
cannot_publish_incomplete_draft` lista **todos** los campos que faltan a la vez, traducidos.

## 7. Markdown

`<textarea>` nativo + `useDeferredValue` + **el `MarkdownContent` de `Task/014`**. No es
compatibilidad prometida: es **la misma pieza**, luego el mismo `react-markdown`, el mismo
`rehype-sanitize` y el mismo esquema. Una prueba escribe `<script>alert(1)</script>` en el
editor y comprueba que en la vista previa **no queda ningún `<script>` en el documento**.

**El vídeo no tiene editor Markdown**, y hay una prueba de que su formulario **no ofrece
vista previa**: su contenido principal es el vídeo externo.

**No se implementó inserción de imágenes en el cuerpo.** `access_url` caduca y
`api-contracts.md` §12 prohíbe almacenarla; escribir `![alt](access_url)` persistiría un
enlace muerto. La URL estable es **D-08** (`Task/030`).

## 8. Medios y `alt_text`

**Render frente a escritura**, con prueba de cada lado: la imagen se muestra por
`access_url` —comprobado sobre el `src` real del `<img>`— y se asocia por `id`.
`object_key` no aparece por ninguna parte.

La carga va en `multipart`: hay una prueba de que el cuerpo **es un `FormData`** y de que la
petición **no lleva `Content-Type`** propio.

Política de `alt_text`, aplicada tal cual y sin redefinirla: si la imagen no tiene texto, el
campo es editable y se envía; si **ya lo tiene**, se muestra como dato de la imagen y **se
omite del cuerpo**. Omitirlo es lo que hace que `409 alt_text_conflict` **no sea alcanzable
desde el panel**: no se envía un valor que pudiera diferir.

Borrar exige confirmación en línea —sin diálogo modal, que habría sido una primitiva nueva
sin consumidor— y hay pruebas de que **cancelar no llama a `DELETE`** y de que un `409
media_in_use` muestra **dónde** se usa.

## 9. Accesibilidad

**A-03.** `FormField` es el único punto donde se generan `id`, `aria-describedby` y
`aria-invalid`. Toda etiqueta es **visible**, ningún `placeholder` la sustituye, y la
obligatoriedad se comunica con el texto «(obligatorio)» además del atributo — nunca con un
asterisco de color, que violaría **A-07**. Hay una prueba que recorre los campos del
formulario de contenido exigiendo nombre accesible propio.

**A-08.** `FormFeedback` anuncia con `role="alert"` los errores y con `role="status"` los
éxitos, y mueve el foco al mensaje tras un fallo. La lista de campos que faltan al publicar
se comprueba dentro del `alert`.

**Preservados:** A-01 (solo controles nativos, enlace de salto propio en `AdminLayout`),
A-02 (`header`/`nav`/`main`/`footer`, un `h1` por página), A-04 (`MediaImage` reutilizado),
A-05/A-06 (ni un color literal ni un `outline: none`; las guardas de `Task/013` recorren el
árbol y ya cubren los CSS del panel), A-07.

**No se afirma WCAG 2.1 AA**: la auditoría es `Task/016`.

## 10. Gate P-05 — rediseñado y verificado

| # | Comprobación | Resultado |
| --- | --- | --- |
| **P-05-1** | Existe chunk administrativo separado y **fuera** del grafo inicial | ✔ `admin-CeWE45ei.js`, 41,13 kB tras la corrección auth |
| **P-05-2** | Clausura de `import` **estáticos** desde `dist/index.html` sin marcadores admin | ✔ cero coincidencias |
| **P-05-3** | Anti-tautología: los marcadores **sí** existen en `dist/` | ✔ |
| **P-05-4** | Una visita pública no pide `/api/v1/admin/*` ni el chunk admin | ✔ prueba de router real |
| **P-05-5** | `__design-system` ausente de producción | ✔ |

El analizador (`src/test/grafoDeCarga.ts`) parte de los `<script type="module">` y
`<link rel="modulepreload">` de `dist/index.html` y sigue **solo los `import` estáticos** de
forma transitiva. **Sin dependencias nuevas y sin tocar `vite.config.ts`**: habilitar
`build.manifest` para poder medir habría medido otro build.

**Mutación de comprobación.** Se añadió un `import` estático del panel desde `routes.tsx`,
se reconstruyó y **P-05-1 y P-05-2 se pusieron rojas** —Vite avisó además con
`INEFFECTIVE_DYNAMIC_IMPORT`—. La mutación se **revirtió por completo**.

**Evidencia del artefacto servido en la implementación inicial (2026-09-05):** `curl` al
sitio local mostró que `index.html` referenciaba únicamente el chunk de entrada, mientras
que `/assets/admin-*.js` existía y respondía `200` cuando se pedía. La corrección auth
validó el nuevo `dist/`; no reconstruyó la imagen Docker ni repitió aquella observación HTTP.

Tras la corrección, **P-05-1/2/3/5** vuelven a pasar sobre el nuevo build (**4/4**).
**P-05-4** pasa en el router real: una visita a `/` no consulta endpoints administrativos.
No se añadió evidencia de la pestaña Red ni observación visual en navegador.

## 11. Dos defectos que las pruebas encontraron

1. **Las acciones de publicación se dibujaban con un estado por defecto.** El estado venía
   de un `useState('draft')` que solo se corregía tras cargar, así que un contenido
   archivado mostraba «Publicar» durante un instante. Se **derivó del elemento cargado** y
   las acciones no se renderizan hasta que existe. Un botón que ofrece una transición
   imposible es peor que ninguno.
2. **Sincronizar datos cargados dentro de un `useEffect`** provocaba renders en cascada y un
   instante con el formulario vacío sobre datos ya disponibles. Se pasó al patrón
   documentado por React de **ajuste durante el render** con centinela, en
   `PaginaDeContenido` y en `ProfileAdminPage`.

Ninguno de los dos se detectó leyendo el código: los encontró la suite.

## 12. Regresión final

| Compuerta | Baseline | Después |
| --- | --- | --- |
| `format:check` | limpio | **limpio** |
| `lint` | limpio | **limpio** |
| `typecheck` | limpio | **limpio** |
| `test:run` | 440 passed, 61 archivos | **600 passed, 67 archivos** (**+160** respecto de 440; **+43** en la corrección auth) |
| `build` | correcto | **correcto** — chunk `admin-*` separado |
| Dependencias | 5 + 22 | **idénticas**, `git diff package*.json` vacío |

**0 fallos, 0 skips, 0 warnings nuevos.** Las 440 pruebas heredadas siguen en verde: las
doce superficies públicas, su comodín, `/__design-system` DEV-only y las guardas CSS, que
descubren los `*.module.css` recorriendo el árbol y por tanto **ya cubren los del panel**.

**Ejecuciones de la corrección auth (2026-09-05).** La primera regresión, simultánea a
otros checks, obtuvo **595 éxitos / 5 fallos** por consultas que agotaron el plazo al cargar
contenido diferido en `rutasDelPanel`, `sesionAdministrativa`, `DashboardPage` y
`formularios`. Sin modificar sus expectativas ni aumentar sus timeouts, la suite completa
con `--maxWorkers=2` pasó **600/600** en **75,23 s**. El comando original
`npm run test:run`, repetido después sin otros checks pesados simultáneos, también pasó
**600/600** en **51,74 s**, con **67 archivos**, cero fallos y cero omisiones. El resultado
es consistente con contención durante la primera ejecución; no se cambió configuración ni
código de esas superficies.

El build con `VITE_API_BASE_URL=http://localhost:8081` emitió `index-BIsqTzxe.js` y
`admin-CeWE45ei.js` separados. Las cinco comprobaciones P-05 se reejecutaron según §10.
El barrido documental del criterio 12 del 2026-09-05 quedó en **C = 0**: referencias
históricas fechadas o reglas permanentes. Antes de la aprobación, el avance registrado
era **14/41 — 34 %**, ETAPA 04 **2/3 — 67 %** y **B-015-1 RESUELTO**.
La aprobación del usuario del 2026-09-05 lleva el avance a **15/41 — 37 %**, completa
ETAPA 04 en **3/3 — 100 %** y conserva **B-015-1 RESUELTO**.

## 13. Archivos

**Creados (55):** `src/lib/rutasAdmin.ts` y su prueba directa · `src/app/{adminSessionContext.ts,
AdminSessionProvider.tsx, RutaProtegida.tsx, AdminLayout.tsx(+css), rutasDelPanel.tsx}` ·
`src/services/admin/` (10 archivos) · `src/components/{FormField,FormFeedback}/` ·
`src/features/admin/{errores.ts, useCargaAdmin.ts}` · `src/features/admin-content/`
(7 archivos) · `src/features/markdown/MarkdownEditor.tsx(+css)` ·
`src/features/media/MediaPicker.tsx(+css)` · `src/pages/admin/` (12 archivos) ·
`src/test/{renderPanel.tsx, grafoDeCarga.ts}` · 5 archivos de prueba.

**Modificados (5):** `src/app/routes.tsx` (subárbol diferido antes del comodín) ·
`src/services/http/httpClient.ts` y su prueba (**D-015-C**, **D-015-D**) ·
`src/components/index.ts` (los dos compartidos nuevos) · `src/services/http/httpError.ts`
(propagación de `Retry-After`).

**No tocados:** `src/services/public/**`, `SiteLayout` y las once páginas públicas,
`src/entities/**`, `MarkdownContent`/`MarkdownRenderer`/`esquema`, `tokens.css`,
`vite.config.ts`, `tsconfig*.json`, `eslint.config.js`, `package.json`, el lockfile y
**todo `personal-blog-backend`**.

## 14. Limitación declarada — validación visual

**No se ejecutó la validación visual a 320, 390, 768 y 1280 px.** Esta sesión no dispone de
automatización de navegador, y las medidas de desbordamiento horizontal exigen un motor de
render real: `jsdom` no aplica hojas de estilo.

Lo que **sí** se verificó, y lo que queda pendiente:

| Aspecto | Estado |
| --- | --- |
| Estrategia responsive | **Verificable por lectura**: rejillas `auto-fit` con `minmax(min(…, 100%), 1fr)`, `Stack wrap`, `Container`. **Ninguna media query de ancho** y **ninguna barra lateral de ancho fijo** — que es la causa habitual de desbordamiento a 320 px |
| Ausencia de colores literales y de `outline: none` | **Verificado**: las guardas CSS de `Task/013` recorren todo `src/**/*.module.css` |
| El panel se sirve y responde en local | **Verificado** por HTTP: `/admin/acceso` responde `200` y el chunk admin se sirve aparte |
| Medición a los cuatro anchos, foco con Tab en el navegador, ausencia de `console.error` | **Pendiente de tu revisión** |

A esto se suma la limitación ya declarada en la ficha: **no hay administrador ni perfil en
la base local** —la semilla es de `Task/022`—, así que el recorrido funcional real en el
navegador no puede completarse. `GET /api/v1/admin/auth/me` responde `401` en el entorno
local, que es exactamente lo que el contrato dicta sin sesión.

**No se creó ninguna semilla para «que se vea bonito»**, y no se tocó el backend.

## 15. Condiciones del entorno local

Dos, ya anticipadas como riesgos en la ficha, y ninguna es un defecto del frontend:

1. **Mismo origen.** El backend no tiene middleware CORS (es de `Task/018`), así que el
   panel debe servirse por la topología Traefik de `Task/007` —`http://localhost:8081`—,
   que es lo que `.env.example` ya describe. Con `vite dev` en otro origen, ninguna petición
   administrativa funcionaría.
2. **`BLOG_ADMIN_ALLOWED_ORIGINS`.** Vacío, **toda escritura responde `403`** (*fail-closed*
   deliberado de `Task/011`). El panel lo distingue de un `401` con mensaje propio y **no
   redirige al acceso**, que produciría un bucle.

## 16. Deuda técnica pendiente

| # | Deuda | Propietario |
| --- | --- | --- |
| 1 | Insertar imágenes dentro del cuerpo Markdown: exige URL estable | **D-08**, `Task/030` |
| 2 | Validación visual a cuatro anchos y recorrido con teclado en navegador | Revisión del usuario |
| 3 | Recorrido funcional completo con administrador y contenido reales | `Task/022` |
| 4 | CORS con credenciales para la topología *cross-origin* de **D-15** | `Task/018` |
| 5 | `noindex` del panel (**E-06**) y código HTTP de la 404 | `Task/016`, `Task/034` |
| 6 | Restringir `provider` en el **backend** a la lista cerrada de `Task/014` | Backend, candidata `Task/018` |
| 7 | El listado administrativo devuelve el `content` completo de cada elemento | Backend, sin propietario |
| 8 | Mostrar autor, contexto o correlation ID de un evento de auditoría | `Task/017` (**el DTO `v1` no los transporta**) |
| 9 | Progreso de carga de imágenes: `fetch` no lo expone y el contrato no lo pide | Sin propietario |

## 17. Pasos de validación para el usuario

```powershell
# Compuertas (personal-blog-frontend)
npm run format:check; npm run lint; npm run typecheck; npm run test:run

# Si la carga de la maquina agota el plazo de las pruebas con imports diferidos:
npm run test:run -- --maxWorkers=2

# Regresion acotada de autenticacion (incluye los timers falsos y state.destino)
npx vitest run src/services/http/httpClient.test.ts src/app/sesionAdministrativa.test.tsx src/lib/rutasAdmin.test.ts

# Build y gate P-05 sobre el artefacto real
$env:VITE_API_BASE_URL = "http://localhost:8081"
npm run build
npx vitest run src/app/p05.guards.test.ts
npx vitest run src/app/rutasDelPanel.test.tsx -t "una visita publica"

# El recuento del dashboard: 12 + 4 + 1 = 17
npx vitest run src/pages/admin/DashboardPage.test.tsx -t "17 peticiones"

# 0 dependencias nuevas (salida vacía)
git diff --stat package.json package-lock.json

# El backend no cambió (salida vacía)
git -C ..\personal-blog-backend status --porcelain
```

Para verlo en el navegador, con el entorno local en marcha y la imagen del frontend
reconstruida: **http://localhost:8081/admin/acceso**. Sin administrador en la base local el
acceso responderá `401`; es la limitación de §14, no un fallo.

## 18. Aprobación

| Campo | Valor |
| --- | --- |
| **Estado** | **Aprobada** |
| **Fecha de aprobación** | 2026-09-05 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/015-Panel-Administrativo` |

La tarea solamente puede aprobarse cuando el usuario escribe exactamente
`approved: Task/015-Panel-Administrativo`.

Antes de esa autorización, [WORKFLOW.md §3](../project-management/WORKFLOW.md#3-aprobación-y-cierre)
prohíbe commit, merge, push y creación de pull request.

La autorización del usuario del 2026-09-05 promueve **D-015-A** a **D-015-H**,
**D-015-J** y **D-015-K** a **Vigentes**. **D-015-I** continúa **retirada** y **D-04**
queda **Resuelta**. La aprobación conserva las limitaciones de §14 y §15.

El cierre integra la rama Task en `dev` y publica el PR **Task → main**. La fusión hacia
`main` corresponde al usuario; después se normaliza `main → dev`. `Task/016` permanece
**Pendiente, no iniciada** y requiere una nueva instrucción. El estado operativo de ramas,
commits y PR se consulta en Git y GitHub, según WORKFLOW §6.1.
