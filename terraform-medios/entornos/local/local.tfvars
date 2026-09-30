# ---------------------------------------------------------------------------
# Destino: LABORATORIO AWS LOCAL — root de medios
#
# Sin secretos y versionable: solo nombres locales y valores ficticios. Las
# credenciales las aporta el entorno que construye scripts/laboratorio.
#
# Los endpoints NO se escriben aqui: los rellena el lanzador desde las variables
# LAB_ENDPOINT_*, ya validadas una a una. Fijarlos aqui haria que cambiar un
# puerto publicado dejara a Terraform hablando con un destino equivocado.
#
# Es el MISMO root y el MISMO modulo que produccion. Lo unico que cambia son
# estos valores.
# ---------------------------------------------------------------------------

region      = "us-east-1"
laboratorio = true

# Vacia: el emulador no implementa la validacion de cuenta y su identidad es
# ficticia. Contra AWS real se declara la cuenta verificada.
cuentas_permitidas = []

nombre_del_bucket = "blog-lab-medios"

etiquetas = {
  Proyecto   = "personal-blog"
  Entorno    = "laboratorio"
  Gestion    = "terraform"
  Componente = "medios"
  Tarea      = "Task-025"
}

# Origen del entorno local del blog: Traefik publica sitio y API en 8081
# (.env.example, TRAEFIK_HTTP_HOST_PORT). Nunca el comodin.
#
# El laboratorio conserva un origen para poder EJERCER la creacion del recurso
# CORS: con la lista vacia el modulo no lo crea y el ciclo no podria demostrar
# esa rama. Produccion usa la lista vacia, que es la decision de D-08.
origenes_cors = ["http://localhost:8081"]

dias_para_expirar_versiones = 30

# El laboratorio se reconstruye en cada ciclo y el bucket lleva objetos de prueba.
forzar_destruccion = true
