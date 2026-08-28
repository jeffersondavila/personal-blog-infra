# DEFINITION OF DONE — Definición de terminado

Define cuándo una tarea puede marcarse `Lista para validación` y cuándo puede
considerarse `Aprobada`.

---

## 1. Lista para validación

Una tarea **solo** puede marcarse `Lista para validación` cuando se cumplen **todos**
estos criterios:

| # | Criterio | Cómo se verifica |
| --- | --- | --- |
| 1 | **Cumple todo el alcance.** Cada elemento de *Dentro del alcance* está entregado. | Checklist de la ficha de tarea completo. |
| 2 | **No agrega funcionalidad fuera del alcance.** | Revisión de archivos modificados contra *Fuera del alcance*. |
| 3 | **El código compila cuando corresponde.** | `npm run build`, `python -m compileall`, `docker compose config`, `terraform validate`, según el caso. |
| 4 | **Las pruebas pasan cuando corresponde.** | Ejecución real de la suite; el resultado se registra tal cual, incluidos fallos. |
| 5 | **La documentación está actualizada.** | `STATUS.md`, `ROADMAP.md`, ficha de tarea, reporte y ADR si aplica. |
| 6 | **No contiene secretos.** | Búsqueda de patrones sensibles; ningún `.env` real, clave, token o credencial versionada. |
| 7 | **Incluye instrucciones para validar.** | Sección *Pasos de validación para el usuario*, reproducible. |
| 8 | **Registra decisiones importantes.** | Sección *Decisiones técnicas*; ADR si la decisión es estructural. |
| 9 | **Registra riesgos y deuda pendiente.** | Secciones *Riesgos* y *Deuda técnica pendiente*; riesgos vivos replicados en `STATUS.md`. |
| 10 | **No rompe tareas aprobadas anteriormente.** | Las validaciones de tareas previas siguen pasando. |
| 11 | **La rama Task nació de `main`.** | `git rev-parse HEAD` coincidía con `git rev-parse main` al crearla, y el SHA base queda registrado en la ficha. |
| 12 | **La documentación no persiste estado transitorio de Git o GitHub.** | Búsqueda dirigida en los documentos tocados: toda mención a un PR, una rama remota o una normalización es **historia fechada** o **regla permanente**, nunca estado vigente ni condición de la tarea siguiente. |

Si un criterio **no aplica** a la tarea, debe declararse explícitamente con su
justificación (por ejemplo: "criterio 4 no aplica: tarea exclusivamente documental").

> **Criterio 11 — higiene Git mínima.** La única base permitida de una rama `Task/*` es
> **`main`**; `dev` **nunca** lo es. Motivo y procedimiento completo:
> [`WORKFLOW.md`](WORKFLOW.md) §2.1. Aquí solo se comprueba el hecho, no se duplica el
> flujo.

> **Criterio 12 — estado duradero.** Un cierre se redacta **antes** de que el usuario
> fusione el PR, así que escribir el trámite en presente lo condena a ser falso. Regla
> completa, tabla duradero/transitorio y forma correcta de redactarlo:
> [`WORKFLOW.md`](WORKFLOW.md) §6.1. Aquí solo se comprueba el hecho, no se duplica la
> regla.

---

## 2. Aprobada

> Una tarea **solo puede considerarse aprobada cuando el usuario lo autoriza**.

- Claude **nunca** marca una tarea como `Aprobada`.
- La autorización se expresa así:

  ```
  approved: Task/<nombre-de-rama>
  ```

- Recibida la autorización, se ejecuta el flujo de cierre definido en
  [`WORKFLOW.md`](WORKFLOW.md), sección 3.
- Sin esa expresión no se hace commit, merge, push ni pull request.
- **Antes de crear el pull request** debe comprobarse que su **base es `main`** y su
  **head es exactamente la rama `Task/<...>`**. Nunca `dev → main`.

---

## 3. Definición de terminado por tipo de tarea

### Tareas documentales
- Todos los documentos declarados existen y son coherentes entre sí.
- Los enlaces relativos resuelven.
- No hay duplicación innecesaria entre repositorios.

### Tareas de backend
- `ruff` y `mypy` sin errores.
- `pytest` en verde.
- Migraciones aplican y revierten.
- La imagen Docker construye.
- Variables de entorno documentadas en `.env.example` con valores ficticios.
- **Cero warnings no documentados.** Si se tolera alguno, se registra con su causa y la
  tarea futura que lo resuelve.

#### Tareas de backend **funcional**

Además de lo anterior, toda tarea que introduzca **comportamiento funcional nuevo**
—dominio, casos de uso, API pública o administrativa, persistencia, autenticación,
autorización, auditoría o `ObjectStorage`— debe cumplir la práctica test-first definida en
[`BACKEND_TESTING_STRATEGY.md`](BACKEND_TESTING_STRATEGY.md):

