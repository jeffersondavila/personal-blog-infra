# syntax=docker/dockerfile:1.19

# Task/027.1 creo este derivado para reconstruir /usr/bin/minio con amqp091-go v1.13.0. Task/028 (H-028-2) lo amplio
# a /usr/bin/mc y subio google.golang.org/grpc a v1.83.2 en ambos binarios: GO-2026-6443 (CVE-2026-84445) era
# alcanzable en los dos segun govulncheck en modo binario.
#
# Task/031 (mantenimiento de CI, contrato v3) corrige dentro del derivado, sin cambiar la base:
# - pcre2 y pcre2-syntax 10.40-6.el9 -> 10.40-7.el9_8 (RPM de UBI 9 BaseOS, firma de Red Hat y SHA-256 fijados);
# - stdlib: toolchain Go 1.27.1 -> 1.27.3;
# - golang.org/x/net v0.59.0 -> v0.60.0 y github.com/klauspost/compress v1.18.0 -> v1.18.7 en minio y mc.
#
# Es una IDENTIDAD DE RECIPE NUEVA: cambian el builder, los dos binarios y aparece una capa de paquetes. Toda la
# procedencia se renueva en build-manifest.json, que conserva la identidad anterior en `supersedes`.
#
# Nada se resuelve durante el build: fuentes por tag y commit verificados, dependencias congeladas en parches
# versionados y hasheados, toolchain fijada sin descarga automatica y RPM por URL fija con SHA-256 y firma
# comprobados.
#
# La actualizacion RPM produce UNA capa declarada: exactamente el resultado de la transaccion `rpm -U`, medido antes y
# despues y fijado por hash. rpm 4.16 honra SOURCE_DATE_EPOCH de forma nativa: INSTALLTID = epoch e INSTALLTIME =
# epoch + orden del paquete en la transaccion, sin depender del reloj (demostrado con dos corridas a horas distintas).

# ---------------------------------------------------------------------------
# Base de ejecucion: la MISMA de los derivados anteriores, por el MISMO digest. Se sirve desde un espejo PRIVADO
# del proyecto que republico los bytes del manifiesto sin alterarlos (H-028-1); el origen historico queda en
# `runtime_base.upstream_index` de build-manifest.json.
# ---------------------------------------------------------------------------
FROM ghcr.io/jeffersondavila/personal-blog-minio-base@sha256:a1a8bd4ac40ad7881a245bab97323e18f971e4d4cba2c2007ec1bedd21cbaba2 AS base

# ---------------------------------------------------------------------------
# Builder de /usr/bin/minio
# ---------------------------------------------------------------------------
FROM docker.io/library/golang:1.27.3-bookworm@sha256:972b4110ba0f47539a975c31e52c64765e1ff19f2d74469ae4a595c6676e80a5 AS builder-minio

ENV CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64 \
    GOTOOLCHAIN=local \
    SOURCE_DATE_EPOCH=1757261589

RUN set -eux; \
    go version; \
    test "$(go env GOVERSION)" = "go1.27.3"; \
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
COPY minio-deps-xnet-0.60.0-compress-1.18.7.patch /tmp/minio-deps-xnet-0.60.0-compress-1.18.7.patch

RUN set -eux; \
 test "$(sha256sum /tmp/minio-amqp091-go-1.13.0.patch | cut -d' ' -f1)" = "16b199bbdf3565d0a8455dad5cc6762d81e4f58be5210daf4221d8852f7a902c" \
 && test "$(sha256sum /tmp/minio-deps-grpc-1.83.2.patch | cut -d' ' -f1)" = "161867bbdcb1db4927e5416279ec5d1a5515fc95df5eaf5ce433e14e423f535d" \
 && test "$(sha256sum /tmp/minio-deps-xnet-0.60.0-compress-1.18.7.patch | cut -d' ' -f1)" = "83851d30e0d85030d224df1fa584f2eb37d31c85571f8c2aa631dcc4861b0898" \
 && git apply --check /tmp/minio-amqp091-go-1.13.0.patch \
 && git apply /tmp/minio-amqp091-go-1.13.0.patch \
 && git apply --check /tmp/minio-deps-grpc-1.83.2.patch \
 && git apply /tmp/minio-deps-grpc-1.83.2.patch \
 && git apply --check /tmp/minio-deps-xnet-0.60.0-compress-1.18.7.patch \
 && git apply /tmp/minio-deps-xnet-0.60.0-compress-1.18.7.patch \
 && test "$(git diff --name-only | sort | tr '\n' ' ')" = "go.mod go.sum " \
 && test "$(grep -c 'github.com/rabbitmq/amqp091-go v1.13.0' go.mod)" = "1" \
 && test "$(grep -c 'google.golang.org/grpc v1.83.2' go.mod)" = "1" \
 && test "$(grep -c 'golang.org/x/net v0.60.0' go.mod)" = "1" \
 && test "$(grep -c 'github.com/klauspost/compress v1.18.7' go.mod)" = "1" \
 && go mod download \
 && go mod verify \
 && mkdir -p /out \
 && LDFLAGS="$(MINIO_RELEASE=RELEASE go run buildscripts/gen-ldflags.go)" \
 && go build -tags kqueue -trimpath --ldflags "$LDFLAGS" -o /out/minio . \
 && test "$(go version -m /out/minio | grep -c 'dep.*github.com/rabbitmq/amqp091-go.*v1.13.0')" = "1" \
 && test "$(go version -m /out/minio | grep -c 'dep.*github.com/rabbitmq/amqp091-go.*v1.10.0')" = "0" \
 && test "$(go version -m /out/minio | grep -c 'dep.*google.golang.org/grpc.*v1.83.2')" = "1" \
 && test "$(go version -m /out/minio | grep -c 'dep.*golang.org/x/net.*v0.60.0')" = "1" \
 && test "$(go version -m /out/minio | grep -c 'dep.*github.com/klauspost/compress.*v1.18.7')" = "1" \
 && test "$(go version -m /out/minio | head -1 | grep -c 'go1.27.3')" = "1"

