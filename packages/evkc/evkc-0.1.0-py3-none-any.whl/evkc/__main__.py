from __future__ import annotations

import argparse
from pathlib import Path

from .crypto import ed25519_keygen, save_key
from .pack import pack_capsule
from .run import RunError, run_capsule
from .verify import verify_capsule


def main() -> int:
    parser = argparse.ArgumentParser(prog="evkc", description="eVKC SCVE minimal toolkit")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_keygen = sub.add_parser("keygen", help="Generate an ed25519 keypair")
    p_keygen.add_argument("--out", type=str, default="evkc_key")

    p_pack = sub.add_parser("pack", help="Pack a folder into a capsule")
    p_pack.add_argument("folder", type=str)
    p_pack.add_argument("--out", type=str, default=None)
    p_pack.add_argument("--sign", type=str, default=None, help="Signer private key (ed25519, base64)")
    p_pack.add_argument("--emit-pub", action="store_true", help="Write SIGNER.pub sidecar")

    p_verify = sub.add_parser("verify", help="Verify a capsule archive")
    p_verify.add_argument("archive", type=str)

    p_run = sub.add_parser("run", help="Run a capsule archive or folder")
    p_run.add_argument("target", type=str)
    p_run.add_argument("--hardened", action="store_true", help="Enable extra enforcement (Python net off, job limits)")

    args = parser.parse_args()

    if args.cmd == "keygen":
        sk, pk = ed25519_keygen()
        save_key(f"{args.out}.sk", sk)
        save_key(f"{args.out}.pk", pk)
        print(f"wrote {args.out}.sk and {args.out}.pk (base64)")
        return 0

    if args.cmd == "pack":
        out = pack_capsule(Path(args.folder), args.out, args.sign)
        if args.sign and args.emit_pub:
            # if signing, create SIGNER.pub sidecar named after archive
            from .crypto import load_key
            pub = load_key(args.sign.replace(".sk", ".pk")) if args.sign.endswith(".sk") else None
            if pub:
                Path(f"{out}.SIGNER.pub").write_bytes(load_key(args.sign.replace(".sk", ".pk")))
        print(out)
        return 0
    if args.cmd == "verify":
        ok, msg = verify_capsule(Path(args.archive))
        print(msg)
        return 0 if ok else 2
    if args.cmd == "run":
        try:
            return run_capsule(Path(args.target), hardened=args.hardened)
        except RunError as e:
            print(str(e))
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
