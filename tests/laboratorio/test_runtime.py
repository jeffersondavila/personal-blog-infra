"""Preparacion del runtime de Lambda fijado por digest (H-025-3).

Por que este archivo existe
---------------------------
La primera guarda del laboratorio comprobaba **frescura de la etiqueta**: hacia
`docker pull public.ecr.aws/lambda/python:3.12` y abortaba si el digest al que
resolvia ya no era el que `Task/024` fijo al construir el artefacto.

Eso era conceptualmente incorrecto, y se demostro:

- `Task/024` construye con una referencia **inmutable**
  `…python:3.12@sha256:a89893d9…`, asi que el movimiento posterior de la
  etiqueta **no** rompe su reproducibilidad;
- el digest antiguo **sigue descargable**: se borro la copia local, se volvio a
  bajar por digest y el ZIP se reconstruyo con el **mismo** `sha256`.

Es decir: la etiqueta movil es una **senal de actualizacion disponible**, no una
autoridad de identidad. La guarda estaba imponiendo que una etiqueta mutable
siguiera apuntando eternamente al digest viejo, lo que bloquea el laboratorio
ante un refresco rutinario de la imagen base y no protege nada.

Lo que SI hay que garantizar es que el emulador ejecute la Lambda sobre **el
mismo runtime que construyo el ZIP**. Y como el emulador resuelve el runtime por
etiqueta, la respuesta correcta es **fijar**, no abortar: descargar por digest y
asociar localmente la etiqueta a ese contenido exacto.
"""

from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from laboratorio import runtime as modulo  # noqa: E402

DIGEST_FIJADO = "sha256:" + "a1" * 32
DIGEST_MAS_NUEVO = "sha256:" + "b2" * 32
DIGEST_AJENO = "sha256:" + "c3" * 32
ETIQUETA = "public.ecr.aws/lambda/python:3.12"
REFERENCIA = f"{ETIQUETA}@{DIGEST_FIJADO}"

#: `docker image inspect --format {{.Id}}` no devuelve el digest del registro,
#: sino el identificador local del contenido. Son valores distintos y el modulo
#: no debe confundirlos.
ID_LOCAL_FIJADO = "sha256:" + "11" * 32
ID_LOCAL_AJENO = "sha256:" + "22" * 32


def manifiesto(ruta_del_zip, *, imagen=None, escribir=True):
    """Escribe un `manifiesto.json` como el que produce `Task/024`."""
    contenido = {
        "artefacto": ruta_del_zip.name,
        "sha256": "0" * 64,
        "handler": "app.lambda_handler.handler",
        "plataforma": "linux/amd64",
        "imagen": {
            "etiqueta": ETIQUETA,
            "digest": DIGEST_FIJADO,
            "digest_amd64": "sha256:" + "d4" * 32,
            "plataforma": "linux/amd64",
            "referencia": REFERENCIA,
        }
        if imagen is None
        else imagen,
    }
    if imagen is False:
        contenido.pop("imagen")
    if escribir:
        (ruta_del_zip.parent / "manifiesto.json").write_text(
            json.dumps(contenido, indent=2), encoding="utf-8"
        )
    return contenido


class DockerFalso:
    """Doble de Docker que registra TODO lo que se le pide.

    Registrar las referencias exactas es lo que permite afirmar que el modulo
    descargo por **digest** y que nunca uso la etiqueta desnuda como autoridad.
    """

    def __init__(self, *, ids=None, fallar_pull=(), fallar_tag=False):
        #: referencia -> id local. Ausente = la referencia no existe localmente.
        self.ids = dict(ids or {})
        self.fallar_pull = set(fallar_pull)
        self.fallar_tag = fallar_tag
        self.descargas = []
        self.etiquetados = []
        self.consultas = []

    def descargar(self, referencia):
        self.descargas.append(referencia)
        if referencia in self.fallar_pull:
            raise modulo.ErrorDeRuntime(f"fallo simulado al descargar {referencia}")
        # Una descarga correcta deja la referencia disponible localmente.
        self.ids.setdefault(referencia, ID_LOCAL_FIJADO)

    def identificador(self, referencia):
        self.consultas.append(referencia)
        return self.ids.get(referencia)

    def etiquetar(self, origen, destino):
        self.etiquetados.append((origen, destino))
        if self.fallar_tag:
            raise modulo.ErrorDeRuntime("fallo simulado al etiquetar")
        self.ids[destino] = self.ids[origen]


