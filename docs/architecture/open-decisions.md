# Decisiones diferidas

| Campo | Valor |
| --- | --- |
| **Estado** | Registro vivo. Iniciado en `Task/002-Definir-MVP-y-Arquitectura` |
| **Última actualización** | 2026-08-15 (`Task/005.2` — **D-14 añadida y resuelta**) |
| **Decisiones abiertas** | **12** — D-05 y D-14 **resueltas** |
| **Decisiones resueltas** | **2** — D-05 (2026-07-29) y **D-14** (2026-08-15) |

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
| D-01 | Proveedor concreto de PostgreSQL administrado | `Task/029` | Abierta |
| D-02 | Mecanismo concreto de autenticación | `Task/011` | Abierta |
| D-03 | Biblioteca de componentes visuales | `Task/013` | Abierta |
| D-04 | Editor Markdown | `Task/015` | Abierta |
| D-05 | Reverse proxy local concreto | `Task/003` | **Resuelta** (2026-07-29) — **Traefik v3** |
| D-06 | Backend de estado de Terraform | `Task/025` | Abierta |
| D-07 | Dominio definitivo | `Task/035` | Abierta |
| D-08 | Estrategia definitiva de CDN para medios | `Task/030` | Abierta |
| D-09 | Herramienta concreta de rate limiting | `Task/011` | Abierta |
| D-10 | Estrategia de backups cloud | `Task/029` | Abierta |
| D-11 | Retención exacta de CloudWatch | `Task/031` | Abierta |
| D-12 | Límites exactos de Lambda | `Task/032` | Abierta |
| D-13 | Presupuesto mensual objetivo | `Task/027` | Abierta |
| D-14 | ¿Se usará un emulador AWS local para la estrategia de IaC? | `Task/005.2` | **Resuelta** (2026-08-15) — **Sí, Floci** |

---

## D-01 — Proveedor concreto de PostgreSQL administrado

- **Se resuelve en:** `Task/029-Seleccionar-PostgreSQL-Administrado`
- **Información necesaria:** costo mensual real de las opciones; soporte TLS; política de
  backups y restauración; límite de conexiones concurrentes; disponibilidad de pooling o
  proxy de conexiones; latencia hacia la región de la Lambda; comportamiento con
  conexiones efímeras.
- **Afecta a:** el patrón de conexión del backend (`Task/005`), el esquema y las
  migraciones (`Task/008`), la configuración de la Lambda (`Task/032`), el costo total
  (`Task/041`).
- **Por qué se difiere:** es el **único componente con costo fijo** de la arquitectura y
  el principal riesgo técnico (agotamiento de conexiones desde Lambda). Decidirlo antes de
  conocer el patrón de acceso real sería adivinar.
- **Riesgo asociado:** R-03.
- **Aclaración añadida el 2026-08-15 (`Task/005.2`):** **sigue abierta y no la afecta la
  estrategia de paridad local.** Que un emulador soporte RDS **no es un criterio de
  arquitectura de datos**. Si `Task/029` elige AWS RDS PostgreSQL, se **evaluará** después
  su emulación local como paridad adicional; si elige un proveedor externo, **no** se usará
  RDS local solo por imitar a AWS. Detalle:
  [aws-local-parity.md](aws-local-parity.md) §8.

## D-02 — Mecanismo concreto de autenticación

- **Se resuelve en:** `Task/011-Autenticacion-Administrativa`
- **Qué está decidido ya:** un solo administrador; todos los endpoints administrativos
  autenticados salvo `login`; contraseñas con hash seguro; protección ante fuerza bruta;
  cierre de sesión; auditoría; secretos fuera de Git.
- **Qué queda por decidir:** cookie de sesión frente a *access/refresh token*; duración
  de la sesión; estrategia CSRF; algoritmo concreto de hash.
- **Información necesaria:** si el frontend y el API compartirán dominio raíz en
  producción (determina la viabilidad de cookies), comportamiento de las cookies a través
  de API Gateway, requisitos de expiración deseados.
