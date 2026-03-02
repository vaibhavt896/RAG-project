"use client";

import { useState, useEffect, useCallback } from "react";

const API_BASE = "http://localhost:8000";

interface Citation {
    ref_number: number;
    title: string;
    source: string;
    page: number | null;
    excerpt: string;
}

interface QueryResponse {
    question: string;
    answer: string;
    citations: Citation[];
    faithfulness_score: number | null;
    latency_ms: number;
    model_used: string;
    tokens_used: number;
}

interface Stats {
    vector_store_size: number;
    bm25_index_size: number;
}

interface IngestResult {
    doc_id: string;
    chunks_created: number;
    source: string;
}

// Parse answer text to highlight citation references like [1], [2]
function renderAnswerWithCitations(answer: string): React.ReactNode[] {
    const parts = answer.split(/(\[\d+(?:,\s*\d+)*\])/g);
    return parts.map((part, i) => {
        const match = part.match(/^\[(\d+(?:,\s*\d+)*)\]$/);
        if (match) {
            const refs = match[1].split(",").map((n) => n.trim());
            return refs.map((ref, j) => (
                <span key={`${i}-${j}`} className="citation-ref" title={`Source [${ref}]`}>
                    {ref}
                </span>
            ));
        }
        return <span key={i}>{part}</span>;
    });
}

