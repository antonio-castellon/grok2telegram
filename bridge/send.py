"""python -m bridge.send --chat-id -100123 --text 'hola' [--title 21] [--buttons ...]"""

from __future__ import annotations

import argparse

from bridge.buttons import parse_buttons_arg, parse_buttons_json
from bridge.config import load_config
from bridge.telegram_io import Telegram


def main() -> None:
    p = argparse.ArgumentParser(
        description="Send a BBS-framed Telegram message (optional inline buttons)."
    )
    p.add_argument("--chat-id", type=int, required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--title", default=None)
    p.add_argument(
        "--buttons",
        default=None,
        help="Pipe-separated id:Label pairs, e.g. 'a:Option A|b:Option B'",
    )
    p.add_argument(
        "--buttons-json",
        default=None,
        help='JSON list, e.g. \'[{"id":"a","label":"Option A"}]\'',
    )
    args = p.parse_args()
    if args.buttons and args.buttons_json:
        raise SystemExit("Use either --buttons or --buttons-json, not both")
    buttons = None
    if args.buttons:
        buttons = parse_buttons_arg(args.buttons)
    elif args.buttons_json:
        buttons = parse_buttons_json(args.buttons_json)
    cfg = load_config()
    if not cfg.telegram_bot_token:
        raise SystemExit("Falta TELEGRAM_BOT_TOKEN")
    Telegram(cfg.telegram_bot_token).send_message(
        args.chat_id,
        args.text,
        title=args.title,
        buttons=buttons,
        data_dir=cfg.data_dir,
    )


if __name__ == "__main__":
    main()
