# Decisiones diferidas

| Campo | Valor |
| --- | --- |
| **Estado** | Registro vivo. Iniciado en `Task/002-Definir-MVP-y-Arquitectura` |
| **Última actualización** | 2026-09-06 (`Task/016` **aprobada** — **D-21 abierta**; la respuesta a `og:image` dentro de D-08 queda **Vigente** y **D-08 sigue Abierta**) |
| **Decisiones abiertas** | **13** — D-05, D-14, D-01, D-15, D-02, D-09, D-03 y **D-04** resueltas. **D-21** añadida por `Task/016` |
| **Decisiones resueltas** | **8** — D-05 (2026-07-29), D-14 y D-01 (2026-08-15), D-15, D-02 y D-09 (2026-09-01), D-03 (2026-09-04), **D-04 (2026-09-05)** |

> **D-01 se resolvió en cuanto al *modelo*** —PostgreSQL autogestionado en VPS externo—. La
> **selección de proveedor, región y tamaño sigue pendiente** y corresponde a
> `Task/029-Preparar-PostgreSQL-Produccion-en-VPS`.

Registro explícito de lo que **todavía no está decidido**, cuándo debe decidirse, qué
información hará falta y qué se ve afectado.

> Una decisión diferida **no es una omisión**: es una decisión consciente de esperar hasta
> tener la información que la haga correcta. Adelantarla sin datos es cómo se acumula
> deuda arquitectónica.

Cuando una decisión se resuelve, se marca aquí y — si es estructural — se registra como
ADR.

---

## Índice

| # | Decisión | Se resuelve en | Estado |
| --- | --- | --- | --- |
| D-01 | Modelo de PostgreSQL de producción | `Task/005.3` (modelo) · `Task/029` (proveedor) | **Resuelta** (2026-08-15) — **autogestionado en VPS externo**. Proveedor pendiente en `Task/029` |
| D-02 | Mecanismo concreto de autenticación | `Task/011` | **Resuelta** (2026-09-01) — **sesión opaca *server-side* con cookie `HttpOnly`** |
| D-03 | Biblioteca de componentes visuales | `Task/013` | **Resuelta** (2026-09-04) — **ninguna biblioteca de terceros**: CSS Modules más CSS Custom Properties |
| D-04 | Editor Markdown | `Task/015` | **Resuelta** (2026-09-05) — `<textarea>` nativo y vista previa con `MarkdownContent` |
| D-05 | Reverse proxy local concreto | `Task/003` | **Resuelta** (2026-07-29) — **Traefik v3** |
| D-06 | Backend de estado de Terraform | `Task/025` | Abierta |
| D-07 | **Dominio concreto y DNS** (no la topología: eso es D-15) | `Task/035` | Abierta |
| D-08 | Estrategia definitiva de CDN **y de acceso a medios públicos** | `Task/030` | Abierta |
| D-09 | Herramienta concreta de rate limiting | `Task/011` · reforzado en `Task/018` | **Resuelta** (2026-09-01) — **contador de ventana fija en PostgreSQL**, por IP |
| D-10 | Estrategia de backups cloud | `Task/029` | Abierta |
| D-11 | Retención exacta de CloudWatch | `Task/031` | Abierta |
| D-12 | Límites exactos de Lambda | `Task/032` | Abierta |
| D-13 | Presupuesto mensual objetivo | `Task/027` | Abierta |
| D-14 | ¿Se usará un emulador AWS local para la estrategia de IaC? | `Task/005.2` | **Resuelta** (2026-08-15) — **Sí, Floci** |
| D-15 | **Topología lógica de dominios** y política de cookies/CORS | `Task/011` | **Resuelta** (2026-09-01) — **mismo *site***: sitio y panel en el dominio raíz, API en subdominio |
| D-16 | **Mecanismo de identidad del VPS hacia AWS** para los backups | `Task/029` (decide) · `Task/030` (materializa) | Abierta |
| D-17 | **Herramienta de gestión de secretos cifrados del VPS** | `Task/029` | Abierta |
| D-18 | **Mecanismo de configuración interna del sistema operativo del VPS** | `Task/029` | Abierta |
| D-19 | **Plan, límites y costo reales de Grafana Cloud** | `Task/041` (con aporte de `Task/027`) | Abierta |
| D-20 | **Mecanismo de integración `CloudWatch → Grafana Cloud`** | `Task/031` (decide) · `Task/040` (valida) | Abierta |
| D-21 | **Estrategia de *rendering* del sitio público frente a *crawlers*** | Sin tarea asignada — abierta por `Task/016` | Abierta |

> **D-17 a D-20 se añadieron en `Task/006.2`** (**aprobada** el 2026-08-23), al formalizar la arquitectura
> objetivo de producción. **Son consecuencia de cerrar decisiones, no de abrirlas al azar:**
> decidir *qué* —secretos cifrados en el VPS, Grafana Cloud, Alloy, CloudWatch mínimo—
> obliga a nombrar explícitamente el *cómo* que **todavía no puede decidirse sin el host
> provisionado ni precios actuales**. Ninguna crea una tarea nueva. Documento canónico:
> [target-production-architecture.md](target-production-architecture.md) — **Vigente** ·
> [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) — **Aceptada**.

---

## D-01 — Modelo de PostgreSQL de producción — **RESUELTA**

> **Estado: Resuelta** el 2026-08-15, al aprobar el usuario
> `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` con la expresión exacta requerida por
> [WORKFLOW.md](../project-management/WORKFLOW.md). **Resuelve el *modelo*, no el
> proveedor.**

### Formulación original y por qué cambió

La decisión se planteó en `Task/002` como *«proveedor concreto de PostgreSQL
administrado»*, dando por supuesto el **modelo administrado**. `Task/005.3` cuestiona
precisamente ese supuesto: en una arquitectura serverless que escala a cero, una base de
datos administrada pasa a ser el componente que **domina la factura**, y además elimina el
aprendizaje operacional que el proyecto busca.

La decisión se separa por tanto en dos, que no deben confundirse:

| | Pregunta | Se resuelve en | Estado |
| --- | --- | --- | --- |
| **Modelo** | ¿Administrado o autogestionado? | **`Task/005.3`** | **Resuelta** (2026-08-15) |
| **Proveedor** | ¿Qué VPS, qué región, qué tamaño? | **`Task/029`** | **Pendiente** |

### Decisión

> **PostgreSQL de producción será autogestionado en un VPS externo**, con **PgBouncer**
> como punto de entrada, **PostgreSQL privado** y conexión **TLS** desde Lambda, que
> permanece en AWS.

- **Motivación principal:** **costo**. Evitar que PostgreSQL domine la factura mensual de
  un blog personal de tráfico bajo.
- **Motivaciones secundarias:** aprendizaje operacional real (Linux, PostgreSQL, seguridad,
  backups, recuperación), mayor control sobre versión y *tuning*, y **conservar la
  arquitectura AWS serverless** íntegra.
- **ADR:** [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) — **Aceptada**.
- **Documento canónico:** [production-postgresql-vps.md](production-postgresql-vps.md) —
  **Vigente**.

### Qué sigue pendiente pese a estar D-01 resuelta

