import argparse
import sys

import requests


class Synchronizer(object):
    """
    Sync a fork branch with the upstream repository via the GitHub API.
    See more details at https://docs.github.com/en/rest/branches/branches?apiVersion=2022-11-28#sync-a-fork-branch-with-the-upstream-repository
    """
    def __init__(self, token, owner, repo, branch):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.branch = branch

    def sync_upstream(self):
        sync_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/merge-upstream"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        data = {
            "branch": f"{self.branch}"
        }
        response = requests.post(sync_url, headers=headers, json=data)
        if response.status_code == 200:
            print("Sync upstream request successful.")
            print(response.json())
        else:
            print(f"Sync upstream request failed, response code: {response.status_code}")
            print(response.text)
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync a fork branch with the upstream repository via the GitHub API.")
    parser.add_argument("--token", help="GitHub personal access token")
    parser.add_argument("--owner", help="Repository owner")
    parser.add_argument("--repo", help="Repository name")
    parser.add_argument("--branch", help="Branch name")
    args = parser.parse_args()
    sync = Synchronizer(args.token, args.owner, args.repo, args.branch)
    sync.sync_upstream()
