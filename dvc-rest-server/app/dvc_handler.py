import os
from subprocess import run, CalledProcessError

REPO_ROOT = "/home/marialuiza/Documents/faculdade/9periodo/poc/git_repo"  # Root directory of the Git repository

def run_command(command: str, cwd: str = None):
    """
    Runs a shell command in a specified directory.
    Captures stdout and stderr, and ensures errors are correctly identified.
    """
    result = run(
        command.split(),
        capture_output=True,
        text=True,
        cwd=cwd
    )

    # Log outputs for debugging
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    # Check if the command failed
    if result.returncode != 0:
        raise CalledProcessError(result.returncode, command, stderr)

    return stdout, stderr

def create_project(username: str, project_name: str):
    """
    Creates a new project directory inside the Git root and initializes DVC.
    """
    project_path = os.path.join(REPO_ROOT, username, project_name)
    os.makedirs(project_path, exist_ok=True)

    # Initialize Git if not already initialized
    if not os.path.exists(os.path.join(REPO_ROOT, ".git")):
        run_command("git init", cwd=REPO_ROOT)

    # Add the project directory to Git
    try:
        # Add the full relative path to Git
        relative_project_path = os.path.join(username, project_name)
        run_command(f"git add {relative_project_path}", cwd=REPO_ROOT)

        # Check if there are staged changes
        stdout, stderr = run_command("git diff --cached --name-only", cwd=REPO_ROOT)
        if not stdout.strip():
            raise Exception(f"No changes to commit for {username}/{project_name}")

        # Commit the changes
        run_command(f'git commit -m "Initialized project {username}/{project_name}"', cwd=REPO_ROOT)
    except CalledProcessError as e:
        raise Exception(f"Failed to commit project: {e.stderr or e.stdout}")


    return project_path

def track_data(username: str, project_name:str, files: list):
    """
    Tracks data files and directories using DVC.
    """
    project_path = os.path.join(REPO_ROOT, username, project_name)
    try:
        for file in files:
            run_command(f"dvc add {file}", cwd=project_path)
        run_command("git commit -m 'tracking data'", cwd=project_path)
        
        return "Data tracked successfully."
    except CalledProcessError as e:
        raise Exception(f"Failed to track data: {e.stderr or e.stdout}")
    
def add_stages(username: str, project_name:str, stages: list):
    """
    Adds DVC stages to connect code and data.
    """
    project_path = os.path.join(REPO_ROOT, username, project_name)
    try:
        for stage in stages:
            run_command(stage, cwd=project_path)
        run_command("git commit -m 'added stages'", cwd=project_path)
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

def run_experiment(username, project_name, experiment_name: str, command: str):
    """
    Runs a DVC experiment.
    """
    project_path = os.path.join(REPO_ROOT, username, project_name)
    try:
        run_command(f"dvc exp run -n {experiment_name} {command}", cwd=project_path)
        return f"Experiment {experiment_name} run successfully."
    except CalledProcessError as e:
        raise Exception(f"Failed to run experiment {experiment_name}: {e.stderr or e.stdout}")
    
def define_pipeline(username, project_name):
    """
    Defines a DVC pipeline.
    """
    project_path = os.path.join(REPO_ROOT, username, project_name)
    try:
        run_command(f"git add .gitignore data/.gitignore dvc.yaml", cwd=project_path)
        run_command("git commit -m 'added pipeline'", cwd=project_path)
        return f"Pipeline defined successfully."
    except CalledProcessError as e:
        raise Exception(f"Failed to define pipeline: {e.stderr or e.stdout}")  


def run_pipeline(username, project_name):
    """
    Runs a DVC pipeline.
    """
    project_path = os.path.join(REPO_ROOT, username, project_name, cwd=project_path)
    try:
        run_command(f"run repro", cwd=project_path)
        run_command("git add dvc.lock && git commit -m 'first pipeline repro'", cwd=project_path)
    except CalledProcessError as e:
        raise Exception(f"Failed to run pipeline pipeline: {e.stderr or e.stdout}")

"""
If you have a DVC pipeline, use dvc exp run to both run your code pipeline and 
save experiment results. dvc exp run also enables advanced features like queuing 
many experiments at once. They are saved locally but can be shared so others can
reproduce them.
"""    
def run_experiment(username, project_name, experiment_name: str, command: str):
    """
    Runs a DVC experiment.
    """
    project_path = os.path.join(REPO_ROOT, username, project_name)
    try:
        run_command(f"dvc exp run -n {experiment_name} {command}", cwd=project_path)
        return f"Experiment {experiment_name} run successfully."
    except CalledProcessError as e:
        raise Exception(f"Failed to run experiment {experiment_name}: {e.stderr or e.stdout}")