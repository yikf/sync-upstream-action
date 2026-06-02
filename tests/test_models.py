"""Tests for models module"""
import pytest
from sync_upstream.models import (
    Repository,
    RepositoryConfig,
    AutoScanConfig,
    SyncConfig,
    AppConfig,
)


def test_repository_config():
    """Test RepositoryConfig initialization"""
    config = RepositoryConfig(name="test-repo", branches=["main", "dev"])
    assert config.name == "test-repo"
    assert config.branches == ["main", "dev"]


def test_repository_config_default_branches():
    """Test RepositoryConfig with default branches"""
    config = RepositoryConfig(name="test-repo")
    assert config.name == "test-repo"
    assert config.branches == []


def test_auto_scan_config():
    """Test AutoScanConfig initialization"""
    config = AutoScanConfig(enabled=True, include_private=True)
    assert config.enabled is True
    assert config.include_private is True


def test_auto_scan_config_defaults():
    """Test AutoScanConfig default values"""
    config = AutoScanConfig()
    assert config.enabled is True
    assert config.include_private is False


def test_sync_config():
    """Test SyncConfig initialization"""
    config = SyncConfig(method="git", timeout=600)
    assert config.method == "git"
    assert config.timeout == 600


def test_sync_config_defaults():
    """Test SyncConfig default values"""
    config = SyncConfig()
    assert config.method == "api"
    assert config.timeout == 300


def test_app_config():
    """Test AppConfig initialization"""
    app_config = AppConfig(github_token="test-token")
    assert app_config.github_token == "test-token"
    assert app_config.owner is None
    assert app_config.auto_scan.enabled is True
    assert app_config.sync.method == "api"


def test_repository_model():
    """Test Repository model initialization"""
    repo = Repository(
        owner="test-owner",
        name="test-repo",
        full_name="test-owner/test-repo",
        is_private=False,
        default_branch="main",
    )
    assert repo.owner == "test-owner"
    assert repo.name == "test-repo"
    assert repo.full_name == "test-owner/test-repo"
    assert repo.is_private is False
    assert repo.has_upstream is False
    assert repo.upstream is None


def test_repository_with_upstream():
    """Test Repository with upstream"""
    repo = Repository(
        owner="test-owner",
        name="test-repo",
        full_name="test-owner/test-repo",
        is_private=False,
        has_upstream=True,
        upstream="upstream-owner/upstream-repo",
        default_branch="main",
    )
    assert repo.has_upstream is True
    assert repo.upstream == "upstream-owner/upstream-repo"
