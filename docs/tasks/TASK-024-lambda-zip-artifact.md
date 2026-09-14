# TASK-024 — Artefacto ZIP de Lambda

| Campo | Valor |
| --- | --- |
| **Identificador** | `Task/024-Artefacto-ZIP-Lambda` |
| **Nombre** | Artefacto ZIP de Lambda |
| **Etapa** | ETAPA 08 — Preparación Cloud + AWS Local Parity |
| **Estado** | **Aprobada** el 2026-09-13 mediante `approved: Task/024-Artefacto-ZIP-Lambda` |
| **Repositorios involucrados** | `personal-blog-backend` —**propiedad funcional**— y `personal-blog-infra` (documentación/gobierno). `personal-blog-frontend` **no participa** |
| **Dependencias** | `Task/023-Compatibilidad-FastAPI-Lambda` ✔ **Aprobada** el 2026-09-13 |
| **Rama** | `Task/024-Artefacto-ZIP-Lambda` |
| **Rama base** | **`main`** — única base permitida |
| **SHA base** | backend `8795ac750f3cdfaacc1d9edd8bd9c94a0726f5b1` · infra `7397eca76a282f4edb5a9da6b7d588bfd5f68efc` |
| **Fecha de inicio** | 2026-09-13 |
| **Última actualización** | 2026-09-13 |

---

## 0. Preparación Git

**Rama base obligatoria: `main`.** `dev` **nunca** es base de una Task
([`WORKFLOW.md`](../project-management/WORKFLOW.md) §2.1).

| # | Comprobación | Resultado |
| --- | --- | --- |
| 1 | `main == origin/main` | ✔ backend `8795ac7…` · infra `7397eca…` · frontend `7dce98a…`, los tres idénticos a `origin/main` |
| 2 | Working tree limpio antes de crear la rama | ✔ `git status --porcelain` vacío en los tres repositorios |
| 3 | Rama creada **desde `main`** | ✔ en backend e infra; **frontend sin rama**, solo lectura |
| 4 | `git rev-parse HEAD` == `git rev-parse main` justo tras crearla | ✔ backend `8795ac7…` == `8795ac7…` · infra `7397eca…` == `7397eca…` |

No existía ninguna rama `Task/*` previa en ningún repositorio. `main` es ancestro de `dev`
y el contenido de ambas coincide en backend e infra: la normalización posterior a
`Task/023` estaba completa.

---

## 1. Objetivo

Producir el **artefacto ZIP de despliegue** del backend para AWS Lambda —Python 3.12 sobre
Linux x86_64— de forma **reproducible byte a byte**, medirlo contra las cuotas de
empaquetado de Lambda, publicar su **SHA-256** y un **manifiesto**, y **demostrar que el
artefacto funciona ejecutando el *handler* desde el ZIP extraído en un proceso Linux
aislado**, sin el árbol de fuentes y sin dependencias externas al propio artefacto.

## 2. Contexto

`Task/023` entregó el adaptador `app/lambda_handler.py` sobre `mangum==0.22.0` y fijó el
nombre del *handler*: `app.lambda_handler.handler`. Eso hace que la aplicación *pueda*
ejecutarse bajo Lambda; **no** produce nada desplegable.

`Task/025` necesita un artefacto real: sus criterios exigen aplicar y ejercitar **Lambda +
API Gateway v2** contra el destino local, y sin artefacto podría declararse lista sin que
existiera nunca lo que sus propios criterios ejercitan
([STAGE-08](../stages/STAGE-08-cloud-ready.md), «Por qué también de `Task/024`»).

El riesgo que esta tarea existe para cerrar está escrito en la propia ficha de etapa:
*«Dependencias nativas de Python incompatibles con el runtime de Lambda»*, con la
mitigación *«construcción del paquete en entorno Linux equivalente al runtime destino»*.
El backend se desarrolla en Windows y **13 de sus 41 distribuciones de ejecución traen
artefactos nativos**: un `.venv` de Windows copiado a un ZIP no arrancaría en Lambda, y el
fallo aparecería por primera vez en la nube.

## 3. Dentro del alcance

- [x] Herramienta de construcción y validación del artefacto, en Python de biblioteca
      estándar, dentro de `personal-blog-backend`.
- [x] Construcción de las dependencias **en Linux**, dentro de la imagen oficial del
      runtime de Lambda para Python 3.12, **fijada por digest**.
- [x] Instalación exclusivamente desde `requirements.lock` (lock de **ejecución**) con
      `--require-hashes`, `--only-binary=:all:` y `--no-compile`.
- [x] *Layout* con `app/` **directamente en la raíz** del ZIP, junto a los paquetes de
      ejecución y sus bibliotecas nativas.
- [x] **Reproducibilidad demostrada**: dos construcciones independientes (`A` y `B`) desde
      directorios distintos producen el **mismo SHA-256** y **los mismos bytes**.
- [x] Medición real de **bytes comprimidos** y **bytes descomprimidos**, con margen frente
      a las cuotas y contribución por distribución.
