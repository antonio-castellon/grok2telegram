# Setup — grok2telegram

This process runs **on the Grok Agent Bot virtual machine**, not on the house PC.

```
Telegram group  --/cmd-->  python -m bridge (Agent VM)
Telegram group  <--say---  sendMessage from the same process
```

No `XAI_API_KEY`. No public IP at home. Companion tavern-on-a-PC: [grokgame](https://github.com/antonio-castellon/grokgame).

---

## 0. Agent Bot

Create a Grok Agent Bot named **Mesa** (or similar). Paste [docs/AGENT.md](docs/AGENT.md) into its standing description.

Clone this repo onto **that** machine (ask the Agent to clone `antonio-castellon/grok2telegram`).

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Never commit `.env`.

---

## 1. Telegram bot

### 1.1 Token

1. [@BotFather](https://t.me/BotFather) → `/newbot`
2. Token into `.env`:

```
TELEGRAM_BOT_TOKEN=paste-here
```

### 1.2 Privacy (required)

`/setprivacy` → this bot → **Disable**

### 1.3 Group

The app **never** creates groups.

1. Create the group yourself.
2. Add the bot, make it **group admin**.
3. Optional: pin the group id in `.env` as `ALLOWED_CHAT_IDS=…` so the process ignores other chats.

### 1.4 Your user id

[@userinfobot](https://t.me/userinfobot) → `Id:` (example placeholder — use yours):

```
ADMIN_TELEGRAM_IDS=123456789
GM_BACKEND=mock
```

---

## 2. Start (mock first)

```
python -m bridge
```

or `scripts/start.sh` (nohup + `data/pid`).

`scripts/healthcheck.sh` exits 0 if that pid is alive.

In the group:

```
/cmd whoami
/cmd help
/cmd new-game misterio en un faro
/cmd cmd list
```

---

## 3. Agent mode (Grok is the GM)

Stop the process. In `.env`:

```
GM_BACKEND=agent
```

Start again. Commands that need a brain go to `data/inbox.jsonl`. On each Agent turn:

1. `scripts/healthcheck.sh` or `scripts/start.sh`
2. Read new lines in `data/inbox.jsonl`
3. Invent `say` in `lang`
4. `python -m bridge.send --chat-id <id> --text "<say>"`

Give the Agent an hourly routine that does those four steps. The VM is not a promised 24/7 VPS; the routine is the watchdog.

A Grok **Automation webhook** is optional and only a doorbell (`202`, empty body). It does not carry `say`. Do not wait for the HTTP response.

---

## 4. `.env` cheat sheet

| Variable | What |
|---|---|
| `TELEGRAM_BOT_TOKEN` | BotFather |
| `ADMIN_TELEGRAM_IDS` | Numeric Telegram id(s) |
| `ALLOWED_CHAT_IDS` | Optional group id whitelist |
| `GM_BACKEND` | `mock` or `agent` |
| `DATA_DIR` | Default `./data` |

No `XAI_API_KEY`. No `WEBHOOK_*` required.

---

## 5. Commands

| Command | Who | Effect |
|---|---|---|
| `/cmd help` | anyone | grammar |
| `/cmd whoami` | anyone | name, id, admin? |
| `/cmd lang es` | admin | `es` / `fr` / `de` / `en` |
| `/cmd new-game …` | admin | invent a table |
| `/cmd cmd list` | anyone | current verbs |
| `/cmd rules …` / `/cmd limit …` | admin | extra rules / limits |
| `/cmd status` | anyone | snapshot |
| `/cmd reset` | admin | close table (`reset hard` deletes JSON) |
| `/cmd grant` / `/cmd revoke` | admin | extra table admins |

---

## 6. Typical failures

| Symptom | What to do |
|---|---|
| Bot ignores `/cmd` in the group | BotFather → `/setprivacy` → this bot → **Disable**. Then send `/cmd help` again. |
| Telegram 401 / Unauthorized | Token is wrong or revoked. BotFather → `/token`, paste the new value into `.env`, restart `python -m bridge`. |
| Silence after `/cmd new-game` in agent mode | The loop only queues the turn. Check `data/inbox.jsonl` grew a line. Run the Agent routine: healthcheck, read inbox, `python -m bridge.send`. Add an hourly watchdog if the VM slept. |
| Group sees no new messages / “conflict” on getUpdates | Only **one** poller per bot token. Stop `grokgame` `python -m mesa.main` on the Desktop PC (and any other `getUpdates`) so this VM is the only loop. |

## Optional: instant Mesa wake

For RPG nights, set `MESA_WAKE_URL` and `MESA_WAKE_KEY` in `.env` (see `.env.example`).
The bridge POSTs on every inbox append. Never commit the key.



### Instant Mesa wake (webhook)

The bridge POSTs to `MESA_WAKE_URL` with `Authorization: Bearer <MESA_WAKE_KEY>` whenever it queues an inbox item.

- URL must be the routine **POST to** value (often `https://api2.cursor.sh/automations/webhook/<id>`).
- Key must start with **`crsr_`** (not `whsec_`). Copy it from the Mesa routine panel after saving a webhook trigger.
- HTTP 200 = Mesa run started. 401 = bad key. 400 = routine disabled or wrong host.

Fallback: the `Mesa bridge drain` routine every 5 minutes. For Misterio, pre-baked `blob.branches` make A/B/C/D instant even if wake fails.
