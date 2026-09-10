# TASK-020 — Reporte de CI Backend

**Fechas:** preflight el 2026-09-09, implementación y aprobación el 2026-09-10
(Guatemala). **Estado:** **Aprobada**.
**Ficha:** [TASK-020](../tasks/TASK-020-ci-backend.md).

Las secciones que siguen conservan, en orden y fechadas, las detenciones del
preflight y las autorizaciones que las desbloquearon: la corrección del avance
de STAGE-06, **B-020-1**, **B-020-2** y **B-020-3A/B**. Son **D preexistentes
detectadas y resueltas durante el preflight**, no la implementación de CI, y
ninguna reabre Task019 ni Task019.1. La implementación medida está en §A–AF.

Las autorizaciones puntuales del preflight y la de la subida de `httpx2` no
aprobaban la tarea. La aprobación llegó después, el 2026-09-10, con la expresión
exacta `approved: Task/020-CI-Backend`; el cierre consta en §Cierre aprobado.

## Corrección heredada autorizada

Durante el preflight se detectó una contradicción preexistente en STAGE-06:
la etapa declaraba 1/3 aprobadas (33 %) pero el campo Avance seguía en 0 %.
Se corrigió a 33 % dentro de Task020 antes de continuar.

**D = contradicción documental preexistente detectada durante el preflight de
Task020.** El usuario autorizó esa corrección el 2026-09-09. Se aplicó solo
después de crear la rama Task de infra. No introduce funcionalidad, no amplía
el alcance, no reabre Task019 y no constituye Task019.2 ni decisión arquitectónica.

## B-020-1 — D preexistente resuelta con autorización

Observado el 2026-09-09, después de corregir STAGE-06: el
`personal-blog-backend/README.md` §3, «Estado actual», líneas 38–43, conservaba
ETAPA 03, `Task/010-Almacenamiento-Compatible-S3` como tarea en curso y `0002`
como head. Se comprobó el mismo contenido en `origin/main` del backend,
SHA `8762bbad2ce6bd67e6e736c6697a38f2d999e453`.

La contradicción se demuestra sin ejecutar ni tocar ninguna base:

- STATUS declaraba ETAPA 06 y Task010 aprobada desde el 2026-08-28.
- `alembic/versions/20260831_0003_sesiones_administrativas_y_limite_de_acceso.py`
  declara revisión `0003`, descendiente de `0002`.
- `app/main.py` incluye autenticación, API administrativa y `/ready`, añadidos
  por tareas posteriores a Task010.

Se clasifica como **D**, contradicción documental preexistente. Se detuvo la
implementación conforme a la instrucción expresa del usuario de reportar otra
contradicción durable antes de modificarla. No se alteró el README.

El desbloqueo requirió autorización expresa del usuario para corregir ese
apartado dentro de Task020. Una vez recibida, se aplicó el texto siguiente.

### Corrección documental autorizada y aplicada

Se sustituyó exclusivamente el contenido de README §3, hasta el separador previo
a §4, por lo siguiente, usando las fuentes del propio repositorio y el estado
central en infra:

```markdown
## 3. Referencias del backend

El estado de las tareas, la etapa y el avance del proyecto se consultan en
[`STATUS.md`](../personal-blog-infra/docs/project-management/STATUS.md).

Las rutas se registran en [`app/main.py`](app/main.py); las revisiones de la
base de datos están en [`alembic/versions`](alembic/versions), y la versión de
Python y las dependencias se declaran en [`pyproject.toml`](pyproject.toml).
```

No cambia rutas, modelo ni comportamiento. Evita volver a duplicar en README
el estado central o un head que puede cambiar con otra migración.

## B-020-2 — D preexistente resuelta con autorización

Observado el 2026-09-09 durante la validación documental: la fila Total de la
tabla de etapas, `docs/project-management/ROADMAP.md` línea 104, conservaba
**18 aprobadas / 44 %**. Se comprobó ese mismo valor en `origin/main` de infra,
SHA `c5b16070d5d3e128bbc299f6bd886a4d8410f075`. STATUS y el cálculo final de
ROADMAP declaraban **19/41 (46 %)**, coherentes con la aprobación de Task019.

Es otra contradicción **D preexistente**, detectada al revisar los contadores;
no se corrigió la fila antes de recibir autorización. Posteriormente se autorizó
y aplicó exclusivamente el cambio de 18 / 44 % a 19 / 46 %. No supone aprobar
Task020 ni cambiar el número de tareas. Tras el desbloqueo, y con Task020 aún
En progreso, STATUS registraba 21 pendientes, 1 en progreso y las mismas 19
aprobadas; son 41 tareas.

## B-020-3 — Contradicción nueva y drift residual en el reporte de Task019

Observado el 2026-09-09 al leer las fuentes obligatorias, después de resolver
B-020-1/B-020-2: `docs/task-reports/TASK-019-report.md` contiene:

| Clase | Ubicación | Texto observado | Contradicción |
| --- | --- | --- | --- |
| **D** | §H, línea 222 | «Task019 no está aprobada» | El encabezado y §R registran la aprobación del 2026-09-08. La negación no está anclada a un momento previo. |
| **C** | §R, líneas 523–525 | «El pull request hacia main queda abierto» | §P registra la fusión manual del 2026-09-09 UTC. El estado operativo aparece como presente, aunque el reporte declara C=0. |

Ambos textos se comprobaron también en `origin/main` de infra, SHA
`c5b16070d5d3e128bbc299f6bd886a4d8410f075`. El reporte de Task019.1 documenta
la corrección de §N; estos párrafos permanecían en §H y §R. No se modificó
ningún documento de Task019 ni Task019.1.

La instrucción vigente del usuario exige detenerse ante otra contradicción
durable antes de modificarla. Se solicitó autorización específica para estos
dos párrafos. Posteriormente el usuario autorizó ambos cambios y se aplicaron: **B-020-3 resuelta**. Task020 retomó En progreso.

### Tratamiento documental autorizado

En §H, sustituir el párrafo que comienza «La instalación usa versiones exactas»:

> La instalación usa versiones exactas e integridad del lockfile. Antes de la
> aprobación del 2026-09-08, S-09 frontend se presentó como implementado para
> revisión; con esa aprobación quedó vigente. S-09 global conserva como
> propietarios pendientes a Task020 (backend) y Task021 (infra). El escaneo de
> secretos es un control distinto y no sustituye a `npm audit`.

En §R, sustituir el párrafo que comienza «Aprobada por el usuario»:

> Aprobada por el usuario mediante `approved: Task/019-CI-Frontend` el 2026-09-08.
> El avance tras esa aprobación fue 19/41 (46 %) y ETAPA 06 1/3 (33 %), sin
> completar la etapa. Durante el cierre aprobado, los PR Task019 hacia main se
> dejaron sin fusionar para revisión del usuario. La fusión manual del
> 2026-09-09 UTC se registra en §P; el estado operativo se consulta en Git y
> GitHub. Task020 no se inició dentro de Task019.

