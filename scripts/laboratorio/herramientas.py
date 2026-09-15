#!/usr/bin/env python3
"""Identidad de la herramienta Terraform y del lock del provider.

Por que existe
--------------
Terraform no viene con este repositorio, y la version con la que se valido la
infraestructura es parte de la infraestructura: una CLI distinta puede leer el
mismo `.tf` y producir otro plan. `versions.tf` fija la version **exigida**; este
modulo fija la version **instalada** y demuestra que el binario es el que
publico HashiCorp.

Dos cosas que se distinguen a proposito (S-09):

- **Identidad y procedencia** — es lo que se comprueba aqui: `sha256` del
  artefacto contra el `SHA256SUMS` oficial, y la firma GPG de ese archivo de
  sumas. Eso demuestra *que artefacto es*, no que no tenga defectos.
- **Vulnerabilidades** — no se comprueba aqui, y no se afirma. `sha256sum` no
  sabe nada de CVE; declarar «Terraform sin vulnerabilidades» porque el checksum
  coincide seria falso.

La herramienta se cachea **fuera de Git**, en el directorio de cache del usuario,
y no se instala en el sistema: el laboratorio no necesita modificar el PATH del
host para funcionar.
"""

from __future__ import annotations

import hashlib
import os
import platform
import re
import zipfile
from pathlib import Path
from typing import Final

#: Version exacta de la CLI. Debe coincidir con `required_version` de
#: `terraform/versions.tf`; hay una prueba que lo exige.
VERSION_DE_TERRAFORM: Final = "1.16.2"

#: Version exacta del provider oficial de AWS.
VERSION_DEL_PROVIDER: Final = "6.64.0"

#: Plataformas soportadas. No hay ARM64: ninguna decision del proyecto lo
#: autoriza, y `Task/024` ya fijo `linux/amd64` para el artefacto.
PLATAFORMAS: Final = ("linux_amd64", "windows_amd64")

#: `sha256` de los artefactos oficiales, verificados el 2026-09-13 contra
#: `https://releases.hashicorp.com/terraform/1.16.2/terraform_1.16.2_SHA256SUMS`,
#: cuyo archivo de sumas lleva firma GPG valida de HashiCorp Security
#: (clave primaria C874011F0AB405110D02105534365D9472D7468F).
CHECKSUMS_DE_TERRAFORM: Final = {
    "linux_amd64": "0d17011f0c4664539b164b044903d04e296c86c13cb9f28040076c65cfb3985a",
    "windows_amd64": "6ef140ce1d399dc43b8315194176ddc2dfb5c21d607968e82ef20a55cfff40d0",
}

#: `sha256` de los artefactos del provider, verificados el 2026-09-13 contra
#: `https://releases.hashicorp.com/terraform-provider-aws/6.64.0/terraform-provider-aws_6.64.0_SHA256SUMS`.
#: Se registran como evidencia de procedencia; la verificacion operativa del
#: provider la hace Terraform con `.terraform.lock.hcl`.
CHECKSUMS_DEL_PROVIDER: Final = {
    "linux_amd64": "17324d4335a7a7ac01cc23eded530775606680ff53b47cb74a3cb95d1121f836",
    "windows_amd64": "cd776b83b1f7b36635957350afe7ce28ba4e4ea3a5e2deb00d13dbd3b35d9d40",
}

#: Direccion oficial de descarga. Solo se usa cuando la cache esta vacia.
BASE_DE_DESCARGA: Final = "https://releases.hashicorp.com/terraform"

#: Identificador del provider tal como aparece en el lock.
PROVIDER: Final = "registry.terraform.io/hashicorp/aws"

BLOQUE: Final = 1024 * 1024


class ErrorDeHerramienta(RuntimeError):
    """La herramienta o el lock no son los que el proyecto fijo."""


def nombre_de_plataforma(*, sistema: str, maquina: str) -> str:
    """Traduce sistema y arquitectura al nombre que usa Terraform."""
    maquina = maquina.lower()
    if maquina not in ("amd64", "x86_64"):
        raise ErrorDeHerramienta(
            f"arquitectura '{maquina}' no soportada: el proyecto fija amd64 y "
            "ninguna decision autoriza otra"
        )
    sistemas = {"windows": "windows_amd64", "linux": "linux_amd64"}
    clave = sistema.lower()
    if clave not in sistemas:
        raise ErrorDeHerramienta(
            f"sistema '{sistema}' no soportado por el laboratorio; se fijan "
            f"{list(PLATAFORMAS)}"
        )
    return sistemas[clave]


def plataforma_actual() -> str:
    return nombre_de_plataforma(sistema=platform.system(), maquina=platform.machine())


