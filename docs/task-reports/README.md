# Reportes de tarea

Esta carpeta contiene el **resumen final de ejecución** de cada tarea del roadmap.

---

## Qué es un reporte de tarea

Es el documento que se entrega al usuario cuando una tarea queda `Lista para validación`.
Responde a: qué se encontró, qué se hizo, qué se validó y cómo comprobarlo.

Se diferencia de la ficha de tarea (`docs/tasks/`):

| Documento | Propósito | Momento |
| --- | --- | --- |
| `docs/tasks/TASK-<n>-<nombre>.md` | Ficha viva: alcance, criterios, decisiones, riesgos. | Se escribe durante la ejecución. |
| `docs/task-reports/TASK-<n>-report.md` | Reporte cerrado: qué ocurrió y qué debe validar el usuario. | Se escribe al finalizar la ejecución. |

---

## Convención de nombres

```
TASK-<numero-3-digitos>-report.md
```

Ejemplo: `TASK-001-report.md`.

---

## Contenido mínimo

1. Identificación de la tarea y su estado final.
2. Estado inicial encontrado (repositorios, ramas, archivos).
3. Cambios realizados, por repositorio.
4. Validaciones ejecutadas y su resultado real, incluidos los fallos.
5. Problemas encontrados y cómo se resolvieron.
6. Riesgos y decisiones pendientes.
7. Instrucciones exactas de validación para el usuario.
8. Próxima tarea propuesta.
9. Confirmación explícita de límites respetados (sin commits, sin push, sin recursos
   cloud, sin avanzar a la siguiente tarea).

---

## Reglas

- El reporte registra el resultado **real**: si una validación falló, se dice.
- Nunca contiene secretos, credenciales ni tokens.
- No declara una tarea `Aprobada`: eso solo lo autoriza el usuario mediante
  `approved: Task/<nombre-de-rama>`.

---

## Índice de reportes

