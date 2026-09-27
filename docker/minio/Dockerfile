# syntax=docker/dockerfile:1.19

# Task/027.1 creo este derivado para reconstruir /usr/bin/minio con
# amqp091-go v1.13.0. Task/028 (H-028-2) lo AMPLIA: reconstruye tambien
# /usr/bin/mc y sube google.golang.org/grpc a v1.83.2 en ambos, porque
# GO-2026-6443 (CVE-2026-84445) era alcanzable en los dos binarios segun
# govulncheck en modo binario.
#
# Es una IDENTIDAD DE RECIPE NUEVA, no un incremento: cambia el builder, cambian
# los dos binarios y cambia el numero de archivos sustituidos. Toda la
# procedencia se renueva en build-manifest.json.
#
# Nada se resuelve durante el build: fuentes por tag y commit verificados,
# dependencias congeladas en parches versionados y hasheados, toolchain fijada
# sin descarga automatica.

# ---------------------------------------------------------------------------
# Builder de /usr/bin/minio
# ---------------------------------------------------------------------------
FROM docker.io/library/golang:1.27.1-bookworm@sha256:69a7b9788769bec032d238959b61854e9ae87f57be9029ec04e9885fabf99195 AS builder-minio

ENV CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64 \
    GOTOOLCHAIN=local \
    SOURCE_DATE_EPOCH=1757261589

# La toolchain efectiva debe ser EXACTAMENTE la declarada. Con GOTOOLCHAIN=local
# Go no puede descargar otra, y esta asercion lo demuestra en el propio build.
RUN set -eux; \
    go version; \
    test "$(go env GOVERSION)" = "go1.27.1"; \
    test "$(go env GOTOOLCHAIN)" = "local"

WORKDIR /src

RUN git init . \
 && git remote add origin https://github.com/minio/minio.git \
 && git fetch --depth=1 origin refs/tags/RELEASE.2025-09-07T16-13-09Z:refs/tags/RELEASE.2025-09-07T16-13-09Z \
 && test "$(git rev-parse refs/tags/RELEASE.2025-09-07T16-13-09Z)" = "01ce918d8279a20e4706b96a64396146894adee4" \
 && test "$(git rev-parse refs/tags/RELEASE.2025-09-07T16-13-09Z^{})" = "07c3a429bfed433e49018cb0f78a52145d4bedeb" \
 && git checkout --detach 07c3a429bfed433e49018cb0f78a52145d4bedeb \
 && test "$(git archive --format=tar HEAD | sha256sum | cut -d' ' -f1)" = "3fd74f9e3123e8d112141b9764e583b263c711b9ce87661bfa3afda586f92091"

COPY minio-amqp091-go-1.13.0.patch /tmp/minio-amqp091-go-1.13.0.patch
COPY minio-deps-grpc-1.83.2.patch /tmp/minio-deps-grpc-1.83.2.patch

RUN set -eux; \
 test "$(sha256sum /tmp/minio-amqp091-go-1.13.0.patch | cut -d' ' -f1)" = "16b199bbdf3565d0a8455dad5cc6762d81e4f58be5210daf4221d8852f7a902c" \
 && test "$(sha256sum /tmp/minio-deps-grpc-1.83.2.patch | cut -d' ' -f1)" = "161867bbdcb1db4927e5416279ec5d1a5515fc95df5eaf5ce433e14e423f535d" \
 && git apply --check /tmp/minio-amqp091-go-1.13.0.patch \
 && git apply /tmp/minio-amqp091-go-1.13.0.patch \
 && git apply --check /tmp/minio-deps-grpc-1.83.2.patch \
 && git apply /tmp/minio-deps-grpc-1.83.2.patch \
 && test "$(git diff --name-only | sort | tr '\n' ' ')" = "go.mod go.sum " \
 && test "$(grep -c 'github.com/rabbitmq/amqp091-go v1.13.0' go.mod)" = "1" \
 && test "$(grep -c 'google.golang.org/grpc v1.83.2' go.mod)" = "1" \
 && go mod download \
 && go mod verify \
 && mkdir -p /out \
 && LDFLAGS="$(MINIO_RELEASE=RELEASE go run buildscripts/gen-ldflags.go)" \
 && go build -tags kqueue -trimpath --ldflags "$LDFLAGS" -o /out/minio . \
 && test "$(go version -m /out/minio | grep -c 'dep.*github.com/rabbitmq/amqp091-go.*v1.13.0')" = "1" \
 && test "$(go version -m /out/minio | grep -c 'dep.*github.com/rabbitmq/amqp091-go.*v1.10.0')" = "0" \
 && test "$(go version -m /out/minio | grep -c 'dep.*google.golang.org/grpc.*v1.83.2')" = "1"

