"""Tests for github_api module"""
import pytest
from sync_upstream.github_api import GitHubAPI
from sync_upstream.models import Repository


def test_github_api_init():
    """Test GitHubAPI initialization"""
    api = GitHubAPI("test-token")
    assert api.token == "test-token"
    assert "Authorization" in api.headers
    assert "Bearer test-token" in api.headers["Authorization"]


def test_github_api_sync_branch_success(mocker):
    """Test syncing a branch successfully"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    
    mocker.patch("requests.post", return_value=mock_response)
    
    api = GitHubAPI("test-token")
    result = api.sync_branch("owner", "repo", "branch")
    
    assert result is True


def test_github_api_sync_branch_failure(mocker):
    """Test syncing a branch with failure"""
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    
    mocker.patch("requests.post", return_value=mock_response)
    
    api = GitHubAPI("test-token")
    result = api.sync_branch("owner", "repo", "branch")
    
    assert result is False


def test_github_api_get_repository_success(mocker):
    """Test getting a repository successfully"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"name": "test-repo"}
    
    mocker.patch("requests.get", return_value=mock_response)
    
    api = GitHubAPI("test-token")
    result = api.get_repository("owner", "repo")
    
    assert result == {"name": "test-repo"}


def test_github_api_get_repository_not_found(mocker):
    """Test getting a repository that doesn't exist"""
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    
    mocker.patch("requests.get", return_value=mock_response)
    
    api = GitHubAPI("test-token")
    result = api.get_repository("owner", "repo")
    
    assert result is None


def test_github_api_get_current_user(mocker):
    """Test getting current user"""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"login": "test-user"}
    
    mocker.patch("requests.get", return_value=mock_response)
    
    api = GitHubAPI("test-token")
    user = api.get_current_user()
    
    assert user["login"] == "test-user"


def test_github_api_get_user_forks(mocker):
    """Test getting user forks"""
    mock_response1 = mocker.Mock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = [
        {
            "fork": True,
            "owner": {"login": "test-user"},
            "name": "fork1",
            "full_name": "test-user/fork1",
            "private": False,
            "default_branch": "main",
            "parent": {"full_name": "upstream/fork1"}
        },
        {
            "fork": True,
            "owner": {"login": "test-user"}, 
            "name": "private-fork",
            "full_name": "test-user/private-fork",
            "private": True,
            "default_branch": "main"
        }
    ]
    
    mock_response2 = mocker.Mock()
    mock_response2.status_code = 200
    mock_response2.json.return_value = []
    
    mocker.patch("requests.get", side_effect=[mock_response1, mock_response2])
    
    api = GitHubAPI("test-token")
    repos = api.get_user_forks("test-user")
    
    assert len(repos) == 1
    assert repos[0].name == "fork1"
    assert repos[0].has_upstream is True


def test_github_api_get_user_forks_include_private(mocker):
    """Test getting user forks including private"""
    mock_response1 = mocker.Mock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = [
        {
            "fork": True,
            "owner": {"login": "test-user"},
            "name": "public-fork",
            "full_name": "test-user/public-fork",
            "private": False,
            "default_branch": "main"
        },
        {
            "fork": True,
            "owner": {"login": "test-user"}, 
            "name": "private-fork",
            "full_name": "test-user/private-fork",
            "private": True,
            "default_branch": "main"
        }
    ]
    
    mock_response2 = mocker.Mock()
    mock_response2.status_code = 200
    mock_response2.json.return_value = []
    
    mocker.patch("requests.get", side_effect=[mock_response1, mock_response2])
    
    api = GitHubAPI("test-token")
    repos = api.get_user_forks("test-user", include_private=True)
    
    assert len(repos) == 2


def test_github_api_get_user_forks_ignore_non_fork(mocker):
    """Test that non-fork repos are ignored"""
    mock_response1 = mocker.Mock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = [
        {
            "fork": False,  # Not a fork
            "owner": {"login": "test-user"},
            "name": "not-a-fork",
            "full_name": "test-user/not-a-fork",
            "private": False,
            "default_branch": "main"
        },
        {
            "fork": True,
            "owner": {"login": "test-user"},
            "name": "actual-fork",
            "full_name": "test-user/actual-fork",
            "private": False,
            "default_branch": "main"
        }
    ]
    
    mock_response2 = mocker.Mock()
    mock_response2.status_code = 200
    mock_response2.json.return_value = []
    
    mocker.patch("requests.get", side_effect=[mock_response1, mock_response2])
    
    api = GitHubAPI("test-token")
    repos = api.get_user_forks("test-user")
    
    assert len(repos) == 1
    assert repos[0].name == "actual-fork"


def test_github_api_get_repository_branches(mocker):
    """Test getting repository branches"""
    mock_response1 = mocker.Mock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = [
        {"name": "main"},
        {"name": "dev"},
        {"name": "feature"}
    ]
    
    mock_response2 = mocker.Mock()
    mock_response2.status_code = 200
    mock_response2.json.return_value = []
    
    mocker.patch("requests.get", side_effect=[mock_response1, mock_response2])
    
    api = GitHubAPI("test-token")
    branches = api.get_repository_branches("owner", "repo")
    
    assert branches == ["main", "dev", "feature"]
