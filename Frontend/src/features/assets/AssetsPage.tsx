import { useEffect, useState } from 'react';
import { apiClient } from '../../api/client';
import type { Repository } from '../../types';
import { Modal } from '../../components/ui/Modal';
import { FileText, Search, Edit3, HardDrive } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

interface Asset {
  id: number;
  repository_id: number;
  category_id?: number;
  relative_path: string;
  file_name: string;
  mime_type?: string;
  size_bytes: number;
  is_active: boolean;
  expected_sha256?: string;
}

export const AssetsPage = () => {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<number | null>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [search, setSearch] = useState('');
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [formData, setFormData] = useState({ category_id: 0, file_name: '', mime_type: '' });
  const { user } = useAuth();
  const canEdit = user?.role_id === 1 || user?.role_id === 2;

  useEffect(() => {
    apiClient.get('/repositories/').then((res) => {
      setRepos(res.data);
      if (res.data.length > 0) setSelectedRepo(res.data[0].id);
    });
  }, []);

  useEffect(() => {
    if (!selectedRepo) return;
    apiClient.get(`/assets/repository/${selectedRepo}`).then(async (res) => {
      // Cargar detalle de cada asset para obtener su hash
      const withHashes = await Promise.all(
        res.data.map(async (asset: Asset) => {
          try {
            const detail = await apiClient.get(`/assets/${asset.id}/detail`);
            return detail.data;
          } catch {
            return asset;
          }
        })
      );
      setAssets(withHashes);
    });
  }, [selectedRepo]);

  const filteredAssets = assets.filter((a) =>
    a.relative_path.toLowerCase().includes(search.toLowerCase())
  );

  const openEdit = (asset: Asset) => {
    setSelectedAsset(asset);
    setFormData({
      category_id: asset.category_id || 0,
      file_name: asset.file_name,
      mime_type: asset.mime_type || '',
    });
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAsset) return;
    await apiClient.patch(`/assets/${selectedAsset.id}`, formData);
    setSelectedAsset(null);
    // Recargar
    apiClient.get(`/assets/repository/${selectedRepo}`).then((res) => setAssets(res.data));
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Inventario de Archivos</h1>
        <p className="text-gray-400 mt-1">Archivos patrimoniales monitoreados con su hash SHA-256 esperado</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm text-gray-400 mb-2">Repositorio</label>
          <select
            value={selectedRepo || ''}
            onChange={(e) => setSelectedRepo(Number(e.target.value))}
            className="w-full px-4 py-2 bg-brand-panel border border-brand-border rounded-lg text-white"
          >
            {repos.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-2">Buscar archivo</label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Buscar por ruta..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-brand-panel border border-brand-border rounded-lg text-white"
            />
          </div>
        </div>
      </div>

      <div className="bg-brand-panel rounded-xl border border-brand-border overflow-hidden">
        <table className="w-full">
          <thead className="bg-brand-dark">
            <tr className="text-left text-xs text-gray-400 uppercase">
              <th className="px-4 py-3">Archivo</th>
              <th className="px-4 py-3">Tipo</th>
              <th className="px-4 py-3">Tamaño</th>
              <th className="px-4 py-3">SHA-256 (Esperado)</th>
              <th className="px-4 py-3">Estado</th>
              {canEdit && <th className="px-4 py-3">Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {filteredAssets.map((a) => (
              <tr key={a.id} className="border-t border-brand-border hover:bg-brand-dark/50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <FileText size={16} className="text-brand-accent flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium">{a.file_name}</p>
                      <p className="text-xs text-gray-500 font-mono">{a.relative_path}</p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-400">{a.mime_type || 'N/A'}</td>
                <td className="px-4 py-3 text-sm text-gray-400">
                  <span className="flex items-center gap-1">
                    <HardDrive size={12} /> {formatSize(a.size_bytes)}
                  </span>
                </td>
                <td className="px-4 py-3 text-xs text-gray-500 font-mono">
                  {a.expected_sha256 ? `${a.expected_sha256.substring(0, 16)}...` : 'Sin baseline'}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs ${a.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                    {a.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                {canEdit && (
                  <td className="px-4 py-3">
                    <button
                      onClick={() => openEdit(a)}
                      className="flex items-center gap-1 px-2 py-1 bg-brand-accent/20 text-brand-accent rounded text-xs hover:bg-brand-accent/30"
                    >
                      <Edit3 size={12} /> Editar
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
        {filteredAssets.length === 0 && (
          <div className="text-center py-12 text-gray-400">No hay archivos registrados.</div>
        )}
      </div>

      <Modal
        isOpen={!!selectedAsset}
        onClose={() => setSelectedAsset(null)}
        title={`Editar Metadatos de ${selectedAsset?.file_name}`}
      >
        <form onSubmit={handleUpdate} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-300 mb-1">Nombre visible</label>
            <input
              type="text" value={formData.file_name}
              onChange={(e) => setFormData({ ...formData, file_name: e.target.value })}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1">Categoría ID</label>
            <input
              type="number" value={formData.category_id}
              onChange={(e) => setFormData({ ...formData, category_id: Number(e.target.value) })}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1">MIME Type</label>
            <input
              type="text" value={formData.mime_type}
              onChange={(e) => setFormData({ ...formData, mime_type: e.target.value })}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white"
              placeholder="application/pdf"
            />
          </div>
          <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded text-xs text-blue-300">
            ℹ La edición solo modifica los metadatos lógicos en la base de datos, no el archivo físico.
          </div>
          <button type="submit" className="w-full py-2 bg-brand-accent text-brand-dark font-bold rounded-lg">
            Guardar Cambios
          </button>
        </form>
      </Modal>
    </div>
  );
};