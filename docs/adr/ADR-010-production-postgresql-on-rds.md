# ADR-010 — PostgreSQL productivo privado en Amazon RDS

| Campo | Valor |
| --- | --- |
| Estado | **Propuesta — pendiente de aprobación** |
| Fecha | 2026-09-27 |
| Tarea | `Task/028.2-Reconsiderar-PostgreSQL-Produccion-RDS` — mantenimiento; no cuenta entre las 41 |
| Reemplaza a (al aceptarse) | [ADR-007](ADR-007-production-postgresql-on-vps.md), íntegramente como dirección productiva |
| Reemplazada por | — |
| Modifica parcialmente | [ADR-003](ADR-003-serverless-low-cost-cloud.md) —fila «Base de datos», alternativa «Lambda dentro de VPC» y consecuencias de costo— y [ADR-008](ADR-008-observability-grafana-cloud-and-alloy.md) —agente de host y alcance de D-20— |
| Conserva | [ADR-006](ADR-006-local-aws-parity-with-floci.md), sus principios y sus límites de evidencia |
| Documento canónico | [production-postgresql-rds.md](../architecture/production-postgresql-rds.md) — **Propuesta** |
| Decisión asociada | **D-01** —resolución histórica conservada; su modelo se sustituye solo al aceptarse— |
| Decisiones diferidas que abre | **D-22** (red y capacidad), **D-23** (TLS, KMS y secretos) y **D-24** (canal privado), todas de `Task/029` |

> **Esta propuesta no autoriza nada.** Ni recursos AWS, ni secretos, ni cambios de *state*.
> Solo `approved: Task/028.2-Reconsiderar-PostgreSQL-Produccion-RDS` la convierte en
> **Aceptada**, y aun entonces cada recurso exige su tarea propietaria y la autorización
> explícita del usuario.

## Contexto

ADR-007 fue aceptada el 2026-08-15 bajo una premisa económica y de aprendizaje
válida entonces: PostgreSQL autogestionado en VPS externo, con PgBouncer y operación
del host. La disponibilidad de créditos AWS y la prioridad explícita del usuario de
aprender servicios administrados, VPC, IAM, KMS y recuperación cambian esa premisa.
La decisión anterior no se considera un error ni se borra su evidencia.

El usuario solicita preparar el cambio, sin crear infraestructura. Task/028 y
Task/028.1 están aprobadas e integradas; no se reabren. El siguiente número libre
verificado es 010 (existen ADR-001 a ADR-009).

## Decisión propuesta

Adoptar **Amazon RDS for PostgreSQL privado**, con Lambda conectada a la VPC,
subnets privadas, DB subnet group y security groups restrictivos. PostgreSQL nunca
será públicamente accesible. Exigir TLS con validación del servidor, cifrado en
reposo, identidad SQL mínima, backups y restore demostrado.

El diseño preferido evita NAT Gateway. RDS privado necesita conectividad VPC;
NAT solo resolvería una necesidad demostrada de salida pública IPv4. Una subnet
pública no da por sí sola acceso a Internet a Lambda. La auditoría del código
actual encuentra PostgreSQL y S3 como destinos de runtime —`PutObject`, `GetObject`,
`HeadObject`, `DeleteObject` y la sonda `ListObjectsV2`; firmar URLs es local—; la
lectura futura de SSM puede usar un endpoint específico. No encontró APIs públicas
externas llamadas por el backend. Esto hace viable el candidato sin NAT, pendiente de
prueba real en Task/032 y de inventario actualizado en Task/029.

El [documento canónico propuesto](../architecture/production-postgresql-rds.md)
define decisiones, evidencia, costos y propietarios. Task/029 decide y prepara;
no provisiona. Task/030 establece primero el backend S3 de estado conforme a D-06.
Task/031 amplía explícitamente su anterior alcance SSM/CloudWatch para incluir
red y RDS, dependiente de Task/030. Task/032 conecta Lambda; Task/036 ejecuta las
primeras migraciones; Task/038 automatiza ese canal; Task/040 valida integralmente.
No se añade una tarea 42.

## Modificaciones precisas de decisiones anteriores

