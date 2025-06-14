from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, (str, ObjectId)):
            raise TypeError('ObjectId required')
        if isinstance(v, str) and not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: dict[str, Any]) -> dict[str, Any]:
        field_schema.update(type="string")
        return field_schema

class ProjectType(str, Enum):
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    SEGMENTATION = "segmentation"
    NLP = "nlp"
    TIME_SERIES = "time_series"
    OTHER = "other"

class Framework(str, Enum):
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    JAX = "jax"
    SCIKIT_LEARN = "scikit-learn"

class PythonVersion(str, Enum):
    V39 = "3.9"
    V310 = "3.10"
    V311 = "3.11"

class UserBase(BaseModel):
    username: str
    user_directory: str
    projects: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: str = Field(default=None, alias="_id")

    @classmethod
    def from_mongo(cls, data: dict):
        if data:
            data["_id"] = str(data["_id"])
            return cls(**data)
        return None

class ProjectRequest(BaseModel):
    username: str
    project_name: str
    description: Optional[str] = None
    project_type: Optional[str] = None
    framework: Optional[str] = None
    python_version: Optional[str] = None
    dependencies: Optional[List[str]] = None

class Project(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    username: str
    project_name: str
    description: Optional[str] = None
    project_type: Optional[str] = None
    framework: Optional[str] = None
    python_version: Optional[str] = None
    dependencies: Optional[List[str]] = None
    models_count: int = 0
    experiments_count: int = 0
    status: str = "active"
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }

class GetUrlRequest(BaseModel):
    url: str
    dest: str

class CloneRequest(BaseModel):
    remote_url: str

class SetRemoteRequest(BaseModel):
    remote_url: str
    remote_name: Optional[str] = None

class TrackRequest(BaseModel):
    files: List[str]

class StageRequest(BaseModel):
    name: str
    deps: List[str]
    outs: List[str]
    params: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    plots: Optional[List[str]] = None
    command: str

class MetricsShowRequest(BaseModel):
    all_commits: Optional[bool] = None
    output_json: Optional[bool] = None
    yaml: Optional[bool] = None

class MetricsDiffRequest(BaseModel):
    a_rev: Optional[str] = None
    b_rev: Optional[str] = None
    all: Optional[bool] = None
    precision: Optional[int] = None
    output_json: Optional[bool] = None
    csv: Optional[bool] = None
    md: Optional[bool] = None

class PlotsShowRequest(BaseModel):
    targets: Optional[List[str]] = None
    output_json: Optional[bool] = None
    html: Optional[bool] = None
    no_html: Optional[bool] = None
    templates_dir: Optional[str] = None
    out: Optional[str] = None

class PlotsDiffRequest(BaseModel):
    targets: Optional[List[str]] = None
    a_rev: Optional[str] = None
    b_rev: Optional[str] = None
    templates_dir: Optional[str] = None
    output_json: Optional[bool] = None
    html: Optional[bool] = None
    no_html: Optional[bool] = None
    out: Optional[str] = None

class ExperimentRequest(BaseModel):
    name: str
    params: Optional[dict] = None
    metrics: Optional[dict] = None
    plots: Optional[dict] = None
    description: Optional[str] = None

class ListExperimentsRequest(BaseModel):
    git_remote: Optional[str] = None

class ApplyExperimentRequest(BaseModel):
    experiment_id: str
    force: Optional[bool] = None

class PushExperimentRequest(BaseModel):
    git_remote: Optional[str] = None
    experiment_id: Optional[str] = None
    force: Optional[bool] = None

class PullExperimentRequest(BaseModel):
    git_remote: Optional[str] = None
    experiment_id: Optional[str] = None

class StagesRequest(BaseModel):
    stages: list[str]  # Expecting a list of stage commands as strings
    
class ExperimentRunRequest(BaseModel):
    experiment_name: str
    command: str = ""  # Optional command argument
    
class SaveExperimentRequest(BaseModel):
    name: str = None
    force: bool = False    
    
