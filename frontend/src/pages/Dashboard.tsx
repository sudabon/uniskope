import { useEffect, useState } from 'react';
import * as api from '../api/client';

export default function Dashboard() {
  const [stats, setStats] = useState<{ active_users: number; active_subscriptions: number } | null>(null);
  const [subscriptions, setSubscriptions] = useState<api.SubscriptionItem[]>([]);
  const [events, setEvents] = useState<api.EventItem[]>([]);
  const [transitions, setTransitions] = useState<api.StateTransitionItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.getStats(),
      api.getSubscriptions(100, 0),
      api.getEvents(50, 0),
      api.getStateTransitions(50, 0),
    ])
      .then(([s, subs, ev, trans]) => {
        setStats(s);
        setSubscriptions(subs.data ?? []);
        setEvents(ev.data ?? []);
        setTransitions(trans.data ?? []);
      })
      .catch((e) => setError(String(e)));
  }, []);

  if (error) {
    return (
      <div className="min-h-screen p-8 text-red-400">
        <h1 className="text-xl font-semibold">エラー</h1>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 md:p-8 text-slate-200 bg-slate-900">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-white">Uniskope Dashboard</h1>
        <p className="text-slate-400 text-sm mt-1">読み取り専用・運用可視化</p>
      </header>

      {/* Stats */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-4">
          <h2 className="text-sm font-medium text-slate-400 mb-1">アクティブユーザー数</h2>
          <p className="text-2xl font-semibold text-white">{stats?.active_users ?? '—'}</p>
        </div>
        <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-4">
          <h2 className="text-sm font-medium text-slate-400 mb-1">アクティブサブスクリプション数</h2>
          <p className="text-2xl font-semibold text-white">{stats?.active_subscriptions ?? '—'}</p>
        </div>
      </section>

      {/* Subscriptions */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold text-white mb-3">アクティブサブスクリプション一覧</h2>
        <div className="rounded-lg border border-slate-700 bg-slate-800/50 overflow-hidden">
          {subscriptions.length === 0 ? (
            <p className="p-4 text-slate-500">アクティブなサブスクリプションはありません</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-slate-800 text-slate-400 text-left">
                <tr>
                  <th className="p-3">User ID</th>
                  <th className="p-3">Provider</th>
                  <th className="p-3">Plan</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Started</th>
                </tr>
              </thead>
              <tbody>
                {subscriptions.map((s) => (
                  <tr key={s.id} className="border-t border-slate-700">
                    <td className="p-3 font-mono text-xs">{s.external_customer_id}</td>
                    <td className="p-3">{s.provider}</td>
                    <td className="p-3">{s.plan_id}</td>
                    <td className="p-3">
                      <span className={statusClass(s.status)}>{s.status}</span>
                    </td>
                    <td className="p-3 text-slate-500">{s.started_at ? new Date(s.started_at).toLocaleString() : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>

      {/* Recent events */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold text-white mb-3">最近のイベント</h2>
        <div className="rounded-lg border border-slate-700 bg-slate-800/50 overflow-hidden">
          {events.length === 0 ? (
            <p className="p-4 text-slate-500">イベントはありません</p>
          ) : (
            <ul className="divide-y divide-slate-700">
              {events.map((e) => (
                <li key={e.id} className="p-3 flex flex-wrap gap-2 items-center text-sm">
                  <span className="text-slate-500 font-mono">{new Date(e.received_at).toLocaleString()}</span>
                  <span className="text-slate-400">{e.provider}</span>
                  <span className="text-white">{e.event_type}</span>
                  <span className="text-slate-500 font-mono text-xs">{e.event_id}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      {/* State transitions */}
      <section>
        <h2 className="text-lg font-semibold text-white mb-3">状態遷移ログ</h2>
        <div className="rounded-lg border border-slate-700 bg-slate-800/50 overflow-hidden">
          {transitions.length === 0 ? (
            <p className="p-4 text-slate-500">状態遷移はありません</p>
          ) : (
            <ul className="divide-y divide-slate-700">
              {transitions.map((t) => (
                <li key={t.id} className="p-3 flex flex-wrap gap-2 items-center text-sm">
                  <span className="text-slate-500">{t.transitioned_at ? new Date(t.transitioned_at).toLocaleString() : '—'}</span>
                  <span className="text-slate-400">{t.entity_type}</span>
                  <span className="text-slate-500 font-mono text-xs">{t.entity_id}</span>
                  <span>{t.from_state ?? '—'} → {t.to_state}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </div>
  );
}

function statusClass(status: string): string {
  const m: Record<string, string> = {
    active: 'text-green-400',
    trialing: 'text-blue-400',
    past_due: 'text-amber-400',
    canceled: 'text-slate-500',
  };
  return m[status] ?? 'text-slate-400';
}
