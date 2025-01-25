from fastapi import APIRouter, HTTPException
from app.classes import *
from bson.objectid import ObjectId
from typing import List, Optional
from app.init_db import users_collection, projects_collection
from pydantic import BaseModel
from app.dvc_handler import (
    create_project as dvc_create_project,
    track_data as dvc_track_data,
    track_files as dvc_track_files,
    get_url as dvc_get_url,
    set_remote as dvc_set_remote,
    push_data as dvc_push_data,
    pull_data as dvc_pull_data,
    list_dvc_branches as dvc_list_dvc_branches,
    checkout_dvc_branch as dvc_checkout_dvc_branch,
    create_dvc_branch as dvc_create_dvc_branch,
    delete_dvc_branch as dvc_delete_dvc_branch,
    add_stages,
    add_stage,
    run_experiment,
    define_pipeline,
    run_pipeline
)
from app.dvc_exp import *

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

@router.post("/{user_id}/{project_id}/get_url")
async def get_url(user_id: str, project_id: str, request: GetUrlRequest):
    """
    Gets the URL of a file tracked by DVC.
    """
    try:
        result = await dvc_get_url(user_id, project_id, request.url, request.dest)
        return {"url": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{user_id}/{project_id}/set_remote")
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

@router.post("/{user_id}/{project_id}/push")
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

@router.post("/{user_id}/{project_id}/pull")
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

@router.get("/{user_id}/{project_id}/list_dvc_branches")
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

@router.post("/{user_id}/{project_id}/track_data")
async def track_project_data(user_id: str, project_id: str, request: TrackRequest):
    """
    Tracks data files and directories.
    """
    try:
        result = await dvc_track_data(user_id, project_id, request.files)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/{user_id}/{project_id}/track_files")
async def track_project_files(user_id: str, project_id: str, request: TrackRequest):
    """
    Tracks data files and directories.
    """
    try:
        result = await dvc_track_files(user_id, project_id, request.files)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/{project_id}/stages")
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
    
@router.post("/{user_id}/{project_id}/stage")
async def add_project_stage(user_id: str, project_id: str, request: StageRequest):
    """
    Adds a DVC stage to the project.
    """
    try:
        # Call the handler to add stages
        result = await add_stage(user_id, project_id, request.name, request.deps, request.outs, request.params, request.metrics, request.plots, request.command)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/{user_id}/{project_id}/experiment/run")
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

@router.get("/{user_id}/{project_id}/define_pipeline")
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
    
@router.get("/{user_id}/{project_id}/run_pipeline")
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
    
@router.post("/{user_id}/{project_id}/exp/run")
async def run_experiment(user_id: str, project_id:str, request: RunExperimentRequest):
    try:
        result = await dvc_exp_run(
            user_id, project_id,
            quiet=request.quiet,
            verbose=request.verbose,
            force=request.force,
            interactive=request.interactive,
            single_item=request.single_item,
            pipeline=request.pipeline,
            recursive=request.recursive,
            run_all=request.run_all,
            queue=request.queue,
            parallel_jobs=request.parallel_jobs,
            temp=request.temp,
            experiment_name=request.experiment_name,
            set_param=request.set_param,
            experiment_rev=request.experiment_rev,
            cwd_reset=request.cwd_reset,
            message=request.message,
            downstream=request.downstream,
            force_downstream=request.force_downstream,
            pull=request.pull,
            dry=request.dry,
            allow_missing=request.allow_missing,
            keep_running=request.keep_running,
            ignore_errors=request.ignore_errors,
            targets=request.targets,
        )
        return {"message": "Experiment run successfully", "output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/{project_id}/exp/show")
async def show_experiments(user_id: str, project_id:str, request: ShowExperimentsRequest): 
    try:
        result = await dvc_exp_show(user_id, project_id, quiet=request.quiet,
            verbose=request.verbose,
            all=request.all,
            include_working_tree=request.include_working_tree,
            all_commits=request.all_commits,
            rev=request.rev,
            num=request.num,
            no_pager=request.no_pager,
            drop=request.drop,
            keep=request.keep,
            param_deps=request.param_deps,
            sort_by=request.sort_by,
            sort_order=request.sort_order,
            sha=request.sha,
            output_format=request.output_format,
            precision=request.precision,
            only_changed=request.only_changed,
            force=request.force,
        )
        return {"message": "Experiments shown successfully", "output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/{project_id}/exp/list")
async def list_experiments(user_id: str, project_id:str, request: ListExperimentsRequest):
    try:
        result = await dvc_exp_list(user_id, project_id, git_remote=request.git_remote)
        return {"message": "Experiments listed successfully", "output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/{project_id}/exp/apply")
async def apply_experiment(user_id: str, project_id:str, request: ApplyExperimentRequest):
    try:
        result = await dvc_exp_apply(user_id, project_id, experiment_id=request.experiment_id)
        return {"message": "Experiment applied successfully", "output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}/{project_id}/exp/remove")
async def remove_experiments(user_id: str, project_id:str, request: RemoveExperimentsRequest):
    """
    Remove experiments from the workspace.
    """
    try:
        result = await dvc_exp_remove(
            user_id, project_id,
            experiment_ids=request.experiment_ids,
            queue=request.queue,
        )
        return {"message": "Experiments removed successfully", "output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/{user_id}/{project_id}/exp/pull")
async def pull_experiment(user_id: str, project_id:str, request: PullExperimentRequest):
    """
    Pull an experiment from a Git remote.
    """
    try:
        result = await dvc_exp_pull(
            user_id, project_id,
            git_remote=request.git_remote,
            experiment_id=request.experiment_id,
        )
        return {"message": "Experiment pulled successfully", "output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/{user_id}/{project_id}/exp/push")
async def push_experiment(user_id: str, project_id:str, request: PushExperimentRequest):
    """
    Push a local experiment to a Git remote.
    """
    try:
        result = await dvc_exp_push(
            user_id, project_id,
            git_remote=request.git_remote,
            experiment_id=request.experiment_id,
        )
        return {"message": "Experiment pushed successfully", "output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/{project_id}/exp/save")
async def save_experiment(user_id: str, project_id:str, request: SaveExperimentRequest):
    """
    Save the current workspace as an experiment.
    """
    try:
        result = await dvc_exp_save(
            user_id, project_id, name=request.name, force=request.force
        )
        return {"message": "Experiment saved successfully", "output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
