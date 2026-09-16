# Un solo puente, boca en la VM

El webhook de Automations responde **202 vacío**. Eso no es un bug del bot: Grok no devuelve `say` en ese socket. El grupo solo oye un `sendMessage`.

## Camino que funciona (recomendado)

El Bridge **vive en la VM del Agent Mesa**:

```
Telegram  --getUpdates-->  python -m bridge   (VM Mesa)
Telegram  <--sendMessage--  el mismo proceso / python -m bridge.send
```

- `GM_BACKEND=mock` — el tubo habla solo (eco). Sirve para validar token y grupo.
- `GM_BACKEND=agent` — el Python guarda `data/inbox.jsonl`; Mesa lee, narra y hace `bridge.send`.

No hace falta `XAI_API_KEY`. No hace falta webhook.

## Qué parar en el PC

Si `grokgame` (`python -m mesa.main`) sigue en long-poll con el **mismo token**, Telegram entrega las updates a uno u otro, no a los dos. Apaga grokgame antes de `scripts/start.sh` aquí.

La automatización `GrokGameBot` puede quedar como timbre opcional. No lleva texto al grupo.

## Rutina del Agent

Cada hora (y al despertar):

1. `scripts/healthcheck.sh` — si falla, `scripts/start.sh`
2. `python -m bridge.drain` — si `pending > 0`, inventa `say` en `lang`
3. `python -m bridge.send --chat-id <id> --text "<say>"`
4. No expliques el protocolo en el grupo.
