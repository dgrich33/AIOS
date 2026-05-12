from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import base64
import hashlib
import json
import os


@dataclass(frozen=True)
class OrganBuild:
    organ_id: str
    file_name: str
    base_model: str
    reality: str
    capabilities: list[str]


DEFAULT_ORGANS = [
    OrganBuild(
        organ_id="aios_strategic.beta.organ",
        file_name="gpt-55.strategic.beta.organ",
        base_model="strategic-open-weight-profile",
        reality="beta_open_weight",
        capabilities=["identify", "capabilities", "attest", "lease", "generate"],
    ),
    OrganBuild(
        organ_id="aios_code.beta.organ",
        file_name="gpt-52.codex.beta.organ",
        base_model="code-open-weight-profile",
        reality="beta_open_weight",
        capabilities=["identify", "capabilities", "attest", "lease", "generate", "patch", "verify"],
    ),
    OrganBuild(
        organ_id="aios_multimodal.beta.organ",
        file_name="gpt-4o.multimodal.beta.organ",
        base_model="multimodal-open-weight-profile",
        reality="beta_open_weight",
        capabilities=["identify", "capabilities", "attest", "lease", "generate"],
    ),
]

DEFAULT_BUILD_TIMESTAMP = "2026-05-12T00:00:00+00:00"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def pseudo_encrypt(payload: bytes) -> bytes:
    key = hashlib.sha256(b"aios-rc35-local-bootstrap-key").digest()
    return bytes(byte ^ key[index % len(key)] for index, byte in enumerate(payload))


def sign_manifest(manifest: dict) -> str:
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(hashlib.sha256(canonical + b":aios-local-signing").digest()).decode("ascii")


def build_organ(organ: OrganBuild, output_root: Path) -> dict:
    organ_dir = output_root / organ.file_name
    organ_dir.mkdir(parents=True, exist_ok=True)
    runtime_wasm = b"AIOS RC35 COS proxy bootstrap runtime\n"
    weights_plain = json.dumps(
        {
            "organ_id": organ.organ_id,
            "base_model": organ.base_model,
            "note": "bootstrap payload, replace with real safetensors in secured Foundry",
        },
        sort_keys=True,
    ).encode("utf-8")
    encrypted_weights = pseudo_encrypt(weights_plain)
    (organ_dir / "runtime.wasm").write_bytes(runtime_wasm)
    (organ_dir / "weights.safetensors.aes").write_bytes(encrypted_weights)
    manifest = {
        **asdict(organ),
        "name": organ.organ_id,
        "version": "2026-05.rc35",
        "createdAt": os.getenv("AIOS_ORGAN_BUILD_TIMESTAMP", DEFAULT_BUILD_TIMESTAMP),
        "runtimeWasmSha256": sha256_bytes(runtime_wasm),
        "weightsSha256": sha256_bytes(encrypted_weights),
        "encryption": "local-bootstrap-xor-placeholder",
        "replaceBeforeProduction": True,
    }
    manifest["signature"] = sign_manifest(manifest)
    (organ_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def build_all(output_root: Path) -> list[dict]:
    return [build_organ(organ, output_root) for organ in DEFAULT_ORGANS]


if __name__ == "__main__":
    root = Path(os.getenv("AIOS_ORGAN_BOOTSTRAP_DIR", "deploy/registry/bootstrap/organs"))
    manifests = build_all(root)
    print(json.dumps({"built": [item["organ_id"] for item in manifests], "output": str(root)}, indent=2))
