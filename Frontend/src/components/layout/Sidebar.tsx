import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Folder, FileText, ShieldAlert, Activity, ClipboardList, LogOut, Users, Archive } from 'lucide-react';
import { useAuth } from '../../features/auth/AuthContext';

const menuItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/repositories', label: 'Repositorios', icon: Folder },
  { path: '/assets', label: 'Inventario', icon: Archive },
  { path: '/baselines', label: 'Líneas Base', icon: FileText },
  { path: '/alerts', label: 'Alertas', icon: ShieldAlert },
  { path: '/events', label: 'Eventos', icon: Activity },
  { path: '/audit', label: 'Auditoría', icon: ClipboardList },
  { path: '/users', label: 'Usuarios', icon: Users },
];

export const Sidebar = () => {
  const location = useLocation();
  const { user, logout } = useAuth();

  // Filtrar menú según rol
  const visibleItems = menuItems.filter(item => {
    if (item.path === '/users' && user?.role_id !== 1) return false; // Solo ADMIN
    if (item.path === '/audit' && user?.role_id === 4) return false; // VIEWER no ve auditoría
    return true;
  });

  return (
    <aside className="w-64 bg-brand-panel border-r border-brand-border h-screen flex flex-col fixed left-0 top-0">
      <div className="p-6 border-b border-brand-border">
        <h1 className="text-2xl font-bold text-brand-accent">PIM-Sec</h1>
        <p className="text-xs text-gray-400 mt-1">Integrity Monitoring</p>
      </div>

      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {visibleItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-brand-accent text-brand-dark font-semibold'
                  : 'text-gray-300 hover:bg-brand-border hover:text-white'
              }`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-brand-border">
        <div className="mb-4">
          <p className="text-sm font-semibold text-white">{user?.username}</p>
          <p className="text-xs text-gray-400">{user?.email}</p>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/20 transition"
        >
          <LogOut size={16} />
          Cerrar Sesión
        </button>
      </div>
    </aside>
  );
};