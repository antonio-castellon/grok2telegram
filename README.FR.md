[EN](README.md) | [ES](README.ES.md) | [**FR**](README.FR.md) | [DE](README.DE.md)

![Knight + dragon BBS night](docs/img/banner-bbs-netscape.png)

# grok2telegram

Règles de la table : [docs/SAFETY.md](docs/SAFETY.md).

Entre, accroche ton manteau. La taverne est un **groupe Telegram**. Le MJ est un **Agent Bot Grok** qui vit sur **sa propre VM** — pas sur ton laptop, pas sous le bureau à côté du Pentium qui sent encore 1996.

Frère errant de [grokgame](https://github.com/antonio-castellon/grokgame).  
`grokgame` = la table **sur ton PC**.  
`grok2telegram` = le même tuyau `/cmd` **sans serveur à la maison et sans `XAI_API_KEY`**.

Tu amènes les amis. Mesa amène les dés, les cartes ASCII et un timing suspect.

---

## Pourquoi ça existe ?

Parce que quelqu’un a dit : *« On peut jouer pour de vrai dans Telegram sans que je nounoute un process sur le Desktop PC ? »*

Oui.

- Les joueurs tapent dans le groupe comme dans un door game BBS.
- Un **bridge** Python mince long-poll (`getUpdates`) et répond en cartes BBS HTML `<pre>`.
- Ce qui demande un vrai cerveau de MJ va dans une **inbox**. **Mesa** se réveille, narre, invente des verbes, envoie un `say`.
- Le laptop **n’est pas** sur le chemin. Pas de ports entrants. L’Agent *est* celui qui parle.

Ne lance **pas** cette boucle et le `getUpdates` de `grokgame` en même temps sur le **même** token. Telegram choisit un favori ; l’autre pleure `409 Conflict`.

---

## Architecture (serviette)

```
  Aventuriers
      │
      ▼
 Groupe Telegram ──HTTPS──►  api.telegram.org
                                  ▲
                                  │ getUpdates / sendMessage
                                  │
                     ┌────────────┴────────────┐
                     │  Bridge Python (VM)     │
                     │  · parse /cmd & @bot    │
                     │  · verbes système       │
                     │  · file d’attente MJ    │
                     │  · skin BBS (WIDTH=28)  │
                     └────────────┬────────────┘
                                  │ data/inbox.jsonl
                                  ▼
                     ┌─────────────────────────┐
                     │  Mesa (Agent Grok)      │
                     │  invente, narre, joue   │
                     │  drain → bridge.send    │
                     └─────────────────────────┘
```

### Qui fait quoi ?

| Couche | Rôle | Vitesse |
|---|---|---|
| **Bridge** | Écoute toujours. Répond aux verbes **système** tout de suite (`help`, `status`, `clear`, …). | Instantané |
| **Inbox** | Parking pour le cerveau (`new-game`, `@bot` libre, verbes de partie). Ack : « Te leo… » | File |
| **Mesa** | Lit la file, parle en `table.lang`, tient `chat_*.json`, n’explique jamais le protocole dans le groupe. | Au réveil (webhook si branché ; sinon filet ~5 min) |

Le bridge reste **volontairement mince**. Il enseigne les commandes. Il ne joue pas au MJ pour « c’est ton tour, prends une carte ». (On a essayé. Le bridge s’est pris pour un caballero. Oros n’oublie pas.)

---

## Commandes

Même grammaire que grokgame :

```
/cmd <verbe> [payload]
@ton_bot <verbe> [payload]
@ton_bot <texte libre>     → verbe inbox "ask"
```

### Système (bridge, immédiat)

| Verbe | Effet |
|---|---|
| `help` / `help <verbe>` / `help extended` | Le parchemin. |
| `whoami` | Ton id, admin ou pas. |
| `lang` | Langue de table : `es` `en` `fr` `de`. |
| `status` | Titre, phase, **joueurs joined (noms seuls)**, règles, limites. |
| `rules` / `limit` | Règles / limites. |
| `cmd list` | Système + inventions de Mesa. |
| `clear` / `clear all` | Admin : purge. |
| `restart` | Admin : même partie, scores à zéro. |
| `unjoin` | Quitter la table. |
| `grant` / `revoke` | Admins. |
| `reset` | Nouveau lobby. |

### Partie (Mesa, après `new-game`)

Mesa invente. Classiques : `new-game`, `join`, puis le reste. Sinon → inbox → réponse en personnage.

**Protocole `new-game` :** si c’est flou, questions d’abord (lobby). Sinon : carte ASCII, mode d’emploi, `/cmd join`.

---

## Démarrage

**Install :** [SETUP.md](SETUP.md).  
**Doctrine MJ :** [docs/AGENT.md](docs/AGENT.md).

```bash
cp .env.example .env
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
scripts/start.sh
scripts/healthcheck.sh
```

Optionnel : `MESA_WAKE_URL` / `MESA_WAKE_KEY` pour un réveil MJ immédiat (jamais committer la key).

---

## Règle du poller unique

Un token. Un `getUpdates`.  
Cette VM **ou** la taverne PC — pas les deux.

---

*Insère une pièce. `/cmd help`. Évite le roman avant `/cmd join`.*
