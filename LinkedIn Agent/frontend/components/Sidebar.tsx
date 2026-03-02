'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    Megaphone,
    Building2,
    Users,
    BarChart3,
    Zap,
    Shield,
    Settings,
} from 'lucide-react';

const NAV = [
    { href: '/', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/campaigns', label: 'Campaigns', icon: Megaphone },
    { href: '/companies', label: 'Companies', icon: Building2 },
    { href: '/leads', label: 'Leads', icon: Users },
    { href: '/analytics', label: 'Analytics', icon: BarChart3 },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside style={{
            width: 220,
            position: 'fixed',
            top: 0,
            left: 0,
            height: '100vh',
            background: '#0a0e17',
            borderRight: '1px solid #1e2a3a',
            display: 'flex',
            flexDirection: 'column',
            padding: '20px 12px',
            zIndex: 100,
        }}>
            {/* Logo */}
            <div style={{ padding: '8px 8px 24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{
                        width: 32, height: 32, borderRadius: 8,
                        background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        flexShrink: 0,
                    }}>
                        <Zap size={16} color="white" />
                    </div>
                    <div>
                        <div style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 700, fontSize: 13, color: '#f1f5f9', letterSpacing: '-0.02em' }}>
                            LI Agent
                        </div>
                        <div style={{ fontSize: 10, color: '#475569', fontWeight: 500 }}>Intelligence Stack</div>
                    </div>
                </div>
            </div>

            {/* Nav */}
            <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
                <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: '0.08em', color: '#334155', textTransform: 'uppercase', padding: '4px 12px 8px' }}>
                    Workspace
                </div>
                {NAV.map(({ href, label, icon: Icon }) => {
                    const active = pathname === href;
                    return (
                        <Link key={href} href={href} className={`nav-item ${active ? 'active' : ''}`}>
                            <Icon size={15} />
                            {label}
                        </Link>
                    );
                })}
            </nav>

            {/* Bottom */}
            <div style={{ borderTop: '1px solid #1e2a3a', paddingTop: 16, display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Link href="/safety" className="nav-item">
                    <Shield size={15} />
                    Safety
                </Link>
                <Link href="/settings" className="nav-item">
                    <Settings size={15} />
                    Settings
                </Link>

                {/* Live status */}
                <div style={{
                    margin: '12px 4px 0',
                    padding: '10px 12px',
                    background: '#0d1117',
                    border: '1px solid #1e2a3a',
                    borderRadius: 8,
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <div className="pulse-dot" />
                        <span style={{ fontSize: 12, color: '#10b981', fontWeight: 500 }}>Agents active</span>
                    </div>
                    <div style={{ fontSize: 11, color: '#475569', marginTop: 4 }}>Scanning signals...</div>
                </div>
            </div>
        </aside>
    );
}
