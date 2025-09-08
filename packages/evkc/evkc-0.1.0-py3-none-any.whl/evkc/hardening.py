from __future__ import annotations

import tempfile
from pathlib import Path

HARDEN_SITE = """
# Auto-injected by eVKC hardened mode: disable outbound networking for Python scripts
import builtins
import socket

class _BlockedSocket(socket.socket):
    def __init__(self, *a, **kw):
        raise OSError("Networking disabled by eVKC hardened policy")

# Monkey-patch low-level creations
socket.socket = _BlockedSocket  # type: ignore
socket.create_connection = lambda *a, **kw: (_ for _ in ()).throw(OSError("Networking disabled by eVKC"))  # type: ignore

# Optional: block common high-level clients if loaded after sitecustomize
try:
    import urllib.request as _u
    _u.urlopen = lambda *a, **kw: (_ for _ in ()).throw(OSError("Networking disabled by eVKC"))
except Exception:
    pass

try:
    import http.client as _h
    _h.HTTPConnection = _BlockedSocket  # type: ignore
    _h.HTTPSConnection = _BlockedSocket  # type: ignore
except Exception:
    pass
"""


def prepare_python_no_network_shim() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="evkc_shim_"))
    (tmp / "sitecustomize.py").write_text(HARDEN_SITE, encoding="utf-8")
    return tmp


def apply_python_no_network(env: dict[str, str]) -> tuple[dict[str, str], Path]:
    shim_dir = prepare_python_no_network_shim()
    new_env = env.copy()
    # Prepend to PYTHONPATH so sitecustomize is loaded by Python before user code
    existing = new_env.get("PYTHONPATH", "")
    sep = ";" if existing else ""
    new_env["PYTHONPATH"] = f"{shim_dir}{sep}{existing}"
    return new_env, shim_dir
