"""H-031-6: el operador invoca la ejecutora con credenciales EN MEMORIA (Task/031). Clientes AWS simulados.

Contrato que estas pruebas fijan ANTES del codigo:
- Solo `PersonalBlogAdministrator` (la identidad operativa decidida en H-031-IAM) y solo us-east-2; si no, nada se lee.
- Cada modo lee de SSM SOLO las credenciales que necesita, con descifrado, y las mantiene en memoria.
- `identidades` envia verificadores SCRAM calculados aqui: la contrasena de blog_migrate y blog_app nunca viaja.
- La invocacion es SINCRONA (`RequestResponse`) y sin cola de logs (`LogType=None`).
- Sale solo la respuesta saneada de la ejecutora. Si contuviera un secreto o el host, se aborta sin imprimirla.
- Cualquier error sale como codigo cerrado, sin mensaje (los de AWS pueden llevar ARN con la cuenta).
"""
import base64
import contextlib
import hashlib
import hmac
import io
import json
import re
import unittest
from pathlib import Path

from scripts.terraform_datos import operar_ejecutora as op
from scripts.terraform_datos import scram

RAIZ = Path(__file__).resolve().parents[2]
CUENTA = "123456789012"
ARN_ADMIN = f"arn:aws:sts::{CUENTA}:assumed-role/PersonalBlogAdministrator/sesion-de-prueba"
HOST = "blog-prod-postgres.abcdefghijkl.us-east-2.rds.amazonaws.com"
RESTAURADA = "blog-prod-restore-h0317-20261007120000"
HOST_RESTAURADA = f"{RESTAURADA}.abcdefghijkl.us-east-2.rds.amazonaws.com"
CLAVES = {"/blog-prod/datos/blogadmin": "M" * 24 + "a1" * 12, "/blog-prod/datos/blog_migrate": "G" * 24 + "b2" * 12,
          "/blog-prod/datos/blog_app": "P" * 24 + "c3" * 12}
SECRETOS = (*CLAVES.values(), HOST, HOST_RESTAURADA, CUENTA)


class Carga:
    def __init__(self, datos):
        self.datos = datos

    def read(self):
        return self.datos


class Sts:
    def __init__(self, arn=ARN_ADMIN):
        self.arn = arn

    def get_caller_identity(self):
        return {"Arn": self.arn, "Account": CUENTA, "UserId": "AROAEJEMPLO:sesion-de-prueba"}


class Ssm:
    def __init__(self):
        self.leidos = []

    def get_parameter(self, Name, WithDecryption):
        assert WithDecryption is True
        self.leidos.append(Name)
        return {"Parameter": {"Name": Name, "Value": CLAVES[Name], "ARN": f"arn:aws:ssm:us-east-2:{CUENTA}:parameter{Name}"}}


class Rds:
    def describe_db_instances(self, DBInstanceIdentifier):
        direccion = {"blog-prod-postgres": HOST, RESTAURADA: HOST_RESTAURADA}[DBInstanceIdentifier]
        return {"DBInstances": [{"DBInstanceIdentifier": DBInstanceIdentifier, "DBInstanceStatus": "available",
                                 "Endpoint": {"Address": direccion, "Port": 5432}}]}


class Lambda:
    def __init__(self, respuesta=None, error=None):
        self.llamadas = []
        self.respuesta = respuesta or {"contrato": "d24-ejecutor-h0316-v1", "estado": "OK", "modo": "verify"}
        self.error = error

    def invoke(self, **parametros):
        self.llamadas.append(parametros)
        resultado = {"StatusCode": 200, "ExecutedVersion": "$LATEST",
                     "Payload": Carga(json.dumps(self.respuesta).encode())}
        if self.error:
            resultado["FunctionError"] = self.error
        return resultado


