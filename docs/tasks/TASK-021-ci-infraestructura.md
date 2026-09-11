# TASK-021 — CI Infraestructura

| Campo | Valor |
| --- | --- |
| **Identificador / rama** | `Task/021-CI-Infraestructura` |
| **Nombre** | CI Infraestructura |
| **Etapa** | ETAPA 06 — Integración Continua |
| **Estado** | **Lista para validación** — `CI Infra` verde el 2026-09-11 |
| **Repositorios involucrados** | `personal-blog-infra`; backend/frontend solo lectura |
| **Dependencias** | `Task/018`, aprobada; Task019 y Task020 aprobadas al inicio |
| **Rama base** | **`main`** |
| **SHA base medido al crear la rama** | `d7136b29a906563af6edbae0b67dfac101c1f3fa` |
| **Fecha de inicio / actualización** | 2026-09-10 (Guatemala) |
| **Reporte** | [TASK-021-report.md](../task-reports/TASK-021-report.md) |

## 0. Preparación Git

Observado el 2026-09-10, entre 20:54 y 20:55 de Guatemala: `fetch --prune`
en los tres repositorios; todos en `main`, limpios, staging vacío, sin ramas
Task locales ni remotas y con `main == origin/main`. En infra se comprobó
también `dev == origin/dev`, `dev..main = 0`, ascendencia de `main` sobre
`dev` y contenido idéntico. La consulta de PR con el head exacto devolvió `[]`.

Se ejecutaron `switch main` y `pull --ff-only origin main` en infra; se
revalidaron limpieza e igualdad antes de crear la rama. A las **20:55:30**,
inmediatamente después de crearla, `HEAD == main`, `main..HEAD = 0` y
staging = 0. Los SHA de los tres repositorios figuran en el reporte.
Regla: [WORKFLOW §2.1](../project-management/WORKFLOW.md).

## 1. Objetivo

Automatizar la validación de los artefactos reales de infraestructura en
GitHub Actions: Compose, scripts, secretos e infraestructura de S-09.
Auditar el historial disponible de los tres repositorios y la evidencia de
salida de STAGE-06, distinguiendo implementación, aprobación y cierre global.

## 2. Contexto

Inicio autorizado el 2026-09-10 tras Task020, Task020.1 y Task020.2 aprobadas.
Avance pre-aprobación: **20/41 — 49 %**; ETAPA 06 **2/3 — 67 %**, En progreso.
La lectura obligatoria encontró **B-021-1** y **B-021-2**, contradicciones
documentales nuevas de clase D, reproducidas en el reporte. Los apartados
4 y 26 de la solicitud ordenan detenerse antes de corregirlas. El usuario
autorizó su corrección el mismo día: **B-021-1/2 Resueltos**. Task021 se
reanudó sin crear otra maintenance.

## 3. Dentro del alcance

- [x] Preflight y creación de la rama desde `main`.
- [x] Clasificar y registrar los bloqueos detectados durante la lectura.
- [x] Completar la lectura canónica y el inventario exacto A–L.
- [x] Medir baseline Compose y sintaxis de scripts con valores ficticios.
- [x] Auditoría histórica de los tres repositorios, en solo lectura.
- [x] Controles negativos locales de las familias existentes, restaurados.
- [x] Implementar `CI Infra` con permisos mínimos y herramientas fijadas.
- [x] Gate S-09 de infraestructura con baseline exacto de riesgo aceptado.
- [x] Bootstrap remoto autorizado, ejecutado tras verde local y C = 0 / D = 0.
- [x] Auditar pasos, logs, tiempos y matriz global de STAGE-06.

## 4. Fuera del alcance

Task022, Terraform/Task025, cloud, deploy, registry, OIDC, settings, secretos
nuevos y modificaciones de backend/frontend. El permiso de bootstrap no
autoriza PR, integración en dev ni publicación de mutaciones rotas. No se
alteran contenedores, volúmenes, datos, `.env` ni el laboratorio residual Task020.

## 5. Entregables

