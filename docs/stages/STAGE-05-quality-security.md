# ETAPA 05 — Calidad y Seguridad

| Campo | Valor |
| --- | --- |
| **Número** | 05 |
| **Estado** | **En curso** — `Task/016` **Aprobada** el 2026-09-06 |
| **Dependencias** | [ETAPA 04](STAGE-04-user-experience.md) — **Completada** ✔ (2026-09-05) |
| **Tareas** | 3 |
| **Aprobadas** | 1 de 3 |
| **Avance** | 33 % |
| **Hito que completa** | Producto con calidad y seguridad verificables. |

---

## Objetivo

Elevar el blog a estándar publicable: descubrible por buscadores, accesible, rápido,
observable y endurecido frente a los riesgos habituales de una aplicación web pública.

## Por qué esta etapa existe

Un blog personal es una cara pública. SEO, accesibilidad y seguridad son mucho más
baratos de aplicar aquí, antes de exponer el sitio en internet, que después.

## Tareas

### `Task/016-SEO-Accesibilidad-y-Rendimiento` — **Aprobada** ✔ (2026-09-06)

Metadatos, Open Graph, sitemap, `robots.txt`, optimización de carga y accesibilidad.

#### SEO de una SPA: verificación, no suposición

> Precisión añadida en `Task/005.5`. **Una SPA de React con metadatos inyectados en el
> cliente no demuestra por sí sola** que el SEO funcione ni que las vistas previas sociales
> se rendericen: muchos *crawlers* de redes sociales **no ejecutan JavaScript**. Tampoco es
> motivo para cambiar el *stack* ahora: [ADR-005](../adr/ADR-005-markdown-content.md) y la
> elección de Vite siguen vigentes y **no se replantean sin evidencia**.

`Task/016` debe convertirse en una **validación comprobable**, con evidencia registrada:

| # | Qué se comprueba |
| --- | --- |
| 1 | `title` y `description` **propios y correctos por URL**, no heredados de la ruta inicial |
| 2 | `canonical` correcto en cada página pública |
| 3 | **Open Graph** completo, incluido `og:image` con **URL estable y no expirable** |
| 4 | **Acceso directo por URL profunda** —no navegando desde la portada— devuelve la página correcta |
| 5 | Lo que **recibe un *crawler***, comprobado con una herramienta real de inspección o de vista previa social |
| 6 | `sitemap.xml` y `robots.txt` generados y accesibles |

**Criterio de reconsideración.** Si esas comprobaciones **no** se satisfacen con
*rendering* en cliente, `Task/016` debe **registrar la limitación y abrir la
reconsideración de la estrategia de *rendering*** —prerender, SSG o SSR— como decisión
nueva con su ADR. **Esa reconsideración no se resuelve aquí**: `Task/005.5` no cambia el
*stack*, solo exige que la tarea sepa reconocer el fallo en lugar de darlo por bueno.

**Depende de:** `Task/014`, `Task/015` — ambas **Aprobadas** ✔ (2026-09-05).
**Repositorios:** `personal-blog-frontend`, `personal-blog-backend`, `personal-blog-infra`
(documentación + ***wiring* local mínimo**: tres líneas autorizadas en el Compose y en
Traefik, ninguna de ellas Nginx, CORS ni cabeceras).
**Ficha:** [TASK-016-seo-accessibility-performance.md](../tasks/TASK-016-seo-accessibility-performance.md)

#### Resultado de la verificación exigida — medido el 2026-09-05 y el 2026-09-06

El *baseline* se midió en los cuatro canales **antes** de escribir código, que es exactamente lo que esta sección exige. Resultado:

| Canal | Qué recibe |
| --- | --- |
| Navegador con JavaScript | `title` **propio y correcto por URL** (11/11) y `h1` único. `description`, `canonical`, `og:*` y JSON-LD: **0** |
| Petición HTTP directa a URL profunda | **HTTP 200** y el mismo cuerpo de **785 bytes** en las 16 URL medidas |
| *Crawler* sin JavaScript | `title` genérico `Blog personal`; **0** metadatos de SEO |
| *User-agent* de *crawler* (`Googlebot`, `facebookexternalhit`, `Twitterbot`) | Respuesta **idéntica**: el servidor no diferencia |

**El criterio de reconsideración enunciado más arriba queda cumplido**, y por una razón estructural, no por falta de código: el propósito canónico de **E-03** es compartir en redes (`MVP_SCOPE.md` §2.2) y esos *crawlers* no ejecutan JavaScript. `Task/016` debe **abrir** la reconsideración con un ADR en estado **Propuesta** y **no** declarar **E-03** cerrado. **ADR-005 sigue Aceptado.**

