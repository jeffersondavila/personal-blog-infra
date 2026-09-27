#!/usr/bin/env python3
"""Verifica, atesta y compara el derivado reproducible de MinIO (Task/027.1, ampliado por Task/028)."""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any

ATTESTATION_SCHEMA = "personal-blog-infra/minio-derivative-attestation"
BUILD_SCHEMA = "personal-blog-infra/minio-reproducible-build"
BUILD_VERSION = 2


class VerificationError(Exception):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def blob_name(digest: str) -> str:
    algorithm, value = digest.split(":", 1)
    if algorithm != "sha256" or len(value) != 64:
        raise VerificationError("digest OCI no soportado")
    return f"blobs/sha256/{value}"


def inspect_oci(oci: Path, build: dict[str, Any]) -> dict[str, Any]:
    with tarfile.open(oci, "r") as archive:
        index_bytes = archive.extractfile("index.json").read()
        index = json.loads(index_bytes)
        descriptors = index.get("manifests") or []
        if len(descriptors) != 1:
            raise VerificationError("el OCI no contiene exactamente un manifest")
        descriptor = descriptors[0]
        if descriptor.get("platform") != {"architecture": "amd64", "os": "linux"}:
            raise VerificationError("plataforma OCI inesperada")

        manifest_bytes = archive.extractfile(blob_name(descriptor["digest"])).read()
        if "sha256:" + sha256(manifest_bytes) != descriptor["digest"]:
            raise VerificationError("digest del manifest OCI invalido")
        manifest = json.loads(manifest_bytes)
        config_bytes = archive.extractfile(blob_name(manifest["config"]["digest"])).read()
        if "sha256:" + sha256(config_bytes) != manifest["config"]["digest"]:
            raise VerificationError("digest de config OCI invalido")
        config = json.loads(config_bytes)

        expected = build["output"]
        checks = {
            "manifest_digest": descriptor["digest"],
            "config_digest": manifest["config"]["digest"],
            "runtime_config_sha256": sha256(canonical(config.get("config"))),
        }
        for key in ("manifest_digest", "config_digest"):
            if checks[key] != expected[key]:
                raise VerificationError(f"{key} inesperado")
        if checks["runtime_config_sha256"] != build["runtime_base"]["runtime_config_sha256"]:
            raise VerificationError("entrypoint/cmd/env/labels del runtime cambiaron")

        # Task/028 (H-028-2): el derivado sustituye DOS binarios, no uno. El
        # contrato evoluciona en lugar de relajarse: la receta declara cada
        # reemplazo y aqui se exige que sean EXACTAMENTE esos, en ese orden, cada
        # uno en su propio layer y sin tocar ningun otro archivo.
        replacements = expected.get("replacements")
        if not isinstance(replacements, list) or not replacements:
            raise VerificationError("la receta no declara ningun reemplazo")
        heredados = len(build["runtime_base"]["layer_digests"])
        total = heredados + len(replacements)

        layers = [item["digest"] for item in manifest.get("layers") or []]
        diff_ids = config.get("rootfs", {}).get("diff_ids") or []
        if len(layers) != total or len(diff_ids) != total:
            raise VerificationError("el derivado no agrega exactamente los layers declarados")
        if layers[:heredados] != build["runtime_base"]["layer_digests"]:
            raise VerificationError("los layers heredados no son los de la base fijada")
        if diff_ids[:heredados] != build["runtime_base"]["diff_ids"]:
            raise VerificationError("los diff IDs heredados no son los de la base fijada")

        declarados = [item["path"] for item in replacements]
        if len(set(declarados)) != len(declarados):
            raise VerificationError("la receta declara un path de reemplazo duplicado")

        vistos = []
        for posicion, item in enumerate(replacements):
            indice = heredados + posicion
            if layers[indice] != item["layer_digest"]:
                raise VerificationError(f"layer de reemplazo inesperado para {item['path']}")
            if diff_ids[indice] != item["diff_id"]:
                raise VerificationError(f"diff ID de reemplazo inesperado para {item['path']}")

            ruta = item["path"]
            partes = ruta.split("/")
            esperados = ["/".join(partes[:n + 1]) for n in range(len(partes))]
            layer_bytes = archive.extractfile(blob_name(layers[indice])).read()
            with tarfile.open(fileobj=io.BytesIO(layer_bytes), mode="r:*") as layer:
                if [m.name for m in layer.getmembers()] != esperados:
                    raise VerificationError(f"el layer de {ruta} modifica algo distinto de ese path")
                member = layer.getmember(ruta)
                if not member.isfile():
                    raise VerificationError(f"{ruta} no es un archivo regular")
                binary = layer.extractfile(member).read()
                if (member.mode, member.uid, member.gid) != (item["mode"], item["uid"], item["gid"]):
                    raise VerificationError(f"modo o propietario de {ruta} inesperado")
                if sha256(binary) != item["binary_sha256"]:
                    raise VerificationError(f"hash del binario {ruta} inesperado")
                if len(binary) != item["binary_size"]:
                    raise VerificationError(f"tamano del binario {ruta} inesperado")
            vistos.append(ruta)

        if vistos != declarados:
            raise VerificationError("los reemplazos observados no son los declarados")

    return {
        "manifest_digest": checks["manifest_digest"],
        "config_digest": checks["config_digest"],
        "replaced_paths": vistos,
        "replacements": {
            item["path"]: {"sha256": item["binary_sha256"], "size": item["binary_size"]}
            for item in replacements
        },
        "layers": len(layers),
        "inherited_layers": heredados,
        "only_declared_paths_replaced": True,
    }


