"""H-031-6: ejecutora privada de D-24 con PostgreSQL (Task/031). Pruebas unitarias con un conector simulado.

Contrato que estas pruebas fijan ANTES del codigo:
- Credenciales en el payload de una invocacion SINCRONA (mecanismo elegido en H-031-6): la funcion no lee SSM ni KMS,
  no tiene variables de entorno y nunca devuelve ni registra la contrasena, el host ni un verificador.
- TLS `verify-full` contra el bundle regional de RDS empaquetado; puerto 5432; base `personal_blog`.
- Host cerrado: solo la instancia productiva o una restaurada de H-031-7, en us-east-2.
- `identidades` crea o ajusta `blog_migrate` y `blog_app` SOLO con verificadores SCRAM (nunca texto plano), con los
  privilegios de D-23 §5.3 y los limites de conexion del presupuesto de D-12 §6.2.
- `verify` informa TLS, version, identidad y atributos; con `blog_app` demuestra que el DDL se rechaza (§9.2); con
  controles negativos demuestra que sin TLS y con otro nombre de host la conexion se rechaza.
- `sintetico` siembra o limpia un marcador NO sensible para H-031-7, con `blog_migrate`.
- `export` (D-10 §10.1) vuelca `public` con `blog_migrate` en una instantanea de solo lectura y escribe CSV y
  manifiesto en el prefijo dedicado del bucket, con escritura condicional y SHA-256; responde recuentos y claves.
- `upgrade`, `downgrade` y `purge` siguen `NOT_IMPLEMENTED` (Task/036).
"""
import ast
import base64
import contextlib
import hashlib
import importlib.util
import io
import json
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
CODIGO = RAIZ / "terraform" / "modulos" / "ejecutor_privado" / "codigo_h0316"
CONTRATO = "d24-ejecutor-h0316-v1"
HOST = "blog-prod-postgres.abcdefghijkl.us-east-2.rds.amazonaws.com"
RESTAURADA = "blog-prod-restore-h0317-20261007120000.abcdefghijkl.us-east-2.rds.amazonaws.com"
MASTER = "M" * 24 + "a1" * 12
MIGRA = "G" * 24 + "b2" * 12
APP = "P" * 24 + "c3" * 12
VERIF_M = "SCRAM-SHA-256$4096:AAECAwQFBgcICQoLDA0ODw==$" + "Q" * 43 + "=:" + "R" * 43 + "="
VERIF_A = "SCRAM-SHA-256$4096:EBESExQVFhcYGRobHB0eHw==$" + "S" * 43 + "=:" + "T" * 43 + "="
MARCADOR = "3f2b8c1e-7a4d-4e9b-9c2f-5d6e7f8a9b0c"
BUCKET = "blog-prod-medios-sintetico"
MARCA = "20261007T120000Z"
SECRETOS = (MASTER, MIGRA, APP, VERIF_M, VERIF_A, HOST, RESTAURADA)


def cargar():
    sys.path.insert(0, str(CODIGO))
    try:
        for nombre in ("ejecutor", "operaciones", "exportacion"):
            sys.modules.pop(nombre, None)
        spec = importlib.util.spec_from_file_location("ejecutor", CODIGO / "ejecutor.py")
        modulo = importlib.util.module_from_spec(spec)
        sys.modules["ejecutor"] = modulo
        spec.loader.exec_module(modulo)
        return modulo, sys.modules["operaciones"], sys.modules["exportacion"]
    finally:
        sys.path.remove(str(CODIGO))


class ErrorSimulado(Exception):
    def __init__(self, mensaje, sqlstate=None):
        super().__init__(mensaje)
        self.sqlstate = sqlstate


class Cursor:
    def __init__(self, conexion):
        self.conexion, self.filas = conexion, []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, parametros=None):
        normal = " ".join(sql.split())
        self.conexion.sql.append((normal, parametros))
        for patron, respuesta in self.conexion.respuestas:
            if patron in normal:
                valor = respuesta(normal, parametros) if callable(respuesta) else respuesta
                if isinstance(valor, Exception):
                    raise valor
                self.filas = valor if isinstance(valor, list) else [valor]
                return self
        self.filas = []
        return self

    def copy(self, sql):
        normal = " ".join(sql.split())
        self.conexion.sql.append((normal, "COPY"))
        for patron, trozos in self.conexion.copias:
            if patron in normal:
                return Copia(trozos)
        return Copia([])

    def fetchone(self):
        return self.filas[0] if self.filas else None

    def fetchall(self):
        return list(self.filas)


class Copia:
    def __init__(self, trozos):
        self.trozos = trozos

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def __iter__(self):
        return iter(self.trozos)


class Conexion:
    def __init__(self, parametros, respuestas, copias=()):
        self.parametros, self.respuestas, self.copias, self.sql = parametros, respuestas, copias, []
        self.commits = self.rollbacks = 0
        self.cerrada = False

    def cursor(self):
        return Cursor(self)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.cerrada = True


def respuestas_base(usuario="blogadmin"):
    return [
        ("current_setting('server_version')", ("17.11", usuario, usuario, "personal_blog")),
        ("FROM pg_stat_ssl", (True, "TLSv1.3", "TLS_AES_256_GCM_SHA384", 256)),
        ("current_setting('rds.force_ssl', true)", ("1",)),
        ("FROM pg_roles WHERE rolname = current_user", (False, False, False, False, False, -1)),
        # Al final: las pruebas que cambian una respuesta por indice siguen apuntando a la misma.
        ("pg_try_advisory_xact_lock", (True,)),
    ]


class Simulador:
    """Conector simulado: registra cada conexion y responde por fragmento de SQL."""

    def __init__(self, respuestas=None, fallos=None, copias=()):
        self.respuestas = respuestas if respuestas is not None else respuestas_base()
        self.fallos = fallos or (lambda parametros: None)
        self.copias = copias
        self.conexiones = []

    def __call__(self, **parametros):
        fallo = self.fallos(parametros)
        if fallo:
            raise fallo
        conexion = Conexion(parametros, self.respuestas, self.copias)
        self.conexiones.append(conexion)
        return conexion


