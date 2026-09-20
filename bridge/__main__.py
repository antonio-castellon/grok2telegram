"""python -m bridge — start the Telegram poll loop.

Important: any `python -m bridge …` used to call run() unconditionally, so
`python -m bridge --help` started a second getUpdates poller and Telegram
returned 409 Conflict. Argv is checked here first.
"""

from __future__ import annotations

import sys


def main() -> None:
    args = [a for a in sys.argv[1:] if a]
    if not args or args == ["run"]:
        from bridge.loop import run

        run()
        return
    if args[0] in {"-h", "--help", "help"}:
        print(
            "usage: python -m bridge\n"
            "       python -m bridge run\n\n"
            "Starts the Telegram getUpdates loop (one process only).\n"
            "For diagnostics use: python -m bridge.drain | bridge.send | …\n"
            "Do NOT pass --help to start a second poller — this entrypoint\n"
            "used to ignore argv and always ran the loop."
        )
        return
    print(f"unknown args: {' '.join(args)}. try: python -m bridge --help", file=sys.stderr)
    raise SystemExit(2)


if __name__ == "__main__":
    main()
