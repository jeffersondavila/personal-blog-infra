"""La topologia de roots debe gobernar TODOS los comandos (DEF-030-2, Task/031).

Por que este archivo existe
---------------------------
La enmienda `H-030-4` extrajo el almacenamiento de medios a su propio root, con su
propio state, y cablo esa topologia **solo** en `comando_ciclo`. Los cinco
subcomandos de runbook —`crear`, `validar`, `rollback`, `destruir`, `recuperar`—
siguieron operando sobre un unico root.

Eso no es cosmetico: son los comandos que los runbooks usan en una incidencia.
`destruir` destruia los 13 recursos del root de aplicacion y despues exigia que
el inventario del emulador estuviera vacio; como el bucket pertenece ahora al
otro root, abortaba con `ErrorDeInventario` dejando el bucket en pie.

Estas pruebas fijan el requisito: **una sola autoridad** sobre el orden, la
cobertura y el contrato entre roots, y ningun comando que asuma un root unico.

`Task/031` (H-031-1, DH-1) anade el tercer root, `terraform-datos` —red privada y
RDS—, entre medios y aplicacion. Las pruebas cubren ahora los tres, y las del
root de datos incluyen el canario de DH-2: la contrasena master no puede
aparecer en el plan, el state ni las salidas.
"""

from dataclasses import replace
from pathlib import Path
import ast
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import nullcontext, ExitStack
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from laboratorio import laboratorio as lanzador  # noqa: E402

BUCKET = "blog-lab-medios"
ARN = f"arn:aws:s3:::{BUCKET}"

#: Los comandos que crean, reconcilian, leen o destruyen infraestructura. Todos
#: deben conocer los tres roots; `inspeccionar-sdk` no toca Terraform.
COMANDOS_DE_INFRAESTRUCTURA = ("ciclo", "crear", "validar", "rollback", "recuperar", "destruir")


class CorredorDeMentira:
    """Registra las invocaciones de Terraform sin ejecutar ninguna."""

    def __init__(self, salidas=None, fallar_en=None):
        self.invocaciones: list[tuple[str, str]] = []
        self._salidas = salidas or {}
        self._fallar_en = fallar_en or ()

    def __call__(self, binario, destino, argumentos, *, raiz=None, **resto):
        nombre_del_root = Path(raiz).name if raiz is not None else "<sin raiz>"
        operacion = argumentos[0] if argumentos else ""
        if argumentos[:2] == ["output", "-json"]:
            operacion = "output"
        self.invocaciones.append((nombre_del_root, operacion))
        if (nombre_del_root, operacion) in self._fallar_en:
            raise lanzador.ErrorDelLaboratorio(
                f"fallo simulado en {nombre_del_root}/{operacion}"
            )
        salida = self._salidas.get((nombre_del_root, operacion), "")
        if operacion == "show" and not salida:
            import json
            salida = json.dumps({"resource_changes": [{
                "address": "module.almacenamiento.aws_s3_bucket.medios",
                "type": "aws_s3_bucket", "change": {"actions": ["create"]},
            }]})
        return subprocess.CompletedProcess(args=[], returncode=0, stdout=salida, stderr="")

    def roots(self, operacion):
        return [root for root, op in self.invocaciones if op == operacion]


def herramental_de_mentira(corredor, *, vaciados=None):
    """Herramental con las operaciones externas sustituidas por registros."""
    registro_de_vaciados = vaciados if vaciados is not None else []
    inicializados: list[str] = []
    variables: list[str] = []

    def inicializar(binario, destino, *, solo_lectura, root):
        inicializados.append(root.nombre)
        corredor(binario, destino, ["init"], raiz=root.directorio)

    def escribir_medios(destino):
        variables.append("medios")

    def escribir_aplicacion(destino, zip_de_lambda, medios=None):
        variables.append(f"aplicacion:{(medios or {}).get('nombre_del_bucket')}")

    def escribir_datos(destino, medios=None):
        variables.append(f"datos:{(medios or {}).get('arn_del_bucket')}")

    def vaciar(destino, *, bucket, **resto):
        registro_de_vaciados.append(bucket)
        return len(registro_de_vaciados)

    herramental = lanzador.HerramentalDeRoots(
        corredor=corredor,
        inicializar=inicializar,
        escribir_variables_de_medios=escribir_medios,
        escribir_variables_de_aplicacion=escribir_aplicacion,
        vaciar_bucket=vaciar,
        escribir_variables_de_datos=escribir_datos,
    )
    return herramental, inicializados, variables, registro_de_vaciados


def salida_de_outputs(bucket=BUCKET, arn=ARN):
    import json

    return json.dumps(
        {"nombre_del_bucket": {"value": bucket}, "arn_del_bucket": {"value": arn}}
    )


#: Contrato que publica el root de datos en el laboratorio.
CONTRATO_DE_DATOS = {
    "id_de_vpc": "vpc-lab",
    "ids_de_subredes": ["subnet-a", "subnet-b"],
    "id_sg_lambda": "sg-lambda",
    "id_sg_admin": "sg-admin",
    "id_sg_rds": "sg-rds",
    "id_endpoint_s3": "vpce-s3",
    "identificador_rds": "blog-lab-postgres",
    "nombre_del_parametro_master": "/blog-lab/datos/blogadmin",
}


def salida_de_datos(**cambios):
    import json

    valores = {**CONTRATO_DE_DATOS, **cambios}
    return json.dumps({clave: {"value": valor} for clave, valor in valores.items() if valor is not None})


def salidas_base(extra=None):
    """Salidas de medios y datos sanos; el root de datos no propone cambios."""
    import json

    return {
        ("terraform-medios", "output"): salida_de_outputs(),
        ("terraform-datos", "output"): salida_de_datos(),
        ("terraform-datos", "show"): json.dumps({"resource_changes": []}),
        **(extra or {}),
    }


