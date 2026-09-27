# MinIO Community derivado (Task/027.1, ampliado por Task/028)

Esta receta conserva el release `RELEASE.2025-09-07T16-13-09Z` y todo el runtime oficial
salvo **dos** archivos, que se recompilan desde las fuentes fijadas de upstream:

| Archivo sustituido | Fuente | Cambios de dependencia |
| --- | --- | --- |
| `/usr/bin/minio` | `minio/minio` `RELEASE.2025-09-07T16-13-09Z` | `amqp091-go` `v1.10.0` → `v1.13.0`; `grpc` `v1.72.0` → `v1.83.2` |
| `/usr/bin/mc` | `minio/mc` `RELEASE.2025-08-13T08-35-41Z` | `grpc` `v1.71.0` → `v1.83.2` |

`amqp091-go` elimina `CVE-2026-79921` (Task/027.1). La subida de `grpc` elimina
`CVE-2026-84445` / `GO-2026-6443`, que **govulncheck en modo binario demostró alcanzable en
los dos binarios**, no solo presente (Task/028, H-028-2).

**Task/028 no es un incremento de Task/027.1: es una identidad de recipe nueva.** Cambia el
constructor, cambian los dos binarios y cambia el número de archivos sustituidos. Toda la
procedencia se renueva en `build-manifest.json`, y la identidad anterior queda conservada
—no movida ni sobrescrita— en su sección `supersedes`.

## Qué clase de imagen es

No es una imagen propia ordinaria ni una imagen de tercero sin modificar: es un **derivado
reproducible de upstream**. Por eso conserva la política `accepted-baseline` limitada a la
clave `minio`, ligada a un manifiesto de construcción y a un atestado local verificado.

**Esto no crea una excepción genérica.** La tolerancia cero de `postgres`, `traefik` y
cualquier futura imagen propia se mantiene intacta: el comparador rechaza el atestado en
cualquier clave que no sea `minio`, y hay un control negativo que lo demuestra
(`tests/security/test_minio_derivative.py`).

## Qué nivel de reproducibilidad está demostrado

**Construcción reproducible con identidades fijadas y verificadas.** Esa es la afirmación
exacta, y no se hace ninguna mayor.

**La construcción NO es hermética ni offline.** Obtiene por red los árboles de fuentes y los
módulos de Go. Lo que está demostrado es que **cada entrada tiene identidad fijada y
comprobada dentro del propio build**, de modo que una sustitución silenciosa hace fallar la
construcción:

| Entrada | Cómo queda fijada |
| --- | --- |
| Imagen constructora | `golang:1.27.1-bookworm` por digest de manifiesto de plataforma |
| Toolchain efectiva | `GOTOOLCHAIN=local` más una aserción de que `go env GOVERSION` es `go1.27.1`: Go no puede descargar otra |
| Frontend de BuildKit | `docker/dockerfile:1.19` por digest |
| Tags de release | objetos de tag comprobados con `git rev-parse` en los dos repositorios |
| Commits | `07c3a429bfed…` (minio) y `7394ce0dd2a8…` (mc), comprobados |
| Árboles de fuentes | `git archive \| sha256sum` comparado con un valor fijo, uno por fuente |
| Parches | tres `sha256` comprobados antes de aplicarlos |
| Resolución de dependencias | **ninguna**: los parches congelan `go.mod` y `go.sum`, y el build no ejecuta `go get` ni `go mod tidy` |
| Módulos Go | `go mod download` seguido de `go mod verify` |
| Metadatos de versión | los `ldflags` salen del mecanismo real de upstream (`buildscripts/gen-ldflags.go`), no de cadenas inventadas |
| Resultado | `go version -m` exige `amqp091-go v1.13.0` presente, `v1.10.0` ausente y `grpc v1.83.2` presente; `mc --version` debe declarar su release y su commit corto |
| Base del runtime | `ghcr.io/jeffersondavila/personal-blog-minio-base` por digest de manifiesto de plataforma (ver H-028-1) |
| Marcas de tiempo | `SOURCE_DATE_EPOCH` fijo y `rewrite-timestamp` en el exportador OCI |

