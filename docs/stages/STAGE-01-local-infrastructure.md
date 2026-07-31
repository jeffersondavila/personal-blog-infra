# ETAPA 01 — Infraestructura Local

| Campo | Valor |
| --- | --- |
| **Número** | 01 |
| **Estado** | **Completada** |
| **Dependencias** | [ETAPA 00](STAGE-00-foundation.md) |
| **Tareas** | 2 |
| **Aprobadas** | 2 |
| **Avance** | **100 %** |
| **Hito que completa** | Entorno local reproducible y recuperable. ✔ |
| **Completada** | 2026-07-31 |
| **Última actualización** | 2026-07-31 |

---

## Objetivo

Disponer de un entorno local levantable con un solo comando, con datos persistentes,
supervisión visual mediante Portainer y capacidad demostrada de respaldo y recuperación.

## Por qué esta etapa existe

La estrategia local-first ([ADR-001](../adr/ADR-001-local-first.md)) exige que la base
de datos y el almacenamiento de objetos existan **antes** que las aplicaciones que los
consumen. Y un entorno que no se puede reconstruir ni restaurar no es un entorno fiable.

## Tareas

### `Task/003-Crear-Infraestructura-Local` — **Aprobada** (2026-07-29)

- [x] Docker Compose base.
- [x] PostgreSQL con volumen persistente.
- [x] MinIO como almacenamiento compatible con S3.
- [x] Portainer CE para supervisión local.
- [x] Redes Docker y aislamiento entre servicios.
- [x] Volúmenes nombrados.
- [x] Healthchecks por servicio, donde la imagen lo permite.

**Depende de:** `Task/002` — Aprobada ✔.
**Repositorio:** `personal-blog-infra`.
**Ficha:** [TASK-003](../tasks/TASK-003-create-local-infrastructure.md) ·
**Reporte:** [TASK-003-report](../task-reports/TASK-003-report.md) ·
**Runbook:** [local-environment.md](../runbooks/local-environment.md)

> `portainer` es el único servicio sin healthcheck: su imagen es *distroless* y no
> contiene ningún binario con el que sondearla desde dentro. Se verifica desde el host
> contra `https://127.0.0.1:9444/api/status`.

**Decisión resuelta:** D-05 — **Traefik v3** como reverse proxy local. Se eligió aquí; se
implementa en `Task/007-Integracion-Local`. Ver
[open-decisions.md](../architecture/open-decisions.md).

### `Task/004-Backups-y-Recuperacion-Local` — **Aprobada** (2026-07-31)

- [x] Backup y restauración de PostgreSQL con `pg_dump` / `pg_restore`, en caliente.
- [x] Copia del **contenido** de los objetos de MinIO, verificada por SHA-256.
- [x] Copia de los **metadatos y tags** de cada objeto, reaplicados y verificados al
      restaurar. El **historial de versiones** queda fuera del alcance y se detecta.
- [x] Registro de la **configuración de cada bucket**, sin reaplicarla al restaurar.
- [x] Respaldo del volumen de datos y configuración de Portainer.
- [x] Conjunto de respaldo por fecha, con manifiesto y checksums SHA-256.
- [x] Prueba de restauración en un entorno temporal **aislado** del principal.
- [x] Procedimiento de reconstrucción completa del entorno desde cero.
- [x] Política manual mínima de retención.

**Depende de:** `Task/003` — Aprobada ✔.
**Repositorio:** `personal-blog-infra`.
**Ficha:** [TASK-004](../tasks/TASK-004-local-backups-and-recovery.md) ·
**Reporte:** [TASK-004-report](../task-reports/TASK-004-report.md) ·
**Runbook:** [local-backup-and-recovery.md](../runbooks/local-backup-and-recovery.md) ·
**Scripts:** [scripts/backup/](../../scripts/backup/README.md)

> La copia es **externa a los volúmenes de Docker**: `Task/003` demostró que los datos
> sobreviven a `docker compose down`, y `Task/004` demuestra que sobreviven a
> `docker compose down -v`, que sí destruye los volúmenes.

## Criterios de salida de la etapa

