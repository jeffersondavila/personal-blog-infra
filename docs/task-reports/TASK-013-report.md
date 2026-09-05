# TASK-013 — Sistema de Diseño — Reporte

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/013-Sistema-de-Diseno` |
| **Etapa** | ETAPA 04 — Experiencia del Usuario |
| **Estado** | **Aprobada** ✔ (2026-09-04) |
| **Fecha** | 2026-09-03 · **aprobada** el 2026-09-04 |
| **Repositorios** | `personal-blog-frontend` (funcional) · `personal-blog-infra` (documentación) |
| **Ficha** | [`TASK-013-design-system.md`](../tasks/TASK-013-design-system.md) |
| **SHA base frontend** | `fd62f221707591a984cf0fb51a03ea339380ab35` |
| **SHA base infra** | `1b6f0c4776311009fde37461608b18c94419cc9f` |

---

## 1. Qué se entregó

La base visual y de componentes que `Task/014` y `Task/015` consumirán:

- **50 tokens** semánticos en CSS Custom Properties.
- **Fundación global** con una **estrategia única de foco visible**.
- **Cinco primitivas**: `Container`, `Stack`, `Button`, `Card`, `Badge`.
- **Accesibilidad base**: **A-05**, **A-06** y **A-07** asumidas; **A-01** iniciada.
- **Guardas ejecutables** que impiden que el sistema se degrade en silencio.
- **Cero dependencias nuevas.**

---

## 2. Preflight Git

| Repositorio | `main` | `main == origin/main` | Árbol limpio | `main` ancestro de `dev` | `dev..main` | `diff main dev` |
| --- | --- | :---: | :---: | :---: | :---: | :---: |
| frontend | `fd62f22` | ✔ | ✔ | ✔ | `0` | vacío |
| infra | `1b6f0c4` | ✔ | ✔ | ✔ | `0` | vacío |
| backend | `ce166fb` | ✔ | ✔ | ✔ | `0` | vacío |

## 3. Creación de ramas

| Repositorio | Rama | `HEAD == main` al crear | `main..HEAD` |
| --- | --- | :---: | :---: |
| frontend | `Task/013-Sistema-de-Diseno` | ✔ `fd62f22` == `fd62f22` | `0` |
| infra | `Task/013-Sistema-de-Diseno` | ✔ `1b6f0c4` == `1b6f0c4` | `0` |
| backend | *(sin rama)* | — | — |

**¿Alguna rama Task nació de `dev`?** **NO.** Ambas nacieron de `main` actualizado y
limpio.

---

## 4. Decisiones

| # | Decisión | Alternativas descartadas |
| --- | --- | --- |
| D-13.1 | **CSS Modules + CSS Custom Properties**, cero dependencias. **Propone resolver D-03.** | Tailwind, MUI, Chakra, Bootstrap, styled-components, Emotion, Sass, CSS global con prefijos. |
| D-13.2 | Sin `ThemeProvider`; tokens en `:root`. | Contexto de tema en React. |
| D-13.3 | Un solo tema claro; `color-scheme: light`. | Modo oscuro; mantener `light dark`. |
| D-13.4 | *System font stack*, sin webfonts. | Google Fonts, fuente autoalojada. |
| D-13.5 | Sin componentes `Link`, `Heading` ni `Text`: CSS global sobre elementos nativos. | Envoltorios de React. |
| D-13.6 | Favicon **diferido a `Task/014`**. | Inventar un icono ahora. |
| D-13.7 | Demostración **solo en desarrollo**. | Storybook; ruta pública permanente; solo pruebas. |
| D-13.8 | Contraste verificado con utilidad propia y probada. | Dependencia externa; revisión visual. |
| D-13.9 | Sin tokens de elevación ni `z-index`. | Escala de sombras y de capas. |

### 4.1 Un hallazgo que cambió el código existente

`global.css` declaraba `color-scheme: light dark`. Con una paleta de **un solo tema**,
esa declaración autoriza al navegador a pintar su lienzo oscuro bajo colores diseñados
para fondo claro, lo que **rompería A-05** — el requisito que esta tarea debe garantizar.

Se corrigió a `color-scheme: light`. **No es implementar modo oscuro**: es dejar de
prometer uno que no existe. Si algún día se decide el modo oscuro, será una tarea con su
propia paleta verificada.

---

## 5. Design tokens

**50 tokens.** Categorías creadas y, con igual importancia, las **descartadas**.

| Categoría | Nº | Ejemplos | Consumidores |
| --- | ---: | --- | --- |
| Color | 19 | `--color-text-primary`, `--color-interactive`, `--color-focus`, ternas de tono | Todo el sistema |
| Tipografía | 11 | `--font-family-sans`, `--font-size-2xl`, `--font-weight-medium` | `foundation.css`, `Button`, `Badge` |
| Espaciado | 7 | `--space-2xs` … `--space-2xl` | `Stack`, `Button`, `Card`, `Badge` |
| Layout | 3 | `--layout-width-prose`, `--layout-width-wide`, `--layout-gutter` | `Container` |
| Forma | 3 | `--radius-sm`, `--radius-md`, `--border-width` | `Button`, `Card`, `Badge` |
| Altura de línea | 2 | `--line-height-tight`, `--line-height-normal` | `foundation.css`, `Button`, `Badge` |
| Foco | 2 | `--focus-ring-width`, `--focus-ring-offset` | `foundation.css` |
| Breakpoints | 2 | `--breakpoint-md`, `--breakpoint-lg` | **Ninguno en `Task/013`** — ver 5.1 |
| Movimiento | 1 | `--transition-fast` | `foundation.css`, `Button` |

### Categorías descartadas

| Categoría | Por qué no |
| --- | --- |
| Elevación / sombras | El lenguaje visual es plano: la separación se resuelve con superficie y borde. Sin consumidor (**M-06**). |
| `z-index` | No hay ningún elemento superpuesto: sin modales, menús ni tooltips. |
| `letter-spacing` | No aporta valor demostrable a esta escala. |

### 5.1 Los dos tokens sin consumidor, declarados como tales

`--breakpoint-md` y `--breakpoint-lg` **no los usa ninguna primitiva de `Task/013`**, y
eso es deliberado: las primitivas son *intrínsecamente* responsive (`clamp`, `min()`,
`flex-wrap`) y no necesitan umbrales.

Existen como **contrato compartido**: sin ellos, `Task/014` y `Task/015` elegirían cada
una sus propios breakpoints — exactamente la divergencia que esta tarea existe para
evitar.

**Limitación real de la plataforma, documentada en el propio archivo:** una media query
no puede leer una custom property, así que quien los use debe repetir el literal y citar
el token como su origen.

---

## 6. Contraste — evidencia (**A-05**)

Los ratios **no son una afirmación de este reporte**: `src/styles/contrast.test.ts` lee
`tokens.css`, extrae los valores reales y calcula cada par. Si alguien cambia un color y
rompe AA, la suite falla y nombra el par.

**22 pares verificados, 22 cumplen.** Umbrales: 4.5:1 texto (WCAG 1.4.3), 3:1 elementos
no textuales que identifican un control (WCAG 1.4.11).

| Par | Ratio | Mínimo | |
| --- | ---: | ---: | :---: |
| texto principal / lienzo | 17.63 | 4.5 | ✔ |
| texto principal / superficie | 16.28 | 4.5 | ✔ |
| texto secundario / lienzo | 7.69 | 4.5 | ✔ |
| texto secundario / superficie | 7.10 | 4.5 | ✔ |
| interactivo / lienzo | 9.51 | 4.5 | ✔ |
| interactivo / superficie | 8.78 | 4.5 | ✔ |
| interactivo hover / lienzo | 12.47 | 4.5 | ✔ |
| texto sobre botón primario | 9.51 | 4.5 | ✔ |
| texto sobre botón primario en hover | 12.47 | 4.5 | ✔ |
| anillo de foco / lienzo | 6.09 | 3.0 | ✔ |
| anillo de foco / superficie | 5.62 | 3.0 | ✔ |
| borde de control / lienzo | 4.55 | 3.0 | ✔ |
| borde de control / superficie | 4.20 | 3.0 | ✔ |
| texto éxito / superficie éxito | 7.60 | 4.5 | ✔ |
| texto aviso / superficie aviso | 7.84 | 4.5 | ✔ |
| texto error / superficie error | 8.01 | 4.5 | ✔ |
| texto éxito / lienzo | 8.63 | 4.5 | ✔ |
| texto aviso / lienzo | 8.65 | 4.5 | ✔ |
| texto error / lienzo | 9.28 | 4.5 | ✔ |
| borde éxito / lienzo | 3.41 | 3.0 | ✔ |
| borde aviso / lienzo | 4.41 | 3.0 | ✔ |
| borde error / lienzo | 4.45 | 3.0 | ✔ |

Cuatro bordes fallaron el umbral de 3:1 en el primer cálculo y **se oscurecieron hasta
cumplirlo**, en lugar de rebajar el criterio o dejarlo para `Task/016`.

### Dos bordes con responsabilidades distintas

- `--color-border` es **decorativo** (1.42:1 contra el lienzo): contornea una tarjeta que
  ya se distingue por superficie y espaciado. WCAG 1.4.11 no le aplica.
- `--color-border-strong` **delimita un control** (4.55:1): es lo que hace reconocible un
  botón secundario, y por eso sí cumple 3:1.

Distinguirlos evita las dos formas de equivocarse: exigir 3:1 a una línea decorativa, o
dejar un control sin contorno perceptible.

### Alcance de la afirmación

> `Task/013` afirma que **los pares que define y verifica** cumplen WCAG 2.1 AA.
> **No** afirma que el producto cumpla AA. La auditoría formal es `Task/016`, cuando
> existan páginas reales.

---

## 7. Foco visible (**A-06**)

**Estrategia única y global**, declarada una sola vez en `foundation.css`:

```css
:focus-visible {
  outline: var(--focus-ring-width) solid var(--color-focus);
  outline-offset: var(--focus-ring-offset);
}
```

| Decisión | Por qué |
| --- | --- |
| Selector universal, no por componente | Todo elemento enfocable —los de hoy y los que añadan `Task/014` y `Task/015`— hereda el anillo sin hacer nada. Ningún componente puede olvidarse del foco. |
| `:focus-visible` y no `:focus` | Aparece con teclado y no molesta al hacer clic, que es la razón por la que la gente acaba escribiendo `outline: none`. |
| `outline-offset` | **No es decorativo.** Separa el anillo del control con una franja del fondo, y es lo que garantiza que se distinga también sobre el relleno azul del botón primario. |

**¿Se eliminó el `outline` en algún sitio sin reemplazo? NO.** Y no es una promesa: la
guarda `designSystem.guards.test.ts` recorre **todo** el CSS del sistema y falla si
aparece `outline: none` u `outline: 0`, o si un componente declara su propio
`:focus-visible`.

**Verificado visualmente**: el anillo con su separación es visible en la captura de la
sección 12.

---

## 8. Sin dependencia exclusiva del color (**A-07**)

`Badge` es donde esta garantía se construye, con **tres capas**:

1. **Texto obligatorio.** `children` es requerido por tipos: un badge sin texto no
   compila. Quien no distinga colores lee el significado igual.
2. **Silueta propia por tono.** No un icono cualquiera: formas exteriores distintas —
   **círculo** (éxito), **triángulo** (aviso), **octógono** (error)— que se distinguen en
   escala de grises y en blanco y negro. El glifo es `aria-hidden`: el texto ya lo dice.
3. **Color**, que llega el último y solo refuerza.

El tono `neutral` **no lleva glifo a propósito**: no señala ningún estado, así que no hay
nada que distinguir; un icono ahí sería ruido.

`Button` comunica `disabled` con tres señales: el **atributo nativo** —que impide foco y
activación y anuncian los lectores de pantalla—, el cursor y la opacidad. La primera es
la que importa.

Una prueba comprueba que **las tres siluetas son distintas entre sí**, no solo que
existen.

---

## 9. Inventario de componentes

Derivado de `USER_FLOWS`, `MVP_SCOPE` §2–§3 y `STAGE-04`.

| Componente | 014 | 015 | Variantes / estados | ¿Aquí? | Motivo |
| --- | :---: | :---: | --- | :---: | --- |
| `Container` | Sí | Sí | `prose`, `wide` | **Sí** | Ancho de lectura (A.3, A.5) y de listado. |
| `Stack` | Sí | Sí | 2 ejes, 7 gaps, 4 alineaciones, envoltura | **Sí** | Único mecanismo de separación. |
| `Button` | Sí | Sí | `primary`, `secondary`; `disabled`, `hover`, `focus-visible` | **Sí** | Reintento (A.1, A.2), paginación, acciones del panel. |
| `Card` | Sí | Sí | ninguna | **Sí** | Elemento de listado y tarjeta de dashboard. |
| `Badge` | Sí | Sí | 4 tonos | **Sí** | Etiquetas (A.2, A.9) y estados de contenido (§3.2). |
| `Link` | Sí | Sí | — | **No** | CSS global sobre `a`: un envoltorio pelearía con `react-router`. |
| `Heading`, `Text` | Sí | Sí | — | **No** | No añaden nada sobre `<h2>` y estorban a **A-02**. |
| `VisuallyHidden` | — | — | — | **No** | Sin consumidor: no hay control solo-icono. |
| `Divider`, `IconButton` | — | Quizá | — | **No** | Sin consumidor demostrado. |
| `Input`, `FormField`, `ValidationMessage` | — | Sí | — | **No** | **A-03** y **A-08** son de `Task/015`, que decide **D-04**. |

### Lo que deliberadamente no se construyó

`Button` tiene **dos** variantes y **un** tamaño. No hay variante `danger` ni tamaño
compacto porque **ningún consumidor actual las necesita**: las confirmaciones destructivas
(B.5, B.11) y las acciones de tabla son de `Task/015`. Los tokens de tono ya están
disponibles para entonces.

Añadir una variante después es barato; quitar una equivocada, no.

---

## 10. Responsive

**Principio: responsive intrínseco.** Las primitivas usan `clamp()`, `min()` y
`flex-wrap`, y **no contienen ni una media query de ancho** — comprobado por guarda.

| Pieza | Mecanismo |
| --- | --- |
| Gutter | `clamp(1rem, 0.5rem + 2.5vw, 2rem)`: crece de forma continua, sin saltos. |
| Contenedor | `width: 100%` + `max-width`. Nunca un ancho rígido: eso es lo que evita el desplazamiento horizontal. |
| Tipografía | Encabezados con `clamp()`; el cuerpo en `rem`, que respeta el tamaño base del usuario. |
| Agrupaciones | `flex-wrap`: una fila de etiquetas o de acciones se reparte sola. |

Un diseño así funciona en **cualquier** ancho, incluido uno que nadie previó, en lugar de
en los tres tamaños que alguien eligió.

### Qué NO puede validarse hasta `Task/014` y `Task/015`

El comportamiento de páginas reales: rejillas de listado, navegación móvil, layout del
panel y tablas en pantalla estrecha. `Task/013` entrega las piezas, no las composiciones.

---

## 11. Pruebas

**161 pruebas en verde, 15 archivos.** Baseline: 50 en 6 archivos. **111 nuevas**, y
**ninguna prueba existente se modificó**.

| Archivo | Nº | Qué demuestra |
| --- | ---: | --- |
| `lib/color/contrast.test.ts` | 8 | Fórmula WCAG: blanco/negro = 21, simetría, gamma, hex corto, entradas inválidas. |
| `styles/contrast.test.ts` | 23 | Los 22 pares reales de `tokens.css` cumplen su umbral. |
| `styles/designSystem.guards.test.ts` | 28 | Sin color literal, sin token inexistente, sin `outline` suprimido, sin media queries de ancho. |
| `components/Button/Button.test.tsx` | 14 | Semántica nativa, `type`, `disabled`, foco, nombre accesible, variantes, ARIA. |
| `components/Badge/Badge.test.tsx` | 17 | Señal no cromática, siluetas distintas, glifo `aria-hidden`, texto siempre presente. |
| `components/Stack/Stack.test.tsx` | 7 | Ejes, 7 gaps, 4 alineaciones, envoltura, props del consumidor. |
| `components/Container/Container.test.tsx` | 5 | Anchos, elemento genérico, props del consumidor. |
| `components/Card/Card.test.tsx` | 4 | Superficie sin rol implícito. |
| `pages/DesignSystemPage.test.tsx` | 6 | Se construye solo con la superficie pública; la ruta no desplaza al comodín 404. |

### Ciclo seguido

Se trabajó comportamiento por comportamiento: **prueba primero, RED demostrado,
implementación, GREEN**.

| Paso | Evidencia observada |
| --- | --- |
| RED de la utilidad de contraste | `Failed to resolve import "./contrast"` |
| GREEN | 8 pruebas en verde |
| RED de `Button` | `Failed to resolve import "./Button"` |
| GREEN | 14 pruebas en verde |
| RED de las otras cuatro primitivas | 4 archivos fallan por import no resuelto |
| GREEN | 46 pruebas de componentes en verde |

### Las guardas se comprobaron *falsando* el sistema

Una guarda que no puede fallar no vale nada. Se inyectó temporalmente en `Card.module.css`
una regla con las tres violaciones y se confirmó que **las tres se detectan**:

```
× 'Card/Card.module.css' no contiene ningun color literal
× 'Card/Card.module.css' solo usa tokens declarados
× 'Card/Card.module.css' no suprime el outline
```

El archivo se restauró inmediatamente.

### Qué NO prueba JSDOM, y se dice

- Que un color «se vea bien»: JSDOM no pinta.
- Que el anillo de foco se note: no se aplican hojas de estilo.
- *Layout* real, `clamp()` y media queries: no hay motor de cajas.
- Activación por teclado: en JSDOM, pulsar Enter sobre un `<button>` **no** dispara
  `click`. Una prueba así comprobaría el motor de pruebas, no el componente. La garantía
  real es **estructural** —el elemento es un `<button>` nativo, no un `div` con
  `onClick`— y eso sí se comprueba.

Esas lagunas se cubren con la inspección del CSS, las guardas y la validación visual.

---

## 12. Validación visual

**Sí se hizo**, con Chrome ya instalado en la máquina y **sin añadir ninguna
dependencia** — ni Playwright ni Storybook.

| Ancho | Método | Resultado |
| --- | --- | --- |
| 320 px | Chrome headless sobre iframe de ancho fijo | Sin desbordamiento. Los nombres de token largos parten en dos líneas; el `h1` envuelve limpio. |
| 390 px | Ídem | Sin desbordamiento. Tarjetas en una columna. |
| 485 px | Chrome headless directo | `scrollWidth == clientWidth` |
| 737 px | Chrome headless directo | `scrollWidth == clientWidth` |
| 1409 px | Chrome headless directo | `scrollWidth == clientWidth`. Rejilla de tres columnas. |

**Medición de desbordamiento (R-01):** se instrumentó temporalmente la página para
comparar `scrollWidth` con `clientWidth` y listar todo elemento que sobresaliera del
viewport. **Cero elementos desbordados** en los tres anchos medidos. La instrumentación se
retiró y `index.html` quedó **idéntico** al de `main`.

**Comprobado también en el navegador:**

- El **anillo de foco** con su separación, sobre el botón primario relleno.
- Las **cuatro siluetas** de `Badge` visiblemente distintas.
- Los botones deshabilitados, atenuados.
- La jerarquía tipográfica y el enlace subrayado dentro de un párrafo.

### Un falso positivo que conviene registrar

La primera captura a 390 px parecía mostrar texto cortado. **No era un defecto de
layout**: Chrome impone en esta máquina un ancho mínimo de ventana de ~485 px, de modo
que la captura era un **recorte de 390 px de un render de 485 px**. Se detectó al medir
`clientWidth` en lugar de fiarse de la imagen, y se resolvió renderizando dentro de un
iframe de ancho exacto.

### Limitación honesta

Lo validado son **las primitivas**, no el producto. La validación visual integral —
páginas reales, navegación, tablas, panel — solo es posible cuando `Task/014` y
`Task/015` existan.

---

## 12.1 Consola — gate de la Definition of Done

> *«Sin errores de consola en las rutas afectadas»*
> ([`DEFINITION_OF_DONE`](../project-management/DEFINITION_OF_DONE.md), tareas de
> frontend).

Comprobado con Chrome ya instalado, **sin dependencias nuevas**. La instrumentación se
instaló en `<head>`, **antes** de que montara la aplicación, e interceptó `console.error`,
el evento `error` de `window` —en fase de captura, para incluir fallos de recurso— y
`unhandledrejection`.

| Modo | Ruta | `console.error` | `window.error` | `unhandledrejection` | Recursos | Resultado |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| desarrollo | `/` | 0 | 0 | 0 | 0 | Pantalla de fundación |
| desarrollo | `/__design-system` | 0 | 0 | 0 | 0 | Sistema de diseño |
| desarrollo | `/ruta-que-no-existe` | 0 | 0 | 0 | 0 | Página 404 |
| preview de producción | `/` | 0 | 0 | 0 | 0 | Pantalla de fundación |
| preview de producción | `/__design-system` | 0 | 0 | 0 | 0 | **Página 404** |

**`/__design-system` responde con la página 404 en producción.** Es la confirmación de
comportamiento —no solo de ausencia de cadenas en `dist/`— de que la ruta de desarrollo
no existe en el artefacto publicable.

### El camino de error sí se ejercitó

El backend está **deliberadamente apagado** (esta tarea no toca Docker). Aun así, `/`
registró **cero** errores: la consulta a `/health` falla, `HomePage` la captura y muestra
«Backend sin respuesta». La ruta que hace E/S de red recorrió su rama de fallo **sin
ensuciar la consola y sin promesas sin capturar**.

### Un hallazgo del gate, ajeno a `Task/013`

El primer intento en preview dio **1 `window.error`** y la aplicación no montó:

```
Uncaught ConfigurationError: Falta la variable de entorno VITE_API_BASE_URL.
```

**No es un defecto de `Task/013`.** Vite incrusta las variables `VITE_*` en tiempo de
**build**, y ese `dist/` se había construido sin ninguna. Es exactamente el
comportamiento *fail-closed* que `Task/006` definió para **T-01**: sin configuración
válida la aplicación **no arranca**, y dice qué variable falta, en lugar de apuntar en
silencio a un origen equivocado.

Se reconstruyó pasando la variable —como haría un despliegue real— y las cinco rutas
quedaron en cero. **No se modificó código productivo.**

> **Nota para `Task/034`** (despliegue en Cloudflare Pages): el build de producción
> **exige** `VITE_API_BASE_URL` definida en el entorno de construcción. Un artefacto
> construido sin ella no monta.

### Instrumentación

Temporal y retirada. `index.html` quedó **idéntico al de `main`**:
`git diff -- index.html` y `git diff main -- index.html` **vacíos**, y ninguna
coincidencia de la instrumentación en el árbol de trabajo ni en `dist/`.

---

## 13. Superficie de demostración y su ausencia en producción

`/__design-system` existe **solo en desarrollo**. `import.meta.env.DEV` es una constante
en tiempo de build, así que en producción el arreglo de rutas queda vacío y el
componente desaparece por *tree shaking*.

**No es una ruta oculta: no existe.** Comprobado sobre el build real:

| Cadena buscada en `dist/` | Resultado |
| --- | --- |
| `__design-system` | **ausente** |
| `DesignSystemPage` | **ausente** |
| `swatchGrid` | **ausente** |
| `octogono` | **ausente** |
| `Encabezado de nivel` | **ausente** |

Importa más allá del peso: una ruta de producto no prevista contaminaría el sitemap y el
`robots.txt` de `Task/016`.

En cambio, **el sistema sí viaja**: `--color-text-primary:#16191d` y la regla
`:focus-visible` están presentes en el CSS de producción.

