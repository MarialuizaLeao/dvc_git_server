import os
from subprocess import run, CalledProcessError
import asyncio
from asyncio.subprocess import PIPE
import logging

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
        raise Exception(f"Command '{command}' failed with error: {stderr.decode().strip()}")
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
            except CalledProcessError as e:
                error_msg = e.stderr.decode().strip() if e.stderr else e.stdout.decode().strip() if e.stdout else str(e)
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
        
    except CalledProcessError as e:
        error_msg = e.stderr.decode().strip() if e.stderr else e.stdout.decode().strip() if e.stdout else str(e)
        raise Exception(f"Failed to add stages: {error_msg}")
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
        
    except CalledProcessError as e:
        error_msg = e.stderr.decode().strip() if e.stderr else e.stdout.decode().strip() if e.stdout else str(e)
        raise Exception(f"Failed to add stage '{name}': {error_msg}")
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
    
    await run_command_async("git add dvc.lock && git commit -m 'pipeline repro'", cwd=project_path)

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
    
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    try:
        # Create a dvc.yaml file with the template
        dvc_yaml_content = f"# Pipeline Template: {template_name}\nstages:\n"
        
        for stage in stages:
            stage_name = stage.get('name', 'unnamed_stage')
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
        
        # Write the dvc.yaml file
        dvc_yaml_path = os.path.join(project_path, 'dvc.yaml')
        with open(dvc_yaml_path, 'w') as f:
            f.write(dvc_yaml_content)
        
        # Add to git and commit
        await run_command_async("git add dvc.yaml", cwd=project_path)
        await run_command_async(f'git commit -m "Created pipeline template: {template_name}"', cwd=project_path)
        
        return f"Pipeline template '{template_name}' created successfully with {len(stages)} stages."
        
    except Exception as e:
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
        import yaml
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
        import yaml
        
        # Read current configuration
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
        import yaml
        
        # Read current configuration
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
    except CalledProcessError as e:
        error_msg = e.stderr.decode().strip() if e.stderr else e.stdout.decode().strip() if e.stdout else str(e)
        return {
            "valid": False,
            "message": "Pipeline validation failed",
            "details": error_msg
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
    
    try:
        # Add remote storage
        await run_command_async(f"dvc remote add {name} {url}", cwd=project_path)
        
        # Set as default if specified
        if remote_type == "default":
            await run_command_async(f"dvc remote default {name}", cwd=project_path)
        
        # Commit changes
        await run_command_async("git add .dvc/config", cwd=project_path)
        await run_command_async(f'git commit -m "Added remote storage: {name}"', cwd=project_path)
        
        return f"Remote storage '{name}' added successfully"
        
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