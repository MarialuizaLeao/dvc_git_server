export const API_BASE_URL = 'http://localhost:8000';

export const API_ENDPOINTS = {
    // Project management
    PROJECTS: (userId: string) => `${API_BASE_URL}/${userId}/projects`,
    PROJECT: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/projects/${projectId}`,

    // DVC operations
    DVC_STATUS: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/dvc/status`,
    DVC_ADD: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/dvc/add`,
    DVC_COMMIT: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/dvc/commit`,
    DVC_PUSH: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/dvc/push`,
    DVC_PULL: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/dvc/pull`,

    // Pipeline management
    PIPELINES: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/pipelines`,
    PIPELINE: (userId: string, projectId: string, pipelineId: string) => `${API_BASE_URL}/${userId}/${projectId}/pipelines/${pipelineId}`,
    PIPELINE_STAGES: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/pipelines/stages`,
    PIPELINE_CONFIG: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/pipelines/config`,
    PIPELINE_EXECUTE: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/pipeline/execute`,
    PIPELINE_RUN: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/pipeline/run`,

    // Pipeline execution history
    PIPELINE_EXECUTIONS: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/pipeline/executions`,
    PIPELINE_EXECUTION: (userId: string, projectId: string, executionId: string) => `${API_BASE_URL}/${userId}/${projectId}/pipeline/executions/${executionId}`,
    LATEST_PIPELINE_EXECUTION: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/pipeline/executions/latest`,

    // Data sources and remotes
    DATA_SOURCES: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/data-sources`,
    REMOTE_STORAGES: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/remote-storages`,

    // Code management
    CODE_FILES: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/code/files`,
    CODE_UPLOAD: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/code/upload`,
    CODE_FILE_CONTENT: (userId: string, projectId: string, fileId: string) => `${API_BASE_URL}/${userId}/${projectId}/code/file/${fileId}/content`,
    CODE_FILE_DELETE: (userId: string, projectId: string, fileId: string) => `${API_BASE_URL}/${userId}/${projectId}/code/file/${fileId}`,

    // Parameter management
    PARAMETERS: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/parameters`,
    CURRENT_PARAMETERS: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/parameters/current`,
    VALIDATE_PARAMETERS: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/parameters/validate`,
    EXPORT_PARAMETERS: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/parameters/export`,
    IMPORT_PARAMETERS: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/parameters/import`,
    UPLOAD_PARAMETERS: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/parameters/upload`,

    // Model management
    MODELS: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/models`,
    MODEL: (userId: string, projectId: string, modelId: string) => `${API_BASE_URL}/${userId}/${projectId}/models/${modelId}`,
    MODEL_UPLOAD: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/models/upload`,
    MODEL_DOWNLOAD: (userId: string, projectId: string, modelId: string) => `${API_BASE_URL}/${userId}/${projectId}/models/${modelId}/download`,
    MODEL_DELETE: (userId: string, projectId: string, modelId: string) => `${API_BASE_URL}/${userId}/${projectId}/models/${modelId}`,
    MODEL_COMPARE: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/models/compare`,

    // Project model files (actual files from project directory)
    PROJECT_MODEL_FILES: (userId: string, projectId: string) => `${API_BASE_URL}/${userId}/${projectId}/models/files`,
}; 