---

## 14. Superficie pública

```ts
import { Badge, Button, Card, Container, Stack } from '../components';
```

`src/components/index.ts` exporta los cinco componentes y sus tipos. **Un solo nivel de
reexportación, sin ciclos.** La página de demostración se construye **solo** con esta
superficie, igual que harán `Task/014` y `Task/015`: si algo no se pudiera montar así,
el defecto estaría en el contrato.

Los CSS Modules refuerzan la frontera por su cuenta: sus nombres de clase se generan en
el build, de modo que **ninguna página puede depender de una clase interna**.

Los tokens no se exportan desde JavaScript: viven en `tokens.css`, los carga `global.css`
una vez y se consumen como `var(--…)`. No hace falta un objeto de tokens en JS.

### Ubicación, según la arquitectura vigente

El sistema **no** vive en `src/design-system/`, sino en `src/components/` y
`src/styles/`, que es lo que `software-architecture.md` §4.1–§4.2 define: *«`components`:
UI compartida sin conocimiento del dominio»* y *«`styles`: tokens de diseño y estilos
globales»*. Se siguió la arquitectura versionada.

---

## 15. Dependencias

| Comprobación | Resultado |
| --- | --- |
| Dependencias runtime nuevas | **0** |
| Dependencias de desarrollo nuevas | **0** |
| `package.json` | **sin cambios** (`git diff` vacío contra `main`) |
| `package-lock.json` | **sin cambios** (`git diff` vacío contra `main`) |
| `npm ls --depth=0` | Árbol idéntico al de `main` |

