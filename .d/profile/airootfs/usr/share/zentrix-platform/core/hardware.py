from __future__ import annotations

import platform
import subprocess


def detect_cpu_vendor() -> str:
    try:
        out = subprocess.check_output(["bash", "-lc", "lscpu | grep 'Vendor ID'"], text=True)
    except Exception:
        return "unknown"
    out = out.lower()
    if "intel" in out:
        return "intel"
    if "amd" in out:
        return "amd"
    return "unknown"


def system_summary() -> dict[str, str]:
    return {
        "kernel": platform.release(),
        "machine": platform.machine(),
        "platform": platform.platform(),
        "cpu_vendor": detect_cpu_vendor(),
    }