- [x] **SHA-256** del ZIP, archivo `.sha256` verificable y **manifiesto** con la
      procedencia del build.
- [x] **Ejecución aislada real** del *handler* desde el ZIP extraído: evento HTTP API v2
      `GET /health`, `statusCode == 200`, cuerpo y cabeceras comprobados.
- [x] **Ejercicio de capacidades nativas offline**: Argon2, Pillow y el driver binario de
      PostgreSQL, más la carga de toda extensión compilada del artefacto.
- [x] **Controles negativos de aislamiento**: con una dependencia retirada del artefacto y
      una copia accesible fuera, la ejecución debe seguir fallando.
- [x] Gates de contenido prohibido: `.env`, secretos, `.git`, pruebas, dependencias de
      desarrollo, `__pycache__`, `.pyc`, binarios de Windows, arquitectura incorrecta,
      rutas absolutas, *path traversal*, duplicados y enlaces simbólicos.
- [x] Ampliación **mínima** del workflow `CI Backend` existente con los gates anteriores.
- [x] Ficha, reporte, `STATUS.md`, `ROADMAP.md` y `STAGE-08` en `personal-blog-infra`.
- [x] Corrección, **solo de sus propias entradas**, de la columna *Repos* y del campo
      *Repositorio* de `Task/024`, que el cierre de `Task/023` dejó anotados para este
      preflight.

## 4. Fuera del alcance

| Queda fuera | Dónde corresponde |
| --- | --- |
| Terraform, módulos, *backend* de estado | `Task/025` (**D-06**) |
| Desplegar el artefacto en el laboratorio AWS local (Floci) | `Task/025` |
| Runbooks de despliegue | `Task/026` |
| Cuenta AWS, credenciales reales, AWS CLI contra AWS real, API Gateway real | ETAPA 09 y 10 |
| ECR, imagen de contenedor de Lambda, *layers* | No previsto; el prefijo `python/` es de *layers* y aquí **no** se usa |
| IAM productivo y mínimo privilegio | `Task/028`, `Task/032` |
| Memoria, *timeout*, concurrencia y **arranque en frío real** | `Task/032` — cierra **D-12** |
| Dominio y *base path* del *stage* | `Task/033`, `Task/035` |
| Rediseñar Mangum, `lifespan`, FastAPI, el *handler* o **T-04** | `Task/023`, **Aprobada**; aquí se **consume**, no se revisa |
| Poda general de dependencias | Ninguna: ver §12, decisión **D-024-G** |

**`D-12` no se cierra aquí.** Respetar las cuotas de empaquetado no equivale a dimensionar
la función: memoria, *timeout*, concurrencia, arranque en frío y costo son de `Task/032`.

## 5. Entregables

| Entregable | Repositorio | Ruta |
| --- | --- | --- |
| Herramienta de construcción y validación | backend | `scripts/empaquetar_lambda.py` |
| Pruebas del empaquetador y sus validadores | backend | `tests/unit/test_empaquetado_lambda.py` |
| *Harness* de ejecución aislada dentro del runtime | backend | `scripts/arranque_aislado_lambda.py` |
| Gates de artefacto en CI | backend | `.github/workflows/ci-backend.yml` |
| Documentación del procedimiento | backend | `README.md` |
| Ficha | infra | `docs/tasks/TASK-024-lambda-zip-artifact.md` |
| Reporte | infra | `docs/task-reports/TASK-024-report.md` |
| Estado, roadmap y ficha de etapa | infra | `docs/project-management/STATUS.md`, `ROADMAP.md`, `docs/stages/STAGE-08-cloud-ready.md` |

Los **artefactos generados no se versionan**: `lambda_package/` y `*.zip` ya están en
`.gitignore` del backend desde `Task/005`. Lo que se versiona es la **herramienta**; lo
que queda como hecho histórico fechado es la **medición**, en el reporte.

## 6. Criterios de aceptación

1. El ZIP se construye dentro de la imagen oficial del runtime de Lambda para Python 3.12,
   `linux/amd64`, **fijada por digest**, y el digest queda registrado.
2. Las **41** distribuciones de `requirements.lock` se instalan como *wheel*, con
   `--require-hashes`; **ninguna** de las **20** exclusivas de desarrollo aparece.
3. Ninguna distribución se construye desde *sdist*. Si alguna careciera de *wheel*
   compatible, la tarea **se detiene** y lo reporta.
4. `app/` está **directamente en la raíz** del ZIP, con `app/lambda_handler.py` presente.
   No existe prefijo `lambda_package/`, `python/`, `site-packages/` ni `.venv/`.
5. Dos construcciones independientes, `A` y `B`, desde directorios distintos, producen
   **manifiestos idénticos**, **bytes idénticos** y **el mismo SHA-256**.
6. Un cambio real de contenido produce un **SHA-256 distinto**.
7. Se registran bytes comprimidos, bytes descomprimidos, margen frente a cada cuota y
   contribución por distribución.
