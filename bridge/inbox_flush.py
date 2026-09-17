"""On bridge boot: do not invent game replies.

Mechanical flush used to auto-play 21 / answer facts. Antonio wants the bridge
thin (help/clear/…). Pending GM lines stay for Mesa.
"""

from __future__ import annotations

import logging

from bridge.config import Config, load_config
from bridge.drain import pending
from bridge.telegram_io import Telegram

log = logging.getLogger("g2t.flush")


def flush_pending(cfg: Config | None = None, tg: Telegram | None = None) -> dict[str, int]:
    cfg = cfg or load_config()
    items = pending(cfg.data_dir)
    n = len(items)
    if n:
        flag = cfg.data_dir / "needs_agent_drain"
        flag.write_text(str(n), encoding="utf-8")
        log.info("boot: %s inbox item(s) left for Mesa (no local game flush)", n)
    return {"pending": n, "flushed": 0, "left": n}


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    print(flush_pending())


if __name__ == "__main__":
    main()
