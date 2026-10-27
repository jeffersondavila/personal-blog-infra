# ---------------------------------------------------------------------------
# Destino: LABORATORIO AWS LOCAL — root de datos
#
# Sin secretos y versionable: solo nombres locales. Las credenciales y la
# contrasena master FICTICIA las aporta el lanzador (scripts/laboratorio), que
# tambien rellena los endpoints desde las variables LAB_ENDPOINT_* ya validadas
# y el ARN del bucket de medios desde las salidas de `terraform-medios`.
#
# Es el MISMO root y los MISMOS modulos que produccion. Solo cambian estos
# valores. Ningun resultado del laboratorio prueba aislamiento de red, TLS, KMS,
# backups ni PITR: todo eso es AWS-only (aws-local-parity.md §8.4).
# ---------------------------------------------------------------------------

region      = "us-east-1"
laboratorio = true

# Vacia: el emulador no implementa la validacion de cuenta.
cuentas_permitidas = []

prefijo = "blog-lab"

etiquetas = {
  Proyecto   = "personal-blog"
  Entorno    = "laboratorio"
  Gestion    = "terraform"
  Componente = "datos"
  Tarea      = "Task-031"
}

# Desde Floci 2.3.0 el emulador publica los ID de zona con el formato de AWS
# (`use1-az1`) y CreateSubnet rechaza el que publicaba 2.1.0 (`us-east-1-az1`).
# Es un valor del destino: el modulo y la validacion son los mismos.
subredes = {
  a = { cidr = "10.40.0.0/20", zona_id = "use1-az1" }
  b = { cidr = "10.40.16.0/20", zona_id = "use1-az2" }
}

# El laboratorio se reconstruye en cada ciclo: sin esto el destroy no podria
# demostrarse. Es un VALOR del destino, no un modulo distinto (R-26), y el root
# lo rechaza fuera del laboratorio.
proteccion_contra_borrado = false
omitir_snapshot_final     = true
