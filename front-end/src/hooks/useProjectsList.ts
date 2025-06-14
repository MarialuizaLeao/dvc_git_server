import { useQuery } from '@tanstack/react-query';
import { projectApi } from '../services/api';
import type { Project } from '../types/api';
import { CURRENT_USER } from '../constants/user';

export function useProjectsList() {
    return useQuery<Project[]>({
        queryKey: ['projects', CURRENT_USER.id],
        queryFn: () => projectApi.getProjects(CURRENT_USER.id),
    });
} 