Se conserva la aprobación, el avance histórico y la responsabilidad exclusiva
del usuario sobre la fusión. No se reabre ni reimplementa Task019.

## Observación histórica de la detención por B-020-3, previa a su autorización

Observado el 2026-09-09:

- B-020-1 y B-020-2 **resueltas**; avance de STAGE-06 corregido previamente.
- Backend: README §3 actualizado; misma rama Task y SHA base, sin commits ni
  staging. Ningún archivo funcional modificado.
- Infra: seis documentos Task020 modificados o creados, sin commit ni staging;
  no se hicieron push, merge ni PR.
- Se leyeron las fichas Task019/019.1 y los pasajes de sus reportes hasta
  detectar B-020-3. La lectura canónica restante no había finalizado.
- Baseline técnico, lock, integración, migraciones, scanners, negativos,
  workflow y bootstrap remoto todavía no ejecutados. No se crearon servicios.
- Task020 **Bloqueada por B-020-3**. Contadores: 19 aprobadas, 21 pendientes,
  1 bloqueada; 41 tareas. ETAPA 06 conserva 1/3 (33 %).
- Criterion12 de la tarea no se declara completado: B-020-3 conserva un
  hallazgo D y uno C sin corregir. No hay aprobación de Task020.
- Validación tras estas correcciones: `git diff --check` sin errores en
  backend e infra; **276 referencias relativas, 0 rotas**, en los seis
  documentos de infra y README backend; **0 coincidencias** de patrones
  sensibles. Frontend se comprobó en `main`, limpio, únicamente en lectura.

> **Sustitución de un estado temporal.** Este reporte contenía una tabla A–AF
> fechada el 2026-09-09 que describía la tarea como *no implementada* y sus
> gates como *no ejecutados*. Aquello era cierto entonces y dejó de serlo el
> 2026-09-10, así que la tabla se sustituye por los resultados medidos. La
> historia de las detenciones y de sus autorizaciones se conserva íntegra en
> las secciones anteriores, que es lo que debía perdurar.

## Baseline previo a la implementación

Medido el 2026-09-10 en un laboratorio **efímero** creado solo para Task020
—`task020-postgres-20260909`, `task020-minio-20260909` y
`task020-runner-20260909`—, nunca contra los seis contenedores del entorno
local. Base `python:3.12.14-slim` fijada por digest, sobre una copia de
`git archive HEAD`, sin reutilizar el `.env` del desarrollador.

| Gate | Salida | Resultado |
| --- | --- | --- |
| `python --version` | `Python 3.12.14` | 0 |
| `pip check` | `No broken requirements found.` | 0 |
| `ruff check .` | `All checks passed!` | 0 |
| `ruff format --check .` | `312 files already formatted` | 0 |
| `mypy .` | `Success: no issues found in 310 source files` | 0 |
| `pytest -W error` | **error de recolección** | **4** |
| `pytest` (sin `-W error`) | `1 failed, 1854 passed` en 147,46 s | 1 |

El baseline, por tanto, **no estaba verde**, y las dos causas eran reales y
preexistentes. Ninguna era visible desde Windows.

### Defecto 1 — la deriva de transitivas rompía `pytest -W error` (R-14 en vivo)

Sin *lock*, la resolución en Linux trajo `starlette` 1.6.0 y `anyio` 4.15.1,
frente a 1.3.1 y 4.14.2 del `.venv` de Windows. `anyio` 4.15.0 marcó obsoleto
el alias `anyio.abc.BlockingPortal`, que `starlette.testclient` sigue usando en
su línea 53, así que con la política declarada del proyecto la suite ni
siquiera llegaba a recolectar.

Se midió el punto exacto de la regresión en entornos aislados:

| `anyio` | `starlette` | `python -W error -c "import starlette.testclient"` |
| --- | --- | --- |
| 4.15.1 | 1.6.0 | `DeprecationWarning` → **exit 1** |
| 4.15.0 | 1.6.0 | `DeprecationWarning` → **exit 1** |
| 4.14.2 | 1.6.0 | **exit 0**, sin advertencia |

`starlette` 1.6.0 es la última versión publicada: **no hay corrección aguas
arriba**. Se acotó `anyio<4.15` en `pyproject.toml`, con la medición y la
condición de retirada escritas junto a la dependencia. **No se añadió
`filterwarnings`**: es el mismo criterio con el que `Task/005` sustituyó `httpx`
por `httpx2` en vez de callar el `StarletteDeprecationWarning`.

### Defecto 2 — tres vulnerabilidades con corrección en `httpx2` (detención)

`pip-audit` sobre el *lock* de desarrollo devolvió tres identificadores en
`httpx2` 2.10.0, todos con versión corregida publicada:

| Identificador | Vector CVSS 3.1 | Base | Corregida en |
| --- | --- | --- | --- |
| CVE-2026-84379 — inyección de cabeceras de parte en `multipart` | `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N` | 5.3 | 2.11.0 |
| CVE-2026-84380 — `Content-Length` y `Transfer-Encoding` simultáneos | `AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L` | 5.6 | 2.11.0 |
| CVE-2026-84382 — descompresión sin acotar la memoria | `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` | **7.5 (HIGH)** | 2.12.0 |

`httpx2` es **solo de pruebas**: no aparece en `requirements.lock`, no entra en
la imagen ni en el artefacto de Lambda, y las tres exigen un servidor hostil,
que en la suite no existe. Aun así, **la tarea se detuvo** y se presentó la
decisión al usuario, que autorizó el 2026-09-10 subir a **2.12.0**. Una
excepción documentada habría seguido siendo una excepción sobre un HIGH que
tiene arreglo.

### Hallazgo de entorno, que no es un defecto

`test_la_base_de_desarrollo_no_puede_ser_destino_y_queda_intacta` falló porque
el laboratorio solo tenía la base `personal_blog_ci_test`. La prueba exige que
exista **también** la base sin el sufijo `_test`, para poder demostrar que la
guarda la rechaza y la deja intacta; sin nada que rechazar, falla en lugar de
omitirse, que es exactamente la política del harness. Creada la segunda base,
el archivo pasó 5 de 5. El workflow la crea en su paso de aprovisionamiento.

## Regresión final

Sobre los *locks* definitivos, instalados con `--require-hashes` en un entorno
virgen del mismo laboratorio.

