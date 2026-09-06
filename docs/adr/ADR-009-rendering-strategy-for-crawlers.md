# ADR-009 — Estrategia de *rendering* del sitio público frente a *crawlers*

| Campo | Valor |
| --- | --- |
| **Estado** | **Propuesta — pendiente de aprobación** |
| **Fecha** | 2026-09-06 |
| **Abierto por** | `Task/016-SEO-Accesibilidad-y-Rendimiento` |
| **Decisión asociada** | **D-21** — [`open-decisions.md`](../architecture/open-decisions.md) |
| **Reemplaza a** | Ninguno. **[ADR-005](ADR-005-markdown-content.md) sigue Aceptado.** |
| **Se resuelve en** | **Sin tarea asignada.** Requiere una decisión del usuario |

> **Nota sobre el número.** `Task/011` menciona «crear ADR-009» como la alternativa que
> **descartó** —su decisión D-011-R fue *«sin ADR»*—, así que ese identificador nunca se
> usó y estaba libre. Se comprobó antes de reservarlo: no existía el archivo ni ninguna
> otra referencia. Aquella mención se refiere a un asunto distinto —la autenticación
> administrativa— y no guarda relación con este documento. El historial de `Task/011` **no
> se reescribe**.

> **Este ADR no decide nada.** Abre formalmente una reconsideración con la
> evidencia que la justifica, tal y como
> [`STAGE-05`](../stages/STAGE-05-quality-security.md) exige a `Task/016`:
> *«registrar la limitación y **abrir** la reconsideración de la estrategia de
> rendering —prerender, SSG o SSR— como decisión nueva con su ADR»*, y
> *«esa reconsideración **no se resuelve aquí**»*.
>
> Ninguna de las opciones de §5 está elegida. Elegir una es un acto posterior,
> con su propia tarea y su propia aprobación.

---

## 1. Contexto

El sitio público es una **SPA de React servida como estático** ([ADR-003](ADR-003-serverless-low-cost-cloud.md),
[ADR-005](ADR-005-markdown-content.md)). Los metadatos SEO se inyectan **en el
cliente**, después de hidratar.

`Task/005.5` anticipó el riesgo y lo dejó por escrito en `STAGE-05`:

> *«Una SPA de React con metadatos inyectados en el cliente **no demuestra por sí
> sola** que el SEO funcione ni que las vistas previas sociales se rendericen:
> muchos *crawlers* de redes sociales **no ejecutan JavaScript**.»*

`Task/016` tenía la obligación de **comprobarlo**, no de suponerlo.

---

## 2. Evidencia medida

Medido el **2026-09-05** (antes de implementar) y el **2026-09-06** (después),
sobre el entorno local completo, en cuatro canales distintos.

### 2.1 Antes de implementar

| Canal | Resultado |
| --- | --- |
| Petición HTTP directa, 16 URL incluidas rutas profundas | Las 16 devuelven **HTTP 200 y el mismo cuerpo de 785 bytes** |
| *Crawler* sin JavaScript | `title` genérico `Blog personal` en todas. `description`, `canonical`, `og:*`, `meta robots`, JSON-LD: **0** |
| *User-agent* de *crawler* (`Googlebot`, `facebookexternalhit`, `Twitterbot`) | Respuesta **idéntica**; el servidor no diferencia |
| Navegador real con JavaScript, 11 rutas | `title` correcto por URL; el resto: **0** |

### 2.2 Después de implementar los metadatos

| Canal | Resultado |
| --- | --- |
| Navegador real con JavaScript, 11 rutas | `title`, `description`, `canonical`, `og:*` y JSON-LD **correctos y propios por URL** |
| `robots.txt` y `sitemap.xml` | **Corregidos**: `text/plain` y `application/xml`. Antes devolvían el `index.html` de la SPA |
| Open Graph **de sitio** en `index.html` | Visible **sin** JavaScript: `og:site_name`, `og:image`, `og:image:*`, `twitter:card` |
| Open Graph **por URL** sin JavaScript | **Sigue siendo 0.** `og:title`, `og:description`, `og:url` y `og:type` solo existen tras hidratar |

**La segunda medición es la que importa:** el problema no era falta de código.
Con el código escrito y verificado, el canal sin JavaScript sigue sin recibir
metadatos **propios de la URL solicitada**.

### 2.3 Por qué esto afecta a E-03 en particular

El propósito de **E-03** no es genérico. `MVP_SCOPE.md` §2.2 lo enuncia así:

> *«Compartir páginas mediante **metadatos Open Graph**.»*

Los consumidores de Open Graph son exactamente los agentes que **no** ejecutan
JavaScript: `facebookexternalhit`, `Twitterbot`, LinkedIn, WhatsApp, Slack. Un
`og:title` que solo existe después de hidratar no lo lee ninguno de ellos.

> **Conclusión, y es una conclusión sobre evidencia, no una preferencia de
> *stack*: la inyección de Open Graph en cliente no puede satisfacer E-03 por
> URL.**

---

## 3. Qué queda cubierto y qué no

| Requisito | Con JavaScript | Sin JavaScript | Estado en `Task/016` |
| --- | :---: | :---: | --- |
| **E-02** `title` + `description` | ✔ propios por URL | ✘ genérico | **Parcial** |
| **E-03** Open Graph | ✔ completo por URL | **Parcial**: solo lo de sitio | **NO cerrado** |
| **E-04** `canonical` | ✔ | ✘ | **Parcial** |
| **E-05** `sitemap.xml` | ✔ | ✔ | **Cerrado** — lo sirve el backend |
| **E-06** `robots.txt` + `noindex` | ✔ | Parcial: `robots.txt` sí, `noindex` no | **Parcial** — la garantía HTTP es `Task/018` |
| **E-07** JSON-LD | ✔ | ✘ | **Parcial** |

