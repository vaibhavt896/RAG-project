'use client';

import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const FUNNEL = [
    { name: 'Total Leads', value: 187 },
    { name: 'Contacted', value: 64 },
    { name: 'Connected', value: 29 },
    { name: 'Replied', value: 8 },
];

const WEEKLY = [
    { week: 'Feb 3', connections: 4, msgs: 2, replies: 0 },
    { week: 'Feb 10', connections: 8, msgs: 5, replies: 1 },
    { week: 'Feb 17', connections: 12, msgs: 9, replies: 2 },
    { week: 'Feb 24', connections: 10, msgs: 11, replies: 3 },
    { week: 'Mar 2', connections: 14, msgs: 15, replies: 4 },
];

const BY_COMPANY = [
    { name: 'Anthropic', rate: 22 },
    { name: 'OpenAI', rate: 11 },
    { name: 'Notion', rate: 14 },
    { name: 'Linear', rate: 20 },
    { name: 'Vercel', rate: 0 },
];

const BY_ACTION = [
    { name: 'Connection', value: 45.3, color: '#3b82f6' },
    { name: 'Reply', value: 12.5, color: '#10b981' },
    { name: 'Email open', value: 28.0, color: '#8b5cf6' },
];

const tip = {
    contentStyle: { background: '#0d1117', border: '1px solid #1e2a3a', borderRadius: 8, color: '#94a3b8', fontSize: 12 },
    labelStyle: { color: '#f1f5f9', fontWeight: 600 },
};

export default function AnalyticsPage() {
    return (
        <div>
            <div style={{ marginBottom: 28 }}>
                <h1 style={{ fontSize: 24, fontFamily: 'Outfit, sans-serif', fontWeight: 700 }}>Analytics</h1>
                <p style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>Outreach performance and A/B insights</p>
            </div>

            {/* KPI Row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
                {[
                    { label: 'Acceptance Rate', value: '45.3%', delta: '+2.1%', color: '#3b82f6' },
                    { label: 'Reply Rate', value: '12.5%', delta: '+1.8%', color: '#10b981' },
                    { label: 'Email Open Rate', value: '28.0%', delta: '+3.2%', color: '#8b5cf6' },
                    { label: 'Avg Score', value: '71.4', delta: '+4.2', color: '#f59e0b' },
                ].map((k) => (
                    <div key={k.label} className="metric-card">
                        <div style={{ fontSize: 26, fontFamily: 'Outfit, sans-serif', fontWeight: 800, color: k.color, marginBottom: 4 }}>{k.value}</div>
                        <div style={{ fontSize: 12, color: '#64748b', marginBottom: 6 }}>{k.label}</div>
                        <div style={{ fontSize: 11, color: '#10b981', fontWeight: 500 }}>↑ {k.delta} this month</div>
                    </div>
                ))}
            </div>

            {/* Charts row 1 */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
                {/* Funnel bar */}
                <div className="glass-card" style={{ padding: 20 }}>
                    <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>Outreach Funnel</h3>
                    <p style={{ fontSize: 12, color: '#475569', marginBottom: 16 }}>All campaigns combined</p>
                    <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={FUNNEL} barSize={32}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e2a3a" vertical={false} />
                            <XAxis dataKey="name" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
                            <YAxis tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
                            <Tooltip {...tip} />
                            <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Weekly trend */}
                <div className="glass-card" style={{ padding: 20 }}>
                    <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>Weekly Activity</h3>
                    <p style={{ fontSize: 12, color: '#475569', marginBottom: 16 }}>Connections, messages, replies</p>
                    <ResponsiveContainer width="100%" height={200}>
                        <LineChart data={WEEKLY}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e2a3a" />
                            <XAxis dataKey="week" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
                            <YAxis tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} />
                            <Tooltip {...tip} />
                            <Line type="monotone" dataKey="connections" stroke="#3b82f6" strokeWidth={2} dot={false} />
                            <Line type="monotone" dataKey="msgs" stroke="#8b5cf6" strokeWidth={2} dot={false} />
                            <Line type="monotone" dataKey="replies" stroke="#10b981" strokeWidth={2} dot={false} />
                        </LineChart>
                    </ResponsiveContainer>
                    <div style={{ display: 'flex', gap: 16, marginTop: 12, justifyContent: 'center' }}>
                        {[['#3b82f6', 'Connections'], ['#8b5cf6', 'Messages'], ['#10b981', 'Replies']].map(([c, l]) => (
                            <div key={l} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                                <div style={{ width: 10, height: 2, background: c, borderRadius: 1 }} />
                                <span style={{ fontSize: 11, color: '#475569' }}>{l}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Charts row 2 */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 20 }}>
                {/* Reply rate by company */}
                <div className="glass-card" style={{ padding: 20 }}>
                    <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>Reply Rate by Company</h3>
                    <p style={{ fontSize: 12, color: '#475569', marginBottom: 16 }}>Which companies respond most</p>
                    <ResponsiveContainer width="100%" height={180}>
                        <BarChart data={BY_COMPANY} layout="vertical" barSize={16}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1e2a3a" horizontal={false} />
                            <XAxis type="number" tick={{ fill: '#475569', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} />
                            <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} width={70} />
                            <Tooltip {...tip} formatter={(v: number | string | undefined) => [`${v ?? 0}%`, 'Reply Rate']} />
                            <Bar dataKey="rate" fill="#10b981" radius={[0, 4, 4, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Donut */}
                <div className="glass-card" style={{ padding: 20 }}>
                    <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>Engagement Mix</h3>
                    <p style={{ fontSize: 12, color: '#475569', marginBottom: 16 }}>Rate breakdown</p>
                    <ResponsiveContainer width="100%" height={140}>
                        <PieChart>
                            <Pie data={BY_ACTION} cx="50%" cy="50%" innerRadius={40} outerRadius={60} dataKey="value" strokeWidth={0}>
                                {BY_ACTION.map((e, i) => <Cell key={i} fill={e.color} />)}
                            </Pie>
                            <Tooltip {...tip} formatter={(v: number | string | undefined) => [`${v ?? 0}%`]} />
                        </PieChart>
                    </ResponsiveContainer>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
                        {BY_ACTION.map((a) => (
                            <div key={a.name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: a.color }} />
                                    <span style={{ fontSize: 12, color: '#64748b' }}>{a.name}</span>
                                </div>
                                <span style={{ fontSize: 12, fontWeight: 600, color: '#94a3b8' }}>{a.value}%</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
