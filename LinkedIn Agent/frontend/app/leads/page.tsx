'use client';

import { useState } from 'react';
import { Users, Mail, ExternalLink, Filter, Search } from 'lucide-react';

type Lead = {
    id: string; full_name: string; title: string; company: string;
    linkedin_url: string; email: string | null; score: number;
    outreach_status: string; sequence_day: number; persona_type: string;
};

const DEMO: Lead[] = [
    { id: '1', full_name: 'Sarah Chen', title: 'Senior Technical Recruiter', company: 'Anthropic', linkedin_url: '#', email: 'sarah.chen@anthropic.com', score: 88, outreach_status: 'replied', sequence_day: 9, persona_type: 'recruiter' },
    { id: '2', full_name: 'Marcus Williams', title: 'Head of Talent Acquisition', company: 'Anthropic', linkedin_url: '#', email: null, score: 82, outreach_status: 'active', sequence_day: 6, persona_type: 'recruiter' },
    { id: '3', full_name: 'Priya Nair', title: 'Engineering Manager', company: 'OpenAI', linkedin_url: '#', email: 'p.nair@openai.com', score: 75, outreach_status: 'active', sequence_day: 4, persona_type: 'hiring_mgr' },
    { id: '4', full_name: 'James Park', title: 'Talent Partner', company: 'OpenAI', linkedin_url: '#', email: null, score: 71, outreach_status: 'queued', sequence_day: 0, persona_type: 'recruiter' },
    { id: '5', full_name: 'Alex Rivera', title: 'HRBP', company: 'Notion', linkedin_url: '#', email: 'alex@notion.so', score: 63, outreach_status: 'active', sequence_day: 2, persona_type: 'hrbp' },
    { id: '6', full_name: 'Dana Kim', title: 'Sourcer', company: 'Linear', linkedin_url: '#', email: null, score: 55, outreach_status: 'queued', sequence_day: 0, persona_type: 'recruiter' },
];

const STATUS_PILL: Record<string, string> = { replied: 'pill-green', active: 'pill-blue', queued: 'pill-gray', paused: 'pill-orange', completed: 'pill-purple' };
const PERSONA_PILL: Record<string, string> = { recruiter: 'pill-blue', hiring_mgr: 'pill-purple', hrbp: 'pill-orange', exec: 'pill-red' };
const SEQ_LABEL: Record<number, string> = { 0: 'Like post', 2: 'Follow co.', 4: 'Comment', 6: 'Connect', 9: 'Message 1', 14: 'Message 2', 21: 'Email' };

function ScoreBar({ score }: { score: number }) {
    const color = score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444';
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ fontSize: 13, fontWeight: 700, color, width: 28 }}>{score}</div>
            <div className="progress-bar" style={{ width: 48 }}>
                <div className="progress-fill" style={{ '--width': `${score}%`, width: `${score}%`, background: color } as React.CSSProperties} />
            </div>
        </div>
    );
}

export default function LeadsPage() {
    const [leads] = useState<Lead[]>(DEMO);
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('all');

    const filtered = leads.filter((l) => {
        const matchSearch = !search ||
            l.full_name.toLowerCase().includes(search.toLowerCase()) ||
            l.company.toLowerCase().includes(search.toLowerCase()) ||
            l.title.toLowerCase().includes(search.toLowerCase());
        const matchFilter = filter === 'all' || l.outreach_status === filter;
        return matchSearch && matchFilter;
    });

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
                <div>
                    <h1 style={{ fontSize: 24, fontFamily: 'Outfit, sans-serif', fontWeight: 700 }}>Leads</h1>
                    <p style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>{leads.length} contacts tracked across {new Set(leads.map((l) => l.company)).size} companies</p>
                </div>
            </div>

            {/* Filters */}
            <div style={{ display: 'flex', gap: 10, marginBottom: 20, alignItems: 'center' }}>
                <div style={{ position: 'relative', flex: 1, maxWidth: 300 }}>
                    <Search size={13} color="#475569" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)' }} />
                    <input value={search} onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search leads..."
                        style={{ width: '100%', background: '#0d1117', border: '1px solid #1e2a3a', borderRadius: 8, padding: '8px 12px 8px 30px', color: '#f1f5f9', fontSize: 13, outline: 'none' }} />
                </div>
                <div style={{ display: 'flex', gap: 6 }}>
                    {['all', 'replied', 'active', 'queued'].map((s) => (
                        <button key={s} onClick={() => setFilter(s)}
                            style={{
                                padding: '7px 12px', borderRadius: 7, fontSize: 12, fontWeight: 500, cursor: 'pointer', border: 'none', transition: 'all 0.15s',
                                background: filter === s ? '#3b82f6' : '#0d1117',
                                color: filter === s ? 'white' : '#64748b',
                                outline: '1px solid ' + (filter === s ? '#3b82f6' : '#1e2a3a'),
                            }}>
                            {s.charAt(0).toUpperCase() + s.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            {/* Table */}
            <div className="glass-card" style={{ overflow: 'hidden' }}>
                <table className="data-table">
                    <thead>
                        <tr>
                            <th style={{ textAlign: 'left' }}>Lead</th>
                            <th style={{ textAlign: 'left' }}>Company</th>
                            <th>Persona</th>
                            <th>Score</th>
                            <th>Status</th>
                            <th>Next Step</th>
                            <th>Email</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.map((lead) => (
                            <tr key={lead.id}>
                                <td>
                                    <div style={{ fontWeight: 500, color: '#f1f5f9', fontSize: 13 }}>{lead.full_name}</div>
                                    <div style={{ fontSize: 11, color: '#475569', marginTop: 1 }}>{lead.title}</div>
                                </td>
                                <td style={{ fontWeight: 500 }}>{lead.company}</td>
                                <td style={{ textAlign: 'center' }}>
                                    <span className={`pill ${PERSONA_PILL[lead.persona_type] ?? 'pill-gray'}`}>{lead.persona_type}</span>
                                </td>
                                <td><ScoreBar score={lead.score} /></td>
                                <td>
                                    <span className={`pill ${STATUS_PILL[lead.outreach_status] ?? 'pill-gray'}`}>{lead.outreach_status}</span>
                                </td>
                                <td style={{ fontSize: 11, color: '#475569' }}>{SEQ_LABEL[lead.sequence_day] ?? `Day ${lead.sequence_day}`}</td>
                                <td>
                                    {lead.email
                                        ? <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}><Mail size={11} color="#10b981" /><span style={{ fontSize: 11, color: '#10b981' }}>Found</span></div>
                                        : <span style={{ fontSize: 11, color: '#334155' }}>—</span>
                                    }
                                </td>
                                <td>
                                    <a href={lead.linkedin_url} target="_blank" rel="noreferrer" style={{ color: '#475569', display: 'inline-flex' }}>
                                        <ExternalLink size={13} />
                                    </a>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {filtered.length === 0 && (
                    <div style={{ textAlign: 'center', padding: '40px 0', color: '#334155' }}>No leads match your filter</div>
                )}
            </div>
        </div>
    );
}
