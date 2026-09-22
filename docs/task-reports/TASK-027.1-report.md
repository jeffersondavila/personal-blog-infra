# TASK-027.1 — Reporte

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/027.1-Corregir-Regresion-S09-MinIO` |
| **Tipo** | Mantenimiento correctivo de seguridad (S-09) |
| **Cuenta en el roadmap** | **No.** Fuera de las 41 tareas; no altera el avance |
| **Estado** | **Aprobada** — addendum Floci aprobado el **2026-09-21**; aprobación del alcance MinIO del 2026-09-20 conservada como historia |
| **Repositorio** | `personal-blog-infra` (**únicamente**) |
| **Rama** | `Task/027.1-Corregir-Regresion-S09-MinIO`, nacida de `main` |
| **SHA base histórico (2026-09-17)** | `67c1904` (`= main = origin/main` al crear la rama) |
| **Commits del addendum Floci** | **0 hasta la aprobación** del 2026-09-21: hasta entonces los cambios permanecieron locales, sin staging, commit ni push, partiendo del publicado `df3ba33`. La aprobación autorizó crearlos y publicarlos; el resultado consta en §16 |
| **Imagen en GHCR** | **Publicada** el 2026-09-19 y verificada contra el registro. Paquete **PRIVADO**; visibilidad **no modificada** |
| **Fechas de las fases** | MinIO: implementación 2026-09-18, publicación 2026-09-19, primera aprobación 2026-09-20. Floci: 2026-09-20 (Guatemala). Reconciliación documental y **segunda aprobación**: 2026-09-21. |
| **Ficha** | [TASK-027.1-fix-s09-minio-regression.md](../tasks/TASK-027.1-fix-s09-minio-regression.md) |

---

> **Cómo leer este reporte:** §1–§13 registran la historia MinIO/BuildKit del
> 2026-09-18 al 2026-09-20, con la aprobación y los commits publicados del alcance original.
> Los recuentos, tablas Git y resultados de esas secciones pertenecen a las fechas
> indicadas. §14 documenta el addendum Floci y §15 su reconciliación y la estrategia de
> cierre por fases, escrita mientras seguía pendiente de aprobación; **§16 registra la
> aprobación del 2026-09-21 y fija el estado vigente**.

## 1. Qué se corrigió

El baseline de S-09 aceptaba **100** hallazgos accionables de la imagen de MinIO bajo
**R-018-3**. Uno de ellos, `CVE-2026-79921` en `github.com/rabbitmq/amqp091-go v1.10.0`
(HIGH, corregido en `1.13.0`), **sí tenía remedio**: no en una imagen más reciente —que no
existe— sino recompilando el binario del mismo release con la dependencia actualizada.

El resultado es un **derivado reproducible de upstream**: el mismo release
`RELEASE.2025-09-07T16-13-09Z`, el mismo runtime oficial y un único archivo distinto,
`/usr/bin/minio`.

| Antes | Después |
| --- | --- |
| 100 identidades aceptadas | **99** identidades aceptadas |
| `amqp091-go v1.10.0`, 1 hallazgo accionable | `amqp091-go v1.13.0`, **0** hallazgos |
| Imagen de tercero sin modificar | Derivado reproducible con manifiesto, SBOM y procedencia |
| Identidad ligada solo al digest | Identidad ligada a digest **y** manifiesto de construcción verificado |

Distribución de las 99 que quedan: **52** en `usr/bin/minio`, **45** en `usr/bin/mc`, **2**
en `os-pkgs:redhat`; **95 HIGH** y **4 CRITICAL**. Ninguna nueva.

## 2. Qué NO se hizo

- **No se hizo público el paquete.** La imagen **sí se publicó** en GHCR el 2026-09-19,
  bajo autorización acotada (§9 y §10), pero el paquete permanece **PRIVADO** y su
  visibilidad **no se modificó**.
- **No se cerró `R-018-3`.** Sigue **ABIERTO** con 99 identidades.
- **No se relajó la política S-09.** `postgres` y `traefik` siguen en tolerancia cero, con
  `accepted_findings` vacío.
- **No se creó una política nueva** ni una capacidad genérica de baseline.
- **No se tocó el stack `personal-blog-local`** ni sus volúmenes.
- **Antes de la primera aprobación (2026-09-18/19)** no se hizo commit, push de Git,
  merge ni PR. El cierre aprobado del 2026-09-20 sí publicó commits y creó #48 (§11).
- **No se inició `Task/028`** ni se modificó `Task/027`.

---

## 3. Gates locales de `CI Infra` sobre el estado final

Ejecutados **después** de que el árbol quedara en su estado definitivo. Ninguno se presenta
como completo estando parcial.

| # | Gate de `CI Infra` | Comando | Resultado |
| --- | --- | --- | --- |
| 1 | Terraform sources exist / lock versionado | `git ls-files terraform/**/*.tf` · `git ls-files --error-unmatch terraform/.terraform.lock.hcl` | **23** archivos `.tf`; lock **versionado** |
| 2 | Install Terraform (versión fijada, digest verificado) | `python scripts/laboratorio/laboratorio.py --modo local herramientas` | **Terraform 1.16.2** en caché verificada |
| 3 | Terraform version agrees with `versions.tf` | `terraform version -json` · `grep "= 1.16.2" terraform/versions.tf` | **coinciden** |
| 4 | Pinned artifact identity is coherent (S-09) | `vulnerability_gate.py --comprobar-coherencia .` | **CORRECTO** |
| 5 | Terraform is formatted | `terraform -chdir=terraform fmt -check -recursive` | **exit 0** |
| 6 | Terraform init (sin backend, lock readonly) | `terraform -chdir=terraform init -backend=false -input=false -lockfile=readonly` | **exit 0**; lock **sin cambios** |
| 7 | Terraform validate | `terraform -chdir=terraform validate` | **Success! The configuration is valid.** |
| 8 | Lab fail-closed guards | `python -B -m unittest discover -s tests/laboratorio` | **162 tests, OK** |
| 9 | Lab Compose is valid | `docker compose -f laboratorio/... config --quiet` | **válido** |
| 10 | Lab emulator loopback + digest | réplica del script del workflow | `127.0.0.1:${LAB_PUERTO:-4566}:4566`; digest `sha256:4e451c39…`; red `internal` |
| 11 | No shell scripts yet | `git ls-files '*.sh' '*.bash'` | **0 archivos** |
| 12 | Compose is valid | `docker compose --env-file .env.example --profile admin config --quiet` | **7 servicios**: backend, frontend, migrations, minio, portainer, postgres, traefik |
| 13 | Compose declares every variable | réplica del script del workflow | **26 usadas / 26 declaradas** |
| 14 | PowerShell scripts parse | `Parser::ParseFile` sobre `*.ps1,*.psm1,*.psd1` | **31 archivos, 0 fallos** |
| 15 | Python scripts compile | `compile()` sobre `scripts/**/*.py` | **13 archivos, 0 fallos** |
| 16 | Exact baseline comparator regressions | `python -B -m unittest discover -s tests/security` | **45 tests, OK** |
| 17 | No secrets in the full history | `gitleaks git . --log-opts=--all --redact=100` | **no leaks found** |
| 18 | Build the project images + OCI del derivado | `docker build` ×2 · `docker buildx build --output type=oci` · `artifact.py verify` | **verificado** (§4) |
| 19 | Scan every infrastructure image | Trivy 0.74.0 sobre postgres, traefik, minio, portainer, floci | **5 informes** |
| 20 | MinIO SBOM and deterministic provenance | `artifact.py canonicalize-sbom` · `provenance` | **generados** (§6) |
| 21 | Scan the pinned Terraform binary | Trivy `rootfs` sobre `linux_amd64` verificado | **253 paquetes**, 9 accionables |
| 22 | Scan the pinned AWS provider | Trivy `rootfs` sobre `terraform-provider-aws v6.64.0` | **377 paquetes, 0 accionables** |
| 23 | Full vulnerability inventory (report only) | `trivy convert --format table` ×7 | **7 inventarios** generados |
| 24 | Image vulnerability gate (S-09) | `vulnerability_gate.py --reports …` | **RESULTADO: CORRECTO** (§5) |

Gates añadidos a la comprobación local, fuera del workflow:

| Gate | Comando | Resultado |
| --- | --- | --- |
| Espacios en blanco | `git diff --check` y `git diff --cached --check` | **exit 0** |
| Secretos en el entregable sin *commit* | `gitleaks dir` sobre los **223** archivos del entregable (`git ls-files` + no rastreados), documentación de este cierre incluida | **no leaks found** |
| Enlaces relativos | validador propio, excluyendo *fences* y código en línea | **1524** comprobados, **0 rotos** |
| YAML estructural | `yaml.safe_load` sobre el workflow y los dos Compose | **3 archivos, 0 fallos**; job `infraestructura`, **28 pasos**, todos con `name` y `run`/`uses` |

### Precisiones honestas sobre tres de esos gates

- **PowerShell — 31 archivos.** El repositorio versiona **6** scripts; los otros 25 son
  copias locales bajo `tmp/` y `local-backups/`, que el CI no ve. El recorrido local es un
  superconjunto del de CI, y **0 fallos** en ambos.
- **Terraform — el binario escaneado no es el que corre en esta máquina.** El baseline
  acepta **exclusivamente** el scope `terraform` del artefacto `linux_amd64`, y declara
  expresamente que el de Windows produce las mismas 9 CVE con scope `terraform.exe`, que
  **no** está aceptado. Además, Trivy sobre Windows **no inventaría** un ELF sin bit de
  ejecución: el primer intento devolvió **0 paquetes**, que es ausencia de análisis, no
  ausencia de riesgo. Por eso el escaneo se hizo con el artefacto `linux_amd64` —
  descargado con la URL y el `sha256` que fija `scripts/laboratorio/herramientas.py`, valor
  verificado `0d17011f…3985a` — **dentro de un contenedor Linux**, que es el entorno del
  CI. Resultado: scope `terraform`, **253 paquetes**, **9 accionables**, exactamente las 9
  del baseline.
- **Provider AWS — se escaneó el binario `windows_amd64`**, que es el que instaló `init` en
  esta máquina. El gate del provider no compara contra baseline: exige inventario no vacío
  y cero accionables. **377 paquetes, 0 accionables**, coherente con lo que `Task/025`
  documentó para `linux_amd64`.

### `actionlint`

**No forma parte del flujo vigente de este repositorio.** `.github/workflows/ci-infra.yml`
es el único workflow de `personal-blog-infra` y no contiene ningún paso de `actionlint` ni
de `yamllint`; las menciones existentes son de tareas del repositorio *backend*
(`Task/019`, `Task/020.3`). No se introdujo una herramienta nueva para satisfacer una
exigencia que el flujo no tiene: se validó el YAML de forma estructural, como consta arriba.

---

## 4. Reproducibilidad de la construcción

### Qué está demostrado

El OCI se volvió a producir en esta sesión con el árbol en su estado final y dio **la misma
identidad**, hasta el último campo que el verificador comprueba:

```
manifest_digest         sha256:84c67632f7e85d4cd86ea5f7f6fbb6b5b8263ecd20f08153c4cd1a42e3059129
config_digest           sha256:25c832aa396d4de7eb2d202529ee8055280633f0ef270687e565bd376d1882a2
binary_sha256           9437671add14972349f023a780c1d873f4d8993d3a6cd7448b1b8a962e89983f
binary_size             111145144
layers                  10
only_minio_replaced     true
build_manifest_sha256   4e47cebc0541084add1e98b74b849dd8c2ed2b167e6b1fff73a3ac127d64074e
```

El verificador no se limita a comparar el digest final. Exige, y comprobó, que:

1. el OCI contenga **exactamente un** manifest, plataforma `linux/amd64`;
2. los **9 primeros** *layers* y *diff IDs* sean **los de la base oficial fijada**;
3. haya **exactamente 10** *layers*: ni uno más;
4. el *entrypoint*, `cmd`, variables y etiquetas del runtime tengan el mismo `sha256`
   canónico que la base (`b6e997f1…db244`);
5. el último *layer* contenga **solo** `usr`, `usr/bin`, `usr/bin/minio`;
6. ese archivo tenga modo `0755`, `uid 0`, `gid 0`;
7. su `sha256` y su tamaño sean los del manifiesto de construcción.

El parche que separa este binario del upstream son **26 líneas** que tocan **dos** archivos,
`go.mod` y `go.sum`, y el propio Dockerfile lo comprueba (`git diff --name-only` debe dar
exactamente `go.mod go.sum`) antes de compilar.

### Qué NO está demostrado — y por qué no se dice

**La construcción no es hermética ni offline.** Descarga por red el árbol de fuentes de
MinIO y los módulos Go. Lo que está demostrado es otra cosa, más modesta y verificable:

| Elemento | Cómo queda fijado | Comprobado en |
| --- | --- | --- |
| Imagen constructora | `golang:1.24.6-bookworm@sha256:4f858936…` (manifest de plataforma) | `FROM` del Dockerfile |
| Frontend de BuildKit | `docker/dockerfile:1.19@sha256:b6afd424…` | manifiesto de construcción |
| Tag del release | objeto `01ce918d…` | `test` en el `RUN` |
| Commit del release | `07c3a429bfed433e49018cb0f78a52145d4bedeb` | `test` en el `RUN` |
| Árbol de fuentes | `git archive \| sha256sum` = `3fd74f9e…92091` | `test` en el `RUN` |
| Parche | `sha256` = `16b199bb…a902c` | `test` en el `RUN` |
| Módulos Go | `go mod download` + **`go mod verify`** | `RUN` |
| Dependencia resultante | `go version -m` exige `v1.13.0` presente y `v1.10.0` ausente | `RUN` |
| Base del runtime | `quay.io/minio/minio@sha256:a1a8bd4a…` | `FROM` final |
| Marca temporal | `SOURCE_DATE_EPOCH=1757261589` + `rewrite-timestamp` | argumento de `buildx` |

La descripción correcta es: **construcción reproducible con todas las identidades fijadas y
verificadas**, no *hermética*. Si mañana desaparece el repositorio de MinIO, la
construcción falla; no se afirma lo contrario.

### Alcance de la reproducción de esta sesión

La comparación **A/B entre dos constructores independientes** (`task0271-build-a` y
`task0271-build-b`) se hizo en la fase de implementación previa. En esta sesión se produjo
una **tercera** construcción, con el árbol final, y devolvió la misma identidad en los siete
puntos verificados. Los constructores ya se eliminaron (§8), de modo que una cuarta
reproducción exigiría recompilar desde cero.

---

## 5. Gate S-09 sobre el estado final

`RESULTADO: CORRECTO` · **194** hallazgos accionables comparados · **6** imágenes declaradas.

| Clave | Política | Observados | Baseline | Nuevos | Coincidencias | Ya no presentes |
| --- | --- | --- | --- | --- | --- | --- |
| `personal-blog-postgres` | zero-tolerance | **0** | 0 | **0** | 0 | 0 |
| `personal-blog-traefik` | zero-tolerance | **0** | 0 | **0** | 0 | 0 |
| **`minio` (derivado)** | accepted-baseline | **99** | **99** | **0** | **99** | **0** |
| `portainer` | accepted-baseline | 16 | 16 | **0** | 16 | 0 |
| `floci` | accepted-baseline | 70 | 70 | **0** | 70 | 0 |
| `terraform` | pinned-artifact | 9 | 9 | **0** | 9 | 0 |

Para MinIO el gate imprimió, antes de comparar hallazgos:

```
Digest   : sha256:84c67632f7e85d4cd86ea5f7f6fbb6b5b8263ecd20f08153c4cd1a42e3059129
Identidad: derivado MinIO reproducible, atestado exacto verificado
```

La regresión que originó la tarea está cerrada, medida sobre el informe real:

```
paquete amqp091-go inventariado : [('github.com/rabbitmq/amqp091-go', 'v1.13.0')]
vulnerabilidades de amqp091-go  : 0   (en cualquier severidad)
CVE-2026-79921 presente         : False
```

### La excepción es nominal, no una puerta abierta

El atestado **no** es una cuarta política. Vive en tres lugares que se exigen mutuamente:

1. `validar_baseline` **rechaza** `identity_attestation` en cualquier clave que no sea
   `minio`, y exige esquema, ruta del manifiesto y `sha256` con forma válida.
2. `evaluar_imagen` exige que el informe lleve el atestado **exacto**: esquema,
   `build_manifest_sha256`, `source_commit`, `binary_sha256` y `only_minio_replaced`.
3. `--comprobar-coherencia` recalcula el `sha256` del manifiesto desde el disco y comprueba
   que referencia, digest, Dockerfile y parche coinciden con él.

`test_attestation_is_not_a_generic_baseline_option` copia la entrada de MinIO, le cambia la
clave y comprueba que el baseline es **rechazado**. La tolerancia cero de las imágenes
propias no se toca: `postgres` y `traefik` siguen con `accepted_findings` vacío, verificado
por dos pruebas independientes.

---

### 5b. S-09 repetido contra la referencia REMOTA (2026-09-19)

Tras publicar, el gate se volvió a ejecutar con el informe obtenido de GHCR —no del OCI
local— para comprobar que lo publicado es lo validado.

`RESULTADO: CORRECTO` · **194** accionables comparados · **6** imágenes declaradas.

| Clave | Política | Observados | Baseline | Nuevos | Coincidencias | Ya no presentes |
| --- | --- | --- | --- | --- | --- | --- |
| `personal-blog-postgres` | zero-tolerance | **0** | 0 | **0** | 0 | 0 |
| `personal-blog-traefik` | zero-tolerance | **0** | 0 | **0** | 0 | 0 |
| **`minio` (remoto, GHCR)** | accepted-baseline | **99** | **99** | **0** | **99** | **0** |
| `portainer` | accepted-baseline | 16 | 16 | **0** | 16 | 0 |
| `floci` | accepted-baseline | 70 | 70 | **0** | 70 | 0 |
| `terraform` | pinned-artifact | 9 | 9 | **0** | 9 | 0 |

Para MinIO, leído del informe remoto:

```
Digest   : sha256:84c67632f7e85d4cd86ea5f7f6fbb6b5b8263ecd20f08153c4cd1a42e3059129
Identidad: derivado MinIO reproducible, atestado exacto verificado

