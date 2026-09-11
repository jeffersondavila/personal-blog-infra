# TASK-020.2 — Corregir la autodescripción obsoleta de Task020.1

| Campo | Valor |
| --- | --- |
| **Identificador / rama** | `Task/020.2-Corregir-Autodescripcion-Obsoleta-de-Task020.1` |
| **Tipo** | Mantenimiento documental; no cuenta dentro de las 41 tareas |
| **Etapa** | Asociada a ETAPA 06; no altera su avance |
| **Estado** | **Aprobada** ✔ el 2026-09-10 por el usuario |
| **Expresión de aprobación** | `approved: Task/020.2-Corregir-Autodescripcion-Obsoleta-de-Task020.1` |
| **Repositorio** | `personal-blog-infra` únicamente |
| **Dependencias** | `Task/020` y `Task/020.1`, ambas **Aprobadas** |
| **Rama base** | `main` |
| **SHA base al crear la rama el 2026-09-10** | `ebd64284fcbc8edf66fb89353eaf0eaaa8a5b97d` |
| **Inicio / última actualización** | 2026-09-10 (Guatemala) |
| **Reporte** | [TASK-020.2-report.md](../task-reports/TASK-020.2-report.md) |

## 0. Preparación Git

Durante el preflight del 2026-09-10 se ejecutaron `fetch --prune`, `switch main`
y `pull --ff-only`. Se verificaron limpieza, staging vacío e igualdad con
`origin/main`, además de ausencia de la rama exacta local/remota y de PR previo
con ese head. La rama nació desde `main`, en el SHA base registrado arriba;
se comprobó inmediatamente la igualdad con esa base y la ausencia de commits
adicionales. Es evidencia de creación, conforme a [WORKFLOW §2.1](../project-management/WORKFLOW.md).

## 1. Objetivo

Corregir una celda del reporte de `Task/020.1` para que describa el registro
pre-aprobación y su posterior promoción documental durante el cierre.

## 2. Contexto

La tabla describía solo la fase inicial del cambio en STATUS, aunque STATUS
ya registraba `Task/020.1` como **Aprobada** y último mantenimiento aprobado.
Es el único residual **D** autorizado: contradicción documental no-Git.
La reproducción exacta y su causa constan en el reporte, apartados B y C.

## 3. Dentro del alcance

- [x] Reproducir y corregir esa celda, conservando ambos momentos históricos.
- [x] Crear ficha y reporte; registrar la maintenance en STATUS e índice.
- [x] Validar referencias, secretos, diff y coherencia mediante Criterion 12.

## 4. Fuera del alcance

Backend, frontend, Docker, CI, Terraform, ADR y cambios funcionales. ROADMAP,
STAGE-06, ficha y reporte de `Task/020` quedan fuera de edición. Una
contradicción independiente obliga a detener la tarea. `Task/021` no se inicia.

## 5. Entregables

Una corrección semántica y cuatro documentos de gobierno, enumerados en el
[reporte, apartado E](../task-reports/TASK-020.2-report.md#e-archivos-tocados).

## 6. Criterios de aceptación

Historia conservada, STATUS y reporte coherentes; **C = 0 · D = 0**; referencias
rotas y secretos **0**; diff sin errores; cinco archivos bajo `infra/docs/`.
Avance **20/41 — 49 %**, ETAPA 06 **2/3 — 67 %**; ambas tareas precedentes
**Aprobadas** y `Task/021` **Pendiente**. La entrega de la fase pre-aprobación
del 2026-09-10 quedó **Lista para validación**, con staging y `main..HEAD` en
**0**; todos los criterios se cumplieron antes de la aprobación.

## 7. TDD / Plan test-first

No aplica: cambio exclusivamente documental, sin comportamiento funcional.
Los apartados de comportamientos, matriz, RED, integración, casos negativos y
regresiones funcionales no aplican por el mismo motivo.

## 8. Plan de validación

Inspeccionar el cambio contra la celda original; contrastar STATUS; resolver
referencias relativas en los cinco documentos; buscar patrones de secretos;
revisar las menciones transitorias según [WORKFLOW §6.1](../project-management/WORKFLOW.md)
y comprobar alcance, contadores y límites Git antes de presentar el resultado.

## 9. Comandos de validación

Desde la raíz de `personal-blog-infra`, los comandos reproducibles figuran en
el [reporte, apartado H](../task-reports/TASK-020.2-report.md#h-validación-documental).
Consultan el estado operativo cuando se ejecutan; no lo fijan en documentos.

## 10. Evidencia esperada

Reproducción y corrección literales, controles documentales sin hallazgos y
evidencia del preflight. Resultados medidos en el reporte, apartados A–J.

## 11. Riesgos

Repetir la autodescripción incompleta durante el cierre. Mitigación: revisar
las referencias de esta maintenance y promover su estado documental antes
del commit autorizado, conservando solo hechos durables. Ningún riesgo nuevo.

## 12. Decisiones técnicas

No aplica: corrección de redacción, sin decisión arquitectónica ni ADR.

## 13. Documentación creada o actualizada

El [reporte, apartado E](../task-reports/TASK-020.2-report.md#e-archivos-tocados)
es la enumeración de las cinco rutas y su propósito.

## 14. Archivos modificados

Tres modificados y dos creados, todos documentales y enumerados en E.

## 15. Resultado de pruebas

Validación pre-aprobación del 2026-09-10: **215 referencias, 0 rotas**;
**0 secretos**; diff sin errores; **C = 0 · D = 0**. Desglose en G–H del reporte.
Compilación y pruebas funcionales no aplican (DoD 3 y 4): solo Markdown.

## 16. Problemas encontrados

Un conteo de PowerShell interpretó el JSON vacío de PR como un elemento;
se detuvo la creación y se corrigió el conteo antes de continuar. Detalle en A.

## 17. Pasos de validación para el usuario

Leer B–F del reporte y ejecutar los comandos de H desde la raíz de infra.
Contrastar después el resultado de Criterion 12 y los contadores de J.

## 18. Deuda técnica pendiente

Ninguna nueva. El residual autorizado se limita a esta autodescripción.

## 19. Próxima tarea

`Task/021-CI-Infraestructura`: **Pendiente y no iniciada**. Su inicio requiere
una instrucción posterior y el preflight que establece WORKFLOW.

## 20. Aprobación

**Aprobada** el 2026-09-10 por el usuario mediante la expresión exacta
`approved: Task/020.2-Corregir-Autodescripcion-Obsoleta-de-Task020.1`.

La entrega de la fase pre-aprobación del 2026-09-10 se había preparado sin
aprobación del usuario, conforme a la regla de cierre. Recibida la expresión,
y **antes del commit**, se promovieron a **Aprobada** ficha, reporte, STATUS e
índice, y se revisó que cada descripción correspondiera al cambio completo,
incluida la autodescripción de esta propia tarea: el defecto que corrige.
Los hechos pre-aprobación se conservan como historia fechada.

El estado operativo —PR, ramas remotas, sincronía de `main` y `dev`— se consulta
en Git y GitHub, no en este documento. La normalización posterior a la fusión
del pull request es **Git-only**, sin cambios documentales.
