"""python -m bridge.drain  — print pending inbox lines for the Agent turn."""

from __future__ import annotations

import json
from pathlib import Path

from bridge.config import load_config


def _offset_file(data_dir: Path) -> Path:
    return data_dir / "inbox.offset"


def read_offset(data_dir: Path) -> int:
    p = _offset_file(data_dir)
    if not p.exists():
        return 0
    raw = p.read_text(encoding="utf-8").strip()
    return int(raw) if raw.isdigit() else 0


def write_offset(data_dir: Path, value: int) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    _offset_file(data_dir).write_text(str(value), encoding="utf-8")


def pending(data_dir: Path) -> list[dict]:
    path = data_dir / "inbox.jsonl"
    if not path.exists():
        return []
    start = read_offset(data_dir)
    out: list[dict] = []
    total = 0
    with path.open(encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            total = i + 1
            if i < start:
                continue
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def mark_all_read(data_dir: Path) -> int:
    path = data_dir / "inbox.jsonl"
    if not path.exists():
        write_offset(data_dir, 0)
        return 0
    n = sum(1 for _ in path.open(encoding="utf-8"))
    write_offset(data_dir, n)
    return n


def main() -> None:
    cfg = load_config()
    rows = pending(cfg.data_dir)
    print(json.dumps({"pending": len(rows), "items": rows}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
