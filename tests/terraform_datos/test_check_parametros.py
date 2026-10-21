"""Regresion de H-031-3 (§27.4): un parametro no modificable no puede volver a llegar al apply.

El apply real se rompio a medias con `InvalidParameterValue: The parameter
superuser_reserved_connections cannot be modified`. Ni el plan, ni `check_plan.py`, ni
Floci lo detectan: solo el catalogo de la familia lo dice. El preflight se ejecuta ANTES
de planificar contra `aws rds describe-engine-default-parameters`.

El catalogo de abajo reproduce las entradas reales observadas el 2026-10-05 para
`postgres17` (§27.4). `shared_buffers` es una entrada estatica y modificable de control.
"""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.terraform_datos.check_parametros import revisar
from scripts.terraform_datos.check_plan import PARAMETROS, PARAMETROS_DE_SISTEMA

RAIZ = Path(__file__).resolve().parents[2]


def _entrada(nombre, valor, modificable, tipo, origen):
    entrada = {"ParameterName": nombre, "IsModifiable": modificable, "ApplyType": tipo, "Source": origen}
    if valor is not None:
        entrada["ParameterValue"] = valor
    return entrada


CATALOGO_OBSERVADO = [
    _entrada("log_connections", None, True, "dynamic", "engine-default"),
    _entrada("log_disconnections", None, True, "dynamic", "engine-default"),
    _entrada("log_min_duration_statement", None, True, "dynamic", "engine-default"),
    _entrada("log_statement", None, True, "dynamic", "engine-default"),
    _entrada("rds.force_ssl", "1", True, "dynamic", "system"),
    _entrada("ssl_min_protocol_version", "TLSv1.2", True, "dynamic", "system"),
    _entrada("superuser_reserved_connections", "3", False, "static", "system"),
    _entrada("shared_buffers", "{DBInstanceClassMemory/32768}", True, "static", "system"),
]

#: El parametro no modificable que rompio el apply de H-031-3, junto a los explicitos vigentes.
CON_SUPERUSER = PARAMETROS | {("superuser_reserved_connections", "3", "pending-reboot")}
#: El conjunto historico completo que llego al apply de H-031-3 (D-22 original).
SIETE_DE_H0313 = PARAMETROS | {("rds.force_ssl", "1", "immediate"), ("ssl_min_protocol_version", "TLSv1.2", "immediate"),
                               ("superuser_reserved_connections", "3", "pending-reboot")}
INVARIANTES = {"superuser_reserved_connections": "3", "rds.force_ssl": "1", "ssl_min_protocol_version": "TLSv1.2"}


