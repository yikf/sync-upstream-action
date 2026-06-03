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

    def get_user_forks(self, username: str, include_private: bool = False) -> List[Repository]:
        logger.info(f"Fetching user forks for {username} (include_private={include_private})")
        repos = []
        page = 1
        per_page = 100

        while True:
            logger.debug(f"Fetching page {page} of user forks")
            url = f"{self.BASE_URL}/users/{username}/repos"
            params = {"per_page": per_page, "page": page, "type": "owner"}
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            page_repos = response.json()

            if not page_repos:
                break

            for repo_data in page_repos:
                if repo_data.get("fork"):
                    if not include_private and repo_data.get("private"):
                        continue
                    # Need to fetch full repo info to get parent/source
                    full_repo_data = self.get_repository(repo_data["owner"]["login"], repo_data["name"])
                    if full_repo_data:
                        repo = Repository(
                            owner=full_repo_data["owner"]["login"],
                            name=full_repo_data["name"],
                            full_name=full_repo_data["full_name"],
                            is_private=full_repo_data["private"],
                            default_branch=full_repo_data["default_branch"]
                        )
                        if "parent" in full_repo_data:
                            repo.has_upstream = True
                            repo.upstream = full_repo_data["parent"]["full_name"]
                        repos.append(repo)

            page += 1

        logger.info(f"Found {len(repos)} user forks")
        return repos

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

    def sync_branch(self, owner: str, repo: str, branch: str) -> bool:
        logger.debug(f"Syncing branch {branch} for {owner}/{repo}")
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/merge-upstream"
        data = {"branch": branch}
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            logger.info(f"Successfully synced {owner}/{repo} branch {branch}")
            return True
        else:
            logger.error(f"Failed to sync {owner}/{repo} branch {branch}: {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"Error message: {error_data}")
            except:
                logger.error(f"Error response: {response.text}")
            return False

    def get_repository(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None
