from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess


@dataclass(frozen=True)
class EvidenceItem:
    name: str
    sha256: str
    bytes: int
    vault_uri: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class EvidenceVault:
    def __init__(self, bucket: str | None = None, local_root: Path | None = None):
        self.bucket = bucket or os.getenv("VAULT_BUCKET", "s3://aios-vault")
        self.local_root = local_root or Path(os.getenv("AIOS_LOCAL_VAULT_DIR", "deploy/evidence-vault"))

    def upload(self, mission_id: str, paths: list[Path]) -> list[EvidenceItem]:
        if not mission_id.strip():
            raise ValueError("mission_id is required")
        items: list[EvidenceItem] = []
        for path in paths:
            if not path.exists() or not path.is_file():
                raise FileNotFoundError(path)
            digest = sha256_file(path)
            key = f"{mission_id}/{path.name}"
            if self.bucket.startswith("s3://"):
                vault_uri = self._upload_s3(path, key)
            else:
                vault_uri = self._upload_local(path, key)
            items.append(EvidenceItem(path.name, digest, path.stat().st_size, vault_uri))
        return items

    def _upload_local(self, path: Path, key: str) -> str:
        target = self.local_root / key
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        return target.as_posix()

    def _upload_s3(self, path: Path, key: str) -> str:
        uri = f"{self.bucket.rstrip('/')}/{key}"
        aws = shutil.which("aws")
        if not aws:
            return self._upload_local(path, key)
        subprocess.run([aws, "s3", "cp", str(path), uri], check=True)
        return uri


def write_ledger_record(mission_id: str, items: list[EvidenceItem], ledger_path: Path) -> dict:
    record = {
        "missionId": mission_id,
        "evidence": [asdict(item) for item in items],
    }
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return record


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upload mission evidence and write ledger record.")
    parser.add_argument("mission_id")
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--ledger", type=Path, default=Path("deploy/evidence-vault/ledger.jsonl"))
    args = parser.parse_args()
    vault = EvidenceVault()
    uploaded = vault.upload(args.mission_id, args.files)
    print(json.dumps(write_ledger_record(args.mission_id, uploaded, args.ledger), indent=2))

