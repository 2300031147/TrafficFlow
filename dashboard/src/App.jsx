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

class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false }; }
  static getDerivedStateFromError(error) { return { hasError: true }; }
  componentDidCatch(error, errorInfo) { console.error("Dashboard crashed:", error, errorInfo); }
  render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-screen items-center justify-center bg-[#050810] text-[#ef4444] font-mono flex-col gap-4">
          <h1 className="text-2xl font-bold tracking-widest">SYSTEM ERROR</h1>
          <p className="text-sm text-[#94a3b8]">UI component crashed or Network unreachabale.</p>
          <button onClick={() => window.location.reload()} className="px-4 py-2 mt-4 border border-[#3d8ef8] text-white hover:bg-[rgba(15,21,37,0.8)] tracking-widest rounded transition-all">REBOOT TERMINAL</button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthListener>
          <ErrorBoundary>
            <Routes>
              <Route path="/" element={<CommandCenter />} />
              <Route path="/junction/:junction_id" element={<JunctionDetail />} />
              <Route path="/login" element={<Login />} />
            </Routes>
          </ErrorBoundary>
        </AuthListener>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
