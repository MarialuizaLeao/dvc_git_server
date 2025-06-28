import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectApi } from '../services/api';
import type { CreateProjectRequest } from '../types/api';

export function useProjects(userId: string) {
    const queryClient = useQueryClient();

    const getProject = (projectId: string) =>
        useQuery({
            queryKey: ['project', userId, projectId],
            queryFn: () => projectApi.getProject(userId, projectId),
            enabled: !!projectId,
        });

    const getProjects = () =>
        useQuery({
            queryKey: ['projects', userId],
            queryFn: () => projectApi.getProjects(userId),
        });

    const createProject = () =>
        useMutation({
            mutationFn: (data: CreateProjectRequest) =>
                projectApi.createProject(userId, data),
            onSuccess: () => {
                // Invalidate projects list
                queryClient.invalidateQueries({ queryKey: ['projects', userId] });
            },
        });

    return {
        getProject,
        getProjects,
        createProject,
    };
} 