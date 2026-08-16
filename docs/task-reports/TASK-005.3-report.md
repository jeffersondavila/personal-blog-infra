# Reporte — TASK-005.3 · Definir PostgreSQL de producción en VPS

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` |
| **Tipo** | **Mantenimiento de arquitectura y gobierno documental** |
| **Cuenta en el roadmap** | **No.** Avance global y ETAPA 02 **sin cambios** |
| **Estado final** | **Aprobada** ✔ — cerrada el 2026-08-15 |
| **Expresión de aprobación** | `approved: Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` |
| **Repositorio** | `personal-blog-infra` **únicamente** |
| **Rama** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS`, creada desde `dev` (`a563de6`). **Publicada en el cierre** |
| **Fecha** | 2026-08-15 |
| **Ficha** | [TASK-005.3](../tasks/TASK-005.3-define-production-postgresql-vps.md) |
| **Commits** | **1**, creado **después** de la aprobación explícita del usuario |
| **Pull request** | `Task/005.3 → main` — **abierto, sin fusionar** |

---

## 1. Estado Git inicial encontrado

Verificado en Git y GitHub al comenzar la sesión, sin asumir nada de conversaciones previas.

| Repositorio | `main` | `dev` | Rama activa | Árbol | Ramas `Task/*` remotas |
| --- | --- | --- | --- | --- | --- |
| `personal-blog-infra` | **`5583947`** | **`a563de6`** | `main` | Limpio | Ninguna — `origin/Task/005.2` aparece como `[deleted]` en el `fetch --prune` |
| `personal-blog-backend` | `db6ab18` | `ce4f1bc` | `main` | Limpio | Ninguna |
| `personal-blog-frontend` | `144a401` | `8823cc3` | `main` | Limpio | Ninguna |

**Cierre de `Task/005.2` confirmado**, tal como indicó el usuario:

| Comprobación | Resultado |
| --- | --- |
| `gh pr view 8` | **`MERGED`**, base `main`, head `Task/005.2-…`, merge commit **`5583947`**, `mergedAt = 2026-08-16T01:23:02Z` (UTC) |
| Rama remota `Task/005.2` | **Eliminada** por el usuario |
| `git ls-remote --heads origin "Task/*"` | **Vacío** en los tres repositorios |
| Normalización `main → dev` | **Hecha por el usuario**: `dev` = `a563de6`, `Merge branch 'main' into dev`, publicado |

**No se repitió el cierre de `Task/005.2`** ni se alteró ninguna historia de Git.

## 2. Confirmación de `main` y `dev` sincronizados

| Comprobación | Resultado |
| --- | --- |
| `main` frente a `origin/main` | **Al día** |
| `dev` frente a `origin/dev` | **Al día** |
| `git log --oneline dev..main` | **Vacío** ✔ — `main` está contenida en `dev` |
| `git diff --stat main dev` | **Vacío** ✔ — mismo contenido |
| Rama `Task/005.2` local o remota | **No existe** ✔ |
| Working tree | **Limpio** ✔ |

Todo coherente: **se usó `dev` como base**, sin ninguna acción correctiva.

**Backend y frontend** se verificaron con `fetch --prune`, comprobando `main`/`dev`,
`dev..main` vacío, `git diff main dev` vacío y árbol limpio. **No se modificó ningún archivo
y no se creó ninguna rama de `005.3` en ellos.**

## 3. Rama creada

Comprobaciones **previas**, todas negativas como se esperaba: sin rama local `Task/005.3`,
sin rama remota, sin PR relacionado.