def fallos_negativos(parametros):
    if parametros.get("sslmode") == "disable":
        return ErrorSimulado("FATAL: no pg_hba.conf entry for host, no encryption", "28000")
    if parametros.get("host", "").startswith("10."):
        return ErrorSimulado('server certificate for "x" does not match host name "10.40.0.9"')
    if parametros.get("sslrootcert") == "system":
        return ErrorSimulado("SSL error: certificate verify failed")
    return None


class S3Simulado:
    """Cliente S3 simulado: registra cada `put_object` o lanza el fallo indicado."""

    def __init__(self, fallo=None):
        self.objetos, self.fallo = [], fallo

    def put_object(self, **parametros):
        if self.fallo is not None:
            raise self.fallo
        self.objetos.append(parametros)
        return {"ETag": '"simulado"'}


class ErrorDeCliente(Exception):
    """Forma de `botocore.exceptions.ClientError`: el codigo viaja en `response`."""

    def __init__(self, codigo):
        super().__init__(f"An error occurred ({codigo}) when calling the PutObject operation: {BUCKET}")
        self.response = {"Error": {"Code": codigo, "Message": BUCKET}}


class EndpointConnectionError(Exception):
    """Mismo nombre que la excepcion de botocore cuando no hay ruta a S3."""


def sin_s3():
    raise AssertionError("ningun modo salvo export crea un cliente S3")


def destino(host=HOST):
    return {"host": host, "base": "personal_blog"}


def credencial(usuario="blogadmin", contrasena=MASTER):
    return {"usuario": usuario, "contrasena": contrasena}


class Base(unittest.TestCase):
    def setUp(self):
        self.ejecutor, self.operaciones, self.exportacion = cargar()

    def invocar(self, evento, simulador=None, resolver=None, s3=None):
        simulador = simulador or Simulador()
        salida, errores = io.StringIO(), io.StringIO()
        parches = [mock.patch.object(self.operaciones, "CONECTAR", simulador),
                   mock.patch.object(self.operaciones, "RESOLVER", resolver or (lambda host: "10.40.0.9")),
                   mock.patch.object(self.exportacion, "CLIENTE_S3", (lambda: s3) if s3 is not None else sin_s3)]
        with contextlib.ExitStack() as pila:
            for parche in parches:
                pila.enter_context(parche)
            pila.enter_context(contextlib.redirect_stdout(salida))
            pila.enter_context(contextlib.redirect_stderr(errores))
            respuesta = self.ejecutor.manejar(evento, object())
        texto = json.dumps(respuesta) + salida.getvalue() + errores.getvalue()
        for secreto in SECRETOS:
            self.assertNotIn(secreto, texto, "la respuesta o el registro repiten un secreto o el host")
        self.assertEqual(errores.getvalue(), "")
        self.assertEqual(len(salida.getvalue().splitlines()), 1)
        self.assertEqual(set(json.loads(salida.getvalue())), {"contrato", "estado", "modo"})
        return respuesta, simulador


class Contrato(Base):
    def test_selfcheck(self):
        r, _ = self.invocar({"modo": "selfcheck"})
        self.assertEqual(r, {"contrato": CONTRATO, "estado": "OK", "modo": "selfcheck",
                             "python": f"{sys.version_info.major}.{sys.version_info.minor}",
                             "modos_d24": {"verify": "IMPLEMENTED", "export": "IMPLEMENTED",
                                           "upgrade": "NOT_IMPLEMENTED", "downgrade": "NOT_IMPLEMENTED",
                                           "purge": "NOT_IMPLEMENTED"},
                             "modos_de_task031": ["identidades", "sintetico"]})

    def test_modos_de_task036_no_implementados(self):
        for modo, fase in (("upgrade", "Task/036"), ("downgrade", "Task/036"), ("purge", "Task/036")):
            with self.subTest(modo=modo):
                r, simulador = self.invocar({"modo": modo})
                self.assertEqual(r, {"contrato": CONTRATO, "estado": "NOT_IMPLEMENTED", "modo": modo,
                                     "fase_propietaria": fase})
                self.assertEqual(simulador.conexiones, [])

    def test_payloads_cerrados(self):
        validos = {
            "verify": {"modo": "verify", "destino": destino(), "credencial": credencial()},
            "identidades": {"modo": "identidades", "destino": destino(), "credencial": credencial(),
                            "verificadores": {"blog_migrate": VERIF_M, "blog_app": VERIF_A}},
            "sintetico": {"modo": "sintetico", "destino": destino(), "credencial": credencial("blog_migrate", MIGRA),
                          "marcador": {"id": MARCADOR, "instante": "2026-10-07T12:00:00Z"}, "accion": "sembrar"},
            "export": {"modo": "export", "destino": destino(), "credencial": credencial("blog_migrate", MIGRA),
                       "salida": {"bucket": BUCKET, "marca": MARCA}},
        }
        invalidos = [
            None, [], {}, {"modo": "verify"},
            {**validos["verify"], "extra": 1},
            {**validos["verify"], "destino": destino("otra-base.abcdefghijkl.us-east-2.rds.amazonaws.com")},
            {**validos["verify"], "destino": destino("blog-prod-postgres.abcdefghijkl.us-east-1.rds.amazonaws.com")},
            {**validos["verify"], "destino": destino("blog-prod-postgres.abcdefghijk.us-east-2.rds.amazonaws.com")},
            {**validos["verify"], "destino": destino("10.40.0.9")},
            {**validos["verify"], "destino": {"host": HOST, "base": "postgres"}},
            {**validos["verify"], "destino": {"host": HOST, "base": "personal_blog", "puerto": 5433}},
            {**validos["verify"], "credencial": credencial("postgres")},
            {**validos["verify"], "credencial": credencial(contrasena="corta")},
            {**validos["verify"], "credencial": {"usuario": "blogadmin"}},
            {**validos["verify"], "controles_negativos": "si"},
            {**validos["identidades"], "credencial": credencial("blog_migrate", MIGRA)},
            {**validos["identidades"], "verificadores": {"blog_migrate": VERIF_M}},
            {**validos["identidades"], "verificadores": {"blog_migrate": VERIF_M, "blog_app": APP}},
            {**validos["identidades"], "verificadores": {"blog_migrate": VERIF_M, "blog_app": VERIF_A.replace("4096", "1")}},
            {**validos["identidades"], "verificadores": {"blog_migrate": VERIF_M, "blog_app": VERIF_A + "'"}},
            {**validos["sintetico"], "credencial": credencial()},
            {**validos["sintetico"], "accion": "borrar_todo"},
            {**validos["sintetico"], "marcador": {"id": "no-es-uuid", "instante": "2026-10-07T12:00:00Z"}},
            {**validos["sintetico"], "marcador": {"id": MARCADOR, "instante": "ayer"}},
            {**validos["sintetico"], "marcador": {"id": MARCADOR, "instante": "2026-13-07T12:00:00Z"}},
            # El marcador vive en un esquema de `blog_migrate`: solo esa identidad lo lee.
            {**validos["verify"], "marcador": {"id": MARCADOR}},
            {**validos["verify"], "credencial": credencial("blog_migrate", MIGRA), "marcador": {"id": "x"}},
            # Las identidades se crean en la productiva; una restaurada ya las trae del snapshot.
            {**validos["identidades"], "destino": destino(RESTAURADA)},
            {"modo": "export"},
            {**validos["export"], "credencial": credencial()},
            {**validos["export"], "destino": destino(RESTAURADA)},
            {**validos["export"], "salida": {"bucket": BUCKET}},
            {**validos["export"], "salida": {"bucket": BUCKET, "marca": MARCA, "prefijo": "medios/"}},
            {**validos["export"], "salida": {"bucket": "Bucket_Invalido", "marca": MARCA}},
            {**validos["export"], "salida": {"bucket": "con.puntos.medios", "marca": MARCA}},
            {**validos["export"], "salida": {"bucket": BUCKET, "marca": "2026-10-07T12:00:00Z"}},
            {**validos["export"], "salida": {"bucket": BUCKET, "marca": "20261307T120000Z"}},
            {**validos["export"], "extra": True},
        ]
        for evento in invalidos:
            with self.subTest(evento=repr(evento)[:90]):
                r, simulador = self.invocar(evento)
                self.assertEqual(r, {"contrato": CONTRATO, "estado": "INVALID_PAYLOAD"})
                self.assertEqual(simulador.conexiones, [], "un payload invalido nunca abre conexion")

    def test_error_interno_sin_traza(self):
        with mock.patch.object(self.operaciones, "verify", side_effect=RuntimeError("detalle-interno")):
            r, _ = self.invocar({"modo": "verify", "destino": destino(), "credencial": credencial()})
        self.assertEqual(r, {"contrato": CONTRATO, "estado": "INTERNAL_ERROR", "modo": "verify"})


