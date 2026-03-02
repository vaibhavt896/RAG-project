'use client';

import { useState } from 'react';
import { Building2, Plus, Trash2, Zap, TrendingUp, Briefcase, RefreshCw } from 'lucide-react';

type Company = {
    id: string; company_name: string; domain: string;
    signal_score: number; signal_type: string | null; signal_detail: string | null;
    total_leads: number; priority: string; status: string; last_scanned_at: string | null;
};

const DEMO: Company[] = [
    { id: '1', company_name: 'Anthropic', domain: 'anthropic.com', signal_score: 85, signal_type: 'funding', signal_detail: 'Anthropic raises $4B Series E', total_leads: 12, priority: 'high', status: 'active', last_scanned_at: '2026-03-02' },
    { id: '2', company_name: 'OpenAI', domain: 'openai.com', signal_score: 70, signal_type: 'hiring_push', signal_detail: 'OpenAI expanding engineering team', total_leads: 9, priority: 'high', status: 'active', last_scanned_at: '2026-03-02' },
    { id: '3', company_name: 'Notion', domain: 'notion.so', signal_score: 65, signal_type: 'job_posting_spike', signal_detail: '8 new relevant roles posted recently', total_leads: 7, priority: 'medium', status: 'watching', last_scanned_at: '2026-03-01' },
    { id: '4', company_name: 'Linear', domain: 'linear.app', signal_score: 50, signal_type: 'hiring_push', signal_detail: 'Linear hiring in 2026', total_leads: 5, priority: 'medium', status: 'watching', last_scanned_at: '2026-02-28' },
    { id: '5', company_name: 'Vercel', domain: 'vercel.com', signal_score: 0, signal_type: null, signal_detail: null, total_leads: 0, priority: 'low', status: 'watching', last_scanned_at: null },
];

const SIGNAL_COLOR: Record<string, string> = { funding: '#10b981', hiring_push: '#3b82f6', job_posting_spike: '#f59e0b' };
const SIGNAL_ICON: Record<string, React.ComponentType<{ size: number; color: string }>> = { funding: TrendingUp, hiring_push: Zap, job_posting_spike: Briefcase };
const PRIORITY_DOT: Record<string, string> = { high: '#ef4444', medium: '#f59e0b', low: '#334155' };

export default function CompaniesPage() {
    const [companies, setCompanies] = useState<Company[]>(DEMO);
    const [showNew, setShowNew] = useState(false);
    const [name, setName] = useState(''); const [domain, setDomain] = useState('');
    const [scanning, setScanning] = useState<string | null>(null);

    function handleAdd() {
        if (!name.trim()) return;
        setCompanies((prev) => [...prev, {
            id: String(Date.now()), company_name: name, domain,
            signal_score: 0, signal_type: null, signal_detail: null,
            total_leads: 0, priority: 'medium', status: 'watching', last_scanned_at: null,
        }]);
        setName(''); setDomain(''); setShowNew(false);
    }

    function handleScan(id: string) {
        setScanning(id);
        setTimeout(() => setScanning(null), 2500);
    }

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
                <div>
                    <h1 style={{ fontSize: 24, fontFamily: 'Outfit, sans-serif', fontWeight: 700 }}>Company Watchlist</h1>
                    <p style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>Monitored for funding, hiring, and job signals</p>
                </div>
                <button className="btn-primary" onClick={() => setShowNew(true)}><Plus size={14} /> Add Company</button>
            </div>

            {showNew && (
                <div className="glass-card" style={{ padding: 20, marginBottom: 20 }}>
                    <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14 }}>Add Company</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
                        {[['Company name', name, setName, 'e.g. Stripe'], ['Domain', domain, setDomain, 'e.g. stripe.com']].map(([label, val, setter, ph]) => (
                            <div key={label as string}>
                                <label style={{ fontSize: 11, color: '#475569', fontWeight: 600, display: 'block', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label as string}</label>
                                <input value={val as string} onChange={(e) => (setter as (v: string) => void)(e.target.value)}
                                    placeholder={ph as string}
                                    style={{ width: '100%', background: '#080b12', border: '1px solid #1e2a3a', borderRadius: 8, padding: '8px 12px', color: '#f1f5f9', fontSize: 13, outline: 'none' }} />
                            </div>
                        ))}
                    </div>
                    <div style={{ display: 'flex', gap: 8 }}>
                        <button className="btn-primary" onClick={handleAdd}>Add</button>
                        <button className="btn-ghost" onClick={() => setShowNew(false)}>Cancel</button>
                    </div>
                </div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {companies.map((c) => {
                    const SigIcon = c.signal_type ? (SIGNAL_ICON[c.signal_type] ?? Zap) : Building2;
                    const sigColor = c.signal_type ? (SIGNAL_COLOR[c.signal_type] ?? '#64748b') : '#334155';
                    return (
                        <div key={c.id} className="glass-card" style={{ padding: '16px 20px', display: 'grid', gridTemplateColumns: 'auto 1fr auto auto', gap: 16, alignItems: 'center' }}>
                            {/* Icon */}
                            <div style={{ width: 40, height: 40, borderRadius: 10, background: `${sigColor}18`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <SigIcon size={16} color={sigColor} />
                            </div>

                            {/* Info */}
                            <div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3 }}>
                                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: PRIORITY_DOT[c.priority] ?? '#334155' }} />
                                    <span style={{ fontSize: 14, fontWeight: 600, color: '#f1f5f9' }}>{c.company_name}</span>
                                    {c.domain && <span style={{ fontSize: 11, color: '#334155' }}>{c.domain}</span>}
                                    {c.signal_score > 0 && (
                                        <span className={`pill ${c.signal_type === 'funding' ? 'pill-green' : c.signal_type === 'hiring_push' ? 'pill-blue' : 'pill-orange'}`}>
                                            {c.signal_type?.replace('_', ' ')}
                                        </span>
                                    )}
                                </div>
                                <div style={{ fontSize: 12, color: '#475569' }}>
                                    {c.signal_detail ?? 'No signal detected yet'}
                                    {c.last_scanned_at && <span style={{ marginLeft: 8, color: '#334155' }}>· scanned {c.last_scanned_at}</span>}
                                </div>
                            </div>

                            {/* Stats */}
                            <div style={{ display: 'flex', gap: 20, textAlign: 'center' }}>
                                <div>
                                    <div style={{ fontSize: 16, fontFamily: 'Outfit, sans-serif', fontWeight: 700, color: sigColor }}>{c.signal_score}</div>
                                    <div style={{ fontSize: 10, color: '#334155' }}>Signal</div>
                                </div>
                                <div>
                                    <div style={{ fontSize: 16, fontFamily: 'Outfit, sans-serif', fontWeight: 700, color: '#94a3b8' }}>{c.total_leads}</div>
                                    <div style={{ fontSize: 10, color: '#334155' }}>Leads</div>
                                </div>
                            </div>

                            {/* Actions */}
                            <div style={{ display: 'flex', gap: 6 }}>
                                <button className="btn-ghost" style={{ padding: '6px 10px', fontSize: 12 }}
                                    onClick={() => handleScan(c.id)}>
                                    <RefreshCw size={12} style={{ animation: scanning === c.id ? 'spin 1s linear infinite' : undefined }} />
                                    {scanning === c.id ? 'Scanning...' : 'Scan'}
                                </button>
                                <button className="btn-ghost" style={{ padding: '6px 8px', color: '#ef444460', borderColor: '#ef444430' }}
                                    onClick={() => setCompanies((p) => p.filter((x) => x.id !== c.id))}>
                                    <Trash2 size={13} />
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>

            <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
        </div>
    );
}
