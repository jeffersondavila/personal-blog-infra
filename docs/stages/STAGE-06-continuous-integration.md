# ETAPA 06 — Integración Continua

| Campo | Valor |
| --- | --- |
| **Número** | 06 |
| **Estado** | **3 de 3 tareas aprobadas (100 %)** — la etapa **no se declara completada**: **cierre técnico demostrado, pendiente de la aprobación** del mantenimiento Task020.3, **Lista para validación** con **B-020.3-C resuelto** |
| **Dependencias** | [ETAPA 05](STAGE-05-quality-security.md) |
| **Tareas** | 3 |
| **Aprobadas** | 3 |
| **Avance** | 100 % de sus tareas; **cierre de etapa pendiente** |
| **Hito que completa** | CI verde en los tres repositorios. |

---

## Objetivo

Automatizar la verificación de calidad en cada cambio de los tres repositorios, de modo
que ningún cambio roto llegue a `dev` ni a `main`.

## Por qué esta etapa existe

Las verificaciones de la Etapa 05 solo tienen valor sostenido si se ejecutan solas.
Aquí se convierten en una barrera automática, no en un ritual manual.

## Tareas

### `Task/019-CI-Frontend` — *Aprobada (2026-09-08)*

Lint, type-check, tests y build en GitHub Actions.

**Depende de:** `Task/018`. **Repositorio:** `personal-blog-frontend`; infra solo
documentación según WORKFLOW. [Ficha](../tasks/TASK-019-ci-frontend.md) ·
[Reporte](../task-reports/TASK-019-report.md).

Añade los gates vigentes de formato y auditoría npm. El build precede a los tests
para ejecutar las guardas SEO/P-05 sobre el artefacto. Un job, Node 22.23.2
coherente con Dockerfile, lockfile reproducible, caché npm, permisos de lectura
y sin secretos ni despliegue. Sus decisiones de implementación quedan
**vigentes** con la aprobación del 2026-09-08. **No hay ADR nuevo.**

*Observado el 2026-09-08 (Guatemala) / 2026-09-09 UTC:* la ejecución
**34305529115**, disparada por `push`, concluyó **`success`** en **79 s** —job de
**76 s**— con los once pasos declarados en verde, **704** pruebas en **75**
archivos y **0** vulnerabilidades. Esa ejecución acreditó el trigger `push`.

*Observado el 2026-09-09 UTC, durante el cierre aprobado:* el trigger
`pull_request` quedó acreditado por la ejecución **34308296565**, disparada por el
pull request `#12`, con conclusión **`success`**; y la ejecución **34308234554**,
disparada por `push` sobre `dev`, también concluyó **`success`**. Ambos triggers
del workflow del frontend tienen, por tanto, ejecución real registrada.

### `Task/020-CI-Backend` — *Aprobada (2026-09-10)*

Ruff, MyPy, Pytest, verificación de migraciones, build de imagen Docker y escaneo.

**Depende de:** `Task/018`. **Repositorios:** `personal-blog-backend` e infra
(documentación). [Ficha](../tasks/TASK-020-ci-backend.md) ·
[Reporte](../task-reports/TASK-020-report.md).

*Observado el 2026-09-09 (Guatemala):* se completó el preflight y se corrigió,
con autorización expresa, el avance heredado de esta tabla de 0 % a 33 %.
La lectura posterior detectó B-020-1, otra contradicción preexistente en README
backend §3, y se detuvo antes de implementar CI. También se detectó B-020-2
en el Total de ROADMAP. El usuario autorizó ambas correcciones y se aplicaron:
son D preexistentes resueltas durante el preflight. Task020 retomó En progreso.
Al registrar ese desbloqueo no se había obtenido todavía una ejecución real
de Task020 en Actions.

La lectura obligatoria posterior del 2026-09-09 detectó B-020-3 en el reporte
Task019: §H negaba su aprobación y §R conservaba el PR como abierto en presente.
Se detuvo Task020 antes de corregir esos párrafos. El desbloqueo requirió tratamiento
autorizado por el usuario. Después se autorizaron y corrigieron: B-020-3A (D) y B-020-3B (C) resueltas; Task020 retomó En progreso. No se reabren Task019/019.1.

