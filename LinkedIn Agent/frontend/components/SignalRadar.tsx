'use client';

import { type CompanyStats } from '@/lib/api';
import { TrendingUp, Zap, Briefcase } from 'lucide-react';

interface Props { companies: CompanyStats[]; }

const SIGNAL_CONFIG: Record<string, { label: string; color: string; icon: React.ComponentType<{ size: number; color: string }> }> = {
    funding: { label: 'Funding', color: '#10b981', icon: TrendingUp },
    hiring_push: { label: 'Hiring surge', color: '#3b82f6', icon: Zap },
    job_posting_spike: { label: 'Job spike', color: '#f59e0b', icon: Briefcase },
    none: { label: 'No signal', color: '#334155', icon: Zap },
};

export default function SignalRadar({ companies }: Props) {
    if (!companies.length) {
        return (
            <div style={{ textAlign: 'center', padding: '32px 0', color: '#334155' }}>
                <div style={{ fontSize: 13 }}>No companies tracked yet</div>
            </div>
        );
    }

    const maxScore = Math.max(...companies.map((c) => c.signal_score), 1);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {companies.slice(0, 6).map((company) => {
                const cfg = SIGNAL_CONFIG[company.signal_type ?? 'none'] ?? SIGNAL_CONFIG.none;
                const Icon = cfg.icon;
                const pct = Math.round((company.signal_score / maxScore) * 100);

                return (
                    <div key={company.company_id}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 5 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                {/* Priority dot */}
                                <div style={{
                                    width: 6, height: 6, borderRadius: '50%',
                                    background: company.priority === 'high' ? '#ef4444' : company.priority === 'medium' ? '#f59e0b' : '#334155',
                                    flexShrink: 0,
                                }} />
                                <span style={{ fontSize: 12.5, fontWeight: 500, color: '#e2e8f0' }}>{company.company_name}</span>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                                    <Icon size={10} color={cfg.color} />
                                    <span style={{ fontSize: 10, color: cfg.color, fontWeight: 500 }}>{cfg.label}</span>
                                </div>
                                <span style={{ fontSize: 11, color: '#475569', marginLeft: 4 }}>{company.signal_score}</span>
                            </div>
                        </div>

                        {/* Bar */}
                        <div className="progress-bar">
                            <div
                                className="progress-fill"
                                style={{
                                    '--width': `${pct}%`,
                                    width: `${pct}%`,
                                    background: `linear-gradient(90deg, ${cfg.color}80, ${cfg.color})`,
                                } as React.CSSProperties}
                            />
                        </div>

                        {/* Lead count */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 3 }}>
                            <span style={{ fontSize: 10, color: '#334155' }}>{company.total_leads} leads tracked</span>
                            <span style={{ fontSize: 10, color: company.replies > 0 ? '#10b981' : '#334155' }}>
                                {company.replies} {company.replies === 1 ? 'reply' : 'replies'}
                            </span>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
