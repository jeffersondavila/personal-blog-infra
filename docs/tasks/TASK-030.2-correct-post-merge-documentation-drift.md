# TASK-030.2 — Corregir drift documental post-merge

| Campo | Valor |
| --- | --- |
| **Identificador** | Task/030.2 |
| **Nombre** | Corregir drift documental post-merge |
| **Etapa** | Mantenimiento documental, **fuera de las 41 tareas** |
| **Estado** | **Aprobada** — 2026-10-01; enmienda previa al merge **H-030.2-CI-Alpine-repair** (§21), **aprobada** el 2026-10-01 |
| **Repositorio modificado** | `personal-blog-infra` |
| **Dependencias** | Task/030 Aprobada; resultado final disponible para contrastar |
| **Base** | `main` actualizado y limpio, conforme a WORKFLOW §2.1 |
| **Fecha de inicio / actualización** | 2026-10-01 |

## 0. Preparación Git

Verificado el invariante de [WORKFLOW §2.1](../project-management/WORKFLOW.md):
base limpia y actualizada, coincidencia con su origen y creación desde `main`.
La evidencia operacional se entrega en la sesión; no se incorporan hashes ni estado
transitorio de ramas o PR a esta ficha, por el alcance expreso y WORKFLOW §6.1.

## 1. Objetivo

Hacer que la documentación durable refleje el resultado final de Task/030 sin reabrirla
ni alterar las afirmaciones correctas de sus checkpoints históricos.

## 2. Contexto

El inventario final del backend abarca DEF-030-1, CI MinIO/GHCR y urllib3 2.8.0:
**6 archivos, +222 / −14**. Parte del resumen seguía describiendo únicamente DEF-030-1.
Faltaban además el origen actual de MinIO y el seguimiento explícito de la excepción
temporal de índice de urllib3.

## 3. Dentro del alcance

- [x] Reconciliar ficha y reporte de Task/030 con el entregable final.
- [x] Documentar MinIO/GHCR actual en STAGE-06 y NFR, preservando la historia de Quay.
- [x] Registrar DT-030-URLLIB3 abierta, con propietario y criterio de retiro.
- [x] Corregir únicamente la fila canónica de Task/029 a **Aprobada (2026-09-27)**,
  bajo la ampliación acotada **H-030.2-counter-fix**.
- [x] Completar los gates documentales y verificar los contadores.

## 4. Fuera del alcance

Backend funcional, frontend, AWS, Terraform apply, cambios de dependencias, scripts,
locks y CI funcional. Task/030 no se reabre y Task/031 no se inicia. La enmienda de §21
es la única excepción, autorizada después de la aprobación y acotada a dos Dockerfiles.

## 5. Entregables

Documentación reconciliada y trazabilidad del mantenimiento en los ocho archivos
enumerados en el [reporte](../task-reports/TASK-030.2-report.md).

## 6. Criterios de aceptación

1. Inventario final de seis archivos, separado de los checkpoints de dos archivos.
2. STAGE-06 y NFR describen GHCR privado, `GHCR_MINIO_READ_TOKEN`, runner `linux/amd64`,
   manifiesto amd64 del índice original, misma release y mismos bytes ejecutados.
3. Deuda urllib3 explícita: fecha global congelada, dos opciones por paquete y retiro
   condicionado a resolución compatible y reproducible sin excepción.
4. Gates en verde; avance **30/41 ≈ 73 %**, ETAPA 10 **1/7 ≈ 14 %**, Task/031 Pendiente.
5. Tabla canónica: Task/001–Task/030 aprobadas y Task/031–Task/041 pendientes,
   **30 aprobadas + 11 pendientes = 41**, sin modificar checkpoints históricos de Task/029.

## 7. TDD / Plan test-first

No aplica: mantenimiento exclusivamente documental, sin comportamiento nuevo.

## 8. Plan de validación

Contrastar contra el entregable del backend en solo lectura; revisar el diff documental;
validar enlaces Markdown y anclas, whitespace, secretos, Account IDs y contadores reales.
Verificar que solo cambia Markdown en infra y que backend/frontend siguen limpios.

## 9. Comandos de validación

Desde la raíz de infra, el gate temporal local, sin dependencias nuevas, comprueba enlaces,
historia, alcance, contadores y Account IDs, y exporta los archivos entregables para Gitleaks:

```powershell
python tmp/task0302/validate.py
git diff --check
git diff --stat
git status --short --branch
```

Invocación del escáner desde la raíz de la exportación, con el binario local ya disponible:

```text
gitleaks dir . --config .gitleaks.toml --redact=100 --no-banner
```

## 10. Evidencia esperada

Cero enlaces rotos, cero hallazgos de secretos y Account ID real, diff limpio,
contadores sin cambios y preservación de los checkpoints históricos. Resultados en el reporte.

## 11. Riesgos

Confundir un checkpoint con el entregable final: se conserva el cuerpo de §§25–27 y se
delimita el primer cierre histórico de §28. La excepción de urllib3 sigue abierta hasta
cumplir su criterio de retiro; documentarla no la elimina.

