"""Unit tests for GitHub Discussions GraphQL client."""

from unittest.mock import Mock, patch

import pytest
from requests.exceptions import RequestException, Timeout

from github_discussions import GitHubDiscussionsClient
from github_discussions.exceptions import (
    AuthenticationError,
    GitHubGraphQLError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
)


class TestGitHubDiscussionsClient:
    """Test cases for GitHubDiscussionsClient."""

    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        return GitHubDiscussionsClient(token="test_token")

    @pytest.fixture
    def mock_response(self):
        """Create a mock response object."""
        response = Mock()
        response.json.return_value = {"data": {"test": "data"}}
        response.status_code = 200
        response.headers = {}
        return response

    def test_init(self, client):
        """Test client initialization."""
        assert client.token == "test_token"
        assert client.timeout == 30.0
        assert client.max_retries == 3
        assert client.base_url == "https://api.github.com/graphql"

    def test_init_custom_params(self):
        """Test client initialization with custom parameters."""
        client = GitHubDiscussionsClient(
            token="test_token",
            timeout=60.0,
            max_retries=5,
            base_url="https://custom.github.com/graphql",
        )
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.base_url == "https://custom.github.com/graphql"

    @patch("github_discussions.client.requests.Session.post")
    def test_make_request_success(self, mock_post, client, mock_response):
        """Test successful GraphQL request."""
        mock_post.return_value = mock_response

        result = client._make_request("query { test }")

        assert result == {"data": {"test": "data"}}
        mock_post.assert_called_once()

    @patch("github_discussions.client.requests.Session.post")
    def test_make_request_rate_limit_error(self, mock_post, client):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.headers = {
            "X-RateLimit-Reset": "1640995200",
            "X-RateLimit-Limit": "5000",
            "X-RateLimit-Remaining": "0",
        }
        mock_post.return_value = mock_response

        with pytest.raises(RateLimitError) as exc_info:
            client._make_request("query { test }")

        assert "Rate limit exceeded" in str(exc_info.value)
        assert exc_info.value.reset_at == "2022-01-01 00:00:00 UTC"

    @patch("github_discussions.client.requests.Session.post")
    def test_make_request_authentication_error(self, mock_post, client):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = RequestException(
            "401 Client Error"
        )
        mock_post.return_value = mock_response

        with pytest.raises(AuthenticationError):
            client._make_request("query { test }")

    @patch("github_discussions.client.requests.Session.post")
    def test_make_request_not_found_error(self, mock_post, client):
        """Test not found error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = RequestException(
            "404 Client Error"
        )
        mock_post.return_value = mock_response

        with pytest.raises(NotFoundError):
            client._make_request("query { test }")

    @patch("github_discussions.client.requests.Session.post")
    def test_make_request_graphql_errors(self, mock_post, client):
        """Test GraphQL error handling."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": None,
            "errors": [{"message": "Field 'invalidField' doesn't exist"}],
        }
        mock_post.return_value = mock_response

        with pytest.raises(GitHubGraphQLError) as exc_info:
            client._make_request("query { invalidField }")

        assert "Field 'invalidField' doesn't exist" in str(exc_info.value)

    @patch("github_discussions.client.requests.Session.post")
    @patch("time.sleep")
    def test_make_request_retry_on_timeout(self, mock_sleep, mock_post, client):
        """Test retry logic on timeout."""
        # First call times out, second succeeds
        mock_timeout = Mock()
        mock_timeout.status_code = 200
        mock_timeout.json.return_value = {"data": {"test": "data"}}

        mock_post.side_effect = [Timeout("Timeout"), mock_timeout]

        result = client._make_request("query { test }")

        assert result == {"data": {"test": "data"}}
        assert mock_post.call_count == 2
        mock_sleep.assert_called_once()

    @patch("github_discussions.client.requests.Session.post")
    @patch("time.sleep")
    def test_make_request_max_retries_exceeded(self, mock_sleep, mock_post, client):
        """Test max retries exceeded."""
        mock_post.side_effect = Timeout("Timeout")

        with pytest.raises(TimeoutError):
            client._make_request("query { test }")

        assert mock_post.call_count == 4  # Initial + 3 retries
        assert mock_sleep.call_count == 3

    @patch.object(GitHubDiscussionsClient, "_make_request")
    def test_get_rate_limit_status(self, mock_make_request, client):
        """Test getting rate limit status."""
        mock_make_request.return_value = {
            "data": {
                "rateLimit": {
                    "limit": 5000,
                    "remaining": 4990,
                    "used": 10,
                    "resetAt": "2023-01-01T00:00:00Z",
                }
            }
        }

        result = client.get_rate_limit_status()

        assert result.limit == 5000
        assert result.remaining == 4990
        assert result.used == 10
        assert result.reset_at == "2023-01-01T00:00:00Z"

    @patch("github_discussions.client.requests.Session.post")
    def test_execute_query(self, mock_post, client, mock_response):
        """Test executing custom GraphQL query."""
        mock_response.json.return_value = {"data": {"custom": "result"}}
        mock_post.return_value = mock_response

        result = client.execute_query("query { custom }")

        assert result == {"data": {"custom": "result"}}

    @patch("github_discussions.client.requests.Session")
    def test_context_manager(self, mock_session_class, client):
        """Test context manager usage."""
        # Mock the session
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Re-initialize client to use mocked session
        client._session = mock_session

        with client as c:
            assert c is client

        # Session should be closed
        mock_session.close.assert_called_once()

    @patch.object(GitHubDiscussionsClient, "_make_request")
    def test_get_discussions(self, mock_make_request, client):
        """Test getting discussions."""
        mock_make_request.return_value = {
            "data": {
                "repository": {
                    "discussions": {
                        "nodes": [
                            {
                                "id": "D_kwDOAHz1OX4uYAah",
                                "number": 1,
                                "title": "Test Discussion",
                                "body": "This is a test discussion",
                                "bodyHTML": "<p>This is a test discussion</p>",
                                "createdAt": "2023-01-01T00:00:00Z",
                                "updatedAt": "2023-01-01T00:00:00Z",
                                "author": {
                                    "login": "testuser",
                                    "avatarUrl": "https://github.com/avatar.jpg",
                                    "url": "https://github.com/testuser",
                                },
                                "category": {
                                    "id": "DIC_kwDOAHz1OX4CW5wG",
                                    "name": "General",
                                    "description": "General discussions",
                                    "emoji": "💬",
                                    "isAnswerable": True,
                                },
                                "comments": {"totalCount": 5},
                                "isAnswered": False,
                                "isLocked": False,
                                "isPinned": False,
                                "url": "https://github.com/owner/repo/discussions/1",
                            }
                        ],
                        "pageInfo": {
                            "hasNextPage": False,
                            "hasPreviousPage": False,
                            "startCursor": "Y3Vyc29yOnYyOpK5MjAyMC0xMi0"
                            "wOFQxNjoyMzo0MyswMDowMM4fGh0=",
                            "endCursor": "Y3Vyc29yOnYyOpK5MjAyMC0xMi0wO"
                            "FQxNjoyMzo0MyswMDowMM4fGh0=",
                        },
                    }
                }
            }
        }

        discussions = client.get_discussions("owner", "repo")

        assert len(discussions.discussions) == 1
        discussion = discussions.discussions[0]
        assert discussion.id == "D_kwDOAHz1OX4uYAah"
        assert discussion.number == 1
        assert discussion.title == "Test Discussion"
        assert discussion.author.login == "testuser"
        assert discussion.category.name == "General"
        assert discussion.comments_count == 5

    @patch.object(GitHubDiscussionsClient, "_make_request")
    def test_create_discussion(self, mock_make_request, client):
        """Test creating a discussion."""
        mock_make_request.return_value = {
            "data": {
                "createDiscussion": {
                    "discussion": {
                        "id": "D_kwDOAHz1OX4uYAah",
                        "number": 1,
                        "title": "New Discussion",
                        "body": "Discussion content",
                        "bodyHTML": "<p>Discussion content</p>",
                        "createdAt": "2023-01-01T00:00:00Z",
                        "updatedAt": "2023-01-01T00:00:00Z",
                        "author": {"login": "testuser"},
                        "category": {
                            "id": "DIC_kwDOAHz1OX4CW5wG",
                            "name": "General",
                            "isAnswerable": True,
                        },
                        "comments": {"totalCount": 0},
                        "isAnswered": False,
                        "isLocked": False,
                        "isPinned": False,
                        "url": "https://github.com/owner/repo/discussions/1",
                    }
                }
            }
        }

        discussion = client.create_discussion(
            repository_id="R_kgDOAHz1OX",
            category_id="DIC_kwDOAHz1OX4CW5wG",
            title="New Discussion",
            body="Discussion content",
        )

        assert discussion.id == "D_kwDOAHz1OX4uYAah"
        assert discussion.title == "New Discussion"
        assert discussion.body == "Discussion content"