class Base(unittest.TestCase):
    def ejecutar(self, argumentos, sts=None, ssm=None, lambda_=None, rds=None):
        self.ssm, self.lambda_ = ssm or Ssm(), lambda_ or Lambda()
        clientes = {"sts": sts or Sts(), "ssm": self.ssm, "lambda": self.lambda_, "rds": rds or Rds()}
        salida, errores = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            codigo = op.main(argumentos, clientes=lambda: clientes)
        texto = salida.getvalue() + errores.getvalue()
        for secreto in SECRETOS:
            self.assertNotIn(secreto, texto, "el operador nunca imprime un secreto, el host ni la cuenta")
        return codigo, salida.getvalue(), errores.getvalue()

    def evento(self, indice=0):
        llamada = self.lambda_.llamadas[indice]
        self.assertEqual((llamada["FunctionName"], llamada["InvocationType"], llamada["LogType"]),
                         ("blog-prod-ejecutor", "RequestResponse", "None"))
        self.assertEqual(set(llamada), {"FunctionName", "InvocationType", "LogType", "Payload"})
        return json.loads(llamada["Payload"])


class Identidad(Base):
    def test_solo_personal_blog_administrator(self):
        for arn in (f"arn:aws:sts::{CUENTA}:assumed-role/PersonalBlogOperadorDatos/s",
                    f"arn:aws:iam::{CUENTA}:root", f"arn:aws:iam::{CUENTA}:user/alguien",
                    f"arn:aws:sts::{CUENTA}:assumed-role/PersonalBlogAdministratorX/s"):
            with self.subTest(arn=arn):
                codigo, salida, _ = self.ejecutar(["selfcheck"], sts=Sts(arn))
                self.assertEqual(codigo, 1)
                self.assertEqual(json.loads(salida), {"estado": "IDENTIDAD_NO_AUTORIZADA"})
                self.assertEqual((self.ssm.leidos, self.lambda_.llamadas), ([], []))


class Modos(Base):
    def test_selfcheck_sin_credenciales(self):
        codigo, salida, _ = self.ejecutar(["selfcheck"])
        self.assertEqual(codigo, 0)
        self.assertEqual(self.evento(), {"modo": "selfcheck"})
        self.assertEqual(self.ssm.leidos, [])
        self.assertEqual(json.loads(salida)["estado"], "OK")

    def test_verify_lee_solo_la_credencial_de_su_identidad(self):
        codigo, _, _ = self.ejecutar(["verify", "--usuario", "blog_app", "--controles-negativos"])
        self.assertEqual(codigo, 0)
        self.assertEqual(self.ssm.leidos, ["/blog-prod/datos/blog_app"])
        self.assertEqual(self.evento(), {"modo": "verify", "destino": {"host": HOST, "base": "personal_blog"},
                                         "credencial": {"usuario": "blog_app",
                                                        "contrasena": CLAVES["/blog-prod/datos/blog_app"]},
                                         "controles_negativos": True})

    def test_verify_de_una_restaurada_con_marcador(self):
        marcador = "3f2b8c1e-7a4d-4e9b-9c2f-5d6e7f8a9b0c"
        self.ejecutar(["verify", "--usuario", "blog_migrate", "--restaurada", RESTAURADA, "--marcador", marcador])
        evento = self.evento()
        self.assertEqual(evento["destino"], {"host": HOST_RESTAURADA, "base": "personal_blog"})
        self.assertEqual(evento["marcador"], {"id": marcador})

    def test_restaurada_fuera_del_patron_de_h0317(self):
        for identificador in ("blog-prod-postgres", "blog-prod-restore-h0317-2026", "otra-instancia"):
            with self.subTest(identificador=identificador):
                codigo, salida, _ = self.ejecutar(["verify", "--usuario", "blog_migrate", "--restaurada", identificador])
                self.assertEqual((codigo, json.loads(salida)), (1, {"estado": "ARGUMENTOS_NO_ADMITIDOS"}))
                self.assertEqual(self.lambda_.llamadas, [])

    def test_identidades_envia_solo_verificadores_de_las_contrasenas_custodiadas(self):
        self.ejecutar(["identidades"])
        self.assertEqual(sorted(self.ssm.leidos), sorted(CLAVES))
        evento = self.evento()
        self.assertEqual(evento["credencial"], {"usuario": "blogadmin", "contrasena": CLAVES["/blog-prod/datos/blogadmin"]})
        texto = json.dumps(evento)
        for rol in ("blog_migrate", "blog_app"):
            with self.subTest(rol=rol):
                contrasena = CLAVES[f"/blog-prod/datos/{rol}"]
                self.assertNotIn(contrasena, texto, "la contrasena de la identidad nunca viaja")
                verificador = evento["verificadores"][rol]
                self.assertRegex(verificador, r"^SCRAM-SHA-256\$4096:[A-Za-z0-9+/]{22}==\$[A-Za-z0-9+/]{43}=:[A-Za-z0-9+/]{43}=$")
                sal = base64.b64decode(verificador.split("$")[1].split(":")[1])
                self.assertEqual(verificador, scram.verificador(contrasena, sal=sal),
                                 "el verificador corresponde a la contrasena custodiada en SSM")

    def test_sintetico_y_export(self):
        marcador = "3f2b8c1e-7a4d-4e9b-9c2f-5d6e7f8a9b0c"
        self.ejecutar(["sintetico", "--accion", "sembrar", "--marcador", marcador, "--instante", "2026-10-07T12:00:00Z"])
        self.assertEqual(self.evento(), {"modo": "sintetico", "destino": {"host": HOST, "base": "personal_blog"},
                                         "credencial": {"usuario": "blog_migrate",
                                                        "contrasena": CLAVES["/blog-prod/datos/blog_migrate"]},
                                         "marcador": {"id": marcador, "instante": "2026-10-07T12:00:00Z"},
                                         "accion": "sembrar"})
        self.ejecutar(["export", "--bucket", "blog-prod-medios-ejemplo", "--marca", "20261007T120000Z"])
        evento = self.evento()
        self.assertEqual((evento["modo"], evento["salida"]),
                         ("export", {"bucket": "blog-prod-medios-ejemplo", "marca": "20261007T120000Z"}))
        self.assertEqual(evento["credencial"]["usuario"], "blog_migrate")


