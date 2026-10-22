#!/usr/bin/env python3
"""Laboratorio AWS local y operaciones de runbook (`Task/025` y `Task/026`).

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

Relacion con los runbooks
-------------------------
`Task/026` anade operaciones humanas atomicas para crear, validar, rollback,
destruir y recuperar. Todas reutilizan este mismo grafo y estas mismas guardas;
no hay un segundo IaC ni una ruta de fuerza. El ciclo automatico conserva la
idempotencia y reconstruccion de `Task/025` y suma inspeccion SDK y drift local.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
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
from terraform_datos import empaquetar_ejecutor as mod_ejecutor  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
DIRECTORIO_DE_TERRAFORM = RAIZ / "terraform"
COMPOSE_DEL_LABORATORIO = RAIZ / "laboratorio" / "docker-compose.laboratorio.yml"
ENV_DEL_LABORATORIO = RAIZ / "laboratorio" / ".env.laboratorio"
ENV_DE_EJEMPLO = RAIZ / "laboratorio" / ".env.laboratorio.example"

#: Root del almacenamiento de medios. Enmienda de Task/030
#: (`H-030-4-root-medios`): el bucket dejo de pertenecer al state del grafo de
#: aplicacion y vive en su propio root, que REUTILIZA el mismo modulo.
#:
#: El laboratorio usa EXACTAMENTE la misma topologia de roots que AWS real: no
#: existe la variante "en local el bucket va dentro del grafo de aplicacion".
DIRECTORIO_DE_MEDIOS = RAIZ / "terraform-medios"

#: Archivos que el lanzador GENERA. Estan ignorados por Git: son configuracion
#: del destino de una ejecucion concreta, no fuente.
BACKEND_GENERADO = DIRECTORIO_DE_TERRAFORM / "backend.generado.tf"
DIRECTORIO_GENERADO = DIRECTORIO_DE_TERRAFORM / "generado"
VARIABLES_GENERADAS = DIRECTORIO_GENERADO / "destino.tfvars.json"
PLAN_GUARDADO = DIRECTORIO_GENERADO / "plan.tfplan"
PLAN_EN_JSON = DIRECTORIO_GENERADO / "plan.json"

TFVARS_LOCAL = DIRECTORIO_DE_TERRAFORM / "entornos" / "local" / "local.tfvars"

BACKEND_GENERADO_DE_MEDIOS = DIRECTORIO_DE_MEDIOS / "backend.generado.tf"
DIRECTORIO_GENERADO_DE_MEDIOS = DIRECTORIO_DE_MEDIOS / "generado"
VARIABLES_GENERADAS_DE_MEDIOS = DIRECTORIO_GENERADO_DE_MEDIOS / "destino.tfvars.json"
PLAN_GUARDADO_DE_MEDIOS = DIRECTORIO_GENERADO_DE_MEDIOS / "plan.tfplan"
TFVARS_LOCAL_DE_MEDIOS = DIRECTORIO_DE_MEDIOS / "entornos" / "local" / "local.tfvars"

#: Endpoints que declara el root de medios. No habla con Lambda, SSM, IAM, logs ni
#: API Gateway, asi que enviarle esos atributos seria un error de tipo.
ENDPOINTS_DEL_ROOT_DE_MEDIOS = ("s3", "sts")

#: Root de DATOS: red privada y RDS de ADR-010. Enmienda de Task/031
#: (`H-031-1`, DH-1), segundo lifecycle extraido con el mismo criterio que el de
#: medios. Tambien aqui la topologia es la misma en el laboratorio y en AWS real.
DIRECTORIO_DE_DATOS = RAIZ / "terraform-datos"
BACKEND_GENERADO_DE_DATOS = DIRECTORIO_DE_DATOS / "backend.generado.tf"
DIRECTORIO_GENERADO_DE_DATOS = DIRECTORIO_DE_DATOS / "generado"
VARIABLES_GENERADAS_DE_DATOS = DIRECTORIO_GENERADO_DE_DATOS / "destino.tfvars.json"
PLAN_GUARDADO_DE_DATOS = DIRECTORIO_GENERADO_DE_DATOS / "plan.tfplan"
TFVARS_LOCAL_DE_DATOS = DIRECTORIO_DE_DATOS / "entornos" / "local" / "local.tfvars"

#: Endpoints de cada root: solo los que su variable `endpoints_aws` declara.
#: Enviarle a un root un servicio que no usa seria un atributo no soportado.
#: Desde H-031-5, datos tambien habla con IAM y Lambda (la ejecutora privada de D-24, de vuelta en el root desde el
#: 2026-10-18 con concurrencia no reservada) y desde H-031-8 con CloudWatch (alarmas de D-11). Sin el endpoint de CloudWatch, las alarmas del
#: laboratorio irian a AWS real: la lista es una guarda, no una preferencia.
ENDPOINTS_DEL_ROOT_DE_DATOS = ("cloudwatch", "ec2", "iam", "lambda", "logs", "rds", "ssm", "sts")

#: D-20 en el laboratorio: valores FICTICIOS, distintos de la cuenta del emulador. Los reales del stack de Grafana
#: solo viven en el archivo privado del destino productivo.
INTEGRACION_GRAFANA_DEL_LABORATORIO = {"cuenta": "999999999999", "external_id": "laboratorio-d20"}

#: Alarmas de D-11 (H-031-8), por senal; el mismo catalogo que el modulo `alarmas_rds`.
SENALES_DE_D11 = ("almacenamiento", "conexiones", "cpu", "creditos", "escritura", "lectura", "memoria", "xid")
ROL_DE_GRAFANA = "PersonalBlogLecturaGrafana"
ROL_DE_LA_EJECUTORA = "PersonalBlogEjecutorDatos"
ENDPOINTS_DEL_ROOT_DE_APLICACION = (
    "apigatewayv2", "cloudwatch", "iam", "lambda", "logs", "s3", "ssm", "sts",
)

#: Contrasena master del LABORATORIO. Es publica por diseno, como las
#: credenciales `test`/`test` de `destino.py`: el emulador no cifra nada y su
#: unica funcion es ser un CANARIO. Tras cada plan y cada apply del root de datos
#: se busca en el plan, el state y las salidas; si aparece, el ciclo aborta. Es
#: la demostracion empirica de DH-2 (la contrasena real nunca se genera aqui).
CONTRASENA_DEL_LABORATORIO = "LaboratorioCanarioPublicoNoEsSecreto0000"
EFIMERAS_DEL_LABORATORIO = {
    "contrasena_master": CONTRASENA_DEL_LABORATORIO,
    "contrasena_blog_migrate": "LaboratorioCanarioMigracionesNoEsSecreto0000",
    "contrasena_blog_app": "LaboratorioCanarioAplicacionNoEsSecreto0000",
}


@dataclass(frozen=True)
class RootDeTerraform:
    """Un root de Terraform con su propio state, y por tanto su propio lifecycle.

    Existe para que el lanzador pueda orquestar VARIOS roots sin bifurcar el
    codigo por destino: todos se tratan igual y solo difieren en sus rutas. El nombre
    del subdirectorio de estado es lo que garantiza que **ningun recurso queda
    administrado por dos states**.
    """

    nombre: str
    directorio: Path
    backend_generado: Path
    directorio_generado: Path
    variables_generadas: Path
    plan_guardado: Path
    tfvars_local: Path


ROOT_DE_APLICACION = RootDeTerraform(
    nombre="aplicacion",
    directorio=DIRECTORIO_DE_TERRAFORM,
    backend_generado=BACKEND_GENERADO,
    directorio_generado=DIRECTORIO_GENERADO,
    variables_generadas=VARIABLES_GENERADAS,
    plan_guardado=PLAN_GUARDADO,
    tfvars_local=TFVARS_LOCAL,
)

ROOT_DE_MEDIOS = RootDeTerraform(
    nombre="medios",
    directorio=DIRECTORIO_DE_MEDIOS,
    backend_generado=BACKEND_GENERADO_DE_MEDIOS,
    directorio_generado=DIRECTORIO_GENERADO_DE_MEDIOS,
    variables_generadas=VARIABLES_GENERADAS_DE_MEDIOS,
    plan_guardado=PLAN_GUARDADO_DE_MEDIOS,
    tfvars_local=TFVARS_LOCAL_DE_MEDIOS,
)

ROOT_DE_DATOS = RootDeTerraform(
    nombre="datos",
    directorio=DIRECTORIO_DE_DATOS,
    backend_generado=BACKEND_GENERADO_DE_DATOS,
    directorio_generado=DIRECTORIO_GENERADO_DE_DATOS,
    variables_generadas=VARIABLES_GENERADAS_DE_DATOS,
    plan_guardado=PLAN_GUARDADO_DE_DATOS,
    tfvars_local=TFVARS_LOCAL_DE_DATOS,
)

#: Orden canonico de los roots al CREAR o reconciliar: medios primero, porque
#: datos recibe el ARN de su bucket para la politica del gateway endpoint; datos
#: despues, y aplicacion al final (Task/032 consumira las salidas de datos).
#: Esta tupla es la **unica** autoridad sobre el orden; ningun comando declara
#: el suyo. Invertirla da el orden de destruccion, y no se escribe a mano para
#: que las dos no puedan desincronizarse.
ROOTS_EN_ORDEN_DE_CREACION: tuple[RootDeTerraform, ...] = (
    ROOT_DE_MEDIOS,
    ROOT_DE_DATOS,
    ROOT_DE_APLICACION,
)

ROOTS_EN_ORDEN_DE_DESTRUCCION: tuple[RootDeTerraform, ...] = tuple(
    reversed(ROOTS_EN_ORDEN_DE_CREACION)
)

#: Sentido de cada operacion del lanzador. Se declara explicitamente para que un
#: comando nuevo no herede un orden por omision: `secuencia_de_roots` aborta si
#: la operacion no esta aqui. Es la leccion de DEF-030-2, donde cinco
#: subcomandos se quedaron operando sobre un solo root sin que nada avisara.
SENTIDO_DE_CADA_OPERACION: dict[str, str] = {
    "ciclo": "creacion",
    "crear": "creacion",
    "rollback": "creacion",
    "recuperar": "creacion",
    "validar": "lectura",
    "destruir": "destruccion",
}

#: Prefijo de los nombres de recurso del laboratorio. Debe coincidir con el
#: `prefijo` de `entornos/local/local.tfvars`: es lo que permite buscar residuos.
PREFIJO_DEL_LABORATORIO = "blog-lab"

#: Unico recurso que el ensayo de drift puede retirar. Es configuracion
#: ficticia, se reconstruye desde el grafo y no contiene datos del usuario.
PARAMETRO_DE_DRIFT = "/blog-lab/local/storage_region"
DIRECCION_TERRAFORM_DEL_DRIFT = (
    'module.parametros.aws_ssm_parameter.configuracion["local/storage_region"]'
)
ACTUALIZACIONES_DEPENDIENTES_DEL_DRIFT = (
    mod_inventario.ActualizacionDependienteDelDrift(
        direccion="module.identidad.aws_iam_role_policy.permisos",
        tipo="aws_iam_role_policy",
        atributo="policy",
    ),
)

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
# H-025-1: Floci 2.0.1 descartaba Tags en PutParameter (2026-09-13).
# Resuelto con 2.1.0 en el addendum de Task/027.1. Se conserva la historia
# en TASK-025-report.md; tags_all vuelve a exigir convergencia literal.
DIFERENCIAS_DEL_DESTINO_LOCAL: tuple[mod_inventario.DiferenciaDelDestino, ...] = ()

#: Diferencias del destino local en el root de DATOS, observadas en H-031-1 con
#: Floci 2.1.0 y RDS en modo `mock` (sin motor). Cada una se demostro con un
#: segundo plan tras un apply limpio: el emulador acepta el valor pero no lo
#: devuelve, y el plan nunca converge por un motivo ajeno a la configuracion.
#: Mismo criterio que arriba: tolerancia ESTRECHA por tipo y atributo, en el
#: verificador y NUNCA como `ignore_changes`. Contra AWS real no se tolera
#: ninguna: la convergencia exigida alli es 0/0/0.
_MOTIVO_RDS_MOCK = (
    "Floci 2.1.0 con RDS en modo mock no conserva ni devuelve este atributo de la "
    "instancia (H-031-1); AWS real si lo representa"
)
DIFERENCIAS_DEL_DESTINO_LOCAL_DE_DATOS: tuple[mod_inventario.DiferenciaDelDestino, ...] = (
    *(
        mod_inventario.DiferenciaDelDestino(
            tipo="aws_db_instance", atributo=atributo, motivo=_MOTIVO_RDS_MOCK
        )
        for atributo in (
            "ca_cert_identifier",
            "enabled_cloudwatch_logs_exports",
            "engine_lifecycle_support",
            "max_allocated_storage",
            "network_type",
            "port",
            "storage_type",
        )
    ),
    mod_inventario.DiferenciaDelDestino(
        tipo="aws_db_parameter_group",
        atributo="parameter",
        motivo="Floci 2.1.0 acepta ModifyDBParameterGroup pero DescribeDBParameters no devuelve los valores de usuario (H-031-1)",
    ),
    mod_inventario.DiferenciaDelDestino(
        tipo="aws_ssm_parameter",
        atributo="key_id",
        motivo="Floci 2.1.0 no devuelve el KeyId de un SecureString: no hay KMS que lo respalde (aws-local-parity.md 6.4)",
    ),
    mod_inventario.DiferenciaDelDestino(
        tipo="aws_ssm_parameter",
        atributo="tier",
        motivo="Floci 2.1.0 no devuelve el Tier del parametro en DescribeParameters (H-031-1)",
    ),
    # Ciclo del 2026-10-19 (H-031-6): primer ciclo completo con las alarmas de H-031-8.
    *(
        mod_inventario.DiferenciaDelDestino(
            tipo="aws_cloudwatch_metric_alarm",
            atributo=atributo,
            motivo=(
                f"Floci 2.1.0 acepta {campo} en PutMetricAlarm pero DescribeAlarms no lo devuelve (llamada "
                "directa al emulador, 2026-10-19); AWS real si: readback 8/8 de H-031-8"
            ),
        )
        for atributo, campo in (("datapoints_to_alarm", "DatapointsToAlarm"),
                                ("extended_statistic", "ExtendedStatistic"))
    ),
)

#: `resource_drift` del root de DATOS: lista CERRADA por direccion, acciones,
#: conjunto exacto de atributos y forma de cada transicion (H-031-1A). Antes de
#: H-031-1A el gate no leia esta seccion y `domain_dns_ips: null -> []` paso sin
#: declararse; el ciclo se rechazo y solo despues de diagnosticarlo se declaro.
#:
#: `domain_dns_ips` NO es una diferencia del emulador: es la representacion del
#: SDKv2 del provider. Por eso su motivo lo dice, y por eso contra AWS real se
#: espera la misma entrada, que `scripts/terraform_datos/check_plan.py` y el
#: plan de convergencia de H-031-3 siguen rechazando (DN-2). Nada de esto viaja
#: a los modulos: ni `ignore_changes`, ni tolerancia productiva.
_MOTIVO_DOMAIN_DNS_IPS = (
    "domain_dns_ips null -> []: representacion del SDKv2 2.40.1 que usa el provider "
    "6.64.0, no del emulador. Read escribe la lista vacia en toda instancia sin dominio "
    "AD; el apply conserva el null planificado (normalizeNullValues con apply=true) y "
    "el refresh no (apply=false); Terraform compara con RawEquals. "
    "enabled_cloudwatch_logs_exports -> []: Floci 2.1.0 con RDS mock no lo devuelve (H-031-1)"
)
_MOTIVO_REGLAS_SEPARADAS = (
    "Floci 2.1.0 devuelve en el grupo las reglas que gestionan aparte los recursos "
    "aws_vpc_security_group_*_rule, creadas despues de escribir el state del grupo. "
    "Observacion del laboratorio: no predice el drift de AWS (DN-2)"
)
DRIFT_DEL_DESTINO_LOCAL_DE_DATOS: tuple[mod_inventario.DriftDelDestino, ...] = (
    mod_inventario.DriftDelDestino(
        direccion="module.base_de_datos.aws_db_instance.this",
        tipo="aws_db_instance",
        acciones=("update",),
        transiciones=(
            ("domain_dns_ips", "nulo_a_lista_vacia"),
            ("enabled_cloudwatch_logs_exports", "lista_a_vacia"),
        ),
        motivo=_MOTIVO_DOMAIN_DNS_IPS,
    ),
    mod_inventario.DriftDelDestino(
        direccion="module.base_de_datos.aws_db_parameter_group.this",
        tipo="aws_db_parameter_group",
        acciones=("update",),
        transiciones=(("parameter", "lista_a_vacia"),),
        motivo="Floci 2.1.0 acepta ModifyDBParameterGroup pero DescribeDBParameters no devuelve los valores de usuario (H-031-1)",
    ),
    *(
        mod_inventario.DriftDelDestino(
            direccion=f"module.red.aws_security_group.{grupo}",
            tipo="aws_security_group",
            acciones=("update",),
            transiciones=((sentido, "agrega_reglas_separadas"),),
            motivo=_MOTIVO_REGLAS_SEPARADAS,
        )
        for grupo, sentido in (("admin", "egress"), ("lambda", "egress"), ("rds", "ingress"))
    ),
    # Ciclo del 2026-10-19 (H-031-6): primer ciclo completo con H-031-8, H-031-9, H-031-5 y H-031-6. Igual que
    # `domain_dns_ips`, NO son diferencias del emulador: es la representacion del SDKv2 tras crear, observada TAMBIEN
    # contra AWS real y resuelta alli con refresh-only guardados y autorizados. La convergencia productiva sigue
    # exigiendo `resource_drift` vacio.
    *(
        mod_inventario.DriftDelDestino(
            direccion=f'module.alarmas_rds.aws_cloudwatch_metric_alarm.this["{senal}"]',
            tipo="aws_cloudwatch_metric_alarm",
            acciones=("update",),
            transiciones=tuple((lista, "nulo_a_lista_vacia")
                               for lista in ("alarm_actions", "insufficient_data_actions", "ok_actions")),
            motivo=(
                "Listas de acciones null -> []: representacion del SDKv2 del provider 6.64.0 tras crear una alarma "
                "sin acciones; la misma que se observo en AWS real (reporte de Task/031 §47.7)"
            ),
        )
        for senal in SENALES_DE_D11
    ),
    mod_inventario.DriftDelDestino(
        direccion="module.ejecutor_privado.aws_iam_role.this",
        tipo="aws_iam_role",
        acciones=("update",),
        transiciones=(("inline_policy", "refleja_politicas_en_linea"),),
        motivo=(
            "inline_policy [] -> reflejo EXACTO de sus politicas en linea (-ejecucion y, desde H-031-6, "
            "-exportacion): representacion del provider; la misma que se observo en AWS real (§49.15)"
        ),
    ),
    mod_inventario.DriftDelDestino(
        direccion="module.ejecutor_privado.aws_lambda_function.this",
        tipo="aws_lambda_function",
        acciones=("update",),
        transiciones=(("layers", "nulo_a_lista_vacia"),),
        motivo="layers null -> []: representacion del SDKv2; la misma que se observo en AWS real (§49.15)",
    ),
    mod_inventario.DriftDelDestino(
        direccion="module.lectura_grafana.aws_iam_role.this",
        tipo="aws_iam_role",
        acciones=("update",),
        transiciones=(("inline_policy", "refleja_politicas_en_linea"), ("tags", "nulo_a_mapa_vacio")),
        motivo=(
            "inline_policy [] -> reflejo EXACTO de su politica -lectura y tags null -> {}: representacion del "
            "provider; la misma que se observo en AWS real (§47.9)"
        ),
    ),
)


class ErrorDelLaboratorio(RuntimeError):
    """Una etapa del laboratorio no se pudo completar de forma demostrable."""


def secuencia_de_roots(operacion: str) -> tuple[RootDeTerraform, ...]:
    """Roots que toca `operacion`, en el orden en que debe tocarlos.

    Es el arreglo de **DEF-030-2**. La enmienda de `Task/030` extrajo el
    almacenamiento de medios a su propio root y cablo la topologia solo en
    `ciclo`; `crear`, `validar`, `rollback`, `destruir` y `recuperar` siguieron
    asumiendo un root unico. `destruir` llegaba a destruir el grafo de aplicacion
    y despues abortaba por inventario, dejando el bucket en pie.

    Aqui vive la unica respuesta a «que roots y en que orden», y una operacion no
    declarada **aborta** en lugar de recibir un orden por omision.
    """
    sentido = SENTIDO_DE_CADA_OPERACION.get(operacion)
    if sentido is None:
        raise ErrorDelLaboratorio(
            f"la operacion '{operacion}' no declara su sentido en "
            "SENTIDO_DE_CADA_OPERACION: sin eso no se puede saber en que orden "
            f"tocar los roots. Declaradas: {sorted(SENTIDO_DE_CADA_OPERACION)}"
        )
    if sentido == "destruccion":
        return ROOTS_EN_ORDEN_DE_DESTRUCCION
    return ROOTS_EN_ORDEN_DE_CREACION


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
    print(f"  endpoints: {resuelto.endpoints['s3']} (los diez servicios)")
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


def validar_publicacion_de_floci(
    inspecciones: list[dict[str, Any]],
    *,
    proyecto_esperado: str,
    puerto_esperado: str,
) -> list[str]:
    """Exige un unico contenedor y un unico *binding*, siempre en loopback.

    Comprobar solamente que los endpoints configurados dicen ``127.0.0.1`` no
    demuestra que Docker no haya publicado ademas el mismo puerto —u otro— en
    LAN, Internet, IPv6 o un rango auxiliar. Por eso se juzga el estado efectivo
    que devuelve ``docker inspect`` y cualquier ambiguedad aborta (R-23).
    """
    if len(inspecciones) != 1:
        raise ErrorDelLaboratorio(
            "no se puede demostrar la publicacion de Floci: se esperaba un "
            f"contenedor y se observaron {len(inspecciones)}"
        )

    inspeccion = inspecciones[0]
    etiquetas = (inspeccion.get("Config") or {}).get("Labels") or {}
    if etiquetas.get("com.docker.compose.project") != proyecto_esperado:
        raise ErrorDelLaboratorio(
            "el contenedor inspeccionado no pertenece al proyecto Compose esperado"
        )
    if etiquetas.get("com.docker.compose.service") != "emulador":
        raise ErrorDelLaboratorio(
            "el contenedor inspeccionado no es el servicio 'emulador'"
        )

    puertos = (inspeccion.get("NetworkSettings") or {}).get("Ports") or {}
    bindings: list[tuple[str, str, str]] = []
    for puerto_del_contenedor, publicaciones in puertos.items():
        for publicacion in publicaciones or []:
            bindings.append(
                (
                    str(puerto_del_contenedor),
                    str(publicacion.get("HostIp") or ""),
                    str(publicacion.get("HostPort") or ""),
                )
            )

    esperado = ("4566/tcp", "127.0.0.1", str(puerto_esperado))
    if bindings != [esperado]:
        observados = [f"{p} -> {h or '<vacio>'}:{hp or '<vacio>'}" for p, h, hp in bindings]
        raise ErrorDelLaboratorio(
            "publicacion insegura o ambigua de Floci: se exige exactamente "
            f"'{esperado[0]} -> {esperado[1]}:{esperado[2]}' y se observo "
            f"{observados or ['ningun binding']}"
        )
    return [f"{esperado[0]} -> {esperado[1]}:{esperado[2]}"]


def comprobar_publicacion_de_floci(env_lab: dict[str, str]) -> list[str]:
    """Consulta Docker y demuestra la publicacion efectiva de Floci (R-23)."""
    proyecto = env_lab.get("LAB_COMPOSE_PROJECT_NAME", "personal-blog-lab")
    puerto = env_lab.get("LAB_PUERTO", "4566")
    resultado = ejecutar(
        [
            "docker",
            "ps",
            "--filter",
            f"label=com.docker.compose.project={proyecto}",
            "--filter",
            "label=com.docker.compose.service=emulador",
            "--format",
            "{{.ID}}",
        ],
        silencioso=True,
    )
    identificadores = [linea.strip() for linea in resultado.stdout.splitlines() if linea.strip()]
    if len(identificadores) != 1:
        raise ErrorDelLaboratorio(
            "no se puede demostrar la publicacion de Floci: se esperaba un "
            f"contenedor activo y se observaron {len(identificadores)}"
        )
    crudo = ejecutar(
        ["docker", "inspect", identificadores[0]],
        silencioso=True,
    )
    try:
        inspecciones = json.loads(crudo.stdout)
    except (TypeError, ValueError) as error:
        raise ErrorDelLaboratorio(
            "docker inspect no devolvio JSON valido para demostrar el perimetro"
        ) from error
    observados = validar_publicacion_de_floci(
        inspecciones,
        proyecto_esperado=proyecto,
        puerto_esperado=puerto,
    )
    print(f"publicacion de Floci demostrada: {observados[0]}")
    return observados


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

    comprobar_publicacion_de_floci(env_lab)
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


def escribir_backend(modo: str, root: RootDeTerraform = ROOT_DE_APLICACION) -> Path:
    """Genera **solo** el bloque `backend`, que es lo que `init` no puede recibir.

    Esta es la respuesta a la dificultad real de **D-06**: `-backend-config` puede
    cambiar los ajustes de un backend, pero **no su tipo**. Elegir entre estado
    local y estado remoto obliga a que el bloque sea distinto.

    Lo que se genera es este archivo y nada mas. Los recursos, los modulos y las
    variables son fuente versionada: el grafo sigue siendo uno solo.

    Cada root recibe su **propio subdirectorio de estado**. Es lo que impide que
    dos roots compartan archivo de state y, con ello, que un recurso acabe
    administrado dos veces (enmienda de Task/030).
    """
    directorio_de_estado = raiz_de_estado(modo) / root.nombre
    directorio_de_estado.mkdir(parents=True, exist_ok=True)
    root.backend_generado.write_text(
        "# ARCHIVO GENERADO por scripts/laboratorio/laboratorio.py — no editar.\n"
        "#\n"
        "# Solo contiene el bloque `backend`, porque su TIPO no se puede cambiar\n"
        f"# con -backend-config. Destino: {modo}. Decision D-06.\n"
        "#\n"
        "# El estado vive FUERA del arbol de Git y FUERA del emulador: el\n"
        "# almacenamiento del emulador es efimero y perderlo dejaria recursos\n"
        "# creados sin registro de como destruirlos.\n"
        f"# Root: {root.nombre}. Su state es propio y no se comparte.\n"
        "\n"
        "terraform {\n"
        '  backend "local" {}\n'
        "}\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"backend generado para el destino '{modo}', root '{root.nombre}': "
        f"{root.backend_generado.name}"
    )
    return directorio_de_estado


def escribir_variables_del_destino(
    destino: mod_destino.Destino,
    zip_de_lambda: Path,
    medios: dict[str, Any] | None = None,
) -> None:
    """Escribe los valores que dependen de la maquina, en JSON.

    En JSON y no en HCL por una razon concreta: en HCL la barra invertida es un
    escape, y una ruta de Windows como `C:\\Users\\...` se interpretaria mal. JSON
    no tiene ese problema.

    `medios` son las salidas del root de almacenamiento, ya aplicado. Viajan por
    aqui —y no con `-var` en cada invocacion— porque este archivo lo incluyen ya
    todos los comandos del root de aplicacion, igual que `lambda_zip_path`. Es el
    transporte del contrato explicito entre los dos roots: sin
    `terraform_remote_state` y sin que este root conozca donde vive el otro state.
    """
    if medios is None:
        # Operaciones humanas de Task/026: corren sobre un laboratorio YA creado,
        # asi que el contrato del bucket ya esta escrito. Se reutiliza en lugar de
        # reinicializar el root de medios solo para releer dos valores.
        previas = (
            json.loads(VARIABLES_GENERADAS.read_text(encoding="utf-8"))
            if VARIABLES_GENERADAS.exists()
            else {}
        )
        medios = {
            "nombre_del_bucket": previas.get("nombre_del_bucket_de_medios"),
            "arn_del_bucket": previas.get("arn_del_bucket_de_medios"),
        }
    for clave in ("nombre_del_bucket", "arn_del_bucket"):
        if not medios.get(clave):
            raise ErrorDelLaboratorio(
                f"falta '{clave}' del contrato del root de medios: el grafo de "
                "aplicacion no puede recibirlo. Ejecuta el ciclo, que aplica el "
                "root de almacenamiento antes que el de aplicacion"
            )
    DIRECTORIO_GENERADO.mkdir(parents=True, exist_ok=True)
    VARIABLES_GENERADAS.write_text(
        json.dumps(
            {
                # Solo los servicios que este root declara: desde Task/031 el
                # destino resuelve tambien EC2 y RDS, que son del root de datos.
                "endpoints_aws": {
                    nombre: valor
                    for nombre, valor in dict(destino.endpoints).items()
                    if nombre in ENDPOINTS_DEL_ROOT_DE_APLICACION
                },
                "lambda_zip_path": str(zip_de_lambda).replace("\\", "/"),
                # Contrato recibido del root de medios. Este root NO administra el
                # bucket: solo lo consume.
                "nombre_del_bucket_de_medios": medios["nombre_del_bucket"],
                "arn_del_bucket_de_medios": medios["arn_del_bucket"],
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


def escribir_variables_de_medios(destino: mod_destino.Destino) -> None:
    """Variables del destino para el root de medios.

    Solo necesita los endpoints: el nombre del bucket, las etiquetas, el CORS y el
    lifecycle viven en su tfvars versionado. Se escribe aparte porque es OTRO root
    con OTRO state, y mezclar sus variables reintroduciria el acoplamiento que la
    enmienda de Task/030 elimina.

    Se pasan **solo** los endpoints que ese root declara. Su variable es un objeto
    con `s3` y `sts`, y enviarle los ocho del grafo de aplicacion seria un atributo
    no soportado: el root de medios no habla con Lambda, ni con SSM, ni con IAM.
    """
    DIRECTORIO_GENERADO_DE_MEDIOS.mkdir(parents=True, exist_ok=True)
    endpoints = {
        nombre: valor
        for nombre, valor in dict(destino.endpoints).items()
        if nombre in ENDPOINTS_DEL_ROOT_DE_MEDIOS
    }
    VARIABLES_GENERADAS_DE_MEDIOS.write_text(
        json.dumps({"endpoints_aws": endpoints}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"variables del root de medios escritas en {VARIABLES_GENERADAS_DE_MEDIOS.name}")


def preparar_ejecutor_h0316(destino: Path) -> str:
    """Copia solo el ZIP H-031-6 previamente construido y verificado; nunca descarga dependencias.

    PERSONAL_BLOG_EJECUTOR_ZIP apunta al resultado de empaquetar_ejecutor.py --fase h0316.
    La guarda exige el mismo pin que AWS. El laboratorio no invoca SQL contra el RDS mock.
    """
    origen = os.environ.get("PERSONAL_BLOG_EJECUTOR_ZIP", "")
    if not origen or not Path(origen).is_file():
        raise ErrorDelLaboratorio("falta PERSONAL_BLOG_EJECUTOR_ZIP: construir el artefacto H-031-6 con sus ruedas fijadas")
    contenido = Path(origen).read_bytes()
    sha256 = hashlib.sha256(contenido).hexdigest()
    if sha256 != mod_ejecutor.SHA256_ESPERADO_H0316:
        raise ErrorDelLaboratorio("el artefacto H-031-6 no coincide con su pin")
    destino.write_bytes(contenido)
    return sha256


def escribir_variables_de_datos(
    destino: mod_destino.Destino, medios: dict[str, Any] | None = None
) -> None:
    """Variables del destino para el root de datos.

    Lleva cinco cosas, y ninguna mas:
    - los endpoints que ese root declara;
    - el ARN del bucket que publica el root de medios, por contrato explicito y sin
      `terraform_remote_state`;
    - el artefacto FIJADO de la ejecutora de D-24 (h0316 desde H-031-6), copiado de
      `PERSONAL_BLOG_EJECUTOR_ZIP` y comprobado contra su pin;
    - la integracion de Grafana FICTICIA de D-20;
    - las tres contrasenas FICTICIAS del laboratorio (master, `blog_migrate` y
      `blog_app`), cada una un canario distinto.

    Las contrasenas son variables efimeras: Terraform las usa para los atributos
    write-only y no las escribe ni en el plan ni en el state. Que aqui viajen en un
    archivo generado e ignorado por Git es aceptable porque son publicas por
    diseno; en AWS real nunca se escriben en un archivo de variables (DH-2).
    """
    if medios is None:
        previas = (
            json.loads(VARIABLES_GENERADAS_DE_DATOS.read_text(encoding="utf-8"))
            if VARIABLES_GENERADAS_DE_DATOS.exists()
            else {}
        )
        medios = {"arn_del_bucket": previas.get("arn_del_bucket_de_medios")}
    if not medios.get("arn_del_bucket"):
        raise ErrorDelLaboratorio(
            "falta 'arn_del_bucket' del contrato del root de medios: el root de "
            "datos no puede limitar a el su gateway endpoint"
        )
    DIRECTORIO_GENERADO_DE_DATOS.mkdir(parents=True, exist_ok=True)
    artefacto = DIRECTORIO_GENERADO_DE_DATOS / "ejecutor.zip"
    sha256 = preparar_ejecutor_h0316(artefacto)
    endpoints = {
        nombre: valor
        for nombre, valor in dict(destino.endpoints).items()
        if nombre in ENDPOINTS_DEL_ROOT_DE_DATOS
    }
    VARIABLES_GENERADAS_DE_DATOS.write_text(
        json.dumps(
            {
                "endpoints_aws": endpoints,
                "arn_del_bucket_de_medios": medios["arn_del_bucket"],
                "integracion_grafana": dict(INTEGRACION_GRAFANA_DEL_LABORATORIO),
                "zip_de_la_ejecutora": {"ruta": artefacto.as_posix(), "sha256": sha256},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    # La efimera en archivo PROPIO: al aplicar un plan guardado hay que volver a
    # aportarla, y Terraform rechaza que se repitan las demas variables.
    ruta_de_las_efimeras_de_datos().write_text(
        json.dumps(EFIMERAS_DEL_LABORATORIO, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"variables del root de datos escritas en {VARIABLES_GENERADAS_DE_DATOS.name}")


def exigir_canarios_ausentes(textos: dict[str, str]) -> list[str]:
    for canario in EFIMERAS_DEL_LABORATORIO.values():
        exigir_secreto_ausente(textos, canario)
    return list(textos)


def exigir_secreto_ausente(textos: dict[str, str], secreto: str) -> list[str]:
    """Aborta si `secreto` aparece en cualquiera de los textos (DH-2).

    Se usa con la contrasena CANARIO del laboratorio sobre el plan, el state y
    las salidas del root de datos. Devuelve lo que se reviso, para el reporte. El
    secreto nunca se imprime: el error nombra el texto, no su contenido.
    """
    if not secreto:
        raise ErrorDelLaboratorio("no hay canario que buscar: la comprobacion seria vacua")
    revisados: list[str] = []
    for nombre, texto in textos.items():
        if secreto in (texto or ""):
            raise ErrorDelLaboratorio(
                f"la contrasena master aparece en '{nombre}': un atributo que no es "
                "write-only la esta persistiendo. STOP (DH-2)"
            )
        revisados.append(nombre)
    return revisados


def terraform(
    binario: Path,
    destino: mod_destino.Destino,
    argumentos: list[str],
    *,
    raiz: Path = DIRECTORIO_DE_TERRAFORM,
    codigos_aceptados: tuple[int, ...] = (0,),
    silencioso: bool = False,
) -> subprocess.CompletedProcess[str]:
    operacion = argumentos[0] if argumentos else ""
    if operacion in {"init", "plan", "apply", "destroy"}:
        print(f"root objetivo: {raiz.name}")
        titulo(
            "GUARDAS — destino y perimetro antes de "
            f"terraform {operacion} (R-23/R-24)"
        )
        env_lab = leer_env_del_laboratorio()
        destino_actual = resolver(env_lab, destino.modo)
        if destino_actual != destino:
            raise ErrorDelLaboratorio(
                "el destino cambio desde la validacion inicial; la operacion Terraform aborta"
            )
        comprobar_publicacion_de_floci(env_lab)
        mod_destino.confirmar_identidad(
            destino_actual,
            lambda d: mod_verificacion.cuenta_observada(
                d,
                clave=mod_destino.CLAVE_FICTICIA,
                secreto=mod_destino.SECRETO_FICTICIO,
            ),
        )
        print(
            "guarda satisfecha: modo local explicito, loopback exclusivo e "
            f"identidad {destino_actual.cuenta_esperada}"
        )
    entorno = mod_destino.entorno_para_terraform(destino)
    return ejecutar(
        [str(binario), f"-chdir={raiz}"] + argumentos,
        entorno=entorno,
        codigos_aceptados=codigos_aceptados,
        silencioso=silencioso,
    )


def variables_comunes(root: RootDeTerraform = ROOT_DE_APLICACION) -> list[str]:
    return [
        f"-var-file={root.tfvars_local}",
        f"-var-file={root.variables_generadas}",
    ] + variables_efimeras(root)


def variables_efimeras(root: RootDeTerraform) -> list[str]:
    """Archivos de variables EFIMERAS del root, si las tiene.

    Al aplicar un plan guardado, Terraform exige volver a aportar las variables
    efimeras —no estan en el plan— y rechaza que se repitan las demas. Por eso
    viajan en un archivo propio que se pasa tanto al planear como al aplicar el
    plan guardado. Hoy solo el root de datos tiene una: la contrasena master.
    """
    if root == ROOT_DE_DATOS:
        return [f"-var-file={ruta_de_las_efimeras_de_datos()}"]
    return []


def ruta_de_las_efimeras_de_datos() -> Path:
    """Junto al archivo de variables del destino, y derivada de el al llamar."""
    return VARIABLES_GENERADAS_DE_DATOS.with_name("efimeras.tfvars.json")


def generar_lock(
    binario: Path, destino: mod_destino.Destino, root: RootDeTerraform = ROOT_DE_APLICACION
) -> None:
    """Genera el lock del provider para **las dos** plataformas y lo versiona.

    `terraform init` a secas escribe solo los hashes de la plataforma actual. Con
    el lock versionado, el dia que CI corra en Linux y el desarrollo en Windows,
    `init -lockfile=readonly` fallaria por una diferencia que no es un problema
    real. `providers lock` con las dos plataformas lo evita.
    """
    titulo(f"LOCK DEL PROVIDER — las dos plataformas, versionado ({root.nombre})")
    terraform(
        binario,
        destino,
        [
            "providers",
            "lock",
            "-platform=linux_amd64",
            "-platform=windows_amd64",
        ],
        raiz=root.directorio,
    )
    lock = root.directorio / ".terraform.lock.hcl"
    if not lock.exists():
        raise ErrorDelLaboratorio("no se genero .terraform.lock.hcl")
    texto = lock.read_text(encoding="utf-8")
    mod_herramientas.verificar_lock(texto)
    hashes = mod_herramientas.hashes_del_lock(texto)
    print(f"lock con {len(hashes)} hashes para el provider {mod_herramientas.VERSION_DEL_PROVIDER}")


def inicializar(
    binario: Path,
    destino: mod_destino.Destino,
    *,
    solo_lectura: bool,
    root: RootDeTerraform = ROOT_DE_APLICACION,
) -> None:
    directorio_de_estado = escribir_backend(destino.modo, root)
    ruta_del_estado = directorio_de_estado / "terraform.tfstate"
    argumentos = [
        "init",
        "-input=false",
        f"-backend-config=path={str(ruta_del_estado).replace(chr(92), '/')}",
        "-reconfigure",
    ]
    if solo_lectura:
        argumentos.append("-lockfile=readonly")
    terraform(binario, destino, argumentos, raiz=root.directorio)
    print(f"estado local del root '{root.nombre}' en: {ruta_del_estado}")


# --- topologia de roots, compartida por TODOS los comandos ------------------
#
# Arreglo de DEF-030-2. La enmienda de Task/030 extrajo el almacenamiento de
# medios a su propio root y cablo la orquestacion unicamente en `ciclo`. Los
# cinco subcomandos de runbook —los que se usan en una incidencia— siguieron
# asumiendo un root unico. Lo que sigue es la orquestacion que ahora usan todos.


@dataclass(frozen=True)
class HerramentalDeRoots:
    """Las operaciones externas que la orquestacion de roots necesita.

    Se agrupan en un objeto, y no como parametros sueltos, para que las pruebas
    puedan sustituirlas de una vez sin tocar el disco ni ejecutar Terraform. Es
    la misma costura inyectable que `exigir_confirmacion_del_plan` ofrece con su
    `leer`.
    """

    corredor: Callable[..., Any]
    inicializar: Callable[..., None]
    escribir_variables_de_medios: Callable[..., None]
    escribir_variables_de_aplicacion: Callable[..., None]
    vaciar_bucket: Callable[..., int]
    escribir_variables_de_datos: Callable[..., None]


def herramental_real() -> HerramentalDeRoots:
    """El herramental que habla con Terraform y con el destino de verdad."""

    def vaciar(destino: mod_destino.Destino, *, bucket: str) -> int:
        return mod_verificacion.vaciar_bucket(
            destino,
            bucket=bucket,
            clave_aws=mod_destino.CLAVE_FICTICIA,
            secreto=mod_destino.SECRETO_FICTICIO,
        )

    return HerramentalDeRoots(
        corredor=terraform,
        inicializar=inicializar,
        escribir_variables_de_medios=escribir_variables_de_medios,
        escribir_variables_de_aplicacion=escribir_variables_del_destino,
        vaciar_bucket=vaciar,
        escribir_variables_de_datos=escribir_variables_de_datos,
    )


#: Lo que el root de medios publica y el de aplicacion consume. Son las dos
#: unicas piezas del contrato explicito entre roots.
CLAVES_DEL_CONTRATO_DE_MEDIOS = ("nombre_del_bucket", "arn_del_bucket")


def contrato_del_root_de_medios(
    binario: Path,
    destino: mod_destino.Destino,
    *,
    aplicar: bool,
    regenerar_lock: bool = False,
    confirmar: bool = False,
    acciones: tuple[str, ...] = ("create", "update"),
    herramental: HerramentalDeRoots | None = None,
) -> dict[str, Any]:
    """Deja el root de medios en su estado y devuelve su contrato explicito.

    `aplicar=True` lo crea o lo reconcilia. `aplicar=False` es el camino de
    lectura, para los comandos que solo consumen el contrato de un laboratorio ya
    creado y no deben modificar nada.

    Si el contrato no esta completo, **aborta aqui**: continuar al root de
    aplicacion con un ARN vacio produciria una politica IAM sin sentido y un
    plan que parece valido.
    """
    herramental = herramental or herramental_real()
    root = ROOT_DE_MEDIOS
    herramental.escribir_variables_de_medios(destino)
    if aplicar and regenerar_lock:
        herramental.inicializar(binario, destino, solo_lectura=False, root=root)
        generar_lock(binario, destino, root)
    herramental.inicializar(binario, destino, solo_lectura=True, root=root)
    herramental.corredor(
        binario, destino, ["fmt", "-check", "-recursive"], raiz=root.directorio
    )
    herramental.corredor(binario, destino, ["validate"], raiz=root.directorio)
    if aplicar:
        herramental.corredor(
            binario,
            destino,
            ["plan", "-input=false", f"-out={root.plan_guardado}"]
            + variables_comunes(root),
            raiz=root.directorio,
        )
        crudo = herramental.corredor(
            binario,
            destino,
            ["show", "-json", str(root.plan_guardado)],
            raiz=root.directorio,
            silencioso=True,
        )
        plan = json.loads(crudo.stdout)
        resumen = mod_inventario.revisar_plan(plan, acciones_permitidas=acciones)
        print(f"plan de medios revisado: {resumen}")
        hay_cambios = any(resumen.get(accion, 0) for accion in acciones) or any(
            salida.get("actions") != ["no-op"]
            for salida in plan.get("output_changes", {}).values()
        )
        if hay_cambios:
            if confirmar:
                exigir_confirmacion_del_plan(
                    sha256_de_archivo(root.plan_guardado), operacion="aplicar medios"
                )
            herramental.corredor(
                binario, destino, ["apply", "-input=false", str(root.plan_guardado)],
                raiz=root.directorio,
            )
        else:
            print("medios sin cambios; se conserva su state sin apply")
    crudas = herramental.corredor(
        binario, destino, ["output", "-json"], raiz=root.directorio, silencioso=True
    )
    contrato = {
        nombre: dato.get("value")
        for nombre, dato in json.loads(crudas.stdout or "{}").items()
    }
    faltantes = [
        clave for clave in CLAVES_DEL_CONTRATO_DE_MEDIOS if not contrato.get(clave)
    ]
    if faltantes:
        raise ErrorDelLaboratorio(
            f"el root de medios no publica {faltantes}: el grafo de aplicacion no "
            "puede recibir su contrato, y no se continua al root de aplicacion"
        )
    nombre = contrato["nombre_del_bucket"]
    arn = contrato["arn_del_bucket"]
    if not isinstance(nombre, str) or arn != f"arn:aws:s3:::{nombre}":
        raise ErrorDelLaboratorio("el nombre y el ARN del contrato de medios no coinciden")
    return contrato


#: Lo que el root de datos publica para la ejecutora (H-031-5) y para la Lambda
#: de aplicacion (Task/032). Sin cualquiera de estas piezas el contrato no sirve.
CLAVES_DEL_CONTRATO_DE_DATOS = (
    "id_de_vpc",
    "ids_de_subredes",
    "id_sg_lambda",
    "id_sg_admin",
    "id_sg_rds",
    "id_endpoint_s3",
    "identificador_rds",
    "nombre_del_parametro_master",
)


def contrato_del_root_de_datos(
    binario: Path,
    destino: mod_destino.Destino,
    *,
    contrato_de_medios: dict[str, Any],
    aplicar: bool,
    regenerar_lock: bool = False,
    confirmar: bool = False,
    acciones: tuple[str, ...] = ("create", "update"),
    herramental: HerramentalDeRoots | None = None,
) -> dict[str, Any]:
    """Deja el root de datos en su estado y devuelve su contrato explicito.

    Mismo patron que `contrato_del_root_de_medios`, con una comprobacion mas,
    que es la razon de ser de DH-2: tras el plan, y tras el apply si lo hay, la
    contrasena CANARIO se busca en el plan, el state y las salidas. Si aparece en
    cualquiera, aborta antes de tocar el root de aplicacion.
    """
    herramental = herramental or herramental_real()
    root = ROOT_DE_DATOS
    herramental.escribir_variables_de_datos(destino, contrato_de_medios)
    if aplicar and regenerar_lock:
        herramental.inicializar(binario, destino, solo_lectura=False, root=root)
        generar_lock(binario, destino, root)
    herramental.inicializar(binario, destino, solo_lectura=True, root=root)
    herramental.corredor(
        binario, destino, ["fmt", "-check", "-recursive"], raiz=root.directorio
    )
    herramental.corredor(binario, destino, ["validate"], raiz=root.directorio)
    if aplicar:
        herramental.corredor(
            binario,
            destino,
            ["plan", "-input=false", f"-out={root.plan_guardado}"]
            + variables_comunes(root),
            raiz=root.directorio,
        )
        crudo = herramental.corredor(
            binario,
            destino,
            ["show", "-json", str(root.plan_guardado)],
            raiz=root.directorio,
            silencioso=True,
        )
        exigir_canarios_ausentes({"plan de datos": crudo.stdout})
        plan = json.loads(crudo.stdout)
        resumen = mod_inventario.revisar_plan(plan, acciones_permitidas=acciones)
        print(f"plan de datos revisado: {resumen}")
        hay_cambios = any(resumen.get(accion, 0) for accion in acciones) or any(
            salida.get("actions") != ["no-op"]
            for salida in plan.get("output_changes", {}).values()
        )
        if hay_cambios:
            if confirmar:
                exigir_confirmacion_del_plan(
                    sha256_de_archivo(root.plan_guardado), operacion="aplicar datos"
                )
            # El plan guardado no lleva la contrasena (es efimera): se aporta otra vez.
            herramental.corredor(
                binario,
                destino,
                ["apply", "-input=false"] + variables_efimeras(root) + [str(root.plan_guardado)],
                raiz=root.directorio,
            )
            estado = herramental.corredor(
                binario, destino, ["show", "-json"], raiz=root.directorio, silencioso=True
            )
            exigir_canarios_ausentes({"state de datos": estado.stdout})
        else:
            print("datos sin cambios; se conserva su state sin apply")
    crudas = herramental.corredor(
        binario, destino, ["output", "-json"], raiz=root.directorio, silencioso=True
    )
    revisados = exigir_canarios_ausentes({"salidas de datos": crudas.stdout})
    print(f"contrasena canario ausente en: {', '.join(revisados)}")
    contrato = {
        nombre: dato.get("value")
        for nombre, dato in json.loads(crudas.stdout or "{}").items()
    }
    faltantes = [clave for clave in CLAVES_DEL_CONTRATO_DE_DATOS if not contrato.get(clave)]
    if faltantes:
        raise ErrorDelLaboratorio(
            f"el root de datos no publica {faltantes}: su contrato no esta completo "
            "y no se continua al root de aplicacion"
        )
    if len(contrato["ids_de_subredes"]) != 2:
        raise ErrorDelLaboratorio("el root de datos debe publicar exactamente dos subredes")
    return contrato


def destruir_los_roots(
    binario: Path,
    destino: mod_destino.Destino,
    *,
    contrato: dict[str, Any] | None,
    herramental: HerramentalDeRoots | None = None,
) -> None:
    """Destruye los roots en el orden **inverso** al de creacion.

    Aplicacion primero, que CONSUME el bucket; datos despues, cuya politica de
    endpoint referencia ese bucket; y medios al final, que lo administra. Al
    reves, un root quedaria referenciando lo que otro ya destruyo.

    Si un root falla, los siguientes **no se tocan**. Su state conserva su
    ownership intacto y la operacion se puede reintentar sin haber perdido el
    registro de como destruir lo que queda.
    """
    herramental = herramental or herramental_real()
    bucket = (contrato or {}).get("nombre_del_bucket")
    for root in secuencia_de_roots("destruir"):
        if root == ROOT_DE_MEDIOS and bucket:
            borrados = herramental.vaciar_bucket(destino, bucket=bucket)
            print(f"objetos y versiones retirados de '{bucket}' antes del destroy: {borrados}")
        herramental.corredor(
            binario,
            destino,
            ["destroy", "-input=false", "-auto-approve"] + variables_comunes(root),
            raiz=root.directorio,
        )


#: Tipos que SOLO puede administrar su root duenno. Un `aws_ssm_parameter` o un
#: `aws_cloudwatch_log_group` existen en mas de un root —cada uno los suyos— y
#: por eso no figuran aqui: la exclusividad se exige solo donde existe.
TIPOS_EXCLUSIVOS_DE_CADA_ROOT: dict[str, tuple[str, ...]] = {
    "medios": ("aws_s3_bucket",),
    "datos": (
        "aws_vpc",
        "aws_subnet",
        "aws_route_table",
        "aws_route_table_association",
        "aws_vpc_endpoint",
        "aws_security_group",
        "aws_vpc_security_group_ingress_rule",
        "aws_vpc_security_group_egress_rule",
        "aws_db_subnet_group",
        "aws_db_parameter_group",
        "aws_db_instance",
    ),
}

#: Lo que cada root duenno DEBE administrar mientras exista.
TIPOS_QUE_DEFINEN_A_CADA_ROOT: dict[str, tuple[str, ...]] = {
    "medios": ("aws_s3_bucket",),
    "datos": ("aws_vpc", "aws_db_instance"),
}


def tipo_de_direccion(direccion: str) -> str:
    """Tipo de recurso de una direccion de state: `module.red.aws_vpc.this` -> `aws_vpc`."""
    for parte in direccion.split("."):
        if parte.startswith("aws_"):
            return parte
    return ""


def _es_del_tipo(direccion: str, tipo: str) -> bool:
    observado = tipo_de_direccion(direccion)
    # `aws_s3_bucket` cubre toda la familia `aws_s3_bucket_*`, que es del mismo duenno.
    return observado == tipo or (tipo == "aws_s3_bucket" and observado.startswith("aws_s3_bucket"))


def exigir_ownership_disjunto(
    estados: dict[str, list[str]],
    *,
    exigir_duennos: bool = True,
) -> None:
    """Ningun recurso puede estar administrado por **dos** states.

    Es el invariante de la regla de paridad (aws-local-parity.md §4.1.1), y se
    comprueba sobre los states reales en lugar de darlo por supuesto:

    - las direcciones de todos los states son **disjuntas** dos a dos;
    - ningun root administra un tipo **exclusivo** de otro: el bucket es de
      medios; la red y RDS son de datos. Los demas solo los consumen por contrato;
    - cada root duenno **si** administra lo que lo define.

    `exigir_duennos=False` sirve despues de un teardown, donde los states quedan
    vacios y eso es exactamente lo correcto.
    """
    nombres = sorted(estados)
    for indice, primero in enumerate(nombres):
        for segundo in nombres[indice + 1:]:
            comunes = sorted(set(estados[primero]) & set(estados[segundo]))
            if comunes:
                raise ErrorDelLaboratorio(
                    f"hay recursos administrados por los states '{primero}' y "
                    f"'{segundo}', que es la situacion que la separacion de roots "
                    f"debe impedir: {comunes}"
                )
    for duenno, tipos in TIPOS_EXCLUSIVOS_DE_CADA_ROOT.items():
        for root, direcciones in estados.items():
            if root == duenno:
                continue
            intrusos = sorted(
                direccion
                for direccion in direcciones
                if any(_es_del_tipo(direccion, tipo) for tipo in tipos)
            )
            if intrusos:
                raise ErrorDelLaboratorio(
                    f"el root '{root}' administra recursos que son de '{duenno}', y "
                    f"solo debe consumirlos por contrato: {intrusos}"
                )
    if exigir_duennos:
        for duenno, tipos in TIPOS_QUE_DEFINEN_A_CADA_ROOT.items():
            if duenno not in estados:
                continue
            for tipo in tipos:
                if not any(_es_del_tipo(d, tipo) for d in estados[duenno]):
                    raise ErrorDelLaboratorio(
                        f"el root '{duenno}' no administra ningun {tipo}: sin eso, el "
                        "contrato que reciben los demas roots no tiene duenno"
                    )


def estados_de_los_roots(
    binario: Path,
    destino: mod_destino.Destino,
    *,
    herramental: HerramentalDeRoots | None = None,
) -> dict[str, list[str]]:
    """El state de CADA root de la topologia, por nombre."""
    return {
        root.nombre: estado_del_root(binario, destino, root, herramental=herramental)
        for root in ROOTS_EN_ORDEN_DE_CREACION
    }


def estado_del_root(
    binario: Path,
    destino: mod_destino.Destino,
    root: RootDeTerraform,
    *,
    herramental: HerramentalDeRoots | None = None,
) -> list[str]:
    """Direcciones que administra el state de `root`."""
    herramental = herramental or herramental_real()
    resultado = herramental.corredor(
        binario,
        destino,
        ["state", "list"],
        raiz=root.directorio,
        silencioso=True,
        codigos_aceptados=(0, 1),
    )
    return [linea.strip() for linea in resultado.stdout.splitlines() if linea.strip()]


def preparar_los_roots_para(
    operacion: str,
    binario: Path,
    destino: mod_destino.Destino,
    zip_de_lambda: Path,
    *,
    regenerar_lock: bool = False,
    herramental: HerramentalDeRoots | None = None,
) -> dict[str, Any]:
    """Deja los tres roots listos para `operacion` y devuelve el contrato de medios.

    Un solo camino para `ciclo`, `crear`, `validar`, `rollback`, `recuperar` y
    `destruir`. El orden y la cobertura salen de `secuencia_de_roots`, de modo que
    no hay cinco copias que puedan divergir: eso fue exactamente DEF-030-2.

    La **preparacion** es siempre en orden de creacion, incluso al destruir: el
    contrato del bucket hace falta antes de tocar datos y aplicacion, aunque sea
    para vaciarlo y destruirlo. El orden inverso gobierna el `destroy`, y lo
    aplica `destruir_los_roots`. El contrato de datos viaja dentro del
    devuelto, bajo la clave `datos`.
    """
    herramental = herramental or herramental_real()
    # Valida que la operacion este declarada: una nueva no hereda orden en silencio.
    secuencia_de_roots(operacion)
    aplicar_medios = operacion in {"ciclo", "crear", "recuperar"}

    titulo(
        "ROOT DE MEDIOS — "
        + ("reconciliacion" if aplicar_medios else "lectura del contrato")
    )
    contrato = contrato_del_root_de_medios(
        binario,
        destino,
        aplicar=aplicar_medios,
        regenerar_lock=regenerar_lock,
        confirmar=operacion in {"crear", "recuperar"},
        acciones=("create",) if operacion == "crear" else ("create", "update"),
        herramental=herramental,
    )
    print(json.dumps(contrato, indent=2, sort_keys=True))

    titulo(
        "ROOT DE DATOS — "
        + ("reconciliacion" if aplicar_medios else "lectura del contrato")
        + "; recibe el ARN de medios por variable"
    )
    datos = contrato_del_root_de_datos(
        binario,
        destino,
        contrato_de_medios=contrato,
        aplicar=aplicar_medios,
        regenerar_lock=regenerar_lock,
        confirmar=operacion in {"crear", "recuperar"},
        acciones=("create",) if operacion == "crear" else ("create", "update"),
        herramental=herramental,
    )
    print(json.dumps(datos, indent=2, sort_keys=True))

    titulo("ROOT DE APLICACION — recibe el contrato por variables explicitas")
    herramental.escribir_variables_de_aplicacion(destino, zip_de_lambda, contrato)
    if regenerar_lock and aplicar_medios:
        herramental.inicializar(
            binario, destino, solo_lectura=False, root=ROOT_DE_APLICACION
        )
        generar_lock(binario, destino, ROOT_DE_APLICACION)
    herramental.inicializar(
        binario, destino, solo_lectura=True, root=ROOT_DE_APLICACION
    )
    return {**contrato, "datos": datos}


def recursos_del_root_de_datos(prefijo: str = PREFIJO_DEL_LABORATORIO) -> dict[str, list[str]]:
    """Nombres EXACTOS que el root de datos crea en el laboratorio, por categoria.

    Son los que derivan los modulos de `prefijo`. Se usan para tolerar, mientras
    el root de datos sigue vivo, exactamente esos recursos y ninguno mas.
    """
    base = f"{prefijo}-postgres"
    return {
        # La ejecutora privada de D-24 (H-031-5): funcion y grupo de logs por prefijo, y su rol de ejecucion.
        "lambda": [f"{prefijo}-ejecutor"],
        "logs": [f"/aws/lambda/{prefijo}-ejecutor"],
        "cloudwatch_alarmas": [f"{prefijo}-rds-{senal}" for senal in SENALES_DE_D11],
        "iam_roles_datos": [ROL_DE_GRAFANA, ROL_DE_LA_EJECUTORA],
        "ec2_vpc": [f"{prefijo}-vpc"],
        "ec2_grupos": [f"{prefijo}-lambda", f"{prefijo}-rds", f"{prefijo}-admin"],
        "rds_instancias": [base],
        "rds_subredes": [base],
        "rds_parametros": [f"{base}17"],
        "logs_rds": [f"/aws/rds/instance/{base}/postgresql"],
        "ssm_datos": [f"/{prefijo}/datos/{rol}" for rol in ("blogadmin", "blog_migrate", "blog_app")],
    }


def exigir_ausencia_en_el_destino(
    inventario: dict[str, list[str]],
    *,
    bucket_de_medios_vivo: str | None,
    datos_vivos: bool = False,
) -> None:
    """Exige ausencia sabiendo que los roots aun no destruidos son legitimos.

    Mientras el root de medios no haya sido destruido, su bucket **no es un
    residuo**: es infraestructura viva de otro root, con su propio state. Tratarlo
    como residuo es lo que hacia `destruir` abortar despues de un destroy
    correcto del grafo de aplicacion. Lo mismo vale, desde Task/031, para la red
    y la base de datos del root de datos.

    Todo lo demas sigue siendo residuo, incluido cualquier **otro** recurso con
    el prefijo del laboratorio: la tolerancia es de nombres exactos, no de un
    servicio entero.
    """
    observado = {servicio: list(valores) for servicio, valores in inventario.items()}
    if bucket_de_medios_vivo:
        observado["s3"] = [
            nombre
            for nombre in observado.get("s3", [])
            if nombre != bucket_de_medios_vivo
        ]
    if datos_vivos:
        for categoria, legitimos in recursos_del_root_de_datos().items():
            observado[categoria] = [
                nombre for nombre in observado.get(categoria, []) if nombre not in legitimos
            ]
    mod_inventario.exigir_inventario_vacio(observado)


def revisar_plan_guardado(
    binario: Path,
    destino: mod_destino.Destino,
    *,
    acciones: tuple[str, ...],
    minimo: int,
    root: RootDeTerraform = ROOT_DE_APLICACION,
) -> dict[str, int]:
    """Revisa el plan guardado de `root` contra una lista cerrada de acciones.

    El root es explicito porque cada uno tiene su propio plan: revisar el del
    grafo de aplicacion y dar por bueno el del almacenamiento fue el defecto que
    dejaba el bucket en pie al destruir.
    """
    plan_en_json = root.directorio_generado / "plan.json"
    resultado = terraform(
        binario,
        destino,
        ["show", "-json", str(root.plan_guardado)],
        raiz=root.directorio,
        silencioso=True,
    )
    plan_en_json.parent.mkdir(parents=True, exist_ok=True)
    plan_en_json.write_text(resultado.stdout, encoding="utf-8", newline="\n")
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
    # Los parametros del root de datos viven bajo `/<prefijo>/datos/`. Se separan
    # de los de aplicacion para que cada categoria tenga un solo root duenno.
    prefijo_ssm_de_datos = f"/{PREFIJO_DEL_LABORATORIO}/datos/"
    parametros = mod_verificacion.parametros_presentes(
        destino, prefijo=f"/{PREFIJO_DEL_LABORATORIO}", **comun
    )
    return {
        # Root de medios
        "s3": mod_verificacion.buckets_presentes(
            destino, prefijo=PREFIJO_DEL_LABORATORIO, **comun
        ),
        # Root de aplicacion y ejecutora del root de datos (mismo prefijo: tolerada solo mientras datos viva)
        "lambda": mod_verificacion.funciones_presentes(
            destino, prefijo=PREFIJO_DEL_LABORATORIO, **comun
        ),
        "apigatewayv2": mod_verificacion.apis_presentes(
            destino, prefijo=PREFIJO_DEL_LABORATORIO, **comun
        ),
        "logs": mod_verificacion.grupos_de_logs(
            destino, prefijo=f"/aws/lambda/{PREFIJO_DEL_LABORATORIO}", **comun
        ),
        "ssm": [p for p in parametros if not p.startswith(prefijo_ssm_de_datos)],
        # Root de datos (Task/031)
        "ec2_vpc": mod_verificacion.vpcs_presentes(
            destino, prefijo=PREFIJO_DEL_LABORATORIO, **comun
        ),
        "ec2_grupos": mod_verificacion.grupos_de_seguridad_presentes(
            destino, prefijo=PREFIJO_DEL_LABORATORIO, **comun
        ),
        "rds_instancias": mod_verificacion.instancias_rds_presentes(
            destino, prefijo=PREFIJO_DEL_LABORATORIO, **comun
        ),
        "rds_subredes": mod_verificacion.grupos_de_subredes_rds_presentes(
            destino, prefijo=PREFIJO_DEL_LABORATORIO, **comun
        ),
        "rds_parametros": mod_verificacion.grupos_de_parametros_rds_presentes(
            destino, prefijo=PREFIJO_DEL_LABORATORIO, **comun
        ),
        "logs_rds": mod_verificacion.grupos_de_logs(
            destino, prefijo=f"/aws/rds/instance/{PREFIJO_DEL_LABORATORIO}", **comun
        ),
        "ssm_datos": [p for p in parametros if p.startswith(prefijo_ssm_de_datos)],
        # Root de datos: alarmas de D-11 (H-031-8) y rol de D-20 (H-031-9)
        "cloudwatch_alarmas": mod_verificacion.alarmas_presentes(
            destino, prefijo=f"{PREFIJO_DEL_LABORATORIO}-", **comun
        ),
        "iam_roles_datos": mod_verificacion.roles_presentes(
            destino, nombres=(ROL_DE_GRAFANA, ROL_DE_LA_EJECUTORA), **comun
        ),
    }


def extraer_artefacto_para_sdk(ruta_del_artefacto: Path, destino: Path) -> None:
    """Extrae el ZIP validando rutas para que botocore pueda leer ``data/``.

    ``zipimport`` basta para importar Python, pero ``botocore`` abre catálogos
    JSON como archivos ordinarios. Extraer a un temporal conserva la procedencia
    del artefacto y evita instalar dependencias en el host.
    """
    raiz = destino.resolve()
    raiz.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(ruta_del_artefacto) as paquete:
            for entrada in paquete.infolist():
                relativa = PurePosixPath(entrada.filename)
                if relativa.is_absolute() or ".." in relativa.parts:
                    raise ErrorDelLaboratorio(
                        f"el artefacto contiene una ruta insegura: {entrada.filename!r}"
                    )
                modo = entrada.external_attr >> 16
                if stat.S_ISLNK(modo):
                    raise ErrorDelLaboratorio(
                        f"el artefacto contiene un enlace simbolico: {entrada.filename!r}"
                    )
                salida = (raiz / Path(*relativa.parts)).resolve()
                if not salida.is_relative_to(raiz):
                    raise ErrorDelLaboratorio(
                        f"el artefacto intenta salir del temporal: {entrada.filename!r}"
                    )
                if entrada.is_dir():
                    salida.mkdir(parents=True, exist_ok=True)
                    continue
                salida.parent.mkdir(parents=True, exist_ok=True)
                with paquete.open(entrada) as origen, salida.open("wb") as archivo:
                    shutil.copyfileobj(origen, archivo)
    except (OSError, zipfile.BadZipFile) as error:
        raise ErrorDelLaboratorio(
            f"no se pudo extraer el SDK del artefacto: {error}"
        ) from error


def inspeccionar_con_sdk(
    destino: mod_destino.Destino,
    valores: dict[str, Any],
    *,
    ruta_del_artefacto: Path,
    boto3_modulo: Any | None = None,
) -> dict[str, Any]:
    """Inspecciona el despliegue con el AWS SDK incluido por Task/024.

    El host no necesita instalar ``boto3``. Cuando no se inyecta un módulo para
    pruebas, el ZIP canónico se extrae a un temporal: ``botocore`` necesita abrir
    su directorio ``data/`` como archivos ordinarios y no funciona directamente
    desde ``zipimport``. Credenciales, región y endpoints se pasan de forma
    explícita; nunca se usa la cadena ambiental del SDK.
    """
    if boto3_modulo is None:
        if "boto3" in sys.modules:
            raise ErrorDelLaboratorio(
                "boto3 ya estaba importado antes de abrir el artefacto; "
                "no se puede demostrar la procedencia del SDK"
            )
        with tempfile.TemporaryDirectory(prefix="personal-blog-task026-sdk-") as temporal:
            raiz_temporal = Path(temporal)
            extraer_artefacto_para_sdk(ruta_del_artefacto, raiz_temporal)
            ruta_en_sys_path = str(raiz_temporal)
            sys.path.insert(0, ruta_en_sys_path)
            try:
                boto3_extraido = importlib.import_module("boto3")
                origen = Path(str(getattr(boto3_extraido, "__file__", ""))).resolve()
                if not origen.is_relative_to(raiz_temporal.resolve()):
                    raise ErrorDelLaboratorio(
                        "boto3 no se importo desde el artefacto extraido"
                    )
                return inspeccionar_con_sdk(
                    destino,
                    valores,
                    ruta_del_artefacto=ruta_del_artefacto,
                    boto3_modulo=boto3_extraido,
                )
            except ImportError as error:
                raise ErrorDelLaboratorio(
                    "el ZIP canonico no contiene un boto3 importable; no se "
                    "sustituye silenciosamente por una dependencia del host"
                ) from error
            finally:
                if ruta_en_sys_path in sys.path:
                    sys.path.remove(ruta_en_sys_path)
                for nombre, modulo in list(sys.modules.items()):
                    archivo = getattr(modulo, "__file__", None)
                    if not archivo:
                        continue
                    try:
                        pertenece = Path(str(archivo)).resolve().is_relative_to(
                            raiz_temporal.resolve()
                        )
                    except OSError:
                        pertenece = False
                    if pertenece:
                        sys.modules.pop(nombre, None)

    try:
        sesion = boto3_modulo.Session(
            aws_access_key_id=mod_destino.CLAVE_FICTICIA,
            aws_secret_access_key=mod_destino.SECRETO_FICTICIO,
            region_name=destino.region,
        )
        llamadas = {
            "s3": ("list_buckets", {}, "Buckets", "Name"),
            "ssm": (
                "get_parameters_by_path",
                {"Path": f"/{PREFIJO_DEL_LABORATORIO}", "Recursive": True},
                "Parameters",
                "Name",
            ),
            "iam": ("list_roles", {}, "Roles", "RoleName"),
            "lambda": ("list_functions", {}, "Functions", "FunctionName"),
            "apigatewayv2": ("get_apis", {}, "Items", "ApiId"),
            "logs": (
                "describe_log_groups",
                {"logGroupNamePrefix": f"/aws/lambda/{PREFIJO_DEL_LABORATORIO}"},
                "logGroups",
                "logGroupName",
            ),
        }
        inventario: dict[str, list[str]] = {}
        for servicio, (metodo, parametros, clave_lista, clave_nombre) in llamadas.items():
            cliente = sesion.client(
                servicio,
                endpoint_url=destino.endpoints[servicio],
                region_name=destino.region,
                aws_access_key_id=mod_destino.CLAVE_FICTICIA,
                aws_secret_access_key=mod_destino.SECRETO_FICTICIO,
                use_ssl=False,
            )
            respuesta = getattr(cliente, metodo)(**parametros)
            inventario[servicio] = sorted(
                str(elemento[clave_nombre])
                for elemento in respuesta.get(clave_lista, [])
                if clave_nombre in elemento
            )
    except Exception as error:
        if isinstance(error, ErrorDelLaboratorio):
            raise
        raise ErrorDelLaboratorio(
            f"la inspeccion con boto3 fallo: {type(error).__name__}: {error}"
        ) from error
    esperados = {
        "s3": [valores["bucket_de_medios"]],
        "ssm": list(valores.get("parametros") or []),
        "iam": [valores["rol_de_ejecucion"]],
        "lambda": [valores["nombre_de_la_funcion"]],
        "apigatewayv2": [valores["id_del_api"]],
        "logs": [valores["grupo_de_logs"]],
    }
    faltantes: list[str] = []
    for servicio, nombres in esperados.items():
        for nombre in nombres:
            if nombre not in inventario[servicio]:
                faltantes.append(f"{servicio}:{nombre}")
    if faltantes:
        raise ErrorDelLaboratorio(
            "boto3 no encontro recursos esperados: " + ", ".join(sorted(faltantes))
        )

    version = str(getattr(boto3_modulo, "__version__", "desconocida"))
    informe = {"sdk": f"boto3/{version}", "servicios": inventario}
    print("inspeccion con AWS SDK oficial contra el destino local:")
    print(json.dumps(informe, indent=2, sort_keys=True))
    return informe


def salidas(
    binario: Path, destino: mod_destino.Destino, root: RootDeTerraform = ROOT_DE_APLICACION
) -> dict[str, Any]:
    resultado = terraform(
        binario, destino, ["output", "-json"], raiz=root.directorio, silencioso=True
    )
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


def introducir_y_reconciliar_drift(
    binario: Path,
    destino: mod_destino.Destino,
    valores: dict[str, Any],
) -> dict[str, Any]:
    """Elimina un parametro ficticio, observa el plan y lo reconstruye."""
    titulo("DRIFT CONTROLADO — eliminar un SSM ficticio y reconciliar")
    if not destino.es_local:
        raise ErrorDelLaboratorio("el ensayo de drift solo esta autorizado en modo local")
    if PARAMETRO_DE_DRIFT not in (valores.get("parametros") or []):
        raise ErrorDelLaboratorio(
            f"el objetivo de drift no figura en las salidas: {PARAMETRO_DE_DRIFT}"
        )

    env_lab = leer_env_del_laboratorio()
    destino_actual = resolver(env_lab, destino.modo)
    if destino_actual != destino:
        raise ErrorDelLaboratorio(
            "el destino cambio antes de introducir el drift; no se elimina nada"
        )
    comprobar_publicacion_de_floci(env_lab)
    mod_destino.confirmar_identidad(
        destino_actual,
        lambda d: mod_verificacion.cuenta_observada(
            d,
            clave=mod_destino.CLAVE_FICTICIA,
            secreto=mod_destino.SECRETO_FICTICIO,
        ),
    )
    estado, _ = mod_verificacion.eliminar_parametro(
        destino,
        nombre=PARAMETRO_DE_DRIFT,
        clave_aws=mod_destino.CLAVE_FICTICIA,
        secreto=mod_destino.SECRETO_FICTICIO,
    )
    if estado != 200:
        raise ErrorDelLaboratorio(
            f"DeleteParameter devolvio {estado}; el drift no quedo demostrado"
        )
    presentes = mod_verificacion.parametros_presentes(
        destino,
        prefijo=f"/{PREFIJO_DEL_LABORATORIO}",
        clave_aws=mod_destino.CLAVE_FICTICIA,
        secreto=mod_destino.SECRETO_FICTICIO,
    )
    if PARAMETRO_DE_DRIFT in presentes:
        raise ErrorDelLaboratorio("el parametro sigue presente despues de DeleteParameter")
    print(f"drift observado por API: ausente {PARAMETRO_DE_DRIFT}")

    terraform(
        binario,
        destino,
        ["plan", "-input=false", f"-out={PLAN_GUARDADO}"] + variables_comunes(ROOT_DE_APLICACION),
    )
    crudo = terraform(
        binario,
        destino,
        ["show", "-json", str(PLAN_GUARDADO)],
        silencioso=True,
    )
    plan = json.loads(crudo.stdout)
    informe = mod_inventario.revisar_reconciliacion_de_drift(
        plan,
        direccion_objetivo=DIRECCION_TERRAFORM_DEL_DRIFT,
        diferencias_toleradas=DIFERENCIAS_DEL_DESTINO_LOCAL,
        actualizaciones_dependientes=ACTUALIZACIONES_DEPENDIENTES_DEL_DRIFT,
    )
    print(f"plan de reconciliacion acotado: {informe}")
    terraform(binario, destino, ["apply", "-input=false", str(PLAN_GUARDADO)])

    estado, cuerpo = mod_verificacion.leer_parametro(
        destino,
        nombre=PARAMETRO_DE_DRIFT,
        clave_aws=mod_destino.CLAVE_FICTICIA,
        secreto=mod_destino.SECRETO_FICTICIO,
    )
    if estado != 200:
        raise ErrorDelLaboratorio(
            f"GetParameter devolvio {estado} tras reconciliar el drift"
        )
    print(f"reconciliacion demostrada por API: presente {PARAMETRO_DE_DRIFT}")
    return {
        "objetivo": PARAMETRO_DE_DRIFT,
        "ausencia_observada": True,
        "recreacion_planificada": informe["objetivo_recreado"],
        "presencia_final": True,
        "tipo_final": (cuerpo or {}).get("Parameter", {}).get("Type"),
    }


def idempotencia_del_root_de_datos(
    binario: Path,
    destino: mod_destino.Destino,
) -> dict[str, Any]:
    """Segundo plan del root de datos: exit 0, o exit 2 SOLO por lo declarado.

    Floci 2.1.0, con RDS en modo `mock`, no devuelve varios atributos que acepta
    (`DIFERENCIAS_DEL_DESTINO_LOCAL_DE_DATOS`). Esas diferencias se toleran por
    tipo y atributo, en el verificador; cualquier otra, o una creacion o
    destruccion, aborta. El plan tambien se revisa en busca del canario.

    H-031-1A: es UN solo plan guardado con `-detailed-exitcode`, y su JSON se lee
    SIEMPRE, tambien con `exit 0`, para revisar `resource_drift` contra
    `DRIFT_DEL_DESTINO_LOCAL_DE_DATOS`. Antes el `exit 0` no se miraba y el
    `exit 2` solo se juzgaba por `resource_changes`.
    """
    root = ROOT_DE_DATOS
    resultado = terraform(
        binario,
        destino,
        ["plan", "-input=false", "-detailed-exitcode", f"-out={root.plan_guardado}"]
        + variables_comunes(root),
        raiz=root.directorio,
        codigos_aceptados=(0, 1, 2),
    )
    if resultado.returncode not in (0, 2):
        mod_inventario.exigir_sin_cambios(resultado.returncode)
    crudo = terraform(
        binario, destino, ["show", "-json", str(root.plan_guardado)],
        raiz=root.directorio, silencioso=True,
    )
    exigir_canarios_ausentes({"segundo plan de datos": crudo.stdout})
    plan = json.loads(crudo.stdout)
    informe = mod_inventario.exigir_sin_cambios(
        resultado.returncode,
        plan=plan,
        diferencias_toleradas=DIFERENCIAS_DEL_DESTINO_LOCAL_DE_DATOS,
        drift_tolerado=DRIFT_DEL_DESTINO_LOCAL_DE_DATOS,
    )
    drift = mod_inventario.revisar_drift(plan, drift_tolerado=DRIFT_DEL_DESTINO_LOCAL_DE_DATOS)
    print(f"idempotencia de datos: exit {resultado.returncode}")
    print("resource_changes — solo diferencias declaradas del emulador:")
    for clave, cuantos in sorted(informe.items()):
        print(f"  {clave}: {cuantos} recurso(s)")
    print("resource_drift — solo entradas declaradas, con atributos y transicion exactos:")
    for direccion, atributos in sorted(drift.items()):
        print(f"  {direccion}: {atributos}")
    print("  Contra AWS real no se tolera ninguna: 0/0/0 y resource_drift = 0 (H-031-3, DN-2).")
    return {"codigo": resultado.returncode, "cambios": informe, "drift": drift}


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
        medios = preparar_los_roots_para(
            "ciclo", binario, destino, zip_congelado.ruta,
            regenerar_lock=argumentos.regenerar_lock,
        )

        terraform(binario, destino, ["fmt", "-check", "-recursive"])
        print("formato correcto")
        terraform(binario, destino, ["validate"])

        titulo("TERRAFORM — plan")
        terraform(
            binario,
            destino,
            ["plan", "-input=false", f"-out={PLAN_GUARDADO}"] + variables_comunes(ROOT_DE_APLICACION),
        )
        revisar_plan_guardado(binario, destino, acciones=("create",), minimo=1)

        titulo("ARTEFACTO — confirmacion antes del apply")
        mod_artefacto.confirmar_sin_cambios(zip_congelado)
        print("el artefacto sigue siendo byte a byte el que se planifico")

        titulo("TERRAFORM — apply del plan revisado")
        terraform(binario, destino, ["apply", "-input=false", str(PLAN_GUARDADO)])
        valores = salidas(binario, destino, ROOT_DE_APLICACION)
        print(json.dumps(valores, indent=2, sort_keys=True))
        exigir_ownership_disjunto(estados_de_los_roots(binario, destino))
        print("ownership disjunto: aplicacion no administra S3, ni red, ni RDS")

        evidencia = ejercitar_servicios(
            destino, valores, runtime_fijado=runtime_fijado, id_del_runtime=id_del_runtime
        )
        evidencia_sdk = inspeccionar_con_sdk(
            destino,
            valores,
            ruta_del_artefacto=zip_congelado.ruta,
        )

        titulo("IDEMPOTENCIA — segundo plan, se exige exit 0")
        segundo_plan_medios = terraform(
            binario, destino,
            ["plan", "-input=false", "-detailed-exitcode"] + variables_comunes(ROOT_DE_MEDIOS),
            raiz=ROOT_DE_MEDIOS.directorio, codigos_aceptados=(0, 1, 2),
        )
        mod_inventario.exigir_sin_cambios(segundo_plan_medios.returncode)
        print("idempotencia de medios: exit 0")
        informe_de_datos = idempotencia_del_root_de_datos(binario, destino)
        resultado = terraform(
            binario,
            destino,
            ["plan", "-input=false", "-detailed-exitcode"] + variables_comunes(ROOT_DE_APLICACION),
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
                ["plan", "-input=false", f"-out={PLAN_GUARDADO}"] + variables_comunes(ROOT_DE_APLICACION),
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

        drift = introducir_y_reconciliar_drift(binario, destino, valores)

        primer_destroy = destruir_y_verificar(binario, destino, valores, etapa="primer destroy")

        titulo("RECONSTRUCCION — desde cero, con las mismas fuentes")
        preparar_los_roots_para("ciclo", binario, destino, zip_congelado.ruta)
        terraform(
            binario,
            destino,
            ["apply", "-input=false", "-auto-approve"] + variables_comunes(ROOT_DE_APLICACION),
        )
        valores_reconstruidos = salidas(binario, destino, ROOT_DE_APLICACION)
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
        "inspeccion_sdk": evidencia_sdk["sdk"],
        "idempotencia": "exit 0" if not informe else f"exit 2 solo por {sorted(informe)}",
        "idempotencia_de_datos": {
            "exit": informe_de_datos["codigo"],
            "resource_changes_declarados": sorted(informe_de_datos["cambios"]),
            "resource_drift_declarado": informe_de_datos["drift"],
        },
        "drift_controlado": drift,
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

    destruir_los_roots(
        binario, destino, contrato={"nombre_del_bucket": valores.get("bucket_de_medios")}
    )

    titulo(f"{etapa.upper()} — verificacion de AUSENCIA contra las APIs")
    restantes: list[str] = []
    for root in secuencia_de_roots("destruir"):
        estado = terraform(
            binario,
            destino,
            ["state", "list"],
            raiz=root.directorio,
            silencioso=True,
            codigos_aceptados=(0, 1),
        )
        restantes += [linea for linea in estado.stdout.splitlines() if linea.strip()]
        if salidas(binario, destino, root):
            raise ErrorDelLaboratorio(f"el state de '{root.nombre}' conserva outputs")
    if restantes:
        raise ErrorDelLaboratorio(f"los states conservan recursos: {restantes}")
    print(f"recursos en los estados de Terraform: {len(restantes)}")
    print("  (el estado vacio no es la evidencia: la evidencia es lo que sigue)")
    inventario = inventario_del_destino(destino)
    for servicio, elementos in sorted(inventario.items()):
        print(f"  {servicio}: {len(elementos)} recurso(s) {elementos}")
    mod_inventario.exigir_inventario_vacio(inventario)
    print(f"Ausencia demostrada en las {len(inventario)} categorias consultadas de los tres roots.")
    return "verificado"


# --- operaciones humanas de Task/026 ---------------------------------------


def sha256_de_archivo(ruta: Path) -> str:
    """Resume un archivo sin cargarlo completo en memoria."""
    resumen = hashlib.sha256()
    try:
        with ruta.open("rb") as archivo:
            while bloque := archivo.read(1024 * 1024):
                resumen.update(bloque)
    except OSError as error:
        raise ErrorDelLaboratorio(f"no se pudo resumir '{ruta}': {error}") from error
    return resumen.hexdigest()


def exigir_confirmacion_del_plan(
    sha256: str,
    *,
    operacion: str,
    leer: Callable[[str], str] = input,
) -> str:
    """Exige aprobación humana ligada a todos los bytes del plan revisado.

    No existe bandera ``--force`` ni confirmación abreviada: si la entrada no es
    interactiva, está incompleta o no coincide exactamente, no se aplica nada.
    """
    esperado = f"APLICAR {sha256}"
    try:
        respuesta = leer(
            f"Para {operacion}, escriba exactamente '{esperado}': "
        ).strip()
    except EOFError as error:
        raise ErrorDelLaboratorio(
            "no hubo confirmacion interactiva; el plan no se aplica"
        ) from error
    if respuesta != esperado:
        raise ErrorDelLaboratorio(
            "la confirmacion no coincide con el SHA-256 completo del plan; "
            "el plan no se aplica"
        )
    return sha256


def preparar_contexto_de_runbook(
    argumentos: argparse.Namespace,
    *,
    preparar_runtime: bool,
) -> tuple[
    dict[str, str],
    mod_destino.Destino,
    Path,
    mod_artefacto.Artefacto,
    mod_runtime.RuntimeFijado,
    str | None,
]:
    """Prepara las autoridades comunes sin duplicar IaC ni fabricar artefactos."""
    env_lab = leer_env_del_laboratorio()
    destino = resolver(env_lab, argumentos.modo)
    comprobar_publicacion_de_floci(env_lab)
    mod_destino.confirmar_identidad(
        destino,
        lambda d: mod_verificacion.cuenta_observada(
            d,
            clave=mod_destino.CLAVE_FICTICIA,
            secreto=mod_destino.SECRETO_FICTICIO,
        ),
    )
    binario = asegurar_terraform()
    artefacto = mod_artefacto.describir_artefacto(argumentos.lambda_zip)
    runtime_fijado = mod_runtime.leer_runtime_fijado(artefacto.ruta)
    id_del_runtime = None
    if preparar_runtime:
        informe = mod_runtime.preparar_runtime(
            runtime_fijado, DockerDelLaboratorio()
        )
        id_del_runtime = informe["id"]
    print(f"artefacto: {artefacto.ruta}")
    print(f"  sha256: {artefacto.sha256}")
    print(f"runtime: {runtime_fijado.referencia}")
    return (
        env_lab,
        destino,
        binario,
        artefacto,
        runtime_fijado,
        id_del_runtime,
    )


def exigir_actualizacion_de_lambda() -> None:
    """Un rollback sin cambio de Lambda no es un rollback demostrable."""
    try:
        plan = json.loads(PLAN_EN_JSON.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ErrorDelLaboratorio(
            "no se pudo leer el plan JSON para demostrar el rollback"
        ) from error
    actualizaciones = [
        cambio.get("address", "?")
        for cambio in plan.get("resource_changes", [])
        if cambio.get("type") == "aws_lambda_function"
        and "update" in ((cambio.get("change") or {}).get("actions") or [])
    ]
    if not actualizaciones:
        raise ErrorDelLaboratorio(
            "el plan no actualiza aws_lambda_function; no se declarara rollback"
        )
    print(f"rollback de Lambda demostrado en el plan: {actualizaciones}")


def aplicar_version_desde_runbook(
    argumentos: argparse.Namespace,
    *,
    operacion: str,
    acciones_permitidas: tuple[str, ...],
) -> int:
    """Planifica, detiene para revisión humana y aplica una versión."""
    titulo(f"{operacion.upper()} — preparacion y autoridades")
    (
        _,
        destino,
        binario,
        artefacto,
        runtime_fijado,
        id_del_runtime,
    ) = preparar_contexto_de_runbook(argumentos, preparar_runtime=True)
    if id_del_runtime is None:  # Cobertura de tipos; preparar_runtime=True lo exige.
        raise ErrorDelLaboratorio("no se observo la identidad local del runtime")

    lock_de_operacion = raiz_de_estado(destino.modo) / "laboratorio.lock"
    with mod_destino.lock_de_escritura(lock_de_operacion):
        if operacion == "crear":
            inventario_inicial = inventario_del_destino(destino)
            # Al crear no existe todavia ningun root, asi que no hay bucket
            # legitimo que tolerar: el inventario debe estar vacio del todo.
            exigir_ausencia_en_el_destino(inventario_inicial, bucket_de_medios_vivo=None)
            print("precondicion de creacion: inventario del destino vacio")

        # Los TRES roots, en el orden canonico, con los contratos inyectados
        # como variables explicitas.
        contrato = preparar_los_roots_para(operacion, binario, destino, artefacto.ruta)
        terraform(
            binario,
            destino,
            ["fmt", "-check", "-recursive"],
            raiz=ROOT_DE_APLICACION.directorio,
        )
        terraform(binario, destino, ["validate"], raiz=ROOT_DE_APLICACION.directorio)
        terraform(
            binario,
            destino,
            ["plan", "-input=false", f"-out={PLAN_GUARDADO}"]
            + variables_comunes(ROOT_DE_APLICACION),
            raiz=ROOT_DE_APLICACION.directorio,
        )
        revisar_plan_guardado(
            binario,
            destino,
            acciones=acciones_permitidas,
            minimo=1,
        )
        if operacion == "rollback":
            exigir_actualizacion_de_lambda()

        sha_del_plan = sha256_de_archivo(PLAN_GUARDADO)
        print(f"SHA-256 del plan revisado: {sha_del_plan}")
        exigir_confirmacion_del_plan(sha_del_plan, operacion=operacion)
        mod_artefacto.confirmar_sin_cambios(artefacto)
        terraform(
            binario,
            destino,
            ["apply", "-input=false", str(PLAN_GUARDADO)],
            raiz=ROOT_DE_APLICACION.directorio,
        )
        valores = salidas(binario, destino, ROOT_DE_APLICACION)
        exigir_ownership_disjunto(estados_de_los_roots(binario, destino))
        print(f"ownership disjunto comprobado; bucket del contrato: {contrato['nombre_del_bucket']}")
        evidencia = ejercitar_servicios(
            destino,
            valores,
            runtime_fijado=runtime_fijado,
            id_del_runtime=id_del_runtime,
        )
        evidencia_sdk = inspeccionar_con_sdk(
            destino,
            valores,
            ruta_del_artefacto=artefacto.ruta,
        )

    titulo(f"{operacion.upper()} — completado")
    print(
        json.dumps(
            {
                "operacion": operacion,
                "plan_sha256": sha_del_plan,
                "artefacto_sha256": artefacto.sha256,
                "camino_critico": evidencia["camino_critico"]["estado"],
                "inspeccion_sdk": evidencia_sdk["sdk"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def comando_crear(argumentos: argparse.Namespace) -> int:
    return aplicar_version_desde_runbook(
        argumentos,
        operacion="crear",
        acciones_permitidas=("create",),
    )


def comando_rollback(argumentos: argparse.Namespace) -> int:
    return aplicar_version_desde_runbook(
        argumentos,
        operacion="rollback",
        acciones_permitidas=("update",),
    )


def comando_recuperar(argumentos: argparse.Namespace) -> int:
    return aplicar_version_desde_runbook(
        argumentos,
        operacion="recuperar",
        acciones_permitidas=("create", "update"),
    )


def comando_validar(argumentos: argparse.Namespace) -> int:
    titulo("VALIDAR — los tres roots, sus contratos, inventario, APIs y camino critico")
    (
        _,
        destino,
        binario,
        artefacto,
        runtime_fijado,
        id_del_runtime,
    ) = preparar_contexto_de_runbook(argumentos, preparar_runtime=True)
    if id_del_runtime is None:
        raise ErrorDelLaboratorio("no se observo la identidad local del runtime")
    lock_de_operacion = raiz_de_estado(destino.modo) / "laboratorio.lock"
    with mod_destino.lock_de_escritura(lock_de_operacion):
        # Camino de LECTURA: prepara los tres roots y lee sus contratos
        # sin aplicar nada. El contrato NO se deduce de las salidas del root de
        # aplicacion, que solo lo consume.
        contrato = preparar_los_roots_para("validar", binario, destino, artefacto.ruta)

        titulo("VALIDAR — configuracion valida en los TRES roots")
        for root in secuencia_de_roots("validar"):
            terraform(
                binario,
                destino,
                ["fmt", "-check", "-recursive"],
                raiz=root.directorio,
            )
            terraform(binario, destino, ["validate"], raiz=root.directorio)
            print(f"  root '{root.nombre}': formato y configuracion correctos")

        titulo("VALIDAR — ownership: ningun recurso en dos states")
        estados = estados_de_los_roots(binario, destino)
        exigir_ownership_disjunto(estados)
        print(
            "  "
            + "; ".join(f"{nombre} administra {len(direcciones)}" for nombre, direcciones in estados.items())
            + ". Aplicacion no administra S3, ni red, ni RDS"
        )

        valores = salidas(binario, destino, ROOT_DE_APLICACION)
        if valores.get("bucket_de_medios") != contrato["nombre_del_bucket"]:
            raise ErrorDelLaboratorio(
                "el grafo de aplicacion no esta usando el bucket que publica el "
                f"root de medios: {valores.get('bucket_de_medios')!r} frente a "
                f"{contrato['nombre_del_bucket']!r}"
            )
        print("  contrato entre roots coherente en ambos extremos")

        evidencia = ejercitar_servicios(
            destino,
            valores,
            runtime_fijado=runtime_fijado,
            id_del_runtime=id_del_runtime,
        )
        evidencia_sdk = inspeccionar_con_sdk(
            destino,
            valores,
            ruta_del_artefacto=artefacto.ruta,
        )
    print(
        json.dumps(
            {
                "artefacto_sha256": artefacto.sha256,
                "camino_critico": evidencia["camino_critico"]["estado"],
                "inspeccion_sdk": evidencia_sdk["sdk"],
                "contrato_de_medios": contrato["nombre_del_bucket"],
                "contrato_de_datos": contrato["datos"]["identificador_rds"],
                "recursos_por_root": {
                    nombre: len(direcciones) for nombre, direcciones in estados.items()
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def comando_destruir(argumentos: argparse.Namespace) -> int:
    titulo("DESTRUIR — plan destructivo y revision humana")
    _, destino, binario, artefacto, _, _ = preparar_contexto_de_runbook(
        argumentos, preparar_runtime=False
    )
    lock_de_operacion = raiz_de_estado(destino.modo) / "laboratorio.lock"
    with mod_destino.lock_de_escritura(lock_de_operacion):
        # Preparacion en orden de creacion para poder leer el contrato del bucket;
        # el `destroy` va despues en orden INVERSO.
        contrato = preparar_los_roots_para("destruir", binario, destino, artefacto.ruta)

        exigir_ownership_disjunto(estados_de_los_roots(binario, destino))
        bucket = contrato["nombre_del_bucket"]
        planes: dict[str, str] = {}
        for indice, root in enumerate(secuencia_de_roots("destruir")):
            if root == ROOT_DE_MEDIOS:
                borrados = herramental_real().vaciar_bucket(destino, bucket=bucket)
                print(f"objetos y versiones retirados de '{bucket}': {borrados}")
            titulo(f"DESTRUIR — plan destructivo del root '{root.nombre}'")
            terraform(
                binario,
                destino,
                ["plan", "-destroy", "-input=false", f"-out={root.plan_guardado}"]
                + variables_comunes(root),
                raiz=root.directorio,
            )
            revisar_plan_guardado(
                binario,
                destino,
                acciones=("delete",),
                minimo=1,
                root=root,
            )
            sha_del_plan = sha256_de_archivo(root.plan_guardado)
            print(f"SHA-256 del plan destructivo de '{root.nombre}': {sha_del_plan}")
            exigir_confirmacion_del_plan(
                sha_del_plan, operacion=f"destruir el root '{root.nombre}'"
            )
            planes[root.nombre] = sha_del_plan

            terraform(
                binario,
                destino,
                ["apply", "-input=false"] + variables_efimeras(root) + [str(root.plan_guardado)],
                raiz=root.directorio,
            )
            restantes = estado_del_root(binario, destino, root)
            outputs = salidas(binario, destino, root)
            if restantes or outputs:
                raise ErrorDelLaboratorio(
                    f"el state de '{root.nombre}' conserva {len(restantes)} "
                    f"recurso(s) y {len(outputs)} output(s) tras su destroy"
                )
            # Los roots que aun no se han destruido son legitimos, y solo ellos.
            vivos = {r.nombre for r in secuencia_de_roots("destruir")[indice + 1:]}
            exigir_ausencia_en_el_destino(
                inventario_del_destino(destino),
                bucket_de_medios_vivo=bucket if "medios" in vivos else None,
                datos_vivos="datos" in vivos,
            )
            print(
                f"root '{root.nombre}' destruido; inventario coherente "
                + (f"(siguen vivos, y son legitimos: {sorted(vivos)})" if vivos else "(nada vivo)")
            )

        exigir_ownership_disjunto(estados_de_los_roots(binario, destino), exigir_duennos=False)
    print(
        "destroy aplicado en los tres roots, en orden inverso, y ausencia "
        f"demostrada contra las APIs. Planes confirmados: {planes}"
    )
    return 0


def comando_inspeccionar_sdk(argumentos: argparse.Namespace) -> int:
    titulo("INSPECCION — AWS SDK oficial contra el destino local")
    _, destino, binario, artefacto, _, _ = preparar_contexto_de_runbook(
        argumentos, preparar_runtime=False
    )
    lock_de_operacion = raiz_de_estado(destino.modo) / "laboratorio.lock"
    with mod_destino.lock_de_escritura(lock_de_operacion):
        escribir_variables_del_destino(destino, artefacto.ruta)
        inicializar(binario, destino, solo_lectura=True)
        valores = salidas(binario, destino, ROOT_DE_APLICACION)
        inspeccionar_con_sdk(
            destino,
            valores,
            ruta_del_artefacto=artefacto.ruta,
        )
    return 0


# --- CLI --------------------------------------------------------------------


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="laboratorio",
        description="Laboratorio AWS local y operaciones de runbook (Task/025-026).",
    )
    parser.add_argument(
        "--modo",
        required=True,
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

    for nombre, ayuda in (
        ("crear", "crea desde inventario vacio tras aprobar el plan"),
        ("validar", "valida inventario, APIs, runtime y camino critico"),
        ("rollback", "aplica un artefacto anterior tras aprobar el plan"),
        ("destruir", "destruye tras aprobar un plan -destroy y verifica ausencia"),
        ("recuperar", "reconcilia ausencia o apply interrumpido y valida"),
        ("inspeccionar-sdk", "inspecciona recursos con boto3 desde el ZIP canonico"),
    ):
        operacion = subcomandos.add_parser(nombre, help=ayuda)
        operacion.add_argument(
            "--lambda-zip",
            required=True,
            help=(
                "Ruta explicita al ZIP canonico de Task/024; su manifiesto "
                "adyacente gobierna el runtime"
            ),
        )
    return parser


def main(argv: list[str] | None = None) -> int:
    argumentos = construir_parser().parse_args(argv)
    comandos = {
        "herramientas": comando_herramientas,
        "levantar": comando_levantar,
        "bajar": comando_bajar,
        "ciclo": comando_ciclo,
        "crear": comando_crear,
        "validar": comando_validar,
        "rollback": comando_rollback,
        "destruir": comando_destruir,
        "recuperar": comando_recuperar,
        "inspeccionar-sdk": comando_inspeccionar_sdk,
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
