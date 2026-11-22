import { useEffect, useState } from 'react';
import { apiClient } from '../../api/client';
import type { SecurityEvent } from '../../types';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Activity } from 'lucide-react';

export const EventsPage = () => {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [severityFilter, setSeverityFilter] = useState<string>('');

  useEffect(() => {
    const url = severityFilter ? `/events/?severity=${severityFilter}` : '/events/';
    apiClient.get(url).then((res) => setEvents(res.data));
  }, [severityFilter]);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Eventos de Seguridad</h1>
        <p className="text-gray-400 mt-1">Registro de todas las desviaciones detectadas por el motor FIM</p>
      </div>

      <div className="flex gap-2 mb-6">
        {['', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((s) => (
          <button
            key={s}
            onClick={() => setSeverityFilter(s)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              severityFilter === s ? 'bg-brand-accent text-brand-dark' : 'bg-brand-panel text-gray-300 hover:bg-brand-border'
            }`}
          >
            {s === '' ? 'Todas' : s}
          </button>
        ))}
      </div>

      <div className="bg-brand-panel rounded-xl border border-brand-border overflow-hidden">
        <table className="w-full">
          <thead className="bg-brand-dark">
            <tr className="text-left text-xs text-gray-400 uppercase">
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Tipo</th>
              <th className="px-4 py-3">Severidad</th>
              <th className="px-4 py-3">Archivo</th>
              <th className="px-4 py-3">Detectado</th>
            </tr>
          </thead>
          <tbody>
            {events.map((ev) => (
              <tr key={ev.id} className="border-t border-brand-border hover:bg-brand-dark/50">
                <td className="px-4 py-3 text-sm">#{ev.id}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Activity size={16} className="text-brand-accent" />
                    <span className="text-sm font-medium">{ev.event_type}</span>
                  </div>
                </td>
                <td className="px-4 py-3"><StatusBadge value={ev.severity} /></td>
                <td className="px-4 py-3 text-sm text-gray-400 font-mono">
                  {ev.details_json?.relative_path || 'N/A'}
                </td>
                <td className="px-4 py-3 text-sm text-gray-400">
                  {new Date(ev.detected_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {events.length === 0 && (
          <div className="text-center py-12 text-gray-400">No hay eventos registrados.</div>
        )}
      </div>
    </div>
  );
};