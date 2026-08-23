# ETAPA 05 — Calidad y Seguridad

| Campo | Valor |
| --- | --- |
| **Número** | 05 |
| **Estado** | Pendiente |
| **Dependencias** | [ETAPA 04](STAGE-04-user-experience.md) |
| **Tareas** | 3 |
| **Aprobadas** | 0 |
| **Avance** | 0 % |
| **Hito que completa** | Producto con calidad y seguridad verificables. |

---

## Objetivo

Elevar el blog a estándar publicable: descubrible por buscadores, accesible, rápido,
observable y endurecido frente a los riesgos habituales de una aplicación web pública.

## Por qué esta etapa existe

Un blog personal es una cara pública. SEO, accesibilidad y seguridad son mucho más
baratos de aplicar aquí, antes de exponer el sitio en internet, que después.

## Tareas

### `Task/016-SEO-Accesibilidad-y-Rendimiento` — *Pendiente*

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

**Depende de:** `Task/014`, `Task/015`.
**Repositorios:** `personal-blog-frontend`, `personal-blog-backend`.

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

- [ ] Cada página pública tiene título, descripción, `canonical` y Open Graph propios,
      **verificados por URL directa y con una herramienta de inspección real**, no
      asumidos por estar el código escrito.
- [ ] `og:image` usa una **URL estable**, nunca una URL prefirmada que expira.
- [ ] `sitemap.xml` y `robots.txt` se generan correctamente.
- [ ] Navegación por teclado y contraste verificados en las páginas principales.
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
