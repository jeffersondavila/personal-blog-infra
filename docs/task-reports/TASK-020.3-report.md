# TASK-020.3 — Registro de MinIO en CI Backend

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/020.3-Corregir-Registro-MinIO-CI-Backend` |
| **Estado** | Lista para validación |
| **Fecha** | 2026-09-12 |
| **Ficha** | [TASK-020.3](../tasks/TASK-020.3-fix-minio-registry-backend-ci.md) |
| **Avance** | **21/41 ≈ 51 %**; ETAPA 06 **3/3 tareas aprobadas** |
| **Naturaleza** | Mantenimiento; no cuenta entre las 41; Task020 y Task021 continúan Aprobadas |

## 1. Alcance y autorización

El usuario autorizó cambiar solo `IMAGEN_DE_MINIO` en el workflow backend:
añadir el prefijo `quay.io/`, sin tocar release, digest, estructura, comandos,
puertos, healthchecks, tests, dependencias, locks, Dockerfile ni políticas.
Infra registra el mantenimiento y el cierre técnico de STAGE-06. Frontend es
solo lectura. No se reabren Task020/021 ni se inicia Task022.

Después de local GREEN y C=0/D=0 está autorizado commit/push de la misma rama
Task en backend e infra. No incluye merge/push dev, PR ni modificaciones directas
de main. No equivale a aprobación del mantenimiento.

**Ampliación autorizada el 2026-09-12, después del diagnóstico de B-020.3-C.**
El gate Trivy destapó un defecto independiente del cambio de registro, descrito
en la sección 6 y diagnosticado por separado. El usuario autorizó entonces la
**Opción 1**: aplicar las actualizaciones de seguridad de Debian en la etapa
`runtime` del Dockerfile backend, y solo ahí. La ampliación mantiene todas las
prohibiciones anteriores y añade las suyas: no cambiar Python, ni distribución
base, ni el digest del `FROM`, ni regenerar locks, ni relajar S-09, ni añadir
`.trivyignore` o baseline de vulnerabilidades del backend. Detalle y evidencia
en la sección 7.

## 2. Preflight Git y hallazgos documentales

*Comprobado el 2026-09-12:* `fetch --prune`, `switch main`, `pull --ff-only`,
árbol limpio, staging 0 y untracked 0 antes de crear cada rama. `main` coincidió
con `origin/main`; inmediatamente después de crearla, `HEAD == main`:

| Repositorio | SHA base medido |
| --- | --- |
| backend | `8055878e415ace2bfc4e7685e0549c5ab8a642ef` |
| infra | `aef66384372c13998eb03f38f5629b8692f8f9e0` |
| frontend, solo lectura, sin rama nueva | `7dce98aff239d61ae3ae15213d9a3f5ebf0fb8ce` |

| Hallazgo | Evidencia en main | Corrección autorizada | Estado |
| --- | --- | --- | --- |
| **D-020.3-A** | ROADMAP, «Actualmente: 20 / 41 ≈ 49 %», contradictorio con resumen/total 21/41 | Solo esa afirmación vigente pasa a 21 / 41 ≈ 51 % | **RESUELTA** |
| **D-020.3-B** | STATUS, cabecera 2026-09-10 pese a aprobación de Task021 el 2026-09-12 | Cabecera 2026-09-12, sin hora inventada | **RESUELTA** |
| **D-020.3-C** | Cuatro presuntos enlaces rotos en `TASK-020-report.md`, señalados por un comprobador provisional antes del commit de infra | Investigada con autorización: **no era un defecto documental** sino un comprobador que no distinguía código literal; ningún enlace se modificó. Detalle en 7.6 | **RESUELTA** |

D-020.3-A y D-020.3-B preexistían en main y no fueron causados por Task020.3.
El usuario autorizó resolverlos dentro del preflight, sin otra maintenance, sin
reabrir Task020/021, sin cambiar avance real ni crear tareas nuevas. D-020.3-C
se registró más tarde, durante el cierre, y se cerró sin modificar documentos:
la investigación demostró que no había defecto que corregir.

**Barrido mecánico acotado:** se revisaron 20/41, 49 %, 2/3, 67 % y estados de
aprobación en los documentos tocados. Se preservaron los valores históricos.
La cabecera del reporte Task021 explicita que su avance de 20/41 corresponde
al 2026-09-10, antes de aprobarla; la ficha separa inicio de actualización.
La próxima Task021 de la ficha Task020 queda fechada al cierre de Task020, y
su veredicto pre-aprobación se identifica como tal. Los estados vigentes
conservan Task020/021 Aprobadas, 21/41 y STAGE-06 3/3. No se hicieron reemplazos
globales de cifras ni se reescribió el historial.

## 3. Defecto demostrado y cronología

| Evidencia backend | Fecha | Contexto | Resultado |
| --- | --- | --- | --- |
| [34491446991, attempt 1](https://github.com/jeffersondavila/personal-blog-backend/actions/runs/34491446991/attempts/1) | 2026-09-10 | push, dev, SHA `5fedcb34f8f1542fcfb0957547e58f472529f6f2` | completed/success, 1855 tests, 0 omitidos; hecho histórico válido |
| [34491446991, attempt 2](https://github.com/jeffersondavila/personal-blog-backend/actions/runs/34491446991/attempts/2) | 2026-09-12 | Mismo run, SHA, rama y evento | completed/failure; paso 11 `Start the ephemeral MinIO`, exit 125; pasos 1–10 success, gates 12–21 skipped |

El attempt 2 devolvió `pull access denied for minio/minio` al intentar obtener
el manifiesto de Docker Hub. La consulta OCI anónima independiente registrada
en el handoff devolvió HTTP 401 / UNAUTHORIZED. Es indisponibilidad de **ese
manifiesto** desde Docker Hub; no un fallo de tests, Quay, Trivy o vulnerabilidades.
No se generaliza el diagnóstico a todo Docker Hub.

No se ejecutó otro rerun. Se consultaron en lectura los metadatos de ambos
intentos. El verde del attempt 1 no certifica la reproducibilidad del attempt 2.

## 4. Cambio de origen e identidad OCI

Referencia autorizada:

```text
quay.io/minio/minio:RELEASE.2025-09-07T16-13-09Z@sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e
```

*Medido el 2026-09-12 antes de modificar el workflow:* GET anónimo al índice
de Quay, sin `Authorization` ni intercambio de token: **HTTP 200**.
SHA256 de los bytes y cabecera `Docker-Content-Digest` coinciden exactamente
con `sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e`.

La equivalencia completa ya está demostrada en
[Task021 §AM](TASK-021-report.md): índice, manifiesto amd64, configuración,
9 layers, RootFS diff IDs, arquitectura/OS, Created, Entrypoint, Cmd y labels.
Mismo contenido OCI, con 100 accepted, 100 actionable, 100 exact matches,
0 baseline-only, 0 quay-only y 0 identidades cambiadas. No se repitió esa
investigación ni se regeneró el baseline.

## 5. Validación local y Criterion12

**Local GREEN antes del bootstrap, medido el 2026-09-12:**

| Control | Resultado |
| --- | --- |
| YAML y estructura | Válido; 19 pasos declarados; triggers push/pull_request intactos |
| actionlint 1.7.12 | Exit 0; herramienta descargada de su release oficial y checksum SHA256 verificado |
| Diff backend | Comparación byte a byte con main: únicamente `quay.io/` añadido en una línea de `IMAGEN_DE_MINIO`; ningún otro archivo ni untracked |
| Release / digest | Exactamente los autorizados; índice OCI anónimo HTTP 200 y digest calculado coincidente |
| Frontend | Mismo SHA y rama main; árbol limpio, sin cambios |
| Infra | Solo los once documentos previstos; archivos LF; definición S-09 y baseline preservados |
| Enlaces Markdown | *Barrido inicial:* 1389 destinos relativos comprobados, 0 rotos; no es un barrido de disponibilidad de todos los sitios externos. Una revisión posterior, antes del commit de infra, señaló cuatro presuntos enlaces rotos; se investigaron y quedaron **descartados** —eran código literal, no enlaces renderizados—. Resultado final en la sección 7.6 |
| Patrones sensibles | 0 en los archivos versionables de infra y workflow backend |
| Gitleaks | 0 hallazgos en la misma superficie, sin leer archivos ignorados del usuario |
| `git diff --check` | Exit 0 en backend e infra, tanto working tree como diff respecto de main |

| Clase | Tratamiento |
| --- | --- |
| A | Reglas permanentes: Task nace de main; aprobación exclusiva del usuario; alcance y bootstrap acotados; S-09 intacto |
| B | Hechos fechados: creación de ramas, approvals anteriores, runs con attempt, control negativo ya ejecutado y OCI anónimo |
| C | Revisión previa a implementar: **0**; no se guarda estado vivo de PR, ramas remotas o normalización como condición vigente |
| D | Preflight autorizado: **0** tras D-020.3-A/B y barrido de la familia; estados y contadores vigentes coherentes, historia preservada |

**Criterion12 previo al bootstrap: C = 0 · D = 0.** Se revisaron los once
documentos, incluyendo las autodescripciones de este reporte y la ficha. Los
pendientes históricos de Task021 están temporalizados; ningún run se cita como
verde sin el intento correspondiente cuando tiene reejecuciones de resultado
distinto. La revisión posterior a registrar la detención también conserva **C = 0 · D = 0**
documentales. B-020.3-C es un bloqueo técnico, no una contradicción documental.

## 6. CI Backend nueva

*Observado el 2026-09-12 UTC:* se publicó únicamente el commit backend
`e8693eb0685c6123257e1a7a59ae35729d474b1c` en la rama Task, bajo el bootstrap
autorizado después de local GREEN y C=0/D=0. El diff sigue siendo una sola
línea: prefijo Quay en `IMAGEN_DE_MINIO`.

[CI Backend 34713222925](https://github.com/jeffersondavila/personal-blog-backend/actions/runs/34713222925): **push**, rama
`Task/020.3-Corregir-Registro-MinIO-CI-Backend`, SHA `e8693eb`, **attempt 1**,
**completed/failure**. Inicio `2026-09-12T19:07:21Z` → fin
`2026-09-12T19:12:12Z`: **291 s**; job **287 s**.

**B-020.3-C, tal como se detectó en este run:** gate Trivy de la imagen backend
con 12 hallazgos accionables (9 HIGH, 3 CRITICAL), exit 1. Quedó **ABIERTO** al
cierre de esta ejecución; su resolución posterior se registra en la sección 7.

**MinIO desde Quay sí quedó demostrado:** el paso 11 descargó el release y
digest exactos; el log muestra `Status: Downloaded newer image for
quay.io/minio/minio@sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e`
y `MinIO responde tras 2 intento(s).` Duración del paso: **5 s**. No hay
`docker login` en el workflow ni en el log, ni credenciales de registro o
GitHub secrets agregados. Las credenciales efímeras de PostgreSQL/MinIO ya
existían y no son credenciales del registro.

### Todos los pasos y gates

**25 pasos registrados por GitHub:** 23 success, 1 failure y 1 skipped.
Los 19 pasos declarados se ejecutaron; el skipped es `Post Setup Python`,
de limpieza, después del fallo. No se acepta este resultado como verde parcial.

| Nº GitHub | Paso | Resultado | Duración |
| --- | --- | --- | --- |
| 1 | Set up job | success | 1 s |
| 2 | Initialize containers | success | 13 s |
| 3 | Checkout | success | 1 s |
| 4 | Setup Python | success | 1 s |
| 5 | Runtime versions | success | 0 s |
| 6 | Install uv (pinned version and verified digest) | success | 1 s |
| 7 | Lock is up to date (R-14) | success | 1 s |
| 8 | Install dependencies from the lock | success | 16 s |
| 9 | Installed tree is coherent | success | 0 s |
| 10 | Provision the ephemeral databases | success | 0 s |
| 11 | Start the ephemeral MinIO | success | 5 s |
| 12 | Check formatting | success | 0 s |
| 13 | Lint | success | 0 s |
| 14 | Type-check | success | 14 s |
| 15 | Migrations against real PostgreSQL | success | 3 s |
| 16 | Tests | success | 172 s |
| 17 | Audit Python dependencies (S-09) | success | 22 s |
| 18 | Build the image | success | 20 s |
| 19 | Install Trivy (pinned version and verified digest) | success | 2 s |
| 20 | Image vulnerability inventory | success | 11 s |
| 21 | Actionable image vulnerabilities (blocking) | failure | 1 s |
| 40 | Post Setup Python | skipped | 0 s |
| 41 | Post Checkout | success | 0 s |
| 42 | Stop containers | success | 0 s |
| 43 | Complete job | success | 0 s |

| Medición del log | Resultado |
| --- | --- |
| Locks, instalación con hashes y pip check | success, sin desfase ni incompatibilidades |
| Formato | 312 archivos ya formateados |
| Lint | All checks passed |
| Tipos | Sin incidencias en 310 fuentes |
| Migraciones | **13 passed**, 1.45 s, PostgreSQL real, -W error |
| Suite completa | **1855 passed**, **0 skipped**, **0 warnings**, 170.27 s, -W error |
| S-09 dependencias | Ambos locks: No known vulnerabilities found, dos resultados |
| Docker build | success, Dockerfile/lock existentes sin cambios |
| Inventario Trivy | **177** en Debian 13.6: LOW 60, MEDIUM 61, HIGH 53, CRITICAL 3; paquetes Python sin hallazgos |
| Trivy accionable | **12** en paquetes Debian: HIGH 9, CRITICAL 3; exit **1** |

### Hallazgo independiente B-020.3-C

El fallo está en `Actionable image vulnerabilities (blocking)`, sobre
`personal-blog-backend:ci (debian 13.6)`. Trivy 0.74.0 reporta estas versiones
corregidas; la tabla reproduce el log, sin una investigación nueva de remedios:

| Paquete | CVE | Severidad | Instalada | Corregida según Trivy |
| --- | --- | --- | --- | --- |
| gzip | CVE-2026-41992 | HIGH | 1.13-1 | 1.13-1+deb13u1 |
| libpcre2-8-0 | CVE-2026-86145 | HIGH | 10.46-1~deb13u1 | 10.46-1~deb13u2 |
| libpcre2-8-0 | CVE-2026-89161 | HIGH | 10.46-1~deb13u1 | 10.46-1~deb13u2 |
| libsqlite3-0 | CVE-2026-11822 | HIGH | 3.46.1-7+deb13u1 | 3.46.1-7+deb13u2 |
| libsqlite3-0 | CVE-2026-11824 | HIGH | 3.46.1-7+deb13u1 | 3.46.1-7+deb13u2 |
| perl-base | CVE-2026-13221 | CRITICAL | 5.40.1-6 | 5.40.1-6+deb13u1 |
| perl-base | CVE-2026-42496 | CRITICAL | 5.40.1-6 | 5.40.1-6+deb13u1 |
| perl-base | CVE-2026-8376 | CRITICAL | 5.40.1-6 | 5.40.1-6+deb13u1 |
| perl-base | CVE-2026-42497 | HIGH | 5.40.1-6 | 5.40.1-6+deb13u1 |
| perl-base | CVE-2026-48962 | HIGH | 5.40.1-6 | 5.40.1-6+deb13u1 |
| perl-base | CVE-2026-57432 | HIGH | 5.40.1-6 | 5.40.1-6+deb13u1 |
| perl-base | CVE-2026-57433 | HIGH | 5.40.1-6 | 5.40.1-6+deb13u1 |

El gate ejecutó la política vigente `--severity HIGH,CRITICAL --ignore-unfixed
--exit-code 1` y falló correctamente. El hallazgo pertenece a la imagen backend,
no al MinIO efímero descargado desde Quay. Cambiar Dockerfile, base o política
excede la única línea funcional autorizada. **No se corrigió ni se exceptuó**,
no se cambió el baseline y no se ejecutó rerun.

**Desbloqueo necesario:** revisión y autorización explícita del usuario para
tratar este defecto independiente. No se eligió actualización ni mitigación.

*Actualización del mismo día:* el usuario autorizó la corrección después de la
auditoría. Su diagnóstico, implementación y evidencia figuran en la
[sección 7](#7-corrección-de-b-0203-c--ci-backend-green). Todo lo descrito
arriba conserva su valor de hecho fechado sobre el run `34713222925`, que
acredita el bloqueo y no la corrección.

### Warnings y secretos

**Tests: 0 warnings**, con `-W error`. El log conserva avisos de herramientas:
hint de Git sobre el nombre inicial de rama; pip ejecutado como root durante
el build; UID 1001 mayor que SYS_UID_MAX 999 al crear el usuario; advertencia
de Trivy sobre severidades de otros vendors en inventario y gate; mensajes de
initdb sobre locales y autenticación local trust mostrados durante la limpieza.
Ninguno sustituye el motivo de failure: el gate de vulnerabilidades, exit 1.

Los **537830 bytes** del log completo se escanearon con Gitleaks
8.30.1 y patrones sensibles: **0 hallazgos** en ambos. SHA256 del log:
`003e6385ced46d5c64ebd66860067e2d63ee3fb9d8ab0e73c2c3ab240e55d311`. Metadatos, logs y salidas locales se conservan en
`tmp/task020.3/`, ignorado por Git.

La reproducción de la descarga MinIO quedó reparada. **En ese run la CI Backend
completa no quedó GREEN** y por sí solo no demuestra el cierre técnico de
STAGE-06. El attempt 1 histórico de `34491446991` conserva su success; el
attempt 2 conserva su fallo de descarga; este run es un tercer hecho,
independiente y fechado. El cuarto —`34719123905`, ya GREEN— se registra en la
sección 7 y no reescribe ninguno de los anteriores.


## 7. Corrección de B-020.3-C — CI Backend GREEN

### 7.1 Autorización y causa medida

El usuario autorizó explícitamente la **Opción 1** del diagnóstico: aplicar las
actualizaciones de seguridad disponibles de Debian dentro de la etapa `runtime`
del Dockerfile backend. Descartó la Opción 2 —fijar las cuatro versiones
corregidas una a una—.

**Causa, con la precisión exigida:** la información de vulnerabilidades
disponible para el **mismo artefacto** evolucionó entre las ejecuciones. Diez
CVE ya figuraban en el inventario anterior pero **no eran accionables** bajo
`--ignore-unfixed` porque no tenían `FixedVersion` utilizable; posteriormente
adquirieron corrección publicada. Además aparecieron **dos CVE adicionales** de
`libpcre2-8-0`. Con el mismo artefacto y la misma versión de Trivy, el gate pasó
de **0 a 12 accionables**.

**Este repositorio no introdujo las 12 vulnerabilidades.** Controles medidos:

| Control | Resultado |
| --- | --- |
| `git diff main..HEAD -- Dockerfile requirements.lock requirements-dev.lock pyproject.toml` | Vacío en el momento del fallo: mismos Dockerfile, locks y `pyproject.toml` |
| Imagen base | Idéntica, mismo digest `sha256:78387bc…` |
| Trivy | 0.74.0 fijado por SHA256 en ambas ejecuciones |
| Estado previo de los 10 CVE | `affected` / `fix_deferred`, sin `FixedVersion`, en el inventario del 2026-09-10 |
| CVE nuevas | `CVE-2026-86145` y `CVE-2026-89161`, ausentes del inventario del 2026-09-10 |
| Cambio Docker Hub → Quay | No participa: afecta al contenedor de servicio MinIO, no a la imagen que Trivy escanea |

Tampoco había reconstrucción disponible aguas arriba: consultado el 2026-09-12,
`python:3.12.14-slim` seguía resolviendo al **mismo digest ya fijado**
(creado 2026-09-01), y el tag móvil `python:3.12-slim` apuntaba al mismo
artefacto —3.12.14 es el último parche publicado de esa serie—. Esperar el
rebuild no tenía fecha conocida.

### 7.2 Cambio aplicado

Un único archivo: `personal-blog-backend/Dockerfile`. Una capa nueva en la etapa
`runtime`, inmediatamente después del `FROM` y antes del resto de su
configuración. **La etapa `builder` no se tocó.**

```dockerfile
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
```

Se actualizó también el comentario que afirmaba «El runtime no instala
paquetes», hoy insuficientemente exacto: el runtime **no incorpora paquetes
adicionales**, pero sí actualiza los existentes con las correcciones
disponibles, y después retira el `pip` global como antes.

**Base inmutable.** El `FROM` conserva exactamente
`python:3.12.14-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea`.
La decisión **no sustituye el pin**. Semántica registrada en el propio
Dockerfile: el digest sigue fijando el **punto de partida** de la imagen, y la
capa posterior de APT aplica las actualizaciones disponibles en el repositorio
Debian **en el momento del build**. Por tanto el sistema de archivos final deja
de estar determinado únicamente por el digest del `FROM`. **Esta consecuencia
queda aceptada explícitamente para esta imagen local/CI** —cuyo destino de
producción es un artefacto ZIP de Lambda, no esta imagen ([ADR-003](../adr/ADR-003-serverless-low-cost-cloud.md))—
y **no se generaliza automáticamente a otras imágenes del proyecto**.

Lo que **no** cambió: versión de Python, distribución base, digest del `FROM`,
`requirements.lock`, `requirements-dev.lock`, `pyproject.toml`, el workflow, el
baseline y la política S-09.

### 7.3 Efecto de APT, medido

Construida la imagen real desde el árbol de la rama con `--no-cache`, no
reutilizando ninguna imagen de diagnóstico:

| Medición | Antes | Después |
| --- | --- | --- |
| Debian detectada por Trivy | 13.6 | **13.7** |
| Paquetes instalados | 87 | **87** |
| Paquetes añadidos | — | **0** |
| Paquetes eliminados | — | **0** |
| Paquetes actualizados | — | **12** |
| Tamaño de la imagen | 405 MB | **451 MB** |

`apt-get` lo confirma en local y en CI con la misma línea: **`12 upgraded,
0 newly installed, 0 to remove and 0 not upgraded.`**

Paquetes actualizados, medidos de nuevo con `dpkg-query` sobre la imagen real y
**no tomados como lista autorizada**: `base-files` 13.8+deb13u7, `bash`
5.2.37-2+b10, `gzip` 1.13-1+deb13u1, `libaudit-common` y `libaudit1`
1:4.0.2-2+deb13u1, `libc-bin` y `libc6` 2.41-12+deb13u4, `libcap2`
1:2.75-10+deb13u1+b3, `libpcre2-8-0` 10.46-1~deb13u2, `libsqlite3-0`
3.46.1-7+deb13u2, `perl-base` 5.40.1-6+deb13u1, `tzdata` 2026c-0+deb13u1.
Los cuatro paquetes de los 12 hallazgos están entre ellos; los ocho restantes
acompañan a la *point release* 13.6 → 13.7.

### 7.4 Validación local

| Control | Resultado |
| --- | --- |
| `ruff format --check .` | **312 archivos ya formateados**, exit 0 |
| `ruff check .` | **All checks passed**, exit 0 |
| `mypy .` | **Sin incidencias en 310 fuentes**, exit 0 |
| Migraciones sobre PostgreSQL real, `-W error` | **13 passed** |
| Suite completa, `-W error --durations=15` | **1854 passed, 1 skipped**, 308.33 s |
| Gate Trivy 0.74.0, semántica exacta de CI | **0 accionables**, exit **0** |
| Inventario Trivy | **149**: LOW 57, MEDIUM 48, HIGH 44, **CRITICAL 0** |
| Locks y `pyproject.toml` frente a `main` | `--exit-code` 0, sin diferencias |
| Archivos modificados en el árbol | Únicamente `Dockerfile` |

El único *skipped* local es `tests/test_logging_utc.py::…`, omitido porque
`time.tzset` no existe en Windows. En el runner Linux de CI ese test sí se
ejecuta, y de ahí la diferencia entre **1854 + 1** en local y **1855 + 0** en CI.

Regresión funcional de la imagen resultante: construye; arranca como
`uid=1001(blog) gid=1001(blog)`; `USER=blog`; `HEALTHCHECK` y `CMD` conservan su
definición; `/usr/local/bin/python -m pip` responde `No module named pip`, sin
`pip` global; `app.main` carga con Python **3.12.14** y registra
`Aplicacion inicializada` con **22 rutas**, y la cadena de conexión aparece
redactada en el log. Ningún paquete nuevo.

### 7.5 CI Backend GREEN

*Observado el 2026-09-12 UTC:* se publicó en la misma rama Task el commit
backend `32c39925aa5078e5cbaecdaa118abdff18715093`, adicional a `e8693eb` —sin
squash, sin amend, sin rebase y sin force push—, con un único archivo
modificado.

[CI Backend 34719123905](https://github.com/jeffersondavila/personal-blog-backend/actions/runs/34719123905):
**push**, rama `Task/020.3-Corregir-Registro-MinIO-CI-Backend`, SHA `32c3992`,
**attempt 1**, **completed/success**. Inicio `2026-09-12T21:09:01Z` → fin
`2026-09-12T21:13:57Z`: **296 s**; job **292 s**. **25 pasos registrados por
GitHub: 25 success, 0 failure y 0 skipped.** No es un verde parcial.

| Nº GitHub | Paso | Resultado | Duración |
| --- | --- | --- | --- |
| 1 | Set up job | success | 0 s |
| 2 | Initialize containers | success | 12 s |
| 3 | Checkout | success | 1 s |
| 4 | Setup Python | success | 0 s |
| 5 | Runtime versions | success | 1 s |
| 6 | Install uv (pinned version and verified digest) | success | 1 s |
| 7 | Lock is up to date (R-14) | success | 1 s |
| 8 | Install dependencies from the lock | success | 16 s |
| 9 | Installed tree is coherent | success | 0 s |
| 10 | Provision the ephemeral databases | success | 1 s |
| 11 | Start the ephemeral MinIO | success | 4 s |
| 12 | Check formatting | success | 0 s |
| 13 | Lint | success | 0 s |
| 14 | Type-check | success | 13 s |
| 15 | Migrations against real PostgreSQL | success | 4 s |
| 16 | Tests | success | 179 s |
| 17 | Audit Python dependencies (S-09) | success | 22 s |
| 18 | Build the image | success | 21 s |
| 19 | Install Trivy (pinned version and verified digest) | success | 2 s |
| 20 | Image vulnerability inventory | success | 10 s |
| 21 | Actionable image vulnerabilities (blocking) | **success** | 0 s |
| 40 | Post Setup Python | success | 0 s |
| 41 | Post Checkout | success | 1 s |
| 42 | Stop containers | success | 0 s |
| 43 | Complete job | success | 0 s |

| Medición del log | Resultado |
| --- | --- |
| MinIO desde Quay | `Status: Downloaded newer image for quay.io/minio/minio@sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e`; `MinIO responde tras 2 intento(s).` |
| Formato | 312 archivos ya formateados |
| Lint | All checks passed |
| Tipos | Sin incidencias en 310 fuentes |
| Migraciones | **13 passed**, 1.47 s, PostgreSQL real, `-W error` |
| Suite completa | **1855 passed**, **0 skipped**, **0 warnings**, 177.12 s, `-W error` |
| S-09 dependencias | Ambos locks: `No known vulnerabilities found`, dos resultados |
| Docker build | success; `12 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.` |
| Inventario Trivy | **149** en **Debian 13.7**: LOW 57, MEDIUM 48, HIGH 44, **CRITICAL 0**; paquetes Python sin hallazgos |
| Trivy accionable | **0**; todos los *targets* en `0`; exit **0** |

**B-020.3-C — RESUELTO.** El gate conserva intacta su política
`--severity HIGH,CRITICAL --ignore-unfixed --exit-code 1` y ahora pasa porque la
imagen dejó de tener vulnerabilidades accionables, **no porque se haya ocultado
el gate**. No se añadió `.trivyignore`, ni `|| true`, ni `continue-on-error`, ni
se bajó ninguna severidad, ni se retiró `--ignore-unfixed` o `--exit-code`, ni
se creó baseline por conteo para el backend.

La ejecución `34713222925` acredita el bloqueo; `34719123905` acredita la
corrección. Ninguna sustituye a la otra.

### 7.6 D-020.3-C — investigada y descartada como defecto

Antes del commit de infra se repitió el barrido de enlaces con un comprobador
provisional basado en expresiones regulares. Señaló **cuatro** presuntos enlaces
rotos en `docs/task-reports/TASK-020-report.md`, preexistentes en `main`:
`../personal-blog-infra/docs/project-management/STATUS.md`, `app/main.py`,
`alembic/versions` y `pyproject.toml`. La sesión **se detuvo** y los reportó como
posible contradicción documental independiente, **D-020.3-C**, sin corregirlos.

La investigación posterior, autorizada por el usuario, demostró que **no son un
defecto**:

| Comprobación | Resultado |
| --- | --- |
| Ubicación en el documento | Dentro de un bloque *fenced* ` ```markdown `; **no son enlaces renderizados** |
| Naturaleza del bloque | Cita literal de `README.md` §3 del repositorio **backend**, reproducida por `Task/020` al documentar esa corrección |
| Fidelidad de la cita | **Idéntica byte a byte** al archivo real de `personal-blog-backend` |
| Resolución en su contexto real | Los cuatro destinos **existen y resuelven** desde la raíz de `personal-blog-backend` |

