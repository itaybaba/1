// shared helpers for the reels. Each page builds window.tl (paused) and window.DURATION.
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
function logo(cls = "mark") {
  return `<svg class="${cls}" viewBox="0 0 942 280"><path fill-rule="evenodd" d="${window.LOGO_D}"/></svg>`;
}
function logoSquare(size = 300) {
  return `<div class="logo-sq" style="width:${size}px;height:${size}px">${logo("")}</div>`;
}
// split "[data-k]" elements into masked words; "|" = line break, "*word" = bold, "~word" = thin
function kinetic(root = document) {
  $$("[data-k]", root).forEach((el) => {
    const raw = el.getAttribute("data-k");
    el.innerHTML = raw
      .split("|")
      .map((line) =>
        line
          .trim()
          .split(/\s+/)
          .map((w) => {
            let cls = "";
            if (w.startsWith("*")) { cls = "b"; w = w.slice(1); }
            if (w.startsWith("~")) { cls = "t"; w = w.slice(1); }
            const dot = w.endsWith("■") ? '<span class="sq"></span>' : "";
            w = w.replace("■", "");
            return `<span class="m"><span class="w ${cls}">${w}${dot}</span></span>`;
          })
          .join(" ")
      )
      .join("<br>");
  });
}
function uline() {
  return `<svg class="uline" viewBox="0 0 300 20" preserveAspectRatio="none"><path pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="M296 9 C 222 3, 92 5, 4 13"/></svg>`;
}
async function icon(name) {
  const r = await fetch(`node_modules/lucide-static/icons/${name}.svg`);
  return (await r.text()).replace(/<!--[\s\S]*?-->/g, "");
}
function showScene(tl, id, start, end) {
  tl.set(id, { autoAlpha: 1 }, start);
  if (end != null) tl.set(id, { autoAlpha: 0 }, end);
}
const rise = (tl, el, t, o = {}) =>
  tl.from($$(".w", typeof el === "string" ? $(el) : el), Object.assign({ yPercent: 115, duration: 0.7, ease: "expo.out", stagger: 0.08 }, o), t);
const drawLine = (tl, el, t, d = 0.6) => (tl.set($$(".uline", typeof el === "string" ? $(el) : el), { autoAlpha: 1 }, t), tl.to($$(".uline path", typeof el === "string" ? $(el) : el), { strokeDashoffset: 0, duration: d, ease: "power2.out" }, t));
function counter(tl, el, from, to, t, d, fmt = (v) => Math.round(v)) {
  const o = { v: from };
  const node = typeof el === "string" ? $(el) : el;
  node.textContent = fmt(from);
  tl.to(o, { v: to, duration: d, ease: "power2.out", onUpdate: () => (node.textContent = fmt(o.v)) }, t);
}
window.seek = (t) => { window.tl.seek(t, false); return true; };
// shared end card: logo, offer line, CTA pill, tagline
async function buildCTA(sel) {
  $(sel).innerHTML = `<div class="center" style="padding-bottom:120px">
    <div class="cta-lg">${logoSquare(330)}</div>
    <div class="cta-line" data-k="*מינוי *ללא *התחייבות|~במחיר ~מוזל"></div>
    <div style="margin-top:80px" class="cta-pw"><span class="pill"><i class="ring"></i>הקליקו לפרטים והצטרפות <span class="cta-arr">${await icon("arrow-left")}</span></span></div>
    <p class="cta-tag">One life. Live it well<span class="sq"></span></p></div>`;
}
function animCTA(tl, sel, C) {
  const q = (s) => $(sel + " " + s);
  tl.from(q(".cta-lg"), { scale: 0, rotate: -12, duration: 0.7, ease: "back.out(1.7)" }, C + 0.05);
  tl.from(q(".cta-lg svg"), { autoAlpha: 0, y: 20, duration: 0.5 }, C + 0.4);
  rise(tl, q(".cta-line"), C + 0.45, { stagger: 0.07 });
  tl.from(q(".cta-pw"), { y: 80, autoAlpha: 0, duration: 0.6, ease: "back.out(1.6)" }, C + 0.9);
  tl.fromTo(q(".ring"), { scale: 1, autoAlpha: 0.8 }, { scale: 1.35, autoAlpha: 0, duration: 1.0, repeat: 2, ease: "power2.out" }, C + 1.4);
  tl.to(q(".cta-arr"), { x: -14, duration: 0.4, repeat: 5, yoyo: true, ease: "sine.inOut" }, C + 1.4);
  tl.from(q(".cta-tag"), { autoAlpha: 0, y: 20, duration: 0.6 }, C + 1.3);
  tl.to(q(".cta-lg"), { y: -10, duration: 1, repeat: 1, yoyo: true, ease: "sine.inOut" }, C + 1.0);
}
