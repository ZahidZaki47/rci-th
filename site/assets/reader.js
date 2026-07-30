const $ = (sel) => document.querySelector(sel);
const pad = (n) => String(n).padStart(3, "0");
const norm = (s) => s.toLowerCase().replace(/[^\p{L}\p{N}\s]/gu, " ");
const esc = (s) => s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[c]);

const el = {
  img: $("#page-img"),
  page: $("#page"),
  input: $("#page-input"),
  total: $("#page-total"),
  prev: $("#prev"),
  next: $("#next"),
  edgePrev: $("#edge-prev"),
  edgeNext: $("#edge-next"),
  panel: $("#searchpanel"),
  scrim: $("#scrim"),
  q: $("#q"),
  status: $("#search-status"),
  results: $("#results"),
  download: $("#download"),
};

const state = { page: 1, total: 1, query: "", texts: null, boxes: new Map(), hits: [] };

/* ---------- routing ---------- */

function readHash() {
  const h = new URLSearchParams(location.hash.slice(1));
  return { p: parseInt(h.get("p"), 10) || 1, q: h.get("q") || "" };
}

function writeHash(replace) {
  const h = new URLSearchParams();
  h.set("p", state.page);
  if (state.query) h.set("q", state.query);
  const url = "#" + h.toString();
  if (replace) history.replaceState(null, "", url);
  else history.pushState(null, "", url);
}

/* ---------- pages ---------- */

function clamp(n) {
  return Math.min(Math.max(n, 1), state.total);
}

function preload(n) {
  if (n >= 1 && n <= state.total) new Image().src = `pages/${pad(n)}.webp`;
}

async function show(n, { push = true } = {}) {
  state.page = clamp(n);
  el.img.src = `pages/${pad(state.page)}.webp`;
  el.img.alt = `Muka surat ${state.page} daripada ${state.total}`;
  el.input.value = state.page;
  el.prev.disabled = el.edgePrev.disabled = state.page === 1;
  el.next.disabled = el.edgeNext.disabled = state.page === state.total;
  writeHash(!push);
  markCurrentResult();
  preload(state.page + 1);
  preload(state.page - 1);
  await paintHighlights();
}

/* ---------- highlights ---------- */

async function loadBoxes(n) {
  if (!state.boxes.has(n)) {
    const r = await fetch(`data/words/${pad(n)}.json`);
    state.boxes.set(n, r.ok ? await r.json() : []);
  }
  return state.boxes.get(n);
}

async function paintHighlights() {
  el.page.querySelectorAll("mark").forEach((m) => m.remove());
  const terms = norm(state.query).split(/\s+/).filter(Boolean);
  if (!terms.length) return;
  const page = state.page;
  const boxes = await loadBoxes(page);
  if (page !== state.page) return; // navigated away while fetching
  const frag = document.createDocumentFragment();
  for (const [x, y, w, h, word] of boxes) {
    const nw = norm(word);
    if (!terms.some((t) => nw.includes(t))) continue;
    const m = document.createElement("mark");
    m.style.cssText = `left:${x * 100}%;top:${y * 100}%;width:${w * 100}%;height:${h * 100}%`;
    frag.append(m);
  }
  el.page.append(frag);
}

/* ---------- search ---------- */

async function texts() {
  if (!state.texts) {
    el.status.textContent = "Memuatkan indeks carian…";
    const r = await fetch("data/pages.json");
    state.raw = await r.json();
    state.texts = state.raw.map(norm);
  }
  return state.texts;
}