class ConexionVerifyFull(Base):
    def test_parametros_exactos_de_la_conexion(self):
        _, simulador = self.invocar({"modo": "verify", "destino": destino(), "credencial": credencial()})
        (conexion,) = simulador.conexiones
        self.assertEqual(conexion.parametros, {
            "host": HOST, "port": 5432, "dbname": "personal_blog", "user": "blogadmin", "password": MASTER,
            "sslmode": "verify-full", "sslrootcert": str(CODIGO / "rds-ca-us-east-2.pem"), "connect_timeout": 10,
            "application_name": "ejecutora-d24"})
        self.assertTrue(conexion.cerrada)
        self.assertEqual(conexion.commits, 0, "verify nunca confirma nada")

    def test_verify_informa_tls_y_la_identidad(self):
        r, simulador = self.invocar({"modo": "verify", "destino": destino(), "credencial": credencial()})
        self.assertEqual(r, {"contrato": CONTRATO, "estado": "OK", "modo": "verify",
                             "conexion": {"tls": True, "version_tls": "TLSv1.3", "cifrado": "TLS_AES_256_GCM_SHA384",
                                          "bits": 256, "sslmode": "verify-full"},
                             "servidor": {"version": "17.11", "base": "personal_blog", "rds_force_ssl": "1"},
                             "identidad": {"usuario": "blogadmin", "superusuario": False, "crea_roles": False,
                                           "crea_bases": False, "replicacion": False, "bypass_rls": False,
                                           "limite_de_conexiones": -1}})
        self.assertTrue(all(not sql.upper().startswith(("CREATE", "ALTER", "DROP", "INSERT", "UPDATE", "DELETE",
                                                        "GRANT", "REVOKE"))
                            for sql, _ in simulador.conexiones[0].sql))

    def test_sin_tls_activo_es_un_fallo(self):
        respuestas = respuestas_base()
        respuestas[1] = ("FROM pg_stat_ssl", (False, None, None, None))
        r, _ = self.invocar({"modo": "verify", "destino": destino(), "credencial": credencial()},
                            Simulador(respuestas))
        self.assertEqual(r["estado"], "TLS_NO_ACTIVO")

    def test_blog_app_no_puede_hacer_ddl(self):
        respuestas = respuestas_base("blog_app") + [
            ("CREATE TABLE", ErrorSimulado("permission denied for schema public", "42501"))]
        r, simulador = self.invocar({"modo": "verify", "destino": destino(),
                                     "credencial": credencial("blog_app", APP)}, Simulador(respuestas))
        self.assertEqual(r["estado"], "OK")
        self.assertTrue(r["ddl_rechazado"])
        self.assertGreaterEqual(simulador.conexiones[0].rollbacks, 1)

    def test_si_blog_app_pudiera_hacer_ddl_es_un_fallo_y_se_revierte(self):
        r, simulador = self.invocar({"modo": "verify", "destino": destino(),
                                     "credencial": credencial("blog_app", APP)},
                                    Simulador(respuestas_base("blog_app")))
        self.assertEqual(r["estado"], "DDL_PERMITIDO_A_BLOG_APP")
        self.assertEqual(simulador.conexiones[0].commits, 0)
        self.assertGreaterEqual(simulador.conexiones[0].rollbacks, 1)

    def test_identidad_de_aplicacion_con_atributos_excesivos_es_un_fallo(self):
        for indice, atributo in enumerate(("superusuario", "crea_roles", "crea_bases", "replicacion", "bypass_rls")):
            with self.subTest(atributo=atributo):
                respuestas = respuestas_base("blog_app")
                fila = [False] * 5 + [-1]
                fila[indice] = True
                respuestas[3] = ("FROM pg_roles WHERE rolname = current_user", tuple(fila))
                r, simulador = self.invocar({"modo": "verify", "destino": destino(),
                                             "credencial": credencial("blog_app", APP)}, Simulador(respuestas))
                self.assertEqual(r, {"contrato": CONTRATO, "estado": "PRIVILEGIOS_EXCESIVOS", "modo": "verify"})
                self.assertEqual(simulador.conexiones[0].commits, 0)

    def test_sesion_con_otra_identidad_o_base_es_un_fallo(self):
        for fila in (("17.11", "otro", "otro", "personal_blog"), ("17.11", "blogadmin", "blogadmin", "postgres")):
            with self.subTest(fila=fila):
                respuestas = respuestas_base()
                respuestas[0] = ("current_setting('server_version')", fila)
                r, _ = self.invocar({"modo": "verify", "destino": destino(), "credencial": credencial()},
                                    Simulador(respuestas))
                self.assertEqual(r, {"contrato": CONTRATO, "estado": "SESION_INESPERADA", "modo": "verify"})

    def test_controles_negativos_rechazados(self):
        r, simulador = self.invocar({"modo": "verify", "destino": destino(), "credencial": credencial(),
                                     "controles_negativos": True}, Simulador(fallos=fallos_negativos))
        self.assertEqual(r["estado"], "OK")
        self.assertEqual(r["controles_negativos"], {"sin_tls": "RECHAZADO_POR_EL_SERVIDOR",
                                                   "host_distinto": "RECHAZADO_POR_TLS",
                                                   "ca_ajena": "RECHAZADO_POR_TLS"})
        intentos = [c for c in simulador.conexiones]
        self.assertEqual(len(intentos), 1, "los controles negativos nunca llegan a conectar")

    def test_los_controles_negativos_nunca_usan_la_contrasena_real(self):
        vistos = []

        def registrar(parametros):
            vistos.append(dict(parametros))
            return fallos_negativos(parametros)

        self.invocar({"modo": "verify", "destino": destino(), "credencial": credencial(),
                      "controles_negativos": True}, Simulador(fallos=registrar))
        negativos = [p for p in vistos if p.get("sslmode") == "disable" or p.get("host", "").startswith("10.")
                     or p.get("sslrootcert") == "system"]
        self.assertEqual(len(negativos), 3)
        self.assertTrue(all(p["password"] != MASTER for p in negativos))

    def test_la_ca_ajena_usa_verify_full_contra_el_almacen_del_sistema(self):
        vistos = []

        def registrar(parametros):
            vistos.append(dict(parametros))
            return fallos_negativos(parametros)

        self.invocar({"modo": "verify", "destino": destino(), "credencial": credencial(),
                      "controles_negativos": True}, Simulador(fallos=registrar))
        (ajena,) = [p for p in vistos if p.get("sslrootcert") == "system"]
        self.assertEqual((ajena["host"], ajena["sslmode"]), (HOST, "verify-full"))

    def test_un_control_que_no_concluye_es_un_fallo(self):
        def fallos(parametros):
            if parametros.get("sslrootcert") == "system":
                return ErrorSimulado("connection timeout expired")
            return fallos_negativos(parametros)

        r, _ = self.invocar({"modo": "verify", "destino": destino(), "credencial": credencial(),
                             "controles_negativos": True}, Simulador(fallos=fallos))
        self.assertEqual(r["estado"], "CONTROL_NEGATIVO_NO_CONCLUYENTE")

    def test_un_control_negativo_aceptado_es_un_fallo(self):
        r, _ = self.invocar({"modo": "verify", "destino": destino(), "credencial": credencial(),
                             "controles_negativos": True}, Simulador())
        self.assertEqual(r["estado"], "CONTROL_NEGATIVO_ACEPTADO")

    def test_errores_de_conexion_solo_como_codigo(self):
        casos = (
            (ErrorSimulado('FATAL: password authentication failed for user "blogadmin"', "28P01"),
             "AUTENTICACION_FALLIDA"),
            (ErrorSimulado("SSL error: certificate verify failed"), "TLS_FALLIDO"),
            (ErrorSimulado("connection timeout expired"), "CONEXION_FALLIDA"),
        )
        for error, codigo in casos:
            with self.subTest(codigo=codigo):
                r, _ = self.invocar({"modo": "verify", "destino": destino(), "credencial": credencial()},
                                    Simulador(fallos=lambda p, e=error: e))
                self.assertEqual(r, {"contrato": CONTRATO, "estado": codigo, "modo": "verify"})

    def test_verify_lee_el_marcador_de_una_restaurada(self):
        respuestas = respuestas_base("blog_migrate") + [
            ("FROM verificacion.marcador", ("2026-10-07T12:00:00+00:00", "a" * 64))]
        r, simulador = self.invocar({"modo": "verify", "destino": destino(RESTAURADA),
                                     "credencial": credencial("blog_migrate", MIGRA),
                                     "marcador": {"id": MARCADOR}}, Simulador(respuestas))
        self.assertEqual(r["marcador"], {"presente": True, "huella": "a" * 64})
        self.assertIn(("SELECT instante, encode(sha256(convert_to(id::text || '|' || extract(epoch FROM instante)::text || '|' || "
                       "contenido, 'UTF8')), 'hex') FROM verificacion.marcador WHERE id = %s", (MARCADOR,)),
                      simulador.conexiones[0].sql)


