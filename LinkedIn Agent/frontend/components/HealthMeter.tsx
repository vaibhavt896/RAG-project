'use client';

import { type HealthReport } from '@/lib/api';

interface Props { report: HealthReport; }

export default function HealthMeter({ report }: Props) {
    const score = report.health_score;
    const radius = 60;
    const circumference = 2 * Math.PI * radius;
    const progress = circumference - (score / 100) * circumference;

    const color =
        report.status === 'healthy' ? '#10b981' :
            report.status === 'caution' ? '#f59e0b' : '#ef4444';

    const metrics = [
        { label: 'Connections sent', value: report.metrics.connections_sent_30d },
        { label: 'Accepted', value: report.metrics.connections_accepted_30d },
        { label: 'Messages sent', value: report.metrics.messages_sent_30d },
        { label: 'Replies', value: report.metrics.messages_replied_30d },
        { label: 'Active days / 30', value: report.metrics.days_active_30d },
    ];

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
            {/* Radial gauge */}
            <div style={{ position: 'relative', width: 160, height: 160 }}>
                <svg width={160} height={160} style={{ transform: 'rotate(-90deg)' }}>
                    {/* Track */}
                    <circle cx={80} cy={80} r={radius} fill="none" stroke="#1e2a3a" strokeWidth={10} />
                    {/* Progress */}
                    <circle
                        cx={80} cy={80} r={radius}
                        fill="none"
                        stroke={color}
                        strokeWidth={10}
                        strokeDasharray={circumference}
                        strokeDashoffset={progress}
                        strokeLinecap="round"
                        className="health-ring"
                        style={{ transition: 'stroke-dashoffset 1s ease', color }}
                    />
                </svg>
                {/* Center text */}
                <div style={{
                    position: 'absolute', inset: 0, display: 'flex',
                    flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                }}>
                    <div style={{ fontSize: 28, fontFamily: 'Outfit, sans-serif', fontWeight: 800, color }}>{score}</div>
                    <div style={{ fontSize: 10, color: '#475569', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Score</div>
                </div>
            </div>

            {/* Status pill */}
            <div className={`pill ${report.status === 'healthy' ? 'pill-green' : report.status === 'caution' ? 'pill-orange' : 'pill-red'}`}>
                <div style={{ width: 5, height: 5, borderRadius: '50%', background: 'currentColor' }} />
                {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
            </div>

            {/* Metrics */}
            <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 6 }}>
                {metrics.map((m) => (
                    <div key={m.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: 11, color: '#475569' }}>{m.label}</span>
                        <span style={{ fontSize: 12, fontWeight: 600, color: '#94a3b8' }}>{m.value}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
