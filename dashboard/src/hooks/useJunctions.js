import { useQuery } from '@tanstack/react-query';
import client from '../api/client';

export const useJunctions = (city = null) => {
  return useQuery({
    queryKey: ['junctions', city],
    queryFn: async () => {
      const res = await client.get('/junctions', { params: { city } });
      return res.data?.data || res.data;
    },
    refetchInterval: parseInt(import.meta.env.VITE_REFETCH_INTERVAL || '15000', 10)
  });
};

export const useJunction = (junctionId) => {
  return useQuery({
    queryKey: ['junction', junctionId],
    queryFn: async () => {
      const res = await client.get(`/junctions/${junctionId}`);
      return res.data?.data || res.data;
    },
    enabled: !!junctionId
  });
};

export const useCountHistory = (junctionId, minutes = 60) => {
  return useQuery({
    queryKey: ['counts', junctionId, minutes],
    queryFn: async () => {
      const res = await client.get(`/junctions/${junctionId}/counts/history`, { params: { minutes } });
      return res.data?.data || res.data;
    },
    refetchInterval: 30000
  });
};

export const useSignalHistory = (junctionId, hours = 24) => {
  return useQuery({
    queryKey: ['signals', junctionId, hours],
    queryFn: async () => {
      const res = await client.get(`/junctions/${junctionId}/signals/history`, { params: { hours } });
      return res.data?.data || res.data;
    }
  });
};
