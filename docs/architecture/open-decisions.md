# Decisiones diferidas

| Campo | Valor |
| --- | --- |
| **Estado** | Registro vivo. Iniciado en `Task/002-Definir-MVP-y-Arquitectura` |
| **Última actualización** | 2026-09-27 — **`Task/029` aprobada**: **D-10**, **D-22**, **D-23** y **D-24** pasan a **Resueltas** y **EX-029-D13** a **Aceptada y Vigente**. **D-12** conserva su presupuesto preliminar aprobado y **sigue abierta**. Antes ese día: enmienda RDS aprobada, `Task/028.2` |
| **Decisiones abiertas** | **7** — D-07, D-08, D-11, D-12, D-19, D-20 y D-21 *(baja de 11 a 7 el 2026-09-27 al aprobarse `Task/029`, que resuelve D-10, D-22, D-23 y D-24)* |
| **Cerradas por no aplicabilidad** | **3** — **D-16**, **D-17** y **D-18**, el 2026-09-27, al aceptarse ADR-010: sin VPS pierden objeto. IDs y texto conservados, no reutilizables |
| **Decisiones resueltas** | **14** — D-05 (2026-07-29), D-14 y D-01 (2026-08-15), D-15, D-02 y D-09 (2026-09-01), D-03 (2026-09-04), D-04 (2026-09-05), **D-06 (2026-09-14)**, **D-13 (2026-09-17)**, y **D-10**, **D-22**, **D-23** y **D-24 (2026-09-27, `Task/029`)** |
| **Excepciones vigentes** | **EX-029-D13** — acota el sublímite AWS de **D-13** durante la etapa financiada con créditos. **Aceptada y Vigente** el 2026-09-27; vence con los créditos o el **2027-03-15**, lo que ocurra primero, y **no se renueva por inercia** |

> **D-01 se resolvió en cuanto al *modelo*** —PostgreSQL autogestionado en VPS externo—. La
> **selección de proveedor, región y tamaño sigue pendiente** y corresponde a
> `Task/029-Preparar-PostgreSQL-Produccion-en-VPS`.

> **Nota de `Task/029`, aprobada el 2026-09-27.** **D-10**, **D-22**, **D-23** y **D-24**
> pasan a **Resueltas**; el registro queda en **7 abiertas** —D-07, D-08, D-11, D-12, D-19,
> D-20 y D-21—, **14 resueltas** y 3 cerradas por no aplicabilidad. **D-12 sigue abierta**:
> se aprueba su presupuesto **preliminar** y `Task/032` la cierra **con medición**. **D-11** y
> **D-19** reciben su estimación de costo y conservan sus propietarios. Contenido:
> [paquete de decisiones](production-postgresql-rds-decisions.md) — **Vigente**.
> **La aprobación no crea recursos:** cada uno exige su tarea propietaria y la autorización
> explícita del usuario.
>
> Los dos resultados que exigían decisión humana quedaron resueltos el mismo día: el **gate
> de D-13 no se cumplía** —ninguna configuración de RDS cabe en el sublímite de USD 5/mes— y
> el usuario aceptó el exceso mediante **EX-029-D13**, con el techo global intacto; y ante el
> **cierre automático de la cuenta en el Free Plan** decidió **conservar el plan gratuito**,
> de donde sale la **vía de salida obligatoria** añadida a D-10 y el gate fechado de **R-47**.

> **Nota de `Task/028.2`, aprobada el 2026-09-27.** D-01 conserva su resolución histórica,
> pero su modelo quedó sustituido: [ADR-010](../adr/ADR-010-production-postgresql-on-rds.md)
> —**Aceptada**— fija **RDS privado**. La parte de proveedor pierde objeto y
> `Task/029-Preparar-PostgreSQL-Produccion-en-RDS` decide **D-22** a **D-24**. El registro
> tiene **24 IDs**: 11 abiertos, 10 resueltos y 3 cerrados por no aplicabilidad.

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
| D-01 | Modelo de PostgreSQL de producción | `Task/005.3` (modelo) · `Task/029` (proveedor) | **Resuelta** (2026-08-15) — **autogestionado en VPS externo**. Proveedor pendiente en `Task/029`. ***Modelo sustituido el 2026-09-27** por **RDS privado** (ADR-010, `Task/028.2`); la parte de proveedor pierde objeto y `Task/029` decide D-22 a D-24* |
| D-02 | Mecanismo concreto de autenticación | `Task/011` | **Resuelta** (2026-09-01) — **sesión opaca *server-side* con cookie `HttpOnly`** |
| D-03 | Biblioteca de componentes visuales | `Task/013` | **Resuelta** (2026-09-04) — **ninguna biblioteca de terceros**: CSS Modules más CSS Custom Properties |
| D-04 | Editor Markdown | `Task/015` | **Resuelta** (2026-09-05) — `<textarea>` nativo y vista previa con `MarkdownContent` |
| D-05 | Reverse proxy local concreto | `Task/003` | **Resuelta** (2026-07-29) — **Traefik v3** |
| D-06 | Backend de estado de Terraform | `Task/025` | **Resuelta** (2026-09-14) — estado **`local` fuera del árbol de Git y fuera del emulador** en el laboratorio; para AWS real, backend **`s3` con `use_lockfile = true`**, **sin DynamoDB** y con *bootstrap* separado. **El bucket de estado no existe todavía** |
| D-07 | **Dominio concreto y DNS** (no la topología: eso es D-15) | `Task/035` | Abierta |
| D-08 | Estrategia definitiva de CDN **y de acceso a medios públicos** | `Task/030` | Abierta |
| D-09 | Herramienta concreta de rate limiting | `Task/011` · reforzado en `Task/018` | **Resuelta** (2026-09-01) — **contador de ventana fija en PostgreSQL**, por IP |
| D-10 | Estrategia de backups cloud | `Task/029` | **Resuelta** (2026-09-27) — retención **7 días**, PITR, *snapshot* antes de cada migración, `deletion_protection`, **RPO ≤ 15 min**, **RTO ≤ 4 h** y **vía de salida fuera de la cuenta** |
| D-11 | Retención exacta de CloudWatch | `Task/031` | Abierta |
| D-12 | Límites exactos de Lambda | `Task/032` · *desde `Task/028.2`: `Task/029` deriva el presupuesto preliminar de conexiones* | Abierta — presupuesto preliminar **aprobado** el 2026-09-27 con `Task/029`: 112 / 89 / 40 con `pool_size=1`, `overflow=1` y RC=20. `Task/032` cierra **con medición** |
| D-13 | Presupuesto mensual objetivo | `Task/027` | **Resuelta** (2026-09-17) — techo USD 20/mes global y sublímite USD 5/mes AWS |
| D-14 | ¿Se usará un emulador AWS local para la estrategia de IaC? | `Task/005.2` | **Resuelta** (2026-08-15) — **Sí, Floci** |
| D-15 | **Topología lógica de dominios** y política de cookies/CORS | `Task/011` | **Resuelta** (2026-09-01) — **mismo *site***: sitio y panel en el dominio raíz, API en subdominio |
| D-16 | **Mecanismo de identidad del VPS hacia AWS** para los backups | `Task/029` (decide) · `Task/030` (materializa) | **Cerrada por no aplicabilidad** (2026-09-27) — `Task/028.2`, ADR-010 |
| D-17 | **Herramienta de gestión de secretos cifrados del VPS** | `Task/029` | **Cerrada por no aplicabilidad** (2026-09-27) — `Task/028.2`, ADR-010 |
| D-18 | **Mecanismo de configuración interna del sistema operativo del VPS** | `Task/029` | **Cerrada por no aplicabilidad** (2026-09-27) — `Task/028.2`, ADR-010 |
| D-19 | **Plan, límites y costo reales de Grafana Cloud** | `Task/041` (con aporte de `Task/027`) · *desde `Task/028.2`: `Task/029` estima y `Task/031` verifica antes de integrar* | Abierta |
| D-20 | **Mecanismo de integración `CloudWatch → Grafana Cloud`** | `Task/031` (decide) · `Task/040` (valida) · *desde `Task/028.2`: `Task/031` decide **e implementa*** | Abierta |
| D-21 | **Estrategia de *rendering* del sitio público frente a *crawlers*** | Sin tarea asignada — abierta por `Task/016` | Abierta |
| D-22 | **Red, topología y capacidad de RDS** | `Task/029` (decide) · `Task/031` (implementa) | **Resuelta** (2026-09-27) — us-east-2 *(confirmación del usuario)*, PostgreSQL **17.11**, **db.t4g.micro**, **gp3 20 GiB**, **Single-AZ**, 2 subnets privadas en 2 AZ, **sin NAT** |
| D-23 | **TLS, KMS, secretos y autenticación SQL de RDS** | `Task/029` (decide) · `Task/031`/`Task/032` (implementan) | **Resuelta** (2026-09-27) — **`verify-full`**, clave KMS gestionada por AWS, 3 identidades SQL, **SSM `SecureString`**, **IAM DB auth descartada** por memoria |
| D-24 | **Canal privado de administración y migraciones** | `Task/029` (decide) · `Task/031`/`Task/036`/`Task/038` (implementan) | **Resuelta** (2026-09-27) — **Lambda ejecutora dedicada**, serializada, con [runbook](../runbooks/rds-private-administration.md) preparado |

