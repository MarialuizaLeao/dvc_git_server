import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { experimentsApi } from '../services/api';
import type { CreateExperimentData } from '../types/api';
import type { AxiosResponse } from 'axios';

export const useExperiments = (userId: string, projectId: string) => {
    const queryClient = useQueryClient();

    const experiments = useQuery({
        queryKey: ['experiments', userId, projectId],
        queryFn: async () => {
            console.log('Fetching experiments for user:', userId, 'project:', projectId);
            const response = await experimentsApi.list(userId, projectId);
            console.log('Experiments API response:', response.data);
            console.log('Experiments API response type:', typeof response.data);
            console.log('Experiments API response output:', response.data?.output);
            return response.data;
        },
        onError: (error: unknown) => {
            console.error('Error fetching experiments:', error);
        },
        onSuccess: (data: any) => {
            console.log('Experiments query succeeded with data:', data);
        },
    });

    const createExperiment = useMutation({
        mutationFn: (data: CreateExperimentData) => experimentsApi.create(userId, projectId, data),
        onSuccess: (data) => {
            console.log('Experiment created, invalidating queries:', data);
            console.log('Invalidating query key:', ['experiments', userId, projectId]);
            queryClient.invalidateQueries({ queryKey: ['experiments', userId, projectId] });

            // Also try to refetch immediately
            setTimeout(() => {
                console.log('Forcing immediate refetch of experiments...');
                queryClient.refetchQueries({ queryKey: ['experiments', userId, projectId] });
            }, 500);

            // Additional refetch after longer delay
            setTimeout(() => {
                console.log('Forcing delayed refetch of experiments...');
                queryClient.refetchQueries({ queryKey: ['experiments', userId, projectId] });
            }, 2000);
        },
        onError: (error) => {
            console.error('Error creating experiment:', error);
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