function snippet(raw, terms) {
  const low = norm(raw);
  let at = -1;
  for (const t of terms) {
    const i = low.indexOf(t);
    if (i !== -1 && (at === -1 || i < at)) at = i;
  }
  if (at === -1) at = 0;
  const from = Math.max(0, at - 70);
  const cut = raw.slice(from, from + 200);
  let html = esc(cut);
  for (const t of terms) {
    html = html.replace(new RegExp(`(${t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi"), "<mark>$1</mark>");
  }
  return (from > 0 ? "…" : "") + html + "…";
}

async function runSearch() {
  const q = el.q.value.trim();
  state.query = q;
  el.results.innerHTML = "";
  state.hits = [];
  if (q.length < 2) {
    el.status.textContent = "Taip sekurang-kurangnya 2 aksara.";
    writeHash(true);
    await paintHighlights();
    return;
  }
  const all = await texts();
  const terms = norm(q).split(/\s+/).filter(Boolean);
  const raw = state.raw;
  const hits = [];
  all.forEach((t, i) => {
    if (terms.every((term) => t.includes(term))) {
      const count = terms.reduce((acc, term) => acc + t.split(term).length - 1, 0);
      hits.push({ page: i + 1, count, text: raw[i] });
    }
  });
  hits.sort((a, b) => b.count - a.count || a.page - b.page);
  state.hits = hits;

  el.status.textContent = hits.length
    ? `${hits.reduce((a, h) => a + h.count, 0)} padanan pada ${hits.length} muka surat`
    : `Tiada padanan untuk “${q}”.`;

  const frag = document.createDocumentFragment();
  for (const h of hits) {
    const li = document.createElement("li");
    const b = document.createElement("button");
    b.type = "button";
    b.dataset.page = h.page;
    b.innerHTML = `<span class="p">Muka surat ${h.page} · ${h.count} padanan</span><span class="s">${snippet(h.text, terms)}</span>`;
    b.addEventListener("click", () => {
      show(h.page);
      if (window.matchMedia("(max-width: 52rem)").matches) toggleSearch(false);
    });
    li.append(b);
    frag.append(li);
  }
  el.results.append(frag);
  writeHash(true);
  markCurrentResult();
  await paintHighlights();
}

function markCurrentResult() {
  el.results.querySelectorAll("button").forEach((b) => {
    b.setAttribute("aria-current", String(Number(b.dataset.page) === state.page));
  });
}

function toggleSearch(open) {
  const next = open ?? el.panel.dataset.open !== "true";
  el.panel.dataset.open = String(next);
  el.scrim.dataset.open = String(next);
  el.panel.setAttribute("aria-hidden", String(!next));
  $("#search-toggle").setAttribute("aria-expanded", String(next));
  if (next) el.q.focus();
}

/* ---------- boot ---------- */

async function init() {
  const manifest = await (await fetch("data/manifest.json")).json();
  state.total = manifest.pages;
  el.total.textContent = manifest.pages;
  el.input.max = manifest.pages;
  el.page.style.setProperty("--page-aspect", String(1 / manifest.aspect));

  el.download.href = window.RCI.pdfUrl;

  const { p, q } = readHash();
  if (q) {
    el.q.value = q;
    toggleSearch(true);
  }
  await show(p, { push: false });
  if (q) await runSearch();

  el.prev.onclick = el.edgePrev.onclick = () => show(state.page - 1);
  el.next.onclick = el.edgeNext.onclick = () => show(state.page + 1);
  el.input.addEventListener("change", () => show(parseInt(el.input.value, 10) || 1));
  $("#search-toggle").onclick = () => toggleSearch();
  $("#search-close").onclick = () => toggleSearch(false);
  el.scrim.onclick = () => toggleSearch(false);

  let t;
  el.q.addEventListener("input", () => {
    clearTimeout(t);
    t = setTimeout(runSearch, 200);
  });

  addEventListener("hashchange", () => {
    const { p } = readHash();
    if (p !== state.page) show(p, { push: false });
  });

  addEventListener("keydown", (e) => {
    if (e.target.matches("input")) {
      if (e.key === "Escape") e.target.blur();
      return;
    }
    if (e.key === "ArrowRight" || e.key === "PageDown") show(state.page + 1);
    else if (e.key === "ArrowLeft" || e.key === "PageUp") show(state.page - 1);
    else if (e.key === "Home") show(1);
    else if (e.key === "End") show(state.total);
    else if (e.key === "/") {
      e.preventDefault();
      toggleSearch(true);
    } else if (e.key === "Escape") toggleSearch(false);
  });

  let x0 = null;
  el.page.addEventListener("touchstart", (e) => (x0 = e.touches[0].clientX), { passive: true });
  el.page.addEventListener(
    "touchend",
    (e) => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 60) show(state.page + (dx < 0 ? 1 : -1));
      x0 = null;
    },
    { passive: true }
  );
}

init();
