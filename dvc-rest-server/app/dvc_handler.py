import os
from subprocess import run, CalledProcessError
import asyncio
from asyncio.subprocess import PIPE
import logging
import hashlib
from datetime import datetime
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = "/home/marialuiza/Documents/faculdade/9periodo/poc/git_repo"  # Root directory of the Git repository

async def create_user_directory(user_id: str):
    """
    Create a new user directory in the repository root.
    """
    user_directory = os.path.join(REPO_ROOT, user_id)
    os.makedirs(user_directory, exist_ok=True)
    return user_directory

async def run_command_async(command: str, cwd: str = None):
    """
    Execute a shell command asynchronously in the specified directory.
    """
    process = await asyncio.create_subprocess_shell(
        command,
        cwd=cwd,
        stdout=PIPE,
        stderr=PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode().strip()
        output_msg = stdout.decode().strip()
        full_error = f"Command '{command}' failed with return code {process.returncode}"
        if error_msg:
            full_error += f"\nError: {error_msg}"
        if output_msg:
            full_error += f"\nOutput: {output_msg}"
        raise Exception(full_error)
    return stdout.decode().strip()

async def is_dvc_initialized(project_path: str) -> bool:
    """
    Check if DVC is initialized in the given project path.
    """
    return os.path.exists(os.path.join(project_path, ".dvc"))

async def is_git_initialized(project_path: str) -> bool:
    """
    Check if GIT is initialized in the given project path.
    """
    return os.path.exists(os.path.join(project_path, ".git"))

async def init_dvc(project_path: str):
    """
    Initialize DVC in the given project path.
    """
    await run_command_async("dvc init", cwd=project_path)
    
async def init_git(project_path: str, project_id: str):
    """
    Initialize Git and create the first commit. and push to remote
    """
    await run_command_async("git init", cwd=project_path)
    await run_command_async("echo '' > README.md", cwd=project_path)
    await run_command_async("git add .", cwd=project_path)
    await run_command_async('git commit -m "Initial commit"', cwd=project_path)
    await run_command_async(f"gh repo create https://github.com/MarialuizaLeao/{project_id}.git --public --source=. --remote=origin", cwd=project_path)
    await run_command_async("git push -u origin master", cwd=project_path)
    
async def create_project(user_id: str, project_id: str):
    """
    Creates a new project directory inside the Git root and initializes DVC.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    # Ensure the project path exists and DVC is initialized
    if os.path.exists(project_path):
        if not await is_git_initialized(project_path):
            await init_git(project_path,project_id)
        if not await is_dvc_initialized(project_path):
            await init_dvc(project_path)
    else:
        os.makedirs(project_path, exist_ok=True)
        await init_git(project_path,project_id)
        await init_dvc(project_path)

    # Add the project directory to Git
    try:

        # Add the project to Git
        await run_command_async(f"git add .", cwd=project_path)

        # Check for staged changes
        stdout = await run_command_async("git diff --cached --name-only", cwd=project_path)
        if not stdout.strip():
            raise Exception(f"No changes to commit for {user_id}/{project_id}")

        # Commit changes
        await run_command_async(f'git commit -m "Initialized project {project_id}"', cwd=project_path)

        # Push changes to the remote repository
        await run_command_async("git push", cwd=project_path)

    except Exception as e:
        raise Exception(f"Error while creating project: {str(e)}")

    return project_path

async def get_url(user_id: str, project_id: str, url: str, dest: str = "."):
    """
    Runs the `dvc get-url` command to download a file or directory from a remote URL.

    Args:
        url (str): The remote URL to download the file or directory from.
        output_path (str): The path where the downloaded content will be saved locally.
        cwd (str): The directory in which to run the command (optional).

    Returns:
        str: The path to the downloaded file or directory.

    Raises:
        Exception: If the `dvc get-url` command fails.
    """
    print(f"Getting URL: {url} to {dest}")
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    command = f"dvc get-url {url} {dest}"
    print(f"Running command: {command} in {project_path}")
    print(f"Running command: {command} in {project_path}")

    process = await asyncio.create_subprocess_shell(
        command,
        cwd=project_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"`dvc get-url` failed: {stderr.decode().strip()}")

    print(f"DVC output: {stdout.decode().strip()}")
    
    # Add the downloaded file to dvc
    await run_command_async(f"dvc add {dest}", cwd=project_path)
    
    # Add the file to git
    await run_command_async(f"git add {dest}.dvc data/.gitignore", cwd=project_path)
    await run_command_async(f"git commit -m 'added {dest}'", cwd=project_path)
    await run_command_async(f"git push", cwd=project_path)
    
    
    return stdout.decode().strip()

async def track_data(user_id: str, project_id: str, files: list):
    """
    Tracks data files and directories using DVC.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    try:
        for file in files:
            await run_command_async(f"dvc add {file}", cwd=project_path)
        await run_command_async("git commit -m 'tracking data'", cwd=project_path)
        
        return "Data tracked successfully."
    except Exception as e:
        raise Exception(f"Failed to track data: {str(e)}")

async def track_files(user_id: str, project_id: str, files: list):
    """
    Tracks data files and directories using DVC.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    try:
        for file in files:
            await run_command_async(f"dvc add {file}", cwd=project_path)
        await run_command_async("git commit -m 'tracking: {files}'", cwd=project_path)
        
        return "Data tracked successfully."
    except Exception as e:
        raise Exception(f"Failed to track data: {str(e)}")

async def clone_project(user_id: str, project_id: str, remote_url: str):
    """
    Clones a project from a remote repository.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    try:
        # Add the remote repository
        await run_command_async(f"git remote add temp_remote {remote_url}", cwd=project_path)
        
        # Fetch the contents of the remote repository
        await run_command_async("git fetch temp_remote", cwd=project_path)
        
        # Merge the contents into the current repository, favoring the remote changes in case of conflicts
        merge_message = "Merged contents from remote repository"
        await run_command_async(f"git merge temp_remote/master -X theirs --allow-unrelated-histories -m '{merge_message}'", cwd=project_path)
        
        # Remove the temporary remote
        await run_command_async("git remote remove temp_remote", cwd=project_path)
        
        return "Repository contents extracted successfully."
    except CalledProcessError as e:
        raise Exception(f"Failed to clone project: {e.stderr or e.stdout}")

async def set_remote(user_id: str, project_id: str, remote_url: str, remote_name: str):
    """
    Sets a DVC remote for the project.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    try:
        await run_command_async(f"dvc remote add -d {remote_name} {remote_url}", cwd=project_path)
        return "Remote set successfully."
    except Exception as e:
        raise Exception(f"Failed to set remote: {str(e)}")
    
async def push_data(user_id: str, project_id: str):
    """
    Pushes the project data to the remote storage.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    try:
        await run_command_async("dvc push", cwd=project_path)
        return "Data pushed successfully."
    except Exception as e:
        raise Exception(f"Failed to push data: {str(e)}")
    
async def pull_data(user_id: str, project_id: str):
    """
    Pulls the project data from the remote storage.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    try:
        await run_command_async("dvc pull", cwd=project_path)
        return "Data pulled successfully."
    except Exception as e:
        raise Exception(f"Failed to pull data: {str(e)}")    
    
async def list_dvc_branches(cwd: str = None):
    """
    List all DVC branches in the current repository.

    Args:
        cwd (str): Directory to run the command.

    Returns:
        list: A list of branch names.
    """
    command = "dvc exp branch --list"
    process = await asyncio.create_subprocess_shell(
        command,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"Error listing DVC branches: {stderr.decode().strip()}")

    return stdout.decode().strip().split("\n")

async def checkout_dvc_branch(branch_name: str, cwd: str = None):
    """
    Checkout to a specific DVC branch.

    Args:
        branch_name (str): The name of the branch to checkout.
        cwd (str): Directory to run the command.

    Returns:
        str: Confirmation message of the checkout.
    """
    command = f"git checkout {branch_name}"
    process = await asyncio.create_subprocess_shell(
        command,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"Error checking out branch {branch_name}: {stderr.decode().strip()}")

    return f"Checked out to branch: {branch_name}"

async def create_dvc_branch(branch_name: str, cwd: str = None):
    """
    Create a new DVC branch.

    Args:
        branch_name (str): The name of the new branch.
        cwd (str): Directory to run the command.

    Returns:
        str: Confirmation message of branch creation.
    """
    command = f"dvc exp branch {branch_name}"
    process = await asyncio.create_subprocess_shell(
        command,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"Error creating DVC branch {branch_name}: {stderr.decode().strip()}")

    return f"Branch '{branch_name}' created successfully."
    
async def delete_dvc_branch(branch_name: str, cwd: str = None):
    """
    Delete a DVC branch.

    Args:
        branch_name (str): The name of the branch to delete.
        cwd (str): Directory to run the command.

    Returns:
        str: Confirmation message of branch deletion.
    """
    command = f"git branch -D {branch_name}"
    process = await asyncio.create_subprocess_shell(
        command,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"Error deleting branch {branch_name}: {stderr.decode().strip()}")

    return f"Branch '{branch_name}' deleted successfully."    
    
async def add_stages(user_id: str, project_id:str, stages: list):
    """
    Adds multiple DVC stages to connect code and data.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        stages (list): List of stage commands as strings
    
    Returns:
        str: Success message
    
    Raises:
        Exception: If any stage creation fails
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    # Verify project path exists
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    if not stages:
        raise Exception("No stages provided")
    
    try:
        successful_stages = []
        failed_stages = []
        
        for i, stage_command in enumerate(stages):
            if not stage_command or not stage_command.strip():
                continue
                
            try:
                print(f"Executing stage {i+1}/{len(stages)}: {stage_command}")
                await run_command_async(stage_command.strip(), cwd=project_path)
                successful_stages.append(stage_command)
            except Exception as e:
                error_msg = str(e)
                failed_stages.append(f"Stage {i+1}: {error_msg}")
        
        # If any stages failed, report them
        if failed_stages:
            error_details = "; ".join(failed_stages)
            raise Exception(f"Some stages failed: {error_details}")
        
        # Add the dvc.yaml file to git
        await run_command_async("git add dvc.yaml", cwd=project_path)
        
        # Commit all changes
        await run_command_async(f'git commit -m "Added {len(successful_stages)} DVC stages"', cwd=project_path)
        
        return f"Successfully added {len(successful_stages)} stages."
        
    except Exception as e:
        raise Exception(f"Failed to add stages: {str(e)}")

async def add_stage(user_id: str, project_id:str, name: str, deps: list = None, outs: list = None, params: list = None, metrics: list = None, plots: list = None, command: str = None):
    """
    Adds a DVC stage to connect code and data.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        name (str): The name of the stage
        deps (list, optional): List of dependencies (files/directories)
        outs (list, optional): List of outputs (files/directories)
        params (list, optional): List of parameter files
        metrics (list, optional): List of metric files
        plots (list, optional): List of plot files
        command (str, optional): The command to execute
    
    Returns:
        str: Success message
    
    Raises:
        Exception: If the stage creation fails
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    # Verify project path exists
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    try:
        # Build the dvc stage add command
        stage_command = f"dvc stage add -n {name}"
        
        # Add dependencies
        if deps:
            for dep in deps:
                if dep.strip():  # Skip empty strings
                    stage_command += f" -d {dep.strip()}"
        
        # Add outputs
        if outs:
            for out in outs:
                if out.strip():  # Skip empty strings
                    stage_command += f" -o {out.strip()}"
        
        # Add parameters
        if params:
            for param in params:
                if param.strip():  # Skip empty strings
                    stage_command += f" -p {param.strip()}"
        
        # Add metrics
        if metrics:
            for metric in metrics:
                if metric.strip():  # Skip empty strings
                    stage_command += f" -M {metric.strip()}"
        
        # Add plots
        if plots:
            for plot in plots:
                if plot.strip():  # Skip empty strings
                    stage_command += f" -m {plot.strip()}"
        
        # Add the command
        if command and command.strip():
            stage_command += f" {command.strip()}"
        else:
            raise Exception("Command is required for stage creation")
        
        print(f"Executing DVC stage command: {stage_command}")
        
        # Execute the stage creation command
        await run_command_async(stage_command, cwd=project_path)
        
        # Add the dvc.yaml file to git
        await run_command_async("git add dvc.yaml", cwd=project_path)
        
        # Commit the changes
        await run_command_async(f'git commit -m "Added DVC stage: {name}"', cwd=project_path)
        
        return f"Stage '{name}' added successfully."
        
    except Exception as e:
        raise Exception(f"Failed to add stage '{name}': {str(e)}")

async def repro(
    user_id: str,
    project_id: str,
    target: str = None,
    pipeline: bool = False,
    force: bool = False,
    dry_run: bool = False,
    no_commit: bool = False,
    cwd: str = None,
):
    """
    Run the `dvc repro` command with various options to reproduce a pipeline stage.

    Args:
        user_id (str): The ID of the user initiating the repro.
        project_id (str): The ID of the project containing the stage.
        target (str, optional): Specify the target stage or file to reproduce.
        pipeline (bool, optional): Reproduce the entire pipeline containing the target.
        force (bool, optional): Force reproduction even if outputs are up-to-date.
        dry_run (bool, optional): Show what will be done without actually executing.
        no_commit (bool, optional): Do not commit changes to cache.
        cwd (str, optional): Directory to run the `dvc repro` command.

    Returns:
        str: The output of the `dvc repro` command.

    Raises:
        Exception: If the `dvc repro` command fails.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    # Build the command
    command = "dvc repro"
    if target:
        command += f" {target}"
    if pipeline:
        command += " --pipeline"
    if force:
        command += " --force"
    if dry_run:
        command += " --dry"
    if no_commit:
        command += " --no-commit"

    # Print debugging info (optional)
    print(f"Running command: {command} in {project_path}")

    # Run the command asynchronously
    process = await asyncio.create_subprocess_shell(
        command,
        cwd=project_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"Error running `dvc repro`: {stderr.decode().strip()}")
    
    # Use safe git commit to handle cases where there are no changes
    await safe_git_commit(project_path, "pipeline repro")

    return stdout.decode().strip()

async def dvc_metrics_show(user_id: str, project_id:str, all_commits: bool = False, json: bool = False, yaml: bool = False):
    """
    Show metrics using `dvc metrics show`.

    Args:
        cwd (str): The directory to run the command in.
        all_commits (bool, optional): Show metrics from all commits.
        json (bool, optional): Output in JSON format.
        yaml (bool, optional): Output in YAML format.

    Returns:
        str: The output of the `dvc metrics show` command.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    command = "dvc metrics show"
    if all_commits:
        command += " --all-commits"
    if json:
        command += " --json"
    if yaml:
        command += " --yaml"

    process = await asyncio.create_subprocess_shell(
        command, cwd=project_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"`dvc metrics show` failed: {stderr.decode().strip()}")

    return stdout.decode().strip()

async def dvc_metrics_diff(
    user_id: str, project_id:str,
    a_rev: str = None,
    b_rev: str = None,
    all: bool = False,
    precision: int = None,
    json: bool = False,
    csv: bool = False,
    md: bool = False,
):
    """
    Show the difference in metrics between two commits using `dvc metrics diff`.

    Args:
        cwd (str): The directory to run the command in.
        a_rev (str, optional): The starting commit or revision.
        b_rev (str, optional): The ending commit or revision.
        all (bool, optional): Show all metrics, even unchanged ones.
        precision (int, optional): Number of decimal places for metric values.
        json (bool, optional): Output in JSON format.
        csv (bool, optional): Output in CSV format.
        md (bool, optional): Output in Markdown format.

    Returns:
        str: The output of the `dvc metrics diff` command.

    Raises:
        Exception: If the `dvc metrics diff` command fails.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    command = "dvc metrics diff"

    if a_rev:
        command += f" {a_rev}"
    if b_rev:
        command += f" {b_rev}"
    if all:
        command += " --all"
    if precision is not None:
        command += f" --precision {precision}"
    if json:
        command += " --json"
    if csv:
        command += " --csv"
    if md:
        command += " --md"

    process = await asyncio.create_subprocess_shell(
        command, cwd=project_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"`dvc metrics diff` failed: {stderr.decode().strip()}")

    return stdout.decode().strip()

async def dvc_plots_show(
    user_id: str, project_id:str,
    targets: list = None,
    json: bool = False,
    html: bool = False,
    no_html: bool = False,
    templates_dir: str = None,
    out: str = None,
):
    """
    Show plots with options for output format and customization.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    command = "dvc plots show"

    if targets:
        command += f" {' '.join(targets)}"
    if json:
        command += " --json"
    if html:
        command += " --html"
    if no_html:
        command += " --no-html"
    if templates_dir:
        command += f" --templates-dir {templates_dir}"
    if out:
        command += f" --out {out}"

    try:
        result = await run_command_async(command, cwd=project_path)
        return result
    except Exception as e:
        raise Exception(f"Failed to show plots: {str(e)}")

async def dvc_plots_diff(
    user_id: str, project_id:str,
    targets: list = None,
    a_rev: str = None,
    b_rev: str = None,
    templates_dir: str = None,
    json: bool = False,
    html: bool = False,
    no_html: bool = False,
    out: str = None,
):
    """
    Show plots diff with options for output format and customization.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    command = "dvc plots diff"

    if targets:
        command += f" {' '.join(targets)}"
    if a_rev:
        command += f" --a-rev {a_rev}"
    if b_rev:
        command += f" --b-rev {b_rev}"
    if templates_dir:
        command += f" --templates-dir {templates_dir}"
    if json:
        command += " --json"
    if html:
        command += " --html"
    if no_html:
        command += " --no-html"
    if out:
        command += f" --out {out}"

    try:
        result = await run_command_async(command, cwd=project_path)
        return result
    except Exception as e:
        raise Exception(f"Failed to show plots diff: {str(e)}")

async def get_dvc_status(user_id: str, project_id: str):
    """
    Get DVC status showing tracked, untracked, and modified files.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    try:
        # Get DVC status
        status_output = await run_command_async("dvc status", cwd=project_path)
        
        # Initialize result structure
        result = {
            "tracked": [],
            "untracked": [],
            "modified": [],
            "total_size": 0
        }
        
        # Parse the status output
        lines = status_output.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if "Tracked files:" in line:
                current_section = "tracked"
                continue
            elif "Untracked files:" in line:
                current_section = "untracked"
                continue
            elif "Modified files:" in line:
                current_section = "modified"
                continue
            elif "Not in cache:" in line:
                current_section = "untracked"
                continue
                
            # Parse file entries
            if current_section and line and not line.startswith("Not in cache:"):
                # Extract file path and size
                parts = line.split()
                if len(parts) >= 1:
                    file_path = parts[0]
                    
                    # Get file size
                    try:
                        file_size = os.path.getsize(os.path.join(project_path, file_path))
                    except OSError:
                        file_size = 0
                    
                    file_info = {
                        "path": file_path,
                        "size": file_size
                    }
                    
                    result[current_section].append(file_info)
                    result["total_size"] += file_size
        
        return result
        
    except Exception as e:
        # If DVC status fails, return empty result
        logger.warning(f"DVC status failed for {user_id}/{project_id}: {str(e)}")
        return {
            "tracked": [],
            "untracked": [],
            "modified": [],
            "total_size": 0
        }

async def create_pipeline_template(user_id: str, project_id: str, template_name: str, stages: list):
    """
    Creates a pipeline template with predefined stages.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        template_name (str): Name of the template
        stages (list): List of stage configurations
    
    Returns:
        str: Success message
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    print(f"Creating pipeline template in: {project_path}")
    print(f"Template name: {template_name}")
    print(f"Stages: {stages}")
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    try:
        # Create a dvc.yaml file with the template
        dvc_yaml_content = f"# Pipeline Template: {template_name}\nstages:\n"
        
        for stage in stages:
            stage_name = stage.get('name', 'unnamed_stage')
            print(f"Processing stage: {stage_name}")
            dvc_yaml_content += f"  {stage_name}:\n"
            
            # Add dependencies
            if stage.get('deps'):
                deps = stage['deps']
                if isinstance(deps, list):
                    dvc_yaml_content += f"    deps:\n"
                    for dep in deps:
                        dvc_yaml_content += f"      - {dep}\n"
                else:
                    dvc_yaml_content += f"    deps: {deps}\n"
            
            # Add outputs
            if stage.get('outs'):
                outs = stage['outs']
                if isinstance(outs, list):
                    dvc_yaml_content += f"    outs:\n"
                    for out in outs:
                        dvc_yaml_content += f"      - {out}\n"
                else:
                    dvc_yaml_content += f"    outs: {outs}\n"
            
            # Add parameters
            if stage.get('params'):
                params = stage['params']
                if isinstance(params, list):
                    dvc_yaml_content += f"    params:\n"
                    for param in params:
                        dvc_yaml_content += f"      - {param}\n"
                else:
                    dvc_yaml_content += f"    params: {params}\n"
            
            # Add metrics
            if stage.get('metrics'):
                metrics = stage['metrics']
                if isinstance(metrics, list):
                    dvc_yaml_content += f"    metrics:\n"
                    for metric in metrics:
                        dvc_yaml_content += f"      - {metric}\n"
                else:
                    dvc_yaml_content += f"    metrics: {metrics}\n"
            
            # Add plots
            if stage.get('plots'):
                plots = stage['plots']
                if isinstance(plots, list):
                    dvc_yaml_content += f"    plots:\n"
                    for plot in plots:
                        dvc_yaml_content += f"      - {plot}\n"
                else:
                    dvc_yaml_content += f"    plots: {plots}\n"
            
            # Add command
            if stage.get('command'):
                dvc_yaml_content += f"    cmd: {stage['command']}\n"
        
        print(f"Generated dvc.yaml content:\n{dvc_yaml_content}")
        
        # Write the dvc.yaml file
        dvc_yaml_path = os.path.join(project_path, 'dvc.yaml')
        print(f"Writing dvc.yaml to: {dvc_yaml_path}")
        
        with open(dvc_yaml_path, 'w') as f:
            f.write(dvc_yaml_content)
        
        print("dvc.yaml file written successfully")
        
        # Add to git and commit
        print("Adding dvc.yaml to git...")
        await run_command_async("git add dvc.yaml", cwd=project_path)
        
        print("Committing changes...")
        await run_command_async(f'git commit -m "Created pipeline template: {template_name}"', cwd=project_path)
        
        print("Pipeline template created successfully")
        return f"Pipeline template '{template_name}' created successfully with {len(stages)} stages."
        
    except Exception as e:
        print(f"Error in create_pipeline_template: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Failed to create pipeline template: {str(e)}")

async def get_pipeline_stages(user_id: str, project_id: str):
    """
    Gets the current pipeline stages from dvc.yaml.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
    
    Returns:
        dict: Pipeline stages configuration
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    dvc_yaml_path = os.path.join(project_path, 'dvc.yaml')
    
    if not os.path.exists(dvc_yaml_path):
        return {"stages": {}}
    
    try:
        with open(dvc_yaml_path, 'r') as f:
            pipeline_config = yaml.safe_load(f)
        
        return pipeline_config or {"stages": {}}
    except Exception as e:
        raise Exception(f"Failed to read pipeline stages: {str(e)}")

async def update_pipeline_stage(user_id: str, project_id: str, stage_name: str, updates: dict):
    """
    Updates an existing pipeline stage.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        stage_name (str): Name of the stage to update
        updates (dict): Updates to apply to the stage
    
    Returns:
        str: Success message
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    dvc_yaml_path = os.path.join(project_path, 'dvc.yaml')
    
    if not os.path.exists(dvc_yaml_path):
        raise Exception("No dvc.yaml file found")
    
    try:
        with open(dvc_yaml_path, 'r') as f:
            pipeline_config = yaml.safe_load(f) or {"stages": {}}
        
        # Update the stage
        if 'stages' not in pipeline_config:
            pipeline_config['stages'] = {}
        
        if stage_name not in pipeline_config['stages']:
            raise Exception(f"Stage '{stage_name}' not found")
        
        # Apply updates
        for key, value in updates.items():
            pipeline_config['stages'][stage_name][key] = value
        
        # Write back to file
        with open(dvc_yaml_path, 'w') as f:
            yaml.dump(pipeline_config, f, default_flow_style=False)
        
        # Add to git and commit
        await run_command_async("git add dvc.yaml", cwd=project_path)
        await run_command_async(f'git commit -m "Updated stage: {stage_name}"', cwd=project_path)
        
        return f"Stage '{stage_name}' updated successfully."
        
    except Exception as e:
        raise Exception(f"Failed to update stage: {str(e)}")

async def remove_pipeline_stage(user_id: str, project_id: str, stage_name: str):
    """
    Removes a pipeline stage from dvc.yaml.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        stage_name (str): Name of the stage to remove
    
    Returns:
        str: Success message
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    dvc_yaml_path = os.path.join(project_path, 'dvc.yaml')
    
    if not os.path.exists(dvc_yaml_path):
        raise Exception("No dvc.yaml file found")
    
    try:
        with open(dvc_yaml_path, 'r') as f:
            pipeline_config = yaml.safe_load(f) or {"stages": {}}
        
        # Remove the stage
        if 'stages' in pipeline_config and stage_name in pipeline_config['stages']:
            del pipeline_config['stages'][stage_name]
        else:
            raise Exception(f"Stage '{stage_name}' not found")
        
        # Write back to file
        with open(dvc_yaml_path, 'w') as f:
            yaml.dump(pipeline_config, f, default_flow_style=False)
        
        # Add to git and commit
        await run_command_async("git add dvc.yaml", cwd=project_path)
        await run_command_async(f'git commit -m "Removed stage: {stage_name}"', cwd=project_path)
        
        return f"Stage '{stage_name}' removed successfully."
        
    except Exception as e:
        raise Exception(f"Failed to remove stage: {str(e)}")

async def validate_pipeline(user_id: str, project_id: str):
    """
    Validates the current pipeline configuration.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
    
    Returns:
        dict: Validation results
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    try:
        # Run dvc check to validate the pipeline
        result = await run_command_async("dvc check", cwd=project_path)
        
        return {
            "valid": True,
            "message": "Pipeline validation successful",
            "details": result
        }
    except Exception as e:
        return {
            "valid": False,
            "message": "Pipeline validation failed",
            "details": str(e)
        }

# Data Source Management Functions

async def add_data_source(user_id: str, project_id: str, name: str, source_type: str, source_path: str, destination: str, description: str = None):
    """
    Add a data source to the project.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        name (str): Name of the data source
        source_type (str): Type of data source (url, local, remote)
        source_path (str): Path or URL to the data source
        destination (str): Where to store the data in the project
        description (str, optional): Description of the data source
    
    Returns:
        str: Success message
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    try:
        # Create destination directory if it doesn't exist
        dest_path = os.path.join(project_path, destination)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        if source_type == "url":
            # Download from URL
            await run_command_async(f"curl -L -o {dest_path} {source_path}", cwd=project_path)
        elif source_type == "local":
            # Copy from local path
            if os.path.exists(source_path):
                await run_command_async(f"cp -r {source_path} {dest_path}", cwd=project_path)
            else:
                raise Exception(f"Source path does not exist: {source_path}")
        elif source_type == "remote":
            # Use DVC to get from remote
            await run_command_async(f"dvc get {source_path} {dest_path}", cwd=project_path)
        else:
            raise Exception(f"Unsupported source type: {source_type}")
        
        # Add to DVC tracking
        await run_command_async(f"dvc add {destination}", cwd=project_path)
        
        # Commit changes
        await run_command_async("git add .", cwd=project_path)
        await run_command_async(f'git commit -m "Added data source: {name}"', cwd=project_path)
        
        return f"Data source '{name}' added successfully to {destination}"
        
    except Exception as e:
        raise Exception(f"Failed to add data source: {str(e)}")

async def remove_data_source(user_id: str, project_id: str, destination: str):
    """
    Remove a data source from the project.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        destination (str): Path to the data source in the project
    
    Returns:
        str: Success message
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    try:
        # Remove from DVC tracking
        await run_command_async(f"dvc remove {destination}", cwd=project_path)
        
        # Remove the actual file/directory
        dest_path = os.path.join(project_path, destination)
        if os.path.exists(dest_path):
            if os.path.isdir(dest_path):
                await run_command_async(f"rm -rf {destination}", cwd=project_path)
            else:
                await run_command_async(f"rm {destination}", cwd=project_path)
        
        # Commit changes
        await run_command_async("git add .", cwd=project_path)
        await run_command_async(f'git commit -m "Removed data source: {destination}"', cwd=project_path)
        
        return f"Data source '{destination}' removed successfully"
        
    except Exception as e:
        raise Exception(f"Failed to remove data source: {str(e)}")

async def update_data_source(user_id: str, project_id: str, destination: str, new_source_path: str, source_type: str = "url"):
    """
    Update a data source with new data.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        destination (str): Path to the data source in the project
        new_source_path (str): New path or URL to the data source
        source_type (str): Type of data source (url, local, remote)
    
    Returns:
        str: Success message
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    try:
        # Remove existing data source
        await remove_data_source(user_id, project_id, destination)
        
        # Add new data source
        await add_data_source(user_id, project_id, f"updated_{destination}", source_type, new_source_path, destination)
        
        return f"Data source '{destination}' updated successfully"
        
    except Exception as e:
        raise Exception(f"Failed to update data source: {str(e)}")

# Remote Storage Management Functions

async def add_remote_storage(user_id: str, project_id: str, name: str, url: str, remote_type: str = "default"):
    """
    Add a remote storage to the project.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        name (str): Name of the remote storage
        url (str): URL of the remote storage
        remote_type (str): Type of remote storage (default, cache, etc.)
    
    Returns:
        str: Success message
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    # Validate and sanitize the remote name
    if not name or not name.strip():
        raise Exception("Remote storage name cannot be empty")
    
    # Sanitize the name: remove spaces and special characters, keep only alphanumeric, hyphens, and underscores
    sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name.strip())
    
    # Ensure the name is not empty after sanitization
    if not sanitized_name:
        raise Exception("Remote storage name cannot be empty after sanitization")
    
    # Limit the name length to avoid issues
    if len(sanitized_name) > 50:
        sanitized_name = sanitized_name[:50]
    
    try:
        # Add remote storage using sanitized name
        await run_command_async(f"dvc remote add {sanitized_name} {url}", cwd=project_path)
        
        # Set as default if specified
        if remote_type == "default":
            await run_command_async(f"dvc remote default {sanitized_name}", cwd=project_path)
        
        # Commit changes
        await run_command_async("git add .dvc/config", cwd=project_path)
        await run_command_async(f'git commit -m "Added remote storage: {sanitized_name}"', cwd=project_path)
        
        return f"Remote storage '{sanitized_name}' added successfully"
        
    except Exception as e:
        raise Exception(f"Failed to add remote storage: {str(e)}")

