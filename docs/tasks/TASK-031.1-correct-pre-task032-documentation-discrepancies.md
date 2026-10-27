# TASK-031.1 — Corregir discrepancias documentales previas a Task/032

| Campo | Valor |
| --- | --- |
| **Identificador** | Task/031.1 |
| **Nombre** | Corregir discrepancias documentales previas a Task/032 |
| **Etapa** | Mantenimiento documental, **fuera de las 41 tareas** |
| **Estado** | **Lista para validación** — 2026-10-27 |
| **Repositorio modificado** | `personal-blog-infra` |
| **Dependencias** | Task/031 Aprobada; auditoría posterior a su fusión y a la normalización `main → dev` |
| **Base** | `main` actualizado y limpio, conforme a WORKFLOW §2.1 |
| **Fecha de inicio / actualización** | 2026-10-27 *(UTC, como el cierre de Task/031; en America/Guatemala, la noche del 2026-10-26)* |

## 0. Preparación Git

Verificado el invariante de [WORKFLOW §2.1](../project-management/WORKFLOW.md):
base limpia y actualizada, coincidencia con su origen y creación desde `main`.
La evidencia operacional se entrega en la sesión; no se incorporan hashes ni estado
transitorio de ramas o PR a esta ficha, conforme a WORKFLOW §6.1.

## 1. Objetivo

Que la documentación vigente describa el estado aprobado antes de iniciar Task/032, sin
reabrir Task/031, sin cambiar decisiones y sin reescribir la historia.

## 2. Contexto

Tras la fusión de Task/031, el usuario pidió una auditoría documental completa antes de
Task/032 y autorizó esta tarea solo si encontraba discrepancias reales. La auditoría
contrastó README, CONTRIBUTING, la gestión del proyecto, la arquitectura, los runbooks,
los ADR, las etapas, las fichas, `docs/claude`, el producto, `.env.example`, los
workflows y el laboratorio con Git, el código y los registros vigentes.

Encontró **nueve discrepancias verificadas** (H1–H9): textos que presentan como actual un
estado que el estado aprobado contradice. Ninguna es un defecto técnico. El código, la
infraestructura y las políticas de seguridad son correctos; lo desfasado es su descripción.

## 3. Dentro del alcance

- [x] **H1:** PROJECT_INSTRUCTIONS §16, regla 10, daba Task/029 por Pendiente.
- [x] **H2:** STATUS y el reporte de Task/031 §53.6 afirmaban como vigente el estado de su PR.
- [x] **H3:** el runbook de recuperación citaba tolerancias del laboratorio ya superadas.
- [x] **H4:** la matriz de paridad describía en presente el comportamiento de Floci 2.1.0.
- [x] **H5:** la fila R-018-3 de STATUS contaba 99 identidades aceptadas de MinIO, no 10.
- [x] **H6:** el comentario de MinIO en `.env.example` describía la identidad de Task/028.
- [x] **H7:** dos comentarios de `ci-infra.yml`, sobre el verificador de MinIO y sobre Floci.
- [x] **H8:** el comentario de `terraform-datos/variables.tf` sobre el formato de ID de zona.
- [x] **H9:** la arquitectura objetivo §14 daba por abiertas decisiones que Task/029 resolvió.
- [x] Registro en ROADMAP y STATUS, ficha, reporte, gates documentales y gates afectadas.

## 4. Fuera del alcance