class RemoveExperimentsRequest(BaseModel):
    experiment_ids: List[str] = None
    queue: bool = False
    
class ShowExperimentsRequest(BaseModel):
    quiet: bool = False
    verbose: bool = False
    all: bool = False
    include_working_tree: bool = False
    all_commits: bool = False
    rev: Optional[str] = None
    num: Optional[int] = None
    no_pager: bool = False
    drop: Optional[str] = None
    keep: Optional[str] = None
    param_deps: bool = False
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None  # 'asc' or 'desc'
    sha: bool = False
    output_format: Optional[str] = None  # 'json', 'csv', 'md'
    precision: Optional[int] = None
    only_changed: bool = False
    force: bool = False
    
class RunExperimentRequest(BaseModel):
    quiet: bool = False
    verbose: bool = False
    force: bool = False
    interactive: bool = False
    single_item: bool = False
    pipeline: bool = False
    recursive: bool = False
    run_all: bool = False
    queue: bool = False
    parallel_jobs: Optional[int] = None
    temp: bool = False
    experiment_name: Optional[str] = None
    set_param: Optional[List[str]] = None
    experiment_rev: Optional[str] = None
    cwd_reset: Optional[str] = None
    message: Optional[str] = None
    downstream: bool = False
    force_downstream: bool = False
    pull: bool = False
    dry: bool = False
    allow_missing: bool = False
    keep_running: bool = False
    ignore_errors: bool = False
    targets: Optional[List[str]] = None

class PipelineStage(BaseModel):
    name: str
    deps: List[str] = []
    outs: List[str] = []
    params: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    plots: Optional[List[str]] = None
    command: str
    description: Optional[str] = None

class PipelineConfig(BaseModel):
    name: str
    description: Optional[str] = None
    stages: List[PipelineStage]
    version: str = "1.0"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_active: bool = True

class PipelineConfigCreate(BaseModel):
    name: str
    description: Optional[str] = None
    stages: List[PipelineStage]

class PipelineConfigUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    stages: Optional[List[PipelineStage]] = None
    is_active: Optional[bool] = None

class PipelineExecutionRequest(BaseModel):
    pipeline_config_id: Optional[str] = None
    force: bool = False
    dry_run: bool = False
    targets: Optional[List[str]] = None

class PipelineExecutionResult(BaseModel):
    execution_id: str
    status: str  # "running", "completed", "failed"
    start_time: str
    end_time: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None

# Data Management Models
class DataSourceType(str, Enum):
    URL = "url"
    LOCAL = "local"
    REMOTE = "remote"