> *(Nota de `Task/028.2`: este párrafo es historia de `Task/006.2`. D-17 y D-18 quedaron
> cerradas por no aplicabilidad el 2026-09-27; los owners vigentes de D-19 y D-20 están en el
> índice.)*
>
> **D-17 a D-20 se añadieron en `Task/006.2`** (**aprobada** el 2026-08-23), al formalizar la arquitectura
> objetivo de producción. **Son consecuencia de cerrar decisiones, no de abrirlas al azar:**
> decidir *qué* —secretos cifrados en el VPS, Grafana Cloud, Alloy, CloudWatch mínimo—
> obliga a nombrar explícitamente el *cómo* que **todavía no puede decidirse sin el host
> provisionado ni precios actuales**. Ninguna crea una tarea nueva. Documento canónico:
> [target-production-architecture.md](target-production-architecture.md) — **Vigente** ·
> [ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) — **Aceptada**.

---

## D-01 — Modelo de PostgreSQL de producción — **RESUELTA**

**Modelo sustituido el 2026-09-27:** RDS privado, con ADR-010 **Aceptada** al aprobarse
Task/028.2. La resolución del 2026-08-15 no se borra. Task/029 ya no selecciona
proveedor de host: resuelve D-22–D-24 y prepara D-10/D-12/costos.

<details>
<summary>Historia anterior a Task/028.2 — no ejecutar como alcance actual</summary>

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

</details>

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
- **Aclaración añadida el 2026-08-15 (`Task/005.2`):** El backend de estado es la
  diferencia local/nube que **no se resuelve con un `tfvars`**: se configura en
  `terraform init -backend-config=...`. Que el laboratorio local permita un backend
  compatible con S3 demuestra que la vía es practicable, **no** decide cuál usará
  producción. La decisión pertenece íntegramente a `Task/025`. Detalle:
  [aws-local-parity.md](aws-local-parity.md) §4.5.

### Propuesta de resolución — `Task/025`, 2026-09-14

> **Estado documental: RESUELTA y VIGENTE** desde el 2026-09-14, con la aprobación
> `approved: Task/025-Terraform-Cloud`. El encabezado de esta sección se conserva como
> *«Propuesta de resolución»* porque así se redactó y porque el contenido no cambió al
> aprobarse; lo que cambió es su **estado**.
>
> **Lo aprobado es el mecanismo, no el recurso.** El bucket de estado de AWS **no
> existe**, y que el backend compatible con S3 funcione en el laboratorio sigue siendo
> **hipótesis hasta la ETAPA 10** (ADR-006, límite 5).

**La dificultad real, que conviene nombrar antes de la propuesta.** `-backend-config` puede
cambiar los **ajustes** de un backend, pero **no su tipo**. Elegir entre estado local y
estado remoto obliga a que el bloque `backend { … }` sea distinto, y ese bloque es
configuración de `init`, no una variable. Cualquier propuesta tiene que resolver eso sin
partir en dos el grafo de recursos.

**Mecanismo propuesto.** El lanzador del laboratorio genera **únicamente el bloque
`backend`** —`terraform/backend.generado.tf`, ignorado por Git— justo antes de `init`, y
pasa la ubicación con `-backend-config=path=…`. Lo generado se limita a la inicialización:
los recursos, los módulos y las variables son fuente versionada y **el grafo sigue siendo
uno solo**. Es la parte de la propuesta que ya está **ejecutada y demostrada** en el
laboratorio, no solo escrita.

**Destino local — implementado y ejercitado en `Task/025`:**

