import { useEffect, useState } from 'react';
import { apiClient } from '../../api/client';
import type { Repository } from '../../types';
import { StatusBadge } from '../../components/ui/StatusBadge';
import { Modal } from '../../components/ui/Modal';
import { FileText, CheckCircle, XCircle, Plus } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

interface Baseline {
  id: number;
  repository_id: number;
  version_no: number;
  status: string;
  created_by: number;
  created_at: string;
  reason: string;
  hmac_sha256?: string;
}

export const BaselinesPage = () => {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<number | null>(null);
  const [baselines, setBaselines] = useState<Baseline[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const { user } = useAuth();
  
  const isAdmin = user?.role_id === 1;
  const canPropose = user?.role_id === 1 || user?.role_id === 2;

  const loadBaselines = () => {
    if (!selectedRepo) return;
    apiClient.get(`/baselines/repository/${selectedRepo}`).then((res) => setBaselines(res.data));
  };

  useEffect(() => {
    apiClient.get('/repositories/').then((res) => {
      setRepos(res.data);
      if (res.data.length > 0) setSelectedRepo(res.data[0].id);
    });
  }, []);

  useEffect(() => { loadBaselines(); }, [selectedRepo]);

  const handlePropose = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await apiClient.post('/baselines/propose', {
        repository_id: selectedRepo,
        reason,
      });
      setIsModalOpen(false);
      setReason('');
      loadBaselines();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al proponer');
    }
  };

  const handleDecision = async (baselineId: number, approve: boolean) => {
    try {
      await apiClient.post(`/baselines/${baselineId}/approve`, {
        approve,
        reason: approve ? 'Aprobada por administrador' : 'Rechazada por administrador',
      });
      loadBaselines();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error en la decisión');
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Líneas Base Criptográficas</h1>
          <p className="text-gray-400 mt-1">Referencias SHA-256 versionadas y protegidas con HMAC</p>
        </div>
        {canPropose && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-brand-accent text-brand-dark font-semibold rounded-lg hover:bg-opacity-90"
          >
            <Plus size={18} /> Proponer Línea Base
          </button>
        )}
      </div>

      <div className="mb-6">
        <label className="block text-sm text-gray-400 mb-2">Seleccionar Repositorio</label>
        <select
          value={selectedRepo || ''}
          onChange={(e) => setSelectedRepo(Number(e.target.value))}
          className="px-4 py-2 bg-brand-panel border border-brand-border rounded-lg text-white"
        >
          {repos.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
        </select>
      </div>

      <div className="space-y-3">
        {baselines.map((b) => (
          <div key={b.id} className="bg-brand-panel p-5 rounded-xl border border-brand-border">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <FileText className="text-brand-accent" size={20} />
                  <span className="font-semibold">Versión {b.version_no}</span>
                  <StatusBadge value={b.status} />
                </div>
                <p className="text-sm text-gray-400 mb-1"><strong>Motivo:</strong> {b.reason}</p>
                <p className="text-sm text-gray-400">
                  <strong>Creada:</strong> {new Date(b.created_at).toLocaleString()}
                </p>
                {b.hmac_sha256 && (
                  <p className="text-xs text-gray-500 font-mono mt-2 break-all">
                    HMAC: {b.hmac_sha256}
                  </p>
                )}
              </div>

              {isAdmin && b.status === 'PROPOSED' && (
                <div className="flex gap-2">
                  <button
                    onClick={() => handleDecision(b.id, true)}
                    className="flex items-center gap-1 px-3 py-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 text-sm"
                  >
                    <CheckCircle size={14} /> Aprobar
                  </button>
                  <button
                    onClick={() => handleDecision(b.id, false)}
                    className="flex items-center gap-1 px-3 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 text-sm"
                  >
                    <XCircle size={14} /> Rechazar
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
        {baselines.length === 0 && (
          <div className="text-center py-12 text-gray-400">No hay líneas base en este repositorio.</div>
        )}
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Proponer Nueva Línea Base"
      >
        <form onSubmit={handlePropose} className="space-y-4">
          {error && <div className="p-2 bg-red-500/10 text-red-400 text-sm rounded">{error}</div>}
          <div>
            <label className="block text-sm text-gray-300 mb-1">Motivo de la propuesta *</label>
            <textarea
              required
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white"
              rows={3}
              placeholder="Ej: Línea base inicial del repositorio patrimonial"
            />
          </div>
          <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded text-xs text-yellow-300">
            ⚠ El sistema recorrerá todos los archivos del repositorio y calculará su SHA-256. La aprobación debe hacerla otro ADMIN.
          </div>
          <button
            type="submit"
            className="w-full py-2 bg-brand-accent text-brand-dark font-bold rounded-lg"
          >
            Generar Propuesta
          </button>
        </form>
      </Modal>
    </div>
  );
};