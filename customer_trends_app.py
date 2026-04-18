"""
customer_trends_app.py: Dashboard Prototype Presentation Layer

This module serves as the primary presentation layer for the buyer's team.
It provides a local HTTP server rendering a dynamic, interactive dashboard (HTML/CSS/JS)
to visualize compiled scores, filtering constraints, and actionable opportunity cards.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from combined_trends import build_combined_trends_payload


HOST = "127.0.0.1"
PORT = 8000


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Trend Opportunities</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #faf7f2;
      --panel: #ffffff;
      --ink: #1a1410;
      --muted: #7a6e64;
      --soft: #b5a89a;
      --line: #e8e0d5;
      --accent: #d96c2d;
      --accent-light: #fdf0e8;
      --green: #1f7a6b;
      --green-light: #eaf4f2;
      --red: #a43c2f;
      --red-light: #faecea;
      --shadow-sm: 0 2px 8px rgba(30,20,10,0.06);
      --shadow-md: 0 8px 32px rgba(30,20,10,0.10);
      --shadow-lg: 0 20px 60px rgba(30,20,10,0.13);
      --radius: 20px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Lato', sans-serif;
      background: var(--bg);
      color: var(--ink);
      min-height: 100vh;
    }

    /* ── TOP BAR ── */
    .topbar {
      background: var(--ink);
      color: #fff;
      padding: 12px 40px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.78rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }
    .topbar-brand {
      font-family: 'Playfair Display', serif;
      font-size: 1.1rem;
      letter-spacing: 0.04em;
      text-transform: none;
      font-weight: 700;
    }
    .topbar-tag {
      background: var(--accent);
      color: #fff;
      padding: 4px 12px;
      border-radius: 99px;
      font-size: 0.72rem;
      letter-spacing: 0.1em;
    }

    /* ── HERO ── */
    .hero {
      background: linear-gradient(120deg, #1a1410 60%, #2e1f0f 100%);
      color: #fff;
      padding: 72px 40px 64px;
      position: relative;
      overflow: hidden;
    }
    .hero::before {
      content: "";
      position: absolute;
      top: -80px; right: -80px;
      width: 480px; height: 480px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(217,108,45,0.22), transparent 70%);
    }
    .hero::after {
      content: "";
      position: absolute;
      bottom: -60px; left: 200px;
      width: 300px; height: 300px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(31,122,107,0.18), transparent 70%);
    }
    .hero-inner {
      position: relative;
      max-width: 1200px;
      margin: 0 auto;
    }
    .hero-eyebrow {
      display: inline-block;
      background: var(--accent);
      color: #fff;
      padding: 5px 14px;
      border-radius: 99px;
      font-size: 0.75rem;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      margin-bottom: 24px;
      font-weight: 700;
    }
    .hero h1 {
      font-family: 'Playfair Display', serif;
      font-size: clamp(2.6rem, 5vw, 5rem);
      font-weight: 900;
      line-height: 1.0;
      max-width: 700px;
      margin-bottom: 20px;
    }
    .hero h1 em {
      color: var(--accent);
      font-style: normal;
    }
    .hero-sub {
      font-size: 1.05rem;
      color: rgba(255,255,255,0.65);
      max-width: 560px;
      line-height: 1.7;
      margin-bottom: 48px;
    }

    /* ── STAT CARDS ── */
    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 14px;
      max-width: 720px;
    }
    .stat {
      background: rgba(255,255,255,0.07);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 16px;
      padding: 18px 20px;
      backdrop-filter: blur(8px);
    }
    .stat-label {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: rgba(255,255,255,0.5);
      margin-bottom: 6px;
    }
    .stat-value {
      font-family: 'Playfair Display', serif;
      font-size: 2.2rem;
      font-weight: 700;
      color: #fff;
    }

    /* ── MAIN LAYOUT ── */
    .shell {
      max-width: 1280px;
      margin: 0 auto;
      padding: 32px 24px 64px;
      display: grid;
      grid-template-columns: 280px 1fr;
      gap: 24px;
      align-items: start;
    }

    /* ── SIDEBAR ── */
    .sidebar {
      position: sticky;
      top: 24px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow-sm);
      padding: 28px 24px;
    }
    .sidebar-title {
      font-family: 'Playfair Display', serif;
      font-size: 1.2rem;
      font-weight: 700;
      margin-bottom: 6px;
    }
    .sidebar-sub {
      font-size: 0.82rem;
      color: var(--muted);
      margin-bottom: 24px;
      line-height: 1.5;
    }
    .field {
      margin-bottom: 18px;
    }
    .field label {
      display: block;
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--muted);
      margin-bottom: 7px;
      font-weight: 700;
    }
    .field input,
    .field select {
      width: 100%;
      padding: 11px 14px;
      border-radius: 12px;
      border: 1.5px solid var(--line);
      background: var(--bg);
      color: var(--ink);
      font: inherit;
      font-size: 0.92rem;
      transition: border-color 0.2s;
      outline: none;
    }
    .field input:focus,
    .field select:focus {
      border-color: var(--accent);
    }
    .toggle-row {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 14px;
      background: var(--accent-light);
      border: 1.5px solid rgba(217,108,45,0.2);
      border-radius: 12px;
      cursor: pointer;
    }
    .toggle-row span {
      font-size: 0.86rem;
      color: var(--ink);
      line-height: 1.4;
    }
    .toggle-row input[type=checkbox] {
      accent-color: var(--accent);
      width: 16px;
      height: 16px;
      flex-shrink: 0;
    }
    .divider {
      height: 1px;
      background: var(--line);
      margin: 20px 0;
    }
    .legend {
      font-size: 0.78rem;
      color: var(--muted);
      line-height: 1.6;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
    }
    .legend-dot {
      width: 10px; height: 10px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    /* ── MAIN CONTENT ── */
    .main {}
    .main-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 18px;
      flex-wrap: wrap;
      gap: 8px;
    }
    .main-title {
      font-family: 'Playfair Display', serif;
      font-size: 1.4rem;
      font-weight: 700;
    }
    .result-count {
      font-size: 0.84rem;
      color: var(--muted);
    }

    /* ── ERROR ── */
    .error {
      padding: 14px 18px;
      border-radius: 12px;
      background: var(--red-light);
      border: 1px solid rgba(164,60,47,0.2);
      color: var(--red);
      font-size: 0.88rem;
      margin-bottom: 16px;
    }

    /* ── CARD GRID ── */
    .card-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 16px;
    }

    .opportunity-card {
      background: var(--panel);
      border: 1.5px solid var(--line);
      border-radius: 18px;
      padding: 22px;
      cursor: pointer;
      transition: box-shadow 0.2s, border-color 0.2s, transform 0.15s;
      position: relative;
      overflow: hidden;
    }
    .opportunity-card:hover {
      box-shadow: var(--shadow-md);
      border-color: var(--accent);
      transform: translateY(-2px);
    }
    .opportunity-card.selected {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(217,108,45,0.15), var(--shadow-md);
    }
    .opportunity-card.pass::before {
      content: "";
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--green), #2ab09c);
    }
    .opportunity-card.fail::before {
      content: "";
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 3px;
      background: var(--line);
    }

    .card-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 14px;
      gap: 10px;
    }
    .card-term {
      font-family: 'Playfair Display', serif;
      font-size: 1.2rem;
      font-weight: 700;
      line-height: 1.2;
      flex: 1;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 5px 10px;
      border-radius: 99px;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      white-space: nowrap;
      flex-shrink: 0;
    }
    .badge.pass {
      background: var(--green-light);
      color: var(--green);
    }
    .badge.fail {
      background: var(--line);
      color: var(--muted);
    }
    .badge::before {
      content: "";
      width: 6px; height: 6px;
      border-radius: 50%;
      background: currentColor;
    }

    .card-meta {
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }
    .tag {
      padding: 4px 10px;
      background: var(--bg);
      border: 1px solid var(--line);
      border-radius: 99px;
      font-size: 0.75rem;
      color: var(--muted);
    }

    .card-scores {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }
    .score-box {
      background: var(--bg);
      border-radius: 12px;
      padding: 12px;
      text-align: center;
    }
    .score-label {
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--muted);
      margin-bottom: 4px;
    }
    .score-value {
      font-family: 'Playfair Display', serif;
      font-size: 1.5rem;
      font-weight: 700;
    }
    .score-value.high { color: var(--green); }
    .score-value.mid { color: var(--accent); }
    .score-value.low { color: var(--muted); }
    .score-value.na { color: var(--soft); font-size: 1rem; }

    .card-source {
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
      font-size: 0.76rem;
      color: var(--muted);
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .source-dot {
      width: 7px; height: 7px;
      border-radius: 50%;
      background: var(--soft);
    }
    .source-dot.active { background: var(--green); }

    /* ── DETAIL DRAWER ── */
    .detail-drawer {
      background: var(--panel);
      border: 1.5px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow-lg);
      margin-top: 24px;
      overflow: hidden;
      animation: slideUp 0.25s ease;
    }
    @keyframes slideUp {
      from { opacity: 0; transform: translateY(12px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .drawer-header {
      background: linear-gradient(90deg, var(--ink), #2e1f0f);
      color: #fff;
      padding: 24px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }
    .drawer-term {
      font-family: 'Playfair Display', serif;
      font-size: 1.6rem;
      font-weight: 700;
    }
    .drawer-close {
      background: rgba(255,255,255,0.12);
      border: none;
      color: #fff;
      border-radius: 99px;
      width: 34px; height: 34px;
      font-size: 1.1rem;
      cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      transition: background 0.2s;
    }
    .drawer-close:hover { background: rgba(255,255,255,0.22); }
    .drawer-body {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 0;
    }
    .drawer-section {
      padding: 24px 28px;
      border-right: 1px solid var(--line);
    }
    .drawer-section:last-child { border-right: none; }
    .drawer-section-title {
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--muted);
      font-weight: 700;
      margin-bottom: 16px;
    }
    .drawer-row {
      display: flex;
      flex-direction: column;
      margin-bottom: 14px;
    }
    .drawer-row-label {
      font-size: 0.78rem;
      color: var(--muted);
      margin-bottom: 2px;
    }
    .drawer-row-value {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--ink);
    }
    .raw-toggle {
      margin: 0 28px 24px;
      background: none;
      border: 1.5px solid var(--line);
      border-radius: 10px;
      padding: 8px 16px;
      font: inherit;
      font-size: 0.82rem;
      color: var(--muted);
      cursor: pointer;
      transition: border-color 0.2s;
    }
    .raw-toggle:hover { border-color: var(--accent); color: var(--accent); }
    pre {
      margin: 0 28px 24px;
      padding: 18px;
      border-radius: 14px;
      background: #1e1a17;
      color: #f6e9d2;
      overflow: auto;
      font-size: 0.8rem;
      line-height: 1.5;
    }

    /* ── EMPTY ── */
    .empty {
      grid-column: 1 / -1;
      text-align: center;
      padding: 64px 20px;
      color: var(--muted);
    }
    .empty-icon { font-size: 3rem; margin-bottom: 12px; }
    .empty h3 { font-family: 'Playfair Display', serif; font-size: 1.4rem; margin-bottom: 8px; color: var(--ink); }

    /* ── SORT BAR ── */
    .sort-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .sort-label {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--muted);
      font-weight: 700;
      white-space: nowrap;
    }
    .sort-btn {
      padding: 6px 14px;
      border-radius: 99px;
      border: 1.5px solid var(--line);
      background: var(--panel);
      color: var(--muted);
      font: inherit;
      font-size: 0.8rem;
      cursor: pointer;
      transition: border-color 0.18s, color 0.18s, background 0.18s;
      white-space: nowrap;
    }
    .sort-btn:hover {
      border-color: var(--accent);
      color: var(--accent);
    }
    .sort-btn.active {
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
      font-weight: 700;
    }

    @media (max-width: 900px) {
      .shell { grid-template-columns: 1fr; }
      .sidebar { position: static; }
      .drawer-body { grid-template-columns: 1fr; }
      .drawer-section { border-right: none; border-bottom: 1px solid var(--line); }
      .card-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

  <div class="topbar">
    <span class="topbar-brand">Prince of Peace</span>
    <span>Opportunity Intelligence</span>
    <span class="topbar-tag">Live Data</span>
  </div>

  <div class="hero">
    <div class="hero-inner">
      <span class="hero-eyebrow">Market Intelligence</span>
      <h1>What's <em>growing</em> right now</h1>
      <p class="hero-sub">
        Real consumer demand signals from Google and Amazon — filtered for food and wellness opportunities you can act on today.
      </p>
      <div class="stats" id="stats"></div>
    </div>
  </div>

  <div class="shell">

    <aside class="sidebar">
      <div class="sidebar-title">Find opportunities</div>
      <p class="sidebar-sub">Narrow results by what matters to your buying decision.</p>

      <div class="field">
        <label for="search">Keyword</label>
        <input id="search" type="text" placeholder="e.g. matcha, probiotic…" />
      </div>
      <div class="field">
        <label for="category">Category</label>
        <select id="category">
          <option value="">All categories</option>
        </select>
      </div>
      <div class="field">
        <label for="format">Product type</label>
        <select id="format">
          <option value="">All types</option>
        </select>
      </div>
      <div class="field">
        <label for="source">Signal source</label>
        <select id="source">
          <option value="">All signals</option>
          <option value="both">Google + Amazon</option>
          <option value="google">Google only</option>
          <option value="amazon">Amazon only</option>
        </select>
      </div>
      <label class="toggle-row">
        <input id="passingOnly" type="checkbox" />
        <span>Show only <strong>ready opportunities</strong> — trends that meet all business criteria</span>
      </label>

      <div class="divider"></div>
      <div class="legend">
        <div class="legend-item"><span class="legend-dot" style="background:var(--green)"></span> Ready opportunity</div>
        <div class="legend-item"><span class="legend-dot" style="background:var(--soft)"></span> Monitoring / not yet ready</div>
        <div class="legend-item"><span class="legend-dot" style="background:var(--accent)"></span> Score 70+ = strong signal</div>
      </div>
    </aside>

    <main class="main">
      <div class="main-header">
        <div class="main-title">Trend Opportunities</div>
        <div class="result-count" id="resultCount">Loading…</div>
      </div>
      <div class="sort-bar" style="margin-bottom:18px;">
        <span class="sort-label">Sort by</span>
        <button class="sort-btn active" data-sort="default">Featured</button>
        <button class="sort-btn" data-sort="alpha-asc">A → Z</button>
        <button class="sort-btn" data-sort="alpha-desc">Z → A</button>
        <button class="sort-btn" data-sort="google-desc">Search demand ↑</button>
        <button class="sort-btn" data-sort="google-asc">Search demand ↓</button>
        <button class="sort-btn" data-sort="amazon-desc">Shopping demand ↑</button>
        <button class="sort-btn" data-sort="amazon-asc">Shopping demand ↓</button>
        <button class="sort-btn" data-sort="ready-first">Ready first</button>
      </div>
      <div id="errorBox" class="error" hidden></div>
      <div class="card-grid" id="cardGrid"></div>
      <div id="detailDrawer"></div>
    </main>

  </div>

  <script>
    const state = {
      payload: null,
      filteredRecords: [],
      selectedTerm: null,
      showRaw: false,
      sortKey: "default",
    };

    const refs = {
      stats:       document.getElementById("stats"),
      resultCount: document.getElementById("resultCount"),
      cardGrid:    document.getElementById("cardGrid"),
      detailDrawer:document.getElementById("detailDrawer"),
      errorBox:    document.getElementById("errorBox"),
      search:      document.getElementById("search"),
      category:    document.getElementById("category"),
      format:      document.getElementById("format"),
      source:      document.getElementById("source"),
      passingOnly: document.getElementById("passingOnly"),
    };

    // Sort button wiring
    document.querySelectorAll(".sort-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        state.sortKey = btn.dataset.sort;
        document.querySelectorAll(".sort-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        applyFilters();
      });
    });

    function sourceLabel(record) {
      const hasGoogle = Boolean(record.google_trends);
      const hasAmazon = Boolean(record.amazon_trends);
      if (hasGoogle && hasAmazon) return "Google + Amazon";
      if (hasGoogle) return "Google only";
      if (hasAmazon) return "Amazon only";
      return "No source";
    }

    function scoreClass(val) {
      if (val === null || val === undefined) return "na";
      if (val >= 70) return "high";
      if (val >= 40) return "mid";
      return "low";
    }

    function buildStats(records) {
      const withGoogle = records.filter(r => r.google_trends).length;
      const withAmazon = records.filter(r => r.amazon_trends).length;
      const passing    = records.filter(r => r.business_filter?.passes).length;
      const items = [
        ["Trends tracked",      records.length],
        ["Google signals",      withGoogle],
        ["Amazon signals",      withAmazon],
        ["Ready opportunities", passing],
      ];
      refs.stats.innerHTML = items.map(([label, value]) => `
        <article class="stat">
          <div class="stat-label">${label}</div>
          <div class="stat-value">${value}</div>
        </article>
      `).join("");
    }

    function populateSelect(select, values, placeholder) {
      select.innerHTML = [`<option value="">${placeholder}</option>`]
        .concat(values.map(v => `<option value="${v}">${v}</option>`)).join("");
    }

    function initFilters(records) {
      const cats    = [...new Set(records.map(r => r.business_filter?.category).filter(Boolean))].sort();
      const formats = [...new Set(records.map(r => r.business_filter?.product_format).filter(Boolean))].sort();
      populateSelect(refs.category, cats, "All categories");
      populateSelect(refs.format, formats, "All types");
    }

    function matchesSource(record, value) {
      if (!value) return true;
      const g = Boolean(record.google_trends);
      const a = Boolean(record.amazon_trends);
      if (value === "both")   return g && a;
      if (value === "google") return g && !a;
      if (value === "amazon") return a && !g;
      return true;
    }

    function applyFilters() {
      if (!state.payload) return;
      const search      = refs.search.value.trim().toLowerCase();
      const category    = refs.category.value;
      const format      = refs.format.value;
      const source      = refs.source.value;
      const passingOnly = refs.passingOnly.checked;

      state.filteredRecords = state.payload.records.filter(r => {
        const term = (r.term || "").toLowerCase();
        return (!search      || term.includes(search))
            && (!category    || r.business_filter?.category === category)
            && (!format      || r.business_filter?.product_format === format)
            && (!passingOnly || r.business_filter?.passes)
            && matchesSource(r, source);
      });

      // Apply sort
      const getG = r => r.combined_signals?.google_opportunity_score ?? -1;
      const getA = r => r.combined_signals?.amazon_opportunity_score ?? -1;
      const sorts = {
        "default":      () => 0,
        "alpha-asc":    (a, b) => a.term.localeCompare(b.term),
        "alpha-desc":   (a, b) => b.term.localeCompare(a.term),
        "google-desc":  (a, b) => getG(b) - getG(a),
        "google-asc":   (a, b) => getG(a) - getG(b),
        "amazon-desc":  (a, b) => getA(b) - getA(a),
        "amazon-asc":   (a, b) => getA(a) - getA(b),
        "ready-first":  (a, b) => (b.business_filter?.passes ? 1 : 0) - (a.business_filter?.passes ? 1 : 0),
      };
      if (state.sortKey !== "default") {
        state.filteredRecords.sort(sorts[state.sortKey] || (() => 0));
      }

      renderCards();
      const sel = state.filteredRecords.find(r => r.term === state.selectedTerm);
      if (sel) renderDrawer(sel);
      else { state.selectedTerm = null; refs.detailDrawer.innerHTML = ""; }
    }

    function renderCards() {
      refs.resultCount.textContent = `${state.filteredRecords.length} result${state.filteredRecords.length === 1 ? "" : "s"}`;

      if (!state.filteredRecords.length) {
        refs.cardGrid.innerHTML = `
          <div class="empty">
            <div class="empty-icon">🔍</div>
            <h3>No results found</h3>
            <p>Try adjusting your filters above.</p>
          </div>`;
        return;
      }

      refs.cardGrid.innerHTML = state.filteredRecords.map(record => {
        const pass  = Boolean(record.business_filter?.passes);
        const gScore = record.combined_signals?.google_opportunity_score;
        const aScore = record.combined_signals?.amazon_opportunity_score;
        const isSelected = record.term === state.selectedTerm;
        const hasG = Boolean(record.google_trends);
        const hasA = Boolean(record.amazon_trends);

        return `
          <article class="opportunity-card ${pass ? "pass" : "fail"} ${isSelected ? "selected" : ""}" data-term="${record.term}">
            <div class="card-top">
              <div class="card-term">${record.term}</div>
              <span class="badge ${pass ? "pass" : "fail"}">${pass ? "Ready" : "Watching"}</span>
            </div>
            <div class="card-meta">
              ${record.business_filter?.category    ? `<span class="tag">${record.business_filter.category}</span>` : ""}
              ${record.business_filter?.product_format ? `<span class="tag">${record.business_filter.product_format}</span>` : ""}
            </div>
            <div class="card-scores">
              <div class="score-box">
                <div class="score-label">Search demand</div>
                <div class="score-value ${scoreClass(gScore)}">${gScore ?? "—"}</div>
              </div>
              <div class="score-box">
                <div class="score-label">Shopping demand</div>
                <div class="score-value ${scoreClass(aScore)}">${aScore ?? "—"}</div>
              </div>
            </div>
            <div class="card-source">
              <span class="source-dot ${hasG ? "active" : ""}"></span> Google
              &nbsp;
              <span class="source-dot ${hasA ? "active" : ""}"></span> Amazon
            </div>
          </article>`;
      }).join("");

      refs.cardGrid.querySelectorAll(".opportunity-card").forEach(card => {
        card.addEventListener("click", () => {
          const term = card.dataset.term;
          if (state.selectedTerm === term) {
            state.selectedTerm = null;
            refs.detailDrawer.innerHTML = "";
            card.classList.remove("selected");
          } else {
            state.selectedTerm = term;
            const record = state.filteredRecords.find(r => r.term === term);
            renderDrawer(record);
            refs.cardGrid.querySelectorAll(".opportunity-card").forEach(c => c.classList.remove("selected"));
            card.classList.add("selected");
            setTimeout(() => refs.detailDrawer.scrollIntoView({ behavior: "smooth", block: "nearest" }), 50);
          }
        });
      });
    }

    function renderDrawer(record) {
      state.showRaw = false;
      const pass   = Boolean(record.business_filter?.passes);
      const gScore = record.combined_signals?.google_opportunity_score;
      const aScore = record.combined_signals?.amazon_opportunity_score;

      refs.detailDrawer.innerHTML = `
        <div class="detail-drawer">
          <div class="drawer-header">
            <div>
              <div class="drawer-term">${record.term}</div>
              <span class="badge ${pass ? "pass" : "fail"}" style="margin-top:8px;display:inline-flex">${pass ? "Ready opportunity" : "Still watching"}</span>
            </div>
            <button class="drawer-close" id="drawerClose">✕</button>
          </div>
          <div class="drawer-body">
            <div class="drawer-section">
              <div class="drawer-section-title">At a glance</div>
              <div class="drawer-row">
                <span class="drawer-row-label">Category</span>
                <span class="drawer-row-value">${record.business_filter?.category || "Uncategorized"}</span>
              </div>
              <div class="drawer-row">
                <span class="drawer-row-label">Product type</span>
                <span class="drawer-row-value">${record.business_filter?.product_format || "Not specified"}</span>
              </div>
              <div class="drawer-row">
                <span class="drawer-row-label">Signal sources</span>
                <span class="drawer-row-value">${sourceLabel(record)}</span>
              </div>
            </div>
            <div class="drawer-section">
              <div class="drawer-section-title">Demand signals</div>
              <div class="drawer-row">
                <span class="drawer-row-label">Search demand (Google)</span>
                <span class="drawer-row-value" style="color:${gScore >= 70 ? "var(--green)" : gScore >= 40 ? "var(--accent)" : "var(--muted)"}">${gScore ?? "No data"}</span>
              </div>
              <div class="drawer-row">
                <span class="drawer-row-label">Shopping demand (Amazon)</span>
                <span class="drawer-row-value" style="color:${aScore >= 70 ? "var(--green)" : aScore >= 40 ? "var(--accent)" : "var(--muted)"}">${aScore ?? "No data"}</span>
              </div>
            </div>
            <div class="drawer-section">
              <div class="drawer-section-title">Business assessment</div>
              <div class="drawer-row">
                <span class="drawer-row-label">Status</span>
                <span class="drawer-row-value">${pass ? "✅ Meets all criteria" : "⏳ Criteria not yet met"}</span>
              </div>
            </div>
          </div>
          <button class="raw-toggle" id="rawToggle">Show raw data ↓</button>
          <pre id="rawPre" hidden>${JSON.stringify(record, null, 2)}</pre>
        </div>`;

      document.getElementById("drawerClose").addEventListener("click", () => {
        state.selectedTerm = null;
        refs.detailDrawer.innerHTML = "";
        refs.cardGrid.querySelectorAll(".opportunity-card").forEach(c => c.classList.remove("selected"));
      });
      document.getElementById("rawToggle").addEventListener("click", () => {
        const pre = document.getElementById("rawPre");
        const btn = document.getElementById("rawToggle");
        state.showRaw = !state.showRaw;
        pre.hidden = !state.showRaw;
        btn.textContent = state.showRaw ? "Hide raw data ↑" : "Show raw data ↓";
      });
    }

    async function loadData() {
      try {
        const response = await fetch("/api/trends");
        if (!response.ok) throw new Error(`Server returned ${response.status}`);
        state.payload = await response.json();

        const sourceErrors = state.payload.meta?.source_errors || {};
        const errorMessages = Object.entries(sourceErrors).map(([src, msg]) => `${src}: ${msg}`);
        if (errorMessages.length) {
          refs.errorBox.hidden = false;
          refs.errorBox.textContent = `Some data sources had issues — results may be incomplete. ${errorMessages.join(" | ")}`;
        }
        buildStats(state.payload.records);
        initFilters(state.payload.records);
        applyFilters();
      } catch (err) {
        refs.errorBox.hidden = false;
        refs.errorBox.textContent = `Couldn't load trend data: ${err.message}`;
        refs.resultCount.textContent = "0 results";
      }
    }

    [refs.search, refs.category, refs.format, refs.source, refs.passingOnly]
      .forEach(el => el.addEventListener("input", applyFilters));

    loadData();
  </script>
</body>
</html>
"""


class CustomerTrendsHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html, status=200):
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self._send_html(HTML_PAGE)
            return

        if parsed.path == "/api/trends":
            query = parse_qs(parsed.query)
            amazon_limit = query.get("amazon_max_keywords", ["10"])[0]
            use_temporary_demo_data = query.get("temporary_demo_data", ["1"])[0] == "1"

            try:
                payload = build_combined_trends_payload(
                    amazon_max_keywords=int(amazon_limit),
                    use_temporary_demo_data=use_temporary_demo_data,
                )
                self._send_json(payload)
            except Exception as exc:
                self._send_json(
                    {"error": str(exc), "records": [], "meta": {}, "source": "combined_trends"},
                    status=500,
                )
            return

        self._send_json({"error": "Not found"}, status=404)


def run_server():
    server = HTTPServer((HOST, PORT), CustomerTrendsHandler)
    print(f"Customer Trends running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()