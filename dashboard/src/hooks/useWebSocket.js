import { useState, useEffect } from 'react';

export function useWebSocket(cityId) {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!cityId) return;
    
    let ws = null;
    let reconnectTimeout = null;
    let attempt = 0;

    const connect = () => {
      // Read the non-httpOnly ws_token cookie set by auth.py (NEW-2 fix)
      const wsToken = document.cookie.split('; ')
        .find(r => r.startsWith('ws_token='))?.split('=')[1] || '';
      const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/${cityId}${wsToken ? '?token=' + wsToken : ''}`;
      ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setConnected(true);
        attempt = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
        } catch (e) {
          console.error("WS Parse error", e);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        const backoff = Math.min(1000 * Math.pow(2, attempt), 30000);
        attempt += 1;
        reconnectTimeout = setTimeout(connect, backoff);
      };

      ws.onerror = (err) => {
        setError('WebSocket error occurred');
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      if (ws) {
        ws.onclose = null;
        ws.close();
      }
    };
  }, [cityId]);

  return { connected, lastMessage, error };
}
