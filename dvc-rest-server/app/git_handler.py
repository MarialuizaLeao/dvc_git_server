from github import Github

GITHUB_TOKEN = "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"  # Replace with your GitHub token
github_client = Github(GITHUB_TOKEN)

def create_or_get_repo(repo_name: str):
    """
    Creates or gets a repository from GitHub.
    """
    user = github_client.get_user()
    print(f"Creating or getting repository {repo_name}...")
    try:
        # Attempt to get the repository
        repo = user.get_repo(repo_name)
    except Exception:
        # If the repo does not exist, create it
        repo = user.create_repo(repo_name, private=True)
    return repo.ssh_url
