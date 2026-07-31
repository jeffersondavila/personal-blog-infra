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
| [local-environment.md](local-environment.md) | Local (Docker Compose) | **Vigente** — aprobado en `Task/003` (2026-07-29) |
| [local-backup-and-recovery.md](local-backup-and-recovery.md) | Local (backup y recuperación) | **Vigente** — aprobado en `Task/004` (2026-07-31) |

Pendientes según el roadmap:

| Runbook previsto | Tarea |
| --- | --- |
| Despliegue, rollback y destrucción en la nube | `Task/026-Runbooks-de-Despliegue` |
