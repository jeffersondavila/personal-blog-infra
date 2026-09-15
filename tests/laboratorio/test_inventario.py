"""Revision del plan, idempotencia y verificacion de ausencia (matriz 33-36, 39-40).

`terraform apply` devolviendo 0 no demuestra que se creo lo previsto, y
`terraform state list` vacio no demuestra que se destruyo: eso solo dice que el
estado esta vacio. Estas guardas convierten las dos afirmaciones en
comprobaciones con contenido.
"""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from laboratorio import inventario as modulo  # noqa: E402


def plan(*cambios):
    return {"format_version": "1.2", "resource_changes": list(cambios)}


def cambio(tipo, *acciones, direccion="modulo.recurso", modo="managed"):
    return {
        "address": direccion,
        "type": tipo,
        "mode": modo,
        "change": {"actions": list(acciones)},
    }


class DataSourceTests(unittest.TestCase):
    """Un data source LEE; no crea, no cambia y no destruye nada.

    Terraform los emite en `resource_changes` con `mode: "data"` y accion
    `read`. Aplicarles la lista cerrada de tipos gestionados los rechazaria sin
    motivo: `aws_iam_policy_document` es la forma canonica de escribir una
    politica IAM y no materializa ningun recurso.
    """

    def test_data_source_no_se_juzga_como_recurso_gestionado(self):
        entrada = plan(
            cambio("aws_iam_role", "create"),
            cambio(
                "aws_iam_policy_document",
                "read",
                modo="data",
                direccion="module.identidad.data.aws_iam_policy_document.permisos",
            ),
        )
        resumen = modulo.revisar_plan(entrada, acciones_permitidas=("create",))
        self.assertEqual(resumen["create"], 1)

    def test_el_data_source_no_cuenta_como_cambio(self):
        entrada = plan(cambio("aws_iam_policy_document", "read", modo="data"))
        resumen = modulo.revisar_plan(entrada, acciones_permitidas=("create",))
        self.assertEqual(resumen.get("create", 0), 0)

    def test_data_source_que_no_solo_lee_aborta(self):
        """Si un `mode: data` declarase otra accion, no se deja pasar."""
        entrada = plan(cambio("aws_iam_policy_document", "create", modo="data"))
        with self.assertRaises(modulo.ErrorDeInventario):
            modulo.revisar_plan(entrada, acciones_permitidas=("create",))

    def test_recurso_gestionado_sin_modo_declarado_se_juzga_como_gestionado(self):
        """Omitir `mode` no debe ser una via para saltarse la lista cerrada."""
        entrada = {
            "resource_changes": [
                {
                    "address": "x",
                    "type": "aws_db_instance",
                    "change": {"actions": ["create"]},
                }
            ]
        }
        with self.assertRaises(modulo.ErrorDeInventario):
            modulo.revisar_plan(entrada, acciones_permitidas=("create",))


class PlanTests(unittest.TestCase):
    def test_plan_conforme_acepta(self):
        entrada = plan(
            cambio("aws_s3_bucket", "create"),
            cambio("aws_lambda_function", "create"),
            cambio("aws_apigatewayv2_api", "create"),
        )
        resumen = modulo.revisar_plan(entrada, acciones_permitidas=("create",))
        self.assertEqual(resumen["create"], 3)

    def test_plan_con_recurso_inesperado_aborta(self):
        entrada = plan(cambio("aws_s3_bucket", "create"), cambio("aws_db_instance", "create"))
        with self.assertRaises(modulo.ErrorDeInventario) as capturado:
            modulo.revisar_plan(entrada, acciones_permitidas=("create",))
        self.assertIn("aws_db_instance", str(capturado.exception))

    def test_plan_con_recurso_rds_aborta_siempre(self):
        """ADR-007: PostgreSQL vive en un VPS externo. Task/025 no crea RDS."""
        for tipo in ("aws_db_instance", "aws_rds_cluster", "aws_db_subnet_group"):
            with self.subTest(tipo=tipo):
                with self.assertRaises(modulo.ErrorDeInventario):
                    modulo.revisar_plan(plan(cambio(tipo, "create")), acciones_permitidas=("create",))

    def test_accion_inesperada_aborta(self):
        entrada = plan(cambio("aws_s3_bucket", "delete"))
        with self.assertRaises(modulo.ErrorDeInventario) as capturado:
            modulo.revisar_plan(entrada, acciones_permitidas=("create",))
        self.assertIn("delete", str(capturado.exception))

    def test_reemplazo_no_pasa_como_creacion(self):
        entrada = plan(cambio("aws_s3_bucket", "delete", "create"))
        with self.assertRaises(modulo.ErrorDeInventario):
            modulo.revisar_plan(entrada, acciones_permitidas=("create",))

    def test_no_op_no_cuenta_como_cambio(self):
        entrada = plan(cambio("aws_s3_bucket", "no-op"))
        resumen = modulo.revisar_plan(entrada, acciones_permitidas=("create",))
        self.assertEqual(resumen.get("create", 0), 0)

    def test_plan_vacio_aborta_cuando_se_espera_creacion(self):
        with self.assertRaises(modulo.ErrorDeInventario):
            modulo.revisar_plan(plan(), acciones_permitidas=("create",), minimo=1)

    def test_destroy_solo_admite_delete(self):
        entrada = plan(cambio("aws_s3_bucket", "delete"), cambio("aws_lambda_function", "delete"))
        resumen = modulo.revisar_plan(entrada, acciones_permitidas=("delete",))
        self.assertEqual(resumen["delete"], 2)

    def test_plan_ilegible_aborta(self):
        for entrada in ({}, {"resource_changes": "no-es-lista"}, {"resource_changes": [{}]}):
            with self.subTest(entrada=entrada):
                with self.assertRaises(modulo.ErrorDeInventario):
                    modulo.revisar_plan(entrada, acciones_permitidas=("create",))


