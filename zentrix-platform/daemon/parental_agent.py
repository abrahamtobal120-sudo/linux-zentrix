from __future__ import annotations

import json
import signal
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.parental import ParentalAgent
from core.parental_runtime import ParentalRuntime


LOOP_SECONDS = 15


def main() -> None:
    agent = ParentalAgent()
    runtime = ParentalRuntime(agent)
    running = True

    def stop(_signo, _frame) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    print("[zentrix-parental] local agent started", flush=True)
    while running:
        try:
            result = runtime.tick()
            if result.get("clock_anomaly"):
                print("[zentrix-parental] warning: system clock anomaly detected", flush=True)
        except Exception as exc:
            print(
                "[zentrix-parental] runtime error: "
                + json.dumps({"type": type(exc).__name__, "message": str(exc)}, ensure_ascii=False),
                file=sys.stderr,
                flush=True,
            )
        deadline = time.monotonic() + LOOP_SECONDS
        while running and time.monotonic() < deadline:
            time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))

    print("[zentrix-parental] local agent stopped", flush=True)


if __name__ == "__main__":
    main()
