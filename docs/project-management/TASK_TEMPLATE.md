# TASK_TEMPLATE — Plantilla reutilizable de tarea

Copia este archivo a `docs/tasks/TASK-<numero>-<nombre>.md` y complétalo.
No elimines secciones: si una no aplica, escribe `No aplica` y la razón.

---

```markdown
# TASK-<numero> — <Nombre de la tarea>

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/<numero>-<nombre>` |
| **Nombre** | <nombre legible> |
| **Etapa** | ETAPA <nn> — <nombre de la etapa> |
| **Estado** | Pendiente \| En progreso \| Lista para validación \| Aprobada \| Bloqueada \| Descartada |
| **Repositorios involucrados** | personal-blog-infra \| personal-blog-frontend \| personal-blog-backend |
| **Dependencias** | `Task/<n>` (deben estar Aprobadas) |
| **Rama** | `Task/<numero>-<nombre>` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | `<git rev-parse main en el momento de crear la rama>` |
| **Fecha de inicio** | AAAA-MM-DD |
| **Última actualización** | AAAA-MM-DD |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](WORKFLOW.md) §2.1).

| # | Comprobación | Resultado |
| --- | --- | --- |
| 1 | `main == origin/main` | |
| 2 | Working tree limpio antes de crear la rama | |
| 3 | Rama creada **desde `main`** | |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | |

El **SHA base se obtiene dinámicamente** al crear la rama; no se fija de antemano ni se
copia de otra tarea.

```powershell
git fetch --prune origin
git switch main
git pull --ff-only origin main
git status --porcelain                          # vacio
git rev-parse main; git rev-parse origin/main   # deben coincidir

git switch -c Task/<numero>-<nombre>

git rev-parse HEAD; git rev-parse main          # deben coincidir
```

---

## 1. Objetivo

Qué se quiere lograr, en una o dos frases verificables.

## 2. Contexto

Por qué se hace ahora, qué la precede y qué depende de ella.

## 3. Dentro del alcance

- [ ] Elemento 1
- [ ] Elemento 2

## 4. Fuera del alcance

Lo que explícitamente **no** se hace en esta tarea y en qué tarea futura corresponde.

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| | | |

## 6. Criterios de aceptación

1. Criterio verificable 1.
2. Criterio verificable 2.

## 7. TDD / Plan test-first

> **Obligatoria** para tareas de backend **funcional** (dominio, casos de uso, API pública o
> administrativa, persistencia, autenticación, autorización, auditoría, `ObjectStorage`).
> En cualquier otra tarea, escribe `No aplica` y la razón.
> Regla completa: [`BACKEND_TESTING_STRATEGY.md`](BACKEND_TESTING_STRATEGY.md).

### 7.1 Comportamientos a construir

- Comportamiento observable 1.
- Comportamiento observable 2.

### 7.2 Matriz de casos

Se completa **antes** de escribir implementación.

| Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- |
| Happy path | | | | dominio |
| Edge | | | | aplicación |
| Error | | | | HTTP |
| Seguridad | | | | integración |

### 7.3 Tests RED esperados

| Test | Capa | Motivo de fallo esperado |
| --- | --- | --- |
| `test_<comportamiento>` | | |

### 7.4 Integración necesaria

PostgreSQL real, MinIO u otra dependencia, y por qué el comportamiento la exige.

### 7.5 Casos negativos y de seguridad

No autenticado, sin permisos, recurso inexistente, contenido no publicado, entrada inválida.

### 7.6 Regresiones relevantes

Pruebas existentes que deben seguir pasando y defectos previos que no pueden reaparecer.

## 8. Plan de validación

Cómo se comprueba cada criterio de aceptación.

## 9. Comandos de validación

```bash
# Comandos exactos, no destructivos, con su propósito
```

## 10. Evidencia esperada

Salidas, capturas, archivos o registros que demuestran que la tarea funciona.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| | | | |

## 12. Decisiones técnicas

| Decisión | Alternativas consideradas | Justificación | ¿ADR? |
| --- | --- | --- | --- |
| | | | |

## 13. Documentación creada o actualizada

- `ruta/archivo.md` — qué cambió.

## 14. Archivos modificados

| Repositorio | Archivo | Acción (creado/modificado) |
| --- | --- | --- |
| | | |

## 15. Resultado de pruebas

| Prueba | Comando | Resultado |
| --- | --- | --- |
| | | |

Si algo falló, se registra el fallo tal cual, sin omitirlo.

## 16. Problemas encontrados

Incidencias durante la ejecución y cómo se resolvieron (o por qué siguen abiertas).

## 17. Pasos de validación para el usuario

Instrucciones exactas y reproducibles para que el usuario verifique el resultado.

```bash
# comandos que el usuario puede ejecutar
```

## 18. Deuda técnica pendiente

Lo que queda por hacer y en qué tarea se abordará.

## 19. Próxima tarea

`Task/<numero+1>-<nombre>` — breve descripción.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | *(pendiente)* |
| **Aprobado por** | *(pendiente — solo el usuario)* |
| **Expresión de aprobación** | `approved: Task/<numero>-<nombre>` |

> Esta sección solo se completa cuando el usuario autoriza explícitamente la aprobación.
> Claude nunca la completa por iniciativa propia.
```

---

## Notas de uso

- El nombre del archivo de la ficha usa el número de tarea a tres dígitos.
- El reporte final asociado va en `docs/task-reports/TASK-<numero>-report.md`.
- Al terminar, actualiza [`STATUS.md`](STATUS.md) y [`ROADMAP.md`](ROADMAP.md).
- Verifica [`DEFINITION_OF_DONE.md`](DEFINITION_OF_DONE.md) antes de marcar
  `Lista para validación`.
- Si la tarea introduce **comportamiento funcional del backend**, la sección 7 es
  **obligatoria** y se completa **antes** de escribir implementación. La práctica completa
  está en [`BACKEND_TESTING_STRATEGY.md`](BACKEND_TESTING_STRATEGY.md).
