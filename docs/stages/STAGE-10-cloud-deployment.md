# ETAPA 10 — Despliegue Cloud

| Campo | Valor |
| --- | --- |
| **Número** | 10 |
| **Estado** | Pendiente |
| **Dependencias** | [ETAPA 09](STAGE-09-cloud-accounts.md) |
| **Tareas** | 7 |
| **Aprobadas** | 0 |
| **Avance** | 0 % |
| **Hito que completa** | Blog en línea y accesible por dominio propio. |

---

## Objetivo

Desplegar el blog en la nube siguiendo el orden de dependencias —almacenamiento,
configuración, cómputo, entrada HTTP, frontend, DNS— y publicar el primer contenido real.

## Por qué esta etapa existe

Es la materialización de la arquitectura de
[ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md). El orden de las tareas no es
arbitrario: cada una habilita a la siguiente.

## Tareas

| Tarea | Contenido | Depende de |
| --- | --- | --- |
| `Task/030-Desplegar-Amazon-S3` | Bucket, CORS, políticas, URLs prefirmadas, lifecycle. | `Task/029` |
| `Task/031-Desplegar-SSM-y-CloudWatch` | Parámetros, grupos de logs, retención, alarmas mínimas. | `Task/029` |
| `Task/032-Desplegar-AWS-Lambda` | Función, rol IAM, configuración, memoria y timeout. | `Task/030`, `Task/031` |
| `Task/033-Desplegar-API-Gateway` | HTTP API, rutas, CORS, throttling. | `Task/032` |
| `Task/034-Desplegar-Cloudflare-Pages` | Build de React, variables, dominio. | `Task/033` |
| `Task/035-Configurar-DNS` | Dominio principal, `www`, `api`, `media` si corresponde. | `Task/034` |
| `Task/036-Publicar-Primer-Contenido` | Migraciones, administrador, perfil, artículo, review, video, imágenes. | `Task/035` |

**Repositorio principal:** `personal-blog-infra` (Terraform), con participación de
`personal-blog-frontend` y `personal-blog-backend` en `Task/034` y `Task/036`.

## Criterios de salida de la etapa

- [ ] El bucket S3 es privado; el acceso a archivos usa URLs prefirmadas.
- [ ] Toda la configuración vive en SSM Parameter Store, nunca en el código.
- [ ] Los logs llegan a CloudWatch con retención limitada y explícita.
- [ ] La Lambda responde correctamente a través de API Gateway.
- [ ] API Gateway tiene throttling configurado.
- [ ] El frontend está publicado en Cloudflare Pages y consume el API real.
- [ ] El dominio resuelve por HTTPS con certificado válido.
- [ ] Existe contenido real publicado y visible en el sitio.
- [ ] El costo real observado coincide con lo estimado.

## Fuera del alcance de la etapa

- Automatizar el despliegue (Etapa 11).
- Validación final integral y protección de costos permanente (Etapa 12).
- EC2, ECS, ECR, EKS, ALB y NAT Gateway (excluidos por ADR-003).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Bucket S3 accidentalmente público. | Bloqueo de acceso público a nivel de cuenta y bucket; verificación explícita. |
| Retención de logs infinita generando costo creciente. | Retención definida en `Task/031`; refuerzo en `Task/041`. |
| CORS mal configurado que rompe el frontend. | Orígenes permitidos explícitos; prueba desde el dominio real. |
| Propagación de DNS más lenta de lo previsto. | TTL bajo durante el corte; ventana de validación holgada. |
| Arranque en frío perceptible en la primera visita. | Medición y ajuste de memoria de la Lambda. |

## Siguiente etapa

[ETAPA 11 — Automatización de Despliegues](STAGE-11-deployment-automation.md)
