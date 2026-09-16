[EN](README.md) · **ES**

# grok2telegram

Un **Agent Bot** de Grok que vive en **su VM**, hace long-poll a un grupo de Telegram y escribe en ese mismo grupo.

Hermano de [grokgame](https://github.com/antonio-castellon/grokgame). Aquel repo es la taberna **en tu PC**. Este es el mismo tubo `/cmd` **sin servidor en casa y sin `XAI_API_KEY`**.

```
jugadores → grupo Telegram → api.telegram.org
                                 ↑ HTTPS de salida
                        este proceso en la VM del Agent Bot
                        getUpdates  /  sendMessage
```

El portátil no está en el camino. Sin puertos de entrada. El Agent *es* quien habla.

No arranques este bucle y el `getUpdates` de `grokgame` a la vez con el mismo token.

**Montaje:** [SETUP.md](SETUP.md).  
**Lo que el Agent tiene que creerse:** [docs/AGENT.md](docs/AGENT.md).

## Probar (mock)

```
GM_BACKEND=mock
python -m bridge
```

En el grupo:

```
/cmd whoami
/cmd lang es
/cmd new-game misterio en un faro, 3 jugadores, sin muerte permanente
/cmd cmd list
/cmd join
/cmd act miro las escaleras
```

`GM_BACKEND=agent` deja los `/cmd` que necesitan cerebro en `data/inbox.jsonl`. El Agent los lee en su turno y responde con `python -m bridge.send`.
