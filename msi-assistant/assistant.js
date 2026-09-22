/* MSI Assistant chat widget — Machine Solutions equipment troubleshooting.
   Include with:  <script src="assistant/assistant.js" data-app="braiding" defer></script>
   Optional data-endpoint="https://…/chat" overrides the default API endpoint. */
(function () {
  if (window.__msiAssistant) return; window.__msiAssistant = true;
  const me = document.currentScript || [...document.scripts].find(s => /assistant\.js/.test(s.src));
  const ENDPOINT = (me && me.dataset.endpoint) || "https://msi-assistant.adam-wade.workers.dev/chat";
  const APP = (me && me.dataset.app) || "";
  const BASE = new URL("../", me ? me.src : location.href);   // site root (assistant.js lives in /assistant/)
  const STORE = "msia.history.v1";
  const WELCOME = "Hi, I'm the Machine Solutions Assistant. Describe what the machine or part is doing, or paste the exact alarm text, and I'll walk you through the likely causes from our troubleshooting guides.";

  const css = `
.msia{--n:#002D72;--g:#6CC24A;--b:#00A8E0;--c:#53565A;--bg:#fff;--bg2:#F2F4F8;--ln:#D4D5D6;--tx:#53565A;--hd:#002D72;--me:#002D72;--meTx:#fff;--lk:#002D72;
  font-family:"Museo Sans","MuseoSans-500",Arial,Helvetica,sans-serif;font-weight:500;line-height:1.45;color:var(--tx)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .msia{--bg:#00245B;--bg2:#00193F;--ln:#406295;--tx:#fff;--hd:#fff;--me:#00A8E0;--meTx:#002D72;--lk:#00A8E0}}
:root[data-theme="dark"] .msia{--bg:#00245B;--bg2:#00193F;--ln:#406295;--tx:#fff;--hd:#fff;--me:#00A8E0;--meTx:#002D72;--lk:#00A8E0}
.msia *{box-sizing:border-box}
.msia-fab{position:fixed;right:16px;bottom:calc(16px + env(safe-area-inset-bottom,0px) + var(--msia-lift,0px));z-index:70;display:flex;align-items:center;gap:8px;
  background:#002D72;color:#fff;border:0;border-radius:999px;padding:12px 18px 12px 14px;font:inherit;font-weight:700;font-size:.95rem;cursor:pointer;
  box-shadow:0 0 0 3px #6CC24A inset,0 6px 20px rgba(0,45,114,.3);transition:transform .15s}
.msia-fab:hover{transform:translateY(-2px)}.msia-fab svg{width:22px;height:22px;flex:none}
@media (max-width:560px){.msia-fab span{display:none}.msia-fab{padding:14px}}
.msia-panel{position:fixed;right:16px;bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:71;width:400px;max-width:calc(100vw - 32px);
  height:min(640px,calc(100vh - 32px));background:var(--bg);border:1px solid var(--ln);border-radius:14px;display:flex;flex-direction:column;overflow:hidden;
  box-shadow:0 18px 50px rgba(0,20,60,.35)}
.msia-panel[hidden],.msia-fab[hidden]{display:none}
@media (max-width:560px){.msia-panel{right:0;left:0;bottom:0;top:0;width:auto;max-width:none;height:auto;border-radius:0;border:0;
  padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
.msia-head{display:flex;align-items:center;gap:10px;padding:12px 14px;background:#002D72;color:#fff;box-shadow:inset 0 -3px 0 #6CC24A}
.msia-head img{width:34px;height:34px;background:#fff;border-radius:8px;padding:3px;flex:none}
.msia-head b{display:block;font-size:1rem}.msia-head small{display:block;font-size:.72rem;opacity:.85;font-weight:300}
.msia-head .sp{flex:1}.msia-head button{background:transparent;border:0;color:#fff;font:inherit;cursor:pointer;padding:6px;border-radius:6px;opacity:.9}
.msia-head button:hover{background:rgba(255,255,255,.12)}
.msia-log{flex:1;overflow-y:auto;padding:14px;background:var(--bg2);display:flex;flex-direction:column;gap:10px}
.msia-m{max-width:88%;padding:10px 12px;border-radius:12px;font-size:.92rem;word-wrap:break-word}
.msia-m.a{background:var(--bg);border:1px solid var(--ln);align-self:flex-start;border-bottom-left-radius:4px}
.msia-m.u{background:var(--me);color:var(--meTx);align-self:flex-end;border-bottom-right-radius:4px;white-space:pre-wrap}
.msia-m p{margin:0 0 6px}.msia-m p:last-child{margin:0}.msia-m ol,.msia-m ul{margin:4px 0 6px;padding-left:1.3em}.msia-m li{margin:2px 0}
.msia-m a{color:var(--lk);font-weight:700}.msia-m strong{color:var(--hd)}.msia-m code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.85em}
.msia-m.err{border-color:#B3261E}
.msia-typing{display:inline-flex;gap:4px}.msia-typing i{width:7px;height:7px;border-radius:50%;background:var(--c);opacity:.4;animation:msia 1s infinite}
.msia-typing i:nth-child(2){animation-delay:.15s}.msia-typing i:nth-child(3){animation-delay:.3s}
@keyframes msia{50%{opacity:1;transform:translateY(-2px)}}
.msia-chips{display:flex;flex-wrap:wrap;gap:6px;padding:0 14px 10px;background:var(--bg2)}
.msia-chips button{font:inherit;font-size:.8rem;border:1px solid var(--ln);background:var(--bg);color:var(--hd);border-radius:999px;padding:6px 10px;cursor:pointer;font-weight:700}
.msia-chips button:hover{border-color:var(--hd)}
.msia-in{display:flex;gap:8px;padding:10px;border-top:1px solid var(--ln);background:var(--bg)}
.msia-in textarea{flex:1;resize:none;font:inherit;font-size:16px;color:var(--tx);background:var(--bg);border:1px solid var(--ln);border-radius:10px;padding:9px 10px;max-height:120px;min-height:42px}
.msia-in textarea:focus{outline:2px solid var(--b);outline-offset:0;border-color:transparent}
.msia-in button{background:#002D72;color:#fff;border:0;border-radius:10px;padding:0 14px;font:inherit;font-weight:700;cursor:pointer}
.msia-in button:disabled{opacity:.5;cursor:default}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .msia-in button{background:#00A8E0;color:#002D72}}
:root[data-theme="dark"] .msia-in button{background:#00A8E0;color:#002D72}
.msia-note{font-size:.7rem;font-weight:300;padding:0 12px 10px;background:var(--bg);color:var(--tx);opacity:.85}
`;
  const ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/><path d="M8.5 10.5h7M8.5 13.5h4.5"/></svg>';

  const esc = s => s.replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  function link(text, href) {
    let u; try { u = href.startsWith("/") ? new URL(href.slice(1), BASE) : new URL(href); } catch (e) { return esc(text); }
    if (!/^https?:$/.test(u.protocol) && u.protocol !== "mailto:" && u.protocol !== "tel:") return esc(text);
    const ext = u.origin !== location.origin && /^https?:$/.test(u.protocol);
    return `<a href="${esc(u.href)}"${ext ? ' target="_blank" rel="noopener"' : ""}>${text}</a>`;
  }
  function inline(s) {
    s = esc(s);
    s = s.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, t, h) => link(t, h.replace(/&amp;/g, "&")));
    s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>");
    s = s.replace(/(^|[\s(])((?:[\w.+-]+)@(?:[\w-]+\.)+[a-z]{2,})/gi, (m, p, e) => p + `<a href="mailto:${e}">${e}</a>`);
    return s;
  }
  function md(text) {
    const lines = text.replace(/\r/g, "").split("\n"); let html = "", list = null, para = [];
    const flush = () => { if (para.length) { html += "<p>" + inline(para.join(" ")) + "</p>"; para = []; } };
    const close = () => { if (list) { html += `</${list}>`; list = null; } };
    for (const raw of lines) {
      const l = raw.trim(), ol = l.match(/^\d+[.)]\s+(.*)/), ul = l.match(/^[-*•]\s+(.*)/), h = l.match(/^#{1,4}\s+(.*)/);
      if (ol || ul) { flush(); const t = ol ? "ol" : "ul"; if (list !== t) { close(); html += `<${t}>`; list = t; } html += "<li>" + inline((ol || ul)[1]) + "</li>"; }
      else if (!l) { flush(); close(); }
      else if (h) { flush(); close(); html += "<p><strong>" + inline(h[1]) + "</strong></p>"; }
      else { close(); para.push(l); }
    }
    flush(); close(); return html;
  }

  function context() {
    const c = { app: APP };
    try {
      if (typeof state !== "undefined" && typeof KB !== "undefined") {
        const L = KB.lines.find(l => l.id === state.line);
        if (L) {
          const d = state.defect && L.defects.find(x => x.id === state.defect);
          if (d) c.symptom = d.name;
          const m = state.model && (L.models || []).find(x => x.id === state.model);
          c.model = (KB.lines.length > 1 ? L.name + " " : "") + (m ? m.name : "");
        }
      }
    } catch (e) {}
    return c;
  }
  const SUGGEST = {
    "": ["My tipped part has flash", "Braid is bunching at high PPI", "HBLT gives a false burst", "Who do I contact for service?"],
    "tip-forming": ["Flash on the tip", "Tip not completely formed", "Tube is stuck in the die"],
    "braiding": ["Frequent wire breaks", "PPI keeps shifting", "Braid jumps over the cone"],
    "bwtec-2711": ["Tube breaks during necking", "Slug length is irregular", "What does a warning on the HMI mean?"],
    "hblt": ["Excessive burping (clicking)", "False burst reported", "Volume correction fails"],
  };

  let history = [];
  try { history = JSON.parse(sessionStorage.getItem(STORE) || "[]"); } catch (e) {}
  const save = () => { try { sessionStorage.setItem(STORE, JSON.stringify(history.slice(-24))); } catch (e) {} };

  function build() {
    const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
    const root = document.createElement("div"); root.className = "msia";
    root.innerHTML = `
<button class="msia-fab" type="button" aria-haspopup="dialog">${ICON}<span>Ask the assistant</span></button>
<section class="msia-panel" role="dialog" aria-label="Machine Solutions Assistant" hidden>
  <div class="msia-head"><img src="${new URL("brand/ms-symbol.svg", BASE).href}" alt="">
    <div><b>Machine Solutions Assistant</b><small>AI help from our troubleshooting guides</small></div><div class="sp"></div>
    <button type="button" data-a="new" title="New conversation">New</button>
    <button type="button" data-a="close" aria-label="Close">✕</button></div>
  <div class="msia-log" aria-live="polite"></div>
  <div class="msia-chips"></div>
  <form class="msia-in"><textarea rows="1" placeholder="Describe the problem…" aria-label="Your question" maxlength="2000"></textarea><button type="submit">Send</button></form>
  <div class="msia-note">AI assistant — it can make mistakes. Follow your operator manual and site safety procedures. Don't share confidential information.</div>
</section>`;
    document.body.appendChild(root);
    const $ = s => root.querySelector(s), fab = $(".msia-fab"), panel = $(".msia-panel"), log = $(".msia-log"),
      chips = $(".msia-chips"), form = $("form"), ta = $("textarea"), send = $(".msia-in button");

    function add(role, text, cls) {
      const d = document.createElement("div"); d.className = `msia-m ${role === "user" ? "u" : "a"}${cls ? " " + cls : ""}`;
      if (role === "user") d.textContent = text; else d.innerHTML = md(text);
      log.appendChild(d); log.scrollTop = log.scrollHeight; return d;
    }
    function renderChips() {
      chips.innerHTML = ""; const c = context(), list = [];
      if (c.symptom) list.push(`Help me with: ${c.symptom}`);
      if (history.length < 2) list.push(...(SUGGEST[APP] || SUGGEST[""]));
      list.slice(0, 4).forEach(t => { const b = document.createElement("button"); b.type = "button"; b.textContent = t; b.onclick = () => ask(t); chips.appendChild(b); });
    }
    function paint() {
      log.innerHTML = ""; add("assistant", WELCOME);
      history.forEach(m => add(m.role, m.content)); renderChips();
    }
    async function ask(q) {
      q = q.trim(); if (!q || send.disabled) return;
      if (!navigator.onLine) { add("assistant", "You're offline. The troubleshooters on this site still work offline, but the assistant needs a connection.", "err"); return; }
      add("user", q); history.push({ role: "user", content: q }); save(); ta.value = ""; chips.innerHTML = "";
      send.disabled = true; const t = add("assistant", ""); t.innerHTML = '<span class="msia-typing"><i></i><i></i><i></i></span>';
      try {
        const r = await fetch(ENDPOINT, { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: history.slice(-12), context: context() }) });
        const j = await r.json().catch(() => ({}));
        if (!r.ok || !j.reply) throw new Error(j.error || "The assistant is unavailable right now.");
        t.innerHTML = md(j.reply); history.push({ role: "assistant", content: j.reply }); save();
      } catch (e) {
        t.classList.add("err"); t.innerHTML = md((e.message || "Something went wrong.") + " You can also email service@machinesolutions.com.");
        history.pop(); save();
      } finally { send.disabled = false; log.scrollTop = log.scrollHeight; renderChips(); }
    }
    fab.onclick = () => { panel.hidden = false; fab.hidden = true; paint(); setTimeout(() => ta.focus(), 50); };
    root.addEventListener("click", e => {
      const a = e.target.closest("[data-a]"); if (!a) return;
      if (a.dataset.a === "close") { panel.hidden = true; fab.hidden = false; fab.focus(); }
      if (a.dataset.a === "new") { history = []; save(); paint(); ta.focus(); }
    });
    document.addEventListener("keydown", e => { if (e.key === "Escape" && !panel.hidden) { panel.hidden = true; fab.hidden = false; } });
    form.addEventListener("submit", e => { e.preventDefault(); ask(ta.value); });
    ta.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask(ta.value); } });
    ta.addEventListener("input", () => { ta.style.height = "auto"; ta.style.height = Math.min(ta.scrollHeight, 120) + "px"; });

    // keep the button clear of the app's "install" banner
    const bar = document.getElementById("pwabar");
    const lift = () => root.style.setProperty("--msia-lift", bar && !bar.hidden ? (bar.offsetHeight + 12) + "px" : "0px");
    if (bar) new MutationObserver(lift).observe(bar, { attributes: true, attributeFilter: ["hidden"] });
    lift();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build); else build();
})();
