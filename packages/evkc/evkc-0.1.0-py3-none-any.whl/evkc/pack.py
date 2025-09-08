from __future__ import annotations

import hashlib
import json
import zipfile
from dataclasses import asdict
from pathlib import Path

from .crypto import ed25519_sign, load_key
from .manifest import Manifest, gen_artifact_index, load_manifest


def _read_file_bytes(p: Path) -> bytes:
    with p.open("rb") as f:
        return f.read()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pack_capsule(folder: Path | str, out_path: Path | str | None = None, signer_priv_key_path: Path | str | None = None) -> Path:
    """
    Build a capsule zip from a folder that contains manifest.json (or construct it),
    add artifact index if missing, and optionally sign the archive.

    Returns the path to the .evkc.zip file.
    """
    root = Path(folder)
    manifest_path = root / "manifest.json"
    if manifest_path.exists():
        # Use loader so dataclasses are constructed properly
        manifest = load_manifest(manifest_path)
    else:
        # Minimal manifest inference
        manifest = Manifest(
            name=root.name,
            version="0.0.0",
            description=f"Auto-generated manifest for {root.name}",
        )

    # Ensure artifacts list and fill missing hashes by regenerating full index
    needs_artifacts = (
        not manifest.artifacts
        or any(getattr(a, "sha256", None) in (None, "") for a in manifest.artifacts)
    )
    if needs_artifacts:
        manifest.artifacts = gen_artifact_index(root)
        (root / "manifest.json").write_text(json.dumps(asdict(manifest), indent=2), encoding="utf-8")

    # Output path
    out = Path(out_path) if out_path else root.with_suffix("")
    out = out.with_name(f"{out.name}.evkc.zip")

    # Create zip
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in root.rglob("*"):
            if p.is_file():
                arcname = p.relative_to(root).as_posix()
                z.write(p, arcname)

    # Sign if key provided (ed25519 over archive bytes)
    if signer_priv_key_path:
        data = _read_file_bytes(out)
        priv = load_key(signer_priv_key_path)
        sig = ed25519_sign(priv, data)
        (out.parent / f"{out.name}.SIGNATURE").write_bytes(sig)

    return out
