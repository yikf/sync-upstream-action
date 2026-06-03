import logging
from typing import List, Optional
from .github_api import GitHubAPI
from .models import Repository, RepositoryConfig

logger = logging.getLogger(__name__)


class Synchronizer:
    def __init__(self, github_api: GitHubAPI):
        self.github_api = github_api

    def sync_repository(self, repo: Repository, repo_config: Optional[RepositoryConfig] = None) -> bool:
        if not repo.has_upstream:
            logger.warning(f"Skipping {repo.full_name}: no upstream repository")
            return False

        print(f"\n📦 {repo.full_name}")
        print(f"   ↳ Upstream: {repo.upstream}")

        # Determine which branches to sync
        branches = []
        if repo_config and repo_config.branches:
            branches = repo_config.branches
        else:
            # Default: only sync default branch
            branches = [repo.default_branch]

        success_count = 0
        for branch in branches:
            if self.github_api.sync_branch(repo.owner, repo.name, branch):
                success_count += 1

        if success_count > 0:
            logger.info(f"   ✓ Synced {success_count}/{len(branches)} branches")
        else:
            logger.error(f"   ✗ No branches synced")
            
        return success_count > 0

    def sync_repositories(self, repos: List[Repository], repo_configs: Optional[List[RepositoryConfig]] = None) -> dict:
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
                logger.error(f"   ✗ Error syncing {repo.full_name}: {e}")
                results["failed"] += 1
                results["details"].append({
                    "repo": repo.full_name,
                    "success": False,
                    "error": str(e)
                })

        return results