| Registro | Permanece | Cambio propuesto |
| --- | --- | --- |
| ADR-007 | Texto, fecha, motivación y evidencia histórica | Se sustituye el modelo VPS/PgBouncer, su exposición TLS pública y toda operación de host por RDS privado |
| ADR-003 | Lambda ZIP, API Gateway HTTP API, S3, Cloudflare Pages, IAM y prioridad de costo controlado | Se concreta PostgreSQL administrado en RDS; Lambda pasa a VPC; se abandona cualquier supuesto de escala a cero del sistema completo o de costo fijo exclusivamente externo; VPC no implica NAT obligatorio |
| ADR-008 | CloudWatch nativo mínimo; Grafana Cloud como plano central; redacción de datos; límites de retención/costo; no autohospedar un stack | Alloy y su credencial/operación de host pierden objeto. Métricas/logs RDS van a CloudWatch; D-20 materializa integración segura hacia Grafana en Task/031. No se elimina Grafana ni se añade emisión directa desde el backend por inercia |
| ADR-006 | Un grafo modular, guardas fail-closed, aplicación independiente de Floci, AWS como autoridad final | Red/RDS se incorporarán al grafo futuro en Task/031; paridad **No evaluada**, validación real obligatoria |
| D-01 | Resolución histórica del modelo en Task/005.3 | RDS sustituirá esa resolución solo con aceptación de este ADR |
| D-16, D-17, D-18 | IDs, formulación y fechas originales | Cierre por no aplicabilidad **propuesto**, efectivo solo con aprobación; nuevas decisiones D-22 a D-24 sin reutilizar IDs |

La restricción de evitar EC2, ECS, EKS, ECR, ALB y NAT Gateway continúa. Si el
canal privado o el egress exigieran uno de esos servicios, se detiene la decisión
y se pide una modificación explícita antes de provisionar.

## Alternativas y consecuencias

- Mantener el VPS conserva control del SO, pero ya no responde a la prioridad del
  usuario y exige parcheo, certificados, agente y backups operados por el proyecto.
- RDS reduce esa operación y permite aprender la plataforma AWS. No elimina
  administración SQL, capacidad, migraciones, restauración ni responsabilidad de costo.
- Aurora, RDS Proxy, Multi-AZ, IAM DB authentication, Secrets Manager, NAT Gateway,
  *interface endpoints* concretos y funciones avanzadas de observabilidad **no quedan
  adoptados** por esta decisión: cada uno lo decide su tarea propietaria con datos.
- RDS **no es serverless ni escala a cero**: tiene costo fijo aunque no haya tráfico, y
  detenerlo no lo deja en costo cero.
- Un RDS Single-AZ sigue teniendo riesgo de interrupción. Multi-AZ no sustituye
  backup ni PITR. Los créditos no eliminan el costo bruto ni modifican D-13.

Task/029 documentará precios reales, elegibilidad y vencimiento de créditos,
riesgo después de agotarlos y compatibilidad con USD 5 AWS / USD 20 global. Si el
costo bruto no cabe, una nueva decisión explícita sobre D-13 es un gate previo a
cualquier apply de aplicación. No se promete gratuidad ni presupuesto viable aún.

## Aceptación y transición

Esta propuesta no autoriza AWS, secretos ni cambios de estado Terraform. El rol
`PersonalBlogGitHubOidcValidation` permanece intacto y sin políticas. EX-028-C7
no se extiende a RDS. Las identidades de ejecución Lambda, despliegue backend,
Terraform y migraciones/administración serán distintas.

Solo `approved: Task/028.2-Reconsiderar-PostgreSQL-Produccion-RDS` permite aceptar
este ADR, marcar ADR-007 reemplazada, cerrar D-16–D-18 por no aplicabilidad y
declarar vigente el nuevo canónico. Hasta entonces existe una sola **dirección
propuesta**, RDS; la instrucción actual del usuario suspende nuevas ejecuciones
del modelo anterior. Task/029 sigue **Pendiente**.

## Referencias

- [Canónico RDS y fuentes AWS verificadas](../architecture/production-postgresql-rds.md).
- [Registro de decisiones](../architecture/open-decisions.md).
- [Ficha de mantenimiento](../tasks/TASK-028.2-reconsider-production-postgresql-rds.md).
- [Historia del modelo sustituido](../architecture/production-postgresql-vps.md).