| Campo | Valor |
| --- | --- |
| **Nombre** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` |
| **Base** | `dev` |
| **Commit base** | **`a563de63d5ff8f9ac1870d39c0f8f23b486fbee4`** |
| **Publicada** | **No** |

## 4. Documentos inspeccionados

`CLAUDE.md` · `PROJECT_INSTRUCTIONS.md` · `WORKFLOW.md` · `STATUS.md` · `ROADMAP.md` ·
`DEFINITION_OF_DONE.md` · `overview.md` · `open-decisions.md` · `local-to-cloud-mapping.md` ·
`security-boundaries.md` · `aws-local-parity.md` · `software-architecture.md` ·
`non-functional-requirements.md` · `MVP_SCOPE.md` · los **6 ADR existentes** · las **13
fichas de etapa** · ficha y reporte de `Task/005.2` · runbook de backup local.

Nombres de archivo, números de ADR, IDs de riesgo y nombres de etapa se **verificaron en el
repositorio**, no se asumieron:

| Dato | Verificado |
| --- | --- |
| Siguiente ADR libre | **ADR-007** — existían ADR-001 a ADR-006 |
| Último ID de riesgo | **R-28** — siguiente libre: **R-29** |
| Etapa que contiene `Task/029` | **`STAGE-09-cloud-accounts.md`** |
| Nombre real de `Task/029` | `Task/029-Seleccionar-PostgreSQL-Administrado`, en 6 archivos |

## 5. Estado previo de D-01

D-01 estaba formulada como **«Proveedor concreto de PostgreSQL administrado»**, con estado
**Abierta**, a resolver en `Task/029`. Daba por supuesto el **modelo administrado** — que es
exactamente el supuesto que esta tarea cuestiona.

Se resolvía en dos documentos: `open-decisions.md` §D-01 y el índice de decisiones. **D-10**
(estrategia de backups cloud) también apuntaba a `Task/029` y dependía del proveedor elegido.

## 6. Problema identificado

[ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md) ya lo dejaba escrito: *«la base de
datos administrada es el único componente con costo fijo de la arquitectura»*.

| # | Problema |
| --- | --- |
| 1 | **Costo desproporcionado.** En una arquitectura que escala a cero, la base de datos administrada **domina la factura** y cuesta más que todo lo demás junto, para servir un blog de tráfico bajo. |
| 2 | **Pérdida del aprendizaje operacional.** Pagar por que un proveedor gestione SO, PostgreSQL, seguridad, backups y recuperación **elimina justo lo que el proyecto quiere aprender**. |
| 3 | **Trabajo de red adicional.** Una instancia administrada privada obliga a **conectar la Lambda a la VPC**, lo que le hace perder el acceso a Internet gestionado por defecto y exige diseñar su *egress*. **No es que RDS «arrastre» NAT Gateway** — ver §7.8. |

La pregunta correcta no era *«¿AWS o VPS?»* sino *«¿qué parte concreta de la arquitectura
justifica un costo fijo?»*.

## 7. Decisión arquitectónica propuesta

> **PostgreSQL de producción será autogestionado en un VPS económico, independiente de AWS,
> mientras el backend FastAPI permanece en AWS Lambda.**

```
Cloudflare Pages → API Gateway → Lambda (FastAPI) ──TLS──► PgBouncer → PostgreSQL (VPS)
```

### 7.1 Qué permanece en AWS

**API Gateway HTTP API · Lambda · IAM · S3 · SSM Parameter Store · CloudWatch.** Toda la
lógica de aplicación y su configuración. Terraform, Floci y Cloudflare Pages **sin cambios**.

### 7.2 Qué vive en el VPS

Sistema operativo · runtime/Docker cuando corresponda · **PgBouncer** · **PostgreSQL** ·
almacenamiento persistente · backups · herramientas operativas necesarias. **Nada más**: la
responsabilidad del VPS es la **capa de datos de producción**.

### 7.3 Rol de PgBouncer

Es el **punto de entrada de la capa de datos**: el **único endpoint de esa capa alcanzable
desde fuera del VPS**. El acceso administrativo por **SSH** es un canal **separado**, ajeno
a la capa de datos.
Controla el número de conexiones reales a PostgreSQL y **protege la base de datos de las
ráfagas de concurrencia de Lambda**, desacoplando el número de clientes del número de
conexiones. Es la materialización concreta de la mitigación que **R-03** pedía desde
`Task/002`.

**No se fija ningún número**: `pool_size`, `max_client_conn`, `max_db_connections`,
`reserve_pool_size`, `pool_mode` y *timeouts* deben salir de la capacidad real del VPS, de
`max_connections`, del comportamiento de SQLAlchemy/psycopg y de **pruebas de carga**.

### 7.4 Por qué PostgreSQL no será público

Una base de datos escuchando en `0.0.0.0:5432` es una superficie de ataque directa sobre los
datos. La regla es obligatoria: **PostgreSQL solo acepta conexiones internas del VPS** y su
puerto **no se publica** en la interfaz pública, por configuración de *binding* y firewall,
no por convención.

Queda además escrito que **no hay *security through obscurity***: cambiar el puerto, usar una
contraseña larga o confiar en que nadie conozca la IP **no son controles**. La frontera son
firewall, *binding* privado, TLS y autenticación.

### 7.5 TLS, SCRAM y mTLS

| Elemento | Estado |
| --- | --- |
| **TLS** | **Obligatorio** en `Lambda → PgBouncer`, con **validación del certificado del servidor**. Un TLS que no valida no protege frente a un intermediario. |
| **SCRAM-SHA-256** | **Mecanismo preferente** de autenticación cuando la implementación lo permita. `Task/029` verifica la compatibilidad real de PgBouncer + PostgreSQL + psycopg. |
| **mTLS** | **Evaluable, no obligatorio.** Antes de adoptarlo hay que resolver rotación de certificados, impacto de una caducidad —dejaría el sitio sin base de datos—, compatibilidad y entrega del certificado a Lambda sin versionarlo. Se decide en `Task/029`. |

### 7.6 Abstracción `DATABASE_URL`

**FastAPI no sabe que PostgreSQL vive en un VPS.** La aplicación depende de una sola cosa:
`DATABASE_URL`. En desarrollo apunta a PostgreSQL local; en producción, a PgBouncer.

El dominio y los casos de uso **no dependen** de proveedor, IP, Floci, RDS, Docker ni
PgBouncer. Consecuencia práctica: **este cambio de arquitectura no obliga a tocar una línea
del backend** — y es también lo que hace la decisión **reversible**.

### 7.7 Concurrencia de Lambda

**Reserved Concurrency** queda registrada como el **primer control**, aguas arriba: limita
cuántas invocaciones simultáneas pueden existir y acota la presión sobre PgBouncer.

**No se fija `N`.** Concurrencia reservada, pool de PgBouncer y `max_connections` forman un
sistema y deben derivarse de pruebas, no de intuición.

### 7.8 La Lambda permanece fuera de VPC — y la precisión sobre RDS/NAT

**La Lambda no se conecta a ninguna VPC.** Así conserva el acceso a Internet gestionado por
Lambda y alcanza el **endpoint público seguro de PgBouncer**, protegido por TLS, firewall y
autenticación fuerte.

Documentación oficial de AWS, consultada el **2026-08-15**:

| # | Hecho |
| --- | --- |
| 1 | Por omisión, las funciones Lambda **tienen acceso a Internet público**. |
| 2 | Un **RDS privado implica conectar la Lambda a la VPC** correspondiente. |
| 3 | **NAT Gateway NO es necesario** para que esa Lambda alcance RDS **dentro** de la VPC: ese tráfico no sale a Internet. |
| 4 | Pero **una Lambda conectada a una VPC pierde la salida a Internet gestionada por defecto**: solo alcanza recursos de esa VPC. |
| 5 | **Si además necesita salida IPv4 a Internet**, hay que darle un mecanismo de *egress*. **NAT Gateway es una opción, no una consecuencia obligatoria de RDS**: existen *egress-only internet gateway* para IPv6 y **VPC endpoints** para servicios AWS. Una subred pública **no** da acceso a Internet a la función. |

> **Corrección explícita de un error frecuente:** **NAT Gateway no es inherente a RDS.** Es la
> consecuencia de que una Lambda *dentro de una VPC* necesite salida IPv4 a Internet.

**Esta precisión no cambia la decisión.** La alternativa RDS se descarta por **costo del
servicio administrado y por aprendizaje operacional**. Lo que queda registrado es que RDS
**exigiría diseñar la conectividad de red de la Lambda**, trabajo que la opción elegida no
requiere.

En nuestra arquitectura la base de datos **no está en una VPC de AWS**, así que la Lambda
necesita salida a Internet — que ya tiene por omisión. Meterla en una VPC sería
contraproducente: perdería esa salida y habría que reponerla, y si fuese con NAT Gateway
aparecería un **costo fijo** que ADR-003 excluye. Si aparece un **requisito real** —IP de
salida fija, conectividad privada, VPN— será una **decisión separada**.

### 7.9 Latencia y región

Requisito futuro registrado: la ubicación del VPS debe elegirse **teniendo en cuenta la
región AWS** de Lambda, para minimizar el RTT. Cada consulta lo paga y una petición HTTP
suele hacer varias.

`Task/029` debe considerar región AWS, regiones del proveedor, **RTT medido**, costo y
disponibilidad. Regla explícita: **no elegir un VPS lejano por ahorrar poco al mes**.

### 7.10 Backups y restore

| Regla | Estado |
| --- | --- |
| **Un backup que solo existe en el mismo VPS no es un backup de recuperación ante desastres** | **Obligatoria** |
| **Un backup no se considera validado hasta haber demostrado una restauración correcta** | **Obligatoria** |

Estrategia candidata: `pg_dump` → compresión → cifrado → **almacenamiento externo** →
retención. **S3 es el destino natural** porque ya está en la arquitectura. **No se
implementan scripts** y **no se fija frecuencia ni retención**: es de `Task/029` y de los
runbooks de `Task/026`.

El proyecto ya tiene precedente: `Task/004` produjo un runbook de backup local **con
restauración demostrada**. La capa de producción debe alcanzar al menos ese estándar.

### 7.11 PITR

**Evaluación futura, no requisito del MVP.** Prioridad correcta: **backup correcto → restore
probado → procedimiento reproducible**. Un PITR mal operado es peor que un `pg_dump` diario
que sí se sabe restaurar. `Task/029` decidirá si aporta valor frente a su complejidad.

### 7.12 SPOF y disponibilidad

`1 VPS = Single Point of Failure`, **aceptado de forma explícita y consciente**.

**No se introducen** segundo PostgreSQL, réplica, Patroni, etcd, *failover* automático,
balanceador ni clúster. Para un blog personal, añadir HA multiplicaría costo y complejidad
para protegerse de una caída que se resuelve reconstruyendo desde un backup — la
sobreingeniería que ADR-003 evita.

Mitigación inicial: backups fuera del host · restore probado · infraestructura reproducible ·
documentación · monitoreo · procedimiento de recuperación.

### 7.13 RPO y RTO

**Intención, no SLA.** RPO: orden de horas, hasta aproximadamente un día para el MVP. RTO:
recuperación manual de algunas horas, aceptable para un blog personal. `Task/029` y los
runbooks deben convertirlo en objetivos concretos y medidos. **No se promete ningún SLA.**

### 7.14 Terraform

La estrategia IaC **no se reduce: se amplía**. La arquitectura pasa a ser conceptualmente
**multi-provider** — AWS + Cloudflare + VPS — sin dejar de ser una sola fuente de verdad.

`Task/029` debe **favorecer** un proveedor con provider de Terraform mantenido, pero **no es
el único criterio**: si el mejor proveedor por costo y red no lo tiene, **la excepción se
documenta explícitamente**. Y **no se crean abstracciones ficticias** para esconder
diferencias entre proveedores.

**No se creó ningún archivo `.tf`, `.tfvars`, `.hcl`, backend, provider, módulo ni *state*.**

### 7.15 Objetivo de costo

Registrado como **objetivo de arquitectura**, no compromiso: la capa PostgreSQL debe
mantenerse en un rango pequeño y predecible. Se anota el orden de magnitud de **USD 5–12
mensuales** con advertencias explícitas: **no es un SLA**, **no es un precio garantizado**,
**no debe usarse para elegir proveedor** sin verificar precios actuales.

La motivación real no es una cifra: es **que PostgreSQL no domine la factura**.

## 8. Validaciones ejecutadas

Ejecutadas el 2026-08-15. **Ninguna se declara sin haberse ejecutado.**

| # | Validación | Resultado real |
| --- | --- | --- |
| 1 | Estado de Git inicial | **Coherente.** `main` = `5583947`, `dev` = `a563de6`, ambos al día; `dev..main` **vacío**; `git diff main dev` **vacío**; sin ramas `Task/*`; árbol limpio. PR `#8` **`MERGED`**. |
| 2 | Rama `Task/005.3` | **Creada desde `dev` (`a563de6`).** Sin colisiones previas: 0 ramas locales, 0 remotas, 0 PR. **No publicada.** |
| 3 | Backend y frontend | **Verificados y sin modificar.** `git status --porcelain -b` devuelve solo la línea de rama en ambos. Sin rama `005.3`. |
| 4 | Documento canónico y diagramas | **Creado** `production-postgresql-vps.md`, 19 secciones. **5 diagramas Mermaid**: arquitectura objetivo con los tres *boundaries*, PgBouncer, topología prohibida, topología correcta, flujo de backup. |
| 5 | Qué no cambia | **Declarado** en §4 con tabla explícita: Lambda, API Gateway, S3, SSM, CloudWatch, Terraform, Floci, Cloudflare Pages y entorno local **sin cambios**. |
| 6 | PgBouncer sin números | **Cumplido.** §8.2 lista explícitamente los parámetros que **no** se fijan y de dónde deben salir. |
| 7 | PostgreSQL no público | **Presente** en §9, con las dos topologías contrastadas y §9.1 rechazando el *security through obscurity*. |
| 8 | TLS, SCRAM y mTLS | **Presentes** en §10. TLS **obligatorio** con validación; SCRAM **preferente**; mTLS **evaluable, no obligatorio**, con las cuatro preguntas que hay que resolver antes. |
| 9 | Abstracción `DATABASE_URL` | **Presente** en §11, con la tabla de destinos por entorno y la prohibición de acoplar el dominio a proveedor, IP, Floci, RDS, Docker o PgBouncer. |
| 10 | NAT Gateway y concurrencia | **Presentes** en §12.1 y §12.2. NAT **no se introduce**; *Reserved Concurrency* registrada **sin fijar `N`**. |
| 11 | Latencia y región | **Presentes** en §12.3, con **RTT medido** como criterio y la regla de no elegir un VPS lejano por ahorrar poco. |
| 12 | Backups, restore y PITR | **Presentes** en §15.1–§15.3. Las dos reglas obligatorias están escritas; PITR queda como futuro. |
| 13 | SPOF y RPO/RTO | **Presentes** en §15.4 y §15.5. SPOF aceptado, HA **no** introducida, RPO/RTO como **intención**, sin SLA. |
| 14 | Proveedor y costo | **Ningún proveedor seleccionado.** §6 nombra las opciones solo para decir que **no se elige ninguna**. §7 registra el rango con cuatro advertencias explícitas. |
| 15 | Terraform multi-provider | **Documentado** en §13, **conceptual**. **0 archivos Terraform** creados. |
| 16 | Floci | **Actualizado.** §8 de `aws-local-parity.md` reescrito: la base de datos **no pertenece al grafo AWS**, `Task/025` **no debe crear RDS**, la matriz no lo valida. **Los hallazgos históricos de §6.9 se conservan íntegros**, reetiquetados como registro de investigación. |
| 17 | D-01 | **Resolución propuesta**, no resuelta. Separa **modelo** (`Task/005.3`) de **proveedor** (`Task/029`), con tabla de lo que sigue pendiente. **D-10** amplía su alcance. **D-06 intacta.** |
| 18 | `Task/029` | **Conserva el ID `029`.** Renombrada a `Task/029-Preparar-PostgreSQL-Produccion-en-VPS` en ROADMAP, STATUS y STAGE-09, con alcance nuevo en 6 bloques y criterios de salida ampliados. **Ninguna tarea añadida ni renumerada.** |
| 19 | ADR | **ADR-007 creado**, estado **`Propuesta — pendiente de aprobación`**. Número libre confirmado. **ADR-006 sigue `Aceptada`**. ADR-003 recibe una **nota de modificación parcial** —solo su fila «Base de datos»— sin alterar su decisión. |
| 20 | Seguridad | **Ampliada.** Componentes **C-13**, **C-14**, **C-15**; nueva **§9** con reglas **V-01 a V-13**; 4 comunicaciones permitidas y 5 prohibidas nuevas; 4 superficies de ataque; principio transversal 10. |
| 21 | Riesgos | **R-29 a R-35** registrados en `STATUS.md` como **`Propuesto`**, cada uno con impacto, mitigación y tarea. Consolidan los nueve escenarios previstos. **Ninguno cerrado.** Numeración verificada: el último previo era **R-28**. **R-03** actualizado con la mitigación concreta. |
| 22 | Recuento del roadmap | **41 filas** en `ROADMAP.md` y **41** en `STATUS.md`. **41 IDs únicos**, `001`–`041`, **0 huecos**, **0 duplicados**. Avance **5 de 41 (12 %)**, ETAPA 02 **1 de 3**, `Task/006` **Pendiente**. |
| 23 | `PROJECT_INSTRUCTIONS.md` | **Actualizado.** Nueva **§16 PRODUCTION DATABASE LAW** con 12 reglas compactas y enlace al canónico; §16 anterior pasa a §17 y §17 a §18, sin pérdida de contenido. |
| 24 | Enlaces Markdown relativos | Barrido de los **20 archivos** afectados: **0 rotos**. |
| 25 | `images/Infraestructura.png` | **Intacta.** `git status --porcelain -- images/` **vacío**. Blob `eaa775f`, SHA-256 `215FF326…37420B`. No modificada, no regenerada, no movida. Reetiquetada como *arquitectura objetivo inicial, anterior a esta decisión*. |
| 26 | Búsqueda de secretos | **0 coincidencias** sobre todos los archivos nuevos y modificados. |
| 27 | Archivos Terraform | **0** en todo el workspace: `*.tf`, `*.tfvars`, `*.tfstate`, `*.hcl`. |
| 28 | Docker Compose y repos ajenos | `docker-compose.yml` **sin cambios**. `personal-blog-backend` y `personal-blog-frontend`: **0 archivos modificados**. |
| 29 | `git diff --check` y codificación | **Sin errores** de espacios en blanco. **0 secuencias de mojibake** en los archivos nuevos. |

## 9. Archivos creados y modificados

**4 creados · 16 modificados · 0 eliminados — 20 archivos.** Todos en `personal-blog-infra`.

### Creados

| Archivo | Contenido |
| --- | --- |
| `docs/architecture/production-postgresql-vps.md` | **Documento canónico.** Fuente única de la capa de datos de producción. |
| `docs/adr/ADR-007-production-postgresql-on-vps.md` | Decisión arquitectónica, estado **`Propuesta`**. |
| `docs/tasks/TASK-005.3-define-production-postgresql-vps.md` | Ficha de la tarea. |
| `docs/task-reports/TASK-005.3-report.md` | Este reporte. |

### Modificados

| Archivo | Cambio |
| --- | --- |
| `docs/architecture/open-decisions.md` | **D-01** reformulada con resolución propuesta y separación modelo/proveedor; **D-10** con alcance ampliado; índice y cabecera actualizados. |
| `docs/stages/STAGE-09-cloud-accounts.md` | `Task/029` renombrada conservando el ID, con alcance en 6 bloques, criterios de salida ampliados, 4 exclusiones y 4 riesgos nuevos. |
| `docs/stages/STAGE-08-cloud-ready.md` | RDS deja de ser destino de producción; `Task/025` no debe crear recursos RDS. |
| `docs/architecture/overview.md` | §4 con diagrama Mermaid actualizado; componente PgBouncer; nota sobre el diagrama versionado; decisión pendiente reformulada. |
| `docs/architecture/local-to-cloud-mapping.md` | Fila «Base de datos» actualizada en las tres columnas; nota de la sección; matiz de Terraform; diferencias 13, 14 y 15; RDS añadido a los servicios excluidos. |
| `docs/architecture/security-boundaries.md` | Componentes **C-13/C-14/C-15**; comunicaciones permitidas y prohibidas; superficies de ataque; principio 10; pendientes; **nueva §9** completa. |
| `docs/architecture/aws-local-parity.md` | §8 reescrito; §6.9 reetiquetado conservando los hallazgos; diagrama del Modo C; matriz de paridad; referencias. |
| `docs/architecture/software-architecture.md` | Pooling externo concretado como PgBouncer. |
| `docs/adr/ADR-003-serverless-low-cost-cloud.md` | Nota de vigencia y campo *Modificado parcialmente por*; marca en la fila «Base de datos». **Su decisión no se altera.** |
| `docs/project-management/ROADMAP.md` | `Task/029` renombrada; nota de cambio de alcance en ETAPA 09; estrategia de la capa de datos; mantenimiento `005.3`. |
| `docs/project-management/STATUS.md` | Vista rápida; sección «Mantenimiento en curso»; cierre real de `Task/005.2`; riesgos **R-29 a R-35**; **R-03** actualizado; tabla de tareas; estado de los repositorios; notas. |
| `docs/claude/PROJECT_INSTRUCTIONS.md` | Nueva **§16 PRODUCTION DATABASE LAW**; renumeración §16→§17 y §17→§18; restricción añadida. |
| `docs/product/MVP_SCOPE.md` | Decisión diferida reformulada: proveedor de VPS, no de servicio administrado. |
| `docs/runbooks/local-backup-and-recovery.md` | Fila de alcance futuro actualizada, con enlace al canónico. |
| `docs/task-reports/README.md` | Índice con `Task/005.3`. |
| `README.md` | Tabla cloud; sección «Base de datos de producción — VPS externo»; nota sobre el diagrama; RDS en servicios excluidos; árbol de `docs/`. |

> **Documentos históricos no tocados.** Las fichas y reportes de `Task/001`, `Task/002`,
> `Task/005`, `Task/005.1` y `Task/005.2` mencionan «PostgreSQL administrado» porque **era
> cierto cuando se escribieron**. Son registro histórico y **no se reescriben**.

## 10. Decisiones y su estado

| Elemento | Durante la ejecución | **Estado final tras la aprobación** |
| --- | --- | --- |
| **ADR-007** | `Propuesta` | **`Aceptada`** ✔ (2026-08-15) |
| **`production-postgresql-vps.md`** | `Propuesta` | **`Vigente`** ✔ |
| **D-01** — modelo de PostgreSQL de producción | Resolución propuesta | **`Resuelta`** en cuanto al **modelo**: autogestionado en VPS externo. **Proveedor, región y tamaño siguen pendientes en `Task/029`** |
| Riesgos **R-29** a **R-35** | `Propuesto` | **`Abierto`** — los siete. **Ninguno cerrado** |
| `security-boundaries.md` §9 y **C-13/C-14/C-15** | `Propuesta` | **`Vigente`** ✔ |
| `PROJECT_INSTRUCTIONS.md` §16 — *PRODUCTION DATABASE LAW* | `Propuesta` | **Vigente y obligatoria** ✔ |
| **D-10** — backups cloud | Abierta | **Abierta**, con alcance ampliado: el proyecto asume backup y restore completos |
| **D-06** — backend de estado de Terraform | Abierta | **Abierta.** `Task/025`. Sin tocar |
| **D-11**, **D-12** | Abiertas | **Abiertas**, sin cambios |
| **ADR-001, ADR-002, ADR-004, ADR-005, ADR-006** | Aceptadas | **Aceptadas**, sin modificar |
| **ADR-003** | Aceptada | **Aceptada y vigente.** Solo se marca que ADR-007 modifica su fila «Base de datos». Su decisión serverless y sus exclusiones **siguen intactas**, y ADR-007 **refuerza** la exclusión de NAT Gateway |
| **`Task/029`** | ID conservado | ID **`029` conservado**; nombre y alcance actualizados. **No iniciada** |

## 11. Riesgos

**7 riesgos nuevos**, **abiertos** desde la aprobación: **R-29** a **R-35**. Consolidan los nueve escenarios
previstos —SPOF, PgBouncer expuesto, backup no restaurable, pérdida de disco, software sin
parchear, agotamiento de conexiones, latencia, disco lleno y error humano— agrupando los que
comparten mitigación.

De impacto **alto**: **R-30** (superficie de ataque del VPS), **R-31** (backup no
restaurable) y **R-32** (pérdida del VPS o agotamiento de recursos).

**R-03** se actualiza con la mitigación concreta (PgBouncer + concurrencia reservada).
**Ningún riesgo se cierra.**

## 12. Problemas encontrados

| # | Problema | Resolución |
| --- | --- | --- |
| 1 | El nombre `Task/029-Seleccionar-PostgreSQL-Administrado` aparecía en **6 archivos**, y «PostgreSQL administrado» en **19**, muchos de ellos **reportes y fichas históricas**. | Se distinguió entre **documentos vigentes** —actualizados— y **registro histórico** —conservado intacto—. Reescribir un reporte de `Task/001` para que dijera «VPS» habría falsificado el historial. |
| 2 | `ADR-003` declara «Base de datos: PostgreSQL administrado» y está **Aceptada**. Cambiarla sin más contradiría el gobierno del proyecto; dejarla sin tocar habría creado una contradicción real en un documento vigente. | Se añadió una **nota de vigencia** y el campo *Modificado parcialmente por*, marcando solo esa fila. La decisión de ADR-003 **no se altera**, y ADR-007 declara explícitamente que la **refuerza**. |
| 3 | El recuento de archivos de la ficha decía **19** cuando el total real es **20** (4 creados + 16 modificados). | Corregido en las cuatro apariciones tras verificar contra `git status`: 16 líneas `M` y 4 `??`. |

Ninguna operación falló. **No se ejecutó ninguna acción destructiva.**

## 13. Confirmación explícita de límites respetados

> **Dos momentos distintos.** Hasta la aprobación no hubo commit, push, merge ni PR. El
> usuario aprobó con la expresión exacta y autorizó el flujo completo; las operaciones de Git
> posteriores son **parte del cierre autorizado**, no una excepción a los límites.

| Límite | Antes de la aprobación | Tras la aprobación |
| --- | --- | --- |
| Commits | **0** | **1**, autorizado |
| Push de la rama `Task/005.3` | **0** — no publicada | Publicada, autorizado |
| Merge de `Task/005.3` **en `dev`** | **0** | Merge `--no-ff`, autorizado |
| Pull request | **0** | **1**, `Task/005.3 → main`, **abierto** |
| **Fusión del PR hacia `main`** | — | **NO ejecutada.** Responsabilidad exclusiva del usuario |
| Modificación directa de `main` | **0** | **0** |
| Repetición del cierre de `Task/005.2` | **No** — ya estaba cerrado y normalizado | **No** |
| Alteración de historia de Git | **0** | **0** |

Límites que se cumplen **igual antes y después** del cierre:

| Límite | Cumplimiento |
| --- | --- |
| VPS contratado | **0** |
| Cuenta en proveedor de VPS | **0** |
| PostgreSQL o PgBouncer instalados | **0** |
| `docker-compose` del VPS creado, o el actual modificado | **0** |
| Cambios en `personal-blog-backend` | **0 archivos** |
| Cambios en `personal-blog-frontend` | **0 archivos** |
| `DATABASE_URL` real, SQLAlchemy o psycopg modificados | **0** |
| Secretos, certificados o claves creados | **0** |
| Puertos abiertos, firewall o usuario SSH configurados | **0** |
| `pg_dump` ejecutado o backups subidos | **0** |
| Buckets nuevos | **0** |
| Archivos Terraform | **0** en todo el workspace |
| `terraform init/plan/apply/destroy` | **No ejecutados** |
| RDS, NAT Gateway o Lambda en VPC | **0 creados** |
| Recursos AWS | **0 creados** |
| Floci instalado | **No** |
| `BACKEND_TESTING_STRATEGY.md` modificado | **No** |
| `images/Infraestructura.png` | **Intacta** — blob `eaa775f` |
| Tareas del roadmap | **41**, ninguna añadida, eliminada ni renumerada |
| `Task/029` | ID **`029` conservado** |
| Avance global | **5 de 41 (12 %)** — sin cambios |
| ETAPA 02 | **1 de 3** — sin cambios |
| `Task/006` | **Pendiente, no iniciada** |
| ADR marcado como aceptado **por decisión propia** | **No.** `ADR-007` pasó a `Aceptada` **solo** por la aprobación explícita del usuario |
| **D-01** marcada resuelta **por decisión propia** | **No.** Se resolvió **solo** con la aprobación, y **únicamente en cuanto al modelo** |
| **D-06** | **No resuelta** |
| Riesgos cerrados | **0** — **R-29** a **R-35** quedan **abiertos** |
| Secretos versionados | **0** |
| Operaciones destructivas | **0** |

## 14. Instrucciones de validación para el usuario

Ver [ficha §15](../tasks/TASK-005.3-define-production-postgresql-vps.md). Resumen mínimo:

```powershell
$env:PATH = "$env:PATH;C:\Program Files\GitHub CLI"
Set-Location C:\Users\jeffe\Downloads\Blog_Personal\personal-blog-infra

git branch --show-current                  # Task/005.3-Definir-PostgreSQL-Produccion-en-VPS
git status --porcelain -b                  # 20 archivos, sin commit
git diff --stat main dev                   # vacio
git ls-remote --heads origin "Task/*"      # vacio

code docs\architecture\production-postgresql-vps.md
code docs\adr\ADR-007-production-postgresql-on-vps.md
```

Ningún comando es destructivo.

## 15. Próxima tarea

`Task/006-Fundacion-Frontend-React` — **Pendiente, no iniciada**. No comienza hasta que el
usuario fusione el PR de `Task/005.3` y se complete la normalización `main → dev`.

## 16. Estado final

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` |
| **Estado** | **Aprobada** ✔ |
| **Fecha de aprobación** | 2026-08-15 |
| **Aprobado por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` |
| **Efecto en el avance** | **Ninguno.** Avance global **5 de 41 (12 %)**; ETAPA 02 **1 de 3**; `Task/006` **Pendiente** |

> La tarea quedó `Lista para validación` **sin commit, sin push, sin merge y sin PR**. El
> usuario la aprobó con la expresión exacta requerida por
> [WORKFLOW.md](../project-management/WORKFLOW.md) §3 y autorizó el flujo completo de cierre.
> Solo **entonces** se creó el commit, se integró la rama en `dev`, se publicó y se abrió el
> pull request. **La fusión del PR hacia `main` sigue siendo responsabilidad exclusiva del
> usuario y no se ejecutó.**