Todo lo necesario es plataforma —CSS Modules de Vite, `clamp`, custom properties, SVG
inline— o ya estaba en el stack. `@types/node` **ya era** una dependencia de desarrollo;
solo se referenció desde dos archivos de prueba.

---

## 16. Compuertas de calidad

| Compuerta | Comando | Resultado |
| --- | --- | --- |
| Formato | `npm run format:check` | ✔ *All matched files use Prettier code style* |
| Lint | `npm run lint` | ✔ sin errores ni *warnings* |
| Tipos | `npm run typecheck` | ✔ sin errores |
| Pruebas | `npm run test:run` | ✔ **161 / 161** en 15 archivos |
| Cobertura | `npm run test:coverage` | ✔ ver 16.1 |
| Build | `npm run build` | ✔ en 365 ms, **sin *warnings*** |
| Dependencias | `npm ls --depth=0` | ✔ árbol sin cambios |
| Consola | Chrome headless, 5 rutas | ✔ **0** errores — ver 12.1 |
| Enlaces relativos | Resolución de los 7 documentos | ✔ **232** comprobados, **0** rotos |
| Whitespace | `git diff --check` en los 3 repos | ✔ sin hallazgos, exit 0 |

### 16.1 Cobertura

```
Statements   : 100%    (140/140)
Branches     : 98.01%  (99/101)
Functions    : 100%    (43/43)
Lines        : 100%    (139/139)
```

