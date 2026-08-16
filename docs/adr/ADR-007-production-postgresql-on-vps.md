# ADR-007 — PostgreSQL de producción en VPS externo

| Campo | Valor |
| --- | --- |
| **Estado** | **Aceptada** ✔ |
| **Fecha** | 2026-08-15 |
| **Fecha de aceptación** | 2026-08-15 |
| **Aceptada por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` |
| **Tarea** | `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` (mantenimiento; **no cuenta** en las 41 tareas) |
| **Reemplaza a** | — |
| **Reemplazada por** | — |
| **Modifica parcialmente** | [ADR-003](ADR-003-serverless-low-cost-cloud.md) — **solo la fila «Base de datos»**. El resto de ADR-003 sigue íntegro y vigente |
| **Documento canónico** | [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) |
| **Decisión diferida** | **D-01** — **Resuelta** en cuanto al **modelo**; proveedor pendiente de `Task/029` |

> **Aceptada** el 2026-08-15, al aprobar el usuario `Task/005.3` con la expresión exacta
> requerida por [WORKFLOW.md](../project-management/WORKFLOW.md). Sus reglas son **vigentes
> y de cumplimiento obligatorio** desde esta fecha.

---

## Contexto

El blog es un proyecto personal con tráfico bajo e irregular, un solo operador y el **costo
como restricción principal de diseño**. [ADR-003](ADR-003-serverless-low-cost-cloud.md)
adoptó por eso una arquitectura serverless de escalado a cero, y dejó registrada su única
excepción:

> «La base de datos administrada es el **único componente con costo fijo** de la
> arquitectura. Es una excepción consciente: no existe una alternativa relacional
> gestionada que escale a cero y sea confiable para contenido publicado.»

Esa excepción se aceptó sin datos concretos. Al acercarse la ETAPA 09 aparecen dos
problemas con ella:

1. **Costo desproporcionado.** En una arquitectura donde API Gateway, Lambda, S3, SSM y
   CloudWatch cuestan prácticamente cero en reposo, una base de datos administrada pasa a
   **dominar la factura mensual** y a costar más que todo lo demás junto — para servir un
   blog con tráfico bajo.
2. **Pérdida del aprendizaje operacional.** El proyecto es también un ejercicio de
   formación. Pagar por que un proveedor gestione el sistema operativo, PostgreSQL, la
   seguridad, los backups y la recuperación **elimina justo la parte que se quiere
   aprender**.

Al mismo tiempo, **no se quiere abandonar AWS ni la arquitectura serverless**: aprender
Lambda, API Gateway, IAM y Terraform es un objetivo explícito del proyecto y el motivo de
[ADR-006](ADR-006-local-aws-parity-with-floci.md). Mover FastAPI a un servidor propio
resolvería el costo destruyendo el objetivo.

La pregunta, por tanto, no es *«¿AWS o VPS?»* sino *«¿qué parte concreta de la arquitectura
justifica un costo fijo?»*.

## Decisión

> **PostgreSQL de producción será autogestionado en un VPS económico, independiente de AWS,
> mientras el backend FastAPI permanece en AWS Lambda.**

El cambio está **acotado a la capa de datos**. Con estos límites, que forman parte de la
decisión:

| # | Límite |
| --- | --- |
| 1 | **FastAPI permanece en AWS Lambda.** API Gateway, IAM, S3, SSM y CloudWatch permanecen en AWS sin cambios. |
| 2 | **PgBouncer es el punto de entrada** de la capa de datos: el **único endpoint de esa capa que la aplicación puede alcanzar desde fuera del VPS**. El acceso administrativo por **SSH** es un canal separado, ajeno a la capa de datos. |
| 3 | **PostgreSQL nunca se expone directamente a Internet.** Acepta solo conexiones internas del VPS. |
| 4 | **El tramo `Lambda → PgBouncer` exige TLS** con validación correcta del certificado del servidor. |
| 5 | **SCRAM-SHA-256** es el mecanismo de autenticación preferente cuando la implementación lo permita. |
| 6 | **El código de aplicación solo depende de `DATABASE_URL`.** No conoce el proveedor, la IP ni PgBouncer. |
| 7 | **La Lambda permanece fuera de VPC**, conservando su salida a Internet gestionada. **No se introduce NAT Gateway** por esta decisión. |
| 8 | **Los backups deben salir del VPS**, y un backup no está validado hasta haberse restaurado. |
| 9 | **El proveedor, la región y el dimensionamiento se deciden en `Task/029`**, con precios actuales. |
| 10 | **Se acepta conscientemente un *single point of failure*** en la primera versión productiva. |

Estrategia completa —arquitectura, *boundaries*, PgBouncer, TLS, secretos, concurrencia,
latencia, backups, restore, PITR, RPO/RTO, Terraform multi-provider y criterios de
reconsideración— en el documento canónico
[production-postgresql-vps.md](../architecture/production-postgresql-vps.md). Este ADR
registra la **decisión**; el documento registra **cómo se aplica**.

### Relación con ADR-003

Este ADR **no reemplaza** a [ADR-003](ADR-003-serverless-low-cost-cloud.md). Modifica
**una sola fila** de su tabla de decisión —«Base de datos: PostgreSQL administrado»— y
**refuerza** su principio rector: *el costo es una restricción de diseño*. Todo lo demás de
ADR-003 sigue intacto, incluida su lista de servicios excluidos, que este ADR **respeta**:
no se introduce NAT Gateway, ni EC2, ni ECS, ni ALB en la arquitectura de AWS.

### Qué NO decide este ADR

- **No** selecciona proveedor de VPS. → `Task/029`
- **No** fija región, tamaño, CPU, RAM ni almacenamiento. → `Task/029`
- **No** fija `pool_size`, `max_client_conn`, `max_connections` ni concurrencia reservada.
  → `Task/029`, `Task/032` (**D-12**)
- **No** decide si se adopta mTLS. → `Task/029`
- **No** decide frecuencia ni retención de backups. → `Task/029` (**D-10**)
- **No** decide si se implementa PITR. → `Task/029`
- **No** resuelve **D-06**, el backend de estado de Terraform. → `Task/025`
- **No** añade, elimina ni renumera tareas del roadmap: siguen siendo **41**.

## Alternativas consideradas

| # | Alternativa | Evaluación |
| --- | --- | --- |
| **A** | **AWS RDS / PostgreSQL administrado en AWS.** | **Ventajas:** operación administrada, backups automáticos, mantenimiento y parcheo incluidos, integración nativa con IAM, VPC y CloudWatch, y un único proveedor. **Desventajas para este proyecto:** es el mayor costo fijo de la arquitectura, desproporcionado frente al tráfico esperado; elimina el aprendizaje operacional buscado; y una instancia privada obliga a **conectar la Lambda a la VPC**, lo que tiene una consecuencia de red que hay que planificar (ver nota siguiente). **Descartada por costo**, no por calidad técnica. |
| **B** | **PostgreSQL serverless o administrado externo a AWS.** | **Ventajas:** operación reducida, posible costo bajo o plan gratuito, escalado a cero en algunos proveedores. **Desventajas:** menor control sobre versión y *tuning*; dependencia fuerte de un proveedor y de su modelo de precios, que puede cambiar; menos aprendizaje de host y de base de datos; y planes gratuitos que suelen traer límites poco compatibles con producción. **No seleccionada**, pero es la **primera alternativa a reevaluar** si aplica un criterio de reconsideración. |
| **C** | **VPS autogestionado con PostgreSQL y PgBouncer.** | **Elegida.** Costo pequeño y predecible, control total, aprendizaje operacional real, y **conserva íntegra la arquitectura AWS serverless**. A cambio, el proyecto asume sistema operativo, parcheo, seguridad, backups y recuperación. |
| **D** | **Mover también FastAPI al VPS.** | Sería el óptimo puro de costo: un solo servidor, sin AWS. **No seleccionada.** Destruye el objetivo declarado del proyecto —aprender AWS, serverless y Terraform— y anula el trabajo de [ADR-006](ADR-006-local-aws-parity-with-floci.md). El usuario quiere conservar Lambda y API Gateway; el costo de AWS en reposo es prácticamente cero, así que mover el backend no ahorraría casi nada y costaría el aprendizaje entero. |

### Precisión sobre RDS, VPC y NAT Gateway

Conviene ser exacto, porque es fácil atribuir a RDS un costo que no le corresponde.
Documentación oficial de AWS, consultada el 2026-08-15:

| # | Hecho |
| --- | --- |
| 1 | Un **RDS privado implica conectar la Lambda a la VPC** correspondiente, adjuntándola a las subredes privadas donde vive la instancia. |
| 2 | **NAT Gateway NO es necesario** para que esa Lambda alcance RDS **dentro** de la VPC. El tráfico no sale a Internet. |
| 3 | Sin embargo, **una Lambda conectada a una VPC pierde el acceso a Internet gestionado por defecto**: *«By default, Lambda functions have access to the public internet. When you attach your function to a VPC, it can only access resources available within that VPC.»* |
| 4 | **Si esa Lambda necesita además salida IPv4 a Internet**, hay que proporcionarle un mecanismo de *egress*. **NAT Gateway es una opción**, no la única ni una consecuencia automática: existen *egress-only internet gateway* para IPv6 y **VPC endpoints** para servicios AWS. Conectar la función a una subred pública **no** le da acceso a Internet. |

**Conclusión honesta:** el costo de NAT Gateway **no es inherente a RDS**. Aparece solo si la
función, ya dentro de la VPC, necesita salida a Internet y esa salida se resuelve con NAT.
En este proyecto la Lambda necesitaría alcanzar servicios AWS —que pueden resolverse con VPC
endpoints— y, según el diseño final, posiblemente destinos externos.

**Esta precisión no cambia la decisión.** La alternativa A se descarta por **costo del propio
servicio administrado y por aprendizaje operacional**, no por NAT Gateway. Lo que sí queda
registrado es que adoptar RDS **exigiría diseñar la conectividad de red de la Lambda**, un
trabajo que la opción elegida no requiere.

### Por qué C sobre A

La comparación decisiva no es «administrado contra autogestionado» en abstracto, sino
**qué se paga y qué se obtiene en este proyecto concreto**:

| Criterio | A — Administrado | C — VPS autogestionado |
| --- | --- | --- |
| Costo mensual del servicio | El mayor de la arquitectura | Pequeño y predecible |
| Diseño de red que exige | Conectar la Lambda a la VPC y resolver su *egress* | Ninguno: la Lambda sigue fuera de VPC |
| Aprendizaje operacional | Bajo | **Alto — es un objetivo del proyecto** |
| Control de versión y *tuning* | Limitado | Total |
| Operación a cargo del proyecto | Mínima | **Completa** |
| Disponibilidad de partida | Mayor | **SPOF aceptado** |

Para un blog personal, la disponibilidad que ofrece un servicio administrado **no compensa
su costo fijo**, y la operación que exige un VPS **es parte del valor buscado**, no un
efecto colateral.

## Consecuencias

### Positivas

- **Costo menor y, sobre todo, predecible.** PostgreSQL deja de dominar la factura.
- **La arquitectura AWS serverless se conserva íntegra**: Lambda, API Gateway, IAM, S3, SSM
  y CloudWatch, y con ellos [ADR-006](ADR-006-local-aws-parity-with-floci.md).
- **Aprendizaje real** de Linux, PostgreSQL, *hardening*, TLS, PgBouncer, backups y
  recuperación.
- **Control total** sobre versión, configuración y *tuning* de la base de datos.
- **Terraform se amplía a multi-provider** (AWS + Cloudflare + VPS), lo que es más
  representativo de infraestructura real.
- **La Lambda no necesita entrar en una VPC**, así que no hay que diseñar su *egress* ni
  incurrir en el costo fijo de un NAT Gateway — coherente con
  [ADR-003](ADR-003-serverless-low-cost-cloud.md).
- **Reversible sin tocar código**: la aplicación solo conoce `DATABASE_URL`.

### Negativas

- **Operación propia**: sistema operativo, parcheo, actualizaciones y mantenimiento pasan a
  ser trabajo del proyecto.
- ***Single point of failure*** en la primera versión productiva.
- **Backups y restore son responsabilidad completa del proyecto**, incluida la prueba de
  restauración.
- **Nueva superficie de ataque**: un host expuesto a Internet, con SSH y un servicio de base
  de datos delante.
- **Latencia**: cada consulta paga el RTT `Lambda ↔ VPS`, que ya no es intra-región.
- **Observabilidad propia**: en la arquitectura propuesta, **CloudWatch no observa el VPS por
  defecto**. Hacerlo requeriría una integración o agente explícito, cuya decisión **no
  corresponde a `Task/005.3`**.
- **Riesgo operacional humano**: un error de configuración puede exponer datos o perderlos.
- **Consume tiempo.** Es un costo real, aunque se acepte como aprendizaje.

### Neutras

- El backend **no cambia**: sigue hablando con PostgreSQL por `DATABASE_URL`. Este ADR no
  obliga a modificar una línea de `personal-blog-backend`.
- El entorno local **no cambia**: PostgreSQL en Docker sigue siendo el destino de
  desarrollo.

## Riesgos

**R-29** a **R-35** —siete en total—, definidos en
[production-postgresql-vps.md](../architecture/production-postgresql-vps.md) §16 y
registrados en [STATUS.md](../project-management/STATUS.md): **R-29** *single point of
failure*, **R-30** superficie de ataque del VPS, **R-31** backup no restaurable, **R-32**
pérdida del VPS o agotamiento de recursos, **R-33** agotamiento de conexiones, **R-34**
latencia `Lambda ↔ VPS` y **R-35** error humano de operación.

Los de impacto alto: **R-30**, **R-31** y **R-32**.

## Criterios para reconsiderar

Esta decisión se revisa si: el tráfico aumenta sustancialmente · se requiere un SLA que un
solo VPS no sostiene · la alta disponibilidad se vuelve necesaria · el costo del servicio
administrado deja de ser relevante · el mantenimiento manual consume demasiado tiempo ·
aparecen requisitos regulatorios · la recuperación exigida se vuelve más estricta · el costo
total de operar el VPS supera su beneficio.

Detalle en
[production-postgresql-vps.md](../architecture/production-postgresql-vps.md) §17.

Revertir la decisión **no exige reescribir la aplicación**: es un cambio de `DATABASE_URL`
y de infraestructura. Sí exigiría un ADR nuevo que reemplace a este.

## Cumplimiento

- Ninguna tarea puede **exponer PostgreSQL directamente a Internet**.
- Ninguna tarea puede conectar `Lambda → PgBouncer` **sin TLS** en producción.
- Ninguna tarea puede **acoplar el código de aplicación** al proveedor, a la IP o a
  PgBouncer: la abstracción es `DATABASE_URL`.
- Ninguna tarea puede **versionar credenciales** de la base de datos de producción.
- Ninguna tarea puede conectar la Lambda a una **VPC** ni introducir **NAT Gateway** por esta
  decisión sin un ADR que lo justifique con un requisito real.
- Ninguna tarea puede afirmar que **NAT Gateway sea una consecuencia inherente de RDS**: no
  lo es.
- Ninguna tarea puede dar por válido un backup **que no se haya restaurado**.
- `Task/025` **no debe crear recursos RDS** para imitar producción.

## Referencias

- [production-postgresql-vps.md](../architecture/production-postgresql-vps.md) — documento canónico
- [ADR-001 — Local-first](ADR-001-local-first.md)
- [ADR-003 — Nube serverless de bajo costo](ADR-003-serverless-low-cost-cloud.md)
- [ADR-006 — Paridad AWS local con Floci](ADR-006-local-aws-parity-with-floci.md)
- [Decisiones diferidas](../architecture/open-decisions.md) — **D-01**, **D-10**, **D-12**
- [Límites de seguridad](../architecture/security-boundaries.md)
- [ETAPA 09 — Cuentas y Seguridad Cloud](../stages/STAGE-09-cloud-accounts.md)

**Documentación oficial de AWS, consultada el 2026-08-15** (base de la precisión sobre RDS,
VPC y NAT Gateway):

- *Giving Lambda functions access to resources in an Amazon VPC* —
  `https://docs.aws.amazon.com/lambda/latest/dg/foundation-networking.html`
- *Enable internet access for VPC-connected Lambda functions* —
  `https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc-internet.html`