class Identidades(Base):
    def evento(self):
        return {"modo": "identidades", "destino": destino(), "credencial": credencial(),
                "verificadores": {"blog_migrate": VERIF_M, "blog_app": VERIF_A}}

    def respuestas(self, existentes=()):
        lectura = lambda sql, p: [(True,)] if p and p[0] in existentes else []  # noqa: E731
        return respuestas_base() + [
            ("SELECT 1 FROM pg_roles WHERE rolname = %s", lectura),
            ("FROM pg_roles WHERE rolname IN", [
                ("blog_app", True, False, False, False, False, False, False, 89),
                ("blog_migrate", True, False, False, False, False, False, False, 5)]),
            ("has_database_privilege", [(True, True, False, False)]),
            # Orden: blog_migrate USAGE, blog_migrate CREATE, blog_app USAGE, blog_app CREATE, PUBLIC CREATE.
            ("has_schema_privilege", [(True, True, True, False, False)]),
            ("FROM pg_default_acl", [("blog_app=arwd/blog_migrate",)]),
        ]

    def test_crea_los_roles_solo_con_verificadores_scram(self):
        r, simulador = self.invocar(self.evento(), Simulador(self.respuestas()))
        sql = [s for s, _ in simulador.conexiones[0].sql]
        crear = [s for s in sql if s.startswith(("CREATE ROLE", "ALTER ROLE"))]
        self.assertEqual(crear, [
            "CREATE ROLE blog_migrate WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION "
            f"NOBYPASSRLS CONNECTION LIMIT 5 PASSWORD '{VERIF_M}'",
            "CREATE ROLE blog_app WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION "
            f"NOBYPASSRLS CONNECTION LIMIT 89 PASSWORD '{VERIF_A}'",
        ])
        for secreto in (MASTER, MIGRA, APP):
            self.assertFalse(any(secreto in s for s in sql), "ninguna contrasena en texto plano llega al SQL")
        self.assertEqual(r["estado"], "OK")

    def test_privilegios_minimos_de_d23(self):
        # Orden exacto, demostrado contra PostgreSQL 17.11 con un CREATEROLE no superusuario (integracion local):
        # ALTER DEFAULT PRIVILEGES FOR ROLE exige los privilegios de blog_migrate y CREATE SCHEMA AUTHORIZATION exige
        # poder hacer SET ROLE. Se obtiene con una membresia SET sin herencia, TRANSITORIA: se revoca en la misma
        # transaccion y no queda privilegio permanente nuevo.
        _, simulador = self.invocar(self.evento(), Simulador(self.respuestas()))
        sql = [s for s, _ in simulador.conexiones[0].sql if not s.startswith("SELECT")]
        self.assertEqual(sql[2:], [
            "REVOKE CONNECT, TEMPORARY ON DATABASE personal_blog FROM PUBLIC",
            "GRANT CONNECT ON DATABASE personal_blog TO blog_migrate, blog_app",
            "REVOKE CREATE ON SCHEMA public FROM PUBLIC",
            "GRANT USAGE, CREATE ON SCHEMA public TO blog_migrate",
            "GRANT USAGE ON SCHEMA public TO blog_app",
            "GRANT blog_migrate TO CURRENT_USER WITH INHERIT FALSE, SET TRUE",
            "SET ROLE blog_migrate",
            "ALTER DEFAULT PRIVILEGES FOR ROLE blog_migrate IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE "
            "ON TABLES TO blog_app",
            "RESET ROLE",
            "CREATE SCHEMA IF NOT EXISTS verificacion AUTHORIZATION blog_migrate",
            "REVOKE blog_migrate FROM CURRENT_USER",
        ])
        prohibidos = ("SUPERUSER", "CREATEDB ", "CREATEROLE ", "REPLICATION ", "BYPASSRLS ", "GRANT ALL",
                      "rds_superuser", "TO PUBLIC")
        for s in sql:
            for p in prohibidos:
                self.assertNotIn(f" {p}", f" {s.replace('NOSUPERUSER', '').replace('NOCREATEDB', '').replace('NOCREATEROLE', '').replace('NOREPLICATION', '').replace('NOBYPASSRLS', '')}")
        self.assertEqual(simulador.conexiones[0].commits, 1)

    def test_roles_existentes_se_ajustan_sin_recrearse(self):
        # Un no superusuario NO puede nombrar SUPERUSER, REPLICATION ni BYPASSRLS en ALTER ROLE ("Only roles with the
        # SUPERUSER attribute may change the SUPERUSER attribute", PostgreSQL 17.11): el ajuste los omite y la
        # relectura exige que sigan en false. Un CREATEROLE no superusuario no pudo concederlos nunca.
        _, simulador = self.invocar(self.evento(), Simulador(self.respuestas(existentes=("blog_migrate", "blog_app"))))
        sql = [s for s, _ in simulador.conexiones[0].sql]
        self.assertFalse(any(s.startswith("CREATE ROLE") for s in sql))
        self.assertEqual([s for s in sql if s.startswith("ALTER ROLE")], [
            f"ALTER ROLE blog_migrate WITH LOGIN NOCREATEDB NOCREATEROLE NOINHERIT CONNECTION LIMIT 5 PASSWORD '{VERIF_M}'",
            f"ALTER ROLE blog_app WITH LOGIN NOCREATEDB NOCREATEROLE NOINHERIT CONNECTION LIMIT 89 PASSWORD '{VERIF_A}'",
        ])

    def test_readback_saneado(self):
        r, _ = self.invocar(self.evento(), Simulador(self.respuestas()))
        self.assertEqual(r["roles"], {
            "blog_app": {"login": True, "superusuario": False, "crea_roles": False, "crea_bases": False,
                         "replicacion": False, "bypass_rls": False, "hereda": False, "limite_de_conexiones": 89},
            "blog_migrate": {"login": True, "superusuario": False, "crea_roles": False, "crea_bases": False,
                             "replicacion": False, "bypass_rls": False, "hereda": False, "limite_de_conexiones": 5}})
        self.assertEqual(r["privilegios"], {
            "connect": {"blog_migrate": True, "blog_app": True, "public": False},
            "temporary_public": False,
            "esquema_public": {"blog_migrate_usage": True, "blog_migrate_create": True, "blog_app_usage": True,
                               "blog_app_create": False, "public_create": False},
            "por_omision_tablas_blog_app": "arwd"})

    def test_un_fallo_revierte_todo(self):
        respuestas = self.respuestas() + [("GRANT USAGE ON SCHEMA public TO blog_app",
                                           ErrorSimulado("permission denied", "42501"))]
        r, simulador = self.invocar(self.evento(), Simulador(respuestas))
        self.assertEqual(r["estado"], "PERMISO_DENEGADO")
        self.assertEqual(simulador.conexiones[0].commits, 0)
        self.assertGreaterEqual(simulador.conexiones[0].rollbacks, 1)


    def test_readback_no_conforme_revierte_y_falla(self):
        respuestas = self.respuestas()
        respuestas[-1] = ("FROM pg_default_acl", [("blog_app=arwdDxt/blog_migrate",)])
        r, simulador = self.invocar(self.evento(), Simulador(respuestas))
        self.assertEqual(r["estado"], "IDENTIDADES_NO_CONFORMES")
        self.assertEqual(r["privilegios"]["por_omision_tablas_blog_app"], "arwdDxt")
        self.assertEqual(simulador.conexiones[0].commits, 0)
        self.assertGreaterEqual(simulador.conexiones[0].rollbacks, 1)