Dos ramas sin cubrir, ambas explicables:

| Ubicación | Motivo |
| --- | --- |
| `app/routes.tsx:39` | **Nueva.** Es la rama de producción de `import.meta.env.DEV`, que Vitest **no puede** ejecutar porque siempre corre en modo desarrollo. Es justamente la rama cuyo comportamiento se verificó **inspeccionando `dist/`** (sección 13). |
| `services/http/httpError.ts:113` | **Preexistente**, heredada de `Task/007`. Este archivo **no se tocó**. |

No se añadió ninguna prueba artificial para subir el porcentaje.

### 16.2 Build

```
dist/index.html                   0.76 kB │ gzip:  0.46 kB
dist/assets/index-OB61GfPJ.css    2.95 kB │ gzip:  1.15 kB
dist/assets/index-D9cD6B9y.js   285.76 kB │ gzip: 91.09 kB
```

**El sistema de diseño completo son 2.95 kB de CSS (1.15 kB comprimido).** El JavaScript
lo domina React y React Router; no se añadió ninguna biblioteca.

No se midió el delta exacto contra `main`: habría exigido `git stash` —desaconsejado por
las instrucciones del proyecto— o una segunda instalación completa. Lo que sí es un hecho
verificable es que **el manifiesto de dependencias no cambió**.

