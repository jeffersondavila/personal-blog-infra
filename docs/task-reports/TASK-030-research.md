# TASK-030 — Investigación y auditoría de la fase D-06

Consulta inicial: **2026-09-27, America/Guatemala**; capturas técnicas **2026-09-28 UTC**.
Reconsulta del backend S3, BPA y precios oficiales: **2026-09-28**.
Fuentes externas exclusivamente oficiales. Este documento fundamenta la propuesta
del [runbook](../runbooks/terraform-state-bootstrap.md), no autoriza su ejecución.

## 1. Contrato recuperado del repositorio

Auditoría del árbol en `db6e9c7804cbf8f8afcb5fcbd8b7ec8cd8dfd485`:

| Documentos/código consultados | Consecuencia para la fase |
| --- | --- |
| PROJECT_INSTRUCTIONS, STATUS, ROADMAP, WORKFLOW, STAGE-10 | Rama desde main; 29/41; siete tareas en ETAPA 10, ninguna aprobada; controles humanos separados del approval final |
| open-decisions, ADR-003, ADR-006, ADR-010 | D-06 Resuelta desde 025; backend S3 separado, lock nativo; un grafo de aplicación; RDS sustituye VPS |
| target-production-architecture, security-boundaries, aws-local-parity | State sensible fuera de Git; evidencia AWS separada de Floci; no inventar paridad |
| production-postgresql-rds y reparto aprobado de Task/029 | D-06 precede a red/RDS; no adelantar Task/031 ni alterar D-10/D-22/D-23/D-24 o EX-029-D13 |
| Runbook OIDC e índice de runbooks; runbooks de despliegue/recuperación | Migración posterior con `init -migrate-state`; backup, único escritor y recuperación demostrada; production del lanzador sigue bloqueado |
| Fichas/reportes 010 y 016 | Mecanismo de storage ya existe; claves persistidas, URL temporal emitida al servir; `og:image` estable del sitio; D-08 permanece abierta |
| Ficha/reporte 025 y `terraform/` | 21 recursos de aplicación en un solo grafo; módulo de medios privado con ownership, BPA, SSE-S3, CORS condicional, versioning, policy TLS y expiración de versiones; no reutilizar esa expiración para state |
| Fichas/reportes 028, 028.2, 029 y 029.1; `bootstrap/github-oidc/` | OIDC separado y sin permisos; custodia satisfecha pero EX-028-C7 no extinguida; no transferir estado ni cerrar decisiones durante preparación |
| `.github/workflows/` | CI Infra admite validación offline; workflow OIDC solo valida federación; no añadir despliegue ni permisos AWS |

El root de aplicación sigue intacto. Para S3 de medios habrá que reutilizar el módulo
de almacenamiento sin aplicar red/Lambda/SSM/API ni usar `-target`; esa composición
se resolverá en su fase, no mediante el bootstrap D-06.

### Contexto funcional de medios, sin decisión D-08

Inspección de `app/shared/storage/`, configuración, emisión de acceso, claves,
modelos/contratos y pruebas actuales de backend:

- `S3Storage` usa boto3 y SigV4, sin crear buckets; sin endpoint propio resuelve AWS.
- Operaciones reales: PutObject, GetObject, HeadObject, DeleteObject y ListObjectsV2
  para `_readiness/`. El listado de readiness impide afirmar que el runtime no usa List.
- Solo genera **presigned GET**; no existe presigned PUT en el contrato actual.
- `object_key` se persiste; `access_url` y `thumbnail_access_url` se emiten al servir.
  Claves: `medios/<uuid>/original.<ext>` y miniatura derivada. Nunca persistir la firma.
- `BLOG_STORAGE_ACCESS_TTL_SECONDS`: valor actual 900 s, rango 60–604800; la política
  productiva es pendiente de D-08, no se cambia aquí.
- El navegador accede directamente al endpoint firmado; cambiar el Host rompe SigV4.
  Una futura restricción global `SourceVpce` podría romper ese canal.
- La suite contractual de ObjectStorage crea/elimina un bucket **local de pruebas**
  mediante guardas de loopback. No se ejecuta esa fixture contra AWS real.
- `og:image` por contenido y CDN/cache necesitan decisión posterior; el recurso estático
  de Task/016 y D-21 no se modifican. Ningún dominio se inventa ni se decide D-07.

### Auditoría VPS/D-16 y drift de estado

