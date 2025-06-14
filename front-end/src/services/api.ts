import axios from 'axios';
import type { User, Project, CreateProjectRequest, CreateExperimentData, Pipeline, CreatePipelineRequest, UpdatePipelineRequest, PipelineExecutionRequest, PipelineExecutionResponse, PipelineRecoveryResponse } from '../types/api';

// Create axios instance
const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add response interceptor for error handling
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            const message = error.response.data.detail || error.response.data.message || 'An error occurred';
            throw new Error(message);
        } else if (error.request) {
            // The request was made but no response was received
            throw new Error('No response received from server');
        } else {
            // Something happened in setting up the request that triggered an Error
            throw new Error('Error setting up the request');
        }
    }
);

// API functions
export const projectApi = {
    // User management
    getUsers: async () => {
        const response = await api.get<User[]>('/users/');
        return response.data;
    },

    // Project management
    createProject: async (userId: string, data: CreateProjectRequest) => {
        const response = await api.post<{ message: string; id: string }>(
            `/${userId}/project/create`,
            data
        );
        return response.data;
    },

    getProjects: async (userId: string) => {
        const response = await api.get<{ projects: Project[] }>(`/${userId}/projects`);
        return response.data.projects;
    },

    getProject: async (userId: string, projectId: string) => {
        const response = await api.get<Project>(`/${userId}/project/${projectId}`);
        return response.data;
    },

    // DVC operations
    trackData: async (userId: string, projectId: string, files: string[]) => {
        const response = await api.post(`/${userId}/${projectId}/track_data`, { files });
        return response.data;
    },

    trackFiles: async (userId: string, projectId: string, files: string[]) => {
        const response = await api.post(`/${userId}/${projectId}/track_files`, { files });
        return response.data;
    },

    getUrl: async (userId: string, projectId: string, url: string, dest: string) => {
        const response = await api.post(`/${userId}/${projectId}/get_url`, { url, dest });
        return response.data;
    },

    setRemote: async (userId: string, projectId: string, remoteUrl: string, remoteName?: string) => {
        const response = await api.get(`/${userId}/${projectId}/set_remote`, {
            params: { remote_url: remoteUrl, remote_name: remoteName }
        });
        return response.data;
    },

    pushData: async (userId: string, projectId: string) => {
        const response = await api.post(`/${userId}/${projectId}/push`);
        return response.data;
    },

    pullData: async (userId: string, projectId: string) => {
        const response = await api.post(`/${userId}/${projectId}/pull`);
        return response.data;
    },

    listDvcBranches: async (userId: string, projectId: string) => {
        const response = await api.get(`/${userId}/${projectId}/list_dvc_branches`);
        return response.data;
    },

    // Metrics and plots
    getMetrics: async (userId: string, projectId: string, params?: {
        all_commits?: boolean;
        json?: boolean;
        yaml?: boolean;
    }) => {
        const response = await api.get(`/${userId}/${projectId}/metrics_show`, { params });
        return response.data;
    },

    getMetricsDiff: async (userId: string, projectId: string, params: {
        a_rev?: string;
        b_rev?: string;
        all?: boolean;
        precision?: number;
        json?: boolean;
        csv?: boolean;
        md?: boolean;
    }) => {
        const response = await api.get(`/${userId}/${projectId}/metrics_diff`, { params });
        return response.data;
    },

    showPlots: async (userId: string, projectId: string, params?: {
        targets?: string[];
        json?: boolean;
        html?: boolean;
        no_html?: boolean;
        templates_dir?: string;
        out?: string;
    }) => {
        const response = await api.get(`/${userId}/${projectId}/plots_show`, { params });
        return response.data;
    },

    diffPlots: async (userId: string, projectId: string, params?: {
        targets?: string[];
        a_rev?: string;
        b_rev?: string;
        templates_dir?: string;
        json?: boolean;
        html?: boolean;
        no_html?: boolean;
        out?: string;
    }) => {
        const response = await api.get(`/${userId}/${projectId}/plots_diff`, { params });
        return response.data;
    },

    // Experiments
    listExperiments: async (userId: string, projectId: string, gitRemote?: string) => {
        const response = await api.get(`/${userId}/${projectId}/exp/list`, {
            params: { git_remote: gitRemote }
        });
        return response.data;
    },

    showExperiments: async (userId: string, projectId: string, params?: {
        quiet?: boolean;
        verbose?: boolean;
        all?: boolean;
        sha?: boolean;
        param_deps?: boolean;
        sort_by?: string;
        sort_order?: string;
    }) => {
        const response = await api.get(`/${userId}/${projectId}/exp/show`, { params });
        return response.data;
    },

    applyExperiment: async (userId: string, projectId: string, experimentId: string, force?: boolean) => {
        const response = await api.post(`/${userId}/${projectId}/exp/apply`, {
            experiment_id: experimentId,
            force
        });
        return response.data;
    },

    pushExperiment: async (userId: string, projectId: string, params?: {
        git_remote?: string;
        experiment_id?: string;
        force?: boolean;
    }) => {
        const response = await api.post(`/${userId}/${projectId}/exp/push`, params);
        return response.data;
    },

    pullExperiment: async (userId: string, projectId: string, params?: {
        git_remote?: string;
        experiment_id?: string;
    }) => {
        const response = await api.post(`/${userId}/${projectId}/exp/pull`, params);
        return response.data;
    },

    // Pipeline operations
    getPipeline: async (userId: string, projectId: string) => {
        const response = await api.get<Pipeline>(
            `/${userId}/${projectId}/pipeline`
        );
        return response.data;
    },

    createPipeline: async (userId: string, projectId: string, data: CreatePipelineRequest) => {
        const response = await api.post<{ message: string; id: string }>(
            `/${userId}/${projectId}/pipeline`,
            data
        );
        return response.data;
    },

    updatePipeline: async (userId: string, projectId: string, data: UpdatePipelineRequest) => {
        const response = await api.put<{ message: string }>(
            `/${userId}/${projectId}/pipeline`,
            data
        );
        return response.data;
    },

    deletePipeline: async (userId: string, projectId: string) => {
        const response = await api.delete<{ message: string }>(
            `/${userId}/${projectId}/pipeline`
        );
        return response.data;
    },

    executePipeline: async (userId: string, projectId: string, data: PipelineExecutionRequest) => {
        const response = await api.post<PipelineExecutionResponse>(
            `/${userId}/${projectId}/pipeline/execute`,
            data
        );
        return response.data;
    },

    recoverPipeline: async (userId: string, projectId: string) => {
        const response = await api.post<PipelineRecoveryResponse>(
            `/${userId}/${projectId}/pipeline/recover`
        );
        return response.data;
    }
};

export const experimentsApi = {
    list: async (projectId: string) => {
        const response = await api.get(`/experiments/${projectId}/list`);
        return response;
    },
    create: async (data: CreateExperimentData) => {
        const response = await api.post('/experiments/create', data);
        return response;
    },
    start: async (experimentId: string) => {
        const response = await api.post(`/experiments/${experimentId}/start`);
        return response;
    },
    stop: async (experimentId: string) => {
        const response = await api.post(`/experiments/${experimentId}/stop`);
        return response;
    },
    getMetrics: async (experimentId: string) => {
        const response = await api.get(`/experiments/${experimentId}/metrics`);
        return response;
    }
};

export default api; 