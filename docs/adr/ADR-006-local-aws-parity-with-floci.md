# ADR-006 — Paridad AWS local con Floci

| Campo | Valor |
| --- | --- |
| **Estado** | **Aceptada** ✔ |
| **Fecha** | 2026-08-15 |
| **Fecha de aceptación** | 2026-08-15 |
| **Aceptada por** | jeffersondavila (usuario) |
| **Expresión de aprobación** | `approved: Task/005.2-Documentar-Estrategia-Floci-IaC-Local` |
| **Tarea** | `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` (mantenimiento; **no cuenta** en las 41 tareas) |
| **Reemplaza a** | — |
| **Reemplazada por** | — |
| **Documento canónico** | [aws-local-parity.md](../architecture/aws-local-parity.md) |

> **Aceptada** el 2026-08-15, al aprobar el usuario `Task/005.2` con la expresión exacta
> requerida por [WORKFLOW.md](../project-management/WORKFLOW.md). Sus reglas son **vigentes
> y de cumplimiento obligatorio** desde esta fecha.

---

## Contexto

[ADR-001](ADR-001-local-first.md) fijó la estrategia **local-first**: nada se despliega
antes de estar validado en local. [ADR-003](ADR-003-serverless-low-cost-cloud.md) fijó la
arquitectura cloud objetivo —API Gateway HTTP API, Lambda, S3, SSM, CloudWatch,
PostgreSQL administrado, Terraform— con el **costo como restricción principal de diseño**.

Existe un hueco entre ambas decisiones.

Hoy, la **ETAPA 08** compromete a `Task/025-Terraform-Cloud` únicamente a
`terraform fmt -check` y `terraform validate`. Eso comprueba **sintaxis y coherencia de
tipos**, no comportamiento: no crea nada, no ejercita permisos, no demuestra que
`terraform apply` funcione, ni que `terraform destroy` limpie de verdad, ni que el
artefacto Lambda se ejecute. Ese es precisamente el riesgo ya registrado en la propia
ficha de la etapa: *«Terraform validado en seco que falla en el primer `apply` real»*.

Consecuencias de dejarlo así:

1. **El primer `apply` real ocurriría en producción**, con cuenta AWS creada y costo
   corriendo, sobre una IaC que nunca se ejecutó.
2. **El aprendizaje ocurriría sobre recursos facturables.** El proyecto es también un
   ejercicio de formación en AWS y Terraform; equivocarse es parte del método, y equivocarse
   en AWS real se paga.
3. **El ciclo `destroy` / `apply` no se habría ensayado nunca**, siendo la garantía de que
   la infraestructura es reproducible y de que el proyecto puede pausarse sin gasto —una
   consecuencia positiva prometida explícitamente por ADR-003.
4. **El *drift* no se habría observado nunca**, siendo el concepto central de trabajar con
   estado en Terraform.

Existen emuladores locales de AWS que permiten ejecutar el ciclo completo sin cuenta y sin
costo. La pregunta es si el proyecto adopta uno y con qué límites.

## Decisión

> **Adoptar Floci como laboratorio AWS local para validar Terraform y las integraciones
> AWS antes del despliegue real, manteniendo AWS real como la autoridad final.**

Con estos límites, que forman parte de la decisión y no son comentarios:

| # | Límite |
| --- | --- |
| 1 | **Terraform es la fuente de verdad de la infraestructura cloud.** Floci y AWS son dos **destinos** de la misma definición. |
| 2 | **Una sola definición de IaC.** No se crean módulos paralelos «locales» ni recursos Terraform ficticios específicos de Floci. Las diferencias se confinan a provider, endpoints, credenciales, región, backend, nombres, capacidad y a las incompatibilidades registradas. |
| 3 | **La aplicación nunca depende de Floci.** El backend y las herramientas usan AWS SDK/boto3, AWS CLI y el provider oficial `hashicorp/aws`. |
| 4 | **Floci no reemplaza el entorno local actual.** Docker Compose, PostgreSQL, MinIO, Traefik y Portainer siguen siendo el entorno de desarrollo de aplicación. Son dos modos con propósitos distintos. |
| 5 | **AWS real es la autoridad final.** Un comportamiento observado en Floci es una hipótesis hasta que la ETAPA 10 lo confirma. |
| 6 | **Toda diferencia se registra en la matriz de paridad.** Nunca se declara «paridad completa». |
| 7 | **Nunca se usan credenciales AWS reales contra Floci**, ni secretos reales en su SSM emulado. |
| 8 | **Se fija una versión concreta de Floci.** `latest` y `nightly` no son versiones reproducibles. |
| 9 | **Floci se trata como infraestructura local privilegiada**, por su acceso al socket de Docker. |
| 10 | **Cero recursos AWS reales** durante toda la ETAPA 08. |

La estrategia completa —arquitectura, matriz de paridad, seguridad, guardas *fail-closed*,
ciclo de aprendizaje y criterios de éxito— vive en el documento canónico
[aws-local-parity.md](../architecture/aws-local-parity.md). Este ADR registra la
**decisión**; el documento registra **cómo se aplica**.