class Sintetico(Base):
    def evento(self, accion="sembrar"):
        return {"modo": "sintetico", "destino": destino(), "credencial": credencial("blog_migrate", MIGRA),
                "marcador": {"id": MARCADOR, "instante": "2026-10-07T12:00:00Z"}, "accion": accion}

    def test_sembrar_marcador_no_sensible(self):
        respuestas = respuestas_base("blog_migrate") + [("FROM verificacion.marcador", ("2026-10-07T12:00:00+00:00",
                                                                                         "b" * 64))]
        r, simulador = self.invocar(self.evento(), Simulador(respuestas))
        sql = simulador.conexiones[0].sql
        self.assertIn(("CREATE TABLE IF NOT EXISTS verificacion.marcador (id uuid PRIMARY KEY, instante timestamptz "
                       "NOT NULL, contenido text NOT NULL)", None), sql)
        self.assertIn(("INSERT INTO verificacion.marcador (id, instante, contenido) VALUES (%s, %s, %s) ON CONFLICT "
                       "(id) DO NOTHING", (MARCADOR, "2026-10-07T12:00:00Z", f"Task/031 H-031-7 marcador sintetico {MARCADOR}")),
                      sql)
        self.assertEqual(simulador.conexiones[0].commits, 1)
        self.assertEqual(r, {"contrato": CONTRATO, "estado": "OK", "modo": "sintetico", "accion": "sembrar",
                             "marcador": {"presente": True, "huella": "b" * 64}})

    def test_limpiar_borra_solo_ese_marcador(self):
        _, simulador = self.invocar(self.evento("limpiar"), Simulador(respuestas_base("blog_migrate")))
        borrados = [s for s in simulador.conexiones[0].sql if s[0].startswith("DELETE")]
        self.assertEqual(borrados, [("DELETE FROM verificacion.marcador WHERE id = %s", (MARCADOR,))])

    def test_solo_contra_la_productiva(self):
        evento = self.evento()
        evento["destino"] = destino(RESTAURADA)
        r, simulador = self.invocar(evento)
        self.assertEqual(r, {"contrato": CONTRATO, "estado": "INVALID_PAYLOAD"})
        self.assertEqual(simulador.conexiones, [])


