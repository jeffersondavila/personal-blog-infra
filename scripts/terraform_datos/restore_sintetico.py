"""Restore sintetico con PITR de H-031-7 (Task/031; D-10 §10 y §9.2 de las decisiones de RDS).

Demuestra recuperacion real con datos SINTETICOS: un marcador no sensible en la productiva, PITR a una instancia
TEMPORAL, la misma huella leida en la restaurada, tiempos medidos y limpieza guardada de lo temporal. Cada fase es
un subcomando y deja constancia en un manifiesto local sin host, cuenta ni ARN:

  preflight   solo lectura: productiva disponible, con backups (retencion >= 1), PITR al dia, cifrada y privada;
              ninguna temporal previa.
  sembrar     marcador por la ejecutora (modo `sintetico`, con `blog_migrate`): id, instante, huella y t0.
  restaurar   REGISTRA el identificador exacto antes de crear; espera a que LatestRestorableTime cubra t0 con margen;
              restaura una instancia privada, Single-AZ, misma clase, mismo subnet group, SOLO el grupo de RDS, sin
              backups, sin exportar logs (un grupo de logs nuevo naceria con retencion infinita) y sin proteccion de
              borrado, etiquetada como temporal; espera `available` y relee. Si la API RECHAZA el restore (HTTP 4xx
              con codigo, p. ej. `FreeTierRestrictionError`), registra el rechazo como definitivo y nunca lo repite.
  verificar   la ejecutora lee el marcador en la restaurada y exige la misma huella.
  limpiar     solo la temporal registrada por ESTA corrida, etiquetada como temporal y distinta de la productiva:
              lista lo que se elimina, borra sin snapshot final ni backups, demuestra la ausencia por API y que la
              productiva sigue intacta, y retira el marcador de la productiva.
  informe     RPO y RTO observados frente a los objetivos de D-10 (15 minutos y 4 horas).

Nunca modifica ni borra la productiva: el unico borrado es el de la temporal, por identificador, recurso y etiquetas.
Uso: python -m scripts.terraform_datos.restore_sintetico <fase> [--identificador ...] --manifiesto <ruta.json>
"""
import argparse
import datetime as dt
import json
import re
import time
import uuid
from pathlib import Path

from scripts.terraform_datos import operar_ejecutora as operador

PRODUCTIVA = "blog-prod-postgres"
PATRON_TEMPORAL = re.compile(r"blog-prod-restore-h0317-[0-9]{14}")
_CODIGO_DE_AWS = re.compile(r"[A-Za-z][A-Za-z0-9.]{0,99}")
PROPOSITO = "restore-sintetico-H-031-7"
MARGEN = dt.timedelta(seconds=60)
OBJETIVO_RPO_S, OBJETIVO_RTO_S = 15 * 60, 4 * 60 * 60
ESPERA_PITR_S, ESPERA_DISPONIBLE_S, ESPERA_BORRADO_S, INTERVALO_S = 1800, 5400, 3600, 30
FORMATO = "%Y-%m-%dT%H:%M:%SZ"
ETIQUETAS = (("Proyecto", "personal-blog"), ("Entorno", "produccion"), ("Gestion", "manual-H-031-7"),
             ("Componente", "datos"), ("Tarea", "Task/031"), ("Proposito", PROPOSITO), ("Temporal", "true"))

RELOJ = lambda: dt.datetime.now(dt.timezone.utc)  # noqa: E731
DORMIR = time.sleep
Abortar = operador.Abortar


def _texto(instante):
    return instante.strftime(FORMATO)


def _instante(texto):
    return dt.datetime.strptime(texto, FORMATO).replace(tzinfo=dt.timezone.utc)


def _clientes():
    """Los MISMOS clientes que el operador: su cliente de Lambda no reintenta (D-24 modificada el 2026-10-18)."""
    return operador._clientes()


def _instancia(rds, identificador):
    """La descripcion de la instancia, o None si no existe."""
    try:
        return rds.describe_db_instances(DBInstanceIdentifier=identificador)["DBInstances"][0]
    except Exception as error:
        if ((getattr(error, "response", None) or {}).get("Error") or {}).get("Code") == "DBInstanceNotFound":
            return None
        raise


