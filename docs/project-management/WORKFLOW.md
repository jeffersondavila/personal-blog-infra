# WORKFLOW — Proceso de trabajo

Define cómo se selecciona, ejecuta, valida, aprueba e integra cada tarea del proyecto.

> ## ⚠️ Invariante crítico de ramas
>
> **Toda rama `Task/<...>` nace SIEMPRE desde `main` actualizado y limpio.**
>
> **`dev` NUNCA es la rama base de una Task.** `dev` es exclusivamente rama de
> integración.
>
> Corregido el 2026-08-15 en `Task/005.4-Corregir-Base-Ramas-Task-Main`. Hasta esa fecha
> este documento indicaba `dev` como base, lo que era incorrecto: ver §2.1.

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

3. **Crear la rama Task desde `main`**
   ```
   git fetch --prune origin
   git switch main
   git pull --ff-only origin main

   # Validar ANTES de crear la rama
   git status --porcelain        # debe estar vacio
   git rev-parse main
   git rev-parse origin/main     # deben coincidir

   git switch -c Task/<numero>-<nombre>

   # Validar INMEDIATAMENTE despues
   git rev-parse HEAD
   git rev-parse main            # deben coincidir
   ```
   Si la tarea afecta a varios repositorios, se crea **la misma rama** en cada uno,
   **siempre desde `main`**.

   **Prohibido**, en cualquier forma equivalente:

   ```
   git switch dev
   git switch -c Task/<numero>-<nombre>     # ❌ NUNCA
   ```

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

12. **Ejecutar el flujo oficial de cierre**
    Solo entonces se ejecuta la secuencia completa de la sección 3. Claude se
    detiene de nuevo después de crear el PR y espera la revisión del usuario
    antes de sincronizar `main` y `dev`.

---

## 2.1 Ciclo oficial de ramas

```
A. INICIO
   origin/main
       ↓
   main actualizado y limpio
       ↓
   Task/<nombre>

B. DESARROLLO
   trabajo únicamente en Task/<nombre>

C. APROBACIÓN
   el usuario escribe:  approved: Task/<nombre>

D. CIERRE
   commit en Task/<nombre>

E. INTEGRACIÓN
   Task/<nombre> ──merge --no-ff──► dev
   push dev

F. PUBLICACIÓN
   push Task/<nombre>

G. PULL REQUEST
   Task/<nombre> ──► main

H. USUARIO
   revisa y fusiona el PR manualmente
   decide si elimina la rama remota

I. NORMALIZACIÓN
   fetch --prune
   main actualizado
   main ──merge --no-ff──► dev
   push dev

J. SIGUIENTE TASK
   main actualizado
       ↓
   Task/<siguiente>
```

**`dev` nunca es la rama base de una Task.**

### Por qué la base es `main` y no `dev`

`dev` contiene **commits de integración** —los merges de tareas anteriores y las
normalizaciones `main → dev`— que **no deben formar parte de la ascendencia de una tarea
nueva**.

Si una Task nace desde `dev`, el pull request `Task → main` puede **heredar historial
exclusivo de integración de `dev`**, ajeno a la tarea.

Crear cada Task desde `main` garantiza que:

- el pull request contiene **únicamente** la tarea correspondiente;
- la ascendencia del trabajo parte de la **rama estable**;
- `dev` conserva su función **exclusivamente integradora**;
- los commits de integración de `dev` **no contaminan** futuras Task.

> **Antecedente.** Hasta el 2026-08-15 este documento indicaba `dev` como base, y las
> tareas `Task/002` a `Task/005.3` se crearon así. **Su historial no se reescribe**: la
> corrección aplica hacia adelante, desde
> `Task/005.4-Corregir-Base-Ramas-Task-Main`, que es la primera creada desde `main`.

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

El flujo oficial completo, desde la preparación hasta la normalización final,
es el siguiente en cada repositorio afectado. Los pasos 1 a 4 ocurren antes de
la aprobación; el paso 5 desbloquea los pasos 6 a 12. Tras el paso 12, Claude
se detiene hasta que el usuario complete el paso 13:

1. **Actualizar `main`** con `fetch --prune` y `pull --ff-only`, y confirmar que
   `main == origin/main` y que el árbol está limpio.
