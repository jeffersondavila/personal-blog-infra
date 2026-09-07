# Requisitos no funcionales

| Campo | Valor |
| --- | --- |
| **Estado** | **Vigente** — aprobado en `Task/002-Definir-MVP-y-Arquitectura` (2026-07-26) |
| **Fecha** | 2026-07-26 · §5 ampliada y **aprobada** el 2026-08-23 (`Task/006.2`) con **O-09** y **O-10** · §2 ampliada y **aprobada** el 2026-09-06 (`Task/016`) con los umbrales **U-1** a **U-9** |

Criterios mínimos que toda implementación posterior debe respetar. Se verifican
principalmente en las Etapas 05 (`Task/016`–`Task/018`), 07 (`Task/022`) y 12
(`Task/040`).

**Total: 59 requisitos** en 7 categorías.

| Categoría | Nº | Prefijo |
| --- | ---: | --- |
| Seguridad | 12 | `S-` |
| Rendimiento | 8 | `P-` |
| Accesibilidad | 8 | `A-` |
| SEO | 8 | `E-` |
| Observabilidad | 10 | `O-` |
| Portabilidad | 7 | `T-` |
| Mantenibilidad | 6 | `M-` |
| **Total** | **59** | |

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
| P-04 | **Imágenes optimizadas**: formatos y dimensiones adecuados; miniaturas para listados. | `Task/010`, `Task/016` — la miniatura se **expone** en el contrato público desde `Task/016` |
| P-05 | **Sin descargar contenido administrativo en páginas públicas**: el código del panel se carga solo en el panel. | `Task/015`, `Task/016` |
| P-06 | **Backend stateless**: sin estado en memoria entre peticiones. | `Task/005`, `Task/023` |
| P-07 | **Compatible con cold starts de Lambda**: artefacto ligero y arranque acotado. | `Task/024`, `Task/032` |
| P-08 | **Consultas acotadas**: los listados usan índices y evitan consultas N+1. | `Task/008`, `Task/009` |

### Umbrales numéricos — fijados en `Task/016`

> **Vigentes** desde el 2026-09-06, al aprobarse `Task/016-SEO-Accesibilidad-y-Rendimiento`.

Cada umbral se ancla a un *baseline* **medido**, no elegido. Los de **peso** se expresan
sobre el *gzip* del informe de `vite build`, que es independiente del entorno; los de
**tiempo**, sobre un laboratorio declarado: Chrome *headless* por CDP, red emulada
**10 Mbps / 40 ms RTT**, CPU **4×**, caché deshabilitada.

| # | Métrica | Umbral | Baseline medido | Qué lo haría fallar |
| --- | --- | ---: | ---: | --- |
| U-1 | JS del grafo inicial público, *gzip* | **≤ 120 kB** | 100,33 kB | Que el panel o el Markdown entren en el grafo inicial |
| U-2 | CSS del grafo inicial público, *gzip* | **≤ 6 kB** | 3,15 kB | Un CSS de página sin `import` diferido |
| U-3 | *Chunk* Markdown, *gzip* | **≤ 45 kB y fuera del grafo inicial** | 37,11 kB | Importar el render de Markdown de forma estática |
| U-4 | *Chunk* administrativo, *gzip* | **≤ 15 kB y fuera del grafo inicial** | 11,25 kB | Un `import` estático del panel (**P-05**) |
| U-5 | Recursos del grafo inicial | **≤ 12** | 4–8 | Añadir peticiones en serie |
| U-6 | LCP, laboratorio | **≤ 2000 ms** | 820–980 ms | Una portada grande sin dimensiones |
| U-7 | CLS, laboratorio | **≤ 0,10** | 0,0000–0,0359 | Imágenes sin `width`/`height` |
| U-8 | Imágenes fuera del *viewport* con `loading="lazy"` | **100 %** | 100 % | Un `<img>` que no pase por el componente de medios |
| U-9 | Imágenes con `width` y `height` | **100 %** de las que el DTO los trae | 100 % | Renderizar sin dimensiones |

**Dos métricas deliberadamente sin umbral:**

- **INP** es una métrica **de campo**. No se afirma desde laboratorio, y el MVP no tiene
  tráfico real que medir.
- **TBT** sería un *proxy* de laboratorio legítimo, pero **no se ha medido**. Fijar un
  número sin *baseline* es exactamente lo que estos umbrales evitan: se mide primero.

