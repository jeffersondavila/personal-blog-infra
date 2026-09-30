# Runbooks

Procedimientos operativos del proyecto: cómo se levanta, se detiene, se verifica, se
diagnostica y se recupera cada entorno.

---

## Qué es un runbook

Un documento de **operación**, no de diseño. Responde a *cómo se hace*, con comandos
exactos y reproducibles, y con el resultado esperado de cada uno.

| Documento | Propósito |
| --- | --- |
| `docs/architecture/` | Cómo está construido el sistema. |
| `docs/runbooks/` | Cómo se opera el sistema. |
| `docs/tasks/` | Qué se hizo en cada tarea. |

---

## Reglas

- Los comandos deben poder copiarse y ejecutarse tal cual.
- Cada procedimiento indica su resultado esperado.
- Los procedimientos destructivos se marcan explícitamente como tales.
- Ningún runbook contiene credenciales reales: solo nombres de variable.
- Si un procedimiento no ha sido ejecutado y verificado, se dice.

---

## Índice

| Runbook | Entorno | Estado |
| --- | --- | --- |
| [terraform-state-bootstrap.md](terraform-state-bootstrap.md) | AWS real; bootstrap D-06 separado | **Task/030 Lista para validación** (2026-09-29): **H-030-2 COMPLETO** — states migrados y validados, locking y recovery probados, locales retirados y **EX-028-C7 Extinguida**; incluye el retorno de `terraform-medios` a S3 tras usar el laboratorio. Tarea aún sin aprobar |
| [github-oidc-bootstrap.md](github-oidc-bootstrap.md) | AWS real; bootstrap OIDC aislado | Ejecutado en `Task/028`; su state pasó a S3 en **Task/030 H-030-2** y **EX-028-C7 quedó Extinguida** el 2026-09-28. Su §2 se conserva como historia |
| [rds-private-administration.md](rds-private-administration.md) | AWS real futuro; migraciones, purga y restore por canal privado sobre RDS | **Vigente** — aprobado en `Task/029` (2026-09-27); **no ejecutado**: no existe RDS ni ejecutor |
| [local-environment.md](local-environment.md) | Local (Docker Compose) | **Vigente** — aprobado en `Task/003` (2026-07-29) |
| [local-backup-and-recovery.md](local-backup-and-recovery.md) | Local (backup y recuperación) | **Vigente** — aprobado en `Task/004` (2026-07-31) |
| [deployment-create.md](deployment-create.md) | Laboratorio AWS local; transición AWS preparada | **Vigente** — aprobado en `Task/026` (2026-09-15) |
| [deployment-validate.md](deployment-validate.md) | Laboratorio AWS local; gates AWS-only identificados | **Vigente** — aprobado en `Task/026` (2026-09-15) |
| [deployment-rollback.md](deployment-rollback.md) | Laboratorio AWS local | **Vigente** — aprobado en `Task/026` (2026-09-15) |
| [deployment-destroy.md](deployment-destroy.md) | Laboratorio AWS local | **Vigente** — aprobado en `Task/026` (2026-09-15) |
| [deployment-recovery.md](deployment-recovery.md) | Laboratorio AWS local; transición AWS preparada | **Vigente** — aprobado en `Task/026` (2026-09-15) |

La operación contra AWS real sigue pendiente según el roadmap:

| Alcance pendiente | Tarea |
| --- | --- |
| Bootstrap de identidad OIDC, separado de los contratos de aplicación | Task/028, previa autorización específica; runbook sin ejecución real |
| Ejecutar y validar estos contratos contra AWS real | ETAPA 10 (`Task/030`–`Task/033`) |

> Los cinco runbooks de `Task/026` son **Vigentes** desde el 2026-09-15 y están
> ejercitados contra el laboratorio AWS local. **Vigente no significa validado en AWS
> real:** el modo `production` permanece **bloqueado**. El bucket S3 de state ya existe
> por H-030-1 (2026-09-28); sus controles se verificaron por API. H-030-2 migró y validó
> los **dos** states de bootstrap contra ese bucket, con lock nativo y sin DynamoDB.
> La **contención** de ese lock y el **recovery** por versión quedaron demostrados, y
> **EX-028-C7 quedó Extinguida** el 2026-09-28 con S3 como única fuente operacional.
> Esto no valida los contratos de aplicación ni los controles AWS de los demás
> servicios.

## Ampliación RDS — Task/028.2

Los cinco runbooks de despliegue conservan evidencia del grafo Task/026.
Task/031 los ampliará para red/RDS y restore antes de usarlos; Task/036/038 para
migraciones privadas; Task/040 para DR integral. [Contrato](../architecture/production-postgresql-rds.md).
