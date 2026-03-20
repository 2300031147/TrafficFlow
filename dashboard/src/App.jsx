import React, { useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import CommandCenter from './pages/CommandCenter';
import JunctionDetail from './pages/JunctionDetail';
import Login from './pages/Login';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 10000,
      retry: 1
    }
  }
});

function AuthListener({ children }) {
  const navigate = useNavigate();
  useEffect(() => {
    const handleAuthExpired = () => navigate('/login');
    window.addEventListener('auth:expired', handleAuthExpired);
    return () => window.removeEventListener('auth:expired', handleAuthExpired);
  }, [navigate]);
  return children;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthListener>
          <Routes>
            <Route path="/" element={<CommandCenter />} />
            <Route path="/junction/:junction_id" element={<JunctionDetail />} />
            <Route path="/login" element={<Login />} />
          </Routes>
        </AuthListener>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
