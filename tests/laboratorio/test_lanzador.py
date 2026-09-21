"""Cableado del lanzador: como se compone el entorno que juzgan las guardas.

Por que este archivo existe
---------------------------
Las guardas de `destino.py` son correctas, pero solo sirven si **ven** lo que hay
en la maquina. Un control negativo del CLI revelo que no era asi: la
configuracion del laboratorio se superponia al entorno del host y sustituia una
credencial de aspecto real por la ficticia, de modo que la guarda de credenciales
nunca llegaba a dispararse.

No habia fuga —el proceso hijo se construye desde una *allowlist* y jamas recibia
la credencial del host—, pero la deteccion quedaba vacia: exactamente el tipo de
cobertura aparente que esta tarea tiene que evitar.

La regla correcta es la contraria: **el valor del host siempre gana y siempre se
juzga.** La configuracion del laboratorio aporta valores por omision, no
sobrescribe.
"""

from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from laboratorio import destino as guarda  # noqa: E402
from laboratorio import laboratorio as lanzador  # noqa: E402
from ejemplo_canonico_de_aws import (  # noqa: E402
    CLAVE_CON_FORMA_REAL,
    SECRETO_DEL_EJEMPLO,
)


def env_del_laboratorio():
    """Lo que aporta `.env.laboratorio`: fixtures ficticias y ajustes locales."""
    return {
        "LAB_COMPOSE_PROJECT_NAME": "personal-blog-lab",
        "LAB_PUERTO": "4566",
        "LAB_REGION": "us-east-1",
        "LAB_EMULADOR_DIGEST": "sha256:" + "0" * 64,
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test",
        "AWS_REGION": "us-east-1",
        "AWS_DEFAULT_REGION": "us-east-1",
        "AWS_EC2_METADATA_DISABLED": "true",
    }


class ComposicionDelEntornoTests(unittest.TestCase):
    def entorno(self, host):
        return lanzador.construir_entorno_para_guardas(
            env_del_laboratorio(), entorno_del_host=host
        )

    def test_sin_nada_en_el_host_se_usan_las_fixtures(self):
        resuelto = self.entorno({"PATH": "/usr/bin"})
        self.assertEqual(resuelto["AWS_ACCESS_KEY_ID"], "test")
        self.assertEqual(resuelto["AWS_REGION"], "us-east-1")

    def test_los_endpoints_se_derivan_del_puerto_publicado(self):
        resuelto = self.entorno({"PATH": "/usr/bin"})
        for servicio in guarda.SERVICIOS:
            with self.subTest(servicio=servicio):
                self.assertEqual(
                    resuelto[guarda.PREFIJO_DE_ENDPOINT + servicio.upper()],
                    "http://127.0.0.1:4566",
                )

    def test_una_credencial_real_del_host_NO_queda_enmascarada(self):
        """Es el defecto que encontro el control negativo del CLI."""
        resuelto = self.entorno(
            {"PATH": "/usr/bin", "AWS_ACCESS_KEY_ID": CLAVE_CON_FORMA_REAL}
        )
        self.assertEqual(resuelto["AWS_ACCESS_KEY_ID"], CLAVE_CON_FORMA_REAL)
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(resuelto, modo="local")

    def test_un_secreto_real_del_host_NO_queda_enmascarado(self):
        resuelto = self.entorno(
            {
                "PATH": "/usr/bin",
                "AWS_SECRET_ACCESS_KEY": SECRETO_DEL_EJEMPLO,
            }
        )
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(resuelto, modo="local")

    def test_una_region_distinta_en_el_host_NO_queda_enmascarada(self):
        resuelto = self.entorno({"PATH": "/usr/bin", "AWS_REGION": "eu-west-1"})
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(resuelto, modo="local")

    def test_la_metadata_habilitada_en_el_host_NO_queda_enmascarada(self):
        resuelto = self.entorno(
            {"PATH": "/usr/bin", "AWS_EC2_METADATA_DISABLED": "false"}
        )
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(resuelto, modo="local")

    def test_un_endpoint_externo_del_host_NO_queda_enmascarado(self):
        resuelto = self.entorno(
            {"PATH": "/usr/bin", "LAB_ENDPOINT_S3": "https://s3.amazonaws.com"}
        )
        with self.assertRaises(guarda.ErrorDeDestino):
            guarda.resolver_destino(resuelto, modo="local")

    def test_las_variables_prohibidas_del_host_llegan_a_la_guarda(self):
        for nombre in ("AWS_PROFILE", "AWS_SESSION_TOKEN", "HTTPS_PROXY"):
            with self.subTest(nombre=nombre):
                resuelto = self.entorno({"PATH": "/usr/bin", nombre: "x"})
                self.assertIn(nombre, resuelto)
                with self.assertRaises(guarda.ErrorDeDestino):
                    guarda.resolver_destino(resuelto, modo="local")


