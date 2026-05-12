.PHONY: build-beta-organs push-beta-organs verify-bootstrap clean

OUT_DIR ?= ../deploy/registry/bootstrap/organs

build-beta-organs:
	AIOS_ORGAN_BOOTSTRAP_DIR="$(OUT_DIR)" python foundry.py

verify-bootstrap: build-beta-organs
	python - <<'PY'
from pathlib import Path
import json

root = Path("$(OUT_DIR)")
required = [
    "gpt-55.strategic.beta.organ",
    "gpt-52.codex.beta.organ",
    "gpt-4o.multimodal.beta.organ",
]
for name in required:
    manifest = root / name / "manifest.json"
    if not manifest.exists():
        raise SystemExit(f"missing {manifest}")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("reality") != "beta_open_weight":
        raise SystemExit(f"{manifest} has wrong reality")
    if not data.get("replaceBeforeProduction"):
        raise SystemExit(f"{manifest} must stay marked replaceBeforeProduction")
print("bootstrap organs verified")
PY

push-beta-organs:
	@if ! command -v aiosctl >/dev/null 2>&1; then \
		echo "aiosctl not found. Install/configure aiosctl before pushing organs."; \
		exit 1; \
	fi
	aiosctl organ push "$(OUT_DIR)"/*.organ

clean:
	rm -rf "$(OUT_DIR)"
