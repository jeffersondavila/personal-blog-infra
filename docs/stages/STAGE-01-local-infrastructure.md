# ETAPA 01 — Infraestructura Local

| Campo | Valor |
| --- | --- |
| **Número** | 01 |
| **Estado** | Pendiente |
| **Dependencias** | [ETAPA 00](STAGE-00-foundation.md) |
| **Tareas** | 2 |
| **Aprobadas** | 0 |
| **Avance** | 0 % |
| **Hito que completa** | Entorno local reproducible y recuperable. |

---

## Objetivo

Disponer de un entorno local levantable con un solo comando, con datos persistentes,
supervisión visual mediante Portainer y capacidad demostrada de respaldo y recuperación.

## Por qué esta etapa existe

La estrategia local-first ([ADR-001](../adr/ADR-001-local-first.md)) exige que la base
de datos y el almacenamiento de objetos existan **antes** que las aplicaciones que los
consumen. Y un entorno que no se puede reconstruir ni restaurar no es un entorno fiable.

## Tareas

### `Task/003-Crear-Infraestructura-Local` — *Pendiente*

- Docker Compose base.
- PostgreSQL con volumen persistente.
- MinIO como almacenamiento compatible con S3.
- Portainer CE para supervisión local.
- Redes Docker y aislamiento entre servicios.
- Volúmenes nombrados.
- Healthchecks por servicio.

**Depende de:** `Task/002`.
**Repositorio:** `personal-blog-infra`.

### `Task/004-Backups-y-Recuperacion-Local` — *Pendiente*

- Backup y restauración de PostgreSQL.
- Verificación de persistencia de MinIO.
- Respaldo de la configuración de Portainer.
- Procedimiento de reconstrucción completa del entorno desde cero.

**Depende de:** `Task/003`.
**Repositorio:** `personal-blog-infra`.

## Criterios de salida de la etapa

- [ ] `docker compose up -d` levanta todos los servicios sanos.
- [ ] Los healthchecks pasan.
- [ ] Los datos sobreviven a `docker compose down` + `up`.
- [ ] Portainer muestra los contenedores, logs y volúmenes.
- [ ] Existe un backup restaurable de PostgreSQL, verificado.
- [ ] Existe un runbook de reconstrucción del entorno.

## Fuera del alcance de la etapa

- Backend y frontend (Etapa 02).
- Reverse proxy con aplicaciones reales (Etapa 02).
- Esquema de base de datos (Etapa 03).
- Cualquier recurso cloud.

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Puertos locales en conflicto con otros proyectos. | Puertos configurables por `.env`, documentados. |
| Pérdida de datos al recrear contenedores. | Volúmenes nombrados + backup verificado en `Task/004`. |
| Credenciales de desarrollo filtradas al repositorio. | `.env` ignorado; solo `.env.example` con valores ficticios. |

## Siguiente etapa

[ETAPA 02 — Fundaciones de las Aplicaciones](STAGE-02-application-foundations.md)
