// User types
export interface User {
    _id: string;
    username: string;
    projects: string[];
}

// Project types
export interface Project {
    _id: string;
    username: string;
    project_name: string;
    description?: string;
    project_type?: string;
    framework?: string;
    python_version?: string;
    dependencies?: string[];
    models_count?: number;
    experiments_count?: number;
    created_at?: string;
    status?: string;
}

export interface CreateProjectRequest {
    username: string;
    project_name: string;
    description?: string;
    project_type?: string;
    framework?: string;
    python_version?: string;
    dependencies?: string[];
}

// DVC types
export interface TrackFilesRequest {
    files: string[];
}

export interface MetricsShowRequest {
    all_commits?: boolean;
    json?: boolean;
    yaml?: boolean;
}

export interface MetricsResponse {
    metrics: Record<string, any>;
}

export interface PlotsShowRequest {
    targets?: string[];
    json?: boolean;
    html?: boolean;
    no_html?: boolean;
    templates_dir?: string;
    out?: string;
}

export interface PlotsResponse {
    output: string;
    message: string;
}

// Experiment types
export interface ExperimentRequest {
    experiment_name: string;
    set_param?: Record<string, any>;
    targets?: string[];
}

export interface ExperimentResponse {
    message: string;
    output: any;
}

export interface CreateExperimentData {
    experiment_name?: string;
    set_param?: Record<string, any>;
    targets?: string[];
    queue?: boolean;
    parallel_jobs?: number;
    temp?: boolean;
    recursive?: boolean;
    force?: boolean;
    run_all?: boolean;
    message?: string;
}

// Pipeline types
export interface PipelineStage {
    name: string;
    deps: string[];
    outs: string[];
    params?: string[];
    metrics?: string[];
    plots?: string[];
    command: string;
    description?: string;
}

export interface Pipeline {
    _id: string;
    user_id: string;
    project_id: string;
    name: string;
    description?: string;
    stages: PipelineStage[];
    version: string;
    created_at?: string;
    updated_at?: string;
    is_active: boolean;
    last_execution?: {
        execution_id: string;
        status: string;
        start_time: string;
        end_time?: string;
        output?: string;
        error?: string;
    };
}

export interface CreatePipelineRequest {
    name: string;
    description?: string;
    stages: PipelineStage[];
}

export interface UpdatePipelineRequest {
    name?: string;
    description?: string;
    stages?: PipelineStage[];
    is_active?: boolean;
}

export interface PipelineExecutionRequest {
    pipeline_config_id?: string;
    force?: boolean;
    dry_run?: boolean;
    targets?: string[];
    parameters?: Record<string, any>;
}

export interface PipelineExecutionResponse {
    execution_id: string;
    status: string;
    start_time: string;
    end_time: string;
    output?: string;
    error?: string;
}

export interface PipelineRecoveryResponse {
    message: string;
    config_name: string;
    stages_applied: number;
}

// Data Management types
export interface DataSource {
    _id: string;
    user_id: string;
    project_id: string;
    name: string;
    description?: string;
    type: 'url' | 'local' | 'remote';
    source: string; // URL, file path, or remote path
    destination: string; // Where to store in the project
    size?: number;
    format?: string;
    created_at: string;
    updated_at: string;
    status: 'pending' | 'downloading' | 'completed' | 'failed';
    error?: string;
}

export interface CreateDataSourceRequest {
    name: string;
    description?: string;
    type: 'url' | 'local' | 'remote';
    source: string;
    destination: string;
}

export interface UpdateDataSourceRequest {
    name?: string;
    description?: string;
    status?: string;
}

export interface RemoteStorage {
    _id: string;
    user_id: string;
    project_id: string;
    name: string;
    url: string;
    type: 's3' | 'gcs' | 'azure' | 'ssh' | 'local';
    is_default: boolean;
    created_at: string;
    updated_at: string;
}

export interface CreateRemoteRequest {
    name: string;
    url: string;
    type: 's3' | 'gcs' | 'azure' | 'ssh' | 'local';
    is_default?: boolean;
}

export interface TrackDataRequest {
    files: string[];
}

export interface GetUrlRequest {
    url: string;
    dest: string;
}

