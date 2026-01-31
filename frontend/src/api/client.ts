const API_BASE = '/api';

function headers(): HeadersInit {
  const h: Record<string, string> = { 'Content-Type': 'application/json' };
  const key = import.meta.env.VITE_API_KEY;
  if (key) h['Authorization'] = `Bearer ${key}`;
  return h;
}

export async function getStats(): Promise<{ active_users: number; active_subscriptions: number }> {
  const r = await fetch(`${API_BASE}/dashboard/stats`, { headers: headers() });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function getSubscriptions(limit = 100, offset = 0): Promise<{ data: SubscriptionItem[] }> {
  const r = await fetch(
    `${API_BASE}/dashboard/subscriptions?limit=${limit}&offset=${offset}`,
    { headers: headers() }
  );
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function getEvents(limit = 50, offset = 0): Promise<{ data: EventItem[]; pagination: { total: number } }> {
  const r = await fetch(
    `${API_BASE}/events?limit=${limit}&offset=${offset}`,
    { headers: headers() }
  );
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function getStateTransitions(limit = 50, offset = 0, entity_type?: string): Promise<{ data: StateTransitionItem[] }> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (entity_type) params.set('entity_type', entity_type);
  const r = await fetch(`${API_BASE}/dashboard/state-transitions?${params}`, { headers: headers() });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export interface SubscriptionItem {
  id: string;
  user_id: string;
  external_customer_id: string;
  provider: string;
  plan_id: string;
  status: string;
  started_at: string | null;
  created_at: string | null;
}

export interface EventItem {
  id: string;
  provider: string;
  event_type: string;
  event_id: string;
  received_at: string;
  raw_payload: Record<string, unknown>;
}

export interface StateTransitionItem {
  id: string;
  entity_type: string;
  entity_id: string;
  from_state: string | null;
  to_state: string;
  event_id: string;
  transitioned_at: string | null;
}
