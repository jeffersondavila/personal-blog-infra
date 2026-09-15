#!/usr/bin/env python3
"""Identidad congelada del artefacto ZIP de Lambda.

Por que existe
--------------
El constructor canonico del artefacto es
`personal-blog-backend/scripts/empaquetar_lambda.py` (`Task/024`). Este
repositorio **no lo construye, no lo versiona y no lo copia**: recibe una **ruta
explicita** y la trata como una entrada externa.

El riesgo concreto que cubre este modulo es una ventana pequena y silenciosa:
Terraform calcula `source_code_hash` cuando corre `plan`, y vuelve a leer el
archivo cuando corre `apply`. Si el ZIP se reconstruye entre ambos —cosa normal
mientras se trabaja en el backend— el `apply` desplegaria bytes que nadie
reviso, y el plan aprobado dejaria de describir lo que se aplico.

La respuesta es congelar la identidad antes del `plan` y volver a exigirla antes
del `apply`. El tamano solo no vale: dos ZIP pueden medir lo mismo y diferir. La
identidad es el **sha256**.

El SHA que `Task/024` registro en su reporte es **evidencia de esa tarea**, no
una constante de este modulo: el artefacto se reconstruye y su hash cambia
legitimamente cuando cambian las fuentes o los locks del backend. Por eso aqui
no hay ningun hash fijado.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Final

#: Se lee por bloques: el artefacto ronda los 41 MiB y no hay motivo para
#: cargarlo entero en memoria solo para resumirlo.
BLOQUE: Final = 1024 * 1024


class ErrorDeArtefacto(RuntimeError):
    """El artefacto no existe, no es legible o dejo de ser el que se reviso."""


@dataclass(frozen=True)
class Artefacto:
    """Identidad de un artefacto en un instante concreto."""

    ruta: Path
    tamano: int
    sha256: str


def _resumir(ruta: Path) -> tuple[int, str]:
    resumen = hashlib.sha256()
    tamano = 0
    try:
        with ruta.open("rb") as archivo:
            while True:
                bloque = archivo.read(BLOQUE)
                if not bloque:
                    break
                tamano += len(bloque)
                resumen.update(bloque)
    except OSError as error:
        raise ErrorDeArtefacto(f"no se pudo leer el artefacto '{ruta}': {error}") from error
    return tamano, resumen.hexdigest()


def describir_artefacto(ruta: str | Path) -> Artefacto:
    """Congela la identidad del artefacto que se va a desplegar."""
    resuelta = Path(ruta).resolve()
    if not resuelta.exists():
        raise ErrorDeArtefacto(
            f"el artefacto '{resuelta}' no existe. Construyelo con "
            "'scripts/empaquetar_lambda.py construir --destino <carpeta>' en "
            "personal-blog-backend y pasa la ruta con --lambda-zip"
        )
    if not resuelta.is_file():
        raise ErrorDeArtefacto(f"'{resuelta}' no es un archivo")
    tamano, sha256 = _resumir(resuelta)
    if tamano == 0:
        raise ErrorDeArtefacto(f"el artefacto '{resuelta}' esta vacio")
    return Artefacto(ruta=resuelta, tamano=tamano, sha256=sha256)


def confirmar_sin_cambios(artefacto: Artefacto) -> None:
    """Exige que el artefacto siga siendo **exactamente** el que se congelo."""
    if not artefacto.ruta.exists():
        raise ErrorDeArtefacto(
            f"el artefacto '{artefacto.ruta}' desaparecio despues de revisarlo"
        )
    tamano, sha256 = _resumir(artefacto.ruta)
    if tamano != artefacto.tamano:
        raise ErrorDeArtefacto(
            f"el artefacto cambio de tamano: {artefacto.tamano} -> {tamano} bytes. "
            "El plan revisado ya no describe lo que se aplicaria"
        )
    if sha256 != artefacto.sha256:
        raise ErrorDeArtefacto(
            "el artefacto cambio de contenido con el mismo tamano: sha256 "
            f"{artefacto.sha256} -> {sha256}. El plan revisado ya no describe "
            "lo que se aplicaria"
        )
