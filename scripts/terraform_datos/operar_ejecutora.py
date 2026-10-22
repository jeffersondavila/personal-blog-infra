"""Operador de la ejecutora privada de D-24 (Task/031 H-031-6 y H-031-7).

Mecanismo de credenciales de H-031-6 (Propuesta - pendiente de aprobacion)
-------------------------------------------------------------------------
- La custodia UNICA de cada credencial SQL es su SecureString de SSM (D-23). La ejecutora no lee SSM ni KMS: no tiene
  ruta (D-22, sin NAT y sin interface endpoint de pago) ni permiso.
- Este proceso, con la identidad operativa autorizada (`PersonalBlogAdministrator`, H-031-IAM), lee en memoria solo
  lo que el modo necesita y lo entrega en el evento de UNA invocacion SINCRONA. La funcion lo usa y lo descarta: nada
  queda en su configuracion, en el ZIP, en el plan, en el state ni en un log.
- `identidades` recibe verificadores SCRAM-SHA-256 calculados aqui: la contrasena de `blog_migrate` y `blog_app`
  nunca viaja.

Nada toca el disco ni la linea de ordenes. La salida es la respuesta saneada de la ejecutora; si contuviera un
secreto, el host o la cuenta, se aborta sin imprimirla. Cualquier error sale como codigo cerrado y sin mensaje: los
de AWS pueden llevar ARN con la cuenta.

Uso, desde la raiz del repositorio, con las dependencias de `requirements-operador.txt` y `aws login`:
  python -m scripts.terraform_datos.operar_ejecutora selfcheck
  python -m scripts.terraform_datos.operar_ejecutora verify --usuario blogadmin [--controles-negativos]
         [--restaurada blog-prod-restore-h0317-AAAAMMDDhhmmss] [--marcador UUID]
  python -m scripts.terraform_datos.operar_ejecutora identidades
  python -m scripts.terraform_datos.operar_ejecutora sintetico --accion sembrar --marcador UUID
         --instante AAAA-MM-DDThh:mm:ssZ
  python -m scripts.terraform_datos.operar_ejecutora export --bucket NOMBRE --marca AAAAMMDDThhmmssZ
"""
import argparse
import json
import re

from scripts.terraform_datos import scram

PREFIJO = "blog-prod"
FUNCION = f"{PREFIJO}-ejecutor"
INSTANCIA = f"{PREFIJO}-postgres"
RUTA = f"/{PREFIJO}/datos"
BASE = "personal_blog"
PERFIL = "personal-blog"
_IDENTIDAD = re.compile(r"arn:aws:sts::[0-9]{12}:assumed-role/PersonalBlogAdministrator/[^/]+")
_RESTAURADA = re.compile(r"blog-prod-restore-h0317-[0-9]{14}")


class Abortar(Exception):
    """Fin controlado: solo un estado cerrado sale por la salida estandar."""

    def __init__(self, estado):
        super().__init__(estado)
        self.estado = estado


def _clientes():
    import boto3  # diferido: las pruebas sustituyen los clientes
    from botocore.config import Config

    sesion = boto3.Session(profile_name=PERFIL, region_name="us-east-2")
    clientes = {nombre: sesion.client(nombre) for nombre in ("sts", "ssm")}
    # H-031-7 comparte este cliente para restore/delete: una respuesta perdida nunca autoriza repetir la mutacion.
    clientes["rds"] = sesion.client("rds", config=Config(retries={"total_max_attempts": 1, "mode": "standard"}))
    # D-24 modificada el 2026-10-18 (aprobada el 2026-10-19): con concurrencia no reservada, un error de red no debe convertirse en
    # una SEGUNDA ejecucion. Sin reintentos, y con un tiempo de lectura que cubre el timeout de la funcion (30 s).
    clientes["lambda"] = sesion.client("lambda", config=Config(retries={"total_max_attempts": 1, "mode": "standard"},
                                                               read_timeout=70))
    return clientes


