# ETAPA 04 — Experiencia del Usuario

| Campo | Valor |
| --- | --- |
| **Número** | 04 |
| **Estado** | **Completada** el 2026-09-05, con la aprobación de `Task/015-Panel-Administrativo` |
| **Dependencias** | [ETAPA 03](STAGE-03-domain-and-backend.md) — **Completada** ✔ (2026-09-03) |
| **Tareas** | 3 |
| **Aprobadas** | **3** de 3 |
| **Avance** | **100 %** |
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

### `Task/015-Panel-Administrativo` — **Aprobada** (2026-09-05)

Acceso y sesión administrativa, dashboard básico, listados y formularios de los cuatro tipos
publicables, editor Markdown con vista previa, carga y selección de imágenes, etiquetas,
perfil y transiciones de publicación: **18 superficies** sobre las primitivas de `Task/013` y
los **27 patrones de ruta / 39 operaciones HTTP** que `Task/011`, `Task/012` y `Task/012.1`
dejaron cerrados.

**Resuelve D-04** —editor Markdown— con `<textarea>` nativo más el componente
`MarkdownContent` de `Task/014`, es decir **el mismo pipeline de sanitización** que el sitio
público (ADR-005, **S-03**) y **cero dependencias nuevas**. Asume **A-03** (labels asociadas),
**A-08** (errores anunciados de forma accesible) y **P-05** (el código del panel no se
descarga en las páginas públicas); continúa **A-01** y **A-02**, y preserva **A-04** a
**A-07**.

**Dashboard mínimo completo, sin bloqueos.** Al reconstruir el alcance del panel se
descubrió que `MVP_SCOPE.md` §3.3 exige *«últimos eventos de auditoría»* y que ninguna
operación HTTP los exponía —bloqueo **B-015-1**—. Lo resolvió
`Task/012.1-Exponer-Auditoria-Para-Dashboard`, mantenimiento fuera de las 41 **aprobado el
2026-09-05**, que añadió `GET /api/v1/admin/audit-events` al contrato del que `Task/012` es
dueña. **`Task/015` no se amplió a backend**: esta ficha declara `personal-blog-frontend`
repositorio de toda la etapa, y esa declaración se respetó.

Las tres piezas del dashboard mínimo son ya construibles dentro de `Task/015`: conteo por
tipo y estado y últimos elementos modificados desde los listados administrativos, y los
últimos eventos de auditoría desde la nueva operación de solo lectura.

Definida, reconciliada e implementada el 2026-09-05: **600 pruebas** en verde —440
heredadas más 160 nuevas (43 añadidas al corregir auth)—, **cero dependencias nuevas** y el gate **P-05** verificado sobre
el artefacto real con una mutación que lo pone rojo. El usuario la aprobó el 2026-09-05
mediante `approved: Task/015-Panel-Administrativo`. **D-015-A** a **D-015-H**,
**D-015-J** y **D-015-K** quedan **Vigentes**; **D-015-I** continúa **retirada**.
La etapa queda **Completada: 3 de 3 — 100 %**.

La aprobación conserva la limitación visual: no se observaron en navegador los anchos
320, 390, 768 y 1280 del panel; el recorrido con administrador y contenido reales sigue
ligado a la semilla local de `Task/022`. La evidencia funcional procede de la suite.

**Depende de:** `Task/013` — **Aprobada** ✔ · `Task/014` — **Aprobada** ✔.
**Ficha:** [`TASK-015-admin-panel.md`](../tasks/TASK-015-admin-panel.md) ·
**Reporte:** [`TASK-015-report.md`](../task-reports/TASK-015-report.md)

**Repositorio de toda la etapa:** `personal-blog-frontend`.

## Criterios de salida de la etapa

- [x] Todas las secciones previstas del blog son navegables. — `Task/014` (2026-09-05).
- [x] El sitio se ve correctamente en móvil, tableta y escritorio. — `Task/014`: medido a
      320, 390, 768 y 1280 px sin desbordamiento horizontal. *Con contenido publicado se
      revalida cuando exista semilla local (`Task/022`).*
- [x] El administrador puede crear, editar, publicar y archivar contenido desde el panel.
      — `Task/015`, aprobado y probado mediante el router real.
- [x] Se pueden subir imágenes y verlas en el contenido publicado. — Carga y asociación
      probadas en `Task/015`; render público por `access_url` entregado por `Task/014`.
      El recorrido con contenido real conserva la limitación de `Task/022`.
- [x] Existe vista previa antes de publicar. — `Task/015` reutiliza el pipeline
      `MarkdownContent` de `Task/014`, con sanitización probada.
- [x] El panel administrativo es inaccesible sin sesión válida. — Guardas de `Task/015`
      verificadas por pruebas de sesión y rutas.
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