| Gate | Salida | Resultado | Tiempo |
| --- | --- | --- | --- |
| `pip install --require-hashes -r requirements-dev.lock` | `Successfully installed …` | 0 | — |
| `pip check` | `No broken requirements found.` | 0 | — |
| Versiones efectivas | `httpx2` 2.12.0 · `anyio` 4.14.2 · `starlette` 1.6.0 | — | — |
| `ruff check .` | `All checks passed!` | 0 | < 1 s |
| `ruff format --check .` | `312 files already formatted` | 0 | 1 s |
| `mypy .` | `Success: no issues found in 310 source files` | 0 | 3 s |
| Migraciones | `13 passed` | 0 | 1,70 s |
| `pytest -W error --durations=15` | **1855 passed** | 0 | 234,50 s |
| `pip-audit --strict -r requirements.lock` | `No known vulnerabilities found` | 0 | — |
| `pip-audit --strict -r requirements-dev.lock` | `No known vulnerabilities found` | 0 | — |
| Desfase del *lock* | sin diferencias | 0 | — |

JUnit de la ejecución: `tests=1855 failures=0 errors=0 skipped=0 time=234,450 s`.

## Controles negativos LOCALES

Cada gate se rompió a propósito, se comprobó que **falla**, se restauró y se
comprobó que **vuelve a verde**. Las mutaciones se aplicaron sobre la copia del
contenedor efímero, nunca sobre el árbol de trabajo del repositorio, de modo
que ninguna pudo llegar a un commit. La comprobación final verificó que
`requirements.lock`, `requirements-dev.lock`, `pyproject.toml` y
`app/api/health.py` quedaban byte a byte idénticos.

| # | Gate | Mutación | Roto | Restaurado |
| --- | --- | --- | --- | --- |
| 1 | Ruff lint | `import os` sin usar en `app/main.py` | **exit 1**, 1 hallazgo `F401` | exit 0 |
| 2 | Ruff format | espaciado inválido | **exit 1**, `File would be reformatted` | exit 0 |
| 3 | MyPy | `str` asignado a `int` | **exit 1**, 1 error de tipado | exit 0 |
| 4 | Pytest | `health.py` devuelve otro `service` | **exit 1**, `2 failed, 1853 passed` | exit 0 |
| 5 | Migraciones | revisión `0001` sin `upgrade()` | **exit 1**, `2 failed, 11 errors` | exit 0, `13 passed` |
| 6 | Desfase del *lock* | dependencia añadida a `pyproject.toml` | **detectado**, el *lock* regenerado difiere | los dos vuelven a ser idénticos |
| 7 | `--require-hashes` | los dos digest del primer paquete alterados | **exit 1**, `THESE PACKAGES DO NOT MATCH THE HASHES…` | *lock* intacto |

> El control 7 exigió alterar **todos** los digest del paquete, no uno: `pip`
> acepta el archivo si coincide **cualquiera** de los hashes declarados, así que
> cambiar solo el del `sdist` no demuestra nada cuando lo que se descarga es la
> rueda. Un primer intento con un solo digest pasó en verde y se corrigió el
> control, no el gate.

### Control negativo del escáner de imagen

| Control | Comando | Resultado |
| --- | --- | --- |
| Imagen de Task020, gate exacto de la CI | `--severity HIGH,CRITICAL --ignore-unfixed --exit-code 1` | **exit 0** — no hay nada accionable |
| Misma imagen, **sin** `--ignore-unfixed` | `--severity HIGH,CRITICAL --exit-code 1` | **exit 1** — 51 HIGH y 3 CRITICAL |
| `python:3.12.0-slim`, gate exacto de la CI | `--severity HIGH,CRITICAL --ignore-unfixed --exit-code 1` | **exit 1** — 65 HIGH y 10 CRITICAL, **todas con versión corregida** |

El tercer control es el que importa: demuestra que `--ignore-unfixed` **no**
desactiva el gate. La imagen del backend pasa porque hoy no hay nada que
arreglar, no porque el escáner esté amordazado.

## Escaneo de la imagen

`personal-blog-backend` construida desde el `Dockerfile` de esta rama, base
`debian 13.6`. Medición del 2026-09-10 con Trivy 0.74.0.

| Severidad | Total | Con corrección publicada |
| --- | --- | --- |
| CRITICAL | 3 | **0** |
| HIGH | 51 | **0** |
| MEDIUM | 57 | **0** |
| LOW | 57 | **0** |
| UNKNOWN | 5 | **0** |
| **Total** | **173** | **0** |

Las 173 son paquetes del sistema base. Los **paquetes Python de la imagen
tienen 0**. Es exactamente el residual que `Task/018` registró en **R-15**: sin
parche aguas arriba no hay acción posible, y la CI lo detectará el día que la
haya. **No se reutilizaron los conteos de Task018**: se volvió a medir.

## Ejecución real de GitHub Actions

Dentro de la excepción de *bootstrap* autorizada **solo para
`personal-blog-backend`**, se crearon los commits y se publicó la rama.
*Estado observado antes de la aprobación:* en esa fase no se había integrado
`dev`, no se había creado ningún pull request y no se había tocado `main`. Eso
dejó de ser cierto con el cierre aprobado del 2026-09-10, registrado en §Cierre
aprobado.

Se observaron **cuatro** ejecuciones del workflow `CI Backend`, evento `push`,
sobre `Task/020-CI-Backend`: las dos primeras durante la implementación y las dos
últimas tras los commits de la revisión previa a la aprobación. **Las cuatro
concluyeron en `success`.**

| | Primera | Segunda | Tercera | Cuarta |
| --- | --- | --- | --- | --- |
| **Head SHA** | `557ca7eae501167e…` | `f2b3d85b8621faa4f…` | `81ce14cdc25f6b6e6…` | `22af3f18d9fd2f955…` |
| **Identificador** | **34481253970** | **34481957688** | **34485074950** | **34488083060** |
| **Conclusión** | **`success`** | **`success`** | **`success`** | **`success`** |
| **Duración** | 283 s | 319 s | 276 s | 295 s |
| **Suite** | 1854, **1 omitida** | **1855, 0 omitidas** | **1855, 0 omitidas** | **1855, 0 omitidas** |

