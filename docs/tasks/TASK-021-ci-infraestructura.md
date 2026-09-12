# TASK-021 — CI Infraestructura

| Campo | Valor |
| --- | --- |
| **Identificador / rama** | `Task/021-CI-Infraestructura` |
| **Nombre** | CI Infraestructura |
| **Etapa** | ETAPA 06 — Integración Continua |
| **Estado** | **En progreso** — revalidación autorizada con MinIO desde Quay; mismo release y mismo digest |
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
scripts, auditoría histórica de los tres repositorios y controles negativos
locales, registrados en el reporte. **Durante la detención histórica en
B-021-3, el workflow y el gate todavía no estaban implementados.** Tras la
decisión explícita del usuario del 2026-09-11 se implementaron y se obtuvieron
las ejecuciones históricas registradas en el reporte. La revisión posterior
detectó un defecto funcional de identidad; esos runs no certifican su
corrección. **D-021-A corregida** preservando esta cronología. En la
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

La matriz inicial, pendiente durante la detención, se ejecutó después
(reporte §U). La regresión del comparador cubre cada campo de identidad,
nombre y digest, baseline inválido/incompleto, informe ausente, tolerancia
cero, orden determinista y desaparición con aviso `baseline_stale`.

### 7.3 Tests RED esperados

Exit distinto de cero en cada negativo, seguido de restauración byte a byte
y GREEN. Durante la detención inicial no se habían ejecutado negativos;
la evidencia posterior está en el reporte §Q y §U. La nueva regresión se
ejecutó antes de corregir el comparador y reprodujo sus fallos.

### 7.4 Integración necesaria

Compose config no exige levantar servicios. CI real por `push`, dentro de
la excepción estrecha del usuario. Herramientas seleccionadas: Gitleaks
8.30.1 y Trivy 0.74.0, con SHA256 verificado.

### 7.5 Casos negativos y de seguridad

No publicar cambios deliberadamente rotos. El canary histórico se prepara
fuera de los tres repositorios; nunca se utiliza una credencial real.

### 7.6 Regresiones relevantes

Gates restaurados y archivos idénticos tras los negativos. La validación
de scripts operativos no debe ejecutar sus operaciones sobre el entorno.

## 8. Plan de validación

Los dos bloqueos documentales quedaron resueltos mediante autorización
explícita el 2026-09-10. El baseline se midió a continuación y quedó verde en
Compose, scripts y secretos del historial. Durante la detención posterior,
el diseño del workflow esperaba la decisión sobre **B-021-3**. El usuario
la tomó el 2026-09-11 y B-021-3 quedó **Resuelto**. Tras corregir la identidad,
se exige repetir todos los gates locales y obtener CI por `push` sobre el
HEAD corregido antes de declarar la tarea Lista para validación.

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

Durante la detención inicial el reporte solo acreditaba validación local:
CI todavía no existía. Después se registraron ejecuciones reales. Observado
el 2026-09-11 UTC mediante GitHub: `34605076928`, `push` sobre `4d47346`,
concluyó `success`. Es evidencia histórica del comparador heredado;
no certifica el comparador corregido ni sustituye la nueva ejecución exigida.

## 11. Riesgos

Confundir una limitación técnica pendiente con una decisión aprobada aún
abierta; declarar C/D = 0 sin terminar el barrido; presentar negativos locales
como remotos. La detención y la separación explícita de evidencia los acotan.

## 12. Decisiones técnicas

Durante el preflight inicial no se tomó ninguna decisión de implementación
o arquitectura. Las
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
PSScriptAnalyzer **considerado y no adoptado**. La identidad completa incluye
`VulnerabilityID`, paquete, `Severity`, `InstalledVersion` y `FixedVersion`;
se conservan además ámbito y ruta para distinguir los binarios. Cambiar
cualquier campo de un hallazgo accionable produce FAIL, incluida una rebaja
de CRITICAL a HIGH. El nombre y digest se validan antes de comparar findings.
**MinIO y Portainer no se actualizan** dentro
de esta tarea, y el backend **no se toca**.

## 13. Documentación creada o actualizada

Esta ficha, reporte, STATUS, ROADMAP, STAGE-06 e índice de reportes. NFR
permaneció intacto durante la detención histórica y se actualizó tras los
primeros runs. La corrección del comparador requiere nueva evidencia remota
para considerar S-09 infraestructura satisfecho.

## 14. Archivos modificados

