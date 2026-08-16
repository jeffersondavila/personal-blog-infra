# ADR-003 — Nube serverless de bajo costo

| Campo | Valor |
| --- | --- |
| **Estado** | Aceptada |
| **Fecha** | 2026-07-26 |
| **Tarea** | `Task/001-Inicializar-Workspace-y-Roadmap` |
| **Reemplaza a** | — |
| **Reemplazada por** | — |
| **Modificado parcialmente por** | [ADR-007](ADR-007-production-postgresql-on-vps.md) — **Aceptada** (2026-08-15), solo la fila «Base de datos» |

> **Nota de vigencia — 2026-08-15 (`Task/005.3`, aprobada).** Este ADR sigue **Aceptado y
> vigente**, incluidas su decisión serverless y su lista de servicios excluidos.
> [ADR-007](ADR-007-production-postgresql-on-vps.md) modifica **una sola fila** de la tabla
> siguiente: la base de datos de producción pasa de **administrada** a **autogestionada en un
> VPS externo**, por el motivo que este mismo ADR ya anticipaba — *es el único componente con
> costo fijo de la arquitectura*. Todo lo demás permanece intacto, y ADR-007 **refuerza** la
> exclusión de NAT Gateway. Detalle:
> [production-postgresql-vps.md](../architecture/production-postgresql-vps.md).

---

## Contexto

El blog es un proyecto personal: tráfico bajo e irregular, un solo operador, sin
requisitos de alta disponibilidad ni acuerdos de nivel de servicio, y con el **costo
como restricción principal de diseño**.

En ese perfil, cualquier servicio con costo fijo mensual se paga íntegro aunque el sitio
reciba pocas visitas. Un NAT Gateway o un balanceador de carga cuestan más al mes que
todo el resto de la arquitectura junta.

## Decisión

Se adopta una arquitectura **serverless y de escalado a cero** donde sea posible:

| Responsabilidad | Servicio | Razón |
| --- | --- | --- |
| Frontend | **Cloudflare Pages** | Plan gratuito generoso para sitios estáticos, CDN global y TLS incluidos. |
| Entrada HTTP | **API Gateway HTTP API** | Pago por petición, sin costo en reposo. Más barato y simple que REST API o que un balanceador. |
| Backend | **AWS Lambda** | Pago por invocación y duración. Sin costo cuando nadie visita el sitio. |
| Archivos e imágenes | **Amazon S3** | Pago por almacenamiento y transferencia reales. Compatible con MinIO local. |
| Base de datos | **PostgreSQL administrado** ⚠️ **modificado — ver nota** | Mismo motor que en local. Proveedor concreto pendiente de `Task/029`, priorizando costo. |
| Configuración | **SSM Parameter Store** | Parámetros estándar sin costo; `SecureString` para valores sensibles. |
| Logs y métricas | **CloudWatch** con retención y uso limitados | Servicio nativo de Lambda. El costo se contiene con retención corta y alarmas mínimas. |
| CI/CD | **GitHub Actions** | Ya se usa para CI; minutos gratuitos suficientes para este volumen. |
| Infraestructura como código | **Terraform** | Reproducibilidad, revisión por `plan` y capacidad de destruir todo si se abandona el proyecto. |

### Servicios explícitamente excluidos

| Servicio | Por qué no |
| --- | --- |
| **Amazon EC2** | Costo fijo por hora esté o no en uso; además obliga a administrar el sistema operativo, parches y escalado. |
| **Amazon ECR** | Innecesario: el despliegue de Lambda se hace por artefacto ZIP (`Task/024`), no por imagen de contenedor. |
| **Amazon ECS Fargate** | Cobra por tarea en ejecución de forma continua; no escala a cero. |
| **Amazon EKS** | Costo fijo del plano de control y complejidad operativa absurda para un blog personal. |
| **Application Load Balancer** | Costo fijo por hora. API Gateway HTTP API cubre la misma necesidad pagando por uso. |
| **NAT Gateway** | Costo fijo por hora más cargo por transferencia. Se evita diseñando la Lambda **fuera de VPC** o accediendo a la base de datos por endpoint público con TLS. |
| **Portainer en producción** | No hay contenedores propios que administrar en una arquitectura serverless. Su uso es exclusivamente local ([ADR-001](ADR-001-local-first.md)). |

