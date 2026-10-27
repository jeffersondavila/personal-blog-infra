"""Operaciones de la ejecutora de D-24 contra PostgreSQL (Task/031 H-031-6).

Cada operacion abre UNA conexion `verify-full` contra el bundle regional de RDS empaquetado junto a este archivo,
ejecuta sentencias fijas y devuelve solo campos saneados. Lo variable viaja como parametro; en las sentencias DDL,
que no admiten parametros, solo entran literales que la ejecutora ya valido contra un patron cerrado.

Un fallo esperado es `Fallo(codigo)`: nunca lleva el mensaje del servidor ni el de libpq, que pueden repetir el host,
el usuario o la sentencia. Una excepcion que no viene de la base de datos sigue su curso y la ejecutora la convierte
en `INTERNAL_ERROR`.
"""

import socket
from pathlib import Path

PUERTO = 5432
BASE = "personal_blog"
CA = Path(__file__).with_name("rds-ca-us-east-2.pem")
APLICACION = "ejecutora-d24"
ESPERA_DE_CONEXION = 10

# Contrasena de los controles negativos: no cumple la politica de contrasenas, asi que nunca es una real.
SIN_CREDENCIAL = "control-negativo-sin-credencial"

# D-12 §6.2: 5 conexiones para migraciones y 89 para la aplicacion.
LIMITES = {"blog_migrate": 5, "blog_app": 89}

# D-23 §5.3: `blog_migrate` hace DDL en `public`; `blog_app` solo DML sobre las tablas que `blog_migrate` cree.
#
# En PostgreSQL 16+ un CREATEROLE no superusuario recibe ADMIN sobre los roles que crea, pero no sus privilegios ni
# SET ROLE: `ALTER DEFAULT PRIVILEGES FOR ROLE` exige los privilegios del rol y `CREATE SCHEMA ... AUTHORIZATION`
# exige poder hacer SET ROLE (demostrado contra 17.11 en la integracion local de H-031-6). Se resuelve con una
# membresia SET sin herencia que se concede y se REVOCA dentro de la misma transaccion: no queda privilegio nuevo.
PRIVILEGIOS = (
    "REVOKE CONNECT, TEMPORARY ON DATABASE personal_blog FROM PUBLIC",
    "GRANT CONNECT ON DATABASE personal_blog TO blog_migrate, blog_app",
    "REVOKE CREATE ON SCHEMA public FROM PUBLIC",
    "GRANT USAGE, CREATE ON SCHEMA public TO blog_migrate",
    "GRANT USAGE ON SCHEMA public TO blog_app",
    "GRANT blog_migrate TO CURRENT_USER WITH INHERIT FALSE, SET TRUE",
    "SET ROLE blog_migrate",
    "ALTER DEFAULT PRIVILEGES FOR ROLE blog_migrate IN SCHEMA public "
    "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO blog_app",
    "RESET ROLE",
    "CREATE SCHEMA IF NOT EXISTS verificacion AUTHORIZATION blog_migrate",
    "REVOKE blog_migrate FROM CURRENT_USER",
)

# Un no superusuario no puede NOMBRAR SUPERUSER, REPLICATION ni BYPASSRLS en ALTER ROLE, aunque sea para negarlos:
# el ajuste de un rol existente los omite y la relectura exige que sigan en false.
ATRIBUTOS_AL_CREAR = "LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS"
ATRIBUTOS_AL_AJUSTAR = "LOGIN NOCREATEDB NOCREATEROLE NOINHERIT"

ATRIBUTOS = ("login", "superusuario", "crea_roles", "crea_bases", "replicacion", "bypass_rls", "hereda",
             "limite_de_conexiones")
ESPERADO = {
    "roles": {
        rol: {"login": True, "superusuario": False, "crea_roles": False, "crea_bases": False, "replicacion": False,
              "bypass_rls": False, "hereda": False, "limite_de_conexiones": LIMITES[rol]}
        for rol in ("blog_app", "blog_migrate")
    },
    "privilegios": {
        "connect": {"blog_migrate": True, "blog_app": True, "public": False},
        "temporary_public": False,
        "esquema_public": {"blog_migrate_usage": True, "blog_migrate_create": True, "blog_app_usage": True,
                           "blog_app_create": False, "public_create": False},
        "por_omision_tablas_blog_app": "arwd",
    },
}

