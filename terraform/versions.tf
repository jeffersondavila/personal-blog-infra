# ---------------------------------------------------------------------------
# personal-blog-infra — Terraform: versiones exigidas (Task/025)
#
# Constraints EXACTAS, no rangos. Una CLI o un provider distintos pueden leer el
# mismo .tf y producir otro plan: la version con la que se valido la
# infraestructura es parte de la infraestructura.
#
# Identidad verificada el 2026-09-13 contra las sumas oficiales de HashiCorp; el
# archivo SHA256SUMS de Terraform lleva firma GPG valida de HashiCorp Security.
# Los valores viven tambien en scripts/laboratorio/herramientas.py, y hay una
# prueba que exige que no discrepen.
#
# Aqui NO hay bloque `backend`: el tipo de backend no se puede cambiar con
# -backend-config, asi que lo genera el lanzador justo antes de `init`
# (docs/architecture/open-decisions.md, D-06). El grafo de recursos es uno solo.
# ---------------------------------------------------------------------------

terraform {
  required_version = "= 1.16.2"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.64.0"
    }
  }
}
