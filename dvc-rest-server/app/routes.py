from fastapi import APIRouter, HTTPException
from app.classes import ProjectRequest, TrackRequest, StagesRequest, ExperimentRunRequest, project, user, GetUrlRequest, SetRemoteRequest
from bson.objectid import ObjectId
from typing import List, Optional
from app.init_db import users_collection, projects_collection
from pydantic import BaseModel
from app.dvc_handler import (
    create_project as dvc_create_project,
    track_data as dvc_track_data,
    get_url as dvc_get_url,
    set_remote as dvc_set_remote,
    push_data as dvc_push_data,
    pull_data as dvc_pull_data,
    list_dvc_branches as dvc_list_dvc_branches,
    checkout_dvc_branch as dvc_checkout_dvc_branch,
    create_dvc_branch as dvc_create_dvc_branch,
    delete_dvc_branch as dvc_delete_dvc_branch,
    add_stages,
    run_experiment,
    define_pipeline,
    run_pipeline
)
from app.git_handler import create_or_get_repo
import os

router = APIRouter()

@router.get("/users/")
async def get_users():
    users = []
    async for user in users_collection.find():
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        users.append(user)
    return users
    
@router.post("/project/create")
async def create_new_project(request: ProjectRequest):
    """
    Creates a new project directory and initializes Git/DVC.
    """
    # Check if user exists
    user = await users_collection.find_one({"_id": ObjectId(request.user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if project name is unique for the user
    project = await projects_collection.find_one({"project_name": request.project_name, "user_id": request.user_id})
    if project:
        raise HTTPException(status_code=400, detail="Project name already exists for the user")
    
    try:
        # Save the project details to the database
        project_data = request.dict()
        result = await projects_collection.insert_one(project_data)

        # Add the project to the user's projects array
        await users_collection.update_one(
            {"_id": ObjectId(request.user_id)}, {"$push": {"projects": str(result.inserted_id)}}
        )
        
        # Create the project directory and initialize DVC
        project_path = await dvc_create_project(request.user_id, str(result.inserted_id))
            
        return {
            "message": f"Project {request.project_name} for user {request.username} created successfully.",
            "id": str(result.inserted_id)
        }
    except Exception as e:
        # Rollback the project creation
        await projects_collection.delete_one({"_id": ObjectId(request.user_id)})
        # Remove the project from the user's projects array
        await users_collection.update_one(
            {"_id": ObjectId(request.user_id)}, {"$pull": {"projects": str(result.inserted_id)}}
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/project/{user_id}/{project_id}/get_url")
async def get_url(user_id: str, project_id: str, request: GetUrlRequest):
    """
    Gets the URL of a file tracked by DVC.
    """
    try:
        result = await dvc_get_url(user_id, project_id, request.url, request.dest)
        return {"url": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/project/{user_id}/{project_id}/set_remote")
async def set_project_remote(user_id: str, project_id: str, request: SetRemoteRequest):
    """
    Sets a remote storage for the project.
    """
    try:
        # Assuming `set_remote` is the handler function for setting DVC remotes
        result = await dvc_set_remote(user_id, project_id, request.remote_url, request.remote_name)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/project/{user_id}/{project_id}/push")
async def push_project_data(user_id: str, project_id: str):
    """
    Pushes the project data to the remote storage.
    """
    try:
        # Assuming `push_data` is the handler function for pushing DVC data to remotes
        result = await dvc_push_data(user_id, project_id)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/project/{user_id}/{project_id}/pull")
async def pull_project_data(user_id: str, project_id: str):
    """
    Pulls the project data from the remote storage.
    """
    try:
        # Assuming `pull_data` is the handler function for pulling DVC data from remotes
        result = await dvc_pull_data(user_id, project_id)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/project/{user_id}/{project_id}/list_dvc_branches")
async def list_dvc_branches(user_id: str, project_id: str):
    """
    Lists the DVC branches for the project.
    """
    try:
        # Assuming `list_dvc_branches` is the handler function for listing DVC branches
        result = await dvc_list_dvc_branches(user_id, project_id)
        return {"branches": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/project/{user_id}/{project_id}/track")
async def track_project_data(user_id: str, project_id: str, request: TrackRequest):
    """
    Tracks data files and directories.
    """
    try:
        result = await dvc_track_data(user_id, project_id, request.files)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/project/{user_id}/{project_id}/stages")
async def add_project_stages(user_id: str, project_id: str, request: StagesRequest):
    """
    Adds DVC stages to the project.
    """
    try:
        # Call the handler to add stages
        result = await add_stages(user_id, project_id, request.stages)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/project/{user_id}/{project_id}/experiment/run")
async def run_project_experiment(user_id: str, project_id: str, request: ExperimentRunRequest):
    """
    Runs a DVC experiment.
    """
    try:
        # Assuming `run_experiment` is the handler function for executing DVC experiments
        result = await run_experiment(user_id, project_id, request.experiment_name, request.command)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/project/{user_id}/{project_id}/define_pipeline")
async def define_project_pipeline(user_id: str, project_id: str):
    """
    Defines a DVC pipeline for the project.
    """
    try:
        # Assuming `define_pipeline` is the handler function for defining DVC pipelines
        result = await define_pipeline(user_id, project_id)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/project/{user_id}/{project_id}/run_pipeline")
async def run_project_pipeline(user_id: str, project_id: str):
    """
    Runs the DVC pipeline for the project.
    """
    try:
        # Assuming `run_pipeline` is the handler function for running DVC pipelines
        result = await run_pipeline(user_id, project_id)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))