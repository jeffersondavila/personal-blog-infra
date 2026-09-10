# TASK-020 — CI Backend

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/020-CI-Backend` |
| **Nombre** | CI Backend |
| **Etapa** | ETAPA 06 — Integración Continua |
| **Estado** | **Aprobada** (2026-09-10) |
| **Repositorios involucrados** | personal-blog-backend; personal-blog-infra (documentación) |
| **Dependencias** | `Task/018`, aprobada |
| **Rama** | `Task/020-CI-Backend` |
| **Rama base** | **`main`** |
| **SHA base backend** | `8762bbad2ce6bd67e6e736c6697a38f2d999e453` |
| **SHA base infra** | `c5b16070d5d3e128bbc299f6bd886a4d8410f075` |
| **Fecha de inicio** | 2026-09-09 (Guatemala) |
| **Última actualización** | 2026-09-10 |

## 0. Preparación Git

Observado el 2026-09-09 (Guatemala): se ejecutaron `fetch --prune`, `switch main`
y `pull --ff-only origin main` en backend e infra. En ambos repositorios,
`main == origin/main`, working tree limpio, staging vacío, rama Task020 local y
remota ausentes y consulta de PR por ese head con resultado vacío. El contenido
de `main` y `origin/dev` coincidía. Frontend estaba en `main`, limpio, y se
consultó únicamente en lectura.

Se creó la rama exacta desde `main` en backend e infra. Inmediatamente después,
`HEAD == main`, `main..HEAD = 0` y staging = 0 en ambos. Los SHA base medidos
constan arriba. Regla permanente: [WORKFLOW §2.1](../project-management/WORKFLOW.md).

## 1. Objetivo

Automatizar los gates del backend en GitHub Actions, con integración efímera,
dependencias reproducibles con hashes y escaneo efectivo de dependencias e imagen.

## 2. Contexto

Task019 y Task019.1 estaban aprobadas al empezar. Con la aprobación de
Task020 el 2026-09-10, el avance global pasa a **20/41 (49 %)** y ETAPA 06 a
**2/3 (67 %)**.

El preflight del 2026-09-09 detectó y corrigió, con autorización expresa del
usuario en cada caso, cuatro contradicciones documentales **preexistentes**:
el avance de STAGE-06 congelado en 0 % pese a declarar 1/3 aprobadas;
**B-020-1** (README del backend §3 describía ETAPA 03, Task010 en curso y `0003`
ausente); **B-020-2** (fila Total de ROADMAP en 18 / 44 %); y **B-020-3**, con
sus dos mitades en el reporte de Task019 —§H negaba la aprobación (D) y §R
presentaba el pull request como abierto en presente (C)—. Ninguna reabre
Task019 ni Task019.1, y ninguna es funcionalidad. La historia fechada de esas
detenciones se conserva en el [reporte](../task-reports/TASK-020-report.md).

La implementación técnica se realizó el 2026-09-10 sobre un laboratorio
efímero de Linux, y es lo que describe el resto de esta ficha.

## 3. Dentro del alcance

- [x] Preflight y creación canónica de ambas ramas.
- [x] Corrección heredada autorizada del avance de STAGE-06 y de B-020-1/2/3.
- [x] Completar lectura canónica y medir baseline real sobre Linux.
- [x] Lock transitivo Linux con hashes y detección de desactualización (R-14).
- [x] Ruff, formato, MyPy y Pytest completo secuencial; decisión de R-37.
- [x] PostgreSQL y MinIO efímeros según las necesidades reales del harness.
- [x] Gate real de migraciones, build Docker, auditoría Python y escaneo de imagen.
- [x] Workflow `CI Backend`, controles negativos locales restaurados y bootstrap
      remoto backend dentro de la excepción autorizada.
- [x] Evidencia real `push` con todos los gates en verde; documentación y Criterion12.

## 4. Fuera del alcance

Task021, funcionalidad de frontend o negocio, Terraform, CD, registry, despliegues,
cloud, settings y secretos de GitHub. Antes de aprobación no se permite integrar
dev ni crear PR. No se permite crear commits ni hacer push de infra durante esta fase.

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Workflow de integración continua | backend | `.github/workflows/ci-backend.yml` |
| Lock de ejecución con hashes | backend | `requirements.lock` |
| Lock de desarrollo con hashes | backend | `requirements-dev.lock` |
| Generador único de los locks | backend | `scripts/generar-locks.sh` |
| Cota de `anyio` y subida de `httpx2` | backend | `pyproject.toml` |
| Instalación fail-closed de la imagen | backend | `Dockerfile` |
| Documentación de dependencias y CI | backend | `README.md` §5.1 y §10.3 |
| Ficha, reporte y estado | infra | Este archivo y los documentos de §13 |

## 6. Criterios de aceptación

Gates reales, integración sin omisiones por dependencias ausentes, locks
verificables con hashes, política de vulnerabilidades efectiva, negativos
restaurados, run real `push` exitoso y revisión de todos sus pasos. Criterion12
exige C = 0 / D = 0 al finalizar.

## 7. TDD / Plan test-first

Task020 es CI, configuración y dependencias. **No introduce comportamiento
Python nuevo**: no se añadió ni se modificó una sola línea de `app/`, y las
1855 pruebas existentes son idénticas antes y después. Encaja en las excepciones
razonables de la [estrategia backend](../project-management/BACKEND_TESTING_STRATEGY.md)
§4 —documentación, `Dockerfile`, configuración sin lógica y cambios mecánicos—.

`scripts/generar-locks.sh` no lleva prueba propia: es una envoltura de nueve
líneas efectivas alrededor de dos invocaciones de `uv`, sin ramas ni lógica, y
lo que de verdad importa —que el lock resultante coincida con `pyproject.toml`—
lo comprueba el gate de desfase de la CI en cada ejecución.

**Una excepción a TDD no es una excepción a validar:** cada gate se sometió a un
control negativo con mutación reversible, y el resultado consta en el reporte §I.

## 8. Plan de validación

1. Medir el baseline **antes** de tocar nada, sobre Linux y Python 3.12.14.
2. Implementar y volver a medir la regresión completa sobre los locks definitivos.
3. Someter cada gate a un control negativo y restaurar.
4. Obtener una ejecución real de GitHub Actions y auditar **todos** sus pasos.

La integración se validó exclusivamente contra servicios descartables creados
para Task020, nunca contra los seis contenedores del entorno local.

## 9. Comandos de validación

Comprobaciones de Git en cada repositorio afectado:

```powershell
git branch --show-current
git rev-parse HEAD
git rev-parse main
git rev-list --count main..HEAD
git diff --cached --name-only
git status --short
git diff --check
```

Gates del backend, tal como los ejecuta la CI:

```sh
sh scripts/generar-locks.sh && git diff --exit-code -- requirements.lock requirements-dev.lock
python -m pip install --require-hashes --requirement requirements-dev.lock
python -m pip check
ruff format --check .
ruff check .
mypy .
pytest tests/integration/test_migrations.py tests/integration/test_esquema_fisico.py -W error
pytest -W error --durations=15
pip-audit --strict --requirement requirements.lock
pip-audit --strict --requirement requirements-dev.lock
docker build --tag personal-blog-backend:ci .
trivy image --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 personal-blog-backend:ci
```

## 10. Evidencia esperada

SHA base y comprobaciones Git en §0. Baseline, regresión, controles negativos,
escaneos y ejecución real de Actions constan medidos en el
[reporte](../task-reports/TASK-020-report.md), cada uno con su código de salida.

## 11. Riesgos

| Riesgo | Efecto de Task020 |
| --- | --- |
| **R-14** | **CERRADO el 2026-09-10 con la aprobación, con alcance explícito.** Los dos locks fijan las transitivas con hashes; el `Dockerfile`, la CI y el desarrollo sobre Linux, WSL o contenedor instalan con `--require-hashes`; la CI detecta el desfase. **El `.venv` de Windows queda deliberadamente fuera**: los locks son artefactos de Linux por construcción y ahí no son instalables (D-020-1). El propio baseline demostró el riesgo en vivo: la resolución sin lock trajo `starlette` 1.6.0 y `anyio` 4.15.1 frente a 1.3.1 y 4.14.2 del entorno de Windows |
| **R-15** | **Sigue abierto.** La CI ya lo *detecta*: el escaneo bloquea cualquier HIGH o CRITICAL con corrección publicada. Hoy la imagen tiene 54 HIGH/CRITICAL de la base Debian y **ninguna** con versión corregida disponible, así que no hay acción posible aguas arriba |
| **R-17** | **Sigue abierto y sin cambio.** Task020 **no** añadió refuerzo automático de la evidencia RED → GREEN. La CI comprueba que la suite pasa, no que las pruebas se escribieran primero. Se registra explícitamente para no dar por hecho un cierre que no ocurrió |
| **R-37** | **Sigue abierto, y deliberadamente.** Se decidió mantener la suite secuencial: sin `pytest-xdist`, sin `matrix` y sin particiones. Ver §12 |

## 12. Decisiones técnicas

Con la aprobación del 2026-09-10, **D-020-A** a **D-020-H** quedan **vigentes**.
**No hay ADR nuevo:** son decisiones reversibles dentro del stack aprobado.

| Decisión | Contenido |
| --- | --- |
| **D-020-A** | **`uv` 0.12.12 como generador de los locks.** Resuelve para Linux desde cualquier anfitrión, que es justo lo que necesita un equipo que desarrolla en Windows y despliega en Linux, y es un binario externo: no entra en el árbol de dependencias del proyecto ni en la imagen. Se descarga fijado por versión **y** por digest |
| **D-020-B** | **`--exclude-newer` con fecha fija.** Hace la resolución determinista, que es la condición para que el gate de desfase compare con `git diff --exit-code` sin falsos fallos por publicaciones nuevas en PyPI. Actualizar dependencias pasa a ser un acto deliberado |
| **D-020-C** | **`pyproject.toml` como única fuente manual.** `requirements.txt` y `requirements-dev.txt` se eliminaron: eran una segunda lista mantenida a mano que ya había divergido |
| **D-020-D** | **Cota `anyio<4.15`.** Medida, no preventiva: `anyio` 4.15.0 marcó obsoleto `anyio.abc.BlockingPortal` y `starlette.testclient` lo sigue usando, de modo que `pytest -W error` fallaba al recolectar. `starlette` 1.6.0 es la última publicada, así que no hay corrección aguas arriba. No se silencia la advertencia |
| **D-020-E** | **`httpx2` 2.10.0 → 2.12.0.** `pip-audit` devolvió tres vulnerabilidades con corrección publicada, una de ellas **HIGH** (CVE-2026-84382, CVSS 7.5). Se detuvo la tarea y el usuario autorizó la subida el 2026-09-10 |
| **D-020-F** | **Política de vulnerabilidades de imagen.** Un paso de inventario lista todas las severidades sin filtrar, y un paso bloqueante falla ante cualquier HIGH o CRITICAL **con corrección disponible**. No hay `.trivyignore`, ni umbral inventado, ni `\|\| true` |
| **D-020-H** | **El árbol bloqueado no llega al `.venv` de Windows, y se dice.** `uv` aplana los marcadores al resolver para una plataforma, así que ambos locks exigen `uvloop==0.22.1`, que no publica distribución de Windows: instalar allí con `--require-hashes` es imposible. **Alternativas conocidas y no adoptadas en `Task/020`:** un tercer lock resuelto con `--python-platform x86_64-pc-windows-msvc`, o una resolución `uv pip compile --universal` que conserve los marcadores en un único archivo. Las dos son viables y las dos cambian el árbol resuelto, así que exigirían regenerar, repetir la suite completa y revalidar. No se hacen aquí: la revisión previa a la aprobación pedía precisión documental, no rediseño. Se documenta el alcance real —la autoridad son la imagen y la CI— y queda anotado para quien decida cerrarlo |
| **D-020-G** | **Suite secuencial (R-37).** No se habilita paralelismo. `concurrency` a nivel de workflow sí se usa, y es otra cosa: cancela ejecuciones superadas, cada una con su propio PostgreSQL |

## 13. Documentación creada o actualizada

Backend: `README.md` (§5.1 dependencias y locks, §10.3 integración continua, y la
nota de advertencias con el caso de `anyio`), comentarios de `pyproject.toml` y
del `Dockerfile`. Infra: esta ficha, el reporte, `STATUS.md`, `ROADMAP.md`,
`STAGE-06`, el índice de reportes y, del preflight, el reporte de `Task/019`.

## 14. Archivos modificados

Backend, en **cuatro commits** —`557ca7e`, `f2b3d85`, `81ce14c` y `22af3f1`—:
`.github/workflows/ci-backend.yml`, `requirements.lock`,
`requirements-dev.lock`, `scripts/generar-locks.sh` (nuevos);
`pyproject.toml`, `Dockerfile`, `README.md`, `.dockerignore` (modificados);
`requirements.txt`, `requirements-dev.txt` (eliminados). Los dos últimos commits
son los de la revisión previa a la aprobación y solo tocaron documentación y
comentarios.

Infra: **siete documentos** en el commit documental del cierre aprobado,
`6bc80e8` —esta ficha, el reporte, `STATUS.md`, `ROADMAP.md`, `STAGE-06`, el
índice de reportes y, del preflight, el reporte de `Task/019`—. Frontend: sin
modificaciones.

## 15. Resultado de pruebas

Regresión final sobre los locks definitivos, Linux y CPython 3.12.14:
**1855 pruebas, 0 fallos, 0 errores, 0 omitidas** con `-W error`, en 234,5 s.
Ruff, formato, MyPy, `pip check`, migraciones y las dos auditorías de
dependencias terminaron en 0. Detalle y baseline previo en el reporte.

## 16. Problemas encontrados

Las cuatro contradicciones documentales del preflight quedaron resueltas con
autorización (§2). El baseline destapó además dos defectos **reales y
preexistentes**, ambos invisibles hasta resolver las dependencias en Linux:
la regresión de `anyio` que rompía `pytest -W error`, y las tres
vulnerabilidades de `httpx2`. Los dos se corrigieron: el primero con una cota
medida, el segundo con la subida autorizada por el usuario. Un tercer hallazgo
no era un defecto sino una necesidad del entorno: la suite exige que exista
también la base "de desarrollo" —el nombre sin `_test`— para poder demostrar
que la guarda la rechaza; el workflow la crea.

La revisión previa a la aprobación, el 2026-09-10, detectó dos contradicciones
más y ambas se corrigieron: **D-020-1**, la instalación local documentada eludía
el propio lock que la tarea declara como garantía; y **D-020-2**, una
sobreafirmación que atribuía SHA o digest a todas las herramientas externas
cuando `pip-audit` solo está fijado por versión. Una tercera revisión detectó
**D-020-3**: el texto afirmaba que `--require-hashes` implica `--no-deps`, lo
cual es falso —`pip` sí resuelve el árbol y aborta ante una dependencia sin
fijar ni hashear—, y quedó demostrado instalando la entrada de `alembic` sin sus
transitivas. Ese error venía del primer commit de la implementación, no de la
revisión, y así consta. **Ninguna de las tres cuestiona la implementación:** el *lock* y los
gates ya estaban en verde antes de las tres correcciones, y las tres son
defectos del texto que los describe.
Detalle y evidencia en el [reporte](../task-reports/TASK-020-report.md).

## 17. Pasos de validación para el usuario

Revisar el diff del backend y los siete documentos de infra. Abrir la ejecución
de GitHub Actions enlazada en el reporte y comprobar sus pasos uno a uno, no solo
el resultado global: el workflow declara **19 pasos** y la ejecución muestra
**21**, porque GitHub añade *Set up job* e *Initialize containers*. Los comandos
de §9 son reproducibles; la integración exige PostgreSQL y MinIO descartables,
nunca el entorno local.

**Acción pendiente del usuario en su máquina:** el `.venv` de Windows conserva
las versiones anteriores. Tras aprobar, reinstalar por la vía que corresponda a
su sistema, según la tabla de alcance de README §5.1.

## 18. Deuda técnica pendiente

**S-09 backend queda satisfecho**; **S-09 global sigue abierto** a la espera de
`Task/021` (infraestructura y escaneo del historial). R-15, R-17 y R-37 siguen
abiertos con el estado de §11. La fecha de `--exclude-newer` deberá moverse
deliberadamente cuando toque actualizar dependencias, y la cota de `anyio` se
retirará cuando starlette publique una versión que no use el alias obsoleto.

## 19. Próxima tarea

Task021 permanece pendiente y **no se inicia en esta tarea**. El siguiente
inicio debe seguir el flujo canónico aprobado.

## 20. Aprobación

**Recibida el 2026-09-10**, mediante la expresión exacta
`approved: Task/020-CI-Backend`. Aprobada por jeffersondavila (usuario).

El cierre aprobado integró la rama en `dev` con merge `--no-ff` en backend e
infra, publicó ambas ramas y abrió los pull request
**`Task/020-CI-Backend → main`**, que se dejaron **para revisión manual del
usuario**: aceptarlos o rechazarlos es responsabilidad exclusiva suya. La rama
Task local se eliminó con `git branch -d`.

*Observado el 2026-09-10 UTC, después del cierre:* el usuario fusionó los dos
pull request —backend `#15` a las 14:42:42Z, merge `8055878`; infra `#36` a las
14:42:24Z, merge `68469dd`— y eliminó las dos ramas Task remotas. La
normalización `main → dev` se ejecutó a continuación en los dos repositorios,
con los merges `5fedcb3` (backend) y `122c90a` (infra). El estado operativo
vigente se consulta en Git y GitHub, no aquí
([WORKFLOW §6.1](../project-management/WORKFLOW.md)). Detalle en el
[reporte](../task-reports/TASK-020-report.md).
