"""Verificadores SCRAM-SHA-256 de PostgreSQL, calculados por el operador (Task/031 H-031-6).

Por que existe
--------------
`CREATE ROLE ... PASSWORD 'texto'` viaja en claro y, con `log_statement = ddl`, queda en el log del servidor, que RDS
exporta a CloudWatch. PostgreSQL guarda tal cual un PASSWORD que ya llega en formato SCRAM, asi que el operador
calcula aqui el verificador y la ejecutora solo recibe eso: la contrasena de `blog_app` y `blog_migrate` nunca llega
a la funcion ni al log.

Formato: `SCRAM-SHA-256$<iteraciones>:<sal>$<StoredKey>:<ServerKey>` (base64), con 4096 iteraciones, el valor por
omision de PostgreSQL. Algoritmo de RFC 5802/7677. Solo se admiten contrasenas alfanumericas ASCII de 32 a 64
caracteres, las que genera el procedimiento del proyecto: para ellas SASLprep es la identidad.
"""
import base64
import hashlib
import hmac
import re
import secrets

ITERACIONES = 4096
BYTES_DE_SAL = 16
_ADMITIDA = re.compile(r"^[A-Za-z0-9]{32,64}$")


def claves(contrasena, sal, iteraciones=ITERACIONES):
    """(ClientKey, StoredKey, ServerKey) de RFC 5802. La contrasena se usa y se descarta."""
    salada = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), sal, iteraciones)
    cliente = hmac.new(salada, b"Client Key", hashlib.sha256).digest()
    return cliente, hashlib.sha256(cliente).digest(), hmac.new(salada, b"Server Key", hashlib.sha256).digest()


def verificador(contrasena, sal=None):
    """Verificador SCRAM-SHA-256 en el formato que PostgreSQL guarda tal cual."""
    if not isinstance(contrasena, str) or not _ADMITIDA.match(contrasena):
        raise ValueError("CONTRASENA_NO_ADMITIDA")
    if sal is None:
        sal = secrets.token_bytes(BYTES_DE_SAL)
    if not isinstance(sal, bytes) or len(sal) != BYTES_DE_SAL:
        raise ValueError("SAL_NO_ADMITIDA")
    _, almacenada, servidor = claves(contrasena, sal)
    b64 = lambda datos: base64.b64encode(datos).decode("ascii")  # noqa: E731
    return f"SCRAM-SHA-256${ITERACIONES}:{b64(sal)}${b64(almacenada)}:{b64(servidor)}"
