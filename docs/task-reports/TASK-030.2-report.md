# TASK-030.2 — Reporte de mantenimiento documental

**Estado: Aprobada — 2026-10-01**, mediante
`approved: Task/030.2-Corregir-Drift-Documental-Post-Merge`.
Mantenimiento **fuera de las 41 tareas**, presentado previamente como
**Task/030.2 — READY FOR FINAL APPROVAL**.
[Ficha](../tasks/TASK-030.2-correct-post-merge-documentation-drift.md).
**Enmienda previa al merge:** H-030.2-CI-Alpine-repair, en
[§7](#7-enmienda-h-0302-ci-alpine-repair), **aprobada** el 2026-10-01. Las secciones 1–6
describen la entrega aprobada originalmente.

## 1. Resultado y alcance

La documentación distingue el entregable final de Task/030 de sus checkpoints anteriores.
Se modifica únicamente Markdown de `personal-blog-infra`. Task/030 conserva su aprobación;
Task/031 permanece **Pendiente, no iniciada**. No hay cambios de backend, frontend, AWS,
Terraform, dependencias, scripts, locks ni workflows.

## 2. Contradicciones corregidas e historia preservada

| Laguna | Resultado durable | Historia preservada |
| --- | --- | --- |
| El inventario final se reducía a DEF-030-1: 2 archivos, +145 / −4 | Ficha §14 y reporte §28 reflejan **6 archivos, +222 / −14**: DEF-030-1, reparación CI MinIO/GHCR y urllib3 2.8.0 con excepción de índice por paquete | §§25–27 del reporte permanecen intactas; sus cifras y gates corresponden a aquellos checkpoints |
| El primer cierre podía leerse como la entrega completa del backend | §28 incorpora el inventario final y delimita explícitamente la lista del primer cierre como checkpoint histórico | Las referencias preexistentes de aquel cierre se conservan, sin sustituirlas por hashes nuevos |
| STAGE-06/NFR no distinguían el origen actual de MinIO del anterior | CI Backend obtiene MinIO del **espejo privado de GHCR**, mediante **`GHCR_MINIO_READ_TOKEN`**, en runner **`linux/amd64`**; manifiesto amd64 preservado del índice original, **misma release y mismos bytes ejecutados** | Los registros de **Task/020.3**, **H-028-1** y los párrafos históricos de Quay se conservan |
| La excepción temporal de urllib3 carecía de seguimiento durable explícito | **DT-030-URLLIB3 abierta**, con propietario, mecanismo y criterio de retiro en NFR §7.1, enlazada desde STATUS y Task/030 | No se atribuye esta deuda a los checkpoints anteriores a la actualización de urllib3 |
| La fila canónica de Task/029 en STATUS seguía como «Pendiente» | **Aprobada (2026-09-27)**, corregida bajo **H-030.2-counter-fix** | Los checkpoints anteriores a su aprobación conservan sus estados originales; Task/029 y Task/029.1 no se reabren |

## 3. Criterio de retiro de DT-030-URLLIB3

Propietario: mantenimiento de dependencias del backend. **`FECHA_DEL_INDICE` global
permanece congelada**; urllib3 tiene temporalmente una fecha propia mediante
**`--exclude-newer-package` + `--upgrade-package`**.

Retirar la variable y ambas opciones específicas cuando un avance autorizado de la fecha
global permita resolver naturalmente urllib3 **2.8.0 o superior compatible**. Deben
coincidir ambos locks regenerados con locks previos y desde cero, pasar el gate de desfase
y los gates existentes del backend, incluidas regresión y auditoría. Fuente única del
criterio: [NFR §7.1](../architecture/non-functional-requirements.md#71-deuda-viva-dt-030-urllib3).
Este mantenimiento solo registra la deuda; no ejecuta su retiro.

## 4. Archivos del entregable

| Archivo | Cambio |
| --- | --- |
| [TASK-030](../tasks/TASK-030-deploy-amazon-s3.md) | Alcance e inventario finales; enlace a deuda urllib3 |
| [Reporte TASK-030](TASK-030-report.md) | Resumen e inventario finales; primer cierre delimitado como historia; deuda viva |
| [STAGE-06](../stages/STAGE-06-continuous-integration.md) | Origen y manifiesto actuales de MinIO en CI Backend |
| [NFR](../architecture/non-functional-requirements.md) | MinIO actual y criterio central de retiro DT-030-URLLIB3 |
| [STATUS](../project-management/STATUS.md) | Estado del mantenimiento fuera de las 41, seguimiento de deuda y corrección de la fila canónica de Task/029 |
| [ROADMAP](../project-management/ROADMAP.md) | Registro de mantenimiento sin alterar el avance |
| [Ficha TASK-030.2](../tasks/TASK-030.2-correct-post-merge-documentation-drift.md) | Nueva: alcance y validación |
| Este reporte | Nuevo: resultado y evidencia |

## 5. Gates y contadores

| Gate | Resultado |
| --- | --- |
| Enlaces Markdown relativos y anclas | **173 documentos, 1992 enlaces/imágenes, 0 rotos** |
| `git diff --check` | **PASS**, sin errores de whitespace |
| Gitleaks 8.30.1, entregable completo | **PASS**, 293 archivos, sin hallazgos |
| Gitleaks 8.30.1, historial completo | **PASS**, sin hallazgos |
| Account-ID scan | **0 apariciones del Account ID real**; solo identificadores ficticios conocidos |
| Alcance y formato | **8 archivos Markdown**, UTF-8 sin BOM ni CRLF; ningún cambio funcional |
| Preservación histórica | **PASS**: §§25–27 y lista del primer cierre de Task/030; cuerpo previo de STAGE-06; checkpoints de Quay en NFR; reportes Task/020.3 y Task/028 intactos |
| Resúmenes STATUS/ROADMAP/STAGE-10 | **30/41 ≈ 73 %**, ETAPA 10 **1/7 ≈ 14 %**; STAGE-10 intacto y Task/031 **Pendiente, no iniciada** |
| Coherencia de la tabla completa de STATUS | **PASS**, Task/001–Task/030 aprobadas y Task/031–Task/041 pendientes: **30 aprobadas + 11 pendientes = 41** |
| Backend y frontend | **PASS**, ambos en `main` limpio, sin cambios |

El primer gate de contadores detectó esa celda fuera de las tres lagunas originales y
falló con **29 aprobadas y 12 pendientes** en la tabla. Bajo autorización explícita
**H-030.2-counter-fix**, se cambió únicamente su estado a **Aprobada (2026-09-27)**,
sin alterar el avance real ni la historia. D-10, D-12, D-22, D-23, D-24, EX-029-D13 y
R-47 permanecen intactos. El validador local ya exigía correctamente Task/001–Task/030
aprobadas y Task/031–Task/041 pendientes: no fue necesario cambiar sus expectativas.
La repetición completa posterior terminó con **exit 0**, sin otras contradicciones
detectadas por los gates. `tmp/task0302/validate.py` y sus evidencias permanecen locales,
ignorados por Git y fuera del entregable versionado.

No aplican builds, suites funcionales, Terraform ni CI funcional: el cambio es
exclusivamente documental. No se añaden dependencias ni gates versionados nuevos.

## 6. Gobierno y Git

Se verificó la creación desde `main` limpio y actualizado de infra conforme a WORKFLOW
§2.1. Backend y frontend se verifican en solo lectura. Los detalles operacionales de Git
se entregan en la sesión, sin incorporarlos como estado durable conforme a §6.1.
El usuario aprobó este mantenimiento el **2026-10-01** mediante
`approved: Task/030.2-Corregir-Drift-Documental-Post-Merge`. No hay ADR ni decisiones
arquitectónicas que promover. **DT-030-URLLIB3 sigue abierta** y Task/031 sigue
**Pendiente, no iniciada**; los contadores no cambian con esta aprobación.

## 7. Enmienda H-030.2-CI-Alpine-repair

Enmienda **posterior a la aprobación y previa al merge**, autorizada mediante
`authorize: Task/030.2 H-030.2-CI-Alpine-repair` en la misma rama y el mismo PR. No
sustituye la aprobación de §6 ni reabre el alcance documental. Con CI Infra en verde, el
usuario aprobó el entregable enmendado el **2026-10-01** mediante una nueva expresión exacta
`approved: Task/030.2-Corregir-Drift-Documental-Post-Merge`.

### 7.1. Causa raíz: deriva externa del índice de Alpine

CI Infra falló, en `push` y en `pull_request`, en *Build the project images*, al construir
PostgreSQL: `apk` respondió `unable to select packages` porque la base trae
`libcrypto3`/`libssl3` 3.5.7-r0 y el Dockerfile exigía **3.5.8-r0**, que el índice ya no
ofrecía. Los pasos anteriores pasaron. El workflow, ambos Dockerfiles y `.env.example` eran
idénticos en `main`, y el CI verde de `main` del 2026-09-30 había instalado ese mismo
3.5.8-r0: **la causa no es el cambio documental**.

La causa es externa. El 2026-09-30, `3.24-stable` de aports publicó
`main/openssl: security upgrade to 3.5.9`: solo cambian `pkgver` y la suma del tarball.
OpenSSL 3.5.9 es una *security patch release*, de severidad máxima High, con trece CVE.
Desde ambas bases fijadas —PostgreSQL y Traefik, Alpine 3.24.1, apk-tools 3.0.6— el
índice firmado de v3.24 ofrece únicamente `libcrypto3`/`libssl3` **3.5.9-r0** y `libuuid`
**2.42.3-r1**. Traefik fijaba también 3.5.8-r0: habría fallado igual en cuanto PostgreSQL
avanzara.

### 7.2. Alternativas evaluadas

| Criterio | A — conservar 3.5.8-r0 | B — adoptar 3.5.9-r0 |
| --- | --- | --- |
| Seguridad | Fija a propósito una versión con trece CVE corregidos aguas arriba | Corrige esos trece CVE; sucesor directo de la misma rama |
| Reproducibilidad | **No**: 3.5.8-r0 responde 404 en un espejo sin caché; `dl-cdn` solo lo sirve desde caché. Ya ocurrió con 3.5.5, 3.5.6 y 3.5.7, hoy 404 | Sí, mientras el índice de v3.24 lo ofrezca; el pin exacto vuelve a fallar cerrado cuando avance |
| Autenticidad | Exigiría URL directas a `.apk` fuera del índice: cadena nueva sin garantía de permanencia | Índice firmado oficial, el mismo mecanismo de confianza que estableció Task/018 |
| Mantenimiento | Repetir el problema en cada poda del espejo | Actualizar el pin cuando avance la rama, tras build y S-09 |
| Cambio | Nuevo mecanismo de instalación | Dos líneas, una por Dockerfile |

**Elegida: B.** A falla en seguridad y en reproducibilidad, de forma independiente;
evaluar la firma de un `.apk` suelto pierde sentido si el archivo deja de existir.
B no retrocede a 3.5.7, mantiene juntos `libcrypto3` y `libssl3` y deja `libuuid`
2.42.3-r1 sin cambios.

### 7.3. Validación local antes del commit

| Gate | Resultado |
| --- | --- |
| Build real de PostgreSQL, `--no-cache --pull`, base de `.env.example` | **PASS**: 3.5.7-r0 → 3.5.9-r0 en ambas; `libuuid` 2.42.1-r0 → 2.42.3-r1 |
| Build real de Traefik, mismo método | **PASS**: 3.5.7-r0 → 3.5.9-r0 en ambas |
| Versiones dentro de las imágenes | PostgreSQL: `libcrypto3`/`libssl3` 3.5.9-r0, `libuuid` 2.42.3-r1. Traefik: `libcrypto3`/`libssl3` 3.5.9-r0. Alpine 3.24.1 |
| Endurecimiento de Task/018 | Sin `gosu`; `USER postgres` (uid 70) y `65532:65532`; `/backup` de `postgres` y escribible en un volumen nuevo |
| Arranque endurecido —`read_only`, `cap_drop: ALL`, `no-new-privileges`— | PostgreSQL 17.11 con SCRAM sobre TCP, `pgcrypto` —SHA-256, CSPRNG y cifrado simétrico— y `uuid-ossp`; Traefik v3.7.13 con la configuración del proyecto y `/ping` OK |
| Trivy 0.74.0, DB del 2026-10-01 | PostgreSQL **0** hallazgos de cualquier severidad; Traefik **0** HIGH/CRITICAL —2 MEDIUM y 4 LOW de OpenTelemetry en el binario Go de la base fijada, ajenos a OpenSSL— |
| Derivado MinIO sin caché | `verify` con el **mismo digest** del baseline; `attest`, SBOM canónico y provenance correctos |
| Gate S-09 completo, seis entradas del baseline | **CORRECTO**: PostgreSQL y Traefik 0; MinIO 10/10, Portainer 4/4, Floci 2/2 y Terraform 9/9 exactas; **0 nuevas, 0 ya no presentes**; provider AWS 0 accionables |
| Gates infra | Terraform fmt/init/validate en los cuatro roots, con `test` en tres —9, 5 y 7—; suites OIDC 60, `terraform_state` 12, laboratorio 236 y `security` 88; ambos Compose; 0 scripts shell; PowerShell 6/6; Python 18/18; Gitleaks del entregable y del historial; `git diff --check` |
| Gate documental de 030.2 | Repetido sobre `main` como base: **30 aprobadas, 11 pendientes**, Task/031 Pendiente, 0 enlaces rotos, Account ID real 0, historia preservada |

Los gates de §5 eran documentales y no construían imágenes; por eso no podían anticipar
la deriva. Los binarios sueltos de Terraform y del provider se escanearon con el Trivy
Linux 0.74.0 del workflow, verificado por SHA-256, porque la compilación para Windows no
inventaría binarios Go en `rootfs`.

### 7.4. Alcance y gobierno

Archivos de la enmienda: `docker/postgres/Dockerfile` y `docker/traefik/Dockerfile`, más
el registro durable en [NFR](../architecture/non-functional-requirements.md#1-seguridad),
STATUS, ROADMAP, la ficha —§21— y este reporte. **Sin cambios** en workflow,
`security/vulnerability-baseline.json`, `.env.example`, scripts, MinIO, backend, frontend,
AWS ni Terraform; ningún gate relajado ni baseline ampliado. La evidencia del CI remoto
se entrega en la sesión, conforme a §6. Avance sin cambios: **30/41 ≈ 73 %**, ETAPA 10
**1/7 ≈ 14 %**, Task/031 **Pendiente, no iniciada**.