También se midieron **dos defectos**, no simples ausencias: `GET /robots.txt` y `GET /sitemap.xml` respondían **HTTP 200 con el `index.html` de la SPA**. Ambos quedaron **corregidos** en la implementación: `text/plain` y `application/xml` respectivamente.

#### Qué demostró volver a medir DESPUÉS de implementar

Es la parte que cierra la exigencia de `Task/005.5`. Con los metadatos escritos y verificados en navegador real:

| Canal | Resultado |
| --- | --- |
| Navegador con JavaScript, 11 rutas | `title`, `description`, `canonical`, `og:*` y JSON-LD **correctos y propios por URL** |
| *Crawler* **sin** JavaScript | **Sigue recibiendo cero** metadatos propios de la URL |

**El problema no era falta de código.** Por eso `Task/016` abre **D-21** con
[ADR-009](../adr/ADR-009-rendering-strategy-for-crawlers.md) en estado **Propuesta**,
**no elige** ninguna estrategia y **no cierra E-03**.

Lo que sí se ganó sin JavaScript: el Open Graph **de sitio** —`og:site_name`, `og:image`
con sus dimensiones, y `twitter:card`— vive ahora en `index.html`, y es información
**correcta para cualquier URL**.

### `Task/017-Observabilidad-Local` — *Pendiente*

Logs en JSON, correlation ID por petición, healthchecks, auditoría y diagnóstico a
través de Portainer.

> **Alcance exclusivamente local** (aclarado en `Task/005.5`). `Task/017` **no es
> propietaria del monitoreo del VPS de producción**: ese *baseline* lo construye
> `Task/029` y lo valida `Task/040`. `Task/031` cubre **solo** AWS. Ningún documento
> vigente debe apuntar el monitoreo del VPS a esta tarea.

**Depende de:** `Task/014`, `Task/015`.
**Repositorios:** `personal-blog-backend`, `personal-blog-infra`.

### `Task/018-Endurecimiento-de-Seguridad` — *Pendiente*

Revisión de dependencias, imágenes Docker, manejo de secretos, CORS, cabeceras de
seguridad, validación de archivos subidos y refuerzo de autenticación.

**Depende de:** `Task/016`, `Task/017`.
**Repositorios:** los tres.

## Criterios de salida de la etapa

- [~] Cada página pública tiene título, descripción, `canonical` y Open Graph propios,
      **verificados por URL directa y con una herramienta de inspección real**, no
      asumidos por estar el código escrito. — **Verificado con JavaScript** en las 11
      superficies. **Sin JavaScript no se cumple**, y ese es el motivo de **D-21**: el
      criterio **no puede marcarse** hasta resolverla.
- [x] `og:image` usa una **URL estable**, nunca una URL prefirmada que expira. — Activo
      estático del sitio (**D-016-A**). El `og:image` **por contenido** sigue bloqueado
      por **D-08**.
- [x] `sitemap.xml` y `robots.txt` se generan correctamente. — `application/xml` y
      `text/plain`; el sitemap deriva del contenido publicado y **E-08** está fijado por
      prueba contra PostgreSQL real.
- [x] Navegación por teclado y contraste verificados en las páginas principales. —
      **139 paradas** de teclado en 10 superficies, **0** sin foco visible y **0** trampas.
      Contraste heredado de `Task/013`, sin hallazgos nuevos.
- [ ] Los logs son JSON y llevan correlation ID rastreable extremo a extremo.
- [ ] Los healthchecks reflejan el estado real de las dependencias.
- [ ] Sin vulnerabilidades críticas ni altas conocidas en dependencias.
- [ ] CORS restringido a orígenes conocidos.
- [ ] Cabeceras de seguridad presentes en las respuestas.
- [ ] Subida de archivos validada por tipo y tamaño.
- [ ] Ningún secreto en el repositorio ni en los logs.

## Fuera del alcance de la etapa

- Automatización de estas verificaciones en CI (Etapa 06).
- Observabilidad cloud con CloudWatch (Etapa 10) y con **Grafana Cloud** (`Task/029`,
  `Task/031`). **`Task/017` es local y no observa el VPS de producción.**
- **Monitoreo del VPS de producción** (`Task/029`, validado en `Task/040`).
- **Cambiar la estrategia de *rendering*** del frontend: `Task/016` solo puede **abrir** la
  reconsideración con evidencia; resolverla exige un ADR propio.
- Protección de costos (Etapa 12).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Cabeceras de seguridad que rompen el frontend. | Ajuste incremental con validación en cada cambio. |
| Actualización de dependencias con cambios incompatibles. | Actualizar por lotes pequeños con pruebas entre lotes. |
| Logs que registran datos sensibles. | Lista explícita de campos a redactar. |

## Siguiente etapa

[ETAPA 06 — Integración Continua](STAGE-06-continuous-integration.md)