class OrdenCanonicoDeLosRootsTests(unittest.TestCase):
    """Una sola autoridad sobre el orden y la cobertura."""

    def test_al_crear_medios_va_primero_y_datos_antes_que_aplicacion(self):
        secuencia = lanzador.secuencia_de_roots("crear")
        self.assertEqual(
            [root.nombre for root in secuencia], ["medios", "datos", "aplicacion"]
        )

    def test_al_destruir_el_orden_es_exactamente_el_inverso(self):
        creacion = lanzador.secuencia_de_roots("crear")
        destruccion = lanzador.secuencia_de_roots("destruir")
        self.assertEqual(list(destruccion), list(reversed(creacion)))

    def test_todas_las_operaciones_de_infraestructura_cubren_los_tres_roots(self):
        for operacion in COMANDOS_DE_INFRAESTRUCTURA:
            with self.subTest(operacion=operacion):
                nombres = {root.nombre for root in lanzador.secuencia_de_roots(operacion)}
                self.assertEqual(nombres, {"medios", "datos", "aplicacion"})

    def test_validar_no_se_limita_al_root_de_aplicacion(self):
        nombres = [root.nombre for root in lanzador.secuencia_de_roots("validar")]
        self.assertIn("medios", nombres)

    def test_una_operacion_desconocida_aborta(self):
        """Un comando nuevo no puede heredar un orden por omision en silencio."""
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.secuencia_de_roots("inventar")

    def test_los_roots_no_comparten_subdirectorio_de_estado(self):
        nombres = {root.nombre for root in lanzador.ROOTS_EN_ORDEN_DE_CREACION}
        self.assertEqual(len(nombres), len(lanzador.ROOTS_EN_ORDEN_DE_CREACION))

    def test_los_roots_no_comparten_directorio_de_terraform(self):
        directorios = {root.directorio for root in lanzador.ROOTS_EN_ORDEN_DE_CREACION}
        self.assertEqual(len(directorios), 3)


class InventarioConscienteDeLosRootsTests(unittest.TestCase):
    """El bucket de medios es legitimo mientras su root no haya sido destruido."""

    def inventario(self, *, buckets=(), lambdas=(), **datos):
        base = {
            "s3": list(buckets),
            "lambda": list(lambdas),
            "apigatewayv2": [],
            "logs": [],
            "ssm": [],
            "ec2_vpc": [],
            "ec2_grupos": [],
            "rds_instancias": [],
            "rds_subredes": [],
            "rds_parametros": [],
            "logs_rds": [],
            "ssm_datos": [],
        }
        base.update({clave: list(valor) for clave, valor in datos.items()})
        return base

    def test_la_red_y_la_base_vivas_no_son_residuo_mientras_datos_viva(self):
        lanzador.exigir_ausencia_en_el_destino(
            self.inventario(buckets=[BUCKET], **lanzador.recursos_del_root_de_datos()),
            bucket_de_medios_vivo=BUCKET,
            datos_vivos=True,
        )

    def test_otra_instancia_rds_sigue_siendo_residuo_aunque_datos_viva(self):
        with self.assertRaises(Exception):
            lanzador.exigir_ausencia_en_el_destino(
                self.inventario(rds_instancias=["blog-lab-postgres", "blog-lab-restore-1"]),
                bucket_de_medios_vivo=None,
                datos_vivos=True,
            )

    def test_destruido_datos_su_vpc_si_es_residuo(self):
        with self.assertRaises(Exception):
            lanzador.exigir_ausencia_en_el_destino(
                self.inventario(ec2_vpc=["blog-lab-vpc"]),
                bucket_de_medios_vivo=BUCKET,
                datos_vivos=False,
            )

    def test_el_parametro_master_no_se_confunde_con_los_de_aplicacion(self):
        """Cada categoria tiene un solo root duenno, tambien en SSM."""
        legitimos = lanzador.recursos_del_root_de_datos()
        self.assertEqual(legitimos["ssm_datos"], [f"/blog-lab/datos/{r}" for r in ("blogadmin", "blog_migrate", "blog_app")])
        self.assertEqual(legitimos["logs_rds"], ["/aws/rds/instance/blog-lab-postgres/postgresql"])

    def test_el_bucket_de_medios_vivo_no_es_residuo(self):
        lanzador.exigir_ausencia_en_el_destino(
            self.inventario(buckets=[BUCKET]), bucket_de_medios_vivo=BUCKET
        )

    def test_otro_bucket_sigue_siendo_residuo_aunque_medios_viva(self):
        with self.assertRaises(Exception):
            lanzador.exigir_ausencia_en_el_destino(
                self.inventario(buckets=[BUCKET, "blog-lab-intruso"]),
                bucket_de_medios_vivo=BUCKET,
            )

    def test_una_lambda_sigue_siendo_residuo_aunque_medios_viva(self):
        with self.assertRaises(Exception):
            lanzador.exigir_ausencia_en_el_destino(
                self.inventario(buckets=[BUCKET], lambdas=["blog-lab-backend"]),
                bucket_de_medios_vivo=BUCKET,
            )

    def test_destruidos_los_dos_roots_el_bucket_si_es_residuo(self):
        with self.assertRaises(Exception):
            lanzador.exigir_ausencia_en_el_destino(
                self.inventario(buckets=[BUCKET]), bucket_de_medios_vivo=None
            )

    def test_inventario_limpio_pasa(self):
        lanzador.exigir_ausencia_en_el_destino(self.inventario(), bucket_de_medios_vivo=None)