AWS; Terraform apply, destroy y refresh-only; PITR; reconstruir o republicar MinIO; el
baseline S-09; excepciones de seguridad; listas cerradas y guardas del laboratorio; lógica
de CI; código funcional, backend y frontend. Task/031 no se reabre y Task/032 no se
inicia. Lo que no es una contradicción queda registrado sin corregir en el
[reporte §7](../task-reports/TASK-031.1-report.md#7-observaciones-no-corregidas).

## 5. Entregables

Las correcciones de H1–H9, un complemento fechado en el reporte de Task/031 y otro en el
runbook de recuperación, esta ficha, su [reporte](../task-reports/TASK-031.1-report.md)
y el registro en STATUS y ROADMAP.

## 6. Criterios de aceptación

1. Cada corrección cita la fuente aprobada que la respalda y no afirma ningún estado nuevo.
2. Historia intacta: el punto 4 de §53.6 y la nota de H-031-1A del runbook se conservan
   palabra por palabra, con un complemento fechado a continuación.
3. En `.env.example`, `ci-infra.yml` y `variables.tf` solo cambian comentarios: ningún
   valor, paso, versión ni validación.
4. Gates en verde: enlaces y anclas, whitespace, LF sin BOM, Gitleaks, valores privados y
   las gates de CI que leen los tres archivos no Markdown.
5. Avance sin cambios: **31/41 ≈ 76 %**, ETAPA 10 **2/7 ≈ 29 %**; **Task/032 Pendiente, no
   iniciada**.

## 7. TDD / Plan test-first

No aplica: mantenimiento documental sin comportamiento nuevo. Los tres archivos no
Markdown solo cambian comentarios, y las suites que los leen se ejecutan igualmente.

## 8. Plan de validación

Contrastar cada hallazgo con su fuente y revisar el diff palabra por palabra. Validar
enlaces y anclas, whitespace, finales de línea, secretos, ID de cuenta y valores privados.
Repetir offline las gates de CI que leen los archivos tocados. Verificar que backend y
frontend siguen limpios y que `terraform-datos/backend.generado.tf` se conserva.

## 9. Comandos de validación

Desde la raíz de infra, con los auxiliares locales ignorados por Git:

```powershell
python -B tmp/h0320/enlaces.py <archivos Markdown modificados>
python -B tmp/t0311/gates/gates.py
git diff --check
git diff --cached --check
```

Secretos: la invocación de CI sobre el historial y el escaneo del entregable exportado,
desde su raíz:

```text
gitleaks git . --log-opts="--all" --redact=100 --no-banner
gitleaks dir . --config .gitleaks.toml --redact=100 --no-banner
```

## 10. Evidencia esperada

Cero enlaces rotos, gates con exit 0, cero hallazgos de secretos y ningún valor privado
nuevo. El diff se limita al inventario y los contadores no cambian. Resultados en el
[reporte §8](../task-reports/TASK-031.1-report.md#8-gates-y-validaciones).

## 11. Riesgos

- **Corregir historia como si fuera estado.** Se evita con complementos fechados y con
  WORKFLOW §6.1.
- **Fechas.** Este mantenimiento usa UTC, como el cierre de Task/031. El reporte lo indica
  donde la hora local daría otro día.
- **Ampliar el alcance.** Solo se corrigen contradicciones verificadas. Lo incompleto o
  histórico queda como observación.

## 12. Decisiones técnicas

Ningún ADR ni decisión cambia. No se modifica ningún control, lista cerrada, baseline ni
excepción.

## 13. Documentación creada o actualizada

PROJECT_INSTRUCTIONS, STATUS, ROADMAP, el reporte de Task/031, el runbook de recuperación,
la matriz de paridad y la arquitectura objetivo. Además, la ficha y el reporte de este
mantenimiento.

## 14. Archivos modificados

Inventario completo en el [reporte §5](../task-reports/TASK-031.1-report.md#5-archivos-y-diffs).

## 15. Resultado de pruebas

Resultado detallado en el [reporte §8](../task-reports/TASK-031.1-report.md#8-gates-y-validaciones).

## 16. Problemas encontrados

La auditoría inicial identificó ocho discrepancias. Un barrido dirigido de afirmaciones en
presente sobre Task/029–Task/031 encontró la novena (H9). Antes del commit, la verificación
de las propias correcciones detectó una frase inexacta en el complemento del runbook: el
ciclo no imprime las listas declaradas, sino lo observado, ya juzgado contra ellas. Se
corrigió.

## 17. Pasos de validación para el usuario

1. Revisar en el reporte cada hallazgo con su fuente y su diff.
2. Comprobar que los comentarios de `.env.example`, `ci-infra.yml` y `variables.tf` no
   alteran ningún valor.
3. Ejecutar los comandos de §9.
4. Confirmar que el avance sigue en 31/41 y que Task/032 sigue Pendiente, no iniciada.

## 18. Deuda técnica pendiente

Ninguna nueva. Las observaciones del reporte §7 no son deuda: son historia fechada o
descripciones incompletas que no contradicen el estado aprobado.

## 19. Próxima tarea

Task/032 sigue **Pendiente, no iniciada**. Este mantenimiento no la inicia ni altera el
avance de las 41 tareas. Lo que hereda está en el
[reporte §10](../task-reports/TASK-031.1-report.md#10-herencias-para-task032).

## 20. Aprobación

**Pendiente.** Solo el usuario puede aprobar este mantenimiento, mediante la expresión
exacta `approved: Task/031.1-Corregir-Discrepancias-Documentales-Pre-Task032`, conforme a
[WORKFLOW §3](../project-management/WORKFLOW.md).
