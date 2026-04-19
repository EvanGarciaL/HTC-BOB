"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import trendsData from "./latest_trends.json";

const ITEMS_PER_PAGE = 50;

const SORT_OPTIONS = [
  { id: "featured", label: "Featured" },
  { id: "alpha-asc", label: "A → Z" },
  { id: "alpha-desc", label: "Z → A" },
  { id: "google-desc", label: "Search demand ↑" },
  { id: "google-asc", label: "Search demand ↓" },
  { id: "amazon-desc", label: "Shopping demand ↑" },
  { id: "amazon-asc", label: "Shopping demand ↓" },
  { id: "trust-desc", label: "Trust score ↑" },
  { id: "trust-asc", label: "Trust score ↓" },
  { id: "ready-first", label: "Ready first" },
] as const;

const HELP_CONTENT: Record<
  string,
  { title: string; meaning: string; calculation: string }
> = {
  trajectory: {
    title: "Trajectory (Velocity)",
    meaning: "How quickly the trend is gaining momentum across the signals we track.",
    calculation:
      "Built from the Google opportunity signal and Amazon opportunity signal, then scaled into the 30-point trajectory bucket.",
  },
  uniqueness: {
    title: "Uniqueness (Whitespace)",
    meaning: "How open the market still looks for this idea compared with more crowded concepts.",
    calculation:
      "Taken from the whitespace estimate in the trust scoring logic, then scaled into the 20-point uniqueness bucket.",
  },
  sourcing: {
    title: "Sourcing Feasibility",
    meaning: "How realistic it is to source, manufacture, and support consistently.",
    calculation:
      "Pulled directly from the sourcing feasibility score and capped at 15 points in the trust model.",
  },
  translation: {
    title: "Market Translation",
    meaning: "How easily the trend can turn into a product consumers immediately understand and want.",
    calculation:
      "Pulled directly from the translation-to-market score and capped at 15 points in the trust model.",
  },
  risk: {
    title: "FDA & Shelf-life",
    meaning: "How cleanly the item passes shelf-life and restricted-ingredient checks.",
    calculation:
      "Based on the compliance and shelf-stability checks in the trust model, then scaled into the 20-point risk bucket.",
  },
};

