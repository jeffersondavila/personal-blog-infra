"""Identidad LOCAL del backend; ejecutar con el venv existente del backend.

Sin ningun flag solo COMPRUEBA: no escribe en PostgreSQL, en MinIO ni en disco.
Cada mutacion vive tras su propio flag explicito y ninguna es implicita:

    --apply                         prepara las identidades runtime y (re)aplica
                                    grants y politicas. No rota administradores
                                    ni toca contenido.
    --rotate-example-credentials    sustituye en el `.env` ignorado las
                                    contrasenas que todavia sean las de ejemplo.
    --reissue-runtime-credentials   reemite las credenciales runtime SIN conocer
                                    las anteriores. Es el camino de recuperacion
                                    tras restaurar un respaldo: `pg_dump` de una
                                    base no incluye `CREATE ROLE`, y la copia de
                                    MinIO no incluye su IAM.

Repetir `--apply` tras cada migracion que anada tablas.
Ninguna salida de un proveedor ni valor de credencial se imprime.
"""

import argparse
import json
import os
import re
import secrets
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

import boto3
import psycopg
from botocore.exceptions import ClientError
from dotenv import dotenv_values, set_key
from psycopg import sql

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_FILE = ROOT / "secrets/backend-runtime.env"
ROLE = "blog_runtime"
ACCESS_KEY = "blog-runtime"
POLICY = "blog-runtime-media"
TABLES = (
    "administrator_sessions", "book_review_tags", "book_reviews", "login_rate_limits",
    "media_assets", "post_tags", "posts", "profile_social_links", "profiles",
    "project_tags", "projects", "tags", "video_tags", "videos",
)


def database(env, *, runtime=None):
    credentials = urlsplit(runtime["BLOG_DATABASE_URL"]) if runtime else None
    return psycopg.connect(
        host="127.0.0.1", port=int(env["POSTGRES_HOST_PORT"]),
        dbname=env["POSTGRES_DB"],
        user=unquote(credentials.username) if credentials else env["POSTGRES_USER"],
        password=unquote(credentials.password) if credentials else env["POSTGRES_PASSWORD"],
        connect_timeout=5, options="-c statement_timeout=10000 -c lock_timeout=3000",
    )


def mc(env, args, *, body="", runtime=None):
    user = runtime["BLOG_STORAGE_ACCESS_KEY"] if runtime else env["MINIO_ROOT_USER"]
    password = runtime["BLOG_STORAGE_SECRET_KEY"] if runtime else env["MINIO_ROOT_PASSWORD"]
    host = f"http://{quote(user, safe='')}:{quote(password, safe='')}@127.0.0.1:9000"
    container = env.get("COMPOSE_PROJECT_NAME", "personal-blog-local") + "-minio"
    # Credenciales por stdin: no aparecen en argv, historial ni un archivo mc.
    wrapper = 'IFS= read -r MC_HOST_task018; export MC_HOST_task018; exec mc --config-dir /tmp/task018-mc --json "$@"'
    result = subprocess.run(
        ["docker", "exec", "-i", container, "sh", "-c", wrapper, "task018", *args],
        input=host + "\n" + body, text=True, capture_output=True, timeout=30,
    )
    return result


def require_mc(result, operation):
    if result.returncode or any(json.loads(line).get("status") == "error" for line in result.stdout.splitlines()):
        raise RuntimeError(f"Fallo de MinIO durante {operation}; salida sensible omitida.")


