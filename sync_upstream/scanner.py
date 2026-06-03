import logging
from typing import List, Set, Optional
from .github_api import GitHubAPI
from .models import Repository, RepositoryConfig, AppConfig

logger = logging.getLogger(__name__)


class RepositoryScanner:
    def __init__(self, config: AppConfig, github_api: GitHubAPI):
        self.config = config
        self.github_api = github_api

    def scan(self) -> List[Repository]:
        logger.info("Starting repository scan")
        all_repos = []
        
        if self.config.auto_scan.enabled:
            logger.info("Auto-scan is enabled, scanning user's forks")
            username = self.config.owner
            if not username:
                logger.info("No owner specified, fetching current user")
                user = self.github_api.get_current_user()
                username = user["login"]
                self.config.owner = username
            
            fork_repos = self.github_api.get_user_forks(
                username, 
                include_private=self.config.auto_scan.include_private
            )
            all_repos.extend(fork_repos)

        included_repos = self._get_included_repos()
        logger.debug(f"Found {len(included_repos)} explicitly included repositories")
        for repo_config in included_repos:
            if not any(r.name == repo_config.name for r in all_repos):
                logger.debug(f"Fetching explicitly included repository: {repo_config.name}")
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
                    all_repos.append(repo)

        excluded_names = set(self.config.repositories.get("excluded", []))
        logger.debug(f"Found {len(excluded_names)} excluded repositories")
        filtered_repos = [repo for repo in all_repos if repo.name not in excluded_names]
        
        repos_with_upstream = [repo for repo in filtered_repos if repo.has_upstream]
        
        logger.info(f"Found {len(repos_with_upstream)} repositories to sync")
        return repos_with_upstream

    def _get_included_repos(self) -> List[RepositoryConfig]:
        return self.config.repositories.get("included", [])

    def get_branches_for_repo(self, repo: Repository, repo_config: Optional[RepositoryConfig] = None) -> List[str]:
        if repo_config and repo_config.branches:
            logger.debug(f"Using configured branches for {repo.full_name}: {repo_config.branches}")
            return repo_config.branches
        
        logger.debug(f"Fetching all branches for {repo.full_name}")
        return self.github_api.get_repository_branches(repo.owner, repo.name)
