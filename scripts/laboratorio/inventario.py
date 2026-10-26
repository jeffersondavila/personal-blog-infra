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

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from typing import Any, Final

#: Tipos de recurso que el laboratorio puede crear. Lista **cerrada**: cualquier
#: otro tipo en el plan aborta, que es como se detecta que el grafo crecio sin que
#: una decision lo autorizara.
#:
#: Task/031 (H-031-1, DH-1) anade los del root de datos —red privada y RDS de
#: ADR-010— y nada mas: ni Internet Gateway, ni NAT, ni Elastic IP, ni RDS Proxy,
#: ni `aws_db_cluster`, ni claves KMS. Si alguno aparece, el plan aborta. Tampoco
#: `aws_default_security_group`: H-031-1A decidio NO gestionar el grupo por omision.
TIPOS_PREVISTOS: Final = frozenset(
    {
        # Red privada — root de datos (Task/031)
        "aws_vpc",
        "aws_subnet",
        "aws_route_table",
        "aws_route_table_association",
        "aws_vpc_endpoint",
        "aws_security_group",
        "aws_vpc_security_group_ingress_rule",
        "aws_vpc_security_group_egress_rule",
        # RDS PostgreSQL — root de datos (Task/031)
        "aws_db_subnet_group",
        "aws_db_parameter_group",
        "aws_db_instance",
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
        # Alarmas ya incorporadas al root de datos por H-031-8; sin EventBridge ni tipos adicionales.
        "aws_cloudwatch_metric_alarm",
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


@dataclass(frozen=True)
class ActualizacionDependienteDelDrift:
    """Atributo exacto que Terraform recalcula por depender del objetivo.

    Solo se acepta cuando el valor posterior figura como desconocido en el
    plan. Esto no autoriza un cambio conocido de la misma politica ni una
    tolerancia amplia por tipo de recurso.
    """

    direccion: str
    tipo: str
    atributo: str


#: Formas de transicion que una entrada de `resource_drift` puede declarar. Cada
#: una fija el antes Y el despues de un atributo; no existe la forma «cualquier
#: cambio».
#:
#: - `nulo_a_lista_vacia`: antes `null`, despues `[]`, y en ese sentido.
#: - `lista_a_vacia`: antes una lista no vacia, despues `[]`: el destino acepto
#:   el valor y no lo devuelve.
#: - `agrega_reglas_separadas`: el `ingress`/`egress` de un grupo de seguridad
#:   pasa a mostrar, sin perder nada, EXACTAMENTE las reglas que gestionan aparte
#:   los `aws_vpc_security_group_*_rule` del mismo plan para ese grupo.
#: - `nulo_a_mapa_vacio`: antes `null`, despues `{}`, y en ese sentido.
#: - `refleja_politicas_en_linea`: el `inline_policy` de un rol pasa de `[]` a
#:   EXACTAMENTE las politicas en linea que el `prior_state` asigna a ese rol
#:   (`aws_iam_role_policy`), por nombre y contenido; ni una de mas ni de menos.
#:   Es la misma idea que `agrega_reglas_separadas`, para IAM (H-031-6).
FORMAS_DE_TRANSICION: Final = frozenset(
    {"nulo_a_lista_vacia", "lista_a_vacia", "agrega_reglas_separadas", "nulo_a_mapa_vacio",
     "refleja_politicas_en_linea", "instante_movil"}
)

#: `instante_movil` (mantenimiento de CI de Task/031, Floci 2.3.0): el MISMO contrato temporal que la convergencia
#: productiva aplica a `latest_restorable_time` (`scripts/terraform_datos/check_plan_refresh_instancia.py`,
#: enmienda de §40 aprobada el 2026-10-19): instantes ISO-8601 con zona, `antes` <= `despues` <= ahora y una
#: frescura de un dia como maximo. Se replica aqui porque el laboratorio no importa los paquetes `scripts.*`; una
#: prueba exige que los dos decidan igual. Solo para los atributos que AWS mueve por si mismo.
ATRIBUTOS_MOVILES: Final = frozenset({"latest_restorable_time"})
VENTANA_MOVIL: Final = timedelta(days=1)


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def _instante(valor: Any) -> datetime | None:
    if not isinstance(valor, str) or not valor:
        return None
    try:
        instante = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        return None
    return instante if instante.tzinfo is not None else None


def instante_movil_valido(anterior: Any, posterior: Any, ahora: datetime) -> bool:
    """`anterior` <= `posterior` <= `ahora` y `ahora - posterior` <= `VENTANA_MOVIL`, ambos instantes con zona."""
    a, b = _instante(anterior), _instante(posterior)
    return a is not None and b is not None and a <= b <= ahora and ahora - b <= VENTANA_MOVIL


@dataclass(frozen=True)
class DriftDelDestino:
    """Entrada de `resource_drift` que el laboratorio sabe explicar (H-031-1A).

    Mas estrecha que `DiferenciaDelDestino`, a proposito: se declara por
    DIRECCION, con las acciones exactas, el conjunto EXACTO de atributos que
    difieren y la forma de cada transicion. Un atributo de mas o de menos, otro
    valor u otra accion detienen el ciclo: comprobar solo que los atributos son
    un subconjunto de los declarados dejaria pasar combinaciones nunca
    observadas.
    """

    direccion: str
    tipo: str
    acciones: tuple[str, ...]
    transiciones: tuple[tuple[str, str], ...]
    motivo: str

    def __post_init__(self) -> None:
        if not self.acciones or not self.transiciones:
            raise ValueError(f"{self.direccion}: declara acciones y transiciones")
        nombres = [atributo for atributo, _ in self.transiciones]
        if len(nombres) != len(set(nombres)):
            raise ValueError(f"{self.direccion}: un atributo declarado dos veces")
        for atributo, forma in self.transiciones:
            if forma not in FORMAS_DE_TRANSICION:
                raise ValueError(f"{self.direccion}.{atributo}: forma desconocida '{forma}'")
            if forma == "agrega_reglas_separadas" and atributo not in ("ingress", "egress"):
                raise ValueError(f"{self.direccion}.{atributo}: no es una lista de reglas")
            if forma == "refleja_politicas_en_linea" and atributo != "inline_policy":
                raise ValueError(f"{self.direccion}.{atributo}: no es el reflejo de politicas en linea")
            if forma == "instante_movil" and atributo not in ATRIBUTOS_MOVILES:
                raise ValueError(f"{self.direccion}.{atributo}: no es un atributo movil aprobado")

    @property
    def atributos(self) -> frozenset[str]:
        return frozenset(atributo for atributo, _ in self.transiciones)


def _atributos_que_cambian(antes: Any, despues: Any) -> set[str]:
    """Atributos de primer nivel cuyo valor difiere entre `before` y `after`."""
    antes = antes if isinstance(antes, Mapping) else {}
    despues = despues if isinstance(despues, Mapping) else {}
    nombres = set(antes) | set(despues)
    return {nombre for nombre in nombres if antes.get(nombre) != despues.get(nombre)}


def _recursos_del_estado_previo(plan: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Recursos de `prior_state`, de todos los modulos."""
    previo = plan.get("prior_state") or {}
    pendientes = [((previo.get("values") or {}).get("root_module")) or {}]
    recursos: list[Mapping[str, Any]] = []
    while pendientes:
        modulo = pendientes.pop()
        if not isinstance(modulo, Mapping):
            continue
        recursos += [r for r in modulo.get("resources") or [] if isinstance(r, Mapping)]
        pendientes += list(modulo.get("child_modules") or [])
    return recursos


def _regla_en_linea(valores: Mapping[str, Any], id_del_grupo: str) -> str:
    """Una regla separada escrita como la representa `aws_security_group`."""
    referenciado = valores.get("referenced_security_group_id")
    protocolo = valores.get("ip_protocol")
    todos = protocolo == "-1"
    return _canonica(
        {
            "cidr_blocks": [valores["cidr_ipv4"]] if valores.get("cidr_ipv4") else [],
            "description": valores.get("description") or "",
            "from_port": 0 if todos else valores.get("from_port"),
            "ipv6_cidr_blocks": [valores["cidr_ipv6"]] if valores.get("cidr_ipv6") else [],
            "prefix_list_ids": (
                [valores["prefix_list_id"]] if valores.get("prefix_list_id") else []
            ),
            "protocol": protocolo,
            "security_groups": (
                [referenciado] if referenciado and referenciado != id_del_grupo else []
            ),
            "self": bool(referenciado) and referenciado == id_del_grupo,
            "to_port": 0 if todos else valores.get("to_port"),
        }
    )


def _canonica(valor: Any) -> str:
    return json.dumps(valor, sort_keys=True)


def _reglas_separadas(plan: Mapping[str, Any], id_del_grupo: str, sentido: str) -> Counter[str]:
    tipo = f"aws_vpc_security_group_{sentido}_rule"
    return Counter(
        _regla_en_linea(recurso.get("values") or {}, id_del_grupo)
        for recurso in _recursos_del_estado_previo(plan)
        if recurso.get("type") == tipo
        and recurso.get("mode", "managed") == "managed"
        and (recurso.get("values") or {}).get("security_group_id") == id_del_grupo
    )


def _politica_canonica(nombre: Any, documento: Any) -> str | None:
    """`(nombre, documento)` comparable, o None si el documento no es JSON valido."""
    try:
        return _canonica([nombre, json.loads(documento)])
    except (TypeError, ValueError):
        return None


def _politicas_en_linea_del_estado(plan: Mapping[str, Any], rol: str) -> Counter[str | None]:
    return Counter(
        _politica_canonica((recurso.get("values") or {}).get("name"), (recurso.get("values") or {}).get("policy"))
        for recurso in _recursos_del_estado_previo(plan)
        if recurso.get("type") == "aws_iam_role_policy"
        and recurso.get("mode", "managed") == "managed"
        and (recurso.get("values") or {}).get("role") == rol
    )


def _cumple_la_transicion(
    forma: str,
    atributo: str,
    antes: Mapping[str, Any],
    despues: Mapping[str, Any],
    plan: Mapping[str, Any],
    ahora: datetime | None = None,
) -> bool:
    valor_antes, valor_despues = antes.get(atributo), despues.get(atributo)
    if forma == "instante_movil":
        return atributo in ATRIBUTOS_MOVILES and instante_movil_valido(
            valor_antes, valor_despues, ahora or _ahora()
        )
    if forma == "nulo_a_lista_vacia":
        return atributo in antes and valor_antes is None and valor_despues == []
    if forma == "nulo_a_mapa_vacio":
        return atributo in antes and valor_antes is None and isinstance(valor_despues, dict) and not valor_despues
    if forma == "refleja_politicas_en_linea":
        rol = antes.get("name")
        if not rol or despues.get("name") != rol or valor_antes != [] or not isinstance(valor_despues, list):
            return False
        if not all(isinstance(p, Mapping) and set(p) == {"name", "policy"} for p in valor_despues):
            return False
        reflejo = Counter(_politica_canonica(p["name"], p["policy"]) for p in valor_despues)
        del_estado = _politicas_en_linea_del_estado(plan, rol)
        return bool(reflejo) and None not in reflejo and None not in del_estado and reflejo == del_estado
    if forma == "lista_a_vacia":
        return isinstance(valor_antes, list) and bool(valor_antes) and valor_despues == []
    if forma == "agrega_reglas_separadas":
        id_del_grupo = antes.get("id")
        if not id_del_grupo or despues.get("id") != id_del_grupo:
            return False
        if not isinstance(valor_antes, list) or not isinstance(valor_despues, list):
            return False
        previas = Counter(_canonica(regla) for regla in valor_antes)
        posteriores = Counter(_canonica(regla) for regla in valor_despues)
        agregadas = posteriores - previas
        return (
            not previas - posteriores
            and bool(agregadas)
            and agregadas == _reglas_separadas(plan, id_del_grupo, atributo)
        )
    return False


def revisar_drift(
    plan: Mapping[str, Any],
    *,
    drift_tolerado: Sequence[DriftDelDestino] = (),
    ahora: datetime | None = None,
) -> dict[str, list[str]]:
    """Exige que `resource_drift` contenga solo entradas declaradas, exactas.

    Existe por H-031-1A: el gate de idempotencia acotaba `resource_changes` y
    nunca leia esta seccion, asi que un drift no declarado pasaba por fuera —con
    `exit 2` justificado por otros cambios, o con `exit 0` sin mirar el plan—.
    Tambien exige `deferred_changes` vacio. Una seccion ausente equivale a vacia:
    Terraform la omite cuando no hay nada que contar.

    Devuelve, por direccion, los atributos que difieren. Cualquier cosa no
    declarada aborta, nombrandola.
    """
    if plan.get("deferred_changes"):
        raise ErrorDeInventario(
            "el plan contiene deferred_changes: no se puede demostrar que esta completo"
        )
    entradas = plan.get("resource_drift") or []
    if not isinstance(entradas, list):
        raise ErrorDeInventario("'resource_drift' no es una lista")

    declaradas: dict[str, DriftDelDestino] = {}
    for declarada in drift_tolerado:
        if declarada.direccion in declaradas:
            raise ErrorDeInventario(f"drift declarado dos veces: {declarada.direccion}")
        declaradas[declarada.direccion] = declarada

    informe: dict[str, list[str]] = {}
    sin_justificar: list[str] = []
    for entrada in entradas:
        if not isinstance(entrada, Mapping):
            sin_justificar.append("una entrada de resource_drift no es un objeto")
            continue
        direccion = str(entrada.get("address") or "?")
        tipo = str(entrada.get("type") or "?")
        detalle = entrada.get("change")
        if entrada.get("mode") != "managed" or not isinstance(detalle, Mapping):
            sin_justificar.append(f"entrada ilegible o no gestionada en {direccion}")
            continue
        if direccion in informe:
            sin_justificar.append(f"{direccion} aparece dos veces")
            continue
        declarada = declaradas.get(direccion)
        if declarada is None or declarada.tipo != tipo:
            sin_justificar.append(f"drift no declarado en {direccion} ({tipo})")
            continue
        acciones = detalle.get("actions")
        if not isinstance(acciones, list) or tuple(acciones) != declarada.acciones:
            sin_justificar.append(
                f"{direccion}: acciones {acciones}, declaradas {list(declarada.acciones)}"
            )
            continue
        antes, despues = detalle.get("before"), detalle.get("after")
        if not isinstance(antes, Mapping) or not isinstance(despues, Mapping):
            sin_justificar.append(f"{direccion}: before/after ilegibles")
            continue
        atributos = _atributos_que_cambian(antes, despues)
        informe[direccion] = sorted(atributos)
        if atributos != declarada.atributos:
            sin_justificar.append(
                f"{direccion}: difieren {sorted(atributos)} y se declararon "
                f"exactamente {sorted(declarada.atributos)}"
            )
            continue
        for atributo, forma in declarada.transiciones:
            if not _cumple_la_transicion(forma, atributo, antes, despues, plan, ahora):
                sin_justificar.append(
                    f"{direccion}: {atributo} no sigue la transicion declarada '{forma}'"
                )

    if sin_justificar:
        raise ErrorDeInventario(
            "resource_drift con diferencias NO declaradas como del destino: "
            + "; ".join(sorted(sin_justificar))
        )
    return informe


def exigir_sin_cambios(
    codigo_de_salida: int,
    *,
    plan: Mapping[str, Any] | None = None,
    diferencias_toleradas: Sequence[DiferenciaDelDestino] = (),
    drift_tolerado: Sequence[DriftDelDestino] = (),
    ahora: datetime | None = None,
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

    `resource_drift` (H-031-1A)
    ---------------------------
    Si recibe el plan, revisa SIEMPRE `resource_drift` y `deferred_changes`
    contra `drift_tolerado` —por omision vacio, asi que cualquier drift aborta—,
    tambien con `exit 0`: un `exit 0` puede venir con drift. Y un `exit 0` cuyo
    plan contiene cambios se contradice, asi que tambien aborta.
    """
    if codigo_de_salida not in (0, 2):
        raise ErrorDeInventario(
            f"el segundo plan devolvio {codigo_de_salida}: la comprobacion de "
            "idempotencia no pudo completarse"
        )
    if plan is not None:
        revisar_drift(plan, drift_tolerado=drift_tolerado, ahora=ahora)
    if codigo_de_salida == 0:
        if plan is not None:
            pendientes = sorted(
                str(cambio.get("address", "?"))
                for cambio in plan.get("resource_changes") or []
                if set((cambio.get("change") or {}).get("actions") or []) - {"no-op", "read"}
            )
            if pendientes:
                raise ErrorDeInventario(
                    "el segundo plan devolvio 0 pero su JSON contiene cambios: "
                    + ", ".join(pendientes)
                )
        return {}
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


def revisar_reconciliacion_de_drift(
    plan: Mapping[str, Any],
    *,
    direccion_objetivo: str,
    diferencias_toleradas: Sequence[DiferenciaDelDestino] = (),
    actualizaciones_dependientes: Sequence[ActualizacionDependienteDelDrift] = (),
) -> dict[str, Any]:
    """Exige que un plan repare un unico drift y nada mas.

    El objetivo debe reaparecer mediante ``create``. Fuera de el solo se
    toleran diferencias del destino declaradas por tipo y atributo, con la misma
    estrechez que el gate de idempotencia, y dependencias declaradas por
    direccion, tipo y atributo cuyo valor posterior sea desconocido. Una
    actualizacion de Lambda, otra creacion o cualquier destruccion abortan el
    ensayo.
    """
    cambios = plan.get("resource_changes")
    if not isinstance(cambios, list):
        raise ErrorDeInventario(
            "el plan de reconciliacion no contiene resource_changes legible"
        )
    permitidos = {(d.tipo, d.atributo) for d in diferencias_toleradas}
    dependencias_permitidas = {
        (d.direccion, d.tipo, d.atributo) for d in actualizaciones_dependientes
    }
    objetivo_recreado = False
    diferencias = 0
    dependencias = 0
    inesperados: set[str] = set()

    for cambio in cambios:
        if not isinstance(cambio, Mapping):
            inesperados.add("entrada de plan ilegible")
            continue
        direccion = str(cambio.get("address") or "?")
        tipo = str(cambio.get("type") or "?")
        detalle = cambio.get("change") or {}
        acciones = detalle.get("actions") or []
        if acciones == ["no-op"]:
            continue
        if cambio.get("mode") == "data" and set(acciones) == {"read"}:
            continue

        if direccion == direccion_objetivo:
            if tipo == "aws_ssm_parameter" and acciones == ["create"]:
                objetivo_recreado = True
            else:
                inesperados.add(
                    f"el objetivo usa {tipo} con acciones {acciones}"
                )
            continue

        if acciones != ["update"]:
            inesperados.add(f"{','.join(acciones) or '?'} en {direccion}")
            continue
        atributos = _atributos_que_cambian(
            detalle.get("before"), detalle.get("after")
        )
        posteriores_desconocidos = detalle.get("after_unknown") or {}
        if not atributos:
            inesperados.add(f"actualizacion sin atributos demostrables en {direccion}")
            continue
        for atributo in atributos:
            if (tipo, atributo) in permitidos:
                diferencias += 1
            elif (
                (direccion, tipo, atributo) in dependencias_permitidas
                and isinstance(posteriores_desconocidos, Mapping)
                and posteriores_desconocidos.get(atributo) is True
            ):
                dependencias += 1
            else:
                inesperados.add(f"{tipo}.{atributo} en {direccion}")

    if not objetivo_recreado:
        inesperados.add(f"no se recrea el objetivo {direccion_objetivo}")
    if inesperados:
        raise ErrorDeInventario(
            "el plan no es una reconciliacion de drift acotada: "
            + ", ".join(sorted(inesperados))
        )
    return {
        "objetivo_recreado": direccion_objetivo,
        "diferencias_del_destino": diferencias,
        "actualizaciones_dependientes": dependencias,
    }


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