def provision(env):
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", "secrets/backend-runtime.env"], cwd=ROOT,
        capture_output=True,
    )
    if ignored.returncode:
        raise RuntimeError("El archivo runtime debe estar ignorado por Git antes de crearlo.")
    bucket = env["BLOG_STORAGE_BUCKET"]
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]", bucket):
        raise RuntimeError("El bucket configurado no es un nombre S3 valido.")
    with database(env) as connection:
        existing = connection.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (ROLE,)).fetchone()
        if not RUNTIME_FILE.exists():
            if existing:
                raise RuntimeError("Ya existe el rol runtime sin su archivo local; no se rota automaticamente.")
            user_info = mc(env, ["admin", "user", "info", "task018", ACCESS_KEY])
            if user_info.returncode == 0:
                raise RuntimeError("Ya existe la identidad MinIO runtime sin archivo; no se rota.")
            pg_password, minio_password = secrets.token_urlsafe(48), secrets.token_urlsafe(48)
            RUNTIME_FILE.parent.mkdir(exist_ok=True)
            dsn = f"postgresql://{ROLE}:{pg_password}@postgres:5432/{quote(env['POSTGRES_DB'], safe='')}"
            with RUNTIME_FILE.open("x", encoding="utf-8", newline="\n") as destination:
                destination.write(
                    "# Credenciales runtime locales. No compartir ni versionar.\n"
                    f"BLOG_DATABASE_URL={dsn}\nBLOG_STORAGE_ACCESS_KEY={ACCESS_KEY}\n"
                    f"BLOG_STORAGE_SECRET_KEY={minio_password}\n"
                )
        runtime = dotenv_values(RUNTIME_FILE)
        credentials = urlsplit(runtime["BLOG_DATABASE_URL"])
        if credentials.username != ROLE or runtime["BLOG_STORAGE_ACCESS_KEY"] != ACCESS_KEY:
            raise RuntimeError("El archivo runtime no corresponde a las identidades de este procedimiento.")
        if not existing:
            connection.execute(sql.SQL(
                "CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE "
                "NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD {}"
            ).format(sql.Identifier(ROLE), sql.Literal(unquote(credentials.password))))
        flags = connection.execute(
            "SELECT rolsuper OR rolcreatedb OR rolcreaterole OR rolreplication OR rolbypassrls "
            "OR EXISTS (SELECT 1 FROM pg_auth_members WHERE member=pg_roles.oid) "
            "FROM pg_roles WHERE rolname=%s", (ROLE,),
        ).fetchone()
        if flags[0]:
            raise RuntimeError("El rol existente tiene privilegios ajenos al procedimiento; revisar antes de continuar.")
        role = sql.Identifier(ROLE)
        db = sql.Identifier(env["POSTGRES_DB"])
        connection.execute(sql.SQL("REVOKE CREATE, TEMPORARY ON DATABASE {} FROM PUBLIC").format(db))
        connection.execute(sql.SQL("REVOKE ALL ON DATABASE {} FROM {}").format(db, role))
        connection.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(db, role))
        connection.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
        connection.execute(sql.SQL("REVOKE ALL ON SCHEMA public FROM {}").format(role))
        connection.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(role))
        connection.execute(sql.SQL("REVOKE ALL ON ALL TABLES IN SCHEMA public FROM {}").format(role))
        for table in TABLES:
            connection.execute(sql.SQL("GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.{} TO {}").format(
                sql.Identifier(table), role,
            ))
        connection.execute(sql.SQL("GRANT SELECT, INSERT ON TABLE public.audit_events TO {}").format(role))
        connection.execute(sql.SQL("GRANT SELECT, UPDATE ON TABLE public.administrators TO {}").format(role))

    policy = {"Version": "2012-10-17", "Statement": [
        {"Effect": "Allow", "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
         "Resource": [f"arn:aws:s3:::{bucket}/*"]},
        {"Effect": "Allow", "Action": ["s3:ListBucket"], "Resource": [f"arn:aws:s3:::{bucket}"],
         "Condition": {"StringEquals": {"s3:prefix": "_readiness/"}}},
    ]}
    require_mc(mc(env, ["admin", "policy", "create", "task018", POLICY, "/dev/stdin"], body=json.dumps(policy)), "politica")
    user_info = mc(env, ["admin", "user", "info", "task018", ACCESS_KEY])
    if user_info.returncode:
        require_mc(mc(env, ["admin", "user", "add", "task018"],
                      body=ACCESS_KEY + "\n" + runtime["BLOG_STORAGE_SECRET_KEY"] + "\n"), "alta de identidad")
    else:
        data = json.loads(user_info.stdout)
        if data.get("policyName", "") not in ("", POLICY) or data.get("memberOf"):
            raise RuntimeError("La identidad MinIO posee politicas o grupos ajenos; revisar sin sobrescribirlos.")
    require_mc(mc(env, ["admin", "policy", "attach", "task018", POLICY, "--user", ACCESS_KEY]), "asignacion")
    # Si existe el .env del backend apuntando a ESTOS servicios locales,
    # sustituye solo las identidades heredadas de bootstrap. No toca destinos
    # externos ni archivos de ejemplo. El puerto/host de desarrollo se conserva.
    backend_env = ROOT.parent / "personal-blog-backend/.env"
    if backend_env.exists():
        values = dotenv_values(backend_env)
        old_dsn = values.get("BLOG_DATABASE_URL", "") or ""
        parsed = urlsplit(old_dsn)
        if parsed.hostname in ("localhost", "127.0.0.1") and parsed.username == env["POSTGRES_USER"]:
            new_auth = f"{ROLE}:{quote(unquote(credentials.password), safe='')}"
            host_part = parsed.netloc.rsplit("@", 1)[-1]
            set_key(str(backend_env), "BLOG_DATABASE_URL", parsed._replace(netloc=new_auth + "@" + host_part).geturl())
        if values.get("BLOG_STORAGE_ACCESS_KEY") == env["MINIO_ROOT_USER"] and values.get("BLOG_STORAGE_SECRET_KEY") == env["MINIO_ROOT_PASSWORD"]:
            set_key(str(backend_env), "BLOG_STORAGE_ACCESS_KEY", ACCESS_KEY)
            set_key(str(backend_env), "BLOG_STORAGE_SECRET_KEY", runtime["BLOG_STORAGE_SECRET_KEY"])
    print("Identidades runtime preparadas; administradores y contenido conservados.")


