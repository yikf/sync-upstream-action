"""Tests for models module"""

from sync_upstream.models import AppConfig, Repository, RepositoryConfig


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


def test_app_config():
    """Test AppConfig initialization"""
    app_config = AppConfig(github_token="test-token")
    assert app_config.github_token == "test-token"
    assert app_config.owner is None
    assert app_config.repositories == []


def test_app_config_with_repositories():
    """Test AppConfig with repositories"""
    repo1 = RepositoryConfig(name="repo1", branches=["main"])
    repo2 = RepositoryConfig(name="repo2")
    app_config = AppConfig(
        github_token="test-token", owner="test-owner", repositories=[repo1, repo2]
    )
    assert app_config.github_token == "test-token"
    assert app_config.owner == "test-owner"
    assert len(app_config.repositories) == 2
    assert app_config.repositories[0].name == "repo1"
    assert app_config.repositories[1].name == "repo2"


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