Enlaces:
[34481253970](https://github.com/jeffersondavila/personal-blog-backend/actions/runs/34481253970)
· [34481957688](https://github.com/jeffersondavila/personal-blog-backend/actions/runs/34481957688)
· [34485074950](https://github.com/jeffersondavila/personal-blog-backend/actions/runs/34485074950)
· [34488083060](https://github.com/jeffersondavila/personal-blog-backend/actions/runs/34488083060).

La **tercera** y la **cuarta** corresponden a los dos commits de la revisión
previa a la aprobación, que solo tocaron documentación y comentarios. En ambos
casos se ejecutó el pipeline completo igualmente, sin provocar ejecuciones
artificiales, y las dos quedaron en verde con **1855 pruebas y 0 omitidas**, las
dos auditorías de dependencias sin hallazgos, **168** vulnerabilidades de
inventario y **0** accionables, permisos `Contents: read` / `Metadata: read` y
**0** patrones de secreto real en sus logs.

### Por qué hubo una segunda ejecución

La primera terminó en `success`, pero la auditoría de sus **21 pasos** —no del
badge— encontró una omisión: `1 skipped`, con el motivo
`el host ya opera en UTC: la diferencia no es observable aqui`. No era
infraestructura ausente. `test_el_timestamp_no_coincide_con_la_hora_local_del_host`
se omite a sí misma cuando el reloj del sistema ya está en UTC, porque entonces
su comprobación sería vacía, y el runner de GitHub opera en UTC. Es decir: la CI
estaba perdiendo justo la prueba que demuestra que el log **no** sigue al reloj
del sistema.

Se fijó `TZ: America/Guatemala` en el job, la zona real de desarrollo. La
segunda ejecución pasa **1855 pruebas y 0 omitidas**, igual que el laboratorio
local. El resto del workflow no cambió.

### Auditoría paso a paso de la segunda ejecución

| # | Paso | s | Evidencia observada en el log |
| --- | --- | --- | --- |
| 1–2 | Preparación y contenedores | 13 | Permisos del token: **`Contents: read`, `Metadata: read`**. Acciones descargadas **por SHA**, no por etiqueta |
| 3–4 | Checkout y Python | 2 | `persist-credentials: false`; **Python 3.12.14**, el mismo parche que fija el `Dockerfile` |
| 5 | Versiones de runtime | 0 | `Python 3.12.14` · `pip 26.2.1` · `Docker 28.0.4` |
| 6 | Instalación de `uv` | 1 | `sha256sum --check --strict` → `/tmp/uv.tar.gz: OK`; `uv 0.12.12` |
| 7 | **Lock al día (R-14)** | 0 | Regenera los dos *locks* y `git diff --exit-code` no imprime nada: sin desfase |
| 8 | Instalación desde el *lock* | 16 | `--require-hashes`; resuelve `anyio-4.14.2`, `httpx2-2.12.0`, `httpcore2-2.12.0`, `starlette-1.6.0` |
| 9 | Coherencia del árbol | 1 | `No broken requirements found.` |
| 10 | Bases efímeras | 0 | `CREATE DATABASE` · `COMMENT` · marca leída de vuelta: `personal-blog:test-database; efimera de la CI, muere con el runner` |
| 11 | MinIO efímero | 3 | `MinIO responde tras 2 intento(s).` |
| 12 | Formato | 0 | `312 files already formatted` |
| 13 | Lint | 0 | `All checks passed!` |
| 14 | Tipado | 17 | `Success: no issues found in 310 source files` |
| 15 | **Migraciones reales** | 3 | `13 passed`; `upgrade head` → `downgrade base` → `upgrade head` y `compare_metadata` sobre PostgreSQL real |
| 16 | **Suite completa** | 203 | `1855 passed in 200.54s`, con `-W error`. **0 omitidas, 0 fallos, 0 errores** |
| 17 | Auditoría de dependencias | 22 | `No known vulnerabilities found` en los **dos** *locks* |
| 18 | Build de la imagen | 19 | `naming to docker.io/library/personal-blog-backend:ci done` |
| 19 | Instalación de Trivy | 2 | `sha256sum --check --strict` correcto; Trivy 0.74.0 |
| 20 | Inventario de la imagen | 10 | 168 hallazgos de `debian 13.6`; **0** en los paquetes Python |
| 21 | **Gate accionable** | 0 | **0 hallazgos**: ningún HIGH o CRITICAL con corrección publicada |

La integración se ejecutó **de verdad**: PostgreSQL y MinIO respondieron, las
migraciones corrieron contra el motor real y **ninguna prueba se omitió por
falta de infraestructura**.

**Alcance exacto de este barrido de secretos.** La búsqueda de patrones de
secretos reales —claves privadas, `AKIA…`, `ghp_…`, `gho_…`— se ejecutó sobre
los logs completos de **dos** ejecuciones concretas, la primera y la segunda,
de **2 448** y **2 447** líneas: **0 coincidencias**. No se extrapola a las
demás ejecuciones; los barridos de la tercera y la cuarta se registran en su
propio párrafo, más arriba, y el de la ejecución `pull_request` y la de `dev` en
§Evidencia posterior al cierre. Las únicas credenciales visibles son las de los
servicios efímeros del runner, deliberadamente a la vista y nombradas como lo
que son.

## Seguridad, permisos y secretos

- `permissions: contents: read` en el workflow, confirmado por el runner.
- Sin `pull_request_target`, sin filtros de rama o ruta, sin `secrets` del
  proyecto. Las credenciales de PostgreSQL y MinIO nacen y mueren con el runner.
- Las de MinIO se pasan **por el entorno**, no como argumentos, para que no
  queden en la línea de comandos del proceso.
- `psql` corre dentro del contenedor de PostgreSQL, por el socket local: la
  contraseña no viaja por la línea de comandos ni aparece en el log.
- Las **Actions oficiales** están fijadas por **SHA de commit**:
  `actions/checkout@3d3c42e…` y `actions/setup-python@5fda3b9…`.
- Los binarios de **`uv` 0.12.12** y **Trivy 0.74.0** se descargan fijados por
  versión **y por digest**, y su `sha256sum` se verifica en el propio job.
- **`pip-audit` se ejecuta fijado a la versión exacta 2.10.1**, mediante
  `uv tool run --from pip-audit==2.10.1`. **No lleva digest**, y no se añadió
  maquinaria de hashes para dárselo: solo lee metadatos, no entra en la imagen
  ni en el árbol de dependencias, y ninguna fuente canónica lo exige.
- Las imágenes de PostgreSQL y MinIO están fijadas **por digest**, los mismos
  que declara el `.env.example` de este repositorio.
- No se leyó el `.env` real del desarrollador; el laboratorio partió de
  `git archive HEAD`.

## Revisión previa a la aprobación — tres D corregidas el 2026-09-10

Antes de aprobar, el usuario pidió auditar varios puntos. Los tres resultaron
ser contradicciones reales y se corrigieron. Se dejan registradas en lugar de
disolverlas en el texto corregido. **Ninguna cuestiona la implementación:** las
tres son defectos del texto que la describe.

### D-020-1 — la instalación local documentada eludía el *lock*

**Contradicción.** Task020 declara **R-14 resuelto**, pero README §5, la ficha
§17 y este reporte daban `pip install -e ".[dev]"` como el procedimiento
oficial para crear o actualizar el entorno de desarrollo. Esa orden **vuelve a
resolver las transitivas** desde `pyproject.toml` y puede producir un árbol
distinto del bloqueado. La garantía quedaba viva en CI y en Docker mientras la
documentación de desarrollo reintroducía resolución libre.

**Comprobación del procedimiento coherente.** Se validó, sin copiarlo a ciegas,
el flujo esperado:

```sh
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install -e . --no-deps
```

Es **correcto sobre Linux** y es el que instala el árbol exacto. La segunda
orden ya se había verificado durante Task020 (`pip install -e . --no-deps`,
exit 0, metadatos y extra `dev` legibles).

**Razón técnica por la que no vale en Windows, medida el 2026-09-10.** `uv`
resuelve para una sola plataforma y **aplana los marcadores de entorno**, así
que ambos *locks* listan `uvloop==0.22.1` **sin condición**. Pero
`uvicorn[standard]` lo declara como `uvloop>=0.15.1; sys_platform != 'win32'`, y
`uvloop` 0.22.1 publica **49 distribuciones, ninguna para Windows**. El intento
real en un entorno virtual desechable de Windows terminó en **exit 1**,
`Getting requirements to build wheel did not run successfully`. Los dos *locks*
son, por construcción, artefactos de Linux.

**Corrección.** README §5.1 pasa a declarar el alcance sin ambigüedad: la vía
con `--require-hashes` para imagen, CI, Linux, WSL y contenedor; y en Windows
`pip install -e ".[dev]"` **nombrada como lo que es**, una resolución libre que
no es el árbol bloqueado. El aviso aparece también junto a la orden de §5. El
extra `[dev]` de `pyproject.toml` **no se toca**: sigue siendo la fuente desde la
que se genera el *lock*.

**Lo que no se hizo, y por qué.** Cerrar del todo el hueco de Windows es
posible: un tercer *lock* con `--python-platform x86_64-pc-windows-msvc`, o una
resolución `uv pip compile --universal` que conserve los marcadores en un solo
archivo. Ambas cambian el árbol resuelto y obligarían a regenerar, repetir la
suite completa y revalidar. La revisión pedía precisión documental, no
rediseño, así que quedan anotadas como decisión abierta en la ficha
(**D-020-H**) en lugar de ejecutarse por iniciativa propia.

**Clasificación: D**, documental y técnica de reproducibilidad. **Resuelta.**

### D-020-2 — sobreafirmación sobre las herramientas externas

**Contradicción.** La sección de seguridad de este reporte afirmaba que las
«acciones y herramientas externas» estaban «fijadas por SHA o por digest, con
verificación efectiva en el propio job». La evidencia real solo lo sostiene para
cuatro de las cinco: `actions/checkout` y `actions/setup-python` por SHA, y `uv`
y Trivy por versión más digest verificado. **`pip-audit` está fijado por versión
exacta y nada más.**

**Corrección.** Se sustituyó la frase por el detalle por herramienta, y se
corrigió el mismo sobreclaim **en su origen**: el comentario del bloque `env` de
`ci-backend.yml` encabezaba con «version exacta Y digest» un grupo que incluía
`VERSION_DE_PIP_AUDIT`. **No se añadió maquinaria de hashes para `pip-audit`**:
solo lee metadatos, no entra en la imagen ni en el árbol de dependencias, y
ninguna fuente canónica lo exige.

**Clasificación: D**, documental por sobreafirmación. **Resuelta.**

### D-020-3 — explicación incorrecta de `--require-hashes`

**Contradicción.** El texto afirmaba que **«el modo implica `--no-deps`»** y lo
usaba para explicar que `pip` no resuelve dependencias. Es falso. `--require-hashes` activa
el *hash-checking mode*; `--no-deps` es una opción distinta y **no queda
implicada**. En ese modo `pip` **sí** recorre el árbol de dependencias, y lo que
hace es **abortar** en cuanto encuentra una que no esté enumerada con versión
exacta y con hash.

**Comprobación empírica del 2026-09-10.** Se extrajo del *lock* únicamente la
entrada de `alembic==1.18.5`, con sus hashes y **sin sus transitivas**, y se
instaló en un entorno virtual desechable:

```text
Collecting alembic==1.18.5 (from -r /tmp/solo-alembic.txt (line 1))
  Using cached alembic-1.18.5-py3-none-any.whl (264 kB)
Collecting SQLAlchemy>=1.4.23 (from alembic==1.18.5->-r /tmp/solo-alembic.txt (line 1))
ERROR: In --require-hashes mode, all requirements must have their versions
pinned with ==. These do not:
    SQLAlchemy>=1.4.23 …
```

`pip` **recogió la dependencia** antes de fallar. Si el modo implicase
`--no-deps`, `alembic` se habría instalado solo y sin error. Queda demostrado
que la resolución ocurre y que la garantía **no** viene de desactivarla.

**De dónde viene realmente la garantía.** Del *lock*: enumera las dependencias
directas **y** transitivas con versión exacta y hash, de modo que no queda nada
que resolver libremente, y cualquier ausencia hace fallar la instalación en
lugar de resolverse en silencio. El editable sí usa `--no-deps` de forma
**explícita**, para registrar el proyecto local sin reinstalar ni resolver sus
dependencias.

**Alcance.** **No era un fallo del gate ni del *lock*.** Los dos archivos ya
contenían el cierre transitivo completo antes de esta corrección, y la CI y la
imagen instalaban correctamente: las ejecuciones en verde anteriores a ella lo
acreditan.
Era una **sobreafirmación factual sobre el mecanismo de `pip`**, y quedó
corregida **antes de aprobar**. No se tocó código, `pyproject.toml` ni los
*locks*; solo el texto de README §5.1 y dos comentarios que repetían el mismo
error, en el `Dockerfile` y en el workflow.

**Origen, comprobado en el historial.** No lo introdujo la revisión: entró con
el **primer commit de la implementación**, `557ca7e`, ya presente en el
`Dockerfile`, en el workflow y una vez en README. La corrección de **D-020-1**
lo **repitió**, y ahí README pasó a tener dos apariciones. Se anota así porque
atribuirlo a la revisión sería más cómodo y menos cierto.

**Clasificación: D**, documental por descripción incorrecta del mecanismo.
**Resuelta.**

## Criterion 12

| | Resultado |
| --- | --- |
| **A — reglas de gobierno** | Rama Task nacida de `main` y verificada; commits solo en backend, dentro de la excepción de *bootstrap* autorizada. **Regla permanente:** antes de la aprobación no se integra `dev`, no se crea PR y no se toca `main`. *Estado pre-aprobación observado:* así fue durante toda la implementación; el cierre aprobado del 2026-09-10 ejecutó esos pasos, y la fusión es acto exclusivo del usuario |
| **B — evidencia fechada** | Baseline, regresión, controles negativos y escaneos, cada uno con su código de salida y su fecha. Ejecuciones reales de Actions: **cuatro** de evento `push` sobre la rama Task, **una** de evento `pull_request` y **una** de `push` sobre `dev` tras la normalización. Seis en total, todas `success`, cada una con su identificador |
| **C — estado Git/GitHub vivo persistido** | **0.** Los identificadores de ejecución, los números de PR, los `mergedAt`, los merge commits y los SHA son **hechos fechados**, no estados vivos. No se afirma que ningún PR esté abierto, que ninguna rama remota exista ahora, ni cuál es el estado actual de `main` o `dev`: eso se consulta en vivo ([WORKFLOW §6.1](../project-management/WORKFLOW.md)) |
| **D — contradicciones documentales** | **0**. Cuatro del preflight, resueltas con autorización; **D-020-1**, **D-020-2** y **D-020-3**, detectadas en la revisión previa a la aprobación del 2026-09-10 y corregidas, quedan registradas arriba con su nombre. Los estados temporales que dejaron de ser ciertos se sustituyeron. **B-020-4** y **B-020-5**, detectados durante el cierre y **fuera** del alcance de Task020, los corrigió `Task/020.1` |

> **Recalculado el 2026-09-10 por [`Task/020.1`](TASK-020.1-report.md).** Esta
> tabla se escribió durante el cierre aprobado, cuando el resultado de la fusión
> todavía no existía, y afirmaba **C = 0** conviviendo con **ocho** afirmaciones
> de estado vivo de este documento —la novena estaba en la ficha §20— que la
> propia fusión volvió falsas. `Task/020.1` las convirtió en
> hechos fechados y corrigió las contradicciones heredadas. **C = 0 y D = 0
> vuelven a ser ciertos**, ahora sí verificados sobre el texto vigente.

## Documentación

Backend: `README.md` §5.1 —una fuente manual y dos *locks* generados—, §10.3
—integración continua— y la nota de advertencias, ampliada con el caso de
`anyio`. Comentarios de `pyproject.toml` y del `Dockerfile` reescritos para que
describan el mecanismo vigente y no el anterior. Infra, **siete documentos**:
ficha, este reporte, `STATUS.md`, `ROADMAP.md`, `STAGE-06`, el índice de reportes
y, del preflight, el reporte de `Task/019`.

Validación documental del 2026-09-10 sobre los siete documentos de infra:
**259 referencias relativas comprobadas, 0 rotas**; **0 coincidencias** de
patrones de claves privadas, credenciales de AWS o tokens de GitHub;
`git diff --check` sin errores.

## Resumen A–AF

| Apartado | Resultado medido el 2026-09-10 |
| --- | --- |
| **A. Preflight Git** | Ambas ramas nacidas de `main` y verificadas el 2026-09-09; SHA base en la ficha §0 |
| **B. Fuentes canónicas** | Lectura completada, incluidas Task019, Task019.1, la estrategia de pruebas, el harness de PostgreSQL y almacenamiento, el runbook y los riesgos R-14/R-15/R-17/R-37 |
| **C. Alcance** | CI backend completa: *lock*, gates, integración efímera, migraciones, Docker, escáneres, R-14, R-37 y S-09 backend |
| **D. Baseline** | Verde en Ruff, formato, MyPy y `pip check`; **rojo** en `pytest -W error` (exit 4) por la deriva de `anyio`, y un fallo por la base de desarrollo ausente en el laboratorio |
| **E. Runtime** | Python **3.12.14** en el laboratorio y en el runner; `pip 26.2.1` en CI |
| **F. Dependencias** | `pyproject.toml` es la única fuente manual. 40 paquetes en el *lock* de ejecución, 60 en el de desarrollo |
| **G. R-14 y lock** | **Resuelto como propuesta, con alcance explícito.** `uv` 0.12.12 fijado por digest, `--generate-hashes`, `--python-platform` Linux, `--exclude-newer` fijo; `--require-hashes` en imagen, CI y desarrollo sobre Linux/WSL/contenedor; desfase detectado por regeneración y `git diff --exit-code`. **El `.venv` de Windows queda fuera del árbol bloqueado** y así consta en README §5.1 |
| **H. Servicios efímeros** | PostgreSQL como `service` del job con las **dos** bases y la marca de seguridad; MinIO por `docker run` con espera de salud. Ambos mueren con el runner |
| **I. Migraciones** | `13 passed` en su propio paso; `upgrade`/`downgrade`/`upgrade` y `compare_metadata` sobre PostgreSQL real. **No se añadió ningún gate tautológico nuevo** |
| **J. Ruff / formato** | `All checks passed!` · `312 files already formatted` |
| **K. MyPy** | `Success: no issues found in 310 source files` |
| **L. Pytest** | **1855 pruebas, 0 fallos, 0 errores, 0 omitidas** con `-W error`, en 200,54 s en CI |
| **M. R-37** | **Secuencial, decisión D-020-G.** Sin `pytest-xdist`, sin `matrix`, sin particiones. `concurrency` del workflow se usa y no es R-37 |
| **N. S-09 backend** | **Satisfecho**: instalación con hashes y auditoría sin umbrales sobre los dos *locks*. **S-09 global sigue abierto** con `Task/021` |
| **O. Docker build** | Construcción real en el job desde `requirements.lock` con `--require-hashes`; base `python:3.12.14-slim` por digest |
| **P. Escaneo de dependencias** | `pip-audit` 2.10.1 `--strict` sobre los dos *locks*: `No known vulnerabilities found`. Antes destapó las tres de `httpx2`, que se corrigieron |
| **Q. Escaneo de imagen** | Trivy 0.74.0. Inventario 173 hallazgos, **0 con corrección**; gate accionable en 0. Medido de nuevo, sin reutilizar Task018 |
| **R. Política de vulnerabilidades** | Inventario sin filtrar + gate que falla ante cualquier HIGH/CRITICAL **con arreglo**. Sin `\|\| true`, sin `.trivyignore`, sin umbral inventado. Demostrada con tres controles |
| **S. Diseño del workflow** | `push` y `pull_request`, sin `pull_request_target`, sin filtros, `contents: read`, un job en `ubuntu-24.04`, **19 pasos declarados** en el YAML —que GitHub muestra como 21 en la ejecución al añadir *Set up job* e *Initialize containers*— |
| **T. Controles negativos** | **7 gates rotos y restaurados**, más 3 controles del escáner. Ninguna mutación quedó en el repositorio |
| **U. Actions real** | **Cuatro** ejecuciones `push` sobre la rama Task en **`success`**: 34481253970, 34481957688, 34485074950 y 34488083060. Auditados los 21 pasos de las tres últimas. Tras el cierre se sumaron **34489982595** (`pull_request`) y **34491446991** (`push` sobre `dev`), las dos en `success` con sus 21 pasos en verde: §Evidencia posterior al cierre |
| **V. Seguridad y secretos** | 0 patrones de secreto real en los logs de las cuatro ejecuciones ni en los archivos nuevos; permisos mínimos confirmados por el runner. Fijado por herramienta declarado con precisión tras **D-020-2**: Actions por SHA, `uv` y Trivy por versión y digest verificado, `pip-audit` solo por versión exacta |
| **W. Duraciones** | 283 s, 319 s, 276 s y 295 s de extremo a extremo; la suite domina con 176 s, 203 s, 170 s y 186 s |
| **X. Documentación** | README backend §5.1 y §10.3, comentarios de `pyproject` y `Dockerfile`; ficha, reporte, STATUS, ROADMAP, STAGE-06 e índice |
| **Y. Riesgos** | **R-14 resuelto** como propuesta. **R-15** abierto, ahora detectado por la CI. **R-17 abierto y sin cambio**: Task020 **no** lo reforzó. **R-37** abierto, sin paralelismo habilitado |
| **Z. Criterion 12** | **C = 0 · D = 0**, recalculado el 2026-09-10 por [`Task/020.1`](TASK-020.1-report.md) sobre el texto vigente |
| **AA. Git backend** | *Estado observado antes de la aprobación, 2026-09-10:* `Task/020-CI-Backend` en `22af3f18d9fd2f955319ea1131bac7c40e57b3df`, **4 commits** sobre `main`, árbol limpio, staging vacío, rama ya publicada por la excepción de *bootstrap*, y todavía sin merge a `dev` y sin PR. El cierre aprobado y la fusión posterior están en §Cierre aprobado y §Evidencia posterior al cierre |
| **AB. Git infra** | *Estado observado antes de la aprobación, 2026-09-10:* `Task/020-CI-Backend` en `c5b16070d5d3e128bbc299f6bd886a4d8410f075`, **0 commits** sobre `main`, staging vacío, siete documentos aún sin commit, y todavía sin push y sin PR. El cierre aprobado los commiteó en `6bc80e8` y siguió el flujo; el detalle fechado está en §Evidencia posterior al cierre |
| **AC. Roadmap** | Task020 **Aprobada** el 2026-09-10. Avance **20/41 (49 %)** y ETAPA 06 **2/3 (67 %)**, etapa **no completada**. Task021 pendiente y no iniciada |
| **AD. Cierre y normalización** | Ejecutado el 2026-09-10: integración en `dev` con `--no-ff`, publicación y PR **`Task/020-CI-Backend → main`** en ambos repositorios, dejados para revisión manual. *Observado el 2026-09-10 UTC:* el usuario fusionó `#15` (backend, merge `8055878`) y `#36` (infra, merge `68469dd`), eliminó las dos ramas Task remotas, y la normalización `main → dev` quedó completada con `5fedcb3` y `122c90a`. **Nada pendiente** de este flujo |
| **AE. Bloqueos** | **Ninguno abierto.** Las dos detenciones de la implementación —`anyio` y `httpx2`— se resolvieron, la segunda con autorización expresa. **D-020-1**, **D-020-2** y **D-020-3**, de la revisión previa a la aprobación, también quedan resueltas. Sigue abierta y anotada la decisión **D-020-H**: el `.venv` de Windows no reproduce el árbol bloqueado |
| **AF. Veredicto** | **TASK020 IMPLEMENTADA — LISTA PARA VALIDACIÓN.** No aprobada |

## Recursos temporales que siguen en la máquina

Task020 creó un laboratorio efímero que **no se ha destruido**, porque eliminar
contenedores es una operación destructiva y requiere autorización explícita:
`task020-postgres-20260909`, `task020-minio-20260909` y
`task020-runner-20260909`; la imagen `personal-blog-backend:task020`; la imagen
`python:3.12.0-slim`, descargada solo para el control negativo del escáner; y
el directorio `.task020-validation/` en la raíz del *workspace*, **fuera de los
tres repositorios**, con los logs de todas las mediciones. Los **seis
contenedores del entorno local no se tocaron** y siguen en marcha.

## Acción pendiente en la máquina del usuario

El `.venv` de Windows conserva `anyio` 4.14.2, `starlette` 1.3.1 y `httpx2`
2.10.0, y ya no coincide con `pyproject.toml`. Tras la aprobación, reinstalar
por la vía que corresponda al sistema, según la tabla de README §5.1:
`pip install --require-hashes -r requirements-dev.lock` en Linux, WSL o
contenedor; `pip install -e ".[dev]"` en Windows, sabiendo que ahí es una
resolución libre y no el árbol bloqueado. No se modificó ese entorno desde la
tarea.

## Archivos modificados

**Backend** — 4 commits: `557ca7e`, `f2b3d85`, `81ce14c` y `22af3f1`.

| Archivo | Cambio |
| --- | --- |
| `.github/workflows/ci-backend.yml` | Nuevo. Workflow `CI Backend`, 19 pasos declarados |
| `requirements.lock` | Nuevo. 40 paquetes de ejecución con hashes |
| `requirements-dev.lock` | Nuevo. 60 paquetes con hashes |
| `scripts/generar-locks.sh` | Nuevo. Fuente única de los argumentos de `uv` |
| `pyproject.toml` | Cota `anyio<4.15`, `httpx2` 2.10.0 → 2.12.0, comentarios del modelo de dependencias |
| `Dockerfile` | Instala `requirements.lock` con `--require-hashes` |
| `README.md` | §5.1 dependencias y *locks*, §10.3 integración continua, nota de advertencias |
| `.dockerignore` | Excluye `scripts/` del contexto de construcción |
| `README.md` §5.1 | Tercer commit: alcance del *lock* por entorno, con la razón técnica de Windows (**D-020-1**). Cuarto commit: explicación correcta de `--require-hashes` (**D-020-3**) |
| `ci-backend.yml` | Tercer commit: comentario del bloque `env` corregido, `pip-audit` no lleva digest (**D-020-2**). Cuarto commit: comentario de la instalación, `--require-hashes` no implica `--no-deps` (**D-020-3**) |
| `Dockerfile` | Cuarto commit: mismo comentario corregido (**D-020-3**) |
| `requirements.txt` | **Eliminado** |
| `requirements-dev.txt` | **Eliminado** |

**Infra** — siete documentos, commiteados en el cierre aprobado como `6bc80e8`:
`docs/tasks/TASK-020-ci-backend.md`,
`docs/task-reports/TASK-020-report.md`,
`docs/project-management/STATUS.md`, `docs/project-management/ROADMAP.md`,
`docs/stages/STAGE-06-continuous-integration.md`,
`docs/task-reports/README.md` y, del preflight,
`docs/task-reports/TASK-019-report.md`.

**Frontend**: sin modificaciones, en `main` y limpio.

## Cierre aprobado

**Aprobada el 2026-09-10** por jeffersondavila (usuario), mediante la expresión
exacta `approved: Task/020-CI-Backend`.

Antes de ejecutar nada se comprobó lo que exige el flujo: la rama existe local y
—en backend— también en origin; es la rama activa en los dos repositorios; las
validaciones de la tarea terminaron correctamente; y **no hay cambios ajenos
mezclados**, verificado archivo por archivo contra `main`. Repositorios
afectados: **backend** e **infra**. El frontend no participa.

Pasos ejecutados en cada repositorio afectado: registro documental de la
aprobación, promoción de **D-020-A** a **D-020-H** a **vigentes**, actualización
de STATUS, ROADMAP, ficha, reporte, etapa e índice, validaciones finales,
commits pendientes, integración en `dev` mediante merge **`--no-ff`**,
publicación de `dev` y de la rama Task, creación del pull request con base
`main` y head `Task/020-CI-Backend`, y borrado de la rama Task **local** con
`git branch -d`. Al terminar ese cierre, la rama Task **remota** seguía
publicada en los dos repositorios.

**Los pull request se dejaron para revisión manual del usuario**, sin fusionar:
aceptarlos, rechazarlos o eliminar la rama remota es responsabilidad exclusiva
suya. Esa es la regla permanente. El estado operativo vigente se consulta en Git
y GitHub, no aquí: este documento registra estado **duradero**
([WORKFLOW §6.1](../project-management/WORKFLOW.md)).

**`Task/021` no se inicia en esta tarea.**

## Evidencia posterior al cierre

*Observado el 2026-09-10 UTC.* El usuario fusionó manualmente los dos pull
request y eliminó las dos ramas Task remotas. La normalización `main → dev` se
ejecutó a continuación en los dos repositorios y quedó verificada. Son hechos
fechados, no estado vigente.

| Repositorio | PR | `mergedAt` | Merge commit | Normalización `dev` |
| --- | --- | --- | --- | --- |
| backend | `#15` | 2026-09-10T14:42:42Z | `8055878e415ace2bfc4e7685e0549c5ab8a642ef` | `5fedcb34f8f1542fcfb0957547e58f472529f6f2` |
| infra | `#36` | 2026-09-10T14:42:24Z | `68469dd016514fafc7ce07da120e908fa8873849` | `122c90a5d321d5dd3808d1d38f8c0b60351d9175` |

Los dos pull request fueron **`Task/020-CI-Backend → main`**, la dirección que
exige el flujo. Las ramas Task locales se habían eliminado durante el cierre con
`git branch -d`; las **remotas** las eliminó después el usuario, que es su
decisión exclusiva.

### Las otras dos ejecuciones del workflow

Las cuatro ejecuciones auditadas arriba son de evento `push` sobre la rama Task.
El cierre aprobado y la fusión produjeron dos más, que acreditan los triggers y
el contexto que faltaban:

| Ejecución | Evento | Head | Conclusión | Suite |
| --- | --- | --- | --- | --- |
| **34489982595** | `pull_request` | `22af3f18d9fd2f955319ea1131bac7c40e57b3df` | **`success`** | **1855** pruebas, **0** omitidas |
| **34491446991** | `push` sobre `dev` | `5fedcb34f8f1542fcfb0957547e58f472529f6f2` | **`success`** | **1855** pruebas, **0** omitidas |

Enlaces:
[34489982595](https://github.com/jeffersondavila/personal-blog-backend/actions/runs/34489982595)
· [34491446991](https://github.com/jeffersondavila/personal-blog-backend/actions/runs/34491446991).

Las dos concluyeron con sus **21 pasos** en verde —los 19 declarados en el
workflow más *Set up job* e *Initialize containers*, que añade GitHub—. La
segunda es la ejecución sobre `dev` posterior a la normalización, y su head es
justamente el merge de normalización del backend.

**Barrido de secretos sobre estos dos logs**, hecho con los mismos patrones que
el de la implementación —claves privadas, `AKIA…`, `ghp_…`, `gho_…`, `ghs_…`,
`github_pat_…`, `aws_secret_access_key`—: **2 480** y **2 469** líneas,
**0 coincidencias** en ambos.

Con estas dos ejecuciones, el workflow del backend tiene evidencia real de sus
**dos** triggers, `push` y `pull_request`, y de un verde sobre `dev`. Eso **no**
completa la ETAPA 06: sus criterios de salida exigen los **tres** repositorios y
`Task/021` sigue pendiente.

### Dos hallazgos detectados durante el cierre y NO corregidos

Al actualizar los contadores aparecieron dos contradicciones **preexistentes en
`origin/main`**, ajenas al alcance de Task020. Se registran sin tocarlas, y
requieren autorización expresa:

| | Hallazgo | Estado |
| --- | --- | --- |
| **B-020-4** | El registro histórico de `Task/002.1` en STATUS —mantenimiento de 2026-07-26— lleva una fila «Avance global» con **44 % — 18 de 41**: un contador vivo dentro de un registro histórico, que ni era cierto en esa fecha ni lo es ahora | **Detectado en `Task/020`, no corregido en ella.** Corregido después por `Task/020.1` |
| **B-020-5** | *Observado el 2026-09-10 sobre `origin/main` en `c5b1607`, antes del cierre:* **cinco** encabezados «Última tarea aprobada» —Task/019, 016, 015, 013 y 006—, porque cada tarea añadió el suyo sin degradar el anterior | **Detectado, parcialmente contenido:** el cierre degradó el de Task/019 para no añadir un sexto, así que tras el merge los cinco pasaron a ser Task/020, 016, 015, 013 y 006. Los cuatro heredados los degradó después `Task/020.1` |

Sí se corrigió, por ser parte del propio cierre, el **avance global de ROADMAP**,
que seguía en **44 % — 18 de 41** mientras la fila Total decía otra cosa. Era el
residuo que **B-020-2** no había alcanzado.

## Veredicto

**TASK020 APROBADA Y CERRADA.**

Aprobada por el usuario el 2026-09-10 mediante `approved: Task/020-CI-Backend`.
Avance **20/41 — 49 %**; ETAPA 06 **2/3 — 67 %**, **no completada**: falta
`Task/021`. Durante el cierre aprobado la rama se integró en `dev` con merge
`--no-ff` en backend e infra, se publicaron ambas ramas y se crearon los pull
request `Task/020-CI-Backend → main`, que se dejaron para revisión manual del
usuario. *Observado el 2026-09-10 UTC:* el usuario los fusionó, eliminó las
ramas remotas y la normalización `main → dev` quedó completada; el detalle
fechado está en §Evidencia posterior al cierre. **Task021 no se inicia en esta
tarea.**
