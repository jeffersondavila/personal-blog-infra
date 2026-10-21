# ETAPA 10 — Despliegue Cloud

| Campo | Valor |
| --- | --- |
| **Número** | 10 |
| **Estado** | En progreso — **1/7 aprobadas**: `Task/030` el 2026-09-29 |
| **Dependencias** | [ETAPA 09](STAGE-09-cloud-accounts.md) |
| **Tareas** | 7 |
| **Aprobadas** | 1 |
| **Avance** | ≈ 14 % |
| **Hito que completa** | Blog en línea y accesible por dominio propio. |

---

**Apertura 2026-09-27:** [Task/030](../tasks/TASK-030-deploy-amazon-s3.md) prepara
el bootstrap D-06. H-030-4 autoriza solo diseño/plan del BPA **global de cuenta**,
además del de bucket. **2026-09-28:** H-030-1 autorizado, aplicado y verificado
(siete recursos). **H-030-4-refresh-apply completado**: primer bootstrap S3
validado tras refresh-only autorizado y convergencia 0/0/0, drift 0. **El state OIDC
también quedó migrado y validado**, sin refresh-only, con drift 0 e IAM real intacto.
**Contención del locking nativo y recovery por versión demostrados** sobre las dos
keys, sin force-unlock y sin tocar nada autoritativo. Después se retiraron los states
locales como fuentes operativas y **EX-028-C7 quedó Extinguida el 2026-09-28**:
**H-030-2 COMPLETO**, con S3 como única fuente operacional. **D-08 quedó Resuelta para el
MVP** ese día: privado, presigned dinámico, sin URL estable ni CDN, `og:image` estático y
**cero servicios nuevos**; **`B-016-1` sigue abierto**. Y una **enmienda al diseño de
`Task/025`**: el almacenamiento de medios pasa a un root propio, `terraform-medios`, con su
propio state, reutilizando el módulo compartido; la regla de paridad queda precisada
([§4.1.1](../architecture/aws-local-parity.md)). *(Hasta aquí, el estado del 2026-09-28.)*

**2026-09-29 — Task/030 Lista para validación, READY FOR FINAL APPROVAL.** El bucket de
medios está creado en su root propio, verificado contra AWS y convergente **0/0/0 con drift
0**; `S3Storage` funciona contra S3 real tras corregir **DEF-030-1** bajo test-first; los
subcomandos del laboratorio operan sobre los dos roots (**DEF-030-2**) y la identidad del
runtime se verifica sin relajar el image ID (**DEF-030-3**), con `crear`, `validar` y
`destruir` ejecutados de verdad. [Reporte §27](../task-reports/TASK-030-report.md).

**2026-09-29 — Task/030 APROBADA** mediante `approved: Task/030-Desplegar-Amazon-S3`. La
etapa pasa a **1/7 ≈ 14 %** y el avance global a **30/41 ≈ 73 %**. Siguiente:
`Task/031`, **Pendiente y no iniciada**.