def verify_recipe(root: Path, manifest_path: Path, build: dict[str, Any]) -> str:
    if build.get("schema") != BUILD_SCHEMA or build.get("version") != BUILD_VERSION:
        raise VerificationError("schema de build desconocido")

    dockerfile = (root / build["recipe"]["dockerfile"]).read_bytes()
    if sha256(dockerfile) != build["recipe"]["dockerfile_sha256"]:
        raise VerificationError("hash de dockerfile no coincide")

    # Cada parche declarado debe existir y coincidir byte a byte. Y el Dockerfile
    # debe aplicar exactamente esos parches y ninguno mas: si un parche vive en el
    # arbol pero la receta no lo usa, o al reves, la identidad no es verificable.
    cambios = build["changes"]
    if not cambios:
        raise VerificationError("el build no declara ningun cambio")
    declarados: list[str] = []
    for cambio in cambios:
        ruta = cambio["patch"]
        if ruta in declarados:
            raise VerificationError(f"parche duplicado en changes: {ruta}")
        declarados.append(ruta)
        data = (root / ruta).read_bytes()
        if sha256(data) != cambio["patch_sha256"]:
            raise VerificationError(f"hash de parche no coincide: {ruta}")
        nombre = PurePosixPath(ruta).name
        if nombre.encode() not in dockerfile:
            raise VerificationError(f"la receta no aplica el parche declarado: {ruta}")

    receta_dir = PurePosixPath(build["recipe"]["dockerfile"]).parent
    presentes = sorted(
        str(receta_dir / item.name) for item in (root / receta_dir).iterdir()
        if item.is_file() and item.name.endswith(".patch")
    )
    if presentes != sorted(declarados):
        raise VerificationError("los parches presentes no son los declarados")

    return sha256(manifest_path.read_bytes())


