#!/usr/bin/env python3
"""Cliente AWS minimo con firma SigV4, solo biblioteca estandar.

Por que no se usa boto3 ni AWS CLI
----------------------------------
`aws-local-parity.md` §4.2 exige que las herramientas hablen **interfaces
estandar de AWS** y no una API propia del emulador. Este modulo cumple esa regla
por la via mas directa: habla el protocolo AWS —SigV4 sobre HTTP— sin ningun
intermediario.

La alternativa era anadir `boto3` o el AWS CLI a `personal-blog-infra`. Hoy este
repositorio no declara **ninguna** dependencia de terceros para Python: sus
scripts son *stdlib* puro, y el proyecto fija cada artefacto externo por version
y digest. Anadir una cadena de dependencias nueva —y su verificacion de
procedencia, y su lugar en el gate S-09— para inspeccionar un laboratorio local
era mas superficie de la que el problema pide.

La contrapartida es que la firma la escribimos nosotros, asi que se valida
contra el **ejemplo canonico publicado por AWS** en
`tests/laboratorio/test_firma_aws.py`: si la firma calculada coincide con la
documentada, la implementacion sigue el protocolo y no una aproximacion.

**Registrado como decision propuesta** en la ficha de `Task/025`: si el usuario
prefiere `boto3`, se sustituye este modulo sin tocar Terraform ni las guardas.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from typing import Any, Final

ALGORITMO: Final = "AWS4-HMAC-SHA256"
TERMINADOR: Final = "aws4_request"

#: sha256 de la cadena vacia. Es el valor que exige `x-amz-content-sha256`
#: cuando no hay cuerpo.
HASH_DEL_CUERPO_VACIO: Final = hashlib.sha256(b"").hexdigest()

#: Caracteres que SigV4 **no** escapa al codificar un componente.
SIN_ESCAPAR: Final = "-_.~"


class ErrorDeFirma(RuntimeError):
    """La peticion no se pudo firmar o el servicio devolvio un error."""


def _codificar(valor: str) -> str:
    return urllib.parse.quote(str(valor), safe=SIN_ESCAPAR)


def cadena_de_consulta(consulta: Mapping[str, Any] | None) -> str:
    """Cadena de consulta canonica: ordenada por clave y codificada."""
    if not consulta:
        return ""
    return "&".join(
        f"{_codificar(clave)}={_codificar(consulta[clave])}" for clave in sorted(consulta)
    )


def peticion_canonica(
    *,
    metodo: str,
    ruta: str,
    consulta: Mapping[str, Any] | None,
    cabeceras: Mapping[str, str],
    hash_del_cuerpo: str,
) -> str:
    """Construye la peticion canonica de SigV4.

    Las cabeceras se normalizan a minusculas, se ordenan y se recortan, que es lo
    que define el algoritmo. La ruta se pasa ya codificada por quien llama: para
    S3 el nombre de la clave forma parte de la ruta y su codificacion no es la
    misma que la de un parametro.
    """
    nombres = sorted(nombre.lower() for nombre in cabeceras)
    normalizadas = {nombre.lower(): valor for nombre, valor in cabeceras.items()}
    canonicas = "".join(f"{nombre}:{normalizadas[nombre].strip()}\n" for nombre in nombres)
    firmadas = ";".join(nombres)
    return "\n".join(
        [
            metodo.upper(),
            ruta or "/",
            cadena_de_consulta(consulta),
            canonicas,
            firmadas,
            hash_del_cuerpo,
        ]
    )


def cabeceras_firmadas(cabeceras: Mapping[str, str]) -> str:
    return ";".join(sorted(nombre.lower() for nombre in cabeceras))


def _derivar_clave(clave_secreta: str, dia: str, region: str, servicio: str) -> bytes:
    def paso(clave: bytes, dato: str) -> bytes:
        return hmac.new(clave, dato.encode("utf-8"), hashlib.sha256).digest()

    clave = paso(("AWS4" + clave_secreta).encode("utf-8"), dia)
    clave = paso(clave, region)
    clave = paso(clave, servicio)
    return paso(clave, TERMINADOR)


def alcance_de_credencial(marca: str, region: str, servicio: str) -> str:
    return f"{marca[:8]}/{region}/{servicio}/{TERMINADOR}"


def calcular_firma(
    *,
    clave_secreta: str,
    marca: str,
    region: str,
    servicio: str,
    peticion_canonica: str,
) -> str:
    """Firma hexadecimal de la peticion canonica."""
    alcance = alcance_de_credencial(marca, region, servicio)
    para_firmar = "\n".join(
        [
            ALGORITMO,
            marca,
            alcance,
            hashlib.sha256(peticion_canonica.encode("utf-8")).hexdigest(),
        ]
    )
    clave = _derivar_clave(clave_secreta, marca[:8], region, servicio)
    return hmac.new(clave, para_firmar.encode("utf-8"), hashlib.sha256).hexdigest()


def cabecera_de_autorizacion(
    *,
    clave_de_acceso: str,
    marca: str,
    region: str,
    servicio: str,
    cabeceras_firmadas: str,
    firma: str,
) -> str:
    alcance = alcance_de_credencial(marca, region, servicio)
    return (
        f"{ALGORITMO} Credential={clave_de_acceso}/{alcance}, "
        f"SignedHeaders={cabeceras_firmadas}, Signature={firma}"
    )


class ClienteAws:
    """Cliente firmado contra un endpoint explicito.

    No resuelve endpoints: quien lo construye pasa el del destino ya validado por
    `destino.py`. Esa es la razon de que no exista ningun valor por omision aqui.
    """

    def __init__(
        self,
        *,
        endpoint: str,
        region: str,
        clave_de_acceso: str,
        clave_secreta: str,
        tiempo_limite: int = 30,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.region = region
        self.clave_de_acceso = clave_de_acceso
        self.clave_secreta = clave_secreta
        self.tiempo_limite = tiempo_limite

    def _anfitrion(self) -> str:
        return urllib.parse.urlsplit(self.endpoint).netloc

    def llamar(
        self,
        *,
        servicio: str,
        metodo: str = "GET",
        ruta: str = "/",
        consulta: Mapping[str, Any] | None = None,
        cuerpo: bytes = b"",
        cabeceras: Mapping[str, str] | None = None,
        momento: dt.datetime | None = None,
    ) -> tuple[int, bytes]:
        """Ejecuta una peticion firmada y devuelve `(estado, cuerpo)`.

        No lanza ante un estado HTTP de error: muchas comprobaciones del
        laboratorio **esperan** un 404 —por ejemplo, para demostrar que un recurso
        ya no existe—, asi que interpretar el estado es del que llama.
        """
        ahora = momento or dt.datetime.now(dt.UTC)
        marca = ahora.strftime("%Y%m%dT%H%M%SZ")
        hash_del_cuerpo = hashlib.sha256(cuerpo).hexdigest()
        todas: dict[str, str] = {
            "host": self._anfitrion(),
            "x-amz-date": marca,
            "x-amz-content-sha256": hash_del_cuerpo,
        }
        for nombre, valor in (cabeceras or {}).items():
            todas[nombre.lower()] = valor

        canonica = peticion_canonica(
            metodo=metodo,
            ruta=ruta,
            consulta=consulta,
            cabeceras=todas,
            hash_del_cuerpo=hash_del_cuerpo,
        )
        firma = calcular_firma(
            clave_secreta=self.clave_secreta,
            marca=marca,
            region=self.region,
            servicio=servicio,
            peticion_canonica=canonica,
        )
        autorizacion = cabecera_de_autorizacion(
            clave_de_acceso=self.clave_de_acceso,
            marca=marca,
            region=self.region,
            servicio=servicio,
            cabeceras_firmadas=cabeceras_firmadas(todas),
            firma=firma,
        )

        consulta_codificada = cadena_de_consulta(consulta)
        url = self.endpoint + ruta + ("?" + consulta_codificada if consulta_codificada else "")
        peticion = urllib.request.Request(url, data=cuerpo or None, method=metodo.upper())
        for nombre, valor in todas.items():
            peticion.add_header(nombre, valor)
        peticion.add_header("Authorization", autorizacion)
        try:
            with urllib.request.urlopen(peticion, timeout=self.tiempo_limite) as respuesta:
                return respuesta.status, respuesta.read()
        except urllib.error.HTTPError as error:
            return error.code, error.read()
        except OSError as error:
            raise ErrorDeFirma(f"no se pudo contactar con '{url}': {error}") from error

    def json_de_servicio(
        self,
        *,
        servicio: str,
        objetivo: str,
        carga: Mapping[str, Any],
        version_json: str = "1.1",
    ) -> tuple[int, Any]:
        """Llamada al protocolo `json` de AWS (SSM, Logs, Lambda de control)."""
        cuerpo = json.dumps(carga).encode("utf-8")
        estado, datos = self.llamar(
            servicio=servicio,
            metodo="POST",
            ruta="/",
            cuerpo=cuerpo,
            cabeceras={
                "content-type": f"application/x-amz-json-{version_json}",
                "x-amz-target": objetivo,
            },
        )
        try:
            return estado, json.loads(datos or b"{}")
        except ValueError:
            return estado, {"crudo": datos.decode("utf-8", "replace")}

    def url_prefirmada(
        self,
        *,
        servicio: str,
        ruta: str,
        expira_en: int = 900,
        metodo: str = "GET",
        momento: dt.datetime | None = None,
    ) -> str:
        """URL prefirmada por *query string*. La firma es local: no viaja nada."""
        ahora = momento or dt.datetime.now(dt.UTC)
        marca = ahora.strftime("%Y%m%dT%H%M%SZ")
        consulta = {
            "X-Amz-Algorithm": ALGORITMO,
            "X-Amz-Credential": f"{self.clave_de_acceso}/"
            + alcance_de_credencial(marca, self.region, servicio),
            "X-Amz-Date": marca,
            "X-Amz-Expires": str(expira_en),
            "X-Amz-SignedHeaders": "host",
        }
        canonica = peticion_canonica(
            metodo=metodo,
            ruta=ruta,
            consulta=consulta,
            cabeceras={"host": self._anfitrion()},
            hash_del_cuerpo="UNSIGNED-PAYLOAD",
        )
        firma = calcular_firma(
            clave_secreta=self.clave_secreta,
            marca=marca,
            region=self.region,
            servicio=servicio,
            peticion_canonica=canonica,
        )
        consulta["X-Amz-Signature"] = firma
        return f"{self.endpoint}{ruta}?{cadena_de_consulta(consulta)}"
