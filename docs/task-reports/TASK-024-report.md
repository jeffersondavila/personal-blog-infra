# TASK-024 — Reporte de tarea

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/024-Artefacto-ZIP-Lambda` |
| **Etapa** | ETAPA 08 — Preparación Cloud + AWS Local Parity |
| **Estado** | **Aprobada** el 2026-09-13 mediante `approved: Task/024-Artefacto-ZIP-Lambda` |
| **Fecha** | 2026-09-13 |
| **Ficha** | [TASK-024-lambda-zip-artifact.md](../tasks/TASK-024-lambda-zip-artifact.md) |
| **Repositorios modificados** | `personal-blog-backend` —propiedad funcional—, `personal-blog-infra` (documentación/gobierno) |
| **Frontend** | **Sin cambios.** Solo lectura, sin rama |
| **Avance** | **24/41 ≈ 59 %.** Con la aprobación pasa de 23/41 ≈ 56 %. **ETAPA 08: 2 de 4 — 50 %** |

> Las decisiones **D-024-A** a **D-024-K** quedan **Aceptadas y Vigentes** desde el
> 2026-09-13. Son decisiones de **implementación dentro de la arquitectura ya aprobada**
> (ADR-003 ya fija Lambda como destino): **no crean ni reemplazan ningún ADR**.

---

## 1. Ramas y SHA base

*Observado el 2026-09-13, tras `git fetch --prune origin`:*

| Repo | Rama | Base | SHA base | `HEAD == main` |
| --- | --- | --- | --- | --- |
| `personal-blog-backend` | `Task/024-Artefacto-ZIP-Lambda` | **`main`** | `8795ac750f3cdfaacc1d9edd8bd9c94a0726f5b1` | ✔ |
| `personal-blog-infra` | `Task/024-Artefacto-ZIP-Lambda` | **`main`** | `7397eca76a282f4edb5a9da6b7d588bfd5f68efc` | ✔ |
| `personal-blog-frontend` | *(sin rama)* | — | `7dce98aff239d61ae3ae15213d9a3f5ebf0fb8ce` | — |

En los tres repositorios `main == origin/main`, el árbol de trabajo estaba **limpio** y no
existía ninguna rama `Task/*` previa. `main` es ancestro de `dev` y su contenido coincide
en backend e infra: la normalización posterior a `Task/023` estaba completa. **Ninguna
rama nació de `dev`.**

---

## 2. Verificación del runtime destino **antes** de fijarlo

La ficha exigía no adoptar una etiqueta móvil como garantía. Lo observado el 2026-09-13,
leído **de la imagen**, no escrito a mano:

| Campo | Valor |
| --- | --- |
| Etiqueta | `public.ecr.aws/lambda/python:3.12` |
| Digest de la lista de manifiestos | `sha256:a89893d9c93a9ffbf9e35ca32d7cadc635cbf3a9aec94480c75ed07150a05daa` |
| Digest de `linux/amd64` | `sha256:e369e098d9db9eafa3238fe827e4756e2016159908b9426b78e2051c08f647e3` |
| Base | Amazon Linux 2023 |
| `glibc` | **2.34** |
| Python | **3.12.14** |
| `pip` | 25.0.1 |
| `zlib` | 1.2.11 (compilación y ejecución) |
| Arquitectura | `x86_64` |

Dos consecuencias que **cambian el plan de preflight**:

1. **No se impone `manylinux2014`.** Con glibc 2.34 son compatibles `manylinux2014`
   (2.17), `manylinux_2_26`, `manylinux_2_28` y `manylinux_2_34`. La autoridad es la
   **carga real** en este runtime, no una etiqueta elegida de antemano. En la práctica
   `pip` resolvió ruedas `manylinux_2_28`, `manylinux_2_17` y `manylinux1` según la
   distribución, y todas cargaron.
2. **El Python del runtime coincide exactamente** con el que fija el proyecto
   (`VERSION_DE_PYTHON: '3.12.14'` en `CI Backend`, y el `FROM` del `Dockerfile`).

**`public.ecr.aws` es un registro público de contenedores.** No exige cuenta ni
credenciales AWS, y ningún paso de esta tarea creó, consultó ni contactó un recurso de
AWS.

---

## 3. Por qué el `Dockerfile` del backend **no** sirve como autoridad

`Dockerfile` parte de `python:3.12.14-slim` con digest fijado, pero después ejecuta
`apt-get update && apt-get upgrade`. Eso es correcto para esa imagen —`Task/020.3` lo
introdujo para resolver **B-020.3-C**, y el propio archivo registra la consecuencia
aceptada—, pero significa que **su digest no determina el sistema de archivos final**.
Una construcción reproducible no puede apoyarse en él. Además es Debian, no AL2023, así
que tampoco responde la pregunta que importa: *«¿esta rueda carga en el runtime de
Lambda?»*. Decisión **D-024-A**.

---

## 4. Matriz test-first y su resultado

La matriz completa está en la [ficha §7.2](../tasks/TASK-024-lambda-zip-artifact.md),
escrita **antes** de la implementación. Resultado por familia:

| Familia | Casos | Capa | Resultado |
| --- | --- | --- | --- |
| **A** *layout* y *handler* | A1–A4 | unidad | ✔ |
| **B/C** inventario frente al lock | B1, B2, C1, C2 | unidad | ✔ |
| **D** hashes y *fail-closed* | D1, D2 | unidad | ✔ |
| **D3** hash alterado | D3 | artefacto | ✔ §8 |
| **E/F** binarios y arquitectura | E1, F1, F2 | unidad | ✔ |
| **G/H/I** determinismo y checksum | G1–G3, H1, I1 | unidad | ✔ |
| **H2/I** reproducibilidad real | H2, cambio real | artefacto | ✔ §7 |
| **J** cuotas de tamaño | J1–J3 | unidad | ✔ |
| **J4** medición real | J4 | artefacto | ✔ §6 |
| **K/L/M/N/O** contenido prohibido | K1–O3 | unidad | ✔ |
| **P/Q/R/S** rutas y enlaces | P1, Q1, R1, S1 | unidad | ✔ (**S1 omitido en Windows**, §12) |
| **T/U/V** ejecución aislada, aislamiento y nativas | T1, T2, U1–U3, V1–V4 | artefacto | ✔ §9 y §10 |

---

## 5. RED demostrado

**RED 1 — el módulo no existe.** Con la matriz escrita y las **49** pruebas creadas antes
de cualquier implementación:

```
ModuleNotFoundError: No module named 'scripts.empaquetar_lambda'
1 error durante la recoleccion
```

**RED 2 — cada prueba falla por la razón de su fila.** Un `ModuleNotFoundError` no
demuestra que las pruebas comprueben algo: solo que falta un archivo. Por eso se escribió
a continuación un **esqueleto deliberadamente ingenuo** —la implementación que saldría de
no leer los requisitos: recolecta archivos, los mete en un ZIP con los valores por defecto
de `zipfile` y **no valida nada**—. Sobre él:

```
37 failed, 11 passed, 1 skipped in 0.96s
```

Los **37** fallos son exactamente los casos negativos de la matriz, cada uno por su propio
motivo: `verificar_layout` no detecta el prefijo, el ZIP hereda el `mtime` del archivo, no
hay contraste con el lock, no hay política de contenido, no hay manifiesto. Los **11** que
pasan son los casos **positivos** —*layout* válido aceptado, contenido legítimo aceptado,
lock de ejemplo leído— que **deben** pasar con una implementación permisiva: si hubieran
fallado, el problema estaría en la prueba.

Dos matices registrados por honestidad:

- `test_dos_arboles_equivalentes_producen_el_mismo_zip` **pasó** con el esqueleto, porque
  los dos árboles se crean en el mismo segundo y heredan el mismo `mtime`. El caso queda
  realmente cubierto por `test_los_timestamps_del_arbol_no_afectan_al_zip`, que **sí**
  falló.
- `test_el_manifiesto_es_deterministico` pasó comparando `{} == {}`. Adquirió sentido en
  cuanto el manifiesto existió.

**GREEN.** Con la implementación real: **48 passed, 1 skipped**.

**REFACTOR.** No se ejecutó ninguno que cambiara el diseño: la implementación nació de la
matriz y no hubo duplicación que extraer. Los únicos cambios posteriores fueron de
formato y tipado, exigidos por `ruff` y `mypy --strict`, sin tocar comportamiento.

### Un test corregido, y por qué no es acomodar el código

`test_el_manifiesto_es_deterministico` falló en GREEN porque **la prueba** nombraba los
dos ZIP `A.zip` y `B.zip`, mientras el flujo real escribe **siempre**
`personal-blog-backend-lambda.zip` y lo que cambia es el **directorio**. El manifiesto
registra el nombre del artefacto, y eso es correcto. Se corrigió la prueba para que
modele el flujo real —mismo nombre, directorios distintos—, que es **reforzar** la
expectativa, no debilitarla: la prueba sigue exigiendo manifiestos idénticos. No se
modificó ninguna aserción del comportamiento.

---

## 6. Medición del artefacto

*Observado el 2026-09-13.*

| Magnitud | Valor | Cuota | Margen | Uso |
| --- | --- | --- | --- | --- |
| **Comprimido** | **43 288 578** B (41,28 MiB) | 52 428 800 B | 9 140 222 B | 82,6 % |
| **Descomprimido** | **114 086 988** B (108,80 MiB) | 262 144 000 B | 148 057 012 B | 43,5 % |
| Entradas | **3 975** | — | — | — |
| Distribuciones | **41** de ejecución | 41 del lock | — | 100 % |
| Dependencias de desarrollo | **0** | — | — | — |

**Contribución por distribución** (bytes descomprimidos):

| Distribución | Bytes | % | | Distribución | Bytes | % |
| --- | ---: | ---: | --- | --- | ---: | ---: |
| `botocore` | 20 292 736 | 17,79 | | `fastapi` | 822 802 | 0,72 |
| `pillow` | 19 667 688 | 17,24 | | `cffi` | 735 422 | 0,64 |
| `psycopg-binary` | 19 017 166 | 16,67 | | `psycopg` | 732 428 | 0,64 |
| `uvloop` | 16 386 832 | 14,36 | | **`app`** | **725 838** | **0,64** |
| `sqlalchemy` | 13 226 383 | 11,59 | | `anyio` | 512 638 | 0,45 |
| `pydantic-core` | 5 093 464 | 4,46 | | `click` | 447 917 | 0,39 |
| `pyyaml` | 2 903 826 | 2,55 | | `python-dateutil` | 441 812 | 0,39 |
| `greenlet` | 2 048 012 | 1,80 | | `urllib3` | 432 606 | 0,38 |
| `pydantic` | 1 892 986 | 1,66 | | `s3transfer` | 341 586 | 0,30 |
| `httptools` | 1 799 112 | 1,58 | | `idna` | 337 471 | 0,30 |
| `watchfiles` | 1 190 161 | 1,04 | | `mako` | 280 462 | 0,25 |
| `alembic` | 1 079 065 | 0,95 | | `uvicorn` | 267 569 | 0,23 |
| `boto3` | 991 022 | 0,87 | | `starlette` | 266 458 | 0,23 |
| `websockets` | 829 384 | 0,73 | | **resto (17)** | 1 641 649 | 1,44 |

El reparto usa el `RECORD` de cada *wheel*, que es la fuente autoritativa de qué archivo
pertenece a qué distribución; por eso `PIL/` y `pillow.libs/` quedan atribuidos a
`pillow`, y `psycopg_binary.libs/` a `psycopg-binary`. `bin/` (3 650 B) e `include/`
(4 755 B) son subproductos de `pip install --target` y se conservan tal cual.

**El código propio es el 0,64 % del artefacto.** El peso es de las dependencias, y esa es
la medida que **P-07** necesitaba y que `Task/032` usará para dimensionar.

### Sobre las cuotas

Verificado en la documentación oficial de AWS el 2026-09-13
(`docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html`):

> *«Deployment package (.zip file archive) size — 50 MB (zipped, when uploaded through the
> Lambda API or SDKs). Upload larger files with Amazon S3. 50 MB (when uploaded through
> the Lambda console). 250 MB The maximum size of the contents of a deployment package,
> including layers and custom runtimes. (unzipped)»*

La misma página advierte: *«The Lambda documentation, log messages, and console use the
abbreviation MB (rather than MiB) to refer to 1,024 KB»*, de donde salen **52 428 800** y
**262 144 000** bytes exactos.

**Los 50 MB son el límite de carga directa, no una prohibición.** Un paquete mayor se
despliega desde Amazon S3. Este proyecto adopta la política conservadora de quedar por
debajo (**D-024-E**) para mantener abierta la vía simple de despliegue de `Task/025`,
**no** porque Lambda prohíba lo contrario.

---

## 7. Reproducibilidad — demostrada byte a byte

Dos construcciones **independientes**, en directorios distintos y en contenedores
efímeros distintos:

```
  A  .../lambda_package/A/personal-blog-backend-lambda.zip
     sha256 6580410109207f330a329ee235e0424a6bb3f7d96d14f550c4605eb3d8a02841  43288578 bytes
  B  .../lambda_package/B/personal-blog-backend-lambda.zip
     sha256 6580410109207f330a329ee235e0424a6bb3f7d96d14f550c4605eb3d8a02841  43288578 bytes
  bytes identicos      True
  sha256 identico      True
  manifiesto identico  True
Reproducibilidad demostrada: A == B byte a byte.
```

**La comparación es de bytes y de SHA-256, nunca de listas de archivos.** Dos ZIP con el
mismo inventario y distintos bytes no son reproducibles.

**Contraprueba (criterio 6).** Con **una línea de comentario añadida** a `app/main.py`, la
construcción dio `19907cafb8760bf8bafead2b6c1d09e65a3feff533408cb622300a88347aa306`
—distinto—. Tras revertir la línea con `git checkout --`, una construcción nueva volvió a
dar **exactamente** `6580410109207f33…`: el determinismo sobrevive a un cambio y su
reversión, y no es un artefacto de haber construido dos veces seguidas.

### Qué se controla

| Control | Cómo |
| --- | --- |
| Mismos *wheels* | `--require-hashes` sobre `requirements.lock` (`sha256:2ec5558e…`) |
| Directorios independientes | Contenedor efímero nuevo por construcción; `/build` se recrea |
| Orden | Lexicográfico por ruta POSIX relativa |
| Fecha | `1980-01-01 00:00:00` fija en toda entrada |
| Permisos | `0644` normalizados; sistema de origen Unix (`3`) |
| Compresión | DEFLATE nivel **9** fijo; `zlib` 1.2.11 fijado por el digest |
| *Bytecode* | `--no-compile`; además vetado por la política de contenido |
| Comentario del ZIP | Ausente y comprobado |
| Entradas de directorio | **Ninguna** (D-024-D) |
| `locale` y zona | `LC_ALL=C`, `LANG=C`, `TZ=UTC`, `PYTHONHASHSEED=0` |

**Por qué el ZIP se escribe dentro del contenedor (D-024-B).** Los bytes de DEFLATE
dependen de la versión de `zlib`. Escribiéndolo fuera, `A == B` solo valdría dentro de una
misma máquina y el *runner* de CI produciría un ZIP distinto del de Windows. Escribiéndolo
dentro, `zlib` y Python quedan fijados por el mismo digest que todo lo demás.

**La fecha `1980-01-01` no es arbitraria.** El formato ZIP guarda fecha **MS-DOS**, cuyo
mínimo representable es esa: el *epoch* de Unix no es expresable y `zipfile` lo rechaza.
Se comprobó contra la biblioteca empleada **antes** de adoptarlo (D-024-C).

### Alcance de la garantía (D-024-F)

La reproducibilidad demostrada vale con: **mismas fuentes**, **mismos locks**, **mismos
artefactos de dependencias**, **mismas herramientas fijadas** y el **mismo entorno de
construcción controlado**.

**No se promete** que PyPI conserve los archivos indefinidamente, ni reproducibilidad
universal en cualquier máquina o con cualquier herramienta. Si el digest de la imagen
dejara de estar disponible, o una distribución desapareciera de PyPI, la construcción no
sería reproducible — y eso es una propiedad del ecosistema, no un defecto de esta tarea.

---

## 8. Instalación *fail-closed* y el hallazgo sobre `--require-hashes`

El comando es:

```
pip install --disable-pip-version-check --no-cache-dir --no-input \
  --require-hashes --only-binary=:all: --no-compile \
  --target /build/arbol --requirement /src/requirements.lock
```

Las **41** distribuciones de ejecución se instalaron **como rueda**. **Ninguna** se
construyó desde *sdist*: `--only-binary=:all:` lo prohíbe, y si alguna hubiera carecido de
rueda compatible la construcción habría **fallado**, que es el resultado correcto y un
hallazgo real — nunca una excusa para actualizar dependencias.

### H-024-1 — un control mal construido, no un fallo de `pip`

Para demostrar **D3** se alteró **un** carácter del primer `--hash` de `mangum` y se
ejecutó la instalación. **`pip` terminó con código 0.** El primer diagnóstico posible
—«`--require-hashes` no protege»— era falso: `mangum` declara **dos** hashes en el lock, y
`--require-hashes` acepta si el archivo coincide con **cualquiera** de los declarados. Es
el comportamiento correcto: una distribución puede publicarse como rueda y como *sdist*, y
el lock enumera ambas huellas.

Corregido el control —alterando **todos** los hashes de esa distribución— el resultado fue
el esperado:

```
ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE.
    mangum==0.22.0 from https://files.pythonhosted.org/.../mangum-0.22.0-py3-none-any.whl
        Expected sha256 001936891aaed8ed66479b871c2bda87ba288fd01c7d5dd6ba6c8e9ba1c239d1
        Expected     or 00595e3cc7a8091b22d8b3997bab5b2ad6aae7a5e40865e19c2015f5c959a93b
             Got        a0595e3cc7a8091b22d8b3997bab5b2ad6aae7a5e40865e19c2015f5c959a93b
CODIGO DE SALIDA DE PIP: 1
```

**No se produjo artefacto.** El lock del repositorio **no se modificó** en ningún momento:
la copia alterada vivió en un directorio temporal fuera del repositorio.

---

## 9. El artefacto se ejecuta, no solo se mide

`unzip -l` demuestra que hay archivos. `import mangum` desde el repositorio demuestra que
el `.venv` del desarrollador funciona. Un ZIP al que le faltara `pydantic_core` pasaría
las dos. Por eso la aceptación ejecuta el *handler* **desde el ZIP extraído**, en un
proceso Linux con `-I -S -W error`:

| Comprobación | Resultado |
| --- | --- |
| `sys.path` | `['/extraido', '/var/lang/lib/python3.12', '/var/lang/lib/python3.12/lib-dynload']` |
| Árbol de fuentes | **No disponible** |
| `site-packages` del runtime | **No disponible** (`-S`) |
| `PYTHONPATH`, *user site* | **Ignorados** (`-I`) |
| `.env` | **Ausente** en el artefacto y en el directorio de trabajo, comprobado |
| Credenciales / AWS | **Ninguna**; configuración ficticia, sin red |
| `statusCode` | **200** |
| `isBase64Encoded` | **false** |
| `content-type` | `application/json` · `content-length` `67` |
| Cuerpo | `{"status":"ok","service":"personal-blog-backend","version":"0.1.0"}` |
| Cabeceras de seguridad | `content-security-policy`, `x-content-type-options`, `x-frame-options`, `referrer-policy`, `permissions-policy`, `x-robots-tag`, `x-request-id` |
| Módulos críticos | **14 de 14** resueltos **desde el artefacto**, verificado por `__file__` |

El evento es de **API Gateway HTTP API v2** (*payload format* 2.0), `GET /health`. Es una
sonda de vivacidad que por diseño no consulta dependencias, así que la validación es
**offline** y no necesita PostgreSQL ni MinIO.

### Capacidades nativas — ejercitadas, no inventariadas

No se acepta la mera presencia del `.so`:

| Capacidad | Qué se ejercitó | Resultado |
| --- | --- | --- |
| **Argon2** | `PasswordHasher.hash` + `verify` | **`argon2id`**, verificación correcta |
| **Pillow** | Codificar y decodificar PNG (77 B) y JPEG (632 B) en memoria; `features.check` | `(9, 7) RGB`; `jpg`, `zlib`, `webp` disponibles |
| **PostgreSQL** | `psycopg.pq.__impl__` y `version()`, **sin conectar** | **`binary`**, `libpq` **180000** |

De las **28** extensiones compiladas del artefacto, **25** se **importaron**. Las **3**
restantes se cargaron con el **enlazador dinámico** (`ctypes.CDLL`), porque su import falla
por un módulo **externo al artefacto**, no por el binario:

| Extensión | Motivo del fallo de import | Carga por el enlazador |
| --- | --- | --- |
| `PIL._imagingtk` | falta `_tkinter`, que el runtime de Lambda no trae | ✔ |
| `greenlet.tests._test_extension` | falta `psutil`, que no es dependencia del proyecto | ✔ |
| `greenlet.tests._test_extension_cpp` | falta `psutil` | ✔ |

La distinción se decide **en ejecución**, no con una lista escrita a mano: solo un
`ModuleNotFoundError` habilita el respaldo por enlazador, y cualquier otro error rompe la
validación. Las bibliotecas de `pillow.libs/` y `psycopg_binary.libs/` no son módulos de
Python: las carga su propia extensión por `RPATH`, y quedan ejercitadas a través de ella
—`libjpeg` y `libpng` por Pillow, `libpq` por psycopg—.

---

## 10. Controles negativos — el aislamiento es real, no declarado

Una validación aislada que tomara prestada una dependencia del entorno aprobaría un
artefacto incompleto. Cada control retira una dependencia **real** del artefacto dejando
una copia **alcanzable fuera**, y se ejecuta **dos veces**: en modo **permeable**, que
debe **funcionar** —si no, el vector no está demostrado y el control es un
espantapájaros—, y en modo **aislado**, que debe **fallar**.

| Retirado | Vector de fuga | Permeable | Aislado | Error aislado |
| --- | --- | --- | --- | --- |
| `mangum` | `PYTHONPATH=/externo` | **0** ✔ | **1** ✔ | `ModuleNotFoundError: No module named 'mangum'` |
| `boto3` | `site-packages` del propio runtime (trae `boto3 1.42.97`) | **0** ✔ | **1** ✔ | `ModuleNotFoundError: No module named 'boto3'` |
| `app` | árbol de fuentes alcanzable por `PYTHONPATH` | **0** ✔ | **1** ✔ | `ModuleNotFoundError: No module named 'app'` |

### H-024-2 — el control negativo encontró un defecto en el propio *harness*

En la primera ejecución, los tres modos aislados fallaron correctamente, pero **dos de los
tres permeables también fallaron**: el vector no quedaba demostrado. La causa no era
`PYTHONPATH` —se verificó que llega a `sys.path` dentro del contenedor— sino que
`/externo` **ya estaba en `sys.path` al arrancar el intérprete sin existir todavía**: el
buscador de imports registró ese hecho en caché y no volvió a mirar el directorio cuando
el *harness* lo creó y lo llenó.

Corregido con `importlib.invalidate_caches()` inmediatamente después de mutar el sistema
de archivos. Los tres permeables pasaron a terminar en **0**.

**El control negativo hizo exactamente su trabajo:** detectó que el *harness* no estaba
demostrando lo que decía demostrar. Sin él, las ejecuciones aisladas habrían seguido
fallando «correctamente» por el motivo equivocado.

---

## 11. Hallazgos sobre la política de contenido

Dos archivos **legítimos** del árbol real habrían sido rechazados por una política
escrita por intuición. Se detectaron inspeccionando el árbol instalado **antes** de fijar
las reglas:

| Archivo | Qué es | Decisión |
| --- | --- | --- |
| `botocore/cacert.pem` | Almacén de CA que `botocore` empaqueta para verificar TLS | `.pem` sigue **prohibido**, con una lista de permitidos **por ruta exacta** que hoy contiene solo este archivo. Cualquier otro `.pem` rompe la construcción |
| `greenlet/platform/setup_switch_x64_masm.cmd` | Script de construcción que `greenlet` publica dentro de su rueda | `.cmd` y `.bat` **no** se vetan por nombre: son texto inerte en Linux. El riesgo real —un binario de Windows— lo cubre el gate de **magia PE/COFF**, y la arquitectura, la lectura de `e_machine` del ELF |

Tampoco se encontró **ningún enlace simbólico** en el árbol real, lo que hace gratuito
prohibirlos y elimina una superficie entera: dentro de un ZIP un enlace es una entrada
ambigua que unos extractores siguen y otros materializan.

La normalización no tuvo que borrar nada (`eliminados_en_la_normalizacion: []`):
`--no-compile` y el filtro de copia de `app/` ya dejan el árbol limpio. Los gates de
*bytecode* y caché son, por tanto, **redundantes a propósito**, no load-bearing.

---

## 12. Resultado de las validaciones

*Ejecutadas el 2026-09-13 sobre el estado final de la rama.*

### `personal-blog-backend`

| Validación | Comando | Resultado |
| --- | --- | --- |
| Formato | `ruff format --check .` | **325 files already formatted** |
| Lint | `ruff check .` | **All checks passed!** |
| Tipos | `mypy .` | **Success: no issues found in 323 source files** |
| Suite completa | `pytest -W error --durations=10` | **1965 passed, 3 skipped** en 322,21 s |
| Árbol de dependencias | `python -m pip check` | **No broken requirements found** |
| **S-09** ejecución | `pip-audit --strict --requirement requirements.lock` | **No known vulnerabilities found** · código 0 |
| **S-09** desarrollo | `pip-audit --strict --requirement requirements-dev.lock` | **No known vulnerabilities found** · código 0 |
| Imagen | `docker build --tag personal-blog-backend:task024 .` | **success** |
| Trivy, gate accionable | `trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1` | **0 accionables** · código 0 |
| Build ZIP **A** | `empaquetar_lambda.py construir` | `6580410109207f33…` |
| Build ZIP **B** | `empaquetar_lambda.py construir` | `6580410109207f33…` |
| **A == B** | `empaquetar_lambda.py comparar` | bytes ✔ · SHA-256 ✔ · manifiesto ✔ |
| Gates del artefacto | `empaquetar_lambda.py verificar` | *layout*, rutas, contenido, binarios, orden, fechas, permisos, inventario y cuotas ✔ |
| `.sha256` | `sha256sum --check --strict` | `personal-blog-backend-lambda.zip: OK` |
| Ejecución aislada | `empaquetar_lambda.py ejecutar-aislado` | **200**, 14/14 módulos desde el artefacto, nativas ✔ |
| Controles negativos | `empaquetar_lambda.py control-negativo` | **3 de 3** se comportan como deben |

**La aritmética de la suite.** De **1918 passed, 1 skipped** (1919 casos, cierre de
`Task/023`) a **1965 passed, 3 skipped** (1968 casos): **49 casos nuevos**, de los que
**48 pasan** en Windows y **1 se omite**. El `passed` sube 47 y no 48 porque una prueba
preexistente —la de `TZ`— pasó de ejecutada a omitida por la variable del lanzamiento, no
por un cambio de código: **1918 + 48 − 1 = 1965**. Las tres omisiones se explican abajo.

### Las tres omisiones, explicadas

| Omisión | Motivo | En CI Linux |
| --- | --- | --- |
| `test_la_variable_tz_no_altera_el_timestamp` | `time.tzset` no existe en Windows. **Preexistente** | **Se ejecuta** |
| `test_un_enlace_simbolico_se_rechaza` | **Nueva.** Windows exige privilegio para crear enlaces simbólicos (`WinError 1314`) | **Se ejecuta** |
| `test_el_timestamp_no_coincide_con_la_hora_local_del_host` | **Artefacto de la ejecución, no del código.** La suite se lanzó cargando el `.env` de infra, que define `TZ=UTC`; con el host en UTC la comprobación sería vacía y la prueba se auto-omite | **Se ejecuta** (`TZ: America/Guatemala`) |

La tercera se verificó de inmediato: re-ejecutada **sin** `TZ=UTC`, el módulo dio
**9 passed, 1 skipped**, quedando solo la omisión estructural de Windows. **No es una
regresión.**

### **H-023-3** no reapareció — y eso **no** es un diagnóstico

`test_dos_publicaciones_simultaneas_solo_prosperan_una` **pasó** en la suite completa del
2026-09-13 (23:13–23:18 UTC, backend `Task/024` sobre `8795ac7…`). **H-023-3 sigue
ABIERTO y NO DIAGNOSTICADO.** No se reintentó ninguna ejecución hasta verde, no se declara
*flake*, y no se atribuye al ZIP ni a Mangum. Su causa sigue sin demostrarse.

### `personal-blog-infra`

| Validación | Resultado |
| --- | --- |
| `git diff --check` | Sin errores de espacios en blanco |
| Enlaces Markdown de los documentos tocados | Todos resuelven |
| Criterion12 | §14 |
| Compose y Terraform | **No tocados.** `Task/024` no los necesita |

### R-14 — el lock no se puede haber movido

`Task/024` **no modifica** `pyproject.toml`, `requirements.lock` ni
`requirements-dev.lock`: `git diff --name-only main --` sobre los tres devuelve vacío. La
regeneración con `uv` es un gate de `CI Backend` y se ejecutará en el cierre; `uv` no está
instalado en la máquina local y **no se instaló para esta tarea**.

---

## 13. Impacto en la CI

`CI Backend` pasa de **19** a **25** pasos. **Ningún paso preexistente se modificó,
reordenó ni relajó.** No se creó ningún workflow nuevo.

| Paso añadido | Qué demuestra |
| --- | --- |
| `Build the Lambda artifact (A)` | Construcción en el runtime fijado por digest |
| `Build the Lambda artifact (B)` | Segunda construcción **independiente** |
| `Artifact is byte-for-byte reproducible (A == B)` | Bytes, SHA-256 y manifiesto |
| `Artifact passes its own gates` | Revalidación leyendo **solo el ZIP** |
| `Handler responds from the isolated artifact` | Ejecución real y cargas nativas |
| `Isolation of the harness is real (negative controls)` | Que el paso anterior no miente |

**El ZIP es efímero a propósito** (**D-024-K**): se construye, se valida y muere con el
*runner*. No se publica como *GitHub Actions Artifact* porque no hay necesidad
demostrada, y la evidencia durable vive en el log y en este reporte. `Task/025` reconstruye
por el mismo mecanismo canónico; `Task/038` es la responsable de la automatización del
despliegue.

**Durante la fase previa a la aprobación no se hace push**, así que **la CI remota no se
ha ejecutado todavía con estos pasos**. Lo validado hasta aquí es el flujo equivalente en
local. **La CI remota se convierte en la autoridad del artefacto al ejecutar el cierre
aprobado.**

---

## 14. Criterion12 — barrido C/D

### Metodología

Cada hallazgo heredado se clasificó **antes** de tocarlo:

- **A — estado durable vigente realmente contradictorio.** Se corrige.
- **B — historia fechada o registro histórico legítimo.** **No se toca.**

Y se exigió **demostrar que la contradicción sigue viva en el `main` actual**, no
heredarla de un informe previo.

### Hallazgos evaluados

| # | Hallazgo | Clase | Acción |
| --- | --- | --- | --- |
| **D-024-1** | La fila de `Task/024` en `ROADMAP.md` y su entrada en `STAGE-08` declaraban solo `backend`, omitiendo el repositorio de documentación que [`WORKFLOW.md`](../project-management/WORKFLOW.md) §6 y §7 hacen obligatorio en **toda** tarea | **A** | **Corregido.** Ambas declaran ya «backend, infra (documentación)». **La propiedad funcional sigue siendo `backend`.** Las anotaciones que `Task/023` dejó abiertas se cierran en su sitio, sin borrarlas |
| **D-024-2** | `aws-local-parity.md` y `production-postgresql-vps.md` seguían describiendo `images/Infraestructura.png` **en presente** como «arquitectura objetivo **inicial**, anterior a `Task/005.3`/ADR-007» y «registro histórico», y negando que fuera canónica | **A** | **Corregido.** Ver el análisis de abajo |
| **D-024-3** | La celda «Tarea actual» de `STATUS.md` describía `Task/023` como **Aprobada** y cerraba con «**Avance sin cambios: 22/41 ≈ 54 %**», sin acotación temporal, mientras «Avance global» decía **23/41 — 56 %** | **A** | **Corregido.** La celda —ahora «Antecedente de la tarea actual»— dice «**Con su aprobación el avance pasó de 22/41 ≈ 54 % a 23/41 ≈ 56 %**», con nota de qué decía antes y por qué |
| **D-024-4** | La **tabla resumen de etapas** de `ROADMAP.md` seguía declarando la ETAPA 08 como «Preparación Cloud **sin Cuentas**», nombre que `Task/005.2` cambió el 2026-08-15, y sus contadores quedaron desfasados al registrar esta aprobación | **A** | **Corregido.** La fila dice «Preparación Cloud + AWS Local Parity», **2 de 4 — 50 %**, y el total **24/41 — 59 %**. Detectado al revalidar los contadores vivos tras registrar la aprobación, no heredado del preflight |
| — | `STATUS.md` líneas 68 y 113: «el avance pasa de 22/41 a 23/41», «de 21/41 a 22/41» | **B** | **No tocado.** Narran la transición de una aprobación concreta |
| — | `STATUS.md` §«Último mantenimiento aprobado» y siguientes: 21/41, 20/41, 19/41 | **B** | **No tocado.** Todas llevan «*en esa fecha*» o describen su propio momento |
| — | `ROADMAP.md` «Actualización anterior» y «Anterior», del 2026-09-12 | **B** | **No tocado.** Entradas fechadas de bitácora |
| — | Contadores «ETAPA 07 = 0» o «ETAPA 08 = 0» que el preflight sospechaba vivos | — | **No existen.** La búsqueda no encontró ninguno: `ROADMAP.md` línea 5 y `STAGE-08` ya decían **1 de 4 — 25 %** y ETAPA 07 **Completada** |

### Análisis de D-024-2 — por qué **sí** era contradicción

El enunciado advertía que declarar la PNG histórica **no es por sí solo** una
contradicción, y que solo se corrige si existe una afirmación **vigente** incompatible con
la arquitectura canónica actual. Existe, y es demostrable en el `main` actual:

1. El usuario **actualizó la imagen** en el commit `d08fe27` («Se actualiza imagen
   desactualizada de la arquitectura»), **posterior** a `Task/005.2` y `Task/005.3`.
2. `Task/006.2` (commit `764c691`, 2026-08-23) formalizó
   `target-production-architecture.md`, que declara la PNG **«Estado: Vigente»** y afirma
   textualmente que las notas que la llamaban histórica **«quedaron obsoletas; se corrigen
   en esta tarea»**.
3. `overview.md` §4 **sí** quedó corregido por esa tarea, y hoy dice que la PNG es la
   «vista visual vigente».
4. Pero `aws-local-parity.md` (dos lugares) y `production-postgresql-vps.md` (uno)
   **conservaban la redacción superada, en presente**. `Task/006.2` corrigió dos de los
   cuatro sitios.

Es decir: **dos documentos vigentes afirmaban estados mutuamente excluyentes del mismo
artefacto.** Clase **A**.

**Qué se corrigió y qué no.** Las tres notas dicen ahora que la PNG es la **vista visual
vigente**, que **no se modifica, no se regenera y no se reemplaza** desde el proyecto, y
que la autoridad **textual** es `target-production-architecture.md` —y, para la capa de
datos, `production-postgresql-vps.md` §3—. Cada una conserva, **como anotación fechada**,
qué decía antes y por qué dejó de ser cierto. **La imagen no se ha tocado, movido,
regenerado ni convertido**, y ninguna decisión de arquitectura ha cambiado: ADR-006 y
ADR-007 siguen **Aceptadas** y vigentes.

### Resultado

**C = 0 · D = 0** para los documentos tocados y para las contradicciones incluidas
legítimamente en el alcance. **Cuatro** contradicciones de clase **A** corregidas:
**D-024-1**, **D-024-2** y **D-024-3** antes de la aprobación, y **D-024-4** al revalidar
los contadores vivos después de registrarla.

No se persiste ningún estado vivo de Git o GitHub como vigente: este reporte describe la
rama **antes** de cualquier commit, push o pull request, y así lo dice. Los hechos
históricos fechados —mediciones, SHA-256, salidas de comandos— **sí** se conservan.

---

## 15. Archivos modificados

### `personal-blog-backend`

| Archivo | Acción | Qué |
| --- | --- | --- |
| `scripts/empaquetar_lambda.py` | **Creado** | Construcción y validación del artefacto |
| `scripts/arranque_aislado_lambda.py` | **Creado** | *Harness* de ejecución aislada |
| `tests/unit/test_empaquetado_lambda.py` | **Creado** | **49** pruebas del empaquetador |
| `.github/workflows/ci-backend.yml` | **Modificado** | 6 pasos añadidos al final; los 19 previos intactos |
| `README.md` | **Modificado** | §11 reestructurada en §11.1 Docker y §11.2 artefacto |

**Sin cambios:** `pyproject.toml`, `requirements.lock`, `requirements-dev.lock`,
`Dockerfile`, `.gitignore`, `.dockerignore`, `app/` y `alembic/`.

`app/` **no se toca** a propósito: el empaquetador vive en `scripts/` para no aparecer
dentro del artefacto ni alterar la guarda de **T-04** (**D-024-I**).

`.gitignore` **no necesitó cambios**: `lambda_package/` y `*.zip` estaban desde `Task/005`.

**No se versiona ningún artefacto generado**: ni el ZIP, ni las ruedas, ni los árboles
extraídos, ni el `.sha256`, ni el manifiesto. Lo durable es la **medición**, y vive en este
reporte.

**Se renumeró la sección 11 del README pero no las siguientes**, a propósito: el reporte de
`Task/005.5` referencia «`README.md` §12», y renumerar convertiría en falso un registro
histórico fechado.

### `personal-blog-infra`

| Archivo | Acción | Qué |
| --- | --- | --- |
| `docs/tasks/TASK-024-lambda-zip-artifact.md` | **Creado** | Ficha, con la matriz escrita antes de implementar |
| `docs/task-reports/TASK-024-report.md` | **Creado** | Este reporte |
| `docs/project-management/STATUS.md` | **Modificado** | Vista rápida, sección de la tarea en curso y **D-024-3** |
| `docs/project-management/ROADMAP.md` | **Modificado** | Cabecera, fila de `Task/024` y **D-024-1** |
| `docs/stages/STAGE-08-cloud-ready.md` | **Modificado** | Entrada de `Task/024` y **D-024-1** |
| `docs/architecture/aws-local-parity.md` | **Modificado** | **D-024-2**, dos lugares |
| `docs/architecture/production-postgresql-vps.md` | **Modificado** | **D-024-2**, un lugar |

**Sin cambios:** ADR, `DEFINITION_OF_DONE.md`, `WORKFLOW.md`,
`BACKEND_TESTING_STRATEGY.md`, `non-functional-requirements.md`, `open-decisions.md`,
Compose, Terraform, runbooks e `images/`.

**No se añaden riesgos al registro del proyecto.** Los **R-024-1** a **R-024-9** de la
ficha son riesgos **de ejecutar la tarea**, mitigados dentro de ella; no son residuales.
El recuento de riesgos abiertos de `STATUS.md` **no cambia**.

### `personal-blog-frontend`

**Sin cambios. Sin rama.** Solo lectura.

---

## 16. Problemas encontrados

| # | Problema | Resolución |
| --- | --- | --- |
| **H-024-1** | Un control de hash alterado no hacía fallar a `pip` | El control estaba mal construido: `mangum` declara **dos** hashes y `--require-hashes` acepta cualquiera. Corregido el control; `pip` aborta con código 1. §8 |
| **H-024-2** | Dos de los tres controles negativos **permeables** fallaban, dejando el vector sin demostrar | Caché negativa del buscador de imports sobre un `/externo` que no existía al arrancar. `importlib.invalidate_caches()`. §10 |
| **H-024-3** | `test_el_manifiesto_es_deterministico` falló en GREEN | Defecto **de la prueba**: nombraba los ZIP `A.zip`/`B.zip` cuando el flujo real usa un nombre canónico único. Corregida la prueba para modelar el flujo real. §5 |
| **H-024-4** | Una política de contenido por intuición habría rechazado `botocore/cacert.pem` y un `.cmd` de `greenlet` | Inspección del árbol real **antes** de fijar las reglas. §11 |
| **H-024-5** | `mypy --strict` rechazó `os.uname()` | No existe en Windows, donde corre `mypy`. Sustituido por `platform.system()` / `platform.machine()` |
| **H-024-6** | Una omisión nueva inesperada en la suite | `TZ=UTC` cargada del `.env` de infra. Verificado re-ejecutando sin ella. §12 |

---

## 17. Lo que esta tarea NO hizo

- **No creó ni tocó Terraform**, ni módulos, ni backend de estado: `Task/025` (**D-06**).
- **No desplegó** el artefacto en el laboratorio local: `Task/025`.
- **No escribió runbooks**: `Task/026`.
- **No usó AWS real**: sin cuenta, sin credenciales, sin AWS CLI contra AWS, sin API
  Gateway real. `public.ecr.aws` es un registro público de contenedores.
- **No creó** ECR, imagen de contenedor de Lambda ni *layers*. El prefijo `python/` es de
  *layers* y está **prohibido** por el gate de *layout*.
- **No cerró D-12.** Respetar las cuotas de empaquetado no es dimensionar la función:
  memoria, *timeout*, concurrencia, arranque en frío y costo son de `Task/032`.
- **No diagnosticó H-023-3.**
- **No podó ninguna dependencia** (**D-024-G**). `uvicorn`, `uvloop`, `watchfiles`,
  `websockets`, `httptools` y `alembic` siguen en el artefacto: están declaradas en el
  lock de ejecución y el paquete cabe con margen. Se **midió** qué pesa cada una.
- **No modificó dependencias ni locks**, ni movió `--exclude-newer`.
- **No relajó ningún gate.** Sin `.trivyignore`, sin exclusiones de `pip-audit`, sin
  hashes opcionales, sin *fallback* a *sdist*, sin advertencias silenciadas.
- **No introdujo ninguna familia de tooling nueva** (**D-024-J**): sin `make`, sin `just`,
  sin PowerShell nuevo, sin `Dockerfile` auxiliar y **sin ningún script de shell**. El
  gate de infra *«No shell scripts yet»* queda intacto.
- **No creó un workflow nuevo** ni publicó artefactos de GitHub Actions.
- **No rediseñó** Mangum, `lifespan`, FastAPI, el *handler* ni **T-04**.
- **No hizo commit, push, merge ni pull request.** No marcó nada como Aprobado.

---

## 18. Estado final

| Elemento | Estado |
| --- | --- |
| `Task/024-Artefacto-ZIP-Lambda` | **Aprobada** el 2026-09-13 mediante `approved: Task/024-Artefacto-ZIP-Lambda` |
| **ETAPA 08** | **En progreso, 2 de 4 — 50 %.** **No completada**: `Task/025` y `Task/026` siguen Pendientes |
| **Avance global** | **24/41 ≈ 59 %**, desde 23/41 ≈ 56 % |
| **T-04** | **Satisfecho y Vigente.** Sin cambios |
| **P-06** | **Conservado** |
| **P-07** | Evidencia del tramo de artefacto registrada —tamaño, composición, reproducibilidad y ejecución del artefacto—; **validación del arranque real pendiente de `Task/032`** |
| **D-12** | **ABIERTA.** `Task/032` |
| **H-023-3** | **ABIERTO y NO DIAGNOSTICADO.** No reapareció, lo que no es un diagnóstico |
| **R-018-3** | **ABIERTO**, ajeno a esta tarea |
| **D-024-A … D-024-K** | **Aceptadas y Vigentes** desde el 2026-09-13. Sin ADR nuevo |
| `Task/025-Terraform-Cloud` | **Pendiente, no iniciada** |
| Ramas Task | Creadas desde `main`. Cierre ejecutado tras la aprobación; detalle en §20. Frontend sin rama |

---

## 19. Cómo validarlo

Requiere **Docker**. No requiere cuenta de AWS, credenciales ni AWS CLI.

```powershell
cd personal-blog-backend

# Gates de calidad
ruff format --check .
ruff check .
mypy .

# Las 49 pruebas del empaquetador (48 pasan en Windows, 1 se omite)
pytest tests/unit/test_empaquetado_lambda.py -W error

# Artefacto: dos construcciones independientes y su comparación
python scripts/empaquetar_lambda.py construir --destino lambda_package/A
python scripts/empaquetar_lambda.py construir --destino lambda_package/B
python scripts/empaquetar_lambda.py comparar lambda_package/A lambda_package/B

# Gates del artefacto, leyendo solo el ZIP
python scripts/empaquetar_lambda.py verificar lambda_package/A

# El handler responde desde el ZIP, aislado
python scripts/empaquetar_lambda.py ejecutar-aislado lambda_package/A

# El aislamiento es real
python scripts/empaquetar_lambda.py control-negativo lambda_package/A
```

Se espera que `comparar` termine en *«Reproducibilidad demostrada: A == B byte a byte»* y
que el SHA-256 sea
`6580410109207f330a329ee235e0424a6bb3f7d96d14f550c4605eb3d8a02841` **mientras las fuentes
y los locks no cambien**.

La suite completa necesita además PostgreSQL y MinIO locales, según
[`README.md` §10.1 y §10.2](https://github.com/jeffersondavila/personal-blog-backend).
**No exportes `TZ=UTC`** o `test_el_timestamp_no_coincide_con_la_hora_local_del_host` se
auto-omitirá.

---

## 20. Cierre aprobado

**Aprobada** el **2026-09-13** por el usuario mediante la expresión exacta
`approved: Task/024-Artefacto-ZIP-Lambda`.

La aprobación autorizó el flujo de cierre de
[`WORKFLOW.md`](../project-management/WORKFLOW.md) §8: commits, integración
`Task → dev`, publicación de las ramas Task, pull requests `Task → main` y borrado de las
ramas Task **locales**. **No** autorizó fusionar los pull requests ni eliminar las ramas
remotas: eso es responsabilidad exclusiva del usuario.

**Qué cambió con la aprobación:**

| Elemento | Antes | Después |
| --- | --- | --- |
| `Task/024` | Lista para validación | **Aprobada** |
| Avance | 23/41 ≈ 56 % | **24/41 ≈ 59 %** |
| ETAPA 08 | 1 de 4 — 25 % | **2 de 4 — 50 %** |
| **D-024-A … D-024-K** | Propuesta | **Aceptadas y Vigentes** |

**Qué NO cambió:** **T-04** Satisfecho y Vigente · **P-06** conservado · **P-07** con la
evidencia del tramo de artefacto y el arranque real pendiente de `Task/032` · **D-12**
**ABIERTA** · **H-023-3** **ABIERTO y NO DIAGNOSTICADO** · **R-018-3** **ABIERTO**.

**El estado operativo del cierre —identificadores de ejecución de CI, números y URL de los
pull requests, SHA de los merges en `dev`, existencia de las ramas remotas— no se persiste
aquí.** Es estado vivo de Git y GitHub, no un hecho durable del proyecto: se reporta al
usuario y se consulta en su origen. Lo que sí queda escrito son los **hechos históricos
fechados**: las mediciones, los SHA-256 del artefacto y los resultados de las validaciones.

---

## 21. Próxima tarea

`Task/025-Terraform-Cloud` — **Pendiente, no iniciada.** Terraform portable con el
provider oficial de AWS, `plan`, `apply` y `destroy` ejecutados contra el laboratorio
local, matriz de paridad y guardas *fail-closed*. Consumirá el artefacto de esta tarea.

**No se inicia** hasta que el usuario escriba
`approved: Task/024-Artefacto-ZIP-Lambda` y se complete el cierre y la normalización.
