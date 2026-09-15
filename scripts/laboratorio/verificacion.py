#!/usr/bin/env python3
"""Comprobaciones funcionales y de ausencia contra el destino del laboratorio.

Por que existe
--------------
`terraform apply` devolviendo 0 dice que el provider acepto las llamadas, no que
el sistema funcione. Este modulo pregunta a las APIs del destino: crea un objeto
y lo vuelve a leer, invoca la funcion a traves de la API real, recupera un evento
de log. Y despues del `destroy` pregunta lo contrario: que ya no este.

Todas las llamadas son AWS estandar firmadas con SigV4 (`firma_aws.py`). Ninguna
usa una API propia del emulador, que es la regla de portabilidad de
`aws-local-parity.md` seccion 4.2: el dia que estas comprobaciones se ejecuten
contra AWS real, el codigo es el mismo.

Las respuestas se interpretan con cuidado deliberado: un 404 al pedir un recurso
es la evidencia de que **no existe**, y un 200 al pedirlo despues de destruirlo es
un fallo. Por eso `ClienteAws.llamar` devuelve el estado en lugar de lanzar.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from typing import Any

from .firma_aws import ClienteAws

#: Version del API de Lambda en su ruta REST.
RUTA_DE_LAMBDA = "/2015-03-31/functions"


class ErrorDeVerificacion(RuntimeError):
    """Una comprobacion funcional no dio el resultado que se esperaba."""


def cliente(destino, servicio: str, *, clave: str, secreto: str) -> ClienteAws:
    """Cliente apuntado al endpoint YA VALIDADO de ese servicio."""
    return ClienteAws(
        endpoint=destino.endpoints[servicio],
        region=destino.region,
        clave_de_acceso=clave,
        clave_secreta=secreto,
    )


# --- Identidad --------------------------------------------------------------


def cuenta_observada(destino, *, clave: str, secreto: str) -> str:
    """`sts:GetCallerIdentity` contra el endpoint local explicito.

    Es la guarda G-03: la identidad se comprueba preguntando. Se usa el protocolo
    `query` de STS, que es el real; la respuesta es XML.
    """
    sts = cliente(destino, "sts", clave=clave, secreto=secreto)
    estado, datos = sts.llamar(
        servicio="sts",
        metodo="POST",
        ruta="/",
        cuerpo=b"Action=GetCallerIdentity&Version=2011-06-15",
        cabeceras={"content-type": "application/x-www-form-urlencoded"},
    )
    if estado != 200:
        raise ErrorDeVerificacion(
            f"STS respondio {estado}; no se pudo demostrar la identidad del destino"
        )
    encontrado = re.search(rb"<Account>([^<]*)</Account>", datos)
    if not encontrado:
        raise ErrorDeVerificacion("la respuesta de STS no contiene ninguna cuenta")
    return encontrado.group(1).decode("ascii")


# --- S3 ---------------------------------------------------------------------


def ejercitar_s3(destino, *, bucket: str, clave_aws: str, secreto: str) -> dict[str, Any]:
    """Recorre el ciclo real de un medio: subir, leer, prefirmar y borrar.

    Se usa una clave bajo el prefijo `medios/`, que es el que genera de verdad
    `app/modules/media/domain/claves.py`. Probar con otro prefijo validaria un
    permiso que la aplicacion no usa.
    """
    s3 = cliente(destino, "s3", clave=clave_aws, secreto=secreto)
    clave_objeto = "medios/00000000-0000-4000-8000-000000000000/original.txt"
    contenido = b"contenido sintetico de laboratorio"
    resultado: dict[str, Any] = {}

    estado, _ = s3.llamar(
        servicio="s3",
        metodo="PUT",
        ruta=f"/{bucket}/{clave_objeto}",
        cuerpo=contenido,
        cabeceras={"content-type": "text/plain"},
    )
    resultado["put"] = estado
    if estado not in (200, 201):
        raise ErrorDeVerificacion(f"PUT del objeto devolvio {estado}")

    estado, datos = s3.llamar(servicio="s3", metodo="GET", ruta=f"/{bucket}/{clave_objeto}")
    resultado["get"] = estado
    if estado != 200:
        raise ErrorDeVerificacion(f"GET del objeto devolvio {estado}")
    if datos != contenido:
        raise ErrorDeVerificacion("el objeto recuperado no coincide byte a byte con el subido")
    resultado["bytes_coinciden"] = True

    # La sonda de disponibilidad del backend: ListObjectsV2 acotado por prefijo.
    estado, _ = s3.llamar(
        servicio="s3",
        metodo="GET",
        ruta=f"/{bucket}",
        consulta={"list-type": "2", "prefix": "_readiness/", "max-keys": "1"},
    )
    resultado["sonda_de_disponibilidad"] = estado
    if estado != 200:
        raise ErrorDeVerificacion(f"la sonda ListObjectsV2 devolvio {estado}")

    # URL prefirmada: la firma es local, no viaja nada al generarla. Se descarga
    # SIN cabecera de autorizacion, que es lo que la hace util.
    url = s3.url_prefirmada(servicio="s3", ruta=f"/{bucket}/{clave_objeto}", expira_en=900)
    try:
        with urllib.request.urlopen(url, timeout=20) as respuesta:
            resultado["prefirmada"] = respuesta.status
            descargado = respuesta.read()
    except urllib.error.HTTPError as error:
        resultado["prefirmada"] = error.code
        descargado = b""
    if resultado["prefirmada"] != 200 or descargado != contenido:
        raise ErrorDeVerificacion(
            f"la URL prefirmada devolvio {resultado['prefirmada']} o un contenido distinto"
        )

    # Control negativo: sin firma y sin URL prefirmada NO deberia poder leerse.
    #
    # Contra AWS real esto devuelve 403: el bucket es privado, tiene los cuatro
    # bloqueos de acceso publico y su politica no concede nada a nadie.
    #
    # El resultado NO se convierte en un fallo aqui a proposito, porque en este
    # destino no mide lo que parece: el emulador solo aplica la autorizacion de
    # S3 si se activa `FLOCI_SERVICES_S3_ENFORCE_AUTH`, que por omision es false.
    # Un 200 aqui no dice que el bucket sea publico: dice que el emulador **no
    # comprueba** la autorizacion. Se registra tal cual y la privacidad del
    # bucket queda declarada AWS-only en la matriz de paridad.
    try:
        with urllib.request.urlopen(
            f"{destino.endpoints['s3']}/{bucket}/{clave_objeto}", timeout=20
        ) as respuesta:
            resultado["anonimo"] = respuesta.status
    except urllib.error.HTTPError as error:
        resultado["anonimo"] = error.code
    resultado["autorizacion_de_s3_verificada"] = resultado["anonimo"] == 403

    estado, _ = s3.llamar(servicio="s3", metodo="DELETE", ruta=f"/{bucket}/{clave_objeto}")
    resultado["delete"] = estado
    if estado not in (200, 204):
        raise ErrorDeVerificacion(f"DELETE del objeto devolvio {estado}")

    return resultado


def vaciar_bucket(destino, *, bucket: str, clave_aws: str, secreto: str) -> int:
    """Borra objetos y versiones para que el bucket pueda destruirse.

    Con versionado activo, borrar un objeto deja un marcador de borrado y el
    bucket sigue sin estar vacio. `force_destroy` deberia bastar; esto existe
    porque el laboratorio tiene que poder recuperarse tambien cuando no baste.
    """
    s3 = cliente(destino, "s3", clave=clave_aws, secreto=secreto)
    estado, datos = s3.llamar(
        servicio="s3", metodo="GET", ruta=f"/{bucket}", consulta={"versions": ""}
    )
    if estado != 200:
        return 0
    texto = datos.decode("utf-8", "replace")
    borrados = 0
    for bloque in re.findall(r"<(?:Version|DeleteMarker)>(.*?)</(?:Version|DeleteMarker)>", texto, re.DOTALL):
        clave = re.search(r"<Key>(.*?)</Key>", bloque, re.DOTALL)
        version = re.search(r"<VersionId>(.*?)</VersionId>", bloque, re.DOTALL)
        if not clave:
            continue
        consulta = {"versionId": version.group(1)} if version else None
        s3.llamar(servicio="s3", metodo="DELETE", ruta=f"/{bucket}/{clave.group(1)}", consulta=consulta)
        borrados += 1
    return borrados


def buckets_presentes(destino, *, prefijo: str, clave_aws: str, secreto: str) -> list[str]:
    s3 = cliente(destino, "s3", clave=clave_aws, secreto=secreto)
    estado, datos = s3.llamar(servicio="s3", metodo="GET", ruta="/")
    if estado != 200:
        raise ErrorDeVerificacion(f"ListBuckets devolvio {estado}")
    nombres = re.findall(rb"<Name>([^<]*)</Name>", datos)
    return [n.decode("utf-8") for n in nombres if n.decode("utf-8").startswith(prefijo)]


# --- SSM --------------------------------------------------------------------


def leer_parametro(destino, *, nombre: str, clave_aws: str, secreto: str) -> tuple[int, Any]:
    ssm = cliente(destino, "ssm", clave=clave_aws, secreto=secreto)
    return ssm.json_de_servicio(
        servicio="ssm",
        objetivo="AmazonSSM.GetParameter",
        carga={"Name": nombre, "WithDecryption": True},
    )


def parametros_presentes(destino, *, prefijo: str, clave_aws: str, secreto: str) -> list[str]:
    ssm = cliente(destino, "ssm", clave=clave_aws, secreto=secreto)
    estado, cuerpo = ssm.json_de_servicio(
        servicio="ssm",
        objetivo="AmazonSSM.GetParametersByPath",
        carga={"Path": prefijo, "Recursive": True},
    )
    if estado != 200:
        return []
    return [p["Name"] for p in cuerpo.get("Parameters", [])]


# --- IAM --------------------------------------------------------------------


def describir_rol(destino, *, nombre: str, clave_aws: str, secreto: str) -> tuple[int, str]:
    iam = cliente(destino, "iam", clave=clave_aws, secreto=secreto)
    estado, datos = iam.llamar(
        servicio="iam",
        metodo="POST",
        ruta="/",
        cuerpo=f"Action=GetRole&RoleName={nombre}&Version=2010-05-08".encode("ascii"),
        cabeceras={"content-type": "application/x-www-form-urlencoded"},
    )
    return estado, datos.decode("utf-8", "replace")


# --- Lambda -----------------------------------------------------------------


def describir_funcion(destino, *, nombre: str, clave_aws: str, secreto: str) -> tuple[int, Any]:
    lam = cliente(destino, "lambda", clave=clave_aws, secreto=secreto)
    estado, datos = lam.llamar(servicio="lambda", metodo="GET", ruta=f"{RUTA_DE_LAMBDA}/{nombre}")
    try:
        return estado, json.loads(datos or b"{}")
    except ValueError:
        return estado, {}


def invocar_funcion(
    destino, *, nombre: str, evento: Mapping[str, Any], clave_aws: str, secreto: str
) -> tuple[int, Any]:
    lam = cliente(destino, "lambda", clave=clave_aws, secreto=secreto)
    estado, datos = lam.llamar(
        servicio="lambda",
        metodo="POST",
        ruta=f"{RUTA_DE_LAMBDA}/{nombre}/invocations",
        cuerpo=json.dumps(evento).encode("utf-8"),
        cabeceras={"content-type": "application/json"},
    )
    try:
        return estado, json.loads(datos or b"{}")
    except ValueError:
        return estado, datos.decode("utf-8", "replace")


def funciones_presentes(destino, *, prefijo: str, clave_aws: str, secreto: str) -> list[str]:
    lam = cliente(destino, "lambda", clave=clave_aws, secreto=secreto)
    estado, datos = lam.llamar(servicio="lambda", metodo="GET", ruta=RUTA_DE_LAMBDA)
    if estado != 200:
        return []
    try:
        cuerpo = json.loads(datos or b"{}")
    except ValueError:
        return []
    return [
        f["FunctionName"]
        for f in cuerpo.get("Functions", [])
        if str(f.get("FunctionName", "")).startswith(prefijo)
    ]


# --- API Gateway v2 ---------------------------------------------------------


def apis_presentes(destino, *, prefijo: str, clave_aws: str, secreto: str) -> list[str]:
    api = cliente(destino, "apigatewayv2", clave=clave_aws, secreto=secreto)
    estado, datos = api.llamar(servicio="apigateway", metodo="GET", ruta="/v2/apis")
    if estado != 200:
        return []
    try:
        cuerpo = json.loads(datos or b"{}")
    except ValueError:
        return []
    return [
        i.get("Name", i.get("ApiId", ""))
        for i in cuerpo.get("Items", [])
        if str(i.get("Name", "")).startswith(prefijo)
    ]


# --- CloudWatch Logs --------------------------------------------------------


def grupos_de_logs(destino, *, prefijo: str, clave_aws: str, secreto: str) -> list[str]:
    logs = cliente(destino, "logs", clave=clave_aws, secreto=secreto)
    estado, cuerpo = logs.json_de_servicio(
        servicio="logs",
        objetivo="Logs_20140328.DescribeLogGroups",
        carga={"logGroupNamePrefix": prefijo},
    )
    if estado != 200:
        return []
    return [g["logGroupName"] for g in cuerpo.get("logGroups", [])]


def eventos_de_log(destino, *, grupo: str, clave_aws: str, secreto: str) -> list[str]:
    """Recupera eventos reales del grupo, no solo su existencia.

    Se usa `FilterLogEvents` y no Logs Insights a proposito: Insights degrada en
    silencio ante sintaxis no soportada (aws-local-parity.md 6.6), asi que una
    consulta vacia no distinguiria "no hay eventos" de "la consulta no se
    entendio".
    """
    logs = cliente(destino, "logs", clave=clave_aws, secreto=secreto)
    estado, cuerpo = logs.json_de_servicio(
        servicio="logs",
        objetivo="Logs_20140328.FilterLogEvents",
        carga={"logGroupName": grupo, "limit": 50},
    )
    if estado != 200:
        return []
    return [e.get("message", "") for e in cuerpo.get("events", [])]


# --- Camino critico ---------------------------------------------------------


#: Dominio con el que el emulador direcciona sus HTTP API. Su comodin resuelve a
#: 127.0.0.1 por DNS publico, y ademas existe como alias dentro de la red del
#: laboratorio.
DOMINIO_LOCAL_DE_API = "execute-api.localhost.floci.io"


def anfitrion_local_de_la_api(id_api: str) -> str:
    return f"{id_api}.{DOMINIO_LOCAL_DE_API}"


def solicitar_camino_critico(
    *,
    id_api: str,
    endpoint_base: str,
    ruta: str,
    tiempo_limite: int = 120,
) -> tuple[int, bytes, dict[str, str], str]:
    """Peticion HTTP real a la API, resolviendo su direccion LOCAL.

    DIFERENCIA DE PARIDAD, registrada y no disimulada
    -------------------------------------------------
    El atributo `api_endpoint` de `aws_apigatewayv2_api` **no sirve contra el
    destino local**. No es un fallo del emulador: lo sintetiza el PROVIDER a
    partir del identificador y la region, y siempre tiene la forma
    `https://{id}.execute-api.{region}.amazonaws.com`. Contra AWS real esa URL es
    la correcta; en el laboratorio no resuelve a nada alcanzable.

    La API local se direcciona por el dominio del emulador. Se intentan dos vias,
    en este orden:

      1. **Nombre DNS**: `http://{id}.execute-api.localhost.floci.io:{puerto}`.
         El comodin resuelve a 127.0.0.1 por DNS publico.
      2. **Cabecera `Host`** contra `127.0.0.1`. Es equivalente y **no depende de
         resolver un nombre publico**, asi que funciona sin DNS externo.

    La segunda es la que sobrevive en una maquina sin salida a internet, y por eso
    existe: el laboratorio no deberia depender de un registro DNS de terceros.

    Que esto sea necesario confina la diferencia al CLIENTE. El grafo de recursos,
    los modulos y la salida de Terraform son identicos para los dos destinos.
    """
    partes = urllib.parse.urlsplit(endpoint_base)
    puerto = partes.port or 4566
    anfitrion = anfitrion_local_de_la_api(id_api)

    intentos = [
        ("dns", f"http://{anfitrion}:{puerto}{ruta}", None),
        ("cabecera-host", f"http://127.0.0.1:{puerto}{ruta}", anfitrion),
    ]
    ultimo_error: Exception | None = None
    for via, url, cabecera_host in intentos:
        peticion = urllib.request.Request(url, method="GET")
        if cabecera_host:
            peticion.add_header("Host", cabecera_host)
        try:
            with urllib.request.urlopen(peticion, timeout=tiempo_limite) as respuesta:
                return respuesta.status, respuesta.read(), dict(respuesta.headers), via
        except urllib.error.HTTPError as error:
            return error.code, error.read(), dict(error.headers or {}), via
        except OSError as error:
            ultimo_error = error
    raise ErrorDeVerificacion(
        f"no se pudo alcanzar la API local por ninguna via ({ultimo_error})"
    )


def solicitar_por_http(url: str, *, tiempo_limite: int = 60) -> tuple[int, bytes, dict[str, str]]:
    """Peticion HTTP real, sin firmar: es como llega un navegador a la API.

    No lleva credenciales ni cabeceras de AWS. Si esto responde 200 con el cuerpo
    del handler, el camino API Gateway -> Lambda -> FastAPI esta demostrado de
    extremo a extremo.
    """
    peticion = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(peticion, timeout=tiempo_limite) as respuesta:
            return respuesta.status, respuesta.read(), dict(respuesta.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers or {})
    except OSError as error:
        raise ErrorDeVerificacion(f"no se pudo alcanzar '{url}': {error}") from error
