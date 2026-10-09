from pathlib import Path

from core.state import CoreState, StateStore


def test_state_roundtrip(tmp_path: Path):
    store = StateStore(str(tmp_path / "state.json"))
    state = CoreState(
        current_profile="gaming",
        active_mode="gaming",
        previous_profile="normal",
        previous_mode="normal",
        pending_restore={"profile": "normal", "mode": "normal"},
    )
    store.save(state)

    loaded = store.load()
    assert loaded.current_profile == "gaming"
    assert loaded.active_mode == "gaming"
    assert loaded.previous_profile == "normal"
    assert loaded.pending_restore["profile"] == "normal"