class ContratoEntreRootsTests(unittest.TestCase):
    """El root de aplicacion recibe nombre y ARN por variables explicitas."""

    def test_aplicar_medios_usa_solo_su_root_y_devuelve_el_contrato(self):
        corredor = CorredorDeMentira(salidas={("terraform-medios", "output"): salida_de_outputs()})
        herramental, inicializados, variables, _ = herramental_de_mentira(corredor)
        contrato = lanzador.contrato_del_root_de_medios(
            Path("terraform.exe"), object(), aplicar=True, herramental=herramental
        )
        self.assertEqual(contrato["nombre_del_bucket"], BUCKET)
        self.assertEqual(contrato["arn_del_bucket"], ARN)
        self.assertEqual(inicializados, ["medios"])
        self.assertEqual({root for root, _ in corredor.invocaciones}, {"terraform-medios"})
        self.assertIn("apply", [op for _, op in corredor.invocaciones])

    def test_el_camino_de_lectura_no_aplica_nada(self):
        corredor = CorredorDeMentira(salidas={("terraform-medios", "output"): salida_de_outputs()})
        herramental, _, _, _ = herramental_de_mentira(corredor)
        lanzador.contrato_del_root_de_medios(
            Path("terraform.exe"), object(), aplicar=False, herramental=herramental
        )
        operaciones = [op for _, op in corredor.invocaciones]
        self.assertNotIn("apply", operaciones)
        self.assertNotIn("destroy", operaciones)

    def test_un_contrato_incompleto_aborta_antes_de_tocar_aplicacion(self):
        import json

        corredor = CorredorDeMentira(
            salidas={
                ("terraform-medios", "output"): json.dumps(
                    {"nombre_del_bucket": {"value": BUCKET}}
                )
            }
        )
        herramental, _, variables, _ = herramental_de_mentira(corredor)
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.contrato_del_root_de_medios(
                Path("terraform.exe"), object(), aplicar=True, herramental=herramental
            )
        self.assertNotIn("aplicacion", [v.split(":")[0] for v in variables])

    def test_un_fallo_en_medios_impide_continuar_a_aplicacion(self):
        corredor = CorredorDeMentira(fallar_en=[("terraform-medios", "apply")])
        herramental, _, variables, _ = herramental_de_mentira(corredor)
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.contrato_del_root_de_medios(
                Path("terraform.exe"), object(), aplicar=True, herramental=herramental
            )
        self.assertEqual({root for root, _ in corredor.invocaciones}, {"terraform-medios"})


class TeardownDeLosRootsTests(unittest.TestCase):
    """Orden inverso, vaciado previo y ownership preservado ante un fallo."""

    def test_el_destroy_va_aplicacion_datos_y_despues_medios(self):
        corredor = CorredorDeMentira()
        herramental, _, _, vaciados = herramental_de_mentira(corredor)
        lanzador.destruir_los_roots(
            Path("terraform.exe"),
            object(),
            contrato={"nombre_del_bucket": BUCKET, "arn_del_bucket": ARN},
            herramental=herramental,
        )
        self.assertEqual(
            corredor.roots("destroy"), ["terraform", "terraform-datos", "terraform-medios"]
        )

    def test_el_bucket_se_vacia_antes_de_destruir_su_root(self):
        corredor = CorredorDeMentira()
        herramental, _, _, vaciados = herramental_de_mentira(corredor)
        lanzador.destruir_los_roots(
            Path("terraform.exe"),
            object(),
            contrato={"nombre_del_bucket": BUCKET, "arn_del_bucket": ARN},
            herramental=herramental,
        )
        self.assertEqual(vaciados, [BUCKET])

    def test_un_fallo_en_aplicacion_no_destruye_datos_ni_medios(self):
        """Ownership preservado: los states siguientes no se tocan si uno falla."""
        corredor = CorredorDeMentira(fallar_en=[("terraform", "destroy")])
        herramental, _, _, _ = herramental_de_mentira(corredor)
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.destruir_los_roots(
                Path("terraform.exe"),
                object(),
                contrato={"nombre_del_bucket": BUCKET, "arn_del_bucket": ARN},
                herramental=herramental,
            )
        self.assertNotIn("terraform-datos", corredor.roots("destroy"))
        self.assertNotIn("terraform-medios", corredor.roots("destroy"))

    def test_un_fallo_en_datos_no_destruye_medios(self):
        corredor = CorredorDeMentira(fallar_en=[("terraform-datos", "destroy")])
        herramental, _, _, vaciados = herramental_de_mentira(corredor)
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.destruir_los_roots(
                Path("terraform.exe"),
                object(),
                contrato={"nombre_del_bucket": BUCKET, "arn_del_bucket": ARN},
                herramental=herramental,
            )
        self.assertNotIn("terraform-medios", corredor.roots("destroy"))
        self.assertEqual(vaciados, [])