class SinReinvocaciones(unittest.TestCase):
    """D-24 modificada el 2026-10-18 (aprobada el 2026-10-19): con concurrencia no reservada, un error de red no debe convertirse en
    una SEGUNDA ejecucion. El cliente de Lambda del operador no reintenta, y su tiempo de lectura cubre el timeout de
    la funcion (30 s). RDS tampoco reintenta: H-031-7 lo usa para restore y borrado."""

    def test_el_cliente_de_lambda_no_reintenta(self):
        import sys
        import types
        from unittest import mock

        creados = {}

        class Config:
            def __init__(self, **opciones):
                self.opciones = opciones

        class Session:
            def __init__(self, **opciones):
                self.opciones = opciones

            def client(self, nombre, config=None):
                creados[nombre] = config
                return nombre

        boto3 = types.SimpleNamespace(Session=Session)
        config = types.SimpleNamespace(Config=Config)
        botocore = types.SimpleNamespace(config=config)
        with mock.patch.dict(sys.modules, {"boto3": boto3, "botocore": botocore, "botocore.config": config}):
            clientes = op._clientes()
        self.assertEqual(set(clientes), {"sts", "ssm", "lambda", "rds"})
        self.assertEqual(creados["lambda"].opciones,
                         {"retries": {"total_max_attempts": 1, "mode": "standard"}, "read_timeout": 70})
        self.assertEqual({nombre: creados[nombre] for nombre in ("sts", "ssm")}, {"sts": None, "ssm": None})
        self.assertEqual(creados["rds"].opciones["retries"]["total_max_attempts"], 1)