Inventario exacto, baseline de Compose, validación de las dos familias de
scripts, auditoría histórica de los tres repositorios y cinco controles
negativos locales, todo registrado en el reporte. **El workflow y el gate de
vulnerabilidades no se implementan**: su forma depende de **B-021-3**. En la
reanudación autorizada del 2026-09-10 se corrigieron además los pasajes
equivalentes de ficha y reporte de Task020.1 y del reporte de Task020. La ficha
Task020 no necesitaba cambios.

## 6. Criterios de aceptación

Alcance completo, gates reales verdes, controles negativos restaurados,
auditoría histórica de los tres repositorios, run `push` exitoso sobre el
SHA exacto de Task021 y logs inspeccionados. Criterion12 C = 0 / D = 0.
La aprobación de Task021 y el cierre global de etapa requieren sus evidencias
respectivas; no se anticipan contadores ni se relajan criterios de salida.

## 7. TDD / Plan test-first

No aplica TDD de aplicación: configuración/CI y ningún backend funcional.
Sí aplican controles negativos para demostrar que cada gate detecta errores.

### 7.1 Comportamientos a construir

Rechazar Compose y scripts inválidos; detectar secretos solo históricos;
aplicar una política efectiva y fail-closed al escaneo de vulnerabilidades.

### 7.2 Matriz de casos

Pendiente de completar tras el desbloqueo y el inventario real. Mínimos
autorizados: Compose inválido, sintaxis inválida por familia existente,
canary solo histórico en repositorio temporal y negativo del gate S-09.

### 7.3 Tests RED esperados

Exit distinto de cero en cada negativo, seguido de restauración byte a byte
y GREEN. Ningún negativo se ha ejecutado en esta detención.

### 7.4 Integración necesaria

Compose config no exige levantar servicios. CI real por `push`, dentro de
la excepción estrecha del usuario. Herramientas aún no seleccionadas.

### 7.5 Casos negativos y de seguridad

No publicar cambios deliberadamente rotos. El canary histórico se prepara
fuera de los tres repositorios; nunca se utiliza una credencial real.

### 7.6 Regresiones relevantes

Gates restaurados y archivos idénticos tras los negativos. La validación
de scripts operativos no debe ejecutar sus operaciones sobre el entorno.

## 8. Plan de validación

Los dos bloqueos documentales quedaron resueltos mediante autorización
explícita el 2026-09-10. El baseline se midió a continuación y quedó verde en
Compose, scripts y secretos del historial. El diseño del workflow queda a la
espera de la decisión sobre **B-021-3**, que determina qué imágenes escanea el
gate de S-09 y con qué política.

## 9. Comandos de validación

Desde infra, consultas no destructivas para revisar esta detención:

```powershell
git status --short --branch
git rev-parse HEAD
git rev-list --count main..HEAD
git diff --cached --name-only
git diff --check
rg -n -C 3 'D-020-H|decisión abierta|simplemente|Pull request' docs/tasks/TASK-020.1-correct-post-merge-documentation-drift.md docs/task-reports/TASK-020.1-report.md
```

Contrastar D-020-H con §12 de la ficha Task020. Leer en el reporte la reproducción histórica y su tratamiento autorizado.

## 10. Evidencia esperada

El reporte registra las mediciones obtenidas y marca como no ejecutado el
trabajo detenido. Acredita validación técnica **local**; **no** acredita
ninguna ejecución de CI, que no existe todavía.

## 11. Riesgos

Confundir una limitación técnica pendiente con una decisión aprobada aún
abierta; declarar C/D = 0 sin terminar el barrido; presentar negativos locales
como remotos. La detención y la separación explícita de evidencia los acotan.

## 12. Decisiones técnicas

Ninguna decisión nueva de implementación o arquitectura tomada. Las
correcciones documentales de B-021-1/2 se aplicaron el 2026-09-10 con
autorización explícita del usuario; no introducen decisiones nuevas.

**Decisión durable adoptada, autorizada expresamente el 2026-09-11:** *S-09 de
infraestructura usa tolerancia cero para las imágenes construidas por el
proyecto y baseline exacto de riesgo aceptado para imágenes third-party fijadas
por digest. El baseline no oculta findings y la CI falla ante cualquier
hallazgo accionable nuevo o digest no revisado.*

