# ETAPA 08 — Preparación Cloud sin Cuentas

| Campo | Valor |
| --- | --- |
| **Número** | 08 |
| **Estado** | Pendiente |
| **Dependencias** | [ETAPA 07](STAGE-07-local-validation.md) |
| **Tareas** | 4 |
| **Aprobadas** | 0 |
| **Avance** | 0 % |
| **Hito que completa** | Artefactos e infraestructura como código listos y validados en seco. |

---

## Objetivo

Dejar todo preparado para la nube —adaptador Lambda, artefacto desplegable, Terraform y
runbooks— **sin crear cuentas ni recursos reales**.

## Por qué esta etapa existe

Separar "preparar" de "desplegar" permite corregir errores de empaquetado y de IaC
mientras el costo sigue siendo cero, y llegar a la Etapa 10 sin sorpresas.

## Tareas

### `Task/023-Compatibilidad-FastAPI-Lambda` — *Pendiente*

Adaptador de FastAPI para API Gateway HTTP API y AWS Lambda, manteniendo la ejecución
local sin cambios.

**Depende de:** `Task/022`. **Repositorio:** `personal-blog-backend`.

### `Task/024-Artefacto-ZIP-Lambda` — *Pendiente*

Paquete ZIP reproducible para Linux, validación de tamaño frente a los límites de
Lambda y checksums.

**Depende de:** `Task/023`. **Repositorio:** `personal-blog-backend`.

### `Task/025-Terraform-Cloud` — *Pendiente*

Módulos Terraform para Cloudflare y AWS, validados con `fmt` y `validate`, sin crear
recursos reales.

**Depende de:** `Task/022`. **Repositorio:** `personal-blog-infra`.

### `Task/026-Runbooks-de-Despliegue` — *Pendiente*

Procedimientos escritos de creación, validación, rollback, destrucción y recuperación.

**Depende de:** `Task/024`, `Task/025`. **Repositorio:** `personal-blog-infra`.

## Criterios de salida de la etapa

- [ ] El backend responde igual ejecutado localmente y a través del adaptador Lambda.
- [ ] El ZIP se construye de forma reproducible y respeta los límites de tamaño.
- [ ] Los checksums del artefacto se registran.
- [ ] `terraform fmt -check` y `terraform validate` pasan en todos los módulos.
- [ ] **Ningún recurso cloud ha sido creado.**
- [ ] Existe un runbook para cada operación: crear, validar, revertir, destruir, recuperar.
- [ ] Los runbooks incluyen el criterio de decisión para hacer rollback.

## Fuera del alcance de la etapa

- Crear cuentas AWS o Cloudflare (Etapa 09).
- `terraform apply` (Etapa 10).
- Configurar DNS (Etapa 10).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Dependencias nativas de Python incompatibles con el runtime de Lambda. | Construcción del paquete en entorno Linux equivalente al runtime destino. |
| Arranque en frío lento por artefacto pesado. | Medición de tamaño y poda de dependencias en `Task/024`. |
| Terraform validado en seco que falla en el primer `apply` real. | Runbooks con verificación paso a paso y rollback definido. |
| Estado de Terraform sin backend remoto definido. | Decisión de backend explícita en `Task/025`. |

## Siguiente etapa

[ETAPA 09 — Cuentas y Seguridad Cloud](STAGE-09-cloud-accounts.md)
