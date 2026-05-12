from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
import re


@dataclass(frozen=True)
class SentinelRule:
    kind: str
    subject: str
    qualifier: str = ""
    value: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


ALLOW_RE = re.compile(r"^allow\s+(?P<subject>\S+)\s+(?P<qualifier>role:\S+)$")
DENY_RE = re.compile(r"^deny\s+(?P<subject>\S+)\s+(?P<qualifier>cmd:\S+)$")
LIMIT_RE = re.compile(r"^limit\s+rate\s+(?P<subject>\S+)\s+(?P<qualifier>per_minute)\s+(?P<value>\d+)$")
REQUIRE_RE = re.compile(r"^require\s+(?P<subject>\S+)\s+before\s+(?P<value>\S+)$")
MASK_RE = re.compile(r"^mask\s+(?P<subject>\S+)\s+(?P<value>.+)$")


def parse_line(line: str) -> SentinelRule | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    for kind, pattern in (
        ("allow", ALLOW_RE),
        ("deny", DENY_RE),
        ("limit_rate", LIMIT_RE),
        ("require", REQUIRE_RE),
        ("mask", MASK_RE),
    ):
        match = pattern.match(stripped)
        if match:
            data = match.groupdict(default="")
            return SentinelRule(kind=kind, subject=data.get("subject", ""), qualifier=data.get("qualifier", ""), value=data.get("value", ""))
    raise ValueError(f"Invalid Sentinel DSL v0.3 rule: {stripped}")


def parse_policy(text: str) -> list[SentinelRule]:
    rules: list[SentinelRule] = []
    for line in text.splitlines():
        rule = parse_line(line)
        if rule:
            rules.append(rule)
    return rules


def compile_to_manifest(policy_path: Path, output_path: Path) -> dict:
    rules = parse_policy(policy_path.read_text(encoding="utf-8"))
    manifest = {
        "dslVersion": "0.3",
        "source": policy_path.as_posix(),
        "rules": [rule.to_dict() for rule in rules],
        "ebpfMode": "manifest_only_until_kernel_loader_available",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compile AIOS Policy Sentinel DSL v0.3")
    parser.add_argument("policy", type=Path)
    parser.add_argument("--out", type=Path, default=Path("deploy/policy/sentinel-v0.3.manifest.json"))
    args = parser.parse_args()
    compile_to_manifest(args.policy, args.out)