**Matiz importante y a favor de no precipitarse:** Googlebot **sí** renderiza
JavaScript, así que para la **indexación en buscadores** el estado actual es
razonable. Lo que queda demostradamente sin cubrir son las **vistas previas
sociales por URL**.

---

## 4. Decisión

**Ninguna todavía.** `Task/016` abre la reconsideración y la deja documentada.

Lo que sí queda fijado:

1. **ADR-005 sigue Aceptado.** El Markdown se sigue renderizando en cliente.
2. **El *stack* no cambia.** Vite y React siguen vigentes.
3. **E-03 no se declara cerrado**, y `STAGE-05` no puede marcar ese criterio de
   salida sin resolver esta decisión.
4. La reconsideración **no se resuelve en `Task/016`**: `STAGE-05` lo excluye
   expresamente del alcance de la etapa.

---

## 5. Opciones a evaluar cuando esta decisión se aborde

Se enumeran para que la decisión futura parta de un marco, **no** para elegir
ahora. Ninguna está evaluada con costos reales todavía.

### 5.1 Mantener *client-only* (situación actual)

- **A favor:** cero cambios; Googlebot renderiza JavaScript; el *build* sigue
  siendo estático estándar (**T-05**) y no depende de ningún servicio.
- **En contra:** **E-03 por URL queda incumplido** de forma permanente. Las
  vistas previas sociales muestran siempre lo mismo, sea cual sea el contenido
  compartido.
- **Coste:** ninguno.

### 5.2 Prerender de las rutas conocidas

- **A favor:** genera HTML real por ruta sin cambiar el modelo de ejecución; el
  *hosting* sigue siendo estático.
- **En contra:** las rutas de **detalle** dependen de contenido, así que el
  prerender debería ejecutarse **al publicar**, no solo al construir. Hoy nada
  dispara un *build* cuando se publica un artículo.
- **Abre:** cómo se dispara la regeneración, y quién es su propietario.

### 5.3 SSG (generación estática en el *build*)

- **A favor:** HTML completo y rápido; excelente para *crawlers*.
- **En contra:** el mismo problema de frescura que 5.2, agravado: el contenido
  publicado después del *build* no existe hasta el siguiente. **Compromete T-05**:
  el *build* pasaría a depender del API.
- **Abre:** *webhooks* de reconstrucción y su costo.

### 5.4 SSR

- **A favor:** resuelve el problema por completo y sin latencia de publicación.
- **En contra:** contradice frontalmente la arquitectura vigente. Cloudflare
  Pages sirve estáticos (`Task/034`), y **ADR-003** eligió un modelo de bajo
  costo sin servidor de aplicación para el frontend. Añade un plano de ejecución
  nuevo que operar.
- **Abre:** revisión de **ADR-003** y del modelo de costos (`Task/041`).

### 5.5 Servicio de *prerendering* para *user-agents* de *crawler*

- **A favor:** no toca la aplicación.
- **En contra:** introduce un tercero, un costo recurrente y una superficie que
  hay que mantener; además, servir contenido distinto por *user-agent* exige
  cuidado para no incurrir en *cloaking*.

---

## 6. Información necesaria antes de decidir

1. **Si el usuario quiere vistas previas sociales por URL.** Es una decisión de
   producto: sin ese requisito, 5.1 es aceptable y esta decisión se cierra sin
   cambiar nada.
2. **Volumen y ritmo de publicación reales.** Con publicaciones esporádicas, un
   prerender disparado al publicar es barato; con muchas, no.
3. **Costo** de cada opción sobre el presupuesto de `Task/027` y `Task/041`.
4. **Evidencia con contenido real**, que hoy no existe: la semilla es de
   `Task/022`.

---

## 7. Consecuencias de dejarla abierta

- **E-03 queda declarado NO cerrado**, con su motivo documentado, en lugar de
  darse por bueno.
- `STAGE-05` no puede marcar el criterio de salida *«Open Graph propios
  verificados con una herramienta de inspección real»* sin resolver esto.
- No se bloquea ninguna otra tarea: `Task/017` y `Task/018` no dependen de ella.

---

## 8. Relación con otras decisiones

| Decisión | Relación |
| --- | --- |
| [ADR-003](ADR-003-serverless-low-cost-cloud.md) | 5.4 exigiría revisarlo |
| [ADR-005](ADR-005-markdown-content.md) | **Sigue Aceptado.** Ya preveía esta reconsideración: *«si resulta insuficiente, se reconsidera con un ADR»* |
| **D-08** (`Task/030`) | Independiente. Afecta a **qué imagen** usa `og:image`, no a **si un *crawler* la ve** |
| **D-07** (`Task/035`) | Independiente: el dominio no cambia el canal de *rendering* |
| `Task/034` | El *hosting* condiciona 5.2 y 5.3, pero no decide esta cuestión |

---

## 9. Evidencia enlazada

- [Ficha de `Task/016`](../tasks/TASK-016-seo-accessibility-performance.md) §7 —
  criterio de reconsideración y las cuatro mediciones.
- [Reporte de `Task/016`](../task-reports/TASK-016-report.md) — medición
  posterior a la implementación, que es la que demuestra que el problema **no**
  era falta de código.
- [`STAGE-05`](../stages/STAGE-05-quality-security.md) — el criterio que obliga a
  abrir esta decisión.