ESCRITURAS = ("CREATE ROLE", "ALTER ROLE", "GRANT", "REVOKE", "CREATE TABLE", "CREATE SCHEMA", "INSERT", "DELETE")


def escrituras(conexion):
    return [s for s, _ in conexion.sql if s.startswith(ESCRITURAS)]


class ExclusionMutua(Base):
    """D-24 modificada el 2026-10-18 (aprobada el 2026-10-19): sin concurrencia reservada en Lambda, las operaciones que ESCRIBEN
    se excluyen con un advisory lock de TRANSACCION en la misma conexion. Ocupado: rechazo inmediato, sin escribir y
    sin reintentar. Los modos de solo lectura no lo toman."""

    def identidades(self):
        return Identidades.evento(self), Identidades.respuestas(self)

    def sintetico(self):
        evento = Sintetico.evento(self)
        return evento, respuestas_base("blog_migrate") + [
            ("FROM verificacion.marcador", ("2026-10-07T12:00:00+00:00", "b" * 64))]

    def test_las_escrituras_toman_el_lock_en_la_misma_conexion_antes_de_escribir(self):
        for nombre in ("identidades", "sintetico"):
            with self.subTest(modo=nombre):
                evento, respuestas = getattr(self, nombre)()
                r, simulador = self.invocar(evento, Simulador(respuestas))
                self.assertEqual(r["estado"], "OK")
                self.assertEqual(len(simulador.conexiones), 1, "una sola conexion: el lock vive en ella")
                sql = simulador.conexiones[0].sql
                orden = [s for s, _ in sql]
                lock = next(i for i, s in enumerate(orden) if "pg_try_advisory_xact_lock" in s)
                primera_escritura = next(i for i, s in enumerate(orden) if s.startswith(ESCRITURAS))
                self.assertLess(lock, primera_escritura)
                self.assertEqual(sql[lock], ("SELECT pg_try_advisory_xact_lock(%s, %s)", (3364, 1)))
                limites = [p for s, p in sql[:lock] if s == "SELECT set_config(%s, %s, true)"]
                self.assertEqual(limites, [("statement_timeout", "20s"),
                                           ("idle_in_transaction_session_timeout", "60s")])
                self.assertEqual(simulador.conexiones[0].commits, 1)
                self.assertTrue(simulador.conexiones[0].cerrada)

    def test_ocupado_se_rechaza_sin_escribir_ni_reintentar(self):
        for nombre in ("identidades", "sintetico"):
            with self.subTest(modo=nombre):
                evento, respuestas = getattr(self, nombre)()
                respuestas = [(p, (False,) if p == "pg_try_advisory_xact_lock" else r) for p, r in respuestas]
                r, simulador = self.invocar(evento, Simulador(respuestas))
                self.assertEqual(r, {"contrato": CONTRATO, "estado": "OPERACION_EN_CURSO", "modo": nombre})
                self.assertEqual(len(simulador.conexiones), 1, "ningun reintento")
                conexion = simulador.conexiones[0]
                self.assertEqual(escrituras(conexion), [])
                self.assertEqual(conexion.commits, 0)
                self.assertGreaterEqual(conexion.rollbacks, 1)
                self.assertTrue(conexion.cerrada)

    def test_un_error_tras_el_lock_revierte_y_no_reejecuta(self):
        evento, respuestas = self.identidades()
        respuestas.append(("GRANT USAGE ON SCHEMA public TO blog_app", ErrorSimulado("permission denied", "42501")))
        r, simulador = self.invocar(evento, Simulador(respuestas))
        self.assertEqual(r["estado"], "PERMISO_DENEGADO")
        self.assertEqual(len(simulador.conexiones), 1)
        conexion = simulador.conexiones[0]
        self.assertEqual(sum(s.startswith("CREATE ROLE blog_migrate") for s in escrituras(conexion)), 1)
        self.assertEqual(conexion.commits, 0)
        self.assertGreaterEqual(conexion.rollbacks, 1)

    def test_los_modos_de_lectura_no_toman_el_lock(self):
        casos = (
            ({"modo": "verify", "destino": destino(), "credencial": credencial()}, Simulador()),
            ({"modo": "verify", "destino": destino(), "credencial": credencial("blog_app", APP)},
             Simulador(respuestas_base("blog_app") + [("CREATE TABLE public.sonda_ddl_h0316",
                                                       ErrorSimulado("permission denied", "42501"))])),
            ({"modo": "export", "destino": destino(), "credencial": credencial("blog_migrate", MIGRA),
              "bucket": BUCKET, "marca": MARCA}, Simulador(respuestas_export())),
        )
        for evento, simulador in casos:
            with self.subTest(modo=evento["modo"], usuario=evento["credencial"]["usuario"]):
                _, simulador = self.invocar(evento, simulador, s3=S3Simulado())
                for conexion in simulador.conexiones:
                    self.assertFalse(any("advisory" in s for s, _ in conexion.sql))

    def test_lock_de_transaccion_sin_desbloqueo_manual(self):
        fuente = (CODIGO / "operaciones.py").read_text(encoding="utf-8")
        self.assertIn("pg_try_advisory_xact_lock", fuente)
        for prohibido in ("pg_advisory_lock(", "pg_try_advisory_lock(", "pg_advisory_unlock", "pg_advisory_xact_lock("):
            self.assertNotIn(prohibido, fuente, "solo el lock de transaccion que no espera")


