import { useEffect, useState } from 'react';
import { apiClient } from '../../api/client';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { ClipboardList, User } from 'lucide-react';

interface AuditLog {
  id: number;
  actor_user_id: number | null;
  action: string;
  resource_type: string;
  resource_id: string | null;
  occurred_at: string;
  source_ip: string | null;
  outcome: string;
  details_json: any;
}

export const AuditPage = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [actionFilter, setActionFilter] = useState('');

  useEffect(() => {
    const url = actionFilter ? `/audit/?action=${actionFilter}` : '/audit/';
    apiClient.get(url).then((res) => setLogs(res.data));
  }, [actionFilter]);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Registro de Auditoría</h1>
        <p className="text-gray-400 mt-1">Historial completo de operaciones críticas (append-only)</p>
      </div>

      <div className="mb-6">
        <input
          type="text"
          placeholder="Filtrar por acción (ej: LOGIN, APPROVE_BASELINE)..."
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          className="w-full max-w-md px-4 py-2 bg-brand-panel border border-brand-border rounded-lg text-white"
        />
      </div>

      <div className="bg-brand-panel rounded-xl border border-brand-border overflow-hidden">
        <table className="w-full">
          <thead className="bg-brand-dark">
            <tr className="text-left text-xs text-gray-400 uppercase">
              <th className="px-4 py-3">Fecha</th>
              <th className="px-4 py-3">Actor</th>
              <th className="px-4 py-3">Acción</th>
              <th className="px-4 py-3">Recurso</th>
              <th className="px-4 py-3">IP</th>
              <th className="px-4 py-3">Resultado</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="border-t border-brand-border hover:bg-brand-dark/50">
                <td className="px-4 py-3 text-sm text-gray-300">
                  {new Date(log.occurred_at).toLocaleString()}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2 text-sm">
                    <User size={14} className="text-brand-accent" />
                    {log.actor_user_id ? `Usuario #${log.actor_user_id}` : 'Sistema'}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <ClipboardList size={14} className="text-gray-400" />
                    <span className="text-sm font-mono">{log.action}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-400">
                  {log.resource_type} {log.resource_id ? `#${log.resource_id}` : ''}
                </td>
                <td className="px-4 py-3 text-sm text-gray-400 font-mono">
                  {log.source_ip || 'N/A'}
                </td>
                <td className="px-4 py-3"><StatusBadge value={log.outcome} /></td>
              </tr>
            ))}
          </tbody>
        </table>
        {logs.length === 0 && (
          <div className="text-center py-12 text-gray-400">No hay registros de auditoría.</div>
        )}
      </div>
    </div>
  );
};