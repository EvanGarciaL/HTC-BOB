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
  <title>Customer Trends</title>
  <style>
    :root {
      --bg: #f5efe3;
      --panel: rgba(255, 252, 246, 0.88);
      --panel-strong: #fffaf2;
      --ink: #1f1a14;
      --muted: #6f6558;
      --line: rgba(92, 78, 60, 0.16);
      --accent: #d96c2d;
      --accent-2: #1f7a6b;
      --accent-3: #a43c2f;
      --shadow: 0 20px 50px rgba(56, 36, 16, 0.12);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(217, 108, 45, 0.18), transparent 26%),
        radial-gradient(circle at top right, rgba(31, 122, 107, 0.18), transparent 22%),
        linear-gradient(180deg, #f6f0e6 0%, #efe5d4 100%);
      min-height: 100vh;
    }

    .shell {
      width: min(1280px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 24px 0 48px;
    }

    .hero {
      background: linear-gradient(135deg, rgba(255, 248, 240, 0.95), rgba(249, 240, 226, 0.82));
      border: 1px solid var(--line);
      border-radius: 28px;
      box-shadow: var(--shadow);
      overflow: hidden;
      position: relative;
      padding: 32px;
    }

    .hero::after {
      content: "";
      position: absolute;
      inset: auto -40px -40px auto;
      width: 220px;
      height: 220px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(217, 108, 45, 0.18), transparent 68%);
    }

    .eyebrow {
      margin: 0 0 12px;
      color: var(--accent-2);
      font-size: 0.85rem;
      letter-spacing: 0.16em;
      text-transform: uppercase;
    }

    h1 {
      margin: 0;
      font-size: clamp(2.3rem, 4vw, 4.4rem);
      line-height: 0.95;
      max-width: 9ch;
    }

    .hero p {
      max-width: 720px;
      font-size: 1rem;
      line-height: 1.6;
      color: var(--muted);
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin-top: 28px;
    }

    .stat {
      background: var(--panel-strong);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px 18px;
    }

    .stat-label {
      margin: 0 0 8px;
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }

    .stat-value {
      margin: 0;
      font-size: 1.9rem;
    }

    .layout {
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 18px;
      margin-top: 20px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(8px);
    }

    .controls {
      padding: 22px;
      position: sticky;
      top: 18px;
      height: fit-content;
    }

    .controls h2,
    .viewer h2,
    .viewer h3 {
      margin: 0 0 12px;
      font-size: 1rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .field {
      margin-bottom: 16px;
    }

    .field label {
      display: block;
      font-size: 0.84rem;
      margin-bottom: 6px;
      color: var(--muted);
    }

    .field input,
    .field select {
      width: 100%;
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: #fffdf8;
      color: var(--ink);
      font: inherit;
    }

    .checkbox {
      display: flex;
      gap: 10px;
      align-items: center;
      padding: 12px 14px;
      background: #fffdf8;
      border: 1px solid var(--line);
      border-radius: 14px;
    }

    .viewer {
      padding: 22px;
    }

    .toolbar {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }

    .toolbar p {
      margin: 0;
      color: var(--muted);
    }

    .table-wrap {
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: #fffdf8;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 960px;
    }

    th,
    td {
      padding: 14px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }

    th {
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--muted);
      background: rgba(217, 108, 45, 0.06);
      position: sticky;
      top: 0;
    }

    tr:hover td {
      background: rgba(31, 122, 107, 0.05);
    }

    .pill {
      display: inline-flex;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 0.76rem;
      font-weight: 600;
      background: rgba(31, 122, 107, 0.12);
      color: var(--accent-2);
      white-space: nowrap;
    }

    .pill.fail {
      background: rgba(164, 60, 47, 0.12);
      color: var(--accent-3);
    }

    .details {
      margin-top: 20px;
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 18px;
    }

    .detail-card {
      padding: 18px;
      background: #fffdf8;
      border: 1px solid var(--line);
      border-radius: 18px;
    }

    .detail-card p {
      margin: 0 0 10px;
      line-height: 1.5;
    }

    pre {
      margin: 0;
      padding: 16px;
      border-radius: 16px;
      background: #1e1a17;
      color: #f6e9d2;
      overflow: auto;
      font-size: 0.84rem;
    }

    .muted {
      color: var(--muted);
    }

    .error {
      padding: 16px;
      border-radius: 18px;
      background: rgba(164, 60, 47, 0.1);
      border: 1px solid rgba(164, 60, 47, 0.25);
      color: var(--accent-3);
    }

    @media (max-width: 960px) {
      .layout,
      .details {
        grid-template-columns: 1fr;
      }

      .controls {
        position: static;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <p class="eyebrow">Trend Intelligence Dashboard</p>
      <h1>Customer Trends</h1>
      <p>
        Explore raw combined Google and Amazon trend records, inspect business filters,
        and review the full source payload behind every food or ingredient opportunity.
      </p>
      <div class="stats" id="stats"></div>
    </section>

    <section class="layout">
      <aside class="panel controls">
        <h2>Filters</h2>
        <div class="field">
          <label for="search">Search term</label>
          <input id="search" type="text" placeholder="matcha, gummies, probiotic..." />
        </div>
        <div class="field">
          <label for="category">Category</label>
          <select id="category">
            <option value="">All categories</option>
          </select>
        </div>
        <div class="field">
          <label for="format">Product format</label>
          <select id="format">
            <option value="">All formats</option>
          </select>
        </div>
        <div class="field">
          <label for="source">Source coverage</label>
          <select id="source">
            <option value="">All records</option>
            <option value="both">Google + Amazon</option>
            <option value="google">Google only</option>
            <option value="amazon">Amazon only</option>
          </select>
        </div>
        <div class="field">
          <label class="checkbox">
            <input id="passingOnly" type="checkbox" />
            <span>Show only records that pass business filtering</span>
          </label>
        </div>
      </aside>

      <main class="panel viewer">
        <div class="toolbar">
          <div>
            <h2>Raw Combined Records</h2>
            <p id="resultCount">Loading trend records...</p>
          </div>
        </div>
        <div id="errorBox" class="error" hidden></div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Term</th>
                <th>Category</th>
                <th>Format</th>
                <th>Google Score</th>
                <th>Amazon Score</th>
                <th>Business Filter</th>
                <th>Sources</th>
              </tr>
            </thead>
            <tbody id="tableBody"></tbody>
          </table>
        </div>

        <div class="details">
          <section class="detail-card">
            <h3>Selected Record Summary</h3>
            <div id="detailSummary" class="muted">Select a row to inspect the full record.</div>
          </section>
          <section class="detail-card">
            <h3>Raw JSON</h3>
            <pre id="rawJson">{}</pre>
          </section>
        </div>
      </main>
    </section>
  </div>

  <script>
    const state = {
      payload: null,
      filteredRecords: [],
      selectedIndex: null,
    };

    const refs = {
      stats: document.getElementById("stats"),
      resultCount: document.getElementById("resultCount"),
      tableBody: document.getElementById("tableBody"),
      detailSummary: document.getElementById("detailSummary"),
      rawJson: document.getElementById("rawJson"),
      errorBox: document.getElementById("errorBox"),
      search: document.getElementById("search"),
      category: document.getElementById("category"),
      format: document.getElementById("format"),
      source: document.getElementById("source"),
      passingOnly: document.getElementById("passingOnly"),
    };

    function sourceLabel(record) {
      const hasGoogle = Boolean(record.google_trends);
      const hasAmazon = Boolean(record.amazon_trends);
      if (hasGoogle && hasAmazon) return "Google + Amazon";
      if (hasGoogle) return "Google only";
      if (hasAmazon) return "Amazon only";
      return "No source";
    }

    function buildStats(records) {
      const withGoogle = records.filter((record) => record.google_trends).length;
      const withAmazon = records.filter((record) => record.amazon_trends).length;
      const passing = records.filter((record) => record.business_filter?.passes).length;

      const stats = [
        ["Combined records", records.length],
        ["With Google data", withGoogle],
        ["With Amazon data", withAmazon],
        ["Passing business filter", passing],
      ];

      refs.stats.innerHTML = stats.map(([label, value]) => `
        <article class="stat">
          <p class="stat-label">${label}</p>
          <p class="stat-value">${value}</p>
        </article>
      `).join("");
    }

    function populateSelect(select, values, placeholder) {
      const options = [`<option value="">${placeholder}</option>`]
        .concat(values.map((value) => `<option value="${value}">${value}</option>`));
      select.innerHTML = options.join("");
    }

    function initializeFilters(records) {
      const categories = [...new Set(records.map((record) => record.business_filter?.category).filter(Boolean))].sort();
      const formats = [...new Set(records.map((record) => record.business_filter?.product_format).filter(Boolean))].sort();
      populateSelect(refs.category, categories, "All categories");
      populateSelect(refs.format, formats, "All formats");
    }

    function matchesSourceFilter(record, value) {
      if (!value) return true;
      const hasGoogle = Boolean(record.google_trends);
      const hasAmazon = Boolean(record.amazon_trends);
      if (value === "both") return hasGoogle && hasAmazon;
      if (value === "google") return hasGoogle && !hasAmazon;
      if (value === "amazon") return hasAmazon && !hasGoogle;
      return true;
    }

    function applyFilters() {
      if (!state.payload) return;

      const search = refs.search.value.trim().toLowerCase();
      const category = refs.category.value;
      const format = refs.format.value;
      const source = refs.source.value;
      const passingOnly = refs.passingOnly.checked;

      state.filteredRecords = state.payload.records.filter((record) => {
        const term = (record.term || "").toLowerCase();
        const matchesSearch = !search || term.includes(search);
        const matchesCategory = !category || record.business_filter?.category === category;
        const matchesFormat = !format || record.business_filter?.product_format === format;
        const matchesPassing = !passingOnly || record.business_filter?.passes;
        const matchesSource = matchesSourceFilter(record, source);

        return matchesSearch && matchesCategory && matchesFormat && matchesPassing && matchesSource;
      });

      renderTable();
      renderSelection(state.filteredRecords[0] || null);
    }

    function renderTable() {
      refs.resultCount.textContent = `${state.filteredRecords.length} records shown`;

      refs.tableBody.innerHTML = state.filteredRecords.map((record, index) => {
        const pass = Boolean(record.business_filter?.passes);
        const googleScore = record.combined_signals?.google_opportunity_score;
        const amazonScore = record.combined_signals?.amazon_opportunity_score;

        return `
          <tr data-index="${index}">
            <td><strong>${record.term}</strong></td>
            <td>${record.business_filter?.category || "uncategorized"}</td>
            <td>${record.business_filter?.product_format || "n/a"}</td>
            <td>${googleScore ?? "n/a"}</td>
            <td>${amazonScore ?? "n/a"}</td>
            <td><span class="pill ${pass ? "" : "fail"}">${pass ? "pass" : "fail"}</span></td>
            <td>${sourceLabel(record)}</td>
          </tr>
        `;
      }).join("");

      [...refs.tableBody.querySelectorAll("tr")].forEach((row) => {
        row.addEventListener("click", () => {
          const index = Number(row.dataset.index);
          renderSelection(state.filteredRecords[index]);
        });
      });
    }

    function renderSelection(record) {
      if (!record) {
        refs.detailSummary.textContent = "No record matches the current filters.";
        refs.rawJson.textContent = "{}";
        return;
      }

      const summary = [
        `<p><strong>Term:</strong> ${record.term}</p>`,
        `<p><strong>Category:</strong> ${record.business_filter?.category || "uncategorized"}</p>`,
        `<p><strong>Product format:</strong> ${record.business_filter?.product_format || "n/a"}</p>`,
        `<p><strong>Business filter:</strong> ${record.business_filter?.passes ? "pass" : "fail"}</p>`,
        `<p><strong>Google score:</strong> ${record.combined_signals?.google_opportunity_score ?? "n/a"}</p>`,
        `<p><strong>Amazon score:</strong> ${record.combined_signals?.amazon_opportunity_score ?? "n/a"}</p>`,
        `<p><strong>Source coverage:</strong> ${sourceLabel(record)}</p>`,
      ].join("");

      refs.detailSummary.innerHTML = summary;
      refs.rawJson.textContent = JSON.stringify(record, null, 2);
    }

    async function loadData() {
      try {
        const response = await fetch("/api/trends");
        if (!response.ok) {
          throw new Error(`Server returned ${response.status}`);
        }

        state.payload = await response.json();
        buildStats(state.payload.records);
        initializeFilters(state.payload.records);
        applyFilters();
      } catch (error) {
        refs.errorBox.hidden = false;
        refs.errorBox.textContent = `Unable to load trend data: ${error.message}`;
        refs.resultCount.textContent = "0 records shown";
      }
    }

    [
      refs.search,
      refs.category,
      refs.format,
      refs.source,
      refs.passingOnly,
    ].forEach((element) => element.addEventListener("input", applyFilters));

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

            try:
                payload = build_combined_trends_payload(
                    amazon_max_keywords=int(amazon_limit),
                )
                self._send_json(payload)
            except Exception as exc:  # pragma: no cover - runtime UI feedback
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
