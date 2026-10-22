# ETAPA 12 — Lanzamiento y Operación

| Campo | Valor |
| --- | --- |
| **Número** | 12 |
| **Estado** | Pendiente |
| **Dependencias** | [ETAPA 11](STAGE-11-deployment-automation.md) |
| **Tareas** | 2 |
| **Aprobadas** | 0 |
| **Avance** | 0 % |
| **Hito que completa** | Blog lanzado, operado y con costo bajo control. |

---

## Objetivo

Validar producción de extremo a extremo y dejar instalada una protección de costos
permanente, para que el blog pueda operarse a largo plazo sin sorpresas.

## Por qué esta etapa existe

Un proyecto personal se abandona cuando su operación es cara o incómoda. Esta etapa
cierra ambos frentes: verificación real y control de gasto sostenido.

## Tareas

### `Task/040-Validacion-Final-Produccion` — *Pendiente*

HTTPS, dominio, API, login administrativo, contenido, logs, SEO, comportamiento
responsive y prueba de rollback.

> **Producción incluye el VPS** (ampliado en `Task/005.5`). Desde
> [ADR-007](../adr/ADR-007-production-postgresql-on-vps.md), la capa de datos de producción
> **no está en AWS**. Una validación final que solo mire AWS y el frontend deja sin
> verificar el componente cuyo fallo deja el blog sin contenido.

`Task/040` es propietaria de la **verificación final** de:

| Ámbito | Qué se verifica |
| --- | --- |
| **Aplicación** | Sitio, API, login, contenido, SEO, responsive, rollback |
| **AWS** | Lambda, API Gateway, S3, SSM, CloudWatch y sus alarmas |
| **Capa de datos** | Conexión `Lambda → PgBouncer`, PostgreSQL respondiendo, pool coherente bajo carga real |
| **VPS** | Disponibilidad del host, espacio en disco, recursos, **Grafana Alloy enviando de verdad** a Grafana Cloud |
| **Observabilidad** | **CloudWatch mínimo** con su retención real · **Grafana Cloud** recibiendo y alertando · integración **D-20** si se implementó · **ninguna alerta muda** |
| **TLS** | Certificado **válido y vigente**, validado **desde la Lambda real**, con su alerta de caducidad activa |
| **Continuidad** | **Backup reciente y verificado**, **restore vigente** —no uno de hace meses—, runbooks y procedimiento de recuperación |

> **Verificar no es implementar.** `Task/040` **no construye** ninguno de esos componentes:
> comprueba que funcionan **antes** de considerar el blog lanzado. Si algo no está, la
> tarea propietaria lo corrige.

> **Enmienda de `Task/028.2`, aprobada el 2026-09-27.** Con
> [ADR-010](../adr/ADR-010-production-postgresql-on-rds.md), la capa de datos vuelve a
> estar **en AWS**, pero sigue siendo el componente cuyo fallo deja el blog sin contenido,
> y **no se valida menos**. Las filas **Capa de datos**, **VPS**, **Observabilidad**,
> **TLS** y **Continuidad** de la tabla anterior quedan sustituidas por:
>
> | Ámbito | Qué se verifica |
> | --- | --- |
> | **Capa de datos** | Conexión `Lambda → RDS` con TLS verificado desde la Lambda real; pool y concurrencia coherentes **bajo carga real**; saturación, reconexión y recuperación |
> | **Red y seguridad** | RDS **no** alcanzable desde Internet; casos negativos de security groups, IAM y TLS; roles separados y rol de validación de `Task/028` sin políticas |
> | **RDS** | Disponibilidad, almacenamiento, IOPS y conexiones con alarmas **disparadas en prueba segura**; *deletion protection* activa |
> | **Observabilidad** | **CloudWatch mínimo** con su retención real · **Grafana Cloud** recibiendo por **D-20** y alertando · **ninguna alerta muda** · muestreo sin secretos ni PII |
> | **TLS** | Certificados públicos vigentes y confianza en la **CA de RDS** con su rotación planificada |
> | **Continuidad** | **Backup reciente restaurado** en destino aislado con el esquema real, **RPO/RTO medidos**, procedimiento de DR y rollback de versión y de migración ejecutados |

