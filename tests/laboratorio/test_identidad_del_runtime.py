"""Identidad del runtime frente a varias REPRESENTACIONES de la misma imagen (DEF-030-3).

Por que este archivo existe
---------------------------
`confirmar_imagen_del_contenedor` hacia dos comprobaciones: la del **image ID**
observado, que es la autoritativa, y una comparacion **textual** de
`Config.Image` contra `fijado.etiqueta`.

La segunda rompio en `Task/030` sin que nada del proyecto cambiara. Con el
almacen de imagenes de containerd, Docker 29.1.3 entrega `Config.Image` como
`sha256:<digest>` en lugar de la etiqueta, y ahi `.Id` **es** el digest del
manifiesto. `Task/025` habia observado la etiqueta y la comprobacion paso; con
el mismo image ID y el mismo digest fijado, ahora fallaba.

Lo que hay que exigir no es una cadena concreta: es que la representacion que
trae el contenedor pueda **vincularse a la identidad inmutable fijada por
Task/024**. Esto NO es relajar la guarda:

- se sigue exigiendo `id_observado == id_esperado`, sin excepcion;
- una etiqueta distinta, un digest distinto o un `sha256:` que no sea el fijado
  siguen abortando;
- «parece un sha256» **no** basta: tiene que ser exactamente el digest fijado o
  exactamente el image ID esperado.
"""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from laboratorio import runtime as modulo  # noqa: E402

REPOSITORIO = "public.ecr.aws/lambda/python"
ETIQUETA = f"{REPOSITORIO}:3.12"
DIGEST_FIJADO = "sha256:" + "a1" * 32
DIGEST_AJENO = "sha256:" + "c3" * 32
REFERENCIA = f"{ETIQUETA}@{DIGEST_FIJADO}"

#: Con el almacen containerd el image ID coincide con el digest del manifiesto,
#: que es exactamente el caso medido en Task/030.
ID_IGUAL_AL_DIGEST = DIGEST_FIJADO
#: Con el almacen clasico son distintos, y los dos casos deben funcionar.
ID_LOCAL_CLASICO = "sha256:" + "11" * 32
ID_LOCAL_AJENO = "sha256:" + "22" * 32


def fijado() -> modulo.RuntimeFijado:
    return modulo.RuntimeFijado(
        etiqueta=ETIQUETA,
        digest=DIGEST_FIJADO,
        referencia=REFERENCIA,
        plataforma="linux/amd64",
    )


class RepresentacionesQueDemuestranLaIdentidad(unittest.TestCase):
    """Cada una denota, sin ambiguedad, el runtime fijado."""

    def comprobar(self, imagen_solicitada: str, id_esperado: str) -> None:
        modulo.confirmar_imagen_del_contenedor(
            fijado(),
            imagen_solicitada=imagen_solicitada,
            id_observado=id_esperado,
            id_esperado=id_esperado,
        )

    def test_etiqueta_fijada(self):
        self.comprobar(ETIQUETA, ID_LOCAL_CLASICO)

    def test_referencia_inmutable_completa(self):
        self.comprobar(REFERENCIA, ID_LOCAL_CLASICO)

    def test_referencia_por_digest_sin_etiqueta(self):
        self.comprobar(f"{REPOSITORIO}@{DIGEST_FIJADO}", ID_LOCAL_CLASICO)

    def test_digest_fijado_desnudo(self):
        """Lo que entrega Docker 29.1.3 con el almacen containerd."""
        self.comprobar(DIGEST_FIJADO, ID_IGUAL_AL_DIGEST)

    def test_image_id_esperado_desnudo(self):
        """Almacen clasico: el ID local no es el digest, y tambien vale."""
        self.comprobar(ID_LOCAL_CLASICO, ID_LOCAL_CLASICO)


class RepresentacionesQueNoLaDemuestran(unittest.TestCase):
    """Todo lo que no pueda vincularse a la identidad fijada debe abortar."""

    def rechaza(self, *, imagen_solicitada, id_observado, id_esperado) -> str:
        with self.assertRaises(modulo.ErrorDeRuntime) as capturado:
            modulo.confirmar_imagen_del_contenedor(
                fijado(),
                imagen_solicitada=imagen_solicitada,
                id_observado=id_observado,
                id_esperado=id_esperado,
            )
        return str(capturado.exception)

    def test_otra_etiqueta(self):
        self.rechaza(
            imagen_solicitada=f"{REPOSITORIO}:3.13",
            id_observado=ID_LOCAL_CLASICO,
            id_esperado=ID_LOCAL_CLASICO,
        )

    def test_otro_repositorio_con_el_digest_fijado(self):
        """El digest correcto bajo otro repositorio no es el runtime fijado."""
        self.rechaza(
            imagen_solicitada=f"ghcr.io/impostor/python@{DIGEST_FIJADO}",
            id_observado=ID_LOCAL_CLASICO,
            id_esperado=ID_LOCAL_CLASICO,
        )

    def test_otro_digest_en_la_referencia(self):
        self.rechaza(
            imagen_solicitada=f"{ETIQUETA}@{DIGEST_AJENO}",
            id_observado=ID_LOCAL_CLASICO,
            id_esperado=ID_LOCAL_CLASICO,
        )

    def test_sha256_desnudo_que_no_es_el_fijado(self):
        """«Parece un sha256» no es una demostracion de identidad."""
        self.rechaza(
            imagen_solicitada=DIGEST_AJENO,
            id_observado=ID_LOCAL_CLASICO,
            id_esperado=ID_LOCAL_CLASICO,
        )

    def test_id_observado_distinto_del_esperado(self):
        """La comprobacion autoritativa del image ID NO se elimina."""
        mensaje = self.rechaza(
            imagen_solicitada=ETIQUETA,
            id_observado=ID_LOCAL_AJENO,
            id_esperado=ID_LOCAL_CLASICO,
        )
        self.assertIn(ID_LOCAL_AJENO, mensaje)

    def test_id_observado_ausente(self):
        """No haber observado el contenedor no confirma nada."""
        self.rechaza(
            imagen_solicitada=ETIQUETA,
            id_observado=None,
            id_esperado=ID_LOCAL_CLASICO,
        )

    def test_representacion_vacia(self):
        self.rechaza(
            imagen_solicitada="",
            id_observado=ID_LOCAL_CLASICO,
            id_esperado=ID_LOCAL_CLASICO,
        )

    def test_representacion_ausente(self):
        self.rechaza(
            imagen_solicitada=None,
            id_observado=ID_LOCAL_CLASICO,
            id_esperado=ID_LOCAL_CLASICO,
        )

    def test_repositorio_sin_etiqueta_ni_digest_es_ambiguo(self):
        """`<repo>` a secas no fija contenido: podria ser cualquier version."""
        self.rechaza(
            imagen_solicitada=REPOSITORIO,
            id_observado=ID_LOCAL_CLASICO,
            id_esperado=ID_LOCAL_CLASICO,
        )

    def test_prefijo_sha256_sin_valor(self):
        self.rechaza(
            imagen_solicitada="sha256:",
            id_observado=ID_LOCAL_CLASICO,
            id_esperado=ID_LOCAL_CLASICO,
        )

    def test_none_de_docker_es_ambiguo(self):
        self.rechaza(
            imagen_solicitada="<none>",
            id_observado=ID_LOCAL_CLASICO,
            id_esperado=ID_LOCAL_CLASICO,
        )


if __name__ == "__main__":
    unittest.main()
