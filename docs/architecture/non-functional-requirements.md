# Requisitos no funcionales

| Campo | Valor |
| --- | --- |
| **Estado** | Propuesta de `Task/002-Definir-MVP-y-Arquitectura` — Lista para validación |
| **Fecha** | 2026-07-26 |

Criterios mínimos que toda implementación posterior debe respetar. Se verifican
principalmente en las Etapas 05 (`Task/016`–`Task/018`), 07 (`Task/022`) y 12
(`Task/040`).

**Total: 57 requisitos** en 7 categorías.

| Categoría | Nº | Prefijo |
| --- | ---: | --- |
| Seguridad | 12 | `S-` |
| Rendimiento | 8 | `P-` |
| Accesibilidad | 8 | `A-` |
| SEO | 8 | `E-` |
| Observabilidad | 8 | `O-` |
| Portabilidad | 7 | `T-` |
| Mantenibilidad | 6 | `M-` |
| **Total** | **57** | |

Relacionados: [security-boundaries.md](security-boundaries.md) ·
[software-architecture.md](software-architecture.md) ·
[DEFINITION_OF_DONE.md](../project-management/DEFINITION_OF_DONE.md)

---

## 1. Seguridad

| # | Requisito | Se verifica en |
| --- | --- | --- |
| S-01 | **Principio de mínimo privilegio** en usuarios de base de datos, roles IAM, permisos de bucket y tokens de CI. | `Task/018`, `Task/028`, `Task/030` |
| S-02 | **Validación de entrada** en todos los endpoints: tipo, longitud, rango y formato. Lo no válido se rechaza con `422`. | `Task/009`, `Task/012` |
| S-03 | **Sanitización de contenido**: el Markdown se sanitiza antes de renderizarse, también en la vista previa. | `Task/014`, `Task/015`, `Task/018` |
| S-04 | **CORS por ambiente**: orígenes permitidos explícitos. Nunca `*` en producción. | `Task/018`, `Task/033` |
| S-05 | **Headers de seguridad** en las respuestas del sitio y del API. | `Task/018` |
| S-06 | **Protección de rutas administrativas**: todo `/api/v1/admin/*` exige autenticación salvo `login`. | `Task/011`, `Task/012` |
| S-07 | **No exponer trazas internas**: ningún error devuelve trazas, SQL, rutas ni nombres de clase. | `Task/009`, `Task/018` |
| S-08 | **No registrar contraseñas, tokens ni secretos** en logs, auditoría ni mensajes de error. | `Task/017`, `Task/018` |
| S-09 | **Dependencias auditables**: versiones fijadas y escaneo de vulnerabilidades en CI. | `Task/019`–`Task/021` |
| S-10 | **Secretos fuera de Git**: `.env` ignorado, SSM en producción, `.env.example` con valores ficticios. | Todas |
| S-11 | **Validación de archivos subidos**: tipo MIME y tamaño comprobados en el servidor. | `Task/010`, `Task/018` |
| S-12 | **Enlaces externos seguros**: `rel="noopener noreferrer"` en todo enlace a terceros. | `Task/014` |

---

## 2. Rendimiento

| # | Requisito | Se verifica en |
| --- | --- | --- |
| P-01 | **Carga inicial razonable** en las páginas públicas, medida en una conexión típica. | `Task/016` |
| P-02 | **Paginación obligatoria**: ningún endpoint devuelve colecciones sin acotar. | `Task/009` |
| P-03 | **Lazy loading de imágenes** fuera del área visible inicial. | `Task/016` |
| P-04 | **Imágenes optimizadas**: formatos y dimensiones adecuados; miniaturas para listados. | `Task/010`, `Task/016` |
| P-05 | **Sin descargar contenido administrativo en páginas públicas**: el código del panel se carga solo en el panel. | `Task/015`, `Task/016` |
| P-06 | **Backend stateless**: sin estado en memoria entre peticiones. | `Task/005`, `Task/023` |
| P-07 | **Compatible con cold starts de Lambda**: artefacto ligero y arranque acotado. | `Task/024`, `Task/032` |
| P-08 | **Consultas acotadas**: los listados usan índices y evitan consultas N+1. | `Task/008`, `Task/009` |

Los umbrales numéricos concretos se fijan en `Task/016`, cuando exista contenido real que
medir.

---

## 3. Accesibilidad

Objetivo de referencia: **WCAG 2.1 nivel AA**.

