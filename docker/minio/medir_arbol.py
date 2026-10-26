"""Medicion determinista de un arbol de archivos y de la diferencia entre dos mediciones.

Forma parte de la receta del derivado de MinIO (contrato v3, Task/031). Se ejecuta en la etapa `paquetes`, nunca
en la imagen final.

    medir_arbol.py medir <raiz> <salida>
    medir_arbol.py delta <antes> <despues> <salida>

Cada entrada: tipo (f, l, d u o), ruta relativa, modo octal, uid, gid, tamano y sha256 para un archivo, o destino para
un enlace. La delta marca cada ruta como A (anadida), M (modificada) o D (retirada) y conserva la entrada que la
describe: la nueva para A y M, la anterior para D.
"""
import hashlib
import os
import stat
import sys


def medir(raiz):
    filas = {}
    for actual, directorios, archivos in os.walk(raiz, followlinks=False):
        directorios.sort()
        for nombre in sorted(directorios + archivos):
            ruta = os.path.join(actual, nombre)
            relativa = os.path.relpath(ruta, raiz).replace(os.sep, "/")
            st = os.lstat(ruta)
            comun = (f"{stat.S_IMODE(st.st_mode):04o}", str(st.st_uid), str(st.st_gid))
            if stat.S_ISLNK(st.st_mode):
                filas[relativa] = ("l", *comun, "-", os.readlink(ruta))
            elif stat.S_ISDIR(st.st_mode):
                filas[relativa] = ("d", *comun, "-", "-")
            elif stat.S_ISREG(st.st_mode):
                resumen = hashlib.sha256()
                with open(ruta, "rb") as archivo:
                    for bloque in iter(lambda: archivo.read(1 << 20), b""):
                        resumen.update(bloque)
                filas[relativa] = ("f", *comun, str(st.st_size), resumen.hexdigest())
            else:
                filas[relativa] = ("o", *comun, "-", "-")
    return filas


def escribir(filas, salida):
    with open(salida, "w", encoding="utf-8", newline="\n") as archivo:
        for relativa in sorted(filas):
            tipo, *resto = filas[relativa]
            archivo.write(" ".join([tipo, relativa, *resto]) + "\n")


def leer(ruta):
    filas = {}
    with open(ruta, encoding="utf-8") as archivo:
        for linea in archivo:
            tipo, relativa, *resto = linea.rstrip("\n").split(" ")
            filas[relativa] = (tipo, *resto)
    return filas


def delta(antes, despues):
    lineas = []
    for relativa in sorted(set(antes) | set(despues)):
        if relativa not in antes:
            lineas.append(("A", relativa, despues[relativa]))
        elif relativa not in despues:
            lineas.append(("D", relativa, antes[relativa]))
        elif antes[relativa] != despues[relativa]:
            lineas.append(("M", relativa, despues[relativa]))
    return lineas


def main(argumentos):
    if argumentos[:1] == ["medir"] and len(argumentos) == 3:
        escribir(medir(argumentos[1]), argumentos[2])
    elif argumentos[:1] == ["delta"] and len(argumentos) == 4:
        with open(argumentos[3], "w", encoding="utf-8", newline="\n") as archivo:
            for marca, relativa, (tipo, *resto) in delta(leer(argumentos[1]), leer(argumentos[2])):
                archivo.write(" ".join([marca, tipo, relativa, *resto]) + "\n")
    else:
        sys.exit("uso: medir_arbol.py medir <raiz> <salida> | delta <antes> <despues> <salida>")


if __name__ == "__main__":
    main(sys.argv[1:])
