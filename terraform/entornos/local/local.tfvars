# ---------------------------------------------------------------------------
# Destino: LABORATORIO AWS LOCAL (Task/025)
#
# Este archivo NO contiene ningun secreto y puede versionarse: todo lo que hay
# aqui son nombres locales y valores ficticios. Las credenciales no estan en
# ningun tfvars: las aporta el entorno que construye scripts/laboratorio.
#
# Los endpoints NO se escriben aqui. Los rellena el lanzador desde las variables
# LAB_ENDPOINT_*, despues de validarlas una a una: si estuvieran fijados en el
# archivo, cambiar el puerto publicado obligaria a editarlo y un olvido dejaria
# a Terraform hablando con un destino equivocado.
# ---------------------------------------------------------------------------

region      = "us-east-1"
laboratorio = true
prefijo     = "blog-lab"

etiquetas = {
  Proyecto = "personal-blog"
  Entorno  = "laboratorio"
  Gestion  = "terraform"
  Tarea    = "Task-025"
}

# --- S3 --------------------------------------------------------------------

bucket_de_medios = "blog-lab-medios"

# Origen del entorno local del blog: Traefik publica sitio y API en 8081
# (.env.example, TRAEFIK_HTTP_HOST_PORT). Nunca el comodin.
origenes_cors = ["http://localhost:8081"]

dias_para_expirar_versiones = 30

# --- Lambda ----------------------------------------------------------------
#
# VALORES DE LABORATORIO. No son dimensionamiento: el arranque en frio local no
# es comparable con el de AWS. Los limites reales son D-12, en Task/032.

lambda_memoria_mb = 512
lambda_timeout_s  = 30

# `lambda_zip_path` NO se fija aqui: se pasa con -var desde el lanzador, que
# recibe la ruta explicita con --lambda-zip. Fijarla aqui acoplaria este
# repositorio a la ubicacion del repositorio del backend.

# Variables BLOG_* del proceso. Todas ficticias y de laboratorio.
#
# BLOG_DATABASE_URL apunta a un destino que no existe: /health no consulta la
# base de datos (app/api/health.py) y es el unico endpoint del smoke. /ready si
# la consultaria, y por eso NO forma parte del camino critico de esta tarea.
variables_de_la_aplicacion = {
  BLOG_APP_ENV              = "local"
  BLOG_LOG_LEVEL            = "INFO"
  BLOG_LOG_FORMAT           = "json"
  BLOG_DATABASE_URL         = "postgresql://blog_lab:blog_lab@127.0.0.1:5432/blog_lab"
  BLOG_STORAGE_PROVIDER     = "s3"
  BLOG_STORAGE_BUCKET       = "blog-lab-medios"
  BLOG_STORAGE_REGION       = "us-east-1"
  BLOG_PUBLIC_SITE_BASE_URL = "http://localhost:8081"
  BLOG_AUTH_COOKIE_SECURE   = "false"
}

# --- CloudWatch Logs -------------------------------------------------------
#
# Valor de laboratorio. La retencion exacta de produccion es D-11, en Task/031.

dias_de_retencion_de_logs = 7

# --- SSM -------------------------------------------------------------------
#
# NOMBRES PROPUESTOS, no nombres productivos aprobados.
#
# El emulador conserva el tipo SecureString pero NO cifra en reposo: el valor de
# database_url es deliberadamente ficticio y no sirve para conectarse a nada.
# Ningun secreto real entra aqui (control S-07).

parametros = {
  "local/database_url" = {
    valor  = "postgresql://blog_lab:blog_lab@127.0.0.1:5432/blog_lab"
    seguro = true
  }
  "local/storage_bucket" = {
    valor = "blog-lab-medios"
  }
  "local/storage_region" = {
    valor = "us-east-1"
  }
  "local/public_site_base_url" = {
    valor = "http://localhost:8081"
  }
}

# --- API Gateway -----------------------------------------------------------
#
# SOLO LABORATORIO. El stage y el base path de produccion son de Task/033.

nombre_del_stage = "$default"