def rotate_example_credentials(env):
    """Rotacion puntual/idempotente de los dos ejemplos conocidos, nunca Portainer.

    Requiere identidades runtime preparadas. Actualiza PG en transaccion y
    reemplaza .env atomicamente; MinIO toma el nuevo root al recrear su servicio.
    """
    if not RUNTIME_FILE.exists():
        raise RuntimeError("Preparar primero las identidades runtime con --apply.")
    example = dotenv_values(ROOT / ".env.example")
    changes = {
        key: secrets.token_urlsafe(48)
        for key in ("POSTGRES_PASSWORD", "MINIO_ROOT_PASSWORD")
        if env.get(key) and env[key] == example.get(key)
    }
    if not changes:
        print("Bootstrap no utiliza contrasenas de ejemplo; no se rota ninguna credencial.")
        return
    path = ROOT / ".env"
    pending = ROOT / ".env.task018-pending"
    content = path.read_text(encoding="utf-8-sig")
    for key, value in changes.items():
        content, count = re.subn(r"^" + key + r"=.*$", key + "=" + value, content, flags=re.M)
        if count != 1:
            raise RuntimeError("La variable a rotar no tiene una unica definicion en .env.")
    with pending.open("x", encoding="utf-8", newline="\n") as destination:
        destination.write(content)
    with database(env) as connection:
        if "POSTGRES_PASSWORD" in changes:
            connection.execute(sql.SQL("ALTER ROLE {} PASSWORD {}").format(
                sql.Identifier(env["POSTGRES_USER"]), sql.Literal(changes["POSTGRES_PASSWORD"]),
            ))
            connection.commit()
        try:
            os.replace(pending, path)
        except OSError:
            if "POSTGRES_PASSWORD" in changes:
                connection.execute(sql.SQL("ALTER ROLE {} PASSWORD {}").format(
                    sql.Identifier(env["POSTGRES_USER"]), sql.Literal(env["POSTGRES_PASSWORD"]),
                ))
                connection.commit()
            raise
    print("Ejemplos sustituidos por valores aleatorios en .env ignorado; Portainer no se toca.")
    print("Recrear ahora postgres, minio y backend con Compose para aplicar la configuracion.")


def reissue_runtime_credentials(env):
    """Reemite las credenciales runtime sin conocer las anteriores.

    Existe por una propiedad del respaldo, no por un capricho: `pg_dump` de una
    base **no** exporta `CREATE ROLE`, y la copia de MinIO no exporta su IAM. Tras
    restaurar, el ACL restaurado menciona a un rol que puede no existir, y el
    archivo runtime —ignorado por Git y fuera del respaldo a proposito— puede
    haberse perdido. Sin este camino, `--apply` se detiene: no rota por su cuenta.

    No destruye contenido: no borra filas, ni objetos, ni el bucket, ni la
    identidad. Solo sustituye los dos secretos y deja que `--apply` reaplique
    grants y politicas.

    Si falla al escribir el archivo despues de cambiar los secretos, la
    recuperacion es volver a ejecutar el mismo comando: genera un par nuevo. No
    se intenta restaurar el secreto anterior porque, por definicion, aqui no se
    conoce.
    """
    nueva_pg, nueva_minio = secrets.token_urlsafe(48), secrets.token_urlsafe(48)
    with database(env) as connection:
        existe = connection.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (ROLE,)).fetchone()
        if existe:
            connection.execute(
                sql.SQL("ALTER ROLE {} PASSWORD {}").format(
                    sql.Identifier(ROLE), sql.Literal(nueva_pg)
                )
            )
    identidad = mc(env, ["admin", "user", "info", "task018", ACCESS_KEY])
    if identidad.returncode == 0:
        require_mc(
            mc(env, ["admin", "user", "add", "task018"], body=ACCESS_KEY + "\n" + nueva_minio + "\n"),
            "reemision de identidad",
        )
    dsn = f"postgresql://{ROLE}:{nueva_pg}@postgres:5432/{quote(env['POSTGRES_DB'], safe='')}"
    RUNTIME_FILE.parent.mkdir(exist_ok=True)
    pendiente = RUNTIME_FILE.with_suffix(".task018-pending")
    with pendiente.open("w", encoding="utf-8", newline="\n") as destino:
        destino.write(
            "# Credenciales runtime locales. No compartir ni versionar.\n"
            f"BLOG_DATABASE_URL={dsn}\nBLOG_STORAGE_ACCESS_KEY={ACCESS_KEY}\n"
            f"BLOG_STORAGE_SECRET_KEY={nueva_minio}\n"
        )
    os.replace(pendiente, RUNTIME_FILE)
    print("Credenciales runtime reemitidas; contenido, administradores y bucket intactos.")
    print("Recrear ahora el servicio backend con Compose para que las tome.")


