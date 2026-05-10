import json
from urllib import request
from urllib.error import URLError

from .config import get_settings


_local_vault: dict[str, dict] = {}


class VaultClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def write_secret(self, name: str, payload: dict) -> dict:
        if not self.settings.vault_url or not self.settings.vault_token:
            _local_vault[name] = payload
            return {"mode": "memory", "name": name}
        body = json.dumps({"data": payload}).encode("utf-8")
        req = request.Request(
            f"{self.settings.vault_url.rstrip('/')}/v1/secret/data/{name}",
            data=body,
            method="POST",
            headers={"X-Vault-Token": self.settings.vault_token, "Content-Type": "application/json"},
        )
        try:
            with request.urlopen(req, timeout=5) as response:
                return {"mode": "vault", "status": response.status, "name": name}
        except URLError:
            _local_vault[name] = payload
            return {"mode": "memory-fallback", "name": name}

    def read_secret(self, name: str) -> dict:
        if not self.settings.vault_url or not self.settings.vault_token:
            return {"mode": "memory", "name": name, "data": _local_vault.get(name, {})}
        req = request.Request(
            f"{self.settings.vault_url.rstrip('/')}/v1/secret/data/{name}",
            method="GET",
            headers={"X-Vault-Token": self.settings.vault_token},
        )
        try:
            with request.urlopen(req, timeout=5) as response:
                body = json.loads(response.read().decode("utf-8"))
            return {"mode": "vault", "name": name, "data": body.get("data", {}).get("data", {})}
        except URLError:
            return {"mode": "memory-fallback", "name": name, "data": _local_vault.get(name, {})}