Durante la detención inicial se modificaron **9 documentos** de infra,
enumerados en §Z del reporte. Compose, Dockerfiles y scripts quedaron byte
a byte idénticos tras aquellos negativos. Después se añadieron workflow,
baseline y comparador. La corrección autorizada añade regresiones permanentes
del comparador; no altera imágenes ni hallazgos aceptados.

## 15. Resultado de pruebas

*Evidencia histórica del 2026-09-11, previa a corregir el comparador:
ejecución **34604423915**, `push`, `success` en **51 s**, según el reporte heredado.*
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

## 21. Detención histórica durante la revalidación — 2026-09-11

**D-021-A y D-021-B Resueltas.** El comparador incluye los cinco campos
exigidos y tiene **13/13** regresiones sintéticas en verde. **El scan real es
RED (exit 1):** CVE-2026-56854 pasó de CRITICAL en el baseline a HIGH en
`usr/bin/minio`, `usr/bin/mc` y `portainer`, manteniendo paquete, versiones y
digests. Son tres identidades completas fuera del baseline y se exige FAIL.
Detalle exacto en el reporte §AG. No se ampliaron los hallazgos aceptados.

Se detuvo la revalidación conforme al apartado 15 del usuario. No se hizo
commit ni push de las correcciones, ni se obtuvo CI nueva. No se declara
C=0/D=0, S-09 infraestructura satisfecho ni Task021 Lista para validación.
B-021-3 conserva su resolución por decisión explícita; esta diferencia real
requiere tratamiento autorizado. Contadores intactos: **20/41**, ETAPA06 **2/3**.

## 22. Revisión humana del baseline — 2026-09-11

Después de la detención de §21, el usuario revisó y aceptó explícitamente
las tres reclasificaciones de CVE-2026-56854. Se sustituyeron únicamente
esas tres severidades CRITICAL por HIGH. Prueba estructural: todo el JSON
restante permanece igual, incluidas imágenes, digests y los otros findings;
**116 entradas** antes y después, sin duplicados añadidos.

La política estricta, el comparador corregido y sus expectativas se
conservan. **13/13** regresiones verdes. Scan real nuevo: Postgres y Traefik
**0 accionables**; MinIO **100** y Portainer **16**, todos con pertenencia
exacta, **0 fuera del baseline**, gate **exit 0**. Es aceptación temporal del
residual tras revisión humana, no corrección de la vulnerabilidad ni una
excepción automática para futuras rebajas. Evidencia en reporte §AH.

Se auditaron en GitHub los tres runs históricos de Task021. `34604423915`
corresponde a `4808d7c`; `34605076928`, a `4d47346`. Ambos son históricos y
no certifican la corrección. La entrega quedó acreditada por el nuevo run conforme de §24.

## 23. Validación reproducible del comparador corregido

Desde la raíz de infra, sin ejecutar scripts operativos:

```powershell
python -B -m unittest discover -s tests/security -p 'test_*.py' -v
docker compose --env-file .env.example --profile admin config --quiet
python -B scripts/security/vulnerability_gate.py --baseline security/vulnerability-baseline.json --reports tmp/task021-revalidation/reports-reviewed
git diff --check
```

El último comando del gate requiere informes Trivy recién generados para
las cuatro imágenes; el workflow describe su generación con Trivy 0.74.0
verificado. No sustituir el scan por fixtures. Resultados locales posteriores
a la revisión humana, enlaces, secretos y Criterion12 **C=0/D=0** en §AH
del reporte. La nueva CI remota se registra en §24 como hecho observado, después de existir.

## 24. Primer resultado conforme — antes del bloqueo de §25

