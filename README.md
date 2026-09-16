[**EN**](README.md) · [ES](README.ES.md)

# grok2telegram

A Grok **Agent Bot** that sits on **its own cloud VM**, long-polls a Telegram group, and writes back into that group.

This is the sibling of [grokgame](https://github.com/antonio-castellon/grokgame). That repo is the tavern **on your PC**. This repo is the same `/cmd` pipe **without a house server and without `XAI_API_KEY`**.

```
players → Telegram group → api.telegram.org
                              ↑ outbound HTTPS
                     this process on the Agent Bot VM
                     getUpdates  /  sendMessage
```

Your laptop is not in the path. No inbound ports. The Agent *is* the process that talks.

Do **not** run this loop and `grokgame` `getUpdates` at the same time on the same bot token.

**Setup:** [SETUP.md](SETUP.md).  
**What the Agent should believe:** [docs/AGENT.md](docs/AGENT.md).

## Play (mock, no Grok turn required)

```
GM_BACKEND=mock
python -m bridge
```

In the group:

```
/cmd whoami
/cmd lang es
/cmd new-game misterio en un faro, 3 jugadores, sin muerte permanente
/cmd cmd list
/cmd rules no se sale de noche
/cmd join
/cmd act miro las escaleras
/cmd reset
```

`GM_BACKEND=agent` writes `/cmd` that need a brain into `data/inbox.jsonl`. The Agent reads that file on its next turn and `python -m bridge.send --chat-id … --text …`.

## Commands

Same grammar as grokgame: `/cmd <verb> [payload]`.

System verbs: `help` `lang` `new-game` `rules` `limit` `cmd list` `status` `reset` `whoami` `grant` `revoke`.

Everything else is invented after `new-game`.
