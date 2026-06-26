/*
 * kratos-core.js — helpers reutilizáveis (genérico, sem domínio).
 *
 * Inclui:
 *  - KC.base()        → caminho base (suporta subcaminho/root_path).
 *  - KC.api(path)     → monta URL de API respeitando o base.
 *  - KC.fetchJSON()   → fetch com credentials + tratamento de 401 (→ /entrar).
 *  - KC.Alerts        → Central de Alertas (som via Web Audio, popup, notificação, prefs).
 *  - KC.VoiceOrb      → orb visual (placeholder de assistente de voz).
 *
 * TODO-DOMINIO: ligue KC.Alerts.fire(...) aos eventos reais do seu app.
 */
(function (global) {
  "use strict";

  var KC = {};

  // ---------- Base / API ----------
  // Remove sufixos de página conhecidos para descobrir o prefixo de montagem.
  KC.base = function () {
    return location.pathname.replace(/\/(index\.html|entrar|admin|versao)?\/?$/, "") || "";
  };
  KC.api = function (path) { return KC.base() + path; };

  KC.onAuthRequired = function () {
    // 401 no polling → manda para o login preservando o base.
    location.href = KC.base() + "/entrar";
  };

  KC.fetchJSON = function (path, opts) {
    opts = opts || {};
    opts.credentials = "include";
    return fetch(KC.api(path), opts).then(function (r) {
      if (r.status === 401) { KC.onAuthRequired(); throw new Error("unauthorized"); }
      return r.json();
    });
  };

  // ---------- Central de Alertas ----------
  var Alerts = (function () {
    var PREF_KEY = "kratos_core_alert_prefs";
    var audioCtx = null;
    // Tipos de alerta — gravidade controla o som. TODO-DOMINIO: ajuste a lista.
    var TYPES = {
      info:    { label: "Informação", freq: 660,  severity: 1 },
      warning: { label: "Atenção",    freq: 880,  severity: 2 },
      danger:  { label: "Crítico",    freq: 1180, severity: 3 }
    };

    function prefs() {
      try { return JSON.parse(localStorage.getItem(PREF_KEY) || "{}"); } catch (e) { return {}; }
    }
    function setPref(type, on) {
      var p = prefs(); p[type] = !!on;
      try { localStorage.setItem(PREF_KEY, JSON.stringify(p)); } catch (e) {}
    }
    function enabled(type) { var p = prefs(); return p[type] !== false; }

    function beep(type) {
      var def = TYPES[type] || TYPES.info;
      try {
        audioCtx = audioCtx || new (global.AudioContext || global.webkitAudioContext)();
        var o = audioCtx.createOscillator(), g = audioCtx.createGain();
        o.type = "sine"; o.frequency.value = def.freq;
        g.gain.setValueAtTime(0.0001, audioCtx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.25, audioCtx.currentTime + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.35);
        o.connect(g); g.connect(audioCtx.destination);
        o.start(); o.stop(audioCtx.currentTime + 0.36);
      } catch (e) {}
    }

    function toast(type, title, body) {
      var def = TYPES[type] || TYPES.info;
      var host = document.getElementById("kc-toasts");
      if (!host) {
        host = document.createElement("div"); host.id = "kc-toasts";
        host.style.cssText = "position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);" +
          "z-index:1600;display:flex;flex-direction:column;gap:10px;align-items:center;pointer-events:none;";
        document.body.appendChild(host);
      }
      var color = def.severity >= 3 ? "#ff5c6c" : def.severity === 2 ? "#f1c40f" : "#3da9fc";
      var card = document.createElement("div");
      card.style.cssText = "pointer-events:auto;min-width:240px;max-width:84vw;background:#111826;" +
        "border:1px solid " + color + ";border-left:4px solid " + color + ";border-radius:12px;" +
        "padding:12px 16px;color:#e6edf6;box-shadow:0 14px 40px rgba(0,0,0,.5);font:14px system-ui,sans-serif;";
      card.innerHTML = "<strong style='color:" + color + "'>" + (title || def.label) + "</strong>" +
        (body ? "<div style='margin-top:4px;color:#b9c7da'>" + body + "</div>" : "");
      host.appendChild(card);
      setTimeout(function () { card.style.transition = "opacity .4s"; card.style.opacity = "0";
        setTimeout(function () { card.remove(); }, 400); }, 4200);
    }

    function notify(title, body) {
      try {
        if (!("Notification" in global)) return;
        if (Notification.permission === "granted") new Notification(title, { body: body });
        else if (Notification.permission !== "denied") Notification.requestPermission();
      } catch (e) {}
    }

    function fire(type, title, body, opts) {
      opts = opts || {};
      if (!enabled(type)) return;
      if (opts.sound !== false) beep(type);
      if (opts.toast !== false) toast(type, title, body);
      if (opts.notify) notify(title || (TYPES[type] || {}).label, body);
    }

    function requestPermission() { try { if ("Notification" in global) Notification.requestPermission(); } catch (e) {} }

    return { TYPES: TYPES, fire: fire, setPref: setPref, enabled: enabled, requestPermission: requestPermission };
  })();
  KC.Alerts = Alerts;

  // ---------- Dynamic Voice Orb (placeholder) ----------
  var VoiceOrb = (function () {
    var node = null, state = "idle";
    function mount(target) {
      target = typeof target === "string" ? document.getElementById(target) : target;
      if (!target) return null;
      node = document.createElement("div");
      node.className = "kc-orb";
      node.style.cssText = "width:56px;height:56px;border-radius:50%;cursor:pointer;" +
        "background:radial-gradient(circle at 35% 30%, #6fd3ff, #2a7fff 60%, #134b9e);" +
        "box-shadow:0 0 18px rgba(61,169,252,.6);transition:transform .2s, box-shadow .2s;";
      target.appendChild(node);
      return node;
    }
    function set(s) {
      state = s; if (!node) return;
      if (s === "listening") { node.style.transform = "scale(1.12)"; node.style.boxShadow = "0 0 28px rgba(46,204,113,.8)"; }
      else if (s === "speaking") { node.style.transform = "scale(1.06)"; node.style.boxShadow = "0 0 28px rgba(241,196,15,.8)"; }
      else { node.style.transform = "scale(1)"; node.style.boxShadow = "0 0 18px rgba(61,169,252,.6)"; }
    }
    return { mount: mount, set: set, get state() { return state; } };
  })();
  KC.VoiceOrb = VoiceOrb;

  global.KC = KC;
})(window);