class SemanticaDeOperacionesTests(unittest.TestCase):
    def test_rollback_lee_medios_y_datos_sanos_sin_aplicarlos(self):
        corredor = CorredorDeMentira(salidas=salidas_base())
        herramental, inicializados, variables, _ = herramental_de_mentira(corredor)
        contrato = lanzador.preparar_los_roots_para(
            'rollback', Path('terraform.exe'), object(), Path('anterior.zip'),
            herramental=herramental,
        )
        self.assertEqual(inicializados, ['medios', 'datos', 'aplicacion'])
        self.assertEqual(variables, ['medios', f'datos:{ARN}', f'aplicacion:{BUCKET}'])
        self.assertNotIn('apply', [op for _, op in corredor.invocaciones])
        self.assertIn(('terraform-medios', 'validate'), corredor.invocaciones)
        self.assertIn(('terraform-datos', 'validate'), corredor.invocaciones)
        self.assertEqual(contrato['datos']['identificador_rds'], 'blog-lab-postgres')

    def test_contrato_nombre_arn_incoherente_aborta(self):
        corredor = CorredorDeMentira(salidas={('terraform-medios', 'output'): salida_de_outputs(arn='arn:aws:s3:::otro')})
        herramental, _, _, _ = herramental_de_mentira(corredor)
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.contrato_del_root_de_medios(
                Path('terraform.exe'), object(), aplicar=False, herramental=herramental,
            )

    def test_fallo_de_aplicacion_no_vacia_el_bucket(self):
        corredor = CorredorDeMentira(fallar_en=[('terraform', 'destroy')])
        herramental, _, _, vaciados = herramental_de_mentira(corredor)
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.destruir_los_roots(
                Path('terraform.exe'), object(), contrato={'nombre_del_bucket': BUCKET},
                herramental=herramental,
            )
        self.assertEqual(vaciados, [])

    def test_recuperar_medios_noop_no_aplica_ni_pide_confirmacion(self):
        import json
        corredor = CorredorDeMentira(salidas=salidas_base({
            ('terraform-medios', 'show'): json.dumps({'resource_changes': []}),
        }))
        herramental, inicializados, _, _ = herramental_de_mentira(corredor)
        with patch.object(lanzador, 'exigir_confirmacion_del_plan') as confirmar:
            lanzador.preparar_los_roots_para(
                'recuperar', Path('terraform.exe'), object(), Path('actual.zip'),
                herramental=herramental,
            )
        self.assertEqual(inicializados, ['medios', 'datos', 'aplicacion'])
        self.assertNotIn('apply', [op for _, op in corredor.invocaciones])
        confirmar.assert_not_called()

    def test_recuperar_rechaza_reemplazo_de_medios_antes_de_apply(self):
        import json
        corredor = CorredorDeMentira(salidas={('terraform-medios', 'show'): json.dumps({
            'resource_changes': [{'address': 'module.almacenamiento.aws_s3_bucket.medios',
                                  'type': 'aws_s3_bucket', 'change': {'actions': ['delete', 'create']}}],
        })})
        herramental, _, variables, _ = herramental_de_mentira(corredor)
        with self.assertRaises(lanzador.mod_inventario.ErrorDeInventario):
            lanzador.preparar_los_roots_para(
                'recuperar', Path('terraform.exe'), object(), Path('actual.zip'),
                herramental=herramental,
            )
        self.assertNotIn('apply', [op for _, op in corredor.invocaciones])
        self.assertEqual(variables, ['medios'])

    def test_recuperar_sin_confirmacion_no_aplica_medios_ni_inicializa_aplicacion(self):
        corredor = CorredorDeMentira()
        herramental, inicializados, _, _ = herramental_de_mentira(corredor)
        with patch.object(lanzador, 'sha256_de_archivo', return_value='a' * 64), patch.object(
            lanzador, 'exigir_confirmacion_del_plan', side_effect=lanzador.ErrorDelLaboratorio('rechazado')
        ), self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.preparar_los_roots_para(
                'recuperar', Path('terraform.exe'), object(), Path('actual.zip'),
                herramental=herramental,
            )
        self.assertEqual(inicializados, ['medios'])
        self.assertNotIn('apply', [op for _, op in corredor.invocaciones])


class VersionDesdeRunbookTests(unittest.TestCase):
    """Entradas CLI reales con Terraform/servicios sustituidos, no incidentes vivos."""

    def ejecutar(self, operacion, acciones_medios=('no-op',), rechazar=False):
        import json
        self.eventos = []
        self.corredor = CorredorDeMentira(salidas={
            ('terraform-medios', 'output'): salida_de_outputs(),
            ('terraform-datos', 'output'): salida_de_datos(),
            ('terraform-datos', 'show'): json.dumps({'resource_changes': []}),
            ('terraform-datos', 'state'): 'module.red.aws_vpc.this\nmodule.base_de_datos.aws_db_instance.this\n',
            ('terraform', 'output'): json.dumps({'bucket_de_medios': {'value': BUCKET}}),
            ('terraform-medios', 'show'): json.dumps({'resource_changes': [{
                'address': 'module.almacenamiento.aws_s3_bucket.medios', 'type': 'aws_s3_bucket',
                'change': {'actions': list(acciones_medios)},
            }]}),
            ('terraform-medios', 'state'): 'module.almacenamiento.aws_s3_bucket.medios\n',
            ('terraform', 'state'): 'module.computo.aws_lambda_function.backend\n',
        })
        herramental, self.inicializados, self.variables, _ = herramental_de_mentira(self.corredor)
        contexto = ({}, SimpleNamespace(modo='local'), Path('terraform.exe'),
                    SimpleNamespace(ruta=Path('anterior.zip'), sha256='b' * 64), object(), 'runtime-id')
        def confirmar(sha, *, operacion):
            self.eventos.append(('confirmar', operacion))
            if rechazar:
                raise lanzador.ErrorDelLaboratorio('rechazado')
        def revisar(*args, acciones, **kwargs):
            self.eventos.append(('acciones', acciones))
        with ExitStack() as stack:
            for nombre, valor in {
                'preparar_contexto_de_runbook': lambda *a, **k: contexto,
                'raiz_de_estado': lambda *a: Path('estado-falso'),
                'herramental_real': lambda: herramental,
                'terraform': self.corredor,
                'revisar_plan_guardado': revisar,
                'exigir_actualizacion_de_lambda': lambda: self.eventos.append(('lambda', 'update obligatorio')),
                'sha256_de_archivo': lambda *a: 'a' * 64,
                'exigir_confirmacion_del_plan': confirmar,
                'ejercitar_servicios': lambda *a, **k: {'camino_critico': {'estado': 200}},
                'inspeccionar_con_sdk': lambda *a, **k: {'sdk': 'boto3'},
            }.items():
                stack.enter_context(patch.object(lanzador, nombre, valor))
            stack.enter_context(patch.object(lanzador.mod_destino, 'lock_de_escritura', return_value=nullcontext()))
            stack.enter_context(patch.object(lanzador.mod_artefacto, 'confirmar_sin_cambios'))
            return getattr(lanzador, 'comando_' + operacion)(SimpleNamespace())

    def test_rollback_solo_aplica_lambda_con_medios_leidos_e_inyectados(self):
        self.assertEqual(self.ejecutar('rollback'), 0)
        self.assertEqual(self.inicializados, ['medios', 'datos', 'aplicacion'])
        self.assertEqual(self.variables[-1], f'aplicacion:{BUCKET}')
        self.assertEqual(self.corredor.roots('apply'), ['terraform'])
        self.assertIn(('acciones', ('update',)), self.eventos)
        self.assertIn(('lambda', 'update obligatorio'), self.eventos)

    def test_rollback_rechazado_no_aplica_ningun_root(self):
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            self.ejecutar('rollback', rechazar=True)
        self.assertEqual(self.corredor.roots('apply'), [])

    def test_recuperar_sin_medios_los_crea_antes_de_aplicacion(self):
        self.assertEqual(self.ejecutar('recuperar', ('create',)), 0)
        self.assertEqual(self.corredor.roots('apply'), ['terraform-medios', 'terraform'])
        self.assertEqual(self.inicializados, ['medios', 'datos', 'aplicacion'])
        self.assertEqual([v for k, v in self.eventos if k == 'confirmar'], ['aplicar medios', 'recuperar'])
        self.assertIn(('acciones', ('create', 'update')), self.eventos)

    def test_recuperar_con_medios_sanos_solo_aplica_aplicacion(self):
        self.assertEqual(self.ejecutar('recuperar'), 0)
        self.assertEqual(self.corredor.roots('apply'), ['terraform'])
        self.assertEqual(self.variables[-1], f'aplicacion:{BUCKET}')