paquete amqp091-go inventariado : [('github.com/rabbitmq/amqp091-go', 'v1.13.0')]
vulnerabilidades de amqp091-go  : 0
CVE-2026-79921 presente         : False
accionables totales             : 99   (95 HIGH + 4 CRITICAL)
```

La corrección que originó la tarea queda así verificada **sobre la imagen realmente
publicada**, no solo sobre el artefacto local.

### 5c. La referencia del Compose resuelve

`.env.example` y `docker compose config` resuelven **exactamente la misma** referencia
publicada:

```
ghcr.io/jeffersondavila/personal-blog-minio:RELEASE.2025-09-07T16-13-09Z-amqp091-go1.13.0@sha256:84c67632…059129
```

`docker manifest inspect` la resuelve contra el registro, y un **pull aislado** la descargó
devolviendo `Digest: sha256:84c67632…059129` y el `RepoDigests` correcto. Esa imagen de
prueba **se eliminó**; no quedan imágenes `personal-blog-minio` locales.

**El stack principal no se recreó ni se reinició, y no se ejecutó `docker compose up`.**
`personal-blog-local-minio` sigue sirviendo con la **imagen original**
`quay.io/minio/minio@sha256:14cea493…`, *healthy*.

---

## 6. SBOM y procedencia

| Artefacto | `sha256` de la salida canónica |
| --- | --- |
| SBOM CycloneDX canónico | `47cc5134f31aef34d8e63b6e81f0b8da66f95a8069695aa3e5f2c2d6cc82c4c7` |
| Procedencia in-toto / SLSA v1 | `77f7a8a40a0b50078942ebc97c19c251569bf6b3eba59aae1979549143bad836` |

La canonización existe porque la salida cruda de Trivy **nunca** es idéntica entre
ejecuciones: lleva `serialNumber`, marca de tiempo y `bom-ref` aleatorios. Se eliminan el
número de serie y el *timestamp*, el componente raíz se nombra por la referencia y el digest
del manifiesto, cada `bom-ref` se sustituye por un identificador derivado del `sha256` de la
identidad del componente, y todas las listas se ordenan. Solo entonces dos SBOM equivalentes
son comparables byte a byte.

La procedencia declara como dependencias resueltas el repositorio de MinIO con su
`gitCommit`, el manifiesto de la imagen constructora y el de la base del runtime, y adjunta
el `sha256` del SBOM como *byproduct*.

---

## 7. Evidencia de la fase de implementación previa

Esta sesión **no repitió** las pruebas funcionales costosas contra el contenedor candidato.
Se registran aquí como lo que son —evidencia producida en la fase de implementación de esta
misma tarea, **no reejecutada hoy**— y no como resultados de esta sesión:

- **36/36** pruebas de contrato de `ObjectStorage`.
- CRUD, *listing*, URL prefirmadas y *multipart*.
- Prueba **positiva** de IAM en runtime y **3 controles negativos**.
- Respaldo y restauración verificando contenido, cabeceras, metadatos y etiquetas.
- Comparación **A/B** de dos construcciones independientes, byte a byte.

El contenedor y los volúmenes sobre los que se obtuvo esa evidencia se eliminaron en la
limpieza (§8), según lo pedido. Reproducirla exigiría reconstruir el derivado y volver a
levantar un candidato.

---

## 8. Limpieza de los recursos temporales

Se eliminaron **exclusivamente** los recursos creados por esta tarea, todos con el prefijo
`task0271`. Cada uno se inspeccionó antes de borrarlo: el contenedor candidato se había
creado el 2026-09-19T04:25Z con dos volúmenes propios (`/data` y `/backup`), sin relación
con el stack.

| Recurso | Tipo | Acción | Resultado |
| --- | --- | --- | --- |
| `task0271-minio-candidate` | contenedor | `docker rm -f` | eliminado |
| `task0271-minio-data` | volumen | `docker volume rm` | eliminado |
| `task0271-minio-backup` | volumen | `docker volume rm` | eliminado |
| `task0271-build-a` | builder buildx | `docker buildx rm` | eliminado |
| `task0271-build-b` | builder buildx | `docker buildx rm` | eliminado |
| `personal-blog-minio:task0271-candidate` | imagen | `docker rmi` | eliminada |
| `personal-blog-postgres:task0271` | imagen | `docker rmi` | eliminada |
| `personal-blog-traefik:task0271` | imagen | `docker rmi` | eliminada |

Los dos últimos no figuraban en la lista original, pero llevaban el mismo prefijo y se
habían creado durante esta tarea. Al eliminar los *builders* desaparecieron también sus
contenedores `buildx_buildkit_task0271-build-a0` / `-b0` y los volúmenes de estado
asociados.

Comprobación posterior, con **0** en las cuatro familias:

```
contenedores con task0271 : 0
volumenes con task0271    : 0
imagenes con task0271     : 0
builders con task0271     : 0
```

### El stack principal quedó intacto

```
personal-blog-local-traefik     personal-blog-traefik:local      Up 3 hours (healthy)
personal-blog-local-frontend    personal-blog-frontend:local     Up 3 hours (healthy)
personal-blog-local-portainer   portainer/portainer-ce:2.39.7    Up 3 hours
personal-blog-local-backend     personal-blog-backend:local      Up 3 hours (healthy)
personal-blog-local-minio       quay.io/minio/minio:RELEASE.2025-09-07T16-13-09Z   Up 3 hours (healthy)
personal-blog-local-postgres    personal-blog-postgres:local     Up 3 hours (healthy)
```

`personal-blog-local-minio` sigue corriendo la **imagen original**, resuelta al digest
`sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e`. Sus cinco
volúmenes (`personal-blog-local_minio_data`, `_minio_backup`, `_postgres_data`,
`_postgres_backup`, `_portainer_data`) están intactos. **El stack no se reinició, no se
recreó y no se apuntó al derivado.**

---

## 9. Identidad de publicación — resuelta y verificada contra el registro

**Publicado el 2026-09-19**, bajo autorización humana explícita y acotada, que **no**
equivalía a aprobar la tarea.

`sha256:84c67632f7e85d4cd86ea5f7f6fbb6b5b8263ecd20f08153c4cd1a42e3059129` es, desde esa
fecha, **las dos cosas a la vez**: el digest del manifiesto OCI producido localmente **y** el
**RepoDigest real** de `ghcr.io/jeffersondavila/personal-blog-minio`. La correspondencia no
se supuso: se comprobó.

### Cómo se publicó

Se publicó **exactamente el OCI ya validado, sin reconstruir**. El `Dockerfile`, el parche,
el `build-manifest.json` y el baseline no se tocaron. El daemon usa el **image store de
containerd**, que preserva el manifiesto OCI original en lugar de reconvertirlo, de modo que
`docker load` del mismo tar devolvió `ID = sha256:84c67632…059129` y el `push` terminó con
ese mismo digest y `size: 2289`.

### Correspondencia local ↔ remota

| Fuente | Digest |
| --- | --- |
| Esperado (`docker/minio/build-manifest.json`) | `sha256:84c67632…059129` |
| `docker buildx imagetools inspect` (consulta al registro) | `sha256:84c67632…059129` |
| `docker manifest inspect` (descriptor remoto) | `sha256:84c67632…059129` |
| **`sha256` recalculado sobre el manifiesto crudo descargado** | `sha256:84c67632…059129` |

La última fila es la comprobación fuerte: se descargó el manifiesto **en crudo** desde GHCR
—**2289 bytes**— y su `sha256` reproduce el digest esperado. No es una afirmación del
cliente sobre sí mismo, sino una verificación criptográfica del contenido remoto.

El registro **conservó el formato**: `mediaType: application/vnd.oci.image.manifest.v1+json`,
`config sha256:25c832aa…` y **10 layers** —los 9 heredados de la base oficial más
`e93c72cb…`, el layer de reemplazo declarado en el manifiesto de construcción—.

### El RepoDigest observado por Trivy es nativo del registro

El escaneo posterior se hizo con `--image-src remote` **tras eliminar la copia local**, para
que no pudiera leerse del daemon. Trivy registró por su cuenta, sin intervención del
atestador:

```
RepoDigests : ghcr.io/jeffersondavila/personal-blog-minio@sha256:84c67632…059129
ImageID     : sha256:25c832aa396d4de7eb2d202529ee8055280633f0ef270687e565bd376d1882a2
```

Es decir: el `RepoDigests` **ya no lo inyecta** el paso `attest`; lo aporta el registro.
Se comprobó además que aplicar el atestado **no modifica** `ArtifactName` ni `RepoDigests`
—idénticos antes y después—: solo añade el bloque `PersonalBlogDerivative`.

*(Hasta el 2026-09-18 esta sección decía que el digest **no** era un RepoDigest, que GHCR no
había recibido ninguna publicación y que la referencia del Compose no era resoluble. Era
cierto entonces y consta abajo como historia; dejó de serlo con la publicación del
2026-09-19.)*

### Historia previa, conservada

**Comprobado el 2026-09-18**, cuando el paquete todavía no existía:

```
GET users/jeffersondavila/packages/container/personal-blog-minio
  -> HTTP 404  "Package not found."

