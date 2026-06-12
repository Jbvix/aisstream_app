# Configuração xAI (Grok) e Voz do KRATOS

Autor: Jossian Brito

Este documento explica como configurar o **cérebro** do KRATOS (xAI Grok) no
servidor e como funciona a **voz** (fala e escuta).

---

## 1. Arquitetura: cérebro x voz (importante)

O KRATOS separa duas camadas:

| Camada | Tecnologia | Onde roda |
|--------|-----------|-----------|
| **Cérebro** (raciocínio estratégico) | **xAI Grok** (`/v1/chat/completions`) | Backend (`main.py`) |
| **Voz** (falar e ouvir) | **Web Speech API** | Navegador (Chrome/Edge) |

> ⚠️ **A API do xAI é de texto.** Ela não expõe um endpoint público de TTS
> (falar) nem STT (ouvir). A "voz do Grok" do app oficial da xAI **não** está
> disponível via API. Por isso, a voz do KRATOS é feita no **navegador** com a
> Web Speech API — gratuita, em PT-BR, sem chave adicional. O Grok continua
> sendo quem **pensa**; o navegador é quem **fala e escuta**.

---

## 2. Console xAI — obter a chave de API

1. Acesse **https://console.x.ai/**.
2. Faça login / crie a conta da organização.
3. Em **API Keys**, clique **Create API Key**, nomeie (ex.: `kratos-prod`) e copie.
4. Em **Billing/Credits**, garanta créditos ativos.
5. (Opcional) Em **Models**, confirme o modelo desejado — o KRATOS usa por
   padrão `grok-3-mini` (ajustável por variável de ambiente).

> 🔒 Trate a chave como senha. **Nunca** versione no Git — somente como variável
> de ambiente no cPanel.

---

## 3. Configurar no cPanel (Aplicação Python)

Em **Setup Python App → Environment variables**, defina:

| Variável | Valor | Observação |
|----------|-------|------------|
| `XAI_API_KEY` | *(sua chave do console xAI)* | obrigatória para respostas com Grok |
| `XAI_MODEL` | `grok-3-mini` | opcional; troque se quiser outro modelo |

Depois **reinicie** o app (ou `touch tmp/restart.txt`).

> Sem `XAI_API_KEY`, o KRATOS continua funcionando em **modo local** (respostas
> por regras a partir do contexto real), apenas sem a fluência do Grok.

---

## 4. Voz do KRATOS (Web Speech API)

### Onde
- **Painel (dashboard):** botões **🎙️ Falar** (você fala → vira mensagem) e
  **🔊 Voz** (KRATOS responde falando). A conversa mantém memória de turno.
- **Mapa:** botão **🔊** na caixa de insights narra os insights em voz.

### Requisitos
- Navegador **Chrome** ou **Edge** (melhor suporte à Web Speech API).
- **HTTPS** (já é o caso em `tuglife.live`) — o microfone exige conexão segura.
- Permitir o **microfone** quando o navegador solicitar (para o 🎙️ Falar).
- Áudio do dispositivo ligado (para ouvir o 🔊).

### Comportamento
- A fala usa voz **pt-BR** se o sistema tiver uma instalada; senão, cai para a
  voz padrão do navegador.
- O reconhecimento captura **uma frase por vez** e envia automaticamente.
- Se o navegador não suportar, os botões aparecem desabilitados com aviso — o
  chat por texto continua normal.

---

## 5. Evolução futura (voz premium, opcional)

Para uma voz mais natural ("comandante"), é possível plugar um TTS premium
(ex.: ElevenLabs ou OpenAI TTS) no backend, gerando áudio a partir do texto do
Grok. Isso exige chave/serviço próprio e custo por uso — fica como evolução,
sem bloquear o uso atual.