8. El ZIP comprimido **no excede 52 428 800 bytes** y el contenido descomprimido **no
   excede 262 144 000 bytes** (política del proyecto, §12 **D-024-E**). Las cuotas son
   **inclusivas**: el gate rechaza a partir del primer byte por encima, como fija el caso
   **J2** de la matriz. La medición real quedó holgadamente por debajo de ambas.
9. Existe el `.sha256` y **verifica**; existe el manifiesto, y **ninguno de los dos viaja
   dentro del ZIP**.
10. El *handler* `app.lambda_handler.handler` responde `200` a un evento **HTTP API v2**
    `GET /health` ejecutado desde el **ZIP extraído**, en un proceso Linux limpio, con
    **`-W error`**, sin árbol de fuentes, sin dependencias externas al artefacto, sin
    `.env`, sin credenciales y sin acceso a AWS.
11. `isBase64Encoded` es `false`, el cuerpo es el JSON real de `/health` y las cabeceras
    relevantes están presentes.
12. Argon2, Pillow y el driver binario de PostgreSQL se **ejercitan**, no solo se
    comprueba que el `.so` existe. Toda extensión compilada del artefacto **carga**.
13. Los **tres controles negativos** de aislamiento fallan como se espera.
14. El ZIP no contiene `.env`, secretos, `.git`, `tests/`, `scripts/`, dependencias de
    desarrollo, `__pycache__`, `.pyc`, binarios de Windows, objetos de arquitectura
    distinta de x86-64, rutas absolutas, `..`, duplicados ni enlaces simbólicos.
15. Los gates preexistentes del backend siguen pasando **sin relajarse**: `ruff format
    --check`, `ruff check`, `mypy`, `pytest -W error` con la suite completa, migraciones,
    `pip check`, `pip-audit` sobre los dos locks (**S-09**), `docker build` y Trivy.
16. **C = 0 · D = 0** en el criterio 12 para los documentos tocados.

## 7. TDD / Plan test-first

`Task/024` **no** introduce comportamiento funcional del backend en el sentido estricto de
la Definition of Done: no toca dominio, casos de uso, API pública o administrativa,
persistencia, autenticación, auditoría ni `ObjectStorage`. Por eso **no** se afirma que
B-1…B-12 sean obligatorios por «backend funcional»
([`BACKEND_TESTING_STRATEGY.md`](../project-management/BACKEND_TESTING_STRATEGY.md) §4).

**Pero el empaquetador y sus validadores sí tienen lógica no trivial**, y a esa lógica se
le aplica la disciplina completa **RED → GREEN → REFACTOR**. Esta sección se completa
**antes** de escribir implementación.

### 7.1 Comportamientos a construir

1. **Inventario del lock**: leer `requirements.lock` y obtener el conjunto exacto de
   distribuciones de ejecución con su versión.
2. **Contraste del árbol instalado** contra ese inventario: ni falta ni sobra ninguna.
3. **Normalización del árbol**: eliminar *bytecode* y cachés; rechazar enlaces simbólicos.
4. **Recolección determinista de entradas**: rutas POSIX relativas, orden lexicográfico,
   sin duplicados, sin rutas absolutas, sin `..`.
5. **Política de contenido prohibido**: secretos, configuración local, control de
   versiones, pruebas, utilidades, dependencias de desarrollo.
6. **Política de binarios**: rechazar PE/COFF de Windows y todo ELF cuya arquitectura no
   sea x86-64.
7. **Escritura determinista del ZIP**: *timestamp* fijo, permisos normalizados, DEFLATE
   con nivel fijo, sistema de origen fijo, sin comentario.
8. **Medición y gates de tamaño** frente a las dos cuotas.
9. **Manifiesto y checksum**, fuera del ZIP.
10. **Verificación del *layout***: `app/` en la raíz y *handler* presente.

### 7.2 Matriz de casos

Se completa **antes** de escribir implementación. La letra es la del enunciado de la
tarea; la columna *Capa* clasifica dónde se prueba.

