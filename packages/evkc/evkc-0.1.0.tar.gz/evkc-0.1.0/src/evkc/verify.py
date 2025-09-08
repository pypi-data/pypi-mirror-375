from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from .crypto import ed25519_verify
from .manifest import Artifact


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_capsule(archive: Path | str) -> tuple[bool, str]:
    """
    Verify manifest integrity and artifact hashes; if a sidecar SIGNATURE file exists,
    check that it matches the archive digest (placeholder signature model).
    Returns (ok, message).
    """
    ap = Path(archive)
    if not ap.exists():
        return False, f"Archive not found: {ap}"

    with zipfile.ZipFile(ap, "r") as z:
        if "manifest.json" not in z.namelist():
            return False, "manifest.json missing in capsule"
        manifest_data = z.read("manifest.json")
        manifest = json.loads(manifest_data.decode("utf-8"))
        artifacts = [Artifact(**a) for a in manifest.get("artifacts", [])]

        # Verify artifacts
        for a in artifacts:
            if a.path not in z.namelist():
                return False, f"artifact missing: {a.path}"
            calc = _sha256_bytes(z.read(a.path))
            if calc != a.sha256:
                return False, f"artifact hash mismatch: {a.path}"

    # Verify sidecar signature (ed25519). If SIGNER.pub exists alongside archive, use it.
    sig_path = ap.parent / f"{ap.name}.SIGNATURE"
    pub_path = ap.parent / f"{ap.name}.SIGNER.pub"
    if sig_path.exists() and pub_path.exists():
        sig = sig_path.read_bytes()
        pub = pub_path.read_bytes()
        data = ap.read_bytes()
        if not ed25519_verify(pub, data, sig):
            return False, "archive signature invalid"

    return True, "OK"