CREAR_MARCADOR = ("CREATE TABLE IF NOT EXISTS verificacion.marcador "
                  "(id uuid PRIMARY KEY, instante timestamptz NOT NULL, contenido text NOT NULL)")
INSERTAR_MARCADOR = ("INSERT INTO verificacion.marcador (id, instante, contenido) VALUES (%s, %s, %s) "
                     "ON CONFLICT (id) DO NOTHING")
# Huella independiente de la zona horaria de la sesion: el instante entra como epoch.
HUELLA_DEL_MARCADOR = ("SELECT instante, encode(sha256(convert_to(id::text || '|' || "
                       "extract(epoch FROM instante)::text || '|' || contenido, 'UTF8')), 'hex') "
                       "FROM verificacion.marcador WHERE id = %s")

# D-24, modificada el 2026-10-18 (Propuesta — pendiente de aprobacion): la ejecutora usa la concurrencia NO
# reservada de Lambda, asi que dos invocaciones pueden coincidir. Las operaciones que ESCRIBEN se excluyen entre si
# con un advisory lock de PostgreSQL de TRANSACCION, que se toma en la misma conexion antes de la primera escritura.
# Se libera solo con el commit, el rollback o el fin de la sesion. Si esta ocupado, se rechaza al instante: nunca se
# espera ni se reintenta. Los modos de solo lectura (`verify` y `export`) no lo toman. No protege nada fuera de
# PostgreSQL: el restore y la limpieza de H-031-7 conservan sus propias guardas.
CLAVE_DE_ADMINISTRACION = (3364, 1)  # 3364 = 0x0D24, por D-24; 1, la clase de escrituras administrativas
# Limites de la transaccion protegida, por debajo del timeout de la funcion (30 s). Si el cliente desaparece a mitad
# de la transaccion, el servidor cierra la sesion y el lock se libera.
LIMITES_DE_LA_TRANSACCION = (("statement_timeout", "20s"), ("idle_in_transaction_session_timeout", "60s"))

CODIGOS_SQL = {"28P01": "AUTENTICACION_FALLIDA", "28000": "ACCESO_RECHAZADO", "42501": "PERMISO_DENEGADO",
               "53300": "SIN_CONEXIONES_DISPONIBLES"}


class Fallo(Exception):
    """Fallo esperado: un codigo cerrado y, como mucho, campos saneados."""

    def __init__(self, codigo, **detalle):
        super().__init__(codigo)
        self.codigo, self.detalle = codigo, detalle


def _conectar(**parametros):
    import psycopg  # diferido: las pruebas unitarias sustituyen CONECTAR y no necesitan el paquete

    return psycopg.connect(**parametros)


def _resolver(host):
    """Primera direccion IPv4 del host: el destino del control negativo de nombre."""
    for familia, _, _, _, direccion in socket.getaddrinfo(host, PUERTO, type=socket.SOCK_STREAM):
        if familia == socket.AF_INET:
            return direccion[0]
    raise OSError("sin direccion IPv4")


CONECTAR = _conectar
RESOLVER = _resolver


def _de_la_base(error):
    """Las excepciones de psycopg llevan `sqlstate`, aunque valga None en los fallos de conexion."""
    return hasattr(error, "sqlstate")


def _codigo(error):
    if error.sqlstate in CODIGOS_SQL:
        return CODIGOS_SQL[error.sqlstate]
    mensaje = str(error).lower()
    if "password authentication failed" in mensaje:
        return "AUTENTICACION_FALLIDA"
    if "no pg_hba.conf entry" in mensaje:
        return "ACCESO_RECHAZADO"
    if "certificate" in mensaje or "ssl" in mensaje:
        return "TLS_FALLIDO"
    if "timeout" in mensaje or "could not" in mensaje or "connection" in mensaje:
        return "CONEXION_FALLIDA"
    return "ERROR_DE_BASE_DE_DATOS"


