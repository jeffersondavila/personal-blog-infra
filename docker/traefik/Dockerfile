ARG TRAEFIK_IMAGE=traefik:v3.7.13@sha256:f86a2cab1b5c649070c49f883c743dd32d8485a56e3368c5f93b9e91f1e91259
FROM ${TRAEFIK_IMAGE}
# v3.7.13 corrige las dependencias Go; la base aun necesita este parche Alpine.
RUN apk add --no-cache libcrypto3=3.5.8-r0 libssl3=3.5.8-r0
USER 65532:65532