async def remove_remote_storage(user_id: str, project_id: str, name: str):
    """
    Remove a remote storage from the project.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        name (str): Name of the remote storage
    
    Returns:
        str: Success message
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    try:
        # Remove remote storage
        await run_command_async(f"dvc remote remove {name}", cwd=project_path)
        
        # Commit changes
        await run_command_async("git add .dvc/config", cwd=project_path)
        await run_command_async(f'git commit -m "Removed remote storage: {name}"', cwd=project_path)
        
        return f"Remote storage '{name}' removed successfully"
        
    except Exception as e:
        raise Exception(f"Failed to remove remote storage: {str(e)}")

async def list_remote_storages(user_id: str, project_id: str):
    """
    List all remote storages for the project.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
    
    Returns:
        dict: Remote storage information
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    try:
        # Get remote storage information
        result = await run_command_async("dvc remote list", cwd=project_path)
        
        # Parse the output to extract remote information
        remotes = {}
        lines = result.strip().split('\n')
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    url = parts[1]
                    remotes[name] = {
                        "name": name,
                        "url": url,
                        "type": "default" if "default" in line else "cache"
                    }
        
        return {"remotes": remotes}
        
    except Exception as e:
        raise Exception(f"Failed to list remote storages: {str(e)}")

async def push_to_remote(user_id: str, project_id: str, remote_name: str = None, target: str = None):
    """
    Push data to a remote storage.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        remote_name (str, optional): Name of the remote storage
        target (str, optional): Specific target to push
    
    Returns:
        str: Success message
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    try:
        # Build push command
        command = "dvc push"
        if remote_name:
            command += f" --remote {remote_name}"
        if target:
            command += f" {target}"
        
        # Execute push
        await run_command_async(command, cwd=project_path)
        
        return f"Data pushed to remote storage successfully"
        
    except Exception as e:
        raise Exception(f"Failed to push to remote storage: {str(e)}")

async def pull_from_remote(user_id: str, project_id: str, remote_name: str = None, target: str = None):
    """
    Pull data from a remote storage.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        remote_name (str, optional): Name of the remote storage
        target (str, optional): Specific target to pull
    
    Returns:
        str: Success message
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    try:
        # Build pull command
        command = "dvc pull"
        if remote_name:
            command += f" --remote {remote_name}"
        if target:
            command += f" {target}"
        
        # Execute pull
        await run_command_async(command, cwd=project_path)
        
        return f"Data pulled from remote storage successfully"
        
    except Exception as e:
        raise Exception(f"Failed to pull from remote storage: {str(e)}")

