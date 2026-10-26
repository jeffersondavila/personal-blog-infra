ARG TRAEFIK_IMAGE=traefik:v3.7.16@sha256:22a759fb803abb5c3a7ba5d5a55a201c5fb0fc8993d5c72c47a89075e64f1953
FROM ${TRAEFIK_IMAGE}
# v3.7.16 se compila con Go 1.26.10. Su base (Alpine 3.24.3) ya trae libcrypto3/libssl3 3.5.9-r0; el pin
# exacto se conserva como suelo para que una base mas antigua no lo pueda bajar.
RUN apk add --no-cache libcrypto3=3.5.9-r0 libssl3=3.5.9-r0
USER 65532:65532