GET ghcr.io/v2/jeffersondavila/personal-blog-minio/manifests/RELEASE.2025-09-07T16-13-09Z-amqp091-go1.13.0
  -> HTTP 403  (sin manifiesto accesible)
```

En esa fecha el paquete no existía y no se intentó publicarlo. Un primer intento del
2026-09-19, previo a que existiera credencial de registro en este perfil, fue **rechazado por
el registro con `denied`** y no publicó nada; la imagen cargada para intentarlo se eliminó.

---

## 10. Procedimiento de publicación — EJECUTADO y verificado

Estaba escrito como plan; se ejecutó el **2026-09-19** bajo autorización humana explícita y
acotada. Cada condición de continuación se cumplió.

| # | Paso | Exigencia | Resultado |
| --- | --- | --- | --- |
| **a** | Publicar exactamente el OCI validado, sin reconstruir ni reetiquetar | El OCI publicado debe ser el verificado | **Cumplido.** Mismo tar (`sha256 c4a115ad…`), `artifact.py verify` exit 0 antes de publicar |
| **b** | Resolver el RepoDigest real de GHCR | Debe devolver un digest, no un error | **Cumplido.** `imagetools inspect` y `manifest inspect` devuelven `sha256:84c67632…059129` |
| **c** | Exigir correspondencia con la identidad esperada | Si difiere, **detenerse** | **Cumplido.** Coincide con `build-manifest.json` y con el baseline; además el `sha256` del manifiesto crudo remoto lo confirma |
| **d** | Reescanear por la referencia remota exacta y repasar S-09 | **99 exactas, 0 nuevas** | **Cumplido.** Trivy con `--image-src remote`; S-09 `CORRECTO` (§5b) |
| **e** | Abortar el cierre Git ante cualquier discrepancia | No hay *commit* mientras haya diferencias | **No hubo ninguna discrepancia.** Aun así **no se hizo *commit*, *push*, *merge* ni PR**: no por discrepancia, sino porque el alcance original **aún no estaba aprobado el 2026-09-19** |

### Preflight ejecutado antes de publicar

Rama `Task/027.1-Corregir-Regresion-S09-MinIO` · **0** commits propios · *staging* vacío ·
mismo OCI existente (`sha256 c4a115ad…`, 101 769 728 bytes) · `artifact.py verify` **exit 0**
· manifest digest **idéntico** al `build-manifest.json` · GHCR **sin esa etiqueta** (`404`).

### Lo que la publicación NO resuelve — licencia y distribución

Por la licencia **AGPL-3.0** de MinIO Community, distribuir la imagen obliga a ofrecer el
código correspondiente: commit upstream exacto, parche, `Dockerfile`, manifiesto de
construcción, SBOM y procedencia.

**Parcialmente satisfecho desde el cierre aprobado del 2026-09-20**, y dicho con precisión:

- **Sí queda disponible** el código correspondiente esencial: `docker/minio/Dockerfile`, el
  parche `minio-amqp091-go-1.13.0.patch`, `build-manifest.json` —con el commit upstream
  exacto `07c3a429…` y todos los digests—, `docker/minio/README.md` y
  `scripts/minio/artifact.py` quedan **versionados** y **publicados** con el *push* de la
  rama, en `jeffersondavila/personal-blog-infra`, que es un repositorio **público**.
- **Todavía NO se publican junto a la imagen** el **SBOM** ni la **procedencia**: `CI Infra`
  los genera de forma determinista, pero no los adjunta al paquete como artefactos.

Lo que acota el alcance es que **el paquete de GHCR permanece PRIVADO**: no hay distribución
pública de la imagen mientras siga así.

> **Condición de salida, todavía vigente:** antes de hacer público el paquete conviene
> publicar SBOM y procedencia junto a la imagen, para que la oferta de fuentes la acompañe y
> no dependa de reconstruirla. La visibilidad **no se modificó** en este cierre.

---

## 11. Estado de Git histórico — antes de la primera aprobación del 2026-09-20

| Comprobación | Resultado |
| --- | --- |
| Rama activa (infra) | `Task/027.1-Corregir-Regresion-S09-MinIO` |
| `git rev-parse HEAD` vs `main` | **coinciden**, `67c1904` |
| `git rev-list --count main..HEAD` | **0** |
| Archivos sin *commit* | **7 modificados**, **6 nuevos** de implementación, más la documentación de este cierre |
| *Staging* | vacío |
| `personal-blog-backend` | `main`, limpio, sin rama Task |
| `personal-blog-frontend` | `main`, limpio, sin rama Task |
| `Task/027` | **Aprobada**; pull request `#47` **OPEN, sin fusionar** |
| `Task/028` | **no iniciada** |
| Publicación GHCR | **HECHA** el 2026-09-19 y verificada: RepoDigest remoto `sha256:84c67632…059129`, idéntico al esperado |
| Visibilidad del paquete GHCR | **PRIVADO**, sin modificar |