class Salida(Base):
    def test_imprime_solo_la_respuesta_saneada(self):
        respuesta = {"contrato": "d24-ejecutor-h0316-v1", "estado": "OK", "modo": "verify",
                     "conexion": {"tls": True, "version_tls": "TLSv1.3"}}
        codigo, salida, errores = self.ejecutar(["verify", "--usuario", "blogadmin"], lambda_=Lambda(respuesta))
        self.assertEqual((codigo, json.loads(salida), errores), (0, respuesta, ""))

    def test_un_estado_distinto_de_ok_sale_con_codigo_1(self):
        respuesta = {"contrato": "d24-ejecutor-h0316-v1", "estado": "TLS_FALLIDO", "modo": "verify"}
        codigo, salida, _ = self.ejecutar(["verify", "--usuario", "blogadmin"], lambda_=Lambda(respuesta))
        self.assertEqual((codigo, json.loads(salida)), (1, respuesta))

    def test_error_de_la_funcion(self):
        codigo, salida, _ = self.ejecutar(["selfcheck"], lambda_=Lambda(error="Unhandled"))
        self.assertEqual((codigo, json.loads(salida)), (1, {"estado": "INVOCACION_FALLIDA"}))

    def test_una_respuesta_con_un_secreto_no_se_imprime(self):
        for fuga in (CLAVES["/blog-prod/datos/blog_app"], HOST):
            with self.subTest(fuga=fuga[:6]):
                respuesta = {"estado": "OK", "detalle": f"x{fuga}x"}
                codigo, salida, _ = self.ejecutar(["verify", "--usuario", "blog_app"], lambda_=Lambda(respuesta))
                self.assertEqual((codigo, json.loads(salida)), (1, {"estado": "RESPUESTA_CON_SECRETO"}))

    def test_errores_de_aws_solo_como_codigo(self):
        class Ssm_que_falla(Ssm):
            def get_parameter(self, Name, WithDecryption):
                raise RuntimeError(f"AccessDeniedException: arn:aws:iam::{CUENTA}:role/x no puede leer {Name}")

        codigo, salida, _ = self.ejecutar(["verify", "--usuario", "blogadmin"], ssm=Ssm_que_falla())
        self.assertEqual((codigo, json.loads(salida)), (1, {"estado": "ERROR_DEL_OPERADOR", "tipo": "RuntimeError"}))


class InvocarModo(unittest.TestCase):
    """API para otros orquestadores (restore de H-031-7): la respuesta como dict, los fallos como `Abortar`."""

    def clientes(self, lambda_=None):
        return {"sts": Sts(), "ssm": Ssm(), "lambda": lambda_ or Lambda(), "rds": Rds()}

    def test_devuelve_la_respuesta_saneada(self):
        respuesta = {"contrato": "d24-ejecutor-h0316-v1", "estado": "OK", "modo": "verify"}
        self.assertEqual(op.invocar_modo(["verify", "--usuario", "blogadmin"], self.clientes(Lambda(respuesta))),
                         respuesta)

    def test_los_fallos_son_abortar_con_codigo(self):
        with self.assertRaises(op.Abortar) as fallo:
            op.invocar_modo(["verify", "--usuario", "blog_app"],
                            self.clientes(Lambda({"estado": "OK", "x": CLAVES["/blog-prod/datos/blog_app"]})))
        self.assertEqual(fallo.exception.estado, "RESPUESTA_CON_SECRETO")


class Fuente(unittest.TestCase):
    def test_ni_disco_ni_argumentos_con_secretos(self):
        texto = (RAIZ / "scripts" / "terraform_datos" / "operar_ejecutora.py").read_text(encoding="utf-8")
        for prohibido in ("open(", "write_text", "write_bytes", "tempfile", "--contrasena", "--password",
                          "environ[", "putenv", "subprocess", "logging", "print(contrasena", "Tail"):
            with self.subTest(prohibido=prohibido):
                self.assertNotIn(prohibido, texto)
        self.assertEqual(re.findall(r'region_name="([a-z0-9-]+)"', texto), ["us-east-2"])

    def test_el_verificador_es_el_mismo_algoritmo_que_postgresql(self):
        # Garantia indirecta: `scram` ya se prueba contra el vector de RFC 7677; aqui se fija que el operador lo usa.
        self.assertIs(op.scram, scram)
        clave, sal = "A" * 40, bytes(range(16))
        _, almacenada, servidor = scram.claves(clave, sal)
        self.assertEqual(almacenada, hashlib.sha256(hmac.new(hashlib.pbkdf2_hmac("sha256", clave.encode(), sal, 4096),
                                                              b"Client Key", hashlib.sha256).digest()).digest())
        self.assertTrue(servidor)


if __name__ == "__main__":
    unittest.main()
