# ETAPA 05 — Calidad y Seguridad

| Campo | Valor |
| --- | --- |
| **Número** | 05 |
| **Estado** | **Completada** el 2026-09-08: `Task/016`, `Task/017` y `Task/018` **Aprobadas**, con las limitaciones declaradas en los criterios de salida |
| **Dependencias** | [ETAPA 04](STAGE-04-user-experience.md) — **Completada** ✔ (2026-09-05) |
| **Tareas** | 3 |
| **Aprobadas** | 3 de 3 |
| **Avance** | 100 % |
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

### `Task/017-Observabilidad-Local` — **Aprobada** ✔ (2026-09-06)

Logs en JSON, correlation ID por petición, healthchecks, auditoría y diagnóstico a
través de Portainer.

Entrega `X-Request-ID` de extremo a extremo —respuesta, logs y `audit_events`—, `GET /ready`
con sonda real de PostgreSQL y almacenamiento bajo **presupuesto total** por debajo del
`timeout` del proxy, redacción automática de secretos en el log —cierra el plano local de
**R-36**— y `healthCheck` de Traefik en `/ready` conservando `/health` como liveness de
Docker. **1808** pruebas de backend en verde, **0 dependencias nuevas**.

**Alcance declarado:** cubre **O-01**, **O-02**, **O-04**, **O-07** y **O-08** en el plano
local, verifica **O-03** y aporta el correlation ID a **O-05**. **No** cubre **O-06**,
**O-09** ni **O-10**, que son observabilidad cloud y del VPS. Detalle en la
[ficha](../tasks/TASK-017-local-observability.md) y el
[reporte](../task-reports/TASK-017-report.md).

> **Alcance exclusivamente local** (aclarado en `Task/005.5`). `Task/017` **no es
> propietaria del monitoreo del VPS de producción**: ese *baseline* lo construye
> `Task/029` y lo valida `Task/040`. `Task/031` cubre **solo** AWS. Ningún documento
> vigente debe apuntar el monitoreo del VPS a esta tarea.

**Depende de:** `Task/014`, `Task/015`.
**Repositorios:** `personal-blog-backend`, `personal-blog-infra`.

### `Task/018-Endurecimiento-de-Seguridad` — **Aprobada** (2026-09-08)

Revisión de dependencias, imágenes Docker, manejo de secretos, CORS, cabeceras de
seguridad, validación de archivos subidos y refuerzo de autenticación.

**Depende de:** `Task/016`, `Task/017`.
**Repositorios:** los tres.

Entregado y verificado en ejecución: dos planos de identidad en PostgreSQL y MinIO
(**S-01**), política de cabeceras por superficie comprobada por HTTP real (**S-05**),
`X-Robots-Tag` que cierra **E-06** sin depender de JavaScript, CORS explícito sin
comodín (**S-04**), errores opacos y redacción con señuelos (**S-07**, **S-08**),
límite de cuerpo y verificación de integridad en las subidas (**S-11**), y contenedores
con capacidades retiradas y raíz en solo lectura.

**No cierra** **R-09** (socket de Docker de Portainer) ni **R-12** (respaldos locales sin
cifrar): ambos siguen abiertos con su propietario. Detalle y recuento de hallazgos
aceptados en el [reporte](../task-reports/TASK-018-report.md).

> **Aprobada** mediante `approved: Task/018-Endurecimiento-de-Seguridad` el
> 2026-09-08. La etapa completa **3 de 3** tareas. Los criterios parciales de
> rendering y vulnerabilidades de imágenes conservan su estado y propietario.

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
- [x] Los logs son JSON y llevan correlation ID rastreable extremo a extremo. —
      Cerrado por `Task/017`, **Aprobada** el 2026-09-06. *(La casilla se quedó sin
      marcar entonces; se corrige en `Task/018`.)*
- [x] Los healthchecks reflejan el estado real de las dependencias. — `GET /ready`
      con sonda real de PostgreSQL y almacenamiento (`Task/017`, **Aprobada**).
      *(Casilla corregida en `Task/018`.)*
- [~] Sin vulnerabilidades críticas ni altas conocidas en dependencias. — **Cumplido
      en dependencias de aplicación**: `npm audit` y `pip-audit` en **0** el 2026-09-07.
      **No cumplido en imágenes base**, donde quedan hallazgos sin parche aguas arriba y
      uno diferido con motivo. El criterio **no se marca**: la garantía duradera es el
      escaneo en CI, que es **S-09** y corresponde a `Task/019`–`Task/021`.
- [x] CORS restringido a orígenes conocidos. — Lista explícita; `*` con credenciales
      no arranca; lista vacía no concede lectura ni permite escrituras de navegador.
      Comprobado por HTTP real y con preflight.
- [x] Cabeceras de seguridad presentes en las respuestas. — Matriz por superficie,
      comprobada por HTTP real contra el entorno levantado, **incluidas las respuestas
      de error y los `500` no controlados**.
- [x] Subida de archivos validada por tipo y tamaño. — Decodificación real desde
      `Task/010`, más verificación de integridad del contenedor de imagen y cota del
      cuerpo antes de parsear el *multipart*.
- [x] Ningún secreto en el repositorio ni en los logs. — Escáner de secretos sobre
      los archivos versionables: **0** hallazgos. Redacción del log comprobada con
      señuelos en mensaje, contexto y cadena de excepciones.

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
