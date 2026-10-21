"""Ejecutora privada de D-24, fase H-031-6 de Task/031: PostgreSQL con `verify-full`.

Contrato de invocacion, cerrado:

- Se invoca solo por el plano de control (`lambda:InvokeFunction`), de forma SINCRONA, por la identidad operativa
  autorizada. No tiene URL, ni API, ni disparadores.
- Las credenciales llegan en el evento de esa invocacion y solo viven en memoria mientras dura. La funcion no lee
  ningun almacen de parametros ni de claves, no tiene variables de configuracion y nunca devuelve ni registra una
  contrasena, un verificador SCRAM ni el host.
- Modos de D-24: `verify` y `export` implementados; `upgrade`, `downgrade` y `purge` responden `NOT_IMPLEMENTED` con
  su fase propietaria (Task/036), sin efectos. Modos de provision de Task/031, fuera de los cuatro de D-24:
  `identidades` (H-031-6) y `sintetico` (H-031-7).
- Cualquier evento fuera del esquema de su modo es `INVALID_PAYLOAD`, sin abrir conexion y sin repetir nada de lo
  recibido.

La respuesta y el registro llevan solo claves del contrato: nunca el evento, el contexto ni una traza.
"""

import json
import re
import sys

import exportacion
import operaciones

CONTRATO = "d24-ejecutor-h0316-v1"
SELFCHECK = "selfcheck"

# Modo de D-24 -> fase que lo implementa; None si este artefacto ya lo implementa.
FASES = {
    "verify": None,
    "export": None,
    "upgrade": "Task/036",
    "downgrade": "Task/036",
    "purge": "Task/036",
}
PROVISION = ("identidades", "sintetico")

# Esquema por modo: claves obligatorias, claves opcionales e identidades SQL admitidas.
ESQUEMAS = {
    "verify": ({"modo", "destino", "credencial"}, {"controles_negativos", "marcador"},
               ("blogadmin", "blog_migrate", "blog_app")),
    "identidades": ({"modo", "destino", "credencial", "verificadores"}, set(), ("blogadmin",)),
    "sintetico": ({"modo", "destino", "credencial", "marcador", "accion"}, set(), ("blog_migrate",)),
    "export": ({"modo", "destino", "credencial", "salida"}, set(), ("blog_migrate",)),
}

_PRODUCTIVA = re.compile(r"blog-prod-postgres\.[a-z0-9]{12}\.us-east-2\.rds\.amazonaws\.com")
_RESTAURADA = re.compile(r"blog-prod-restore-h0317-[0-9]{14}\.[a-z0-9]{12}\.us-east-2\.rds\.amazonaws\.com")
_CONTRASENA = re.compile(r"[A-Za-z0-9]{32,64}")
_VERIFICADOR = re.compile(r"SCRAM-SHA-256\$4096:[A-Za-z0-9+/]{22}==\$[A-Za-z0-9+/]{43}=:[A-Za-z0-9+/]{43}=")
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
_INSTANTE = re.compile(r"20[0-9]{2}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]Z")
# Sin puntos: el certificado comodin de S3 no cubre un nombre con puntos en el estilo de host virtual.
_BUCKET = re.compile(r"[a-z0-9][a-z0-9-]{1,61}[a-z0-9]")
_MARCA = re.compile(r"20[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3])[0-5][0-9][0-5][0-9]Z")


def _texto(valor, patron):
    return type(valor) is str and patron.fullmatch(valor) is not None


def _objeto(valor, claves):
    return type(valor) is dict and set(valor) == claves


def _valido(evento, modo):
    """True si el evento cumple EXACTAMENTE el esquema de un modo que abre conexion."""
    obligatorias, opcionales, usuarios = ESQUEMAS[modo]
    if not obligatorias <= set(evento) <= obligatorias | opcionales:
        return False
    destino, credencial = evento["destino"], evento["credencial"]
    if not _objeto(destino, {"host", "base"}) or destino["base"] != operaciones.BASE:
        return False
    # Solo `verify` alcanza una instancia restaurada de H-031-7; lo que escribe va siempre a la productiva.
    if not (_texto(destino["host"], _PRODUCTIVA) or modo == "verify" and _texto(destino["host"], _RESTAURADA)):
        return False
    if not _objeto(credencial, {"usuario", "contrasena"}) or credencial["usuario"] not in usuarios:
        return False
    if not _texto(credencial["contrasena"], _CONTRASENA):
        return False
    if modo == "verify":
        if "controles_negativos" in evento and type(evento["controles_negativos"]) is not bool:
            return False
        if "marcador" in evento:
            marcador = evento["marcador"]
            return (credencial["usuario"] == "blog_migrate" and _objeto(marcador, {"id"})
                    and _texto(marcador["id"], _UUID))
        return True
    if modo == "export":
        salida = evento["salida"]
        return (_objeto(salida, {"bucket", "marca"}) and _texto(salida["bucket"], _BUCKET)
                and _texto(salida["marca"], _MARCA))
    if modo == "identidades":
        verificadores = evento["verificadores"]
        return _objeto(verificadores, {"blog_migrate", "blog_app"}) and all(
            _texto(valor, _VERIFICADOR) for valor in verificadores.values())
    marcador = evento["marcador"]
    return (evento["accion"] in ("sembrar", "limpiar") and _objeto(marcador, {"id", "instante"})
            and _texto(marcador["id"], _UUID) and _texto(marcador["instante"], _INSTANTE))


def _modo(evento):
    """El modo pedido, o None si el evento no cumple EXACTAMENTE el esquema de ese modo."""
    if type(evento) is not dict or type(evento.get("modo")) is not str:
        return None
    modo = evento["modo"]
    if modo == SELFCHECK or FASES.get(modo) is not None:
        return modo if list(evento) == ["modo"] else None
    if modo in ESQUEMAS and _valido(evento, modo):
        return modo
    return None


def _responder(estado, modo=None, **campos):
    respuesta = {"contrato": CONTRATO, "estado": estado}
    if modo is not None:
        respuesta["modo"] = modo
    respuesta.update(campos)
    json.dumps(respuesta)  # una respuesta que no se puede serializar es un error interno, no una a medias
    # Una linea por invocacion, con las mismas claves siempre: nada del evento.
    print(json.dumps({"contrato": CONTRATO, "estado": estado, "modo": modo}, sort_keys=True))
    return respuesta


def manejar(evento, contexto):
    modo = None
    try:
        modo = _modo(evento)
        if modo is None:
            return _responder("INVALID_PAYLOAD")
        if modo == SELFCHECK:
            return _responder(
                "OK",
                modo,
                python=f"{sys.version_info.major}.{sys.version_info.minor}",
                modos_d24={nombre: "NOT_IMPLEMENTED" if fase else "IMPLEMENTED" for nombre, fase in FASES.items()},
                modos_de_task031=list(PROVISION),
            )
        if FASES.get(modo) is not None:
            return _responder("NOT_IMPLEMENTED", modo, fase_propietaria=FASES[modo])
        modulo = exportacion if modo == "export" else operaciones
        return _responder("OK", modo, **getattr(modulo, modo)(evento))
    except operaciones.Fallo as fallo:
        return _responder(fallo.codigo, modo, **fallo.detalle)
    except Exception:
        # Fail-closed: ni el detalle ni la traza salen de la funcion.
        return _responder("INTERNAL_ERROR", modo)
