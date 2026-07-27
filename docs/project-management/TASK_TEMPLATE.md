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
| **Rama** | `Task/<numero>-<nombre>` (creada desde `dev`) |
| **Fecha de inicio** | AAAA-MM-DD |
| **Última actualización** | AAAA-MM-DD |

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

## 7. Plan de validación

Cómo se comprueba cada criterio de aceptación.

## 8. Comandos de validación

```bash
# Comandos exactos, no destructivos, con su propósito
```

## 9. Evidencia esperada

Salidas, capturas, archivos o registros que demuestran que la tarea funciona.

## 10. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| | | | |

## 11. Decisiones técnicas

| Decisión | Alternativas consideradas | Justificación | ¿ADR? |
| --- | --- | --- | --- |
| | | | |

## 12. Documentación creada o actualizada

- `ruta/archivo.md` — qué cambió.

## 13. Archivos modificados

| Repositorio | Archivo | Acción (creado/modificado) |
| --- | --- | --- |
| | | |

## 14. Resultado de pruebas

| Prueba | Comando | Resultado |
| --- | --- | --- |
| | | |

Si algo falló, se registra el fallo tal cual, sin omitirlo.

## 15. Problemas encontrados

Incidencias durante la ejecución y cómo se resolvieron (o por qué siguen abiertas).

## 16. Pasos de validación para el usuario

Instrucciones exactas y reproducibles para que el usuario verifique el resultado.

```bash
# comandos que el usuario puede ejecutar
```

## 17. Deuda técnica pendiente

Lo que queda por hacer y en qué tarea se abordará.

## 18. Próxima tarea

`Task/<numero+1>-<nombre>` — breve descripción.

## 19. Aprobación

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
