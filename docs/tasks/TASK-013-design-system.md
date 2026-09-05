# TASK-013 — Sistema de Diseño

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/013-Sistema-de-Diseno` |
| **Nombre** | Sistema de Diseño |
| **Etapa** | ETAPA 04 — Experiencia del Usuario |
| **Estado** | **Aprobada** ✔ |
| **Repositorios involucrados** | `personal-blog-frontend` (funcional) · `personal-blog-infra` (gobierno documental) |
| **Dependencias** | `Task/012-API-Administrativa` — **Aprobada** ✔ (2026-09-03) |
| **Rama** | `Task/013-Sistema-de-Diseno` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base (frontend)** | `fd62f221707591a984cf0fb51a03ea339380ab35` |
| **SHA base (infra)** | `1b6f0c4776311009fde37461608b18c94419cc9f` |
| **Fecha de inicio** | 2026-09-03 |
| **Última actualización** | 2026-09-04 |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

| # | Comprobación | Resultado frontend | Resultado infra |
| --- | --- | --- | --- |
| 1 | `main == origin/main` | ✔ `fd62f22` | ✔ `1b6f0c4` |
| 2 | Working tree limpio antes de crear la rama | ✔ vacío | ✔ vacío |
| 3 | Rama creada **desde `main`** | ✔ | ✔ |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | ✔ idénticos | ✔ idénticos |
| 5 | `git rev-list --count main..HEAD` | ✔ `0` | ✔ `0` |
| 6 | `main` es ancestro de `dev` y `dev..main = 0` | ✔ | ✔ |

`personal-blog-backend` **no recibe rama**: la tarea no lo modifica. Queda en `main`
limpio, en solo lectura.

---

## 1. Objetivo

Entregar la base visual y de componentes **reutilizable** que `Task/014` (sitio público)
y `Task/015` (panel administrativo) consumirán, de modo que ninguna de las dos tenga que
inventar por su cuenta colores, espaciados, tipografía, radios, foco, botones,
superficies ni semántica de estado.

La tarea es **fundacional, no de producto**: no construye páginas.

---

## 2. Contexto

La ETAPA 03 cerró el backend: el contrato completo del API público y administrativo ya
existe. La ETAPA 04 convierte ese API en producto. El roadmap coloca el sistema de diseño
**primero** por una razón explícita en
[`STAGE-04`](../stages/STAGE-04-user-experience.md): *«el sistema de diseño va primero
para evitar inconsistencia visual y reescrituras de componentes»*, y el riesgo registrado
en esa misma ficha —*«inconsistencia visual entre sitio público y panel»*— se mitiga
precisamente porque ambos consumen el sistema de `Task/013`.

El frontend existe desde `Task/006` y consume el backend desde `Task/007`. Su
`global.css` actual declara, textualmente, que *«el sistema de diseño del proyecto
—tokens, tipografía, escala de espaciado, componentes— es `Task/013`»* y que allí solo
hay «lo imprescindible». Esta tarea es el reemplazo previsto de ese mínimo.

Además, `Task/013` es la propietaria designada de la decisión diferida **D-03 —
Biblioteca de componentes visuales**
([`open-decisions.md`](../architecture/open-decisions.md)).

---

## 3. Dentro del alcance

- [x] Matriz previa del sistema de diseño (sección 6) — **antes** de código productivo.
- [x] Tokens de diseño como CSS Custom Properties: color, tipografía, espaciado, forma,
      layout, breakpoints, foco y movimiento.
- [x] Colores **semánticos** con pares de contraste definidos y **verificados**.
- [x] Fundación global: `box-sizing`, defaults de documento, tipografía, estrategia de
      foco y respeto a `prefers-reduced-motion`.
- [x] Tipografía: familias, escala, pesos y alturas de línea.
- [x] Comportamiento responsive base, **intrínseco**, sin hacks por dispositivo.
- [x] Primitivas base compartidas: `Container`, `Stack`, `Button`, `Card`, `Badge`.
- [x] Accesibilidad base propiedad de esta tarea: **A-05** (contraste), **A-06** (foco
      visible), **A-07** (sin dependencia exclusiva del color) e inicio de **A-01**
      (teclado).
- [x] Utilidad pura de cálculo de contraste y pruebas sobre los tokens reales.
- [x] Guardas ejecutables del sistema: sin colores literales en componentes, sin
      `outline` suprimido, sin tokens inexistentes.
- [x] Superficie pública de importación para `Task/014` y `Task/015`.
- [x] Superficie de demostración **exclusiva de desarrollo**, ausente del build de
      producción.
- [x] Resolución de **D-03** — **Vigente** desde el 2026-09-04.
- [x] Documentación: ficha, reporte, `STATUS`, `ROADMAP`, `STAGE-04`, `open-decisions`.

---

## 4. Fuera del alcance

| Queda fuera | Tarea propietaria |
| --- | --- |
| Páginas del sitio público: Inicio, Quién soy, Artículos, Reviews, Videos, Proyectos, Contacto, 404 real | `Task/014` |
| HTML semántico de página (**A-02**) y `alt` en el render público (**A-04**) | `Task/014` |
| Panel administrativo, dashboard, editor Markdown, formularios CRUD, carga de imágenes, vista previa | `Task/015` |
| Labels de formulario (**A-03**) y anuncio accesible de errores (**A-08**) | `Task/015` |
| Editor Markdown concreto (**D-04**) | `Task/015` |
| SEO: `title` y `description`, Open Graph, canonical, sitemap, `robots`, datos estructurados | `Task/016` |
| Auditoría formal de accesibilidad y umbrales de rendimiento | `Task/016` |
| Sanitización del render Markdown (**S-03**) | `Task/014`, `Task/015`, `Task/018` |
| Rutas de producto y layouts de sitio y panel | `Task/014`, `Task/015` |
| Modo oscuro | Sin tarea: **no lo pide ninguna fuente canónica** |
| Icono real del sitio (favicon) | `Task/014` — ver decisión D-13.6 |

**No se toca:** backend, Docker, PostgreSQL, MinIO, Terraform, AWS, cliente HTTP
(`src/services/http/*`), ni versiones de dependencias.

---

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Tokens de diseño | frontend | `src/styles/tokens.css` |
| Fundación global: reset, tipografía, foco, motion | frontend | `src/styles/foundation.css` |
| Composición de estilos globales | frontend | `src/styles/global.css` |
| Utilidad pura de contraste | frontend | `src/lib/color/contrast.ts` |
| Verificación de contraste sobre los tokens reales | frontend | `src/styles/contrast.test.ts` |
| Guardas del sistema de diseño | frontend | `src/styles/designSystem.guards.test.ts` |
| `Container` | frontend | `src/components/Container/` |
| `Stack` | frontend | `src/components/Stack/` |
| `Button` | frontend | `src/components/Button/` |
| `Card` | frontend | `src/components/Card/` |
| `Badge` | frontend | `src/components/Badge/` |
| Superficie pública | frontend | `src/components/index.ts` |
| Demostración solo-desarrollo | frontend | `src/pages/DesignSystemPage.tsx` y ruta condicional |
| Ficha | infra | `docs/tasks/TASK-013-design-system.md` |
| Reporte | infra | `docs/task-reports/TASK-013-report.md` |
| Estado y avance | infra | `STATUS.md`, `ROADMAP.md`, `STAGE-04-user-experience.md` |
| **D-03** resuelta | infra | `docs/architecture/open-decisions.md` |

---

## 6. MATRIZ DEL SISTEMA DE DISEÑO

> **Decision gate.** Esta sección se completó **antes** de escribir código productivo.
> Todo lo que sigue está derivado de las fuentes canónicas, no de preferencia estética.

### 6.A Identidad visual

Ninguna fuente canónica define marca, paleta corporativa ni familia tipográfica. El
producto es un **blog personal de un único autor** ([`MVP_SCOPE`](../product/MVP_SCOPE.md)
§1) cuyo valor es el **contenido de lectura**: artículos, reviews, videos, proyectos y
perfil.

| Aspecto | Decisión | Fuente o razón |
| --- | --- | --- |
| Tono | Sobrio y editorial. Neutro, sin identidad comercial inventada. | No existe marca definida; inventarla sería una decisión de producto que nadie tomó. |
| Densidad | Cómoda para lectura en el sitio; la escala admite composiciones más densas en el panel. | `MVP_SCOPE` §2 (lectura) frente a §3 (dashboard y listados). |
| Jerarquía | Por **tamaño y peso** tipográfico, no por color. | **A-07**. |
| Contraste | Alto. El texto principal supera con holgura AA sobre fondo. | **A-05**. |
| Uso del color | El color **acompaña**; nunca es el único portador de significado. | **A-07**. |
| Sitio público | Columna de lectura acotada, tarjetas de listado y etiquetas. | Flujos A.1–A.11. |
| Panel | Superficies, acciones y estados de contenido. | Flujos B.1–B.12. |

### 6.B Tokens — qué categorías hacen falta de verdad

| Categoría | ¿Se crea? | Razón |
| --- | :---: | --- |
| Color | **Sí** | **A-05** y **A-07** son responsabilidad de esta tarea. |
| Tipografía | **Sí** | Alcance explícito del roadmap. |
| Espaciado | **Sí** | `CONTRIBUTING` §6 prohíbe «valores mágicos de espaciado». |
| Forma: radio y grosor de borde | **Sí** | Botón, tarjeta y badge lo comparten. |
| Layout: anchos y gutter | **Sí** | Responsive base; columna de lectura frente a listados. |
| Breakpoints | **Sí** | Contrato de umbrales compartido por `Task/014` y `Task/015`. |
| Foco | **Sí** | **A-06** exige una estrategia **de sistema**, no una por componente. |
| Movimiento | **Sí**, mínimo: 1 token | Transición compartida por botón y enlace, con guarda `prefers-reduced-motion`. |
| Elevación y sombras | **No** | El lenguaje visual es plano y editorial: la separación se resuelve con borde y superficie. Un token sin uso sería infraestructura vacía (**M-06**). |
| `z-index` | **No** | No existe ningún elemento superpuesto en `Task/013`: sin modales, menús ni tooltips. Se creará cuando exista el primer consumidor real. |
| `letter-spacing` | **No** | No aporta valor demostrable a esta escala, y §15 lo condiciona a que lo aporte. |

### 6.C Componentes base — inventario derivado

Derivado de [`USER_FLOWS`](../product/USER_FLOWS.md),
[`MVP_SCOPE`](../product/MVP_SCOPE.md) §2–§3 y
[`STAGE-04`](../stages/STAGE-04-user-experience.md).

| Componente | ¿`Task/014`? | ¿`Task/015`? | ¿Aquí? | Razón |
| --- | :---: | :---: | :---: | --- |
| `Container` | Sí | Sí | **Sí** | Ancho de lectura (A.3, A.5) y ancho de listado o dashboard. Sin él, cada página inventa su `max-width`. |
| `Stack` | Sí | Sí | **Sí** | Único mecanismo de separación; evita los márgenes sueltos que `CONTRIBUTING` §6 prohíbe. Cubre el eje vertical y el horizontal con envoltura: listas de etiquetas y filas de acciones. |
| `Button` | Sí | Sí | **Sí** | Reintento de carga (A.1, A.2), paginación (A.2, A.4) y toda acción del panel. |
| `Card` | Sí | Sí | **Sí** | Elemento de listado (A.2, A.4, A.6, A.7) y tarjeta de dashboard (§3.3). |
| `Badge` | Sí | Sí | **Sí** | Etiquetas públicas (A.2, A.9) y **estados de contenido** del panel (`MVP_SCOPE` §3.2). Es donde **A-07** se demuestra. |
| Enlace (`Link`) | Sí | Sí | **No — CSS global** | Un envoltorio pelearía con `react-router`. La garantía real —color tokenizado y foco visible— se cumple estilando `a` globalmente. §22: navegación es enlace, no botón. |
| `Heading` y `Text` | Sí | Sí | **No — CSS global sobre `h1`–`h6` y `p`** | Un `<Heading level={2}>` no añade nada sobre `<h2>` y facilita elegir el nivel equivocado. **A-02** es de `Task/014`, que debe escribir el elemento correcto. |
| `VisuallyHidden` | — | — | **No** | Sin consumidor: `Task/013` no tiene ningún control solo-icono. Crearlo ahora sería infraestructura vacía (**M-06**). |
| `Divider` | — | — | **No** | Sin consumidor demostrado. |
| `IconButton` | — | Probable | **No** | Su primer consumidor real está en `Task/015`. |
| `Input`, `Textarea`, `Select`, `Checkbox`, `FormField`, `ValidationMessage` | — | Sí | **No** | **A-03** y **A-08** son de `Task/015`, que además decide **D-04**. Construir campos sin su semántica de validación produciría primitivas que habría que rehacer. |
| Tabla, paginación, layout de panel | Sí | Sí | **No** | Son composición de página, no primitivas. |

### 6.D Responsive — qué se resuelve aquí

| Se resuelve en `Task/013` | Pertenece a `Task/014` o `Task/015` |
| --- | --- |
| Gutter fluido con `clamp`, sin salto por dispositivo. | Rejillas de listado y su número de columnas. |
| Anchos de contenedor: `prose` y `wide`. | Layout del panel: barra lateral y contenido. |
| Escala tipográfica fluida en encabezados. | Navegación móvil y menús. |
| Envoltura de agrupaciones horizontales. | Comportamiento de tablas en pantalla estrecha. |
| Ausencia de anchos rígidos en las primitivas. | Validación visual integral de páginas reales. |
| Tokens de breakpoint como contrato compartido. | Uso de esos breakpoints en sus rejillas. |

**Principio:** el diseño es *intrínsecamente* responsive (`clamp`, `min()`, `flex-wrap`).
Las primitivas de `Task/013` **no necesitan** ninguna media query de ancho — eso es una
propiedad deseada, no una omisión.

### 6.E Accesibilidad — qué garantiza esta tarea

| # | Requisito | ¿Propiedad de `Task/013`? | Cómo se demuestra |
| --- | --- | --- | --- |
| **A-05** | Contraste texto/fondo | **Sí, completa para los tokens** | Prueba que lee `tokens.css` y calcula el ratio real de cada par declarado. |
| **A-06** | Foco visible, nunca suprimido sin reemplazo | **Sí, completa** | Estrategia global `:focus-visible` y guarda que prohíbe `outline: none`. |
| **A-07** | Sin dependencia exclusiva del color | **Sí, para los componentes de esta tarea** | `Badge` con tono exige texto y añade un glifo de **silueta distinta** por tono. |
| **A-01** | Navegación con teclado | **Se inicia aquí** | Solo elementos nativos; pruebas de foco y activación por teclado. Continúa en `Task/014`–`Task/016`. |
| A-02, A-03, A-04, A-08 | — | **No** | Propietarias: `Task/014` y `Task/015`. `Task/013` **no las cierra**. |

**Afirmación permitida:** *la paleta y los pares que `Task/013` define y verifica cumplen
WCAG 2.1 AA*. **No** se afirma que el producto cumpla AA: eso lo audita `Task/016`.

### 6.F Theming

| Pregunta | Respuesta | Razón |
| --- | --- | --- |
| ¿Cuántos temas? | **Uno**, claro. | Ninguna fuente canónica pide más. |
| ¿`ThemeProvider` de React? | **No.** | No resuelve ningún problema real: no hay tema conmutable ni estado. Un provider vacío contradice **M-06**. El punto de extensión de `App.tsx` **sigue disponible**; no se rellena por rellenarlo. |
| ¿Mecanismo? | **CSS Custom Properties en `:root`.** | Runtime nativo, cascada, sin dependencia, reutilizable por sitio y panel, y no impide una futura variación de tema. |
| ¿Modo oscuro? | **No.** | Funcionalidad especulativa. **Consecuencia obligatoria:** `global.css` declara hoy `color-scheme: light dark`; mantenerlo con una paleta solo-clara permitiría al navegador pintar un lienzo oscuro bajo colores diseñados para fondo claro, y **rompería A-05**. Se corrige a `color-scheme: light`. Esto **no** es implementar modo oscuro: es dejar de prometer uno que no existe. |

### 6.G Estrategia CSS

| Alternativa | Veredicto |
| --- | --- |
| Tailwind, MUI, Chakra, Bootstrap, styled-components, Emotion, Sass | **Rechazadas.** Ninguna fuente canónica exige un framework de estilos. Añadirlo implica dependencia, peso de bundle y pelear con sus decisiones de accesibilidad, contra **P-01**, **P-05** y **M-06**. |
| CSS global con convención de prefijos | Viable, pero los nombres de clase quedan como API pública accidental y el riesgo de colisión crece con `Task/014` y `Task/015`. |
| **CSS Modules (nativo de Vite) + CSS Custom Properties** | **Elegida.** Cero dependencias nuevas, encapsulamiento real, y los nombres hasheados hacen **estructuralmente imposible** que `Task/014` o `Task/015` dependan de una clase interna. |

Los **tokens y la fundación** permanecen en CSS global (`src/styles/`) porque su
globalidad es intencional; solo los **componentes** usan módulos.

> **Consecuencia verificada del `tsconfig` estricto:** con
> `noPropertyAccessFromIndexSignature`, las clases se acceden como `styles['x']`, no
> `styles.x`. Comprobado empíricamente **antes** de decidir.

### 6.H Tipografía

| Decisión | Valor | Razón |
| --- | --- | --- |
| Webfonts | **No** | Ninguna fuente canónica fija una familia. Una webfont añade peso, latencia, una consideración de privacidad y un fallback que mantener, sin beneficio pedido. **P-01**. |
| Familia de interfaz y lectura | *System font stack* | Cero bytes, renderizado nativo, disponible en todas las plataformas. §17 lo propone como línea base. |
| Familia monoespaciada | Stack de sistema | Ya la usa `code` en el `global.css` actual. |

### 6.I Dependencias

**Objetivo: cero dependencias nuevas**, de runtime y de desarrollo. Todo lo necesario
—CSS Modules, `clamp`, custom properties, SVG inline— es plataforma o ya está en el
stack. `package.json` y `package-lock.json` **no deben cambiar**.

### 6.J Superficie de demostración

| Opción | Veredicto |
| --- | --- |
| A. Solo pruebas y CSS | Insuficiente por sí sola: una tarea **visual** debe poder verse. |
| B. Harness interno no enrutable | Equivalente a A en la práctica: sin ruta no se abre en el navegador. |
| **C. Ruta explícita de desarrollo** | **Elegida.** Guardada por `import.meta.env.DEV`, ausente del build de producción y verificada como tal. |
| D. Storybook | **Rechazada.** Dependencia grande para cinco primitivas; convierte el proyecto en librería. §29. |

---

## 7. TDD / Plan test-first

> `Task/013` es **frontend**.
> [`BACKEND_TESTING_STRATEGY`](../project-management/BACKEND_TESTING_STRATEGY.md)
> **no aplica** como regla de `pytest`. Sí se trabaja comportamiento por comportamiento:
> se especifica, se prueba donde la prueba tiene señal real, se implementa y se
> refactoriza.

### 7.1 Dónde la prueba tiene señal real, y dónde no

| Sí se prueba | No se prueba, y por qué |
| --- | --- |
| Semántica del elemento raíz: `button`, `span`, `div`. | Que un color «se vea bien». |
| Atributos preservados: `type`, `disabled`, `aria-*`. | *Layout* real: JSDOM no calcula cajas. |
| Nombre accesible. | Que el foco «se note»: JSDOM no pinta el `outline`. |
| Activación por teclado y ausencia de activación si `disabled`. | Media queries y `clamp` resueltos. |
| Señal **no cromática** presente en cada tono. | |
| Ratios de contraste sobre los **valores reales** de `tokens.css`. | |
| Ausencia de color literal y de `outline` suprimido en el CSS fuente. | |

### 7.2 Matriz de comportamiento

**Tokens**

| # | Comportamiento | Cómo se verifica |
| --- | --- | --- |
| T-01 | Ningún componente define un color propio: todos vienen del sistema. | Guarda: sin `#hex`, `rgb()` ni `hsl()` literal en los `*.module.css`. |
| T-02 | Los pares críticos de contraste están definidos y cumplen el umbral. | Prueba de contraste sobre `tokens.css`. |
| T-03 | Espaciado coherente: escala única, sin valores mágicos. | Guarda: todo `var(--...)` referenciado existe en `tokens.css`. |
| T-04 | Tipografía coherente: familias, tamaños, pesos y alturas tokenizados. | T-03 más revisión de `foundation.css`. |

**Foco**

| # | Comportamiento | Cómo se verifica |
| --- | --- | --- |
| F-01 | `Button` recibe foco y es alcanzable con teclado. | Prueba: `.focus()` lo deja como `activeElement`. |
| F-02 | El enlace tiene foco visible por la misma estrategia global. | Guarda CSS: existe una regla `:focus-visible` global. |
| F-03 | Ningún reset elimina el foco sin reemplazo. | Guarda CSS: sin `outline: none` ni `outline: 0`. |

**Button**

| # | Comportamiento | Cómo se verifica |
| --- | --- | --- |
| B-01 | Es un `<button>` nativo. | `getByRole('button')` y `tagName`. |
| B-02 | `disabled` es real: el DOM lo marca y no se activa. | Atributo más click sin efecto. |
| B-03 | `type` se conserva cuando el consumidor lo indica; por defecto es `button`. | Dos pruebas. |
| B-04 | Los hijos forman el nombre accesible. | `getByRole('button', { name })`. |
| B-05 | Las variantes se distinguen sin perder semántica ni atributos. | Render de ambas variantes. |

**Estado y color**

| # | Comportamiento | Cómo se verifica |
| --- | --- | --- |
| S-01 | El significado del tono **no** depende solo del color. | Cada tono no neutro renderiza un glifo de silueta propia. |
| S-02 | El texto siempre está presente y es el portador principal. | `children` obligatorio; se comprueba el texto accesible. |
| S-03 | El glifo es decorativo: no ensucia el nombre accesible. | `aria-hidden` en el SVG. |

**Responsive**

| # | Comportamiento | Cómo se verifica |
| --- | --- | --- |
| R-01 | El contenedor no fuerza desbordamiento horizontal. | Inspección CSS: `width: 100%` más `max-width`, nunca ancho rígido. |
| R-02 | El gutter varía de forma continua. | `clamp()` en el token de gutter. |
| R-03 | Nada depende de un dispositivo concreto. | Ausencia de media queries de ancho en las primitivas. |

**API pública**

| # | Comportamiento | Cómo se verifica |
| --- | --- | --- |
| A-01 | Las importaciones públicas son claras y únicas. | `src/components/index.ts` exporta componentes y tipos. |
| A-02 | Los consumidores no necesitan importar internals. | La demostración importa solo desde el barrel. |

**Regresión**

| # | Comportamiento | Cómo se verifica |
| --- | --- | --- |
| G-01 | `App` sigue renderizando. | Suite existente de `App`. |
| G-02 | El router sigue funcionando. | Ídem. |
| G-03 | El cliente HTTP queda intacto. | `git diff` vacío sobre `src/services/http/` más su suite. |
| G-04 | La 404 base sigue funcionando. | Suite existente. |

### 7.3 Integración necesaria

**Ninguna.** No hay PostgreSQL, MinIO ni backend en el alcance.

### 7.4 Regresiones relevantes

Las **50 pruebas** existentes en **6 archivos** deben seguir en verde **sin modificarse**.

---

## 8. Plan de validación

1. Guardas y contraste ejecutables (`npm run test:run`).
2. Pruebas de comportamiento por primitiva.
3. Regresión completa de la suite.
4. `format:check`, `lint`, `typecheck`, `build`.
5. Comprobación de que la superficie de demostración **no** está en `dist/`.
6. Comprobación de que `package.json` y `package-lock.json` no cambiaron.
7. Inspección del CSS para lo que JSDOM no puede demostrar.

## 9. Comandos de validación

```bash
npm run format:check
npm run lint
npm run typecheck
npm run test:run
npm run test:coverage
npm run build

# El cliente HTTP y el manifiesto de dependencias no cambian.
git diff --stat main -- package.json package-lock.json src/services/http

# La superficie de demostracion no viaja al build de produccion.
grep -ril "design-system" dist/
```

## 10. Evidencia esperada

- Tabla de pares de contraste con su ratio calculado sobre los tokens reales.
- Salida de las seis compuertas de calidad.
- Ausencia probada de la superficie de demostración en el build.
- Diff vacío en cliente HTTP y manifiesto de dependencias.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| 1 | Construir un «framework de UI» en lugar de la base necesaria. | Alcance desbordado; componentes sin consumidor. | Inventario derivado de flujos canónicos (§6.C), con veredicto y razón por componente. |
| 2 | Adelantar `Task/014` o `Task/015`. | Rompe la secuencia del roadmap. | Prohibición explícita de páginas, formularios y layouts; solo primitivas. |
| 3 | Elegir colores «porque se ven bien» y fallar AA. | Deuda de accesibilidad heredada por todo el producto. | Ratios calculados y **verificados por prueba** sobre los valores reales. |
| 4 | Que `Task/014` o `Task/015` dependan de clases CSS internas. | API pública accidental. | CSS Modules con nombres hasheados y barrel público. |
| 5 | Afirmar cumplimiento AA del producto. | Afirmación falsa; invade `Task/016`. | La afirmación se acota a los pares definidos y verificados aquí. |
| 6 | Que la superficie de demostración contamine producción. | Ruta pública no prevista; afecta a `Task/016` (sitemap y `robots`). | Guardada por `import.meta.env.DEV` y **verificada** ausente de `dist/`. |
| 7 | Declarar «responsive validado» sin poder verlo. | Afirmación no sostenible. | Se declara explícitamente qué puede y qué no puede demostrarse sin navegador. |

## 12. Decisiones técnicas

| # | Decisión | Alternativas | Justificación | ¿ADR? |
| --- | --- | --- | --- | --- |
| D-13.1 | **CSS Modules + CSS Custom Properties**, cero dependencias. | Tailwind, MUI, Chakra, styled-components, Emotion, Sass, CSS global con prefijos. | Nativo de Vite; encapsulamiento real; ninguna fuente canónica exige framework. **Resuelve D-03.** | No — no reemplaza ninguna decisión aceptada; se registra en `open-decisions`. |
| D-13.2 | **Sin `ThemeProvider`.** Tokens en `:root`. | Provider de React con contexto de tema. | No hay tema conmutable; un provider vacío viola **M-06**. | No |
| D-13.3 | **Un solo tema, claro.** `color-scheme: light`. | Modo oscuro; mantener `light dark`. | Modo oscuro es especulativo; mantener `light dark` con paleta clara rompería **A-05**. | No |
| D-13.4 | **System font stack**, sin webfonts. | Google Fonts, fuente autoalojada. | Cero bytes y ninguna fuente canónica fija familia. **P-01**. | No |
| D-13.5 | **Sin componentes de enlace, encabezado ni texto**; CSS global sobre elementos nativos. | `Link`, `Heading`, `Text`. | No añaden nada sobre el HTML nativo y estorban a **A-02** y a `react-router`. | No |
| D-13.6 | **Favicon diferido a `Task/014`.** | Crear un icono ahora. | `index.html` lo señalaba como decisión de `Task/013`; la decisión **se toma aquí, y es diferir**: un icono es identidad visual, y no corresponde inventar identidad que el producto no ha definido. `Task/014` construye la identidad del sitio público. | No |
| D-13.7 | **Demostración solo en desarrollo**, fuera del build. | Storybook; ruta pública permanente; solo pruebas. | Storybook es una dependencia grande para cinco primitivas. Una ruta pública contaminaría el sitemap de `Task/016`. Sin ninguna superficie, una tarea **visual** no sería validable por el usuario. | No |
| D-13.8 | **Contraste verificado por prueba propia**, no por dependencia. | Librería de contraste; verificación manual. | La fórmula WCAG es pequeña y estable; una prueba que lee los tokens reales impide que un cambio de color rompa **A-05** en silencio. | No |
| D-13.9 | **Sin tokens de elevación ni `z-index`.** | Escala de sombras y de capas. | Ningún consumidor en `Task/013`; **M-06**. | No |

## 13. Documentación creada o actualizada

| Documento | Qué cambió |
| --- | --- |
| `docs/tasks/TASK-013-design-system.md` | Ficha completa, con la matriz previa a la implementación. |
| `docs/task-reports/TASK-013-report.md` | Reporte de cierre pre-approval. |
| `docs/project-management/STATUS.md` | ETAPA 04 en curso; `Task/013` Lista para validación; sección de la tarea; avance **sin cambios**. |
| `docs/project-management/ROADMAP.md` | Fila de `Task/013` y fecha de actualización. |
| `docs/stages/STAGE-04-user-experience.md` | Etapa en curso; detalle de `Task/013`. |
| `docs/architecture/open-decisions.md` | **D-03** como **Propuesta — pendiente de aprobación**. |
| `docs/architecture/software-architecture.md` | §4.4 y §7: se retira «todavía no se selecciona una biblioteca visual». |
| `personal-blog-frontend/README.md` | Sección del sistema de diseño, estructura y tareas previstas. |

## 14. Archivos modificados

Detalle completo en el reporte, sección 19. Resumen: **25 archivos creados** y **3
modificados** en el frontend (`global.css`, `routes.tsx`, `README.md`); **2 creados** y
**5 modificados** en infra. **Sin cambios** en `package.json`, `package-lock.json`,
`index.html`, la configuración de build y lint, ni `src/services/`.

## 15. Resultado de pruebas

| Prueba | Comando | Resultado |
| --- | --- | --- |
| Formato | `npm run format:check` | ✔ limpio |
| Lint | `npm run lint` | ✔ sin errores |
| Tipos | `npm run typecheck` | ✔ sin errores |
| Suite | `npm run test:run` | ✔ **161 / 161** en 15 archivos |
| Cobertura | `npm run test:coverage` | ✔ 100 % líneas · 98.01 % ramas |
| Build | `npm run build` | ✔ sin *warnings* |
| Ausencia en `dist/` | `grep -ril "design-system" dist/` | ✔ sin resultados |

Nada falló al cerrar. Los fallos observados **durante** la ejecución —RED de cada
primitiva, cuatro bordes por debajo de 3:1, `?raw` vacío bajo `css: false`— están
registrados en el reporte, secciones 6, 11 y 20.

## 16. Problemas encontrados

Siete, con su resolución, en el reporte sección 20. Los dos de fondo:

1. `color-scheme: light dark` heredado habría roto **A-05** con una paleta de un solo
   tema. Corregido a `light`.
2. Una captura a 390 px aparentaba desbordamiento horizontal. Al medir `scrollWidth`
   resultó ser un artefacto del ancho mínimo de ventana de Chrome, no un defecto.

## 17. Pasos de validación para el usuario

En el reporte, sección 22. Incluye las compuertas de calidad, la comprobación de que la
demostración no viaja a producción y las cuatro comprobaciones visuales en el navegador
—foco con teclado, ausencia de desbordamiento, badges en escala de grises y regresión de
`/` y la 404—.

## 18. Deuda técnica pendiente

Siete elementos, en el reporte sección 21. Todos con tarea propietaria: variantes y
tamaños de `Button` y primitivas de formulario (`Task/015`), `VisuallyHidden` e
`IconButton` (`Task/014`–`015`), favicon (`Task/014`), validación visual integral
(`Task/014`–`015`) y auditoría formal (`Task/016`).

## 19. Próxima tarea

`Task/014-Sitio-Publico` — Inicio, Quién soy, Artículos, Reviews de libros, Videos,
Proyectos, Contacto y página 404, construidos sobre este sistema de diseño.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-04** |
| **Aprobado por** | **jeffersondavila** (el usuario) |
| **Expresión de aprobación** | `approved: Task/013-Sistema-de-Diseno` |

La aprobación autorizó el flujo de cierre de
[`WORKFLOW.md`](../project-management/WORKFLOW.md) §3: promoción de **D-03** a
**Resuelta** y **Vigente**, actualización del gobierno, commits, integración en `dev` y
pull request `Task/013-Sistema-de-Diseno → main` en los dos repositorios participantes.
**La fusión del pull request es decisión exclusiva del usuario.**
