"""H-031-7: no perder la identidad de una operacion ambigua ni repetir escrituras al reanudar."""
import datetime as dt
from unittest import mock

from tests.terraform_datos.test_restore_sintetico import Base, TEMPORAL, rs


class FallosDeRestore(Base):
    def test_siembra_registrada_antes_de_invocar_aun_si_se_pierde_la_respuesta(self):
        vistos = []
        def falla(argv, conexiones):
            vistos.append(self.leer()["marcador"]["id"])
            raise TimeoutError("respuesta perdida")
        with mock.patch.object(rs.operador, "invocar_modo", side_effect=falla):
            self.assertEqual(self.ejecutar("sembrar")[0], 1)
        self.assertEqual(len(vistos), 1)
        self.assertEqual(self.ejecutar("sembrar"), (1, {"estado": "MANIFIESTO_EN_USO"}))
        self.assertEqual(self.ejecutar("restaurar", "--identificador", TEMPORAL),
                         (1, {"estado": "MARCADOR_NO_CONFIRMADO"}))

    def test_productiva_publica_impide_sembrar_sin_invocacion(self):
        self.rds.instancias[rs.PRODUCTIVA]["PubliclyAccessible"] = True
        self.assertEqual(self.ejecutar("sembrar"), (1, {"estado": "PRODUCTIVA_NO_CONFORME"}))
        self.assertEqual(self.ejecutora.llamadas, [])

    def test_retraso_negativo_no_pasa_preflight(self):
        self.rds._refrescar = lambda: None
        self.rds.instancias[rs.PRODUCTIVA]["LatestRestorableTime"] = self.reloj.ahora() + dt.timedelta(minutes=1)
        self.assertEqual(self.ejecutar("preflight"), (1, {"estado": "PRODUCTIVA_NO_CONFORME"}))

    def test_paginacion_detecta_temporal_en_segunda_pagina(self):
        original = self.rds.describe_db_instances
        def describir(DBInstanceIdentifier=None, **kwargs):
            if DBInstanceIdentifier:
                return original(DBInstanceIdentifier)
            if kwargs.get("Marker"):
                return {"DBInstances": [{"DBInstanceIdentifier": TEMPORAL}]}
            return {**original(), "Marker": "pagina2"}
        self.rds.describe_db_instances = describir
        self.assertEqual(self.ejecutar("preflight"), (1, {"estado": "TEMPORAL_PREVIA_EXISTENTE"}))

    def test_productiva_reemplazada_impide_borrar_o_retirar_marcador(self):
        self.hasta_restaurada()
        self.rds.instancias[rs.PRODUCTIVA]["DbiResourceId"] = "db-OTRA"
        antes = len(self.ejecutora.llamadas)
        self.assertEqual(self.ejecutar("limpiar"), (1, {"estado": "PRODUCTIVA_CAMBIO"}))
        self.assertEqual(len(self.ejecutora.llamadas), antes)
        self.assertFalse(any(c[0] == "delete" for c in self.rds.llamadas))

    def test_borrado_confirmado_se_reanuda_sin_otro_delete(self):
        self.hasta_restaurada()
        original = self.rds.delete_db_instance
        def borrar(**kwargs):
            original(**kwargs)
            del self.rds.instancias[TEMPORAL]
            raise TimeoutError("respuesta perdida")
        self.rds.delete_db_instance = borrar
        self.assertEqual(self.ejecutar("limpiar")[0], 1)
        self.assertEqual(self.ejecutar("limpiar")[0], 0)
        self.assertEqual(sum(c[0] == "delete" for c in self.rds.llamadas), 1)

    def test_si_retiro_del_marcador_es_ambiguo_no_se_reinvoca(self):
        self.hasta_restaurada()
        with mock.patch.object(rs.operador, "invocar_modo", side_effect=TimeoutError):
            self.assertEqual(self.ejecutar("limpiar")[0], 1)
        antes = len(self.ejecutora.llamadas)
        self.assertEqual(self.ejecutar("limpiar"), (1, {"estado": "RETIRO_DEL_MARCADOR_INCIERTO"}))
        self.assertEqual(len(self.ejecutora.llamadas), antes)

    def test_verificar_no_admite_instancia_recreada_con_el_mismo_nombre(self):
        self.hasta_restaurada()
        self.rds.instancias[TEMPORAL]["DbiResourceId"] = "db-OTRA"
        antes = len(self.ejecutora.llamadas)
        self.assertEqual(self.ejecutar("verificar"), (1, {"estado": "RESTAURADA_NO_CONFORME"}))
        self.assertEqual(len(self.ejecutora.llamadas), antes)
