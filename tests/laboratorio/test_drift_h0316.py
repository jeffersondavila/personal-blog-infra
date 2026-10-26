"""Idempotencia del root de datos con H-031-5 a H-031-9 y H-031-6 cableados (ciclo del 2026-10-19).

El ciclo completo del laboratorio se detuvo en la idempotencia: el gate cerrado de `resource_drift` (H-031-1A) leyo
entradas que nadie habia declarado. Se declaran SOLO las observadas, con la misma estrechez que H-031-1A:
- por DIRECCION, acciones exactas, conjunto EXACTO de atributos y FORMA de cada transicion;
- dos formas nuevas, ambas con antes Y despues fijos:
  - `refleja_politicas_en_linea`: `inline_policy` pasa de `[]` a EXACTAMENTE las politicas en linea que el state
    asigna a ese rol, por nombre y contenido, como hace `agrega_reglas_separadas` con las reglas de un grupo;
  - `nulo_a_mapa_vacio`: antes `null`, despues `{}`.
- `datapoints_to_alarm` y `extended_statistic` de las alarmas, en `resource_changes`, por tipo y atributo.

Origen de cada declaracion:
- **Representacion del provider** (SDKv2), observada TAMBIEN contra AWS real: las listas de acciones de las alarmas
  (reporte §47.7), el reflejo y las etiquetas de los roles (§47.9 y §49.15) y `layers` (§49.15). Alli las resolvio un
  refresh-only guardado y autorizado; la convergencia productiva sigue exigiendo `resource_drift` vacio.
- **Diferencia del emulador**: `DescribeAlarms` de Floci 2.1.0 no devuelve `DatapointsToAlarm` ni
  `ExtendedStatistic` (llamada directa al emulador, 2026-10-19); AWS si los devolvio en el readback de H-031-8.

Nada de esto viaja a los modulos: ni `ignore_changes`, ni tolerancia productiva.
"""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from laboratorio import inventario as modulo  # noqa: E402
from laboratorio import laboratorio as lanzador  # noqa: E402
import drift_observado_h0316 as obs  # noqa: E402

DECLARADO = lanzador.DRIFT_DEL_DESTINO_LOCAL_DE_DATOS
CAMBIOS_DECLARADOS = lanzador.DIFERENCIAS_DEL_DESTINO_LOCAL_DE_DATOS

# Floci 2.3.0: el drift de RDS incluye un instante movil, y su contrato se evalua contra un `ahora` fijo.
_RELOJ = patch.object(modulo, "_ahora", return_value=obs.base.AHORA)


def setUpModule():
    _RELOJ.start()


def tearDownModule():
    _RELOJ.stop()


def revisar(plan):
    return modulo.revisar_drift(plan, drift_tolerado=DECLARADO)


def rechaza(caso, plan, fragmento):
    with caso.assertRaises(modulo.ErrorDeInventario) as error:
        revisar(plan)
    caso.assertIn(fragmento, str(error.exception))


class SegundoPlanObservadoH0316Tests(unittest.TestCase):
    def test_el_drift_observado_se_acepta_con_atributos_exactos(self):
        informe = revisar(obs.plan_de_datos_observado())
        for senal in obs.SENALES:
            self.assertEqual(informe[obs.ALARMA.format(senal)],
                             ["alarm_actions", "insufficient_data_actions", "ok_actions"])
        self.assertEqual(informe[obs.ROL_EJECUTORA], ["inline_policy"])
        self.assertEqual(informe[obs.FUNCION], ["layers"])
        self.assertEqual(informe[obs.ROL_GRAFANA], ["inline_policy", "tags"])
        self.assertEqual(informe[obs.base.GRUPO_ADMIN], ["egress"])

    def test_el_gate_completo_acepta_el_segundo_plan_observado(self):
        informe = modulo.exigir_sin_cambios(2, plan=obs.plan_de_datos_observado(),
                                            diferencias_toleradas=CAMBIOS_DECLARADOS, drift_tolerado=DECLARADO)
        self.assertNotIn("aws_cloudwatch_metric_alarm.datapoints_to_alarm", informe)
        self.assertEqual(informe["aws_cloudwatch_metric_alarm.extended_statistic"], 2)
        self.assertNotIn("aws_ssm_parameter.key_id", informe)