async def sync_with_remote(user_id: str, project_id: str, remote_name: str = None):
    """
    Sync data with a remote storage.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        remote_name (str, optional): Name of the remote storage
    
    Returns:
        str: Success message
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    try:
        # Build sync command
        command = "dvc sync"
        if remote_name:
            command += f" --remote {remote_name}"
        
        # Execute sync
        await run_command_async(command, cwd=project_path)
        
        return f"Data synced with remote storage successfully"
        
    except Exception as e:
        raise Exception(f"Failed to sync with remote storage: {str(e)}")

# Code Management Functions

async def add_code_file(user_id: str, project_id: str, filename: str, file_path: str, content: str, file_type: str = "python", description: str = None):
    """
    Add a code file to the project using DVC.
    """
    try:
        project_path = os.path.join(REPO_ROOT, user_id, project_id)
        
        # Ensure project directory exists
        os.makedirs(project_path, exist_ok=True)
        
        # Create the file path
        full_file_path = os.path.join(project_path, file_path)
        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
        
        # Write content to file
        with open(full_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Add file to Git
        git_add_cmd = f"git add {file_path}"
        await run_command_async(git_add_cmd, cwd=project_path)
        
        # Commit the file
        commit_message = f"Add {filename}"
        if description:
            commit_message += f": {description}"
        
        git_commit_cmd = f'git commit -m "{commit_message}"'
        commit_result = await run_command_async(git_commit_cmd, cwd=project_path)
        
        # Get commit hash
        git_hash_cmd = "git rev-parse HEAD"
        hash_result = await run_command_async(git_hash_cmd, cwd=project_path)
        commit_hash = hash_result.strip()
        
        # Calculate content hash
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        return {
            "status": "success",
            "message": f"Code file {filename} added successfully",
            "file_path": file_path,
            "size": len(content.encode('utf-8')),
            "content_hash": content_hash,
            "git_commit_hash": commit_hash
        }
        
    except Exception as e:
        print(f"Error adding code file: {str(e)}")
        raise Exception(f"Failed to add code file: {str(e)}")

async def update_code_file(user_id: str, project_id: str, file_path: str, content: str, description: str = None):
    """
    Update an existing code file.
    """
    try:
        project_path = os.path.join(REPO_ROOT, user_id, project_id)
        full_file_path = os.path.join(project_path, file_path)
        
        # Check if file exists
        if not os.path.exists(full_file_path):
            raise Exception(f"File {file_path} does not exist")
        
        # Write new content to file
        with open(full_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Add file to Git
        git_add_cmd = f"git add {file_path}"
        await run_command_async(git_add_cmd, cwd=project_path)
        
        # Commit the changes
        commit_message = f"Update {os.path.basename(file_path)}"
        if description:
            commit_message += f": {description}"
        
        git_commit_cmd = f'git commit -m "{commit_message}"'
        commit_result = await run_command_async(git_commit_cmd, cwd=project_path)
        
        # Get commit hash
        git_hash_cmd = "git rev-parse HEAD"
        hash_result = await run_command_async(git_hash_cmd, cwd=project_path)
        commit_hash = hash_result.strip()
        
        # Calculate content hash
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        return {
            "status": "success",
            "message": f"Code file {file_path} updated successfully",
            "size": len(content.encode('utf-8')),
            "content_hash": content_hash,
            "git_commit_hash": commit_hash
        }
        
    except Exception as e:
        print(f"Error updating code file: {str(e)}")
        raise Exception(f"Failed to update code file: {str(e)}")

async def remove_code_file(user_id: str, project_id: str, file_path: str):
    """
    Remove a code file from the project.
    """
    try:
        project_path = os.path.join(REPO_ROOT, user_id, project_id)
        full_file_path = os.path.join(project_path, file_path)
        
        # Check if file exists
        if not os.path.exists(full_file_path):
            raise Exception(f"File {file_path} does not exist")
        
        # Remove file from Git
        git_rm_cmd = f"git rm {file_path}"
        await run_command_async(git_rm_cmd, cwd=project_path)
        
        # Commit the removal
        commit_message = f"Remove {os.path.basename(file_path)}"
        git_commit_cmd = f'git commit -m "{commit_message}"'
        commit_result = await run_command_async(git_commit_cmd, cwd=project_path)
        
        # Get commit hash
        git_hash_cmd = "git rev-parse HEAD"
        hash_result = await run_command_async(git_hash_cmd, cwd=project_path)
        commit_hash = hash_result.strip()
        
        return {
            "status": "success",
            "message": f"Code file {file_path} removed successfully",
            "git_commit_hash": commit_hash
        }
        
    except Exception as e:
        print(f"Error removing code file: {str(e)}")
        raise Exception(f"Failed to remove code file: {str(e)}")

async def get_code_file_content(user_id: str, project_id: str, file_path: str):
    """
    Get the content of a code file.
    """
    try:
        project_path = os.path.join(REPO_ROOT, user_id, project_id)
        full_file_path = os.path.join(project_path, file_path)
        
        # Check if file exists
        if not os.path.exists(full_file_path):
            raise Exception(f"File {file_path} does not exist")
        
        # Read file content
        with open(full_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
        
    except Exception as e:
        print(f"Error getting code file content: {str(e)}")
        raise Exception(f"Failed to get code file content: {str(e)}")

async def list_code_files(user_id: str, project_id: str, file_type: str = None, path_pattern: str = None):
    """
    List code files in the project directory.
    """
    try:
        project_path = os.path.join(REPO_ROOT, user_id, project_id)
        
        # Check if project directory exists
        if not os.path.exists(project_path):
            return []
        
        files = []
        
        # Walk through the project directory
        for root, dirs, filenames in os.walk(project_path):
            # Skip .git and .dvc directories
            dirs[:] = [d for d in dirs if d not in ['.git', '.dvc']]
            
            for filename in filenames:
                # Skip hidden files and common non-code files
                if filename.startswith('.') or filename in ['__pycache__', '.DS_Store']:
                    continue
                
                # Get relative path
                rel_path = os.path.relpath(os.path.join(root, filename), project_path)
                
                # Apply path pattern filter
                if path_pattern and path_pattern not in rel_path:
                    continue
                
                # Determine file type
                file_ext = os.path.splitext(filename)[1].lower()
                detected_type = "other"
                
                if file_ext in ['.py']:
                    detected_type = 'python'
                elif file_ext in ['.ipynb']:
                    detected_type = 'jupyter'
                elif file_ext in ['.yaml', '.yml', '.json', '.toml', '.ini', '.cfg']:
                    detected_type = 'config'
                elif file_ext in ['.md', '.txt', '.rst']:
                    detected_type = 'documentation'
                elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
                    detected_type = 'javascript'
                elif file_ext in ['.html', '.css', '.scss', '.sass']:
                    detected_type = 'web'
                elif file_ext in ['.java', '.cpp', '.c', '.h', '.hpp']:
                    detected_type = 'compiled'
                
                # Apply file type filter
                if file_type and detected_type != file_type:
                    continue
                
                # Get file size
                full_path = os.path.join(root, filename)
                file_size = os.path.getsize(full_path)
                
                files.append({
                    "filename": filename,
                    "file_path": rel_path,
                    "file_type": detected_type,
                    "size": file_size,
                    "full_path": full_path
                })
        
        return files
        
    except Exception as e:
        print(f"Error listing code files: {str(e)}")
        raise Exception(f"Failed to list code files: {str(e)}")

async def bulk_upload_code_files(user_id: str, project_id: str, files: list):
    """
    Upload multiple code files at once.
    """
    try:
        results = []
        successful_uploads = 0
        failed_uploads = 0
        
        for file_data in files:
            try:
                result = await add_code_file(
                    user_id=user_id,
                    project_id=project_id,
                    filename=file_data["filename"],
                    file_path=file_data["file_path"],
                    content=file_data["content"],
                    file_type=file_data["file_type"],
                    description=file_data.get("description")
                )
                
                results.append({
                    "filename": file_data["filename"],
                    "status": "success",
                    "file_path": file_data["file_path"],
                    "git_commit_hash": result["git_commit_hash"]
                })
                successful_uploads += 1
                
            except Exception as e:
                results.append({
                    "filename": file_data["filename"],
                    "status": "failed",
                    "error": str(e)
                })
                failed_uploads += 1
        
        return {
            "message": f"Bulk upload completed: {successful_uploads} successful, {failed_uploads} failed",
            "results": results,
            "successful_uploads": successful_uploads,
            "failed_uploads": failed_uploads
        }
        
    except Exception as e:
        print(f"Error in bulk upload: {str(e)}")
        raise Exception(f"Failed to perform bulk upload: {str(e)}")

async def get_code_file_info(user_id: str, project_id: str, file_path: str):
    """
    Get detailed information about a code file.
    """
    try:
        project_path = os.path.join(REPO_ROOT, user_id, project_id)
        full_file_path = os.path.join(project_path, file_path)
        
        # Check if file exists
        if not os.path.exists(full_file_path):
            raise Exception(f"File {file_path} does not exist")
        
        # Get file stats
        stat_info = os.stat(full_file_path)
        
        # Read file content for hash calculation
        with open(full_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Calculate content hash
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # Get Git commit info
        git_log_cmd = f'git log --oneline -1 -- "{file_path}"'
        log_result = await run_command_async(git_log_cmd, cwd=project_path)
        
        git_commit_hash = None
        if log_result.strip():
            git_commit_hash = log_result.strip().split()[0]
        
        # Determine file type
        file_ext = os.path.splitext(file_path)[1].lower()
        file_type = "other"
        
        if file_ext in ['.py']:
            file_type = 'python'
        elif file_ext in ['.ipynb']:
            file_type = 'jupyter'
        elif file_ext in ['.yaml', '.yml', '.json', '.toml', '.ini', '.cfg']:
            file_type = 'config'
        elif file_ext in ['.md', '.txt', '.rst']:
            file_type = 'documentation'
        elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
            file_type = 'javascript'
        elif file_ext in ['.html', '.css', '.scss', '.sass']:
            file_type = 'web'
        elif file_ext in ['.java', '.cpp', '.c', '.h', '.hpp']:
            file_type = 'compiled'
        
        return {
            "filename": os.path.basename(file_path),
            "file_path": file_path,
            "file_type": file_type,
            "size": stat_info.st_size,
            "content_hash": content_hash,
            "git_commit_hash": git_commit_hash,
            "created_at": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "lines": len(content.splitlines())
        }
        
    except Exception as e:
        print(f"Error getting code file info: {str(e)}")
        raise Exception(f"Failed to get code file info: {str(e)}")

async def create_parameter_set(user_id: str, project_id: str, parameter_set: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a parameter set and save it as a YAML file.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        parameter_set (Dict[str, Any]): The parameter set data
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        project_path = os.path.join(REPO_ROOT, user_id, project_id)
        
        # Generate YAML content from parameter set
        yaml_content = generate_params_yaml(parameter_set)
        
        # Save to params.yaml file in project root
        params_file = os.path.join(project_path, "params.yaml")
        with open(params_file, 'w') as f:
            f.write(yaml_content)
        
        # Add to git using safe commit
        git_success = await safe_git_commit(
            project_path, 
            f"Updated parameters: {parameter_set.get('name', 'unnamed')}",
            ["params.yaml"]
        )
        
        # Add to DVC tracking if DVC is initialized
        dvc_tracked = False
        try:
            if await is_dvc_initialized(project_path):
                await run_command_async("dvc add params.yaml", cwd=project_path)
                await safe_git_commit(project_path, "Add params.yaml to DVC tracking", ["params.yaml.dvc"])
                dvc_tracked = True
        except Exception as e:
            print(f"Warning: Could not add params.yaml to DVC tracking: {str(e)}")
        
        return {
            "success": True,
            "message": f"Parameter set '{parameter_set.get('name', 'unnamed')}' created successfully",
            "file_path": params_file,
            "parameter_count": count_parameters(parameter_set),
            "dvc_tracked": dvc_tracked,
            "git_committed": git_success
        }
        
    except Exception as e:
        raise Exception(f"Failed to create parameter set: {str(e)}")

async def update_parameter_set(user_id: str, project_id: str, parameter_set: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing parameter set.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        parameter_set (Dict[str, Any]): The updated parameter set data
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        project_path = os.path.join(REPO_ROOT, user_id, project_id)
        params_file = os.path.join(project_path, "params.yaml")
        
        # Generate updated YAML content
        yaml_content = generate_params_yaml(parameter_set)
        
        # Save updated parameters
        with open(params_file, 'w') as f:
            f.write(yaml_content)
        
        # Add to git using safe commit
        git_success = await safe_git_commit(
            project_path, 
            f"Updated parameters: {parameter_set.get('name', 'unnamed')}",
            ["params.yaml"]
        )
        
        # Update DVC tracking if DVC is initialized
        dvc_tracked = False
        try:
            if await is_dvc_initialized(project_path):
                await run_command_async("dvc add params.yaml", cwd=project_path)
                await safe_git_commit(project_path, "Update params.yaml in DVC tracking", ["params.yaml.dvc"])
                dvc_tracked = True
        except Exception as e:
            print(f"Warning: Could not update params.yaml in DVC tracking: {str(e)}")
        
        return {
            "success": True,
            "message": f"Parameter set '{parameter_set.get('name', 'unnamed')}' updated successfully",
            "file_path": params_file,
            "parameter_count": count_parameters(parameter_set),
            "dvc_tracked": dvc_tracked,
            "git_committed": git_success
        }
        
    except Exception as e:
        raise Exception(f"Failed to update parameter set: {str(e)}")

async def get_parameter_set(user_id: str, project_id: str) -> Dict[str, Any]:
    """
    Get the current parameter set from the project.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        
    Returns:
        Dict[str, Any]: The parameter set data
    """
    try:
        project_path = os.path.join(REPO_ROOT, user_id, project_id)
        params_file = os.path.join(project_path, "params.yaml")
        
        if not os.path.exists(params_file):
            return {
                "success": True,
                "message": "No parameter set found",
                "parameter_set": None,
                "file_path": params_file
            }
        
        # Read and parse YAML file
        with open(params_file, 'r') as f:
            yaml_content = f.read()
        
        # Parse YAML to structured format
        parameter_set = parse_params_yaml(yaml_content)
        
        return {
            "success": True,
            "message": "Parameter set retrieved successfully",
            "parameter_set": parameter_set,
            "file_path": params_file,
            "raw_yaml": yaml_content
        }
        
    except Exception as e:
        raise Exception(f"Failed to get parameter set: {str(e)}")

async def delete_parameter_set(user_id: str, project_id: str) -> Dict[str, Any]:
    """
    Delete the parameter set file.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        project_path = os.path.join(REPO_ROOT, user_id, project_id)
        params_file = os.path.join(project_path, "params.yaml")
        
        if not os.path.exists(params_file):
            return {
                "success": True,
                "message": "No parameter set found to delete",
                "file_path": params_file
            }
        
        # Remove the file
        os.remove(params_file)
        
        # Remove from git using safe commit
        git_success = await safe_git_commit(project_path, "Deleted parameter set", ["params.yaml"])
        
        # Remove from DVC tracking if DVC is initialized
        try:
            if await is_dvc_initialized(project_path):
                if os.path.exists(os.path.join(project_path, "params.yaml.dvc")):
                    await run_command_async("dvc remove params.yaml.dvc", cwd=project_path)
                    await safe_git_commit(project_path, "Remove params.yaml from DVC tracking", ["params.yaml.dvc"])
        except Exception as e:
            print(f"Warning: Could not remove params.yaml from DVC tracking: {str(e)}")
        
        return {
            "success": True,
            "message": "Parameter set deleted successfully",
            "file_path": params_file,
            "git_committed": git_success
        }
        
    except Exception as e:
        raise Exception(f"Failed to delete parameter set: {str(e)}")

