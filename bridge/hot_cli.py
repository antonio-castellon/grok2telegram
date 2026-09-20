"""python -m bridge.hot_cli start|clear|status [seconds]"""

from __future__ import annotations

import sys

from bridge.config import load_config
from bridge import hot


def main() -> None:
    cfg = load_config()
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "status").strip().lower()
    if cmd == "start":
        sec = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0
        until = hot.start_hot(cfg.data_dir, seconds=sec)
        print({"hot": True, "until": until, "seconds": sec})
    elif cmd == "extend":
        sec = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0
        until = hot.extend_hot(cfg.data_dir, seconds=sec)
        print({"hot": True, "until": until, "seconds": sec})
    elif cmd == "clear":
        hot.clear_hot(cfg.data_dir)
        print({"hot": False})
    else:
        print({"hot": hot.is_hot(cfg.data_dir), "remaining": round(hot.remaining(cfg.data_dir), 1)})


if __name__ == "__main__":
    main()
