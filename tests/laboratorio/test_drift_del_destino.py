"""`resource_drift` del laboratorio: lista CERRADA, exacta y fail-closed (H-031-1A).

Por que existe
--------------
El gate de idempotencia acotaba las diferencias del destino en `resource_changes`,
pero nunca leia `resource_drift`. En H-031-1A el segundo plan del root de datos
trajo `aws_db_instance.domain_dns_ips: null -> []` en esa seccion y nada lo
habria detenido: el `exit 2` se justificaba con `resource_changes` y el drift
pasaba por fuera. Un `exit 0` ni siquiera se miraba.

Desde H-031-1A cada entrada de `resource_drift` debe coincidir con una
declaracion por DIRECCION, tipo, acciones exactas, conjunto EXACTO de atributos
y forma de la transicion. No basta con que los atributos sean un subconjunto de
los declarados: eso dejaria pasar combinaciones nunca observadas.

Estas pruebas no relajan el gate productivo: `scripts/terraform_datos/check_plan.py`
sigue exigiendo `resource_drift` vacio (ver `tests/terraform_datos`).
"""

from pathlib import Path
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from laboratorio import inventario as modulo  # noqa: E402
from laboratorio import laboratorio as lanzador  # noqa: E402
import drift_observado as obs  # noqa: E402

DECLARADO = lanzador.DRIFT_DEL_DESTINO_LOCAL_DE_DATOS
CAMBIOS_DECLARADOS = lanzador.DIFERENCIAS_DEL_DESTINO_LOCAL_DE_DATOS


def revisar(plan):
    return modulo.revisar_drift(plan, drift_tolerado=DECLARADO)


class DriftObservadoTests(unittest.TestCase):
    """El plan real de H-031-1A, y solo el, pasa la guarda."""

    def test_el_drift_observado_se_acepta_con_atributos_exactos(self):
        informe = revisar(obs.plan_de_datos_observado())
        self.assertEqual(
            informe,
            {
                obs.INSTANCIA: ["domain_dns_ips", "enabled_cloudwatch_logs_exports"],
                obs.GRUPO_DE_PARAMETROS: ["parameter"],
                obs.GRUPO_ADMIN: ["egress"],
                obs.GRUPO_LAMBDA: ["egress"],
                obs.GRUPO_RDS: ["ingress"],
            },
        )

    def test_el_gate_completo_acepta_el_segundo_plan_observado(self):
        informe = modulo.exigir_sin_cambios(
            2,
            plan=obs.plan_de_datos_observado(),
            diferencias_toleradas=CAMBIOS_DECLARADOS,
            drift_tolerado=DECLARADO,
        )
        self.assertEqual(informe["aws_db_instance.port"], 1)
        self.assertNotIn("aws_db_instance.domain_dns_ips", informe)

    def test_sin_drift_no_hay_nada_que_justificar(self):
        plan = obs.plan_de_datos_observado()
        del plan["resource_drift"]  # Terraform omite la seccion cuando esta vacia.
        self.assertEqual(revisar(plan), {})

    def test_una_entrada_declarada_puede_faltar_del_todo(self):
        # Que el destino deje de diferir nunca es inseguro.
        plan = obs.plan_de_datos_observado()
        plan["resource_drift"] = [obs.entrada(plan, obs.GRUPO_ADMIN)]
        self.assertEqual(revisar(plan), {obs.GRUPO_ADMIN: ["egress"]})