[CI Infra 34636624843](https://github.com/jeffersondavila/personal-blog-infra/actions/runs/34636624843):
`push`, rama `Task/021-CI-Infraestructura`, SHA
`43c1bf20f3a75bca7d4cde294bae771c4f92acf3`, `completed/success`,
19/19 pasos registrados verdes, 0 skipped. Run **56 s**, job **52 s**.
Comparador estricto, 13/13 tests, 46 commits sin secretos, cuatro imágenes,
100/16 identidades aprobadas y **0 fuera del baseline**. Residual visible
116/116; log completo auditado con Gitleaks y patrones sensibles: **0**.

**TASK021 IMPLEMENTADA — LISTA PARA VALIDACIÓN.** S-09 infraestructura queda
satisfecho técnicamente por el gate real. B-021-3 y defecto del comparador
Resueltos; D-021-A/B Resueltas; revisión humana limitada a tres severidades.
C=0/D=0; no aprobada. Historial completo, regresiones y matriz literal en
reporte §AH–AK. Contadores **20/41**, ETAPA06 **2/3**.

**ETAPA 06 — CIERRE GLOBAL PENDIENTE DE EVIDENCIA AUTORIZADA:** faltan PR real
de infra, run sobre dev y broken push remoto deliberado, que no fue autorizado.
Las detenciones de §21 y los runs anteriores se conservan como historia.

## 25. Revalidación del commit documental: bloqueo externo

Observado el 2026-09-11 Guatemala / 2026-09-12 UTC: el run
[34663425054](https://github.com/jeffersondavila/personal-blog-infra/actions/runs/34663425054)
sobre `94c5e6779d1d00063567a3f93fb6b7fee4dda17d`, evento `push`, terminó
`completed/failure` en dos intentos. Docker Hub negó con `UNAUTHORIZED`
el acceso anónimo al mismo manifiesto de MinIO fijado por digest; una
comprobación independiente también devolvió HTTP 401.

Las 13 regresiones y los gates anteriores al scan pasaron. El inventario y
S-09 quedaron skipped tras fallar el scan. **Task021 Bloqueada:** no existe
verde sobre el HEAD final y no se reutiliza el primer run conforme de §24.
El reporte §AL conserva la evidencia exacta. *Registrado el 2026-09-12 UTC:*
la documentación del bloqueo quedó entonces sin commit y no se publicó otro
push con el fallo conocido; esa contención terminó con la autorización de §26.
No se cambiaron imágenes, baseline, política, settings ni secretos para
evitarlo.

Ese bloqueo se conserva como hecho histórico y **no se reescribe**. Lo
demostrado entonces es acotado: el acceso **anónimo** a **ese manifiesto**
devolvió **HTTP 401 / `UNAUTHORIZED`** durante esos dos intentos. No se
afirma que Docker Hub esté roto, se haya vuelto privado ni haya retirado
el repositorio.

## 26. Revalidación autorizada: MinIO desde Quay

Autorización explícita del usuario, recibida el 2026-09-11 (Guatemala):
sustituir el registro de origen de MinIO por **Quay**, sin tocar release,
digest, contenido OCI, `accepted_findings`, versión de MinIO ni Portainer.

La referencia pasa de `minio/minio` a `quay.io/minio/minio`. El resto de la
cadena permanece **carácter por carácter**:

`quay.io/minio/minio:RELEASE.2025-09-07T16-13-09Z@sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e`

El cambio toca **tres** archivos funcionales, con **una línea cada uno**:
[`docker-compose.yml`](../../docker-compose.yml),
[`.github/workflows/ci-infra.yml`](../../.github/workflows/ci-infra.yml) y
[`security/vulnerability-baseline.json`](../../security/vulnerability-baseline.json),
donde solo cambia el campo `reference`. `expected_digest`, `policy`, `risk` y
las **100** identidades aprobadas quedan intactas.

**Disponibilidad anónima.** La OCI Registry API de Quay respondió **HTTP 200**
sin cabecera `Authorization`, sin login y sin intercambio de token, para el
índice multiarch, el manifiesto `linux/amd64` y su configuración.

**Equivalencia de contenido demostrada.** Se comparó la imagen de Docker Hub
ya almacenada localmente, exportada con `docker image save` y sin *pull*,
contra los bytes recibidos de Quay: índice, manifiesto `amd64`, configuración,
los **9** layer digests, los **9** RootFS diff IDs, `architecture`, `os`,
`Created`, `Entrypoint`, `Cmd` y labels. Todos **idénticos**. Es el mismo
contenido OCI, no un reempaquetado.

**Identidad de hallazgos.** Trivy **0.74.0** escaneó Quay con el comparador
versionado: **100** aprobados, **100** accionables, **100** coincidencias
exactas, **0** solo en baseline, **0** solo en Quay, **0** identidades
cambiadas. El baseline **no se regenera**.

**Control negativo.** Un informe con `ArtifactName` de Docker Hub contra el
baseline aprobado de Quay se rechaza **antes** de comparar hallazgos, por
nombre de imagen inesperado. La comparación estricta no se relajó.

El residual **no se corrige ni se oculta**: siguen siendo los mismos **100**
hallazgos aceptados temporalmente bajo **R-018-3**, que permanece **ABIERTO**.
La referencia independiente de MinIO en la CI del backend **no entra en este
alcance** y se evaluará por separado, si resulta necesario, antes del cierre
global de ETAPA 06.

Esta sección registra la decisión y la evidencia local. **No declara verde
ninguna CI**: el run real sobre el commit de esta revalidación se registra en
el reporte cuando exista.
