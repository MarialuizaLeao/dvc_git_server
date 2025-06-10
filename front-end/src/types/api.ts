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

// API Response types
export interface ApiResponse<T> {
    data: T;
    message?: string;
    error?: string;
} 