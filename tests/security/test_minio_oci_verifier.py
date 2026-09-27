"""Negativos del verificador OCI del derivado de MinIO.

Task/028 (H-028-2) amplio el derivado a DOS binarios sustituidos. El contrato
que se verifica aqui es el que impide que esa ampliacion se convierta en una
puerta abierta: el artefacto debe sustituir EXACTAMENTE los paths declarados en
la receta, cada uno en su layer, con su contenido, su modo y su propietario.

Cada prueba construye un OCI sintetico coherente y despues rompe UNA sola cosa.
Si el verificador aceptara cualquiera de esos artefactos, el derivado real
podria transportar un binario extra sin que nadie lo notara.
"""

import copy
import hashlib
import io
import json
import shutil
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/minio"))
import artifact  # noqa: E402

CONFIG_RUNTIME = {
    "Entrypoint": ["/usr/bin/docker-entrypoint.sh"],
    "Cmd": ["minio"],
    "Env": ["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"],
}
MINIO = b"binario-minio-simulado"
MC = b"binario-mc-simulado"


def dig(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def tar_de(miembros):
    """Serializa una lista de (nombre, tipo, contenido, modo, uid, gid)."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w", format=tarfile.PAX_FORMAT) as archivo:
        for nombre, tipo, contenido, modo, uid, gid in miembros:
            info = tarfile.TarInfo(nombre)
            info.type = tipo
            info.mode = modo
            info.uid = uid
            info.gid = gid
            info.uname = ""
            info.gname = ""
            info.mtime = 0
            if tipo == tarfile.REGTYPE:
                info.size = len(contenido)
                archivo.addfile(info, io.BytesIO(contenido))
            else:
                archivo.addfile(info)
    return buffer.getvalue()


def layer_de_binario(ruta, contenido, modo=0o755, uid=0, gid=0):
    partes = ruta.split("/")
    miembros = [
        ("/".join(partes[:n + 1]), tarfile.DIRTYPE, b"", 0o755, 0, 0)
        for n in range(len(partes) - 1)
    ]
    miembros.append((ruta, tarfile.REGTYPE, contenido, modo, uid, gid))
    return tar_de(miembros)


class ArtefactoSintetico:
    """Un OCI valido y su build manifest, cada uno mutable por separado."""

    BASE = [
        tar_de([("etc/base-a", tarfile.REGTYPE, b"base-a", 0o644, 0, 0)]),
        tar_de([("etc/base-b", tarfile.REGTYPE, b"base-b", 0o644, 0, 0)]),
    ]

    def __init__(self, reemplazos):
        self.reemplazos = list(reemplazos)
        self.layers_extra = [datos for _, datos in self.reemplazos]

    def construir(self, directorio, layers_extra=None):
        extra = list(self.layers_extra if layers_extra is None else layers_extra)
        layers = list(self.BASE) + extra
        digests = [dig(item) for item in layers]
        heredados = len(self.BASE)

        config = {
            "architecture": "amd64",
            "os": "linux",
            "config": CONFIG_RUNTIME,
            "rootfs": {"type": "layers", "diff_ids": digests},
        }
        config_bytes = artifact.canonical(config)
        manifest = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "config": {
                "mediaType": "application/vnd.oci.image.config.v1+json",
                "digest": dig(config_bytes),
                "size": len(config_bytes),
            },
            "layers": [
                {
                    "mediaType": "application/vnd.oci.image.layer.v1.tar",
                    "digest": digest,
                    "size": len(data),
                }
                for digest, data in zip(digests, layers)
            ],
        }
        manifest_bytes = artifact.canonical(manifest)
        index = {
            "schemaVersion": 2,
            "manifests": [{
                "mediaType": "application/vnd.oci.image.manifest.v1+json",
                "digest": dig(manifest_bytes),
                "size": len(manifest_bytes),
                "platform": {"architecture": "amd64", "os": "linux"},
            }],
        }
        index_bytes = artifact.canonical(index)

        ruta = Path(directorio) / ("artefacto-%s.oci.tar" % hashlib.sha256(index_bytes).hexdigest()[:12])
        with tarfile.open(ruta, "w") as archivo:
            def agregar(nombre, data):
                info = tarfile.TarInfo(nombre)
                info.size = len(data)
                info.mtime = 0
                archivo.addfile(info, io.BytesIO(data))

            agregar("oci-layout", b'{"imageLayoutVersion":"1.0.0"}')
            agregar("index.json", index_bytes)
            for data in layers + [config_bytes, manifest_bytes]:
                agregar("blobs/sha256/" + hashlib.sha256(data).hexdigest(), data)

        build = {
            "schema": artifact.BUILD_SCHEMA,
            "version": artifact.BUILD_VERSION,
            "runtime_base": {
                "layer_digests": digests[:heredados],
                "diff_ids": digests[:heredados],
                "runtime_config_sha256": artifact.sha256(artifact.canonical(CONFIG_RUNTIME)),
            },
            "output": {
                "manifest_digest": index["manifests"][0]["digest"],
                "config_digest": manifest["config"]["digest"],
                "replacements": [],
            },
        }
        for posicion, (declarado, data) in enumerate(self.reemplazos):
            indice = heredados + posicion
            binario = declarado["contenido"]
            propio = digests[indice] if indice < len(digests) else dig(data)
            build["output"]["replacements"].append({
                "path": declarado["path"],
                "mode": declarado.get("mode_declarado", 0o755),
                "uid": declarado.get("uid_declarado", 0),
                "gid": declarado.get("gid_declarado", 0),
                "layer_digest": propio,
                "diff_id": propio,
                "binary_sha256": artifact.sha256(binario),
                "binary_size": len(binario),
            })
        return ruta, build


def artefacto_de_dos_binarios():
    return ArtefactoSintetico([
        ({"path": "usr/bin/minio", "contenido": MINIO}, layer_de_binario("usr/bin/minio", MINIO)),
        ({"path": "usr/bin/mc", "contenido": MC}, layer_de_binario("usr/bin/mc", MC)),
    ])


class VerificadorOciTests(unittest.TestCase):
    def setUp(self):
        self.directorio = tempfile.TemporaryDirectory(prefix="task028-oci-")
        self.addCleanup(self.directorio.cleanup)

    def construir(self, artefacto, layers_extra=None):
        return artefacto.construir(self.directorio.name, layers_extra)

    def rechaza(self, ruta, build, fragmento):
        with self.assertRaises(artifact.VerificationError) as error:
            artifact.inspect_oci(ruta, build)
        self.assertIn(fragmento, str(error.exception))

    def test_el_artefacto_coherente_de_dos_binarios_se_acepta(self):
        ruta, build = self.construir(artefacto_de_dos_binarios())
        resultado = artifact.inspect_oci(ruta, build)
        self.assertEqual(resultado["replaced_paths"], ["usr/bin/minio", "usr/bin/mc"])
        self.assertEqual(resultado["inherited_layers"], 2)
        self.assertEqual(resultado["layers"], 4)
        self.assertTrue(resultado["only_declared_paths_replaced"])

    def test_un_tercer_archivo_dentro_del_layer_se_rechaza(self):
        artefacto = artefacto_de_dos_binarios()
        contaminado = tar_de([
            ("usr", tarfile.DIRTYPE, b"", 0o755, 0, 0),
            ("usr/bin", tarfile.DIRTYPE, b"", 0o755, 0, 0),
            ("usr/bin/minio", tarfile.REGTYPE, MINIO, 0o755, 0, 0),
            ("usr/bin/extra", tarfile.REGTYPE, b"pasajero", 0o755, 0, 0),
        ])
        ruta, build = self.construir(artefacto, [contaminado, artefacto.layers_extra[1]])
        self.rechaza(ruta, build, "distinto de ese path")

    def test_un_tercer_layer_no_declarado_se_rechaza(self):
        artefacto = artefacto_de_dos_binarios()
        polizon = layer_de_binario("usr/bin/extra", b"pasajero")
        ruta, build = self.construir(artefacto, artefacto.layers_extra + [polizon])
        self.rechaza(ruta, build, "layers declarados")

    def test_si_falta_minio_se_rechaza(self):
        artefacto = artefacto_de_dos_binarios()
        ruta, build = self.construir(artefacto, [artefacto.layers_extra[1]])
        self.rechaza(ruta, build, "layers declarados")

    def test_si_falta_mc_se_rechaza(self):
        artefacto = artefacto_de_dos_binarios()
        ruta, build = self.construir(artefacto, [artefacto.layers_extra[0]])
        self.rechaza(ruta, build, "layers declarados")

    def test_si_mc_se_sustituye_por_otro_path_se_rechaza(self):
        """El numero de layers es correcto, pero el segundo no es el declarado."""
        artefacto = artefacto_de_dos_binarios()
        impostor = layer_de_binario("usr/bin/otro", MC)
        ruta, build = self.construir(artefacto, [artefacto.layers_extra[0], impostor])
        self.rechaza(ruta, build, "distinto de ese path")

    def test_un_hash_de_binario_discrepante_se_rechaza(self):
        ruta, build = self.construir(artefacto_de_dos_binarios())
        build["output"]["replacements"][1]["binary_sha256"] = "0" * 64
        self.rechaza(ruta, build, "hash del binario")

    def test_un_tamano_de_binario_discrepante_se_rechaza(self):
        ruta, build = self.construir(artefacto_de_dos_binarios())
        build["output"]["replacements"][0]["binary_size"] += 1
        self.rechaza(ruta, build, "tamano del binario")

    def test_un_modo_inesperado_se_rechaza(self):
        artefacto = ArtefactoSintetico([
            ({"path": "usr/bin/minio", "contenido": MINIO},
             layer_de_binario("usr/bin/minio", MINIO, modo=0o777)),
            ({"path": "usr/bin/mc", "contenido": MC}, layer_de_binario("usr/bin/mc", MC)),
        ])
        ruta, build = self.construir(artefacto)
        self.rechaza(ruta, build, "modo o propietario")

    def test_un_propietario_inesperado_se_rechaza(self):
        artefacto = ArtefactoSintetico([
            ({"path": "usr/bin/minio", "contenido": MINIO}, layer_de_binario("usr/bin/minio", MINIO)),
            ({"path": "usr/bin/mc", "contenido": MC},
             layer_de_binario("usr/bin/mc", MC, uid=1000, gid=1000)),
        ])
        ruta, build = self.construir(artefacto)
        self.rechaza(ruta, build, "modo o propietario")

    def test_un_path_declarado_dos_veces_se_rechaza(self):
        ruta, build = self.construir(artefacto_de_dos_binarios())
        build["output"]["replacements"][1]["path"] = "usr/bin/minio"
        self.rechaza(ruta, build, "duplicado")

    def test_una_receta_sin_reemplazos_se_rechaza(self):
        ruta, build = self.construir(artefacto_de_dos_binarios())
        build["output"]["replacements"] = []
        self.rechaza(ruta, build, "ningun reemplazo")

    def test_un_layer_heredado_alterado_se_rechaza(self):
        ruta, build = self.construir(artefacto_de_dos_binarios())
        heredados = build["runtime_base"]["layer_digests"]
        build["runtime_base"]["layer_digests"] = [heredados[0], "sha256:" + "1" * 64]
        self.rechaza(ruta, build, "layers heredados")

    def test_un_entrypoint_alterado_se_rechaza(self):
        ruta, build = self.construir(artefacto_de_dos_binarios())
        build["runtime_base"]["runtime_config_sha256"] = "0" * 64
        self.rechaza(ruta, build, "entrypoint")


class RecetaTests(unittest.TestCase):
    """La receta real: cada parche declarado existe, se usa y nada sobra."""

    def setUp(self):
        self.manifest_path = ROOT / "docker/minio/build-manifest.json"
        self.build = json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def rechaza(self, build, fragmento):
        with self.assertRaises(artifact.VerificationError) as error:
            artifact.verify_recipe(ROOT, self.manifest_path, build)
        self.assertIn(fragmento, str(error.exception))

    def test_la_receta_real_es_coherente(self):
        esperado = artifact.sha256(self.manifest_path.read_bytes())
        self.assertEqual(artifact.verify_recipe(ROOT, self.manifest_path, self.build), esperado)

    def test_declara_las_dos_fuentes_y_los_tres_cambios(self):
        self.assertEqual(sorted(self.build["sources"]), ["mc", "minio"])
        objetivos = sorted(item["target"] for item in self.build["changes"])
        self.assertEqual(objetivos, ["mc", "minio", "minio"])
        rutas = {item["path"] for item in self.build["output"]["replacements"]}
        self.assertEqual(rutas, {"usr/bin/mc", "usr/bin/minio"})

    def test_un_parche_con_hash_incorrecto_se_rechaza(self):
        build = copy.deepcopy(self.build)
        build["changes"][1]["patch_sha256"] = "0" * 64
        self.rechaza(build, "hash de parche")

    def test_un_dockerfile_con_hash_incorrecto_se_rechaza(self):
        build = copy.deepcopy(self.build)
        build["recipe"]["dockerfile_sha256"] = "0" * 64
        self.rechaza(build, "hash de dockerfile")

    def test_un_parche_presente_pero_no_declarado_se_rechaza(self):
        """Un parche que vive en el arbol sin figurar en la receta es opaco."""
        build = copy.deepcopy(self.build)
        build["changes"] = build["changes"][:2]
        self.rechaza(build, "los parches presentes no son los declarados")

    def test_un_parche_declarado_que_la_receta_no_aplica_se_rechaza(self):
        """Declarar un parche que el Dockerfile nunca aplica es procedencia falsa.

        Se monta una copia de la receta en una raiz temporal para que el parche
        intruso exista en disco y el conjunto presente coincida con el
        declarado: asi la unica razon posible del rechazo es que la receta no lo
        aplica.
        """
        build = copy.deepcopy(self.build)
        with tempfile.TemporaryDirectory(prefix="task028-receta-") as directorio:
            raiz = Path(directorio)
            destino = raiz / "docker/minio"
            destino.mkdir(parents=True)
            for item in (ROOT / "docker/minio").iterdir():
                if item.is_file():
                    shutil.copy2(item, destino / item.name)
            intruso = destino / "intruso-no-aplicado.patch"
            intruso.write_bytes(b"--- a/go.mod\n+++ b/go.mod\n")
            build["changes"].append({
                "target": "minio",
                "patch": "docker/minio/intruso-no-aplicado.patch",
                "patch_sha256": artifact.sha256(intruso.read_bytes()),
            })
            with self.assertRaises(artifact.VerificationError) as error:
                artifact.verify_recipe(raiz, self.manifest_path, build)
        self.assertIn("no aplica el parche declarado", str(error.exception))

    def test_una_version_de_schema_antigua_se_rechaza(self):
        build = copy.deepcopy(self.build)
        build["version"] = 1
        self.rechaza(build, "schema de build desconocido")


if __name__ == "__main__":
    unittest.main()