D-01 responde **qué modelo**, no **con qué proveedor**. Siguen pendientes y se resuelven en
`Task/029-Preparar-PostgreSQL-Produccion-en-VPS`:

| Pendiente |
| --- |
| Proveedor de VPS concreto, con **precios actuales** |
| Región, y su RTT real hacia la región AWS |
| Tamaño: CPU, RAM, almacenamiento y tipo de disco |
| Versión de PostgreSQL y distribución del host |
| `pool_mode`, tamaños de pool y `max_connections` |
| Si se adopta **mTLS** además de TLS |
| Frecuencia y retención de backups (**D-10**) |
| Si **PITR** aporta valor frente a su complejidad |
| Provider de Terraform del VPS |

- **Información necesaria para `Task/029`:** costo mensual real y costos ocultos; RAM, CPU y
  almacenamiento; tráfico incluido y *egress*; snapshots del proveedor; IPv4/IPv6; región y
  **RTT medido**; SLA y reputación; provider de Terraform mantenido.
- **Afecta a:** el patrón de conexión del backend (`Task/005`), el esquema y las
  migraciones (`Task/008`), la configuración de la Lambda (`Task/032`), los backups
  (**D-10**), el costo total (`Task/041`).
- **Riesgos asociados:** **R-03** (agotamiento de conexiones, ahora mitigado por PgBouncer)
  y los nuevos **R-29** a **R-35**.
- **Nota sobre `Task/005.2`:** la aclaración de que *«la disponibilidad de un emulador no es
  un criterio de arquitectura de datos»* **sigue siendo válida y se cumple**. La decisión no
  se toma por lo que Floci soporte: se toma por costo y por aprendizaje, y su consecuencia
  es que **RDS deja de ser el destino de producción**. Ver
  [aws-local-parity.md](aws-local-parity.md) §8.

## D-02 — Mecanismo concreto de autenticación — **RESUELTA**

> **RESUELTA** en `Task/011` (2026-09-01). **Sesión opaca *server-side* con cookie
> `HttpOnly`.** Alternativas comparadas y motivo completo en la
> [ficha de `Task/011`](../tasks/TASK-011-administrative-authentication.md), sección
> *Decision Brief*; evidencia en el
> [reporte §C](../task-reports/TASK-011-report.md).
>
> **El argumento decisivo no fue la simplicidad.** USER_FLOWS.md B.12 exige que cerrar
> sesión **invalide en el servidor**, y un JWT no puede hacerlo por construcción: es una
> afirmación autocontenida, válida hasta su expiración. Cumplir ese contrato con JWT
> obliga a consultar una lista de revocación en cada petición, y ahí el JWT **pierde su
> única ventaja** —no consultar estado compartido— y **conserva todos sus costes**: un
> secreto de firma que custodiar y rotar, y *claims* que este proyecto no necesita porque
> hay un solo administrador sin roles.
>
> | Aspecto | Valor decidido |
> | --- | --- |
> | Credencial | `secrets.token_urlsafe(32)` — 256 bits, opaca |
> | Almacenamiento en la base | **`sha256(token)`**, nunca la credencial |
> | Transporte | Cookie `HttpOnly`, `SameSite=Lax`, `Path` administrativo, sin `Domain`, `Secure` obligatorio en producción |
> | Duración | **12 h absolutas**, sin renovación deslizante ni caducidad por inactividad |
> | Sesiones simultáneas | Permitidas; `logout` revoca **la actual** |
> | Hash de contraseñas | **Argon2id** (`argon2-cffi`), parámetros mínimos de OWASP |
> | CSRF | `SameSite=Lax` **+** validación de `Origin`, sin *token* sincronizado |
> | Secreto de firma | **Ninguno**: la arquitectura elegida no firma nada |
>
> **Sigue abierto para `Task/018`:** el endurecimiento (cabeceras de seguridad, CORS
> efectivo). **Para `Task/015`:** el consumo desde el panel.

- **Se resuelve en:** `Task/011-Autenticacion-Administrativa`
- **Qué está decidido ya:** un solo administrador; todos los endpoints administrativos
  autenticados salvo `login`; contraseñas con hash seguro; protección ante fuerza bruta;
  cierre de sesión; auditoría; secretos fuera de Git.
- **Qué queda por decidir:** cookie de sesión frente a *access/refresh token*; duración
  de la sesión; estrategia CSRF; algoritmo concreto de hash.
- **Información necesaria:** la **topología lógica de dominios** (**D-15**, que se resuelve
  en esta misma tarea), comportamiento de las cookies a través de API Gateway, requisitos
  de expiración deseados.
- **Afecta a:** frontend del panel (`Task/015`), API administrativa (`Task/012`), CORS
  (`Task/018`), DNS (`Task/035`).
- **Por qué se difiere:** exige tener ya el modelo de datos y el administrador (`Task/008`).
- **Corregido en `Task/005.5`.** Antes decía *«depende de la topología de dominios, que se
  define en `Task/035`»*. Eso era una **dependencia invertida**: D-02 se resuelve en
  `Task/011` y `Task/035` ocurre veinticuatro tareas después. La topología **lógica** pasa a
  ser **D-15**, resuelta en `Task/011`; `Task/035` conserva el **dominio concreto y el DNS**
  (**D-07**).

## D-03 — Biblioteca de componentes visuales — **RESUELTA**

> **Vigente** desde el 2026-09-04. Aprobada por el usuario en
> `Task/013-Sistema-de-Diseno`.

- **Se resuelve en:** `Task/013-Sistema-de-Diseno`
- **Información necesaria:** dirección visual deseada; nivel de personalización;
  accesibilidad de la biblioteca; peso del bundle; compatibilidad con los tokens propios.
- **Afecta a:** todo el frontend (`Task/013`–`Task/015`), rendimiento (`Task/016`),
  accesibilidad (`Task/016`).
- **Por qué se difirió:** elegir una biblioteca antes de saber qué componentes se
  necesitan lleva a arrastrar peso innecesario o a pelear contra sus decisiones.

### Decisión

**No se adopta ninguna biblioteca de componentes visuales de terceros.** El sistema de
diseño se construye con **CSS Modules** —nativos de Vite— y **CSS Custom Properties**,
con **cero dependencias nuevas** de runtime y de desarrollo.

### Por qué

El inventario derivado de [`USER_FLOWS`](../product/USER_FLOWS.md) y
[`MVP_SCOPE`](../product/MVP_SCOPE.md) da **cinco primitivas compartidas**: `Container`,
`Stack`, `Button`, `Card` y `Badge`. Para ese conjunto, una biblioteca de terceros
—Material UI, Chakra, Bootstrap— aporta mucho más de lo que se usaría y cobra por ello
en peso de bundle (**P-01**, **P-05**), en superficie de mantenimiento y en tener que
pelear contra sus decisiones visuales y de accesibilidad. Los frameworks de estilo
(Tailwind, Sass, styled-components, Emotion) resuelven un problema de escala que este
proyecto no tiene y ninguna fuente canónica exige.