# ---------------------------------------------------------------------------
# Builder de /usr/bin/mc
#
# La metadata de version sale del mecanismo REAL de upstream:
# `MC_RELEASE=RELEASE go run buildscripts/gen-ldflags.go`, que deriva ReleaseTag
# y CommitID del propio repositorio. No se inventa ninguna cadena.
# ---------------------------------------------------------------------------
FROM docker.io/library/golang:1.27.1-bookworm@sha256:69a7b9788769bec032d238959b61854e9ae87f57be9029ec04e9885fabf99195 AS builder-mc

ENV CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64 \
    GOTOOLCHAIN=local \
    SOURCE_DATE_EPOCH=1757261589

RUN set -eux; \
    go version; \
    test "$(go env GOVERSION)" = "go1.27.1"; \
    test "$(go env GOTOOLCHAIN)" = "local"

WORKDIR /src

RUN git init . \
 && git remote add origin https://github.com/minio/mc.git \
 && git fetch --depth=1 origin refs/tags/RELEASE.2025-08-13T08-35-41Z:refs/tags/RELEASE.2025-08-13T08-35-41Z \
 && test "$(git rev-parse refs/tags/RELEASE.2025-08-13T08-35-41Z)" = "d6541ea280b73a834b64d4097e21f2be77676104" \
 && test "$(git rev-parse refs/tags/RELEASE.2025-08-13T08-35-41Z^{})" = "7394ce0dd2a80935aded936b09fa12cbb3cb8096" \
 && git checkout --detach 7394ce0dd2a80935aded936b09fa12cbb3cb8096 \
 && test "$(git archive --format=tar HEAD | sha256sum | cut -d' ' -f1)" = "3a4e9b4b48ad0cd5ce87e6d0a2e67959e44e47f576a52c2837179ddff9e814e2"

COPY mc-deps-grpc-1.83.2.patch /tmp/mc-deps-grpc-1.83.2.patch

RUN set -eux; \
 test "$(sha256sum /tmp/mc-deps-grpc-1.83.2.patch | cut -d' ' -f1)" = "ff61358cc625873fad0ac0fceb0f6b17ec2d7aefad820fb27cc9d6bde1429d6e" \
 && git apply --check /tmp/mc-deps-grpc-1.83.2.patch \
 && git apply /tmp/mc-deps-grpc-1.83.2.patch \
 && test "$(git diff --name-only | sort | tr '\n' ' ')" = "go.mod go.sum " \
 && test "$(grep -c 'google.golang.org/grpc v1.83.2' go.mod)" = "1" \
 && go mod download \
 && go mod verify \
 && mkdir -p /out \
 && LDFLAGS="$(MC_RELEASE=RELEASE go run buildscripts/gen-ldflags.go)" \
 && go build -tags kqueue -trimpath --ldflags "$LDFLAGS" -o /out/mc . \
 && test "$(go version -m /out/mc | grep -c 'dep.*google.golang.org/grpc.*v1.83.2')" = "1" \
 && /out/mc --version \
 && test "$(/out/mc --version | head -1 | grep -c 'RELEASE.2025-08-13T08-35-41Z')" = "1" \
 && test "$(/out/mc --version | head -1 | grep -c '7394ce0dd2a8')" = "1"

# ---------------------------------------------------------------------------
# Runtime
#
# Misma base que el derivado anterior, por el MISMO digest. H-028-1: la
# ubicacion oficial de `minio/minio` dejo de estar publicamente accesible en las
# ubicaciones oficiales comprobadas, de modo que se sirve desde un espejo
# PRIVADO del proyecto que republico los bytes del manifiesto sin alterarlos y
# conserva por tanto el mismo digest. El origen historico queda en
# `runtime_base.upstream_index` de build-manifest.json.
#
# Se sustituyen EXACTAMENTE dos archivos. El verificador OCI lo exige y falla si
# aparece un tercero.
# ---------------------------------------------------------------------------
FROM ghcr.io/jeffersondavila/personal-blog-minio-base@sha256:a1a8bd4ac40ad7881a245bab97323e18f971e4d4cba2c2007ec1bedd21cbaba2
COPY --from=builder-minio --chown=0:0 --chmod=0755 /out/minio /usr/bin/minio
COPY --from=builder-mc --chown=0:0 --chmod=0755 /out/mc /usr/bin/mc
