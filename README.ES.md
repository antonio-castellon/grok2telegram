[EN](README.md) | [**ES**](README.ES.md) | [FR](README.FR.md) | [DE](README.DE.md)

![Knight + dragon BBS night](docs/img/banner-bbs-netscape.png)

# grok2telegram

Reglas de la mesa: [docs/SAFETY.md](docs/SAFETY.md).

Esto es un experimento con una premisa ridícula y una excusa adorable — un **fork de [grokgame](https://github.com/antonio-castellon/grokgame)** para que el Desktop PC pueda irse por fin a dormir.

**¿Puede un agente ser el máster?** No un motor de reglas con 400 páginas de erratas. Un cerebro. Esta noche dirige una cacería de dragones. Mañana reparte el 21. El sábado se convierte en Parchís con rencor extra. El mismo grupo, los mismos amigos, otra mesa.

El canal es **Telegram**, a propósito. Los críos ya lo tienen. Los padres también. Nadie tiene que instalar *Yet Another Game Client 3.2 (beta)* ni crearse una cuenta llamada `xXMagoOscuro2009Xx`. Si el teléfono sabe escribir en un grupo, ya está sentado a la mesa.

Es internet de los 90 colándose por una puerta de ahora. Antes de que las tarjetas gráficas tuvieran más ventiladores que un estadio, la gente jugaba en **BBS**, mazmorras ASCII y MUDs donde un dragón eran tres caracteres de fuego y mucha imaginación:

```
  /\
 /  \    "Oyes dados en la oscuridad."
< DM >
 \  /
  \/
```

La misma energía. Escribes un comando. Te llega una historia. Discutís si el orco tenía línea de visión. El tapete es un chat; el máster es Grok.

La primera mesa la hice **por diversión, para mi hijo**, para que meta a sus amigos en una partida sin reglamento, sin tienda y sin un «mínimo 40 GB». Un grupo. Un bot. Un adulto escribe `/cmd new-game …` en lenguaje de verdad. Grok inventa el resto.

**Este fork es el segundo reto:** ¿podemos hacer eso **sin cuidar un proceso Python en el Desktop PC**? Aquí el tubo `/cmd` vive en la **VM del Agent Bot**. Sin servidor en casa. Sin `XAI_API_KEY`. Si un agente puede ser máster esta noche, mañana puede ser un quiz, un monitor de campamento, un diablo de deberes, un cuentacuentos familiar — primero juegos, después otras mesas.

Si funciona, tenemos una taberna de bolsillo que no necesita el PC encendido. Si no, igual nos queda una noche rara y unas cartas ASCII. En cualquier caso: el caballero se queda en la caja, los críos en Telegram, y el adulto no tiene que explicar Steam *ni* `systemd` a un niño de doce años a las 22:17.

**¿Quieres abrir tu propia mesa?** Lo aburrido (e imprescindible) está en **[SETUP.md](SETUP.md)**.

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
