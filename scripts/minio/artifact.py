#!/usr/bin/env python3
"""Verifica, atesta y compara el derivado reproducible de MinIO de Task/027.1."""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import tarfile
from pathlib import Path
from typing import Any

ATTESTATION_SCHEMA = "personal-blog-infra/minio-derivative-attestation"
BUILD_SCHEMA = "personal-blog-infra/minio-reproducible-build"


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

        layers = [item["digest"] for item in manifest.get("layers") or []]
        diff_ids = config.get("rootfs", {}).get("diff_ids") or []
        if layers[:-1] != build["runtime_base"]["layer_digests"]:
            raise VerificationError("los layers heredados no son los de la base fijada")
        if diff_ids[:-1] != build["runtime_base"]["diff_ids"]:
            raise VerificationError("los diff IDs heredados no son los de la base fijada")
        if len(layers) != 10 or len(diff_ids) != 10:
            raise VerificationError("el derivado no agrega exactamente un layer")
        if layers[-1] != expected["replacement_layer_digest"]:
            raise VerificationError("layer de reemplazo inesperado")
        if diff_ids[-1] != expected["replacement_diff_id"]:
            raise VerificationError("diff ID de reemplazo inesperado")

        layer_bytes = archive.extractfile(blob_name(layers[-1])).read()
        with tarfile.open(fileobj=io.BytesIO(layer_bytes), mode="r:*") as layer:
            members = layer.getmembers()
            if [m.name for m in members] != ["usr", "usr/bin", "usr/bin/minio"]:
                raise VerificationError("el ultimo layer modifica algo distinto de /usr/bin/minio")
            member = layer.getmember("usr/bin/minio")
            binary = layer.extractfile(member).read()
            if (member.mode, member.uid, member.gid) != (0o755, 0, 0):
                raise VerificationError("modo o propietario de /usr/bin/minio inesperado")
            if sha256(binary) != expected["binary_sha256"] or len(binary) != expected["binary_size"]:
                raise VerificationError("binario MinIO inesperado")

    return {
        "manifest_digest": checks["manifest_digest"],
        "config_digest": checks["config_digest"],
        "binary_sha256": expected["binary_sha256"],
        "binary_size": expected["binary_size"],
        "layers": len(layers),
        "only_minio_replaced": True,
    }


def verify_recipe(root: Path, manifest_path: Path, build: dict[str, Any]) -> str:
    if build.get("schema") != BUILD_SCHEMA or build.get("version") != 1:
        raise VerificationError("schema de build desconocido")
    for section, path_key, hash_key in (
        ("recipe", "dockerfile", "dockerfile_sha256"),
        ("change", "patch", "patch_sha256"),
    ):
        data = (root / build[section][path_key]).read_bytes()
        if sha256(data) != build[section][hash_key]:
            raise VerificationError(f"hash de {path_key} no coincide")
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
                "source_commit": build["source"]["commit"],
                "binary_sha256": result["binary_sha256"],
                "only_minio_replaced": True,
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
                            {"uri": build["source"]["repository"], "digest": {"gitCommit": build["source"]["commit"]}},
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
