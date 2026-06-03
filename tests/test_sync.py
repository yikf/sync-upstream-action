"""Tests for sync module"""

from sync_upstream.models import Repository, RepositoryConfig
from sync_upstream.sync import Synchronizer


def test_synchronizer_init(mocker):
    """Test Synchronizer initialization"""
    mock_github_api = mocker.Mock()
    sync = Synchronizer(mock_github_api)
    assert sync.github_api is mock_github_api


def test_sync_repository_no_upstream(mocker):
    """Test syncing a repository with no upstream"""
    mock_github_api = mocker.Mock()
    sync = Synchronizer(mock_github_api)

    repo = Repository(
        owner="owner",
        name="repo",
        full_name="owner/repo",
        is_private=False,
        has_upstream=False,
    )

    result = sync.sync_repository(repo)
    assert result is False
    mock_github_api.sync_branch.assert_not_called()


def test_sync_repository_success_default_branch(mocker):
    """Test successful repository sync with default branch only"""
    mock_github_api = mocker.Mock()
    mock_github_api.sync_branch.return_value = True

    sync = Synchronizer(mock_github_api)

    repo = Repository(
        owner="owner",
        name="repo",
        full_name="owner/repo",
        is_private=False,
        has_upstream=True,
        upstream="upstream/repo",
        default_branch="main",
    )

    result = sync.sync_repository(repo)
    assert result is True
    mock_github_api.sync_branch.assert_called_once_with("owner", "repo", "main")


def test_sync_repository_with_specified_branches(mocker):
    """Test syncing repository with specified branches via config"""
    mock_github_api = mocker.Mock()
    mock_github_api.sync_branch.return_value = True

    sync = Synchronizer(mock_github_api)

    repo = Repository(
        owner="owner",
        name="repo",
        full_name="owner/repo",
        is_private=False,
        has_upstream=True,
        upstream="upstream/repo",
        default_branch="main",
    )

    repo_config = RepositoryConfig(name="repo", branches=["main", "dev"])

    result = sync.sync_repository(repo, repo_config)
    assert result is True
    assert mock_github_api.sync_branch.call_count == 2
    mock_github_api.sync_branch.assert_any_call("owner", "repo", "main")
    mock_github_api.sync_branch.assert_any_call("owner", "repo", "dev")


def test_sync_repositories_empty(mocker):
    """Test syncing empty repository list"""
    mock_github_api = mocker.Mock()
    sync = Synchronizer(mock_github_api)

    results = sync.sync_repositories([])
    assert results["total"] == 0
    assert results["success"] == 0
    assert results["failed"] == 0


def test_sync_repositories_multiple(mocker):
    """Test syncing multiple repositories"""
    mock_github_api = mocker.Mock()
    mock_github_api.sync_branch.side_effect = [True, False]

    sync = Synchronizer(mock_github_api)

    repos = [
        Repository(
            owner="owner",
            name="repo1",
            full_name="owner/repo1",
            is_private=False,
            has_upstream=True,
            upstream="upstream/repo1",
            default_branch="main",
        ),
        Repository(
            owner="owner",
            name="repo2",
            full_name="owner/repo2",
            is_private=False,
            has_upstream=True,
            upstream="upstream/repo2",
            default_branch="main",
        ),
    ]

    results = sync.sync_repositories(repos)
    assert results["total"] == 2
    assert results["success"] == 1
    assert results["failed"] == 1
    assert len(results["details"]) == 2


def test_sync_repositories_with_configs(mocker):
    """Test syncing multiple repositories with configs"""
    mock_github_api = mocker.Mock()
    mock_github_api.sync_branch.side_effect = [True, True, True]

    sync = Synchronizer(mock_github_api)

    repos = [
        Repository(
            owner="owner",
            name="repo1",
            full_name="owner/repo1",
            is_private=False,
            has_upstream=True,
            upstream="upstream/repo1",
            default_branch="main",
        ),
        Repository(
            owner="owner",
            name="repo2",
            full_name="owner/repo2",
            is_private=False,
            has_upstream=True,
            upstream="upstream/repo2",
            default_branch="main",
        ),
    ]

    repo_configs = [
        RepositoryConfig(name="repo1", branches=["main", "dev"]),
        RepositoryConfig(name="repo2", branches=["main"]),
    ]

    results = sync.sync_repositories(repos, repo_configs)
    assert results["total"] == 2
    assert results["success"] == 2
    assert results["failed"] == 0
    assert mock_github_api.sync_branch.call_count == 3  # 2 + 1


def test_sync_repositories_exception(mocker):
    """Test syncing with exception"""
    mock_github_api = mocker.Mock()
    mock_github_api.sync_branch.side_effect = Exception("API Error")

    sync = Synchronizer(mock_github_api)

    repo = Repository(
        owner="owner",
        name="repo",
        full_name="owner/repo",
        is_private=False,
        has_upstream=True,
        upstream="upstream/repo",
        default_branch="main",
    )

    results = sync.sync_repositories([repo])
    assert results["total"] == 1
    assert results["success"] == 0
    assert results["failed"] == 1
    assert "error" in results["details"][0]
