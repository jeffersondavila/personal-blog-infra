#!/usr/bin/env python3
"""Guardas *fail-closed* del destino de una operacion de infraestructura.

Por que existe
--------------
El fallo mas caro posible del laboratorio es que un `terraform apply` —o peor,
un `terraform destroy`— pensado para el emulador local acabe hablando con **AWS
real** porque falto un endpoint. `aws-local-parity.md` §9.3 lo registra como
riesgo **R-24** y exige guardas G-01 a G-05 antes del primer `apply`.

`AWS_ACCESS_KEY_ID=test` **no es** una guarda: el SDK y el provider resuelven
credenciales y endpoints por una cadena de fuentes —variables, perfiles,
`credential_process`, SSO, *web identity*, metadata de instancia, proxies—, y
cualquiera de ellas puede introducir un destino real sin que el comando lo diga.

De ahi la forma de este modulo: **no** comprueba que el destino *parezca*
correcto; exige que **cada** via por la que podria colarse un destino real este
explicitamente ausente o explicitamente apuntando al laboratorio. Lo que no se
puede demostrar, aborta.

Principios
----------
1. **Sin valor por omision.** Modo, region y los ocho endpoints son
   obligatorios. Ausencia = abortar, nunca «continuar con lo razonable».
2. **`production` se rechaza aqui.** Mientras `Task/025` no este aprobada no
   existe autorizacion de AWS real, asi que el modo se reconoce —para poder
   rechazarlo con un mensaje claro— pero no se ejecuta.
3. **Nunca se imprime un valor recibido del entorno.** Un mensaje de error que
   incluyera la credencial la publicaria en el log que se adjunta al reporte.
4. **El entorno del hijo se construye, no se hereda.** `entorno_para_terraform`
   parte de una *allowlist*: lo que no esta nombrado, no llega.
5. **La identidad se comprueba contra el servicio**, no se supone: `000000000000`
   es la expectativa, y se verifica preguntando.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Final
from urllib.parse import urlsplit

#: Modos reconocidos. `production` se reconoce **para rechazarlo** (principio 2).
MODOS: Final = ("local", "production")

#: Region del laboratorio. Coincide con la de por omision del emulador.
REGION_DEL_LABORATORIO: Final = "us-east-1"

#: Cuenta ficticia que el emulador atribuye a una clave que no son 12 digitos.
CUENTA_DEL_LABORATORIO: Final = "000000000000"

#: Credenciales ficticias exactas. Su valor es publico por diseno: no protegen
#: nada y no pueden coincidir con una credencial real (S-04, S-05).
CLAVE_FICTICIA: Final = "test"
SECRETO_FICTICIO: Final = "test"

#: Servicios cuyo endpoint local es **obligatorio**. Son los de ADR-003 mas STS,
#: que es el que responde a la comprobacion de identidad.
SERVICIOS: Final = (
    "apigatewayv2",
    "cloudwatch",
    "iam",
    "lambda",
    "logs",
    "s3",
    "ssm",
    "sts",
)

#: Prefijo de las variables que declaran cada endpoint del laboratorio.
PREFIJO_DE_ENDPOINT: Final = "LAB_ENDPOINT_"

#: Anfitriones aceptables para un endpoint local. `internal` de Docker no entra:
#: el ejecutor corre en el host y habla con el puerto publicado en loopback.
ANFITRIONES_LOCALES: Final = frozenset({"127.0.0.1", "localhost", "::1"})

#: Esquemas aceptables.
ESQUEMAS: Final = frozenset({"http", "https"})

#: Variables que introducirian una identidad AWS distinta de la ficticia. Su
#: mera presencia aborta: no se intenta interpretar su valor.
VARIABLES_PROHIBIDAS: Final = (
    # Credenciales temporales y perfiles.
    "AWS_SESSION_TOKEN",
    "AWS_SECURITY_TOKEN",
    "AWS_PROFILE",
    "AWS_DEFAULT_PROFILE",
    # Archivos de configuracion: pueden traer `credential_process` y SSO.
    "AWS_SHARED_CREDENTIALS_FILE",
    "AWS_CONFIG_FILE",
    # Web identity / OIDC.
    "AWS_WEB_IDENTITY_TOKEN_FILE",
    "AWS_ROLE_ARN",
    "AWS_ROLE_SESSION_NAME",
    # Proveedor de credenciales de contenedor (ECS, EKS).
    "AWS_CONTAINER_CREDENTIALS_FULL_URI",
    "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI",
    "AWS_CONTAINER_AUTHORIZATION_TOKEN",
    "AWS_CONTAINER_AUTHORIZATION_TOKEN_FILE",
    # Metadata de instancia: otra via de credenciales reales.
    "AWS_EC2_METADATA_SERVICE_ENDPOINT",
    "AWS_EC2_METADATA_SERVICE_ENDPOINT_MODE",
    # Proxies: reenviarian la peticion a un destino que no controlamos.
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    # Overrides heredados de Terraform: podrian cambiar argumentos y backend.
    "TF_CLI_ARGS",
    "TF_CLI_CONFIG_FILE",
)

#: Prefijos prohibidos: cubren las variantes por comando de `TF_CLI_ARGS_*`.
PREFIJOS_PROHIBIDOS: Final = ("TF_CLI_ARGS_",)

#: Variables del host que el proceso hijo **si** hereda, por plataforma. Sin
#: ellas Terraform no encuentra su cache, su temporal ni el interprete.
HERENCIA_COMUN: Final = ("PATH", "TMPDIR", "TEMP", "TMP")
HERENCIA_WINDOWS: Final = (
    "SystemRoot",
    "SYSTEMROOT",
    "windir",
    "ComSpec",
    "PATHEXT",
    "APPDATA",
    "LOCALAPPDATA",
    "USERPROFILE",
    "HOMEDRIVE",
    "HOMEPATH",
    "NUMBER_OF_PROCESSORS",
    "PROCESSOR_ARCHITECTURE",
)
HERENCIA_POSIX: Final = ("HOME", "USER", "LANG", "LC_ALL")


class ErrorDeDestino(RuntimeError):
    """El destino no se puede demostrar seguro. La operacion no se ejecuta."""


@dataclass(frozen=True)
class Destino:
    """Destino validado de una operacion de infraestructura."""

    modo: str
    region: str
    endpoints: Mapping[str, str]
    cuenta_esperada: str

    @property
    def es_local(self) -> bool:
        return self.modo == "local"


def _presente(entorno: Mapping[str, str], nombre: str) -> bool:
    """Una variable cuenta como presente si existe y no esta vacia."""
    return bool((entorno.get(nombre) or "").strip())


def _validar_endpoint(servicio: str, valor: str) -> str:
    """Comprueba que el endpoint apunta inequivocamente al laboratorio local.

    Se validan esquema, anfitrion, puerto y ausencia de `userinfo`. Un endpoint
    sin puerto explicito se rechaza a proposito: `http://127.0.0.1` es ambiguo
    —resolveria al 80— y la ambiguedad es justo lo que esta guarda elimina.
    """
    partes = urlsplit(valor)
    if partes.scheme not in ESQUEMAS:
        raise ErrorDeDestino(
            f"el endpoint de '{servicio}' no declara un esquema http o https: "
            f"'{partes.scheme or valor}'"
        )
    if partes.username or partes.password:
        raise ErrorDeDestino(
            f"el endpoint de '{servicio}' incluye credenciales en la URL; "
            "no se admite userinfo"
        )
    anfitrion = (partes.hostname or "").lower()
    if not anfitrion:
        raise ErrorDeDestino(f"el endpoint de '{servicio}' no declara anfitrion")
    if anfitrion not in ANFITRIONES_LOCALES:
        raise ErrorDeDestino(
            f"el endpoint de '{servicio}' apunta a '{anfitrion}', que no es un "
            f"anfitrion local permitido {sorted(ANFITRIONES_LOCALES)}"
        )
    try:
        puerto = partes.port
    except ValueError as error:  # puerto no numerico
        raise ErrorDeDestino(f"el endpoint de '{servicio}' declara un puerto invalido") from error
    if puerto is None:
        raise ErrorDeDestino(
            f"el endpoint de '{servicio}' no declara puerto explicito; "
            "un endpoint implicito no es un destino demostrado"
        )
    if partes.path not in ("", "/"):
        raise ErrorDeDestino(f"el endpoint de '{servicio}' declara una ruta: '{partes.path}'")
    return valor


def _validar_ausencias(entorno: Mapping[str, str]) -> None:
    """Exige que ninguna via alternativa de credenciales o destino este activa."""
    for nombre in VARIABLES_PROHIBIDAS:
        if _presente(entorno, nombre):
            raise ErrorDeDestino(
                f"la variable '{nombre}' esta definida en el entorno; podria "
                "introducir un destino o una identidad distintos del laboratorio. "
                "Su valor no se muestra."
            )
    for nombre in entorno:
        if any(nombre.startswith(prefijo) for prefijo in PREFIJOS_PROHIBIDOS):
            raise ErrorDeDestino(
                f"la variable '{nombre}' esta definida en el entorno y podria "
                "alterar los argumentos de Terraform. Su valor no se muestra."
            )


def _validar_metadata(entorno: Mapping[str, str]) -> None:
    """`AWS_EC2_METADATA_DISABLED` debe valer exactamente `true`.

    La variable es solo una de las dos capas: el perimetro de red del
    laboratorio tambien bloquea el rango *link-local*. Confiar unicamente en la
    variable dejaria la proteccion en manos de quien exporta el entorno.
    """
    valor = entorno.get("AWS_EC2_METADATA_DISABLED")
    if valor != "true":
        raise ErrorDeDestino(
            "AWS_EC2_METADATA_DISABLED debe valer exactamente 'true' para "
            "impedir que el SDK busque credenciales en la metadata de instancia"
        )


def _validar_credenciales(entorno: Mapping[str, str]) -> None:
    """Exige las credenciales ficticias exactas, sin revelar lo recibido."""
    if entorno.get("AWS_ACCESS_KEY_ID") != CLAVE_FICTICIA:
        raise ErrorDeDestino(
            "AWS_ACCESS_KEY_ID no es la credencial ficticia esperada del "
            "laboratorio; el valor recibido no se muestra"
        )
    if entorno.get("AWS_SECRET_ACCESS_KEY") != SECRETO_FICTICIO:
        raise ErrorDeDestino(
            "AWS_SECRET_ACCESS_KEY no es la credencial ficticia esperada del "
            "laboratorio; el valor recibido no se muestra"
        )


def _validar_region(entorno: Mapping[str, str]) -> str:
    """La region se declara y debe coincidir en las dos variables que la fijan."""
    region = entorno.get("AWS_REGION")
    if not region:
        raise ErrorDeDestino("AWS_REGION no esta declarada")
    if region != REGION_DEL_LABORATORIO:
        raise ErrorDeDestino(
            f"AWS_REGION vale '{region}' y el laboratorio opera en "
            f"'{REGION_DEL_LABORATORIO}'"
        )
    por_defecto = entorno.get("AWS_DEFAULT_REGION")
    if por_defecto and por_defecto != REGION_DEL_LABORATORIO:
        raise ErrorDeDestino(
            f"AWS_DEFAULT_REGION vale '{por_defecto}' y discrepa de AWS_REGION"
        )
    return region


def _validar_overrides_de_endpoint(entorno: Mapping[str, str]) -> None:
    """`AWS_ENDPOINT_URL*` actua como override global: si existe, debe ser local.

    No se prohibe —es la forma estandar de apuntar un SDK al emulador, y el
    propio proyecto la usa para inspeccionar—, pero apuntando a AWS seria
    exactamente el accidente que esta guarda evita.
    """
    for nombre, valor in entorno.items():
        if not nombre.startswith("AWS_ENDPOINT_URL"):
            continue
        if not (valor or "").strip():
            continue
        _validar_endpoint(nombre, valor)


def resolver_destino(
    entorno: Mapping[str, str],
    *,
    modo: str | None,
    produccion_autorizada: bool = False,
) -> Destino:
    """Resuelve y valida el destino, o aborta.

    `produccion_autorizada` existe para que la firma no tenga que cambiar el dia
    que una tarea futura reciba autorizacion explicita de AWS real. **Hoy nadie
    la activa**: `Task/025` no tiene esa autorizacion y el valor por omision es
    el unico que se usa.
    """
    if modo is None or not modo.strip():
        raise ErrorDeDestino(
            "no se declaro el modo del destino; los valores admitidos son "
            f"{list(MODOS)} y no existe un valor por omision"
        )
    if modo not in MODOS:
        raise ErrorDeDestino(
            f"modo '{modo}' desconocido; los valores admitidos son {list(MODOS)}"
        )
    if modo == "production":
        if not produccion_autorizada:
            raise ErrorDeDestino(
                "el modo 'production' esta rechazado: no existe autorizacion "
                "para actuar sobre AWS real. La ETAPA 08 opera con cero "
                "recursos AWS reales (ADR-006, limite 10)"
            )
        raise ErrorDeDestino(
            "el modo 'production' no esta implementado en este lanzador; su "
            "materializacion pertenece a la ETAPA 10"
        )

    _validar_ausencias(entorno)
    _validar_metadata(entorno)
    _validar_credenciales(entorno)
    region = _validar_region(entorno)
    _validar_overrides_de_endpoint(entorno)

    endpoints: dict[str, str] = {}
    faltantes: list[str] = []
    for servicio in SERVICIOS:
        valor = (entorno.get(PREFIJO_DE_ENDPOINT + servicio.upper()) or "").strip()
        if not valor:
            faltantes.append(servicio)
            continue
        endpoints[servicio] = _validar_endpoint(servicio, valor)
    if faltantes:
        raise ErrorDeDestino(
            "faltan endpoints locales obligatorios: " + ", ".join(sorted(faltantes))
        )

    return Destino(
        modo=modo,
        region=region,
        endpoints=endpoints,
        cuenta_esperada=CUENTA_DEL_LABORATORIO,
    )


def entorno_para_terraform(
    destino: Destino,
    *,
    entorno: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Entorno del proceso hijo, construido desde una *allowlist*.

    Se construye en lugar de heredarse: un `AWS_PROFILE` o un `HTTPS_PROXY` del
    host no llegan a Terraform porque nunca se copian, no porque se hayan
    borrado. Los endpoints **no** viajan aqui: se pasan como variables de
    Terraform, de modo que el destino quede escrito en el plan y sea auditable.
    """
    origen = dict(os.environ if entorno is None else entorno)
    nombres = list(HERENCIA_COMUN)
    nombres += HERENCIA_WINDOWS if os.name == "nt" else HERENCIA_POSIX
    hijo = {nombre: origen[nombre] for nombre in nombres if origen.get(nombre)}
    hijo.update(
        {
            "AWS_ACCESS_KEY_ID": CLAVE_FICTICIA,
            "AWS_SECRET_ACCESS_KEY": SECRETO_FICTICIO,
            "AWS_REGION": destino.region,
            "AWS_DEFAULT_REGION": destino.region,
            "AWS_EC2_METADATA_DISABLED": "true",
            # Terraform desatendido: sin preguntas y sin telemetria de version.
            "TF_IN_AUTOMATION": "1",
            "TF_INPUT": "0",
            "CHECKPOINT_DISABLE": "1",
        }
    )
    return hijo


