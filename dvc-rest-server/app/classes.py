from pydantic import BaseModel, Field
from typing import List, Optional

class ProjectRequest(BaseModel):
    username: str
    project_name: str
    
class StagesRequest(BaseModel):
    stages: list[str]  # Expecting a list of stage commands as strings
    
class ExperimentRunRequest(BaseModel):
    experiment_name: str
    command: str = ""  # Optional command argument
    
class TrackRequest(BaseModel):
    files: list[str]
    
# Pydantic Models
class project(BaseModel):
    user_id: str
    name: str

class user(BaseModel):
    username: str
    user_directory: str
    projects: List[str] = Field(default_factory=list)
    
class GetUrlRequest(BaseModel): 
    url: str
    dest: str = None
    
class SetRemoteRequest(BaseModel):
    remote_url: str
    remote_name: str = "origin"
    
class StageRequest(BaseModel):
    name: str
    deps: list = None
    outs: list = None
    params: list = None
    metrics: list = None
    plots: list = None
    command: str
    
class PullExperimentRequest(BaseModel):
    git_remote: str
    experiment_id: str
    
class PushExperimentRequest(BaseModel):
    git_remote: str
    experiment_id: str
    
class SaveExperimentRequest(BaseModel):
    name: str = None
    force: bool = False    
    
class RemoveExperimentsRequest(BaseModel):
    experiment_ids: List[str] = None
    queue: bool = False
    
class ApplyExperimentRequest(BaseModel):
    experiment_id: str
    
class ListExperimentsRequest(BaseModel):
    git_remote: str = None
    
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
    
class CloneRequest(BaseModel):
    remote_url: str
    
class MetricsShowRequest(BaseModel):
    all_commits: bool = False
    json: bool = False
    yaml: bool = False
    
class MetricsDiffRequest(BaseModel):
    a_rev: Optional[str] = None
    b_rev: Optional[str] = None
    all: bool = False
    precision: Optional[int] = None
    json: bool = False
    csv: bool = False
    md: bool = False
    
class PlotsShowRequest(BaseModel):
    targets: Optional[List[str]] = None
    json: bool = False
    html: bool = False
    no_html: bool = False
    templates_dir: Optional[str] = None
    out: Optional[str] = None
    
class PlotsDiffRequest(BaseModel):
    targets: Optional[List[str]] = None
    a_rev: Optional[str] = None
    b_rev: Optional[str] = None
    templates_dir: Optional[str] = None
    json: bool = False
    html: bool = False
    no_html: bool = False
    out: Optional[str] = None