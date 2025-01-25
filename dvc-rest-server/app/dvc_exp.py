import os
from subprocess import run, CalledProcessError
import asyncio
from asyncio.subprocess import PIPE
import logging

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
        command += " " + " ".join(f"-S {param}" for param in set_param)
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
    if targets:
        command += " " + " ".join(targets)

    process = await asyncio.create_subprocess_shell(
        command, cwd=project_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"`dvc exp run` failed: {stderr.decode().strip()}")

    return stdout.decode().strip()

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

    process = await asyncio.create_subprocess_shell(
        command, cwd=project_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"`dvc exp show` failed: {stderr.decode().strip()}")

    return stdout.decode().strip()

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

    process = await asyncio.create_subprocess_shell(
        command, cwd=project_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
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
