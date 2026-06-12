# Configuração xAI (Grok) e Voz do KRATOS

Autor: Jossian Brito

Este documento explica como configurar o **cérebro** do KRATOS (xAI Grok) e a
**voz ao vivo** (xAI Realtime Voice API, voz **Leo**) no servidor, além dos
recursos de voz do navegador usados como alternativa.

---

## 1. Arquitetura: três camadas de voz/inteligência

| Camada | Tecnologia | Onde roda |
|--------|-----------|-----------|
| **Cérebro** (chat de texto, relatórios, insights) | xAI Grok (`/v1/chat/completions`) | Backend (`main.py`) |
| **🎧 Voz ao vivo** (conversa falada em tempo real) | **xAI Realtime Voice API** (`wss://api.x.ai/v1/realtime`, modelo `grok-voice-latest`, voz **Leo**) | Navegador ↔ xAI (token efêmero do backend) |
| **🎙️/🔊 Voz do navegador** (alternativa) | Web Speech API (STT/TTS) | Navegador (Chrome/Edge) |

### Como a voz ao vivo funciona (fluxo)
1. O usuário clica **🎧 Voz ao vivo** no painel.
2. O backend cunha um **token efêmero** em `POST https://api.x.ai/v1/realtime/client_secrets`
   (a `XAI_API_KEY` **nunca** vai ao navegador) e devolve as instruções do KRATOS
   com o **contexto operacional fresco** (insights do tabuleiro).
3. O navegador conecta a `wss://api.x.ai/v1/realtime?model=grok-voice-latest`
   usando o subprotocolo `xai-client-secret.<token>` e envia `session.update`
   com: voz `leo`, instruções, `server_vad`, transcrição (`grok-2-audio`) e
   áudio PCM 16-bit 24 kHz (captura via AudioWorklet `pcm-processor-worklet.js`).
4. O áudio do microfone é **bufferizado até `session.updated`** (nada se perde)
   e depois flui em tempo real; a resposta volta em chunks PCM reproduzidos em
   fila gapless. Se o usuário **falar por cima**, a reprodução é cortada e um
   `response.cancel` é enviado (interrupção natural).
5. As falas (usuário e KRATOS) aparecem **transcritas** no fio da conversa.

---

## 2. Console xAI — chave e endpoint Voice

1. Acesse **https://console.x.ai/**.
2. Em **API Keys**, crie/edite a chave (ex.: `kratos-prod`) e **habilite o
   endpoint Voice** para ela.
3. Em **Billing/Credits**, garanta créditos ativos.
4. (Opcional) Na **Voice library** do console, ouça as vozes built-in
   (Ara, Eve, **Leo**, Rex, Sal). O KRATOS usa **Leo** por padrão.

> 🔒 Trate a chave como senha. **Nunca** versione no Git — somente como variável
> de ambiente no cPanel.
> ℹ️ A Voice API atende na região `us-east-1`.

---

## 3. Configurar no cPanel (Aplicação Python)

Em **Setup Python App → Environment variables**:

| Variável | Valor | Observação |
|----------|-------|------------|
| `XAI_API_KEY` | *(chave do console xAI)* | obrigatória (texto e voz) — com endpoint Voice habilitado |
| `XAI_MODEL` | `grok-3-mini` | modelo do chat de texto (opcional) |
| `XAI_REALTIME_MODEL` | `grok-voice-latest` | modelo da voz ao vivo (opcional, é o padrão) |
| `XAI_VOICE` | `leo` | voz do KRATOS (opcional, é o padrão; alternativas: ara, eve, rex, sal) |

Depois **reinicie** o app (`touch tmp/restart.txt`).

> Sem `XAI_API_KEY`, o chat cai no **modo local** (regras) e a voz ao vivo
> retorna erro explicando a ausência da chave.

---

## 4. Uso no painel

- **🎧 Voz ao vivo** — conversa falada natural com a voz **Leo**; interrompível;
  transcrições no chat. Requer HTTPS (ok em `tuglife.live`) e permissão de microfone.
- **🎙️ Falar** — alternativa: reconhecimento de voz do navegador vira mensagem de texto.
- **🔊 Voz** — alternativa: o navegador lê em voz alta as respostas do chat de texto.
- **Mapa** — botão 🔊 na caixa de insights narra os insights (voz do navegador).

### Persona da voz
As instruções da sessão de voz usam a **persona oficial do KRATOS** (estrategista
naval / enxadrista do porto, SAA = SAAM, WIL/CAM concorrentes) + o contexto
operacional do momento, com diretriz de respostas curtas para conversa falada.
Para alterar a persona, edite `_kratos_voice_instructions()` em `main.py`.

---

## 5. Solução de problemas

| Sintoma | Causa provável | Ação |
|---------|----------------|------|
| "xAI recusou a criação do token (4xx)" | Chave sem endpoint Voice habilitado | Habilitar Voice na chave no console.x.ai |
| Voz não conecta / fecha logo | Sem créditos, rede bloqueando WSS | Conferir billing; testar rede |
| Microfone não abre | Permissão negada / sem HTTPS | Autorizar mic; usar https |
| Sem transcrição do usuário | — | Já configurado (`input_audio_transcription: grok-2-audio`) |
| Áudio picotado | Aba em segundo plano/CPU | Manter aba ativa durante a conversa |
