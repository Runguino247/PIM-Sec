import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import { apiClient } from '../../api/client';

export const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // FastAPI OAuth2PasswordRequestForm espera form-data
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const { data } = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      await login(data.access_token);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al iniciar sesión');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-brand-dark">
      <div className="w-full max-w-md p-8 bg-brand-panel rounded-xl border border-brand-border shadow-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-brand-accent">PIM-Sec</h1>
          <p className="text-gray-400 mt-2">Monitoreo de Integridad Patrimonial</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/50 text-red-400 rounded text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Usuario</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 bg-brand-dark border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent outline-none text-white"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-brand-dark border border-brand-border rounded-lg focus:ring-2 focus:ring-brand-accent outline-none text-white"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full py-2 bg-brand-accent text-brand-dark font-bold rounded-lg hover:bg-opacity-90 transition"
          >
            Iniciar Sesión
          </button>
        </form>
      </div>
    </div>
  );
};