class PlanDeRollbackTests(unittest.TestCase):
    """La guarda real lee el plan guardado; invocarla no basta para probarla."""

    def comprobar(self, tipo, acciones):
        import json
        with tempfile.TemporaryDirectory() as directorio:
            plan = Path(directorio) / 'plan.json'
            plan.write_text(json.dumps({'resource_changes': [{
                'address': 'module.computo.aws_lambda_function.backend',
                'type': tipo, 'change': {'actions': acciones},
            }]}), encoding='utf-8')
            with patch.object(lanzador, 'PLAN_EN_JSON', plan):
                lanzador.exigir_actualizacion_de_lambda()

    def test_update_de_lambda_demuestra_el_rollback(self):
        self.comprobar('aws_lambda_function', ['update'])

    def test_lambda_sin_cambio_no_demuestra_rollback(self):
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            self.comprobar('aws_lambda_function', ['no-op'])

    def test_actualizar_otro_recurso_no_demuestra_rollback(self):
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            self.comprobar('aws_iam_role_policy', ['update'])


class DestruirDesdeRunbookTests(unittest.TestCase):
    def ejecutar(self, rechazar=None, outputs=None):
        self.eventos = []
        destino = SimpleNamespace(modo='local')
        contexto = ({}, destino, Path('terraform.exe'), SimpleNamespace(ruta=Path('actual.zip')), None, None)
        def terraform(binario, destino, args, *, raiz, **kwargs):
            self.eventos.append((Path(raiz).name, args[0]))
        def confirmar(sha, *, operacion):
            self.eventos.append(('confirmar', operacion))
            if rechazar and rechazar in operacion:
                raise lanzador.ErrorDelLaboratorio('rechazado')
        def vaciar(*args, **kwargs):
            self.eventos.append(('vaciar', kwargs['bucket']))
            return 1
        with ExitStack() as stack:
            sustitutos = {
                'preparar_contexto_de_runbook': lambda *a, **k: contexto,
                'raiz_de_estado': lambda *a: Path('estado-falso'),
                'preparar_los_roots_para': lambda *a, **k: {'nombre_del_bucket': BUCKET, 'arn_del_bucket': ARN},
                'terraform': terraform,
                'revisar_plan_guardado': lambda *a, root, **k: self.eventos.append(('revisar', root.nombre)),
                'sha256_de_archivo': lambda *a: 'a' * 64,
                'exigir_confirmacion_del_plan': confirmar,
                'estado_del_root': lambda *a, **k: [],
                'salidas': lambda *a, **k: outputs or {},
                'inventario_del_destino': lambda *a: {'s3': [BUCKET] if ('terraform-medios', 'apply') not in self.eventos else []},
                'exigir_ownership_disjunto': lambda *a, **k: None,
            }
            for nombre, valor in sustitutos.items():
                stack.enter_context(patch.object(lanzador, nombre, valor))
            stack.enter_context(patch.object(lanzador.mod_destino, 'lock_de_escritura', return_value=nullcontext()))
            stack.enter_context(patch.object(lanzador.mod_verificacion, 'vaciar_bucket', vaciar))
            return lanzador.comando_destruir(SimpleNamespace())

    def test_destruye_aplicacion_y_datos_antes_de_vaciar_y_planificar_medios(self):
        self.assertEqual(self.ejecutar(), 0)
        self.assertLess(self.eventos.index(('terraform', 'apply')), self.eventos.index(('terraform-datos', 'plan')))
        self.assertLess(self.eventos.index(('terraform-datos', 'apply')), self.eventos.index(('vaciar', BUCKET)))
        self.assertLess(self.eventos.index(('terraform', 'apply')), self.eventos.index(('vaciar', BUCKET)))
        self.assertLess(self.eventos.index(('vaciar', BUCKET)), self.eventos.index(('terraform-medios', 'plan')))
        self.assertLess(self.eventos.index(('revisar', 'medios')), self.eventos.index(('terraform-medios', 'apply')))

    def test_rechazar_aplicacion_no_vacia_ni_aplica(self):
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            self.ejecutar(rechazar='aplicacion')
        self.assertFalse(any(e[0] == 'vaciar' or e[1] == 'apply' for e in self.eventos))

    def test_rechazar_medios_conserva_su_state(self):
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            self.ejecutar(rechazar='medios')
        self.assertIn(('terraform', 'apply'), self.eventos)
        self.assertIn(('terraform-datos', 'apply'), self.eventos)
        self.assertNotIn(('terraform-medios', 'apply'), self.eventos)

    def test_rechazar_datos_conserva_datos_y_medios(self):
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            self.ejecutar(rechazar='datos')
        self.assertIn(('terraform', 'apply'), self.eventos)
        self.assertNotIn(('terraform-datos', 'apply'), self.eventos)
        self.assertFalse(any(e[0] == 'vaciar' for e in self.eventos))

    def test_outputs_residuales_impiden_declarar_teardown(self):
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            self.ejecutar(outputs={'residuo': 'valor'})


