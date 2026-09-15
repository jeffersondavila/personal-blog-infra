# TASK-026 — Runbooks de despliegue

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/026-Runbooks-de-Despliegue` |
| **Etapa** | ETAPA 08 — Preparación Cloud + AWS Local Parity |
| **Estado** | **Aprobada** el 2026-09-15 mediante `approved: Task/026-Runbooks-de-Despliegue` |
| **Repositorio modificado** | `personal-blog-infra` |
| **Repositorios en solo lectura** | `personal-blog-backend`, `personal-blog-frontend` |
| **Dependencias** | `Task/024` ✔ · `Task/025` ✔ |
| **Rama** | `Task/026-Runbooks-de-Despliegue` |
| **Rama base** | `main` — nunca `dev` |
| **SHA base** | `940a531827602ae04db37ddc5b15b5722500cc37` |
| **Fecha de inicio** | 2026-09-15 |

> **Aprobada el 2026-09-15.** Las decisiones **D-026-A** a **D-026-J** pasan a
> **Aceptadas y Vigentes**, sin ADR nuevo, y los cinco runbooks pasan a **Vigentes**. Con
> esta aprobación la **ETAPA 08 queda Completada** (4/4, 100 %) y el avance global pasa a
> **26/41 ≈ 63 %**. **La aprobación no autoriza AWS real:** el modo `production` sigue
> bloqueado y lo observado en Floci sigue siendo hipótesis hasta la ETAPA 10.

---

## 0. Preparación Git demostrada

Antes de la primera mutación se repitió el checkpoint físico:

| Repositorio | `main == origin/main` | Árbol | Ramas `Task/*` |
| --- | --- | --- | --- |
| infra | `940a531827602ae04db37ddc5b15b5722500cc37` | limpio | 0 |
| backend | `4a40364bbd6a444f9469b815d17d2d77a37949ce` | limpio | 0 |
| frontend | `7dce98aff239d61ae3ae15213d9a3f5ebf0fb8ce` | limpio | 0 |

No había contenedores, redes ni volúmenes del laboratorio por nombre de proyecto ni por
la etiqueta `floci=true`. Después de `fetch --prune`, `switch main` y
`pull --ff-only`, la rama de esta tarea se creó **sólo en infra** y
`HEAD == main == 940a5318…`.

## 1. Objetivo

Convertir el laboratorio y el Terraform portable de Task/025 en procedimientos de
operación concretos: crear, validar, revertir, destruir y recuperar, con destino
demostrado antes de actuar, revisión humana de planes, inspección por API y AWS SDK,
drift controlado y transición futura —no ejecutada— hacia AWS real.

## 2. Alcance

### Dentro

- Cinco runbooks separados y un índice actualizado.
- Arranque y retirada limpia del laboratorio.
- `init`, `plan`, revisión humana, `apply`, inventario y camino crítico.
- Rollback desde un `ref` Git anterior aprobado y un artefacto recién reconstruido.
- `plan -destroy`, aprobación humana, vaciado controlado del bucket, destrucción y
  ausencia consultada contra las APIs.
- Recuperación desde ausencia total o `apply` parcial con estado conservado.
- Drift controlado sobre un único SSM ficticio y reconciliación estrecha.
- Diagnóstico y criterio de salida cuando Floci no tiene paridad.
- Preparación documental para AWS real, sin habilitar el modo `production`.

### Fuera

- Cuentas, credenciales, recursos o costos AWS reales.
- El bucket S3 de estado: no existe y requiere un bootstrap posterior separado.
- Automatización CI/CD de `plan`, `apply` o `destroy`.
- Cambios de producto en backend o frontend.
- Otro grafo Terraform o excepciones locales dentro de los módulos compartidos.
- Rollback de base de datos: el laboratorio no tiene DB y no existe un mecanismo
  aprobado que pueda documentarse honestamente.

## 3. Fuentes de verdad

- ADR-003 y ADR-006.
- Stage 08 y `aws-local-parity.md`.
- Ficha, manifiesto y reporte de Task/024.
- Terraform, matriz de paridad, guardas, resultados y excepciones aprobadas de Task/025.
- `security-boundaries.md`, NFR, Definition of Done y D-06.

## 4. Contradicciones heredadas y contención

| Hallazgo | Tratamiento en Task/026 |
| --- | --- |
| El CLI asignaba `local` por omisión aunque G-01 exige destino explícito | Corregir con RED→GREEN: `--modo` obligatorio |
| La prueba de red no enumeraba todos los bindings efectivos de Floci | Exigir exactamente `4566/tcp → 127.0.0.1:<puerto>` |
| Ficha/reporte históricos de Task/025 mezclan estados previo y posterior a aprobación | No reabrirlos ni reescribirlos |
| `STATUS`, `ROADMAP` y Stage 08 conservan valores vivos obsoletos | Corregir sólo esos documentos vivos |

No hay una decisión arquitectónica nueva: las dos correcciones de código hacen cumplir
controles ya aprobados.

## 5. Decisiones

| ID | Decisión | Estado |
| --- | --- | --- |
| D-026-A | Toda invocación declara `--modo`; no existe valor por omisión | **Aceptada y Vigente** |
| D-026-B | El binding efectivo de Floci es una lista cerrada de un único elemento en `127.0.0.1` | **Aceptada y Vigente** |
| D-026-C | `init`, `plan`, `apply` y `destroy` revalidan automáticamente destino, binding e identidad | **Aceptada y Vigente** |
| D-026-D | Una operación humana aplica sólo después de escribir `APLICAR <sha256 completo del plan>` | **Aceptada y Vigente** |
| D-026-E | No existe `--force` ni confirmación abreviada | **Aceptada y Vigente** |
| D-026-F | El SDK oficial se extrae temporalmente desde el ZIP canónico para que `botocore` lea sus datos; no se instala ni se hereda del host | **Aceptada y Vigente** |
| D-026-G | El drift controlado elimina sólo `/blog-lab/local/storage_region` y sólo localmente | **Aceptada y Vigente** |
| D-026-H | Rollback significa reconstruir un `ref` aprobado; no reutilizar un ZIP histórico sin procedencia | **Aceptada y Vigente** |
| D-026-I | Si Floci no tiene paridad, se registra la diferencia; no se deforma el Terraform compartido | **Aceptada y Vigente** |
| D-026-J | El modo `production` permanece bloqueado hasta bootstrap, credenciales efímeras y autorización futura | **Aceptada y Vigente** |

## 6. Entregables

| Entregable | Ruta |
| --- | --- |
| Crear | `docs/runbooks/deployment-create.md` |
| Validar | `docs/runbooks/deployment-validate.md` |
| Rollback | `docs/runbooks/deployment-rollback.md` |
| Destruir | `docs/runbooks/deployment-destroy.md` |
| Recuperar | `docs/runbooks/deployment-recovery.md` |
| Guardas y operaciones | `scripts/laboratorio/laboratorio.py` |
| Drift/API | `scripts/laboratorio/inventario.py`, `verificacion.py` |
| Regresiones | `tests/laboratorio/` |
| Evidencia | `docs/task-reports/TASK-026-report.md` |

## 7. Matriz de validabilidad

| Capacidad | Laboratorio | AWS real |
| --- | --- | --- |
| Sintaxis, plan, apply y destroy | Sí | Pendiente Stage 10 |
| Inventario con APIs y `boto3` | Sí, contra loopback | Pendiente |
| API Gateway v2 → Lambda → handler | Sí, hipótesis local | Autoridad pendiente |
| Privacidad S3 e IAM efectivo | No; Floci no aplica esas políticas | Sólo AWS |
| Cifrado real de SecureString | No | Sólo AWS |
| Alarmas, cuotas, latencia y costos | No | Sólo AWS |
| Backend remoto S3 | No existe | Bootstrap futuro |

## 8. Riesgos controlados

- **R-23:** binding efectivo, no sólo configuración declarada.
- **R-24:** modo explícito, endpoint cerrado, identidad `000000000000`, allowlist de
  entorno y repetición antes de Terraform.
- **R-20/R-27/R-28:** el reporte distingue hipótesis Floci de evidencia AWS.
- **R-22:** el socket Docker sigue siendo privilegio de host y el laboratorio se retira
  al finalizar.
- **R-35:** planes revisados, confirmación por digest y condiciones de aborto.

## 9. Criterios de aceptación

- [x] Existen cinco runbooks concretos y copiables.
- [x] `--modo` es obligatorio y `production` continúa rechazado.
- [x] Floci aborta ante cualquier binding que no sea el loopback exacto.
- [x] Las guardas se ejecutan antes de toda operación Terraform protegida.
- [x] Los planes humanos exigen el SHA-256 completo y no existe fuerza.
- [x] Inventario por cliente SigV4 y por `boto3` del artefacto.
- [x] Drift controlado observado y reconciliado sin cambios colaterales.
- [x] CREATE → VALIDATE → DESTROY → ABSENCE → RECOVER/REPEAT ejecutado localmente.
- [x] Rollback ejecutado sólo si existe una versión anterior apta; en otro caso, el
  aborto queda registrado sin fingir éxito.
- [x] Suite completa en verde y laboratorio sin residuos.
- [x] Backend y frontend sin cambios rastreados.
- [x] Durante la ejecución el proyecto permaneció en 25/41 y Stage 08 en 3/4 (75 %); los
      contadores solo avanzaron con la aprobación, a **26/41** y **4/4**.
- [x] La tarea no se marcó Aprobada por decisión propia: el usuario escribió
      `approved: Task/026-Runbooks-de-Despliegue` el 2026-09-15.

Resultado: **13 criterios en PASS**, ningún FAIL. El noveno se cumple por su rama
negativa —no existe versión anterior apta, y el aborto quedó registrado sin fingir
éxito—; el detalle está en el §7 del [reporte](../task-reports/TASK-026-report.md).

## 10. Plan de ejecución

1. RED→GREEN de modo explícito y binding.
2. RED→GREEN de operaciones humanas y confirmación del plan.
3. RED→GREEN de drift estrecho y AWS SDK del artefacto.
4. Redacción de runbooks y actualización de estado vivo.
5. Suite estática/completa.
6. Construcción del artefacto Task/024 sin cambios rastreados.
7. Ensayo local completo y controles negativos.
8. Ausencia final, retirada del laboratorio y auditoría Git.
9. Reporte final **en progreso**, sin commit, push, PR ni aprobación.
