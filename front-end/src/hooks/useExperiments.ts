import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { experimentsApi } from '../services/api';
import type { CreateExperimentData } from '../services/api';

export const useExperiments = (projectId: string) => {
    const queryClient = useQueryClient();

    const experiments = useQuery({
        queryKey: ['experiments', projectId],
        queryFn: () => experimentsApi.list(projectId).then((res) => res.data),
    });

    const createExperiment = useMutation({
        mutationFn: (data: CreateExperimentData) => experimentsApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['experiments', projectId] });
        },
    });

    const startExperiment = useMutation({
        mutationFn: (experimentId: string) => experimentsApi.start(experimentId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['experiments', projectId] });
        },
    });

    const stopExperiment = useMutation({
        mutationFn: (experimentId: string) => experimentsApi.stop(experimentId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['experiments', projectId] });
        },
    });

    const getMetrics = (experimentId: string) =>
        useQuery({
            queryKey: ['metrics', experimentId],
            queryFn: () => experimentsApi.getMetrics(experimentId).then((res) => res.data),
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