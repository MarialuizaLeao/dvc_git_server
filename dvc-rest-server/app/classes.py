from pydantic import BaseModel, Field
from typing import List, Optional

class ProjectRequest(BaseModel):
    username: str
    user_id: str = None
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