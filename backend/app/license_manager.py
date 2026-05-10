import hashlib
from pathlib import Path


LOCAL_LICENSE_CONTENT = "AIOS-CODEX-UNLIMITED-LOCAL-RC13-LICENSE"


def license_status(path: str, authorized_hash: str) -> dict:
    license_path = Path(path)
    present = license_path.exists() and license_path.is_file()
    digest = ""
    if present:
        digest = hashlib.sha256(license_path.read_bytes()).hexdigest()
    authorized = bool(present and digest and digest.lower() == authorized_hash.lower())
    return {
        "phase": "RC13_LOCAL_LICENSE",
        "status": "local_unlimited_enabled" if authorized else "restricted",
        "licensePresent": present,
        "hashAuthorized": authorized,
        "hash": digest,
        "licensePath": str(license_path),
        "entitlementId": "aios_codex_unlimited",
        "priorityClass": "premium_unlimited",
        "productUnit": "codex_sessions",
        "authorizationScope": "aios_codex_unlimited_enterprise_runtime",
        "authorizesOfficialRuntime": authorized,
        "authorizesPersistentServiceTokens": authorized,
        "allowsControlledRuntimeArtifacts": authorized,
        "runtimeCredentialBinding": "service_token_vault_kms_or_secure_runtime_bridge",
        "providerBillingMode": "approved_runtime_service_account_policy" if authorized else "restricted",
        "technicalCredentialStoredInLicense": False,
        "unlocksOfficialRuntime": authorized,
        "unlocksProviderBilling": authorized,
        "secretsExposed": False,
        "message": (
            "license.cert reconhecida como prova local de autorizacao do AIOS Codex Unlimited RC13. Ela ativa entitlement e permissao de runtime no AIOS; chamadas externas usam service token, Vault/KMS ou Secure Runtime Bridge como mecanismo tecnico de autenticacao e auditoria."
            if authorized
            else "license.cert ausente ou invalida. O AIOS permanece restrito ate receber uma prova local de autorizacao valida."
        ),
    }