async def import_parameters_from_file(user_id: str, project_id: str, file_path: str, format: str = "yaml") -> Dict[str, Any]:
    """
    Import parameters from an external file.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        file_path (str): Path to the file to import from
        format (str): File format (yaml, json, env)
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        project_path = os.path.join(REPO_ROOT, user_id, project_id)
        
        # Read the source file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Parse based on format
        if format.lower() == "yaml":
            parameters = yaml.safe_load(content)
        elif format.lower() == "json":
            parameters = json.loads(content)
        elif format.lower() == "env":
            parameters = parse_env_file(content)
        else:
            raise Exception(f"Unsupported format: {format}")
        
        # Convert to structured format
        parameter_set = convert_to_parameter_set(parameters, f"Imported from {os.path.basename(file_path)}")
        
        # Save the imported parameters
        result = await create_parameter_set(user_id, project_id, parameter_set)
        result["imported_from"] = file_path
        result["import_format"] = format
        
        return result
        
    except Exception as e:
        raise Exception(f"Failed to import parameters: {str(e)}")

async def export_parameters_to_file(user_id: str, project_id: str, format: str = "yaml", include_metadata: bool = True) -> Dict[str, Any]:
    """
    Export parameters to a file in the specified format.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        format (str): Export format (yaml, json, env)
        include_metadata (bool): Whether to include metadata
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        # Get current parameter set
        param_result = await get_parameter_set(user_id, project_id)
        
        if not param_result["parameter_set"]:
            raise Exception("No parameter set found to export")
        
        project_path = os.path.join(REPO_ROOT, user_id, project_id)
        export_dir = os.path.join(project_path, "exports")
        os.makedirs(export_dir, exist_ok=True)
        
        # Convert to export format
        if format.lower() == "yaml":
            export_content = yaml.dump(param_result["parameter_set"], default_flow_style=False, indent=2)
            file_extension = "yaml"
        elif format.lower() == "json":
            export_content = json.dumps(param_result["parameter_set"], indent=2)
            file_extension = "json"
        elif format.lower() == "env":
            export_content = convert_to_env_format(param_result["parameter_set"])
            file_extension = "env"
        else:
            raise Exception(f"Unsupported export format: {format}")
        
        # Save export file
        export_file = os.path.join(export_dir, f"parameters_export.{file_extension}")
        with open(export_file, 'w') as f:
            f.write(export_content)
        
        return {
            "success": True,
            "message": f"Parameters exported successfully to {format.upper()} format",
            "export_file": export_file,
            "format": format,
            "file_size": len(export_content)
        }
        
    except Exception as e:
        raise Exception(f"Failed to export parameters: {str(e)}")

