import React, { useState } from 'react';
import client from '../api/client';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await client.post('/auth/login', { email, password });
      navigate('/');
    } catch (err) {
      if (err.response?.status === 401) {
        setError('Invalid credentials');
      } else if (err.response?.status === 423) {
        setError('Account locked — try again later');
      } else {
        setError('Authentication Failed. Access Denied.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex h-screen items-center justify-center bg-[var(--bg)] m-0 font-mono text-[var(--text)] overflow-hidden">
      {/* Dynamic Background Elements */}
      <div className="absolute top-0 left-0 w-full h-full scan-lines pointer-events-none"></div>

      <form 
        onSubmit={onSubmit} 
        className="glass-panel p-10 max-w-md w-full rounded-[8px] relative z-10 transition-all duration-500"
      >
        <div className="flex flex-col items-center mb-10">
          <div className="w-20 h-20 rounded-full border border-[var(--border)] flex items-center justify-center mb-6 bg-[var(--surface-solid)] relative group">
             <div className="absolute inset-0 rounded-full border border-[var(--accent)] opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
             <div className="absolute inset-2 rounded-full border border-[var(--border)] opacity-50"></div>
             <span className="font-rajdhani text-3xl font-bold text-[var(--accent)] tracking-widest ml-1">UF</span>
          </div>
          <h2 className="font-rajdhani text-5xl font-bold uppercase tracking-[0.2em] text-center mb-3 text-white">
            UrbanFlow
          </h2>
          <h3 className="text-xs uppercase tracking-[0.35em] text-center text-[var(--accent)] opacity-80">
            Command Access Protocol
          </h3>
        </div>
        
        {error && (
          <div className="bg-[rgba(239,68,68,0.1)] border border-[var(--danger)] text-[var(--danger)] text-sm mb-6 p-4 rounded-lg text-center animate-pulse flex items-center justify-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[var(--danger)]"></span>
            <span className="tracking-wide">ERR: {error}</span>
          </div>
        )}
        
        <div className="flex flex-col gap-6">
          <div className="relative group/input">
            <input 
              type="email" 
              placeholder="OPERATOR ID / EMAIL" 
              className="peer w-full bg-[var(--surface-solid)] border border-[var(--border)] p-4 pt-5 text-sm text-[var(--text)] placeholder-transparent outline-none rounded-xl focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] transition-all"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
            <label className="absolute left-4 top-1 text-[10px] text-[var(--muted)] peer-placeholder-shown:top-4 peer-placeholder-shown:text-sm peer-focus:top-1 peer-focus:text-[10px] peer-focus:text-[var(--accent)] transition-all uppercase tracking-wider font-bold pointer-events-none">
              Operator ID / Email
            </label>
          </div>
          
          <div className="relative group/input">
            <input 
              type="password" 
              placeholder="PASSPHRASE" 
              className="peer w-full bg-[var(--surface-solid)] border border-[var(--border)] p-4 pt-5 text-sm text-[var(--text)] placeholder-transparent outline-none rounded-xl focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] transition-all"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
            <label className="absolute left-4 top-1 text-[10px] text-[var(--muted)] peer-placeholder-shown:top-4 peer-placeholder-shown:text-sm peer-focus:top-1 peer-focus:text-[10px] peer-focus:text-[var(--accent)] transition-all uppercase tracking-wider font-bold pointer-events-none">
              Passphrase
            </label>
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="mt-6 bg-[var(--accent)] text-white hover:brightness-125 transition-all font-rajdhani py-4 uppercase tracking-[0.25em] font-bold rounded-[8px] relative overflow-hidden group disabled:opacity-70 disabled:cursor-not-allowed"
          >
            <span className="relative z-10 flex items-center justify-center gap-3">
               {loading ? (
                 <>
                   <div className="w-5 h-5 rounded-full border-2 border-[var(--surface-solid)] border-t-white animate-spin"></div>
                   <span>AUTHENTICATING...</span>
                 </>
               ) : 'Initiate Handshake'}
            </span>
          </button>
        </div>
      </form>
    </div>
  );
}
