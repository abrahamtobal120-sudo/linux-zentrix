#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dbus_next.aio import MessageBus
from dbus_next.constants import BusType

from core.config import ConfigManager
from core.logger import build_logger
from core.state import StateStore
from daemon.service import ZentrixService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Zentrix Core daemon")
    parser.add_argument("--config", default="/etc/zentrix/zentrix.yaml")
    parser.add_argument("--bus", choices=["system", "session"], default="system")
    return parser.parse_args()


async def run() -> None:
    args = parse_args()
    cfg_mgr = ConfigManager(args.config)
    cfg = cfg_mgr.load()

    # In development mode, make local paths usable without root.
    if args.bus == "session":
        root = Path(__file__).resolve().parents[1]
        cfg.profile_dir = str(root / "profiles")
        cfg.state_file = str(root / ".runtime" / "state.json")
        cfg.log_file = str(root / ".runtime" / "daemon.log")

    logger = build_logger("zentrix-daemon", cfg.log_file)
    state_store = StateStore(cfg.state_file)
    state = state_store.load()

    bus_type = BusType.SYSTEM if args.bus == "system" else BusType.SESSION
    bus = await MessageBus(bus_type=bus_type).connect()

    service = ZentrixService(cfg, cfg_mgr, state_store, state, logger)
    bus.export("/org/zentrix/Core", service)
    await bus.request_name("org.zentrix.Core")

    logger.info("Zentrix daemon started on %s bus", args.bus)
    await asyncio.get_running_loop().create_future()


def main() -> None:
    if os.geteuid() != 0:
        # Development and testing can run as non-root on session bus.
        pass
    asyncio.run(run())


if __name__ == "__main__":
    main()
