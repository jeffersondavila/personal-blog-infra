# ETAPA 08 — Preparación Cloud + AWS Local Parity

| Campo | Valor |
| --- | --- |
| **Número** | 08 |
| **Estado** | Pendiente |
| **Dependencias** | [ETAPA 07](STAGE-07-local-validation.md) |
| **Tareas** | 4 |
| **Aprobadas** | 0 |
| **Avance** | 0 % |
| **Hito que completa** | Artefactos e infraestructura como código listos y **ejecutados en un laboratorio AWS local**, sin cuentas ni recursos reales. |

> **Nota de alcance — 2026-08-15.** El nombre y el objetivo de la etapa se ampliaron en
> `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` (mantenimiento). Las **4 tareas
> conservan sus identificadores y nombres**: no se añadió, eliminó ni renumeró ninguna, y
> el roadmap sigue teniendo **41 tareas**. Estrategia completa:
> [aws-local-parity.md](../architecture/aws-local-parity.md) ·
> [ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) — **Aceptada** ✔ (2026-08-15).

---

## Objetivo

Dejar todo preparado para la nube —adaptador Lambda, artefacto desplegable, Terraform y
runbooks— **sin crear cuentas ni recursos reales**, y **validar la infraestructura como
código ejecutándola de verdad contra un emulador AWS local**.

## Por qué esta etapa existe

Separar "preparar" de "desplegar" permite corregir errores de empaquetado y de IaC
mientras el costo sigue siendo cero, y llegar a la Etapa 10 sin sorpresas.

Hasta el 2026-08-15 esa validación se limitaba a `terraform fmt` y `terraform validate`,
que comprueban **sintaxis, no comportamiento**: no crean nada, no ejercitan permisos y no
demuestran que `apply` o `destroy` funcionen. El primer `apply` real habría ocurrido en
producción, con la factura abierta, sobre una IaC nunca ejecutada.

El **AWS Local Parity Lab** cierra ese hueco: la misma definición de Terraform se aplica
contra un destino local, se inspecciona, se rompe a propósito y se reconstruye — **sin
cuenta AWS y sin costo**. AWS real sigue siendo la **autoridad final**: lo que funcione en
el laboratorio es una hipótesis hasta que la ETAPA 10 lo confirme.

## Tareas

### `Task/023-Compatibilidad-FastAPI-Lambda` — *Pendiente*

Adaptador de FastAPI para API Gateway HTTP API y AWS Lambda, manteniendo la ejecución
local sin cambios. Se prepara además la compatibilidad para **ejecutarse bajo la Lambda
emulada** del laboratorio.

**Depende de:** `Task/022`. **Repositorio:** `personal-blog-backend`.

### `Task/024-Artefacto-ZIP-Lambda` — *Pendiente*

Paquete ZIP reproducible para Linux, validación de tamaño frente a los límites de
Lambda y checksums. El artefacto pasa a ser **validable ejecutándolo** en el laboratorio
local, no solo medido.

**Depende de:** `Task/023`. **Repositorio:** `personal-blog-backend`.

### `Task/025-Terraform-Cloud` — *Pendiente*

Terraform **portable** con el provider oficial de AWS: una sola definición, dos destinos
—configuración local hacia el emulador, configuración real hacia AWS— con módulos
compartidos y **sin duplicar el grafo de recursos**.

Alcance ampliado: `plan`, `apply` y `destroy` **ejecutados localmente** sobre S3, SSM, IAM,
Lambda, API Gateway v2 y CloudWatch **cuando el soporte y la fidelidad lo permitan**;
[matriz de paridad](../architecture/aws-local-parity.md) rellenada con evidencia real; y
**guardas *fail-closed*** que impidan que un comando pensado para el laboratorio termine
hablando con AWS real. **Cero recursos AWS reales.**

Aquí se resuelve **D-06** (backend de estado de Terraform), no antes.

Además, **`Task/025` amplía el workflow de CI creado en `Task/021`** con `terraform fmt`
y `terraform validate`: son sus primeros archivos `.tf` y por tanto la primera vez que
esas verificaciones tienen algo real que comprobar.

**Depende de:** `Task/022` **y `Task/024`**. **Repositorio:** `personal-blog-infra`.

> **Por qué también de `Task/024`** (corregido en `Task/005.5`). Los criterios de esta
> tarea exigen aplicar y ejercitar **Lambda + API Gateway v2** contra el destino local.
> Eso necesita un **artefacto desplegable real**, que produce `Task/024` —y que a su vez
> depende del adaptador de `Task/023`—. Con la dependencia anterior, `Task/025` podía
> declararse lista sin que existiera nunca el artefacto que sus propios criterios
> ejercitan. La [matriz de paridad](../architecture/aws-local-parity.md) §7 ya reflejaba
> esta realidad: la fila **Lambda** se valida en `Task/024`, `Task/025` → `Task/032`.