class ManifiestoTests(unittest.TestCase):
    """El digest lo declara Task/024, no Task/025."""

    def setUp(self):
        self.directorio = tempfile.TemporaryDirectory(prefix="task025-runtime-")
        self.addCleanup(self.directorio.cleanup)
        self.zip = Path(self.directorio.name) / "personal-blog-backend-lambda.zip"
        self.zip.write_bytes(b"PK\x03\x04relleno")

    def test_el_runtime_se_lee_del_manifiesto_de_task024(self):
        manifiesto(self.zip)
        fijado = modulo.leer_runtime_fijado(self.zip)
        self.assertEqual(fijado.etiqueta, ETIQUETA)
        self.assertEqual(fijado.digest, DIGEST_FIJADO)
        self.assertEqual(fijado.referencia, REFERENCIA)
        self.assertEqual(fijado.plataforma, "linux/amd64")

    def test_sin_manifiesto_aborta(self):
        """Task/025 consume el paquete de Task/024, no un ZIP suelto."""
        with self.assertRaises(modulo.ErrorDeRuntime) as capturado:
            modulo.leer_runtime_fijado(self.zip)
        self.assertIn("manifiesto", str(capturado.exception).lower())

    def test_manifiesto_sin_seccion_de_imagen_aborta(self):
        manifiesto(self.zip, imagen=False)
        with self.assertRaises(modulo.ErrorDeRuntime):
            modulo.leer_runtime_fijado(self.zip)

    def test_manifiesto_con_digest_malformado_aborta(self):
        manifiesto(self.zip, imagen={"etiqueta": ETIQUETA, "digest": "no-es-un-digest",
                                     "referencia": "x", "plataforma": "linux/amd64"})
        with self.assertRaises(modulo.ErrorDeRuntime):
            modulo.leer_runtime_fijado(self.zip)

    def test_manifiesto_con_referencia_incoherente_aborta(self):
        """La referencia debe ser exactamente etiqueta@digest."""
        manifiesto(self.zip, imagen={
            "etiqueta": ETIQUETA,
            "digest": DIGEST_FIJADO,
            "referencia": f"{ETIQUETA}@{DIGEST_AJENO}",
            "plataforma": "linux/amd64",
        })
        with self.assertRaises(modulo.ErrorDeRuntime):
            modulo.leer_runtime_fijado(self.zip)

    def test_manifiesto_ilegible_aborta(self):
        (self.zip.parent / "manifiesto.json").write_text("{no es json", encoding="utf-8")
        with self.assertRaises(modulo.ErrorDeRuntime):
            modulo.leer_runtime_fijado(self.zip)

    def test_plataforma_distinta_de_amd64_aborta(self):
        manifiesto(self.zip, imagen={
            "etiqueta": ETIQUETA, "digest": DIGEST_FIJADO,
            "referencia": REFERENCIA, "plataforma": "linux/arm64",
        })
        with self.assertRaises(modulo.ErrorDeRuntime):
            modulo.leer_runtime_fijado(self.zip)


