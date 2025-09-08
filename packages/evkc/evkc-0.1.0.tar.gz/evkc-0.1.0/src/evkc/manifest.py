from __future__ import annotations

import dataclasses as dc
import hashlib
import json
from pathlib import Path
from typing import Any


@dc.dataclass
class Artifact:
    path: str
    sha256: str


@dc.dataclass
class Step:
    name: str
    command: list[str]
    expected_exit_code: int = 0
    # Optional: PCT or proof artifact ids
    proofs: list[str] | None = None


@dc.dataclass
class Policy:
    # Very conservative defaults; runner can enforce
    network: bool = False
    filesystem_write: bool = False
    max_seconds: int = 60
    max_memory_mb: int = 512


@dc.dataclass
class Manifest:
    name: str
    version: str
    description: str
    # Fully pinned dependencies (optional for samples)
    requirements: list[str] | None = None
    entrypoint: list[str] | None = None
    steps: list[Step] | None = None
    artifacts: list[Artifact] | None = None
    policy: Policy = dc.field(default_factory=Policy)
    # signer pub key, signature stored beside archive; can also embed
    signer_fingerprint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return dc.asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(path: Path | str) -> Manifest:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # Manual construction for type clarity
    artifacts = [Artifact(**a) for a in data.get("artifacts", [])]
    steps = [Step(**s) for s in data.get("steps", [])]
    policy = Policy(**data.get("policy", {}))
    return Manifest(
        name=data["name"],
        version=data["version"],
        description=data.get("description", ""),
        requirements=data.get("requirements"),
        entrypoint=data.get("entrypoint"),
        steps=steps,
        artifacts=artifacts,
        policy=policy,
        signer_fingerprint=data.get("signer_fingerprint"),
    )


def gen_artifact_index(root: Path) -> list[Artifact]:
    items: list[Artifact] = []
    for p in root.rglob("*"):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            # Skip manifest and signatures if present
            if rel in ("manifest.json", "SIGNATURE", "SIGNER.pub"):
                continue
            items.append(Artifact(path=rel, sha256=_sha256_file(p)))
    return items
