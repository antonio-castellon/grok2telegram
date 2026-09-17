[EN](README.md) | [ES](README.ES.md) | [FR](README.FR.md) | [**DE**](README.DE.md)

![Knight + dragon BBS night](docs/img/banner-bbs-netscape.png)

# grok2telegram

Tischregeln: [docs/SAFETY.md](docs/SAFETY.md).

Das hier ist ein Experiment mit einer albernen Prämisse und einer herzlichen Ausrede — ein **Fork von [grokgame](https://github.com/antonio-castellon/grokgame)**, damit der Desktop PC endlich schlafen gehen darf.

**Kann ein Agent der Spielleiter sein?** Keine Regelmaschine mit 400 Seiten Errata. Ein Gehirn. Heute Abend leitet er eine Drachenjagd. Morgen gibt er 21 aus. Am Samstag wird er zum Parchís mit Extra-Bosheit. Dieselbe Gruppe, dieselben Freunde, ein neuer Tisch.

Der Kanal ist **Telegram**, absichtlich. Die Kinder haben es schon. Die Eltern auch. Niemand muss *Yet Another Game Client 3.2 (beta)* installieren oder einen Account namens `xXDunklerMagier2009Xx` anlegen. Wenn das Handy in eine Gruppe tippen kann, hat es schon einen Platz an diesem Tisch.

Das ist das alte Internet, das sich durch eine moderne Tür mogelt. Bevor Grafikkarten mehr Lüfter hatten als ein Fußballstadion, spielte man auf **BBS-Boards**, ASCII-Kerkern und MUDs, wo ein Drache aus drei Zeichen Feuer und sehr viel Vorstellungskraft bestand:

```
  /\
 /  \    "Du hörst Würfel in der Dunkelheit."
< DM >
 \  /
  \/
```

Dieselbe Energie. Befehl tippen. Geschichte kriegen. Streiten, ob der Ork wirklich Sichtlinie hatte. Das Filz ist ein Chatfenster; der Meister ist Grok.

Den ersten Tisch habe ich **zum Spaß, für meinen Sohn** gebaut, damit er seine Freunde in ein Spiel ziehen kann — ohne Regelbuch, ohne Shop, ohne „mindestens 40 GB Download“. Eine Gruppe. Ein Bot. Ein Erwachsener schreibt `/cmd new-game …` in normaler Sprache. Grok erfindet den Rest.

**Dieser Fork ist die zweite Wette:** geht das **ohne einen Python-Prozess auf dem Desktop PC zu babysitten**? Hier lebt die dünne `/cmd`-Pipe auf der **Agent-Bot-VM**. Kein Heimserver. Kein `XAI_API_KEY`. Wenn ein Agent heute SL sein kann, kann er morgen Quizmaster sein, Betreuer, Hausaufgaben-Teufel, Familienerzähler — erst Spiele, dann andere Tische.

Wenn es klappt, haben wir eine Taschentaverne, die den PC nicht anlassen muss. Wenn nicht, bleibt wenigstens ein schräger Abend und ein paar ASCII-Karten. So oder so: der Ritter bleibt auf der Schachtel, die Kinder bleiben bei Telegram, und der Erwachsene muss einem Zwölfjährigen um 22:17 weder Steam *noch* `systemd` erklären.

**Eigenen Tisch aufmachen?** Das Langweilige (aber Nötige) steht in **[SETUP.md](SETUP.md)**.

Starte **nicht** diese Schleife und `grokgame`s `getUpdates` gleichzeitig mit dem **selben** Token. Telegram wählt Favoriten; der andere heult `409 Conflict`.

---

## Architektur (Serviette)

```
  Abenteurer
      │
      ▼
 Telegram-Gruppe ──HTTPS──►  api.telegram.org
                                  ▲
                                  │ getUpdates / sendMessage
                                  │
                     ┌────────────┴────────────┐
                     │  Python-Bridge (VM)     │
                     │  · parse /cmd & @bot    │
                     │  · System-Verben        │
                     │  · SL-Warteschlange     │
                     │  · BBS-Skin (WIDTH=28)  │
                     └────────────┬────────────┘
                                  │ data/inbox.jsonl
                                  ▼
                     ┌─────────────────────────┐
                     │  Mesa (Grok-Agent)      │
                     │  erfindet, erzählt      │
                     │  drain → bridge.send    │
                     └─────────────────────────┘
```

### Wer macht was?

| Schicht | Aufgabe | Tempo |
|---|---|---|
| **Bridge** | Hört immer zu. Beantwortet **System**-Verben sofort (`help`, `status`, `clear`, …). | Sofort |
| **Inbox** | Parkplatz für Gehirn (`new-game`, freies `@bot`, Spielverben). Ack: „Te leo…“ | Warteschlange |
| **Mesa** | Liest die Queue, spricht `table.lang`, hält `chat_*.json`, erklärt nie das Protokoll in der Gruppe. | Beim Wake (Webhook falls verdrahtet; sonst ~5-Min-Netz) |

Die Bridge bleibt **absichtlich dünn**. Sie erklärt Befehle. Sie spielt nicht SL für „du bist dran, zieh eine Karte“. (Haben wir versucht. Die Bridge wurde übermütig. Der Caballo de Oros vergisst nicht.)

---

## Befehle

Gleiche Grammatik wie grokgame:

```
/cmd <verb> [payload]
@dein_bot <verb> [payload]
@dein_bot <Freitext>     → Inbox-Verb "ask"
```

### System (Bridge, sofort)

| Verb | Wirkung |
|---|---|
| `help` / `help <verb>` / `help extended` | Die heilige Schriftrolle. |
| `whoami` | Deine Id, Admin ja/nein. |
| `lang` | Tischsprache: `es` `en` `fr` `de`. |
| `status` | Titel, Phase, **joined Spieler (nur Namen)**, Regeln, Limits. |
| `rules` / `limit` | Regeln / Limits. |
| `cmd list` | System + Mesas Erfindungen. |
| `clear` / `clear all` | Admin: Nachrichten löschen. |
| `restart` | Admin: gleiches Spiel, Hände weg. |
| `unjoin` | Tisch verlassen. |
| `grant` / `revoke` | Admins. |
| `reset` | Neue Lobby. |

### Spiel (Mesa, nach `new-game`)

Mesa erfindet sie. Klassiker: `new-game`, `join`, dann der Rest. Sonst → Inbox → Antwort in Rolle.

**`new-game`-Protokoll:** unklar → kurze Fragen (Lobby). Klar → ASCII-Titel, Kurzanleitung, `/cmd join`.

---

## Start

**Setup:** [SETUP.md](SETUP.md).  
**SL-Doktrin:** [docs/AGENT.md](docs/AGENT.md).

```bash
cp .env.example .env
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
scripts/start.sh
scripts/healthcheck.sh
```

Optional: `MESA_WAKE_URL` / `MESA_WAKE_KEY` für sofortigen SL-Wake (Key nie committen).

---

## Ein-Poller-Regel

Ein Token. Ein `getUpdates`.  
Diese VM **oder** die PC-Taverne — nicht beides.

---

*Münze einwerfen. `/cmd help`. Keinen Roman vor `/cmd join`.*
