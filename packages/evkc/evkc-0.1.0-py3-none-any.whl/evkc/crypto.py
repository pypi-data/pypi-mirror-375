from __future__ import annotations

import base64
import hashlib
from pathlib import Path

try:
    from nacl.exceptions import BadSignatureError
    from nacl.signing import SigningKey, VerifyKey
except Exception:  # pragma: no cover
    SigningKey = None  # type: ignore
    VerifyKey = None  # type: ignore
    BadSignatureError = Exception  # type: ignore


def require_crypto():
    if SigningKey is None:
        raise RuntimeError("PyNaCl is required: pip install pynacl")


def ed25519_keygen() -> tuple[bytes, bytes]:
    require_crypto()
    sk = SigningKey.generate()
    vk = sk.verify_key
    return bytes(sk), bytes(vk)


def ed25519_sign(privkey_bytes: bytes, data: bytes) -> bytes:
    require_crypto()
    sk = SigningKey(privkey_bytes)
    signed = sk.sign(data)
    return signed.signature


def ed25519_verify(pubkey_bytes: bytes, data: bytes, signature: bytes) -> bool:
    require_crypto()
    vk = VerifyKey(pubkey_bytes)
    try:
        vk.verify(data, signature)
        return True
    except BadSignatureError:
        return False


def save_key(path: Path | str, key_bytes: bytes) -> None:
    p = Path(path)
    p.write_text(base64.b64encode(key_bytes).decode("ascii"), encoding="utf-8")


def load_key(path: Path | str) -> bytes:
    p = Path(path)
    return base64.b64decode(p.read_text(encoding="utf-8").strip())


def fingerprint(pubkey_bytes: bytes) -> str:
    return hashlib.sha256(pubkey_bytes).hexdigest()
