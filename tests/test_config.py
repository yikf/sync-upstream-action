"""Tests for config module"""
import os
import tempfile
import yaml
import pytest
from sync_upstream.config import ConfigLoader
from sync_upstream.models import AppConfig, RepositoryConfig


def test_config_loader_from_env_token():
    """Test loading config from environment variables with token"""
    os.environ["GITHUB_TOKEN"] = "test-env-token"
    config = ConfigLoader.load_from_env()
    assert config.github_token == "test-env-token"
    del os.environ["GITHUB_TOKEN"]


def test_config_loader_from_env_owner():
    """Test loading config from environment variables with owner"""
    os.environ["GITHUB_TOKEN"] = "test-token"
    os.environ["OWNER"] = "test-owner"
    config = ConfigLoader.load_from_env()
    assert config.owner == "test-owner"
    del os.environ["GITHUB_TOKEN"]
    del os.environ["OWNER"]


def test_config_loader_from_file():
    """Test loading config from YAML file"""
    config_data = {
        "github_token": "file-token",
        "owner": "file-owner",
        "auto_scan": {"enabled": True, "include_private": False},
        "repositories": {
            "included": [{"name": "repo1", "branches": ["main", "dev"]}],
            "excluded": ["repo2", "repo3"]
        }
    }
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = f.name
    
    try:
        config = ConfigLoader.load_from_file(temp_path)
        assert config.github_token == "file-token"
        assert config.owner == "file-owner"
        assert config.auto_scan.enabled is True
        assert len(config.repositories["included"]) == 1
        assert config.repositories["included"][0].name == "repo1"
        assert config.repositories["excluded"] == ["repo2", "repo3"]
    finally:
        os.unlink(temp_path)


def test_config_loader_from_file_string_repos():
    """Test loading config from YAML file with string repo names in included"""
    config_data = {
        "github_token": "file-token",
        "owner": "file-owner",
        "repositories": {
            "included": ["repo1", "repo2"],
            "excluded": []
        }
    }
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        temp_path = f.name
    
    try:
        config = ConfigLoader.load_from_file(temp_path)
        assert len(config.repositories["included"]) == 2
        assert isinstance(config.repositories["included"][0], RepositoryConfig)
        assert config.repositories["included"][0].name == "repo1"
    finally:
        os.unlink(temp_path)


def test_config_parse_empty():
    """Test parsing empty config data"""
    config = ConfigLoader._parse_config({})
    assert config.github_token == ""
    assert config.owner is None


def test_config_token_from_env_fallback():
    """Test that token falls back to env if not in config"""
    os.environ["GITHUB_TOKEN"] = "fallback-token"
    config = ConfigLoader._parse_config({})
    assert config.github_token == "fallback-token"
    del os.environ["GITHUB_TOKEN"]


def test_config_token_from_env_override():
    """Test that config token overrides env var"""
    os.environ["GITHUB_TOKEN"] = "env-token"
    config = ConfigLoader._parse_config({"github_token": "config-token"})
    assert config.github_token == "config-token"
    del os.environ["GITHUB_TOKEN"]
