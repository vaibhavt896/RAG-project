'use client';

import { useState } from 'react';
import { Megaphone, Play, Pause, Plus, Trash2, Target, Users, MessageSquare } from 'lucide-react';

type Campaign = {
    id: string; name: string; status: string;
    total_leads: number; leads_contacted: number; replies_received: number;
    connections_accepted: number; target_role: string; created_at: string;
};

const DEMO: Campaign[] = [
    { id: '1', name: 'Anthropic Fall Outreach', status: 'active', total_leads: 12, leads_contacted: 8, replies_received: 2, connections_accepted: 5, target_role: 'ML Engineer', created_at: '2026-02-20' },
    { id: '2', name: 'OpenAI / Research Labs', status: 'paused', total_leads: 9, leads_contacted: 4, replies_received: 1, connections_accepted: 2, target_role: 'Research Engineer', created_at: '2026-02-15' },
    { id: '3', name: 'Startup Series B Push', status: 'draft', total_leads: 0, leads_contacted: 0, replies_received: 0, connections_accepted: 0, target_role: 'Software Engineer', created_at: '2026-03-01' },
];

const STATUS_PILL: Record<string, string> = { active: 'pill-green', paused: 'pill-orange', draft: 'pill-gray', completed: 'pill-blue' };

export default function CampaignsPage() {
    const [campaigns, setCampaigns] = useState<Campaign[]>(DEMO);
    const [showNew, setShowNew] = useState(false);
    const [newName, setNewName] = useState('');
    const [newRole, setNewRole] = useState('');

    function handleCreate() {
        if (!newName.trim()) return;
        setCampaigns((prev) => [...prev, {
            id: String(Date.now()), name: newName, status: 'draft',
            total_leads: 0, leads_contacted: 0, replies_received: 0, connections_accepted: 0,
            target_role: newRole, created_at: new Date().toISOString().slice(0, 10),
        }]);
        setNewName(''); setNewRole(''); setShowNew(false);
    }

    function toggleStatus(id: string) {
        setCampaigns((prev) => prev.map((c) =>
            c.id === id ? { ...c, status: c.status === 'active' ? 'paused' : 'active' } : c
        ));
    }

    function remove(id: string) { setCampaigns((prev) => prev.filter((c) => c.id !== id)); }

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
                <div>
                    <h1 style={{ fontSize: 24, fontFamily: 'Outfit, sans-serif', fontWeight: 700 }}>Campaigns</h1>
                    <p style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>Manage your outreach sequences</p>
                </div>
                <button className="btn-primary" onClick={() => setShowNew(true)}>
                    <Plus size={14} /> New Campaign
                </button>
            </div>

            {/* New campaign form */}
            {showNew && (
                <div className="glass-card" style={{ padding: 20, marginBottom: 20 }}>
                    <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14 }}>Create Campaign</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
                        <div>
                            <label style={{ fontSize: 11, color: '#475569', fontWeight: 600, display: 'block', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Campaign Name</label>
                            <input value={newName} onChange={(e) => setNewName(e.target.value)}
                                placeholder="e.g. Anthropic Q2 Outreach"
                                style={{ width: '100%', background: '#080b12', border: '1px solid #1e2a3a', borderRadius: 8, padding: '8px 12px', color: '#f1f5f9', fontSize: 13, outline: 'none' }} />
                        </div>
                        <div>
                            <label style={{ fontSize: 11, color: '#475569', fontWeight: 600, display: 'block', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Target Role</label>
                            <input value={newRole} onChange={(e) => setNewRole(e.target.value)}
                                placeholder="e.g. ML Engineer"
                                style={{ width: '100%', background: '#080b12', border: '1px solid #1e2a3a', borderRadius: 8, padding: '8px 12px', color: '#f1f5f9', fontSize: 13, outline: 'none' }} />
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: 8 }}>
                        <button className="btn-primary" onClick={handleCreate}>Create</button>
                        <button className="btn-ghost" onClick={() => setShowNew(false)}>Cancel</button>
                    </div>
                </div>
            )}

            {/* Campaign cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {campaigns.map((c) => (
                    <div key={c.id} className="glass-card" style={{ padding: '18px 20px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                <div style={{ width: 38, height: 38, borderRadius: 9, background: '#3b82f618', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <Megaphone size={16} color="#3b82f6" />
                                </div>
                                <div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <span style={{ fontSize: 14, fontWeight: 600, color: '#f1f5f9' }}>{c.name}</span>
                                        <span className={`pill ${STATUS_PILL[c.status] ?? 'pill-gray'}`}>{c.status}</span>
                                    </div>
                                    <div style={{ fontSize: 12, color: '#475569', marginTop: 2 }}>
                                        {c.target_role} · Created {c.created_at}
                                    </div>
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: 6 }}>
                                {c.status !== 'draft' && (
                                    <button className="btn-ghost" onClick={() => toggleStatus(c.id)}
                                        style={{ padding: '6px 10px' }}>
                                        {c.status === 'active' ? <Pause size={13} /> : <Play size={13} />}
                                        {c.status === 'active' ? 'Pause' : 'Resume'}
                                    </button>
                                )}
                                {c.status === 'draft' && (
                                    <button className="btn-primary" style={{ padding: '6px 12px', fontSize: 12 }}
                                        onClick={() => toggleStatus(c.id)}>
                                        <Play size={12} /> Launch
                                    </button>
                                )}
                                <button className="btn-ghost" style={{ padding: '6px 8px', color: '#ef444460', borderColor: '#ef444430' }}
                                    onClick={() => remove(c.id)}>
                                    <Trash2 size={13} />
                                </button>
                            </div>
                        </div>

                        {/* Stats */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginTop: 16, paddingTop: 16, borderTop: '1px solid #1e2a3a' }}>
                            {[
                                { label: 'Leads', value: c.total_leads, icon: Users, color: '#3b82f6' },
                                { label: 'Contacted', value: c.leads_contacted, icon: Target, color: '#8b5cf6' },
                                { label: 'Connected', value: c.connections_accepted, icon: Users, color: '#10b981' },
                                { label: 'Replies', value: c.replies_received, icon: MessageSquare, color: '#f59e0b' },
                            ].map((s) => (
                                <div key={s.label} style={{ textAlign: 'center' }}>
                                    <div style={{ fontSize: 20, fontFamily: 'Outfit, sans-serif', fontWeight: 700, color: s.color }}>{s.value}</div>
                                    <div style={{ fontSize: 11, color: '#475569', marginTop: 2 }}>{s.label}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