async def validate_parameters(user_id: str, project_id: str, parameter_set: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate parameter values against their validation rules.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        parameter_set (Dict[str, Any]): The parameter set to validate
        
    Returns:
        Dict[str, Any]: Validation results
    """
    try:
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "validated_parameters": 0
        }
        
        # Check if parameter_set is valid
        if parameter_set is None or not isinstance(parameter_set, dict):
            validation_results["valid"] = False
            validation_results["errors"].append("Invalid parameter set: parameter_set is None or not a dictionary")
            return validation_results
        
        # Get groups safely
        groups = parameter_set.get("groups", [])
        if groups is None:
            groups = []
        
        # Validate each parameter group
        for group in groups:
            if group is None or not isinstance(group, dict):
                validation_results["valid"] = False
                validation_results["errors"].append("Invalid group: group is None or not a dictionary")
                continue
                
            parameters = group.get("parameters", [])
            if parameters is None:
                parameters = []
                
            for param in parameters:
                validation_results["validated_parameters"] += 1
                
                # Validate based on type and validation rules
                param_validation = validate_single_parameter(param)
                
                if param_validation["valid"] == False:
                    validation_results["valid"] = False
                    validation_results["errors"].append(param_validation["error"])
                elif param_validation.get("warning"):
                    validation_results["warnings"].append(param_validation["warning"])
        
        return validation_results
        
    except Exception as e:
        raise Exception(f"Failed to validate parameters: {str(e)}")

def generate_params_yaml(parameter_set: Dict[str, Any]) -> str:
    """Generate YAML content from parameter set structure."""
    try:
        yaml_data = {}
        
        for group in parameter_set.get("groups", []):
            group_name = group.get("name", "default")
            yaml_data[group_name] = {}
            
            for param in group.get("parameters", []):
                param_name = param.get("name", "unnamed")
                param_value = param.get("value")
                yaml_data[group_name][param_name] = param_value
        
        return yaml.dump(yaml_data, default_flow_style=False, indent=2)
        
    except Exception as e:
        raise Exception(f"Failed to generate YAML: {str(e)}")

def parse_params_yaml(yaml_content: str) -> Dict[str, Any]:
    """Parse YAML content to parameter set structure."""
    try:
        yaml_data = yaml.safe_load(yaml_content)
        
        parameter_set = {
            "name": "Parsed Parameters",
            "description": "Parameters parsed from YAML file",
            "groups": []
        }
        
        # Handle flat structure with top-level sections
        for section_name, section_data in yaml_data.items():
            if isinstance(section_data, dict):
                # This is a section with nested parameters
                group = {
                    "name": section_name,
                    "description": f"Parameters for {section_name}",
                    "parameters": []
                }
                
                for param_name, param_value in section_data.items():
                    param = {
                        "name": param_name,
                        "value": param_value,
                        "type": get_value_type(param_value),
                        "description": f"Parameter {param_name} in {section_name}",
                        "required": False
                    }
                    group["parameters"].append(param)
                
                parameter_set["groups"].append(group)
            else:
                # This is a top-level parameter (not in a section)
                param = {
                    "name": section_name,
                    "value": section_data,
                    "type": get_value_type(section_data),
                    "description": f"Parameter {section_name}",
                    "required": False
                }
                
                # Add to default group if no groups exist, or create one
                if not parameter_set["groups"]:
                    parameter_set["groups"].append({
                        "name": "default",
                        "description": "Default parameters",
                        "parameters": []
                    })
                
                parameter_set["groups"][0]["parameters"].append(param)
        
        return parameter_set
        
    except Exception as e:
        raise Exception(f"Failed to parse YAML: {str(e)}")

def count_parameters(parameter_set: Dict[str, Any]) -> int:
    """Count the total number of parameters in a parameter set."""
    count = 0
    for group in parameter_set.get("groups", []):
        count += len(group.get("parameters", []))
    return count

def get_value_type(value: Any) -> str:
    """Determine the type of a value."""
    if isinstance(value, bool):
        return "boolean"
    elif isinstance(value, (int, float)):
        return "number"
    elif isinstance(value, list):
        return "array"
    elif isinstance(value, dict):
        return "object"
    else:
        return "string"

def validate_single_parameter(param: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a single parameter against its validation rules."""
    try:
        validation = {"valid": True}
        
        # Check if param is None or not a dictionary
        if param is None or not isinstance(param, dict):
            return {"valid": False, "error": "Invalid parameter: parameter is None or not a dictionary"}
        
        # Check if required parameter has a value
        if param.get("required", False) and param.get("value") is None:
            validation["valid"] = False
            validation["error"] = f"Required parameter '{param.get('name', 'unnamed')}' has no value"
            return validation
        
        # Type validation
        param_type = param.get("type", "string")
        value = param.get("value")
        
        if value is not None:
            if param_type == "number" and not isinstance(value, (int, float)):
                validation["valid"] = False
                validation["error"] = f"Parameter '{param.get('name', 'unnamed')}' must be a number"
            elif param_type == "boolean" and not isinstance(value, bool):
                validation["valid"] = False
                validation["error"] = f"Parameter '{param.get('name', 'unnamed')}' must be a boolean"
        
        # Custom validation rules
        validation_rules = param.get("validation", {})
        
        if validation_rules and isinstance(validation_rules, dict):
            if validation_rules.get("min") is not None and value is not None:
                if isinstance(value, (int, float)) and value < validation_rules["min"]:
                    validation["valid"] = False
                    validation["error"] = f"Parameter '{param.get('name', 'unnamed')}' must be >= {validation_rules['min']}"
            
            if validation_rules.get("max") is not None and value is not None:
                if isinstance(value, (int, float)) and value > validation_rules["max"]:
                    validation["valid"] = False
                    validation["error"] = f"Parameter '{param.get('name', 'unnamed')}' must be <= {validation_rules['max']}"
        
        return validation
        
    except Exception as e:
        return {"valid": False, "error": f"Validation error: {str(e)}"}

def parse_env_file(content: str) -> Dict[str, Any]:
    """Parse environment file content to parameter structure."""
    parameters = {}
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            parameters[key.strip()] = value.strip()
    return parameters

def convert_to_parameter_set(parameters: Dict[str, Any], name: str) -> Dict[str, Any]:
    """Convert flat parameter dictionary to structured parameter set."""
    parameter_set = {
        "name": name,
        "description": f"Parameters converted from {name}",
        "groups": []
    }
    
    # Handle nested parameter structure
    for key, value in parameters.items():
        if isinstance(value, dict):
            # This is a section with nested parameters
            group = {
                "name": key,
                "description": f"Parameters for {key}",
                "parameters": []
            }
            
            for param_name, param_value in value.items():
                param = {
                    "name": param_name,
                    "value": param_value,
                    "type": get_value_type(param_value),
                    "description": f"Parameter {param_name} in {key}",
                    "required": False
                }
                group["parameters"].append(param)
            
            parameter_set["groups"].append(group)
        else:
            # This is a top-level parameter
            param = {
                "name": key,
                "value": value,
                "type": get_value_type(value),
                "description": f"Parameter {key}",
                "required": False
            }
            
            # Add to default group if no groups exist, or create one
            if not parameter_set["groups"]:
                parameter_set["groups"].append({
                    "name": "default",
                    "description": "Default parameters",
                    "parameters": []
                })
            
            parameter_set["groups"][0]["parameters"].append(param)
    
    return parameter_set

def convert_to_env_format(parameter_set: Dict[str, Any]) -> str:
    """Convert parameter set to environment file format."""
    env_content = []
    
    for group in parameter_set.get("groups", []):
        for param in group.get("parameters", []):
            key = param.get("name", "unnamed")
            value = param.get("value", "")
            env_content.append(f"{key}={value}")
    
    return '\n'.join(env_content)

async def import_parameters_from_upload(user_id: str, project_id: str, file_content: str, filename: str, format: str = None) -> Dict[str, Any]:
    """
    Import parameters from an uploaded file content.
    
    Args:
        user_id (str): The user ID
        project_id (str): The project ID
        file_content (str): The content of the uploaded file
        filename (str): The name of the uploaded file
        format (str): File format (yaml, json, env) - auto-detected if None
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    try:
        project_path = os.path.join(REPO_ROOT, user_id, project_id)
        
        # Auto-detect format if not specified
        if format is None:
            format = detect_file_format(filename, file_content)
        
        # Parse based on format
        if format.lower() == "yaml":
            parameters = yaml.safe_load(file_content)
        elif format.lower() == "json":
            parameters = json.loads(file_content)
        elif format.lower() == "env":
            parameters = parse_env_file(file_content)
        else:
            raise Exception(f"Unsupported format: {format}")
        
        # Convert to structured format
        parameter_set = convert_to_parameter_set(parameters, f"Imported from {filename}")
        
        # Validate the imported parameters
        validation_result = await validate_parameters(user_id, project_id, parameter_set)
        
        # Save the imported parameters
        result = await create_parameter_set(user_id, project_id, parameter_set)
        result["imported_from"] = filename
        result["import_format"] = format
        result["validation"] = validation_result
        
        # Save the original file for reference
        import_dir = os.path.join(project_path, "imports")
        os.makedirs(import_dir, exist_ok=True)
        
        import_file = os.path.join(import_dir, f"imported_params_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
        with open(import_file, 'w') as f:
            f.write(file_content)
        
        result["import_file_path"] = import_file
        
        # Generate and save params.yaml in project root for DVC
        params_yaml_content = generate_params_yaml(parameter_set)
        params_yaml_path = os.path.join(project_path, "params.yaml")
        
        with open(params_yaml_path, 'w') as f:
            f.write(params_yaml_content)
        
        result["params_yaml_path"] = params_yaml_path
        result["params_yaml_content"] = params_yaml_content
        
        # Add params.yaml to DVC tracking if DVC is initialized
        try:
            if await is_dvc_initialized(project_path):
                await run_command_async("dvc add params.yaml", cwd=project_path)
                await run_command_async("git add params.yaml.dvc", cwd=project_path)
                await run_command_async(f'git commit -m "Add params.yaml from import: {filename}"', cwd=project_path)
                result["dvc_tracked"] = True
            else:
                result["dvc_tracked"] = False
        except Exception as e:
            print(f"Warning: Could not add params.yaml to DVC tracking: {str(e)}")
            result["dvc_tracked"] = False
        
        return result
        
    except Exception as e:
        raise Exception(f"Failed to import parameters from upload: {str(e)}")

def detect_file_format(filename: str, content: str) -> str:
    """
    Auto-detect the format of a file based on filename and content.
    
    Args:
        filename (str): The filename
        content (str): The file content
        
    Returns:
        str: Detected format (yaml, json, env)
    """
    # Check filename extension first
    if filename.endswith(('.yaml', '.yml')):
        return "yaml"
    elif filename.endswith('.json'):
        return "json"
    elif filename.endswith('.env'):
        return "env"
    
    # Try to detect from content
    content = content.strip()
    
    # Check for JSON
    if content.startswith('{') or content.startswith('['):
        try:
            json.loads(content)
            return "json"
        except:
            pass
    
    # Check for YAML
    if ':' in content and ('{' in content or '\n' in content):
        try:
            yaml.safe_load(content)
            return "yaml"
        except:
            pass
    
    # Check for ENV format
    if '=' in content and '\n' in content:
        lines = content.split('\n')
        env_lines = [line for line in lines if '=' in line and not line.strip().startswith('#')]
        if len(env_lines) > 0:
            return "env"
    
    # Default to YAML
    return "yaml"

async def safe_git_commit(project_path: str, commit_message: str, files_to_add: list = None) -> bool:
    """
    Safely commit changes to Git, handling untracked files.
    
    Args:
        project_path (str): Path to the project directory
        commit_message (str): Commit message
        files_to_add (list): List of specific files to add (if None, adds all)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if there are any changes to commit
        result = await run_command_async("git status --porcelain", cwd=project_path)
        if not result.strip():
            print("No changes to commit")
            return True
        
        # Add files to staging
        if files_to_add:
            for file_path in files_to_add:
                await run_command_async(f"git add {file_path}", cwd=project_path)
        else:
            # Add all changes including untracked files
            await run_command_async("git add .", cwd=project_path)
        
        # Commit the changes
        await run_command_async(f'git commit -m "{commit_message}"', cwd=project_path)
        return True
        
    except Exception as e:
        print(f"Warning: Git commit failed: {str(e)}")
        return False