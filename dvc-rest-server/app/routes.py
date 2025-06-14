from fastapi import APIRouter, HTTPException
from app.classes import *
from bson.objectid import ObjectId
from typing import List, Optional
from app.init_db import get_users_collection, get_projects_collection, get_pipeline_configs_collection, get_data_sources_collection, get_remote_storages_collection, get_code_files_collection
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
    repro,
    get_dvc_status,
    create_pipeline_template,
    get_pipeline_stages,
    update_pipeline_stage,
    remove_pipeline_stage,
    validate_pipeline,
    add_data_source,
    remove_data_source,
    update_data_source,
    add_remote_storage,
    remove_remote_storage,
    list_remote_storages,
    push_to_remote,
    pull_from_remote,
    sync_with_remote,
    add_code_file,
    update_code_file,
    remove_code_file,
    get_code_file_content,
    list_code_files,
    bulk_upload_code_files,
    get_code_file_info,
    create_parameter_set,
    update_parameter_set,
    get_parameter_set,
    delete_parameter_set,
    import_parameters_from_file,
    import_parameters_from_upload,
    export_parameters_to_file,
    validate_parameters
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
        await create_user_directory(user_id)
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

@router.get("/{user_id}/{project_id}/dvc/status")
async def get_dvc_status_endpoint(user_id: str, project_id: str):
    """
    Get DVC status showing tracked, untracked, and modified files.
    """
    try:
        result = await get_dvc_status(user_id, project_id)
        return result
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
        
        # Convert ObjectId to string for JSON serialization
        project_dict = dict(project)
        project_dict["_id"] = str(project_dict["_id"])
        return project_dict
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
        # Find the user
        users_collection = await get_users_collection()
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Get all projects for the user
        project_collection = await get_projects_collection()
        projects = await project_collection.find({
            "user_id": user_id
        }).to_list(None)
        
        # Convert ObjectId to string for JSON serialization
        serialized_projects = []
        for project in projects:
            project_dict = dict(project)
            project_dict["_id"] = str(project_dict["_id"])
            serialized_projects.append(project_dict)
            
        return {"projects": serialized_projects}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid user ID format: {str(e)}")
    except Exception as e:
        print("Error in get_user_projects:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get user projects: {str(e)}")

# Pipeline Configuration Endpoints

@router.post("/{user_id}/{project_id}/pipeline/config")
async def create_pipeline_config(user_id: str, project_id: str, request: PipelineConfigCreate):
    """
    Create a new pipeline configuration for a project with DVC stages.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Prepare pipeline config data
        pipeline_config_data = {
            "user_id": user_id,
            "project_id": project_id,
            "name": request.name,
            "description": request.description,
            "stages": [stage.dict() for stage in request.stages],
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_active": True
        }

        # Convert Pydantic stages to dict format for the handler
        stages_dict = []
        for stage in request.stages:
            stage_dict = {
                "name": stage.name,
                "deps": stage.deps,
                "outs": stage.outs,
                "params": stage.params,
                "metrics": stage.metrics,
                "plots": stage.plots,
                "command": stage.command
            }
            stages_dict.append(stage_dict)
        
        # Step 1: Create the pipeline template using DVC handler
        print(f"Creating pipeline template: {request.name}")
        template_result = await create_pipeline_template(user_id, project_id, request.name, stages_dict)
        print(f"Template created: {template_result}")
        
        # Step 2: Create individual DVC stages
        print("Creating DVC stages...")
        created_stages = []
        failed_stages = []
        
        for stage in request.stages:
            try:
                print(f"Creating stage: {stage.name}")
                stage_result = await add_stage(
                    user_id=user_id,
                    project_id=project_id,
                    name=stage.name,
                    deps=stage.deps,
                    outs=stage.outs,
                    params=stage.params,
                    metrics=stage.metrics,
                    plots=stage.plots,
                    command=stage.command
                )
                created_stages.append({
                    "name": stage.name,
                    "result": stage_result
                })
                print(f"Stage {stage.name} created successfully")
            except Exception as e:
                error_msg = f"Failed to create stage {stage.name}: {str(e)}"
                print(error_msg)
                failed_stages.append({
                    "name": stage.name,
                    "error": str(e)
                })
        
        # Step 3: Validate the pipeline
        print("Validating pipeline...")
        validation_result = await validate_pipeline(user_id, project_id)
        print(f"Validation result: {validation_result}")
        
        # Step 4: Save to database
        pipeline_configs_collection = await get_pipeline_configs_collection()
        db_result = await pipeline_configs_collection.insert_one(pipeline_config_data)
        
        # Prepare response
        response = {
            "message": f"Pipeline configuration '{request.name}' created successfully",
            "id": str(db_result.inserted_id),
            "template_result": template_result,
            "stages_created": len(created_stages),
            "stages_failed": len(failed_stages),
            "created_stages": created_stages,
            "failed_stages": failed_stages,
            "validation": validation_result
        }
        
        # Add warning if some stages failed
        if failed_stages:
            response["warning"] = f"Pipeline created but {len(failed_stages)} stages failed"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in create_pipeline_config:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create pipeline configuration: {str(e)}")

@router.get("/{user_id}/{project_id}/pipeline/configs")
async def get_pipeline_configs(user_id: str, project_id: str):
    """
    Get all pipeline configurations for a project.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get pipeline configurations
        pipeline_configs_collection = await get_pipeline_configs_collection()
        configs = await pipeline_configs_collection.find({
            "user_id": user_id,
            "project_id": project_id
        }).to_list(None)
        
        # Convert ObjectId to string for JSON serialization
        serialized_configs = []
        for config in configs:
            config_dict = dict(config)
            config_dict["_id"] = str(config_dict["_id"])
            serialized_configs.append(config_dict)
            
        return {"pipeline_configs": serialized_configs}
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_pipeline_configs:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline configurations: {str(e)}")

