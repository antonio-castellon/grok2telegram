[EN](README.md) · [**ES**](README.ES.md) · [FR](README.FR.md) · [DE](README.DE.md)

```
╔══════════════════════════════════════════════════════════╗
║  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄  ║
║  █  ***  G R O K 2 T E L E G R A M  B B S  ***       █  ║
║  █      rol de los 90 · sin RTC · solo /cmd          █  ║
║  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀  ║
║   SysOp: Mesa   ·   Tablero: tu grupo de Telegram        ║
║   "Tirad iniciativa. El módem es opcional."              ║
╚══════════════════════════════════════════════════════════╝
```

# grok2telegram

Pasa, cuelga la capa. La taberna es un **grupo de Telegram**. El máster es un **Agent Bot de Grok** que vive en **su propia VM** — no en tu portátil, ni debajo del escritorio junto al Pentium que aún huele a 1996.

Hermano errante de [grokgame](https://github.com/antonio-castellon/grokgame).  
`grokgame` = la mesa **en tu PC**.  
`grok2telegram` = el mismo tubo `/cmd` **sin servidor en casa y sin `XAI_API_KEY`**.

Tú traes amigos. Mesa trae dados, cartas ASCII y un timing sospechosamente bueno.

---

## ¿Para qué existe esto?

Porque alguien dijo: *“¿Podemos jugar de verdad en Telegram sin que yo cuide un proceso en el Yoga?”*

Sí.

- Los jugadores escriben en el grupo como en un door game de BBS.
- Un **bridge** Python delgado hace long-poll (`getUpdates`) y responde con tarjetas BBS en HTML `<pre>`.
- Lo que necesita cerebro de GM va a una **inbox**. **Mesa** (el Agent) despierta, narra, inventa verbos y manda un `say`.
- El portátil **no** está en el camino. Sin puertos de entrada. El Agent *es* quien habla.

No arranques este bucle y el `getUpdates` de `grokgame` **a la vez** con el mismo token. Telegram elige favorito y el otro llora `409 Conflict`.

---

## Arquitectura (servilleta)

```
  Aventureros
      │
      ▼
 Grupo Telegram  ──HTTPS──►  api.telegram.org
                                  ▲
                                  │ getUpdates / sendMessage
                                  │
                     ┌────────────┴────────────┐
                     │  Bridge Python (VM)     │
                     │  · parse /cmd y @bot    │
                     │  · verbos de sistema    │
                     │  · encola verbos GM     │
                     │  · skin BBS (WIDTH=28)  │
                     └────────────┬────────────┘
                                  │ data/inbox.jsonl
                                  ▼
                     ┌─────────────────────────┐
                     │  Mesa (Agent Grok)      │
                     │  inventa, narra, juega  │
                     │  drain → bridge.send    │
                     └─────────────────────────┘
```

### ¿Quién hace qué?

| Capa | Trabajo | Velocidad |
|---|---|---|
| **Bridge** | Escucha siempre. Contesta verbos de **sistema** al momento (`help`, `status`, `clear`, …). Enmarca como SysOp con gusto. | Instantáneo |
| **Inbox** | Parking de lo que necesita cerebro (`new-game`, chat libre `@bot`, verbos de partida). Ack: “Te leo…” | Cola |
| **Mesa** | Lee la cola, habla en `table.lang`, mantiene `chat_*.json`, nunca explica el protocolo en el grupo. | Al despertar (webhook si está; si no, red de ~5 min) |

El bridge es **deliberadamente delgado**. Enseña comandos y pulsa interruptores. **No** finge entender “te toca, pide carta” — eso es de Mesa. (Lo intentamos. El bridge se vino arriba. El caballo de oros no olvida.)

---

## Comandos

Misma gramática que grokgame:

```
/cmd <verbo> [payload]
@tu_bot <verbo> [payload]
@tu_bot <texto libre>     → verbo inbox "ask"
```

### Sistema (bridge, al instante)

| Verbo | Qué hace |
|---|---|
| `help` / `help <verbo>` / `help extended` | El pergamino sagrado. |
| `whoami` | Tu id y si eres admin. |
| `lang` | Idioma de mesa: `es` `en` `fr` `de`. |
| `status` | Título, fase, **jugadores joined (solo nombres)**, reglas, límites. |
| `rules` / `limit` | Añadir o ver reglas / límites. |
| `cmd list` | Sistema + lo que Mesa inventó. |
| `clear` / `clear all` | Admin: borra mensajes recientes. |
| `restart` | Admin: misma partida, manos a cero. |
| `unjoin` | Salir (o sacar a alguien). |
| `grant` / `revoke` | Admins. |
| `reset` | Lobby nuevo. Tierra quemada. |

### De partida (Mesa, tras `new-game`)

Mesa los inventa. Clásicos:

```
/cmd new-game …
/cmd join
```

Luego lo que pida el tablero. Si no es de sistema → inbox → Mesa responde en personaje.

**Protocolo `new-game`:** si hay duda, primero preguntas cortas (sigue lobby). Cuando esté claro: tarjeta ASCII con el nombre, cómo se juega, `/cmd join`.

---

## Arranque

**Montaje:** [SETUP.md](SETUP.md).  
**Doctrina del GM:** [docs/AGENT.md](docs/AGENT.md).

```bash
cp .env.example .env
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
scripts/start.sh
scripts/healthcheck.sh
```

Noche mock (sin cerebro de Agent):

```bash
GM_BACKEND=mock python -m bridge
```

### Opcional: wake instantáneo del GM

```
MESA_WAKE_URL=…
MESA_WAKE_KEY=…    # nunca al repo
```

El bridge hace POST en cada `append_inbox`. Sin eso, el drain programado es la red de seguridad.

---

## Archivos que importan

```
bridge/          # el tubo
data/            # chat_*.json, inbox.jsonl, pid
scripts/         # start.sh, healthcheck.sh
docs/AGENT.md    # lo que Mesa debe creerse
```

---

## Regla del un solo poller

Un token. Un `getUpdates`.  
Esta VM **o** la taberna del PC — no las dos. El SysOp ha hablado.

---

*Inserta moneda. `/cmd help`. No le escribas una novela al bot antes de `/cmd join`.*