---

## 17. Regresión

| Comprobación | Resultado |
| --- | --- |
| `App` renderiza | ✔ suite existente, sin modificar |
| Router resuelve `/` | ✔ |
| Página 404 en ruta desconocida | ✔ el comodín `*` sigue siendo la última ruta, comprobado por prueba |
| Cliente HTTP | ✔ **`git diff` vacío** sobre `src/services/http/` |
| `index.html` | ✔ intacto |
| Configuración de build y lint | ✔ `vite.config.ts`, `tsconfig*.json`, `eslint.config.js` **sin cambios** |
| 50 pruebas previas | ✔ en verde, **ninguna modificada** |

---

## 18. Backend, Docker y host

| Recurso | ¿Modificado? |
| --- | --- |
| `personal-blog-backend` | **NO** — `main` limpio, sin rama, solo lectura |
| Docker / `docker compose` | **NO** |
| PostgreSQL | **NO** |
| MinIO | **NO** |
| Terraform / AWS / Floci | **NO** |
| WSL / WinNAT | **NO** |

Se ejecutó un servidor de desarrollo de Vite **temporal** en `localhost` para la
validación visual, y se detuvo al terminar. No creó ni modificó ningún recurso.

---

## 19. Archivos

### `personal-blog-frontend`

| Archivo | Acción |
| --- | --- |
| `src/styles/tokens.css` | creado |
| `src/styles/foundation.css` | creado |
| `src/styles/global.css` | **modificado** — pasa a componer las dos capas |
| `src/styles/contrast.test.ts` | creado |
| `src/styles/designSystem.guards.test.ts` | creado |
| `src/lib/color/contrast.ts` | creado |
| `src/lib/color/contrast.test.ts` | creado |
| `src/components/index.ts` | creado |
| `src/components/Button/` (`.tsx`, `.module.css`, `.test.tsx`) | creado |
| `src/components/Container/` (3 archivos) | creado |
| `src/components/Stack/` (3 archivos) | creado |
| `src/components/Card/` (3 archivos) | creado |
| `src/components/Badge/` (3 archivos) | creado |
| `src/pages/DesignSystemPage.tsx` | creado |
| `src/pages/DesignSystemPage.module.css` | creado |
| `src/pages/DesignSystemPage.test.tsx` | creado |
| `src/app/routes.tsx` | **modificado** — ruta condicional de desarrollo |
| `README.md` | **modificado** — sección del sistema de diseño |

