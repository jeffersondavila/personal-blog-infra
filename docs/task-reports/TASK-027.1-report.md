# TASK-027.1 — Reporte

| Campo | Valor |
| --- | --- |
| **Tarea** | `Task/027.1-Corregir-Regresion-S09-MinIO` |
| **Tipo** | Mantenimiento correctivo de seguridad (S-09) |
| **Cuenta en el roadmap** | **No.** Fuera de las 41 tareas; no altera el avance |
| **Estado** | **Aprobada** ✔ el 2026-09-20 por el usuario mediante `approved: Task/027.1-Corregir-Regresion-S09-MinIO` |
| **Repositorio** | `personal-blog-infra` (**únicamente**) |
| **Rama** | `Task/027.1-Corregir-Regresion-S09-MinIO`, nacida de `main` |
| **SHA base** | `67c1904` (`= main = origin/main`) |
| **Commits propios** | **0.** Sin *commit*, *push* de Git, *merge* ni PR |
| **Imagen en GHCR** | **Publicada** el 2026-09-19 y verificada contra el registro. Paquete **PRIVADO**; visibilidad **no modificada** |
| **Fecha del cierre de esta fase** | 2026-09-20 (Guatemala); implementación y gates, 2026-09-18; publicación, 2026-09-19 |
| **Ficha** | [TASK-027.1-fix-s09-minio-regression.md](../tasks/TASK-027.1-fix-s09-minio-regression.md) |

---

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
- **No se hizo *commit*, *push*, *merge*, pull request ni aprobación.**
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
| **e** | Abortar el cierre Git ante cualquier discrepancia | No hay *commit* mientras haya diferencias | **No hubo ninguna discrepancia.** Aun así **no se hizo *commit*, *push*, *merge* ni PR**: no por discrepancia, sino porque la tarea sigue **no aprobada** |

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

## 11. Estado de Git en la fase previa a la aprobación

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

Esta tarea **no** hizo *commit*, *push* de Git, *merge* ni pull request, y **no** promovió
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

> **Por qué no se fija aquí un número.** Esta rama nació de `main`, que todavía **no**
> contiene `Task/027`; la rama de integración `dev` **sí** la contiene. El avance vigente
> difiere entre ambas según esté fusionado o no el pull request `#47`, así que una cifra
> escrita aquí sería falsa en una de las dos. Lo que **no** depende de la rama es que este
> mantenimiento **no suma ni resta** avance.

**Matiz sobre `D-027.1-F`.** Esa decisión decía «no publicar en GHCR dentro de esta tarea».
El usuario autorizó después una **fase controlada de publicación**, explícitamente **no
equivalente** a aprobar la tarea, y la publicación se ejecutó en ese marco. La decisión se
conserva tal cual como registro de lo decidido en la fase de implementación; lo que cambió
es que **existió una autorización posterior y acotada**, no el criterio de que publicar
requiere permiso humano explícito.

La tarea quedó **Aprobada** el 2026-09-20.

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
6. **`STATUS.md` y `ROADMAP.md` entrarán en conflicto con `Task/027`.** Ambas ramas nacen
   del mismo `main` y tocan las mismas secciones de cabecera. El `main` de esta rama aún no
   contiene `Task/027`. El orden de integración lo decide el usuario; la resolución será
   manual y **no se anticipó por iniciativa propia**.
7. **El escaneo local de Terraform y del provider no usó exactamente los mismos binarios que
   el CI.** Está detallado en §3, con el motivo y la equivalencia demostrada.

---

## 12b. Addendum — 2026-09-20: portabilidad del CI (post-aprobación, pre-merge)

**No reescribe nada de lo anterior.** Es un hecho posterior a la aprobación y anterior a la
fusión del pull request.

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

## 13. Qué falta para cerrar

| Paso | Estado | Responsable |
| --- | --- | --- |
| Autorizar la publicación en GHCR | **Hecho** el 2026-09-19, de forma acotada | Usuario |
| Aprobar la tarea | **Hecho** el 2026-09-20 | Usuario |
| Versionar el código correspondiente de AGPL | **Hecho** por este cierre: repositorio público | — |
| **Fusionar el pull request `Task/027.1 → main`** | **Pendiente** | **Usuario, en exclusiva** |
| Decidir el orden de integración frente al PR `#47` | **Pendiente** | **Usuario** |
| Publicar SBOM y procedencia junto a la imagen antes de hacerla pública | **Pendiente** | **Usuario** |

Tras el cierre: `Task/027.1` **Aprobada**, con su pull request hacia `main` **abierto y sin
fusionar**; `Task/027` **Aprobada** con el PR `#47` **abierto y sin fusionar**; `Task/028`
**no iniciada**; el paquete de GHCR **privado**; y **R-018-3 ABIERTO** con 99 identidades.
