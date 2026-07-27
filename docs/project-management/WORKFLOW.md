# WORKFLOW — Proceso de trabajo

Define cómo se selecciona, ejecuta, valida, aprueba e integra cada tarea del proyecto.

---

## 1. Estados oficiales de una tarea

Solo se permiten estos seis estados:

| Estado | Significado | Quién lo asigna |
| --- | --- | --- |
| `Pendiente` | Registrada en el backlog, no iniciada. | Claude / usuario |
| `En progreso` | Trabajo activo en su rama `Task/*`. | **Claude** |
| `Lista para validación` | Alcance completo, validaciones ejecutadas, reporte creado. | **Claude** |
| `Aprobada` | El usuario verificó y autorizó el cierre. | **Solo el usuario** |
| `Bloqueada` | No puede avanzar. Debe indicar motivo y desbloqueo necesario. | Claude / usuario |
| `Descartada` | Se decide no ejecutarla. Debe indicar justificación. | **Solo el usuario** |

Reglas:

- Claude **puede** marcar `En progreso` y `Lista para validación`.
- Claude **nunca** marca `Aprobada`. La aprobación es exclusiva del usuario.
- Toda tarea `Bloqueada` debe registrar en `STATUS.md`: **motivo** y **acción de desbloqueo**.

---

## 2. Ciclo de vida de una tarea

1. **Seleccionar una tarea pendiente**
   Desde [`STATUS.md`](STATUS.md), eligiendo la siguiente en orden del roadmap.

2. **Confirmar sus dependencias**
   Todas las tareas de las que depende deben estar `Aprobada`.
   Si alguna no lo está, la tarea no puede iniciarse.

3. **Crear la rama Task desde `dev`**
   ```
   git switch dev
   git pull --ff-only            # si hay remoto y seguimiento
   git switch -c Task/<numero>-<nombre>
   ```
   Si la tarea afecta a varios repositorios, se crea **la misma rama** en cada uno.

4. **Marcarla `En progreso`**
   Actualizar `STATUS.md` y `ROADMAP.md`.

5. **Implementar únicamente su alcance**
   Nada fuera de *Dentro del alcance*. Lo detectado de más se anota como deuda o
   como tarea futura, no se implementa.

6. **Ejecutar validaciones**
   Las declaradas en la ficha de la tarea (build, lint, tests, comprobaciones manuales).
   Se registra el resultado real, incluidos los fallos.

7. **Crear reporte de tarea**
   - Ficha: `docs/tasks/TASK-<numero>-<nombre>.md` (a partir de [`TASK_TEMPLATE.md`](TASK_TEMPLATE.md)).
   - Reporte final: `docs/task-reports/TASK-<numero>-report.md`.

8. **Marcarla `Lista para validación`**
   Actualizar `STATUS.md` y `ROADMAP.md`. Verificar
   [`DEFINITION_OF_DONE.md`](DEFINITION_OF_DONE.md).

9. **Esperar validación del usuario**
   Claude se detiene. No inicia la siguiente tarea.

10. **Corregir observaciones**
    Si el usuario reporta problemas, se corrigen en la misma rama `Task/*` y se vuelve
    al paso 6.

11. **Recibir aprobación**
    El usuario autoriza explícitamente (ver sección 3).

12. **Integrarla según el flujo autorizado**
    Solo entonces se ejecuta el cierre descrito en la sección 3.

---

## 3. Aprobación y cierre

La expresión exacta que autoriza el cierre de una tarea es:

```
approved: Task/<nombre-de-rama>
```

Ejemplo:

```
approved: Task/001-Inicializar-Workspace-y-Roadmap
```

Al recibirla —y **solo** entonces— se ejecuta este flujo en cada repositorio afectado:

1. **Crear commit si falta** — confirmar el trabajo pendiente en la rama `Task/*`.
2. **Integrar la rama Task en `dev`** — merge de `Task/*` → `dev`.
3. **Hacer push de `dev`** al remoto.
4. **Publicar la rama Task** (`git push -u origin Task/*`).
5. **Crear pull request hacia `main`** desde `dev`.
6. **Volver a `main`** localmente.
7. **Actualizar referencias** (`git fetch --prune`, sincronizar `main`).
8. **Limpiar la rama local** `Task/*` una vez integrada.

Restricciones:

- **No se hace merge automático hacia `main`.** El PR hacia `main` queda abierto para
  revisión y lo cierra el usuario.
- Sin la expresión `approved:`, no se hace commit, merge, push ni PR.
- La aprobación es por tarea: aprobar una tarea no autoriza iniciar la siguiente.

---

## 4. Estrategia de ramas

| Rama | Propósito | Origen | Destino |
| --- | --- | --- | --- |
| `main` | Versión estable o liberable. | — | — |
| `dev` | Integración de tareas aprobadas. | `main` | PR → `main` |
| `Task/<numero>-<nombre>` | Trabajo aislado de una tarea. | `dev` | merge → `dev` |

Reglas:

- Nunca se trabaja directamente sobre `main` ni sobre `dev`.
- Una tarea que afecta a varios repositorios usa **el mismo nombre de rama** en todos.
- No se reescribe historial publicado (`rebase`/`push --force` sobre ramas compartidas).

### Estado actual de las ramas

Los tres repositorios están en `main` **sin commits** (rama no nacida). Git no permite
crear `dev` ni `Task/*` mientras no exista al menos un commit. La creación de ramas se
realizará durante la aprobación de `Task/001`; los pasos exactos están en
[`../tasks/TASK-001-initial-workspace-and-roadmap.md`](../tasks/TASK-001-initial-workspace-and-roadmap.md).

---

## 5. Convención de nombres

| Elemento | Formato | Ejemplo |
| --- | --- | --- |
| Rama de tarea | `Task/<numero-3-digitos>-<Nombre-En-Kebab>` | `Task/003-Crear-Infraestructura-Local` |
| Ficha de tarea | `docs/tasks/TASK-<numero>-<nombre-en-ingles>.md` | `docs/tasks/TASK-001-initial-workspace-and-roadmap.md` |
| Reporte | `docs/task-reports/TASK-<numero>-report.md` | `docs/task-reports/TASK-001-report.md` |
| Ficha de etapa | `docs/stages/STAGE-<nn>-<nombre>.md` | `docs/stages/STAGE-01-local-infrastructure.md` |
| ADR | `docs/adr/ADR-<nnn>-<nombre>.md` | `docs/adr/ADR-001-local-first.md` |

---

## 6. Documentos que se actualizan en cada tarea

| Documento | Cuándo |
| --- | --- |
| [`STATUS.md`](STATUS.md) | Al iniciar, al quedar lista y al aprobarse. |
| [`ROADMAP.md`](ROADMAP.md) | Al cambiar el estado o el avance de una etapa. |
| `docs/tasks/TASK-<n>-*.md` | Durante la ejecución. |
| `docs/task-reports/TASK-<n>-report.md` | Al finalizar la ejecución. |
| `docs/adr/` | Cuando la tarea toma una decisión arquitectónica relevante. |
| Ficha de etapa | Cuando se completa la etapa. |

---

## 7. Principio de no duplicación

El roadmap, el estado y las decisiones viven **solo** en `personal-blog-infra`.
`personal-blog-frontend` y `personal-blog-backend` los **referencian**, no los copian.
