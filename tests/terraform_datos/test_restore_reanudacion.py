"""H-031-7: reanudar `restaurar` si la sesion se pierde durante la espera, SIN pedir nunca un segundo restore.

Por que: la sesion de `aws login` vive como mucho lo que la sesion de rol de la consola (1 h), y un PITR a una
`db.t4g.micro` tarda minutos. Si la sesion caduca durante la espera, el proceso termina con la temporal YA pedida, y
facturando. Antes, volver a ejecutar `restaurar` daba `TEMPORAL_YA_REGISTRADA`; `verificar` exigia `t_disponible`
(`SIN_RESTAURADA`), y si el corte llegaba antes de registrar el `DbiResourceId`, `limpiar` se negaba a borrarla.

Contrato:
- solicitud registrada (`t_solicitud`) y temporal presente con el mismo identificador y SUS etiquetas: se reanuda la
  espera, se registra su `DbiResourceId` si faltaba y se completan readback y `t_disponible`. Ningun restore nuevo.
- solicitud registrada y temporal AUSENTE: `RESTAURACION_INCIERTA`. Ningun restore: lo decide una persona.
- temporal presente con otra identidad (etiquetas ajenas o `DbiResourceId` distinto del registrado):
  `RESTAURADA_NO_CONFORME`. Ningun restore.
- otro identificador que el registrado: `IDENTIFICADOR_NO_ADMITIDO`.
- una restauracion ya completa no se repite: `TEMPORAL_YA_REGISTRADA`.
"""
from tests.terraform_datos.test_restore_sintetico import Base, TEMPORAL, rs


class SesionCaducada(Exception):
    """Lo que ve el operador cuando la sesion de rol de la consola expira a mitad de la espera."""


class ReanudarRestore(Base):
    def restores(self):
        return sum(c[0] == "restore" for c in self.rds.llamadas)

    def cortar_la_sesion_tras_el_restore(self, cortes=1):
        original = self.rds.describe_db_instances
        pendientes = {"cortes": cortes}

        def describir(DBInstanceIdentifier=None):
            if DBInstanceIdentifier == TEMPORAL and pendientes["cortes"] and self.restores():
                pendientes["cortes"] -= 1
                raise SesionCaducada("ExpiredToken")
            return original(DBInstanceIdentifier)

        self.rds.describe_db_instances = describir

    def test_reanuda_la_espera_sin_un_segundo_restore(self):
        self.assertEqual(self.ejecutar("sembrar")[0], 0)
        self.cortar_la_sesion_tras_el_restore()
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL),
                         (1, {"estado": "ERROR_DEL_OPERADOR", "tipo": "SesionCaducada"}))
        self.assertNotIn("t_disponible", self.leer()["temporal"])
        codigo, salida = self.ejecutar("restaurar", "--identificador", TEMPORAL)
        self.assertEqual((codigo, salida["estado"], salida["identificador"]), (0, "OK", TEMPORAL))
        temporal = self.leer()["temporal"]
        self.assertEqual(temporal["dbi_resource_id"], "db-TEMPORAL")
        self.assertIn("t_disponible", temporal)
        self.assertTrue(temporal["reanudado"])
        self.assertEqual(self.restores(), 1)
        # La cadena sigue: verificar y limpiar funcionan sobre la temporal reanudada.
        self.assertEqual(self.ejecutar("verificar"), (0, {"estado": "OK", "fase": "verificar", "integridad": True}))
        self.assertEqual(self.ejecutar("limpiar")[0], 0)

    def test_solicitud_registrada_sin_temporal_es_incierta(self):
        self.assertEqual(self.ejecutar("sembrar")[0], 0)

        def restore_sin_respuesta(**parametros):
            self.rds.llamadas.append(("restore", parametros))
            raise SesionCaducada("respuesta perdida")

        self.rds.restore_db_instance_to_point_in_time = restore_sin_respuesta
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL)[0], 1)
        self.assertIn("t_solicitud", self.leer()["temporal"])
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL),
                         (1, {"estado": "RESTAURACION_INCIERTA"}))
        self.assertEqual(self.restores(), 1)

    def test_temporal_con_etiquetas_ajenas_no_se_adopta(self):
        self.assertEqual(self.ejecutar("sembrar")[0], 0)
        self.cortar_la_sesion_tras_el_restore()
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL)[0], 1)
        self.rds.instancias[TEMPORAL]["TagList"] = [{"Key": "Proposito", "Value": "otro"}]
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL),
                         (1, {"estado": "RESTAURADA_NO_CONFORME"}))
        self.assertEqual(self.restores(), 1)

    def test_temporal_recreada_con_otro_dbi_no_se_adopta(self):
        self.assertEqual(self.ejecutar("sembrar")[0], 0)
        self.cortar_la_sesion_tras_el_restore(cortes=1)
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL)[0], 1)
        datos = self.leer()
        datos["temporal"]["dbi_resource_id"] = "db-REGISTRADA"
        self.manifiesto.write_text(rs.json.dumps(datos), encoding="utf-8")
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL),
                         (1, {"estado": "RESTAURADA_NO_CONFORME"}))
        self.assertEqual(self.restores(), 1)

    def test_otro_identificador_que_el_registrado(self):
        self.assertEqual(self.ejecutar("sembrar")[0], 0)
        self.cortar_la_sesion_tras_el_restore()
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL)[0], 1)
        otro = "blog-prod-restore-h0317-20261007130000"
        self.assertEqual(self.ejecutar("restaurar", "--identificador", otro),
                         (1, {"estado": "IDENTIFICADOR_NO_ADMITIDO"}))
        self.assertEqual(self.restores(), 1)

    def test_corte_antes_de_pedir_el_restore_se_reanuda(self):
        """`t_solicitud` se guarda ANTES de llamar a la API: sin el, no salio ninguna solicitud."""
        self.assertEqual(self.ejecutar("sembrar")[0], 0)
        original = self.rds.describe_db_instances
        pendientes = {"cortes": 1}

        def describir(DBInstanceIdentifier=None):
            if DBInstanceIdentifier == rs.PRODUCTIVA and pendientes["cortes"] and "temporal" in self.leer():
                pendientes["cortes"] -= 1
                raise SesionCaducada("ExpiredToken")
            return original(DBInstanceIdentifier)

        self.rds.describe_db_instances = describir
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL)[0], 1)
        self.assertNotIn("t_solicitud", self.leer()["temporal"])
        self.assertEqual(self.restores(), 0)
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL)[0], 0)
        self.assertEqual(self.restores(), 1)
        self.assertIn("t_disponible", self.leer()["temporal"])

    def test_una_restauracion_completa_no_se_repite(self):
        self.hasta_restaurada()
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL),
                         (1, {"estado": "TEMPORAL_YA_REGISTRADA"}))
        self.assertEqual(self.restores(), 1)
