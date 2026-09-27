# Correspondencia local → nube

**Última actualización:** 2026-08-23 (`Task/006.2` — observabilidad de producción y papel
de Docker, **aprobada** y **vigente**. La capa de datos en VPS de `Task/005.3` sigue
**aprobada** y **vigente**). **Enmienda propuesta:** 2026-09-27 (`Task/028.2` — capa de
datos en RDS privado, **pendiente de aprobación**)

> Consistente con la arquitectura definida en `Task/002`. Ver
> [software-architecture.md](software-architecture.md) para la organización interna del
> código y [security-boundaries.md](security-boundaries.md) para las comunicaciones
> permitidas entre componentes.

Cada responsabilidad del sistema tiene una implementación local y una implementación
prevista en la nube. El objetivo es que **el código de aplicación no cambie** al pasar
de una a otra: lo que cambia es la configuración y el adaptador.

Desde `Task/005.2` (**aprobada** el 2026-08-15) existe además un **tercer entorno**, el
**AWS Local Parity Lab**: un laboratorio local de infraestructura que permite ejecutar la
misma definición de Terraform contra un emulador AWS, sin cuenta y sin costo. **No
sustituye al entorno local de desarrollo** y **no es autoridad sobre el comportamiento de
AWS**. Estrategia completa y límites de fidelidad:
[aws-local-parity.md](aws-local-parity.md) — **Vigente** ·
[ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) — **Aceptada**.

Desde `Task/005.3` cambia además el destino de la **capa de datos de producción**: deja de
ser un PostgreSQL administrado y pasa a ser **PostgreSQL autogestionado en un VPS externo,
con PgBouncer delante**, mientras el backend permanece en AWS Lambda. **Aprobada** el 2026-08-15. Estrategia:
[production-postgresql-vps.md](production-postgresql-vps.md) ·
[ADR-007](../adr/ADR-007-production-postgresql-on-vps.md).

> **Enmienda propuesta por `Task/028.2` (2026-09-27), pendiente de aprobación.**
> [ADR-010](../adr/ADR-010-production-postgresql-on-rds.md) propone que la capa de datos
> de producción vuelva a ser **administrada**: **Amazon RDS for PostgreSQL privado**, con la
> Lambda conectada a la VPC y **sin NAT Gateway** por defecto. La aplicación **sigue sin
> enterarse**: solo conoce `DATABASE_URL`. Canónico propuesto:
> [production-postgresql-rds.md](production-postgresql-rds.md). Las filas y notas afectadas
> se marcan abajo; el texto del modelo VPS se conserva como historia.

---

## Tabla de correspondencia

