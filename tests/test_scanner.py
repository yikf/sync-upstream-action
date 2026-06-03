"""Tests for scanner module"""

from sync_upstream.models import AppConfig, RepositoryConfig
from sync_upstream.scanner import RepositoryScanner


def test_scanner_init(mocker):
    """Test RepositoryScanner initialization"""
    mock_config = mocker.Mock(spec=AppConfig)
    mock_github_api = mocker.Mock()
    scanner = RepositoryScanner(mock_config, mock_github_api)
    assert scanner.config is mock_config
    assert scanner.github_api is mock_github_api


def test_scan_get_current_user(mocker):
    """Test scanning when owner is None - should get from API"""
    mock_config = AppConfig(github_token="test", repositories=[])
    mock_config.owner = None

    mock_github_api = mocker.Mock()
    mock_github_api.get_current_user.return_value = {"login": "api-owner"}

    scanner = RepositoryScanner(mock_config, mock_github_api)
    scanner.scan()

    mock_github_api.get_current_user.assert_called_once()
    assert mock_config.owner == "api-owner"


def test_scan_with_configured_repos(mocker):
    """Test scanning with configured repos"""
    repo_config = RepositoryConfig(name="included-repo", branches=[])
    mock_config = AppConfig(github_token="test", owner="test-owner", repositories=[repo_config])

    mock_github_api = mocker.Mock()
    repo_data = {
        "owner": {"login": "test-owner"},
        "name": "included-repo",
        "full_name": "test-owner/included-repo",
        "private": False,
        "default_branch": "main",
        "parent": {"full_name": "upstream/repo"},
    }
    mock_github_api.get_repository.return_value = repo_data

    scanner = RepositoryScanner(mock_config, mock_github_api)
    repos = scanner.scan()

    assert len(repos) == 1
    assert repos[0].name == "included-repo"


def test_scan_no_upstream_repos_excluded(mocker):
    """Test that repos without upstream are filtered out"""
    repo_config1 = RepositoryConfig(name="no-upstream", branches=[])
    repo_config2 = RepositoryConfig(name="with-upstream", branches=[])
    mock_config = AppConfig(
        github_token="test", owner="test-owner", repositories=[repo_config1, repo_config2]
    )

    mock_github_api = mocker.Mock()

    repo_data_without_upstream = {
        "owner": {"login": "test-owner"},
        "name": "no-upstream",
        "full_name": "test-owner/no-upstream",
        "private": False,
        "default_branch": "main",
        # No parent (no upstream)
    }

    repo_data_with_upstream = {
        "owner": {"login": "test-owner"},
        "name": "with-upstream",
        "full_name": "test-owner/with-upstream",
        "private": False,
        "default_branch": "main",
        "parent": {"full_name": "upstream/repo"},
    }

    mock_github_api.get_repository.side_effect = [
        repo_data_without_upstream,
        repo_data_with_upstream,
    ]

    scanner = RepositoryScanner(mock_config, mock_github_api)
    repos = scanner.scan()

    assert len(repos) == 1
    assert repos[0].name == "with-upstream"


def test_scan_repo_not_found(mocker):
    """Test that non-existent repos are handled gracefully"""
    repo_config = RepositoryConfig(name="missing-repo", branches=[])
    mock_config = AppConfig(github_token="test", owner="test-owner", repositories=[repo_config])

    mock_github_api = mocker.Mock()
    mock_github_api.get_repository.return_value = None

    scanner = RepositoryScanner(mock_config, mock_github_api)
    repos = scanner.scan()

    assert len(repos) == 0