@router.get("/{user_id}/{project_id}/pipeline/config/{config_id}")
async def get_pipeline_config(user_id: str, project_id: str, config_id: str):
    """
    Get a specific pipeline configuration by ID.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get pipeline configuration
        pipeline_configs_collection = await get_pipeline_configs_collection()
        config = await pipeline_configs_collection.find_one({
            "_id": ObjectId(config_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not config:
            raise HTTPException(status_code=404, detail="Pipeline configuration not found")
        
        # Convert ObjectId to string for JSON serialization
        config_dict = dict(config)
        config_dict["_id"] = str(config_dict["_id"])
        
        return config_dict
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_pipeline_config:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline configuration: {str(e)}")

@router.put("/{user_id}/{project_id}/pipeline/config/{config_id}")
async def update_pipeline_config(user_id: str, project_id: str, config_id: str, request: PipelineConfigUpdate):
    """
    Update a pipeline configuration and sync with DVC stages.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get existing pipeline configuration
        pipeline_configs_collection = await get_pipeline_configs_collection()
        existing_config = await pipeline_configs_collection.find_one({
            "_id": ObjectId(config_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not existing_config:
            raise HTTPException(status_code=404, detail="Pipeline configuration not found")
        
        # Prepare update data
        update_data = {"updated_at": datetime.now().isoformat()}
        stages_updated = False
        
        if request.name is not None:
            update_data["name"] = request.name
        if request.description is not None:
            update_data["description"] = request.description
        if request.is_active is not None:
            update_data["is_active"] = request.is_active
        
        # Handle stage updates
        if request.stages is not None:
            update_data["stages"] = [stage.dict() for stage in request.stages]
            stages_updated = True
            
            # Update DVC stages if stages were modified
            print("Updating DVC stages...")
            updated_stages = []
            failed_stages = []
            
            # First, remove existing stages
            existing_stages = existing_config.get("stages", [])
            for stage in existing_stages:
                try:
                    stage_name = stage.get("name", "unnamed_stage")
                    print(f"Removing existing stage: {stage_name}")
                    await remove_pipeline_stage(user_id, project_id, stage_name)
                except Exception as e:
                    print(f"Warning: Failed to remove stage {stage_name}: {str(e)}")
            
            # Then, create new stages
            for stage in request.stages:
                try:
                    print(f"Creating updated stage: {stage.name}")
                    stage_result = await add_stage(
                        user_id=user_id,
                        project_id=project_id,
                        name=stage.name,
                        deps=stage.deps,
                        outs=stage.outs,
                        params=stage.params,
                        metrics=stage.metrics,
                        plots=stage.plots,
                        command=stage.command
                    )
                    updated_stages.append({
                        "name": stage.name,
                        "result": stage_result
                    })
                    print(f"Stage {stage.name} updated successfully")
                except Exception as e:
                    error_msg = f"Failed to update stage {stage.name}: {str(e)}"
                    print(error_msg)
                    failed_stages.append({
                        "name": stage.name,
                        "error": str(e)
                    })
        
        # Update pipeline configuration in database
        result = await pipeline_configs_collection.update_one(
            {
                "_id": ObjectId(config_id),
                "user_id": user_id,
                "project_id": project_id
            },
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Pipeline configuration not found")
        
        # Validate the updated pipeline
        print("Validating updated pipeline...")
        validation_result = await validate_pipeline(user_id, project_id)
        
        # Prepare response
        response = {
            "message": "Pipeline configuration updated successfully",
            "config_id": config_id,
            "stages_updated": stages_updated,
            "validation": validation_result
        }
        
        if stages_updated:
            response["updated_stages"] = updated_stages
            response["failed_stages"] = failed_stages
            response["stages_updated_count"] = len(updated_stages)
            response["stages_failed_count"] = len(failed_stages)
            
            if failed_stages:
                response["warning"] = f"Pipeline updated but {len(failed_stages)} stages failed"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in update_pipeline_config:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to update pipeline configuration: {str(e)}")

@router.delete("/{user_id}/{project_id}/pipeline/config/{config_id}")
async def delete_pipeline_config(user_id: str, project_id: str, config_id: str):
    """
    Delete a pipeline configuration and clean up DVC stages.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get pipeline configuration before deletion
        pipeline_configs_collection = await get_pipeline_configs_collection()
        config = await pipeline_configs_collection.find_one({
            "_id": ObjectId(config_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not config:
            raise HTTPException(status_code=404, detail="Pipeline configuration not found")
        
        # Clean up DVC stages
        print("Cleaning up DVC stages...")
        removed_stages = []
        failed_removals = []
        
        stages = config.get("stages", [])
        for stage in stages:
            try:
                stage_name = stage.get("name", "unnamed_stage")
                print(f"Removing DVC stage: {stage_name}")
                await remove_pipeline_stage(user_id, project_id, stage_name)
                removed_stages.append(stage_name)
                print(f"Stage {stage_name} removed successfully")
            except Exception as e:
                error_msg = f"Failed to remove stage {stage_name}: {str(e)}"
                print(error_msg)
                failed_removals.append({
                    "name": stage_name,
                    "error": str(e)
                })
        
        # Delete pipeline configuration from database
        result = await pipeline_configs_collection.delete_one({
            "_id": ObjectId(config_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Pipeline configuration not found")
        
        # Prepare response
        response = {
            "message": f"Pipeline configuration '{config['name']}' deleted successfully",
            "config_id": config_id,
            "config_name": config["name"],
            "stages_removed": len(removed_stages),
            "stages_failed_removal": len(failed_removals),
            "removed_stages": removed_stages,
            "failed_removals": failed_removals
        }
        
        if failed_removals:
            response["warning"] = f"Pipeline deleted but {len(failed_removals)} stages failed to remove"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in delete_pipeline_config:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to delete pipeline configuration: {str(e)}")

@router.post("/{user_id}/{project_id}/pipeline/execute")
async def execute_pipeline(user_id: str, project_id: str, request: PipelineExecutionRequest):
    """
    Execute a pipeline configuration.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # If config_id is provided, verify it exists
        if request.pipeline_config_id:
            pipeline_configs_collection = await get_pipeline_configs_collection()
            config = await pipeline_configs_collection.find_one({
                "_id": ObjectId(request.pipeline_config_id),
                "user_id": user_id,
                "project_id": project_id
            })
            if not config:
                raise HTTPException(status_code=404, detail="Pipeline configuration not found")
        
        # Execute the pipeline using existing DVC functionality
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now().isoformat()
        
        try:
            # Use the existing repro function to execute the pipeline
            result = await repro(
                user_id, 
                project_id, 
                force=request.force,
                dry=request.dry_run,
                targets=request.targets
            )
            
            end_time = datetime.now().isoformat()
            
            return {
                "execution_id": execution_id,
                "status": "completed",
                "start_time": start_time,
                "end_time": end_time,
                "output": result,
                "error": None
            }
        except Exception as e:
            end_time = datetime.now().isoformat()
            return {
                "execution_id": execution_id,
                "status": "failed",
                "start_time": start_time,
                "end_time": end_time,
                "output": None,
                "error": str(e)
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print("Error in execute_pipeline:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to execute pipeline: {str(e)}")

@router.post("/{user_id}/{project_id}/pipeline/recover")
async def recover_pipeline(user_id: str, project_id: str, config_id: str):
    """
    Recover a pipeline by applying a saved configuration.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get pipeline configuration
        pipeline_configs_collection = await get_pipeline_configs_collection()
        config = await pipeline_configs_collection.find_one({
            "_id": ObjectId(config_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not config:
            raise HTTPException(status_code=404, detail="Pipeline configuration not found")
        
        # Apply the pipeline configuration by creating DVC stages
        try:
            # Import the add_stage function
            from app.dvc_handler import add_stage
            
            # Apply each stage from the configuration
            for stage_data in config["stages"]:
                await add_stage(
                    user_id, 
                    project_id,
                    name=stage_data["name"],
                    deps=stage_data.get("deps", []),
                    outs=stage_data.get("outs", []),
                    params=stage_data.get("params"),
                    metrics=stage_data.get("metrics"),
                    plots=stage_data.get("plots"),
                    command=stage_data["command"]
                )
            
            return {
                "message": f"Pipeline '{config['name']}' recovered successfully",
                "config_name": config["name"],
                "stages_applied": len(config["stages"])
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to apply pipeline configuration: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        print("Error in recover_pipeline:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to recover pipeline: {str(e)}")

# Additional Pipeline Management Endpoints

@router.post("/{user_id}/{project_id}/pipeline/template")
async def create_pipeline_template_endpoint(user_id: str, project_id: str, request: PipelineTemplateRequest):
    """
    Create a pipeline template with predefined stages.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Convert Pydantic stages to dict format for the handler
        stages_dict = []
        for stage in request.stages:
            stage_dict = {
                "name": stage.name,
                "deps": stage.deps,
                "outs": stage.outs,
                "params": stage.params,
                "metrics": stage.metrics,
                "plots": stage.plots,
                "command": stage.command
            }
            stages_dict.append(stage_dict)
        
        result = await create_pipeline_template(user_id, project_id, request.template_name, stages_dict)
        return {"message": result}
    except HTTPException:
        raise
    except Exception as e:
        print("Error in create_pipeline_template_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create pipeline template: {str(e)}")

@router.get("/{user_id}/{project_id}/pipeline/stages")
async def get_pipeline_stages_endpoint(user_id: str, project_id: str):
    """
    Get the current pipeline stages from dvc.yaml.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        result = await get_pipeline_stages(user_id, project_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_pipeline_stages_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline stages: {str(e)}")

@router.put("/{user_id}/{project_id}/pipeline/stage/{stage_name}")
async def update_pipeline_stage_endpoint(user_id: str, project_id: str, stage_name: str, request: StageUpdateRequest):
    """
    Update an existing pipeline stage.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        result = await update_pipeline_stage(user_id, project_id, stage_name, request.updates)
        return {"message": result}
    except HTTPException:
        raise
    except Exception as e:
        print("Error in update_pipeline_stage_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to update pipeline stage: {str(e)}")

@router.delete("/{user_id}/{project_id}/pipeline/stage/{stage_name}")
async def remove_pipeline_stage_endpoint(user_id: str, project_id: str, stage_name: str):
    """
    Remove a pipeline stage from dvc.yaml.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        result = await remove_pipeline_stage(user_id, project_id, stage_name)
        return {"message": result}
    except HTTPException:
        raise
    except Exception as e:
        print("Error in remove_pipeline_stage_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to remove pipeline stage: {str(e)}")

@router.get("/{user_id}/{project_id}/pipeline/validate")
async def validate_pipeline_endpoint(user_id: str, project_id: str):
    """
    Validate the current pipeline configuration.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        result = await validate_pipeline(user_id, project_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print("Error in validate_pipeline_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to validate pipeline: {str(e)}")

@router.post("/{user_id}/{project_id}/pipeline/run")
async def run_pipeline_endpoint(user_id: str, project_id: str, request: PipelineRunRequest):
    """
    Run the pipeline with optional parameters.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        result = await repro(
            user_id, 
            project_id, 
            target=request.target,
            pipeline=request.pipeline,
            force=request.force,
            dry_run=request.dry_run,
            no_commit=request.no_commit
        )
        
        return {
            "message": "Pipeline executed successfully",
            "output": result,
            "parameters": {
                "target": request.target,
                "pipeline": request.pipeline,
                "force": request.force,
                "dry_run": request.dry_run,
                "no_commit": request.no_commit
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print("Error in run_pipeline_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to run pipeline: {str(e)}")

# Data Sources endpoints
@router.get("/{user_id}/{project_id}/data/sources")
async def get_data_sources(user_id: str, project_id: str):
    """
    Get all data sources for a project.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get data sources from database
        data_sources_collection = await get_data_sources_collection()
        data_sources = await data_sources_collection.find({
            "user_id": user_id,
            "project_id": project_id
        }).to_list(None)
        
        # Convert ObjectId to string for JSON serialization
        serialized_sources = []
        for source in data_sources:
            source_dict = dict(source)
            source_dict["_id"] = str(source_dict["_id"])
            serialized_sources.append(source_dict)
        
        return {"data_sources": serialized_sources}
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_data_sources:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get data sources: {str(e)}")

@router.get("/{user_id}/{project_id}/data/source/{source_id}")
async def get_data_source(user_id: str, project_id: str, source_id: str):
    """
    Get a specific data source by ID.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get data source from database
        data_sources_collection = await get_data_sources_collection()
        data_source = await data_sources_collection.find_one({
            "_id": ObjectId(source_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not data_source:
            raise HTTPException(status_code=404, detail="Data source not found")
        
        # Convert ObjectId to string for JSON serialization
        source_dict = dict(data_source)
        source_dict["_id"] = str(source_dict["_id"])
        
        return source_dict
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_data_source:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get data source: {str(e)}")

@router.post("/{user_id}/{project_id}/data/source")
async def create_data_source(user_id: str, project_id: str, request: CreateDataSourceRequest):
    """
    Create a new data source.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Prepare data source data
        data_source_data = {
            "user_id": user_id,
            "project_id": project_id,
            "name": request.name,
            "description": request.description,
            "type": request.type,
            "source": request.source,
            "destination": request.destination,
            "size": None,  # Will be updated after download
            "format": None,  # Will be detected from file
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "pending",
            "error": None
        }
        
        # Save to database first
        data_sources_collection = await get_data_sources_collection()
        result = await data_sources_collection.insert_one(data_source_data)
        source_id = str(result.inserted_id)
        
        try:
            # Add data source using DVC
            result = await add_data_source(
                user_id=user_id,
                project_id=project_id,
                name=request.name,
                source_type=request.type.value,
                source_path=request.source,
                destination=request.destination,
                description=request.description
            )
            
            # Update status to completed
            await data_sources_collection.update_one(
                {"_id": ObjectId(source_id)},
                {"$set": {"status": "completed", "updated_at": datetime.now().isoformat()}}
            )
            
            return {
                "message": "Data source created successfully",
                "id": source_id,
                "dvc_result": result
            }
            
        except Exception as e:
            # Update status to failed
            await data_sources_collection.update_one(
                {"_id": ObjectId(source_id)},
                {"$set": {"status": "failed", "error": str(e), "updated_at": datetime.now().isoformat()}}
            )
            raise e
            
    except HTTPException:
        raise
    except Exception as e:
        print("Error in create_data_source:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create data source: {str(e)}")

@router.put("/{user_id}/{project_id}/data/source/{source_id}")
async def update_data_source_endpoint(user_id: str, project_id: str, source_id: str, request: UpdateDataSourceRequest):
    """
    Update a data source.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get existing data source
        data_sources_collection = await get_data_sources_collection()
        data_source = await data_sources_collection.find_one({
            "_id": ObjectId(source_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not data_source:
            raise HTTPException(status_code=404, detail="Data source not found")
        
        # Prepare update data
        update_data = {"updated_at": datetime.now().isoformat()}
        if request.name is not None:
            update_data["name"] = request.name
        if request.description is not None:
            update_data["description"] = request.description
        if request.status is not None:
            update_data["status"] = request.status
        
        # Update in database
        await data_sources_collection.update_one(
            {"_id": ObjectId(source_id)},
            {"$set": update_data}
        )
        
        return {"message": "Data source updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in update_data_source_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to update data source: {str(e)}")

@router.delete("/{user_id}/{project_id}/data/source/{source_id}")
async def delete_data_source_endpoint(user_id: str, project_id: str, source_id: str):
    """
    Delete a data source.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get existing data source
        data_sources_collection = await get_data_sources_collection()
        data_source = await data_sources_collection.find_one({
            "_id": ObjectId(source_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not data_source:
            raise HTTPException(status_code=404, detail="Data source not found")
        
        try:
            # Remove data source using DVC
            result = await remove_data_source(
                user_id=user_id,
                project_id=project_id,
                destination=data_source["destination"]
            )
            
            # Remove from database
            await data_sources_collection.delete_one({"_id": ObjectId(source_id)})
            
            return {"message": "Data source deleted successfully", "dvc_result": result}
            
        except Exception as e:
            raise e
            
    except HTTPException:
        raise
    except Exception as e:
        print("Error in delete_data_source_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to delete data source: {str(e)}")

# Remote Storage endpoints
@router.get("/{user_id}/{project_id}/data/remotes")
async def get_remote_storages(user_id: str, project_id: str):
    """
    Get all remote storages for a project.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get remote storages from database
        remote_storages_collection = await get_remote_storages_collection()
        remote_storages = await remote_storages_collection.find({
            "user_id": user_id,
            "project_id": project_id
        }).to_list(None)
        
        # Convert ObjectId to string for JSON serialization
        serialized_remotes = []
        for remote in remote_storages:
            remote_dict = dict(remote)
            remote_dict["_id"] = str(remote_dict["_id"])
            serialized_remotes.append(remote_dict)
        
        return {"remote_storages": serialized_remotes}
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_remote_storages:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get remote storages: {str(e)}")

@router.get("/{user_id}/{project_id}/data/remote/{remote_id}")
async def get_remote_storage(user_id: str, project_id: str, remote_id: str):
    """
    Get a specific remote storage by ID.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get remote storage from database
        remote_storages_collection = await get_remote_storages_collection()
        remote_storage = await remote_storages_collection.find_one({
            "_id": ObjectId(remote_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not remote_storage:
            raise HTTPException(status_code=404, detail="Remote storage not found")
        
        # Convert ObjectId to string for JSON serialization
        remote_dict = dict(remote_storage)
        remote_dict["_id"] = str(remote_dict["_id"])
        
        return remote_dict
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_remote_storage:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get remote storage: {str(e)}")

@router.post("/{user_id}/{project_id}/data/remote")
async def create_remote_storage(user_id: str, project_id: str, request: CreateRemoteRequest):
    """
    Create a new remote storage.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Prepare remote storage data
        remote_storage_data = {
            "user_id": user_id,
            "project_id": project_id,
            "name": request.name,
            "url": request.url,
            "type": request.type,
            "is_default": request.is_default,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save to database first
        remote_storages_collection = await get_remote_storages_collection()
        result = await remote_storages_collection.insert_one(remote_storage_data)
        remote_id = str(result.inserted_id)
        
        try:
            # Add remote storage using DVC
            remote_type = "default" if request.is_default else "cache"
            result = await add_remote_storage(
                user_id=user_id,
                project_id=project_id,
                name=request.name,
                url=request.url,
                remote_type=remote_type
            )
            
            return {
                "message": "Remote storage created successfully",
                "id": remote_id,
                "dvc_result": result
            }
            
        except Exception as e:
            # Remove from database if DVC operation failed
            await remote_storages_collection.delete_one({"_id": ObjectId(remote_id)})
            raise e
            
    except HTTPException:
        raise
    except Exception as e:
        print("Error in create_remote_storage:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create remote storage: {str(e)}")

@router.put("/{user_id}/{project_id}/data/remote/{remote_id}")
async def update_remote_storage(user_id: str, project_id: str, remote_id: str, request: dict):
    """
    Update a remote storage.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get existing remote storage
        remote_storages_collection = await get_remote_storages_collection()
        remote_storage = await remote_storages_collection.find_one({
            "_id": ObjectId(remote_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not remote_storage:
            raise HTTPException(status_code=404, detail="Remote storage not found")
        
        # Prepare update data
        update_data = {"updated_at": datetime.now().isoformat()}
        if "name" in request:
            update_data["name"] = request["name"]
        if "url" in request:
            update_data["url"] = request["url"]
        if "is_default" in request:
            update_data["is_default"] = request["is_default"]
        
        # Update in database
        await remote_storages_collection.update_one(
            {"_id": ObjectId(remote_id)},
            {"$set": update_data}
        )
        
        return {"message": "Remote storage updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in update_remote_storage:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to update remote storage: {str(e)}")

@router.delete("/{user_id}/{project_id}/data/remote/{remote_id}")
async def delete_remote_storage(user_id: str, project_id: str, remote_id: str):
    """
    Delete a remote storage.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get existing remote storage
        remote_storages_collection = await get_remote_storages_collection()
        remote_storage = await remote_storages_collection.find_one({
            "_id": ObjectId(remote_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not remote_storage:
            raise HTTPException(status_code=404, detail="Remote storage not found")
        
        try:
            # Remove remote storage using DVC
            result = await remove_remote_storage(
                user_id=user_id,
                project_id=project_id,
                name=remote_storage["name"]
            )
            
            # Remove from database
            await remote_storages_collection.delete_one({"_id": ObjectId(remote_id)})
            
            return {"message": "Remote storage deleted successfully", "dvc_result": result}
            
        except Exception as e:
            raise e
            
    except HTTPException:
        raise
    except Exception as e:
        print("Error in delete_remote_storage:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to delete remote storage: {str(e)}")

# Additional Remote Storage Operations

@router.post("/{user_id}/{project_id}/data/remote/{remote_id}/push")
async def push_to_remote_endpoint(user_id: str, project_id: str, remote_id: str, request: dict = None):
    """
    Push data to a specific remote storage.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get remote storage
        remote_storages_collection = await get_remote_storages_collection()
        remote_storage = await remote_storages_collection.find_one({
            "_id": ObjectId(remote_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not remote_storage:
            raise HTTPException(status_code=404, detail="Remote storage not found")
        
        # Get push parameters
        target = request.get("target") if request else None
        
        # Push to remote
        result = await push_to_remote(
            user_id=user_id,
            project_id=project_id,
            remote_name=remote_storage["name"],
            target=target
        )
        
        return {"message": "Data pushed successfully", "result": result}
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in push_to_remote_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to push to remote: {str(e)}")

@router.post("/{user_id}/{project_id}/data/remote/{remote_id}/pull")
async def pull_from_remote_endpoint(user_id: str, project_id: str, remote_id: str, request: dict = None):
    """
    Pull data from a specific remote storage.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get remote storage
        remote_storages_collection = await get_remote_storages_collection()
        remote_storage = await remote_storages_collection.find_one({
            "_id": ObjectId(remote_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not remote_storage:
            raise HTTPException(status_code=404, detail="Remote storage not found")
        
        # Get pull parameters
        target = request.get("target") if request else None
        
        # Pull from remote
        result = await pull_from_remote(
            user_id=user_id,
            project_id=project_id,
            remote_name=remote_storage["name"],
            target=target
        )
        
        return {"message": "Data pulled successfully", "result": result}
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in pull_from_remote_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to pull from remote: {str(e)}")

@router.post("/{user_id}/{project_id}/data/remote/{remote_id}/sync")
async def sync_with_remote_endpoint(user_id: str, project_id: str, remote_id: str):
    """
    Sync data with a specific remote storage.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get remote storage
        remote_storages_collection = await get_remote_storages_collection()
        remote_storage = await remote_storages_collection.find_one({
            "_id": ObjectId(remote_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not remote_storage:
            raise HTTPException(status_code=404, detail="Remote storage not found")
        
        # Sync with remote
        result = await sync_with_remote(
            user_id=user_id,
            project_id=project_id,
            remote_name=remote_storage["name"]
        )
        
        return {"message": "Data synced successfully", "result": result}
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in sync_with_remote_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to sync with remote: {str(e)}")

@router.get("/{user_id}/{project_id}/data/remote/list")
async def list_remote_storages_endpoint(user_id: str, project_id: str):
    """
    List all remote storages configured in DVC.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # List remote storages from DVC
        result = await list_remote_storages(user_id, project_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in list_remote_storages_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to list remote storages: {str(e)}")

# Code Upload and Management Endpoints

@router.get("/{user_id}/{project_id}/code/files")
async def get_code_files(user_id: str, project_id: str, file_type: Optional[str] = None, path_pattern: Optional[str] = None):
    """
    Get all code files for a project with optional filtering.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get code files from database
        code_files_collection = await get_code_files_collection()
        query = {
            "user_id": user_id,
            "project_id": project_id
        }
        
        if file_type:
            query["file_type"] = file_type
        if path_pattern:
            query["file_path"] = {"$regex": path_pattern, "$options": "i"}
        
        code_files = await code_files_collection.find(query).to_list(None)
        
        # Convert ObjectId to string for JSON serialization
        serialized_files = []
        for file in code_files:
            file_dict = dict(file)
            file_dict["_id"] = str(file_dict["_id"])
            serialized_files.append(file_dict)
        
        return {
            "code_files": serialized_files,
            "total_count": len(serialized_files)
        }
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_code_files:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get code files: {str(e)}")

@router.get("/{user_id}/{project_id}/code/file/{file_id}")
async def get_code_file(user_id: str, project_id: str, file_id: str):
    """
    Get a specific code file by ID.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get code file from database
        code_files_collection = await get_code_files_collection()
        code_file = await code_files_collection.find_one({
            "_id": ObjectId(file_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not code_file:
            raise HTTPException(status_code=404, detail="Code file not found")
        
        # Convert ObjectId to string for JSON serialization
        file_dict = dict(code_file)
        file_dict["_id"] = str(file_dict["_id"])
        
        return file_dict
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_code_file:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get code file: {str(e)}")

@router.get("/{user_id}/{project_id}/code/file/{file_id}/content")
async def get_code_file_content_endpoint(user_id: str, project_id: str, file_id: str):
    """
    Get the content of a specific code file.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get code file from database
        code_files_collection = await get_code_files_collection()
        code_file = await code_files_collection.find_one({
            "_id": ObjectId(file_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not code_file:
            raise HTTPException(status_code=404, detail="Code file not found")
        
        # Get file content
        content = await get_code_file_content(
            user_id=user_id,
            project_id=project_id,
            file_path=code_file["file_path"]
        )
        
        return {
            "file_id": file_id,
            "file_path": code_file["file_path"],
            "filename": code_file["filename"],
            "content": content
        }
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_code_file_content_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get code file content: {str(e)}")

@router.post("/{user_id}/{project_id}/code/file")
async def create_code_file(user_id: str, project_id: str, request: CreateCodeFileRequest):
    """
    Create a new code file.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Prepare code file data
        code_file_data = {
            "user_id": user_id,
            "project_id": project_id,
            "filename": request.filename,
            "file_path": request.file_path,
            "file_type": request.file_type.value,
            "description": request.description,
            "size": len(request.content.encode('utf-8')),
            "content_hash": None,  # Will be updated after upload
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "pending",
            "error": None,
            "git_commit_hash": None
        }
        
        # Save to database first
        code_files_collection = await get_code_files_collection()
        result = await code_files_collection.insert_one(code_file_data)
        file_id = str(result.inserted_id)
        
        try:
            # Add code file using DVC
            dvc_result = await add_code_file(
                user_id=user_id,
                project_id=project_id,
                filename=request.filename,
                file_path=request.file_path,
                content=request.content,
                file_type=request.file_type.value,
                description=request.description
            )
            
            # Update database with results
            await code_files_collection.update_one(
                {"_id": ObjectId(file_id)},
                {
                    "$set": {
                        "status": "completed",
                        "size": dvc_result["size"],
                        "content_hash": dvc_result["content_hash"],
                        "git_commit_hash": dvc_result["git_commit_hash"],
                        "updated_at": datetime.now().isoformat()
                    }
                }
            )
            
            return {
                "message": "Code file created successfully",
                "file_id": file_id,
                "file_path": request.file_path,
                "git_commit_hash": dvc_result["git_commit_hash"]
            }
            
        except Exception as e:
            # Update status to failed
            await code_files_collection.update_one(
                {"_id": ObjectId(file_id)},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(e),
                        "updated_at": datetime.now().isoformat()
                    }
                }
            )
            raise e
            
    except HTTPException:
        raise
    except Exception as e:
        print("Error in create_code_file:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create code file: {str(e)}")

@router.put("/{user_id}/{project_id}/code/file/{file_id}")
async def update_code_file_endpoint(user_id: str, project_id: str, file_id: str, request: UpdateCodeFileRequest):
    """
    Update an existing code file.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get existing code file
        code_files_collection = await get_code_files_collection()
        code_file = await code_files_collection.find_one({
            "_id": ObjectId(file_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not code_file:
            raise HTTPException(status_code=404, detail="Code file not found")
        
        try:
            # Update code file using DVC handler
            dvc_result = await update_code_file(
                user_id=user_id,
                project_id=project_id,
                file_path=code_file["file_path"],
                content=request.content,
                description=request.description
            )
            
            # Prepare update data
            update_data = {
                "updated_at": datetime.now().isoformat(),
                "status": "completed",
                "size": dvc_result["size"],
                "content_hash": dvc_result["content_hash"],
                "git_commit_hash": dvc_result["git_commit_hash"]
            }
            
            if request.filename is not None:
                update_data["filename"] = request.filename
            if request.file_path is not None:
                update_data["file_path"] = request.file_path
            if request.description is not None:
                update_data["description"] = request.description
            
            # Update in database
            await code_files_collection.update_one(
                {"_id": ObjectId(file_id)},
                {"$set": update_data}
            )
            
            return {
                "message": "Code file updated successfully",
                "git_commit_hash": dvc_result["git_commit_hash"]
            }
            
        except Exception as e:
            # Update status to failed
            await code_files_collection.update_one(
                {"_id": ObjectId(file_id)},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(e),
                        "updated_at": datetime.now().isoformat()
                    }
                }
            )
            raise e
            
    except HTTPException:
        raise
    except Exception as e:
        print("Error in update_code_file_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to update code file: {str(e)}")

@router.delete("/{user_id}/{project_id}/code/file/{file_id}")
async def delete_code_file_endpoint(user_id: str, project_id: str, file_id: str):
    """
    Delete a code file.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get existing code file
        code_files_collection = await get_code_files_collection()
        code_file = await code_files_collection.find_one({
            "_id": ObjectId(file_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not code_file:
            raise HTTPException(status_code=404, detail="Code file not found")
        
        try:
            # Remove code file using DVC handler
            result = await remove_code_file(
                user_id=user_id,
                project_id=project_id,
                file_path=code_file["file_path"]
            )
            
            # Remove from database
            await code_files_collection.delete_one({"_id": ObjectId(file_id)})
            
            return {"message": "Code file deleted successfully", "dvc_result": result}
            
        except Exception as e:
            raise e
            
    except HTTPException:
        raise
    except Exception as e:
        print("Error in delete_code_file_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to delete code file: {str(e)}")

@router.post("/{user_id}/{project_id}/code/files/bulk")
async def bulk_upload_code_files_endpoint(user_id: str, project_id: str, request: BulkCodeUploadRequest):
    """
    Upload multiple code files at once.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Prepare files for bulk upload
        files_data = []
        for file_request in request.files:
            files_data.append({
                "filename": file_request.filename,
                "file_path": file_request.file_path,
                "content": file_request.content,
                "file_type": file_request.file_type.value,
                "description": file_request.description
            })
        
        # Perform bulk upload
        result = await bulk_upload_code_files(
            user_id=user_id,
            project_id=project_id,
            files=files_data
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in bulk_upload_code_files_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to perform bulk upload: {str(e)}")

@router.get("/{user_id}/{project_id}/code/files/scan")
async def scan_code_files_endpoint(user_id: str, project_id: str, file_type: Optional[str] = None, path_pattern: Optional[str] = None):
    """
    Scan the project directory for code files.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Scan for code files
        files = await list_code_files(
            user_id=user_id,
            project_id=project_id,
            file_type=file_type,
            path_pattern=path_pattern
        )
        
        return {
            "files": files,
            "total_count": len(files)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in scan_code_files_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to scan code files: {str(e)}")

# File Upload Endpoint (for web interface)
from fastapi import UploadFile, File, Form
from typing import List

@router.post("/{user_id}/{project_id}/code/upload")
async def upload_code_file_web(
    user_id: str,
    project_id: str,
    file: UploadFile = File(...),
    file_path: str = Form(...),
    file_type: str = Form("python"),
    description: str = Form(None)
):
    """
    Upload a code file via web interface (multipart form data).
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Prepare code file data
        code_file_data = {
            "user_id": user_id,
            "project_id": project_id,
            "filename": file.filename,
            "file_path": file_path,
            "file_type": file_type,
            "description": description,
            "size": len(content),
            "content_hash": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "pending",
            "error": None,
            "git_commit_hash": None
        }
        
        # Save to database first
        code_files_collection = await get_code_files_collection()
        result = await code_files_collection.insert_one(code_file_data)
        file_id = str(result.inserted_id)
        
        try:
            # Add code file using DVC handler
            dvc_result = await add_code_file(
                user_id=user_id,
                project_id=project_id,
                filename=file.filename,
                file_path=file_path,
                content=content_str,
                file_type=file_type,
                description=description
            )
            
            # Update database with results
            await code_files_collection.update_one(
                {"_id": ObjectId(file_id)},
                {
                    "$set": {
                        "status": "completed",
                        "size": dvc_result["size"],
                        "content_hash": dvc_result["content_hash"],
                        "git_commit_hash": dvc_result["git_commit_hash"],
                        "updated_at": datetime.now().isoformat()
                    }
                }
            )
            
            return {
                "message": "Code file uploaded successfully",
                "file_id": file_id,
                "file_path": file_path,
                "filename": file.filename,
                "git_commit_hash": dvc_result["git_commit_hash"]
            }
            
        except Exception as e:
            # Update status to failed
            await code_files_collection.update_one(
                {"_id": ObjectId(file_id)},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(e),
                        "updated_at": datetime.now().isoformat()
                    }
                }
            )
            raise e
            
    except HTTPException:
        raise
    except Exception as e:
        print("Error in upload_code_file_web:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to upload code file: {str(e)}")

@router.post("/{user_id}/{project_id}/code/upload/multiple")
async def upload_multiple_code_files_web(
    user_id: str,
    project_id: str,
    files: List[UploadFile] = File(...),
    base_path: str = Form("src")
):
    """
    Upload multiple code files via web interface.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        results = []
        successful_uploads = 0
        failed_uploads = 0
        
        for file in files:
            try:
                # Read file content
                content = await file.read()
                content_str = content.decode('utf-8')
                
                # Determine file path
                file_path = f"{base_path}/{file.filename}"
                
                # Determine file type
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext in ['.py']:
                    file_type = 'python'
                elif file_ext in ['.ipynb']:
                    file_type = 'jupyter'
                elif file_ext in ['.yaml', '.yml', '.json', '.toml', '.ini', '.cfg']:
                    file_type = 'config'
                elif file_ext in ['.md', '.txt', '.rst']:
                    file_type = 'documentation'
                else:
                    file_type = 'other'
                
                # Add code file using DVC handler
                dvc_result = await add_code_file(
                    user_id=user_id,
                    project_id=project_id,
                    filename=file.filename,
                    file_path=file_path,
                    content=content_str,
                    file_type=file_type
                )
                
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "file_path": file_path,
                    "git_commit_hash": dvc_result["git_commit_hash"]
                })
                successful_uploads += 1
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": str(e)
                })
                failed_uploads += 1
        
        return {
            "message": f"Multiple file upload completed: {successful_uploads} successful, {failed_uploads} failed",
            "results": results,
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in upload_multiple_code_files_web:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to upload multiple code files: {str(e)}")

@router.post("/{user_id}/{project_id}/pipeline/config/{config_id}/execute")
async def execute_pipeline_config(user_id: str, project_id: str, config_id: str, request: PipelineExecutionRequest = None):
    """
    Execute a specific pipeline configuration.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get pipeline configuration
        pipeline_configs_collection = await get_pipeline_configs_collection()
        config = await pipeline_configs_collection.find_one({
            "_id": ObjectId(config_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not config:
            raise HTTPException(status_code=404, detail="Pipeline configuration not found")
        
        # Validate pipeline before execution
        print("Validating pipeline before execution...")
        validation_result = await validate_pipeline(user_id, project_id)
        if not validation_result.get("valid", False):
            raise HTTPException(status_code=400, detail=f"Pipeline validation failed: {validation_result.get('details', 'Unknown error')}")
        
        # Execute the pipeline
        print("Executing pipeline...")
        execution_result = await repro(
            user_id=user_id,
            project_id=project_id,
            pipeline=True,
            force=request.force if request else False,
            dry_run=request.dry_run if request else False
        )
        
        # Update pipeline configuration with execution info
        await pipeline_configs_collection.update_one(
            {"_id": ObjectId(config_id)},
            {
                "$set": {
                    "last_executed": datetime.now().isoformat(),
                    "execution_count": config.get("execution_count", 0) + 1,
                    "updated_at": datetime.now().isoformat()
                }
            }
        )
        
        return {
            "message": f"Pipeline '{config['name']}' executed successfully",
            "config_id": config_id,
            "config_name": config["name"],
            "execution_result": execution_result,
            "validation": validation_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in execute_pipeline_config:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to execute pipeline configuration: {str(e)}")

@router.post("/{user_id}/{project_id}/pipeline/config/{config_id}/dry-run")
async def dry_run_pipeline_config(user_id: str, project_id: str, config_id: str):
    """
    Perform a dry run of a pipeline configuration.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get pipeline configuration
        pipeline_configs_collection = await get_pipeline_configs_collection()
        config = await pipeline_configs_collection.find_one({
            "_id": ObjectId(config_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not config:
            raise HTTPException(status_code=404, detail="Pipeline configuration not found")
        
        # Validate pipeline
        print("Validating pipeline for dry run...")
        validation_result = await validate_pipeline(user_id, project_id)
        
        # Perform dry run
        print("Performing dry run...")
        dry_run_result = await repro(
            user_id=user_id,
            project_id=project_id,
            pipeline=True,
            dry_run=True
        )
        
        return {
            "message": f"Dry run completed for pipeline '{config['name']}'",
            "config_id": config_id,
            "config_name": config["name"],
            "dry_run_result": dry_run_result,
            "validation": validation_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in dry_run_pipeline_config:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to perform dry run: {str(e)}")

@router.get("/{user_id}/{project_id}/pipeline/config/{config_id}/status")
async def get_pipeline_config_status(user_id: str, project_id: str, config_id: str):
    """
    Get the status and execution history of a pipeline configuration.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get pipeline configuration
        pipeline_configs_collection = await get_pipeline_configs_collection()
        config = await pipeline_configs_collection.find_one({
            "_id": ObjectId(config_id),
            "user_id": user_id,
            "project_id": project_id
        })
        
        if not config:
            raise HTTPException(status_code=404, detail="Pipeline configuration not found")
        
        # Get DVC status
        print("Getting DVC status...")
        dvc_status = await get_dvc_status(user_id, project_id)
        
        # Validate pipeline
        print("Validating pipeline...")
        validation_result = await validate_pipeline(user_id, project_id)
        
        # Get pipeline stages
        print("Getting pipeline stages...")
        pipeline_stages = await get_pipeline_stages(user_id, project_id)
        
        return {
            "config_id": config_id,
            "config_name": config["name"],
            "config_status": {
                "is_active": config.get("is_active", True),
                "created_at": config.get("created_at"),
                "updated_at": config.get("updated_at"),
                "last_executed": config.get("last_executed"),
                "execution_count": config.get("execution_count", 0)
            },
            "dvc_status": dvc_status,
            "validation": validation_result,
            "pipeline_stages": pipeline_stages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_pipeline_config_status:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline status: {str(e)}")

# Parameter Management Endpoints

@router.get("/{user_id}/{project_id}/parameters")
async def get_parameter_sets(user_id: str, project_id: str):
    """
    Get all parameter sets for a project.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get current parameter set
        param_result = await get_parameter_set(user_id, project_id)
        
        return {
            "parameter_sets": [param_result["parameter_set"]] if param_result["parameter_set"] else [],
            "current_set": param_result["parameter_set"],
            "file_path": param_result.get("file_path")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_parameter_sets:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get parameter sets: {str(e)}")

@router.get("/{user_id}/{project_id}/parameters/current")
async def get_current_parameters(user_id: str, project_id: str):
    """
    Get the current parameter set for a project.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get current parameter set
        param_result = await get_parameter_set(user_id, project_id)
        
        return param_result
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in get_current_parameters:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get current parameters: {str(e)}")

@router.post("/{user_id}/{project_id}/parameters")
async def create_parameter_set_endpoint(user_id: str, project_id: str, request: ParameterSetCreate):
    """
    Create a new parameter set for a project.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Prepare parameter set data
        parameter_set_data = {
            "name": request.name,
            "description": request.description,
            "groups": [group.dict() for group in request.groups],
            "is_default": request.is_default,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Validate parameters
        validation_result = await validate_parameters(user_id, project_id, parameter_set_data)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Parameter validation failed: {validation_result['errors']}"
            )
        
        # Create parameter set
        result = await create_parameter_set(user_id, project_id, parameter_set_data)
        
        return {
            "message": f"Parameter set '{request.name}' created successfully",
            "result": result,
            "validation": validation_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in create_parameter_set_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create parameter set: {str(e)}")

@router.put("/{user_id}/{project_id}/parameters")
async def update_parameter_set_endpoint(user_id: str, project_id: str, request: ParameterSetUpdate):
    """
    Update the current parameter set for a project.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get current parameter set
        current_result = await get_parameter_set(user_id, project_id)
        if not current_result["parameter_set"]:
            raise HTTPException(status_code=404, detail="No parameter set found to update")
        
        # Prepare updated parameter set data
        current_set = current_result["parameter_set"]
        updated_set = {
            "name": request.name or current_set["name"],
            "description": request.description or current_set.get("description"),
            "groups": [group.dict() for group in request.groups] if request.groups else current_set["groups"],
            "is_default": request.is_default if request.is_default is not None else current_set.get("is_default", False),
            "updated_at": datetime.now().isoformat()
        }
        
        # Validate parameters
        validation_result = await validate_parameters(user_id, project_id, updated_set)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Parameter validation failed: {validation_result['errors']}"
            )
        
        # Update parameter set
        result = await update_parameter_set(user_id, project_id, updated_set)
        
        return {
            "message": f"Parameter set updated successfully",
            "result": result,
            "validation": validation_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in update_parameter_set_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to update parameter set: {str(e)}")

@router.delete("/{user_id}/{project_id}/parameters")
async def delete_parameter_set_endpoint(user_id: str, project_id: str):
    """
    Delete the current parameter set for a project.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Delete parameter set
        result = await delete_parameter_set(user_id, project_id)
        
        return {
            "message": "Parameter set deleted successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in delete_parameter_set_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to delete parameter set: {str(e)}")

@router.post("/{user_id}/{project_id}/parameters/import")
async def import_parameters_endpoint(user_id: str, project_id: str, request: ParameterImportRequest):
    """
    Import parameters from an external source.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Import parameters
        result = await import_parameters_from_file(
            user_id, 
            project_id, 
            request.source_path, 
            request.source_type
        )
        
        return {
            "message": f"Parameters imported successfully from {request.source_path}",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in import_parameters_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to import parameters: {str(e)}")

@router.post("/{user_id}/{project_id}/parameters/upload")
async def upload_parameters_file(
    user_id: str,
    project_id: str,
    file: UploadFile = File(...),
    format: str = Form(None)
):
    """
    Upload and import parameters from a file.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Validate file type
        allowed_extensions = ['.yaml', '.yml', '.json', '.env']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        file_content_str = file_content.decode('utf-8')
        
        # Import parameters from uploaded file
        result = await import_parameters_from_upload(
            user_id,
            project_id,
            file_content_str,
            file.filename,
            format
        )
        
        return {
            "message": f"Parameters imported successfully from {file.filename}",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in upload_parameters_file:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to upload and import parameters: {str(e)}")

@router.post("/{user_id}/{project_id}/parameters/export")
async def export_parameters_endpoint(user_id: str, project_id: str, request: ParameterExportRequest):
    """
    Export parameters to a file in the specified format.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Export parameters
        result = await export_parameters_to_file(
            user_id, 
            project_id, 
            request.format, 
            request.include_metadata
        )
        
        return {
            "message": f"Parameters exported successfully to {request.format.upper()} format",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in export_parameters_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to export parameters: {str(e)}")

@router.post("/{user_id}/{project_id}/parameters/validate")
async def validate_parameters_endpoint(user_id: str, project_id: str, request: ParameterValidationRequest):
    """
    Validate parameter values against their validation rules.
    """
    try:
        # Verify project exists and belongs to user
        project_collection = await get_projects_collection()
        project = await project_collection.find_one({
            "_id": ObjectId(project_id),
            "user_id": user_id
        })
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get current parameter set
        param_result = await get_parameter_set(user_id, project_id)
        if not param_result["parameter_set"]:
            raise HTTPException(status_code=404, detail="No parameter set found to validate")
        
        # Validate parameters
        validation_result = await validate_parameters(user_id, project_id, param_result["parameter_set"])
        
        return {
            "message": "Parameter validation completed",
            "validation": validation_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error in validate_parameters_endpoint:", str(e))
        print("Traceback:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to validate parameters: {str(e)}")
