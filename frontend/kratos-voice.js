// KRATOS Voz ao vivo — xAI Realtime Voice API (voz Leo), módulo compartilhado.
// Usado pelo painel (dashboard) e pelo mapa (index). Conversa falada em tempo
// real: mic (PCM 24 kHz via AudioWorklet) -> wss://api.x.ai/v1/realtime -> áudio
// do Grok em fila gapless. A XAI_API_KEY NUNCA chega ao navegador: o backend
// cunha um token efêmero via /api/kratos/voice-session.
//
// Uso:
//   const voice = createKratosLiveVoice({
//     apiUrl,                       // (path) => url absoluta
//     workletPath: "/frontend/pcm-processor-worklet.js",
//     onUserText:   (t) => {},      // transcrição do que o usuário falou
//     onAssistantText: (t) => {},   // texto parcial/total do KRATOS (streaming)
//     onAssistantInterrupted: () => {},
//     onSystem:     (msg) => {},    // mensagens de status/erro
//     onStateChange:(active) => {}, // liga/desliga
//   });
//   voice.start(); voice.stop(); voice.isActive();

function createKratosLiveVoice(cfg) {
  const apiUrl = cfg.apiUrl || ((p) => p);
  const workletPath = cfg.workletPath || "/frontend/pcm-processor-worklet.js";
  const onUserText = cfg.onUserText || (() => {});
  const onAssistantText = cfg.onAssistantText || (() => {});
  const onAssistantInterrupted = cfg.onAssistantInterrupted || (() => {});
  const onSystem = cfg.onSystem || (() => {});
  const onStateChange = cfg.onStateChange || (() => {});

  let ws = null;
  let audioCtx = null;
  let micStream = null;
  let workletNode = null;
  let sourceNode = null;
  let active = false;
  let sessionReady = false;
  let micBuffer = [];
  let micBufferedSamples = 0;
  const MIC_BUFFER_CAP = 240000; // ~10 s @ 24 kHz
  let nextPlayTime = 0;
  const queuedSources = [];
  let liveText = "";
  let intentionalClose = false;

  function audioToBase64(int16Array) {
    const bytes = new Uint8Array(int16Array.buffer, int16Array.byteOffset, int16Array.byteLength);
    const CHUNK = 0x2000;
    const parts = [];
    for (let i = 0; i < bytes.length; i += CHUNK) {
      parts.push(String.fromCharCode.apply(null, bytes.subarray(i, i + CHUNK)));
    }
    return btoa(parts.join(""));
  }

  function playPcmChunk(base64) {
    if (!audioCtx) return;
    const raw = atob(base64);
    const bytes = new Uint8Array(raw.length);
    for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
    const int16 = new Int16Array(bytes.buffer);
    const float32 = new Float32Array(int16.length);
    for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 32768;
    const buf = audioCtx.createBuffer(1, float32.length, 24000);
    buf.getChannelData(0).set(float32);
    const src = audioCtx.createBufferSource();
    src.buffer = buf;
    src.connect(audioCtx.destination);
    const startAt = Math.max(audioCtx.currentTime, nextPlayTime);
    src.start(startAt);
    nextPlayTime = startAt + buf.duration;
    queuedSources.push(src);
    src.onended = () => {
      const idx = queuedSources.indexOf(src);
      if (idx !== -1) queuedSources.splice(idx, 1);
    };
  }

  function interruptPlayback() {
    for (const src of queuedSources) { try { src.stop(); } catch (_) {} }
    queuedSources.length = 0;
    nextPlayTime = 0;
  }

  function handleEvent(event) {
    switch (event.type) {
      case "session.updated":
        if (!sessionReady) {
          sessionReady = true;
          for (const chunk of micBuffer) {
            ws.send(JSON.stringify({ type: "input_audio_buffer.append", audio: audioToBase64(chunk) }));
          }
          micBuffer = [];
          micBufferedSamples = 0;
        }
        break;
      case "input_audio_buffer.speech_started":
        interruptPlayback();
        try { ws.send(JSON.stringify({ type: "response.cancel" })); } catch (_) {}
        if (liveText) onAssistantInterrupted();
        liveText = "";
        break;
      case "conversation.item.input_audio_transcription.completed":
        if (event.transcript) onUserText(String(event.transcript));
        break;
      case "response.created":
        liveText = "";
        break;
      case "response.output_audio.delta":
        if (event.delta) playPcmChunk(event.delta);
        break;
      case "response.output_audio_transcript.delta":
        if (event.delta) {
          liveText += event.delta;
          onAssistantText(liveText);
        }
        break;
      case "response.done":
        liveText = "";
        break;
      case "error": {
        const err = event.error || event;
        const detail = err.message || err.code || err.type || JSON.stringify(event).slice(0, 200);
        onSystem("Voz ao vivo — erro: " + detail);
        break;
      }
    }
  }

  async function start() {
    if (active) return;
    intentionalClose = false;
    audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
    if (audioCtx.state === "suspended") await audioCtx.resume();

    const tokenPromise = (async () => {
      const paths = ["/api/kratos/voice-session", "/dashboard/api/kratos/voice-session"];
      // Corpo opcional (ex.: visão do mapa) fornecido pelo chamador.
      let reqBody = null;
      try { reqBody = cfg.getSessionBody ? cfg.getSessionBody() : null; } catch (_) {}
      const fetchOpts = {
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        body: JSON.stringify(reqBody || {}),
      };
      let body = null;
      for (const p of paths) {
        const res = await fetch(apiUrl(p), fetchOpts);
        body = await res.json().catch(() => ({}));
        if (res.status !== 404) {
          if (!res.ok || !body.ok) throw new Error(body.error || ("HTTP " + res.status));
          return body;
        }
      }
      throw new Error((body && body.error) || "endpoint indisponível");
    })();

    micStream = await navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, sampleRate: 24000 },
    });
    await audioCtx.audioWorklet.addModule(apiUrl(workletPath));
    sourceNode = audioCtx.createMediaStreamSource(micStream);
    workletNode = new AudioWorkletNode(audioCtx, "pcm-processor");
    sourceNode.connect(workletNode);
    sessionReady = false;
    micBuffer = [];
    micBufferedSamples = 0;
    workletNode.port.onmessage = (ev) => {
      const int16 = ev.data;
      if (sessionReady && ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "input_audio_buffer.append", audio: audioToBase64(int16) }));
      } else if (micBufferedSamples < MIC_BUFFER_CAP) {
        micBuffer.push(int16);
        micBufferedSamples += int16.length;
      }
    };

    const session = await tokenPromise;
    ws = new WebSocket(
      "wss://api.x.ai/v1/realtime?model=" + encodeURIComponent(session.model || "grok-voice-latest"),
      ["xai-client-secret." + session.token]
    );
    const connectTimeout = setTimeout(() => {
      if (ws && ws.readyState !== WebSocket.OPEN) { try { ws.close(); } catch (_) {} }
    }, 10000);
    ws.onopen = () => {
      clearTimeout(connectTimeout);
      ws.send(JSON.stringify({
        type: "session.update",
        session: {
          voice: session.voice || "leo",
          instructions: session.instructions || "",
          turn_detection: { type: "server_vad" },
          tools: [{ type: "web_search" }, { type: "x_search" }],
          input_audio_transcription: { model: "grok-2-audio" },
          audio: {
            input: { format: { type: "audio/pcm", rate: 24000 } },
            output: { format: { type: "audio/pcm", rate: 24000 } },
          },
        },
      }));
    };
    ws.onmessage = (msg) => {
      let event = null;
      try { event = JSON.parse(msg.data); } catch (_) { return; }
      handleEvent(event);
    };
    ws.onerror = () => {};
    ws.onclose = (ev) => {
      if (active && !intentionalClose) {
        const code = ev && ev.code ? ev.code : "";
        const reason = (ev && ev.reason) ? " — " + ev.reason : "";
        const hint = code === 1006
          ? " (não conectou: verifique se a chave tem o endpoint Voice habilitado e créditos no console.x.ai)"
          : (String(code).startsWith("40") || code === 1008)
            ? " (autenticação/permissão recusada pela xAI)"
            : "";
        onSystem("Voz ao vivo desconectada" + (code ? " [" + code + "]" : "") + reason + hint);
      }
      cleanup();
    };
    active = true;
    onStateChange(true);
    onSystem("Voz ao vivo conectada (voz Leo). Pode falar — eu ouço e respondo.");
  }

  function cleanup() {
    active = false;
    sessionReady = false;
    interruptPlayback();
    try { workletNode && workletNode.disconnect(); } catch (_) {}
    try { sourceNode && sourceNode.disconnect(); } catch (_) {}
    try { micStream && micStream.getTracks().forEach((t) => t.stop()); } catch (_) {}
    try { audioCtx && audioCtx.close(); } catch (_) {}
    ws = null; audioCtx = null; micStream = null; workletNode = null; sourceNode = null;
    micBuffer = []; micBufferedSamples = 0;
    onStateChange(false);
  }

  function stop() {
    intentionalClose = true;
    try { ws && ws.close(); } catch (_) {}
    cleanup();
  }

  return { start, stop, isActive: () => active };
}

window.createKratosLiveVoice = createKratosLiveVoice;