*Implementación del 2026-09-10:* workflow `CI Backend` en cada `push` y
`pull_request`, un job secuencial en `ubuntu-24.04` con Python 3.12.14,
PostgreSQL y MinIO efímeros del propio runner, migraciones sobre el motor real,
la suite completa con `-W error` y escaneo de imagen con política *fail-closed*.
**R-14 queda resuelto** como propuesta: dos *locks* transitivos con hashes,
instalación `--require-hashes` y detección de desfase. El baseline destapó dos
defectos reales y preexistentes —la regresión de `anyio` y tres
vulnerabilidades con corrección en `httpx2`— y ambos se corrigieron, el segundo
con autorización expresa. Ejecuciones reales de Actions y su auditoría paso a
paso en el [reporte](../task-reports/TASK-020-report.md).

*Revisión previa a la aprobación, 2026-09-10:* a petición del usuario se
auditaron dos puntos y los dos resultaron ser contradicciones reales, ya
corregidas. **D-020-1**: la instalación local documentada usaba
`pip install -e ".[dev]"`, que vuelve a resolver transitivas y elude el propio
*lock* que la tarea declara como garantía; el alcance real quedó documentado por
entorno, con la razón técnica por la que los *locks* no son instalables en
Windows. **D-020-2**: una sobreafirmación atribuía SHA o digest a todas las
herramientas externas cuando `pip-audit` solo está fijado por versión exacta.
**D-020-3**: el texto afirmaba que `--require-hashes` implica `--no-deps`, y no
es así; la garantía viene de que el *lock* enumera el cierre transitivo, no de
desactivar la resolución. Las tres son defectos del texto, no de la
implementación, y ninguna reabre etapas anteriores.

*Aprobada el 2026-09-10* mediante `approved: Task/020-CI-Backend`. Avance de
aquel día: **20/41 — 49 %**; esa aprobación llevó la etapa a **2/3 — 67 %**,
sin completarla, y faltaba entonces `Task/021`. **R-14 cerrado**; **S-09 backend** satisfecho y **S-09 global**
abierto. Las decisiones **D-020-A** a **D-020-H** quedan **vigentes**, sin ADR
nuevo.

*Observado el 2026-09-10 UTC, durante y después del cierre aprobado:* el trigger
`pull_request` quedó acreditado por la ejecución **34489982595**, disparada por el
pull request `#15` sobre el head `22af3f1`, con conclusión **`success`**; y la
ejecución **34491446991, attempt 1**, disparada por `push` sobre `dev` con head en el merge
de normalización `5fedcb3`, también concluyó **`success`**. Las dos con sus **21**
pasos en verde, **1855** pruebas y **0** omitidas. Ambos triggers del workflow del
backend tienen, por tanto, ejecución real registrada.

**Criterion 12 de `Task/020` cierra en C = 0 y D = 0**, recalculado el 2026-09-10
por [`Task/020.1`](../tasks/TASK-020.1-correct-post-merge-documentation-drift.md):
la afirmación se escribió durante el cierre, cuando el resultado de la fusión
todavía no existía, y ese mantenimiento convirtió en hechos fechados las
afirmaciones de estado vivo que la fusión volvió falsas.

### `Task/021-CI-Infraestructura` — *Aprobada (2026-09-12)*

`docker compose config`, validación de scripts y escaneo de secretos.

> **Corrección de `Task/005.5`.** Esta tarea pertenece a la ETAPA 06 y **no existe todavía
> ningún archivo Terraform**: el primero lo crea `Task/025`, en la ETAPA 08. Declarar aquí
> `terraform fmt` y `terraform validate` produciría **checks permanentemente en verde por
> no tener nada que validar**, que es peor que no tenerlos: aparentan cobertura.
>
> Regla vigente: `Task/021` configura el CI de infraestructura **para los artefactos que
> existen en ese momento**, y **`Task/025` es responsable de ampliarlo** con `terraform
> fmt -check` y `terraform validate` cuando cree la IaC. Ese *ownership* futuro es
> explícito, no implícito.

**Depende de:** `Task/018`. **Repositorio:** `personal-blog-infra`.

