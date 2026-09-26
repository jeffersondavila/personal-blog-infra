# syntax=docker/dockerfile:1.19

# Task/027.1: reconstruccion minima y reproducible del binario de MinIO.
# Cada identidad esta fijada aqui y se comprueba otra vez en build-manifest.json.
FROM docker.io/library/golang:1.24.6-bookworm@sha256:4f8589362626cfa081fdab2b474cda87c3b51d74b1e227c110d2ffde56daad5c AS builder

ENV CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64 \
    SOURCE_DATE_EPOCH=1757261589

WORKDIR /src

RUN git init . \
 && git remote add origin https://github.com/minio/minio.git \
 && git fetch --depth=1 origin refs/tags/RELEASE.2025-09-07T16-13-09Z:refs/tags/RELEASE.2025-09-07T16-13-09Z \
 && test "$(git rev-parse refs/tags/RELEASE.2025-09-07T16-13-09Z)" = "01ce918d8279a20e4706b96a64396146894adee4" \
 && test "$(git rev-parse refs/tags/RELEASE.2025-09-07T16-13-09Z^{})" = "07c3a429bfed433e49018cb0f78a52145d4bedeb" \
 && git checkout --detach 07c3a429bfed433e49018cb0f78a52145d4bedeb \
 && test "$(git archive --format=tar HEAD | sha256sum | cut -d' ' -f1)" = "3fd74f9e3123e8d112141b9764e583b263c711b9ce87661bfa3afda586f92091"

COPY minio-amqp091-go-1.13.0.patch /tmp/minio-amqp091-go-1.13.0.patch

RUN set -eux; \
 test "$(sha256sum /tmp/minio-amqp091-go-1.13.0.patch | cut -d' ' -f1)" = "16b199bbdf3565d0a8455dad5cc6762d81e4f58be5210daf4221d8852f7a902c" \
 && git apply --check /tmp/minio-amqp091-go-1.13.0.patch \
 && git apply /tmp/minio-amqp091-go-1.13.0.patch \
 && test "$(git diff --name-only | sort | tr '\n' ' ')" = "go.mod go.sum " \
 && test "$(grep -c 'github.com/rabbitmq/amqp091-go v1.13.0' go.mod)" = "1" \
 && go mod download \
 && go mod verify \
 && mkdir -p /out \
 && LDFLAGS="$(MINIO_RELEASE=RELEASE go run buildscripts/gen-ldflags.go)" \
 && go build -tags kqueue -trimpath --ldflags "$LDFLAGS" -o /out/minio . \
 && test "$(go version -m /out/minio | grep -c 'dep.*github.com/rabbitmq/amqp091-go.*v1.13.0')" = "1" \
 && test "$(go version -m /out/minio | grep -c 'dep.*github.com/rabbitmq/amqp091-go.*v1.10.0')" = "0"

# Es exactamente el manifest linux/amd64 de la imagen vigente. El unico layer
# nuevo sustituye /usr/bin/minio; mc, entrypoint, OS, config y permisos quedan
# heredados byte a byte y el verificador OCI lo exige.
#
# H-028-1 (2026-09-26): `minio/minio` dejo de estar publicamente accesible en sus
# ubicaciones oficiales comprobadas —exige autenticacion en quay.io, no existe en
# Docker Hub— y el digest dejo de ser recuperable anonimamente. La referencia apunta ahora a un espejo PRIVADO en el
# GHCR del proyecto que conserva **el mismo digest**: los bytes del manifiesto se
# republicaron sin alterarlos, de modo que el pin sigue siendo identico y la
# identidad verificada por Task/027.1 se mantiene, no se sustituye. Solo cambia
# el registry/repository. El origen historico queda en `runtime_base.upstream_index`.
FROM ghcr.io/jeffersondavila/personal-blog-minio-base@sha256:a1a8bd4ac40ad7881a245bab97323e18f971e4d4cba2c2007ec1bedd21cbaba2
COPY --from=builder --chown=0:0 --chmod=0755 /out/minio /usr/bin/minio
