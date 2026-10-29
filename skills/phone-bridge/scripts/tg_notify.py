#!/usr/bin/env python3
"""tg_notify.py: send a Telegram ping from a ZCode task to the configured chat.

Reads config from ~/.config/zcode-phone-bridge/config.json (mode 0600):
  { "bot_token": "123456:ABC...", "chat_id": 987654321 }

Outbound pings only. This script opens no inbound channel and no remote
control: it calls api.telegram.org/bot<token>/sendMessage and nothing else.

Exit codes:
  0  message delivered (Telegram answered ok=true)
  1  config missing or invalid (setup instructions printed to stderr)
  2  bad usage
  3  network error or Telegram error (details printed to stderr)

Usage:
  python3 tg_notify.py --text "build finished"
  python3 tg_notify.py --status done --file /path/to/build.log
  python3 tg_notify.py --status failed --text "exit 2: ..."

Python 3 stdlib only (urllib). Cross-OS.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "zcode-phone-bridge" / "config.json"
API = "https://api.telegram.org/bot{token}/sendMessage"


def fail_config(msg: str):
    print(f"config error: {msg}", file=sys.stderr)
    print(
        "\nSetup (one time):\n"
        f"  1. mkdir -p {CONFIG_PATH.parent}\n"
        "  2. Create a bot with @BotFather on Telegram and copy the token.\n"
        "  3. Get your chat id: send your bot any message, then open\n"
        "     https://api.telegram.org/bot<TOKEN>/getUpdates  and read chat.id.\n"
        "  4. Write the config file with 0600 permissions:\n"
        f"     echo '{{\"bot_token\": \"<TOKEN>\", \"chat_id\": <CHAT_ID>}}' > {CONFIG_PATH}\n"
        "     chmod 600 " + str(CONFIG_PATH) + "\n"
        "  5. Do not commit that file to any git repo.",
        file=sys.stderr,
    )
    sys.exit(1)


def load_config():
    if not CONFIG_PATH.exists():
        fail_config(f"missing {CONFIG_PATH}")
    try:
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        fail_config(f"unreadable or invalid JSON at {CONFIG_PATH}: {e}")
    token = raw.get("bot_token")
    chat_id = raw.get("chat_id")
    if not token or not isinstance(token, str):
        fail_config("config has no 'bot_token' (string from @BotFather)")
    if chat_id is None or isinstance(chat_id, bool):
        fail_config("config has no 'chat_id' (number from getUpdates)")
    return token, chat_id


def read_tail(path: str, limit: int) -> str:
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e:
        return f"(could not read {path}: {e})"
    return "\n".join(lines[-limit:])


def build_message(args, status: str) -> str:
    parts = [f"[zcode:{status}]"]
    if args.text:
        parts.append(args.text)
    if args.file:
        parts.append(f"last {args.tail} lines of {args.file}:\n" + read_tail(args.file, args.tail))
    text = "\n".join(parts)
    return text[:4000]  # Telegram keeps 4096 char limit with headroom


def send(token: str, chat_id, text: str):
    url = API.format(token=token)
    body = urllib.parse.urlencode(
        {"chat_id": chat_id, "text": text, "disable_web_page_preview": "true"}
    ).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", errors="replace")[:300]
        except OSError:
            pass
        print(f"telegram HTTP {e.code}: {detail or e.reason}", file=sys.stderr)
        sys.exit(3)
    except (urllib.error.URLError, OSError) as e:
        print(f"network error talking to Telegram: {e}", file=sys.stderr)
        sys.exit(3)
    if not data.get("ok"):
        print(f"telegram error: {json.dumps(data)[:300]}", file=sys.stderr)
        sys.exit(3)
    print(f"delivered to chat {chat_id} ({data['result']['message_id']})")


def main():
    ap = argparse.ArgumentParser(
        prog="tg_notify.py",
        description="Send a status ping to the Telegram chat in the local config. Outbound only.",
    )
    ap.add_argument("--text", help="message body (required unless --file given)")
    ap.add_argument(
        "--status",
        choices=["info", "done", "failed", "started"],
        default="info",
        help="prefix tag for the ping",
    )
    ap.add_argument("--file", help="append the last N lines of this file to the ping")
    ap.add_argument(
        "--tail",
        type=int,
        default=20,
        help="how many trailing lines to include with --file (default 20)",
    )
    args = ap.parse_args()

    if not args.text and not args.file:
        print("error: give --text, --file, or both", file=sys.stderr)
        sys.exit(2)

    token, chat_id = load_config()
    text = build_message(args, args.status)
    send(token, chat_id, text)


if __name__ == "__main__":
    main()
