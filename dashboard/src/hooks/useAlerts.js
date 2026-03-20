import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import client from '../api/client';

export const useAlerts = () => {
  return useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const res = await client.get('/alerts');
      const alerts = res.data?.data || res.data || [];
      const unreadCount = alerts.filter(a => a.resolved_at === null).length;
      return { data: alerts, unreadCount };
    },
    refetchInterval: 10000
  });
};

export const useResolveAlert = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ alertId, note }) => {
      const res = await client.post(`/alerts/${alertId}/resolve`, { resolution_note: note });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    }
  });
};
