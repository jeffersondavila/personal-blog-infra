# ETAPA 08 — Preparación Cloud + AWS Local Parity

| Campo | Valor |
| --- | --- |
| **Número** | 08 |
| **Estado** | **En progreso** desde el 2026-09-13 (`Task/023`); `Task/024` **Aprobada** el 2026-09-13; `Task/025` **Aprobada** el 2026-09-14. Las **Aprobadas** pasan de **2** a **3**. **La etapa NO queda completada:** `Task/026` sigue **Pendiente, no iniciada** |
| **Dependencias** | [ETAPA 07](STAGE-07-local-validation.md) |
| **Tareas** | 4 |
| **Aprobadas** | **3** |
| **Avance** | **75 %** |
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

### `Task/023-Compatibilidad-FastAPI-Lambda` — **Aprobada** el 2026-09-13

Adaptador de FastAPI para API Gateway HTTP API y AWS Lambda, manteniendo la ejecución
local sin cambios. Se prepara además la compatibilidad para **ejecutarse bajo la Lambda
emulada** del laboratorio.

**Aprobada** el 2026-09-13 mediante `approved: Task/023-Compatibilidad-FastAPI-Lambda`.
Entrega `app/lambda_handler.py` —**un archivo** más una línea de `pyproject.toml`— sobre
`mangum==0.22.0` con `lifespan="off"`, decidido tras verificar la fuente de la versión
fijada. `app/main.py`, el `Dockerfile` y el Compose **no cambian**, y `uvicorn app.main:app`
sigue siendo el entrypoint local. **T-04 Satisfecho y Vigente**; **P-06 revalidado**.
**42 pruebas nuevas** y el flujo administrativo real recorrido a través del *handler*.
**Con ella la etapa queda 1 de 4 — 25 %; no está completada.**

**Depende de:** `Task/022` ✔ (**Aprobada** el 2026-09-12).
**Repositorios:** `personal-blog-backend` —propiedad funcional— e infra (documentación).
`personal-blog-frontend` **no participa**.
[Ficha](../tasks/TASK-023-fastapi-lambda-compatibility.md) ·
[Reporte](../task-reports/TASK-023-report.md).

> **Corrección del campo *Repositorio* — 2026-09-13 (`Task/023`).** Decía
> `personal-blog-backend` en singular. El campo describe la **propiedad funcional**, que no
> cambia, pero omitía el repositorio de documentación que
> [`WORKFLOW.md`](../project-management/WORKFLOW.md) §6 y §7 hacen obligatorio en **toda**
> tarea. STAGE-06 ya lo declaraba correctamente para la tarea backend comparable
> (`Task/020`: «**Repositorios:** `personal-blog-backend` e infra (documentación)»).
> `Task/024`, más abajo, arrastraba la misma omisión y quedó anotada para su propio
> preflight, sin que esta tarea auditara su contenido.
>
> **Cierre de esa anotación — 2026-09-13 (`Task/024`, D-024-1).** La entrada de `Task/024`
> declara ya sus dos repositorios. Su **propiedad funcional sigue siendo
> `personal-blog-backend`**.

### `Task/024-Artefacto-ZIP-Lambda` — **Aprobada** el 2026-09-13

Paquete ZIP reproducible para Linux, validación de tamaño frente a los límites de
Lambda y checksums. El artefacto pasa a ser **validable ejecutándolo**, no solo medido.

**Aprobada** el 2026-09-13 mediante `approved: Task/024-Artefacto-ZIP-Lambda`: el avance
pasa a **24/41 ≈ 59 %** y la etapa a **2 de 4 — 50 %**. **La etapa no está completada.** Entrega `scripts/empaquetar_lambda.py` y su *harness* de arranque
aislado. Las dependencias se instalan **dentro de la imagen oficial del runtime de Lambda
para Python 3.12, `linux/amd64`, fijada por digest** —el backend se desarrolla en Windows y
**13** de sus **41** distribuciones de ejecución traen binarios nativos—, con
`--require-hashes`, `--only-binary=:all:` y `--no-compile`. Dos construcciones
independientes produjeron **el mismo SHA-256 y los mismos bytes**:
**43 288 578** comprimidos (41,28 MiB) y **114 086 988** descomprimidos (108,80 MiB),
**3 975** entradas, **41/41** distribuciones de ejecución y **ninguna** de las **20** de
desarrollo. El *handler* `app.lambda_handler.handler` respondió **200** a un evento
**HTTP API v2** `GET /health` ejecutado **desde el ZIP extraído** en un proceso Linux con
`-I -S -W error`, sin árbol de fuentes, sin `site-packages`, sin `.env` y sin credenciales;
Argon2, Pillow y el driver binario de PostgreSQL se **ejercitaron**, y **tres controles
negativos** demostraron que el aislamiento es real. `Task/025` y `Task/026` siguen
**Pendientes**, y **D-12** sigue **ABIERTA**.

**Depende de:** `Task/023` ✔ (**Aprobada** el 2026-09-13).
**Repositorios:** `personal-blog-backend` —propiedad funcional— e infra (documentación).
`personal-blog-frontend` **no participa**.
[Ficha](../tasks/TASK-024-lambda-zip-artifact.md) ·
[Reporte](../task-reports/TASK-024-report.md).

### `Task/025-Terraform-Cloud` — **Aprobada** (2026-09-14)

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