> **Añadido el 2026-10-21 al cerrar `Task/031`, por decisión del usuario: alertamiento efectivo de RDS (D-11).**
> Por esa decisión, `Task/040` es la **propietaria** de implementarlo y probarlo: es una excepción explícita a «verificar no es implementar». **D-11 sigue abierta** hasta que el alertamiento efectivo y la calibración de `memoria` (bloque siguiente) estén implementados y verificados.
>
> - **Situación de partida** ([reporte de Task/031 §51.16](../task-reports/TASK-031-report.md#5116-matriz-final-de-aceptación-excepciones-y-evidencia-del-cierre-2026-10-21)):
>   - las 8 alarmas de RDS de H-031-8 existen **sin acciones** (`actions_enabled = false`), porque no hay destinatarios aprobados;
>   - el fallo de *backup* no tiene alarma y se supervisa a mano (B3, opción A);
>   - hoy **ninguna alarma avisa a nadie**.
> - **Alcance:**
>   1. decidir y aprobar los destinatarios o canales de notificación, por ejemplo SNS con correo o reglas de alerta de Grafana Cloud vía D-20, con su costo, su privacidad y sin secretos ni datos personales en los mensajes;
>   2. implementarlos con Terraform y conectar las alarmas de RDS a esos canales;
>   3. demostrar en una prueba segura que las alertas **se reciben** de verdad en cada canal aprobado.
> - **Evidencia requerida:**
>   - el plan revisado, la guarda y la convergencia 0/0/0 del cambio;
>   - la configuración de cada alarma leída por API, con sus acciones apuntando a los canales aprobados;
>   - por cada canal, la recepción efectiva de una alerta de prueba, con su marca de tiempo, y el retorno a `OK`;
>   - que ninguna notificación contiene secretos ni datos personales.
> - **Criterios de aceptación:**
>   1. los canales están aprobados y desplegados con Terraform; nada a mano en la consola;
>   2. las alarmas de RDS tienen acciones hacia esos canales;
>   3. una prueba segura, sin provocar un incidente real en la productiva, demuestra la recepción en cada canal y la vuelta a `OK`;
>   4. D-11 registra los canales y la prueba, y solo se cierra cuando se cumplen 1 a 3 y la calibración de `memoria`.
> - **Hasta entonces**, las alarmas no se modifican en AWS.

> **Añadido el 2026-10-21 al cerrar `Task/031`, por decisión del usuario: calibración de la alarma `memoria` de RDS (D-11).**
> Por esa decisión, `Task/040` es la **propietaria** de esta corrección: es una excepción explícita a «verificar no es implementar». D-11 sigue **abierta** hasta resolverla.
>
> - **Problema observado** ([reporte de Task/031 §47.8](../task-reports/TASK-031-report.md#478-hallazgo-de-calibración-alarma-memoria-en-alarm)): `blog-prod-rds-memoria` está en `ALARM` desde su primera evaluación, el 2026-10-15. Mide `FreeableMemory`, en media, sobre 60 s × 15 puntos, con umbral `< 256 MiB` (el 25 % de 1 GiB, criterio de AWS), y una `db.t4g.micro` en reposo ronda los 148 MiB libres. La alarma no tiene acciones y, tal como está, no discrimina.
> - **Condiciones a evaluar:**
>   - `FreeableMemory`, y `SwapUsage`, en reposo, con el tráfico real de la Lambda de `Task/032` y durante las pruebas de carga de esta tarea;
>   - su relación con `DatabaseConnections`, `max_connections = 112` y el pool de la aplicación;
>   - si el problema es el umbral o la clase de instancia. Cambiar de clase es una decisión aparte, con su costo (D-13).
> - **Evidencia requerida para ajustar el umbral:**
>   - las series de CloudWatch del periodo medido: mínimo, media y percentiles;
>   - los valores en reposo y bajo carga;
>   - el umbral propuesto, con su margen razonado;
>   - una prueba segura de que la alarma pasa a `ALARM` cuando debe y vuelve a `OK`.
> - **Criterios de aceptación:**
>   1. la alarma está en `OK` en reposo y con la carga nominal;
>   2. pasa a `ALARM` en una prueba segura de presión de memoria, o el umbral se justifica con las series medidas, y vuelve a `OK`;
>   3. el cambio se hace con Terraform, en el módulo `alarmas_rds`, con plan revisado, guarda y convergencia 0/0/0; nunca a mano en la consola;
>   4. D-11 registra la decisión y solo se cierra cuando se cumplen los criterios 1 a 3.
> - **Hasta entonces**, la alarma no se modifica en AWS.

**Depende de:** `Task/039`. **Repositorios:** los tres.

### `Task/041-Proteccion-de-Costos` — *Pendiente*

Presupuestos, alarmas, retención de logs, límites de servicio y revisión periódica de
recursos activos.

> **El costo no es solo AWS** (ampliado en `Task/005.5`, y en `Task/006.2` con la
> observabilidad). Debe contemplar **todos** los recursos productivos que cuestan dinero:
> **AWS**, **Cloudflare si aplica**, **dominio**, **VPS**, **IPv4 si tiene costo**,
> **almacenamiento de backups**, **snapshots**, **transferencia** y **Grafana Cloud**
> (**D-19**). Un control de costos que ignore el VPS o la observabilidad no protege la
> factura real.
>
> **Y debe confirmar que los tiers gratuitos siguen siendo aplicables** en ese momento
> (**R-38**). Las condiciones de un plan gratuito **no son una garantía eterna**: «Grafana
> Cloud Free» es una **preferencia presupuestaria**, no una dependencia arquitectónica.
>
> **Precios vigentes en el momento de ejecutarse**, nunca cifras heredadas de este
> documento ni de `Task/029`.
>
> *(Enmienda de `Task/028.2`: sin VPS ni IPv4 propia. Se incluyen **RDS**
> —instancia, almacenamiento, IOPS, backup excedente, snapshots y restores temporales—,
> ***endpoints*** por AZ y hora, **KMS** y transferencia. Se separan **costo bruto**,
> **crédito consumido**, **desembolso**, **vencimiento** de los créditos y **escenario
> poscrédito**. **D-13** no se eleva automáticamente, ni se cambia de plan sin decisión
> explícita.)*

**Depende de:** `Task/040`. **Repositorio:** `personal-blog-infra`.

## Criterios de salida de la etapa

- [ ] El sitio carga por HTTPS en el dominio principal y en `www`.
- [ ] El API responde en su subdominio con CORS correcto.
- [ ] El login administrativo funciona en producción.
- [ ] Todas las secciones del blog muestran contenido real.
- [ ] Los logs llegan a CloudWatch y son consultables, con la retención real verificada.
- [ ] **Grafana Cloud recibe la telemetría del VPS** y sus alertas —disco, caducidad de
      certificado, fallo de backup— **se dispararon en una prueba**, no solo están
      configuradas.
- [ ] La telemetría enviada **no contiene secretos ni datos personales innecesarios**
      (**O-09**), comprobado por muestreo.
- [ ] Los metadatos SEO se validan con herramientas externas.
- [ ] El sitio se comporta correctamente en móvil, tableta y escritorio.
- [ ] El rollback se ejecutó realmente y funcionó.
- [ ] La **conexión `Lambda → PgBouncer → PostgreSQL`** funciona con **TLS validado** y el
      certificado está **vigente**, con alerta de caducidad activa.
- [ ] El **VPS** está disponible, con espacio en disco y recursos suficientes, y su
      **observabilidad opera de verdad** —no solo está configurada—.
- [ ] Existe un **backup reciente y verificado**, y un **restore demostrado vigente**.
- [ ] Los **runbooks** de recuperación de la capa de datos existen y son ejecutables.
- [ ] Presupuestos y alarmas activos y probados.
- [ ] Retención de logs limitada y verificada.
- [ ] Existe una lista revisable de **todos** los recursos productivos que cuestan dinero y
      su costo: AWS, **VPS**, dominio, **backups**, transferencia, Cloudflare si aplica y
      **Grafana Cloud**.
- [ ] **Confirmado con precios y límites vigentes en ese momento** que los tiers gratuitos
      utilizados siguen siendo aplicables (**D-19**, **R-38**).
- [ ] Está definida la periodicidad de la revisión de costos.

*(Enmienda de `Task/028.2`: los criterios que nombran **VPS**, **PgBouncer** o
**Alloy** se leen sobre RDS según la tabla de enmienda de `Task/040`. Se añaden desde la aprobación
del 2026-09-27:)*

- [ ] RDS no es accesible públicamente; casos negativos de red, security groups, IAM y TLS
      comprobados.
- [ ] Carga y latencia `Lambda ↔ RDS`, saturación de conexiones, reconexión y *cold starts*
      medidos contra los límites de **D-12**.
- [ ] **Backup reciente restaurado** en destino aislado, con esquema y contenido íntegros y
      **RPO/RTO medidos**; limpieza autorizada sin tocar producción.
- [ ] Procedimiento de DR y rollback de versión y de migración verificados.
- [ ] Alarmas de RDS —almacenamiento, conexiones, backup— **disparadas en prueba segura**.
- [ ] *(Añadido el 2026-10-21, D-11.)* **Alertamiento efectivo de RDS**: canales de notificación aprobados,
      alarmas conectadas a ellos y **recepción demostrada** en una prueba segura.
- [ ] *(Añadido el 2026-10-21, D-11.)* Alarma `memoria` **calibrada** con historial real: en `OK` en reposo y
      con la carga nominal.
- [ ] Costo bruto real contrastado con la estimación de `Task/029`; crédito consumido,
      desembolso, vencimiento y escenario poscrédito separados; **D-13** sin elevar
      automáticamente.

## Fuera del alcance de la etapa

- Nuevas funcionalidades del blog (roadmap posterior).
- Migración a arquitecturas con costo fijo (EC2, ECS, EKS), excluidas por
  [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md).
- *(`Task/028.2`)* Introducir NAT Gateway, RDS Proxy, Multi-AZ, Secrets Manager o
  funciones avanzadas de monitoreo **sin** la decisión de su tarea propietaria.

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Crecimiento silencioso del costo con el tiempo. | Revisión periódica agendada y alarmas por umbral. |
| **Un tier gratuito de terceros cambia de límites o de precio** (**R-38**). | Declarado como preferencia presupuestaria, no como dependencia; verificación de precios reales en cada revisión; la arquitectura admite pagar, reducir volumen o cambiar de destino. |
| Recursos huérfanos que nadie recuerda haber creado. | Inventario de recursos mantenido en Terraform y revisado. |
| Rollback nunca probado en producción real. | Se ejecuta como criterio obligatorio en `Task/040`. |
| Abandono del mantenimiento tras el lanzamiento. | Runbooks y automatización que reducen el esfuerzo de operación. |
| *(`Task/028.2`)* **Los créditos AWS se agotan o caducan** y el costo bruto de RDS pasa a pagarse (**R-02**). | Escenario poscrédito en `Task/029` y `Task/041`; decisión explícita antes de que ocurra, no después. |
| *(`Task/028.2`)* **Confundir backup administrado con recuperación** (**R-31**). | Solo cuenta un restore reciente demostrado; Multi-AZ **no** sustituye al backup ni al PITR. |

## Cierre del roadmap

Esta es la última etapa del roadmap inicial. Las funcionalidades posteriores se
registrarán como nuevas etapas en [ROADMAP.md](../project-management/ROADMAP.md).