class PreparacionTests(unittest.TestCase):
    def setUp(self):
        self.fijado = modulo.RuntimeFijado(
            etiqueta=ETIQUETA, digest=DIGEST_FIJADO,
            referencia=REFERENCIA, plataforma="linux/amd64",
        )

    def test_digest_disponible_y_etiqueta_local_ausente(self):
        """Caso 1: se descarga por digest y se asocia la etiqueta."""
        docker = DockerFalso()
        informe = modulo.preparar_runtime(self.fijado, docker)
        self.assertEqual(docker.descargas, [REFERENCIA])
        self.assertEqual(docker.etiquetados, [(REFERENCIA, ETIQUETA)])
        self.assertEqual(informe["accion"], "etiquetada")
        self.assertEqual(informe["id"], ID_LOCAL_FIJADO)

    def test_la_etiqueta_local_apunta_a_otro_runtime_se_corrige(self):
        """Caso 2 y control negativo de §7: una cache obsoleta NO manda."""
        docker = DockerFalso(ids={ETIQUETA: ID_LOCAL_AJENO})
        informe = modulo.preparar_runtime(self.fijado, docker)
        self.assertIn((REFERENCIA, ETIQUETA), docker.etiquetados)
        self.assertEqual(docker.ids[ETIQUETA], ID_LOCAL_FIJADO)
        self.assertEqual(informe["accion"], "reetiquetada")
        self.assertEqual(informe["id_anterior"], ID_LOCAL_AJENO)

    def test_la_etiqueta_local_ya_es_correcta_es_idempotente(self):
        """Caso 3: no se vuelve a etiquetar si ya coincide."""
        docker = DockerFalso(ids={REFERENCIA: ID_LOCAL_FIJADO, ETIQUETA: ID_LOCAL_FIJADO})
        informe = modulo.preparar_runtime(self.fijado, docker)
        self.assertEqual(docker.etiquetados, [])
        self.assertEqual(informe["accion"], "ya_correcta")

    def test_una_etiqueta_local_mas_nueva_no_se_acepta(self):
        """Caso 10: ser mas reciente no es un argumento de identidad."""
        docker = DockerFalso(ids={ETIQUETA: ID_LOCAL_AJENO})
        modulo.preparar_runtime(self.fijado, docker)
        self.assertEqual(docker.ids[ETIQUETA], ID_LOCAL_FIJADO)

    def test_no_se_descarga_nunca_la_etiqueta_desnuda(self):
        """Casos 8 y 9: la etiqueta mutable no es autoridad de identidad."""
        docker = DockerFalso(ids={ETIQUETA: ID_LOCAL_AJENO})
        modulo.preparar_runtime(self.fijado, docker)
        self.assertNotIn(ETIQUETA, docker.descargas)
        for referencia in docker.descargas:
            self.assertIn("@sha256:", referencia)

    def test_el_digest_no_disponible_aborta(self):
        """Caso 4: si el contenido fijado no se puede obtener, fail closed."""
        docker = DockerFalso(fallar_pull={REFERENCIA})
        with self.assertRaises(modulo.ErrorDeRuntime) as capturado:
            modulo.preparar_runtime(self.fijado, docker)
        self.assertIn(DIGEST_FIJADO, str(capturado.exception))

    def test_la_descarga_que_no_deja_la_imagen_aborta(self):
        """Caso 5: `pull` que dice funcionar pero no deja nada utilizable."""
        class Mudo(DockerFalso):
            def descargar(self, referencia):
                self.descargas.append(referencia)  # no registra ningun id
        with self.assertRaises(modulo.ErrorDeRuntime):
            modulo.preparar_runtime(self.fijado, Mudo())

    def test_el_etiquetado_que_falla_aborta(self):
        """Caso 6."""
        docker = DockerFalso(fallar_tag=True)
        with self.assertRaises(modulo.ErrorDeRuntime):
            modulo.preparar_runtime(self.fijado, docker)

    def test_la_verificacion_posterior_detecta_identidad_distinta(self):
        """Caso 7: etiquetar "con exito" pero dejar otra imagen -> fail closed."""
        class Tramposo(DockerFalso):
            def etiquetar(self, origen, destino):
                self.etiquetados.append((origen, destino))
                self.ids[destino] = ID_LOCAL_AJENO  # no es lo que se pidio
        docker = Tramposo()
        with self.assertRaises(modulo.ErrorDeRuntime) as capturado:
            modulo.preparar_runtime(self.fijado, docker)
        self.assertIn("identidad", str(capturado.exception).lower())