| # | Caso | Entrada | Precondición | Resultado esperado | Capa |
| --- | --- | --- | --- | --- | --- |
| **A1** | *Layout* correcto | Árbol con `app/lambda_handler.py` en la raíz | — | Verificación **pasa** | unidad |
| **A2** | *Handler* ausente | Árbol sin `app/lambda_handler.py` | — | **Falla** nombrando el módulo ausente | unidad |
| **A3** | *Layout* anidado | Árbol con `lambda_package/app/…` | — | **Falla**: `app/` no está en la raíz | unidad |
| **A4** | Prefijo de *layer* | Árbol con `python/app/…` | — | **Falla**: `python/` es de *layers* | unidad |
| **B1** | Dependencia faltante | Árbol sin `mangum-0.22.0.dist-info` | Lock con 41 | **Falla** nombrando `mangum` | unidad |
| **B2** | Inventario completo | Árbol con las 41 | Lock con 41 | **Pasa** | unidad |
| **C1** | Distribución extra | Árbol con `pytest-9.1.1.dist-info` | Lock de ejecución | **Falla** nombrando `pytest` | unidad |
| **C2** | Versión distinta | `fastapi-0.140.0.dist-info` | Lock pide `0.141.1` | **Falla** indicando ambas versiones | unidad |
| **D1** | Lock sin hashes | Línea `fastapi==0.141.1` sin `--hash` | — | **Falla**: el lock no es *fail-closed* | unidad |
| **D2** | Orden de instalación | — | — | El comando incluye `--require-hashes`, `--only-binary=:all:` y `--no-compile` | unidad |
| **D3** | Hash alterado | Lock con un `--hash` corrupto | Construcción real | `pip` **aborta**; no se produce artefacto | artefacto |
| **E1** | Binario de Windows | Archivo con magia `MZ` | — | **Falla** nombrando la ruta | unidad |
| **F1** | ELF de otra arquitectura | ELF con `e_machine` = AArch64 | — | **Falla** nombrando la ruta y la arquitectura | unidad |
| **F2** | ELF x86-64 | ELF con `e_machine` = x86-64 | — | **Pasa** | unidad |
| **G1** | *Timestamps* variables | Dos árboles idénticos con `mtime` distintos | — | ZIP **idéntico**: el *timestamp* es fijo | unidad |
| **G2** | Orden de recorrido variable | Mismo árbol, entradas entregadas desordenadas | — | Entradas en **orden lexicográfico** idéntico | unidad |
| **G3** | Permisos variables | Mismo archivo con modos distintos | — | Permisos **normalizados** en el ZIP | unidad |
| **H1** | Entradas equivalentes → ZIP idéntico | Dos árboles equivalentes en directorios distintos | — | **Mismos bytes** y mismo SHA-256 | unidad |
| **H2** | Reproducibilidad real | Build `A` y build `B` | Docker con imagen fijada | **Mismos bytes**, mismo SHA-256, manifiesto idéntico | artefacto |
| **I1** | Cambio real → checksum distinto | Un byte distinto en un archivo | — | SHA-256 **distinto** | unidad |
| **J1** | Tamaño por debajo del umbral | Medida < cuota | — | **Pasa**, con margen registrado | unidad |
| **J2** | Tamaño exactamente en el umbral | Medida == cuota | — | **Pasa**: la cuota es inclusiva | unidad |
| **J3** | Tamaño por encima | Medida == cuota + 1 | — | **Falla** indicando exceso | unidad |
| **J4** | Medición real | Artefacto real | — | Comprimido < 50 MiB y descomprimido < 250 MiB | artefacto |
| **K1** | `.env` en el árbol | Archivo `.env` | — | **Falla** | unidad |
| **K2** | `.env` anidado | `app/.env` | — | **Falla** | unidad |
| **L1** | Secreto por nombre | `credentials.json`, `id_rsa`, `*.pem` | — | **Falla** nombrando la ruta | unidad |
| **L2** | `.git` | `.git/config` | — | **Falla** | unidad |
| **M1** | Pruebas del proyecto | `tests/unit/test_x.py` | — | **Falla** | unidad |
| **M2** | Utilidades del proyecto | `scripts/seed_local.py` | — | **Falla** | unidad |
| **N1** | Dependencia de desarrollo | `pytest/`, `ruff/`, `mypy/` | — | **Falla** (mismo gate que **C1**) | unidad |
| **O1** | `__pycache__` | `app/__pycache__/main.cpython-312.pyc` | — | Se **elimina** en la normalización | unidad |
| **O2** | `.pyc` suelto | `app/main.pyc` | — | **Falla** si sobrevive a la normalización | unidad |
| **O3** | Cachés de herramientas | `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/` | — | Se **eliminan** | unidad |
| **P1** | *Path traversal* | Entrada `../fuera.py` | — | **Falla** | unidad |
| **Q1** | Ruta absoluta | Entrada `/etc/passwd` o `C:\x` | — | **Falla** | unidad |
| **R1** | Entradas duplicadas | Misma ruta dos veces | — | **Falla** | unidad |
| **S1** | Enlace simbólico | *Symlink* dentro del árbol | — | **Falla**: la política los prohíbe | unidad |
| **T1** | *Handler* real desde ZIP aislado | Evento HTTP API v2 `GET /health` | ZIP extraído, proceso Linux limpio, `-W error` | `statusCode == 200`, `isBase64Encoded == false`, cuerpo `{"status":"ok",…}`, `content-type: application/json` | artefacto |
| **T2** | Módulos críticos desde el artefacto | `fastapi`, `starlette`, `mangum`, `pydantic`, `sqlalchemy`, `boto3`, `alembic` | Igual que **T1** | Todos resuelven **desde el ZIP extraído** | artefacto |
| **U1** | Dependencia retirada, copia en `PYTHONPATH` | Sin `mangum/`; copia en `/externo`, `PYTHONPATH=/externo`, `cwd=/externo` | — | **Falla** igualmente | artefacto |
| **U2** | Dependencia retirada, copia en *site-packages* del entorno | Sin `boto3/`; la imagen trae `boto3` preinstalado | — | **Falla** igualmente | artefacto |
| **U3** | `app/` retirada, árbol de fuentes montado | Sin `app/`; repositorio en `/src`, `cwd=/src` | — | **Falla** igualmente | artefacto |
| **V1** | Argon2 | `PasswordHasher.hash` + `verify` | Offline | Verifica correctamente | artefacto |
| **V2** | Pillow | Crear, guardar PNG y JPEG en memoria, reabrir | Offline | Dimensiones y modo correctos | artefacto |
| **V3** | Driver binario de PostgreSQL | `psycopg.pq.__impl__` y `version()` | Offline, **sin conectar** | Implementación `binary`, versión de `libpq` legible | artefacto |
| **V4** | Toda extensión compilada | Cada `.so` del artefacto | Offline | **Carga** sin error | artefacto |