class DataSourceStatus(str, Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"

class DataSource(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    project_id: str
    name: str
    description: Optional[str] = None
    type: DataSourceType
    source: str  # URL, file path, or remote path
    destination: str  # Where to store in the project
    size: Optional[int] = None
    format: Optional[str] = None
    created_at: str
    updated_at: str
    status: DataSourceStatus
    error: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }

class CreateDataSourceRequest(BaseModel):
    name: str
    description: Optional[str] = None
    type: DataSourceType
    source: str
    destination: str

class UpdateDataSourceRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[DataSourceStatus] = None

class RemoteStorageType(str, Enum):
    S3 = "s3"
    GCS = "gcs"
    AZURE = "azure"
    SSH = "ssh"
    LOCAL = "local"

class RemoteStorage(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    project_id: str
    name: str
    url: str
    type: RemoteStorageType
    is_default: bool
    created_at: str
    updated_at: str

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }

class CreateRemoteRequest(BaseModel):
    name: str
    url: str
    type: RemoteStorageType
    is_default: bool = False

# Pipeline Template and Stage Management Models
class PipelineTemplateRequest(BaseModel):
    template_name: str
    stages: List[PipelineStage]

class StageUpdateRequest(BaseModel):
    updates: dict

class PipelineRunRequest(BaseModel):
    target: Optional[str] = None
    pipeline: bool = False
    force: bool = False
    dry_run: bool = False
    no_commit: bool = False

class PipelineValidationResult(BaseModel):
    valid: bool
    message: str
    details: Optional[str] = None

class PipelineStageInfo(BaseModel):
    name: str
    deps: Optional[List[str]] = None
    outs: Optional[List[str]] = None
    params: Optional[List[str]] = None
    metrics: Optional[List[str]] = None
    plots: Optional[List[str]] = None
    cmd: Optional[str] = None

class PipelineInfo(BaseModel):
    stages: Dict[str, PipelineStageInfo]

# Code Upload Models

class CodeFileType(str, Enum):
    PYTHON = "python"
    JUPYTER = "jupyter"
    CONFIG = "config"
    DOCUMENTATION = "documentation"
    OTHER = "other"

class CodeFileStatus(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"

class CodeFile(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    project_id: str
    filename: str
    file_path: str  # Path within the project
    file_type: CodeFileType
    description: Optional[str] = None
    size: Optional[int] = None
    content_hash: Optional[str] = None
    created_at: str
    updated_at: str
    status: CodeFileStatus
    error: Optional[str] = None
    git_commit_hash: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }

class CreateCodeFileRequest(BaseModel):
    filename: str
    file_path: str  # Path within the project (e.g., "src/main.py")
    file_type: CodeFileType
    description: Optional[str] = None
    content: str  # File content as string

class UpdateCodeFileRequest(BaseModel):
    filename: Optional[str] = None
    file_path: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None

class CodeUploadResponse(BaseModel):
    message: str
    file_id: str
    file_path: str
    git_commit_hash: Optional[str] = None

class CodeFileListResponse(BaseModel):
    code_files: List[CodeFile]
    total_count: int

class BulkCodeUploadRequest(BaseModel):
    files: List[CreateCodeFileRequest]

class CodeFileSearchRequest(BaseModel):
    file_type: Optional[CodeFileType] = None
    filename_pattern: Optional[str] = None
    path_pattern: Optional[str] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0

class ParameterValue(BaseModel):
    """Represents a single parameter value with metadata."""
    name: str
    value: Any
    type: str = "string"  # string, number, boolean, array, object
    description: Optional[str] = None
    default_value: Optional[Any] = None
    required: bool = False
    validation: Optional[Dict[str, Any]] = None  # min, max, pattern, etc.
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ParameterGroup(BaseModel):
    """Represents a group of related parameters."""
    name: str
    description: Optional[str] = None
    parameters: List[ParameterValue]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ParameterSet(BaseModel):
    """Represents a complete set of parameters for a project."""
    name: str
    description: Optional[str] = None
    groups: List[ParameterGroup]
    is_default: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ParameterSetCreate(BaseModel):
    """Request model for creating a parameter set."""
    name: str
    description: Optional[str] = None
    groups: List[ParameterGroup]
    is_default: bool = False

class ParameterSetUpdate(BaseModel):
    """Request model for updating a parameter set."""
    name: Optional[str] = None
    description: Optional[str] = None
    groups: Optional[List[ParameterGroup]] = None
    is_default: Optional[bool] = None

class ParameterValueUpdate(BaseModel):
    """Request model for updating a single parameter value."""
    value: Any
    description: Optional[str] = None

class ParameterImportRequest(BaseModel):
    """Request model for importing parameters from external sources."""
    source_type: str  # yaml_file, json_file, url, etc.
    source_path: str
    parameter_set_name: str
    description: Optional[str] = None
    overwrite_existing: bool = False

class ParameterExportRequest(BaseModel):
    """Request model for exporting parameters to external formats."""
    format: str  # yaml, json, env, etc.
    include_metadata: bool = True
    include_descriptions: bool = True

class ParameterValidationRequest(BaseModel):
    """Request model for validating parameter values."""
    parameter_set_id: str
    validate_all: bool = True
    parameter_names: Optional[List[str]] = None

class ParameterDiffRequest(BaseModel):
    """Request model for comparing parameter sets."""
    base_set_id: str
    compare_set_id: str
    show_differences_only: bool = True