# ETAPA 04 — Experiencia del Usuario

| Campo | Valor |
| --- | --- |
| **Número** | 04 |
| **Estado** | **En curso** — abierta el 2026-09-03 con `Task/013`, **aprobada** el 2026-09-04 |
| **Dependencias** | [ETAPA 03](STAGE-03-domain-and-backend.md) — **Completada** ✔ (2026-09-03) |
| **Tareas** | 3 |
| **Aprobadas** | **1** de 3 |
| **Avance** | **33 %** |
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

### `Task/014-Sitio-Publico` — *Pendiente*

Inicio, Quién soy, Artículos, Reviews de libros, Videos, Proyectos y laboratorio,
Contacto y enlaces, y página 404.

**Depende de:** `Task/013`.

### `Task/015-Panel-Administrativo` — *Pendiente*

Dashboard, editor Markdown, gestión de contenido, carga de imágenes y vista previa.

**Depende de:** `Task/013`.

**Repositorio de toda la etapa:** `personal-blog-frontend`.

## Criterios de salida de la etapa

- [ ] Todas las secciones previstas del blog son navegables.
- [ ] El sitio se ve correctamente en móvil, tableta y escritorio.
- [ ] El administrador puede crear, editar, publicar y archivar contenido desde el panel.
- [ ] Se pueden subir imágenes y verlas en el contenido publicado.
- [ ] Existe vista previa antes de publicar.
- [ ] El panel administrativo es inaccesible sin sesión válida.
- [ ] La página 404 funciona en rutas inexistentes.

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