export interface SetRemoteRequest {
    remote_url: string;
    remote_name?: string;
}

export interface DataOperationResponse {
    message: string;
    output?: string;
    error?: string;
}

export interface DvcFile {
    path: string;
    size: number;
    hash: string;
    status: 'tracked' | 'untracked' | 'modified';
    type: 'file' | 'directory';
}

export interface DvcStatus {
    tracked: DvcFile[];
    untracked: DvcFile[];
    modified: DvcFile[];
    total_size: number;
}

// API Response types
export interface ApiResponse<T> {
    data: T;
    message?: string;
    error?: string;
}

// Pipeline Execution History types
export interface PipelineExecution {
    id?: string;
    execution_id: string;
    pipeline_config_id?: string;
    status: 'running' | 'completed' | 'failed' | 'cancelled';
    start_time: string;
    end_time?: string;
    duration?: number; // in seconds
    stages: Record<string, any>[];
    output_files: string[];
    models_produced: string[];
    logs: string[];
    error_message?: string;
    parameters_used: Record<string, any>;
    metrics: Record<string, any>;
    execution_output?: {
        stdout: string;
        stderr: string;
        structured_logs: Array<{
            type: 'stage_start' | 'stage_skipped' | 'error' | 'pipeline_status' | 'info';
            message: string;
            timestamp: string;
        }>;
        summary: {
            stages_executed: number;
            stages_skipped: number;
            stages_failed: number;
            total_stages: number;
        };
        pipeline_stats?: {
            output_files: string[];
            models_produced: string[];
            parameters_used: Record<string, any>;
            executed_stages: string[];
            skipped_stages: string[];
            failed_stages: string[];
        };
    };
}

export interface PipelineExecutionListResponse {
    executions: PipelineExecution[];
    total_count: number;
    page: number;
    page_size: number;
}

// Model Management types
export interface Model {
    id?: string;
    name: string;
    version: string;
    file_path: string;
    file_size: number;
    model_type: string;
    framework: string;
    accuracy?: number;
    created_at: string;
    updated_at: string;
    description?: string;
    tags: string[];
    metadata: Record<string, any>;
    pipeline_execution_id?: string;
}

export interface ModelCreate {
    name: string;
    version: string;
    file_path: string;
    file_size: number;
    model_type: string;
    framework: string;
    accuracy?: number;
    description?: string;
    tags?: string[];
    metadata?: Record<string, any>;
    pipeline_execution_id?: string;
}

export interface ModelUpdate {
    name?: string;
    version?: string;
    accuracy?: number;
    description?: string;
    tags?: string[];
    metadata?: Record<string, any>;
}

export interface ModelListResponse {
    models: Model[];
    total_count: number;
    page: number;
    page_size: number;
}

export interface ModelUploadResponse {
    model_id: string;
    message: string;
    file_path: string;
}

export interface ModelComparisonResult {
    comparison_id: string;
    models: Model[];
    comparison_metrics: Record<string, any>;
    comparison_date: string;
}

// Project Model Files types
export interface ProjectModelFile {
    name: string;
    path: string;
    size: number;
    modified_time: string;
    file_type: string;
}

export interface ProjectModelFilesResponse {
    files: ProjectModelFile[];
    total_count: number;
}

// Model Path Configuration types
export interface ModelPathConfig {
    _id: string;
    user_id: string;
    project_id: string;
    model_path: string;
    model_name: string;
    description?: string;
    created_at: string;
    updated_at: string;
}

export interface CreateModelPathRequest {
    model_path: string;
    model_name: string;
    description?: string;
}

export interface UpdateModelPathRequest {
    model_path?: string;
    model_name?: string;
    description?: string;
}

// Model Evaluation types
export interface ModelEvaluation {
    _id: string;
    user_id: string;
    project_id: string;
    model_path: string;
    evaluation_date: string;
    metrics: Record<string, number>;
    evaluation_logs: string[];
    status: 'running' | 'completed' | 'failed';
    error_message?: string;
    created_at: string;
    updated_at: string;
}

export interface CreateEvaluationRequest {
    model_path: string;
}

export interface EvaluationResult {
    message: string;
    evaluation_id: string;
    metrics: Record<string, number>;
    logs: string[];
} 