def _argumentos(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    modos = parser.add_subparsers(dest="modo", required=True)
    modos.add_parser("selfcheck")
    verify = modos.add_parser("verify")
    verify.add_argument("--usuario", required=True, choices=("blogadmin", "blog_migrate", "blog_app"))
    verify.add_argument("--controles-negativos", action="store_true")
    verify.add_argument("--restaurada")
    verify.add_argument("--marcador")
    modos.add_parser("identidades")
    sintetico = modos.add_parser("sintetico")
    sintetico.add_argument("--accion", required=True, choices=("sembrar", "limpiar"))
    sintetico.add_argument("--marcador", required=True)
    sintetico.add_argument("--instante", required=True)
    export = modos.add_parser("export")
    export.add_argument("--bucket", required=True)
    export.add_argument("--marca", required=True)
    args = parser.parse_args(argv)
    if getattr(args, "restaurada", None) and not _RESTAURADA.fullmatch(args.restaurada):
        raise Abortar("ARGUMENTOS_NO_ADMITIDOS")
    return args


def _comprobar_identidad(sts, secretos):
    identidad = sts.get_caller_identity()
    secretos.append(identidad["Account"])
    if not _IDENTIDAD.fullmatch(identidad["Arn"]):
        raise Abortar("IDENTIDAD_NO_AUTORIZADA")


def _leer(ssm, usuario, secretos):
    valor = ssm.get_parameter(Name=f"{RUTA}/{usuario}", WithDecryption=True)["Parameter"]["Value"]
    secretos.append(valor)
    return valor


def _destino(rds, identificador, secretos):
    instancia = rds.describe_db_instances(DBInstanceIdentifier=identificador)["DBInstances"][0]
    if instancia["DBInstanceStatus"] != "available":
        raise Abortar("INSTANCIA_NO_DISPONIBLE")
    host = instancia["Endpoint"]["Address"]
    secretos.append(host)
    return {"host": host, "base": BASE}


def _evento(args, clientes, secretos):
    if args.modo == "selfcheck":
        return {"modo": "selfcheck"}
    ssm, rds = clientes["ssm"], clientes["rds"]
    if args.modo == "verify":
        evento = {"modo": "verify", "destino": _destino(rds, args.restaurada or INSTANCIA, secretos),
                  "credencial": {"usuario": args.usuario, "contrasena": _leer(ssm, args.usuario, secretos)}}
        if args.controles_negativos:
            evento["controles_negativos"] = True
        if args.marcador:
            evento["marcador"] = {"id": args.marcador}
        return evento
    destino = _destino(rds, INSTANCIA, secretos)
    if args.modo == "identidades":
        verificadores = {}
        for rol in ("blog_migrate", "blog_app"):
            verificadores[rol] = scram.verificador(_leer(ssm, rol, secretos))
            secretos.append(verificadores[rol])
        return {"modo": "identidades", "destino": destino,
                "credencial": {"usuario": "blogadmin", "contrasena": _leer(ssm, "blogadmin", secretos)},
                "verificadores": verificadores}
    credencial = {"usuario": "blog_migrate", "contrasena": _leer(ssm, "blog_migrate", secretos)}
    if args.modo == "sintetico":
        return {"modo": "sintetico", "destino": destino, "credencial": credencial,
                "marcador": {"id": args.marcador, "instante": args.instante}, "accion": args.accion}
    return {"modo": "export", "destino": destino, "credencial": credencial,
            "salida": {"bucket": args.bucket, "marca": args.marca}}


def _invocar(cliente, evento):
    respuesta = cliente.invoke(FunctionName=FUNCION, InvocationType="RequestResponse", LogType="None",
                               Payload=json.dumps(evento).encode("utf-8"))
    if respuesta.get("StatusCode") != 200 or respuesta.get("FunctionError"):
        raise Abortar("INVOCACION_FALLIDA")
    return json.loads(respuesta["Payload"].read())


def invocar_modo(argv, conexiones):
    """La respuesta saneada de la ejecutora para `argv`, o `Abortar` con un codigo cerrado.

    API para otros orquestadores (el restore de H-031-7): mismas guardas que la linea de ordenes.
    """
    secretos = []
    args = _argumentos(argv)
    _comprobar_identidad(conexiones["sts"], secretos)
    respuesta = _invocar(conexiones["lambda"], _evento(args, conexiones, secretos))
    if any(secreto in json.dumps(respuesta, ensure_ascii=False) for secreto in secretos):
        raise Abortar("RESPUESTA_CON_SECRETO")
    return respuesta


def main(argv=None, clientes=_clientes):
    try:
        respuesta = invocar_modo(argv, clientes())
        print(json.dumps(respuesta, sort_keys=True, ensure_ascii=False))
        return 0 if respuesta.get("estado") == "OK" else 1
    except Abortar as fin:
        print(json.dumps({"estado": fin.estado}))
        return 1
    except Exception as error:
        print(json.dumps({"estado": "ERROR_DEL_OPERADOR", "tipo": type(error).__name__}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