def respuestas_export(tablas=(("public", "administradores"), ("public", "publicaciones"))):
    return respuestas_base("blog_migrate") + [
        ("FROM pg_tables", list(tablas)),
        ('SELECT count(*) FROM public."administradores"', (1,)),
        ('SELECT count(*) FROM public."publicaciones"', (2,)),
    ]


COPIAS = (
    ('COPY public."administradores" TO STDOUT', [b"id,correo\n", b"1,admin@ejemplo.invalid\n"]),
    ('COPY public."publicaciones" TO STDOUT', [b"id,titulo\n1,Uno\n2,Dos\n"]),
)


class Export(Base):
    def evento(self):
        return {"modo": "export", "destino": destino(), "credencial": credencial("blog_migrate", MIGRA),
                "salida": {"bucket": BUCKET, "marca": MARCA}}

    def test_vuelca_public_en_una_instantanea_de_solo_lectura(self):
        _, simulador = self.invocar(self.evento(), Simulador(respuestas_export(), copias=COPIAS), s3=S3Simulado())
        (conexion,) = simulador.conexiones
        sql = [s for s, _ in conexion.sql]
        inicio = sql.index("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
        self.assertEqual(sql[inicio:], [
            "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY",
            "SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename",
            'SELECT count(*) FROM public."administradores"',
            'COPY public."administradores" TO STDOUT WITH (FORMAT csv, HEADER true)',
            'SELECT count(*) FROM public."publicaciones"',
            'COPY public."publicaciones" TO STDOUT WITH (FORMAT csv, HEADER true)',
        ])
        self.assertEqual(conexion.commits, 0, "export nunca confirma nada")
        self.assertGreaterEqual(conexion.rollbacks, 2)
        self.assertTrue(conexion.cerrada)

    def test_escribe_csv_y_manifiesto_condicionales_y_con_sha256(self):
        s3 = S3Simulado()
        r, _ = self.invocar(self.evento(), Simulador(respuestas_export(), copias=COPIAS), s3=s3)
        base = f"exportaciones/{MARCA}/"
        cuerpos = {"public.administradores": b"id,correo\n1,admin@ejemplo.invalid\n",
                   "public.publicaciones": b"id,titulo\n1,Uno\n2,Dos\n"}
        self.assertEqual([o["Key"] for o in s3.objetos], [f"{base}public.administradores.csv",
                                                          f"{base}public.publicaciones.csv", f"{base}manifiesto.json"])
        for objeto in s3.objetos:
            with self.subTest(clave=objeto["Key"]):
                self.assertEqual(objeto["Bucket"], BUCKET)
                self.assertEqual(objeto["IfNoneMatch"], "*", "una exportacion nunca pisa otra")
                self.assertEqual(objeto["ChecksumSHA256"],
                                 base64.b64encode(hashlib.sha256(objeto["Body"]).digest()).decode())
                self.assertEqual(set(objeto), {"Bucket", "Key", "Body", "ContentType", "ChecksumSHA256", "IfNoneMatch"})
        self.assertEqual(s3.objetos[0]["Body"], cuerpos["public.administradores"])
        self.assertEqual(s3.objetos[0]["ContentType"], "text/csv; charset=utf-8")
        manifiesto = json.loads(s3.objetos[2]["Body"])
        self.assertEqual(s3.objetos[2]["ContentType"], "application/json")
        self.assertEqual(manifiesto, {
            "formato": "d24-export-v1", "marca": MARCA, "csv": "COPY ... TO STDOUT WITH (FORMAT csv, HEADER true)",
            "tablas": [{"tabla": tabla, "objeto": f"{base}{tabla}.csv", "filas": filas, "bytes": len(cuerpos[tabla]),
                        "sha256": hashlib.sha256(cuerpos[tabla]).hexdigest()}
                       for tabla, filas in (("public.administradores", 1), ("public.publicaciones", 2))]})
        self.assertEqual(r, {"contrato": CONTRATO, "estado": "OK", "modo": "export", "exportacion": {
            "prefijo": base, "manifiesto": f"{base}manifiesto.json",
            "tablas": {"public.administradores": 1, "public.publicaciones": 2},
            "bytes": sum(len(c) for c in cuerpos.values())}})

    def test_sin_tablas_solo_escribe_el_manifiesto(self):
        s3 = S3Simulado()
        r, _ = self.invocar(self.evento(), Simulador(respuestas_export(tablas=())), s3=s3)
        self.assertEqual([o["Key"] for o in s3.objetos], [f"exportaciones/{MARCA}/manifiesto.json"])
        self.assertEqual(json.loads(s3.objetos[0]["Body"])["tablas"], [])
        self.assertEqual(r["exportacion"]["tablas"], {})

    def test_la_respuesta_nunca_lleva_datos_ni_el_bucket(self):
        r, _ = self.invocar(self.evento(), Simulador(respuestas_export(), copias=COPIAS), s3=S3Simulado())
        texto = json.dumps(r)
        for prohibido in ("admin@ejemplo.invalid", "Uno", BUCKET):
            self.assertNotIn(prohibido, texto)

    def test_demasiado_grande_se_detiene_sin_escribir(self):
        s3 = S3Simulado()
        with mock.patch.object(self.exportacion, "LIMITE_DE_BYTES", 20):
            r, simulador = self.invocar(self.evento(), Simulador(respuestas_export(), copias=COPIAS), s3=s3)
        self.assertEqual(r, {"contrato": CONTRATO, "estado": "EXPORTACION_DEMASIADO_GRANDE", "modo": "export"})
        self.assertEqual(s3.objetos, [])
        self.assertEqual(simulador.conexiones[0].commits, 0)

    def test_tabla_con_nombre_fuera_del_patron(self):
        r, _ = self.invocar(self.evento(), Simulador(respuestas_export(tablas=(("public", 'raro"nombre'),))),
                            s3=S3Simulado())
        self.assertEqual(r, {"contrato": CONTRATO, "estado": "TABLA_NO_ADMITIDA", "modo": "export"})

    def test_fallos_de_s3_solo_como_codigo(self):
        for fallo, codigo in ((ErrorDeCliente("PreconditionFailed"), "EXPORTACION_YA_EXISTE"),
                              (ErrorDeCliente("AccessDenied"), "S3_ACCESO_DENEGADO"),
                              (ErrorDeCliente("InternalError"), "S3_FALLIDO"),
                              (EndpointConnectionError("Could not connect to the endpoint URL"), "S3_SIN_CONEXION")):
            with self.subTest(codigo=codigo):
                r, _ = self.invocar(self.evento(), Simulador(respuestas_export(), copias=COPIAS),
                                    s3=S3Simulado(fallo))
                self.assertEqual(r, {"contrato": CONTRATO, "estado": codigo, "modo": "export"})

    def test_un_error_que_no_es_de_s3_es_interno(self):
        r, _ = self.invocar(self.evento(), Simulador(respuestas_export(), copias=COPIAS),
                            s3=S3Simulado(KeyError("detalle")))
        self.assertEqual(r, {"contrato": CONTRATO, "estado": "INTERNAL_ERROR", "modo": "export"})

    def test_permiso_denegado_en_la_base(self):
        respuestas = respuestas_base("blog_migrate") + [("FROM pg_tables", ErrorSimulado("permission denied", "42501"))]
        r, _ = self.invocar(self.evento(), Simulador(respuestas), s3=S3Simulado())
        self.assertEqual(r, {"contrato": CONTRATO, "estado": "PERMISO_DENEGADO", "modo": "export"})


class FuenteDeLaExportacion(unittest.TestCase):
    def setUp(self):
        self.texto = (CODIGO / "exportacion.py").read_text(encoding="utf-8")

    def test_solo_importa_lo_necesario(self):
        importados = set()
        for nodo in ast.walk(ast.parse(self.texto)):
            if isinstance(nodo, ast.Import):
                importados |= {a.name for a in nodo.names}
            elif isinstance(nodo, ast.ImportFrom):
                importados.add(nodo.module)
        self.assertEqual(importados, {"base64", "hashlib", "json", "re", "operaciones", "boto3", "botocore.config"})

    def test_solo_s3_y_solo_put_object(self):
        texto = self.texto.lower()
        self.assertEqual(re.findall(r'client\(\s*"([a-z0-9-]+)"', self.texto), ["s3"])
        self.assertIn("put_object(", texto)
        for prohibido in ("ssm", "kms", "environ", "getenv", "subprocess", "secretsmanager", "eval(", "exec(", "open(",
                          "database_url", "get_object", "delete_object", "list_objects", "copy_object", "head_object",
                          "upload_file", "download", "resource(", "assume_role"):
            with self.subTest(prohibido=prohibido):
                self.assertNotIn(prohibido, texto)

    def test_prefijo_dedicado_fuera_de_medios(self):
        self.assertIn('PREFIJO = "exportaciones/"', self.texto)

    def test_mismo_prefijo_que_la_politica_iam_del_modulo(self):
        # El codigo escribe donde la politica de terraform/modulos/exportacion permite escribir, y en ningun otro sitio.
        modulo = (RAIZ / "terraform" / "modulos" / "exportacion" / "main.tf").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r'prefijo = "([^"]+)"', modulo), ["exportaciones/"])
        self.assertEqual(re.findall(r'PREFIJO = "([^"]+)"', self.texto), ["exportaciones/"])


