# eVKC SCVE — Self‑Contained Verifiable Capsules

Pack code + data + a manifest into a single capsule, then verify and re‑execute it under policy on another machine.

![CI](https://github.com/Maverick0351a/sCVE-SelfContainedVerifiableEnvironment/actions/workflows/ci.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/evkc)
![License](https://img.shields.io/badge/license-Apache--2.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6)
![Status](https://img.shields.io/badge/status-alpha-orange)

Simple, predictable, and auditable—aimed at reproducible results, artifact signing, and policy‑guarded execution.

## Table of contents
- Why eVKC?
- Quick start (Windows, Python 3.9+)
- Features at a glance
- CLI overview and examples
- Manifest, signing, and sidecars
- Policy and enforcement
- Samples
- Roadmap
- Contributing and support
- License

## Why eVKC?
Reproducibility is hard when code, data, and environment drift. eVKC provides a minimal, language‑agnostic container: a zip capsule with a JSON manifest, optional Ed25519 signature, and a policy‑enforced runner. It’s intentionally small and transparent so you can inspect, sign, verify, and re‑run with confidence.

Common use cases:
- Share a deterministic result with verifiable inputs and steps.
- Exchange small, self‑contained research artifacts.
- Execute third‑party capsules with clear safety rails (no network, read‑only, time/memory limits).

## Quick start (Windows, Python 3.9+)
Tested with Python 3.11 on Windows. Linux/macOS planned.

```powershell
# Install from PyPI
pip install evkc

# Optional: create and activate a virtual environment
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# Or install from source (editable dev install)
pip install -e .

# Pack the included sample and produce samples/vqcs.evkc.zip
python -m evkc pack samples/vqcs

# Verify and run under policy (with extra hardening)
python -m evkc verify samples/vqcs.evkc.zip
python -m evkc run --hardened samples/vqcs.evkc.zip
```

## Features at a glance
- Clean JSON manifest: artifacts, entrypoint/steps, and policy in one file.
- Deterministic artifact index: SHA‑256 of each file, generated during pack.
- Optional Ed25519 signing: sign the capsule; verify via sidecar public key.
- Policy‑enforced execution: no‑network, read‑only filesystem, time/memory limits (Windows Job Objects).
- Hardened Python mode: blocks sockets and common HTTP clients inside Python.
- Minimal footprint: inspectable zip archive and sidecar files.

## CLI overview and examples
The CLI is available via `python -m evkc` (or `evkc` when installed):

- `keygen` — generate an Ed25519 keypair (base64 `.sk` and `.pk`)
- `pack` — create a `.evkc.zip` capsule from a folder
- `verify` — validate manifest, artifact hashes, and signature (if present)
- `run` — execute a capsule under policy; `--hardened` enables extra Python‑level protections

Examples:

```powershell
# Generate signing keys
python -m evkc keygen --out signer

# Pack and sign a sample; also emit the public key sidecar next to the archive
python -m evkc pack samples/vqcs --sign signer.sk --emit-pub

# Verify (requires signature to validate when SIGNER.pub is present)
python -m evkc verify samples/vqcs.evkc.zip

# Run with enforcement and extra Python hardening
python -m evkc run --hardened samples/vqcs.evkc.zip
```

### Minimal manifest example
`samples/vqcs/manifest.json` (abridged):

```json
{
	"name": "vqcs",
	"version": "0.1.0",
	"description": "Deterministic light-bulb sample",
	"entrypoint": ["python", "simulate.py"],
	"policy": { "network": false, "filesystem_write": false, "max_seconds": 10, "max_memory_mb": 256 },
	"artifacts": [
		{ "path": "simulate.py", "sha256": "..." },
		{ "path": "expected.json", "sha256": "..." }
	]
}
```

## Manifest, signing, and sidecars
- Manifest lives at the root of the folder (`manifest.json`).
- During `pack`, missing artifact hashes are generated and written back to the manifest.
- Capsule is a zip archive named `<folder>.evkc.zip`.
- If signed, sidecars are placed alongside the archive:
	- `NAME.evkc.zip.SIGNATURE` — raw Ed25519 signature bytes
	- `NAME.evkc.zip.SIGNER.pub` — raw Ed25519 public key bytes

## Policy and enforcement
Policies are enforced by the runner and (optionally) via an extra Python hardening shim:
- `network: false` — strips proxy env vars; in `--hardened` mode, blocks sockets/HTTP in Python.
- `filesystem_write: false` — sets files read‑only and performs pre/post integrity checks.
- `max_seconds`, `max_memory_mb` — enforced via Windows Job Objects; processes are assigned to a kill‑on‑close job with limits.

Edge cases handled:
- Timeouts terminate the job (exit code 124).
- Any file mutation under `filesystem_write: false` fails the run.

## Samples
Included sample folders you can pack, verify, and run:
- `samples/vqcs` — deterministic “light‑bulb” calculation.
- `samples/causal_passport` — toy deterministic twin check.
- `samples/negative_write` — attempts to write; verification passes, run fails under policy (expected).

Pack and try one:

```powershell
python -m evkc pack samples/vqcs
python -m evkc verify samples/vqcs.evkc.zip
python -m evkc run --hardened samples/vqcs.evkc.zip
```

## Roadmap
- Linux/macOS support (cgroups/rlimits and platform‑specific sandboxes).
- Additional policies (CPU affinity, stdout size limits, environment allowlist).
- Optional in‑archive signature block (besides sidecars).
- Richer step orchestration (multi‑step pipelines with typed outputs).

Track progress and file ideas in Issues: https://github.com/Maverick0351a/sCVE-SelfContainedVerifiableEnvironment/issues

## Contributing and support
- Linting: Ruff is configured (`ruff check`, `ruff check --fix`).
- Dev install: `pip install -e .`.
- Questions/bugs: open an Issue in the repository.

## License
Apache License 2.0 — see `LICENSE`.
