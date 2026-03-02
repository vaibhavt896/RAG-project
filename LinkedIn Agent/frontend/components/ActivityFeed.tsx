'use client';

import { type OutreachAction } from '@/lib/api';
import { Heart, UserPlus, MessageSquare, Building2, Mail, Eye } from 'lucide-react';

interface Props { actions: OutreachAction[]; }

const ACTION_CONFIG: Record<string, { label: string; icon: React.ComponentType<{ size: number; color: string }>; color: string }> = {
    like_post: { label: 'Liked post', icon: Heart, color: '#ec4899' },
    follow_company: { label: 'Followed company', icon: Building2, color: '#8b5cf6' },
    send_connection: { label: 'Sent connection', icon: UserPlus, color: '#3b82f6' },
    send_message: { label: 'Sent message', icon: MessageSquare, color: '#10b981' },
    send_email: { label: 'Sent email', icon: Mail, color: '#f59e0b' },
    comment_post: { label: 'Commented on post', icon: MessageSquare, color: '#06b6d4' },
    profile_view: { label: 'Viewed profile', icon: Eye, color: '#64748b' },
};

function timeAgo(dateStr: string): string {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
}

export default function ActivityFeed({ actions }: Props) {
    if (!actions.length) {
        return (
            <div style={{ textAlign: 'center', padding: '32px 0', color: '#334155' }}>
                <MessageSquare size={28} color="#1e2a3a" style={{ marginBottom: 8 }} />
                <div style={{ fontSize: 13 }}>No activity yet</div>
            </div>
        );
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {actions.map((action) => {
                const cfg = ACTION_CONFIG[action.action_type] ?? ACTION_CONFIG.profile_view;
                const Icon = cfg.icon;
                return (
                    <div
                        key={action.id}
                        style={{
                            display: 'flex', alignItems: 'center', gap: 10,
                            padding: '10px 8px', borderRadius: 8,
                            transition: 'background 0.15s',
                            cursor: 'default',
                        }}
                        onMouseEnter={(e) => { (e.currentTarget as HTMLDivElement).style.background = '#111722'; }}
                        onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.background = 'transparent'; }}
                    >
                        {/* Icon */}
                        <div style={{
                            width: 30, height: 30, borderRadius: 8, flexShrink: 0,
                            background: `${cfg.color}18`,
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                        }}>
                            <Icon size={13} color={cfg.color} />
                        </div>

                        {/* Text */}
                        <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ fontSize: 12.5, color: '#e2e8f0', fontWeight: 500 }}>{cfg.label}</div>
                            <div style={{ fontSize: 11, color: '#334155', marginTop: 1 }}>
                                Day {action.sequence_day}
                                {action.outcome === 'failed' && <span style={{ color: '#ef4444', marginLeft: 6 }}>· failed</span>}
                            </div>
                        </div>

                        {/* Time */}
                        <div style={{ fontSize: 10.5, color: '#334155', flexShrink: 0 }}>
                            {action.executed_at ? timeAgo(action.executed_at) : '—'}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
