import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

export interface CreateProjectData {
    name: string;
    description: string;
}

export interface CreateExperimentData {
    name: string;
    project_id: string;
    model: string;
    dataset: string;
    hyperparameters: Record<string, any>;
}

export const projectsApi = {
    list: () => api.get('/projects'),
    create: (data: CreateProjectData) => api.post('/projects', data),
    get: (id: string) => api.get(`/projects/${id}`),
    delete: (id: string) => api.delete(`/projects/${id}`),
};

export const experimentsApi = {
    list: (projectId: string) => api.get(`/projects/${projectId}/experiments`),
    create: (data: CreateExperimentData) => api.post('/experiments', data),
    get: (id: string) => api.get(`/experiments/${id}`),
    start: (id: string) => api.post(`/experiments/${id}/start`),
    stop: (id: string) => api.post(`/experiments/${id}/stop`),
    getMetrics: (id: string) => api.get(`/experiments/${id}/metrics`),
    getLogs: (id: string) => api.get(`/experiments/${id}/logs`),
};

export const datasetsApi = {
    list: () => api.get('/datasets'),
    upload: (formData: FormData) => api.post('/datasets/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    }),
};

export default api; 