class ResiduosTests(unittest.TestCase):
    """Que se considera residuo del laboratorio.

    Hallazgo real: tras `compose down --volumes` quedaba un volumen
    `floci-code-blog-lab-backend-…` con etiquetas `floci=true` y
    `floci_emulator=floci-aws`. Compose no lo retira porque **no lo creo el
    Compose**: lo creo el emulador a traves del socket de Docker, igual que crea
    los contenedores de las funciones.

    La primera comprobacion solo buscaba por **nombre de proyecto**, asi que
    declaraba «0 volumenes» mientras ese seguia ahi. Buscar tambien por la
    **etiqueta del emulador** es lo que cierra el hueco.
    """

    def consultas_realizadas(self):
        registradas = []

        def listar(argumentos):
            registradas.append(argumentos)
            return []

        lanzador.residuos_del_laboratorio(
            {"LAB_COMPOSE_PROJECT_NAME": "personal-blog-lab"}, listar=listar
        )
        return registradas

    def test_se_consultan_las_tres_categorias(self):
        aplanadas = [" ".join(a) for a in self.consultas_realizadas()]
        for categoria in ("ps", "network ls", "volume ls"):
            with self.subTest(categoria=categoria):
                self.assertTrue(
                    any(categoria in c for c in aplanadas),
                    f"no se consulta {categoria}",
                )

    def test_se_busca_por_nombre_de_proyecto(self):
        aplanadas = [" ".join(a) for a in self.consultas_realizadas()]
        self.assertTrue(any("name=personal-blog-lab" in c for c in aplanadas))

    def test_se_busca_tambien_por_la_etiqueta_del_emulador(self):
        """Lo que Compose no creo, Compose no lo retira."""
        aplanadas = [" ".join(a) for a in self.consultas_realizadas()]
        self.assertTrue(
            any("label=floci=true" in c for c in aplanadas),
            "no se buscan los recursos que crea el emulador por el socket de Docker",
        )

    def test_los_recursos_del_emulador_se_reportan_como_residuo(self):
        def listar(argumentos):
            if "label=floci=true" in " ".join(argumentos) and "volume" in " ".join(argumentos):
                return ["floci-code-blog-lab-backend-ZYBBAQ"]
            return []

        residuos = lanzador.residuos_del_laboratorio(
            {"LAB_COMPOSE_PROJECT_NAME": "personal-blog-lab"}, listar=listar
        )
        planos = [v for valores in residuos.values() for v in valores]
        self.assertIn("floci-code-blog-lab-backend-ZYBBAQ", planos)


class DiferenciasDeclaradasTests(unittest.TestCase):
    def test_cada_diferencia_del_destino_declara_su_motivo(self):
        # H-025-1 se resolvio en Floci 2.1.0; una lista vacia es valida.
        for diferencia in lanzador.DIFERENCIAS_DEL_DESTINO_LOCAL:
            with self.subTest(tipo=diferencia.tipo):
                self.assertTrue(diferencia.tipo)
                self.assertTrue(diferencia.atributo)
                self.assertGreater(len(diferencia.motivo), 40)

    def test_regresion_de_tags_ssm_ya_no_se_tolera(self):
        from laboratorio.inventario import ErrorDeInventario, exigir_sin_cambios

        plan = {"resource_changes": [{
            "address": "aws_ssm_parameter.ejemplo", "type": "aws_ssm_parameter",
            "change": {"actions": ["update"],
                       "before": {"tags_all": {}},
                       "after": {"tags_all": {"Proyecto": "personal-blog"}}},
        }]}
        with self.assertRaises(ErrorDeInventario):
            exigir_sin_cambios(2, plan=plan, diferencias_toleradas=lanzador.DIFERENCIAS_DEL_DESTINO_LOCAL)

    def test_el_lanzador_NO_declara_su_propio_digest_del_runtime(self):
        """Una sola autoridad sobre el runtime: el manifiesto de Task/024.

        Cambio de expectativa justificado, y conviene dejar por escrito por que.
        Hasta la correccion de **H-025-3** esta prueba exigia lo contrario: que el
        lanzador declarase `DIGEST_DEL_RUNTIME_DE_TASK024`, una constante copiada a
        mano de Task/024. Esa constante era la mitad del defecto —la otra mitad era
        comparar contra la etiqueta movil—: duplicaba una decision que pertenece a
        Task/024 y podia desincronizarse en silencio.

        El requisito cambio: ahora el digest se **lee** del `manifiesto.json` que
        Task/024 escribe junto al artefacto. Asi que la expectativa correcta es la
        inversa, y esta prueba la fija: el lanzador **no** debe declarar ningun
        digest de runtime propio.
        """
        self.assertFalse(hasattr(lanzador, "DIGEST_DEL_RUNTIME_DE_TASK024"))
        self.assertFalse(hasattr(lanzador, "ETIQUETA_DEL_RUNTIME"))

    def test_el_lanzador_no_asigna_ninguna_constante_del_runtime(self):
        """Ninguna asignacion de modulo puede fijar el runtime.

        Se recorre el arbol sintactico en lugar de buscar texto: mencionar la
        etiqueta en un comentario que explica por que ya NO es autoridad es
        correcto y debe seguir permitido. Lo que no puede existir es una
        **asignacion** que la convierta otra vez en dato del lanzador.

        Mismo enfoque que la guarda del adaptador de `Task/023`, que recorre `app/`
        con `ast` para comprobar que `mangum` no se filtra.
        """
        import ast

        arbol = ast.parse(Path(lanzador.__file__).read_text(encoding="utf-8"))
        sospechosas = []
        for nodo in arbol.body:
            if not isinstance(nodo, (ast.Assign, ast.AnnAssign)):
                continue
            for literal in ast.walk(nodo):
                if isinstance(literal, ast.Constant) and isinstance(literal.value, str):
                    if "public.ecr.aws/lambda" in literal.value or (
                        literal.value.startswith("sha256:") and len(literal.value) == 71
                    ):
                        destinos = (
                            [nodo.target] if isinstance(nodo, ast.AnnAssign) else nodo.targets
                        )
                        nombres = [
                            t.id for t in destinos if isinstance(t, ast.Name)
                        ] or ["<sin nombre>"]
                        sospechosas.append((nombres[0], literal.value[:40]))
        self.assertEqual(
            sospechosas, [], f"el lanzador vuelve a fijar el runtime: {sospechosas}"
        )