**No modificados:** `package.json`, `package-lock.json`, `index.html`, `vite.config.ts`,
`tsconfig*.json`, `eslint.config.js`, `src/services/**`, `src/app/App.tsx`,
`src/pages/HomePage.tsx`, `src/pages/NotFoundPage.tsx`.

### `personal-blog-infra`

| Archivo | Acción |
| --- | --- |
| `docs/tasks/TASK-013-design-system.md` | creado |
| `docs/task-reports/TASK-013-report.md` | creado |
| `docs/project-management/STATUS.md` | modificado |
| `docs/project-management/ROADMAP.md` | modificado |
| `docs/stages/STAGE-04-user-experience.md` | modificado |
| `docs/architecture/open-decisions.md` | modificado — **D-03** como propuesta |
| `docs/architecture/software-architecture.md` | modificado — §4.4 y §7 |

---

## 20. Problemas encontrados

| # | Problema | Resolución |
| --- | --- | --- |
| 1 | `color-scheme: light dark` heredado rompería **A-05** con una paleta de un solo tema. | Corregido a `light`, con la razón registrada. |
| 2 | Cuatro bordes no alcanzaban 3:1 (WCAG 1.4.11). | Se oscurecieron hasta cumplir. No se rebajó el criterio. |
| 3 | `import.meta.url` no tiene esquema `file:` bajo Vitest. | Se lee la ruta desde la raíz del proyecto. |
| 4 | `?raw` de Vite devuelve vacío: la suite corre con `css: false`. | Lectura del archivo con `node:fs`. |
| 5 | Los tipos de Node no estaban en `tsconfig.app.json`, y añadirlos los pondría al alcance del código de navegador. | `/// <reference types="node" />` **acotada a los dos archivos de prueba** que lo necesitan. Sin tocar la configuración compartida. |
| 6 | La captura a 390 px parecía mostrar desbordamiento. | Era un artefacto: Chrome impone ~485 px de ancho mínimo. Se midió `scrollWidth` y se renderizó en un iframe de ancho exacto. **No había desbordamiento.** |
| 7 | `noPropertyAccessFromIndexSignature` obliga a `styles['x']`. | Comprobado **antes** de elegir CSS Modules; se asume el coste, documentado. |

