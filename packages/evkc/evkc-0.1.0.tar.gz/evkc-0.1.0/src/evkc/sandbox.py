from __future__ import annotations

# Minimal guardrails: disable proxy envs. Real isolation needs OS sandboxing; this just removes net hints.


def apply_no_network_env(env: dict[str, str]) -> dict[str, str]:
    env = env.copy()
    # Unset proxy variables commonly used by Python/requests
    for var in [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "http_proxy",
        "https_proxy",
        "NO_PROXY",
        "no_proxy",
    ]:
        env.pop(var, None)
    env["EVKC_NO_NETWORK"] = "1"
    return env