| Responsabilidad | Local (desarrollo) | AWS Local Parity Lab | Nube inicial |
| --- | --- | --- | --- |
| Frontend | React + Vite | No aplica | Cloudflare Pages |
| Backend | FastAPI local/Docker | Lambda emulada ejecutando el mismo FastAPI | AWS Lambda |
| Entrada HTTP | Reverse proxy | API Gateway v2 emulado | API Gateway HTTP API |
| Base de datos | PostgreSQL Docker | **Local**, cuando la prueba lo requiera — no pertenece al grafo AWS. *(Propuesta: RDS entraría en el grafo en `Task/031`, **No evaluado** en el laboratorio)* | **PgBouncer → PostgreSQL en VPS externo**. *(Propuesta: **Amazon RDS for PostgreSQL privado**)* |
| Red *(fila añadida por la enmienda propuesta)* | Red de Docker local | **No evaluada** | **VPC, subnets privadas, security groups** y rutas a S3/SSM (**D-22**) |
| Archivos | MinIO | S3 emulado | Amazon S3 |
| Administración Docker | Portainer | No aplica | No se despliega |
| Configuración | `.env` | SSM emulado (**sin cifrado real**) | SSM Parameter Store |
| Logs | Docker y Portainer | CloudWatch Logs emulado | **CloudWatch mínimo** (AWS) + **Grafana Cloud** (VPS, vía Alloy). *(Propuesta: CloudWatch —Lambda, API y RDS— + Grafana Cloud vía **D-20**)* |
| Métricas y alertas | No aplica | No aplica | **CloudWatch mínimo** (AWS) + **Grafana Cloud** como plano central |
| Agente de telemetría | No aplica | No aplica | **Grafana Alloy** en el VPS. *(Propuesta: **ninguno**; métricas nativas de RDS)* |
| Supervisión operativa | **Portainer** | No aplica | **Grafana Cloud.** Portainer **no se despliega** |
| Permisos | No aplica | IAM emulado — **crea, no autoriza** | IAM |
| Ejecución | Docker Compose | Emulador AWS local | Serverless + VPS acotado a la capa de datos. *(Propuesta: serverless + **RDS administrado**, con costo fijo)* |
| Papel de Docker | **Runtime del entorno de desarrollo** | Runtime del emulador y de la Lambda emulada | **No es runtime de producción.** Solo *build*/test si hace falta |
| Secretos del host | No aplica | No aplica | **Cifrados en el VPS**, clave fuera del repositorio (**D-17**). *(Propuesta: sin host; credenciales de la base de datos y KMS según **D-23**)* |
| Infraestructura | Docker Compose | **Terraform** (misma definición) | **Terraform** (misma definición) |
| Integración continua | GitHub Actions | GitHub Actions + emulador efímero (`Task/039`) | GitHub Actions |
| Despliegue | No aplica todavía | `apply`/`destroy` local (`Task/025`) | GitHub Actions + Terraform |

> La estrategia del laboratorio está **aprobada**, pero **nada de esa columna está probado
> todavía**: se implementa en `Task/025`. El grado real de paridad de cada fila se registra
> en la [matriz de paridad](aws-local-parity.md) §7, que hoy está entera en `No evaluada`.
>
> *(Corrección de drift de `Task/028.2`, 2026-09-27: esta nota quedó escrita antes de
> `Task/025`. Desde su aprobación, el 2026-09-14, el grafo de 21 recursos **tiene evidencia
> local** en la matriz de paridad, siempre como hipótesis hasta la ETAPA 10. Las filas nuevas
> de red y RDS de la enmienda propuesta están **No evaluadas**.)*

---

## Notas por responsabilidad

### Frontend
Mismo build de Vite en ambos entornos. En local lo sirve el reverse proxy; en la nube,
Cloudflare Pages sirve los estáticos. La URL del API se inyecta como variable de entorno
en tiempo de build.

### Backend
El mismo código FastAPI se ejecuta como proceso ASGI en local y bajo un adaptador Lambda
en la nube (`Task/023`). Restricción de diseño: sin estado en memoria entre peticiones y
sin trabajos en segundo plano de larga duración.

### Entrada HTTP
El reverse proxy local reproduce el enrutado que hará API Gateway (rutas de sitio y de
API, CORS). API Gateway añade throttling y TLS gestionado.

### Base de datos
El mismo motor PostgreSQL en ambos lados. Diferencia crítica: desde Lambda las
conexiones son efímeras y numerosas, lo que exige pooling o un proxy de conexiones.

**Cambio aprobado en `Task/005.3` (2026-08-15):** la base de datos de producción **no será un servicio
administrado**, sino **PostgreSQL autogestionado en un VPS externo**, con **PgBouncer** como
único endpoint externo de la capa de datos y **PostgreSQL no expuesto a Internet**. El tramo `Lambda → PgBouncer`
va cifrado con TLS.

```
AWS Lambda ──TLS──► PgBouncer ──red interna del VPS──► PostgreSQL
```

La aplicación **no se entera**: sigue dependiendo únicamente de `DATABASE_URL`. El proveedor,
la región y el dimensionamiento se deciden en `Task/029`. Detalle completo:
[production-postgresql-vps.md](production-postgresql-vps.md).

**Enmienda propuesta en `Task/028.2` (2026-09-27), pendiente de aprobación:** la base de
datos de producción pasa a **Amazon RDS for PostgreSQL privado**. La Lambda **se conecta a
la VPC** y llega a RDS con TLS verificado, solo de security group a security group.