class FuenteSinSecretosNiServicios(unittest.TestCase):
    def test_solo_importa_lo_necesario(self):
        importados = set()
        for archivo in ("ejecutor.py", "operaciones.py"):
            for nodo in ast.walk(ast.parse((CODIGO / archivo).read_text(encoding="utf-8"))):
                if isinstance(nodo, ast.Import):
                    importados |= {a.name for a in nodo.names}
                elif isinstance(nodo, ast.ImportFrom):
                    importados.add(nodo.module)
        self.assertEqual(importados, {"json", "sys", "re", "socket", "pathlib", "operaciones", "exportacion",
                                      "psycopg"})

    def test_sin_referencias_a_ssm_kms_entorno_ni_procesos(self):
        for archivo in ("ejecutor.py", "operaciones.py"):
            texto = (CODIGO / archivo).read_text(encoding="utf-8").lower()
            for palabra in ("boto", "ssm", "kms", "environ", "getenv", "subprocess", "database_url", "secretsmanager",
                            "eval(", "exec(", "open("):
                with self.subTest(archivo=archivo, palabra=palabra):
                    self.assertNotIn(palabra, texto)

    def test_bundle_de_la_ca_empaquetado_y_fijado(self):
        import hashlib

        ca = CODIGO / "rds-ca-us-east-2.pem"
        self.assertEqual(hashlib.sha256(ca.read_bytes()).hexdigest(),
                         "d46e1bdfda05c8e7644e50930806a19b139a222542bf0348082fb59ece2b5fa5")
        self.assertEqual(ca.read_bytes().count(b"-----BEGIN CERTIFICATE-----"), 3)


if __name__ == "__main__":
    unittest.main()
