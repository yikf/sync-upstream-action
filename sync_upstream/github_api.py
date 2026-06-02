import requests
from typing import List, Optional, Dict, Any
from .models import Repository


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
        repos = []
        page = 1
        per_page = 100

        while True:
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

            page += 1

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
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/merge-upstream"
        data = {"branch": branch}
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            print(f"Successfully synced {owner}/{repo} branch {branch}")
            return True
        else:
            print(f"Failed to sync {owner}/{repo} branch {branch}: {response.status_code}")
            print(response.text)
            return False

    def get_repository(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None