def _etiquetas(instancia):
    return {etiqueta["Key"]: etiqueta["Value"] for etiqueta in instancia.get("TagList") or []}


def _esperar(condicion, limite_s, fallo):
    limite = RELOJ() + dt.timedelta(seconds=limite_s)
    while True:
        resultado = condicion()
        if resultado:
            return resultado
        if RELOJ() >= limite:
            raise Abortar(fallo)
        DORMIR(INTERVALO_S)


def _leer(ruta):
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}


def _guardar(ruta, datos):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(".tmp")
    temporal.write_text(json.dumps(datos, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    temporal.replace(ruta)


def parametros(prod, identificador, instante):
    """Parametros EXACTOS del PITR a la temporal: la red y la configuracion de la productiva, nada publico ni
    persistente."""
    return {
        "SourceDBInstanceIdentifier": PRODUCTIVA, "TargetDBInstanceIdentifier": identificador, "RestoreTime": instante,
        "DBInstanceClass": prod["DBInstanceClass"], "DBSubnetGroupName": prod["DBSubnetGroup"]["DBSubnetGroupName"],
        "VpcSecurityGroupIds": [grupo["VpcSecurityGroupId"] for grupo in prod["VpcSecurityGroups"]],
        "DBParameterGroupName": prod["DBParameterGroups"][0]["DBParameterGroupName"],
        "StorageType": prod["StorageType"], "PubliclyAccessible": False, "MultiAZ": False, "BackupRetentionPeriod": 0,
        "EnableCloudwatchLogsExports": [], "DeletionProtection": False, "CopyTagsToSnapshot": False,
        "AutoMinorVersionUpgrade": False, "EnableIAMDatabaseAuthentication": False,
        "Tags": [{"Key": clave, "Value": valor} for clave, valor in ETIQUETAS] + [{"Key": "Name", "Value": identificador}],
    }


def _readback(temporal, prod):
    etiquetas = _etiquetas(temporal)
    return {
        "disponible": temporal["DBInstanceStatus"] == "available",
        "publica": temporal["PubliclyAccessible"],
        "cifrada": temporal["StorageEncrypted"],
        "mismos_grupos": sorted(g["VpcSecurityGroupId"] for g in temporal["VpcSecurityGroups"])
        == sorted(g["VpcSecurityGroupId"] for g in prod["VpcSecurityGroups"]),
        "mismo_subnet_group": temporal["DBSubnetGroup"]["DBSubnetGroupName"] == prod["DBSubnetGroup"]["DBSubnetGroupName"],
        "misma_clase": temporal["DBInstanceClass"] == prod["DBInstanceClass"],
        "single_az": not temporal["MultiAZ"],
        "sin_backups": temporal["BackupRetentionPeriod"] == 0,
        "sin_exportar_logs": not temporal.get("EnabledCloudwatchLogsExports"),
        "sin_proteccion_de_borrado": not temporal["DeletionProtection"],
        "etiquetada_temporal": etiquetas.get("Proposito") == PROPOSITO and etiquetas.get("Temporal") == "true",
    }


def preflight(conexiones, ruta):
    rds = conexiones["rds"]
    prod = _instancia(rds, PRODUCTIVA)
    if prod is None:
        raise Abortar("PRODUCTIVA_AUSENTE")
    previas, marker, vistos = [], None, set()
    while True:
        pagina = rds.describe_db_instances(**({"Marker": marker} if marker else {}))
        previas.extend(i for i in pagina["DBInstances"]
                       if i["DBInstanceIdentifier"].startswith("blog-prod-restore-h0317-"))
        marker = pagina.get("Marker")
        if not marker:
            break
        if marker in vistos:
            raise Abortar("PAGINACION_NO_CONCLUYENTE")
        vistos.add(marker)
    if previas:
        raise Abortar("TEMPORAL_PREVIA_EXISTENTE")
    estado = {"disponible": prod["DBInstanceStatus"] == "available",
              "retencion_de_backups": prod["BackupRetentionPeriod"],
              "retraso_de_pitr_s": int((RELOJ() - prod["LatestRestorableTime"]).total_seconds()),
              "cifrada": prod["StorageEncrypted"], "publica": prod["PubliclyAccessible"],
              "clase": prod["DBInstanceClass"], "motor": prod["EngineVersion"]}
    if not (estado["disponible"] and estado["retencion_de_backups"] >= 1 and estado["cifrada"]
            and not estado["publica"] and 0 <= estado["retraso_de_pitr_s"] <= OBJETIVO_RPO_S):
        raise Abortar("PRODUCTIVA_NO_CONFORME")
    return {"productiva": estado, "temporales_previas": 0}


def sembrar(conexiones, ruta):
    datos = _leer(ruta)
    if datos:
        raise Abortar("MANIFIESTO_EN_USO")
    preflight(conexiones, ruta)
    marcador, instante = str(uuid.uuid4()), _texto(RELOJ())
    # Persistir la intencion ANTES de la llamada: un timeout no demuestra rollback del servidor.
    # Una respuesta perdida exige reconciliar este UUID mediante verify, nunca sembrar otro a ciegas.
    datos["marcador"] = {"id": marcador, "instante": instante, "estado": "solicitado"}
    _guardar(ruta, datos)
    respuesta = operador.invocar_modo(["sintetico", "--accion", "sembrar", "--marcador", marcador,
                                       "--instante", instante], conexiones)
    if respuesta.get("estado") != "OK" or not respuesta.get("marcador", {}).get("presente"):
        raise Abortar("MARCADOR_NO_SEMBRADO")
    datos["marcador"] = {"id": marcador, "instante": instante, "huella": respuesta["marcador"]["huella"],
                         "t0": _texto(RELOJ()), "estado": "confirmado"}
    _guardar(ruta, datos)
    return {"marcador": {"id": marcador, "huella": datos["marcador"]["huella"]}}


def _rechazo(error):
    """{codigo, http} si la API RECHAZO la llamada con una respuesta 4xx y un codigo cerrado; None si el rechazo no
    esta demostrado (sin respuesta, 5xx o codigo fuera del patron), y entonces el resultado sigue siendo incierto.

    CloudTrail no registra las llamadas que rechaza el plan FREE (2026-10-05, reporte §32): la respuesta sincrona
    es la unica prueba. Nunca se conserva el mensaje, que lleva ARN y cuenta."""
    respuesta = getattr(error, "response", None) or {}
    codigo = (respuesta.get("Error") or {}).get("Code")
    http = (respuesta.get("ResponseMetadata") or {}).get("HTTPStatusCode")
    if (type(codigo) is str and _CODIGO_DE_AWS.fullmatch(codigo) and type(http) is int and 400 <= http < 500):
        return {"codigo": codigo, "http": http}
    return None


def _backups_automaticos(rds, identificador):
    """Backups automaticos retenidos de la temporal. Si no hay ninguno, la API responde HTTP 404
    `DBInstanceAutomatedBackupNotFound` en vez de una lista vacia (H-031-7 real, 2026-10-20): eso es CERO. Cualquier
    otro error sigue su curso."""
    try:
        return len(rds.describe_db_instance_automated_backups(DBInstanceIdentifier=identificador)
                   ["DBInstanceAutomatedBackups"])
    except Exception as error:
        if ((getattr(error, "response", None) or {}).get("Error") or {}).get("Code") == "DBInstanceAutomatedBackupNotFound":
            return 0
        raise


def _es_la_temporal_registrada(temporal, registrada):
    """La instancia que existe es la que pidio ESTA corrida: identificador, etiquetas de temporal y, si ya se
    registro, el mismo `DbiResourceId`. Nunca la productiva."""
    etiquetas = _etiquetas(temporal)
    return (temporal["DBInstanceIdentifier"] == registrada["identificador"] != PRODUCTIVA
            and etiquetas.get("Proposito") == PROPOSITO and etiquetas.get("Temporal") == "true"
            and temporal["DbiResourceId"] == registrada.get("dbi_resource_id", temporal["DbiResourceId"]))


def restaurar(conexiones, ruta, identificador):
    if not PATRON_TEMPORAL.fullmatch(identificador or "") or identificador == PRODUCTIVA:
        raise Abortar("IDENTIFICADOR_NO_ADMITIDO")
    datos = _leer(ruta)
    if "marcador" not in datos:
        raise Abortar("SIN_MARCADOR")
    if not all(datos["marcador"].get(k) for k in ("huella", "t0")):
        raise Abortar("MARCADOR_NO_CONFIRMADO")
    rds = conexiones["rds"]
    registrada = datos.get("temporal")
    # Reanudacion (la sesion de la consola dura 1 h y el PITR tarda minutos): NUNCA un segundo restore. `t_solicitud`
    # se guarda ANTES de llamar a la API, asi que su ausencia prueba que no salio ninguna solicitud.
    if registrada is not None:
        if registrada.get("identificador") != identificador:
            raise Abortar("IDENTIFICADOR_NO_ADMITIDO")
        if "rechazo" in registrada:
            raise Abortar("RESTORE_RECHAZADO")  # la API ya lo rechazo: definitivo, nunca se repite
        if "t_disponible" in registrada:
            raise Abortar("TEMPORAL_YA_REGISTRADA")
    solicitada = registrada is not None and "t_solicitud" in registrada
    temporal = _instancia(rds, identificador)
    if solicitada:
        if temporal is None:
            raise Abortar("RESTAURACION_INCIERTA")  # se pidio y no esta: lo decide una persona
        if not _es_la_temporal_registrada(temporal, registrada):
            raise Abortar("RESTAURADA_NO_CONFORME")
        prod = _instancia(rds, PRODUCTIVA)
        if prod is None or prod["DbiResourceId"] != datos.get("productiva", {}).get("dbi_resource_id"):
            raise Abortar("PRODUCTIVA_CAMBIO")
        datos["temporal"]["reanudado"] = True
        _guardar(ruta, datos)
    else:
        if temporal is not None:
            raise Abortar("TEMPORAL_PREVIA_EXISTENTE" if registrada is None else "RESTAURADA_NO_CONFORME")
        if registrada is None:
            datos["temporal"] = {"identificador": identificador, "registrado": _texto(RELOJ())}
            _guardar(ruta, datos)  # la identidad exacta queda registrada ANTES de crear nada

        t0 = _instante(datos["marcador"]["t0"])

        def pitr_cubre_el_marcador():
            prod = _instancia(rds, PRODUCTIVA)
            return prod if prod["LatestRestorableTime"] >= t0 + MARGEN else None

        prod = _esperar(pitr_cubre_el_marcador, ESPERA_PITR_S, "PITR_NO_ALCANZA_EL_MARCADOR")
        instante = prod["LatestRestorableTime"]
        datos["productiva"] = {"dbi_resource_id": prod["DbiResourceId"]}
        datos["temporal"].update(t_lrt=_texto(RELOJ()), t_solicitud=_texto(RELOJ()), restore_time=_texto(instante))
        _guardar(ruta, datos)
        try:
            rds.restore_db_instance_to_point_in_time(**parametros(prod, identificador, instante))
        except Exception as error:
            rechazo = _rechazo(error)
            if rechazo is None:
                raise  # sin rechazo demostrado: incierto, con `t_solicitud` ya registrado
            datos["temporal"]["rechazo"] = {**rechazo, "t_rechazo": _texto(RELOJ())}
            _guardar(ruta, datos)
            raise Abortar("RESTORE_RECHAZADO") from None

    def disponible():
        temporal = _instancia(rds, identificador)
        if temporal and "dbi_resource_id" not in datos["temporal"]:
            # El recurso queda registrado en cuanto aparece: `limpiar` puede borrarlo aunque nunca llegue a available.
            datos["temporal"]["dbi_resource_id"] = temporal["DbiResourceId"]
            _guardar(ruta, datos)
        return temporal if temporal and temporal["DBInstanceStatus"] == "available" else None

    temporal = _esperar(disponible, ESPERA_DISPONIBLE_S, "TEMPORAL_NO_DISPONIBLE")
    readback = _readback(temporal, prod)
    datos["temporal"].update(t_disponible=_texto(RELOJ()), dbi_resource_id=temporal["DbiResourceId"], readback=readback)
    _guardar(ruta, datos)
    if readback["publica"] or not all(valor for clave, valor in readback.items() if clave != "publica"):
        raise Abortar("RESTAURADA_NO_CONFORME")
    return {"identificador": identificador, "readback": readback}


def verificar(conexiones, ruta):
    datos = _leer(ruta)
    if "t_disponible" not in datos.get("temporal", {}):
        raise Abortar("SIN_RESTAURADA")
    temporal = _instancia(conexiones["rds"], datos["temporal"]["identificador"])
    prod = _instancia(conexiones["rds"], PRODUCTIVA)
    if (not temporal or not prod or temporal["DbiResourceId"] != datos["temporal"].get("dbi_resource_id")
            or prod["DbiResourceId"] != datos["productiva"].get("dbi_resource_id")):
        raise Abortar("RESTAURADA_NO_CONFORME")
    readback = _readback(temporal, prod)
    if readback["publica"] or not all(v for k, v in readback.items() if k != "publica"):
        raise Abortar("RESTAURADA_NO_CONFORME")
    marcador = datos["marcador"]
    respuesta = operador.invocar_modo(["verify", "--usuario", "blog_migrate", "--restaurada",
                                       datos["temporal"]["identificador"], "--marcador", marcador["id"]], conexiones)
    leido = respuesta.get("marcador", {})
    integridad = respuesta.get("estado") == "OK" and leido.get("presente") is True and leido.get("huella") == marcador["huella"]
    datos["verificacion"] = {"t_verificado": _texto(RELOJ()), "integridad": integridad}
    _guardar(ruta, datos)
    if not integridad:
        raise Abortar("INTEGRIDAD_FALLIDA")
    return {"integridad": True}


def limpiar(conexiones, ruta):
    datos, rds = _leer(ruta), conexiones["rds"]
    registrada = datos.get("temporal", {})
    identificador = registrada.get("identificador") or ""
    if not PATRON_TEMPORAL.fullmatch(identificador) or identificador == PRODUCTIVA:
        raise Abortar("LIMPIEZA_NO_AUTORIZADA")
    temporal, prod = _instancia(rds, identificador), _instancia(rds, PRODUCTIVA)
    if (not prod or prod["DbiResourceId"] != datos.get("productiva", {}).get("dbi_resource_id")
            or prod["DBInstanceStatus"] != "available" or not prod["DeletionProtection"]):
        raise Abortar("PRODUCTIVA_CAMBIO")
    limpieza = datos.get("limpieza") or {}
    ya_solicitado = limpieza.get("borrado_solicitado") is True
    if (temporal is None and not ya_solicitado) or (temporal is not None and (
            temporal["DbiResourceId"] != registrada.get("dbi_resource_id")
            or temporal["DbiResourceId"] == prod["DbiResourceId"] or temporal["DeletionProtection"]
            or _etiquetas(temporal).get("Temporal") != "true" or _etiquetas(temporal).get("Proposito") != PROPOSITO)):
        raise Abortar("LIMPIEZA_NO_AUTORIZADA")
    se_elimina = [{"tipo": "aws_db_instance", "identificador": identificador,
                   "dbi_resource_id": registrada.get("dbi_resource_id")}]
    if not ya_solicitado:
        datos["limpieza"] = {"se_elimina": se_elimina, "listado": _texto(RELOJ()), "borrado_solicitado": True}
        _guardar(ruta, datos)  # lo que se elimina queda listado antes de borrar
        rds.delete_db_instance(DBInstanceIdentifier=identificador, SkipFinalSnapshot=True, DeleteAutomatedBackups=True)
    elif temporal is not None and temporal["DBInstanceStatus"] != "deleting":
        raise Abortar("BORRADO_INCIERTO")  # observar/investigar, nunca emitir de nuevo delete
    _esperar(lambda: _instancia(rds, identificador) is None, ESPERA_BORRADO_S, "TEMPORAL_NO_ELIMINADA")
    restantes = _backups_automaticos(rds, identificador)
    prod = _instancia(rds, PRODUCTIVA)
    intacta = (prod is not None and prod["DBInstanceStatus"] == "available" and prod["DeletionProtection"]
               and prod["DbiResourceId"] == datos["productiva"]["dbi_resource_id"])
    if restantes or not intacta:
        raise Abortar("LIMPIEZA_INCOMPLETA")
    if datos["limpieza"].get("retiro_solicitado"):
        if datos["limpieza"].get("marcador_retirado") is True:
            return {"se_elimina": se_elimina, "ausente_por_api": True, "productiva_intacta": True,
                    "marcador_retirado": True}
        raise Abortar("RETIRO_DEL_MARCADOR_INCIERTO")
    datos["limpieza"].update(ausente_por_api=True, retiro_solicitado=True)
    _guardar(ruta, datos)
    marcador = datos["marcador"]
    respuesta = operador.invocar_modo(["sintetico", "--accion", "limpiar", "--marcador", marcador["id"],
                                       "--instante", marcador["instante"]], conexiones)
    retirado = respuesta.get("estado") == "OK" and respuesta.get("marcador", {}).get("presente") is False
    datos["limpieza"].update(t_limpieza=_texto(RELOJ()), ausente_por_api=True, backups_automaticos_restantes=restantes,
                             productiva_intacta=intacta, marcador_retirado=retirado)
    _guardar(ruta, datos)
    if restantes or not intacta or not retirado:
        raise Abortar("LIMPIEZA_INCOMPLETA")
    return {"se_elimina": se_elimina, "ausente_por_api": True, "productiva_intacta": True, "marcador_retirado": True}


def informe(datos):
    """Duraciones en segundos, RPO y RTO observados y su comparacion con los objetivos de D-10."""
    t0, temporal = _instante(datos["marcador"]["t0"]), datos["temporal"]
    t_lrt, t_solicitud = _instante(temporal["t_lrt"]), _instante(temporal["t_solicitud"])
    restore_time, t_disponible = _instante(temporal["restore_time"]), _instante(temporal["t_disponible"])
    t_verificado = _instante(datos["verificacion"]["t_verificado"])
    segundos = lambda desde, hasta: int((hasta - desde).total_seconds())  # noqa: E731
    rpo, rto = segundos(restore_time, t_solicitud), segundos(t_solicitud, t_verificado)
    return {"espera_hasta_pitr_s": segundos(t0, t_lrt), "restore_hasta_available_s": segundos(t_solicitud, t_disponible),
            "verificacion_s": segundos(t_disponible, t_verificado), "total_s": segundos(t0, t_verificado),
            "rpo_observado_s": rpo, "rto_observado_s": rto, "objetivo_rpo_s": OBJETIVO_RPO_S,
            "objetivo_rto_s": OBJETIVO_RTO_S, "rpo_cumple": rpo <= OBJETIVO_RPO_S, "rto_cumple": rto <= OBJETIVO_RTO_S,
            "integridad": datos["verificacion"]["integridad"]}


def main(argv=None, clientes=_clientes):
    comun = argparse.ArgumentParser(add_help=False)
    comun.add_argument("--manifiesto", required=True, type=Path)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    fases = parser.add_subparsers(dest="fase", required=True)
    for fase in ("preflight", "sembrar", "verificar", "limpiar", "informe"):
        fases.add_parser(fase, parents=[comun])
    fases.add_parser("restaurar", parents=[comun]).add_argument("--identificador", required=True)
    args = parser.parse_args(argv)
    try:
        if args.fase == "informe":
            resultado = informe(_leer(args.manifiesto))
        else:
            conexiones = clientes()
            operador._comprobar_identidad(conexiones["sts"], [])
            if args.fase == "restaurar":
                resultado = restaurar(conexiones, args.manifiesto, args.identificador)
            else:
                resultado = globals()[args.fase](conexiones, args.manifiesto)
        print(json.dumps({"estado": "OK", "fase": args.fase, **resultado}, sort_keys=True, ensure_ascii=False))
        return 0
    except Abortar as fin:
        print(json.dumps({"estado": fin.estado}))
        return 1
    except Exception as error:
        print(json.dumps({"estado": "ERROR_DEL_OPERADOR", "tipo": type(error).__name__}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