class FalloEstructuralTests(unittest.TestCase):
    """Regresion del fallo que encontro Codex: el drift vivia fuera del gate."""

    def test_exit_2_con_cambios_tolerados_y_drift_no_declarado_aborta(self):
        plan = obs.plan_de_datos_observado()
        with self.assertRaises(modulo.ErrorDeInventario) as capturado:
            modulo.exigir_sin_cambios(
                2, plan=plan, diferencias_toleradas=CAMBIOS_DECLARADOS
            )
        self.assertIn("resource_drift", str(capturado.exception))

    def test_exit_0_con_drift_no_declarado_aborta(self):
        plan = obs.plan_de_datos_observado()
        plan["resource_changes"] = []
        with self.assertRaises(modulo.ErrorDeInventario) as capturado:
            modulo.exigir_sin_cambios(0, plan=plan)
        self.assertIn(obs.INSTANCIA, str(capturado.exception))

    def test_exit_0_con_plan_y_drift_declarado_es_idempotente(self):
        plan = obs.plan_de_datos_observado()
        plan["resource_changes"] = []
        self.assertEqual(
            modulo.exigir_sin_cambios(0, plan=plan, drift_tolerado=DECLARADO), {}
        )

    def test_exit_0_que_contradice_su_plan_aborta(self):
        plan = obs.plan_de_datos_observado()
        with self.assertRaises(modulo.ErrorDeInventario):
            modulo.exigir_sin_cambios(0, plan=plan, drift_tolerado=DECLARADO)

    def test_cambios_diferidos_abortan(self):
        plan = obs.plan_de_datos_observado()
        plan["deferred_changes"] = [{"reason": "provider_config_unknown"}]
        with self.assertRaises(modulo.ErrorDeInventario) as capturado:
            revisar(plan)
        self.assertIn("deferred_changes", str(capturado.exception))

    def test_drift_ilegible_aborta(self):
        casos = {
            "no es lista": lambda p: p.update(resource_drift={"x": 1}),
            "entrada no es objeto": lambda p: p["resource_drift"].append("x"),
            "sin change": lambda p: obs.entrada(p, obs.GRUPO_ADMIN).pop("change"),
            "modo data": lambda p: obs.entrada(p, obs.GRUPO_ADMIN).update(mode="data"),
            "direccion repetida": lambda p: p["resource_drift"].append(
                obs.entrada(obs.plan_de_datos_observado(), obs.GRUPO_ADMIN)
            ),
        }
        for nombre, mutar in casos.items():
            with self.subTest(caso=nombre):
                plan = obs.plan_de_datos_observado()
                mutar(plan)
                with self.assertRaises(modulo.ErrorDeInventario):
                    revisar(plan)


