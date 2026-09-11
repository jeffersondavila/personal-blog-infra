# Reporte — TASK-021 · CI Infraestructura

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/021-CI-Infraestructura` |
| **Estado** | **En progreso** — B-021-1/2 resueltos; medición técnica completa; **B-021-3** abierto |
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
| Escaneo en CI | **Implementado** el 2026-09-11 en `CI Infra`, con la política de §Ñ. Se marca satisfecho cuando la ejecución remota lo demuestre |

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

La comparación **no** usa conteos. Un umbral por cantidad sería insuficiente:
podrían desaparecer cinco CVE y entrar otras cinco sin que el número cambie.
Cada hallazgo se identifica por:

| Campo | Papel |
| --- | --- |
| `scope` | Familia de paquetes del sistema, o ruta del binario dentro de la imagen |
| `id` | Identificador de la vulnerabilidad |
| `package` · `package_path` | Paquete afectado |
| `installed_version` | Versión presente en la imagen |
| `severity` | **Forma parte de la identidad**: si un hallazgo conocido sube de severidad, deja de estar aprobado y la CI falla |
| `fixed_version` | **Se registra, pero queda fuera de la identidad**: que el proyecto de origen publique otra versión corregida no es un riesgo nuevo, y convertirlo en rojo sería un falso positivo |

El `scope` de los paquetes de sistema se normaliza a la familia —por ejemplo
`os-pkgs:redhat`— en lugar de usar el `Target` crudo de Trivy, que incluye el
texto completo de la etiqueta de la imagen. Así el baseline no queda atado a
cómo se escribió el tag. Los paquetes de lenguaje conservan su ruta, que
distingue dos copias del mismo CVE: en MinIO, `usr/bin/minio` y `usr/bin/mc`.

Con esta identidad, las **100** entradas de MinIO y las **16** de Portainer son
**únicas**, sin colisiones, y coinciden exactamente con los hallazgos
accionables medidos.

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
3. una **severidad mayor** en un hallazgo conocido, porque cambia su identidad;
4. un informe del scanner **ausente o ilegible**;
5. un **baseline inválido**: schema, versión, política, digest o campos de
   identidad incompletos;
6. un baseline de tolerancia cero que **no** esté vacío.

Un hallazgo que **desaparece** no rompe la ejecución: se informa como aviso,
porque una mejora no puede presentarse como fallo de seguridad. Queda anotado
para depurar el baseline en una revisión documental posterior.

El gate imprime siempre cuántos hallazgos comparó, por imagen y en total, de
modo que la comparación es demostrable y no un resultado opaco.

### Ñ.5 Resultado sobre el escaneo real

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

## Q. Control negativo F — el gate S-09

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

## W. Logs y duraciones

No hay logs de CI de Task021 que auditar: no existe ejecución remota. Las
duraciones registradas son **mediciones locales** y se presentan como tales,
**nunca** como tiempos de CI.

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

## X. Matriz de criterios de STAGE-06

| Criterio literal | Frontend | Backend | Infra | Estado global |
| --- | --- | --- | --- | --- |
| Workflow en cada push y pull_request | Registrados push `34305529115` y PR `34308296565` | Registrados push `34488083060` y PR `34489982595` | **Sin workflow** | **Sin demostrar en los tres** |
| Los tres verdes sobre `dev` | Registrado `34308234554` | Registrado `34491446991` | Sin workflow | **Pendiente** |
| Un cambio roto hace fallar el workflow | Negativos locales | Negativos locales | **Negativos locales A, B, D y E demostrados** | **Evidencia remota no demostrada**; el broken push sigue sin autorizarse |
| Ningún secreto en los logs de CI | Evidencia previa | Evidencia previa | Sin run | **No verificado por Task021** |
| Duración documentada | 79 s (push de bootstrap) | 334 s sobre `dev` | Solo mediciones locales | **Pendiente** |
| El escaneo cubre todo el historial | **Auditado por Task021: 13 commits, 0 hallazgos** | **Auditado por Task021: 19 commits, 2 falsos positivos demostrados** | **Auditado por Task021: 42 commits, 0 hallazgos** | **Auditado en lectura**; falta automatizarlo en CI |
| Ningún check vacío | Pendiente de inspección | Pendiente de inspección | Terraform y Bash/sh **declarados explícitamente** como inexistentes | **Pendiente** |

Los identificadores de ejecuciones anteriores se citan como **evidencia
documental heredada**. Task021 **no** volvió a consultarlos en GitHub y **no**
los presenta como auditoría remota propia.

**ETAPA 06 no se declara completada.**

## Y. Estado de S-09 global

Frontend y backend conservan sus porciones aprobadas. **Infraestructura tiene
ahora las dos mitades**: versiones fijadas por tag y digest, y escaneo
automatizado en `CI Infra` con la política de §Ñ.
`non-functional-requirements.md` se actualiza **solo cuando la ejecución
remota lo demuestre**, no antes.

## Z. Documentación de esta fase

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

## AA. Criterion12 A/B/C/D

| Clase | Evaluación tras la medición |
| --- | --- |
| **A** | Reglas de ramas, aprobación, límites del bootstrap y vigencia de **D-020-H** conservadas. **Regla durable nueva:** la política de S-09 de infraestructura descrita en §Ñ.1 |
| **B** | Preflight fechado; primera detención conservada como historia; creación fechada del PR de Task020.1 intacta; mediciones de esta fase fechadas |
| **C** | **0.** Ningún estado vivo de Git o GitHub persistido en documentación. Las dos afirmaciones heredadas «`Task/021` sigue Pendiente y no iniciada», dentro de registros históricos de STATUS, quedaron **ancladas a su fecha** |
| **D** | **0.** B-021-1 y B-021-2 resueltos y verificados; la contradicción residual de §12 de la ficha, dejada por la edición parcial, corregida; separador de sección restituido en STATUS |

**B-021-3 no es una contradicción documental**: es un hallazgo técnico medido,
abierto y con decisión pendiente.

## AB. Git de infra

Observado el 2026-09-10 al cerrar esta fase: rama
`Task/021-CI-Infraestructura`, `HEAD = d7136b29a906563af6edbae0b67dfac101c1f3fa`,
**`main..HEAD` = 0**, staging **0**, **9** archivos sin commit. Sin commit, sin
push, sin merge y sin PR. El estado operativo posterior se consulta en Git y
GitHub, no en este documento.

## AC. Integridad del entorno

**9** contenedores en ejecución antes y después, con el mismo estado. Los **5**
volúmenes del proyecto, intactos. **0** imágenes añadidas al demonio Docker por
los escaneos. El repositorio temporal del canary, eliminado. El `.env` real
nunca se leyó ni se imprimió.

## AD. Contadores

**20/41 — 49 %**; ETAPA 06 **2/3 — 67 %**, **En progreso**. Task021 **En
progreso**, sin aprobación. `Task/022` **Pendiente** y no iniciada.

## AE. Bloqueos

| ID | Estado |
| --- | --- |
| **B-021-1** | **Resuelto** con autorización explícita el 2026-09-10 |
| **B-021-2** | **Resuelto** con autorización explícita el 2026-09-10 |
| **B-021-3** | **Resuelto** el 2026-09-11 por decisión explícita del usuario: baseline exacto de riesgo aceptado, sin `.trivyignore`, sin umbral por cantidad y sin excluir ninguna imagen |

## AF. Veredicto

**TASK021 EN PROGRESO — DETENIDA EN B-021-3.**

Inventario, baseline, validación de scripts, auditoría histórica de los tres
repositorios y cinco controles negativos: **completados y verdes**. El workflow,
el gate de vulnerabilidades y el bootstrap remoto **no se ejecutan** a la espera
de la decisión sobre MinIO y Portainer.

**No está Lista para validación. No aprobada.**