### 7.3 Tests RED esperados

Todos sobre `scripts/empaquetar_lambda.py`, que **no existe** al escribir esta sección. El
primer RED es, por tanto, `ModuleNotFoundError`; a partir de que el módulo exista, cada
test debe fallar **por la razón de su fila**, no por ausencia de módulo. Esa distinción se
registra en el reporte.

| Test | Capa | Motivo de fallo esperado |
| --- | --- | --- |
| `test_el_layout_valido_se_acepta` | unidad | `ModuleNotFoundError` → luego verificación inexistente |
| `test_el_layout_sin_handler_se_rechaza` | unidad | No se detecta la ausencia del *handler* |
| `test_el_layout_anidado_se_rechaza` | unidad | No se detecta el prefijo |
| `test_el_prefijo_de_layer_se_rechaza` | unidad | No se detecta `python/` |
| `test_una_distribucion_faltante_se_rechaza` | unidad | No hay contraste con el lock |
| `test_una_distribucion_extra_se_rechaza` | unidad | No hay contraste con el lock |
| `test_una_version_distinta_se_rechaza` | unidad | No se compara la versión |
| `test_un_lock_sin_hashes_se_rechaza` | unidad | No se exige `--hash` |
| `test_el_comando_de_instalacion_es_fail_closed` | unidad | No existe el comando |
| `test_un_binario_de_windows_se_rechaza` | unidad | No se inspecciona la magia del archivo |
| `test_un_elf_de_otra_arquitectura_se_rechaza` | unidad | No se lee `e_machine` |
| `test_los_timestamps_del_arbol_no_afectan_al_zip` | unidad | El ZIP hereda el `mtime` |
| `test_las_entradas_van_en_orden_lexicografico` | unidad | Se conserva el orden de entrega |
| `test_los_permisos_se_normalizan` | unidad | El ZIP hereda el modo |
| `test_dos_arboles_equivalentes_producen_el_mismo_zip` | unidad | Bytes distintos |
| `test_un_cambio_real_cambia_el_checksum` | unidad | No hay checksum |
| `test_el_gate_de_tamano_acepta_debajo_y_en_el_umbral` | unidad | No hay gate |
| `test_el_gate_de_tamano_rechaza_por_encima` | unidad | No hay gate |
| `test_un_env_se_rechaza` | unidad | No hay política de contenido |
| `test_un_secreto_por_nombre_se_rechaza` | unidad | No hay política de contenido |
| `test_el_control_de_versiones_se_rechaza` | unidad | No hay política de contenido |
| `test_las_pruebas_del_proyecto_se_rechazan` | unidad | No hay política de contenido |
| `test_las_utilidades_del_proyecto_se_rechazan` | unidad | No hay política de contenido |
| `test_el_bytecode_se_elimina_en_la_normalizacion` | unidad | No hay normalización |
| `test_un_pyc_superviviente_se_rechaza` | unidad | No hay política de contenido |
| `test_una_ruta_con_traversal_se_rechaza` | unidad | No hay validación de rutas |
| `test_una_ruta_absoluta_se_rechaza` | unidad | No hay validación de rutas |
| `test_una_entrada_duplicada_se_rechaza` | unidad | No hay detección de duplicados |
| `test_un_enlace_simbolico_se_rechaza` | unidad | No hay política de enlaces |
| `test_el_manifiesto_registra_la_procedencia` | unidad | No hay manifiesto |
| `test_el_checksum_y_el_manifiesto_no_viajan_dentro_del_zip` | unidad | No hay separación |

Los casos de capa **artefacto** (`D3`, `H2`, `J4`, `T*`, `U*`, `V*`) no se prueban con
`pytest`: exigen Docker, la imagen fijada y varios minutos de descarga. Son **pasos
propios** de la herramienta y de `CI Backend`, con su evidencia en el reporte. Meterlos en
la suite unitaria la volvería lenta y dependiente de Docker sin ganar rigor.

### 7.4 Integración necesaria

**No** se necesita PostgreSQL ni MinIO: el artefacto se valida **offline y sin
credenciales**, y `GET /health` es una sonda de vivacidad que no consulta dependencias
(`app/api/health.py`). El driver de PostgreSQL se ejercita **sin conectar**.

Lo que sí se necesita es **Docker** con la imagen oficial del runtime de Lambda fijada por
digest. Es la única autoridad admisible sobre «qué rueda es compatible con el runtime
destino»: el backend se desarrolla en Windows y la pregunta no se puede responder allí.

