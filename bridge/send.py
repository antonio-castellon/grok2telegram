"""python -m bridge.send --chat-id -100123 --text 'hola' [--title 21]"""

from __future__ import annotations

import argparse

from bridge.config import load_config
from bridge.telegram_io import Telegram


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--chat-id", type=int, required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--title", default=None)
    args = p.parse_args()
    cfg = load_config()
    if not cfg.telegram_bot_token:
        raise SystemExit("Falta TELEGRAM_BOT_TOKEN")
    Telegram(cfg.telegram_bot_token).send_message(args.chat_id, args.text, title=args.title)


if __name__ == "__main__":
    main()
