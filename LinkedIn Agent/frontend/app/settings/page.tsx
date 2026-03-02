'use client';

import { useState } from 'react';
import { Settings, Key, User, Clock, Upload, Globe, Bell, CheckCircle } from 'lucide-react';

type Config = {
    full_name: string;
    email: string;
    target_role: string;
    timezone: string;
    warmup_phase: number;
    linkedin_email: string;
    gemini_key_set: boolean;
    resume_uploaded: boolean;
    gmail_configured: boolean;
    apollo_key_set: boolean;
    hunter_key_set: boolean;
    skrapp_key_set: boolean;
};

const DEMO: Config = {
    full_name: '',
    email: '',
    target_role: '',
    timezone: 'Asia/Kolkata',
    warmup_phase: 1,
    linkedin_email: '',
    gemini_key_set: true,
    resume_uploaded: false,
    gmail_configured: false,
    apollo_key_set: false,
    hunter_key_set: false,
    skrapp_key_set: false,
};

function Field({ label, value, onChange, placeholder, type = 'text' }: {
    label: string; value: string; onChange: (v: string) => void; placeholder: string; type?: string;
}) {
    return (
        <div>
            <label style={{ fontSize: 11, color: '#475569', fontWeight: 600, display: 'block', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {label}
            </label>
            <input value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} type={type}
                style={{ width: '100%', background: '#080b12', border: '1px solid #1e2a3a', borderRadius: 8, padding: '9px 12px', color: '#f1f5f9', fontSize: 13, outline: 'none', transition: 'border-color 0.15s' }}
                onFocus={(e) => { e.currentTarget.style.borderColor = '#3b82f6'; }}
                onBlur={(e) => { e.currentTarget.style.borderColor = '#1e2a3a'; }}
            />
        </div>
    );
}

function StatusDot({ active }: { active: boolean }) {
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 7, height: 7, borderRadius: '50%', background: active ? '#10b981' : '#334155' }} />
            <span style={{ fontSize: 12, color: active ? '#10b981' : '#475569' }}>{active ? 'Configured' : 'Not set'}</span>
        </div>
    );
}

