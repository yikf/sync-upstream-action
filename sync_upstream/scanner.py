import logging
from typing import List, Optional
from .github_api import GitHubAPI
from .models import Repository, RepositoryConfig, AppConfig

logger = logging.getLogger(__name__)


class RepositoryScanner:
    def __init__(self, config: AppConfig, github_api: GitHubAPI):
        self.config = config
        self.github_api = github_api

    def scan(self) -> List[Repository]:
        logger.info("Starting repository scan - only explicitly configured repositories will be synced")
        repos = []
        
        # Ensure owner is set
        if not self.config.owner:
            logger.info("No owner specified, fetching current user")
            user = self.github_api.get_current_user()
            self.config.owner = user["login"]
        
        # Only fetch explicitly configured repositories
        for repo_config in self.config.repositories:
            logger.info(f"Fetching configured repository: {repo_config.name}")
            repo_data = self.github_api.get_repository(self.config.owner, repo_config.name)
            if repo_data:
                repo = Repository(
                    owner=repo_data["owner"]["login"],
                    name=repo_data["name"],
                    full_name=repo_data["full_name"],
                    is_private=repo_data["private"],
                    default_branch=repo_data["default_branch"]
                )
                if "parent" in repo_data:
                    repo.has_upstream = True
                    repo.upstream = repo_data["parent"]["full_name"]
                repos.append(repo)
            else:
                logger.error(f"Repository {self.config.owner}/{repo_config.name} not found")
        
        repos_with_upstream = [repo for repo in repos if repo.has_upstream]
        
        logger.info(f"Found {len(repos_with_upstream)} repositories to sync with upstream")
        return repos_with_upstream