| Aspecto | Decisión propuesta |
| --- | --- |
| Tipo de backend | `local` |
| Ubicación del estado | **Fuera del árbol de Git** y **fuera del emulador**: directorio de caché del usuario, derivado del entorno. Nunca una ruta absoluta escrita en un archivo versionado |
| Por qué fuera del emulador | Su almacenamiento es `memory` y se destruye con el contenedor. Guardar ahí el estado significaría **perder el registro de lo que hay que destruir** |
| Bloqueo | El del backend `local` de Terraform, más un **cerrojo propio del lanzador** (`O_EXCL`) que garantiza **una sola operación escritora**: el ciclo toca además Docker, el emulador y el artefacto, fuera del alcance del bloqueo de estado |
| Versionado | **Nunca.** El estado puede contener valores sensibles (S-10) |

**Destino AWS real — propuesto, NO creado:**

| Aspecto | Decisión propuesta |
| --- | --- |
| Tipo de backend | `s3` |
| Bucket | **Privado y dedicado exclusivamente al estado**, separado del bucket de medios |
| Protección | Versionado, cifrado, bloqueo de acceso público, mínimo privilegio |
| Bloqueo | **`use_lockfile = true`** — bloqueo nativo en S3. **Sin tabla DynamoDB nueva**: sería un recurso más que crear, pagar y vigilar para algo que S3 ya sabe hacer |
| *Bootstrap* | **Separado del grafo de la aplicación.** Un backend remoto exige que su propio bucket exista **antes** que todo lo demás; ese arranque es una tarea aparte |
| Acceso desde CI | Mediante la identidad autorizada que definan `Task/028` y `Task/039`. Aquí no se concede ningún permiso |

**Lo que esta propuesta NO hace:**

- **No crea el bucket de estado en AWS.** No hay cuenta y no hay autorización.
- **No migra** el estado del laboratorio a AWS. Estado local y estado real son mundos
  separados: el del laboratorio describe recursos de un emulador que no existen en la nube.
- **No decide** región, nombre del bucket ni política de retención: son de la ETAPA 10.
- **No convierte** al laboratorio en prueba de que el backend `s3` funcionará en AWS. Que la
  vía sea practicable en local es una hipótesis hasta la ETAPA 10 (ADR-006, límite 5).

### Addendum Task/028 — mecanismo resuelto, materialización pendiente

**D-06 sigue Resuelta y Vigente desde Task/025.** No se reabre por la ausencia del
bucket. **EX-028-C7**, aceptada como diseño de trabajo el 2026-09-21, permite
exclusivamente al root `bootstrap/github-oidc/` estado local privado fuera de Git
y fuera del grafo de aplicación: un escritor, lock, snapshots y backups cifrados
externos con recuperación verificada. No concede permisos a CI ni cumple C-7
literalmente. Revisar a 30 días de primera creación cloud.

**Task/030** materializa el bucket S3 dedicado solo al estado: privado, versionado,
cifrado, public access block, bloqueo nativo `use_lockfile=true`, sin DynamoDB,
separado de medios/backups. Migra `bootstrap/github-oidc/terraform.tfstate` mediante
`terraform init -migrate-state` y resuelve la custodia/migración del estado del
propio bootstrap del bucket. Debe extinguir EX-028-C7 **antes del primer apply
de infraestructura de aplicación**. La ficha Task/030 deberá incorporar estos
entregables y su recuperación verificada cuando se abra; no se implementa aquí.

Es una **excepción explícita y acotada de ETAPA 10**. Task/030–033 siguen reutilizando
los módulos Task/025 para aplicación: el backend debe existir antes de inicializar
el grafo que depende de él y, por tanto, requiere bootstrap independiente.
[Procedimiento y límites](../runbooks/github-oidc-bootstrap.md).

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

**Abierta; Task/029 decide** RPO/RTO, backups automáticos RDS, PITR, retención,
snapshots, cifrado, deletion protection/snapshot final y destrucción no productiva.
Task/031 prueba restore sintético; Task/036 protege las primeras migraciones;
Task/040 restaura un backup reciente con esquema de app en destino aislado y mide
integridad/tiempos. No exigir evidencia RDS real en Task/029. Backups administrados
no necesitan identidad de host ni un bucket del proyecto como destino. D-16 quedó
cerrada por no aplicabilidad el 2026-09-27. Costos de restore temporal y snapshots cuentan.
La custodia de backups **locales** R-12 se revisa separadamente: Task/029 prepara
contrato y Task/031 documenta controles; retirar D-17 no los cifra.

