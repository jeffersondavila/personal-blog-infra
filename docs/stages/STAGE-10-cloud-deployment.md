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

## Relación con la ETAPA 08 — reutilizar, no reinventar

`Task/030`–`Task/033` **no crean recursos Terraform nuevos**. La expectativa explícita es:

> **Utilizar los módulos construidos y validados localmente en `Task/025` y materializarlos
> contra AWS real.**

Esta etapa es, además, donde el proyecto descubre **qué era realmente cierto** del
laboratorio local. Por cada recurso se documenta y se clasifica:

| Categoría | Significado |
| --- | --- |
| **Funcionó sin cambios** | El módulo se aplicó tal cual. |
| **Cambio de configuración** | Bastó ajustar variables, endpoints o nombres. |
| **Adaptación necesaria** | Hubo que modificar el diseño del recurso. |
| **No simulable localmente** | El emulador no lo reproducía con fidelidad suficiente. |
| **AWS-only** | Nunca pudo validarse en local por naturaleza. |

Diferencias que hay que comparar de forma expresa: **IAM** (autorización real, que el
laboratorio **no** ejercita), **red y DNS** (`execute-api`, TLS, dominios personalizados),
**cuotas y límites de cuenta**, **arranque en frío real** de la Lambda, **cifrado real de
`SecureString`** en SSM y **evaluación real de alarmas** en CloudWatch.

Toda esa evidencia se vuelca en la **matriz de paridad** de
[aws-local-parity.md](../architecture/aws-local-parity.md) §7, cuyas celdas pasan aquí a
`Validada en AWS`. Ninguna celda puede marcarse así sin haberse ejecutado contra AWS real.

**AWS real es la autoridad final.** Si el laboratorio y AWS discrepan, AWS tiene razón y el
laboratorio se corrige.

## Tareas

| Tarea | Contenido | Depende de |
| --- | --- | --- |
| `Task/030-Desplegar-Amazon-S3` | Bucket, CORS, políticas, URLs prefirmadas, lifecycle. **Destino y retención de los backups del VPS**, **materialización de la identidad decidida en D-16** y **validación de `S3Storage` contra S3 real**. Resuelve **D-08**. | `Task/029` |
| `Task/031-Desplegar-SSM-y-CloudWatch` | Parámetros **`SecureString`** y permisos IAM mínimos. **CloudWatch mínimo**: grupos de logs, **retención corta y explícita** (**D-11**), alarmas mínimas. **Base de la integración `CloudWatch → Grafana Cloud`: decide D-20** y su modelo IAM de **solo lectura**. **Alcance exclusivamente AWS: no observa el VPS.** | `Task/029` |
| `Task/032-Desplegar-AWS-Lambda` | Función, rol IAM, configuración, memoria y timeout. ***Reserved Concurrency*** coherente con el pool de PgBouncer, **RTT real `Lambda → PgBouncer` medido** y *wiring* de `S3Storage`. | `Task/030`, `Task/031` |
| `Task/033-Desplegar-API-Gateway` | HTTP API, rutas, CORS, throttling. | `Task/032` |
| `Task/034-Desplegar-Cloudflare-Pages` | Build de React, variables, dominio. | `Task/033` |
| `Task/035-Configurar-DNS` | Dominio principal, `www`, `api`, `media` si corresponde. | `Task/034` |
| `Task/036-Publicar-Primer-Contenido` | Migraciones, administrador, perfil, artículo, review, video, imágenes. | `Task/035` |

**Repositorio principal:** `personal-blog-infra` (Terraform), con participación de
`personal-blog-frontend` y `personal-blog-backend` en `Task/034` y `Task/036`.

## Criterios de salida de la etapa

- [ ] El bucket S3 es privado; el acceso a archivos usa URLs prefirmadas.
- [ ] Toda la configuración vive en SSM Parameter Store, nunca en el código.
- [ ] Los logs llegan a CloudWatch con retención limitada y explícita, y el alcance de
      CloudWatch se mantiene **mínimo**: sin *dashboards* elaborados ni funcionalidades no
      justificadas.
- [ ] **D-20 decidida**: está definido con qué mecanismo IAM de **solo lectura** accedería
      Grafana Cloud a CloudWatch, sin credenciales de larga vida versionadas. **Implementarla
      no es obligatorio en esta etapa; decidirla, sí.**
- [ ] La Lambda responde correctamente a través de API Gateway.
- [ ] API Gateway tiene throttling configurado.
- [ ] El frontend está publicado en Cloudflare Pages y consume el API real.
- [ ] El dominio resuelve por HTTPS con certificado válido.
- [ ] Existe contenido real publicado y visible en el sitio.
- [ ] El costo real observado coincide con lo estimado.
- [ ] El **destino de backups del VPS** existe en S3, con su política, su retención y el
      **principal de acceso** derivado de **D-16**, sin credenciales versionadas.
- [ ] `S3Storage` —cuyo código entrega `Task/010`— **funciona contra S3 real**.
- [ ] La **`Reserved Concurrency`** de la Lambda es coherente con el pool de PgBouncer y con
      `max_connections`, según los números derivados en `Task/029`.
- [ ] Los módulos aplicados son los **validados en `Task/025`**, no módulos nuevos.
- [ ] La **matriz de paridad** queda actualizada con evidencia real de AWS, recurso a
      recurso y con la clasificación de diferencias.

## Fuera del alcance de la etapa

- Automatizar el despliegue (Etapa 11).
- Validación final integral y protección de costos permanente (Etapa 12).
- EC2, ECS, ECR, EKS, ALB y NAT Gateway (excluidos por ADR-003).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Bucket S3 accidentalmente público. | Bloqueo de acceso público a nivel de cuenta y bucket; verificación explícita. |
| Retención de logs infinita generando costo creciente. | Retención definida en `Task/031`; refuerzo en `Task/041`. |
| **Dar a un tercero acceso amplio o permanente a AWS** al integrar la observabilidad (**D-20**). | Permiso **mínimo**, **solo lectura** y sin credenciales de larga vida versionadas. El compromiso de Grafana Cloud **no debe** implicar el de AWS. |
| CORS mal configurado que rompe el frontend. | Orígenes permitidos explícitos; prueba desde el dominio real. |
| Propagación de DNS más lenta de lo previsto. | TTL bajo durante el corte; ventana de validación holgada. |
| Arranque en frío perceptible en la primera visita. | Medición y ajuste de memoria de la Lambda. |

## Siguiente etapa

[ETAPA 11 — Automatización de Despliegues](STAGE-11-deployment-automation.md)
