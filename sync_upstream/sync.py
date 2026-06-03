import logging
from typing import List, Optional
from .github_api import GitHubAPI
from .git_sync import GitSync
from .models import Repository, RepositoryConfig, SyncConfig

logger = logging.getLogger(__name__)


class Synchronizer:
    def __init__(self, github_api: GitHubAPI, sync_config: SyncConfig):
        self.github_api = github_api
        self.sync_config = sync_config

    def sync_repository(self, repo: Repository, repo_config: Optional[RepositoryConfig] = None) -> bool:
        if not repo.has_upstream:
            logger.warning(f"Skipping {repo.full_name}: no upstream repository")
            return False

        logger.info(f"Syncing {repo.full_name} with upstream {repo.upstream}")

        branches = None
        local_path = None
        if repo_config:
            branches = repo_config.branches if repo_config.branches else None
            local_path = repo_config.local_path

        if not branches:
            logger.debug(f"Fetching all branches for {repo.full_name}")
            branches = self.github_api.get_repository_branches(repo.owner, repo.name)

        success_count = 0
        for branch in branches:
            if self.sync_config.method == "git" and local_path:
                # Use git command sync
                if GitSync.sync_repository(local_path, branch):
                    success_count += 1
            else:
                # Use GitHub API sync (default)
                if self.github_api.sync_branch(repo.owner, repo.name, branch):
                    success_count += 1

        logger.info(f"Synced {success_count}/{len(branches)} branches for {repo.full_name}")
        return success_count > 0

    def sync_repositories(self, repos: List[Repository], repo_configs: Optional[List[RepositoryConfig]] = None) -> dict:
        logger.info(f"Starting sync for {len(repos)} repositories using method: {self.sync_config.method}")
        results = {
            "total": len(repos),
            "success": 0,
            "failed": 0,
            "details": []
        }

        config_map = {}
        if repo_configs:
            for config in repo_configs:
                config_map[config.name] = config

        for repo in repos:
            repo_config = config_map.get(repo.name)
            
            try:
                success = self.sync_repository(repo, repo_config)
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                results["details"].append({
                    "repo": repo.full_name,
                    "success": success
                })
            except Exception as e:
                logger.error(f"Error syncing {repo.full_name}: {e}", exc_info=True)
                results["failed"] += 1
                results["details"].append({
                    "repo": repo.full_name,
                    "success": False,
                    "error": str(e)
                })

        return results