---

## 21. Deuda técnica pendiente

| # | Deuda | Tarea |
| --- | --- | --- |
| 1 | Variantes `danger` y silenciosa de `Button`, y tamaños alternativos. | `Task/015` |
| 2 | Primitivas de formulario con **A-03** y **A-08**. | `Task/015` |
| 3 | `VisuallyHidden`, `IconButton`, `Divider`: con su primer consumidor real. | `Task/014`, `Task/015` |
| 4 | Icono real del sitio (favicon). | `Task/014` |
| 5 | Validación visual integral con páginas reales. | `Task/014`, `Task/015` |
| 6 | Auditoría formal de accesibilidad y umbrales de rendimiento. | `Task/016` |
| 7 | Los breakpoints obligan a repetir el literal en cada media query (limitación de CSS). | Ninguna: documentado en `tokens.css`. |

---

## 22. Pasos de validación para el usuario

```bash
cd C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-frontend

# 1. Compuertas de calidad.
npm run format:check
npm run lint
npm run typecheck
npm run test:run          # 161 en verde
npm run test:coverage
npm run build             # sin warnings

# 2. Las dependencias y el cliente HTTP no cambiaron (salida vacia).
git diff --stat main -- package.json package-lock.json src/services/http

# 3. La superficie de demostracion NO esta en produccion (sin resultados).
grep -ril "design-system" dist/
```

**Ver el sistema en el navegador.** La ruta es de desarrollo, así que hace falta el
servidor de Vite. Si aún no existe `.env.local`, créalo desde el ejemplo — la aplicación
valida su configuración al arrancar y sin ella no monta:

```bash
copy .env.example .env.local
npm run dev
```

Y abrir **`http://localhost:5173/__design-system`**. Merece la pena comprobar:

1. **Tabular con el teclado** hasta los botones: el anillo de foco aparece con su
   separación, y el botón deshabilitado **se salta**.
2. **Estrechar la ventana** hasta el ancho de un móvil: nada se desborda en horizontal y
   el margen lateral se ajusta de forma continua.