# ---------------------------------------------------------------------------
# Builder de /usr/bin/mc
# ---------------------------------------------------------------------------
FROM docker.io/library/golang:1.27.3-bookworm@sha256:972b4110ba0f47539a975c31e52c64765e1ff19f2d74469ae4a595c6676e80a5 AS builder-mc

ENV CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64 \
    GOTOOLCHAIN=local \
    SOURCE_DATE_EPOCH=1757261589

RUN set -eux; \
    go version; \
    test "$(go env GOVERSION)" = "go1.27.3"; \
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
COPY mc-deps-xnet-0.60.0-compress-1.18.7.patch /tmp/mc-deps-xnet-0.60.0-compress-1.18.7.patch

RUN set -eux; \
 test "$(sha256sum /tmp/mc-deps-grpc-1.83.2.patch | cut -d' ' -f1)" = "ff61358cc625873fad0ac0fceb0f6b17ec2d7aefad820fb27cc9d6bde1429d6e" \
 && test "$(sha256sum /tmp/mc-deps-xnet-0.60.0-compress-1.18.7.patch | cut -d' ' -f1)" = "3e6df144c70ed31a43a97d2304abd9e28721bb3aac904f4cd2f4d85ae4aaaf2a" \
 && git apply --check /tmp/mc-deps-grpc-1.83.2.patch \
 && git apply /tmp/mc-deps-grpc-1.83.2.patch \
 && git apply --check /tmp/mc-deps-xnet-0.60.0-compress-1.18.7.patch \
 && git apply /tmp/mc-deps-xnet-0.60.0-compress-1.18.7.patch \
 && test "$(git diff --name-only | sort | tr '\n' ' ')" = "go.mod go.sum " \
 && test "$(grep -c 'google.golang.org/grpc v1.83.2' go.mod)" = "1" \
 && test "$(grep -c 'golang.org/x/net v0.60.0' go.mod)" = "1" \
 && test "$(grep -c 'github.com/klauspost/compress v1.18.7' go.mod)" = "1" \
 && go mod download \
 && go mod verify \
 && mkdir -p /out \
 && LDFLAGS="$(MC_RELEASE=RELEASE go run buildscripts/gen-ldflags.go)" \
 && go build -tags kqueue -trimpath --ldflags "$LDFLAGS" -o /out/mc . \
 && test "$(go version -m /out/mc | grep -c 'dep.*google.golang.org/grpc.*v1.83.2')" = "1" \
 && test "$(go version -m /out/mc | grep -c 'dep.*golang.org/x/net.*v0.60.0')" = "1" \
 && test "$(go version -m /out/mc | grep -c 'dep.*github.com/klauspost/compress.*v1.18.7')" = "1" \
 && test "$(go version -m /out/mc | head -1 | grep -c 'go1.27.3')" = "1" \
 && /out/mc --version \
 && test "$(/out/mc --version | head -1 | grep -c 'RELEASE.2025-08-13T08-35-41Z')" = "1" \
 && test "$(/out/mc --version | head -1 | grep -c '7394ce0dd2a8')" = "1"

# ---------------------------------------------------------------------------
# Actualizacion RPM de la base, fuera de la imagen final.
#
# Los RPM se descargan por URL fija y se verifican DOS veces: SHA-256 fijado (identidad) y firma de Red Hat (origen:
# release key 2, del keyring del builder fijado por digest). La transaccion se mide antes y despues; la diferencia debe
# ser EXACTAMENTE la declarada, fijada por hash. Si cambia cualquier archivo no previsto, no hay build.
# ---------------------------------------------------------------------------
FROM registry.access.redhat.com/ubi9/ubi@sha256:217dd5692d369799d34d09ffb6f5f3404efebc7900834490fdf9ae92fd6721d4 AS paquetes

ENV SOURCE_DATE_EPOCH=1757261589 \
    TZ=UTC

COPY medir_arbol.py /usr/local/libexec/medir_arbol.py

