/**
 * API client — thin wrapper around the FastAPI backend.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ─ Default User ID (replace with Clerk auth later) ──────────────────────────
export const DEFAULT_USER_ID = 'demo-user-001';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

// ─ Campaigns ────────────────────────────────────────────────────────────────
export const campaignsApi = {
  list: (userId: string) => request<Campaign[]>(`/api/campaigns/?user_id=${userId}`),
  get: (id: string) => request<Campaign>(`/api/campaigns/${id}`),
  create: (userId: string, data: Partial<Campaign>) =>
    request<Campaign>(`/api/campaigns/?user_id=${userId}`, { method: 'POST', body: JSON.stringify(data) }),
  start: (id: string) => request(`/api/campaigns/${id}/start`, { method: 'POST' }),
  pause: (id: string) => request(`/api/campaigns/${id}/pause`, { method: 'POST' }),
  delete: (id: string) => request(`/api/campaigns/${id}`, { method: 'DELETE' }),
};

// ─ Companies ────────────────────────────────────────────────────────────────
export const companiesApi = {
  list: (userId: string) => request<Company[]>(`/api/companies/?user_id=${userId}`),
  create: (userId: string, data: Partial<Company>) =>
    request<Company>(`/api/companies/?user_id=${userId}`, { method: 'POST', body: JSON.stringify(data) }),
  scan: (id: string) => request(`/api/companies/${id}/scan`, { method: 'POST' }),
  discoverLeads: (id: string, userId: string) =>
    request(`/api/companies/${id}/discover-leads?user_id=${userId}`, { method: 'POST' }),
  delete: (id: string) => request(`/api/companies/${id}`, { method: 'DELETE' }),
};

// ─ Leads ────────────────────────────────────────────────────────────────────
export const leadsApi = {
  list: (userId: string, params?: { company_id?: string; status?: string }) => {
    const qs = new URLSearchParams({ user_id: userId, ...params }).toString();
    return request<Lead[]>(`/api/leads/?${qs}`);
  },
  score: (id: string) => request<LeadScoreResponse>(`/api/leads/${id}/score`, { method: 'POST' }),
  findEmail: (id: string) => request(`/api/leads/${id}/find-email`, { method: 'POST' }),
  delete: (id: string) => request(`/api/leads/${id}`, { method: 'DELETE' }),
};

// ─ Analytics ────────────────────────────────────────────────────────────────
export const analyticsApi = {
  funnel: (userId: string) => request<FunnelMetrics>(`/api/analytics/funnel/${userId}`),
  activity: (userId: string, limit = 20) =>
    request<OutreachAction[]>(`/api/analytics/activity/${userId}?limit=${limit}`),
  companyStats: (userId: string) =>
    request<CompanyStats[]>(`/api/analytics/company-stats/${userId}`),
};

// ─ Safety ───────────────────────────────────────────────────────────────────
export const safetyApi = {
  health: (userId: string) => request<HealthReport>(`/api/safety/health/${userId}`),
  budget: (userId: string) => request<BudgetReport>(`/api/safety/budget/${userId}`),
};

// ─ Types ────────────────────────────────────────────────────────────────────
export interface Campaign {
  id: string;
  user_id: string;
  name: string;
  description: string;
  target_role: string;
  status: 'draft' | 'active' | 'paused' | 'completed';
  total_leads: number;
  leads_contacted: number;
  replies_received: number;
  connections_accepted: number;
  avg_response_rate: number;
  created_at: string;
  updated_at: string;
}

export interface Company {
  id: string;
  company_name: string;
  linkedin_company_url: string;
  domain: string;
  signal_score: number;
  signal_type: string | null;
  signal_detail: string | null;
  employee_count: number | null;
  open_roles_count: number;
  priority: 'high' | 'medium' | 'low';
  status: string;
  last_scanned_at: string | null;
}

export interface Lead {
  id: string;
  company_id: string;
  linkedin_url: string;
  full_name: string;
  title: string;
  headline: string;
  location: string;
  persona_type: string;
  email: string | null;
  score: number;
  outreach_status: string;
  sequence_day: number;
  connected: boolean;
  created_at: string;
}

export interface OutreachAction {
  id: string;
  lead_id: string;
  action_type: string;
  sequence_day: number;
  content: string | null;
  outcome: string;
  executed_at: string | null;
  created_at: string;
}

export interface FunnelMetrics {
  total_leads: number;
  contacted: number;
  connected: number;
  replied: number;
  connection_rate: number;
  reply_rate: number;
}

export interface CompanyStats {
  company_id: string;
  company_name: string;
  signal_score: number;
  signal_type: string | null;
  total_leads: number;
  replies: number;
  priority: string;
}

export interface HealthReport {
  health_score: number;
  status: 'healthy' | 'caution' | 'critical';
  metrics: {
    connections_sent_30d: number;
    connections_accepted_30d: number;
    messages_sent_30d: number;
    messages_replied_30d: number;
    days_active_30d: number;
  };
}

export interface BudgetReport {
  warmup_phase: number;
  health_score: number;
  budget: {
    [key: string]: { limit: number; used: number; remaining: number };
  };
}

export interface LeadScoreResponse {
  lead_id: string;
  score: number;
  breakdown: Record<string, unknown>;
}
