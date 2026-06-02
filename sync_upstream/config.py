import os
import yaml
from typing import Optional
from .models import AppConfig, AutoScanConfig, SyncConfig, RepositoryConfig


class ConfigLoader:
    @staticmethod
    def load_from_file(file_path: str) -> AppConfig:
        with open(file_path, "r") as f:
            config_data = yaml.safe_load(f)
        return ConfigLoader._parse_config(config_data)

    @staticmethod
    def load_from_env() -> AppConfig:
        config_data = {}
        
        if os.environ.get("GITHUB_TOKEN"):
            config_data["github_token"] = os.environ["GITHUB_TOKEN"]
        if os.environ.get("OWNER"):
            config_data["owner"] = os.environ["OWNER"]
        if os.environ.get("CONFIG_FILE"):
            return ConfigLoader.load_from_file(os.environ["CONFIG_FILE"])
        
        return ConfigLoader._parse_config(config_data)

    @staticmethod
    def _parse_config(config_data: dict) -> AppConfig:
        github_token = config_data.get("github_token", "")
        if not github_token and os.environ.get("GITHUB_TOKEN"):
            github_token = os.environ["GITHUB_TOKEN"]

        auto_scan_data = config_data.get("auto_scan", {})
        auto_scan = AutoScanConfig(
            enabled=auto_scan_data.get("enabled", True),
            include_private=auto_scan_data.get("include_private", False)
        )

        sync_data = config_data.get("sync", {})
        sync = SyncConfig(
            method=sync_data.get("method", "api"),
            timeout=sync_data.get("timeout", 300)
        )

        repositories = config_data.get("repositories", {"included": [], "excluded": []})
        included_repos = []
        for repo_data in repositories.get("included", []):
            if isinstance(repo_data, str):
                included_repos.append(RepositoryConfig(name=repo_data, branches=[]))
            else:
                included_repos.append(RepositoryConfig(
                    name=repo_data.get("name"),
                    branches=repo_data.get("branches", [])
                ))

        excluded_repos = repositories.get("excluded", [])

        return AppConfig(
            github_token=github_token,
            owner=config_data.get("owner"),
            auto_scan=auto_scan,
            repositories={"included": included_repos, "excluded": excluded_repos},
            sync=sync
        )
