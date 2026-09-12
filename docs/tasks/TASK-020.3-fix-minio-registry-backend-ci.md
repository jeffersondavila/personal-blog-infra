# TASK-020.3 — Corregir registro de MinIO en CI Backend

| Campo | Valor |
| --- | --- |
| **Identificador / rama** | `Task/020.3-Corregir-Registro-MinIO-CI-Backend` |
| **Nombre** | Corregir registro de MinIO en CI Backend |
| **Etapa** | ETAPA 06 — mantenimiento, fuera de las 41 tareas |
| **Estado** | Lista para validación |
| **Repositorios involucrados** | backend: workflow; infra: documentación; frontend: solo lectura |
| **Dependencias** | Task020 y Task021, Aprobadas |
| **Rama base** | `main` actualizado y limpio |
| **SHA base backend** | `8055878e415ace2bfc4e7685e0549c5ab8a642ef` |
| **SHA base infra** | `aef66384372c13998eb03f38f5629b8692f8f9e0` |
| **Fecha de inicio / actualización** | 2026-09-12 |
| **Reporte** | [TASK-020.3-report.md](../task-reports/TASK-020.3-report.md) |

## 0. Preparación Git

Observado el 2026-09-12: en ambos repositorios se ejecutaron `fetch --prune`,
`switch main` y `pull --ff-only origin main`. Árbol limpio, staging 0,
untracked 0 y `main == origin/main` antes de crear la rama. Inmediatamente
después, `HEAD == main` en los SHA de la tabla. Frontend permaneció limpio en
`main`, SHA `7dce98aff239d61ae3ae15213d9a3f5ebf0fb8ce`, sin rama nueva.
Regla: [WORKFLOW §2.1](../project-management/WORKFLOW.md).

## 1. Objetivo

Recuperar una ejecución completa y reproducible de CI Backend usando Quay como
origen del mismo artefacto MinIO, y documentar el cierre técnico de STAGE-06.

## 2. Contexto

`34491446991` attempt 1 fue success el 2026-09-10. Su attempt 2 falló el
2026-09-12 en la descarga desde Docker Hub, con el mismo SHA `5fedcb3`.
Task020 y Task021 conservan su aprobación. Avance real: **21/41 ≈ 51 %**;
ETAPA 06: **3/3 tareas aprobadas**. Este mantenimiento no suma avance.

## 3. Dentro del alcance

- [x] Corregir D-020.3-A/B y revisar la familia documental autorizada.
- [x] Comprobar acceso anónimo al digest exacto en Quay.
- [x] Cambiar únicamente el registro de `IMAGEN_DE_MINIO` y validar localmente.
- [x] Bootstrap autorizado de backend y run nuevo; resultado failure registrado en el reporte.
- [x] Auditar todos los pasos y documentar la detención; STAGE-06 conserva cierre pendiente.

## 4. Fuera del alcance

Actualizar MinIO o digest; cambiar estructura, comandos, puertos, healthchecks,
tests, dependencias, locks, Dockerfile, Trivy o S-09; credenciales de registro,
GitHub secrets, ADR, frontend, Task022, otro broken push, otro rerun de
34491446991, merge/push de dev y PR. No se modifica main directamente.

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Origen Quay para el mismo MinIO | backend | `.github/workflows/ci-backend.yml` |
| Estado, evidencia y cierre técnico | infra | Esta ficha, reporte, STATUS, ROADMAP, STAGE-06, NFR, índice y referencias históricas de Task020/021 |

## 6. Criterios de aceptación

Una sola línea funcional; release y digest idénticos; acceso Quay anónimo;
workflow válido; CI nueva completed/success con todos los gates ejecutados;
logs sin secretos; enlaces relativos sin destinos rotos; C=0/D=0; frontend
intacto; avance y aprobaciones previas conservados. La tarea no se aprueba sola.

## 7. TDD / Plan test-first

No aplica TDD de comportamiento: configuración declarativa sin lógica y cambio
mecánico, excepción de [estrategia §4](../project-management/BACKEND_TESTING_STRATEGY.md).
El fallo real ya está demostrado en attempt 2; no se repite. La validación es
estática, OCI anónima y de integración en el nuevo runner. Refactor innecesario.

### 7.1 Comportamientos a construir

No se añade comportamiento del backend.

### 7.2 Matriz de casos

