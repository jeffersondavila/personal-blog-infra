# Correspondencia local → nube

**Última actualización:** 2026-08-15 (`Task/005.2` — columna *AWS Local Parity Lab*)

> Consistente con la arquitectura definida en `Task/002`. Ver
> [software-architecture.md](software-architecture.md) para la organización interna del
> código y [security-boundaries.md](security-boundaries.md) para las comunicaciones
> permitidas entre componentes.

Cada responsabilidad del sistema tiene una implementación local y una implementación
prevista en la nube. El objetivo es que **el código de aplicación no cambie** al pasar
de una a otra: lo que cambia es la configuración y el adaptador.

Desde `Task/005.2` (**aprobada** el 2026-08-15) existe además un **tercer entorno**, el
**AWS Local Parity Lab**: un laboratorio local de infraestructura que permite ejecutar la
misma definición de Terraform contra un emulador AWS, sin cuenta y sin costo. **No
sustituye al entorno local de desarrollo** y **no es autoridad sobre el comportamiento de
AWS**. Estrategia completa y límites de fidelidad:
[aws-local-parity.md](aws-local-parity.md) — **Vigente** ·
[ADR-006](../adr/ADR-006-local-aws-parity-with-floci.md) — **Aceptada**.

---

## Tabla de correspondencia

| Responsabilidad | Local (desarrollo) | AWS Local Parity Lab | Nube inicial |
| --- | --- | --- | --- |
| Frontend | React + Vite | No aplica | Cloudflare Pages |
| Backend | FastAPI local/Docker | Lambda emulada ejecutando el mismo FastAPI | AWS Lambda |
| Entrada HTTP | Reverse proxy | API Gateway v2 emulado | API Gateway HTTP API |
| Base de datos | PostgreSQL Docker | Fuera del alcance inicial (**D-01**) | PostgreSQL administrado |
| Archivos | MinIO | S3 emulado | Amazon S3 |
| Administración Docker | Portainer | No aplica | No se despliega |
| Configuración | `.env` | SSM emulado (**sin cifrado real**) | SSM Parameter Store |
| Logs | Docker y Portainer | CloudWatch Logs emulado | CloudWatch |
| Permisos | No aplica | IAM emulado — **crea, no autoriza** | IAM |
| Ejecución | Docker Compose | Emulador AWS local | Serverless |
| Infraestructura | Docker Compose | **Terraform** (misma definición) | **Terraform** (misma definición) |
| Integración continua | GitHub Actions | GitHub Actions + emulador efímero (`Task/039`) | GitHub Actions |
| Despliegue | No aplica todavía | `apply`/`destroy` local (`Task/025`) | GitHub Actions + Terraform |

> La estrategia del laboratorio está **aprobada**, pero **nada de esa columna está probado
> todavía**: se implementa en `Task/025`. El grado real de paridad de cada fila se registra
> en la [matriz de paridad](aws-local-parity.md) §7, que hoy está entera en `No evaluada`.

---

## Notas por responsabilidad

### Frontend
Mismo build de Vite en ambos entornos. En local lo sirve el reverse proxy; en la nube,
Cloudflare Pages sirve los estáticos. La URL del API se inyecta como variable de entorno
en tiempo de build.

### Backend
El mismo código FastAPI se ejecuta como proceso ASGI en local y bajo un adaptador Lambda
en la nube (`Task/023`). Restricción de diseño: sin estado en memoria entre peticiones y
sin trabajos en segundo plano de larga duración.

### Entrada HTTP
El reverse proxy local reproduce el enrutado que hará API Gateway (rutas de sitio y de
API, CORS). API Gateway añade throttling y TLS gestionado.

### Base de datos
El mismo motor PostgreSQL en ambos lados. Diferencia crítica: desde Lambda las
conexiones son efímeras y numerosas, lo que exige pooling o un proxy de conexiones.
Se decide en `Task/029`.

### Archivos
MinIO expone la API de S3, así que el mismo cliente sirve para ambos. Todo acceso pasa
por la interfaz `ObjectStorage` (`Task/010`), con una implementación por entorno.
En ambos casos el acceso a archivos privados usa URLs prefirmadas.

### Administración Docker
Portainer CE es exclusivamente local: sirve para inspeccionar contenedores, logs,
healthchecks, volúmenes y redes durante el desarrollo y la validación.
**No se despliega en la nube** — allí no hay contenedores propios que administrar.

### Configuración
En local, `.env` (ignorado por Git) más un `.env.example` con valores ficticios.
En la nube, SSM Parameter Store; los valores sensibles como `SecureString`. El código
lee siempre variables de entorno: quién las provee es indiferente.

### Logs
En local, salida estándar capturada por Docker y visible en Portainer. En la nube,
CloudWatch con retención explícita y limitada para contener el costo. En ambos casos el
formato es JSON con correlation ID (`Task/017`).

### Ejecución
Docker Compose local frente a ejecución serverless en la nube. Implicación: no hay
procesos residentes en producción; toda tarea periódica debe modelarse como invocación.

### Infraestructura
Docker Compose describe el entorno local de aplicación; Terraform describe el cloud. No se
comparte definición entre ambos, pero sí la nomenclatura de recursos y variables.

**Matiz añadido en `Task/005.2`:** entre esos dos mundos se propone el *AWS Local Parity
Lab*, donde **Terraform sí es la misma definición** que la de producción, apuntada a un
destino local. Regla de portabilidad: **una sola definición, un solo grafo de recursos**;
las diferencias se confinan a provider, endpoints, credenciales, región, backend, nombres,
dominios y capacidad ([aws-local-parity.md](aws-local-parity.md) §4).

### Integración continua
GitHub Actions en ambos casos, con los mismos workflows de calidad. El despliegue se
añade en la Etapa 11, usando OIDC para acceder a AWS sin credenciales permanentes.

---

## Diferencias que exigen atención explícita

| # | Diferencia | Dónde se aborda |
| --- | --- | --- |
| 1 | Lambda no mantiene estado ni conexiones entre invocaciones. | `Task/023`, `Task/029` |
| 2 | Arranque en frío afecta la latencia de la primera petición. | `Task/024`, `Task/032` |
| 3 | Límite de tamaño del artefacto de Lambda. | `Task/024` |
| 4 | En local no hay TLS real; en la nube todo es HTTPS. | `Task/035`, `Task/040` |
| 5 | S3 cobra por almacenamiento y transferencia; MinIO no. | `Task/030`, `Task/041` |
| 6 | CloudWatch cobra por ingesta y retención de logs. | `Task/031`, `Task/041` |
| 7 | El límite de conexiones de PostgreSQL administrado suele ser bajo. | `Task/029` |
| 8 | No hay equivalente de Portainer en producción. | Diagnóstico por CloudWatch (`Task/031`) |
| 9 | **El laboratorio local no aplica políticas IAM**: un rol puede validarse en local y ser incorrecto en AWS. | `Task/028`, `Task/032` — **AWS-only** |
| 10 | **`SecureString` no se cifra** en el SSM emulado. | `Task/031` — ningún secreto real en el laboratorio |
| 11 | El arranque en frío del laboratorio **no es comparable** con el de AWS. | `Task/032` (**D-12**) — medir solo en AWS real |
| 12 | El laboratorio no emula dominios personalizados ni TLS gestionado. | `Task/035`, `Task/040` — **AWS-only** |

---

## Servicios excluidos de la arquitectura cloud

EC2, ECR, ECS Fargate, EKS, Application Load Balancer, NAT Gateway y Portainer en
producción. Motivo: costo fijo mensual y complejidad operativa injustificados para un
blog personal. Ver [ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md).
