from __future__ import annotations

import signal
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.parental import ParentalAgent


def main() -> None:
    agent = ParentalAgent()
    running = True

    def stop(_signo, _frame) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    while running:
        policy, state = agent.load()
        state.setdefault("users", {})
        state["last_sync"] = agent._now_iso()
        for user in policy.selected_users:
            user_state = state["users"].setdefault(
                user,
                {"remaining_minutes": 0, "daily_used_minutes": 0, "locked": False, "mode": "normal"},
            )
            if user_state.get("remaining_minutes", 0) <= 0:
                user_state["locked"] = True
        agent.save_state(state)
        time.sleep(15)


if __name__ == "__main__":
    main()