def normalize_sbom(document: Any, build: dict[str, Any]) -> Any:
    data = copy.deepcopy(document)
    data.pop("serialNumber", None)
    metadata = data.get("metadata") or {}
    metadata.pop("timestamp", None)
    component = metadata.get("component") or {}
    root_old_ref = component.get("bom-ref")
    component["name"] = build["output"]["reference"]
    component["version"] = build["output"]["manifest_digest"]
    root_new_ref = "urn:personal-blog:minio:" + build["output"]["manifest_digest"]
    component["bom-ref"] = root_new_ref
    metadata["component"] = component
    data["metadata"] = metadata

    replacements: dict[str, str] = {}
    if root_old_ref:
        replacements[root_old_ref] = root_new_ref
    for item in data.get("components") or []:
        old = item.get("bom-ref")
        identity = {key: item.get(key) for key in ("type", "group", "name", "version", "purl")}
        new = "urn:personal-blog:component:sha256:" + sha256(canonical(identity))
        if old:
            replacements[old] = new
        item["bom-ref"] = new
        if isinstance(item.get("properties"), list):
            item["properties"].sort(key=lambda value: canonical(value))

    def replace_refs(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: replace_refs(item) for key, item in value.items()}
        if isinstance(value, list):
            return [replace_refs(item) for item in value]
        if isinstance(value, str):
            return replacements.get(value, value)
        return value

    data = replace_refs(data)
    for dependency in data.get("dependencies") or []:
        if isinstance(dependency.get("dependsOn"), list):
            dependency["dependsOn"].sort()
    for key in ("components", "dependencies", "vulnerabilities", "services"):
        if isinstance(data.get(key), list):
            data[key].sort(key=lambda item: canonical(item))
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path("."))
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--oci", type=Path, required=True)
    attest = sub.add_parser("attest")
    attest.add_argument("--oci", type=Path, required=True)
    attest.add_argument("--report", type=Path, required=True)
    sbom = sub.add_parser("canonicalize-sbom")
    sbom.add_argument("--input", type=Path, required=True)
    sbom.add_argument("--output", type=Path, required=True)
    provenance = sub.add_parser("provenance")
    provenance.add_argument("--oci", type=Path, required=True)
    provenance.add_argument("--sbom", type=Path, required=True)
    provenance.add_argument("--output", type=Path, required=True)
    compare = sub.add_parser("compare")
    compare.add_argument("--first", type=Path, required=True)
    compare.add_argument("--second", type=Path, required=True)

    args = parser.parse_args()
    build = read_json(args.manifest)
    try:
        manifest_sha = verify_recipe(args.root, args.manifest, build)
        if args.command == "verify":
            result = inspect_oci(args.oci, build)
            result["build_manifest_sha256"] = manifest_sha
            print(json.dumps(result, sort_keys=True))
        elif args.command == "attest":
            result = inspect_oci(args.oci, build)
            report = read_json(args.report)
            report["ArtifactName"] = build["output"]["reference"] + "@" + result["manifest_digest"]
            metadata = report.setdefault("Metadata", {})
            repository = build["output"]["reference"].rsplit(":", 1)[0]
            metadata["RepoDigests"] = [repository + "@" + result["manifest_digest"]]
            metadata["PersonalBlogDerivative"] = {
                "schema": ATTESTATION_SCHEMA,
                "build_manifest_sha256": manifest_sha,
                "source_commits": {
                    nombre: datos["commit"] for nombre, datos in sorted(build["sources"].items())
                },
                "replacements": result["replacements"],
                "only_declared_paths_replaced": True,
            }
            args.report.write_bytes(canonical(report) + b"\n")
            print("attestation_ok=true")
        elif args.command == "canonicalize-sbom":
            normalized = normalize_sbom(read_json(args.input), build)
            args.output.write_bytes(canonical(normalized) + b"\n")
            print("canonical_sbom_sha256=" + sha256(args.output.read_bytes()))
        elif args.command == "provenance":
            subject = inspect_oci(args.oci, build)
            statement = {
                "_type": "https://in-toto.io/Statement/v1",
                "predicateType": "https://slsa.dev/provenance/v1",
                "subject": [{
                    "name": build["output"]["reference"],
                    "digest": {"sha256": subject["manifest_digest"].split(":", 1)[1]},
                }],
                "predicate": {
                    "buildDefinition": {
                        "buildType": "personal-blog-infra/minio-route-a-v1",
                        "externalParameters": {
                            "platform": build["platform"],
                            "source_date_epoch": build["source_date_epoch"],
                        },
                        "resolvedDependencies": [
                            {
                                "name": nombre,
                                "uri": datos["repository"],
                                "digest": {"gitCommit": datos["commit"]},
                            }
                            for nombre, datos in sorted(build["sources"].items())
                        ] + [
                            {"uri": build["recipe"]["builder_platform_manifest"]},
                            {"uri": build["runtime_base"]["platform_manifest"]},
                        ],
                    },
                    "runDetails": {
                        "builder": {"id": "personal-blog-infra/docker-minio-route-a"},
                        "metadata": {"invocationId": "reproducible-local-build"},
                    },
                    "byproducts": [{
                        "name": "cyclonedx-sbom",
                        "digest": {"sha256": sha256(args.sbom.read_bytes())},
                    }],
                },
            }
            args.output.write_bytes(canonical(statement) + b"\n")
            print("provenance_sha256=" + sha256(args.output.read_bytes()))
        elif args.command == "compare":
            first = inspect_oci(args.first, build)
            second = inspect_oci(args.second, build)
            if first != second:
                raise VerificationError("las identidades OCI difieren")
            print(json.dumps({"reproducible": True, **first}, sort_keys=True))
    except (KeyError, OSError, tarfile.TarError, ValueError, VerificationError) as error:
        print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