### `Task/026-Runbooks-de-Despliegue` — *Pendiente*

Procedimientos escritos de creación, validación, rollback, destrucción y recuperación,
ampliados con: levantar el laboratorio, **validar el destino antes de actuar**,
`init`/`plan`/`apply`, inspección con AWS CLI/SDK, *drift* controlado, `destroy`,
reconstrucción, *troubleshooting*, transición futura a AWS real y **qué hacer cuando el
emulador no tenga paridad suficiente**.

**Depende de:** `Task/024`, `Task/025`. **Repositorio:** `personal-blog-infra`.

## Criterios de salida de la etapa

- [ ] El backend responde igual ejecutado localmente y a través del adaptador Lambda.
- [ ] El ZIP se construye de forma reproducible y respeta los límites de tamaño.
- [ ] Los checksums del artefacto se registran.
- [ ] `terraform fmt -check` y `terraform validate` pasan en todos los módulos.
- [ ] La definición de Terraform es **una sola**, con las diferencias local/AWS confinadas
      a la tabla de diferencias legítimas de [aws-local-parity.md](../architecture/aws-local-parity.md) §4.4.
- [ ] `terraform init`, `plan` y `apply` **se ejecutan** contra el destino local.
- [ ] Los recursos creados se **inspeccionan** con AWS CLI o SDK.
- [ ] `terraform destroy` elimina el entorno y se **verifica la ausencia** de los recursos.
- [ ] `terraform apply` **reconstruye** todo desde cero.
- [ ] Se introduce al menos un ***drift* controlado** y se observa la reconciliación.
- [ ] La **matriz de paridad** queda rellenada con evidencia real, sin ninguna celda de
      «paridad completa».
- [ ] Existen **guardas *fail-closed*** que impiden actuar sobre AWS real por accidente.
- [ ] La versión del emulador está **fijada**, nunca `latest`.
- [ ] **Ningún recurso cloud ha sido creado. Ninguna cuenta AWS ha sido creada.**
- [ ] **No se han usado credenciales AWS reales** en ningún punto de la etapa.
- [ ] Existe un runbook para cada operación: crear, validar, revertir, destruir, recuperar.
- [ ] Los runbooks incluyen el criterio de decisión para hacer rollback.

## Fuera del alcance de la etapa

- Crear cuentas AWS o Cloudflare (Etapa 09).
- `terraform apply` **contra AWS real** (Etapa 10).
- Configurar DNS (Etapa 10).
- Seleccionar el proveedor de VPS de la base de datos de producción (`Task/029`, **D-01**).
  Que el emulador soporte RDS **no** decide nada: desde
  [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md) (**Aceptada**) **RDS ya no es
  el destino de producción**, y `Task/025` **no debe crear recursos RDS**.
- Verificar el **mínimo privilegio** de las políticas IAM: es **AWS-only**, porque el
  emulador no aplica políticas por omisión.
- Dimensionar la Lambda a partir de mediciones locales: el arranque en frío del laboratorio
  no es comparable con el de AWS.

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Dependencias nativas de Python incompatibles con el runtime de Lambda. | Construcción del paquete en entorno Linux equivalente al runtime destino. |
| Arranque en frío lento por artefacto pesado. | Medición de tamaño y poda de dependencias en `Task/024`. **Medido en AWS real**, nunca en el laboratorio. |
| Terraform validado en seco que falla en el primer `apply` real. | **Mitigación principal de la etapa:** `apply` real contra el destino local, más runbooks con verificación paso a paso y rollback definido. |
| Estado de Terraform sin backend remoto definido. | Decisión **D-06** explícita en `Task/025`. |
| **Falsa sensación de paridad** (R-20). | La matriz nace en `No evaluada`; prohibido el estado «paridad completa»; AWS real es la autoridad final. |
| **El camino crítico —Terraform + API Gateway v2 + Lambda + Logs— no está cubierto por la suite oficial de compatibilidad del emulador** (R-25). | Es el objetivo explícito de `Task/025`. Si no se logra, esos recursos pasan a `AWS-only` y se documenta, sin fabricar sustitutos locales. |
| **Actuar sobre AWS real por accidente** al faltar un endpoint (R-24). | Guardas *fail-closed* obligatorias antes del primer `apply` ([aws-local-parity.md](../architecture/aws-local-parity.md) §9.3). |
| **Privilegio de nivel host**: el emulador necesita el socket de Docker (R-22). | Mismo tratamiento que Portainer: solo local, nunca expuesto, compromiso = incidente de nivel host. |
| **IAM sin aplicación de políticas** en local (R-28). | El laboratorio valida creación y adjunción, nunca autorización. Mínimo privilegio queda para `Task/028` y `Task/032`. |

## Siguiente etapa

[ETAPA 09 — Cuentas y Seguridad Cloud](STAGE-09-cloud-accounts.md)
