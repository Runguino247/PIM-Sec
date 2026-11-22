import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './features/auth/AuthContext';
import { LoginPage } from './features/auth/LoginPage';
import { Layout } from './components/layout/Layout';
import { DashboardPage } from './features/dashboard/DashboardPage';
import { RepositoriesPage } from './features/repositories/RepositoriesPage';
import { AlertsPage } from './features/alerts/AlertsPage';
import { EventsPage } from './features/events/EventsPage';
import { AuditPage } from './features/audit/AuditPage';

// import { BaselinesPage } from './features/baselines/BaseLinesPage';
import { AssetsPage } from './features/assets/AssetsPage';
import { UsersPage } from './features/users/UsersPage';
import { BaselinesPage } from './features/baselines/BaselinesPage';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, isLoading } = useAuth();
  if (isLoading) return <div className="min-h-screen flex items-center justify-center">Cargando...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="assets" element={<AssetsPage />} />
        <Route path="repositories" element={<RepositoriesPage />} />
        <Route path="baselines" element={<BaselinesPage />} />
        <Route path="alerts" element={<AlertsPage />} />
        <Route path="events" element={<EventsPage />} />
        <Route path="audit" element={<AuditPage />} />
        <Route path="users" element={<UsersPage />} />
        {/* Aquí irás agregando las demás rutas: /repositories, /alerts, /audit, etc. */}
      </Route>
    </Routes>
  );
};

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}