class IdentificacionDeContenedoresTests(unittest.TestCase):
    """Que contenedor es el de la funcion, y cual no.

    Observado en los logs del emulador durante una invocacion real: lanza DOS
    contenedores distintos y solo uno ejecuta el codigo.

      floci-codevol-blog-lab-backend-c702b34d   <- puebla el volumen de codigo
      floci-blog-lab-backend-85f90d15           <- ejecuta la funcion

    Confundirlos daria por evidencia un contenedor auxiliar que no corrio el
    handler. Ambos se retiran al terminar, asi que hay que observarlos mientras
    viven.
    """

    def test_reconoce_el_contenedor_de_la_funcion(self):
        self.assertTrue(
            modulo.es_contenedor_de_la_funcion(
                "floci-blog-lab-backend-85f90d15", "blog-lab-backend"
            )
        )

    def test_descarta_el_contenedor_del_volumen_de_codigo(self):
        self.assertFalse(
            modulo.es_contenedor_de_la_funcion(
                "floci-codevol-blog-lab-backend-c702b34d", "blog-lab-backend"
            )
        )

    def test_descarta_el_emulador(self):
        self.assertFalse(
            modulo.es_contenedor_de_la_funcion(
                "personal-blog-lab-emulador", "blog-lab-backend"
            )
        )

    def test_descarta_los_servicios_del_entorno_ordinario(self):
        for nombre in (
            "personal-blog-local-backend",
            "personal-blog-local-postgres",
            "personal-blog-local-minio",
        ):
            with self.subTest(nombre=nombre):
                self.assertFalse(
                    modulo.es_contenedor_de_la_funcion(nombre, "blog-lab-backend")
                )

    def test_descarta_otra_funcion(self):
        self.assertFalse(
            modulo.es_contenedor_de_la_funcion("floci-otra-funcion-abc", "blog-lab-backend")
        )

    def test_exige_el_prefijo_del_emulador(self):
        """Un contenedor con ese nombre pero sin el prefijo no es del emulador."""
        self.assertFalse(
            modulo.es_contenedor_de_la_funcion("blog-lab-backend", "blog-lab-backend")
        )


class ContenedorTests(unittest.TestCase):
    """La ultima milla: que el contenedor lanzado use esa imagen.

    El mensaje del emulador —*«Image already present locally, skipping pull»*— es
    evidencia util pero NO suficiente. Hay que mirar el contenedor real.
    """

    def setUp(self):
        self.fijado = modulo.RuntimeFijado(
            etiqueta=ETIQUETA, digest=DIGEST_FIJADO,
            referencia=REFERENCIA, plataforma="linux/amd64",
        )

    def test_contenedor_con_la_imagen_esperada(self):
        modulo.confirmar_imagen_del_contenedor(
            self.fijado,
            imagen_solicitada=ETIQUETA,
            id_observado=ID_LOCAL_FIJADO,
            id_esperado=ID_LOCAL_FIJADO,
        )

    def test_contenedor_con_otro_id_aborta(self):
        with self.assertRaises(modulo.ErrorDeRuntime) as capturado:
            modulo.confirmar_imagen_del_contenedor(
                self.fijado,
                imagen_solicitada=ETIQUETA,
                id_observado=ID_LOCAL_AJENO,
                id_esperado=ID_LOCAL_FIJADO,
            )
        self.assertIn(ID_LOCAL_AJENO, str(capturado.exception))

    def test_contenedor_que_pidio_otra_imagen_aborta(self):
        with self.assertRaises(modulo.ErrorDeRuntime):
            modulo.confirmar_imagen_del_contenedor(
                self.fijado,
                imagen_solicitada="public.ecr.aws/lambda/python:3.13",
                id_observado=ID_LOCAL_FIJADO,
                id_esperado=ID_LOCAL_FIJADO,
            )

    def test_sin_contenedor_observado_aborta(self):
        """No encontrar el contenedor no es una confirmacion."""
        with self.assertRaises(modulo.ErrorDeRuntime):
            modulo.confirmar_imagen_del_contenedor(
                self.fijado,
                imagen_solicitada=ETIQUETA,
                id_observado=None,
                id_esperado=ID_LOCAL_FIJADO,
            )


if __name__ == "__main__":
    unittest.main()