```
AWS Lambda (en VPC) ──TLS verificado · SG → SG──► RDS for PostgreSQL (subnets privadas)
```

La aplicación sigue sin enterarse: `DATABASE_URL` y nada más. Lo que la enmienda **no**
cambia es la diferencia crítica de arriba: las conexiones siguen siendo efímeras y
numerosas; el pool por proceso y la concurrencia se derivan y se miden (**D-12**), y RDS
Proxy es evaluable, no obligatorio. Región, clase, disponibilidad y red se deciden en
`Task/029` (**D-22**). Detalle:
[production-postgresql-rds.md](production-postgresql-rds.md).

### Archivos
MinIO expone la API de S3, así que el mismo cliente sirve para ambos. Todo acceso pasa
por la interfaz `ObjectStorage` (`Task/010`), con una implementación por entorno.
En ambos casos el acceso a archivos privados usa URLs prefirmadas.

**Reparto de responsabilidades** (aclarado en `Task/005.5`):

| Qué | Owner |
| --- | --- |
| Interfaz `ObjectStorage`, `MinIOStorage` y **el código de `S3Storage`**, con pruebas de contrato comunes a ambas implementaciones | **`Task/010`** — sin AWS real |
| Bucket, políticas, CORS, *lifecycle*, expiración de URLs prefirmadas y **validación de `S3Storage` contra S3 real** | **`Task/030`** |
| *Wiring* productivo: variables/SSM que hacen que la Lambda use `S3Storage` | **`Task/032`** |

**Regla vigente:** la base de datos y el Markdown persisten **la clave del objeto**, nunca
una URL prefirmada — que expira. La URL de acceso se genera en el momento de servir.

### Administración Docker
Portainer CE es exclusivamente local: sirve para inspeccionar contenedores, logs,
healthchecks, volúmenes y redes durante el desarrollo y la validación.
**No se despliega en la nube** — allí no hay contenedores propios que administrar.

### Configuración
En local, `.env` (ignorado por Git) más un `.env.example` con valores ficticios.
En la nube, SSM Parameter Store; los valores sensibles como `SecureString`. El código
lee siempre variables de entorno: quién las provee es indiferente.

### Logs y observabilidad
En local, salida estándar capturada por Docker y visible en Portainer. En ambos entornos el
formato es JSON con correlation ID (`Task/017`).

**Ampliado en `Task/006.2`** (**aprobada** el 2026-08-23)**.** La observabilidad de producción tiene **dos
planos**, porque producción vive en **dos sitios**:

| Plano | Qué observa | Cómo |
| --- | --- | --- |
| **CloudWatch mínimo** | Lambda y API Gateway | Nativo de AWS. Retención **corta y explícita** (**D-11**) |
| **Grafana Cloud** | El **VPS** y sus servicios; a futuro también CloudWatch | **Grafana Alloy** en el host empuja logs, métricas y telemetría |

**CloudWatch no observa el VPS** —un host externo no aparece allí por defecto— y **no se
adopta CloudWatch Agent por omisión**. **No se autohospedan Grafana, Prometheus ni Loki en
el VPS**: sus recursos son de PostgreSQL. La integración `CloudWatch → Grafana Cloud` está
**contemplada y no implementada** (**D-20**, `Task/031`).

*(Enmienda propuesta por `Task/028.2`: con RDS, **toda** la producción observada vive en
AWS. CloudWatch recibe las métricas nativas de RDS y los logs que se seleccionen, y
Grafana Cloud recibe datos **solo** por la integración **D-20**, que `Task/031` decide **e
implementa**. Sin agente de host.)*

**La aplicación no se acopla a ningún destino** (**O-09**): emite JSON por `stdout` y quien
lo recoge es una decisión de infraestructura. Detalle:
[target-production-architecture.md](target-production-architecture.md) §10–§13 ·
[ADR-008](../adr/ADR-008-observability-grafana-cloud-and-alloy.md) — **Aceptada**.