class IdempotenciaTests(unittest.TestCase):
    def test_exit_0_es_idempotente(self):
        self.assertEqual(modulo.exigir_sin_cambios(0), {})

    def test_exit_2_aborta(self):
        with self.assertRaises(modulo.ErrorDeInventario) as capturado:
            modulo.exigir_sin_cambios(2)
        self.assertIn("2", str(capturado.exception))

    def test_exit_1_aborta(self):
        with self.assertRaises(modulo.ErrorDeInventario):
            modulo.exigir_sin_cambios(1)


def cambio_de_atributos(tipo, antes, despues, direccion="modulo.recurso"):
    return {
        "address": direccion,
        "type": tipo,
        "mode": "managed",
        "change": {"actions": ["update"], "before": antes, "after": despues},
    }


class DiferenciasDelDestinoTests(unittest.TestCase):
    """Un `exit 2` solo se acepta si CADA atributo que cambia esta declarado.

    No es una valvula de escape: la tolerancia se declara por tipo de recurso y
    por atributo, con su motivo. Cualquier otro cambio sigue abortando, y el
    resultado se informa como «idempotente salvo la diferencia documentada», no
    como idempotente a secas.
    """

    def setUp(self):
        self.toleradas = (
            modulo.DiferenciaDelDestino(
                tipo="aws_ssm_parameter",
                atributo="tags_all",
                motivo="el emulador descarta las etiquetas en PutParameter",
            ),
        )

    def test_solo_la_diferencia_declarada_se_tolera(self):
        plan_json = plan(
            cambio_de_atributos(
                "aws_ssm_parameter", {"tags_all": {}}, {"tags_all": {"Proyecto": "x"}}
            )
        )
        informe = modulo.exigir_sin_cambios(
            2, plan=plan_json, diferencias_toleradas=self.toleradas
        )
        self.assertEqual(informe["aws_ssm_parameter.tags_all"], 1)

    def test_otro_atributo_del_mismo_tipo_aborta(self):
        plan_json = plan(
            cambio_de_atributos("aws_ssm_parameter", {"value": "a"}, {"value": "b"})
        )
        with self.assertRaises(modulo.ErrorDeInventario) as capturado:
            modulo.exigir_sin_cambios(2, plan=plan_json, diferencias_toleradas=self.toleradas)
        self.assertIn("value", str(capturado.exception))

    def test_el_mismo_atributo_en_otro_tipo_aborta(self):
        plan_json = plan(
            cambio_de_atributos(
                "aws_lambda_function", {"tags_all": {}}, {"tags_all": {"Proyecto": "x"}}
            )
        )
        with self.assertRaises(modulo.ErrorDeInventario):
            modulo.exigir_sin_cambios(2, plan=plan_json, diferencias_toleradas=self.toleradas)

    def test_una_creacion_pendiente_aborta_aunque_haya_tolerancias(self):
        plan_json = plan(cambio("aws_s3_bucket", "create"))
        with self.assertRaises(modulo.ErrorDeInventario) as capturado:
            modulo.exigir_sin_cambios(2, plan=plan_json, diferencias_toleradas=self.toleradas)
        self.assertIn("create", str(capturado.exception))

    def test_una_destruccion_pendiente_aborta(self):
        plan_json = plan(cambio("aws_s3_bucket", "delete"))
        with self.assertRaises(modulo.ErrorDeInventario):
            modulo.exigir_sin_cambios(2, plan=plan_json, diferencias_toleradas=self.toleradas)

    def test_sin_tolerancias_declaradas_el_exit_2_sigue_abortando(self):
        plan_json = plan(
            cambio_de_atributos(
                "aws_ssm_parameter", {"tags_all": {}}, {"tags_all": {"Proyecto": "x"}}
            )
        )
        with self.assertRaises(modulo.ErrorDeInventario):
            modulo.exigir_sin_cambios(2, plan=plan_json)


class AusenciaTests(unittest.TestCase):
    def test_inventario_vacio_acepta(self):
        modulo.exigir_inventario_vacio({"s3": [], "lambda": [], "ssm": []})

    def test_inventario_con_residuo_aborta_y_lo_nombra(self):
        with self.assertRaises(modulo.ErrorDeInventario) as capturado:
            modulo.exigir_inventario_vacio({"s3": ["personal-blog-media-local"], "lambda": []})
        mensaje = str(capturado.exception)
        self.assertIn("s3", mensaje)
        self.assertIn("personal-blog-media-local", mensaje)

    def test_inventario_sin_servicios_aborta(self):
        """Un inventario vacio de servicios no demuestra ausencia: demuestra que no se miro."""
        with self.assertRaises(modulo.ErrorDeInventario):
            modulo.exigir_inventario_vacio({})

    def test_laboratorio_limpio_acepta(self):
        modulo.exigir_laboratorio_limpio({"contenedores": [], "redes": [], "volumenes": []})

    def test_residuo_del_laboratorio_aborta(self):
        with self.assertRaises(modulo.ErrorDeInventario) as capturado:
            modulo.exigir_laboratorio_limpio(
                {"contenedores": ["lab-floci-1"], "redes": [], "volumenes": []}
            )
        self.assertIn("lab-floci-1", str(capturado.exception))


if __name__ == "__main__":
    unittest.main()
