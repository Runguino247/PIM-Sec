import { useEffect, useState } from 'react';
import { apiClient } from '../../api/client';
import type { Alert, SecurityEvent } from '../../types';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Modal } from '../../components/ui/Modal';
import { Bell, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

export const AlertsPage = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [events, setEvents] = useState<Record<number, SecurityEvent>>({});
  const [filter, setFilter] = useState<string>('ALL');
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [resolutionNote, setResolutionNote] = useState('');
  const { user } = useAuth();

  // Solo ADMIN, OPERADOR y AUDITOR pueden interactuar
  const canInteract = user?.role_id !== 4; // 4 = VIEWER

  const loadAlerts = async () => {
    const url = filter === 'ALL' ? '/alerts/' : `/alerts/?status=${filter}`;
    const { data } = await apiClient.get(url);
    setAlerts(data);

    // Cargar eventos asociados
    const eventMap: Record<number, SecurityEvent> = {};
    await Promise.all(
      data.map(async (alert: Alert) => {
        try {
          const res = await apiClient.get(`/events/?id=${alert.event_id}`);
          if (res.data.length > 0) eventMap[alert.event_id] = res.data[0];
        } catch {}
      })
    );
    setEvents(eventMap);
  };

  useEffect(() => { loadAlerts(); }, [filter]);

  const handleAcknowledge = async (alertId: number) => {
    await apiClient.post(`/alerts/${alertId}/acknowledge`);
    loadAlerts();
  };

  const handleResolve = async () => {
    if (!selectedAlert || !resolutionNote.trim()) return;
    await apiClient.post(`/alerts/${selectedAlert.id}/resolve`, { resolution_note: resolutionNote });
    setSelectedAlert(null);
    setResolutionNote('');
    loadAlerts();
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Gestión de Alertas</h1>
        <p className="text-gray-400 mt-1">Seguimiento de desviaciones de integridad detectadas</p>
      </div>

      <div className="flex gap-2 mb-6">
        {['ALL', 'NEW', 'ACKNOWLEDGED', 'RESOLVED'].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              filter === s ? 'bg-brand-accent text-brand-dark' : 'bg-brand-panel text-gray-300 hover:bg-brand-border'
            }`}
          >
            {s === 'ALL' ? 'Todas' : s}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {alerts.map((alert) => {
          const event = events[alert.event_id];
          return (
            <div key={alert.id} className="bg-brand-panel p-4 rounded-xl border border-brand-border">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <Bell size={18} className="text-brand-accent" />
                    <span className="font-semibold">Alerta #{alert.id}</span>
                    <StatusBadge value={alert.status} />
                    {event && <StatusBadge value={event.severity} />}
                  </div>
                  {event && (
                    <div className="text-sm text-gray-400 space-y-1">
                      <p><strong>Tipo:</strong> {event.event_type}</p>
                      <p><strong>Archivo:</strong> {event.details_json?.relative_path || 'N/A'}</p>
                      <p><strong>Detectado:</strong> {new Date(event.detected_at).toLocaleString()}</p>
                    </div>
                  )}
                  {alert.resolution_note && (
                    <div className="mt-2 p-2 bg-green-500/10 border-l-2 border-green-500 rounded">
                      <p className="text-xs text-green-400">Resolución: {alert.resolution_note}</p>
                    </div>
                  )}
                </div>

                {canInteract && (
                  <div className="flex flex-col gap-2">
                    {alert.status === 'NEW' && (
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        className="flex items-center gap-1 px-3 py-2 bg-yellow-500/20 text-yellow-400 rounded-lg hover:bg-yellow-500/30 text-sm"
                      >
                        <AlertCircle size={14} /> Reconocer
                      </button>
                    )}
                    {alert.status === 'ACKNOWLEDGED' && (
                      <button
                        onClick={() => setSelectedAlert(alert)}
                        className="flex items-center gap-1 px-3 py-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 text-sm"
                      >
                        <CheckCircle size={14} /> Resolver
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
        {alerts.length === 0 && (
          <div className="text-center py-12 text-gray-400">No hay alertas que mostrar.</div>
        )}
      </div>

      <Modal
        isOpen={!!selectedAlert}
        onClose={() => { setSelectedAlert(null); setResolutionNote(''); }}
        title={`Resolver Alerta #${selectedAlert?.id}`}
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-300 mb-1">Nota de Resolución *</label>
            <textarea
              value={resolutionNote}
              onChange={(e) => setResolutionNote(e.target.value)}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white"
              rows={4}
              placeholder="Describe la causa y la acción tomada..."
            />
          </div>
          <button
            onClick={handleResolve}
            disabled={!resolutionNote.trim()}
            className="w-full py-2 bg-green-500 text-white font-bold rounded-lg disabled:opacity-50"
          >
            Confirmar Resolución
          </button>
        </div>
      </Modal>
    </div>
  );
};