function formatLabel(value: string | null | undefined) {
  if (!value) return "";
  return value
    .split(/[\s_-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function getMetricColor(ratio: number) {
  if (ratio <= 0.2) return "#d14f45";
  if (ratio <= 0.4) return "#df7a3f";
  if (ratio <= 0.6) return "#d9ad34";
  if (ratio <= 0.8) return "#92b765";
  return "#2f8b57";
}

function ScoreSquares({
  value,
  max,
}: {
  value: number;
  max: number;
}) {
  const safeMax = max || 1;
  const ratio = Math.max(0, Math.min(value / safeMax, 1));
  const fill = ratio * 5;
  const color = getMetricColor(ratio);

  return (
    <div className="score-squares" aria-hidden="true">
      {Array.from({ length: 5 }).map((_, index) => {
        const squareFill = Math.max(0, Math.min(fill - index, 1));
        return (
          <span className="score-square-shell" key={index}>
            <span
              className="score-square-fill"
              style={{
                width: `${squareFill * 100}%`,
                background: color,
              }}
            />
          </span>
        );
      })}
    </div>
  );
}

function HelpButton({
  metricKey,
  activeMetric,
  onToggle,
}: {
  metricKey: string;
  activeMetric: string | null;
  onToggle: (metricKey: string) => void;
}) {
  const isOpen = activeMetric === metricKey;
  const content = HELP_CONTENT[metricKey];

  return (
    <div className="help-wrap">
      <button
        type="button"
        className="help-button"
        onClick={(event) => {
          event.stopPropagation();
          onToggle(metricKey);
        }}
        aria-label={`About ${content.title}`}
      >
        ?
      </button>
      {isOpen && (
        <div className="help-popup" onClick={(event) => event.stopPropagation()}>
          <div className="help-popup-title">{content.title}</div>
          <div className="help-popup-block">
            <div className="help-popup-label">Meaning</div>
            <p className="help-popup-copy">{content.meaning}</p>
          </div>
          <div className="help-popup-block">
            <div className="help-popup-label">Calculation</div>
            <div className="help-popup-equation">{content.calculation}</div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [format, setFormat] = useState("");
  const [source, setSource] = useState("");
  const [passingOnly, setPassingOnly] = useState(false);
  const [sortKey, setSortKey] = useState<string>("featured");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedCardId, setSelectedCardId] = useState<number | null>(null);
  const [activeHelpMetric, setActiveHelpMetric] = useState<string | null>(null);
  const [cols, setCols] = useState(3);
  const [insightModal, setInsightModal] = useState<{
    type: "recommendations" | "competitors";
    term: string;
    category: string;
  } | null>(null);
  const [insightState, setInsightState] = useState<{
    loading: boolean;
    error: string | null;
    competitors: string[];
    recommendations: string[];
  }>({
    loading: false,
    error: null,
    competitors: [],
    recommendations: [],
  });
  const gridRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!gridRef.current) return;
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const containerWidth = entry.contentRect.width;
        const calculatedCols = Math.floor((containerWidth + 16) / (320 + 16)) || 1;
        setCols(calculatedCols);
      }
    });
    observer.observe(gridRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    setData(trendsData);
  }, []);

  const trends = data?.trusted_trends || [];

  const categories = useMemo(
    () =>
      Array.from(
        new Set(trends.map((record: any) => record.business_filter?.category).filter(Boolean)),
      ).sort() as string[],
    [trends],
  );

  const formats = useMemo(
    () =>
      Array.from(
        new Set(trends.map((record: any) => record.business_filter?.product_format).filter(Boolean)),
      ).sort() as string[],
    [trends],
  );

  const withGoogle = trends.filter((record: any) => record.google_trends).length;
  const withAmazon = trends.filter((record: any) => record.amazon_trends).length;
  const passing = trends.filter((record: any) => record.business_filter?.passes).length;

  const filteredRecords = useMemo(() => {
    const matchesSource = (record: any) => {
      if (!source) return true;
      const hasGoogle = Boolean(record.google_trends);
      const hasAmazon = Boolean(record.amazon_trends);
      if (source === "both") return hasGoogle && hasAmazon;
      if (source === "google") return hasGoogle && !hasAmazon;
      if (source === "amazon") return hasAmazon && !hasGoogle;
      return true;
    };

    const getGoogle = (record: any) => record.combined_signals?.google_opportunity_score ?? -1;
    const getAmazon = (record: any) => record.combined_signals?.amazon_opportunity_score ?? -1;
    const getTrust = (record: any) => record.trust_breakdown?.total_score ?? -1;

    const records = trends.filter((record: any) => {
      const term = String(record.term || "").toLowerCase();
      return (
        (!search || term.includes(search.toLowerCase())) &&
        (!category || record.business_filter?.category === category) &&
        (!format || record.business_filter?.product_format === format) &&
        (!passingOnly || record.business_filter?.passes) &&
        matchesSource(record)
      );
    });

    records.sort((a: any, b: any) => {
      if (sortKey === "alpha-asc") return a.term.localeCompare(b.term);
      if (sortKey === "alpha-desc") return b.term.localeCompare(a.term);
      if (sortKey === "google-desc") return getGoogle(b) - getGoogle(a);
      if (sortKey === "google-asc") return getGoogle(a) - getGoogle(b);
      if (sortKey === "amazon-desc") return getAmazon(b) - getAmazon(a);
      if (sortKey === "amazon-asc") return getAmazon(a) - getAmazon(b);
      if (sortKey === "trust-desc") return getTrust(b) - getTrust(a);
      if (sortKey === "trust-asc") return getTrust(a) - getTrust(b);
      if (sortKey === "ready-first") {
        return Number(Boolean(b.business_filter?.passes)) - Number(Boolean(a.business_filter?.passes));
      }
      return getTrust(b) - getTrust(a);
    });

    return records;
  }, [trends, search, category, format, source, passingOnly, sortKey]);

  useEffect(() => {
    setCurrentPage(1);
    setSelectedCardId(null);
    setActiveHelpMetric(null);
  }, [search, category, format, source, passingOnly, sortKey]);

  const totalPages = Math.max(1, Math.ceil(filteredRecords.length / ITEMS_PER_PAGE));
  const currentPageSafe = Math.min(currentPage, totalPages);
  const pageStartIndex = (currentPageSafe - 1) * ITEMS_PER_PAGE;
  const pageRecords = filteredRecords.slice(pageStartIndex, pageStartIndex + ITEMS_PER_PAGE);

  const selectedRecord = selectedCardId !== null ? pageRecords[selectedCardId] : null;

  function formatSignalValue(value: number | null | undefined) {
    if (value === null || value === undefined || Number.isNaN(value)) return "—";
    return Number(value).toFixed(1);
  }

  function signalTone(value: number | null | undefined) {
    if (value === null || value === undefined || Number.isNaN(value)) return "muted";
    if (value >= 80) return "high";
    if (value >= 60) return "medium";
    return "low";
  }

  async function openInsightModal(type: "recommendations" | "competitors", record: any) {
    setInsightModal({
      type,
      term: record.term,
      category: record.business_filter?.category || "uncategorized",
    });

    const fallback = record.product_insights || {};
    setInsightState({
      loading: true,
      error: null,
      competitors: fallback.competitors || [],
      recommendations: fallback.recommendations || [],
    });

    try {
      const query = new URLSearchParams({
        term: record.term,
        category: record.business_filter?.category || "uncategorized",
      });
      const response = await fetch(`/api/product-insights?${query.toString()}`);
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "Unable to fetch product insights.");
      }
      setInsightState({
        loading: false,
        error: null,
        competitors: payload.competitors || [],
        recommendations: payload.recommendations || [],
      });
    } catch (error) {
      setInsightState((current) => ({
        ...current,
        loading: false,
        error: error instanceof Error ? error.message : "Unable to fetch product insights.",
      }));
    }
  }

  return (
    <>
      <div className="topbar">
        <span className="topbar-brand">Prince of Peace</span>
        <span>BOB: Best of Buyers</span>
        <span className="topbar-tag">Live Data</span>
      </div>

      <div className="hero">
        <div className="hero-inner">
          <span className="hero-eyebrow">Market Intelligence</span>
          <h1>
            What&apos;s <em>growing</em> right now
          </h1>
          <p className="hero-sub">
            Real consumer demand signals from Google and Amazon, filtered into product opportunities your team can evaluate quickly.
          </p>
          <div className="stats">
            <article className="stat">
              <div className="stat-label">Google/Amazon Signals</div>
              <div className="stat-value">{trends.length}</div>
            </article>
            <article className="stat">
              <div className="stat-label">Ready Opportunities</div>
              <div className="stat-value">{passing}</div>
            </article>
          </div>
        </div>
      </div>

      <div className="shell">
        <aside className="sidebar">
          <div className="sidebar-title">Find opportunities</div>
          <p className="sidebar-sub">Narrow results by the signals that matter most to your buying decision.</p>

          <div className="field">
            <label>Keyword</label>
            <input
              type="text"
              placeholder="e.g. matcha, probiotic..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>

          <div className="field">
            <label>Category</label>
            <select value={category} onChange={(event) => setCategory(event.target.value)}>
              <option value="">All categories</option>
              {categories.map((value) => (
                <option key={value} value={value}>
                  {formatLabel(value)}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label>Product Type</label>
            <select value={format} onChange={(event) => setFormat(event.target.value)}>
              <option value="">All types</option>
              {formats.map((value) => (
                <option key={value} value={value}>
                  {formatLabel(value)}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label>Signal Source</label>
            <select value={source} onChange={(event) => setSource(event.target.value)}>
              <option value="">All signals</option>
              <option value="both">Google + Amazon</option>
              <option value="google">Google only</option>
              <option value="amazon">Amazon only</option>
            </select>
          </div>

          <label className="toggle-row">
            <input
              type="checkbox"
              checked={passingOnly}
              onChange={(event) => setPassingOnly(event.target.checked)}
            />
            <span>
              Show only <strong>ready opportunities</strong>
            </span>
          </label>

          <div className="divider" />

          <div className="legend">
            <div className="legend-item">
              <span className="legend-dot" style={{ background: "var(--green)" }} />
              Ready opportunity
            </div>
            <div className="legend-item">
              <span className="legend-dot" style={{ background: "var(--soft)" }} />
              Monitoring
            </div>
            <div className="legend-item">
              <span className="legend-dot" style={{ background: "var(--accent)" }} />
              Strong trust score
            </div>
          </div>
        </aside>

        <main className="main">
          <div className="main-header">
            <div className="main-title">Trend Opportunities</div>
            <div className="result-count">{filteredRecords.length} results</div>
          </div>

          <div className="sort-bar">
            <span className="sort-label">Sort By</span>
            {SORT_OPTIONS.map((option) => (
              <button
                key={option.id}
                type="button"
                className={`sort-btn ${sortKey === option.id ? "active" : ""}`}
                onClick={() => setSortKey(option.id)}
              >
                {option.label}
              </button>
            ))}
          </div>

          <div className="page-range">
            Showing {filteredRecords.length === 0 ? 0 : pageStartIndex + 1}-
            {Math.min(pageStartIndex + ITEMS_PER_PAGE, filteredRecords.length)} of {filteredRecords.length}
          </div>

          <div className="card-grid" ref={gridRef}>
            {pageRecords.map((record: any, idx: number) => {
              const trust = record.trust_breakdown || {};
              const passed = Boolean(record.business_filter?.passes);
              const isSelected = selectedCardId === idx;
              const googleScore = record.combined_signals?.google_opportunity_score ?? null;
              const amazonScore = record.combined_signals?.amazon_opportunity_score ?? null;
              const isDrawerTarget =
                selectedCardId !== null &&
                idx === Math.min((Math.floor(selectedCardId / cols) + 1) * cols - 1, pageRecords.length - 1);
              const activeRecord = selectedCardId !== null ? pageRecords[selectedCardId] : null;
              const activeTrust = activeRecord?.trust_breakdown || {};
              const activePass = activeRecord?.business_filter?.passes;

              return (
                <React.Fragment key={record.term}>
                  <article
                    className={`opportunity-card ${passed ? "pass" : "fail"} ${isSelected ? "selected" : ""}`}
                    onClick={() => {
                      setSelectedCardId(isSelected ? null : idx);
                      setActiveHelpMetric(null);
                    }}
                  >
                    <div className="card-top">
                      <h2 className="card-term" style={{ textTransform: "capitalize" }}>{record.term}</h2>
                      <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                        <span className="status-badge" style={{ background: "#f8f1e8", color: "#766759" }}>
                          Trust: {trust.total_score ?? "—"}
                        </span>
                        <span className={`status-badge ${passed ? "ready" : "watching"}`}>
                          {passed ? "Ready" : "Watching"}
                        </span>
                      </div>
                    </div>

                    <div className="card-meta">
                      {record.business_filter?.category && (
                        <span className="tag">{formatLabel(record.business_filter.category)}</span>
                      )}
                      {record.business_filter?.product_format && (
                        <span className="tag">{formatLabel(record.business_filter.product_format)}</span>
                      )}
                    </div>

                    <div className="signal-grid">
                      <div className="signal-card">
                        <div className="signal-label">Search Demand</div>
                        <div className={`signal-value ${signalTone(googleScore)}`}>
                          {formatSignalValue(googleScore)}
                        </div>
                      </div>
                      <div className="signal-card">
                        <div className="signal-label">Shopping Demand</div>
                        <div className={`signal-value ${signalTone(amazonScore)}`}>
                          {formatSignalValue(amazonScore)}
                        </div>
                      </div>
                    </div>

                  </article>

                  {isDrawerTarget && activeRecord && (
                    <div className="detail-drawer inline-drawer" style={{ gridColumn: "1 / -1" }}>
                      <div className="drawer-header">
                        <h3 className="drawer-term" style={{ textTransform: "capitalize" }}>{activeRecord.term}</h3>
                        <button type="button" className="drawer-close" onClick={() => setSelectedCardId(null)}>
                          ×
                        </button>
                      </div>

                      <div className="drawer-body">
                        <div className="drawer-section">
                          <h4 className="drawer-section-title">Breakdown</h4>

                          <div className="drawer-metric">
                            <div className="drawer-row">
                              <span className="drawer-row-label">
                                Trajectory (Velocity)
                                <HelpButton
                                  metricKey="trajectory"
                                  activeMetric={activeHelpMetric}
                                  onToggle={(metricKey) =>
                                    setActiveHelpMetric((current) => (current === metricKey ? null : metricKey))
                                  }
                                />
                              </span>
                              <span className="drawer-row-value">
                                {activeTrust.trajectory_30 ?? 0} / 30
                              </span>
                            </div>
                            <ScoreSquares value={activeTrust.trajectory_30 ?? 0} max={30} />
                          </div>

                          <div className="drawer-metric">
                            <div className="drawer-row">
                              <span className="drawer-row-label">
                                Uniqueness (Whitespace)
                                <HelpButton
                                  metricKey="uniqueness"
                                  activeMetric={activeHelpMetric}
                                  onToggle={(metricKey) =>
                                    setActiveHelpMetric((current) => (current === metricKey ? null : metricKey))
                                  }
                                />
                              </span>
                              <span className="drawer-row-value">
                                {activeTrust.uniqueness_20 ?? 0} / 20
                              </span>
                            </div>
                            <ScoreSquares value={activeTrust.uniqueness_20 ?? 0} max={20} />
                          </div>
                        </div>

                        <div className="drawer-section">
                          <h4 className="drawer-section-title">Business Fit</h4>

                          <div className="drawer-metric">
                            <div className="drawer-row">
                              <span className="drawer-row-label">
                                Sourcing Feasibility
                                <HelpButton
                                  metricKey="sourcing"
                                  activeMetric={activeHelpMetric}
                                  onToggle={(metricKey) =>
                                    setActiveHelpMetric((current) => (current === metricKey ? null : metricKey))
                                  }
                                />
                              </span>
                              <span className="drawer-row-value">
                                {activeTrust.sourcing_15 ?? 0} / 15
                              </span>
                            </div>
                            <ScoreSquares value={activeTrust.sourcing_15 ?? 0} max={15} />
                          </div>

                          <div className="drawer-metric">
                            <div className="drawer-row">
                              <span className="drawer-row-label">
                                Market Translation
                                <HelpButton
                                  metricKey="translation"
                                  activeMetric={activeHelpMetric}
                                  onToggle={(metricKey) =>
                                    setActiveHelpMetric((current) => (current === metricKey ? null : metricKey))
                                  }
                                />
                              </span>
                              <span className="drawer-row-value">
                                {activeTrust.translation_15 ?? 0} / 15
                              </span>
                            </div>
                            <ScoreSquares value={activeTrust.translation_15 ?? 0} max={15} />
                          </div>
                        </div>

                        <div className="drawer-section">
                          <h4 className="drawer-section-title">Risk Assessment</h4>

                          <div className="drawer-metric">
                            <div className="drawer-row">
                              <span className="drawer-row-label">
                                FDA & Shelf-life (+20)
                                <HelpButton
                                  metricKey="risk"
                                  activeMetric={activeHelpMetric}
                                  onToggle={(metricKey) =>
                                    setActiveHelpMetric((current) => (current === metricKey ? null : metricKey))
                                  }
                                />
                              </span>
                              <span className={`drawer-row-value ${activePass ? "high" : ""}`}>
                                {activeTrust.risk_20 ?? 0} / 20
                              </span>
                            </div>
                            <ScoreSquares value={activeTrust.risk_20 ?? 0} max={20} />
                          </div>

                          <div className="drawer-row notes-inline">
                            <span className="drawer-row-label">Agent Notes</span>
                            <span className="agent-notes">
                              {activePass ? "✅" : (activeTrust.risk_notes || "Flagged compliance issue.")}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="drawer-links">
                        <button
                          type="button"
                          className="drawer-link"
                          onClick={() => openInsightModal("recommendations", activeRecord)}
                        >
                          Product Recommendations
                        </button>
                        <button
                          type="button"
                          className="drawer-link"
                          onClick={() => openInsightModal("competitors", activeRecord)}
                        >
                          Product Competitors
                        </button>
                      </div>
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>

          {filteredRecords.length === 0 && (
            <div className="empty">
              <div className="empty-icon">🔍</div>
              <h3>No opportunities found</h3>
              <p>Try adjusting your filters or search terms.</p>
            </div>
          )}

          {filteredRecords.length > ITEMS_PER_PAGE && (
            <div className="pagination">
              <button
                type="button"
                className="page-btn"
                disabled={currentPageSafe === 1}
                onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
              >
                Previous
              </button>
              <div className="page-list">
                {Array.from({ length: totalPages }).map((_, index) => {
                  const page = index + 1;
                  return (
                    <button
                      type="button"
                      key={page}
                      className={`page-number ${page === currentPageSafe ? "active" : ""}`}
                      onClick={() => setCurrentPage(page)}
                    >
                      {page}
                    </button>
                  );
                })}
              </div>
              <button
                type="button"
                className="page-btn"
                disabled={currentPageSafe === totalPages}
                onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
              >
                Next
              </button>
            </div>
          )}
        </main>
      </div>

      {insightModal && (
        <div className="modal-backdrop" onClick={() => setInsightModal(null)}>
          <div className="modal-window" onClick={(event) => event.stopPropagation()}>
            <div className="modal-header">
              <div>
                <div className="modal-kicker">{insightModal.term}</div>
                <h3 className="modal-title">
                  {insightModal.type === "recommendations" ? "Product Recommendations" : "Product Competitors"}
                </h3>
              </div>
              <button type="button" className="drawer-close" onClick={() => setInsightModal(null)}>
                ×
              </button>
            </div>

            {insightState.loading && <div className="modal-message">Loading...</div>}
            {!insightState.loading && insightState.error && (
              <div className="modal-message">{insightState.error}</div>
            )}

            {!insightState.loading && !insightState.error && (
              <div className="modal-list">
                {(insightModal.type === "recommendations"
                  ? insightState.recommendations
                  : insightState.competitors
                ).length > 0 ? (
                  (insightModal.type === "recommendations"
                    ? insightState.recommendations
                    : insightState.competitors
                  ).map((item, index) => (
                    <div className="modal-list-item" key={`${item}-${index}`}>
                      {item}
                    </div>
                  ))
                ) : (
                  <div className="modal-message">No information yet.</div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
