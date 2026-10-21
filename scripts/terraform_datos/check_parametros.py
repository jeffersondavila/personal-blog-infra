"""Preflight offline del parameter group: se ejecuta ANTES de planificar; nunca llama a AWS ni aplica.

Por que existe
--------------
El apply real de H-031-3 (§27.4) creo 20 de 21 recursos y fallo en
`ModifyDBParameterGroup` con `InvalidParameterValue: The parameter
superuser_reserved_connections cannot be modified`. Ni el plan, ni `check_plan.py`, ni
Floci validan si un parametro es modificable: solo lo hace la API real, y lo hace en
mitad del apply. Esta guarda adelanta esa comprobacion al catalogo de la familia.

Entrada: la respuesta de
`aws rds describe-engine-default-parameters --db-parameter-group-family postgres17`, o la
LISTA de sus paginas crudas (`--no-paginate` y `--marker`). Cada pagina debe declarar la
familia y solo la ultima puede venir sin `Marker`. La salida que el AWS CLI fusiona al
paginar solo descarta la familia y se rechaza.

Que exige
---------
- cada parametro explicito de `check_plan.PARAMETROS` existe en el catalogo, tiene
  `IsModifiable = true` y declara el `apply_method` de su `ApplyType`
  (`dynamic` -> `immediate`, `static` -> `pending-reboot`);
- ningun parametro de `PARAMETROS_DE_SISTEMA` se gestiona, y el catalogo sigue declarando
  su valor con `Source = system`: `superuser_reserved_connections = 3` (y no modificable),
  `rds.force_ssl = 1` y `ssl_min_protocol_version = TLSv1.2`. De ellos dependen el
  presupuesto de conexiones de D-12 y el TLS obligatorio de D-23 (RECOVERY-2, §33).
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.terraform_datos.check_plan import PARAMETROS, PARAMETROS_DE_SISTEMA, require

FAMILIA = "postgres17"
METODO_POR_TIPO = {"dynamic": "immediate", "static": "pending-reboot"}
#: Invariantes de sistema que ademas deben seguir siendo NO modificables.
NO_MODIFICABLES = {"superuser_reserved_connections"}


def _entradas(catalogo):
    """Entradas del catalogo, de UNA respuesta o de la LISTA de paginas crudas de la API.

    Cada pagina debe declarar la familia; todas menos la ultima llevan `Marker` y la ultima
    no. La salida que el AWS CLI fusiona al paginar solo descarta `DBParameterGroupFamily`
    (observado el 2026-10-05) y por eso se rechaza: no demuestra de que familia es.
    """
    paginas = catalogo if isinstance(catalogo, list) else [catalogo]
    require(bool(paginas), "CATALOG_EMPTY")
    entradas = []
    for i, pagina in enumerate(paginas):
        defaults = pagina["EngineDefaults"]
        require(defaults.get("DBParameterGroupFamily") == FAMILIA, "FAMILY")
        if i == len(paginas) - 1:
            require(not defaults.get("Marker"), "CATALOG_TRUNCATED")
        else:
            require(bool(defaults.get("Marker")), "CATALOG_PAGES")
        entradas.extend(defaults["Parameters"])
    return entradas


def revisar(parametros, catalogo):
    """`parametros`: conjunto de (nombre, valor, apply_method). `catalogo`: respuesta o paginas de la API."""
    por_nombre = {}
    for entrada in _entradas(catalogo):
        nombre = entrada["ParameterName"]
        require(nombre not in por_nombre, f"CATALOG_DUPLICATE {nombre}")
        por_nombre[nombre] = entrada

    require(bool(parametros), "NO_PARAMETERS")
    for nombre, _valor, metodo in sorted(parametros):
        # Primero la regla general del catalogo; despues la lista propia, por si AWS cambiara la bandera.
        entrada = por_nombre.get(nombre)
        require(entrada is not None, f"PARAM_UNKNOWN {nombre}")
        require(entrada.get("IsModifiable") is True, f"PARAM_NOT_MODIFIABLE {nombre}")
        require(nombre not in PARAMETROS_DE_SISTEMA, f"PARAM_SYSTEM_MANAGED {nombre}")
        require(entrada.get("ApplyType") in METODO_POR_TIPO, f"PARAM_APPLY_TYPE {nombre}")
        require(METODO_POR_TIPO[entrada["ApplyType"]] == metodo, f"PARAM_APPLY_METHOD {nombre}")

    for nombre, valor in PARAMETROS_DE_SISTEMA.items():
        entrada = por_nombre.get(nombre) or {}
        require(entrada.get("ParameterValue") == valor and entrada.get("Source") == "system", f"SYSTEM_DEFAULT {nombre}")
        if nombre in NO_MODIFICABLES:
            require(entrada.get("IsModifiable") is False, f"SYSTEM_DEFAULT {nombre}")

    return {
        "parametros": [{"nombre": n, "metodo": m, "apply_type": por_nombre[n]["ApplyType"], "modificable": True}
                       for n, _v, m in sorted(parametros)],
        "sistema": {n: por_nombre[n]["ParameterValue"] for n in PARAMETROS_DE_SISTEMA},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalogo_json", type=Path)
    args = parser.parse_args()
    try:
        raw = args.catalogo_json.read_bytes()
        resultado = revisar(PARAMETROS, json.loads(raw))
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        codigo = str(error) if isinstance(error, ValueError) else type(error).__name__
        raise SystemExit(f"parameter group rejected ({codigo}). No plan authorized.") from None
    print(json.dumps({"gate": "PARAMETERS_OK", "familia": FAMILIA,
                      "catalogo_sha256": hashlib.sha256(raw).hexdigest(), **resultado}))


if __name__ == "__main__":
    main()
