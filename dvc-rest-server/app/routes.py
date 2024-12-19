from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.dvc_handler import  create_project, add_stages, track_data, run_experiment, define_pipeline, run_pipeline
from app.git_handler import create_or_get_repo
import os

router = APIRouter()


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
    
    
@router.post("/project/create")
async def create_new_project(request: ProjectRequest):
    """
    Creates a new project directory and initializes Git/DVC.
    """
    try:
        project_path = create_project(request.username, request.project_name)
        return {
            "message": f"Project {request.project_name} for user {request.username} created successfully.",
            "project_path": project_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/project/{username}/{project_name}/track")
async def track_project_data(username: str, project_name: str, request: TrackRequest):
    """
    Tracks data files and directories.
    """
    try:
        result = track_data(username, project_name, request.files)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/project/{username}/{project_name}/stages")
async def add_project_stages(username: str, project_name: str, request: StagesRequest):
    """
    Adds DVC stages to the project.
    """
    try:
        # Call the handler to add stages
        result = add_stages(username, project_name, request.stages)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/project/{username}/{project_name}/experiment/run")
async def run_project_experiment(username: str, project_name: str, request: ExperimentRunRequest):
    """
    Runs a DVC experiment.
    """
    try:
        # Assuming `run_experiment` is the handler function for executing DVC experiments
        result = run_experiment(username, project_name, request.experiment_name, request.command)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/project/{username}/{project_name}/define_pipeline")
async def define_project_pipeline(username: str, project_name: str):
    """
    Defines a DVC pipeline for the project.
    """
    try:
        # Assuming `define_pipeline` is the handler function for defining DVC pipelines
        result = define_pipeline(username, project_name)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/project/{username}/{project_name}/run_pipeline")
async def run_project_pipeline(username: str, project_name: str):
    """
    Runs the DVC pipeline for the project.
    """
    try:
        # Assuming `run_pipeline` is the handler function for running DVC pipelines
        result = run_pipeline(username, project_name)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))