En aquella fase previa **no** se hizo commit, push de Git, merge ni pull request, ni se promovió
ninguna decisión a Aceptada. Las decisiones `D-027.1-A` a `D-027.1-F` siguen como
**Propuesta — pendiente de aprobación**.

### Aprobación y cierre — 2026-09-20

El usuario aprobó la tarea con `approved: Task/027.1-Corregir-Regresion-S09-MinIO`. A partir
de ese momento, y **solo entonces**, el cierre aprobado ejecutó: *commit* de los 19 archivos,
integración en `dev` con merge `--no-ff`, publicación de `dev` y de la rama Task, y creación
del pull request **`Task/027.1 → main`**, que **no se fusionó**: aceptar un PR hacia `main`
es responsabilidad exclusiva del usuario.

Con la aprobación, **D-027.1-A** a **D-027.1-F** pasan a **Aceptadas y Vigentes**, sin ADR
nuevo. **El avance no cambia**, porque el mantenimiento no cuenta entre las 41 tareas; la
cifra vigente la fija la última tarea canónica aprobada.

> **Corrección documental del 2026-09-21:** el avance no depende de la rama ni de
> fusionar un PR. Task/027 fue aprobada el 2026-09-17: el avance vigente es **27/41 ≈ 66 %**,
> ETAPA 09 **1/3 ≈ 33 %**. El `main` histórico tras Task/026 reflejaba **26/41**;
> no corresponde al estado duradero posterior a la aprobación de Task/027.

**Matiz sobre `D-027.1-F`.** Esa decisión decía «no publicar en GHCR dentro de esta tarea».
El usuario autorizó después una **fase controlada de publicación**, explícitamente **no
equivalente** a aprobar la tarea, y la publicación se ejecutó en ese marco. La decisión se
conserva tal cual como registro de lo decidido en la fase de implementación; lo que cambió
es que **existió una autorización posterior y acotada**, no el criterio de que publicar
requiere permiso humano explícito.

El **alcance original MinIO** recibió su primera aprobación el 2026-09-20.
Observados el 2026-09-21, los commits publicados anteriores eran `7e7d56e`, `6890ded`
y `df3ba33`; este último contiene la corrección BuildKit de §12b. El addendum posterior
requiere **nueva aprobación** (§14–§15).

---

## 12. Limitaciones residuales

1. **La distribución conforme a AGPL-3.0 queda resuelta solo en parte.** La imagen está
   publicada, la referencia de `.env.example` **resuelve**, y el cierre del 2026-09-20
   **versiona y publica** el código correspondiente esencial en un repositorio **público**.
   **Falta** publicar **SBOM y procedencia junto a la imagen**. El paquete sigue **PRIVADO**,
   lo que acota el alcance. Es **DT-027.1-1**.
   *(Hasta el 2026-09-18 esta limitación decía que la imagen no estaba publicada y que un
   `docker compose up` limpio fallaría: cierto entonces, resuelto con la publicación del
   2026-09-19.)*
2. **`R-018-3` sigue ABIERTO** con 99 identidades. Esta tarea redujo el conjunto y lo ató a
   un manifiesto verificado; no lo cerró.
3. **La construcción usa red.** No es hermética ni offline. Lo demostrado es la identidad
   fijada y verificada de cada entrada.
4. **La reproducción A/B no se repitió hoy.** Se produjo una tercera construcción idéntica;
   los dos *builders* originales ya se eliminaron.
5. **La evidencia funcional de §7 no se reejecutó** en esta sesión y su contenedor ya no
   existe.
6. **Posibles conflictos al consolidar en Task/027.** El usuario fijó el orden el
   2026-09-21 (§15). Se resolverán semánticamente y se conservarán ambos alcances;
   la consolidación requiere autorización posterior y no se ejecuta en esta fase.
7. **El escaneo local de Terraform y del provider no usó exactamente los mismos binarios que
   el CI.** Está detallado en §3, con el motivo y la equivalencia demostrada.

---

## 12b. Addendum histórico — 2026-09-20: portabilidad del CI

**Publicado en `df3ba33`, después de la primera aprobación.** El cierre posterior sin
merge del PR #48 se fecha en §15. No se implica una fusión que nunca ocurrió.

### Qué falló

Tras integrar la tarea en `dev`, `CI Infra` quedó **rojo** en el paso «Build the project
images» (run `35543639572`, sobre `853ff90`):

```
#0 building with "default" instance using docker driver
ERROR: failed to build: OCI exporter is not supported for the docker driver.
Switch to a different driver, or turn on the containerd image store, and try again.
```

`personal-blog-postgres:ci` y `personal-blog-traefik:ci` **construyeron correctamente**; el
log muestra `#7 DONE 1.0s` para traefik justo antes del error. Falla el comando siguiente,
el `docker buildx build --output type=oci` del derivado.

### Causa

El workflow no creaba ni seleccionaba ningún builder, así que buildx usaba la instancia
`default`, cuyo **driver `docker`** no implementa exportadores. El exportador OCI exige un
driver `docker-container`.

**Por qué no se detectó localmente:** la validación usó builders `docker-container`
explícitos y, además, Docker Desktop tenía el *image store* de containerd. Dos motivos
independientes para funcionar que el runner no tiene. El gate de YAML era estructural
—parseo y presencia de `name`/`run`—, no semántico, y `actionlint` no forma parte del flujo
ni conoce los drivers de buildx.

### Corrección aplicada

Un builder **aislado** solo para este paso, con la imagen de BuildKit **fijada por digest**:

- `IMAGEN_DE_BUILDKIT: moby/buildkit@sha256:28a898…41d8` — **índice multi-arquitectura**
  verificado contra el registro, que contiene `linux/amd64`
  (`sha256:040d3412…`) y corresponde a **BuildKit v0.32.2**, commit `991535e0…`: la **misma**
  versión que produjo la identidad OCI verificada de esta tarea. No se usa la etiqueta
  `buildx-stable-1`, que es móvil.
- **No** se pasa `--use`: el builder por defecto sigue siendo el `docker`, de modo que
  `docker build` de Postgres y Traefik **no cambia** y sus imágenes siguen quedando en el
  daemon, que es donde Trivy las busca.
- El builder se retira con un `trap` que **conserva y reemite** el código de salida real, sin
  enmascarar un fallo del build.
- **No** se habilita containerd globalmente en el runner.

### Lo que NO cambia — verificado, no supuesto

Se reconstruyó el OCI con el builder dedicado, **sin caché y con `--pull`**, igual que el CI.
Es la **cuarta** construcción independiente de esta tarea:

| Comprobación | Resultado |
| --- | --- |
| `manifest_digest` | `sha256:84c67632…059129` — **idéntico** |
| `config_digest` | `sha256:25c832aa…882a2` — **idéntico** |
| `binary_sha256` / tamaño | `9437671a…` / 111 145 144 — **idénticos** |
| Número y **orden** de layers | 10, mismos digests y mismos tamaños |
| `mediaType` | `application/vnd.oci.image.manifest.v1+json` |
| `artifact.py verify` | **exit 0** |
| `artifact.py compare` (OCI previo vs nuevo) | `"reproducible": true` |
| `docker/minio/build-manifest.json` | **sin cambios** (`4e47cebc…`) |
| `security/vulnerability-baseline.json` | **sin cambios** (`69ee2b6d…`) |
| Dockerfile, parche, fuente, `amqp091-go` | **sin cambios** |
| Imagen publicada en GHCR | **sin tocar**; el paquete sigue **privado** |

Si el digest hubiera cambiado aunque fuera un byte, `artifact.py verify` lo habría rechazado
en el propio CI: el control es *fail-closed*.

