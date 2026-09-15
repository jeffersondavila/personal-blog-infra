#!/usr/bin/env python3
"""Revision del plan, idempotencia y verificacion de ausencia.

Por que existe
--------------
Tres afirmaciones que parecen evidencia y no lo son:

1. **«`terraform apply` devolvio 0»** no dice *que* se creo. Un plan puede
   contener un recurso que nadie pidio —o una destruccion no prevista— y aplicar
   correctamente. Por eso el plan se revisa contra una lista cerrada de tipos y
   acciones antes de aplicarlo.
2. **«`terraform state list` esta vacio»** no demuestra que se destruyo nada:
   demuestra que el **estado** esta vacio, que es exactamente lo que pasaria si
   alguien borrara el estado sin destruir. La ausencia se comprueba preguntando a
   las APIs del destino.
3. **«el emulador ya no esta»** no demuestra que el `destroy` funcionara. Eliminar
   el laboratorio antes de comprobar la ausencia no es evidencia: es borrar al
   testigo.

Este modulo es deliberadamente puro: recibe estructuras ya obtenidas y decide.
Quien habla con Docker o con el emulador es `laboratorio.py`, y asi los controles
negativos se ejercitan sin red.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final

#: Tipos de recurso que esta tarea puede crear. Lista **cerrada**: cualquier otro
#: tipo en el plan aborta, que es como se detecta que el grafo crecio sin que una
#: decision lo autorizara. En particular no hay ningun `aws_db_*` ni `aws_rds_*`:
#: ADR-007 situa PostgreSQL en un VPS externo y `Task/025` no crea RDS.
TIPOS_PREVISTOS: Final = frozenset(
    {
        # S3 — bucket de medios
        "aws_s3_bucket",
        "aws_s3_bucket_public_access_block",
        "aws_s3_bucket_ownership_controls",
        "aws_s3_bucket_versioning",
        "aws_s3_bucket_cors_configuration",
        "aws_s3_bucket_policy",
        "aws_s3_bucket_lifecycle_configuration",
        "aws_s3_bucket_server_side_encryption_configuration",
        # SSM — parametros de configuracion
        "aws_ssm_parameter",
        # IAM — rol de ejecucion de la funcion
        "aws_iam_role",
        "aws_iam_role_policy",
        # CloudWatch — grupo de logs
        "aws_cloudwatch_log_group",
        # Lambda
        "aws_lambda_function",
        "aws_lambda_permission",
        # API Gateway HTTP API (v2)
        "aws_apigatewayv2_api",
        "aws_apigatewayv2_integration",
        "aws_apigatewayv2_route",
        "aws_apigatewayv2_stage",
    }
)

#: Acciones que nunca son aceptables en este laboratorio, se pidan donde se pidan.
ACCIONES_SIEMPRE_PROHIBIDAS: Final = frozenset({"forget"})


class ErrorDeInventario(RuntimeError):
    """El plan, la idempotencia o la ausencia de recursos no son demostrables."""


def revisar_plan(
    plan: Mapping[str, Any],
    *,
    acciones_permitidas: Sequence[str],
    minimo: int = 0,
) -> dict[str, int]:
    """Comprueba que el plan solo contiene lo previsto y resume sus acciones.

    `no-op` se ignora: Terraform lo emite para recursos que no cambian y no es un
    cambio. Un reemplazo llega como `["delete", "create"]`; si `delete` no esta
    permitido, aborta — que es lo correcto en el primer `apply`, donde una
    destruccion no tiene explicacion posible.
    """
    if "resource_changes" not in plan:
        raise ErrorDeInventario(
            "el plan no contiene 'resource_changes'; no se puede demostrar que "
            "se reviso su contenido"
        )
    cambios = plan["resource_changes"]
    if not isinstance(cambios, list):
        raise ErrorDeInventario("'resource_changes' no es una lista")

    permitidas = set(acciones_permitidas)
    resumen: dict[str, int] = {accion: 0 for accion in permitidas}
    tipos_inesperados: set[str] = set()
    acciones_inesperadas: set[str] = set()
    total = 0
    datos_leidos = 0

    for cambio in cambios:
        if not isinstance(cambio, Mapping):
            raise ErrorDeInventario("una entrada de 'resource_changes' no es un objeto")
        tipo = cambio.get("type")
        direccion = cambio.get("address")
        detalle = cambio.get("change")
        if not tipo or not direccion or not isinstance(detalle, Mapping):
            raise ErrorDeInventario(
                f"entrada de plan incompleta: {dict(cambio) or '{}'}"
            )
        acciones = detalle.get("actions")
        if not isinstance(acciones, list) or not acciones:
            raise ErrorDeInventario(f"'{direccion}' no declara acciones legibles")
        if acciones == ["no-op"]:
            continue

        # Un data source LEE: no crea, no cambia y no destruye. Terraform lo
        # emite aqui con `mode: "data"` y accion `read`. Juzgarlo contra la lista
        # de tipos GESTIONADOS lo rechazaria sin motivo: `aws_iam_policy_document`
        # es la forma canonica de escribir una politica y no materializa nada.
        #
        # Omitir `mode` no es una via de escape: por omision se trata como
        # gestionado, que es el lado seguro.
        if cambio.get("mode") == "data":
            if set(acciones) - {"read"}:
                raise ErrorDeInventario(
                    f"el data source '{direccion}' declara acciones distintas de "
                    f"'read': {acciones}"
                )
            datos_leidos += 1
            continue

        if tipo not in TIPOS_PREVISTOS:
            tipos_inesperados.add(f"{tipo} ({direccion})")
        for accion in acciones:
            if accion in ACCIONES_SIEMPRE_PROHIBIDAS or accion not in permitidas:
                acciones_inesperadas.add(f"{accion} en {direccion}")
            else:
                resumen[accion] = resumen.get(accion, 0) + 1
                total += 1

    if tipos_inesperados:
        raise ErrorDeInventario(
            "el plan contiene tipos de recurso no previstos por esta tarea: "
            + ", ".join(sorted(tipos_inesperados))
        )
    if acciones_inesperadas:
        raise ErrorDeInventario(
            "el plan contiene acciones no permitidas (se admiten "
            f"{sorted(permitidas)}): " + ", ".join(sorted(acciones_inesperadas))
        )
    if total < minimo:
        raise ErrorDeInventario(
            f"el plan declara {total} cambios y se esperaban al menos {minimo}"
        )
    if datos_leidos:
        resumen["read"] = datos_leidos
    return resumen


@dataclass(frozen=True)
class DiferenciaDelDestino:
    """Diferencia permanente causada por el DESTINO, no por la configuracion.

    Se declara por tipo de recurso Y por atributo, con su motivo. Es
    deliberadamente estrecha: una tolerancia por tipo entero dejaria pasar
    cualquier cambio de ese recurso, que es justo lo que el gate debe detectar.
    """

    tipo: str
    atributo: str
    motivo: str


def _atributos_que_cambian(antes: Any, despues: Any) -> set[str]:
    """Atributos de primer nivel cuyo valor difiere entre `before` y `after`."""
    antes = antes if isinstance(antes, Mapping) else {}
    despues = despues if isinstance(despues, Mapping) else {}
    nombres = set(antes) | set(despues)
    return {nombre for nombre in nombres if antes.get(nombre) != despues.get(nombre)}


def exigir_sin_cambios(
    codigo_de_salida: int,
    *,
    plan: Mapping[str, Any] | None = None,
    diferencias_toleradas: Sequence[DiferenciaDelDestino] = (),
) -> dict[str, int]:
    """Gate de idempotencia sobre `terraform plan -detailed-exitcode`.

    Los codigos son parte del contrato de Terraform: 0 = sin cambios, 1 = error,
    2 = hay cambios. Un 2 despues de un `apply` correcto significa que la
    configuracion no converge.

    Por que existe `diferencias_toleradas`, y por que es tan estrecha
    -----------------------------------------------------------------
    Un emulador puede **no saber representar** un atributo. Cuando eso ocurre, el
    plan nunca converge por un motivo que no esta en la configuracion y que
    desapareceria contra AWS real.

    La respuesta facil seria poner `ignore_changes` en el modulo. Se rechaza a
    proposito: eso viajaria a produccion y silenciaria un *drift* REAL de un
    atributo que AWS si sabe representar. Es exactamente el acoplamiento al
    emulador que prohibe ADR-006 (limite 2) y que vigila el riesgo R-26.

    Asi que la tolerancia vive **aqui, en el verificador del laboratorio**, y no
    en la infraestructura. Se declara por tipo y atributo concretos, obliga a un
    motivo, y **cualquier** otro cambio —una creacion, una destruccion, otro
    atributo— sigue abortando. El resultado se informa como «idempotente salvo la
    diferencia documentada», nunca como idempotente sin mas.
    """
    if codigo_de_salida == 0:
        return {}
    if codigo_de_salida != 2:
        raise ErrorDeInventario(
            f"el segundo plan devolvio {codigo_de_salida}: la comprobacion de "
            "idempotencia no pudo completarse"
        )
    if plan is None or not diferencias_toleradas:
        raise ErrorDeInventario(
            "el segundo plan devolvio 2: quedan cambios pendientes despues de "
            "un apply correcto, asi que la configuracion no es idempotente"
        )

    permitidos = {(d.tipo, d.atributo) for d in diferencias_toleradas}
    informe: dict[str, int] = {}
    sin_justificar: set[str] = set()

    for cambio in plan.get("resource_changes", []):
        detalle = cambio.get("change") or {}
        acciones = [a for a in detalle.get("actions", []) if a != "no-op"]
        if not acciones:
            continue
        if cambio.get("mode") == "data":
            continue
        direccion = cambio.get("address", "?")
        tipo = cambio.get("type", "?")
        if set(acciones) != {"update"}:
            sin_justificar.add(f"{','.join(acciones)} en {direccion}")
            continue
        for atributo in _atributos_que_cambian(detalle.get("before"), detalle.get("after")):
            if (tipo, atributo) in permitidos:
                clave = f"{tipo}.{atributo}"
                informe[clave] = informe.get(clave, 0) + 1
            else:
                sin_justificar.add(f"{tipo}.{atributo} en {direccion}")

    if sin_justificar:
        raise ErrorDeInventario(
            "el segundo plan devolvio 2 con cambios que NO estan justificados "
            "como diferencia del destino: " + ", ".join(sorted(sin_justificar))
        )
    if not informe:
        raise ErrorDeInventario(
            "el segundo plan devolvio 2 pero no se pudo identificar que cambia; "
            "no se acepta sin poder nombrarlo"
        )
    return informe


def _describir_residuos(inventario: Mapping[str, Iterable[str]]) -> list[str]:
    residuos = []
    for servicio in sorted(inventario):
        for elemento in sorted(inventario[servicio]):
            residuos.append(f"{servicio}: {elemento}")
    return residuos


def exigir_inventario_vacio(inventario: Mapping[str, Iterable[str]]) -> None:
    """Exige que las APIs del destino no devuelvan ningun recurso del proyecto."""
    if not inventario:
        raise ErrorDeInventario(
            "el inventario no cubre ningun servicio; un inventario vacio no "
            "demuestra ausencia, demuestra que no se miro"
        )
    residuos = _describir_residuos(inventario)
    if residuos:
        raise ErrorDeInventario(
            "el destroy no elimino todo; siguen presentes: " + ", ".join(residuos)
        )


def exigir_laboratorio_limpio(residuos: Mapping[str, Iterable[str]]) -> None:
    """Exige que no queden contenedores, redes ni volumenes del laboratorio."""
    if not residuos:
        raise ErrorDeInventario(
            "no se inspecciono ninguna categoria de residuo del laboratorio"
        )
    pendientes = _describir_residuos(residuos)
    if pendientes:
        raise ErrorDeInventario(
            "quedan residuos del laboratorio: " + ", ".join(pendientes)
        )