- [x] `docker compose up -d` levanta todos los servicios sanos. — `Task/003`, verificado.
- [x] Los healthchecks pasan. — `Task/003`: `postgres` y `minio` en `healthy`.
- [x] Los datos sobreviven a `docker compose down` + `up`. — `Task/003`, verificado con
      datos reales de prueba.
- [x] Portainer muestra los contenedores, logs y volúmenes. — `Task/003`: la consola
      responde. El socket de Docker se monta con `:ro`, lo que protege el **archivo** del
      socket pero **no** limita la Docker API: Portainer conserva capacidad
      administrativa sobre el host. Ver R-09 en
      [STATUS](../project-management/STATUS.md) y el
      [runbook §2.1](../runbooks/local-environment.md).
- [x] Existe un backup restaurable de PostgreSQL, verificado. — `Task/004`: volcado
      `pg_dump` custom, checksums SHA-256 y **restauración probada** en instancia temporal
      aislada, con el dato de verificación recuperado íntegro.
- [x] Existe un runbook de reconstrucción del entorno. — `Task/003` entrega
      [local-environment.md](../runbooks/local-environment.md) (arranque, parada,
      verificación, diagnóstico) y `Task/004`
      [local-backup-and-recovery.md](../runbooks/local-backup-and-recovery.md)
      (respaldo, verificación y **recuperación tras pérdida total**).

> Los cuatro primeros criterios quedaron confirmados con la aprobación de `Task/003`
> (2026-07-29) y los dos últimos con la de `Task/004` (2026-07-31). **Los seis criterios
> de salida están cumplidos: la ETAPA 01 queda COMPLETADA** con 2 de 2 tareas aprobadas.

## Fuera del alcance de la etapa

- Backend y frontend (Etapa 02).
- Reverse proxy con aplicaciones reales (Etapa 02).
- Esquema de base de datos (Etapa 03).
- Cualquier recurso cloud.

## Riesgos conocidos

| Riesgo | Mitigación | Estado |
| --- | --- | --- |
| Puertos locales en conflicto con otros proyectos. | Puertos configurables por `.env`, documentados. En `Task/003` se materializó: otro proyecto ya ocupaba `5432` y `9443`, y se eligieron `55432` y `9444`. | **Materializado y mitigado** |
| Pérdida de datos al recrear contenedores. | Volúmenes nombrados, verificados en `Task/003`; backup externo con restauración demostrada en `Task/004`. | **Mitigado** — R-08 cerrado; queda R-11 (el backup es manual) |
| Credenciales de desarrollo filtradas al repositorio. | `.env` ignorado por `.gitignore`; solo `.env.example` con valores ficticios `change-me-*`. Verificado en `Task/003`. | Mitigado |
| Imágenes fijadas que envejecen y acumulan vulnerabilidades. | Escaneo en `Task/018`; validación del Compose en CI en `Task/021`. | Abierto — R-10 |
| Portainer conserva capacidad administrativa sobre el daemon de Docker. | Aceptado por ser local, publicado en `127.0.0.1` y autenticado. No exponerlo nunca. Socket proxy a evaluar en `Task/018`. | Abierto — R-09 |

## Resultado de la etapa

Con `Task/003` y `Task/004` aprobadas, el proyecto dispone de un **entorno local
reproducible y recuperable**:

| Entregable | Dónde |
| --- | --- |
| Docker Compose con PostgreSQL, MinIO y Portainer CE | [`docker-compose.yml`](../../docker-compose.yml) |
| Variables documentadas con valores ficticios | [`.env.example`](../../.env.example) |
| Operación del entorno | [local-environment.md](../runbooks/local-environment.md) |
| Respaldo, verificación y recuperación | [local-backup-and-recovery.md](../runbooks/local-backup-and-recovery.md) |
| Scripts de backup y restauración | [scripts/backup/](../../scripts/backup/README.md) |

Decisión resuelta en la etapa: **D-05 — Traefik v3** como reverse proxy local, a
implementar en `Task/007`.

## Siguiente etapa

[ETAPA 02 — Fundaciones de las Aplicaciones](STAGE-02-application-foundations.md), que
empieza con `Task/005-Fundacion-Backend-FastAPI`: el **primer código de aplicación** del
proyecto, en `personal-blog-backend`.
