import requests
import logging
from typing import List, Optional, Dict, Any
from .models import Repository

logger = logging.getLogger(__name__)


class GitHubAPI:
    BASE_URL = "https://api.github.com"
    API_VERSION = "2022-11-28"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": self.API_VERSION
        }

    def get_current_user(self) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/user"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_repository(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def get_repository_branches(self, owner: str, repo: str) -> List[str]:
        branches = []
        page = 1
        per_page = 100

        while True:
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/branches"
            params = {"per_page": per_page, "page": page}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            page_branches = response.json()

            if not page_branches:
                break

            for branch in page_branches:
                branches.append(branch["name"])

            page += 1

        return branches

    def get_branch_sha(self, owner: str, repo: str, branch: str) -> Optional[str]:
        """Get the SHA of a branch in a repository"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/branches/{branch}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()["commit"]["sha"]
        else:
            logger.error(f"Failed to get branch {branch} for {owner}/{repo}: {response.status_code}")
            logger.error(f"Response: {response.text}")
        return None

    def update_branch(self, owner: str, repo: str, branch: str, sha: str, force: bool = True) -> bool:
        """Update a branch to point to a specific SHA"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/git/refs/heads/{branch}"
        data = {
            "sha": sha,
            "force": force
        }
        response = requests.patch(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            logger.info(f"Successfully updated {owner}/{repo} branch {branch} to {sha}")
            return True
        else:
            logger.error(f"Failed to update {owner}/{repo} branch {branch}: {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"Error message: {error_data}")
            except:
                logger.error(f"Error response: {response.text}")
            return False

    def sync_branch(self, owner: str, repo: str, branch: str) -> bool:
        """Sync a branch by getting upstream's SHA and updating our branch to match (no merge commit)"""
        logger.info(f"Syncing branch {branch} for {owner}/{repo}")
        
        # Get repository info to find upstream
        repo_data = self.get_repository(owner, repo)
        if not repo_data or "parent" not in repo_data:
            logger.error(f"Repository {owner}/{repo} is not a fork or has no upstream")
            return False
        
        upstream_owner = repo_data["parent"]["owner"]["login"]
        upstream_repo = repo_data["parent"]["name"]
        
        # Get upstream branch SHA
        upstream_sha = self.get_branch_sha(upstream_owner, upstream_repo, branch)
        if not upstream_sha:
            logger.error(f"Failed to get SHA for upstream branch {upstream_owner}/{upstream_repo}/{branch}")
            return False
        
        # Update our branch to upstream's SHA
        return self.update_branch(owner, repo, branch, upstream_sha)