class OwnershipDisjuntoTests(unittest.TestCase):
    """Ningun recurso puede quedar administrado por dos states."""

    MEDIOS = [
        "module.almacenamiento.aws_s3_bucket.medios",
        "module.almacenamiento.aws_s3_bucket_versioning.medios",
    ]
    DATOS = [
        "module.red.aws_vpc.this",
        'module.red.aws_subnet.privada["a"]',
        "module.red.aws_security_group.rds",
        "module.base_de_datos.aws_db_instance.this",
        "module.base_de_datos.aws_ssm_parameter.contrasena_master",
    ]
    APLICACION = [
        "module.computo.aws_lambda_function.backend",
        "module.identidad.aws_iam_role.ejecucion",
        'module.parametros.aws_ssm_parameter.configuracion["local/storage_region"]',
    ]

    def estados(self, **cambios):
        return {"medios": self.MEDIOS, "datos": self.DATOS, "aplicacion": self.APLICACION, **cambios}

    def test_states_disjuntos_pasan(self):
        lanzador.exigir_ownership_disjunto(self.estados())

    def test_un_recurso_en_dos_states_aborta(self):
        compartido = "module.almacenamiento.aws_s3_bucket.medios"
        with self.assertRaises(lanzador.ErrorDelLaboratorio) as capturado:
            lanzador.exigir_ownership_disjunto(
                self.estados(aplicacion=self.APLICACION + [compartido])
            )
        self.assertIn(compartido, str(capturado.exception))

    def test_el_root_de_aplicacion_no_puede_administrar_s3(self):
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.exigir_ownership_disjunto(
                self.estados(aplicacion=self.APLICACION + ["module.otro.aws_s3_bucket_policy.copia"])
            )

    def test_ni_aplicacion_ni_medios_pueden_administrar_red_o_rds(self):
        for root, intruso in (
            ("aplicacion", "module.computo.aws_security_group.propio"),
            ("aplicacion", "module.otro.aws_db_instance.copia"),
            ("medios", "module.otro.aws_vpc.copia"),
        ):
            with self.subTest(root=root, intruso=intruso):
                base = self.estados()
                base[root] = base[root] + [intruso]
                with self.assertRaises(lanzador.ErrorDelLaboratorio):
                    lanzador.exigir_ownership_disjunto(base)

    def test_un_ssm_propio_en_cada_root_no_es_intrusion(self):
        """El master de datos y la configuracion de aplicacion son parametros DISTINTOS."""
        lanzador.exigir_ownership_disjunto(self.estados())

    def test_el_root_de_medios_debe_administrar_el_bucket(self):
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.exigir_ownership_disjunto(self.estados(medios=[]))

    def test_el_root_de_datos_debe_administrar_vpc_y_rds(self):
        for sin in ("module.red.aws_vpc.this", "module.base_de_datos.aws_db_instance.this"):
            with self.subTest(falta=sin):
                with self.assertRaises(lanzador.ErrorDelLaboratorio):
                    lanzador.exigir_ownership_disjunto(
                        self.estados(datos=[d for d in self.DATOS if d != sin])
                    )

    def test_sin_exigir_duennos_los_states_vacios_se_admiten(self):
        """Tras el teardown los tres states quedan vacios y eso es correcto."""
        lanzador.exigir_ownership_disjunto(
            {"medios": [], "datos": [], "aplicacion": []}, exigir_duennos=False
        )

    def test_el_tipo_se_extrae_de_la_direccion(self):
        self.assertEqual(lanzador.tipo_de_direccion('module.red.aws_subnet.privada["a"]'), "aws_subnet")
        self.assertEqual(lanzador.tipo_de_direccion("aws_vpc.raiz"), "aws_vpc")


class ContratoDelRootDeDatosTests(unittest.TestCase):
    """El root de datos recibe el ARN de medios y publica un contrato completo (DH-1)."""

    def test_aplica_solo_su_root_y_devuelve_el_contrato(self):
        corredor = CorredorDeMentira(salidas={("terraform-datos", "output"): salida_de_datos()})
        herramental, inicializados, variables, _ = herramental_de_mentira(corredor)
        contrato = lanzador.contrato_del_root_de_datos(
            Path("terraform.exe"), object(),
            contrato_de_medios={"arn_del_bucket": ARN}, aplicar=True, herramental=herramental,
        )
        self.assertEqual(contrato["identificador_rds"], "blog-lab-postgres")
        self.assertEqual(inicializados, ["datos"])
        self.assertEqual(variables, [f"datos:{ARN}"])
        self.assertEqual({root for root, _ in corredor.invocaciones}, {"terraform-datos"})
        self.assertIn("apply", [op for _, op in corredor.invocaciones])

    def test_el_camino_de_lectura_no_aplica_nada(self):
        corredor = CorredorDeMentira(salidas={("terraform-datos", "output"): salida_de_datos()})
        herramental, _, _, _ = herramental_de_mentira(corredor)
        lanzador.contrato_del_root_de_datos(
            Path("terraform.exe"), object(),
            contrato_de_medios={"arn_del_bucket": ARN}, aplicar=False, herramental=herramental,
        )
        self.assertNotIn("apply", [op for _, op in corredor.invocaciones])

    def test_un_contrato_incompleto_aborta(self):
        corredor = CorredorDeMentira(
            salidas={("terraform-datos", "output"): salida_de_datos(id_sg_admin=None)}
        )
        herramental, _, _, _ = herramental_de_mentira(corredor)
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.contrato_del_root_de_datos(
                Path("terraform.exe"), object(),
                contrato_de_medios={"arn_del_bucket": ARN}, aplicar=False, herramental=herramental,
            )

    def test_la_contrasena_en_el_plan_aborta_antes_de_aplicar(self):
        """DH-2: si el canario aparece en el plan, no se aplica nada."""
        import json

        plan = json.dumps({"resource_changes": [], "fuga": lanzador.CONTRASENA_DEL_LABORATORIO})
        corredor = CorredorDeMentira(salidas={
            ("terraform-datos", "show"): plan,
            ("terraform-datos", "output"): salida_de_datos(),
        })
        herramental, _, _, _ = herramental_de_mentira(corredor)
        with self.assertRaises(lanzador.ErrorDelLaboratorio) as capturado:
            lanzador.contrato_del_root_de_datos(
                Path("terraform.exe"), object(),
                contrato_de_medios={"arn_del_bucket": ARN}, aplicar=True, herramental=herramental,
            )
        self.assertNotIn("apply", [op for _, op in corredor.invocaciones])
        self.assertNotIn(lanzador.CONTRASENA_DEL_LABORATORIO, str(capturado.exception))

    def test_la_contrasena_en_las_salidas_aborta(self):
        corredor = CorredorDeMentira(salidas={
            ("terraform-datos", "output"): salida_de_datos(
                nombre_del_parametro_master=lanzador.CONTRASENA_DEL_LABORATORIO
            ),
        })
        herramental, _, _, _ = herramental_de_mentira(corredor)
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.contrato_del_root_de_datos(
                Path("terraform.exe"), object(),
                contrato_de_medios={"arn_del_bucket": ARN}, aplicar=False, herramental=herramental,
            )

    def test_sin_canario_no_hay_comprobacion(self):
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.exigir_secreto_ausente({"plan": "{}"}, "")

    def test_un_fallo_en_datos_impide_continuar_a_aplicacion(self):
        corredor = CorredorDeMentira(
            salidas=salidas_base(), fallar_en=[("terraform-datos", "validate")]
        )
        herramental, inicializados, _, _ = herramental_de_mentira(corredor)
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            lanzador.preparar_los_roots_para(
                "rollback", Path("terraform.exe"), object(), Path("anterior.zip"),
                herramental=herramental,
            )
        self.assertNotIn("aplicacion", inicializados)