*Observado el 2026-09-10 (Guatemala):* preflight y creación desde `main`
superados. La lectura canónica detectó **B-021-1** y **B-021-2**, dos
contradicciones de clase D en la ficha/reporte Task020.1. Se detuvo antes de
corregirlas y antes de implementar CI, conforme al prompt. El usuario autorizó
las correcciones el mismo día; se aplicaron y ambos bloqueos quedaron
**Resueltos**. Task021 retomó **En progreso**.

*Medido el mismo día, tras la reanudación:* inventario exacto —**1** Compose,
**2** Dockerfiles, **6** scripts PowerShell, **2** Python, **0** Bash/sh,
**0** Terraform—, baseline de Compose en **exit 0** sin warnings con los **7**
servicios cubiertos vía `--profile admin`, sintaxis de scripts sin errores, y
auditoría del historial de secretos de los **tres** repositorios con Gitleaks
8.30.1: **0** hallazgos en infra y frontend, y **2 falsos positivos
demostrados** en tests de redacción del backend. Cuatro controles negativos
locales en rojo y restaurados byte a byte.

**B-021-3, detectada y resuelta.** El gate de vulnerabilidades **no podía
quedar verde** con la política de Task020 aplicada tal cual: las dos imágenes
que el proyecto construye están en **0** hallazgos, pero `minio/minio` suma
**100** HIGH/CRITICAL con corrección aguas arriba y `portainer-ce` **16**, y la
imagen de MinIO **ya es la última publicada en Docker Hub**. El 2026-09-11 el
usuario autorizó la política definitiva: **tolerancia cero** en las imágenes
propias y **baseline exacto de riesgo aceptado**, ligado al digest y por
identidad de cada hallazgo, en las de terceros. El residual **no se corrige ni
se oculta**: se enumera en `security/vulnerability-baseline.json` y la CI falla
ante cualquier hallazgo accionable nuevo. Propietarios: **R-018-3** y
**R-021-1**. Evidencia en el
[reporte Task021](../task-reports/TASK-021-report.md) §M, §N y §Ñ.

**Revisión autorizada del 2026-09-11:** el comparador heredado excluía
`Severity` y `FixedVersion` de la identidad. Es un defecto funcional que
exigió un nuevo run conforme antes de acreditar S-09 infraestructura.
Ese run se obtuvo después: `34636624843`, sobre `43c1bf2`, `push`, success,
19 pasos verdes y 116 coincidencias exactas. El residual permanece aceptado
temporalmente; se sustituyeron solo tres severidades tras revisión humana. D-021-A/B se corrigen preservando la cronología.

*Evidencia histórica anterior a esa revisión, 2026-09-11 UTC:* el workflow **`CI Infra`** quedó implementado y
la ejecución **34604423915**, por `push` sobre `4808d7c`,
terminó en **`success`** en **51 s** con los **15** pasos declarados en verde (**18** registrados por GitHub): **7**
servicios de Compose, **26** variables, **6** scripts PowerShell, **3** Python,
**44** commits de historial sin hallazgos de secretos y **116** hallazgos de
imagen comparados sin ninguno fuera del baseline. La ejecución anterior,
**34604012128**, terminó en **`failure`** ante un cambio de severidad. La relajación aplicada
después se identificó como defecto funcional y requiere la corrección
autorizada; no es una excepción válida a la identidad completa. Logs auditados, **0** secretos.
[Ficha](../tasks/TASK-021-ci-infraestructura.md).

**Bloqueo intermedio y su resolución autorizada, 2026-09-12 UTC.** La CI del
commit documental `94c5e67`, run `34663425054`, terminó en **failure** en dos
intentos: el acceso **anónimo** a ese manifiesto de MinIO devolvió **HTTP 401 /
`UNAUTHORIZED`** y el scan no pudo completarse, de modo que el inventario y
S-09 quedaron `skipped`. Eso es lo único demostrado; no que Docker Hub esté
roto, privado o retirado. Con autorización explícita, la infraestructura pasó a
tomar la **misma imagen** desde **Quay**: mismo release, **mismo digest**
`sha256:14cea…`, contenido OCI comparado byte a byte —índice, manifiesto
`amd64`, configuración, 9 layers, 9 RootFS diff IDs, `Created`, `Entrypoint`,
`Cmd` y labels, todos idénticos— y **100/100** identidades del baseline, que
**no se regeneró**. El cambio ocupa **tres líneas**, solo el prefijo de
registro.