export default function SettingsPage() {
    const [config, setConfig] = useState<Config>(DEMO);
    const [saved, setSaved] = useState(false);

    function update(key: keyof Config, value: string | number) {
        setConfig((prev) => ({ ...prev, [key]: value }));
        setSaved(false);
    }

    function save() {
        setSaved(true);
        setTimeout(() => setSaved(false), 2500);
    }

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 28 }}>
                <div>
                    <h1 style={{ fontSize: 24, fontFamily: 'Outfit, sans-serif', fontWeight: 700 }}>Settings</h1>
                    <p style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>Agent configuration, credentials, and preferences</p>
                </div>
                <button className="btn-primary" onClick={save}>
                    {saved ? <><CheckCircle size={14} /> Saved</> : <>Save Changes</>}
                </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                {/* Profile */}
                <div className="glass-card" style={{ padding: 20 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                        <div style={{ width: 32, height: 32, borderRadius: 8, background: '#3b82f618', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <User size={14} color="#3b82f6" />
                        </div>
                        <h3 style={{ fontSize: 14, fontWeight: 600 }}>Profile</h3>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        <Field label="Full Name" value={config.full_name} onChange={(v) => update('full_name', v)} placeholder="Your name as it appears on LinkedIn" />
                        <Field label="Email" value={config.email} onChange={(v) => update('email', v)} placeholder="your@email.com" type="email" />
                        <Field label="Target Role" value={config.target_role} onChange={(v) => update('target_role', v)} placeholder="e.g. ML Engineer, Product Manager" />
                        <div>
                            <label style={{ fontSize: 11, color: '#475569', fontWeight: 600, display: 'block', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Timezone</label>
                            <select value={config.timezone} onChange={(e) => update('timezone', e.target.value)}
                                style={{ width: '100%', background: '#080b12', border: '1px solid #1e2a3a', borderRadius: 8, padding: '9px 12px', color: '#f1f5f9', fontSize: 13, outline: 'none' }}>
                                {['America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles', 'Europe/London', 'Europe/Berlin', 'Asia/Kolkata', 'Asia/Tokyo'].map((tz) => (
                                    <option key={tz} value={tz}>{tz.replace('_', ' ')}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label style={{ fontSize: 11, color: '#475569', fontWeight: 600, display: 'block', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Warmup Phase</label>
                            <div style={{ display: 'flex', gap: 6 }}>
                                {[1, 2, 3, 4, 5].map((p) => (
                                    <button key={p} onClick={() => update('warmup_phase', p)}
                                        style={{
                                            flex: 1, padding: '8px 0', borderRadius: 6, fontSize: 12.5, fontWeight: 600, cursor: 'pointer', border: 'none',
                                            background: config.warmup_phase === p ? '#3b82f6' : '#0d1117',
                                            color: config.warmup_phase === p ? 'white' : '#475569',
                                            outline: '1px solid ' + (config.warmup_phase === p ? '#3b82f6' : '#1e2a3a'),
                                        }}>
                                        {p}
                                    </button>
                                ))}
                            </div>
                            <div style={{ fontSize: 10, color: '#334155', marginTop: 4 }}>Phase {config.warmup_phase}: {['Crawl', 'Walk', 'Jog', 'Run', 'Cruise'][config.warmup_phase - 1]}</div>
                        </div>
                    </div>
                </div>

                {/* Integrations */}
                <div className="glass-card" style={{ padding: 20 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                        <div style={{ width: 32, height: 32, borderRadius: 8, background: '#10b98118', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <Key size={14} color="#10b981" />
                        </div>
                        <h3 style={{ fontSize: 14, fontWeight: 600 }}>Integrations</h3>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                        {/* LinkedIn */}
                        <div style={{ padding: '12px 14px', background: '#080b12', border: '1px solid #1e2a3a', borderRadius: 8 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                <span style={{ fontSize: 13, fontWeight: 500, color: '#e2e8f0' }}>LinkedIn Account</span>
                                <StatusDot active={!!config.linkedin_email} />
                            </div>
                            <div style={{ fontSize: 11, color: '#334155' }}>Used for actions only — never for data collection</div>
                        </div>

                        {/* Gemini */}
                        <div style={{ padding: '12px 14px', background: '#080b12', border: '1px solid #1e2a3a', borderRadius: 8 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                <span style={{ fontSize: 13, fontWeight: 500, color: '#e2e8f0' }}>Gemini 1.5 Flash</span>
                                <StatusDot active={config.gemini_key_set} />
                            </div>
                            <div style={{ fontSize: 11, color: '#334155' }}>1,500 free requests/day · Personalized messages</div>
                        </div>

                        {/* Gmail */}
                        <div style={{ padding: '12px 14px', background: '#080b12', border: '1px solid #1e2a3a', borderRadius: 8 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                <span style={{ fontSize: 13, fontWeight: 500, color: '#e2e8f0' }}>Gmail SMTP</span>
                                <StatusDot active={config.gmail_configured} />
                            </div>
                            <div style={{ fontSize: 11, color: '#334155' }}>Plain-text email outreach · 500 emails/day</div>
                        </div>

                        {/* Email Finders */}
                        <div style={{ padding: '12px 14px', background: '#080b12', border: '1px solid #1e2a3a', borderRadius: 8 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                <span style={{ fontSize: 13, fontWeight: 500, color: '#e2e8f0' }}>Email Finders</span>
                                <span style={{ fontSize: 11, color: '#475569' }}>
                                    {[config.apollo_key_set, config.hunter_key_set, config.skrapp_key_set].filter(Boolean).length}/3 configured
                                </span>
                            </div>
                            <div style={{ display: 'flex', gap: 8, marginTop: 6 }}>
                                {[['Apollo', config.apollo_key_set], ['Hunter', config.hunter_key_set], ['Skrapp', config.skrapp_key_set]].map(([name, active]) => (
                                    <div key={name as string} className={`pill ${active ? 'pill-green' : 'pill-gray'}`}>
                                        {name as string}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Resume */}
                        <div style={{ padding: '12px 14px', background: '#080b12', border: '1px solid #1e2a3a', borderRadius: 8 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                <span style={{ fontSize: 13, fontWeight: 500, color: '#e2e8f0' }}>Resume (RAG)</span>
                                <StatusDot active={config.resume_uploaded} />
                            </div>
                            <div style={{ fontSize: 11, color: '#334155' }}>Upload for personalized message generation</div>
                            <button className="btn-ghost" style={{ marginTop: 8, padding: '5px 10px', fontSize: 11 }}>
                                <Upload size={11} /> Upload Resume
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
