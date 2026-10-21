# TASK-031 — Desplegar Red, RDS, SSM y CloudWatch

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch` |
| **Nombre** | Desplegar Red, RDS, SSM y CloudWatch |
| **Etapa** | ETAPA 10 — Despliegue Cloud |
| **Estado** | **Lista para validación** (cierre técnico del 2026-10-21) — H-031-1 completado el 2026-10-03, **solo offline**. **H-031-1A READY FOR H-031-IAM** (2026-10-03), tras rechazar un primer ciclo por drift no declarado y resolverlo con evidencia. **H-031-IAM COMPLETE** (2026-10-04): operador creado y validado, S-10 aplicada (simulación contra el rol vivo 62/62, convergencia 0/0/0); por **decisión operacional del usuario** no se configura `personal-blog-datos` y las operaciones restantes usan `personal-blog` / `PersonalBlogAdministrator`. **H-031-2-ALIGN READY**: `terraform-datos` y su guarda exigen exactamente `PersonalBlogAdministrator` ([§25](../task-reports/TASK-031-report.md#25-h-031-2-align--terraform-datos-exige-personalblogadministrator-2026-10-04)); **H-031-2 PLAN READY FOR APPLY REVIEW** ([§26](../task-reports/TASK-031-report.md#26-h-031-2--plan-guardado-de-red-y-rds-sin-apply-2026-10-04)); **H-031-3 APPLY FAILED / RECOVERY REVIEW REQUIRED** ([§27.4](../task-reports/TASK-031-report.md#274-h-031-3--reintento-apply-fallido-en-el-parameter-group-2026-10-05)): 20 de 21 recursos creados, sin RDS; **H-031-3-RECOVERY: DN-2 DRIFT REVIEW REQUIRED** ([§28](../task-reports/TASK-031-report.md#28-h-031-3-recovery--corrección-de-d-22-y-plan-de-recuperación-2026-10-05)) **H-031-3-RECOVERY-DN2: REFRESH PLAN REJECTED (`OUTPUTS`)** ([§29](../task-reports/TASK-031-report.md#29-h-031-3-recovery-dn2--refresh-only-plan-only-rechazado-por-las-salidas-2026-10-05)); sin apply. **H-031-3 DN-2 REFRESH PLAN READY** ([§30](../task-reports/TASK-031-report.md#30-h-031-3-recovery-dn2-outputs--alineación-de-la-guarda-dn-2-2026-10-05)): mismo plan, `DN2_REFRESH_PLAN_OK`; sin apply. **H-031-3 DN-2 REFRESH APPLIED / RECOVERY PLAN READY** ([§31](../task-reports/TASK-031-report.md#31-h-031-3-dn-2--refresh-only-aplicado-y-nuevo-plan-de-recuperación-2026-10-05)): state reconciliado (serial 2, taint conservado, AWS sin cambios), plan de recuperación 2/0/1 con `RECOVERY_PLAN_OK`; sin recovery apply ni RDS. **H-031-3 RECOVERY APPLY FAILED / REVIEW REQUIRED** ([§32](../task-reports/TASK-031-report.md#32-h-031-3--recovery-apply-fallido-restricción-del-plan-gratuito-de-la-cuenta-2026-10-05)): `FreeTierRestrictionError` por la retención de backups; parameter group reemplazado, 20/21 sin taint, **sin RDS**. **H-031-3 RECOVERY-2 DECISION READY** ([§33](../task-reports/TASK-031-report.md#33-h-031-3-recovery-2--plan-de-cuenta-y-parameter-group-de-cuatro-parámetros-2026-10-05)): cuenta `FREE`/`ACTIVE` hasta 2027-03-15; retención máxima desconocida; parameter group de cuatro parámetros. Espera la decisión de retención y plan de cuenta. **H-031-3 RECOVERY-3-FREE: DRIFT REVIEW REQUIRED** ([§34](../task-reports/TASK-031-report.md#34-h-031-3-recovery-3-free--retención-temporal-de-1-día-y-plan-de-recuperación-2026-10-05)): se mantiene FREE con retención temporal de 1 día; plan 1/1/0 sin destroy ni replace, `resource_drift = 1` de representación; sin apply. **H-031-3 RECOVERY-3-FREE PLAN READY** ([§35](../task-reports/TASK-031-report.md#35-h-031-3-recovery-3-free-drift--excepción-exacta-de-drift-en-la-guarda-2026-10-05)): excepción exacta de ese drift; mismo plan con `RECOVERY_3_FREE_PLAN_OK`; sin apply ni RDS. **H-031-3 RECOVERY-3-FREE APPLY FAILED / REVIEW REQUIRED** ([§36](../task-reports/TASK-031-report.md#36-h-031-3-recovery-3-free--apply-interrumpido-por-credenciales-caducadas-2026-10-05)): `ExpiredToken` a mitad del apply; **RDS existe (`available`, retención 1)** pero el state remoto no la registra; `errored.tfstate` local y lock retenido. **H-031-3 STATE RECOVERED / UNTAINT RETENIDO** ([§37](../task-reports/TASK-031-report.md#37-h-031-3-recovery-state--lock-liberado-y-state-restaurado-untaint-retenido-2026-10-05)): lock liberado, `state push` sin `-force` (21/21); la instancia sigue `tainted` porque su registro en el state está incompleto; revisión requerida. **H-031-3 TAINTED INSTANCE REFRESH PLAN READY** ([§38](../task-reports/TASK-031-report.md#38-h-031-3-recovery-state-refresh--plan-refresh-only-de-la-instancia-tainted-2026-10-05)): refresh-only con 36 atributos contrastados con AWS, sin cambios de infraestructura y con el taint conservado; `INSTANCE_REFRESH_PLAN_OK`; sin apply. **STOP de frescura antes del apply** ([§39](../task-reports/TASK-031-report.md#39-h-031-3-recovery-state-refresh-apply--stop-de-frescura-antes-del-apply-2026-10-05)): `latest_restorable_time` avanza solo; decisión requerida. **H-031-3 MOVING ATTRIBUTE CONTRACT READY** ([§40](../task-reports/TASK-031-report.md#40-h-031-3-moving-attribute--contrato-del-atributo-móvil-y-criterio-de-convergencia-2026-10-05)): contrato móvil y `ACTIONABLE_CONVERGENCE_OK` definidos; el mismo plan da `INSTANCE_REFRESH_PLAN_OK` con un describe fresco; sin apply. **H-031-3 STATE REFRESHED / CONVERGENCE REVIEW REQUIRED** ([§41](../task-reports/TASK-031-report.md#41-h-031-3--refresh-only-aplicado-readback-4040-y-untaint-convergencia-en-revisión-2026-10-06)): refresh-only aplicado, readback 40/40, untaint (21/21, 0 taints); convergencia «No changes» con drift móvil, pero la guarda la rechaza por exigir `applyable = true`; corrección propuesta. **H-031-3: convergencia aceptada** ([§42](../task-reports/TASK-031-report.md#42-h-031-3-convergence-guard-fix--guarda-corregida-y-el-mismo-json-aceptado-2026-10-06)): guarda corregida con TDD; el mismo JSON da `ACTIONABLE_CONVERGENCE_OK`, caso B; sin apply. **H-031-3 COMPLETE** ([§43](../task-reports/TASK-031-report.md#43-h-031-3-markdown-link-gate--pin-durable-de-la-gate-de-enlaces-y-cierre-de-h-031-3-2026-10-06)): gate de enlaces completa con un pin durable nuevo (`markdown-it-py` 4.2.0 y `mdurl` 0.1.2, con SHA-256 versionados) y **0 enlaces rotos**; seguridad y regresión en verde; sin cambios en AWS, state ni plan de convergencia. **H-031-5 IMPLEMENTATION READY / LAMBDA QUOTA PENDING** ([§44](../task-reports/TASK-031-report.md#44-h-031-5--ejecutora-privada-de-d-24-por-fases-implementación-offline-y-cuota-lambda-2026-10-06)): ejecutora privada de D-24 por fases, implementada y probada offline (*shell* sin base de datos, solo `sg-admin`, IAM mínimo, RC=1 y 4 recursos nuevos); sin plan productivo porque la cuota de concurrencia sigue en 10. **H-031-5-LAMBDA-QUOTA** ([§45](../task-reports/TASK-031-report.md#45-h-031-5-lambda-quota--rol-vinculado-creado-solicitud-a-101-rechazada-por-aws-2026-10-07)): se creó el rol vinculado de Service Quotas (única mutación) y la solicitud a 101 fue **rechazada por AWS**, que exige un valor mayor que el por omisión (1000); no quedó registrada y la decisión es del usuario. State en serial 8 y 21/21, sin cambios. **REMAINDER — H-031-6 a H-031-9 PREPARADOS OFFLINE / BLOCKERS REMAINING** ([§46](../task-reports/TASK-031-report.md#46-remainder--h-031-6-a-h-031-9-preparados-offline-aws-bloqueado-por-la-cuota-de-lambda-2026-10-07)): ejecutora h0316 (`verify`, `identidades`, `sintetico` y `export`) con artefacto fijado e integración local real en verde; operador, restore PITR, alarmas de D-11 y rol de D-20 preparados como código y módulos no cableados, con pruebas. **Ninguna llamada a AWS**: la cuota de Lambda (10) bloquea todo apply de `terraform-datos` y, por decisión del usuario del 2026-10-07, no se repite la solicitud. Propuestas pendientes de aprobación: mecanismo de credenciales, modos de provisión, D-20 y cierre de R-12. **H-031-8 y H-031-9 — APLICADOS Y CONVERGENTES / BLOCKERS REMAINING** ([§47](../task-reports/TASK-031-report.md#47-h-031-8-y-h-031-9--alarmas-de-d-11-y-rol-de-d-20-aplicados-y-convergentes-2026-10-08-a-2026-10-15)): por decisión del usuario, `terraform-datos` se reordenó: la ejecutora sale del root hasta la cuota, con módulo, artefacto, RC=1 y guarda intactos. Las 8 alarmas de D-11, sin acciones, y el rol `PersonalBlogLecturaGrafana` de D-20 (confianza con ExternalId, solo métricas y alarmas, sin logs) se aplicaron con plan guardado, guarda de lista cerrada, apply exacto, readback, simulación IAM 20/20 y convergencia con las guardas originales. El usuario aprobó una excepción puntual de la ventana móvil y dos refresh-only guardados de normalizaciones del provider. State en serial 12, 31/31. D-19 verificado para integrar: trial sin método de pago y comprobación pendiente al terminar. Hallazgo: la alarma `memoria` está en `ALARM` en reposo, con la calibración pendiente. Siguen B1 (cuota de Lambda: H-031-5, H-031-6 y H-031-7), B3 y B4. «Save & test» de Grafana (2026-10-16): API de métricas validada; la prueba combinada sale en rojo solo por la denegación prevista de logs (`logs:DescribeLogGroups`); Explore con métricas reales de RDS: **PASS** (2026-10-16), con lo que queda validada la ruta Grafana Cloud → AssumeRole → CloudWatch → RDS. Los estados de alarma en Grafana no se han probado: sus anotaciones requieren `DescribeAlarmHistory`, que no se concede. **B1, B3 y B4: DECISIONES DEL USUARIO DEL 2026-10-16** ([§48](../task-reports/TASK-031-report.md#48-bloqueos-b1-b3-y-b4--decisiones-del-usuario-del-2026-10-16)). B1: una única solicitud de cuota de Lambda (1001, con caso permitido); AWS abrió un caso (**CASE_OPENED**), sin tocar D-24 ni RC=1. B3: supervisión manual de solo lectura de los backups, con TDD (25 pruebas) y ejecución real en OK. B4: R-12 sigue **abierto** y documentado, con seguimiento en Task/040; BitLocker queda pendiente de verificación elevada. H-031-5 preparado offline (guarda con la línea base real de 31 recursos, fase `h0315`, refresh-only de normalizaciones y recableado validado). **No** es READY: H-031-5, H-031-6 y H-031-7 siguen sin evidencia de AWS (B1). **D-24 MODIFICADA (2026-10-18) — aprobada por el usuario el 2026-10-19, con la nueva semántica de §40** ([§49](../task-reports/TASK-031-report.md#49-d-24-modificada-y-plan-de-h-031-5-2026-10-18)): la ejecutora vuelve al root **sin concurrencia reservada**; las escrituras administrativas se excluyen con un bloqueo de aviso de PostgreSQL y B1 deja de bloquear, con la solicitud a 1001 abierta. Contrato de §40 enmendado: las 24 h miden la frescura del valor de AWS. **H-031-5 DESPLEGADA Y CONVERGENTE (2026-10-19)** ([§49.15](../task-reports/TASK-031-report.md#4915-aprobación-de-d-24-y-40-y-apply-de-h-031-5-2026-10-19)): apply exacto del plan autorizado (4 creates), *readback* y `selfcheck` exactos, refresh-only preautorizado de normalizaciones y convergencia 0/0/0; state en serial 15, 35/35. La cuota de Lambda ya es 1000. **2026-10-20** ([§50](../task-reports/TASK-031-report.md#50-trabajo-de-codex-retomado-laboratorio-completo-y-preparación-de-h-031-6-y-h-031-7-2026-10-19-y-2026-10-20)): trabajo de Codex retomado y revisado (dos falsos positivos de la guarda de H-031-6 corregidos con TDD); **laboratorio: CICLO COMPLETO** con H-031-6 cableado; gates 32/32; H-031-7 reanudable sin segundo restore. **Plan real de H-031-6 verificado** ([§50.12](../task-reports/TASK-031-report.md#5012-plan-real-de-h-031-6-2026-10-20)): `H0316_PLAN_OK`, 4 creates, 1 update en sitio y 0 destrucciones (SHA-256 `8d1a7307…7a6d`); sin apply. **2026-10-20 y 2026-10-21** ([§51](../task-reports/TASK-031-report.md#51-h-031-6-aplicada-y-verificada-y-h-031-7-completa-2026-10-20-y-2026-10-21)): **H-031-6 APLICADA Y CONVERGENTE** (apply 4/1/0, refresh-only `H0316_REFRESH_OK` y `ACTIONABLE_CONVERGENCE_OK` 0/0/0 sobre 39 recursos) **y SQL CONFORME** (`blog_migrate` y `blog_app` con D-23 y D-12; TLS `verify-full` con controles negativos; DDL rechazado a `blog_app`; `export` validado sin tablas de aplicación); **H-031-7 COMPLETA**: PITR real con integridad `true`, RPO 180 s y RTO 774 s, temporal eliminada con un único `DeleteDBInstance`, marcador retirado, cero residuos y productiva idéntica a su línea base; el incidente del 404 de backups automáticos, corregido con TDD. **CIERRE TÉCNICO COMPLETADO — Lista para validación**: pendiente la revisión del usuario y `approved`. ([reporte §24](../task-reports/TASK-031-report.md#24-h-031-iam--complete-por-decisión-operacional-del-usuario-2026-10-04)) |
| **Repositorios involucrados** | `personal-blog-infra`. Backend y frontend **intactos** en `main` |
| **Dependencias** | `Task/030` — Aprobada el 2026-09-29 (D-06 operativo, EX-028-C7 Extinguida) |
| **Rama** | `Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | `6c31d1d0cc5c0c75de79cc291bbc6e8c2ec6bffc` |
| **Fecha de inicio** | 2026-10-01, America/Guatemala |
| **Última actualización** | 2026-10-03 |