*Aprobada el 2026-09-12* mediante `approved: Task/021-CI-Infraestructura`.
Avance **21/41 — 51 %**; con ella la etapa alcanza **3 de 3 tareas aprobadas**
y **no se declara completada**. Las decisiones de la tarea quedan **vigentes**,
sin ADR nuevo: la política de S-09 de infraestructura, el registro de MinIO en
Quay por el mismo digest y la identidad estricta de siete campos. **S-09
infraestructura** satisfecho técnicamente por el gate aprobado; **el residual
de MinIO no se corrigió**: **100** hallazgos aceptados temporalmente bajo
**R-018-3**, que sigue **ABIERTO**, y **16** de Portainer bajo **R-021-1**.
Los criterios de salida siguientes no se relajan ni se dan por demostrados.

## Mantenimiento de reproducibilidad — Task020.3, 2026-09-12

**Bloqueada**, sin reabrir Task020 ni Task021 y sin añadir una tarea a las 41.
El control negativo remoto ya se ejecutó: `34710854803`, `push`, failure en
`Compose is valid`, 12 s; no se repite. El PR de infra quedó acreditado por
`34709782197` y su `dev` normalizado por `34711465394`, success, 50 s, 19/19 pasos.

El backend conserva el verde histórico `34491446991` **attempt 1** del
2026-09-10. El **attempt 2**, mismo SHA `5fedcb3`, falló el 2026-09-12 por la
descarga del manifiesto de MinIO desde Docker Hub. Task020.3 cambia solo el
registro a Quay. *Observado el 2026-09-12 UTC:* [run 34713222925](https://github.com/jeffersondavila/personal-blog-backend/actions/runs/34713222925),
push, `e8693eb`, attempt 1, **completed/failure**, 291 s. MinIO success en
5 s, migraciones y suite 1855/0 skipped/0 warnings en verde; ambos locks sin
vulnerabilidades conocidas. Falló el gate Trivy sobre la imagen backend:
**12 accionables (9 HIGH, 3 CRITICAL)**, exit 1. **B-020.3-C quedó abierto al
cierre de esa ejecución**, y la sesión se detuvo a pedir autorización.

Con la corrección autorizada —actualizaciones de seguridad de Debian en la etapa
`runtime` del Dockerfile backend, sin tocar Python, distribución base, digest
del `FROM`, locks ni la política S-09—, *observado el 2026-09-12 UTC:*
[run 34719123905](https://github.com/jeffersondavila/personal-blog-backend/actions/runs/34719123905),
push, `32c3992`, attempt 1, **completed/success**, 296 s, **25 de 25 pasos en
success**. MinIO desde Quay success en 4 s, migraciones 13 passed, suite
**1855 passed / 0 skipped / 0 warnings**, ambos locks sin vulnerabilidades
conocidas, inventario Trivy **149** en **Debian 13.7** con **CRITICAL 0**, y
gate accionable **0** con exit 0. **B-020.3-C resuelto.**

Con CI Frontend, CI Infra y CI Backend completas en verde, y el control negativo
remoto ya demostrado, **el cierre técnico de la etapa queda demostrado y
pendiente únicamente de la aprobación de este mantenimiento**. No se relajó
ningún criterio. Evidencia y trazabilidad en el
[reporte](../task-reports/TASK-020.3-report.md).

## Criterios de salida de la etapa

### Registro histórico al aprobar Task021 — 2026-09-12

Los párrafos y la matriz histórica de esta sección describen la evidencia y
los permisos existentes **antes** de ejecutar el cierre aprobado y el control
negativo posterior. No describen el estado vigente de Git/GitHub ni revocan
la autorización posterior. El seguimiento de Task020.3 figura arriba.

**Distribución de responsabilidades reconstruida en Task019:** cada repositorio
implementa sus triggers, gates, medición y revisión de logs en su tarea de CI.
S-09 frontend corresponde a Task019; backend a Task020; infraestructura a Task021.
El escaneo de secretos del historial está asignado explícitamente a Task021 y
se comprueba al cerrar la etapa; Task019 no afirma haber cubierto ese historial.
Task025 incorpora las verificaciones Terraform cuando existan archivos reales.

Los controles negativos locales se distinguen de la ejecución remota. En Task019,
el usuario autorizó el 2026-09-08 el bootstrap por push antes de aprobar; la
ejecución real de `pull_request` y el verde sobre `dev` quedaron comprobados
después, durante el cierre ordinario autorizado, con las ejecuciones citadas
arriba. Task020 siguió el mismo patrón el 2026-09-10, con su propia autorización
de bootstrap y sus dos ejecuciones posteriores al cierre. Publicar una mutación
deliberadamente rota exige un permiso adicional y **sigue sin autorizarse**.
Ninguna de estas observaciones completa por sí sola la etapa: los criterios de
salida exigen los **tres** repositorios. `Task/021` quedó **Aprobada el 2026-09-12**. Su historia intermedia se conserva: la CI `34663425054` sobre `94c5e67`
falló en dos intentos porque el acceso **anónimo** a ese manifiesto de MinIO
devolvió **HTTP 401**, hecho que no se reescribe, y el usuario
**autorizó** tomar la misma imagen desde **Quay** —mismo release, mismo digest
`sha256:14cea…`, contenido OCI idéntico y **100/100** identidades del baseline,
que no se regeneró—. *Observado el 2026-09-12 UTC:* los runs
[34669960835](https://github.com/jeffersondavila/personal-blog-infra/actions/runs/34669960835)
sobre `a6bd1ec` y
[34670245277](https://github.com/jeffersondavila/personal-blog-infra/actions/runs/34670245277)
sobre `a3434eb`, ambos por `push`, concluyeron **`success`** en **44 s** y
**42 s**, cada uno con **19/19** pasos, **116** identidades exactas, **0**
hallazgos fuera del baseline y **0** secretos. El primer
verde estricto se conserva como antecedente, no certifica ese HEAD final. La detención local del
2026-09-11 por tres identidades CRITICAL→HIGH de CVE-2026-56854 se resolvió
mediante revisión humana explícita y sustitución exclusiva de esas tres
severidades. El scan posterior fue GREEN, sin relajar el comparador. Su workflow
existe y tuvo un `push` histórico en **`success`** en **51 s** con la regla
defectuosa. La corrección sí queda acreditada por `34636624843`, no por
esa ejecución histórica. El criterio del escaneo del historial quedó
**auditado en lectura** sobre los tres repositorios y **automatizado** para
infra. *Registrado al aprobar la tarea, el 2026-09-12:* el `pull_request` de
infra y su verde sobre `dev` todavía no se habían ejecutado. Ambos pertenecen
a este cierre aprobado, que los produce **después** de este registro. Su
evidencia se conserva fuera del árbol versionado: encadenar un commit
documental por cada ejecución generaría a su vez nuevas ejecuciones, y ese
ciclo no aporta garantía alguna. El **control negativo remoto deliberado**
sigue **sin autorizarse**, y la expresión `approved:` no lo autoriza de forma
implícita.

- [ ] Cada repositorio ejecuta su workflow en cada push y pull request.
- [ ] Los tres workflows terminan en verde sobre `dev`.
- [ ] Un cambio deliberadamente roto hace fallar el workflow correspondiente.
- [ ] Ningún secreto aparece en los logs de CI.
- [ ] El tiempo de ejecución de cada workflow está documentado y es razonable.
- [ ] El escaneo de secretos cubre todo el historial disponible.
- [ ] **Ningún check pasa por no tener nada que verificar.** Si una verificación no aplica
      todavía, se declara explícitamente con la tarea que la incorporará.

### Matriz literal reconstruida al aprobar `Task/021` — 2026-09-12

| Criterio literal de STAGE-06 | Frontend | Backend | Infraestructura | Estado global |
| --- | --- | --- | --- | --- |
| Cada repositorio ejecuta su workflow en cada push y pull request. | Push `34305529115` y PR `34308296565`, success | Push `34488083060` y PR `34489982595`, success | Push `34670245277` sobre `a3434eb`, success; el `pull_request` se ejecuta durante este cierre | **Pendiente al aprobar: PR de infra** |
| Los tres workflows terminan en verde sobre `dev`. | `34308234554`, success | `34491446991`, attempt 1, success el 2026-09-10 | La integración en `dev` se ejecuta durante este cierre | **Pendiente al aprobar: infra sobre dev** |
| Un cambio deliberadamente roto hace fallar el workflow correspondiente. | Negativos locales, sin broken push autorizado | Negativos locales, sin broken push autorizado | Regresiones locales; `34604012128` fue un fallo real, no un broken push deliberado | **Pendiente: control remoto deliberado; no autorizado** |
| Ningún secreto aparece en los logs de CI. | Auditoría documentada en Task019 §K | Auditorías documentadas en Task020 y su cierre | Run `34670245277`: 538 470 bytes de log, patrones sensibles 0, Gitleaks 0 | **Verificado en las ejecuciones auditadas**, sin afirmar cobertura de todos los runs futuros |
| El tiempo de ejecución de cada workflow está documentado y es razonable. | Run de bootstrap 79 s | Run dev 334 s | Run 42 s; job 39 s | **Documentado**, según createdAt→updatedAt para los runs |
| El escaneo de secretos cubre todo el historial disponible. | Auditoría histórica Task021: 13 commits, 0 hallazgos | Auditoría histórica Task021: 19 commits, 2 falsos positivos demostrados | Gate con fetch-depth 0 y `--all`: 49 commits, 0 hallazgos | **Evidencia de auditoría en los tres**; automatización continua del historial solo en infra |
| **Ningún check pasa por no tener nada que verificar.** Si una verificación no aplica todavía, se declara explícitamente con la tarea que la incorporará. | Scripts npm inspeccionados y fuentes presentes; 704 tests/75 archivos en evidencia de Task019 | Tests y migraciones referenciados presentes; 1855 tests/0 omitidos en evidencia de Task020 | 7 servicios, 6 PS, 3 fuentes Python más 13 tests, 4 imágenes e historial real; Terraform queda en Task025 y Bash sin familia existente | **Verificado por inspección de artefactos y evidencia registrada**; no se añadió ningún check vacío |

La matriz se reconstruyó al aprobar `Task/021` el 2026-09-12. El bloqueo
intermedio de acceso a MinIO y el failure que produjo se conservan en la
historia de la tarea; la revalidación con Quay repara la dependencia sin
alterar ninguna casilla, porque no cambian ni la imagen ni sus hallazgos. Las
dos filas marcadas «Pendiente al aprobar» son precisamente las que este cierre
aprobado produce después del registro documental. La matriz
distingue evidencia fechada y automatización continua; su detalle,
metadatos de runs y auditorías están en el [reporte Task021](../task-reports/TASK-021-report.md).
**ETAPA 06 — 3 DE 3 TAREAS APROBADAS; CIERRE GLOBAL PENDIENTE DE EVIDENCIA
AUTORIZADA.** Las tres tareas de la etapa están aprobadas —Task019 el
2026-09-08, Task020 el 2026-09-10 y Task021 el 2026-09-12—, y **la etapa no se
marca completada**: son dos cosas distintas. El **control negativo remoto
deliberado** sigue **sin autorizarse** y ninguna aprobación de tarea lo
autoriza implícitamente. El `pull_request` de infra y su verde sobre `dev` se
producen dentro del cierre aprobado de `Task/021`, después del registro
documental de esa aprobación.

## Fuera del alcance de la etapa

- Despliegue automático (Etapa 11).
- Credenciales cloud y OIDC (Etapa 09).
- `terraform plan` contra una cuenta real (Etapa 09/10).

## Riesgos conocidos

| Riesgo | Mitigación |
| --- | --- |
| Consumo de minutos de GitHub Actions. | Workflows acotados, caché de dependencias, sin matrices innecesarias. |
| CI que falla de forma intermitente y se ignora. | Tests deterministas; cualquier fallo intermitente se trata como defecto. |
| Escaneos que bloquean por falsos positivos. | Lista de excepciones justificada y revisada. |

## Siguiente etapa

[ETAPA 07 — Validación Local](STAGE-07-local-validation.md)