**Decisiones instrumentales medidas, no adoptadas por iniciativa propia:**
Gitleaks **8.30.1** y Trivy **0.74.0**, ambos fijados por versión y verificados
por SHA256; `--profile admin` para que el gate de Compose cubra los 7
servicios; `--env-file .env.example` para no tocar el `.env` real;
PSScriptAnalyzer **considerado y no adoptado**. La identidad de un hallazgo
excluye `fixed_version` a propósito: que el origen publique otra versión
corregida no es un riesgo nuevo. **MinIO y Portainer no se actualizan** dentro
de esta tarea, y el backend **no se toca**.

## 13. Documentación creada o actualizada

Esta ficha, reporte, STATUS, ROADMAP, STAGE-06 e índice de reportes. NFR
permanece sin cambios: no se ha satisfecho S-09 infraestructura.

## 14. Archivos modificados

**9 documentos** de infra, enumerados en §Z del reporte: los seis de la primera
detención más las tres fuentes heredadas corregidas por B-021-1/2. **Ningún
artefacto funcional modificado**: Compose, Dockerfiles y scripts quedaron byte
a byte idénticos tras los controles negativos.

## 15. Resultado de pruebas

*Ejecución **34604423915**, `push`, `success` en **51 s**, 15 de 15 pasos.*
Preflight Git superado. Compose **exit 0** sin warnings, con los 7 servicios
cubiertos mediante `--profile admin`. PowerShell **6/6** y Python **2/2** sin
errores de sintaxis. Gitleaks sobre el historial: infra **0 hallazgos**,
frontend **0**, backend **2 falsos positivos demostrados**. Controles negativos
A, B, D, E y F en rojo y restaurados. Trivy: las dos imágenes propias en **0**;
el residual de MinIO y Portainer, aceptado y vigilado. En CI: **44** commits
escaneados, **116** hallazgos comparados y **0** fuera del baseline. Logs
auditados: **1 861** líneas, **0** secretos.

## 16. Problemas encontrados

**B-021-1 y B-021-2 Resueltos** el 2026-09-10: D documentales heredadas,
corregidas con autorización explícita durante el preflight de Task021. D-020-H
permanece vigente y se conserva la trazabilidad histórica de Task020.1.

**B-021-3 Resuelto** el 2026-09-11 por decisión explícita del usuario. La
imagen de MinIO que el proyecto fija **ya es la última publicada en Docker
Hub** y acumula 100 hallazgos HIGH/CRITICAL con corrección aguas arriba;
Portainer suma 16 y su mejor versión disponible solo baja a 9. Además, MinIO
está fijado también en el CI del backend, que esta tarea no puede modificar.

La política autorizada separa dos clases: **tolerancia cero** en las imágenes
que construye el proyecto, ambas medidas en **0**, y **baseline exacto de
riesgo aceptado** en las de terceros, con los **116** hallazgos enumerados uno
a uno en `security/vulnerability-baseline.json` y ligados a su digest. El
residual **no queda corregido ni oculto**: queda **vigilado**. Propietarios:
**R-018-3** y **R-021-1**. Detalle y mediciones en §M, §N y §Ñ del reporte.

## 17. Pasos de validación para el usuario

Revisar las correcciones autorizadas contra los pasajes originales del
reporte; ejecutar §9 para consultar Git. La autorización recibida para corregirlos y
reanudar Task021 no equivale a aprobar la tarea ni habilita un negativo remoto.

## 18. Deuda técnica pendiente

Depurar el baseline cuando el residual se reduzca, actualizar Portainer cuando
su salto de línea pueda validarse contra el volumen persistente, y decidir el
futuro de MinIO ahora que no recibe imágenes aguas arriba: **ninguna de las
tres pertenece a `Task/021`**. El cierre global de la etapa conserva la
exigencia de PR y `dev` en los tres repositorios y del control negativo remoto
autorizado, que sigue sin concederse.

## 19. Próxima tarea

`Task/022-Validacion-Local-Production-Like` permanece **Pendiente** y no se
inicia.

## 20. Aprobación

No recibida. La expresión aplicable al futuro cierre es
`approved: Task/021-CI-Infraestructura`; esta entrega no la solicita.