Lo que sí se necesitaba —tokens compartidos, encapsulamiento de estilos y una estrategia
única de foco— lo da la plataforma: las Custom Properties son el runtime natural del
navegador y los CSS Modules generan sus nombres de clase en el *build*, lo que impide
estructuralmente que `Task/014` y `Task/015` dependan de una clase interna.

### Qué **no** decide

- El **editor Markdown** concreto sigue siendo **D-04** (`Task/015`).
- No prohíbe una dependencia futura para un problema puntual que la plataforma no
  resuelva: obliga a justificarla, no a evitarla.

### Consecuencia registrada

`software-architecture.md` §4.4 decía *«todavía no se selecciona una biblioteca visual
concreta»*. Queda actualizado con esta decisión, ya vigente.

## D-04 — Editor Markdown — **RESUELTA**

- **Resuelta en:** `Task/015-Panel-Administrativo`, aprobada el 2026-09-05 mediante
  `approved: Task/015-Panel-Administrativo`.
- **Estado:** **Vigente**; decisión **D-015-E**.
- **Decisión:** `<textarea>` nativo para editar Markdown, `useDeferredValue` y vista previa
  con el mismo `MarkdownContent` de `Task/014`: `react-markdown` y `rehype-sanitize`, con
  el esquema de [ADR-005](../adr/ADR-005-markdown-content.md).
- **Motivos:** conserva controles nativos y etiquetas accesibles; no añade dependencias
  ni un segundo pipeline de sanitización. El código del panel se carga en diferido,
  comprobado por P-05. Artículos, reviews, proyectos y biografía usan la vista previa;
  el contrato de videos no incluye contenido Markdown.
- **Imágenes dentro del cuerpo:** no se insertan URLs `access_url` caducables. La URL
  estable de medios continúa en **D-08 / Task/030**, que esta decisión no cierra.
