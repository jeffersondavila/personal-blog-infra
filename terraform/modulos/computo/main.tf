# ---------------------------------------------------------------------------
# Modulo: computo — funcion Lambda del backend
#
# Que crea y por que existe
#   La funcion que ejecuta el backend FastAPI. Es el destino de produccion del
#   codigo que en local corre bajo uvicorn: el MISMO codigo, envuelto por el
#   adaptador de Task/023 y empaquetado por Task/024.
#
# De que depende
#   Del rol de ejecucion, del grupo de logs y del artefacto ZIP. Depende de ella
#   la integracion de API Gateway.
#
# Por que package_type = Zip y no Image
#   ADR-003 excluye ECR de la arquitectura. El paquete de Task/024 mide 41,28 MiB
#   comprimidos, por debajo del limite de carga directa, asi que tampoco hace
#   falta un bucket de despliegue.
#
# Sobre el artefacto
#   `filename` recibe una RUTA EXPLICITA por variable. `source_code_hash` es lo
#   que hace que Terraform advierta un artefacto nuevo: sin el, un ZIP
#   reconstruido con el mismo nombre no producira ningun cambio en el plan y la
#   funcion seguiria ejecutando el codigo anterior.
#
#   El SHA concreto NO se fija aqui: el artefacto se reconstruye legitimamente
#   cuando cambian las fuentes del backend. Quien congela la identidad entre el
#   plan y el apply es scripts/laboratorio/artefacto.py.
#
# Diferencia conocida con AWS real
#   El emulador ejecuta la funcion en un contenedor Docker basado en la imagen
#   oficial del runtime. Eso da fidelidad al modelo de ejecucion, pero el
#   arranque en frio local NO es comparable con el de AWS: las mediciones de
#   latencia de aqui no sirven para dimensionar (D-12, Task/032).
# ---------------------------------------------------------------------------

resource "aws_lambda_function" "backend" {
  function_name = var.nombre
  role          = var.arn_del_rol

  package_type     = "Zip"
  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  handler       = var.handler
  runtime       = var.runtime
  architectures = [var.arquitectura]

  memory_size = var.memoria_mb
  timeout     = var.timeout_s

  # Las variables se fusionan en un unico mapa: las BLOG_* que la aplicacion lee
  # y las del SDK que el contenedor necesita para hablar con el destino. Con el
  # mapa vacio no se emite el bloque, que es el comportamiento correcto en AWS
  # real cuando la configuracion venga de otro sitio.
  dynamic "environment" {
    for_each = length(merge(var.variables_de_la_aplicacion, var.variables_del_sdk)) > 0 ? [1] : []

    content {
      variables = merge(var.variables_de_la_aplicacion, var.variables_del_sdk)
    }
  }

  # El grupo de logs debe existir ANTES que la funcion. Si no, Lambda lo crea al
  # primer arranque con retencion infinita y Terraform se encuentra despues un
  # recurso que ya existe.
  depends_on = [var.dependencia_del_grupo_de_logs]
}
