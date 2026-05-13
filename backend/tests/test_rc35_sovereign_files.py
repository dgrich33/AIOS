from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = spec_from_file_location(name, path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_sentinel_v03_default_policy_compiles(tmp_path) -> None:
    sentinel = load_module("sentinel_dsl", REPO_ROOT / "aios-codex-fabric" / "sentinel" / "sentinel_dsl.py")
    policy = REPO_ROOT / "aios-codex-specs" / "policy" / "sentinel-default.v0.3.aiosdsl"
    manifest = sentinel.compile_to_manifest(policy, tmp_path / "sentinel.json")
    assert manifest["dslVersion"] == "0.3"
    assert any(rule["kind"] == "allow" and rule["subject"] == "organ:codex.plan.core" for rule in manifest["rules"])
    assert any(rule["kind"] == "deny" and rule["subject"] == "tool:TerminalRunner" for rule in manifest["rules"])
    assert any(rule["kind"] == "limit_rate" and rule["value"] == "30" for rule in manifest["rules"])


def test_foundry_builds_three_signed_beta_organs(tmp_path) -> None:
    foundry = load_module("foundry", REPO_ROOT / "aios-codex-foundry" / "foundry.py")
    manifests = foundry.build_all(tmp_path / "organs")
    assert {item["organ_id"] for item in manifests} == {
        "aios_strategic.beta.organ",
        "aios_code.beta.organ",
        "aios_multimodal.beta.organ",
    }
    for manifest in manifests:
        manifest_path = tmp_path / "organs" / manifest["file_name"] / "manifest.json"
        weights_path = tmp_path / "organs" / manifest["file_name"] / "weights.safetensors.aes"
        assert manifest_path.exists()
        assert weights_path.exists()
        assert manifest["reality"] == "beta_open_weight"
        assert manifest["signature"]


def test_evidence_vault_writes_local_copy_and_ledger(tmp_path) -> None:
    evidence = load_module("evidence_vault", REPO_ROOT / "aios-codex-fabric" / "evidence" / "evidence_vault.py")
    patch = tmp_path / "patch.diff"
    patch.write_text("diff --git a/a b/a\n", encoding="utf-8")
    vault = evidence.EvidenceVault(bucket="file://local", local_root=tmp_path / "vault")
    items = vault.upload("mission-1", [patch])
    record = evidence.write_ledger_record("mission-1", items, tmp_path / "ledger.jsonl")
    assert items[0].sha256
    assert Path(items[0].vault_uri).exists()
    assert record["missionId"] == "mission-1"
    assert "patch.diff" in (tmp_path / "ledger.jsonl").read_text(encoding="utf-8")


def test_rc35_prod_scripts_manage_cluster_secret_readiness_without_literal_args() -> None:
    preflight = (REPO_ROOT / "scripts" / "rc35-prod-preflight.ps1").read_text(encoding="utf-8")
    deploy = (REPO_ROOT / "scripts" / "rc35-prod-deploy.ps1").read_text(encoding="utf-8")

    assert "vault-creds" in preflight
    assert "aios-registry-pull-secret" in preflight
    assert "MISSING SECRETS - run rc35-prod-deploy.ps1 -CreateClusterSecrets first." in preflight
    assert "exit 2" in preflight
    assert "CreateClusterSecrets" in deploy
    assert "AIOS_REGISTRY_DOCKERCONFIGJSON" in deploy
    assert "kubectl apply -f -" in deploy
    assert "--from-literal" not in deploy


def test_rc35_docs_put_first_install_deploy_before_preflight() -> None:
    operations = (REPO_ROOT / "docs" / "RC35_PRODUCTION_OPERATIONS.md").read_text(encoding="utf-8")
    overlay_readme = (REPO_ROOT / "deploy" / "kustomize" / "prod" / "README.md").read_text(encoding="utf-8")

    first_install = operations.index("## First Install")
    deploy_first = operations.index(".\\scripts\\rc35-prod-deploy.ps1 -CreateClusterSecrets", first_install)
    preflight_after = operations.index(".\\scripts\\rc35-prod-preflight.ps1", deploy_first)
    assert deploy_first < preflight_after
    assert "For later deployments" in operations
    assert "idempotent" in overlay_readme.lower()