def verificar_checksum(ruta: Path, esperado: str) -> str:
    """Comprueba el `sha256` de un artefacto contra el valor oficial."""
    if not ruta.is_file():
        raise ErrorDeHerramienta(f"no existe el artefacto a verificar: '{ruta}'")
    resumen = hashlib.sha256()
    with ruta.open("rb") as archivo:
        while True:
            bloque = archivo.read(BLOQUE)
            if not bloque:
                break
            resumen.update(bloque)
    obtenido = resumen.hexdigest()
    if obtenido != esperado:
        raise ErrorDeHerramienta(
            f"checksum inesperado para '{ruta.name}': se esperaba {esperado} y "
            f"se obtuvo {obtenido}"
        )
    return obtenido


def verificar_lock(texto: str, *, zip_por_plataforma: dict[str, str] | None = None) -> None:
    """Exige que el lock fije el provider y cubra **las dos** plataformas.

    Un lock generado en una sola maquina solo lleva los hashes de esa plataforma:
    el dia que CI corre en Linux y el desarrollo en Windows, `init
    -lockfile=readonly` falla por una diferencia que no es un problema real. Por
    eso el lock se genera para ambas y esta comprobacion lo vigila.
    """
    bloque = re.search(
        r'provider\s+"' + re.escape(PROVIDER) + r'"\s*\{(.*?)\n\}',
        texto,
        re.DOTALL,
    )
    if bloque is None:
        raise ErrorDeHerramienta(
            f"el lock no declara el provider '{PROVIDER}'"
        )
    contenido = bloque.group(1)
    version = re.search(r'version\s*=\s*"([^"]+)"', contenido)
    if version is None:
        raise ErrorDeHerramienta("el lock no declara la version del provider")
    if version.group(1) != VERSION_DEL_PROVIDER:
        raise ErrorDeHerramienta(
            f"el lock fija la version {version.group(1)} del provider y el "
            f"proyecto exige {VERSION_DEL_PROVIDER}"
        )
    hashes = re.findall(r'"(h1:[^"]+|zh:[^"]+)"', contenido)
    if not hashes:
        raise ErrorDeHerramienta("el lock no contiene ningun hash del provider")

    if zip_por_plataforma is None:
        return
    faltantes = [
        plataforma
        for plataforma, valor in zip_por_plataforma.items()
        if valor not in hashes
    ]
    for plataforma in PLATAFORMAS:
        if plataforma not in zip_por_plataforma:
            faltantes.append(plataforma)
    if faltantes:
        raise ErrorDeHerramienta(
            "el lock no cubre estas plataformas: " + ", ".join(sorted(set(faltantes)))
        )


def hashes_del_lock(texto: str) -> list[str]:
    """Devuelve los hashes que el lock declara para el provider."""
    bloque = re.search(
        r'provider\s+"' + re.escape(PROVIDER) + r'"\s*\{(.*?)\n\}',
        texto,
        re.DOTALL,
    )
    if bloque is None:
        return []
    return re.findall(r'"(h1:[^"]+|zh:[^"]+)"', bloque.group(1))


def raiz_de_cache() -> Path:
    """Directorio de cache de herramientas, **fuera** del arbol de Git.

    Se deriva del entorno y nunca se escribe una ruta absoluta del usuario en un
    archivo versionado. Si no hay variable util, cae en el directorio personal.
    """
    for variable in ("PERSONAL_BLOG_CACHE", "LOCALAPPDATA", "XDG_CACHE_HOME"):
        valor = os.environ.get(variable)
        if valor:
            return Path(valor) / "personal-blog-infra" / "herramientas"
    return Path.home() / ".cache" / "personal-blog-infra" / "herramientas"


def ruta_de_terraform(plataforma: str | None = None) -> Path:
    plataforma = plataforma or plataforma_actual()
    binario = "terraform.exe" if plataforma.startswith("windows") else "terraform"
    return raiz_de_cache() / f"terraform-{VERSION_DE_TERRAFORM}" / plataforma / binario


def url_de_terraform(plataforma: str) -> str:
    return (
        f"{BASE_DE_DESCARGA}/{VERSION_DE_TERRAFORM}/"
        f"terraform_{VERSION_DE_TERRAFORM}_{plataforma}.zip"
    )


def extraer_terraform(zip_descargado: Path, destino: Path) -> Path:
    """Extrae el binario del ZIP oficial ya verificado."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_descargado) as archivo:
        nombres = [n for n in archivo.namelist() if n in ("terraform", "terraform.exe")]
        if not nombres:
            raise ErrorDeHerramienta(
                f"el artefacto '{zip_descargado.name}' no contiene el binario de Terraform"
            )
        with archivo.open(nombres[0]) as origen, destino.open("wb") as salida:
            salida.write(origen.read())
    if not destino.name.endswith(".exe"):
        destino.chmod(0o755)
    return destino
