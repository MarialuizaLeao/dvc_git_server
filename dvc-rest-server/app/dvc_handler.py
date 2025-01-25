import os
from subprocess import run, CalledProcessError
import asyncio
from asyncio.subprocess import PIPE
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = "/home/marialuiza/Documents/faculdade/9periodo/poc/git_repo"  # Root directory of the Git repository

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
    await run_command_async("dvc init --subdir", cwd=project_path)
    
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
            await init_git(project_path)
        if not await is_dvc_initialized(project_path):
            await init_dvc(project_path)
    else:
        os.makedirs(project_path, exist_ok=True)
        await init_dvc(project_path)

    # Add the project directory to Git
    try:
        user_root = os.path.join(REPO_ROOT, user_id)

        # Add the project to Git
        await run_command_async(f"git add .", cwd=user_root)

        # Check for staged changes
        stdout = await run_command_async("git diff --cached --name-only", cwd=user_root)
        if not stdout.strip():
            raise Exception(f"No changes to commit for {user_id}/{project_id}")

        # Commit changes
        await run_command_async(f'git commit -m "Initialized project {project_id}"', cwd=user_root)

        # Push changes to the remote repository
        await run_command_async("git push", cwd=user_root)

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
    Adds DVC stages to connect code and data.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    try:
        for stage in stages:
            await run_command_async(stage, cwd=project_path)
        await run_command_async("git commit -m 'added stages'", cwd=project_path)
        return "Stages added successfully."
    except CalledProcessError as e:
        raise Exception(f"Failed to add stages: {e.stderr or e.stdout}")
    
def clean_git_repo(repo_path: str):
    """
    Cleans the Git repository by stashing or discarding uncommitted changes.
    """
    try:
        run(["git", "reset", "--hard"], cwd=repo_path, check=True)
        run(["git", "clean", "-fd"], cwd=repo_path, check=True)
    except CalledProcessError as e:
        raise Exception(f"Failed to clean Git repository: {e}")

async def run_experiment(user_id, project_id, experiment_name: str, command: str):
    """
    Runs a DVC experiment.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    try:
        await run_command_async(f"dvc exp run -n {experiment_name} {command}", cwd=project_path)
        return f"Experiment {experiment_name} run successfully."
    except Exception as e:
        raise Exception(f"Failed to run experiment {experiment_name}: {str(e)}")
    
async def define_pipeline(user_id, project_id):
    """
    Defines a DVC pipeline.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    try:
        await run_command_async(f"git add .gitignore data/.gitignore dvc.yaml", cwd=project_path)
        await run_command_async("git commit -m 'added pipeline'", cwd=project_path)
        return f"Pipeline defined successfully."
    except CalledProcessError as e:
        raise Exception(f"Failed to define pipeline: {e.stderr or e.stdout}")  

async def run_pipeline(user_id, project_id):
    """
    Runs a DVC pipeline.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    try:
        await run_command_async(f"run repro", cwd=project_path)
        await run_command_async("git add dvc.lock && git commit -m 'first pipeline repro'", cwd=project_path)
    except CalledProcessError as e:
        raise Exception(f"Failed to run pipeline pipeline: {e.stderr or e.stdout}")