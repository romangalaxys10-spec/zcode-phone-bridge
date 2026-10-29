---
name: phone-bridge
description: "Use when the user wants to get ZCode status pings on their phone via Telegram, or asks to monitor/steer a long-running ZCode task from their phone. Triggers: 'ping me when this build finishes', 'send me a telegram when the task ends', 'set up phone notifications', 'can I control zcode from my phone'."
---

# Phone Bridge

Honest design statement first, say it to the user when relevant:

- This plugin SENDS pings to a Telegram chat. It does NOT open an inbound
  control channel: there is no remote shell, no auto-approval of tool calls,
  no way for a phone message to approve or direct a running ZCode turn.
- Approvals and follow-ups still happen in the normal ZCode chat. The "APPROVE"
  step below means: end the turn, state what is pending, and let the user
  answer from their phone in the ordinary chat UI. Telegram carries the
  notification only.
- The bot token is a credential. It lives in a local 0600 config file and must
  never be committed to git or pasted into a prompt.

The sender script is `scripts/tg_notify.py` (relative to this skill dir).
Stdlib only, cross-OS, outbound HTTP to api.telegram.org via urllib.

## Workflow

### 1. SETUP (first use only)

Check whether the config exists:

```bash
ls -l ~/.config/zcode-phone-bridge/config.json
```

If it is missing, walk the user through it, one step at a time:

1. Create a bot with @BotFather on Telegram, note the token. Ask the user to
   paste the token into THIS session; write it into the config yourself.
2. Get the chat id: user sends the bot any message, then fetches
   `https://api.telegram.org/bot<TOKEN>/getUpdates` (browser is fine, the page
   shows the last inbound messages). Read `chat.id` from the result.
3. Create the config with 0600 permissions:

   ```bash
   mkdir -p ~/.config/zcode-phone-bridge
   cat > ~/.config/zcode-phone-bridge/config.json <<'EOF'
   {"bot_token": "<TOKEN>", "chat_id": <CHAT_ID>}
   EOF
   chmod 600 ~/.config/zcode-phone-bridge/config.json
   ```

4. Test ping:

   ```bash
   python3 scripts/tg_notify.py --status info --text "phone-bridge setup test"
   ```

   Expect: `delivered to chat <id> (<msg_id>)`. If the error says
   `chat not found` or the token is invalid, the chat id or token is wrong.
   The script fails loudly on a missing config and prints these same setup
   instructions in the error text.

Security notes to say out loud: 0600 permissions are set; the file stays in
`~/.config` which is not in any git repo; the user can revoke the bot at any
time with /revoke in BotFather.

### 2. NOTIFY (during and after long-running work)

For a task that runs for minutes or more:

- Before it starts: `python3 scripts/tg_notify.py --status started --text "<one line what is running>"`
- On success: `python3 scripts/tg_notify.py --status done --text "<summary>" --file <logfile>`
  (the script appends the last 20 lines of the file, `--tail N` to change).
- On failure: `python3 scripts/tg_notify.py --status failed --text "exit code 2: <short reason>"`

Keep ping bodies short: script name, exit code or outcome, elapsed time
(`time` the command or record start/finish), and the last few lines of output
when there is a log file. When a command was backgrounded, capture its output
to a file first (e.g. `cmd > /tmp/task.log 2>&1`) so `--file` has something
to tail.

Exit codes of `tg_notify.py`: 0 delivered; 1 config missing/invalid (setup
instructions in stderr); 2 bad usage; 3 network or Telegram error. On 1, run
SETUP. On 3, retry once, then tell the user the ping did not go through.

### 3. APPROVE (steering, honestly scoped)

The only "steer from phone" this plugin supports:

1. When a task needs a user decision (a fork in approach, a destructive step,
   a missing requirement), END THE TURN. State the question plainly in the
   chat and, if notify is configured, ping:
   `python3 scripts/tg_notify.py --status info --text "waiting on you: <question>"`
2. The user sees the ping and replies in the NORMAL ZCode chat on their phone
   (or desktop). The next ZCode turn starts with their message.
3. Never claim the bot received an instruction. It cannot. If the user asks,
   restate this limit.

## Guardrails

- Never put the token or chat id into the prompt history, logs, notebooks, or
  any file under the workspace or a repo.
- Never add inbound polling (getUpdates) as a control loop without the user
  explicitly asking for a separate design; the default stays outbound-only.
- If the config file is found with world-readable permissions, warn and fix
  with `chmod 600`.