### 7.5 Casos negativos y de seguridad

Cubiertos por **K, L, M, N, O, P, Q, R, S** (contenido prohibido y rutas) y por **U1–U3**
(aislamiento). El ZIP no debe poder llevar una credencial, y el *harness* no debe poder
aprobar un artefacto incompleto tomando prestada una dependencia del entorno.

**S-09 no se relaja**: sin `.trivyignore`, sin exclusiones de `pip-audit`, sin hashes
opcionales, sin *fallback* a *sdist* y sin advertencias silenciadas.

### 7.6 Regresiones relevantes

- La suite completa del backend —**1918 passed, 1 skipped** en el cierre de `Task/023`—
  debe seguir en verde con `-W error`.
- `tests/unit/test_guarda_del_adaptador_lambda.py`: **T-04** sigue satisfecho; `mangum` no
  puede aparecer fuera de `app/lambda_handler.py`. El empaquetador vive en `scripts/`, no
  en `app/`, precisamente para no tocar esa guarda.
- `tests/unit/test_arranque_del_handler_lambda.py`: el bucle de eventos del *handler*.
- `tests/test_hermeticidad.py`: la suite no depende del entorno de la máquina.
- **R-14**: `sh scripts/generar-locks.sh` seguido de `git diff --exit-code` sobre los dos
  locks. Esta tarea **no** modifica dependencias, así que el lock no puede moverse.
- **H-023-3** sigue **abierto y no diagnosticado**. Si
  `test_dos_publicaciones_simultaneas_solo_prosperan_una` reaparece, se conserva traza,
  comando, entorno, SHA, momento, duración y contexto, y **la tarea se detiene**. No se
  reintenta hasta verde, no se declara *flake* y no se atribuye al ZIP ni a Mangum sin
  evidencia.

## 8. Plan de validación

| Criterio | Cómo se comprueba |
| --- | --- |
| 1 | El manifiesto registra referencia, digest de la lista de manifiestos, digest de `linux/amd64`, arquitectura, Python, `pip`, `zlib` y base del sistema, leídos **de la imagen**, no escritos a mano |
| 2, 3 | Inventario del artefacto contrastado con `requirements.lock`; la salida de `pip` demuestra que toda distribución vino como *wheel* |
| 4 | Verificación de *layout* sobre el ZIP construido |
| 5 | Builds `A` y `B` en directorios independientes; comparación de SHA-256, de bytes y de manifiestos |
| 6 | Alteración deliberada de un archivo y recomparación del checksum |
| 7, 8 | Medición de la herramienta, con desglose por distribución |
| 9 | `sha256sum --check` sobre el `.sha256`; inventario del ZIP sin manifiesto ni checksum dentro |
| 10, 11 | *Harness* de ejecución aislada, con su evento y su respuesta completa |
| 12 | Ejercicios nativos del *harness* |
| 13 | Tres ejecuciones de control negativo, cada una con su fallo esperado |
| 14 | Gates de contenido sobre el artefacto real |
| 15 | Los pasos preexistentes del backend, localmente y en `CI Backend` |
| 16 | Criterio 12 sobre los documentos tocados |

## 9. Comandos de validación

```bash
# Backend — gates preexistentes, sin relajar
ruff format --check .
ruff check .
mypy .
pytest -W error
python -m pip check
sh scripts/generar-locks.sh && git diff --exit-code -- requirements.lock requirements-dev.lock

# Backend — artefacto (requiere Docker; sin AWS y sin credenciales)
python scripts/empaquetar_lambda.py construir --destino lambda_package/A
python scripts/empaquetar_lambda.py construir --destino lambda_package/B
python scripts/empaquetar_lambda.py comparar   lambda_package/A lambda_package/B
python scripts/empaquetar_lambda.py verificar  lambda_package/A
python scripts/empaquetar_lambda.py ejecutar-aislado lambda_package/A
python scripts/empaquetar_lambda.py control-negativo lambda_package/A

# Infra
git diff --check
```

## 10. Evidencia esperada

- Referencia y **digest** de la imagen del runtime, con Python, `pip`, `zlib` y base.
- Inventario de las **41** distribuciones y ausencia de las **20** de desarrollo.
- **SHA-256** de `A` y de `B`, idénticos, y comparación de bytes.
- Bytes comprimidos y descomprimidos, margen frente a ambas cuotas y desglose por
  distribución.
- Respuesta completa del *handler* al evento `GET /health`.
- Salida de los ejercicios nativos.
- Salida de los **tres** controles negativos, con el error de cada uno.
- Suite completa del backend y todos los gates preexistentes.

## 11. Riesgos