class ControlesNegativosTests(unittest.TestCase):
    """Cada variacion de lo observado debe detenerse."""

    def rechaza(self, plan, *fragmentos):
        with self.assertRaises(modulo.ErrorDeInventario) as capturado:
            revisar(plan)
        for fragmento in fragmentos:
            self.assertIn(fragmento, str(capturado.exception))

    def test_otro_atributo_de_la_instancia_rds(self):
        plan = obs.plan_de_datos_observado()
        cambio = obs.entrada(plan, obs.INSTANCIA)["change"]
        cambio["after"]["port"] = 5432
        self.rechaza(plan, "port")

    def test_mas_atributos_que_los_declarados(self):
        plan = obs.plan_de_datos_observado()
        cambio = obs.entrada(plan, obs.INSTANCIA)["change"]
        cambio["before"]["storage_type"] = "gp2"
        cambio["after"]["storage_type"] = "gp3"
        self.rechaza(plan, "storage_type")

    def test_menos_atributos_que_los_declarados(self):
        plan = obs.plan_de_datos_observado()
        cambio = obs.entrada(plan, obs.INSTANCIA)["change"]
        cambio["after"]["enabled_cloudwatch_logs_exports"] = ["postgresql"]
        self.rechaza(plan, "enabled_cloudwatch_logs_exports")

    def test_otro_valor_de_domain_dns_ips(self):
        casos = {
            "dos IP": (None, ["10.0.0.2", "10.0.0.3"]),
            "sentido inverso": ([], None),
            "de lista con IP a vacia": (["10.0.0.2", "10.0.0.3"], []),
            "cadena vacia": (None, ""),
        }
        for nombre, (antes, despues) in casos.items():
            with self.subTest(caso=nombre):
                plan = obs.plan_de_datos_observado()
                cambio = obs.entrada(plan, obs.INSTANCIA)["change"]
                cambio["before"]["domain_dns_ips"] = antes
                cambio["after"]["domain_dns_ips"] = despues
                self.rechaza(plan, "domain_dns_ips")

    def test_otro_valor_de_los_logs_exportados(self):
        plan = obs.plan_de_datos_observado()
        obs.entrada(plan, obs.INSTANCIA)["change"]["after"][
            "enabled_cloudwatch_logs_exports"
        ] = ["upgrade"]
        self.rechaza(plan, "enabled_cloudwatch_logs_exports")

    def test_el_grupo_de_parametros_devuelve_otros_valores(self):
        plan = obs.plan_de_datos_observado()
        obs.entrada(plan, obs.GRUPO_DE_PARAMETROS)["change"]["after"]["parameter"] = [
            {"apply_method": "immediate", "name": "rds.force_ssl", "value": "0"}
        ]
        self.rechaza(plan, "parameter")

    def test_otro_tipo_de_recurso_en_la_misma_direccion(self):
        plan = obs.plan_de_datos_observado()
        obs.entrada(plan, obs.INSTANCIA)["type"] = "aws_rds_cluster"
        self.rechaza(plan, obs.INSTANCIA)

    def test_otra_accion(self):
        for acciones in (["delete"], ["create"], ["delete", "create"], ["update", "update"]):
            with self.subTest(acciones=acciones):
                plan = obs.plan_de_datos_observado()
                obs.entrada(plan, obs.INSTANCIA)["change"]["actions"] = acciones
                self.rechaza(plan, obs.INSTANCIA)

    def test_drift_en_un_recurso_no_autorizado(self):
        plan = obs.plan_de_datos_observado()
        plan["resource_drift"].append(
            {
                "address": "module.red.aws_vpc.this",
                "mode": "managed",
                "type": "aws_vpc",
                "change": {
                    "actions": ["update"],
                    "before": {"enable_dns_support": True},
                    "after": {"enable_dns_support": False},
                },
            }
        )
        self.rechaza(plan, "module.red.aws_vpc.this")

    def test_un_grupo_de_seguridad_gana_una_regla_no_gestionada(self):
        plan = obs.plan_de_datos_observado()
        abierta = dict(obs.SALIDA_POR_OMISION, protocol="tcp", from_port=5432, to_port=5432)
        obs.entrada(plan, obs.GRUPO_RDS)["change"]["after"]["ingress"].append(abierta)
        self.rechaza(plan, obs.GRUPO_RDS, "ingress")

    def test_un_grupo_de_seguridad_pierde_una_regla(self):
        plan = obs.plan_de_datos_observado()
        despues = obs.entrada(plan, obs.GRUPO_ADMIN)["change"]["after"]
        despues["egress"] = despues["egress"][1:]
        self.rechaza(plan, obs.GRUPO_ADMIN, "egress")

    def test_falta_la_regla_separada_que_justifica_el_drift(self):
        plan = obs.plan_de_datos_observado()
        modulo_red = plan["prior_state"]["values"]["root_module"]["child_modules"][0]
        modulo_red["resources"] = [
            r for r in modulo_red["resources"] if r["name"] != "lambda_a_s3"
        ]
        self.rechaza(plan, obs.GRUPO_LAMBDA)

    def test_la_regla_separada_difiere_de_la_regla_en_linea(self):
        plan = obs.plan_de_datos_observado()
        modulo_red = plan["prior_state"]["values"]["root_module"]["child_modules"][0]
        for regla in modulo_red["resources"]:
            if regla["name"] == "admin_a_rds":
                regla["values"]["to_port"] = 5433
        self.rechaza(plan, obs.GRUPO_ADMIN)

    def test_sg_rds_con_drift_de_salida(self):
        plan = obs.plan_de_datos_observado()
        obs.entrada(plan, obs.GRUPO_RDS)["change"]["after"]["egress"] = []
        self.rechaza(plan, obs.GRUPO_RDS, "egress")

    def test_otro_atributo_de_un_grupo_de_seguridad(self):
        plan = obs.plan_de_datos_observado()
        obs.entrada(plan, obs.GRUPO_LAMBDA)["change"]["after"]["revoke_rules_on_delete"] = True
        self.rechaza(plan, "revoke_rules_on_delete")


