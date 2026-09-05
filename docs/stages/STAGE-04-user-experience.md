# ETAPA 04 — Experiencia del Usuario

| Campo | Valor |
| --- | --- |
| **Número** | 04 |
| **Estado** | **En curso** — abierta el 2026-09-03 con `Task/013`; `Task/014` **aprobada** el 2026-09-05 |
| **Dependencias** | [ETAPA 03](STAGE-03-domain-and-backend.md) — **Completada** ✔ (2026-09-03) |
| **Tareas** | 3 |
| **Aprobadas** | **2** de 3 |
| **Avance** | **67 %** |
| **Hito que completa** | Blog usable de extremo a extremo en local. |

---

## Objetivo

Construir el sistema de diseño, el sitio público y el panel administrativo, de modo que
el blog pueda usarse completamente en local: publicar contenido y verlo publicado.

## Por qué esta etapa existe

Es donde el proyecto se vuelve un producto real y no solo un API. El sistema de diseño
va primero para evitar inconsistencia visual y reescrituras de componentes.

## Tareas

### `Task/013-Sistema-de-Diseno` — **Aprobada** ✔ (2026-09-04)

Tokens de diseño semánticos, fundación global con estrategia única de foco, tipografía,
comportamiento responsive intrínseco y accesibilidad base.

Entrega cinco primitivas compartidas —`Container`, `Stack`, `Button`, `Card`, `Badge`—
y asume **A-05** (contraste), **A-06** (foco visible) y **A-07** (sin dependencia
exclusiva del color), además de iniciar **A-01** (teclado).

**Resuelve D-03** —biblioteca de componentes visuales— con CSS Modules más CSS Custom
Properties y **cero dependencias nuevas**, en lugar de adoptar una biblioteca de
terceros.

**Depende de:** `Task/012`.
**Ficha:** [`TASK-013-design-system.md`](../tasks/TASK-013-design-system.md) ·
**Reporte:** [`TASK-013-report.md`](../task-reports/TASK-013-report.md)

### `Task/014-Sitio-Publico` — **Aprobada** ✔ (2026-09-05)

Inicio, Quién soy, Artículos, Reviews de libros, Videos, Proyectos y laboratorio,
Contacto y enlaces, búsqueda básica, filtro por etiqueta y página 404, sobre las cinco
primitivas de `Task/013` y los diez recursos públicos de la API.

Confirma las rutas propuestas en `MVP_SCOPE` §2.1 —incluido el detalle de proyecto—, asume
**A-02** (HTML semántico) y **A-04** (texto alternativo en el render), continúa **A-01**, y
cierra la **lista de proveedores de video** que `CONTENT_MODEL` §3.4 le asigna. El Markdown
se renderiza **sanitizado** en el frontend (ADR-005) con `react-markdown` y
`rehype-sanitize`, las dos únicas dependencias nuevas. Definida el 2026-09-04, implementada
y **aprobada** el 2026-09-05: **440 pruebas** en verde y validación en Chrome a cuatro
anchos.

Hace verdaderos, para el sitio público, los criterios de salida «todas las secciones
previstas son navegables», «se ve correctamente en móvil, tableta y escritorio» y «la
página 404 funciona en rutas inexistentes»; la comprobación con contenido publicado en el
navegador real queda pendiente de la semilla local (`Task/022`).

**Depende de:** `Task/013` — **Aprobada** ✔.
**Ficha:** [`TASK-014-public-site.md`](../tasks/TASK-014-public-site.md) ·
**Reporte:** [`TASK-014-report.md`](../task-reports/TASK-014-report.md)

### `Task/015-Panel-Administrativo` — *Pendiente*

Dashboard, editor Markdown, gestión de contenido, carga de imágenes y vista previa.

**Depende de:** `Task/013`.

**Repositorio de toda la etapa:** `personal-blog-frontend`.

## Criterios de salida de la etapa

- [x] Todas las secciones previstas del blog son navegables. — `Task/014` (2026-09-05).
- [x] El sitio se ve correctamente en móvil, tableta y escritorio. — `Task/014`: medido a
      320, 390, 768 y 1280 px sin desbordamiento horizontal. *Con contenido publicado se
      revalida cuando exista semilla local (`Task/022`).*
- [ ] El administrador puede crear, editar, publicar y archivar contenido desde el panel.
- [ ] Se pueden subir imágenes y verlas en el contenido publicado. — El **render** público
      de imágenes por `access_url` está entregado por `Task/014`; falta la carga desde el
      panel (`Task/015`).
- [ ] Existe vista previa antes de publicar. — `Task/015` reutilizará el pipeline
      `MarkdownContent` de `Task/014`.
- [ ] El panel administrativo es inaccesible sin sesión válida.
- [x] La página 404 funciona en rutas inexistentes. — `Task/014`. El **código HTTP** `404`
      real de la SPA es de `Task/016` y `Task/034`.

## Fuera del alcance de la etapa

- Metadatos SEO y Open Graph (Etapa 05).
- Auditoría de accesibilidad formal (Etapa 05).
- Optimización de rendimiento (Etapa 05).
- Despliegue (Etapa 10).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Alcance visual creciente sin límite. | El MVP definido en `Task/002` acota las secciones y sus componentes. |
| Editor Markdown como vector de inyección. | Sanitización del render; se revisa en `Task/018`. |
| Inconsistencia visual entre sitio público y panel. | Ambos consumen el mismo sistema de diseño de `Task/013`. |

## Siguiente etapa

[ETAPA 05 — Calidad y Seguridad](STAGE-05-quality-security.md)
