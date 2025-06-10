from fastapi import APIRouter, HTTPException
from app.classes import *
from bson.objectid import ObjectId
from typing import List, Optional
from app.init_db import get_users_collection, get_projects_collection
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
    dvc_metrics_show,
    dvc_metrics_diff,
    dvc_plots_show,
    dvc_plots_diff,
    add_stages,
    add_stage,
    repro
)
from app.dvc_exp import *
import traceback
from datetime import datetime

import os

router = APIRouter()

@router.get("/users/", response_model=List[User])
async def get_users():
    """
    Get all users
    """
    try:
        users_collection = await get_users_collection()
        users = await users_collection.find().to_list(None)
        return [User.from_mongo(user) for user in users]
    except Exception as e:
        print("Error in get_users:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """
    Get a specific user by ID
    """
    try:
        users_collection = await get_users_collection()
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return User.from_mongo(user)
    except Exception as e:
        print("Error in get_user:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    """
    Create a new user
    """
    try:
        users_collection = await get_users_collection()
        user_dict = user.dict()
        result = await users_collection.insert_one(user_dict)
        created_user = await users_collection.find_one({"_id": result.inserted_id})
        return User.from_mongo(created_user)
    except Exception as e:
        print("Error in create_user:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user: User):
    """
    Update a user
    """
    try:
        users_collection = await get_users_collection()
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": user.dict(exclude={"id"})}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
        return User(**updated_user)
    except Exception as e:
        print("Error in update_user:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """
    Delete a user
    """
    try:
        users_collection = await get_users_collection()
        result = await users_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except Exception as e:
        print("Error in delete_user:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/project/create")
async def create_new_project(user_id: str, request: ProjectRequest):
    """
    Creates a new project directory and initializes Git/DVC.
    """
    try:
        # Check if project name is unique for the user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "project_name": request.project_name,
            "user_id": user_id
        })
        if project:
            raise HTTPException(status_code=400, detail="Project name already exists for this user")
        
        # Prepare project data
        project_data = {
            "user_id": user_id,
            "username": request.username,
            "project_name": request.project_name,
            "description": request.description,
            "project_type": request.project_type,
            "framework": request.framework,
            "python_version": request.python_version,
            "dependencies": request.dependencies,
            "models_count": 0,
            "experiments_count": 0,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        # Save the project details to the database
        result = await project_collection.insert_one(project_data)
        project_id = str(result.inserted_id)

        # Add the project to the user's projects array
        users_collection = await get_users_collection()
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"projects": project_id}}
        )
        
        # Create the project directory and initialize DVC
        try:
            project_path = await dvc_create_project(user_id, project_id)
            print(f"Created project directory at: {project_path}")
        except Exception as e:
            print(f"Error creating project directory: {e}")
            # Rollback database changes
            await project_collection.delete_one({"_id": result.inserted_id})
            await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$pull": {"projects": project_id}}
            )
            raise HTTPException(status_code=500, detail=f"Failed to create project directory: {str(e)}")
            
        return {
            "message": f"Project {request.project_name} created successfully",
            "id": project_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print("Error in create_new_project:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

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

@router.get("/{user_id}/{project_id}/clone_project")
async def clone_project(user_id: str, project_id: str, request: CloneRequest):
    """
    Clones a project from a remote repository.
    """
    try:
        # Assuming `clone_project` is the handler function for cloning projects
        result = await clone_project(user_id, project_id, request.remote_url)
        return {"message": result}
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
    
@router.get("/{user_id}/{project_id}/run_pipeline")
async def run_project_pipeline(user_id: str, project_id: str):
    """
    Runs the DVC pipeline for the project.
    """
    try:
        # Assuming `run_pipeline` is the handler function for running DVC pipelines
        result = await repro(user_id, project_id)
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/{project_id}/metrics_show")
async def show_metrics(user_id: str, project_id: str, request: MetricsShowRequest):
    """
    Show metrics for a project.
    """
    try:
        result = await dvc_metrics_show(user_id, project_id, request.all_commits, request.output_json, request.yaml)
        return result
    except Exception as e:
        print("Error in show_metrics:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/{project_id}/metrics_diff")
async def metrics_diff(user_id: str, project_id: str, request: MetricsDiffRequest):
    """
    Show metrics diff for a project.
    """
    try:
        result = await dvc_metrics_diff(
            user_id, project_id,
            request.a_rev, request.b_rev,
            request.all, request.precision,
            request.output_json, request.csv, request.md
        )
        return result
    except Exception as e:
        print("Error in metrics_diff:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{user_id}/{project_id}/plots_show")
async def show_plots(user_id: str, project_id: str, request: PlotsShowRequest):
    """
    Show plots for a project.
    """
    try:
        result = await dvc_plots_show(
            user_id, project_id,
            request.targets, request.output_json,
            request.html, request.no_html,
            request.templates_dir, request.out
        )
        return result
    except Exception as e:
        print("Error in show_plots:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/{project_id}/plots_diff")
async def plots_diff(user_id: str, project_id: str, request: PlotsDiffRequest):
    """
    Show plots diff for a project.
    """
    try:
        result = await dvc_plots_diff(
            user_id, project_id,
            request.targets, request.a_rev,
            request.b_rev, request.templates_dir,
            request.output_json, request.html,
            request.no_html, request.out
        )
        return result
    except Exception as e:
        print("Error in plots_diff:", str(e))
        print("Traceback:", traceback.format_exc())
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

@router.get("/{user_id}/project/{project_id}")
async def get_project(user_id: str, project_id: str):
    """
    Get a single project by ID.
    """
    try:
        # Convert string ID to ObjectId
        try:
            project_id_obj = ObjectId(project_id)
        except Exception as e:
            print(f"Invalid project ID format: {project_id}")
            raise HTTPException(status_code=400, detail=f"Invalid project ID format: {project_id}")
        
        # Find the project with matching user_id
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": project_id_obj,
            "user_id": user_id
        })
        
        if not project:
            print(f"Project not found: {project_id} for user {user_id}")
            raise HTTPException(status_code=404, detail="Project not found")
            
        return project
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_project:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")

@router.get("/{user_id}/projects")
async def get_user_projects(user_id: str):
    """
    Get all projects for a user.
    """
    try:
        # Convert string ID to ObjectId
        try:
            user_id_obj = ObjectId(user_id)
        except Exception as e:
            print(f"Invalid user ID format: {user_id}")
            raise HTTPException(status_code=400, detail=f"Invalid user ID format: {user_id}")
        
        # Find the user
        users_collection = await get_users_collection()
        user = await users_collection.find_one({"_id": user_id_obj})
        if not user:
            print(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
            
        # Get all projects for the user
        project_collection = await get_projects_collection()
        projects = await project_collection.find({
            "user_id": user_id
        }).to_list(None)
        
        return projects
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_user_projects:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get user projects: {str(e)}")
