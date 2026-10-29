# Phone Bridge

One-sentence pitch: get ZCode task results on your phone via Telegram pings, with an honest no-remote-control guarantee.

## Why

You start a long build or crawl, leave your desk, and sit waiting to see
whether it finished. Phone Bridge pings your Telegram chat when a task starts,
finishes, or fails, with a short summary and the last lines of output. It also
pings "waiting on you" when ZCode stops at a decision, so you know it is
blocked. The plugin sends messages. It does not let your phone type into
ZCode: no remote shell, no auto-approval. Approvals still happen in the
normal chat.

## How it works

1. SETUP: create a Telegram bot with BotFather, grab your chat id from
   `getUpdates`, and store token + chat id in
   `~/.config/zcode-phone-bridge/config.json` with 0600 permissions.
2. NOTIFY: the skill calls `scripts/tg_notify.py` with `--status
   started/done/failed`, a short `--text` summary, and optionally
   `--file <logfile>` to append the last lines of output.
3. APPROVE: when a decision is needed, ZCode ends its turn, pings the
   question to your phone, and waits for your answer in the normal chat.

Config file shape: `{"bot_token": "123456:ABC...", "chat_id": 987654321}`.

## Install

Option A: self-installable marketplace

1. Download or clone this repo into a folder.
2. In ZCode, open Plugin Marketplace, then Add, then Add Plugin Marketplace.
3. Paste the folder path, wait for it to load, then Install `phone-bridge`.

Option B: manual copy

Copy the `phone-bridge` folder into your workspace `plugins/` directory,
then restart ZCode.

## Try it

After setup, run:

```
/phone-bridge test
```

Expected: the script prints `delivered to chat <id> (<message_id>)` and you
see the ping on your phone. Then run a real task and expect a
`[zcode:done]` ping with the summary and the last 20 lines of the log.

## Requirements

Python 3 (stdlib only). A Telegram bot token and a chat id, which you supply
once. Network access to `api.telegram.org`. The config file must stay out of
any git repo.

---

<p align="center">
  <a href="https://z.ai/subscribe?ic=R0K78RJKNW"><img alt="z.ai coding plans - 10% OFF coupon" src="https://img.shields.io/badge/z.ai%20coding%20plans-10%25%20OFF%20coupon-blueviolet" /></a>
  <a href="https://zcode.z.ai/invite/ALWM9JUA"><img alt="Try ZCode free" src="https://img.shields.io/badge/Try%20ZCode-free%20invite-0969da" /></a>
</p>

## License

MIT
