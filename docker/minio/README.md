# MinIO Community derivado (Task/027.1)

Esta receta conserva el release `RELEASE.2025-09-07T16-13-09Z` y todo el runtime oficial
actual salvo `/usr/bin/minio`. El único cambio de dependencia es
`github.com/rabbitmq/amqp091-go` de `v1.10.0` a `v1.13.0`, que elimina `CVE-2026-79921`.

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

**La construcción NO es hermética ni offline.** Obtiene por red el árbol de fuentes de MinIO
y los módulos de Go. Lo que está demostrado es que **cada entrada tiene identidad fijada y
comprobada dentro del propio build**, de modo que una sustitución silenciosa hace fallar la
construcción:

| Entrada | Cómo queda fijada |
| --- | --- |
| Imagen constructora | `golang:1.24.6-bookworm` por digest de manifiesto de plataforma |
| Frontend de BuildKit | `docker/dockerfile:1.19` por digest |
| Tag del release | objeto de tag comprobado con `git rev-parse` |
| Commit del release | `07c3a429bfed433e49018cb0f78a52145d4bedeb`, comprobado |
| Árbol de fuentes | `git archive \| sha256sum` comparado con un valor fijo |
| Parche | `sha256` comprobado antes de aplicarlo |
| Módulos Go | `go mod download` seguido de `go mod verify` |
| Resultado | `go version -m` exige `v1.13.0` presente y `v1.10.0` ausente |
| Base del runtime | `quay.io/minio/minio` por digest de manifiesto de plataforma |
| Marcas de tiempo | `SOURCE_DATE_EPOCH` fijo y `rewrite-timestamp` en el exportador OCI |

El verificador (`scripts/minio/artifact.py`) comprueba además que la imagen resultante
hereda **los 9 layers y diff IDs** de la base, que tiene **exactamente 10 layers**, que el
entrypoint, `cmd`, variables y etiquetas son los mismos, y que el último layer contiene
**solo** `usr/bin/minio` con modo `0755` y propietario `0:0`.

## Identidad de publicación

`sha256:84c67632f7e85d4cd86ea5f7f6fbb6b5b8263ecd20f08153c4cd1a42e3059129` es el digest del
manifiesto OCI producido localmente **y** el **RepoDigest real** del paquete en
`ghcr.io/jeffersondavila/personal-blog-minio`.

**Publicado el 2026-09-19**, bajo autorización humana acotada. Se publicó **exactamente el
OCI ya validado, sin reconstruir**: mismo tar, `artifact.py verify` en verde antes de
empujarlo, y `Dockerfile`, parche, manifiesto y baseline sin tocar.

La correspondencia local ↔ remota se **verificó**, no se supuso:

- `docker buildx imagetools inspect` y `docker manifest inspect` devuelven ese mismo digest;
- el manifiesto se descargó **en crudo** (2289 bytes) y su `sha256` reproduce el digest;
- GHCR conservó `mediaType: application/vnd.oci.image.manifest.v1+json`, el `config`
  `sha256:25c832aa…` y los **10 layers** esperados;
- Trivy, escaneando la referencia **remota** tras borrar la copia local, registró el
  `RepoDigests` **de forma nativa desde el registro**, sin intervención del atestador;
- la referencia de `.env.example` **resuelve**, comprobado con un *pull* aislado que después
  se eliminó.

*(Antes de esa fecha esta sección decía que el digest no era un RepoDigest, que la imagen no
se había publicado y que la referencia no era resoluble. Era cierto entonces.)*

## Visibilidad y distribución — leer antes de hacer público el paquete

**El paquete es PRIVADO.** Su visibilidad **no se ha modificado** y cambiarla no está
autorizado.

Eso importa por la licencia: mientras el paquete sea privado no hay distribución pública de
la imagen.

**El código correspondiente sí está disponible** desde el cierre aprobado del 2026-09-20:
este `Dockerfile`, el parche, `build-manifest.json`, este README y
`scripts/minio/artifact.py` están **versionados** en `jeffersondavila/personal-blog-infra`,
que es un repositorio **público**. El commit upstream exacto y todos los digests quedan
declarados en el manifiesto de construcción.

> **Condición de salida, todavía vigente.** El **SBOM** y la **procedencia** se generan en
> `CI Infra` pero **no se publican como artefactos junto a la imagen**. Conviene resolverlo
> antes de hacer público el paquete, para que la oferta de fuentes acompañe a la imagen y no
> dependa de reconstruirla.

## Licencia

MinIO Community es **GNU AGPL-3.0**. La distribución de la imagen debe ofrecer el código
fuente correspondiente: commit upstream exacto, parche, `Dockerfile`, manifiesto de
construcción, SBOM y procedencia. Publicar solo el binario o la imagen sin esas fuentes
**no** es un cierre conforme. Commit, parche, `Dockerfile` y manifiesto **ya están
publicados** en este repositorio público; **SBOM y procedencia todavía no se publican junto
a la imagen**: ver la sección anterior.