El verificador (`scripts/minio/artifact.py`) comprueba además que la imagen resultante
hereda **los 9 layers y diff IDs** de la base, que tiene **exactamente 11 layers**, que el
entrypoint, `cmd`, variables y etiquetas son los mismos, y que **cada uno de los dos layers
añadidos contiene solo su propio archivo declarado**, con modo `0755`, propietario `0:0` y el
`sha256` y el tamaño exactos. Un tercer archivo, un archivo que falte, un hash distinto o un
modo distinto hacen fallar la verificación; hay negativos para cada caso en
`tests/security/test_minio_oci_verifier.py`.

### Por qué la base viene de un espejo privado

`quay.io/minio/minio` y `docker.io/minio/minio` **dejaron de estar públicamente accesibles en
las ubicaciones oficiales comprobadas** (H-028-1). No se afirma nada sobre la intención de
upstream: solo lo observado. El proyecto republicó **los bytes del manifiesto sin alterarlos**
en un espejo **privado**, que por eso conserva el mismo digest
`sha256:a1a8bd4a…cbaba2`. El origen histórico queda declarado en
`runtime_base.upstream_index` de `build-manifest.json`.

## Identidad de publicación

Hay **dos** identidades y conviene no confundirlas. **El digest es la autoridad, no la
etiqueta.**

| | Task/027.1 | Task/028 (D-1) |
| --- | --- | --- |
| Digest del manifiesto | `sha256:84c67632…059129` | `sha256:247a1cd3…f80702` |
| Archivos sustituidos | `usr/bin/minio` | `usr/bin/minio`, `usr/bin/mc` |
| Layers | 10 | 11 |
| Constructor | `golang:1.24.6-bookworm` | `golang:1.27.1-bookworm` |
| Residual accionable aceptado | 99 | **10** |
| Estado en GHCR | **Publicado** el 2026-09-19 | **NO publicado** |

La identidad de Task/027.1 **se conserva tal cual**: no se mueve la etiqueta, no se
sobrescribe el manifiesto y no se borra el paquete. Su verificación remota quedó registrada
en `docs/task-reports/TASK-027.1-report.md`.

> **Brecha declarada, no resuelta.** `.env.example` sigue apuntando al digest
> `sha256:84c67632…059129`, que es el **único publicado**. El entorno local, por tanto, sigue
> ejecutando la identidad anterior. Publicar el derivado D-1 es una **acción externa que
> requiere autorización humana explícita**, igual que la de Task/027.1, y **no** se ha hecho
> en Task/028. Hasta entonces: `CI Infra` construye, verifica y escanea la identidad nueva
> desde la receta, y el baseline está ligado a ella; el entorno local no la usa.

## Visibilidad y distribución — leer antes de hacer público el paquete

**El paquete es PRIVADO.** Su visibilidad **no se ha modificado** y cambiarla no está
autorizado. Lo mismo vale para el espejo de la base.

Eso importa por la licencia: mientras el paquete sea privado no hay distribución pública de
la imagen.

**El código correspondiente sí está disponible** desde el cierre aprobado del 2026-09-20 y se
amplía con Task/028: este `Dockerfile`, los **tres** parches, `build-manifest.json`, este
README y `scripts/minio/artifact.py` están **versionados** en
`jeffersondavila/personal-blog-infra`, que es un repositorio **público**. Los commits upstream
exactos de las **dos** fuentes y todos los digests quedan declarados en el manifiesto de
construcción.

> **Condición de salida, todavía vigente.** El **SBOM** y la **procedencia** se generan en
> `CI Infra` pero **no se publican como artefactos junto a la imagen**. Conviene resolverlo
> antes de hacer público el paquete, para que la oferta de fuentes acompañe a la imagen y no
> dependa de reconstruirla.

## Licencia

MinIO Community y `mc` son **GNU AGPL-3.0**. La distribución de la imagen debe ofrecer el
código fuente correspondiente: commits upstream exactos de las dos fuentes, parches,
`Dockerfile`, manifiesto de construcción, SBOM y procedencia. Publicar solo los binarios o la
imagen sin esas fuentes **no** es un cierre conforme. Commits, parches, `Dockerfile` y
manifiesto **ya están publicados** en este repositorio público; **SBOM y procedencia todavía
no se publican junto a la imagen**: ver la sección anterior.
