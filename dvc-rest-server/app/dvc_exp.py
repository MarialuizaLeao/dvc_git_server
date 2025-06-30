import os
from subprocess import run, CalledProcessError
import asyncio
from asyncio.subprocess import PIPE
import logging
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = "/home/marialuiza/Documents/faculdade/9periodo/poc/git_repo"  # Root directory of the Git repository

async def dvc_exp_run(user_id: str, project_id: str,quiet: bool = False,
    verbose: bool = False,
    force: bool = False,
    interactive: bool = False,
    single_item: bool = False,
    pipeline: bool = False,
    recursive: bool = False,
    run_all: bool = False,
    queue: bool = False,
    parallel_jobs: int = None,
    temp: bool = False,
    experiment_name: str = None,
    set_param: list = None,  # List of "[<filename>:]<override_pattern>"
    experiment_rev: str = None,
    cwd_reset: str = None,
    message: str = None,
    downstream: bool = False,
    force_downstream: bool = False,
    pull: bool = False,
    dry: bool = False,
    allow_missing: bool = False,
    keep_running: bool = False,
    ignore_errors: bool = False,
    targets: list = None,
):
    """
    Run a new experiment using `dvc exp run` with all supported flags.

    Args:
        cwd (str): The directory to run the command in.
        quiet (bool, optional): Suppress command output.
        verbose (bool, optional): Provide verbose command output.
        force (bool, optional): Re-run pipeline stages even if their outputs are up-to-date.
        interactive (bool, optional): Ask for confirmation when prompted.
        single_item (bool, optional): Execute a single pipeline stage.
        pipeline (bool, optional): Run the pipeline instead of individual stages.
        recursive (bool, optional): Run all pipelines recursively.
        run_all (bool, optional): Run all queued experiments.
        queue (bool, optional): Queue the experiment without running.
        parallel_jobs (int, optional): Number of parallel jobs to run.
        temp (bool, optional): Run the experiment in a temporary directory.
        experiment_name (str, optional): Name of the experiment.
        set_param (list, optional): List of parameters to override.
        experiment_rev (str, optional): Use this revision as the experiment base.
        cwd_reset (str, optional): Reset working directory for the run.
        message (str, optional): Description of the experiment.
        downstream (bool, optional): Reproduce stages downstream of the target.
        force_downstream (bool, optional): Force downstream stage execution even if outputs are up-to-date.
        pull (bool, optional): Pull missing cache before reproducing stages.
        dry (bool, optional): Only display the steps without executing them.
        allow_missing (bool, optional): Allow missing dependencies.
        keep_running (bool, optional): Keep running if there are errors.
        ignore_errors (bool, optional): Ignore errors during stage execution.
        targets (list, optional): List of targets to reproduce.

    Returns:
        str: The output of the `dvc exp run` command.

    Raises:
        Exception: If the `dvc exp run` command fails.
    """
    
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    
    # Validate project path exists
    if not os.path.exists(project_path):
        raise Exception(f"Project path does not exist: {project_path}")
    
    # Check if this is a DVC project
    dvc_yaml_path = os.path.join(project_path, "dvc.yaml")
    dvc_dir = os.path.join(project_path, ".dvc")
    if not os.path.exists(dvc_yaml_path):
        raise Exception(f"Not a DVC project: {dvc_yaml_path} not found")
    if not os.path.exists(dvc_dir):
        raise Exception(f"DVC not initialized: {dvc_dir} not found")
    
    command = "dvc exp run"

    if quiet:
        command += " -q"
    if verbose:
        command += " -v"
    if force:
        command += " -f"
    if interactive:
        command += " -i"
    if single_item:
        command += " -s"
    if pipeline:
        command += " -p"
    if recursive:
        command += " -R"
    if run_all:
        command += " --run-all"
    if queue:
        command += " --queue"
    if parallel_jobs:
        command += f" -j {parallel_jobs}"
    if temp:
        command += " --temp"
    if experiment_name:
        command += f" -n {experiment_name}"
    if set_param:
        # Handle both list and dict formats
        if isinstance(set_param, dict):
            # Convert nested dict to list of "section.param=value" strings
            param_list = []
            for section, section_params in set_param.items():
                if isinstance(section_params, dict):
                    for param_name, param_value in section_params.items():
                        param_list.append(f"{section}.{param_name}={param_value}")
                else:
                    # Handle flat parameters (not in a section)
                    param_list.append(f"{section}={section_params}")
            logger.info(f"Converting nested parameter dict to list: {set_param} -> {param_list}")
        elif isinstance(set_param, list):
            param_list = set_param
            logger.info(f"Using parameter list as-is: {param_list}")
        else:
            param_list = []
            logger.warning(f"Unexpected set_param format: {type(set_param)}")
        
        if param_list:
            # Force temp mode when parameters are provided to avoid modifying workspace
            if not temp:
                command += " --temp"
                logger.info("Added --temp flag to prevent workspace modification")
            command += " " + " ".join(f"-S {param}" for param in param_list)
            logger.info(f"Added parameters to command: {param_list}")
            logger.info(f"Final command: {command}")
    if experiment_rev:
        command += f" -r {experiment_rev}"
    if cwd_reset:
        command += f" -C {cwd_reset}"
    if message:
        command += f" -m {message}"
    if downstream:
        command += " --downstream"
    if force_downstream:
        command += " --force-downstream"
    if pull:
        command += " --pull"
    if dry:
        command += " --dry"
    if allow_missing:
        command += " --allow-missing"
    if keep_running:
        command += " -k"
    if ignore_errors:
        command += " --ignore-errors"
    
    # Add targets at the end as positional arguments
    if targets:
        command += " " + " ".join(targets)
    # If no targets specified, don't add any - DVC will run the default pipeline

    # Log the final command for debugging
    logger.info(f"Executing DVC command: {command}")

    try:
        # Use full path to DVC and set proper environment
        import subprocess
        env = os.environ.copy()
        env['PATH'] = f"{os.path.expanduser('~/.local/bin')}:{env.get('PATH', '')}"
        
        process = await asyncio.create_subprocess_shell(
            command, 
            cwd=project_path, 
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        stdout, stderr = await process.communicate()

        # Log the output for debugging
        if stdout:
            logger.info(f"DVC stdout: {stdout.decode().strip()}")
        if stderr:
            logger.warning(f"DVC stderr: {stderr.decode().strip()}")

        if process.returncode != 0:
            error_msg = stderr.decode().strip() if stderr else "Unknown error"
            logger.error(f"DVC command failed with return code {process.returncode}: {error_msg}")
            raise Exception(f"`dvc exp run` failed: {error_msg}")

        return stdout.decode().strip()
    except Exception as e:
        logger.error(f"Exception during DVC command execution: {str(e)}")
        raise

async def dvc_exp_show(user_id: str, project_id: str,     quiet: bool = False,
    verbose: bool = False,
    all: bool = False,
    include_working_tree: bool = False,
    all_commits: bool = False,
    rev: str = None,
    num: int = None,
    no_pager: bool = False,
    drop: str = None,
    keep: str = None,
    param_deps: bool = False,
    sort_by: str = None,
    sort_order: str = None,  # Should be 'asc' or 'desc'
    sha: bool = False,
    output_format: str = None,  # 'json', 'csv', 'md'
    precision: int = None,
    only_changed: bool = False,
    force: bool = False,
):
    """
    Show the results of experiments using `dvc exp show` with all supported flags.

    Args:
        cwd (str): The directory to run the command in.
        quiet (bool, optional): Suppress command output.
        verbose (bool, optional): Provide verbose command output.
        all (bool, optional): Show all columns in the output.
        include_working_tree (bool, optional): Include the workspace changes in the output.
        all_commits (bool, optional): Include experiments from all commits.
        rev (str, optional): Include experiments from the specified revision or commit.
        num (int, optional): Limit the number of commits to include.
        no_pager (bool, optional): Prevent paginated output.
        drop (str, optional): Drop columns matching the specified regex.
        keep (str, optional): Keep columns matching the specified regex.
        param_deps (bool, optional): Show only parameters directly referenced by stage dependencies.
        sort_by (str, optional): Sort the rows by the specified metric or parameter.
        sort_order (str, optional): Specify sort order ('asc' or 'desc').
        sha (bool, optional): Show only commit hashes.
        output_format (str, optional): Output format ('json', 'csv', 'md').
        precision (int, optional): Specify floating-point precision.
        only_changed (bool, optional): Show only experiments with changed metrics/parameters.
        force (bool, optional): Force experiment table formatting.
    
    Returns:
        str: The output of the `dvc exp show` command.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    command = "dvc exp show"

    if quiet:
        command += " -q"
    if verbose:
        command += " -v"
    if all:
        command += " -a"
    if include_working_tree:
        command += " -T"
    if all_commits:
        command += " -A"
    if rev:
        command += f" --rev {rev}"
    if num:
        command += f" -n {num}"
    if no_pager:
        command += " --no-pager"
    if drop:
        command += f" --drop {drop}"
    if keep:
        command += f" --keep {keep}"
    if param_deps:
        command += " --param-deps"
    if sort_by:
        command += f" --sort-by {sort_by}"
    if sort_order:
        command += f" --sort-order {sort_order}"
    if sha:
        command += " --sha"
    if output_format:
        command += f" --{output_format}"
    if precision is not None:
        command += f" --precision {precision}"
    if only_changed:
        command += " --only-changed"
    if force:
        command += " -f"

    logger.info(f"Executing DVC exp show command: {command}")

    # Use full path to DVC and set proper environment
    env = os.environ.copy()
    env['PATH'] = f"{os.path.expanduser('~/.local/bin')}:{env.get('PATH', '')}"

    process = await asyncio.create_subprocess_shell(
        command, cwd=project_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode().strip() if stderr else "Unknown error"
        logger.error(f"DVC exp show failed with return code {process.returncode}: {error_msg}")
        raise Exception(f"`dvc exp show` failed: {error_msg}")

    result = stdout.decode().strip()
    logger.info(f"DVC exp show output length: {len(result)}")
    logger.info(f"DVC exp show output preview: {result[:200]}...")
    
    return result

async def dvc_exp_list(user_id: str, project_id: str, git_remote: str = None):
    """
    List experiments in the repository using `dvc exp list`.

    Args:
        cwd (str): The directory to run the command in.
        git_remote (str, optional): The Git remote to list experiments from.

    Returns:
        str: The output of the `dvc exp list` command.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    command = "dvc exp list"
    if git_remote:
        command += f" {git_remote}"

    # Use full path to DVC and set proper environment
    env = os.environ.copy()
    env['PATH'] = f"{os.path.expanduser('~/.local/bin')}:{env.get('PATH', '')}"

    process = await asyncio.create_subprocess_shell(
        command, cwd=project_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env=env
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"`dvc exp list` failed: {stderr.decode().strip()}")

    return stdout.decode().strip()

async def dvc_exp_apply(user_id: str, project_id: str, experiment_id: str):
    """
    Apply an experiment's results using `dvc exp apply`.

    Args:
        cwd (str): The directory to run the command in.
        experiment_id (str): The ID of the experiment to apply.

    Returns:
        str: The output of the `dvc exp apply` command.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    command = f"dvc exp apply {experiment_id}"

    process = await asyncio.create_subprocess_shell(
        command, cwd=project_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"`dvc exp apply` failed: {stderr.decode().strip()}")

    return stdout.decode().strip()

async def dvc_exp_remove(user_id: str, project_id: str, experiment_ids: list, queue: bool = False):
    """
    Remove experiments using `dvc exp remove`.

    Args:
        cwd (str): The directory to run the command in.
        experiment_ids (list): List of experiment IDs to remove.
        queue (bool, optional): Remove queued experiments.

    Returns:
        str: The output of the `dvc exp remove` command.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    command = "dvc exp remove"
    if queue:
        command += " --queue"
    if experiment_ids:
        command += f" {' '.join(experiment_ids)}"

    process = await asyncio.create_subprocess_shell(
        command, cwd=project_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"`dvc exp remove` failed: {stderr.decode().strip()}")

    return stdout.decode().strip()

async def dvc_exp_pull(user_id: str, project_id: str, git_remote: str, experiment_id: str):
    """
    Pull an experiment from a Git remote using `dvc exp pull`.

    Args:
        cwd (str): The directory to run the command in.
        git_remote (str): The Git remote to pull from.
        experiment_id (str): The ID of the experiment to pull.

    Returns:
        str: The output of the `dvc exp pull` command.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    command = f"dvc exp pull {git_remote} {experiment_id}"

    process = await asyncio.create_subprocess_shell(
        command, cwd=project_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"`dvc exp pull` failed: {stderr.decode().strip()}")

    return stdout.decode().strip()

async def dvc_exp_push(user_id: str, project_id: str, git_remote: str, experiment_id: str):
    """
    Push a local experiment to a Git remote using `dvc exp push`.

    Args:
        cwd (str): The directory to run the command in.
        git_remote (str): The Git remote to push to.
        experiment_id (str): The ID of the experiment to push.

    Returns:
        str: The output of the `dvc exp push` command.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    command = f"dvc exp push {git_remote} {experiment_id}"

    process = await asyncio.create_subprocess_shell(
        command, cwd=project_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"`dvc exp push` failed: {stderr.decode().strip()}")

    return stdout.decode().strip()

async def dvc_exp_save(user_id: str, project_id: str, name: str = None, force: bool = False):
    """
    Save the current workspace as an experiment using `dvc exp save`.

    Args:
        cwd (str): The directory to run the command in.
        name (str, optional): The name to give to the saved experiment.
        force (bool, optional): Force overwrite if the experiment already exists.

    Returns:
        str: The output of the `dvc exp save` command.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    command = "dvc exp save"
    if name:
        command += f" --name {name}"
    if force:
        command += " --force"

    process = await asyncio.create_subprocess_shell(
        command, cwd=project_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"`dvc exp save` failed: {stderr.decode().strip()}")

    return stdout.decode().strip()

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
    Show differences in plots between two revisions using `dvc plots diff`.

    Args:
        cwd (str): The directory to run the command in.
        targets (list, optional): List of plot files to include.
        a_rev (str, optional): The starting revision.
        b_rev (str, optional): The ending revision.
        templates_dir (str, optional): Directory containing custom templates.
        json (bool, optional): Output in JSON format.
        html (bool, optional): Generate an HTML file and return its path.
        no_html (bool, optional): Skip generating an HTML file.
        out (str, optional): Directory or file path for saving plots.

    Returns:
        str: The output of the `dvc plots diff` command.

    Raises:
        Exception: If the `dvc plots diff` command fails.
    """
    project_path = os.path.join(REPO_ROOT, user_id, project_id)
    command = "dvc plots diff"
    if targets:
        command += " " + " ".join(targets)
    if a_rev:
        command += f" {a_rev}"
    if b_rev:
        command += f" {b_rev}"
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

    process = await asyncio.create_subprocess_shell(
        command, cwd=project_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"`dvc plots diff` failed: {stderr.decode().strip()}")

    return stdout.decode().strip()