def confirmar_identidad(
    destino: Destino,
    consultar_cuenta: Callable[[Destino], str],
) -> str:
    """Comprueba la identidad **preguntando**, no suponiendo (guarda G-03).

    `consultar_cuenta` se inyecta para que los controles negativos puedan
    ejercitar la discrepancia sin abrir ningun socket.
    """
    observada = (consultar_cuenta(destino) or "").strip()
    if not observada:
        raise ErrorDeDestino(
            "la consulta de identidad no devolvio ninguna cuenta; sin identidad "
            "demostrada no se ejecuta ninguna operacion"
        )
    if observada != destino.cuenta_esperada:
        raise ErrorDeDestino(
            f"la cuenta observada es '{observada}' y se esperaba "
            f"'{destino.cuenta_esperada}'; el destino no es el laboratorio"
        )
    return observada


@contextmanager
def lock_de_escritura(ruta: Path):
    """Garantiza **una sola operacion escritora** sobre el laboratorio.

    El backend local de Terraform ya bloquea su propio estado, pero el ciclo
    toca ademas Docker, el emulador y el artefacto: dos ejecuciones simultaneas
    se pisarian fuera del alcance de ese bloqueo. `O_EXCL` es la primitiva
    correcta aqui —la creacion es atomica en Windows y en POSIX— y el archivo se
    retira al salir, tambien si la operacion falla.
    """
    ruta.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(ruta, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise ErrorDeDestino(
            f"ya hay una operacion del laboratorio en curso ({ruta}); "
            "solo se admite una operacion escritora a la vez"
        ) from error
    try:
        os.write(descriptor, f"pid={os.getpid()}\n".encode("ascii"))
        os.close(descriptor)
        yield ruta
    finally:
        try:
            ruta.unlink()
        except FileNotFoundError:
            pass