**Aprobada el 2026-09-14** mediante `approved: Task/025-Terraform-Cloud`. Todas sus
decisiones pasan de **Propuesta** a **Aceptadas y Vigentes**, y el avance de la etapa pasa
a **3 de 4 — 75 %**. La aprobación **incluye expresamente** las dos excepciones
humanas —**H-025-1** del laboratorio y la temporal de S-09— y **no** convierte en hecho de
AWS real nada de lo observado en el emulador: eso sigue siendo hipótesis hasta la
ETAPA 10 (ADR-006, límite 5).

> **S-09 quedó decidido el 2026-09-14.** El usuario autorizó una excepción **temporal y
> limitada** de **79 identidades** — 70 del emulador, ligadas a su digest exacto, y 9 de
> Terraform 1.16.2 `linux_amd64` —, registrada en el baseline canónico y revalidada con prueba
> positiva y ocho controles negativos. **H-025-6** y **H-025-7** dejan de ser bloqueantes.
>
> **No** se declaran resueltos ni libres de riesgo: el residual sigue enumerado, el del binario
> nativo del emulador ni se inventaría, y cada entrada lleva sus condiciones de reevaluación.
>
> **H-025-1 también quedó decidido el 2026-09-14.** El criterio de aceptación **7** (segundo
> plan `exit 0`) **no se cumple literalmente**: `exit 2` por `aws_ssm_parameter.tags_all`,
> diferencia demostrada del emulador y **sin** `ignore_changes`. El usuario lo **aceptó como
> excepción explícita del laboratorio local**: **11 criterios en PASS literal y 1 en PASS con
> excepción humana**, ningún FAIL.
>
> **No** significa que Terraform sea idempotente en Floci sin excepciones, ni que el criterio 7
> sea un PASS literal, ni que el emulador reproduzca AWS. **AWS real deberá confirmar la
> idempotencia definitiva.**
>
> **La revisión final quedó superada y no hay bloqueos.**

Lo demostrado hasta ahora, ejecutando de verdad:

| Qué | Evidencia |
| --- | --- |
| Un solo grafo | **21 recursos** en `terraform/`, con módulos compartidos por los dos destinos. Sin `terraform/local/` ni `terraform/production/` |
| Herramienta | CLI `= 1.16.2` y provider `= 6.64.0`, constraints **exactas**; `sha256` verificado contra las sumas oficiales, con **firma GPG** válida de HashiCorp |
| Lock | `.terraform.lock.hcl` **versionado** con los hashes de `linux_amd64` **y** `windows_amd64`; `.gitignore` corregido, porque lo ignoraba |
| Ciclo | `init`, `fmt -check -recursive`, `validate`, `plan` (21 altas), `apply`, pruebas funcionales, segundo `plan`, `destroy`, **ausencia verificada por API**, **reconstrucción**, *smoke* y segundo `destroy` |
| **Camino crítico (R-25)** | `GET /health` por **HTTP real** atravesando API Gateway v2 → Lambda → *handler* del ZIP de `Task/024`: **HTTP 200** con `{"status":"ok",…}`. **La combinación que la suite oficial del emulador no cubre funciona** |
| *Fail-closed* | **112 pruebas** de las guardas y **13 controles negativos** de CLI que abortan **sin abrir ningún socket**; el modo `production` se **rechaza** |
| Perímetro | Red de ejecución `internal`, comprobada lanzando un contenedor en ella: **sin salida TCP externa y sin acceso al rango link-local** de metadata |
| Limitaciones registradas | Tres, **sin disimular**: el emulador no aplica la autorización de S3 (la lectura anónima devolvió **200**, no 403); descarta las etiquetas en `PutParameter`, lo que impide converger en `tags_all`; y no aplica políticas IAM |
| Cuentas y recursos | **Cero recursos AWS reales. Cero credenciales reales.** |
| **S-09 del emulador y de Terraform** | **Medido y temporalmente aceptado** por decisión del usuario del 2026-09-14: 79 identidades en el baseline canónico, ligadas al digest y al `sha256` exactos, con condiciones de reevaluación (**H-025-6**, **H-025-7**) |

**Depende de:** `Task/022` **y `Task/024`**. **Repositorio:** `personal-blog-infra`
(**único modificado**; backend y frontend en **solo lectura**).
[Ficha](../tasks/TASK-025-terraform-cloud.md) ·
[Reporte](../task-reports/TASK-025-report.md).

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
      *Evidencia acumulada, **pendiente de aprobación**: `Task/023` recorrió el flujo
      administrativo real a través del adaptador **en proceso**, y `Task/025` obtuvo
      `{"status":"ok","service":"personal-blog-backend","version":"0.1.0"}` —**el mismo
      cuerpo byte a byte**— por dos caminos: `uvicorn` detrás de Traefik en el entorno local,
      y una **Lambda desplegada de verdad** detrás de API Gateway v2 en el laboratorio. La
      casilla **no se marca todavía**: marcar criterios de salida pertenece al cierre
      aprobado ([`WORKFLOW.md`](../project-management/WORKFLOW.md) §8), y `Task/025` no está
      aprobada. Queda además la porción que solo AWS real puede confirmar (`Task/032`).*
- [x] El ZIP se construye de forma reproducible y respeta los límites de tamaño. *Cumplido por `Task/024`, **Aprobada** el 2026-09-13.*
- [x] Los checksums del artefacto se registran. *Cumplido por `Task/024`, **Aprobada** el 2026-09-13.*
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