export default function Home() {
    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<QueryResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [stats, setStats] = useState<Stats | null>(null);
    const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set());

    // Ingest state
    const [ingestSource, setIngestSource] = useState("");
    const [ingesting, setIngesting] = useState(false);
    const [ingestResult, setIngestResult] = useState<IngestResult | null>(null);
    const [ingestError, setIngestError] = useState<string | null>(null);

    // Fetch stats on mount
    useEffect(() => {
        fetch(`${API_BASE}/stats`)
            .then((res) => res.json())
            .then(setStats)
            .catch(() => { });
    }, []);

    const handleQuery = useCallback(async () => {
        if (!query.trim() || loading) return;
        setLoading(true);
        setError(null);
        setResult(null);
        setExpandedSources(new Set());

        try {
            const res = await fetch(`${API_BASE}/query`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: query, top_k: 5 }),
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Query failed");
            }

            const data: QueryResponse = await res.json();
            setResult(data);

            // Refresh stats
            fetch(`${API_BASE}/stats`)
                .then((r) => r.json())
                .then(setStats)
                .catch(() => { });
        } catch (e: any) {
            setError(e.message || "Something went wrong. Is the API server running?");
        } finally {
            setLoading(false);
        }
    }, [query, loading]);

    const handleIngest = async () => {
        if (!ingestSource.trim() || ingesting) return;
        setIngesting(true);
        setIngestResult(null);
        setIngestError(null);

        try {
            const res = await fetch(`${API_BASE}/ingest`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ source: ingestSource }),
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Ingestion failed");
            }

            const data: IngestResult = await res.json();
            setIngestResult(data);
            setIngestSource("");

            // Refresh stats
            fetch(`${API_BASE}/stats`)
                .then((r) => r.json())
                .then(setStats)
                .catch(() => { });
        } catch (e: any) {
            setIngestError(e.message || "Ingestion failed");
        } finally {
            setIngesting(false);
        }
    };

    const toggleSource = (refNum: number) => {
        setExpandedSources((prev) => {
            const next = new Set(prev);
            if (next.has(refNum)) {
                next.delete(refNum);
            } else {
                next.add(refNum);
            }
            return next;
        });
    };

    return (
        <>
            {/* Header */}
            <header className="header">
                <div className="app-container header-inner">
                    <div className="logo">
                        <div className="logo-icon">R</div>
                        <div className="logo-text">
                            RAG<span>System</span>
                        </div>
                    </div>
                    <div className="header-badge">Gemini Powered</div>
                </div>
            </header>

            <main className="app-container">
                {/* Hero */}
                <section className="hero">
                    <h1>Search Your Documents Intelligently</h1>
                    <p>
                        Ask questions across your ingested documents. Get cited, grounded answers with source verification.
                    </p>
                </section>

                {/* Stats */}
                {stats && (
                    <div className="stats-bar">
                        <div className="stat-card">
                            <div className="stat-value">{stats.vector_store_size}</div>
                            <div className="stat-label">Vector Chunks</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">{stats.bm25_index_size}</div>
                            <div className="stat-label">BM25 Index</div>
                        </div>
                    </div>
                )}

                {/* Search */}
                <div className="search-container">
                    <div className="search-bar">
                        <input
                            type="text"
                            placeholder="Ask a question about your documents..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && handleQuery()}
                            disabled={loading}
                        />
                        <button className="search-btn" onClick={handleQuery} disabled={loading || !query.trim()}>
                            {loading ? (
                                <>
                                    <div className="spinner" />
                                    Searching...
                                </>
                            ) : (
                                <>🔍 Search</>
                            )}
                        </button>
                    </div>
                </div>

                {/* Error */}
                {error && <div className="error-banner">⚠️ {error}</div>}

                {/* Answer */}
                {result && (
                    <>
                        <section className="answer-section">
                            <div className="answer-card">
                                <div className="answer-label">
                                    <span className="dot" />
                                    AI Answer
                                </div>
                                <div className="answer-text">{renderAnswerWithCitations(result.answer)}</div>

                                <div className="metrics-bar">
                                    <div className="metric-chip latency">
                                        <span className="icon">⚡</span>
                                        {result.latency_ms}ms
                                    </div>
                                    <div className="metric-chip tokens">
                                        <span className="icon">📊</span>
                                        {result.tokens_used} tokens
                                    </div>
                                    <div className="metric-chip model">
                                        <span className="icon">🤖</span>
                                        {result.model_used}
                                    </div>
                                </div>
                            </div>
                        </section>

                        {/* Sources */}
                        {result.citations.length > 0 && (
                            <section className="sources-section">
                                <div className="sources-label">
                                    Sources ({result.citations.length})
                                </div>
                                <div className="sources-grid">
                                    {result.citations.map((citation) => (
                                        <div
                                            key={citation.ref_number}
                                            className={`source-card ${expandedSources.has(citation.ref_number) ? "expanded" : ""}`}
                                            onClick={() => toggleSource(citation.ref_number)}
                                        >
                                            <div className="source-card-header">
                                                <span className="source-ref-badge">{citation.ref_number}</span>
                                                <span className="source-title">{citation.title}</span>
                                                <span className="source-toggle">
                                                    {expandedSources.has(citation.ref_number) ? "▲ Hide" : "▼ Show"}
                                                </span>
                                            </div>
                                            <div className="source-meta">
                                                {citation.source}
                                                {citation.page && ` · Page ${citation.page}`}
                                            </div>
                                            <div className="source-excerpt">{citation.excerpt}</div>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}
                    </>
                )}

                {/* Ingest Panel */}
                <section className="ingest-section">
                    <div className="ingest-card">
                        <div className="ingest-header">
                            <span>📄</span>
                            <h3>Ingest Document</h3>
                        </div>
                        <div className="ingest-form">
                            <input
                                className="ingest-input"
                                type="text"
                                placeholder="File path or URL (e.g. data/raw/report.pdf)"
                                value={ingestSource}
                                onChange={(e) => setIngestSource(e.target.value)}
                                onKeyDown={(e) => e.key === "Enter" && handleIngest()}
                                disabled={ingesting}
                            />
                            <button className="ingest-btn" onClick={handleIngest} disabled={ingesting || !ingestSource.trim()}>
                                {ingesting ? "Ingesting..." : "Ingest"}
                            </button>
                        </div>
                        {ingestResult && (
                            <div className="ingest-result success">
                                ✓ Ingested: {ingestResult.source} → {ingestResult.chunks_created} chunks (ID: {ingestResult.doc_id})
                            </div>
                        )}
                        {ingestError && (
                            <div className="ingest-result error">✗ {ingestError}</div>
                        )}
                    </div>
                </section>
            </main>
        </>
    );
}
