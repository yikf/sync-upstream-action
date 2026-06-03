import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class GitHubAPI:
    BASE_URL = "https://api.github.com"
    API_VERSION = "2022-11-28"

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": self.API_VERSION,
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

    def sync_branch(self, owner: str, repo: str, branch: str) -> bool:
        """Sync a branch using GitHub's merge-upstream API"""
        logger.info(f"  → Syncing branch: {branch}")
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/merge-upstream"
        data = {"branch": branch}
        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 200:
            logger.info(f"  ✓ Branch {branch} synced successfully")
            return True
        else:
            logger.error(f"  ✗ Failed to sync branch {branch}")
            try:
                error_data = response.json()
                logger.error(f"    Error: {error_data}")
            except ValueError:
                logger.error(f"    Response: {response.text}")
            return False