| Caso | Entrada / precondición | Resultado esperado | Capa |
| --- | --- | --- | --- |
| Registro alternativo | Quay, release y digest aprobados | Descarga y MinIO saludable sin login | CI / OCI |
| Identidad preservada | Workflow de main frente a Task | Solo prefijo `quay.io/` añadido | Configuración |
| Regresión | PostgreSQL y MinIO efímeros | Todos los gates existentes en success | Integración real |

### 7.3 Tests RED esperados

No aplica test nuevo; RED remoto previo: attempt 2, paso 11, exit 125.

### 7.4 Integración necesaria

La CI existente aprovisiona PostgreSQL y MinIO reales; ejecutar su suite completa.

### 7.5 Casos negativos y de seguridad

Se conserva la evidencia remota negativa de STAGE-06; no se publica otra mutación.
Revisar permisos, ausencia de login y secretos, y gates sin omisiones.

### 7.6 Regresiones relevantes

Formato, lint, tipos, migraciones, suite completa, locks, pip-audit, build,
inventario Trivy y gate de vulnerabilidades de la imagen.

## 8. Plan de validación

Preflight documental, YAML/actionlint y prueba de diff exacto antes del bootstrap.
Después del push autorizado, auditar el nuevo run y sus logs, sin aceptar verde
parcial. Registrar el resultado observado antes de declarar el cierre técnico.

## 9. Comandos de validación

Desde backend:

```powershell
git diff main -- .github/workflows/ci-backend.yml
git diff --check
gh run list --workflow ci-backend.yml --branch Task/020.3-Corregir-Registro-MinIO-CI-Backend
gh run view <run-nuevo> --json status,conclusion,event,headSha,jobs
gh run view <run-nuevo> --log
```

El reporte conserva herramientas, comprobaciones locales y resultados concretos.

## 10. Evidencia esperada

Run nuevo ligado al commit funcional, todos los pasos y tiempos, métricas de
tests, warnings, S-09, Trivy, logs y comprobaciones locales reproducibles.

## 11. Riesgos

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Disponibilidad futura de registry | CI puede volver a fallar | Digest fijado y ejecución real; no se garantiza disponibilidad perpetua |
| R-018-3 / R-021-1, abiertos | Residual aceptado: MinIO 100, Portainer 16 | Política exacta y baseline de Task021 intactos; no son vulnerabilidades corregidas |

## 12. Decisiones técnicas

**Propuesta — pendiente de aprobación del mantenimiento:** usar Quay en la
referencia independiente de CI Backend, con exactamente el release y digest ya
comparados en Task021. Cambio autorizado, sin ADR ni política nueva.

## 13. Documentación creada o actualizada

Esta ficha, reporte, STATUS, ROADMAP, STAGE-06, NFR/S-09, índice de reportes y
fichas/reportes de Task020 y Task021. Se distinguen fechas e intentos, sin
reescribir los resultados históricos ni reabrir tareas aprobadas.

## 14. Archivos modificados

Backend, en dos commits separados: una línea del workflow
(`.github/workflows/ci-backend.yml`) y una capa de actualización de seguridad en
la etapa `runtime` del `Dockerfile`, autorizada despues del diagnostico de
B-020.3-C. Infra: once documentos, enumerados en el reporte. Frontend permanece
en solo lectura.

## 15. Resultado de pruebas

Preflight Git y OCI anónimo conformes. Local GREEN: YAML y actionlint 1.7.12,
diff exacto de una línea, 1389 destinos relativos / 0 rotos, patrones sensibles
0 y Gitleaks 0. CI **34713222925**, completed/failure, **291 s**:
MinIO Quay success, migraciones 13 passed, suite **1855 passed / 0 skipped /
0 warnings**, S-09 dependencias success y build success. Inventario Trivy
177 hallazgos; gate final falla por **12 accionables (9 HIGH, 3 CRITICAL)**.
23 pasos success, 1 failure y 1 skipped de limpieza.

Tras corregir B-020.3-C, validación local de la imagen real: `ruff format` 312
archivos, `ruff check` sin hallazgos, `mypy` 310 fuentes, migraciones 13 passed,
suite **1854 passed / 1 skipped** —el skip es `time.tzset`, inexistente en
Windows— y gate Trivy en **0 accionables, exit 0**. CI final **34719123905**,
push sobre `32c3992`, **completed/success**, **296 s**, **25 pasos success, 0
failure, 0 skipped**: MinIO Quay success, migraciones 13 passed, suite **1855
passed / 0 skipped / 0 warnings**, S-09 dependencias success, build con
`12 upgraded, 0 newly installed, 0 to remove`, inventario **149** en Debian 13.7
con **CRITICAL 0** y gate accionable **0**. Detalle en el reporte.