### Qué NO decide este ADR

- **No** resuelve **D-01** (proveedor de PostgreSQL administrado, `Task/029`). Que Floci
  soporte RDS es irrelevante para esa elección.
- **No** resuelve **D-06** (backend de estado de Terraform, `Task/025`).
- **No** modifica [ADR-003](ADR-003-serverless-low-cost-cloud.md): la arquitectura objetivo
  y los servicios excluidos siguen intactos. Floci no introduce ningún servicio nuevo en la
  arquitectura de producción.
- **No** añade tareas al roadmap: siguen siendo **41**, sin renumerar.

## Alternativas consideradas

| # | Alternativa | Evaluación |
| --- | --- | --- |
| **A** | **No usar ningún emulador AWS.** Quedarse en `terraform fmt` + `validate` y aprender directamente contra AWS real. | Es el estado actual. Ventaja: cero herramientas nuevas y cero riesgo de aprender un comportamiento falso. Desventaja: el primer `apply`, el primer error de IAM y el primer `destroy` ocurren con la factura abierta, sobre una IaC nunca ejecutada. **Descartada** como opción única, pero conserva su papel: sigue siendo el modo de operación para todo lo que resulte `AWS-only`. |
| **B** | **Arquitectura local completamente distinta**: Docker, MinIO y PostgreSQL, sin intentar parecerse a AWS. | Es el **Modo A**, que ya existe y **se conserva**. Como estrategia única no sirve para este objetivo: no ejercita Terraform, ni IAM, ni el empaquetado Lambda, ni el ciclo de estado. **No se descarta —se mantiene—**, pero no cubre la necesidad. |
| **C** | **Floci.** | **Elegida.** Razones en el apartado siguiente. |
| **D** | **LocalStack u otro emulador AWS.** | **Alternativa válida y técnicamente razonable.** No se elige ahora. Si Floci se abandona (§ criterio de revisión), esta es la primera opción a evaluar, y el coste de cambiar es bajo precisamente por la regla de portabilidad: la IaC no depende del emulador. |

### Por qué Floci, sobre necesidades del proyecto

La elección **no** se basa en popularidad ni en número de estrellas, sino en necesidades
concretas contrastadas con documentación oficial el **2026-08-15**:

| Necesidad del proyecto | Evidencia oficial observada |
| --- | --- |
| Terraform con el **provider oficial de AWS**, no con un provider propietario | El repositorio incluye una suite de compatibilidad versionada que usa `hashicorp/aws ~> 6.0` con bloque `endpoints`, más suites para OpenTofu y CDK. |
| Los servicios de [ADR-003](ADR-003-serverless-low-cost-cloud.md): API Gateway v2, Lambda, S3, SSM, IAM, CloudWatch | Los seis tienen documentación de servicio propia y soporte declarado. |
| Lambda con fidelidad razonable | Ejecución en **contenedores Docker reales** basados en las imágenes oficiales de runtime de AWS, con empaquetado ZIP —que es el que exige ADR-003 al excluir ECR. |
| Ciclo `apply` / `destroy` / reconstrucción sin costo | Ejecución local completa, sin cuenta AWS. |
| Coste cero, coherente con la restricción principal del proyecto | Licencia **MIT**, sin plan de pago ni funcionalidades bajo licencia para el uso previsto. |
| Interfaces estándar, para no acoplarse | Se opera por `AWS_ENDPOINT_URL` / `--endpoint-url` con AWS CLI, boto3 y los SDK oficiales. Abandonarlo no obliga a reescribir la IaC. |
| Reversibilidad | Ver *Criterio de revisión y abandono*. |

## Consecuencias

### Positivas

- La IaC se **ejecuta** antes de existir la cuenta AWS: `apply`, inspección, *drift*,
  `destroy` y reconstrucción.
- El aprendizaje de AWS y Terraform ocurre **sin costo y sin miedo a romper nada**.
- El artefacto Lambda y el adaptador FastAPI se prueban **ejecutándose**, no solo midiendo
  el ZIP.
- Refuerza [ADR-001](ADR-001-local-first.md): amplía el «local-first» de la aplicación a la
  infraestructura.
- Protege la restricción de costo de [ADR-003](ADR-003-serverless-low-cost-cloud.md): los
  errores caros se descubren gratis.
- Abre la puerta a CI de infraestructura sin credenciales cloud (`Task/039`).
- La regla de portabilidad deja la IaC **independiente del emulador**: abandonar Floci no
  obliga a reescribir nada.

### Negativas

- **Una herramienta más que mantener**, con versión fijada y revalidación en cada
  actualización (**R-21**).
- **Falsa sensación de paridad** si se confunde «funciona en el laboratorio» con «funcionará
  en AWS» (**R-20**). Es el riesgo más peligroso de esta decisión.
