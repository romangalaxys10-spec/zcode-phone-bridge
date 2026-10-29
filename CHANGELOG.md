# Changelog

## 0.1.0 - 2026-10-29

- Initial release: guided setup for a local 0600 Telegram config (bot token + chat id, never committed).
- Outbound status pings via stdlib-only `scripts/tg_notify.py` with `--status started/done/failed/info`, `--text` summary, and `--file` log tails.
- Waiting-for-you pings so the user can answer pending decisions from the phone in the normal chat; the plugin has no inbound control channel by design.
