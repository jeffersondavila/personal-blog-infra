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
| **VPS** | Disponibilidad del host, espacio en disco, recursos, observabilidad operando de verdad |
| **TLS** | Certificado **válido y vigente**, validado **desde la Lambda real**, con su alerta de caducidad activa |
| **Continuidad** | **Backup reciente y verificado**, **restore vigente** —no uno de hace meses—, runbooks y procedimiento de recuperación |

> **Verificar no es implementar.** `Task/040` **no construye** ninguno de esos componentes:
> comprueba que funcionan **antes** de considerar el blog lanzado. Si algo no está, la
> tarea propietaria lo corrige.

**Depende de:** `Task/039`. **Repositorios:** los tres.

### `Task/041-Proteccion-de-Costos` — *Pendiente*

Presupuestos, alarmas, retención de logs, límites de servicio y revisión periódica de
recursos activos.

> **El costo no es solo AWS** (ampliado en `Task/005.5`). Debe contemplar **todos** los
> recursos productivos que cuestan dinero: **AWS**, **Cloudflare si aplica**, **dominio**,
> **VPS**, **IPv4 si tiene costo**, **almacenamiento de backups**, **snapshots** y
> **transferencia**. Un control de costos que ignore el VPS no protege la factura real.
>
> **Precios vigentes en el momento de ejecutarse**, nunca cifras heredadas de este
> documento ni de `Task/029`.

**Depende de:** `Task/040`. **Repositorio:** `personal-blog-infra`.

## Criterios de salida de la etapa

- [ ] El sitio carga por HTTPS en el dominio principal y en `www`.
- [ ] El API responde en su subdominio con CORS correcto.
- [ ] El login administrativo funciona en producción.
- [ ] Todas las secciones del blog muestran contenido real.
- [ ] Los logs llegan a CloudWatch y son consultables.
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
      su costo: AWS, **VPS**, dominio, **backups**, transferencia y Cloudflare si aplica.
- [ ] Está definida la periodicidad de la revisión de costos.

## Fuera del alcance de la etapa

- Nuevas funcionalidades del blog (roadmap posterior).
- Migración a arquitecturas con costo fijo (EC2, ECS, EKS), excluidas por
  [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Crecimiento silencioso del costo con el tiempo. | Revisión periódica agendada y alarmas por umbral. |
| Recursos huérfanos que nadie recuerda haber creado. | Inventario de recursos mantenido en Terraform y revisado. |
| Rollback nunca probado en producción real. | Se ejecuta como criterio obligatorio en `Task/040`. |
| Abandono del mantenimiento tras el lanzamiento. | Runbooks y automatización que reducen el esfuerzo de operación. |

## Cierre del roadmap

Esta es la última etapa del roadmap inicial. Las funcionalidades posteriores se
registrarán como nuevas etapas en [ROADMAP.md](../project-management/ROADMAP.md).
