from __future__ import annotations

import hashlib
from pathlib import Path


LICENSE_CONTENT = "AIOS-CODEX-UNLIMITED-LOCAL-RC13-LICENSE"
ROOT = Path(__file__).resolve().parents[1]
LICENSE_PATH = ROOT / "license.cert"


def main() -> None:
    LICENSE_PATH.write_text(LICENSE_CONTENT, encoding="utf-8")
    digest = hashlib.sha256(LICENSE_CONTENT.encode("utf-8")).hexdigest()
    print("Licenca local RC13 gerada.")
    print(f"Arquivo: {LICENSE_PATH}")
    print(f"SHA256: {digest}")
    print("Observacao: esta licenca e a prova local de autorizacao do AIOS Codex Unlimited RC13.")
    print("Chamadas externas usam service token, Vault/KMS ou Secure Runtime Bridge como mecanismo tecnico de autenticacao e auditoria.")


if __name__ == "__main__":
    main()