### Ejecución y papel de Docker
Docker Compose local frente a ejecución serverless en la nube. Implicación: no hay procesos
residentes en el plano de aplicación; toda tarea periódica debe modelarse como invocación.

**Aclarado en `Task/006.2`** (**aprobada** el 2026-08-23)**.** **Docker sí se utiliza** en este proyecto —
desarrollo local, integración local (`Task/007`), *build* y test reproducibles, y el
laboratorio de paridad. Lo que **no** es, es **runtime obligatorio de producción**: el
frontend son estáticos en Cloudflare Pages, el backend es un **ZIP** en Lambda —**ECR sigue
excluido**— y en el VPS solo vive la capa de datos, que puede usar Docker o no (decisión de
`Task/029`, con el mínimo privilegio razonable). **Portainer no llega a producción.**
*(Con la enmienda propuesta no hay VPS: RDS es administrado y la pregunta sobre Docker en
el host pierde objeto.)*

### Infraestructura
Docker Compose describe el entorno local de aplicación; Terraform describe el cloud. No se
comparte definición entre ambos, pero sí la nomenclatura de recursos y variables.

**Matiz añadido en `Task/005.2`** (**aprobada**)**:** entre esos dos mundos se añade el
*AWS Local Parity Lab*, donde **Terraform sí es la misma definición** que la de producción, apuntada a un
destino local. Regla de portabilidad: **una sola definición, un solo grafo de recursos**;
las diferencias se confinan a provider, endpoints, credenciales, región, backend, nombres,
dominios y capacidad ([aws-local-parity.md](aws-local-parity.md) §4).

**Matiz añadido en `Task/005.3`:** con PostgreSQL en un VPS externo, Terraform pasa a ser
conceptualmente **multi-provider** —AWS + Cloudflare + VPS— sin dejar de ser una sola fuente
de verdad. Estructura y límites:
[production-postgresql-vps.md](production-postgresql-vps.md) §13.

**Enmienda propuesta en `Task/028.2`:** sin VPS, los providers vuelven a ser **AWS y
Cloudflare**. Red y RDS entran en el **mismo grafo** en `Task/031`, sin duplicar módulos
local/cloud.

### Integración continua
GitHub Actions en ambos casos, con los mismos workflows de calidad. El despliegue se
añade en la Etapa 11, usando OIDC para acceder a AWS sin credenciales permanentes.

---

## Diferencias que exigen atención explícita

| # | Diferencia | Dónde se aborda |
| --- | --- | --- |
| 1 | Lambda no mantiene estado ni conexiones entre invocaciones. | `Task/023`, `Task/029` |
| 2 | Arranque en frío afecta la latencia de la primera petición. | `Task/024`, `Task/032` |
| 3 | Límite de tamaño del artefacto de Lambda. | `Task/024` |
| 4 | En local no hay TLS real; en la nube todo es HTTPS. | `Task/035`, `Task/040` |
| 5 | S3 cobra por almacenamiento y transferencia; MinIO no. | `Task/030`, `Task/041` |
| 6 | CloudWatch cobra por ingesta y retención de logs. | `Task/031`, `Task/041` |
| 7 | El límite de conexiones de PostgreSQL es finito y en una máquina económica es bajo: **PgBouncer** y la concurrencia reservada de Lambda lo acotan. | `Task/029`, `Task/032` |
| 8 | No hay equivalente de Portainer en producción. | **CloudWatch mínimo** para AWS (`Task/031`) y **Grafana Cloud** como plano de supervisión, alimentado por **Alloy** desde el VPS (`Task/029`) |
| 9 | **El laboratorio local no aplica políticas IAM**: un rol puede validarse en local y ser incorrecto en AWS. | `Task/028`, `Task/032` — **AWS-only** |
| 10 | **`SecureString` no se cifra** en el SSM emulado. | `Task/031` — ningún secreto real en el laboratorio |
| 11 | El arranque en frío del laboratorio **no es comparable** con el de AWS. | `Task/032` (**D-12**) — medir solo en AWS real |
| 12 | El laboratorio no emula dominios personalizados ni TLS gestionado. | `Task/035`, `Task/040` — **AWS-only** |
| 13 | **La base de datos de producción no está en AWS**: el laboratorio de paridad no la reproduce y, en la arquitectura vigente, **CloudWatch no observa el VPS por defecto** —requeriría una integración o agente explícito, **no decidido**. `Task/017` es observabilidad **local** y **no** es owner de esto; `Task/031` es **solo AWS**. | `Task/029` (baseline del VPS) · `Task/040` (validación) |
| 14 | **La base de datos deja de estar en la misma región que el cómputo**: cada consulta paga el RTT `Lambda ↔ VPS`. | `Task/029` — RTT **medido**, no estimado |
| 15 | En producción, **la operación del host es del proyecto**: parcheo, backups y restore ya no los resuelve un proveedor. | `Task/029`, `Task/026` |