| # | Criterio | Cómo se verifica |
| --- | --- | --- |
| B-1 | **Matriz de casos** construida antes de implementar. | Sección *TDD / Plan test-first* de la ficha, con la capa de cada caso. |
| B-2 | **Evidencia RED.** | Salida registrada en el reporte: el test falló **por la razón esperada** antes de la implementación. |
| B-3 | **Evidencia GREEN.** | El mismo test en verde tras la implementación mínima. |
| B-4 | **Refactor ejecutado o declarado innecesario.** | Registrado en el reporte, sin cambio de comportamiento observable. |
| B-5 | **Suite afectada en verde.** | Ejecución real de las pruebas del área tocada. |
| B-6 | **Integración correspondiente.** | PostgreSQL real cuando el comportamiento depende de PostgreSQL; MinIO cuando dependa del almacenamiento. Nunca SQLite como sustituto. |
| B-7 | **Regresión completa.** | La suite entera vuelve a ejecutarse antes de marcar `Lista para validación`. |
| B-8 | **Edge cases cubiertos.** | Presentes en la matriz y en la suite. |
| B-9 | **Casos negativos cubiertos.** | Entradas inválidas, recursos inexistentes, estados no permitidos. |
| B-10 | **Seguridad cuando aplique.** | No autenticado, sin permisos, contenido no publicado, ausencia de filtraciones. |
| B-11 | **Sin bug fix sin test de regresión.** | Todo defecto corregido deja su prueba permanentemente en la suite. |
| B-12 | **Los tests no se modificaron para acomodar la implementación.** | Cualquier cambio de expectativa está justificado por requisito, contradicción documentada, error demostrado o decisión registrada. |

Una tarea de backend funcional que no pueda demostrar **B-2** y **B-3** no está terminada:
sin evidencia de RED y GREEN no hay ciclo TDD, solo pruebas escritas a posteriori.

### Tareas de frontend
- Lint y type-check sin errores.
- Tests en verde.
- `build` de producción exitoso.
- Sin errores de consola en las rutas afectadas.

### Tareas de infraestructura local
- `docker compose config` válido.
- Los servicios levantan y sus healthchecks pasan.
- Los volúmenes persisten tras reinicio.
- Los servicios son visibles y sanos en Portainer.

### Tareas de infraestructura cloud

Actualizada en `Task/005.5`: la versión anterior era **anterior a ADR-006** y solo exigía
sintaxis y `plan`. Se aplica **lo que corresponda al destino de la tarea**; un criterio que
no aplique se declara con su razón.

| # | Criterio |
| --- | --- |
| C-1 | `terraform fmt -check` y `terraform validate` sin errores. |
| C-2 | **Destino explícito y verificado antes de actuar**: local o AWS real. Sin declaración, no se ejecuta. |
| C-3 | **Guardas *fail-closed*** operativas antes de cualquier `apply` o `destroy` ([security-boundaries](../architecture/security-boundaries.md) §8.2). |
| C-4 | `terraform plan` revisado y **sin cambios inesperados**. |
| C-5 | **Evidencia registrada distinguiendo emulación de validación real.** Lo observado en el laboratorio es *hipótesis*; solo AWS real *valida*. Prohibido el estado «paridad completa». |
| C-6 | **Matriz de paridad actualizada** cuando la tarea toque un recurso que figure en ella. |
| C-7 | **Estado de Terraform** en el backend acordado (**D-06**), sin dejarlo suelto. |
| C-8 | Ningún recurso creado sin **autorización explícita del usuario**. |
| C-9 | **Recursos realmente creados** enumerados y contrastados con lo planificado. |
| C-10 | **Impacto en costo** estimado y documentado, con precios vigentes. |
| C-11 | Ningún secreto versionado y **ninguna credencial cloud real usada contra el emulador**. |

> **C-5 es el criterio que no debe relajarse.** Es la defensa concreta contra **R-20**: un
> laboratorio en verde no demuestra que AWS funcionará.

### Tareas de CI
- El workflow se ejecuta y termina en verde.
- Ningún secreto expuesto en logs.
- El tiempo de ejecución es razonable y está documentado.

---

## 4. Qué invalida una tarea

Una tarea **no** está terminada si:

- Se implementó funcionalidad no solicitada.
- Se eliminó o sobrescribió contenido preexistente sin justificación documentada.
- Se ejecutaron commits, merges o pushes sin autorización.
- Se crearon recursos cloud sin autorización.
- Se versionaron secretos.
- Se marcó `Aprobada` sin la expresión `approved:` del usuario.
- Se avanzó a la siguiente tarea sin aprobación de la actual.
- **Se escribieron las pruebas después de la implementación** en una tarea de backend
  funcional, o no hay evidencia de RED.
- **Se modificó un test para que pasara** en lugar de corregir la implementación, sin
  justificación registrada ([`BACKEND_TESTING_STRATEGY.md`](BACKEND_TESTING_STRATEGY.md) §9).
