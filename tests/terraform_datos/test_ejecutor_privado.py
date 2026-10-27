"""H-031-5: ejecutora privada de D-24, shell SIN base de datos (Task/031).

Contrato que estas pruebas fijan ANTES del codigo:
- Solo biblioteca estandar: el modulo importa `json` y `sys`, nada mas.
- Handler exacto `manejar(evento, contexto)`, que en el ZIP es `ejecutor.manejar`.
- Payload CERRADO: un objeto con la UNICA clave `modo`, que es `selfcheck` o un modo de D-24.
- Los modos de D-24 (`verify`, `export`, `upgrade`, `downgrade`, `purge`) responden `NOT_IMPLEMENTED` con su
  fase propietaria y SIN efectos: ninguna conexion de red.
- Salida y registro saneados: nunca se repite el evento ni se devuelve una traza.
- Ninguna referencia a credenciales, cadenas de conexion, SSM, KMS ni S3 en la fuente.
"""
import ast
import contextlib
import importlib.util
import io
import json
import socket
import sys
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
FUENTE = RAIZ / "terraform" / "modulos" / "ejecutor_privado" / "codigo" / "ejecutor.py"
CONTRATO = "d24-ejecutor-h0315-v1"
CANARIO = "CanarioDelPayloadQueNoDebeAparecer0123456789"
MODOS_D24 = {"verify": "H-031-6", "export": "H-031-6", "upgrade": "Task/036", "downgrade": "Task/036",
             "purge": "Task/036"}
PROHIBIDOS = ("password", "contrase", "database_url", "secret", "ssm", "kms", "boto", "socket", "ssl", "urllib",
              "http", "psycopg", "environ", "getenv", "subprocess", "s3", "credential", "token")


def cargar():
    spec = importlib.util.spec_from_file_location("ejecutor_bajo_prueba", FUENTE)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class SinRed:
    """Cualquier intento de abrir un socket queda REGISTRADO y falla: la prueba exige la lista vacia."""

    def __init__(self):
        self.intentos = []

    def _bloquear(self, *args, **kwargs):
        self.intentos.append(args[:1])
        raise OSError("red prohibida en la ejecutora de H-031-5")

    def __enter__(self):
        self._parches = [mock.patch.object(socket.socket, "connect", self._bloquear),
                         mock.patch.object(socket, "create_connection", self._bloquear),
                         mock.patch.object(socket, "getaddrinfo", self._bloquear)]
        for parche in self._parches:
            parche.start()
        return self

    def __exit__(self, *exc):
        for parche in self._parches:
            parche.stop()
        return False


def invocar(modulo, evento):
    salida, errores = io.StringIO(), io.StringIO()
    with SinRed() as red, contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
        respuesta = modulo.manejar(evento, object())
    return respuesta, salida.getvalue(), errores.getvalue(), red.intentos


