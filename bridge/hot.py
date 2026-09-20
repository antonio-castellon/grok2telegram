"""Hot session: Mesa stays in a short linger loop after a wake.

While hot, further wake POSTs are skipped — the live agent turn polls inbox.
"""

from __future__ import annotations

import time
from pathlib import Path

_FLAG = "mesa_hot_until"


def _path(data_dir: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / _FLAG


def is_hot(data_dir: Path, *, now: float | None = None) -> bool:
    p = _path(data_dir)
    if not p.exists():
        return False
    try:
        until = float(p.read_text(encoding="utf-8").strip() or "0")
    except ValueError:
        return False
    return (now if now is not None else time.time()) < until


def start_hot(data_dir: Path, seconds: float = 120.0) -> float:
    until = time.time() + max(5.0, float(seconds))
    _path(data_dir).write_text(str(until), encoding="utf-8")
    return until


def extend_hot(data_dir: Path, seconds: float = 120.0) -> float:
    """Refresh the window from now (call when new work arrives during linger)."""
    return start_hot(data_dir, seconds=seconds)


def clear_hot(data_dir: Path) -> None:
    p = _path(data_dir)
    if p.exists():
        p.unlink()


def remaining(data_dir: Path) -> float:
    p = _path(data_dir)
    if not p.exists():
        return 0.0
    try:
        until = float(p.read_text(encoding="utf-8").strip() or "0")
    except ValueError:
        return 0.0
    return max(0.0, until - time.time())