class SeleccionExplicitaDelDestinoTests(unittest.TestCase):
    """R-24: omitir el destino debe abortar antes de ejecutar un comando."""

    def test_el_modo_no_tiene_valor_por_omision(self):
        with self.assertRaises(SystemExit):
            lanzador.construir_parser().parse_args(["herramientas"])

    def test_local_declarado_explicitamente_se_conserva(self):
        argumentos = lanzador.construir_parser().parse_args(
            ["--modo", "local", "herramientas"]
        )
        self.assertEqual(argumentos.modo, "local")


class PublicacionLoopbackTests(unittest.TestCase):
    """R-23: se juzgan todos los bindings, no solo la URL anunciada."""

    def inspeccion(self, bindings):
        return [
            {
                "Config": {
                    "Labels": {
                        "com.docker.compose.project": "personal-blog-lab",
                        "com.docker.compose.service": "emulador",
                    }
                },
                "NetworkSettings": {"Ports": bindings},
            }
        ]

    def validar(self, bindings):
        return lanzador.validar_publicacion_de_floci(
            self.inspeccion(bindings),
            proyecto_esperado="personal-blog-lab",
            puerto_esperado="4566",
        )

    def test_acepta_unicamente_4566_publicado_en_127_0_0_1(self):
        observados = self.validar(
            {"4566/tcp": [{"HostIp": "127.0.0.1", "HostPort": "4566"}]}
        )
        self.assertEqual(observados, ["4566/tcp -> 127.0.0.1:4566"])

    def test_rechaza_publicacion_en_todas_las_interfaces(self):
        for host in ("0.0.0.0", "::"):
            with self.subTest(host=host), self.assertRaises(
                lanzador.ErrorDelLaboratorio
            ):
                self.validar(
                    {"4566/tcp": [{"HostIp": host, "HostPort": "4566"}]}
                )

    def test_rechaza_publicacion_en_lan(self):
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            self.validar(
                {"4566/tcp": [{"HostIp": "192.168.1.20", "HostPort": "4566"}]}
            )

    def test_rechaza_un_binding_auxiliar_aunque_sea_loopback(self):
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            self.validar(
                {
                    "4566/tcp": [
                        {"HostIp": "127.0.0.1", "HostPort": "4566"},
                        {"HostIp": "127.0.0.1", "HostPort": "4570"},
                    ]
                }
            )

    def test_rechaza_ausencia_de_publicacion_demostrable(self):
        with self.assertRaises(lanzador.ErrorDelLaboratorio):
            self.validar({"4566/tcp": None})


