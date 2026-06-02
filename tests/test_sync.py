"""Tests for sync module"""
import pytest
from sync_upstream.sync import Synchronizer
from sync_upstream.models import Repository


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


def test_sync_repository_success(mocker):
    """Test successful repository sync"""
    mock_github_api = mocker.Mock()
    mock_github_api.get_repository_branches.return_value = ["main", "dev"]
    mock_github_api.sync_branch.return_value = True
    
    sync = Synchronizer(mock_github_api)
    
    repo = Repository(
        owner="owner",
        name="repo",
        full_name="owner/repo",
        is_private=False,
        has_upstream=True,
        upstream="upstream/repo",
    )
    
    result = sync.sync_repository(repo)
    assert result is True
    assert mock_github_api.sync_branch.call_count == 2


def test_sync_repository_with_branches(mocker):
    """Test syncing repository with specified branches"""
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
    )
    
    result = sync.sync_repository(repo, ["main"])
    assert result is True
    mock_github_api.get_repository_branches.assert_not_called()
    mock_github_api.sync_branch.assert_called_once_with("owner", "repo", "main")


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
    mock_github_api.get_repository_branches.return_value = ["main"]
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
            default_branch="main"
        ),
        Repository(
            owner="owner",
            name="repo2",
            full_name="owner/repo2",
            is_private=False,
            has_upstream=True,
            upstream="upstream/repo2",
            default_branch="main"
        ),
    ]
    
    results = sync.sync_repositories(repos)
    assert results["total"] == 2
    assert results["success"] == 1
    assert results["failed"] == 1
    assert len(results["details"]) == 2


def test_sync_repositories_exception(mocker):
    """Test syncing with exception"""
    mock_github_api = mocker.Mock()
    mock_github_api.get_repository_branches.side_effect = Exception("API Error")
    
    sync = Synchronizer(mock_github_api)
    
    repo = Repository(
        owner="owner",
        name="repo",
        full_name="owner/repo",
        is_private=False,
        has_upstream=True,
        upstream="upstream/repo",
    )
    
    results = sync.sync_repositories([repo])
    assert results["total"] == 1
    assert results["success"] == 0
    assert results["failed"] == 1
    assert "error" in results["details"][0]