**2026-10-03 — Task/031 En progreso.** H-031-1 completado, solo offline: root
`terraform-datos` con red privada y RDS, laboratorio de tres roots ejecutado de verdad,
diseño de la identidad operativa mínima `PersonalBlogDataOperator` sin aplicar. **Cero
recursos AWS.** H-031-1A **READY FOR H-031-IAM**. Historia: un primer ciclo local se
**rechazó** por `resource_drift` no declarado (`domain_dns_ips: null → []`) que la guarda
omitía; sin ampliar tolerancias, se diagnosticó como representación del SDKv2 del provider, la
guarda pasó a juzgar `resource_drift` con lista cerrada y un ciclo nuevo y los gates quedaron en
verde ([reporte §15](../task-reports/TASK-031-report.md#15-h-031-1a--resolución-del-bloqueo-de-domain_dns_ips-2026-10-03)).
Se mantienen **21 recursos** de datos; SG por omisión no
gestionado ni usado, DN-3 eliminada, simulación desde bootstrap. DN-2 solo si AWS demuestra
drift, con refresh-only revisado y autorización explícita posterior. **H-031-IAM COMPLETE** (2026-10-04): operador creado y validado, S-10 aplicada y
verificada; por decisión operacional del usuario, el resto de Task/031 se opera con `personal-blog`
(`PersonalBlogAdministrator`); `terraform-datos` ya exige esa identidad; **H-031-2 PLAN READY FOR APPLY REVIEW** (21/0/0, [§26](../task-reports/TASK-031-report.md#26-h-031-2--plan-guardado-de-red-y-rds-sin-apply-2026-10-04)); alineación en [§25](../task-reports/TASK-031-report.md#25-h-031-2-align--terraform-datos-exige-personalblogadministrator-2026-10-04)).
**H-031-3 APPLY FAILED / RECOVERY REVIEW REQUIRED** ([§27.4](../task-reports/TASK-031-report.md#274-h-031-3--reintento-apply-fallido-en-el-parameter-group-2026-10-05)): existen 20 de 21 recursos y la instancia RDS no se creó. **H-031-3-RECOVERY: DN-2 DRIFT REVIEW REQUIRED** ([§28](../task-reports/TASK-031-report.md#28-h-031-3-recovery--corrección-de-d-22-y-plan-de-recuperación-2026-10-05)). **H-031-3-RECOVERY-DN2: REFRESH PLAN REJECTED (`OUTPUTS`)** ([§29](../task-reports/TASK-031-report.md#29-h-031-3-recovery-dn2--refresh-only-plan-only-rechazado-por-las-salidas-2026-10-05)); sin apply. **H-031-3 DN-2 REFRESH PLAN READY** ([§30](../task-reports/TASK-031-report.md#30-h-031-3-recovery-dn2-outputs--alineación-de-la-guarda-dn-2-2026-10-05)): mismo plan, `DN2_REFRESH_PLAN_OK`; sin apply. **H-031-3 DN-2 REFRESH APPLIED / RECOVERY PLAN READY** ([§31](../task-reports/TASK-031-report.md#31-h-031-3-dn-2--refresh-only-aplicado-y-nuevo-plan-de-recuperación-2026-10-05)): state reconciliado (serial 2, taint conservado, AWS sin cambios), plan de recuperación 2/0/1 con `RECOVERY_PLAN_OK`; sin recovery apply ni RDS. **H-031-3 RECOVERY APPLY FAILED / REVIEW REQUIRED** ([§32](../task-reports/TASK-031-report.md#32-h-031-3--recovery-apply-fallido-restricción-del-plan-gratuito-de-la-cuenta-2026-10-05)): `FreeTierRestrictionError` por la retención de backups; parameter group reemplazado, 20/21 sin taint, **sin RDS**. **H-031-3 RECOVERY-2 DECISION READY** ([§33](../task-reports/TASK-031-report.md#33-h-031-3-recovery-2--plan-de-cuenta-y-parameter-group-de-cuatro-parámetros-2026-10-05)): cuenta `FREE`/`ACTIVE` hasta 2027-03-15; retención máxima desconocida; parameter group de cuatro parámetros. Espera la decisión de retención y plan de cuenta. **H-031-3 RECOVERY-3-FREE: DRIFT REVIEW REQUIRED** ([§34](../task-reports/TASK-031-report.md#34-h-031-3-recovery-3-free--retención-temporal-de-1-día-y-plan-de-recuperación-2026-10-05)): se mantiene FREE con retención temporal de 1 día; plan 1/1/0 sin destroy ni replace, `resource_drift = 1` de representación; sin apply. **H-031-3 RECOVERY-3-FREE PLAN READY** ([§35](../task-reports/TASK-031-report.md#35-h-031-3-recovery-3-free-drift--excepción-exacta-de-drift-en-la-guarda-2026-10-05)): excepción exacta de ese drift; mismo plan con `RECOVERY_3_FREE_PLAN_OK`; sin apply ni RDS. **H-031-3 RECOVERY-3-FREE APPLY FAILED / REVIEW REQUIRED** ([§36](../task-reports/TASK-031-report.md#36-h-031-3-recovery-3-free--apply-interrumpido-por-credenciales-caducadas-2026-10-05)): `ExpiredToken` a mitad del apply; **RDS existe (`available`, retención 1)** pero el state remoto no la registra; `errored.tfstate` local y lock retenido. **H-031-3 STATE RECOVERED / UNTAINT RETENIDO** ([§37](../task-reports/TASK-031-report.md#37-h-031-3-recovery-state--lock-liberado-y-state-restaurado-untaint-retenido-2026-10-05)): lock liberado, `state push` sin `-force` (21/21); la instancia sigue `tainted` porque su registro en el state está incompleto; revisión requerida. **H-031-3 TAINTED INSTANCE REFRESH PLAN READY** ([§38](../task-reports/TASK-031-report.md#38-h-031-3-recovery-state-refresh--plan-refresh-only-de-la-instancia-tainted-2026-10-05)): refresh-only con 36 atributos contrastados con AWS, sin cambios de infraestructura y con el taint conservado; `INSTANCE_REFRESH_PLAN_OK`; sin apply. **STOP de frescura antes del apply** ([§39](../task-reports/TASK-031-report.md#39-h-031-3-recovery-state-refresh-apply--stop-de-frescura-antes-del-apply-2026-10-05)): `latest_restorable_time` avanza solo; decisión requerida. **H-031-3 MOVING ATTRIBUTE CONTRACT READY** ([§40](../task-reports/TASK-031-report.md#40-h-031-3-moving-attribute--contrato-del-atributo-móvil-y-criterio-de-convergencia-2026-10-05)): contrato móvil y `ACTIONABLE_CONVERGENCE_OK` definidos; el mismo plan da `INSTANCE_REFRESH_PLAN_OK` con un describe fresco; sin apply. **H-031-3 STATE REFRESHED / CONVERGENCE REVIEW REQUIRED** ([§41](../task-reports/TASK-031-report.md#41-h-031-3--refresh-only-aplicado-readback-4040-y-untaint-convergencia-en-revisión-2026-10-06)): refresh-only aplicado, readback 40/40, untaint (21/21, 0 taints); convergencia «No changes» con drift móvil, pero la guarda la rechaza por exigir `applyable = true`; corrección propuesta. **H-031-3: convergencia aceptada** ([§42](../task-reports/TASK-031-report.md#42-h-031-3-convergence-guard-fix--guarda-corregida-y-el-mismo-json-aceptado-2026-10-06)): guarda corregida con TDD; el mismo JSON da `ACTIONABLE_CONVERGENCE_OK`, caso B; sin apply. **H-031-3 COMPLETE** ([§43](../task-reports/TASK-031-report.md#43-h-031-3-markdown-link-gate--pin-durable-de-la-gate-de-enlaces-y-cierre-de-h-031-3-2026-10-06)): gate de enlaces completa con un pin durable nuevo (`markdown-it-py` 4.2.0 y `mdurl` 0.1.2, con SHA-256 versionados) y **0 enlaces rotos**; seguridad y regresión en verde; sin cambios en AWS, state ni plan de convergencia. **H-031-5 IMPLEMENTATION READY / LAMBDA QUOTA PENDING** ([§44](../task-reports/TASK-031-report.md#44-h-031-5--ejecutora-privada-de-d-24-por-fases-implementación-offline-y-cuota-lambda-2026-10-06)): ejecutora privada de D-24 por fases, implementada y probada offline (*shell* sin base de datos, solo `sg-admin`, IAM mínimo, RC=1 y 4 recursos nuevos); sin plan productivo porque la cuota de concurrencia sigue en 10. **H-031-5-LAMBDA-QUOTA** ([§45](../task-reports/TASK-031-report.md#45-h-031-5-lambda-quota--rol-vinculado-creado-solicitud-a-101-rechazada-por-aws-2026-10-07)): se creó el rol vinculado de Service Quotas (única mutación) y la solicitud a 101 fue **rechazada por AWS**, que exige un valor mayor que el por omisión (1000); no quedó registrada y la decisión es del usuario. State en serial 8 y 21/21, sin cambios. **REMAINDER — H-031-6 a H-031-9 PREPARADOS OFFLINE / BLOCKERS REMAINING** ([§46](../task-reports/TASK-031-report.md#46-remainder--h-031-6-a-h-031-9-preparados-offline-aws-bloqueado-por-la-cuota-de-lambda-2026-10-07)): ejecutora h0316 (`verify`, `identidades`, `sintetico` y `export`) con artefacto fijado e integración local real en verde; operador, restore PITR, alarmas de D-11 y rol de D-20 preparados como código y módulos no cableados, con pruebas. **Ninguna llamada a AWS**: la cuota de Lambda (10) bloquea todo apply de `terraform-datos` y, por decisión del usuario del 2026-10-07, no se repite la solicitud. Propuestas pendientes de aprobación: mecanismo de credenciales, modos de provisión, D-20 y cierre de R-12. **H-031-8 y H-031-9 — APLICADOS Y CONVERGENTES / BLOCKERS REMAINING** ([§47](../task-reports/TASK-031-report.md#47-h-031-8-y-h-031-9--alarmas-de-d-11-y-rol-de-d-20-aplicados-y-convergentes-2026-10-08-a-2026-10-15)): por decisión del usuario, `terraform-datos` se reordenó: la ejecutora sale del root hasta la cuota, con módulo, artefacto, RC=1 y guarda intactos. Las 8 alarmas de D-11, sin acciones, y el rol `PersonalBlogLecturaGrafana` de D-20 (confianza con ExternalId, solo métricas y alarmas, sin logs) se aplicaron con plan guardado, guarda de lista cerrada, apply exacto, readback, simulación IAM 20/20 y convergencia con las guardas originales. El usuario aprobó una excepción puntual de la ventana móvil y dos refresh-only guardados de normalizaciones del provider. State en serial 12, 31/31. D-19 verificado para integrar: trial sin método de pago y comprobación pendiente al terminar. Hallazgo: la alarma `memoria` está en `ALARM` en reposo, con la calibración pendiente. Siguen B1 (cuota de Lambda: H-031-5, H-031-6 y H-031-7), B3 y B4. «Save & test» de Grafana (2026-10-16): API de métricas validada; la prueba combinada sale en rojo solo por la denegación prevista de logs (`logs:DescribeLogGroups`); Explore con métricas reales de RDS: **PASS** (2026-10-16), con lo que queda validada la ruta Grafana Cloud → AssumeRole → CloudWatch → RDS. Los estados de alarma en Grafana no se han probado: sus anotaciones requieren `DescribeAlarmHistory`, que no se concede. **B1, B3 y B4: DECISIONES DEL USUARIO DEL 2026-10-16** ([§48](../task-reports/TASK-031-report.md#48-bloqueos-b1-b3-y-b4--decisiones-del-usuario-del-2026-10-16)). B1: una única solicitud de cuota de Lambda (1001, con caso permitido); AWS abrió un caso (**CASE_OPENED**), sin tocar D-24 ni RC=1. B3: supervisión manual de solo lectura de los backups, con TDD (25 pruebas) y ejecución real en OK. B4: R-12 sigue **abierto** y documentado, con seguimiento en Task/040; BitLocker queda pendiente de verificación elevada. H-031-5 preparado offline (guarda con la línea base real de 31 recursos, fase `h0315`, refresh-only de normalizaciones y recableado validado). **No** es READY: H-031-5, H-031-6 y H-031-7 siguen sin evidencia de AWS (B1). **D-24 MODIFICADA (2026-10-18) — aprobada por el usuario el 2026-10-19, con la nueva semántica de §40** ([§49](../task-reports/TASK-031-report.md#49-d-24-modificada-y-plan-de-h-031-5-2026-10-18)): la ejecutora vuelve al root **sin concurrencia reservada**; las escrituras administrativas se excluyen con un bloqueo de aviso de PostgreSQL y B1 deja de bloquear, con la solicitud a 1001 abierta. Contrato de §40 enmendado: las 24 h miden la frescura del valor de AWS. **H-031-5 DESPLEGADA Y CONVERGENTE (2026-10-19)** ([§49.15](../task-reports/TASK-031-report.md#4915-aprobación-de-d-24-y-40-y-apply-de-h-031-5-2026-10-19)): apply exacto del plan autorizado (4 creates), *readback* y `selfcheck` exactos, refresh-only preautorizado de normalizaciones y convergencia 0/0/0; state en serial 15, 35/35. La cuota de Lambda ya es 1000. **2026-10-20** ([§50](../task-reports/TASK-031-report.md#50-trabajo-de-codex-retomado-laboratorio-completo-y-preparación-de-h-031-6-y-h-031-7-2026-10-19-y-2026-10-20)): trabajo de Codex retomado y revisado (dos falsos positivos de la guarda de H-031-6 corregidos con TDD); **laboratorio: CICLO COMPLETO** con H-031-6 cableado; gates 32/32; H-031-7 reanudable sin segundo restore. **Plan real de H-031-6 verificado** ([§50.12](../task-reports/TASK-031-report.md#5012-plan-real-de-h-031-6-2026-10-20)): `H0316_PLAN_OK`, 4 creates, 1 update en sitio y 0 destrucciones (SHA-256 `8d1a7307…7a6d`); sin apply. **2026-10-20 y 2026-10-21** ([§51](../task-reports/TASK-031-report.md#51-h-031-6-aplicada-y-verificada-y-h-031-7-completa-2026-10-20-y-2026-10-21)): **H-031-6 APLICADA Y CONVERGENTE** (apply 4/1/0, refresh-only `H0316_REFRESH_OK` y `ACTIONABLE_CONVERGENCE_OK` 0/0/0 sobre 39 recursos) **y SQL CONFORME** (`blog_migrate` y `blog_app` con D-23 y D-12; TLS `verify-full` con controles negativos; DDL rechazado a `blog_app`; `export` validado sin tablas de aplicación); **H-031-7 COMPLETA**: PITR real con integridad `true`, RPO 180 s y RTO 774 s, temporal eliminada con un único `DeleteDBInstance`, marcador retirado, cero residuos y productiva idéntica a su línea base; el incidente del 404 de backups automáticos, corregido con TDD. **CIERRE TÉCNICO COMPLETADO — Lista para validación**: pendiente la revisión del usuario y `approved`.
La etapa sigue en **1/7 ≈ 14 %**.
[Ficha](../tasks/TASK-031-deploy-network-rds-ssm-cloudwatch.md).

## Objetivo

Desplegar el blog en la nube siguiendo el orden de dependencias —almacenamiento,
configuración, cómputo, entrada HTTP, frontend, DNS— y publicar el primer contenido real.

## Por qué esta etapa existe

Es la materialización de la arquitectura de
[ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md). El orden de las tareas no es
arbitrario: cada una habilita a la siguiente.

## Relación con la ETAPA 08 — reutilizar, no reinventar

`Task/030`–`Task/033` **reutilizan los módulos Task/025 para infraestructura
de aplicación**. La expectativa explícita es:

> **Utilizar los módulos construidos y validados localmente en `Task/025` y materializarlos
> contra AWS real.**

> **Enmienda de `Task/028.2`, aprobada el 2026-09-27.** Con
> [ADR-010](../adr/ADR-010-production-postgresql-on-rds.md), `Task/031` **amplía** los
> módulos comunes con **red y RDS**, que el grafo de `Task/025` no contenía. Lo hace en el
> **mismo grafo**, sin duplicar módulos local/cloud, sin recursos específicos del emulador
> y sin reabrir `Task/025`. Esos recursos entran en la matriz de paridad como
> **No evaluados**: la evidencia local de `Task/025` **no** acredita RDS, security groups,
> IAM, KMS ni restore administrado. Contrato de evidencia por tarea:
> [canónico RDS §7](../architecture/production-postgresql-rds.md#7-propietarios-dependencias-y-evidencia).

**Excepción explícita Task/030 — bootstrap D-06.** Puede crear mediante Terraform
exclusivamente el bucket dedicado al estado y su protección: privado, versionado,
cifrado, public access block, bloqueo nativo `use_lockfile=true`, sin DynamoDB y
separado de medios/backups. Debe migrar `bootstrap/github-oidc/terraform.tfstate`
con `terraform init -migrate-state` y resolver la custodia/migración del estado del
propio bootstrap del bucket, con recuperación probada. La ficha Task/030 recogerá
estos entregables al abrirse. EX-028-C7 debía terminar antes del primer apply de
aplicación: **terminó el 2026-09-28**, **Extinguida** en H-030-2, sin que se haya
ejecutado ningún apply de aplicación.
*(Precisión de `Task/028.2`: la **custodia** de EX-028-C7 quedó cerrada en `Task/028`; la
**excepción** sigue acotada al root del bootstrap OIDC y **no se extiende a RDS** ni a
ningún recurso de aplicación. Por eso `Task/031` depende de `Task/030`.)*

No duplica el grafo Task/025: **el backend debe existir antes de inicializar el grafo
que depende de él**. Por eso se materializa desde un root bootstrap independiente,
con su propio ciclo de estado. [Runbook OIDC](../runbooks/github-oidc-bootstrap.md).

Esta etapa es, además, donde el proyecto descubre **qué era realmente cierto** del
laboratorio local. Por cada recurso se documenta y se clasifica:

| Categoría | Significado |
| --- | --- |
| **Funcionó sin cambios** | El módulo se aplicó tal cual. |
| **Cambio de configuración** | Bastó ajustar variables, endpoints o nombres. |
| **Adaptación necesaria** | Hubo que modificar el diseño del recurso. |
| **No simulable localmente** | El emulador no lo reproducía con fidelidad suficiente. |
| **AWS-only** | Nunca pudo validarse en local por naturaleza. |

Diferencias que hay que comparar de forma expresa: **IAM** (autorización real, que el
laboratorio **no** ejercita), **red y DNS** (`execute-api`, TLS, dominios personalizados),
**cuotas y límites de cuenta**, **arranque en frío real** de la Lambda, **cifrado real de
`SecureString`** en SSM y **evaluación real de alarmas** en CloudWatch. *(Enmienda:
también **red privada** —VPC, subnets, security groups, rutas y *endpoints*—, **TLS
verificado hacia RDS**, **KMS**, **backups administrados, PITR y restore**, y el
comportamiento de la **Lambda conectada a la VPC**: todo **AWS-only** a efectos de
evidencia.)*

Toda esa evidencia se vuelca en la **matriz de paridad** de
[aws-local-parity.md](../architecture/aws-local-parity.md) §7, cuyas celdas pasan aquí a
`Validada en AWS`. Ninguna celda puede marcarse así sin haberse ejecutado contra AWS real.

**AWS real es la autoridad final.** Si el laboratorio y AWS discrepan, AWS tiene razón y el
laboratorio se corrige.

## Tareas

| Tarea | Contenido | Depende de |
| --- | --- | --- |
| `Task/030-Desplegar-Amazon-S3` | Bucket, CORS, políticas, URLs prefirmadas, lifecycle. **Validación de `S3Storage` contra S3 real**. Resuelve **D-08**. **Excepción D-06:** bucket de estado y protección, migración OIDC y custodia/migración del estado del propio bootstrap. *(Enmienda `Task/028.2`: se retiran el **destino de los backups del VPS** y la **materialización de D-16**, que pierden objeto con los backups administrados de RDS.)* | `Task/029` |
| `Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch` *(antes `Task/031-Desplegar-SSM-y-CloudWatch`; `Task/028.2`)* | Parámetros **`SecureString`** y permisos IAM mínimos. **CloudWatch mínimo**: grupos de logs, **retención corta y explícita** (**D-11**), alarmas mínimas. Integración `CloudWatch → Grafana Cloud`: **decide e implementa D-20**, con modelo IAM de **solo lectura** y **D-19** verificada antes. **Alcance exclusivamente AWS.** Además: **VPC, subnets, security groups y rutas o *endpoints*** (**D-22**), **RDS privado** con *parameter group*, KMS y credenciales (**D-23**), **acceso operativo privado** (**D-24**), **restore sintético y PITR** demostrados (**D-10**), y runbooks, inventarios y guardas ampliados | `Task/030` *(antes `Task/029`)* |
| `Task/032-Desplegar-AWS-Lambda` | Función, rol IAM, configuración, memoria y timeout. ***Reserved Concurrency*** coherente con el pool de PgBouncer, **RTT real `Lambda → PgBouncer` medido** y *wiring* de `S3Storage`. *(Enmienda `Task/028.2`: Lambda **conectada a la VPC**, `DATABASE_URL` hacia **RDS** con **TLS verificado**, secretos según **D-23**, *Reserved Concurrency* y pool **medidos** frente a `max_connections`, **latencia `Lambda ↔ RDS` medida**, y tráfico real a PostgreSQL, S3, SSM y logs **sin NAT**.)* | `Task/030`, `Task/031` |
| `Task/033-Desplegar-API-Gateway` | HTTP API, rutas, CORS, throttling. *(Desde `Task/028.2`: logs y métricas del API con la política **D-11**.)* | `Task/032` |
| `Task/034-Desplegar-Cloudflare-Pages` | Build de React, variables, dominio. | `Task/033` |
| `Task/035-Configurar-DNS` | Dominio principal, `www`, `api`, `media` si corresponde. | `Task/034` |
| `Task/036-Publicar-Primer-Contenido` | Migraciones, administrador, perfil, artículo, review, video, imágenes. *(Enmienda `Task/028.2`: migraciones por el **canal privado D-24**, con identidad SQL distinta y **backup previo**; recuperación del administrador **R-43** y purga **R-44** según el diseño de `Task/029`.)* | `Task/035` |

**Repositorio principal:** `personal-blog-infra` (Terraform), con participación de
`personal-blog-frontend` y `personal-blog-backend` en `Task/034` y `Task/036`. *(Desde
`Task/028.2`: el backend participa además en `Task/032` si **D-23** exige leer secretos en
*runtime*; hoy no existe ese lector.)*

## Criterios de salida de la etapa

- [x] El bucket S3 es privado; el acceso a archivos usa URLs prefirmadas.
      *(`Task/030`, aprobada el 2026-09-29: BPA de cuenta y bucket, policy sin ningún
      `Allow` e `IsPublic=false`, GET sin firma **403** y prefirmada GET **HTTP 200** contra
      el bucket real.)*
- [ ] Toda la configuración vive en SSM Parameter Store, nunca en el código.
- [ ] Los logs llegan a CloudWatch con retención limitada y explícita, y el alcance de
      CloudWatch se mantiene **mínimo**: sin *dashboards* elaborados ni funcionalidades no
      justificadas.
- [ ] **D-20 decidida**: está definido con qué mecanismo IAM de **solo lectura** accedería
      Grafana Cloud a CloudWatch, sin credenciales de larga vida versionadas. **Implementarla
      no es obligatorio en esta etapa; decidirla, sí.** *(Enmienda: sin Alloy, es
      la única vía de datos hacia Grafana; `Task/031` también la **implementa**, salvo una
      decisión explícita en contra por costo o mecanismo.)*
- [ ] La Lambda responde correctamente a través de API Gateway.
- [ ] API Gateway tiene throttling configurado.
- [ ] El frontend está publicado en Cloudflare Pages y consume el API real.
- [ ] El dominio resuelve por HTTPS con certificado válido.
- [ ] Existe contenido real publicado y visible en el sitio.
- [ ] El costo real observado coincide con lo estimado.
> **Criterio histórico sustituido por ADR-010; no es un gate actual:** el destino
> de backups del VPS existía en el alcance previsto de S3, con política, retención
> y principal derivado de D-16. Lo sustituyen los criterios RDS de abajo;
> Task/030 no crea ese destino ni esa identidad.
- [x] `S3Storage` —cuyo código entrega `Task/010`— **funciona contra S3 real**.
      *(`Task/030`, aprobada el 2026-09-29: **14/14** contra el bucket real tras DEF-030-1.)*
- [ ] La **`Reserved Concurrency`** de la Lambda es coherente con el pool de PgBouncer y con
      `max_connections`, según los números derivados en `Task/029`. *(Enmienda:
      coherente con el pool por proceso y `max_connections` de RDS, **medidos** en
      `Task/032`.)*
- [ ] Los módulos de **aplicación** son los validados en Task/025; solo se añade
      el bootstrap independiente de D-06 bajo la excepción Task/030. *(Enmienda:
      además, la **extensión de red y RDS** de `Task/031`, en el mismo grafo.)*

Criterios **fijados por `Task/028.2`** (2026-09-27) para la capa de datos RDS:

- [ ] RDS **no es accesible públicamente**: subnets privadas y security group que solo
      admite el puerto SQL desde los security groups autorizados. Casos negativos
      comprobados.
- [ ] TLS con validación de CA y *hostname* desde la Lambda real; TLS obligatorio en el
      *parameter group*; cifrado en reposo con la clave KMS decidida.
- [ ] Credenciales SQL separadas —aplicación, migraciones, *master*—, ninguna en Git, en
      *outputs*, en planes publicados ni en logs.
- [ ] **Restore sintético y PITR demostrados** en `Task/031` —integridad, tiempos,
      *endpoint*, security groups y KMS revisados— y limpieza autorizada.
- [ ] La Lambda conectada a la VPC alcanza PostgreSQL, S3, SSM y sus logs **sin NAT
      Gateway**, según el diseño aprobado.
- [ ] Primeras migraciones ejecutadas por el **canal privado D-24**, con backup previo.
- [ ] Runbooks de creación, destrucción, recuperación, rollback y validación **ampliados**
      a red y RDS antes de operar esos recursos.
- [ ] Costo real contrastado con la estimación de `Task/029` frente a **D-13**, separando
      costo bruto y crédito consumido.
- [x] Bucket de estado dedicado protegido, `use_lockfile=true`, sin DynamoDB.
- [x] Estados OIDC y del bootstrap del bucket bajo custodia definida y recuperable;
      migración verificada por lineage/serial/recursos y plan sin cambios.
      *(`Task/030`, aprobada el 2026-09-29, para estos dos criterios: tres keys en S3 con
      lock nativo y sin DynamoDB, locking por contención y recovery por versión
      demostrados, y los tres states intactos en el AWS final del 2026-09-29.)*
- [x] **EX-028-C7 Extinguida** el 2026-09-28, antes de cualquier apply de infraestructura de aplicación.
- [ ] La **matriz de paridad** queda actualizada con evidencia real de AWS, recurso a
      recurso y con la clasificación de diferencias.

## Fuera del alcance de la etapa

- Automatizar el despliegue (Etapa 11).
- Validación final integral y protección de costos permanente (Etapa 12).
- EC2, ECS, ECR, EKS, ALB y NAT Gateway (excluidos por ADR-003).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Bucket S3 accidentalmente público. | Bloqueo de acceso público a nivel de cuenta y bucket; verificación explícita. |
| Retención de logs infinita generando costo creciente. | Retención definida en `Task/031`; refuerzo en `Task/041`. |
| **Dar a un tercero acceso amplio o permanente a AWS** al integrar la observabilidad (**D-20**). | Permiso **mínimo**, **solo lectura** y sin credenciales de larga vida versionadas. El compromiso de Grafana Cloud **no debe** implicar el de AWS. |
| CORS mal configurado que rompe el frontend. | Orígenes permitidos explícitos; prueba desde el dominio real. |
| Propagación de DNS más lenta de lo previsto. | TTL bajo durante el corte; ventana de validación holgada. |
| Arranque en frío perceptible en la primera visita. | Medición y ajuste de memoria de la Lambda. |
| *(`Task/028.2`)* **RDS o sus snapshots expuestos por error**, o security group demasiado amplio (**R-30**). | Sin acceso público, subnets privadas, SG de SG a SG, casos negativos en `Task/031` y `Task/040`. |
| *(`Task/028.2`)* **Borrado o pérdida de acceso** a RDS, a sus snapshots o a su clave KMS (**R-35**). | *Deletion protection*, snapshot final, claves nunca deshabilitadas en pruebas, planes revisados y ningún `destroy` automático contra la base real. |
| *(`Task/028.2`)* **Backup administrado que no restaura** (**R-31**). | Restore sintético y PITR en `Task/031`; restore reciente en `Task/040`. «`available`» no es evidencia. |
| *(`Task/028.2`)* **Agotamiento de conexiones** (**R-03**, **R-33**). | Pool por proceso y concurrencia **medidos** en `Task/032`; RDS Proxy solo con evidencia. |
| *(`Task/028.2`)* **Costo fijo de RDS y *endpoints*** por encima de **D-13**, o créditos que caducan (**R-02**). | Estimación de `Task/029` y decisión explícita si no cabe, antes del primer `apply` de aplicación. |
| *(`Task/028.2`)* Una política de bucket con `aws:SourceVpce` **rompe las URLs prefirmadas** del navegador. | Validarla con **D-08** en `Task/030` y con la Lambda real en `Task/032`. |

## Siguiente etapa

[ETAPA 11 — Automatización de Despliegues](STAGE-11-deployment-automation.md)