class OperacionesDeRunbookTests(unittest.TestCase):
    """Task/026: operaciones separadas y aprobación humana no eludible."""

    def test_el_parser_expone_las_cinco_operaciones(self):
        casos = {
            "crear": ["--lambda-zip", "funcion.zip"],
            "validar": ["--lambda-zip", "funcion.zip"],
            "rollback": ["--lambda-zip", "funcion-anterior.zip"],
            "destruir": ["--lambda-zip", "funcion.zip"],
            "recuperar": ["--lambda-zip", "funcion.zip"],
            "inspeccionar-sdk": ["--lambda-zip", "funcion.zip"],
        }
        for comando, resto in casos.items():
            with self.subTest(comando=comando):
                argumentos = lanzador.construir_parser().parse_args(
                    ["--modo", "local", comando, *resto]
                )
                self.assertEqual(argumentos.comando, comando)

    def test_la_confirmacion_exige_el_sha256_completo_del_plan(self):
        sha256 = "a" * 64
        observado = lanzador.exigir_confirmacion_del_plan(
            sha256,
            operacion="crear",
            leer=lambda _: f"APLICAR {sha256}",
        )
        self.assertEqual(observado, sha256)

    def test_no_hay_confirmacion_parcial_ni_palabra_de_fuerza(self):
        sha256 = "b" * 64
        for respuesta in ("si", "--force", "APLICAR", f"APLICAR {sha256[:12]}"):
            with self.subTest(respuesta=respuesta), self.assertRaises(
                lanzador.ErrorDelLaboratorio
            ):
                lanzador.exigir_confirmacion_del_plan(
                    sha256,
                    operacion="destruir",
                    leer=lambda _, valor=respuesta: valor,
                )

    def test_el_sdk_usa_endpoints_locales_y_encuentra_el_inventario(self):
        respuestas = {
            "s3": {"Buckets": [{"Name": "blog-lab-medios"}]},
            "ssm": {
                "Parameters": [{"Name": "/blog-lab/local/storage_region"}]
            },
            "iam": {"Roles": [{"RoleName": "blog-lab-lambda"}]},
            "lambda": {"Functions": [{"FunctionName": "blog-lab-backend"}]},
            "apigatewayv2": {
                "Items": [{"ApiId": "api-1", "Name": "blog-lab-api"}]
            },
            "logs": {
                "logGroups": [{"logGroupName": "/aws/lambda/blog-lab-backend"}]
            },
        }

        class ClienteFalso:
            def __init__(self, servicio):
                self.servicio = servicio

            def __getattr__(self, _):
                return lambda **__: respuestas[self.servicio]

        class SesionFalsa:
            llamadas = []

            def __init__(self, **credenciales):
                self.credenciales = credenciales

            def client(self, servicio, **opciones):
                self.llamadas.append((servicio, opciones))
                return ClienteFalso(servicio)

        class Boto3Falso:
            __version__ = "test"
            Session = SesionFalsa

        endpoints = {s: "http://127.0.0.1:4566" for s in guarda.SERVICIOS}
        destino = guarda.Destino(
            modo="local",
            region="us-east-1",
            endpoints=endpoints,
            cuenta_esperada="000000000000",
        )
        valores = {
            "bucket_de_medios": "blog-lab-medios",
            "parametros": ["/blog-lab/local/storage_region"],
            "rol_de_ejecucion": "blog-lab-lambda",
            "nombre_de_la_funcion": "blog-lab-backend",
            "id_del_api": "api-1",
            "grupo_de_logs": "/aws/lambda/blog-lab-backend",
        }

        informe = lanzador.inspeccionar_con_sdk(
            destino,
            valores,
            ruta_del_artefacto=Path("funcion.zip"),
            boto3_modulo=Boto3Falso,
        )

        self.assertEqual(informe["sdk"], "boto3/test")
        self.assertEqual(set(informe["servicios"]), set(respuestas))
        self.assertEqual(
            {opciones["endpoint_url"] for _, opciones in SesionFalsa.llamadas},
            {"http://127.0.0.1:4566"},
        )

    def test_el_sdk_se_extrae_para_que_botocore_vea_sus_datos(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            artefacto = raiz / "funcion.zip"
            destino = raiz / "sdk"
            with zipfile.ZipFile(artefacto, "w") as paquete:
                paquete.writestr("boto3/__init__.py", "__version__ = 'prueba'\n")
                paquete.writestr("botocore/data/endpoints.json", "{}\n")

            lanzador.extraer_artefacto_para_sdk(artefacto, destino)

            self.assertEqual(
                (destino / "botocore/data/endpoints.json").read_text(
                    encoding="utf-8"
                ),
                "{}\n",
            )

    def test_la_extraccion_del_sdk_rechaza_zip_slip(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            artefacto = raiz / "funcion.zip"
            with zipfile.ZipFile(artefacto, "w") as paquete:
                paquete.writestr("../fuera.txt", "no")
            with self.assertRaises(lanzador.ErrorDelLaboratorio):
                lanzador.extraer_artefacto_para_sdk(artefacto, raiz / "sdk")


if __name__ == "__main__":
    unittest.main()