| Tarea | Reporte | Estado |
| --- | --- | --- |
| `Task/001-Inicializar-Workspace-y-Roadmap` | [TASK-001-report.md](TASK-001-report.md) | Aprobada (2026-07-26) |
| `Task/002-Definir-MVP-y-Arquitectura` | [TASK-002-report.md](TASK-002-report.md) | Aprobada (2026-07-26) |
| `Task/003-Crear-Infraestructura-Local` | [TASK-003-report.md](TASK-003-report.md) | Aprobada (2026-07-29) |
| `Task/004-Backups-y-Recuperacion-Local` | [TASK-004-report.md](TASK-004-report.md) | Aprobada (2026-07-31) |
| `Task/004.1-Corregir-Backup-Rutas-Literales` *(mantenimiento)* | [TASK-004.1-report.md](TASK-004.1-report.md) | Aprobada (2026-09-06) |
| `Task/004.2-Corregir-Drift-Documental-Post-Merge` *(mantenimiento)* | [TASK-004.2-report.md](TASK-004.2-report.md) | Aprobada (2026-09-06) |
| `Task/005-Fundacion-Backend-FastAPI` | [TASK-005-report.md](TASK-005-report.md) | Aprobada (2026-08-12) |
| `Task/005.1-Formalizar-TDD-Backend` *(mantenimiento)* | [TASK-005.1-report.md](TASK-005.1-report.md) | Aprobada (2026-08-13) |
| `Task/005.2-Documentar-Estrategia-Floci-IaC-Local` *(mantenimiento)* | [TASK-005.2-report.md](TASK-005.2-report.md) | Aprobada (2026-08-15) |
| `Task/005.3-Definir-PostgreSQL-Produccion-en-VPS` *(mantenimiento)* | [TASK-005.3-report.md](TASK-005.3-report.md) | Aprobada (2026-08-15) |
| `Task/005.4-Corregir-Base-Ramas-Task-Main` *(mantenimiento)* | [TASK-005.4-report.md](TASK-005.4-report.md) | Aprobada (2026-08-15) |
| `Task/005.5-Alinear-Planificacion-Tras-Auditoria` *(mantenimiento)* | [TASK-005.5-report.md](TASK-005.5-report.md) | Aprobada (2026-08-16) |
| `Task/005.6-Cerrar-Fundaciones-Tras-Mega-Auditoria` *(mantenimiento)* | [TASK-005.6-report.md](TASK-005.6-report.md) | Aprobada (2026-08-16) |
| `Task/005.7-Cerrar-Hallazgos-Finales-de-Certificacion` *(mantenimiento)* | [TASK-005.7-report.md](TASK-005.7-report.md) | Aprobada (2026-08-16) |
| `Task/006-Fundacion-Frontend-React` | [TASK-006-report.md](TASK-006-report.md) | Aprobada (2026-08-18) |
| `Task/006.1-Corregir-Drift-Documental-Post-Merge` *(mantenimiento)* | [TASK-006.1-report.md](TASK-006.1-report.md) | Aprobada (2026-08-21) |
| `Task/006.2-Formalizar-Arquitectura-Objetivo-Produccion` *(mantenimiento)* | [TASK-006.2-report.md](TASK-006.2-report.md) | Aprobada (2026-08-23) |
| `Task/007-Integracion-Local` | [TASK-007-report.md](TASK-007-report.md) | Aprobada (2026-08-23) |
| `Task/008-Modelo-de-Datos` | [TASK-008-report.md](TASK-008-report.md) | Aprobada (2026-08-25) |
| `Task/009-API-Publica` | [TASK-009-report.md](TASK-009-report.md) | Aprobada (2026-08-27) — remediacion TDD previa a la aprobacion |
| `Task/009.1-Corregir-Drift-Documental-Post-Merge` *(mantenimiento)* | [TASK-009.1-report.md](TASK-009.1-report.md) | Aprobada (2026-08-27) |
| `Task/010-Almacenamiento-Compatible-S3` | [TASK-010-report.md](TASK-010-report.md) | Aprobada (2026-08-28) |
| `Task/011-Autenticacion-Administrativa` | [TASK-011-report.md](TASK-011-report.md) | Aprobada (2026-09-01) |
| `Task/012-API-Administrativa` | [TASK-012-report.md](TASK-012-report.md) | Aprobada (2026-09-03) |
| `Task/012.1-Exponer-Auditoria-Para-Dashboard` *(mantenimiento)* | [TASK-012.1-report.md](TASK-012.1-report.md) | Aprobada (2026-09-05) |
| `Task/013-Sistema-de-Diseno` | [TASK-013-report.md](TASK-013-report.md) | Aprobada (2026-09-04) |
| `Task/013.1-Corregir-Drift-Documental-Post-Merge` *(mantenimiento)* | [TASK-013.1-report.md](TASK-013.1-report.md) | Aprobada (2026-09-04) |
| `Task/014-Sitio-Publico` | [TASK-014-report.md](TASK-014-report.md) | Aprobada (2026-09-05) |
| `Task/015-Panel-Administrativo` | [TASK-015-report.md](TASK-015-report.md) | Aprobada (2026-09-05) |
| `Task/016-SEO-Accesibilidad-y-Rendimiento` | [TASK-016-report.md](TASK-016-report.md) | Aprobada (2026-09-06) |
| `Task/017-Observabilidad-Local` | [TASK-017-report.md](TASK-017-report.md) | Aprobada (2026-09-06) |
| `Task/018-Endurecimiento-de-Seguridad` | [TASK-018-report.md](TASK-018-report.md) | Aprobada (2026-09-08) |
| `Task/019-CI-Frontend` | [TASK-019-report.md](TASK-019-report.md) | Aprobada (2026-09-08) |
| `Task/019.1-Corregir-Drift-Documental-Post-Merge` *(mantenimiento)* | [TASK-019.1-report.md](TASK-019.1-report.md) | Aprobada (2026-09-09) |
| `Task/020-CI-Backend` | [TASK-020-report.md](TASK-020-report.md) | Aprobada (2026-09-10) |
| `Task/020.1-Corregir-Drift-Documental-Post-Merge` *(mantenimiento)* | [TASK-020.1-report.md](TASK-020.1-report.md) | Aprobada (2026-09-10) |
| `Task/020.2-Corregir-Autodescripcion-Obsoleta-de-Task020.1` *(mantenimiento)* | [TASK-020.2-report.md](TASK-020.2-report.md) | Aprobada (2026-09-10) |

> Las tareas de **mantenimiento** llevan sufijo (`004.1`, `004.2`, `005.1`, `005.2`,
> `005.3`, `005.4`, `005.5`, `005.6`, `005.7`, `006.1`, `006.2`, `009.1`, `012.1`,
> `013.1`, `019.1`, `020.1`, `020.2`) y **no cuentan** dentro de las 41 tareas del roadmap.
>
> El indice omitia `Task/010` a `Task/017`, cuyos reportes existian desde su
> aprobacion. Se completo el 2026-09-07 durante `Task/018`.
