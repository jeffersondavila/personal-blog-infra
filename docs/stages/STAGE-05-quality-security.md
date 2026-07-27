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

**Depende de:** `Task/014`, `Task/015`.
**Repositorios:** `personal-blog-frontend`, `personal-blog-backend`.

### `Task/017-Observabilidad-Local` — *Pendiente*

Logs en JSON, correlation ID por petición, healthchecks, auditoría y diagnóstico a
través de Portainer.

**Depende de:** `Task/014`, `Task/015`.
**Repositorios:** `personal-blog-backend`, `personal-blog-infra`.

### `Task/018-Endurecimiento-de-Seguridad` — *Pendiente*

Revisión de dependencias, imágenes Docker, manejo de secretos, CORS, cabeceras de
seguridad, validación de archivos subidos y refuerzo de autenticación.

**Depende de:** `Task/016`, `Task/017`.
**Repositorios:** los tres.

## Criterios de salida de la etapa

- [ ] Cada página pública tiene título, descripción y Open Graph propios.
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
- Observabilidad cloud con CloudWatch (Etapa 10).
- Protección de costos (Etapa 12).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Cabeceras de seguridad que rompen el frontend. | Ajuste incremental con validación en cada cambio. |
| Actualización de dependencias con cambios incompatibles. | Actualizar por lotes pequeños con pruebas entre lotes. |
| Logs que registran datos sensibles. | Lista explícita de campos a redactar. |

## Siguiente etapa

[ETAPA 06 — Integración Continua](STAGE-06-continuous-integration.md)