def _parametros(host, usuario, contrasena, sslmode="verify-full"):
    parametros = {"host": host, "port": PUERTO, "dbname": BASE, "user": usuario, "password": contrasena,
                  "sslmode": sslmode, "connect_timeout": ESPERA_DE_CONEXION, "application_name": APLICACION}
    if sslmode == "verify-full":
        parametros["sslrootcert"] = str(CA)
    return parametros


def _revertir(conexion):
    try:
        conexion.rollback()
    except Exception as error:
        if not _de_la_base(error):
            raise
        # Conexion rota: el servidor revierte la transaccion al perder la sesion.


def _operar(pedido, usuario, trabajo):
    """Abre la conexion `verify-full`, comprueba la sesion y ejecuta `trabajo`; nada queda a medias."""
    credencial = pedido["credencial"]
    try:
        conexion = CONECTAR(**_parametros(pedido["destino"]["host"], usuario, credencial["contrasena"]))
    except Exception as error:
        if not _de_la_base(error):
            raise
        raise Fallo(_codigo(error)) from None
    try:
        with conexion.cursor() as cursor:
            sesion = _sesion(cursor, usuario)
            return trabajo(conexion, cursor, sesion)
    except Fallo:
        _revertir(conexion)
        raise
    except Exception as error:
        _revertir(conexion)
        if not _de_la_base(error):
            raise
        raise Fallo(_codigo(error)) from None
    finally:
        conexion.close()


def _sesion(cursor, usuario):
    """TLS, servidor e identidad de la sesion. Falla si no hay TLS o si no es la identidad y la base pedidas."""
    cursor.execute("SELECT current_setting('server_version'), current_user, session_user, current_database()")
    version, actual, de_sesion, base = cursor.fetchone()
    cursor.execute("SELECT ssl, version, cipher, bits FROM pg_stat_ssl WHERE pid = pg_backend_pid()")
    tls, version_tls, cifrado, bits = cursor.fetchone() or (False, None, None, None)
    if tls is not True:
        raise Fallo("TLS_NO_ACTIVO")
    if actual != usuario or de_sesion != usuario or base != BASE:
        raise Fallo("SESION_INESPERADA")
    cursor.execute("SELECT current_setting('rds.force_ssl', true)")
    (forzado,) = cursor.fetchone()
    cursor.execute("SELECT rolsuper, rolcreaterole, rolcreatedb, rolreplication, rolbypassrls, rolconnlimit "
                   "FROM pg_roles WHERE rolname = current_user")
    superusuario, crea_roles, crea_bases, replicacion, bypass_rls, limite = cursor.fetchone()
    if usuario != "blogadmin" and any((superusuario, crea_roles, crea_bases, replicacion, bypass_rls)):
        raise Fallo("PRIVILEGIOS_EXCESIVOS")
    return {
        "conexion": {"tls": True, "version_tls": version_tls, "cifrado": cifrado, "bits": bits,
                     "sslmode": "verify-full"},
        "servidor": {"version": version, "base": base, "rds_force_ssl": forzado},
        "identidad": {"usuario": usuario, "superusuario": superusuario, "crea_roles": crea_roles,
                      "crea_bases": crea_bases, "replicacion": replicacion, "bypass_rls": bypass_rls,
                      "limite_de_conexiones": limite},
    }


def _exclusion(cursor):
    """El lock de administracion en la transaccion en curso, en la misma conexion, o `OPERACION_EN_CURSO`."""
    for nombre, valor in LIMITES_DE_LA_TRANSACCION:
        cursor.execute("SELECT set_config(%s, %s, true)", (nombre, valor))
    cursor.execute("SELECT pg_try_advisory_xact_lock(%s, %s)", CLAVE_DE_ADMINISTRACION)
    if cursor.fetchone() != (True,):
        raise Fallo("OPERACION_EN_CURSO")


def _marcador(cursor, identificador):
    cursor.execute(HUELLA_DEL_MARCADOR, (identificador,))
    fila = cursor.fetchone()
    return {"presente": True, "huella": fila[1]} if fila else {"presente": False}


