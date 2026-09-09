# Misma serie PostgreSQL 17. El runtime arranca directamente como postgres.
ARG POSTGRES_IMAGE=postgres:17.11-alpine@sha256:18cfe3ef5e6815560c98237d6216d1e5119702fb0f3894c8785dd58b8bbe5d73
FROM ${POSTGRES_IMAGE}
# Parches exactos del repositorio oficial de la MISMA rama Alpine.
RUN apk add --no-cache libcrypto3=3.5.8-r0 libssl3=3.5.8-r0 libuuid=2.42.3-r1 \
    && rm /usr/local/bin/gosu \
    && mkdir -p /backup && chown postgres:postgres /backup
# /backup es el area de intercambio del runbook de respaldo. Se crea AQUI y no
# solo en el Compose porque un volumen nombrado nuevo hereda contenido y
# propietario del directorio de la imagen: creado sobre la marcha por Docker
# naceria como root y el proceso, que ya no lo es, no podria escribir en el.
USER postgres