## 12. Decisiones técnicas

Ningún ADR ni cambio de arquitectura. Se documenta el resultado existente y se centraliza
el criterio de retiro en [NFR §7.1](../architecture/non-functional-requirements.md#71-deuda-viva-dt-030-urllib3).

## 13. Documentación creada o actualizada

Task/030, su reporte, STAGE-06, NFR, STATUS y ROADMAP; ficha y reporte de este mantenimiento.

## 14. Archivos modificados

Inventario completo en [reporte §4](../task-reports/TASK-030.2-report.md#4-archivos-del-entregable).
STAGE-10 solo se verifica; no necesita cambios. La enmienda de §21 añade
`docker/postgres/Dockerfile` y `docker/traefik/Dockerfile`
([reporte §7](../task-reports/TASK-030.2-report.md#7-enmienda-h-0302-ci-alpine-repair)).

## 15. Resultado de pruebas

Todos los gates repetidos tras la corrección, **PASS**: enlaces, whitespace, Gitleaks
del entregable e historial, Account-ID scan, preservación histórica, alcance y contadores.
**30 aprobadas, 11 pendientes, total 41; ETAPA 10 1/7; Task/031 Pendiente, no iniciada.**
Compilación, suites funcionales, Terraform y ejecuciones de CI no aplican: no hay cambios
de implementación o configuración. Detalle en el reporte.

## 16. Problemas encontrados

Además de las tres lagunas de §2, el gate de contadores detectó que la tabla completa de
STATUS conservaba Task/029 como «Pendiente», pese a su aprobación registrada del 2026-09-27.
El usuario autorizó **H-030.2-counter-fix**: se corrigió exclusivamente esa fila canónica
a **Aprobada (2026-09-27)**. Los checkpoints históricos de Task/029 se preservan; Task/029
y Task/029.1 no se reabren. D-10, D-12, D-22, D-23, D-24, EX-029-D13 y R-47 no cambian.

## 17. Pasos de validación para el usuario

Revisar el inventario final en Task/030 §14 y reporte §28; contrastar las secciones actuales
de STAGE-06/NFR y el criterio de retiro NFR §7.1. Revisar el diff y ejecutar §9.
Confirmar los contadores de STATUS/ROADMAP/STAGE-10 y Task/031 Pendiente, no iniciada.

## 18. Deuda técnica pendiente

**DT-030-URLLIB3 abierta**, propiedad del mantenimiento de dependencias del backend:
retirar la excepción cuando la fecha global admita urllib3 ≥2.8.0 compatible y se cumplan
la reproducibilidad de ambos locks y los gates existentes. No se programa su ejecución aquí.

## 19. Próxima tarea

Task/031 sigue **Pendiente, no iniciada**. Este mantenimiento no autoriza iniciarla ni
altera el avance de las 41 tareas.

## 20. Aprobación

**Aprobada por el usuario el 2026-10-01**, mediante la expresión exacta
`approved: Task/030.2-Corregir-Drift-Documental-Post-Merge`, conforme a
[WORKFLOW §3](../project-management/WORKFLOW.md). La aprobación mantiene el carácter
documental del mantenimiento y no autoriza iniciar Task/031.

## 21. Enmienda post-aprobación H-030.2-CI-Alpine-repair

Tras la aprobación y antes del merge, CI Infra falló en el PR al construir la imagen de
PostgreSQL: el pin exacto `libcrypto3`/`libssl3` **3.5.8-r0** ya no era seleccionable en el
índice de Alpine v3.24, que avanzó a **3.5.9-r0** por una actualización de seguridad. El
workflow, ambos Dockerfiles y `.env.example` —todo lo que interviene en ese build— eran
idénticos en `main`: deriva externa, no regresión del cambio documental.

Autorización: `authorize: Task/030.2 H-030.2-CI-Alpine-repair`, en la misma rama y el mismo
PR, limitada a restaurar la reproducibilidad de las imágenes de PostgreSQL y Traefik.

- [x] Comparar con evidencia conservar 3.5.8-r0 frente a adoptar 3.5.9-r0.
- [x] Actualizar el pin en `docker/postgres/Dockerfile` y `docker/traefik/Dockerfile`.
- [x] Builds reales sin caché, versiones dentro de las imágenes, arranque endurecido y S-09.
- [x] Repetir los gates infra completos y el gate documental.
- [x] Registro durable en NFR, STATUS, ROADMAP, esta ficha y el reporte.

Fuera de la enmienda: AWS, Terraform apply, backend, frontend, MinIO, workflow, baseline,
`.env.example` y scripts. Comparación y resultados en el
[reporte §7](../task-reports/TASK-030.2-report.md#7-enmienda-h-0302-ci-alpine-repair).
La aprobación de §20 se conserva; la enmienda no la sustituye ni inicia Task/031.

**Enmienda aprobada por el usuario el 2026-10-01**, con CI Infra en verde, mediante una
nueva expresión exacta `approved: Task/030.2-Corregir-Drift-Documental-Post-Merge` sobre
el entregable enmendado.