class ControlesNegativosH0316Tests(unittest.TestCase):
    def test_una_alarma_con_un_atributo_de_mas(self):
        plan = obs.plan_de_datos_observado()
        obs.entrada(plan, obs.ALARMA.format("cpu"))["change"]["after"]["threshold"] = 1
        rechaza(self, plan, "threshold")

    def test_una_lista_de_acciones_que_no_queda_vacia(self):
        plan = obs.plan_de_datos_observado()
        obs.entrada(plan, obs.ALARMA.format("memoria"))["change"]["after"]["alarm_actions"] = [
            "arn:aws:sns:us-east-1:000000000000:alertas"]
        rechaza(self, plan, "alarm_actions")

    def test_el_reflejo_con_una_politica_que_el_state_no_tiene(self):
        plan = obs.plan_de_datos_observado()
        obs.entrada(plan, obs.ROL_EJECUTORA)["change"]["after"]["inline_policy"].append(
            {"name": "ajena", "policy": '{"Version": "2012-10-17", "Statement": []}'})
        rechaza(self, plan, "inline_policy")

    def test_el_reflejo_al_que_le_falta_una_politica_del_state(self):
        plan = obs.plan_de_datos_observado()
        obs.entrada(plan, obs.ROL_EJECUTORA)["change"]["after"]["inline_policy"].pop()
        rechaza(self, plan, "inline_policy")

    def test_el_reflejo_con_otro_contenido(self):
        plan = obs.plan_de_datos_observado()
        obs.entrada(plan, obs.ROL_GRAFANA)["change"]["after"]["inline_policy"][0]["policy"] = (
            '{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}')
        rechaza(self, plan, "inline_policy")

    def test_el_reflejo_no_parte_de_una_lista_vacia(self):
        plan = obs.plan_de_datos_observado()
        entrada = obs.entrada(plan, obs.ROL_EJECUTORA)["change"]
        entrada["before"]["inline_policy"] = list(entrada["after"]["inline_policy"][:1])
        rechaza(self, plan, "inline_policy")

    def test_etiquetas_que_no_quedan_vacias(self):
        plan = obs.plan_de_datos_observado()
        obs.entrada(plan, obs.ROL_GRAFANA)["change"]["after"]["tags"] = {"Clave": "valor"}
        rechaza(self, plan, "tags")

    def test_la_funcion_con_otro_atributo(self):
        plan = obs.plan_de_datos_observado()
        obs.entrada(plan, obs.FUNCION)["change"]["after"]["timeout"] = 60
        rechaza(self, plan, "timeout")

    def test_sg_admin_sin_la_regla_separada_de_s3_en_el_state(self):
        plan = obs.plan_de_datos_observado()
        hijos = plan["prior_state"]["values"]["root_module"]["child_modules"]
        exportacion = next(h for h in hijos if h["address"] == "module.exportacion")
        exportacion["resources"] = [r for r in exportacion["resources"]
                                    if r["type"] != "aws_vpc_security_group_egress_rule"]
        rechaza(self, plan, "egress")

    def test_un_cambio_planificado_de_alarma_no_declarado(self):
        plan = obs.plan_de_datos_observado()
        cambio = next(c for c in plan["resource_changes"] if c["address"] == obs.ALARMA.format("escritura"))
        cambio["change"]["after"]["threshold"] = 7
        with self.assertRaises(modulo.ErrorDeInventario):
            modulo.exigir_sin_cambios(2, plan=plan, diferencias_toleradas=CAMBIOS_DECLARADOS,
                                      drift_tolerado=DECLARADO)


class DeclaracionH0316Tests(unittest.TestCase):
    def test_las_formas_nuevas_solo_donde_tienen_sentido(self):
        with self.assertRaises(ValueError):
            modulo.DriftDelDestino(direccion="x", tipo="aws_iam_role", acciones=("update",),
                                   transiciones=(("tags", "refleja_politicas_en_linea"),), motivo="m")
        modulo.DriftDelDestino(direccion="x", tipo="aws_iam_role", acciones=("update",),
                               transiciones=(("inline_policy", "refleja_politicas_en_linea"),
                                             ("tags", "nulo_a_mapa_vacio")), motivo="m")

    def test_cada_declaracion_nueva_tiene_motivo_y_origen(self):
        direcciones = {d.direccion: d for d in DECLARADO}
        for direccion in [obs.ALARMA.format(s) for s in obs.SENALES] + [obs.ROL_EJECUTORA, obs.FUNCION,
                                                                        obs.ROL_GRAFANA]:
            with self.subTest(direccion=direccion):
                self.assertIn(direccion, direcciones)
                self.assertIn("AWS real", direcciones[direccion].motivo)
        motivos = {(d.tipo, d.atributo): d.motivo for d in CAMBIOS_DECLARADOS}
        for atributo in ("extended_statistic",):
            with self.subTest(atributo=atributo):
                self.assertIn("DescribeAlarms", motivos[("aws_cloudwatch_metric_alarm", atributo)])
        # Floci 2.3.0 ya devuelve DatapointsToAlarm: su tolerancia se retiro.
        self.assertNotIn(("aws_cloudwatch_metric_alarm", "datapoints_to_alarm"), motivos)


if __name__ == "__main__":
    unittest.main()