def _sonda_ddl(conexion, cursor):
    """§9.2 de D-24: con `blog_app`, un CREATE TABLE DEBE fallar por permisos. Nunca se confirma."""
    try:
        cursor.execute("CREATE TABLE public.sonda_ddl_h0316 (id integer)")
    except Exception as error:
        if not _de_la_base(error):
            raise
        _revertir(conexion)
        if error.sqlstate != "42501":
            raise Fallo("SONDA_DDL_NO_CONCLUYENTE") from None
        return True
    _revertir(conexion)
    raise Fallo("DDL_PERMITIDO_A_BLOG_APP")


def _rechazado(parametros, *fragmentos):
    """Un intento que DEBE fallar: True si el error trae todos los fragmentos esperados, False si el transporte se
    acepto y None si no concluye."""
    try:
        conexion = CONECTAR(**parametros)
    except Exception as error:
        if not _de_la_base(error):
            raise
        mensaje = str(error).lower()
        if all(fragmento in mensaje for fragmento in fragmentos):
            return True
        if error.sqlstate == "28P01" or "password authentication failed" in mensaje:
            return False  # el servidor llego a pedir la contrasena: el transporte se acepto
        return None
    conexion.close()
    return False


def _controles_negativos(host, usuario):
    """Sin TLS, con otro nombre de host y con una CA que no es la de RDS, la conexion DEBE fallar. Nunca con la
    contrasena real.

    - `sin_tls`: `rds.force_ssl = 1` hace que el servidor la rechace antes de autenticar.
    - `host_distinto`: la IP del mismo servidor no figura en su certificado; `verify-full` la rechaza.
    - `ca_ajena`: `verify-full` contra el almacen del sistema, que no contiene la CA privada de RDS.
    """
    sin_tls = _rechazado(_parametros(host, usuario, SIN_CREDENCIAL, "disable"), "no pg_hba.conf entry",
                         "no encryption")
    try:
        direccion = RESOLVER(host)
    except OSError:
        host_distinto = None
    else:
        host_distinto = _rechazado(_parametros(direccion, usuario, SIN_CREDENCIAL), "does not match host name")
    ca_ajena = _rechazado({**_parametros(host, usuario, SIN_CREDENCIAL), "sslrootcert": "system"},
                          "certificate verify failed")
    resultados = (sin_tls, host_distinto, ca_ajena)
    if False in resultados:
        raise Fallo("CONTROL_NEGATIVO_ACEPTADO")
    if None in resultados:
        raise Fallo("CONTROL_NEGATIVO_NO_CONCLUYENTE")
    return {"sin_tls": "RECHAZADO_POR_EL_SERVIDOR", "host_distinto": "RECHAZADO_POR_TLS",
            "ca_ajena": "RECHAZADO_POR_TLS"}


def verify(pedido):
    """Solo lectura: TLS, servidor, identidad y, segun el caso, sonda de DDL, marcador y controles negativos."""
    usuario = pedido["credencial"]["usuario"]

    def trabajo(conexion, cursor, sesion):
        if usuario == "blog_app":
            sesion["ddl_rechazado"] = _sonda_ddl(conexion, cursor)
        if "marcador" in pedido:
            sesion["marcador"] = _marcador(cursor, pedido["marcador"]["id"])
        _revertir(conexion)  # verify nunca confirma nada
        return sesion

    resultado = _operar(pedido, usuario, trabajo)
    if pedido.get("controles_negativos"):
        resultado["controles_negativos"] = _controles_negativos(pedido["destino"]["host"], usuario)
    return resultado


