import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { experimentsApi } from '../services/api';
import type { CreateExperimentData } from '../types/api';
import type { AxiosResponse } from 'axios';

export const useExperiments = (userId: string, projectId: string) => {
    const queryClient = useQueryClient();

    const experiments = useQuery({
        queryKey: ['experiments', userId, projectId],
        queryFn: async () => {
            const response = await experimentsApi.list(userId, projectId);
            return response.data;
        },
    });

    const createExperiment = useMutation({
        mutationFn: (data: CreateExperimentData) => experimentsApi.create(userId, projectId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['experiments', userId, projectId] });
        },
    });

    const startExperiment = useMutation({
        mutationFn: (experimentId: string) => experimentsApi.start(userId, projectId, experimentId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['experiments', userId, projectId] });
        },
    });

    const stopExperiment = useMutation({
        mutationFn: (experimentId: string) => experimentsApi.stop(userId, projectId, experimentId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['experiments', userId, projectId] });
        },
    });

    const getMetrics = (experimentId: string) =>
        useQuery({
            queryKey: ['metrics', userId, projectId, experimentId],
            queryFn: () => experimentsApi.getMetrics(userId, projectId, experimentId).then((res: AxiosResponse) => res.data),
            enabled: !!experimentId,
        });

    return {
        experiments,
        createExperiment,
        startExperiment,
        stopExperiment,
        getMetrics,
    };
}; 