| # | Requisito | Se verifica en |
| --- | --- | --- |
| A-01 | **Navegación con teclado** completa en sitio público y panel. | `Task/013`–`Task/016` |
| A-02 | **HTML semántico**: encabezados jerárquicos, listas, `nav`, `main`, `article`. | `Task/014` |
| A-03 | **Labels en formularios**, asociadas correctamente a sus campos. | `Task/015` |
| A-04 | **Texto alternativo** en imágenes; `alt_text` es parte de `MediaAsset`. | `Task/010`, `Task/014` |
| A-05 | **Contraste adecuado** entre texto y fondo. | `Task/013` |
| A-06 | **Estados de foco visibles**, nunca suprimidos sin reemplazo. | `Task/013` |
| A-07 | **Sin dependencia exclusiva del color** para transmitir información. | `Task/013` |
| A-08 | **Errores de formulario anunciados** de forma accesible. | `Task/015` |

---

## 4. SEO

| # | Requisito | Se verifica en |
| --- | --- | --- |
| E-01 | **Slugs legibles** y estables en todo el contenido público. | `Task/008`, `Task/014` |
| E-02 | **`title` y `description`** propios por página. | `Task/016` |
| E-03 | **Open Graph** para compartir en redes. | `Task/016` |
| E-04 | **Canonical URL** en cada página pública. | `Task/016` |
| E-05 | **Sitemap** generado a partir del contenido publicado. | `Task/016` |
| E-06 | **`robots.txt`** coherente: el panel administrativo no se indexa. | `Task/016` |
| E-07 | **Datos estructurados** cuando corresponda (artículo, review de libro, persona). | `Task/016` |
| E-08 | El contenido no publicado **nunca** aparece en sitemap ni es indexable. | `Task/016` |

---

## 5. Observabilidad

| # | Requisito | Se verifica en |
| --- | --- | --- |
| O-01 | **Logs en JSON**, estructurados y parseables. | `Task/017` |
| O-02 | **Correlation ID** en cada petición, propagado a todos sus logs y a la respuesta. | `Task/017` |
| O-03 | **Healthcheck** (`/health`) que refleja la vivacidad del proceso. | `Task/005`, `Task/017` |
| O-04 | **Readiness** (`/ready`) que comprueba base de datos y almacenamiento. | `Task/017` |
| O-05 | **Auditoría administrativa** de toda acción que modifica datos. | `Task/011`, `Task/012` |
| O-06 | **CloudWatch con retención limitada** en producción, para contener el costo. | `Task/031`, `Task/041` |
| O-07 | **Logs locales visibles mediante Docker y Portainer**. | `Task/003`, `Task/017` |
| O-08 | Los logs **no contienen** contraseñas, tokens, secretos ni datos personales innecesarios. | `Task/017`, `Task/018` |

---

## 6. Portabilidad

| # | Requisito | Se verifica en |
| --- | --- | --- |
| T-01 | **Configuración mediante variables de entorno**, validada al arrancar. | `Task/005`, `Task/006` |
| T-02 | **PostgreSQL estándar**: sin extensiones ni funciones propietarias que aten a un proveedor. | `Task/008`, `Task/029` |
| T-03 | **Interfaz `ObjectStorage`**: el dominio no conoce MinIO ni S3. | `Task/010` |
| T-04 | **Backend independiente de Lambda**: el adaptador es una capa fina y removible. | `Task/023` |
| T-05 | **Frontend independiente de Cloudflare Pages**: build estático estándar. | `Task/006`, `Task/034` |
| T-06 | **Infraestructura cloud mediante Terraform**, reproducible y destruible. | `Task/025`, `Task/039` |
| T-07 | El entorno local **se reconstruye desde cero** siguiendo un runbook escrito. | `Task/004`, `Task/022` |

---

## 7. Mantenibilidad

| # | Requisito | Se verifica en |
| --- | --- | --- |
| M-01 | **Lint y formato** automatizados en los tres repositorios. | `Task/019`–`Task/021` |
| M-02 | **Tipado estático** en backend (MyPy) y frontend (TypeScript estricto). | `Task/019`, `Task/020` |
| M-03 | **Pruebas** en la lógica de dominio y los endpoints críticos. | `Task/008`–`Task/012` |
| M-04 | **Migraciones reversibles**: toda migración aplica y revierte. | `Task/005`, `Task/008` |
| M-05 | **Documentación actualizada** como parte de la Definition of Done. | Todas |
| M-06 | **Sin capas ni abstracciones vacías** (ver [ADR-004](../adr/ADR-004-modular-monolith.md)). | Todas |

---

## 8. Cómo se usan estos requisitos

1. Toda tarea consulta los requisitos que le aplican antes de declararse lista.
2. `DEFINITION_OF_DONE.md` incorpora los que son verificables por tipo de tarea.
3. `Task/016`, `Task/017` y `Task/018` los verifican de forma sistemática.
4. `Task/022` y `Task/040` los comprueban de extremo a extremo.
5. Un requisito que no pueda cumplirse se registra como **deuda técnica explícita**, con
   su justificación — nunca se ignora en silencio.