> **Resuelta por `Task/029`, aprobada el 2026-09-27.** Retención **7 días**
> —el rango es 0–35 y el default 7; **nunca 0**, que desactiva los *backups*—; **PITR
> activo** como consecuencia de la retención no nula, con granularidad ~5 min; *snapshot*
> **manual antes de cada migración**, porque un *backup* automático no es un punto de
> control elegido; `deletion_protection = true` y *snapshot* final obligatorio.
> **RPO ≤ 15 min** y **RTO ≤ 4 h**, coherentes con Single-AZ y con que PITR **restaura a
> una instancia nueva**. *Backup* dentro de la asignación gratuita —igual al
> almacenamiento aprovisionado de la región—, así que **0.00 USD** mientras no se exceda.
> Copia entre regiones **no se adopta ahora**: el contenido es reproducible desde Git y S3.
> Contrato de **R-12** entregado sin cifrar nada: los respaldos locales **no** son el
> mecanismo de recuperación de producción y **no se monta un trabajo desde el equipo hacia
> S3**. Detalle:
> [paquete de decisiones §10 y §8.7](production-postgresql-rds-decisions.md#10-d-10--recuperación-backups-pitr-rpo-y-rto--resuelta).

> **Ampliación del 2026-09-27, por la decisión H-4: vía de salida fuera de la cuenta.** El
> usuario conserva el plan gratuito y difiere la continuidad a una decisión fechada. Eso
> obliga a que la opción «no continuar» sea **ejecutable**, y con el diseño anterior **no lo
> era**: los *backups* automáticos, los *snapshots* y el bucket de medios **viven dentro de la
> cuenta y desaparecen con ella**. D-10 protege de fallos de AZ, de error humano y de
> corrupción; **no** de la pérdida de la cuenta.
>
> Diseño añadido, sin servicio nuevo, **sin NAT** y sin binario extra: el **esquema** no se
> exporta —son las revisiones de Alembic ya versionadas en Git—; los **datos** salen con
> `COPY … TO STDOUT` en CSV desde el ejecutor privado de **D-24** usando `psycopg`, se
> escriben en un prefijo dedicado del bucket por el **gateway endpoint** de S3, y un **humano
> autorizado** los descarga a su estación, donde los custodia el mecanismo de respaldo local
> de `Task/004` (**R-12**). Los medios se sincronizan con AWS CLI.
>
> Propietarios: `Task/029` diseña · `Task/031` añade el modo `export` al ejecutor y sus
> permisos mínimos · **`Task/040` demuestra que el artefacto es restaurable fuera de AWS** en
> un PostgreSQL 17.11 local · `Task/041` es el gate fechado. **Un CSV en un bucket no es una
> salida probada:** hasta que `Task/040` restaure desde ella, es diseño. Detalle:
> [§10.1](production-postgresql-rds-decisions.md#101-vía-de-salida-exportación-fuera-de-la-cuenta)
> y [runbook §6.1](../runbooks/rds-private-administration.md).

<details>
<summary>Historia anterior a Task/028.2 — no ejecutar como alcance actual</summary>

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

</details>

## D-11 — Retención exacta de CloudWatch

**Abierta; Task/031 decide e implementa.** Retención explícita para logs AWS
y DB, volumen/costo/privacidad, alarmas y capacidad. Task/029 estima el costo antes
de provisionar. Task/032/033 añaden señales al desplegar sus servicios; Task/040
verifica alarmas y diagnóstico. Database Insights/Enhanced Monitoring se justifican
por utilidad y precio, no se incluyen implícitamente.

> **Estimación de `Task/029`, 2026-09-27.** Precios de us-east-1 del 2026-09-22: ingesta de
> logs **0.50 USD/GB** en clase Standard y **0.25** en Infrequent Access; almacenamiento
> **0.03 USD/GB-mes**; alarmas **0.10/alarma-mes**; métricas personalizadas **0.30/mes**;
> API **0.01/1.000 peticiones**. *Free tier* aplicable: **5 GB de ingesta, 5 GB de
> almacenamiento, 10 alarmas, 10 métricas y 1.000.000 de peticiones al mes**.
>
> Con el volumen de un blog personal, **la observabilidad mínima cabe en el *free tier*:
> 0.00 USD/mes**. Para que siga cabiendo, `Task/029` propone un techo de **8 alarmas**
> —`CPUUtilization`, `CPUCreditBalance`, `FreeableMemory`, `FreeStorageSpace`,
> `DatabaseConnections`, latencia de lectura y escritura, fallo de *backup* y
> `MaximumUsedTransactionIDs`— y un *parameter group* que **no** activa
> `log_statement = all` ni `log_min_duration_statement = 0`, porque volcarían sentencias con
> parámetros a CloudWatch y de ahí, por **D-20**, a un tercero (**R-39**, **O-08**).
> **Los umbrales los fija `Task/031`: `Task/029` no copia umbrales arbitrarios.**

<details>
<summary>Historia anterior a Task/028.2 — no ejecutar como alcance actual</summary>

- **Se resuelve en:** `Task/031-Desplegar-SSM-y-CloudWatch`
- **Información necesaria:** volumen real de logs generado; costo por GB ingerido y
  almacenado; cuánto historial se necesita para diagnosticar.
- **Afecta a:** costo (`Task/041`), capacidad de diagnóstico (`Task/040`).
- **Criterio ya fijado:** la retención es **limitada y explícita**; nunca infinita.

</details>

## D-12 — Límites exactos de Lambda

**Abierta; Task/029 deriva presupuesto preliminar y Task/032 decide con medición.**
Memoria/timeout/concurrencia reservada, pool por proceso, max_connections y reserva
de administración/migraciones/sondas. Evaluar directo frente a RDS Proxy, incluyendo
precio, autenticación, pinning y compatibilidad psycopg. Task/040 prueba carga,
saturación y recuperación. No trasladar defaults locales (pool 5 + overflow 5) a
producción sin cálculo; no exigir medición Lambda real como salida de Task/029.

> **Presupuesto preliminar de `Task/029`, 2026-09-27 — derivado, no medido.** Con
> `db.t4g.micro` (1 GiB), `max_connections` = `LEAST(DBInstanceClassMemory/9531392, 5000)`
> = **112**. Restando 3 de `superuser_reserved_connections` y reservas para migraciones
> (5), administración (3), monitorización (2) y *churn* (10): **presupuesto de aplicación =
> 89**. Con el **default local de 5 + 5 solo caben 8 entornos concurrentes**, que es la
> razón concreta de no trasladarlo. Candidato: **`pool_size = 1`, `max_overflow = 1` y
> *Reserved Concurrency* = 20** → techo de 40 conexiones, con margen de 2,2×. Se justifica
> porque el backend es **síncrono y una invocación atiende una petición**, así que un pool
> grande por proceso no compra concurrencia: solo reserva *slots*.
> **RDS Proxy descartado** — **+21.90/mes** (0.015 USD/vCPU-h × 2 vCPU × 730 h) más
> Secrets Manager, que **exige** y añade 0.80: **+22.70/mes**, ~1,6× la instancia. Además
> PostgreSQL **no admite filtros de *session pinning*** y no soporta cancelación de
> consultas por el proxy. Criterio objetivo para incorporarlo, con **medición** de
> `Task/032` o `Task/040`:
> [§6.3](production-postgresql-rds-decisions.md#63-rds-proxy--decisión-negativa-con-criterio-objetivo).
> **La configuración del backend no se modificó en `Task/029`**: el cambio es de `Task/032`.

<details>
<summary>Historia anterior a Task/028.2 — no ejecutar como alcance actual</summary>

- **Se resuelve en:** `Task/032-Desplegar-AWS-Lambda`
- **Información necesaria:** memoria necesaria medida; tiempo de arranque en frío real;
  duración típica y máxima de las peticiones; concurrencia esperada.
- **Afecta a:** rendimiento (`Task/016`), costo (`Task/041`), conexiones a base de datos
  (D-01).
- **Tensión conocida:** más memoria acelera la ejecución y puede reducir el costo total, y
  más concurrencia agrava el problema de conexiones. Requiere medición, no intuición.

</details>

## D-13 — Presupuesto mensual objetivo

- **Se resuelve en:** `Task/027-Configurar-Cuentas-y-Presupuestos`
- **Estado al 2026-09-17:** **Resuelta** mediante
  `approved: Task/027-Configurar-Cuentas-y-Presupuestos`. Gates A–E están completos. El usuario fijó **USD 20/mes** como techo de
  todo el proyecto y **USD 5/mes** como sublímite AWS, con alertas al 50 % actual, 80 %
  forecasted, 80 % actual y 100 % actual; sin actions, SNS ni reportes pagos. El
  presupuesto fue creado y verificado manualmente: mensual fijo USD 5, UnblendedCost,
  Credit/Refund excluidos, cuatro alertas porcentuales con un destinatario EMAIL cada
  una, cero SNS y cero Budget Actions. Billing Home mostró Free Plan y créditos activos tras
  la creación. Un monitor y una suscripción diaria de Cost Anomaly Detection fueron
  auditados y conservados por decisión humana como protección secundaria sin cambios;
  su atribución causal a la creación del Budget es inferida, no demostrada.
- **Información ya decidida:** voluntad máxima de gasto, sublímite AWS y umbrales. El costo
  estimado de VPS/Grafana/dominio seguirá refinándose en sus tareas propietarias sin elevar
  el techo global salvo nueva decisión explícita.
- **Descomposición obligatoria:** distinguir el techo mensual de **todo el proyecto** del
  sublímite observado por AWS Budgets. El total debe contemplar AWS, VPS, Cloudflare,
  Grafana Cloud, dominio/costos futuros y reserva. El VPS permanece sin cifra hasta
  `Task/029`; D-19 permanece abierta hasta `Task/041`.
- **Afecta a:** selección de PostgreSQL (D-01), retención de logs (D-11), límites de
  Lambda (D-12), decisión de continuar o no con la nube.
- **Por qué es crítica:** es la restricción que gobierna toda la Etapa 09 en adelante. Se
  fija **antes** de crear el primer recurso.

> **Nota de `Task/028.2`, aprobada el 2026-09-27.** **D-13 no
> cambia**: USD 20/mes para todo el proyecto y USD 5/mes de sublímite AWS. Con RDS, las
> referencias de arriba al costo del VPS se leen como costo de **RDS** —instancia,
> almacenamiento, backups y *endpoints*—. **Los créditos AWS no elevan el límite ni hacen
> gratis el costo bruto**: Budgets los excluye (Credit/Refund). `Task/029` separa **costo
> bruto**, **crédito elegible consumido**, **desembolso**, **vencimiento** y **escenario
> poscrédito**. Si el costo no cabe, una **decisión explícita** del usuario es requisito
> previo al primer `apply` de aplicación. Los créditos tampoco autorizan cambiar de plan
> (Free Plan). D-19 se verifica antes de integrar Grafana (`Task/031`).

> **Resultado del gate — `Task/029`, 2026-09-27. D-13 sigue Resuelta y NO se cambia aquí.**
>
> **El sublímite AWS de USD 5/mes es incompatible con cualquier RDS.** Con la lista de
> precios de AWS del **2026-09-24**, el mínimo absoluto —`db.t4g.micro` Single-AZ en la
> región más barata, gp3 de 20 GiB, clave gestionada por AWS, SSM estándar, solo gateway
> endpoint S3, sin Proxy, sin endpoints de interfaz y sin NAT— es **USD 13.98/mes** de costo
> bruto: **11.68** de instancia (0.016 × 730) más **2.30** de almacenamiento (20 × 0.115).
> Con el resto de AWS, **≈ 15.48/mes**: **3,1× el sublímite**. No es un problema de la
> configuración elegida; **no existe una configuración de RDS que quepa en USD 5**.
>
> **El techo global de USD 20/mes sí se sostiene:** ≈ 16.48 con ≈ 3.52 de margen.
>
> **Parar RDS no sirve como estrategia:** el máximo son **7 días consecutivos** y mientras
> está detenida se siguen cobrando almacenamiento y *backups*.

> **EX-029-D13 — excepción acotada. Aceptada y Vigente** desde el 2026-09-27, decidida por el
> usuario y aprobada con `Task/029` ese mismo día. **D-13 sigue Resuelta y su techo global no
> se modifica.**
>
> | Campo | Valor |
> | --- | --- |
> | **Qué suspende** | **Solo** el sublímite de **USD 5/mes de AWS** |
> | **Qué NO cambia** | El **techo global de USD 20/mes**, íntegro y con ≈ 3.52 de margen. Ningún otro presupuesto sube. **No reabre ni sustituye D-13** |
> | **Techo efectivo** | El costo bruto de AWS puede superar los USD 5/mes **mientras quepa bajo el techo global** junto con lo no AWS. Referencia aprobada: **≈ 15.48/mes**; una desviación material exige revisión |
> | **Motivo** | Etapa de **prueba y aprendizaje** financiada con créditos ya disponibles, con **visibilidad del costo bruto real** |
> | **Vigencia** | Hasta el **agotamiento de los créditos o el 2027-03-15**, lo que ocurra primero |
> | **No autoriza** | **Ningún recurso**; ni cambiar de plan, ni tocar Billing, ni elevar el techo global |
> | **Al expirar** | **No se renueva por inercia**: exige la decisión fechada A/B |
> | **Revisión** | `Task/041` y toda operación que se acerque al vencimiento |
>
> **Las cuatro cifras, separadas.** **A bruto:** ≈ 15.48/mes de AWS más ≈ 1.00 no AWS —la
> cifra que el proyecto vigila, y no baja por haber créditos—. **B crédito consumido:** con
> saldo de **USD 120** verificado por el usuario y límite **2027-03-15**, entre ≈ 37 y ≈ 84
> según cuándo exista RDS. **C desembolso:** **0.00** de AWS mientras rija el plan gratuito.
> **D poscrédito:** **no es un costo, es una decisión fechada**.
>
> **Hallazgo del cálculo: manda la fecha, no el saldo.** USD 120 durarían **7,75 meses**;
> solo quedan **5,55** hasta el límite, así que **caducarían ≈ USD 34 sin usar**. No hay que
> optimizar para estirar el saldo. Eso **no** justifica acelerar `Task/030` ni saltarse el
> gate de **D-06**.
>
> **Plan de la cuenta:** el usuario decidió **no** pasar a Paid Plan y que **no** sea
> prerrequisito de `Task/031`. Antes del agotamiento o del 2027-03-15 se decide **A** pagar y
> continuar o **B** desmontar, migrar o preservar. Como los *backups* administrados **mueren
> con la cuenta**, `Task/029` añade a **D-10** una **vía de salida** obligatoria. **R-47**
> reformulado. Detalle:
> [§7.5](production-postgresql-rds-decisions.md#75-ex-029-d13--excepción-acotada-al-sublímite-aws),
> [§7.7](production-postgresql-rds-decisions.md#77-la-decisión-fechada-que-sustituye-al-escenario-poscrédito)
> y [§11](production-postgresql-rds-decisions.md#11-decisiones-del-usuario--h-1-a-h-4-resueltas).

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

*(Nota de `Task/028.2`, 2026-09-27: la tabla es la del 2026-08-15. `Task/025` y `Task/026`
se aprobaron después, así que versión, estructura, guardas y **D-06** ya tienen evidencia
en la matriz de paridad; esas filas no reabren nada. La fila de D-01 pasa a ser el diseño
RDS de `Task/029` —**D-22** a **D-24**— desde que se aceptó ADR-010, igualmente **sin relación con
D-14**: RDS no se elige porque Floci lo soporte.)*

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

## D-16 — Mecanismo de identidad del VPS hacia AWS — **CERRADA POR NO APLICABILIDAD**

**Cerrada por no aplicabilidad el 2026-09-27**, al aprobarse Task/028.2 y aceptarse
ADR-010. Motivo: RDS usa backups administrados, no un proceso VPS que escribe
en AWS. No reutilizar el ID ni provisionar
el principal antes previsto. Acceso privado y nuevos roles son D-24 y tareas 031,
032, 036, 038/039; ninguno amplía el rol OIDC de validación.

<details>
<summary>Historia anterior a Task/028.2 — no ejecutar como alcance actual</summary>

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

</details>

## D-17 — Herramienta de gestión de secretos cifrados del VPS — **CERRADA POR NO APLICABILIDAD**

**Cerrada por no aplicabilidad el 2026-09-27**, al aprobarse Task/028.2 y aceptarse
ADR-010. Desaparece la gestión de secretos del host VPS, no la obligación
de proteger credenciales. D-23 cubre TLS/KMS/SSM/Secrets Manager/rotación para
RDS. R-12 de backups locales sigue abierto
y se conserva su revisión Task/029 → Task/031; no queda abandonado por este cierre.

<details>
<summary>Historia anterior a Task/028.2 — no ejecutar como alcance actual</summary>

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

</details>

## D-18 — Mecanismo de configuración interna del VPS — **CERRADA POR NO APLICABILIDAD**

**Cerrada por no aplicabilidad el 2026-09-27**, al aprobarse Task/028.2 y aceptarse
ADR-010. AWS opera el SO del host RDS. Ya no se elige Ansible/cloud-init/
scripts de Linux. D-22 conserva parameter group, ventana y upgrades; Terraform y
runbooks de Task/031/039 controlan drift administrado. ID y formulación original
preservados.

<details>
<summary>Historia anterior a Task/028.2 — no ejecutar como alcance actual</summary>

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

</details>

## D-19 — Plan, límites y costo reales de Grafana Cloud

**Abierta y aplicable:** Grafana Cloud permanece. Task/029 incorpora precios,
volumen y límites al modelo bruto/créditos; Task/031 verifica antes de contratar o
integrar; Task/041 revisa consumo real periódicamente. El tier gratuito es una
preferencia, no garantía. Todo cambio de gasto incompatible con D-13 exige decisión
explícita. No esperar hasta Task/041 para descubrir costos obligatorios.

> **Aporte de `Task/029`, 2026-09-27.** Sigue **abierta**; la verificación previa a integrar
> es de `Task/031`. **Ninguna cifra comercial de Grafana se persiste aquí**, conforme a la
> regla de redacción vigente. Lo que sí se modela es el costo **de AWS** que la integración
> **D-20** generará: `GetMetricData` cuesta **0.01 USD/1.000 métricas solicitadas**, con
> **1.000.000 de peticiones/mes** en el *free tier*. Un sondeo agresivo sobre muchas
> métricas es lo único que podría salirse del tier gratuito, así que `Task/031` fija el
> intervalo y el conjunto de métricas con ese límite a la vista. El objetivo sigue siendo el
> tier gratuito de Grafana, declarado **preferencia presupuestaria y no dependencia
> arquitectónica** (**R-38**).

<details>
<summary>Historia anterior a Task/028.2 — no ejecutar como alcance actual</summary>

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

</details>

## D-20 — Mecanismo de integración `CloudWatch → Grafana Cloud`

**Abierta; Task/031 decide e implementa** integración CloudWatch → Grafana
Cloud, con rol/principal dedicado, lectura mínima y costo de consulta/exportación
incluido. Task/040 demuestra datos y alertas con Lambda/API ya presentes. Alloy de
host pierde objeto en la enmienda ADR-010; Grafana no desaparece. No dar acceso SQL,
permisos de despliegue ni secretos permanentes versionados. Si costo o mecanismo
no encajan, resolverlo explícitamente antes de integrar, sin fingir evidencia.

<details>
<summary>Historia anterior a Task/028.2 — no ejecutar como alcance actual</summary>

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

</details>

## Decisiones no diferidas

> **Nota de `Task/028.2`, aprobada el 2026-09-27.** Las filas de esta sección que
> describen el **VPS**, **PgBouncer**, los **secretos del host**, **Alloy** o la
> **configuración del sistema operativo** quedaron sustituidas por
> [ADR-010](../adr/ADR-010-production-postgresql-on-rds.md), **Aceptada**: se conservan como
> historia y no habilitan ejecutar ese modelo. **Todas las demás siguen vigentes sin
> cambios.**


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

## D-22 — Red, topología y capacidad de RDS

> **Abierta** por `Task/028.2` el 2026-09-27, junto con
> [ADR-010](../adr/ADR-010-production-postgresql-on-rds.md), **Aceptada**. Sustituye la parte
> de **proveedor, región y tamaño** que D-01
> dejaba a `Task/029` en el modelo VPS.

- **Se resuelve en:** `Task/029-Preparar-PostgreSQL-Produccion-en-RDS` (decide) ·
  `Task/031` (implementa) · `Task/032` (prueba el tráfico real) · `Task/040` (carga y DR).
- **Qué decide:** región; versión soportada de PostgreSQL; clase, CPU y memoria;
  almacenamiento, IOPS, *throughput* y límite de crecimiento; **Single-AZ o Multi-AZ**
  según RPO/RTO y costo; VPC, CIDR, subnets, AZ y **DB subnet group** —que exige subnets en
  al menos dos AZ incluso para Single-AZ—; security groups; DNS; rutas y *endpoints*;
  ventana de mantenimiento, actualizaciones menores y *parameter group*.
- **Información necesaria:** inventario de tráfico de la Lambda repetido sobre el código
  vigente ([canónico §2](production-postgresql-rds.md#2-inventario-lambda--vpc--egress));
  precios de la fecha por región, clase, almacenamiento y *endpoint* por AZ; volumen
  esperado.
- **Afecta a:** costo frente a **D-13**, conexiones (**D-12**), recuperación (**D-10**),
  riesgos **R-29**, **R-30**, **R-32** y **R-34**.
- **Criterio ya fijado:** RDS **sin acceso público**; **sin NAT Gateway** salvo necesidad
  de salida pública demostrada y decisión explícita; ningún servicio excluido —EC2, ECS,
  EKS, ECR, ALB— sin decisión nueva; ningún valor elegido por inercia.

> **Resuelta por `Task/029`, aprobada el 2026-09-27.**
>
> | Punto | Decisión | Por qué, con dato |
> | --- | --- | --- |
> | Región | **us-east-2** — **decidida por el usuario el 2026-09-27 (H-1)** | Precio mínimo empatado con us-east-1 (13.98/mes) y latencia equivalente hacia Centroamérica; `sa-east-1` cuesta **2,1×** (29.20) y **no** mejora la latencia. **No había región canónica**: `us-east-1` es valor de laboratorio y plantilla; `us-east-2` solo aparecía como CloudShell temporal de `Task/028`. El `us-east-1` del laboratorio **no se toca**: es otro destino |
> | Versión | **PostgreSQL 17.11** | **Es la que el proyecto ya usa**: `.env` y el CI del backend fijan `postgres:17.11-alpine`. `17.8`, `16.12`, `15.16` y `14.21` están en **`NO_CREATE`**; `13.x` perdió el soporte estándar el 2026-02-28 |
> | Clase | **db.t4g.micro** (2 vCPU, 1 GiB) | 11.68/mes, la más pequeña de generación actual. `t4g.small` duplica. Cambio *in-place* con reinicio: **reversible** |
> | Almacenamiento | **gp3 20 GiB**, *autoscaling* a 50 | gp2 cuesta lo mismo con peor línea base; magnetic **deprecado**. Techo de 50 evita cruzar los 400 GiB del volumen *striped* |
> | IOPS / *throughput* | **No se configuran** | Bajo 400 GiB, gp3 incluye **3.000 IOPS y 125 MiB/s** y el rango aprovisionable es *«Not applicable»*: **no se puede**. Decisión cerrada por el servicio |
> | Disponibilidad | **Single-AZ** | Multi-AZ duplica a 27.96 para un RTO de minutos en un blog que tolera horas. **R-29 aceptado por escrito** |
> | Red | VPC `10.40.0.0/16`, **2 subnets privadas en 2 AZ**, sin subnet pública, sin IGW, **sin NAT** | El DB subnet group **exige 2 AZ incluso en Single-AZ**. Una subnet pública **no** da IP pública a la Lambda |
> | Security groups | 3, por **referencia de grupo** y nunca por CIDR | Si las subnets cambian, la regla sigue correcta y ningún rango entra por coincidencia |
> | Mantenimiento | *backup* 07:00–07:30 UTC; mantenimiento dom 08:00–09:00 UTC; minor automático **sí**, major **manual** | Madrugada local (UTC−6). Desactivar el minor automático crearía el *drift* que **R-42** persigue |
> | *Parameter group* | **Propio**, familia `postgres17`, costo 0.00 | Hace explícito `rds.force_ssl = 1` —ya default en v15+, pero un default no es contrato— y fija el registro de logs sin volcar datos |
>
> **Inventario A–E repetido** sobre `main` = `d96d5d5`: **la clase D está vacía**, así que el
> candidato **sin NAT** es viable con el código vigente. Hallazgo nuevo: **Lambda reclama la
> Hyperplane ENI tras 14 días de inactividad** y la siguiente invocación falla; owner
> `Task/032`. Detalle:
> [§2 a §4](production-postgresql-rds-decisions.md#2-inventario-de-tráfico-de-la-lambda-ae-sobre-el-código-vigente).

## D-23 — TLS, KMS, secretos y autenticación SQL de RDS

> **Abierta** por `Task/028.2` el 2026-09-27. Sustituye
> en su fondo a **D-17**: desaparecen los secretos **de host**, no la obligación de proteger
> credenciales.

- **Se resuelve en:** `Task/029` (decide) · `Task/031` (almacena, KMS, IAM y usuarios
  SQL) · `Task/032` (cliente, entrega, caché y rotación) · `Task/040` (casos negativos).
- **Qué decide:** TLS con validación de CA y *hostname* (`verify-full`), TLS obligatorio
  en el *parameter group* y rotación de la CA; clave KMS de la instancia —gestionada por AWS
  o CMK—, con custodia y recuperación; credencial *master* separada del usuario de la
  aplicación y del de migraciones; **SSM `SecureString` frente a Secrets Manager**; cómo
  llega el secreto a la Lambda —en despliegue o en *runtime*— y su rotación; si se adopta
  **IAM DB authentication**.
- **Información necesaria:** capacidades de rotación, precio y operación de cada opción;
  compatibilidad con RDS Proxy si **D-12** lo contempla; custodia del *state* de Terraform.
- **Afecta a:** si `personal-blog-backend` participa en `Task/032` —hoy no tiene lector de
  secretos—; riesgos **R-35** y **R-40**.
- **Criterio ya fijado:** SSM `SecureString` sigue siendo la base; Secrets Manager e IAM DB
  authentication **no se adoptan por inercia**. Ningún secreto en Git, `.tfvars`,
  *outputs*, planes publicados ni logs; `sensitive` no elimina un valor del *state*. La
  clave de la instancia se elige **antes** de crearla. **Este mantenimiento no lee ni crea
  secretos.**

> **Resuelta por `Task/029`, aprobada el 2026-09-27. Cero secretos generados
> o leídos.**
>
> - **TLS: `sslmode=verify-full`** —`verify-ca` no valida el *hostname*—, con
>   `rds.force_ssl = 1` explícito y CA **`rds-ca-rsa2048-g1`**, el default, con rotación
>   automática del certificado de servidor. En el *trust store* **solo el root**: registrar
>   intermedios rompe la rotación.
> - **Hallazgo del código con consecuencia concreta:** no hay `sslmode` ni `sslrootcert` en
>   `app/shared/database/` ni en `app/shared/configuration/`. Por tanto **el TLS viaja en la
>   propia `BLOG_DATABASE_URL`** y **el backend no necesita cambios** —lo que confirma que
>   `Task/029` no toca `personal-blog-backend`—, pero **el ZIP de la Lambda debe incluir el
>   bundle de la CA**: requisito de empaquetado de `Task/032`.
> - **KMS: clave gestionada por AWS (`aws/rds`)**, costo **0.00**, frente a **+1.00/mes** de
>   una CMK. La CMK añade una forma nueva de perder los datos de manera irreversible
>   (**R-35**) para controles que un solo administrador no necesita. La clave **se elige
>   antes de crear** y **ninguna prueba la deshabilita ni programa su borrado**.
> - **Tres identidades SQL separadas:** `blogadmin` (*master*, solo recuperación),
>   `blog_app` **sin DDL** y `blog_migrate` con DDL. Que `blog_app` no tenga DDL es la
>   garantía **estructural** de que una migración no puede ejecutarse al arrancar la Lambda.
> - **SSM `SecureString`, sin migrar.** Los parámetros estándar **no tienen cargo**; Secrets
>   Manager cuesta **0.40/secreto/mes** y su única ventaja real es la rotación gestionada,
>   que no se justifica con tres credenciales estables. Se reconsidera **solo** si se adopta
>   RDS Proxy —que **exige** Secrets Manager o IAM DB auth— o si la rotación pasa a ser un
>   requisito con frecuencia definida.
> - **Entrega del secreto en despliegue, no en *runtime*.** El backend **no tiene lector de
>   SSM** y leer en *runtime* exigiría un **interface endpoint a +14.60/mes** más latencia
>   de arranque en frío. Contrapartida aceptada: **rotar exige redesplegar**.
> - **IAM DB authentication: descartada, por memoria.** La documentación exige **300–1000
>   MiB extra** en la instancia, y `db.t4g.micro` tiene **1 GiB en total**: entre el 30 % y
>   el 100 % de su memoria. Secundario: token de 15 min, **CloudWatch y CloudTrail no
>   registran** la autenticación IAM, y `rds_iam` **toma precedencia** sobre la contraseña,
>   lo que puede dejar fuera al administrador (**R-43**).
>
> Detalle: [§5](production-postgresql-rds-decisions.md#5-d-23--tls-kms-secretos-y-autenticación-sql--resuelta).

## D-24 — Canal privado de administración y migraciones

> **Abierta** por `Task/028.2` el 2026-09-27. Con RDS
> privado **no hay SSH ni host**, y un *runner* público de GitHub **no alcanza la base de
> datos** solo por tener identidad OIDC.

- **Se resuelve en:** `Task/029` (decide) · `Task/031` (acceso operativo para restore) ·
  `Task/036` (primeras migraciones, recuperación del administrador **R-43** y purga
  **R-44**) · `Task/038` (canal repetible y automatizado).
- **Qué decide:** el mecanismo privado, comparando un **ejecutor Lambda dedicado**,
  invocado por el plano de control, con otras alternativas compatibles con las
  restricciones; su identidad, red, artefacto, bloqueo de concurrencia, duración máxima,
  salida saneada y recuperación.
- **Información necesaria:** duración real de las migraciones y de las operaciones de
  restore; límites del ejecutor candidato; costo.
- **Afecta a:** `Task/031`, `Task/036`, `Task/038`; riesgos **R-35**, **R-43** y **R-44**.
- **Criterio ya fijado:** ejecuciones **serializadas**, identidad SQL de migración distinta
  de la de la aplicación, **backup previo** y migraciones **nunca** como efecto lateral del
  arranque de la Lambda. Si el canal exigiera EC2 u otro servicio excluido, **se detiene** y
  se pide una decisión explícita. **Nunca** se abre la base de datos a Internet por
  conveniencia.

> **Resuelta por `Task/029`, aprobada el 2026-09-27.** Mecanismo elegido:
> **Lambda ejecutora dedicada** en las subnets privadas, invocada por el plano de control.
> No introduce ningún servicio excluido y su costo es **≈ 0.00** para uso esporádico.
>
> | Alternativa | Veredicto |
> | --- | --- |
> | *Runner* público de GitHub Actions | **No funciona**: le falta la ruta de red, no el permiso |
> | EC2 *bastion* o *host* efímero | **EC2 excluido** (§17); requeriría decisión explícita |
> | SSM Session Manager con *port forwarding* | **Exige una instancia gestionada**, es decir EC2 |
> | Client VPN | **0.10 USD/h por asociación ≈ 73/mes**: desproporcionado |
> | Abrir RDS a Internet «temporalmente» | **Prohibido**. ADR-010, **R-30** |
>
> Contrato: rol IAM propio, distinto del de la Lambda de aplicación, del de validación de
> `Task/028`, del de despliegue y del de Terraform; identidad SQL `blog_migrate`;
> **concurrencia reservada = 1** más el bloqueo de aviso de Alembic; artefacto con digest;
> salida saneada sin `DATABASE_URL` ni contraseñas; **`Task/036` toma un *snapshot* manual
> antes de la primera migración**.
>
> **Límite reconocido, no disfrazado:** el techo de Lambda es **900 s**. Las tres revisiones
> del MVP son DDL sobre tablas pequeñas y caben, pero si una migración futura no cabe **se
> detiene y se pide decisión explícita**; no se parte en trozos en silencio. `Task/036` mide
> la duración real.
>
> **Alembic es compatible con RDS sin excepciones:** **ninguna migración usa `CREATE
> EXTENSION`** —búsqueda en todo el repositorio: solo coincidencias dentro de `.venv`—, así
> que **no se necesita `rds_superuser`**. `alembic.ini` deja `sqlalchemy.url` vacío a
> propósito y `env.py` usa `get_settings()`: **las migraciones respetan el contrato
> `DATABASE_URL`**.
>
> **R-43** (recuperación del administrador) y **R-44** (purga de `login_rate_limits` y
> `administrator_sessions`) quedan diseñados sobre el mismo canal, con retenciones de 7 y 30
> días y ejecución con `blog_migrate`, **nunca** con `blog_app`. Runbook preparado y **no
> ejecutado**: [rds-private-administration.md](../runbooks/rds-private-administration.md).
> Detalle: [§8](production-postgresql-rds-decisions.md#8-d-24--canal-privado-de-administración-y-migraciones--resuelta).

Contrato detallado de las tres decisiones:
[canónico RDS §3](production-postgresql-rds.md#3-decisiones-que-entrega-task029) ·
[paquete de decisiones de `Task/029`](production-postgresql-rds-decisions.md).