### Regresión añadida

`tests/security/test_workflow_build_drivers.py` — **14 pruebas** que comprueban el
**contrato del workflow**, no el entorno. Un `docker buildx build` con exportador
incompatible con el driver `docker` (`oci`, `tar`, `local`) queda en rojo si: no declara
`--builder`; usa un builder no creado antes en el workflow; ese builder no es
`docker-container`; su imagen de BuildKit no va por digest; o se crea con `--use`.

Incluye **cinco controles negativos demostrados**: cada uno manipula el workflow y exige que
la verificación **falle**, empezando por quitar el `--builder`, que es exactamente el defecto
que rompió el CI. Una prueba explícita garantiza que el contrato **no** se impone a los
builds de Postgres y Traefik.

---

## 13. Cierre original — historia y estrategia sustituida

| Hecho histórico | Fecha / evidencia |
| --- | --- |
| Publicación MinIO autorizada, ejecutada y verificada | 2026-09-19, §9–§10 |
| Primera aprobación humana del alcance MinIO | 2026-09-20, §11 |
| Código correspondiente esencial versionado y publicado | Cierre original, §10–§11 |
| PR #48 creado para Task/027.1 → main | Cierre original del 2026-09-20; cierre sin merge observado el 2026-09-21, §15 |
| BuildKit corregido y publicado | `df3ba33`, 2026-09-20, §12b |

El plan anterior contemplaba fusionar #48 y decidir después el orden frente a #47.
**Fue sustituido por instrucción del usuario del 2026-09-21**: no reabrir ninguno,
no crear otro PR de 027.1; consolidar íntegramente en 027 solo tras las autorizaciones
separadas de §15. SBOM/procedencia junto a la imagen siguen pendientes (DT-027.1-1).

## 14. Addendum Floci — regresión S-09 descubierta durante el cierre de Task/027.1

**Addendum Floci / regresión S-09 descubierta durante el cierre de Task/027.1.**
Ejecutado el **2026-09-20 (Guatemala; 2026-09-21 UTC)**. Estado: **Aprobado** el
**2026-09-21** (§16). Las secciones anteriores son historia del alcance MinIO y su cierre
aprobado; **aquella aprobación no autorizaba publicar este addendum**, la del 2026-09-21 sí.

### 14.1 Alcance, Git y CI publicados

El usuario amplió expresamente `Task/027.1`, siguiendo el precedente de `Task/020.3`.
No se crea otra maintenance ni `Task/025.1`; no cuenta entre las 41 ni altera el avance.
Floci continúa siendo **solo laboratorio local**; **no se despliega Floci a AWS** y
producción usa **AWS real**. Nada de esta evidencia declara paridad completa.

Se ejecutó `git fetch --all --prune` antes de editar. Observación del **2026-09-20
(Guatemala; 2026-09-21 UTC)** al iniciar y terminar la implementación del addendum: ramas y heads publicados conservados; cambios del addendum exclusivamente locales.

| Referencia | SHA completo observado |
| --- | --- |
| `main = origin/main` | `67c1904944fc624b15c15e466f575f055c5c312d` |
| `dev = origin/dev` | `853ff905078cbe35e864ec9af2c5add4690e7491` |
| `HEAD = origin/Task/027.1-Corregir-Regresion-S09-MinIO` | `df3ba33777058f6cbad1747e3d695c09e7a74fee` |
| Head publicado de Task/027 | `e158e60543c159066c592e310c0526ebb1dea498` |

Árbol y staging iniciales vacíos. Final: cambios sin commit y staging vacío. No se crea
rama, no se toma `dev` como base, no se reescribe historial y no se modifica Task/027.

