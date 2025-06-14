import axios from 'axios';
import type { User, Project, CreateProjectRequest, CreateExperimentData, Pipeline, CreatePipelineRequest, UpdatePipelineRequest, PipelineExecutionRequest, PipelineExecutionResponse, PipelineRecoveryResponse, DataSource, CreateDataSourceRequest, UpdateDataSourceRequest, RemoteStorage, CreateRemoteRequest, TrackDataRequest, GetUrlRequest, SetRemoteRequest, DataOperationResponse, DvcStatus } from '../types/api';

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
        // Get all pipeline configs and return the first one (since we only support one per project)
        const response = await api.get<{ pipeline_configs: Pipeline[] }>(
            `/${userId}/${projectId}/pipeline/configs`
        );
        const configs = response.data.pipeline_configs;
        if (configs.length === 0) {
            throw new Error('No pipeline found');
        }
        return configs[0]; // Return the first pipeline config
    },

    createPipeline: async (userId: string, projectId: string, data: CreatePipelineRequest) => {
        const response = await api.post<{ message: string; id: string }>(
            `/${userId}/${projectId}/pipeline/config`,
            data
        );
        return response.data;
    },

    updatePipeline: async (userId: string, projectId: string, data: UpdatePipelineRequest) => {
        // First get the pipeline to get its ID
        try {
            const pipeline = await projectApi.getPipeline(userId, projectId);
            const response = await api.put<{ message: string }>(
                `/${userId}/${projectId}/pipeline/config/${pipeline._id}`,
                data
            );
            return response.data;
        } catch (error) {
            if (error instanceof Error && error.message === 'No pipeline found') {
                throw new Error('No pipeline configuration found to update');
            }
            throw error;
        }
    },

    deletePipeline: async (userId: string, projectId: string) => {
        // First get the pipeline to get its ID
        try {
            const pipeline = await projectApi.getPipeline(userId, projectId);
            const response = await api.delete<{ message: string }>(
                `/${userId}/${projectId}/pipeline/config/${pipeline._id}`
            );
            return response.data;
        } catch (error) {
            if (error instanceof Error && error.message === 'No pipeline found') {
                throw new Error('No pipeline configuration found to delete');
            }
            throw error;
        }
    },

    executePipeline: async (userId: string, projectId: string, data: PipelineExecutionRequest) => {
        let executionData = { ...data };

        // If no pipeline_config_id is provided, get the project's pipeline
        if (!data.pipeline_config_id) {
            try {
                const pipeline = await projectApi.getPipeline(userId, projectId);
                executionData.pipeline_config_id = pipeline._id;
            } catch (error) {
                // If no pipeline exists, execute without config_id (use project's default pipeline)
                console.log('No pipeline configuration found, executing project pipeline');
            }
        }

        const response = await api.post<PipelineExecutionResponse>(
            `/${userId}/${projectId}/pipeline/execute`,
            executionData
        );
        return response.data;
    },

    recoverPipeline: async (userId: string, projectId: string) => {
        // First get the pipeline to get its ID
        try {
            const pipeline = await projectApi.getPipeline(userId, projectId);
            const response = await api.post<PipelineRecoveryResponse>(
                `/${userId}/${projectId}/pipeline/recover?config_id=${pipeline._id}`
            );
            return response.data;
        } catch (error) {
            if (error instanceof Error && error.message === 'No pipeline found') {
                throw new Error('No pipeline configuration found to recover');
            }
            throw error;
        }
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

export const dataApi = {
    // Data Management operations
    getDataSources: async (userId: string, projectId: string) => {
        const response = await api.get<{ data_sources: DataSource[] }>(
            `/${userId}/${projectId}/data/sources`
        );
        return response.data.data_sources;
    },

    getDataSource: async (userId: string, projectId: string, sourceId: string) => {
        const response = await api.get<DataSource>(
            `/${userId}/${projectId}/data/source/${sourceId}`
        );
        return response.data;
    },

    createDataSource: async (userId: string, projectId: string, data: CreateDataSourceRequest) => {
        const response = await api.post<{ message: string; id: string }>(
            `/${userId}/${projectId}/data/source`,
            data
        );
        return response.data;
    },

    updateDataSource: async (userId: string, projectId: string, sourceId: string, data: UpdateDataSourceRequest) => {
        const response = await api.put<{ message: string }>(
            `/${userId}/${projectId}/data/source/${sourceId}`,
            data
        );
        return response.data;
    },

    deleteDataSource: async (userId: string, projectId: string, sourceId: string) => {
        const response = await api.delete<{ message: string }>(
            `/${userId}/${projectId}/data/source/${sourceId}`
        );
        return response.data;
    },

    getRemoteStorages: async (userId: string, projectId: string) => {
        const response = await api.get<{ remote_storages: RemoteStorage[] }>(
            `/${userId}/${projectId}/data/remotes`
        );
        return response.data.remote_storages;
    },

    createRemoteStorage: async (userId: string, projectId: string, data: CreateRemoteRequest) => {
        const response = await api.post<{ message: string; id: string }>(
            `/${userId}/${projectId}/data/remote`,
            data
        );
        return response.data;
    },

    deleteRemoteStorage: async (userId: string, projectId: string, remoteId: string) => {
        const response = await api.delete<{ message: string }>(
            `/${userId}/${projectId}/data/remote/${remoteId}`
        );
        return response.data;
    },

    // DVC Data operations (using existing backend endpoints)
    trackData: async (userId: string, projectId: string, files: string[]) => {
        const response = await api.post<DataOperationResponse>(
            `/${userId}/${projectId}/track_data`,
            { files }
        );
        return response.data;
    },

    trackFiles: async (userId: string, projectId: string, files: string[]) => {
        const response = await api.post<DataOperationResponse>(
            `/${userId}/${projectId}/track_files`,
            { files }
        );
        return response.data;
    },

    getUrl: async (userId: string, projectId: string, url: string, dest: string) => {
        const response = await api.post<DataOperationResponse>(
            `/${userId}/${projectId}/get_url`,
            { url, dest }
        );
        return response.data;
    },

    setRemote: async (userId: string, projectId: string, remoteUrl: string, remoteName?: string) => {
        const response = await api.get<DataOperationResponse>(
            `/${userId}/${projectId}/set_remote`,
            {
                params: { remote_url: remoteUrl, remote_name: remoteName }
            }
        );
        return response.data;
    },

    pushData: async (userId: string, projectId: string) => {
        const response = await api.post<DataOperationResponse>(
            `/${userId}/${projectId}/push`
        );
        return response.data;
    },

    pullData: async (userId: string, projectId: string) => {
        const response = await api.post<DataOperationResponse>(
            `/${userId}/${projectId}/pull`
        );
        return response.data;
    },

    getDvcStatus: async (userId: string, projectId: string) => {
        const response = await api.get<DvcStatus>(
            `/${userId}/${projectId}/dvc/status`
        );
        return response.data;
    },
};

export default api; 