def verify(env):
    runtime = dotenv_values(RUNTIME_FILE)
    if not runtime:
        raise RuntimeError("Falta el archivo runtime. Ejecutar --apply despues de las migraciones locales.")
    with database(env, runtime=runtime) as connection:
        check = connection.execute(
            "SELECT NOT rolsuper AND NOT rolcreatedb AND NOT rolcreaterole AND NOT rolbypassrls "
            "AND NOT has_database_privilege(current_user, current_database(), 'CREATE') "
            "AND NOT has_database_privilege(current_user, current_database(), 'TEMP') "
            "AND NOT has_schema_privilege(current_user, 'public', 'CREATE') "
            "AND has_table_privilege(current_user, 'public.audit_events', 'SELECT,INSERT') "
            "AND NOT has_table_privilege(current_user, 'public.audit_events', 'UPDATE,DELETE,TRUNCATE') "
            "FROM pg_roles WHERE rolname=current_user"
        ).fetchone()
        if not check or not check[0]:
            raise RuntimeError("La identidad DB no satisface minimo privilegio.")
        connection.execute("SELECT id FROM public.posts LIMIT 1").fetchall()
        for statement in (
            "UPDATE public.audit_events SET action=action WHERE false",
            "DELETE FROM public.audit_events WHERE false",
            "CREATE TABLE public.task018_permission_guard (id integer)",
        ):
            try:
                with connection.transaction(force_rollback=True):
                    connection.execute(statement)
            except psycopg.errors.InsufficientPrivilege:
                continue
            raise RuntimeError("Una operacion DB prohibida fue autorizada (transaccion revertida).")
    print("DB: SELECT permitido; UPDATE/DELETE de auditoria y DDL denegados realmente.")
    client = boto3.client(
        "s3", endpoint_url=f"http://127.0.0.1:{env['MINIO_API_HOST_PORT']}",
        aws_access_key_id=runtime["BLOG_STORAGE_ACCESS_KEY"],
        aws_secret_access_key=runtime["BLOG_STORAGE_SECRET_KEY"],
        region_name=env.get("BLOG_STORAGE_REGION", "us-east-1"),
    )
    bucket = env["BLOG_STORAGE_BUCKET"]
    client.list_objects_v2(Bucket=bucket, Prefix="_readiness/", MaxKeys=1)
    for operation in (lambda: client.list_buckets(), lambda: client.list_objects_v2(Bucket=bucket, MaxKeys=1)):
        try:
            operation()
        except ClientError as error:
            if error.response["ResponseMetadata"]["HTTPStatusCode"] == 403:
                continue
            raise RuntimeError("El control negativo S3 no devolvio denegacion de permisos.") from None
        raise RuntimeError("MinIO autorizo una enumeracion prohibida.")
    # Solo este objeto aleatorio recien creado; nunca enumera ni borra datos previos.
    key = "task018-permission-check/" + secrets.token_hex(16)
    try:
        client.put_object(Bucket=bucket, Key=key, Body=b"task018-probe", ContentType="text/plain")
        body = client.get_object(Bucket=bucket, Key=key)["Body"]
        with body:
            if body.read() != b"task018-probe":
                raise RuntimeError("El control positivo S3 no conserva bytes.")
    finally:
        client.delete_object(Bucket=bucket, Key=key)
    admin_result = mc(env, ["admin", "info", "task018"], runtime=runtime)
    denied = any(
        item.get("status") == "error" and item.get("error") == "Access Denied."
        for item in (json.loads(line) for line in admin_result.stdout.splitlines())
    )
    if not denied:
        raise RuntimeError("MinIO no demostro denegacion administrativa para runtime.")
    print("MinIO: sonda/PUT/GET/DELETE propios permitidos; listar global/bucket y administrar denegados.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--rotate-example-credentials", action="store_true")
    parser.add_argument("--reissue-runtime-credentials", action="store_true")
    args = parser.parse_args()
    env = dotenv_values(ROOT / ".env")
    try:
        # Orden fijo: primero se reemite, si se pide, para que `--apply` encuentre
        # el archivo runtime coherente y solo tenga que reaplicar grants.
        if args.reissue_runtime_credentials:
            reissue_runtime_credentials(env)
        if args.apply:
            provision(env)
        if args.rotate_example_credentials:
            rotate_example_credentials(env)
        verify(env)
    except Exception as error:
        # No mostrar excepciones de drivers: pueden transportar DSN/credenciales.
        if type(error) is RuntimeError:
            print(str(error), file=sys.stderr)
        else:
            print(f"Verificacion interrumpida ({type(error).__name__}); no se imprime informacion sensible.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
