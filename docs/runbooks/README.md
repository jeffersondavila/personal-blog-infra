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
| [github-oidc-bootstrap.md](github-oidc-bootstrap.md) | AWS real futuro; bootstrap OIDC aislado | **Borrador operativo Task/028, no ejecutado**; solo diseño/local autorizado |
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
> real:** el modo `production` permanece **bloqueado**, el bucket S3 del backend de
> estado **no existe**, y privacidad de S3, *enforcement* de IAM y cifrado real siguen
> siendo AWS-only hasta la ETAPA 10.
