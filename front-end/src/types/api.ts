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
    experiment_name: string;
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