Observados el **2026-09-20**: [PR #48](https://github.com/jeffersondavila/personal-blog-infra/pull/48)
y [PR #47](https://github.com/jeffersondavila/personal-blog-infra/pull/47) **OPEN**, hacia
`main`, ambos con checks publicados **FAILURE**. El run de #48
[35545696830](https://github.com/jeffersondavila/personal-blog-infra/actions/runs/35545696830)
superó construcción de imágenes y verificación/SBOM de MinIO, y falló únicamente en el
gate S-09. No se reabre BuildKit: el bloque corregido en `df3ba33` permanece intacto.

**Esta evidencia de CI es histórica.** El usuario cerró después ambos PR sin merge
y sustituyó la estrategia de entrega (§15). Los gates del addendum son locales; no se
afirma una ejecución remota de cambios sin publicar. Task/027 conserva su aprobación,
Task/028 no se inicia y solo el usuario fusiona hacia main.

### 14.2 Identidad y revisión de upstream

`docker buildx imagetools inspect floci/floci:2.1.0` resolvió nuevamente:

| Identidad | Digest |
| --- | --- |
| Índice OCI 2.1.0 | `sha256:f5aa8c18302cedb4f2385f5c4e455b3efc77fee6bf7b6e5d1712b2817ba102db` |
| Manifiesto `linux/amd64` | `sha256:2e2343974a15137a6bda6de5a9e0b16207f97a786cc57ee9c2bf25d14a67b84c` |

Se revisaron el [release estable 2.1.0](https://github.com/floci-io/floci/releases/tag/2.1.0)
y el código de esa etiqueta. Incluye persistencia de Tags en `PutParameter`, cambio a
UBI micro y retirada de gosu. El inventario confirma que **openssl y libevent desaparecen**;
las siete regresiones no se remedian actualizando esos paquetes, sino retirándolos.
No se usa `latest`, nightly, una imagen derivada ni paquetes añadidos.

### 14.3 Healthcheck y hallazgo DNS durante S-11

La sonda ejecuta `/bin/bash -ec` con builtins exclusivamente, conexión `/dev/tcp`, lectura
con plazo y límite global de Docker de 4 s. Exige **HTTP 200** y `s3`, `ssm`, `lambda`,
`logs`, `iam`, `apigateway` en `running` dentro de `services`. Se escapan los dólares para
Compose. El contenedor final quedó **healthy** y exigir `inexistente` devolvió **exit 1**.
Pruebas con `PATH` vacío, respuestas HTTP controladas y servicio ausente/detenido impiden
reintroducir curl, wget, Python, jq, grep, sed, awk u otros ejecutables en la sonda.

La imagen conserva `timeout` y `getent`: se comprobó, por lo que no se alteró la sonda
preexistente de red del lanzador. **Esa sonda no basta por sí sola** para acreditar el DNS
del runtime Lambda: usa los resolutores ordinarios de Docker.

La primera observación del **contenedor Lambda real** descubrió una ruta adicional:
Floci inyectaba su IP y `8.8.8.8/8.8.4.4` como DNS; su servidor reenviaba consultas a
través de la red `entrada`. `example.com`, `github.com` y `registry-1.docker.io` resolvían,
aunque Internet TCP y metadata estaban bloqueados. La afirmación heredada del preflight
«DNS externo bloqueado» **no se tomó como evidencia del runtime**.

Se verificó la causa en
[EmbeddedDnsServer.java](https://github.com/floci-io/floci/blob/2.1.0/src/main/java/io/github/hectorvent/floci/core/common/dns/EmbeddedDnsServer.java)
y [ContainerBuilder.java](https://github.com/floci-io/floci/blob/2.1.0/src/main/java/io/github/hectorvent/floci/core/common/docker/ContainerBuilder.java).
Desactivar solo `container-fallback-enabled` no cierra el reenvío del servidor.

Corrección acotada al Compose: `dns: ["::1"]`,
`FLOCI_DNS_CONTAINER_FALLBACK_ENABLED=false` y
`FLOCI_DNS_CONTAINER_FALLBACK_SERVERS=::1`. Los resolutores quedan en loopback IPv6,
donde la imagen fijada no tiene servidor DNS; Floci escucha DNS solo en IPv4.
Docker sigue resolviendo nombres locales. El daemon descarga imágenes separadamente;
se fijaron y precargaron antes del ciclo. No se necesita DNS externo en el emulador.
Esta condición depende del runtime fijado y se debe revalidar al actualizarlo (S-11).

El gate CI de loopback interpretaba cualquier línea YAML acabada en `:número` como puerto
y confundió `::1` con una publicación. Ahora usa **`docker compose config --format json`**
y examina exclusivamente `services[*].ports[*].host_ip`. Controles negativos rechazan LAN,
`0.0.0.0`, `::`, binding omitido y lista vacía. El bloque BuildKit permanece idéntico.

### 14.4 Baseline: reducción exacta, no regeneración

Trivy **0.74.0**, misma BD para todas las comparaciones, `UpdatedAt`
`2026-09-20T19:19:55.870896177Z`. Se observaron **112 → 22 entradas de paquetes** en los
informes completos (el preflight había estimado 111 → 21); no se sustituye la medida
actual por aquella aproximación. El escaneo de 2.0.1 dio
**77 accionables**, **70 exactos históricos**, **7 nuevos** conocidos. 2.1.0 dio
**2 exactos históricos**, **68 retirados**, **0 nuevos**.

| CVE residual | Paquete | Instalada | Corregida | Severidad / scope |
| --- | --- | --- | --- | --- |
| CVE-2026-4878 | libcap | 2.48-10.el9_7.1 | 2.48-10.el9_8.1 | HIGH / os-pkgs:redhat |
| CVE-2026-54369 | libacl | 2.3.1-4.el9 | 2.4.0-1.el9_8 | HIGH / os-pkgs:redhat |

`package_path` vacío en ambas. Los dos objetos se conservan exactamente del baseline
histórico; se eliminan solo los 68 ausentes. Todas las demás entradas del baseline,
**incluida MinIO**, son estructuralmente idénticas a `HEAD`. Las siete CVE de la regresión
(`14456`, `63382`, `63383`, `63384`, `63385`, `63387`, `63388`, todas de 2026) no se aceptan.
Se actualiza la justificación de H-025-6 sin heredar a 2.1.0 el análisis de símbolos de
gosu/usermod de 2.0.1. La falta de cobertura Maven/Java del binario nativo sigue declarada.

### 14.5 S-11 y pruebas funcionales reales

Laboratorio efímero `task0271-floci-addendum`, binding exclusivo `127.0.0.1:14566`,
cuenta ficticia `000000000000`, recursos `blog-lab-add0271-*`. Estado y harness fuera
del repositorio. Mismos módulos y grafo Terraform; solo valores locales temporales.
Herramienta **1.16.2**, provider **6.64.0** y runtime del manifiesto Task/024 verificados.

| Comprobación | Resultado observado |
| --- | --- |
| Destino/credenciales | `production` rechazado; credencial no ficticia rechazada; STS de cuenta ficticia confirmado antes de escribir |
| Plan/apply | 21 recursos creados; sin cambios ni destrucciones imprevistas |
| S3 | PUT/GET/DELETE, contenido idéntico, ListObjectsV2 y URL prefirmada correctos |
| SSM / H-025-1 | 4 parámetros leídos; cuatro tags persistidos por parámetro; `PutParameter` directo con Tags y readback correcto |
| IAM | GetRole 200 y confianza a Lambda; no acredita enforcement |
| Inventario API antes de destroy | El parser corregido devuelve `blog-lab-add0271-api`; el control negativo rechaza declararlo ausente |
| Segundo plan | **No changes, detailed-exitcode 0**, sin tolerancia a `tags_all` |
| API Gateway → Lambda | GET /health **HTTP 200**, cuerpo del backend correcto |
| CloudWatch Logs | Eventos reales de invocación y `/health 200` recuperados |
| Destroy | 21 recursos destruidos; estado vacío y ausencia contrastada por APIs, incluido API Gateway; IAM 404 y cuatro SSM exactos ausentes |

**Cold start correcto:** se retiró exclusivamente
`floci-code-blog-lab-add0271-backend-ZYBBAQkgfzMKMp7iNeBC` y se comprobó la ausencia de
contenedores de esa función antes de invocar. `ClienteAws(..., tiempo_limite=300)` real,
sin monkey-patching; duración mediante `time.monotonic()`.

| Invocación final | Duración | Transporte | Payload | Contenido |
| --- | --- | --- | --- | --- |
| Cold, volumen de código ausente | **16,063 s** | HTTP 200 | statusCode 200 | status=ok, service=personal-blog-backend, version=0.1.0 |
| Segunda invocación, código ya preparado | **3,750 s** | HTTP 200 | statusCode 200 | mismo contenido |

El Compose usa ejecución efímera: «warm» aquí significa segunda invocación con el volumen
de código preparado; **no prueba reutilización de un mismo proceso Lambda**, ni mide
rendimiento comparable con AWS. El intento inicial respondió en 16,641 s, pero su harness
filtraba por etiqueta literal y no capturó el runtime solicitado por ID; se corrigió el
observador temporal para comparar el ID efectivo y se repitió desde frío. La siguiente
observación descubrió el DNS expuesto; esa ejecución tampoco se presentó como validación
final. Se conserva el diagnóstico y la repetición final anterior.

**Aislamiento del runtime real:** imagen
`sha256:a89893d9c93a9ffbf9e35ca32d7cadc635cbf3a9aec94480c75ed07150a05daa`, solo en
`task0271-floci-addendum_ejecucion`; emulador HTTP **200**; TCP `1.1.1.1:443`, DNS externo
y metadata `169.254.169.254:80` **bloqueados**. DNS del contenedor: solo la IP del emulador,
sin resolutores públicos. La sonda Python se ejecutó por `docker exec` dentro de ese
contenedor; el límite de resolución del harness fue acotado sin modificar producción.

El launcher usa `test/test`. Floci entrega al runtime **credenciales temporales sintéticas
ASIA…**, correspondientes al rol de la cuenta ficticia; no se afirma que el runtime use
literalmente `test/test`. `AWS_ENDPOINT_URL=http://emulador:4566` y
`AWS_EC2_METADATA_DISABLED=true` comprobados. Valores completos de credenciales omitidos.
La antigua asignación a `ClienteAws.__init__.__defaults__` no ajustaba el parámetro
keyword-only; **no se reutiliza ni se presenta como cold de 180 s**.

### 14.6 S-09 completo y MinIO intacto

| Artefacto | Accionables / exactos | Nuevos |
| --- | --- | --- |
| PostgreSQL construido | 0 / 0 | 0 |
| Traefik construido | 0 / 0 | 0 |
| MinIO remoto GHCR | **99 / 99** | **0** |
| Portainer | 16 / 16 | 0 |
| Floci 2.1.0 | **2 / 2** | **0** |
| Terraform linux_amd64 | 9 / 9 | 0 |
| Provider AWS windows_amd64, sin baseline | 0; 377 paquetes inventariados | 0 |

Gate canónico: **RESULTADO: CORRECTO, 126 accionables comparados**. Terraform Linux:
253 paquetes; ZIP verificado por SHA-256 fijado, escaneo dentro de Linux. El provider
escaneado localmente es Windows; el CI escanea Linux. No se confunden ambos artefactos.

MinIO se escaneó con `--image-src remote`. RepoDigest nativo del informe:
`ghcr.io/jeffersondavila/personal-blog-minio@sha256:84c67632f7e85d4cd86ea5f7f6fbb6b5b8263ecd20f08153c4cd1a42e3059129`.
Se verificó el OCI **ya existente**, sin reconstruir: config, binario y diez layers idénticos;
`artifact.py verify` y atestado correctos, `amqp091-go v1.13.0`. Dockerfile, parche,
build-manifest, scripts MinIO, referencia principal y baseline MinIO intactos. No se hizo
push de imagen ni cambio de visibilidad. La consulta REST de visibilidad no pudo repetirse:
el token de `gh` carece de `read:packages` (403); no se presenta como una nueva lectura
exitosa del atributo. La condición privada documentada previamente no se modifica.

### 14.7 Gates y regresiones

- **64/64** pruebas de `tests/security`; **176/176** de `tests/laboratorio`: **240**.
- RED demostrado antes de corregir API Gateway, sonda sin curl, tolerancia SSM, DNS y
  gate de puertos; GREEN final de ambas suites completas. Las pruebas genéricas históricas
  de tolerancias permanecen; se retira solo la tolerancia activa ya resuelta.
- Coherencia del baseline, Terraform fijado `fmt/init -backend=false -lockfile=readonly/validate`,
  lock intacto y presencia de fuentes/lock versionados: correctos.
- Compose principal con perfil admin (**7 servicios**) y Compose de laboratorio válidos;
  variables principales **26/26**, guardas de loopback/digest/socket/red correctas.
- **6** scripts PowerShell versionados parseados, **13** scripts Python compilados,
  **0** scripts shell versionados. YAML de Compose parseado por Docker y workflow por
  **actionlint 1.7.12**; sin ShellCheck/Pyflakes adicionales, que no son gates vigentes.
- PostgreSQL/Traefik construidos con las bases fijadas y reescaneados. MinIO: verificación
  del OCI existente, SBOM y procedencia regenerados con los mismos hashes de §6,
  **sin reconstruir** por instrucción expresa. El intento de leer el OCI por ruta Windows
  no fue soportado por Trivy; se completó dentro de Linux sobre el mismo OCI montado en
  lectura. La evidencia de build es la CI publicada; esta es la excepción local al paso
  de build completo.
- S-09 completo y siete inventarios generados. `git diff --check` y staging: correctos.
  **Gitleaks 8.30.1: 0 hallazgos**, tanto en todo el historial alcanzable (`--all`) como
  en los **227 archivos** del entregable sin commit. **1535 enlaces relativos, 0 rotos**;
  anchor nuevo del addendum comprobado. Suites finales sin ResourceWarning.

### 14.8 Archivos y límites

Cambios funcionales: plantilla/Compose del laboratorio; baseline; parser de API Gateway;
tolerancia SSM del launcher; referencia Floci y lectura de puertos en CI. Regresiones:
`test_verificacion.py`, `test_lanzador.py`, `test_healthcheck.py`,
`test_floci_addendum.py`, `test_workflow_lab_ports.py`. Documentación: esta ficha/reporte,
STATUS/ROADMAP, matriz de paridad y seguimiento de los hallazgos históricos de Task/025.

**H-025-1 cerrada técnicamente** en este addendum, cuya aprobación sigue pendiente;
la evidencia de 2.0.1 permanece histórica. **H-025-6 abierta con dos identidades exactas**.
Siguen abiertos R-018-3 (99), Portainer (16), H-025-7 (9), cobertura del binario nativo de
Floci y las limitaciones AWS-only: privacidad efectiva de S3, IAM, cifrado SSM, alarmas,
cuotas y rendimiento. La lectura anónima S3 devolvió 200: no se oculta ni se llama seguridad
validada en AWS. DT-027.1-1 (SBOM/procedencia junto al paquete) permanece pendiente.

Las pruebas usaron recursos temporales del addendum; se retiraron sus contenedores,
volúmenes de código/datos, redes y etiquetas de imagen propias, y se eliminó el estado
Terraform temporal después de verificar ausencia. Se conservaron informes e inventarios
de evidencia fuera de Git. El stack `personal-blog-local-*` conserva IDs, imágenes,
montajes y tiempos de arranque; cinco servicios con healthcheck **healthy** y Portainer
**running** (sin healthcheck declarado). No se recreó ni reinició.

**Detención:** cambios locales revisables, sin staging, commit, push, merge ni PR nuevo.
Nueva aprobación `approved: Task/027.1-Corregir-Regresion-S09-MinIO` necesaria para publicar.
La estrategia de §15 sustituye cualquier referencia anterior a continuar mediante #47/#48.

## 15. Reconciliación documental y estrategia de cierre — 2026-09-21

**Estado en el momento de escribir esta sección: Lista para validación, pendiente de nueva
aprobación humana.** La aprobación MinIO del **2026-09-20** es un hecho histórico; el
usuario autorizó después el addendum Floci, cuyas decisiones eran entonces
**Propuesta — pendiente de aprobación**. **Esa espera terminó el 2026-09-21:** el usuario
aprobó el addendum y sus decisiones pasaron a **Aceptadas y Vigentes** (§16). Lo que sigue
en esta sección es la instantánea de aquella fase y la estrategia de cierre que sigue
gobernando las fases posteriores.

**Estado duradero del proyecto:** Task/027 **Aprobada** el 2026-09-17; avance
**27/41 ≈ 66 %**; **Stage09 / ETAPA 09: 1/3 ≈ 33 %, En progreso**. Task/027.1 es
mantenimiento, fuera de las 41. Task/028 **Pendiente, no iniciada**. **26/41** solo
describe el cierre histórico de Task/026/main previo a aprobar Task/027.

**Observado el 2026-09-21:** el usuario cerró sin merge los
[PR #47](https://github.com/jeffersondavila/personal-blog-infra/pull/47) y
[PR #48](https://github.com/jeffersondavila/personal-blog-infra/pull/48), con `closedAt`
`2026-09-21T02:38:32Z` y `2026-09-21T02:38:38Z`, respectivamente, y `mergedAt=null`
en ambos. El cierre ocurrió el 2026-09-20 en Guatemala. Es un hecho histórico;
Git/GitHub son la fuente viva de ramas, PR y checks.

**Observado el 2026-09-21, tras `git fetch --prune origin`:** rama activa 027.1,
`HEAD = origin/Task/027.1-Corregir-Regresion-S09-MinIO =
df3ba33777058f6cbad1747e3d695c09e7a74fee`. Tres commits publicados sobre el main de origen:
`7e7d56e`, `6890ded`, `df3ba33`. Addendum local sin commit; staging vacío. La referencia
publicada de Task/027 conservaba `e158e60543c159066c592e310c0526ebb1dea498`.

Se reconciliaron completos STATUS, ROADMAP, ficha y reporte 027.1, reporte 025 y matriz de
paridad: cabeceras actuales, tablas de avance, primera aprobación, evidencia histórica,
H-025-1/H-025-6 y reglas de cierre. Se conservan las mediciones originales, identificando
sus límites: parser API histórico y prueba DNS genérica no sustituyen la evidencia nueva.
En esta fase solo se modifica documentación; código, Compose, baseline, MinIO y BuildKit
se conservan respecto del addendum ya validado. El laboratorio real de §14 no se repite.

### Puntos de detención y autorizaciones separadas

Esta instrucción expresa del usuario **sustituye el cierre ordinario de WORKFLOW para
esta entrega**; no cambia cómo nacen las ramas Task ni autoriza actuar anticipadamente.

1. **Fase actual:** reconciliar documentación y revalidar los gates locales. Detenerse
   con 027.1 Lista para validación. **Sin commit, push, merge, cambio a Task/027 ni PR.**
2. **Solo al recibir de nuevo exactamente**
   `approved: Task/027.1-Corregir-Regresion-S09-MinIO`: registrar aprobación, crear los
   commits del addendum en 027.1, publicar esa rama y verificar su SHA remoto final.
   **Detenerse y presentar el SHA.** No crear PR, no reabrir #48, no integrar en dev.
3. **Solo con otra autorización de consolidación:** cambiar a
   `Task/027-Configurar-Cuentas-y-Presupuestos`, verificar el commit original `e158e60`
   y todo su alcance, e integrar mediante
   `git merge --no-ff origin/Task/027.1-Corregir-Regresion-S09-MinIO`.
   Conservar todo el historial: sin squash, rebase, cherry-pick selectivo ni force push.
   Resolver conflictos semánticamente, sin `ours` o `theirs` global.
4. Validar todos los gates aplicables sobre **el árbol combinado**, preservando ambas
   entregas. No realizar nuevas acciones AWS/Cloudflare. Solo con el combinado verde,
   publicar Task/027 y crear **un único PR nuevo `Task/027 → main`**. No reabrir #47/#48
   ni crear otro PR de 027.1. **Detenerse; solo el usuario fusiona hacia main.**
   Task/028 no se inicia. La normalización `main → dev` corresponde al flujo posterior
   al merge manual, no a esta fase.

### Alcance que debe conservar la consolidación

- **Task/027:** cuentas AWS/Cloudflare, IAM administrativo separado, MFA, cero access keys,
  Free Plan, presupuestos, alertas, D-13 y toda la evidencia/documentación aprobada.
  Fuentes originales inmutables en `e158e60`:
  [ficha](https://github.com/jeffersondavila/personal-blog-infra/blob/e158e60543c159066c592e310c0526ebb1dea498/docs/tasks/TASK-027-cloud-accounts-and-budgets.md)
  y [reporte](https://github.com/jeffersondavila/personal-blog-infra/blob/e158e60543c159066c592e310c0526ebb1dea498/docs/task-reports/TASK-027-report.md).
  La reconciliación actual reconoce su aprobación; no sustituye ni importa selectivamente
  ese entregable cloud. Se conservará entero en su rama de entrega.
- **Task/027.1:** MinIO derivado, amqp091-go 1.13.0, OCI reproducible, GHCR privado,
  99/99, BuildKit `df3ba33`; Floci 2.1.0, baseline 70 → 2, H-025-1 resuelta,
  healthcheck sin curl, parser API fail-closed, aislamiento DNS, S-11, cold/warm,
  pruebas y toda su documentación. H-025-6 permanece abierta con dos identidades.

### Validación de esta reconciliación

Se reejecutan diff-check, enlaces relativos, Gitleaks worktree, barrido del criterio 12,
tests/security y tests/laboratorio, gate S-09 completo y coherencia, ambos Compose,
actionlint y parsers/compile aplicables. S-09 usa los siete informes completos ya
obtenidos con la misma BD de Trivy de §14.4; no se presenta como un escaneo con BD nueva.
Terraform y el ciclo real S-11 conservan la evidencia de §14: no se modificaron sus
entradas técnicas en esta reconciliación documental.

**Resultados del 2026-09-21, tras la reconciliación:**

| Gate | Resultado |
| --- | --- |
| Diff-check | Correcto; staging vacío |
| Enlaces relativos | **1547 comprobados, 0 rotos**; anclas nuevas verificadas |
| Gitleaks 8.30.1 worktree | **0 hallazgos**, sobre los **227 archivos** del entregable, incluidos los tres nuevos |
| Criterio 12 | Barrido de los seis documentos completos; referencias Git/PR como observaciones fechadas o reglas de cierre, sin estado transitorio como estado duradero |
| Coherencia del avance | STATUS y ROADMAP: **41 filas, 27 aprobadas, 14 pendientes**; Task/027 aprobada, Task/028 pendiente, Stage09 **1/3** |
| tests/security + tests/laboratorio | **64 + 176 = 240 PASS**, con `-W error::ResourceWarning` |
| S-09 completo y coherencia | **CORRECTO**, **126 exactas, 0 nuevas**; MinIO **99**, Floci **2**; provider **377 paquetes, 0 accionables** |
| Compose principal y laboratorio | Válidos |
| actionlint 1.7.12 | Correcto, sin ShellCheck/Pyflakes adicionales |
| Parsers / compile | **6 PowerShell** y **13 Python**, 0 fallos |
| Conservación técnica | **221 archivos ajenos a los seis documentos idénticos por SHA-256** respecto al comienzo de esta fase |

**Observación del stack, 2026-09-21:** los seis contenedores conservaban los IDs, imágenes
y montajes de la evidencia anterior; cinco estaban `healthy` y Portainer `running` sin
healthcheck. Sus `StartedAt` mostraban **2026-09-21T21:45:12Z**, frente a
`2026-09-21T01:16:14Z` en la instantánea de §14. No se afirma que los arranques siguieran
iguales entre sesiones. En esta fase no se ejecutó reinicio, recreación ni `compose up`;
la causa de ese arranque no se investigó ni se atribuye. La comprobación comparó los
montajes por destino: el orden de la lista de `docker inspect` no es una identidad.

---

## 16. Segunda aprobación y publicación del addendum — 2026-09-21

**Estado vigente: Aprobada.** Esta sección sustituye, como estado, a §15: aquella se
escribió mientras el addendum seguía pendiente y describe la fase anterior.

### 16.1 Registro de la aprobación

| Campo | Valor |
| --- | --- |
| **Fecha** | **2026-09-21** (Guatemala) |
| **Aprobado por** | **el usuario** (`jeffersondavila`) |
| **Expresión exacta recibida** | `approved: Task/027.1-Corregir-Regresion-S09-MinIO` |
| **Alcance cubierto** | El **addendum Floci** (§14) y su reconciliación documental (§15) |
| **Aprobación anterior** | 2026-09-20, alcance MinIO (§11). Se conserva íntegra como historia |
| **Efecto en el avance** | **Ninguno.** Es mantenimiento fuera de las 41: sigue **27/41 ≈ 66 %**, ETAPA 09 **1/3 ≈ 33 %** |

Las **decisiones del addendum** —Floci 2.1.0 por digest, reducción del baseline por
intersección exacta con el riesgo histórico, convergencia literal de SSM, healthcheck con
el Bash ya presente en la imagen, cierre del reenvío DNS del laboratorio e interpretación
*fail-closed* del inventario de API Gateway— pasan de **Propuesta** a **Aceptadas y
Vigentes**, **sin ADR nuevo**: ninguna altera una decisión arquitectónica aceptada.
**ADR-006 sigue Aceptada y Vigente**, Floci sigue siendo **laboratorio local**, nunca se
despliega a AWS y **no se declara paridad completa**.

### 16.2 Qué autorizó esta aprobación, y qué no

Por instrucción expresa del usuario —registrada en §15 antes de recibirla— esta aprobación
**sustituye el cierre ordinario de
[`WORKFLOW.md`](../project-management/WORKFLOW.md) y de la sección 8 de las instrucciones
del proyecto para esta entrega**. Autoriza **solo** el punto de detención 2: registrar la
aprobación, validar, *commitear* el addendum, publicar la rama y verificar su SHA remoto.

| Acción | Resultado |
| --- | --- |
| Registrar la aprobación y promover las decisiones | **Hecho** (§16.1) |
| Validaciones finales sobre el estado documentado | **Hechas** (§16.3) |
| Commit del addendum sobre `Task/027.1` | **Hecho** (§16.4) |
| Publicar **únicamente** la rama `Task/027.1` en `origin` | **Hecho** (§16.4) |
| Crear pull request | **NO.** Prohibido por la estrategia de cierre |
| Reabrir #47 o #48 | **NO** |
| Integrar en `dev` | **NO** |
| Cambiar a `Task/027` o consolidar con `merge --no-ff` | **NO.** Requiere otra autorización |
| Tocar `main` | **NO** |
| Iniciar `Task/028` | **NO.** Sigue **Pendiente, no iniciada** |
| Reconstruir, republicar o cambiar la visibilidad de la imagen de GHCR | **NO.** Paquete **privado**, sin modificar |
| Ejecutar acciones nuevas en AWS o Cloudflare | **NO** |

La excepción vale para **esta entrega** y no cambia cómo nacen las ramas Task: toda Task
sigue naciendo de `main` actualizado y limpio ([WORKFLOW §2.1](../project-management/WORKFLOW.md)).

### 16.3 Validaciones ejecutadas antes de publicar

Ejecutadas el **2026-09-21** sobre el árbol final, ya con la documentación de la
aprobación incluida. Se reejecutó la herramienta real, no se reutilizó el resultado de §15.

| Gate | Invocación | Resultado |
| --- | --- | --- |
| Diff-check | `git diff --check` | **Correcto**; sin conflictos ni espacios en blanco erróneos |
| `tests/security` | `python -B -W error::ResourceWarning -m unittest discover -s tests/security` | **64 PASS**, exit 0 |
| `tests/laboratorio` | `python -B -W error::ResourceWarning -m unittest discover -s tests/laboratorio` | **176 PASS**, exit 0 |
| Coherencia de artefactos fijados (S-09) | `vulnerability_gate.py --comprobar-coherencia .` | **CORRECTO**: `terraform` y `minio` coinciden con baseline, workflow y lanzador |
| Gate S-09 completo | `vulnerability_gate.py --reports <7 informes>` | **CORRECTO**: **126 accionables comparados, 0 nuevos**. MinIO **99**, Floci **2**, Terraform **9**, provider **0** |
| Compose principal | `docker compose --env-file .env.example --profile admin config --quiet` | **Válido** |
| Compose del laboratorio | `docker compose -f laboratorio/... --env-file laboratorio/... config --quiet` | **Válido** |
| Variables del Compose | Gate del workflow replicado | **26 usadas, 26 declaradas**, ninguna sin declarar |
| Compilación Python | Gate del workflow replicado | **13 archivos, 0 fallos** |
| Parseo PowerShell | Gate del workflow replicado | **6 archivos del entregable, 0 fallos** |
| Enlaces relativos Markdown | Verificador propio, excluyendo *fences* y código inline | **149 documentos, 1557 enlaces, 0 destinos rotos, 0 anclas sin resolver** |
| Gitleaks **8.30.1** | Versión y `sha256` fijados por `ci-infra.yml`, sobre el entregable de `git ls-files` | **0 hallazgos** |

**Límites declarados, sin adornos.** Estos son **gates locales**: no equivalen a una
ejecución de `CI Infra` en el runner. **Terraform y el ciclo real S-11 conservan la
evidencia de §14**: esta fase no volvió a levantar el laboratorio ni a ejecutar
`apply`/`destroy`, porque no modificó sus entradas técnicas. El gate S-09 reutiliza los
**siete informes completos** obtenidos en §14.4 con la misma base de datos de Trivy; **no
se presenta como un escaneo con base de datos nueva**. `actionlint` **no se ejecutó en
esta fase**: no hay binario disponible en este perfil y el workflow **no cambió** respecto
del estado que §15 validó con `actionlint 1.7.12`.

### 16.4 Operaciones Git del cierre

Ejecutadas **solo** en `personal-blog-infra`. `personal-blog-backend` y
`personal-blog-frontend` permanecieron en `main`, limpios y **sin rama Task**: esta tarea
no los modifica.

1. Rama activa verificada: `Task/027.1-Corregir-Regresion-S09-MinIO`, partiendo del
   publicado `df3ba33`.
2. Barrido de secretos sobre el entregable completo antes de *commitear*.
3. *Commit* del addendum sobre esa rama.
4. `git push origin Task/027.1-Corregir-Regresion-S09-MinIO`.
5. Verificación de que `HEAD` local y la referencia remota coinciden, contrastando contra
   `git ls-remote origin` —no contra la referencia local de seguimiento—.

**El SHA remoto resultante se presentó al usuario en el reporte de cierre.** No se escribe
aquí como constante: el estado vivo de ramas, commits y PR se consulta en Git y GitHub
—`git fetch --prune`, `git ls-remote --heads origin "Task/*"`, `gh pr list`—, nunca
leyendo este documento ([WORKFLOW §6.1](../project-management/WORKFLOW.md)).

### 16.5 Lo que sigue abierto tras esta aprobación

| # | Asunto | Estado |
| --- | --- | --- |
| **R-018-3** | Residual de MinIO | **ABIERTO**, 99 identidades. El derivado no lo cierra |
| **H-025-6** | Residual del emulador | **ABIERTA**, reducida a **dos** identidades exactas (`CVE-2026-4878` en `libcap`, `CVE-2026-54369` en `libacl`) |
| **H-025-7** | Residual de Terraform | **ABIERTA**, nueve riesgos, con sus condiciones de revisión |
| **H-025-1** | Idempotencia de SSM | **Cerrada técnicamente** en el laboratorio. La confirmación definitiva es **AWS real** (`Task/031`) |
| **DT-027.1-1** | SBOM y procedencia junto a la imagen | **Pendiente.** Se generan en CI pero no se publican como artefactos junto al paquete |
| **DT-027.1-3** | La construcción obtiene fuente y módulos por red | **Pendiente**, sin tarea asignada |
| **D-06** | Backend de estado de Terraform | Resuelta por `Task/025`; el bucket **no existe** |
| **Consolidación en `Task/027`** | `merge --no-ff` y PR único `Task/027 → main` | **Autorizada y ejecutada** el 2026-09-21, después de escribir esta tabla (§17) |
| **`Task/028`** | GitHub OIDC ↔ AWS | **Pendiente, no iniciada** |

**Nada de lo observado en Floci es hecho de AWS real.** Sigue siendo hipótesis hasta la
ETAPA 10 (ADR-006, límite 5).

---

## 17. Consolidación en Task/027 — 2026-09-21

**Hecho posterior a §16.** El usuario concedió la autorización de consolidación que §15 y
§16 declaraban pendiente. Las secciones anteriores **no se reescriben**: describen con
exactitud qué autorizaba cada aprobación por sí sola.

### 17.1 Qué se integró y cómo

`Task/027.1-Corregir-Regresion-S09-MinIO`, publicada en `39b6d59`, quedó integrada dentro
de `Task/027-Configurar-Cuentas-y-Presupuestos` mediante **`git merge --no-ff`** sobre el
commit original `e158e60`.

- **Historial completo conservado.** Sin *squash*, sin *rebase*, sin *cherry-pick*
  selectivo y sin *force push*. Los cinco commits de 027.1 —`7e7d56e`, `6890ded`,
  `df3ba33` y los dos del addendum, `5915299` y `39b6d59`— quedan como ancestros de
  `Task/027`.
- **Alcance cloud de `Task/027` intacto.** Sus dos entregables propios —la
  [ficha](../tasks/TASK-027-cloud-accounts-and-budgets.md) y el
  [reporte](TASK-027-report.md)— no se tocaron en la resolución: cuentas AWS y Cloudflare,
  IAM administrativo separado, MFA, cero access keys, Free Plan, presupuestos, alertas y
  **D-13 resuelta** siguen íntegros, byte a byte.
- **Conflictos:** solo dos documentos de gestión, `STATUS.md` y `ROADMAP.md`, resueltos
  **archivo por archivo y bloque por bloque**, nunca con `ours` o `theirs` global.

### 17.2 Qué NO cambia esta consolidación

- `Task/027` sigue siendo la **tarea canónica aprobada** el 2026-09-17 y **cuenta entre
  las 41**.
- `Task/027.1` sigue siendo **mantenimiento fuera de las 41** y **conserva su historia
  propia**. Lo único que cambia es la rama por la que se entrega.
- **El avance no se mueve:** **27/41 ≈ 66 %**, ETAPA 09 **1/3 ≈ 33 %**.
- `Task/028` sigue **Pendiente, no iniciada**.
- **H-025-1** resuelta; **H-025-6** abierta con dos identidades; **H-025-7** con sus nueve;
  **R-018-3** abierto con 99.
- MinIO **99/99** y Floci **2/2**, sin reconstruir, republicar ni cambiar la visibilidad
  del paquete de GHCR, que sigue **privado**.
- **Floci sigue siendo laboratorio local**: no se despliega a producción. **AWS real es el
  destino definitivo** y lo observado en el emulador es hipótesis hasta la ETAPA 10.
- Cero acciones nuevas en AWS o Cloudflare.

### 17.3 Entrega

`Task/027` pasa a ser la **única rama de entrega** hacia `main`, con **un único PR nuevo**
`Task/027 → main`. Los [PR #47](https://github.com/jeffersondavila/personal-blog-infra/pull/47)
y [PR #48](https://github.com/jeffersondavila/personal-blog-infra/pull/48) son **hechos
históricos**, cerrados sin merge el `2026-09-21T02:38:32Z` y el `2026-09-21T02:38:38Z`:
**no se reabren y no representan la entrega final**.

`dev` **no se modifica** en esta fase; su normalización pertenece al flujo posterior al
merge manual. **Solo el usuario fusiona hacia `main`.** El número, la URL y el estado vivo
del PR se consultan en GitHub, nunca leyendo este documento
([WORKFLOW §6.1](../project-management/WORKFLOW.md)).
