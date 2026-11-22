import { useEffect, useState } from 'react';
import { apiClient } from '../../api/client';
import { Modal } from '../../components/ui/Modal';
import { UserPlus, Shield, User as UserIcon } from 'lucide-react';

interface UserRecord {
  id: number;
  username: string;
  email: string;
  role_id: number;
  is_active: boolean;
  created_at: string;
  last_login_at?: string;
}

const ROLES = [
  { id: 1, name: 'ADMIN' },
  { id: 2, name: 'OPERADOR' },
  { id: 3, name: 'AUDITOR' },
  { id: 4, name: 'VIEWER' },
];

export const UsersPage = () => {
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({ username: '', email: '', password: '', role_id: 4 });
  const [error, setError] = useState('');

  const loadUsers = () => {
    // Endpoint que deberás crear en el backend: GET /users/
    apiClient.get('/users/').then((res) => setUsers(res.data)).catch(() => setUsers([]));
  };

  useEffect(() => { loadUsers(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      // Endpoint que deberás crear en el backend: POST /users/
      await apiClient.post('/users/', formData);
      setIsModalOpen(false);
      setFormData({ username: '', email: '', password: '', role_id: 4 });
      loadUsers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear usuario');
    }
  };

  const toggleActive = async (userId: number, currentActive: boolean) => {
    try {
      await apiClient.patch(`/users/${userId}`, { is_active: !currentActive });
      loadUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al cambiar estado');
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">Gestión de Usuarios</h1>
          <p className="text-gray-400 mt-1">Administración de cuentas y roles del sistema</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-brand-accent text-brand-dark font-semibold rounded-lg hover:bg-opacity-90"
        >
          <UserPlus size={18} /> Nuevo Usuario
        </button>
      </div>

      <div className="bg-brand-panel rounded-xl border border-brand-border overflow-hidden">
        <table className="w-full">
          <thead className="bg-brand-dark">
            <tr className="text-left text-xs text-gray-400 uppercase">
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Usuario</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Rol</th>
              <th className="px-4 py-3">Último Acceso</th>
              <th className="px-4 py-3">Estado</th>
              <th className="px-4 py-3">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-t border-brand-border hover:bg-brand-dark/50">
                <td className="px-4 py-3 text-sm">#{u.id}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <UserIcon size={14} className="text-brand-accent" />
                    <span className="font-medium">{u.username}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-400">{u.email}</td>
                <td className="px-4 py-3">
                  <span className="flex items-center gap-1 text-sm">
                    <Shield size={14} className="text-brand-accent" />
                    {ROLES.find(r => r.id === u.role_id)?.name || 'DESCONOCIDO'}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-400">
                  {u.last_login_at ? new Date(u.last_login_at).toLocaleString() : 'Nunca'}
                </td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs ${u.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                    {u.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => toggleActive(u.id, u.is_active)}
                    className={`px-3 py-1 rounded text-xs ${
                      u.is_active
                        ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                        : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                    }`}
                  >
                    {u.is_active ? 'Desactivar' : 'Activar'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {users.length === 0 && (
          <div className="text-center py-12 text-gray-400">No hay usuarios para mostrar.</div>
        )}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Crear Nuevo Usuario">
        <form onSubmit={handleCreate} className="space-y-4">
          {error && <div className="p-2 bg-red-500/10 text-red-400 text-sm rounded">{error}</div>}
          <div>
            <label className="block text-sm text-gray-300 mb-1">Usuario</label>
            <input type="text" required value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white" />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1">Email</label>
            <input type="email" required value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white" />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1">Contraseña</label>
            <input type="password" required minLength={8} value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white" />
          </div>
          <div>
            <label className="block text-sm text-gray-300 mb-1">Rol</label>
            <select value={formData.role_id}
              onChange={(e) => setFormData({ ...formData, role_id: Number(e.target.value) })}
              className="w-full px-3 py-2 bg-brand-dark border border-brand-border rounded-lg text-white">
              {ROLES.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
            </select>
          </div>
          <button type="submit" className="w-full py-2 bg-brand-accent text-brand-dark font-bold rounded-lg">
            Crear Usuario
          </button>
        </form>
      </Modal>
    </div>
  );
};