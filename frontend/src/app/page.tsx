"use client";

import React, { useEffect, useState, useRef } from 'react';

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [format, setFormat] = useState('');
  const [source, setSource] = useState('');
  const [passingOnly, setPassingOnly] = useState(false);
  const [sortKey, setSortKey] = useState('default');
  
  const [selectedCardId, setSelectedCardId] = useState<number | null>(null);
  const [cols, setCols] = useState(3);
  const gridRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!gridRef.current) return;
    const observer = new ResizeObserver((entries) => {
      for (let entry of entries) {
        // Calculation matching CSS grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)) with 16px gap
        const containerWidth = entry.contentRect.width;
        const calculatedCols = Math.floor((containerWidth + 16) / (320 + 16)) || 1;
        setCols(calculatedCols);
      }
    });
    observer.observe(gridRef.current);
    return () => observer.disconnect();
  }, []);
/*
  useEffect(() => {
    // Dynamic import to simulate grabbing the file (in Next.js you'd ideally use an API route, but this works purely locally)
    fetch('/api/trends')
      .then(res => {
        // We will just create an API route to read the file so it works seamlessly inside Next.js
        return res.json();
      })
      .catch(e => {
        console.error("Using a mock fallback while API routing isn't set up...", e);
      });
  }, []);
*/
  // Use a hack to load the file directly if /api/trends is missing: 
  // Normally we would just wait for the api, but actually I need an API route! Wait, let's just make page.tsx pull data on the server part. 
  // Because it's "use client", I should just use `useEffect` and `fetch`. 
  // Let me just import the JSON directly utilizing Webpack.
  
  useEffect(() => {
  fetch('/latest_trends.json')
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then(data => setData(data))
    .catch(err => console.error('Failed to load trends:', err));
}, []);

  const trends = data?.trusted_trends || [];

  // Derived filters
  const categories = Array.from(new Set(trends.map((r: any) => r.business_filter?.category).filter(Boolean))).sort() as string[];
  const formats = Array.from(new Set(trends.map((r: any) => r.business_filter?.product_format).filter(Boolean))).sort() as string[];

  const withGoogle = trends.filter((r: any) => r.google_trends).length;
  const withAmazon = trends.filter((r: any) => r.amazon_trends).length;
  const passing = trends.filter((r: any) => r.business_filter?.passes).length;

  const matchesSource = (record: any, value: string) => {
    if (!value) return true;
    const g = Boolean(record.google_trends);
    const a = Boolean(record.amazon_trends);
    if (value === "both") return g && a;
    if (value === "google") return g && !a;
    if (value === "amazon") return a && !g;
    return true;
  };

  let filteredRecords = trends.filter((r: any) => {
    const term = (r.term || "").toLowerCase();
    return (!search || term.includes(search.toLowerCase()))
        && (!category || r.business_filter?.category === category)
        && (!format || r.business_filter?.product_format === format)
        && (!passingOnly || r.business_filter?.passes)
        && matchesSource(r, source);
  });

  const getG = (r: any) => r.combined_signals?.google_opportunity_score ?? -1;
  const getA = (r: any) => r.combined_signals?.amazon_opportunity_score ?? -1;

  if (sortKey === "alpha-asc") filteredRecords.sort((a: any, b: any) => a.term.localeCompare(b.term));
  if (sortKey === "alpha-desc") filteredRecords.sort((a: any, b: any) => b.term.localeCompare(a.term));
  if (sortKey === "google-desc") filteredRecords.sort((a: any, b: any) => getG(b) - getG(a));
  if (sortKey === "google-asc") filteredRecords.sort((a: any, b: any) => getG(a) - getG(b));
  if (sortKey === "amazon-desc") filteredRecords.sort((a: any, b: any) => getA(b) - getA(a));
  if (sortKey === "amazon-asc") filteredRecords.sort((a: any, b: any) => getA(a) - getA(b));
  if (sortKey === "ready-first") filteredRecords.sort((a: any, b: any) => {
    return (b.business_filter?.passes ? 1 : 0) - (a.business_filter?.passes ? 1 : 0);
  });

  return (
    <>
      <div className="topbar">
        <span className="topbar-brand">Prince of Peace</span>
        <span>Opportunity Intelligence</span>
        <span className="topbar-tag">Live Data</span>
      </div>

      <div className="hero">
        <div className="hero-inner">
          <span className="hero-eyebrow">Market Intelligence</span>
          <h1>What's <em>growing</em> right now</h1>
          <p className="hero-sub">
            Real consumer demand signals from Google and Amazon — filtered for food and wellness opportunities you can act on today.
          </p>
          <div className="stats">
            <article className="stat">
              <div className="stat-label">Trends Tracked</div>
              <div className="stat-value">{trends.length}</div>
            </article>
            <article className="stat">
              <div className="stat-label">Google Signals</div>
              <div className="stat-value">{withGoogle}</div>
            </article>
            <article className="stat">
              <div className="stat-label">Amazon Signals</div>
              <div className="stat-value">{withAmazon}</div>
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
          <p className="sidebar-sub">Narrow results by what matters to your buying decision.</p>

          <div className="field">
            <label>Keyword</label>
            <input type="text" placeholder="e.g. matcha, probiotic…" value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <div className="field">
            <label>Category</label>
            <select value={category} onChange={e => setCategory(e.target.value)}>
              <option value="">All categories</option>
              {categories.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Product type</label>
            <select value={format} onChange={e => setFormat(e.target.value)}>
              <option value="">All types</option>
              {formats.map(f => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Signal source</label>
            <select value={source} onChange={e => setSource(e.target.value)}>
              <option value="">All signals</option>
              <option value="both">Google + Amazon</option>
              <option value="google">Google only</option>
              <option value="amazon">Amazon only</option>
            </select>
          </div>
          <label className="toggle-row">
            <input type="checkbox" checked={passingOnly} onChange={e => setPassingOnly(e.target.checked)} />
            <span>Show only <strong>ready opportunities</strong> — trends that meet all business criteria</span>
          </label>

          <div className="divider"></div>
          <div className="legend">
            <div className="legend-item"><span className="legend-dot" style={{background:'var(--green)'}}></span> Ready opportunity</div>
            <div className="legend-item"><span className="legend-dot" style={{background:'var(--soft)'}}></span> Monitoring / not yet ready</div>
            <div className="legend-item"><span className="legend-dot" style={{background:'var(--accent)'}}></span> Score 70+ = strong signal</div>
          </div>
        </aside>

        <main className="main">
          <div className="main-header">
            <div className="main-title">Trend Opportunities</div>
            <div className="result-count">{filteredRecords.length} results</div>
          </div>
          <div className="sort-bar" style={{marginBottom: "18px"}}>
            <span className="sort-label">Sort by</span>
            {[
              { id: 'default', label: 'Featured' },
              { id: 'alpha-asc', label: 'A → Z' },
              { id: 'alpha-desc', label: 'Z → A' },
              { id: 'google-desc', label: 'Search demand ↑' },
              { id: 'google-asc', label: 'Search demand ↓' },
              { id: 'amazon-desc', label: 'Shopping demand ↑' },
              { id: 'amazon-asc', label: 'Shopping demand ↓' },
              { id: 'ready-first', label: 'Ready first' },
            ].map(s => (
              <button 
                key={s.id} 
                className={`sort-btn ${sortKey === s.id ? 'active' : ''}`}
                onClick={() => setSortKey(s.id)}
              >
                {s.label}
              </button>
            ))}
          </div>

          <div className="card-grid" ref={gridRef}>
            {filteredRecords.map((record: any, idx: number) => {
              const pass = record.business_filter?.passes;
              const tr = record.trust_breakdown || {};
              const total = tr.total_score || 0;
              const isSelected = selectedCardId === idx;
              
              // Calculate if we should render the drawer AFTER this item
              const isDrawerTarget = selectedCardId !== null 
                  && idx === Math.min((Math.floor(selectedCardId / cols) + 1) * cols - 1, filteredRecords.length - 1);
              
              const activeRecord = selectedCardId !== null ? filteredRecords[selectedCardId] : null;
              const activeTr = activeRecord?.trust_breakdown || {};
              const activePass = activeRecord?.business_filter?.passes;

              return (
                <React.Fragment key={idx}>
                  <article 
                    className={`opportunity-card ${pass ? 'pass' : 'fail'} ${isSelected ? 'selected' : ''}`}
                    onClick={() => setSelectedCardId(isSelected ? null : idx)}
                  >
                  <div className="card-top">
                    <h2 className="card-term">{record.term}</h2>
                    <span className={`badge ${pass ? 'pass' : 'fail'}`}>
                      {total} T.R.U.S.T
                    </span>
                  </div>

                  <div className="card-meta">
                    {record.business_filter?.category && <span className="tag">{record.business_filter.category}</span>}
                    {record.business_filter?.product_format && <span className="tag">{record.business_filter.product_format}</span>}
                  </div>
                  </article>

                  {isDrawerTarget && activeRecord && (
                    <div className="detail-drawer" style={{ gridColumn: '1 / -1', margin: '0 0 16px 0' }}>
                       <div className="drawer-header">
                         <h3 className="drawer-term">{activeRecord.term}</h3>
                         <button className="drawer-close" onClick={() => setSelectedCardId(null)}>×</button>
                       </div>
                       
                       <div className="drawer-body">
                          <div className="drawer-section">
                            <h4 className="drawer-section-title">Breakdown</h4>
                            <div className="drawer-row">
                              <span className="drawer-row-label">Trajectory (Velocity)</span>
                              <span className="drawer-row-value">{activeTr.trajectory_30} / 30</span>
                            </div>
                            <div className="drawer-row">
                              <span className="drawer-row-label">Uniqueness (Whitespace)</span>
                              <span className="drawer-row-value">{activeTr.uniqueness_20} / 20</span>
                            </div>
                          </div>
                          
                          <div className="drawer-section">
                            <h4 className="drawer-section-title">Business Fit</h4>
                            <div className="drawer-row">
                              <span className="drawer-row-label">Sourcing Feasibility</span>
                              <span className="drawer-row-value">{activeTr.sourcing_15} / 15</span>
                            </div>
                            <div className="drawer-row">
                              <span className="drawer-row-label">Market Translation</span>
                              <span className="drawer-row-value">{activeTr.translation_15} / 15</span>
                            </div>
                          </div>

                          <div className="drawer-section">
                            <h4 className="drawer-section-title">Risk Assessment</h4>
                            <div className="drawer-row">
                              <span className="drawer-row-label">FDA & Shelf-life (+20)</span>
                              <span className={`drawer-row-value ${activePass ? 'high' : ''}`}>
                                {activeTr.risk_20} / 20
                              </span>
                            </div>
                            <div className="drawer-row">
                              <span className="drawer-row-label">Agent Notes</span>
                              <span className="agent-notes">
                                {activeTr.risk_notes || (activePass ? "Cleared constraints." : "Flagged compliance issue.")}
                              </span>
                            </div>
                          </div>
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
        </main>
      </div>
    </>
  );
}