---

## 0. Preparación Git

| # | Comprobación | Resultado |
| --- | --- | --- |
| 1 | `main == origin/main` | Sí: `6c31d1d` tras `fetch --prune` y `pull --ff-only` |
| 2 | Working tree limpio antes de crear la rama | Sí. `dev` contenía a `main` y `git diff main dev` estaba vacío |
| 3 | Rama creada **desde `main`** | Sí |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | Sí: `6c31d1d0cc5c0c75de79cc291bbc6e8c2ec6bffc` |

Backend `9692796` y frontend `7dce98a`, en `main == origin/main`, limpios y sin rama de
tarea. No había ramas Task ni PR abiertos en los tres repositorios.

## 1. Objetivo

Desplegar la red privada y el RDS PostgreSQL de ADR-010 con los valores de D-22, D-23 y D-10,
con una identidad humana autorizada explícitamente —por decisión del usuario, `PersonalBlogAdministrator` mediante
`personal-blog` ([reporte §24](../task-reports/TASK-031-report.md#24-h-031-iam--complete-por-decisión-operacional-del-usuario-2026-10-04))—, el acceso privado de D-24, el restore sintético con PITR,
CloudWatch mínimo (D-11) y la integración D-20, todo con evidencia de AWS real y por
checkpoints autorizados.

## 2. Contexto

Nombre y alcance fijados por `Task/028.2`; valores decididos en el
[paquete de `Task/029`](../architecture/production-postgresql-rds-decisions.md). `Task/030` dejó
D-06 operativo. La preparación (*IMPLEMENTATION PREP*, 2026-10-01) se presentó al usuario,
que autorizó **H-031-1** el 2026-10-03 con las decisiones DH-1 a DH-6 (§12).

## 3. Dentro del alcance

- [x] **H-031-1 — trabajo offline**: root `terraform-datos`, módulos `red` y `base_de_datos`,
      pruebas, guarda del plan, control negativo de DH-2, laboratorio de tres roots,
      diseño exacto de la identidad operativa, CI y documentación durable.
- [x] **H-031-1A — IAM hardening offline**: grupo por omisión sin gestionar ni usar; 21 recursos; simulación desde bootstrap; DN-3 eliminada. **READY FOR H-031-IAM** (2026-10-03). Historia: un primer ciclo quedó **rechazado** por `domain_dns_ips: null → []` no declarado en `resource_drift`, sección que la guarda omitía ([§14.5](../task-reports/TASK-031-report.md#145-ciclo-final-y-punto-de-detención)); sin ampliar tolerancias, se diagnosticó como representación del SDKv2 del provider, la guarda pasó a juzgar `resource_drift` con lista cerrada y un ciclo nuevo y los gates quedaron en verde ([§15](../task-reports/TASK-031-report.md#15-h-031-1a--resolución-del-bloqueo-de-domain_dns_ips-2026-10-03)).
- [x] **H-031-IAM** — crear la identidad operativa mínima con la administrativa **solo** como bootstrap. **COMPLETE el 2026-10-04 por decisión del usuario** ([reporte §24](../task-reports/TASK-031-report.md#24-h-031-iam--complete-por-decisión-operacional-del-usuario-2026-10-04)): operador creado y validado y S-10 aplicada; el operador **no** será el contexto operativo, y Task/031 continúa con `personal-blog` / `PersonalBlogAdministrator`. Historia: **Aplicado; BLOQUEADO en la simulación por S-10** ([reporte §17](../task-reports/TASK-031-report.md#17-h-031-iam--apply-ejecutado-stop-en-la-simulación-2026-10-03)). Antes, con autorización *PLAN ONLY*: STS, preflight —rol vinculado de RDS ausente, caso B—, Access Analyzer sin hallazgos, `init` de la key dedicada, plan de **8 creates** y guarda `PLAN_OK`; **sin apply**, nada creado en AWS ([reporte §16](../task-reports/TASK-031-report.md#16-h-031-iam--plan-guardado-sin-apply-2026-10-03)). Hecho después: apply del binario autorizado (8/0/0) y readback verde. Corrección S-10 diseñada, simulada y planificada; su plan quedó bloqueado por `resource_drift` de metadatos ([reporte §18](../task-reports/TASK-031-report.md#18-h-031-iam-s10-fix--diseño-simulación-y-plan-stop-por-resource_drift-2026-10-03)). Plan refresh-only preparado y revisado, sin aplicar ([reporte §19](../task-reports/TASK-031-report.md#19-h-031-iam-state-refresh--plan-refresh-only-preparado-sin-apply-2026-10-04)). Refresh-only aplicado: exit 1, state persistido con solo los cinco metadatos ([reporte §20](../task-reports/TASK-031-report.md#20-h-031-iam-state-refresh-apply--exit-1-con-state-persistido-stop-2026-10-04)). Corrección S-10 aplicada y verificada ([reporte §22](../task-reports/TASK-031-report.md#22-h-031-iam-s10-fix--aplicada-y-verificada-login-del-operador-pendiente-2026-10-04)); state aceptado y replan en [§21](../task-reports/TASK-031-report.md#21-h-031-iam--state-aceptado-y-nuevo-plan-s-10-sin-apply-2026-10-04)). Pendientes: perfil `personal-blog-datos`, pruebas del operador y convergencia 0/0/0.
- [ ] **H-031-2** — preflight de lectura, `init` remoto y plan guardado, con la identidad operativa. *Desde el 2026-10-04, por decisión del usuario: con `personal-blog` / `PersonalBlogAdministrator`. **Plan listo para revisión del apply** (2026-10-04): 21/0/0, `PLAN_OK`, sin drift, sin apply ([§26](../task-reports/TASK-031-report.md#26-h-031-2--plan-guardado-de-red-y-rds-sin-apply-2026-10-04)). Alineación offline: [§25](../task-reports/TASK-031-report.md#25-h-031-2-align--terraform-datos-exige-personalblogadministrator-2026-10-04)).*
- [x] **H-031-3** — primer apply de red y RDS del plan revisado, readback y convergencia. **COMPLETE el 2026-10-06** ([reporte §43](../task-reports/TASK-031-report.md#43-h-031-3-markdown-link-gate--pin-durable-de-la-gate-de-enlaces-y-cierre-de-h-031-3-2026-10-06)): red y RDS desplegadas tras la recuperación de §27–§41, readback 40/40 + 5/5, serial 8 con 21/21 y 0 taints, `ACTIONABLE_CONVERGENCE_OK` en el caso B (§42) y gate de enlaces completa con 0 rotos.
- [x] **H-031-5** — ejecutora privada de D-24, por fases. **DESPLEGADA Y CONVERGENTE el 2026-10-19** ([reporte §49.15](../task-reports/TASK-031-report.md#4915-aprobación-de-d-24-y-40-y-apply-de-h-031-5-2026-10-19)). Historia: **IMPLEMENTATION READY / LAMBDA QUOTA PENDING** (2026-10-06, [reporte §44](../task-reports/TASK-031-report.md#44-h-031-5--ejecutora-privada-de-d-24-por-fases-implementación-offline-y-cuota-lambda-2026-10-06)): *shell* sin base de datos implementado y probado offline; sin plan productivo hasta que la cuota de concurrencia permita RC=1. La solicitud a 101 fue rechazada por AWS, que exige más de 1000; decisión pendiente ([§45](../task-reports/TASK-031-report.md#45-h-031-5-lambda-quota--rol-vinculado-creado-solicitud-a-101-rechazada-por-aws-2026-10-07)). **2026-10-16 ([reporte §48](../task-reports/TASK-031-report.md#48-bloqueos-b1-b3-y-b4--decisiones-del-usuario-del-2026-10-16)):** solicitud única de cuota a 1001; AWS abrió un caso (`CASE_OPENED`). Guarda con la línea base real (31), fase `h0315`, refresh-only de normalizaciones y recableado validado offline. D-24 y RC=1 sin cambios. **2026-10-18 ([reporte §49](../task-reports/TASK-031-report.md#49-d-24-modificada-y-plan-de-h-031-5-2026-10-18)):** D-24 modificada por el usuario (**aprobada el 2026-10-19**; se consolida con la aprobación de la tarea): la ejecutora no reserva concurrencia y vuelve al root; el plan productivo ya no espera la cuota. La exclusión entre escrituras la garantiza un bloqueo de aviso de PostgreSQL (criterio 10). **2026-10-19:** plan guardado real con `EXECUTOR_PLAN_OK` (4/0/0 sobre 31) y red verificada; sin apply ([§49.8](../task-reports/TASK-031-report.md#49-d-24-modificada-y-plan-de-h-031-5-2026-10-18)).
- [x] **H-031-6** — identidades SQL y TLS `verify-full`. **APLICADA, CONVERGENTE Y SQL CONFORME el 2026-10-20** ([reporte §51](../task-reports/TASK-031-report.md#51-h-031-6-aplicada-y-verificada-y-h-031-7-completa-2026-10-20-y-2026-10-21)). Historia: **Preparado offline** ([reporte §46](../task-reports/TASK-031-report.md#46-remainder--h-031-6-a-h-031-9-preparados-offline-aws-bloqueado-por-la-cuota-de-lambda-2026-10-07)): ejecutora h0316 con `verify`, `identidades`, `sintetico` y `export`, artefacto fijado `98f41bfd…8e43` desde el 2026-10-18 (antes `02cf270d…8ddf`; añade el bloqueo de aviso de D-24, [§49](../task-reports/TASK-031-report.md#49-d-24-modificada-y-plan-de-h-031-5-2026-10-18)), integración local real, operador y módulos `credenciales_sql` y `exportacion` no cableados. **2026-10-20 ([§50](../task-reports/TASK-031-report.md#50-trabajo-de-codex-retomado-laboratorio-completo-y-preparación-de-h-031-6-y-h-031-7-2026-10-19-y-2026-10-20)):** cableado en el root (`credenciales_sql`, `exportacion` y el código h0316), guarda `check_plan_h0316`, refresh-only `check_plan_refresh_h0316` y convergencia `h0316` (39), probados con TDD y en el ciclo completo del laboratorio. **Plan real verificado el 2026-10-20** ([§50.12](../task-reports/TASK-031-report.md#5012-plan-real-de-h-031-6-2026-10-20)): `H0316_PLAN_OK`, 4 creates, 1 update en sitio y 0 destrucciones, SHA-256 `8d1a7307…7a6d`. Pendiente: la autorización consolidada y lo de AWS.
- [x] **H-031-7** — datos sintéticos, PITR, restore, tiempos y limpieza autorizada. **COMPLETA el 2026-10-21** ([reporte §51](../task-reports/TASK-031-report.md#51-h-031-6-aplicada-y-verificada-y-h-031-7-completa-2026-10-20-y-2026-10-21)): PITR real con integridad `true`, RPO 180 s, RTO 774 s, limpieza sin residuos y productiva intacta. Historia: **Preparado offline**: orquestador `scripts/terraform_datos/restore_sintetico.py` con guardas de limpieza y 16 pruebas. **2026-10-20 ([§50](../task-reports/TASK-031-report.md#50-trabajo-de-codex-retomado-laboratorio-completo-y-preparación-de-h-031-6-y-h-031-7-2026-10-19-y-2026-10-20)):** reanudable sin un segundo restore si la sesión caduca durante la espera, más los controles de fallo de Codex (32 pruebas del restore); el operador se autentica con `aws login` (`awscrt` fijado) y el `preflight` real dio OK. Pendiente: la autorización consolidada (fase B de §50.9) y, después, lo de AWS.
- [x] **H-031-8** — alarmas y umbrales de D-11. **APLICADO Y CONVERGENTE el 2026-10-15** ([reporte §47](../task-reports/TASK-031-report.md#47-h-031-8-y-h-031-9--alarmas-de-d-11-y-rol-de-d-20-aplicados-y-convergentes-2026-10-08-a-2026-10-15)): 8 alarmas sin acciones, readback 8/8 y convergencia con la guarda original, tras la excepción puntual de la ventana móvil y un refresh-only guardado, ambos aprobados por el usuario. Pendientes de decisión, sin bloquear la fase: el fallo de backup, que no tiene métrica (B3), y la calibración de `memoria`, que está en `ALARM` en reposo.
- [x] **H-031-9** — D-19 verificada y D-20 implementada. **D-19 verificado para integrar** (trial sin método de pago; comprobación al terminar el trial pendiente). **D-20 APLICADO, VALIDADO Y CONVERGENTE el 2026-10-15**: rol `PersonalBlogLecturaGrafana` con confianza exacta (cuenta de Grafana y `sts:ExternalId`), solo métricas y estados de alarma, simulación IAM 20/20 y convergencia con la guarda original tras un refresh-only guardado aprobado. «Save & test» del 2026-10-16: API de métricas **validada** desde Grafana Cloud; logs denegados por diseño (`AccessDeniedException` en `logs:DescribeLogGroups`); CloudTrail confirma `AssumeRole` solo desde la cuenta de Grafana con su ExternalId. Explore con métricas reales de RDS (`CPUUtilization` de `blog-prod-postgres`): **PASS** el 2026-10-16. Queda validada la ruta Grafana Cloud → AssumeRole → CloudWatch → RDS. Los estados de alarma en Grafana son una validación distinta y no hecha: sus anotaciones requieren `DescribeAlarmHistory`, que no se concede, y ampliarlo exige una decisión ([runbook](../runbooks/grafana-cloudwatch.md) §1.1).
- [ ] Cierre: matriz de paridad, runbooks, R-12, reporte y Lista para validación. Paridad, runbook y reporte actualizados. **R-12: decisión del usuario del 2026-10-16**: sigue ABIERTO y documentado, con seguimiento en `Task/040`. La propuesta de cierre de §46.9 queda sustituida, porque BitLocker solo tiene un indicador sin elevación, que no basta como evidencia.

**H-031-4** es permanente: STOP ante destroy, reemplazo, import, recurso preexistente,
colisión, IAM inesperado —cualquiera que no sea el diseño exacto aprobado—, NAT, servicio
nuevo, CMK, costo fijo imprevisto, drift, lock anómalo o cambio de arquitectura.

## 4. Fuera del alcance

Lambda de aplicación, su execution role, `vpc_config`, `DATABASE_URL`, bundle de la CA y D-12
medida: **`Task/032`**. API Gateway: `Task/033`. Primeras migraciones, R-43 y R-44: `Task/036`.
NAT, IPv4 pública, Internet Gateway, CloudFront, RDS Proxy, IAM DB auth, Multi-AZ, CMK,
Secrets Manager. Backend y frontend no cambian.

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Módulo de red privada | infra | `terraform/modulos/red/` |
| Módulo de RDS y custodia de la master | infra | `terraform/modulos/base_de_datos/` |
| Root de datos, con pruebas, lock y destinos | infra | `terraform-datos/` |
| Guarda offline del plan productivo y sus pruebas | infra | `scripts/terraform_datos/check_plan.py`, `tests/terraform_datos/test_check_plan.py` |
| Control negativo de DH-2 | infra | `tests/terraform_datos/test_secretos.py` |
| Laboratorio de tres roots | infra | `scripts/laboratorio/`, `tests/laboratorio/`, `laboratorio/docker-compose.laboratorio.yml` |
| Bootstrap de la identidad operativa (aplicado en H-031-IAM; conservado **sin uso operativo**, §24) | infra | `bootstrap/operador-datos/` |
| Diseño de la identidad y de H-031-IAM | infra | [identidad-operativa-datos.md](../architecture/identidad-operativa-datos.md) |
| CI | infra | `.github/workflows/ci-infra.yml` |
| Ejecutora privada de D-24, fase H-031-5: módulo, *shell* y empaquetador determinista | infra | `terraform/modulos/ejecutor_privado/`, `scripts/terraform_datos/empaquetar_ejecutor.py` |
| Guarda del plan de H-031-5 y sus pruebas | infra | `scripts/terraform_datos/check_plan_ejecutor.py`, `tests/terraform_datos/test_check_plan_ejecutor.py` |
| Reporte | infra | [TASK-031-report.md](../task-reports/TASK-031-report.md) |

## 6. Criterios de aceptación

1. Red y RDS privados: `publicly_accessible = false`; sin IGW, NAT ni EIP; rutas sin
   `0.0.0.0/0`; grupos por referencia y `sg-rds` sin salida, **leído de la API**. Grupo por omisión no
   gestionado ni usado; RDS solo `sg-rds`; Task/032 adjunta `sg-lambda` y H-031-5 adjunta
   `sg-admin` explícitamente; endpoint S3 Gateway sin SG ni `subnet_ids`.
2. TLS: `rds.force_ssl = 1` en el *parameter group* efectivo; CA `rds-ca-rsa2048-g1` con su
   `ValidTill` registrado.
3. Cifrado con `aws/rds`; ninguna prueba deshabilita ni programa el borrado de una clave.
4. Contraseña master **ausente** del plan, del state y de las salidas, con evidencia.
5. Backups de 7 días, PITR activo y `LatestRestorableTime` avanzando.
6. Identidad operativa mínima creada, validada y usada; la administrativa, solo en el bootstrap.
7. Restore sintético y PITR con integridad, tiempos medidos y limpieza autorizada.
8. CloudWatch D-11 con retención explícita y ≤ 10 alarmas; D-20 tras verificar D-19.
9. Convergencia **0/0/0** tras cada apply; matriz de paridad sin declarar paridad completa.
10. **Serialización de D-24** *(añadido el 2026-10-18; aprobado por el usuario el 2026-10-19)*. Lambda ya no la
    garantiza: la ejecutora no reserva concurrencia. Toda operación SQL administrativa de escritura toma
    `pg_try_advisory_xact_lock(3364, 1)` en su misma conexión antes de escribir; una segunda operación incompatible
    se rechaza con `OPERACION_EN_CURSO` y sin efectos; el bloqueo se libera al terminar la transacción o la sesión;
    ningún error provoca una reejecución; los modos de lectura no lo toman. El bloqueo no protege operaciones de
    AWS (restore, PITR, *snapshots*), que conservan sus guardas.

> **Estado final del 2026-10-21, pendiente del `approved`.** Matriz completa en el [reporte §51.16](../task-reports/TASK-031-report.md#5116-matriz-final-de-aceptación-excepciones-y-evidencia-del-cierre-2026-10-21).
> - **Cumplidos:** 1, 2, 3, 4, 7, 9 y 10. El 9 se cumple en sus términos: convergencia 0/0/0 tras cada apply y matriz de paridad **sin** declarar paridad completa. Quedan explícitos los componentes `AWS-only` y `No evaluada`, y que no hubo pruebas de *failover*.
> - **Con excepción**: **no se cumplen tal como se redactaron**. Tienen desviaciones respecto del requisito original y solo se cierran con su aceptación expresa al aprobar:
>   - **5:** backups de 1 día, como excepción temporal del plan FREE; el objetivo es volver a 7 días al pasar al plan PAID.
>   - **6:** `PersonalBlogAdministrator` como identidad operativa autorizada (reporte §24).
>   - **8:** alarmas sin acciones, sin alertamiento efectivo; fallo de *backup* con supervisión manual (B3); `memoria` sin calibrar. El alertamiento efectivo (canales aprobados, alarmas conectadas y recepción probada) y la calibración de `memoria` pasan a **`Task/040`**, con **D-11 abierta** hasta verificarlos. **D-19 abierta**, con la comprobación al terminar el trial de Grafana en **`Task/041`**.
> - **Limitación de la prueba:** la exportación a S3 se validó **sin tablas de aplicación**; la exportación de datos reales queda para **`Task/036`** y **`Task/040`**.

## 7. TDD / Plan test-first

**No aplica la BACKEND TEST-FIRST LAW**: no hay comportamiento funcional del backend. Sí hay
pruebas primero sobre la infraestructura: las pruebas offline del root, de la guarda y del
bootstrap se escribieron con sus controles negativos, y el laboratorio actuó como prueba de
integración. Tres fallos reales que las pruebas detectaron y se corrigieron están en el
[reporte](../task-reports/TASK-031-report.md) §8.

## 8. Plan de validación

Offline (fmt, validate, `terraform test`, guardas Python, CI). Laboratorio Floci con tres roots.
AWS real solo a partir de H-031-IAM, con plan guardado, guarda, revisión humana y readback.

## 9. Comandos de validación

```text
terraform -chdir=terraform-datos fmt -check -recursive
terraform -chdir=terraform-datos init -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform-datos validate
terraform -chdir=terraform-datos test
terraform -chdir=bootstrap/operador-datos fmt -check -recursive
terraform -chdir=bootstrap/operador-datos init -backend=false -input=false -lockfile=readonly
terraform -chdir=bootstrap/operador-datos validate
terraform -chdir=bootstrap/operador-datos test
python -B -m unittest discover -s tests/terraform_datos -v
python -B -m unittest discover -s tests/laboratorio -p "test_*.py"
python -B scripts/laboratorio/laboratorio.py --modo local ciclo --lambda-zip <ZIP canónico>
git diff --check
```

## 10. Evidencia esperada

Planes, JSON y logs de AWS **privados**, fuera de Git; en el reporte solo hashes, direcciones,
conteos y resúmenes saneados. Nunca credenciales, Account ID, contraseñas ni volcados.

## 11. Riesgos

| Riesgo | Mitigación |
| --- | --- |
| Un permiso que falta detiene el apply a medias | Simulación en H-031-IAM; STOP y corrección en un checkpoint de IAM, nunca ampliando por conveniencia |
| Drift de `ingress`/`egress` en los grupos tras el primer apply (reglas gestionadas aparte) | Si AWS lo demuestra: STOP, evidencia y refresh-only revisado, con autorización explícita posterior; nunca preautorizado. DN-2 del reporte, §12 |
| La contraseña acaba en el state | Atributos *write-only*, guarda del plan, control negativo y escaneo del state real |
| Costo fijo de RDS desde el primer apply (≈ 0.46 USD/día) | EX-029-D13 Vigente; R-47 y el gate del 2027-03-15 |
| El emulador no representa RDS ni la revocación de salidas | Registrado en la matriz como `Paridad parcial`/`AWS-only`; validación en AWS real |
| Dos operaciones administrativas simultáneas, sin concurrencia reservada (D-24 modificada el 2026-10-18, aprobada el 2026-10-19) | Bloqueo de aviso de transacción en la misma conexión, rechazo inmediato `OPERACION_EN_CURSO`, sin reintentos; criterio 10 |

## 12. Decisiones técnicas

**Propuesta — pendiente de aprobación** hasta el cierre de la tarea:

| Decisión | Estado tras H-031-1 |
| --- | --- |
| DH-1 — root `terraform-datos`, key `application/data/terraform.tfstate`, orden medios → datos → aplicación | Aprobada por el usuario; implementada offline |
| DH-2 — contraseña efímera, `password_wo` y `value_wo` con `aws/ssm` | Aprobada; implementada y demostrada offline y en el laboratorio |
| DH-3 — identidad operativa mínima; la administrativa solo como bootstrap | **Modificada** por el usuario. El operador se **creó y validó** en H-031-IAM; el 2026-10-04 el usuario decidió operar el resto de Task/031 con `personal-blog` / `PersonalBlogAdministrator` (§24 del reporte) |
| DH-4 — política del endpoint, Extended Support deshabilitado, backups conservados, logs 14 días, drift visible, AZ IDs | Aprobada con condiciones. H-031-1A sustituye la gestión del SG por omisión por **no gestión y no uso**, según la decisión del usuario; DN-3 cerrada. La orderabilidad se confirma en H-031-2 |
| DH-5 — laboratorio antes de H-031-3 | Aprobada; ejecutada de verdad |
| DH-6 — ejecutora solo en H-031-5 | Aprobada con frontera; fuera de H-031-1. **H-031-5 por fases** ([reporte §44](../task-reports/TASK-031-report.md#44-h-031-5--ejecutora-privada-de-d-24-por-fases-implementación-offline-y-cuota-lambda-2026-10-06)): *shell* sin base de datos; credenciales y `verify` en H-031-6; Alembic y migraciones en Task/036 |

## 13. Documentación creada o actualizada

Nueva: esta ficha, el reporte e [identidad-operativa-datos.md](../architecture/identidad-operativa-datos.md).
Actualizada: STATUS, ROADMAP, STAGE-10, [aws-local-parity](../architecture/aws-local-parity.md)
(§4.1.1.1, §6.9 y matriz), [paquete de decisiones](../architecture/production-postgresql-rds-decisions.md)
(enmienda a §12.2), [open-decisions](../architecture/open-decisions.md) (D-11),
[bucket de estado](../runbooks/terraform-state-bootstrap.md) (keys) y los cinco runbooks del laboratorio.

## 14. Archivos modificados

Inventario completo en el [reporte](../task-reports/TASK-031-report.md) §4.

## 15. Resultado de pruebas

H-031-1: `terraform-datos` **22/22**, `bootstrap/operador-datos` **7/7**, el resto de roots sin
cambios y en verde; Python: laboratorio **263 OK**, `terraform_datos` **24 OK**,
`terraform_state` **12 OK**, `oidc` **60 OK** (1 *skip* de plataforma), `security` **88 OK**;
ciclo real de tres roots **exit 0**; Gitleaks sin hallazgos con control positivo. Detalle en
el [reporte](../task-reports/TASK-031-report.md) §11.

## 16. Problemas encontrados

Nueve hallazgos del laboratorio y de las pruebas, todos resueltos sin deformar el diseño de AWS:
formato de ID de zona del emulador, revocación de salidas no aplicada por Floci, referencia de
grupo con prefijo de cuenta, atributos de RDS no devueltos, la variable efímera que hay que
repetir al aplicar un plan guardado, el tamaño de la política inline y otros. Ver el
[reporte](../task-reports/TASK-031-report.md) §8.

En H-031-1A, el gate de idempotencia del laboratorio **no leía `resource_drift`** y un ciclo
quedó rechazado por `domain_dns_ips: null → []` no declarado. Se diagnosticó como
representación del SDKv2 del provider —no del emulador— y la guarda pasó a juzgar esa sección
con una lista cerrada y controles negativos; la guarda productiva no cambió. Ver el
[reporte §15](../task-reports/TASK-031-report.md#15-h-031-1a--resolución-del-bloqueo-de-domain_dns_ips-2026-10-03).

## 17. Pasos de validación para el usuario

El gate de H-031-1A quedó resuelto (§15 del reporte) y **H-031-IAM está COMPLETE** (§24): S-10 aplicada y
verificada; por decisión operacional del usuario, Task/031 continúa con `personal-blog` /
`PersonalBlogAdministrator`. `terraform-datos` y su guarda ya exigen exactamente esa identidad (§25). H-031-2 tiene
su plan guardado listo (§26). H-031-3 se aplicó y falló en el parameter group (§27.4). H-031-3-RECOVERY (§28): D-22 corregida, preflight del catálogo
(`check_parametros.py`) y guarda de recuperación (`check_plan_recuperacion.py`); plan 2/0/1 sin apply, **DN-2 DRIFT
REVIEW REQUIRED**. H-031-3-RECOVERY-DN2 (§29): refresh-only con guarda propia (`check_plan_dn2.py`),
rechazado por `OUTPUTS`; sin apply. H-031-3-RECOVERY-DN2-OUTPUTS (§30): contrato de salidas ampliado;
**DN-2 REFRESH PLAN READY**, sin apply. §31: refresh-only aplicado y nuevo plan de recuperación `RECOVERY_PLAN_OK`;
sin recovery apply. Antes: **H-031-3**, el apply de ese binario exacto,
con la contraseña real generada según §25.4, readback y convergencia. DN-2 registra
una preferencia condicionada —el diagnóstico anticipa que AWS probablemente la active por
`domain_dns_ips`—; DN-3 está cerrada por eliminación.

## 18. Deuda técnica pendiente

Las fases H-031-IAM a H-031-9 y el cierre. R-12 sigue abierto.

> **Actualización del 2026-10-15.** H-031-8 y H-031-9 están aplicados y convergentes (reporte §47). Quedan:
> - B1, la cuota de Lambda, que bloquea la evidencia de AWS de H-031-5, H-031-6 y H-031-7;
> - B3, el fallo de backup sin métrica;
> - B4, R-12;
> - la calibración de la alarma `memoria`;
> - la comprobación de D-19 al terminar el trial de Grafana.
>
> **Actualización del 2026-10-18** ([reporte §49](../task-reports/TASK-031-report.md#49-d-24-modificada-y-plan-de-h-031-5-2026-10-18)). Con D-24 modificada (Propuesta — pendiente de
> aprobación), B1 deja de bloquear: la solicitud a 1001 sigue abierta, pero ya no es requisito. Quedan:
> - ~~el apply de H-031-5~~: desplegada y convergente el 2026-10-19; quedan H-031-6 y H-031-7 en AWS;
> - ~~la aprobación de D-24 y de §40~~: concedida por el usuario el 2026-10-19;
> - B3, B4, la calibración de `memoria` y D-19, sin cambios.
>
> **Actualización del 2026-10-21** ([reporte §51](../task-reports/TASK-031-report.md#51-h-031-6-aplicada-y-verificada-y-h-031-7-completa-2026-10-20-y-2026-10-21)). H-031-6 y H-031-7 están completas en AWS y el cierre técnico está COMPLETADO. Quedan:
> - la revisión del usuario, la aceptación de las desviaciones documentadas y `approved`;
> - ~~antes del *commit*, versionar `terraform/modulos/ejecutor_privado/codigo_h0316/rds-ca-us-east-2.pem`, la CA pública de RDS, que ignora la regla `*.pem`~~: resuelto el 2026-10-21 con la excepción exacta en `.gitignore` (reporte §51.15);
> - seguimientos fuera de esta tarea, que no la bloquean ([reporte §51.16](../task-reports/TASK-031-report.md#5116-matriz-final-de-aceptación-excepciones-y-evidencia-del-cierre-2026-10-21)):
>   - el alertamiento efectivo de RDS (canales aprobados, alarmas conectadas y recepción probada) y la calibración de `memoria`, en **`Task/040`**, con **D-11 abierta** hasta verificarlos;
>   - D-19, con la comprobación al terminar el trial de Grafana, en **`Task/041`**;
>   - R-12 (B4), en **`Task/040`**;
>   - la exportación con tablas de aplicación, en **`Task/036`** y **`Task/040`**;
>   - la retención de 7 días, al pasar al plan PAID.
>
>   La supervisión manual de los *backups* (B3) sigue vigente.

## 19. Próxima tarea

`Task/032-Desplegar-AWS-Lambda`, solo después de aprobar y cerrar esta.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| Fecha de aprobación | — |
| Aprobado por | — |
| Expresión de aprobación final | `approved: Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch` — **no concedida** |