3. **Poner la pantalla en escala de grises** (o imprimir en blanco y negro): los cuatro
   badges siguen siendo distinguibles por su forma y su texto.
4. Comprobar que **`/` y una ruta inexistente** siguen funcionando como antes.

Para confirmar que la demostración no viaja a producción: `npm run build && npm run
preview`, y abrir `/__design-system` — debe responder la **página 404**.

---

## 23. Criterion 12 — estado duradero frente a transitorio

Búsqueda dirigida en los documentos tocados
([`WORKFLOW`](../project-management/WORKFLOW.md) §6.1):

| Clase | Nº | Ejemplos |
| --- | ---: | --- |
| **A — historia fechada** | varias | «`Task/012` — Aprobada el 2026-09-03»; «cuatro bordes se oscurecieron hasta cumplir». |
| **B — regla permanente** | varias | «toda rama Task nace de `main`»; «`Lista para validación` no suma avance»; «D-03 no es vigente hasta la aprobación». |
| **C — estado vivo de Git o GitHub** | **0** | — |

**C = 0.** Ningún documento afirma que exista un PR, que una rama remota esté publicada,
que algo esté pendiente de fusionar ni que haya una normalización en curso.

`Task/013 — Lista para validación` **es estado duradero** y se registra como tal.

---

## 24. Estado de Git al cerrar

| Repositorio | Rama | *Staging* | Commits sobre `main` | Push | Merge | PR |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| frontend | `Task/013-Sistema-de-Diseno` | **0** | **0** | **0** | **0** | **0** |
| infra | `Task/013-Sistema-de-Diseno` | **0** | **0** | **0** | **0** | **0** |
| backend | `main` — limpio, 0 cambios | **0** | **0** | **0** | **0** | **0** |

Los cambios están **sin commit**, como corresponde a una tarea no aprobada
([`PROJECT_INSTRUCTIONS`](../claude/PROJECT_INSTRUCTIONS.md) §6).

---

## 25. Gobierno

| Campo | Valor |
| --- | --- |
| **`Task/013`** | **Aprobada** ✔ (2026-09-04) |
| **Avance global** | **13 de 41 — 32 %** |
| **ETAPA 04** | **En curso** — **1 de 3** aprobadas — **33 %** |
| **`Task/014`** | Pendiente |
| **`Task/015`** | Pendiente |
| **D-03** | **Resuelta** y **Vigente** (2026-09-04) |

---

## 26. Veredicto

| Criterio | |
| --- | :---: |
| ¿La rama nació de `main`? | **SÍ** |
| ¿Alcance derivado de las fuentes canónicas? | **SÍ** |
| ¿Matriz previa a la implementación? | **SÍ** |
| ¿Tokens coherentes y semánticos? | **SÍ** |
| ¿Tipografía definida? | **SÍ** |
| ¿Responsive base sin hacks por dispositivo? | **SÍ** |
| ¿Contraste válido y evidenciado? | **SÍ** — 22 pares verificados por prueba |
| ¿Foco visible sistemático? | **SÍ** |
| ¿Sin dependencia exclusiva del color? | **SÍ** |
| ¿Teclado correcto en las primitivas? | **SÍ** — solo elementos nativos |
| ¿Componentes mínimos y reutilizables? | **SÍ** |
| ¿`Task/014` no adelantada? | **SÍ** |
| ¿`Task/015` no adelantada? | **SÍ** |
| ¿Sin modo oscuro especulativo? | **SÍ** |
| ¿Sin framework de UI innecesario? | **SÍ** |
| ¿Dependencias nuevas = 0? | **SÍ** |
| ¿`package-lock.json` sin cambios? | **SÍ** |
| ¿Cliente HTTP intacto? | **SÍ** |
| ¿Backend intacto? | **SÍ** |
| ¿Docker, PostgreSQL y MinIO intactos? | **SÍ** |
| ¿Pruebas en verde? | **SÍ** — 161/161 |
| ¿Lint, typecheck y formato limpios? | **SÍ** |
| ¿Cobertura conforme? | **SÍ** — 100 % líneas |
| ¿Build en verde? | **SÍ** — sin *warnings* |
| ¿Criterion 12 con C = 0? | **SÍ** |
| ¿0 commits, push, merge y PR? | **SÍ** |
| **¿`Task/013` Lista para validación?** | **SÍ** |

---

## 27. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-04** |
| **Aprobado por** | **jeffersondavila** (el usuario) |
| **Expresión de aprobación** | `approved: Task/013-Sistema-de-Diseno` |

Recibida la aprobación se ejecutó el cierre de
[`WORKFLOW.md`](../project-management/WORKFLOW.md) §3: **D-03** promovida a **Resuelta** y
**Vigente**, gobierno actualizado, commits creados, rama integrada en `dev` mediante
merge `--no-ff` y pull request `Task/013-Sistema-de-Diseno → main` en `personal-blog-frontend`
y `personal-blog-infra`.

**La revisión y la fusión del pull request son responsabilidad exclusiva del usuario.**
`Task/014-Sitio-Publico` no se inicia hasta que `main` y `dev` queden normalizadas.
