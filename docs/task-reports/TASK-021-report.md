# Reporte — TASK-021 · CI Infraestructura

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/021-CI-Infraestructura` |
| **Estado** | **Lista para validación** — local GREEN y CI estricta conforme el 2026-09-11; no aprobada |
| **Fecha de observación** | 2026-09-10 (Guatemala) |
| **Repositorio de trabajo** | `personal-blog-infra` |
| **Ficha** | [TASK-021](../tasks/TASK-021-ci-infraestructura.md) |
| **Avance aprobado** | **20/41 — 49 %**; ETAPA 06 **2/3 — 67 %**, En progreso |

## Reanudación autorizada — 2026-09-10

El usuario autorizó explícitamente corregir **B-021-1** y **B-021-2** dentro
de esta rama, sin crear otra maintenance. **Ambos Resueltos**: D documentales
heredadas, corregidas durante el preflight de Task021. Se modificaron solo
los pasajes equivalentes en ficha/reporte Task020.1 y reporte Task020; la
ficha Task020, que ya declaraba D-020-H vigente, se conservó intacta.

D-020-H sigue **Vigente**; la limitación Windows permanece documentada y las
alternativas Windows/universal no fueron adoptadas por Task020. No se
inventó owner, tarea futura, D ni ADR. La fila histórica de PR Task020.1
permanece intacta; se corrigió la afirmación de que sus documentos la omiten.

Validación previa a continuar, 2026-09-10: **9 documentos**, **295 destinos
de enlaces relativos, 0 rotos**, barrido acotado de patrones sensibles **0**,
`git diff --check` exit **0**, staging **0**, `main..HEAD` **0**. Auditoría
semántica de las cuatro fuentes indicadas por el usuario: **D-020-H Vigente**,
ninguna formulación equivalente pendiente y fila histórica de PR conservada.
**C = 0 y D = 0 respecto de B-021-1/2**. La ficha Task020 no fue modificada.

**Los apartados A y B conservan la evidencia de la primera detención del
2026-09-10**: las propuestas reproducidas son las de esa detención y el
resultado autorizado se registra aquí. **Los apartados C–AG recogen la
medición técnica ejecutada después**, el mismo día, tras la reanudación. Donde
un apartado registraba «no ejecutado» en la detención inicial, ahora consta el
resultado real y se indica así.

## A. Preflight Git

Medido el 2026-09-10, 20:54–20:55 de Guatemala. En los tres repositorios se
ejecutó `git fetch --prune origin`; todos estaban en `main`, limpios, con
staging vacío y sin ramas `Task/*` locales/remotas. `HEAD`, `main` y
`origin/main` coincidían en cada repositorio:

| Repo | HEAD = main = origin/main | dev = origin/dev |
| --- | --- | --- |
| infra | `d7136b29a906563af6edbae0b67dfac101c1f3fa` | `0f3856134d0d3b5f13dd0911bbba631b945cbcea` |
| backend | `8055878e415ace2bfc4e7685e0549c5ab8a642ef` | `5fedcb34f8f1542fcfb0957547e58f472529f6f2` |
| frontend | `7dce98aff239d61ae3ae15213d9a3f5ebf0fb8ce` | `b261e6542a7c5bbac0c6838ad8363574b0e97231` |

En infra: `git rev-list --count dev..main = 0`,
`git merge-base --is-ancestor main dev` exit **0** y diff de contenido vacío.
La consulta GitHub CLI de PR en cualquier estado con el head exacto Task021
devolvió `[]`; `ls-remote --heads` tampoco encontró esa rama.

Tras `switch main` y `pull --ff-only origin main` se repitieron las guardas;
la rama exacta nació de `main` a las **20:55:30**. Verificación inmediata:
`HEAD == main`, `main..HEAD = 0`, staging = 0. No se tomó un SHA heredado
como sustituto del preflight.

## B. Fuentes canónicas y motivo de detención

Leídos AGENTS.md, PROJECT_INSTRUCTIONS, WORKFLOW, DoD, STAGE-06, las fichas
Task019/020/020.1/020.2 y el reporte Task020.2. Se revisaron los apartados
pertinentes de STATUS, ROADMAP, NFR y security-boundaries, además del
inventario Git, Compose, `.env.example`, `.gitignore`, `.gitattributes` y
los dos Dockerfiles de infra. La lectura de los reportes Task020 y Task020.1
alcanzó los pasajes necesarios para confirmar los defectos de abajo.

**La lectura canónica no se declara completa.** Quedaron pendientes la
lectura íntegra de los reportes anteriores exigidos, la evidencia de Task018,
los scripts, runbooks y configuraciones consumidas. La detención precedió
al diseño y al baseline, como exigen los apartados **4** y **26** del prompt:
«Si encuentras una contradicción durable NUEVA: DETENTE antes de corregirla».

### B-021-1 — estado de D-020-H contradictorio (clase D)

Reproducido sobre el contenido heredado de la base `d7136b2`:

| Fuente | Pasaje |
| --- | --- |
| [Ficha Task020 §12](../tasks/TASK-020-ci-backend.md), líneas 168–179 | «D-020-A a D-020-H quedan vigentes» desde la aprobación. D-020-H define el alcance Linux del lock y la exclusión deliberada del `.venv` Windows |
| [Reporte Task020.1 §4 y §9](TASK-020.1-report.md), líneas 160 y 360 | Clasifica como A las decisiones D-020-A a D-020-H **vigentes** |
| [Ficha Task020.1 §7](../tasks/TASK-020.1-correct-post-merge-documentation-drift.md), líneas 177–178 | «D-020-H sigue anotada como decisión abierta» |
| [Reporte Task020.1 §10](TASK-020.1-report.md), líneas 375–376 | «D-020-H sigue anotada como decisión abierta» |

La contradicción es el **estado asignado al mismo identificador**, no la
existencia de la limitación Windows. Esa limitación puede seguir pendiente
sin reabrir la decisión aprobada que la documenta. Los dos pasajes de límites
no están presentados como citas del estado anterior a la aprobación; el
propio reporte de mantenimiento les contrapone la vigencia de la decisión.

**Propuesta registrada en la detención inicial (2026-09-10):** sustituir esas dos afirmaciones de
«decisión abierta» por:

> D-020-H está vigente desde la aprobación de Task020. Persiste la limitación
> documentada: el `.venv` de Windows no reproduce el árbol bloqueado. Incorporar
> un lock de Windows o universal requiere una decisión posterior; no se
> implementa en esta tarea.

Conservar R-15, R-17 y R-37, los hechos históricos y el alcance aprobado.
Las referencias del reporte Task020 a su revisión pre-aprobación se conservan
como **B**, sin convertirlas automáticamente en otro bloqueo.

### B-021-2 — autodescripción de Task020.1 incompatible (clase D)

En la [ficha Task020.1](../tasks/TASK-020.1-correct-post-merge-documentation-drift.md):

- Tabla inicial, línea **18**: su PR fue «creado durante el cierre aprobado
  del 2026-09-10»; remite a Git/GitHub para consultar el estado operativo.
- §5, líneas **147–150**: «No dicen que estén pendientes ni que hayan ocurrido:
  simplemente lo omiten» al describir lo que sus documentos dicen de su propio
  PR, rama y normalización.

El registro fechado del PR es **B válido** conforme a WORKFLOW §6.1. El
defecto **D** está en afirmar que ese hecho se omite cuando la propia ficha
lo registra. No se propone borrar el registro histórico ni cuestionar el PR.

**Propuesta registrada en la detención inicial (2026-09-10):** reemplazar el párrafo de §5 por:

> Sobre esta propia maintenance: sus documentos conservan hechos históricos
> fechados de su cierre. El estado operativo de ramas, PR y normalización se
> consulta en Git y GitHub. La regla de no persistirlo como estado vigente no
> exige omitir los hechos fechados; la normalización posterior es Git-only.

Durante la primera detención se propuso intervenir en ficha/reporte
Task020.1, dejando los originales intactos. La autorización posterior
exigió auditar también ficha/reporte Task020: el reporte contenía dos
formulaciones semánticamente equivalentes de B-021-1 y se corrigieron.
También se corrigió la autodescripción equivalente de §12 del reporte
Task020.1. No se creó otra maintenance ni se reabrió una aprobación.

## C. Alcance reconstruido

CI de los artefactos de infraestructura que **existen hoy**: Compose, scripts
PowerShell y Python, secretos del worktree y del historial, y la porción de
**S-09** que corresponde a infraestructura. Terraform pertenece a `Task/025` y
**no** se declara aquí como check vacío. Backend y frontend se auditan en
**solo lectura**.

## D. Inventario de infraestructura (A–L)

Medido el 2026-09-10 sobre `git ls-files`: **143** archivos versionados, de los
que **125** son Markdown y **18** son artefactos no documentales.

| Apartado | Resultado |
| --- | --- |
| **A. Compose y overrides** | **1**: `docker-compose.yml`. No existe override versionado ni presente en el árbol; `COMPOSE_FILE` no está definido |
| **B. Variables necesarias** | **26** referenciadas por el Compose; **26** declaradas en `.env.example`. Los dos conjuntos son **idénticos**: 0 faltantes y 0 sobrantes. **10** llevan valor por defecto en el propio Compose; **16** deben proveerse |
| **C. Imágenes externas** | **4**, todas con **tag + digest `sha256`**: `postgres:17.11-alpine`, `traefik:v3.7.13`, `minio/minio:RELEASE.2025-09-07T16-13-09Z`, `portainer/portainer-ce:2.39.7`. `postgres` y `traefik` entran como `ARG` de sus Dockerfiles; MinIO y Portainer se consumen directamente |
| **D. Dockerfiles** | **2**: `docker/postgres/Dockerfile` y `docker/traefik/Dockerfile`. Ambos parten de la base fijada por digest y aplican parches Alpine con versión exacta |
| **E. Scripts PowerShell** | **6**, todos en `scripts/backup/` |
| **F. Scripts Bash/sh** | **0**. Familia inexistente: **no se inventa un check para ella** |
| **G. Scripts Python** | **2**: `scripts/security/check_http.py` y `scripts/security/runtime_privileges.py` |
| **H. Otros artefactos** | `.editorconfig`, `.env.example`, `.gitattributes`, `.gitignore`, `docker/traefik/traefik.yml`, `docker/traefik/dynamic/routes.yml`, `images/Infraestructura.png` |
| **I. Workflows existentes** | **0**. `.github/` no existe todavía en infra |
| **J. Herramientas externas** | Disponibles y medidas en local: Docker **29.1.3**, Docker Compose **v5.0.1**, Python **3.12.10**, Windows PowerShell **5.1**, Git, GitHub CLI. `pwsh` **no** está instalado en la máquina; el runner de CI sí lo trae |
| **K. Sensibles ignorados** | Presentes y **correctamente ignorados**: `.env`, `secrets/`, `local-backups/`, `tmp/`. Ninguno versionado. **El `.env` real no se leyó ni se imprimió en ningún momento** |
| **L. Temporales que no deben entrar a CI** | Ninguno sin seguimiento salvo los dos documentos de Task021. `.gitignore` cubre datos, volúmenes, respaldos, logs, temporales y el futuro estado de Terraform |

**Terraform: 0 archivos `.tf` o `.tfvars`.** Confirma que `Task/025` es su
propietario y que aquí no corresponde ninguna verificación suya.

## E. Baseline de Compose

Ejecutado con **`--env-file .env.example`**, que además impide que Compose
cargue el `.env` real. Se comprobó en la salida que los valores resueltos son
los del ejemplo. **No se levantó, detuvo ni modificó ningún contenedor.**

| Medición | Resultado |
| --- | --- |
| `docker compose config` | exit **0**, **286** líneas, **0** warnings, **433 ms** |
| `docker compose config --quiet` | exit **0**, **0** warnings, **320 ms** |
| Con `--profile admin` | exit **0**, **0** warnings, **276 ms** |
| Archivos realmente cubiertos | **1**: `docker-compose.yml` |
| Servicios sin perfil | **6**: `postgres`, `minio`, `backend`, `frontend`, `traefik`, `portainer` |
| Servicios con `--profile admin` | **7**: los anteriores más **`migrations`** |
| Contextos de build ausentes | exit **0**: `config` **no** exige que existan |

**Hallazgo de diseño.** `migrations` declara `profiles: [admin]`, así que una
validación sin perfiles **lo deja fuera** y el gate quedaría parcialmente
vacío. El gate debe ejecutarse con `--profile admin`.

**Consecuencia para CI.** Los servicios `backend` y `frontend` construyen desde
`../personal-blog-backend` y `../personal-blog-frontend`, que **no existen** en
un runner que solo hace checkout de infra. Se comprobó que `config` termina en
**0** con esos contextos ausentes, de modo que el gate es viable sin clonar los
otros repositorios. Que `.env.example` baste como fuente de valores queda
**demostrado**, no supuesto.

## F. Inventario y validación de scripts

| Familia | Archivos | Método | Resultado |
| --- | --- | --- | --- |
| PowerShell | 6 | `[System.Management.Automation.Language.Parser]::ParseFile()` | **0 errores**, **1 134 ms** |
| Python | 2 | `compile(..., 'exec')` sobre el fuente | **0 errores**, **129 ms** |
| Bash/sh | 0 | — | No aplica: **no existe la familia** |

Ambos métodos son **análisis real, no ejecución**: ningún script de respaldo,
restauración o comprobación HTTP llegó a ejecutar sus operaciones. Se prefirió
`compile()` sobre `compileall` porque no escribe `__pycache__` en el árbol.

**PSScriptAnalyzer: no se adopta.** Exigiría descargar un módulo de PSGallery
sin digest verificable del artefacto, y aporta reglas de estilo más que de
validez sintáctica, que es lo que el gate necesita. Queda registrado como
alternativa considerada y **no adoptada**, no como decisión abierta.

## G. Estrategia de validación

Un gate por familia realmente existente, cada uno con su control negativo
local. Ninguna verificación se declara para artefactos inexistentes: Terraform
(`Task/025`) y Bash/sh (**0 archivos**) se nombran explícitamente en lugar de
producir un check que pasa por no tener nada que mirar.

## H. S-09 de infraestructura — reconstrucción

**NFR S-09** exige dos cosas: *versiones fijadas* **y** *escaneo de
vulnerabilidades en CI*. `security-boundaries` §13.4 es explícito en que
`Task/018` **no** afirma «cero vulnerabilidades» y en que sus auditorías fueron
**puntuales y fechadas**, por lo que caducan. STAGE-06 asigna la porción de
infraestructura a esta tarea.

Las «dependencias» de infraestructura son hoy, exactamente:

1. las **4 imágenes externas** del Compose;
2. las **2 imágenes que infra construye** sobre ellas;
3. las **herramientas externas** que la propia CI descargue.

| Mitad del requisito | Estado medido |
| --- | --- |
| Versiones fijadas | **Satisfecha.** Las 4 imágenes llevan tag **y** digest; **0** coincidencias de `:latest` o `:nightly` en todo el árbol versionado |
| Escaneo en CI | Evidencia histórica: **34604423915** en `success` sobre `4808d7c`, con el comparador defectuoso. La corrección exige nueva CI conforme |

## I. Escáner de secretos

**Gitleaks 8.30.1**, publicado el 2026-03-21, la última versión estable.
Descargado desde el release oficial y verificado contra
`gitleaks_8.30.1_checksums.txt`: **checksum correcto**. Se fija la versión
exacta; no se usa `latest`.

| Artefacto | SHA256 |
| --- | --- |
| `gitleaks_8.30.1_linux_x64.tar.gz` (destinado a CI) | `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb` |
| `gitleaks_8.30.1_windows_x64.zip` (medición local) | `d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e` |

Todas las ejecuciones usaron **`--redact=100`**. En ningún momento se imprimió
el valor de un hallazgo.

## J. Cobertura histórica de infra

| Medición | Valor |
| --- | --- |
| `HEAD` | `d7136b29a906563af6edbae0b67dfac101c1f3fa` |
| Refs locales y remotas | **6**; tags **0** |
| Commits alcanzables con `--all` | **158** |
| Commits sin merge | **44** |
| Commits escaneados por Gitleaks | **42** |
| **Hallazgos** | **0** |
| exit | **0**, en **1 214 ms**, ~3,50 MB |

**La diferencia de 2 está explicada y es completa:** `b894472` («commit inicial
del repositorio») tiene **diff vacío**, y `d08fe27` cambia **únicamente**
`images/Infraestructura.png`, un binario. Ninguno de los dos contiene texto que
pueda portar un secreto. Los commits de merge no aportan contenido propio: son
integraciones `--no-ff` de ramas Task ya cubiertas. Se verificó además que
`--log-opts` **sí** se aplica, contrastando `-n 1` y `-n 5` contra `--all`.

## K. Auditoría histórica de backend y frontend — solo lectura

| Repo | HEAD | Refs | Commits `--all` | Sin merge | Escaneados | Hallazgos | exit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `personal-blog-backend` | `8055878e415ace2bfc4e7685e0549c5ab8a642ef` | 5 | 65 | 20 | **19** | **2** | **1** |
| `personal-blog-frontend` | `7dce98aff239d61ae3ae15213d9a3f5ebf0fb8ce` | 5 | 50 | 14 | **13** | **0** | **0** |

### Los 2 hallazgos del backend son falsos positivos — demostrado

Regla disparada: **`generic-api-key`**, la heurística por entropía de Gitleaks.

| # | Archivo | Línea | Commit | Entropía |
| --- | --- | --- | --- | --- |
| 1 | `tests/test_endurecimiento_redaccion.py` | 14 | `deb4977` (2026-09-08, `Task/018`) | 3,84 |
| 2 | `tests/test_logging_redaccion.py` | 319 | `0210d1e` (2026-09-07, `Task/017`) | 3,92 |

Prueba, obtenida **sin imprimir ningún literal**:

- Los dos archivos son las pruebas de **`redactar_texto`**, la función que
  cumple **S-08**. El primer literal se asigna a una constante llamada
  `SECRETO`; el segundo grupo parametriza
  `test_redaccion_etiquetada_es_idempotente`.
- Los **4** literales implicados se buscaron en todos los archivos versionados
  del backend: cada uno aparece en **exactamente 1** archivo y **los 4 están
  dentro de `tests/`**. **0** apariciones fuera de las pruebas.
- Sus prefijos enmascarados corresponden a **nombres de cabeceras y campos**
  que la redacción debe reconocer, no a credenciales de un servicio.

**No hay secreto real. No se detiene la tarea por este motivo y no se modifica
el backend.** Queda registrado porque, el día que se añada escaneo de secretos
al CI del backend, esos dos hallazgos deberán tratarse con una *allowlist*
justificada y acotada a esos dos archivos de prueba, nunca con un *ignore*
general. **Propietario: la tarea que incorpore secret scanning al backend. No
es de Task021, que no puede modificar ese repositorio.**

**Backend y frontend quedaron intactos:** ambos en `main`, **0** cambios y el
mismo `HEAD` antes y después del escaneo.

## L. Control negativo del historial

Repositorio Git **temporal**, creado **fuera** de los tres repos, en el
directorio temporal de la sesión.

1. **Commit 1** — fichero de configuración con una credencial **sintética** con
   formato de clave de acceso AWS. Nunca una credencial real.
2. **Commit 2** — se retira el fichero del árbol de trabajo.

| Escaneo | Resultado | exit |
| --- | --- | --- |
| `gitleaks dir .` (solo árbol actual) | **no leaks found** | **0** |
| `gitleaks git . --log-opts="--all"` | **1 hallazgo**, 1 commit escaneado | **1** |

Queda demostrado lo que el criterio de STAGE-06 exige: **un escáner de sistema
de archivos no sustituye al escaneo del historial.** El repositorio temporal se
eliminó al terminar; los tres repos reales nunca se tocaron.

## M. Vulnerabilidades de las imágenes — medición

**Trivy 0.74.0**, la **misma versión** que el CI del backend ya usa. El SHA256
del tarball Linux se verificó contra los checksums oficiales y **coincide
exactamente** con el fijado en `ci-backend.yml`:
`2ae6fe3ee734b7fdf11335663e18c75ea12dccc76062f09f164a3b0f8be4371a`.

Medido el 2026-09-10 sobre las imágenes que el entorno ya tenía. **No se
construyó ninguna imagen y no se alteró ningún contenedor ni volumen.**

| Imagen | CRITICAL | HIGH | MEDIUM | LOW | **HIGH+CRITICAL con corrección** |
| --- | --- | --- | --- | --- | --- |
| `personal-blog-postgres:local` | 0 | 0 | 0 | 0 | **0** |
| `personal-blog-traefik:local` | 0 | 0 | 0 | 0 | **0** |
| `minio/minio:RELEASE.2025-09-07T16-13-09Z` | **8** | **98** | 101 | 16 | **100** |
| `portainer/portainer-ce:2.39.7` | **1** | **17** | 9 | 1 | **16** |

**Las dos imágenes que el proyecto construye están en cero.** Los parches
Alpine con versión exacta de los dos Dockerfiles funcionan y son verificables.
El problema está **únicamente** en las dos imágenes de terceros que se consumen
tal cual.

## N. B-021-3 — la detención del 2026-09-10 (histórico)

**Clase: técnica. Estado: RESUELTO el 2026-09-11** por decisión explícita
del usuario; la resolución está en §Ñ. Lo que sigue es la medición que motivó
la detención, conservada como hecho fechado.

Aplicar a infra el mismo gate *fail-closed* que `Task/020` dejó aprobado
—`--severity HIGH,CRITICAL --ignore-unfixed --exit-code 1`, sin `.trivyignore`,
sin umbral y sin excepciones— **falla hoy**: MinIO con **100** hallazgos y
Portainer con **16**. Se comprobó en ejecución real: exit **1**.

### Por qué no se resuelve actualizando

| Imagen | Mejor versión disponible | Hallazgos tras actualizar |
| --- | --- | --- |
| MinIO | **Ninguna.** La imagen que el proyecto usa **ya es la última publicada** | **100**, sin cambio |
| Portainer | `2.45.0` (2026-08-27) | **9**. Mejora, pero **no llega a 0** |

**MinIO no tiene salida por actualización.** El último release de GitHub,
`RELEASE.2025-10-15T17-29-55Z`, **no existe como imagen en Docker Hub**:
devuelve **HTTP 404**. El tag `latest` del registro apunta a
`RELEASE.2025-09-07T16-13-09Z`, **exactamente la que el proyecto ya fija por
digest**. La edición comunitaria dejó de publicar imágenes.

**Portainer tampoco llega a verde**, y saltar de la línea `2.39.x` a `2.45.0`
es un cambio de versión mayor sobre un componente **solo local** (**R-09**).

### Por qué Task021 no puede decidirlo

1. La imagen de MinIO está fijada **también** en el CI del backend
   (`ci-backend.yml`, `IMAGEN_DE_MINIO`). Cambiarla obliga a **modificar
   `personal-blog-backend`**, fuera del alcance de esta tarea.
2. Que MinIO haya dejado de publicar imágenes es una **decisión
   arquitectónica** —seguir, sustituir el almacenamiento S3 local o construir
   imagen propia—, no un ajuste de CI.
3. Las salidas que **no** se toman por iniciativa propia, porque el prompt las
   prohíbe: `|| true`, `continue-on-error`, `.trivyignore`, *ignore* general o
   un umbral inventado. **Ninguna se usó.**

**Consecuencia:** **S-09 infraestructura no queda satisfecho**, el workflow no
se escribe con un gate cuya forma depende de esta decisión, y **el bootstrap
remoto no se activa**, porque el §17 lo condiciona a una implementación local
completa con gates verdes.

## Ñ. B-021-3 — resuelto por decisión explícita del usuario (2026-09-11)

El usuario autorizó resolverlo dentro de esta rama. **No** se actualizó MinIO,
**no** se actualizó Portainer, **no** se tocó el backend y **no** se abrió una
decisión arquitectónica de sustitución.

### Ñ.1 Política adoptada

> **S-09 de infraestructura usa tolerancia cero para las imágenes construidas
> por el proyecto y baseline exacto de riesgo aceptado para imágenes
> third-party fijadas por digest. El baseline no oculta findings y la CI falla
> ante cualquier hallazgo accionable nuevo o digest no revisado.**

| Clase | Imágenes | Política | Baseline |
| --- | --- | --- | --- |
| Construidas por el proyecto | `personal-blog-postgres`, `personal-blog-traefik` | **Tolerancia cero.** Cualquier HIGH o CRITICAL con corrección publicada falla | **Vacío a propósito**, y debe seguir vacío |
| Terceros fijadas por digest | `minio/minio`, `portainer/portainer-ce` | Inventario completo y comparación por **identidad exacta** contra el riesgo aceptado | **100** hallazgos de MinIO, **16** de Portainer |

### Ñ.2 Identidad de un hallazgo

La política aprobada exige pertenencia exacta, con normalización explícita:

| Campo normalizado | Fuente Trivy / baseline v1 |
| --- | --- |
| `vulnerability_id` | `VulnerabilityID` / `id` |
| `package` | `PkgName` / `package` |
| `severity` | `Severity` / `severity` |
| `installed_version` | `InstalledVersion` / `installed_version` |
| `fixed_version` | `FixedVersion` / `fixed_version` |

Se conservan además `scope` y `package_path` del baseline para distinguir
copias en diferentes binarios. Las claves se ordenan antes de comparar;
no intervienen descripciones humanas ni conteos. El nombre exacto de la
imagen y su digest se comprueban antes de aceptar sus hallazgos.

`actual - approved` produce FAIL, incluido cualquier cambio de severidad,
versión instalada o versión corregida de un hallazgo accionable. Incluso
CRITICAL → HIGH requiere que la nueva identidad esté aprobada.
`approved - actual` genera `baseline_stale`, sin fallar por la desaparición.

La implementación heredada excluía `FixedVersion` y comparaba `Severity`
fuera de la identidad. **Eso era un defecto funcional, no una decisión
válida de B-021-3.** Su corrección fue autorizada el 2026-09-11 y no amplía
los hallazgos aceptados. Los runs anteriores no certifican esta corrección.

### Ñ.3 Generación y auditoría del baseline

Generado a partir de las mediciones del **2026-09-10** y **auditado contra un
escaneo nuevo del 2026-09-11** antes de adoptarlo, como exige la autorización:

| Imagen | Baseline (10-09) | Escaneo nuevo (11-09) | Entradas nuevas | Entradas ausentes | Coincidencia |
| --- | --- | --- | --- | --- | --- |
| `minio/minio` | 100 | 100 | **0** | **0** | **exacta** |
| `portainer/portainer-ce` | 16 | 16 | **0** | **0** | **exacta** |

El artefacto versionado es
[`security/vulnerability-baseline.json`](../../security/vulnerability-baseline.json).
**No se usó `.trivyignore`.** El archivo declara su propio `schema` y `version`,
la fecha de aceptación, la tarea que lo acepta, la política completa, y por cada
imagen su referencia, su digest esperado, el riesgo que la respalda y sus
hallazgos normalizados. No copia las descripciones extensas del scanner.

### Ñ.4 El comparador

[`scripts/security/vulnerability_gate.py`](../../scripts/security/vulnerability_gate.py),
**fail-closed**. Termina con código distinto de cero ante:

1. un hallazgo accionable que **no** esté en el baseline;
2. un **digest** distinto del revisado;
3. cualquier cambio de los cinco campos de identidad de un hallazgo accionable;
4. un informe del scanner **ausente o ilegible**;
5. un **baseline inválido**: schema, versión, política, digest o campos de
   identidad incompletos;
6. un baseline de tolerancia cero que **no** esté vacío;
7. una **severidad desconocida** dentro del propio baseline.

Un hallazgo que **desaparece** no rompe la ejecución: se informa como aviso,
porque una mejora no puede presentarse como fallo de seguridad. Queda anotado
para depurar el baseline en una revisión documental posterior.

El gate imprime siempre cuántos hallazgos comparó, por imagen y en total, de
modo que la comparación es demostrable y no un resultado opaco.

### Ñ.5 Resultado histórico sobre el escaneo real (antes de corregir el comparador)

| Imagen | Política | Observados | Aprobados | Nuevos | Ausentes | Resultado |
| --- | --- | --- | --- | --- | --- | --- |
| `personal-blog-postgres` | tolerancia cero | 0 | 0 | 0 | 0 | **correcto** |
| `personal-blog-traefik` | tolerancia cero | 0 | 0 | 0 | 0 | **correcto** |
| `minio/minio` | baseline aceptado | 100 | 100 | **0** | 0 | **correcto** |
| `portainer/portainer-ce` | baseline aceptado | 16 | 16 | **0** | 0 | **correcto** |

**116** hallazgos accionables comparados, exit **0**, en **538 ms**.

### Ñ.6 Esto es aceptación de riesgo, no ausencia de riesgo

MinIO y Portainer **contienen vulnerabilidades reales**. Este baseline **no las
corrige y no las oculta**: las enumera una a una, las mantiene visibles en el
inventario completo del workflow y bloquea cualquier regresión fuera de lo
aprobado. La redacción de los documentos y del propio gate evita decir «sin
vulnerabilidades» o «resueltas».

**Propietarios del residual:**

| Imagen | Riesgo | Tratamiento |
| --- | --- | --- |
| MinIO | **R-018-3**, ya existente | Se **actualizó su evidencia y su mitigación** con el baseline automático y con la medición de que no hay imagen más reciente. **No se creó un riesgo duplicado** |
| Portainer | **R-021-1**, nuevo y estrecho | No lo cubrían **R-09**, que trata el socket de Docker, ni **R-12**, que trata los respaldos sin cifrar. Registrado con la convención real de la sección de riesgos. **No se inventó un ADR** |

Razones de la aceptación, todas medidas: ambos son **solo local**, publicados
en **loopback**, con los controles ya existentes, **fuera de la arquitectura de
producción**; la actualización disponible **no elimina** el residual; el salto
de línea de Portainer afecta a un componente con **volumen persistente** y no
se hace aquí; y MinIO **no tiene una imagen oficial más reciente utilizable**.
Ninguna de estas mitigaciones elimina el riesgo, y no se presentan como si lo
hicieran.

### Ñ.7 MinIO en el backend

`personal-blog-backend` fija la **misma** imagen de MinIO en su CI. **No se
modifica.** Queda registrado como **deuda cruzada**: el día que MinIO se
actualice, los dos repositorios deberán moverse a la vez. El alcance de
`CI Infra` es la infraestructura de este repositorio.

## O. Workflow `CI Infra`

[`.github/workflows/ci-infra.yml`](../../.github/workflows/ci-infra.yml), **15
pasos** en un job `Infra quality` sobre `ubuntu-24.04`, con `timeout` de 30
minutos.

| Elemento | Valor |
| --- | --- |
| Disparadores | `push` y `pull_request`, sin filtros |
| Permisos | `contents: read`, nada más |
| Checkout | `actions/checkout` fijado por **SHA completo** `3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1) |
| Historial | **`fetch-depth: 0`**, imprescindible para el escaneo de secretos |
| Credenciales | **`persist-credentials: false`** |
| Secretos del proyecto | **Ninguno**. El workflow no los necesita ni los declara |
| Concurrencia | Cancela ejecuciones superadas de la misma referencia |
| Herramientas | Gitleaks **8.30.1** y Trivy **0.74.0**, ambas por versión exacta **y** SHA256 comprobado con `sha256sum --check --strict` |

### Las dos guardas de alcance no son checks vacíos

`Task/025` trae Terraform, y hoy no hay ningún `.tf`. En lugar de declarar un
check que pasa por no tener nada que mirar, el workflow **falla** en cuanto
aparezca el primer archivo de Terraform o el primer script de shell, y explica
qué gate hay que añadir antes de integrarlo. Es una comprobación con contenido
real: protege el criterio de STAGE-06 en vez de simularlo.

### Los gates

| Paso | Qué comprueba |
| --- | --- |
| `Compose is valid` | `config --quiet` con `--env-file .env.example` y **`--profile admin`**, que cubre los **7** servicios. Sin el perfil, `migrations` quedaría fuera |
| `Compose declares every variable it uses` | Las **26** variables del Compose están declaradas en `.env.example`. Falla si alguna falta |
| `PowerShell scripts parse` | Parser real sobre los **6** scripts. **Falla si no encuentra ninguno**, para que el gate no pueda quedarse vacío |
| `Python scripts compile` | Compilación real de los scripts de `scripts/`. Misma guarda contra el vacío |
| `No secrets in the full history` | Gitleaks sobre `--log-opts="--all"`, con `--redact=100` para que ningún hallazgo imprima su valor en un log |
| `Full vulnerability inventory` | Inventario **completo** de las 4 imágenes, sin filtrar por severidad y sin `--ignore-unfixed`. Es un informe: no lleva `--exit-code` y **no oculta nada** |
| `Image vulnerability gate (S-09)` | El comparador contra el baseline. **Este es el gate real** |

Las imágenes propias se **construyen en el workflow** con la misma base fijada
por digest que declara `.env.example`, de modo que se escanea lo que el
proyecto ejecuta, con sus parches aplicados, y no la base sin parchear.

## P. Ensayo local del workflow

Los pasos ejecutables se corrieron uno a uno en local antes de publicar nada.

| Paso | Resultado |
| --- | --- |
| Guarda de Terraform | **0** archivos. Correcto |
| Guarda de shell | **0** scripts. Correcto |
| Compose con `--profile admin` | **7** servicios, exit **0** |
| Variables declaradas | 26 y 26. Correcto |
| Scripts Python | **3** archivos, **0** fallos. Incluye el propio comparador |
| Scripts PowerShell | **6** archivos, **0** fallos |
| Gitleaks historial | **42** commits, **0** hallazgos, exit **0** |
| Gate S-09 | **116** comparados, exit **0** |

Se comprobó además que el YAML es válido, que los dos *heredoc* de Python
quedan correctamente desindentados al procesarse el bloque, y que las dos
imágenes propias se construyen **sin caché**: los parches Alpine con versión
exacta siguen disponibles aguas arriba, en **14,2 s** y **11,4 s**.

## Q. Control negativo F — evidencia histórica anterior a la corrección

Completado **sin introducir ninguna vulnerabilidad real en el proyecto**. Las
mutaciones se hicieron sobre **copias temporales** del informe normalizado y de
un baseline auxiliar, fuera del árbol versionado.

| # | Mutación | Esperado | Obtenido |
| --- | --- | --- | --- |
| **F1** | Hallazgo sintético `CVE-9999-00001` añadido al informe de MinIO | Rojo | **exit 1**, lo señala como nuevo y lo nombra |
| **F2** | Digest esperado sustituido por uno falso | Rojo | **exit 1**, imprime el esperado y el observado |
| **F3** | Baseline con `schema` desconocido | Rojo | **exit 2**, `schema desconocido` |
| **F4** | Informe de Portainer ausente | Rojo | **exit 2**, no puede comparar y no lo disimula |
| **F5** | Hallazgo sintético en una imagen **propia** | Rojo | **exit 1**, la tolerancia cero lo rechaza |
| **F6** | Hallazgo aprobado que **sube** de HIGH a CRITICAL | Rojo | **exit 1**, lo nombra e indica con qué severidad estaba aprobado |
| **F7** | Hallazgo aprobado que **baja** de CRITICAL a HIGH | Expectativa heredada incorrecta: verde | **exit 0** histórico; no satisface la política exacta. La nueva regresión exige RED |
| **Restauración** | Fixtures eliminados, baseline real | Verde | **exit 0**, 116 comparados |

Los fixtures temporales se eliminaron. El árbol versionado **nunca** contuvo un
estado roto.

## U. Controles negativos locales

| # | Control | Resultado |
| --- | --- | --- |
| **A** | Compose inválido | GREEN → **RED exit 1** (`yaml: line 102: did not find expected ',' or ']'`) → restaurado → GREEN |
| **B** | PowerShell inválido | GREEN → **RED exit 1** (`FAIL Test-LocalBackup.ps1`, 1 de 6) → restaurado → GREEN |
| **C** | Bash/sh inválido | **No aplica.** 0 scripts de esa familia; no se inventa |
| **D** | Python inválido | GREEN → **RED exit 1** (`'(' was never closed`) → restaurado → GREEN |
| **E** | Secreto solo histórico | **RED exit 1** en el historial y **exit 0** en el árbol. Demostrado |
| **F** | Gate S-09 *fail-closed* | **Completado el 2026-09-11 en cinco variantes**, detalladas en §Q. No se introdujo ninguna vulnerabilidad real en el proyecto |

**Restauración verificada por SHA256 en los tres casos mutados**: el archivo
vuelve **byte a byte** al original y `git status` no reporta ningún cambio sobre
artefactos funcionales. El árbol conserva exactamente los **9** documentos de
esta tarea.

## V. Bootstrap remoto

Con **B-021-3 resuelto** y los gates locales en verde, se cumplen las
condiciones de la excepción autorizada. La evidencia de la ejecución real
—identificador, resultado y duración— se registra en §V.1 cuando existe. No se
hizo merge a `dev`, ni pull request, ni publicación de ninguna mutación rota.

### V.1 Primera ejecución y defecto introducido después (histórico)

Observado y registrado el 2026-09-11 UTC: run **34604012128**, evento `push`,
rama `Task/021-CI-Infraestructura`, SHA `de3cb47`, conclusión `failure`.
El scanner reclasificó `CVE-2026-56854` sobre `golang.org/x/crypto` de
CRITICAL a HIGH en `usr/bin/mc`, `usr/bin/minio` y `portainer`.

El commit posterior `4808d7c` retiró `severity` de la identidad y permitió
rebajas; `fixed_version` ya estaba excluido. El reporte heredado presentó
esa relajación como una corrección. **La revisión posterior determinó que
era un defecto funcional del comparador:** la política aprobada exige
ambos campos dentro de la identidad y no permite aceptar una reclasificación
por iniciativa del agente. Se conserva el fallo remoto como evidencia
histórica, sin convertirlo en un broken push deliberado autorizado.

El usuario autorizó corregir el defecto dentro de Task021 el 2026-09-11,
con regresiones para cada campo. No autorizó regenerar el baseline para
aceptar diferencias reales nuevas ni actualizar MinIO o Portainer.

### V.2 Segunda ejecución: verde histórico del comparador defectuoso

*Observado el 2026-09-11 UTC.* Ejecución **34604423915**, evento `push`, rama
`Task/021-CI-Infraestructura`, SHA `4808d7c`. **`success`** en **51 s**, del
13:27:42 al 13:28:33 UTC (duración del job; el run completo duró 55 s). **15 pasos declarados en verde; la API registra 18 al incluir preparación
y limpieza del runner.**

| Gate | Resultado observado en el runner |
| --- | --- |
| Guarda de Terraform | 0 archivos. Sus verificaciones siguen siendo de `Task/025` |
| Guarda de shell | 0 scripts. No se declara un check para una familia inexistente |
| Compose | **7** servicios cubiertos: `backend`, `frontend`, **`migrations`**, `minio`, `portainer`, `postgres`, `traefik` |
| Variables del Compose | **26** usadas y **26** declaradas |
| PowerShell | **6** archivos, **0** fallos |
| Python | **3** archivos, **0** fallos, incluido el propio comparador |
| Secretos del historial | **44 commits** escaneados, **`no leaks found`** |
| Inventario de vulnerabilidades | Publicado completo para las 4 imágenes, sin filtrar |
| Gate S-09 | **116** hallazgos comparados, **0** nuevos, **0** escalados, **3** rebajas informadas como mejora |

**El escaneo del historial cubrió 44 commits, no 42.** La diferencia son los dos
commits propios de esta rama: en el runner existen y se escanean. Es la
comprobación de que `fetch-depth: 0` funciona y de que el gate mira el historial
real, no una copia superficial.

### V.3 Auditoría de los logs

Se descargó el log completo de la ejecución, **1 861 líneas**, y se revisó
entero.

| Comprobación | Resultado |
| --- | --- |
| Claves privadas, credenciales AWS, tokens de GitHub o Slack | **0 coincidencias** |
| Los valores de `.env.example` (usuarios y contraseñas de ejemplo) | **0 apariciones** |
| Cadenas enmascaradas | **2**, ambas de `actions/checkout`: su `token: ***`, ya redactado por GitHub, y la ruta del archivo temporal de credenciales, sin valor |
| Hallazgos de Gitleaks con su valor expuesto | **0**. `--redact=100` lo impide por diseño |

**Ningún secreto aparece en los logs de CI.**

## W. Logs y duraciones

**Duración histórica del job, no del run completo:** el job `Infra quality`
tardó **51 s** en la ejecución verde **34604423915** y **36 s** en la fallida
**34604012128**. Es un tiempo razonable y comparable al de los otros dos
repositorios: 79 s el frontend y 295 s el backend, que además levanta servicios.

Las duraciones de la tabla siguiente son **mediciones locales** y se presentan
como tales, **nunca** como tiempos de CI.

| Operación local | Duración |
| --- | --- |
| `docker compose config` | 433 ms |
| `docker compose config --quiet` | 320 ms |
| `docker compose --profile admin config --quiet` | 276 ms |
| Parser PowerShell, 6 archivos | 1 134 ms |
| Compilación Python, 2 archivos | 129 ms |
| Gitleaks historial infra | 1 214 ms |
| Gitleaks historial backend | 944 ms |
| Gitleaks historial frontend | 724 ms |
| Trivy, 4 imágenes | de 252 ms a 12 362 ms |

## X. Matriz histórica de criterios de STAGE-06 (previa a la corrección)

| Criterio literal | Frontend | Backend | Infra | Estado global |
| --- | --- | --- | --- | --- |
| Workflow en cada push y pull_request | Registrados push `34305529115` y PR `34308296565` | Registrados push `34488083060` y PR `34489982595` | **Declarado**; `push` demostrado con `34604423915`. **`pull_request` sin ejecutar**: no se crea PR antes de aprobar | **Sin demostrar en los tres** |
| Los tres verdes sobre `dev` | Registrado `34308234554` | Registrado `34491446991` | **Sin ejecución sobre `dev`**: la integración pertenece al cierre aprobado | **Pendiente** |
| Un cambio roto hace fallar el workflow | Negativos locales | Negativos locales | **Negativos locales A, B, D, E y F**, más un **fallo remoto real**: `34604012128` en `failure` por el gate S-09 | **Demostrado en local y, para infra, también en remoto**; el broken push deliberado sigue sin autorizarse |
| Ningún secreto en los logs de CI | Evidencia previa | Evidencia previa | **Auditado**: 1 861 líneas, 0 secretos, 0 valores de `.env.example` | **Verificado para infra**; frontend y backend conservan su evidencia previa |
| Duración documentada | 79 s (push de bootstrap) | 334 s sobre `dev` | **51 s** | **Documentada en los tres** |
| El escaneo cubre todo el historial | **Auditado por Task021: 13 commits, 0 hallazgos** | **Auditado por Task021: 19 commits, 2 falsos positivos demostrados** | **Automatizado**: 44 commits en cada ejecución, 0 hallazgos | **Automatizado solo en infra**; en frontend y backend es auditoría fechada, no gate |
| Ningún check vacío | Pendiente de inspección | Pendiente de inspección | **Cumplido**: Terraform y Bash/sh son **guardas activas** que fallan si aparece el artefacto, y los gates de scripts fallan si no encuentran ninguno | **Pendiente** en los otros dos |

En esa matriz, los IDs de frontend y backend eran **evidencia documental
heredada**, sin nueva consulta remota. Los tres runs de infra se auditaron
posteriormente en GitHub: metadatos exactos y contexto en §AH.

**ETAPA 06 no se declara completada.** Para infra faltan la ejecución de
`pull_request` y el verde sobre `dev`, que pertenecen al cierre aprobado, y el
control negativo remoto deliberado, que **sigue sin autorizarse**. Para frontend
y backend falta inspeccionar sus workflows contra el criterio de «ningún check
vacío» y automatizar el escaneo del historial, hoy solo auditado.

## Y. Estado de S-09 global registrado antes de detectar el defecto

Frontend y backend conservan sus porciones aprobadas. **Infraestructura tiene
ahora las dos mitades**: versiones fijadas por tag y digest, y escaneo
automatizado en `CI Infra` con la política de §Ñ.
`non-functional-requirements.md` **queda actualizado**, ya con la ejecución
remota que lo demuestra. **S-09 global** sigue **abierto** hasta que la
aprobación cierre la porción de infraestructura.

## Z. Documentación de la implementación inicial

| Archivo | Acción |
| --- | --- |
| `docs/tasks/TASK-021-ci-infraestructura.md` | Actualizado: alcance medido, B-021-3 y punto de detención |
| `docs/task-reports/TASK-021-report.md` | Actualizado: toda la evidencia de la medición técnica |
| `docs/project-management/STATUS.md` | Actualizado: tarea en curso y B-021-3; **contadores intactos** |
| `docs/project-management/ROADMAP.md` | Actualizado: estado de Task021; **contadores intactos** |
| `docs/stages/STAGE-06-continuous-integration.md` | Actualizado: avance y detención; **criterios de salida intactos** |
| `docs/task-reports/README.md` | Actualizado: índice |
| `docs/task-reports/TASK-020-report.md` · `docs/task-reports/TASK-020.1-report.md` · `docs/tasks/TASK-020.1-correct-post-merge-documentation-drift.md` | Corregidos por **B-021-1/2** con autorización explícita |

**Artefactos creados el 2026-09-11 al resolver B-021-3:**

| Archivo | Papel |
| --- | --- |
| `.github/workflows/ci-infra.yml` | Workflow `CI Infra`, 15 pasos |
| `security/vulnerability-baseline.json` | Baseline exacto de riesgo aceptado, 116 hallazgos |
| `scripts/security/vulnerability_gate.py` | Comparador *fail-closed* |

También se actualizó **R-018-3** con su evidencia y mitigación nuevas, y se
registró **R-021-1** para el residual de Portainer. **El backend y el frontend
no se tocaron.**

## AA. Criterion12 A/B/C/D declarado antes de la revisión

| Clase | Evaluación tras la medición |
| --- | --- |
| **A** | Reglas de ramas, aprobación, límites del bootstrap y vigencia de **D-020-H** conservadas. **Regla durable nueva:** la política de S-09 de infraestructura descrita en §Ñ.1 |
| **B** | Preflight fechado; primera detención conservada como historia; creación fechada del PR de Task020.1 intacta; mediciones de esta fase fechadas |
| **C** | **0.** Ningún estado vivo de Git o GitHub persistido en documentación. Las dos afirmaciones heredadas «`Task/021` sigue Pendiente y no iniciada», dentro de registros históricos de STATUS, quedaron **ancladas a su fecha** |
| **D** | **0.** B-021-1 y B-021-2 resueltos y verificados; la contradicción residual de §12 de la ficha, dejada por la edición parcial, corregida; separador de sección restituido en STATUS |

**Estado observado durante la detención previa a la decisión del usuario:**
B-021-3 era un hallazgo técnico medido, abierto y con decisión pendiente.
Posteriormente, con la autorización explícita del usuario del 2026-09-11,
**B-021-3 quedó Resuelto** mediante el baseline exacto de riesgo aceptado.
**D-021-B Resuelta:** se conserva la detención como historia, sin presentarla
como un bloqueo vigente.

## AB. Git de infra

*Observado el 2026-09-11:* rama `Task/021-CI-Infraestructura` con **2 commits**
sobre `main`, `de3cb47` y `4808d7c`, árbol limpio y staging vacío. La rama se
publicó en `origin` bajo la excepción de bootstrap autorizada. **No** se integró
en `dev`, **no** se creó pull request y **no** se tocó `main`. El estado
operativo posterior se consulta en Git y GitHub, no en este documento.

## AC. Integridad del entorno en la medición histórica inicial

**9** contenedores en ejecución antes y después, con el mismo estado. Los **5**
volúmenes del proyecto, intactos. **0** imágenes añadidas al demonio Docker por
los escaneos. El repositorio temporal del canary, eliminado. El `.env` real
nunca se leyó ni se imprimió.

## AD. Contadores

**20/41 — 49 %**; ETAPA 06 **2/3 — 67 %**, **En progreso**. **Sin cambio**:
Task021 está **Lista para validación**, no aprobada, así que **no suma**. No se
escribe 21/41, ni 3/3, ni «ETAPA 06 Completada». `Task/022` **Pendiente** y no
iniciada.

## AE. Bloqueos

| ID | Estado |
| --- | --- |
| **B-021-1** | **Resuelto** con autorización explícita el 2026-09-10 |
| **B-021-2** | **Resuelto** con autorización explícita el 2026-09-10 |
| **B-021-3** | **Resuelto** el 2026-09-11 por decisión explícita del usuario: baseline exacto de riesgo aceptado, sin `.trivyignore`, sin umbral por cantidad y sin excluir ninguna imagen |

**B-021-1/2/3 Resueltos.** D-021-A/B Resueltas; el defecto funcional
consistía en excluir severidad y FixedVersion de la identidad, no en
rechazar sus cambios. Quedó corregido con regresión permanente. La detención
posterior por tres diferencias reales y su revisión humana se conservan en
§AG–AH. La validación de la corrección quedó acreditada por el nuevo run de §AI.

## AF. Veredicto histórico, invalidado por la revisión del comparador

**TASK021 IMPLEMENTADA — LISTA PARA VALIDACIÓN.**

**ETAPA 06 — CIERRE GLOBAL PENDIENTE DE EVIDENCIA AUTORIZADA.**

Inventario, baseline de Compose, validación de las dos familias de scripts,
auditoría histórica de los tres repositorios, siete controles negativos y el
gate S-09 con baseline exacto de riesgo aceptado: **completados**. El workflow
`CI Infra` está implementado y su ejecución por `push` terminó en **`success`**
sobre el SHA exacto de la rama.

Lo que falta para cerrar la **etapa** no depende de esta implementación: la
ejecución de `pull_request` y el verde sobre `dev` pertenecen al cierre
aprobado, y el **control negativo remoto deliberado sigue sin autorizarse**.

**No aprobada.** No se hizo merge a `dev`, ni pull request, ni se inició
`Task/022`.

## AG. Corrección autorizada y detención histórica — 2026-09-11

**Estado observado durante esa detención, antes de la revisión humana de §AH.**
No había veredicto final de conformidad ni nueva aprobación. La revalidación se detuvo por tres identidades reales fuera del baseline,
detalladas al final. Faltan gates locales, Criterion12 y un nuevo run `push`
sobre el HEAD corregido. Los verdes históricos no
certifican el comparador nuevo; S-09 infraestructura requiere esa evidencia.
Contadores pre-aprobación: **20/41 — 49 %**, ETAPA 06 **2/3 — 67 %**.

### Auditoría del commit heredado, antes de editar

Observado el 2026-09-11 UTC mediante Git y GitHub, no inferido del reporte:
`HEAD = 4d47346a6360961929b47603619880975278b2f8`, rama
`Task/021-CI-Infraestructura`, árbol limpio, staging 0 y `main..HEAD = 3`.
`git ls-remote` devolvió ese mismo SHA para la rama Task publicada.

El commit contiene exclusivamente siete documentos: NFR, ROADMAP, STATUS,
STAGE-06, índice de reportes, ficha y reporte Task021; 170 inserciones y
50 eliminaciones. No cambia workflow, comparador ni baseline. Registró
los runs anteriores y presentó la tarea como Lista para validación.

La consulta con el SHA completo confirmó el run
[34605076928](https://github.com/jeffersondavila/personal-blog-infra/actions/runs/34605076928),
`CI Infra`, evento `push`, misma rama y SHA, `status=completed`,
`conclusion=success`; inicio `2026-09-11T13:34:26Z`, actualización final
`2026-09-11T13:35:07Z`. Se registra como hecho histórico; **no se reutiliza
para certificar la corrección**.

### Correcciones y regresión

- **D-021-A Resuelta:** las frases de la ficha sobre la no implementación
  y ausencia de CI quedan ancladas a la detención histórica.
- **D-021-B Resuelta:** la afirmación antigua de B-021-3 abierto queda
  temporalizada; **B-021-3 Resuelto** por decisión explícita del usuario.
- **Defecto funcional de identidad corregido en local:** cinco campos
  completos, orden determinista, nombre/digest previos a la comparación y
  desaparición con aviso. La aceptación temporal del residual no cambia.

Regresión permanente en
[`tests/security/test_vulnerability_gate.py`](../../tests/security/test_vulnerability_gate.py).
Primero se ejecutó contra el comparador heredado: **13 tests, 5 fallos**;
reprodujo la aceptación indebida de `FixedVersion`, rebaja de severidad y
nombre de imagen, y verificó la salida visible y el aviso de obsolescencia.
Después de la corrección: **13/13 GREEN**. Los tests usan informes sintéticos
en directorios temporales eliminados al terminar; ninguna imagen real se
modifica. La regresión se incorpora al workflow.

### Scan real nuevo: RED y detención obligatoria

Observado el **2026-09-11; escaneos a las 12:29 Guatemala / 18:29 UTC**:
Trivy **0.74.0**, ZIP Windows verificado por SHA256
`94c40e0696e4b907a74b7b2e1438d5d72ebaca83115817407f568a002d520842`.
Base de datos descargada de nuevo, sin reutilizar el cache heredado:
`UpdatedAt=2026-09-11T07:00:51.617232631Z`.
Los cuatro escaneos terminaron con exit 0; el comparador terminó con **exit 1**.

| Imagen / ubicación | VulnerabilityID | Paquete | InstalledVersion | FixedVersion | Baseline | Scan actual |
| --- | --- | --- | --- | --- | --- | --- |
| MinIO / `usr/bin/minio` | CVE-2026-56854 | `golang.org/x/crypto` | `v0.37.0` | `0.55.0` | CRITICAL | HIGH |
| MinIO / `usr/bin/mc` | CVE-2026-56854 | `golang.org/x/crypto` | `v0.40.0` | `0.55.0` | CRITICAL | HIGH |
| Portainer / `portainer` | CVE-2026-56854 | `golang.org/x/crypto` | `v0.54.0` | `0.55.0` | CRITICAL | HIGH |

**No es un VulnerabilityID nuevo ni una actualización de imagen.** Son tres
identidades completas reales no incluidas en el baseline: la política exacta
ordena FAIL también para esta rebaja de severidad. No se aceptaron por
iniciativa del agente. Los nombres y digests de MinIO y Portainer coincidieron
exactamente; las entradas `images` y `accepted_findings` permanecieron
idénticas a las de `4d47346`, comprobado por comparación estructural.

Postgres y Traefik: **0 accionables**. MinIO: **100** observados, **98**
coincidencias exactas, **2** fuera del baseline. Portainer: **16** observados,
**15** coincidencias exactas, **1** fuera. Las tres identidades CRITICAL del
baseline se informaron además como `baseline_stale`; el aviso no convierte
las nuevas identidades HIGH en aceptadas. Los conteos no se usan como permiso.

**Detención conforme al apartado 15 de la autorización.** No se completó la
revalidación general, no se afirma C=0/D=0 y no se hizo commit ni push de estas
correcciones. No hay CI nueva que las certifique. La prueba A con estado real
no obtuvo GREEN; tampoco puede declararse el GREEN final solicitado.
Los 13 tests sintéticos pasaron y sus fixtures temporales se eliminaron.
Los informes reales y el log se conservaron en `tmp/task021-revalidation/`,
ignorado por Git, como evidencia local; no contienen mutaciones sintéticas.
La revisión automática de aprobación rechazó la limpieza de la copia extraída
de Trivy y su cache temporal con el motivo `blocked by policy`. Esos artefactos
también permanecen dentro del mismo directorio ignorado; no se publicaron.

**B-021-3 sigue Resuelto** por la decisión explícita sobre la política;
no equivale a aprobar estas tres identidades distintas. D-021-A y D-021-B
están Resueltas. El defecto de identidad está corregido y cubierto por
regresión local; en esa detención la entrega completa quedó **Bloqueada**
por el scan real. La revisión humana posterior se registra en §AH.
MinIO y Portainer conservan el residual aceptado temporalmente, sin corregir.

No se emite el veredicto de implementación lista. ETAPA 06 conserva **2/3**
y el avance **20/41**. No se reconstruye una matriz final a partir de un run
heredado; quedan pendientes CI conforme y las evidencias globales autorizadas.

## AH. Revisión humana acotada del baseline — 2026-09-11

El 2026-09-11 una actualización de la base de datos de Trivy reclasificó
**CVE-2026-56854 de CRITICAL a HIGH** en tres ubicaciones, sin cambiar
VulnerabilityID, paquete, InstalledVersion, FixedVersion ni digest.
**El gate estricto la rechazó correctamente.** Después de revisión humana
explícita se actualizaron únicamente esas tres identidades del baseline.
**La política no se relajó: cualquier cambio futuro de identidad vuelve a
requerir revisión.** La vulnerabilidad no fue corregida; sigue siendo residual
real aceptado temporalmente bajo R-018-3 y R-021-1.

### Demostración estructural

La comparación anterior/posterior produjo exactamente estos tres cambios:

| Imagen | Scope | Paquete | InstalledVersion | FixedVersion | Severity |
| --- | --- | --- | --- | --- | --- |
| MinIO | `usr/bin/minio` | `golang.org/x/crypto` | `v0.37.0` | `0.55.0` | CRITICAL → HIGH |
| MinIO | `usr/bin/mc` | `golang.org/x/crypto` | `v0.40.0` | `0.55.0` | CRITICAL → HIGH |
| Portainer | `portainer` | `golang.org/x/crypto` | `v0.54.0` | `0.55.0` | CRITICAL → HIGH |

Se comparó el JSON completo, se revirtieron esas tres severidades en una
copia en memoria y se comprobó igualdad estructural con la entrada anterior.
Mismas cuatro imágenes, referencias, digests, riesgos, ubicación, package_path,
VulnerabilityID, paquetes y versiones; **116** accepted_findings antes y
después, sin duplicados añadidos. Ningún otro finding cambió. El texto de
política ya corregido en la reanudación anterior se conservó intacto.

El comparador y las expectativas de las pruebas no se modificaron en esta
revisión humana: SHA256 del comparador
`15c898abc8c1ac84e40d99301ecd2d856bb1701f7235ea74e701478596c98e8c`;
de las pruebas
`3365e59072850cae7aa08cd84b1e176aeaf9a4a492cc58ef59d80183e54541ff`.
Regresión permanente ejecutada nuevamente: **13/13 GREEN**, incluyendo
CRITICAL → HIGH sintético rechazado, FixedVersion cambiado rechazado y
desaparición aceptada con `baseline_stale`. No se cambiaron expectativas.

### Auditoría expresa de runs históricos desde GitHub

Consultado el 2026-09-11 mediante la API de GitHub. En los tres:
`workflow=CI Infra`, `event=push`, `headBranch=Task/021-CI-Infraestructura`,
`status=completed`. Ninguno certifica el comparador corregido.

| databaseId | headSha | conclusion | createdAt (UTC) | updatedAt (UTC) |
| --- | --- | --- | --- | --- |
| [34604012128](https://github.com/jeffersondavila/personal-blog-infra/actions/runs/34604012128) | `de3cb4788fe5177a60b6b74fafd4027d73e2352f` | `failure` | 2026-09-11T13:23:18Z | 2026-09-11T13:23:58Z |
| [34604423915](https://github.com/jeffersondavila/personal-blog-infra/actions/runs/34604423915) | `4808d7c46a3e9f62a3a4760d5a53aeef58788c68` | `success` | 2026-09-11T13:27:39Z | 2026-09-11T13:28:34Z |
| [34605076928](https://github.com/jeffersondavila/personal-blog-infra/actions/runs/34605076928) | `4d47346a6360961929b47603619880975278b2f8` | `success` | 2026-09-11T13:34:26Z | 2026-09-11T13:35:07Z |

**34604423915 pertenece a `4808d7c`, no a `4d47346`.** Su job duró
**51 s** y el intervalo createdAt→updatedAt del run, **55 s**.
**34605076928 pertenece a `4d47346`**: job **37 s**, intervalo del run **41 s**.
El primero verificó la relajación defectuosa de severidad; el segundo incluyó
la documentación heredada y el mismo comparador. **34604012128** pertenece a
`de3cb47`: job **36 s**, intervalo del run **40 s**; falló en S-09.

La API registra **18 pasos** en cada run histórico: **15 declarados** más
`Set up job`, `Post Checkout` y `Complete job`. En los verdes los 18 fueron
`success`; en el rojo falló S-09. Se distingue esta contabilidad para no
confundir pasos declarados con todos los registrados. La revisión agrega
una regresión permanente: el workflow corregido declara **16 pasos**.
No se reescribieron commits ni el mensaje histórico de `4d47346`.

### Medición local posterior a la revisión humana

Trivy **0.74.0**, archivo Windows y ejecutable verificados. Se usó la DB
`UpdatedAt=2026-09-11T07:00:51.617232631Z`, descargada el mismo día a las
18:28:40 UTC; el scan nuevo comenzó a las **18:51:59 UTC**. Las cuatro imágenes
se escanearon de nuevo. Después se construyeron también las dos imágenes
propias del workflow y se volvieron a escanear antes de validar el gate.

| Gate | Resultado local |
| --- | --- |
| Comparador, regresión permanente | **13/13 GREEN** |
| Postgres / Traefik | **0 / 0** accionables; tolerancia cero |
| MinIO | **100** accionables, **100** coincidencias exactas, **0** fuera del baseline |
| Portainer | **16** accionables, **16** coincidencias exactas, **0** fuera del baseline |
| S-09 con baseline revisado | **exit 0**, residual visible |
| Compose con `--profile admin` | **exit 0**, los **7** servicios |
| Variables Compose | **26** usadas, **26** declaradas, **0** faltantes |
| PowerShell | **6/6**, parser local 5.1; CI ejecuta su parser PowerShell 7 |
| Python | **4/4** fuentes: dos scripts previos, gate y test; sin ejecutar operaciones de respaldo |
| Gitleaks 8.30.1, historial `--all` | **45 commits**, **0** hallazgos |
| Terraform / Bash | **0 / 0** artefactos; guardas activas, sin verificaciones vacías |
| Builds de las dos imágenes propias | Ambos **exit 0**, mismas bases y parches fijados |
| YAML, triggers, permisos y checkout | Válidos; **16** pasos declarados |

El primer intento de validación adicional del YAML no disponía de PyYAML en
el Python del host; no fue un fallo del workflow. Se instaló **PyYAML 6.0.2**
exclusivamente en el temporal ignorado, con wheel verificado por SHA256
`7e7401d0de89a9a855c839bc697c079a4af81cf878373abd7dc625847d25cbd8`,
y la validación pasó. No es una dependencia nueva del repositorio ni de CI.
Trivy informó la ausencia de Alpine 3.24 en su lista de EOL y el uso de
severidades de distintos proveedores; sus escaneos finalizaron con exit 0
sin silenciar esos avisos ni convertirlos en excepciones del baseline.

Durante esa revalidación Task021 permaneció **En progreso** hasta completar
el barrido local y obtener el nuevo `push` conforme registrado en §AI.
La revisión humana del baseline no equivale a aprobación de la tarea.

### Barrido local previo al bootstrap de las correcciones

Ejecutado el 2026-09-11 tras aplicar la revisión humana y los gates anteriores:
**1359 destinos de enlaces relativos** comprobados en **127 archivos Markdown**,
**0 rotos**; **0** coincidencias de patrones sensibles. Dos cadenas
`![alt](access_url)` en ejemplos de código de Task015 se excluyeron como
código literal, no como enlaces renderizados; esos documentos no se tocaron.
Gitleaks 8.30.1 escaneó además una copia de los **149 archivos versionados o
no ignorados** del worktree: **0 hallazgos**. La copia excluyó los archivos
ignorados, por lo que no se leyó el `.env` real ni los secretos locales.
`git diff --check`: **exit 0**. Staging previo al bootstrap: **0**.

La comparación estructural del baseline volvió a pasar, así como los hashes
del comparador y de sus pruebas, sin modificar sus expectativas. No quedan
negativos activos. `tmp/task021-revalidation/` está ignorado, no aparece en
`git status` ni en `git ls-files`, y ningún temporal se incluye en el commit.
Su conservación fue autorizada expresamente; no bloquea la entrega.

**Criterion12 recalculado sobre la documentación afectada, 2026-09-11:**

| Clase | Resultado de la revisión |
| --- | --- |
| A | Reglas durables de ramas, aprobación, límites del bootstrap y política estricta conservadas; revisión humana acotada de tres severidades documentada |
| B | Creación de rama, detenciones, mediciones y los tres runs históricos con fecha y SHA correctos; ninguna evidencia histórica certifica por sí sola el comparador nuevo |
| C | **0**. Las referencias a ramas, PR, staging y normalización son reglas o mediciones fechadas, sin estado operativo persistido como vigente |
| D | **0**. D-021-A/B y defecto de identidad corregidos; estado pre-aprobación y distribución coherentes; semántica estricta común en ficha, reporte, baseline, NFR, STATUS y STAGE-06; runs reconciliados |

Los conteos de etapas anteriores se conservan como historia fechada. La
revisión no altera aprobaciones, R-14 ni el alcance de backend/frontend.
No se amplía una autorización por el resultado de una prueba. Solo procede
commit y push de la misma rama Task bajo la excepción explícita del usuario;
la aprobación, PR, integración en dev y broken push remoto no están incluidos.

## AI. CI nueva sobre las correcciones — 2026-09-11

Tras todos los gates locales GREEN, C=0/D=0 y staging 0, se creó el commit
`43c1bf20f3a75bca7d4cde294bae771c4f92acf3` y se publicó exclusivamente la rama
`Task/021-CI-Infraestructura`. Contiene D-021-A/B, el comparador estricto,
la regresión permanente y las tres severidades revisadas. No se integró dev,
no se creó PR ni se publicaron mutaciones deliberadamente rotas.

| Campo verificado desde GitHub | Valor |
| --- | --- |
| Workflow / databaseId | [CI Infra · 34636624843](https://github.com/jeffersondavila/personal-blog-infra/actions/runs/34636624843) |
| headSha | `43c1bf20f3a75bca7d4cde294bae771c4f92acf3` |
| event / headBranch | `push` / `Task/021-CI-Infraestructura` |
| status / conclusion | `completed` / `success` |
| createdAt / updatedAt | `2026-09-11T19:02:06Z` / `2026-09-11T19:03:02Z` |
| Duración del run | **56 s** |
| Job / duración | `Infra quality`, `19:02:09Z` → `19:03:01Z`, **52 s** |
| Pasos | **19/19 success**, **0 skipped**: 16 declarados y 3 de preparación/limpieza |

### Auditoría de todos los pasos y logs

Se verificaron las conclusiones de cada paso en la API de jobs y se descargó
el log completo, **1998 líneas**. No se utilizó ningún run anterior a la
corrección para certificarla. El cliente `gh` mostró `UNKNOWN STEP` al
etiquetar las líneas descargadas; los nombres y conclusiones se obtuvieron
de la API de jobs y los contenidos se verificaron contra sus salidas.

| Evidencia del runner | Resultado |
| --- | --- |
| Checkout | SHA correcto, credenciales no persistentes, historial completo |
| Integridad de herramientas | Gitleaks 8.30.1 y Trivy 0.74.0; ambos archivos SHA256 `OK` |
| Terraform y Bash | Guardas verdes, 0 artefactos; no hay fmt/validate o bash -n vacíos |
| Compose | 7 servicios: backend, frontend, migrations, minio, portainer, postgres, traefik |
| Variables | 26 utilizadas y 26 declaradas |
| PowerShell | 6 fuentes, 0 fallos; runtime 7.6.5 |
| Python | 3 fuentes compiladas, incluido el gate; runtime 3.12.3 del runner |
| Regresión del comparador | 13/13 GREEN, incluido el archivo de tests; 0.604 s |
| Gitleaks, historial `--all` | 46 commits, `no leaks found` |
| Builds / scans | Dos imágenes propias construidas y las cuatro imágenes escaneadas |
| Postgres / Traefik | 0 / 0 accionables; tolerancia cero |
| MinIO / Portainer | 100 / 16 coincidencias exactas; **0 fuera del baseline** |
| Residual visible | **116/116** identidades aprobadas localizadas literalmente en el log; nombres y digests exactos comprobados |
| Resultado S-09 | `RESULTADO: CORRECTO`, exit 0 |
| Secretos en logs | **0** patrones de claves/tokens y **0** hallazgos de Gitleaks 8.30.1 sobre el log completo |

El historial creció de 45 commits escaneados localmente a **46** en CI por
el commit de corrección. La clasificación HIGH de las tres entradas revisadas
aparece explícitamente en el log. No se corrigieron MinIO ni Portainer:
se preserva el residual real aceptado temporalmente.

**S-09 infraestructura técnicamente satisfecho por esta ejecución real**, con
Task021 **Lista para validación**, todavía no aprobada. Las evidencias globales
pendientes de STAGE-06 no se sustituyen por este run.

## AJ. Matriz literal de salida de STAGE-06 tras el nuevo verde

Reconstruida el 2026-09-11 después del run `34636624843`. Se consultaron
nuevamente desde GitHub los IDs de frontend y backend incluidos en la matriz:
los seis son `completed/success` con los eventos y ramas indicados. Sus
pruebas y auditorías de logs se citan desde los reportes de sus tareas;
Task021 no volvió a ejecutar pruebas de aplicación ni modificó esos repositorios.
La inspección en lectura de ambos workflows y sus scripts confirmó artefactos
reales: 192 fuentes TS/TSX en frontend y 112 fuentes Python bajo tests backend.

| Criterio literal de STAGE-06 | Frontend | Backend | Infraestructura | Estado global |
| --- | --- | --- | --- | --- |
| Cada repositorio ejecuta su workflow en cada push y pull request. | Push `34305529115` y PR `34308296565`, success | Push `34488083060` y PR `34489982595`, success | Push `34636624843`, success; PR real no ejecutado | **Pendiente: PR de infra** |
| Los tres workflows terminan en verde sobre `dev`. | `34308234554`, success | `34491446991`, success | Sin run sobre dev autorizado para estas correcciones | **Pendiente: infra sobre dev** |
| Un cambio deliberadamente roto hace fallar el workflow correspondiente. | Negativos locales, sin broken push autorizado | Negativos locales, sin broken push autorizado | Regresiones locales; `34604012128` fue un fallo real, no un broken push deliberado | **Pendiente: control remoto deliberado; no autorizado** |
| Ningún secreto aparece en los logs de CI. | Auditoría documentada en Task019 §K | Auditorías documentadas en Task020 y su cierre | Run `34636624843`: 1998 líneas, patrones sensibles 0, Gitleaks 0 | **Verificado en las ejecuciones auditadas**, sin afirmar cobertura de todos los runs futuros |
| El tiempo de ejecución de cada workflow está documentado y es razonable. | Run de bootstrap 79 s | Run dev 334 s | Run 56 s; job 52 s | **Documentado**, según createdAt→updatedAt para los runs |
| El escaneo de secretos cubre todo el historial disponible. | Auditoría histórica Task021: 13 commits, 0 hallazgos | Auditoría histórica Task021: 19 commits, 2 falsos positivos demostrados | Gate con fetch-depth 0 y `--all`: 46 commits, 0 hallazgos | **Evidencia de auditoría en los tres**; automatización continua del historial solo en infra |
| **Ningún check pasa por no tener nada que verificar.** Si una verificación no aplica todavía, se declara explícitamente con la tarea que la incorporará. | Scripts npm inspeccionados y fuentes presentes; 704 tests/75 archivos en evidencia de Task019 | Tests y migraciones referenciados presentes; 1855 tests/0 omitidos en evidencia de Task020 | 7 servicios, 6 PS, 3 fuentes Python más 13 tests, 4 imágenes e historial real; Terraform queda en Task025 y Bash sin familia existente | **Verificado por inspección de artefactos y evidencia registrada**; no se añadió ningún check vacío |

El criterio del historial se distingue de su automatización continua:
frontend y backend tienen una auditoría fechada, no un gate histórico en
sus workflows. La matriz no inventa autorización para modificarlos.

**ETAPA 06 — CIERRE GLOBAL PENDIENTE DE EVIDENCIA AUTORIZADA.** Faltan al menos
el PR real de infra, su run sobre dev y el control negativo remoto deliberado.
Este último sigue **NO autorizado**; el fallo histórico de S-09 no lo sustituye.
Las casillas literales de STAGE-06 no se marcan como cierre global de etapa.

## AK. Veredicto de implementación

**TASK021 IMPLEMENTADA — LISTA PARA VALIDACIÓN.**

B-021-3 Resuelto por decisión explícita; D-021-A/B Resueltas; defecto del
comparador Resuelto y cubierto por regresión; tres reclasificaciones revisadas
y aceptadas mediante sustitución acotada. C=0/D=0 en el barrido de la entrega;
contadores **20/41 — 49 %**, ETAPA06 **2/3 — 67 %**. No Aprobada.
La documentación conserva las detenciones y los runs como hechos fechados.
El estado operativo posterior se consulta en Git/GitHub, nunca se presume
por esta instantánea. No merge dev, no PR, no Task022.

Verificación posterior a registrar esta evidencia, antes del commit documental:
**1360 destinos relativos**, **127 Markdown**, **0 rotos**, **0** patrones
sensibles, Gitleaks del worktree **0**, historial **46 commits / 0 hallazgos**,
`git diff --check` limpio y staging **0**. C=0/D=0 revalidados; los únicos
cambios desde `43c1bf2` son siete documentos. Comparador, tests y baseline
permanecen idénticos a los que ejecutó `34636624843`.