Corregirlos habría falsificado una cita literal y la habría hecho divergir del
archivo que documenta. **No se modificó ninguno de los cuatro.**

**Los barridos históricos eran correctos.** El de `Task/021` del 2026-09-11
—1359 destinos, 0 rotos, con exclusión declarada de ejemplos de código literal—
y el barrido inicial de este mantenimiento —1389 destinos, 0 rotos— se conservan
tal cual: excluían correctamente el código literal. El comprobador provisional
era el defectuoso, por no distinguir contenido *fenced* e *inline* del texto
renderizado. No se reescribe ningún resultado histórico ni se afirma que aquellas
ejecuciones no ocurrieran.

**Barrido final**, con un analizador que separa bloques *fenced* (` ``` ` y
`~~~`), código *inline* y bloques indentados de cuatro espacios, sin lista de
excepciones de destinos:

| Medición | Resultado |
| --- | --- |
| Archivos Markdown inspeccionados | **129** (127 versionados + los dos nuevos de este mantenimiento) |
| Enlaces renderizados relativos | **1394** |
| Destinos dentro de código literal, excluidos y clasificados | **14** |
| **Enlaces renderizados rotos** | **0** |

Las 14 exclusiones se clasifican una a una y ninguna es deuda aceptada: cinco
*fenced* en `TASK_TEMPLATE.md`, una *fenced* en `TASK-013.1-report.md`, las
cuatro *fenced* de `TASK-020-report.md` descritas arriba, tres `access_url`
*inline* en `TASK-015-report.md`, `TASK-021-report.md` y `TASK-015-admin-panel.md`,
y un `javascript:alert(1` *inline* en `TASK-014-public-site.md`. **No se versionó
ninguna allowlist**: la exclusión la decide el análisis de Markdown, no una lista
de destinos tolerados.

**D-020.3-C — RESUELTA:** no existía un defecto documental; existía un
comprobador insuficiente. Ningún documento requirió corrección de enlaces.

### 7.7 Criterion12 final, previo al commit de infra

| Clase | Resultado |
| --- | --- |
| A | Reglas permanentes intactas: la Task nació de `main`, la aprobación sigue siendo exclusiva del usuario, S-09 conserva su definición y el alcance no se amplió más allá de lo autorizado |
| B | Hechos fechados y separados: `34491446991` attempt 1 success y attempt 2 failure; `34713222925` **failure**, que acredita el bloqueo; `34719123905` **success**, que acredita la corrección. Ninguna ejecución fallida se presenta como verde |
| C | **0** — no queda estado vivo de PR, ramas remotas ni normalización descrito como condición vigente |
| D | **0** — D-020.3-A, D-020.3-B y D-020.3-C resueltas; estados y contadores vigentes coherentes; historia preservada sin reescrituras |

**C = 0 · D = 0.** Controles ejecutados antes del commit: `git diff --check`
exit 0; finales de línea LF en los once documentos; **0** enlaces renderizados
rotos sobre 1394 destinos en 129 archivos; **0** patrones sensibles y **0**
credenciales en los archivos tocados. Task020 y Task021 siguen **Aprobadas**,
el avance sigue en **21/41 ≈ 51 %** y Task022 sigue **Pendiente, no iniciada**.

## 8. Evidencia ya disponible de STAGE-06

Hechos fechados del 2026-09-12, consultados en lectura durante Task020.3:

| Evidencia infra | Resultado |
| --- | --- |
| [34709782197](https://github.com/jeffersondavila/personal-blog-infra/actions/runs/34709782197) | pull_request de Task021, SHA `7e1d4f3`, completed/success, 54 s, 19/19 pasos |
| [34711465394](https://github.com/jeffersondavila/personal-blog-infra/actions/runs/34711465394) | push sobre dev normalizado, SHA `854c9bc`, completed/success, 50 s, 19/19 pasos |
| [34710854803](https://github.com/jeffersondavila/personal-blog-infra/actions/runs/34710854803) | control negativo remoto autorizado, push, SHA `30e265c`, completed/failure, 12 s |

El control negativo cambió deliberadamente `profiles: [admin]` por
`profiles: [admin` y falló en `Compose is valid`: `yaml: line 329: did not find
expected ',' or ']'`, exit 1. El handoff conserva Gitleaks 0 findings y la
comprobación de que el commit roto no es ancestro de main/dev/origin/main/origin/dev
ni estaba contenido por ninguna ref tras eliminar la rama efímera. **No se
repitió el control ni se recreó la rama.**

Triggers frontend/backend, verdes históricos sobre dev, auditorías de logs e
historial disponible, tiempos y ausencia de checks vacuos se conservan en
[STAGE-06](../stages/STAGE-06-continuous-integration.md) y los reportes Task019–021.
La descarga desde Quay quedó recuperada; el run `34713222925` terminó en failure
por B-020.3-C, y el run `34719123905`, ya con la corrección, quedó
**completed/success** con sus 25 pasos en verde (sección 7). Con CI Backend
completa restaurada junto a CI Frontend, CI Infra y el control negativo remoto
ya demostrado, **el cierre técnico de STAGE-06 queda demostrado y pendiente de
la aprobación de este mantenimiento**. La evidencia anterior no se invalida ni
se repite.

## 9. Seguridad, riesgos y deuda

No se usan Docker Hub credentials, GitHub secrets ni login de registro.
MinIO conserva **100** hallazgos aceptados temporalmente bajo **R-018-3,
ABIERTO**; Portainer conserva **16** bajo **R-021-1, ABIERTO**. No se corrigieron
esas vulnerabilidades. Release, digest, baseline y políticas permanecen intactos.
S-09 conserva su definición [canónica](../architecture/non-functional-requirements.md)
y verificaciones futuras en ETAPAS 07/12. Cerrar STAGE-06 no las reemplaza.

## 10. Archivos, validación del usuario y veredicto

Backend: `.github/workflows/ci-backend.yml` y `Dockerfile`, en dos commits
separados.
Infra: STATUS, ROADMAP, STAGE-06, NFR, índice de reportes, fichas/reportes
Task020 y Task021, ficha y reporte Task020.3: **once documentos**.
Frontend: solo lectura. No aplica TDD nuevo por cambio declarativo sin lógica;
la validación de integración corresponde al workflow completo existente.

El usuario puede revisar `git diff main` en ambos repositorios, contrastar
la referencia exacta y consultar el run 34713222925 con su auditoría en §6 y el
run 34719123905 con su evidencia en §7.
**TASK020.3 IMPLEMENTADA — LISTA PARA VALIDACIÓN.**

**B-020.3-C — RESUELTO:** gate Trivy de la imagen backend en **0 accionables**,
exit **0**, con la política S-09 intacta.

**Descarga de MinIO reparada y CI Backend completa GREEN. ETAPA 06 — CIERRE
TÉCNICO DEMOSTRADO, PENDIENTE DE APROBACIÓN DEL MANTENIMIENTO.** Avance
intacto: **21/41 ≈ 51 %**. Task022 permanece **Pendiente, no iniciada**.

*Estado observado al detenerse el 2026-09-12, antes de autorizar la corrección:*
backend conservaba únicamente el commit `e8693eb` publicado en su rama Task; la
documentación de infra quedaba sin commit ni push. El bootstrap de entonces no
autorizaba otro cambio funcional, así que la sesión se detuvo y pidió
autorización para tratar B-020.3-C.

*Estado observado al cerrar el 2026-09-12, tras la autorización explícita de la
Opción 1:* backend conserva `e8693eb` y el commit adicional
`32c39925aa5078e5cbaecdaa118abdff18715093`, ambos publicados en la misma rama
Task; infra publica su commit de documentación en la rama Task homónima. No hubo
merge ni push a dev, ni pull request, ni cambios directos en main, ni cambios en
frontend, ni force push, ni rerun del run `34713222925`.
Task022 — **Pendiente, no iniciada**.
