"""Tests for scanner module"""
import pytest
from sync_upstream.scanner import RepositoryScanner
from sync_upstream.models import Repository, RepositoryConfig, AppConfig


def test_scanner_init(mocker):
    """Test RepositoryScanner initialization"""
    mock_config = mocker.Mock(spec=AppConfig)
    mock_github_api = mocker.Mock()
    scanner = RepositoryScanner(mock_config, mock_github_api)
    assert scanner.config is mock_config
    assert scanner.github_api is mock_github_api


def test_scan_auto_scan_enabled(mocker):
    """Test scanning with auto_scan enabled"""
    mock_config = mocker.Mock()
    mock_config.auto_scan.enabled = True
    mock_config.auto_scan.include_private = False
    mock_config.owner = "test-owner"
    mock_config.repositories = {"included": [], "excluded": []}
    
    mock_github_api = mocker.Mock()
    mock_repo = Repository(
        owner="test-owner",
        name="test-repo",
        full_name="test-owner/test-repo",
        is_private=False,
        has_upstream=True,
        upstream="upstream/repo",
        default_branch="main"
    )
    mock_github_api.get_user_forks.return_value = [mock_repo]
    
    scanner = RepositoryScanner(mock_config, mock_github_api)
    repos = scanner.scan()
    
    assert len(repos) == 1
    assert repos[0].name == "test-repo"
    mock_github_api.get_user_forks.assert_called_once_with("test-owner", include_private=False)


def test_scan_get_current_user(mocker):
    """Test scanning when owner is None - should get from API"""
    mock_config = mocker.Mock()
    mock_config.auto_scan.enabled = True
    mock_config.auto_scan.include_private = False
    mock_config.owner = None
    mock_config.repositories = {"included": [], "excluded": []}
    
    mock_github_api = mocker.Mock()
    mock_github_api.get_current_user.return_value = {"login": "api-owner"}
    mock_github_api.get_user_forks.return_value = []
    
    scanner = RepositoryScanner(mock_config, mock_github_api)
    scanner.scan()
    
    mock_github_api.get_current_user.assert_called_once()
    assert mock_config.owner == "api-owner"


def test_scan_with_included_repos(mocker):
    """Test scanning with included repos"""
    mock_config = mocker.Mock()
    mock_config.auto_scan.enabled = False
    mock_config.owner = "test-owner"
    repo_config = RepositoryConfig(name="included-repo", branches=[])
    mock_config.repositories = {"included": [repo_config], "excluded": []}
    
    mock_github_api = mocker.Mock()
    repo_data = {
        "owner": {"login": "test-owner"},
        "name": "included-repo",
        "full_name": "test-owner/included-repo",
        "private": False,
        "default_branch": "main",
        "parent": {"full_name": "upstream/repo"}
    }
    mock_github_api.get_repository.return_value = repo_data
    
    scanner = RepositoryScanner(mock_config, mock_github_api)
    repos = scanner.scan()
    
    assert len(repos) == 1
    assert repos[0].name == "included-repo"


def test_scan_with_excluded_repos(mocker):
    """Test scanning with excluded repos"""
    mock_config = mocker.Mock()
    mock_config.auto_scan.enabled = True
    mock_config.auto_scan.include_private = False
    mock_config.owner = "test-owner"
    mock_config.repositories = {"included": [], "excluded": ["excluded-repo"]}
    
    mock_github_api = mocker.Mock()
    
    # Create one repo that will be excluded and one that will remain
    excluded_repo = Repository(
        owner="test-owner",
        name="excluded-repo",
        full_name="test-owner/excluded-repo",
        is_private=False,
        has_upstream=True,
        upstream="upstream/repo",
        default_branch="main"
    )
    kept_repo = Repository(
        owner="test-owner",
        name="kept-repo",
        full_name="test-owner/kept-repo",
        is_private=False,
        has_upstream=True,
        upstream="upstream/repo2",
        default_branch="main"
    )
    mock_github_api.get_user_forks.return_value = [excluded_repo, kept_repo]
    
    scanner = RepositoryScanner(mock_config, mock_github_api)
    repos = scanner.scan()
    
    assert len(repos) == 1
    assert repos[0].name == "kept-repo"


def test_scan_no_upstream_repos_excluded(mocker):
    """Test that repos without upstream are filtered out"""
    mock_config = mocker.Mock()
    mock_config.auto_scan.enabled = True
    mock_config.auto_scan.include_private = False
    mock_config.owner = "test-owner"
    mock_config.repositories = {"included": [], "excluded": []}
    
    mock_github_api = mocker.Mock()
    
    repo_without_upstream = Repository(
        owner="test-owner",
        name="no-upstream",
        full_name="test-owner/no-upstream",
        is_private=False,
        has_upstream=False,
        default_branch="main"
    )
    repo_with_upstream = Repository(
        owner="test-owner",
        name="with-upstream",
        full_name="test-owner/with-upstream",
        is_private=False,
        has_upstream=True,
        upstream="upstream/repo",
        default_branch="main"
    )
    mock_github_api.get_user_forks.return_value = [repo_without_upstream, repo_with_upstream]
    
    scanner = RepositoryScanner(mock_config, mock_github_api)
    repos = scanner.scan()
    
    assert len(repos) == 1
    assert repos[0].name == "with-upstream"


def test_get_branches_for_repo_config_override(mocker):
    """Test getting branches from repo config override"""
    mock_config = mocker.Mock()
    mock_github_api = mocker.Mock()
    
    scanner = RepositoryScanner(mock_config, mock_github_api)
    
    repo = Repository(owner="owner", name="repo", full_name="owner/repo", 
                     is_private=False, default_branch="main")
    repo_config = RepositoryConfig(name="repo", branches=["custom-branch"])
    
    branches = scanner.get_branches_for_repo(repo, repo_config)
    assert branches == ["custom-branch"]
    mock_github_api.get_repository_branches.assert_not_called()


def test_get_branches_for_repo_no_config(mocker):
    """Test getting branches from API when no config"""
    mock_config = mocker.Mock()
    mock_github_api = mocker.Mock()
    mock_github_api.get_repository_branches.return_value = ["api-branch-1", "api-branch-2"]
    
    scanner = RepositoryScanner(mock_config, mock_github_api)
    
    repo = Repository(owner="owner", name="repo", full_name="owner/repo", 
                     is_private=False, default_branch="main")
    
    branches = scanner.get_branches_for_repo(repo)
    assert branches == ["api-branch-1", "api-branch-2"]
