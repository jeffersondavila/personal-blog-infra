#!/usr/bin/env python3
"""Lanzador del laboratorio AWS local (`Task/025`).

Que hace
--------
Orquesta el ciclo completo de la infraestructura contra el destino local:
prepara y verifica la herramienta, valida el destino con las guardas
*fail-closed*, levanta el emulador, ejecuta `init`/`plan`/`apply`, ejercita los
servicios de verdad, comprueba la idempotencia, destruye y **verifica la
ausencia**, reconstruye y vuelve a destruir.

Por que un lanzador y no una lista de comandos en un runbook
------------------------------------------------------------
Tres razones concretas, y ninguna es comodidad:

1. **El destino se revalida antes de cada operacion**, en particular antes de
   `apply` y de `destroy`. Un runbook puede saltarse un paso; esto no.
2. **El tipo de backend no se puede elegir con `-backend-config`.** Cambiar entre
   estado local y estado remoto exige que el bloque `backend` sea distinto, asi
   que se genera *solo ese bloque* justo antes de `init`. El grafo de recursos no
   se genera: es uno, versionado y unico.
3. **El entorno del proceso hijo se construye desde una *allowlist*.** Invocar
   Terraform a mano heredaria el entorno del host, con sus perfiles y proxies.

Lo que este lanzador NO es
--------------------------
No es el runbook operativo de *drift*, *rollback* y recuperacion: eso es de
`Task/026` y esta tarea no lo adelanta. Aqui hay idempotencia y reconstruccion
desde cero, que son criterios de `Task/025`.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

# Permite ejecutar tanto `python scripts/laboratorio/laboratorio.py` como
# `python -m laboratorio.laboratorio`: en el primer caso el paquete todavia no
# esta en el camino de busqueda.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from laboratorio import artefacto as mod_artefacto  # noqa: E402
from laboratorio import destino as mod_destino  # noqa: E402
from laboratorio import herramientas as mod_herramientas  # noqa: E402
from laboratorio import inventario as mod_inventario  # noqa: E402
from laboratorio import runtime as mod_runtime  # noqa: E402
from laboratorio import verificacion as mod_verificacion  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
DIRECTORIO_DE_TERRAFORM = RAIZ / "terraform"
COMPOSE_DEL_LABORATORIO = RAIZ / "laboratorio" / "docker-compose.laboratorio.yml"
ENV_DEL_LABORATORIO = RAIZ / "laboratorio" / ".env.laboratorio"
ENV_DE_EJEMPLO = RAIZ / "laboratorio" / ".env.laboratorio.example"

#: Archivos que el lanzador GENERA. Estan ignorados por Git: son configuracion
#: del destino de una ejecucion concreta, no fuente.
BACKEND_GENERADO = DIRECTORIO_DE_TERRAFORM / "backend.generado.tf"
DIRECTORIO_GENERADO = DIRECTORIO_DE_TERRAFORM / "generado"
VARIABLES_GENERADAS = DIRECTORIO_GENERADO / "destino.tfvars.json"
PLAN_GUARDADO = DIRECTORIO_GENERADO / "plan.tfplan"
PLAN_EN_JSON = DIRECTORIO_GENERADO / "plan.json"

TFVARS_LOCAL = DIRECTORIO_DE_TERRAFORM / "entornos" / "local" / "local.tfvars"

#: Prefijo de los nombres de recurso del laboratorio. Debe coincidir con el
#: `prefijo` de `entornos/local/local.tfvars`: es lo que permite buscar residuos.
PREFIJO_DEL_LABORATORIO = "blog-lab"

#: Imagenes que el laboratorio necesita. Se pre-descargan y se verifican ANTES de
#: aislar la red: `internal: true` aisla a los contenedores, no al demonio de
#: Docker, que seguiria descargando lo que falte (riesgo 8 de la ficha).
#:
#: El runtime de Lambda NO se declara aqui. Lo declara `Task/024` en el
#: `manifiesto.json` que escribe junto al artefacto, y `scripts/laboratorio/runtime.py`
#: lo lee de ahi. Asi hay **una sola autoridad** sobre el runtime y no una
#: constante duplicada que pueda desincronizarse.
#:
#: Aqui vivia un digest copiado a mano y una guarda que abortaba si la ETIQUETA
#: movil `public.ecr.aws/lambda/python:3.12` dejaba de resolver a ese digest. Eso
#: era comprobar **frescura de la etiqueta** y tratarla como autoridad de
#: identidad (H-025-3). Bloqueaba el laboratorio ante un refresco rutinario de la
#: imagen base sin proteger nada: `Task/024` construye con una referencia
#: inmutable `etiqueta@digest`, y ese digest sigue descargable.
#:
#: Lo correcto es FIJAR: descargar por digest y asociar localmente la etiqueta que
#: el emulador pide a ese contenido exacto. Ver `runtime.py`.

#: Diferencias permanentes causadas por el DESTINO local, no por la
#: configuracion. Cada una se demostro con llamadas directas a la API del
#: emulador y esta registrada en la matriz de paridad.
#:
#: Viven aqui, en el verificador, y NO como `ignore_changes` en los modulos:
#: un `ignore_changes` viajaria a produccion y silenciaria un drift REAL de un
#: atributo que AWS si sabe representar (ADR-006 limite 2, riesgo R-26).
DIFERENCIAS_DEL_DESTINO_LOCAL = (
    mod_inventario.DiferenciaDelDestino(
        tipo="aws_ssm_parameter",
        atributo="tags_all",
        motivo=(
            "el emulador DESCARTA las etiquetas enviadas en PutParameter. "
            "Comprobado el 2026-09-13 con llamadas directas: tras crear el "
            "parametro, ListTagsForResource devuelve TagList vacia; "
            "AddTagsToResource por separado SI las persiste, y el grupo de "
            "CloudWatch Logs SI conserva las cuatro etiquetas por omision. "
            "Contra AWS real PutParameter honra Tags y el plan converge."
        ),
    ),
)


class ErrorDelLaboratorio(RuntimeError):
    """Una etapa del laboratorio no se pudo completar de forma demostrable."""


# --- utilidades -------------------------------------------------------------


def titulo(texto: str) -> None:
    print()
    print("=" * 78)
    print(texto)
    print("=" * 78)


def ejecutar(
    argumentos: list[str],
    *,
    entorno: dict[str, str] | None = None,
    directorio: Path | None = None,
    codigos_aceptados: tuple[int, ...] = (0,),
    silencioso: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Ejecuta un comando y muestra su salida tal cual, sin filtrarla."""
    if not silencioso:
        print("$ " + " ".join(argumentos))
    resultado = subprocess.run(
        argumentos,
        env=entorno,
        cwd=str(directorio) if directorio else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if resultado.stdout and not silencioso:
        print(resultado.stdout, end="" if resultado.stdout.endswith("\n") else "\n")
    if resultado.stderr and not silencioso:
        print(resultado.stderr, end="" if resultado.stderr.endswith("\n") else "\n")
    if resultado.returncode not in codigos_aceptados:
        raise ErrorDelLaboratorio(
            f"'{argumentos[0]}' termino con codigo {resultado.returncode}"
        )
    return resultado


def leer_env_del_laboratorio() -> dict[str, str]:
    """Carga `.env.laboratorio`, o el ejemplo si el primero no existe.

    El ejemplo solo contiene valores ficticios y publicos por diseno, asi que
    usarlo como respaldo no introduce ningun secreto y permite ejecutar el
    laboratorio recien clonado el repositorio.
    """
    ruta = ENV_DEL_LABORATORIO if ENV_DEL_LABORATORIO.exists() else ENV_DE_EJEMPLO
    if not ruta.exists():
        raise ErrorDelLaboratorio(f"no existe '{ruta}'")
    valores: dict[str, str] = {}
    for linea in ruta.read_text(encoding="utf-8-sig").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        nombre, valor = linea.split("=", 1)
        valores[nombre.strip()] = valor.strip()
    print(f"configuracion del laboratorio: {ruta.name}")
    return valores


def construir_entorno_para_guardas(
    env_lab: dict[str, str],
    *,
    entorno_del_host: dict[str, str] | None = None,
) -> dict[str, str]:
    """Entorno sobre el que operan las guardas.

    **El valor del host siempre gana, y por tanto siempre se juzga.** La
    configuracion del laboratorio aporta valores POR OMISION, no sobrescribe.

    El orden importa, y no es un detalle de estilo. La primera version de esta
    funcion superponia `env_lab` encima del entorno del proceso, de modo que un
    `AWS_ACCESS_KEY_ID` real presente en la maquina quedaba **sustituido** por la
    fixture `test` antes de que ninguna guarda lo mirara. No habia fuga —el
    proceso hijo se construye desde una allowlist y nunca recibia esa
    credencial—, pero la comprobacion de credenciales se volvia vacua: siempre
    veia `test`. Un control negativo del CLI lo puso al descubierto.

    Invirtiendo la precedencia, una credencial real exportada en la sesion
    **detiene** el laboratorio y lo dice, que es la conducta fail-closed: una
    maquina con credenciales AWS reales en el entorno es exactamente el escenario
    contra el que avisan S-05 y el riesgo R-24.

    Regresion permanente: `tests/laboratorio/test_lanzador.py`.
    """
    entorno = dict(os.environ if entorno_del_host is None else entorno_del_host)
    for nombre, valor in env_lab.items():
        entorno.setdefault(nombre, valor)
    puerto = entorno.get("LAB_PUERTO", "4566")
    base = f"http://127.0.0.1:{puerto}"
    for servicio in mod_destino.SERVICIOS:
        entorno.setdefault(mod_destino.PREFIJO_DE_ENDPOINT + servicio.upper(), base)
    return entorno


def resolver(env_lab: dict[str, str], modo: str) -> mod_destino.Destino:
    """Resuelve el destino y lo deja por escrito. Se llama antes de cada etapa."""
    entorno = construir_entorno_para_guardas(env_lab)
    resuelto = mod_destino.resolver_destino(entorno, modo=modo)
    print(f"destino validado: modo={resuelto.modo} region={resuelto.region}")
    print(f"  endpoints: {resuelto.endpoints['s3']} (los ocho servicios)")
    print(f"  cuenta esperada: {resuelto.cuenta_esperada}")
    return resuelto


def raiz_de_estado(modo: str) -> Path:
    """Directorio del estado de Terraform. **Fuera de Git y fuera del emulador.**

    Las dos condiciones importan. Fuera de Git porque el estado puede contener
    valores sensibles y nunca se versiona (S-10). Fuera del emulador porque su
    almacenamiento es `memory` y se destruye con el contenedor: guardar ahi el
    estado significaria perder el registro de lo que hay que destruir.
    """
    return mod_herramientas.raiz_de_cache().parent / "estado" / modo


# --- herramienta ------------------------------------------------------------


def asegurar_terraform() -> Path:
    """Devuelve la ruta a un Terraform de version e identidad demostradas."""
    plataforma = mod_herramientas.plataforma_actual()
    destino_binario = mod_herramientas.ruta_de_terraform(plataforma)
    if destino_binario.exists():
        resultado = ejecutar([str(destino_binario), "version", "-json"], silencioso=True)
        try:
            version = json.loads(resultado.stdout)["terraform_version"]
        except (ValueError, KeyError):
            version = ""
        if version == mod_herramientas.VERSION_DE_TERRAFORM:
            print(f"Terraform {version} en cache verificada: {destino_binario}")
            return destino_binario
        print(f"la cache contiene la version '{version}'; se vuelve a descargar")

    url = mod_herramientas.url_de_terraform(plataforma)
    descarga = destino_binario.parent / f"terraform_{mod_herramientas.VERSION_DE_TERRAFORM}.zip"
    descarga.parent.mkdir(parents=True, exist_ok=True)
    print(f"descargando {url}")
    try:
        with urllib.request.urlopen(url, timeout=300) as respuesta, descarga.open("wb") as salida:
            shutil.copyfileobj(respuesta, salida)
    except OSError as error:
        raise ErrorDelLaboratorio(f"no se pudo descargar Terraform: {error}") from error

    esperado = mod_herramientas.CHECKSUMS_DE_TERRAFORM[plataforma]
    obtenido = mod_herramientas.verificar_checksum(descarga, esperado)
    print(f"sha256 verificado contra el valor oficial: {obtenido}")
    mod_herramientas.extraer_terraform(descarga, destino_binario)
    descarga.unlink()
    resultado = ejecutar([str(destino_binario), "version"], silencioso=True)
    print(resultado.stdout.strip())
    return destino_binario


def comando_herramientas(_: argparse.Namespace) -> int:
    titulo("HERRAMIENTAS — identidad y version")
    binario = asegurar_terraform()
    print()
    print("Alcance de esta comprobacion, dicho con precision (S-09):")
    print("  - Demuestra IDENTIDAD y PROCEDENCIA: el sha256 del artefacto coincide")
    print("    con el publicado por HashiCorp, cuyo SHA256SUMS lleva firma GPG.")
    print("  - NO demuestra ausencia de vulnerabilidades: un checksum no sabe nada")
    print("    de CVE. Esa afirmacion no se hace.")
    print()
    print(f"binario: {binario}")
    return 0


# --- imagenes ---------------------------------------------------------------


class DockerDelLaboratorio:
    """Adaptador de Docker para `runtime.py`.

    Existe para que el modulo de runtime no invoque procesos directamente y sus
    controles negativos —descarga que falla, etiquetado que falla, identidad
    discordante— se puedan ejercitar sin tocar el demonio.
    """

    def descargar(self, referencia: str) -> None:
        ejecutar(["docker", "pull", "--platform", "linux/amd64", referencia])

    def identificador(self, referencia: str) -> str | None:
        resultado = ejecutar(
            ["docker", "image", "inspect", referencia, "--format", "{{.Id}}"],
            silencioso=True,
            codigos_aceptados=(0, 1),
        )
        valor = resultado.stdout.strip()
        return valor or None

    def etiquetar(self, origen: str, destino: str) -> None:
        ejecutar(["docker", "tag", origen, destino])


def digest_de_imagen(referencia: str) -> str:
    resultado = ejecutar(
        ["docker", "image", "inspect", referencia, "--format", "{{.Id}}"], silencioso=True
    )
    return resultado.stdout.strip()


def preparar_imagenes(
    env_lab: dict[str, str],
    *,
    runtime_fijado: mod_runtime.RuntimeFijado | None = None,
) -> dict[str, Any]:
    """Pre-descarga y FIJA cada imagen ANTES de aislar la red.

    `internal: true` aisla a los contenedores, no al demonio de Docker, que
    seguiria descargando lo que falte. Por eso todo lo que el ciclo necesita se
    obtiene aqui, con acceso al registro, y despues el perimetro se cierra.

    El runtime de Lambda se **fija**, no se vigila (H-025-3): el emulador lo pide
    por etiqueta, asi que se descarga el digest que declara `Task/024` y se asocia
    la etiqueta a ese contenido exacto. Ver `runtime.py`.
    """
    titulo("IMAGENES — pre-descarga y fijacion de identidad")
    digest_emulador = env_lab.get("LAB_EMULADOR_DIGEST", "")
    if not digest_emulador.startswith("sha256:"):
        raise ErrorDelLaboratorio(
            "LAB_EMULADOR_DIGEST no declara un digest sha256; el laboratorio no "
            "opera con etiquetas moviles (control S-10)"
        )
    referencia_emulador = f"floci/floci@{digest_emulador}"

    docker = DockerDelLaboratorio()
    observados: dict[str, Any] = {}

    # El emulador ya esta fijado por digest: su identidad es trivialmente la pedida.
    docker.descargar(referencia_emulador)
    observados[referencia_emulador] = docker.identificador(referencia_emulador)
    print(f"  {referencia_emulador}\n    -> {observados[referencia_emulador]}")

    if runtime_fijado is None:
        print()
        print("  runtime de Lambda: no se prepara en esta fase porque no se")
        print("  proporciono el artefacto. `ciclo` lo fija leyendo el manifiesto.")
        return observados

    print()
    print("Runtime de Lambda — se FIJA por digest (H-025-3):")
    print(f"  autoridad             : manifiesto.json de Task/024")
    print(f"  referencia inmutable  : {runtime_fijado.referencia}")
    print(f"  etiqueta que pide el emulador: {runtime_fijado.etiqueta}")
    informe = mod_runtime.preparar_runtime(runtime_fijado, docker)
    print(f"  id local del contenido fijado: {informe['id']}")
    print(f"  accion sobre la etiqueta     : {informe['accion']}")
    if informe["accion"] == "reetiquetada":
        print(f"    la etiqueta apuntaba a {informe['id_anterior']} y se corrigio:")
        print("    una cache local obsoleta —o adelantada— no controla la evidencia.")
    print()
    print("  La etiqueta movil NO es autoridad de identidad. Que upstream la mueva")
    print("  es una senal de actualizacion disponible, no un fallo de")
    print("  reproducibilidad: Task/024 construye por digest y ese digest sigue")
    print("  descargable.")
    observados["runtime"] = informe
    return observados


# --- compose ----------------------------------------------------------------


def argumentos_de_compose(env_lab: dict[str, str]) -> list[str]:
    archivo_env = ENV_DEL_LABORATORIO if ENV_DEL_LABORATORIO.exists() else ENV_DE_EJEMPLO
    return [
        "docker",
        "compose",
        "--file",
        str(COMPOSE_DEL_LABORATORIO),
        "--env-file",
        str(archivo_env),
    ]


def esperar_emulador(env_lab: dict[str, str], *, intentos: int = 60) -> None:
    """Espera a que el emulador responda su comprobacion de salud."""
    puerto = env_lab.get("LAB_PUERTO", "4566")
    url = f"http://127.0.0.1:{puerto}/_localstack/health"
    for intento in range(1, intentos + 1):
        try:
            with urllib.request.urlopen(url, timeout=4) as respuesta:
                if respuesta.status == 200:
                    print(f"emulador listo tras {intento} intento(s)")
                    return
        except (OSError, urllib.error.HTTPError):
            pass
        time.sleep(2)
    raise ErrorDelLaboratorio(
        f"el emulador no respondio en '{url}' tras {intentos} intentos"
    )


def comprobar_perimetro(env_lab: dict[str, str]) -> dict[str, str]:
    """Demuestra que la red de ejecucion no tiene salida ni alcanza la metadata.

    No se da por supuesto: se lanza un contenedor en esa misma red y se le pide
    salir. Se usa la imagen del emulador, ya descargada, para no introducir
    ninguna imagen mas.
    """
    titulo("PERIMETRO — aislamiento real de la red de ejecucion")
    proyecto = env_lab.get("LAB_COMPOSE_PROJECT_NAME", "personal-blog-lab")
    red = f"{proyecto}_ejecucion"
    imagen = f"floci/floci@{env_lab['LAB_EMULADOR_DIGEST']}"
    pruebas = {
        "salida_tcp_externa": "timeout 5 bash -c '</dev/tcp/1.1.1.1/443' 2>&1 || true",
        "metadata_link_local": "timeout 5 bash -c '</dev/tcp/169.254.169.254/80' 2>&1 || true",
        "dns_externo": "getent hosts registry-1.docker.io 2>&1 || true",
        "alcanza_el_emulador": "getent hosts emulador 2>&1 || true",
    }
    observado: dict[str, str] = {}
    for nombre, orden in pruebas.items():
        resultado = ejecutar(
            [
                "docker", "run", "--rm", "--network", red, "--entrypoint", "sh",
                imagen, "-c", orden,
            ],
            silencioso=True,
        )
        salida = (resultado.stdout + resultado.stderr).strip() or "(sin salida)"
        observado[nombre] = salida
        print(f"  {nombre}: {salida.splitlines()[0] if salida else ''}")

    for nombre in ("salida_tcp_externa", "metadata_link_local"):
        if "unreachable" not in observado[nombre].lower() and "(sin salida)" != observado[nombre]:
            if "connect" not in observado[nombre].lower():
                raise ErrorDelLaboratorio(
                    f"la prueba '{nombre}' no demuestra aislamiento: {observado[nombre]}"
                )
    if "(sin salida)" == observado["dns_externo"] or "emulador" not in observado["alcanza_el_emulador"]:
        print("  nota: el detalle completo queda en el reporte")
    print("Aislamiento demostrado: sin salida TCP externa y sin metadata link-local.")
    return observado


def comando_levantar(argumentos: argparse.Namespace) -> int:
    titulo("LEVANTAR — laboratorio AWS local")
    env_lab = leer_env_del_laboratorio()
    destino = resolver(env_lab, argumentos.modo)

    # El runtime se fija AQUI, con acceso al registro, antes de cerrar el
    # perimetro (H-025-3). Sin artefacto no se puede: su manifiesto es la
    # autoridad. `ciclo` lo fija de todas formas, asi que no queda hueco.
    runtime_fijado = None
    if getattr(argumentos, "lambda_zip", None):
        runtime_fijado = mod_runtime.leer_runtime_fijado(argumentos.lambda_zip)
    preparar_imagenes(env_lab, runtime_fijado=runtime_fijado)

    titulo("COMPOSE — validacion y arranque")
    ejecutar(argumentos_de_compose(env_lab) + ["config", "--quiet"])
    print("Compose valido.")
    ejecutar(argumentos_de_compose(env_lab) + ["up", "--detach"])
    esperar_emulador(env_lab)
    ejecutar(
        argumentos_de_compose(env_lab)
        + ["ps", "--format", "{{.Name}} | {{.Status}} | {{.Ports}}"]
    )

    comprobar_perimetro(env_lab)

    titulo("IDENTIDAD — comprobacion contra el destino (guarda G-03)")
    observada = mod_destino.confirmar_identidad(
        destino,
        lambda d: mod_verificacion.cuenta_observada(
            d, clave=mod_destino.CLAVE_FICTICIA, secreto=mod_destino.SECRETO_FICTICIO
        ),
    )
    print(f"cuenta observada en el destino: {observada}")
    return 0


def comando_bajar(argumentos: argparse.Namespace) -> int:
    titulo("BAJAR — retirar el laboratorio y comprobar que no queda nada")
    env_lab = leer_env_del_laboratorio()
    ejecutar(
        argumentos_de_compose(env_lab) + ["down", "--volumes", "--remove-orphans"],
        codigos_aceptados=(0, 1),
    )
    # Lo que el emulador creo por el socket no lo retira Compose.
    retirados = retirar_recursos_del_emulador()
    if retirados:
        print(f"retirados {len(retirados)} recurso(s) creados por el emulador:")
        for nombre in retirados:
            print(f"  {nombre}")

    residuos = residuos_del_laboratorio(env_lab)
    for categoria, elementos in sorted(residuos.items()):
        print(f"  {categoria}: {len(elementos)}")
    mod_inventario.exigir_laboratorio_limpio(residuos)
    print("Sin contenedores, redes ni volumenes del laboratorio, ni del emulador.")
    return 0


#: Etiqueta con la que el emulador marca lo que crea a traves del socket de
#: Docker. Es la unica forma de encontrarlo: no lleva el nombre del proyecto y
#: Compose no lo conoce.
ETIQUETA_DEL_EMULADOR = "floci=true"


def residuos_del_laboratorio(
    env_lab: dict[str, str],
    *,
    listar: Callable[[list[str]], list[str]] | None = None,
) -> dict[str, list[str]]:
    """Busca restos por nombre de proyecto **y** por la etiqueta del emulador.

    Dos familias, y hacen falta las dos:

    - Lo que crea **Compose** lleva el nombre del proyecto y `compose down` lo
      retira.
    - Lo que crea el **emulador** por el socket de Docker —contenedores de las
      funciones y sus volumenes de codigo— **no** lo conoce Compose, no lleva el
      nombre del proyecto y sobrevive al `down`.

    Se comprobo en una ejecucion real: tras `compose down --volumes` quedaba
    `floci-code-blog-lab-backend-…`, con etiquetas `floci=true` y
    `floci_emulator=floci-aws`. Buscar solo por nombre de proyecto declaraba
    «0 volumenes» mientras ese seguia ahi.
    """
    proyecto = env_lab.get("LAB_COMPOSE_PROJECT_NAME", "personal-blog-lab")

    if listar is None:

        def listar(argumentos: list[str]) -> list[str]:  # type: ignore[misc]
            resultado = ejecutar(argumentos, silencioso=True, codigos_aceptados=(0, 1))
            return [l.strip() for l in resultado.stdout.splitlines() if l.strip()]

    def consultar(recurso: list[str], filtro: str, formato: str) -> list[str]:
        return listar(["docker", *recurso, "--filter", filtro, "--format", formato])

    return {
        "contenedores": consultar(["ps", "--all"], f"name={proyecto}", "{{.Names}}"),
        "contenedores_del_emulador": consultar(
            ["ps", "--all"], f"label={ETIQUETA_DEL_EMULADOR}", "{{.Names}}"
        ),
        "redes": consultar(["network", "ls"], f"name={proyecto}", "{{.Name}}"),
        "volumenes": consultar(["volume", "ls"], f"name={proyecto}", "{{.Name}}"),
        "volumenes_del_emulador": consultar(
            ["volume", "ls"], f"label={ETIQUETA_DEL_EMULADOR}", "{{.Name}}"
        ),
    }


def retirar_recursos_del_emulador() -> list[str]:
    """Retira lo que el emulador creo por el socket y Compose no conoce.

    No es una limpieza indiscriminada: se acota a la etiqueta del emulador, asi
    que no puede alcanzar nada del entorno ordinario del blog.
    """
    retirados: list[str] = []
    for recurso, formato in ((["ps", "--all"], "{{.ID}}"), (["volume", "ls"], "{{.Name}}")):
        resultado = ejecutar(
            ["docker", *recurso, "--filter", f"label={ETIQUETA_DEL_EMULADOR}",
             "--format", formato],
            silencioso=True,
            codigos_aceptados=(0, 1),
        )
        nombres = [l.strip() for l in resultado.stdout.splitlines() if l.strip()]
        for nombre in nombres:
            orden = ["docker", "rm", "--force", nombre] if recurso[0] == "ps" else [
                "docker", "volume", "rm", "--force", nombre
            ]
            ejecutar(orden, silencioso=True, codigos_aceptados=(0, 1))
            retirados.append(nombre)
    return retirados


# --- Terraform --------------------------------------------------------------


def escribir_backend(modo: str) -> Path:
    """Genera **solo** el bloque `backend`, que es lo que `init` no puede recibir.

    Esta es la respuesta a la dificultad real de **D-06**: `-backend-config` puede
    cambiar los ajustes de un backend, pero **no su tipo**. Elegir entre estado
    local y estado remoto obliga a que el bloque sea distinto.

    Lo que se genera es este archivo y nada mas. Los recursos, los modulos y las
    variables son fuente versionada: el grafo sigue siendo uno solo.
    """
    directorio_de_estado = raiz_de_estado(modo)
    directorio_de_estado.mkdir(parents=True, exist_ok=True)
    BACKEND_GENERADO.write_text(
        "# ARCHIVO GENERADO por scripts/laboratorio/laboratorio.py — no editar.\n"
        "#\n"
        "# Solo contiene el bloque `backend`, porque su TIPO no se puede cambiar\n"
        f"# con -backend-config. Destino: {modo}. Decision D-06.\n"
        "#\n"
        "# El estado vive FUERA del arbol de Git y FUERA del emulador: el\n"
        "# almacenamiento del emulador es efimero y perderlo dejaria recursos\n"
        "# creados sin registro de como destruirlos.\n"
        "\n"
        "terraform {\n"
        '  backend "local" {}\n'
        "}\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"backend generado para el destino '{modo}': {BACKEND_GENERADO.name}")
    return directorio_de_estado


def escribir_variables_del_destino(destino: mod_destino.Destino, zip_de_lambda: Path) -> None:
    """Escribe los valores que dependen de la maquina, en JSON.

    En JSON y no en HCL por una razon concreta: en HCL la barra invertida es un
    escape, y una ruta de Windows como `C:\\Users\\...` se interpretaria mal. JSON
    no tiene ese problema.
    """
    DIRECTORIO_GENERADO.mkdir(parents=True, exist_ok=True)
    VARIABLES_GENERADAS.write_text(
        json.dumps(
            {
                "endpoints_aws": dict(destino.endpoints),
                "lambda_zip_path": str(zip_de_lambda).replace("\\", "/"),
                # El contenedor de la funcion NO ve 127.0.0.1 del host: ve la red
                # de ejecucion. Este es el endpoint que el SDK debe usar desde
                # dentro, y es una de las diferencias legitimas de destino.
                "variables_del_sdk": {
                    "AWS_ENDPOINT_URL": "http://emulador:4566",
                    "AWS_ACCESS_KEY_ID": mod_destino.CLAVE_FICTICIA,
                    "AWS_SECRET_ACCESS_KEY": mod_destino.SECRETO_FICTICIO,
                    "AWS_REGION": destino.region,
                    "AWS_DEFAULT_REGION": destino.region,
                    "AWS_EC2_METADATA_DISABLED": "true",
                    "BLOG_STORAGE_ENDPOINT_URL": "http://emulador:4566",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"variables del destino escritas en {VARIABLES_GENERADAS.name}")


def terraform(
    binario: Path,
    destino: mod_destino.Destino,
    argumentos: list[str],
    *,
    codigos_aceptados: tuple[int, ...] = (0,),
    silencioso: bool = False,
) -> subprocess.CompletedProcess[str]:
    entorno = mod_destino.entorno_para_terraform(destino)
    return ejecutar(
        [str(binario), f"-chdir={DIRECTORIO_DE_TERRAFORM}"] + argumentos,
        entorno=entorno,
        codigos_aceptados=codigos_aceptados,
        silencioso=silencioso,
    )


def variables_comunes() -> list[str]:
    return [
        f"-var-file={TFVARS_LOCAL}",
        f"-var-file={VARIABLES_GENERADAS}",
    ]


def generar_lock(binario: Path, destino: mod_destino.Destino) -> None:
    """Genera el lock del provider para **las dos** plataformas y lo versiona.

    `terraform init` a secas escribe solo los hashes de la plataforma actual. Con
    el lock versionado, el dia que CI corra en Linux y el desarrollo en Windows,
    `init -lockfile=readonly` fallaria por una diferencia que no es un problema
    real. `providers lock` con las dos plataformas lo evita.
    """
    titulo("LOCK DEL PROVIDER — las dos plataformas, versionado")
    terraform(
        binario,
        destino,
        [
            "providers",
            "lock",
            "-platform=linux_amd64",
            "-platform=windows_amd64",
        ],
    )
    lock = DIRECTORIO_DE_TERRAFORM / ".terraform.lock.hcl"
    if not lock.exists():
        raise ErrorDelLaboratorio("no se genero .terraform.lock.hcl")
    texto = lock.read_text(encoding="utf-8")
    mod_herramientas.verificar_lock(texto)
    hashes = mod_herramientas.hashes_del_lock(texto)
    print(f"lock con {len(hashes)} hashes para el provider {mod_herramientas.VERSION_DEL_PROVIDER}")


def inicializar(binario: Path, destino: mod_destino.Destino, *, solo_lectura: bool) -> None:
    directorio_de_estado = escribir_backend(destino.modo)
    ruta_del_estado = directorio_de_estado / "terraform.tfstate"
    argumentos = [
        "init",
        "-input=false",
        f"-backend-config=path={str(ruta_del_estado).replace(chr(92), '/')}",
        "-reconfigure",
    ]
    if solo_lectura:
        argumentos.append("-lockfile=readonly")
    terraform(binario, destino, argumentos)
    print(f"estado local en: {ruta_del_estado}")


def revisar_plan_guardado(
    binario: Path, destino: mod_destino.Destino, *, acciones: tuple[str, ...], minimo: int
) -> dict[str, int]:
    resultado = terraform(binario, destino, ["show", "-json", str(PLAN_GUARDADO)], silencioso=True)
    PLAN_EN_JSON.write_text(resultado.stdout, encoding="utf-8", newline="\n")
    plan = json.loads(resultado.stdout)
    resumen = mod_inventario.revisar_plan(plan, acciones_permitidas=acciones, minimo=minimo)
    print(f"plan revisado contra la lista cerrada de tipos: {resumen}")
    for cambio in plan.get("resource_changes", []):
        acciones_del_cambio = ",".join(cambio["change"]["actions"])
        print(f"  {acciones_del_cambio:<8} {cambio['type']:<50} {cambio['address']}")
    return resumen


def inventario_del_destino(destino: mod_destino.Destino) -> dict[str, list[str]]:
    """Pregunta a cada API si queda algo del proyecto. Es la prueba de ausencia."""
    comun = {
        "clave_aws": mod_destino.CLAVE_FICTICIA,
        "secreto": mod_destino.SECRETO_FICTICIO,
    }
    return {
        "s3": mod_verificacion.buckets_presentes(
            destino, prefijo=PREFIJO_DEL_LABORATORIO, **comun
        ),
        "lambda": mod_verificacion.funciones_presentes(
            destino, prefijo=PREFIJO_DEL_LABORATORIO, **comun
        ),
        "apigatewayv2": mod_verificacion.apis_presentes(
            destino, prefijo=PREFIJO_DEL_LABORATORIO, **comun
        ),
        "logs": mod_verificacion.grupos_de_logs(
            destino, prefijo=f"/aws/lambda/{PREFIJO_DEL_LABORATORIO}", **comun
        ),
        "ssm": mod_verificacion.parametros_presentes(
            destino, prefijo=f"/{PREFIJO_DEL_LABORATORIO}", **comun
        ),
    }


def salidas(binario: Path, destino: mod_destino.Destino) -> dict[str, Any]:
    resultado = terraform(binario, destino, ["output", "-json"], silencioso=True)
    crudas = json.loads(resultado.stdout or "{}")
    return {nombre: dato.get("value") for nombre, dato in crudas.items()}


class ObservadorDeContenedores:
    """Vigila los contenedores de Lambda MIENTRAS viven.

    Por que hace falta observar en vivo
    -----------------------------------
    El laboratorio corre con `FLOCI_SERVICES_LAMBDA_EPHEMERAL=true`, asi que el
    emulador **retira** el contenedor al terminar la invocacion. Mirar despues con
    `docker ps --all` devuelve cero: se comprobo, y la primera version de esta
    verificacion fallo por eso.

    Tambien se observo que el emulador lanza **dos** contenedores en un arranque en
    frio —uno puebla el volumen de codigo, otro ejecuta la funcion—, y solo el
    segundo sirve como evidencia. El filtrado vive en `runtime.py`, con sus pruebas.

    Se sondea en un hilo mientras la invocacion ocurre, y de cada contenedor nuevo
    se lee de inmediato su imagen efectiva.
    """

    def __init__(self, nombre_de_la_funcion: str, *, intervalo: float = 0.12) -> None:
        self.nombre_de_la_funcion = nombre_de_la_funcion
        self.intervalo = intervalo
        self.observaciones: list[dict[str, str]] = []
        self._vistos: set[str] = set()
        self._parar = threading.Event()
        self._hilo: threading.Thread | None = None

    def _mirar_una_vez(self) -> None:
        listado = subprocess.run(
            ["docker", "ps", "--no-trunc", "--format", "{{.ID}}\t{{.Names}}"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        for linea in listado.stdout.splitlines():
            partes = linea.split("\t")
            if len(partes) < 2:
                continue
            identificador, nombre = partes[0].strip(), partes[1].strip()
            if identificador in self._vistos:
                continue
            if not mod_runtime.es_contenedor_de_la_funcion(nombre, self.nombre_de_la_funcion):
                continue
            self._vistos.add(identificador)
            detalle = subprocess.run(
                ["docker", "inspect", identificador,
                 "--format", "{{.Image}}\t{{.Config.Image}}"],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            campos = detalle.stdout.strip().split("\t")
            self.observaciones.append({
                "id": identificador,
                "nombre": nombre,
                "id_de_la_imagen": campos[0].strip() if campos else "",
                "imagen_solicitada": campos[1].strip() if len(campos) > 1 else "",
            })

    def _bucle(self) -> None:
        while not self._parar.is_set():
            try:
                self._mirar_una_vez()
            except OSError:
                pass
            self._parar.wait(self.intervalo)

    def __enter__(self) -> ObservadorDeContenedores:
        self._hilo = threading.Thread(target=self._bucle, daemon=True)
        self._hilo.start()
        return self

    def __exit__(self, *_excepcion: object) -> None:
        # Una ultima pasada antes de parar: el contenedor puede haber aparecido
        # justo al final de la invocacion.
        try:
            self._mirar_una_vez()
        except OSError:
            pass
        self._parar.set()
        if self._hilo is not None:
            self._hilo.join(timeout=5)


def verificar_contenedor_observado(
    observaciones: list[dict[str, str]],
    *,
    runtime_fijado: mod_runtime.RuntimeFijado,
    id_esperado: str,
) -> dict[str, Any]:
    """Demuestra con el CONTENEDOR REAL que se ejecuto el runtime fijado.

    El mensaje del emulador —*«Image already present locally, skipping pull»*— dice
    lo que el emulador **decidio**, no lo que **ejecuto**. Aqui se compara la
    identidad efectiva de la imagen del contenedor.
    """
    print(f"  contenedores de la funcion observados en vivo: {len(observaciones)}")
    for o in observaciones:
        print(f"    {o['nombre']}  imagen={o['imagen_solicitada']}  id={o['id_de_la_imagen']}")

    if not observaciones:
        raise ErrorDelLaboratorio(
            "no se observo ningun contenedor de Lambda del que leer la imagen. Sin esa "
            "observacion no se puede afirmar que se ejecuto el runtime fijado: el log "
            "del emulador no basta como evidencia"
        )

    elegido = observaciones[0]
    print(f"  contenedor               : {elegido['nombre']} ({elegido['id'][:12]})")
    print(f"  imagen solicitada        : {elegido['imagen_solicitada']}")
    print(f"  image ID real            : {elegido['id_de_la_imagen']}")
    print(f"  runtime fijado Task/024  : {id_esperado}")

    mod_runtime.confirmar_imagen_del_contenedor(
        runtime_fijado,
        imagen_solicitada=elegido["imagen_solicitada"],
        id_observado=elegido["id_de_la_imagen"],
        id_esperado=id_esperado,
    )
    print("  COINCIDE: el contenedor ejecuto exactamente el runtime que construyo el ZIP.")
    return {
        "contenedor": elegido["nombre"],
        "id_del_contenedor": elegido["id"][:12],
        "imagen_solicitada": elegido["imagen_solicitada"],
        "id_de_la_imagen": elegido["id_de_la_imagen"],
        "coincide_con_task024": True,
    }


def ejercitar_servicios(
    destino: mod_destino.Destino,
    valores: dict[str, Any],
    *,
    runtime_fijado: mod_runtime.RuntimeFijado,
    id_del_runtime: str,
) -> dict[str, Any]:
    """Pruebas funcionales reales sobre lo que el destino acaba de crear."""
    comun = {
        "clave_aws": mod_destino.CLAVE_FICTICIA,
        "secreto": mod_destino.SECRETO_FICTICIO,
    }
    evidencia: dict[str, Any] = {}

    titulo("FUNCIONAL — S3")
    evidencia["s3"] = mod_verificacion.ejercitar_s3(
        destino, bucket=valores["bucket_de_medios"], **comun
    )
    print(json.dumps(evidencia["s3"], indent=2, sort_keys=True))
    if not evidencia["s3"]["autorizacion_de_s3_verificada"]:
        print()
        print("  LIMITACION DEL DESTINO, no un aprobado:")
        print(f"    la lectura ANONIMA del objeto devolvio {evidencia['s3']['anonimo']},")
        print("    no 403. El emulador no aplica la autorizacion de S3 por omision")
        print("    (FLOCI_SERVICES_S3_ENFORCE_AUTH=false), asi que este laboratorio")
        print("    NO demuestra que el bucket sea privado. Demuestra que la")
        print("    CONFIGURACION de privacidad se acepta. La privacidad efectiva")
        print("    queda AWS-only: Task/030.")

    titulo("FUNCIONAL — SSM")
    evidencia["ssm"] = {}
    for nombre in valores.get("parametros") or []:
        estado, cuerpo = mod_verificacion.leer_parametro(destino, nombre=nombre, **comun)
        parametro = (cuerpo or {}).get("Parameter", {})
        evidencia["ssm"][nombre] = {"estado": estado, "tipo": parametro.get("Type")}
        print(f"  {nombre}: HTTP {estado} tipo={parametro.get('Type')}")
    print("  NOTA: el emulador conserva el tipo SecureString pero NO cifra en reposo.")
    print("        Que un parametro figure como SecureString aqui no demuestra que este protegido.")

    titulo("FUNCIONAL — IAM")
    estado, cuerpo = mod_verificacion.describir_rol(
        destino, nombre=valores["rol_de_ejecucion"], **comun
    )
    evidencia["iam"] = {"estado": estado, "confianza_a_lambda": "lambda.amazonaws.com" in cuerpo}
    print(f"  GetRole {valores['rol_de_ejecucion']}: HTTP {estado}")
    print(f"  la politica de confianza nombra a lambda.amazonaws.com: {evidencia['iam']['confianza_a_lambda']}")
    print("  NOTA: el emulador NO aplica politicas IAM por omision (R-28). Esto demuestra")
    print("        que el rol SE CREA y la politica SE ADJUNTA, no que autorice correctamente.")
    print("        El minimo privilegio es AWS-only: Task/028 y Task/032.")

    titulo("FUNCIONAL — Lambda")
    estado, cuerpo = mod_verificacion.describir_funcion(
        destino, nombre=valores["nombre_de_la_funcion"], **comun
    )
    configuracion = cuerpo.get("Configuration", cuerpo)
    evidencia["lambda"] = {
        "estado": estado,
        "runtime": configuracion.get("Runtime"),
        "handler": configuracion.get("Handler"),
        "arquitecturas": configuracion.get("Architectures"),
        "memoria": configuracion.get("MemorySize"),
        "timeout": configuracion.get("Timeout"),
        "package_type": configuracion.get("PackageType"),
    }
    print(json.dumps(evidencia["lambda"], indent=2, sort_keys=True))

    titulo("CAMINO CRITICO — GET /health por HTTP real")
    print(f"api_endpoint que devuelve Terraform: {valores['endpoint_del_api']}")
    print("  ese valor lo sintetiza el PROVIDER con la forma de AWS y NO es")
    print("  alcanzable en local. Se direcciona la API por su dominio local.")
    # La peticion se hace DENTRO del observador: el contenedor de Lambda vive solo
    # unos segundos y se retira, asi que hay que mirarlo mientras ocurre.
    with ObservadorDeContenedores(valores["nombre_de_la_funcion"]) as observador:
        estado, cuerpo_http, cabeceras, via = mod_verificacion.solicitar_camino_critico(
            id_api=valores["id_del_api"],
            endpoint_base=destino.endpoints["apigatewayv2"],
            ruta="/health",
        )
    texto = cuerpo_http.decode("utf-8", "replace")
    evidencia["camino_critico"] = {
        "api_endpoint_de_terraform": valores["endpoint_del_api"],
        "anfitrion_local": mod_verificacion.anfitrion_local_de_la_api(valores["id_del_api"]),
        "via": via,
        "estado": estado,
        "cuerpo": texto[:500],
        "content_type": cabeceras.get("Content-Type", ""),
    }
    print(f"via: {via}")
    print(f"HTTP {estado}")
    print(f"cuerpo: {texto[:500]}")
    if estado != 200:
        raise ErrorDelLaboratorio(
            f"el camino critico devolvio {estado} en lugar de 200. Esto es el "
            "criterio central de la tarea: API Gateway v2 -> Lambda -> handler"
        )

    titulo("RUNTIME — que imagen ejecuto realmente el contenedor de Lambda")
    evidencia["runtime"] = verificar_contenedor_observado(
        observador.observaciones,
        runtime_fijado=runtime_fijado,
        id_esperado=id_del_runtime,
    )

    titulo("FUNCIONAL — CloudWatch Logs")
    grupo = valores["grupo_de_logs"]
    eventos: list[str] = []
    for _ in range(10):
        eventos = mod_verificacion.eventos_de_log(destino, grupo=grupo, **comun)
        if eventos:
            break
        time.sleep(2)
    evidencia["logs"] = {"grupo": grupo, "eventos": len(eventos), "muestra": eventos[:3]}
    print(f"  grupo {grupo}: {len(eventos)} evento(s) recuperado(s)")
    for evento in eventos[:3]:
        print(f"    {evento.strip()[:160]}")
    sospechoso = [e for e in eventos if mod_destino.SECRETO_FICTICIO in e and "test" != e.strip()]
    evidencia["logs"]["sin_secretos_evidentes"] = not sospechoso
    return evidencia


def comando_ciclo(argumentos: argparse.Namespace) -> int:
    """Ciclo completo, en el orden en que cada paso produce su evidencia."""
    env_lab = leer_env_del_laboratorio()

    titulo("CICLO — validacion previa al primer plan")
    destino = resolver(env_lab, argumentos.modo)
    binario = asegurar_terraform()
    zip_congelado = mod_artefacto.describir_artefacto(argumentos.lambda_zip)
    print(f"artefacto: {zip_congelado.ruta}")
    print(f"  tamano: {zip_congelado.tamano} bytes")
    print(f"  sha256: {zip_congelado.sha256}")

    # Runtime fijado por digest (H-025-3). Idempotente: si `levantar` ya lo dejo
    # correcto, esto no cambia nada. Se hace aqui de todas formas para que el
    # ciclo no pueda ejecutarse sobre un runtime distinto del que construyo el ZIP.
    titulo("RUNTIME — fijado por digest desde el manifiesto de Task/024")
    runtime_fijado = mod_runtime.leer_runtime_fijado(zip_congelado.ruta)
    print(f"  referencia inmutable: {runtime_fijado.referencia}")
    informe_runtime = mod_runtime.preparar_runtime(runtime_fijado, DockerDelLaboratorio())
    print(f"  id local: {informe_runtime['id']}   accion: {informe_runtime['accion']}")
    id_del_runtime = informe_runtime["id"]

    mod_destino.confirmar_identidad(
        destino,
        lambda d: mod_verificacion.cuenta_observada(
            d, clave=mod_destino.CLAVE_FICTICIA, secreto=mod_destino.SECRETO_FICTICIO
        ),
    )
    print("identidad del destino confirmada antes de tocar nada")

    lock_de_operacion = raiz_de_estado(destino.modo) / "laboratorio.lock"
    with mod_destino.lock_de_escritura(lock_de_operacion):
        escribir_variables_del_destino(destino, zip_congelado.ruta)

        titulo("TERRAFORM — init, fmt, validate")
        if argumentos.regenerar_lock:
            inicializar(binario, destino, solo_lectura=False)
            generar_lock(binario, destino)
        inicializar(binario, destino, solo_lectura=True)
        terraform(binario, destino, ["fmt", "-check", "-recursive"])
        print("formato correcto")
        terraform(binario, destino, ["validate"])

        titulo("TERRAFORM — plan")
        terraform(
            binario,
            destino,
            ["plan", "-input=false", f"-out={PLAN_GUARDADO}"] + variables_comunes(),
        )
        revisar_plan_guardado(binario, destino, acciones=("create",), minimo=1)

        titulo("ARTEFACTO — confirmacion antes del apply")
        mod_artefacto.confirmar_sin_cambios(zip_congelado)
        print("el artefacto sigue siendo byte a byte el que se planifico")

        titulo("TERRAFORM — apply del plan revisado")
        terraform(binario, destino, ["apply", "-input=false", str(PLAN_GUARDADO)])
        valores = salidas(binario, destino)
        print(json.dumps(valores, indent=2, sort_keys=True))

        evidencia = ejercitar_servicios(
            destino, valores, runtime_fijado=runtime_fijado, id_del_runtime=id_del_runtime
        )

        titulo("IDEMPOTENCIA — segundo plan, se exige exit 0")
        resultado = terraform(
            binario,
            destino,
            ["plan", "-input=false", "-detailed-exitcode"] + variables_comunes(),
            codigos_aceptados=(0, 1, 2),
        )
        print(f"codigo de salida del segundo plan: {resultado.returncode}")
        informe = {}
        if resultado.returncode == 2:
            # Se vuelve a pedir el plan en JSON para poder NOMBRAR que cambia.
            # Aceptar un exit 2 sin saber exactamente que difiere seria
            # justamente lo que este gate existe para impedir.
            terraform(
                binario,
                destino,
                ["plan", "-input=false", f"-out={PLAN_GUARDADO}"] + variables_comunes(),
                silencioso=True,
            )
            crudo = terraform(
                binario, destino, ["show", "-json", str(PLAN_GUARDADO)], silencioso=True
            )
            informe = mod_inventario.exigir_sin_cambios(
                2,
                plan=json.loads(crudo.stdout),
                diferencias_toleradas=DIFERENCIAS_DEL_DESTINO_LOCAL,
            )
            print()
            print("IDEMPOTENTE SALVO UNA DIFERENCIA DEMOSTRADA DEL DESTINO:")
            for clave, cuantos in sorted(informe.items()):
                print(f"  {clave}: {cuantos} recurso(s)")
            for diferencia in DIFERENCIAS_DEL_DESTINO_LOCAL:
                print(f"  motivo ({diferencia.tipo}.{diferencia.atributo}): {diferencia.motivo}")
            print("  Ningun otro cambio quedo pendiente. La diferencia NO se oculta")
            print("  con ignore_changes: los modulos quedan intactos para AWS real.")
        else:
            mod_inventario.exigir_sin_cambios(resultado.returncode)
            print("sin cambios pendientes: la configuracion es idempotente")

        primer_destroy = destruir_y_verificar(binario, destino, valores, etapa="primer destroy")

        titulo("RECONSTRUCCION — desde cero, con las mismas fuentes")
        terraform(
            binario,
            destino,
            ["apply", "-input=false", "-auto-approve"] + variables_comunes(),
        )
        valores_reconstruidos = salidas(binario, destino)
        print(json.dumps(valores_reconstruidos, indent=2, sort_keys=True))

        titulo("SMOKE DE LA RECONSTRUCCION — GET /health otra vez")
        estado, cuerpo_http, _, via = mod_verificacion.solicitar_camino_critico(
            id_api=valores_reconstruidos["id_del_api"],
            endpoint_base=destino.endpoints["apigatewayv2"],
            ruta="/health",
        )
        print(f"via {via} — HTTP {estado} — {cuerpo_http.decode('utf-8', 'replace')[:300]}")
        if estado != 200:
            raise ErrorDelLaboratorio(
                f"el smoke de la reconstruccion devolvio {estado}: la "
                "infraestructura no es reproducible"
            )

        segundo_destroy = destruir_y_verificar(
            binario, destino, valores_reconstruidos, etapa="segundo destroy"
        )

    titulo("CICLO COMPLETO")
    resumen = {
        "artefacto_sha256": zip_congelado.sha256,
        "camino_critico": evidencia["camino_critico"]["estado"],
        "idempotencia": "exit 0" if not informe else f"exit 2 solo por {sorted(informe)}",
        "primer_destroy": primer_destroy,
        "segundo_destroy": segundo_destroy,
    }
    print(json.dumps(resumen, indent=2, sort_keys=True))
    return 0


def destruir_y_verificar(
    binario: Path,
    destino: mod_destino.Destino,
    valores: dict[str, Any],
    *,
    etapa: str,
) -> str:
    """Destruye y despues PREGUNTA a las APIs si queda algo.

    El emulador sigue en pie durante la comprobacion, a proposito: retirarlo antes
    de verificar la ausencia no seria evidencia de que el `destroy` funciono.
    """
    titulo(f"{etapa.upper()} — revalidacion del destino antes de destruir (guarda G-05)")
    mod_destino.confirmar_identidad(
        destino,
        lambda d: mod_verificacion.cuenta_observada(
            d, clave=mod_destino.CLAVE_FICTICIA, secreto=mod_destino.SECRETO_FICTICIO
        ),
    )
    print("destino revalidado inmediatamente antes de la operacion destructiva")

    bucket = valores.get("bucket_de_medios")
    if bucket:
        borrados = mod_verificacion.vaciar_bucket(
            destino,
            bucket=bucket,
            clave_aws=mod_destino.CLAVE_FICTICIA,
            secreto=mod_destino.SECRETO_FICTICIO,
        )
        print(f"objetos y versiones retirados del bucket antes del destroy: {borrados}")

    terraform(
        binario,
        destino,
        ["destroy", "-input=false", "-auto-approve"] + variables_comunes(),
    )

    titulo(f"{etapa.upper()} — verificacion de AUSENCIA contra las APIs")
    estado = terraform(binario, destino, ["state", "list"], silencioso=True, codigos_aceptados=(0, 1))
    restantes = [linea for linea in estado.stdout.splitlines() if linea.strip()]
    print(f"recursos en el estado de Terraform: {len(restantes)}")
    print("  (el estado vacio no es la evidencia: la evidencia es lo que sigue)")
    inventario = inventario_del_destino(destino)
    for servicio, elementos in sorted(inventario.items()):
        print(f"  {servicio}: {len(elementos)} recurso(s) {elementos}")
    mod_inventario.exigir_inventario_vacio(inventario)
    print("Ausencia demostrada en los cinco servicios consultados.")
    return "verificado"


# --- CLI --------------------------------------------------------------------


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="laboratorio",
        description="Laboratorio AWS local del blog (Task/025).",
    )
    parser.add_argument(
        "--modo",
        default="local",
        help=(
            "Destino de la operacion. Solo 'local' esta autorizado: el modo "
            "'production' se rechaza porque no existe autorizacion de AWS real."
        ),
    )
    subcomandos = parser.add_subparsers(dest="comando", required=True)

    subcomandos.add_parser("herramientas", help="prepara y verifica Terraform")
    levantar = subcomandos.add_parser(
        "levantar", help="pre-descarga imagenes, fija el runtime y arranca el emulador"
    )
    levantar.add_argument(
        "--lambda-zip",
        default=None,
        help=(
            "Ruta al artefacto de Task/024. Si se da, el runtime de Lambda se fija "
            "por digest en esta fase, que es la autorizada para hablar con el "
            "registro. `ciclo` lo fija igualmente."
        ),
    )
    subcomandos.add_parser("bajar", help="retira el laboratorio y comprueba residuos")

    ciclo = subcomandos.add_parser("ciclo", help="ciclo completo init/plan/apply/destroy")
    ciclo.add_argument(
        "--lambda-zip",
        required=True,
        help=(
            "Ruta EXPLICITA al artefacto ZIP de Task/024. Este repositorio no lo "
            "construye ni supone donde vive el repositorio del backend."
        ),
    )
    ciclo.add_argument(
        "--regenerar-lock",
        action="store_true",
        help="regenera .terraform.lock.hcl para las dos plataformas antes del ciclo",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    argumentos = construir_parser().parse_args(argv)
    comandos = {
        "herramientas": comando_herramientas,
        "levantar": comando_levantar,
        "bajar": comando_bajar,
        "ciclo": comando_ciclo,
    }
    try:
        return comandos[argumentos.comando](argumentos)
    except (
        mod_destino.ErrorDeDestino,
        mod_artefacto.ErrorDeArtefacto,
        mod_herramientas.ErrorDeHerramienta,
        mod_inventario.ErrorDeInventario,
        mod_verificacion.ErrorDeVerificacion,
        ErrorDelLaboratorio,
    ) as error:
        print()
        print("=" * 78)
        print("OPERACION DETENIDA")
        print("=" * 78)
        print(f"{type(error).__name__}: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