> **Los umbrales de tiempo no son Core Web Vitals de campo** y no deben presentarse como
> tales. Y el servidor estático local **no comprime**, así que los bytes transferidos en
> local no representan producción: por eso los umbrales de peso van sobre el *gzip* del
> *build*.

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
| E-03 | **Open Graph** para compartir en redes. | `Task/016` — **NO cerrado**: por URL exige que el *crawler* ejecute JavaScript, y los de redes sociales no lo hacen. Ver **D-21** / [ADR-009](../adr/ADR-009-rendering-strategy-for-crawlers.md) |
| E-04 | **Canonical URL** en cada página pública. | `Task/016` |
| E-05 | **Sitemap** generado a partir del contenido publicado. | `Task/016` |
| E-06 | **`robots.txt`** coherente: el panel administrativo no se indexa. | `Task/016` — **parcial**: `robots.txt` y `meta noindex`. La garantía **sin JavaScript** exige `X-Robots-Tag`, que es cabecera de respuesta y por tanto **S-05**, de `Task/018` |
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
| O-06 | **CloudWatch mínimo con retención limitada y explícita** en producción, para contener el costo. Nunca retención infinita. | `Task/031`, `Task/041` |
| O-07 | **Logs locales visibles mediante Docker y Portainer**. | `Task/003`, `Task/017` |
| O-08 | Los logs **no contienen** contraseñas, tokens, secretos ni datos personales innecesarios. | `Task/017`, `Task/018` |
| O-09 | **La telemetría enviada fuera del proyecto** —logs, métricas y trazas hacia un destino de terceros— **no contiene secretos ni datos personales innecesarios**. Enviar a un tercero es **exportar**: qué se recolecta es parte del diseño, no configuración. | `Task/029`, `Task/018`, `Task/040` |
| O-10 | **La observabilidad del VPS de producción sale del host.** Un plano de observabilidad alojado en la máquina que vigila cae con ella; el *baseline* —uptime, CPU, RAM, disco, PostgreSQL, PgBouncer, fallo de backup y caducidad del certificado— se envía a un destino externo. | `Task/029`, `Task/040` |

### 5.1 Estado tras `Task/017` — **plano local**

`Task/017` implementa la observabilidad **del entorno local**. Lo que sigue clasifica lo
verificado y, con el mismo cuidado, lo que **no** queda cubierto. El alcance es local en
sentido estricto: **nada de esto afirma nada sobre la observabilidad en la nube.**

| # | Estado tras `Task/017` | Qué lo demuestra |
| --- | --- | --- |
| **O-01** | **Cubierto en local.** Logs en JSON por `stdout`, una línea por evento, con `timestamp`, `level`, `logger`, `module`, `line` y `context`. El formato `text` sigue disponible para desarrollo, y también redacta y también lleva el correlation ID | Suite de logging y lectura del contenedor real |
| **O-02** | **Cubierto en local.** `X-Request-ID` en petición y respuesta (api-contracts §9.1–§9.3), presente en **todas** las líneas de log de la petición, en `error.request_id` y en `audit_events.request_id` | Correlación extremo a extremo verificada contra el stack real |
| **O-03** | **Verificado.** `/health` responde a la vivacidad del proceso **sin** consultar dependencias. `Task/017` no lo reimplementa: lo verifica y corrige su justificación escrita | Suite de `/health` y `HEALTHCHECK` del contenedor |
| **O-04** | **Cubierto en local.** `GET /ready` comprueba PostgreSQL (`SELECT 1`) y almacenamiento (`ListObjectsV2` acotado) con **presupuesto total** por debajo del `timeout` de su consumidor, y responde `503` sin nombrar el componente | Cinco escenarios de almacenamiento y de dependencias, medidos |
| **O-05** | **Participación, no cierre.** El requisito lo cumplen `Task/011` y `Task/012`; `Task/017` aporta que el evento de auditoría lleve el **mismo** `request_id` que la respuesta y que los logs | Cadena `respuesta → log → AuditEvent` verificada |
| **O-07** | **Cubierto en local.** Los logs del backend son legibles por `docker logs` / `docker compose logs` y por la interfaz de Portainer, que lee ese mismo flujo | Ver el reporte de la tarea |
| **O-08** | **Cubierto en local.** Redacción automática e idempotente de credenciales, cookies, cabeceras de autorización, DSN y datos personales innecesarios, aplicada al mensaje, al contexto y a la **cadena de excepciones**. Cierra el plano local de **R-36** | Pruebas de señuelo: un valor sensible sembrado no aparece en la salida |

**Lo que `Task/017` NO cubre, y no debe interpretarse que cubra:**

| # | Por qué queda fuera | Propietario |
| --- | --- | --- |
| **O-06** | CloudWatch y su retención son de producción. `Task/017` no crea ningún recurso cloud | `Task/031`, `Task/041` |
| **O-08** *(endurecimiento)* | La redacción local existe y está probada; **ampliar la política** —más patrones, cabeceras y superficies— sigue siendo endurecimiento de seguridad | `Task/018` |
| **O-09** | **Exportar** telemetría a un tercero es un problema distinto del de redactar el log propio. Que el log local no filtre **no** demuestra que lo enviado fuera tampoco lo haga | `Task/029`, `Task/018`, `Task/040` |
| **O-10** | Observabilidad del VPS, que aún no existe | `Task/029`, `Task/040` |

> **Estado:** **Vigente** desde el 2026-09-06, con la aprobación de `Task/017`.

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