class Preflight(unittest.TestCase):
    def catalogo(self):
        return {"EngineDefaults": {"DBParameterGroupFamily": "postgres17",
                                   "Parameters": copy.deepcopy(CATALOGO_OBSERVADO)}}

    def rechaza(self, parametros, catalogo, codigo):
        with self.assertRaises(ValueError) as error:
            revisar(parametros, catalogo)
        self.assertTrue(str(error.exception).startswith(codigo), str(error.exception))

    def test_los_cuatro_parametros_explicitos_pasan_contra_el_catalogo_observado(self):
        resultado = revisar(PARAMETROS, self.catalogo())
        self.assertEqual(len(resultado["parametros"]), 4)
        self.assertEqual(resultado["sistema"], INVARIANTES)

    def test_el_conjunto_explicito_es_exactamente_el_de_d22_corregido(self):
        # RECOVERY-2 (§33): solo los cuatro realmente personalizados.
        self.assertEqual(PARAMETROS, {("log_connections", "1", "immediate"), ("log_disconnections", "1", "immediate"),
                                      ("log_min_duration_statement", "1000", "immediate"),
                                      ("log_statement", "ddl", "immediate")})
        self.assertEqual(PARAMETROS_DE_SISTEMA, INVARIANTES)
        self.assertFalse({n for n, _, _ in PARAMETROS} & set(PARAMETROS_DE_SISTEMA))

    def test_regresion_h0313_parametro_no_modificable_rechazado(self):
        self.rechaza(CON_SUPERUSER, self.catalogo(), "PARAM_NOT_MODIFIABLE superuser_reserved_connections")

    def test_el_conjunto_historico_de_h0313_se_rechaza(self):
        self.rechaza(SIETE_DE_H0313, self.catalogo(), "PARAM_SYSTEM_MANAGED rds.force_ssl")

    def test_un_parametro_de_sistema_nunca_se_gestiona_aunque_parezca_modificable(self):
        catalogo = self.catalogo()
        for p in catalogo["EngineDefaults"]["Parameters"]:
            if p["ParameterName"] == "superuser_reserved_connections":
                p["IsModifiable"] = True
        self.rechaza(CON_SUPERUSER, catalogo, "PARAM_SYSTEM_MANAGED superuser_reserved_connections")

    def test_rds_force_ssl_gestionado_por_terraform_rechazado(self):
        self.rechaza(PARAMETROS | {("rds.force_ssl", "1", "immediate")}, self.catalogo(),
                     "PARAM_SYSTEM_MANAGED rds.force_ssl")

    def test_ssl_min_protocol_version_gestionado_por_terraform_rechazado(self):
        self.rechaza(PARAMETROS | {("ssl_min_protocol_version", "TLSv1.2", "immediate")}, self.catalogo(),
                     "PARAM_SYSTEM_MANAGED ssl_min_protocol_version")

    def _invariante(self, nombre, **cambios):
        catalogo = self.catalogo()
        for p in catalogo["EngineDefaults"]["Parameters"]:
            if p["ParameterName"] == nombre:
                p.update(cambios)
        return catalogo

    def test_rds_force_ssl_distinto_de_1_rechazado(self):
        self.rechaza(PARAMETROS, self._invariante("rds.force_ssl", ParameterValue="0"), "SYSTEM_DEFAULT rds.force_ssl")

    def test_ssl_min_protocol_version_distinto_de_tls12_rechazado(self):
        for valor in ("TLSv1.1", "TLSv1.3"):
            with self.subTest(valor=valor):
                self.rechaza(PARAMETROS, self._invariante("ssl_min_protocol_version", ParameterValue=valor),
                             "SYSTEM_DEFAULT ssl_min_protocol_version")

    def test_invariante_que_deja_de_ser_de_sistema_rechazada(self):
        for nombre in INVARIANTES:
            with self.subTest(nombre=nombre):
                self.rechaza(PARAMETROS, self._invariante(nombre, Source="engine-default"), f"SYSTEM_DEFAULT {nombre}")

    def test_superuser_reserved_connections_modificable_rompe_la_invariante(self):
        self.rechaza(PARAMETROS, self._invariante("superuser_reserved_connections", IsModifiable=True),
                     "SYSTEM_DEFAULT superuser_reserved_connections")

    def test_invariante_ausente_del_catalogo_rechazada(self):
        for nombre in INVARIANTES:
            with self.subTest(nombre=nombre):
                catalogo = self.catalogo()
                catalogo["EngineDefaults"]["Parameters"] = [
                    p for p in catalogo["EngineDefaults"]["Parameters"] if p["ParameterName"] != nombre]
                self.rechaza(PARAMETROS, catalogo, f"SYSTEM_DEFAULT {nombre}")

    def test_parametro_desconocido_rechazado(self):
        self.rechaza(PARAMETROS | {("no_existe", "1", "immediate")}, self.catalogo(), "PARAM_UNKNOWN no_existe")

    def test_dinamico_con_pending_reboot_rechazado(self):
        parametros = (PARAMETROS - {("log_statement", "ddl", "immediate")}) | {("log_statement", "ddl", "pending-reboot")}
        self.rechaza(parametros, self.catalogo(), "PARAM_APPLY_METHOD log_statement")

    def test_estatico_con_immediate_rechazado(self):
        self.rechaza(PARAMETROS | {("shared_buffers", "1", "immediate")}, self.catalogo(),
                     "PARAM_APPLY_METHOD shared_buffers")

    def test_estatico_modificable_con_pending_reboot_admitido(self):
        revisar(PARAMETROS | {("shared_buffers", "1", "pending-reboot")}, self.catalogo())

    def test_apply_type_desconocido_rechazado(self):
        catalogo = self.catalogo()
        catalogo["EngineDefaults"]["Parameters"][0]["ApplyType"] = "otro"
        self.rechaza(PARAMETROS, catalogo, "PARAM_APPLY_TYPE log_connections")

    def test_valor_de_sistema_distinto_de_3_rompe_el_presupuesto(self):
        catalogo = self.catalogo()
        for p in catalogo["EngineDefaults"]["Parameters"]:
            if p["ParameterName"] == "superuser_reserved_connections":
                p["ParameterValue"] = "5"
        self.rechaza(PARAMETROS, catalogo, "SYSTEM_DEFAULT superuser_reserved_connections")

    def test_valor_de_sistema_ausente_del_catalogo_rechazado(self):
        catalogo = self.catalogo()
        catalogo["EngineDefaults"]["Parameters"] = [
            p for p in catalogo["EngineDefaults"]["Parameters"] if p["ParameterName"] != "superuser_reserved_connections"]
        self.rechaza(PARAMETROS, catalogo, "SYSTEM_DEFAULT superuser_reserved_connections")

    def test_catalogo_truncado_rechazado(self):
        catalogo = self.catalogo()
        catalogo["EngineDefaults"]["Marker"] = "pagina-2"
        self.rechaza(PARAMETROS, catalogo, "CATALOG_TRUNCATED")

    def test_otra_familia_rechazada(self):
        catalogo = self.catalogo()
        catalogo["EngineDefaults"]["DBParameterGroupFamily"] = "postgres16"
        self.rechaza(PARAMETROS, catalogo, "FAMILY")

    def test_entrada_duplicada_rechazada(self):
        catalogo = self.catalogo()
        catalogo["EngineDefaults"]["Parameters"].append(copy.deepcopy(CATALOGO_OBSERVADO[0]))
        self.rechaza(PARAMETROS, catalogo, "CATALOG_DUPLICATE log_connections")

    def test_sin_parametros_rechazado(self):
        self.rechaza(set(), self.catalogo(), "NO_PARAMETERS")