class VariablesDeCadaRootTests(unittest.TestCase):
    """Cada root recibe SOLO los endpoints que declara (Task/031 anade EC2 y RDS)."""

    def destino(self):
        endpoints = {servicio: "http://127.0.0.1:4566" for servicio in lanzador.mod_destino.SERVICIOS}
        return SimpleNamespace(endpoints=endpoints, region="us-east-1")

    def test_aplicacion_no_recibe_ec2_ni_rds(self):
        import json

        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "destino.tfvars.json"
            with patch.object(lanzador, "DIRECTORIO_GENERADO", Path(directorio)), patch.object(
                lanzador, "VARIABLES_GENERADAS", ruta
            ):
                lanzador.escribir_variables_del_destino(
                    self.destino(), Path("a.zip"), {"nombre_del_bucket": BUCKET, "arn_del_bucket": ARN}
                )
            endpoints = json.loads(ruta.read_text(encoding="utf-8"))["endpoints_aws"]
        self.assertEqual(set(endpoints), set(lanzador.ENDPOINTS_DEL_ROOT_DE_APLICACION))
        self.assertNotIn("ec2", endpoints)
        self.assertNotIn("rds", endpoints)

    def test_datos_recibe_sus_endpoints_el_arn_y_la_contrasena_ficticia(self):
        import json

        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "destino.tfvars.json"
            with patch.object(lanzador, "DIRECTORIO_GENERADO_DE_DATOS", Path(directorio)), patch.object(
                lanzador, "VARIABLES_GENERADAS_DE_DATOS", ruta
            ):
                with patch.object(lanzador, "preparar_ejecutor_h0316", return_value="a" * 64):
                    lanzador.escribir_variables_de_datos(self.destino(), {"arn_del_bucket": ARN})
                efimeras = json.loads(
                    lanzador.ruta_de_las_efimeras_de_datos().read_text(encoding="utf-8")
                )
            valores = json.loads(ruta.read_text(encoding="utf-8"))
        self.assertEqual(set(valores["endpoints_aws"]), set(lanzador.ENDPOINTS_DEL_ROOT_DE_DATOS))
        self.assertEqual(valores["arn_del_bucket_de_medios"], ARN)
        # La efimera NO va con las demas: al aplicar un plan guardado solo ella se repite.
        self.assertNotIn("contrasena_master", valores)
        self.assertEqual(efimeras, lanzador.EFIMERAS_DEL_LABORATORIO)

    def test_solo_el_root_de_datos_tiene_variables_efimeras(self):
        self.assertEqual(lanzador.variables_efimeras(lanzador.ROOT_DE_MEDIOS), [])
        self.assertEqual(lanzador.variables_efimeras(lanzador.ROOT_DE_APLICACION), [])
        (argumento,) = lanzador.variables_efimeras(lanzador.ROOT_DE_DATOS)
        self.assertTrue(argumento.startswith("-var-file=") and argumento.endswith("efimeras.tfvars.json"))

    def test_el_apply_del_plan_guardado_de_datos_aporta_las_efimeras(self):
        """Sin ellas Terraform rechaza el apply: hallazgo real del laboratorio (H-031-1)."""
        aplicados = []

        def corredor(binario, destino, argumentos, *, raiz=None, **resto):
            if argumentos[0] == "apply":
                aplicados.append(list(argumentos))
            if argumentos[:2] == ["output", "-json"]:
                return subprocess.CompletedProcess([], 0, salida_de_datos(), "")
            if argumentos[0] == "show":
                import json
                return subprocess.CompletedProcess([], 0, json.dumps({"resource_changes": [{
                    "address": "module.red.aws_vpc.this", "type": "aws_vpc",
                    "change": {"actions": ["create"]},
                }]}), "")
            return subprocess.CompletedProcess([], 0, "", "")

        herramental, _, _, _ = herramental_de_mentira(corredor)
        lanzador.contrato_del_root_de_datos(
            Path("terraform.exe"), object(),
            contrato_de_medios={"arn_del_bucket": ARN}, aplicar=True, herramental=herramental,
        )
        (apply,) = aplicados
        self.assertIn(lanzador.variables_efimeras(lanzador.ROOT_DE_DATOS)[0], apply)
        self.assertEqual(apply[-1], str(lanzador.ROOT_DE_DATOS.plan_guardado))

    def test_datos_sin_arn_de_medios_aborta(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "destino.tfvars.json"
            with patch.object(lanzador, "DIRECTORIO_GENERADO_DE_DATOS", Path(directorio)), patch.object(
                lanzador, "VARIABLES_GENERADAS_DE_DATOS", ruta
            ):
                with self.assertRaises(lanzador.ErrorDelLaboratorio):
                    lanzador.escribir_variables_de_datos(self.destino(), {"arn_del_bucket": None})

    def test_la_contrasena_ficticia_cumple_la_validacion_del_root(self):
        """Debe pasar la misma validacion que una real: 32-64 alfanumericos."""
        import re

        self.assertRegex(lanzador.CONTRASENA_DEL_LABORATORIO, re.compile(r"^[A-Za-z0-9]{32,64}$"))


class NingunComandoAsumeUnSoloRootTests(unittest.TestCase):
    """Comprobacion estatica: ningun comando puede heredar el root por omision."""

    #: Ayudantes cuyo root es un argumento por omision. Llamarlos sin decir el
    #: root desde un comando es exactamente el defecto de DEF-030-2.
    AYUDANTES_CON_ROOT_IMPLICITO = frozenset(
        {"inicializar", "salidas", "variables_comunes", "escribir_backend", "generar_lock"}
    )
    #: Nombres de la orquestacion multi-root. Todo comando de infraestructura
    #: debe apoyarse en al menos uno.
    ORQUESTACION = frozenset(
        {
            "secuencia_de_roots",
            "contrato_del_root_de_medios",
            "contrato_del_root_de_datos",
            "destruir_los_roots",
            "exigir_ausencia_en_el_destino",
            "ROOTS_EN_ORDEN_DE_CREACION",
        }
    )

    @classmethod
    def setUpClass(cls):
        cls.arbol = ast.parse(Path(lanzador.__file__).read_text(encoding="utf-8"))
        cls.funciones = {
            nodo.name: nodo
            for nodo in ast.walk(cls.arbol)
            if isinstance(nodo, ast.FunctionDef)
        }
        cls.cuerpos = {
            nombre: nodo
            for nombre, nodo in cls.funciones.items()
            if nombre.startswith("comando_")
        }

    def nombres_usados(self, nodo):
        return {
            hijo.id for hijo in ast.walk(nodo) if isinstance(hijo, ast.Name)
        } | {
            hijo.attr for hijo in ast.walk(nodo) if isinstance(hijo, ast.Attribute)
        }

    def nombres_alcanzables(self, nombre, vistos=None):
        """Nombres usados por la funcion y por todo lo que llama, transitivamente.

        Hace falta porque `crear`, `rollback` y `recuperar` delegan en un cuerpo
        compartido: delegar en un ayudante que SI conoce los dos roots cumple el
        requisito, y una comprobacion de un solo nivel lo marcaria como infractor.
        """
        vistos = vistos if vistos is not None else set()
        if nombre in vistos or nombre not in self.funciones:
            return set()
        vistos.add(nombre)
        nodo = self.funciones[nombre]
        alcanzables = self.nombres_usados(nodo)
        for llamado in set(alcanzables):
            alcanzables |= self.nombres_alcanzables(llamado, vistos)
        return alcanzables

    @staticmethod
    def declara_el_root(llamada):
        """¿La llamada dice sobre que root opera, por clave o por posicion?

        No basta con exigir la palabra clave: `escribir_backend(modo, root)` pasa
        el root **posicionalmente** y es correcto. Lo que se busca es que el root
        aparezca de algun modo en los argumentos.
        """
        for kw in llamada.keywords:
            if kw.arg in {"root", "raiz"}:
                return True
        for argumento in list(llamada.args) + [kw.value for kw in llamada.keywords]:
            for hijo in ast.walk(argumento):
                nombre = getattr(hijo, "id", None) or getattr(hijo, "attr", None)
                if nombre and "root" in nombre.lower():
                    return True
        return False

    def funciones_de_cada_comando(self):
        """Cada comando de infraestructura con el cierre de lo que alcanza."""
        for nombre in sorted(self.cuerpos):
            operacion = nombre.removeprefix("comando_").replace("_", "-")
            if operacion in COMANDOS_DE_INFRAESTRUCTURA:
                yield nombre

    def test_ningun_comando_llama_a_un_ayudante_sin_declarar_el_root(self):
        infractores = []
        for nombre in self.funciones_de_cada_comando():
            alcanzadas = {nombre} | (
                self.nombres_alcanzables(nombre) & set(self.funciones)
            )
            for funcion in sorted(alcanzadas):
                for llamada in ast.walk(self.funciones[funcion]):
                    if not isinstance(llamada, ast.Call):
                        continue
                    objetivo = getattr(llamada.func, "id", None)
                    if objetivo not in self.AYUDANTES_CON_ROOT_IMPLICITO:
                        continue
                    if not self.declara_el_root(llamada):
                        infractores.append(f"{nombre} -> {funcion} -> {objetivo}()")
        self.assertEqual(
            sorted(set(infractores)),
            [],
            f"caminos que asumen un solo root: {sorted(set(infractores))}",
        )

    def test_cada_comando_de_infraestructura_usa_la_orquestacion(self):
        sin_orquestacion = [
            nombre
            for nombre in self.funciones_de_cada_comando()
            if not (self.nombres_alcanzables(nombre) & self.ORQUESTACION)
        ]
        self.assertEqual(
            sin_orquestacion,
            [],
            f"comandos que no pasan por la topologia de roots: {sin_orquestacion}",
        )

    def test_los_comandos_de_infraestructura_existen_todos(self):
        esperados = {
            f"comando_{operacion.replace('-', '_')}" for operacion in COMANDOS_DE_INFRAESTRUCTURA
        }
        self.assertTrue(esperados <= set(self.cuerpos))


if __name__ == "__main__":
    unittest.main()
