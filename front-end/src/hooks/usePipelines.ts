import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectApi } from '../services/api';
import type {
    CreatePipelineRequest,
    UpdatePipelineRequest,
    PipelineExecutionRequest
} from '../types/api';

export const usePipelines = (userId: string, projectId: string) => {
    const queryClient = useQueryClient();

    const getPipeline = () => useQuery({
        queryKey: ['pipeline', userId, projectId],
        queryFn: () => projectApi.getPipeline(userId, projectId),
    });

    const createPipeline = useMutation({
        mutationFn: (data: CreatePipelineRequest) =>
            projectApi.createPipeline(userId, projectId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['pipeline', userId, projectId] });
        },
    });

    const updatePipeline = useMutation({
        mutationFn: (data: UpdatePipelineRequest) =>
            projectApi.updatePipeline(userId, projectId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['pipeline', userId, projectId] });
        },
    });

    const deletePipeline = useMutation({
        mutationFn: () =>
            projectApi.deletePipeline(userId, projectId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['pipeline', userId, projectId] });
        },
    });

    const executePipeline = useMutation({
        mutationFn: (data: PipelineExecutionRequest) =>
            projectApi.executePipeline(userId, projectId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['pipeline', userId, projectId] });
        },
    });

    const recoverPipeline = useMutation({
        mutationFn: () =>
            projectApi.recoverPipeline(userId, projectId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['pipeline', userId, projectId] });
        },
    });

    return {
        getPipeline,
        createPipeline,
        updatePipeline,
        deletePipeline,
        executePipeline,
        recoverPipeline,
    };
}; 