La enmienda ADR-010 vigente retira de Task/030 backups del VPS, identidad VPS→AWS,
D-16 y PgBouncer. Las tablas/relatos históricos de 025/028 y arquitectura se conservan.
En STAGE-10 el antiguo criterio de backups del VPS se convierte en nota histórica,
sin checkbox de aceptación actual. La ficha nueva excluye expresamente ese alcance.

La tabla resumida del ROADMAP aún contaba **28/41** y **ETAPA 09 2/3**, y la vista
rápida de STATUS mostraba tareas anteriores pese a la aprobación registrada de 029.
Se reconcilian con el estado canónico de entrada **29/41**, **09 3/3** y apertura de
030/ETAPA 10, sin sumar una aprobación. No se reescriben las cronologías legítimas.

## 2. Terraform y recuperación

El [backend S3 de HashiCorp](https://developer.hashicorp.com/terraform/language/backend/s3)
soporta `use_lockfile=true`, opt-in. DynamoDB locking está deprecado; **no se añade**.
State necesita Get/PutObject; lock necesita además DeleteObject. ListBucket debe
permitir el prefix del estado. La recuperación requiere versionado del bucket.

La [referencia de init](https://developer.hashicorp.com/terraform/cli/commands/init)
distingue migrar de reinicializar. Cambiar de local a S3 exige cambiar el bloque backend;
`-migrate-state` copia el state y puede pedir confirmación. `-reconfigure` no sustituye
esa copia. El runbook reserva la migración a H-030-2 y no usa `-force-copy`.

El [provider 6.64.0, BPA de cuenta](https://raw.githubusercontent.com/hashicorp/terraform-provider-aws/v6.64.0/website/docs/r/s3_account_public_access_block.html.markdown)
expone las cuatro flags; su configuración es única para la cuenta.
La [implementación del bucket](https://raw.githubusercontent.com/hashicorp/terraform-provider-aws/v6.64.0/internal/service/s3/bucket.go)
consulta ACL, policy, versioning, cifrado, lifecycle, CORS, website, logging,
replicación, object lock, request payment y aceleración al refrescar. Se documentan
esas lecturas, aunque no se creen todos esos controles.

## 3. Seguridad y ciclo de vida S3

| Tema | Hallazgo oficial y aplicación propuesta |
| --- | --- |
| [Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html) | Prevalece la combinación más restrictiva. El control de cuenta se propaga globalmente; su ausencia fue H-030-4, autorizada solo para diseño/plan. Cuatro flags en cuenta y bucket |
| [Ownership/ACL](https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html) | BucketOwnerEnforced deshabilita ACL y atribuye ownership al dueño del bucket. Se declara explícito, sin recurso ACL |
| [Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html) | Cada versión almacena/cobra el objeto completo. Permite recuperar sobrescrituras y delete markers; no es inmutabilidad. No expirar versiones del state |
| [SSE-S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingServerSideEncryption.html) | AES256 con claves administradas por S3; sin cargo de cifrado adicional. Declaración explícita en Terraform, no dependencia del default |
| [TLS y policy](https://docs.aws.amazon.com/AmazonS3/latest/userguide/amazon-s3-policy-keys.html) | `aws:SecureTransport=false` permite denegar HTTP. Aquí se aplica a bucket/objetos sin conceder acceso ni restricciones de VPC |
| [Naming](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html) | Unicidad dentro de la partición AWS, 3–63 caracteres; evitar datos sensibles y nombres que interfieran con TLS. Nombre sin puntos y con sufijo determinístico; colisión obliga a parar |
| [CORS](https://docs.aws.amazon.com/AmazonS3/latest/userguide/enabling-cors-examples.html) | CORS permite al navegador evaluar respuestas entre orígenes; no concede permisos S3. State no tiene consumidor browser y no lleva CORS |
| [Presigned GET/PUT](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html) | Acceso firmado a objetos privados limitado por permisos y duración de credenciales. BPA no convierte esas solicitudes autenticadas en acceso anónimo; la policy IAM/TLS sigue aplicando. No se implementa PUT prefirmado inexistente |
| [Multipart/lifecycle](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpu-abort-incomplete-mpu-lifecycle-config.html) | AbortIncompleteMultipartUpload limpia partes sin eliminar objetos completos. El state usa pequeños PutObject; no se introduce lifecycle de state. La política de medios se evaluará en su propia fase |

SSE-KMS permitiría control separado de la clave, a cambio de permisos KMS, dependencia
de su disponibilidad y operación de la clave. Una clave propia añade **USD 1/mes** y
requests (ejemplo oficial: USD 0.03/10.000); claves AWS-managed no tienen ese cargo
de almacenamiento, pero sí de requests. D-06 no exige KMS y se propone **SSE-S3**.
[Precios oficiales KMS](https://aws.amazon.com/kms/pricing/).

## 4. Costo bruto incremental del bootstrap

Tarifas USD de Ohio, obtenidas del catálogo público oficial, sin consultar Billing:

- [AmazonS3 us-east-2](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-2/index.json),
  publicación `2026-09-26T01:55:12Z`, SHA-256
  `f1931cba7a04f6d14d848d6b438920132d6bb71d5da0b15431b3f0ba08034884`.
- [AWSDataTransfer us-east-2](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSDataTransfer/current/us-east-2/index.json),
  publicación `2026-09-16T13:22:08Z`.
- [Página oficial de precios S3](https://aws.amazon.com/s3/pricing/).

| Concepto | Tarifa | Escenario mensual deliberadamente holgado | USD bruto |
| --- | --- | --- | --- |
| S3 Standard, primeras 50 TB | 0.023/GB-mes | 1 GB, **incluye versiones y locks históricos** | 0.0230 |
| PUT/COPY/POST/LIST | 0.005/1.000 | 1.000 | 0.0050 |
| GET y demás lecturas | 0.0004/1.000 | 1.000 | 0.0004 |
| Egress a Internet, tramo facturable | 0.09/GB | 1 GB, sin descontar franquicia | 0.0900 |
| **Total conservador** | | | **0.1184 ≈ 0.12/mes** |

El catálogo incluye **100 GB/mes globales de salida sin cargo**, compartidos entre
servicios/regiones. Si queda esa franquicia, este escenario baja a **USD 0.0284/mes**
antes de créditos. No se presupone su disponibilidad. Entrada de datos sin cargo;
no hay transferencias interregionales, servicios CDN ni costos fijos nuevos.
Versioning no tiene tarifa separada: multiplica los bytes almacenados. No hay
transiciones ni expiración lifecycle, recuperación desde Glacier ni requests KMS.

El bucket vacío tras H-030-1 almacenaría 0 bytes de state hasta H-030-2. Para la
configuración inicial se reserva conservadoramente **menos de USD 0.001** suponiendo
hasta 100 requests Tier1 y 100 Tier2; no es una medición de factura ni un tope de uso.
BPA no añade un cargo fijo. Los planes no crean almacenamiento.

**Créditos:** conservar lo confirmado en Task/029: USD 120 observados, límite
2027-03-15; no se reconsultó el saldo ni se cambió Billing. Crédito potencialmente
consumido equivale al cargo elegible, hasta el saldo y fecha disponibles. Con crédito
suficiente, desembolso incremental esperado cero; **costo bruto no es cero**.
Después del crédito, si la cuenta sigue operativa bajo un plan habilitado, el mismo
consumo costaría hasta USD 0.1184/mes según este supuesto, más impuestos aplicables.
La decisión de continuidad del Free Plan y EX-029-D13 siguen como fueron aprobadas.

## 5. Paridad de esta fase

| Capacidad | Clasificación | Evidencia actual |
| --- | --- | --- |
| Bootstrap independiente D-06 | AWS-only | H-030-1: siete recursos aplicados y verificados. H-030-2: primer backend apunta a S3, pero migración detenida en H-030-4 por cambio de lineage/serial/checks |
| BPA de cuenta | AWS-only | Ausente antes de H-030-1; ahora cuatro flags globales verificadas por API, además de las del bucket |
| IAM efectivo y privacidad del state | No simulable localmente con evidencia suficiente | Gestión S3 humana ejercida y controles privados leídos; objetos/locking/recuperación y negativas todavía pendientes |
| Lock nativo, versionado y recuperación de state | AWS-only a efectos de evidencia de esta fase | Versioning Enabled; primer objeto state presente. Backups GPG verificados; convergencia, segunda migración, contención y recovery remoto pendientes por H-030-4 |
| Módulo de medios Task/025 | Sin clasificación de resultado AWS todavía | Solo lectura; no se aplicó ni modificó |

No se marca ninguna capacidad como validada en AWS por haber pasado un plan.
H-030-1 aporta apply y readback de configuración; no prueba todavía operaciones
de state remoto ni recuperación. Evidencia exacta en el reporte de ejecución.
