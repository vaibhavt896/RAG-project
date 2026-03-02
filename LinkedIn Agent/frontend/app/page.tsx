'use client';

import { useEffect, useState } from 'react';
import {
  Activity, TrendingUp, Users, Building2, Zap,
  ArrowUpRight, MessageSquare, UserCheck, Target, ChevronRight,
} from 'lucide-react';
import { analyticsApi, safetyApi, DEFAULT_USER_ID, type FunnelMetrics, type HealthReport, type OutreachAction, type CompanyStats } from '@/lib/api';
import HealthMeter from '@/components/HealthMeter';
import ActivityFeed from '@/components/ActivityFeed';
import SignalRadar from '@/components/SignalRadar';

export default function DashboardPage() {
  const [funnel, setFunnel] = useState<FunnelMetrics | null>(null);
  const [health, setHealth] = useState<HealthReport | null>(null);
  const [activity, setActivity] = useState<OutreachAction[]>([]);
  const [companyStats, setCompanyStats] = useState<CompanyStats[]>([]);

  useEffect(() => {
    const uid = DEFAULT_USER_ID;

    // Fetch all data in parallel — gracefully handle backend being offline
    Promise.allSettled([
      analyticsApi.funnel(uid).then(setFunnel),
      safetyApi.health(uid).then(setHealth),
      analyticsApi.activity(uid, 10).then(setActivity),
      analyticsApi.companyStats(uid).then(setCompanyStats),
    ]).catch(() => { });

    // Demo data so dashboard looks great even without backend
    setFunnel({ total_leads: 187, contacted: 64, connected: 29, replied: 8, connection_rate: 45.3, reply_rate: 12.5 });
    setHealth({ health_score: 82, status: 'healthy', metrics: { connections_sent_30d: 68, connections_accepted_30d: 31, messages_sent_30d: 42, messages_replied_30d: 7, days_active_30d: 19 } });
    setActivity([
      { id: '1', lead_id: 'l1', action_type: 'send_connection', sequence_day: 6, content: null, outcome: 'sent', executed_at: new Date().toISOString(), created_at: new Date().toISOString() },
      { id: '2', lead_id: 'l2', action_type: 'like_post', sequence_day: 0, content: null, outcome: 'sent', executed_at: new Date(Date.now() - 900000).toISOString(), created_at: new Date().toISOString() },
      { id: '3', lead_id: 'l3', action_type: 'send_message', sequence_day: 9, content: 'Message sent', outcome: 'sent', executed_at: new Date(Date.now() - 1800000).toISOString(), created_at: new Date().toISOString() },
      { id: '4', lead_id: 'l4', action_type: 'follow_company', sequence_day: 2, content: null, outcome: 'sent', executed_at: new Date(Date.now() - 3600000).toISOString(), created_at: new Date().toISOString() },
      { id: '5', lead_id: 'l5', action_type: 'send_email', sequence_day: 21, content: null, outcome: 'sent', executed_at: new Date(Date.now() - 7200000).toISOString(), created_at: new Date().toISOString() },
    ]);
    setCompanyStats([
      { company_id: '1', company_name: 'Anthropic', signal_score: 85, signal_type: 'funding', total_leads: 12, replies: 2, priority: 'high' },
      { company_id: '2', company_name: 'OpenAI', signal_score: 70, signal_type: 'hiring_push', total_leads: 9, replies: 1, priority: 'high' },
      { company_id: '3', company_name: 'Notion', signal_score: 65, signal_type: 'job_posting_spike', total_leads: 7, replies: 0, priority: 'medium' },
      { company_id: '4', company_name: 'Linear', signal_score: 50, signal_type: 'hiring_push', total_leads: 5, replies: 1, priority: 'medium' },
    ]);
  }, []);

  const metrics = [
    { label: 'Total Leads', value: funnel?.total_leads ?? '—', icon: Users, color: '#3b82f6', change: '+24 this week' },
    { label: 'Connected', value: funnel?.connected ?? '—', icon: UserCheck, color: '#10b981', change: `${funnel?.connection_rate ?? '—'}% rate` },
    { label: 'Replied', value: funnel?.replied ?? '—', icon: MessageSquare, color: '#8b5cf6', change: `${funnel?.reply_rate ?? '—'}% rate` },
    { label: 'Active Campaigns', value: '3', icon: Target, color: '#f59e0b', change: '2 companies pending' },
  ];

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 24, fontFamily: 'Outfit, sans-serif', fontWeight: 700, marginBottom: 4 }}>
          Command Center
        </h1>
        <p style={{ color: '#64748b', fontSize: 13 }}>
          Signal-first outreach running. Monday, 9:12 AM — inside working hours.
        </p>
      </div>

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        {metrics.map((m) => (
          <div key={m.label} className="metric-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
              <div style={{ width: 36, height: 36, borderRadius: 8, background: `${m.color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <m.icon size={16} color={m.color} />
              </div>
              <ArrowUpRight size={14} color="#10b981" />
            </div>
            <div style={{ fontSize: 28, fontFamily: 'Outfit, sans-serif', fontWeight: 700, color: '#f1f5f9', marginBottom: 2 }}>{m.value}</div>
            <div style={{ fontSize: 12, color: '#64748b' }}>{m.label}</div>
            <div style={{ fontSize: 11, color: m.color, marginTop: 4, fontWeight: 500 }}>{m.change}</div>
          </div>
        ))}
      </div>

      {/* Main Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 300px', gap: 20 }}>
        {/* Activity Feed */}
        <div className="glass-card" style={{ padding: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div>
              <h3 style={{ fontSize: 14, fontWeight: 600 }}>Activity Feed</h3>
              <div style={{ fontSize: 11, color: '#475569', marginTop: 2 }}>Real-time agent actions</div>
            </div>
            <div className="pill pill-green">Live</div>
          </div>
          <ActivityFeed actions={activity} />
        </div>

        {/* Signal Radar */}
        <div className="glass-card" style={{ padding: 20 }}>
          <div style={{ marginBottom: 16 }}>
            <h3 style={{ fontSize: 14, fontWeight: 600 }}>Signal Radar</h3>
            <div style={{ fontSize: 11, color: '#475569', marginTop: 2 }}>Companies ranked by signal strength</div>
          </div>
          <SignalRadar companies={companyStats} />
        </div>

        {/* Health Meter */}
        <div className="glass-card" style={{ padding: 20 }}>
          <div style={{ marginBottom: 16 }}>
            <h3 style={{ fontSize: 14, fontWeight: 600 }}>Account Health</h3>
            <div style={{ fontSize: 11, color: '#475569', marginTop: 2 }}>Safety score</div>
          </div>
          {health && <HealthMeter report={health} />}
        </div>
      </div>

      {/* Funnel */}
      {funnel && (
        <div className="glass-card" style={{ padding: 20, marginTop: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>Outreach Funnel</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
            {[
              { label: 'Total Leads', value: funnel.total_leads, pct: 100, color: '#3b82f6' },
              { label: 'Contacted', value: funnel.contacted, pct: Math.round(funnel.contacted / funnel.total_leads * 100), color: '#8b5cf6' },
              { label: 'Connected', value: funnel.connected, pct: Math.round(funnel.connected / funnel.total_leads * 100), color: '#10b981' },
              { label: 'Replied', value: funnel.replied, pct: Math.round(funnel.replied / funnel.total_leads * 100), color: '#f59e0b' },
            ].map((s) => (
              <div key={s.label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 22, fontFamily: 'Outfit, sans-serif', fontWeight: 700, color: s.color, marginBottom: 4 }}>{s.value}</div>
                <div style={{ fontSize: 11, color: '#64748b', marginBottom: 8 }}>{s.label}</div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ '--width': `${s.pct}%`, width: `${s.pct}%`, background: s.color } as React.CSSProperties} />
                </div>
                <div style={{ fontSize: 10, color: '#475569', marginTop: 4 }}>{s.pct}%</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