RUN set -eux; \
 test "$(sha256sum /usr/local/libexec/medir_arbol.py | cut -d' ' -f1)" = "637b2d6701215d660dd6cda42a385966f6d7d0e95c81e2fef4907caa2c70afbd"; \
 mkdir -p /tmp/rpms; \
 cd /tmp/rpms; \
 curl -fsSL --proto '=https' --tlsv1.2 -o pcre2.rpm https://cdn-ubi.redhat.com/content/public/ubi/dist/ubi9/9/x86_64/baseos/os/Packages/p/pcre2-10.40-7.el9_8.x86_64.rpm; \
 curl -fsSL --proto '=https' --tlsv1.2 -o pcre2-syntax.rpm https://cdn-ubi.redhat.com/content/public/ubi/dist/ubi9/9/x86_64/baseos/os/Packages/p/pcre2-syntax-10.40-7.el9_8.noarch.rpm; \
 printf '%s  %s\n' \
   ef2c65a463e1ef1bfbf3d9ee66986e14cca0fbae88343f099dd5b16619276f1f pcre2.rpm \
   e7466a43ef2bfda2b1dc07e855b0db743d48b11c0bdc1402e1d2ea6fb23d33a3 pcre2-syntax.rpm \
   | sha256sum -c -; \
 rpm -K pcre2.rpm pcre2-syntax.rpm; \
 test "$(rpm -K pcre2.rpm pcre2-syntax.rpm | grep -c ': digests signatures OK$')" = "2"

RUN --mount=type=bind,from=base,target=/base \
 set -eux; \
 mkdir /target /salida; \
 cp -a /base/. /target/; \
 python3 /usr/local/libexec/medir_arbol.py medir /target /salida/antes.txt; \
 test "$(rpm --root /target -q pcre2 pcre2-syntax | tr '\n' ' ')" = "pcre2-10.40-6.el9.x86_64 pcre2-syntax-10.40-6.el9.noarch "; \
 test "$SOURCE_DATE_EPOCH" = "1757261589"; \
 rpm --root /target -Uvh --noscripts --excludedocs /tmp/rpms/pcre2-syntax.rpm /tmp/rpms/pcre2.rpm; \
 test "$(rpm --root /target -q pcre2 pcre2-syntax | tr '\n' ' ')" = "pcre2-10.40-7.el9_8.x86_64 pcre2-syntax-10.40-7.el9_8.noarch "; \
 test "$(rpm --root /target -q --qf '%{NAME}=%{INSTALLTIME}/%{INSTALLTID} ' pcre2 pcre2-syntax)" = "pcre2=1757261590/1757261589 pcre2-syntax=1757261589/1757261589 "; \
 python3 /usr/local/libexec/medir_arbol.py medir /target /salida/despues.txt; \
 python3 /usr/local/libexec/medir_arbol.py delta /salida/antes.txt /salida/despues.txt /salida/delta.txt; \
 cat /salida/delta.txt; \
 test "$(sha256sum /salida/delta.txt | cut -d' ' -f1)" = "269386761c1514a1a954c30a1b75e44b9e74055b1c0410995d408e2e290fbf37"

# ---------------------------------------------------------------------------
# Runtime: base + UNA capa de paquetes + los dos binarios. El verificador OCI exige las 9 capas heredadas, la capa
# de paquetes con EXACTAMENTE sus miembros declarados y una capa por binario con solo su archivo.
# ---------------------------------------------------------------------------
FROM base
# Capa de paquetes: EXACTAMENTE la delta medida y fijada en la etapa `paquetes`. Las bibliotecas se reemplazan con
# --remove-destination (inodo nuevo): `cp` enlaza libpcre2 a traves de libselinux y no debe sobrescribir en sitio una
# biblioteca que tiene mapeada. Sin red, y montada sobre /mnt, que existe vacio en la base: no deja mount stubs.
RUN --network=none --mount=type=bind,from=paquetes,source=/target,target=/mnt \
 set -eux; \
 rm /usr/lib/.build-id/48/1282542036ac05da5dbbe987bb1feae7f7eb4a; \
 rm /usr/lib/.build-id/76/2e199f8f08725f767cb3c3167faae14327659f; \
 rmdir /usr/lib/.build-id/76; \
 cp -a /mnt/usr/lib/.build-id/2d /usr/lib/.build-id/2d; \
 cp -a /mnt/usr/lib/.build-id/6a /usr/lib/.build-id/6a; \
 cp -a --remove-destination /mnt/usr/lib64/libpcre2-8.so.0.11.0 /usr/lib64/libpcre2-8.so.0.11.0; \
 cp -a --remove-destination /mnt/usr/lib64/libpcre2-posix.so.3.0.2 /usr/lib64/libpcre2-posix.so.3.0.2; \
 cp -a --remove-destination /mnt/var/lib/rpm/rpmdb.sqlite /var/lib/rpm/rpmdb.sqlite
COPY --from=builder-minio --chown=0:0 --chmod=0755 /out/minio /usr/bin/minio
COPY --from=builder-mc --chown=0:0 --chmod=0755 /out/mc /usr/bin/mc