class Paginas(unittest.TestCase):
    """La API devuelve el catalogo en paginas; cada una declara su familia y todas menos la ultima un Marker.

    Observado el 2026-10-05: la salida que el AWS CLI fusiona al paginar solo conserva `Parameters`
    y descarta `DBParameterGroupFamily`. Por eso el runner lee las paginas crudas (`--no-paginate`
    y `--marker`) y la guarda exige la familia en cada una.
    """

    def paginas(self, cortes=(3, 6)):
        trozos, inicio = [], 0
        for fin in (*cortes, len(CATALOGO_OBSERVADO)):
            trozos.append(copy.deepcopy(CATALOGO_OBSERVADO[inicio:fin]))
            inicio = fin
        paginas = []
        for i, trozo in enumerate(trozos):
            defaults = {"DBParameterGroupFamily": "postgres17", "Parameters": trozo}
            if i < len(trozos) - 1:
                defaults["Marker"] = f"marca-{i}"
            paginas.append({"EngineDefaults": defaults})
        return paginas

    def rechaza(self, paginas, codigo):
        with self.assertRaises(ValueError) as error:
            revisar(PARAMETROS, paginas)
        self.assertTrue(str(error.exception).startswith(codigo), str(error.exception))

    def test_paginas_crudas_pasan(self):
        self.assertEqual(len(revisar(PARAMETROS, self.paginas())["parametros"]), 4)

    def test_salida_fusionada_del_cli_sin_familia_rechazada(self):
        fusionada = {"EngineDefaults": {"Parameters": copy.deepcopy(CATALOGO_OBSERVADO)}}
        with self.assertRaises(ValueError) as error:
            revisar(PARAMETROS, fusionada)
        self.assertEqual(str(error.exception), "FAMILY")

    def test_pagina_de_otra_familia_rechazada(self):
        paginas = self.paginas(); paginas[1]["EngineDefaults"]["DBParameterGroupFamily"] = "postgres16"
        self.rechaza(paginas, "FAMILY")

    def test_ultima_pagina_con_marker_rechazada(self):
        paginas = self.paginas(); paginas[-1]["EngineDefaults"]["Marker"] = "mas"
        self.rechaza(paginas, "CATALOG_TRUNCATED")

    def test_pagina_intermedia_sin_marker_rechazada(self):
        paginas = self.paginas(); paginas[0]["EngineDefaults"].pop("Marker")
        self.rechaza(paginas, "CATALOG_PAGES")

    def test_duplicado_entre_paginas_rechazado(self):
        paginas = self.paginas()
        paginas[2]["EngineDefaults"]["Parameters"].append(copy.deepcopy(CATALOGO_OBSERVADO[0]))
        self.rechaza(paginas, "CATALOG_DUPLICATE log_connections")

    def test_lista_vacia_rechazada(self):
        self.rechaza([], "CATALOG_EMPTY")


class Cli(unittest.TestCase):
    def ejecutar(self, catalogo):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "catalogo.json"
            ruta.write_text(json.dumps(catalogo), encoding="utf-8")
            return subprocess.run([sys.executable, "-B", "-m", "scripts.terraform_datos.check_parametros", str(ruta)],
                                  cwd=RAIZ, capture_output=True, text=True)

    def test_cli_acepta_el_catalogo_observado(self):
        r = self.ejecutar({"EngineDefaults": {"DBParameterGroupFamily": "postgres17", "Parameters": CATALOGO_OBSERVADO}})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["gate"], "PARAMETERS_OK")

    def test_cli_rechaza_sin_apply(self):
        catalogo = {"EngineDefaults": {"DBParameterGroupFamily": "postgres17", "Parameters": CATALOGO_OBSERVADO[:2]}}
        r = self.ejecutar(catalogo)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("PARAM_UNKNOWN", r.stderr)
        self.assertIn("No plan authorized", r.stderr)


if __name__ == "__main__":
    unittest.main()
