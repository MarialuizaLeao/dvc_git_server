import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectsApi } from '../services/api';
import type { CreateProjectData } from '../services/api';

export const useProjects = () => {
    const queryClient = useQueryClient();

    const projects = useQuery({
        queryKey: ['projects'],
        queryFn: () => projectsApi.list().then((res) => res.data),
    });

    const createProject = useMutation({
        mutationFn: (data: CreateProjectData) => projectsApi.create(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects'] });
        },
    });

    const deleteProject = useMutation({
        mutationFn: (projectId: string) => projectsApi.delete(projectId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['projects'] });
        },
    });

    const getProject = (projectId: string) =>
        useQuery({
            queryKey: ['project', projectId],
            queryFn: () => projectsApi.get(projectId).then((res) => res.data),
            enabled: !!projectId,
        });

    return {
        projects,
        createProject,
        deleteProject,
        getProject,
    };
}; 