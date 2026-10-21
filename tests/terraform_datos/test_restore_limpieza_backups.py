"""H-031-7: `limpiar` cuenta como CERO los backups automaticos cuando la API responde que no hay ninguno.

Por que (H-031-7 real, 2026-10-20): tras borrar la temporal con `DeleteAutomatedBackups=True`, la API respondio a
`DescribeDBInstanceAutomatedBackups` con HTTP 404 `DBInstanceAutomatedBackupNotFound` (asi la modela botocore:
`DBInstanceAutomatedBackupNotFoundFault`), no con una lista vacia. `limpiar` lo trato como un error del operador y se
detuvo DESPUES del borrado y ANTES de retirar el marcador; el RDS simulado de las pruebas devolvia una lista vacia.

Contrato:
- 404 `DBInstanceAutomatedBackupNotFound`: cero backups restantes; la limpieza termina y retira el marcador.
- reanudar tras un corte posterior al borrado: ningun segundo delete; termina igual.
- cualquier otro error de esa lectura sigue siendo un error: el marcador NO se retira.
- un backup automatico retenido sigue siendo `LIMPIEZA_INCOMPLETA`.
"""
from tests.terraform_datos.test_restore_sintetico import Base, CUENTA, TEMPORAL


class RespuestaDeAws(Exception):
    """Como `botocore.exceptions.ClientError`: codigo y estado HTTP en `response`; el mensaje lleva un ARN."""

    def __init__(self, http, codigo):
        super().__init__(codigo)
        self.response = {"Error": {"Code": codigo, "Message": f"arn:aws:rds:us-east-2:{CUENTA}:db:{TEMPORAL}"},
                         "ResponseMetadata": {"HTTPStatusCode": http}}


class BackupsAutomaticosTrasElBorrado(Base):
    def borrados(self):
        return sum(c[0] == "delete" for c in self.rds.llamadas)

    def retiros(self):
        return sum(1 for c in self.ejecutora.llamadas if c[0] == "sintetico" and c[2] == "limpiar")

    def responder_a_los_backups(self, *respuestas):
        pendientes = list(respuestas)

        def describir(DBInstanceIdentifier):
            self.rds.llamadas.append(("backups", DBInstanceIdentifier))
            respuesta = pendientes.pop(0) if len(pendientes) > 1 else pendientes[0]
            if isinstance(respuesta, Exception):
                raise respuesta
            return {"DBInstanceAutomatedBackups": respuesta}

        self.rds.describe_db_instance_automated_backups = describir

    def test_404_sin_backups_cuenta_como_cero_y_retira_el_marcador(self):
        self.hasta_restaurada()
        self.assertEqual(self.ejecutar("verificar")[0], 0)
        self.responder_a_los_backups(RespuestaDeAws(404, "DBInstanceAutomatedBackupNotFound"))
        self.assertEqual(self.ejecutar("limpiar")[0], 0)
        limpieza = self.leer()["limpieza"]
        self.assertEqual(limpieza["backups_automaticos_restantes"], 0)
        self.assertTrue(limpieza["marcador_retirado"])
        self.assertEqual((self.borrados(), self.retiros()), (1, 1))

    def test_reanudar_tras_el_borrado_no_pide_otro_delete(self):
        # El caso real: el borrado se completo y la lectura de backups corto la limpieza antes del marcador.
        self.hasta_restaurada()
        self.assertEqual(self.ejecutar("verificar")[0], 0)
        self.responder_a_los_backups(TimeoutError("respuesta perdida"), RespuestaDeAws(404,
                                                                                     "DBInstanceAutomatedBackupNotFound"))
        self.assertEqual(self.ejecutar("limpiar")[0], 1)
        self.assertNotIn("marcador_retirado", self.leer()["limpieza"])
        self.assertEqual(self.ejecutar("limpiar")[0], 0)
        self.assertTrue(self.leer()["limpieza"]["marcador_retirado"])
        self.assertEqual((self.borrados(), self.retiros()), (1, 1))

    def test_otro_error_de_la_lectura_no_retira_el_marcador(self):
        self.hasta_restaurada()
        self.assertEqual(self.ejecutar("verificar")[0], 0)
        self.responder_a_los_backups(RespuestaDeAws(403, "AccessDenied"))
        self.assertEqual(self.ejecutar("limpiar"), (1, {"estado": "ERROR_DEL_OPERADOR", "tipo": "RespuestaDeAws"}))
        self.assertEqual(self.retiros(), 0)
        self.assertNotIn("marcador_retirado", self.leer()["limpieza"])

    def test_un_404_con_otro_codigo_no_cuenta_como_cero(self):
        self.hasta_restaurada()
        self.assertEqual(self.ejecutar("verificar")[0], 0)
        self.responder_a_los_backups(RespuestaDeAws(404, "DBInstanceNotFound"))
        self.assertEqual(self.ejecutar("limpiar")[0], 1)
        self.assertEqual(self.retiros(), 0)

    def test_un_backup_retenido_sigue_siendo_limpieza_incompleta(self):
        self.hasta_restaurada()
        self.assertEqual(self.ejecutar("verificar")[0], 0)
        self.responder_a_los_backups([{"DBInstanceIdentifier": TEMPORAL, "Status": "retained"}])
        self.assertEqual(self.ejecutar("limpiar"), (1, {"estado": "LIMPIEZA_INCOMPLETA"}))
        self.assertEqual(self.retiros(), 0)
