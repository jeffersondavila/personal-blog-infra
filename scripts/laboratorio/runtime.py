#!/usr/bin/env python3
"""Runtime de Lambda: se FIJA por digest, no se vigila la etiqueta (H-025-3).

El error que corrige este modulo
--------------------------------
La primera version de la guarda hacia `docker pull` de la **etiqueta**
`public.ecr.aws/lambda/python:3.12` y abortaba si el digest al que resolvia ya no
era el que `Task/024` fijo. Es decir, comprobaba **frescura de la etiqueta** y la
trataba como autoridad de identidad.

Eso estaba mal, y se demostro con hechos:

- `Task/024` construye con una referencia **inmutable**,
  `REFERENCIA_DEL_RUNTIME = etiqueta + "@" + digest`. El movimiento posterior de
  la etiqueta **no** afecta a su reproducibilidad.
- El digest fijado **sigue descargable**: se borro la copia local, se volvio a
  bajar por digest desde el registro y el ZIP se reconstruyo con el **mismo**
  `sha256`.

Consecuencia: exigir que una etiqueta mutable siguiera apuntando eternamente al
digest antiguo bloqueaba el laboratorio ante un refresco rutinario de la imagen
base de AWS, sin proteger nada. La etiqueta movil es una **senal de que hay una
actualizacion disponible**, no una autoridad.

Lo que si hay que garantizar
----------------------------
Que el emulador ejecute la Lambda sobre **el mismo runtime que construyo el
ZIP**. El emulador resuelve el runtime **por etiqueta**, asi que la respuesta
correcta es **fijar**, no abortar:

1. descargar la referencia **por digest** que declara `Task/024`;
2. asociar localmente la **etiqueta** que el emulador pide a ese contenido;
3. verificar con la identidad efectiva de Docker que la etiqueta resuelve a esa
   imagen;
4. tras una invocacion real, comprobar que el contenedor lanzado usa esa imagen.

Una sola autoridad
------------------
El digest **no se declara aqui**. Se lee del `manifiesto.json` que `Task/024`
escribe junto al artefacto, campo `imagen`. `Task/024` sigue siendo la autoridad
del runtime y `Task/025` lo **consume**; no hay una segunda decision
independiente ni una constante duplicada que pueda desincronizarse.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Protocol

#: Nombre del manifiesto que escribe `Task/024` junto al ZIP.
NOMBRE_DEL_MANIFIESTO: Final = "manifiesto.json"

#: Unica plataforma autorizada por el proyecto.
PLATAFORMA: Final = "linux/amd64"

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


class ErrorDeRuntime(RuntimeError):
    """El runtime fijado no se pudo leer, obtener o demostrar."""


@dataclass(frozen=True)
class RuntimeFijado:
    """Identidad del runtime, tal como la declaro `Task/024`."""

    etiqueta: str
    digest: str
    referencia: str
    plataforma: str


class Docker(Protocol):
    """Lo minimo que este modulo necesita de Docker.

    Se declara como protocolo para que los controles negativos ejerciten cada
    fallo —descarga, etiquetado, identidad discordante— sin tocar el demonio.
    """

    def descargar(self, referencia: str) -> None: ...
    def identificador(self, referencia: str) -> str | None: ...
    def etiquetar(self, origen: str, destino: str) -> None: ...


def leer_runtime_fijado(ruta_del_zip: str | Path) -> RuntimeFijado:
    """Lee la identidad del runtime del manifiesto de `Task/024`.

    Se exige el manifiesto a proposito: `Task/025` consume el **paquete** que
    produce `Task/024` —ZIP mas manifiesto—, no un ZIP suelto. Sin el, el digest
    tendria que declararse aqui, y eso crearia una segunda autoridad sobre el
    runtime que podria desincronizarse en silencio.
    """
    zip_resuelto = Path(ruta_del_zip).resolve()
    ruta = zip_resuelto.parent / NOMBRE_DEL_MANIFIESTO
    if not ruta.is_file():
        raise ErrorDeRuntime(
            f"no existe el manifiesto '{NOMBRE_DEL_MANIFIESTO}' junto al artefacto "
            f"({ruta}). Lo escribe 'scripts/empaquetar_lambda.py construir "
            "--destino <carpeta>' de personal-blog-backend, y es la autoridad de "
            "Task/024 sobre el runtime: sin el, Task/025 tendria que declarar el "
            "digest por su cuenta"
        )
    try:
        datos: Any = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ErrorDeRuntime(f"no se pudo leer '{ruta}': {error}") from error

    imagen = datos.get("imagen") if isinstance(datos, dict) else None
    if not isinstance(imagen, dict):
        raise ErrorDeRuntime(
            f"'{ruta}' no declara la seccion 'imagen'; no se puede saber sobre que "
            "runtime se construyo el artefacto"
        )

    etiqueta = str(imagen.get("etiqueta") or "")
    digest = str(imagen.get("digest") or "")
    referencia = str(imagen.get("referencia") or "")
    plataforma = str(imagen.get("plataforma") or "")

    if not _DIGEST.match(digest):
        raise ErrorDeRuntime(f"el manifiesto declara un digest invalido: '{digest}'")
    if not etiqueta:
        raise ErrorDeRuntime("el manifiesto no declara la etiqueta del runtime")
    # La referencia debe ser EXACTAMENTE etiqueta@digest. Si no lo es, el
    # manifiesto se contradice y no hay forma de elegir a cual creer.
    if referencia != f"{etiqueta}@{digest}":
        raise ErrorDeRuntime(
            "el manifiesto es incoherente: la referencia "
            f"'{referencia}' no es '{etiqueta}@{digest}'"
        )
    if plataforma != PLATAFORMA:
        raise ErrorDeRuntime(
            f"el manifiesto declara la plataforma '{plataforma}' y el proyecto solo "
            f"autoriza '{PLATAFORMA}'"
        )
    return RuntimeFijado(
        etiqueta=etiqueta, digest=digest, referencia=referencia, plataforma=plataforma
    )


def preparar_runtime(fijado: RuntimeFijado, docker: Docker) -> dict[str, Any]:
    """Deja la etiqueta local resolviendo al contenido fijado por `Task/024`.

    Se ejecuta en la fase de **preparacion**, con acceso al registro, antes de
    cerrar el perimetro. Despues, durante el ciclo aislado, el emulador encuentra
    el runtime ya presente y no necesita descargar nada.

    Nunca se descarga la etiqueta desnuda: la unica referencia que se pide al
    registro lleva `@sha256:`.
    """
    informe: dict[str, Any] = {
        "referencia": fijado.referencia,
        "etiqueta": fijado.etiqueta,
        "digest": fijado.digest,
    }

    id_previo_de_la_etiqueta = docker.identificador(fijado.etiqueta)
    informe["id_anterior"] = id_previo_de_la_etiqueta

    # Descarga por DIGEST. Si el contenido fijado no se puede obtener, se aborta:
    # ejecutar el artefacto sobre otro runtime invalidaria la evidencia.
    try:
        docker.descargar(fijado.referencia)
    except ErrorDeRuntime:
        raise
    except Exception as error:
        raise ErrorDeRuntime(
            f"no se pudo descargar el runtime fijado {fijado.digest}: {error}"
        ) from error

    id_del_digest = docker.identificador(fijado.referencia)
    if not id_del_digest:
        raise ErrorDeRuntime(
            f"la descarga de '{fijado.referencia}' no dejo ninguna imagen utilizable; "
            f"no se puede demostrar la identidad del runtime {fijado.digest}"
        )
    informe["id"] = id_del_digest

    if id_previo_de_la_etiqueta == id_del_digest:
        # Idempotente: la etiqueta ya resuelve al contenido correcto.
        informe["accion"] = "ya_correcta"
        return informe

    try:
        docker.etiquetar(fijado.referencia, fijado.etiqueta)
    except ErrorDeRuntime:
        raise
    except Exception as error:
        raise ErrorDeRuntime(
            f"no se pudo asociar la etiqueta '{fijado.etiqueta}' al runtime fijado: "
            f"{error}"
        ) from error

    # Verificacion con la identidad EFECTIVA de Docker, no con el texto de la
    # etiqueta: etiquetar puede "funcionar" y dejar otra cosa.
    id_final = docker.identificador(fijado.etiqueta)
    if id_final != id_del_digest:
        raise ErrorDeRuntime(
            f"la identidad de '{fijado.etiqueta}' no es la del runtime fijado: "
            f"resuelve a {id_final} y se esperaba {id_del_digest}"
        )

    informe["accion"] = "reetiquetada" if id_previo_de_la_etiqueta else "etiquetada"
    return informe


#: Prefijo con el que el emulador nombra los contenedores que lanza.
PREFIJO_DEL_EMULADOR: Final = "floci-"

#: El emulador lanza DOS contenedores por invocacion en frio. Solo uno ejecuta el
#: codigo; el otro puebla el volumen de codigo y se llama `floci-codevol-…`.
#: Observado en sus logs durante una invocacion real:
#:
#:   floci-codevol-blog-lab-backend-c702b34d   <- puebla el volumen
#:   floci-blog-lab-backend-85f90d15           <- ejecuta la funcion
#:
#: Confundirlos daria por evidencia un contenedor auxiliar que nunca corrio el
#: handler.
INFIJOS_AUXILIARES: Final = ("codevol-",)


def es_contenedor_de_la_funcion(nombre: str, nombre_de_la_funcion: str) -> bool:
    """Decide si un contenedor es el que ejecuta la funcion.

    Se exige el prefijo del emulador **y** el nombre de la funcion, y se descartan
    los contenedores auxiliares. Un nombre que solo contenga el de la funcion no
    basta: el servicio del entorno ordinario del blog tambien lo contendria.
    """
    if not nombre.startswith(PREFIJO_DEL_EMULADOR):
        return False
    resto = nombre[len(PREFIJO_DEL_EMULADOR):]
    if any(resto.startswith(infijo) for infijo in INFIJOS_AUXILIARES):
        return False
    return resto.startswith(nombre_de_la_funcion)


def repositorio_de_la_etiqueta(etiqueta: str) -> str:
    """Parte de repositorio de una etiqueta, sin la etiqueta de version.

    Se separa por el **ultimo** `:` y solo si lo que sigue no contiene `/`, porque
    un registro con puerto —`registro:5000/imagen`— tambien lleva dos puntos.
    """
    cuerpo, separador, version = etiqueta.rpartition(":")
    if separador and "/" not in version:
        return cuerpo
    return etiqueta


def representaciones_de_la_identidad(fijado: RuntimeFijado, id_esperado: str) -> frozenset[str]:
    """Las formas en que Docker puede nombrar EXACTAMENTE el runtime fijado.

    Es una lista **cerrada**, derivada por completo de la identidad inmutable de
    `Task/024` y del identificador local de esa misma imagen. No hay ningun
    patron: «parece un sha256» no entra aqui, y una etiqueta, un digest o un
    identificador distintos quedan fuera por construccion.
    """
    return frozenset(
        {
            # Etiqueta fijada, que es lo que entregaba Docker historicamente.
            fijado.etiqueta,
            # Referencia inmutable completa, etiqueta mas digest.
            fijado.referencia,
            # Referencia por digest sin etiqueta.
            f"{repositorio_de_la_etiqueta(fijado.etiqueta)}@{fijado.digest}",
            # Digest desnudo. Con el almacen de imagenes de containerd, Docker
            # 29.1.3 entrega esto en `Config.Image`, y ahi `.Id` ES el digest del
            # manifiesto: la misma identidad, nombrada de otra manera.
            fijado.digest,
            # Identificador local de la imagen fijada, para el almacen clasico,
            # donde el `.Id` no coincide con el digest del registro.
            id_esperado,
        }
        - {""}
    )


def confirmar_imagen_del_contenedor(
    fijado: RuntimeFijado,
    *,
    imagen_solicitada: str | None,
    id_observado: str | None,
    id_esperado: str,
) -> None:
    """Comprueba que el contenedor que lanzo el emulador usa el runtime fijado.

    El mensaje del emulador *«Image already present locally, skipping pull»* es
    evidencia util, pero dice lo que el emulador **decidio**, no lo que
    **ejecuto**. Por eso aqui se compara la identidad del contenedor real.

    `id_observado` a `None` no es una confirmacion: no haber encontrado el
    contenedor significa que no se pudo demostrar nada.

    Sobre la **representacion** de la imagen, que es el arreglo de **DEF-030-3**:
    antes se exigia que `Config.Image` fuera textualmente `fijado.etiqueta`. Eso
    confundia una **forma de nombrar** con la **identidad**, y rompio sin que
    nada del proyecto cambiara: con el almacen de imagenes de containerd, Docker
    29.1.3 entrega el digest desnudo en lugar de la etiqueta. `Task/025` habia
    observado la etiqueta, con el mismo image ID y el mismo digest fijado.

    Ahora se exige que la representacion pertenezca a la lista **cerrada** de
    formas que denotan el runtime fijado. La comprobacion autoritativa del
    identificador **no se relaja**: sigue exigiendose igualdad exacta con
    `id_esperado`, y se comprueba siempre.
    """
    if not id_observado:
        raise ErrorDeRuntime(
            "no se observo ningun contenedor de Lambda del que leer la imagen; sin "
            "esa observacion no se puede afirmar que se ejecuto el runtime fijado"
        )
    admitidas = representaciones_de_la_identidad(fijado, id_esperado)
    if not imagen_solicitada or imagen_solicitada not in admitidas:
        raise ErrorDeRuntime(
            f"el contenedor pidio la imagen '{imagen_solicitada}', que no denota el "
            f"runtime fijado por Task/024 ({fijado.referencia}). Representaciones "
            f"admitidas: {sorted(admitidas)}"
        )
    if id_observado != id_esperado:
        raise ErrorDeRuntime(
            f"el contenedor ejecuto la imagen {id_observado} y el runtime fijado por "
            f"Task/024 es {id_esperado}"
        )
