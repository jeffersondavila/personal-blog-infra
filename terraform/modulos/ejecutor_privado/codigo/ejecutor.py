"""Ejecutora privada de D-24, fase H-031-5 de Task/031: shell sin conexiones.

Contrato de invocacion, cerrado:

- Se invoca solo por el plano de control (`lambda:InvokeFunction`). No tiene URL, ni API, ni disparadores.
- El evento es un objeto JSON con UNA sola clave, `modo`.
- `selfcheck` demuestra que la funcion se invoca y responde el contrato. No abre ninguna conexion.
- Los modos de D-24 estan reconocidos y NO implementados en esta fase: responden `NOT_IMPLEMENTED` con su fase
  propietaria, sin efectos. Ninguno se finge completo.
- Cualquier otro evento es `INVALID_PAYLOAD`, sin repetir nada de lo recibido.

La respuesta y el registro llevan solo claves del contrato: nunca el evento, el contexto ni una traza. Solo
biblioteca estandar.
"""

import json
import sys

CONTRATO = "d24-ejecutor-h0315-v1"
SELFCHECK = "selfcheck"

# Modo de D-24 -> fase que lo implementa. Hasta entonces, NOT_IMPLEMENTED.
FASES = {
    "verify": "H-031-6",
    "export": "H-031-6",
    "upgrade": "Task/036",
    "downgrade": "Task/036",
    "purge": "Task/036",
}
MODOS = (SELFCHECK, *FASES)


def _modo(evento):
    """El modo pedido, o None si el evento no cumple EXACTAMENTE el esquema."""
    if type(evento) is not dict or list(evento) != ["modo"]:
        return None
    modo = evento["modo"]
    if type(modo) is not str or modo not in MODOS:
        return None
    return modo


def _responder(estado, modo=None, **campos):
    respuesta = {"contrato": CONTRATO, "estado": estado}
    if modo is not None:
        respuesta["modo"] = modo
    respuesta.update(campos)
    # Una linea por invocacion, con las mismas claves siempre: nada del evento.
    print(json.dumps({"contrato": CONTRATO, "estado": estado, "modo": modo}, sort_keys=True))
    return respuesta


def manejar(evento, contexto):
    try:
        modo = _modo(evento)
        if modo is None:
            return _responder("INVALID_PAYLOAD")
        if modo == SELFCHECK:
            return _responder(
                "OK",
                modo,
                python=f"{sys.version_info.major}.{sys.version_info.minor}",
                modos_d24={nombre: "NOT_IMPLEMENTED" for nombre in FASES},
            )
        return _responder("NOT_IMPLEMENTED", modo, fase_propietaria=FASES[modo])
    except Exception:
        # Fail-closed: ni el detalle ni la traza salen de la funcion.
        return {"contrato": CONTRATO, "estado": "INTERNAL_ERROR"}
