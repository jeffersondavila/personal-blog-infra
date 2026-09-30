# TASK-030 — Desplegar Amazon S3

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/030-Desplegar-Amazon-S3` |
| **Nombre** | Desplegar Amazon S3 |
| **Etapa** | ETAPA 10 — Despliegue Cloud |
| **Estado** | **Aprobada** — 2026-09-29, mediante `approved: Task/030-Desplegar-Amazon-S3`. Bucket de medios **creado, verificado y convergente** (0/0/0, drift 0); **DEF-030-1**, **DEF-030-2** y **DEF-030-3 corregidos**; `crear`, `validar` y `destruir` **reales** sobre los dos roots; laboratorio retirado sin residuos; AWS final **0/0/0, drift 0** |
| **Repositorios involucrados** | `personal-blog-infra` y `personal-blog-backend` —ampliación explícita y acotada para DEF-030-1—; frontend **intacto** |
| **Dependencias** | Task/029 aprobada; Task/029.1 aprobada e integrada |
| **Rama** | `Task/030-Desplegar-Amazon-S3` |
| **Rama base** | `main` actualizado y limpio; nunca `dev` |
| **SHA base** | `db6e9c7804cbf8f8afcb5fcbd8b7ec8cd8dfd485` |
| **Fecha de inicio** | 2026-09-27, America/Guatemala |
| **Última actualización** | 2026-09-29, America/Guatemala |
| **Avance** | **30/41 ≈ 73 %**; ETAPA 10 **En progreso, 1/7 ≈ 14 %**, abierta con esta aprobación |

## 0. Preparación Git

Observación al abrir la tarea: fetch de los tres repositorios, árboles limpios en
main, `HEAD == main == origin/main`; sin ramas Task/030 locales/remotas.
Infra: `dev == origin/dev == 5c27f7b2471ce2fa17f1abdaf32a6de57b16d41d`,
diff main/dev vacío, `dev..main=0`. Merges de 029 y 029.1 presentes en main.
Tras switch/pull fast-forward y creación: HEAD y main coinciden con el SHA base.
Backend `4a40364bbd6a444f9469b815d17d2d77a37949ce`; frontend
`7dce98aff239d61ae3ae15213d9a3f5ebf0fb8ce`, ambos sin rama de tarea.
Rige el [WORKFLOW](../project-management/WORKFLOW.md); no commit/push/PR/merge
antes de la aprobación final exacta.

## 1. Objetivo

Materializar D-06 y después S3 de medios mediante fases autorizadas, con evidencia
AWS real y recuperación del state, sin adelantar el despliegue de aplicación.
H-030-1 quedó aplicado y verificado bajo autorización expresa. La primera migración
abrió H-030-4 por metadata y después por un resource_drift. Tras diagnóstico y plan
refresh-only revisado, el usuario autorizó aplicar su binario exacto: solo state,
lineage preservado y serial 1→2. Nuevo plan normal exit 0, 0/0/0, drift 0 (§14 del
reporte). Después se migró el state OIDC bajo la misma autorización H-030-2:
reprodujo el patrón conocido de Terraform 1.16.2 —solo lineage y serial, con
recursos, outputs y check_results idénticos— y su plan de convergencia quedó
**limpio sin refresh-only**: exit 0, 0/0/0, drift 0, ocho checks pass (§15 del
reporte). IAM real intacto. Después se demostraron la **contención del locking
nativo** —solapamiento real, segunda operación rechazada por error de adquisición del
state lock vía `PutObject` 412— y el **recovery por versión** de las dos keys, con
0 desviaciones y sin crear versiones nuevas (§16). H-030-2 sigue pendiente solo de
retirar los locales, eliminar el scaffolding de la prueba y extinguir la excepción.
Todo ello quedó hecho el 2026-09-28: S3 es la **única** fuente operacional de ambos
roots, los locales son **backups históricos inactivos** y **EX-028-C7 está
Extinguida** (§17). **H-030-2 COMPLETO.** Backups cifrados intactos.

## 2. Contexto

Primera tarea de ETAPA 10. D-06 ya está Resuelta; **EX-028-C7 quedó Extinguida el
2026-09-28**, antes de cualquier apply de aplicación, como exigía la regla. RDS reemplazó al VPS; D-16 no se implementa.
La [auditoría](../task-reports/TASK-030-research.md) recoge fuentes, código actual,
historia y diferencias documentales sin resolver D-08 anticipadamente.

## 3. Dentro del alcance

- [x] Preflight y rama; identidad humana verificada; inventario pertinente read-only.
- [x] Investigación oficial, nombre/costos, bootstrap independiente y plan real.
- [x] Incorporación de BPA global y de bucket al **diseño/plan**, autorizada en H-030-4.
- [x] H-030-1: apply del plan autorizado y readback independiente: **7 añadidos, 0 cambios, 0 destruidos**.
- [x] H-030-2 **COMPLETO**: ambos states migrados y validados, locking probado por
      contención real, recovery por versión probado, locales retirados como fuentes
      operativas y **EX-028-C7 Extinguida** el 2026-09-28.
- [x] Análisis y decisión **D-08: RESUELTA para el MVP** (2026-09-28, `H-030-D08-MVP`):
      privado + presigned dinámico, sin URL estable, sin CDN y sin servicio nuevo.
      **`B-016-1` permanece abierto** como limitación de producto aceptada.
- [x] H-030-3: bloqueo de §21 **resuelto por la vía A** (§22): el almacenamiento de medios
      pasa a un **root propio**, `terraform-medios`, que **reutiliza** el módulo de
      `Task/025` sin duplicar ningún `aws_s3_*`; el grafo de aplicación recibe nombre y ARN
      por **contrato explícito**. Apply autorizado de **7 altas**, readback 10/10 y, tras
      el refresh-only autorizado de H-030-4, convergencia **0/0/0 con drift 0** (§§23–24).
- [x] **DEF-030-1**: prefirmadas de `S3Storage` contra AWS real, corregidas bajo la
      **BACKEND TEST-FIRST LAW**; **1974 passed, 2 skipped**, MinIO **48/48**, AWS **14/14** (§25).
- [x] **DEF-030-2**: los cinco subcomandos de runbook operan sobre los **dos roots**, en orden
      de creación o inverso; **44 pruebas** y `crear`, `validar` y `destruir` **reales** (§27).
- [x] **DEF-030-3**: identidad del runtime por lista **cerrada** de representaciones, sin
      relajar la igualdad del image ID; **16 pruebas** y runtime **COINCIDE** en real (§27).
- [x] **H-030-5**: ciclo real, subcomandos reales, teardown, `bajar` sin residuos, contexto
      productivo restaurado, AWS final **0/0/0, drift 0** y gates en verde (§27).
      `rollback` y `recuperar`: **pruebas controladas**, no ejecución real.

## 4. Fuera del alcance

VPC/subnets/rutas/endpoints, NAT, RDS, security groups, Lambda, API Gateway,
SSM/secretos/KMS de aplicación, CloudWatch, Grafana, Pages, DNS/dominio,
migraciones PostgreSQL y CI/CD de despliegue. Task/031 conserva red/RDS/configuración,
observabilidad y restore. No VPS, SSH, PgBouncer, backups/identidad de host ni D-16.
No cambiar código backend/frontend, Billing ni el rol OIDC de validación.

## 5. Entregables

| Entregable | Ruta |
| --- | --- |
| Root/bootstrap con tests y lock | `bootstrap/terraform-state/` |
| Guarda offline de plan y regresiones | `scripts/terraform_state/check_plan.py`, `tests/terraform_state/test_plan.py` |
| Runbook y estrategia del state | [terraform-state-bootstrap.md](../runbooks/terraform-state-bootstrap.md) |
| Investigación/auditoría/costos | [TASK-030-research.md](../task-reports/TASK-030-research.md) |
| Evidencia cronológica y checkpoint | [TASK-030-report.md](../task-reports/TASK-030-report.md) |
| CI offline y gobierno actualizado | `.github/workflows/ci-infra.yml`, STATUS, ROADMAP, STAGE-10 |
| Root de almacenamiento de medios, con tests y lock | `terraform-medios/` |
| Laboratorio consciente de dos roots y runtime por lista cerrada | `scripts/laboratorio/laboratorio.py`, `scripts/laboratorio/runtime.py` |
| Regresiones de DEF-030-2 y DEF-030-3 | `tests/laboratorio/test_topologia_de_roots.py`, `tests/laboratorio/test_identidad_del_runtime.py` |
| Arreglo de DEF-030-1, en el backend | `app/shared/storage/s3.py`, `tests/unit/test_adaptadores_de_almacenamiento.py` |

## 6. Criterios de aceptación

1. Plan H-030-1 de siete creaciones exactas; cero cambios/destrucciones/importaciones,
   sin IAM ni recursos de aplicación. BPA global identificado expresamente.
2. Bucket privado/dedicado, ownership sin ACL, versionado/cifrado explícitos, TLS,
   tags y prevención de destrucción; sin lifecycle que expire versiones de state.
3. State temporal fuera de Git, protegido, con destino propio y recuperación diseñada.
4. Después de autorizaciones: backend S3 real `use_lockfile=true`, sin DynamoDB,
   ambos estados migrados/verificados, recovery y locking demostrados.
5. Después: D-08 propuesta revisada; S3Storage real y controles negativos demostrados.
6. Gates locales y AWS con resultados reales; contadores sin aprobación anticipada.
7. Checkpoints humanos no equivalen al approval final ni autorizan publicaciones.

## 7. TDD / Plan test-first

La ley de backend funcional **sí** se aplicó a DEF-030-1, el único cambio de comportamiento
del backend: matriz, RED demostrado, GREEN mínimo, refactor declarado innecesario y regresión
completa (§25 del reporte). *(Esta sección decía antes que ningún comportamiento backend
cambiaba; dejó de ser cierto con DEF-030-1.)*
Terraform se valida mediante planes con provider simulado y postcondiciones de identidad.
La guarda offline tiene controles negativos de alcance y seguridad; no se atribuye
RED histórico ni ejecución AWS a esos mocks. Las suites existentes se reejecutan.

## 8. Plan de validación

Sintaxis/formato/lock; Terraform tests de bootstrap y OIDC; guardas de laboratorio,
OIDC y nuevo plan; pruebas storage/configuración/contrato API contra local; gates de
texto, links, encabezados, tareas, secretos y state fuera de Git. Luego plan real.
Las pruebas AWS de apply, locking, recuperación y `S3Storage` ya se ejecutaron (§§7–25 del
reporte); el ciclo del laboratorio y sus subcomandos, en §§26–27.

## 9. Comandos de validación

```text
terraform -chdir=bootstrap/terraform-state fmt -check -recursive
terraform -chdir=bootstrap/terraform-state validate
terraform -chdir=bootstrap/terraform-state test
python -B -m unittest discover -s tests/terraform_state -v
python -B -m unittest discover -s tests/laboratorio -q
python -B -m unittest discover -s tests/oidc -q
terraform -chdir=terraform-medios fmt -check -recursive
terraform -chdir=terraform-medios init -backend=false -input=false -lockfile=readonly
terraform -chdir=terraform-medios validate
terraform -chdir=terraform-medios test
python -B -m unittest discover -s tests/laboratorio -p "test_*.py"
python -B -m unittest discover -s tests/security -p "test_*.py"
git diff --check
```

Rutas privadas, init/plan y variables operativas: [runbook](../runbooks/terraform-state-bootstrap.md).
No ejecutar comandos de migración: H-030-2 ya está cerrado y S3 es la única fuente operativa.

## 10. Evidencia esperada

Plan binario/JSON/log **privados**; solo hashes, direcciones, conteos y resumen
saneado en el reporte. Readback de controles después de apply; metadatos de versiones,
state y backups después de migrar; nunca snapshots ni credenciales en Git/chat.

## 11. Riesgos

| Riesgo | Mitigación |
| --- | --- |
| BPA global afecta buckets futuros de toda la cuenta | H-030-4 explícito; arquitectura privada; decisión futura antes de acceso público directo |
| Colisión entre check y create | Hash determinístico y parada ante colisión; no sufijos automáticos |
| Dos backends activos o pérdida del state bootstrap | Un operador, backups, migración secuencial y readback antes de archivar el local |
| Borrado de versiones recuperables | Sin expiración, sin permisos de DeleteObjectVersion para operación normal |
| Crecimiento de versiones | Modelo de costos y seguimiento en Task/041; no purga silenciosa |
| Plan obsoleto/identidad distinta | Hash/fuentes/inventario/sesión revalidados; plan distinto vuelve al checkpoint |

## 12. Decisiones técnicas

Diseño **aceptado con la aprobación del 2026-09-29** —antes, propuesto—: root independiente,
siete recursos, SSE-S3, retención de todas las versiones, nombre determinístico y keys
separadas. D-06 no se reabre. El root **`terraform-medios`**, la precisión de la regla de
paridad (§4.1.1, Vigente desde el 2026-09-28) y el runbook del bucket de state quedan
**Vigentes**.
H-030-4 autoriza **diseñar y planear** el BPA global con cuatro flags; no su apply.
**D-08 quedó Resuelta para el MVP** el 2026-09-28 (§§19–20 del reporte): bucket privado,
presigned dinámico para borrador y publicado, TTL 900 s, CORS con lista vacía, *lifecycle*
de 30 y 7 días, `forzar_destruccion = false` y **ningún servicio nuevo**. **`B-016-1` sigue
abierto**; el dominio continúa en **D-07**.

## 13. Documentación creada o actualizada

Ficha, reporte, investigación y runbook nuevos; STATUS/ROADMAP/STAGE-10 e índice
de runbooks actualizados. Los cinco runbooks del laboratorio —crear, validar, rollback,
destruir y recuperar— describen ya los **dos roots** (DEF-030-2). Las decisiones RDS,
EX-029-D13 y los reportes previos conservan sus estados/historia.

## 14. Archivos modificados

Inventario del entregable en el [reporte](../task-reports/TASK-030-report.md).
`bootstrap/github-oidc/versions.tf` es el único archivo versionado que
H-030-2 modifica: su backend pasa de `local` a `s3`. La enmienda de H-030-4 añade el root
`terraform-medios/` y toca `terraform/` —`main.tf`, `variables.tf`, `outputs.tf`, los dos
tfvars y el módulo de almacenamiento— más la orquestación del laboratorio en
`scripts/laboratorio/laboratorio.py`. DEF-030-2 y DEF-030-3 tocan `laboratorio.py` y
`runtime.py` y añaden dos archivos de prueba en `tests/laboratorio/`. En el **backend**,
DEF-030-1 modifica exactamente dos archivos, **+145 / −4**. Inventario exacto en el reporte.

## 15. Resultado de pruebas

Resultados exactos, incluido un skip de plataforma y fallos iniciales de invocación
local corregidos, en el [reporte](../task-reports/TASK-030-report.md).
Un plan verde no prueba privacidad, locking ni recuperación en AWS.

Cierre (§27.8): `tests/laboratorio` **236 OK**, `tests/oidc` **60 OK** con 1 skip de
plataforma, `tests/terraform_state` **12 OK**, `tests/security` **88 OK**; Terraform **16/16**
en los cuatro roots, con `terraform-medios test` **7 passed**; Gitleaks sin hallazgos; 0
enlaces rotos; Account ID real con 0 apariciones. Backend: almacenamiento **29 passed**, Ruff,
mypy y `git diff --check` en verde; suite completa **1974 passed, 2 skipped** (§26.10).

## 16. Problemas encontrados

Sesión AWS expirada: parada y renovación humana. BPA de cuenta ausente:
H-030-4 y autorización explícita de opción 1, exclusivamente diseño/plan.
Drift documental de contadores/vista rápida corregido al abrir la tarea;
ninguna ampliación de permisos ni mutación cloud.
Después: el grafo único no admitía un plan solo de medios (§21), resuelto con el root propio;
`resource_drift = 1` por atributos espejo, reconciliado con refresh-only autorizado (§§23–24);
**DEF-030-1**, prefirmadas con 403 contra AWS real (§§24–25); **DEF-030-2** y **DEF-030-3**,
en el herramental del laboratorio (§§26–27). En H-030-5, el traspaso tras agotarse la sesión
anterior afirmaba que el destroy de medios seguía pendiente; el log y el state demostraron que
ya se había aplicado, y se verificó de forma independiente (§27.3).

## 17. Pasos de validación para el usuario

Revisar §§11–14 del reporte —diagnóstico, plan refresh-only, autorización exacta,
apply y convergencia limpia— y después **§15**: preflight OIDC, sonda previa,
migración, readback de la versión S3 concreta, IAM real sin cambios y plan de
convergencia 0/0/0 con drift 0. Los dos bootstrap quedan técnicamente validados
contra S3. Revisar **§16** —preflight, contención real del lock con su mecanismo
exacto y recovery de las dos keys, incluida una versión anterior— y **§17**: retirada
de los locales a un archivo inactivo con manifiestos, eliminación del scaffolding de
la prueba y extinción de EX-028-C7 con su base factual. **H-030-2 queda COMPLETO.**
Después, **§§19–20** —D-08 Resuelta para el MVP—, **§§21–24** —root de medios, apply,
readback y convergencia—, **§25** —DEF-030-1 bajo test-first— y **§§26–27** —laboratorio,
DEF-030-2, DEF-030-3, ejecución real, teardown, AWS final y gates—. Todo eso dejó la tarea
**READY FOR FINAL APPROVAL**; el usuario la **aprobó el 2026-09-29**. Para revisar el cierre
Git y los PR, **§28**.

## 18. Deuda técnica pendiente

**D-08**, el S3 de medios y sus pruebas reales ya **no** son deuda: están hechos (§§20–27).
Quedan, con propietario:

- **`B-016-1`** sigue **abierto**, como limitación de producto aceptada por D-08.
- **Reanudar un `destruir` interrumpido entre roots** no es posible relanzando el comando:
  falla cerrado en el root de aplicación, ya vacío (§27.9). Decisión humana documentada en
  el [runbook](../runbooks/deployment-destroy.md); deuda del herramental del laboratorio.
- Las dos fixtures sintéticas del backend que Gitleaks reconoce siguen sin *allowlist*
  (§26.9): observación, no hallazgo de seguridad.

H-030-2 ya no deja deuda:
migración, convergencia, locking por contención, recovery, retirada de locales y
extinción de EX-028-C7 están hechos y verificados (§§15–17). Deuda documental
detectada y corregida en el camino: el runbook no registraba `AWS_PROFILE`. La
otra deuda anotada aquí era **un error propio, ya rectificado**: se afirmó que la ACL
declarada para `bootstrap/terraform-state` no se sostenía, midiendo el directorio
ancestro en lugar del documentado. Ese root **sí** tiene herencia deshabilitada y solo
`SYSTEM` y `jeffe`, sin acceso de `CodexSandboxUsers`. El hueco real estaba en
`bootstrap/github-oidc` y en el archivo histórico, que heredaban lectura de
`%LOCALAPPDATA%`, y quedó cerrado bajo `H-030-2-custodia-local` (§§17.6 y 18 del
reporte).
*(Dos líneas anteriores de esta sección quedaron superadas y se retiran: el hueco de
`AWS_PROFILE` en el runbook ya está corregido, y EX-028-C7 quedó **Extinguida** el
2026-09-28.)* Backups previos verificados y preservados.
IAM de CI en Tasks/038/039; no reutilizar rol OIDC.
Task/041 revisa costos/versiones; Tasks/031+ conservan los propietarios del roadmap.

## 19. Próxima tarea

`Task/031-Desplegar-Red-RDS-SSM-y-CloudWatch` **no está iniciada**. Nacerá de `main`
actualizado y limpio **después** de que el usuario fusione los PR `Task/030 → main` y se
normalice `main → dev`. La aprobación no autoriza iniciarla ni aplicar nada contra AWS.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| Fecha de aprobación | **2026-09-29** |
| Aprobado por | **El usuario**, con la expresión exacta requerida |
| Expresión de aprobación final | `approved: Task/030-Desplegar-Amazon-S3` |

H-030-1/2/3/4, H-030-D08 y H-030-5 no sustituían esa aprobación final. **Recibida el
2026-09-29**: la tarea queda **Aprobada**; el cierre Git se registra en §28 del
[reporte](../task-reports/TASK-030-report.md).