- **Afecta a:** frontend del panel (`Task/015`), API administrativa (`Task/012`), CORS
  (`Task/018`), DNS (`Task/035`).
- **Por qué se difiere:** depende de la topología de dominios, que se define en
  `Task/035`.

## D-03 — Biblioteca de componentes visuales

- **Se resuelve en:** `Task/013-Sistema-de-Diseno`
- **Información necesaria:** dirección visual deseada; nivel de personalización;
  accesibilidad de la biblioteca; peso del bundle; compatibilidad con los tokens propios.
- **Afecta a:** todo el frontend (`Task/013`–`Task/015`), rendimiento (`Task/016`),
  accesibilidad (`Task/016`).
- **Por qué se difiere:** elegir una biblioteca antes de saber qué componentes se
  necesitan lleva a arrastrar peso innecesario o a pelear contra sus decisiones.

## D-04 — Editor Markdown

- **Se resuelve en:** `Task/015-Panel-Administrativo`
- **Información necesaria:** necesidad de vista previa en vivo; inserción de imágenes;
  peso; accesibilidad; mantenimiento del proyecto; compatibilidad con la sanitización
  elegida.
- **Afecta a:** panel administrativo (`Task/015`), sanitización (`Task/018`), tamaño del
  bundle del panel (`Task/016`).
- **Restricción ya fijada:** el backend almacena Markdown original y el render se
  sanitiza (ver [ADR-005](../adr/ADR-005-markdown-content.md)).

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

## D-07 — Dominio definitivo

- **Se resuelve en:** `Task/035-Configurar-DNS`
- **Información necesaria:** dominio disponible y elegido por el usuario; costo anual;
  subdominios necesarios (`www`, `api`, `media`).
- **Afecta a:** CORS (`Task/018`), Cloudflare Pages (`Task/034`), canonical URL y SEO
  (`Task/016`), estrategia de cookies (D-02).
- **Por qué se difiere:** es una decisión del usuario, con costo asociado.

## D-08 — Estrategia definitiva de CDN para medios

- **Se resuelve en:** `Task/030-Desplegar-Amazon-S3`
- **Información necesaria:** volumen y peso reales de las imágenes; costo de
  transferencia de S3; posibilidad de servir medios a través de Cloudflare; compatibilidad
  con URLs prefirmadas y su caché.
- **Afecta a:** rendimiento (`Task/016`), costo (`Task/041`), configuración del bucket
  (`Task/030`).
- **Tensión conocida:** las URLs prefirmadas expiran, lo que complica el cacheo en CDN.
  Hay que equilibrar privacidad y rendimiento.

## D-09 — Herramienta concreta de rate limiting

- **Se resuelve en:** `Task/011-Autenticacion-Administrativa`, reforzado en `Task/018`
- **Información necesaria:** si basta con el throttling de API Gateway o hace falta
  control por identidad; dónde guardar los contadores dado que Lambda no tiene estado;
  costo de una solución con almacén externo.
- **Afecta a:** login (`Task/011`), API Gateway (`Task/033`), endurecimiento
  (`Task/018`).
- **Restricción:** el backend es *stateless*; cualquier contador debe vivir fuera del
  proceso.

## D-10 — Estrategia de backups cloud

- **Se resuelve en:** `Task/029-Seleccionar-PostgreSQL-Administrado`
- **Información necesaria:** qué backups incluye el proveedor elegido; retención; costo
  de retención adicional; procedimiento y tiempo de restauración; si S3 necesita
  versionado.
- **Afecta a:** selección de proveedor (D-01), runbooks (`Task/026`), costo (`Task/041`).
- **Criterio ya fijado:** un backup que nunca se ha restaurado no cuenta como backup.

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
| **Proveedor de PostgreSQL administrado** (**D-01**) | `Task/029` — **sin relación con esta decisión** |
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
