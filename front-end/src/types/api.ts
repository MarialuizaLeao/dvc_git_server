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
    stages_applied: number;
}

// API Response types
export interface ApiResponse<T> {
    data: T;
    message?: string;
    error?: string;
} 