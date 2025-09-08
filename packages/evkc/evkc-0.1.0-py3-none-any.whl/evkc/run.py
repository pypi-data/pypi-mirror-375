from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from contextlib import suppress
from pathlib import Path

from .hardening import apply_python_no_network
from .manifest import gen_artifact_index, load_manifest
from .sandbox import apply_no_network_env
from .windows_job import JobHandle, assign_pid_to_job, create_job


class RunError(Exception):
    pass


def _extract_capsule(archive: Path, dest: Path) -> None:
    with zipfile.ZipFile(archive, "r") as z:
        z.extractall(dest)


def _run_step(
    step_cmd: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
    job: JobHandle | None = None,
) -> int:
    proc = subprocess.Popen(
        step_cmd,
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    # Assign process to Job for limits/enforcement
    if job and job.valid():
        assign_pid_to_job(job, proc.pid)
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        if job:
            job.terminate(124)
        proc.kill()
        out, err = proc.communicate()
        sys.stdout.write(out)
        sys.stderr.write(err)
        return 124
    sys.stdout.write(out)
    sys.stderr.write(err)
    return proc.returncode


def run_capsule(
    archive_or_folder: Path | str,
    env_overrides: dict[str, str] | None = None,
    hardened: bool = False,
) -> int:
    """
    Run the capsule. If a folder is provided, uses it directly. If an archive is provided,
    extracts into a temp dir. Enforces minimal policy constraints (timeout only for now).
    Returns final exit code (0 if all steps pass).
    """
    p = Path(archive_or_folder)

    # Prepare execution directory
    cleanup = False
    if p.is_file() and p.suffix == ".zip":
        tmp = Path(tempfile.mkdtemp(prefix="evkc_"))
        _extract_capsule(p, tmp)
        workdir = tmp
        cleanup = True
    else:
        workdir = p

    exec_dir: Path | None = None
    job: JobHandle | None = None
    try:
        manifest = load_manifest(workdir / "manifest.json")
        env = os.environ.copy()
        if env_overrides:
            env.update(env_overrides)

        timeout = manifest.policy.max_seconds if manifest and manifest.policy else None

        # Apply simple policy knobs
        if not manifest.policy.network:
            env = apply_no_network_env(env)
            if hardened:
                env, shim_dir = apply_python_no_network(env)

        # Prepare execution workspace: copy to temp and optionally set read-only
        exec_dir = Path(tempfile.mkdtemp(prefix="evkc_exec_"))
        shutil.copytree(workdir, exec_dir, dirs_exist_ok=True)

        # Make files read-only if filesystem_write is false
        if not manifest.policy.filesystem_write:
            env["PYTHONDONTWRITEBYTECODE"] = "1"  # prevent __pycache__ writes
            for target in exec_dir.rglob("*"):
                with suppress(Exception):
                    if target.is_file():
                        os.chmod(target, 0o444)
        # Index before run for integrity check
        before = {a.path: a.sha256 for a in gen_artifact_index(exec_dir)}

        # Create Job with limits
        job = create_job(
            max_seconds=manifest.policy.max_seconds,
            max_memory_mb=manifest.policy.max_memory_mb,
            active_process_limit=1,
        )

        # If entrypoint specified, run it; else run steps
        if manifest.entrypoint:
            code = _run_step(manifest.entrypoint, exec_dir, env=env, timeout=timeout, job=job)
            # Post-run integrity check for entrypoint mode
            after = {a.path: a.sha256 for a in gen_artifact_index(exec_dir)}
            if not manifest.policy.filesystem_write and after != before:
                raise RunError("Filesystem changed under filesystem_write=false policy")
            return code

        if manifest.steps:
            for s in manifest.steps:
                code = _run_step(s.command, exec_dir, env=env, timeout=timeout, job=job)
                if code != s.expected_exit_code:
                    raise RunError(
                        f"Step '{s.name}' failed: exit {code} != expected {s.expected_exit_code}"
                    )
            # Post-run integrity check
            after = {a.path: a.sha256 for a in gen_artifact_index(exec_dir)}
            if not manifest.policy.filesystem_write and after != before:
                raise RunError("Filesystem changed under filesystem_write=false policy")
            return 0

        # Fallback: no steps, nothing to do
        return 0
    finally:
        # Close job handle
        with suppress(Exception):
            if job:
                job.close()
        # Cleanup exec_dir
        with suppress(Exception):
            if exec_dir and exec_dir.exists():
                for child in exec_dir.rglob("*"):
                    if child.is_file():
                        with suppress(Exception):
                            os.chmod(child, 0o600)
                            child.unlink()
                for child in sorted([d for d in exec_dir.rglob("*") if d.is_dir()], reverse=True):
                    with suppress(Exception):
                        child.rmdir()
                exec_dir.rmdir()
        # Cleanup extracted workdir if we created it from an archive
        if cleanup:
            with suppress(Exception):
                for child in workdir.rglob("*"):
                    if child.is_file():
                        with suppress(Exception):
                            child.unlink()
                for child in sorted([d for d in workdir.rglob("*") if d.is_dir()], reverse=True):
                    with suppress(Exception):
                        child.rmdir()
                workdir.rmdir()
