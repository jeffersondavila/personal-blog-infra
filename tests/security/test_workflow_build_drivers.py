"""Contrato del workflow: el exportador OCI exige un builder compatible y fijado.

`Task/027.1` introdujo un `docker buildx build --output type=oci` y el CI de
GitHub lo rechazo con «OCI exporter is not supported for the docker driver».
La causa no fue el Dockerfile ni el baseline: fue que el comando cayo en el
builder `default` del runner, cuyo driver `docker` no implementa exportadores.

Las pruebas locales no lo vieron porque alli se uso un builder
`docker-container` explicito y, ademas, Docker Desktop tenia el *image store*
de containerd: dos motivos independientes para funcionar que el runner no
tiene. Este modulo cierra esa brecha comprobando el **contrato del workflow**,
no el entorno donde se ejecute.

No impone nada a los `docker build` de Postgres y Traefik: esos construyen con
el builder por defecto y deben seguir haciendolo, porque sus imagenes tienen
que quedar en el daemon para que Trivy las escanee despues.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/ci-infra.yml"

#: Exportadores que el driver `docker` no implementa. `--output type=X` con
#: cualquiera de estos exige un builder `docker-container` (o equivalente).
EXPORTADORES_INCOMPATIBLES = ("oci", "tar", "local")

#: Un digest fijado, no una etiqueta movil.
IMAGEN_POR_DIGEST = re.compile(r"^[^\s@]+@sha256:[0-9a-f]{64}$")


def texto_del_workflow() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def unir_continuaciones(texto: str) -> list[str]:
    """Une las lineas partidas con barra invertida en comandos completos."""
    salida: list[str] = []
    acumulado = ""
    for linea in texto.split("\n"):
        desnuda = linea.rstrip()
        if desnuda.endswith("\\"):
            acumulado += desnuda[:-1].strip() + " "
            continue
        acumulado += desnuda.strip()
        salida.append(acumulado)
        acumulado = ""
    if acumulado:
        salida.append(acumulado)
    return salida


def variables_de_entorno(texto: str) -> dict[str, str]:
    """Lee el bloque `env:` de nivel superior del workflow."""
    entorno: dict[str, str] = {}
    dentro = False
    for linea in texto.split("\n"):
        if linea.startswith("env:"):
            dentro = True
            continue
        if dentro:
            if linea and not linea.startswith(" "):
                break
            hallazgo = re.match(r"\s{2}([A-Z_][A-Z0-9_]*):\s*'([^']*)'\s*$", linea)
            if hallazgo:
                entorno[hallazgo.group(1)] = hallazgo.group(2)
    return entorno


def resolver(valor: str, entorno: dict[str, str]) -> str:
    """Sustituye `$VAR` y `${VAR}` por su valor del bloque `env:`."""
    for clave, contenido in entorno.items():
        valor = valor.replace("${%s}" % clave, contenido)
        valor = valor.replace('"$%s"' % clave, contenido)
        valor = valor.replace("$%s" % clave, contenido)
    return valor


def builds_con_exportador_incompatible(texto: str) -> list[str]:
    comandos = []
    for comando in unir_continuaciones(texto):
        if "docker buildx build" not in comando:
            continue
        salida = re.search(r"--output\s+(?:\"|')?type=([a-z]+)", comando)
        if salida and salida.group(1) in EXPORTADORES_INCOMPATIBLES:
            comandos.append(comando)
    return comandos


def creaciones_de_builder(texto: str) -> dict[str, str]:
    """Nombre del builder -> comando completo que lo crea."""
    creados = {}
    entorno = variables_de_entorno(texto)
    for comando in unir_continuaciones(texto):
        if "docker buildx create" not in comando:
            continue
        nombre = re.search(r"--name\s+(\S+)", comando)
        if nombre:
            creados[resolver(nombre.group(1), entorno)] = comando
    return creados


class ExportadorOciExigeBuilderCompatibleTests(unittest.TestCase):
    def setUp(self):
        self.texto = texto_del_workflow()
        self.entorno = variables_de_entorno(self.texto)
        self.comandos = builds_con_exportador_incompatible(self.texto)
        self.creados = creaciones_de_builder(self.texto)

    def test_el_gate_no_queda_vacio(self):
        """Si nadie exporta OCI, este modulo no estaria comprobando nada."""
        self.assertTrue(
            self.comandos,
            "no se encontro ningun 'docker buildx build --output type=oci': "
            "el gate quedaria vacio y dejaria de proteger nada",
        )

    def test_cada_build_declara_un_builder_explicito(self):
        for comando in self.comandos:
            with self.subTest(comando=comando[:60]):
                self.assertIn(
                    "--builder",
                    comando,
                    "un exportador incompatible con el driver 'docker' sin "
                    "--builder cae en el builder 'default' del runner y falla "
                    "con 'OCI exporter is not supported for the docker driver'",
                )

    def test_el_builder_se_crea_antes_de_usarse(self):
        for comando in self.comandos:
            nombre = resolver(
                re.search(r"--builder\s+(\S+)", comando).group(1), self.entorno
            )
            with self.subTest(builder=nombre):
                self.assertIn(
                    nombre,
                    self.creados,
                    "el builder '%s' se usa pero no lo crea ningun "
                    "'docker buildx create' del workflow" % nombre,
                )
                self.assertLess(
                    self.texto.index(self.creados[nombre]. split(" ")[0]),
                    self.texto.index("--output type=oci"),
                    "el builder debe crearse ANTES de usarlo",
                )

    def test_el_builder_usa_driver_docker_container(self):
        for comando in self.comandos:
            nombre = resolver(
                re.search(r"--builder\s+(\S+)", comando).group(1), self.entorno
            )
            creacion = self.creados[nombre]
            with self.subTest(builder=nombre):
                self.assertIn(
                    "--driver docker-container",
                    creacion,
                    "solo un driver con exportadores sirve; 'docker' no los tiene",
                )

    def test_la_imagen_de_buildkit_esta_fijada_por_digest(self):
        for comando in self.comandos:
            nombre = resolver(
                re.search(r"--builder\s+(\S+)", comando).group(1), self.entorno
            )
            creacion = self.creados[nombre]
            imagen = re.search(r"--driver-opt\s+\"?image=([^\"\s]+)", creacion)
            with self.subTest(builder=nombre):
                self.assertIsNotNone(
                    imagen,
                    "el builder no fija la imagen de BuildKit: su version "
                    "podria cambiar sola y con ella el manifiesto exportado",
                )
                resuelta = resolver(imagen.group(1), self.entorno)
                self.assertRegex(
                    resuelta,
                    IMAGEN_POR_DIGEST,
                    "la imagen de BuildKit debe ir por digest, no por una "
                    "etiqueta movil como 'buildx-stable-1'",
                )

    def test_el_builder_dedicado_no_se_vuelve_el_predeterminado(self):
        for creacion in self.creados.values():
            with self.subTest(creacion=creacion[:60]):
                self.assertNotIn(
                    "--use",
                    creacion,
                    "'--use' convertiria el builder en predeterminado y los "
                    "'docker build' de Postgres y Traefik dejarian de cargar "
                    "sus imagenes en el daemon, que es donde Trivy las busca",
                )

    def test_el_builder_dedicado_se_retira(self):
        for nombre in self.creados:
            with self.subTest(builder=nombre):
                self.assertIn(
                    "docker buildx rm",
                    self.texto,
                    "el builder dedicado debe retirarse al terminar",
                )

    def test_postgres_y_traefik_siguen_con_el_builder_por_defecto(self):
        """El contrato NO se extiende a los builds normales.

        Sus imagenes deben quedar en el daemon local para que Trivy las
        escanee; forzarlas a un builder `docker-container` las sacaria de ahi.
        """
        comandos = [
            c for c in unir_continuaciones(self.texto)
            if re.search(r"(?<!buildx )docker build ", c)
        ]
        self.assertEqual(len(comandos), 2, "se esperan los builds de postgres y traefik")
        for comando in comandos:
            with self.subTest(comando=comando[:50]):
                self.assertNotIn("--builder", comando)
                self.assertNotIn("--output", comando)


class ControlesNegativosTests(unittest.TestCase):
    """Demuestran que el contrato se pone ROJO cuando debe.

    No basta con comprobar que la manipulacion se aplico: cada caso ejecuta la
    verificacion real sobre el workflow manipulado y exige que **falle**. Sin
    esto, las comprobaciones de arriba podrian estar pasando por construccion.
    """

    def setUp(self):
        self.texto = texto_del_workflow()

    @staticmethod
    def verificar(texto: str) -> None:
        """La verificacion real, aislada para poder ejercitarla contra texto manipulado.

        Lanza AssertionError si el workflow incumple el contrato.
        """
        entorno = variables_de_entorno(texto)
        creados = creaciones_de_builder(texto)
        comandos = builds_con_exportador_incompatible(texto)
        assert comandos, "ningun build con exportador incompatible"
        for comando in comandos:
            builder = re.search(r"--builder\s+(\S+)", comando)
            assert builder, "exportador incompatible sin --builder"
            nombre = resolver(builder.group(1), entorno)
            assert nombre in creados, "builder no creado en el workflow"
            creacion = creados[nombre]
            assert "--driver docker-container" in creacion, "driver incompatible"
            assert "--use" not in creacion, "el builder se vuelve predeterminado"
            imagen = re.search(r'--driver-opt\s+"?image=([^"\s]+)', creacion)
            assert imagen, "imagen de BuildKit sin fijar"
            assert IMAGEN_POR_DIGEST.match(resolver(imagen.group(1), entorno)),                 "imagen de BuildKit sin digest"

    def test_el_workflow_vigente_cumple_el_contrato(self):
        """Prueba positiva: sin ella, los negativos no probarian nada."""
        self.verificar(self.texto)

    def test_quitar_el_builder_es_rojo(self):
        """Este es EXACTAMENTE el defecto que rompio el CI de GitHub."""
        manipulado = self.texto.replace('--builder "$BUILDER_OCI_DE_MINIO" \
', "", 1)
        self.assertNotEqual(manipulado, self.texto, "el control negativo no manipulo nada")
        with self.assertRaises(AssertionError):
            self.verificar(manipulado)

    def test_una_imagen_de_buildkit_por_etiqueta_movil_es_rojo(self):
        manipulado = self.texto.replace(
            "moby/buildkit@sha256:28a898719c18a33f4e8000685287fa36fd0dd9560c6440227d3a732d79bb41d8",
            "moby/buildkit:buildx-stable-1",
            1,
        )
        self.assertNotEqual(manipulado, self.texto, "el control negativo no manipulo nada")
        with self.assertRaises(AssertionError):
            self.verificar(manipulado)

    def test_degradar_el_driver_a_docker_es_rojo(self):
        manipulado = self.texto.replace("--driver docker-container", "--driver docker", 1)
        self.assertNotEqual(manipulado, self.texto, "el control negativo no manipulo nada")
        with self.assertRaises(AssertionError):
            self.verificar(manipulado)

    def test_convertirlo_en_predeterminado_es_rojo(self):
        manipulado = self.texto.replace("--bootstrap", "--use --bootstrap", 1)
        self.assertNotEqual(manipulado, self.texto, "el control negativo no manipulo nada")
        with self.assertRaises(AssertionError):
            self.verificar(manipulado)

    def test_no_crear_el_builder_es_rojo(self):
        manipulado = self.texto.replace("docker buildx create --name", "docker buildx noop --name", 1)
        self.assertNotEqual(manipulado, self.texto, "el control negativo no manipulo nada")
        with self.assertRaises(AssertionError):
            self.verificar(manipulado)


if __name__ == "__main__":
    unittest.main()
