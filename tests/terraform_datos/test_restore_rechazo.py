"""H-031-7: un restore que la API RECHAZA (HTTP 4xx con codigo) queda registrado como definitivo y nunca se repite.

Por que (indicacion del usuario del 2026-10-20 sobre `FreeTierRestrictionError`): CloudTrail NO registra las llamadas
que rechaza el plan FREE. El 2026-10-05, entre las 14:59:10Z y las 14:59:17Z, el historial de RDS muestra hasta las
lecturas fallidas (`DescribeDBInstances` con `DBInstanceNotFoundFault`) pero no el `CreateDBInstance` que la API
rechazo con HTTP 400 `FreeTierRestrictionError` (reporte §32). La unica prueba del rechazo es la respuesta sincrona de
la API, y `restaurar` la perdia: `ERROR_DEL_OPERADOR` con el tipo de la excepcion, y al relanzar,
`RESTAURACION_INCIERTA`.

Contrato:
- respuesta HTTP 4xx con codigo: `temporal.rechazo` = {codigo, http, t_rechazo} en el manifiesto y salida
  `RESTORE_RECHAZADO`. Nunca el mensaje de AWS, que lleva ARN y cuenta.
- relanzar `restaurar` tras un rechazo registrado: `RESTORE_RECHAZADO` otra vez, sin ninguna llamada de restore.
- sin respuesta HTTP (timeout, conexion perdida) o con 5xx: NO hay rechazo demostrado; sigue siendo incierto
  (`t_solicitud` sin `rechazo`), como antes.
- un rechazo no autoriza a `limpiar`: no hay temporal que borrar, y el marcador solo se retira con la ausencia
  demostrada por el runner que lo orquesta.
"""
from tests.terraform_datos.test_restore_sintetico import Base, CUENTA, TEMPORAL


class RespuestaDeAws(Exception):
    """Como `botocore.exceptions.ClientError`: codigo y estado HTTP en `response`; el mensaje lleva un ARN."""

    def __init__(self, http, codigo):
        super().__init__(codigo)
        self.response = {"Error": {"Code": codigo, "Message": f"arn:aws:rds:us-east-2:{CUENTA}:db:{TEMPORAL}"},
                         "ResponseMetadata": {"HTTPStatusCode": http}}


class RestoreRechazado(Base):
    def restores(self):
        return sum(c[0] == "restore" for c in self.rds.llamadas)

    def responder_al_restore(self, error):
        def restore(**parametros):
            self.rds.llamadas.append(("restore", parametros))
            raise error

        self.rds.restore_db_instance_to_point_in_time = restore

    def test_rechazo_del_plan_free_queda_registrado_y_no_es_incierto(self):
        self.assertEqual(self.ejecutar("sembrar")[0], 0)
        self.responder_al_restore(RespuestaDeAws(400, "FreeTierRestrictionError"))
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL), (1, {"estado": "RESTORE_RECHAZADO"}))
        temporal = self.leer()["temporal"]
        self.assertIn("t_solicitud", temporal)
        # El reloj simulado no avanza entre la solicitud y la respuesta: el rechazo lleva el mismo instante.
        self.assertEqual(temporal["rechazo"], {"codigo": "FreeTierRestrictionError", "http": 400,
                                               "t_rechazo": temporal["t_solicitud"]})
        self.assertNotIn("dbi_resource_id", temporal)
        self.assertNotIn("t_disponible", temporal)
        self.assertEqual(self.restores(), 1)

    def test_relanzar_tras_un_rechazo_no_pide_otro_restore(self):
        self.assertEqual(self.ejecutar("sembrar")[0], 0)
        self.responder_al_restore(RespuestaDeAws(400, "FreeTierRestrictionError"))
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL)[0], 1)
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL), (1, {"estado": "RESTORE_RECHAZADO"}))
        self.assertEqual(self.restores(), 1)

    def test_otro_rechazo_4xx_tambien_es_definitivo(self):
        self.assertEqual(self.ejecutar("sembrar")[0], 0)
        self.responder_al_restore(RespuestaDeAws(400, "InvalidParameterCombination"))
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL), (1, {"estado": "RESTORE_RECHAZADO"}))
        self.assertEqual(self.leer()["temporal"]["rechazo"]["codigo"], "InvalidParameterCombination")

    def test_sin_respuesta_http_sigue_siendo_incierto(self):
        self.assertEqual(self.ejecutar("sembrar")[0], 0)
        self.responder_al_restore(TimeoutError("respuesta perdida"))
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL),
                         (1, {"estado": "ERROR_DEL_OPERADOR", "tipo": "TimeoutError"}))
        self.assertNotIn("rechazo", self.leer()["temporal"])
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL),
                         (1, {"estado": "RESTAURACION_INCIERTA"}))
        self.assertEqual(self.restores(), 1)

    def test_un_5xx_no_es_un_rechazo_demostrado(self):
        self.assertEqual(self.ejecutar("sembrar")[0], 0)
        self.responder_al_restore(RespuestaDeAws(500, "InternalFailure"))
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL),
                         (1, {"estado": "ERROR_DEL_OPERADOR", "tipo": "RespuestaDeAws"}))
        self.assertNotIn("rechazo", self.leer()["temporal"])

    def test_un_codigo_fuera_del_patron_no_es_un_rechazo_demostrado(self):
        self.assertEqual(self.ejecutar("sembrar")[0], 0)
        self.responder_al_restore(RespuestaDeAws(400, "codigo con espacios y <marcas>"))
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL)[1]["estado"], "ERROR_DEL_OPERADOR")
        self.assertNotIn("rechazo", self.leer()["temporal"])

    def test_un_rechazo_no_autoriza_limpiar(self):
        self.assertEqual(self.ejecutar("sembrar")[0], 0)
        self.responder_al_restore(RespuestaDeAws(400, "FreeTierRestrictionError"))
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL)[0], 1)
        antes = len(self.ejecutora.llamadas)
        self.assertEqual(self.ejecutar("limpiar"), (1, {"estado": "LIMPIEZA_NO_AUTORIZADA"}))
        self.assertEqual(len(self.ejecutora.llamadas), antes)
        self.assertFalse(any(c[0] == "delete" for c in self.rds.llamadas))