| # | Riesgo | Impacto | Mitigación |
| --- | --- | --- | --- |
| R-024-1 | Una distribución sin *wheel* para el runtime destino | La construcción no es posible sin *sdist* | `--only-binary=:all:`: la construcción **falla** y se reporta como hallazgo. **No** se actualizan dependencias para forzar el verde |
| R-024-2 | La etiqueta de la imagen del runtime se mueve | La reproducibilidad se pierde en silencio | Digest inmutable registrado; la etiqueta sola nunca es garantía |
| R-024-3 | El *harness* toma prestada una dependencia del entorno | Un artefacto incompleto pasaría por válido | Aislamiento con `-I -S` y `sys.path` reconstruido, más **tres controles negativos** |
| R-024-4 | Construir en Windows por comodidad | Binarios inservibles en Lambda | La construcción ocurre **solo** dentro del contenedor Linux; el `.venv` de Windows nunca se copia |
| R-024-5 | Declarar reproducibilidad comparando listas de archivos | Garantía falsa | La comparación es de **bytes** y de **SHA-256**, nunca solo de inventario |
| R-024-6 | Prometer reproducibilidad universal | Afirmación indefendible | El alcance de la garantía se documenta explícitamente (**D-024-F**) |
| R-024-7 | Confundir la cuota de carga directa con una prohibición | Documentación falsa | Se documenta que **50 MB es el límite de carga directa** y que por S3 se admite más |
| R-024-8 | Podar dependencias para reducir tamaño | Rotura silenciosa en producción | **D-024-G**: no se poda nada; solo se mide |
| R-024-9 | **H-023-3** reaparece | Diagnóstico erróneo atribuido al ZIP | Se conserva la traza completa y **la tarea se detiene** |

## 12. Decisiones técnicas

**Estado de las decisiones: Aceptadas y Vigentes** desde el 2026-09-13, con la aprobación
de la tarea. Son decisiones de **implementación dentro de la arquitectura ya aprobada**
—ADR-003 ya fija Lambda como destino—, así que **no crean ni reemplazan ningún ADR**.

| Decisión | Alternativas consideradas | Justificación | ¿ADR? |
| --- | --- | --- | --- |
| **D-024-A** — La autoridad de construcción es la **imagen oficial del runtime de Lambda para Python 3.12**, `linux/amd64`, fijada por digest | `python:3.12.14-slim` del `Dockerfile`; construir en el *runner* de CI; construir en Windows | La pregunta que hay que responder es «¿esta rueda carga en el runtime destino?», y solo el runtime destino la responde. La base es **AL2023 con glibc 2.34**, que acepta `manylinux2014`, `manylinux_2_26`, `manylinux_2_28` y `manylinux_2_34`: por eso **no** se impone ciegamente `manylinux2014`. El `Dockerfile` del backend, además, **actualiza paquetes Debian después del `FROM`**, así que su digest no determina el sistema de archivos final y no sirve como autoridad de reproducibilidad | No |
| **D-024-B** — El ZIP se **escribe dentro del contenedor**, no en el anfitrión | Escribirlo en Windows tras extraer el árbol | Los bytes de DEFLATE dependen de la versión de `zlib`. Escribiéndolo dentro, `zlib` y Python quedan fijados por el mismo digest, y `A == B` se sostiene también entre Windows y el *runner* de CI. Escribiéndolo fuera, la reproducibilidad solo valdría dentro de una misma máquina | No |
| **D-024-C** — *Timestamp* fijo `1980-01-01 00:00:00` y permisos normalizados | *Epoch* Unix `1970-01-01`; `SOURCE_DATE_EPOCH` | El formato ZIP guarda fecha **MS-DOS**, cuyo mínimo representable es 1980-01-01: `1970` no es expresable y `zipfile` lo rechaza. Comprobado contra la biblioteca empleada antes de adoptarlo | No |
| **D-024-D** — El ZIP contiene **solo entradas de archivo**, sin entradas de directorio | Emitir también directorios | Menos superficie no determinista y Lambda no las exige. Queda documentado | No |
| **D-024-E** — Política conservadora del proyecto: comprimido **< 52 428 800 bytes**, descomprimido **< 262 144 000 bytes** | Adoptar solo el límite descomprimido; no poner gate | Verificado contra la documentación oficial vigente el 2026-09-13: `50 MB (zipped, when uploaded through the Lambda API or SDKs)` —**carga directa**, ampliable vía S3— y `250 MB … including layers and custom runtimes (unzipped)`. La propia página aclara que usa **MB por 1 024 KB**, de donde salen los bytes exactos. Quedarse por debajo del límite de carga directa mantiene abierta la vía simple de despliegue para `Task/025` | No |
| **D-024-F** — El alcance de la garantía de reproducibilidad se **documenta y se acota** | Declarar «reproducible» sin condiciones | La garantía vale con: mismas fuentes, mismos locks, mismos artefactos de dependencias, mismas herramientas fijadas y el mismo entorno de construcción controlado. **No** se promete que PyPI conserve los archivos indefinidamente ni reproducibilidad universal en cualquier máquina o herramienta | No |
| **D-024-G** — **No se poda ninguna dependencia** | Retirar `uvicorn`, `uvloop`, `watchfiles`, `websockets`, `httptools` o `alembic` para reducir tamaño | Están declaradas en el lock de **ejecución**; el artefacto cabe con margen, así que no hay necesidad que justifique el riesgo. Podar exigiría demostrar que no pertenecen al runtime real, justificar, analizar impacto, regenerar locks y autorización explícita. `Task/024` **mide** qué pesa cada una y deja el dato; no se convierte en limpieza general de dependencias | No |
| **D-024-H** — **`boto3` y `botocore` se empaquetan** desde el lock | Confiar en los que trae el runtime de Lambda | Verificado en la imagen: trae `boto3 1.42.97` / `botocore 1.42.97`, mientras el lock fija `1.43.82` / `1.43.91`. Depender del runtime significaría ejecutar en producción un SDK que **ninguna prueba validó**, y que AWS puede cambiar sin aviso | No |
| **D-024-I** — El empaquetador vive en `scripts/`, **nunca en `app/`** | `app/empaquetado.py`; un paquete nuevo de primer nivel | `app/` es lo que viaja al artefacto y lo que recorre la guarda de **T-04**. Una herramienta de construcción dentro de `app/` se empaquetaría a sí misma. `scripts/` ya está excluido de la imagen por `.dockerignore` y es *first-party* para isort | No |
| **D-024-J** — Herramienta en **Python de biblioteca estándar**, con Docker como autoridad Linux | `make`, `just`, `bash`, PowerShell, `Dockerfile` auxiliar | No se introduce ninguna familia de *tooling* nueva ni un gate nuevo que mantener. `zipfile`, `hashlib`, `json`, `subprocess` y `pathlib` bastan. El gate de infra *«No shell scripts yet»* queda intacto: esta tarea no añade ningún `.sh` en ningún repositorio | No |
| **D-024-K** — El artefacto **no** se publica como *GitHub Actions Artifact* | Subirlo en cada ejecución | No hay necesidad demostrada: el ZIP se construye, se valida y se descarta; la evidencia durable vive en el reporte. Introducir retención y transferencia sin requisito añadiría costo y superficie. `Task/025` reconstruye por el mismo mecanismo canónico y `Task/038` es responsable de la automatización del despliegue | No |