**Enmienda propuesta por `Task/028.2`, pendiente de aprobación.** Las filas **7**, **8**,
**13**, **14** y **15** describen el VPS. Con RDS quedan así, y se añaden tres diferencias
nuevas:

| # | Diferencia propuesta | Dónde se aborda |
| --- | --- | --- |
| 7 | El límite de conexiones de RDS es finito y depende de la clase: el pool por proceso, la concurrencia reservada y, **si la evidencia lo justifica**, RDS Proxy lo acotan | `Task/029` (**D-12** preliminar), `Task/032` (medición), `Task/040` (carga) |
| 8 | No hay equivalente de Portainer en producción | **CloudWatch mínimo** con señales de Lambda, API y RDS (`Task/031`–`Task/033`) y **Grafana Cloud** vía **D-20** (`Task/031`) |
| 13 | La base de datos **sí** está en AWS, pero el laboratorio **no acredita** su red, IAM, KMS, backups ni *failover*: son **AWS-only** a efectos de evidencia | `Task/031` · `Task/040` |
| 14 | La latencia `Lambda ↔ RDS` es intra-región, pero **se mide**, no se supone | `Task/032`, `Task/040` |
| 15 | AWS opera el host de RDS; el proyecto sigue operando versión, *parameter group*, capacidad, usuarios SQL, KMS, restore y DR | `Task/029` (decide), `Task/031` (runbooks), `Task/040` |
| 16 | **Una Lambda en VPC no tiene salida a Internet por defecto**: S3 y SSM necesitan rutas específicas; NAT solo con necesidad demostrada y decisión explícita | `Task/029` (**D-22**), `Task/032` (tráfico real) |
| 17 | **RDS tiene costo fijo** aunque no haya tráfico; los créditos AWS reducen el desembolso, no el costo bruto | `Task/029` (frente a **D-13**), `Task/041` |
| 18 | **PITR restaura en una instancia nueva**: el *endpoint* cambia y hay que revisar security groups, *parameter group* y KMS | `Task/031` (restore sintético), `Task/040` |

---

## Servicios excluidos de la arquitectura cloud

EC2, ECR, ECS Fargate, EKS, Application Load Balancer, NAT Gateway y Portainer en
producción. Motivo: costo fijo mensual y complejidad operativa injustificados para un
blog personal. Ver [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md).

**Añadido en `Task/005.3` (aprobada):** también queda excluido **AWS RDS** como destino de
la base de datos de producción, por el mismo motivo —costo fijo desproporcionado para el
tráfico esperado—. La exclusión de **NAT Gateway** se refuerza: no se introduce para
conectar Lambda con PostgreSQL. Ver
[ADR-007](../adr/ADR-007-production-postgresql-on-vps.md).

**Enmienda propuesta en `Task/028.2` (2026-09-27), pendiente de aprobación:**
[ADR-010](../adr/ADR-010-production-postgresql-on-rds.md) propone **retirar RDS de esta
lista**. La premisa cambió —créditos AWS disponibles y prioridad de aprender servicios
administrados—, pero **el costo fijo no desaparece** y se evalúa frente a **D-13**. **NAT
Gateway sigue excluido**: la Lambda llega a RDS por la VPC, y S3/SSM por rutas específicas.
El resto de la lista no cambia.
