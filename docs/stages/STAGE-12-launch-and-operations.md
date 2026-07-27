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

**Depende de:** `Task/039`. **Repositorios:** los tres.

### `Task/041-Proteccion-de-Costos` — *Pendiente*

Presupuestos, alarmas, retención de logs, límites de servicio y revisión periódica de
recursos activos.

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
- [ ] Presupuestos y alarmas activos y probados.
- [ ] Retención de logs limitada y verificada.
- [ ] Existe una lista revisable de todos los recursos cloud activos y su costo.
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
