"""Tests for github_api module"""

from sync_upstream.github_api import GitHubAPI


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


def test_github_api_get_repository_branches(mocker):
    """Test getting repository branches"""
    mock_response1 = mocker.Mock()
    mock_response1.status_code = 200
    mock_response1.json.return_value = [{"name": "main"}, {"name": "dev"}, {"name": "feature"}]

    mock_response2 = mocker.Mock()
    mock_response2.status_code = 200
    mock_response2.json.return_value = []

    mocker.patch("requests.get", side_effect=[mock_response1, mock_response2])

    api = GitHubAPI("test-token")
    branches = api.get_repository_branches("owner", "repo")

    assert branches == ["main", "dev", "feature"]