class DeclaracionTests(unittest.TestCase):
    def test_cada_entrada_es_exacta_y_tiene_motivo(self):
        direcciones = [d.direccion for d in DECLARADO]
        self.assertEqual(len(direcciones), len(set(direcciones)))
        for declarada in DECLARADO:
            with self.subTest(direccion=declarada.direccion):
                self.assertEqual(declarada.acciones, ("update",))
                self.assertTrue(declarada.transiciones)
                self.assertGreater(len(declarada.motivo), 40)
                for _, forma in declarada.transiciones:
                    self.assertIn(forma, modulo.FORMAS_DE_TRANSICION)

    def test_la_declaracion_rechaza_formas_y_atributos_invalidos(self):
        with self.assertRaises(ValueError):
            modulo.DriftDelDestino(
                direccion="x.y", tipo="x", acciones=("update",),
                transiciones=(("a", "cualquier_cosa"),), motivo="m" * 50,
            )
        with self.assertRaises(ValueError):
            modulo.DriftDelDestino(
                direccion="x.y", tipo="x", acciones=("update",),
                transiciones=(("a", "lista_a_vacia"), ("a", "nulo_a_lista_vacia")),
                motivo="m" * 50,
            )
        with self.assertRaises(ValueError):
            modulo.DriftDelDestino(
                direccion="x.y", tipo="x", acciones=("update",),
                transiciones=(), motivo="m" * 50,
            )

    def test_domain_dns_ips_solo_se_tolera_en_drift_y_en_un_sentido(self):
        self.assertNotIn(
            ("aws_db_instance", "domain_dns_ips"),
            {(d.tipo, d.atributo) for d in CAMBIOS_DECLARADOS},
        )
        formas = {
            (d.tipo, atributo): forma
            for d in DECLARADO
            for atributo, forma in d.transiciones
        }
        self.assertEqual(
            formas[("aws_db_instance", "domain_dns_ips")], "nulo_a_lista_vacia"
        )

    def test_el_root_de_aplicacion_no_declara_drift(self):
        self.assertEqual(lanzador.DIFERENCIAS_DEL_DESTINO_LOCAL, ())


def _proceso(codigo, stdout=""):
    return subprocess.CompletedProcess(args=[], returncode=codigo, stdout=stdout, stderr="")


class CableadoDelRootDeDatosTests(unittest.TestCase):
    """El segundo plan de datos SIEMPRE se lee en JSON, tambien con exit 0."""

    def ejecutar(self, codigo, plan):
        llamadas = []

        def terraform_falso(binario, destino, argumentos, **opciones):
            llamadas.append(list(argumentos))
            if argumentos[0] == "plan":
                return _proceso(codigo)
            if argumentos[0] == "show":
                return _proceso(0, json.dumps(plan))
            raise AssertionError(f"llamada inesperada: {argumentos}")

        with patch.object(lanzador, "terraform", terraform_falso):
            resultado = lanzador.idempotencia_del_root_de_datos(Path("tf"), object())
        return resultado, llamadas

    def test_un_solo_plan_guardado_con_detailed_exitcode(self):
        _, llamadas = self.ejecutar(2, obs.plan_de_datos_observado())
        planes = [a for a in llamadas if a[0] == "plan"]
        self.assertEqual(len(planes), 1)
        self.assertIn("-detailed-exitcode", planes[0])
        self.assertIn(f"-out={lanzador.ROOT_DE_DATOS.plan_guardado}", planes[0])
        self.assertIn(["show", "-json", str(lanzador.ROOT_DE_DATOS.plan_guardado)], llamadas)

    def test_exit_2_observado_devuelve_cambios_y_drift(self):
        resultado, _ = self.ejecutar(2, obs.plan_de_datos_observado())
        self.assertIn("aws_db_instance.port", resultado["cambios"])
        self.assertEqual(
            resultado["drift"][obs.INSTANCIA],
            ["domain_dns_ips", "enabled_cloudwatch_logs_exports"],
        )

    def test_exit_0_tambien_lee_el_plan_y_aborta_con_drift_no_declarado(self):
        plan = obs.plan_de_datos_observado()
        plan["resource_changes"] = []
        plan["resource_drift"].append(
            {
                "address": "module.red.aws_subnet.privada[\"a\"]",
                "mode": "managed",
                "type": "aws_subnet",
                "change": {
                    "actions": ["update"],
                    "before": {"map_public_ip_on_launch": False},
                    "after": {"map_public_ip_on_launch": True},
                },
            }
        )
        with self.assertRaises(modulo.ErrorDeInventario):
            self.ejecutar(0, plan)

    def test_exit_1_aborta_sin_leer_el_plan(self):
        with self.assertRaises(modulo.ErrorDeInventario):
            self.ejecutar(1, obs.plan_de_datos_observado())

    def test_el_canario_en_el_plan_aborta(self):
        plan = obs.plan_de_datos_observado()
        plan["variables"] = {"x": {"value": lanzador.CONTRASENA_DEL_LABORATORIO}}
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            self.ejecutar(2, plan)


if __name__ == "__main__":
    unittest.main()