## 16. Problemas encontrados

**D-020.3-A:** contador vigente obsoleto en ROADMAP. **D-020.3-B:** fecha obsoleta
en STATUS. Ambos confirmados en main, anteriores a Task020.3, corregidos con
autorización explícita del 2026-09-12. No alteran avance ni suman tareas.

**D-020.3-C — RESUELTA sin modificar documentos.** Antes del commit de infra, un
comprobador de enlaces provisional señaló cuatro presuntos enlaces rotos en
`TASK-020-report.md`. La sesión se detuvo y los reportó. La investigación
autorizada demostró que están dentro de un bloque *fenced* ` ```markdown `, que
reproducen literalmente y byte a byte el `README.md` §3 del repositorio backend,
y que en ese contexto los cuatro destinos resuelven. **No eran enlaces
renderizados y no se modificó ninguno.** Los barridos históricos —Task021 el
2026-09-11 y el inicial de este mantenimiento— eran correctos; el comprobador
provisional era el defectuoso. El barrido final, con un analizador que separa
bloques *fenced*, código *inline* e indentado y sin allowlist de destinos, da
**129 archivos, 1394 enlaces renderizados, 14 exclusiones de código literal
clasificadas una a una y 0 enlaces renderizados rotos**.
El barrido acotado también distingue el avance histórico de la cabecera del
reporte Task021 y actualiza la fecha de su ficha, sin cambiar su inicio.

**B-020.3-C — RESUELTO:** gate Trivy de la imagen backend en **0 accionables**,
exit **0**.

Detectado en la CI del 2026-09-12 con 12 hallazgos accionables (9 HIGH, 3
CRITICAL), independiente del registro de MinIO. La implementación se detuvo y se
pidió autorización; no se presupuso la solución ni el alcance. El usuario
autorizó la **Opción 1**, aplicada solo a la etapa `runtime` del Dockerfile.

Causa medida: la información de vulnerabilidades disponible para el **mismo
artefacto** evolucionó entre ejecuciones. Diez CVE ya figuraban en el inventario
anterior pero no eran accionables bajo `--ignore-unfixed` por carecer de
`FixedVersion` utilizable, y después adquirieron corrección publicada; además
aparecieron dos CVE adicionales de `libpcre2-8-0`. Con el mismo artefacto y la
misma versión de Trivy, el gate pasó de 0 a 12 accionables. **El repositorio no
introdujo esas vulnerabilidades.** Tampoco había reconstrucción disponible aguas
arriba: `python:3.12.14-slim` seguía resolviendo al mismo digest ya fijado.

No se cambiaron Python, distribución base, digest del `FROM`, dependencias,
locks, política ni baseline. El `FROM` conserva tag y digest; la capa de APT
aplica las correcciones publicadas en el momento del build, de modo que el
sistema de archivos final deja de estar determinado únicamente por el digest:
consecuencia aceptada explícitamente para esta imagen local/CI y no generalizada
al resto.

## 17. Pasos de validación para el usuario

Revisar los dos commits de backend y los once documentos de infra. Consultar los
dos runs citados en el reporte: **34713222925**, que acredita el bloqueo, y
**34719123905**, que acredita la corrección, especialmente MinIO, suite, S-09,
inventario y gate Trivy. Comprobar que la política S-09 sigue intacta en el
workflow, que el digest del `FROM` no cambió, que los locks no se tocaron, que
el mantenimiento permanece sin aprobación y que Task022 no se inicia.

## 18. Deuda técnica pendiente

R-018-3 y R-021-1 abiertos: las imágenes de terceros —MinIO y Portainer— no se
actualizan aquí. S-09 mantiene las verificaciones futuras del NFR; el cierre
técnico de STAGE-06 no las sustituye. Queda como deuda conocida que el sistema
de archivos de la imagen backend ya no está determinado solo por el digest del
`FROM`: si en el futuro se publica una reconstrucción de `python:3.12.14-slim`
que incorpore las correcciones, convendrá revisar si la capa de APT sigue siendo
necesaria.

## 19. Próxima tarea

Task022 — **Pendiente, no iniciada**. No se inicia dentro de este mantenimiento.

## 20. Aprobación

**Pendiente, exclusiva del usuario.** El bootstrap autorizado permite commit y
push de la rama Task después de local GREEN y C=0/D=0; no aprueba la tarea ni
autoriza integraciones o PR. Regla permanente en
[WORKFLOW](../project-management/WORKFLOW.md).