- **Privilegio de nivel host**: Floci necesita el socket de Docker, sumándose a Portainer
  (**R-22**, agrava **R-09**).
- **Riesgo de tocar AWS real por accidente** si falta un endpoint (**R-24**). Exige guardas
  *fail-closed* antes del primer `apply`.
- **Trabajo adicional en `Task/025` y `Task/026`**, que dejan de ser tareas de validación en
  seco.
- **Tentación de bifurcar la IaC** para acomodar limitaciones locales (**R-26**).

### Límites de fidelidad conocidos

Documentación oficial, **2026-08-15**. No son sospechas: están declarados por el propio
proyecto.

| Servicio | Límite declarado | Consecuencia |
| --- | --- | --- |
| **IAM** | La aplicación de políticas está **desactivada por omisión**; con el modo opcional activo persisten exenciones. | El laboratorio valida que un rol **se crea**, no que **autoriza**. Mínimo privilegio es **AWS-only** (**R-28**). |
| **SSM** | `SecureString` conserva el tipo pero **no se cifra en reposo**. | Ningún secreto real entra en el SSM emulado. |
| **CloudWatch Logs** | Filtros de suscripción almacenados pero **no entregados**; Logs Insights **degrada en silencio** ante sintaxis no soportada. | Una consulta puede parecer correcta y estar mintiendo. |
| **CloudWatch alarmas** | Estado fijado manualmente vía `SetAlarmState`; sin motor de evaluación documentado. | Se valida la definición, no el disparo. |
| **Lambda** | Sin *layers*, sin concurrencia aprovisionada, sin *response streaming*. | Coincide con lo que el proyecto necesita, pero el **arranque en frío local no es comparable**: no sirve para dimensionar. |
| **API Gateway** | Sin dominios personalizados, VPC Links ni certificados de cliente. | `Task/035` (DNS) no tiene ensayo local. |
| **S3** | Sin replicación, *access logging*, *inventory* ni configuraciones de métricas; `RestoreObject` es *stub*. | Ninguna afecta al alcance del MVP. |
| **Terraform** | La suite oficial de compatibilidad **no cubre** `aws_lambda_function`, `aws_apigatewayv2_*` ni `aws_cloudwatch_log_group`. | **Es exactamente el camino crítico del proyecto** (**R-25**): demostrarlo es el objetivo de `Task/025`. |

## Riesgos

**R-19** a **R-28**, definidos en [aws-local-parity.md](../architecture/aws-local-parity.md)
§14 y registrados en [STATUS.md](../project-management/STATUS.md). Los de impacto alto:
**R-20** (falsa paridad), **R-22** (privilegio Docker), **R-23** (endpoint expuesto),
**R-24** (AWS real accidental), **R-25** (camino crítico no cubierto upstream) y **R-28**
(IAM sin *enforcement*).

## Criterio de revisión y abandono

Esta decisión se revisa o se revierte si:

1. `Task/025` no logra desplegar localmente **API Gateway v2 + Lambda + S3 + SSM + Logs**
   con Terraform y fidelidad suficiente → se reduce el alcance del laboratorio y el resto
   pasa a `AWS-only`.
2. El costo de mantenimiento supera al beneficio → se abandona Floci **sin tocar la IaC**.
3. Aparece una diferencia que hace **engañosa** la validación local → se degrada el estado
   en la matriz de paridad.
4. Floci se archiva, cambia de licencia o deja de mantenerse → se evalúa la alternativa **D**
   o se abandona el Modo B.

Revertir esta decisión **no exige un ADR que la reemplace si la IaC no cambia**: basta con
dejar de usar el destino local. Solo haría falta un ADR nuevo si se decidiera acoplar la
infraestructura a un emulador concreto, que es justo lo que la decisión prohíbe.

## Cumplimiento

- Ninguna tarea puede introducir un recurso Terraform específico de Floci ni un módulo
  paralelo local/cloud.
- Ninguna tarea puede acoplar el código de aplicación a una API propia de Floci.
- Ninguna tarea puede usar credenciales AWS reales contra Floci.
- Ninguna tarea puede declarar «paridad completa» en la matriz.
- `Task/025` no puede ejecutar un `apply` local sin las guardas *fail-closed*.
- La ETAPA 10 sigue siendo obligatoria: el laboratorio no la sustituye.

## Referencias

- [aws-local-parity.md](../architecture/aws-local-parity.md) — documento canónico
- [ADR-001 — Local-first](ADR-001-local-first.md)
- [ADR-003 — Nube serverless de bajo costo](ADR-003-serverless-low-cost-cloud.md)
- [Decisiones diferidas](../architecture/open-decisions.md) — **D-01**, **D-06**, **D-14**
- [Límites de seguridad](../architecture/security-boundaries.md)
- [ETAPA 08 — Preparación Cloud + AWS Local Parity](../stages/STAGE-08-cloud-ready.md)
- Fuentes oficiales de Floci consultadas el 2026-08-15: `https://github.com/floci-io/floci`
  y `https://floci.io/floci/`