- **Evidencia:** [ficha de Task/015](../tasks/TASK-015-admin-panel.md#6g-markdown--d-04-resuelta-vigente--aprobada-el-2026-09-05)
  y [reporte](../task-reports/TASK-015-report.md#7-markdown). La vista previa neutraliza
  HTML peligroso en la prueba de integración.
- **ADR:** no se crea uno nuevo; se aplica el render sanitizado ya aceptado en ADR-005.

## D-05 — Reverse proxy local concreto — **RESUELTA**

- **Resuelta en:** `Task/003-Crear-Infraestructura-Local`
- **Estado:** **Resuelta** el 2026-07-29, al aprobar el usuario `Task/003` con
  `approved: Task/003-Crear-Infraestructura-Local`.
- **Decisión: Traefik v3.**
- **Se implementa en:** `Task/007-Integracion-Local`. `Task/003` eligió la tecnología pero
  **no despliega el servicio**: la Etapa 01 deja el reverse proxy con aplicaciones reales
  para la Etapa 02, y en `Task/003` no existe todavía ninguna aplicación a la que enrutar.
- **Información necesaria:** simplicidad de configuración; soporte de rutas para sitio y
  API; comportamiento equivalente al de API Gateway; peso de la imagen; healthchecks.
- **Afecta a:** Docker Compose (`Task/003`), integración local (`Task/007`), paridad con
  producción (`Task/022`).
- **Por qué se difirió:** era una decisión local y reversible; no condiciona la nube.
- **ADR:** ninguno. Por ser local y reversible no exige registro arquitectónico.

### Decisión: Traefik v3

`Task/003` levantó PostgreSQL, MinIO y Portainer, pero **no desplegó el reverse proxy**:
la Etapa 01 deja el proxy con aplicaciones reales para la Etapa 02, y en esa tarea no
existía todavía ninguna aplicación a la que enrutar. Se eligió la tecnología; el servicio
se implementa en `Task/007-Integracion-Local`.

| Criterio | Traefik v3 | Nginx | Caddy |
| --- | --- | --- | --- |
| Simplicidad de configuración | Descubre los servicios por etiquetas del propio Compose. | Exige mantener `nginx.conf` sincronizado a mano con el Compose. | Configuración breve, en archivo aparte. |
| Rutas de sitio y de API | Por prefijo de ruta y por host, mediante etiquetas. | Soportado. | Soportado. |
| Equivalencia con API Gateway HTTP API | Alta: enrutado por ruta y middlewares de CORS y límite de tasa, las mismas capacidades previstas en `Task/033`. | Media: CORS a mano. | Media. |
| Peso de la imagen | ~200 MB | ~50 MB | ~50 MB |
| Healthchecks | `traefik healthcheck` incluido en la imagen. | Requiere `curl` o `wget` en la imagen. | Endpoint propio. |

**Compensación aceptada:** Traefik pesa unas cuatro veces más que las alternativas. Se
acepta porque elimina la duplicación de la topología entre el Compose y un archivo de
configuración paralelo, que es la fuente habitual de desajustes en un entorno local que
cambia con frecuencia.

**Aceptada** el 2026-07-29 por el usuario, junto con la aprobación de `Task/003`.
No requiere ADR: es una decisión local y reversible.

## D-06 — Backend de estado de Terraform

- **Se resuelve en:** `Task/025-Terraform-Cloud`
- **Información necesaria:** si el estado se guarda localmente o en remoto; necesidad de
  bloqueo; costo del backend remoto; acceso desde GitHub Actions (`Task/039`).
- **Afecta a:** toda la infraestructura cloud (Etapas 08, 10 y 11), automatización
  (`Task/039`).
- **Consideración:** un backend remoto exige un recurso creado antes que el resto — un
  problema de arranque que hay que resolver explícitamente.
- **Aclaración añadida el 2026-08-15 (`Task/005.2`):** **sigue abierta.** El backend de
  estado es la diferencia local/nube que **no se resuelve con un `tfvars`**: se configura en
  `terraform init -backend-config=...`. Que el laboratorio local permita un backend
  compatible con S3 demuestra que la vía es practicable, **no** decide cuál usará
  producción. La decisión sigue perteneciendo íntegramente a `Task/025`. Detalle:
  [aws-local-parity.md](aws-local-parity.md) §4.5.

## D-07 — Dominio concreto y DNS

> **Reformulada en `Task/005.5`.** Antes se llamaba *«dominio definitivo»* y arrastraba
> implícitamente la **topología**, que hace falta mucho antes. La topología lógica es ahora
> **D-15** (`Task/011`); D-07 conserva **únicamente** lo que de verdad depende del usuario y
> del gasto.

- **Se resuelve en:** `Task/035-Configurar-DNS`
- **Qué decide:** el **nombre concreto** del dominio, su compra, los registros DNS, los
  subdominios reales y los certificados públicos.
- **Qué NO decide:** si el sitio y el API comparten *site*, si las cookies son
  *first-party* o *cross-site*, y qué política CORS se aplica. Todo eso es **D-15** y se
  decide en `Task/011`, **antes**.
- **Información necesaria:** dominio disponible y elegido por el usuario; costo anual;
  subdominios necesarios (`www`, `api`, `media`) **según la topología ya fijada en D-15**.
- **Afecta a:** CORS (`Task/018`), Cloudflare Pages (`Task/034`), canonical URL y SEO
  (`Task/016`), costo (`Task/041`).
- **Por qué se difiere:** es una decisión del usuario, con costo asociado. **Diferir el
  nombre no obliga a diferir la topología**, y esa confusión era el defecto corregido.

## D-08 — Estrategia definitiva de CDN y de acceso a medios públicos

- **Se resuelve en:** `Task/030-Desplegar-Amazon-S3`
- **Información necesaria:** volumen y peso reales de las imágenes; costo de
  transferencia de S3; posibilidad de servir medios a través de Cloudflare; compatibilidad
  con URLs prefirmadas y su caché.
- **Afecta a:** rendimiento (`Task/016`), costo (`Task/041`), configuración del bucket
  (`Task/030`).
- **Tensión conocida:** las URLs prefirmadas expiran, lo que complica el cacheo en CDN.
  Hay que equilibrar privacidad y rendimiento.

### Alcance ampliado en `Task/005.5` — contenido público con bucket privado

El contenido del blog es **público**, pero el bucket es **privado** y las URLs prefirmadas
**caducan**. Esa combinación tiene consecuencias que no estaban asignadas a nadie. D-08
debe resolver, además de la CDN:

| Pregunta |
| --- |
| Si existe una **URL pública estable** para los medios del contenido publicado, y por qué vía |
| Cómo se genera la URL de acceso en cada caso: publicado frente a borrador |
| **Semántica de caché** de esas URLs, y su compatibilidad con un CDN |
| Qué URL usa **`og:image`**, que un *crawler* debe poder leer sin autenticación y sin que caduque |

**Regla que NO espera a D-08 y ya está vigente:** *nunca se persiste una URL prefirmada como
dato canónico*. La base de datos guarda `object_key`
([CONTENT_MODEL](../product/CONTENT_MODEL.md) §3.7) y **el Markdown del contenido guarda una
referencia estable, nunca una URL con expiración**. Propietarios: `Task/010` (persistencia y
generación), `Task/012` (gestión de imágenes del contenido), `Task/016` (`og:image`).

### Qué aportó `Task/010` (2026-08-28) — y qué **no** decidió

D-08 **sigue abierta**. Lo que `Task/010` entregó es el **mecanismo**, no la
política:

| Entregado en `Task/010` | Sigue siendo de `Task/030` |
| --- | --- |
| El campo público de acceso existe: `access_url`, un enlace **temporal** | Si además hay una URL **estable** para el contenido publicado, y por qué vía |
| Se genera al servir y **no se persiste** — fijado por prueba sobre las columnas reales | La **semántica de caché** de esas URLs y su compatibilidad con un CDN |
| El TTL es **configuración** (`BLOG_STORAGE_ACCESS_TTL_SECONDS`, 900 s por defecto), no una constante del adaptador | El **valor productivo** del TTL |
| `object_key` no es un campo del contrato; la precisión operativa de la invariante 9 está escrita en [`api-contracts.md`](api-contracts.md) §12 | Política del bucket, CORS y *lifecycle* |
| — | Qué URL usa `og:image` (`Task/016`) |

**Deliberadamente no se expuso `access_expires_at`**: declarar cuándo caduca el
enlace *es* describir su semántica de caché, que es una de las preguntas de
arriba. Añadirlo después sería compatible; retirarlo, no.

### Qué aporta `Task/016` — y por qué **D-08 sigue abierta**

> **Vigente** desde el 2026-09-06, al aprobarse `Task/016`. **D-08 sigue Abierta**: lo que
> `Task/016` respondió es **qué URL usa `og:image`**, que es una de sus preguntas, no la
> decisión completa.

`Task/016` es propietaria de **qué URL usa `og:image`**, y esa pregunta admite respuesta
**sin** decidir ninguna de las otras cuatro que este documento reserva a `Task/030`.

| Pregunta | Respuesta propuesta por `Task/016` |
| --- | --- |
| Qué URL usa `og:image` | Una **imagen estática propia del sitio**, versionada en `personal-blog-frontend/public/` y servida desde el mismo origen que el sitio (decisión **D-016-A**) |

**Por qué esa y no otra.** Es la única alternativa que cumple *«URL estable y no
expirable»* sin tocar el mecanismo de medios: un activo estático de `dist/` no caduca, no
exige autenticación y su semántica de caché es la que `Task/007` ya fijó para `dist/`.
Publicar un `access_url` como `og:image` está **prohibido** por la regla vigente de esta
misma decisión.

**Lo que `Task/016` NO decide, y sigue siendo de `Task/030`:**

- Si existe una URL **pública y estable** para los **medios** del contenido publicado, y
  por qué vía.
- La **semántica de caché** de esas URLs y su compatibilidad con un CDN.
- El **valor productivo** del TTL.
- La política del bucket, CORS y *lifecycle*.

**Bloqueo declarado — `B-016-1`.** Un `og:image` **personalizado por contenido** —la
portada del artículo compartido— exige precisamente una URL de medio pública y estable que
**hoy no existe**. `Task/016` entrega la imagen de sitio, **declara la limitación** y **no
cierra D-08 para desbloquearse**. Detalle en la
[ficha de `Task/016` §8](../tasks/TASK-016-seo-accessibility-performance.md).

## D-09 — Herramienta concreta de rate limiting — **RESUELTA**

> **RESUELTA** en `Task/011` (2026-09-01). **Contador de ventana fija en PostgreSQL**,
> particionado por dirección IP, aplicado a `POST /api/v1/admin/auth/login`: **10
> intentos por 300 s**, resuelto con un único `INSERT … ON CONFLICT DO UPDATE` atómico y
> respondido con `429` más `Retry-After`.
>
> **La restricción escrita en esta misma decisión es la que eligió el mecanismo:** *«el
> backend es stateless; cualquier contador debe vivir fuera del proceso»*. Eso descarta
> las bibliotecas en memoria —con `N` instancias tibias el límite efectivo sería
> `N × límite`, y llamarlo «límite global» sería falso—. Redis daría lo mismo a cambio de
> un servicio con estado, su costo y su operación **para un endpoint de un blog con un
> usuario**.
>
> **No se confunde con el bloqueo de cuenta**, que es la otra mitad y protege una cuenta
> concreta frente a la adivinación de su contraseña usando `failed_login_attempts` y
> `locked_until`. Ninguno sustituye al otro: un atacante con muchas IP burla el límite de
> tasa pero no el bloqueo.
>
> **Límites declarados, no disimulados:** la ventana fija admite hasta **2 × límite** en
> su frontera; no protege frente a un atacante distribuido que rote direcciones; y las
> filas caducadas **no se purgan**, porque no hay procesos residentes.
>
> **El *throttling* de API Gateway sigue siendo un refuerzo futuro de `Task/033`**, no el
> mecanismo: es por etapa o clave de uso, no conoce la IP como partición y no existe en
> el entorno local.

- **Se resuelve en:** `Task/011-Autenticacion-Administrativa`, reforzado en `Task/018`
- **Información necesaria:** si basta con el throttling de API Gateway o hace falta
  control por identidad; dónde guardar los contadores dado que Lambda no tiene estado;
  costo de una solución con almacén externo.
- **Afecta a:** login (`Task/011`), API Gateway (`Task/033`), endurecimiento
  (`Task/018`).
- **Restricción:** el backend es *stateless*; cualquier contador debe vivir fuera del
  proceso.

## D-10 — Estrategia de backups cloud

- **Se resuelve en:** `Task/029-Preparar-PostgreSQL-Produccion-en-VPS`
- **Información necesaria:** qué backups y snapshots incluye el proveedor elegido;
  retención; costo de retención adicional; procedimiento y tiempo de restauración; si S3
  necesita versionado.
- **Afecta a:** selección de proveedor (D-01), runbooks (`Task/026`), costo (`Task/041`).
- **Criterio ya fijado:** un backup que nunca se ha restaurado no cuenta como backup.
- **Alcance ampliado el 2026-08-15 (`Task/005.3`, aprobada):** al pasar PostgreSQL a un VPS
  autogestionado, **el proyecto asume la responsabilidad completa** del backup y del
  restore; ya no hay proveedor que los resuelva. Se añaden dos criterios firmes: **el backup
  debe salir del VPS** —una copia que solo vive en el mismo host no protege de perderlo— y
  **el restore debe demostrarse**. **PITR** y *WAL archiving* quedan como evaluación futura,
  nunca por delante de tener un backup correcto y un restore probado. Detalle:
  [production-postgresql-vps.md](production-postgresql-vps.md) §15.
- **Reparto aclarado en `Task/005.5`.** La cadena completa tiene tres propietarios y ninguno
  exige recursos que aún no existan:

  | Tramo | Owner |
  | --- | --- |
  | Mecanismo, cifrado, retención, RPO/RTO y **restore demostrado** off-host | `Task/029` |
  | **Destino S3**, política, permisos, retención definitiva y el principal de **D-16** | `Task/030` |
  | **Backup reciente y restore vigente** verificados antes del lanzamiento | `Task/040` |

  Con qué **identidad** escribe el VPS en S3 es **D-16**, no parte de esta decisión.

## D-11 — Retención exacta de CloudWatch

- **Se resuelve en:** `Task/031-Desplegar-SSM-y-CloudWatch`
- **Información necesaria:** volumen real de logs generado; costo por GB ingerido y
  almacenado; cuánto historial se necesita para diagnosticar.
- **Afecta a:** costo (`Task/041`), capacidad de diagnóstico (`Task/040`).
- **Criterio ya fijado:** la retención es **limitada y explícita**; nunca infinita.

## D-12 — Límites exactos de Lambda

- **Se resuelve en:** `Task/032-Desplegar-AWS-Lambda`
- **Información necesaria:** memoria necesaria medida; tiempo de arranque en frío real;
  duración típica y máxima de las peticiones; concurrencia esperada.
- **Afecta a:** rendimiento (`Task/016`), costo (`Task/041`), conexiones a base de datos
  (D-01).
- **Tensión conocida:** más memoria acelera la ejecución y puede reducir el costo total, y
  más concurrencia agrava el problema de conexiones. Requiere medición, no intuición.

## D-13 — Presupuesto mensual objetivo

- **Se resuelve en:** `Task/027-Configurar-Cuentas-y-Presupuestos`
- **Información necesaria:** cuánto está dispuesto a gastar el usuario al mes; costo
  estimado de cada componente; umbrales de alerta deseados.
- **Afecta a:** selección de PostgreSQL (D-01), retención de logs (D-11), límites de
  Lambda (D-12), decisión de continuar o no con la nube.
- **Por qué es crítica:** es la restricción que gobierna toda la Etapa 09 en adelante. Se
  fija **antes** de crear el primer recurso.

## D-14 — ¿Se usará un emulador AWS local para la estrategia de IaC? — **RESUELTA**

- **Planteada y resuelta en:** `Task/005.2-Documentar-Estrategia-Floci-IaC-Local`.
- **Estado:** **Resuelta** el 2026-08-15, al aprobar el usuario `Task/005.2` con
  `approved: Task/005.2-Documentar-Estrategia-Floci-IaC-Local`.

**Pregunta:** ¿el proyecto adopta un emulador AWS local para desarrollar, aprender y
validar la infraestructura como código antes de crear recursos reales, o se queda con
`terraform fmt` + `validate` y aprende directamente contra AWS?

### Decisión: **sí — Floci** como laboratorio AWS local

Se adopta **Floci** como laboratorio AWS local para validar Terraform y las integraciones
AWS antes del despliegue real, **manteniendo AWS real como la autoridad final** y con la
regla de portabilidad que impide duplicar la IaC. Justificación, alternativas (A–D),
límites de fidelidad y criterio de abandono:
[ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) — **Aceptada**; estrategia
completa: [aws-local-parity.md](aws-local-parity.md) — **Vigente**.

**Qué sigue pendiente pese a estar D-14 resuelta.** D-14 responde *si* se usa un emulador,
no *cómo*. Siguen abiertas y **no se resuelven aquí**:

| Pendiente | Se resuelve en |
| --- | --- |
| Versión concreta del emulador que se fija | `Task/025` |
| Estructura concreta de directorios de Terraform | `Task/025` |
| **Backend de estado de Terraform** (**D-06**) | `Task/025` |
| Implementación concreta de las guardas *fail-closed* | `Task/025` |
| Qué servicios resultan realmente validables en local | `Task/025`, con la matriz de paridad |
| Configuración de red y DNS del laboratorio | `Task/025` |
| Procedimientos operativos del laboratorio | `Task/026` |
| **Proveedor de la base de datos de producción** (**D-01**) | `Task/029` — **sin relación con esta decisión** |
| Integración del laboratorio en CI | `Task/039` |

- **Afecta a:** ETAPA 08 (`Task/023`–`Task/026`), ETAPA 10 (reutilización de módulos),
  ETAPA 11 (`Task/039`) y los límites de seguridad (C-12).
- **Por qué se planteó ahora y no en `Task/025`:** condiciona el **alcance** de cuatro
  tareas futuras y la forma de escribir Terraform desde el primer archivo. Descubrirlo con
  la IaC ya escrita habría obligado a rehacerla.
- **Riesgos asociados:** **R-19 a R-28**, todos **abiertos** desde la aprobación.
- **ADR:** [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) — **Aceptada** el
  2026-08-15. Por ser una decisión estructural de infraestructura, sí exige registro
  arquitectónico.

## D-15 — Topología lógica de dominios y política de cookies/CORS — **RESUELTA**

> **Añadida en `Task/005.5`** (2026-08-16). No es una decisión nueva del proyecto: es la
> **mitad temprana de D-07**, que estaba diferida hasta `Task/035` pese a que `Task/011`,
> `Task/016` y `Task/018` la necesitan antes. Separarla **elimina una dependencia
> invertida** sin adelantar ningún gasto.

> **RESUELTA** en `Task/011` (2026-09-01). **Mismo *site*, distinto origen:** el sitio
> público y el panel comparten el dominio raíz —el panel en la ruta `/admin`— y el API
> vive en un **subdominio** (`api.<dominio>`).
>
> | Aspecto | Valor decidido |
> | --- | --- |
> | Relación de sitio | **Same-site** — mismo esquema y mismo dominio registrable |
> | Relación de origen | **Cross-origin** — difiere el anfitrión |
> | Cookies | ***First-party*, host-only** (sin `Domain`). Al ser la petición *same-site*, `SameSite=Lax` **viaja igualmente**, también en `POST` |
> | CORS | Lista **explícita** del origen del panel, con credenciales. **`*` prohibido**: la configuración **no arranca si se declara `*` como origen permitido**. Declarar orígenes concretos es lo normal y no impide arrancar |
>
> **Por qué no dominios separados:** la cookie sería *cross-site*, es decir **de
> terceros**, y la autenticación pasaría a depender de políticas de privacidad y de
> configuraciones que **varían entre navegadores y entre usuarios**. Esa dependencia es
> innecesaria aquí: la topología *same-site* mantiene la cookie como *first-party* y
> reduce fragilidad **sin introducir ningún componente adicional**. **Por qué no mismo
> origen con proxy:** eliminaría CORS y el CSRF *cross-origin*, pero exige interponer un
> componente nuevo delante del API Gateway que **no figura en la arquitectura objetivo
> aprobada**; queda registrado como alternativa si `Task/035` pone un CDN delante.
>
> **No decide los nombres reales**, que siguen siendo **D-07** (`Task/035`), ni el CORS
> efectivo, que sigue siendo de `Task/018`.

- **Se resuelve en:** `Task/011-Autenticacion-Administrativa`
- **Qué decide:** si el sitio público y el API viven en el **mismo *site*** —dominio raíz
  compartido, API en subdominio— o en **dominios separados**; si las cookies serán
  ***first-party*** o ***cross-site***; y la **política CORS** que se deriva de ello.
- **Qué NO decide:** el **nombre comercial** del dominio, su compra, el DNS y los
  certificados. Eso es **D-07**, en `Task/035`.
- **Información necesaria:** viabilidad de cookies a través de API Gateway; requisitos de
  sesión de D-02; restricciones de Cloudflare Pages; implicaciones de `SameSite` y CSRF.
- **Afecta a:** mecanismo de autenticación (**D-02**, `Task/011`), API administrativa
  (`Task/012`), canonical y SEO (`Task/016`), CORS efectivo (`Task/018`), Cloudflare Pages
  (`Task/034`), DNS (`Task/035`).
- **Por qué debe resolverse aquí:** es el **primer punto del roadmap donde la respuesta es
  obligatoria**. Elegir entre cookie de sesión y *token* sin saber si habrá dominio
  compartido es elegir a ciegas, y rehacerlo después toca autenticación, CORS y frontend.
- **Restricción:** se decide la **forma**, con nombres de ejemplo. **No se compra ni se
  reserva ningún dominio** en `Task/011`.

## D-16 — Mecanismo de identidad del VPS hacia AWS

> **Añadida en `Task/005.5`** (2026-08-16), a partir de un hueco real detectado por la
> auditoría: **`Task/028` cubre GitHub OIDC → AWS y eso no da credenciales a un host
> externo.** El VPS debe escribir sus backups en S3 y **nadie era propietario de cómo se
> autentica**.

- **Se decide en:** `Task/029-Preparar-PostgreSQL-Produccion-en-VPS`
- **Se materializa en:** `Task/030-Desplegar-Amazon-S3` — principal, política y destino
- **Se valida en:** `Task/040-Validacion-Final-Produccion`
- **Pregunta:** ¿con qué identidad escribe el VPS en S3, sin que eso se convierta en una
  credencial de larga vida, con permisos amplios y sin rotación?

**Opciones que `Task/029` deberá comparar** —ninguna está elegida—:

| Opción | A favor | En contra |
| --- | --- | --- |
| Clave de acceso IAM de larga vida, muy acotada | Simple; funciona en cualquier VPS | Credencial permanente en el host: si el VPS se compromete, se compromete también |
| **IAM Roles Anywhere** con certificado | Credenciales temporales, sin clave estática | Exige PKI y rotación de certificados: complejidad operativa real |
| Empuje desde AWS en lugar de desde el VPS | Evita dar credenciales AWS al host | Invierte el flujo; puede exigir exponer más el VPS |

- **Restricciones de seguridad que la decisión debe respetar:** permiso mínimo —**escritura
  sobre un prefijo concreto**, sin lectura ni borrado del resto—; **rotación definida**;
  ninguna credencial versionada; y el compromiso del VPS **no debe** implicar el compromiso
  de la cuenta AWS.
- **Información necesaria:** distribución y capacidades del VPS ya elegido; soporte real de
  la opción en ese host; costo operativo de la rotación.
- **Afecta a:** backups (**D-10**, `Task/029`), bucket y políticas (`Task/030`), límites de
  seguridad ([security-boundaries](security-boundaries.md) §9, regla V-12), validación final
  (`Task/040`).
- **Por qué no se resuelve ahora:** depende del proveedor de VPS, que **todavía no está
  seleccionado**. Elegir el mecanismo antes que el host sería inventarlo.

> **Corolario de redacción.** Mientras D-16 siga abierta, **no debe afirmarse «sin
> credenciales permanentes» como propiedad global del proyecto**. La afirmación
> verificada se limita a **GitHub Actions → AWS** (`Task/028`).

## D-17 — Herramienta de gestión de secretos cifrados del VPS

> **Añadida en `Task/006.2`** (2026-08-23). El **modelo** queda cerrado por esa tarea:
> **secretos cifrados, clave fuera del repositorio y descifrado local seguro**. Lo que sigue
> abierto es **la herramienta**, y separar ambas cosas es deliberado.

- **Se resuelve en:** `Task/029-Preparar-PostgreSQL-Produccion-en-VPS`
- **Qué está decidido ya:** ningún secreto del VPS se versiona en claro; la clave de
  descifrado **no vive en el repositorio**; el material cifrado **sí puede versionarse**; el
  descifrado ocurre **en el host**, en el momento de usarlo. **SSM no sustituye a este
  mecanismo**: SSM sirve a la Lambda, esto sirve al VPS, y son dos superficies distintas.
- **Qué queda por decidir:** la herramienta concreta y su operación —generación, custodia y
  **rotación de la clave**, formato del material cifrado, integración con el mecanismo de
  configuración del host (**D-18**) y con el despliegue.
- **Candidato actual:** **SOPS + age**. Es el más probable, pero **no se declara todavía
  tecnología irreversible**: nadie lo ha validado en este proyecto y elegirlo sin haber
  provisionado el host ni conocido su distribución sería inventar la decisión.
- **Información necesaria:** distribución y capacidades del VPS ya elegido; qué secretos
  existen realmente (contraseñas de PostgreSQL y PgBouncer, clave privada del certificado,
  credencial de backup hacia S3 según **D-16**, credencial de Alloy hacia Grafana Cloud);
  cómo se entregan al arrancar cada servicio; costo operativo de la rotación.
- **Afecta a:** *hardening* del VPS (`Task/029`), backups (**D-10**, **D-16**), configuración
  del host (**D-18**), observabilidad (`Task/029`, ADR-008), runbooks (`Task/026`).
- **Riesgo asociado:** **R-40**.
- **Por qué no se resuelve ahora:** depende del proveedor de VPS, que **todavía no está
  seleccionado**, y del mecanismo de configuración que se elija para el host.
- **Restricción firme mientras siga abierta:** **no se generan claves `age`, ni de ninguna
  otra herramienta, ni se instala nada**, hasta `Task/029`.

## D-18 — Mecanismo de configuración interna del VPS

> **Añadida en `Task/006.2`** (2026-08-23), a partir de una regla que esa tarea sí cierra:
> **Terraform no es la herramienta de configuración del sistema operativo.** Terraform
> provisiona el recurso; lo que ocurre **dentro** del host tiene otro ciclo de vida y otra
> idempotencia. Nadie era propietario de con qué se hace ese *dentro*.

- **Se resuelve en:** `Task/029-Preparar-PostgreSQL-Produccion-en-VPS`
- **Qué está decidido ya:** la configuración interna del host **está separada de
  Terraform**. Terraform **puede** crear el VPS si el proveedor elegido tiene un provider
  mantenido, pero **no** configurar Linux.
- **Qué queda por decidir:** la herramienta. **Candidatos, ninguno elegido:** **Ansible**,
  **cloud-init**, **scripts idempotentes**. También queda por decidir cómo se ejecuta —desde
  dónde, con qué credencial— y cómo se detecta el *drift*.
- **Qué deberá cubrir, sea cual sea:** usuarios · firewall · TLS y ciclo de vida del
  certificado · PostgreSQL · PgBouncer · **Grafana Alloy** · secretos (**D-17**) · backups ·
  *hardening* y parcheo.
- **Información necesaria:** distribución del host; si el proveedor soporta `cloud-init`;
  cuántas veces se espera reconstruir el VPS; esfuerzo de mantener Ansible para **un solo
  host**; cómo se prueba el resultado sin un segundo servidor.
- **Afecta a:** reproducibilidad del VPS (`Task/029`), runbooks (`Task/026`), recuperación
  ante desastre (**R-29**, **R-35**), automatización (`Task/039`).
- **Riesgo asociado:** **R-42** — *drift* de configuración que Terraform no ve.
- **Tensión conocida:** Ansible es la respuesta profesional, pero para **un único host** su
  costo de mantenimiento puede superar su beneficio; `cloud-init` más scripts idempotentes
  puede bastar. La decisión exige tener el host delante, no elegirse por prestigio.
- **Por qué no se resuelve ahora:** depende del proveedor y de la distribución, que
  **todavía no están seleccionados**.

## D-19 — Plan, límites y costo reales de Grafana Cloud

> **Añadida en `Task/006.2`** (2026-08-23). `Task/006.2` cierra **que** Grafana Cloud es el
> plano central de observabilidad; **no** cierra en qué plan, con qué límites ni a qué
> precio — y **deliberadamente no los documenta**, porque son datos comerciales de terceros
> con fecha de caducidad.

- **Se resuelve en:** `Task/041-Proteccion-de-Costos`, con aporte de
  `Task/027-Configurar-Cuentas-y-Presupuestos`
- **Qué está decidido ya:** Grafana Cloud es el plano central de visualización, consulta y
  alertas. **El tier gratuito es una preferencia presupuestaria, no una dependencia
  arquitectónica rígida**: si deja de ser suficiente, se paga, se reduce el volumen de
  telemetría o se cambia de destino, **y la arquitectura no se rompe**.
- **Qué queda por decidir:** plan concreto; si los límites de ingesta, retención, series y
  usuarios del tier disponible **en ese momento** bastan para este volumen; costo si no
  bastan; volumen de telemetría que el proyecto va a enviar de verdad.
- **Información necesaria:** **precios y límites vigentes en el momento de decidir**, nunca
  heredados de este documento; volumen real de logs y métricas observado; presupuesto
  mensual (**D-13**).
- **Afecta a:** costo total (`Task/041`), presupuesto (**D-13**, `Task/027`), qué recolecta
  Alloy (`Task/029`), validación final (`Task/040`).
- **Riesgo asociado:** **R-38**.
- **Regla de redacción vigente:** ningún documento del proyecto persiste cuotas, límites ni
  precios de Grafana como permanentes. Si se registran, se marcan
  ***«verificar en `Task/041` / antes de contratar»***.
- **Por qué se difiere:** las condiciones de un tier gratuito **no son una garantía eterna**,
  y el volumen real de telemetría no se conoce hasta que el sistema esté en producción.

## D-20 — Mecanismo de integración `CloudWatch → Grafana Cloud`

> **Añadida en `Task/006.2`** (2026-08-23). La arquitectura **contempla** que Grafana Cloud
> vea lo que hay en CloudWatch. **Que exista** está cerrado; **con qué mecanismo**, no.

- **Se decide en:** `Task/031-Desplegar-SSM-y-CloudWatch`
- **Se valida en:** `Task/040-Validacion-Final-Produccion`
- **Pregunta:** ¿con qué identidad y por qué vía accede Grafana Cloud a CloudWatch, sin que
  eso se convierta en una credencial de larga vida, con permisos amplios y sin rotación?
- **Qué está decidido ya:** la integración **se contempla y no se implementa ahora**; cuando
  exista será de **solo lectura** y de **permiso mínimo**; **ninguna credencial de larga vida
  se versiona**; y **el compromiso de Grafana Cloud no debe implicar el compromiso de AWS**.
- **Opciones que `Task/031` deberá comparar** —ninguna está elegida—:

  | Opción | A favor | En contra |
  | --- | --- | --- |
  | **Rol IAM asumible** por el proveedor de observabilidad, con *external id* | Credenciales temporales, sin clave estática | Confía en un tercero para asumir un rol de la cuenta; exige acotar muy bien la política |
  | **Clave de acceso IAM** de solo lectura, muy acotada | Simple y universal | Credencial permanente en manos de un tercero, con rotación manual |
  | ***Push* desde AWS** hacia el destino | No entrega ninguna credencial AWS al tercero | Invierte el flujo, añade componentes y puede tener costo por volumen |

- **Información necesaria:** qué ofrece realmente el plan contratado (**D-19**); qué métricas
  y logs de CloudWatch hacen falta de verdad —no todos—; costo de las consultas de la
  API de CloudWatch, que **se paga por petición**.
- **Afecta a:** IAM (`Task/031`), costo (`Task/041`), validación final (`Task/040`),
  límites de seguridad ([security-boundaries](security-boundaries.md) §10, regla G-07).
- **Relación con D-16:** son de la **misma familia** —dar acceso acotado a AWS a algo que
  vive fuera— y deben resolverse con el mismo criterio. **No se fusionan**: son dos
  principals distintos, con dos superficies y dos ciclos de rotación distintos.
- **Por qué no se resuelve ahora:** exige que exista la cuenta AWS, los grupos de logs y el
  plan de Grafana. Nada de eso ocurre antes de la ETAPA 09.

---

## Decisiones no diferidas

Todas están **aceptadas**: aprobadas explícitamente por el usuario. Para evitar reabrir lo
cerrado:

### Aprobadas en `Task/001` (2026-07-26)

| Decisión | Dónde |
| --- | --- |
| Estrategia local-first | [ADR-001](../adr/ADR-001-local-first.md) |
| Tres repositorios separados | [ADR-002](../adr/ADR-002-three-repositories.md) |
| Nube serverless de bajo costo; exclusión de EC2, ECS, EKS, ECR, ALB y NAT Gateway | [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md) |

### Aprobadas en `Task/003` (2026-07-29)

| Decisión | Dónde |
| --- | --- |
| **Traefik v3** como reverse proxy local (D-05), a implementar en `Task/007` | D-05, en este documento |

### Aprobadas en `Task/005.2` (2026-08-15)

| Decisión | Dónde |
| --- | --- |
| **Floci** como laboratorio AWS local para validar la IaC (D-14), con AWS real como autoridad final | [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) · [aws-local-parity.md](aws-local-parity.md) |
| Terraform como fuente de verdad, **una sola definición** para local y AWS, sin duplicar módulos | [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) |

### Aprobadas en `Task/005.3` (2026-08-15)

| Decisión | Dónde |
| --- | --- |
| **PostgreSQL de producción autogestionado en VPS externo** (D-01, modelo), con **PgBouncer** delante y **PostgreSQL privado**, manteniendo FastAPI en AWS Lambda | [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) · [production-postgresql-vps.md](production-postgresql-vps.md) |
| **TLS obligatorio** en `Lambda → PgBouncer`, con **SCRAM-SHA-256** preferente y **mTLS** opcional | [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) |
| **Backups fuera del host** y **restore probado** como reglas obligatorias | [production-postgresql-vps.md](production-postgresql-vps.md) §15 |
| **La Lambda permanece fuera de VPC**; no se introduce NAT Gateway por esta decisión | [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) |

### Aprobadas en `Task/006.2` (2026-08-23)

> **Aceptadas** el 2026-08-23, al aprobar el usuario `Task/006.2` con la expresión exacta
> requerida por [WORKFLOW.md](../project-management/WORKFLOW.md). Son **vigentes y de
> cumplimiento obligatorio**. Documento canónico:
> [target-production-architecture.md](target-production-architecture.md) §21 — **Vigente**.
>
> **Aceptarlas no autoriza a implementarlas:** cada pieza sigue exigiendo su tarea
> propietaria y la autorización explícita del usuario.

| Decisión | Dónde |
| --- | --- |
| **CloudWatch se mantiene en modo mínimo**, con retención corta y alarmas imprescindibles | [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) |
| **Grafana Cloud** como plano central de visualización, consulta y alertas; tier gratuito como **preferencia presupuestaria**, no como dependencia arquitectónica | [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) |
| **Grafana Alloy** como agente del VPS; **no se autohospedan Grafana, Prometheus ni Loki** allí | [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) |
| **Secretos del VPS cifrados**, con la clave fuera del repositorio y descifrado local seguro (la herramienta es **D-17**) | [target-production-architecture.md](target-production-architecture.md) §9 |
| **La configuración interna del VPS está separada de Terraform** (el mecanismo es **D-18**) | [target-production-architecture.md](target-production-architecture.md) §17 |
| **Docker es herramienta de desarrollo, integración local y *build*/test; producción no depende de Docker como runtime** | [target-production-architecture.md](target-production-architecture.md) §18 |

### Aprobadas en `Task/002` (2026-07-26)

| Decisión | Dónde |
| --- | --- |
| Monolito modular con Clean Architecture pragmática; sin microservicios | [ADR-004](../adr/ADR-004-modular-monolith.md) |
| Contenido principal en Markdown, sanitizado al renderizar | [ADR-005](../adr/ADR-005-markdown-content.md) |
| Alcance del MVP y lo que queda fuera | [MVP_SCOPE.md](../product/MVP_SCOPE.md) |
| Convenciones de API, paginación y modelo de error | [api-contracts.md](api-contracts.md) |
| Interfaz `ObjectStorage` con implementaciones por entorno | [software-architecture.md](software-architecture.md) |
| Requisitos de autenticación (no su mecanismo) | [security-boundaries.md](security-boundaries.md) |
| Portainer solo local y sin relación con el panel | [security-boundaries.md](security-boundaries.md) |

---

## Cómo mantener este registro

1. Al resolver una decisión, se marca aquí como **Resuelta**, con fecha y tarea.
2. Si la decisión es estructural, se crea un ADR y se enlaza.
3. Una decisión nueva que aparezca a mitad del proyecto se **añade** aquí, no se resuelve
   sobre la marcha.
4. Ninguna tarea debe resolver una decisión que corresponda a otra sin registrarlo.

## D-21 — Estrategia de *rendering* del sitio público frente a *crawlers*

> **Abierta por `Task/016`** el 2026-09-06, con evidencia medida. ADR asociado:
> [ADR-009](../adr/ADR-009-rendering-strategy-for-crawlers.md) — **Propuesta**.
>
> `STAGE-05` obligaba a `Task/016` a **comprobar** el SEO de la SPA y, si las
> comprobaciones no se satisfacían, a **abrir** esta reconsideración. Se
> comprobó, no se satisfacen, y por eso existe esta decisión.

- **Se resuelve en:** **sin tarea asignada.** `STAGE-05` excluye resolverla en la
  ETAPA 05, y ninguna tarea posterior la reclama todavía.
- **Información necesaria:** si el usuario quiere **vistas previas sociales por
  URL** —es una decisión de producto, no técnica—; ritmo real de publicación;
  costo de cada opción; y evidencia con contenido real, que hoy no existe porque
  la semilla es de `Task/022`.
- **Afecta a:** **E-02**, **E-03**, **E-04** y **E-07** en el canal sin
  JavaScript; el *hosting* (`Task/034`); y, si se eligiera SSR, el modelo de
  costos de [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md).
- **Restricción:** [ADR-005](../adr/ADR-005-markdown-content.md) **sigue
  Aceptado** y el *stack* no cambia mientras esta decisión no se resuelva.

### La evidencia, en una línea

Con los metadatos **ya implementados y verificados**, un *crawler* que no ejecuta
JavaScript sigue recibiendo **cero** `og:title`, `og:description`, `og:url`,
`description`, `canonical` y JSON-LD **propios de la URL**. No era falta de
código: es el modelo de *rendering*.

Y el propósito canónico de **E-03** son las redes sociales
(`MVP_SCOPE.md` §2.2), cuyos *crawlers* son justamente los que no ejecutan
JavaScript.

### Qué NO es esta decisión

- **No es D-08.** D-08 decide **qué imagen** usa `og:image`; D-21 decide **si un
  *crawler* llega a verla**. Son independientes.
- **No es un cambio de *stack* pendiente.** Una de las opciones sobre la mesa es
  **no cambiar nada** y aceptar la limitación, que sería una decisión legítima si
  el usuario no quiere vistas previas sociales por URL.

### Qué aportó `Task/016` sin resolverla

| Entregado | Sigue abierto |
| --- | --- |
| Metadatos correctos por URL **con** JavaScript, verificados en navegador real | Los mismos **sin** JavaScript |
| Open Graph **de sitio** en `index.html`, visible sin JavaScript | Open Graph **por URL** sin JavaScript |
| `sitemap.xml` y `robots.txt` correctos en **ambos** canales | — |
| La medición de los cuatro canales, antes y después | La elección de estrategia |
