import os
import yaml
from typing import Optional
from .models import AppConfig, RepositoryConfig


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

        # Parse repositories - must be explicitly specified
        repos_config = config_data.get("repositories", [])
        repositories = []
        for repo_data in repos_config:
            if isinstance(repo_data, str):
                repositories.append(RepositoryConfig(name=repo_data, branches=[]))
            else:
                repositories.append(RepositoryConfig(
                    name=repo_data.get("name"),
                    branches=repo_data.get("branches", [])
                ))

        return AppConfig(
            github_token=github_token,
            owner=config_data.get("owner"),
            repositories=repositories
        )
