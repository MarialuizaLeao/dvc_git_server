from pydantic import BaseModel, Field
from typing import List, Optional, Any
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