2. **Crear `Task/<nombre>` desde `main`**, verificando que `HEAD == main` justo después.
3. **Implementar y validar** únicamente el alcance autorizado.
4. **Dejar la tarea `Lista para validación`** y detenerse.
5. **Recibir `approved: Task/<nombre>`** del usuario.
6. **Crear los commits pendientes** en la rama Task.
7. **Integrar `Task/<nombre>` dentro de `dev`**.
8. **Publicar `dev`**.
9. **Publicar la rama `Task/<nombre>`**.
10. **Crear el pull request `Task/<nombre> → main`**, con `main` como base y
    la rama Task exacta como head.
11. **Eliminar la rama Task local** desde otra rama con:

    ```text
    git branch -d Task/<nombre>
    ```

12. **Conservar la rama Task remota** mientras exista el pull request.
13. **Esperar a que el usuario revise y fusione el PR**. Claude se detiene en
    este punto y no fusiona hacia `main`.
14. **Permitir que el usuario decida** si elimina la rama Task remota desde
    GitHub.
15. **Ejecutar `git fetch --prune origin`** después de la confirmación del
    usuario.
16. **Actualizar `main`** con `git pull --ff-only origin main`.
17. **Integrar `main` dentro de `dev`** cuando sus historiales difieran.
18. **Publicar `dev`** después de la normalización.
19. **Confirmar que `main` y `dev` tienen el mismo contenido** y que los
    árboles de trabajo están limpios.
20. **Solo entonces iniciar la siguiente tarea**.

Restricciones:

- Está **prohibido** crear un PR `dev → main` como cierre ordinario de una tarea.
- El pull request debe usar exactamente la rama Task como head y `main` como base.
- **Solo el usuario puede fusionar hacia `main`.**
- Claude no debe ejecutar `gh pr merge`.
- La rama Task local se elimina con `git branch -d` después de publicar la rama
  y crear el PR.
- La rama Task remota se mantiene hasta la decisión del usuario.
- Después de la fusión del usuario, `main → dev` normaliza los historiales que
  difieran.
- Sin la expresión `approved:`, no se hace commit, merge, push ni PR.
- La aprobación es por tarea: aprobar una tarea no autoriza iniciar la siguiente.

> Este flujo entra en vigor a partir de `Task/002.1-Configurar-Claude-Code`.
> Las fichas y reportes de `Task/001` y `Task/002` conservan el flujo anterior
> como registro histórico; no son instrucciones vigentes.

---

## 4. Estrategia de ramas

| Rama | Propósito | Origen | Destino |
| --- | --- | --- | --- |
| `main` | Versión estable o liberable. **Única base permitida de las ramas Task.** | — | — |
| `dev` | **Solo integración** de tareas aprobadas y normalización posterior al PR. | `main` | Publicación directa; recibe Task y luego `main` |
| `Task/<numero>-<nombre>` | Trabajo aislado de una tarea. | **`main`** | merge → `dev` y PR → `main` |

Reglas:

- **`main` es la única rama base para crear `Task/*`.**
- **`dev` NUNCA es base de una Task.** `dev` es exclusivamente rama de integración.
- Nunca se implementa el trabajo de una tarea directamente sobre `main` ni
  sobre `dev`; solo se realizan las operaciones de integración y
  normalización definidas en este workflow.
- Una tarea que afecta a varios repositorios usa **el mismo nombre de rama** en todos, y
  **todas nacen de `main`**.
- No se reescribe historial publicado (`rebase`/`push --force` sobre ramas compartidas).
- `dev` nunca es el head obligatorio ni el head ordinario del PR de cierre.
- El PR de cierre siempre usa `Task/<numero>-<nombre>` como head y `main` como
  base.
- Una tarea aprobada **se integra en `dev`**; el PR sale **directamente de la rama Task
  hacia `main`**. Nunca se crea un PR `dev → main`.
- Tras la fusión manual del usuario, **`main` se integra de nuevo en `dev`** para
  normalizar, y la siguiente Task vuelve a nacer de `main`.

### Estado actual de las ramas

El estado real y vigente de las ramas se registra en [`STATUS.md`](STATUS.md).
Debe verificarse con Git antes de iniciar o cerrar cualquier tarea.

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