class Contrato(unittest.TestCase):
    def setUp(self):
        self.modulo = cargar()

    def test_handler_exacto(self):
        arbol = ast.parse(FUENTE.read_text(encoding="utf-8"))
        funciones = {n.name: [a.arg for a in n.args.args] for n in arbol.body if isinstance(n, ast.FunctionDef)}
        self.assertEqual(funciones.get("manejar"), ["evento", "contexto"])

    def test_selfcheck_responde_el_contrato_sin_red(self):
        respuesta, salida, errores, intentos = invocar(self.modulo, {"modo": "selfcheck"})
        self.assertEqual(respuesta, {
            "contrato": CONTRATO, "estado": "OK", "modo": "selfcheck",
            "python": f"{sys.version_info.major}.{sys.version_info.minor}",
            "modos_d24": {modo: "NOT_IMPLEMENTED" for modo in MODOS_D24},
        })
        self.assertEqual((intentos, errores), ([], ""))

    def test_cada_modo_d24_no_implementado_y_sin_efectos(self):
        for modo, fase in MODOS_D24.items():
            with self.subTest(modo=modo):
                respuesta, _, errores, intentos = invocar(self.modulo, {"modo": modo})
                self.assertEqual(respuesta, {"contrato": CONTRATO, "estado": "NOT_IMPLEMENTED", "modo": modo,
                                             "fase_propietaria": fase})
                self.assertEqual((intentos, errores), ([], ""))

    def test_los_modos_del_contrato_son_exactos(self):
        self.assertEqual(self.modulo.FASES, MODOS_D24)
        self.assertEqual(self.modulo.MODOS, ("selfcheck", *MODOS_D24))

    def test_payload_cerrado(self):
        class Diccionario(dict):
            pass

        invalidos = [None, [], "selfcheck", 7, {}, {"modo": "VERIFY"}, {"modo": " verify"}, {"modo": "verify "},
                     {"modo": 1}, {"modo": True}, {"modo": None}, {"modo": ["verify"]}, {"Modo": "verify"},
                     {"modo": "verify", "extra": 1}, {"modo": "selfcheck", "credencial": "x"}, {"modo": "otro"},
                     Diccionario(modo="verify")]
        for evento in invalidos:
            with self.subTest(evento=repr(evento)):
                respuesta, _, errores, intentos = invocar(self.modulo, evento)
                self.assertEqual(respuesta, {"contrato": CONTRATO, "estado": "INVALID_PAYLOAD"})
                self.assertEqual((intentos, errores), ([], ""))

    def test_nunca_repite_el_evento(self):
        for evento in ({"modo": CANARIO}, {"modo": "verify", CANARIO: CANARIO}, {CANARIO: "selfcheck"},
                       {"modo": "selfcheck", "extra": CANARIO}):
            with self.subTest(evento=evento):
                respuesta, salida, errores, _ = invocar(self.modulo, evento)
                self.assertNotIn(CANARIO, json.dumps(respuesta) + salida + errores)

    def test_registro_saneado_una_linea_por_invocacion(self):
        for evento, esperado in (({"modo": "selfcheck"}, ("OK", "selfcheck")),
                                 ({"modo": "purge"}, ("NOT_IMPLEMENTED", "purge")),
                                 ({"modo": "x"}, ("INVALID_PAYLOAD", None))):
            with self.subTest(evento=evento):
                _, salida, _, _ = invocar(self.modulo, evento)
                lineas = salida.splitlines()
                self.assertEqual(len(lineas), 1)
                self.assertEqual(json.loads(lineas[0]), {"contrato": CONTRATO, "estado": esperado[0],
                                                         "modo": esperado[1]})

    def test_error_interno_sin_traza_ni_detalle(self):
        with mock.patch.object(self.modulo.json, "dumps", side_effect=RuntimeError("detalle-interno")):
            respuesta, salida, errores, _ = invocar(self.modulo, {"modo": "selfcheck"})
        self.assertEqual(respuesta, {"contrato": CONTRATO, "estado": "INTERNAL_ERROR"})
        for texto in (json.dumps(respuesta), salida, errores):
            self.assertNotIn("detalle-interno", texto)
            self.assertNotIn("Traceback", texto)

    def test_determinista(self):
        for evento in ({"modo": "selfcheck"}, {"modo": "export"}, {"modo": "?"}):
            with self.subTest(evento=evento):
                self.assertEqual(invocar(self.modulo, evento)[:2], invocar(self.modulo, evento)[:2])


class FuenteSinDependenciasNiSecretos(unittest.TestCase):
    def setUp(self):
        self.texto = FUENTE.read_text(encoding="utf-8")
        self.arbol = ast.parse(self.texto)

    def test_solo_biblioteca_estandar_json_y_sys(self):
        importados = set()
        for nodo in ast.walk(self.arbol):
            if isinstance(nodo, ast.Import):
                importados |= {alias.name for alias in nodo.names}
            elif isinstance(nodo, ast.ImportFrom):
                importados.add(nodo.module)
        self.assertEqual(importados, {"json", "sys"})

    def test_sin_referencias_a_credenciales_red_ni_servicios(self):
        minusculas = self.texto.lower()
        for palabra in PROHIBIDOS:
            with self.subTest(palabra=palabra):
                self.assertNotIn(palabra, minusculas)

    def test_sin_ejecucion_dinamica_ni_archivos(self):
        llamadas = {n.func.id for n in ast.walk(self.arbol)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertFalse(llamadas & {"open", "exec", "eval", "compile", "__import__", "getattr", "input"})

    def test_fuente_normalizada(self):
        crudo = FUENTE.read_bytes()
        self.assertNotIn(b"\r", crudo)
        self.assertFalse(crudo.startswith(b"\xef\xbb\xbf"))


if __name__ == "__main__":
    unittest.main()
