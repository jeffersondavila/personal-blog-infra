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
| `Task/005-Fundacion-Backend-FastAPI` | [TASK-005-report.md](TASK-005-report.md) | Aprobada (2026-08-12) |
| `Task/005.1-Formalizar-TDD-Backend` *(mantenimiento)* | [TASK-005.1-report.md](TASK-005.1-report.md) | Aprobada (2026-08-13) |

> Las tareas de **mantenimiento** llevan sufijo (`005.1`) y **no cuentan** dentro de las 41
> tareas del roadmap.
