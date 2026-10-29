---
description: Set up and send Telegram status pings for ZCode tasks
allowed-tools: Read, Bash, Write
argument-hint: <setup | test | started <what> | done <summary> [logfile] | failed <reason> [logfile] | approve <question>>
---
Invoke the `phone-bridge` skill with this input: **$ARGUMENTS**

If no arguments are given, check whether `~/.config/zcode-phone-bridge/config.json`
exists and is 0600. If missing, start SETUP and ask the user for the bot token
and chat id. If present, send a `--status info` test ping to confirm delivery.
Outbound pings only; approvals always happen in the normal ZCode chat.