def _leer_identidades(cursor):
    cursor.execute("SELECT rolname, rolcanlogin, rolsuper, rolcreaterole, rolcreatedb, rolreplication, rolbypassrls, "
                   "rolinherit, rolconnlimit FROM pg_roles WHERE rolname IN ('blog_app', 'blog_migrate') "
                   "ORDER BY rolname")
    roles = {fila[0]: dict(zip(ATRIBUTOS, fila[1:])) for fila in cursor.fetchall()}
    cursor.execute("SELECT has_database_privilege('blog_migrate', 'personal_blog', 'CONNECT'), "
                   "has_database_privilege('blog_app', 'personal_blog', 'CONNECT'), "
                   "has_database_privilege('public', 'personal_blog', 'CONNECT'), "
                   "has_database_privilege('public', 'personal_blog', 'TEMPORARY')")
    connect_migra, connect_app, connect_public, temporary_public = cursor.fetchone()
    cursor.execute("SELECT has_schema_privilege('blog_migrate', 'public', 'USAGE'), "
                   "has_schema_privilege('blog_migrate', 'public', 'CREATE'), "
                   "has_schema_privilege('blog_app', 'public', 'USAGE'), "
                   "has_schema_privilege('blog_app', 'public', 'CREATE'), "
                   "has_schema_privilege('public', 'public', 'CREATE')")
    migra_usage, migra_create, app_usage, app_create, public_create = cursor.fetchone()
    cursor.execute("SELECT array_to_string(d.defaclacl, ',') FROM pg_default_acl d "
                   "JOIN pg_namespace n ON n.oid = d.defaclnamespace "
                   "WHERE d.defaclrole = 'blog_migrate'::regrole AND n.nspname = 'public' AND d.defaclobjtype = 'r'")
    fila = cursor.fetchone()
    entradas = (fila[0] or "").split(",") if fila else []
    por_omision = next((e.split("=", 1)[1].split("/", 1)[0] for e in entradas if e.startswith("blog_app=")), None)
    return {
        "roles": roles,
        "privilegios": {
            "connect": {"blog_migrate": connect_migra, "blog_app": connect_app, "public": connect_public},
            "temporary_public": temporary_public,
            "esquema_public": {"blog_migrate_usage": migra_usage, "blog_migrate_create": migra_create,
                               "blog_app_usage": app_usage, "blog_app_create": app_create,
                               "public_create": public_create},
            "por_omision_tablas_blog_app": por_omision,
        },
    }


def identidades(pedido):
    """Crea o ajusta `blog_migrate` y `blog_app` con verificadores SCRAM y los privilegios de D-23, en UNA
    transaccion que solo se confirma si la relectura coincide exactamente con lo esperado."""
    verificadores = pedido["verificadores"]

    def trabajo(conexion, cursor, sesion):
        _exclusion(cursor)
        for rol in ("blog_migrate", "blog_app"):
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (rol,))
            verbo, atributos = ("ALTER", ATRIBUTOS_AL_AJUSTAR) if cursor.fetchone() else ("CREATE", ATRIBUTOS_AL_CREAR)
            cursor.execute(f"{verbo} ROLE {rol} WITH {atributos} CONNECTION LIMIT {LIMITES[rol]} "
                           f"PASSWORD '{verificadores[rol]}'")
        for sentencia in PRIVILEGIOS:
            cursor.execute(sentencia)
        lectura = _leer_identidades(cursor)
        if lectura != ESPERADO:
            _revertir(conexion)
            raise Fallo("IDENTIDADES_NO_CONFORMES", **lectura)
        conexion.commit()
        return lectura

    return _operar(pedido, "blogadmin", trabajo)


def sintetico(pedido):
    """Siembra o limpia el marcador NO sensible de H-031-7 en la productiva, con `blog_migrate`."""
    identificador, accion = pedido["marcador"]["id"], pedido["accion"]

    def trabajo(conexion, cursor, sesion):
        _exclusion(cursor)
        if accion == "sembrar":
            cursor.execute(CREAR_MARCADOR)
            cursor.execute(INSERTAR_MARCADOR, (identificador, pedido["marcador"]["instante"],
                                               f"Task/031 H-031-7 marcador sintetico {identificador}"))
        else:
            cursor.execute("DELETE FROM verificacion.marcador WHERE id = %s", (identificador,))
        conexion.commit()
        return {"accion": accion, "marcador": _marcador(cursor, identificador)}

    return _operar(pedido, "blog_migrate", trabajo)
