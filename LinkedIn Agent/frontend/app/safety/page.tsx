'use client';

import { useState, useEffect } from 'react';
import { Shield, HeartPulse, AlertTriangle, CheckCircle, Activity, Gauge } from 'lucide-react';
import HealthMeter from '@/components/HealthMeter';
import { safetyApi, DEFAULT_USER_ID, type HealthReport, type BudgetReport } from '@/lib/api';

export default function SafetyPage() {
    const [health, setHealth] = useState<HealthReport | null>(null);
    const [budget, setBudget] = useState<BudgetReport | null>(null);

    useEffect(() => {
        // Try live data, fall back to demo
        Promise.allSettled([
            safetyApi.health(DEFAULT_USER_ID).then(setHealth),
            safetyApi.budget(DEFAULT_USER_ID).then(setBudget),
        ]).catch(() => { });

        setHealth({
            health_score: 82,
            status: 'healthy',
            metrics: {
                connections_sent_30d: 68,
                connections_accepted_30d: 31,
                messages_sent_30d: 42,
                messages_replied_30d: 7,
                days_active_30d: 19,
            },
        });
        setBudget({
            warmup_phase: 3,
            health_score: 82,
            budget: {
                connections: { limit: 15, used: 6, remaining: 9 },
                messages: { limit: 20, used: 8, remaining: 12 },
                profile_views: { limit: 60, used: 22, remaining: 38 },
            },
        });
    }, []);

    const RULES = [
        { icon: Shield, label: 'Never log in for data collection — public scraper only', status: 'active' },
        { icon: HeartPulse, label: 'Health score < 50 = emergency pause on all activity', status: 'active' },
        { icon: Activity, label: '9AM–6PM only in your timezone — never overnight', status: 'active' },
        { icon: Gauge, label: 'Normal-distribution delays — never constant timing', status: 'active' },
        { icon: AlertTriangle, label: 'CAPTCHA detected = instant hard stop + alert', status: 'active' },
        { icon: Shield, label: '12% random offline days — humans skip days', status: 'active' },
    ];

    const WARMUP_PHASES = [
        { phase: 1, conns: 5, msgs: 5, views: 20, label: 'Week 1 — Crawl' },
        { phase: 2, conns: 10, msgs: 10, views: 40, label: 'Week 2 — Walk' },
        { phase: 3, conns: 15, msgs: 20, views: 60, label: 'Week 3 — Jog' },
        { phase: 4, conns: 20, msgs: 30, views: 80, label: 'Week 4 — Run' },
        { phase: 5, conns: 25, msgs: 35, views: 100, label: 'Week 5+ — Cruise' },
    ];

    return (
        <div>
            <div style={{ marginBottom: 28 }}>
                <h1 style={{ fontSize: 24, fontFamily: 'Outfit, sans-serif', fontWeight: 700 }}>Safety Center</h1>
                <p style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>Account protection, warmup schedule, and daily budgets</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: 20, marginBottom: 24 }}>
                {/* Health Meter */}
                <div className="glass-card" style={{ padding: 20 }}>
                    <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>Account Health</h3>
                    {health && <HealthMeter report={health} />}
                </div>

                {/* Today's Budget */}
                <div className="glass-card" style={{ padding: 20 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                        <div>
                            <h3 style={{ fontSize: 14, fontWeight: 600 }}>Today&#39;s Budget</h3>
                            <div style={{ fontSize: 11, color: '#475569', marginTop: 2 }}>
                                Phase {budget?.warmup_phase ?? '—'} · Health {budget?.health_score ?? '—'}
                            </div>
                        </div>
                        <div className={`pill ${health?.status === 'healthy' ? 'pill-green' : health?.status === 'caution' ? 'pill-orange' : 'pill-red'}`}>
                            {health?.status ?? '...'}
                        </div>
                    </div>

                    {budget && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                            {Object.entries(budget.budget).map(([key, val]) => {
                                const pct = Math.round((val.used / Math.max(val.limit, 1)) * 100);
                                const color = key === 'connections' ? '#3b82f6' : key === 'messages' ? '#10b981' : '#8b5cf6';
                                return (
                                    <div key={key}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                                            <span style={{ fontSize: 12.5, fontWeight: 500, color: '#e2e8f0', textTransform: 'capitalize' }}>{key.replace('_', ' ')}</span>
                                            <span style={{ fontSize: 12, color: '#475569' }}>{val.used} / {val.limit}</span>
                                        </div>
                                        <div className="progress-bar" style={{ height: 6 }}>
                                            <div className="progress-fill" style={{ '--width': `${pct}%`, width: `${pct}%`, background: color } as React.CSSProperties} />
                                        </div>
                                        <div style={{ fontSize: 10, color: '#334155', marginTop: 3 }}>{val.remaining} remaining today</div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>

            {/* Safety Rules */}
            <div className="glass-card" style={{ padding: 20, marginBottom: 20 }}>
                <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14 }}>Active Safety Rules</h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                    {RULES.map((rule) => (
                        <div key={rule.label} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', background: '#10b98108', border: '1px solid #10b98115', borderRadius: 8 }}>
                            <CheckCircle size={14} color="#10b981" />
                            <span style={{ fontSize: 12.5, color: '#94a3b8' }}>{rule.label}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Warmup Schedule */}
            <div className="glass-card" style={{ padding: 20 }}>
                <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14 }}>Warmup Ramp Schedule</h3>
                <table className="data-table">
                    <thead>
                        <tr>
                            <th style={{ textAlign: 'left' }}>Phase</th>
                            <th>Connections/day</th>
                            <th>Messages/day</th>
                            <th>Profile views/day</th>
                        </tr>
                    </thead>
                    <tbody>
                        {WARMUP_PHASES.map((p) => {
                            const isCurrent = p.phase === (budget?.warmup_phase ?? 1);
                            return (
                                <tr key={p.phase} style={isCurrent ? { background: '#3b82f610' } : {}}>
                                    <td>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                            {isCurrent && <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#3b82f6' }} />}
                                            <span style={{ fontWeight: isCurrent ? 600 : 400, color: isCurrent ? '#f1f5f9' : '#64748b' }}>{p.label}</span>
                                        </div>
                                    </td>
                                    <td style={{ textAlign: 'center', color: isCurrent ? '#3b82f6' : '#64748b', fontWeight: isCurrent ? 600 : 400 }}>{p.conns}</td>
                                    <td style={{ textAlign: 'center', color: isCurrent ? '#10b981' : '#64748b', fontWeight: isCurrent ? 600 : 400 }}>{p.msgs}</td>
                                    <td style={{ textAlign: 'center', color: isCurrent ? '#8b5cf6' : '#64748b', fontWeight: isCurrent ? 600 : 400 }}>{p.views}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
