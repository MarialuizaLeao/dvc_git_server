import { useQuery } from '@tanstack/react-query';
import { projectApi } from '../services/api';
import type { Project } from '../types/api';
import { CURRENT_USER } from '../constants/user';

export function useProjectsList() {
    return useQuery<Project[]>({
        queryKey: ['projects', CURRENT_USER.id],
        queryFn: async () => {
            try {
                const projectIds = await projectApi.getProjects(CURRENT_USER.id);
                const projects = await Promise.allSettled(
                    projectIds.map(projectId =>
                        projectApi.getProject(CURRENT_USER.id, projectId)
                    )
                );

                // Filter out failed project loads and log errors
                const successfulProjects = projects
                    .filter((result): result is PromiseFulfilledResult<Project> => {
                        if (result.status === 'rejected') {
                            console.warn('Failed to load project:', result.reason);
                            return false;
                        }
                        return true;
                    })
                    .map(result => result.value);

                return successfulProjects;
            } catch (error) {
                if (error instanceof Error) {
                    throw new Error(`Failed to fetch projects: ${error.message}`);
                }
                throw error;
            }
        },
    });
} 