Ninguna decisión de esta tarea modifica una decisión arquitectónica aceptada, así que
**no se crea ni se reemplaza ningún ADR**.

## 13. Documentación creada o actualizada

- `docs/tasks/TASK-024-lambda-zip-artifact.md` — esta ficha (creada).
- `docs/task-reports/TASK-024-report.md` — reporte de la tarea (creado).
- `docs/project-management/STATUS.md` — tarea en curso, etapa y contadores.
- `docs/project-management/ROADMAP.md` — fila de `Task/024`: estado y columna *Repos*.
- `docs/stages/STAGE-08-cloud-ready.md` — entrada de `Task/024`: estado y campo
  *Repositorio*.
- `docs/architecture/aws-local-parity.md` y `docs/architecture/production-postgresql-vps.md`
  — **D-024-2**: el estado documental de `images/Infraestructura.png`, que `Task/006.2`
  declaró obsoleto pero solo corrigió en dos de los cuatro sitios. Análisis completo en el
  [reporte §14](../task-reports/TASK-024-report.md). **La imagen no se toca.**
- `personal-blog-backend/README.md` — procedimiento de construcción y validación.

## 14. Archivos modificados

El detalle definitivo vive en el [reporte](../task-reports/TASK-024-report.md).

## 15. Resultado de pruebas

El detalle definitivo vive en el [reporte](../task-reports/TASK-024-report.md).
**Si algo falla, se registra tal cual.**

## 16. Problemas encontrados

El detalle definitivo vive en el [reporte](../task-reports/TASK-024-report.md).

## 17. Pasos de validación para el usuario

En el [reporte](../task-reports/TASK-024-report.md).

## 18. Deuda técnica pendiente

- **P-07** queda con la evidencia del tramo de artefacto registrada —tamaño, composición,
  reproducibilidad y ejecución del artefacto—; la **validación del arranque real** es de
  `Task/032`.
- **D-12** sigue **ABIERTA**: `Task/032`.
- **H-023-3** sigue **ABIERTO y no diagnosticado**.
- **R-018-3** sigue **ABIERTO** (residual de MinIO), ajeno a esta tarea.

## 19. Próxima tarea

`Task/025-Terraform-Cloud` — Terraform portable con el provider oficial de AWS, `plan`,
`apply` y `destroy` ejecutados contra el laboratorio local, matriz de paridad y guardas
*fail-closed*. **No se inicia** hasta que `Task/024` esté Aprobada y normalizada.

## 20. Aprobación

| Campo | Valor |
| --- | --- |
| **Fecha de aprobación** | **2026-09-13** |
| **Aprobado por** | **El usuario** |
| **Expresión de aprobación** | `approved: Task/024-Artefacto-ZIP-Lambda` |
| **Efecto** | Avance **24/41 ≈ 59 %**; **ETAPA 08 En progreso, 2 de 4 — 50 %**. **D-024-A … D-024-K Aceptadas y Vigentes** |

> Completada al recibir la expresión exacta de aprobación del usuario. La etapa **no queda
> completada**: `Task/025` y `Task/026` siguen **Pendientes**.
