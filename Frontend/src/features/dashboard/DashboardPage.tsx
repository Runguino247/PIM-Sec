import { useEffect, useState } from 'react';
import { apiClient } from '../../api/client';
import type { DashboardSummary, Repository } from '../../types';
import { Shield, AlertTriangle, Folder, Activity, Play, RefreshCw } from 'lucide-react';
import { Modal } from '../../components/ui/Modal';
import { useAuth } from '../auth/AuthContext';

interface Baseline {
  id: number;
  repository_id: number;
  version_no: number;
  status: string;
}

export const DashboardPage = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [repos, setRepos] = useState<Repository[]>([]);
  const [baselines, setBaselines] = useState<Baseline[]>([]);
  const [isScanModalOpen, setIsScanModalOpen] = useState(false);
  const [selectedRepo, setSelectedRepo] = useState<number | null>(null);
  const [selectedBaseline, setSelectedBaseline] = useState<number | null>(null);
  const [scanMessage, setScanMessage] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const { user } = useAuth();

  const canScan = user?.role_id === 1 || user?.role_id === 2; // ADMIN u OPERADOR

  const loadSummary = () => {
    apiClient.get('/dashboard/summary').then((res) => setSummary(res.data));
  };

  useEffect(() => {
    loadSummary();
    apiClient.get('/repositories/').then((res) => {
      setRepos(res.data);
      if (res.data.length > 0) setSelectedRepo(res.data[0].id);
    });
  }, []);

  // Cargar línea base activa cuando cambia el repositorio
  useEffect(() => {
    if (!selectedRepo) return;
    apiClient.get(`/baselines/repository/${selectedRepo}`).then((res) => {
      const active = res.data.find((b: Baseline) => b.status === 'ACTIVE');
      setBaselines(res.data);
      setSelectedBaseline(active ? active.id : null);
    });
  }, [selectedRepo]);

  const handleRunScan = async () => {
    if (!selectedRepo || !selectedBaseline) {
      setScanMessage('Debes seleccionar un repositorio con línea base ACTIVA');
      return;
    }
    setIsScanning(true);
    setScanMessage('');
    try {
      const { data } = await apiClient.post('/scans/run', {
        repository_id: selectedRepo,
        baseline_id: selectedBaseline,
      });
      setScanMessage(
        `✅ Escaneo completado. Archivos: ${data.files_checked}. Resultados: ${JSON.stringify(data.summary_json)}`
      );
      loadSummary(); // Refrescar dashboard
    } catch (err: any) {
      setScanMessage(`❌ Error: ${err.response?.data?.detail || 'Error desconocido'}`);
    } finally {
      setIsScanning(false);
    }
  };

  if (!summary) return <div className="text-center py-10">Cargando...</div>;

  const cards = [
    { label: 'Repositorios Activos', value: summary.total_repositories, icon: Folder, color: 'text-blue-400' },
    { label: 'Alertas Abiertas', value: summary.open_alerts, icon: AlertTriangle, color: 'text-yellow-400' },
    { label: 'Último Escaneo', value: summary.last_scan?.status || 'N/A', icon: Activity, color: 'text-green-400' },
    { label: 'Estado Sistema', value: 'Operativo', icon: Shield, color: 'text-brand-accent' },
  ];

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Dashboard de Seguridad</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className="bg-brand-panel p-6 rounded-xl border border-brand-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">{card.label}</p>
                  <p className="text-3xl font-bold mt-2">{card.value}</p>
                </div>
                <Icon className={card.color} size={40} />
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-brand-panel p-6 rounded-xl border border-brand-border">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Resumen del Último Escaneo</h2>
            <button onClick={loadSummary} className="text-gray-400 hover:text-white" title="Refrescar">
              <RefreshCw size={18} />
            </button>
          </div>
          {summary.last_scan?.summary ? (
            <div className="space-y-3">
              {Object.entries(summary.last_scan.summary).map(([key, val]) => (
                <div key={key} className="flex justify-between items-center p-2 bg-brand-dark rounded">
                  <span className="text-gray-300">{key}</span>
                  <span className="font-bold text-brand-accent">{String(val)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400">No hay escaneos registrados aún.</p>
          )}
        </div>

        <div className="bg-brand-panel p-6 rounded-xl border border-brand-border">
          <h2 className="text-xl font-semibold mb-4">Acciones Rápidas</h2>
          <div className="space-y-3">
            {canScan && (
              <button
                onClick={() => setIsScanModalOpen(true)}
                className="w-full py-3 bg-brand-accent/10 text-brand-accent rounded-lg hover:bg-brand-accent/20 transition text-left px-4 flex items-center gap-3"
              >
                <Play size={18} /> ▶ Ejecutar Escaneo Manual
              </button>
            )}
            <a href="/alerts" className="w-full py-3 bg-yellow-500/10 text-yellow-400 rounded-lg hover:bg-yellow-500/20 transition text-left px-4 flex items-center gap-3 block">
              ⚠ Revisar Alertas Pendientes
            </a>
            <a href="/baselines" className="w-full py-3 bg-green-500/10 text-green-400 rounded-lg hover:bg-green-500/20 transition text-left px-4 flex items-center gap-3 block">
              ✓ Gestionar Líneas Base
            </a>
          </div>
        </div>
      </div>

      <Modal
        isOpen={isScanModalOpen}
        onClose={() => { setIsScanModalOpen(false); setScanMessage(''); }}
        title="Ejecutar Escaneo Manual"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-300 mb-1">Repositorio</label>
            <select
              value={selectedRepo || ''}
              onChange={(e) => setSelectedRepo(Number(e.target.value))}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white"
            >
              {repos.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1">Línea Base Activa</label>
            <select
              value={selectedBaseline || ''}
              onChange={(e) => setSelectedBaseline(Number(e.target.value))}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white"
            >
              {baselines.filter(b => b.status === 'ACTIVE').map((b) => (
                <option key={b.id} value={b.id}>Versión {b.version_no}</option>
              ))}
              {baselines.filter(b => b.status === 'ACTIVE').length === 0 && (
                <option value="">Sin línea base activa</option>
              )}
            </select>
          </div>
          {scanMessage && (
            <div className="p-3 bg-brand-dark rounded text-sm text-gray-300 break-words">
              {scanMessage}
            </div>
          )}
          <button
            onClick={handleRunScan}
            disabled={isScanning || !selectedBaseline}
            className="w-full py-2 bg-brand-accent text-brand-dark font-bold rounded-lg disabled:opacity-50"
          >
            {isScanning ? 'Ejecutando...' : 'Iniciar Escaneo'}
          </button>
        </div>
      </Modal>
    </div>
  );
};