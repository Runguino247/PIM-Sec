import { useEffect, useState } from 'react';
import { apiClient } from '../../api/client';
import type { Repository } from '../../types';
import { Modal } from '../../components/ui/Modal';
import { Plus, Folder } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

export const RepositoriesPage = () => {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', root_path: '', description: '' });
  const [error, setError] = useState('');
  const { user } = useAuth();

  // Solo ADMIN y OPERADOR pueden crear
  const canCreate = user?.role_id === 1 || user?.role_id === 2;

  const loadRepos = async () => {
    const { data } = await apiClient.get('/repositories/');
    setRepos(data);
  };

  useEffect(() => { loadRepos(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await apiClient.post('/repositories/', formData);
      setIsModalOpen(false);
      setFormData({ name: '', root_path: '', description: '' });
      loadRepos();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear repositorio');
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Repositorios</h1>
          <p className="text-gray-400 mt-1">Carpetas patrimoniales monitoreadas por el sistema</p>
        </div>
        {canCreate && (
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 bg-brand-accent text-brand-dark font-semibold rounded-lg hover:bg-opacity-90"
          >
            <Plus size={18} /> Nuevo Repositorio
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {repos.map((repo) => (
          <div key={repo.id} className="bg-brand-panel p-6 rounded-xl border border-brand-border hover:border-brand-accent transition">
            <div className="flex items-start gap-3 mb-4">
              <Folder className="text-brand-accent" size={28} />
              <div>
                <h3 className="font-semibold text-lg">{repo.name}</h3>
                <p className="text-xs text-gray-400">ID: {repo.id}</p>
              </div>
            </div>
            <p className="text-sm text-gray-300 mb-2">{repo.description || 'Sin descripción'}</p>
            <div className="text-xs text-gray-500 bg-brand-dark p-2 rounded font-mono break-all">
              {repo.root_path}
            </div>
            <div className="mt-4">
              <span className={`px-2 py-1 rounded text-xs ${repo.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                {repo.is_active ? 'Activo' : 'Inactivo'}
              </span>
            </div>
          </div>
        ))}
        {repos.length === 0 && (
          <div className="col-span-full text-center py-12 text-gray-400">
            No hay repositorios registrados aún.
          </div>
        )}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Registrar Nuevo Repositorio">
        <form onSubmit={handleCreate} className="space-y-4">
          {error && <div className="p-2 bg-red-500/10 text-red-400 text-sm rounded">{error}</div>}
          <div>
            <label className="block text-sm text-gray-300 mb-1">Nombre</label>
            <input
              type="text" required value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1">Ruta Absoluta (root_path)</label>
            <input
              type="text" required value={formData.root_path}
              onChange={(e) => setFormData({ ...formData, root_path: e.target.value })}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white font-mono text-sm"
              placeholder="C:\ruta\a\data\repositorio_patrimonial"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1">Descripción</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white"
              rows={2}
            />
          </div>
          <button type="submit" className="w-full py-2 bg-brand-accent text-brand-dark font-bold rounded-lg">
            Registrar
          </button>
        </form>
      </Modal>
    </div>
  );
};