## Consecuencias

### Positivas

- Costo cercano a cero cuando el sitio no recibe tráfico.
- Sin servidores que parchear, dimensionar ni vigilar.
- TLS, CDN y escalado gestionados por las plataformas.
- El proyecto puede pausarse sin generar gasto.
- Todo el conjunto es destruible y recreable con Terraform.

### Negativas

- **Arranque en frío.** La primera petición tras un periodo de inactividad es más lenta.
  *Mitigación:* artefacto ligero (`Task/024`) y ajuste de memoria (`Task/032`).
  Aceptable para un blog.
- **Restricciones del modelo Lambda.** Sin estado en memoria entre peticiones, sin
  procesos de larga duración, límite de duración por invocación y de tamaño del
  artefacto.
  *Mitigación:* el backend se diseña sin estado desde `Task/005`.
- **Conexiones a PostgreSQL.** Muchas invocaciones concurrentes pueden agotar el límite
  de conexiones de una instancia administrada pequeña.
  *Mitigación:* pooling o proxy de conexiones, decidido en `Task/029`. Es el riesgo
  técnico principal de esta arquitectura.
- **Dependencia de dos proveedores** (Cloudflare y AWS), con dos consolas, dos
  facturaciones y dos superficies de configuración.
  *Mitigación:* ambos gestionados por Terraform, con presupuestos en los dos.
- **Costo variable.** Un pico de tráfico o un bucle accidental se traducen en gasto.
  *Mitigación:* throttling en API Gateway (`Task/033`), presupuestos y alarmas
  (`Task/027`), y protección permanente en `Task/041`.
- **Adherencia a proveedor.** Migrar fuera de Lambda y API Gateway tendría un costo.
  *Mitigación:* el código sigue siendo una aplicación FastAPI estándar; el adaptador
  Lambda es una capa fina y removible (`Task/023`).

### Neutras

- La base de datos administrada es el **único componente con costo fijo** de la
  arquitectura. Es una excepción consciente: no existe una alternativa relacional
  gestionada que escale a cero y sea confiable para contenido publicado.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
| --- | --- |
| Contenedor en ECS Fargate detrás de un ALB | Combina dos costos fijos (tarea siempre activa + balanceador) para un tráfico que no lo justifica. |
| Instancia EC2 pequeña con todo instalado | Costo fijo, administración del sistema operativo, parches, backups manuales y punto único de fallo. |
| Blog totalmente estático generado en build | Sería el más barato, pero elimina el panel administrativo, que es un requisito explícito del proyecto. |
| Plataforma tipo PaaS todo-en-uno | Simplificaría la operación, pero suele implicar costo fijo por servicio y menor control mediante infraestructura como código. |
| Lambda dentro de VPC con base de datos privada | Más seguro en aislamiento de red, pero exige NAT Gateway para salida a internet, cuyo costo fijo supera al del resto de la arquitectura. Se compensa con TLS obligatorio y reglas de acceso restringidas. |

## Cumplimiento

- Ninguna tarea puede introducir un servicio de la lista de excluidos sin un ADR que
  reemplace a este.
- `Task/027` exige presupuestos y alarmas **antes** de crear el primer recurso.
- `Task/041` establece la revisión periódica de recursos y costos.

## Referencias

- [ADR-001 — Local-first](ADR-001-local-first.md)
- [Correspondencia local → nube](../architecture/local-to-cloud-mapping.md)
- [ETAPA 10 — Despliegue Cloud](../stages/STAGE-10-cloud-deployment.md)
